"""Bind a complete R14 publication without changing any historical input.

The manifest order is acyclic: PRESERVATION -> FINAL_AUDIT -> EVIDENCE_MANIFEST.
The containing Git commit identifies the publication; it is not written into
one of its own files. Execution sources and publication source are distinct.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import sys
from collections import Counter
from pathlib import Path

from provenance import (
    PRIMARY_SOURCE, EXTENSION_SOURCE, REVIEW_SOURCE, HISTORICAL_TEST_SOURCE,
    PRIMARY_RELATIVE, EXTENSION_RELATIVE, PUBLICATION_RELATIVE,
    digest, git, check_files, pinned_sha256, preservation_check, write_json,
)

EXPECTED_ARTIFACTS = 19
EXPECTED_RAW_FILES = 5639
EXPECTED_RUNS = {37173328744: PRIMARY_SOURCE, 37173700379: EXTENSION_SOURCE}
EXPECTED_SUITES = {"R6": 12, "R7": 11, "R8": 15, "R9": 20, "R10": 18}
DEPENDENCIES = {"numpy": "2.3.5", "scipy": "1.17.0", "numba": "0.65.1",
                "torch": "2.10.0+cpu", "mpmath": "1.3.0"}
STAGES = ["restore", "primary", "extension", "reference", "sensing",
          "diagnostic-tables", "tests", "integrate", "build"]
LIVE_LOG = "logs/pipeline-finalize.log"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read(path):
    return json.loads(Path(path).read_text())


def finite_files(directory):
    return [p for p in directory.rglob("*") if p.is_file()
            and "__pycache__" not in p.parts
            and p.suffix not in {".pyc", ".pyo", ".nbi", ".nbc"}]


def artifact_identity(repo, r):
    manifest = read(r / "ARTIFACT_RESTORE_MANIFEST.json")
    require(manifest["repository"] == "TrillionniumFoundation/NBO", "wrong artifact repository")
    artifacts = manifest["artifacts"]
    require(len(artifacts) == EXPECTED_ARTIFACTS, "wrong artifact count")
    require(len({a["artifact_id"] for a in artifacts}) == EXPECTED_ARTIFACTS, "duplicate artifact ids")
    require(Counter(a["run_id"] for a in artifacts) == {37173328744: 12, 37173700379: 7},
            "wrong artifact run allocation")
    metadata = {row["id"]: row for row in read(r / "results/ARTIFACT_METADATA.json")}
    runs = {row["id"]: row for row in read(r / "results/WORKFLOW_RUNS.json")}
    raw = {}
    for artifact in artifacts:
        run_id = artifact["run_id"]
        require(artifact["source_commit"] == EXPECTED_RUNS[run_id], "artifact generating source mismatch")
        source = metadata[artifact["artifact_id"]]
        require(source["name"] == artifact["name"]
                and source["size_in_bytes"] == artifact["size_bytes"]
                and source["digest"] == "sha256:" + artifact["archive_sha256"]
                and source["workflow_run"]["id"] == run_id
                and source["workflow_run"]["head_sha"] == artifact["source_commit"],
                "artifact API metadata disagrees with restore manifest")
        execution = runs[run_id]
        require(execution["head_sha"] == artifact["source_commit"]
                and execution["status"] == "completed" and execution["conclusion"] == "success",
                "original numerical workflow was not completed successfully")
        prefix = str(PRIMARY_RELATIVE if run_id == 37173328744 else EXTENSION_RELATIVE) + "/results/"
        require(artifact["destination"] == prefix, "unexpected artifact extraction destination")
        for name, sha in artifact["files"].items():
            require(name.startswith(prefix), "artifact path is outside its declared result directory")
            require(name not in raw or raw[name] == sha, "conflicting shared artifact member")
            raw[name] = sha
    require(len(raw) == EXPECTED_RAW_FILES, "wrong unique raw-file count")
    actual = {str(p.relative_to(repo))
              for parent in [PRIMARY_RELATIVE, EXTENSION_RELATIVE]
              for p in finite_files(repo / parent / "results")}
    require(actual == set(raw), "original result directories gained or lost files")
    check_files(repo, raw, "original raw artifact identity failed")
    restoration = read(r / "results/ARTIFACT_RESTORATION.json")
    require(restoration["unique_files"] == EXPECTED_RAW_FILES
            and restoration["all_members_identical"] is True
            and restoration["restore_manifest_sha256"] == digest(r / "ARTIFACT_RESTORE_MANIFEST.json")
            and set(restoration["generating_commits"]) == set(EXPECTED_RUNS.values()),
            "artifact restoration ledger is incomplete")
    require({a["artifact_id"] for a in restoration["artifacts"]} == {a["artifact_id"] for a in artifacts},
            "restoration did not cover all artifacts")
    canonical = json.dumps(raw, sort_keys=True, separators=(",", ":")).encode()
    return raw, {"artifacts": EXPECTED_ARTIFACTS, "unique_files": len(raw),
                 "archive_members_including_shared_files": sum(len(a["files"]) for a in artifacts),
                 "file_map_sha256": hashlib.sha256(canonical).hexdigest(),
                 "generating_sources": EXPECTED_RUNS,
                 "all_original_members_identical": True}


def check_manifest(repo, path, script):
    record = read(path)
    require(record["reporting_script_sha256"] == digest(script), "report script hash differs: " + str(script))
    for group in ["inputs", "outputs"]:
        check_files(repo, record[group], "component manifest " + group)
    return record


def numerical_gates(repo, r):
    primary = read(r / "results/AUDIT.json")
    require(primary["source_commit"] == PRIMARY_SOURCE and primary["development"] is False,
            "primary audit relabelled or nonfinal")
    for name, expected in {"primary_fits": 90, "all_fits": 121, "policy_evaluations": 244,
                           "method_comparisons": 120, "raw_arrays_replayed": 364,
                           "one_sided_used": 728, "one_sided_allocated": 4000}.items():
        require(primary[name] == expected, "primary audit count: " + name)
    require(not primary["training_failures"], "primary fitting failures remain")
    primary_provenance = read(r / "results/PRIMARY_REPLAY_PROVENANCE.json")
    require(primary_provenance["execution_source_commit"] == PRIMARY_SOURCE
            and primary_provenance["reporting_script_sha256"] == digest(r / "code/report_primary.py")
            and primary_provenance["original_records_modified"] is False
            and primary_provenance["numerical_experiments_reexecuted"] is False,
            "primary replay provenance is inconsistent")
    check_files(repo, primary_provenance["numerical_source_files"], "primary historical source map")
    extension = read(r / "results/EXTENSION_AUDIT.json")
    require(extension["source_commit"] == EXTENSION_SOURCE and extension["complete"] is True
            and extension["union_check_complete"] is True,
            "extension audit is incomplete or relabelled")
    for name, expected in {"one_sided_used": 196, "primary_one_sided_used": 728,
                           "union_one_sided_used": 924, "one_sided_allocated": 4000}.items():
        require(extension[name] == expected, "extension inference allocation: " + name)
    for name, expected in {"source_fits": 28, "policy_evaluations": 56,
                           "paired_comparisons": 42, "mechanism_panels": 7}.items():
        require(extension["summary"][name] == expected, "extension completeness: " + name)
    manifests = {}
    for name, script in [("TABLE_MANIFEST.json", "report_primary.py"),
                         ("EXTENSION_TABLE_MANIFEST.json", "report_extension.py"),
                         ("DIAGNOSTIC_TABLE_MANIFEST.json", "diagnostic_tables.py")]:
        manifests[name] = check_manifest(repo, r / name, r / "code" / script)
    require(manifests["DIAGNOSTIC_TABLE_MANIFEST.json"]["new_statistical_endpoints"] == 0,
            "diagnostics silently added confidence endpoints")
    require(extension["reporting_script_sha256"] == digest(r / "code/report_extension.py"),
            "extension audit was generated by different report code")
    return primary, extension, manifests


def diagnostic_gates(repo, r, plan):
    directory = r / "results/reference"
    reference = read(directory / "REFERENCE_DIAGNOSTICS.json")
    require(reference["source_commit"] == PRIMARY_SOURCE
            and reference["diagnostic_program_sha256"] == digest(r / "code/reference_diagnostics.py"),
            "scalar diagnostic source mismatch")
    for key in ["original_inputs_unchanged", "all_original_arrays_reproduced",
                "all_howard_steps_converged", "all_howard_iteration_counts_match"]:
        require(reference[key] is True, "scalar replay failed: " + key)
    require(len(reference["records"]) == 4, "incomplete scalar diagnostic grids")
    manifest = read(directory / "MANIFEST.json")
    require(manifest["diagnostic_program_sha256"] == reference["diagnostic_program_sha256"],
            "scalar manifest source mismatch")
    check_files(directory, manifest["outputs"], "scalar diagnostic output hash")
    check_files(repo / PRIMARY_RELATIVE / "results/reference", manifest["original_inputs"],
                "scalar original input hash")
    directory = r / "results/sensing"
    index, protocol, environment = [read(directory / name) for name in
                                     ["INDEX.json", "PROTOCOL.json", "ENVIRONMENT.json"]]
    require(index["complete"] is True and index["records"] == 3 and index["diagnostic_rows"] == 18,
            "incomplete sensing diagnostics")
    require(index["protocol_sha256"] == digest(directory / "PROTOCOL.json")
            and environment["protocol_sha256"] == index["protocol_sha256"]
            and environment["script_sha256"] == digest(r / "code/sensing_diagnostic.py"),
            "sensing protocol or program changed after execution")
    declared = plan["sensor_diagnostic"]
    for key in ["dimensions", "training_seed", "checkpoint_iteration", "paths", "actor_cells",
                "truth_refinement", "noise_seed"]:
        require(protocol[key] == declared[key], "sensing design differs from revision plan: " + key)
    require(protocol["sensor_noise_rms"] == declared["normalized_sensor_rms"],
            "sensing noise family changed")
    check_files(repo, environment["weights"], "sensing original weights")
    check_files(repo, environment["historical_kernels"], "sensing historical kernels")
    rows = []
    for path in directory.glob("nbo_*.json"):
        record = read(path)
        require(digest(repo / record["weights"]) == record["weights_sha256"]
                and digest(repo / record["raw_file"]) == record["raw_sha256"],
                "sensing raw/weight identity")
        require(record["protocol"] == protocol, "a sensing record used a different protocol")
        rows.extend(record["rows"])
    found = {(row["dimension"], row["actor_cells"], row["sensor_noise_rms"]) for row in rows}
    expected = {(d, n, nu) for d in declared["dimensions"] for n in declared["actor_cells"]
                for nu in declared["normalized_sensor_rms"]}
    require(found == expected and len(rows) == 18, "sensing cells are not complete and unique")
    return {"scalar_grids": 4, "scalar_original_arrays_reproduced": True,
            "sensing_policy_checkpoints": 3, "sensing_rows": 18,
            "new_statistical_endpoints": 0}


def test_gates(repo, r):
    current = read(r / "results/TESTS.json")
    require(current["success"] is True and current["tests"] == 19
            and current["failures"] == 0 and current["errors"] == 0, "current tests failed")
    check_files(repo, current["scripts_sha256"], "current test assertions changed")
    inherited = read(r / "results/INHERITED_TESTS.json")
    require(inherited["success"] is True and inherited["tests"] == 104
            and inherited["tested_source_commit"] == HISTORICAL_TEST_SOURCE
            and inherited["current_roots_modified"] is False
            and inherited["historical_assertions_modified"] is False,
            "historical tests failed or used the wrong view")
    for row in inherited["reports"]:
        require(row["returncode"] == 0, "historical test process failure")
    detail = inherited["historical_details"]
    require(detail["history_unchanged"] is True, "historical numerical inputs changed")
    require({row["suite"]: row["tests"] for row in detail["suites"]} == EXPECTED_SUITES,
            "historical suites were omitted or replaced")
    require(all(row["success"] and not row["failures"] and not row["errors"] for row in detail["suites"]),
            "an inherited suite failed")
    return {"current": 19, "inherited": 104, "total": 123, "all_passed": True,
            "historical_source_commit": HISTORICAL_TEST_SOURCE,
            "historical_layout_assertions_run_in_isolated_original_view": True}


def compilation_gate(r):
    records = read(r / "results/COMPILATION.json")
    require(set(records) == {"ECTA", "supp", "response"}, "three compiled documents are required")
    for name, row in records.items():
        pdf, log = r / "build" / (name + ".pdf"), r / "build" / (name + ".log")
        require(pdf.is_file() and pdf.stat().st_size > 0 and pdf.read_bytes().startswith(b"%PDF-"),
                "missing compiled PDF: " + name)
        require(row["pdf_sha256"] == digest(pdf) and row["pages"] > 0, "compiled PDF identity: " + name)
        require(not row["undefined"] and not row["multiply_defined"] and not row["overfull_hbox_pt"],
                "strict compilation gate failed: " + name)
        text = log.read_text(errors="replace")
        require(not re.search(r"undefined references|Citation .* undefined|Reference .* undefined|Undefined control sequence", text),
                "undefined source reference survived: " + name)
        require(not re.search(r"multiply.defined (labels|citations)|Overfull \\[hv]box", text),
                "typography/reference defect survived: " + name)
        pages = re.findall(r"Output written on .*?\((\d+) pages?", text, re.S)
        require(pages and int(pages[-1]) == row["pages"], "compiled page count differs: " + name)
    return records


def source_gate(repo, r, component_manifests, strict):
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    declared = os.environ.get("NBO_R14_SOURCE_COMMIT")
    generated = {name for manifest in component_manifests.values() for name in manifest["outputs"]}
    contracts = set()
    for path in finite_files(r / "code"):
        if path.suffix == ".py":
            contracts.add(str(path.relative_to(repo)))
    for name in ["REVISION_PLAN.json", "ARTIFACT_RESTORE_MANIFEST.json", "MATHEMATICAL_AUDIT.md",
                 "README.md", "RESPONSE_MAP.json"]:
        contracts.add(str((r / name).relative_to(repo)))
    for folder in ["archive", "review_source", "manuscript"]:
        for path in finite_files(r / folder):
            relative = str(path.relative_to(repo))
            if relative not in generated and not relative.endswith("archive/conclusion.base.tex"):
                contracts.add(relative)
    workflow = ".github/workflows/nbo-r14-delivery.yml"
    if (repo / workflow).is_file():
        contracts.add(workflow)
    contracts.update({"ECTA.tex", "supp.tex", "README.md"})
    current = {name: digest(repo / name) for name in sorted(contracts)}
    if declared:
        require(head == declared, "wrong reporting-source checkout")
        pinned = pinned_sha256(repo, declared, contracts)
        require(current == pinned, "reporting program or authored input changed during reproduction")
    else:
        require(not strict, "NBO_R14_SOURCE_COMMIT is required for publication-source verification")
    return {"reporting_source_commit": declared, "reporting_checkout_commit": head,
            "source_checkout_asserted": bool(declared), "source_contracts_sha256": current,
            "scope": "The generating studies keep their original source commits. "
                     "The containing descendant Git commit identifies the materialized publication."}


def run(repo, strict=False, require_reproduction=False):
    repo = Path(repo).resolve()
    r = repo / PUBLICATION_RELATIVE
    # A failed rerun must not leave an earlier success record appearing current.
    for name in ["FINAL_AUDIT.json", "EVIDENCE_MANIFEST.json"]:
        previous = r / name
        if previous.exists():
            previous.unlink()
    plan = read(r / "REVISION_PLAN.json")
    require(plan["base_commit"] == EXTENSION_SOURCE and plan["review_commit"] == REVIEW_SOURCE
            and plan["new_training"] is False, "revision plan changed its declared base or training scope")
    raw, artifact_audit = artifact_identity(repo, r)
    primary, extension, manifests = numerical_gates(repo, r)
    diagnostic = diagnostic_gates(repo, r, plan)
    tests = test_gates(repo, r)
    compilation = compilation_gate(r)
    actual_versions = {name: importlib.metadata.version(name) for name in DEPENDENCIES}
    require(actual_versions == DEPENDENCIES, "the declared numerical dependency versions are required")
    source = source_gate(repo, r, manifests, strict)
    reproduction_path = r / "results/REPRODUCTION.json"
    reproduction = read(reproduction_path) if reproduction_path.exists() else None
    if require_reproduction:
        require(reproduction is not None, "reproduction ledger missing")
    if reproduction is not None:
        require(reproduction["pre_finalization_complete"] is True
                and [row["stage"] for row in reproduction["stages"]] == STAGES
                and all(row["returncode"] == 0 for row in reproduction["stages"]),
                "reproduction did not complete every dependency stage")
        check_files(repo, reproduction["program_sha256"], "program changed after reproduction began")
    archive_map = {"ECTA.tex": str(PUBLICATION_RELATIVE / "archive/ECTA.base.tex"),
                   "supp.tex": str(PUBLICATION_RELATIVE / "archive/supp.base.tex"),
                   "README.md": str(PUBLICATION_RELATIVE / "archive/README.base.md")}
    preservation = preservation_check(repo, EXTENSION_SOURCE, archive_map)
    require(len(preservation["files"]) == 2826, "unexpected base tracked-blob count")
    write_json(r / "PRESERVATION.json", preservation)
    editorial = read(r / "EDITORIAL_MAP.json")
    require(editorial["base_commit"] == EXTENSION_SOURCE and editorial["title"] == "Neural Bellman Operators"
            and not editorial["historical_revision_files_edited"], "editorial preservation map mismatch")
    check_files(r / "manuscript", editorial["new_manuscript_files"], "integrated manuscript input changed")
    check_files(r / "archive", editorial["archived_roots"], "archived root changed after integration")
    component_names = ["PRESERVATION.json", "EDITORIAL_MAP.json", "TABLE_MANIFEST.json",
                       "EXTENSION_TABLE_MANIFEST.json", "DIAGNOSTIC_TABLE_MANIFEST.json",
                       "results/AUDIT.json", "results/EXTENSION_AUDIT.json",
                       "results/PRIMARY_REPLAY_PROVENANCE.json", "results/TESTS.json",
                       "results/INHERITED_TESTS.json", "results/COMPILATION.json",
                       "results/ARTIFACT_RESTORATION.json", "results/reference/MANIFEST.json",
                       "results/reference/REFERENCE_DIAGNOSTICS.json", "results/sensing/INDEX.json"]
    if reproduction is not None:
        component_names.append("results/REPRODUCTION.json")
    components = {str((r / name).relative_to(repo)): digest(r / name) for name in component_names}
    final = {
        "revision": "R14", "complete": True,
        "publication_source_verified": source["source_checkout_asserted"],
        "base_commit": EXTENSION_SOURCE, "review_commit": REVIEW_SOURCE,
        **source,
        "generating_studies": {
            "primary": {"source_commit": PRIMARY_SOURCE, "workflow_run_id": 37173328744},
            "fixed_work": {"source_commit": EXTENSION_SOURCE, "workflow_run_id": 37173700379}},
        "artifact_identity": artifact_audit,
        "preservation": {"base_blobs": len(preservation["files"]), "all_preserved": True,
                         "root_archive_map": archive_map},
        "inference": {"primary_one_sided": 728, "extension_one_sided": 196,
                      "total_one_sided": 924, "allocated": 4000, "alpha": 0.05,
                      "new_diagnostic_endpoints": 0},
        "primary": {name: primary[name] for name in ["primary_fits", "all_fits", "policy_evaluations", "method_comparisons"]},
        "extension": extension["summary"], "diagnostics": diagnostic,
        "tests": tests, "compilation": compilation,
        "runtime": {"python": platform.python_version(), "dependencies": actual_versions},
        "components_sha256": components,
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "workflow_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "new_training": False, "historical_raw_records_modified": False,
        "positive_economic_endpoints_not_required_for_software_gate": True,
        "scope": "A completed, source-bound publication of two originally executed studies and separately labelled new diagnostics. "
                 "The gate tests identity, completeness, regression assertions and compilation; it does not require a favorable economic sign.",
        "manifest_order": ["PRESERVATION.json", "FINAL_AUDIT.json", "EVIDENCE_MANIFEST.json"],
    }
    write_json(r / "FINAL_AUDIT.json", final)
    files = dict(raw)
    for path in finite_files(r):
        relative = str(path.relative_to(r))
        if relative in {"EVIDENCE_MANIFEST.json", LIVE_LOG}:
            continue
        files[str(path.relative_to(repo))] = digest(path)
    for name in ["ECTA.tex", "supp.tex", "README.md", "revision_reference.bib",
                 "econsocart.cls", "econsocart.cfg", "ecta-fullname.bst"]:
        files[name] = digest(repo / name)
    write_json(r / "EVIDENCE_MANIFEST.json", {
        "revision": "R14", "reporting_source_commit": source["reporting_source_commit"],
        "generating_sources": [PRIMARY_SOURCE, EXTENSION_SOURCE],
        "files": dict(sorted(files.items())), "file_count": len(files),
        "excluded": ["this self-referential manifest", LIVE_LOG + " (still open while finalizing)",
                     "Python and Numba caches"],
        "history_binding": "All 2,826 base Git blobs are independently bound by PRESERVATION.json; "
                           "all 5,639 restored raw files are individually SHA-256 bound here.",
    })
    print(json.dumps({"complete": True, "source_verified": source["source_checkout_asserted"],
                      "historical_blobs": len(preservation["files"]), "raw_files": len(raw),
                      "tests_passed": tests["total"], "pdfs": 3,
                      "one_sided_statements": 924, "manifest_files": len(files)}, indent=2))
    return final


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--require-source-checkout", action="store_true")
    parser.add_argument("--require-reproduction-ledger", action="store_true")
    arguments = parser.parse_args()
    sys.dont_write_bytecode = True
    run(arguments.repo_root, arguments.require_source_checkout, arguments.require_reproduction_ledger)
