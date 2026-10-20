"""Assemble a declared R121 byte transport, without scientific execution.

The request and every chunk must already be committed at the exact current
transport commit T. Every compressed byte, ZIP member, CRC, SHA256 and Git blob
is checked in temporary storage before any native artifact is materialized.
Existing native files may only be retained byte-identically. No deletion,
scientific import, Git mutation, commit or network operation occurs here.
The separate, narrowly scoped Actions workflow commits and pushes the result.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import tempfile
import time
import zipfile

PREFIX = "revisions/2026-10-20-r121"
BUNDLES = PREFIX + "/transport121/bundles"
REQUEST = "REQUEST121.json"
RECEIPT = "ASSEMBLY121.json"
CHUNK = 1 << 20
PART_LIMIT = 8 << 20
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SHA1 = re.compile(r"[0-9a-f]{40}\Z")
BUNDLE = re.compile(r"[a-z0-9][a-z0-9._-]{0,95}\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def canonical(value):
    require(isinstance(value, str) and value, "A nonempty relative POSIX path is required")
    path = PurePosixPath(value)
    require(not path.is_absolute() and str(path) == value and ".." not in path.parts
            and "\\" not in value and not any(ord(c) < 32 or ord(c) == 127 for c in value),
            "Unsafe or noncanonical path: " + repr(value))
    return path


def local(repo, name):
    path = repo.joinpath(*canonical(name).parts)
    require(path.resolve().is_relative_to(repo), "Path leaves repository")
    for item in (path, *path.parents):
        if item == repo:
            break
        require(not item.is_symlink(), "A symlink is forbidden in a transport path")
    return path


def nonduplicate(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path):
    def nonfinite(value):
        raise ValueError("Nonfinite JSON number: " + value)
    return json.loads(path.read_bytes(), object_pairs_hook=nonduplicate,
                      parse_constant=nonfinite)


def identity(path):
    size = path.stat().st_size
    h = hashlib.sha256()
    g = hashlib.sha1(b"blob " + str(size).encode() + b"\0")
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK), b""):
            h.update(block)
            g.update(block)
    return dict(bytes=size, sha256=h.hexdigest(), git_blob=g.hexdigest())


def declared_identity(item, git_required=False):
    require(type(item.get("bytes")) is int and item["bytes"] >= 0,
            "Declared byte size must be a nonnegative integer")
    require(isinstance(item.get("sha256"), str) and SHA256.fullmatch(item["sha256"]),
            "A complete lowercase SHA256 is required")
    if git_required:
        require(isinstance(item.get("git_blob"), str) and SHA1.fullmatch(item["git_blob"]),
                "A complete lowercase Git blob identity is required")


def matches(actual, expected, fields=("bytes", "sha256")):
    require(all(actual[k] == expected[k] for k in fields),
            "Actual byte identity differs from the declared request")


def current_tree(repo, commit):
    entries = {}
    for row in git(repo, "ls-tree", "-r", "-z", commit, "--", PREFIX).split(b"\0"):
        if not row:
            continue
        header, name = row.split(b"\t", 1)
        mode, kind, sha = header.decode().split()
        entries[name.decode()] = (mode, kind, sha)
    return entries


def check_bound_file(repo, name, tree):
    item = tree.get(name)
    require(item is not None and item[0] in ("100644", "100755") and item[1] == "blob",
            "Transport input is not a regular file at T: " + name)
    path = local(repo, name)
    require(path.is_file(), "Missing committed transport input: " + name)
    value = identity(path)
    require(value["git_blob"] == item[2], "Local transport input differs from T: " + name)
    return path, value


def added_request(repo, commit):
    parents = git(repo, "rev-list", "--parents", "-n", "1", commit).decode().split()
    require(len(parents) == 2, "A transport commit must have exactly one parent")
    raw = git(repo, "diff", "--name-only", "--diff-filter=A", "--no-renames", "-z",
              parents[1], commit, "--", BUNDLES)
    names = [v.decode() for v in raw.split(b"\0") if v]
    requests = [name for name in names if name.endswith("/" + REQUEST)]
    require(len(requests) == 1, "T must add exactly one transport REQUEST121.json")
    return requests[0]


def assemble(args):
    started = utc()
    clock = time.perf_counter()
    repo = args.repository.resolve()
    require(repo.is_dir(), "Repository directory is required")
    require(isinstance(args.transport_commit, str) and SHA1.fullmatch(args.transport_commit),
            "A complete immutable transport commit T is required")
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    require(head == args.transport_commit, "Checked-out HEAD is not the requested T")
    require(not git(repo, "status", "--porcelain=v1", "--untracked-files=no").strip(),
            "Tracked worktree and index must be clean before assembly")
    expected_request = added_request(repo, head)
    request_name = expected_request if args.request == "auto" else args.request
    require(request_name == expected_request, "Explicit request differs from the only added request")
    request_parts = canonical(request_name).parts
    require(len(request_parts) == 6 and "/".join(request_parts[:4]) == BUNDLES
            and request_parts[-1] == REQUEST and BUNDLE.fullmatch(request_parts[-2]),
            "Unexpected native bundle request path")
    tree = current_tree(repo, head)
    request_path, request_identity = check_bound_file(repo, request_name, tree)
    request = read_json(request_path)
    require(request.get("kind") == "nbo-r121-byte-transport-v1"
            and request.get("revision_prefix") == PREFIX
            and request.get("bundle_id") == request_parts[-2], "Unexpected request schema or bundle identity")
    archive_info = request["archive"]
    declared_identity(archive_info)
    require(archive_info["bytes"] > 0, "The declared ZIP must be nonempty")
    parts = request["parts"]
    files = request["files"]
    require(isinstance(parts, list) and parts and isinstance(files, list) and files,
            "Complete nonempty part and member manifests are required")
    require(sum(row["bytes"] for row in parts) == archive_info["bytes"], "Part bytes do not sum to ZIP size")
    declared = {}
    for row in files:
        declared_identity(row, True)
        path = canonical(row["path"])
        require(str(path).startswith(PREFIX + "/")
                and not str(path).startswith(PREFIX + "/transport121/"),
                "Native members must stay inside R121 and outside transport control files")
        require(row["path"] not in declared, "Duplicate requested native path")
        declared[row["path"]] = row
    receipt_path = request_path.parent / RECEIPT
    require(not receipt_path.exists(), "An existing assembly receipt must never be overwritten")
    stage_list = args.stage_list.resolve()
    require(not stage_list.is_relative_to(repo), "The transient stage list must be outside the repository")
    require(not stage_list.exists(), "The requested stage list must be a fresh path")
    stage_list.parent.mkdir(parents=True, exist_ok=True)
    initial_existing = {}
    for name, row in declared.items():
        destination = local(repo, name)
        if destination.exists():
            require(destination.is_file(), "A native destination is not a regular file")
            matches(identity(destination), row, ("bytes", "sha256", "git_blob"))
            require(name in tree and tree[name][1] == "blob" and tree[name][2] == row["git_blob"],
                    "An existing destination must already be the same tracked file at T")
            initial_existing[name] = True
    # A native file cannot be another requested file's parent directory.
    for name in declared:
        require(not any(str(parent) in declared for parent in PurePosixPath(name).parents),
                "Requested file/directory prefix collision")
    part_receipts = []
    native_receipts = []
    copied = []
    with tempfile.TemporaryDirectory(prefix="nbo-r121-transport-") as temporary:
        temp = Path(temporary)
        archive = temp / "payload.zip"
        whole = hashlib.sha256()
        total = 0
        with archive.open("xb") as output:
            for index, row in enumerate(parts):
                declared_identity(row)
                require(row.get("name") == f"payload.zip.part{index:04d}" and 0 < row["bytes"] <= PART_LIMIT,
                        "Part names must be consecutive and at most 8 MiB")
                name = (PurePosixPath(request_name).parent / row["name"]).as_posix()
                path, got = check_bound_file(repo, name, tree)
                matches(got, row)
                part_receipts.append(dict(path=name, **got))
                with path.open("rb") as source:
                    for block in iter(lambda: source.read(CHUNK), b""):
                        output.write(block)
                        whole.update(block)
                        total += len(block)
            output.flush()
            os.fsync(output.fileno())
        matches(dict(bytes=total, sha256=whole.hexdigest()), archive_info)
        # Empty-comment ZIPs, including ZIP64 archives, terminate with the
        # ordinary 22-byte EOCD record. Do not silently accept trailing bytes.
        require(total >= 22, "A ZIP end-of-central-directory record is required")
        with archive.open("rb") as source:
            source.seek(-22, os.SEEK_END)
            ending = source.read(22)
        require(ending[:4] == b"PK\x05\x06" and ending[-2:] == b"\0\0",
                "The ZIP must terminate exactly at its empty-comment EOCD")
        staged = {}
        with zipfile.ZipFile(archive, "r") as zipped:
            infos = zipped.infolist()
            names = [info.filename for info in infos]
            require(len(names) == len(set(names)) == len(declared) and set(names) == set(declared),
                    "ZIP members must exactly equal the declared native file set")
            require(not zipped.comment, "Undeclared ZIP archive comment")
            for index, info in enumerate(infos):
                name = info.filename
                canonical(name)
                row = declared[name]
                mode = info.external_attr >> 16
                require(not info.is_dir() and stat.S_IFMT(mode) in (0, stat.S_IFREG)
                        and not info.flag_bits & 1, "Only unencrypted regular ZIP members are accepted")
                require(info.file_size == row["bytes"], "ZIP member size differs from manifest")
                path = temp / f"member-{index:06d}"
                with zipped.open(info, "r") as source, path.open("xb") as output:
                    length = 0
                    for block in iter(lambda: source.read(CHUNK), b""):
                        length += len(block)
                        require(length <= row["bytes"], "Decompressed member exceeds its declared size")
                        output.write(block)
                    output.flush()
                    os.fsync(output.fileno())
                # Reading each member to EOF above verifies its ZIP CRC.
                got = identity(path)
                matches(got, row, ("bytes", "sha256", "git_blob"))
                native_receipts.append(dict(path=name, **got, zip_crc32=f"{info.CRC:08x}"))
                staged[name] = path
        # Recheck the immutable request, input HEAD and every destination after
        # validation, before materializing any artifact.
        require(git(repo, "rev-parse", "HEAD").decode().strip() == head, "HEAD moved during validation")
        matches(identity(request_path), request_identity, ("bytes", "sha256", "git_blob"))
        for name, source in staged.items():
            destination = local(repo, name)
            if destination.exists():
                require(name in initial_existing and destination.is_file(), "A new destination appeared during validation")
                matches(identity(destination), declared[name], ("bytes", "sha256", "git_blob"))
                continue
            require(name not in initial_existing, "An existing native destination disappeared")
            destination.parent.mkdir(parents=True, exist_ok=True)
            local(repo, name)
            with source.open("rb") as incoming, destination.open("xb") as output:
                shutil.copyfileobj(incoming, output, CHUNK)
                output.flush()
                os.fsync(output.fileno())
            copied.append(name)
            matches(identity(destination), declared[name], ("bytes", "sha256", "git_blob"))
    receipt = dict(kind="nbo-r121-verified-byte-assembly-v1", status="verified_and_materialized",
        transport_commit=head, bundle_id=request["bundle_id"],
        request=dict(path=request_name, **request_identity), archive=archive_info,
        parts=part_receipts, native_files=sorted(native_receipts, key=lambda row: row["path"]),
        requested_file_count=len(declared), new_native_files=len(copied),
        already_identical_native_files=len(initial_existing),
        every_member_read_to_EOF_and_CRC_checked=True,
        every_native_SHA256_and_Git_blob_verified=True,
        original_parts_and_request_retained=True,
        existing_native_bytes_changed=False, native_files_deleted=0,
        scientific_executions=0, scientific_success_claimed=False,
        commit_and_remote_push_performed_by_this_script=False,
        started_utc=started, ended_utc=utc(), elapsed_seconds=time.perf_counter()-clock,
        assembly_source=dict(path=Path(__file__).resolve().relative_to(repo).as_posix(),
                             **identity(Path(__file__).resolve())))
    with receipt_path.open("x", encoding="utf-8") as output:
        json.dump(receipt, output, indent=2, sort_keys=True, allow_nan=False)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    names = sorted(declared) + [receipt_path.relative_to(repo).as_posix()]
    with stage_list.open("xb") as output:
        output.write(b"\0".join(name.encode() for name in names) + b"\0")
        output.flush()
        os.fsync(output.fileno())
    print(json.dumps(dict(status=receipt["status"], transport_commit=head,
          requested_file_count=len(declared), new_native_files=len(copied),
          receipt=receipt_path.relative_to(repo).as_posix(),
          stage_list=str(stage_list), scientific_executions=0), sort_keys=True), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--transport-commit", required=True)
    parser.add_argument("--request", default="auto")
    parser.add_argument("--stage-list", type=Path, required=True)
    assemble(parser.parse_args())


if __name__ == "__main__":
    main()
