"""Bounded author-side record check of the R120 prose; no scientific rerun."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import datetime as dt
import hashlib
import json
import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--revision", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    r = args.revision.resolve()
    o = r / "results120/reporting-attempt01"
    inputs = []
    checks = []

    def identity(p):
        b = p.read_bytes()
        return {"path": str(p), "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}

    def load(name):
        p = o / "tables120" / (name + ".json")
        inputs.append(identity(p))
        return json.loads(p.read_text())

    def check(name, value):
        assert value, name
        checks.append({"check": name, "passed": True})

    g = load("groups120")
    c = load("sample_contrasts120")
    t = load("raw_timing_clocks120")
    p = load("population_groups120")
    prices = load("price_domains120")
    levels = load("paired_bound_levels120")
    bg = load("paired_bound_groups120")
    rh = load("relu_hinge_action_checks120")
    tc = load("timing_action_checks120")
    by = {(x["index"], x["arm"], x["service"]): x for x in g}
    clocks = {(x["index"], x["arm"], x["service"], x["repeat"]): x for x in t}
    check("64 groups each preserve64 state rows", len(g) == 64 and all(x["independent_units"] == 64 for x in g))
    learned = [x for x in g if x["arm"] != "online" and x["service"] != "completed"]
    check("42 learned-incumbent cells have strictly positive independent sample gain lower", len(learned) == 42 and all(F(x["own_incumbent_gain_mean_lower"]) > 0 for x in learned))
    check("every online refinement has exact unchanged actions and zero own gain", all(x["changed_state_actions"] == 0 and F(x["own_incumbent_gain_mean_lower"]) == F(x["own_incumbent_gain_mean_upper"]) == 0 for x in g if x["arm"] == "online"))
    oc = [x for x in c if x["a_arm"] == "online" and x["a_service"] == x["b_service"] == "completed"]
    check("online strictly beats all14 learned completed cells in original sample J", len(oc) == 14 and all(x["sign"] == "strict-negative" for x in oc))
    lp = [x for x in c if x["within_arm_service_contrast"] and x["a_service"] == "legacy-safe" and x["b_service"] == "paired"]
    check("L P comparisons preserve9 exact identities7 unresolved and12 changed rows", Counter(x["sign"] for x in lp) == {"exact-zero": 9, "contains-zero": 7} and sum(x["changed_policy_rows"] for x in lp) == 12)
    ld = [x for x in c if x["within_arm_service_contrast"] and x["a_service"] == "legacy-safe" and x["b_service"] == "direct-refine"]
    check("direct versus L has5 strict gains2 exact identities9 unresolved", Counter(x["sign"] for x in ld) == {"strict-positive": 5, "exact-zero": 2, "contains-zero": 9})
    check("strict direct gains are ReLU Hinge both risks and Spline at threequarters", {(x["index"], x["a_arm"]) for x in ld if x["sign"] == "strict-positive"} == {(0, "relu"), (0, "hinge"), (1, "relu"), (1, "hinge"), (1, "spline")})
    for service, changes, accepted in [("legacy-safe", 388, 807), ("paired", 391, 815), ("direct-refine", 391, 391)]:
        z = [x for x in g if x["service"] == service]
        check(service + " action changes and accepted steps", sum(x["changed_state_actions"] for x in z) == changes and sum(x["accepted_steps"] for x in z) == accepted)
    check("all16 primary paired costs exceed legacy", all(F(x["complete_observed64_total_seconds"]) > F(by[x["index"], x["arm"], "legacy-safe"]["complete_observed64_total_seconds"]) for x in g if x["service"] == "paired"))
    ratios = {}
    for a, b in [("paired", "legacy-safe"), ("direct-refine", "legacy-safe"), ("direct-refine", "paired")]:
        ratios[a, b] = [F(x["complete_observed32_total_seconds"]) / F(clocks[x["index"], x["arm"], b, x["repeat"]]["complete_observed32_total_seconds"]) for x in t if x["service"] == a]
    check("all48 paired clocks slower than legacy", len(ratios["paired", "legacy-safe"]) == 48 and all(x > 1 for x in ratios["paired", "legacy-safe"]))
    check("direct clocks versus legacy retain41 favorable7 adverse", sum(x < 1 for x in ratios["direct-refine", "legacy-safe"]) == 41 and sum(x > 1 for x in ratios["direct-refine", "legacy-safe"]) == 7)
    check("all48 direct clocks faster than paired", all(x < 1 for x in ratios["direct-refine", "paired"]))
    needed = [x for x in levels if x["accepted_needs_mixed_upper_at_recorded_resolution"]]
    check("two necessary levels are one exact shared economic case", len(needed) == 2 and {(x["index"], x["arm"], x["row"], x["trial"], x["m"], x["incumbent_action_hex"], x["candidate_action_hex"]) for x in needed}.__len__() == 1 and {x["service"] for x in needed} == {"paired", "direct-refine"})
    check("necessary original paired upper is negative and separate convex scalar upper positive", all(F(x["difference_upper"]) < 0 < F(x["convex_only_exact_scalar_upper"]) for x in needed))
    check("mixed activity is5961 of9016 levels", len(levels) == 9016 and sum(x["paired_upper_active"] for x in levels) == 5961)
    check("transfer inactive in all2290 acquired density pairs", sum(x.get("density_pairs", 0) for x in bg) == 2290 and sum(x.get("transfer_active_density_pairs", 0) for x in bg) == 0)
    check("all48 population groups keep64 units and42 positive simultaneous lower bounds", len(p) == 48 and all(x["independent_units"] == 64 for x in p) and sum(F(x["simultaneous_population_mean_lower"]) > 0 for x in p) == 42)
    check("ordinary Hoeffding mean lower bounds all zero", all(F(x["hoeffding_population_mean_lower"]) == 0 for x in p))
    check("simultaneous family failure allocation exactlyone twentieth", 192*F(1, 7680) + 48*F(1, 1920) == F(1, 20))
    menu = [x for x in prices if x["repeat"] == "intersection-all-three" and x["comparator"] == "every-conventional-menu-alternative"]
    nn = [x for x in menu if x["arm"] == "relu"]
    check("all32 ReLU menu sufficient and upper intersections empty", len(nn) == 32 and all(x["sufficient_positive_benefit_prices"]["empty"] and x["not_ruled_out_positive_benefit_prices"]["empty"] for x in nn))
    nonempty = [x for x in menu if not x["sufficient_positive_benefit_prices"]["empty"]]
    check("17 nonempty menu sets all completed conventional", len(nonempty) == 17 and all(x["arm"] != "relu" and x["service"] == "completed" for x in nonempty))
    check("all scenario adoption assertions exclude population scope", all(x["population_adoption_claim"] is False for x in prices))
    check("all6144 timing comparisons are state and action identical", len(tc) == 6144 and all(x["action_equal"] and x["state_equal"] for x in tc))
    check("all512 ReLU Hinge action checks equal", len(rh) == 512 and all(x["action_equal"] for x in rh))
    for i in range(2):
        x = next(x for x in prices if x["repeat"] == "actual-primary64" and x["comparator"] == "own-completed" and x["arm"] == "relu" and x["service"] == "paired" and x["index"] == i)
        d = x["sufficient_positive_benefit_prices"]
        check("actual64 ReLU price bound follows exact gain over extra cost risk" + str(i), not d["empty"] and F(d["lower"]) == 0 and d["lower_closed"] and not d["upper_closed"] and F(d["upper"]) == F(x["mean_original_gain_lower"])/F(x["extra_seconds_per_decision"]))
    source_paths = [r/"new120/economic_interpretation120.tex", r/"new120/results120.tex", r/"new120/development120_results.tex", r/"code120/report120.py", r/"code120/stats120.py"]
    source_ids = [identity(x) for x in source_paths]
    for name in ["new120/results120.tex", "new120/development120_results.tex"]:
        check("generated stable snippet unchanged " + name, (r/name).read_bytes() == (o/name).read_bytes())
    for value in inputs:
        check("review input remained unchanged " + Path(value["path"]).name, identity(Path(value["path"])) == value)
    receipt = {
        "kind": "bounded author-side source and exact-record mathematical-scope review",
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "reviewer_role": "AI author assistant; no claim of external or human review",
        "executed_source": identity(Path(__file__).resolve()), "reviewed_sources": source_ids,
        "inputs": inputs, "checks": checks, "actual_checks_passed": len(checks),
        "material_findings": [], "scientific_imports_or_solver_reruns": False,
        "source_read_scope": ["Exact strict-price sign cases, nonnegative price domains and interval intersection", "Original-action RMS is an upper square root of the mean independent squared-error upper bound", "64 independent state units, fixed48 mean and192 event family", "Generated rounded displays are explicitly subordinate to exact rational endpoints", "Production acquisition/cohort costs and independent research/process costs remain distinct"],
        "preserved_limits": ["No neural-specific superiority or full-menu strict adoption", "Nine P L cell identities and seven unresolved economic signs", "All adverse timing clocks and unmeasured timing causality retained", "Finite policy interval compatibility is not the certificate proof", "No new population family or scaling experiment", "PDF layout review is separate and not claimed here"]}
    with args.output.open("x") as f:
        json.dump(receipt, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"receipt": identity(args.output), "checks_passed": len(checks), "material_findings": []}))


if __name__ == "__main__":
    main()
