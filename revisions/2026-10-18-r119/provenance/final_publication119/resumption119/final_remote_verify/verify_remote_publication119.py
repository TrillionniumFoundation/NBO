#!/usr/bin/env python3
"""Verify published R119 tree identity and historical branch preservation.

Read-only Git and file checks. This does not execute scientific experiments,
rebuild PDFs, or infer that CI ran on the derivative publication commit.
Use a fresh output directory; every observation is copied with its own hash.
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import shutil
import subprocess


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def identities(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "git_sha": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=pathlib.Path, required=True)
    parser.add_argument("--inputs-dir", type=pathlib.Path, required=True)
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()
    start = utc()
    repo, inputs = args.repo.resolve(), args.inputs_dir.resolve()
    native = repo / "revisions/2026-10-18-r119"
    inventory = json.loads((inputs / "FINAL_PUBLICATION_INVENTORY119.json").read_text())
    observation = json.loads((inputs / "REMOTE_PUBLICATION_OBSERVATION119.json").read_text())
    original = json.loads((native / "provenance/branch_inventory.json").read_text())
    pub, parent, source = (observation[k] for k in
                           ("expected_publication", "expected_pdf", "expected_source"))
    failures = []

    def git(*argv):
        return subprocess.check_output(["git", *argv], cwd=repo)

    def tree(commit):
        out = {}
        for entry in git("ls-tree", "-r", "-z", commit, "--", "revisions/2026-10-18-r119").split(b"\0"):
            if not entry:
                continue
            meta, path = entry.split(b"\t")
            mode, kind, sha = meta.decode().split()
            out[path.decode()] = {"mode": mode, "kind": kind, "sha": sha}
        return out

    published, preserved, author = tree(pub), tree(parent), tree(source)
    if git("rev-parse", pub + "^{tree}").decode().strip() != observation["expected_tree"]:
        failures.append("remote tree differs from created tree")
    if observation["commit"]["sha"] != pub or observation["commit"]["tree"]["sha"] != observation["expected_tree"]:
        failures.append("GitHub commit/tree observation mismatch")
    if [x["sha"] for x in observation["commit"]["parents"]] != [parent]:
        failures.append("unexpected publication parent")
    for label, mapping in (("author", author), ("PDF publication", preserved)):
        for path, entry in mapping.items():
            if published.get(path) != entry or identities(repo / path)["git_sha"] != entry["sha"]:
                failures.append(label + " identity changed: " + path)
    planned = {x["path"]: x for x in inventory["inventory"]}
    for path, row in planned.items():
        actual = identities(repo / path)
        if any(actual[k] != row[k] for k in ("bytes", "sha256", "git_sha")):
            failures.append("new local file differs: " + path)
        if published.get(path) != {"mode": "100644", "kind": "blob", "sha": row["git_sha"]}:
            failures.append("new remote Git identity differs: " + path)
    changes = git("diff-tree", "--no-commit-id", "--name-status", "-r", parent, pub).decode().splitlines()
    change_map = dict(line.split("\t", 1)[::-1] for line in changes)
    if change_map != {path: "A" for path in planned}:
        failures.append("repository changes exceed exact planned additions")
    heads = {x["ref"]: x["sha"] for x in observation["heads"]}
    before = {"refs/heads/" + x["branch"]: x["sha"] for x in original["branches"]}
    changed_old = [{"ref": ref, "before": sha, "after": heads.get(ref)}
                   for ref, sha in before.items() if heads.get(ref) != sha]
    added = {ref: sha for ref, sha in heads.items() if ref not in before}
    expected_ref = "refs/heads/" + observation["expected_branch"]
    if changed_old or added != {expected_ref: pub}:
        failures.append("historical branch preservation mismatch")
    manifest = json.loads((native / "REFEREE_READY_PACKAGE119.json").read_text())
    zip_identity = identities(native / "referee-ready119.zip")
    if zip_identity["bytes"] != 180801336 or zip_identity["sha256"] != "86a4f5b26861ba009b6c62fc8b483f492ce8cf8ca10bebac5a29c8a8021dd769":
        failures.append("frozen container identity mismatch")
    pdfs = {name: identities(native / "build" / name) for name in
            ("ECTA.pdf", "supp.pdf", "appendix.pdf", "RESPONSE_TO_REFEREE.pdf")}
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    copied = {}
    for name in ("FINAL_PUBLICATION_INVENTORY119.json", "PUBLICATION_PREFLIGHT119_ATTEMPT01.json",
                 "PUBLICATION_PREFLIGHT119.json", "REMOTE_PUBLICATION_OBSERVATION119.json"):
        shutil.copyfile(inputs / name, output / name)
        copied[name] = identities(output / name)
    shutil.copyfile(pathlib.Path(__file__), output / pathlib.Path(__file__).name)
    copied[pathlib.Path(__file__).name] = identities(output / pathlib.Path(__file__).name)
    record = {"schema": "nbo-r119-final-remote-publication-verification-v1", "started_utc": start,
              "finished_utc": utc(), "status": "passed" if not failures else "failed",
              "repository": "TrillionniumFoundation/NBO", "publication_commit": pub,
              "publication_tree": observation["expected_tree"], "author_source_commit": source,
              "pdf_publication_commit": parent, "author_native_files_preserved": len(author),
              "P_native_files_preserved": len(preserved), "publication_native_files": len(published),
              "new_additions_verified": len(planned), "all_repository_changes_are_planned_additions":
              change_map == {path: "A" for path in planned}, "original_branch_count": len(before),
              "observed_branch_count": len(heads), "original_branches_changed": changed_old,
              "added_branches": added, "pdfs": pdfs, "container": zip_identity,
              "container_manifest": identities(native / "REFEREE_READY_PACKAGE119.json"),
              "copied_input_and_verifier_identities": copied, "failures": failures,
              "scope": "Actual read-only verification of the remotely fetched publication tree, all original branch heads, unchanged S/P native files and exact planned additions. The container's independent 22-part/member verification has separate retained receipts. No new scientific or CI execution is claimed. A subsequent verification-only commit can bind this receipt without changing the verified source, PDFs or container."}
    (output / "REMOTE_PUBLICATION_VERIFICATION119.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
