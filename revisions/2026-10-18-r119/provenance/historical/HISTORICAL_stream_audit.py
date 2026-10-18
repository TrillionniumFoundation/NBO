#!/usr/bin/env python3
"""Read immutable historical blobs; never import historical programs or unpickle.

One raw blob is staged, Git/SHA256 verified, parsed by a memory/CPU-limited child,
then deleted. ijson==3.4.0.post0 is the only non-stdlib parser dependency. Parsed
fields describe retained evidence, not independently successful experiments.
"""
from __future__ import annotations

import argparse
import ast
import collections
import csv
import datetime as dt
import decimal
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import re
import resource
import shutil
import sqlite3
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

CHUNK = 65536
JSON_VERSION = "3.4.0.post0"
SIGNATURE = re.compile(r"sha(?:1|256)?|hash|commit|source|freeze|protocol|prereg|"
                       r"status|success|fail|error|traceback|abort|timeout|cancel|"
                       r"conclusion|return.?code|exit.?code|seed|sample|trial|"
                       r"regret|objective|policy|action|bellman|critic|actor|"
                       r"certificate|certified|reject|adopt|cost|elapsed|seconds|"
                       r"wall.?time|budget|tolerance|residual|confidence|coverage|"
                       r"evidence|result|manifest|validation|risk|alpha|beta", re.I)
HEX = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?:[0-9a-f]{24})?(?![0-9a-f])", re.I)
SCIENCE = {".tex", ".py", ".md", ".json"}
RAW = {".npz", ".npy", ".log", ".txt", ".csv", ".tsv", ".jsonl", ".ndjson",
       ".gz", ".zip", ".out", ".stdout", ".stderr", ".pt", ".pth", ".b64"}
TEXT = {".tex", ".py", ".md", ".log", ".txt", ".out", ".stdout", ".stderr",
        ".sh", ".yml", ".yaml", ".bib", ".b64"}


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def dump(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")


def sha_file(path, git=False):
    h = hashlib.sha1() if git else hashlib.sha256()
    if git:
        h.update(f"blob {Path(path).stat().st_size}\0".encode())
    with open(path, "rb") as f:
        for data in iter(lambda: f.read(CHUNK), b""):
            h.update(data)
    return h.hexdigest()


def scalar(v, cap=2048):
    if isinstance(v, decimal.Decimal):
        return {"decimal_exact": str(v)}
    if isinstance(v, str) and len(v) > cap:
        return {"prefix": v[:cap], "characters": len(v), "decoded_utf8_sha256":
                hashlib.sha256(v.encode("utf-8", errors="surrogatepass")).hexdigest(),
                "display_truncated": True}
    return v


class Events:
    def __init__(self, path, cap):
        self.f = gzip.open(path, "wt", encoding="utf-8", compresslevel=6)
        self.cap, self.total, self.kept = cap, 0, 0

    def emit(self, **row):
        self.total += 1
        if self.kept < self.cap:
            self.f.write(json.dumps(row, ensure_ascii=True, allow_nan=False) + "\n")
            self.kept += 1

    def close(self):
        self.f.close()
        return {"matched_events": self.total, "retained_events": self.kept,
                "all_matched_events_retained": self.total == self.kept}


def json_audit(path, events, multiple=False, max_depth=256, max_fields=10000):
    import ijson
    if ijson.__version__ != JSON_VERSION:
        raise RuntimeError(f"required ijson {JSON_VERSION}; found {ijson.__version__}")
    counts, field_counts = collections.Counter(), collections.Counter()
    frames, roots, max_seen, field_overflow = [], 0, 0, 0

    def value_path():
        if not frames:
            return [roots] if multiple else []
        f = frames[-1]
        return f["path"] + [f["key"] if f["kind"] == "map" else f["length"]]

    def finish():
        nonlocal roots
        if frames:
            frames[-1]["length"] += 1
        else:
            roots += 1

    with open(path, "rb") as f:
        for event, value in ijson.basic_parse(f, use_float=False, multiple_values=multiple,
                                             allow_comments=False, buf_size=CHUNK):
            counts[event] += 1
            if event == "map_key":
                if len(value) > 8192:
                    raise ValueError("map key exceeds explicit 8192-character bound")
                frames[-1]["key"] = value
                events.emit(kind="json_key", path=frames[-1]["path"], key=value,
                            member_ordinal=frames[-1]["length"])
                if value in field_counts or len(field_counts) < max_fields:
                    field_counts[value] += 1
                else:
                    field_overflow += 1
            elif event in ("start_map", "start_array"):
                p = value_path()
                frames.append({"kind": event[6:], "path": p, "length": 0, "key": None})
                max_seen = max(max_seen, len(frames))
                if max_seen > max_depth:
                    raise ValueError("JSON nesting exceeds explicit depth bound")
            elif event in ("end_map", "end_array"):
                f = frames.pop()
                if len(f["path"]) <= 2 or any(SIGNATURE.search(str(x)) for x in f["path"] if isinstance(x, str)):
                    events.emit(kind="json_container", path=f["path"], container=f["kind"],
                                members_or_items=f["length"])
                finish()
            else:
                p = value_path()
                matched = len(p) <= 1 or any(SIGNATURE.search(x) for x in p if isinstance(x, str))
                if isinstance(value, str) and HEX.search(value):
                    matched = True
                if matched:
                    events.emit(kind="json_scalar", path=p, value_type=event, value=scalar(value))
                finish()
    if frames or not roots:
        raise ValueError("incomplete or empty JSON document")
    return {"semantic_complete": True, "format": "json_sequence" if multiple else "json",
            "json_roots": roots, "event_counts": dict(counts), "maximum_depth": max_seen,
            "field_occurrences": dict(field_counts), "unretained_new_field_occurrences": field_overflow,
            "field_inventory_complete": field_overflow == 0,
            "all_field_occurrences_emitted": True,
            "parser": {"package": "ijson", "version": ijson.__version__, "backend": ijson.backend,
                       "use_float": False, "allow_comments": False},
            "duplicate_keys": "all SAX occurrences retained by order; no last-value dictionary resolution",
            "dialect": "strict JSON; NaN/Infinity or malformed retained files become explicit parse errors"}


def text_audit(path, events, max_line=8 * 1024 * 1024):
    lines, oversized, invalid = 0, 0, 0
    with open(path, "rb") as f:
        while True:
            data = f.readline(max_line + 1)
            if not data:
                break
            lines += 1
            h, n, prefix = hashlib.sha256(data), len(data), data[:8192]
            too_long = len(data) > max_line and not data.endswith(b"\n")
            if too_long:
                oversized += 1
                while not data.endswith(b"\n"):
                    data = f.readline(CHUNK)
                    if not data:
                        break
                    h.update(data)
                    n += len(data)
            try:
                content = (prefix if too_long else data).decode("utf-8")
            except UnicodeDecodeError:
                invalid += 1
                content = (prefix if too_long else data).decode("utf-8", errors="replace")
            if SIGNATURE.search(content) or HEX.search(content) or too_long:
                events.emit(kind="text_line", line=lines, bytes=n, sha256=h.hexdigest(),
                            prefix=content[:2048], display_truncated=len(content) > 2048 or too_long,
                            signature_scan_complete=not too_long)
    return {"semantic_complete": oversized == 0 and invalid == 0, "format": "text",
            "lines": lines, "oversized_lines": oversized, "invalid_utf8_lines": invalid}


class CSVLines:
    def __init__(self, raw, cap):
        self.raw, self.cap, self.row_bytes = raw, cap, 0

    def __iter__(self):
        return self

    def __next__(self):
        b = self.raw.readline(self.cap + 1)
        if not b:
            raise StopIteration
        self.row_bytes += len(b)
        if self.row_bytes > self.cap:
            raise ValueError("CSV row exceeds explicit byte bound")
        return b.decode("utf-8")


def csv_audit(path, events, delimiter=","):
    csv.field_size_limit(1024 * 1024)
    rows, header, widths, numeric, bounds = 0, [], collections.Counter(), collections.Counter(), {}
    with open(path, "rb") as f:
        lines = CSVLines(f, 16 * 1024 * 1024)
        reader = csv.reader(lines, delimiter=delimiter, strict=True)
        while True:
            lines.row_bytes = 0
            try:
                row = next(reader)
            except StopIteration:
                break
            if len(row) > 4096:
                raise ValueError("CSV column count exceeds explicit bound")
            rows += 1
            widths[len(row)] += 1
            if rows == 1:
                header = [x[:8192] for x in row]
                events.emit(kind="csv_header", values=header)
                continue
            for j, v in enumerate(row):
                name = header[j] if j < len(header) else f"column_{j}"
                try:
                    q = decimal.Decimal(v)
                    if q.is_finite():
                        numeric[j] += 1
                        a, b = bounds.get(j, (q, q))
                        bounds[j] = min(a, q), max(b, q)
                except decimal.InvalidOperation:
                    pass
                if SIGNATURE.search(name) or HEX.search(v):
                    events.emit(kind="csv_field", row=rows, column=j, name=name, value=scalar(v))
    return {"semantic_complete": True, "format": "csv", "rows_including_header": rows,
            "row_width_counts": dict(widths), "header_interpretation": "first row retained as header",
            "numeric_column_counts": dict(numeric),
            "finite_numeric_bounds_exact_decimal": {str(k): [str(a), str(b)] for k, (a, b) in bounds.items()}}


def dtype_info(descr, depth=0):
    if depth > 32:
        raise ValueError("NPY dtype nesting exceeds explicit bound")
    if isinstance(descr, str):
        m = re.fullmatch(r"([<>=|])?([?bBiufcmMOSUV])(\d*)(?:\[[^\]]*\])?", descr)
        if not m:
            return {"object": None, "itemsize": None, "struct": None}
        endian, kind, width = m.groups()
        size = int(width or (1 if kind in "?bB" else 0))
        if kind == "U":
            size *= 4
        fmt = {("b", 1): "b", ("B", 1): "B", ("?", 1): "?",
               ("i", 1): "b", ("i", 2): "h", ("i", 4): "i", ("i", 8): "q",
               ("u", 1): "B", ("u", 2): "H", ("u", 4): "I", ("u", 8): "Q",
               ("f", 2): "e", ("f", 4): "f", ("f", 8): "d"}.get((kind, size))
        return {"object": kind == "O", "itemsize": size or None,
                "struct": ((endian if endian in ("<", ">", "=") else "=") + fmt) if fmt else None}
    if isinstance(descr, list):
        size, obj = 0, False
        for field in descr:
            if not isinstance(field, (tuple, list)) or len(field) not in (2, 3):
                return {"object": None, "itemsize": None, "struct": None}
            q = dtype_info(field[1], depth + 1)
            if q["object"] is True:
                obj = True
            elif q["object"] is None and not obj:
                obj = None
            factor = math.prod(field[2]) if len(field) == 3 and isinstance(field[2], (tuple, list)) else (field[2] if len(field) == 3 else 1)
            if not isinstance(factor, int) or factor < 0 or q["itemsize"] is None:
                size = None
            elif size is not None:
                size += factor * q["itemsize"]
        return {"object": obj, "itemsize": size, "struct": None}
    return {"object": None, "itemsize": None, "struct": None}


class NPYSink:
    def __init__(self):
        self.buf, self.header, self.data_bytes = bytearray(), None, 0
        self.data_hash, self.carry = hashlib.sha256(), b""
        self.number_count, self.finite_count, self.nan_count, self.inf_count = 0, 0, 0, 0
        self.minimum, self.maximum = None, None

    def feed(self, data):
        if self.header is None:
            self.buf.extend(data)
            if len(self.buf) < 8:
                return
            if self.buf[:6] != b"\x93NUMPY":
                raise ValueError("NPY member has invalid magic")
            major, minor = self.buf[6], self.buf[7]
            if (major, minor) not in ((1, 0), (2, 0), (3, 0)):
                raise ValueError("unsupported NPY version")
            nlen = 2 if major == 1 else 4
            if len(self.buf) < 8 + nlen:
                return
            length = int.from_bytes(self.buf[8:8 + nlen], "little")
            if length > 65536:
                raise ValueError("NPY header exceeds explicit 64-KiB bound")
            start = 8 + nlen + length
            if len(self.buf) < start:
                return
            raw = bytes(self.buf[8 + nlen:start])
            h = ast.literal_eval(raw.decode("utf-8" if major == 3 else "latin1").strip())
            if not isinstance(h, dict) or set(h) != {"descr", "fortran_order", "shape"}:
                raise ValueError("NPY header keys invalid")
            if not isinstance(h["shape"], tuple) or len(h["shape"]) > 64 or any(type(x) is not int or x < 0 for x in h["shape"]):
                raise ValueError("NPY shape invalid or exceeds explicit dimension bound")
            if type(h["fortran_order"]) is not bool:
                raise ValueError("NPY fortran_order invalid")
            self.header, self.dtype = h, dtype_info(h["descr"])
            self.version, self.header_sha256 = [major, minor], hashlib.sha256(raw).hexdigest()
            data = bytes(self.buf[start:])
            self.buf = bytearray()
        self.data_bytes += len(data)
        self.data_hash.update(data)
        fmt = self.dtype["struct"]
        if fmt:
            b = self.carry + data
            size = struct.calcsize(fmt)
            stop = len(b) - len(b) % size
            for (v,) in struct.iter_unpack(fmt, b[:stop]):
                self.number_count += 1
                if isinstance(v, float) and math.isnan(v):
                    self.nan_count += 1
                elif isinstance(v, float) and math.isinf(v):
                    self.inf_count += 1
                else:
                    self.finite_count += 1
                    self.minimum = v if self.minimum is None else min(self.minimum, v)
                    self.maximum = v if self.maximum is None else max(self.maximum, v)
            self.carry = b[stop:]

    def result(self):
        if self.header is None:
            raise ValueError("incomplete NPY header")
        elements = math.prod(self.header["shape"])
        expected = elements * self.dtype["itemsize"] if self.dtype["object"] is False and self.dtype["itemsize"] is not None else None
        return {"header": self.header, "version": self.version, "header_sha256": self.header_sha256,
                "array_elements": elements, "data_bytes": self.data_bytes,
                "data_sha256": self.data_hash.hexdigest(), "dtype_interpretation": self.dtype,
                "expected_nonobject_data_bytes": expected,
                "expected_size_matches": self.data_bytes == expected if expected is not None else None,
                "object_payload_policy": "opaque bytes hashed; never unpickled",
                "simple_numeric_statistics": {"available": bool(self.dtype["struct"]),
                    "values": self.number_count, "finite": self.finite_count,
                    "nan": self.nan_count, "infinite": self.inf_count,
                    "minimum": self.minimum, "maximum": self.maximum}}


def zip_preflight(path, max_directory=16 * 1024 * 1024, max_members=65536):
    size = Path(path).stat().st_size
    with open(path, "rb") as f:
        f.seek(max(0, size - 65557))
        tail = f.read(65557)
        p = tail.rfind(b"PK\x05\x06")
        if p < 0 or len(tail) - p < 22:
            raise ValueError("ZIP end-of-central-directory missing")
        e = struct.unpack_from("<4s4H2LH", tail, p)
        count, directory = e[4], e[5]
        if count == 65535 or directory == 0xffffffff or e[6] == 0xffffffff:
            # Refuse an unchecked Zip64 directory allocation. Raw bytes are still verified.
            raise ValueError("Zip64 directory needs separately bounded parser; semantic coverage unresolved")
        if count > max_members or directory > max_directory:
            raise ValueError("ZIP central directory exceeds explicit metadata bound")
    return {"members_declared": count, "central_directory_bytes": directory}


def archive_audit(path, events, expanded_limit):
    meta = zip_preflight(path)
    expanded, count, arrays, opaque_objects, issues = 0, 0, 0, 0, []
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            count += 1
            if info.file_size > expanded_limit - expanded:
                raise ValueError("ZIP expanded byte budget exceeded before member read")
            if info.flag_bits & 1 or info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                raise ValueError("encrypted or non-stored/non-deflate ZIP member not supported")
            h, n = hashlib.sha256(), 0
            sink = NPYSink() if info.filename.lower().endswith(".npy") else None
            with z.open(info) as member:
                for data in iter(lambda: member.read(CHUNK), b""):
                    n += len(data)
                    expanded += len(data)
                    if expanded > expanded_limit:
                        raise ValueError("ZIP expanded byte budget exceeded during member read")
                    h.update(data)
                    if sink:
                        sink.feed(data)
            rec = {"kind": "zip_member", "name": info.filename, "compressed_bytes": info.compress_size,
                   "declared_bytes": info.file_size, "read_bytes": n, "sha256": h.hexdigest(),
                   "crc32_declared": f"{info.CRC:08x}", "crc_checked_by_zipfile": True}
            if sink:
                arrays += 1
                rec["npy"] = sink.result()
                if rec["npy"]["dtype_interpretation"]["object"] is True:
                    opaque_objects += 1
                if rec["npy"]["expected_size_matches"] is False:
                    issues.append({"name": info.filename, "issue": "NPY data size mismatch"})
            events.emit(**rec)
    return {"semantic_complete": not issues, "format": "zip_or_npz", **meta,
            "members_read": count, "npy_members": arrays, "expanded_bytes": expanded,
            "opaque_object_arrays": opaque_objects, "issues": issues,
            "scope": "all member bytes/CRC; NPY headers and simple numeric statistics; no pickle semantics"}


def parse_file(path, suffix, events, expanded_limit):
    with open(path, "rb") as f:
        prefix = f.read(256)
    if prefix.startswith(b"version https://git-lfs.github.com/spec/v1\n"):
        return {"semantic_complete": False, "format": "git_lfs_pointer",
                "pointer": prefix.decode("ascii", errors="replace"),
                "reason": "Git blob is only an LFS pointer; actual payload has not been read"}
    if suffix in (".json", ".jsonl", ".ndjson"):
        return json_audit(path, events, suffix != ".json")
    if suffix in (".npz", ".zip"):
        return archive_audit(path, events, expanded_limit)
    if suffix == ".npy":
        sink = NPYSink()
        with open(path, "rb") as f:
            for data in iter(lambda: f.read(CHUNK), b""):
                sink.feed(data)
        result = sink.result()
        events.emit(kind="npy", **result)
        return {"semantic_complete": result["expected_size_matches"] is not False,
                "format": "npy", "scope": "header/data hash; object data remain opaque"}
    if suffix in (".csv", ".tsv"):
        return csv_audit(path, events, "\t" if suffix == ".tsv" else ",")
    if suffix in TEXT:
        return text_audit(path, events)
    if suffix == ".gz":
        n, h = 0, hashlib.sha256()
        with gzip.open(path, "rb") as f:
            for data in iter(lambda: f.read(CHUNK), b""):
                n += len(data)
                if n > expanded_limit:
                    raise ValueError("gzip expanded byte budget exceeded")
                h.update(data)
        return {"semantic_complete": True, "format": "gzip_opaque_payload", "expanded_bytes": n,
                "expanded_sha256": h.hexdigest(), "scope": "decompressed bytes/CRC only; no nested archive semantics"}
    return {"semantic_complete": True, "format": "opaque_binary",
            "scope": "complete raw blob hash only; no PDF, model, image or pickle interpretation"}


def worker(args):
    memory = args.memory_mib * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    resource.setrlimit(resource.RLIMIT_CPU, (args.cpu_seconds, args.cpu_seconds + 1))
    resource.setrlimit(resource.RLIMIT_FSIZE, (args.output_mib * 1024 * 1024,) * 2)
    begin = time.monotonic()
    events = Events(args.events, args.event_limit)
    result = {"started_utc": utc(), "semantic_complete": False}
    try:
        result.update(parse_file(args.input, args.suffix, events, args.expanded_mib * 1024 * 1024))
    except Exception as e:
        result.update(error_type=type(e).__name__, error=str(e)[:8192])
    finally:
        result.update(events.close())
        if result.get("all_field_occurrences_emitted"):
            result["all_field_occurrences_retained"] = result["all_matched_events_retained"]
        result.update(ended_utc=utc(), elapsed_seconds=time.monotonic() - begin,
                      maximum_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        dump(args.result, result)


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        host = urllib.parse.urlsplit(newurl).hostname
        if host not in {"api.github.com", "raw.githubusercontent.com"}:
            raise urllib.error.URLError("redirect outside approved GitHub content hosts refused")
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if urllib.parse.urlsplit(req.full_url).hostname != host:
            new.remove_header("Authorization")
        return new


def obtain(row, destination, args):
    sha = row["sha"]
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("manifest Git object id is not SHA1")
    cap = args.object_mib * 1024 * 1024
    expected = row.get("bytes", row.get("size"))
    if isinstance(expected, int) and expected > cap:
        raise ValueError("declared object size exceeds per-object disk bound")
    transport = args.transport
    if transport == "auto":
        transport = "local" if row.get("available") and args.local_repo else "github_blob"
    n, h = 0, hashlib.sha256()
    meta = {"transport": transport}
    proc = None
    if transport == "local":
        if not args.local_repo:
            raise ValueError("local transport needs --local-repo")
        env = {**os.environ, "GIT_NO_LAZY_FETCH": "1"}
        proc = subprocess.Popen(["git", "-C", args.local_repo, "cat-file", "blob", sha],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)
        stream = proc.stdout
    else:
        if transport == "github_blob":
            url = f"https://api.github.com/repos/{args.repository}/git/blobs/{sha}"
        else:
            commit, path = row.get("witness_commit"), row.get("witness_path")
            if not commit or not re.fullmatch(r"[0-9a-f]{40}", commit) or not path:
                raise ValueError("raw_commit transport needs immutable representative commit and path")
            url = f"https://raw.githubusercontent.com/{args.repository}/{commit}/{urllib.parse.quote(path, safe='/')}"
        headers = {"User-Agent": "NBO-historical-custody-audit119", "Accept-Encoding": "identity",
                   "Accept": "application/vnd.github.raw+json", "X-GitHub-Api-Version": "2022-11-28"}
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = "Bearer " + token
        request = urllib.request.Request(url, headers=headers)
        opener = urllib.request.build_opener(SafeRedirect())
        stream = opener.open(request, timeout=45)
        meta.update(url=url, http_status=stream.status,
                    rate_remaining=stream.headers.get("X-RateLimit-Remaining"),
                    rate_reset=stream.headers.get("X-RateLimit-Reset"),
                    content_type=stream.headers.get("Content-Type"))
        length = stream.headers.get("Content-Length")
        if length and int(length) > cap:
            stream.close()
            raise ValueError("HTTP object size exceeds per-object disk bound")
    try:
        with stream, open(destination, "wb") as out:
            for data in iter(lambda: stream.read(CHUNK), b""):
                n += len(data)
                if n > cap:
                    raise ValueError("download crossed per-object disk bound")
                out.write(data)
                h.update(data)
        if proc and proc.wait(timeout=15) != 0:
            raise RuntimeError("offline local Git object unavailable")
    finally:
        if proc and proc.poll() is None:
            proc.kill()
            proc.wait()
    actual_sha = sha_file(destination, git=True)
    meta.update(bytes_read=n, sha256=h.hexdigest(), git_blob_sha1=actual_sha,
                git_blob_verified=actual_sha == sha,
                declared_size_matches=(n == expected) if isinstance(expected, int) else None)
    return meta


def read_manifest(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def run(args):
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    records_path = out / "records.jsonl"
    done = set()
    if args.resume and records_path.exists():
        for r in read_manifest(records_path):
            if r.get("git_blob_verified") and r.get("parse", {}).get("semantic_complete"):
                done.add(r["sha"])
    counters = collections.Counter()
    started = utc()
    chosen, selection_sha = 0, hashlib.sha256()
    records = open(records_path, "a" if args.resume else "w", encoding="utf-8")
    event_dir = out / "events"
    event_dir.mkdir(exist_ok=True)
    try:
        for row in read_manifest(args.manifest):
            if int(row["sha"], 16) % args.shard_count != args.shard_index:
                continue
            suffix = row.get("parse_suffix") or Path(row.get("witness_path", "")).suffix.lower()
            if args.suffix and suffix not in args.suffix:
                continue
            chosen += 1
            selection_sha.update((row["sha"] + "\n").encode())
            if row["sha"] in done:
                counters["previously_complete_skipped"] += 1
                continue
            if args.max_objects and counters["attempted"] >= args.max_objects:
                counters["not_attempted_limit"] += 1
                continue
            counters["attempted"] += 1
            begin = time.monotonic()
            rec = {**row, "parse_suffix": suffix, "started_utc": utc()}
            try:
                with tempfile.TemporaryDirectory(prefix="nbo-history119-", dir=args.temp_dir) as tmp:
                    blob = Path(tmp) / "blob"
                    rec.update(obtain(row, blob, args))
                    if not rec["git_blob_verified"] or rec["declared_size_matches"] is False:
                        raise ValueError("download bytes do not match immutable Git blob identity/declared size")
                    counters["raw_verified"] += 1
                    counters["raw_bytes_read"] += rec["bytes_read"]
                    parsed, event_path = Path(tmp) / "parse.json", Path(tmp) / "events.jsonl.gz"
                    command = [sys.executable, str(Path(__file__).resolve()), "_parse", "--input", str(blob),
                               "--suffix", suffix or ".opaque", "--result", str(parsed), "--events", str(event_path),
                               "--memory-mib", str(args.memory_mib), "--cpu-seconds", str(args.cpu_seconds),
                               "--expanded-mib", str(args.expanded_mib), "--event-limit", str(args.event_limit),
                               "--output-mib", str(args.output_mib)]
                    try:
                        cp = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                            timeout=args.wall_seconds, check=False)
                        rec["parser_returncode"] = cp.returncode
                        rec["parser_stderr_prefix"] = cp.stderr[:4096].decode("utf-8", errors="replace")
                    except subprocess.TimeoutExpired:
                        rec["parser_timeout"] = True
                    if parsed.exists() and parsed.stat().st_size <= 16 * 1024 * 1024:
                        rec["parse"] = json.loads(parsed.read_text())
                    else:
                        rec["parse"] = {"semantic_complete": False,
                                        "error": "worker limit/termination or missing result; no completion inferred"}
                    if event_path.exists():
                        dest = event_dir / (row["sha"] + ".jsonl.gz")
                        shutil.copyfile(event_path, dest)
                        rec["events_artifact"] = {"path": str(dest.relative_to(out)),
                                                  "bytes": dest.stat().st_size, "sha256": sha_file(dest)}
                    if rec["parse"].get("semantic_complete"):
                        counters["semantic_complete"] += 1
                    else:
                        counters["semantic_unresolved"] += 1
            except Exception as e:
                rec.update(error_type=type(e).__name__, error=str(e)[:4096])
                counters["transport_or_identity_unresolved"] += 1
            rec.update(ended_utc=utc(), elapsed_seconds=time.monotonic() - begin)
            records.write(json.dumps(rec, ensure_ascii=True, allow_nan=False) + "\n")
            records.flush()
            if counters["attempted"] % 25 == 0:
                print(json.dumps({"at": utc(), "counts": dict(counters)}), flush=True)
    finally:
        records.close()
        unresolved = (counters["not_attempted_limit"] + counters["semantic_unresolved"] +
                      counters["transport_or_identity_unresolved"])
        summary = {"started_utc": started, "ended_utc": utc(), "repository": args.repository,
                   "manifest_sha256": sha_file(args.manifest), "selected_objects": chosen,
                   "selected_sha_order_sha256": selection_sha.hexdigest(), "counts_this_invocation": dict(counters),
                   "selected_scope_complete": unresolved == 0,
                   "script_sha256": sha_file(__file__), "python": sys.version, "platform": platform.platform(),
                   "limits": {k: getattr(args, k) for k in ("object_mib", "memory_mib", "cpu_seconds", "wall_seconds",
                                                             "expanded_mib", "event_limit", "output_mib")},
                   "shard": [args.shard_index, args.shard_count],
                   "scope": "custody/read/parse audit; no historical code executed and no experiment rerun",
                   "coverage_warning": "raw verification, semantic parse, opaque payloads, and field truncation are separate; inspect records"}
        dump(out / "summary.json", summary)
    return 0 if summary["selected_scope_complete"] else 2


def make_manifest(args):
    strict = json.loads(Path(args.priority_sizes).read_text())["records"]
    priority = {r["sha"]: i for i, r in enumerate(strict)}
    sizes = {r["sha"]: r["size"] for r in strict}
    db = sqlite3.connect(f"file:{Path(args.database).resolve()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    # All containing commits are in the index; exclude objects found only in new
    # R119 commits, which were not members of the captured 359 historical heads.
    branches = json.loads(Path(args.branch_inventory).read_text())
    if isinstance(branches, dict):
        branches = branches.get("branches", branches.get("items", branches))
    if not isinstance(branches, list):
        raise ValueError("branch inventory needs its actual list schema; do not guess")
    head_shas = set()
    for b in branches:
        c = b.get("commit", {})
        s = b.get("sha") or (c.get("sha") if isinstance(c, dict) else c)
        if s:
            head_shas.add(s)
    commit_rows = [dict(x) for x in db.execute("select * from commits")]
    columns = set(commit_rows[0])
    bit_key = "bit_index" if "bit_index" in columns else "bit"
    if bit_key not in columns:
        raise ValueError("commit bit-index schema must be supplied explicitly")
    by_sha = {c["sha"]: c for c in commit_rows}
    historical_mask, visited, stack = 0, set(), list(head_shas)
    while stack:
        sha = stack.pop()
        if sha in visited:
            continue
        visited.add(sha)
        c = by_sha.get(sha)
        if c is None:
            raise ValueError("historical commit ancestor missing from frozen index")
        historical_mask |= 1 << c[bit_key]
        stack.extend(json.loads(c["parents_json"]))
    if not historical_mask:
        raise ValueError("no historical branch heads resolved")
    selected = []
    for raw in db.execute("select * from objects where kind in ('blob','missing')"):
        r = dict(raw)
        mask = int(r["commit_mask_hex"], 16)
        if not mask & historical_mask:
            continue
        ext = json.loads(r["extensions"])
        included = sorted(set(ext) & (SCIENCE | RAW))
        if args.scope == "science-raw" and not included:
            continue
        if args.scope == "missing-blobs" and r["available"]:
            continue
        suffix = ".json" if ".json" in included else (Path(r["witness_path"]).suffix.lower() or (included[0] if included else ".opaque"))
        selected.append({"sha": r["sha"], "witness_commit": r["witness_commit"],
                         "witness_path": r["witness_path"], "parse_suffix": suffix,
                         "extension_aliases": ext, "available": bool(r["available"]),
                         "bytes": sizes.get(r["sha"], r["size"]),
                         "priority": 0 if r["sha"] in priority else (1 if suffix == ".json" and not r["available"] else 2),
                         "strict_identity_priority": r["sha"] in priority})
    selected.sort(key=lambda r: (r["priority"], priority.get(r["sha"], 999999), r["sha"]))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        for r in selected:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    counts = collections.Counter(r["parse_suffix"] for r in selected)
    dump(str(output) + ".scope.json", {"objects": len(selected), "formats": dict(counts),
         "missing_json": sum(r["parse_suffix"] == ".json" and not r["available"] for r in selected),
         "strict_identity": sum(r["strict_identity_priority"] for r in selected),
         "manifest_sha256": sha_file(output), "historical_unique_heads": len(head_shas),
         "historical_branch_refs": len(branches), "historical_reachable_commits": len(visited),
         "selection_scope": args.scope})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    q = sub.add_parser("run")
    q.add_argument("--manifest", required=True)
    q.add_argument("--output", required=True)
    q.add_argument("--repository", default="TrillionniumFoundation/NBO")
    q.add_argument("--local-repo")
    q.add_argument("--transport", choices=("auto", "local", "github_blob", "raw_commit"), default="auto")
    q.add_argument("--temp-dir")
    q.add_argument("--resume", action="store_true")
    q.add_argument("--max-objects", type=int, default=0)
    q.add_argument("--shard-count", type=int, default=1)
    q.add_argument("--shard-index", type=int, default=0)
    q.add_argument("--suffix", action="append")
    q.add_argument("--object-mib", type=int, default=128)
    q.add_argument("--wall-seconds", type=int, default=360)
    w = sub.add_parser("_parse")
    for key in ("input", "suffix", "result", "events"):
        w.add_argument("--" + key, required=True)
    for parser in (q, w):
        parser.add_argument("--memory-mib", type=int, default=512)
        parser.add_argument("--cpu-seconds", type=int, default=300)
        parser.add_argument("--expanded-mib", type=int, default=1024)
        parser.add_argument("--event-limit", type=int, default=500000)
        parser.add_argument("--output-mib", type=int, default=128)
    m = sub.add_parser("make-manifest")
    for key in ("database", "priority-sizes", "branch-inventory", "output"):
        m.add_argument("--" + key, required=True)
    m.add_argument("--scope", choices=("science-raw", "all-blobs", "missing-blobs"), default="science-raw")
    a = p.parse_args()
    if a.command == "_parse":
        worker(a)
        return 0
    if a.command == "make-manifest":
        make_manifest(a)
        return 0
    if not 0 <= a.shard_index < a.shard_count or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", a.repository):
        p.error("invalid shard or repository")
    return run(a)


if __name__ == "__main__":
    raise SystemExit(main())
