"""Classify native R121 bytes and prepare an explicit immutable byte transport.

This unfrozen infrastructure helper never imports the scientific code, runs an
experiment, builds a document, edits native files, changes Git, or uses a
network. Both commands require a fresh staging directory outside native R121.

classify inventories every local native path against a supplied immutable
parent commit. All authored/scientific evidence is retained. Only untracked
Python/tool caches, narrowly declared non-evidence temporary files, the exact
final container's own root outputs, and deferred S/P controls are separated.
Tracked paths are never silently excluded. Build logs, recorders, generated
inputs, raw traces, failures and old transport parts remain in the census.

pack accepts explicit JSON or line-based file lists. It refuses changed files
already present at the supplied parent and rejects new executable files that
the current assembler cannot materialize with their mode. Changed files go
through the separately reviewed direct GitHub write at T. ZIP members follow
the declared mixed or all-stored compression policy, in lexical order with
fixed metadata, and are split into consecutive 8 MiB parts compatible with
assemble_transport121.py. Mixed mode stores .gz/.png/.pdf/.zip files and uses
deflate level 6 for other files, matching the prior public transport rule.
"""
from __future__ import annotations

import argparse
import codecs
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import time
import traceback
import zipfile
import zlib

PREFIX = "revisions/2026-10-20-r121"
PART_BYTES = 8 << 20
CHUNK = 1 << 20
ZIP_DATE = (2026, 10, 20, 0, 0, 0)
STORED_SUFFIXES = {".gz", ".png", ".pdf", ".zip"}
SHA1 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
BUNDLE = re.compile(r"[a-z0-9][a-z0-9._-]{0,95}\Z")
CACHES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
DEFERRED = {
    "EVIDENCE_MANIFEST121.json": "final-author-source-S",
    "SOURCE_READY121.json": "final-author-source-S",
    "SOURCE_PDF_MANIFEST121.json": "post-S-publication-P",
    "AUTHOR_SOURCE_INVENTORY121.json": "post-S-publication-P",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def serializable(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serializable(item) for item in value]
    return value


def canonical(value):
    require(isinstance(value, str) and value, "A nonempty relative POSIX path is required")
    p = PurePosixPath(value)
    require(not p.is_absolute() and str(p) == value and value != "."
            and ".." not in p.parts and "\\" not in value
            and not any(ord(c) < 32 or ord(c) == 127 for c in value),
            "Unsafe or noncanonical path: " + repr(value))
    return value


def native_name(value):
    name = canonical(value)
    if name.startswith(PREFIX + "/"):
        name = name[len(PREFIX) + 1:]
    require(not name.startswith("revisions/"), "A different revision cannot enter this transport")
    return canonical(name)


def local(root, name):
    path = root.joinpath(*PurePosixPath(canonical(name)).parts)
    require(path.resolve().is_relative_to(root), "Input path leaves native R121")
    for item in (path, *path.parents):
        if item == root:
            break
        require(not item.is_symlink(), "Symlink input is forbidden: " + str(path))
    return path


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def decode_json(raw):
    def nonfinite(value):
        raise ValueError("Nonfinite JSON value: " + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=nonfinite)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def signature(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def stream_identity(stream, size, target=None, inspect_text=False):
    sha = hashlib.sha256()
    blob = hashlib.sha1(b"blob " + str(size).encode() + b"\0")
    total = 0
    decoder = codecs.getincrementaldecoder("utf-8")("strict") if inspect_text else None
    text = inspect_text
    for block in iter(lambda: stream.read(CHUNK), b""):
        total += len(block)
        require(total <= size, "Input exceeds its declared size")
        sha.update(block)
        blob.update(block)
        if target is not None:
            target.write(block)
        if text:
            try:
                require(b"\0" not in block, "NUL is not plugin text")
                decoder.decode(block, final=False)
            except (ValueError, UnicodeDecodeError):
                text = False
    require(total == size, "Input is shorter than its declared size")
    if text:
        try:
            decoder.decode(b"", final=True)
        except UnicodeDecodeError:
            text = False
    result = dict(bytes=total, sha256=sha.hexdigest(), git_blob=blob.hexdigest())
    if inspect_text:
        result["utf8_text_without_nul"] = text
    return result


def file_identity(path, target=None, inspect_text=False):
    require(not path.is_symlink(), "A symlink cannot be read as a native file")
    before = path.stat()
    require(stat.S_ISREG(before.st_mode), "A regular native file is required")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as stream:
        require(signature(os.fstat(stream.fileno())) == signature(before), "Input changed before reading")
        result = stream_identity(stream, before.st_size, target, inspect_text)
        require(signature(os.fstat(stream.fileno())) == signature(before), "Input changed during reading")
    require(not path.is_symlink() and signature(path.stat()) == signature(before), "Input was replaced during reading")
    result["git_mode"] = "100755" if before.st_mode & 0o111 else "100644"
    return result


def matches(actual, expected, keys=("bytes", "sha256", "git_blob", "git_mode")):
    for key in keys:
        if key in expected:
            require(actual[key] == expected[key], "Input identity changed: " + key)


def final_container(name):
    return name in {"referee-ready121.zip", "REFEREE_READY_PACKAGE121.json"} or bool(
        re.fullmatch(r"referee-ready121\.zip\.part[0-9]{4,}", name))


def sensitive_evidence(name):
    parts = PurePosixPath(name).parts
    return (any(part.lower().startswith(("results", "provenance", "evidence", "ci121")) for part in parts)
            or any(token in name.lower() for token in ("failure", "failed", "trace", "witness", "execution", "launch", "receipt")))


def explicit_temp_name(name):
    base = PurePosixPath(name).name
    return base == ".DS_Store" or base.endswith((".tmp", ".temp", ".swp", ".swo", "~"))


def compression_type(name, policy):
    return zipfile.ZIP_STORED if policy == "store" or PurePosixPath(name).suffix in STORED_SUFFIXES else zipfile.ZIP_DEFLATED


class Attempt:
    def __init__(self, args):
        self.args = args
        self.repo = args.repository.resolve()
        self.root = self.repo / PREFIX
        self.out = args.output_dir.resolve()
        require(self.root.is_dir(), "Native R121 must exist in the supplied repository")
        require(not self.out.is_relative_to(self.root), "Staging output must be outside native R121")
        self.out.mkdir(parents=True, exist_ok=False)
        self.started, self.clock = utc(), time.perf_counter()
        self.commands = []
        self.record = dict(kind="nbo-r121-transport-preparation-v1", mode=args.mode,
            status="started", started_utc=self.started, arguments=serializable(vars(args)),
            helper=file_identity(Path(__file__).resolve()),
            git_commands=self.commands, scientific_execution=False, scientific_modules_imported=False,
            native_files_changed=False, git_mutation=False, network_access=False)
        write_json(self.out / "START_PREPARATION121.json", self.record)

    def git(self, *args):
        argv = ["git", "-C", str(self.repo), *args]
        row = dict(argv=argv, started_utc=utc(), exit_code=None)
        self.commands.append(row)
        start = time.perf_counter()
        result = subprocess.run(argv, capture_output=True, env=dict(os.environ,
            GIT_NO_LAZY_FETCH="1", GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0"))
        row.update(exit_code=result.returncode, elapsed_seconds=time.perf_counter()-start,
            stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),
            stderr=result.stderr.decode("utf-8", errors="replace"))
        require(result.returncode == 0, "Read-only Git metadata command failed: " + " ".join(args))
        return result.stdout

    def context(self):
        require(Path(self.git("rev-parse", "--show-toplevel").decode().strip()).resolve() == self.repo,
                "--repository must name the actual repository root")
        require(self.git("rev-parse", "--show-object-format").decode().strip() == "sha1", "SHA-1 Git repository required")
        commit = self.args.base_commit
        require(SHA1.fullmatch(commit), "A full immutable parent commit is required")
        require(self.git("rev-parse", "--verify", commit + "^{commit}").decode().strip() == commit,
                "The selected parent must resolve to its exact commit")
        self.head = self.git("rev-parse", "HEAD").decode().strip()
        self.git("merge-base", "--is-ancestor", commit, self.head)
        tree = {}
        for entry in self.git("ls-tree", "-r", "-z", commit, "--", PREFIX + "/").split(b"\0"):
            if not entry:
                continue
            metadata, name = entry.split(b"\t", 1)
            mode, kind, blob = metadata.decode().split()
            name = name.decode("utf-8")
            require(name.startswith(PREFIX + "/") and kind == "blob" and mode in {"100644", "100755"},
                    "Only regular native Git files are supported")
            name = native_name(name)
            require(name not in tree, "Duplicate native parent path")
            tree[name] = dict(git_blob=blob, git_mode=mode)
        require(tree, "The selected parent has no native R121 files")
        self.tree = tree
        self.record.update(base_commit=commit, actual_head=self.head, revision_prefix=PREFIX,
            base_native_files=len(tree), base_native_tree=self.git("rev-parse", commit + ":" + PREFIX).decode().strip())

    def finish(self, status, **fields):
        self.record.update(status=status, ended_utc=utc(), elapsed_seconds=time.perf_counter()-self.clock, **fields)
        write_json(self.out / "PREPARATION121.json", self.record)


def exclusions(path):
    if path is None:
        return {}
    obj = decode_json(path.read_bytes())
    require(obj.get("kind") == "nbo-r121-transient-exclusions-v1" and isinstance(obj.get("files"), list),
            "Explicit transient exclusions require their declared schema")
    result = {}
    for row in obj["files"]:
        name = native_name(row["path"])
        require(name not in result and isinstance(row.get("reason"), str) and row["reason"].strip()
                and row.get("not_authored_or_scientific_evidence") is True,
                "Each transient exclusion needs a unique path and explicit non-evidence declaration")
        require(explicit_temp_name(name) and not sensitive_evidence(name),
                "Temporary exclusions cannot hide scientific evidence or arbitrary authored files: " + name)
        result[name] = row["reason"]
    return result


def classify(attempt):
    attempt.context()
    root, tree = attempt.root, attempt.tree
    declared = exclusions(attempt.args.transient_exclusions)
    require(not set(declared) & set(tree), "A tracked parent file cannot be excluded as temporary")
    rows, seen, blocks = [], set(), []
    def traversal_error(error):
        raise error
    for directory, dirs, files in os.walk(root, topdown=True, followlinks=False, onerror=traversal_error):
        dirs.sort()
        files.sort()
        for name in list(dirs):
            path = Path(directory) / name
            if path.is_symlink():
                dirs.remove(name)
                files.append(name)
        for base in sorted(files):
            path = Path(directory) / base
            name = canonical(path.relative_to(root).as_posix())
            seen.add(name)
            prior = tree.get(name)
            info = path.lstat()
            row = dict(path=name, repository_path=PREFIX + "/" + name, base=prior)
            if not stat.S_ISREG(info.st_mode):
                row.update(disposition="unsupported_local_path", bytes=info.st_size)
                blocks.append(dict(path=name, reason="Symlink or nonregular native path"))
                rows.append(row)
                continue
            reason = None
            if prior is None:
                if any(part in CACHES for part in PurePosixPath(name).parts):
                    reason = "Untracked generated interpreter/tool cache; not authored evidence"
                elif name in declared:
                    reason = declared[name]
                elif final_container(name):
                    reason = "Exact final container root output excluded from its own E0/P input snapshot"
            if reason:
                row.update(disposition="excluded_non_authored_generated", reason=reason, bytes=info.st_size,
                    content_hash_performed=False, original_file_retained=True)
                rows.append(row)
                continue
            actual = file_identity(local(root, name), inspect_text=True)
            row.update(actual)
            if name in DEFERRED:
                row.update(disposition="deferred_control", target_boundary=DEFERRED[name], original_file_retained=True)
                if prior is not None:
                    blocks.append(dict(path=name, reason="E0 parent already contains a deferred S/P control"))
            elif final_container(name):
                row.update(disposition="tracked_final_container_blocker")
                blocks.append(dict(path=name, reason="Tracked final package output cannot be silently removed or included recursively"))
            elif prior is not None and actual["git_blob"] == prior["git_blob"] and actual["git_mode"] == prior["git_mode"]:
                row["disposition"] = "unchanged_tracked"
            elif prior is not None:
                row["disposition"] = "changed_tracked_direct_write"
                row["direct_write_kind"] = "utf8_text" if actual["utf8_text_without_nul"] else "binary_blob"
            elif name.startswith("transport121/"):
                row.update(disposition="new_transport_control_direct_write", original_file_retained=True)
            elif actual["git_mode"] != "100644":
                row.update(disposition="new_executable_direct_write", reason="Current assembler writes new members as regular 100644 files")
            else:
                row["disposition"] = "new_transportable_native"
            rows.append(row)
    for name in sorted(set(tree) - seen):
        rows.append(dict(path=name, repository_path=PREFIX + "/" + name, base=tree[name], disposition="missing_tracked"))
        blocks.append(dict(path=name, reason="A tracked parent path is absent locally; no deletion is authorized"))
    require(set(declared) <= seen, "An explicit transient exclusion does not name an existing native file")
    indexed = {row["path"]: row for row in rows}
    freeze_name = "SOURCE_FREEZE121.json"
    require(freeze_name in indexed and indexed[freeze_name].get("git_blob") == tree.get(freeze_name, {}).get("git_blob"),
            "The native freeze manifest must exactly match the immutable parent")
    frozen = decode_json(local(root, freeze_name).read_bytes())["scientific_files"]
    for name, wanted in frozen.items():
        require(name in indexed and indexed[name].get("sha256") == wanted,
                "Frozen scientific byte changed or missing: " + name)
        require(indexed[name].get("disposition") == "unchanged_tracked", "Frozen scientific path differs from parent: " + name)
    rows.sort(key=lambda row: row["path"])
    counts = {}
    for row in rows:
        counts[row["disposition"]] = counts.get(row["disposition"], 0) + 1
    census = dict(kind="nbo-r121-native-classification-v1", revision_prefix=PREFIX,
        base_commit=attempt.args.base_commit, actual_head=attempt.head, files=rows,
        counts=counts, blockers=blocks, frozen_files_verified=len(frozen),
        native_evidence_excluded_by_extension=False, build_inputs_logs_and_recorders_retained=True,
        scientific_traces_failures_and_existing_transport_parts_retained=True,
        excluded_files_are_not_deleted=True, deferred_controls_are_not_completed_claims=True)
    write_json(attempt.out / "NATIVE_CLASSIFICATION121.json", census)
    include = [dict(path=row["path"], **{key: row[key] for key in ("bytes", "sha256", "git_blob", "git_mode")})
               for row in rows if row["disposition"] == "new_transportable_native"]
    write_json(attempt.out / "TRANSPORT_INCLUDE121.json", dict(kind="nbo-r121-transport-include-v1",
        revision_prefix=PREFIX, base_commit=attempt.args.base_commit, files=include,
        declared_scope="All newly materialized regular native evidence; no changed tracked file or deferred control"))
    direct = [row for row in rows if row["disposition"] in
              {"changed_tracked_direct_write", "new_transport_control_direct_write", "new_executable_direct_write"}]
    write_json(attempt.out / "DIRECT_WRITES121.json", dict(kind="nbo-r121-direct-git-writes-v1",
        base_commit=attempt.args.base_commit, files=direct,
        routing="Publish these exact bytes and Git modes directly before or in T; do not ask assembly to overwrite them"))
    attempt.finish("classified_with_blockers" if blocks else "native_files_classified", counts=counts,
        blockers=blocks, transportable_new_files=len(include), direct_write_files=len(direct),
        scientific_files_verified=len(frozen), large_evidence_packing_performed=False)
    return 2 if blocks else 0


def include_records(attempt):
    rows, sources = {}, []
    def add(row):
        row = dict(path=row) if isinstance(row, str) else dict(row)
        name = native_name(row["path"])
        normalized = dict(path=name)
        for key in ("bytes", "sha256", "git_blob", "git_mode"):
            if key in row:
                normalized[key] = row[key]
        if "bytes" in normalized:
            require(type(normalized["bytes"]) is int and normalized["bytes"] >= 0, "Invalid include byte size")
        for key, pattern in (("sha256", SHA256), ("git_blob", SHA1)):
            if key in normalized:
                require(isinstance(normalized[key], str) and pattern.fullmatch(normalized[key]), "Invalid include digest")
        if "git_mode" in normalized:
            require(normalized["git_mode"] in {"100644", "100755"}, "Invalid include file mode")
        if name in rows:
            matches(normalized, rows[name], tuple(set(normalized) & set(rows[name]) - {"path"}))
            rows[name].update(normalized)
        else:
            rows[name] = normalized
    for path in attempt.args.include_list:
        path = path.resolve()
        raw = path.read_bytes()
        sources.append(dict(path=str(path), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
        if raw.lstrip().startswith((b"{", b"[")):
            data = decode_json(raw)
            if isinstance(data, dict):
                if "revision_prefix" in data:
                    require(data["revision_prefix"] == PREFIX, "Include list names a different revision")
                if "base_commit" in data:
                    require(data["base_commit"] == attempt.args.base_commit, "Include list was classified against a different parent")
                require(("files" in data) != ("paths" in data), "JSON include object requires exactly one files/paths list")
                data = data.get("files", data.get("paths"))
            require(isinstance(data, list), "JSON include list must be a list or files/paths object")
            for row in data:
                add(row)
        else:
            for line in raw.decode("utf-8").splitlines():
                if line and not line.startswith("#"):
                    add(line)
    for name in attempt.args.include:
        add(name)
    require(rows, "An explicit nonempty native file list is required")
    for name in rows:
        require(name not in DEFERRED and not final_container(name) and not name.startswith("transport121/"),
                "Transport cannot contain its controls, final container or deferred S/P bindings")
        require(not any(part in CACHES for part in PurePosixPath(name).parts), "Generated caches are not transport members")
        require(not any(str(parent) in rows for parent in PurePosixPath(name).parents), "File/directory member collision")
    return rows, sources


def pack(attempt):
    attempt.context()
    bundle = attempt.args.bundle_id
    require(BUNDLE.fullmatch(bundle), "A safe fresh bundle id is required")
    bundle_native = "transport121/bundles/" + bundle
    require(not any(name == bundle_native or name.startswith(bundle_native + "/") for name in attempt.tree),
            "Bundle id already exists at the immutable parent")
    require(not (attempt.root / bundle_native).exists(), "Bundle id already exists in the native worktree")
    selected, sources = include_records(attempt)
    bundle_dir = attempt.out / "bundle"
    bundle_dir.mkdir()
    archive = attempt.out / "payload.zip"
    files = []
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as zipped:
        for name, expected in sorted(selected.items()):
            source = local(attempt.root, name)
            prior = attempt.tree.get(name)
            size = source.stat().st_size
            info = zipfile.ZipInfo(PREFIX + "/" + name, ZIP_DATE)
            info.create_system = 3
            info.compress_type = compression_type(name, attempt.args.compression_policy)
            # Python 3.12 exposes the streaming ZipInfo level under this name;
            # ZipFile.writestr(..., compresslevel=6) sets the same field.
            info._compresslevel = 6
            info.external_attr = 0o100644 << 16
            with zipped.open(info, "w", force_zip64=True) as target:
                actual = file_identity(source, target)
            matches(actual, expected)
            require(actual["bytes"] == size, "Native source changed before ZIP write")
            if prior is not None:
                require(actual["git_blob"] == prior["git_blob"] and actual["git_mode"] == prior["git_mode"],
                        "Assembly cannot overwrite a changed parent path: " + name)
            else:
                require(actual["git_mode"] == "100644", "New executable needs a direct Git write: " + name)
            files.append(dict(path=PREFIX + "/" + name, **{key: actual[key] for key in ("bytes", "sha256", "git_blob")}))
    declared = {row["path"]: row for row in files}
    with zipfile.ZipFile(archive, "r") as zipped:
        members = zipped.infolist()
        require(not zipped.comment and [row.filename for row in members] == sorted(declared), "Complete canonical ZIP member order")
        for member in members:
            require(member.compress_type == compression_type(member.filename, attempt.args.compression_policy)
                    and member.date_time == ZIP_DATE
                    and member.create_system == 3 and member.external_attr >> 16 == 0o100644,
                    "Canonical ZIP member metadata")
            with zipped.open(member, "r") as stream:
                matches(stream_identity(stream, member.file_size), declared[member.filename], ("bytes", "sha256", "git_blob"))
    size = archive.stat().st_size
    whole = hashlib.sha256()
    whole_blob = hashlib.sha1(b"blob " + str(size).encode() + b"\0")
    parts, total = [], 0
    with archive.open("rb") as stream:
        for index, block in enumerate(iter(lambda: stream.read(PART_BYTES), b"")):
            name = f"payload.zip.part{index:04d}"
            destination = bundle_dir / name
            with destination.open("xb") as output:
                output.write(block)
                output.flush()
                os.fsync(output.fileno())
            part = file_identity(destination)
            require(part["sha256"] == hashlib.sha256(block).hexdigest(), "Actual part readback differs")
            parts.append(dict(name=name, **{key: part[key] for key in ("bytes", "sha256", "git_blob")}))
            total += len(block)
            whole.update(block)
            whole_blob.update(block)
    require(total == size and parts, "Complete nonempty archive parts")
    with archive.open("rb") as stream:
        stream.seek(-22, os.SEEK_END)
        ending = stream.read(22)
    require(ending[:4] == b"PK\x05\x06" and ending[-2:] == b"\0\0", "Exact empty-comment ZIP EOF")
    request = dict(kind="nbo-r121-byte-transport-v1", bundle_id=bundle, revision_prefix=PREFIX,
        archive=dict(bytes=size, sha256=whole.hexdigest()), parts=parts, files=files,
        preparation_base_commit=attempt.args.base_commit,
        zip_policy=dict(compression_policy=attempt.args.compression_policy,
            stored_suffixes=sorted(STORED_SUFFIXES),
            other_file_deflate_level=6 if attempt.args.compression_policy == "mixed" else None,
            timestamp=list(ZIP_DATE), member_order="lexicographic full repository-relative POSIX path"),
        preparation_scope="Exact selected native bytes; no economic computation, scientific sampling or result selection")
    write_json(bundle_dir / "REQUEST121.json", request)
    request_info = file_identity(bundle_dir / "REQUEST121.json")
    write_json(attempt.out / "UPLOAD_PLAN121.json", dict(kind="nbo-r121-transport-upload-plan-v1",
        preparation_base_commit=attempt.args.base_commit, bundle_repository_directory=PREFIX + "/" + bundle_native,
        request=dict(path=PREFIX + "/" + bundle_native + "/REQUEST121.json", **request_info),
        files=[dict(local_path="bundle/" + row["name"], repository_path=PREFIX + "/" + bundle_native + "/" + row["name"],
                    **{key: row[key] for key in ("bytes", "sha256", "git_blob")}) for row in parts],
        transport_commit_not_created=True, native_materialization_not_performed=True, remote_upload_not_performed=True))
    attempt.finish("deterministic_transport_prepared", bundle_id=bundle, files=len(files),
        native_bytes=sum(row["bytes"] for row in files), archive=dict(bytes=size, sha256=whole.hexdigest(), git_blob=whole_blob.hexdigest()),
        parts=len(parts), include_lists=sources, complete_ZIP_member_bytes_and_CRC_verified=True,
        every_part_readback_verified=True, request=request_info, compression_policy=request["zip_policy"],
        compression_environment=dict(python=sys.version, zlib_compiled=zlib.ZLIB_VERSION,
                                    zlib_runtime=zlib.ZLIB_RUNTIME_VERSION),
        old_parent_paths_included=sum(native_name(row["path"]) in attempt.tree for row in files),
        no_native_source_or_evidence_mutated=True, no_scientific_success_claimed=True)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    for name in ("classify", "pack"):
        sub = commands.add_parser(name)
        sub.add_argument("--repository", type=Path, required=True)
        sub.add_argument("--base-commit", required=True)
        sub.add_argument("--output-dir", type=Path, required=True)
        if name == "classify":
            sub.add_argument("--transient-exclusions", type=Path)
        else:
            sub.add_argument("--bundle-id", required=True)
            sub.add_argument("--compression-policy", choices=("mixed", "store"), default="mixed",
                             help="mixed stores .gz/.png/.pdf/.zip and deflates other files at level 6; store disables compression")
            sub.add_argument("--include-list", action="append", type=Path, default=[])
            sub.add_argument("--include", action="append", default=[], help="Explicit individual native or full repository-relative file; repeatable")
    args = parser.parse_args()
    attempt = Attempt(args)
    try:
        result = classify(attempt) if args.mode == "classify" else pack(attempt)
    except BaseException:
        write_json(attempt.out / "FAILURE_PREPARATION121.json", dict(status="failed", ended_utc=utc(),
            traceback=traceback.format_exc(), all_partial_outputs_retained=True,
            no_scientific_execution=True, no_native_file_mutation=True))
        attempt.finish("failed", all_partial_outputs_retained=True)
        raise
    print(json.dumps({key: attempt.record[key] for key in ("status", "mode", "elapsed_seconds")}), flush=True)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
