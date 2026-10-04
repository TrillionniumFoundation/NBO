"""Immutable-source delivery of the four R15 protected-observation cells.

Only ``check`` is a pre-freeze operation. ``pack`` reads exact Git blobs;
``run`` receives that small source artifact and times a fresh child process.
``collect`` verifies every declared cell without conditioning on its outcome.
No fitting or historical-result restoration is performed by this pipeline.
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
import math
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
PROTOCOL = R15 + "/PROTECTED_OBSERVATION_PROTOCOL.json"
PRODUCER = R15 + "/code/protected_observation.py"
PIPELINE = R15 + "/code/pipeline_observation.py"
WORKFLOW = ".github/workflows/nbo-r15-observation.yml"
BASE = "f5021cefa71492babfcbfa580e0c984f59a9de26"
CLOSURE = [
    PROTOCOL, PRODUCER, PIPELINE, WORKFLOW,
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
ENVIRONMENT = {
    "python": "3.12", "numpy": "2.3.5", "scipy": "1.17.0",
    "numba": "0.65.1", "mpmath": "1.3.0", "torch": "2.10.0+cpu",
    "platform": "Linux", "numeric_threads": 1,
}


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha_bytes(data):
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


def expected_cells(protocol):
    return [{"dimension": int(d), "cells": int(n), "cell_id": f"d{d}_n{n}"}
            for d in protocol["dimensions"] for n in protocol["actor_cells"]]


def validate_protocol(p):
    require(p["dimensions"] == [10, 50], "observation dimensions changed")
    require(p["actor_cells"] == [1024, 4096], "observation grids changed")
    require(p["paths"] == 8192, "observation path count changed")
    require(p["sensor_noise_rms"] == [0., .0001, .001], "sensor levels changed")
    require(p["alpha"] == .01 and p["one_sided_family_size"] == 8,
            "R15 observation confidence allocation changed")
    require(len(expected_cells(p)) == 4, "four observation cells are required")
    for d in p["dimensions"]:
        weight = p["weights"][str(d)]
        require(weight["path"].startswith("revisions/2026-10-04-r13/results/"),
                "unexpected historical weight location")
        require(re.fullmatch("[0-9a-f]{64}", weight["sha256"]), "invalid weight digest")


def source_files(protocol):
    return sorted(CLOSURE + [protocol["weights"][str(d)]["path"] for d in protocol["dimensions"]])


def check(repo):
    repo = Path(repo).resolve()
    p = read(repo / PROTOCOL)
    validate_protocol(p)
    files = source_files(p)
    for name in files:
        require((repo / name).is_file(), f"missing source dependency: {name}")
        if name.endswith(".py"):
            ast.parse((repo / name).read_text(), filename=name)
    for weight in p["weights"].values():
        require(sha(repo / weight["path"]) == weight["sha256"], "historical weights changed")
    return {"complete": True, "operation": "static pre-freeze closure check; no experiment",
            "files": len(files), "source_bytes": sum((repo / n).stat().st_size for n in files),
            "protocol_sha256": sha(repo / PROTOCOL), "matrix": {"include": expected_cells(p)}}


def pack(repo, out, source):
    repo, out = Path(repo).resolve(), Path(out).resolve()
    require(re.fullmatch("[0-9a-f]{40}", source or ""), "an immutable Git source SHA is required")
    require(git(repo, "rev-parse", "HEAD").decode().strip() == source, "checkout is not the numerical source")
    git(repo, "merge-base", "--is-ancestor", BASE, source)
    if os.environ.get("GITHUB_SHA"):
        require(os.environ["GITHUB_SHA"] == source, "Actions event differs from source")
    check(repo)
    p = read(repo / PROTOCOL)
    payload, inventory = {}, {}
    for name in source_files(p):
        data = git(repo, "show", f"{source}:{name}")
        require((repo / name).read_bytes() == data, f"working source differs from committed blob: {name}")
        payload[name] = data
        inventory[name] = {"sha256": sha_bytes(data), "bytes": len(data),
                           "git_blob": git(repo, "rev-parse", f"{source}:{name}").decode().strip()}
    fingerprint_input = {"method_id": "nbo", "implementation": "protected_finite_observation",
                         "protocol_sha256": inventory[PROTOCOL]["sha256"],
                         "files": {n: x["sha256"] for n, x in inventory.items()},
                         "environment_contract": ENVIRONMENT}
    out.mkdir(parents=True, exist_ok=True)
    archive = out / "source.tar.gz"
    with archive.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w", format=tarfile.PAX_FORMAT) as tar:
                for name, data in payload.items():
                    info = tarfile.TarInfo(name)
                    info.size, info.mode, info.mtime = len(data), 0o644, 0
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    tar.addfile(info, io.BytesIO(data))
    manifest = {
        "record_type": "R15 immutable protected-observation source package",
        "numerical_source_commit": source, "historical_base_commit": BASE,
        "packed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "files": inventory, "protocol_sha256": inventory[PROTOCOL]["sha256"],
        "method_id": "nbo", "method_fingerprint": sha_bytes(canonical(fingerprint_input)),
        "fingerprint_input": fingerprint_input, "environment_contract": ENVIRONMENT,
        "matrix": {"include": expected_cells(p)}, "archive_sha256": sha(archive),
        "archive_bytes": archive.stat().st_size,
        "history_policy": "Only two fixed historical weights and the unchanged kernel closure are packed; the historical evidence stays in Git ancestry.",
    }
    write(out / "SOURCE_MANIFEST.json", manifest)
    (out / "pipeline_observation.py").write_bytes(payload[PIPELINE])
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as stream:
            stream.write("matrix=" + canonical(manifest["matrix"]).decode() + "\n")
    return {"complete": True, "source": source, "archive_bytes": manifest["archive_bytes"],
            "files": len(inventory), "matrix": manifest["matrix"]}


def extract(bundle, workspace):
    bundle, workspace = Path(bundle).resolve(), Path(workspace).resolve()
    manifest = read(bundle / "SOURCE_MANIFEST.json")
    require(re.fullmatch("[0-9a-f]{40}", manifest["numerical_source_commit"]), "invalid source identity")
    require(sha(__file__) == manifest["files"][PIPELINE]["sha256"], "launcher is not the source-bound wrapper")
    require(sha(bundle / "source.tar.gz") == manifest["archive_sha256"], "source archive digest mismatch")
    require(sha_bytes(canonical(manifest["fingerprint_input"])) == manifest["method_fingerprint"],
            "methodology fingerprint mismatch")
    require(not workspace.exists() or not any(workspace.iterdir()), "worker source directory must be empty")
    workspace.mkdir(parents=True, exist_ok=True)
    seen = set()
    with tarfile.open(bundle / "source.tar.gz", "r:gz") as tar:
        for member in tar:
            name = member.name
            require(name in manifest["files"] and name not in seen, "unexpected or duplicate archive member")
            require(member.isfile() and not PurePosixPath(name).is_absolute()
                    and ".." not in PurePosixPath(name).parts, "unsafe source archive member")
            data = tar.extractfile(member).read()
            require(sha_bytes(data) == manifest["files"][name]["sha256"], f"source digest mismatch: {name}")
            target = workspace / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            seen.add(name)
    require(seen == set(manifest["files"]), "source archive is incomplete")
    p = read(workspace / PROTOCOL)
    validate_protocol(p)
    require(seen == set(source_files(p)), "source inventory differs from declared minimal closure")
    require(sha(workspace / PROTOCOL) == manifest["protocol_sha256"], "protocol digest mismatch")
    require(manifest["matrix"] == {"include": expected_cells(p)}, "matrix differs from frozen protocol")
    return manifest, p


def environment():
    versions = {name: importlib.metadata.version(name) for name in ("numpy", "scipy", "numba", "mpmath", "torch")}
    for name, value in versions.items():
        require(value == ENVIRONMENT[name], f"unexpected {name} version: {value}")
    require(f"{sys.version_info.major}.{sys.version_info.minor}" == ENVIRONMENT["python"], "Python version differs")
    require(platform.system() == "Linux", "Linux wait4 memory units are required")
    cpu = None
    if Path("/proc/cpuinfo").exists():
        cpu = next((line.split(":", 1)[1].strip() for line in Path("/proc/cpuinfo").read_text().splitlines()
                    if line.startswith("model name")), None)
    return {"python": sys.version, "packages": versions, "platform": platform.platform(),
            "machine": platform.machine(), "cpu_model": cpu, "logical_cpus": os.cpu_count(),
            "threads": 1, "github_run_id": os.environ.get("GITHUB_RUN_ID"),
            "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "runner_os": os.environ.get("RUNNER_OS"), "runner_arch": os.environ.get("RUNNER_ARCH")}


def validate_result(folder, cell, manifest, protocol):
    folder = Path(folder)
    name = f'protected_nbo_d{cell["dimension"]}_n{cell["cells"]}'
    result_path, raw = folder / (name + ".json"), folder / (name + ".npz")
    r = read(result_path)
    require(r["record_type"] == "protected_parent_and_sensor_certificate", "unexpected result schema")
    require(r["method"] == "nbo" and r["implementation"] == "protected_finite_observation", "incorrect method identity")
    require(r["dimension"] == cell["dimension"] and r["cells"] == cell["cells"], "result cell mismatch")
    require(r["numerical_source_commit"] == manifest["numerical_source_commit"], "result source mismatch")
    require(r["protocol_sha256"] == manifest["protocol_sha256"], "result protocol mismatch")
    require(r["paths"] == protocol["paths"], "result path count mismatch")
    require(r["state_transitions"] == 2 * cell["cells"] * protocol["paths"], "transition count mismatch")
    require(r["seed"] == protocol["noise_seed"] + 10000 * cell["dimension"] + cell["cells"], "noise seed mismatch")
    weight = protocol["weights"][str(cell["dimension"])]
    require(r["weights"] == weight["path"] and r["weights_sha256"] == weight["sha256"], "parent weights mismatch")
    require(sha(raw) == r["raw_sha256"], "raw result digest mismatch")
    bound = r["parent_bound"]
    require(bound["alpha"] == protocol["alpha"] and bound["family_size"] == protocol["one_sided_family_size"],
            "parent confidence family mismatch")
    require(bound["paths"] == protocol["paths"] and math.isfinite(bound["lower"])
            and math.isfinite(bound["upper"]) and bound["lower"] <= bound["upper"], "invalid parent interval")
    require([t["sensor_noise_rms"] for t in r["transfers"]] == protocol["sensor_noise_rms"], "missing or selected sensor transfers")
    for transfer in r["transfers"]:
        require(transfer["parent_id"] == name and transfer["parent_grid"] == cell["cells"], "transfer parent mismatch")
        allowance = transfer["payoff_difference_upper"]
        lo, hi = transfer["continuous_gain_interval"]
        require(math.isfinite(allowance) and allowance >= 0 and math.isfinite(lo) and math.isfinite(hi), "invalid deterministic transfer")
        require(lo <= bound["lower"] - allowance and hi >= bound["upper"] + allowance, "transfer interval does not contain the outward sum")
        require(len(transfer["recursion"]) == cell["cells"], "incomplete transfer recursion")
    return r


def run(bundle, workspace, out, dimension, cells):
    manifest, protocol = extract(bundle, workspace)
    cell = {"dimension": dimension, "cells": cells, "cell_id": f"d{dimension}_n{cells}"}
    require(cell in expected_cells(protocol), "worker cell is not prespecified")
    actual_env = environment()
    out, workspace = Path(out).resolve(), Path(workspace).resolve()
    out.mkdir(parents=True, exist_ok=True)
    require(not (out / "WORK.json").exists(), "refusing to overwrite a previous cell execution")
    child_env = dict(os.environ)
    child_env.update({"OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                      "NUMBA_NUM_THREADS": "1", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                      "NBO_R15_NUMERICAL_SOURCE_COMMIT": manifest["numerical_source_commit"],
                      "NBO_R15_SOURCE_COMMIT": manifest["numerical_source_commit"]})
    command = [sys.executable, str(workspace / PRODUCER), "--dimension", str(dimension),
               "--cells", str(cells), "--out", str(out)]
    receipt = {"record_type": "R15 independent observation process work", "complete": False,
               "cell": cell, "method_id": "nbo", "numerical_source_commit": manifest["numerical_source_commit"],
               "protocol_sha256": manifest["protocol_sha256"], "method_fingerprint": manifest["method_fingerprint"],
               "environment": actual_env, "environment_fingerprint": sha_bytes(canonical(actual_env)),
               "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "timing_scope": "fresh child process launch through exit: imports, initialization, fixed-weight I/O, interval constants, simulation, all deterministic transfers, raw output and final result JSON; no refitting",
               "provisioning_scope": "Actions provisioning, dependency installation and source-package integrity checks are outside algorithm execution and do not reuse a numerical cache"}
    with tempfile.TemporaryDirectory(prefix="nbo-r15-observation-numba-") as cache:
        child_env["NUMBA_CACHE_DIR"] = cache
        with (out / "process.log").open("wb") as log:
            start = time.perf_counter_ns()
            process = subprocess.Popen(command, cwd=workspace, env=child_env, stdout=log, stderr=subprocess.STDOUT)
            _, status, usage = os.wait4(process.pid, 0)
            finish = time.perf_counter_ns()
            process.returncode = os.waitstatus_to_exitcode(status)
        receipt.update(end_to_end_seconds=(finish - start) / 1e9,
                       peak_process_rss_kib=int(usage.ru_maxrss), user_cpu_seconds=usage.ru_utime,
                       system_cpu_seconds=usage.ru_stime, returncode=process.returncode)
    try:
        require(process.returncode == 0, f"observation process failed with status {process.returncode}")
        result = validate_result(out, cell, manifest, protocol)
        for name, facts in manifest["files"].items():
            require(sha(workspace / name) == facts["sha256"], f"experiment changed an input: {name}")
        receipt.update(complete=True, parent_interval=[result["parent_bound"]["lower"], result["parent_bound"]["upper"]],
                       state_transitions=result["state_transitions"])
    except Exception as exc:
        receipt["failure"] = str(exc)
        raise
    finally:
        receipt["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        receipt["files"] = {p.name: sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name != "WORK.json"}
        write(out / "WORK.json", receipt)
    return {"complete": True, "cell": cell, "end_to_end_seconds": receipt["end_to_end_seconds"],
            "peak_process_rss_kib": receipt["peak_process_rss_kib"]}


def collect(repo, bundle, input_dir):
    repo, bundle, input_dir = Path(repo).resolve(), Path(bundle).resolve(), Path(input_dir).resolve()
    manifest = read(bundle / "SOURCE_MANIFEST.json")
    source = manifest["numerical_source_commit"]
    require(git(repo, "rev-parse", "HEAD").decode().strip() == source, "collector is not on the experiment source")
    require(not git(repo, "diff", "--name-only", source).strip(), "a tracked historical/source file changed")
    for name, facts in manifest["files"].items():
        require(sha(repo / name) == facts["sha256"], f"collector source mismatch: {name}")
    protocol = read(repo / PROTOCOL)
    validate_protocol(protocol)
    require(manifest["matrix"] == {"include": expected_cells(protocol)}, "collector matrix mismatch")
    found = {}
    for receipt_path in input_dir.rglob("WORK.json"):
        w = read(receipt_path)
        cell_id = w["cell"]["cell_id"]
        require(cell_id not in found, "duplicate observation cell artifact")
        found[cell_id] = receipt_path
    require(set(found) == {x["cell_id"] for x in expected_cells(protocol)}, "missing or extra observation cell")
    destination = repo / R15 / "results/observation"
    require(not destination.exists(), "refusing to replace existing observation evidence")
    rows = []
    for cell in expected_cells(protocol):
        receipt_path = found[cell["cell_id"]]
        w = read(receipt_path)
        require(w["complete"] and w["returncode"] == 0 and w["cell"] == cell, "incomplete observation execution")
        require(w["numerical_source_commit"] == source and w["protocol_sha256"] == manifest["protocol_sha256"]
                and w["method_fingerprint"] == manifest["method_fingerprint"], "execution provenance mismatch")
        require(w["end_to_end_seconds"] > 0 and w["peak_process_rss_kib"] > 0, "missing measured work")
        require(sha_bytes(canonical(w["environment"])) == w["environment_fingerprint"], "environment fingerprint mismatch")
        for name, digest in w["files"].items():
            require(Path(name).name == name and sha(receipt_path.parent / name) == digest, "worker output digest mismatch")
        result = validate_result(receipt_path.parent, cell, manifest, protocol)
        target = destination / cell["cell_id"]
        target.mkdir(parents=True, exist_ok=True)
        for name in [*w["files"], "WORK.json"]:
            shutil.copyfile(receipt_path.parent / name, target / name)
        rows.append({"cell": cell, "method_id": "nbo", "parent_bound": result["parent_bound"],
                     "sensor_intervals": [{"sensor_noise_rms": t["sensor_noise_rms"],
                                            "payoff_difference_upper": t["payoff_difference_upper"],
                                            "continuous_gain_interval": t["continuous_gain_interval"]}
                                           for t in result["transfers"]],
                     "end_to_end_seconds": w["end_to_end_seconds"], "peak_process_rss_kib": w["peak_process_rss_kib"],
                     "state_transitions": result["state_transitions"]})
    write(destination / "SOURCE_MANIFEST.json", manifest)
    audit = {"record_type": "R15 complete protected-observation evidence audit", "complete": True,
             "numerical_source_commit": source, "historical_base_commit": BASE,
             "protocol_sha256": manifest["protocol_sha256"], "method_fingerprint": manifest["method_fingerprint"],
             "cells_expected": 4, "cells_completed": len(rows), "parent_intervals": 4,
             "deterministic_sensor_transfers": sum(len(r["sensor_intervals"]) for r in rows),
             "alpha": protocol["alpha"], "one_sided_family_size": protocol["one_sided_family_size"],
             "statistical_scope": "R15 observation family only; the historical R14 alpha family and other R15 allocations are recorded separately",
             "selection": "all prespecified cells and sensor levels, regardless of interval sign",
             "historical_preservation": "all tracked source-tree files unchanged; new evidence only below R15/results/observation",
             "total_measured_process_seconds": sum(r["end_to_end_seconds"] for r in rows), "rows": rows}
    write(destination / "FINAL_AUDIT.json", audit)
    inventory = {str(p.relative_to(repo)): sha(p) for p in sorted(destination.rglob("*")) if p.is_file()}
    write(destination / "EVIDENCE_MANIFEST.json", {
        "record_type": "R15 observation evidence digests", "numerical_source_commit": source,
        "hash_scope": "all observation evidence and source/audit records; this digest manifest excludes itself to avoid circular hashes",
        "files": inventory})
    return {"complete": True, "cells": len(rows), "transfers": audit["deterministic_sensor_transfers"],
            "numerical_source_commit": source, "evidence_files": len(inventory) + 1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("check")
    p.add_argument("--repo", type=Path, default=Path.cwd())
    p = commands.add_parser("pack")
    p.add_argument("--repo", type=Path, default=Path.cwd())
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--source-commit", default=os.environ.get("NBO_R15_NUMERICAL_SOURCE_COMMIT"))
    p = commands.add_parser("run")
    p.add_argument("--bundle", type=Path, required=True)
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--dimension", type=int, required=True)
    p.add_argument("--cells", type=int, required=True)
    p = commands.add_parser("collect")
    p.add_argument("--repo", type=Path, default=Path.cwd())
    p.add_argument("--bundle", type=Path, required=True)
    p.add_argument("--input-dir", type=Path, required=True)
    args = vars(parser.parse_args())
    command = args.pop("command")
    if command == "pack":
        args["source"] = args.pop("source_commit")
    result = globals()[command](**args)
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
