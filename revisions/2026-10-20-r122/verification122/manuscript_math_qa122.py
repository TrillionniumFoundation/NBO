"""Read-only manuscript closure and exact inference-constant checks.

This administrative verifier never imports scientific service modules or
queries an economic model.  It hashes the frozen source closure, traverses
the four current TeX roots, and checks the rational arithmetic printed in
the new inference proof.  The accompanying manual review is scoped to the
listed mathematical chains; it is not a formal proof assistant or a claim
to have newly proved every retained historical theorem.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re

REVISION = Path(__file__).resolve().parents[1]
REPO = REVISION.parents[1]
FREEZE = "2f483615c8bc0037e43ec01a16cce05c724f8c60"
ROOTS = ("ECTA.tex", "supp.tex", "appendix.tex", "RESPONSE_TO_REFEREE.tex")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uncomment(text: str) -> str:
    return re.sub(r"(?<!\\)%[^\n]*", "", text)


def closure() -> dict:
    seen, missing = {}, set()
    labels, references, citations = defaultdict(list), defaultdict(list), defaultdict(list)
    bibliography = set()

    def walk(path: Path) -> None:
        path = path.resolve()
        if path in seen:
            return
        if not path.is_file():
            missing.add(str(path.relative_to(REVISION)))
            return
        raw = path.read_text()
        body = uncomment(raw)
        rel = str(path.relative_to(REVISION))
        seen[path] = {"path": rel, "sha256": sha(path)}
        for value in re.findall(r"\\label\s*\{([^{}]+)\}", body):
            labels[value].append(rel)
        for value in re.findall(r"\\(?:ref|eqref|pageref|autoref)\*?\s*\{([^{}]+)\}", body):
            references[value].append(rel)
        for group in re.findall(r"\\cite\w*\*?(?:\[[^\]]*\])*\s*\{([^{}]+)\}", body):
            for value in group.split(","):
                citations[value.strip()].append(rel)
        for group in re.findall(r"\\bibliography\s*\{([^{}]+)\}", body):
            bibliography.update(group.split(","))
        for value in re.findall(r"\\(?:input|include)\s*\{([^{}]+)\}", body):
            target = REVISION / value
            if not target.suffix:
                target = target.with_suffix(".tex")
            walk(target)

    for root in ROOTS:
        walk(REVISION / root)
    bibkeys, bibfiles = set(), []
    for name in sorted(bibliography):
        path = REVISION / (name.strip() + ".bib")
        if not path.is_file():
            missing.add(str(path.relative_to(REVISION)))
            continue
        bibfiles.append({"path": str(path.relative_to(REVISION)), "sha256": sha(path)})
        bibkeys.update(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", path.read_text()))
    pending = [r["path"] for p, r in seen.items() if "R122-INTEGRATION-PENDING" in p.read_text()]
    return {
        "scope": "Union of actual source inputs for four cross-linked TeX wrappers; actual TeX logs and PDF rendering are separately required.",
        "roots": ROOTS,
        "source_files": sorted(seen.values(), key=lambda r: r["path"]),
        "bibliography_files": bibfiles,
        "source_count": len(seen), "label_count": len(labels),
        "reference_count": sum(map(len, references.values())),
        "citation_count": sum(map(len, citations.values())),
        "missing_sources": sorted(missing),
        "unresolved_references": {k: v for k, v in references.items() if k not in labels},
        "unresolved_citations": {k: v for k, v in citations.items() if k not in bibkeys},
        "duplicate_source_labels": {k: v for k, v in labels.items() if len(v) > 1},
        "pending_result_integration_sources": pending,
    }


def constants() -> dict:
    n, tau = 32, Fraction(1, 256)
    rg, rh = 13 * tau / 32, 13 * tau / 16
    exponent = 2 * n * (rg / tau) ** 2
    assert exponent == 2 * n * (rh / (2 * tau)) ** 2 == Fraction(169, 16)
    floors = [math.floor(exponent ** j / math.factorial(j)) for j in range(12)]
    assert floors == [1, 10, 55, 196, 518, 1095, 1928, 2910, 3842, 4509, 4763, 4573]
    assert sum(floors) == 24400 > 23200
    t30 = sum(exponent ** j / math.factorial(j) for j in range(31))
    assert 232 / t30 < Fraction(1, 100)
    assert 696 / t30 < Fraction(3, 100)
    assert 232 * Fraction(1, 23200) == Fraction(1, 100)
    assert sum((Fraction(1, 100), Fraction(1, 100), Fraction(3, 100))) == Fraction(1, 20)

    # All possible binomial counts, evaluated without importing stats122.py.
    # These are deterministic arithmetic checks, not additional observations.
    def below(p: Fraction, k: int) -> bool:
        c, d = p.numerator, p.denominator
        total = sum(math.comb(n, j) * c ** j * (d - c) ** (n - j)
                    for j in range(k, n + 1))
        return 23200 * total <= d ** n

    brackets = []
    for k in range(1, 33):
        lo, hi = Fraction(0), Fraction(1)
        for _ in range(48):
            mid = (lo + hi) / 2
            if below(mid, k):
                lo = mid
            else:
                hi = mid
        assert below(lo, k) and not below(hi, k) and hi - lo == Fraction(1, 2 ** 48)
        brackets.append({"successes": k, "lower": str(lo), "upper": str(hi)})
    assert all(Fraction(a["lower"]) <= Fraction(b["lower"])
               for a, b in zip(brackets, brackets[1:]))
    return {"n": n, "tau": str(tau), "safe_radius": str(rg),
            "signed_radius": str(rh), "exponent": str(exponent),
            "first_twelve_integer_lower_bounds": floors, "integer_sum": sum(floors),
            "Taylor_degree": 30, "Taylor_lower": str(t30),
            "joint_failure_at_most": "1/20", "binomial_all_positive_counts": brackets,
            "production_scientific_imports": 0, "original_economic_queries": 0,
            "new_population_observations": 0}


MANUAL_CHAINS = [
    {
        "name": "Original Bellman objective, existence, selection, stability and full computation graph",
        "sources": ["new121/core_main121.tex", "sections/proofs67.tex", "new119/foundations_main.tex", "new119/foundations_supplement.tex"],
        "finding": "Checked finite-horizon continuity and Borel selection, history-policy comparison, nonexpansiveness, terminal residual accounting, own-future cone construction, original feasible repairs and critic/actor chain-rule qualifications. The retained infinite-horizon assertion uses its additional stationary discount and selection premises.",
        "limits": "Effective covers, feasible repairs, certified integration and original risk assumptions remain premises. Exact ReLU/min-plus realizability is not convergence of a neural training optimizer or an exclusive representational advantage.",
    },
    {
        "name": "Original continuous-risk marginal and boundary-constrained tail",
        "sources": ["new122/regularity122.tex", "new121/marginal_main.tex", "new121/marginal_proofs.tex", "new/precision96-revised.tex", "sections/proofs96.tex"],
        "finding": "Checked the same two-date investment model and original continuous uniform innovations, upper-cost AVaR, strong convexity, constrained central-tail cut and envelope derivative. Fixed-density envelope differentiation and finite outward derivative labels retain the original objective. Convex-order integration bounds do not redefine the innovation law.",
        "limits": "The experiment buys labels from the original optimal V1 primitive; it does not numerically validate a long composition of learned continuation operators. The all-state service totalization cited for inference concerns the prescribed dyadic initial-state population; arbitrary real-state acquisition transfer is separate.",
    },
    {
        "name": "Paid support to action information and safe complete-policy improvement",
        "sources": ["new122/support_to_action_main122.tex", "new122/support_to_action_proofs122.tex", "code122/service122.py"],
        "finding": "Checked the producer's fixed feasible risk-density support, original Q upper before the separately added future allowance, asymmetric derivative intervals, constant-curvature sharpness witnesses, endpoint counterexample, actual-displacement safeguards and gain telescoping. The three tests separately cover strict gain, original regret and objective width.",
        "limits": "Sharpness is restricted to exact support slope and the exact untruncated information class. The implemented finite dyadic radii and global gradient cap need not be sharp. The inner dyadic capacity is used for actual menu construction. Precision-rate guarantees require the stated oracle assumptions and do not remove the curvature/future-policy width floor. Priced stopping is only the compulsory-cost single-decision dominance region.",
    },
    {
        "name": "Joint conditional inference for the frozen original policies",
        "sources": ["new122/inference122.tex", "code122/stats122.py", "new122/numerical122.tex"],
        "finding": "Checked the independent dyadic state law, common original-policy support, paired numerical enclosures, exact same-method identity rule, self-contained bounded-mean proof, rational exponential witness and one-sided binomial inversion. The 116 safe means, 232 threshold events and 348 signed comparisons use the same 32 initial states and the 0.01/0.01/0.03 union-bound allocation.",
        "limits": "Coverage is conditional on fixed inherited actors and frozen rules, valid numerical enclosures and the uniform original-policy qualification premises on P40. The explicit computational-scope paragraph distinguishes finite dyadic exact-rational totalization from measured wall-time/memory and from unproved transfer to a continuous initial-state population. The proof-supported intersection does not independently confirm its sharper gain bound. Same sampled actions for different keys imply sample zero only. Own-incumbent gain does not prove neural-specific superiority or adoption; price regions and repeated clocks are not added population observations.",
    },
    {
        "name": "Recursive utility and stochastic-control interface",
        "sources": ["new110/recursive_bridge.tex", "new119/foundations_supplement.tex"],
        "finding": "Checked decoupled Brownian forward well-posedness, Lipschitz BSDE fixed-point argument, original driver/sign/filtration, residual linearization, bounded-coefficient Girsanov integrability and the boundary-inclusive stopped certificate. The full z=Sigma-transpose-gradient graph is required.",
        "limits": "Optimizing-control attainment requires separate conditions; the infimum suffices for verification. Generic fully coupled or general-martingale NDU/FBSDE remains open. ReLU classical C2 use is not licensed, and investment-policy numerical values are not transferred to another recursive utility.",
    },
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    freeze_path = REVISION / "SOURCE_FREEZE122.json"
    freeze = json.loads(freeze_path.read_text())
    members = freeze["scientific_files"]
    mismatches = [{"path": name, "expected": expected,
                   "actual": sha(REPO / name) if (REPO / name).is_file() else None}
                  for name, expected in members.items()
                  if not (REPO / name).is_file() or sha(REPO / name) != expected]
    tree = closure()
    for chain in MANUAL_CHAINS:
        chain["source_sha256"] = {name: sha(REVISION / name) for name in chain["sources"]}
    supplementary = ["revisions/2026-10-20-r121/code121/labels121.py",
                     "revisions/2026-10-20-r121/frozen108/code/rational96.py"]
    receipt = {
        "kind": "source-bound author manuscript mathematics and static reference QA",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "reviewer_role": "Independent read-only manuscript/math subagent; author revision support, not a new referee decision",
        "source_freeze_commit": FREEZE,
        "source_freeze_manifest_sha256": sha(freeze_path),
        "frozen_files_checked": len(members), "frozen_file_mismatches": mismatches,
        "original_economic_queries": 0, "new_population_observations": 0,
        "production_scientific_imports": 0,
        "manual_review": MANUAL_CHAINS,
        "additional_service_totalization_sources": {name: sha(REPO / name) for name in supplementary},
        "exact_inference_arithmetic": constants(),
        "static_source_reference_audit": tree,
        "scientific_status": "No claim of completed R122 execution, independent economic audit, CI success or final package. Those require their actual source-bound receipts.",
        "mathematical_result": "No material defect identified in the specifically reviewed chains under their stated assumptions and scope. This is a human-readable analytical review, not formal verification or a new proof of all historical results.",
        "final_pdf_qa_status": "Requires separately identified final four-document build, log verification and visual inspection.",
        "verifier_sha256": sha(Path(__file__)),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError("Preserve the existing QA receipt; use a distinct new output path")
    args.output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(args.output), "receipt_sha256": sha(args.output),
                     "frozen_files": len(members), "frozen_mismatches": len(mismatches),
                     "sources": tree["source_count"],
                     "missing_sources": tree["missing_sources"],
                     "unresolved_references": tree["unresolved_references"],
                     "unresolved_citations": tree["unresolved_citations"],
                     "duplicate_source_labels": tree["duplicate_source_labels"],
                     "pending_integration": tree["pending_result_integration_sources"]}, indent=2))
    if mismatches or tree["missing_sources"] or tree["unresolved_references"] or tree["unresolved_citations"] or tree["duplicate_source_labels"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
