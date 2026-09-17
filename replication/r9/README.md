# R9: participation, surrender, and first-period portfolio permissions

The current complete source entry points are `ECTA_R9.tex` and `SUPP_R9.tex`.
The revision is based on review `8c20474bca5b7388f5ba4640ec165f1ad8f5e91a`,
which reviews the complete R8 at `be77b2a81b4d3a68806c534c1e892d2eb4b1230d`.
Historical scientific files, policies, outputs, manuscripts, and reviews are
read-only inputs. No training or new settlement-grid run occurs in R9.

## Reproduce

Use a full checkout of the revision branch, Python 3.13, and the pinned numerical
requirements. LaTeX compilation uses the repository's Econometric Society class,
`latexmk`, and the TeX Live extra/science/recommended-font packages.

```bash
python -m pip install -r replication/r9/requirements.txt
python replication/r9/run.py --mode all
python replication/r9/validate.py
python replication/r9/tables.py
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build-r9 ECTA_R9.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build-r9 SUPP_R9.tex
python replication/r9/package.py --build build-r9
```

The numerical run writes only this revision's `output` directory. Use an isolated
worktree when auditing a deposited execution so that its original results remain
available for comparison. Timings and environment fields are execution-specific;
compare scientific values with stated numerical tolerances, not whole-file hashes.
The full baseline sparse kernel payload is about 775 MB; temporary action arrays
and interpreter/process overhead require additional memory.

## Programs and evidence

`contracts.py` implements the additional stop action, policy moments, streamed
upper certificates, first-date breakpoint reduction, and exact interpolation-cell
permission derivatives. `run.py` reoptimizes fee/term counterfactuals, constructs
the reachable-state enforcement bound, maps both permission and benefit roots,
and evaluates three regional targets with both upper methods. `validate.py`
compares the stopping recursion with separately enumerated toy policies, checks
full-model parameter points, reconstructs selected-control economic transitions,
and records procurement and statewise capacity comparisons. `tables.py` generates
eight manuscript tables from executed JSON. `package.py` performs preservation,
output, and manuscript checks before assembling the reading package.

The fee certificate adds voluntary surrender to the original finite action target.
The permission study instead permits a continuous **first-date risky share** for
each inherited finite consumption/adjustment pair and feasible original frozen
proposal; every later menu is unchanged. It is not a continuous-control solution
in all three controls. These two action targets are not silently combined.

## Interpretation

The original noncancellable experiment is retained. Free surrender, the negative
relative option at an intermediate fee, the failed regional result at fee 0.80,
and both adverse portfolio-permission extensions are retained. The fee interval
[0.85, 0.90] is tested on the **original** law/benefit rectangle.

Participation uses a separate additive utility numeraire and finite external
guarantee capacity. It is not a managed-wealth injection or a monetary CRRA
compensating-variation calculation. Positive capacity carrying costs and a
principal's break-even service flow are explicit.

The error allowance applies to evaluation of stored transition/reward arrays.
Direct selected-control reconstruction is an implementation check, not a directed-
rounding enclosure of the constructor. Benefit roots are local floating-point
solver brackets, not uniqueness theorems or interval root enclosures. No diffusion
sign, new neural speedup, or optimal contract-design claim is made by these runs.
