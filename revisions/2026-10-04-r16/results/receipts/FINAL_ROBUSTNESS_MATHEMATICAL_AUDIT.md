# Final economic-robustness mathematical attestation

**PASS — 8,164 independent checks.** Auditor: `r16_math`. Report SHA-256: `2b675db41f2827d987c3ceae3e3ee01627a0e80228e0b9f54f85d2922d7e17fd`. Numerical source: `21d4cc505202686382b5b45d5f710ffdc12f889c`. Evidence commit: `0b0b113b8c249d916daf0da22808180ce15caa2f`, tree `f508f30d92f1a117131d555bf2926c71755013c8`. These identities agree with the separately recorded remote-evidence and complete-report replay receipts.

## Scope and arithmetic

The audit covers all 648 two-sided events: 576 conditional-stream intervals and 72 complete finite-stream averages. It also checks the 288 retained original-transfer endpoints on those same events. All 256 paired numerical allowances include the ideal continuous-time transfer, both complete statistic-error accounts, both path-arithmetic terms, and the direct-subtraction allowance. Their range, tail, moments, sample size, and probability allocation remain unchanged by the deterministic transfer refinement.

An independent 100-digit calculation checks every empirical-Bernstein formula and endpoint using neighboring binary64 enclosures of the published exact-moment summaries. Exact rational calculations check the within/between pooled-variance identity, outward mean stratum allowances, paired numerical sums, full-adapted-class regret subtraction, and every final target-attainment fraction. The eight declared training streams are exhaustively retained; each conditional event has 8,192 independent confirmation paths and each pooled event has 65,536. The family remains 0.01 over 648 events. Cross-method common innovations do not create additional independent samples.

The frozen collector separately replays the raw arrays. This post-execution audit checks protected published summaries and does not claim a second raw-bank replay or a new proof of the previously independently audited general-horizon transfer.

## Economic interpretation

All forty pooled method-versus-reference intervals are positive. NBO improves on the same analytical reference in every one of the eight economic cells:

| Continuous-diffusion design | Dimension | NBO gain interval, rounded outward | Full-adapted-class regret upper bound |
| --- | ---: | ---: | ---: |
| high | 10 | [0.00090811, 0.00163115] | 0.02600579 |
| high | 50 | [0.00092700, 0.00176748] | 0.03687272 |
| low | 10 | [0.00119640, 0.00173056] | 0.02040579 |
| low | 50 | [0.00128976, 0.00191782] | 0.02976042 |
| long | 10 | [0.00687158, 0.01012253] | 0.19127177 |
| long | 50 | [0.00629858, 0.01024458] | 0.29309644 |
| stress | 10 | [0.00461613, 0.00684939] | 0.17618124 |
| stress | 50 | [0.00611926, 0.00876912] | 0.24797683 |

Only two of the thirty-two pooled direct NBO comparisons certify economic superiority at the unchanged margin 0.0001: low-volatility, dimension 50, against HJB greedy, with interval [0.00033413, 0.00069663], and against HJB distilled, with interval [0.00034063, 0.00070305]. The remaining thirty direct comparisons are unresolved. None establishes practical equivalence, and none establishes a material advantage over Raw or Direct policy in this continuous-diffusion family. All 320 policy outputs are retained, with zero fallbacks.

Positive reference gains do not establish near optimality in the full adapted policy class. The displayed regret bounds remain much larger than 0.0001. The continuous-diffusion longer-horizon design has T=2; the separate finite-menu longer-horizon design has T=4. The stress design changes several economic primitives, initial heterogeneity, and the actor radius jointly, so it has no single-primitive causal interpretation. HJB collocation diagnostics are not uniform residual or global value-error certificates. Statements about the eight-stream distribution remain conditional on that declared finite population.

## Independent reproduction

Program: `revisions/2026-10-04-r16/code/audit_final_robustness_report.py`, SHA-256 `495974a36a064f98a78d4cedc352c7765f73c5cfeaa1fdee3bea9f8c32928d17`. It uses only the Python standard library, imports no estimator or inference implementation, and performs no fit or random draw. A portable rerun returned identical mathematical results.

```sh
python revisions/2026-10-04-r16/code/audit_final_robustness_report.py \
  --root . --evidence-commit 0b0b113b8c249d916daf0da22808180ce15caa2f \
  --out /tmp/final-robustness-independent-audit.json
```

Full check counts, exact account hashes and scope qualifications are retained in `FINAL_ROBUSTNESS_MATHEMATICAL_AUDIT.json`. No frozen scientific source, observation, statistical allocation, or economic margin was changed.
