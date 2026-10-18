"""Preserve source and run custody for unchanged R117/R118 reproductions.

This orchestrator does not change either frozen scientific executable. Every
requested episode gets new outputs, checked source bytes, all process logs,
and an explicit failure or success receipt. Scientific timing stages run
sequentially with one numerical-library thread and must not overlap R119's
new-investment timing campaign.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
R117_PROTOCOL = "e65a0180896406610922e48f65bcf7f55ada366f"
R117_FREEZE = "a21e33471047b966dd375d0b9aceab6b9492e4fb"
R118_PROTOCOL = "7f6864e9fca9929b4f171e44ce3c558614b8ea06"
R118_FREEZE = "17ed16688f2f66924915192d3db7035c86bc846c"
R108_FREEZE = "29180a4ce4a6db7298e7458ecdfff3da08abb08f"
THREAD_VARIABLES = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def checked_commit(commit, paths):
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise ValueError("The actual 40-character committed R119 source/custody identity is required")
    repository = Path(subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "--show-toplevel"], text=True).strip())
    kind = subprocess.check_output(["git", "-C", str(repository), "cat-file", "-t", commit], text=True).strip()
    if kind != "commit":
        raise ValueError("Custody identity is not a Git commit")
    verified = {}
    for path in sorted(set(paths)):
        relative = path.relative_to(repository).as_posix()
        committed = subprocess.check_output(["git", "-C", str(repository), "show", commit + ":" + relative])
        if path.read_bytes() != committed:
            raise RuntimeError("Source differs from actual custody commit: " + relative)
        verified[relative] = hashlib.sha256(committed).hexdigest()
    return verified


def frozen_files(episode):
    folder = ROOT / ("frozen117" if episode == "r117" else "frozen118")
    manifest = folder / ("SOURCE_FREEZE117.json" if episode == "r117" else "SOURCE_FREEZE118.json")
    info = json.loads(manifest.read_text())
    files = [manifest, folder / ("PROTOCOL117.md" if episode == "r117" else "PROTOCOL118.md")]
    for name, expected in info["files"].items():
        path = folder / name
        if digest(path) != expected:
            raise RuntimeError("Different original frozen source: " + str(path))
        files.append(path)
    return folder, files


def run_episode(episode, output, custody_commit):
    if output.exists():
        raise FileExistsError("Preserve every previous attempt; choose a new output: " + str(output))
    folder, files = frozen_files(episode)
    files += [Path(__file__), ROOT / "REVISION_BOUNDARY119.md"]
    if episode == "r117":
        files.append(ROOT / "code119" / "independent_exact117_audit119.py")
    verified = checked_commit(custody_commit, files)
    output.mkdir(parents=True)
    logs = output / "logs119"
    logs.mkdir()
    started = time.perf_counter()
    commands = []
    environment = os.environ.copy()
    for variable in THREAD_VARIABLES:
        environment[variable] = "1"
    environment["PYTHONHASHSEED"] = "0"
    environment["NBO_SOURCE117"] = R117_FREEZE
    environment["NBO_PROTOCOL108"] = R108_FREEZE
    protocol, freeze = ((R117_PROTOCOL, R117_FREEZE) if episode == "r117"
                        else (R118_PROTOCOL, R118_FREEZE))
    custody = {
        "episode": episode, "run_kind": "R119 new-host reproduction of unchanged frozen protocol",
        "custody_commit": custody_commit, "original_protocol_commit": protocol,
        "original_executable_freeze_commit": freeze, "started_unix": time.time(),
        "python": sys.version, "python_executable": sys.executable, "platform": platform.platform(),
        "numerical_thread_environment": {v: environment[v] for v in THREAD_VARIABLES},
        "git_verified_current_source_sha256": verified,
        "output_directory": str(output),
        "scope": "New attributable reproduction. It does not replace original observations, old clocks, "
                 "failed CI, R98/R115 samples, or another frozen experiment.",
    }
    write(output / "CUSTODY_START119.json", custody)

    def execute(name, arguments, cwd=folder):
        log = logs / (name + ".log")
        before = time.perf_counter()
        command = [sys.executable] + [str(a) for a in arguments]
        print("START", episode, name, flush=True)
        with log.open("w") as stream:
            process = subprocess.run(command, cwd=cwd, env=environment,
                                     stdout=stream, stderr=subprocess.STDOUT)
        receipt = {"stage": name, "command": command, "cwd": str(cwd),
                   "exit_code": process.returncode, "seconds": time.perf_counter() - before,
                   "log": str(log.relative_to(output)), "log_sha256": digest(log)}
        commands.append(receipt)
        write(output / "COMMAND_PROGRESS119.json", {"commands": commands})
        print("END", episode, name, "exit", process.returncode,
              "seconds", round(receipt["seconds"], 3), flush=True)
        if process.returncode:
            raise RuntimeError("Scientific stage failed; original outputs retained: " + name)

    try:
        if episode == "r117":
            execute("frozen108-preflight", [folder / "frozen108/code108/test108.py"])
            execute("frozen117-preflight", [folder / "code117/test117.py"])
            execute("full-frozen117-campaign", [folder / "code117/campaign117.py", "all", "--output", output])
            execute("frozen117-exact-record-audit", [folder / "code117/audit117.py", "--output", output])
            execute("new-independent-exact117-audit", [ROOT / "code119/independent_exact117_audit119.py",
                    "--input", output / "EXACT117.json", "--output", output / "EXACT117_INDEPENDENT119.json"])
            native_receipt = json.loads((output / "CAMPAIGN117.json").read_text())
            audit_receipt = json.loads((output / "AUDIT117.json").read_text())
            success = {
                "primary_decisions": native_receipt["primary_decisions"],
                "timing_decisions": native_receipt["timing_decisions"],
                "timing_processes": len(native_receipt["processes"]),
                "rational_record_checks": audit_receipt["rational_record_checks"],
                "kernel_checks": audit_receipt["kernel_checks"],
                "exact_method_rows": audit_receipt["exact_method_rows"],
            }
        else:
            native = output / "native118"
            execute("frozen118-exact-catalogue", [folder / "code118/recovery118.py", "--output", native,
                    "--freeze-commit", R118_FREEZE])
            execute("frozen118-independent-audit", [folder / "code118/audit118.py", "--output", native])
            receipt = json.loads((native / "AUDIT118.json").read_text())
            success = {k: receipt[k] for k in ("cells", "exact_record_checks", "exhaustive_grid_actions",
                       "strict_improvements", "equal_regret", "nonzero_width_zero_regret")}
        result = {"status": "passed", "custody": custody, "commands": commands,
                  "scientific_summary": success, "finished_unix": time.time(),
                  "total_wrapper_seconds": time.perf_counter() - started,
                  "scientific_success_scope": "Only the actually completed frozen episode and named audits; "
                                               "not full-history theorem verification or neural-specific advantage."}
        write(output / "REPRODUCTION119.json", result)
        print("REPRODUCTION PASSED", episode, json.dumps(success, sort_keys=True), flush=True)
        return result
    except BaseException:
        write(output / "FAILED119.json", {"status": "failed", "custody": custody,
              "commands": commands, "exception": traceback.format_exc(),
              "elapsed_seconds": time.perf_counter() - started, "failed_unix": time.time(),
              "scope": "All existing output and logs retained. No retry or relabelling occurred."})
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--custody-commit", required=True)
    parser.add_argument("--only", choices=("all", "r117", "r118"), default="all")
    parser.add_argument("--output-base", type=Path, default=ROOT / "results119")
    arguments = parser.parse_args()
    requested = ("r117", "r118") if arguments.only == "all" else (arguments.only,)
    outputs = {name: arguments.output_base.resolve() / ("reproduction117" if name == "r117" else "reproduction118")
               for name in requested}
    # Discover conflicting prior attempts before starting any requested science.
    for path in outputs.values():
        if path.exists():
            raise FileExistsError("Do not overwrite a prior attempt: " + str(path))
    for name in requested:
        run_episode(name, outputs[name], arguments.custody_commit)


if __name__ == "__main__":
    main()
