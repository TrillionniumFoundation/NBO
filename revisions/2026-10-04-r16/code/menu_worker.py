"""Isolated source-bound menu fitting worker and complete parent process clock.

This module deliberately imports only the standard library before launching its
scientific child. It never reads a final-confirmation bank. All stage candidates
and every failed fit remain available to a separate collector/verifier.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import resource
import subprocess
import sys
import tempfile
import time
import traceback
import zipfile

ROOT = Path(__file__).resolve().parents[3]
CODE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    # A killed writer leaves either the preceding complete JSON or a temporary
    # file. It cannot expose half of the final sealed stage record.
    fd, temporary = tempfile.mkstemp(prefix="."+path.name+".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
            f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def seal_stage(out, row, args, economy, queries, origin, source=None):
    """Atomically publish the only record that authorizes prefix preservation."""
    out = Path(out); row = dict(row); stage = int(row["stage"])
    action_path = out/f"actions_stage{stage}.npz"
    if row.get("actions_file") != action_path.name or not action_path.is_file():
        raise ValueError("stage action file is absent or misidentified at sealing")
    with action_path.open("rb") as f:
        os.fsync(f.fileno())
    if row.get("actions_sha256") != sha(action_path):
        raise ValueError("stage action bytes changed before sealing")
    row.update(schema="nbo-r16-menu-sealed-stage-v1", sealed=True,
        method=args.method, calibration=args.calibration, dimension=int(args.dimension),
        seed=int(args.seed), source_commit=source,
        parent_prefix_seconds=(time.perf_counter_ns()-origin)/1e9,
        prefix_scope="actual parent launch through durable candidate before final seal metadata; the complete fit clock also charges all seal writes",
        continuation_sha256=economy.continuation_sha256,
        query_catalog_sha256=queries["catalog_sha256"])
    if not isinstance(row.get("fallback"), bool) or not isinstance(row.get("counters"), dict):
        raise ValueError("a sealed stage requires an explicit fallback flag and recorded counters")
    write(out/f"stage{stage}.json", row)
    return row


def preserved_prefix(out, stage, args, economy, queries, source=None):
    """Return a fully sealed, identity-bound prefix; malformed drafts are data."""
    out = Path(out); record_path = out/f"stage{stage}.json"
    action_path = out/f"actions_stage{stage}.npz"
    try:
        row = json.loads(record_path.read_text())
        if not isinstance(row, dict):
            return None, "stage record is not a JSON object"
        if row.get("sealed") is not True:
            return None, "stage has not been atomically sealed"
        expected = dict(schema="nbo-r16-menu-sealed-stage-v1", sealed=True,
            stage=int(stage), method=args.method, calibration=args.calibration,
            dimension=int(args.dimension), seed=int(args.seed), source_commit=source,
            actions_file=action_path.name, continuation_sha256=economy.continuation_sha256,
            query_catalog_sha256=queries["catalog_sha256"])
        for key, value in expected.items():
            if key not in row or row[key] != value:
                return None, "missing or mismatched sealed field: "+key
        prefix = row.get("parent_prefix_seconds")
        if isinstance(prefix, bool) or not isinstance(prefix, (int, float)) or not math.isfinite(prefix) or prefix < 0:
            return None, "invalid or absent complete prefix clock"
        if not isinstance(row.get("fallback"), bool) or not isinstance(row.get("counters"), dict):
            return None, "missing fallback status or recorded counters"
        if not re.fullmatch(r"[0-9a-f]{64}", str(row.get("actions_sha256", ""))):
            return None, "missing action SHA-256"
        if not action_path.is_file() or sha(action_path) != row["actions_sha256"]:
            return None, "action file absent or action SHA-256 mismatch"
        return row, None
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, type(exc).__name__+": "+str(exc)


def archive_unsealed_stage(out, stage, reason):
    """Move exact interrupted bytes aside before writing the fixed fallback."""
    out = Path(out)
    base = out/"failure_recovery"/f"stage{stage}"
    attempt = 0
    while (base/f"attempt{attempt:03d}").exists():
        attempt += 1
    archive = base/f"attempt{attempt:03d}"
    archive.mkdir(parents=True)
    candidates = [out/f"stage{stage}.json", out/f"actions_stage{stage}.npz"]
    candidates.extend(sorted(out.glob(f".stage{stage}.json.*.tmp")))
    files = []
    for path in candidates:
        if not path.is_file():
            continue
        info = dict(original=str(path.relative_to(out)), bytes=path.stat().st_size, sha256=sha(path))
        target = archive/path.name
        os.replace(path, target)
        info["archived"] = str(target.relative_to(out)); files.append(info)
    write(archive/"RECOVERY.json", dict(schema="nbo-r16-interrupted-prefix-archive-v1",
        stage=int(stage), reason=reason, files=files,
        rule="original incomplete bytes retained; no retraining, replacement seed, or inference from an unsealed prefix"))
    return str(archive.relative_to(out))


def verify_source(protocol_path, protocol):
    source = os.environ.get("NBO_R16_MENU_SOURCE_COMMIT", "")
    if not re.fullmatch(r"[0-9a-f]{40}", source):
        raise RuntimeError("frozen execution requires NBO_R16_MENU_SOURCE_COMMIT")
    paths = list(protocol["execution"]["source_files"])
    rel_protocol = str(Path(protocol_path).resolve().relative_to(ROOT))
    if rel_protocol not in paths:
        raise ValueError("protocol is absent from its frozen source closure")
    manifest = None
    manifest_path = os.environ.get("NBO_R16_MENU_SOURCE_MANIFEST")
    if manifest_path:
        expected = os.environ.get("NBO_R16_MENU_SOURCE_MANIFEST_SHA256", "")
        if not re.fullmatch(r"[0-9a-f]{64}", expected) or sha(manifest_path) != expected:
            raise RuntimeError("source manifest is not bound to the independently supplied SHA-256")
        manifest = json.loads(Path(manifest_path).read_text())
        if manifest.get("source_commit") != source:
            raise RuntimeError("source manifest and frozen commit differ")
    records = {}
    for relative in paths:
        path = ROOT/relative
        if not path.is_file():
            raise FileNotFoundError("missing declared source: "+relative)
        actual = path.read_bytes()
        if manifest is not None:
            item = manifest.get("files", {}).get(relative)
            if item is None:
                raise RuntimeError("source closure file absent from bound manifest: "+relative)
            git_blob = hashlib.sha1(b"blob "+str(len(actual)).encode()+b"\0"+actual).hexdigest()
            expected_blob = item.get("git_blob_sha", item.get("git_blob", item.get("blob_sha")))
            if (item.get("sha256") != hashlib.sha256(actual).hexdigest()
                    or item.get("bytes") != len(actual) or expected_blob != git_blob):
                raise RuntimeError("source file differs from bound Git object manifest: "+relative)
            records[relative] = dict(sha256=item["sha256"], bytes=len(actual), git_blob_sha=git_blob,
                                     binding="independently hashed source-commit manifest")
        else:
            blob = subprocess.run(["git", "cat-file", "blob", source+":"+relative],
                cwd=ROOT, capture_output=True, check=True).stdout
            if blob != actual:
                raise RuntimeError("working source differs from frozen commit: "+relative)
            records[relative] = dict(sha256=hashlib.sha256(blob).hexdigest(), bytes=len(blob),
                git_blob_sha=hashlib.sha1(b"blob "+str(len(blob)).encode()+b"\0"+blob).hexdigest(),
                binding="direct Git object equality")
    return source, records


def fallback_scalar(args, protocol, economy, out, failure):
    if args.method != "nbo_scalar":
        return
    import numpy as np
    from menu_economy import array_hash, scalar_query_spec
    out = Path(out)
    spec = scalar_query_spec(protocol, economy)
    left, right = spec["a_left"][0], spec["a_right"][0]
    candidate = min(1., max(0., (float(economy.schedule[0])-left)/(right-left))) if right > left else 0.
    record_path = out/"SCALAR_CANDIDATE.json"
    grid_path = out/"scalar_candidate_grid.npz"
    reason = "scalar candidate was not fully published"
    if record_path.is_file():
        try:
            row = json.loads(record_path.read_text())
            if not isinstance(row, dict) or any(row.get(k) != v for k, v in spec.items()):
                raise ValueError("scalar query or continuation identity differs")
            if (row.get("seed") != args.seed or row.get("stage") != len(protocol["training"]["cumulative_replay_states"])
                    or not isinstance(row.get("failed_fit"), bool) or row.get("primary_vector_candidate_unchanged") is not True):
                raise ValueError("scalar trial or completed stage differs")
            choice = row.get("candidate_s")
            if isinstance(choice, bool) or not isinstance(choice, (int, float)) or not math.isfinite(choice) or not 0 <= choice <= 1:
                raise ValueError("invalid scalar candidate parameter")
            if row["failed_fit"]:
                if choice != candidate:
                    raise ValueError("scalar fallback differs from the declared reference")
            else:
                count = protocol["scalar_accuracy"]["candidate_grid_points"]
                with grid_path.open("rb") as grid_file:
                    with np.load(grid_file, allow_pickle=False) as payload:
                        if set(payload.files) != {"scalar_parameters", "critic_values"}:
                            raise ValueError("incomplete scalar candidate grid")
                        grid, values = payload["scalar_parameters"], payload["critic_values"]
                if (grid.shape != (count,) or not np.array_equal(grid, np.linspace(0., 1., count))
                        or values.shape != (count, 1) or not np.all(np.isfinite(values))):
                    raise ValueError("scalar candidate grid differs from the fixed finite search")
                index = int(np.argmax(values))
                if (row.get("candidate_grid_points") != count or row.get("selected_grid_index") != index
                        or choice != float(grid[index]) or row.get("selected_critic_values_sha256") != array_hash(values)):
                    raise ValueError("scalar selection differs from its durable critic grid")
            return
        except (OSError, UnicodeError, ValueError, TypeError, KeyError, EOFError, zipfile.BadZipFile) as exc:
            reason = type(exc).__name__+": "+str(exc)
    interrupted = [p for p in [record_path, grid_path, *sorted(out.glob(".SCALAR_CANDIDATE.json.*.tmp"))] if p.is_file()]
    if interrupted:
        base = out/"failure_recovery"/"scalar"
        attempt = 0
        while (base/f"attempt{attempt:03d}").exists():
            attempt += 1
        archive = base/f"attempt{attempt:03d}"
        archive.mkdir(parents=True)
        files = []
        for path in interrupted:
            target = archive/path.name
            info = dict(original=str(path.relative_to(out)), bytes=path.stat().st_size,
                        sha256=sha(path), archived=str(target.relative_to(out)))
            os.replace(path, target); files.append(info)
        write(archive/"RECOVERY.json", dict(schema="nbo-r16-interrupted-scalar-archive-v1",
            reason=reason, files=files, seed=args.seed,
            rule="original interrupted bytes retained; the fixed reference parameter replaces only an invalid scalar record"))
        spec["recovery_archive"] = str(archive.relative_to(out))
    spec.update(candidate_s=candidate, failed_fit=True, failure=failure,
        stage=len(protocol["training"]["cumulative_replay_states"]), seed=args.seed,
        selection="declared feasible reference fallback after a retained fitting failure",
        primary_vector_candidate_unchanged=True)
    write(record_path, spec)


def child(args):
    import numpy as np
    from menu_economy import fixed_queries, load_economy
    from menu_methods import MenuRun
    protocol = json.loads(Path(args.protocol).read_text())
    economy = load_economy(protocol, args.calibration, args.dimension)
    out = Path(args.out)
    run = MenuRun(economy, protocol, args.method, args.seed, out)
    queries = run.queries
    failure = None
    origin = int(os.environ["NBO_R16_MENU_PARENT_PERF_NS"])
    for stage in range(1, len(protocol["training"]["cumulative_replay_states"])+1):
        if failure is None:
            try:
                row = run.advance(stage)
                row["fallback"] = False
            except Exception as exc:
                failure = dict(type=type(exc).__name__, message=str(exc), traceback=traceback.format_exc(),
                               failed_stage=stage, seed=args.seed, method=args.method)
                write(out/"FAILURE.json", failure)
        if failure is not None:
            archive = archive_unsealed_stage(out, stage, failure)
            actions = np.maximum(queries["lower"], np.minimum(queries["upper"], economy.schedule[0]))
            actions = np.broadcast_to(actions, queries["states"].shape).copy()
            path = out/f"actions_stage{stage}.npz"
            np.savez_compressed(path, actions=actions,
                **{k: queries[k] for k in ["states", "task_id", "state_id", "utility_weight", "adjustment", "lower", "upper"]})
            row = dict(stage=stage, method=args.method, fallback=True,
                fallback_policy="reference current schedule clipped only to the temporary task constraint",
                failure=failure, actions_file=path.name, actions_sha256=sha(path),
                counters=dict(run.counters), continuation_sha256=economy.continuation_sha256,
                query_catalog_sha256=queries["catalog_sha256"], recovery_archive=archive)
        row = seal_stage(out, row, args, economy, queries, origin,
                         source=os.environ.get("NBO_R16_MENU_SOURCE_COMMIT"))
        print(json.dumps(dict(stage=stage, fallback=row["fallback"],
                             parent_prefix_seconds=row["parent_prefix_seconds"])), flush=True)
    fallback_scalar(args, protocol, economy, out, failure)
    payload = dict(schema="nbo-r16-menu-fit-child-v1", method=args.method,
        calibration=args.calibration, dimension=args.dimension, seed=args.seed,
        continuation_identity=economy.continuation_identity,
        continuation_sha256=economy.continuation_sha256,
        all_declared_stages_written=True, failed_fit=failure is not None,
        final_confirmation_read=False, counters=dict(run.counters))
    write(out/"CANDIDATE_FIT.json", payload)


def parent(args):
    protocol_path = Path(args.protocol).resolve()
    protocol = json.loads(protocol_path.read_text())
    if args.method not in protocol["methods"] or args.seed not in protocol["training_streams"]["seeds"]:
        raise ValueError("method or training stream was not declared before confirmation")
    if args.dimension not in protocol["dimensions"]:
        raise ValueError("undeclared dimension")
    if args.calibration not in [x["id"] for x in protocol["calibrations"]]:
        raise ValueError("undeclared calibration")
    source, source_files = verify_source(protocol_path, protocol)
    out = Path(args.out).resolve()
    if out.exists() and any(out.iterdir()):
        raise FileExistsError("a complete method stream cannot overwrite prior evidence")
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    for key in ["OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMBA_NUM_THREADS"]:
        env[key] = "1"
    env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    started = time.perf_counter_ns()
    env["NBO_R16_MENU_PARENT_PERF_NS"] = str(started)
    cmd = [sys.executable, str(Path(__file__).resolve()), "--_fit", "--protocol", str(protocol_path),
        "--calibration", args.calibration, "--dimension", str(args.dimension), "--seed", str(args.seed),
        "--method", args.method, "--out", str(out)]
    usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    process_failure = None
    with (out/"fit.stdout").open("w") as log:
        try:
            result = subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                timeout=protocol["execution"]["method_timeout_seconds"], check=False)
            if result.returncode != 0:
                process_failure = dict(type="child_exit", returncode=result.returncode)
        except subprocess.TimeoutExpired:
            process_failure = dict(type="declared_timeout", timeout_seconds=protocol["execution"]["method_timeout_seconds"])
        log.flush(); os.fsync(log.fileno())
    if process_failure is not None or not (out/"CANDIDATE_FIT.json").is_file():
        # A crashed process is never silently rerun or assigned a replacement
        # seed. Keep every previously completed prefix and fill only missing
        # prefixes with the prospectively declared feasible fallback.
        import numpy as np
        from menu_economy import fixed_queries, load_economy
        economy = load_economy(protocol, args.calibration, args.dimension)
        queries = fixed_queries(protocol, args.dimension)
        reason = process_failure or dict(type="missing_child_completion_record")
        write(out/"PROCESS_FAILURE.json", dict(**reason, source_commit=source,
            seconds=(time.perf_counter_ns()-started)/1e9, command=cmd, final_confirmation_read=False))
        last_counters = {}
        for stage in range(1, len(protocol["training"]["cumulative_replay_states"])+1):
            record_path = out/f"stage{stage}.json"
            action_path = out/f"actions_stage{stage}.npz"
            preserved, invalid_reason = preserved_prefix(out, stage, args, economy, queries, source)
            if preserved is not None:
                last_counters = preserved["counters"]
                continue
            archive = archive_unsealed_stage(out, stage,
                dict(process_failure=reason, prefix_validation=invalid_reason))
            actions = np.broadcast_to(np.maximum(queries["lower"],
                np.minimum(queries["upper"], economy.schedule[0])), queries["states"].shape).copy()
            np.savez_compressed(action_path, actions=actions,
                **{k: queries[k] for k in ["states", "task_id", "state_id", "utility_weight", "adjustment", "lower", "upper"]})
            fallback = dict(stage=stage, method=args.method, fallback=True,
                fallback_policy="reference current schedule clipped to the temporary constraint",
                failure=reason, actions_file=action_path.name, actions_sha256=sha(action_path),
                counters=last_counters, continuation_sha256=economy.continuation_sha256,
                query_catalog_sha256=queries["catalog_sha256"],
                recovery_archive=archive)
            seal_stage(out, fallback, args, economy, queries, started, source)
        fallback_scalar(args, protocol, economy, out, reason)
        write(out/"CANDIDATE_FIT.json", dict(schema="nbo-r16-menu-fit-child-v1",
            method=args.method, calibration=args.calibration, dimension=args.dimension, seed=args.seed,
            continuation_identity=economy.continuation_identity,
            continuation_sha256=economy.continuation_sha256,
            all_declared_stages_written=True, failed_fit=True,
            final_confirmation_read=False, counters=last_counters))
    complete = (time.perf_counter_ns()-started)/1e9
    usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    child_record = json.loads((out/"CANDIDATE_FIT.json").read_text())
    inventory = {}
    for path in sorted(out.rglob("*")):
        if path.is_file():
            inventory[str(path.relative_to(out))] = dict(sha256=sha(path), bytes=path.stat().st_size)
    write(out/"FIT_WORK.json", dict(schema="nbo-r16-menu-fit-work-v1",
        source_commit=source, source_files=source_files, protocol_sha256=sha(protocol_path),
        method=args.method, calibration=args.calibration, dimension=args.dimension, seed=args.seed,
        complete_fit_seconds=complete,
        clock_scope="parent launch through scientific child completion, durable candidates and log; verification separately charged",
        environment_installation_included=False,
        source_manifest_validation_included=False,
        source_archive_extraction_included=False,
        user_cpu_seconds=usage_after.ru_utime-usage_before.ru_utime,
        system_cpu_seconds=usage_after.ru_stime-usage_before.ru_stime,
        peak_child_rss_bytes=int(usage_after.ru_maxrss)*1024,
        failed_fit=child_record["failed_fit"], final_confirmation_read=False,
        counters=child_record["counters"],
        counters_complete=not child_record["failed_fit"],
        counter_scope="complete recorded counts for successful execution; only known completed counts after a failure, while the full process clock remains charged",
        payload_inventory=inventory))
    print(json.dumps(dict(out=str(out), source_commit=source,
        complete_fit_seconds=complete, failed_fit=child_record["failed_fit"])), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--calibration", required=True)
    parser.add_argument("--dimension", required=True, type=int)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--method", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--_fit", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    child(args) if args._fit else parent(args)


if __name__ == "__main__":
    main()
