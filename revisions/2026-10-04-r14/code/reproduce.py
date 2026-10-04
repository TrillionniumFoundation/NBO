"""Materialize R14 from the exact retained evidence; no policy training.

This executes the dependency order and stops on the first failed gate. The
pre-finalization ledger closes before finalize.py hashes the publication.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from provenance import PUBLICATION_RELATIVE, digest, git, write_json


def commands(repo, verify_only=False, strict=False):
    r = PUBLICATION_RELATIVE
    c = r / "code"
    py = sys.executable
    def command(script, *args):
        return [py, str(c / script), *map(str, args)]
    plan = json.loads((repo / r / "REVISION_PLAN.json").read_text())
    sensor = plan["sensor_diagnostic"]
    weights = [Path("revisions/2026-10-04-r13/results") /
               f"ubuntu24_d{d}_s{sensor['training_seed']}" /
               f"nbo_d{d}_s{sensor['training_seed']}_fixed_nbo_k{sensor['checkpoint_iteration']}.pt"
               for d in sensor["dimensions"]]
    steps = [
        ("restore", command("restore_artifacts.py", *(["--verify-only"] if verify_only else []))),
        ("primary", command("report_primary.py", "--repo-root", ".")),
        ("extension", command("report_extension.py", "--repo", ".",
                              "--out", r, "--primary-audit", r / "results/AUDIT.json")),
        ("reference", command("reference_diagnostics.py", "--repo", ".",
                              "--reference-dir", "revisions/2026-10-04-r12/results/reference",
                              "--output-dir", r / "results/reference")),
        ("sensing", command("sensing_diagnostic.py", "--repo", ".", "--weights", *weights,
                            "--out", r / "results/sensing")),
        ("diagnostic-tables", command("diagnostic_tables.py")),
        ("tests", command("run_tests.py", "--repo-root", ".", "--inherited")),
        ("integrate", command("integrate.py")),
        ("build", command("build.py")),
    ]
    final = command("finalize.py", "--repo-root", ".", "--require-reproduction-ledger",
                    *(["--require-source-checkout"] if strict else []))
    return steps, final


def run(repo, verify_only=False, strict=False, list_only=False):
    repo = Path(repo).resolve()
    r = repo / PUBLICATION_RELATIVE
    steps, final = commands(repo, verify_only, strict)
    if list_only:
        print(json.dumps({"stages": [{"stage": name, "command": args} for name, args in steps],
                          "finalization": final, "new_training": False}, indent=2))
        return
    if strict and not os.environ.get("NBO_R14_SOURCE_COMMIT"):
        raise RuntimeError("NBO_R14_SOURCE_COMMIT is required by the publication-source gate")
    (r / "logs").mkdir(parents=True, exist_ok=True)
    (r / "results").mkdir(exist_ok=True)
    programs = {str(path.relative_to(repo)): digest(path) for path in (r / "code").glob("*.py")}
    reports = []
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    if os.environ.get("NBO_R14_SOURCE_COMMIT", head) != head:
        raise AssertionError("the current checkout is not the declared R14 reporting source")
    versions = {name: importlib.metadata.version(name) for name in ["numpy", "scipy", "numba", "torch", "mpmath"]}
    with tempfile.TemporaryDirectory(prefix="nbo-r14-numba-cache-") as cache:
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", NUMBA_CACHE_DIR=cache,
                           OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                           PYTHONHASHSEED="0")
        for name, command in steps:
            print("R14 stage:", name, flush=True)
            logfile = r / "logs" / ("pipeline-" + name + ".log")
            start = time.perf_counter()
            with logfile.open("w") as stream:
                result = subprocess.run(command, cwd=repo, env=environment,
                                        stdout=stream, stderr=subprocess.STDOUT, timeout=3600)
            reports.append({"stage": name, "command": command, "returncode": result.returncode,
                            "seconds": time.perf_counter() - start,
                            "log": str(logfile.relative_to(repo)), "log_sha256": digest(logfile)})
            ledger = {"reporting_source_commit": os.environ.get("NBO_R14_SOURCE_COMMIT"),
                      "reporting_checkout_commit": head, "program_sha256": programs,
                      "python": platform.python_version(), "dependencies": versions,
                      "stages": reports, "pre_finalization_complete": False,
                      "new_training": False,
                      "scope": "Restore exact studies, replay endpoints, compute prespecified diagnostics, "
                               "run unchanged regression assertions, and compile the materialized publication."}
            write_json(r / "results/REPRODUCTION.json", ledger)
            if result.returncode:
                # No secret-bearing environment or signed download URL is printed.
                print("Failed stage:", name, "; diagnostics retained in", logfile.relative_to(repo), flush=True)
                raise SystemExit(result.returncode)
        ledger["pre_finalization_complete"] = True
        ledger["finalization_record"] = str(PUBLICATION_RELATIVE / "FINAL_AUDIT.json")
        ledger["ledger_closed_before_finalization"] = True
        write_json(r / "results/REPRODUCTION.json", ledger)
        print("R14 stage: finalize", flush=True)
        final_log = r / "logs/pipeline-finalize.log"
        with final_log.open("w") as stream:
            result = subprocess.run(final, cwd=repo, env=environment,
                                    stdout=stream, stderr=subprocess.STDOUT, timeout=3600)
        if result.returncode:
            print("Finalization failed; diagnostics retained in", final_log.relative_to(repo), flush=True)
            raise SystemExit(result.returncode)
        # Do not rewrite the closed reproduction ledger or any hashed output.
        print(final_log.read_text(), end="", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--verify-restored-only", action="store_true")
    parser.add_argument("--require-source-checkout", action="store_true")
    parser.add_argument("--list-steps", action="store_true")
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    run(args.repo_root, args.verify_restored_only, args.require_source_checkout, args.list_steps)
