"""Preserve R121 development support bytes without executing scientific code."""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import stat
import sys
import tarfile
import time
import traceback
import zlib

CHUNK = 1 << 20
TAR_EPOCH = 1792454400
ARCHIVE_ROOT = "audit121-experiments"
ARCHIVE_NAME = "DEVELOPMENT_SUPPORT121.tar.gz"
DOCS = ("REMOTE_PUBLICATION_HANDOFF121.md", "REMOTE_PUBLICATION_HANDOFF121.json",
        "FINAL_TRANSPORT_HELPER_HANDOFF121.md")
WORKFLOWS = ("nbo-r121-transport.yml", "nbo-r121-author-package.yml", "nbo-r121-publication.yml")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def json_write(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def stamp(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns, info.st_uid, info.st_gid)


def identity(path):
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode), "Regular file required: " + str(path))
    sha = hashlib.sha256()
    blob = hashlib.sha1(b"blob " + str(before.st_size).encode() + b"\0")
    total = 0
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(fd, "rb") as stream:
        require(stamp(os.fstat(stream.fileno())) == stamp(before), "Input replaced before read")
        for data in iter(lambda: stream.read(CHUNK), b""):
            sha.update(data)
            blob.update(data)
            total += len(data)
        require(stamp(os.fstat(stream.fileno())) == stamp(before), "Input changed during read")
    require(stamp(path.lstat()) == stamp(before) and total == before.st_size, "Input changed after read")
    return dict(bytes=total, sha256=sha.hexdigest(), git_blob=blob.hexdigest())


def safe(name):
    path = PurePosixPath(name)
    require(name and not path.is_absolute() and str(path) == name and ".." not in path.parts
            and "." not in path.parts and "\\" not in name
            and not any(ord(char) < 32 or ord(char) == 127 for char in name),
            "Unsafe archive path: " + repr(name))
    name.encode("utf-8", errors="strict")
    return name


def census(root):
    result = {}

    def visit(path, relative):
        info = path.lstat()
        mode = info.st_mode
        if stat.S_ISREG(mode):
            kind = "regular"
        elif stat.S_ISDIR(mode):
            kind = "directory"
        elif stat.S_ISLNK(mode):
            kind = "symlink"
        else:
            raise ValueError("Unsupported special source entry: " + str(path))
        name = ARCHIVE_ROOT + ("/" + relative if relative else "")
        safe(name)
        row = dict(path=name, source_relative_path=relative or ".", type=kind,
            mode=stat.S_IMODE(mode), mode_octal=format(stat.S_IMODE(mode), "04o"),
            source_lstat_size=info.st_size, source_mtime_ns=info.st_mtime_ns,
            source_ctime_ns=info.st_ctime_ns, source_uid=info.st_uid, source_gid=info.st_gid,
            source_device=info.st_dev, source_inode=info.st_ino,
            source_signature=stamp(info))
        if kind == "symlink":
            target = os.readlink(path)
            target_raw = os.fsencode(target)
            row.update(link_target=target, link_target_bytes=len(target_raw),
                link_target_sha256=hashlib.sha256(target_raw).hexdigest(),
                symlink_target_followed=False)
        result[name] = row
        if kind == "directory":
            with os.scandir(path) as listing:
                names = sorted(entry.name for entry in listing)
            for child in names:
                visit(path / child, relative + "/" + child if relative else child)

    visit(root, "")
    return {name: result[name] for name in sorted(result)}


class HashingReader:
    def __init__(self, stream, expected_size):
        self.stream = stream
        self.count = 0
        self.sha = hashlib.sha256()
        self.blob = hashlib.sha1(b"blob " + str(expected_size).encode() + b"\0")

    def read(self, size):
        data = self.stream.read(size)
        self.count += len(data)
        self.sha.update(data)
        self.blob.update(data)
        return data

    def record(self):
        return dict(bytes=self.count, sha256=self.sha.hexdigest(), git_blob=self.blob.hexdigest())


class HashSink:
    def __init__(self):
        self.sha = hashlib.sha256()
        self.count = 0

    def write(self, data):
        self.sha.update(data)
        self.count += len(data)
        return len(data)

    def tell(self):
        return self.count

    def flush(self):
        pass


def create_archive(root, rows, target, retain_identities):
    with gzip.GzipFile(filename="", mode="wb", compresslevel=9, mtime=0, fileobj=target) as compressed:
        with tarfile.open(mode="w|", fileobj=compressed, format=tarfile.PAX_FORMAT) as archived:
            for name, row in rows.items():
                path = root if row["source_relative_path"] == "." else root / row["source_relative_path"]
                before = path.lstat()
                require(stamp(before) == tuple(row["source_signature"]), "Source changed since census: " + name)
                member = tarfile.TarInfo(name)
                member.mode = row["mode"]
                member.mtime = TAR_EPOCH
                member.uid = member.gid = 0
                member.uname = member.gname = ""
                member.pax_headers = {}
                if row["type"] == "regular":
                    member.type = tarfile.REGTYPE
                    member.size = before.st_size
                    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
                    with os.fdopen(fd, "rb") as source:
                        require(stamp(os.fstat(source.fileno())) == stamp(before), "Regular source replaced")
                        hashed = HashingReader(source, before.st_size)
                        archived.addfile(member, hashed)
                        require(not source.read(1), "Source grew while archived")
                        require(stamp(os.fstat(source.fileno())) == stamp(before), "Regular source changed during archive")
                    result = hashed.record()
                    require(result["bytes"] == before.st_size, "Source length differs from archived bytes")
                else:
                    member.size = 0
                    result = dict(bytes=0, sha256=hashlib.sha256(b"").hexdigest(),
                        git_blob=hashlib.sha1(b"blob 0\0").hexdigest())
                    if row["type"] == "directory":
                        member.type = tarfile.DIRTYPE
                    else:
                        member.type = tarfile.SYMTYPE
                        require(os.readlink(path) == row["link_target"], "Symlink target changed")
                        member.linkname = row["link_target"]
                    archived.addfile(member)
                require(stamp(path.lstat()) == stamp(before), "Source replaced after archiving")
                if retain_identities:
                    row.update(result, sha256_scope="regular file contents" if row["type"] == "regular" else "empty tar member payload")
                else:
                    require(all(result[key] == row[key] for key in result), "Source content differs during deterministic replay")


def verify_archive(path, rows, log):
    seen = set()
    read_bytes = 0
    with path.open("rb") as raw, gzip.GzipFile(mode="rb", fileobj=raw) as uncompressed:
        with tarfile.open(mode="r|", fileobj=uncompressed) as archived:
            for member in archived:
                name = safe(member.name)
                require(name in rows and name not in seen, "Unexpected or duplicate archive member")
                row = rows[name]
                require(member.mode == row["mode"] and member.uid == member.gid == 0
                        and member.uname == member.gname == "" and member.mtime == TAR_EPOCH,
                        "Archive metadata differs from declared normalization")
                expected_type = {"regular":tarfile.REGTYPE, "directory":tarfile.DIRTYPE, "symlink":tarfile.SYMTYPE}[row["type"]]
                require(member.type == expected_type and member.size == row["bytes"], "Archive type/size differs")
                if row["type"] == "regular":
                    stream = archived.extractfile(member)
                    require(stream is not None, "Regular archive payload is missing")
                    hashed = HashingReader(stream, row["bytes"])
                    while hashed.read(CHUNK):
                        pass
                    actual = hashed.record()
                    require(all(actual[key] == row[key] for key in actual), "Full archived member content mismatch")
                    read_bytes += actual["bytes"]
                elif row["type"] == "symlink":
                    require(member.linkname == row["link_target"], "Archived symlink target differs")
                seen.add(name)
                log.write(json.dumps(dict(path=name, type=row["type"], mode=row["mode_octal"],
                    bytes=row["bytes"], sha256=row["sha256"], status="full_member_verified"), sort_keys=True)+"\n")
        # Consume the gzip footer as well as any tar record padding. This
        # performs the gzip CRC/length check without extracting any member.
        padding = 0
        for remaining in iter(lambda: uncompressed.read(CHUNK), b""):
            require(not remaining.strip(b"\0"), "Nonzero data after the tar logical EOF")
            padding += len(remaining)
    require(seen == set(rows), "Archive omitted source entries")
    log.flush()
    os.fsync(log.fileno())
    return dict(verified_members=len(seen), verified_regular_bytes=read_bytes,
        gzip_read_to_EOF_with_CRC_check=True, archive_extraction_performed=False,
        unread_tar_record_padding_consumed=padding)


def copy_exact(source, target, role):
    expected = identity(source)
    before = source.lstat()
    with source.open("rb") as original, target.open("xb") as copied:
        shutil.copyfileobj(original, copied, CHUNK)
        copied.flush()
        os.fsync(copied.fileno())
    require(stamp(source.lstat()) == stamp(before), "Readable copy source changed")
    actual = identity(target)
    require(actual == expected, "Readable copy differs from source")
    return dict(role=role, source_path=str(source), copy_path=str(target), source=expected,
        copied=actual, exact_bytes_equal=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workflow-output", type=Path, required=True)
    args = parser.parse_args()
    source, repo, output, workflow_output = (path.resolve() for path in
        (args.source, args.repository, args.output, args.workflow_output))
    require(source.is_dir() and not source.is_symlink(), "Existing real source directory required")
    require(not output.is_relative_to(source) and not workflow_output.is_relative_to(source),
            "Archival outputs must be outside the source tree")
    require(output.is_relative_to(repo) and workflow_output.is_relative_to(repo),
            "Native repository destinations required")
    require(not output.exists() and not workflow_output.exists(), "Both output directories must be fresh")
    output.mkdir(parents=True)
    workflow_output.mkdir(parents=True)
    started, clock = utc(), time.perf_counter()
    start = dict(kind="nbo-r121-development-support-archive-start-v1", started_utc=started,
        source_directory=str(source), output_directory=str(output), workflow_output_directory=str(workflow_output),
        argv=sys.argv, helper=dict(path=str(Path(__file__).resolve()), **identity(Path(__file__).resolve())),
        scope="Support/development preservation only; no original economic/scientific execution or original science file read.",
        python=sys.version, platform=platform.platform(), zlib_version=zlib.ZLIB_RUNTIME_VERSION,
        subprocess_execution=False, Git_operation=False, network_access=False)
    json_write(output/"START121.json", start)
    try:
        copied_driver = copy_exact(Path(__file__).resolve(), output/"ARCHIVE_SUPPORT121.py", "actual executed preservation source")
        rows = census(source)
        counts = {kind:sum(row["type"] == kind for row in rows.values()) for kind in ("regular", "directory", "symlink")}
        archive_path = output/ARCHIVE_NAME
        with archive_path.open("xb") as archived:
            create_archive(source, rows, archived, True)
            archived.flush()
            os.fsync(archived.fileno())
        archive_identity = identity(archive_path)
        with (output/"MEMBER_VERIFICATION121.jsonl").open("x", encoding="utf-8") as log:
            verified = verify_archive(archive_path, rows, log)
        require(identity(archive_path) == archive_identity, "Archive changed during full verification")
        sink = HashSink()
        create_archive(source, rows, sink, False)
        require(sink.count == archive_identity["bytes"] and sink.sha.hexdigest() == archive_identity["sha256"],
                "Deterministic archive replay bytes differ")
        final_census = census(source)
        require(set(final_census) == set(rows) and all(
            final_census[name]["source_signature"] == rows[name]["source_signature"]
            and final_census[name].get("link_target") == rows[name].get("link_target") for name in rows),
            "Source entries changed or appeared during preservation")
        manifest = dict(kind="nbo-r121-complete-development-support-manifest-v1", source_directory=str(source),
            archive=dict(path=ARCHIVE_NAME, **archive_identity), member_count=len(rows), type_counts=counts,
            regular_bytes=sum(row["bytes"] for row in rows.values() if row["type"] == "regular"),
            members=list(rows.values()), all_source_entries_included=True,
            exclusions=[], nested_synthetic_Git_metadata_retained_inside_archive=True,
            symlink_targets_preserved_without_following=True,
            hardlink_policy="Every regular directory entry is stored with its complete bytes; original device/inode metadata retains hardlink relationships if any.",
            deterministic_tar=dict(format="PAX", member_order="lexical POSIX path", mtime=TAR_EPOCH,
                uid=0, gid=0, uname="", gname="", original_permission_modes_retained=True),
            deterministic_gzip=dict(mtime=0, filename="", compression_level=9),
            original_lstat_metadata_retained_in_manifest=True,
            scope="Development support evidence only; archive construction and readback are not scientific execution.")
        json_write(output/"MANIFEST121.json", manifest)
        copies = [copied_driver]
        for name in DOCS:
            copies.append(copy_exact(source/name, output/name, "plain readable development handoff"))
        json_write(output/"READABLE_COPY_RECEIPT121.json", dict(kind="nbo-r121-development-readable-copy-v1",
            copies=copies, exact_all_bytes_verified=True, scientific_execution=False))
        workflows=[]
        for name in WORKFLOWS:
            workflows.append(copy_exact(repo/".github/workflows"/name, workflow_output/name, "exact authored workflow snapshot"))
        json_write(workflow_output/"WORKFLOW_COPY_RECEIPT121.json", dict(kind="nbo-r121-workflow-source-copy-v1",
            copies=workflows, actual_names_verified=WORKFLOWS, exact_all_bytes_verified=True,
            source_workflows_modified=False, workflow_executed=False))
        result = dict(kind="nbo-r121-development-support-archive-verification-v1", status="complete_archive_and_readable_copies_verified",
            archive=dict(path=ARCHIVE_NAME, **archive_identity), manifest=dict(path="MANIFEST121.json", **identity(output/"MANIFEST121.json")),
            member_verification_log=dict(path="MEMBER_VERIFICATION121.jsonl", **identity(output/"MEMBER_VERIFICATION121.jsonl")),
            counts=counts, complete_source_entries=len(rows), regular_bytes=manifest["regular_bytes"], **verified,
            deterministic_archive_replay=dict(bytes=sink.count, sha256=sink.sha.hexdigest(), exact_bytes_equal=True,
                second_archive_file_created=False), source_census_unchanged=True,
            readable_copies=len(copies)-1, workflow_copies=len(workflows),
            all_failed_attempts_and_source_snapshots_retained=True, nested_synthetic_Git_records_retained=True,
            original_scientific_files_read=False, scientific_execution=False, source_files_modified=False,
            network_access=False, Git_mutation=False, build_or_registry_executed=False,
            started_utc=started, ended_utc=utc(), elapsed_seconds=time.perf_counter()-clock)
        json_write(output/"VERIFICATION121.json", result)
        print(json.dumps({key:result[key] for key in ("status","archive","complete_source_entries","regular_bytes","elapsed_seconds")}),flush=True)
    except BaseException:
        json_write(output/"FAILURE121.json", dict(kind="nbo-r121-development-support-archive-failure-v1",
            status="failed", started_utc=started, ended_utc=utc(), traceback=traceback.format_exc(),
            partial_outputs_retained=True, scientific_execution=False, source_modified=False))
        raise


if __name__ == "__main__":
    main()
