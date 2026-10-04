"""Source-first activation and complete delivery of the R15 occupation bridge.

This source can be frozen while the primary experiment is still running. A
second branch pointing at the identical source commit activates the 32 jobs
after all primary artifacts exist. Selected weights retain their original fit
source; the new commit identifies the independently randomized assessment.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import gzip
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time


R15 = "revisions/2026-10-04-r15"
PROTOCOL = R15 + "/MECHANISM_PROTOCOL.json"
EXECUTION = R15 + "/MECHANISM_EXECUTION.json"
PRIMARY_PROTOCOL = R15 + "/PROTOCOL.json"
PIPELINE = R15 + "/code/pipeline_mechanism.py"
PRODUCER = R15 + "/code/costate_bridge.py"
REPORT = R15 + "/code/report_mechanism.py"
WORKFLOW = ".github/workflows/nbo-r15-mechanism.yml"
PACKAGES = {"numpy": "2.3.5", "scipy": "1.17.0", "numba": "0.65.1",
            "mpmath": "1.3.0", "torch": "2.10.0+cpu"}
CLOSURE = [
    PROTOCOL, EXECUTION, PRIMARY_PROTOCOL, PIPELINE, PRODUCER, REPORT, WORKFLOW,
    R15 + "/code/test_costate_bridge.py",
    R15 + "/code/training_core.py", R15 + "/code/actor_verifier.py",
    R15 + "/code/baselines.py", R15 + "/code/method_statistics.py",
    "revisions/2026-10-04-r14/code/sensing_diagnostic.py",
    "revisions/2026-10-04-r12/code/common.py",
    "revisions/2026-10-04-r12/code/evaluation.py",
    "revisions/2026-10-04-r12/PROTOCOL.json",
    "revisions/2026-10-04-r11/code/bellman_study.py",
    "revisions/2026-10-04-r11/code/policy_certificate.py",
    "revisions/2026-10-04-r11/code/fast_arithmetic.py",
    "revisions/2026-10-04-r10/code/tube_neural.py",
    "revisions/2026-10-04-r10/code/tube_certificate.py",
    "revisions/2026-09-29-r6/code/interval_certificate.py",
]


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def trials(protocol):
    return [{"trial_id": f"d{d}_s{s}", "dimension": d, "stream_seed": s}
            for d in protocol["dimensions"] for s in protocol["declared_seeds"]]


def source_files(repo):
    repo = Path(repo)
    tests = []
    for pattern in ["test_costate_bridge*.py", "test_*mechanism*.py"]:
        tests.extend(str(p.relative_to(repo)) for p in (repo / R15 / "code").glob(pattern))
    return sorted(set(CLOSURE + tests))


def validate_design(protocol, primary):
    require(protocol["dimensions"] == primary["design"]["dimensions"] == [10, 50], "mechanism dimension mismatch")
    require(protocol["declared_seeds"] == primary["design"]["seeds"]
            and len(set(protocol["declared_seeds"])) == 16, "incomplete registered stream set")
    require(protocol["primitives"] == primary["design"]["primitives"], "mixed mechanism primitives")
    require(digest(canonical(protocol["primitives"])) == protocol["primitives_sha256"]
            == primary["design"]["primitives_sha256"], "mechanism primitive fingerprint mismatch")
    require(protocol["assessment_steps"] == 2048 and protocol["bridges_per_stream"] == 256
            and protocol["pooled_bridges_per_dimension"] == 4096, "registered assessment budget changed")
    require(protocol["future_banks"] == 2 and protocol["rollouts_per_bank"] == 4, "independent future-bank design changed")
    require(protocol["confidence"]["alpha"] == .01 and protocol["confidence"]["event_count"] == 12
            and protocol["confidence"]["sides"] == 2, "registered mechanism confidence family changed")
    require(protocol["statistics"] == ["M", "A", "E", "D", "E_raw", "E_minus_raw"], "assessment statistics changed")


def check(repo):
    repo = Path(repo).resolve()
    p, primary, execution = read(repo / PROTOCOL), read(repo / PRIMARY_PROTOCOL), read(repo / EXECUTION)
    validate_design(p, primary)
    require(re.fullmatch("[0-9a-f]{40}", execution["primary_numerical_source_commit"]), "primary source identity missing")
    require(isinstance(execution["primary_actions_run_id"], int) and execution["primary_actions_run_id"] > 0,
            "primary artifact run must be fixed")
    files = source_files(repo)
    for name in files:
        require((repo / name).is_file(), f"missing mechanism dependency: {name}")
        if name.endswith(".py"):
            ast.parse((repo / name).read_text(), filename=name)
    require(not any("/results/" in name for name in files), "checkpoint data must come from the selected primary artifact, not a duplicate source copy")
    return {"complete": True, "operation": "static mechanism source check; no assessment",
            "files": len(files), "source_bytes": sum((repo / name).stat().st_size for name in files),
            "trials": len(trials(p)), "bridges": len(trials(p)) * p["bridges_per_stream"]}


def pack(repo, out, primary_bundle, source):
    repo, out, primary_bundle = Path(repo).resolve(), Path(out).resolve(), Path(primary_bundle).resolve()
    require(re.fullmatch("[0-9a-f]{40}", source or ""), "immutable mechanism source SHA required")
    require(git(repo, "rev-parse", "HEAD").decode().strip() == source, "mechanism checkout mismatch")
    check(repo)
    p, primary, execution = read(repo / PROTOCOL), read(repo / PRIMARY_PROTOCOL), read(repo / EXECUTION)
    primary_source = execution["primary_numerical_source_commit"]
    git(repo, "merge-base", "--is-ancestor", primary_source, source)
    # The scientific design is the very blob committed before primary outcomes.
    for name in [PROTOCOL, PRIMARY_PROTOCOL]:
        require(git(repo, "show", f"{primary_source}:{name}") == (repo / name).read_bytes(),
                f"the preregistered primary-source design changed: {name}")
    primary_manifest_path = primary_bundle / "SOURCE_MANIFEST.json"
    primary_manifest = read(primary_manifest_path)
    require(primary_manifest["numerical_source_commit"] == primary_source, "downloaded primary source artifact is from another commit")
    require(int(primary_manifest["github_run_id"]) == execution["primary_actions_run_id"], "downloaded primary source artifact is from another run")
    require(primary_manifest["protocol_sha256"] == sha(repo / PRIMARY_PROTOCOL), "primary artifact protocol mismatch")
    for name, facts in primary_manifest["files"].items():
        require(digest(git(repo, "show", f"{primary_source}:{name}")) == facts["sha256"],
                "primary source artifact does not identify its actual Git blobs")
    payload, inventory = {}, {}
    for name in source_files(repo):
        data = git(repo, "show", f"{source}:{name}")
        require(data == (repo / name).read_bytes(), f"uncommitted mechanism dependency: {name}")
        if name in primary_manifest["files"]:
            require(digest(data) == primary_manifest["files"][name]["sha256"],
                    f"a shared primary numerical dependency changed: {name}")
        payload[name] = data
        inventory[name] = {"sha256": digest(data), "bytes": len(data),
                           "git_blob": git(repo, "rev-parse", f"{source}:{name}").decode().strip()}
    environment_contract = {"python": "3.12", "packages": PACKAGES, "platform": "Linux", "numeric_threads": 1}
    fingerprint_input = {"assessment_id": "occupation_bridge", "candidate_method_id": "nbo",
                         "protocol_sha256": inventory[PROTOCOL]["sha256"],
                         "files": {name: f["sha256"] for name, f in inventory.items()},
                         "environment_contract": environment_contract,
                         "candidate_source_commit": primary_source}
    out.mkdir(parents=True, exist_ok=True)
    archive = out / "source.tar.gz"
    with archive.open("wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w", format=tarfile.PAX_FORMAT) as tar:
                for name, data in payload.items():
                    info = tarfile.TarInfo(name)
                    info.size, info.mode, info.mtime = len(data), 0o644, 0
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    tar.addfile(info, io.BytesIO(data))
    manifest = {"record_type": "R15 immutable mechanism numerical source package",
                "numerical_source_commit": source, "candidate_source_commit": primary_source,
                "primary_actions_run_id": execution["primary_actions_run_id"],
                "primary_source_manifest_sha256": sha(primary_manifest_path),
                "primary_protocol_sha256": primary_manifest["protocol_sha256"],
                "candidate_method_fingerprint": primary_manifest["method_fingerprints"]["nbo"]["sha256"],
                "protocol_sha256": inventory[PROTOCOL]["sha256"], "execution": execution,
                "files": inventory, "matrix": {"include": trials(p)},
                "assessment_fingerprint": digest(canonical(fingerprint_input)), "fingerprint_input": fingerprint_input,
                "environment_contract": environment_contract, "archive_sha256": sha(archive),
                "archive_bytes": archive.stat().st_size, "packed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "github_run_id": os.environ.get("GITHUB_RUN_ID"), "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
                "preregistered_design_source_commit": primary_source,
                "preregistered_design_git_blob": git(repo, "rev-parse", f"{primary_source}:{PROTOCOL}").decode().strip()}
    write(out / "SOURCE_MANIFEST.json", manifest)
    shutil.copyfile(primary_manifest_path, out / "PRIMARY_SOURCE_MANIFEST.json")
    (out / "pipeline_mechanism.py").write_bytes(payload[PIPELINE])
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as stream:
            stream.write("matrix=" + canonical(manifest["matrix"]).decode() + "\n")
            stream.write("primary_run_id=" + str(execution["primary_actions_run_id"]) + "\n")
    return {"complete": True, "files": len(inventory), "source": source,
            "archive_bytes": manifest["archive_bytes"], "trials": len(trials(p))}


def extract(bundle, workspace):
    bundle, workspace = Path(bundle).resolve(), Path(workspace).resolve()
    m = read(bundle / "SOURCE_MANIFEST.json")
    require(sha(__file__) == m["files"][PIPELINE]["sha256"], "unbound mechanism launcher")
    require(sha(bundle / "source.tar.gz") == m["archive_sha256"], "mechanism source archive changed")
    require(sha(bundle / "PRIMARY_SOURCE_MANIFEST.json") == m["primary_source_manifest_sha256"], "primary artifact source inventory changed")
    require(digest(canonical(m["fingerprint_input"])) == m["assessment_fingerprint"], "assessment fingerprint mismatch")
    require(not workspace.exists() or not any(workspace.iterdir()), "mechanism source workspace must be empty")
    workspace.mkdir(parents=True, exist_ok=True)
    seen = set()
    with tarfile.open(bundle / "source.tar.gz", "r:gz") as tar:
        for member in tar:
            name = member.name
            require(member.isfile() and name in m["files"] and name not in seen
                    and not PurePosixPath(name).is_absolute() and ".." not in PurePosixPath(name).parts,
                    "unsafe, duplicated or undeclared source member")
            data = tar.extractfile(member).read()
            require(digest(data) == m["files"][name]["sha256"], f"mechanism source digest mismatch: {name}")
            target = workspace / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            seen.add(name)
    require(seen == set(m["files"]), "incomplete mechanism source package")
    check(workspace)
    p = read(workspace / PROTOCOL)
    require(m["matrix"] == {"include": trials(p)}, "mechanism source matrix mismatch")
    return m, p


def environment():
    versions = {name: importlib.metadata.version(name) for name in PACKAGES}
    require(versions == PACKAGES and sys.version_info[:2] == (3, 12) and platform.system() == "Linux",
            "mechanism runtime differs from the frozen CPU environment")
    cpu = None
    if Path("/proc/cpuinfo").exists():
        cpu = next((x.split(":", 1)[1].strip() for x in Path("/proc/cpuinfo").read_text().splitlines()
                    if x.startswith("model name")), None)
    return {"python": sys.version, "packages": versions, "platform": platform.platform(),
            "machine": platform.machine(), "cpu_model": cpu, "logical_cpus": os.cpu_count(),
            "threads": 1, "github_run_id": os.environ.get("GITHUB_RUN_ID"),
            "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT")}


def inventory(folder, exclude=()):
    folder = Path(folder)
    return {str(p.relative_to(folder)): sha(p) for p in sorted(folder.rglob("*"))
            if p.is_file() and str(p.relative_to(folder)) not in exclude}


def primary_candidate(primary_dir, trial, manifest):
    primary_dir = Path(primary_dir).resolve()
    receipt = read(primary_dir / "TRIAL.json")
    require(receipt["complete"] and receipt["trial"]["trial_id"] == trial["trial_id"], "missing or wrong primary trial")
    require(receipt["numerical_source_commit"] == manifest["candidate_source_commit"], "primary trial fit source mismatch")
    nbo = primary_dir / "nbo"
    work, result = read(nbo / "WORK.json"), read(nbo / "RESULT.json")
    row = [r for r in receipt["methods"] if r["method_id"] == "nbo"]
    require(len(row) == 1 and row[0]["work_sha256"] == sha(nbo / "WORK.json"), "primary NBO work receipt mismatch")
    require(work["complete"] and work["files"]["RESULT.json"] == sha(nbo / "RESULT.json") and result["complete"],
            "primary selected NBO stream is incomplete")
    for key, expected in {"method_id": "nbo", "trial_id": trial["trial_id"], "dimension": trial["dimension"],
                          "stream_seed": trial["stream_seed"], "numerical_source_commit": manifest["candidate_source_commit"],
                          "protocol_sha256": manifest["primary_protocol_sha256"],
                          "method_fingerprint": manifest["candidate_method_fingerprint"]}.items():
        require(result[key] == expected, f"primary candidate identity mismatch: {key}")
    name = result["selected_checkpoint"]
    require(Path(name).name == name, "primary selected checkpoint must be a basename")
    checkpoint = nbo / name
    require(sha(checkpoint) == result["selected_checkpoint_sha256"] == work["files"][name], "selected candidate bytes changed")
    proof = {"record_type": "R15 selected primary NBO input receipt", "trial": trial,
             "candidate_source_commit": manifest["candidate_source_commit"],
             "candidate_method_fingerprint": result["method_fingerprint"],
             "candidate_sha256": sha(checkpoint), "candidate_relative_path": name,
             "primary_result_sha256": sha(nbo / "RESULT.json"), "primary_work_sha256": sha(nbo / "WORK.json"),
             "primary_trial_receipt_sha256": sha(primary_dir / "TRIAL.json"),
             "primary_actions_run_id": manifest["primary_actions_run_id"], "fallback": result["fallback"],
             "primary_work_seconds": work["end_to_end_seconds"],
             "work_scope": "Primary method work is retained as historical input provenance and is not charged again to this separate mechanism assessment."}
    return checkpoint, proof


def validate_result(folder, trial, manifest, proof):
    folder = Path(folder)
    r = read(folder / "BRIDGE.json")
    require(r["complete"] and r["trial_id"] == trial["trial_id"], "mechanism trial is incomplete")
    for key, expected in {"dimension": trial["dimension"], "stream_seed": trial["stream_seed"],
                          "numerical_source_commit": manifest["numerical_source_commit"],
                          "candidate_source_commit": manifest["candidate_source_commit"],
                          "candidate_sha256": proof["candidate_sha256"],
                          "protocol_sha256": manifest["protocol_sha256"],
                          "assessment_fingerprint": manifest["assessment_fingerprint"]}.items():
        require(r[key] == expected, f"mechanism result identity mismatch: {key}")
    raw = r["raw_path"]
    require(Path(raw).name == raw and sha(folder / raw) == r["raw_sha256"], "mechanism raw vector digest mismatch")
    return r


def run(bundle, workspace, primary_dir, out, trial_id):
    m, p = extract(bundle, workspace)
    matches = [t for t in trials(p) if t["trial_id"] == trial_id]
    require(len(matches) == 1, "unknown mechanism trial")
    trial = matches[0]
    checkpoint, proof = primary_candidate(primary_dir, trial, m)
    workspace, out = Path(workspace).resolve(), Path(out).resolve()
    require(not out.exists(), "refusing to overwrite a mechanism execution")
    out.mkdir(parents=True)
    write(out / "INPUT_MANIFEST.json", proof)
    actual = environment()
    env = dict(os.environ)
    env.update({"NBO_R15_NUMERICAL_SOURCE_COMMIT": m["numerical_source_commit"],
                "NBO_R15_ASSESSMENT_FINGERPRINT": m["assessment_fingerprint"],
                "NBO_R15_SOURCE_COMMIT": m["numerical_source_commit"],
                "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                "NUMBA_NUM_THREADS": "1", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"})
    command = [sys.executable, str(workspace / PRODUCER), "--protocol", str(workspace / PROTOCOL),
               "--checkpoint", str(checkpoint), "--trial-id", trial_id, "--out", str(out)]
    work = {"record_type": "R15 full independent mechanism-assessment work", "complete": False,
            "trial": trial, "method_id": "nbo", "assessment_id": "occupation_bridge",
            "numerical_source_commit": m["numerical_source_commit"], "candidate_source_commit": m["candidate_source_commit"],
            "protocol_sha256": m["protocol_sha256"], "assessment_fingerprint": m["assessment_fingerprint"],
            "environment": actual, "environment_fingerprint": digest(canonical(actual)),
            "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "timing_scope": "fresh process launch through exit: imports, selected-weight loading, all protected constants, candidate occupation paths, both future banks, interval arithmetic and final raw/JSON I/O",
            "work_scope": "Separate post-selection scientific assessment; excluded from every primary method's work-to-target clock and reported additionally for the complete study."}
    with tempfile.TemporaryDirectory(prefix="nbo-r15-mechanism-numba-") as cache:
        env["NUMBA_CACHE_DIR"] = cache
        with (out / "process.log").open("wb") as log:
            beginning = time.perf_counter_ns()
            process = subprocess.Popen(command, cwd=workspace, env=env, stdout=log, stderr=subprocess.STDOUT)
            _, status, usage = os.wait4(process.pid, 0)
            end = time.perf_counter_ns()
            process.returncode = os.waitstatus_to_exitcode(status)
        work.update(end_to_end_seconds=(end-beginning)/1e9, returncode=process.returncode,
                    peak_rss_kib=int(usage.ru_maxrss), user_cpu_seconds=usage.ru_utime,
                    system_cpu_seconds=usage.ru_stime, cpu_seconds=usage.ru_utime+usage.ru_stime)
    try:
        require(process.returncode == 0, f"mechanism producer exited with status {process.returncode}")
        validate_result(out, trial, m, proof)
        require(sha(checkpoint) == proof["candidate_sha256"], "mechanism changed the selected primary weights")
        for name, facts in m["files"].items():
            require(sha(workspace / name) == facts["sha256"], f"assessment changed a source input: {name}")
        work["complete"] = True
    except Exception as exc:
        work["failure"] = str(exc)
    work["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    work["files"] = inventory(out, exclude=["WORK.json"])
    write(out / "WORK.json", work)
    require(work["complete"], "mechanism execution failed; full diagnostics retained")
    return {"complete": True, "trial_id": trial_id, "end_to_end_seconds": work["end_to_end_seconds"],
            "peak_rss_kib": work["peak_rss_kib"]}


def verify_unchanged_source(repo, source):
    for row in git(repo, "diff", "--name-status", source).decode().splitlines():
        status, name = row.split("\t", 1)
        require(status == "A" and name.startswith(R15 + "/results/experiment/"),
                "a mechanism source or historical file changed during evidence joining")


def collect(repo, bundle, input_dir, primary_evidence_commit, primary_evidence_tree):
    repo, bundle = Path(repo).resolve(), Path(bundle).resolve()
    m = read(bundle / "SOURCE_MANIFEST.json")
    source = m["numerical_source_commit"]
    require(git(repo, "rev-parse", "HEAD").decode().strip() == source, "collector source checkout mismatch")
    verify_unchanged_source(repo, source)
    git(repo, "merge-base", "--is-ancestor", m["candidate_source_commit"], primary_evidence_commit)
    actual_tree = git(repo, "rev-parse", f"{primary_evidence_commit}:{R15}/results/experiment").decode().strip()
    require(actual_tree == primary_evidence_tree, "main experiment subtree identity mismatch")
    main_audit = json.loads(git(repo, "show", f"{primary_evidence_commit}:{R15}/results/experiment/FINAL_AUDIT.json"))
    require(main_audit["complete"] and main_audit["numerical_source_commit"] == m["candidate_source_commit"]
            and main_audit["method_executions"] == 128 and main_audit["trial_count"] == 32, "main evidence is incomplete or from another source")
    for name, facts in m["files"].items():
        require(sha(repo / name) == facts["sha256"], f"mechanism collector source mismatch: {name}")
    protocol = read(repo / PROTOCOL)
    found = {}
    for path in Path(input_dir).rglob("WORK.json"):
        work = read(path)
        ident = work["trial"]["trial_id"]
        require(ident not in found, "duplicate mechanism stream artifact")
        found[ident] = path
    expected = trials(protocol)
    require(set(found) == {x["trial_id"] for x in expected}, "missing or extra mechanism stream")
    destination = repo / R15 / "results/mechanism"
    require(not destination.exists(), "refusing to replace mechanism evidence")
    elapsed = []
    for trial in expected:
        path = found[trial["trial_id"]]
        work = read(path)
        proof = read(path.parent / "INPUT_MANIFEST.json")
        require(work["complete"] and work["returncode"] == 0 and work["trial"] == trial,
                "incomplete mechanism process record")
        require(work["numerical_source_commit"] == source and work["candidate_source_commit"] == m["candidate_source_commit"]
                and work["protocol_sha256"] == m["protocol_sha256"]
                and work["assessment_fingerprint"] == m["assessment_fingerprint"], "mixed mechanism provenance")
        require(inventory(path.parent, exclude=["WORK.json"]) == work["files"], "mechanism artifact bytes changed")
        require(work["end_to_end_seconds"] > 0 and work["peak_rss_kib"] > 0
                and digest(canonical(work["environment"])) == work["environment_fingerprint"], "missing mechanism work/environment")
        validate_result(path.parent, trial, m, proof)
        # Check each selected checkpoint against the newly joined exact primary
        # evidence subtree, without copying those checkpoints into this study.
        primary = read(repo / R15 / "results/experiment/trials" / trial["trial_id"] / "nbo/RESULT.json")
        require(primary["selected_checkpoint_sha256"] == proof["candidate_sha256"], "assessed checkpoint differs from published primary selection")
        shutil.copytree(path.parent, destination / "trials" / trial["trial_id"])
        elapsed.append(work["end_to_end_seconds"])
    write(destination / "SOURCE_MANIFEST.json", m)
    shutil.copyfile(bundle / "PRIMARY_SOURCE_MANIFEST.json", destination / "PRIMARY_SOURCE_MANIFEST.json")
    subprocess.run([sys.executable, str(repo / REPORT), "--protocol", str(repo / PROTOCOL),
                    "--results", str(destination / "trials"), "--out", str(destination / "report")], cwd=repo, check=True)
    audit = {"record_type": "R15 complete occupation-bridge evidence audit", "complete": True,
             "numerical_source_commit": source, "candidate_source_commit": m["candidate_source_commit"],
             "primary_evidence_commit": primary_evidence_commit, "primary_experiment_git_tree": primary_evidence_tree,
             "protocol_sha256": m["protocol_sha256"], "assessment_fingerprint": m["assessment_fingerprint"],
             "trial_count": len(expected), "streams_per_dimension": 16, "bridges_per_stream": protocol["bridges_per_stream"],
             "alpha": protocol["confidence"]["alpha"], "two_sided_events": protocol["confidence"]["event_count"],
             "all_declared_streams_retained": True, "total_assessment_process_seconds": sum(elapsed),
             "history_policy": "All source/historical bytes preserved. The exact already-published main experiment tree is joined at its original path, not copied into a new results hierarchy.",
             "commit_parent_policy": "Publication commit has the immutable mechanism source and complete main evidence commit as parents."}
    write(destination / "FINAL_AUDIT.json", audit)
    write(destination / "EVIDENCE_MANIFEST.json", {"record_type": "R15 mechanism evidence digests",
          "numerical_source_commit": source, "primary_evidence_commit": primary_evidence_commit,
          "primary_experiment_git_tree": primary_evidence_tree,
          "hash_scope": "All new mechanism files excluding this digest manifest itself; existing main raw evidence is identified by its immutable Git subtree.",
          "files": {str(p.relative_to(repo)): sha(p) for p in sorted(destination.rglob("*")) if p.is_file()}})
    return {"complete": True, "trials": len(expected), "bridges": len(expected)*protocol["bridges_per_stream"],
            "primary_evidence_commit": primary_evidence_commit}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    sub = commands.add_parser("check")
    sub.add_argument("--repo", type=Path, default=Path.cwd())
    sub = commands.add_parser("pack")
    sub.add_argument("--repo", type=Path, default=Path.cwd())
    sub.add_argument("--out", type=Path, required=True)
    sub.add_argument("--primary-bundle", type=Path, required=True)
    sub.add_argument("--source-commit", default=os.environ.get("NBO_R15_NUMERICAL_SOURCE_COMMIT"))
    sub = commands.add_parser("run")
    for key in ["bundle", "workspace", "primary-dir", "out"]:
        sub.add_argument("--"+key, type=Path, required=True)
    sub.add_argument("--trial-id", required=True)
    sub = commands.add_parser("collect")
    sub.add_argument("--repo", type=Path, default=Path.cwd())
    for key in ["bundle", "input-dir"]:
        sub.add_argument("--"+key, type=Path, required=True)
    sub.add_argument("--primary-evidence-commit", required=True)
    sub.add_argument("--primary-evidence-tree", required=True)
    args = vars(parser.parse_args())
    command = args.pop("command")
    if command == "pack":
        args["source"] = args.pop("source_commit")
    print(json.dumps(globals()[command](**args), indent=2, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
