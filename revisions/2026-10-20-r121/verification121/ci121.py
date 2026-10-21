"""Source-bound R121 evidence, deterministic replay and four-document CI.

This gate reads already completed scientific records. It replays only the
frozen statistical aggregation and the declared deterministic reporting code;
it never reacquires labels, refits actors, draws states, evaluates the economic
model, or retimes a policy. The actual final author commit is read from Git and
checked against GITHUB_SHA when supplied, never embedded self-referentially.

--precommit is a local candidate check, not a final-source CI assertion.
--skip-build verifies saved evidence/replay only, not the complete package gate.
Every output directory is new and every started command retains its log/exit.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import resource
import subprocess
import sys
import time
import traceback

PREFIX = "revisions/2026-10-20-r121"
DOCS = ("ECTA", "supp", "appendix", "RESPONSE_TO_REFEREE")
STATS_TABLES = ("ORIGINAL_OPTIMUM121.jsonl", "POLICY_GROUPS121.jsonl", "LOSS_CONTRASTS121.jsonl")
MANUSCRIPT_TABLES = ("new121/results121.tex", "new121/development121_results.tex")
EXCLUDED = {"EVIDENCE_MANIFEST121.json", "SOURCE_READY121.json"}
SHA1 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
CHUNK = 1 << 20


def require(value, message):
    if not value:
        raise ValueError(message)


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def relative(value):
    require(isinstance(value, str) and value, "A nonempty native-relative path is required")
    path = PurePosixPath(value)
    require(not path.is_absolute() and str(path) == value and ".." not in path.parts
            and "\\" not in value and not any(ord(c) < 32 or ord(c) == 127 for c in value),
            "Unsafe or noncanonical native path: " + repr(value))
    return path


def local(root, value):
    path = root.joinpath(*relative(value).parts)
    require(path.resolve().is_relative_to(root), "Input path leaves native revision")
    for item in (path, *path.parents):
        if item == root:
            break
        require(not item.is_symlink(), "Native input symlinks are not accepted")
    return path


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path):
    def invalid(value):
        raise ValueError("Nonfinite JSON value: " + value)
    return json.loads(path.read_bytes(), object_pairs_hook=unique, parse_constant=invalid)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def identity(path):
    require(path.is_file(), "Required regular input is missing: " + str(path))
    size = path.stat().st_size
    h = hashlib.sha256()
    g = hashlib.sha1(b"blob " + str(size).encode() + b"\0")
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK), b""):
            h.update(block)
            g.update(block)
    return dict(bytes=size, sha256=h.hexdigest(), git_blob=g.hexdigest())


def match(actual, wanted, fields=("bytes", "sha256", "git_blob")):
    require(all(actual[key] == wanted[key] for key in fields), "Actual input identity differs from manifest")


def git(repo, *argv):
    return subprocess.check_output(["git", "-C", str(repo), *argv])


def git_tree(repo, commit):
    require(isinstance(commit, str) and SHA1.fullmatch(commit), "A complete immutable Git commit is required")
    result = {}
    for item in git(repo, "ls-tree", "-r", "-z", commit, "--", PREFIX).split(b"\0"):
        if not item:
            continue
        metadata, name = item.split(b"\t", 1)
        mode, kind, blob = metadata.decode().split()
        path = name.decode()
        require(path.startswith(PREFIX + "/") and kind == "blob" and mode in ("100644", "100755"),
                "Only regular native Git files are accepted")
        result[path[len(PREFIX) + 1:]] = dict(mode=mode, git_blob=blob)
    return result


def ancestor(repo, early, late):
    require(early != late, "Required custody boundaries must be distinct")
    result = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", early, late],
                            capture_output=True)
    require(result.returncode == 0, "Missing required custody ancestry: " + early + " -> " + late)


def native_reporting_links(root, report, manifest):
    """Bind the two native TeX copies to the original deterministic report."""
    rows = manifest["stable_replay_files"]
    require(isinstance(rows, list), "Stable report inventory must be a file-record list")
    files = {str(relative(row["path"])): row for row in rows}
    require(len(files) == len(rows), "Original stable report inventory contains duplicate paths")
    linked = []
    for name in MANUSCRIPT_TABLES:
        require(name in files, "Native manuscript table is absent from the stable report inventory: " + name)
        original = identity(local(report, name))
        native = identity(local(root, name))
        match(original, files[name])
        match(native, original)
        linked.append(dict(native_path=name, original_report_path=local(report, name).relative_to(root).as_posix(),
            **native, exact_original_report_bytes_equal=True))
    return linked


def validate_build(root, receipt, pdf_expected):
    require(receipt.get("status") == "compiled_clean" and receipt.get("diagnostic") is False,
            "A completed strict clean source build is required")
    require(not receipt.get("issues") and not receipt.get("placeholders"), "Source build has unresolved diagnostics")
    require(receipt.get("scientific_execution") is False, "Document build scope must be explicit")
    require(receipt.get("source_date_epoch") == "1792454400", "Unexpected deterministic source epoch")
    commands = receipt.get("commands", [])
    require(commands and all(row.get("exit_code") == 0 and row.get("status") == "passed" for row in commands),
            "Every declared source build command must actually succeed")
    for row in commands:
        log = local(root, row["log"])
        require(identity(log)["sha256"] == row["log_sha256"], "Actual build command log identity")
    produced = {row["path"]: row for row in receipt.get("pdfs", [])}
    require(set(produced) == set(pdf_expected) and len(receipt["pdfs"]) == 4, "All four actual source PDFs")
    for name, expected in pdf_expected.items():
        match(produced[name], expected, ("bytes", "sha256"))
    require(identity(root / "build121.py")["sha256"] == receipt["builder_sha256"], "Actual strict builder source")
    for field in ("source_sha256", "graphic_asset_sha256"):
        require(isinstance(receipt.get(field), dict), "Source build dependency hashes are required")
        for name, wanted in receipt[field].items():
            require(identity(local(root, name))["sha256"] == wanted, "Source build input changed: " + name)
    require(set(receipt.get("actual_project_inputs", {})) == set(DOCS), "Four complete recorder closures are required")
    for entries in receipt["actual_project_inputs"].values():
        for name, wanted in entries.items():
            require(identity(local(root, name))["sha256"] == wanted, "Actual TeX recorder input changed: " + name)


class Gate:
    def __init__(self, args):
        self.args = args
        self.root = Path(__file__).resolve().parents[1]
        self.repo = Path(git(self.root, "rev-parse", "--show-toplevel").decode().strip()).resolve()
        require(self.root.relative_to(self.repo).as_posix() == PREFIX, "Unexpected native revision location")
        self.out = args.output.resolve()
        require(args.skip_build or self.out.is_relative_to(self.root),
                "A build-enabled gate output must lie under the native revision for recorder-relative log paths")
        self.out.mkdir(parents=True, exist_ok=False)
        self.started = utc()
        self.clock = time.perf_counter()
        self.head = git(self.repo, "rev-parse", "HEAD").decode().strip()
        self.commands = []
        self.initial_files = {}
        self.script_identity = identity(Path(__file__).resolve())
        self.env = dict(os.environ)
        for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
            self.env[name] = "1"
        self.env["PYTHONHASHSEED"] = "0"
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"
        write_json(self.out / "START_CI121.json", dict(kind="r121-author-package-ci-v1", status="started",
            started_utc=self.started, checked_out_commit=self.head, github_sha=os.environ.get("GITHUB_SHA"),
            precommit=args.precommit, skip_build=args.skip_build, source=vars(args) | {"output": str(args.output)},
            python=sys.version, platform=platform.platform(), ci_source=self.script_identity,
            original_economic_execution_performed=False))

    def command(self, name, argv):
        logfile = self.out / (name + ".log")
        started = utc()
        clock = time.perf_counter()
        row = dict(stage=name, argv=list(map(str, argv)), working_directory=str(self.root),
                   started_utc=started, status="started", exit_code=None, log=logfile.name)
        write_json(self.out / (name + ".START.json"), row)
        try:
            with logfile.open("xb") as output:
                process = subprocess.run(row["argv"], cwd=self.root, env=self.env,
                                         stdout=output, stderr=subprocess.STDOUT)
                output.flush()
                os.fsync(output.fileno())
            row["exit_code"] = process.returncode
            row["status"] = "passed" if process.returncode == 0 else "failed_exit"
        except BaseException as error:
            row.update(status="launch_or_execution_exception", exception=repr(error))
            raise
        finally:
            row.update(ended_utc=utc(), elapsed_seconds=time.perf_counter() - clock)
            if logfile.exists():
                row["log_identity"] = identity(logfile)
            self.commands.append(row)
            write_json(self.out / (name + ".RESULT.json"), row)
        require(row["exit_code"] == 0, "Command failed; retained log: " + str(logfile))
        print(json.dumps(dict(stage=name, exit_code=0, elapsed_seconds=row["elapsed_seconds"])), flush=True)

    def source_gate(self):
        github = os.environ.get("GITHUB_SHA")
        if github:
            require(github == self.head, "GITHUB_SHA does not match actual checked-out HEAD")
        ready_path = local(self.root, self.args.ready)
        runs_path = local(self.root, self.args.runs)
        manifest_path = local(self.root, self.args.manifest)
        ready, runs, manifest = map(read_json, (ready_path, runs_path, manifest_path))
        require(ready.get("kind") == "nbo-r121-final-author-source-ready-v1", "Final author source marker required")
        require(runs.get("kind") == "nbo-r121-run-registry-v1", "Declared R121 run registry required")
        require(manifest.get("kind") == "nbo-r121-complete-evidence-manifest-v1"
                and manifest.get("revision_prefix") == PREFIX, "Complete native evidence manifest required")
        require(ready["runs_path"] == self.args.runs and ready["manifest_path"] == self.args.manifest,
                "Source marker does not point to the selected registry/manifest")
        require(identity(runs_path)["sha256"] == ready["runs_sha256"]
                and identity(manifest_path)["sha256"] == ready["manifest_sha256"], "Source marker input hashes")
        require(set(manifest["excluded_paths"]) == EXCLUDED and len(manifest["excluded_paths"]) == 2,
                "Only the manifest and source marker are excluded from their self-referential list")
        require(self.args.manifest == "EVIDENCE_MANIFEST121.json" and self.args.ready == "SOURCE_READY121.json"
                and self.args.runs == "RUNS121.json", "Canonical native source-control filenames required")
        entries = {}
        for row in manifest["files"]:
            name = str(relative(row["path"]))
            require(name not in entries and name not in EXCLUDED, "Unique complete evidence paths")
            require(type(row.get("bytes")) is int and row["bytes"] >= 0
                    and SHA256.fullmatch(row.get("sha256", "")) and SHA1.fullmatch(row.get("git_blob", "")),
                    "Complete evidence file identity required")
            actual = identity(local(self.root, name))
            match(actual, row)
            entries[name] = row
            self.initial_files[name] = actual
        require(entries and "RUNS121.json" in entries and "verification121/ci121.py" in entries,
                "Complete evidence must include registry and executing CI source")
        tree = git_tree(self.repo, self.head)
        if not self.args.precommit:
            require(set(tree) == set(entries) | EXCLUDED, "Manifest must cover every native file at actual S")
            for name, row in entries.items():
                require(tree[name]["git_blob"] == row["git_blob"], "Native file differs from actual S: " + name)
            for name in EXCLUDED:
                require(tree[name]["git_blob"] == identity(local(self.root, name))["git_blob"], "Source-control file differs from S")
        commits = {key: runs[key] for key in ("source_commit", "actor_commit", "state_commit")}
        for value in commits.values():
            require(isinstance(value, str) and SHA1.fullmatch(value), "Complete F/M/D identities required")
        ancestor(self.repo, commits["source_commit"], commits["actor_commit"])
        ancestor(self.repo, commits["actor_commit"], commits["state_commit"])
        if self.head != commits["state_commit"]:
            ancestor(self.repo, commits["state_commit"], self.head)
        elif not self.args.precommit:
            raise ValueError("Final author S must follow the separately committed state boundary D")
        frozen = read_json(self.root / "SOURCE_FREEZE121.json")
        ftree = git_tree(self.repo, commits["source_commit"])
        for name, wanted in frozen["scientific_files"].items():
            actual = identity(local(self.root, name))
            require(actual["sha256"] == wanted and ftree[name]["git_blob"] == actual["git_blob"],
                    "Frozen scientific F byte differs: " + name)
        require(ftree["SOURCE_FREEZE121.json"]["git_blob"] == identity(self.root / "SOURCE_FREEZE121.json")["git_blob"],
                "Exact source freeze manifest at F")
        required = {"acquisition5", "acquisition9", "training_audit5", "training_audit9", "states", "primary", "independent", "stats", "report"}
        require(set(runs["paths"]) == required, "Complete declared successful attempt paths")
        self.paths = {name: local(self.root, value) for name, value in runs["paths"].items()}
        require(len(set(self.paths.values())) == len(required), "Scientific/report attempt paths must be distinct")
        self.runs = runs
        pdfs = ready["pdfs"]
        expected = {"build/" + name + ".pdf" for name in DOCS}
        require(len(pdfs) == 4 and {row["path"] for row in pdfs} == expected, "All four declared source PDF snapshots")
        self.pdfs = {row["path"]: row for row in pdfs}
        for name, row in self.pdfs.items():
            match(identity(local(self.root, name)), row, ("bytes", "sha256"))
            require(name in entries, "Each source PDF must be in complete S manifest")
        receipt_path = local(self.root, ready["source_build_receipt"])
        require(ready["source_build_receipt"] in entries, "Actual strict source build receipt must be source-bound")
        validate_build(self.root, read_json(receipt_path), self.pdfs)
        self.original_report_manifest = read_json(self.paths["report"] / "OUTPUT_MANIFEST121.json")
        require(self.original_report_manifest["reporting_source_sha256"] == identity(self.root / "code121/report121.py")["sha256"],
                "Original actual report and replay use identical reporting source")
        self.native_table_links = native_reporting_links(self.root, self.paths["report"], self.original_report_manifest)
        for row in self.native_table_links:
            require(row["native_path"] in entries and row["original_report_path"] in entries,
                    "Both native and original report TeX copies must be in the complete S evidence manifest")
        write_json(self.out / "NATIVE_MANUSCRIPT_TABLE_LINKAGE121.json", dict(status="verified",
            tables=self.native_table_links, complete_required_table_pair_verified=True,
            original_economic_reexecution=False))
        result = dict(status="verified", actual_checked_out_commit=self.head,
            final_author_source_binding=not self.args.precommit, local_precommit_scope=self.args.precommit,
            source_commits=commits, complete_evidence_files=len(entries),
            complete_native_git_census_checked=not self.args.precommit,
            source_manifest_sha256=identity(manifest_path)["sha256"], source_ready_sha256=identity(ready_path)["sha256"],
            scientific_files_at_F=len(frozen["scientific_files"]), scientific_source_modified=False,
            historical_and_transport_evidence_in_complete_manifest=True,
            native_manuscript_tables_match_original_report=True, original_scientific_execution=False)
        write_json(self.out / "SOURCE_GATE121.json", result)
        print(json.dumps(dict(stage="source-gate", files=len(entries), actual_head=self.head,
                              precommit=self.args.precommit)), flush=True)

    def reporting_args(self):
        args = []
        for key in ("source_commit", "actor_commit", "state_commit"):
            args += ["--" + key.replace("_", "-"), self.runs[key]]
        for key in ("acquisition5", "acquisition9", "training_audit5", "training_audit9", "states", "primary", "independent", "stats"):
            args += ["--" + key.replace("_", "-"), str(self.paths[key])]
        return args

    def replay(self):
        self.command("01-saved-record-integrity", [sys.executable, "verification121/study_integrity121.py",
            *self.reporting_args(), "--output", self.out / "integrity"])
        integrity = read_json(self.out / "integrity/EXECUTION_REPORT121.json")
        require(integrity["status"] == "executed" and integrity["exit_code"] == 0,
                "Saved-record integrity gate must complete")
        statout = self.out / "statistics-replay"
        self.command("02-frozen-statistics-replay", [sys.executable, "code121/stats121.py",
            "--source-commit", self.runs["source_commit"], "--primary", self.paths["primary"] / "records121.jsonl",
            "--independent", self.paths["independent"] / "comparisons121.jsonl", "--output", statout])
        comparisons = []
        for name in STATS_TABLES:
            old, new = identity(self.paths["stats"] / name), identity(statout / name)
            match(new, old)
            comparisons.append(dict(path=name, **new, exact_bytes_equal=True))
        write_json(self.out / "STATISTICS_REPLAY121.json", dict(status="verified", scientific_tables=comparisons,
            runtime_and_path_receipts_excluded_from_byte_equality=True, original_economic_reexecution=False))
        reportout = self.out / "reporting-replay"
        self.command("03-exact-reporting-replay", [sys.executable, "code121/report121.py",
            *self.reporting_args(), "--output", reportout])
        replay_manifest = read_json(reportout / "OUTPUT_MANIFEST121.json")
        oldrows = self.original_report_manifest["stable_replay_files"]
        newrows = replay_manifest["stable_replay_files"]
        old = {row["path"]: row for row in oldrows}
        new = {row["path"]: row for row in newrows}
        require(len(oldrows) == len(old) == len(newrows) == len(new) and set(old) == set(new),
                "Exact complete deterministic report file set required")
        for name, row in old.items():
            match(identity(local(self.paths["report"], name)), row)
            match(identity(local(reportout, name)), row)
            match(new[name], row)
        for name in MANUSCRIPT_TABLES:
            match(identity(local(self.root, name)), identity(local(reportout, name)))
        write_json(self.out / "REPORTING_REPLAY121.json", dict(status="verified", stable_file_count=len(old),
            stable_files=[dict(path=name, **identity(local(reportout, name))) for name in sorted(old)],
            complete_file_set_equal=True, native_manuscript_tables_equal_to_replay=list(MANUSCRIPT_TABLES),
            actual_source_sha256=replay_manifest["reporting_source_sha256"],
            runtime_and_custody_exclusions=self.original_report_manifest["explicitly_excluded_from_stable_equality"],
            original_economic_reexecution=False))

    def build(self):
        if self.args.skip_build:
            return
        receipts = self.out / "build-receipts"
        self.command("04-strict-four-document-build", [sys.executable, "build121.py", "--receipt-dir", receipts])
        found = list(receipts.glob("*/BUILD_RECEIPT121.json"))
        require(len(found) == 1, "Exactly one fresh strict CI build receipt")
        actual = read_json(found[0])
        comparison = [dict(path=name, expected={key: wanted[key] for key in ("bytes", "sha256")},
                           actual=identity(local(self.root, name)),
                           exact_bytes_equal=all(identity(local(self.root, name))[key] == wanted[key]
                                                 for key in ("bytes", "sha256")))
                      for name, wanted in self.pdfs.items()]
        write_json(self.out / "PDF_COMPARISON121.json", dict(documents=comparison,
            actual_strict_build_receipt=str(found[0]),
            comparison_before_requiring_all_source_PDF_bytes_equal=True))
        validate_build(self.root, actual, self.pdfs)
        for name, wanted in self.pdfs.items():
            match(identity(local(self.root, name)), wanted, ("bytes", "sha256"))
        write_json(self.out / "PDF_REPLAY121.json", dict(status="verified", exact_source_pdf_bytes_equal=True,
            documents=[dict(path=name, **identity(local(self.root, name))) for name in sorted(self.pdfs)],
            actual_strict_build_receipt=str(found[0]), tool_versions=actual["tool_versions"],
            scientific_execution=False))

    def run(self):
        try:
            self.source_gate()
            self.replay()
            self.build()
            require(git(self.repo, "rev-parse", "HEAD").decode().strip() == self.head, "Git HEAD changed during CI")
            require(identity(Path(__file__).resolve()) == self.script_identity, "CI gate source changed during execution")
            for name, old in self.initial_files.items():
                if not name.startswith("build/"):
                    match(identity(local(self.root, name)), old)
            status = ("passed_local_precommit_evidence_only" if self.args.skip_build else "passed_local_precommit_package") if self.args.precommit else ("passed_final_source_evidence_only" if self.args.skip_build else "passed_final_author_source_package")
            result = dict(kind="r121-author-package-ci-v1", status=status, exit_code=0,
                checked_out_commit=self.head, final_author_source_ci=not self.args.precommit,
                local_precommit_check=self.args.precommit,
                complete_author_package_gate=not self.args.skip_build,
                strict_build_and_all_four_pdf_hashes_verified=not self.args.skip_build,
                native_manuscript_tables_match_original_report_and_replay=True,
                original_economic_execution_performed=False,
                statistical_and_reporting_replay_only=True, commands=self.commands,
                started_utc=self.started, ended_utc=utc(), elapsed_seconds=time.perf_counter()-self.clock,
                child_peak_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                scientific_clocks_reused_from_original_receipts_not_retimed=True)
            write_json(self.out / "CI_RESULT121.json", result)
            print(json.dumps({key: result[key] for key in ("status", "checked_out_commit", "final_author_source_ci", "complete_author_package_gate", "elapsed_seconds")}), flush=True)
        except BaseException:
            write_json(self.out / "CI_FAILURE121.json", dict(kind="r121-author-package-ci-v1", status="failed",
                checked_out_commit=self.head, precommit=self.args.precommit, skip_build=self.args.skip_build,
                started_utc=self.started, ended_utc=utc(), elapsed_seconds=time.perf_counter()-self.clock,
                commands=self.commands, traceback=traceback.format_exc(), all_started_command_logs_retained=True,
                no_scientific_reexecution_or_automatic_retry=True))
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", default="RUNS121.json")
    parser.add_argument("--manifest", default="EVIDENCE_MANIFEST121.json")
    parser.add_argument("--ready", default="SOURCE_READY121.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--precommit", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    Gate(parser.parse_args()).run()


if __name__ == "__main__":
    main()
