"""Copy completed reporting derivatives only; preserve the original report run."""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import os


def identity(p):
    b = p.read_bytes()
    return {
        "bytes": len(b),
        "sha256": hashlib.sha256(b).hexdigest(),
        "git_blob": hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", required=True, type=Path)
    args = parser.parse_args()
    revision = args.revision.resolve()
    output = revision / "results120/reporting-attempt01"
    manifest_path = output / "OUTPUT_MANIFEST120.json"
    manifest = json.loads(manifest_path.read_text())
    by_path = {r["path"]: r for r in manifest["files"]}
    execution = json.loads((output / "EXECUTION_REPORT120.json").read_text())
    assert execution["exit_code"] == 0
    assert execution["all_scientific_input_bytes_unchanged"]
    assert not execution["economic_solver_executed"]
    files = manifest["stable_replay_files"]
    assert len(files) == len(set(files)) == 36
    expected_placeholder_sha = "6930f742ad01c63ab9c2aa42e35d922da51618e79ff600cd29d771895e4ae9ba"
    preparation = []
    total = 0
    for name in files:
        rel = Path(name)
        assert not rel.is_absolute() and ".." not in rel.parts
        assert rel.parts[0] in {"new120", "tables120"}
        source = output / rel
        target = revision / rel
        ident = identity(source)
        assert all(ident[k] == by_path[name][k] for k in ident)
        assert by_path[name]["stable_replay_bytes"]
        before = None
        if target.exists():
            before = identity(target)
            assert name in {"new120/results120.tex", "new120/development120_results.tex"}
            assert before["bytes"] == 107 and before["sha256"] == expected_placeholder_sha
            before["utf8_contents"] = target.read_text()
        preparation.append((name, source, target, ident, before))
        total += ident["bytes"]
    fs = os.statvfs(revision)
    assert fs.f_bavail * fs.f_frsize > total + 32 * 1024 * 1024
    receipt_path = Path(__file__).parent / "REPORTING_PRODUCTS_COPY120.json"
    assert not receipt_path.exists()
    rows = []
    for name, source, target, ident, before in preparation:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb" if before is not None else "xb") as handle:
            handle.write(source.read_bytes())
        assert identity(source) == identity(target) == ident
        rows.append({"path": name, "source": str(source), "target": str(target),
                     **ident, "target_previous_placeholder": before,
                     "source_and_target_exact_byte_identity": True})
    receipt = {
        "kind": "native_author_copy_of_completed_reporting_products120",
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_manifest": {"path": str(manifest_path), **identity(manifest_path)},
        "executed_copy_source": {"path": str(Path(__file__).resolve()), **identity(Path(__file__))},
        "copied_files": len(rows), "copied_bytes": total, "files": rows,
        "scientific_records_or_reporter_outputs_modified": False,
        "native_author_copies_may_receive_separately_documented_editorial_changes": True,
    }
    with receipt_path.open("x") as handle:
        json.dump(receipt, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"receipt": str(receipt_path), **identity(receipt_path),
                      "copied_files": len(rows), "copied_bytes": total}))


if __name__ == "__main__":
    main()
