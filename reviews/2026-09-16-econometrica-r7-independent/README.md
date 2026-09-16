# Independent Econometrica-style review of NBO R7

**结论：当前版本建议拒稿（Reject in its present form）。** 本目录是仓库所有者委托的独立审稿材料，不代表 Econometrica 的正式任命或编辑决定。

本次核查时，`revision/econometrica-r8-2026-09-16` 仍指向原 R7 review head，并无新的 R8 稿件。实际审阅的是 R7 稿件 `fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17`。本目录补充新的独立审稿，不覆盖原 R7 报告，不修改论文、作者代码或历史输出。

## Read first

[referee_report.md](referee_report.md) is the complete English report. [diagnostic_results.json](diagnostic_results.json) records the newly executed evidence, source provenance, environment, and program identities.

Two findings extend the previous report rather than merely repeat it. At the same eight decision dates, the same common action menu, and `(lambda,d)=(0.25,0.45)`, spatial refinement changes the no-adjustment class difference from `-5.300125090501595e-5` on `33 x 49` states to `+7.203016004175833e-5` on `65 x 97` states. A separate kernel audit shows that positive interpolation inflates local preference variance by approximately 2.828 at zero adjustment on the original grid; this numerical contribution depends on the adjustment control. The report explains why neither finding is a counterexample to a theorem expressly conditional on the original stored finite arrays.

The report credits the repaired finite-model mathematics, regional coefficient certificate, and positive autonomous compression comparison. It distinguishes these from the still unresolved robustness, mechanism, and contribution questions. The earlier matched neural-free regional result and author timings are attributed to existing records, not claimed as fresh executions.

## Reproduction

Run from a checkout containing the pinned R7 source and evidence. This review branch inherits all required inputs. The tested environment was Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, and PyTorch 2.10.0+cpu on Linux. PyTorch is imported by the inherited transition module; these reviewer checks do not train neural networks. The spatial program fixes numerical-library thread counts to one.

Set an output directory outside author evidence paths:

```bash
REVIEW=reviews/2026-09-16-econometrica-r7-independent
OUT=/tmp/nbo-r7-independent-replay
mkdir -p "$OUT"

python "$REVIEW/reviewer_author_replay.py" \
  --root . --output "$OUT/author_replay.json"

python "$REVIEW/reviewer_kernel_moments.py" \
  --root . --output "$OUT/kernel_moments.json"

python "$REVIEW/reviewer_spatial_checks.py" \
  --root . --shape 33,49 --all-corners \
  --output "$OUT/spatial_33x49.json"

python "$REVIEW/reviewer_spatial_checks.py" \
  --root . --shape 49,73 --all-corners \
  --output "$OUT/spatial_49x73.json"

python "$REVIEW/reviewer_spatial_checks.py" \
  --root . --shape 65,97 --all-corners \
  --cache-dir "$OUT/kernel-cache" \
  --output "$OUT/spatial_65x97.json"
```

The last command stores the same float64 sparse-kernel and reward entries in read-only memory-mapped NPY files. Allow several gigabytes of temporary disk space and run the large cases serially. An initial all-in-memory attempt at `65 x 97` was killed by this session's 4-GiB memory limit; the reported run completed with this disk-backed mode. This is a reviewer implementation constraint, not an allegation about the author's algorithm or a performance benchmark. No results from the incomplete attempt are used.

`--all-corners` evaluates the four corners and center of the declared rectangle. At each point, the program solves the two adjustment regimes, then constrains only the first portfolio sign to produce two class values. The no-adjustment regime restricts deliberate adjustment at every date. Later portfolio signs remain unrestricted. Both published common meshes are explicitly retained, giving 1,565 actions on every grid; frozen neural proposals are excluded identically. Calling the author's ordinary `include_neural=False` constructor would not retain this same union and is deliberately not used.

The sparse Bellman continuation is checked against the original positive weighted-gather implementation on a deterministic probe. Every selected policy is reevaluated by calling the author's transition and interpolation functions directly rather than the sparse Bellman path. This checks implementations; it does not independently validate the transition-law specification or prove a diffusion limit. The pointwise finer-grid results are not uniform regional certificates.

The moment program uses one interior state and a fixed consumption/portfolio action, checks that all raw branches survive, removes their common discount, and compares covariance before and after interpolation. It checks mean preservation and the exact interpolation variance-increment identity. The `129 x 193` entry in these diagnostics is **only a local moment calculation**, not a full Bellman solve on that grid. Temporal moment rows likewise do not rerun the previous review's full time-refinement economy.

The author-replay program replaces only the save hooks of the author's R7 small-model validation and primitive modules. The deposited decision coefficient arrays remain read-only. The resulting replay checks 96 small models, 480 parameter values, the primitive family, and the stored coefficient signs. It does not rebuild the full regional policy bank or rerun the autonomous author timing contest.

## Evidence format and interpretation

`diagnostic_results.json` is a compact extraction of the completed raw outputs generated by the commands above. It includes all 30 spatial regime/parameter/grid records, not just the corner that changes sign. Each spatial row gives `lambda`, `d`, the adjustment flag, the positive-class value, the nonpositive-class value, their difference, and the maximum selected-policy replay discrepancy. Kernel-moment rows identify both grid dimensions, date count, control, endpoint correlation, raw variance, interpolated variance, inflation factor, and mean error. The reproduction commands generate the fuller raw JSON including first actions, full local covariance matrices, and environment/timing fields.

Observed arithmetic discrepancies are consistency checks, not rigorous new value-error bounds. The author certificate's arithmetic allowance is relative to its original stored finite model. It must not be transferred without argument to a different grid, action target, or continuous-time model. The report does not infer that the local preference-variance distortion is the sole cause of the economic sign movement.

The replay summary also records which work was not rerun: historical neural training, the full author adaptive timing experiment, and the prior referee's matched neural-free regional construction. Those existing results remain available in their original directories and are separately attributed in the report.

## Provenance

The reviewed manuscript commit is `fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17`, with Git tree `cdc8e227881d5e95a8740c4f77298f73a0b9399d`. The downloaded source/evidence archive came from Actions run `35063710310`, artifact `10433863234`, and had SHA-256 `b0bcb8542760adffae90e3ffff7ad61d0fe5b49e0b93e0f66a05eeea170d51c2`. Reconstructing the final snapshot reproduced the exact reviewed tree. All 27 authored-source inventory entries matched and the tracked author-source diff remained empty after execution.

The new review branch is based on prior review commit `3b40e6813a2b56d88b454f5a164a648fb035d0f3`, so the original R7 report remains present. The new files are additive and confined to this directory. Program Git blob identities in `diagnostic_results.json` match the executed local program files byte for byte. SHA-256 identities of the author modules and coefficient inputs are also recorded there.
