# NBO R11: policy-specific continuous-economy verification

This revision responds to the 4 October 2026 advisory review of R10. It retains
Neural Bellman Operators as the paper's topic and preserves the original
recursive-utility, preference, temporal-self, strategic and trace applications.
The main article is reorganized rather than shortened by deleting those models.
`EDITORIAL_MAP.json` records exact source relocation and prior-root hashes.

## Research changes

The new policy-specific certificate combines an exact paired payoff identity,
a proved O(h) diffusion-transfer bound for an explicitly deployed innovation
controller, a Gaussian-tail clipping account, and finite-family empirical
Bernstein inference. The real economic state remains the original diffusion.
The result is conditional on the declared numerical and sampling contract and
is pointwise at recorded initial states. It is not a state-uniform PDE bound,
an optimizer convergence theorem, a formally verified random generator, or a
continuous-transfer result for the preference model.

The NBO evaluation block fits both current-policy rollout values and pathwise
costates, then improves the actor while holding the new critic derivatives
fixed. Ten-seed primary comparisons include direct-policy and affine actors.
Additional comparisons include longer baselines, validation-tuned projected
critic greedification, architecture/radius changes, checkpoint frontiers,
shifted and dispersed initial states, a Student-t cross-sectional stress, and
poor policies in the same feasible tube. `PROTOCOL.json` was fixed after
exploratory development but before final remote fitting. Its final noise bank
is distinct from the development bank. All final checkpoints and raw path
statistics are retained; numerical completion and economic accuracy are
separate fields.

## Reproduction

Use Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, PyTorch 2.10.0 CPU, mpmath 1.3.0,
and optional Numba 0.65.1. Set OMP/MKL/OPENBLAS threads to one. From repository root:

```sh
python revisions/2026-10-04-r11/code/test_r11.py
python revisions/2026-10-04-r11/code/run_study.py --seed 11
# Repeat for all ten seeds in PROTOCOL.json, without replacing failed seeds.
python revisions/2026-10-04-r11/code/run_greedy.py
python revisions/2026-10-04-r11/code/replay_inherited.py
python revisions/2026-10-04-r11/code/report.py
python revisions/2026-10-04-r11/code/build.py
```

The build needs the unchanged repository Econometrica class and BibTeX style,
TeX Live with the science/extra packages, and Poppler. `integrate.py` is needed
only on the pre-integration source pack; an evidence branch already contains
the integrated roots. It verifies the exact R10 root before editing.

`report.py` recomputes every paired statistic and interval from saved arrays,
verifies weight and raw-data hashes, checks the finite-family allocation, and
writes all printed numerical tables. `finalize.py` additionally verifies every
historical blob, the materialized source manifest, tests, and compilation before
publication to new evidence/referee branches. It does not turn a failed gain
target into a pass. `REMOTE_EXECUTION.json` identifies the actual run and source.

## Files and reading order

The repository root `ECTA.tex` is the authoritative new main manuscript;
`supp.tex` contains complete retained applications and proofs as well as the new
transfer proof and seed-level record. `response.tex` answers B1--B7 and M1--M10.
`build/` holds fresh compiled artifacts and logs; `results/` holds weights,
raw arrays, exact-state and noise identities, costs, diagnostics and replay
accounts. `TABLE_MANIFEST.json` binds every generated table to its inputs.

The historical R10 comparison remains adverse for some actors. New successes,
competitive baselines, failures and unmet targets are reported from the actual
R11 record. No numerical result is evidence of an Econometrica editorial
assessment. Existing review and revision branches are left unchanged.
