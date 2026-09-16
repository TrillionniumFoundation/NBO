# R5 preservation and substantive-content map

Base: `11082cc5054e91d3b2ac27826705f374ca74bfae`, the complete R4 review branch.

No earlier manuscript, review, result, checkpoint, figure, bibliography, or program is deleted or overwritten. The root `REVISION_INDEX.md` is updated and its complete former contents retained under the historical R4 heading. New work is confined to the two R5 wrappers, `revisions/2026-09-16-r5/`, `replication/r5/`, and `.github/workflows/revision-r5.yml`. The build verifies changed paths against the base and refuses alterations outside this allowlist.

| Existing substantive material | R5 treatment |
|---|---|
| Original `ECTA.tex`, R2/R3/R4 sources and supplements | Preserved unchanged in their original paths |
| R4 exact separated policy-improvement proof | Main operators section and Supplement S.1 retained |
| Approximate ε/δ/κ/η theorem and continuous-time residual result | Main approximation section retained, supplemented by operational finite-contract certificate |
| Nonoptimal actor stationary point, viscosity counterexample, trace estimand | Main approximation section and Supplement S.2 retained |
| Stopped nonlinear preference diffusion, all controls/covariance, cardinal utility derivative, supersolution | Main preferences section and Supplement S.3 retained; changed-contract distinction added |
| Adjustment-effort theorem and approximate version | Retained; effort versus weighted charge stated and tested explicitly |
| Original neural policy tables, unfavorable residuals and deviations | Retained and followed by expanded-menu repair, occupation analysis, and contract transfer |
| Constrained neural resource model and original nine runs | Retained; same-checkpoint actor-free and full convex-quadratic comparisons added |
| Homothetic Merton/Epstein–Zin, domain and transversality arguments | Retained in main extensions and Supplement S.4 |
| Sophisticated temporal selves and beta separation | Retained in main extensions and Supplement S.5 |
| Reset capacity game | Preserved as a regression with its closed-form solution; persistent-capacity model added |
| R4 date-zero exploitability output | Original file unchanged; new all-date implementation, full arrays, and late-date negative control added |
| R4 neural weights and positive transition/resource source | Read as immutable inputs; hashes recorded |
| All previous referee reports and response letters | Inherited unchanged from review base |
| Introduction, abstract, conclusion | Rewritten to express the demonstrated contract-reuse and economic results; prior versions remain preserved |

R5 mathematical additions appear in `04b_contract_transfer.tex`, `S7_contract_proofs.tex`, and `S8_new_computation.tex`. R5 numerical tables are generated from executed JSON by `replication/r5/tables.py`.
