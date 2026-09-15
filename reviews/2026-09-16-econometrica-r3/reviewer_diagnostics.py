#!/usr/bin/env python3
"""Independent, read-only diagnostics for NBO R3 at eb3b908.

Run from a checkout of the review branch:
  python reviews/2026-09-16-econometrica-r3/reviewer_diagnostics.py
Requires NumPy. Does not overwrite author files. A successful diagnostic run
means the reported discrepancies were reproduced, NOT that NBO passed review.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import platform
from pathlib import Path
import numpy as np

REVIEWED_COMMIT = "eb3b908ed0d95f44c762ae9bec562ff1cfeda81d"
SOURCE_SHA256 = "20a5ed73c2b8f533e3f17c76c6cfc789f0ce6e9ce124dd57afbea7b1bc26579a"
SOURCE_BLOB = "a83d97c0ce7439b3031ff47720a925e36fea4857"
AUTHOR_CODE_LABEL = "a694ede0d5408ae3c9e6d7e3dd9131441cb9b146"
SEED = 20260915
EXPECTED_RAW = {
    "r3-merton-analytical": "26fdd00d27a84cffe8ea446ec2666a3a1540b69e82751de2b9b536a4abc524a3",
    "r3-ndu-grid": "bcd4679c5c2356dd880ba25024084dd6296c3858edf9c908457d4ea433276bcb",
    "r3-temporal-self-beta-0p7": "cef683ce7093385e1a3a4b09e91c25c997a68edc7a4062973a1dd43eac210b2e",
    "r3-temporal-self-beta-1p0": "e90642035307fa7c7da1a7dfb5cb7c375c37411e2bff703824a68c68a979e501",
    "r3-cournot-nash": "8954f6417b8b7360f0bd16f60063e5b2aa856f931e92310d9d082907ec3fa959",
    "r3-ez-stationary": "2b25dcd85700b582b2e8f2ebd27bfb4656a0ed6ef18fe833f774b46b1ec0e932",
    "r3-hutchinson-k1": "252cdabf9641a219d68b5479e26506a401e8a79da54b800c9b5b9bcfb2c2a9e3",
    "r3-hutchinson-k2": "ec73277a105a4d4454e1ecea1bfdf99bf3721c363778f225857d6f758b532169",
    "r3-hutchinson-k8": "b4a58dc206e8bac4a0e46d4020173abeb03a1e1517b5a26df9aaf9686e98e25b",
    "r3-hutchinson-k64": "099e76d8c7123cb7e8adeb0dffa42a544e690fc27a0c6609522d343603cc37bb",
}


def temporal_checks(author, beta):
    """Check author policy against undiscounted continuation evaluation.

    rho=0 and Delta=1 are favorable specializations of the manuscript. Only
    the erroneous beta in the evaluation equation is changed. The clipped
    transition and nearest-neighbor grid are retained, not endorsed.
    """
    data = author.temporal_dp(beta, 161, 321, 2)
    w = np.asarray(data["w_grid"])
    stored = np.asarray(data["values"])
    p = np.asarray(data["policies"])
    evaluated = np.zeros_like(stored)
    evaluated[-1] = np.log(w)
    evaluation_residual = []
    for t in (1, 0):
        for i, wi in enumerate(w):
            c = p[t, i]
            j = int(np.argmin(abs(w - max(.1, wi-c))))
            evaluation_residual.append(abs(stored[t, i]-math.log(c)-stored[t+1, j]))
            evaluated[t, i] = math.log(c)+evaluated[t+1, j]
    gaps = []
    for i, wi in enumerate(w):
        c = p[0, i]
        choices = np.append(np.linspace(.05*wi, .95*wi, 641), c)
        next_indices = np.argmin(abs(w[:, None]-np.maximum(.1, wi-choices)[None, :]), axis=0)
        scores = np.log(choices)+beta*evaluated[1, next_indices]
        chosen_j = int(np.argmin(abs(w-max(.1, wi-c))))
        gaps.append(float(max(scores)-math.log(c)-beta*evaluated[1, chosen_j]))
    return {
        "beta": beta, "rho": 0, "Delta": 1, "grid": [161, 321, 2],
        "max_violation_of_manuscript_evaluation_equation": float(max(evaluation_residual)),
        "max_value_difference_after_correct_policy_evaluation": float(np.max(abs(stored-evaluated))),
        "max_one_shot_gain_against_correctly_evaluated_author_continuation": float(max(gaps)),
        "gain_is_a_grid_lower_bound_not_a_global_certificate": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("diagnostic_results.json"))
    args = parser.parse_args()
    source = args.root / "replication/run_r3_diagnostics.py"
    data = source.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    blob = hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if sha != SOURCE_SHA256 or blob != SOURCE_BLOB:
        raise RuntimeError("Source differs from reviewed R3. Review and update tests rather than silently reusing findings.")
    spec = importlib.util.spec_from_file_location("nbo_r3_author", source)
    author = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(author)
    runs = [author.run_merton(SEED, AUTHOR_CODE_LABEL),
            author.run_ndu(SEED, AUTHOR_CODE_LABEL),
            author.run_temporal(.7, SEED, AUTHOR_CODE_LABEL),
            author.run_temporal(1., SEED, AUTHOR_CODE_LABEL),
            author.run_cournot(SEED, AUTHOR_CODE_LABEL),
            author.run_ez(SEED, AUTHOR_CODE_LABEL)]
    runs += [author.run_hutchinson(SEED, AUTHOR_CODE_LABEL, k) for k in (1, 2, 8, 64)]
    runs += [author.run_coupled(SEED, AUTHOR_CODE_LABEL, d) for d in (4, 8, 16)]
    indexed = {r[0]["run_id"]: r for r in runs}
    matches = {name: indexed[name][0]["raw_output_sha256"] == digest for name, digest in EXPECTED_RAW.items()}
    if not all(matches.values()):
        raise RuntimeError("Non-timing raw payload mismatch: inspect environment and numerical changes.")
    ndu_record, ndu_payload = indexed["r3-ndu-grid"]
    nd = ndu_payload["raw"]
    coarse, fine = nd["coarse"], nd["fine"]
    pi_c = np.asarray(coarse["policy_pi"])[0]
    pi_f = np.asarray(fine["policy_pi"])[0, ::2, ::2]
    lock = {}
    for name, item in (("coarse", coarse), ("fine", fine)):
        ug = np.asarray(item["u_grid"])
        moved = sum(int(np.argmin(abs(ug-np.clip(u+th*.25, ug[0], ug[-1])))) != i
                    for i, u in enumerate(ug) for th in np.linspace(-.2, .2, 5))
        lock[name] = {"u_spacing": float(ug[1]-ug[0]), "state_action_pairs_moving_u": int(moved),
                      "unique_consumption": np.unique(item["policy_c"]).tolist(),
                      "unique_theta": np.unique(item["policy_theta"]).tolist(),
                      "unique_pi": np.unique(item["policy_pi"]).tolist()}
    temporal = [temporal_checks(author, beta) for beta in (.7, 1.)]
    hutch = []
    for k in (1, 2, 8, 64):
        raw = indexed[f"r3-hutchinson-k{k}"][1]["raw"]
        loss_of_mean = (1.25-raw["estimate_mean"]/2)**2
        hutch.append({"K": k, "author_mean_of_squared_residuals": raw["empirical_squared_residual"],
                      "squared_residual_of_K_probe_mean": loss_of_mean,
                      "author_realized_shift": raw["objective_shift"],
                      "correct_realized_shift": loss_of_mean-raw["target_squared_residual"],
                      "population_shift_for_K_probe_mean": 7.5/k,
                      "population_shift_for_author_statistic": 7.5})
    roots = np.sort(np.roots([4., 0., -4., -.2]).real)
    h = lambda a: -(a*a-1)**2+.2*a
    bad, good = float(roots[0]), float(roots[-1])
    coupled = []
    for d in (4, 8, 16):
        record, payload = indexed[f"r3-coupled-d{d}"]
        raw = payload["raw"]
        eig = np.linalg.eigvalsh(np.asarray(raw["Q"]))
        coupled.append({"dimension": d, "condition_number": float(eig[-1]/eig[0]),
                        "max_abs_exact_action": float(np.max(np.abs(raw["exact_solution"]))),
                        "all_box_constraints_inactive": bool(np.max(np.abs(raw["exact_solution"])) < 1),
                        "stationarity_residual": record["metrics"]["residual_mean"],
                        "elapsed_seconds_excluded_from_reviewer_digest_comparison": True})
    result = {
        "reviewed_commit": REVIEWED_COMMIT,
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "source": {"path": "replication/run_r3_diagnostics.py", "bytes": len(data), "sha256": sha, "git_blob_sha1": blob},
        "author_rerun": {"records": len(runs), "non_timing_raw_digest_matches": matches,
                         "timing_records_not_required_to_match_raw_digest": ["r3-coupled-d4", "r3-coupled-d8", "r3-coupled-d16"]},
        "D1_missing_diffusion_generator_test": {"test_function": "phi(u,X)=u^2; theta=0 at an interior grid node",
            "continuous_generator": .05**2, "author_transition_generator": 0.,
            "omitted_cross_covariance_for_phi_uX_at_pi_0p8_X_1": .8*.2*.05*(-.25)},
        "D2_boundary_obstruction": {"u_normal_variance": .05**2,
            "max_wealth_drift_at_lower_boundary_over_all_actions": (.02+.8*(.08-.02))*.5-.05,
            "wealth_drift_when_pi_zero_and_c_min": .02*.5-.05,
            "illustrative_wealth_created_by_clip_at_X_0p5_c_0p8_pi_zero": .5-(.5+(.02*.5-.8)*.25)},
        "D3_grid_lock_and_mislabelled_errors": {"grid_lock": lock,
            "reported_metrics": ndu_record["metrics"], "max_portfolio_discrepancy_at_t0_common_nodes": float(np.max(abs(pi_c-pi_f))),
            "note": "The reported policy_error uses consumption alone; improvement_gap is an action-distance, not Hamiltonian value."},
        "D4_temporal_model_mismatch": temporal,
        "D5_two_period_log_counterexample_without_grid_or_floor": {
            "beta": .7, "exponential_beta_c0_over_w": 1/(1+.7+.7**2),
            "sophisticated_beta_c0_over_w": 1/(1+2*.7),
            "assumptions": "rho=0, Delta=1, log utility and log terminal wealth, unrestricted interior consumption"},
        "D6_hutchinson_estimand_mismatch": hutch,
        "D7_stochastic_approximation_counterexample": {"Hamiltonian": "-(a^2-1)^2+0.2*a; a in [-2,2]",
            "isolated_stationary_points": roots.tolist(), "stable_suboptimal_actor": bad,
            "global_maximizer": good, "suboptimal_second_derivative": 4-12*bad*bad,
            "strictly_positive_improvement_gap": h(good)-h(bad),
            "interpretation": "Exact evaluation and isolated actor stationary points do not force zero Hamiltonian gap."},
        "D8_coupled_problem_diagnostics": coupled,
        "limitations": ["No neural training or PDE error certificate is produced by this reviewer script.",
                        "No LaTeX build or PDF layout audit is performed.",
                        "Hash agreement verifies execution/provenance, not economic correctness."]
    }
    assert result["D3_grid_lock_and_mislabelled_errors"]["max_portfolio_discrepancy_at_t0_common_nodes"] > 1.29
    assert temporal[0]["max_violation_of_manuscript_evaluation_equation"] > .1
    assert temporal[1]["max_violation_of_manuscript_evaluation_equation"] < 1e-12
    assert h(good)-h(bad) > .39
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+"\n", encoding="utf-8")
    print(f"Reproduced {len(runs)} author records and {len(matches)} exact non-timing raw digests.")
    print(f"Portfolio discrepancy: {np.max(abs(pi_c-pi_f))}; SA gap: {h(good)-h(bad)}")
    print(json.dumps(temporal, indent=2))
    print(f"Diagnostic output: {args.output}")

if __name__ == "__main__":
    main()
