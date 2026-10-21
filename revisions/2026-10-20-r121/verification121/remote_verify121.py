"""Verify immutable R121 delivery parts without materializing the large ZIP.

Only Python's standard library is used. The caller supplies actual V, S and P
commit identities and independently observed SHA256 values for the package
manifest and virtual chunk descriptor. URLs are restricted to immutable
raw.githubusercontent.com paths at V. A separate explicitly synthetic local
HTTP option exists for small infrastructure fixtures only.

Every 8 MiB part is checked against its declared SHA256/Git blob on every
download. The complete archive is hashed in part order, then all ZIP members
are streamed through CRC, content, mode and S/P-binding checks. The LRU part
cache is at most 32 MiB. No assembled archive, extracted member, economic
evaluation, Git command, remote ancestry assertion or CI-success inference
is produced. Only metadata and verification receipts are written locally.
"""
from __future__ import annotations

import argparse
from collections import OrderedDict
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
import zipfile

PREFIX = "revisions/2026-10-20-r121"
PACKAGE = "REFEREE_READY_PACKAGE121.json"
DESCRIPTOR = "VIRTUAL_ZIP_CHUNKS121.json"
ARCHIVE = "referee-ready121.zip"
SPM = "SOURCE_PDF_MANIFEST121.json"
INVENTORY = "AUTHOR_SOURCE_INVENTORY121.json"
DOCS = ("ECTA", "supp", "appendix", "RESPONSE_TO_REFEREE")
PART_BYTES = 8 << 20
CACHE_LIMIT = 32 << 20
READ_LIMIT = 32 << 20
METADATA_LIMIT = 16 << 20
STREAM_BYTES = 1 << 20
ZIP_DATE = (2026, 10, 20, 0, 0, 0)
SHA1 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def relative(value):
    require(isinstance(value, str) and value and value != ".", "A native relative path is required")
    path = PurePosixPath(value)
    require(not path.is_absolute() and str(path) == value and ".." not in path.parts
            and "\\" not in value and not any(ord(c) < 32 or ord(c) == 127 for c in value),
            "Unsafe or noncanonical native path: " + repr(value))
    return value


def final_output(name):
    return name in {ARCHIVE, PACKAGE} or name.startswith(ARCHIVE + ".part")


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
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def append_json(path, value):
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, sort_keys=True, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def bytes_identity(raw):
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0")
    blob.update(raw)
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), git_blob=blob.hexdigest())


def stream_identity(stream, size):
    sha, blob = hashlib.sha256(), hashlib.sha1(b"blob " + str(size).encode() + b"\0")
    count = 0
    for block in iter(lambda: stream.read(STREAM_BYTES), b""):
        count += len(block)
        require(count <= size, "ZIP member exceeds declared size")
        sha.update(block)
        blob.update(block)
    require(count == size, "ZIP member is shorter than declared size")
    return dict(bytes=count, sha256=sha.hexdigest(), git_blob=blob.hexdigest())


def match(actual, expected, label):
    for key in ("bytes", "sha256", "git_blob"):
        if key in expected:
            require(actual[key] == expected[key], "Mismatch in " + key + ": " + label)


def identity_fields(row, label, mode=False):
    require(isinstance(row, dict) and type(row.get("bytes")) is int and row["bytes"] >= 0,
            "Invalid declared byte size: " + label)
    require(isinstance(row.get("sha256"), str) and SHA256.fullmatch(row["sha256"]),
            "Invalid declared SHA256: " + label)
    require(isinstance(row.get("git_blob"), str) and SHA1.fullmatch(row["git_blob"]),
            "Invalid declared Git blob: " + label)
    if mode:
        require(row.get("git_mode") in {"100644", "100755"}, "Invalid regular Git mode: " + label)


def indexed(rows, label, mode=False):
    require(isinstance(rows, list), "Expected a file record list: " + label)
    result = {}
    for row in rows:
        require(isinstance(row, dict), "Invalid file record: " + label)
        name = relative(row["path"])
        require(name not in result, "Duplicate path in " + label + ": " + name)
        identity_fields(row, label + "/" + name, mode)
        result[name] = row
    return result


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, target):
        raise urllib.error.HTTPError(request.full_url, code, "Redirects are forbidden for immutable raw verification", headers, response)


class Transport:
    def __init__(self, args, output):
        require(REPOSITORY.fullmatch(args.repository), "Repository must be owner/name")
        for name in ("delivery_commit", "source_commit", "publication_commit"):
            require(SHA1.fullmatch(getattr(args, name)), "Full immutable commit required: " + name)
        for name in ("expected_manifest_sha256", "expected_descriptor_sha256"):
            require(SHA256.fullmatch(getattr(args, name)), "Caller-observed complete SHA256 required: " + name)
        require(0 < args.timeout_seconds <= 60, "Per-request timeout must be in (0,60]")
        self.args, self.output = args, output
        self.synthetic = bool(args.synthetic_local_base_url)
        if self.synthetic:
            require(args.allow_synthetic_local_http, "Synthetic local HTTP requires its explicit permission flag")
            parsed = urllib.parse.urlsplit(args.synthetic_local_base_url)
            require(parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}
                    and not parsed.username and not parsed.password and not parsed.query and not parsed.fragment
                    and parsed.path in {"", "/"}, "Only a bare loopback HTTP origin is allowed for synthetic fixtures")
            base = args.synthetic_local_base_url.rstrip("/")
        else:
            require(not args.allow_synthetic_local_http, "Synthetic flag requires an explicit loopback URL")
            base = "https://raw.githubusercontent.com"
        self.base = base + "/" + args.repository + "/" + args.delivery_commit + "/" + PREFIX + "/"
        self.opener = urllib.request.build_opener(NoRedirect())
        self.requests = 0
        self.downloaded_bytes = 0
        self.successful_requests = 0

    def url(self, name):
        return self.base + urllib.parse.quote(relative(name), safe="/")

    def fetch(self, name, expected=None, limit=METADATA_LIMIT, purpose="metadata"):
        relative(name)
        if expected is not None:
            identity_fields(expected, name)
            require(expected["bytes"] <= limit, "Declared remote file exceeds bounded request limit")
            maximum = expected["bytes"]
        else:
            maximum = limit
        url = self.url(name)
        self.requests += 1
        number, started, clock = self.requests, utc(), time.perf_counter()
        headers = {"Accept-Encoding": "identity", "User-Agent": "NBO-R121-immutable-byte-verifier/1"}
        if expected is not None and expected["bytes"]:
            headers["Range"] = "bytes=0-" + str(expected["bytes"]-1)
        row = dict(request=number, event="started", purpose=purpose, path=name, url=url,
            started_utc=started, declared_maximum_bytes=maximum, range=headers.get("Range"),
            synthetic_transport=self.synthetic)
        append_json(self.output / "HTTP_TRANSACTIONS121.jsonl", row)
        try:
            request = urllib.request.Request(url, headers=headers, method="GET")
            with self.opener.open(request, timeout=self.args.timeout_seconds) as response:
                status = response.status
                row.update(http_status=status, final_url=response.geturl(),
                    content_length=response.headers.get("Content-Length"),
                    content_range=response.headers.get("Content-Range"), etag=response.headers.get("ETag"))
                require(response.geturl() == url, "Response URL changed despite immutable-path constraint")
                require(status in {200, 206}, "A successful complete or range response is required")
                encoding = response.headers.get("Content-Encoding")
                require(encoding in {None, "", "identity"}, "Remote bytes must use identity content encoding")
                length = response.headers.get("Content-Length")
                if length is not None:
                    require(length.isdigit() and int(length) <= maximum, "Remote Content-Length exceeds declared bound")
                    if expected is not None:
                        require(int(length) == maximum, "Remote Content-Length differs from declared part size")
                if status == 206:
                    require(expected is not None and maximum > 0
                            and response.headers.get("Content-Range") == f"bytes 0-{maximum-1}/{maximum}",
                            "Unexpected HTTP range coverage")
                payload = response.read(maximum + 1)
                require(len(payload) <= maximum, "Remote response exceeds bounded request")
                require(not response.read(1), "Unexpected remote trailing byte")
                actual = bytes_identity(payload)
                self.downloaded_bytes += actual["bytes"]
                row.update(http_status=status, final_url=response.geturl(), content_length=length,
                    content_range=response.headers.get("Content-Range"), etag=response.headers.get("ETag"), actual=actual)
            if expected is not None:
                match(actual, expected, name)
            self.successful_requests += 1
            row.update(event="verified", ended_utc=utc(), elapsed_seconds=time.perf_counter()-clock)
            append_json(self.output / "HTTP_TRANSACTIONS121.jsonl", row)
            return payload
        except BaseException as error:
            row.update(event="failed", ended_utc=utc(), elapsed_seconds=time.perf_counter()-clock,
                exception_type=type(error).__name__, exception=str(error),
                http_status=getattr(error, "code", row.get("http_status")))
            append_json(self.output / "HTTP_TRANSACTIONS121.jsonl", row)
            raise


class RemoteParts(io.RawIOBase):
    """Seekable immutable ZIP view over verified bounded-size remote parts."""
    def __init__(self, transport, chunks, cache_bytes):
        super().__init__()
        require(0 < cache_bytes <= CACHE_LIMIT, "Part cache may not exceed 32 MiB")
        self.transport, self.chunks, self.limit = transport, chunks, cache_bytes
        self.size = sum(row["bytes"] for row in chunks)
        self.position, self.cache_size, self.peak_cache_bytes = 0, 0, 0
        self.cache, self.hits, self.misses = OrderedDict(), 0, 0
        self.ends = []
        total = 0
        for row in chunks:
            require(0 < row["bytes"] <= cache_bytes, "Each part must fit in the declared cache")
            total += row["bytes"]
            self.ends.append(total)

    def part(self, index):
        require(not self.closed, "Remote ZIP reader is closed")
        if index in self.cache:
            self.hits += 1
            self.cache.move_to_end(index)
            return self.cache[index]
        row = self.chunks[index]
        # Evict before the download, so cached bytes plus the new whole part
        # fit the same stated bound. No chunk is staged on disk.
        while self.cache_size + row["bytes"] > self.limit:
            _, old = self.cache.popitem(last=False)
            self.cache_size -= len(old)
            del old
        self.misses += 1
        raw = self.transport.fetch(row["path"], row, PART_BYTES, "archive-part")
        require(len(raw) == row["bytes"], "Verified part length changed")
        self.cache[index] = raw
        self.cache_size += len(raw)
        self.peak_cache_bytes = max(self.peak_cache_bytes, self.cache_size)
        require(self.cache_size <= self.limit, "Part cache exceeded its bound")
        return raw

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        require(whence in {0, 1, 2}, "Invalid seek origin")
        target = offset + (0 if whence == 0 else self.position if whence == 1 else self.size)
        require(target >= 0, "Negative remote seek")
        self.position = target
        return target

    def read(self, size=-1):
        require(not self.closed, "Remote ZIP reader is closed")
        remaining = max(0, self.size-self.position)
        needed = remaining if size is None or size < 0 else min(size, remaining)
        require(needed <= READ_LIMIT, "A single ZIP read may not materialize the archive")
        result = bytearray()
        while needed:
            # The normal descriptor has fixed 8 MiB parts. A small binary
            # search also supports tiny boundary fixtures without large data.
            lo, hi = 0, len(self.ends)
            while lo < hi:
                mid = (lo+hi)//2
                if self.ends[mid] <= self.position:
                    lo = mid+1
                else:
                    hi = mid
            index = lo
            start = 0 if index == 0 else self.ends[index-1]
            count = min(needed, self.ends[index]-self.position)
            raw = self.part(index)
            offset = self.position-start
            result.extend(memoryview(raw)[offset:offset+count])
            del raw
            self.position += count
            needed -= count
        return bytes(result)

    def close(self):
        self.cache.clear()
        self.cache_size = 0
        super().close()


def validate_metadata(manifest, descriptor, manifest_identity, args):
    require(manifest.get("schema") == "NBO_R121_REFEREE_READY_PACKAGE_V1"
            and manifest.get("archive") == ARCHIVE, "Unexpected package manifest schema")
    require(descriptor.get("schema") == "NBO_R121_VIRTUAL_ZIP_CHUNKS_V1"
            and descriptor.get("archive") == ARCHIVE, "Unexpected virtual chunk descriptor schema")
    require(manifest.get("split_performed") is False and manifest.get("parts") == [],
            "This delivery preserves the original no-split package manifest")
    require(descriptor.get("future_prefix") == "" and descriptor.get("chunk_size") == PART_BYTES,
            "This delivery uses root native 8 MiB virtual ranges")
    for obj in (manifest, descriptor):
        identity_fields(obj, "complete archive")
        require(obj["bytes"] >= 22 and obj["author_source_commit"] == args.source_commit
                and obj["publication_commit"] == args.publication_commit,
                "Caller-selected S/P or complete archive identity differs")
    match(descriptor, manifest, "descriptor complete archive")
    require(descriptor["package_manifest"]["path"] == PACKAGE, "Descriptor names a different package manifest")
    match(manifest_identity, descriptor["package_manifest"], "remote package manifest")
    rows = indexed(manifest["members"], "complete P ZIP members", True)
    require(rows and SPM in rows and INVENTORY in rows and not any(final_output(name) for name in rows),
            "Empty, incomplete or self-referential P ZIP inventory")
    chunks = descriptor["chunks"]
    require(isinstance(chunks, list) and chunks, "Complete nonempty virtual chunk list required")
    offset = 0
    for index, row in enumerate(chunks):
        identity_fields(row, "virtual chunk")
        require(row["path"] == ARCHIVE + ".part" + str(index).zfill(4)
                and type(row.get("offset")) is int and row["offset"] == offset
                and 0 < row["bytes"] <= PART_BYTES
                and (index == len(chunks)-1 or row["bytes"] == PART_BYTES),
                "Virtual chunk path, order, offset or size differs")
        offset += row["bytes"]
    require(offset == manifest["bytes"], "Virtual chunks do not cover the complete archive")
    return rows, chunks


def verify_archive(reader, manifest, output):
    sha = hashlib.sha256()
    blob = hashlib.sha1(b"blob " + str(reader.size).encode() + b"\0")
    total = 0
    for index in range(len(reader.chunks)):
        raw = reader.part(index)
        sha.update(raw)
        blob.update(raw)
        total += len(raw)
        append_json(output / "PART_VERIFICATION121.jsonl", dict(index=index,
            path=reader.chunks[index]["path"], bytes=len(raw), status="verified_in_archive_order"))
        del raw
    actual = dict(bytes=total, sha256=sha.hexdigest(), git_blob=blob.hexdigest())
    match(actual, manifest, "complete sequential remote archive")
    reader.seek(-22, 2)
    ending = reader.read()
    require(ending[:4] == b"PK\x05\x06" and ending[-2:] == b"\0\0", "Exact empty-comment ZIP EOF required")
    reader.seek(0)
    require(reader.read(4) == b"PK\x03\x04", "ZIP must begin with its first local header")
    write_json(output / "ARCHIVE_VERIFICATION121.json", dict(status="verified", **actual,
        remote_parts=len(reader.chunks), assembled_archive_written=False,
        memory_part_cache_limit=reader.limit, every_part_SHA256_and_Git_blob_checked=True))
    return actual


def embedded_json(zipped, name, expected):
    require(expected["bytes"] <= METADATA_LIMIT, "Embedded JSON exceeds bounded metadata size")
    with zipped.open(name, "r") as stream:
        raw = stream.read(METADATA_LIMIT+1)
        require(len(raw) <= METADATA_LIMIT and not stream.read(1), "Embedded JSON exceeds declared bound")
    match(bytes_identity(raw), expected, name)
    return decode_json(raw)


def verify_bindings(zipped, rows, manifest, args):
    bound = embedded_json(zipped, SPM, rows[SPM])
    inventory = embedded_json(zipped, INVENTORY, rows[INVENTORY])
    require(bound.get("schema") == "NBO_R121_SOURCE_PDF_BINDING_V1"
            and inventory.get("schema") == "NBO_R121_AUTHOR_SOURCE_INVENTORY_V1",
            "Unexpected embedded S binding schema")
    require(bound["author_source_commit"] == inventory["author_source_commit"] == args.source_commit,
            "Embedded source identity differs from caller S")
    sid, pid = manifest["author_source_identity"], manifest["publication_identity"]
    require(sid["commit"] == args.source_commit and pid["commit"] == args.publication_commit,
            "Embedded S/P commit identity differs")
    for identity in (sid, pid):
        require(identity["repository_revision_path"] == PREFIX
                and SHA1.fullmatch(identity["repository_tree_sha"])
                and SHA1.fullmatch(identity["native_revision_tree_sha"]), "Complete repository tree/path identities required")
    for key in ("repository_tree_sha", "native_revision_tree_sha", "repository_revision_path"):
        require(bound[key] == inventory[key] == sid[key], "Embedded S tree/path differs: " + key)
    require(manifest["source_pdf_manifest"]["path"] == SPM
            and manifest["source_inventory"]["path"] == bound["source_inventory"]["path"] == INVENTORY,
            "Embedded source/PDF manifest route differs")
    match(rows[SPM], manifest["source_pdf_manifest"], SPM)
    match(rows[INVENTORY], manifest["source_inventory"], INVENTORY)
    match(rows[INVENTORY], bound["source_inventory"], INVENTORY)
    source_rows = indexed(inventory["files"], "embedded S inventory", True)
    require(len(source_rows) == inventory["native_files"] == bound["native_files"]
            == manifest["source_tree_verified_members"], "Complete source file count differs")
    for name, row in source_rows.items():
        require(name in rows and rows[name]["git_mode"] == row["git_mode"],
                "A source file or its mode is omitted from the P archive: " + name)
        match(rows[name], row, "S file at P: " + name)
    source_bytes = sum(row["bytes"] for row in source_rows.values())
    require(source_bytes == inventory["native_bytes"] == bound["native_bytes"], "Complete S byte total differs")
    require(len(rows) == manifest["publication_native_members"]
            and len(rows)-len(source_rows) == manifest["publication_added_members"], "Complete P membership totals differ")
    required = indexed(bound["required_publication_inputs"], "required publication inputs")
    pdfs = indexed(bound["pdfs"], "bound PDFs")
    advertised = indexed(manifest["pdfs"], "advertised PDFs")
    require(set(pdfs) == set(advertised) == {"build/" + doc + ".pdf" for doc in DOCS}
            and set(pdfs) <= set(required), "Exactly four complete bound PDFs are required")
    for group in (required, pdfs, advertised):
        for name, row in group.items():
            require(name in rows, "Missing bound publication file: " + name)
            match(rows[name], row, name)
    for name in manifest.get("root_selected_required_paths", []):
        require(relative(name) in rows, "Missing caller-required P evidence: " + name)
    return dict(source_files=len(source_rows), source_bytes=source_bytes,
        publication_added_files=len(rows)-len(source_rows), required_publication_inputs=len(required),
        native_PDFs=4, caller_selected_source_commit=args.source_commit,
        caller_selected_publication_commit=args.publication_commit,
        Git_ancestry_or_remote_Git_tree_equality_claimed=False)


def verify_members(reader, rows, manifest, args, output):
    seen, total = set(), 0
    with zipfile.ZipFile(reader, "r", allowZip64=True) as zipped:
        require(not zipped.comment, "ZIP archive comment must be empty")
        members = zipped.infolist()
        require([item.filename for item in members] == sorted(rows), "Complete lexically ordered ZIP member set differs")
        for index, member in enumerate(members):
            name = relative(member.filename)
            require(name in rows and name not in seen and not member.is_dir(), "Duplicate or unexpected ZIP member")
            row = rows[name]
            require(member.file_size == row["bytes"] and member.compress_type == zipfile.ZIP_STORED
                    and member.compress_size == member.file_size, "Expected exact ZIP_STORED member: " + name)
            require(not member.flag_bits & 1 and member.date_time == ZIP_DATE
                    and member.create_system == 3 and member.external_attr >> 16 == int(row["git_mode"], 8),
                    "Unexpected ZIP encryption, timestamp or mode: " + name)
            with zipped.open(member, "r") as stream:
                actual = stream_identity(stream, member.file_size)
            match(actual, row, name)
            seen.add(name)
            total += member.file_size
            append_json(output / "MEMBER_VERIFICATION121.jsonl", dict(index=index, path=name,
                status="verified", **actual, git_mode=row["git_mode"], zip_crc32=f"{member.CRC:08x}"))
        require(seen == set(rows), "Missing ZIP members")
        require(len(seen) == manifest["complete_member_readback"]["verified_members"]
                and total == manifest["complete_member_readback"]["verified_uncompressed_bytes"],
                "Declared complete member readback counts differ")
        binding = verify_bindings(zipped, rows, manifest, args)
    return dict(verified_members=len(seen), verified_uncompressed_bytes=total,
        every_member_CRC_SHA256_Git_blob_mode_verified=True, binding=binding)


def run(args):
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    started, clock = utc(), time.perf_counter()
    transport, reader = None, None
    source = bytes_identity(Path(__file__).read_bytes())
    write_json(output / "START_REMOTE_VERIFICATION121.json", dict(kind="nbo-r121-remote-byte-verification-v1",
        status="started", started_utc=started, arguments={key: str(value) if isinstance(value, Path) else value
        for key, value in vars(args).items()}, helper=source, scientific_execution=False,
        Git_mutation=False, assembled_archive_written=False))
    try:
        transport = Transport(args, output)
        manifest_raw = transport.fetch(PACKAGE, purpose="caller-bound-package-manifest")
        manifest_info = bytes_identity(manifest_raw)
        require(manifest_info["sha256"] == args.expected_manifest_sha256, "Observed package manifest SHA256 differs from caller binding")
        descriptor_raw = transport.fetch(DESCRIPTOR, purpose="caller-bound-virtual-descriptor")
        descriptor_info = bytes_identity(descriptor_raw)
        require(descriptor_info["sha256"] == args.expected_descriptor_sha256, "Observed descriptor SHA256 differs from caller binding")
        manifest, descriptor = decode_json(manifest_raw), decode_json(descriptor_raw)
        rows, chunks = validate_metadata(manifest, descriptor, manifest_info, args)
        for name, raw in ((PACKAGE, manifest_raw), (DESCRIPTOR, descriptor_raw)):
            with (output / name).open("xb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
        del manifest_raw, descriptor_raw
        reader = RemoteParts(transport, chunks, args.cache_mib << 20)
        archive = verify_archive(reader, manifest, output)
        members = verify_members(reader, rows, manifest, args, output)
        require(bytes_identity(Path(__file__).read_bytes()) == source, "Executing verifier source changed")
        result = dict(kind="nbo-r121-remote-byte-verification-v1",
            status="passed_synthetic_transport_fixture" if transport.synthetic else "immutable_remote_delivery_bytes_verified",
            repository=args.repository, delivery_commit=args.delivery_commit,
            author_source_commit=args.source_commit, publication_commit=args.publication_commit,
            package_manifest=manifest_info, virtual_descriptor=descriptor_info, archive=archive, **members,
            http_requests=transport.requests, successful_http_requests=transport.successful_requests,
            downloaded_bytes=transport.downloaded_bytes, actual_remote_paths_at_delivery_commit=True,
            synthetic_transport=transport.synthetic, part_cache_limit_bytes=reader.limit,
            peak_cached_part_bytes=reader.peak_cache_bytes, part_cache_hits=reader.hits, part_cache_misses=reader.misses,
            maximum_single_reader_return_bytes=READ_LIMIT,
            started_utc=started, ended_utc=utc(), elapsed_seconds=time.perf_counter()-clock,
            large_archive_or_member_written_to_disk=False, only_metadata_and_receipts_written=True,
            original_scientific_execution=False, scientific_result_correctness_or_CI_success_inferred=False,
            Git_ancestry_or_remote_commit_tree_identity_verified=False,
            verification_scope="Actual immutable URL bytes, full archive/member identities, CRCs and embedded S/P consistency; Git ancestry and actual CI success require separate evidence.")
        write_json(output / "REMOTE_VERIFICATION121.json", result)
        print(json.dumps({key: result[key] for key in ("status", "delivery_commit", "verified_members", "downloaded_bytes", "peak_cached_part_bytes", "elapsed_seconds")}), flush=True)
    except BaseException:
        write_json(output / "FAILURE_REMOTE_VERIFICATION121.json", dict(status="failed", started_utc=started,
            ended_utc=utc(), elapsed_seconds=time.perf_counter()-clock, traceback=traceback.format_exc(),
            http_requests=transport.requests if transport else 0,
            successful_http_requests=transport.successful_requests if transport else 0,
            downloaded_bytes=transport.downloaded_bytes if transport else 0,
            all_actual_request_and_partial_verification_logs_retained=True,
            large_archive_or_member_written_to_disk=False, original_scientific_execution=False))
        raise
    finally:
        if reader is not None:
            reader.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default="TrillionniumFoundation/NBO")
    parser.add_argument("--delivery-commit", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--publication-commit", required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--expected-descriptor-sha256", required=True)
    parser.add_argument("--cache-mib", type=int, choices=(8, 16, 24, 32), default=32)
    parser.add_argument("--timeout-seconds", type=float, default=30)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--synthetic-local-base-url", help="Explicit loopback HTTP origin for bounded synthetic fixtures only")
    parser.add_argument("--allow-synthetic-local-http", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
