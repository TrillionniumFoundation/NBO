"""Compile the four native R126 documents without materializing historical code.

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
EPOCH = '1792713600'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--diagnostic", action="store_true")
    ap.add_argument("--passes", type=int, default=4)
    ap.add_argument("--receipt-dir", default="build_receipts126")
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
               "scientific_execution": False, "status": "running"}
    receipt["builder_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    receipt["tool_versions"] = {}
    for tool in ("pdflatex", "bibtex", "pdfinfo"):
        option = "-v" if tool == "pdfinfo" else "--version"
        version = subprocess.run([tool, option], capture_output=True, text=True, check=True)
        receipt["tool_versions"][tool] = (version.stdout + version.stderr).splitlines()[0]
    sources = {}
    for pattern in ("*.tex", "*.bib", "*.cls", "*.bst", "*.sty", "*.cfg"):
        for p in ROOT.rglob(pattern):
            if any(part in {"build", "results122", "verification122", "ci122", "__pycache__", "provenance", "provenance122", "frozen_inputs", "historical_wrappers122"}
                   for part in p.relative_to(ROOT).parts):
                continue
            sources[str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    receipt["source_sha256"] = dict(sorted(sources.items()))
    receipt["graphic_asset_sha256"] = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for folder in ("figures119", "figures120", "figures121", "figures122", "figures125", "figures126")
        for p in sorted((ROOT / folder).rglob("*"))
        if p.is_file() and p.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg", ".eps"}
    }

    def save():
        (out / "BUILD_RECEIPT126.json").write_text(json.dumps(receipt, indent=2) + "\n")

    def run(argv, label):
        start = time.time()
        log = out / (label + ".log")
        row = {"argv": argv, "started_unix": start, "exit_code": None,
               "log": str(log.relative_to(ROOT)), "status": "started"}
        receipt["commands"].append(row)
        save()
        try:
            with log.open("wb") as f:
                p = subprocess.run(argv, cwd=ROOT, env=env, stdout=f,
                                   stderr=subprocess.STDOUT, timeout=600)
            row["exit_code"] = p.returncode
            row["status"] = "passed" if p.returncode == 0 else "failed_exit"
            if p.returncode:
                receipt["status"] = "build_failed"
        except BaseException as error:
            row["status"] = "launch_or_execution_exception"
            row["exception_type"], row["exception"] = type(error).__name__, str(error)
            receipt["status"] = "build_failed"
            raise
        finally:
            row["ended_unix"] = time.time()
            row["elapsed_seconds"] = row["ended_unix"] - start
            row["log_sha256"] = hashlib.sha256(log.read_bytes()).hexdigest() if log.exists() else None
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
    active.extend((ROOT / "new126").glob("*.tex"))
    placeholders = [str(p.relative_to(ROOT)) for p in active
                    if "R126-INTEGRATION-PENDING" in p.read_text(errors="replace")
                    or "PENDING126" in p.read_text(errors="replace")
                    or "RECEIPT-PENDING" in p.read_text(errors="replace")
                    or "prospective manuscript component" in p.read_text(errors="replace")]
    receipt.update({"finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "issues": issues, "placeholders": placeholders,
                    "pdfs": [{"path": "build/" + d + ".pdf",
                              "bytes": (build / (d + ".pdf")).stat().st_size,
                              "sha256": hashlib.sha256((build / (d + ".pdf")).read_bytes()).hexdigest()}
                             for d in DOCUMENTS]})
    receipt["actual_project_inputs"] = {}
    receipt["generated_build_inputs"] = {}
    for doc in DOCUMENTS:
        project, generated = {}, {}
        recorder = (build / (doc + ".fls")).read_text(errors="strict")
        for line in recorder.splitlines():
            if not line.startswith("INPUT "):
                continue
            path = Path(line[6:])
            path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
            if not path.is_file() or not path.is_relative_to(ROOT):
                continue
            relative = path.relative_to(ROOT).as_posix()
            target = generated if relative.startswith("build/") else project
            target[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        receipt["actual_project_inputs"][doc] = dict(sorted(project.items()))
        receipt["generated_build_inputs"][doc] = dict(sorted(generated.items()))
    receipt["input_scope"] = "source_sha256 describes native declared author text dependencies, excluding expanded raw records and replays; actual_project_inputs is the final TeX recorder closure for each document. Generated auxiliary/bibliography files have their own hashes. Tool versions identify the installed system TeX inputs."
    receipt["source_mutations_during_build"] = {}
    for relative, before in {**receipt["source_sha256"], **receipt["graphic_asset_sha256"]}.items():
        path = ROOT / relative
        after = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        if before != after:
            receipt["source_mutations_during_build"][relative] = {"before": before, "after": after}
    for project in receipt["actual_project_inputs"].values():
        for relative, actual in project.items():
            if relative in receipt["source_sha256"] and receipt["source_sha256"][relative] != actual:
                receipt["source_mutations_during_build"][relative] = {
                    "before": receipt["source_sha256"][relative], "actual_recorder_input": actual}
    receipt["status"] = "compiled_with_diagnostics" if issues or placeholders else "compiled_clean"
    if receipt["source_mutations_during_build"]:
        receipt["status"] = "source_changed_during_build"
    save()
    print(json.dumps({"receipt": str(out.relative_to(ROOT)), "status": receipt["status"],
                      "issues": issues, "placeholders": placeholders,
                      "source_mutations": receipt["source_mutations_during_build"]}))
    if receipt["source_mutations_during_build"] or ((issues or placeholders) and not args.diagnostic):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
