#!/usr/bin/env python3
"""Replay the executed R13 extension and write R14 derived evidence.

The input schema is the 122-line extension.py at c8299feb, not the separate
R13 development fork.  No model is trained or deserialized.  The R13 tree is
read only.  Statistical replay uses the unchanged pure interval functions
from the source-pinned historical kernel; PyTorch is not needed.

Example (run from any directory):
  python report_extension.py --repo /path/to/NBO
  python report_extension.py --repo /path/to/NBO --out /tmp/r14-extension
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import math
import pickletools
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np

SOURCE = "c8299feb2a3af0f147295d50036c8d8acca8f65c"
RUN = 37173700379
REV12 = Path("revisions/2026-10-04-r12")
REV13 = Path("revisions/2026-10-04-r13")
REV14 = Path("revisions/2026-10-04-r14")
NAMES = {"nbo": "NBO", "dpo": "DPO", "linear": "Affine", "raw": "Raw"}
SOURCES = [
    ".github/workflows/nbo-r13-extension.yml",
    str(REV13 / "PROTOCOL.json"), str(REV13 / "code/extension.py"),
    str(REV12 / "PROTOCOL.json"), str(REV12 / "code/common.py"),
    str(REV12 / "code/training.py"), str(REV12 / "code/evaluation.py"),
    "revisions/2026-10-04-r11/code/bellman_study.py",
    "revisions/2026-10-04-r11/code/policy_certificate.py",
    "revisions/2026-10-04-r11/code/fast_arithmetic.py",
    "revisions/2026-10-04-r10/code/tube_neural.py",
    "revisions/2026-10-04-r10/code/tube_certificate.py",
    "revisions/2026-09-29-r6/code/interval_certificate.py",
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(path):
    return sha(Path(path).read_bytes())


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def close(actual, expected, message, atol=2e-14, rtol=1e-12):
    if not math.isclose(float(actual), float(expected), rel_tol=rtol, abs_tol=atol):
        raise AssertionError(f"{message}: {actual!r} != {expected!r}")


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def fmt(x, side=None, digits=6):
    if side == "lo":
        x = math.floor(float(x) * 10**digits) / 10**digits
    elif side == "hi":
        x = math.ceil(float(x) * 10**digits) / 10**digits
    return f"{x:.{digits}f}"


def tab(out, filename, title, label, columns, head, rows, note):
    require(rows, f"empty table {filename}")
    text = "\\begingroup\\small\\setlength{\\tabcolsep}{3pt}\n"
    text += "\\begin{longtable}{" + columns + "}\n"
    text += "\\caption{" + title + "}\\label{" + label + "}\\\\\n"
    hdr = "\\toprule\n" + " & ".join(head) + "\\\\\\midrule\n"
    text += hdr + "\\endfirsthead\n" + hdr + "\\endhead\n"
    text += "\n".join(" & ".join(map(str, row)) + "\\\\" for row in rows)
    text += "\n\\bottomrule\\end{longtable}\n\\noindent " + note + "\n\\endgroup\n"
    (out / "manuscript" / filename).write_text(text)


def pure_kernel(repo):
    """Load only source-checked deterministic interval code, without torch."""
    sys.dont_write_bytecode = True
    path = repo / "revisions/2026-10-04-r10/code/tube_certificate.py"
    spec = importlib.util.spec_from_file_location("r14_extension_tube", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    path = repo / "revisions/2026-10-04-r11/code/policy_certificate.py"
    names = {"sum_axis", "mean_i", "nonnegative", "sqrt_nonnegative", "gamma",
             "weights", "midpoint", "radius", "constants", "empirical_lower"}
    definitions = [x for x in ast.parse(path.read_text()).body
                   if isinstance(x, ast.FunctionDef) and x.name in names]
    require({x.name for x in definitions} == names, "missing pure interval functions")
    namespace = dict(vars(mod), np=np, math=math, U=np.finfo(np.float64).eps,
                     tanh_kernel=None)
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(path), "exec"), namespace)
    return SimpleNamespace(**namespace)


def profiles(d, protocol):
    v = np.linspace(-1.0, 1.0, d)
    v -= v.mean()
    v /= np.sqrt(np.mean(v * v))
    return np.asarray([mu + s * v for mu in protocol["population_means"]
                       for s in protocol["population_spreads"]], dtype=np.float64)


def account(kernel, d, plan, protocol):
    support = profiles(d, protocol)
    wt = kernel.weights(plan["final_steps"])
    components = [kernel.constants(d, plan["final_steps"], protocol["epsilon"], y, wt)
                  for y in support]
    avg = lambda seq: float(kernel.mean_i(kernel.I(np.asarray(seq, dtype=float))).hi)
    return dict(
        initial_profiles=support,
        bias_upper=avg([v["bias_upper"] for v in components]),
        actor_bias_upper=avg([v["actor_bias"]["total"] for v in components]),
        statistic_error_upper=float(kernel.up(max(v["quadrature_and_statistic_roundoff"] for v in components))),
        clipping_threshold=max(v["clipping_threshold"] for v in components),
        clipping_bias=max(v["clipping_bias"] for v in components),
        anchor_upper=avg([v["anchor_upper"] for v in components]),
        state_cap=max(v["state_cap"] for v in components),
    )


def weight_storage(path):
    """Read inert ZIP storage bytes, not pickle execution or torch.load."""
    with zipfile.ZipFile(path) as z:
        require(z.testzip() is None, f"corrupt weight ZIP: {path}")
        keys = [s for s in z.namelist() if re.search(r"/data/\d+$", s)]
        require(keys, f"missing tensor storage: {path}")
        keys.sort(key=lambda s: int(s.rsplit("/", 1)[1]))
        meta_names = [s for s in z.namelist() if s.endswith("/data.pkl")]
        require(len(meta_names) == 1, f"ambiguous weight metadata: {path}")
        meta = z.read(meta_names[0])
        globals_used = [arg for op, arg, _ in pickletools.genops(meta) if op.name == "GLOBAL"]
        require("torch DoubleStorage" in globals_used, "unexpected non-double weight archive")
        require(not any("Storage" in x and x != "torch DoubleStorage" for x in globals_used),
                "mixed storage types in weight archive")
        byteorder = [s for s in z.namelist() if s.endswith("/byteorder")]
        require(len(byteorder) == 1 and z.read(byteorder[0]) == b"little", "unexpected byte order")
        payload = [z.read(k) for k in keys]
        require(all(len(x) % 8 == 0 for x in payload), "non-double storage length")
        return dict(metadata_sha256=sha(meta),
                    storage_sha256=[sha(x) for x in payload],
                    storage_bytes=[len(x) for x in payload]), payload


def hamiltonian(q, action, adjustment):
    return np.log(action).mean(-1) - adjustment / 2 * action.mean(-1)**2 - (q * action).mean(-1)


def greedy(q, times, primitive, epsilon):
    """Independent scalar fixed-point solution of the strictly concave H."""
    times = np.asarray(times).reshape(-1, 1)
    if epsilon is None:
        low = np.full_like(times, primitive["lower"])
        high = np.full_like(times, primitive["upper"])
    else:
        discount = primitive["discount"]
        exponential = np.exp(-discount * (primitive["T"] - times))
        w = (1 - exponential) / discount + exponential
        center = 2 / (w + np.sqrt(w * w + 4 * primitive["adjustment"]))
        low, high = center - epsilon, center + epsilon
    a, b = low.copy(), high.copy()
    for _ in range(64):
        mean = (a + b) / 2
        den = q + primitive["adjustment"] * mean
        action = np.clip(np.where(den > 0, 1 / np.maximum(den, 1e-30), high), low, high)
        left = action.mean(1, keepdims=True) > mean
        a, b = np.where(left, mean, a), np.where(left, b, mean)
    den = q + primitive["adjustment"] * ((a + b) / 2)
    action = np.clip(np.where(den > 0, 1 / np.maximum(den, 1e-30), high), low, high)
    derivative = 1 / action - primitive["adjustment"] * action.mean(1, keepdims=True) - q
    violation = np.where(action <= low + 1e-13, np.maximum(derivative, 0),
                         np.where(action >= high - 1e-13, np.maximum(-derivative, 0), abs(derivative)))
    require(float(violation.max()) < 1e-10, "independent greedy KKT residual")
    return action, float(violation.max())


def mechanism_metrics(arr, source, primitive, epsilon):
    qc, qf, pred = arr["q_coarse"], arr["q_fine"], arr["critic_q"]
    vc, vf, value = arr["values_coarse"], arr["values_fine"], arr["critic_value"]
    n = len(qf)
    ref = qf.mean(0)
    variance = qf.var(0, ddof=1) / n
    H = lambda q, a: hamiltonian(q, a, primitive["adjustment"])
    replay = dict(
        rollout_variance_coarse=float(qc.var(0, ddof=1).mean()),
        rollout_variance_fine=float(qf.var(0, ddof=1).mean()),
        critic_costate_mse_to_fine_mean=float(((pred-ref)**2).mean()),
        critic_costate_mse_mc_debiased=float((((pred-ref)**2)-variance).mean()),
        raw_costate_mse_to_independent_fine_mean=float(((qc[0]-qf[1:].mean(0))**2).mean()),
        nested_costate_mean_change=float(((qc.mean(0)-ref)**2).mean()),
        fine_mean_mc_variance=float(variance.mean()),
        critic_value_mse_to_fine_mean=float(((value-vf.mean(0))**2).mean()),
    )
    for name in ["actor", "critic_greedy", "raw_greedy"]:
        key = "actor_action" if name == "actor" else name
        gaps = H(ref, arr["reference_greedy"]) - H(ref, arr[key])
        np.testing.assert_allclose(gaps, arr[name + "_gap"], rtol=1e-11, atol=2e-14)
        replay[name + "_hamiltonian_gap"] = float(gaps.mean())
    for k, v in replay.items():
        close(v, source[k], "source mechanism " + k)
    for input_q, key in [(ref, "reference_greedy"), (pred, "critic_greedy"), (qc[0], "raw_greedy")]:
        independent_action, _ = greedy(input_q, arr["states"][:, 0], primitive, epsilon)
        np.testing.assert_allclose(independent_action, arr[key], rtol=1e-12, atol=2e-13)

    # The raw action uses qc[0], coupled to qf[0].  Removing qf[0] makes
    # the Hamiltonian reference independent of that action and common to
    # the actor, critic-greedy action, and raw-greedy action.
    independent_ref = qf[1:].mean(0)
    independent_variance = qf[1:].var(0, ddof=1) / (n-1)
    optimum, residual = greedy(independent_ref, arr["states"][:, 0], primitive, epsilon)
    full_optimum, full_residual = greedy(independent_ref, arr["states"][:, 0], primitive, None)
    critic_mse = float(((pred-independent_ref)**2).mean())
    raw_mse = float(((qc[0]-independent_ref)**2).mean())
    delta = qc - qf
    paired_noise = delta.var(0, ddof=1) / n
    derived = dict(independent_fine_mean=independent_ref,
                   independent_fine_mean_variance=independent_variance,
                   reference_greedy=optimum, full_box_reference_greedy=full_optimum,
                   states=arr["states"], critic_q=pred, raw_q=qc[0],
                   actor_action=arr["actor_action"], critic_greedy=arr["critic_greedy"],
                   raw_greedy=arr["raw_greedy"],
                   nested_costate_mean_difference=delta.mean(0),
                   nested_costate_mean_variance=paired_noise)
    metrics = dict(
        original_metrics=replay,
        common_independent_reference_replicates=n-1,
        critic_costate_mse=critic_mse, raw_costate_mse=raw_mse,
        critic_to_raw_mse_ratio=critic_mse/raw_mse,
        fine_reference_mc_variance=float(independent_variance.mean()),
        critic_costate_mse_mc_debiased=critic_mse-float(independent_variance.mean()),
        raw_costate_mse_mc_debiased=raw_mse-float(independent_variance.mean()),
        nested_costate_squared_mean_change=float((delta.mean(0)**2).mean()),
        nested_costate_paired_mc_variance=float(paired_noise.mean()),
        nested_costate_squared_mean_change_mc_debiased=float(((delta.mean(0)**2)-paired_noise).mean()),
        critic_value_mse=float(((value-vf[1:].mean(0))**2).mean()),
        fine_value_reference_mc_variance=float((vf[1:].var(0, ddof=1)/(n-1)).mean()),
        nested_value_squared_mean_change=float(((vc-vf).mean(0)**2).mean()),
        nested_value_paired_mc_variance=float(((vc-vf).var(0, ddof=1)/n).mean()),
        tube_greedy_max_kkt_residual=residual,
        full_box_greedy_max_kkt_residual=full_residual,
    )
    for name in ["actor", "critic_greedy", "raw_greedy"]:
        action = arr["actor_action" if name == "actor" else name]
        gaps = H(independent_ref, optimum) - H(independent_ref, action)
        full_gaps = H(independent_ref, full_optimum) - H(independent_ref, action)
        require(float(gaps.min()) > -1e-12, "negative corrected optimum gap")
        derived[name + "_gap"] = gaps
        derived[name + "_full_box_gap"] = full_gaps
        metrics[name + "_hamiltonian_gap"] = float(gaps.mean())
        metrics[name + "_full_box_hamiltonian_gap"] = float(full_gaps.mean())
    advantage = H(independent_ref, arr["critic_greedy"]) - H(independent_ref, arr["raw_greedy"])
    derived["critic_minus_raw_hamiltonian"] = advantage
    metrics["critic_minus_raw_hamiltonian"] = float(advantage.mean())
    metrics["critic_mse_better_than_raw"] = critic_mse < raw_mse
    metrics["critic_hamiltonian_better_than_raw"] = float(advantage.mean()) > 0
    return metrics, derived


def run(args):
    repo = args.repo.resolve()
    base = args.results.resolve() if args.results else repo / REV13 / "results"
    out = args.out.resolve() if args.out else repo / REV14
    require(base != out and base not in out.parents, "derived output cannot be inside R13 evidence")
    (out / "manuscript").mkdir(parents=True, exist_ok=True)
    (out / "results").mkdir(parents=True, exist_ok=True)
    plan = json.loads((repo / REV13 / "PROTOCOL.json").read_text())
    protocol = json.loads((repo / REV12 / "PROTOCOL.json").read_text())
    require(plan["dimensions"] == [10, 20, 50] and plan["fixed_work_seeds"] == [7919, 15401]
            and plan["fixed_iterations"] == [20, 80]
            and plan["fixed_methods"] == ["nbo", "dpo", "linear", "raw"], "incompatible protocol schema")
    require(plan["final_noise_seed"] != protocol["final_noise_seed"], "extension reused primary final bank")
    source_checks, inputs, outputs, arrays, weights = {}, {}, {}, {}, {}
    for rel in SOURCES:
        pinned = subprocess.run(["git", "show", f"{SOURCE}:{rel}"], cwd=repo,
                                check=True, capture_output=True).stdout
        current = (repo / rel).read_bytes()
        require(current == pinned, "source differs from executed source: " + rel)
        source_checks[rel] = dict(sha256=sha(current), source_commit=SOURCE, matches_pinned_source=True)
        inputs[rel] = sha(current)
    kernel = pure_kernel(repo)
    proto_hash = digest(repo / REV13 / "PROTOCOL.json")
    methods, iterations = plan["fixed_methods"], plan["fixed_iterations"]
    cells = [("ubuntu24", d, s) for d in plan["dimensions"] for s in plan["fixed_work_seeds"]]
    second = plan["second_environment"]
    cells += [("ubuntu22", second["dimension"], second["seed"])]
    names = {f"{env}_d{d}_s{s}" for env, d, s in cells}
    require({p.name for p in base.iterdir() if p.is_dir()} == names, "missing or extra extension cells")
    accounts = {}
    policy_rows, pair_rows, mechanism_rows, environments, frontier, target_rows = [], [], [], [], [], []
    by_cell = {}

    def logical(path):
        return str(REV13 / "results" / path.relative_to(base))

    def read(path):
        require(path.is_file(), "missing record: " + str(path))
        inputs[logical(path)] = digest(path)
        value = json.loads(path.read_text())
        require(value["source_commit"] == SOURCE, "mixed source record: " + str(path))
        return value

    def raw(path, expected):
        require(digest(path) == expected, "raw array digest mismatch: " + str(path))
        inputs[logical(path)] = expected
        with np.load(path, allow_pickle=False) as archive:
            arr = {key: archive[key] for key in archive.files}
        require(all(np.isfinite(a).all() for a in arr.values()), "nonfinite raw arrays")
        arrays[logical(path)] = {key: dict(shape=list(a.shape), dtype=str(a.dtype), sha256=sha(a.tobytes()))
                                 for key, a in arr.items()}
        return arr

    def weight(path, expected):
        rel = logical(path)
        if rel not in weights:
            require(digest(path) == expected, "weight digest mismatch: " + rel)
            info, _ = weight_storage(path)
            weights[rel] = dict(sha256=expected, **info)
            inputs[rel] = expected
        else:
            require(weights[rel]["sha256"] == expected, "conflicting weight identity")

    for env, d, seed in cells:
        name = f"{env}_d{d}_s{seed}"
        folder = base / name
        print("Audit extension cell", name, flush=True)
        envrow, ledger = read(folder / "ENVIRONMENT.json"), read(folder / "FIXED_WORK.json")
        for row in [envrow, ledger]:
            require((row["environment"], row["dimension"], row["seed"]) == (env, d, seed), "wrong cell identity")
            require(row["protocol_sha256"] == proto_hash, "protocol hash mismatch")
        require(envrow["primary_source_commit"] == plan["primary_source_commit"], "wrong primary source")
        require(envrow["threads"] == 1, "unexpected thread count")
        require(ledger["complete"] is True, "incomplete execution ledger")
        require(ledger["ledger"] == [{"task": method, "completed": True} for method in methods], "failed or reordered tasks")
        require(len(ledger["fits"]) == 4 and len(ledger["diagnostics"]) == 1, "missing fit or diagnostic")
        require(not (folder / "FAILURES.json").exists(), "failure ledger exists")
        environments.append(envrow)
        record = by_cell[name] = dict(fits={}, evaluations={}, pairs={}, folder=folder)
        expected_json = {"ENVIRONMENT.json", "FIXED_WORK.json"}
        expected_npz, expected_pt = set(), set()
        if d not in accounts:
            accounts[d] = account(kernel, d, plan, protocol)
        con = accounts[d]
        for method_index, method in enumerate(methods):
            loader = "nbo" if method == "raw" else method
            ident = f"{loader}_d{d}_s{seed}_fixed_{method}"
            fit = read(folder / (ident + ".json"))
            expected_json.add(ident + ".json")
            require(fit == ledger["fits"][method_index], "summary fit disagrees with source record")
            require(fit["failure"] is None and fit["completed_iterations"] == max(iterations), "fit did not complete")
            require((fit["method"], fit["dimension"], fit["seed"], fit["tag"]) == (loader, d, seed, "_fixed_" + method), "wrong fit identity")
            require(fit["costate_mode"] == ("raw" if method == "raw" else "critic"), "wrong costate mode")
            for key in ["epsilon", "width", "value_weight", "costate_weight"]:
                require(fit[key] == protocol[key], "undeclared fitting setting: " + key)
            expected_history = list(range(protocol["checkpoint_every"], max(iterations)+1, protocol["checkpoint_every"]))
            require([h["iteration"] for h in fit["history"]] == expected_history, "checkpoint sequence incomplete")
            require(fit["selected_iteration"] == max(fit["history"], key=lambda h: h["validation_return"])["iteration"], "validation selection mismatch")
            previous_time = 0
            for h in fit["history"]:
                k = h["iteration"]
                require(h["training_state_visits"] == k*protocol["batch"]*protocol["rollout_steps"], "training visits mismatch")
                require(h["validation_state_visits"] == k//protocol["checkpoint_every"]*protocol["validation_paths"]*protocol["validation_steps"], "validation visits mismatch")
                require(h["actor_updates"] == k*(protocol["actor_updates"] if method in ["nbo", "raw"] else 1), "actor update count mismatch")
                require(h["critic_updates"] == (k*protocol["critic_updates"] if method == "nbo" else 0), "critic update count mismatch")
                require(h["seconds"] > previous_time, "non-increasing fitting clock")
                previous_time = h["seconds"]
                fname = ident + f"_k{k}.pt"
                weight(folder / fname, h["weights_sha256"])
                expected_pt.add(fname)
            for key in ["training_state_visits", "validation_state_visits", "actor_updates", "critic_updates"]:
                require(fit[key] == fit["history"][-1][key], "final work ledger mismatch")
            require(fit["seconds"] >= previous_time, "final fit clock precedes checkpoint")
            weight(folder / (ident + ".pt"), fit["weights_sha256"])
            expected_pt.add(ident + ".pt")
            selected_sig = weights[logical(folder / (ident + ".pt"))]
            checkpoint_sig = weights[logical(folder / (ident + f"_k{fit['selected_iteration']}.pt"))]
            require(selected_sig["metadata_sha256"] == checkpoint_sig["metadata_sha256"] and
                    selected_sig["storage_sha256"] == checkpoint_sig["storage_sha256"], "selected model differs from selected checkpoint")
            record["fits"][method] = fit
            cumulative_verify = 0.0
            for index, k in enumerate(iterations, 1):
                eid = ident + f"_k{k}_population_n{plan['final_steps']}"
                path = folder / (eid + ".json")
                evaluation = read(path)
                expected_json.add(eid + ".json")
                expected_npz.add(eid + ".npz")
                require(evaluation["extension_method"] == method and evaluation["training_seed"] == seed, "wrong evaluation method/seed")
                require((evaluation["dimension"], evaluation["iteration"], evaluation["method"], evaluation["design"], evaluation["steps"], evaluation["paths"]) ==
                        (d, k, loader, "population", plan["final_steps"], plan["final_paths"]), "undeclared evaluation cell")
                require(evaluation["weights"] == logical(folder / f"{ident}_k{k}.pt"), "wrong evaluation weight path")
                weight(folder / f"{ident}_k{k}.pt", evaluation["weights_sha256"])
                a = raw(path.with_suffix(".npz"), evaluation["raw_sha256"])
                n = plan["final_paths"]
                for key in ["paired_gain", "production", "consumption_deficit", "terminal_gain", "initial_profile"]:
                    require(a[key].shape == (n,), "wrong policy array shape: " + key)
                for key in ["terminal_policy", "terminal_anchor"]:
                    require(a[key].shape == (n, d), "wrong state-array shape")
                np.testing.assert_array_equal(a["production"]-a["consumption_deficit"]+a["terminal_gain"], a["paired_gain"])
                ids = np.random.default_rng(plan["final_noise_seed"]+100003+d).integers(0, len(con["initial_profiles"]), size=n)
                np.testing.assert_array_equal(ids, a["initial_profile"])
                require(sha(ids.tobytes()) == evaluation["initial_index_hash"], "initial index hash mismatch")
                require(sha(con["initial_profiles"][ids].tobytes()) == evaluation["initial_state_hash"], "initial state hash mismatch")
                require(evaluation["noise_seed"] == plan["final_noise_seed"] + d, "wrong final noise seed")
                np.testing.assert_array_equal(con["initial_profiles"], evaluation["constants"]["initial_profiles"])
                for key in ["bias_upper", "actor_bias_upper", "statistic_error_upper", "clipping_threshold", "clipping_bias", "anchor_upper", "state_cap"]:
                    close(con[key], evaluation["constants"][key], "independent interval account " + key)
                bound = kernel.empirical_lower(a["paired_gain"], con["clipping_threshold"], con["bias_upper"], con["clipping_bias"], plan["one_sided_family_size"], plan["alpha"])
                for key in ["mean", "sample_sd", "empirical_bernstein_margin", "lower", "upper"]:
                    close(bound[key], evaluation["bound"][key], "policy endpoint " + key)
                for key in ["paths", "family_size", "alpha", "clipped_payoffs"]:
                    require(bound[key] == evaluation["bound"][key], "bound allocation mismatch")
                require(evaluation["nonfinite_proposals"] == 0 and evaluation["max_internal_state"] <= con["state_cap"], "numerical state violation")
                h = next(h for h in fit["history"] if h["iteration"] == k)
                cumulative_verify += evaluation["seconds"]
                transitions = 2*index*plan["final_steps"]*plan["final_paths"]
                point = dict(environment=env, dimension=d, seed=seed, method=method, iteration=k,
                             evaluation=eid, mean=bound["mean"], lower=bound["lower"], upper=bound["upper"],
                             training_state_visits=h["training_state_visits"], validation_state_visits=h["validation_state_visits"],
                             actor_updates=h["actor_updates"], critic_updates=h["critic_updates"],
                             prefix_fit_seconds=h["seconds"], completed_fit_seconds=fit["seconds"],
                             verification_calls_paid=index, verification_seconds=evaluation["seconds"],
                             cumulative_verification_seconds=cumulative_verify,
                             retrospective_prefix_accounted_seconds=h["seconds"]+cumulative_verify,
                             executed_method_accounted_seconds=fit["seconds"]+cumulative_verify,
                             cumulative_verification_pair_time_cells=index*plan["final_steps"]*plan["final_paths"],
                             cumulative_verification_state_transitions=transitions,
                             retrospective_prefix_state_transitions=h["training_state_visits"]+h["validation_state_visits"]+transitions,
                             executed_method_state_transitions=fit["training_state_visits"]+fit["validation_state_visits"]+transitions)
                point["retrospective_prefix_coordinate_transitions"] = d*point["retrospective_prefix_state_transitions"]
                point["executed_method_coordinate_transitions"] = d*point["executed_method_state_transitions"]
                frontier.append(point)
                policy_rows.append(point)
                record["evaluations"][(method, k)] = dict(json=evaluation, arrays=a, point=point)
            for target in plan["certified_improvement_targets"]:
                candidates = [record["evaluations"][(method, k)]["point"] for k in iterations]
                qualifying = [p for p in candidates if p["lower"] > target]
                row = dict(environment=env, dimension=d, seed=seed, method=method, target=target,
                           criterion="simultaneous_lower_endpoint > target", attained=bool(qualifying),
                           tested_iterations=iterations)
                if qualifying:
                    q = min(qualifying, key=lambda x: x["executed_method_accounted_seconds"])
                    row.update({key: q[key] for key in ["iteration", "lower", "verification_calls_paid",
                                "cumulative_verification_seconds", "retrospective_prefix_accounted_seconds",
                                "executed_method_accounted_seconds", "retrospective_prefix_state_transitions",
                                "executed_method_state_transitions", "actor_updates", "critic_updates"]})
                target_rows.append(row)

        require(set(ledger["evaluations"]) == {r["json"]["id"] for r in record["evaluations"].values()}, "evaluation ledger incomplete")
        for k in iterations:
            for other in ["dpo", "linear", "raw"]:
                ident = f"paired_d{d}_s{seed}_k{k}_nbo_{other}"
                path = folder / (ident + ".json")
                pair = read(path)
                expected_json.add(ident + ".json")
                expected_npz.add(ident + ".npz")
                left, right = record["evaluations"][("nbo", k)], record["evaluations"][(other, k)]
                for key in ["dimension", "design", "steps", "paths", "initial_state_hash", "initial_index_hash", "noise_seed", "noise_sha256"]:
                    require(left["json"][key] == right["json"][key], "unpaired records: " + key)
                for side, item in [("left", left), ("right", right)]:
                    require(pair[side] == logical(folder / (item["json"]["id"] + ".json")), "paired input path")
                    require(pair[side+"_raw_sha256"] == item["json"]["raw_sha256"], "paired input array hash")
                require(pair["shared_noise_sha256"] == left["json"]["noise_sha256"] and pair["anchor_transfer_cancelled"] is True, "paired account identity")
                np.testing.assert_array_equal(left["arrays"]["terminal_anchor"], right["arrays"]["terminal_anchor"])
                paired = raw(path.with_suffix(".npz"), pair["raw_sha256"])
                require(set(paired) == {"paired_difference"}, "unexpected paired array members")
                np.testing.assert_array_equal(paired["paired_difference"], left["arrays"]["paired_gain"]-right["arrays"]["paired_gain"])
                I = kernel.I
                bias = float((I(con["actor_bias_upper"])+I(con["actor_bias_upper"])+I(con["statistic_error_upper"])+I(con["statistic_error_upper"])+I(1e-12)).hi)
                clip = float((I(con["clipping_threshold"])+I(con["clipping_threshold"])).hi)
                tail = float((I(con["clipping_bias"])+I(con["clipping_bias"])).hi)
                for a, b in [(bias, pair["bias_upper"]), (clip, pair["clipping_threshold"]), (tail, pair["clipping_bias"])]:
                    close(a, b, "paired transfer account")
                bound = kernel.empirical_lower(paired["paired_difference"], clip, bias, tail, plan["one_sided_family_size"], plan["alpha"])
                for key in ["mean", "sample_sd", "empirical_bernstein_margin", "lower", "upper"]:
                    close(bound[key], pair["bound"][key], "paired endpoint " + key)
                row = dict(environment=env, dimension=d, seed=seed, iteration=k, comparator=other,
                           mean=bound["mean"], lower=bound["lower"], upper=bound["upper"],
                           status="positive" if bound["lower"] > 0 else "negative" if bound["upper"] < 0 else "inconclusive")
                pair_rows.append(row)
                record["pairs"][(k, other)] = row
        require(set(ledger["comparisons"]) == {f"paired_d{d}_s{seed}_k{k}_nbo_{o}" for k in iterations for o in ["dpo", "linear", "raw"]}, "comparison ledger incomplete")
        mid = f"nbo_d{d}_s{seed}_fixed_nbo_k{max(iterations)}_mechanism"
        source = read(folder / (mid + ".json"))
        require(source == ledger["diagnostics"][0], "mechanism summary disagrees with record")
        expected_json.add(mid + ".json")
        expected_npz.add(mid + ".npz")
        require(source["states"] == plan["mechanism_states"] and source["replicates"] == plan["mechanism_replicates"]
                and source["grids"] == plan["mechanism_steps"], "wrong mechanism design")
        source_path = folder / f"nbo_d{d}_s{seed}_fixed_nbo_k{max(iterations)}.pt"
        require(source["weights"] == logical(source_path), "mechanism weight path mismatch")
        weight(source_path, source["weights_sha256"])
        a = raw(folder / (mid + ".npz"), source["raw_sha256"])
        require(a["q_fine"].shape == a["q_coarse"].shape == (plan["mechanism_replicates"], plan["mechanism_states"], d), "wrong mechanism shape")
        metrics, derived = mechanism_metrics(a, source, kernel.P, protocol["epsilon"])
        derived_dir = out / "results" / "mechanism_independent"
        derived_dir.mkdir(exist_ok=True)
        derived_path = derived_dir / (name + ".npz")
        np.savez_compressed(derived_path, **derived)
        metadata = dict(environment=env, dimension=d, seed=seed, source_commit=SOURCE,
                        source_record=logical(folder / (mid+".json")),
                        source_record_sha256=digest(folder / (mid+".json")), source_raw_sha256=source["raw_sha256"],
                        derived_raw_sha256=digest(derived_path), metrics=metrics,
                        paired_nbo_minus_raw_at_80=record["pairs"][(max(iterations), "raw")],
                        reference="mean(q_fine[1:]); excludes q_fine[0], which is nested with raw q_coarse[0]",
                        scope="R14 postprocessing of unchanged R13 arrays; common independent 15-replicate Euler reference; no continuous-time costate certificate, inferential interval, or new economic sampling endpoint")
        save(derived_path.with_suffix(".json"), metadata)
        mechanism_rows.append(metadata)
        record["mechanism"] = dict(json=source, arrays=a, corrected=metadata)
        outputs[str(REV14 / derived_path.relative_to(out))] = digest(derived_path)
        outputs[str(REV14 / derived_path.with_suffix(".json").relative_to(out))] = digest(derived_path.with_suffix(".json"))
        require({p.name for p in folder.glob("*.json")} == expected_json, "missing or extra JSON records in " + name)
        require({p.name for p in folder.glob("*.npz")} == expected_npz, "missing or extra arrays in " + name)
        require({p.name for p in folder.glob("*.pt")} == expected_pt, "missing or extra weights in " + name)

    # Repeated environment is not an extra economic/optimization seed.
    environment_comparison = []
    d, seed = second["dimension"], second["seed"]
    left, right = by_cell[f"ubuntu24_d{d}_s{seed}"], by_cell[f"ubuntu22_d{d}_s{seed}"]
    for method in methods:
        for k in iterations:
            a, b = left["evaluations"][(method, k)], right["evaluations"][(method, k)]
            for key in ["noise_seed", "initial_index_hash", "initial_state_hash"]:
                require(a["json"][key] == b["json"][key], "environment inputs differ")
            p1, p2 = base / Path(a["json"]["weights"]).relative_to(REV13/"results"), base / Path(b["json"]["weights"]).relative_to(REV13/"results")
            sig1, vals1 = weight_storage(p1)
            sig2, vals2 = weight_storage(p2)
            require(sig1["metadata_sha256"] == sig2["metadata_sha256"] and sig1["storage_bytes"] == sig2["storage_bytes"], "environment tensor layout differs")
            maxweight = max(float(np.max(abs(np.frombuffer(x, dtype="<f8")-np.frombuffer(y, dtype="<f8")))) for x,y in zip(vals1, vals2))
            row = dict(method=method, iteration=k,
                       noise_seed=a["json"]["noise_seed"],
                       ubuntu24_noise_sha256=a["json"]["noise_sha256"],
                       ubuntu22_noise_sha256=b["json"]["noise_sha256"],
                       noise_sha256_equal=a["json"]["noise_sha256"]==b["json"]["noise_sha256"],
                       weight_archive_sha256_equal=digest(p1)==digest(p2),
                       tensor_storage_bitwise_equal=sig1["storage_sha256"]==sig2["storage_sha256"],
                       maximum_tensor_storage_absolute_difference=maxweight,
                       maximum_paired_gain_absolute_difference=float(abs(a["arrays"]["paired_gain"]-b["arrays"]["paired_gain"]).max()),
                       maximum_terminal_anchor_absolute_difference=float(abs(a["arrays"]["terminal_anchor"]-b["arrays"]["terminal_anchor"]).max()),
                       mean_absolute_difference=abs(a["point"]["mean"]-b["point"]["mean"]),
                       lower_absolute_difference=abs(a["point"]["lower"]-b["point"]["lower"]),
                       upper_absolute_difference=abs(a["point"]["upper"]-b["point"]["upper"]),
                       ubuntu24_prefix_fit_seconds=a["point"]["prefix_fit_seconds"],
                       ubuntu22_prefix_fit_seconds=b["point"]["prefix_fit_seconds"],
                       ubuntu24_verification_seconds=a["point"]["verification_seconds"],
                       ubuntu22_verification_seconds=b["point"]["verification_seconds"])
            row["verification_seconds_ratio_22_over_24"] = row["ubuntu22_verification_seconds"]/row["ubuntu24_verification_seconds"]
            environment_comparison.append(row)

    primary_policy = [r for r in policy_rows if r["environment"] == "ubuntu24"]
    primary_pairs = [r for r in pair_rows if r["environment"] == "ubuntu24"]
    primary_mechanism = [r for r in mechanism_rows if r["environment"] == "ubuntu24"]
    require(len(policy_rows) == 56 and len(pair_rows) == 42 and len(mechanism_rows) == 7, "incomplete extension")
    one_sided = 2*(len(policy_rows)+len(pair_rows))
    require(one_sided <= plan["family_allocation"]["extension_reserved"], "extension allocation exceeded")
    primary_audit_path = args.primary_audit or repo/REV14/"results/AUDIT.json"
    if args.primary_audit is None and not primary_audit_path.exists():
        primary_audit_path = repo/REV12/"results/AUDIT.json"
    primary_used = None
    if primary_audit_path.exists():
        audit = json.loads(primary_audit_path.read_text())
        require(audit["source_commit"] == plan["primary_source_commit"] and audit["development"] is False, "wrong primary audit")
        primary_used = audit["one_sided_used"]
        require(primary_used <= plan["family_allocation"]["primary_reserved"], "primary reserved allocation exceeded")
        require(primary_used+one_sided <= plan["one_sided_family_size"], "union allocation exceeded")
        primary_audit_logical = (str(primary_audit_path.resolve().relative_to(repo))
                                 if repo in primary_audit_path.resolve().parents
                                 else str(primary_audit_path.resolve()))
        inputs[primary_audit_logical] = digest(primary_audit_path)

    summary = dict(
        primary_fixed_work_cells=6, second_environment_cells=1,
        source_fits=28, policy_evaluations=56, paired_comparisons=42, mechanism_panels=7,
        positive_nbo_policies=sum(r["lower"]>0 for r in primary_policy if r["method"]=="nbo"),
        nbo_policy_count=sum(r["method"]=="nbo" for r in primary_policy),
        pair_signs={o: {status: sum(r["comparator"]==o and r["status"]==status for r in primary_pairs)
                        for status in ["positive", "negative", "inconclusive"]} for o in ["dpo", "linear", "raw"]},
        critic_mse_better_count=sum(r["metrics"]["critic_mse_better_than_raw"] for r in primary_mechanism),
        critic_hamiltonian_better_count=sum(r["metrics"]["critic_hamiltonian_better_than_raw"] for r in primary_mechanism),
        critic_to_raw_mse_ratio_range=[min(r["metrics"]["critic_to_raw_mse_ratio"] for r in primary_mechanism), max(r["metrics"]["critic_to_raw_mse_ratio"] for r in primary_mechanism)],
        primary_targets={str(t): {m: sum(r["environment"]=="ubuntu24" and r["method"]==m and r["target"]==t and r["attained"] for r in target_rows) for m in methods} for t in plan["certified_improvement_targets"]},
        maximum_second_environment_gain_difference=max(r["maximum_paired_gain_absolute_difference"] for r in environment_comparison),
        second_environment_noise_hashes_match=all(r["noise_sha256_equal"] for r in environment_comparison),
        second_environment_verification_time_ratio_range=[min(r["verification_seconds_ratio_22_over_24"] for r in environment_comparison),max(r["verification_seconds_ratio_22_over_24"] for r in environment_comparison)],
    )
    scopes = dict(
        fixed_work="At k=20 and k=80 all methods use equal training and validation vector-state visits; actor/critic optimizer steps, derivative work, dimension-dependent arithmetic and memory are not equated.",
        work_units="One vector-state transition is one simulated state update. Each final verification updates both actor and anchor states: 2*8192*1024 transitions. Coordinate counts multiply by d; these are not floating-point-operation counts.",
        target_frontier="Strict lower>target among two preregistered checkpoints only. Previously attempted full verifications are charged. A failure to attain a target means neither tested checkpoint certifies it, not impossibility at other work budgets.",
        actual_execution="Every method completed 80 iterations before either checkpoint was verified. Executed method accounting charges all 80 iterations even if k=20 attains the target. The checkpoint-prefix account is retrospective and is not an observed early-stop wall time.",
        timing="Saved evaluation seconds exclude model loading, analytical interval-account construction, and final JSON serialization; saved fit seconds exclude final selected-weight serialization. Summed recorded clocks are accounted components, not complete end-to-end elapsed time. Cross-method fits, mechanism diagnostics, pair postprocessing, environment setup and scheduling are excluded.",
        mechanism="The common independent fine reference averages replicates 1..15 and excludes the fine replicate coupled to raw replicate 0. MSE debiasing subtracts estimated reference Monte Carlo variance without truncation. Paired nested 32/128 differences expose discretization sensitivity without certifying continuous-time bias.",
        mechanism_design="Six fixed NBO k=80 policies, 64 held-out states and 16 nested rollout replicates per policy. State/noise seeds depend on dimension, so the two fitted seeds share diagnostic designs. Mechanism states are not discounted policy occupancy samples. A diagnostic raw greedy step for a frozen NBO policy differs from the independently trained raw-costate comparator.",
        mechanism_inference="Only descriptive saved-array diagnostics are reported; no causal chain, confidence interval for costate error, continuous-time reference, or universal critic advantage follows.",
        second_environment="One repeated d=10, seed=7919 cell with identical final initial-state banks and the same nominal innovation seed. The recorded innovation byte hashes differ across operating systems, although hashes agree within each paired method comparison. It is an implementation repeat, not an independent economic sample; OS and hardware/runtime variation are jointly observed rather than separately randomized.",
    )

    tab(out, "table_extension_fixed_work.tex", "Fixed-iteration and simulator-visit extension", "tab:r14fixed", "rrlrrrr",
        ["$d$", "$k$", "Method", "Mean", "Min. lower", "Positive", "Fit sec."],
        [[d,k,NAMES[m],fmt(np.mean([r["mean"] for r in primary_policy if r["dimension"]==d and r["iteration"]==k and r["method"]==m])),
          fmt(min(r["lower"] for r in primary_policy if r["dimension"]==d and r["iteration"]==k and r["method"]==m),"lo"),
          str(sum(r["lower"]>0 for r in primary_policy if r["dimension"]==d and r["iteration"]==k and r["method"]==m))+"/2",
          fmt(np.median([r["prefix_fit_seconds"] for r in primary_policy if r["dimension"]==d and r["iteration"]==k and r["method"]==m]),digits=2)]
         for d in plan["dimensions"] for k in iterations for m in methods],
        "Ubuntu 24.04; both fixed training seeds are retained. Each method uses 81,920 training and 8,192 validation state visits at 20 iterations, and 327,680 plus 32,768 at 80. NBO and Raw use five actor updates per iteration; DPO and Affine use one. NBO additionally uses five critic updates. Fit seconds are checkpoint-prefix clocks. Means are numerical paired statistics; lower endpoints include the stated continuous-time transfer and sampling account.")
    tab(out, "table_extension_paired.tex", "Every fixed-work NBO-minus-comparator endpoint", "tab:r14pairs", "lrrrlrrr",
        ["OS", "$d$", "Seed", "$k$", "Comparator", "Mean", "Lower", "Upper"],
        [["22" if r["environment"]=="ubuntu22" else "24",r["dimension"],r["seed"],r["iteration"],NAMES[r["comparator"]],fmt(r["mean"]),fmt(r["lower"],"lo"),fmt(r["upper"],"hi")] for r in pair_rows],
        "All 36 Ubuntu 24.04 and six repeated Ubuntu 22.04 direct comparisons. Endpoints are reconstructed from common-path differences within each environment; neither differences of separate lower endpoints nor counts of training seeds constitute a method-population inference.")
    tab(out, "table_extension_work_targets.tex", "Accounted work to each declared certified-gain target", "tab:r14targets", "lrrlrrrrr",
        ["OS","$d$","Seed","Method","Target","$k$","Prefix sec.","Executed sec.","Calls"],
        [["22" if r["environment"]=="ubuntu22" else "24",r["dimension"],r["seed"],NAMES[r["method"]],fmt(r["target"],digits=4),r.get("iteration","--"),
          fmt(r["retrospective_prefix_accounted_seconds"],digits=2) if r["attained"] else "--",
          fmt(r["executed_method_accounted_seconds"],digits=2) if r["attained"] else "--",r.get("verification_calls_paid","--")]
         for r in target_rows],
        "A target is attained when the simultaneous lower endpoint strictly exceeds it. Every earlier verification is charged, including the 20-iteration verification when the first qualifying checkpoint is 80. Prefix seconds add the checkpoint fitting clock to cumulative saved verification clocks. Executed seconds charge the full 80-iteration fit, which precedes both evaluations in the executed program. These recorded components exclude interval-account construction and other untimed overhead. A dash means neither declared checkpoint attained that target.")
    target_summary = []
    for d in plan["dimensions"]:
        for method in methods:
            entry = [d, NAMES[method]]
            for target in plan["certified_improvement_targets"]:
                hits = [r for r in target_rows if r["environment"]=="ubuntu24" and r["dimension"]==d
                        and r["method"]==method and r["target"]==target and r["attained"]]
                entry.append(f"{len(hits)}/2")
                entry.append((fmt(min(r["executed_method_accounted_seconds"] for r in hits),digits=1)
                              + "--" + fmt(max(r["executed_method_accounted_seconds"] for r in hits),digits=1)) if hits else "--")
            target_summary.append(entry)
    tab(out, "table_extension_targets_summary.tex", "Certified targets and accounted work", "tab:r14targetsummary", "rlrrrrrr",
        ["$d$","Method","$g=0$","Sec.","$g=.0005$","Sec.","$g=.001$","Sec."], target_summary,
        "Each count is the number of the two fixed seeds whose 20- or 80-iteration checkpoint has a lower endpoint strictly above the target. Seconds give the range of minimum executed method-accounted work among attaining seeds, charging the full 80-iteration fit and every verification through the first qualifying checkpoint. A dash means no tested checkpoint attained the target. These are recorded computational components, not complete end-to-end wall clocks; Table~\\ref{tab:r14targets} also gives retrospective checkpoint-prefix accounts and every failure to attain a target.")
    tab(out, "table_extension_policy_all.tex", "All extension policy endpoints and verification work", "tab:r14policyall", "lrrlrrrrr",
        ["OS","$d$","Seed","Method","$k$","Mean","Lower","Upper","Verify sec."],
        [["22" if r["environment"]=="ubuntu22" else "24",r["dimension"],r["seed"],NAMES[r["method"]],r["iteration"],fmt(r["mean"]),fmt(r["lower"],"lo"),fmt(r["upper"],"hi"),fmt(r["verification_seconds"],digits=2)] for r in policy_rows],
        "All 56 full-bank policy rows are retained. Each verification has 8,192 paired paths and 1,024 time cells, hence 16,777,216 actor-plus-anchor state transitions. The saved verification clock excludes model loading and interval-account construction. OS denotes Ubuntu 22.04 or 24.04; the repeated environment does not add an independent fitted-seed observation.")
    tab(out, "table_extension_mechanism_costate.tex", "Held-out costate errors on a common independent reference", "tab:r14costates", "rrrrrrr",
        ["$d$","Seed","Critic MSE","Raw MSE","Reference var.","Nested change","Nested var."],
        [[r["dimension"],r["seed"],fmt(r["metrics"]["critic_costate_mse"]*1e5,digits=3),fmt(r["metrics"]["raw_costate_mse"]*1e5,digits=3),fmt(r["metrics"]["fine_reference_mc_variance"]*1e5,digits=3),fmt(r["metrics"]["nested_costate_squared_mean_change"]*1e5,digits=3),fmt(r["metrics"]["nested_costate_paired_mc_variance"]*1e5,digits=6)] for r in primary_mechanism],
        "All displayed entries are multiplied by $10^5$. Costates are scaled as $dD_yV$. Both critic and raw MSE use the same mean of 15 independent 128-step rollouts, excluding the replicate coupled to the raw 32-step sample. Reference variance is the estimated variance of that mean. Nested change is the mean squared difference between the 16-replicate coarse and fine means; nested variance uses paired replicate differences. These are held-out Euler diagnostics; subtracting the corresponding Monte Carlo variance gives the signed debiased diagnostic saved in the audit, not a continuous-time bias certificate.")
    tab(out, "table_extension_mechanism_hamiltonian.tex", "Independent-reference Hamiltonian gaps and the raw-policy contrast", "tab:r14hamiltonian", "rrrrrrrr",
        ["$d$","Seed","Actor gap","Critic gap","Raw gap","Payoff mean","Lower","Upper"],
        [[r["dimension"],r["seed"],fmt(r["metrics"]["actor_hamiltonian_gap"]*1e5,digits=3),fmt(r["metrics"]["critic_greedy_hamiltonian_gap"]*1e5,digits=3),fmt(r["metrics"]["raw_greedy_hamiltonian_gap"]*1e5,digits=3),fmt(r["paired_nbo_minus_raw_at_80"]["mean"]*1e5,digits=3),fmt(r["paired_nbo_minus_raw_at_80"]["lower"]*1e5,"lo",3),fmt(r["paired_nbo_minus_raw_at_80"]["upper"]*1e5,"hi",3)] for r in primary_mechanism],
        "All displayed entries are multiplied by $10^5$. Gaps evaluate the original actor, critic-greedy action, and raw-greedy action against an independently solved tube optimum using the common 15-replicate fine-costate mean. The final three columns are separate certified NBO-minus-Raw policy comparisons at 80 iterations. The Raw policy is trained independently of the frozen NBO-policy diagnostic. These columns therefore display distinct links in the proposed mechanism, without a causal or occupancy-weighted identification claim.")
    tab(out, "table_extension_environment.tex", "Repeated environment: economic reproducibility and clock variation", "tab:r14environment", "lrrrrrr",
        ["Method","$k$","Max. gain diff.","Fit 24","Fit 22","Verify 24","Verify 22"],
        [[NAMES[r["method"]],r["iteration"],f"{r['maximum_paired_gain_absolute_difference']:.2e}",fmt(r["ubuntu24_prefix_fit_seconds"],digits=2),fmt(r["ubuntu22_prefix_fit_seconds"],digits=2),fmt(r["ubuntu24_verification_seconds"],digits=2),fmt(r["ubuntu22_verification_seconds"],digits=2)] for r in environment_comparison],
        "Dimension 10, training seed 7919, identical final initial states and the same nominal innovation seed. Recorded innovation byte hashes differ between operating systems, so the realized innovation arrays are not asserted to be bitwise identical. Maximum differences are over individual paired-gain samples. Clocks are seconds for the recorded components and depend on the complete software and hardware environment. Both environments and tensor-storage differences are retained in the audit; this one-cell repeat is not a second economic inference sample.")
    statement = (
        f"The executed fixed-work extension retains 28 fits, 56 full-bank policy evaluations, "
        f"42 direct policy contrasts, and seven held-out mechanism panels. Six cells use Ubuntu 24.04 "
        f"and one repeats dimension 10 and seed 7919 under Ubuntu 22.04. Among the twelve Ubuntu 24.04 "
        f"NBO checkpoints, {summary['positive_nbo_policies']} have positive simultaneous lower improvement endpoints. "
        f"The direct NBO-minus-DPO comparisons have {summary['pair_signs']['dpo']['positive']} positive, "
        f"{summary['pair_signs']['dpo']['negative']} negative, and {summary['pair_signs']['dpo']['inconclusive']} inconclusive intervals. "
        f"On the common independent costate reference, the critic has a smaller MSE than the raw target "
        f"in {summary['critic_mse_better_count']} of six panels and a smaller greedy Hamiltonian gap "
        f"in {summary['critic_hamiltonian_better_count']} of six. "
        "Thus the completed record distinguishes verified policy improvement from an empirical advantage "
        "attributable to fitting a critic. The projection identity and conditional improvement bound "
        "supply an error decomposition; they do not convert these fitted-network diagnostics into "
        "a demonstrated variance-reduction or causal payoff mechanism.\n")
    (out/"manuscript/extension_summary.tex").write_text(statement)
    explanation = (
        "The work frontier uses only the preregistered 20- and 80-iteration checkpoints and the stated "
        "gain targets. A checkpoint at 20 entails 90,112 fitting and validation state transitions; "
        "the corresponding figure at 80 is 360,448. Each full verification adds 16,777,216 actor-plus-anchor "
        "state transitions. The retrospective prefix totals are therefore 16,867,328 and 33,914,880 "
        "when one and two verification calls have been paid. In the executed program every fit reaches "
        "80 before either verification, so the executed total at the first check is 17,137,664. "
        "These counts expose certification work without treating vector-state visits as equal "
        "floating-point work or the stored partial clocks as complete elapsed time.\n\n"
        "For the mechanism diagnostic, the saved raw action uses the first coarse rollout. The original "
        "16-replicate fine reference contains the nested partner of that rollout. The R14 postprocessing "
        "therefore removes the first fine replicate and evaluates all three original actions against "
        "the same independent 15-replicate mean. A scalar root solve of the strictly concave Hamiltonian "
        "provides the reference optimizer independently of the critic. The audit also retains the original "
        "metrics, the Monte Carlo variance of the fine mean, the paired 32/128-step mean change and its "
        "Monte Carlo variance, and full-box reference gaps. A finite nested-grid change measures "
        "discretization sensitivity; it is not an upper bound on continuous-time costate bias.\n")
    (out/"manuscript/extension_interpretation.tex").write_text(explanation)
    main_tables = ["table_extension_fixed_work.tex", "table_extension_targets_summary.tex",
                   "table_extension_mechanism_costate.tex", "table_extension_mechanism_hamiltonian.tex"]
    supplement_tables = ["table_extension_policy_all.tex", "table_extension_paired.tex",
                         "table_extension_work_targets.tex", "table_extension_environment.tex"]
    for filename, selected in [("extension_main_tables.tex", main_tables),
                               ("extension_supplement.tex", supplement_tables)]:
        (out/"manuscript"/filename).write_text("\n".join("\\input{"+str(REV14/"manuscript"/name)+"}" for name in selected)+"\n")

    report = dict(schema="r14-derived-audit-of-c8299feb-r13-extension-v1", source_commit=SOURCE,
                  source_workflow_run=RUN, protocol_sha256=proto_hash,
                  reporting_script_sha256=digest(Path(__file__)), complete=True,
                  source_checks=source_checks, summary=summary, environments=environments,
                  fixed_work_policy_rows=policy_rows, paired_rows=pair_rows,
                  target_frontier_rows=target_rows, mechanism_rows=mechanism_rows,
                  environment_comparison=environment_comparison,
                  one_sided_used=one_sided, extension_reserved=plan["family_allocation"]["extension_reserved"],
                  primary_one_sided_used=primary_used,
                  union_one_sided_used=None if primary_used is None else primary_used+one_sided,
                  one_sided_allocated=plan["one_sided_family_size"],
                  union_check_complete=primary_used is not None,
                  raw_array_hash_checks=arrays, weight_archive_hash_checks=weights, scopes=scopes)
    save(out/"results/EXTENSION_AUDIT.json", report)
    save(out/"results/EXTENSION_FRONTIER.json", dict(source_commit=SOURCE, rows=frontier, targets=target_rows, scopes=scopes))
    for p in sorted((out/"manuscript").glob("*extension*.tex")):
        outputs[str(REV14/p.relative_to(out))] = digest(p)
    for name in ["EXTENSION_AUDIT.json", "EXTENSION_FRONTIER.json"]:
        outputs[str(REV14/"results"/name)] = digest(out/"results"/name)
    save(out/"EXTENSION_TABLE_MANIFEST.json", dict(source_commit=SOURCE, workflow_run=RUN,
         protocol_sha256=proto_hash, reporting_script_sha256=digest(Path(__file__)), inputs=inputs, outputs=outputs))
    print(json.dumps(summary, indent=2), flush=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--results", type=Path, help="read-only relocated R13/results tree")
    parser.add_argument("--out", type=Path, help="derived revision directory; defaults to R14")
    parser.add_argument("--primary-audit", type=Path, help="completed R12 AUDIT.json for union allocation check")
    run(parser.parse_args())
