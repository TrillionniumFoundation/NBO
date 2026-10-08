#!/usr/bin/env python3
"""Deterministic threshold audit for the purported NBO R50 revision.

Run from a Git checkout containing the inspected commits. The script verifies
that R50 is one workflow-only commit on top of the R49 review commit, that the
root README still designates R48 as authoritative, and that no R50 manuscript
package exists. It does not evaluate scientific claims absent from the branch.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from typing import Any

REPO = "TrillionniumFoundation/NBO"
R50 = "25295d60f3083ad82b8ec4d1587561ea7985e951"
R50_TREE = "81f8266103617786b55a21942997b7c067c83530"
R49_REVIEW = "4708450610c38e6b8963670cecadc887508c85c0"
R49_SOURCE = "4ede6077aa3d78aa36ec9b9471e5338a636a49f4"
ONLY_PATH = ".github/workflows/nbo-r50-inputs.yml"


def run(*args: str, cwd: pathlib.Path) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".", help="Path to the Git checkout")
    parser.add_argument("--write", help="Optional JSON output path")
    ns = parser.parse_args()
    root = pathlib.Path(ns.repo).resolve()

    if not (root / ".git").exists():
        raise SystemExit(f"Not a Git checkout: {root}")

    # Ensure the inspected objects are locally available.
    for sha in (R50, R49_REVIEW, R49_SOURCE):
        run("cat-file", "-e", f"{sha}^{{commit}}", cwd=root)

    tree = run("show", "-s", "--format=%T", R50, cwd=root)
    parent = run("show", "-s", "--format=%P", R50, cwd=root)
    message = run("show", "-s", "--format=%s", R50, cwd=root)
    changed = run("diff", "--name-status", R49_REVIEW, R50, cwd=root).splitlines()
    changed = [line for line in changed if line.strip()]

    readme = run("show", f"{R50}:README.md", cwd=root)
    files = run("ls-tree", "-r", "--name-only", R50, cwd=root).splitlines()
    file_set = set(files)

    r50_prefix = "revisions/2026-10-08-r50/"
    r50_files = sorted(path for path in files if path.startswith(r50_prefix))
    expected_absences = [
        "revisions/2026-10-08-r50/ECTA.tex",
        "revisions/2026-10-08-r50/supp.tex",
        "revisions/2026-10-08-r50/response.md",
        "revisions/2026-10-08-r50/build/ECTA.pdf",
        "revisions/2026-10-08-r50/audit/RELEASE_AUDIT.json",
        "revisions/2026-10-08-r50/audit/FINAL_DELIVERY.json",
    ]

    checks: dict[str, Any] = {
        "r50_tree_matches": tree == R50_TREE,
        "r50_parent_is_r49_review": parent == R49_REVIEW,
        "commit_message_declares_no_prior_file_changes": (
            message
            == "R50: pin referee and export ordinary revision inputs without changing prior files"
        ),
        "one_changed_path": len(changed) == 1,
        "only_change_is_added_input_workflow": changed == [f"A\t{ONLY_PATH}"],
        "workflow_present": ONLY_PATH in file_set,
        "root_readme_designates_r48": "Authoritative referee revision: R48" in readme,
        "root_readme_points_to_r48_review_ready": (
            "revision/econometrica-nbo-r48-review-ready-2026-10-08" in readme
        ),
        "no_r50_manuscript_directory": not r50_files,
        "required_r50_submission_files_absent": all(
            path not in file_set for path in expected_absences
        ),
    }

    result: dict[str, Any] = {
        "status": "passed" if all(checks.values()) else "failed",
        "repository": REPO,
        "inspected": {
            "r50_commit": R50,
            "r50_tree": tree,
            "parent": parent,
            "parent_role": "R49 Econometrica numerical-methods review commit",
            "latest_substantive_source": R49_SOURCE,
        },
        "diff": {
            "base": R49_REVIEW,
            "head": R50,
            "changed_paths": changed,
            "changed_path_count": len(changed),
        },
        "checks": checks,
        "r50_files": r50_files,
        "interpretation": (
            "The R50 branch is an input-snapshot preparation branch, not a new "
            "manuscript revision. No substantive R50 paper claims were available "
            "for referee evaluation."
        ),
    }

    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if ns.write:
        pathlib.Path(ns.write).write_text(encoded, encoding="utf-8")
    sys.stdout.write(encoded)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
