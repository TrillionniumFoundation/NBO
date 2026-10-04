"""Execute one complete registered R15 method stream with real early stopping.

The outer pipeline measures this process from launch through exit. This worker
never reconstructs an early-stop clock from a completed training trajectory.
Every attempted stage/check is retained; a training failure deploys the declared
analytical-schedule fallback and still receives independent final confirmation.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import sys
import time
import traceback


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relative_verification(row, subdir):
    answer = copy.deepcopy(row)
    for key in ["raw_path", "json_path"]:
        require(Path(answer[key]).name == answer[key], "verifier path must be a basename")
        answer[key] = str(Path(subdir) / answer[key])
    answer["clip"] = answer["clipping_threshold"]
    return answer


def execute(protocol, trial_id, method_id, out):
    start = time.perf_counter()
    protocol_path, out = Path(protocol).resolve(), Path(out).resolve()
    p = json.loads(protocol_path.read_text())
    from pipeline_experiment import validate_protocol
    validate_protocol(p)
    match = re.fullmatch(r"d(\d+)_s(\d+)", trial_id)
    require(match is not None, "trial id must identify a declared dimension and stream")
    d, seed = map(int, match.groups())
    require(d in p["design"]["dimensions"] and seed in p["design"]["seeds"], "undeclared trial")
    require(method_id in p["design"]["methods"], "undeclared canonical method")
    source = os.environ.get("NBO_R15_NUMERICAL_SOURCE_COMMIT", "")
    fingerprint = os.environ.get("NBO_R15_METHOD_FINGERPRINT", "")
    require(re.fullmatch("[0-9a-f]{40}", source), "official worker requires immutable numerical source")
    require(re.fullmatch("[0-9a-f]{64}", fingerprint), "official worker requires source-bound method fingerprint")
    protocol_sha = sha(protocol_path)
    out.mkdir(parents=True, exist_ok=True)
    require(not (out / "RESULT.json").exists(), "refusing to overwrite a complete stream")

    # Imports occur inside the independently timed process, before any training
    # or constant calculation. Historical files remain byte-for-byte unchanged.
    from training_core import TrainingRun, load_candidate, save_fallback, stream_seed
    from actor_verifier import verify
    from method_statistics import ConfidenceBudget

    inf = p["inference"]
    online_budget = ConfidenceBudget(inf["alpha_allocation"]["online_stopping"], inf["online_stopping_events"])
    final_budget = ConfidenceBudget(inf["alpha_allocation"]["method_confirmation"], inf["method_confirmation_events"])
    target = p["stopping"]["primary_certified_gain_target"]
    metadata = dict(method_id=method_id, trial_id=trial_id, dimension=d,
                    stream_seed=seed, source_commit=source, numerical_source_commit=source,
                    protocol_sha256=protocol_sha, method_fingerprint=fingerprint,
                    primitives_sha256=p["design"]["primitives_sha256"], epsilon=p["training"]["epsilon"])
    result = dict(metadata, record_type="R15 complete registered method stream", complete=False,
                  actual_early_stopping_execution=True, attained_online=False, attained=False,
                  primary_certified_gain_target=target,
                  stopping_scope="The registered algorithm is executed prospectively; training stops at the first successful online check. A failure before the first check remains a failed complete stream.",
                  fallback=False, selected_checkpoint=None, selected_checkpoint_sha256=None,
                  online_checks=[], training_stages=[], failures=[], counters={},
                  confirmation_independent_of_selection=True,
                  confidence_budget={"online": online_budget.as_dict(), "confirmation": final_budget.as_dict()},
                  final_confirmation=None)
    write(out / "START.json", dict(metadata, stage="before training initialization"))
    run = None
    last_checkpoint = None
    verification_work = []
    fatal = None

    def failure(phase, stage, exc):
        row = dict(phase=phase, stage=stage, error_type=type(exc).__name__, error=str(exc),
                   traceback=traceback.format_exc(), seconds_since_worker_entry=time.perf_counter()-start)
        result["failures"].append(row)
        write(out / "failures" / f"{len(result['failures']):02d}_{phase}.json", row)
        return row

    try:
        try:
            run = TrainingRun(p, d, seed, method_id, out / "training", metadata=metadata)
            require(run.method_fingerprint == fingerprint, "training candidate uses a different methodology fingerprint")
        except Exception as exc:
            failure("initialization", 0, exc)
            result["fallback"] = True

        if run is not None and not result["fallback"]:
            for stage in range(1, p["stopping"]["maximum_checkpoint_checks"] + 1):
                stage_start = time.perf_counter()
                checkpoint = out / "checkpoints" / f"stage_{stage}.pt"
                try:
                    details = run.advance(stage)
                    checkpoint_sha = run.save_checkpoint(checkpoint)
                    last_checkpoint = checkpoint
                    stage_row = dict(stage=stage, checkpoint=str(checkpoint.relative_to(out)),
                                     checkpoint_sha256=checkpoint_sha, training=details,
                                     training_and_checkpoint_seconds=time.perf_counter()-stage_start)
                    result["training_stages"].append(stage_row)
                    write(out / "training" / f"stage_{stage}.json", stage_row)
                except Exception as exc:
                    failure("training", stage, exc)
                    result["fallback"] = True
                    break

                # The actual completed checkpoint is reloaded and checked now.
                # Neither future training nor the independent final bank has
                # been run when the stopping decision is made.
                bank_seed = stream_seed(seed, d, "online_check", stage)
                bank_key = f"NBO-R15-v1/{seed}/{d}/online_check/{stage}"
                online = dict(stage=stage, noise_seed=bank_seed, noise_key=bank_key,
                              complete=False, attained=False, checkpoint_sha256=checkpoint_sha)
                try:
                    actor, _, checkpoint_state = load_candidate(checkpoint)
                    require(checkpoint_state["method_id"] == method_id
                            and checkpoint_state["source_commit"] == source
                            and checkpoint_state["protocol_sha256"] == protocol_sha
                            and checkpoint_state["method_fingerprint"] == fingerprint,
                            "online candidate provenance mismatch")
                    subdir = f"online/stage_{stage}"
                    row = verify(actor, dimension=d, steps=p["stopping"]["steps"],
                                 paths=p["stopping"]["paths_per_checkpoint"], noise_seed=bank_seed,
                                 event_alpha=online_budget.event_alpha, primitives=p["design"]["primitives"],
                                 out=out / subdir, record_id="online_check",
                                 metadata=dict(metadata, is_confirmation=False, noise_key=bank_key,
                                               stage=stage, checkpoint_sha256=checkpoint_sha,
                                               analytic_schedule=bool(getattr(actor, "is_analytical_schedule", False))))
                    require(math.isfinite(row["lower"]) and math.isfinite(row["upper"]), "online interval is nonfinite")
                    verification_work.append(row["work"])
                    online.update(complete=True, attained=row["lower"] >= target,
                                  verification=relative_verification(row, subdir))
                except Exception as exc:
                    online["failure"] = failure("online_check", stage, exc)
                online["seconds_since_worker_entry"] = time.perf_counter() - start
                result["online_checks"].append(online)
                write(out / "online" / f"stage_{stage}" / "DECISION.json", online)
                if online["attained"]:
                    result["attained_online"] = result["attained"] = True
                    result["attainment_stage"] = stage
                    result["attainment_worker_seconds"] = online["seconds_since_worker_entry"]
                    break

        # Preserve reusable training information and charge the I/O before final
        # confirmation. A partially failed fit remains in the recorded history.
        if run is not None:
            result["counters"] = dict(run.counters)
            result["training_history"] = copy.deepcopy(run.history)
            if run.train_states is not None:
                try:
                    replay = out / "training" / "replay.npz"
                    result["training_replay"] = dict(path=str(replay.relative_to(out)), sha256=run.save_replay(replay))
                except Exception as exc:
                    failure("replay_serialization", getattr(run, "stage", 0), exc)
                    raise

        selected = out / "selected.pt"
        if result["fallback"]:
            save_fallback(selected, p, d, seed, method_id, metadata=metadata,
                          failure=result["failures"], counters=result["counters"])
        else:
            require(last_checkpoint is not None, "no returned candidate exists")
            shutil.copyfile(last_checkpoint, selected)
        result["selected_checkpoint"] = selected.name
        result["selected_checkpoint_sha256"] = sha(selected)
        actor, _, state = load_candidate(selected)
        require(state["method_id"] == method_id and state["source_commit"] == source
                and state["protocol_sha256"] == protocol_sha and state["method_fingerprint"] == fingerprint
                and state["primitives_sha256"] == p["design"]["primitives_sha256"], "returned candidate provenance mismatch")
        analytic = bool(getattr(actor, "is_analytical_schedule", False))
        require(analytic == result["fallback"], "analytical fallback identity mismatch")
        bank_seed = stream_seed(seed, d, "independent_confirmation", 0)
        bank_key = f"NBO-R15-v1/{seed}/{d}/independent_confirmation/0"
        final = verify(actor, dimension=d, steps=p["confirmation"]["steps"],
                       paths=p["confirmation"]["paths_per_seed"], noise_seed=bank_seed,
                       event_alpha=final_budget.event_alpha, primitives=p["design"]["primitives"],
                       out=out / "confirmation", record_id="confirmation",
                       metadata=dict(metadata, is_confirmation=True, noise_key=bank_key,
                                     analytic_schedule=analytic, checkpoint_sha256=result["selected_checkpoint_sha256"],
                                     attained_online=result["attained_online"], fallback=result["fallback"]))
        verification_work.append(final["work"])
        result["final_confirmation"] = relative_verification(final, "confirmation")
        result["complete"] = True
    except Exception as exc:
        fatal = exc
        failure("finalization_or_confirmation", None, exc)
    finally:
        if run is not None:
            result["counters"] = dict(run.counters)
        result["training_counters"] = dict(result["counters"])
        aggregate = defaultdict(float)
        for work in verification_work:
            for key, value in work.items():
                aggregate[key] += value
        result["verification_work"] = dict(aggregate)
        for key, value in aggregate.items():
            if not key.endswith("seconds") and not key.startswith("seconds_"):
                require(float(value).is_integer(), "work counter must be an integer")
                result["counters"][key] = result["counters"].get(key, 0) + int(value)
        result["counters"]["total_state_transitions"] = (
            result["counters"].get("simulator_transitions", 0)
            + result["counters"].get("verification_transitions", 0))
        result["counter_scope"] = "Training cumulative counters plus every completed online and final verification. Simulator transitions count training; verification transitions count the separately evaluated policy/reference paths; total_state_transitions sums both. Shared actor/derivative counters sum training and verification. Parent WORK.json supplies full CPU/RSS/time."
        result["verification_counters_complete"] = not any(
            r["phase"] in ["online_check", "finalization_or_confirmation"] for r in result["failures"])
        result["failure_work_scope"] = "Every failed attempt is included in the independent process clock. If an exception prevents a verifier work return, verification_counters_complete is false and its partial operation counts are not invented."
        result["completed_online_checks"] = sum(r["complete"] for r in result["online_checks"])
        result["attempted_online_checks"] = len(result["online_checks"])
        result["seconds_before_final_result_write"] = time.perf_counter() - start
        result["timing_authority"] = "The independent parent WORK.json includes process startup, imports and this final result write; internal stage clocks are descriptive."
        write(out / "RESULT.json", result)
    if fatal is not None:
        raise RuntimeError("complete stream has no valid final confirmation; failed evidence retained") from fatal
    return {"complete": True, "trial_id": trial_id, "method_id": method_id,
            "attained_online": result["attained_online"], "fallback": result["fallback"],
            "completed_online_checks": result["completed_online_checks"],
            "final_lower": result["final_confirmation"]["lower"],
            "final_upper": result["final_confirmation"]["upper"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--trial-id", required=True)
    parser.add_argument("--method-id", required=True)
    parser.add_argument("--out", type=Path, required=True)
    print(json.dumps(execute(**vars(parser.parse_args())), indent=2, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
