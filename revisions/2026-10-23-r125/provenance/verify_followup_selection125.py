"""Read-only exact selection/transport check; no economic evaluations."""
from pathlib import Path
from collections import Counter
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


checks = ROOT / "results125/independent/checks125.jsonl"
rows = [json.loads(line) for line in checks.read_text().splitlines() if line]
unresolved = [row for row in rows if not (row["contained"] and row["gain_confirmed"])]
keys = sorted({row[field] for row in unresolved for field in ("final_key", "baseline_key")})
assert (len(rows), len(unresolved), len(keys)) == (936, 86, 110)

manifest_path = ROOT / "POSTFREEZE_AUDIT_FREEZE125.json"
manifest = json.loads(manifest_path.read_text())
for relative, expected_hash in manifest["files"].items():
    assert sha(ROOT / relative) == expected_hash, relative

logical = manifest["logical_independent_terminal_trace"]
digest = hashlib.sha256()
size = 0
for relative in logical["parts"]:
    with (ROOT / relative).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
            size += len(block)
assert size == logical["bytes"] == 13869944
assert digest.hexdigest() == logical["sha256"]
assert sha(ROOT / logical["path"]) == logical["sha256"]

output = ROOT / "provenance/FOLLOWUP_SELECTION_REVIEW125.json"
previous = json.loads(output.read_text()) if output.exists() else None
review = {
    "schema": "r125-post-primary-selection-review-v2",
    "checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status": "complete_selection_and_lossless_transport_verified_without_economic_execution",
    "role": "Independent author-side source and deterministic selection check; not an execution receipt for the follow-up audit",
    "source_script_sha256": sha(Path(__file__)),
    "original_rows": len(rows),
    "unresolved_rows": len(unresolved),
    "selected_distinct_state_risk_action_keys": len(keys),
    "unresolved_by_mode": dict(Counter(row["mode"] for row in unresolved)),
    "selection_rule": "Union of both final and completed-prefix keys from every original row with unresolved containment or gain confirmation",
    "selected_keys_sha256": hashlib.sha256(("\n".join(keys) + "\n").encode()).hexdigest(),
    "selected_keys": keys,
    "frozen_files_verified": len(manifest["files"]),
    "logical_original_trace_bytes": size,
    "logical_original_trace_sha256": digest.hexdigest(),
    "concatenation_identical_to_original_gzip": True,
    "economic_evaluations": 0,
    "source_sha256": {
        relative: sha(ROOT / relative)
        for relative in [
            "results125/independent/checks125.jsonl",
            "POSTFREEZE_AUDIT_PROTOCOL125.md",
            "reporting125/audit_followup125.py",
            "reporting125/materialize_independent_trace125.py",
            "POSTFREEZE_AUDIT_FREEZE125.json",
            "results125/independent_transport/TRANSPORT_SPLIT125.json",
        ]
    },
    "scope": "The follow-up design was selected after the original capped audit; all unresolved rows are included. Original 850/936 and 193/251 counts are unchanged. Transport splitting changes no evidence byte. Future results require their own completed source-bound receipt.",
}
if previous and previous.get("schema") == "r125-post-primary-selection-review-v1":
    review["pre_transport_source_binding"] = {
        "checked_utc": previous["checked_utc"],
        "source_sha256": previous["source_sha256"],
        "selection_unchanged": previous["selected_keys_sha256"] == review["selected_keys_sha256"],
    }
elif previous and "pre_transport_source_binding" in previous:
    review["pre_transport_source_binding"] = previous["pre_transport_source_binding"]
output.write_text(json.dumps(review, indent=2) + "\n")
print(json.dumps({key: value for key, value in review.items() if key not in ("selected_keys", "source_sha256", "pre_transport_source_binding")}, indent=2))

# The boundary is an actual remote-readback receipt, and START files are actual
# process records. This check is deliberately separate from audit completion.
boundary_path = ROOT / "POSTFREEZE_AUDIT_BOUNDARY125.json"
parent_start_path = ROOT / "results125/launch-independent-followup512/START125.json"
child_start_path = ROOT / "results125/independent-followup512/START125.json"
if boundary_path.exists() and parent_start_path.exists() and child_start_path.exists():
    boundary = json.loads(boundary_path.read_text())
    readback_path = ROOT / boundary["readback_receipt"]
    readback = json.loads(readback_path.read_text())
    parent = json.loads(parent_start_path.read_text())
    child = json.loads(child_start_path.read_text())
    assert boundary["source_commit"] == readback["source_commit"]
    assert boundary["manifest_sha256"] == sha(manifest_path)
    assert boundary["remote_readback_before_new_economics"] is True
    assert readback["all_entries_verified"] is True
    assert readback["remote_readback_before_new_economics"] is True
    assert boundary["remote_readback_completed_utc"] == readback["readback_completed_utc"]
    assert len(readback["entries"]) == boundary["remote_entries_verified"] == 20
    repo = ROOT.parents[1]
    for entry in readback["entries"]:
        path = repo / entry["path"]
        data = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert len(data) == entry["bytes"]
        assert hashlib.sha256(data).hexdigest() == entry["sha256"] == entry["remote_readback_sha256"]
        assert blob == entry["git_blob"] == entry["remote_readback_git_blob"]
        assert entry["verified"] is True
    moment = datetime.datetime.fromisoformat
    freeze_time = moment(manifest["created_utc"])
    readback_time = moment(readback["readback_completed_utc"])
    parent_time = moment(parent["started_utc"])
    child_time = moment(child["started_utc"])
    assert freeze_time <= readback_time < parent_time <= child_time
    actual_selection_path = ROOT / "results125/independent-followup512/SELECTION125.json"
    actual_selection = json.loads(actual_selection_path.read_text())
    assert actual_selection["keys"] == keys
    assert actual_selection["unique_actions"] == 110
    chronology = {
        "schema": "r125-followup-chronology-review-v1",
        "checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "source_readback_precedes_actual_process_launch",
        "role": "Independent author-side check of saved remote byte-readback and actual process-start records; no inference of audit completion",
        "source_script_sha256": sha(Path(__file__)),
        "source_commit": boundary["source_commit"],
        "source_tree": readback["tree"],
        "manifest_sha256": sha(manifest_path),
        "remote_readback_entries_independently_bound_to_local_bytes": 20,
        "freeze_created_utc": manifest["created_utc"],
        "remote_readback_completed_utc": readback["readback_completed_utc"],
        "parent_started_utc": parent["started_utc"],
        "child_started_utc": child["started_utc"],
        "readback_to_parent_seconds": (parent_time - readback_time).total_seconds(),
        "readback_to_child_seconds": (child_time - readback_time).total_seconds(),
        "actual_selected_keys_match_complete_selection": True,
        "actual_selected_keys": len(keys),
        "original_audit_containment_count_unchanged": 850,
        "original_audit_accepted_gain_count_unchanged": 193,
        "economic_evaluations_in_this_check": 0,
        "source_sha256": {
            str(path.relative_to(ROOT)): sha(path)
            for path in [boundary_path, readback_path, parent_start_path, child_start_path, actual_selection_path]
        },
        "scope": "Remote-readback receipt contents and process chronology are consistent. This is not a fresh network fetch, a completed independent evaluation, or evidence that all original claims are independently confirmed.",
    }
    (ROOT / "provenance/FOLLOWUP_CHRONOLOGY_REVIEW125.json").write_text(json.dumps(chronology, indent=2) + "\n")
    print(json.dumps({key: value for key, value in chronology.items() if key != "source_sha256"}, indent=2))
