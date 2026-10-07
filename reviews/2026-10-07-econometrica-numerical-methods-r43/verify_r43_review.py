#!/usr/bin/env python3
"""Replay the repository-state checks for the pinned NBO R43 review.

This script uses only the Python standard library and the public GitHub REST
API. It verifies the exact incomplete snapshot reviewed by the referee report;
it does not reconstruct or execute the missing R43 source capsule.

Set GITHUB_TOKEN optionally to avoid anonymous rate limits.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

OWNER = "TrillionniumFoundation"
REPO = "NBO"
BRANCH = "revision/econometrica-nbo-r43-referee-revision-2026-10-07"
EXPECTED_COMMIT = "3c9ad7a969bddf3c79ec5dc07e4b74704fed8615"
EXPECTED_TREE = "4d08baa453265bdaad20d7c0a79033f76c4b9f34"
EXPECTED_PROTOCOL_BLOB = "99eb924c7fbe2d2a2131decf5ac37da7cc9fc5b3"
EXPECTED_ROOTS = {
    "ECTA.tex": ("2bb46996b301e1c0df9d36e258caae06e816483a", "\\input{revisions/2026-10-07-r41/ECTA.tex}\n"),
    "supp.tex": ("3c961995e6a0641d0c3963ab39f43e4e295f95d9", "\\input{revisions/2026-10-07-r41/supp.tex}\n"),
    "README.md": ("2959f121ce9720d9eb6889d09c767173a0460a6f", None),
}
EXPECTED_PARTS = {
    "source-00.b64": ("5adea223ce4ca3b6bf92495dad0a166627a0146b", 12000),
    "source-01.b64": ("b66f6cb55368d62b9df3ab38ca5794f3b1430f47", 12000),
    "source-02.b64": ("4c4da44dd76ffb0166048ed04d3fd1256132d503", 12000),
}
MISSING_PARTS = ["source-03.b64", "source-04.b64"]


def api(path: str) -> Any:
    url = f"https://api.github.com/repos/{OWNER}/{REPO}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "nbo-r43-independent-review-audit",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {exc.code} for {url}: {body}") from exc


def contents(path: str) -> Any:
    encoded = urllib.parse.quote(path, safe="/")
    ref = urllib.parse.quote(BRANCH, safe="")
    return api(f"/contents/{encoded}?ref={ref}")


def decode_file(record: dict[str, Any]) -> str:
    if record.get("type") != "file" or record.get("encoding") != "base64":
        raise AssertionError(f"Unexpected contents record for {record.get('path')}")
    return base64.b64decode(record["content"]).decode("utf-8")


def check_not_found(path: str) -> bool:
    encoded = urllib.parse.quote(path, safe="/")
    ref = urllib.parse.quote(BRANCH, safe="")
    try:
        api(f"/contents/{encoded}?ref={ref}")
    except RuntimeError as exc:
        return "GitHub API 404" in str(exc)
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Write JSON result to this path")
    args = parser.parse_args()

    result: dict[str, Any] = {
        "status": "passed",
        "reviewed_snapshot": {"branch": BRANCH},
        "checks": {},
        "limitations": [
            "This checks the repository snapshot only.",
            "It does not reconstruct the incomplete five-part source capsule.",
            "It does not execute uncommitted R43 diagnostics or simulations.",
        ],
    }

    branch = api(f"/branches/{urllib.parse.quote(BRANCH, safe='')}")
    head = branch["commit"]["sha"]
    assert head == EXPECTED_COMMIT, (head, EXPECTED_COMMIT)
    commit = api(f"/git/commits/{head}")
    tree = commit["tree"]["sha"]
    assert tree == EXPECTED_TREE, (tree, EXPECTED_TREE)
    assert commit["message"].endswith("(3/5)"), commit["message"]
    result["reviewed_snapshot"].update(commit=head, tree=tree, message=commit["message"])

    for path, (expected_sha, expected_text) in EXPECTED_ROOTS.items():
        record = contents(path)
        assert record["sha"] == expected_sha, (path, record["sha"], expected_sha)
        text = decode_file(record)
        if expected_text is not None:
            assert text == expected_text, (path, text)
        if path == "README.md":
            assert text.startswith("# Neural Bellman Operators — R41")
    result["checks"]["root_entrypoints_still_r41"] = True

    r43_listing = contents("revisions/2026-10-07-r43")
    r43_names = sorted(item["name"] for item in r43_listing)
    assert r43_names == ["STUDY_PROTOCOL.md", "publication"], r43_names
    protocol = contents("revisions/2026-10-07-r43/STUDY_PROTOCOL.md")
    assert protocol["sha"] == EXPECTED_PROTOCOL_BLOB
    protocol_text = decode_file(protocol)
    required_protocol_phrases = [
        "R42 success counts remain 6/12 at .04 and 5/6 at .10",
        "post-review diagnostic selected using the already observed allowance decomposition",
        "The primary estimand is J_neural-J_ridge",
        "No equivalence or superiority is inferred from overlap",
    ]
    for phrase in required_protocol_phrases:
        assert phrase in protocol_text, phrase
    result["checks"]["protocol_phrases_verified"] = required_protocol_phrases

    publication = contents("revisions/2026-10-07-r43/publication")
    publication_map = {item["name"]: item for item in publication}
    assert sorted(publication_map) == sorted(EXPECTED_PARTS), sorted(publication_map)
    for name, (expected_sha, expected_size) in EXPECTED_PARTS.items():
        item = publication_map[name]
        assert item["sha"] == expected_sha, (name, item["sha"], expected_sha)
        assert item["size"] == expected_size, (name, item["size"], expected_size)
    result["checks"]["source_parts_present"] = sorted(publication_map)
    result["checks"]["source_parts_missing"] = MISSING_PARTS

    missing_paths = [
        "revisions/2026-10-07-r43/ECTA.tex",
        "revisions/2026-10-07-r43/supp.tex",
        "revisions/2026-10-07-r43/response.md",
        "revisions/2026-10-07-r43/results",
        "revisions/2026-10-07-r43/audit",
        "revisions/2026-10-07-r43/build",
    ]
    for path in missing_paths:
        assert check_not_found(path), path
    result["checks"]["missing_materialized_r43_paths"] = missing_paths

    ref = urllib.parse.quote(BRANCH, safe="")
    runs = api(f"/actions/runs?branch={ref}&per_page=20")
    assert runs["total_count"] == 0, runs["total_count"]
    result["checks"]["workflow_runs"] = 0

    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as stream:
            stream.write(output)
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
