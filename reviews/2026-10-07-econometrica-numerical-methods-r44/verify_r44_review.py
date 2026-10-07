#!/usr/bin/env python3
"""Deterministic audit for the R44 Econometrica numerical-methods review."""
from __future__ import annotations
import argparse, hashlib, itertools, json, statistics
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

COMMIT="e00d3d46484029738884119f18ce1e15fbdcc929"
TREE="28d2c344da8875eefbf2e6e6f5d27c77c33ef999"
ARTIFACT="5e80020a7a737fcb970e5e2c05ef8c7ad8fd103b524b4cf2ebe6110df9dacff9"
BLOBS={"ECTA.tex":"724c6e74f8a5b7500875f46b9982dc90b52166ad","supp.tex":"e3d5a6834897929e4646600261d8d5ef4c213db8","response.md":"5c31016c623e6d070b6db8546301c1eafe2918c7"}
IDS=(41,89,120,124,128,145,147)

def load(p): return json.loads(Path(p).read_text())
def sha256(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def blob(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()

def theorem_spot_check():
    beta=F(3,4); states=range(3); actions=range(2); T=3
    f=[[F(5*t-2*x+1,7) for x in states] for t in range(T+1)]
    g=[F(3*x-2,5) for x in states]
    c=[[[F(2*t+3*x+a-4,8) for a in actions] for x in states] for t in range(T)]
    pol=[[(t+x)%2 for x in states] for t in range(T)]
    def q(t,x,a,v):
        y0=(x+a)%3; y1=(x+2*a+1)%3
        return c[t][x][a]+beta*(v[y0]+v[y1])/2
    lo=[]; hi=[]; eta=[]
    for t in range(T):
        qs=[[q(t,x,a,f[t+1]) for a in actions] for x in states]
        r=[f[t][x]-min(qs[x]) for x in states]
        lo.append(min(r)); hi.append(max(r))
        eta.append(max(qs[x][pol[t][x]]-min(qs[x]) for x in states))
    rt=[f[T][x]-g[x] for x in states]; lo.append(min(rt)); hi.append(max(rt))
    opt=g[:]; cand=g[:]
    for t in reversed(range(T)):
        opt=[min(q(t,x,a,opt) for a in actions) for x in states]
        cand=[q(t,x,pol[t][x],cand) for x in states]
    cert=sum(beta**t*(hi[t]-lo[t]+eta[t]) for t in range(T))+beta**T*(hi[T]-lo[T])
    assert max(cand[x]-opt[x] for x in states)<=cert
    shifts=[F(2*t-3,5) for t in range(T+1)]
    assert all((hi[t]+shifts[t]-beta*shifts[t+1])-(lo[t]+shifts[t]-beta*shifts[t+1])==hi[t]-lo[t] for t in range(T))
    return {"exact":True,"maximum_gap":float(max(cand[x]-opt[x] for x in states)),"certificate":float(cert),"shift_width_invariance":True}

def paired_spot_check():
    beta=F(3,4); T=3; fit=[[F(t+x,7) for x in range(2)] for t in range(T+1)]
    def cost(x,a): return F(2*x+a,5)
    def terminal(x): return F(3*x,4)
    scores=[]; costs=[]
    for shocks in itertools.product((0,1),repeat=T):
        ss=[]; cc=[]
        for policy in (0,1):
            x=0; z=fit[0][x]; j=F()
            for t,e in enumerate(shocks):
                a=policy; q=cost(x,a)+beta*sum(fit[t+1][(x+a+u)%2] for u in (0,1))/2
                z+=beta**t*(q-fit[t][x]); j+=beta**t*cost(x,a); x=(x+a+e)%2
            z+=beta**T*(terminal(x)-fit[T][x]); j+=beta**T*terminal(x)
            ss.append(z); cc.append(j)
        scores.append(ss[0]-ss[1]); costs.append(cc[0]-cc[1])
    assert sum(scores)==sum(costs)
    return {"exact":True,"trajectories":len(scores),"mean_difference":float(sum(scores)/len(scores))}

def audit(root:Path, artifact:Path|None):
    root=root.resolve(); ev=root/"evidence/2026-10-07-r42"; pub=ev/"results/publication"
    assert {k:blob(root/k) for k in BLOBS}==BLOBS
    if artifact: assert sha256(artifact)==ARTIFACT
    idx=load(pub/"INDEX.json"); assert idx["executed"]==idx["fixed_catalogue_size"]==150 and idx["software_failures"]==0
    methods=Counter(); source_hashes={}
    for i in range(150):
        d=pub/f"service-{i:03d}"; raw=(d/"record.json").read_bytes(); clk=load(d/"clock.json")
        assert hashlib.sha256(raw).hexdigest()==clk["record_sha256"]
        rec=json.loads(raw); methods[rec.get("method",rec.get("selected_method"))]+=1
        for name,h in clk["source_sha256"].items():
            if name in source_hashes: assert source_hashes[name]==h
            source_hashes[name]=h
    assert len(source_hashes)==5
    rec=[]
    for i in IDS:
        r=load(root/f"results/recertify-{i:03d}.json")
        assert r["networks_unchanged"] and r["deployed_actor_unchanged"] and r["retained_policy_bound"]<=r["target"]
        rec.append(r)
    scalar_work=sum(r["verification_work"].get("bellman_transition_evaluations",0) for r in rec)
    coupled=next(r for r in rec if r["service_id"]==128)
    pairs=[]
    for p in sorted((root/"results").glob("paired-[0-9]-[0-9].json")):
        r=load(p); assert r["confidence_lower"]<=0<=r["confidence_upper"] and r["sign"]=="unresolved"
        assert r["ambiguous_actions_neural"]+r["ambiguous_actions_ridge"]==0
        pairs.append(r)
    assert len(pairs)==24
    widths=[r["confidence_upper"]-r["confidence_lower"] for r in pairs]
    means=[sum(r["direct_cost_sample_mean_enclosure"])/2 for r in pairs]
    s=load(root/"audit/PUBLICATION_SUMMARY.json"); rel=load(root/"audit/RELEASE_AUDIT.json")
    assert s["paired_unresolved"]==24 and s["recertified_unchanged_policies"]==7
    comp={x["document"]:x for x in rel["compilation"]}
    return {
      "status":"passed",
      "reviewed_snapshot":{"branch":"revision/econometrica-nbo-r44-review-ready-2026-10-07","commit":COMMIT,"tree":TREE,"publication_artifact_sha256":ARTIFACT},
      "source_identity":{"git_blob_sha1":BLOBS,"original_records_verified":150,"original_source_hashes_verified":5,"method_counts":dict(sorted(methods.items()))},
      "recertification":{"objects":7,"all_networks_and_actors_unchanged":True,"all_targets_attained":True,"relative_bound_reduction_range":[min(1-r["retained_policy_bound"]/r["original_bound"] for r in rec),max(1-r["retained_policy_bound"]/r["original_bound"] for r in rec)],"scalar_additional_bellman_transition_evaluations":scalar_work,"coupled_state_nodes":coupled["verification_work"]["state_nodes"],"coupled_transient_actor_scalars":coupled["transient_fine_actor_scalars_discarded"],"coupled_additional_neuron_expectations":coupled["verification_work"]["neural_neuron_expectations"]},
      "paired_policy_costs":{"comparisons":24,"unresolved":24,"ambiguous_action_selections":0,"interval_width_range":[min(widths),max(widths)],"interval_width_median":statistics.median(widths),"sample_mean_range":[min(means),max(means)],"sample_mean_signs":{"negative":sum(x<0 for x in means),"positive":sum(x>0 for x in means)},"smallest_symmetric_margin_containing_all_reported_intervals":max(max(abs(r["confidence_lower"]),abs(r["confidence_upper"])) for r in pairs)},
      "precision":{"fixed32_certified":s["precision"]["fixed32-cached"]["certified"],"fixed64_certified":s["precision"]["fixed64-cached"]["certified"],"adaptive_certified":s["precision"]["adaptive-cached"]["certified"],"adaptive_rejected_binary32":s["precision"]["adaptive-cached"]["rejected32"],"adaptive_faster_pairs":s["adaptive_faster"],"adaptive_slower_pairs":s["adaptive_slower"],"adaptive_aggregate_time_percent_change_vs_fixed64":s["adaptive_aggregate_percent"]},
      "compilation":{k:{"pages":v["pages"],"undefined_references":len(v["undefined_references"]),"duplicate_labels":v["duplicate_labels"],"overfull_boxes":v["overfull_boxes"]} for k,v in comp.items()},
      "independent_mathematical_spot_checks":{"centered_policy_theorem":theorem_spot_check(),"paired_telescoping":paired_spot_check()},
      "scope":["Frozen-record audit; training and full diagnostics were not rerun.","Recertification was selected after R42 failures and does not alter original capped attainment.","Paired intervals condition on frozen policies and the stipulated iid innovation-bin model.","Singleton and cross-host clocks support no hardware-general claim."]}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--root",type=Path,required=True); p.add_argument("--artifact-zip",type=Path); p.add_argument("--output",type=Path); a=p.parse_args()
    text=json.dumps(audit(a.root,a.artifact_zip),indent=2,sort_keys=True)+"\n"
    if a.output:a.output.write_text(text)
    print(text,end="")
if __name__=="__main__": main()
