"""Bind and package an already completed NBO R120 author revision.

Standard library only.  No science, build, test, network, Git mutation or CI
query is performed.  All output directories must be new staging directories
outside the native revision.  Failed attempts and partial containers remain.

bind: verify every native file at immutable author commit S, the supplied
strict build receipt, its command logs, all declared and final recorder inputs,
and the four existing PDFs.  Root copies the emitted manifests into a later P.

pack: verify that publication commit P descends from S without changing any
native S entry, then include EVERY native P file.  The final ZIP and its output
manifest must not already be in P.  No extension or evidence-directory filter
is used.  Existing evidence archive parts remain archive parts in this ZIP;
their committed materialization instructions/manifests remain included.

verify: stream-read a ZIP, or its ordered parts without reassembly, against the
published output manifest.  This verifies bytes and routing, not scientific
correctness, actual CI success, or remote availability of the named commits.

describe-parts: describe 8 MiB byte ranges of an actual verified ZIP without
writing duplicate chunk files.  These are virtual transport descriptors, not
receipts of successful upload or existing remote Git objects.
"""
from __future__ import annotations

import argparse
import bisect
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import time
import traceback
import zipfile


DOCS = ("ECTA", "supp", "appendix", "RESPONSE_TO_REFEREE")
SPM = "SOURCE_PDF_MANIFEST120.json"
INVENTORY = "AUTHOR_SOURCE_INVENTORY120.json"
PACKAGE = "REFEREE_READY_PACKAGE120.json"
ARCHIVE = "referee-ready120.zip"
VIRTUAL_PARTS = "VIRTUAL_ZIP_CHUNKS120.json"
RECEIPT = "PUBLICATION_ATTEMPT120.json"
CHUNK = 1024 * 1024
PART_SIZE = 8 * CHUNK
ZIP_DATE = (2026, 10, 19, 0, 0, 0)
SHA1 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relative(value):
    require(isinstance(value, str) and value, "A relative POSIX path is required")
    p = PurePosixPath(value)
    require(not p.is_absolute() and ".." not in p.parts and "\\" not in value
            and str(p) == value and value != "." and "\x00" not in value,
            "Unsafe/noncanonical path: " + repr(value))
    return value


def final_output(name):
    return name in {ARCHIVE, PACKAGE} or name.startswith(ARCHIVE + ".part")


def json_data(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def write_new(path, value):
    with Path(path).open("xb") as f:
        f.write(json_data(value))
        f.flush()
        os.fsync(f.fileno())


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json_bytes(raw):
    def nonfinite(value):
        raise ValueError("Nonfinite JSON value: " + value)
    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=nonfinite)


def load_json(path, expected=None):
    raw = Path(path).read_bytes()
    if expected is not None:
        match({"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()},
              {k: expected[k] for k in ("bytes", "sha256") if k in expected}, str(path))
    return read_json_bytes(raw)


def signature(s):
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def local(root, name):
    name = relative(name)
    p = root.joinpath(*PurePosixPath(name).parts)
    require(p.resolve().is_relative_to(root), "Path leaves revision: " + name)
    for ancestor in (p, *p.parents):
        if ancestor == root:
            break
        require(not ancestor.is_symlink(), "Symlink in native path: " + name)
    return p


def stream_record(source, size, target=None):
    h = hashlib.sha256()
    g = hashlib.sha1(b"blob " + str(size).encode() + b"\0")
    count = 0
    for block in iter(lambda: source.read(CHUNK), b""):
        count += len(block)
        require(count <= size, "Stream exceeded the declared file size")
        h.update(block)
        g.update(block)
        if target is not None:
            target.write(block)
    require(count == size, "Stream is shorter than its declared file size")
    return {"bytes": count, "sha256": h.hexdigest(), "git_blob": g.hexdigest()}


def file_record(path, target=None):
    path = Path(path)
    require(not path.is_symlink(), "Refusing a symlink file: " + str(path))
    before = path.stat()
    require(stat.S_ISREG(before.st_mode), "Not a regular file: " + str(path))
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    with os.fdopen(os.open(path, flags), "rb") as f:
        require(signature(os.fstat(f.fileno())) == signature(before),
                "File changed before reading: " + str(path))
        result = stream_record(f, before.st_size, target)
        require(signature(os.fstat(f.fileno())) == signature(before),
                "File changed during reading: " + str(path))
    require(signature(path.stat()) == signature(before) and not path.is_symlink(),
            "File was replaced during reading: " + str(path))
    return result


def match(info, expected, label):
    for key in ("bytes", "sha256", "git_blob"):
        if key in expected:
            require(info[key] == expected[key], "Mismatch in " + key + ": " + label)


class Attempt:
    def __init__(self, args):
        self.args = args
        self.output = args.output_dir.resolve()
        self.root = args.revision.resolve() if getattr(args, "revision", None) else None
        if self.root is not None:
            require(self.root.is_dir(), "Missing native revision")
            require(not self.output.is_relative_to(self.root),
                    "Use a fresh staging output outside the native revision")
        self.output.mkdir(parents=True, exist_ok=False)
        self.record = {
            "schema": "NBO_R120_PUBLICATION_ATTEMPT_V1", "mode": args.mode,
            "started_unix": time.time(), "status": "started",
            "argv": sys.argv, "git_commands": [], "outputs": [],
            "helper": {"path": str(Path(__file__).resolve()), **file_record(__file__)},
            "scientific_execution": False, "build_execution": False,
            "native_code_imported": False, "network_access": False,
            "git_mutation": False, "CI_queried_or_status_inferred": False,
        }
        write_new(self.output / "START120.json", self.record)

    def add_output(self, name, role):
        row = {"path": relative(name), "role": role,
               **file_record(self.output / name)}
        self.record["outputs"].append(row)
        return row

    def finish(self, error=None):
        if error is not None:
            self.record.update(status="failed", exception_type=type(error).__name__,
                               exception=str(error), traceback=traceback.format_exc())
            write_new(self.output / "FAILURE120.json", {
                "exception_type": type(error).__name__, "exception": str(error),
                "traceback": self.record["traceback"],
                "partial_files": [{"path": p.name, "bytes": p.stat().st_size}
                                  for p in sorted(self.output.iterdir()) if p.is_file()],
                "scope": "Original failed attempt retained; no partial output is declared verified.",
            })
        self.record["ended_unix"] = time.time()
        self.record["elapsed_seconds"] = self.record["ended_unix"] - self.record["started_unix"]
        write_new(self.output / RECEIPT, self.record)

    def git(self, arguments, cwd=None, allow_one=False):
        argv = ["git", *arguments]
        start = time.time()
        env = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_OPTIONAL_LOCKS="0",
                   GIT_TERMINAL_PROMPT="0")
        row = {
            "argv": argv, "cwd": str(cwd or self.repo),
            "started_unix": start, "exit_code": None, "status": "started",
        }
        self.record["git_commands"].append(row)
        try:
            p = subprocess.run(argv, cwd=cwd or self.repo, env=env,
                               capture_output=True, timeout=120)
            row.update(exit_code=p.returncode, status="completed",
                       stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),
                       stderr=p.stderr.decode("utf-8", errors="replace"))
        except BaseException as error:
            row.update(status="launch_or_execution_exception",
                       exception_type=type(error).__name__, exception=str(error))
            raise
        finally:
            row["ended_unix"] = time.time()
        require(p.returncode == 0 or (allow_one and p.returncode == 1),
                "Read-only Git metadata command failed: " + " ".join(arguments))
        return p

    def repository(self):
        p = self.git(["rev-parse", "--show-toplevel"], cwd=self.root)
        self.repo = Path(p.stdout.decode().strip()).resolve()
        require(self.root.is_relative_to(self.repo) and self.root != self.repo,
                "The native revision must be a directory inside a Git repository")
        self.prefix = self.root.relative_to(self.repo).as_posix()
        fmt = self.git(["rev-parse", "--show-object-format"]).stdout.decode().strip()
        require(fmt == "sha1", "This publication interface requires the repository's SHA-1 Git identities")

    def tree(self, commit):
        require(SHA1.fullmatch(commit), "Supply a full lowercase immutable commit SHA")
        resolved = self.git(["rev-parse", "--verify", commit + "^{commit}"]).stdout.decode().strip()
        require(resolved == commit, "Supplied identity is not its resolved commit")
        root_tree = self.git(["rev-parse", commit + "^{tree}"]).stdout.decode().strip()
        native_tree = self.git(["rev-parse", commit + ":" + self.prefix]).stdout.decode().strip()
        # Always run at the repository root and limit recursion to this revision.
        listing = self.git(["ls-tree", "-r", "-z", commit, "--", self.prefix + "/"]).stdout
        result = {}
        for entry in listing.split(b"\0"):
            if not entry:
                continue
            header, encoded = entry.split(b"\t", 1)
            mode, kind, blob = header.decode("ascii").split()
            name = encoded.decode("utf-8")
            require(name.startswith(self.prefix + "/"), "Git path outside native revision")
            name = relative(name[len(self.prefix) + 1:])
            require(kind == "blob" and mode in {"100644", "100755"}
                    and SHA1.fullmatch(blob), "Unsupported Git entry: " + name)
            require(name not in result and not final_output(name),
                    "Duplicate path or already committed final package output: " + name)
            result[name] = {"path": name, "git_mode": mode, "git_blob": blob}
        require(result, "Empty native commit tree")
        return result, {"commit": commit, "repository_tree_sha": root_tree,
                        "native_revision_tree_sha": native_tree,
                        "repository_revision_path": self.prefix}

    def verify_tree(self, tree, role):
        result = {}
        for index, (name, row) in enumerate(sorted(tree.items()), 1):
            info = file_record(local(self.root, name))
            match(info, row, name)
            result[name] = {**row, **info, "kind": role}
            if index % 128 == 0:
                print(json.dumps({"stage": role, "verified_files": index}), flush=True)
        return result


def indexed(rows, label):
    require(isinstance(rows, list), "Expected a record list: " + label)
    result = {}
    for row in rows:
        require(isinstance(row, dict), "Invalid record: " + label)
        name = relative(row["path"])
        require(name not in result, "Duplicate path in " + label + ": " + name)
        require(isinstance(row["bytes"], int) and not isinstance(row["bytes"], bool)
                and row["bytes"] >= 0 and SHA256.fullmatch(row["sha256"]),
                "Invalid file identity in " + label + ": " + name)
        if "git_blob" in row:
            require(SHA1.fullmatch(row["git_blob"]), "Invalid Git blob in " + label)
        if "git_mode" in row:
            require(row["git_mode"] in {"100644", "100755"}, "Invalid regular-file Git mode in " + label)
        result[name] = row
    return result


def bind(attempt):
    args, root = attempt.args, attempt.root
    attempt.repository()
    tree, identity = attempt.tree(args.source_commit)
    require(not {SPM, INVENTORY} & set(tree),
            "Author S must precede its source/PDF manifests; use a fresh source identity")
    if args.expected_source_tree:
        require(identity["repository_tree_sha"] == args.expected_source_tree,
                "Author repository tree differs from the supplied tree")
    source = attempt.verify_tree(tree, "author_source")
    build_path = args.build_receipt.resolve()
    require(build_path.is_relative_to(root), "Build receipt must have a portable native relative path")
    build_name = relative(build_path.relative_to(root).as_posix())
    build_info = file_record(local(root, build_name))
    if build_name in source:
        match(build_info, source[build_name], build_name)
    build = load_json(build_path, build_info)
    require(build.get("status") == "compiled_clean" and build.get("diagnostic") is False
            and build.get("issues") == {} and build.get("placeholders") == [],
            "The supplied actual strict build receipt is not clean")
    require(build.get("scientific_execution") is False, "Unexpected build receipt scope")
    require(source.get("build120.py", {}).get("sha256") == build["builder_sha256"],
            "Actual builder source differs from S")
    required = {build_name: {"path": build_name, **build_info}}

    def keep(name, expected=None):
        name = relative(name)
        info = file_record(local(root, name))
        if expected is not None:
            match(info, expected, name)
        if name in source:
            match(info, source[name], name)
        if name in required:
            match(info, required[name], name)
        required[name] = {"path": name, **info}
        return required[name]

    commands = build.get("commands")
    require(isinstance(commands, list) and commands, "Missing actual build commands")
    latex_counts = {d: 0 for d in DOCS}
    logs = set()
    for row in commands:
        require(row.get("status") == "passed" and row.get("exit_code") == 0,
                "An actual build command did not pass")
        require(row.get("ended_unix", -1) >= row.get("started_unix", 0),
                "Incomplete build command timing receipt")
        argv = row.get("argv", [])
        require(isinstance(argv, list) and argv, "Missing build command argv")
        name = Path(argv[0]).name
        if name == "pdflatex":
            require(all(flag in argv for flag in ("-halt-on-error", "-recorder",
                                                 "-output-directory=build")),
                    "Build command lacks a strict recorder invocation")
            document = argv[-1].removesuffix(".tex")
            require(document in DOCS and argv[-1] == document + ".tex",
                    "Unexpected TeX build target")
            latex_counts[document] += 1
        else:
            require(name == "bibtex" and len(argv) == 2
                    and argv[1] in {"build/" + d for d in DOCS},
                    "Unexpected command in the actual build receipt")
        log = relative(row["log"])
        require(log not in logs, "Duplicate build command log")
        logs.add(log)
        keep(log, {"sha256": row["log_sha256"]})
    require(len(set(latex_counts.values())) == 1 and 2 <= next(iter(latex_counts.values())) <= 8,
            "The four documents lack the same complete 2--8-pass build")

    declared = {}
    for group in ("source_sha256", "graphic_asset_sha256"):
        require(isinstance(build.get(group), dict), "Missing declared source group: " + group)
        for name, sha in build[group].items():
            require(name in source, "Declared build input absent from S: " + name)
            match(source[name], {"sha256": sha}, name)
            declared[name] = source[name]
    require(declared, "Empty declared build input inventory")
    for group in ("actual_project_inputs", "generated_build_inputs"):
        require(set(build.get(group, {})) == set(DOCS), "Incomplete recorded closure: " + group)

    project_inputs, generated_inputs, recorder_files = {}, {}, {}
    external = {}
    for document in DOCS:
        fls_name = "build/" + document + ".fls"
        recorder_files[document] = keep(fls_name)
        parsed_project, parsed_generated = {}, {}
        for line in local(root, fls_name).read_text(encoding="utf-8", errors="strict").splitlines():
            if line.startswith("PWD "):
                require(Path(line[4:]).resolve() == root, "Recorder PWD differs from current native build root")
            if not line.startswith("INPUT "):
                continue
            literal = line[6:]
            require(literal and "\x00" not in literal, "Empty/invalid recorder input")
            p = Path(literal)
            p = (root / p).resolve() if not p.is_absolute() else p.resolve()
            require(p.is_file(), "Final recorder input is unavailable: " + literal)
            if p.is_relative_to(root):
                name = relative(p.relative_to(root).as_posix())
                info = keep(name)
                target = parsed_generated if name.startswith("build/") else parsed_project
                target[name] = info
            else:
                # The builder did not hash system inputs during its execution.
                # Record current bytes without pretending that it did.
                name = str(p)
                if name not in external:
                    external[name] = {"absolute_path_at_observation": name,
                                      "literal_recorder_paths": [], "documents": [],
                                      **file_record(p)}
                if literal not in external[name]["literal_recorder_paths"]:
                    external[name]["literal_recorder_paths"].append(literal)
                if document not in external[name]["documents"]:
                    external[name]["documents"].append(document)
        require(parsed_project and document + ".tex" in parsed_project,
                "Final recorder lacks its native TeX master")
        for parsed, group in ((parsed_project, "actual_project_inputs"),
                              (parsed_generated, "generated_build_inputs")):
            expected = build[group][document]
            require(set(parsed) == set(expected), "Final recorder closure differs from actual receipt: " + document + "/" + group)
            for name, info in parsed.items():
                match(info, {"sha256": expected[name]}, name)
                if group == "actual_project_inputs":
                    require(name in source, "Actual native TeX input absent from S: " + name)
                    match(info, source[name], name)
        project_inputs[document] = list(parsed_project.values())
        generated_inputs[document] = list(parsed_generated.values())
    pdf_rows = indexed(build.get("pdfs"), "build PDFs")
    require(set(pdf_rows) == {"build/" + d + ".pdf" for d in DOCS},
            "Actual receipt must identify exactly the four native PDFs")
    pdfs = [keep(name, row) for name, row in sorted(pdf_rows.items())]
    for name in required:
        require(not final_output(name) and name not in {SPM, INVENTORY},
                "A build input creates a publication self-cycle: " + name)

    inventory = {"schema": "NBO_R120_AUTHOR_SOURCE_INVENTORY_V1",
                 "author_source_commit": args.source_commit, **identity,
                 "native_files": len(source),
                 "native_bytes": sum(r["bytes"] for r in source.values()),
                 "files": list(source.values()),
                 "scope": "Every native S Git blob and mode, including all evidence archive parts. No directory or extension omission."}
    write_new(attempt.output / INVENTORY, inventory)
    inventory_info = attempt.add_output(INVENTORY, "complete author S inventory")
    manifest = {
        "schema": "NBO_R120_SOURCE_PDF_BINDING_V1", "author_source_commit": args.source_commit,
        **identity, "source_inventory": {"path": INVENTORY, **file_record(attempt.output / INVENTORY)},
        "native_files": len(source), "native_bytes": inventory["native_bytes"],
        "build_receipt": {"path": build_name, **build_info},
        "build_status": build["status"], "build_command_count": len(commands),
        "latex_passes_per_document": latex_counts, "builder_sha256": build["builder_sha256"],
        "source_date_epoch": build["source_date_epoch"], "tool_versions": build["tool_versions"],
        "declared_build_inputs": [declared[n] for n in sorted(declared)],
        "actual_project_inputs": project_inputs, "generated_build_inputs": generated_inputs,
        "final_recorders": recorder_files, "pdfs": pdfs,
        "required_publication_inputs": [required[n] for n in sorted(required)],
        "external_system_input_observations": [external[n] for n in sorted(external)],
        "external_input_scope": "Every final recorder INPUT was read. Project/generated hashes agree with the actual build receipt; external TeX/font hashes are current observations because build120.py captured only tool versions for system files. External system bytes are not claimed to be in S or the referee ZIP.",
        "required_publication_scope": "P must also retain the recorded build receipt, all command logs, the four final recorder files, all generated build inputs, and PDFs listed here. Source inventory and this manifest are copied from this exclusive staging attempt.",
        "preparation_helper_sha256": attempt.record["helper"]["sha256"],
        "CI_scope": "No CI state is queried, read for success, or inferred. Actual CI receipts are independently supplied publication material.",
        "scope": "An existing strict clean build bound to exact S bytes and actual PDFs; no build or experiment was rerun.",
    }
    write_new(attempt.output / SPM, manifest)
    attempt.add_output(SPM, "source/PDF binding")
    attempt.record.update(status="source_pdf_binding_verified", author_source_commit=args.source_commit,
                          source_identity=identity, source_files=len(source),
                          source_bytes=inventory["native_bytes"], verified_pdf_count=4,
                          required_publication_inputs=len(required),
                          external_system_inputs_observed=len(external),
                          source_inventory_sha256=inventory_info["sha256"])


def validate_binding(root, source, source_identity, publication):
    require(SPM in publication and INVENTORY in publication, "P lacks source/PDF binding or complete S inventory")
    manifest = load_json(local(root, SPM), publication[SPM])
    inventory = load_json(local(root, INVENTORY), publication[INVENTORY])
    require(manifest.get("schema") == "NBO_R120_SOURCE_PDF_BINDING_V1"
            and inventory.get("schema") == "NBO_R120_AUTHOR_SOURCE_INVENTORY_V1", "Unexpected binding schema")
    for obj in (manifest, inventory):
        require(obj["author_source_commit"] == source_identity["commit"], "Source identity mismatch")
        for key in ("repository_tree_sha", "native_revision_tree_sha", "repository_revision_path"):
            require(obj[key] == source_identity[key], "Source tree/path binding mismatch: " + key)
    expected_source = indexed(inventory["files"], "author S inventory")
    require(set(expected_source) == set(source), "Source inventory is incomplete or contains extra paths")
    for name, row in source.items():
        require(expected_source[name]["git_mode"] == row["git_mode"], "Source mode mismatch")
        match(publication[name], expected_source[name], name)
        match(publication[name], row, name)
    require(inventory["native_files"] == manifest["native_files"] == len(source), "Source count mismatch")
    total = sum(publication[name]["bytes"] for name in source)
    require(inventory["native_bytes"] == manifest["native_bytes"] == total, "Source byte total mismatch")
    require(manifest["source_inventory"]["path"] == INVENTORY, "Inventory path mismatch")
    match(publication[INVENTORY], manifest["source_inventory"], INVENTORY)
    required = indexed(manifest["required_publication_inputs"], "required publication inputs")
    for name, row in required.items():
        require(name in publication, "P omitted a bound build input/receipt: " + name)
        match(publication[name], row, name)
    receipt_name = relative(manifest["build_receipt"]["path"])
    require(receipt_name in required, "Binding omitted its actual build receipt")
    match(publication[receipt_name], manifest["build_receipt"], receipt_name)
    build = load_json(local(root, receipt_name), publication[receipt_name])
    require(manifest["build_status"] == build.get("status") == "compiled_clean"
            and build.get("diagnostic") is False and build.get("issues") == {}
            and build.get("placeholders") == [], "Embedded strict build is not clean")
    require(build["builder_sha256"] == manifest["builder_sha256"]
            == publication["build120.py"]["sha256"], "Embedded builder identity differs")
    commands = build["commands"]
    require(len(commands) == manifest["build_command_count"] and commands,
            "Embedded actual build command count differs")
    for command in commands:
        require(command.get("status") == "passed" and command.get("exit_code") == 0,
                "Embedded actual build command did not pass")
        name = relative(command["log"])
        require(name in required, "Binding omitted a build command log")
        match(publication[name], {"sha256": command["log_sha256"]}, name)
    declared = indexed(manifest["declared_build_inputs"], "bound declared build inputs")
    declared_hashes = {}
    for group in ("source_sha256", "graphic_asset_sha256"):
        for name, sha in build[group].items():
            require(name not in declared_hashes or declared_hashes[name] == sha,
                    "Conflicting declared build input hashes")
            declared_hashes[name] = sha
    require(set(declared) == set(declared_hashes), "Declared build source inventory differs")
    for name, row in declared.items():
        require(name in source, "Declared build source is absent from S")
        match(publication[name], row, name)
        match(row, {"sha256": declared_hashes[name]}, name)
    require(set(manifest["final_recorders"]) == set(DOCS), "Missing final recorder identity")
    for document in DOCS:
        recorder = manifest["final_recorders"][document]
        require(recorder["path"] == "build/" + document + ".fls"
                and recorder["path"] in required, "Binding omitted a final recorder")
        match(publication[recorder["path"]], recorder, recorder["path"])
        for group in ("actual_project_inputs", "generated_build_inputs"):
            require(set(manifest[group]) == set(build[group]) == set(DOCS),
                    "Incomplete embedded document input closure")
            inputs = indexed(manifest[group][document], "bound " + group)
            require(set(inputs) == set(build[group][document]), "Embedded recorder input set differs")
            for name, row in inputs.items():
                require(name in required and (group != "actual_project_inputs" or name in source),
                        "Binding omitted a required actual input: " + name)
                match(publication[name], row, name)
                match(row, {"sha256": build[group][document][name]}, name)
    pdfs = indexed(manifest["pdfs"], "source-bound PDFs")
    require(set(pdfs) == {"build/" + d + ".pdf" for d in DOCS}, "Incomplete source-bound PDF set")
    for name, row in pdfs.items():
        require(name in publication and name in required, "P omitted a required PDF")
        match(publication[name], row, name)
    build_pdfs = indexed(build["pdfs"], "embedded actual build PDFs")
    require(set(build_pdfs) == set(pdfs), "Embedded actual build PDF set differs")
    for name, row in build_pdfs.items():
        match(pdfs[name], row, name)
    return manifest


def zip_members(archive, expected):
    expected = indexed(expected, "ZIP member inventory")
    seen, total = set(), 0
    with zipfile.ZipFile(archive, "r", allowZip64=True) as z:
        require(not z.comment, "Unexpected ZIP comment")
        for item in z.infolist():
            name = relative(item.filename)
            require(name in expected and name not in seen and not item.is_dir(),
                    "Unexpected, duplicate, or non-file ZIP member: " + name)
            row = expected[name]
            require(item.file_size == row["bytes"] and item.compress_type == zipfile.ZIP_STORED,
                    "ZIP size/compression mismatch: " + name)
            require(not (item.flag_bits & 1) and item.date_time == ZIP_DATE,
                    "Encrypted or noncanonical ZIP member: " + name)
            require(item.create_system == 3 and item.external_attr >> 16 == int(row["git_mode"], 8),
                    "ZIP mode mismatch: " + name)
            with z.open(item, "r") as f:
                info = stream_record(f, item.file_size)
            match(info, row, name)
            seen.add(name)
            total += item.file_size
    require(seen == set(expected), "ZIP omitted an expected native publication file")
    return {"verified_members": len(seen), "verified_uncompressed_bytes": total,
            "verification": "Every member read to EOF, with ZIP CRC, SHA256, Git blob, size, name and mode checks."}


def split(archive, expected):
    rows, combined = [], hashlib.sha256()
    with archive.open("rb") as f:
        for index, block in enumerate(iter(lambda: f.read(PART_SIZE), b"")):
            name = ARCHIVE + ".part" + str(index).zfill(4)
            p = archive.parent / name
            with p.open("xb") as out:
                out.write(block)
                out.flush()
                os.fsync(out.fileno())
            info = file_record(p)
            require(info["sha256"] == hashlib.sha256(block).hexdigest(), "Split part readback failed")
            rows.append({"path": name, **info})
            combined.update(block)
    require(combined.hexdigest() == expected["sha256"]
            and sum(r["bytes"] for r in rows) == expected["bytes"], "Ordered parts do not reconstruct ZIP")
    return rows


def pack(attempt):
    args, root = attempt.args, attempt.root
    attempt.repository()
    source, sid = attempt.tree(args.source_commit)
    publication, pid = attempt.tree(args.publication_commit)
    ancestor = attempt.git(["merge-base", "--is-ancestor", args.source_commit,
                            args.publication_commit], allow_one=True)
    require(ancestor.returncode == 0, "P is not S or a descendant of S")
    require(set(source) <= set(publication), "P deleted a native author S path")
    for name, row in source.items():
        require(publication[name] == row, "P changed a native author S blob/mode: " + name)
    rows = attempt.verify_tree(publication, "publication_commit_native")
    binding = validate_binding(root, source, sid, rows)
    for name in args.required_path:
        require(relative(name) in rows, "Required root-selected publication receipt absent from P: " + name)
    ordered = [rows[name] for name in sorted(rows)]
    archive = attempt.output / ARCHIVE
    # ZIP_STORED for every member avoids recompressing evidence parts and removes
    # zlib-version variability.  No timestamp is taken from the filesystem.
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_STORED, allowZip64=True) as z:
        for row in ordered:
            info = zipfile.ZipInfo(row["path"], date_time=ZIP_DATE)
            info.create_system = 3
            info.external_attr = int(row["git_mode"], 8) << 16
            info.compress_type = zipfile.ZIP_STORED
            with z.open(info, "w", force_zip64=True) as target:
                written = file_record(local(root, row["path"]), target)
            match(written, row, row["path"])
    archive_info = file_record(archive)
    verified = zip_members(archive, ordered)
    attempt.add_output(ARCHIVE, "deterministic complete P snapshot ZIP")
    parts = [] if args.no_split else split(archive, archive_info)
    for row in parts:
        attempt.record["outputs"].append({**row, "role": "ordered 8 MiB ZIP part"})
    manifest = {
        "schema": "NBO_R120_REFEREE_READY_PACKAGE_V1", "archive": ARCHIVE,
        **archive_info, "author_source_commit": args.source_commit,
        "publication_commit": args.publication_commit,
        "author_source_identity": sid, "publication_identity": pid,
        "source_tree_verified_members": len(source),
        "publication_native_members": len(rows),
        "publication_added_members": len(rows) - len(source),
        "members": ordered, "parts": parts, "part_size": PART_SIZE,
        "split_performed": not args.no_split,
        "source_pdf_manifest": {"path": SPM, **file_record(local(root, SPM))},
        "source_inventory": {"path": INVENTORY, **file_record(local(root, INVENTORY))},
        "pdfs": binding["pdfs"], "root_selected_required_paths": sorted(set(args.required_path)),
        "zip_policy": {"member_order": "lexicographic POSIX path", "timestamp": list(ZIP_DATE),
                       "compression": "ZIP_STORED", "modes": "exact regular-file P Git modes",
                       "zip64": True, "comments": "empty"},
        "complete_member_readback": verified,
        "packager_sha256": attempt.record["helper"]["sha256"],
        "container_scope": "Every native P path without extension or directory omissions. P descends from S and preserves every native S blob and mode. All untracked files are outside this exact-commit snapshot.",
        "evidence_scope": "Already committed evidence archive parts and their manifests/materialization helpers are included byte-for-byte; expanded duplicate raw records are not invented or added.",
        "cycle_scope": "P excludes this final ZIP, its ordered parts and this output manifest. A later delivery commit may add those outputs. No output claims to contain its own hash manifest.",
        "CI_scope": "CI records are included if committed in P. No successful CI status is inferred by this byte-packaging helper.",
    }
    write_new(attempt.output / PACKAGE, manifest)
    attempt.add_output(PACKAGE, "complete ZIP and parts member manifest")
    attempt.record.update(status="complete_publication_snapshot_verified", author_source_commit=args.source_commit,
                          publication_commit=args.publication_commit, archive_sha256=archive_info["sha256"],
                          archive_bytes=archive_info["bytes"], parts=len(parts), **verified)


class PartsReader(io.RawIOBase):
    """Seek across verified parts without writing a duplicate assembled ZIP."""
    def __init__(self, directory, rows):
        super().__init__()
        self.paths = [local(directory, row["path"]) for row in rows]
        self.ends, total = [], 0
        for row in rows:
            total += row["bytes"]
            self.ends.append(total)
        self.size, self.position = total, 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        require(whence in (0, 1, 2), "Invalid seek origin")
        target = offset + (0 if whence == 0 else self.position if whence == 1 else self.size)
        require(target >= 0, "Negative seek")
        self.position = target
        return target

    def read(self, size=-1):
        require(not self.closed, "ZIP parts stream is closed")
        remaining = max(0, self.size - self.position)
        needed = remaining if size is None or size < 0 else min(size, remaining)
        result = bytearray()
        while needed:
            index = bisect.bisect_right(self.ends, self.position)
            start = 0 if index == 0 else self.ends[index - 1]
            count = min(needed, self.ends[index] - self.position)
            with self.paths[index].open("rb") as f:
                f.seek(self.position - start)
                block = f.read(count)
            require(len(block) == count, "ZIP part changed or became shorter")
            result.extend(block)
            needed -= count
            self.position += count
        return bytes(result)


def verify(attempt):
    args = attempt.args
    manifest_info = file_record(args.manifest)
    if args.expected_manifest_sha256:
        require(manifest_info["sha256"] == args.expected_manifest_sha256,
                "Published package manifest hash differs from supplied identity")
    manifest = load_json(args.manifest, manifest_info)
    require(manifest.get("schema") == "NBO_R120_REFEREE_READY_PACKAGE_V1"
            and manifest.get("archive") == ARCHIVE, "Unexpected package manifest")
    require(SHA1.fullmatch(manifest["author_source_commit"])
            and SHA1.fullmatch(manifest["publication_commit"]), "Invalid source/publication identity")
    for key in ("source_commit", "publication_commit"):
        wanted = getattr(args, key)
        actual = manifest["author_source_commit" if key == "source_commit" else key]
        if wanted is not None:
            require(actual == wanted, "Supplied immutable commit differs from package: " + key)
    rows = indexed(manifest["members"], "published ZIP inventory")
    require(rows and not any(final_output(name) for name in rows), "Empty or cyclic package inventory")
    require(SPM in rows and INVENTORY in rows, "Published ZIP inventory lacks source/PDF bindings")
    if args.archive:
        archive_info = file_record(args.archive)
        match(archive_info, manifest, "complete ZIP")
        container = args.archive
    else:
        directory = args.parts_dir.resolve()
        parts = manifest["parts"]
        require(parts and manifest.get("split_performed") is True,
                "The published manifest does not declare ZIP parts")
        require(len(indexed(parts, "ordered ZIP parts")) == len(parts), "Duplicate ZIP parts")
        combined, total = hashlib.sha256(), 0
        for index, row in enumerate(parts):
            require(row["path"] == ARCHIVE + ".part" + str(index).zfill(4),
                    "ZIP part order/name mismatch")
            require(0 < row["bytes"] <= PART_SIZE
                    and (index == len(parts) - 1 or row["bytes"] == PART_SIZE),
                    "ZIP part size mismatch")
            p = local(directory, row["path"])
            match(file_record(p), row, row["path"])
            with p.open("rb") as f:
                for block in iter(lambda: f.read(CHUNK), b""):
                    combined.update(block)
                    total += len(block)
        require(total == manifest["bytes"] and combined.hexdigest() == manifest["sha256"],
                "Concatenated ZIP parts differ from published container")
        container = PartsReader(directory, parts)
    try:
        result = zip_members(container, list(rows.values()))
        with zipfile.ZipFile(container, "r", allowZip64=True) as z:
            embedded = {}
            for name in (SPM, INVENTORY):
                raw = z.read(name)
                match({"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()},
                      {key: rows[name][key] for key in ("bytes", "sha256")}, name)
                embedded[name] = read_json_bytes(raw)
            bound, inventory = embedded[SPM], embedded[INVENTORY]
        require(bound["author_source_commit"] == inventory["author_source_commit"]
                == manifest["author_source_commit"], "Embedded author-source binding differs")
        require(bound.get("schema") == "NBO_R120_SOURCE_PDF_BINDING_V1"
                and inventory.get("schema") == "NBO_R120_AUTHOR_SOURCE_INVENTORY_V1",
                "Unexpected embedded source/PDF binding schema")
        sid, pid = manifest["author_source_identity"], manifest["publication_identity"]
        require(sid["commit"] == manifest["author_source_commit"]
                and pid["commit"] == manifest["publication_commit"],
                "Embedded commit/tree identity mismatch")
        for key in ("repository_tree_sha", "native_revision_tree_sha", "repository_revision_path"):
            require(bound[key] == inventory[key] == sid[key],
                    "Embedded author source tree/path differs: " + key)
        require(pid["repository_revision_path"] == sid["repository_revision_path"],
                "Author and publication native paths differ")
        match(rows[SPM], manifest["source_pdf_manifest"], SPM)
        match(rows[INVENTORY], manifest["source_inventory"], INVENTORY)
        match(rows[INVENTORY], bound["source_inventory"], INVENTORY)
        source_rows = indexed(inventory["files"], "embedded source inventory")
        require(len(source_rows) == manifest["source_tree_verified_members"]
                == inventory["native_files"] == bound["native_files"], "Embedded source count mismatch")
        for name, row in source_rows.items():
            require(name in rows and row["git_mode"] == rows[name]["git_mode"],
                    "Embedded S path/mode omitted from P ZIP: " + name)
            match(rows[name], row, name)
        source_bytes = sum(row["bytes"] for row in source_rows.values())
        require(source_bytes == inventory["native_bytes"] == bound["native_bytes"],
                "Embedded source byte total differs")
        require(len(rows) == manifest["publication_native_members"]
                and len(rows) - len(source_rows) == manifest["publication_added_members"],
                "Publication member totals differ")
        require(result["verified_members"] == manifest["complete_member_readback"]["verified_members"]
                and result["verified_uncompressed_bytes"]
                == manifest["complete_member_readback"]["verified_uncompressed_bytes"],
                "Publication readback totals differ")
        required = indexed(bound["required_publication_inputs"], "embedded required build inputs")
        bound_pdfs = indexed(bound["pdfs"], "embedded source-bound PDFs")
        published_pdfs = indexed(manifest["pdfs"], "published PDFs")
        require(set(bound_pdfs) == set(published_pdfs)
                == {"build/" + d + ".pdf" for d in DOCS},
                "The standalone package must bind exactly the four native PDFs")
        require(set(bound_pdfs) <= set(required), "A native PDF is absent from required publication inputs")
        for group in (required, bound_pdfs, published_pdfs):
            for name, row in group.items():
                require(name in rows, "A bound publication input is absent from ZIP: " + name)
                match(rows[name], row, name)
    finally:
        if isinstance(container, PartsReader):
            container.close()
    attempt.record.update(status="published_container_bytes_verified", package_manifest=manifest_info,
                          author_source_commit=manifest["author_source_commit"],
                          publication_commit=manifest["publication_commit"],
                          archive_sha256=manifest["sha256"], **result,
                          verification_scope="Complete member/part bytes and embedded binding consistency. Git ancestry and remote commit availability are not independently queried in standalone verify mode.")


def describe_parts(attempt):
    args = attempt.args
    manifest_info = file_record(args.manifest)
    manifest = load_json(args.manifest, manifest_info)
    require(manifest.get("schema") == "NBO_R120_REFEREE_READY_PACKAGE_V1"
            and manifest.get("archive") == ARCHIVE, "Unexpected completed package manifest")
    archive_info = file_record(args.archive)
    match(archive_info, manifest, "actual ZIP for virtual transport ranges")
    prefix = relative(args.future_prefix) if args.future_prefix else ""
    rows, offset, combined = [], 0, hashlib.sha256()
    before = args.archive.stat()
    with args.archive.open("rb") as source:
        for index, block in enumerate(iter(lambda: source.read(PART_SIZE), b"")):
            name = ARCHIVE + ".part" + str(index).zfill(4)
            name = relative(prefix + "/" + name if prefix else name)
            size = len(block)
            rows.append({"path": name, "offset": offset, "bytes": size,
                         "sha256": hashlib.sha256(block).hexdigest(),
                         "git_blob": hashlib.sha1(b"blob " + str(size).encode()
                                                   + b"\0" + block).hexdigest()})
            combined.update(block)
            offset += size
            require(offset <= archive_info["bytes"], "ZIP grew during chunk description")
    require(signature(args.archive.stat()) == signature(before)
            and offset == archive_info["bytes"]
            and combined.hexdigest() == archive_info["sha256"],
            "ZIP changed during virtual chunk description")
    descriptor = {
        "schema": "NBO_R120_VIRTUAL_ZIP_CHUNKS_V1", "archive": ARCHIVE,
        **archive_info, "package_manifest": {"path": args.manifest.name, **manifest_info},
        "author_source_commit": manifest["author_source_commit"],
        "publication_commit": manifest["publication_commit"],
        "chunk_size": PART_SIZE, "future_prefix": prefix, "chunks": rows,
        "virtual_descriptor_only": True, "physical_chunk_files_written": 0,
        "remote_upload_attempted": False, "remote_Git_object_existence_verified": False,
        "helper_sha256": attempt.record["helper"]["sha256"],
        "scope": "Each row describes an exact byte range of the one existing ZIP. Its Git SHA is the identity those bytes would have if uploaded. No chunk file, remote upload, committed path, or remote object existence is claimed.",
        "materialization": "Read ranges in increasing offset order. A later uploader must check actual returned Git object identities; a later assembler must open its destination exclusively, verify each downloaded chunk, concatenate in order, verify the whole ZIP identity, then use the unchanged package manifest for complete ZIP-member verification.",
    }
    write_new(attempt.output / VIRTUAL_PARTS, descriptor)
    attempt.add_output(VIRTUAL_PARTS, "virtual byte-range transport descriptor only")
    attempt.record.update(status="virtual_zip_ranges_described", archive_sha256=archive_info["sha256"],
                          archive_bytes=archive_info["bytes"], described_chunks=len(rows),
                          physical_chunk_files_written=0, remote_upload_attempted=False,
                          package_manifest_sha256=manifest_info["sha256"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    binding = sub.add_parser("bind", help="Bind actual clean build and all S native files")
    binding.add_argument("--revision", type=Path, required=True)
    binding.add_argument("--source-commit", required=True)
    binding.add_argument("--expected-source-tree")
    binding.add_argument("--build-receipt", type=Path, required=True)
    binding.add_argument("--output-dir", type=Path, required=True)
    packaging = sub.add_parser("pack", help="Package every P native path after exact S binding")
    packaging.add_argument("--revision", type=Path, required=True)
    packaging.add_argument("--source-commit", required=True)
    packaging.add_argument("--publication-commit", required=True)
    packaging.add_argument("--required-path", action="append", default=[],
                           help="Additional root-selected native CI/publication receipt required in P; repeatable")
    packaging.add_argument("--no-split", action="store_true",
                           help="Keep only the verified ZIP; do not allocate duplicate 8 MiB parts")
    packaging.add_argument("--output-dir", type=Path, required=True)
    verification = sub.add_parser("verify", help="Verify ZIP or ordered parts without science or Git")
    verification.add_argument("--manifest", type=Path, required=True)
    choice = verification.add_mutually_exclusive_group(required=True)
    choice.add_argument("--archive", type=Path)
    choice.add_argument("--parts-dir", type=Path)
    verification.add_argument("--expected-manifest-sha256")
    verification.add_argument("--source-commit")
    verification.add_argument("--publication-commit")
    verification.add_argument("--output-dir", type=Path, required=True)
    describing = sub.add_parser("describe-parts", help="Describe virtual ZIP chunks without writing parts")
    describing.add_argument("--manifest", type=Path, required=True)
    describing.add_argument("--archive", type=Path, required=True)
    describing.add_argument("--future-prefix", default="",
                            help="Future native relative directory for chunk paths; empty means the revision root")
    describing.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    attempt = Attempt(args)
    try:
        {"bind": bind, "pack": pack, "verify": verify,
         "describe-parts": describe_parts}[args.mode](attempt)
    except BaseException as error:
        attempt.finish(error)
        raise
    else:
        attempt.finish()
        print(json.dumps({"status": attempt.record["status"],
                          "receipt": str(attempt.output / RECEIPT)}), flush=True)


if __name__ == "__main__":
    main()
