"""Independently validate a transported R122 referee archive; execute no science.

The verifier reassembles parts into a temporary ZIP, checks exact member
census, safe ordinary-file metadata and every streamed member hash, then
checks the native-file manifest, including the I122 publication receipt and
all three independently pinned published independent-repair Git blobs.
The observed I122 tree and source identities are fixed in this reader.
--repository optionally verifies every
archived member against the current ordinary native file, including the
manifest.  It never extracts into the repository or imports a scientific
module.  --receipt, when supplied, is a new exclusive output file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import tempfile
import time
import zipfile

SOURCE_F = "2f483615c8bc0037e43ec01a16cce05c724f8c60"
STATE_D = "a3323b6f557315ea91b536637419ef6fd7984b61"
ADAPTER = "af73f9bca8f2249da1601208a1921f50ea8fd074"
INDEPENDENT = "1f19410305c707716135defd91d6644d70657d84"
# Independently observed immutable I122 publication identities. The offline
# reader pins these bytes; it does not fetch Git objects or infer membership
# solely from a self-consistent archive attestation.
INDEPENDENT_TREE = '6f92dd077a1b27986d22c264603ddb1cf4f07667'
INDEPENDENT_SOURCE_ROWS = [
    {
        "bytes": 6894,
        "git_blob": "23f295b45b26798c3ed99da5355232682a13ea67",
        "path": "revisions/2026-10-20-r122/provenance122/INDEPENDENT_SCHEMA_AMENDMENT122.md",
        "sha256": "2e21674081a07c03a797b43b8f765c9acffa8ff40f5528854f00817cecc14518"
    },
    {
        "bytes": 9203,
        "git_blob": "5f9c41216025c97cc94bef4ca5a5de2288c94002",
        "path": "revisions/2026-10-20-r122/verification122/independent_schema_adapter122.py",
        "sha256": "9d2fcf4dd41cb1eab45afec5f4e737164b0992bac459105dd06563abc95aa92c"
    },
    {
        "bytes": 9147,
        "git_blob": "b1f32dc2fc690ae67b3e57c2a12486e191616a68",
        "path": "revisions/2026-10-20-r122/verification122/test_independent_schema_adapter122.py",
        "sha256": "6c6c293f5432eaa8d87b1b8d01ae6f392c90fe92e8a6c33a6d18733b3955c67a"
    }
]
INDEPENDENT_PUBLICATION = "revisions/2026-10-20-r122/provenance122/INDEPENDENT_SCHEMA_PUBLICATION122.json"
INDEPENDENT_SOURCE_PATHS = (
    "revisions/2026-10-20-r122/provenance122/INDEPENDENT_SCHEMA_AMENDMENT122.md",
    "revisions/2026-10-20-r122/verification122/independent_schema_adapter122.py",
    "revisions/2026-10-20-r122/verification122/test_independent_schema_adapter122.py",
)
PART_BYTES = 8 * 1024 * 1024
BLOCK_BYTES = 1024 * 1024
STAMP = (1980, 1, 1, 0, 0, 0)


def check(condition, message):
    if not condition:
        raise ValueError(message)


def safe_relative(value):
    check(isinstance(value, str) and bool(value), "Missing relative path")
    p = PurePosixPath(value)
    check(not p.is_absolute() and ".." not in p.parts and "\\" not in value
          and p.as_posix() == value and value != "." and "\x00" not in value,
          "Unsafe/noncanonical path: " + repr(value))
    return value


def native(root, relative):
    current = root
    for component in PurePosixPath(safe_relative(relative)).parts:
        current /= component
        check(not current.is_symlink(), "Symlink component is not ordinary native evidence")
    check(current.resolve().is_relative_to(root.resolve()) and current.is_file()
          and stat.S_ISREG(current.stat().st_mode), "Missing/nonregular native file: " + str(current))
    return current


def hash_stream(stream):
    h, size = hashlib.sha256(), 0
    for block in iter(lambda: stream.read(BLOCK_BYTES), b""):
        h.update(block)
        size += len(block)
    return size, h.hexdigest()


def hash_file(path):
    with path.open("rb") as stream:
        return hash_stream(stream)


def record_map(rows, label):
    check(isinstance(rows, list) and bool(rows), "Empty " + label)
    result = {}
    for row in rows:
        check(isinstance(row, dict) and set(row) == {"path", "bytes", "sha256"},
              "Unexpected record schema in " + label)
        name = safe_relative(row["path"])
        check(name not in result, "Duplicate path in " + label)
        check(isinstance(row["bytes"], int) and not isinstance(row["bytes"], bool) and row["bytes"] >= 0,
              "Invalid member size")
        sha = row["sha256"]
        check(isinstance(sha, str) and len(sha) == 64 and all(c in "0123456789abcdef" for c in sha),
              "Invalid SHA256")
        result[name] = row
    return result


def identities(value):
    check(value.get("path_root") == "repository", "Wrong package path root")
    check(value.get("source_commit_F") == SOURCE_F and value.get("state_commit_D") == STATE_D
          and value.get("reporting_adapter_commit") == ADAPTER, "Package scientific/source identity differs")
    check(value.get("independent_adapter_commit") == INDEPENDENT
          and value.get("independent_adapter_git_membership_verified") is True,
          "Independent repair I122 identity or Git-membership attestation differs")
    check(value.get("independent_initial_state_units") == 32, "Packaging cannot change the original scientific n")
    for name in ("new_population_observations", "new_training", "new_economic_evaluations", "new_service_timing_processes"):
        check(value.get(name) == 0, "Publication package must not claim new science: " + name)


def independent_publication_binding(value, members, zipped):
    """Check I122 metadata, its archived receipt, and its three native Git blobs."""
    publication_record = value.get("independent_adapter_publication")
    checked = record_map([publication_record], "independent publication")
    check(set(checked) == {INDEPENDENT_PUBLICATION}
          and members.get(INDEPENDENT_PUBLICATION) == publication_record,
          "I122 publication receipt is not an exact native archive member")
    publication = json.loads(zipped.read(INDEPENDENT_PUBLICATION))
    check(publication.get("status") == "executed"
          and publication.get("source_commit_F") == SOURCE_F
          and publication.get("independent_adapter_commit") == INDEPENDENT
          and publication.get("independent_adapter_tree") == value.get("independent_adapter_tree"),
          "Archived I122 publication receipt differs from manifest/transport identity")
    check(value.get("independent_adapter_tree") == INDEPENDENT_TREE,
          "I122 tree differs from the independently observed publication")
    source_rows = value.get("independent_adapter_source_files")
    check(isinstance(source_rows, list) and len(source_rows) == len(INDEPENDENT_SOURCE_PATHS)
          and {r.get("path") for r in source_rows} == set(INDEPENDENT_SOURCE_PATHS),
          "Exact three-source I122 repair binding required")
    check(sorted(publication.get("source_files", []), key=lambda r: r["path"])
          == source_rows, "I122 receipt/source records differ or are unsorted")
    check(source_rows == INDEPENDENT_SOURCE_ROWS,
          "I122 source rows differ from the independently observed publication")
    for row in source_rows:
        check(set(row) == {"path", "bytes", "sha256", "git_blob"},
              "Unexpected I122 source binding schema")
        name = safe_relative(row["path"])
        native_record = {k: row[k] for k in ("path", "bytes", "sha256")}
        record_map([native_record], "independent repair source")
        check(members.get(name) == native_record, "I122 source omitted or changed in native archive")
        data = zipped.read(name)
        blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        check(blob == row["git_blob"] and len(data) == row["bytes"]
              and hashlib.sha256(data).hexdigest() == row["sha256"],
              "I122 archived native bytes/Git blob identity differ")
    return {name: value[name] for name in (
        "independent_adapter_commit", "independent_adapter_tree",
        "independent_adapter_publication", "independent_adapter_source_files",
        "independent_adapter_git_membership_verified")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transport", type=Path, required=True)
    parser.add_argument("--repository", type=Path,
                        help="Optional native repository root; every archived member must match")
    parser.add_argument("--receipt", type=Path,
                        help="Optional new exclusive JSON verification receipt")
    args = parser.parse_args()
    started = time.perf_counter()
    if args.receipt:
        check(not args.receipt.exists() and not args.receipt.is_symlink(), "Verification receipt already exists")
    transport_path = args.transport.resolve()
    raw = transport_path.read_bytes()
    transport = json.loads(raw)
    check(transport.get("schema") == "nbo.r122.referee-package.transport.v1" and
          transport.get("kind") == "lossless R122 referee-package transport", "Wrong transport schema")
    identities(transport)
    parts = record_map(transport["parts"], "parts")
    check(transport["part_size_bytes"] == PART_BYTES and transport["part_count"] == len(parts),
          "Part size/count differs")
    check(list(parts) == [f"part-{i:05d}.bin" for i in range(len(parts))],
          "Parts must have the complete ordered sequence")
    check(all(0 < r["bytes"] <= PART_BYTES for r in parts.values()) and
          all(r["bytes"] == PART_BYTES for r in list(parts.values())[:-1]), "Invalid part extent")
    members = record_map(transport["members"], "archive members")
    check(transport["member_count"] == len(members) and list(members) == sorted(members),
          "Wrong or unsorted archive member census")
    manifest_name = safe_relative(transport["manifest_path"])
    check(manifest_name in members and members[manifest_name] == {
        "path": manifest_name, "bytes": transport["manifest_bytes"],
        "sha256": transport["manifest_sha256"]}, "Manifest identity differs from member census")
    check(transport["native_input_count"] == len(members) - 1, "Native input count differs")
    check(transport["input_hashes_verified_before_during_and_after_archive"] is True,
          "Builder did not attest input stability")
    check(transport.get("compression") == "DEFLATE level 9", "Unexpected compression declaration")
    repository = args.repository.resolve() if args.repository else None
    if repository:
        check(repository.is_dir(), "Native repository root is not a directory")

    member_bytes, native_checked = 0, 0
    with tempfile.TemporaryDirectory(prefix="nbo-r122-referee-readonly-") as directory:
        archive = Path(directory) / "referee-package.zip"
        archive_hash, archive_bytes = hashlib.sha256(), 0
        with archive.open("xb") as target:
            for row in parts.values():
                p = native(transport_path.parent, row["path"])
                h, size = hashlib.sha256(), 0
                with p.open("rb") as source:
                    for block in iter(lambda: source.read(BLOCK_BYTES), b""):
                        target.write(block)
                        h.update(block)
                        size += len(block)
                        archive_hash.update(block)
                        archive_bytes += len(block)
                check(size == row["bytes"] and h.hexdigest() == row["sha256"],
                      "Transport part differs: " + row["path"])
        check(archive_bytes == transport["archive_bytes"] == sum(r["bytes"] for r in parts.values())
              and archive_hash.hexdigest() == transport["archive_sha256"], "Whole archive identity differs")
        with zipfile.ZipFile(archive) as zipped:
            infos = zipped.infolist()
            check(zipped.comment == b"", "Unexpected archive comment")
            check(len(infos) == len(members) and [r.filename for r in infos] == list(members),
                  "ZIP member census, order or duplicates differ")
            for info in infos:
                safe_relative(info.filename)
                row = members[info.filename]
                check(not info.is_dir() and not (info.flag_bits & 1) and
                      info.create_system == 3 and (info.external_attr >> 16) == (stat.S_IFREG | 0o644)
                      and info.date_time == STAMP and info.comment == b""
                      and info.compress_type == zipfile.ZIP_DEFLATED,
                      "ZIP member is not the declared safe regular file: " + info.filename)
                check(info.file_size == row["bytes"], "ZIP member size differs")
                with zipped.open(info) as stream:
                    size, sha = hash_stream(stream)
                check((size, sha) == (row["bytes"], row["sha256"]),
                      "ZIP member bytes/hash differ: " + info.filename)
                member_bytes += size
                if repository:
                    p = native(repository, info.filename)
                    check(hash_file(p) == (row["bytes"], row["sha256"]),
                          "Existing native member differs: " + info.filename)
                    native_checked += 1
            manifest_bytes = zipped.read(manifest_name)
            check(hashlib.sha256(manifest_bytes).hexdigest() == transport["manifest_sha256"],
                  "Native manifest hash differs")
            manifest = json.loads(manifest_bytes)
            identities(manifest)
            check(manifest.get("schema") == "nbo.r122.referee-package.native.v1"
                  and manifest.get("self_excluded") is True, "Native manifest schema/self policy differs")
            declared = record_map(manifest["files"], "native manifest")
            check(manifest_name not in declared and declared ==
                  {k: v for k, v in members.items() if k != manifest_name},
                  "Native manifest and exact archive members disagree")
            expected_native_bytes = sum(r["bytes"] for r in declared.values())
            check(manifest["native_input_count"] == transport["native_input_count"] == len(declared)
                  and manifest["native_input_bytes"] == transport["native_input_bytes"] == expected_native_bytes,
                  "Native manifest byte/count total differs")
            check(member_bytes == expected_native_bytes + len(manifest_bytes), "Archive uncompressed byte census differs")
            transport_binding = independent_publication_binding(transport, members, zipped)
            manifest_binding = independent_publication_binding(manifest, members, zipped)
            check(manifest_binding == transport_binding,
                  "Manifest and transport differ on the actual independent repair binding")

    receipt = {"status": "verified", "scope": "Independent publication transport and native-byte verification; no scientific execution or archive extraction into the repository.",
        "source_commit_F": SOURCE_F, "state_commit_D": STATE_D,
        "reporting_adapter_commit": ADAPTER, "independent_initial_state_units": 32,
        "independent_adapter_commit": INDEPENDENT,
        "independent_adapter_tree": INDEPENDENT_TREE,
        "independent_adapter_published_source_identities_pinned": True,
        "independent_adapter_publication_sha256": transport["independent_adapter_publication"]["sha256"],
        "independent_adapter_sources_checked": len(INDEPENDENT_SOURCE_PATHS),
        "transport_sha256": hashlib.sha256(raw).hexdigest(),
        "archive_sha256": transport["archive_sha256"], "archive_bytes": transport["archive_bytes"],
        "manifest_path": manifest_name, "manifest_sha256": transport["manifest_sha256"],
        "parts_checked": len(parts), "archive_members_checked": len(members),
        "uncompressed_member_bytes": member_bytes,
        "native_input_count": transport["native_input_count"],
        "native_repository": str(repository) if repository else None,
        "native_members_checked": native_checked,
        "new_population_observations": 0, "new_training": 0,
        "new_economic_evaluations": 0, "new_service_timing_processes": 0,
        "verifier_sha256": hash_file(Path(__file__))[1],
        "seconds": time.perf_counter() - started}
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        with args.receipt.open("x") as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write("\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
