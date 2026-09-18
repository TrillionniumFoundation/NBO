# R11: dynamic transport and joint contract certification

Run from the repository root in a clean checkout. The recorded Python/NumPy/SciPy versions are 3.13.5/2.3.5/1.17.0. This runner uses the numerical loader and does not import neural-training frameworks.

```bash
python -m venv /tmp/nbo-r11
. /tmp/nbo-r11/bin/activate
python -m pip install numpy==2.3.5 scipy==1.17.0
python -u replication/r11/run.py
python replication/r11/validate.py
latexmk -pdf -interaction=nonstopmode -halt-on-error ECTA_R11.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error SUPP_R11.tex
python replication/r11/package.py
```

The runner performs a fresh computation, without a resume/checkpoint switch. It overwrites this revision's `output` files; copy a deposit elsewhere before comparing. It does not rewrite inherited scientific files. Timings depend on the machine. The kernel payload is 775,469,952 bytes, not process peak memory; allocate several GB for the full certificate workload.

`core.py` implements directional restrictions, exact first-date cap interpolation on stored knot rows, feasible-policy Bernstein coefficients, matched signed-chord/count upper values, complete feasible reachability, interval continuations, and signed transport dominance. `run.py` executes directional and adverse-state replays, the current/future dynamic decomposition, all twelve joint interventions, regional certificates, priced term/capacity choices, and independent selected-control/interior checks. `validate.py` checks the recorded numerical evidence and deposited arrays. `package.py` refuses missing/failed science, compiles no substitute sources, audits actual PDF outputs, and on GitHub checks every inherited blob against the latest review parent.

The certificate targets are fixed: eight dates; 1,617 continuation states; the inherited 1,568 later operating actions; finite first-date consumption/drift pairs plus the original frozen proposals; continuous first risky share on the stored piecewise-affine envelope; surrender eligibility after one interval. No all-date continuous-action or diffusion claim is made. Permission endpoints that are not stored knots are evaluated by interpolation between adjacent rows, not snapped to the closest feasible knot. First-date rows are deposited in `output/first_date_operator.npz`.

`output/certificate_arrays.npz` contains lower policies, their first actions, all reward-corner Bernstein coefficients, both upper coefficient arrays, feasible support, and continuation enclosures. `array_manifest.json` identifies the generated primitive arrays. Lower policy identity is held fixed before minimizing over reward corners and Bernstein indices. Direct interior checks validate implementation; they are not the continuum proof.

The active-surrender theorem is about the constrained positive class without adjustment. It does not assert elective surrender by the unconstrained agent, who chooses the nonpositive class in that region. The priced implementation frontier is an optimization over an explicit term/capacity technology implementing a selected noncancellable allocation, not an unrestricted optimal contract theorem.

A failed development run omitted arbitrary permission endpoints from the search; the stress test rejected it. The fix evaluates cap endpoints on the piecewise-affine target and was followed by fresh full reruns. This is recorded in the revision's development notes; no failed run is counted as evidence for the final source.
