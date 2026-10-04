"""One fresh R16 robustness worker, with fixed fits and one final bank.

The parent times process launch through exit and durable output.  The three
inherited methods execute all three training stages without online payoff
selection.  The HJB group constructs both predetermined deployments from one
residual-selected family; no final payoff chooses between them.
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

ROOT = Path(__file__).resolve().parents[3]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+"\n")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relative_confirmation(row, directory):
    row = copy.deepcopy(row)
    for name in ("raw_path", "json_path"):
        require(Path(row[name]).name == row[name], "verifier path must be a basename")
        row[name] = str(Path(directory)/row[name])
    row["clip"] = row["clipping_threshold"]
    return row


def training_protocol(protocol, calibration):
    return dict(design=dict(primitives=copy.deepcopy(calibration["primitives"]),
        primitives_sha256=calibration["primitives_sha256"],
        initial_state_population=copy.deepcopy(calibration["initial_state_population"]),
        methods=list(protocol["methods"])),
        training=dict(copy.deepcopy(protocol["training"]), epsilon=calibration["epsilon"]),
        confirmation=dict(steps=protocol["confirmation"]["steps"]))


def hjb_counters(record):
    result = defaultdict(int)
    for candidate in record.get("candidates", []):
        for key, value in candidate.get("work", {}).items():
            result[key] += int(value)
    for value in record.get("collocation_work", {}).values():
        result["simulator_transitions"] += int(value.get("simulator_transitions", 0))
        result["occupation_trajectory_starts"] += int(value.get("occupation_trajectories", 0))
    for key, value in record.get("independent_diagnostics", {}).get("work", {}).items():
        result[key] += int(value)
    distillation = record.get("distillation", {})
    for key in ["greedy_label_rows", "greedy_scalar_row_iterations", "actor_adam_updates", "actor_lbfgs_closures"]:
        result["distillation_"+key] += int(distillation.get(key, 0))
    probe = record.get("probe_diagnostics", {})
    for key in ["diagnostic_hessian_rows", "diagnostic_quadratic_rows"]:
        result[key] += int(probe.get(key, 0))
    return dict(result)


def execute(protocol, trial_id, group, out):
    start = time.perf_counter()
    protocol_path, out = Path(protocol).resolve(), Path(out).resolve()
    p = json.loads(protocol_path.read_text())
    require(p.get("schema") == "nbo-r16-robustness-v1", "wrong robustness protocol")
    match = re.fullmatch(r"([a-z][a-z0-9_]*)_d(\d+)_s(\d+)", trial_id)
    require(match is not None, "trial id must name calibration, dimension and stream")
    calibration_id, dimension, seed = match.group(1), int(match.group(2)), int(match.group(3))
    calibrations = {row["id"]: row for row in p["calibrations"]}
    require(calibration_id in calibrations and dimension in p["dimensions"] and seed in p["seeds"], "undeclared trial")
    require(group in p["execution_groups"], "undeclared execution group")
    require(group in ("nbo", "raw_costate", "direct_policy", "hjb_family"), "unsupported execution group")
    source = os.environ.get("NBO_R16_SOURCE_COMMIT", "")
    fingerprint = os.environ.get("NBO_R16_METHOD_FINGERPRINT", "")
    require(re.fullmatch(r"[0-9a-f]{40}", source), "official worker requires immutable R16 source")
    require(re.fullmatch(r"[0-9a-f]{64}", fingerprint), "official worker requires source-bound method fingerprint")
    require(not out.exists() or not any(out.iterdir()), "refusing to overwrite a robustness worker")
    out.mkdir(parents=True, exist_ok=True)
    calibration, protocol_sha = calibrations[calibration_id], sha(protocol_path)
    outputs = ["hjb_greedy", "hjb_distilled"] if group == "hjb_family" else [group]
    require(all(method in p["methods"] for method in outputs), "output method missing from protocol")
    metadata = dict(trial_id=trial_id, calibration_id=calibration_id, dimension=dimension,
        stream_seed=seed, source_commit=source, numerical_source_commit=source,
        protocol_sha256=protocol_sha, method_fingerprint=fingerprint,
        primitives_sha256=calibration["primitives_sha256"], epsilon=calibration["epsilon"])
    result = dict(schema="nbo-r16-robustness-group-v1", **metadata, group=group,
        complete=False, outputs={}, failures=[], online_payoff_checks=0,
        final_payoff_used_for_selection=False, source_protocol=str(protocol_path.relative_to(ROOT)),
        confirmation_scope="One fixed final bank after all fitting/selection; no online target stopping.")
    write(out/"START.json", result)
    fatal = None
    fit_counters, prepared, fit_complete = {}, {}, True

    def failure(phase, exc, method_id=None, stage=None):
        row = dict(phase=phase, method_id=method_id, stage=stage,
            error_type=type(exc).__name__, error=str(exc), traceback=traceback.format_exc(),
            seconds_since_worker_entry=time.perf_counter()-start)
        result["failures"].append(row)
        write(out/"failures"/f"{len(result['failures']):02d}_{phase}.json", row)
        return row

    try:
        # Imports and all parameter/constant work occur inside the child clock.
        from capital_adapter import bind_economy
        import strong_hjb
        bound = bind_economy(calibration["primitives"], calibration["epsilon"],
                             calibration["initial_state_population"], calibration_id)
        require(bound.primitives_sha256 == calibration["primitives_sha256"], "calibration primitive hash mismatch")
        result["capital_binding"] = bound.audit_record(p["training"]["global_steps"])
        write(out/"CAPITAL_BINDING.json", result["capital_binding"])
        local_protocol = training_protocol(p, calibration)
        bound.validate_protocol(local_protocol)
        from method_statistics import ConfidenceBudget
        budget = ConfidenceBudget(p["inference"]["alpha"], p["inference"]["two_sided_event_count"])
        result["confidence_budget"] = budget.as_dict()
        fit_start = time.perf_counter()
        if group != "hjb_family":
            run, stages = None, []
            last_checkpoint = None
            try:
                run = bound.training_run(local_protocol, dimension, seed, group, out/"training",
                                         metadata=dict(metadata, method_id=group))
                for stage in range(1, p["training"]["checkpoint_count"]+1):
                    stage_start = time.perf_counter()
                    details = run.advance(stage)
                    checkpoint = out/"checkpoints"/f"stage_{stage}.pt"
                    checksum = run.save_checkpoint(checkpoint)
                    last_checkpoint = checkpoint
                    row = dict(stage=stage, checkpoint=str(checkpoint.relative_to(out)),
                        checkpoint_sha256=checksum, training=details,
                        training_and_checkpoint_seconds=time.perf_counter()-stage_start,
                        payoff_checked=False)
                    stages.append(row)
                    write(out/"training"/f"stage_{stage}.json", row)
            except Exception as exc:
                failure("training", exc, group, None if run is None else run.stage+1)
                fit_complete = False
            if run is not None:
                fit_counters = dict(run.counters)
                result["training_history"] = copy.deepcopy(run.history)
                if run.train_states is not None:
                    replay = out/"training"/"replay.npz"
                    result["training_replay"] = dict(path=str(replay.relative_to(out)), sha256=run.save_replay(replay))
            selected = out/"selected.pt"
            if fit_complete:
                require(last_checkpoint is not None and len(stages) == p["training"]["checkpoint_count"], "fixed training stages incomplete")
                shutil.copyfile(last_checkpoint, selected)
            else:
                bound.core.save_fallback(selected, local_protocol, dimension, seed, group,
                    metadata=dict(metadata, method_id=group), failure=result["failures"], counters=fit_counters)
            prepared[group] = dict(checkpoint=selected, loader="inherited", fallback=not fit_complete,
                training_stages=stages, counters=fit_counters,
                operation_counters_complete=fit_complete,
                fit_complete=fit_complete, fit_seconds=time.perf_counter()-fit_start)
        else:
            design_path = (ROOT/p["strong_hjb_design"]).resolve()
            require(design_path.is_relative_to(ROOT), "HJB design must lie in the frozen repository")
            design = json.loads(design_path.read_text())
            configuration = design["implementation_configuration"]
            require(configuration["occupation_steps"] == p["training"]["global_steps"], "HJB must use the common training occupation grid")
            result["strong_hjb_design_sha256"] = sha(design_path)
            try:
                held = bound.held_reference(configuration["occupation_steps"])
                greedy, actor, family = strong_hjb.run_hjb_family(dimension=dimension,
                    params=calibration["primitives"], epsilon=calibration["epsilon"],
                    population=calibration["initial_state_population"], seed=seed,
                    configuration=configuration, out=out/"hjb", reference_held_schedule=held,
                    source_metadata=metadata)
                del greedy, actor
                fit_counters = hjb_counters(family)
                result["hjb_family_record"] = "hjb/HJB_FAMILY.json"
                result["hjb_family_sha256"] = sha(out/result["hjb_family_record"])
                result["hjb_selected_variant"] = family["selected_variant"]
                result["hjb_residual_diagnostics"] = family["independent_diagnostics"]
                for method in outputs:
                    prepared[method] = dict(checkpoint=out/"hjb"/(method+".pt"), loader="strong_hjb",
                        fallback=False, fit_complete=True, counters=fit_counters,
                        operation_counters_complete=family["operation_counters_complete"],
                        diagnostics=family["independent_diagnostics"],
                        fit_seconds=time.perf_counter()-fit_start)
            except Exception as exc:
                failure("hjb_family_training", exc)
                fit_complete = False
                for method in outputs:
                    selected = out/(method+"_fallback.pt")
                    bound.core.save_fallback(selected, local_protocol, dimension, seed, method,
                        metadata=dict(metadata, method_id=method), failure=result["failures"], counters=fit_counters)
                    prepared[method] = dict(checkpoint=selected, loader="inherited", fallback=True,
                        fit_complete=False, counters=fit_counters, operation_counters_complete=False,
                        fit_seconds=time.perf_counter()-fit_start)
        result["shared_fit_seconds"] = time.perf_counter()-fit_start
        result["shared_prerequisite_seconds_since_entry"] = time.perf_counter()-start
        key = f"{p['stream_domain']}/{calibration_id}/{seed}/{dimension}/{p['confirmation']['bank_domain']}/0"
        bank_seed = int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")
        result["confirmation_bank"] = key
        result["confirmation_noise_seed"] = bank_seed
        for method in outputs:
            entry = prepared[method]
            method_start = time.perf_counter()
            row = dict(method_id=method, checkpoint=str(entry["checkpoint"].relative_to(out)),
                checkpoint_sha256=sha(entry["checkpoint"]), confirmation=None,
                fallback=entry["fallback"], fit_complete=entry["fit_complete"],
                fit_seconds=entry["fit_seconds"], counters=dict(entry["counters"]),
                training_counters=dict(entry["counters"]),
                training_operation_counters_complete=entry["operation_counters_complete"],
                final_certified_target=False, complete=False,
                shared_family_construction=(group == "hjb_family"))
            for extra in ("training_stages", "diagnostics"):
                if extra in entry:
                    row[extra] = entry[extra]
            try:
                bound.assert_bound()
                loader = strong_hjb.load_candidate if entry["loader"] == "strong_hjb" else bound.load_candidate
                actor, _, state = loader(entry["checkpoint"])
                require(state["method_id"] == method and state["params"] == calibration["primitives"], "returned policy scientific identity mismatch")
                state_metadata = state.get("source_metadata", state)
                for name in ("source_commit", "protocol_sha256", "method_fingerprint"):
                    require(state_metadata.get(name) == metadata[name], "returned policy provenance mismatch: "+name)
                require(float(state["epsilon"]) == calibration["epsilon"], "returned action radius mismatch")
                analytical = bool(getattr(actor, "is_analytical_schedule", False))
                require(analytical == entry["fallback"], "analytical fallback identity mismatch")
                directory = "confirmation/"+method
                confirmation = bound.verifier.verify(actor, dimension=dimension,
                    steps=p["confirmation"]["steps"], paths=p["confirmation"]["paths_per_stream"],
                    noise_seed=bank_seed, event_alpha=budget.event_alpha,
                    primitives=calibration["primitives"], out=out/directory, record_id="confirmation",
                    metadata=dict(metadata, method_id=method, is_confirmation=True,
                        noise_key=key, analytic_schedule=analytical, fallback=entry["fallback"],
                        checkpoint_sha256=row["checkpoint_sha256"],
                        economic_design_identity_sha256=bound.identity_sha256,
                        fixed_fit=True, online_target_attainment=False))
                require(math.isfinite(confirmation["lower"]) and math.isfinite(confirmation["upper"]), "nonfinite final interval")
                row["confirmation"] = relative_confirmation(confirmation, directory)
                row["verification_work"] = confirmation["work"]
                for name, value in confirmation["work"].items():
                    if not name.endswith("seconds") and not name.startswith("seconds_"):
                        require(float(value).is_integer(), "noninteger verification operation counter")
                        row["counters"][name] = row["counters"].get(name, 0)+int(value)
                row["final_certified_target"] = confirmation["lower"] >= p["confirmation"]["fixed_budget_gain_target"]
                row["secondary_final_certified_target"] = confirmation["lower"] >= p["confirmation"]["secondary_gain_target"]
                row["complete"] = True
            except Exception as exc:
                failure("final_confirmation", exc, method)
            row["deployment_and_confirmation_seconds"] = time.perf_counter()-method_start
            row["operation_counters_complete"] = entry["operation_counters_complete"] and row["complete"]
            row["operation_counter_scope"] = "Complete recorded operation counts" if row["operation_counters_complete"] else "Known completed-call counts only; partial failed-attempt operations are not invented, while the full parent clock includes them."
            row["standalone_seconds_before_group_final_write"] = result["shared_prerequisite_seconds_since_entry"]+row["deployment_and_confirmation_seconds"]
            result["outputs"][method] = row
            write(out/(method+"_OUTPUT.json"), row)
        result["complete"] = all(result["outputs"][method]["complete"] for method in outputs)
        if not result["complete"]:
            raise RuntimeError("one or more final certificates failed; no successful replacement is allowed")
    except Exception as exc:
        fatal = exc
        failure("group_finalization", exc)
    finally:
        result["seconds_before_final_result_write"] = time.perf_counter()-start
        result["timing_authority"] = "Parent WORK.json measures launch, imports, all science, all output files, final RESULT.json and process exit. HJB standalone accounting includes shared prerequisite work plus the relevant deployment only."
        result["failure_work_scope"] = "Every failed attempt remains in parent elapsed and CPU time. Missing partial operation counters are not invented."
        result["verification_counters_complete"] = all(row.get("complete", False) for row in result["outputs"].values()) and len(result["outputs"]) == len(outputs)
        write(out/"RESULT.json", result)
    if fatal is not None:
        raise RuntimeError("robustness group has incomplete final evidence; failure record retained") from fatal
    return dict(complete=True, trial_id=trial_id, group=group,
        outputs={method: dict(fallback=row["fallback"], lower=row["confirmation"]["lower"],
                             upper=row["confirmation"]["upper"]) for method, row in result["outputs"].items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--trial-id", required=True)
    parser.add_argument("--group", required=True)
    parser.add_argument("--out", type=Path, required=True)
    print(json.dumps(execute(**vars(parser.parse_args())), indent=2, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
