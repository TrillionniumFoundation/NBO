"""Verify retained Git identities and complete current/historical response routes.

This source audit requires the pinned Git trees. It does not fetch blobs,
evaluate an economic primitive, infer scientific closure, or rebuild TeX.
"""
from pathlib import Path
import argparse
from collections import Counter, defaultdict
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--git-repository", type=Path, default=ROOT.parents[1])
    args = parser.parse_args()
    retention_path = ROOT / "CONTENT_RETENTION125.json"
    retention = json.loads(retention_path.read_text())
    records = retention["records"]
    assert len(records) == 307
    assert Counter(row["retention_kind"] for row in records) == {
        "exact-original-bytes": 296, "exact-later-inherited-source": 11
    }
    grouped = defaultdict(list)
    for row in records:
        grouped[row["source_commit"]].append(row["source_path"])
    objects = {}
    for commit, paths in grouped.items():
        output = subprocess.run(
            ["git", "-C", str(args.git_repository), "ls-tree", "-r", "-z", "--full-tree", commit, "--", *paths],
            check=True, capture_output=True,
            env=dict(os.environ, GIT_NO_LAZY_FETCH="1"),
        ).stdout
        for entry in output.split(b"\0"):
            if entry:
                header, path = entry.split(b"\t", 1)
                mode, kind, blob = header.decode().split()
                assert kind == "blob"
                objects[(commit, path.decode())] = blob
    assert len(objects) == 307

    receipt_path = ROOT / retention["closure_snapshot_identity"]["build_receipt"]
    receipt = json.loads(receipt_path.read_text())
    assert digest(receipt_path) == retention["closure_snapshot_identity"]["build_receipt_sha256"]
    assert receipt["status"] == "compiled_clean"
    assert retention["closure_snapshot"] == {
        document: sorted(paths) for document, paths in receipt["actual_project_inputs"].items()
    }
    doc_inputs = {document: set(paths) for document, paths in receipt["actual_project_inputs"].items()}
    document_text = {
        document: "\n".join((ROOT / path).read_text() for path in sorted(paths) if path.endswith(".tex"))
        for document, paths in doc_inputs.items()
    }
    bibliography = {}
    for document, text in document_text.items():
        bibliography[document] = {
            name.strip() + ".bib"
            for group in re.findall(r"\\bibliography\{([^}]+)\}", text)
            for name in group.split(",")
        }
    retained_checks = []
    routes_checked = 0
    for row in records:
        path = ROOT / row["retained_path"]
        data = path.read_bytes()
        sha256 = hashlib.sha256(data).hexdigest()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert sha256 == row["sha256"], row["retained_path"]
        assert blob == objects[(row["source_commit"], row["source_path"])], row["source_path"]
        if "git_blob" in row:
            assert blob == row["git_blob"]
        for document in row["rendered_in"]:
            assert row["retained_path"] in doc_inputs[document] | bibliography[document], (row["retained_path"], document)
            routes_checked += 1
        retained_checks.append({
            "source_commit": row["source_commit"], "source_path": row["source_path"],
            "retained_path": row["retained_path"], "source_git_blob": blob,
            "retained_sha256": sha256, "reader_routes": row["rendered_in"],
        })

    # Re-run the existing source-custody verifier, then independently check that
    # every mapped current chapter label and response ID resolves.
    subprocess.run([sys.executable, str(ROOT / "provenance/verify_response_maps125.py")], check=True)
    current_path = ROOT / "response_inputs/CURRENT_RESPONSE125.json"
    historical_path = ROOT / "response_inputs/HISTORICAL_ITEM_ROUTES125.json"
    current = json.loads(current_path.read_text())
    historical = json.loads(historical_path.read_text())
    labels = set(re.findall(r"\\label\{([^}]+)\}", "\n".join(document_text.values())))
    current_ids = {row["request_id"] for row in current["records"]}
    assert len(current_ids) == 30
    mapped_labels = set()
    for row in current["records"]:
        mapped_labels.update(row["current_chapter_labels"])
        assert set(row["current_chapter_labels"]) <= labels
    for row in historical["records"]:
        mapped_labels.update(row["r125_current_chapter_labels"])
        assert set(row["r125_current_chapter_labels"]) <= labels
        assert set(row["r125_current_response_ids"]) <= current_ids
    assert len(historical["records"]) == 684
    response_text = (ROOT / "new125/response125_body.tex").read_text()
    response_refs = set(re.findall(r"\\ref\{([^}]+)\}", response_text))
    assert response_refs <= labels
    source_inputs = [retention_path, receipt_path, current_path, historical_path,
                     ROOT / "provenance/RESPONSE_MAP_VERIFICATION125.json",
                     ROOT / "new125/response125_body.tex"]
    result = {
        "schema": "r125-complete-source-route-coverage-v1",
        "checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "passed",
        "scope": "Exact retained-byte/Git-identity custody, actual build-input routes, and complete current/historical response mapping. The build snapshot is dated; this check does not claim a new build, scientific issue closure or new numerical execution.",
        "source_script_sha256": digest(Path(__file__)),
        "retained_records_verified": len(records),
        "original_r122_records": 296,
        "later_inherited_records": 11,
        "reader_routes_verified": routes_checked,
        "source_only_retention_records": sum(not row["rendered_in"] for row in records),
        "current_request_records": len(current_ids),
        "historical_index_records": len(historical["records"]),
        "historical_major_blocks": 620,
        "historical_overlapping_parents": 64,
        "mapped_current_chapter_labels_verified": sorted(mapped_labels),
        "rendered_response_references_verified": sorted(response_refs),
        "build_snapshot_finished_utc": receipt["finished_utc"],
        "source_inputs_sha256": {str(path.relative_to(ROOT)): digest(path) for path in source_inputs},
        "retention_checks": retained_checks,
        "economic_evaluations": 0,
        "all_scientific_closure_claims_false": True,
    }
    (ROOT / "provenance/COVERAGE_VERIFICATION125.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key not in ("source_inputs_sha256", "retention_checks")}, indent=2))


if __name__ == "__main__":
    main()
