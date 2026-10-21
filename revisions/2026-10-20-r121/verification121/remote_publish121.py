"""Publish a complete, already validated R121 package from GitHub Actions.

No scientific code is imported or executed. Local bind precedes publication P.
Q is a single child of P adding only the canonical package request. Preparation
runs the unchanged P pack/verify/describe helpers outside the native tree. The
workflow uploads the complete ZIP before finalize writes part Git objects and
an additive child V. The actual pushed V is recorded after the push, never in
a self-referential receipt inside V. No full-size part copies are created.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.request

PREFIX = "revisions/2026-10-20-r121"
REPOSITORY = "TrillionniumFoundation/NBO"
BRANCH = "revision/econometrica-nbo-r121-action-marginal-learning-2026-10-20"
REQUEST_NATIVE = "delivery121/PACKAGE_REQUEST121.json"
REQUEST_REPO = PREFIX + "/" + REQUEST_NATIVE
WORKFLOW = ".github/workflows/nbo-r121-publication.yml"
CI_WORKFLOW = ".github/workflows/nbo-r121-author-package.yml"
PACKAGE = "REFEREE_READY_PACKAGE121.json"
DESCRIPTOR = "VIRTUAL_ZIP_CHUNKS121.json"
ARCHIVE = "referee-ready121.zip"
PART_SIZE = 8 << 20
CHUNK = 1 << 20
SHA1 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def canonical(value):
    require(isinstance(value, str) and value, "A nonempty relative POSIX path is required")
    path = PurePosixPath(value)
    require(not path.is_absolute() and value != "." and str(path) == value
            and ".." not in path.parts and "\\" not in value
            and not any(ord(c) < 32 or ord(c) == 127 for c in value),
            "Unsafe or noncanonical path: " + repr(value))
    return value


def local(root, name):
    path = root.joinpath(*PurePosixPath(canonical(name)).parts)
    require(path.resolve().is_relative_to(root), "Path leaves its declared root")
    for item in (path, *path.parents):
        if item == root:
            break
        require(not item.is_symlink(), "Symlinks are forbidden in publication inputs")
    return path


def unique(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, "Duplicate JSON key: " + key)
        obj[key] = value
    return obj


def decode(raw):
    def bad(value):
        raise ValueError("Nonfinite JSON number: " + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=bad)


def json_bytes(obj):
    return (json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(json_bytes(obj))
        stream.flush()
        os.fsync(stream.fileno())


def signature(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def identity_bytes(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                git_blob=hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest())


def identity_file(path):
    require(not path.is_symlink(), "A regular file is required")
    before = path.stat()
    require(stat.S_ISREG(before.st_mode), "A regular file is required")
    sha = hashlib.sha256()
    blob = hashlib.sha1(b"blob " + str(before.st_size).encode() + b"\0")
    total = 0
    with path.open("rb") as stream:
        require(signature(os.fstat(stream.fileno())) == signature(before), "Input changed before reading")
        for block in iter(lambda: stream.read(CHUNK), b""):
            total += len(block)
            sha.update(block)
            blob.update(block)
        require(signature(os.fstat(stream.fileno())) == signature(before), "Input changed during reading")
    require(signature(path.stat()) == signature(before) and total == before.st_size, "Input changed after reading")
    return dict(bytes=total, sha256=sha.hexdigest(), git_blob=blob.hexdigest())


def matches(actual, expected):
    for key in ("bytes", "sha256", "git_blob"):
        if key in expected:
            require(actual[key] == expected[key], "Byte identity mismatch: " + key)


def positive_id(value, label):
    text = str(value)
    require(text.isascii() and text.isdigit() and int(text) > 0, "Positive numeric " + label + " required")
    return text


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise ValueError("Unexpected redirect from authenticated GitHub metadata API")


class Job:
    def __init__(self, args):
        self.args = args
        self.repo = args.repository.resolve()
        self.native = self.repo / PREFIX
        self.work = args.work_dir.resolve()
        require(not self.work.is_relative_to(self.repo), "Publication staging must be outside the repository")
        if args.phase == "prepare":
            self.work.mkdir(parents=True, exist_ok=False)
        else:
            require(self.work.is_dir(), "Completed preparation directory is required")
        self.logs = self.work / "logs"
        self.logs.mkdir(exist_ok=True)
        self.started, self.clock = utc(), time.perf_counter()
        self.commands = []
        self.new_commit = None
        self.environment = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_OPTIONAL_LOCKS="0",
                                GIT_TERMINAL_PROMPT="0", PYTHONDONTWRITEBYTECODE="1")
        self.run_id = positive_id(os.environ.get("GITHUB_RUN_ID", ""), "GitHub run id")
        self.run_attempt = positive_id(os.environ.get("GITHUB_RUN_ATTEMPT", ""), "GitHub run attempt")
        require(os.environ.get("GITHUB_REPOSITORY") == REPOSITORY, "Unexpected GitHub repository context")
        require(os.environ.get("GITHUB_REF") == "refs/heads/" + BRANCH, "Unexpected GitHub branch context")
        self.q = args.request_commit
        require(SHA1.fullmatch(self.q) and os.environ.get("GITHUB_SHA") == self.q,
                "Complete Q must match actual Actions GITHUB_SHA")
        self.helper_identity = identity_file(Path(__file__).resolve())
        save(self.work / (args.phase.upper() + "_START121.json"), dict(
            kind="nbo-r121-remote-publication-stage-v1", phase=args.phase,
            request_commit=self.q, actual_run_id=self.run_id, actual_run_attempt=self.run_attempt, started_utc=self.started,
            helper=self.helper_identity, scientific_execution=False, original_results_recomputed=False))

    def command(self, label, argv, input_bytes=None):
        number = len(self.commands)
        prefix = f"{self.args.phase}-{number:04d}-{label}"
        stdout = self.logs / (prefix + ".stdout.log")
        stderr = self.logs / (prefix + ".stderr.log")
        row = dict(label=label, argv=list(map(str, argv)), cwd=str(self.repo),
            started_utc=utc(), status="started", exit_code=None,
            stdout=stdout.relative_to(self.work).as_posix(), stderr=stderr.relative_to(self.work).as_posix())
        if input_bytes is not None:
            row["stdin_identity"] = identity_bytes(input_bytes)
        self.commands.append(row)
        save(self.logs / (prefix + ".START.json"), row)
        start = time.perf_counter()
        try:
            with stdout.open("xb") as out, stderr.open("xb") as err:
                result = subprocess.run(row["argv"], cwd=self.repo, env=self.environment,
                                        input=input_bytes, stdout=out, stderr=err)
                out.flush()
                err.flush()
                os.fsync(out.fileno())
                os.fsync(err.fileno())
            row.update(exit_code=result.returncode, status="passed" if result.returncode == 0 else "failed_exit")
        except BaseException as error:
            row.update(status="launch_or_execution_exception", exception=repr(error))
            raise
        finally:
            row.update(ended_utc=utc(), elapsed_seconds=time.perf_counter()-start)
            if stdout.exists():
                row["stdout_identity"] = identity_file(stdout)
            if stderr.exists():
                row["stderr_identity"] = identity_file(stderr)
            save(self.logs / (prefix + ".RESULT.json"), row)
        require(row["exit_code"] == 0, "Actual command failed: " + label)
        return stdout.read_bytes()

    def git(self, *args, input_bytes=None):
        return self.command("git-" + str(args[0]), ["git", *args], input_bytes)

    def metadata(self, route, label):
        require(route.startswith("/repos/" + REPOSITORY + "/actions/"), "Only this repository's Actions metadata API is allowed")
        token = os.environ.get("GITHUB_TOKEN")
        require(token, "The narrowly scoped Actions token is required")
        url = "https://api.github.com" + route
        request = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json", "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "NBO-R121-publication"})
        opener = urllib.request.build_opener(NoRedirect())
        started = utc()
        try:
            with opener.open(request, timeout=60) as response:
                require(response.status == 200 and response.geturl() == url, "Unexpected metadata response")
                raw = response.read(8 << 20)
                require(not response.read(1), "Metadata response exceeds its bounded size")
                status = response.status
        except urllib.error.HTTPError as error:
            raw = error.read(65536)
            save(self.work / (label + "-failure.json"), dict(url=url, status=error.code,
                response_identity=identity_bytes(raw), started_utc=started, ended_utc=utc(),
                authorization_header_recorded=False))
            raise
        result = decode(raw)
        save(self.work / (label + ".json"), dict(url=url, status=status, started_utc=started,
            ended_utc=utc(), response_identity=identity_bytes(raw), response=result,
            authorization_header_recorded=False))
        return result

    def tree(self, commit):
        require(SHA1.fullmatch(commit), "Complete immutable Git commit required")
        # Only native R121 files and the two relevant workflows can enter
        # this publication. Avoid materializing unrelated revision trees.
        data = self.git("ls-tree", "-r", "-z", commit, "--", PREFIX + "/", WORKFLOW, CI_WORKFLOW)
        result = {}
        for item in data.split(b"\0"):
            if not item:
                continue
            metadata, name = item.split(b"\t", 1)
            mode, kind, blob = metadata.decode().split()
            result[name.decode("utf-8")] = dict(mode=mode, kind=kind, git_blob=blob)
        return result

    def compare_remote_q(self):
        raw = self.git("ls-remote", "--exit-code", "origin", "refs/heads/" + BRANCH).decode().split()
        require(raw == [self.q, "refs/heads/" + BRANCH], "Remote branch no longer equals the authorized Q")

    def context(self, query_ci=False):
        require(Path(self.git("rev-parse", "--show-toplevel").decode().strip()).resolve() == self.repo,
                "Actual Git repository root differs")
        require(self.git("rev-parse", "HEAD").decode().strip() == self.q, "Actual checkout is not Q")
        require(self.git("rev-parse", "--show-object-format").decode().strip() == "sha1", "SHA-1 Git object format required")
        require(not self.git("status", "--porcelain=v1", "--untracked-files=no").strip(),
                "Tracked worktree and index must be clean before publication staging")
        request_path = local(self.native, REQUEST_NATIVE)
        request_info = identity_file(request_path)
        request = decode(request_path.read_bytes())
        require(request.get("kind") == "nbo-r121-remote-publication-request-v1"
                and request.get("revision_prefix") == PREFIX, "Unexpected Q request schema")
        self.s, self.p = request["author_source_commit"], request["publication_commit"]
        require(SHA1.fullmatch(self.s) and SHA1.fullmatch(self.p) and len({self.s, self.p, self.q}) == 3,
                "Distinct full S/P/Q identities are required")
        parents = self.git("rev-list", "--parents", "-n", "1", self.q).decode().split()
        require(parents == [self.q, self.p], "Q must be the single direct child of P")
        change = [part for part in self.git("diff", "--name-status", "--no-renames", "-z", self.p, self.q).split(b"\0") if part]
        require(change == [b"A", REQUEST_REPO.encode()], "Q must add only the canonical package request")
        self.git("merge-base", "--is-ancestor", self.s, self.p)
        self.ptree, self.qtree = self.tree(self.p), self.tree(self.q)
        stree = self.tree(self.s)
        matches(request_info, self.qtree[REQUEST_REPO])
        helpers = [PREFIX + "/verification121/remote_publish121.py",
                   PREFIX + "/verification121/publication121.py",
                   PREFIX + "/verification121/remote_verify121.py", WORKFLOW, CI_WORKFLOW]
        helper_rows = []
        for name in helpers:
            require(name in stree and stree[name] == self.ptree.get(name) == self.qtree.get(name)
                    and stree[name]["kind"] == "blob" and stree[name]["mode"] in {"100644", "100755"},
                    "Publication helper/workflow bytes must already exist unchanged at S and P")
            actual = identity_file(local(self.repo, name))
            matches(actual, stree[name])
            helper_rows.append(dict(path=name, **actual))
        records = request["required_records"]
        require(set(records) == {"author_source_ci_result", "author_source_ci_remote_readback"},
                "Exact actual CI and remote readback paths are required")
        required = {canonical(name) for name in records.values()}
        extra = request.get("required_publication_paths", [])
        require(isinstance(extra, list), "Required publication paths must be a list")
        required.update(canonical(name) for name in extra)
        require(len(set(records.values())) == 2, "The actual CI result and remote readback need separate paths")
        bound_records = []
        for name in sorted(required):
            full = PREFIX + "/" + name
            require(full in self.ptree and self.ptree[full]["kind"] == "blob", "Required publication record is absent from P")
            actual = identity_file(local(self.native, name))
            matches(actual, self.ptree[full])
            bound_records.append(dict(path=name, **actual))
        ci = decode(local(self.native, records["author_source_ci_result"]).read_bytes())
        require(ci.get("status") == "passed_final_author_source_package" and ci.get("exit_code") == 0
                and ci.get("checked_out_commit") == self.s and ci.get("final_author_source_ci") is True
                and ci.get("complete_author_package_gate") is True
                and ci.get("strict_build_and_all_four_pdf_hashes_verified") is True
                and ci.get("original_economic_execution_performed") is False,
                "Required saved CI result is not a successful complete actual S gate")
        run_id = positive_id(request["source_ci_run_id"], "source CI run id")
        readback = decode(local(self.native, records["author_source_ci_remote_readback"]).read_bytes())
        require(readback.get("source_commit") == self.s and readback.get("head_sha") == self.s
                and str(readback.get("run_id")) == run_id and readback.get("status") == "completed"
                and readback.get("conclusion") == "success" and readback.get("workflow_path") == CI_WORKFLOW,
                "Saved remote CI readback must identify the same completed successful actual S workflow run")
        if query_ci:
            run = self.metadata("/repos/" + REPOSITORY + "/actions/runs/" + run_id, "source-ci-api")
            require(str(run.get("id")) == run_id and run.get("head_sha") == self.s
                    and run.get("status") == "completed" and run.get("conclusion") == "success"
                    and run.get("path") == CI_WORKFLOW and run.get("head_branch") == BRANCH,
                    "The declared actual source workflow did not successfully validate S")
        self.compare_remote_q()
        self.request, self.required = request, sorted(required)
        self.context_record = dict(request_commit=self.q, publication_commit=self.p, author_source_commit=self.s,
            request=dict(path=REQUEST_REPO, **request_info), helper_files=helper_rows,
            required_records=bound_records, source_ci_run_id=run_id,
            actual_workflow_run_id=self.run_id, actual_workflow_run_attempt=self.run_attempt,
            repository=REPOSITORY, branch=BRANCH,
            Q_only_change_is_added_request=True, source_ancestor_publication=True)

    def failure(self):
        save(self.work / (self.args.phase.upper() + "_FAILURE121.json"), dict(
            kind="nbo-r121-remote-publication-failure-v1", phase=self.args.phase,
            request_commit=self.q, actual_workflow_run_id=self.run_id, actual_workflow_run_attempt=self.run_attempt,
            new_local_commit=self.new_commit, started_utc=self.started,
            ended_utc=utc(), elapsed_seconds=time.perf_counter()-self.clock,
            traceback=traceback.format_exc(), commands=self.commands,
            partial_outputs_retained=True, scientific_execution=False,
            successful_remote_publication_not_inferred=True))


def prepare(job):
    job.context(query_ci=True)
    helper = job.native / "verification121/publication121.py"
    packdir, verifydir, describedir = (job.work / name for name in ("pack", "verify", "describe"))
    command = [sys.executable, helper, "pack", "--revision", job.native,
        "--source-commit", job.s, "--publication-commit", job.p, "--no-split", "--output-dir", packdir]
    for name in job.required:
        command += ["--required-path", name]
    job.command("complete-publication-pack", command)
    archive = packdir / ARCHIVE
    manifest = packdir / PACKAGE
    manifest_info = identity_file(manifest)
    parsed = decode(manifest.read_bytes())
    require(parsed.get("split_performed") is False and parsed.get("parts") == []
            and parsed.get("author_source_commit") == job.s and parsed.get("publication_commit") == job.p,
            "Actual complete P package must have the requested no-split identity")
    job.command("independent-container-verify", [sys.executable, helper, "verify",
        "--manifest", manifest, "--archive", archive, "--source-commit", job.s,
        "--publication-commit", job.p, "--expected-manifest-sha256", manifest_info["sha256"],
        "--output-dir", verifydir])
    job.command("describe-exact-eight-MiB-ranges", [sys.executable, helper, "describe-parts",
        "--manifest", manifest, "--archive", archive, "--output-dir", describedir])
    virtual = describedir / DESCRIPTOR
    descriptor_info = identity_file(virtual)
    descriptor = decode(virtual.read_bytes())
    require(descriptor.get("future_prefix") == "" and descriptor.get("physical_chunk_files_written") == 0
            and descriptor.get("author_source_commit") == job.s and descriptor.get("publication_commit") == job.p,
            "Expected exact virtual root-native part description")
    matches(descriptor, parsed)
    matches(manifest_info, descriptor["package_manifest"])
    prepared = dict(kind="nbo-r121-remote-package-prepared-v1", status="package_prepared_and_verified",
        context=job.context_record, actual_archive=dict(path="pack/" + ARCHIVE,
            **{key: parsed[key] for key in ("bytes", "sha256", "git_blob")}),
        package_manifest=dict(path="pack/" + PACKAGE, **manifest_info),
        virtual_descriptor=dict(path="describe/" + DESCRIPTOR, **descriptor_info),
        artifact_name="nbo-r121-referee-ready-" + job.q + "-attempt" + job.run_attempt,
        commands=job.commands, started_utc=job.started, ended_utc=utc(),
        elapsed_seconds=time.perf_counter()-job.clock, helper=job.helper_identity,
        archive_verified_without_scientific_execution=True,
        no_physical_duplicate_parts_created=True, remote_upload_performed_by_helper=False,
        remote_commit_or_push_performed=False, artifact_upload_required_before_finalize=True)
    save(job.work / "PREPARED121.json", prepared)
    print(json.dumps(dict(status=prepared["status"], request_commit=job.q,
        archive_bytes=parsed["bytes"], archive_sha256=parsed["sha256"],
        package_manifest_sha256=manifest_info["sha256"], virtual_descriptor_sha256=descriptor_info["sha256"])), flush=True)


def artifact_check(job, prepared):
    aid = positive_id(job.args.artifact_id, "uploaded artifact id")
    digest = job.args.artifact_digest.removeprefix("sha256:")
    require(SHA256.fullmatch(digest), "Actual upload-artifact digest output required")
    expected_url = "https://github.com/" + REPOSITORY + "/actions/runs/" + job.run_id + "/artifacts/" + aid
    require(job.args.artifact_url == expected_url, "Actual artifact URL does not match this workflow run/id")
    artifact = job.metadata("/repos/" + REPOSITORY + "/actions/artifacts/" + aid, "uploaded-artifact-api")
    require(str(artifact.get("id")) == aid and artifact.get("name") == prepared["artifact_name"]
            and artifact.get("expired") is False, "Actual uploaded artifact identity differs")
    run = artifact.get("workflow_run", {})
    require(str(run.get("id")) == job.run_id and run.get("head_sha") == job.q,
            "Uploaded artifact did not come from the Q workflow run")
    api_digest = artifact.get("digest")
    if api_digest is not None:
        require(api_digest.removeprefix("sha256:") == digest, "Upload step and artifact API digest disagree")
    return dict(id=aid, url=expected_url, action_output_digest_sha256=digest,
        api_digest=api_digest, api_digest_available=api_digest is not None,
        bytes=artifact.get("size_in_bytes"), actual_workflow_run_id=job.run_id,
        actual_workflow_run_attempt=job.run_attempt,
        created_at=artifact.get("created_at"), expires_at=artifact.get("expires_at"),
        upload_completed_before_Git_object_staging=True,
        digest_scope="The uploaded Actions artifact container, not the inner referee-ready ZIP")


def finalize(job):
    job.context(query_ci=False)
    prepared_path = job.work / "PREPARED121.json"
    prepared = decode(prepared_path.read_bytes())
    require(prepared.get("kind") == "nbo-r121-remote-package-prepared-v1"
            and prepared.get("status") == "package_prepared_and_verified"
            and prepared["context"] == job.context_record, "Actual preparation does not match unchanged Q/P/S")
    matches(job.helper_identity, prepared["helper"])
    manifest_path = local(job.work, prepared["package_manifest"]["path"])
    descriptor_path = local(job.work, prepared["virtual_descriptor"]["path"])
    matches(identity_file(manifest_path), prepared["package_manifest"])
    matches(identity_file(descriptor_path), prepared["virtual_descriptor"])
    manifest, descriptor = decode(manifest_path.read_bytes()), decode(descriptor_path.read_bytes())
    matches(descriptor, manifest)
    matches(prepared["actual_archive"], manifest)
    artifact = artifact_check(job, prepared)
    archive = local(job.work, prepared["actual_archive"]["path"])
    before = archive.stat()
    require(before.st_size == manifest["bytes"], "Actual verified archive size changed before staging")
    rows = descriptor["chunks"]
    require(rows and descriptor.get("chunk_size") == PART_SIZE and descriptor.get("future_prefix") == "",
            "Declared exact root-native 8 MiB ranges required")
    staged, part_records = {}, []

    def store_blob(name, raw, expected=None):
        name = canonical(name)
        full = PREFIX + "/" + name
        require(full not in job.qtree and full not in staged and name != ARCHIVE,
                "V may add only new named delivery files, never overwrite P/Q or commit a full ZIP")
        actual = identity_bytes(raw)
        if expected:
            matches(actual, expected)
        written = job.git("hash-object", "-w", "--stdin", input_bytes=raw).decode().strip()
        require(written == actual["git_blob"], "Actual stored Git object differs from the exact bytes")
        staged[full] = actual
        return actual

    whole = hashlib.sha256()
    whole_blob = hashlib.sha1(b"blob " + str(before.st_size).encode() + b"\0")
    offset = 0
    with archive.open("rb") as stream:
        for index, row in enumerate(rows):
            name = ARCHIVE + ".part" + str(index).zfill(4)
            require(row["path"] == name and row["offset"] == offset
                    and 0 < row["bytes"] <= PART_SIZE
                    and (index == len(rows)-1 or row["bytes"] == PART_SIZE), "Exact contiguous part ranges required")
            block = stream.read(row["bytes"])
            actual = store_blob(name, block, row)
            offset += len(block)
            whole.update(block)
            whole_blob.update(block)
            part_records.append(dict(path=name, offset=row["offset"], **actual, actual_git_object_written=True))
        require(not stream.read(1), "Archive has undeclared trailing bytes")
    require(signature(archive.stat()) == signature(before), "Archive changed during Git object staging")
    matches(dict(bytes=offset, sha256=whole.hexdigest(), git_blob=whole_blob.hexdigest()), manifest)
    store_blob(PACKAGE, manifest_path.read_bytes(), prepared["package_manifest"])
    store_blob(DESCRIPTOR, descriptor_path.read_bytes(), prepared["virtual_descriptor"])
    receipt_prefix = "delivery121/receipts/"
    small = {
        "PREPARED121.json": prepared_path,
        "SOURCE_CI_API121.json": job.work / "source-ci-api.json",
        "UPLOADED_ARTIFACT_API121.json": job.work / "uploaded-artifact-api.json",
    }
    for folder in ("pack", "verify", "describe"):
        for name in ("START121.json", "PUBLICATION_ATTEMPT121.json"):
            small[folder + "/" + name] = job.work / folder / name
    # These are the completed preparation command records and stdout/stderr,
    # not a self-mutating snapshot of the later commit/push commands.
    for path in sorted(job.logs.glob("prepare-*")):
        if path.is_file():
            small["logs/" + path.name] = path
    for name, path in sorted(small.items()):
        require(path.stat().st_size <= 32 << 20, "A delivery receipt/log unexpectedly exceeds the small-record bound")
        store_blob(receipt_prefix + name, path.read_bytes())
    part_receipt = dict(kind="nbo-r121-remote-part-object-write-v1", request_commit=job.q,
        author_source_commit=job.s, publication_commit=job.p, parts=part_records,
        whole_archive={key: manifest[key] for key in ("bytes", "sha256", "git_blob")},
        actual_stored_objects=len(part_records), physical_part_files_written=0,
        original_archive_unchanged=True, complete_archive_reverified_while_staging=True)
    save(job.work / "PART_OBJECTS121.json", part_receipt)
    store_blob(receipt_prefix + "PART_OBJECTS121.json", json_bytes(part_receipt))
    # Take a finite snapshot of completed finalization logs. The subsequent
    # act of storing these log blobs creates new logs, so those later logs,
    # index/commit/push commands, and the actual V identity are retained by
    # the workflow's final diagnostics artifact instead of being recursively
    # self-embedded in V.
    finalization_logs = [path for path in sorted(job.logs.glob("finalize-*")) if path.is_file()]
    finalization_snapshot = dict(kind="nbo-r121-completed-finalization-log-snapshot-v1",
        request_commit=job.q, completed_commands=json.loads(json_bytes(job.commands)),
        logs=[dict(path=path.relative_to(job.work).as_posix(), **identity_file(path))
              for path in finalization_logs],
        snapshot_created_utc=utc(),
        scope="Completed context, exact part-object writes and small receipt-object writes before this finite log snapshot.",
        subsequent_log_storage_index_commit_push_and_readback_logs="Preserved in the final Actions diagnostics artifact.",
        scientific_execution=False)
    save(job.work / "FINALIZATION_LOG_SNAPSHOT121.json", finalization_snapshot)
    for path in finalization_logs:
        require(path.stat().st_size <= 32 << 20, "A finalization log exceeds the small-record bound")
        store_blob(receipt_prefix + "logs/" + path.name, path.read_bytes())
    store_blob(receipt_prefix + "FINALIZATION_LOG_SNAPSHOT121.json", json_bytes(finalization_snapshot))
    delivery = dict(kind="nbo-r121-remote-delivery-precommit-v1",
        status="actual_artifact_uploaded_and_exact_part_objects_stored_before_index_and_commit",
        context=job.context_record, artifact=artifact, helper=job.helper_identity,
        package_manifest=prepared["package_manifest"], virtual_descriptor=prepared["virtual_descriptor"],
        archive={key: manifest[key] for key in ("bytes", "sha256", "git_blob")},
        actual_part_objects=len(part_records), existing_P_Q_files_modified=False,
        all_current_native_source_and_evidence_retained=True, scientific_execution=False,
        commit_and_remote_push_completed_at_receipt_creation=False,
        finalization_log_snapshot=dict(path=receipt_prefix + "FINALIZATION_LOG_SNAPSHOT121.json",
            **identity_file(job.work / "FINALIZATION_LOG_SNAPSHOT121.json")),
        identity_scope="V is the later actual Git commit containing this receipt; it cannot contain its own SHA.",
        authoritative_postpush_record="The workflow's final diagnostics artifact and independent remote Git/part readback record actual V.",
        started_utc=job.started, receipt_created_utc=utc(), commands_completed_before_commit=job.commands)
    save(job.work / "DELIVERY_PRECOMMIT121.json", delivery)
    store_blob(receipt_prefix + "DELIVERY_PRECOMMIT121.json", json_bytes(delivery))
    entries = b"".join(b"100644 " + info["git_blob"].encode() + b"\t" + name.encode() + b"\0"
                       for name, info in sorted(staged.items()))
    job.git("update-index", "-z", "--index-info", input_bytes=entries)
    expected = []
    for name in sorted(staged):
        expected += [b"A", name.encode()]
    actual = [item for item in job.git("diff", "--cached", "--name-status", "--no-renames", "-z").split(b"\0") if item]
    require(actual == expected, "Index contains something other than the exact new delivery set")
    require(job.git("rev-parse", "HEAD").decode().strip() == job.q, "Q moved during preparation")
    job.compare_remote_q()
    job.git("-c", "user.name=github-actions[bot]", "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
            "commit", "-m", "Publish verified R121 referee package and exact remote parts; no scientific execution [skip ci]")
    job.new_commit = job.git("rev-parse", "HEAD").decode().strip()
    require(job.git("rev-parse", "HEAD^").decode().strip() == job.q, "V must have the actual Q parent")
    committed = [item for item in job.git("diff", "--name-status", "--no-renames", "-z", job.q, job.new_commit).split(b"\0") if item]
    require(committed == expected, "Actual V differs from the exact additive delivery set")
    job.compare_remote_q()
    job.git("push", "origin", "HEAD:refs/heads/" + BRANCH)
    remote = job.git("ls-remote", "--exit-code", "origin", "refs/heads/" + BRANCH).decode().split()
    require(remote == [job.new_commit, "refs/heads/" + BRANCH], "Remote head readback differs from actual pushed V")
    pushed = dict(kind="nbo-r121-remote-package-push-v1", status="actual_V_pushed_and_remote_head_verified",
        author_source_commit=job.s, publication_commit=job.p, request_commit=job.q, delivery_commit=job.new_commit,
        actual_workflow_run_id=job.run_id, actual_workflow_run_attempt=job.run_attempt,
        artifact=artifact, added_files=len(staged), added_part_files=len(part_records),
        existing_P_Q_files_modified=False, scientific_execution=False, force_push_used=False,
        actual_remote_head=remote[0], commands=job.commands, started_utc=job.started,
        ended_utc=utc(), elapsed_seconds=time.perf_counter()-job.clock,
        record_created_after_push_and_not_self_embedded_in_V=True)
    save(job.work / "PUSH_RESULT121.json", pushed)
    print(json.dumps({key: pushed[key] for key in ("status", "author_source_commit", "publication_commit", "request_commit", "delivery_commit", "added_part_files")}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="phase", required=True)
    for name in ("prepare", "finalize"):
        command = sub.add_parser(name)
        command.add_argument("--repository", type=Path, required=True)
        command.add_argument("--request-commit", required=True)
        command.add_argument("--work-dir", type=Path, required=True)
        if name == "finalize":
            command.add_argument("--artifact-id", required=True)
            command.add_argument("--artifact-digest", required=True)
            command.add_argument("--artifact-url", required=True)
    args = parser.parse_args()
    job = Job(args)
    try:
        prepare(job) if args.phase == "prepare" else finalize(job)
    except BaseException:
        job.failure()
        raise


if __name__ == "__main__":
    main()
