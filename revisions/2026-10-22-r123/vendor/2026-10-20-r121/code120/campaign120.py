"""Prospectively frozen R120 acquisition, independent sampling and policy study.

No scientific package is imported before the actual source-commit byte gate.
Acquisition, actor publication, entropy/state publication and held-out decisions
are separate invocations, with immutable artifacts verified between stages.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback

from io120 import (REVISION, append_jsonl, digest, exclusive_attempt, manifest_files,
                   verify_artifacts, verify_ancestry, write_json)
from custody120 import verify_source

ARMS = ("online", "quadratic", "relu", "hinge", "spline", "poly2", "poly3", "grid")
SERVICES = ("completed", "legacy-safe", "paired", "direct-refine")
LEVELS = (0.5, 0.75)
N_STATES = 64
TIMING_STATES = 32
TIMING_REPEATS = 3


class Events:
    """A flushed deterministic-gzip trace with every failed prefix retained."""
    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.raw = path.open("xb")
        self.gz = gzip.GzipFile(filename="", mode="wb", fileobj=self.raw, mtime=0)
        self.text = io.TextIOWrapper(self.gz, encoding="utf-8", newline="\n")
        self.records = 0
        self.serialization_seconds = 0.0

    def __call__(self, event):
        started = time.perf_counter()
        self.text.write(json.dumps(dict(sequence=self.records, **event), sort_keys=True, allow_nan=False) + "\n")
        self.text.flush()
        self.raw.flush()
        os.fsync(self.raw.fileno())
        self.records += 1
        self.serialization_seconds += time.perf_counter()-started

    def close(self):
        self.text.close()
        self.raw.close()


def scientific():
    import improvement120 as imp
    return imp


def acquire(args, out):
    imp = scientific()
    np, rep, kern, econ = imp.np, imp.rep, imp.kern, imp.econ
    started = time.perf_counter()
    x = rep.grid(16)
    receipts = []
    for index, alpha in enumerate(LEVELS):
        before, label_started = econ.COUNTS.copy(), time.perf_counter()
        append_jsonl(out/"ACQUISITION_PROGRESS120.jsonl", dict(event="labels-start",
            index=index, alpha=alpha, state=x.tolist(), terminal_tolerance=econ.TERMINAL_TOL))
        # The original terminal problem and label accuracy are unchanged.
        # The common analytic compiler is available to every representation.
        lab = kern.compiled_certificate(imp.I(x), alpha)
        label_seconds = time.perf_counter()-label_started
        label_counts = imp.base.counter_delta(before)
        ts = time.perf_counter()
        write_json(out/f"labels-{index}.json", dict(index=index, alpha=alpha, state=x.tolist(),
            lower=lab["lower"].tolist(), upper=lab["upper"].tolist(),
            label_seconds=label_seconds, querycounts=label_counts,
            original_terminal_target=True, labels_are_value_intervals_not_actions=True,
            compiler_available_to_all_arms=True, maximum_terminal_gap=float(np.max(lab["gap"]))))
        label_recording_seconds = time.perf_counter()-ts
        emit_path = out/f"fit-events-{index}.jsonl"
        append_jsonl(emit_path, dict(event="all-fits-start", index=index, alpha=alpha,
                                   label_sha256=digest(out/f"labels-{index}.json")))
        tfit = time.perf_counter()
        old_build, old_audit = rep.study97.build, rep.audit_greedy
        def observed_build(kind, states, labels, rank):
            append_jsonl(emit_path, dict(event="critic-fit-start", kind=kind, rank=rank))
            model = old_build(kind, states, labels, rank)
            append_jsonl(emit_path, imp.plain(dict(event="critic-fit-complete", kind=kind,
                model_payload=rep.payload(model), actual_fit_record=model.record)))
            return model
        def observed_audit(kind, states, labels, model):
            append_jsonl(emit_path, dict(event="fit-audit-start", kind=kind))
            answer = old_audit(kind, states, labels, model)
            append_jsonl(emit_path, imp.plain(dict(event="fit-audit-complete", kind=kind, audit=answer)))
            return answer
        rep.study97.build, rep.audit_greedy = observed_build, observed_audit
        try:
            models, records = rep.fit_all(x, lab)
        finally:
            rep.study97.build, rep.audit_greedy = old_build, old_audit
        fit_total = time.perf_counter()-tfit
        known_fit = sum(float(r.get("fit_seconds", 0))+float(r.get("audit_seconds", 0))+
                        float(r.get("serialization_seconds", 0)) for r in records.values())
        unassigned_fit_overhead = max(0., fit_total-known_fit)
        append_jsonl(emit_path, dict(event="all-fits-complete", index=index, alpha=alpha,
            all_models_fit_audit_serialization_seconds=fit_total,
            unassigned_fit_bookkeeping_seconds=unassigned_fit_overhead))
        summary = dict(index=index, alpha=alpha, label_seconds=label_seconds,
                       label_recording_seconds=label_recording_seconds,
                       all_models_fit_audit_serialization_seconds=fit_total,
                       unassigned_fit_bookkeeping_seconds=unassigned_fit_overhead, models={})
        for arm in ARMS:
            folder = out/"models"/f"{index}-{arm}"
            folder.mkdir(parents=True, exist_ok=False)
            tstore = time.perf_counter()
            raw = rep.encoded(models[arm])
            with (folder/"model.json").open("xb") as stream:
                stream.write(raw); stream.flush(); os.fsync(stream.fileno())
            storage_seconds = time.perf_counter()-tstore
            model_sha = hashlib.sha256(raw).hexdigest()
            own = dict(records[arm])
            parent = records["relu"] if arm=="hinge" else own
            learned = arm != "online"
            component_fit = float(parent.get("fit_seconds", 0))
            component_audit = float(parent.get("audit_seconds", 0))
            component_serialization = float(own.get("serialization_seconds", 0))
            standalone = (label_seconds+label_recording_seconds+component_fit+component_audit+
                          component_serialization+storage_seconds+unassigned_fit_overhead) if learned else storage_seconds+component_serialization
            own.update(index=index, alpha=alpha, arm=arm, model_sha256=model_sha,
                model_bytes=len(raw), original_label_sites=256 if learned else 0,
                original_label_querycounts_if_standalone=label_counts if learned else {},
                label_cost_if_standalone_seconds=label_seconds+label_recording_seconds if learned else 0.,
                deployment_artifact_write_seconds=storage_seconds,
                actual_standalone_acquisition_charge_seconds=standalone,
                standalone_fit_component_seconds=component_fit if learned else 0.,
                standalone_fit_audit_component_seconds=component_audit if learned else 0.,
                standalone_serialization_component_seconds=component_serialization,
                unassigned_common_fit_overhead_charged_in_full=unassigned_fit_overhead if learned else 0.,
                charge_scope="sum of actual measured components; every learned arm pays all common label and residual bookkeeping work; hinge pays the ReLU fit and audit in full",
                critic_target="midpoint of original V1 value enclosure; ordinary value loss",
                actor_rule="retained recursive proposal rep.proposal; no direct action-supervised fitting")
            write_json(folder/"acquisition.json", own)
            summary["models"][arm] = dict(model_sha256=model_sha,
                acquisition_receipt_sha256=digest(folder/"acquisition.json"),
                standalone_acquisition_charge_seconds=standalone)
        receipts.append(summary)
        print("ACQUIRE", index, alpha, "all eight actors stored", flush=True)
    write_json(out/"ACQUISITION120.json", dict(status="executed", records=receipts,
        new_random_samples=0, heldout_states_available=False, risk_levels=LEVELS,
        fixed_training_grid="16 by 16 tensor midpoint design", state_dimension=2,
        total_acquisition_seconds=time.perf_counter()-started, machine=imp.base.machine(),
        full_experiment_cost_is_separate_from_standalone_allocation=True))


def sample(args, out):
    # This subcommand imports no scientific dependency. Every individual state
    # coordinate receives its own five independent bytes from the operating
    # system, rather than extrapolating a finite seed into a purported iid law.
    actors = verify_artifacts(args.actors, "ACQUISITION_MANIFEST120.json", args.actor_commit)
    validate_manifest_identity(args.actors, "ACQUISITION_MANIFEST120.json", "acquire", args.source_commit)
    validate_model_census(args.actors)
    source_actor_order = verify_ancestry(args.source_commit, args.actor_commit)
    entropy = os.urandom(N_STATES*2*5)
    with (out/"entropy120.bin").open("xb") as stream:
        stream.write(entropy); stream.flush(); os.fsync(stream.fileno())
    states = []
    for row in range(N_STATES):
        ints = [int.from_bytes(entropy[(row*2+j)*5:(row*2+j+1)*5], "big") for j in range(2)]
        state = [v/2**40 for v in ints]
        states.append(dict(row=row, coordinate_numerators=ints, denominator=2**40,
                           state=state, state_hex=[v.hex() for v in state]))
    write_json(out/"states120.json", dict(population="product discrete uniform on {0,...,2^40-1}/2^40 in two coordinates",
        rows=N_STATES, dimension=2, coordinates_independently_acquired_from_os_bytes=True,
        common_states_across_risk_levels=True, iid_unit="state row; both risks and every arm/service share each row",
        original_innovation_law_unchanged="continuous uniform on [-1/32,1/32]",
        entropy_bytes=len(entropy), entropy_sha256=hashlib.sha256(entropy).hexdigest(),
        source_commit=args.source_commit, actor_commit=args.actor_commit,
        source_actor_ancestry=source_actor_order, actors=actors, states=states))
    print("SAMPLE", N_STATES, "states saved; no economic evaluation", flush=True)


def validate_manifest_identity(root, name, kind, source_commit):
    manifest = json.loads((root/name).read_text())
    if manifest.get("kind") != kind or manifest.get("source_commit") != source_commit:
        raise RuntimeError("Artifact kind or generating source commit differs: " + name)
    return manifest


def validate_model_census(root):
    manifest = json.loads((root/"ACQUISITION_MANIFEST120.json").read_text())
    files = {item["path"] for item in manifest["files"]}
    actual = {p for p in files if Path(p).name == "model.json"}
    expected = {f"models/{i}-{arm}/model.json" for i in range(2) for arm in ARMS}
    if actual != expected:
        raise RuntimeError("Exactly sixteen frozen risk/arm actors are required")


def read_inputs(args):
    actors = verify_artifacts(args.actors, "ACQUISITION_MANIFEST120.json", args.actor_commit)
    states = verify_artifacts(args.states, "STATE_MANIFEST120.json", args.state_commit)
    validate_manifest_identity(args.actors, "ACQUISITION_MANIFEST120.json", "acquire", args.source_commit)
    validate_manifest_identity(args.states, "STATE_MANIFEST120.json", "sample", args.source_commit)
    validate_model_census(args.actors)
    verify_ancestry(args.source_commit, args.actor_commit)
    verify_ancestry(args.actor_commit, args.state_commit)
    data = json.loads((args.states/"states120.json").read_text())
    raw = (args.states/"entropy120.bin").read_bytes()
    if len(raw) != 640 or hashlib.sha256(raw).hexdigest()!=data["entropy_sha256"] or len(data["states"])!=N_STATES:
        raise RuntimeError("Frozen entropy/state dimensions differ")
    for row, item in enumerate(data["states"]):
        integers = [int.from_bytes(raw[(row*2+j)*5:(row*2+j+1)*5], "big") for j in range(2)]
        vals = [v/2**40 for v in integers]
        if item["row"]!=row or item["coordinate_numerators"]!=integers or item["state"]!=vals or item["state_hex"]!=[v.hex() for v in vals]:
            raise RuntimeError("Stored state is not the exact originally drawn binary rational")
    if data["actor_commit"] != args.actor_commit or data["source_commit"] != args.source_commit:
        raise RuntimeError("State draw did not follow the declared frozen actor commit")
    return actors, states, data


def run_catalogue(args, out, repeat=None):
    actor_receipt, state_receipt, input_data = read_inputs(args)
    imp = scientific()
    x = imp.np.array([row["state"] for row in input_data["states"]])
    if repeat is not None:
        x = x[:TIMING_STATES]
    source_context = dict(source_commit=args.source_commit, actor_commit=args.actor_commit,
                          state_commit=args.state_commit,
                          acquisition_manifest_sha256=actor_receipt["manifest_sha256"],
                          state_manifest_sha256=state_receipt["manifest_sha256"])
    records = []
    process_started = time.perf_counter()
    for index, alpha in enumerate(LEVELS):
        for arm in ARMS:
            modelpath = args.actors/"models"/f"{index}-{arm}"/"model.json"
            acquisition = json.loads((modelpath.parent/"acquisition.json").read_text())
            order = list(SERVICES)
            if repeat is not None:
                rotation = (repeat+index+ARMS.index(arm)) % len(order)
                order = order[rotation:]+order[:rotation]
            for service in order:
                batch = f"{index}-{arm}-{service}"
                cohort_started = time.perf_counter()
                sink = Events(out/"events"/f"{batch}.jsonl.gz")
                before_load = time.perf_counter()
                raw_model = modelpath.read_bytes()
                model = imp.rep.restore(json.loads(raw_model))
                load_seconds = time.perf_counter()-before_load
                cohort_rows, cohort_trials, scientific_seconds, recording_seconds = [], [], 0., 0.
                cohort_counts = {}
                try:
                    sink(dict(event="cohort-start", batch=batch, index=index, alpha=alpha,
                              arm=arm, service=service, source=source_context,
                              state=x.tolist(), model_sha256=hashlib.sha256(raw_model).hexdigest(),
                              cold_model_load_seconds=load_seconds,
                              reloaded_independently_for_each_service=True,
                              original_initial_state_batch_size=1))
                    for j, state in enumerate(x):
                        # Every returned policy is a function of this state and
                        # the previously frozen model only. A whole-batch
                        # compiler fallback cannot couple different test rows.
                        def row_sink(event):
                            sink(dict(initial_state_row=j, **event))
                        one = imp.service(state[None, :], alpha, model, service, sink=row_sink)
                        if len(one["rows"]) != 1:
                            raise ArithmeticError("Population service must return exactly one row")
                        row = one["rows"][0]
                        row.update(row=j, index=index, risk_index=index, alpha=alpha,
                            arm=arm, service=service, batch_id=batch, repeat=repeat,
                            population_observation=repeat is None,
                            source_commit=args.source_commit, actor_commit=args.actor_commit,
                            state_commit=args.state_commit,
                            model_sha256=hashlib.sha256(raw_model).hexdigest(),
                            seconds=one["seconds"], seconds_scope="actual singleton policy service, including its scientific audit trace",
                            querycounts=one["counts"], querycounts_scope="this initial state only",
                            original_initial_state_batch_size=1,
                            cold_model_load_seconds=load_seconds,
                            cold_load_scope="once for this model/service cohort; additional to singleton seconds",
                            standalone_acquisition_charge_seconds=acquisition["actual_standalone_acquisition_charge_seconds"],
                            acquisition_scope="one model/risk deployment charge, never multiplied by state count")
                        trecord = time.perf_counter()
                        append_jsonl(out/"records120.jsonl", row)
                        for original_trial in one["trials"]:
                            trial = dict(original_trial, row=j, index=index, alpha=alpha, arm=arm,
                                         service=service, batch_id=batch, repeat=repeat)
                            append_jsonl(out/"trials120.jsonl", trial)
                            cohort_trials.append(trial)
                        recording_seconds += time.perf_counter()-trecord
                        cohort_rows.append(row)
                        scientific_seconds += one["seconds"]
                        for key, count in one["counts"].items():
                            cohort_counts[key] = cohort_counts.get(key, 0)+count
                    event_count = sink.records
                    event_seconds = sink.serialization_seconds
                except BaseException as exc:
                    sink(dict(event="cohort-failed", batch=batch, exception=traceback.format_exc(),
                              completed_rows=len(cohort_rows), evidence=getattr(exc, "evidence120", None)))
                    append_jsonl(out/"ERRORS120.jsonl", dict(batch=batch, status="failed", index=index,
                        alpha=alpha, arm=arm, service=service, state=x.tolist(),
                        completed_rows=len(cohort_rows), source=source_context,
                        exception=traceback.format_exc(), partial_evidence=getattr(exc, "evidence120", None)))
                    raise
                finally:
                    sink.close()
                cohort_seconds = time.perf_counter()-cohort_started
                result = dict(rows=cohort_rows, trials=cohort_trials, counts=cohort_counts,
                    seconds=scientific_seconds, cohort_end_to_end_seconds=cohort_seconds,
                    cohort_end_to_end_scope="model loading, every singleton call, all row/trial/event recording and loop overhead",
                    decision_row_trial_recording_seconds=recording_seconds,
                    index=index, alpha=alpha, arm=arm, service=service, batch_id=batch,
                    repeat=repeat, source=source_context, cold_model_load_seconds=load_seconds,
                    event_records=event_count, event_serialization_seconds=event_seconds,
                    most_event_serialization_included_in_singleton_service_time=True,
                    original_initial_state_batch_size=1,
                    event_trace_sha256=digest(out/"events"/f"{batch}.jsonl.gz"),
                    standalone_acquisition_charge_seconds=acquisition["actual_standalone_acquisition_charge_seconds"])
                write_json(out/"batches"/f"{batch}.json", imp.plain(result))
                info = dict(batch_id=batch, index=index, alpha=alpha, arm=arm, service=service,
                    decisions=len(x), seconds=scientific_seconds,
                    cohort_end_to_end_seconds=cohort_seconds, cold_model_load_seconds=load_seconds,
                    accepted_steps=sum(row["accepted_steps"] for row in cohort_rows),
                    changed_actions=sum(row["action"]!=row["completed_incumbent_action"] for row in cohort_rows),
                    querycounts=cohort_counts, batch_sha256=digest(out/"batches"/f"{batch}.json"))
                records.append(info)
                append_jsonl(out/"PROGRESS120.jsonl", dict(event="completed-cohort", **info))
                print("COHORT", repeat, batch, len(x), round(cohort_seconds, 6), flush=True)
    write_json(out/"CATALOGUE120.json", dict(status="executed", source=source_context,
        population_observations=repeat is None, records=records,
        decisions=sum(row["decisions"] for row in records),
        scientific_batch_count=len(records), singleton_decision_calls=sum(row["decisions"] for row in records),
        inside_catalogue_seconds=time.perf_counter()-process_started,
        machine=imp.base.machine(), timing_order_rule="rotation by repeat+risk+arm index" if repeat is not None else "fixed prospectively declared order",
        no_service_or_arm_selected_by_outcome=True,
        input_state_coupling_prevented_by_singleton_services=True))


def primary(args, out):
    run_catalogue(args, out)
    receipts = []
    for repeat in range(TIMING_REPEATS):
        target = out/"timing"/f"attempt-{repeat:02d}"
        command = [sys.executable, str(Path(__file__).resolve()), "timing-one",
            "--source-commit", args.source_commit, "--actors", str(args.actors),
            "--actor-commit", args.actor_commit, "--states", str(args.states),
            "--state-commit", args.state_commit, "--output", str(target), "--repeat", str(repeat)]
        logpath = out/"timing"/f"launcher-{repeat:02d}.log"
        logpath.parent.mkdir(exist_ok=True)
        started_wall, started = time.time(), time.perf_counter()
        with logpath.open("xb") as log:
            run = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
            log.flush(); os.fsync(log.fileno())
        item = dict(repeat=repeat, command=command, exit_code=run.returncode,
            started_unix=started_wall, ended_unix=time.time(), elapsed_seconds=time.perf_counter()-started,
            log_sha256=digest(logpath), fresh_process=True, sequential_with_no_campaign_overlap=True)
        receipts.append(item)
        write_json(out/"timing"/f"launcher-{repeat:02d}.json", item)
        if run.returncode:
            raise RuntimeError("A declared timing attempt failed; no failed observation is replaced")
        print("TIMING", repeat, "completed", flush=True)
    write_json(out/"TIMING120.json", dict(status="executed", repeats=receipts,
        descriptive_only=True, external_load_or_cpu_frequency_not_controlled=True,
        all_clocks_retained=True, additional_new_iid_states=0))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("acquire", "sample", "primary", "timing-one"))
    p.add_argument("--source-commit", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--actors", type=Path)
    p.add_argument("--actor-commit")
    p.add_argument("--states", type=Path)
    p.add_argument("--state-commit")
    p.add_argument("--repeat", type=int)
    args = p.parse_args()
    if args.mode in ("sample", "primary", "timing-one") and (args.actors is None or args.actor_commit is None):
        p.error("The actor artifact directory and its immutable commit are required")
    if args.mode in ("primary", "timing-one") and (args.states is None or args.state_commit is None):
        p.error("The separately frozen held-out state artifacts and commit are required")
    if args.mode=="timing-one" and args.repeat not in range(TIMING_REPEATS):
        p.error("Only the three declared timing process indices are permitted")
    if args.actors is not None:
        args.actors = args.actors.resolve()
    if args.states is not None:
        args.states = args.states.resolve()
    source = verify_source(args.source_commit)
    out, initial = exclusive_attempt(args.output, args.mode, source)
    start = time.perf_counter()
    try:
        if args.mode=="acquire":
            acquire(args, out)
        elif args.mode=="sample":
            sample(args, out)
        elif args.mode=="primary":
            primary(args, out)
        else:
            run_catalogue(args, out, repeat=args.repeat)
        write_json(out/"EXECUTION120.json", dict(status="executed", source=source,
            mode=args.mode, exit_code=0, started_unix=initial["started_unix"], ended_unix=time.time(),
            total_seconds=time.perf_counter()-start,
            max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
        if args.mode in ("acquire", "sample"):
            name = "ACQUISITION_MANIFEST120.json" if args.mode=="acquire" else "STATE_MANIFEST120.json"
            write_json(out/name, dict(kind=args.mode, source_commit=args.source_commit,
                status="completed and awaiting immutable remote artifact commit", files=manifest_files(out)))
        else:
            write_json(out/"RESULT_MANIFEST120.json", dict(kind=args.mode,
                source_commit=args.source_commit, files=manifest_files(out)))
    except BaseException as exc:
        imp = sys.modules.get("improvement120")
        partial = imp.partial_scientific_frames(exc) if imp is not None else []
        append_jsonl(out/"FAILED120.jsonl", dict(status="failed", mode=args.mode,
            source=source, ended_unix=time.time(), total_seconds=time.perf_counter()-start,
            exception=traceback.format_exc(), partial_evidence=getattr(exc, "evidence120", None),
            partial_scientific_frames=partial,
            earlier_output_preserved=True, replacement_attempt_generated=False))
        raise


if __name__ == "__main__":
    main()
