"""Derive full-class payoff-gap accounts from the frozen R15 confirmation.

This reporting-only addition does not train, simulate, select, or create a new
confidence event.  It checks all 128 source-bound records and subtracts each
already reported lower gain endpoint from a deterministic population anchor.
Repeated anchor copies are audited, never treated as new population draws.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
R15 = "revisions/2026-10-04-r15"
METHODS = ["nbo", "raw_costate", "direct_policy", "neural_hjb"]
NAMES = {"nbo": "NBO", "raw_costate": "Raw", "direct_policy": "Direct policy",
         "neural_hjb": "Neural HJB"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def finite(value, name, nonnegative=False):
    value = float(value)
    require(math.isfinite(value) and (not nonnegative or value >= 0),
            "invalid finite quantity: " + name)
    return value


def upward(value):
    """Smallest binary64 not below an exact rational result."""
    value = Fraction(value)
    result = float(value)
    require(math.isfinite(result), "outward result overflow")
    if Fraction.from_float(result) < value:
        result = math.nextafter(result, math.inf)
    require(Fraction.from_float(result) >= value, "outward conversion failed")
    return result


def subtract_upper(upper, lower):
    return upward(Fraction.from_float(float(upper))
                  - Fraction.from_float(float(lower)))


def child_path(base, relative):
    base = Path(base).resolve()
    relative = Path(relative)
    require(not relative.is_absolute() and ".." not in relative.parts,
            "evidence path must be local and relative")
    path = (base / relative).resolve()
    require(path.is_relative_to(base) and path.is_file(),
            "missing or escaping evidence path: " + str(relative))
    return path


def unique_index(rows, keys, expected, label):
    answer = {}
    for row in rows:
        key = tuple(row[k] for k in keys)
        require(key not in answer, "duplicate " + label)
        answer[key] = row
    require(set(answer) == set(expected), "incomplete or extra " + label)
    return answer


def expected_population(d, design):
    law = design["initial_state_population"]
    require(law == {"means": [-.5, 0., .5], "spreads": [0., .25, .5],
                    "weights": "uniform over nine profiles as in R12"},
            "initial population differs from the proved R15 account")
    z = np.linspace(-1., 1., d)
    z -= z.mean()
    z /= np.sqrt(np.mean(z*z))
    return np.asarray([mean + spread*z for mean in law["means"]
                       for spread in law["spreads"]], dtype=np.float64)


def audit_anchor(constants, d, p):
    """Validate ONE population upper bound, before comparing repeated copies."""
    require(constants["dimension"] == d
            and constants["steps"] == p["confirmation"]["steps"]
            and constants["epsilon"] == p["training"]["epsilon"]
            and constants["design"] == "uniform_nine_profiles",
            "anchor constants use a different design")
    profiles = np.asarray(constants["initial_profiles"], dtype=np.float64)
    expected = expected_population(d, p["design"])
    require(np.array_equal(profiles, expected), "anchor initial profiles differ")
    require(constants["population_weights"] == [1./9]*9,
            "anchor population weights are not the declared uniform law")
    components = constants["components"]
    require(len(components) == 9, "nine pointwise anchor accounts are required")
    anchors = []
    for row, y in zip(components, expected):
        require(row["dimension"] == d
                and row["steps"] == p["confirmation"]["steps"]
                and row["epsilon"] == p["training"]["epsilon"]
                and np.array_equal(np.asarray(row["initial_state"]), y),
                "pointwise anchor identity differs from population")
        anchors.append(finite(row["anchor_upper"], "pointwise anchor", True))
    # The intended law is EXACTLY uniform. The binary64 1/9 fields describe
    # that law; multiplication by their rounded sum would change the target.
    exact_mean = sum((Fraction.from_float(x) for x in anchors), Fraction()) / 9
    upper = finite(constants["anchor_upper"], "population anchor", True)
    require(Fraction.from_float(upper) >= exact_mean,
            "stored population anchor rounds below its component average")
    return dict(anchor_upper=upper,
                component_average_outward=upward(exact_mean),
                pointwise_anchor_uppers=anchors,
                population_sha256=hashlib.sha256(canonical({
                    "profiles": expected.tolist(),
                    "weights": "exactly 1/9 for every profile"})).hexdigest(),
                components_sha256=hashlib.sha256(canonical(components)).hexdigest())


def report(protocol_path, results, report_path, manifest_path, out,
           evidence_manifest_path=None, repo=ROOT):
    repo = Path(repo).resolve()
    protocol_path, results, report_path, manifest_path = map(
        lambda x: Path(x).resolve(), [protocol_path, results, report_path, manifest_path])
    evidence_manifest_path = (Path(evidence_manifest_path).resolve()
                             if evidence_manifest_path else
                             manifest_path.parent / "EVIDENCE_MANIFEST.json")
    p, main, manifest, evidence = map(read, [protocol_path, report_path,
                                           manifest_path, evidence_manifest_path])
    require(p["status"] == "frozen_before_confirmatory_execution",
            "confirmatory protocol is not frozen")
    design = p["design"]
    dims, seeds, methods = design["dimensions"], design["seeds"], design["methods"]
    require(dims == [10, 50] and methods == METHODS
            and len(seeds) == len(set(seeds)) == 16,
            "complete declared 128-execution design required")
    source = manifest["numerical_source_commit"]
    require(re.fullmatch("[0-9a-f]{40}", source or "") is not None,
            "immutable numerical source commit missing")
    ph = digest(protocol_path)
    primitive_hash = hashlib.sha256(canonical(design["primitives"])).hexdigest()
    require(ph == manifest["protocol_sha256"] == main["protocol_sha256"],
            "protocol provenance mismatch")
    require(primitive_hash == design["primitives_sha256"]
            == manifest["primitives_sha256"] == main["primitives_sha256"],
            "primitive provenance mismatch")
    require(main["status"] == "complete" and main["trial_count"] == 128
            and main["source_commit"] == source
            and evidence["numerical_source_commit"] == source,
            "main report or evidence source differs")
    source_inventory = manifest["files"]
    for name, row in source_inventory.items():
        require(digest(child_path(repo, name)) == row["sha256"],
                "frozen numerical dependency differs: " + name)
    required_sources = [R15 + "/PROTOCOL.json", R15 + "/code/actor_verifier.py",
                        R15 + "/code/report_experiment.py", R15 + "/code/method_statistics.py",
                        "revisions/2026-10-04-r11/code/policy_certificate.py",
                        "revisions/2026-10-04-r10/code/tube_certificate.py"]
    require(set(required_sources) <= set(source_inventory),
            "anchor and inference sources absent from immutable manifest")

    def check_evidence(path):
        path = Path(path).resolve()
        require(path.is_relative_to(repo), "evidence must lie in the delivered repository")
        name = path.relative_to(repo).as_posix()
        require(evidence["files"].get(name) == digest(path),
                "delivered evidence digest mismatch: " + name)

    for path in [report_path, manifest_path]:
        check_evidence(path)
    for method in methods:
        fp = manifest["method_fingerprints"][method]
        require(hashlib.sha256(canonical(fp["input"])).hexdigest() == fp["sha256"]
                and fp["input"]["method_id"] == method
                and fp["input"]["protocol_sha256"] == ph
                and fp["input"]["files"] == {k: v["sha256"] for k, v in source_inventory.items()},
                "method fingerprint does not bind the frozen source")
    keys = [(d, s, m) for d in dims for s in seeds for m in methods]
    identities = unique_index(main["identity_records"],
                              ["dimension", "stream_seed", "method"], keys, "report identity ledger")
    means = unique_index([x for x in main["method_endpoints"] if x["endpoint"] in methods],
                         ["dimension", "endpoint"], [(d, m) for d in dims for m in methods],
                         "method mean endpoints")
    seed_endpoints = unique_index([x for x in main["seed_endpoints"] if x["endpoint"] in methods],
                                  ["dimension", "stream_seed", "endpoint"], keys,
                                  "conditional policy endpoints")
    events = p["inference"]["method_confirmation_events"]
    require(len(main["method_endpoints"]) + len(main["seed_endpoints"]) == events == 238,
            "existing confirmation event count changed")
    event_alpha = math.nextafter(p["inference"]["alpha_allocation"]["method_confirmation"] / events, 0.)
    require(main["confidence"]["event_count"] == events
            and main["confidence"]["event_alpha"] == event_alpha
            and main["confidence"]["alpha"] == p["inference"]["alpha_allocation"]["method_confirmation"],
            "existing confirmation confidence budget differs")

    audit = []
    anchor_copies = {d: [] for d in dims}
    per_seed = []
    for d, seed, method in keys:
        trial_id = f"d{d}_s{seed}"
        trial = results / trial_id / method
        rp, wp = trial / "RESULT.json", trial / "WORK.json"
        r, w = read(rp), read(wp)
        require(r["complete"] is True and w["complete"] is True and w["returncode"] == 0,
                "incomplete execution cannot enter an economic bound")
        fingerprint = manifest["method_fingerprints"][method]["sha256"]
        shared = dict(method_id=method, trial_id=trial_id, dimension=d, stream_seed=seed,
                      numerical_source_commit=source, protocol_sha256=ph,
                      method_fingerprint=fingerprint)
        c = r["final_confirmation"]
        for record in [r, w, c]:
            for key, value in shared.items():
                require(record.get(key) == value, "execution identity mismatch: " + key)
        for record in [r, c]:
            require(record["source_commit"] == source
                    and record["primitives_sha256"] == primitive_hash,
                    "confirmation source/primitives differ")
        require(c["primitives"] == design["primitives"]
                and c["steps"] == p["confirmation"]["steps"]
                and c["paths"] == p["confirmation"]["paths_per_seed"]
                and c["epsilon"] == p["training"]["epsilon"]
                and r["confirmation_independent_of_selection"] is True
                and c["confirmation_independent_of_selection"] is True,
                "confirmation does not target the declared economy")
        require(hashlib.sha256(canonical(w["environment"])).hexdigest()
                == w["environment_fingerprint"], "work environment fingerprint differs")
        require(finite(w["end_to_end_seconds"], "inclusive work", True) > 0,
                "inclusive work receipt is absent")
        require(bool(r["fallback"]) == bool(c["analytic_schedule"]) == bool(w["fallback"]),
                "fallback provenance differs")
        identity = identities[d, seed, method]
        raw = child_path(trial, c["raw_path"])
        selected = child_path(trial, r["selected_checkpoint"])
        for path in [rp, wp, raw, selected]:
            check_evidence(path)
        require(identity["result_sha256"] == digest(rp)
                and identity["work_sha256"] == digest(wp)
                and identity["raw_sha256"] == digest(raw) == c["raw_sha256"]
                and identity["method_fingerprint"] == fingerprint
                and identity["fallback"] == r["fallback"],
                "main report is not bound to these complete execution records")
        require(digest(selected) == r["selected_checkpoint_sha256"] == c["checkpoint_sha256"],
                "the reported policy differs from the confirmed checkpoint")
        for path in [rp, raw, selected]:
            item = w["files"].get(path.relative_to(trial).as_posix())
            require(item == digest(path),
                    "independent work receipt does not bind the evidence file")
        confirmation_path = child_path(trial, c["json_path"])
        check_evidence(confirmation_path)
        require(w["files"].get(confirmation_path.relative_to(trial).as_posix())
                == digest(confirmation_path), "confirmation receipt differs")
        original = read(confirmation_path)
        normalized = dict(original)
        for key in ["raw_path", "json_path"]:
            normalized[key] = "confirmation/" + original[key]
        normalized["clip"] = original["clipping_threshold"]
        require(normalized == c, "RESULT confirmation differs from the original verifier record")
        anchor = audit_anchor(c["constants"], d, p)
        anchor_copies[d].append(anchor)
        lower = finite(seed_endpoints[d, seed, method]["lower"], "conditional lower gain")
        require(seed_endpoints[d, seed, method]["event_alpha"] == event_alpha
                and lower == c["lower"], "conditional endpoint differs from final confirmation")
        upper = subtract_upper(anchor["anchor_upper"], lower)
        require(finite(c["policy_regret_upper"], "worker policy regret") >= upper,
                "worker regret account rounds below its own deterministic translation")
        per_seed.append(dict(dimension=d, stream_seed=seed, method_id=method,
                             fallback=r["fallback"], population_anchor_upper=anchor["anchor_upper"],
                             gain_lower=lower, full_class_regret_upper=upper,
                             worker_policy_regret_upper=c["policy_regret_upper"]))
        audit.append(dict(dimension=d, stream_seed=seed, method_id=method,
                          result_sha256=digest(rp), work_sha256=digest(wp),
                          raw_sha256=digest(raw), selected_checkpoint_sha256=digest(selected),
                          population_sha256=anchor["population_sha256"],
                          components_sha256=anchor["components_sha256"],
                          population_anchor_upper=anchor["anchor_upper"]))

    populations, rows = [], []
    margin = finite(p["economic_decision"]["equivalence_margin_payoff"], "material margin", True)
    require(margin == .0001, "declared economic margin changed")
    for d in dims:
        copies = anchor_copies[d]
        require(len(copies) == 64 and len({x["population_sha256"] for x in copies}) == 1,
                "repeated copies do not concern one initial population")
        anchors = [x["anchor_upper"] for x in copies]
        # A maximum preserves every valid upper bound even if machine rounding
        # differs across workers. These are repeated constants, NOT 64 draws.
        anchor = max(anchors)
        populations.append(dict(dimension=d, population_anchor_upper=anchor,
                                minimum_stored_copy=min(anchors), maximum_stored_copy=max(anchors),
                                copies=64, all_anchor_copies_bitwise_equal=len({x.hex() for x in anchors}) == 1,
                                all_component_accounts_identical=len({x["components_sha256"] for x in copies}) == 1,
                                population_sha256=copies[0]["population_sha256"],
                                aggregation="maximum of repeated already-population-averaged deterministic upper bounds; no average over algorithm streams"))
        for method in methods:
            endpoint = means[d, method]
            require(endpoint["declared_seeds"] == seeds and endpoint["seed_count"] == 16
                    and endpoint["paths_per_seed"] == p["confirmation"]["paths_per_seed"]
                    and endpoint["event_alpha"] == event_alpha,
                    "method lower endpoint uses another target or event")
            lower = finite(endpoint["lower"], "method lower gain")
            upper = subtract_upper(anchor, lower)
            rows.append(dict(dimension=d, method_id=method,
                             population_anchor_upper=anchor,
                             mean_gain=finite(endpoint["raw_mean"], "method raw gain"),
                             gain_lower=lower, gain_upper=finite(endpoint["upper"], "method upper gain"),
                             full_class_regret_upper=upper, material_payoff_margin=margin,
                             regret_upper_to_margin=upward(Fraction.from_float(upper)/Fraction.from_float(margin)),
                             negative_regret_endpoint=upper < 0,
                             existing_confidence_event_alpha=event_alpha))
    answer = dict(status="complete", record_type="R15 full-class economic bounds from existing endpoints",
                  numerical_source_commit=source, source_commit=source,
                  reporting_source_sha256=digest(__file__), protocol_sha256=ph,
                  primitives_sha256=primitive_hash, main_report_sha256=digest(report_path),
                  source_manifest_sha256=digest(manifest_path),
                  evidence_manifest_sha256=digest(evidence_manifest_path),
                  audited_execution_count=len(audit), populations=populations,
                  method_bounds=rows, per_seed_bounds=per_seed, identity_audit=audit,
                  additional_alpha=0., existing_confidence=main["confidence"],
                  bound_identity="V_population^* - uniform_stream_mean J(policy) <= population_anchor_upper - existing_method_gain_lower",
                  target="Original continuous capital economy; unrestricted original adapted action-box class for the optimum; complete declared finite-stream mean for each returned method",
                  scope="A deterministic translation of the existing simultaneous confirmation event, conditional on the same numerical proof and arithmetic assumptions. It is not a new confidence event or a claim that the absolute upper bound is tight.",
                  negative_endpoint_scope="A negative upper endpoint would diagnose failure of the confidence event or an implementation assumption; it is preserved and flagged, never reported as a negative true regret.")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    write(out / "ECONOMIC_BOUNDS.json", answer)
    generate_tables(answer, out, repo)
    return answer


def bound_format(value, digits, upper):
    """Directed decimal display: the printed endpoint remains conservative."""
    scaled = Fraction.from_float(float(value)) * 10**digits
    integer = (-((-scaled.numerator)//scaled.denominator) if upper
               else scaled.numerator//scaled.denominator)
    sign = "-" if integer < 0 else ""
    integer = abs(integer)
    return f"{sign}{integer//10**digits}.{integer%10**digits:0{digits}d}"


def generate_tables(answer, out, repo):
    rows = []
    for x in answer["method_bounds"]:
        rows.append(f"{x['dimension']} & {NAMES[x['method_id']]} & "
                    f"{bound_format(x['gain_lower'],6,False)} & "
                    f"{bound_format(x['full_class_regret_upper'],6,True)} & "
                    f"{x['material_payoff_margin']:.4f} & "
                    f"{bound_format(x['regret_upper_to_margin'],1,True)}" + r" \\")
    table = [r"\begin{table}[!htbp]", r"\centering\small",
             r"\caption{Full-class payoff-gap upper bounds and the economic margin}",
             r"\label{tab:r15absolute}", r"\begin{tabular}{llrrrr}", r"\toprule",
             r"$d$ & Method & Gain lower & Regret upper & Margin & Ratio \\",
             r"\midrule", *rows, r"\bottomrule", r"\end{tabular}",
             r"\par\medskip\noindent\footnotesize "
             r"The regret upper bound is $B_{d,\nu}-L_{d,m}$, rounded outward: "
             r"$B_{d,\nu}$ bounds the analytical schedule's loss against the original "
             r"full adapted control class, and $L_{d,m}$ is the existing lower endpoint "
             r"for the uniform mean over all sixteen returned policies. The ratio divides "
             r"the regret upper bound by the prespecified $10^{-4}$ payoff margin. "
             r"All 128 source-bound confirmation records are audited. This deterministic "
             r"translation uses the existing confirmation event and no additional alpha.",
             r"\end{table}"]
    (out / "table_economic_bounds.tex").write_text("\n".join(table) + "\n")
    relative = out.resolve().relative_to(repo).as_posix()
    bounds=answer["method_bounds"]
    ratios=[x["regret_upper_to_margin"] for x in bounds]
    minimum=min(x["full_class_regret_upper"] for x in bounds)
    maximum=max(x["full_class_regret_upper"] for x in bounds)
    if any(x["negative_regret_endpoint"] for x in bounds):
        interpretation=(r"A negative computed upper endpoint is retained and flagged in the account. "
                        r"It indicates a failure of the confidence event or an implementation assumption, "
                        r"rather than a negative economic regret.")
    elif all(x["full_class_regret_upper"]>x["material_payoff_margin"] for x in bounds):
        interpretation=(r"The reported full-class upper bounds range from "+bound_format(minimum,6,True)+
                        " to "+bound_format(maximum,6,True)+r" payoff units. Their ratios to the declared margin range from "+
                        bound_format(min(ratios),1,True)+" to "+bound_format(max(ratios),1,True)+
                        r". Thus the current absolute account gives guarantees at those explicit tolerances. "
                        r"It does not certify proximity to the full optimum within the $10^{-4}$ margin, "
                        r"even when a relative method comparison is resolved.")
    else:
        meeting=[x for x in bounds if x["full_class_regret_upper"]<=x["material_payoff_margin"]]
        interpretation=(r"The full-class upper endpoint is at most the declared $10^{-4}$ margin for "+
                        ", ".join(NAMES[x["method_id"]]+r" at $d="+str(x["dimension"])+"$" for x in meeting)+
                        r". This conclusion follows from the absolute account on the existing simultaneous event; "
                        r"the remaining methods retain the larger explicit upper bounds shown in the table.")
    text = [r"\subsection{Absolute accuracy in the original control problem}",
            r"\label{sec:r15absolute}",
            r"Let $\nu$ be the declared uniform distribution over the nine initial "
            r"profiles, and let $J_\nu^0$ denote the analytical schedule's payoff. "
            r"The pointwise anchor account in \eqref{eq:r10anchorbound} implies "
            r"$V_\nu^*-J_\nu^0\le B_{d,\nu}$ after averaging over this initial "
            r"population. The repeated worker records concern this same bound. "
            r"We verify their profiles and component weights and retain the maximum "
            r"of the already averaged upper bounds if their final rounding differs.",
            r"For a method $m$, write $\overline J_{d,m}=16^{-1}\sum_s "
            r"J_\nu(\pi_{m,s})$. On the simultaneous confirmation event, its "
            r"existing gain lower endpoint satisfies "
            r"$\overline J_{d,m}-J_\nu^0\ge L_{d,m}$. Consequently,",
            "\n".join([r"\begin{equation}\label{eq:r15methodregret}",
                       r"0\le V_\nu^*-\overline J_{d,m}\le B_{d,\nu}-L_{d,m}.",
                       r"\end{equation}"]),
            r"The optimum in this expression ranges over the original adapted "
            r"action-box class. The returned methods use the declared common tube, "
            r"which is a feasible subset. The inequality therefore accounts for "
            r"absolute loss against the original economic problem. It does not "
            r"identify the unobserved loss or require another probability allocation.",
            r"\input{" + relative + r"/table_economic_bounds.tex}",
            interpretation,
            r"Table~\ref{tab:r15absolute} puts this absolute account next to the "
            r"economic margin used for direct method comparisons. A positive gain "
            r"lower endpoint establishes improvement on the schedule; a direct "
            r"comparison resolves a difference between two trained methods; and a "
            r"small right-hand side of \eqref{eq:r15methodregret} would establish "
            r"proximity to the full optimum. These implications concern different "
            r"quantities. The neural HJB comparator supplies an independent candidate "
            r"construction, while the scalar calculation supplies a separate "
            r"finite-grid accuracy account. Neither supplies an exact high-dimensional "
            r"reference value."]
    (out / "economic_bounds.tex").write_text("\n\n".join(text) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", dest="protocol_path", required=True)
    parser.add_argument("--results", required=True)
    parser.add_argument("--report", dest="report_path", required=True)
    parser.add_argument("--manifest", dest="manifest_path", required=True)
    parser.add_argument("--evidence-manifest", dest="evidence_manifest_path")
    parser.add_argument("--repo", default=str(ROOT))
    parser.add_argument("--out", required=True)
    result = report(**vars(parser.parse_args()))
    print(json.dumps({"status": result["status"],
                      "audited_execution_count": result["audited_execution_count"],
                      "method_bounds": len(result["method_bounds"]),
                      "additional_alpha": result["additional_alpha"]}))
