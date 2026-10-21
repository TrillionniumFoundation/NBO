"""Prospectively published GitHub recovery orchestration around unchanged F/I/R.

This module never chooses a state, model, action, mesh, statistical threshold,
or service clock. It runs the existing continuation and records its real jobs.
Completed stage bytes are published after each validated continuation segment.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
REL = ROOT.relative_to(REPO).as_posix()
BRANCH = "revision/econometrica-nbo-r122-action-information-2026-10-20"
F = "2f483615c8bc0037e43ec01a16cce05c724f8c60"
D = "a3323b6f557315ea91b536637419ef6fd7984b61"
M = "796c5f2badf68b051ac6c144884c0e61b87faf5e"
I = "1f19410305c707716135defd91d6644d70657d84"
R = "0fe0f2bbf76529201a1890db0fc2a94b0be44418"
AF = "af73f9bca8f2249da1601208a1921f50ea8fd074"
RESTART = "56cff43b088c7d6b1cee352d27fc9de8573c46ed"
PRIMARY_SHA = "94fc7537e5020e464118c64076c8f6ace5ff3dd6d77b1e15d35dc3f2712e5044"
CACHE_SHA = "9588b3fa4cfeb3340106fc4879fa5343b75a9d8bb020b7fb40a8c104cc6e80ec"
OWN = (REL + "/verification122/recover_after_runtime_reset122.py",
       REL + "/provenance122/RUNTIME_RECOVERY_PROTOCOL122.md",
       ".github/workflows/nbo-r122-runtime-recovery.yml")
PYTHON = sys.executable


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write(path, data, exclusive=True):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w") as stream:
        json.dump(data, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def read(path):
    return json.loads(Path(path).read_text())


def relative(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Recovery output must be inside R122")
    return path.relative_to(ROOT).as_posix()


def git(*args, env=None, data=None):
    return subprocess.check_output(["git", *args], cwd=REPO, env=env, input=data)


class Recovery:
    def __init__(self, source):
        if os.environ.get("GITHUB_ACTIONS") != "true":
            raise RuntimeError("Real GitHub Actions execution required")
        if os.environ.get("GITHUB_REPOSITORY") != "TrillionniumFoundation/NBO":
            raise ValueError("Wrong repository")
        if os.environ.get("GITHUB_REF") != "refs/heads/" + BRANCH:
            raise ValueError("Recovery may run only on the isolated author branch")
        if Path(os.environ["GITHUB_WORKSPACE"]).resolve() != REPO:
            raise ValueError("Unexpected GitHub workspace")
        if source != os.environ["GITHUB_SHA"] or git("rev-parse", "HEAD").decode().strip() != source:
            raise ValueError("Actual checkout and triggering source differ")
        self.source = source
        self.run = os.environ["GITHUB_RUN_ID"]
        self.attempt = os.environ["GITHUB_RUN_ATTEMPT"]
        if not self.run.isdigit() or not self.attempt.isdigit():
            raise ValueError("Actual numeric workflow run/attempt required")
        self.prefix = "runtime-recovery-" + self.run + "-" + self.attempt
        self.admin = ROOT / "provenance122" / self.prefix
        self.admin.mkdir(parents=True, exist_ok=False)
        self.started = time.perf_counter()
        self.sequence = 0
        self.directories = []
        self.bundled = set()
        self.receipt = dict(status="started", source_commit=source, source_commit_F=F,
            state_commit_D=D, actor_commit_M=M, independent_schema_commit_I=I,
            continuation_commit_R=R, workflow_run_id=self.run,
            workflow_run_attempt=self.attempt, branch=BRANCH, started_utc=utc(),
            stages=[], publications=[], aliases=[], new_initial_states=0,
            new_training=0, new_primary_decisions=0, new_service_timing_replicates=0,
            prior_unpublished_completion_is_not_a_native_input=True,
            scope="New recovery audit executions on unchanged saved R122 inputs; actual new auditor clocks are additional research costs, never replacement service clocks.")
        self.save()

    def save(self):
        write(self.admin / "RECOVERY_STATUS122.json", self.receipt, exclusive=False)

    def stage(self, label, command, expected=(0,)):
        begin = time.perf_counter()
        path = self.admin / (label + ".log")
        with path.open("xb") as stream:
            result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
        row = dict(label=label, command=command, exit_code=result.returncode,
            elapsed_seconds=time.perf_counter()-begin, log=relative(path), log_sha256=sha(path))
        self.receipt["stages"].append(row)
        self.save()
        print(json.dumps({k: row[k] for k in ("label", "exit_code", "elapsed_seconds")}), flush=True)
        if result.returncode not in expected:
            print(path.read_text(errors="replace")[-12000:], flush=True)
            raise RuntimeError("Recovery stage failed: " + label)
        return result.returncode

    def launch(self, label, program, arguments, expected=(0,)):
        output = ROOT / "results122" / (self.prefix + "-" + label)
        launcher = ROOT / "results122" / ("launch-" + self.prefix + "-" + label)
        if output.exists() or launcher.exists():
            raise FileExistsError("Recovery stages must be new and exclusive")
        self.directories.extend([output, launcher])
        child = [PYTHON, program, *arguments, "--output", str(output)]
        code = self.stage(label, [PYTHON, "code122/launch122.py", "--receipt", str(launcher), "--", *child], expected)
        return output, code

    def initialize(self):
        bindings = []
        for name in OWN:
            path = REPO / name
            native = path.read_bytes()
            if git("show", self.source + ":" + name) != native:
                raise ValueError("Recovery source differs from its pre-execution publication: " + name)
            bindings.append(dict(path=name, bytes=len(native), sha256=sha(path),
                git_blob=hashlib.sha1(b"blob " + str(len(native)).encode() + b"\0" + native).hexdigest()))
        write(self.admin / "SOURCE_GATE122.json", dict(status="verified_before_recovery_economics",
            source_commit=self.source, source_tree=git("rev-parse", self.source + "^{tree}").decode().strip(),
            files=bindings, actual_workflow_run_id=self.run))
        for commit, depth in ((self.source, 40), (D, 16), (M, 1), (RESTART, 1), (AF, 1), (I, 1), (R, 1)):
            self.stage("fetch-" + commit[:8], ["git", "fetch", "--filter=tree:0", "--depth=" + str(depth), "origin", commit])
        manifest = read(ROOT / "SOURCE_FREEZE122.json")
        if len(manifest["scientific_files"]) != 243:
            raise ValueError("Original frozen scientific census differs")
        for name, digest in sorted(manifest["scientific_files"].items()):
            data = git("show", F + ":" + name)
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError("Frozen Git source differs: " + name)
            path = REPO / name
            if path.exists():
                if path.read_bytes() != data:
                    raise ValueError("Existing frozen bytes differ: " + name)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        # Only authentic earlier execution prefixes are restored. No existing
        # unrelated directory/symlink is replaced and no receipt is rewritten.
        for alias in (Path("/workspace/scratch/411f2ee67342/NBO"),
                      Path("/dev/shm/nbo-r122-411f2ee67342/NBO")):
            if alias == REPO or (alias.is_symlink() and alias.resolve() == REPO):
                action = "already_same_repository"
            elif alias.exists() or alias.is_symlink():
                raise ValueError("Refuse to replace unrelated historical prefix " + str(alias))
            else:
                subprocess.run(["sudo", "mkdir", "-p", str(alias.parent)], check=True)
                subprocess.run(["sudo", "ln", "-sT", str(REPO), str(alias)], check=True)
                action = "created_absent_authenticated_prefix"
            if alias.resolve() != REPO:
                raise ValueError("Historical prefix does not resolve to actual checkout")
            self.receipt["aliases"].append(dict(path=str(alias), action=action))
        self.stage("materialize-original", [PYTHON, "verification122/materialize_evidence122.py",
            "--registry", "transport122/REGISTRY122.json", "--output", relative(self.admin / "MATERIALIZATION122.json")])
        self.stage("prewarm", [PYTHON, "verification122/prewarm_git_objects122.py",
            "--source-commit", F, "--state-commit", D, "--resume-publication",
            "provenance122/RESUME_INDEPENDENT_PUBLICATION122.json", "--output", str(self.admin / "PREWARM122.json")])
        if sha(ROOT / "results122/primary-attempt02/records122.jsonl") != PRIMARY_SHA:
            raise ValueError("Original completed primary differs")
        if sha(ROOT / "results122/independent-cache-attempt01/CACHE_INDEX122.json") != CACHE_SHA:
            raise ValueError("Retained 716-policy cache differs")
        self.save()

    def publish(self, label, bundle=True):
        self.sequence += 1
        sequence = self.sequence
        newdirs = [p for p in self.directories if p.is_dir() and relative(p) not in self.bundled]
        request = None
        if bundle and newdirs:
            name = "transport122/bundles/" + self.prefix + "-" + str(sequence).zfill(3)
            archive = Path(os.environ["RUNNER_TEMP"]) / (self.prefix + "-" + str(sequence).zfill(3) + ".zip")
            self.stage("bundle-" + str(sequence).zfill(3), [PYTHON, "verification122/make_evidence_bundle122.py",
                "--directories", *[relative(p) for p in newdirs], "--bundle", name, "--archive", str(archive)])
            request = name + "/REQUEST122.json"
            # Actual independent CRC/SHA/native-byte readback before publication.
            temp_registry = self.admin / ("BUNDLE_REGISTRY" + str(sequence).zfill(3) + ".json")
            write(temp_registry, {"kind": "R122 recovery checkpoint subset", "requests": [request]})
            self.stage("materialize-" + str(sequence).zfill(3), [PYTHON, "verification122/materialize_evidence122.py",
                "--registry", relative(temp_registry), "--output", relative(self.admin / ("BUNDLE_READBACK" + str(sequence).zfill(3) + ".json"))])
        files = list(self.admin.rglob("*"))
        files = [p for p in files if p.is_file()]
        if request:
            files.extend((ROOT / request).parent.iterdir())
        files = sorted(set(p for p in files if p.is_file()))
        # Three bounded non-force attempts handle only a concurrent branch tip.
        # Every attempt records its real elapsed clock, including failures.
        attempts = []
        result = None
        for attempt in range(1, 4):
            tick = time.perf_counter()
            record = dict(attempt=attempt, started_utc=utc(), status="started")
            log = self.admin / ("publish-" + str(sequence).zfill(3) + "-" + str(attempt) + ".log")
            try:
                with log.open("xb") as stream:
                    subprocess.run(["git", "fetch", "--filter=tree:0", "--depth=1", "origin", BRANCH], cwd=REPO, stdout=stream, stderr=subprocess.STDOUT, check=True)
                    parent = git("rev-parse", "FETCH_HEAD").decode().strip()
                    registry_rel = REL + "/transport122/REGISTRY122.json"
                    registry = json.loads(git("show", parent + ":" + registry_rel))
                    if request and request not in registry["requests"]:
                        registry["requests"].append(request)
                    registry_bytes = (json.dumps(registry, indent=2, sort_keys=True) + "\n").encode()
                    with tempfile.TemporaryDirectory(prefix="nbo-r122-publish-", dir=os.environ["RUNNER_TEMP"]) as td:
                        env = {**os.environ, "GIT_INDEX_FILE": str(Path(td) / "index"),
                            "GIT_AUTHOR_NAME": "NBO verified recovery", "GIT_AUTHOR_EMAIL": "actions@users.noreply.github.com",
                            "GIT_COMMITTER_NAME": "NBO verified recovery", "GIT_COMMITTER_EMAIL": "actions@users.noreply.github.com"}
                        git("read-tree", parent, env=env)
                        manifest = []
                        payloads = [(p.relative_to(REPO).as_posix(), p.read_bytes()) for p in files]
                        payloads.append((registry_rel, registry_bytes))
                        for name, data in payloads:
                            obj = git("hash-object", "-w", "--stdin", data=data).decode().strip()
                            git("update-index", "--add", "--cacheinfo", "100644", obj, name, env=env)
                            manifest.append(dict(path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), git_blob=obj))
                        tree = git("write-tree", env=env).decode().strip()
                        message = "R122: preserve actual runtime recovery " + label + " (run " + self.run + ")\n"
                        commit = git("commit-tree", tree, "-p", parent, env=env, data=message.encode()).decode().strip()
                    pushed = subprocess.run(["git", "push", "origin", commit + ":refs/heads/" + BRANCH], cwd=REPO,
                        stdout=stream, stderr=subprocess.STDOUT)
                    if pushed.returncode:
                        raise RuntimeError("Non-force checkpoint push rejected; inspect recorded log")
                    remote = git("ls-remote", "origin", "refs/heads/" + BRANCH).decode().split()[0]
                    if remote != commit:
                        raise RuntimeError("Published checkpoint was not the actual remote branch head at readback")
                (ROOT / "transport122/REGISTRY122.json").write_bytes(registry_bytes)
                record.update(status="published", parent=parent, tree=tree, commit=commit,
                    files=manifest, branch=BRANCH, force=False, remote_readback_equal=True)
                result = commit
            except BaseException:
                record.update(status="failed", traceback=traceback.format_exc())
            finally:
                record.update(ended_utc=utc(), elapsed_seconds=time.perf_counter()-tick,
                    log=relative(log), log_sha256=sha(log))
                attempts.append(record)
            if result:
                break
        receipt = dict(status="executed" if result else "failed", source_commit_F=F,
            recovery_source_commit=self.source, checkpoint_label=label, workflow_run_id=self.run,
            commit=result, publication_attempts=attempts, actual_command=sys.argv,
            cost_clock_components=[dict(category="publication_git_observed",
                clock_fields=[["publication_attempts", j, "elapsed_seconds"]],
                scope="Actual checkpoint Git publication attempt only; excludes separately recorded scientific stages, transport creation and materialization.",
                partial_lower_bound_only=True, overlaps_counted_parent=False) for j in range(len(attempts))])
        destination = self.admin / ("CHECKPOINT" + str(sequence).zfill(3) + "_PUBLICATION122.json")
        write(destination, receipt)
        self.receipt["publications"].append(dict(path=relative(destination), sha256=sha(destination), commit=result))
        self.save()
        if not result:
            raise RuntimeError("Checkpoint publication failed; all native bytes remain for always-run artifact upload")
        self.bundled.update(relative(p) for p in newdirs)
        print(json.dumps(dict(checkpoint=label, commit=result, native_directories=len(newdirs))), flush=True)

    def resume(self):
        self.initialize()
        cache = ROOT / "results122/independent-cache-attempt01"
        base = ["--resume-commit", R, "--repair-commit", I, "--source-commit", F,
                "--primary", str(ROOT / "results122/primary-attempt02")]
        for j in range(1, 101):
            segment, code = self.launch("segment" + str(j).zfill(3), "verification122/resume_independent122.py",
                ["--mode", "segment", *base, "--cache", str(cache)], expected=(0, 75))
            meta = read(segment / "RESUME_SEGMENT122.json")
            expected = "planned_checkpoint" if code == 75 else "segment_complete_not_canonical"
            if meta["status"] != expected:
                raise ValueError("Actual segment status differs from its exit")
            cache, _ = self.launch("cache" + str(j + 1).zfill(3), "verification122/resume_independent122.py",
                ["--mode", "cache", *base, "--cache", str(cache), "--segment", str(segment)])
            self.receipt["latest_validated_cache"] = relative(cache)
            self.receipt["latest_evaluation_count"] = read(cache / "CACHE_INDEX122.json")["evaluation_count"]
            self.save()
            self.publish("validated segment " + str(j))
            if code == 0:
                break
        else:
            raise RuntimeError("Administrative100-segment cap reached; do not alter original precision or rule")
        canonical, _ = self.launch("canonical", "verification122/resume_independent122.py",
            ["--mode", "finalize", *base, "--cache", str(cache)])
        meta = read(canonical / "RESUME_SEGMENT122.json")
        if meta["status"] != "canonical_complete" or meta["fresh_policy_calls"] != 0:
            raise ValueError("Canonical finalization must finish with zero new economic calls")
        self.receipt["canonical_directory"] = relative(canonical)
        self.receipt["canonical_receipt_sha256"] = sha(canonical / "RESUME_SEGMENT122.json")
        self.publish("canonical complete independent evidence")
        composite = self.admin / "composite-verification"
        self.stage("composite-verification", [PYTHON, "verification122/verify_independent_resume122.py",
            "--resume-publication", "provenance122/RESUME_INDEPENDENT_PUBLICATION122.json",
            "--primary", "results122/primary-attempt02", "--independent", str(canonical), "--output", str(composite)])
        self.receipt["composite_verification"] = relative(composite / "VERIFICATION_RESUME122.json")
        stats, _ = self.launch("statistics", "code122/stats122.py", ["--source-commit", F,
            "--primary", "results122/primary-attempt02", "--independent", str(canonical)])
        report_args = ["--source-commit", F, "--primary", "results122/primary-attempt02",
            "--independent", str(canonical), "--stats", str(stats)]
        original_report, _ = self.launch("original-report", "code122/report122.py", report_args, expected=(1,))
        if "multiple values for keyword argument" not in read(original_report / "FAILURE122.json")["traceback"]:
            raise ValueError("Frozen reporter failure differs from disclosed duplicate-key failure")
        report, _ = self.launch("adapted-report", "verification122/report_protocol_adapter122.py",
            ["--repair-commit", AF, *report_args])
        gate = self.admin / "report-verification"
        self.stage("report-verification", [PYTHON, "verification122/verify_package122.py", "--source-commit", F,
            "--state-commit", D, "--through", "report", "--independent", str(canonical),
            "--stats", str(stats), "--report", str(report), "--original-report", str(original_report), "--output", str(gate)])
        self.receipt.update(status="completed_recovery_science_and_report", statistics_directory=relative(stats),
            original_report_directory=relative(original_report), report_directory=relative(report),
            report_verification=relative(gate / "VERIFICATION122.json"),
            prior_primary_service_clocks_unchanged=True, original_economic_model_unchanged=True,
            independent_completion_claimed_only_from_current_native_receipts=True)
        self.save()
        self.publish("verified recovered science and complete report")

    def finish(self, failure=None):
        if failure is not None:
            self.receipt.update(status="failed", traceback=failure)
        self.receipt.update(finished_utc=utc(), orchestrator_elapsed_seconds=time.perf_counter()-self.started,
            orchestrator_elapsed_overlaps_nested_jobs_not_additive=True)
        self.save()
        # This last checkpoint publishes all preceding completed publication
        # receipts. Its own commit is recorded in the always-uploaded artifact.
        self.publish("terminal recovery custody", bundle=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    recovery = Recovery(args.source_commit)
    failure = None
    try:
        recovery.resume()
    except BaseException:
        failure = traceback.format_exc()
        print(failure, flush=True)
    try:
        recovery.finish(failure)
    except BaseException:
        print(traceback.format_exc(), flush=True)
        if failure is None:
            failure = traceback.format_exc()
    if failure:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
