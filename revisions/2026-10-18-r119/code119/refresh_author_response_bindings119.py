"""Check/refresh current source bindings in the delivered R119 author maps.

Standard library only. This command never runs scientific code, changes author
responses, rewrites old referee text, reclassifies an issue, or edits a manuscript.
Original report blobs and item hashes must still verify. All changed current
bindings are listed in the receipt, so a refresh is an identity operation rather
than scientific revalidation of the changed file.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re


def sha(data):
    return hashlib.sha256(data).hexdigest()


def gitblob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", type=Path, required=True)
    parser.add_argument("--major", type=Path)
    parser.add_argument("--additional", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--refresh", action="store_true", help="Write new current bindings after original identities verify")
    args = parser.parse_args()
    root = args.revision.resolve()
    major_path = (args.major or root / "provenance/HISTORICAL_CARRYFORWARD119.json").resolve()
    additional_path = (args.additional or root / "provenance/ADDITIONAL_REFEREE_RESPONSE119.json").resolve()
    receipt_path = args.receipt or root / "provenance/AUTHOR_RESPONSE_BINDING_RECEIPT119.json"
    before_major = major_path.read_bytes()
    before_additional = additional_path.read_bytes()
    major = json.loads(before_major)
    additional = json.loads(before_additional)
    assert len(major["rows"]) == 620 and len(additional["rows"]) == 394
    assert len(additional["overlapping_parent_treatments"]) == 35
    assert len(additional["section_classification"]) == 1146
    assert len({r["key"] for r in major["rows"] + additional["rows"]}) == 1014

    report_cache = {}
    original_checks = 0
    for row in major["rows"] + additional["rows"] + additional["overlapping_parent_treatments"]:
        assert row["closed"] is False, row["key"]
        source = root / "provenance" / row["source_path"]
        if source not in report_cache:
            raw = source.read_bytes()
            report_cache[source] = (gitblob(raw), raw.decode("utf-8"))
        observed, report_text = report_cache[source]
        assert observed == row["report_git_blob_sha1"], row["key"]
        exact = row["exact_text"]
        assert exact.rstrip() in report_text, row["key"]
        expected = row.get("comment_sha256", row.get("item_sha256", row.get("section_sha256")))
        alternatives = [exact, exact + "\n", exact.rstrip(), exact.rstrip() + "\n", exact.rstrip() + "\n\n"]
        assert expected in {sha(s.encode()) for s in alternatives}, row["key"]
        original_checks += 1

    cache, changes = {}, {}
    def refresh_binding(binding):
        relative = binding["path"]
        path = (root / relative).resolve()
        assert path.is_relative_to(root), relative
        assert path not in {major_path, additional_path, receipt_path.resolve()}, "circular source binding"
        if relative not in cache:
            data = path.read_bytes()
            cache[relative] = {"path": relative, "bytes": len(data), "sha256": sha(data), "git_blob_sha1": gitblob(data)}
            if path.suffix == ".tex":
                cache[relative]["labels"] = list(dict.fromkeys(re.findall(r"\\label\{([^}]+)\}", data.decode("utf-8"))))
        actual = cache[relative]
        if "labels" in binding:
            removed = set(binding["labels"]) - set(actual.get("labels", []))
            assert not removed, (relative, "removed routed theorem labels", sorted(removed))
        if binding.get("sha256") != actual["sha256"] or binding.get("bytes") != actual["bytes"]:
            old = {k: binding.get(k) for k in ["sha256", "bytes", "git_blob_sha1"]}
            changes[(relative, old["sha256"])] = {"path": relative, "previous_binding": old, "current_binding": actual}
        result = dict(binding)
        result.update({k: v for k, v in actual.items() if k != "labels" or "labels" in binding})
        return result

    for document, key in [(major, "current_source_registry"), (additional, "source_registry")]:
        document[key] = {path: refresh_binding(value) for path, value in document[key].items()}
        for row in document["rows"] + document.get("overlapping_parent_treatments", []):
            row["current_source_bindings"] = [refresh_binding(b) for b in row["current_source_bindings"]]

    new_major = encoded(major)
    expected_major_sha = sha(new_major if args.refresh else before_major)
    linkage_changed = additional["major_map_binding"].get("sha256") != expected_major_sha
    if args.refresh:
        additional["major_map_binding"]["sha256"] = expected_major_sha
        additional["major_map_binding"]["path"] = str(major_path.relative_to(root)) if major_path.is_relative_to(root) else major_path.name
    new_additional = encoded(additional)
    if args.refresh:
        major_path.write_bytes(new_major)
        additional_path.write_bytes(new_additional)
    stale = bool(changes) or linkage_changed
    receipt = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "refreshed_current_source_bindings" if args.refresh else "passed" if not stale else "stale_current_source_bindings",
        "scope": "Original referee identity/text verification and current source binding only. No proof, experiment, timing or CI is rerun or declared successful by this operation.",
        "source_script_sha256": sha(Path(__file__).read_bytes()),
        "counts": {"major_blocks": 620, "additional_items": 394, "combined_routed_records": 1014, "overlapping_parent_treatments": 35, "hierarchical_sections": 1146, "original_text_hash_checks": original_checks, "distinct_original_report_blobs": len(report_cache), "current_source_files": len(cache)},
        "changes": list(changes.values()),
        "additional_to_major_binding_changed": linkage_changed,
        "before": {major_path.name: sha(before_major), additional_path.name: sha(before_additional)},
        "after": {major_path.name: sha(major_path.read_bytes()), additional_path.name: sha(additional_path.read_bytes())},
        "original_comment_text_or_identity_changed": False,
        "author_actions_or_remaining_requirements_changed": False,
        "blanket_closure_asserted": False,
        "scientific_execution": False,
    }
    receipt_path.write_bytes(encoded(receipt))
    print(json.dumps({k: v for k, v in receipt.items() if k != "changes"}, indent=2))
    print("Changed current bindings:", len(changes))
    if stale and not args.refresh:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
