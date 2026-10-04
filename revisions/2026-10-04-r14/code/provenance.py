"""Source-aware R14 integration checks; no historical record is relabelled.

The primary and fixed-work studies were executed at different committed
sources. A publication can bind both studies in one tree without claiming
that their computations were performed by the publication commit.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

PRIMARY_SOURCE = "95053e722e57523c1a61c71f2f8bb7a6afbf09a7"
EXTENSION_SOURCE = "c8299feb2a3af0f147295d50036c8d8acca8f65c"
REVIEW_SOURCE = "65110ed2991f4b955d2df37b2ab8635b12df5d1c"
HISTORICAL_TEST_SOURCE = "840565f451be6103aeb325a8fc548a57507a8fb2"
PRIMARY_RELATIVE = Path("revisions/2026-10-04-r12")
EXTENSION_RELATIVE = Path("revisions/2026-10-04-r13")
PUBLICATION_RELATIVE = Path("revisions/2026-10-04-r14")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def write_json(path: Path, value) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def git(repo: Path, *arguments: str) -> bytes:
    return subprocess.check_output(["git", *arguments], cwd=repo)


def source_commit(repo: Path, ref: str) -> str:
    return git(repo, "rev-parse", "--verify", ref + "^{commit}").decode().strip()


def tree_blobs(repo: Path, commit: str) -> dict[str, str]:
    result = {}
    for entry in git(repo, "ls-tree", "-rz", "--full-tree", commit).split(b"\0"):
        if not entry:
            continue
        metadata, name = entry.split(b"\t", 1)
        _, kind, oid = metadata.split()
        if kind == b"blob":
            result[name.decode()] = oid.decode()
    return result


def pinned_sha256(repo: Path, commit: str, paths) -> dict[str, str]:
    """Hash exact Git blobs in one subprocess, rather than trusting HEAD."""
    paths = sorted(set(map(str, paths)))
    entries = tree_blobs(repo, commit)
    missing = [name for name in paths if name not in entries]
    if missing:
        raise AssertionError("paths absent from pinned source: " + repr(missing))
    objects = [entries[name] for name in paths]
    if not objects:
        return {}
    response = subprocess.run(
        ["git", "cat-file", "--batch"],
        input=("\n".join(objects) + "\n").encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=repo,
        check=True,
    ).stdout
    offset = 0
    result = {}
    for name, expected in zip(paths, objects):
        newline = response.index(b"\n", offset)
        oid, kind, length = response[offset:newline].split()
        if oid.decode() != expected or kind != b"blob":
            raise AssertionError("invalid pinned blob response for " + name)
        start = newline + 1
        stop = start + int(length)
        if response[stop : stop + 1] != b"\n":
            raise AssertionError("truncated pinned blob " + name)
        result[name] = hashlib.sha256(response[start:stop]).hexdigest()
        offset = stop + 1
    if offset != len(response):
        raise AssertionError("unexpected data after pinned blobs")
    return result


def check_files(repo: Path, manifest: dict[str, str], label: str) -> None:
    for name, expected in manifest.items():
        path = repo / name
        if not path.is_file() or digest(path) != expected:
            raise AssertionError(label + ": " + name)


def numerical_source_manifest(repo: Path, source: str) -> dict[str, str]:
    """Bind the complete historical Python/protocol dependency pool.

    Worker environment files themselves bind the R12 directory. This adds
    the earlier Python kernels and their protocol files, which the worker
    did not enumerate separately, to the publication's source audit.
    """
    names = tree_blobs(repo, source)
    paths = [
        name
        for name in names
        if name.startswith("revisions/")
        and ("/code/" in name and name.endswith(".py")
             or name.endswith("/PROTOCOL.json"))
    ]
    return pinned_sha256(repo, source, paths)


def primary_preflight(repo: Path) -> dict:
    """Verify completeness and provenance before the numerical replay."""
    root = repo / PRIMARY_RELATIVE
    protocol = json.loads((root / "PROTOCOL.json").read_text())
    pinned = numerical_source_manifest(repo, PRIMARY_SOURCE)
    check_files(repo, pinned, "historical numerical source differs from execution")
    protocol_hash = digest(root / "PROTOCOL.json")
    code = {
        name: value
        for name, value in pinned.items()
        if name.startswith(str(PRIMARY_RELATIVE / "code") + "/")
    }
    expected_shards = set(map(str, protocol["seeds"])) | {"aux", "reference"}
    found_shards = {path.parent.name for path in (root / "results").glob("*/EXECUTION.json")}
    if found_shards != expected_shards:
        raise AssertionError("missing or unexpected primary shards: " + repr(found_shards ^ expected_shards))
    environments = {}
    for shard in sorted(expected_shards):
        directory = root / "results" / shard
        execution = json.loads((directory / "EXECUTION.json").read_text())
        environment = json.loads((directory / "ENVIRONMENT.json").read_text())
        if (execution["source_commit"] != PRIMARY_SOURCE
                or execution["protocol_sha256"] != protocol_hash
                or execution["smoke"] or not execution["all_tasks_completed"]
                or not all(task["success"] for task in execution["tasks"])):
            raise AssertionError("incomplete/different-source primary execution: " + shard)
        if (environment["source_commit"] != PRIMARY_SOURCE
                or environment["protocol_sha256"] != protocol_hash
                or environment["source_files"] != code):
            raise AssertionError("worker source mismatch: " + shard)
        environments[shard] = environment

    rows = {}
    fits = {}
    evaluations = {}
    pairs = {}
    for path in sorted((root / "results").rglob("*.json")):
        row = json.loads(path.read_text())
        name = str(path.relative_to(repo))
        rows[name] = row
        if "source_commit" in row and row["source_commit"] != PRIMARY_SOURCE:
            raise AssertionError("primary record provenance mismatch: " + name)
        if "history" in row and "method" in row:
            fits[name] = row
        elif "bound" in row and "constants" in row and "weights" in row:
            evaluations[name] = row
        elif "bound" in row and "left" in row:
            pairs[name] = row

    expected_fits = {
        (seed, d, method)
        for seed in protocol["seeds"]
        for d in protocol["dimensions"]
        for method in protocol["methods"]
    }
    found_fits = []
    for name, row in fits.items():
        if Path(name).parent.name in set(map(str, protocol["seeds"])) and not row.get("tag"):
            key = (row["seed"], row["dimension"], row["method"])
            found_fits.append(key)
            if row.get("failure") or not row.get("weights_sha256"):
                raise AssertionError("retained primary fitting failure: " + name)
            if row["seed"] != int(Path(name).parent.name):
                raise AssertionError("primary fit in wrong shard: " + name)
    if set(found_fits) != expected_fits or len(found_fits) != len(expected_fits):
        raise AssertionError("the declared primary fit cells are not present exactly once")

    expected_evaluations = {(s, d, m, design) for s, d, m in expected_fits for design in protocol["designs"]}
    found_evaluations = []
    for name, row in evaluations.items():
        if row["steps"] != protocol["final_steps"] or row["paths"] != protocol["final_paths"]:
            raise AssertionError("nonfinal primary evaluation: " + name)
        if row["noise_seed"] != protocol["final_noise_seed"] + row["dimension"]:
            raise AssertionError("different final inference bank: " + name)
        if row["bound"]["family_size"] != protocol["one_sided_family_size"] or row["bound"]["alpha"] != protocol["alpha"]:
            raise AssertionError("different inference allocation: " + name)
        weight = row["weights"]
        matching_fit = fits.get(str(Path(weight).with_suffix(".json")))
        if matching_fit is not None and not matching_fit.get("tag") and Path(name).parent.name in set(map(str, protocol["seeds"])):
            found_evaluations.append((matching_fit["seed"], row["dimension"], row["method"], row["design"]))
    if set(found_evaluations) != expected_evaluations or len(found_evaluations) != len(expected_evaluations):
        raise AssertionError("the declared primary evaluation cells are not present exactly once")

    expected_pairs = {
        (s, d, design, left, right)
        for s in protocol["seeds"]
        for d in protocol["dimensions"]
        for design in protocol["designs"]
        for left, right in protocol["method_contrasts"]
    }
    found_pairs = []
    for name, row in pairs.items():
        left, right = evaluations[row["left"]], evaluations[row["right"]]
        if row["left_raw_sha256"] != left["raw_sha256"] or row["right_raw_sha256"] != right["raw_sha256"]:
            raise AssertionError("paired-input hash reference mismatch: " + name)
        left_fit = fits[str(Path(left["weights"]).with_suffix(".json"))]
        right_fit = fits[str(Path(right["weights"]).with_suffix(".json"))]
        if left_fit["seed"] != right_fit["seed"]:
            raise AssertionError("different fitting streams in paired contrast: " + name)
        found_pairs.append((left_fit["seed"], row["dimension"], row["design"], left["method"], right["method"]))
    if set(found_pairs) != expected_pairs or len(found_pairs) != len(expected_pairs):
        raise AssertionError("the declared direct comparison cells are not present exactly once")

    return {
        "execution_source_commit": PRIMARY_SOURCE,
        "review_commit": REVIEW_SOURCE,
        "protocol_sha256": protocol_hash,
        "numerical_source_files": pinned,
        "worker_environments": environments,
        "complete_primary_fits": len(found_fits),
        "complete_primary_evaluations": len(found_evaluations),
        "complete_primary_pairs": len(found_pairs),
        "scope": "Source and completeness checks; no positive economic outcome is a passing condition.",
    }


def preservation_check(repo: Path, base: str, archive_map: dict[str, str]) -> dict:
    """Keep every base blob at its old path or its explicitly named archive.

    A changed root manuscript is allowed only when its exact old blob has
    been archived. No old numerical source, test assertion or result receives
    an implicit exemption. Run this independently of historical suite replay.
    """
    entries = tree_blobs(repo, base)
    unused = set(archive_map) - set(entries)
    if unused:
        raise AssertionError("archive map contains paths absent from base: " + repr(unused))
    checks = {}
    for name, expected in entries.items():
        target = archive_map.get(name, name)
        path = repo / target
        if not path.is_file():
            raise AssertionError("historical file missing: " + name)
        with path.open("rb") as stream:
            header = b"blob " + str(path.stat().st_size).encode() + b"\0"
            actual = hashlib.sha1(header)
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                actual.update(chunk)
        if actual.hexdigest() != expected:
            raise AssertionError("historical blob not preserved: " + name + " -> " + target)
        checks[name] = {"retained_at": target, "git_blob": expected}
    return {"base_commit": source_commit(repo, base), "files": checks, "all_preserved": True}
