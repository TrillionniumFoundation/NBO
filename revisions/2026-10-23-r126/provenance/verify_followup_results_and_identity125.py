"""Independent saved-evidence reconciliation; no economic imports or re-timing."""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
import datetime
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def read(relative):
    return json.loads((ROOT / relative).read_text())


def rows(relative):
    path = ROOT / relative
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def key(row):
    return tuple(row[name] for name in ("index", "budget", "arm", "training_loss", "mode"))


def save(relative, value):
    (ROOT / relative).write_text(json.dumps(value, indent=2) + "\n")


primary = rows("results125/primary/records125.jsonl.gz")
original_checks = rows("results125/independent/checks125.jsonl")
followup_checks = rows("results125/independent-followup512/checks125.jsonl")
original = {row["key_id"]: row for row in rows("results125/independent/evaluations125.jsonl.gz")}
refined = {row["key_id"]: row for row in rows("results125/independent-followup512/evaluations125.jsonl.gz")}
selection = read("results125/independent-followup512/SELECTION125.json")
summary = read("results125/independent-followup512/SUMMARY125.json")
execution = read("results125/independent-followup512/EXECUTION125.json")
parent = read("results125/launch-independent-followup512/PROCESS125.json")
old_parent = read("results125/launch-independent/PROCESS125.json")
assert execution["status"] == "executed" and execution["exit_code"] == parent["returncode"] == 0
assert set(refined) == set(selection["keys"]) and len(refined) == 110
assert len(original) == 157
assert len(primary) == len(original_checks) == len(followup_checks) == 936
combined = dict(original)
for identifier, new in refined.items():
    old = original[identifier]
    for field in ("state_hex", "action_hex", "alpha"):
        assert old[field] == new[field], (identifier, field)
    merged = dict(new)
    for field in ("q_lower", "j_lower", "optimum_lower"):
        merged[field] = max(F(old[field]), F(new[field]))
    for field in ("q_upper", "j_upper"):
        merged[field] = min(F(old[field]), F(new[field]))
    assert merged["q_lower"] <= merged["q_upper"]
    assert merged["j_lower"] <= merged["j_upper"]
    combined[identifier] = merged
initial_by_row = {(key(row), row["row"]): row for row in original_checks}
primary_by_row = {(key(row), row["row"]): row for row in primary}
assert len(initial_by_row) == len(primary_by_row) == 936
totals = Counter()
unresolved = []
for row in followup_checks:
    identity = (key(row), row["row"])
    before = initial_by_row[identity]
    production = primary_by_row[identity]
    assert row["initial_contained"] == before["contained"]
    assert row["initial_gain_confirmed"] == before["gain_confirmed"]
    assert row["accepted"] == before["accepted"] == production["accepted125"]
    assert row["final_key"] == before["final_key"] and row["baseline_key"] == before["baseline_key"]
    final = combined[row["final_key"]]
    baseline = combined[row["baseline_key"]]
    lo, hi = F(production["complete_policy_lower"]), F(production["complete_policy_upper"])
    contained = lo <= F(final["j_lower"]) <= F(final["j_upper"]) <= hi
    overlap = not (F(final["j_upper"]) < lo or F(final["j_lower"]) > hi)
    same = row["final_key"] == row["baseline_key"]
    gain_lower = F(0) if same else F(baseline["j_lower"]) - F(final["j_upper"])
    gain_upper = F(0) if same else F(baseline["j_upper"]) - F(final["j_lower"])
    claim = F(before["claimed_gain"])
    gain_ok = not row["accepted"] or gain_lower >= claim
    contradiction = not overlap or (row["accepted"] and gain_upper < claim)
    assert contained == row["contained"] and gain_ok == row["gain_confirmed"]
    assert contradiction == row["contradiction"]
    assert gain_lower == F(row["independent_gain_lower"])
    assert gain_upper == F(row["independent_gain_upper"])
    totals.update(decisions=1, contained=int(contained), accepted=int(row["accepted"]),
                  accepted_gain_confirmed=int(row["accepted"] and gain_ok), contradictions=int(contradiction))
    if not contained:
        unresolved.append({name: row[name] for name in ("index", "budget", "arm", "training_loss", "mode", "row", "final_key")})
for field in ("decisions", "contained", "accepted", "accepted_gain_confirmed", "contradictions"):
    assert totals[field] == summary[field] == execution[field]
assert totals == Counter(decisions=936, contained=934, accepted=251, accepted_gain_confirmed=251, contradictions=0)
assert sum(row["contained"] for row in original_checks) == 850
assert sum(row["accepted"] and row["gain_confirmed"] for row in original_checks) == 193
assert len(unresolved) == 2 and all(row["arm"] == "uniform_dp" and row["index"] == 0 for row in unresolved)
assert summary["counts"]["terminal_contexts"] + summary["counts"]["reused_independent_terminal_contexts"] == 112750
assert summary["changed_production_policies"] == summary["new_population_samples"] == 0
for field, value in summary.items():
    assert execution[field] == value
followup_sources = [
    "POSTFREEZE_AUDIT_BOUNDARY125.json", "POSTFREEZE_AUDIT_FREEZE125.json",
    "provenance/FOLLOWUP_CHRONOLOGY_REVIEW125.json",
    "results125/primary/records125.jsonl.gz", "results125/independent/checks125.jsonl",
    "results125/independent/evaluations125.jsonl.gz",
    "results125/independent-followup512/checks125.jsonl",
    "results125/independent-followup512/evaluations125.jsonl.gz",
    "results125/independent-followup512/SUMMARY125.json",
    "results125/independent-followup512/EXECUTION125.json",
    "results125/launch-independent-followup512/PROCESS125.json",
]
followup_review = {
    "schema": "r125-independent-followup-result-reconciliation-v1",
    "checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status": "passed_saved_rational_reconciliation",
    "source_script_sha256": sha(Path(__file__)),
    "source_boundary": summary["source_boundary"],
    "original_audit_counts_unchanged": {"contained": 850, "accepted_gain_confirmed": 193},
    "combined_counts_independently_recomputed": dict(totals),
    "unresolved_containment_records": unresolved,
    "new_unique_state_risk_action_keys": 110,
    "requested_contexts": 112750,
    "new_terminal_contexts": summary["counts"]["terminal_contexts"],
    "exactly_reused_terminal_contexts": summary["counts"]["reused_independent_terminal_contexts"],
    "child_seconds": execution["seconds"], "parent_seconds": parent["seconds"],
    "cache_loading_seconds_included_in_child": summary["cache_loading_seconds"],
    "both_audit_parent_seconds": old_parent["seconds"] + parent["seconds"],
    "economic_evaluations_in_this_check": 0,
    "scope": "Independent exact reconciliation of saved original/refined intervals, all 936 production rows, all 251 accepted claims and their original flags. The independent evaluator's bound validity is a premise; its economics are not re-executed here. Original capped results are preserved.",
    "inputs_sha256": {relative: sha(ROOT / relative) for relative in followup_sources},
}
save("provenance/FOLLOWUP_RESULT_REVIEW125.json", followup_review)

diagnostic = read("results125/ADOPTION_SUPPORT_DIAGNOSTIC125.json")
assert diagnostic["status"] == "executed"
assert diagnostic["economic_evaluations"] == diagnostic["services_retimed"] == 0
assert diagnostic["original_classifications_unchanged"] is True
for relative, digest in diagnostic["inputs"].items():
    assert sha(ROOT / relative) == digest
controller = "code125/frozen_inputs/revisions/2026-10-22-r123/vendor/2026-10-20-r121/frozen108/code/terminal_controller94.py"
assert sha(ROOT / controller) == diagnostic["fixed_controller_sha256"]
first = {key(row): row for row in primary if row["row"] == 0}
assert len(first) == 234
for risk in (0, 1):
    group = [row for row in first.values() if row["index"] == risk and row["arm"] != "uniform_dp"]
    assert len(group) == 116
    assert len({(tuple(row["state_hex"]), row["alpha"], row["action_hex"], row["future_controller"]) for row in group}) == 1
    assert all(float.fromhex(row["action_hex"]) == row["action"] for row in group)
summaries = {tuple(row["cohort"]): row for row in rows("results125/report/cohorts_summary125.jsonl")}
adoption = {(tuple(row["cohort"]), row["N"]): row for row in rows("results125/report/neural_adoption125.jsonl")}
assert len(adoption) == 128
blocker_roles = Counter()
role_rows = []
seen = set()
cost_checks = 0
for witness in diagnostic["positive_price_identity_blocker_witnesses"]:
    identity = (tuple(witness["cohort"]), witness["N"])
    assert identity not in seen
    seen.add(identity)
    original_region = adoption[identity]
    assert witness["original_optimistic"] == original_region["optimistic"]
    assert original_region["sufficient"]["empty"] is True
    assert original_region["optimistic"]["empty"] is False
    assert F(original_region["optimistic"]["price_lower"]) == 0
    assert F(original_region["optimistic"]["price_upper"]) > 0
    own_key, n = identity
    own = summaries[own_key]
    own_record = first[own_key]
    own_lower = F(own["acquisition"]) / n + F(own["timing_min"])
    candidates = []
    for other_key, other in summaries.items():
        other_record = first[other_key]
        if other["index"] != own["index"] or other["arm"] == "relu":
            continue
        if other_record["action_hex"] != own_record["action_hex"]:
            continue
        if other_record.get("future_controller") != own_record["future_controller"]:
            continue
        assert (other_record["state_hex"], other_record["alpha"]) == (own_record["state_hex"], own_record["alpha"])
        candidates.append((F(other["acquisition"]) / n + F(other["timing_max"]), other_key))
        cost_checks += 1
    assert len(candidates) == witness["same_policy_competitors"] == 100
    upper, competitor_key = min(candidates)
    assert competitor_key == tuple(witness["chosen_blocker"])
    assert own_lower == F(witness["own_lower_complete_cost"])
    assert upper == F(witness["blocker_upper_complete_cost"])
    assert own_lower - upper == F(witness["strictly_positive_complete_cost_gap"]) > 0
    assert F(witness["exact_original_J_difference"]) == 0
    competitor = first[competitor_key]
    blocker_roles[competitor["arm"]] += 1
    matched_budget = competitor["budget"] == own_record["budget"]
    matched_loss = competitor["training_loss"] == own_record["training_loss"]
    role_rows.append({"cohort": list(own_key), "N": n, "blocker": list(competitor_key),
                      "same_training_budget": matched_budget,
                      "same_training_loss": matched_loss,
                      "same_budget_and_loss": matched_budget and matched_loss,
                      "matched_hinge_control": competitor["arm"] == "hinge"})
assert seen == set(adoption)
assert blocker_roles == Counter(online=64, poly2=64)
assert sum(row["same_budget_and_loss"] for row in role_rows) == 16
assert not any(row["matched_hinge_control"] for row in role_rows)
proof = ROOT / "new125/identity_adoption125.tex"
proof_text = proof.read_text()
assert "well-defined and finite" in proof_text
assert "reachable continuation histories" in proof_text
identity_sources = list(diagnostic["inputs"]) + [
    controller, "results125/ADOPTION_SUPPORT_DIAGNOSTIC125.json",
    "reporting125/examine_adoption_support125.py", "new125/identity_adoption125.tex",
]
identity_review = {
    "schema": "r125-independent-policy-identity-adoption-review-v1",
    "checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status": "passed_exact_saved_witnesses_and_analytic_scope_review",
    "source_script_sha256": sha(Path(__file__)),
    "analytic_claim": "Well-defined finite original recursive values coincide under identical implemented policies on the specified state's reachable histories. A strictly positive lower bound on the complete-cost difference gives strict priced-objective domination for every positive price and every time pair inside the declared ranges.",
    "policy_identity_records": 232,
    "risk_groups": 2,
    "original_positive_price_outer_regions_preserved": 128,
    "original_empty_sufficient_regions_preserved": 128,
    "strict_rational_blockers_verified": 128,
    "same_policy_comparator_cost_checks": cost_checks,
    "selected_blocker_roles": dict(blocker_roles),
    "same_budget_witnesses": sum(row["same_training_budget"] for row in role_rows),
    "same_budget_and_loss_witnesses": 16,
    "matched_hinge_witnesses": 0,
    "scope": "Post-execution complete-service economic comparison conditional on the recorded first-state acquisition accounting and descriptive timing ranges. This establishes neither equal-training-information nor equal-feature representation dominance, and no population, future-hardware, or future-runtime guarantee. Zero price ties only with the identical-policy comparator; a different-policy grid may have a different original value.",
    "analytic_corrections_incorporated": [
        "Original recursive objective explicitly well-defined and finite for both policies.",
        "Complete reachable-history policy identity required; first-action equality alone is insufficient.",
        "Common adapted randomization and economic filtration, not merely identical marginal randomization laws.",
        "64 online and 64 poly2 blockers; only 16 match both budget and loss and none is a matched-hinge witness.",
    ],
    "economic_evaluations": 0,
    "services_retimed": 0,
    "inputs_sha256": {relative: sha(ROOT / relative) for relative in identity_sources},
    "comparator_role_rows": role_rows,
}
save("provenance/IDENTITY_ADOPTION_REVIEW125.json", identity_review)
print(json.dumps({"followup": dict(totals), "original_counts": [850, 193], "unresolved_grid_rows": 2,
                  "identity_blockers": 128, "cost_checks": cost_checks, "blocker_roles": dict(blocker_roles),
                  "same_budget_and_loss": 16, "economic_evaluations": 0}, indent=2))
