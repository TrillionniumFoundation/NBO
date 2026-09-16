# R7 execution summary

These records are generated from an actual run of the deposited code. They do not establish publication acceptance, a diffusion approximation theorem, or neural dominance.

## Matched full-model comparison

| d | anchors | chord bound | local-count bound | rectangular bound | chord total s | count total s |
|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 19 | 0.0009045733003105738 | 0.00073384636746332 | 0.01876078675071147 | 53.344426 | 121.399216 |
| 0.5 | 18 | 0.0008998289604379428 | 0.0006851026198662069 | 0.01714986664439822 | 51.014746 | 114.426225 |
| 0.5 | 6 | 0.006984583911619269 | 0.003381319761768031 | 0.04272528033957268 | 19.264258 | 37.521687 |
| 0.5 | 10 | 0.003273356965230678 | 0.002024601140089288 | 0.02556377241100372 | 29.790984 | 62.744128 |
| 1.0 | 17 | 0.0009414120278261606 | 0.0004357448654037643 | 0.01508291406723605 | 47.043047 | 105.266586 |

All compared arms include setup, anchor optimization, policy evaluation, local restriction, upper construction and certificate subdivision. One pass, one machine, one thread. The 51 original intervals reproduce the sixth-round comparison; the two coarser banks are additional.

## Autonomous refinement

- chord: 18 anchors; bound 0.0008998289604379428; total 73.405311 s; 858 upper kernel applications, including rejected parents.
- count: 11 anchors; bound 0.0009244712735729799; total 115.376866 s; 1330 upper kernel applications, including rejected parents.
- cascade: 11 anchors; bound 0.0009244712735729799; total 127.731816 s; 1614 upper kernel applications, including rejected parents.

## Joint economic decision

Entire rectangle lambda in [0, 0.25], d in [0.4, 0.45], at (u,X)=(2,1.25), k=2. Minimum adjusted positive-class advantage: 6.888728805714623e-05. Minimum fixed-adjustment nonpositive-class advantage: 5.299365560501097e-05. Minimum relative option: 0.0001218809436621572.

Per-class a priori floating-point allowance: 3.797650002493679e-09; scope is the stored finite target, not quadrature construction or diffusion discretization. Eight corner optimizations, sixteen class policies, eight count upper constructions. All tensor coefficients are deposited.

## Primitive family

For all p in [0.06,0.10], k in [20,80], the computed exact-formula lower estimate for the relative option is 0.00186682876524398; the manuscript uses the conservatively rounded 0.00186 bound. The implied threshold shift exceeds 0.00372. This is an analytical two-stage specialization, not a calibration replacing the full economy.

## Validation scope

Independent small-model recursions test count dominance, finite-horizon operation counts, upper validity, and the total coefficient-error bound. The mathematical proofs establish the general statements. Coefficient-only replay verifies the deposited decision intervals. Historical R4--R6 results are preserved inputs; the R7 run does not claim to retrain all historical networks.
