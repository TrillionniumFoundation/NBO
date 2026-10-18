"""Compile the four native R119 documents without materializing historical code.

Actual build receipts are separate from scientific execution receipts.  This
builder never runs an experiment, regenerates a table, or changes a source.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parent
DOCUMENTS = ("ECTA", "supp", "appendix", "RESPONSE_TO_REFEREE")
EPOCH = "1792281600"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--diagnostic", action="store_true")
    ap.add_argument("--passes", type=int, default=4)
    ap.add_argument("--receipt-dir", default="build_receipts119")
    args = ap.parse_args()
    assert 2 <= args.passes <= 8
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    out = ROOT / args.receipt_dir / stamp
    out.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ, SOURCE_DATE_EPOCH=EPOCH, FORCE_SOURCE_DATE="1")
    receipt = {"started_utc": stamp, "source_date_epoch": EPOCH,
               "diagnostic": args.diagnostic, "commands": [],
               "scientific_execution": False}
    receipt["builder_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    receipt["tool_versions"] = {}
    for tool in ("pdflatex", "bibtex", "pdfinfo"):
        option = "-v" if tool == "pdfinfo" else "--version"
        version = subprocess.run([tool, option], capture_output=True, text=True, check=True)
        receipt["tool_versions"][tool] = (version.stdout + version.stderr).splitlines()[0]
    sources = {}
    for pattern in ("*.tex", "*.bib", "*.cls", "*.bst", "*.sty", "*.cfg"):
        for p in ROOT.rglob(pattern):
            if "build" in p.relative_to(ROOT).parts:
                continue
            sources[str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    receipt["source_sha256"] = dict(sorted(sources.items()))
    receipt["graphic_asset_sha256"] = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((ROOT / "figures119").rglob("*"))
        if p.is_file() and p.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg", ".eps"}
    }

    def save():
        (out / "BUILD_RECEIPT119.json").write_text(json.dumps(receipt, indent=2) + "\n")

    def run(argv, label):
        start = time.time()
        log = out / (label + ".log")
        with log.open("wb") as f:
            p = subprocess.run(argv, cwd=ROOT, env=env, stdout=f,
                               stderr=subprocess.STDOUT, timeout=600)
        row = {"argv": argv, "started_unix": start,
               "elapsed_seconds": time.time() - start, "exit_code": p.returncode,
               "log": str(log.relative_to(ROOT)),
               "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest()}
        receipt["commands"].append(row)
        save()
        print(json.dumps({"stage": label, "exit_code": p.returncode,
                          "seconds": row["elapsed_seconds"]}), flush=True)
        if p.returncode:
            print(log.read_text(errors="replace")[-5000:])
            raise SystemExit(p.returncode)

    for iteration in range(args.passes):
        for doc in DOCUMENTS:
            run(["pdflatex", "-halt-on-error", "-interaction=nonstopmode",
                 "-file-line-error", "-recorder", "-output-directory=build",
                 doc + ".tex"], f"{iteration + 1:02d}-{doc}")
        if iteration == 0:
            for doc in DOCUMENTS:
                aux = (build / (doc + ".aux")).read_text(errors="replace")
                if "\\bibdata" in aux:
                    run(["bibtex", "build/" + doc], "bibtex-" + doc)
    issues = {}
    for doc in DOCUMENTS:
        log = (build / (doc + ".log")).read_text(errors="replace")
        hits = re.findall(r"^.*(?:Overfull \\[hv]box|undefined references|undefined citations|"
                          r"multiply-defined labels|Rerun to get|Citation .* undefined|"
                          r"Reference .* undefined).*$", log, re.M)
        if hits:
            issues[doc] = hits
    active = [ROOT / (d + ".tex") for d in DOCUMENTS]
    active.extend((ROOT / "new119").glob("*.tex"))
    placeholders = [str(p.relative_to(ROOT)) for p in active
                    if "R119-INTEGRATION-PENDING" in p.read_text(errors="replace")
                    or "RECEIPT-PENDING" in p.read_text(errors="replace")]
    receipt.update({"finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "issues": issues, "placeholders": placeholders,
                    "pdfs": [{"path": "build/" + d + ".pdf",
                              "bytes": (build / (d + ".pdf")).stat().st_size,
                              "sha256": hashlib.sha256((build / (d + ".pdf")).read_bytes()).hexdigest()}
                             for d in DOCUMENTS]})
    receipt["status"] = "compiled_with_diagnostics" if issues or placeholders else "compiled_clean"
    save()
    print(json.dumps({"receipt": str(out.relative_to(ROOT)), "status": receipt["status"],
                      "issues": issues, "placeholders": placeholders}))
    if (issues or placeholders) and not args.diagnostic:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
