#!/usr/bin/env python3
"""Independent standard-library audit of the committed NBO R65 records.

This verifies frozen records and arithmetic. It does not rerun fitting,
Bellman services, policy evaluation, LaTeX, or timing experiments.
"""
from __future__ import annotations
import argparse, hashlib, json, statistics
from collections import Counter, defaultdict
from pathlib import Path

BRANCH="revision/econometrica-nbo-r65-review-ready-2026-10-10"
COMMIT="34a5ce17dc3ac4681b6d004eca00637f28104e28"
TREE="0e3572437c8edad55ca123545477c5593c917f6d"
ARTIFACT="2c139fc5f139e37deabd7a0f6ca7adea9699d41db059f24950d74f42fddd1cd7"
BLOBS={"ECTA.tex":"2d2570456c2a7e2ae5d038489dcba3116cdde2bb",
       "supp.tex":"b777d6b74a4f078f065f3eecf473a88de5a80721",
       "response.md":"aee7d72fc496972429d30975c9d74f78a0bf7e40"}

def read(p): return json.loads(p.read_text())
def git_blob(p):
    b=p.read_bytes(); return hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()
def sha256(p):
    h=hashlib.sha256();
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()
def signs(xs):
    c=Counter("lower" if x<0 else "higher" if x>0 else "equal" for x in xs)
    return {k:c[k] for k in ("lower","equal","higher")}
def stats(xs):
    xs=list(xs); return {"count":len(xs),"min":min(xs),"median":statistics.median(xs),
                          "mean":sum(xs)/len(xs),"max":max(xs)} if xs else {"count":0}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--root",type=Path,default=Path("."))
    ap.add_argument("--audit-root",type=Path); ap.add_argument("--artifact",type=Path)
    ap.add_argument("--skip-source-files",action="store_true"); ap.add_argument("--output",type=Path)
    a=ap.parse_args(); root=a.root.resolve(); rev=root/"revisions/2026-10-10-r65"
    au=a.audit_root.resolve() if a.audit_root else rev/"audit"
    A=read(au/"ANALYSIS65.json"); R=read(au/"RESULT_AUDIT65.json")
    F=read(au/"FINAL_DELIVERY65.json"); L=read(au/"RELEASE65.json")
    C=read(au/"CLEAN_REBUILD65.json"); T=read(au/"TESTS65.json")
    if a.skip_source_files: blob_check="pinned from GitHub API"
    else:
        got={n:git_blob(rev/n) for n in BLOBS}; assert got==BLOBS; blob_check="verified"
    assert F["canonical_branch"]==BRANCH and F["checked_services"]==256
    assert F["checked_policy_decisions"]==55296 and F["requeried_distinct_decisions"]==27648
    assert T["total"]==63 and all(v["pdf_bytes_equal"] and v["text_equal"] and v["pages_equal"] for v in C["document_checks"].values())
    r63,r64=R["R63"]["rows"],R["R64"]["rows"]; assert (len(r63),len(r64))==(96,160)
    assert R["summary"]["returned_services"]==256 and R["summary"]["rational_fallbacks"]==0
    groups=defaultdict(list)
    for r in r64: groups[(r["d"],r["T"],r["target"],r["mode"])].append(r)
    cells=sorted({(r["d"],r["T"],r["target"]) for r in r64}); winners=[]
    modes=sorted({r["mode"] for r in r64})
    for cell in cells:
        m={z:statistics.median(x["wall"] for x in groups[cell+(z,)]) for z in modes}
        winners.append({"cell":cell,"winner":min(m,key=m.get),"medians":m})
    distinct={}
    for r in r64: distinct.setdefault((r["d"],r["T"],r["target"],r["seed"],r["mode"]),r)
    qdiff=[]; wdiff=[]
    for d,h,t,s in sorted({k[:4] for k in distinct if k[4]=="relu-route"}):
        rr=distinct[(d,h,t,s,"relu-route")]; qr=distinct[(d,h,t,s,"quadratic-route")]
        qdiff.append(rr["counts"]["q_queries"]-qr["counts"]["q_queries"])
        rw=[x["wall"] for x in r64 if (x["d"],x["T"],x["target"],x["seed"],x["mode"])==(d,h,t,s,"relu-route")]
        qw=[x["wall"] for x in r64 if (x["d"],x["T"],x["target"],x["seed"],x["mode"])==(d,h,t,s,"quadratic-route")]
        wdiff.append(statistics.median(rw)-statistics.median(qw))
    cell_repr=[]
    for cell in cells:
        rm=statistics.median(x["wall"] for x in groups[cell+("relu-route",)])
        qm=statistics.median(x["wall"] for x in groups[cell+("quadratic-route",)])
        cell_repr.append({"cell":cell,"relu":rm,"quadratic":qm,"winner":"relu" if rm<qm else "quadratic"})
    amort={}
    for model in ("relu","quadratic"):
        vals=[]; no=0
        for r in A["comparisons"][model]["rows"]:
            saving=-r["query_difference_from_adaptive"]
            if saving>0: vals.append(r["training_queries"]/saving)
            else: no+=1
        amort[model]={"finite_repeated_workloads":stats(vals),"no_positive_saving":no,
                      "scope":"training queries / deployment-query saving; costs not assumed equal"}
    warns=Counter(); services=Counter()
    for r in r64: warns[r["mode"]]+=r["fit_warnings"]; services[r["mode"]]+=1
    artifact={"provided":bool(a.artifact)}
    if a.artifact:
        d=sha256(a.artifact); assert d==ARTIFACT; artifact|={"sha256":d,"matches":True}
    out={"status":"passed","snapshot":{"branch":BRANCH,"commit":COMMIT,"tree":TREE,"blobs":BLOBS,"blob_check":blob_check},
         "artifact":artifact,"publication":{"workflow":F["workflow_run_id"],"services":256,"decisions":55296,
         "requeried":27648,"tests":T,"pages":{d["document"]:d["pages"] for d in L["documents"]},
         "clean_rebuild":True,"new_training_runs":0,"new_continuous_law_observations":0},
         "catalogue":{"R63":96,"R64":160,"warnings":A["R63_fit_warnings"]+A["R64_fit_warnings"],
         "R64_warnings_by_mode":dict(warns),"R64_services_by_mode":dict(services),"fallbacks":0,
         "max_batch":A["maximum_batch"],"max_rss_kib":A["maximum_rss_kib"],"worst_seconds":A["worst_process_seconds"]},
         "cold_start":{"cells":winners,"winner_counts":dict(Counter(x["winner"] for x in winners)),"learned_wins":0},
         "queries":{"relu_route_vs_insert":A["comparisons"]["relu"]["query_difference_from_insert"],
         "quadratic_route_vs_insert":A["comparisons"]["quadratic"]["query_difference_from_insert"],
         "relu_route_vs_adaptive":A["comparisons"]["relu"]["query_difference_from_adaptive"],
         "quadratic_route_vs_adaptive":A["comparisons"]["quadratic"]["query_difference_from_adaptive"],
         "relu_minus_quadratic":signs(qdiff),"relu_minus_quadratic_clock_medians":signs(wdiff),
         "representation_cell_medians":cell_repr},"amortization_diagnostic":amort,
         "scope":["Frozen-record audit only; no scientific service or clock rerun.",
         "Repeat-identical traces are not independent numerical transcripts.",
         "Dyadic workload means are not new continuous-law policy-value observations."]}
    text=json.dumps(out,indent=2,sort_keys=True)+"\n"
    if a.output: a.output.write_text(text)
    else: print(text,end="")
if __name__=="__main__": main()
