"""Build an explicitly enumerated R122 publication archive; execute no science.

--paths is a JSON array of repository-relative ordinary-file paths.  No glob,
directory expansion or implicit historical selection is performed.  The only
automatically added archive member is the newly written native-file manifest.
The explicit inputs must include the actual I122 publication receipt and its
three repair sources and the actual R122 receipt/four continuation sources;
all native source bytes are checked against their immutable Git commits.
The manifest, archive and parts directory must all be new.  Failure preserves
partial outputs; retry with distinct publication-attempt paths.

Determinism: sorted members, canonical manifest JSON, 1980 timestamps, regular
0644 members, no archive comment, and DEFLATE level 9.  Identical inputs under
the recorded Python/zlib implementation give identical archive bytes.  ZIP
compression bytes across different zlib versions are not presumed identical.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import time
import zipfile
import zlib

REVISION = Path(__file__).resolve().parents[1]
REPOSITORY = REVISION.parents[1]
SOURCE_F = "2f483615c8bc0037e43ec01a16cce05c724f8c60"
STATE_D = "a3323b6f557315ea91b536637419ef6fd7984b61"
ADAPTER = "af73f9bca8f2249da1601208a1921f50ea8fd074"
INDEPENDENT = "1f19410305c707716135defd91d6644d70657d84"
INDEPENDENT_PUBLICATION = "revisions/2026-10-20-r122/provenance122/INDEPENDENT_SCHEMA_PUBLICATION122.json"
INDEPENDENT_SOURCE_PATHS = (
    "revisions/2026-10-20-r122/provenance122/INDEPENDENT_SCHEMA_AMENDMENT122.md",
    "revisions/2026-10-20-r122/verification122/independent_schema_adapter122.py",
    "revisions/2026-10-20-r122/verification122/test_independent_schema_adapter122.py",
)
RESUME = "0fe0f2bbf76529201a1890db0fc2a94b0be44418"
RESUME_TREE = "e9325eb847d018e444b3c04cf2056740fd0a1989"
RESUME_PREFIX = "revisions/2026-10-20-r122/"
RESUME_PUBLICATION = RESUME_PREFIX + "provenance122/RESUME_INDEPENDENT_PUBLICATION122.json"
RESUME_PUBLICATION_SHA256 = "95cbeb89293df0202aed02a927b05e5a373f86d5f0d242e8fc87619b2006a03b"
RESUME_SOURCE_ROWS = [
    {"path": RESUME_PREFIX + "provenance122/RESUME_INDEPENDENT_PROTOCOL122.md", "bytes": 9503, "sha256": "1c288e36a240e1389955baf9b7eece506b49bc687ab3ae6e35e11fe272971e4c", "git_blob": "2375f5e4d0d454c490d47624fc3441fe5558f116"},
    {"path": RESUME_PREFIX + "verification122/resume_independent122.py", "bytes": 21573, "sha256": "32b7582c4f459851407bde3df24ae82a6c87f5ceaff34d606bba282b48b0d3a4", "git_blob": "5371ebc0768be62b3f5875cdd1b35dfaf7f0c110"},
    {"path": RESUME_PREFIX + "verification122/test_resume_independent122.py", "bytes": 8376, "sha256": "157c01d46dcbced69e71347b6330427c1383cffc96b52e66b5302e6e03489a03", "git_blob": "0df1e0dac336ee06d654122f313613f61e6208de"},
    {"path": RESUME_PREFIX + "verification122/validate_cached_witness122.py", "bytes": 9643, "sha256": "ff4eade48c8f04f737a4c44847d0f801a267a2a7f4bb330b8defe070dc05585f", "git_blob": "f90e9e99a056a5607a3abf6c3e3fa5e5b1ae80a4"},
]

PART_BYTES = 8 * 1024 * 1024
BLOCK_BYTES = 1024 * 1024
STAMP = (1980, 1, 1, 0, 0, 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relative_name(value):
    require(isinstance(value, str) and bool(value), "A nonempty relative path string is required")
    p = PurePosixPath(value)
    require(not p.is_absolute() and ".." not in p.parts and "\\" not in value
            and p.as_posix() == value and value != "." and "\x00" not in value,
            "Unsafe or noncanonical relative path: " + repr(value))
    return value


def no_symlink_components(root, relative):
    path = root
    for component in PurePosixPath(relative).parts:
        path = path / component
        require(not path.is_symlink(), "Symlink path component is not an ordinary native file: " + str(path))
    require(path.resolve().is_relative_to(root.resolve()), "Path escapes its declared root")
    return path


def ordinary_file(root, relative):
    p = no_symlink_components(root, relative_name(relative))
    require(p.is_file() and stat.S_ISREG(p.stat().st_mode), "Explicit input is not an ordinary file: " + str(p))
    return p


def digest_file(path):
    h, size = hashlib.sha256(), 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(BLOCK_BYTES), b""):
            h.update(block)
            size += len(block)
    return size, h.hexdigest()


def canonical_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def new_file(path):
    require(not path.exists() and not path.is_symlink(), "Publication output already exists: " + str(path))


def metadata(name, size):
    info = zipfile.ZipInfo(name, date_time=STAMP)
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    info.file_size = size
    info.comment = b""
    info.extra = b""
    return info


def independent_publication_binding(native):
    """Bind the actual I122 receipt and every declared repair source to Git I."""
    by_path = {r["path"]: r for r in native}
    required = {INDEPENDENT_PUBLICATION, *INDEPENDENT_SOURCE_PATHS}
    require(required <= set(by_path),
            "Explicit package inputs must include the I122 publication receipt and all three repair sources")
    publication_path = ordinary_file(REPOSITORY, INDEPENDENT_PUBLICATION)
    publication = json.loads(publication_path.read_text())
    require(publication.get("status") == "executed"
            and publication.get("source_commit_F") == SOURCE_F
            and publication.get("independent_adapter_commit") == INDEPENDENT,
            "Independent repair publication identity differs")
    actual_tree = subprocess.check_output(
        ["git", "rev-parse", INDEPENDENT + "^{tree}"], cwd=REPOSITORY, text=True).strip()
    require(publication.get("independent_adapter_tree") == actual_tree,
            "Independent repair publication tree differs from actual Git I122")
    source_rows = publication.get("source_files")
    require(isinstance(source_rows, list) and len(source_rows) == len(INDEPENDENT_SOURCE_PATHS)
            and {r.get("path") for r in source_rows} == set(INDEPENDENT_SOURCE_PATHS),
            "Independent repair publication must bind the exact three declared sources")
    sources = []
    for row in sorted(source_rows, key=lambda r: r["path"]):
        require(set(row) == {"path", "bytes", "sha256", "git_blob"},
                "Unexpected independent repair source record schema")
        name = relative_name(row["path"])
        expected_native = {k: row[k] for k in ("path", "bytes", "sha256")}
        require(by_path[name] == expected_native,
                "Explicit native I122 source differs from its publication receipt")
        actual = ordinary_file(REPOSITORY, name).read_bytes()
        published = subprocess.check_output(
            ["git", "show", INDEPENDENT + ":" + name], cwd=REPOSITORY)
        blob = hashlib.sha1(b"blob " + str(len(actual)).encode("ascii") + b"\0" + actual).hexdigest()
        require(actual == published and len(actual) == row["bytes"]
                and hashlib.sha256(actual).hexdigest() == row["sha256"]
                and blob == row["git_blob"],
                "Independent repair native bytes do not match their actual published Git blob")
        sources.append(dict(row))
    return {
        "independent_adapter_commit": publication["independent_adapter_commit"],
        "independent_adapter_tree": publication["independent_adapter_tree"],
        "independent_adapter_publication": dict(by_path[INDEPENDENT_PUBLICATION]),
        "independent_adapter_source_files": sources,
        "independent_adapter_git_membership_verified": True,
    }


def resume_publication_binding(native):
    """Bind the actual R122 continuation receipt and four source bytes to Git R."""
    by_path = {row["path"]: row for row in native}
    required = {RESUME_PUBLICATION, *(row["path"] for row in RESUME_SOURCE_ROWS)}
    require(required <= set(by_path), "Explicit package omits actual R122 receipt or continuation source")
    publication_bytes = ordinary_file(REPOSITORY, RESUME_PUBLICATION).read_bytes()
    require(hashlib.sha256(publication_bytes).hexdigest() == RESUME_PUBLICATION_SHA256,
            "R122 continuation publication receipt differs from observed immutable receipt")
    publication = json.loads(publication_bytes)
    tree = subprocess.check_output(["git", "rev-parse", RESUME + "^{tree}"], cwd=REPOSITORY, text=True).strip()
    require(publication.get("status") == "executed" and publication.get("source_commit_F") == SOURCE_F
            and publication.get("commit") == publication.get("resume_adapter_commit") == RESUME
            and publication.get("tree") == publication.get("resume_adapter_tree") == tree == RESUME_TREE,
            "Actual R122 continuation publication commit/tree differs")
    normalized = sorted([dict(row, path=RESUME_PREFIX + row["path"]) for row in publication["source_files"]], key=lambda row: row["path"])
    require(normalized == RESUME_SOURCE_ROWS, "R122 continuation receipt source census differs")
    for row in RESUME_SOURCE_ROWS:
        native_row = {key: row[key] for key in ("path", "bytes", "sha256")}
        require(by_path[row["path"]] == native_row, "R122 continuation source differs from explicit native list")
        data = ordinary_file(REPOSITORY, row["path"]).read_bytes()
        published = subprocess.check_output(["git", "show", RESUME + ":" + row["path"]], cwd=REPOSITORY)
        blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        require(data == published and len(data) == row["bytes"]
                and hashlib.sha256(data).hexdigest() == row["sha256"] and blob == row["git_blob"],
                "R122 native continuation source is not its actual published Git blob")
    return {"resume_adapter_commit": RESUME, "resume_adapter_tree": tree,
            "resume_adapter_publication": dict(by_path[RESUME_PUBLICATION]),
            "resume_adapter_source_files": RESUME_SOURCE_ROWS,
            "resume_adapter_git_membership_verified": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths", type=Path, required=True)
    parser.add_argument("--manifest", required=True,
                        help="New path relative to revisions/2026-10-20-r122")
    parser.add_argument("--archive", type=Path, required=True,
                        help="New absolute ZIP path")
    parser.add_argument("--parts-directory", required=True,
                        help="New directory relative to revisions/2026-10-20-r122")
    args = parser.parse_args()
    started = time.perf_counter()
    request_bytes = args.paths.read_bytes()
    requested = json.loads(request_bytes)
    require(isinstance(requested, list) and bool(requested), "--paths must contain a nonempty JSON array")
    names = [relative_name(p) for p in requested]
    require(len(names) == len(set(names)), "Explicit file list contains duplicate paths")
    names.sort()
    manifest = no_symlink_components(REVISION, relative_name(args.manifest))
    parts_dir = no_symlink_components(REVISION, relative_name(args.parts_directory))
    manifest_name = manifest.relative_to(REPOSITORY).as_posix()
    archive = args.archive
    require(archive.is_absolute(), "--archive must be absolute")
    # Resolve only the parent: never follow a possibly existing output symlink.
    archive = archive.parent.resolve() / archive.name
    require(archive.name not in ("", ".", ".."), "An archive filename is required")
    require(manifest_name not in names, "Manifest excludes itself from native input files")
    require(not manifest.is_relative_to(parts_dir) and not parts_dir.is_relative_to(manifest),
            "Manifest and parts directory must be disjoint")
    require(not archive.is_relative_to(parts_dir) and not parts_dir.is_relative_to(archive)
            and not archive.is_relative_to(manifest) and not manifest.is_relative_to(archive),
            "Archive, manifest and parts directory must have disjoint file/directory destinations")
    for path in (manifest, archive, parts_dir):
        new_file(path)

    native = []
    for name in names:
        p = ordinary_file(REPOSITORY, name)
        require(p != archive, "Archive cannot be an input")
        size, sha = digest_file(p)
        require(size == p.stat().st_size, "Input size changed while hashing: " + name)
        native.append({"path": name, "bytes": size, "sha256": sha})
    independent_binding = independent_publication_binding(native)
    independent_binding.update(resume_publication_binding(native))
    manifest_value = {
        "schema": "nbo.r122.referee-package.native.v1",
        "path_root": "repository", "self_excluded": True,
        "source_commit_F": SOURCE_F, "state_commit_D": STATE_D,
        "reporting_adapter_commit": ADAPTER, **independent_binding,
        "independent_initial_state_units": 32,
        "new_population_observations": 0, "new_training": 0,
        "new_economic_evaluations": 0, "new_service_timing_processes": 0,
        "explicit_paths_request_sha256": hashlib.sha256(request_bytes).hexdigest(),
        "native_input_count": len(native), "native_input_bytes": sum(r["bytes"] for r in native),
        "selection_scope": "Exactly the caller's explicit ordinary-file list. No directory expansion, historical evidence substitution or new scientific execution.",
        "historical_scope": "Historical original attachments retain their source-branch routes in the supplied retention map; this manifest makes no claim that unlisted historical archives are included.",
        "files": native,
    }
    manifest_bytes = canonical_bytes(manifest_value)
    manifest_record = {"path": manifest_name, "bytes": len(manifest_bytes),
                       "sha256": hashlib.sha256(manifest_bytes).hexdigest()}
    members = sorted(native + [manifest_record], key=lambda r: r["path"])

    # Every output is exclusive. A failure does not overwrite or delete evidence.
    manifest.parent.mkdir(parents=True, exist_ok=True)
    archive.parent.mkdir(parents=True, exist_ok=True)
    parts_dir.mkdir(parents=True, exist_ok=False)
    with manifest.open("xb") as stream:
        stream.write(manifest_bytes)
    with archive.open("xb") as file:
        with zipfile.ZipFile(file, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9, allowZip64=True) as zipped:
            zipped.comment = b""
            for row in members:
                p = ordinary_file(REPOSITORY, row["path"])
                h, count = hashlib.sha256(), 0
                info = metadata(row["path"], row["bytes"])
                # ZipInfo otherwise ignores ZipFile's compresslevel.
                info._compresslevel = 9
                with p.open("rb") as source, zipped.open(info, "w", force_zip64=row["bytes"] >= zipfile.ZIP64_LIMIT) as target:
                    for block in iter(lambda: source.read(BLOCK_BYTES), b""):
                        target.write(block)
                        h.update(block)
                        count += len(block)
                require(count == row["bytes"] and h.hexdigest() == row["sha256"],
                        "Input changed while writing ZIP: " + row["path"])
        file.flush()
        os.fsync(file.fileno())

    # Re-read all originals after closing the archive, including its manifest.
    for row in members:
        actual = digest_file(ordinary_file(REPOSITORY, row["path"]))
        require(actual == (row["bytes"], row["sha256"]),
                "Input changed after archive construction: " + row["path"])
    with zipfile.ZipFile(archive) as zipped:
        infos = zipped.infolist()
        require(len(infos) == len(members) and [r.filename for r in infos] == [r["path"] for r in members],
                "Written archive member census differs")
        require(all(r.date_time == STAMP and r.create_system == 3 and
                    (r.external_attr >> 16) == (stat.S_IFREG | 0o644) for r in infos),
                "Written archive metadata differs")

    archive_hash, archive_size, parts = hashlib.sha256(), 0, []
    with archive.open("rb") as stream:
        index = 0
        while block := stream.read(PART_BYTES):
            name = f"part-{index:05d}.bin"
            with (parts_dir / name).open("xb") as target:
                target.write(block)
            parts.append({"path": name, "bytes": len(block),
                          "sha256": hashlib.sha256(block).hexdigest()})
            archive_hash.update(block)
            archive_size += len(block)
            index += 1
    require(archive_size == archive.stat().st_size and bool(parts), "Archive size changed during splitting")
    transport = {
        "schema": "nbo.r122.referee-package.transport.v1",
        "kind": "lossless R122 referee-package transport",
        "path_root": "repository", "source_commit_F": SOURCE_F,
        "state_commit_D": STATE_D, "reporting_adapter_commit": ADAPTER, **independent_binding,
        "independent_initial_state_units": 32,
        "new_population_observations": 0, "new_training": 0,
        "new_economic_evaluations": 0, "new_service_timing_processes": 0,
        "archive_name": archive.name, "archive_bytes": archive_size,
        "archive_sha256": archive_hash.hexdigest(),
        "part_size_bytes": PART_BYTES, "part_count": len(parts), "parts": parts,
        "member_count": len(members), "members": members,
        "native_input_count": len(native),
        "native_input_bytes": sum(r["bytes"] for r in native),
        "manifest_path": manifest_name, "manifest_bytes": len(manifest_bytes),
        "manifest_sha256": manifest_record["sha256"],
        "input_hashes_verified_before_during_and_after_archive": True,
        "compression": "DEFLATE level 9",
        "zip_metadata": {"timestamp": list(STAMP), "create_system": 3,
                         "regular_file_permissions_octal": "0644", "archive_comment": ""},
        "runtime": {"python": sys.version, "zlib_compile": zlib.ZLIB_VERSION,
                    "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION},
        "builder_sha256": digest_file(Path(__file__))[1],
        "scientific_scope": "Publication packaging only; the original independent scientific state count remains 32.",
    }
    transport_path = parts_dir / "PACKAGE_TRANSPORT122.json"
    with transport_path.open("xb") as stream:
        stream.write(canonical_bytes(transport))
    print(json.dumps({"status": "packaged", "manifest": manifest_name,
        "manifest_sha256": manifest_record["sha256"], "archive": str(archive),
        "archive_bytes": archive_size, "archive_sha256": archive_hash.hexdigest(),
        "parts_directory": parts_dir.relative_to(REVISION).as_posix(),
        "transport_sha256": digest_file(transport_path)[1],
        "members": len(members), "parts": len(parts),
        "seconds": time.perf_counter() - started, "new_economic_evaluations": 0}, indent=2))


if __name__ == "__main__":
    main()
