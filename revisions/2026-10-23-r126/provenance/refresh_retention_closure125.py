"""Refresh recorder metadata from one successful build; retain all source routes."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = {"ECTA", "supp", "appendix", "RESPONSE_TO_REFEREE"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True, help="Build receipt relative to the R125 directory, or an absolute path within it")
    args = parser.parse_args()
    receipt_path = Path(args.receipt)
    if not receipt_path.is_absolute():
        receipt_path = ROOT / receipt_path
    receipt_path = receipt_path.resolve()
    relative_receipt = receipt_path.relative_to(ROOT).as_posix()
    receipt = json.loads(receipt_path.read_text())
    assert receipt["status"] == "compiled_clean"
    assert receipt["diagnostic"] is False
    assert not receipt["issues"] and not receipt["placeholders"]
    assert set(receipt["actual_project_inputs"]) == DOCS
    for command in receipt["commands"]:
        assert command["exit_code"] == 0 and command["status"] == "passed"
        assert sha(ROOT / command["log"]) == command["log_sha256"]

    map_path = ROOT / "CONTENT_RETENTION125.json"
    mapping = json.loads(map_path.read_text())
    records_hash = stable_hash(mapping["records"])
    assert len(mapping["records"]) == 307 and mapping["unchanged_original_objects"] == 296
    if "initial_declared_closure_snapshot_sha256" not in mapping:
        mapping["initial_declared_closure_snapshot_sha256"] = stable_hash(mapping["closure_snapshot"])
    mapping["closure_snapshot"] = {
        document: sorted(paths)
        for document, paths in receipt["actual_project_inputs"].items()
    }
    changed = sorted({
        relative
        for paths in receipt["actual_project_inputs"].values()
        for relative, digest in paths.items()
        if not (ROOT / relative).is_file() or sha(ROOT / relative) != digest
    })
    identity = {
        "scope": "Actual project inputs recorded by TeX for this successful build, as of that build. Generated auxiliary/bibliography files and installed system inputs are separately bound in the build receipt. Bibliography source routes in the retained records are not replaced by this recorder list.",
        "build_receipt": relative_receipt,
        "build_receipt_sha256": sha(receipt_path),
        "build_started_utc": receipt["started_utc"],
        "build_finished_utc": receipt["finished_utc"],
        "build_status": receipt["status"],
        "document_project_input_counts": {document: len(paths) for document, paths in mapping["closure_snapshot"].items()},
        "records_unchanged_sha256": records_hash,
        "retained_records": 307,
        "original_baseline_records": 296,
        "later_inherited_records": 11,
        "refresh_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "refresh_script_sha256": sha(Path(__file__)),
        "current_project_inputs_changed_since_this_build": changed,
    }
    mapping["closure_snapshot_identity"] = identity
    assert stable_hash(mapping["records"]) == records_hash
    map_path.write_text(json.dumps(mapping, indent=2) + "\n")

    markdown_path = ROOT / "CONTENT_RETENTION125.md"
    markdown = markdown_path.read_text()
    changed_text = ("The current sources contain later edits; this recorder snapshot is a dated successful build, not a claim that those edits have already been rebuilt."
                    if changed else "Every recorded project input still matches the current bytes at this refresh.")
    block = (
        "<!-- R125-RECORDER-SNAPSHOT-BEGIN -->\n"
        "## Recorded build dependency snapshot\n\n"
        f"The JSON closure snapshot is taken from the strict successful build completed at `{receipt['finished_utc']}`, "
        f"receipt `{relative_receipt}` (SHA256 `{sha(receipt_path)}`). "
        "It records the project inputs actually read by TeX for all four documents. "
        "Generated auxiliary files, bibliography output and installed system inputs are identified separately in that receipt. "
        "All 307 retained file records, their source hashes and their reader routes remain unchanged. "
        f"{changed_text}\n\n"
        "Refresh only the build metadata after a later successful build with "
        "`python provenance/refresh_retention_closure125.py --receipt <receipt-relative-to-r125>`.\n"
        "<!-- R125-RECORDER-SNAPSHOT-END -->\n\n"
    )
    pattern = r"<!-- R125-RECORDER-SNAPSHOT-BEGIN -->.*?<!-- R125-RECORDER-SNAPSHOT-END -->\n*"
    if re.search(pattern, markdown, flags=re.S):
        markdown = re.sub(pattern, lambda match: block, markdown, flags=re.S)
    else:
        markdown = markdown.replace("## Exact file map\n", block + "## Exact file map\n", 1)
    markdown_path.write_text(markdown)
    print(json.dumps(identity, indent=2))


if __name__ == "__main__":
    main()
