"""Read-only R121 reporting under the prospectively frozen REPORTING_SPEC.

Only the standard library is used. This program does not acquire labels, fit
models, evaluate an economic oracle, draw data, retime a service, or change any
experimental rule. Fractions denote the exact numbers in completed records.
The reporting source is deposited with final author S, not misdated as F.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as F
from functools import lru_cache
import gzip
import hashlib
import io
import itertools
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback

ARMS=("quadratic","relu","hinge","spline","poly2","poly3","grid")
LOSSES=("value","marginal")
BUDGETS=(5,9)
VOLUMES=(64,256,1024,16384)
RISKS=(F(1,2),F(3,4))
TAU=F(1,256)
WIDTH=F(1,8192)
K=F(21097,4096)
SCENARIOS=("primary64","timing0","timing1","timing2","timing3","timing4")
COUNTS=Counter()


def require(condition,message):
    COUNTS["record_assertions"]+=1
    if not condition:raise ArithmeticError(message)


def exact(value):
    if isinstance(value,F):return value
    if isinstance(value,dict) and set(value)>={"numerator","denominator"}:
        return F(value["numerator"],value["denominator"])
    return F(value)


def encoded(value):
    if isinstance(value,F):return str(value)
    if isinstance(value,Path):return str(value)
    if isinstance(value,dict):return {str(k):encoded(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [encoded(v) for v in value]
    return value


def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda:stream.read(1<<20),b""):h.update(block)
    return h.hexdigest()


def file_identity(path):
    p=Path(path);size=p.stat().st_size;h=hashlib.sha256();g=hashlib.sha1(b"blob "+str(size).encode()+b"\0")
    with p.open("rb") as stream:
        for block in iter(lambda:stream.read(1<<20),b""):h.update(block);g.update(block)
    return dict(bytes=size,sha256=h.hexdigest(),git_blob=g.hexdigest())


def write_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="utf-8") as stream:
        json.dump(encoded(value),stream,sort_keys=True,indent=2,allow_nan=False);stream.write("\n")
        stream.flush();os.fsync(stream.fileno())


def append_jsonl(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a",encoding="utf-8") as stream:
        stream.write(json.dumps(encoded(value),sort_keys=True,allow_nan=False)+"\n")
        stream.flush();os.fsync(stream.fileno())


def group(row):return (int(row["index"]),int(row["budget"]),row["arm"],row["loss"])
def identity(row):return (int(row["index"]),int(row["row"]),int(row["budget"]),row["arm"],row["loss"])
def group_row(key):return dict(zip(("index","budget","arm","loss"),key))
def ident_row(key):return dict(zip(("index","row","budget","arm","loss"),key))
def label(key):return "/".join(map(str,key))


def groups():
    return [key for i in range(2) for key in
            ([(i,0,"online","online")]+[(i,b,a,l) for b in BUDGETS for a in ARMS for l in LOSSES])]


GROUPS=tuple(groups())


def mean(values):
    require(bool(values),"Nonempty prescribed aggregation")
    return sum(map(exact,values),F(0))/len(values)


def median(values):
    values=sorted(map(exact,values));n=len(values)
    require(n>0,"Nonempty descriptive clocks")
    return values[n//2] if n%2 else (values[n//2-1]+values[n//2])/2


def sign_interval(lo,hi):
    require(lo<=hi,"Ordered signed interval")
    if lo==hi==0:return "exact-zero"
    if hi<0:return "strict-negative"
    if lo>0:return "strict-positive"
    return "contains-zero"


def sqrt_upper(value,bits=48):
    value=exact(value);require(value>=0,"Nonnegative action-error square bound")
    scale=1<<bits;n=math.isqrt((value.numerator<<(2*bits))//value.denominator)
    if F(n*n,scale*scale)<value:n+=1
    return F(n,scale)


class Inputs:
    """Byte custody with native source and separately materialized evidence."""
    def __init__(self,args):
        self.args=args;self.revision=args.revision.resolve();self.evidence=args.evidence_root.resolve()
        self.repository=args.repository.resolve();self.source_prefix=self.revision.relative_to(self.repository)
        self.entries={};self.trees={};self.cache={}

    def path(self,value):
        path=Path(value)
        return path.resolve() if path.is_absolute() else (self.evidence/path).resolve()

    def name(self,path):
        path=Path(path).resolve()
        try:return path.relative_to(self.evidence).as_posix()
        except ValueError:return "source:"+path.relative_to(self.revision).as_posix()

    def track(self,path):
        path=Path(path).resolve();name=self.name(path)
        if name not in self.entries:
            info=file_identity(path);stat=path.stat()
            self.entries[name]=dict(info,path=str(path),relative=name,mtime_ns=stat.st_mtime_ns)
        return self.entries[name]

    def read(self,path):
        path=Path(path).resolve();self.track(path);key=str(path)
        if key not in self.cache:
            opener=gzip.open if str(path).endswith(".gz") else open
            with opener(path,"rt",encoding="utf-8") as stream:self.cache[key]=json.load(stream)
        return self.cache[key]

    def rows(self,path):
        path=Path(path).resolve();self.track(path)
        opener=gzip.open if str(path).endswith(".gz") else open
        with opener(path,"rt",encoding="utf-8") as stream:
            return [json.loads(line) for line in stream if line.strip()]

    def tree(self,commit):
        require(len(commit)==40 and all(c in "0123456789abcdef" for c in commit),"Complete immutable commit")
        if commit not in self.trees:
            command=["git","-C",str(self.repository),"ls-tree","-r","-z",commit,"--",self.source_prefix.as_posix()]
            run=subprocess.run(command,check=True,capture_output=True);entries={}
            for part in run.stdout.split(b"\0"):
                if not part:continue
                metadata,name=part.split(b"\t",1);mode,kind,blob=metadata.decode().split()
                entries[name.decode()]=(mode,kind,blob)
            self.trees[commit]=entries
        return self.trees[commit]

    def git_binding(self,path,commit,source=False):
        path=Path(path).resolve();relative=path.relative_to(self.revision if source else self.evidence)
        name=(self.source_prefix/relative).as_posix();entry=self.tree(commit).get(name)
        require(entry is not None and entry[0] in ("100644","100755") and entry[1]=="blob","Regular immutable Git input: "+name)
        info=self.track(path);require(entry[2]==info["git_blob"],"Actual bytes equal immutable Git blob: "+name)
        COUNTS["git_bound_input_files"]+=1
        return dict(path=name,commit=commit,git_blob=entry[2],sha256=info["sha256"])

    def source(self):
        manifest=self.revision/"SOURCE_FREEZE121.json";obj=self.read(manifest)
        bound=[self.git_binding(manifest,self.args.source_commit,True)]
        require("PROTOCOL121.md" in obj["scientific_files"] and "REPORTING_SPEC121.md" in obj["scientific_files"],"Prospective scientific and reporting specifications")
        for name,wanted in sorted(obj["scientific_files"].items()):
            path=(self.revision/name).resolve();path.relative_to(self.revision)
            require(self.track(path)["sha256"]==wanted,"Frozen scientific SHA: "+name)
            bound.append(self.git_binding(path,self.args.source_commit,True))
        for early,late in ((self.args.source_commit,self.args.actor_commit),(self.args.actor_commit,self.args.state_commit)):
            require(early!=late,"Distinct F/M/D")
            run=subprocess.run(["git","-C",str(self.repository),"merge-base","--is-ancestor",early,late],capture_output=True)
            require(run.returncode==0,"Actual F to M to D ancestry")
        return dict(source_commit=self.args.source_commit,actor_commit=self.args.actor_commit,state_commit=self.args.state_commit,
                    files=len(bound),source_manifest_sha256=self.track(manifest)["sha256"],
                    scientific_imports_performed=False,reporting_source_deposited_later_not_misdated_as_F=True)

    def artifact(self,root,name,commit,kind,budget=None):
        root=Path(root).resolve();manifest=root/name;obj=self.read(manifest)
        require(obj.get("kind")==kind and obj.get("source_commit")==self.args.source_commit,"Artifact kind/source F")
        if budget is not None:require(obj.get("budget")==budget,"Artifact declared budget")
        self.git_binding(manifest,commit)
        seen=set()
        for item in obj["files"]:
            relative=item["path"];require(relative not in seen,"Unique artifact member");seen.add(relative)
            path=(root/relative).resolve();path.relative_to(root);info=self.track(path)
            require(all(info[k]==item[k] for k in ("bytes","sha256","git_blob")),"Manifest actual member bytes: "+relative)
            self.git_binding(path,commit)
        return obj

    def immutable(self):
        # Structured records used by the arithmetic are rehashed. Large
        # manifest-only payloads retain their already verified bytes plus an
        # end-of-analysis size/mtime check; no second scientific evaluation.
        for name,item in self.entries.items():
            path=Path(item["path"]);stat=path.stat()
            require(stat.st_size==item["bytes"] and stat.st_mtime_ns==item["mtime_ns"],"Input metadata unchanged during reporting: "+name)
            if str(path) in self.cache or path.suffix in (".jsonl",".py",".md"):
                require(sha256(path)==item["sha256"],"Read structured input hash unchanged: "+name)


def complete_receipt(inputs,directory):
    obj=inputs.read(directory/"EXECUTION121.json")
    require(obj.get("status")=="executed" and obj.get("exit_code")==0,"Actual completed execution receipt: "+str(directory))
    require(obj["source"]["source_commit"]==inputs.args.source_commit,"Execution generating source F")
    return obj


def arg_value(command,name):
    return command[command.index(name)+1] if name in command else None


def launch_ledger(inputs,ledger_root,required_outputs):
    rows=[];selected={}
    for path in sorted(Path(ledger_root).rglob("LAUNCH121.json")):
        obj=inputs.read(path);command=obj.get("command",[])
        if any(Path(str(v)).name in ("report121.py","study_integrity121.py") for v in command):
            continue
        require(obj.get("exit_code") is not None and exact(obj["elapsed_seconds"])>=0,"Recorded completed process attempt")
        log=path.parent/"stdout.log";info=inputs.track(log)
        require(info["sha256"]==obj["stdout_sha256"] and info["bytes"]==obj["stdout_bytes"],"Launch stdout hash and byte receipt")
        row=dict(path=inputs.name(path),status=obj["status"],exit_code=obj["exit_code"],
                 command=command,started_utc=obj["started_utc"],ended_utc=obj["ended_utc"],
                 elapsed_seconds=exact(obj["elapsed_seconds"]),stdout_sha256=obj["stdout_sha256"],
                 child_peak_rss_kib=obj.get("child_peak_rss_kib"),
                 python=obj.get("python"),platform=obj.get("platform"),thread_environment=obj.get("thread_environment"),
                 source_commit=arg_value(command,"--source-commit"),
                 nested_timing_children_are_inside_primary_clock="primary" in command and
                    any(Path(str(v)).name=="campaign121.py" for v in command))
        rows.append(row)
        supplied=arg_value(command,"--output")
        if supplied is None:continue
        for role,directory in required_outputs.items():
            expected=tuple(directory.relative_to(inputs.evidence).parts)
            parts=Path(supplied).parts
            if len(parts)>=len(expected) and tuple(parts[-len(expected):])==expected:
                require(role not in selected,"One actual launcher receipt for each selected completed attempt")
                require(obj["exit_code"]==0 and obj["status"]=="executed","Selected attempt actually succeeded")
                require(arg_value(command,"--source-commit")==inputs.args.source_commit,"Selected launcher F")
                selected[role]=row
    require(set(selected)==set(required_outputs),"All required actual acquisition/audit/primary/independent/statistical launch receipts")
    return rows,selected


def raw_key(state_hex,action_hex,alpha):
    return hashlib.sha256(json.dumps((tuple(state_hex),action_hex,float(alpha).hex()),separators=(",",":")).encode()).hexdigest()


@lru_cache(maxsize=None)
def binomial_tail_leq(probability,successes,delta):
    """Certify an already saved CP bracket; no inversion or new statistic choice."""
    c,d=probability.numerator,probability.denominator
    total=sum(math.comb(64,j)*c**j*(d-c)**(64-j) for j in range(successes,65))
    return total*delta.denominator<=delta.numerator*d**64


def check_saved_cp(record,successes,delta):
    require(record["successes"]==successes and 0<=successes<=64,"Exact original certified-event count")
    lo,hi=exact(record["lower"]),exact(record["inversion_upper"])
    if successes==0:
        require(lo==hi==0 and record["bisections"]==0,"Zero-event CP endpoint is exactly zero")
    else:
        require(record["bisections"]==48 and 0<=lo<hi<=1 and hi-lo==F(1,2**48),"Saved fixed48-step CP bracket")
        require(binomial_tail_leq(lo,successes,delta) and not binomial_tail_leq(hi,successes,delta),
                "Both saved binomial bracket inequalities hold in exact arithmetic")
    COUNTS["saved_cp_endpoints_checked"]+=1
    return lo,hi


def check_saved_mean(record,pairs,low,high,radius):
    require(len(pairs)==64 and all(low<=a<=b<=high for a,b in pairs),"All64 interval observations have the frozen support")
    ml=mean([a for a,_ in pairs]);mh=mean([b for _,b in pairs])
    wanted=dict(sample_mean_lower=ml,sample_mean_upper=mh,
                population_mean_lower=max(low,ml-radius),population_mean_upper=min(high,mh+radius))
    require(all(exact(record[name])==value for name,value in wanted.items()),"Every saved sample and population mean endpoint uses the frozen radius")
    COUNTS["saved_mean_intervals_checked"]+=1
    return wanted


def check_saved_family(receipt):
    cert=receipt["radius_certificate"]
    exponent=F(1225,128);ref_exponent=F(49,8)
    exp_lower=sum((exponent**j/F(math.factorial(j)) for j in range(21)),F(0))
    ref_lower=sum((ref_exponent**j/F(math.factorial(j)) for j in range(21)),F(0))
    expected=dict(regret_radius=35*TAU/128,signed_gain_radius=35*TAU/64,optimum_radius=7*K/32,
        contrast_exponent=exponent,contrast_exponential_lower=exp_lower,optimum_exponent=ref_exponent,
        optimum_exponential_lower=ref_lower,total_failure_at_most=F(1,20))
    require(all(exact(cert[k])==v for k,v in expected.items()),"Frozen exact simultaneous-family radius certificate")
    require(cert["independent_units"]==64 and cert["taylor_degree"]==20 and exp_lower>11600 and ref_lower>400,"Saved Taylor lower bounds and observation census")
    require(list(map(exact,cert["regret_range"]))==[F(0),TAU] and list(map(exact,cert["signed_gain_range"]))==[-TAU,TAU]
            and list(map(exact,cert["original_optimum_range"]))==[F(0),K],"Correct original supports in saved population family")
    require(2*F(1,200)+58*F(1,5800)+28*F(1,2800)+112*F(1,11200)+116*F(1,11600)==F(1,20),"Declared exact multiplicity sum")
    require(exact(receipt["simultaneous_coverage_at_least"])==F(19,20),"Correct coverage declaration after exact family checks")


def certify_records(inputs):
    args=inputs.args;source=inputs.source()
    paths={name:inputs.path(getattr(args,name)) for name in
           ("acquisition5","acquisition9","training_audit5","training_audit9","states","primary","independent","stats")}
    ledger_root=inputs.path(args.ledger_root)
    receipts={name:complete_receipt(inputs,path) for name,path in paths.items() if name!="states"}
    selected_outputs={name:path for name,path in paths.items() if name!="states"}
    ledger,launches=launch_ledger(inputs,ledger_root,selected_outputs)
    acquisition={};fit_audits={};models={};acquisition_manifests={}
    for budget in BUDGETS:
        directory=paths[f"acquisition{budget}"]
        manifest=inputs.artifact(directory,"ACQUISITION_MANIFEST121.json",args.actor_commit,"acquire",budget)
        acquisition_manifests[budget]=inputs.track(directory/"ACQUISITION_MANIFEST121.json")["sha256"]
        obj=inputs.read(directory/"ACQUISITION121.json");acquisition[budget]=obj
        require(obj["frozen_model_count"]==28 and obj["budget"]==budget,"Complete per-budget actor census")
        require(obj["original_Q_contexts"]==26*budget**2 and obj["main_marginal_contexts"]==10*budget**2,"Complete paid original label contexts")
        actual={item["path"] for item in manifest["files"] if Path(item["path"]).name=="model.json"}
        expected={f"models/{i}-{arm}-{loss}/model.json" for i in range(2) for arm in ARMS for loss in LOSSES}
        require(actual==expected,"Every declared acquired actor, no selected subset")
        audit_rows=inputs.rows(paths[f"training_audit{budget}"]/"models121.jsonl")
        require(len(audit_rows)==28,"Every per-budget independent finite-design fit audit")
        require(receipts[f"training_audit{budget}"]["audited_models"]==28,"Completed independent fit-audit receipt census")
        audit_map={group(row):row for row in audit_rows};require(len(audit_map)==28,"Unique model audits")
        for index in range(2):
            labels=inputs.read(directory/f"labels-{index}.json")
            require(labels["source_commit"]==args.source_commit and labels["index"]==index and exact(labels["alpha"])==RISKS[index],"Original label source/risk identity")
            require(len(labels["values"])==13*budget**2 and len(labels["marginals"])==5*budget**2,"All paid value and derivative label rows")
            require(labels["normalized_action_probes"]==sorted(set(v for knot in (0.,.25,.5,.75,1.) for v in (knot-2**-12,knot,knot+2**-12) if 0<=v<=1)),"Unchanged probe design")
            for arm in ARMS:
                for loss in LOSSES:
                    key=(index,budget,arm,loss);folder=directory/"models"/f"{index}-{arm}-{loss}"
                    model=inputs.read(folder/"model.json");fit=inputs.read(folder/"fit.json");cost=inputs.read(folder/"acquisition.json")
                    require(model["index"]==index and model["basis"]["budget"]==budget and model["basis"]["arm"]==arm and model["loss"]==loss,"Exact canonical acquired model identity")
                    require(model["source_commit"]==args.source_commit and model["label_sha256"]==inputs.track(directory/f"labels-{index}.json")["sha256"],"Model and same paid labels bound to F")
                    theta=list(map(exact,model["theta"]));require(len(theta)==model["basis"]["feature_count"],"Readout dimension")
                    require(theta==[F(n,2**30) for n in model["theta_numerators"]] and model["theta_denominator"]==2**30,"Actual dyadic readout")
                    require(model["theta_hex"]==[float(v).hex() for v in theta],"Stored readout hex")
                    require(all(exact(lo)<=v<=exact(hi) for lo,v,hi in zip(model["basis"]["coefficient_lower"],theta,model["basis"]["coefficient_upper"])),"Declared coefficient box")
                    require(fit["raw_solver"]["success"] is True,"Actually successful stored fitting attempt")
                    aud=audit_map[key]
                    inputs.track(paths[f"training_audit{budget}"]/f"{index}-{arm}-{loss}-witnesses.jsonl")
                    for field,p in (("model_sha256",folder/"model.json"),("fit_sha256",folder/"fit.json"),("design_sha256",folder/"design.json.gz"),("labels_sha256",directory/f"labels-{index}.json")):
                        require(aud[field]==inputs.track(p)["sha256"],"Independent fit audit input bytes")
                    require(exact(aud["value_optimum_lower"])<=exact(aud["value_sum_of_squares"]),"Exact value-fit weak duality")
                    if loss=="marginal":require(exact(aud["marginal_optimum_lower"])<=exact(aud["marginal_primal_upper"]),"Exact marginal weak duality")
                    models[key]=dict(model=model,fit=fit,acquisition=cost,model_sha256=inputs.track(folder/"model.json")["sha256"],model_bytes=inputs.track(folder/"model.json")["bytes"])
                    fit_audits[key]=aud
        for index in range(2):
            for loss in LOSSES:
                relu=models[index,budget,"relu",loss]["model"];hinge=models[index,budget,"hinge",loss]["model"]
                require(relu["theta"]==hinge["theta"] and relu["basis"]["units"]==hinge["basis"]["units"],"Equal-feature ReLU/hinge actors")
                COUNTS["exact_relu_hinge_model_pairs"]+=1
    inputs.artifact(paths["states"],"STATE_MANIFEST121.json",args.state_commit,"sample")
    states=inputs.read(paths["states"]/"states121.json");entropy_path=paths["states"]/"entropy121.bin";entropy=entropy_path.read_bytes();inputs.track(entropy_path)
    require(len(entropy)==640 and hashlib.sha256(entropy).hexdigest()==states["entropy_sha256"],"Actual fixed 640 entropy bytes")
    require(states["source_commit"]==args.source_commit and states["actor_commit"]==args.actor_commit and len(states["states"])==64,"F/M before all64 states")
    for budget in BUDGETS:require(states["actors"][str(budget)]["manifest_sha256"]==acquisition_manifests[budget],"Draw follows both exact model artifacts")
    state_map={}
    for row,item in enumerate(states["states"]):
        integers=[int.from_bytes(entropy[(row*2+j)*5:(row*2+j+1)*5],"big") for j in range(2)]
        x=[F(v,2**40) for v in integers]
        require(item["row"]==row and item["coordinate_numerators"]==integers and list(map(exact,item["state"]))==x and item["state_hex"]==[float(v).hex() for v in x],"Every exact independent state row retained")
        state_map[row]=item
    primary=inputs.rows(paths["primary"]/"records121.jsonl");pmap={identity(row):row for row in primary}
    expected={(i,row,b,arm,loss) for i,b,arm,loss in GROUPS for row in range(64)}
    require(len(primary)==len(pmap)==3712 and set(pmap)==expected,"All3712 unique declared primary decisions")
    for ident,row in pmap.items():
        index,j,b,arm,loss=ident;x=list(map(exact,row["state"]));cap=F(1,8)+sum(x)/16;a=exact(row["action"])
        require(row["state_hex"]==state_map[j]["state_hex"] and row["state"]==state_map[j]["state"],"Common exact state catalogue")
        require(exact(row["alpha"])==RISKS[index] and 0<=a<=cap and row["action_hex"]==float(a).hex(),"Original risk and feasible binary action")
        require(row["qualified"] is True and row["population_observation"] is True and row["repeat"] is None and row["original_initial_state_batch_size"]==1,"All fixed singleton primary qualifications")
        require(row["source_commit"]==args.source_commit and row["actor_commit"]==args.actor_commit and row["state_commit"]==args.state_commit,"Every primary F/M/D identity")
        lo,hi,opt=map(exact,(row["complete_policy_lower"],row["complete_policy_upper"],row["original_optimum_lower"]))
        require(lo<=hi and 0<=hi-opt<=TAU and hi-lo<=WIDTH,"Unchanged original complete-service targets")
        require(exact(row["certified_regret_upper"])>=hi-opt and exact(row["certified_regret_upper"])<=TAU,"Explicit numeric regret certificate, separate loss identity")
        require(exact(row["seconds"])>=0 and row["first_rejected"] in (True,False),"Measured service and refusal record")
        proposal=row["first_proposal_action"]
        if proposal is None:require(row["proposal_numerical_failure"] is True and row["numerical_failure"] is not None,"No invented raw proposal after failure")
        else:require(0<=exact(proposal)<=cap and row["first_proposal_action_hex"]==float(proposal).hex(),"Every actual raw feasible proposal")
        if arm!="online":require(row["model_sha256"]==models[index,b,arm,loss]["model_sha256"],"Primary actual frozen actor bytes")
    independent=inputs.rows(paths["independent"]/"comparisons121.jsonl");imap={identity(r):r for r in independent}
    independent_input=inputs.read(paths["independent"]/"PRIMARY_INPUT121.json")
    primary_info=inputs.track(paths["primary"]/"records121.jsonl")
    require(independent_input["sha256"]==primary_info["sha256"] and independent_input["bytes"]==primary_info["bytes"],"Independent evaluator's actual primary input bytes")
    inputs.track(paths["independent"]/"terminal_witnesses121.jsonl.gz")
    policy_rows=inputs.rows(paths["independent"]/"policies121.jsonl");policies={row["key_id"]:row for row in policy_rows}
    require(len(independent)==len(imap)==3712 and set(imap)==expected,"All independent final/proposal comparisons")
    require(len(policy_rows)==len(policies)==receipts["independent"]["unique_policy_and_proposal_keys"],"Every unique independent policy key")
    require(receipts["independent"]["counts"]["terminal_contexts"]==129*len(policies),"Complete declared independent terminal node census")
    used=set();optima={}
    for row in policy_rows:
        kid=raw_key(row["state_hex"],row["action_hex"],row["alpha"]);require(kid==row["key_id"],"Independent exact action key hash")
        require(row["bins"]==64 and row["terminal_steps"]==32 and row["terminal_contexts"]==129,"Unchanged independent policy resolution")
        require(exact(row["q_lower"])==exact(row["j_lower"]) and exact(row["j_upper"])-exact(row["q_upper"])==F(15,16*2**20),"Single implemented-future allowance")
        sk=(tuple(row["state_hex"]),float(row["alpha"]).hex());low=exact(row["optimum_lower"]);high=exact(row["q_upper"])
        if sk in optima:low=max(low,optima[sk][0]);high=min(high,optima[sk][1])
        require(low<=high,"Independent original optimum interval")
        optima[sk]=(low,high)
    for ident,r in imap.items():
        p=pmap[ident];kid=raw_key(p["state_hex"],p["action_hex"],p["alpha"])
        require(r["key_id"]==kid and kid in policies,"Independent final action exactly matches primary")
        used.add(kid);rec=policies[kid]
        for name in ("j_lower","j_upper"):require(exact(r[name])==exact(rec[name]),"Independent final value record")
        low,high=optima[(tuple(p["state_hex"]),float(p["alpha"]).hex())]
        require(exact(r["original_optimum_lower"])==low and exact(r["original_optimum_upper"])==high,"Same-state independent optimum support aggregation")
        require(exact(r["original_regret_lower"])==max(F(0),exact(rec["j_lower"])-high) and exact(r["original_regret_upper"])==exact(rec["j_upper"])-low,"Independent original regret arithmetic")
        require(max(exact(p["complete_policy_lower"]),exact(r["j_lower"]))<=min(exact(p["complete_policy_upper"]),exact(r["j_upper"])),"Production/independent overlap is compatibility only")
        if p["first_proposal_action"] is None:require(r["proposal_key_id"] is None and r["proposal_regret_lower"] is None,"Unavailable raw proposal remains unavailable")
        else:
            pk=raw_key(p["state_hex"],p["first_proposal_action_hex"],p["alpha"]);used.add(pk)
            require(r["proposal_key_id"]==pk and pk in policies,"Every raw proposal including rejects independently evaluated")
            for name in ("j_lower","j_upper"):require(exact(r["proposal_"+name])==exact(policies[pk][name]),"Raw proposal original objective")
        if ident[4]=="marginal":
            vk=(ident[0],ident[1],ident[2],ident[3],"value");v=imap[vk]
            gl,gu=(F(0),F(0)) if v["key_id"]==r["key_id"] else (max(-TAU,exact(v["j_lower"])-exact(r["j_upper"])),min(TAU,exact(v["j_upper"])-exact(r["j_lower"])))
            require((gl,gu)==(exact(r["marginal_gain_lower"]),exact(r["marginal_gain_upper"])),"Signed paired gain, no nonnegative clipping")
    require(used==set(policies),"No missing or silently substituted unique validation key")
    batches={};timing_checks=[];timing_rows={};timing_process={}
    for scenario in SCENARIOS:
        repeat=None if scenario=="primary64" else int(scenario[-1]);directory=paths["primary"] if repeat is None else paths["primary"]/"timing"/f"attempt-{repeat:02d}"
        catalogue=inputs.read(directory/"CATALOGUE121.json");n=64 if repeat is None else 32
        require(catalogue["decisions"]==58*n and len(catalogue["records"])==58,"Every policy in each actual clock")
        bmap={}
        for key in GROUPS:
            i,b,arm,loss=key;name=f"{i}-{b}-{arm}-{loss}";batch=inputs.read(directory/"batches"/f"{name}.json")
            require(group(batch)==key and len(batch["rows"])==n,"Complete cohort payload")
            require(exact(batch["cohort_end_to_end_seconds"])>=exact(batch["cold_model_load_seconds"])>=0,"Complete/load cost ordering")
            require(exact(batch["singleton_service_seconds"])>=0 and exact(batch["cohort_end_to_end_seconds"])+F(1,10**6)>=exact(batch["singleton_service_seconds"]),"Service time inside complete cohort")
            require(batch["event_trace_sha256"]==inputs.track(directory/"events"/f"{name}.jsonl.gz")["sha256"],"Actual full scientific event trace")
            bmap[key]=batch
        batches[scenario]=bmap
        if repeat is not None:
            complete_receipt(inputs,directory)
            saved=inputs.rows(directory/"records121.jsonl");mapping={identity(r):r for r in saved}
            expected32={ident for ident in expected if ident[1]<32}
            require(len(saved)==len(mapping)==1856 and set(mapping)==expected32,"Every1856 actual timing decision")
            for ident,r in mapping.items():
                p=pmap[ident]
                for name in ("state_hex","action_hex","first_proposal_action_hex","qualified","first_rejected"):
                    require(r[name]==p[name],"Timing/primary action and failure identity")
                timing_checks.append(dict(repeat=repeat,**ident_row(ident),final_action_equal=True,
                                         first_proposal_equal=True,state_equal=True,qualification_equal=True))
            timing_rows[scenario]=mapping
            launcher=inputs.read(paths["primary"]/"timing"/f"launcher-{repeat:02d}.json")
            require(launcher["exit_code"]==0 and launcher["repeat"]==repeat,"Actually successful distinct timing subprocess")
            log=paths["primary"]/"timing"/f"launcher-{repeat:02d}.log"
            require(inputs.track(log)["sha256"]==launcher["log_sha256"],"Timing launcher stdout bound")
            timing_process[scenario]=launcher
    require(len(timing_checks)==9280,"All9280 timing action identities")
    timing_summary=inputs.read(paths["primary"]/"TIMING121.json")
    require(timing_summary["full_saved_record_action_identity_checks"]==9280 and len(timing_summary["repeats"])==5,"Native complete five-clock record check")
    statgroups=inputs.rows(paths["stats"]/"POLICY_GROUPS121.jsonl");statcontrasts=inputs.rows(paths["stats"]/"LOSS_CONTRASTS121.jsonl");statopt=inputs.rows(paths["stats"]/"ORIGINAL_OPTIMUM121.jsonl")
    require(len(statgroups)==58 and len(statcontrasts)==28 and len(statopt)==2,"Fixed joint inference census")
    expected_contrasts={(i,b,a) for i in range(2) for b in BUDGETS for a in ARMS}
    contrast_keys=[(r["index"],r["budget"],r["arm"]) for r in statcontrasts]
    require(len(set(contrast_keys))==28 and set(contrast_keys)==expected_contrasts,"Exact unique28 signed learning-treatment keys")
    optimum_keys=[r["index"] for r in statopt]
    require(len(set(optimum_keys))==2 and set(optimum_keys)=={0,1},"Exactly both original optimal-value risk groups")
    statistical_inputs=inputs.read(paths["stats"]/"INPUTS121.json")
    require(receipts["stats"]["inputs"]==statistical_inputs and set(statistical_inputs)=={"primary","independent"},"Saved statistical execution and input manifest agree")
    require(statistical_inputs["primary"]["sha256"]==primary_info["sha256"] and
            statistical_inputs["independent"]["sha256"]==inputs.track(paths["independent"]/"comparisons121.jsonl")["sha256"],
            "Statistics used these exact selected primary and independent-comparison bytes")
    check_saved_family(receipts["stats"])
    statoptmap={r["index"]:r for r in statopt}
    for index,row in statoptmap.items():
        require(row["independent_units"]==64,"All64 optimum observations")
        pairs=[(max(F(0),exact(imap[(index,j,0,"online","online")]["original_optimum_lower"])),
                min(K,exact(imap[(index,j,0,"online","online")]["original_optimum_upper"]))) for j in range(64)]
        check_saved_mean(row,pairs,F(0),K,7*K/32)
    statmap={group(r):r for r in statgroups};require(set(statmap)==set(GROUPS),"Every fixed inference policy cell")
    for key,row in statmap.items():
        data=[imap[(key[0],j,*key[1:])] for j in range(64)];raw=[pmap[(key[0],j,*key[1:])] for j in range(64)]
        require(row["independent_units"]==64,"All64 policy observations")
        require(exact(row["sample_original_objective_lower"])==mean([r["j_lower"] for r in data]) and exact(row["sample_original_objective_upper"])==mean([r["j_upper"] for r in data]),"Statistical sample original objective reaggregation")
        reg=check_saved_mean(row["regret"],[(max(F(0),exact(r["original_regret_lower"])),min(TAU,exact(r["original_regret_upper"]))) for r in data],F(0),TAU,35*TAU/128)
        optimum=statoptmap[key[0]]
        require(exact(row["population_original_objective_lower"])==max(F(0),exact(optimum["population_mean_lower"])+reg["population_mean_lower"]) and
                exact(row["population_original_objective_upper"])==min(K+TAU,exact(optimum["population_mean_upper"])+reg["population_mean_upper"]),"Saved original-policy population endpoints use the joint optimum and regret bounds")
        rejected=sum(r["first_rejected"] for r in raw)
        require(row["first_rejections"]==rejected,"All actual rejection counts")
        cl,_=check_saved_cp(row["rejection_lower_inversion"],rejected,F(1,11600))
        cu,_=check_saved_cp(row["rejection_complement_lower_inversion"],64-rejected,F(1,11600))
        require(exact(row["rejection_probability_lower"])==cl and exact(row["rejection_probability_upper"])==1-cu,"Both actual saved first-rejection probability endpoints")
    for row in statcontrasts:
        key=(row["index"],row["budget"],row["arm"],"marginal");data=[imap[(key[0],j,*key[1:])] for j in range(64)]
        require(row["independent_units"]==64,"All64 signed treatment observations")
        check_saved_mean(row["gain"],[(exact(r["marginal_gain_lower"]),exact(r["marginal_gain_upper"])) for r in data],-TAU,TAU,35*TAU/64)
        require(len(row["threshold_events"])==4,"Both prescribed positive/negative thresholds")
        event_keys=[(exact(e["threshold"]),e["direction"]) for e in row["threshold_events"]]
        expected_events={(t,d) for t in (F(1,2**20),F(1,2**16)) for d in ("benefit","harm")}
        require(len(set(event_keys))==4 and set(event_keys)==expected_events,"Unique complete four signed threshold events per treatment")
        for event in row["threshold_events"]:
            threshold=exact(event["threshold"]);require(threshold in (F(1,2**20),F(1,2**16)),"Frozen gain threshold")
            k=sum(exact(r["marginal_gain_lower"])>=threshold for r in data) if event["direction"]=="benefit" else sum(exact(r["marginal_gain_upper"])<=-threshold for r in data)
            require(event["successes"]==k,"Certified signed threshold events only")
            check_saved_cp(event,k,F(1,11200))
    require(COUNTS["saved_cp_endpoints_checked"]==228 and COUNTS["saved_mean_intervals_checked"]==88,"All112 event and116 rejection endpoints, plus2+58+28 mean intervals, actually checked")
    attempts=inputs.rows(paths["primary"]/"attempts121.jsonl");actor_rows=inputs.rows(paths["primary"]/"actors121.jsonl")
    require(len(actor_rows)==3712 and len({identity(r) for r in actor_rows})==3712,"All actor-root traces including unavailable proposals")
    acount=Counter(identity(row) for row in attempts)
    for ident,row in pmap.items():require(acount[ident]==row["qualification_attempts"],"No missing rejected or fallback attempt")
    for key in GROUPS:
        flat=[r for r in attempts if group(r)==key]
        require(flat==batches["primary64"][key]["attempts"],"Every actual primary attempt equals the batch payload")
    feature_controls=[]
    for key in GROUPS:
        if key[2]!="relu":continue
        for j in range(64):
            p=pmap[(key[0],j,*key[1:])];h=pmap[(key[0],j,key[1],"hinge",key[3])]
            equal=p["action_hex"]==h["action_hex"] and p["first_proposal_action_hex"]==h["first_proposal_action_hex"]
            feature_controls.append(dict(**ident_row((key[0],j,*key[1:])),scenario="primary64",
                relu_action_hex=p["action_hex"],hinge_action_hex=h["action_hex"],
                final_action_equal=p["action_hex"]==h["action_hex"],
                raw_proposal_equal=p["first_proposal_action_hex"]==h["first_proposal_action_hex"],
                exact_readout_and_feature_control=True,independent_training_replicate=False))
            COUNTS["relu_hinge_primary_action_pairs"]+=1
            COUNTS["relu_hinge_primary_equal_action_pairs"]+=int(equal)
        for scenario in SCENARIOS[1:]:
            for j in range(32):
                p=timing_rows[scenario][(key[0],j,*key[1:])];h=timing_rows[scenario][(key[0],j,key[1],"hinge",key[3])]
                feature_controls.append(dict(**ident_row((key[0],j,*key[1:])),scenario=scenario,
                    relu_action_hex=p["action_hex"],hinge_action_hex=h["action_hex"],
                    final_action_equal=p["action_hex"]==h["action_hex"],
                    raw_proposal_equal=p["first_proposal_action_hex"]==h["first_proposal_action_hex"],
                    exact_readout_and_feature_control=True,independent_training_replicate=False))
    return dict(source=source,paths=paths,receipts=receipts,launches=launches,ledger=ledger,
        acquisition=acquisition,fit_audits=fit_audits,models=models,states=state_map,
        primary=primary,pmap=pmap,independent=independent,imap=imap,policies=policies,optima=optima,
        batches=batches,timing_checks=timing_checks,timing_rows=timing_rows,timing_process=timing_process,
        statgroups=statgroups,statmap=statmap,statcontrasts=statcontrasts,statopt=statopt,
        attempts=attempts,actor_rows=actor_rows,feature_controls=feature_controls)


def acquisition_costs(data):
    result={};budget_rows=[];model_rows=[]
    for budget in BUDGETS:
        acq=data["acquisition"][budget]
        phases=sum((exact(r["seconds"]) for r in acq["phase_intervals"]),F(0))
        outer=exact(data["launches"][f"acquisition{budget}"]["elapsed_seconds"])
        residual=outer-phases
        require(residual>=0,"Actual acquisition outer clock encloses all nonoverlapping phases")
        audit_outer=exact(data["launches"][f"training_audit{budget}"]["elapsed_seconds"])
        audit_phases=sum((exact(r["seconds"]) for key,r in data["fit_audits"].items() if key[1]==budget),F(0))
        audit_residual=audit_outer-audit_phases
        require(audit_residual>=0,"Actual training-audit outer clock encloses all model audit phases")
        label_counters=Counter()
        for record in acq["records"]:
            label_counters.update(record["labels"]["counts"])
        budget_rows.append(dict(budget=budget,actual_acquisition_process_seconds=outer,
            nonoverlapping_acquisition_phase_seconds=phases,common_acquisition_process_residual_seconds=residual,
            actual_training_audit_process_seconds=audit_outer,model_training_audit_seconds=audit_phases,
            common_training_audit_residual_seconds=audit_residual,
            original_root_Q_contexts=acq["original_Q_contexts"],main_marginal_contexts=acq["main_marginal_contexts"],
            actual_label_operation_counts=dict(label_counters),
            actual_training_audit_counts=data["receipts"][f"training_audit{budget}"]["counts"],
            designed_label_risk_node_contexts=26*budget**2*(2*256+1),
            designed_risk_nodes_are_not_total_primitive_work=True,
            source_gate_seconds=exact(acq["source_gate_seconds"]),scientific_import_seconds=exact(acq["scientific_import_seconds"]),
            max_acquisition_rss_kib=data["receipts"][f"acquisition{budget}"].get("max_rss_kib"),
            max_training_audit_rss_kib=data["receipts"][f"training_audit{budget}"].get("max_rss_kib"),
            independent_actual_budget_process=True,no_fine_to_coarse_retiming_allocation=True))
        for index in range(2):
            record=acq["records"][index];labels=exact(record["labels"]["seconds"])
            for arm in ARMS:
                for loss in LOSSES:
                    key=(index,budget,arm,loss);phase=record["models"][f"{arm}-{loss}"]
                    own=exact(phase["own_model_phase_seconds"])
                    parent=exact(phase["parent_relu_model_phase_charge_seconds"])
                    own_audit=exact(data["fit_audits"][key]["seconds"])
                    parent_audit=exact(data["fit_audits"][index,budget,"relu",loss]["seconds"]) if arm=="hinge" else F(0)
                    require(exact(phase["standalone_measured_component_subtotal_seconds"])==exact(float(labels)+float(own)+float(parent)),
                            "Saved floating component subtotal has its actual declared phase sum")
                    total=labels+own+parent+residual+own_audit+parent_audit+audit_residual
                    model=data["models"][key];fit=data["fit_audits"][key]
                    row=dict(**group_row(key),label_phase_seconds=labels,own_model_phase_seconds=own,
                        parent_relu_model_phase_seconds=parent,common_acquisition_residual_seconds=residual,
                        own_required_training_audit_seconds=own_audit,parent_relu_training_audit_seconds=parent_audit,
                        common_training_audit_residual_seconds=audit_residual,
                        complete_allocated_acquisition_seconds=total,
                        actual_fit_design_seconds=exact(model["acquisition"]["fit_design_seconds"]),
                        actual_solver_seconds=exact(model["acquisition"]["solver_seconds"]),
                        model_write_seconds=exact(model["acquisition"]["model_write_seconds"]),
                        design_write_seconds=exact(model["acquisition"]["design_write_seconds"]),
                        fit_write_seconds=exact(model["acquisition"]["fit_write_seconds"]),
                        model_bytes=model["model_bytes"],feature_count=model["model"]["basis"]["feature_count"],
                        nonzero_stored_coefficients=sum(exact(v)!=0 for v in model["model"]["theta"]),
                        coefficient_bits=30,coefficient_box=128,
                        original_root_Q_contexts_if_standalone=13*budget**2,
                        terminal_label_rows_if_standalone=13*budget**2*(2*256+1),
                        terminal_label_rows_scope="Requested midpoint/endpoint risk contexts; actual internal compiler, certificate and fallback work is in label_operation_counts_if_standalone.",
                        label_operation_counts_if_standalone=model["acquisition"]["original_label_counts_if_standalone"],
                        measured_component_allocation_not_separately_observed_standalone_process=True,
                        independent_policy_validation_in_research_ledger_not_deployment_cost=True,
                        finite_node_marginal_residual=exact(fit["marginal_primal_upper"]),
                        marginal_optimum_lower=None if loss!="marginal" else exact(fit["marginal_optimum_lower"]),
                        marginal_fit_gap_upper=None if loss!="marginal" else exact(fit["marginal_optimality_gap_upper"]),
                        value_mean_squared_residual=exact(fit["value_mean_of_squares"]),
                        value_sum_squared_residual=exact(fit["value_sum_of_squares"]),
                        value_optimum_lower=exact(fit["value_optimum_lower"]),
                        value_fit_gap_upper=exact(fit["value_optimality_gap_upper"]),
                        derivative_assembly_max_exact_error=exact(fit["derivative_assembly_max_exact_error"]),
                        value_assembly_max_exact_error=exact(fit["value_assembly_max_exact_error"]),
                        finite_node_only=True,global_feature_cover_numerically_certified=False,
                        model_sha256=model["model_sha256"])
                    result[key]=row;model_rows.append(row)
    for index in range(2):
        result[index,0,"online","online"]=dict(**group_row((index,0,"online","online")),
            complete_allocated_acquisition_seconds=F(0),model_bytes=0,feature_count=0,
            original_root_Q_contexts_if_standalone=0,terminal_label_rows_if_standalone=0,
            no_fitted_artifact=True,online_source_and_primitive_costs_in_service_and_common_process=True)
    return result,budget_rows,model_rows


def service_costs(data,acquisition):
    process_rows=[];result={};clock_rows=[]
    child=sum((exact(r["elapsed_seconds"]) for r in data["timing_process"].values()),F(0))
    primary_parent=exact(data["launches"]["primary"]["elapsed_seconds"])
    for scenario in SCENARIOS:
        n=64 if scenario=="primary64" else 32
        elapsed=primary_parent-child if scenario=="primary64" else exact(data["timing_process"][scenario]["elapsed_seconds"])
        phases=sum((exact(b["cohort_end_to_end_seconds"]) for b in data["batches"][scenario].values()),F(0))
        common=elapsed-phases
        require(common>=0,"Actual process residual after all nonoverlapping cohort clocks")
        process_rows.append(dict(scenario=scenario,matching_initial_state_rows=n,
            actual_process_seconds_excluding_nested_timing_children=elapsed,
            actual_cohort_seconds=phases,common_source_import_verification_and_process_residual_seconds=common,
            primary_timing_children_subtracted_once=child if scenario=="primary64" else F(0),
            primary_parent_outer_clock=primary_parent if scenario=="primary64" else None,
            complete_common_residual_charged_to_each_declared_standalone_service=True,
            current_whole_menu_process_time_not_an_observed_single_model_process=True))
        for key in GROUPS:
            batch=data["batches"][scenario][key];T=exact(batch["cohort_end_to_end_seconds"]);L=exact(batch["cold_model_load_seconds"])
            A=acquisition[key]["complete_allocated_acquisition_seconds"]
            service=exact(batch["singleton_service_seconds"]);recording=exact(batch["decision_and_attempt_recording_seconds"])
            rows=batch["rows"]
            actual_map=data["pmap"] if scenario=="primary64" else data["timing_rows"][scenario]
            require(all(r==actual_map[identity(r)] for r in rows),"Batch actions/cost rows equal their actual flat records")
            countsum=Counter()
            for row in rows:countsum.update(row["counts"])
            require(dict(countsum)==batch["counts"],"Actual per-state operation counter sum")
            clock=dict(**group_row(key),scenario=scenario,matching_initial_state_rows=n,
                cohort_end_to_end_seconds=T,cold_model_and_cost_record_load_seconds=L,
                singleton_service_seconds=service,decision_actor_attempt_recording_seconds=recording,
                event_serialization_seconds=exact(batch["event_serialization_seconds"]),
                event_serialization_is_included_not_added_again=True,
                cohort_remaining_seconds=T-L-service-recording,
                allocated_common_process_residual_seconds=common,
                complete_allocated_acquisition_seconds=A,
                complete_cost_at_matching_observed_cohort_volume=A+common+T,
                model_bytes=batch["model_bytes"],counts=batch["counts"],
                first_rejections=sum(r["first_rejected"] for r in rows),
                numerical_service_failures=sum(r["numerical_service_failure"] for r in rows),
                unavailable_first_proposals=sum(r["first_proposal_action"] is None for r in rows),
                exact_fallbacks=sum(r["exact_fallback"] for r in rows),
                all_attempts=sum(r["qualification_attempts"] for r in rows),
                descriptive_clock_not_timing_confidence=True)
            result[scenario,key]=clock;clock_rows.append(clock)
    require(len(clock_rows)==348,"All58 primary plus290 repeated cohort clocks")
    return result,process_rows,clock_rows


def paired_gain(data,candidate,comparator,n):
    require(candidate[0]==comparator[0] and n in (32,64),"Matched same-risk, same-state economics")
    values=[];equal=0
    for j in range(n):
        a=data["imap"][(candidate[0],j,*candidate[1:])];b=data["imap"][(comparator[0],j,*comparator[1:])]
        if a["key_id"]==b["key_id"]:lo=hi=F(0);equal+=1
        else:lo=max(-TAU,exact(b["j_lower"])-exact(a["j_upper"]));hi=min(TAU,exact(b["j_upper"])-exact(a["j_lower"]))
        require(-TAU<=lo<=hi<=TAU,"Original signed pair support")
        values.append((lo,hi))
    return dict(lower=mean([v[0] for v in values]),upper=mean([v[1] for v in values]),
                identical_original_policy_keys=equal,states=n)


def economic_tables(data,acquisition,clocks):
    cells=[];states=[];pairs=[];contrasts=[];pair_cache={}
    for key in GROUPS:
        ind=[data["imap"][(key[0],j,*key[1:])] for j in range(64)]
        primary=[data["pmap"][(key[0],j,*key[1:])] for j in range(64)]
        stat=data["statmap"][key];missing=sum(r["proposal_key_id"] is None for r in ind)
        attempts=[r for r in data["attempts"] if group(r)==key]
        by_stage=Counter(r["stage"] for r in attempts);rejected_stages=Counter(r["stage"] for r in attempts if not r["qualified"])
        row=dict(**group_row(key),independent_initial_states=64,
            original_objective_mean_lower=mean([r["j_lower"] for r in ind]),original_objective_mean_upper=mean([r["j_upper"] for r in ind]),
            original_optimum_mean_lower=mean([r["original_optimum_lower"] for r in ind]),original_optimum_mean_upper=mean([r["original_optimum_upper"] for r in ind]),
            independently_reconstructed_regret_mean_lower=mean([r["original_regret_lower"] for r in ind]),
            independently_reconstructed_regret_mean_upper=mean([r["original_regret_upper"] for r in ind]),
            independent_regret_maximum_upper=max(exact(r["original_regret_upper"]) for r in ind),
            qualified_regret_sample_lower=exact(stat["regret"]["sample_mean_lower"]),qualified_regret_sample_upper=exact(stat["regret"]["sample_mean_upper"]),
            joint_population_regret_lower=exact(stat["regret"]["population_mean_lower"]),joint_population_regret_upper=exact(stat["regret"]["population_mean_upper"]),
            joint_population_original_objective_lower=exact(stat["population_original_objective_lower"]),
            joint_population_original_objective_upper=exact(stat["population_original_objective_upper"]),
            original_action_mean_squared_error_upper=mean([r["squared_original_action_error_upper"] for r in ind]),
            original_action_rms_error_upper=sqrt_upper(mean([r["squared_original_action_error_upper"] for r in ind])),
            raw_proposal_regret_mean_lower=None if missing else mean([r["proposal_regret_lower"] for r in ind]),
            raw_proposal_regret_mean_upper=None if missing else mean([r["proposal_regret_upper"] for r in ind]),
            raw_proposal_original_objective_mean_lower=None if missing else mean([r["proposal_j_lower"] for r in ind]),
            raw_proposal_original_objective_mean_upper=None if missing else mean([r["proposal_j_upper"] for r in ind]),
            raw_proposal_action_rms_error_upper=None if missing else sqrt_upper(mean([r["proposal_squared_original_action_error_upper"] for r in ind])),
            unavailable_raw_proposals=missing,first_rejections=sum(r["first_rejected"] for r in primary),
            first_rejection_probability_lower=exact(stat["rejection_probability_lower"]),first_rejection_probability_upper=exact(stat["rejection_probability_upper"]),
            final_actions_changed_from_available_first=sum(r["proposal_equals_final"] is False for r in ind),
            numerical_service_failures=sum(r["numerical_service_failure"] for r in primary),
            exact_fallbacks=sum(r["exact_fallback"] for r in primary),
            qualification_attempts=len(attempts),attempts_by_stage=dict(by_stage),unqualified_attempts_by_stage=dict(rejected_stages),
            all64_final_policies_qualified=True,original_action_errors_are_bounds_not_exact_errors=True,
            production_independent_interval_overlap_is_compatibility_only=True,
            complete_allocated_acquisition_seconds=acquisition[key]["complete_allocated_acquisition_seconds"],
            actual_primary64_cohort_seconds=clocks["primary64",key]["cohort_end_to_end_seconds"],
            full_primary64_allocated_cost=clocks["primary64",key]["complete_cost_at_matching_observed_cohort_volume"],
            primary_singleton_service_seconds=clocks["primary64",key]["singleton_service_seconds"],
            timing32_cohort_seconds_all_five=[clocks[s,key]["cohort_end_to_end_seconds"] for s in SCENARIOS[1:]],
            timing32_cohort_seconds_median=median([clocks[s,key]["cohort_end_to_end_seconds"] for s in SCENARIOS[1:]]),
            timing32_cohort_seconds_minimum=min(clocks[s,key]["cohort_end_to_end_seconds"] for s in SCENARIOS[1:]),
            timing32_cohort_seconds_maximum=max(clocks[s,key]["cohort_end_to_end_seconds"] for s in SCENARIOS[1:]),
            primary_operation_counts=clocks["primary64",key]["counts"],
            stored_model_bytes=data["batches"]["primary64"][key]["model_bytes"],
            feature_count=acquisition[key]["feature_count"])
        cells.append(row)
        for j,(p,indrow) in enumerate(zip(primary,ind)):
            states.append(dict(**ident_row((key[0],j,*key[1:])),state=p["state"],state_hex=p["state_hex"],
                action=p["action"],action_hex=p["action_hex"],first_proposal_action=p["first_proposal_action"],
                first_proposal_action_hex=p["first_proposal_action_hex"],
                first_rejected=p["first_rejected"],proposal_numerical_failure=p["proposal_numerical_failure"],
                numerical_service_failure=p["numerical_service_failure"],exact_fallback=p["exact_fallback"],
                complete_policy_lower=exact(p["complete_policy_lower"]),complete_policy_upper=exact(p["complete_policy_upper"]),
                certified_regret_upper=exact(p["certified_regret_upper"]),original_production_optimum_lower=exact(p["original_optimum_lower"]),
                independent=indrow,actual_singleton_seconds=exact(p["seconds"]),operation_counts=p["counts"],
                qualification_attempts=p["qualification_attempts"],qualified=p["qualified"]))
    for n in (64,32):
        for index in range(2):
            keys=[key for key in GROUPS if key[0]==index]
            for a,b in itertools.combinations(keys,2):
                gain=paired_gain(data,a,b,n);pair_cache[n,a,b]=gain
                pair_cache[n,b,a]=dict(gain,lower=-gain["upper"],upper=-gain["lower"])
                lo,hi=-gain["upper"],-gain["lower"]
                pairs.append(dict(index=index,states=n,a_budget=a[1],a_arm=a[2],a_loss=a[3],
                    b_budget=b[1],b_arm=b[2],b_loss=b[3],mean_original_a_minus_b_lower=lo,mean_original_a_minus_b_upper=hi,
                    sign=sign_interval(lo,hi),identical_original_policy_keys=gain["identical_original_policy_keys"],
                    sample_comparison_not_cross_representation_population_inference=True))
    for stat in data["statcontrasts"]:
        key=(stat["index"],stat["budget"],stat["arm"],"marginal");value=(*key[:3],"value")
        c64=pair_cache[64,key,value];c32=pair_cache[32,key,value]
        ratios=[clocks[s,key]["cohort_end_to_end_seconds"]/clocks[s,value]["cohort_end_to_end_seconds"] for s in SCENARIOS[1:]]
        full_ratios=[clocks[s,key]["complete_cost_at_matching_observed_cohort_volume"]/clocks[s,value]["complete_cost_at_matching_observed_cohort_volume"] for s in SCENARIOS[1:]]
        m=data["fit_audits"][key];v=data["fit_audits"][value]
        contrasts.append(dict(index=key[0],budget=key[1],arm=key[2],independent_states=64,
            sample64_gain_lower=c64["lower"],sample64_gain_upper=c64["upper"],sample64_sign=sign_interval(c64["lower"],c64["upper"]),
            sample32_gain_lower=c32["lower"],sample32_gain_upper=c32["upper"],
            identical_original_policy_keys=c64["identical_original_policy_keys"],
            population_gain_lower=exact(stat["gain"]["population_mean_lower"]),population_gain_upper=exact(stat["gain"]["population_mean_upper"]),
            population_gain_sign=sign_interval(exact(stat["gain"]["population_mean_lower"]),exact(stat["gain"]["population_mean_upper"])),
            threshold_events=stat["threshold_events"],first_rejection_change=stat["first_rejection_change"],
            node_marginal_residual_value=exact(v["marginal_primal_upper"]),node_marginal_residual_marginal=exact(m["marginal_primal_upper"]),
            node_marginal_residual_change=exact(m["marginal_primal_upper"])-exact(v["marginal_primal_upper"]),
            marginal_fit_optimality_gap_upper=exact(m["marginal_optimality_gap_upper"]),
            actual_primary64_cohort_cost_ratio=clocks["primary64",key]["cohort_end_to_end_seconds"]/clocks["primary64",value]["cohort_end_to_end_seconds"],
            actual_primary64_full_allocated_cost_ratio=clocks["primary64",key]["complete_cost_at_matching_observed_cohort_volume"]/clocks["primary64",value]["complete_cost_at_matching_observed_cohort_volume"],
            all_five_timing32_cohort_cost_ratios=ratios,median_timing32_cohort_ratio=median(ratios),
            minimum_timing32_cohort_ratio=min(ratios),maximum_timing32_cohort_ratio=max(ratios),
            all_five_timing32_full_allocated_cost_ratios=full_ratios,
            full_cost_faster_timing_clocks=sum(r<1 for r in full_ratios),full_cost_slower_timing_clocks=sum(r>1 for r in full_ratios),
            training_gain_is_signed_not_safe_improvement=True))
    require(len(cells)==58 and len(states)==3712 and len(pairs)==1624 and len(contrasts)==28,"All prespecified and full-menu descriptive economic tables")
    return cells,states,pairs,contrasts,pair_cache


def domain_empty():return dict(empty=True,lower=None,lower_closed=False,upper=None,upper_closed=False)
def domain_all():return dict(empty=False,lower=F(0),lower_closed=True,upper=None,upper_closed=False)


def positive_domain(gain,extra_seconds):
    """Exact strict gain-p*extra_seconds>0, p>=0; inherited algebra, no new choice."""
    gain,extra_seconds=exact(gain),exact(extra_seconds)
    if extra_seconds==0:return domain_all() if gain>0 else domain_empty()
    threshold=gain/extra_seconds
    if extra_seconds>0:
        return domain_empty() if threshold<=0 else dict(empty=False,lower=F(0),lower_closed=True,upper=threshold,upper_closed=False)
    return domain_all() if threshold<0 else dict(empty=False,lower=threshold,lower_closed=False,upper=None,upper_closed=False)


def intersect_domains(a,b):
    if a["empty"] or b["empty"]:return domain_empty()
    low=max(a["lower"],b["lower"])
    lc=(a["lower"]<low or a["lower_closed"]) and (b["lower"]<low or b["lower_closed"])
    finite=[x["upper"] for x in (a,b) if x["upper"] is not None];high=min(finite) if finite else None
    hc=high is not None and all(x["upper"] is None or x["upper"]>high or x["upper_closed"] for x in (a,b))
    if high is not None and (low>high or (low==high and not(lc and hc))):return domain_empty()
    return dict(empty=False,lower=low,lower_closed=lc,upper=high,upper_closed=hc)


def scenario_cost(clock,volume):
    n=clock["matching_initial_state_rows"]
    A=clock["complete_allocated_acquisition_seconds"];L=clock["cold_model_and_cost_record_load_seconds"]
    T=clock["cohort_end_to_end_seconds"];H=clock["allocated_common_process_residual_seconds"]
    return A+H+L+F(volume,n)*(T-L)


def menu_specifications():
    configurations=[]
    for key in GROUPS:
        full=[other for other in GROUPS if other[0]==key[0] and other[2]!="relu" and other!=key]
        configurations.append((key,"all-budgets-conventional",full))
        for budget in BUDGETS:
            if key[1] not in (0,budget):continue
            rivals=[other for other in full if other[1] in (0,budget)]
            configurations.append((key,f"within-budget-{budget}",rivals))
    require(len(configurations)==118,"All full and within-budget menus, with online retained")
    return configurations


def prices_and_frontiers(data,clocks,pair_cache):
    costs=[];costmap={};constraints=[];menus=[];robust=[];frontiers=[]
    for scenario in SCENARIOS:
        n=64 if scenario=="primary64" else 32
        for volume in VOLUMES:
            for key in GROUPS:
                cost=scenario_cost(clocks[scenario,key],volume);costmap[scenario,volume,key]=cost
                costs.append(dict(**group_row(key),scenario=scenario,volume=volume,economic_state_rows=n,
                    total_seconds_scenario=cost,seconds_per_decision_scenario=cost/volume,
                    acquisition_seconds=clocks[scenario,key]["complete_allocated_acquisition_seconds"],
                    one_load_seconds=clocks[scenario,key]["cold_model_and_cost_record_load_seconds"],
                    common_process_seconds=clocks[scenario,key]["allocated_common_process_residual_seconds"],
                    formula="A + H + L + (N/n)*(T-L)",
                    hypothetical_reuse_not_measured_throughput=volume!=n,
                    independent_original_policy_research_validation_is_separate=True))
            for key,menu,rivals in menu_specifications():
                sufficient,upper=domain_all(),domain_all();tight_low=[];tight_up=[]
                for other in rivals:
                    gain=pair_cache[n,key,other];dc=costmap[scenario,volume,key]-costmap[scenario,volume,other]
                    gl,gu=volume*gain["lower"],volume*gain["upper"]
                    low_domain=positive_domain(gl,dc);up_domain=positive_domain(gu,dc)
                    new_low=intersect_domains(sufficient,low_domain);new_up=intersect_domains(upper,up_domain)
                    if new_low!=sufficient:tight_low.append(label(other))
                    if new_up!=upper:tight_up.append(label(other))
                    sufficient,upper=new_low,new_up
                    constraints.append(dict(**group_row(key),menu=menu,scenario=scenario,volume=volume,economic_state_rows=n,
                        comparator_budget=other[1],comparator_arm=other[2],comparator_loss=other[3],
                        total_original_gain_lower=gl,total_original_gain_upper=gu,
                        total_extra_seconds=dc,sufficient_price_domain=low_domain,
                        upper_not_ruled_out_price_domain=up_domain,
                        strict_gain_minus_price_times_extra_cost=True,population_adoption_claim=False))
                menus.append(dict(**group_row(key),menu=menu,scenario=scenario,volume=volume,economic_state_rows=n,
                    comparator_count=len(rivals),comparators=[label(k) for k in rivals],
                    sufficient_price_domain=sufficient,upper_not_ruled_out_price_domain=upper,
                    constraints_tightening_sufficient=tight_low,constraints_tightening_upper=tight_up,
                    upper_intersection_is_only_pairwise_not_ruled_out=True,
                    all_matching_clock_actions_verified=True,population_or_calibrated_adoption_claim=False))
            for key in GROUPS:
                dominators=[];traditional=[];C=costmap[scenario,volume,key]
                for other in GROUPS:
                    if other[0]!=key[0] or other==key:continue
                    gain=pair_cache[n,other,key];O=costmap[scenario,volume,other]
                    if O<=C and gain["lower"]>=0 and (O<C or gain["lower"]>0):
                        dominators.append(label(other))
                        if other[2]!="relu":traditional.append(label(other))
                frontiers.append(dict(**group_row(key),scenario=scenario,volume=volume,economic_state_rows=n,
                    complete_cost=costmap[scenario,volume,key],certified_sample_dominators=dominators,
                    certified_conventional_sample_dominators=traditional,
                    not_certifiably_dominated=not dominators,
                    unresolved_intervals_do_not_prove_true_frontier_membership=True,
                    same_risk_and_exact_matching_state_cohort=True))
    menu_index={(group(r),r["menu"],r["scenario"],r["volume"]):r for r in menus}
    for key,menu,rivals in menu_specifications():
        for volume in VOLUMES:
            low,upper=domain_all(),domain_all()
            for scenario in SCENARIOS[1:]:
                row=menu_index[key,menu,scenario,volume]
                low=intersect_domains(low,row["sufficient_price_domain"])
                upper=intersect_domains(upper,row["upper_not_ruled_out_price_domain"])
            robust.append(dict(**group_row(key),menu=menu,scenario="intersection-all-five-timing32",volume=volume,
                economic_state_rows=32,sufficient_price_domain=low,upper_not_ruled_out_price_domain=upper,
                comparator_count_per_clock=len(rivals),clock_count=5,
                interpretation="common price across all five recorded32-state timing scenarios; neither timing confidence nor a claim about every individual clock",
                upper_intersection_is_not_joint_existence_or_adoption=True))
    require(len(costs)==1392 and len(menus)==2832 and len(robust)==472 and len(frontiers)==1392,"Complete fixed volume/clock/menu reporting census")
    return costs,constraints,menus,robust,frontiers


def training_scaling(data,acquisition,cells,contrasts):
    """Two actually acquired budgets; differences are descriptive, not extra units."""
    c={group(r):r for r in cells};result=[]
    for index in range(2):
        for arm in ARMS:
            for loss in LOSSES:
                lo=(index,5,arm,loss);hi=(index,9,arm,loss)
                gain=paired_gain(data,hi,lo,64)
                result.append(dict(index=index,arm=arm,loss=loss,
                    coarse_budget=5,fine_budget=9,
                    coarse_Q_contexts=325,fine_Q_contexts=1053,information_ratio=F(81,25),
                    coarse_features=acquisition[lo]["feature_count"],fine_features=acquisition[hi]["feature_count"],
                    acquisition_cost_ratio=acquisition[hi]["complete_allocated_acquisition_seconds"]/acquisition[lo]["complete_allocated_acquisition_seconds"],
                    full_primary64_cost_ratio=c[hi]["full_primary64_allocated_cost"]/c[lo]["full_primary64_allocated_cost"],
                    gain_fine_relative_to_coarse_lower=gain["lower"],gain_fine_relative_to_coarse_upper=gain["upper"],
                    original_gain_sign=sign_interval(gain["lower"],gain["upper"]),
                    coarse_first_rejections=c[lo]["first_rejections"],fine_first_rejections=c[hi]["first_rejections"],
                    finite_node_residual_coarse=acquisition[lo]["finite_node_marginal_residual"],
                    finite_node_residual_fine=acquisition[hi]["finite_node_marginal_residual"],
                    different_node_sets_make_fit_residual_ratio_descriptive_only=True,
                    state_dimension=2,neither_horizon_nor_state_dimension_scaling=True))
    require(len(result)==28,"All budget-scaling policy pairs")
    return result


def failure_and_research_ledger(inputs,data):
    """Actual whole-study process time; nested timing children are not added twice."""
    failures=[]
    scientific_roots=set(data["paths"].values())
    # Selected actual attempts are immutable and all their partial/failure
    # records are retained. Other whole-attempt failures are bound through the
    # complete launcher registry even when no scientific receipt was reached.
    for directory in sorted(scientific_roots):
        for name in ("FAILED121.jsonl","ERRORS121.jsonl"):
            path=directory/name
            if path.exists():
                for no,row in enumerate(inputs.rows(path),1):
                    failures.append(dict(path=inputs.name(path),line=no,record=row))
    stages=[]
    for name,launch in sorted(data["launches"].items()):
        stages.append(dict(role=name,elapsed_seconds=launch["elapsed_seconds"],
            child_peak_rss_kib=launch["child_peak_rss_kib"],
            generating_source_commit=launch["source_commit"],
            nested_timing_children_included=name=="primary",
            independent_policy_research_validation=name=="independent",
            exact_training_design_validation=name.startswith("training_audit"),
            full_actual_process_not_sum_of_standalone_allocations=True))
    actual=sum((r["elapsed_seconds"] for r in data["ledger"]),F(0))
    selected=sum((r["elapsed_seconds"] for r in stages),F(0))
    failed=[r for r in data["ledger"] if r["exit_code"]!=0]
    scientific_names={"campaign121.py","training_audit121.py","independent121.py","stats121.py"}
    failed_science=[r for r in failed if r["source_commit"]==inputs.args.source_commit and
                    any(Path(str(v)).name in scientific_names for v in r["command"])]
    require(actual>=selected,"Research ledger retains every selected process and other actual attempts")
    ledger=dict(selected_completed_scientific_stages=stages,
        selected_completed_process_seconds=selected,
        all_discovered_outer_launch_seconds=actual,
        other_actual_process_seconds=actual-selected,
        failed_outer_attempts=len(failed),failed_outer_attempt_seconds=sum((r["elapsed_seconds"] for r in failed),F(0)),
        failed_frozen_scientific_attempts=len(failed_science),
        failed_frozen_scientific_attempt_seconds=sum((r["elapsed_seconds"] for r in failed_science),F(0)),
        failed_attempt_receipts=failed,all_actual_launches=data["ledger"],
        selected_failure_records=failures,
        independent_original_policy_validation_seconds=data["launches"]["independent"]["elapsed_seconds"],
        independent_policy_validation_included_in_research_total=True,
        independent_policy_validation_excluded_from_deployment_reuse_formula=True,
        timing_children_already_inside_primary_outer_receipt_not_added_twice=True,
        per_method_allocated_acquisitions_are_not_summed_as_actual_research_time=True,
        reporting_build_publication_and_remote_wait_costs_not_inside_these_scientific_launches=True,
        reporting_actual_cost_recorded_separately_in_EXECUTION_REPORT121=True,
        unallocated_other_or_failed_attempt_costs_remain_explicit_research_cost=True)
    return ledger,stages,failures


def summary_report(data,cells,contrasts,menus,robust,frontiers,models,budgets,processes,research):
    signkeys=("strict-positive","strict-negative","exact-zero","contains-zero")
    def signs(rows,key):
        c=Counter(r[key] for r in rows);return {k:c[k] for k in signkeys}
    controls=data["feature_controls"]
    relu_full=[r for r in menus if r["arm"]=="relu" and r["menu"]=="all-budgets-conventional"]
    relu_robust=[r for r in robust if r["arm"]=="relu" and r["menu"]=="all-budgets-conventional"]
    relu_primary=[r for r in relu_full if r["scenario"]=="primary64"]
    relu_individual=[r for r in relu_full if r["scenario"]!="primary64"]
    require(len(relu_primary)==32 and len(relu_individual)==160 and len(relu_robust)==32,"All neural price scenarios, no clock selection")
    controls_summary={}
    for scenario in SCENARIOS:
        rows=[r for r in controls if r["scenario"]==scenario]
        controls_summary[scenario]=dict(pairs=len(rows),final_action_equal=sum(r["final_action_equal"] for r in rows),
            raw_proposal_equal=sum(r["raw_proposal_equal"] for r in rows))
    q=Counter()
    for r in data["primary"]:q.update(r["counts"])
    per_state_qualified=[exact(r["certified_regret_upper"]) for r in data["primary"]]
    prod_width=[exact(r["complete_policy_upper"])-exact(r["complete_policy_lower"]) for r in data["primary"]]
    scopes=dict(original_dimension=2,risks=[F(1,2),F(3,4)],continuous_original_innovation_law_unchanged=True,
        original_actual_future_controller_unchanged=True,future_value_allowance_once=F(15,16*2**20),
        independent_initial_state_population="product uniform on two 40-bit dyadic coordinates, conditional on the entropy assumption and frozen actors",
        all64_observation_rows_retained_if_duplicate_states=True,
        timing_rows_and_hinge_encodings_are_not_new_independent_units=True,
        fitted_feature_cover_not_numerically_certified=True,
        finite_node_loss_improvement_is_not_by_itself_economic_improvement=True,
        raw_first_proposals_do_not_inherit_final_qualification=True,
        action_error_quantities_are_upper_bounds_not_exact_observed_errors=True,
        interval_overlap_is_compatibility_not_proof_of_narrower_production_endpoints=True,
        descriptive_price_regions_are_not_population_or_calibrated_adoption=True,
        exact_F_M_D_values=data["source"])
    return dict(status="computed_from_actual_completed_records",policy_cells=58,primary_decisions=3712,
        timing_processes=5,timing_decisions=9280,timing_action_identity_checks=len(data["timing_checks"]),
        fitted_models=56,actual_optimizer_fits=48,paid_equal_feature_hinge_copies=8,
        independent_state_units=64,distinct_state_rows=len({tuple(r["state_hex"]) for r in data["states"].values()}),
        independently_evaluated_unique_original_policy_and_proposal_keys=len(data["policies"]),
        independent_terminal_contexts=data["receipts"]["independent"]["counts"]["terminal_contexts"],
        independent_checks=data["receipts"]["independent"]["counts"],
        all_primary_qualified=True,production_regret_target=TAU,production_width_target=WIDTH,
        maximum_saved_production_regret_upper=max(per_state_qualified),maximum_actual_production_interval_width=max(prod_width),
        mean_original_objective_interval_width_range=[min(r["original_objective_mean_upper"]-r["original_objective_mean_lower"] for r in cells),max(r["original_objective_mean_upper"]-r["original_objective_mean_lower"] for r in cells)],
        independent_mean_regret_upper_range=[min(r["independently_reconstructed_regret_mean_upper"] for r in cells),max(r["independently_reconstructed_regret_mean_upper"] for r in cells)],
        original_action_rms_error_upper_range=[min(r["original_action_rms_error_upper"] for r in cells),max(r["original_action_rms_error_upper"] for r in cells)],
        paired_learning_treatments=28,signed_sample64_gain_groups=signs(contrasts,"sample64_sign"),
        joint_population_gain_groups=signs(contrasts,"population_gain_sign"),
        joint_coverage_at_least=F(19,20),threshold_events=112,first_rejection_one_sided_endpoints=116,
        same_value_marginal_final_policy_pairs=sum(r["identical_original_policy_keys"] for r in contrasts),
        changed_value_marginal_final_policy_pairs=28*64-sum(r["identical_original_policy_keys"] for r in contrasts),
        marginal_finite_node_residual_lower_groups=sum(r["node_marginal_residual_change"]<0 for r in contrasts),
        marginal_finite_node_residual_equal_groups=sum(r["node_marginal_residual_change"]==0 for r in contrasts),
        marginal_finite_node_residual_higher_groups=sum(r["node_marginal_residual_change"]>0 for r in contrasts),
        marginal_LP_gap_upper_range=[min(r["marginal_fit_optimality_gap_upper"] for r in contrasts),max(r["marginal_fit_optimality_gap_upper"] for r in contrasts)],
        value_LS_gap_upper_range=[min(r["value_fit_gap_upper"] for r in models if r["loss"]=="value"),max(r["value_fit_gap_upper"] for r in models if r["loss"]=="value")],
        first_rejections=sum(r["first_rejections"] for r in cells),
        numerical_service_failures=sum(r["numerical_service_failures"] for r in cells),
        exact_fallbacks=sum(r["exact_fallbacks"] for r in cells),
        unavailable_raw_proposals=sum(r["unavailable_raw_proposals"] for r in cells),
        final_actions_changed_from_available_first=sum(r["final_actions_changed_from_available_first"] for r in cells),
        qualification_attempts=len(data["attempts"]),unqualified_attempts=sum(not r["qualified"] for r in data["attempts"]),
        qualification_stages=dict(Counter(r["stage"] for r in data["attempts"])),
        actual_primary_operation_counts=dict(q),
        marginal_faster_primary_complete_cohort_groups=sum(r["actual_primary64_cohort_cost_ratio"]<1 for r in contrasts),
        marginal_slower_primary_complete_cohort_groups=sum(r["actual_primary64_cohort_cost_ratio"]>1 for r in contrasts),
        marginal_faster_primary_full_allocated_groups=sum(r["actual_primary64_full_allocated_cost_ratio"]<1 for r in contrasts),
        marginal_slower_primary_full_allocated_groups=sum(r["actual_primary64_full_allocated_cost_ratio"]>1 for r in contrasts),
        marginal_faster_timing_complete_cohort_clocks=sum(r<1 for c in contrasts for r in c["all_five_timing32_cohort_cost_ratios"]),
        marginal_slower_timing_complete_cohort_clocks=sum(r>1 for c in contrasts for r in c["all_five_timing32_cohort_cost_ratios"]),
        marginal_faster_timing_full_allocated_clocks=sum(r["full_cost_faster_timing_clocks"] for r in contrasts),
        marginal_slower_timing_full_allocated_clocks=sum(r["full_cost_slower_timing_clocks"] for r in contrasts),
        all140_timing_cohort_ratio_range=[min(r for c in contrasts for r in c["all_five_timing32_cohort_cost_ratios"]),max(r for c in contrasts for r in c["all_five_timing32_cohort_cost_ratios"])],
        all140_timing_full_cost_ratio_range=[min(r for c in contrasts for r in c["all_five_timing32_full_allocated_cost_ratios"]),max(r for c in contrasts for r in c["all_five_timing32_full_allocated_cost_ratios"])],
        equal_feature_control=controls_summary,
        complete_volume_cost_rows=1392,complete_frontier_rows=len(frontiers),price_menu_rows=len(menus),five_clock_price_intersection_rows=len(robust),
        relu_full_menu_primary_price_cells=32,relu_full_menu_individual_timing_price_cells=160,relu_full_menu_all_five_price_cells=32,
        relu_primary_sufficient_nonempty=sum(not r["sufficient_price_domain"]["empty"] for r in relu_primary),
        relu_primary_upper_not_ruled_out_nonempty=sum(not r["upper_not_ruled_out_price_domain"]["empty"] for r in relu_primary),
        relu_individual_timing_sufficient_nonempty=sum(not r["sufficient_price_domain"]["empty"] for r in relu_individual),
        relu_individual_timing_upper_not_ruled_out_nonempty=sum(not r["upper_not_ruled_out_price_domain"]["empty"] for r in relu_individual),
        relu_all_five_sufficient_nonempty=sum(not r["sufficient_price_domain"]["empty"] for r in relu_robust),
        relu_all_five_upper_not_ruled_out_nonempty=sum(not r["upper_not_ruled_out_price_domain"]["empty"] for r in relu_robust),
        strict_upper_not_ruled_out_is_not_jointly_attainable_adoption=True,
        failed_frozen_scientific_attempts_in_research_ledger=research["failed_frozen_scientific_attempts"],
        failed_frozen_scientific_attempt_seconds=research["failed_frozen_scientific_attempt_seconds"],
        complete_selected_scientific_process_seconds=research["selected_completed_process_seconds"],
        independent_original_policy_validation_seconds=research["independent_original_policy_validation_seconds"],
        budget_processes=budgets,service_processes=processes,scope=scopes)


class Outputs:
    """Deterministic table bytes; clocks and absolute custody paths are separate."""
    def __init__(self,root):self.root=Path(root);self.stable=[]

    def remember(self,path):
        self.stable.append(path.relative_to(self.root).as_posix())

    def json(self,name,obj,stable=True):
        p=self.root/name;write_json(p,obj)
        if stable:self.remember(p)

    def rows(self,name,rows,compressed=False):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True)
        if compressed:
            with p.open("xb") as raw:
                with gzip.GzipFile(fileobj=raw,mode="wb",filename="",mtime=0,compresslevel=6) as stream:
                    for row in rows:stream.write((json.dumps(encoded(row),sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode())
                raw.flush();os.fsync(raw.fileno())
        else:
            with p.open("x",encoding="utf-8",newline="\n") as stream:
                for row in rows:stream.write(json.dumps(encoded(row),sort_keys=True,separators=(",",":"),allow_nan=False)+"\n")
                stream.flush();os.fsync(stream.fileno())
        self.remember(p)

    def csv(self,name,rows,compressed=False):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True)
        fields=sorted({key for row in rows for key in row})
        def emit(stream):
            writer=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n");writer.writeheader()
            for row in rows:
                cooked={}
                for key,value in row.items():
                    value=encoded(value)
                    cooked[key]="" if value is None else json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False) if isinstance(value,(dict,list)) else value
                writer.writerow(cooked)
        if compressed:
            with p.open("xb") as raw:
                with gzip.GzipFile(fileobj=raw,mode="wb",filename="",mtime=0,compresslevel=6) as gz:
                    with io.TextIOWrapper(gz,encoding="utf-8",newline="") as stream:emit(stream);stream.flush()
                raw.flush();os.fsync(raw.fileno())
        else:
            with p.open("x",encoding="utf-8",newline="") as stream:emit(stream);stream.flush();os.fsync(stream.fileno())
        self.remember(p)

    def table(self,stem,rows,large=False):
        suffix=".jsonl.gz" if large else ".jsonl"
        self.rows("tables121/"+stem+suffix,rows,large)
        self.csv("tables121/"+stem+(".csv.gz" if large else ".csv"),rows,large)

    def text(self,name,content):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True)
        with p.open("x",encoding="utf-8",newline="\n") as stream:stream.write(content);stream.flush();os.fsync(stream.fileno())
        self.remember(p)


def fixed(value,digits=3,direction=None):
    """Exact rational decimal rounding, including outward interval endpoints."""
    value=exact(value);scale=10**digits;num=value.numerator*scale;den=value.denominator
    integer,remainder=divmod(num,den)
    if direction=="up":integer+=int(remainder!=0)
    elif direction is None and (2*remainder>den or (2*remainder==den and integer%2)):integer+=1
    sign="-" if integer<0 else "";integer=abs(integer)
    if not digits:return sign+str(integer)
    return sign+str(integer//scale)+"."+str(integer%scale).zfill(digits)


def interval_tex(lo,hi,scale=1,digits=2):
    if lo is None or hi is None:return r"\text{unavailable}"
    lo,hi=exact(lo)*scale,exact(hi)*scale
    if lo==hi==0:return "[0,0]"
    return "["+fixed(lo,digits,"down")+","+fixed(hi,digits,"up")+"]"


def tex_escape(value):
    text=str(value)
    mapping={"\\":r"\textbackslash{}","&":r"\&","%":r"\%","$":r"\$","#":r"\#",
             "_":r"\_","{":r"\{","}":r"\}","~":r"\textasciitilde{}","^":r"\textasciicircum{}"}
    return "".join(mapping.get(c,c) for c in text)


ARM_TEX={"quadratic":"Quad.","relu":"ReLU","hinge":"Hinge","spline":"Spline",
         "poly2":"Poly2","poly3":"Poly3","grid":"Grid","online":"Online"}


def method_tex(row):
    loss={"value":"V","marginal":"M","online":"O"}[row["loss"]]
    return ARM_TEX[row["arm"]]+" "+loss


def risk_tex(index):return "1/2" if index==0 else "3/4"


def long_table(caption,label_name,headers,rows,colspec=None):
    cols=colspec or "l"+"r"*(len(headers)-1)
    content=[r"\begingroup",r"\small\setlength{\tabcolsep}{3pt}",
             r"\begin{longtable}{"+cols+"}",
             r"\caption{"+caption+r"}\label{"+label_name+r"}\\",
             r"\toprule"," & ".join(headers)+r"\\",r"\midrule\endfirsthead",
             r"\toprule"," & ".join(headers)+r"\\",r"\midrule\endhead",
             r"\midrule\multicolumn{"+str(len(headers))+r"}{r}{Continued on next page}\\\endfoot",
             r"\bottomrule\endlastfoot"]
    content.extend(" & ".join(map(str,row))+r"\\" for row in rows)
    content.extend([r"\end{longtable}",r"\endgroup",""])
    return "\n".join(content)


def domain_tex(domain):
    if domain["empty"]:return r"\varnothing"
    lo=domain["lower"];hi=domain["upper"]
    # The exact endpoints, including strictness, remain in the machine table.
    def number(value):
        if value==0:return "0"
        with localcontext() as ctx:
            ctx.prec=20
            val=Decimal(value.numerator)/Decimal(value.denominator)
            return format(val,".3E").replace("E+",r"\!\times\!10^{+")+"}" if "E+" in format(val,".3E") else format(val,".3E").replace("E-",r"\!\times\!10^{-")+"}"
    left="[" if domain["lower_closed"] else "("
    right="]" if domain["upper_closed"] else ")"
    return left+number(lo)+","+(r"\infty" if hi is None else number(hi))+right


def manuscript_text(summary,cells,contrasts,models,budgets,processes,menus,robust,scaling):
    s=summary;sg=s["signed_sample64_gain_groups"];pg=s["joint_population_gain_groups"]
    main=[r"\section{Learning the original action marginal: completed evidence}\label{sec:results121}",
        "The experiment changes the fitted original Bellman critic. VALUE and MARGINAL use the same paid original-law value probes, the same anchored features, coefficient boxes and feasible proposal rule within each budget. MARGINAL is fitted to minimize the finite-node robust action-marginal loss; VALUE is fitted to minimize bounded value least squares. Both fitting calculations retain their actual independently bounded optimization gaps. The trained critic proposes an action, and the unchanged original-model service qualifies the complete policy. Thus a smaller training loss and a better original economic decision are distinct outcomes.",
        "All 56 stored actors and the online comparator were fixed before the new 64-row initial-state sample. The completed study contains all 58 risk--policy cells, 3,712 primary decisions and 9,280 decisions in five fresh serial timing processes. Both risks share the same 64 initial states; neither timing repeats nor the equal-feature hinge encoding increase the number of independent observations. The innovation distribution remains continuous and the original future controller is unchanged.",
        f"The independent primitive implementation evaluated {s['independently_evaluated_unique_original_policy_and_proposal_keys']:,} distinct exact state--action--risk keys, including every available first proposal and every final policy, using {s['independent_terminal_contexts']:,} terminal contexts. Its fixed 64-cell enclosures reconstruct original optimized-continuation values and add the unchanged $\\beta 2^{{-20}}$ future-policy allowance once. Agreement with production intervals is compatibility; it does not certify the production compiler's narrower endpoints. All final production policies qualified at regret target $1/256$ and interval-width target $1/8192$. The largest saved production regret upper bound was {fixed(s['maximum_saved_production_regret_upper'],7,'up')}, and the largest recorded interval width was {fixed(s['maximum_actual_production_interval_width'],8,'up')}.",
        r"\subsection{Original economic gains and the cost of qualification}\label{subsec:learninggains121}",
        f"Of the 28 prespecified MARGINAL-minus-VALUE treatments, independently enclosed gain $J_{{\\rm V}}-J_{{\\rm M}}$ was strictly positive in {sg['strict-positive']}, strictly negative in {sg['strict-negative']}, exactly zero in {sg['exact-zero']}, and contained zero in {sg['contains-zero']} complete-sample comparisons. Actual final actions differed in {s['changed_value_marginal_final_policy_pairs']:,} of the 1,792 paired state records. Under the fixed joint 95 percent population family, {pg['strict-positive']} mean-gain lower bounds were positive, {pg['strict-negative']} mean-gain upper bounds were negative, {pg['exact-zero']} intervals were exactly zero and {pg['contains-zero']} contained zero. These are signed learning treatments: they do not inherit the nonnegative safe-gain restriction of the older post-fit R120 intervention.",
        "Table~\\ref{tab:learninggains121} reports every treatment. Gain intervals are outward decimal displays of exact rational record arithmetic. A positive gain denotes lower original cost under MARGINAL. The population column uses only the 64 initial-state units and the prospectively fixed simultaneous family; it is not a confidence interval for runtime or for superiority over the entire representation menu."]
    gain_rows=[]
    for r in contrasts:
        gain_rows.append(["$"+risk_tex(r["index"])+"$",r["budget"],ARM_TEX[r["arm"]],
            "$"+interval_tex(r["sample64_gain_lower"],r["sample64_gain_upper"],10**6,2)+"$",
            "$"+interval_tex(r["population_gain_lower"],r["population_gain_upper"],10**3,3)+"$",
            r["first_rejection_change"],fixed(r["actual_primary64_cohort_cost_ratio"],3),
            fixed(r["median_timing32_cohort_ratio"],3)])
    main.append(long_table("All learning contrasts. Sample gain is in $10^{-6}$ original objective units; population gain is in $10^{-3}$ units. $\\Delta R$ is MARGINAL minus VALUE first rejections. $T$ ratios compare MARGINAL with VALUE for the complete cohort; the five-clock column is their descriptive median, with every clock retained in the development tables.",
        "tab:learninggains121",[r"$\alpha$","Grid","Family",r"Sample $10^6G$",r"Population $10^3G$",r"$\Delta R$",r"$T_{64}$",r"Med. $T_{32}$"],gain_rows,"rrlrrrrr"))
    main.extend([
        f"Across the full primary catalogue, {s['first_rejections']:,} first proposals were not accepted, {s['final_actions_changed_from_available_first']:,} available first actions changed before deployment, {s['numerical_service_failures']} numerical service failures were retained and {s['exact_fallbacks']} exact fallbacks were used. There were {s['unavailable_raw_proposals']} unavailable raw proposals and {s['qualification_attempts']:,} saved qualification attempts, of which {s['unqualified_attempts']:,} did not qualify. Every attempted action and its paid work remain recorded. A final qualifying action does not retroactively qualify a rejected raw action.",
        "The independent evaluator reports original objective, optimum and regret intervals for each final policy and available raw proposal. Squared action error is bounded using the original curvature, and the reported RMS quantity is an upper bound, not an observed exact action error. A raw-proposal cell aggregate is unavailable if any raw proposal is absent. Complete independent regret intervals are retained alongside their intersection with the separately proved final-service regret cap; the fixed statistical program states which interval it uses.",
        r"\subsection{What the learning calculation certifies}\label{subsec:fitresults121}",
        f"The exact independent finite-design audit found a smaller stored-coefficient marginal residual for MARGINAL in {s['marginal_finite_node_residual_lower_groups']} of the 28 treatments, equality in {s['marginal_finite_node_residual_equal_groups']}, and a larger residual in {s['marginal_finite_node_residual_higher_groups']}. It reconstructs the feature and derivative design with rational arithmetic, checks the 30-bit coefficients and boxes, and bounds the finite-box optimum using valid rational dual weights. The marginal optimality-gap upper bounds range from {fixed(s['marginal_LP_gap_upper_range'][0],7,'down')} to {fixed(s['marginal_LP_gap_upper_range'][1],7,'up')}; the corresponding VALUE least-squares gap upper bounds range from {fixed(s['value_LS_gap_upper_range'][0],7,'down')} to {fixed(s['value_LS_gap_upper_range'][1],7,'up')}. The complete per-model results include floating-design discrepancies and both losses evaluated at every actual stored coefficient vector.",
        "These finite-node optimization statements establish the implemented fitting calculation. A global feature-cover bound was not numerically established by this experiment, and a small node residual is not a substitute for the separate original-law policy certificate. The two grids measure paid information and feature-budget changes within this two-state, two-date economy. They do not provide state-dimension, horizon or innovation-dimension scaling evidence.",
        f"The ReLU and hinge controls have identical fixed features and stored readouts. In the primary records, {s['equal_feature_control']['primary64']['final_action_equal']} of {s['equal_feature_control']['primary64']['pairs']} paired final actions and {s['equal_feature_control']['primary64']['raw_proposal_equal']} paired raw proposals were identical. All five timing comparisons are retained separately. Hinge pays the corresponding full ReLU fitting charge plus its own identity, encoding and audit costs. It is a conventional equal-feature control, not an independent fit or an additional independent scientific outcome; shared geometry cannot establish a neural-exclusive representation advantage.",
        r"\subsection{Full paid comparisons and conditional use}\label{subsec:costresults121}",
        f"MARGINAL had a lower complete-cohort primary clock in {s['marginal_faster_primary_complete_cohort_groups']} of 28 treatments and a higher clock in {s['marginal_slower_primary_complete_cohort_groups']}. Among all 140 matched repeated clocks, it was faster in {s['marginal_faster_timing_complete_cohort_clocks']} and slower in {s['marginal_slower_timing_complete_cohort_clocks']}; the complete-cohort ratios ranged from {fixed(s['all140_timing_cohort_ratio_range'][0],3)} to {fixed(s['all140_timing_cohort_ratio_range'][1],3)}. When acquisition and the declared process overhead are included at the measured cohort size, the five-clock comparisons contain {s['marginal_faster_timing_full_allocated_clocks']} lower-cost and {s['marginal_slower_timing_full_allocated_clocks']} higher-cost MARGINAL records. These repeated observations describe the recorded hardware circumstances and are not runtime confidence bounds.",
        "Each learned method pays the complete shared risk-label bundle, its own complete fit and serialization phase, the corresponding required exact training audit, and the explicitly allocated common process residual. Hinge also pays its parent ReLU phase and parent training audit. Competitors' fits and the other risk's labels are not charged as information used by that method. Each service clock includes loading, original-law certification, rejected candidates, refinement and fallback; event serialization is already inside these measured clocks and is not added again. These component sums are declared standalone allocations of actual measurements, not separately observed one-model processes.",
        f"The selected acquisition, training-audit, primary-with-five-timings, independent-validation and statistical subprocess receipts total {fixed(s['complete_selected_scientific_process_seconds'],3)} seconds. The independent original-policy evaluator contributes {fixed(s['independent_original_policy_validation_seconds'],3)} seconds of that research cost. Failed frozen-source scientific attempts number {s['failed_frozen_scientific_attempts_in_research_ledger']}, with {fixed(s['failed_frozen_scientific_attempt_seconds'],3)} additional seconds retained in the whole-study ledger. Reporting, typesetting, publication and remote waits have their own receipts and are outside these selected scientific clocks. The nested timing children are already inside the primary outer clock and are not added twice.",
        r"For the prespecified reuse volumes $N\in\{64,256,1024,16384\}$, the deployment scenario is $C_m(N)=A_m+H_m+L_m+(N/n)(T_m-L_m)$. Here $A_m$ is the allocated acquisition and training-audit cost, $H_m$ the stated common process residual, $L_m$ the cold load, and $T_m$ the measured complete cohort. The primary scenario has $n=64$ and matching 64-state economics; each timing scenario has $n=32$ and matching first-32 economics. Independent all-policy research validation is reported separately and excluded from this deployment-reuse formula. Reuse is a specified amortization calculation, not measured throughput.",
        r"For every conventional rival, the criterion is $N J_m+p C_m(N)$ with $p\geq0$ in original objective units per measured second. A sufficient price domain requires the lower original-gain bound minus $p$ times the extra cost to be strictly positive. The upper domain is only a pairwise condition not ruled out by these intervals. The machine tables preserve all full-menu and within-budget rivals, empty domains, reversed cost inequalities and strict endpoints.",
        f"For the eight ReLU risk--budget--loss cells and four volumes, the primary64 comparisons yield {s['relu_primary_sufficient_nonempty']} nonempty sufficient regions and {s['relu_primary_upper_not_ruled_out_nonempty']} nonempty upper regions among 32 full-menu scenarios. The 160 individual timing scenarios yield {s['relu_individual_timing_sufficient_nonempty']} nonempty sufficient and {s['relu_individual_timing_upper_not_ruled_out_nonempty']} nonempty upper regions. Intersecting all five clocks at a common price leaves {s['relu_all_five_sufficient_nonempty']} nonempty sufficient and {s['relu_all_five_upper_not_ruled_out_nonempty']} nonempty upper regions among 32 cases. An empty five-clock intersection does not state that every individual-clock region is empty. A nonempty upper intersection neither establishes joint attainability nor justifies adoption or population superiority.",
        "All 58 cells, all conventional wins and losses, all 28 learning and 28 budget contrasts, the full pairwise recorded-menu comparisons, the 348 distinct cohort clocks and all 1,392 cost/frontier rows remain in the development and machine tables. Methods whose original-objective and paid-cost intervals leave an unresolved choice remain unresolved."])
    dev=[r"\section{Complete R121 numerical tables}\label{sec:developmentresults121}",
        "These tables are deterministic displays of completed, hash-bound records. V and M denote VALUE and MARGINAL; O denotes the online original-model comparator. Every risk and method is retained. Interval endpoints are rounded outward; clocks are descriptive rounded displays. Exact rational numbers, all row-level observations and all conditional price endpoints remain in the machine tables.",
        r"\subsection{All original policy levels and action bounds}"]
    rows=[]
    for r in cells:
        rows.append(["$"+risk_tex(r["index"])+"$",r["budget"],method_tex(r),
            "$"+interval_tex(r["original_objective_mean_lower"],r["original_objective_mean_upper"],1,6)+"$",
            "$"+interval_tex(r["independently_reconstructed_regret_mean_lower"],r["independently_reconstructed_regret_mean_upper"],10**6,2)+"$",
            fixed(r["original_action_rms_error_upper"],6,"up"),r["first_rejections"],r["final_actions_changed_from_available_first"]])
    dev.append(long_table("All 58 complete policy cells, each with 64 independent initial-state rows. Original regret is the independently reconstructed interval in $10^{-6}$ units before any use of the production cap. RMS is an upper bound on original action error. Reject counts retain the first proposal, and changed counts compare every available raw proposal with the final action.",
        "tab:allpolicies121",[r"$\alpha$","Grid","Policy",r"Mean original $J$",r"$10^6$ regret","RMS bound","Reject","Changed"],rows,"rrlrrrrr"))
    raw=[]
    for r in cells:
        raw.append(["$"+risk_tex(r["index"])+"$",r["budget"],method_tex(r),
            "$"+interval_tex(r["raw_proposal_original_objective_mean_lower"],r["raw_proposal_original_objective_mean_upper"],1,6)+"$",
            "$"+interval_tex(r["raw_proposal_regret_mean_lower"],r["raw_proposal_regret_mean_upper"],10**6,2)+"$",
            r["unavailable_raw_proposals"],r["exact_fallbacks"],r["qualification_attempts"]])
    dev.append(long_table("All first-proposal outcomes and completion work. Raw proposals have no final qualification guarantee; an aggregate with any unavailable raw proposal is explicitly unavailable. Every unique available raw action, including rejections, was independently evaluated.",
        "tab:rawproposals121",[r"$\alpha$","Grid","Policy",r"Raw mean $J$",r"Raw $10^6$ regret","Missing","Exact","Attempts"],raw,"rrlrrrrr"))
    fitrows=[]
    for r in models:
        gap=r["marginal_fit_gap_upper"] if r["loss"]=="marginal" else r["value_fit_gap_upper"]
        fitrows.append(["$"+risk_tex(r["index"])+"$",r["budget"],method_tex(r),r["feature_count"],
            fixed(r["finite_node_marginal_residual"],5,"up"),fixed(r["value_mean_squared_residual"],7,"up"),
            fixed(gap,7,"up"),fixed(r["complete_allocated_acquisition_seconds"],3)])
    dev.append(r"\subsection{All finite-design fits and acquisition charges}")
    dev.append(long_table("Every stored model. The marginal residual is the robust finite-node residual at the actual 30-bit coefficients. V-MSE evaluates the VALUE loss on all paid value probes. The gap bounds the optimum of the method's own finite-box fitting problem: least-squares for V, minimax marginal for M. The full charge includes the declared shared information, model phases and required audit; it is not a new isolated process timing.",
        "tab:allfits121",[r"$\alpha$","Grid","Policy","Features","Marg. res.","V-MSE","Own gap","Acq.+audit s"],fitrows,"rrlrrrrr"))
    costrows=[]
    for r in cells:
        costrows.append(["$"+risk_tex(r["index"])+"$",r["budget"],method_tex(r),
            fixed(r["complete_allocated_acquisition_seconds"],3),fixed(r["actual_primary64_cohort_seconds"],3),
            fixed(r["full_primary64_allocated_cost"],3),fixed(r["timing32_cohort_seconds_median"],3),
            "$"+interval_tex(r["timing32_cohort_seconds_minimum"],r["timing32_cohort_seconds_maximum"],1,3)+"$"])
    dev.append(r"\subsection{Full costs and all five clocks}")
    dev.append(long_table("Complete costs in seconds for all 58 cells. Primary full cost is acquisition plus allocated common process residual plus the measured 64-state cohort. The timing median and range describe all five measured 32-state cohorts, excluding the separately displayed acquisition charge. Every individual clock follows below.",
        "tab:fullcost121",[r"$\alpha$","Grid","Policy","Acq.+audit",r"Cohort $T_{64}$",r"Full $C_{64}$",r"Med. $T_{32}$",r"Range $T_{32}$"],costrows,"rrlrrrrr"))
    clockrows=[]
    for r in cells:
        clockrows.append(["$"+risk_tex(r["index"])+"$",r["budget"],method_tex(r)]+[fixed(v,4) for v in r["timing32_cohort_seconds_all_five"]])
    dev.append(long_table("All 290 separate 32-state complete-cohort clocks in seconds, without selecting repeats. The other 58 primary cohort clocks are in Table~\\ref{tab:fullcost121}. All 9,280 timing actions and first-proposal identities were checked against the matching primary records.",
        "tab:allclocks121",[r"$\alpha$","Grid","Policy","Clock 0","Clock 1","Clock 2","Clock 3","Clock 4"],clockrows,"rrlrrrrr"))
    scalerows=[]
    for r in scaling:
        scalerows.append(["$"+risk_tex(r["index"])+"$",method_tex(r),
            str(r["coarse_features"])+"/"+str(r["fine_features"]),
            fixed(r["acquisition_cost_ratio"],3),fixed(r["full_primary64_cost_ratio"],3),
            "$"+interval_tex(r["gain_fine_relative_to_coarse_lower"],r["gain_fine_relative_to_coarse_upper"],10**6,2)+"$",
            str(r["coarse_first_rejections"])+"/"+str(r["fine_first_rejections"])])
    dev.append(r"\subsection{Every budget change and price condition}")
    dev.append(long_table("All 28 fine-versus-coarse comparisons. Both acquisition processes actually recompute their complete original-law bundles. Cost ratios are budget9 divided by budget5; gain is original cost under budget5 minus cost under budget9, in $10^{-6}$ units. Feature and rejection entries show coarse/fine. These are recorded-sample comparisons, with no cross-budget population superiority claim.",
        "tab:budgetscaling121",[r"$\alpha$","Policy","Features","Acq. ratio",r"$C_{64}$ ratio",r"$10^6$ fine gain","Rejects"],scalerows,"rlrrrrr"))
    priced=[]
    for r in robust:
        if r["arm"]!="relu" or r["menu"]!="all-budgets-conventional":continue
        priced.append(["$"+risk_tex(r["index"])+"$",r["budget"],method_tex(r),r["volume"],
            "$"+domain_tex(r["sufficient_price_domain"])+"$","$"+domain_tex(r["upper_not_ruled_out_price_domain"])+"$"])
    dev.append(long_table("All 32 ReLU conditions against the full conventional menu, intersected over all five matching 32-state clocks. Price is in original objective units per second. Decimal endpoints are descriptive approximations; exact rational endpoints and open/closed flags are in the machine tables. An upper region is only not ruled out pairwise and never denotes established adoption. Individual-clock and primary64 regions are all retained in the machine tables.",
        "tab:reluprices121",[r"$\alpha$","Grid","Policy",r"$N$","Sufficient price","Upper not ruled out"],priced,"rrlrrr"))
    dev.extend([r"\subsection{Machine tables and exact record custody}",
        "The machine companion retains all 3,712 state-level economic rows and every original key; the 56 independent fit audits and their exact finite-design gaps; all 1,624 unordered full-menu original-objective comparisons (812 for all64 and 812 for the first32); all 348 clock and counter records; all 9,280 timing identity checks; all actual first and rejected candidates, root traces and qualification stages; 1,392 complete volume-cost/frontier rows; every individual pairwise price constraint; 2,832 full or within-budget menu regions and 472 five-clock intersections. Empty, adverse and inconclusive cases are included. Not being certifiably dominated by these interval records does not prove membership of the unknown exact economic frontier.",
        "The output manifest lists every deterministic replay file. Execution duration, absolute input locations, file metadata and the evolving publication/support ledger are separate custody products, excluded from byte-identical scientific-table replay with that exclusion stated explicitly. The frozen scientific files, actor artifact M and state artifact D are checked against immutable Git objects before reporting. This program imports no production economic primitive, training solver or evaluator and does not reacquire, refit, redraw, resolve an economic action or retime a service."])
    return "\n\n".join(main)+"\n","\n\n".join(dev)+"\n"


def publish_tables(outputs,data,acquisition,budgets,models,processes,clock_rows,cells,
                   state_rows,pairs,contrasts,costs,constraints,menus,robust,frontiers,
                   scaling,research,stages,summary):
    outputs.json("SUMMARY_REPORT121.json",summary)
    outputs.table("policy_cells121",cells)
    outputs.table("state_economics121",state_rows,True)
    outputs.table("loss_contrasts121",contrasts)
    outputs.table("all_policy_contrasts121",pairs,True)
    outputs.table("fit_and_acquisition121",models)
    outputs.table("independent_fit_audits121",[data["fit_audits"][k] for k in GROUPS if k[1]!=0],True)
    outputs.table("budget_processes121",budgets)
    outputs.table("service_processes121",processes)
    outputs.table("all_cohort_clocks121",clock_rows)
    outputs.table("all_timing_action_checks121",data["timing_checks"],True)
    outputs.table("equal_feature_control121",data["feature_controls"],True)
    outputs.table("all_qualification_attempts121",data["attempts"],True)
    outputs.rows("tables121/all_actor_traces121.jsonl.gz",data["actor_rows"],True)
    outputs.table("budget_scaling121",scaling)
    outputs.table("all_volume_costs121",costs)
    outputs.table("all_price_constraints121",constraints,True)
    outputs.table("all_price_menus121",menus,True)
    outputs.table("all_five_clock_price_intersections121",robust,True)
    outputs.table("all_cost_frontiers121",frontiers,True)
    outputs.table("original_optimum_inference121",data["statopt"])
    outputs.table("all_policy_population_inference121",data["statgroups"],True)
    threshold_rows=[]
    for r in data["statcontrasts"]:
        for event in r["threshold_events"]:
            threshold_rows.append(dict(index=r["index"],budget=r["budget"],arm=r["arm"],
                **event,independent_units=64,one_sided_failure_budget=F(1,11200),
                event_counts_only_independently_certified_sign=True))
    require(len(threshold_rows)==112,"Every frozen signed event endpoint")
    outputs.table("all_signed_threshold_events121",threshold_rows)
    outputs.table("selected_research_stage_costs121",stages)
    outputs.json("RESEARCH_LEDGER121.json",research,False)
    main,development=manuscript_text(summary,cells,contrasts,models,budgets,processes,menus,robust,scaling)
    outputs.text("new121/results121.tex",main)
    outputs.text("new121/development121_results.tex",development)
    outputs.text("TABLE_SCOPE121.md", """# R121 deterministic reporting products

All numerical rows are computed from the actual completed, hash-bound records.
The reporter imports only the Python standard library. It performs no economic
evaluation, fitting, entropy acquisition, or timing rerun.

`policy_cells121` retains all 58 cells; `state_economics121` all 3,712 primary
rows including every available raw proposal; `loss_contrasts121` all 28 signed
VALUE/MARGINAL comparisons; `all_policy_contrasts121` all 812 unordered policy
pairs for each of the 64-state and first-32-state cohorts. The joint population
family is restricted to the frozen 2 optimal-value, 58 regret, 28 gain,
112 signed event and 116 rejection-endpoint quantities.

`fit_and_acquisition121` and `independent_fit_audits121` retain all 56 stored
models. Finite-node fitting gaps are separate from global feature-cover and
economic-policy claims. Equal-feature hinge copies are charged their parent
ReLU fit and audit plus their own required work. They are not independent fits.

`all_cohort_clocks121` retains all 58 primary plus 290 distinct repeated cohort
clocks; `all_timing_action_checks121` retains all 9,280 action checks. Costs use
exact rational sums of recorded binary64 clock components; displayed decimals
are descriptive. The complete common residual is a stated allocation from the
actual full process, not an observed isolated one-model clock. The nested five
timing processes are inside the primary outer process and are not added twice
to the actual study ledger. Event serialization already lies inside its phase.

`all_volume_costs121` and `all_cost_frontiers121` contain all 1,392 prescribed
clock/volume/policy scenarios. Reuse C=A+H+L+(N/n)(T-L) is hypothetical except at
the actually observed cohort size. Each scenario uses matching original
economic rows: 64 for primary, first32 for each of five timing clocks.
Independent all-policy economic validation is included in RESEARCH_LEDGER121
and excluded from this explicitly stated deployment-reuse formula; required
training audits and production certification remain in the method charges.
Other failed or support attempts remain in the full ledger and are not silently
identified with a successful standalone method's measured components.

`all_price_constraints121` retains every conventional rival, including the
online original-model comparator. `all_price_menus121` contains 2,832 full or
within-budget regions, and `all_five_clock_price_intersections121` 472 common
five-clock conditions. Price endpoints and open/closed flags are exact rational
records. Upper intersections are only pairwise not ruled out, not joint
attainability or adoption. An empty five-clock intersection does not imply that
all individual-clock regions are empty. Non-domination by interval evidence is
not proof of the unknown exact economic frontier.

JSONL and CSV tables represent rationals as exact numerator/denominator strings.
Nested CSV objects are JSON. Gzip products use an empty header name and mtime0.
Every file in OUTPUT_MANIFEST121.stable_replay_files must replay byte-for-byte.
START_REPORT121, INPUTS_REPORT121, EXECUTION_REPORT121, RESEARCH_LEDGER121 and the
output manifest retain actual execution/location/custody information and are
explicitly excluded from stable table equality. Reporting and publication
costs are separately measured support work; no scientific clock is retimed.
""")


def arguments(argv=None):
    here=Path(__file__).resolve()
    native=here.parent.parent if here.parent.name=="code121" else None
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision",type=Path,default=native,required=native is None)
    parser.add_argument("--evidence-root",type=Path)
    parser.add_argument("--repository",type=Path)
    for name in ("source-commit","actor-commit","state-commit"):parser.add_argument("--"+name,required=True)
    defaults={"acquisition5":"results121/acquisition5-attempt01",
              "acquisition9":"results121/acquisition9-attempt01",
              "training-audit5":"results121/training-audit5-attempt01",
              "training-audit9":"results121/training-audit9-attempt01",
              "states":"results121/states-attempt01","primary":"results121/primary-attempt01",
              "independent":"results121/independent-attempt01","stats":"results121/stats-attempt01"}
    for name,default in defaults.items():parser.add_argument("--"+name,type=Path,default=Path(default))
    parser.add_argument("--ledger-root",type=Path,default=Path("results121"),
                        help="Completed LAUNCH121 receipts under this evidence-relative directory; explicit external ledger roots must remain inside evidence-root")
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--integrity-only",action="store_true",help="Run only immutable-byte, census, saved-record and cost gates; no scientific solver is invoked in either mode")
    args=parser.parse_args(argv);args.revision=args.revision.resolve()
    if args.evidence_root is None:args.evidence_root=args.revision
    args.evidence_root=args.evidence_root.resolve()
    if args.repository is None:
        args.repository=Path(subprocess.check_output(["git","-C",str(args.revision),"rev-parse","--show-toplevel"],text=True).strip())
    args.repository=args.repository.resolve();args.output=args.output.resolve()
    return args


def main(argv=None):
    args=arguments(argv);out=args.output;out.mkdir(parents=True,exist_ok=False)
    COUNTS.clear();start_wall=time.time();clock=time.perf_counter()
    source_path=Path(__file__).resolve();report_identity=file_identity(source_path)
    start=dict(status="started",kind="integrity121" if args.integrity_only else "reporting121",
        started_unix=start_wall,command=[sys.executable,str(source_path)]+list(sys.argv[1:] if argv is None else argv),
        arguments=vars(args),reporting_source=dict(path=str(source_path),**report_identity),
        reporting_source_is_postprocessing_not_the_prospective_scientific_freeze=True,
        original_scientific_evaluation_performed=False)
    write_json(out/"START_REPORT121.json",start);inputs=Inputs(args);outputs=Outputs(out)
    try:
        print("REPORT121 immutable source, actors, states and complete actual records",flush=True)
        data=certify_records(inputs)
        acquisition,budgets,models=acquisition_costs(data)
        clocks,processes,clock_rows=service_costs(data,acquisition)
        research,stages,failures=failure_and_research_ledger(inputs,data)
        if args.integrity_only:
            outputs.json("INTEGRITY121.json",dict(status="verified_saved_records",source=data["source"],
                policy_cells=58,models=56,primary_rows=3712,timing_rows=9280,
                independent_unique_keys=len(data["policies"]),all_available_raw_and_final_keys_evaluated=True,
                original_terminal_contexts=data["receipts"]["independent"]["counts"]["terminal_contexts"],
                paired_treatments=28,threshold_endpoints=112,first_rejection_endpoints=116,
                clock_rows=len(clock_rows),qualification_attempts=len(data["attempts"]),
                equal_feature_control_pairs=len(data["feature_controls"]),
                no_original_economic_evaluation_or_timing_rerun=True,
                production_compatibility_does_not_certify_narrower_endpoints=True))
            outputs.json("RESEARCH_LEDGER121.json",research,False)
        else:
            print("REPORT121 exact original economic contrasts and all complete-cost scenarios",flush=True)
            cells,state_rows,pairs,contrasts,pair_cache=economic_tables(data,acquisition,clocks)
            costs,constraints,menus,robust,frontiers=prices_and_frontiers(data,clocks,pair_cache)
            scaling=training_scaling(data,acquisition,cells,contrasts)
            summary=summary_report(data,cells,contrasts,menus,robust,frontiers,models,budgets,processes,research)
            summary["full_menu_sample_pair_signs_by_cohort"]={str(n):dict(Counter(r["sign"] for r in pairs if r["states"]==n)) for n in (64,32)}
            summary["all_price_pair_constraints"]=len(constraints)
            publish_tables(outputs,data,acquisition,budgets,models,processes,clock_rows,cells,state_rows,pairs,
                           contrasts,costs,constraints,menus,robust,frontiers,scaling,research,stages,summary)
        inputs.immutable()
        require(file_identity(source_path)==report_identity,"Read-only reporter source unchanged during execution")
        forbidden={"numpy","scipy","investment94","continuum94","kernel108","models121","labels121","exact121"}
        require(not forbidden.intersection(sys.modules),"No scientific or production module imported")
        write_json(out/"INPUTS_REPORT121.json",dict(source=data["source"],files=[inputs.entries[k] for k in sorted(inputs.entries)],
            scientific_records_read_from_evidence_root=str(inputs.evidence),source_files_read_from_revision=str(inputs.revision),
            metadata_is_actual_local_custody_not_a_stable_scientific_table=True,
            source_and_M_D_git_byte_bindings_checked=True,
            large_manifest_payloads_verified_once_and_end_metadata_checked=True))
        excluded=["START_REPORT121.json","INPUTS_REPORT121.json","RESEARCH_LEDGER121.json","EXECUTION_REPORT121.json","OUTPUT_MANIFEST121.json"]
        manifest=dict(kind="r121-read-only-reporting-output",source=data["source"],reporting_source_sha256=report_identity["sha256"],
            stable_replay_files=[dict(path=name,**file_identity(out/name)) for name in sorted(outputs.stable)],
            stable_replay_scope="Every listed exact numerical table and generated TeX or table-scope text; no solver, entropy or timing rerun",
            explicitly_excluded_from_stable_equality=excluded,
            exclusion_reason="Actual execution clocks, absolute remapping, custody metadata and evolving publication/support ledger are distinct from deterministic scientific summaries",
            all_output_paths_new_and_exclusive=True)
        write_json(out/"OUTPUT_MANIFEST121.json",manifest)
        result=dict(status="executed",exit_code=0,kind=start["kind"],source=data["source"],
            reporting_source_sha256=report_identity["sha256"],started_unix=start_wall,ended_unix=time.time(),
            total_seconds=time.perf_counter()-clock,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            counts=dict(COUNTS),stable_replay_files=len(outputs.stable),
            output_manifest_sha256=sha256(out/"OUTPUT_MANIFEST121.json"),
            input_manifest_sha256=sha256(out/"INPUTS_REPORT121.json"),
            original_economic_evaluations=0,training_solver_invocations=0,new_state_draws=0,timing_repeats=0,
            source_and_scientific_record_mutations=0,all_partial_outputs_retained=True)
        write_json(out/"EXECUTION_REPORT121.json",result)
        print(json.dumps(encoded({k:result[k] for k in ("status","kind","counts","stable_replay_files","total_seconds")}),sort_keys=True),flush=True)
        return 0
    except BaseException:
        append_jsonl(out/"FAILED_REPORT121.jsonl",dict(status="failed",started_unix=start_wall,ended_unix=time.time(),
            elapsed_seconds=time.perf_counter()-clock,exception=traceback.format_exc(),
            reporting_source_sha256=report_identity["sha256"],counts=dict(COUNTS),
            all_partial_outputs_retained=True,no_automatic_retry_or_scientific_rerun=True))
        raise


if __name__=="__main__":raise SystemExit(main())
