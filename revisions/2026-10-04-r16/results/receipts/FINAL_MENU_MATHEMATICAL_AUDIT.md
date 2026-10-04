# Final continuation-menu mathematical attestation

**PASS.** Auditor: `r16_math`. This independent audit is bound to the final menu report, with SHA-256 `2a729aff851dc7060beb18e7fb8c1e0e9bb94d2b7d239c53f15cdd66a584cb63`, numerical source `503a724817899105a78f8c2fd516f417efb6b483`, and evidence commit `103b6717dac939cb9cd18876f56d889c9e2a751d`. The audit does not modify any frozen scientific source or add a statistical family.

## Arithmetic and completeness

All 128 scalar records passed exact-rational reconstruction from the protected payoff interval through the secant, derivative interval, whole-interval quadratic maximization, and the implemented action-rounding allowance. Both interval boundaries and every feasible interior stationary point were checked. The empirical-Bernstein formula and endpoints were separately checked at 100-digit precision using one-binary64-neighbor enclosures for the report’s serialized exact moments. All 128 curvature records equal their corresponding pre-data deterministic accounts. Sampling uses 65,536 independent antithetic pairs per scalar event, with the original 0.002/128 family allocation.

All 216 primary interval records have the declared 3,145,728 independent-pair observations and the 0.018/216 allocation. All economic flags and all 96 direct-comparison aggregates were independently recomputed. The source-bound collector separately reconstructed every endpoint from the stored raw arrays; this audit checks the final protected summaries and does not claim a second raw-bank download.

## Scalar results and interpretation

Eighty of 128 scalar statements certify a gap at most 0.0001. The five successful calibration/dimension cells certify all sixteen streams. The class contains every continuous scalar action in the fixed reference ±0.1 segment, applied uniformly across sectors at the first stored state and central task, with the same future reference. It does not include arbitrary vector actions, future adapted policies, or continuous-time controls.

| Calibration / dimension | Certified streams | Largest recorded upper bound |
| --- | ---: | ---: |
| original_low_d10 | 16/16 | 1.101139221884191e-07 |
| original_low_d50 | 16/16 | 3.4542419596365313e-07 |
| quarterly_reuse_d10 | 16/16 | 2.3756146893838156e-06 |
| quarterly_reuse_d50 | 16/16 | 1.4020626521047468e-05 |
| long_reuse_d10 | 0/16 | 0.045458771026785534 |
| long_reuse_d50 | 0/16 | 0.19631679293390536 |
| untouched_intermediate_d10 | 16/16 | 2.34062993225963e-06 |
| untouched_intermediate_d50 | 0/16 | 0.00028452305937202885 |

The remaining forty-eight statements give valid wider upper bounds. They do not establish a lower bound on the true policy gap. Likewise, a nonpositive proved strong-concavity lower bound does not establish that the true objective is nonconcave. The parameter intervals, sample sizes and confidence allocations remain unchanged.

## Economic comparison categories

| Comparator | Positive | Materially superior | Equivalent | Positive and equivalent |
| --- | ---: | ---: | ---: | ---: |
| dpo_actor | 16 | 4 | 14 | 11 |
| raw_actor | 19 | 7 | 14 | 12 |
| raw_saa | 0 | 0 | 16 | 0 |
| vector_costate | 22 | 9 | 15 | 13 |

Each comparator has twenty-four simultaneous direct comparisons. A protected interval strictly above zero can still lie entirely within the economic-equivalence band, so these columns must not be added as mutually exclusive successes. Negative differences can likewise be economically equivalent: the counts are 1 for Raw actor, 2 for DPO, and 11 for cached sample-average Raw. No observed endpoint lies exactly at zero or ±0.0001, so the source’s strict decision fields and the report’s closed-boundary aggregate convention agree for every reported comparison.

The learned-critic variance identity remains conditional on a fixed gradient dictionary independent of the label array. The observed nonlinear comparisons do not establish that the trained network equals that projection or isolate a causal reduction in critic mean-squared error.

Full check counts, scope qualifications, exact data hashes and per-cell values are retained in `FINAL_MENU_MATHEMATICAL_AUDIT.json`.

## Independent reproduction

The post-execution audit program is retained as `revisions/2026-10-04-r16/code/audit_final_menu_report.py` (SHA-256 `2c0f6425e5e40c0a74a602c53e744a299e86a7bff5ba972944e72b7ec0fb7a12`). It uses only the Python standard library and imports no estimator or inference implementation. The portable rerun passed all 4,250 checks with every mathematical result unchanged. From the repository root:

```sh
python revisions/2026-10-04-r16/code/audit_final_menu_report.py \
  --root . --out /tmp/final-menu-independent-audit.json
```

Explicit `--report`, `--protocol`, and `--power` arguments support an extracted evidence bundle. The program was added after the numerical experiment; it performs no fit, random draw, or new statistical comparison and does not change the frozen scientific source.
