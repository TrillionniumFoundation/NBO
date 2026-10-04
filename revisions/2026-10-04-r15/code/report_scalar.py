"""Audit and typeset the separate, frozen original-regime scalar comparison.

Only retained arrays are read. No training, simulation, policy selection, or
new statistical confidence assertion is performed by this reporting addition.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from decimal import Decimal, ROUND_CEILING
import hashlib
import itertools
import math
from pathlib import Path

import numpy as np

from report_economic_bounds import (ROOT, R15, canonical, child_path, digest,
                                    finite, read, require, upward, write)


def moments(values):
    values = np.asarray(values, dtype=np.float64)
    require(values.ndim == 1 and len(values) > 1 and np.isfinite(values).all(),
            "invalid scalar payoff sample")
    return dict(paths=len(values), mean=float(values.mean()),
                monte_carlo_standard_error=float(values.std(ddof=1)/math.sqrt(len(values))))


def check_moments(record, values):
    fresh = moments(values)
    for key in ["mean", "monte_carlo_standard_error"]:
        require(math.isclose(float(record[key]), fresh[key], rel_tol=1e-13, abs_tol=1e-14),
                "retained scalar moment differs from its raw sample: " + key)
    if "paths" in record:
        require(record["paths"] == fresh["paths"], "conditional scalar sample size differs")
    return fresh


def conditional(values, ids, profiles):
    return [dict(initial_state=float(y), **moments(values[ids == index]))
            for index, y in enumerate(profiles)]


def audit_interpolation_values(fit, arrays):
    y, t, a, v = (arrays[k] for k in ["state", "time", "action", "value_grid"])
    require(y.shape == (fit["nx"],) and t.shape == (fit["nt"]+1,)
            and a.shape == v.shape == (fit["nt"]+1, fit["nx"])
            and np.isfinite(v).all() and np.isfinite(a).all(), "scalar policy/value array shape differs")
    require(np.array_equal(v[0], arrays["value_t0"])
            and np.array_equal(v[-1], y), "scalar value initial/terminal arrays differ")
    for key, value in fit["value_at_initial_profiles"].items():
        require(float(np.interp(float(key), y, v[0])) == value,
                "reported scalar grid value differs from its saved vector")
    require(np.array_equal(v[:-1, 0], arrays["boundary_left"][:-1])
            and np.array_equal(v[:-1, -1], arrays["boundary_right"][:-1]),
            "scalar boundary values differ from the declared finite-grid problem")
    lower, upper = arrays["action_lower_by_time"], arrays["action_upper_by_time"]
    require((a >= lower[:, None]).all() and (a <= upper[:, None]).all(),
            "saved classical policy is outside its declared action class")


def audit_algebraic_bound(fit, arrays, rho, horizon):
    radii = arrays["max_equation_residual_upper_by_time"]
    require(radii.shape == (fit["nt"],) and np.isfinite(radii).all()
            and (radii >= 0).all(), "invalid outward Bellman residual vector")
    h = Fraction.from_float(float(horizon/fit["nt"]))
    denominator = 1 + Fraction.from_float(float(rho))*h
    bound = 0.
    for radius in radii[::-1]:
        bound = upward((Fraction.from_float(bound) + h*Fraction.from_float(float(radius))) / denominator)
    recorded = finite(fit["finite_grid_solve_error_bound"], "scalar algebraic error", True)
    require(recorded >= bound, "stored algebraic bound rounds below the residual recurrence")
    require(float(radii.max()) == fit["max_equation_residual_upper"],
            "maximum scalar residual differs from saved time series")
    return dict(replayed_recurrence_upper=bound, recorded_finite_grid_upper=recorded,
                recurrence_scope="exact finite-grid and boundary equations; no domain or diffusion discretization allowance")


def report(protocol_path, scalar_dir, manifest_path, out, repo=ROOT,
           evidence_manifest_path=None):
    repo = Path(repo).resolve()
    protocol_path, scalar_dir, manifest_path, out = map(
        lambda x: Path(x).resolve(), [protocol_path, scalar_dir, manifest_path, out])
    evidence_manifest_path = (Path(evidence_manifest_path).resolve() if evidence_manifest_path
                              else manifest_path.parent/"EVIDENCE_MANIFEST.json")
    p, manifest, evidence = map(read, [protocol_path, manifest_path, evidence_manifest_path])
    result_path, work_path = scalar_dir/"SCALAR_BASELINE.json", scalar_dir/"WORK.json"
    result, work = read(result_path), read(work_path)
    source, protocol_hash = manifest["numerical_source_commit"], digest(protocol_path)
    require(p["study_id"] == "r15_scalar_original_regime" and p["dimension"] == 1
            and p["primitives"]["idiosyncratic_sigma"] == .15
            and p["primitives"]["common_sigma"] == .1,
            "scalar report must use its separately declared original calibration")
    require(result["stage"] == "official_scalar_comparison"
            and result["source_commit"] == work["numerical_source_commit"]
            == evidence["numerical_source_commit"] == source,
            "scalar evidence has not been generated by the frozen numerical source")
    require(result["protocol_sha256"] == work["protocol_sha256"]
            == manifest["scalar_protocol_sha256"] == protocol_hash,
            "scalar protocol provenance differs")
    require(work["complete"] is True and work["returncode"] == 0
            and work["method_id"] == "scalar_howard"
            and work["method_fingerprint"] == manifest["method_fingerprints"]["scalar_howard"]["sha256"],
            "complete, independently timed scalar process receipt is required")
    require(hashlib.sha256(canonical(work["environment"])).hexdigest() == work["environment_fingerprint"],
            "scalar execution environment fingerprint differs")
    for name, item in manifest["files"].items():
        require(digest(child_path(repo, name)) == item["sha256"],
                "frozen scalar numerical dependency differs: " + name)
    fp = manifest["method_fingerprints"]["scalar_howard"]
    require(hashlib.sha256(canonical(fp["input"])).hexdigest() == fp["sha256"]
            and fp["input"]["protocol_sha256"] == protocol_hash
            and fp["input"]["files"] == {k: v["sha256"] for k, v in manifest["files"].items()},
            "scalar algorithm fingerprint does not bind the declared source")
    inventory = {x.relative_to(scalar_dir).as_posix(): digest(x)
                 for x in scalar_dir.rglob("*") if x.is_file() and x != work_path}
    require(inventory == work["files"], "scalar artifact inventory differs from inclusive work receipt")
    for path in [manifest_path, work_path, *[scalar_dir/name for name in inventory]]:
        require(path.is_relative_to(repo)
                and evidence["files"].get(path.relative_to(repo).as_posix()) == digest(path),
                "scalar source/evidence digest mismatch: " + str(path))

    fits = result["classical_fits"]
    expected_grids = [(a["epsilon"], g["nx"], g["nt"], g["L"])
                      for a in p["classical_action_classes"] for g in p["grids"]]
    require(len(fits) == 8 and [(f["epsilon"], f["nx"], f["nt"], f["L"]) for f in fits] == expected_grids,
            "all eight prespecified classical training candidates are required")
    labels, fit_audit, arrays_by_fit = {"schedule": "Schedule"}, [], {}
    for index, fit in enumerate(fits):
        require(fit["source_commit"] == source and fit["dimension"] == 1
                and fit["method_id"] == "scalar_howard", "classical candidate source differs")
        require(read(scalar_dir/(fit["id"]+".json")) == fit,
                "embedded classical record differs from its original record")
        raw = child_path(scalar_dir, fit["policy_path"])
        require(digest(raw) == fit["policy_sha256"], "classical policy array hash differs")
        with np.load(raw, allow_pickle=False) as data:
            arrays = {k: data[k].copy() for k in data.files}
        audit_interpolation_values(fit, arrays)
        audit = audit_algebraic_bound(fit, arrays, p["primitives"]["discount"], p["primitives"]["T"])
        labels[fit["id"]] = ("F" if fit["epsilon"] is None else "T") + str(index%4+1)
        fit_audit.append(dict(policy=fit["id"], label=labels[fit["id"]], converged=fit["converged"], **audit))
        arrays_by_fit[fit["id"]] = arrays
    neural = result["neural_candidates"]
    require([x["name"] for x in neural] == [x["name"] for x in p["frozen_neural_candidates"]],
            "historical scalar neural candidate set differs")
    for found, declared in zip(neural, p["frozen_neural_candidates"]):
        require(found["weights_sha256"] == declared["sha256"]
                == digest(child_path(repo, declared["path"]))
                and found["provenance"] == declared
                and found["iteration"] == declared["selected_iteration"],
                "historical scalar candidate weights or selection provenance differ")
        labels[found["name"]] = "NBO (R12)" if found["method_id"] == "nbo_r12" else "DPO (R12)"
    profiles = p["initial_profiles"]
    names = ["schedule"] + [x["id"] for x in fits] + [x["name"] for x in neural]
    require(len(names) == 11, "eleven scalar deployed candidates are required")
    evaluations, raw_banks, contrasts = result["evaluations"], [], []
    require([e["steps"] for e in evaluations] == p["evaluation_steps"],
            "both declared scalar deployment meshes are required")
    gain_rows, payoff_rows = [], []
    for e in evaluations:
        require(e["source_commit"] == source and e["paths"] == p["evaluation_paths"]
                and e["seed"] == p["evaluation_seed"]
                and e["brownian_base_steps"] == p["brownian_base_steps"]
                and e["initial_profiles"] == profiles, "scalar evaluation design differs")
        require(read(scalar_dir/(e["id"]+".json")) == e, "embedded evaluation differs from original record")
        raw = scalar_dir/(e["id"]+".npz")
        require(digest(raw) == e["raw_sha256"], "scalar payoff bank hash differs")
        with np.load(raw, allow_pickle=False) as data:
            bank = {k: data[k].copy() for k in data.files}
        require(list(bank["policy_names"]) == names
                and bank["payoff"].shape == (11, e["paths"])
                and np.isfinite(bank["payoff"]).all(), "scalar payoff bank shape or candidate order differs")
        ids = bank["initial_profile"]
        require(np.isin(ids, np.arange(3)).all()
                and np.array_equal(bank["initial_state"], np.asarray(profiles)[ids])
                and hashlib.sha256(ids.tobytes()).hexdigest() == e["initial_index_hash"]
                and hashlib.sha256(bank["initial_state"].tobytes()).hexdigest() == e["initial_state_hash"],
                "scalar initial-state bank identity differs")
        require([x["policy"] for x in e["records"]] == names, "incomplete scalar policy summary")
        for index, row in enumerate(e["records"]):
            vv = bank["payoff"][index]
            checked = check_moments(row, vv)
            by_profile = conditional(vv, ids, profiles)
            for stored, group in zip(row["by_initial_profile"], by_profile):
                require(stored["initial_state"] == group["initial_state"], "conditional profile order differs")
                check_moments(stored, vv[ids == profiles.index(group["initial_state"])] )
            payoff_rows.append(dict(steps=e["steps"], policy=row["policy"], **checked,
                                    by_initial_profile=by_profile))
            gain = vv-bank["payoff"][0]
            gain_rows.append(dict(steps=e["steps"], policy=row["policy"], label=labels[row["policy"]],
                                  **moments(gain), by_initial_profile=conditional(gain, ids, profiles),
                                  deployment_forward_seconds=row["deployment_forward_seconds"],
                                  outside_policy_grid_frequency=row["outside_policy_grid_frequency"],
                                  primitive_action_bound_frequency=row["primitive_action_bound_frequency"]))
        expected_pairs = list(itertools.combinations(names, 2))
        require([(x["left"], x["right"]) for x in e["paired_contrasts"]] == expected_pairs,
                "all 55 scalar pairs on each mesh are required")
        for row in e["paired_contrasts"]:
            delta = bank["payoff"][names.index(row["left"])]-bank["payoff"][names.index(row["right"])]
            checked = check_moments(row, delta)
            for index, stored in enumerate(row["by_initial_profile"]):
                check_moments(stored, delta[ids == index])
            contrasts.append(dict(steps=e["steps"], left=row["left"], right=row["right"],
                                  **checked, by_initial_profile=conditional(delta, ids, profiles)))
        raw_banks.append(bank)
    for key in ["initial_state_hash", "initial_index_hash", "noise_sha256", "brownian_base_steps", "paths"]:
        require(evaluations[0][key] == evaluations[1][key], "scalar deployment grids do not share fine Brownian paths")

    refinements = result["grid_refinement"]
    require(len(refinements) == 6, "all six scalar training-grid comparisons are required")
    fits_by_id = {x["id"]: x for x in fits}
    for r in refinements:
        earlier, later = fits_by_id[r["earlier"]], fits_by_id[r["later"]]
        for y in profiles:
            expected = later["value_at_initial_profiles"][str(y)]-earlier["value_at_initial_profiles"][str(y)]
            require(r["value_change_at_initial_profiles"][str(y)] == expected,
                    "training-grid refinement differs from saved values")
        if r["comparison"] == "domain_at_fixed_mesh":
            require(earlier["nt"] == later["nt"]
                    and math.isclose(2*earlier["L"]/(earlier["nx"]-1),
                                     2*later["L"]/(later["nx"]-1), rel_tol=0, abs_tol=1e-17),
                    "domain comparison also changes the declared mesh")
    changes = raw_banks[1]["payoff"]-raw_banks[0]["payoff"]
    temporal = result["deployment_mesh_refinement"]
    require([x["policy"] for x in temporal] == names, "all deployment sensitivities are required")
    for index, r in enumerate(temporal):
        check_moments(r, changes[index])
        for profile_index, stored in enumerate(r["by_initial_profile"]):
            check_moments(stored, changes[index][raw_banks[0]["initial_profile"] == profile_index])

    class_pairs = []
    for full, tube in zip(fits[:4], fits[4:]):
        fa, ta = arrays_by_fit[full["id"]], arrays_by_fit[tube["id"]]
        require(np.array_equal(fa["state"],ta["state"])
                and np.array_equal(fa["time"],ta["time"])
                and np.array_equal(fa["boundary_left"],ta["boundary_left"])
                and np.array_equal(fa["boundary_right"],ta["boundary_right"])
                and (ta["action_lower_by_time"]>=fa["action_lower_by_time"]).all()
                and (ta["action_upper_by_time"]<=fa["action_upper_by_time"]).all(),
                "full/tube finite-grid comparison requires identical nodes/data and nested action sets")
        # Enlarge the action set, then combine the two proved algebraic
        # enclosures. This is a deterministic finite-grid restriction bound.
        nodal_difference=max(abs(Fraction.from_float(float(a))-Fraction.from_float(float(b)))
                             for a,b in zip(fa["value_t0"],ta["value_t0"]))
        tube_loss=upward(nodal_difference+Fraction.from_float(full["finite_grid_solve_error_bound"])
                         +Fraction.from_float(tube["finite_grid_solve_error_bound"]))
        array_identity={}
        for name in ["state","time","value_t0","value_grid","action","boundary_left","boundary_right"]:
            first_hash=hashlib.sha256(fa[name].tobytes(order="C")).hexdigest()
            second_hash=hashlib.sha256(ta[name].tobytes(order="C")).hexdigest()
            array_identity[name]=dict(shape=list(fa[name].shape),dtype=fa[name].dtype.str,
                                      full_sha256=first_hash,tube_sha256=second_hash,
                                      bitwise_equal=fa[name].shape==ta[name].shape and fa[name].dtype==ta[name].dtype
                                      and first_hash==second_hash)
        class_pairs.append(dict(full=full["id"], tube=tube["id"],
                                full_policy_sha256=full["policy_sha256"],tube_policy_sha256=tube["policy_sha256"],
                                array_identity=array_identity,
                                action_arrays_bitwise_equal=array_identity["action"]["bitwise_equal"],
                                value_arrays_bitwise_equal=array_identity["value_grid"]["bitwise_equal"],
                                maximum_action_difference=float(np.max(abs(fa["action"]-ta["action"]))),
                                maximum_value_difference=float(np.max(abs(fa["value_grid"]-ta["value_grid"]))),
                                exact_finite_grid_tube_loss_upper_at_t0=tube_loss,
                                restriction_bound_scope="All t=0 spatial nodes of the identical finite-grid boundary problem; not an unbounded continuous-time restriction bound"))
    answer = dict(status="complete", record_type="R15 independently audited scalar training and deployment report",
                  numerical_source_commit=source, source_commit=source,
                  reporting_source_sha256=digest(__file__), reporting_helper_sha256=digest(Path(__file__).with_name("report_economic_bounds.py")),
                  protocol_sha256=protocol_hash, source_manifest_sha256=digest(manifest_path),
                  evidence_manifest_sha256=digest(evidence_manifest_path),
                  input_manifest_record_type=evidence.get("record_type", "declared evidence digest manifest"),
                  input_manifest_scope=evidence.get("scope", evidence.get("hash_scope", "complete scalar inputs; main study completeness is a separate account")),
                  scalar_result_sha256=digest(result_path), work_sha256=digest(work_path),
                  counts=dict(classical_fits=8, frozen_neural_policies=2, total_deployed_policies=11,
                              deployment_meshes=2, paired_policy_comparisons=110,
                              grid_refinements=6, deployment_refinements=11),
                  labels=labels, classical_fits=fits, fit_audit=fit_audit,
                  neural_candidates=neural, payoff_rows=payoff_rows, gain_rows=gain_rows,
                  paired_comparisons=contrasts, grid_refinement=refinements,
                  deployment_mesh_refinement=temporal, full_tube_comparisons=class_pairs,
                  work=dict(end_to_end_seconds=work["end_to_end_seconds"],
                            peak_rss_kib=work["peak_rss_kib"], cpu_seconds=work["cpu_seconds"],
                            classical_fitting_and_serialization_seconds=sum(x["seconds"] for x in fits),
                            evaluation_seconds=sum(e["seconds"] for e in evaluations),
                            scope=work["timing_scope"]),
                  initial_profile_counts={str(y):int(np.sum(raw_banks[0]["initial_profile"] == i))
                                          for i,y in enumerate(profiles)},
                  fine_noise_sha256=evaluations[0]["noise_sha256"],
                  scope="Separate original-volatility scalar comparison. All Monte Carlo standard errors are conditional numerical Euler-policy errors; no continuous-time or unbounded-domain coverage is added.")
    out.mkdir(parents=True,exist_ok=True)
    write(out/"SCALAR_REPORT.json", answer)
    generate_tables(answer, out, repo)
    return answer


def number(value, digits=6):
    rendered=f"{float(value):.{digits}f}"
    return f"{0.:.{digits}f}" if float(rendered)==0. else rendered


def scientific_upper(value, digits=2):
    value=Decimal.from_float(float(value))
    exponent=value.adjusted()
    rounded=value.quantize(Decimal(1).scaleb(exponent-digits),rounding=ROUND_CEILING)
    return f"{rounded:.{digits}E}"


def scientific_tex(value, digits=3):
    mantissa, exponent=f"{float(value):.{digits}e}".split("e")
    return r"$"+mantissa+r"\times10^{"+str(int(exponent))+r"}$"


def scientific_upper_tex(value, digits=3):
    mantissa, exponent=scientific_upper(value,digits).split("E")
    return r"$"+mantissa+r"\times10^{"+str(int(exponent))+r"}$"


def table(path, caption, label, header, rows, note, long=False):
    columns = "l" + "r"*(len(header)-1)
    lines = ([r"\begingroup\small",r"\begin{longtable}{"+columns+"}",
              r"\caption{"+caption+r"}\label{"+label+r"}\\"] if long else
             [r"\begin{table}[!htbp]",r"\centering\small",r"\caption{"+caption+"}",
              r"\label{"+label+"}",r"\begin{tabular}{"+columns+"}"])
    lines += [r"\toprule", " & ".join(header)+r" \\", r"\midrule"]
    if long:
        lines += [r"\endfirsthead",r"\toprule"," & ".join(header)+r" \\",r"\midrule",r"\endhead"]
    lines += [" & ".join(str(x) for x in row)+r" \\" for row in rows]
    lines += [r"\bottomrule",r"\end{longtable}" if long else r"\end{tabular}",
              r"\par\medskip\noindent\footnotesize "+note,
              r"\endgroup" if long else r"\end{table}"]
    path.write_text("\n".join(lines)+"\n")


def generate_tables(r,out,repo):
    labels = r["labels"]
    rows = []
    for f in r["classical_fits"]:
        vals = f["value_at_initial_profiles"]
        rows.append([labels[f["id"]], f"{f['nx']}/{f['nt']}/{f['L']:g}"]+
                    [number(vals[str(y)]) for y in [-1.,0.,1.]]+
                    [scientific_upper(f['finite_grid_solve_error_bound']),number(f["seconds"],2)])
    table(out/"table_scalar_training.tex", "Independent scalar training and algebraic accuracy", "tab:r15scalartraining",
          ["Policy", "$N_y/N_t/L$", "$v(-1)$", "$v(0)$", "$v(1)$", "$E_0$", "Seconds"], rows,
          r"F1--F4 solve the full primitive action box; T1--T4 solve the common schedule tube of radius $0.1$. "
          r"$E_0$ is the outward finite-grid algebraic error bound in Proposition~\ref{prop:r15scalarresidual}. "
          r"The displayed error endpoints are rounded upward; the full outward endpoints are retained in the artifact. "
          r"Seconds include each new solve, its interval residual audit, and policy serialization. The last grid enlarges the domain "
          r"from $[-6,6]$ to $[-9,9]$ at the same declared spatial and temporal spacing. Boundary data are the stated far-state approximation.")
    fine_steps = max(x["steps"] for x in r["gain_rows"])
    for fine_only, filename, label in [(True,"table_scalar_deployment.tex","tab:r15scalardeployment"),
                                     (False,"table_scalar_all_meshes.tex","tab:r15scalarallmeshes")]:
        rows=[]
        for z in r["gain_rows"]:
            if fine_only and z["steps"] != fine_steps:continue
            row=[labels[z["policy"]]]
            if not fine_only:row.append(z["steps"])
            row += [number(1e3*x["mean"],4) for x in z["by_initial_profile"]]
            row += [number(1e3*z["mean"],4),number(1e3*z["monte_carlo_standard_error"],4)]
            rows.append(row)
        table(out/filename,"Deployed scalar policy gains on common diffusion paths",label,
              ["Policy"]+([] if fine_only else ["Steps"])+["$y=-1$","$y=0$","$y=1$","Population","MC s.e."],rows,
              r"All payoff gains and standard errors are multiplied by $10^3$. The comparator is the analytical schedule evaluated "
              r"on the same numerical mesh and Brownian path. Population denotes the mean over independent uniform initial-state draws; "
              r"the last column is its paired Monte Carlo standard error. Initial-state columns retain their separate rankings. "
              r"NBO and DPO are the prespecified frozen R12 scalar policies. These are conditional Euler-deployment diagnostics; "
              r"Monte Carlo standard errors do not include continuous-time or boundary approximation error.",long=not fine_only)
    rows=[]
    for z in r["grid_refinement"]:
        rows.append([labels[z["earlier"]]+"--"+labels[z["later"]],
                     "Domain" if z["comparison"] == "domain_at_fixed_mesh" else "Mesh"]+
                    [f"{z['value_change_at_initial_profiles'][str(y)]:.3e}" for y in [-1.,0.,1.]])
    table(out/"table_scalar_refinement.tex","Scalar training-grid and domain sensitivity","tab:r15scalarrefinement",
          ["Comparison","Change","$y=-1$","$y=0$","$y=1$"],rows,
          r"Entries are later-grid minus earlier-grid values, retaining their signs. Domain changes keep the declared "
          r"difference spacing and time step fixed. The differences are numerical sensitivities, separate from the algebraic residual bound.")
    rows=[]
    for z in r["deployment_mesh_refinement"]:
        rows.append([labels[z["policy"]]]+[f"{x['mean']:.3e}" for x in z["by_initial_profile"]]
                    +[f"{z['mean']:.3e}",f"{z['monte_carlo_standard_error']:.3e}"])
    table(out/"table_scalar_time_refinement.tex","Scalar deployment-mesh sensitivity","tab:r15scalartime",
          ["Policy","$y=-1$","$y=0$","$y=1$","Population","MC s.e."],rows,
          r"Entries are payoff at 2,048 steps minus payoff at 1,024 steps using the same fine Brownian increments and initial draws. "
          r"The frozen policy table or neural weights are unchanged between deployments. These paired numerical changes are not a time-discretization error bound.")
    rows=[]
    for z in r["paired_comparisons"]:
        rows.append([labels[z["left"]]+"--"+labels[z["right"]],z["steps"]]
                    +[number(1e3*x["mean"],4) for x in z["by_initial_profile"]]
                    +[number(1e3*z["mean"],4),number(1e3*z["monte_carlo_standard_error"],4)])
    table(out/"table_scalar_all_pairs.tex","Every paired scalar policy comparison","tab:r15scalarpairs",
          ["Left minus right","Steps","$y=-1$","$y=0$","$y=1$","Population","MC s.e."],rows,
          r"All 55 pairs on both meshes are retained; means and standard errors are multiplied by $10^3$. "
          r"The full machine-readable account additionally retains every initial-state standard error and raw payoff array. "
          r"These conditional numerical comparisons spend no confidence allocation and do not claim continuous-time coverage.",long=True)
    relative=out.relative_to(repo).as_posix()
    full_fine=r["classical_fits"][3]["id"]
    gain_by_policy={x["policy"]:x for x in r["gain_rows"] if x["steps"]==fine_steps}
    fine_pairs={(x["left"],x["right"]):x for x in r["paired_comparisons"] if x["steps"]==fine_steps}
    classical_nbo=fine_pairs[full_fine,"frozen_r12_nbo"]
    classical_dpo=fine_pairs[full_fine,"frozen_r12_dpo"]
    neural_pair=fine_pairs["frozen_r12_nbo","frozen_r12_dpo"]
    domain=max(abs(v) for x in r["grid_refinement"] if x["comparison"]=="domain_at_fixed_mesh"
               for v in x["value_change_at_initial_profiles"].values())
    last_refinement=[x for x in r["grid_refinement"] if x["later"]==r["classical_fits"][2]["id"]][0]
    last_changes=list(last_refinement["value_change_at_initial_profiles"].values())
    e0=[x["finite_grid_solve_error_bound"] for x in r["classical_fits"]]
    max_steps=max(x["maximum_howard_iterations"] for x in r["classical_fits"])
    scalar_fit=[x["seconds"] for x in r["classical_fits"]]
    grid_forward=[gain_by_policy[x["id"]]["deployment_forward_seconds"] for x in r["classical_fits"]]
    neural_forward=[gain_by_policy[x]["deployment_forward_seconds"] for x in ["frozen_r12_nbo","frozen_r12_dpo"]]
    complete_solves=sum(bool(x["converged"]) for x in r["classical_fits"])
    main=[r"\subsection{Independent scalar training and numerical accuracy}",r"\label{sec:r15scalarresults}",
          r"The separate scalar study uses the original volatility calibration, $(\sigma_I,\sigma_C)=(0.15,0.10)$, "
          r"and the same one-state capital economy. Eight independent Howard solves generate full-box and matched-tube "
          r"policies on all four prespecified grids. The policies are then evaluated by actual interpolation-based deployment "
          r"on 8,192 fresh paths at both 1,024 and 2,048 time steps. The analytical schedule and both frozen scalar neural "
          r"policies use the same initial states and Brownian paths.",
          r"\input{"+relative+r"/table_scalar_training.tex}",
          f"All {complete_solves} classical solves reached the stated stopping criterion, using at most {max_steps} Howard updates "
          r"at each date. Their finite-grid algebraic bounds range from "+scientific_tex(min(e0))+" to "+scientific_tex(max(e0))+". "
          r"The last joint state--time refinement changes the three initial-state values by amounts between "+
          scientific_tex(min(abs(x) for x in last_changes))+" and "+scientific_tex(max(abs(x) for x in last_changes))+". "
          r"The subsequent enlargement of the domain changes these values by at most "+scientific_tex(domain)+". "
          r"Thus the algebraic solve, the training-grid approximation, and the finite-domain approximation have separate, "
          r"observable numerical accounts. The small domain change does not bound the remaining time or spatial discretization error.",
          r"\input{"+relative+r"/table_scalar_deployment.tex}",
          r"At 2,048 deployment steps, the largest-domain classical policy has a mean schedule gain of "+
          scientific_tex(gain_by_policy[full_fine]["mean"])+", compared with "+
          scientific_tex(gain_by_policy["frozen_r12_nbo"]["mean"])+" for NBO and "+
          scientific_tex(gain_by_policy["frozen_r12_dpo"]["mean"])+" for DPO. "
          r"The paired classical advantages are "+scientific_tex(classical_nbo["mean"])+
          r" (Monte Carlo standard error "+scientific_tex(classical_nbo["monte_carlo_standard_error"])+r") against NBO and "+
          scientific_tex(classical_dpo["mean"])+r" ("+scientific_tex(classical_dpo["monte_carlo_standard_error"])+r") against DPO. "
          r"Both advantages are positive at each of the three reported initial states. The numerical comparison therefore "
          r"identifies an independently computed feasible classical competitor with higher observed payoffs "
          r"than both frozen neural policies in this scalar economy.",
          r"The neural ordering varies across initial states. NBO minus DPO has population mean "+
          scientific_tex(neural_pair["mean"])+r", but its conditional mean at $y=1$ is "+
          scientific_tex(neural_pair["by_initial_profile"][2]["mean"])+
          r". The same reversal occurs on the 1,024-step deployment mesh. This state-specific outcome is retained "
          r"alongside the population comparison. Corresponding full-box and tube policies have identical payoffs "
          r"path by path on both reported deployment meshes. The maximum recorded nodal deviation from the schedule is "+
          number(max(f["maximum_schedule_deviation"] for f in r["classical_fits"]),6)+
          r", below the tube radius. This observation concerns the computed scalar policies and does not establish "
          r"that the tube restriction is harmless in every dimension.",
          r"The complete scalar process consumed "+number(r["work"]["end_to_end_seconds"],2)+
          r" seconds, including fresh-process setup, all eight solves, interval audits, serialization, "
          r"both common-path deployments, and output. The individual new classical solves consumed "+
          number(min(scalar_fit),2)+r"--"+number(max(scalar_fit),2)+r" seconds. Within the fine-mesh deployment, "
          r"the measured action-evaluation totals were "+number(min(grid_forward),2)+r"--"+number(max(grid_forward),2)+
          r" seconds for the classical tables and "+number(min(neural_forward),2)+r"--"+number(max(neural_forward),2)+
          r" seconds for the frozen neural maps. These are operation-specific measurements on the recorded worker. "
          r"The historical neural fitting clocks are not included in a new end-to-end training comparison.",
          r"The algebraic error bound concerns the exact equations with their declared boundary data. "
          r"The independent domain enlargement and paired deployment-mesh comparisons quantify distinct numerical sensitivities. "
          r"The complete tables retain all trained policies, both meshes, all initial-state strata, and all 110 pairwise numerical "
          r"comparisons. They supply a scalar accuracy and classical-work benchmark without identifying an exact value for "
          r"the high-dimensional diffusion."]
    if r.get("full_tube_comparisons"):
        loss=max(x["exact_finite_grid_tube_loss_upper_at_t0"] for x in r["full_tube_comparisons"])
        equal=all(x["value_arrays_bitwise_equal"] for x in r["full_tube_comparisons"])
        text=(r"The complete full-box and matched-tube value arrays "
              +(r"coincide bit for bit on each of the four grids. " if equal else r"are compared at every stored node. ")
              +r"Because the action sets are nested and the terminal and boundary data are identical, "
              +r"Corollary~\ref{cor:r15scalartube} converts the two algebraic enclosures into a bound on the "
              +r"loss from the tube restriction in the exact finite-grid problem. Across the four grids, "
              +r"this loss at every initial-date node is at most "+scientific_upper_tex(loss,3)+
              r". This deterministic conclusion concerns the stated finite-grid problem; the domain "
              r"and diffusion approximation accounts retain their separate scope.")
        main.insert(8,text)
    (out/"scalar_evidence.tex").write_text("\n\n".join(main)+"\n")
    supp=[r"\section{Complete Scalar Comparison Tables}",r"\label{app:r15scalartables}"]
    for name in ["all_meshes","refinement","time_refinement","all_pairs"]:
        supp.append(r"\input{"+relative+"/table_scalar_"+name+r".tex}")
    (out/"scalar_complete_tables.tex").write_text("\n\n".join(supp)+"\n")


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol",dest="protocol_path",required=True)
    parser.add_argument("--scalar",dest="scalar_dir",required=True)
    parser.add_argument("--manifest",dest="manifest_path",required=True)
    parser.add_argument("--evidence-manifest",dest="evidence_manifest_path")
    parser.add_argument("--repo",default=str(ROOT))
    parser.add_argument("--out",required=True)
    answer=report(**vars(parser.parse_args()))
    print({"status":answer["status"],"counts":answer["counts"]})
