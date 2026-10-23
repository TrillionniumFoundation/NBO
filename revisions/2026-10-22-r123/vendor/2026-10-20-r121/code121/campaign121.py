"""Frozen R121 acquisition, model/state custody and complete policy campaign.

The original scientific modules are imported only after a complete Git-byte
source check. Each acquisition budget is a separate process; every common
label and every prescribed model is actually acquired before fresh OS states.
No failure, rejected actor, timing repeat or negative comparison is replaced.
"""
from __future__ import annotations

import argparse
import copy
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

from custody121 import verify_source
from io121 import (REVISION, append_jsonl, digest, exclusive_attempt, manifest_files,
                   verify_artifacts, verify_ancestry, write_json)

ARMS = ("quadratic", "relu", "hinge", "spline", "poly2", "poly3", "grid")
LOSSES = ("value", "marginal")
BUDGETS = (5, 9)
LEVELS = (.5, .75)
N_STATES = 64
TIMING_STATES = 32
TIMING_REPEATS = 5


class Events:
    """Exclusive, flushed gzip stream; deterministic headers and retained prefix."""
    def __init__(self, path):
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        self.raw = path.open("xb")
        self.gz = gzip.GzipFile(filename="", mode="wb", fileobj=self.raw, mtime=0)
        self.text = io.TextIOWrapper(self.gz, encoding="utf-8", newline="\n")
        self.records = 0; self.serialization_seconds = 0.

    def __call__(self, event):
        started = time.perf_counter()
        self.text.write(json.dumps(dict(sequence=self.records, **event),
                                   sort_keys=True, allow_nan=False)+"\n")
        self.text.flush(); self.raw.flush(); os.fsync(self.raw.fileno())
        self.records += 1; self.serialization_seconds += time.perf_counter()-started

    def close(self):
        self.text.close(); self.raw.close()


def write_gzip_json(path, payload):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8", newline="\n") as stream:
                json.dump(payload, stream, sort_keys=True, allow_nan=False)
                stream.write("\n")
        raw.flush(); os.fsync(raw.fileno())


def scientific():
    import labels121 as lab
    import models121 as models
    return lab, models


def manifest_identity(root, name, kind, source_commit, budget=None):
    obj = json.loads((Path(root)/name).read_text())
    if obj.get("kind") != kind or obj.get("source_commit") != source_commit:
        raise RuntimeError("Artifact kind or generating source differs: "+name)
    if budget is not None and obj.get("budget") != budget:
        raise RuntimeError("The acquisition budget differs from the frozen artifact")
    return obj


def model_census(root, source_commit, budget):
    obj = manifest_identity(root, "ACQUISITION_MANIFEST121.json", "acquire", source_commit, budget)
    expected = {f"models/{i}-{arm}-{loss}/model.json"
                for i in range(2) for arm in ARMS for loss in LOSSES}
    actual = {item["path"] for item in obj["files"] if Path(item["path"]).name == "model.json"}
    if actual != expected:
        raise RuntimeError("Exactly twenty-eight risk/arm/loss models are required per budget")
    for relative in sorted(expected):
        model = json.loads((Path(root)/relative).read_text())
        index, arm, loss = Path(relative).parent.name.split("-")
        if (model.get("kind") != "r121-anchored-root-critic" or model.get("loss") != loss or
            model["basis"].get("arm") != arm or model["basis"].get("budget") != budget or
            model.get("source_commit") != source_commit or model.get("index") != int(index)):
            raise RuntimeError("Stored actor identity differs: "+relative)
    return expected


def acquisition_dirs(args):
    return {5: args.actors5, 9: args.actors9}


def verify_actors(args):
    receipts = {}
    for budget, directory in acquisition_dirs(args).items():
        receipts[str(budget)] = verify_artifacts(directory, "ACQUISITION_MANIFEST121.json", args.actor_commit)
        model_census(directory, args.source_commit, budget)
    verify_ancestry(args.source_commit, args.actor_commit)
    return receipts


def acquire(args, out):
    import_started = time.perf_counter(); lab, models = scientific()
    import_seconds = time.perf_counter()-import_started
    started = time.perf_counter(); risk_receipts = []; phase_intervals = []
    for index, alpha in enumerate(LEVELS):
        label_start = time.perf_counter(); label_wall = time.time()
        sink = Events(out/"events"/f"labels-{index}.jsonl.gz")
        try:
            sink(dict(event="labels-start", index=index, alpha=alpha, budget=args.budget,
                      source_commit=args.source_commit, no_heldout_states_available=True))
            labels = lab.acquire_labels(args.budget, alpha, sink)
            labels.update(index=index, source_commit=args.source_commit)
            serialize = time.perf_counter()
            write_json(out/f"labels-{index}.json", lab.inherited.plain(labels))
            label_file_write_seconds = time.perf_counter()-serialize
            sink(dict(event="labels-artifact-complete", path=f"labels-{index}.json",
                      sha256=digest(out/f"labels-{index}.json")))
        except BaseException as exc:
            sink(dict(event="labels-failed", exception=traceback.format_exc(),
                      partial_evidence=getattr(exc,"evidence121",None)))
            raise
        finally:
            sink.close()
        label_seconds = time.perf_counter()-label_start
        label_phase = dict(kind="risk-label-acquisition", index=index, alpha=alpha,
                           started_unix=label_wall, ended_unix=time.time(), seconds=label_seconds,
                           label_solver_trace_seconds=labels["seconds"],
                           label_file_write_seconds=label_file_write_seconds,
                           event_records=sink.records, event_serialization_seconds=sink.serialization_seconds,
                           counts=labels["counts"], label_sha256=digest(out/f"labels-{index}.json"))
        phase_intervals.append(label_phase)
        append_jsonl(out/"ACQUISITION_PROGRESS121.jsonl", dict(event="labels-complete", **label_phase))
        model_records = {}; relu_cache = {}
        for arm in ARMS:
            for loss in LOSSES:
                folder = out/"models"/f"{index}-{arm}-{loss}"
                phase_start = time.perf_counter(); phase_wall = time.time()
                folder.mkdir(parents=True, exist_ok=False)
                events = Events(folder/"fit-events.jsonl.gz")
                assembly_seconds = 0.; copy_seconds = 0.; identity_seconds = 0.
                try:
                    desc = models.definition(arm,args.budget)
                    events(dict(event="model-acquisition-start", index=index, alpha=alpha,
                                arm=arm, loss=loss, budget=args.budget, basis=desc,
                                labels_sha256=label_phase["label_sha256"]))
                    if arm == "hinge":
                        original_model, original_fit, original_design, parent_cost = relu_cache[loss]
                        tick = time.perf_counter()
                        model, fit = models.hinge_copy(original_model,original_fit)
                        copy_seconds = time.perf_counter()-tick
                        tick = time.perf_counter(); design = models.training_design(desc,labels)
                        assembly_seconds = time.perf_counter()-tick
                        tick = time.perf_counter()
                        for key in ("value_matrix","derivative_matrix","value_lower","value_upper",
                                    "derivative_lower","derivative_upper"):
                            if not lab.np.array_equal(design[key],original_design[key]):
                                raise ArithmeticError("Identical ReLU/hinge design failed exact binary equality")
                        if model["theta"] != original_model["theta"]:
                            raise ArithmeticError("Hinge readout differs from the paid ReLU readout")
                        identity_seconds = time.perf_counter()-tick
                        fit.update(hinge_own_design_seconds=assembly_seconds, hinge_copy_seconds=copy_seconds,
                                   hinge_identity_check_seconds=identity_seconds,
                                   parent_relu_model_sha256=digest(out/"models"/f"{index}-relu-{loss}"/"model.json"),
                                   parent_relu_model_phase_charge_seconds=parent_cost)
                        events(dict(event="hinge-identity-complete", full_parent_fit_charged=True,
                                    exact_design_identity=True, exact_readout_identity=True,
                                    actual_new_solver_invocation=False))
                    else:
                        model, fit, design = models.fit(desc,labels,loss,events)
                        parent_cost = 0.
                    model.update(index=index, alpha=alpha, source_commit=args.source_commit,
                                 label_sha256=label_phase["label_sha256"])
                    tick = time.perf_counter()
                    write_gzip_json(folder/"design.json.gz",models._plain(design))
                    design_write_seconds = time.perf_counter()-tick
                    tick = time.perf_counter(); write_json(folder/"model.json",model)
                    model_write_seconds = time.perf_counter()-tick
                    tick = time.perf_counter(); write_json(folder/"fit.json",models._plain(fit))
                    fit_write_seconds = time.perf_counter()-tick
                    events(dict(event="model-files-complete", model_sha256=digest(folder/"model.json"),
                                fit_sha256=digest(folder/"fit.json"), design_sha256=digest(folder/"design.json.gz"),
                                design_write_seconds=design_write_seconds, model_write_seconds=model_write_seconds,
                                fit_write_seconds=fit_write_seconds))
                except BaseException as exc:
                    events(dict(event="model-acquisition-failed", exception=traceback.format_exc(),
                                fit_evidence=getattr(exc,"fit121",None)))
                    raise
                finally:
                    events.close()
                before_receipt = time.perf_counter()-phase_start
                # The full phase, including this receipt, is measured outside
                # the receipt below. No timestamp or self-referential total is
                # fabricated inside its own scientific artifact.
                acquisition = dict(index=index,alpha=alpha,budget=args.budget,arm=arm,loss=loss,
                    source_commit=args.source_commit, labels_sha256=label_phase["label_sha256"],
                    model_sha256=digest(folder/"model.json"), model_bytes=(folder/"model.json").stat().st_size,
                    fit_sha256=digest(folder/"fit.json"),design_sha256=digest(folder/"design.json.gz"),
                    feature_count=desc["feature_count"], label_phase_seconds=label_seconds,
                    original_root_label_contexts=labels["original_root_Q_contexts"],
                    original_label_counts_if_standalone=labels["counts"],
                    fit_design_seconds=fit["design_seconds"] if arm!="hinge" else assembly_seconds,
                    solver_seconds=fit["solver_seconds"] if arm!="hinge" else 0.,
                    own_actual_solver_invocation=arm!="hinge", copied_readout=arm=="hinge",
                    parent_relu_model_phase_charge_seconds=parent_cost,
                    full_relu_charge_required_if_hinge=arm=="hinge",
                    design_write_seconds=design_write_seconds, model_write_seconds=model_write_seconds,
                    fit_write_seconds=fit_write_seconds, event_serialization_seconds=events.serialization_seconds,
                    model_phase_before_this_receipt_seconds=before_receipt,
                    full_model_phase_in_ACQUISITION121=True,
                    label_targets_identical_for_every_arm_and_loss=True,
                    no_heldout_information=True,
                    exact_fit_optimality_is_separate_rational_audit=True,
                    charge_scope="Full common labels plus own complete acquisition phase; hinge also pays the whole parent ReLU phase. Shared source/import and residual full-process costs remain separately explicit in the final cost ledger.")
                write_json(folder/"acquisition.json",acquisition)
                phase_seconds=time.perf_counter()-phase_start
                model_phase = dict(kind="model-acquisition",index=index,alpha=alpha,budget=args.budget,
                    arm=arm,loss=loss,started_unix=phase_wall,ended_unix=time.time(),seconds=phase_seconds,
                    own_model_phase_seconds=phase_seconds,parent_relu_model_phase_charge_seconds=parent_cost,
                    label_phase_seconds=label_seconds,
                    standalone_measured_component_subtotal_seconds=label_seconds+phase_seconds+parent_cost,
                    source_and_import_and_common_residual_costs_additional=True,
                    receipt_sha256=digest(folder/"acquisition.json"),
                    model_sha256=acquisition["model_sha256"],model_bytes=acquisition["model_bytes"],
                    event_records=events.records,event_serialization_seconds=events.serialization_seconds)
                phase_intervals.append(model_phase)
                model_records[f"{arm}-{loss}"]=model_phase
                if arm=="relu":
                    relu_cache[loss]=(model,fit,design,phase_seconds)
                append_jsonl(out/"ACQUISITION_PROGRESS121.jsonl",dict(event="model-complete",**model_phase))
                print("MODEL",args.budget,index,arm,loss,"saved",round(phase_seconds,6),flush=True)
        risk_receipts.append(dict(index=index,alpha=alpha,labels=label_phase,models=model_records))
    measured=sum(row["seconds"] for row in phase_intervals)
    total=time.perf_counter()-started
    result=dict(kind="r121-complete-original-root-acquisition",status="executed",budget=args.budget,
        source_commit=args.source_commit,records=risk_receipts,phase_intervals=phase_intervals,
        independent_budget_process=True,common_sites_recomputed_not_allocated_from_other_budget=True,
        frozen_model_count=28,independent_solver_fits=24,exact_hinge_copies=4,
        original_Q_contexts=sum(13*args.budget**2 for _ in LEVELS),
        main_marginal_contexts=sum(5*args.budget**2 for _ in LEVELS),
        scientific_import_seconds=import_seconds,source_gate_seconds=args.source_gate_seconds,
        total_acquisition_body_seconds=total,
        measured_nonoverlapping_phase_seconds=measured,
        remaining_inside_acquisition_bookkeeping_seconds=max(0.,total-measured),
        source_and_import_outside_acquisition_body=True,
        final_summary_hash_manifest_shutdown_costs_in_outer_process_receipt=True,
        standalone_charge_rule="For a learned risk/model pay its complete risk labels and own complete model phase; hinge additionally pays its matching ReLU phase. Add the full common source/import/residual process overhead. Exclude competing models' fits and the other risk's labels; sum actual process clocks separately for whole research cost.",
        validation_cost_scope="Independent rational training and policy audits are paid separately as research validation, never silently treated as free or included in deployed production certificate clocks.",
        no_model_selected_by_outcome=True,heldout_states_available=False,new_random_samples=0,
        machine=lab.inherited.base.machine())
    write_json(out/"ACQUISITION121.json",result)


def sample(args,out):
    actors=verify_actors(args)
    # No scientific import occurs in sampling. Every coordinate has its own
    # five OS bytes, and the exact draw is stored before any economic query.
    entropy=os.urandom(N_STATES*2*5)
    with (out/"entropy121.bin").open("xb") as stream:
        stream.write(entropy);stream.flush();os.fsync(stream.fileno())
    rows=[]
    for row in range(N_STATES):
        integers=[int.from_bytes(entropy[(2*row+j)*5:(2*row+j+1)*5],"big") for j in range(2)]
        x=[v/2**40 for v in integers]
        rows.append(dict(row=row,coordinate_numerators=integers,denominator=2**40,
                         state=x,state_hex=[v.hex() for v in x]))
    write_json(out/"states121.json",dict(kind="r121-fresh-heldout-states",source_commit=args.source_commit,
        actor_commit=args.actor_commit,actors=actors,population="product discrete uniform on {0,...,2^40-1}/2^40 in two coordinates",
        rows=N_STATES,dimension=2,states=rows,entropy_bytes=len(entropy),
        entropy_sha256=hashlib.sha256(entropy).hexdigest(),
        coordinates_independently_acquired_from_os_bytes=True,
        common_states_across_risks_budgets_arms_losses=True,iid_unit="initial state row",
        duplicate_draws_retained=True,original_innovation_law="continuous uniform on [-1/32,1/32] unchanged",
        acquired_after_all_56_models_were_committed=True,no_economic_evaluation_performed=True))
    print("SAMPLE",N_STATES,"exact state rows saved; no economic evaluation",flush=True)


def read_inputs(args):
    actors=verify_actors(args)
    state_receipt=verify_artifacts(args.states,"STATE_MANIFEST121.json",args.state_commit)
    manifest_identity(args.states,"STATE_MANIFEST121.json","sample",args.source_commit)
    verify_ancestry(args.actor_commit,args.state_commit)
    data=json.loads((args.states/"states121.json").read_text());raw=(args.states/"entropy121.bin").read_bytes()
    if (data.get("kind")!="r121-fresh-heldout-states" or data.get("source_commit")!=args.source_commit or
        data.get("actor_commit")!=args.actor_commit or len(raw)!=640 or
        hashlib.sha256(raw).hexdigest()!=data["entropy_sha256"] or len(data["states"])!=N_STATES):
        raise RuntimeError("Frozen actor/state custody or exact entropy census differs")
    for row,item in enumerate(data["states"]):
        integers=[int.from_bytes(raw[(2*row+j)*5:(2*row+j+1)*5],"big") for j in range(2)]
        x=[v/2**40 for v in integers]
        if (item["row"]!=row or item["coordinate_numerators"]!=integers or item["denominator"]!=2**40 or
            item["state"]!=x or item["state_hex"]!=[v.hex() for v in x]):
            raise RuntimeError("A state differs from the exact original OS coordinate draw")
    for budget in BUDGETS:
        if data["actors"][str(budget)]["manifest_sha256"]!=actors[str(budget)]["manifest_sha256"]:
            raise RuntimeError("Sample was not acquired after these same actor artifacts")
    return actors,state_receipt,data


def policies():
    return [(0,"online","online")]+[(budget,arm,loss) for budget in BUDGETS for arm in ARMS for loss in LOSSES]


def load_policy(args,index,budget,arm,loss):
    tick=time.perf_counter()
    if arm=="online":
        # The direct solver is source-defined: no unreported trained artifact.
        definition=dict(kind="original-online-policy",index=index,alpha=LEVELS[index],budget=0,
                        midpoints=512,derivative_iterations=24,source_commit=args.source_commit)
        raw=json.dumps(definition,sort_keys=True,allow_nan=False).encode()
        model=None;cost=dict(standalone_measured_component_subtotal_seconds=0.,
                            acquisition_component_scope="no learned labels or fit; shared source/import/process setup and its actual online service remain charged")
    else:
        directory=acquisition_dirs(args)[budget]
        path=directory/"models"/f"{index}-{arm}-{loss}"/"model.json"
        raw=path.read_bytes();model=json.loads(raw)
        # This already verified cost record is read with the deployment load;
        # its I/O is not silently excluded from the measured load.
        summary=json.loads((directory/"ACQUISITION121.json").read_text())
        cost=summary["records"][index]["models"][f"{arm}-{loss}"]
    return model,cost,hashlib.sha256(raw).hexdigest(),len(raw),time.perf_counter()-tick


def run_catalogue(args,out,repeat=None):
    gate_started=time.perf_counter();actors,states,data=read_inputs(args)
    artifact_gate_seconds=time.perf_counter()-gate_started
    import_started=time.perf_counter();lab,models=scientific();import_seconds=time.perf_counter()-import_started
    x=[row["state"] for row in data["states"]]
    if repeat is not None:x=x[:TIMING_STATES]
    source=dict(source_commit=args.source_commit,actor_commit=args.actor_commit,state_commit=args.state_commit,
                acquisition_manifest_sha256={k:v["manifest_sha256"] for k,v in actors.items()},
                state_manifest_sha256=states["manifest_sha256"])
    body_started=time.perf_counter();cohorts=[];cohort_phase_seconds=0.
    for index,alpha in enumerate(LEVELS):
        order=policies()
        if repeat is not None:
            shift=(7*repeat+index)%len(order);order=order[shift:]+order[:shift]
        for budget,arm,loss in order:
            batch=f"{index}-{budget}-{arm}-{loss}"
            tick=time.perf_counter();wall=time.time();sink=Events(out/"events"/f"{batch}.jsonl.gz")
            cohort_rows=[];cohort_attempts=[];counts={};scientific_seconds=0.;recording_seconds=0.
            try:
                model,cost,model_hash,model_bytes,load_seconds=load_policy(args,index,budget,arm,loss)
                sink(dict(event="cohort-start",index=index,alpha=alpha,budget=budget,arm=arm,loss=loss,
                    repeat=repeat,state=x,source=source,model_sha256=model_hash,model_bytes=model_bytes,
                    cold_model_load_seconds=load_seconds,source_defined_online_model=arm=="online",
                    original_initial_state_batch_size=1))
                for row,state in enumerate(x):
                    def row_sink(event):sink(dict(initial_state_row=row,**event))
                    one=lab.service(state,alpha,model,row_sink)
                    rec=one["row"]
                    rec.update(index=index,risk_index=index,row=row,alpha=alpha,budget=budget,arm=arm,loss=loss,
                        service="completed",batch_id=batch,repeat=repeat,population_observation=repeat is None,
                        source_commit=args.source_commit,actor_commit=args.actor_commit,state_commit=args.state_commit,
                        original_initial_state_batch_size=1,model_sha256=model_hash,model_bytes=model_bytes,
                        seconds_scope="actual singleton complete policy service including its original primitive and candidate trace writes",
                        cold_model_load_seconds=load_seconds,cold_load_scope="once per policy/risk cohort, additional to singleton seconds",
                        standalone_acquisition_component_subtotal_seconds=cost["standalone_measured_component_subtotal_seconds"],
                        acquisition_scope="measured labels and own fit/storage components; shared source/import/residual process and independent research validation are separately explicit",
                        querycounts=one["counts"],all_first_proposals_retained_for_independent_evaluation=True)
                    save=time.perf_counter();append_jsonl(out/"records121.jsonl",rec)
                    for j,attempt in enumerate(one["attempts"]):
                        event=dict(attempt,index=index,row=row,alpha=alpha,budget=budget,arm=arm,loss=loss,
                                   batch_id=batch,repeat=repeat,attempt_index=j)
                        append_jsonl(out/"attempts121.jsonl",event);cohort_attempts.append(event)
                    append_jsonl(out/"actors121.jsonl",dict(index=index,row=row,alpha=alpha,budget=budget,
                        arm=arm,loss=loss,batch_id=batch,repeat=repeat,actor_trace=one["actor_trace"]))
                    recording_seconds+=time.perf_counter()-save;scientific_seconds+=one["seconds"]
                    cohort_rows.append(rec)
                    for name,value in one["counts"].items():counts[name]=counts.get(name,0)+value
            except BaseException as exc:
                failure=dict(batch_id=batch,index=index,alpha=alpha,budget=budget,arm=arm,loss=loss,repeat=repeat,
                    source=source,completed_rows=len(cohort_rows),exception=traceback.format_exc(),
                    partial_evidence=getattr(exc,"evidence121",None),all_completed_and_failed_prefixes_retained=True)
                sink(dict(event="cohort-failed",**failure));append_jsonl(out/"ERRORS121.jsonl",failure)
                raise
            finally:sink.close()
            cohort_seconds=time.perf_counter()-tick;cohort_phase_seconds+=cohort_seconds
            result=dict(index=index,alpha=alpha,budget=budget,arm=arm,loss=loss,batch_id=batch,repeat=repeat,
                source=source,rows=cohort_rows,attempts=cohort_attempts,counts=counts,
                singleton_service_seconds=scientific_seconds,cohort_end_to_end_seconds=cohort_seconds,
                cohort_end_to_end_scope="event open/close, actual model and cost-record loading, singleton calls, all scientific/row/attempt/actor recording, and loop overhead",
                cold_model_load_seconds=load_seconds,decision_and_attempt_recording_seconds=recording_seconds,
                event_records=sink.records,event_serialization_seconds=sink.serialization_seconds,
                event_serialization_already_included_not_additive=True,
                event_trace_sha256=digest(out/"events"/f"{batch}.jsonl.gz"),
                started_unix=wall,ended_unix=time.time(),model_sha256=model_hash,model_bytes=model_bytes,
                standalone_acquisition_component_subtotal_seconds=cost["standalone_measured_component_subtotal_seconds"],
                shared_source_import_verification_summary_and_validation_costs_separate=True,
                original_initial_state_batch_size=1)
            write_json(out/"batches"/f"{batch}.json",lab.inherited.plain(result))
            summary=dict(index=index,alpha=alpha,budget=budget,arm=arm,loss=loss,batch_id=batch,repeat=repeat,
                decisions=len(x),qualified=sum(r["qualified"] for r in cohort_rows),
                first_rejections=sum(r["first_rejected"] for r in cohort_rows),
                final_different_from_first=sum(r["first_proposal_action"] is not None and r["action"]!=r["first_proposal_action"] for r in cohort_rows),
                unavailable_first_proposals=sum(r["first_proposal_action"] is None for r in cohort_rows),
                numerical_service_failures=sum(r["numerical_service_failure"] for r in cohort_rows),
                exact_fallbacks=sum(r["exact_fallback"] for r in cohort_rows),
                singleton_service_seconds=scientific_seconds,cohort_end_to_end_seconds=cohort_seconds,
                cold_model_load_seconds=load_seconds,counts=counts,
                model_sha256=model_hash,model_bytes=model_bytes,
                standalone_acquisition_component_subtotal_seconds=cost["standalone_measured_component_subtotal_seconds"],
                batch_sha256=digest(out/"batches"/f"{batch}.json"))
            cohorts.append(summary);append_jsonl(out/"PROGRESS121.jsonl",dict(event="cohort-complete",**summary))
            print("COHORT",repeat,batch,len(x),round(cohort_seconds,6),flush=True)
    total=sum(row["decisions"] for row in cohorts);expected=(N_STATES if repeat is None else TIMING_STATES)*58
    if total!=expected or len(cohorts)!=58:raise ArithmeticError("Complete prospective cohort census differs")
    write_json(out/"CATALOGUE121.json",dict(status="executed",source=source,records=cohorts,
        decisions=total,cohorts=58,population_observations=repeat is None,
        source_gate_seconds=args.source_gate_seconds,artifact_gate_seconds=artifact_gate_seconds,
        scientific_import_seconds=import_seconds,inside_catalogue_seconds=time.perf_counter()-body_started,
        measured_cohort_phase_seconds=cohort_phase_seconds,
        final_summary_hash_manifest_shutdown_in_external_process_cost=True,
        timing_order_rule="rotate full29-policy order by (7*repeat+risk)%29" if repeat is not None else "online then budget, declared arm, value then marginal",
        duplicate_initial_states_retained=True,all_actions_and_rejections_retained=True,
        initial_state_batch_size=1,machine=lab.inherited.base.machine(),
        no_policy_or_state_selected_by_outcome=True))


def primary(args,out):
    run_catalogue(args,out);receipts=[]
    for repeat in range(TIMING_REPEATS):
        target=out/"timing"/f"attempt-{repeat:02d}"
        command=[sys.executable,str(Path(__file__).resolve()),"timing-one","--source-commit",args.source_commit,
                 "--actors5",str(args.actors5),"--actors9",str(args.actors9),"--actor-commit",args.actor_commit,
                 "--states",str(args.states),"--state-commit",args.state_commit,
                 "--repeat",str(repeat),"--output",str(target)]
        logpath=out/"timing"/f"launcher-{repeat:02d}.log";logpath.parent.mkdir(parents=True,exist_ok=True)
        wall=time.time();tick=time.perf_counter()
        with logpath.open("xb") as stream:
            run=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT)
            stream.flush();os.fsync(stream.fileno())
        receipt=dict(repeat=repeat,command=command,exit_code=run.returncode,started_unix=wall,ended_unix=time.time(),
            elapsed_seconds=time.perf_counter()-tick,log_sha256=digest(logpath),
            fresh_process=True,serial_processes=True,external_load_or_frequency_not_controlled=True)
        write_json(out/"timing"/f"launcher-{repeat:02d}.json",receipt);receipts.append(receipt)
        if run.returncode:raise RuntimeError("A declared timing process failed; no replacement timing was generated")
        print("TIMING",repeat,"complete",flush=True)
    # No scientific solver is rerun by these deterministic saved-record checks.
    primary_rows={tuple(row[k] for k in ("index","row","budget","arm","loss")):row
                  for row in read_jsonl(out/"records121.jsonl")}
    comparisons=0
    for repeat in range(TIMING_REPEATS):
        rows=read_jsonl(out/"timing"/f"attempt-{repeat:02d}"/"records121.jsonl")
        if len(rows)!=1856:raise ArithmeticError("Timing decision census differs")
        for row in rows:
            key=tuple(row[k] for k in ("index","row","budget","arm","loss"));old=primary_rows[key]
            for name in ("state_hex","action_hex","first_proposal_action_hex","qualified","first_rejected"):
                if row[name]!=old[name]:raise ArithmeticError("Repeated policy outcome differs: "+str((repeat,key,name)))
            comparisons+=1
    if comparisons!=9280:raise ArithmeticError("Repeated action identity census differs")
    write_json(out/"TIMING121.json",dict(status="executed",repeats=receipts,descriptive_only=True,
        all_clocks_retained=True,new_iid_states=0,full_saved_record_action_identity_checks=comparisons,
        scientific_solver_rerun_for_identity_check=False,
        identity_failure_would_fail_attempt_without_replacing_any_clock=True))


def read_jsonl(path):
    with Path(path).open() as stream:return [json.loads(line) for line in stream if line.strip()]


def main():
    p=argparse.ArgumentParser();p.add_argument("mode",choices=("acquire","sample","primary","timing-one"))
    p.add_argument("--source-commit",required=True);p.add_argument("--output",type=Path,required=True)
    p.add_argument("--budget",type=int,choices=BUDGETS);p.add_argument("--actors5",type=Path);p.add_argument("--actors9",type=Path)
    p.add_argument("--actor-commit");p.add_argument("--states",type=Path);p.add_argument("--state-commit");p.add_argument("--repeat",type=int)
    args=p.parse_args()
    if args.mode=="acquire" and args.budget is None:p.error("One separately executed acquisition budget is required")
    if args.mode in ("sample","primary","timing-one") and (args.actors5 is None or args.actors9 is None or args.actor_commit is None):
        p.error("Both frozen acquisition directories and their immutable actor commit are required")
    if args.mode in ("primary","timing-one") and (args.states is None or args.state_commit is None):
        p.error("Separately frozen held-out states and their immutable commit are required")
    if args.mode=="timing-one" and args.repeat not in range(TIMING_REPEATS):p.error("Only five declared timing indices are permitted")
    for name in ("actors5","actors9","states"):
        value=getattr(args,name)
        if value is not None:setattr(args,name,value.resolve())
    tick=time.perf_counter();source=verify_source(args.source_commit);args.source_gate_seconds=time.perf_counter()-tick
    out,initial=exclusive_attempt(args.output,args.mode,source);started=time.perf_counter()
    try:
        if args.mode=="acquire":acquire(args,out)
        elif args.mode=="sample":sample(args,out)
        elif args.mode=="primary":primary(args,out)
        else:run_catalogue(args,out,args.repeat)
        write_json(out/"EXECUTION121.json",dict(status="executed",exit_code=0,mode=args.mode,budget=args.budget,
            source=source,started_unix=initial["started_unix"],ended_unix=time.time(),
            total_after_initial_receipt_seconds=time.perf_counter()-started,
            source_gate_seconds=args.source_gate_seconds,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            actual_external_process_total_is_separate=True,all_failed_prefixes_preserved=True))
        name={"acquire":"ACQUISITION_MANIFEST121.json","sample":"STATE_MANIFEST121.json"}.get(args.mode,"RESULT_MANIFEST121.json")
        write_json(out/name,dict(kind=args.mode,budget=args.budget,source_commit=args.source_commit,
            actor_commit=args.actor_commit,state_commit=args.state_commit,files=manifest_files(out),
            status="completed; immutable publication occurs separately"))
    except BaseException as exc:
        lab=sys.modules.get("labels121")
        partial=lab.partial_scientific_frames(exc) if lab is not None else []
        append_jsonl(out/"FAILED121.jsonl",dict(status="failed",mode=args.mode,budget=args.budget,source=source,
            ended_unix=time.time(),elapsed_seconds=time.perf_counter()-started,exception=traceback.format_exc(),
            partial_evidence=getattr(exc,"evidence121",None),fit_evidence=getattr(exc,"fit121",None),
            partial_scientific_frames=partial,earlier_output_preserved=True,replacement_attempt_generated=False))
        raise


if __name__=="__main__":main()
