"""Frozen R85 calibration/evaluation; no fit, actor selection, or precision update.

The two original-law streams are new. Both complete whole-bin implementations
and the exact midpoint check run for every actor; a disagreement aborts and is
retained. --replay regenerates streams and checks saved integer moments/hashes.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import argparse, hashlib, itertools, json, os, resource, sys, time
import numpy as np
import cost77 as k
import cost80 as actors
R = Path(__file__).resolve().parents[1]
STREAMS = (("calibration", 8192, 2026101208501), ("evaluation", 131072, 2026101208502))
BITS = 40
LOG = 11
PROTOCOL_COMMIT = "11bb69900bb31fef107f11aa9db66affc9f68a3a"
REVIEW_COMMIT = "b030d87d7e96440eb25a3178c94ee6a87940cdb0"


def raw_hash(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def input_records() -> dict:
    files = [R / "code" / n for n in ("prospective85.py", "cost77.py", "cost80.py", "float77.py", "independent77.py")]
    files += sorted((R / "results73").glob("*/service.json"))
    files += sorted((R / "results80/construction").glob("*/service.json"))
    return {str(p.relative_to(R)): k.sha(p) for p in files}


def pair_interval(report: dict, first: str, second: str, estimator: str = "conditional") -> tuple[F, F]:
    if first == second:
        return F(0), F(0)
    for rec in report["inference"][estimator]:
        l, u = map(F, rec["interval_exact"])
        if (rec["first"], rec["second"]) == (first, second):
            return l, u
        if (rec["first"], rec["second"]) == (second, first):
            return -u, -l
    raise KeyError((first, second))


def run_stream(label: str, n: int, seed: int, action_tables: dict, output: Path | None) -> dict:
    began = time.perf_counter()
    paths = np.random.Generator(np.random.PCG64(seed)).integers(0, 1 << BITS, size=(n, 4), dtype=np.uint64)
    if output is not None:
        output.mkdir(parents=True, exist_ok=False)
        np.savez_compressed(output / "bins.npz", bins=paths)
    arrays, work, means = {}, {}, {}
    for name in actors.NAMES:
        print(label, name, n, flush=True)
        start = time.perf_counter()
        result, ledger = k.enclose(paths, action_tables[name])
        arrays[name] = result
        ledger["raw_endpoint_sha256"] = raw_hash(result)
        if output is not None:
            np.savez_compressed(output / (name + ".npz"), endpoints=result)
        ledger["seconds_through_serialization"] = time.perf_counter() - start
        work[name] = ledger
        means[name] = tuple(F(sum(map(int, result[j])), n * k.S) for j in (2, 3))
    inference = {}
    for e, estimator in enumerate(("cash", "conditional")):
        records = []
        for a, b in itertools.combinations(actors.NAMES, 2):
            bounds = k.interval(arrays[a][2*e] - arrays[b][2*e+1], arrays[a][2*e+1] - arrays[b][2*e], (-k.H, k.H))
            records.append(dict(first=a, second=b, **bounds))
        inference[estimator] = records
    return dict(label=label, rows=n, seed=seed, raw_bins_sha256=raw_hash(paths),
                empirical_conditional_endpoint_means=means, work=work, inference=inference,
                seconds_before_summary=time.perf_counter()-began,
                estimands=72, family_failure_upper="288*exp(-11) < 0.005")


def without_clocks(obj):
    if isinstance(obj, dict):
        return {a: without_clocks(b) for a, b in obj.items() if "seconds" not in a}
    if isinstance(obj, list):
        return [without_clocks(a) for a in obj]
    return obj


def main(replay: bool = False) -> None:
    start = time.perf_counter()
    k.R = actors.R = R
    k.BITS = BITS
    k.LOG = LOG
    folder = R / "results85"
    if not replay and folder.exists():
        raise FileExistsError("Retain existing attempt; do not overwrite or extend it")
    freeze = input_records()
    action_tables, metadata = actors.controllers()
    records = {}
    for label, n, seed in STREAMS:
        records[label] = run_stream(label, n, seed, action_tables, None if replay else folder / label)
        if not replay:
            k.save(folder / (label + ".json"), records[label])
        if label == "calibration":
            selected = min(actors.NAMES, key=lambda name: (F(records[label]["empirical_conditional_endpoint_means"][name][1]), name))
            print("Calibration selector frozen:", selected, flush=True)
            if not replay:
                k.save(folder / "SELECTOR85.json", dict(selected=selected, calibration_raw_bins_sha256=records[label]["raw_bins_sha256"], evaluation_started=False))
    evaluation = records["evaluation"]
    comparisons = {name: pair_interval(evaluation, selected, name) for name in actors.NAMES}
    regret_upper = max(F(0), *(u for l, u in comparisons.values()))
    factorial = {}
    for n in (8, 16):
        ca = pair_interval(evaluation, f"calibrated-relu-n{n}", f"calibrated-bernstein-n{n}")
        le = pair_interval(evaluation, f"legacy-relu-n{n}", f"legacy-bernstein-n{n}")
        factorial[str(n)] = dict(calibrated_relu_minus_bernstein=ca, legacy_relu_minus_bernstein=le,
                                difference_in_basis_effect=(ca[0]-le[1], ca[1]-le[0]))
    summary = dict(status="passed", protocol_commit=PROTOCOL_COMMIT, review_commit=REVIEW_COMMIT,
        scientific_sources=freeze, actor_metadata=metadata, streams=records,
        selected_controller=selected, evaluation_selected_minus_comparators=comparisons,
        evaluation_selector_regret_upper=regret_upper, factorial=factorial,
        normalized_margin="1/256", new_fit_attempts=0, new_independent_rows=sum(n for _, n, _ in STREAMS),
        joint_failure_upper="576*exp(-11) < 0.01", bin_bits=BITS, log_upper=LOG,
        selector="Minimum calibration conditioned empirical upper endpoint mean, lexical ties",
        environment=k.environment(), peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        seconds_before_summary=time.perf_counter()-start,
        scope="Prospective evaluation of nine frozen complete two-date d=2 actors; no new training, cross-regime score or multi-date experiment. Both independent interval kernels run on every new bin; mathematical multi-date results are separate.")
    if replay:
        old = k.read(folder / "SUMMARY85.json")
        for label in records:
            if without_clocks(k.encode(records[label])) != without_clocks(old["streams"][label]):
                raise AssertionError("Independent deterministic stream replay mismatch: " + label)
        if k.encode(comparisons) != old["evaluation_selected_minus_comparators"]:
            raise AssertionError("Selected-policy inference mismatch")
        k.save(R / "audit/REPLAY85.json", dict(status="passed", rows=sum(n for _,n,_ in STREAMS),
            complete_paths_per_implementation=sum(n for _,n,_ in STREAMS)*9,
            all_144_stream_estimands_recomputed=True, new_independent_rows=0,
            summary_sha256=k.sha(folder / "SUMMARY85.json"), seconds=time.perf_counter()-start))
    else:
        k.save(folder / "SUMMARY85.json", summary)
    print(json.dumps(k.encode(dict(status="passed", replay=replay, selected=selected, regret_upper=regret_upper,
        comparisons=comparisons, factorial=factorial, seconds=time.perf_counter()-start)), indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay", action="store_true")
    main(parser.parse_args().replay)
