"""Stage exact R119 source/PDF and referee-ready input manifests.

Only standard-library hashing, JSON and read-only Git metadata commands run.
No native build, scientific code, test suite, CI query or publication command
is invoked.  The output directory must be explicit and new.  Use --source-only
to prepare source/PDF bindings before root supplies PUBLICATION119.json.
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
import time
import traceback


DOCUMENTS = ("ECTA", "supp", "appendix", "RESPONSE_TO_REFEREE")
BUILD_RECEIPT = "build_receipts119/20261018T151048.083917Z/BUILD_RECEIPT119.json"
PDF_MANIFEST = "SOURCE_PDF_MANIFEST119.json"
INPUT_MANIFEST = "REFEREE_READY_INPUTS119.json"
SOURCE_INVENTORY = "AUTHOR_SOURCE_INVENTORY119.json"
RECEIPT = "MANIFEST_PREPARATION119.json"
PUBLICATION = "PUBLICATION119.json"
CHUNK = 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def write_new(path, value):
    with path.open("xb") as stream:
        stream.write(json_bytes(value))
        stream.flush()
        os.fsync(stream.fileno())


def relative_name(value):
    require(isinstance(value, str) and value, "A nonempty relative POSIX path is required")
    p = PurePosixPath(value)
    require(not p.is_absolute() and ".." not in p.parts and "\\" not in value
            and str(p) == value and value != ".", "Unsafe or noncanonical path: " + value)
    return value


def forbidden_member(relative):
    name = relative.split("/", 1)[0]
    return (name in {INPUT_MANIFEST, RECEIPT, SOURCE_INVENTORY,
                     "REFEREE_READY_PACKAGE119.json"}
            or name == "referee-ready119.zip"
            or name.startswith("referee-ready119.zip.part"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--expected-root-tree")
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="Explicit fresh staging directory; never inferred as the native revision")
    parser.add_argument("--source-only", action="store_true",
                        help="Write source/PDF bindings and full source inventory; no package-input inventory")
    parser.add_argument("--publication", type=Path,
                        help="Root-owned PUBLICATION119.json bytes; defaults to revision/PUBLICATION119.json")
    parser.add_argument("--derivatives-json", type=Path,
                        help='Explicit relative paths, or {"files":[{"path":...,"bytes":...,"sha256":...}]}; no globs')
    args = parser.parse_args()
    source_commit = args.source_commit
    require(re.fullmatch(r"[0-9a-f]{40}", source_commit), "Use a full lowercase immutable commit SHA")
    revision = args.revision.resolve()
    require(revision.is_dir(), "Revision directory does not exist")
    output = args.output_dir.resolve()
    require(output != revision and not output.is_relative_to(revision),
            "This scratch helper requires staging outside the native revision; root copies final bytes")
    output.mkdir(parents=True, exist_ok=False)
    started = time.time()
    receipt = {"schema": "NBO_R119_MANIFEST_PREPARATION_V1", "started_unix": started,
               "revision": str(revision), "output_dir": str(output),
               "author_source_commit": source_commit, "source_only": args.source_only,
               "git_commands": [], "status": "started",
               "scientific_execution": False, "build_execution": False,
               "native_code_imported": False, "CI_queried_or_status_inferred": False,
               "native_files_written": False}
    cache = {}

    def file_record(path):
        path = Path(path)
        require(not path.is_symlink(), "Symlink is not a source/derivative regular file: " + str(path))
        before = path.stat()
        require(stat.S_ISREG(before.st_mode), "Not a regular file: " + str(path))
        key = str(path.resolve())
        signature = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        if key in cache:
            require(cache[key][0] == signature, "File changed during manifest preparation: " + key)
            return dict(cache[key][1])
        sha256 = hashlib.sha256()
        git_blob = hashlib.sha1(b"blob " + str(before.st_size).encode() + b"\0")
        size = 0
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(CHUNK), b""):
                sha256.update(block)
                git_blob.update(block)
                size += len(block)
        after = path.stat()
        require(size == before.st_size and signature ==
                (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
                "File changed while being hashed: " + key)
        result = {"bytes": size, "sha256": sha256.hexdigest(), "git_blob": git_blob.hexdigest()}
        cache[key] = (signature, result)
        return dict(result)

    def local(relative):
        relative = relative_name(relative)
        path = revision.joinpath(*PurePosixPath(relative).parts)
        require(path.resolve().is_relative_to(revision), "Resolved path leaves the revision: " + relative)
        for parent in [path, *path.parents]:
            if parent == revision:
                break
            require(not parent.is_symlink(), "Symlink in revision path: " + relative)
        return path

    def git(arguments, cwd):
        begin = time.time()
        env = dict(os.environ, GIT_NO_LAZY_FETCH="1")
        result = subprocess.run(["git", *arguments], cwd=cwd, env=env, capture_output=True)
        receipt["git_commands"].append({"argv": ["git", *arguments],
            "started_unix": begin, "ended_unix": time.time(), "exit_code": result.returncode,
            "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
            "stderr": result.stderr.decode("utf-8", errors="replace")})
        require(result.returncode == 0, "Read-only Git metadata command failed: " + " ".join(arguments))
        return result.stdout

    try:
        repository = Path(git(["rev-parse", "--show-toplevel"], revision).decode().strip()).resolve()
        require(revision.is_relative_to(repository), "Revision must lie inside its Git repository")
        prefix = revision.relative_to(repository).as_posix()
        resolved = git(["rev-parse", "--verify", source_commit + "^{commit}"], repository).decode().strip()
        require(resolved == source_commit, "The supplied identity is not the resolved commit")
        root_tree = git(["rev-parse", source_commit + "^{tree}"], repository).decode().strip()
        if args.expected_root_tree:
            require(root_tree == args.expected_root_tree, "Author repository tree differs from the supplied identity")
        revision_tree = git(["rev-parse", source_commit + ":" + prefix], repository).decode().strip()
        listing = git(["ls-tree", "-r", "-z", source_commit, "--", prefix + "/"], repository)
        tree = {}
        for entry in listing.split(b"\0"):
            if not entry:
                continue
            header, encoded_name = entry.split(b"\t", 1)
            mode, kind, blob = header.decode("ascii").split()
            name = encoded_name.decode("utf-8")
            require(kind == "blob" and mode in {"100644", "100755"}, "Unsupported Git entry: " + name)
            require(name.startswith(prefix + "/"), "Git path is outside the native revision")
            relative = relative_name(name[len(prefix) + 1:])
            require(relative not in tree, "Duplicate native Git path: " + relative)
            require(not forbidden_member(relative) and relative != PDF_MANIFEST,
                    "The author commit contains a later packaging/self-manifest output: " + relative)
            tree[relative] = {"git_blob": blob, "git_mode": mode}
        require(tree, "The author commit contains no native revision files")
        source = {}
        # Intentionally no extension or directory filter: frozen results and
        # every other native S Git path must be included and read in full.
        for relative, identity in sorted(tree.items()):
            info = file_record(local(relative))
            require(info["git_blob"] == identity["git_blob"], "Local bytes differ from S: " + relative)
            source[relative] = {"path": relative, "kind": "author_source", **info,
                                "git_mode": identity["git_mode"]}

        build_path = local(BUILD_RECEIPT)
        build_info = file_record(build_path)
        build = json.loads(build_path.read_bytes())
        require(build["status"] == "compiled_clean" and not build["diagnostic"]
                and not build["issues"] and not build["placeholders"], "The selected strict build is not clean")
        require(len(build["commands"]) == 19 and all(r["exit_code"] == 0 for r in build["commands"]),
                "The actual selected build does not contain 19 successful commands")
        require(source["build119.py"]["sha256"] == build["builder_sha256"], "Builder differs from S/build receipt")
        declared = {}
        for group in ("source_sha256", "graphic_asset_sha256"):
            for relative, expected in build[group].items():
                require(relative in source, "Declared build source is absent from S: " + relative)
                require(source[relative]["sha256"] == expected, "Declared build source differs: " + relative)
                declared[relative] = source[relative]
        require(set(build["actual_project_inputs"]) == set(DOCUMENTS), "Incomplete TeX project-input closure")
        project_inputs = {}
        for document in DOCUMENTS:
            rows = []
            for relative, expected in build["actual_project_inputs"][document].items():
                require(relative in source, "Actual TeX input absent from S: " + relative)
                require(source[relative]["sha256"] == expected, "Actual TeX input differs from S/build: " + relative)
                rows.append(source[relative])
            require(rows, "Empty actual TeX input closure for " + document)
            project_inputs[document] = sorted(rows, key=lambda row: row["path"])
        generated_inputs = {}
        for document in DOCUMENTS:
            generated_inputs[document] = []
            for relative, expected in build["generated_build_inputs"][document].items():
                require(relative.startswith("build/"), "Generated build input is outside build/: " + relative)
                info = file_record(local(relative))
                require(info["sha256"] == expected, "Generated build input changed: " + relative)
                generated_inputs[document].append({"path": relative, **info})
        pdfs = []
        require(len(build["pdfs"]) == 4, "Exactly four built PDFs are required")
        for row in build["pdfs"]:
            info = file_record(local(row["path"]))
            require(info["bytes"] == row["bytes"] and info["sha256"] == row["sha256"],
                    "Built PDF differs from the actual build receipt: " + row["path"])
            pdfs.append({"path": row["path"], "bytes": info["bytes"], "sha256": info["sha256"]})
        require({row["path"] for row in pdfs} == {"build/" + d + ".pdf" for d in DOCUMENTS},
                "The four PDF paths are incomplete or duplicated")
        helper_info = file_record(Path(__file__))
        source_summary = {"repository_revision_path": prefix, "repository_tree_sha": root_tree,
            "native_revision_tree_sha": revision_tree, "native_files": len(source),
            "native_bytes": sum(row["bytes"] for row in source.values()),
            "scope": "Every native path in the immutable author commit, including all frozen results files; no extension or directory omission."}
        pdf_manifest = {"schema": "NBO_R119_SOURCE_PDF_BINDING_V1", "author_source_commit": source_commit,
            **source_summary, "pdfs": pdfs, "build_receipt": {"path": BUILD_RECEIPT, **build_info},
            "build_status": build["status"], "build_command_count": len(build["commands"]),
            "tool_versions": build["tool_versions"], "source_date_epoch": build["source_date_epoch"],
            "builder_sha256": build["builder_sha256"], "declared_build_sources_verified": len(declared),
            "actual_project_inputs": project_inputs, "generated_build_inputs": generated_inputs,
            "input_scope": build["input_scope"],
            "preparation_helper_sha256": helper_info["sha256"],
            "CI_scope": "No CI state is queried or inferred. Root-owned PUBLICATION119.json separately records actual CI observations.",
            "scope": "Existing clean local build bound to exact committed native sources and four actual PDF bytes; no build or science rerun."}
        write_new(output / PDF_MANIFEST, pdf_manifest)
        write_new(output / SOURCE_INVENTORY, {"author_source_commit": source_commit,
                  **source_summary, "files": list(source.values())})
        receipt.update(source_summary)
        receipt.update({"actual_project_input_counts": {d: len(v) for d, v in project_inputs.items()},
                        "declared_build_sources_verified": len(declared), "verified_pdf_count": len(pdfs)})

        if not args.source_only:
            publication_path = (args.publication or revision / PUBLICATION).resolve()
            publication_info = file_record(publication_path)
            publication = json.loads(publication_path.read_bytes())
            require(publication["author_source_commit"] == source_commit,
                    "Root-owned publication metadata has another author-source identity")
            members = dict(source)
            staged_origins = {}

            def add_member(relative, path, expected=None):
                relative = relative_name(relative)
                require(not forbidden_member(relative), "Excluded self/final-container output: " + relative)
                info = file_record(path)
                if expected:
                    for key in ("bytes", "sha256", "git_blob"):
                        if key in expected:
                            require(info[key] == expected[key], "Selected derivative changed: " + relative)
                if relative in members:
                    require(all(members[relative][k] == info[k] for k in ("bytes", "sha256", "git_blob")),
                            "Duplicate member has conflicting bytes: " + relative)
                else:
                    members[relative] = {"path": relative, "kind": "publication_derivative", **info}
                if Path(path).resolve() != local(relative).resolve():
                    staged_origins[relative] = {"source": str(Path(path).resolve()), **info}

            for row in pdfs:
                add_member(row["path"], local(row["path"]), row)
            add_member(PDF_MANIFEST, output / PDF_MANIFEST)
            add_member(PUBLICATION, publication_path)
            add_member(BUILD_RECEIPT, build_path, build_info)
            selection_record = None
            if args.derivatives_json:
                selection_path = args.derivatives_json.resolve()
                selection = json.loads(selection_path.read_bytes())
                rows = selection["files"] if isinstance(selection, dict) else selection
                require(isinstance(rows, list), "Derivative selection must contain a files list")
                selected = set()
                for row in rows:
                    relative = row if isinstance(row, str) else row["path"]
                    require(relative not in selected, "Duplicate selected derivative: " + relative)
                    selected.add(relative)
                    add_member(relative, local(relative), row if isinstance(row, dict) else None)
                selection_record = {"path": str(selection_path), **file_record(selection_path),
                                    "selected_paths": sorted(selected)}
            required = set(source) | {PDF_MANIFEST, PUBLICATION} | {row["path"] for row in pdfs}
            require(required <= set(members), "Package input is incomplete")
            package_input = {"schema": "NBO_R119_REFEREE_READY_INPUT_V1",
                "author_source_commit": source_commit, **source_summary,
                "files": [members[p] for p in sorted(members)],
                "publication_derivative_members": sum(r["kind"] == "publication_derivative" for r in members.values()),
                "root_selected_derivatives": selection_record,
                "staged_files_to_copy_into_revision": staged_origins,
                "scope": "Every native committed author-source path plus the exact four PDFs, source/PDF manifest, root-owned publication metadata and explicitly selected publication derivatives. No self-input or final ZIP/output-manifest cycle."}
            write_new(output / INPUT_MANIFEST, package_input)
            receipt.update({"package_members": len(members),
                            "publication_derivative_members": package_input["publication_derivative_members"],
                            "staged_files_to_copy_into_revision": staged_origins,
                            "publication_metadata": {"source": str(publication_path), **publication_info}})
        receipt["status"] = "source_pdf_binding_prepared" if args.source_only else "complete_package_input_staged"
    except BaseException:
        receipt["status"] = "failed_manifest_preparation"
        receipt["exception"] = traceback.format_exc()
        raise
    finally:
        receipt["ended_unix"] = time.time()
        receipt["elapsed_seconds"] = receipt["ended_unix"] - started
        receipt["outputs"] = [{"path": p.name, **file_record(p)} for p in sorted(output.iterdir()) if p.is_file()]
        write_new(output / RECEIPT, receipt)
    print(json.dumps({"status": receipt["status"], "author_source_commit": source_commit,
        "source_files": receipt["native_files"], "source_bytes": receipt["native_bytes"],
        "actual_project_input_counts": receipt["actual_project_input_counts"],
        "output_dir": str(output), "receipt": str(output / RECEIPT)}, indent=2))


if __name__ == "__main__":
    main()
