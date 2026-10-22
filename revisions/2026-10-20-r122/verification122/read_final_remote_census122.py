#!/usr/bin/env python3
"""Read-only final remote-head comparison; no scientific or Git-ref mutations."""
import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

REV = Path(__file__).resolve().parents[1]
REPO = REV.parents[1]
BRANCH = "revision/econometrica-nbo-r122-action-information-2026-10-20"
BASELINES = [
    ("provenance122/REMOTE_BRANCH_CENSUS_RECOVERY122.json", "d70814099d3e907cd26a9eafb5c3491276cf72b1b5e7f25f05e07d9679b6cd88"),
    ("provenance122/runtime_recovery/REMOTE_BRANCH_CENSUS122.json", "41c0dcf7a53ed88cc5d41f9b1351b088ac8343aea115fc55cdf023474f206b53"),
    ("provenance122/runtime_recovery_after_upload_reset/REMOTE_BRANCH_CENSUS122.json", "944287a567644d4d2dfbd8d4baa7c28ba9408b678ea6e405b55cc87a023ec82f"),
]


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def normalized_heads(value):
    heads = value["branches"]
    if isinstance(heads, list):
        result = {row["name"]: row["commit"]["sha"] for row in heads}
        if len(result) != len(heads):
            raise ValueError("duplicate baseline branch")
    else:
        result = dict(heads)
    if not result or any(not re.fullmatch(r"[0-9a-f]{40}", v) for v in result.values()):
        raise ValueError("invalid baseline heads")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--output", required=True, help="New JSON receipt below the R122 revision")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.expected_head):
        parser.error("expected head must be a complete lowercase SHA-1")
    output = Path(args.output).resolve()
    if not output.is_relative_to(REV) or output.suffix != ".json":
        parser.error("output must be a new R122 JSON path")
    raw_path = output.with_suffix(".tsv")
    err_path = output.with_suffix(".stderr.log")
    if any(p.exists() for p in (output, raw_path, err_path)):
        parser.error("refusing to overwrite any prior output")
    baselines = []
    for relative, expected_sha in BASELINES:
        data = (REV / relative).read_bytes()
        if sha(data) != expected_sha:
            raise ValueError("baseline bytes differ: " + relative)
        baselines.append((relative, expected_sha, normalized_heads(json.loads(data))))
    output.parent.mkdir(parents=True, exist_ok=True)
    command = ["git", "ls-remote", "--heads", "origin"]
    receipt = {
        "kind": "Final read-only complete remote-head comparison",
        "repository": "TrillionniumFoundation/NBO",
        "source_path": str(Path(__file__).resolve().relative_to(REPO)),
        "source_sha256": sha(Path(__file__).read_bytes()),
        "started_utc": now(), "command": command,
        "expected_branch": BRANCH, "expected_head": args.expected_head,
        "status": "failed", "new_economic_evaluations": 0,
        "git_ref_mutations": 0,
        "scope": "Observed remote heads only. No claim of rereading all historical source, causal attribution of unrelated changes, or inclusion of this post-publication readback in an earlier package ledger.",
    }
    start = time.perf_counter()
    status = 1
    try:
        proc = subprocess.run(command, cwd=REPO, capture_output=True, timeout=60)
        receipt["command_exit_code"] = proc.returncode
        raw_path.write_bytes(proc.stdout)
        err_path.write_bytes(proc.stderr)
        if proc.returncode:
            raise RuntimeError("git ls-remote failed; actual stdout and stderr preserved")
        heads = {}
        for line in proc.stdout.decode("utf-8").splitlines():
            value, name = line.split("\t", 1)
            if not name.startswith("refs/heads/") or not re.fullmatch(r"[0-9a-f]{40}", value):
                raise ValueError("invalid remote head row")
            name = name[len("refs/heads/"):]
            if name in heads:
                raise ValueError("duplicate remote head row")
            heads[name] = value
        if not heads:
            raise ValueError("empty remote census")
        comparisons = []
        for relative, digest, old in baselines:
            added = {k: heads[k] for k in sorted(heads.keys() - old.keys())}
            removed = {k: old[k] for k in sorted(old.keys() - heads.keys())}
            changed = {k: {"old": old[k], "current": heads[k]} for k in sorted(old.keys() & heads.keys()) if old[k] != heads[k]}
            other = (set(added) | set(removed) | set(changed)) - {BRANCH}
            comparisons.append({
                "baseline_path": str((REV / relative).relative_to(REPO)),
                "baseline_sha256": digest, "baseline_count": len(old),
                "added": added, "removed": removed, "changed": changed,
                "all_other_observed_branch_heads_identical": not other,
                "unrelated_difference_names": sorted(other),
            })
        receipt.update({"branches": heads, "head_count": len(heads), "comparisons": comparisons,
                        "expected_branch_head_matches": heads.get(BRANCH) == args.expected_head})
        if heads.get(BRANCH) != args.expected_head:
            raise ValueError("actual final branch head differs from requested publication identity")
        receipt["status"] = "complete_expected_head_verified"
        status = 0
    except Exception as exc:
        if isinstance(exc, subprocess.TimeoutExpired):
            raw_path.write_bytes(exc.stdout or b"")
            err_path.write_bytes(exc.stderr or b"")
        receipt["error_type"] = type(exc).__name__
        receipt["error"] = str(exc)
    finally:
        receipt["elapsed_seconds"] = time.perf_counter() - start
        receipt["ended_utc"] = now()
        receipt["exit_code"] = status
        receipt["cost_clock_components"] = [{
            "category": "source_identity_readback",
            "clock_fields": [["elapsed_seconds"]],
            "overlaps_counted_parent": False,
            "partial_lower_bound_only": True,
            "scope": "This separate final remote census invocation only; if invoked inside a separately charged parent, count only the enclosing parent instead.",
        }]
        receipt["raw_files"] = [{"path": str(p.relative_to(REPO)), "bytes": p.stat().st_size, "sha256": sha(p.read_bytes())} for p in (raw_path, err_path) if p.exists()]
        output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": receipt["status"], "receipt": str(output.relative_to(REPO)), "head_count": receipt.get("head_count"), "elapsed_seconds": receipt["elapsed_seconds"]}, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
