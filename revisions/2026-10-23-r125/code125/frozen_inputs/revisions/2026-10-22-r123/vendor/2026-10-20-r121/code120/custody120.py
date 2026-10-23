"""Standard-library custody for R120; importing this module evaluates no economy."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


REVISION = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def write_json(path, value):
    """Exclusive immutable record: no failed or completed observation is overwritten."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def append_jsonl(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, sort_keys=True, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def record(path, root):
    path, root = Path(path).resolve(), Path(root).resolve()
    raw = path.read_bytes()
    return dict(path=path.relative_to(root).as_posix(), bytes=len(raw),
                sha256=hashlib.sha256(raw).hexdigest(), git_blob=git_blob(raw))


def repository(revision=REVISION):
    run = subprocess.run(["git", "-C", str(revision), "rev-parse", "--show-toplevel"],
                         check=True, capture_output=True, text=True)
    return Path(run.stdout.strip()).resolve()


def verify_commit_file(path, commit, repo):
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise ValueError("A complete immutable Git commit SHA is required")
    path, repo = Path(path).resolve(), Path(repo).resolve()
    relative = path.relative_to(repo).as_posix()
    run = subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{relative}"],
                         check=True, capture_output=True)
    raw = path.read_bytes()
    if run.stdout != raw:
        raise RuntimeError("Local bytes differ from the immutable commit: " + relative)
    return dict(path=relative, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                git_blob=git_blob(raw), commit=commit)


def verify_source(commit, revision=REVISION):
    """Run before importing scientific dependencies or producing samples."""
    revision = Path(revision).resolve()
    repo = repository(revision)
    manifest = revision / "SOURCE_FREEZE120.json"
    bound = [verify_commit_file(manifest, commit, repo)]
    info = json.loads(manifest.read_text())
    files = info["scientific_files"]
    if not files or "PROTOCOL120.md" not in files:
        raise RuntimeError("The source freeze must include the actual protocol")
    for name, expected in sorted(files.items()):
        path = (revision / name).resolve()
        path.relative_to(revision)
        if digest(path) != expected:
            raise RuntimeError("Source SHA-256 differs: " + name)
        bound.append(verify_commit_file(path, commit, repo))
    return dict(source_commit=commit, source_manifest_sha256=digest(manifest),
                verified_files=bound, verified_before_scientific_import=True)


def manifest_files(root, excluded=()):
    root = Path(root).resolve()
    return [record(path, root) for path in sorted(root.rglob("*"))
            if path.is_file() and path.relative_to(root).as_posix() not in set(excluded)]


def verify_artifacts(root, manifest_name, commit, revision=REVISION):
    root, revision = Path(root).resolve(), Path(revision).resolve()
    repo = repository(revision)
    path = root / manifest_name
    bound = [verify_commit_file(path, commit, repo)]
    info = json.loads(path.read_text())
    for item in info["files"]:
        p = (root / item["path"]).resolve()
        p.relative_to(root)
        got = record(p, root)
        if got != item:
            raise RuntimeError("Frozen artifact identity differs: " + str(p))
        bound.append(verify_commit_file(p, commit, repo))
    return dict(commit=commit, manifest_sha256=digest(path), verified_files=bound)


def exclusive_attempt(path, command, source):
    path = Path(path).resolve()
    path.mkdir(parents=True, exist_ok=False)
    started = dict(status="started", command=command, argv=sys.argv,
                   started_unix=time.time(), source=source,
                   python=sys.version, pid=os.getpid())
    write_json(path / "START120.json", started)
    return path, started
