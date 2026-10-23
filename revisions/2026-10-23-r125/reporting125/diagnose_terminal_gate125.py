"""Post-freeze algebraic diagnosis of an unchanged singleton-capacity action.

Reads existing R125 outputs only. It does not import a production service,
evaluate an economic primitive, mutate frozen sources, or reclassify any
preregistered result. Selection of this diagnostic followed the primary run.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse
import collections
import datetime as dt
import gzip
import hashlib
import json
import resource
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
DELTA, TARGET, OMEGA = F(15, 2**24), F(1, 65536), F(1, 8192)


def plain(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, dict):
        return {str(k): plain(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)):
        return [plain(v) for v in x]
    return x


def write(path, value):
    with path.open("x") as out:
        json.dump(plain(value), out, indent=2, sort_keys=True, allow_nan=False)
        out.write("\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def smoothness(alpha):
    """Original proved rational bound, independently transcribed from R122."""
    beta, mz = F(15, 16), F(181, 64)
    m = F(1413, 128) + beta * (
        F(127, 16) + F(19625, 20480) * alpha / (1 - alpha)
    )
    c = F(4, 5) * m
    return 5 + beta * (F(5, 16) * m + c*c * alpha / (mz * (1 - alpha)))


def upper_at_capacity(record, capacity, L):
    """Exact consequence of a recorded globally valid original support.

    A feasible left displacement h gives q'(a) <= p_upper+e/h+(L-mu)h/2.
    Smoothness then gives q'(A) <= q'(a)+L(A-a). The recorded support's
    original-economic validity remains an inherited premise; this is algebra.
    """
    a = F(record["original_action"])
    gap = F(record["original_q_upper"]) - F(record["support_anchor_lower"])
    assert 0 <= a <= capacity and gap >= 0
    assert record["full_support_continuous_risk"] is True
    assert F(record["support_curvature"]) == 2
    assert F(record["support_slope_lower"]) <= F(record["support_slope_upper"])
    if a == 0:
        h, radius, upper = None, None, F(7)
    else:
        radii = {a} | {F(1, 2**j) for j in range(2, 41) if F(1, 2**j) <= a}
        h = min(radii, key=lambda t: (gap/t + (L-2)*t/2, t))
        radius = gap/h + (L-2)*h/2
        upper = min(F(7), F(record["support_slope_upper"]) + radius)
    return dict(anchor=a, gap=gap, feasible_left_h=h, radius=radius,
                original_gradient_upper=upper,
                capacity_gradient_upper=upper+L*(capacity-a))


def run(output):
    tick = time.perf_counter()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    write(output / "START125.json", dict(
        started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        argv=sys.argv, kind="post-freeze-terminal-gate-diagnostic",
        prospective_experiment=False, original_economic_evaluations=0,
        source_script_sha256=sha(Path(__file__)),
    ))
    try:
        primary = ROOT / "results125/primary/records125.jsonl.gz"
        verification = ROOT / "results125/verification/EXECUTION125.json"
        boundary = ROOT / "BOUNDARIES125.json"
        manifest = ROOT / "SOURCE_FREEZE125.json"
        theorem = ROOT / "new125/acquisition_main125.tex"
        proofs = ROOT / "new125/acquisition_proofs125.tex"
        inputs = {str(p.relative_to(ROOT)): sha(p)
                  for p in (primary, verification, boundary, manifest, theorem, proofs)}
        source = json.loads(manifest.read_text())
        for name, digest in source["files"].items():
            assert sha(ROOT / name) == digest, name
        bnd = json.loads(boundary.read_text())
        assert bnd["source_manifest_sha256"] == sha(manifest)
        audit = json.loads(verification.read_text())
        assert audit["status"] == "executed" and audit["exit_code"] == 0
        assert audit["primary_decisions"] == 936
        with gzip.open(primary, "rt") as stream:
            rows = [json.loads(line) for line in stream if line.strip()]
        assert len(rows) == 936
        by_mode = collections.defaultdict(lambda: dict(decisions=0, stronger_target_successes=0))
        matches = []
        for r in rows:
            by_mode[r["mode"]]["decisions"] += 1
            by_mode[r["mode"]]["stronger_target_successes"] += int(r["target_qualified125"])
            assert r["target_qualified125"] == (
                F(r["certified_regret_upper"]) <= TARGET and F(r["width"]) <= OMEGA
            )
            bracket = r.get("final_q_optimizer_bracket125")
            if r["target_qualified125"] or bracket is None:
                continue
            left, right, action = F(bracket[0]), F(bracket[1]), F(r["action"])
            capacity = F(1, 8) + sum(map(F, r["state125"])) / 16
            if not left == right == action == capacity:
                continue
            # This ex-post rule includes every recorded failed-target singleton
            # at capacity; it does not select a new experimental state or action.
            assert r["same_original_future"] is True and not r["accepted125"]
            assert action == F(r["baseline_action125"])
            assert float.fromhex(r["action_hex"]) == r["action"]
            assert not r["new_queries125"] and not r["localization125"]
            assert F(r["gain_lower125"]) == 0
            assert r["stop125"] == "original-optimum-localized-to-singleton"
            assert F(r["width"]) <= OMEGA
            assert F(r["complete_policy_upper"])-F(r["complete_policy_lower"]) <= F(r["width"])
            prefix = r["complete_fused_prefix125"]
            supports = prefix["initial_support_certificates"]
            case = prefix["multi_anchor_cases"][0]["case"]
            L = smoothness(F(r["alpha"]))
            assert F(case["L"]) == L and F(case["A"]) == capacity
            assert F(case["delta"]) == DELTA and F(case["mu"]) == 2
            assert len(case["payloads"]) == len(supports)
            consequences = []
            for s, saved in zip(supports, case["payloads"]):
                assert s["original_state"] == [r["state125"]] and s["alpha"] == r["alpha"]
                d = upper_at_capacity(s, capacity, L)
                assert F(saved["a"]) == d["anchor"]
                assert F(saved["g_upper"]) == d["original_gradient_upper"]
                consequences.append(d)
            derivative_upper = min(d["capacity_gradient_upper"] for d in consequences)
            assert derivative_upper < 0
            # Convex q has nondecreasing derivative. q'(A)<0 proves q decreases
            # over [0,A], so q(A)=min q. The same implemented future satisfies
            # 0<=J(A)-q(A)<=DELTA. No policy change or value query is required.
            assert DELTA < TARGET
            matches.append(dict(
                identity={k: r[k] for k in ("index", "budget", "arm", "training_loss", "mode", "row")},
                state=r["state125"], risk=r["alpha"], action=action,
                action_hex=r["action_hex"], capacity=capacity,
                recorded_optimizer_bracket=[left, right],
                original_gradient_upper_at_capacity=derivative_upper,
                support_consequences=consequences,
                unchanged_value_interval=[F(r["complete_policy_lower"]), F(r["complete_policy_upper"])],
                unchanged_displayed_width=F(r["width"]), absolute_width_requirement=OMEGA,
                recorded_regret_upper=F(r["certified_regret_upper"]),
                recorded_stronger_target_success=False,
                analytic_terminal_regret_upper=DELTA, stronger_target=TARGET,
                analytic_terminal_bound_meets_target=True,
                frozen_target_result_reclassified=False, policy_changed=False,
                newly_observed_policy_gain=F(0), economic_evaluations=0,
            ))
        assert len(matches) == 2
        assert {r["identity"]["mode"] for r in matches} == {"warm_adaptive", "warm_fixed512"}
        assert by_mode["warm_adaptive"] == dict(decisions=232, stronger_target_successes=231)
        assert by_mode["warm_fixed512"] == dict(decisions=232, stronger_target_successes=231)
        for name, digest in inputs.items():
            assert sha(ROOT / name) == digest, "Diagnostic input changed: " + name
        result = dict(
            status="executed", scope="post-freeze exact saved-support algebra, not new economics",
            source_commit=bnd["source_commit"], source_manifest_sha256=sha(manifest),
            all_frozen_scientific_files_unchanged=len(source["files"]),
            diagnostic_selected_after_primary_results=True, inputs_sha256=inputs,
            theorem="thm:paidwork125 / eq:terminalpolicy125; J(b)-min q <= delta+M*r_b",
            support_validity_scope="Consequences of the original globally valid supports and proved smoothness; independent economic reconstruction remains separate",
            stronger_target_counts_unchanged=dict(by_mode), cases=matches,
            interpretation="The stored value-level optimum bound remains loose after the original action is exactly localized. A direct bracket gate can certify the same action without narrowing absolute value width. This is a prospective implementation change, not an executed action improvement or a revised experimental success.",
            original_economic_evaluations=0, new_population_observations=0,
        )
        write(output / "DIAGNOSTIC125.json", result)
        receipt = dict(status="executed", exit_code=0,
                       ended_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                       seconds=time.perf_counter()-tick,
                       peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                       original_economic_evaluations=0, cases=len(matches),
                       source_script_sha256=sha(Path(__file__)),
                       diagnostic_sha256=sha(output / "DIAGNOSTIC125.json"),
                       frozen_scientific_files_unchanged=len(source["files"]))
        write(output / "EXECUTION125.json", receipt)
        print(json.dumps(receipt, sort_keys=True))
    except BaseException:
        write(output / "FAILURE125.json", dict(
            status="failed", seconds=time.perf_counter()-tick,
            traceback=traceback.format_exc(), partial_outputs_retained=True))
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    run(parser.parse_args().output)
