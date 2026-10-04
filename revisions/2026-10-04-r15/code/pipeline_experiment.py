"""R15 main numerical source packaging, isolated execution and complete delivery.

The source branch precedes every confirmatory outcome. Matrix workers use a
small, verified dependency archive, not another copy of historical evidence.
Each method executes in a fresh process; no scientific work or cache is shared
between methods. The manuscript can subsequently cite this numerical source.
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
PROTOCOL = R15 + "/PROTOCOL.json"
SCALAR_PROTOCOL = R15 + "/SCALAR_PROTOCOL.json"
PIPELINE = R15 + "/code/pipeline_experiment.py"
WORKER = R15 + "/code/worker.py"
REPORT = R15 + "/code/report_experiment.py"
WORKFLOW = ".github/workflows/nbo-r15-experiment.yml"
BASE = "f5021cefa71492babfcbfa580e0c984f59a9de26"
METHODS = ["nbo", "raw_costate", "direct_policy", "neural_hjb"]
PACKAGES = {"numpy": "2.3.5", "scipy": "1.17.0", "numba": "0.65.1",
            "mpmath": "1.3.0", "torch": "2.10.0+cpu"}
CLOSURE = [
    PROTOCOL, SCALAR_PROTOCOL, PIPELINE, WORKER, REPORT, WORKFLOW,
    R15 + "/code/training_core.py", R15 + "/code/actor_verifier.py",
    R15 + "/code/method_statistics.py", R15 + "/code/baselines.py",
    R15 + "/code/scalar_baseline.py",
    "revisions/2026-10-04-r12/code/common.py",
    "revisions/2026-10-04-r12/code/evaluation.py",
    "revisions/2026-10-04-r12/code/training.py",
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


def trials(p):
    answer = []
    for di, d in enumerate(p["design"]["dimensions"]):
        for si, seed in enumerate(p["design"]["seeds"]):
            offset = (di + si) % len(METHODS)
            answer.append({"trial_id": f"d{d}_s{seed}", "dimension": d,
                           "stream_seed": seed, "method_order": METHODS[offset:] + METHODS[:offset]})
    return answer


def validate_protocol(p, *, frozen=True):
    require(p["design"]["methods"] == METHODS, "canonical four-method design required")
    require(p["design"]["dimensions"] == [10, 50], "main dimensions changed")
    seeds = p["design"]["seeds"]
    require(len(seeds) == len(set(seeds)) == 16, "the complete sixteen-stream distribution is required")
    require(digest(canonical(p["design"]["primitives"])) == p["design"]["primitives_sha256"], "primitive fingerprint mismatch")
    inf = p["inference"]
    require(inf["alpha_allocation"] == {"online_stopping": .01, "method_confirmation": .02,
                                        "mechanism": .01, "protected_observation": .01}, "R15 alpha allocation changed")
    require(inf["online_stopping_events"] == 384 and inf["method_confirmation_events"] == 238, "confidence event counts changed")
    require(p["stopping"]["maximum_checkpoint_checks"] == 3, "three fixed online looks required")
    require(p["stopping"]["primary_certified_gain_target"] == .0005, "primary target changed")
    if frozen:
        require(p["status"] == "frozen_before_confirmatory_execution", "main protocol is not frozen")
        require(isinstance(p["training"]["checkpoint_budgets"], list)
                and len(p["training"]["checkpoint_budgets"]) == 3, "training budgets missing")
        require(p["confirmation"]["paths_per_seed"] in [4096, 8192]
                and p["confirmation"]["steps"] in [2048, 4096], "final confirmation design missing")
        require(isinstance(p["stopping"].get("paths_per_checkpoint"), int) and isinstance(p["stopping"].get("steps"), int),
                "online paths and mesh missing")


def source_files(repo):
    scalar = read(Path(repo) / SCALAR_PROTOCOL)
    tests = sorted(str(p.relative_to(repo)) for p in (Path(repo) / R15 / "code").glob("test_*.py"))
    return sorted(set(CLOSURE + tests + [x["path"] for x in scalar["frozen_neural_candidates"]]))


def check(repo, allow_draft=False):
    repo = Path(repo).resolve()
    p = read(repo / PROTOCOL)
    validate_protocol(p, frozen=not allow_draft)
    files = source_files(repo)
    for name in files:
        require((repo / name).is_file(), f"missing dependency: {name}")
        if name.endswith(".py"):
            ast.parse((repo / name).read_text(), filename=name)
    for x in read(repo / SCALAR_PROTOCOL)["frozen_neural_candidates"]:
        require(sha(repo / x["path"]) == x["sha256"], "scalar frozen neural weights changed")
    return {"complete": True, "operation": "static source and protocol check; no experiment",
            "files": len(files), "source_bytes": sum((repo / n).stat().st_size for n in files),
            "trials": len(trials(p)), "method_runs": len(trials(p)) * len(METHODS)}


def pack(repo, out, source):
    repo, out = Path(repo).resolve(), Path(out).resolve()
    require(re.fullmatch("[0-9a-f]{40}", source or ""), "immutable numerical source SHA required")
    require(git(repo, "rev-parse", "HEAD").decode().strip() == source, "checkout differs from numerical source")
    git(repo, "merge-base", "--is-ancestor", BASE, source)
    if os.environ.get("GITHUB_SHA"):
        require(os.environ["GITHUB_SHA"] == source, "Actions source mismatch")
    check(repo)
    payload, inventory = {}, {}
    for name in source_files(repo):
        data = git(repo, "show", f"{source}:{name}")
        require((repo / name).read_bytes() == data, f"uncommitted numerical dependency: {name}")
        payload[name] = data
        inventory[name] = {"sha256": digest(data), "bytes": len(data),
                           "git_blob": git(repo, "rev-parse", f"{source}:{name}").decode().strip()}
    p = read(repo / PROTOCOL)
    environment_contract = {"python": "3.12", "packages": PACKAGES, "platform": "Linux",
                            "numeric_threads": 1, "torch_device": "cpu", "method_processes": "fresh and serial within trial"}
    fingerprints = {}
    for method in METHODS + ["scalar_howard"]:
        appropriate_protocol = SCALAR_PROTOCOL if method == "scalar_howard" else PROTOCOL
        item = {"method_id": method, "protocol_sha256": inventory[appropriate_protocol]["sha256"],
                "files": {n: x["sha256"] for n, x in inventory.items()}, "environment_contract": environment_contract}
        fingerprints[method] = {"sha256": digest(canonical(item)), "input": item}
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
    manifest = {"record_type": "R15 immutable main numerical source package", "numerical_source_commit": source,
                "historical_base_commit": BASE, "packed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "github_run_id": os.environ.get("GITHUB_RUN_ID"), "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
                "files": inventory, "method_fingerprints": fingerprints, "environment_contract": environment_contract,
                "protocol_sha256": inventory[PROTOCOL]["sha256"],
                "scalar_protocol_sha256": inventory[SCALAR_PROTOCOL]["sha256"],
                "primitives_sha256": p["design"]["primitives_sha256"], "matrix": {"include": trials(p)},
                "archive_sha256": sha(archive), "archive_bytes": archive.stat().st_size,
                "provenance_scope": "New high-volatility method experiment and separate original-regime scalar study. R15 protected observations have a distinct immutable numerical source; historical evidence remains in Git ancestry."}
    write(out / "SOURCE_MANIFEST.json", manifest)
    (out / "pipeline_experiment.py").write_bytes(payload[PIPELINE])
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as stream:
            stream.write("matrix=" + canonical(manifest["matrix"]).decode() + "\n")
    return {"complete": True, "source": source, "files": len(payload),
            "archive_bytes": manifest["archive_bytes"], "trials": len(trials(p))}


def extract(bundle, workspace):
    bundle, workspace = Path(bundle).resolve(), Path(workspace).resolve()
    m = read(bundle / "SOURCE_MANIFEST.json")
    require(sha(__file__) == m["files"][PIPELINE]["sha256"], "unbound experiment launcher")
    require(sha(bundle / "source.tar.gz") == m["archive_sha256"], "source archive mismatch")
    require(re.fullmatch("[0-9a-f]{40}", m["numerical_source_commit"]), "source SHA missing")
    for f in m["method_fingerprints"].values():
        require(digest(canonical(f["input"])) == f["sha256"], "method fingerprint mismatch")
    require(not workspace.exists() or not any(workspace.iterdir()), "source workspace must be empty")
    workspace.mkdir(parents=True, exist_ok=True)
    seen = set()
    with tarfile.open(bundle / "source.tar.gz", "r:gz") as tar:
        for member in tar:
            name = member.name
            require(member.isfile() and name in m["files"] and name not in seen
                    and not PurePosixPath(name).is_absolute() and ".." not in PurePosixPath(name).parts,
                    "unsafe, duplicated or undeclared source member")
            data = tar.extractfile(member).read()
            require(digest(data) == m["files"][name]["sha256"], f"source hash mismatch: {name}")
            target = workspace / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            seen.add(name)
    require(seen == set(m["files"]), "incomplete numerical source archive")
    check(workspace)
    p = read(workspace / PROTOCOL)
    require(sha(workspace / PROTOCOL) == m["protocol_sha256"], "main protocol hash mismatch")
    require(m["matrix"] == {"include": trials(p)}, "source matrix mismatch")
    return m, p


def environment():
    versions = {n: importlib.metadata.version(n) for n in PACKAGES}
    require(versions == PACKAGES, f"unexpected numerical package versions: {versions}")
    require(sys.version_info[:2] == (3, 12) and platform.system() == "Linux", "Python 3.12 on Linux required")
    cpu = None
    if Path("/proc/cpuinfo").exists():
        cpu = next((x.split(":", 1)[1].strip() for x in Path("/proc/cpuinfo").read_text().splitlines()
                    if x.startswith("model name")), None)
    return {"python": sys.version, "packages": versions, "platform": platform.platform(),
            "machine": platform.machine(), "cpu_model": cpu, "logical_cpus": os.cpu_count(),
            "threads": 1, "github_run_id": os.environ.get("GITHUB_RUN_ID"),
            "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT")}


def file_inventory(folder, exclude=()):
    folder = Path(folder)
    return {str(x.relative_to(folder)): sha(x) for x in sorted(folder.rglob("*"))
            if x.is_file() and str(x.relative_to(folder)) not in exclude}


def execute_child(command, workspace, out, manifest, method, trial=None):
    out, workspace = Path(out).resolve(), Path(workspace).resolve()
    require(not out.exists(), "refusing to overwrite a numerical execution")
    out.mkdir(parents=True)
    actual = environment()
    env = dict(os.environ)
    env.update({"NBO_R15_NUMERICAL_SOURCE_COMMIT": manifest["numerical_source_commit"],
                "NBO_R15_SOURCE_COMMIT": manifest["numerical_source_commit"],
                "NBO_R15_METHOD_FINGERPRINT": manifest["method_fingerprints"][method]["sha256"],
                "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0", "OMP_NUM_THREADS": "1",
                "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "NUMBA_NUM_THREADS": "1"})
    work = {"record_type": "R15 full independent numerical process work", "complete": False,
            "method_id": method, "trial_id": None if trial is None else trial["trial_id"],
            "numerical_source_commit": manifest["numerical_source_commit"],
            "protocol_sha256": manifest["scalar_protocol_sha256"] if method == "scalar_howard" else manifest["protocol_sha256"],
            "method_fingerprint": manifest["method_fingerprints"][method]["sha256"],
            "environment": actual, "environment_fingerprint": digest(canonical(actual)),
            "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "timing_scope": "fresh subprocess launch through exit; includes imports, initialization, all fitting and failed/successful online checks, checkpoints, reload, independent confirmation and final durable result I/O",
            "provisioning_scope": "environment installation and verified source extraction precede algorithm timing; numerical constants and JIT caches are not shared between method processes"}
    with tempfile.TemporaryDirectory(prefix="nbo-r15-main-numba-") as cache:
        env["NUMBA_CACHE_DIR"] = cache
        with (out / "process.log").open("wb") as log:
            started = time.perf_counter_ns()
            child = subprocess.Popen(command, cwd=workspace, env=env, stdout=log, stderr=subprocess.STDOUT)
            _, status, usage = os.wait4(child.pid, 0)
            finished = time.perf_counter_ns()
            child.returncode = os.waitstatus_to_exitcode(status)
        work.update(end_to_end_seconds=(finished - started) / 1e9, peak_rss_kib=int(usage.ru_maxrss),
                    user_cpu_seconds=usage.ru_utime, system_cpu_seconds=usage.ru_stime,
                    cpu_seconds=usage.ru_utime + usage.ru_stime, returncode=child.returncode)
    try:
        require(child.returncode == 0, f"numerical child exited with status {child.returncode}")
        if method == "scalar_howard":
            r = read(out / "SCALAR_BASELINE.json")
            require(r.get("source_commit", r.get("numerical_source_commit")) == manifest["numerical_source_commit"], "scalar source mismatch")
            require(r.get("protocol_sha256") == manifest["scalar_protocol_sha256"], "scalar protocol mismatch")
        else:
            r = read(out / "RESULT.json")
            require(r["complete"] and r["method_id"] == method and r["trial_id"] == trial["trial_id"], "result identity/integrity mismatch")
            require(r["numerical_source_commit"] == manifest["numerical_source_commit"]
                    and r["protocol_sha256"] == manifest["protocol_sha256"]
                    and r["primitives_sha256"] == manifest["primitives_sha256"]
                    and r["method_fingerprint"] == manifest["method_fingerprints"][method]["sha256"], "result source/method provenance mismatch")
            require(r["actual_early_stopping_execution"], "retrospective prefix is not an actual stopping execution")
            work.update(actual_early_stopping_execution=True, attained=bool(r["attained_online"]),
                        fallback=bool(r["fallback"]), dimension=trial["dimension"], stream_seed=trial["stream_seed"])
        for name, facts in manifest["files"].items():
            require(sha(workspace / name) == facts["sha256"], f"child changed a frozen input: {name}")
        work["complete"] = True
    except Exception as exc:
        work["failure"] = str(exc)
    work["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    work["files"] = file_inventory(out, exclude=["WORK.json"])
    write(out / "WORK.json", work)
    return work


def run_trial(bundle, workspace, out, trial_id):
    m, p = extract(bundle, workspace)
    found = [t for t in trials(p) if t["trial_id"] == trial_id]
    require(len(found) == 1, "unknown complete algorithm-stream trial")
    trial, out, workspace = found[0], Path(out).resolve(), Path(workspace).resolve()
    out.mkdir(parents=True, exist_ok=True)
    require(not (out / "TRIAL.json").exists(), "refusing to repeat a recorded trial")
    records = []
    for method in trial["method_order"]:
        method_out = out / method
        command = [sys.executable, str(workspace / WORKER), "--protocol", str(workspace / PROTOCOL),
                   "--trial-id", trial_id, "--method-id", method, "--out", str(method_out)]
        records.append(execute_child(command, workspace, method_out, m, method, trial))
    receipt = {"record_type": "R15 complete four-method algorithm-stream trial", "trial": trial,
               "complete": all(w["complete"] for w in records), "numerical_source_commit": m["numerical_source_commit"],
               "protocol_sha256": m["protocol_sha256"],
               "method_order_scope": "rotation fixed from the declared stream index and dimension before outcomes",
               "methods": [{"method_id": w["method_id"], "complete": w["complete"],
                            "end_to_end_seconds": w["end_to_end_seconds"], "work_sha256": sha(out / w["method_id"] / "WORK.json")}
                           for w in records]}
    write(out / "TRIAL.json", receipt)
    require(receipt["complete"], "a method lacks complete independent confirmation; all four attempted records retained")
    return {"complete": True, "trial_id": trial_id, "methods": len(records)}


def run_scalar(bundle, workspace, out):
    m, _ = extract(bundle, workspace)
    workspace, out = Path(workspace).resolve(), Path(out).resolve()
    command = [sys.executable, str(workspace / R15 / "code/scalar_baseline.py"),
               "--protocol", str(workspace / SCALAR_PROTOCOL), "--out", str(out)]
    work = execute_child(command, workspace, out, m, "scalar_howard")
    require(work["complete"], "scalar study failed; all diagnostics retained")
    return {"complete": True, "method_id": "scalar_howard", "end_to_end_seconds": work["end_to_end_seconds"]}


def verify_work(folder, source, protocol_sha, fingerprint):
    folder = Path(folder)
    w = read(folder / "WORK.json")
    require(w["complete"] and w["returncode"] == 0, "incomplete independent process record")
    require(w["numerical_source_commit"] == source and w["protocol_sha256"] == protocol_sha
            and w["method_fingerprint"] == fingerprint, "inconsistent work provenance")
    require(w["end_to_end_seconds"] > 0 and w["peak_rss_kib"] > 0, "missing inclusive clock/memory")
    require(digest(canonical(w["environment"])) == w["environment_fingerprint"], "environment changed")
    require(file_inventory(folder, exclude=["WORK.json"]) == w["files"], "method output inventory differs from independent process receipt")
    return w


def collect(repo, bundle, input_dir, scalar_dir):
    repo, bundle = Path(repo).resolve(), Path(bundle).resolve()
    m = read(bundle / "SOURCE_MANIFEST.json")
    source = m["numerical_source_commit"]
    require(git(repo, "rev-parse", "HEAD").decode().strip() == source, "collection checkout differs from source")
    require(not git(repo, "diff", "--name-only", source).strip(), "tracked historical/source bytes changed")
    for name, facts in m["files"].items():
        require(sha(repo / name) == facts["sha256"], f"source mismatch during collection: {name}")
    p = read(repo / PROTOCOL)
    validate_protocol(p)
    expected = trials(p)
    found = {}
    for path in Path(input_dir).rglob("TRIAL.json"):
        t = read(path)
        ident = t["trial"]["trial_id"]
        require(ident not in found, "duplicate trial artifact")
        found[ident] = path
    require(set(found) == {t["trial_id"] for t in expected}, "incomplete or selected seed distribution")
    destination = repo / R15 / "results/experiment"
    require(not destination.exists(), "refusing to replace existing main evidence")
    count = 0
    for trial in expected:
        path = found[trial["trial_id"]]
        receipt = read(path)
        require(receipt["complete"] and receipt["trial"] == trial
                and receipt["numerical_source_commit"] == source and receipt["protocol_sha256"] == m["protocol_sha256"], "invalid trial receipt")
        require([r["method_id"] for r in receipt["methods"]] == trial["method_order"], "method order was not prespecified")
        for row in receipt["methods"]:
            method = row["method_id"]
            folder = path.parent / method
            require(sha(folder / "WORK.json") == row["work_sha256"], "trial work receipt changed")
            verify_work(folder, source, m["protocol_sha256"], m["method_fingerprints"][method]["sha256"])
            count += 1
        shutil.copytree(path.parent, destination / "trials" / trial["trial_id"])
    scalar_paths = [x.parent for x in Path(scalar_dir).rglob("SCALAR_BASELINE.json")]
    require(len(scalar_paths) == 1, "one complete scalar study required")
    verify_work(scalar_paths[0], source, m["scalar_protocol_sha256"], m["method_fingerprints"]["scalar_howard"]["sha256"])
    shutil.copytree(scalar_paths[0], destination / "scalar")
    write(destination / "SOURCE_MANIFEST.json", m)
    command = [sys.executable, str(repo / REPORT), "--protocol", str(repo / PROTOCOL),
               "--results", str(destination / "trials"), "--out", str(destination / "report")]
    subprocess.run(command, cwd=repo, check=True)
    audit = {"record_type": "R15 complete source-bound main numerical evidence audit", "complete": True,
             "numerical_source_commit": source, "historical_base_commit": BASE,
             "protocol_sha256": m["protocol_sha256"], "primitives_sha256": m["primitives_sha256"],
             "trial_count": len(expected), "method_executions": count, "all_declared_streams_retained": True,
             "scalar_studies": 1, "method_ids": METHODS,
             "method_confirmation_events": p["inference"]["method_confirmation_events"],
             "online_stopping_maximum_events": p["inference"]["online_stopping_events"],
             "preservation": "All tracked source/historical bytes remain unchanged; only R15/results/experiment is added.",
             "source_scope": "This main numerical source is separate from the R15 protected-observation source and subsequent manuscript source."}
    write(destination / "FINAL_AUDIT.json", audit)
    write(destination / "EVIDENCE_MANIFEST.json", {"record_type": "R15 main evidence digests", "numerical_source_commit": source,
          "hash_scope": "Every new experiment evidence file, source inventory and audit; this digest manifest excludes itself.",
          "files": {str(x.relative_to(repo)): sha(x) for x in sorted(destination.rglob("*")) if x.is_file()}})
    return {"complete": True, "trials": len(expected), "method_runs": count, "scalar_studies": 1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    sub = commands.add_parser("check")
    sub.add_argument("--repo", type=Path, default=Path.cwd())
    sub.add_argument("--allow-draft", action="store_true")
    sub = commands.add_parser("pack")
    sub.add_argument("--repo", type=Path, default=Path.cwd())
    sub.add_argument("--out", type=Path, required=True)
    sub.add_argument("--source-commit", default=os.environ.get("NBO_R15_NUMERICAL_SOURCE_COMMIT"))
    sub = commands.add_parser("run-trial")
    for name in ["bundle", "workspace", "out"]:
        sub.add_argument("--" + name, type=Path, required=True)
    sub.add_argument("--trial-id", required=True)
    sub = commands.add_parser("run-scalar")
    for name in ["bundle", "workspace", "out"]:
        sub.add_argument("--" + name, type=Path, required=True)
    sub = commands.add_parser("collect")
    sub.add_argument("--repo", type=Path, default=Path.cwd())
    for name in ["bundle", "input-dir", "scalar-dir"]:
        sub.add_argument("--" + name, type=Path, required=True)
    args = vars(parser.parse_args())
    command = args.pop("command").replace("-", "_")
    if command == "pack":
        args["source"] = args.pop("source_commit")
    print(json.dumps(globals()[command](**args), indent=2, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
