"""Post-freeze execution recorder; never chooses or changes scientific inputs."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("label")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command or not args.label.replace("-", "").replace("_", "").isalnum():
        raise ValueError("An exclusive simple label and exact command are required")
    out = ROOT / "results120" / "launches" / args.label
    out.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
               MKL_NUM_THREADS="1", PYTHONUNBUFFERED="1")
    receipt = {"label": args.label, "argv": command, "cwd": str(ROOT),
               "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "driver_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "driver_scope": "post-freeze launch recording; no scientific design change",
               "thread_environment": {k: env[k] for k in
                   ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")},
               "head_at_launch": subprocess.check_output(
                   ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
               "status": "started", "exit_code": None}
    def save():
        (out / "LAUNCH120.json").write_text(json.dumps(receipt, indent=2) + "\n")
    save()
    print(json.dumps({"launch": args.label, "argv": command,
                      "started_utc": receipt["started_utc"]}), flush=True)
    start = time.perf_counter()
    code = 1
    try:
        with (out / "stdout.log").open("xb") as log:
            proc = subprocess.run(command, cwd=ROOT, env=env,
                                  stdout=log, stderr=subprocess.STDOUT)
        code = proc.returncode
        receipt.update(status="executed" if code == 0 else "failed_exit", exit_code=code)
    except BaseException as exc:
        receipt.update(status="launch_or_execution_exception",
                       exception_type=type(exc).__name__, exception=str(exc))
        raise
    finally:
        receipt.update(ended_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                       elapsed_seconds=time.perf_counter() - start)
        if (out / "stdout.log").exists():
            receipt["stdout_sha256"] = hashlib.sha256((out / "stdout.log").read_bytes()).hexdigest()
            receipt["stdout_bytes"] = (out / "stdout.log").stat().st_size
        save()
        print(json.dumps(receipt), flush=True)
    return code

if __name__ == "__main__":
    sys.exit(main())
