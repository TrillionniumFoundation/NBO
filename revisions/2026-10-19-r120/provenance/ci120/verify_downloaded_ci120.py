"""Verify the downloaded, already completed source CI artifact without rerunning science."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    root = Path(__file__).resolve().parents[2]
    target = root / "provenance/ci120/source-run-39240515942"
    archive = target / "CI_ARTIFACT120.zip"
    output = target / "DOWNLOADED_ARTIFACT_VERIFICATION120.json"
    assert not output.exists(), "Use a fresh attempt; do not overwrite a receipt"
    metadata = json.loads((target / "CI_RECEIPT120.json").read_text())
    assert metadata["source_commit"] == "39a20bf1fe011175857811bf67bacd788ae80c52"
    assert metadata["run"]["status"] == "completed"
    assert metadata["run"]["conclusion"] == "success"
    assert metadata["run"]["head_sha"] == metadata["source_commit"]
    raw = archive.read_bytes()
    expected = next(x for x in metadata["artifact_metadata"]["artifacts"] if x["id"] == 12181820272)
    assert len(raw) == expected["size_in_bytes"]
    assert "sha256:" + sha(raw) == expected["digest"]
    inventory, compared, sources, pdfs = [], [], {}, []
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist()) == len(set(z.namelist()))
        for item in z.infolist():
            path = Path(item.filename)
            assert not path.is_absolute() and ".." not in path.parts
            data = z.read(item.filename)  # Includes each member's CRC verification.
            assert len(data) == item.file_size
            inventory.append({"path": item.filename, "bytes": len(data), "sha256": sha(data)})
        audit_name = "ci120/evidence-audit/AUDIT_EVIDENCE120.json"
        audit = json.loads(z.read(audit_name))
        assert audit["status"] == "passed" and audit["exit_code"] == 0
        assert audit["checked_out_commit"] == metadata["source_commit"]
        assert audit["publication_tool_commit_binding_required"] is True
        assert audit["manifest"]["sha256"] == sha((root / "EVIDENCE_MANIFEST120.json").read_bytes())
        for name in audit["details"]["reporting"]["stable_replay_files"]:
            data = z.read("ci120/evidence-audit/reporting-replay/" + name)
            assert data == (root / name).read_bytes(), name
            compared.append(name)
        assert len(compared) == 36
        build_names = [x for x in z.namelist() if x.endswith("/BUILD_RECEIPT120.json")]
        assert len(build_names) == 1
        build_name = build_names[0]
        build = json.loads(z.read(build_name))
        assert build["status"] == "compiled_clean"
        assert not build["issues"] and not build["placeholders"]
        assert len(build["commands"]) == 19
        for command in build["commands"]:
            assert command["exit_code"] == 0 and command["status"] == "passed"
            assert sha(z.read(command["log"])) == command["log_sha256"]
        for mapping in [build["source_sha256"], build["graphic_asset_sha256"], *build["actual_project_inputs"].values()]:
            for name, digest in mapping.items():
                assert sha((root / name).read_bytes()) == digest, name
                if name in sources:
                    assert sources[name] == digest
                sources[name] = digest
        for record in build["pdfs"]:
            data = z.read(record["path"])
            assert len(data) == record["bytes"] and sha(data) == record["sha256"]
            assert data == (root / record["path"]).read_bytes(), record["path"]
            pdfs.append({**record, "byte_identical_to_native_final_pdf": True})
        assert len(pdfs) == 4
        # Small original execution receipts are also convenient native publication records.
        for name, basename in [(audit_name, "CI_AUDIT_EVIDENCE120.json"), (build_name, "CI_BUILD_RECEIPT120.json")]:
            out = target / basename
            assert not out.exists()
            out.write_bytes(z.read(name))
    receipt = {
        "schema": "NBO_R120_DOWNLOADED_CI_ARTIFACT_VERIFICATION_V1",
        "recorded_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_commit": metadata["source_commit"], "run_id": 39240515942,
        "artifact_id": 12181820272, "archive_bytes": len(raw), "archive_sha256": sha(raw),
        "status": "passed", "members": inventory, "member_count": len(inventory),
        "source_paths_compared": len(sources), "stable_replay_outputs_compared": compared,
        "all_19_CI_build_command_logs_verified": True, "pdfs": pdfs,
        "scope": "Actual completed S CI, downloaded artifact custody, all member bytes/CRCs, original audit/build receipts, source hashes, deterministic reporting and exact four-PDF equality. No experiment, training, draw, timing or solver rerun.",
        "prior_read_only_inspection_failure": "An exploratory print attempted to slice an input-hash dictionary and raised KeyError before this verification; the artifact and all source bytes remained unchanged.",
    }
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "passed", "members": len(inventory), "source_paths": len(sources), "stable_outputs": len(compared), "byte_identical_PDFs": len(pdfs), "receipt": str(output)}))


if __name__ == "__main__":
    main()
