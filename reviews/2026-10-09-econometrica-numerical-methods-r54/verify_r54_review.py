#!/usr/bin/env python3
"""Independent standard-library audit of the frozen NBO R54 publication.

The script verifies the source-bound publication artifact and recomputes the
comparisons used in the accompanying referee report. It does not rerun policy
construction, simulation, statistical inference, or timing services.
"""
from __future__ import annotations
import argparse, hashlib, json, math, shutil, tempfile, zipfile
from pathlib import Path

SNAPSHOT = {
    "branch": "revision/econometrica-nbo-r54-review-ready-2026-10-08",
    "commit": "00e837adb431f4d4b5248fc6d5ff1fc927dd3b65",
    "tree": "70fe6bd2584c9026f0f31e9dfd5f3b3a23c1ed86",
    "workflow_run_id": 37811366061,
    "artifact_id": 11565815940,
    "artifact_sha256": "3b74173305dd489f900f4fd3c7dcf2a71a115856fc8ef5368e5867a1d510f9e5",
}

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)

def need(ok: bool, msg: str):
    if not ok:
        raise AssertionError(msg)

def root_at(path: Path) -> Path:
    if (path / "audit" / "RESULT_AUDIT54.json").is_file():
        return path
    q = path / "revisions" / "2026-10-08-r54"
    if (q / "audit" / "RESULT_AUDIT54.json").is_file():
        return q
    raise FileNotFoundError("R54 audit tree not found")

def service(rows, method, T):
    x = [r for r in rows if r["method"] == method and int(r["T"]) == T]
    need(len(x) == 1, f"service identity {method}, T={T}")
    return x[0]

def run(root: Path, artifact: Path | None):
    a = root / "audit"
    result, release = load(a / "RESULT_AUDIT54.json"), load(a / "RELEASE54.json")
    clean, delivery = load(a / "CLEAN_REBUILD54.json"), load(a / "FINAL_DELIVERY54.json")
    for obj, name in ((result,"result"),(release,"release"),(clean,"clean"),(delivery,"delivery")):
        need(obj["status"] == "passed", f"{name} status")
    need(delivery["canonical_branch"] == SNAPSHOT["branch"], "canonical branch")
    need(int(delivery["workflow_run_id"]) == SNAPSHOT["workflow_run_id"], "workflow")
    need(release["total_tests"] == 80, "test count")
    need(result["checked_full_sweep_cell_decisions"] == 38912, "cell decisions")
    need(result["misspecification"]["checked_cell_cases"] == 393216, "misspecification cases")
    if artifact:
        need(digest(artifact) == SNAPSHOT["artifact_sha256"], "artifact digest")

    docs = {}
    expected_docs = {x["document"]: x for x in release["documents"]}
    for name in ("ECTA","supp","complete","complete-supp","response"):
        pdf = root / "build" / f"{name}.pdf"
        need(pdf.is_file(), f"missing {pdf}")
        need(digest(pdf) == expected_docs[name]["sha256"], f"PDF digest {name}")
        docs[name] = {"pages": expected_docs[name]["pages"], "sha256": expected_docs[name]["sha256"]}

    costs = {int(x["T"]): x for x in result["primary_costs"]}
    primary = {}
    for T in (2,3):
        x = costs[T]
        w, f = x["absolute_cost"][f"compiled-witness-pass{T}"], x["absolute_cost"][f"tensor-fvi-pass{T}"]
        cross = x["contrasts"][f"witness-minus-fvi-pass{T}"]
        wg = x["contrasts"][f"compiled-witness-pass{T}-initial-gain"]
        fg = x["contrasts"][f"tensor-fvi-pass{T}-initial-gain"]
        need(wg[0] > 0 and cross[0] <= 0 <= cross[1], f"primary signs T={T}")
        primary[str(T)] = {"witness_final": w, "fvi_final": f, "cross": cross,
                           "witness_gain": wg, "fvi_gain": fg,
                           "witness_upper_excess": w[1]-f[1]}

    directed = {}
    for T in (2,3):
        w, f = service(result["primary"],"compiled-witness",T), service(result["primary"],"tensor-fvi",T)
        wp, fp = w["passes"][-1], f["passes"][-1]
        directed[str(T)] = {
            "witness_gap": wp["gap_upper"], "fvi_gap": fp["gap_upper"],
            "gap_ratio": wp["gap_upper"]/fp["gap_upper"],
            "service_ratio": w["total_service_seconds"]/f["total_service_seconds"],
            "witness_actor_queries": wp["work"]["actor_queries"],
            "fvi_actor_queries": fp["work"]["actor_queries"],
            "witness_pair_nodes": wp["work"]["pair_nodes"],
            "fvi_pair_nodes": fp["work"]["pair_nodes"],
            "witness_ambiguity_rate": wp["work"]["ambiguous_actor_boxes"]/wp["work"]["actor_queries"],
            "fvi_ambiguity_rate": fp["work"]["ambiguous_actor_boxes"]/fp["work"]["actor_queries"],
        }
    need(math.isclose(directed["2"]["gap_ratio"],1.2899681731117587,rel_tol=1e-12),"T2 ratio")
    need(math.isclose(directed["3"]["gap_ratio"],2.4122557198868124,rel_tol=1e-12),"T3 ratio")

    miss = result["misspecification"]
    need(miss["false_null_certified_harmful_cell_cases"] == 116185, "harmful false-null count")
    return {
        "status":"passed", "reviewed_snapshot":SNAPSHOT,
        "documents":docs,
        "release":{"tests":80,"files":delivery["file_count"],"clean_rebuild":clean["status"]},
        "primary_costs":primary, "directed_certificate":directed,
        "catalogue_work":result["actual_cost_catalogues"],
        "misspecification":{
            "cases":miss["cases"], "checked_cell_cases":miss["checked_cell_cases"],
            "harmful_false_null_cell_cases":miss["false_null_certified_harmful_cell_cases"],
            "safe_changed_cell_cases":miss["safe_changed_cell_cases"],
            "maximum_contrast_bound":miss["maximum_contrast_bound"],
            "statistical_observations":miss["statistical_observations"]},
        "scope":["Frozen-record audit only; no scientific reruns.",
                 "Single-host clocks are descriptive, not hardware-general.",
                 "Controlled perturbations are deterministic diagnostics, not population samples."]}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--root",type=Path); p.add_argument("--artifact-zip",type=Path); p.add_argument("--output",type=Path,required=True); x=p.parse_args()
    tmp=None
    try:
        if x.root: root=root_at(x.root.resolve())
        elif x.artifact_zip:
            tmp=Path(tempfile.mkdtemp(prefix="nbo-r54-audit-")); zipfile.ZipFile(x.artifact_zip).extractall(tmp); root=root_at(tmp)
        else: p.error("provide --root or --artifact-zip")
        out=run(root,x.artifact_zip.resolve() if x.artifact_zip else None)
        x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps(out,indent=2,sort_keys=True))
    finally:
        if tmp: shutil.rmtree(tmp,ignore_errors=True)
if __name__ == "__main__": main()
