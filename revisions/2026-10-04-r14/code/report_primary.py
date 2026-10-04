"""Replay the executed primary study and write only R14 deliverables.

Usage: python revisions/2026-10-04-r14/code/report_primary.py --repo-root .

All R12 worker records retain their original source identities. The exact
historical reporter supplies the statistical replay and existing tables;
this small adapter redirects its outputs and adds missing direct seed rows.
It does not change the fitting, evaluation, statistical bound or old sources.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import platform
import sys
from pathlib import Path

from provenance import (
    PRIMARY_RELATIVE, PRIMARY_SOURCE, PUBLICATION_RELATIVE,
    check_files, digest, git, primary_preflight, write_json,
)


def load_report(repo: Path):
    """Load exact historical modules and prevent generic import collisions."""
    code = repo / PRIMARY_RELATIVE / "code"
    sys.path.insert(0, str(code))
    import common
    if Path(common.__file__).resolve() != (code / "common.py").resolve():
        raise AssertionError("an unrelated common module was already imported")
    # Loading historical kernels prepends their own directories. Restore the
    # current module's import directory before any generic sibling imports.
    sys.path.insert(0, str(code))
    import evaluation
    if Path(evaluation.__file__).resolve() != (code / "evaluation.py").resolve():
        raise AssertionError("a historical evaluation module shadowed R12")
    name = "_nbo_executed_primary_report"
    spec = importlib.util.spec_from_file_location(name, code / "report.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run(repo: Path) -> dict:
    repo = Path(repo).resolve()
    current = repo / PUBLICATION_RELATIVE
    old = repo / PRIMARY_RELATIVE
    manuscript = current / "manuscript"
    manuscript.mkdir(parents=True, exist_ok=True)
    (current / "logs").mkdir(exist_ok=True)
    before = {
        str(path.relative_to(repo)): digest(path)
        for path in (old / "results").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    preflight = primary_preflight(repo)
    report = load_report(repo)
    report.ROOT = repo
    report.R = old
    report.M = manuscript
    report.source = lambda: PRIMARY_SOURCE
    captured = {}

    def redirected_write(path, value):
        path = Path(path)
        allowed = {
            old / "results/AUDIT.json": current / "results/AUDIT.json",
            old / "TABLE_MANIFEST.json": current / "TABLE_MANIFEST.json",
        }
        if path not in allowed:
            raise AssertionError("unexpected historical write requested: " + str(path))
        captured[path.name] = value
        write_json(allowed[path], value)

    report.write = redirected_write
    original_table = report.table
    short_headings = {
        "Mean statistic": "Mean", "Min. lower": "Lower",
        "Max. upper": "Upper", "Max. regret": "Regret ub.",
        "Min. ceiling, bp": "Floor, bp",
    }

    def table(name, title, label, columns, headings, rows, note):
        if name == "table_cost.tex":
            note += (" The saved verification clock starts after model loading and "
                     "construction of deterministic interval constants. It is a timed "
                     "simulation-and-reporting component, not a fully inclusive wall "
                     "clock. Fitting clocks exclude the final selected-weight copy.")
        original_table(name, title, label, columns,
                       [short_headings.get(value, value) for value in headings], rows, note)

    report.table = table
    with (current / "logs/primary-replay.log").open("w") as log:
        with contextlib.redirect_stdout(log):
            audit = report.run(development=False)

    pairs = []
    for path in sorted((old / "results").rglob("*.json")):
        row = json.loads(path.read_text())
        if "bound" not in row or "left" not in row:
            continue
        left = json.loads((repo / row["left"]).read_text())
        right = json.loads((repo / row["right"]).read_text())
        fit = json.loads((repo / left["weights"]).with_suffix(".json").read_text())
        pairs.append((row["dimension"], row["design"], fit["seed"], right["method"], row))
    pairs.sort(key=lambda item: item[:4])
    table(
        "table_paired_seed_all.tex", "Every direct primary method comparison",
        "tab:r14pairedseeds", "rrllrrr",
        ["$d$", "Seed", "State", "Other", "Mean", "Lower", "Upper"],
        [[d, seed, "P" if design == "population" else "0", other.upper(),
          report.fixed(row["bound"]["mean"]), report.fixed(row["bound"]["lower"], "lo"),
          report.fixed(row["bound"]["upper"], "hi")]
         for d, design, seed, other, row in pairs],
        "NBO minus the named comparator on the same initial profiles and innovations. "
        "Every declared stream is retained. A positive lower endpoint establishes a "
        "positive fitted-policy difference; a negative upper endpoint establishes a "
        "negative difference; the remaining intervals are inconclusive. P is the "
        "nine-profile population and 0 is the origin. No optimizer-population inference is made.",
    )
    full = manuscript / "full_results.tex"
    text = full.read_text().replace(
        "\\input{" + str(PRIMARY_RELATIVE / "manuscript") + "/",
        "\\input{" + str(PUBLICATION_RELATIVE / "manuscript") + "/",
    )
    text += "\\input{" + str(PUBLICATION_RELATIVE / "manuscript/table_paired_seed_all.tex") + "}\n"
    full.write_text(text)

    primary_table_names = {
        "table_primary.tex", "table_paired.tex", "table_cost.tex", "table_stress.tex",
        "table_fee.tex", "table_reference.tex", "table_seed_all.tex", "table_aux_all.tex",
        "table_frontier_all.tex", "table_paired_seed_all.tex",
    }
    outputs = {
        str(path.relative_to(repo)): digest(path)
        for path in manuscript.glob("table_*.tex")
        if path.name in primary_table_names
    }
    for name in ["full_results.tex", "results_summary.tex"]:
        outputs[str((manuscript / name).relative_to(repo))] = digest(manuscript / name)
    manifest = captured["TABLE_MANIFEST.json"]
    manifest["outputs"] = outputs
    manifest["execution_source_commit"] = PRIMARY_SOURCE
    manifest["reporting_script_sha256"] = digest(Path(__file__))
    manifest["reporting_scope"] = "R14 materialization of unchanged, source-bound primary records."
    write_json(current / "TABLE_MANIFEST.json", manifest)
    check_files(repo, before, "historical result changed while reporting")
    check_files(repo, preflight["numerical_source_files"], "historical source changed while reporting")
    check_files(repo, manifest["inputs"], "table input changed after replay")
    after_paths = {
        str(path.relative_to(repo)) for path in (old / "results").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    if after_paths != set(before):
        raise AssertionError("historical reporting directory gained or lost files")
    provenance = {
        **preflight,
        "reporting_checkout": git(repo, "rev-parse", "HEAD").decode().strip(),
        "reporting_script_sha256": digest(Path(__file__)),
        "reporting_python": platform.python_version(),
        "materialized_outputs": outputs,
        "original_records_modified": False,
        "numerical_experiments_reexecuted": False,
        "single_numerical_source_for_both_studies": False,
        "all_primary_arrays_replayed": audit["raw_arrays_replayed"],
        "current_publication_tests_are_separate_from_original_worker_tests": True,
    }
    write_json(current / "results/PRIMARY_REPLAY_PROVENANCE.json", provenance)
    print(json.dumps({
        "execution_source_commit": PRIMARY_SOURCE,
        "primary_fits": audit["primary_fits"],
        "policy_evaluations": audit["policy_evaluations"],
        "direct_method_comparisons": audit["method_comparisons"],
        "original_records_modified": False,
        "outputs": str(current.relative_to(repo)),
    }, indent=2))
    return audit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    arguments = parser.parse_args()
    sys.dont_write_bytecode = True
    run(arguments.repo_root)
