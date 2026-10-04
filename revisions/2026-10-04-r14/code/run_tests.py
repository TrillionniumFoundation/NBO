"""Run current regressions and unchanged historical suites without root swaps.

Historical suites run on an isolated export of the exact R11 evidence commit.
This validates the suites in their declared manuscript view, including README.
The R14 current-tree preservation check is deliberately a separate operation.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import math
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
from pathlib import Path

from provenance import (
    HISTORICAL_TEST_SOURCE, PRIMARY_RELATIVE, PUBLICATION_RELATIVE,
    digest, git, pinned_sha256, check_files, write_json,
)


def current_tests(repo: Path, output: Path) -> dict:
    code = repo / PRIMARY_RELATIVE / "code"
    sys.path.insert(0, str(code))
    import common
    if Path(common.__file__).resolve() != (code / "common.py").resolve():
        raise AssertionError("wrong current common module")
    sys.path.insert(0, str(code))
    import test_r12
    import test_extra
    # This is the same missing module-global name supplied by the original
    # test_runner; neither an assertion nor a test function is changed.
    test_r12.math = math
    suite = unittest.TestSuite([
        unittest.defaultTestLoader.loadTestsFromModule(test_r12),
        unittest.defaultTestLoader.loadTestsFromModule(test_extra),
    ])
    start = time.perf_counter()
    with (output / "logs/current-tests.log").open("w") as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    record = {
        "tests": result.testsRun, "failures": len(result.failures),
        "errors": len(result.errors), "success": result.wasSuccessful(),
        "elapsed_seconds": time.perf_counter() - start,
        "scope": "Unchanged R12 regression assertions, run without its result-writing wrapper.",
        "scripts_sha256": {str(Path(module.__file__).relative_to(repo)): digest(Path(module.__file__))
                           for module in [test_r12, test_extra]},
    }
    write_json(output / "results/TESTS.json", record)
    if not result.wasSuccessful():
        raise RuntimeError("current regression suite failed; see current-tests.log")
    return record


def export_git_tree(repo: Path, commit: str, target: Path) -> None:
    """Export an immutable tree, never symlink historical tests to live data."""
    process = subprocess.Popen(["git", "archive", "--format=tar", commit],
                               cwd=repo, stdout=subprocess.PIPE)
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
            for member in archive:
                # Git repository paths are trusted source paths, but enforce
                # containment for robustness of the isolated exporter.
                destination = (target / member.name).resolve()
                if not destination.is_relative_to(target.resolve()):
                    raise AssertionError("archive path escapes test workspace")
                if member.issym() or member.islnk():
                    raise AssertionError("unexpected symlink in historical test export")
                archive.extract(member, target, filter="data")
    finally:
        process.stdout.close()
        returncode = process.wait()
    if returncode:
        raise RuntimeError("historical Git export failed")


def inherited_tests(repo: Path, output: Path) -> dict:
    reports = []
    scripts = ["replay_inherited.py", "test_r11.py", "test_initial_state_inputs.py"]
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    start = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="nbo-r14-historical-") as directory:
        view = Path(directory)
        export_git_tree(repo, HISTORICAL_TEST_SOURCE, view)
        roots = {name: digest(view / name) for name in ["ECTA.tex", "supp.tex", "revision_reference.bib", "README.md"]}
        # The source commit is the recorded evidence tree. Its README is the
        # original README required by the historical R8 preservation manifest.
        for name in scripts:
            logfile = output / "logs" / ("inherited-" + name + ".log")
            with logfile.open("w") as stream:
                result = subprocess.run(
                    [sys.executable, str(view / "revisions/2026-10-04-r11/code" / name)],
                    cwd=view, env=environment, stdout=stream, stderr=subprocess.STDOUT,
                    timeout=1200,
                )
            text = logfile.read_text(errors="replace")
            reports.append({"script": name, "returncode": result.returncode,
                            "tests": sum(map(int, re.findall(r"Ran (\d+) tests?", text)))})
            if result.returncode:
                record = {"success": False, "reports": reports,
                          "tested_source_commit": HISTORICAL_TEST_SOURCE,
                          "isolated_historical_roots": roots}
                write_json(output / "results/INHERITED_TESTS.json", record)
                raise RuntimeError("unchanged historical suite failed: " + name)
        detail = json.loads((view / "revisions/2026-10-04-r11/results/INHERITED_TESTS.json").read_text())
        if not detail["history_unchanged"]:
            raise AssertionError("historical numerical inputs changed inside isolated replay")
    record = {
        "success": True, "tests": sum(item["tests"] for item in reports),
        "reports": reports, "historical_details": detail,
        "tested_source_commit": HISTORICAL_TEST_SOURCE,
        "isolated_historical_roots": roots,
        "elapsed_seconds": time.perf_counter() - start,
        "current_roots_modified": False,
        "historical_assertions_modified": False,
        "scope": "Historical numerical/layout suites on their exact evidence tree. "
                 "R14 current-tree preservation and current manuscript compilation are separate gates.",
    }
    write_json(output / "results/INHERITED_TESTS.json", record)
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--inherited", action="store_true")
    parser.add_argument("--output", type=Path, help="defaults to the R14 publication directory")
    arguments = parser.parse_args()
    sys.dont_write_bytecode = True
    repo = arguments.repo_root.resolve()
    output = (arguments.output or (repo / PUBLICATION_RELATIVE)).resolve()
    (output / "logs").mkdir(parents=True, exist_ok=True)
    (output / "results").mkdir(exist_ok=True)
    records = {"current": current_tests(repo, output)}
    if arguments.inherited:
        records["inherited"] = inherited_tests(repo, output)
    print(json.dumps(records, indent=2))
