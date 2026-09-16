# R7 advisory referee review — 16 September 2026

Read [referee_report.md](referee_report.md) first. The recommendation is **reject in its present form for Econometrica**. This is an owner-commissioned advisory review, not a journal appointment or editorial decision.

Reviewed manuscript: `fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17` on `revision/econometrica-r7-2026-09-16`. Review branch: `review/econometrica-r7-2026-09-16-fbfbf90`, created from that exact commit. Only this new review directory is added; manuscript, author outputs, historical reports, main, and revision branches are not edited.

## Main findings

R7 genuinely repairs the matched comparison, supplies a positive autonomous compression result, adds a primitive option inequality, and certifies a joint-region decision for its eight-date finite target. The report explicitly credits these changes.

The new reviewer experiments establish two distinct facts. First, removing all three neural proposals from the feasible lower-policy bank while retaining the original full-target upper tensors still certifies the whole advertised opposite-ranking region. Second, a common-menu temporal sensitivity calculation changes the non-adjusting class difference at `(lambda,d)=(0.25,0.45)` from `-5.300125090501595e-5` at eight dates to `+5.312359482567697e-5` at sixteen. The latter is a nearby finite-target diagnostic, not a refutation of the eight-date certificate and not a diffusion convergence theorem.

The other major concerns are the generality of the computational frontier and the missing explanatory connection between the primitive lottery result and the stopped economy. Each finding in the report identifies manuscript locations, evidence, limitations, and the substantive response needed.

## Files and evidence classes

`diagnostic_results.json` records the author-suite replay, matched neural-free regional bounds, and all 15 completed temporal parameter-point comparisons with both adjustment regimes. It distinguishes author-written tests rerun by the reviewer from reviewer-written extensions. `review_manifest.json` records provenance and file hashes.

`reviewer_r7_checks.py` reruns the author's validation, primitive calculation, and coefficient-only replay, then executes the reviewer-written neural-free masked optimization. It reuses the author's kernels and independently reevaluates policies through their selected-policy arithmetic path. It keeps the full 1,565-action union mesh and retains the original 1,568-action upper target. Its complete runtime JSON also includes corner values, controls, replay errors, and the primitive checks.

`reviewer_time_refinement.py` uses the same union mesh at each horizon, excludes neural proposals in both regimes, and changes only the number of dates and the associated time step. Its runtime JSON records individual class values and focal controls, not just differences. A completed horizon has ten records: five parameter points times two adjustment regimes. An `in_progress` entry is a partial run and is not a completed result.

## Reproduction

From the repository root on this review branch, use an environment with NumPy, SciPy, and PyTorch. The actual reviewer environment was Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, and PyTorch 2.10.0+cpu; numerical execution was single-threaded. The scripts import historical author modules but do not train neural networks. Full finite-target kernels require substantial memory, so run one temporal horizon per process.

```bash
python reviews/2026-09-16-econometrica-r7/reviewer_r7_checks.py \
  --repo . --output /tmp/nbo-r7-review-checks.json

for h in 4 8 16; do
  python reviews/2026-09-16-econometrica-r7/reviewer_time_refinement.py \
    --repo . --horizons "$h" --output "/tmp/nbo-r7-time-${h}.json"
done
```

The temporal program defaults to eight dates; the report uses the explicitly completed four-, eight-, and sixteen-date runs. The initial multi-horizon invocation completed four and eight dates but was interrupted during sixteen; sixteen was then completed in a separate invocation. No 32-date result is claimed. The deposited default was narrowed to eight for safer one-horizon invocation; no numerical recursion was changed.

Use output paths outside the author directories and do not run Python with `-O`, since assertions check source hashes and numerical consistency. The matched audit verifies all 27 R7 authored-source inventory entries before and after execution. A final local tracked-file comparison also found no author-file changes. The audit does not replace a full historical training reproduction, a fresh rerun of all author timing experiments, a directed-rounding proof, or a joint spatial-temporal-action convergence study.

## 中文摘要

本轮审阅对象是 R7，而非 main 的旧稿。审稿意见认可 R7 已完成的实质修复，但仍建议现稿不予接收。新增的核心证据是：保留原完整目标上界，删除神经动作后仍能认证整个区域的风险反转；而在相同公共动作集和状态网格下，将日期数从 8 增至 16，会使区域右上角无调整组的风险差值变号。报告明确区分有限模型证明有效性、经济稳健性和方法贡献，未将数值敏感性误写成对原定理的反例。
