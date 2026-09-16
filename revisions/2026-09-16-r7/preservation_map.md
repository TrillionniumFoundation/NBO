# Preservation and change map

Base review: `10a7cbee28de5126d844dea9eae8c36c5cda9e9b`. Its parent is the complete R6 paper, `24011fef6da09bc05dc79946a3c1779e1fe7d8a8`.

The R7 branch is a descendant of the review branch. No historical file is deleted or overwritten, except that `REVISION_INDEX.md` receives a new prefatory entry with its old contents retained. `build_report.py` verifies all protected tracked paths against the review base. The initial local source reconstruction independently matched the R6 Git tree `36709be3522fb7e29e7bfc45abfc6305a84b203d`.

| Material | R7 treatment |
|---|---|
| Operator definitions, continuous-time formulation, approximation and policy-improvement analysis | Same R6 source inputs `02_operators.tex`, `03_approximation.tex` |
| Stopped preference economy and all original primitives | Same `04_preferences.tex` input |
| Reward transfer, scalar OLS, independent policy features, sign exclusions | Same `04b_contract_transfer.tex` and original computation; OLS comparison retained |
| Corrected transition chord, residual supersolutions, Bernstein policy evaluation and switching | Same `04c_kernel_transfer.tex`, followed by new comparison and total-error results |
| Duration–effort identity, nested adjustment option, direct threshold scope | Same `04d_risk_frontier.tex`, followed by primitive and tensor-certificate results |
| Original numerical tests and adverse learned-policy comparisons | Same `05_computation.tex`; all tables retained |
| Structural QP, mesh-only bank, old transition table and mechanism tables | New prose copy `05b_incremental_evidence.tex` still inputs the unchanged R6 tables; global/adaptive inference corrected at the table |
| Recursive utility, temporal selves and persistent capacity competition | Same `06_extensions.tex`; no economic extension removed |
| Historical supplement S.1–S.9 | Same source inputs, followed by S.10–S.11 |
| Introduction, conclusion and related literature | New R7 copies; preserve the economic problem and adverse comparisons while integrating the new results |
| References | All R6 entries retained; Quatmann et al. (2016) added |
| Journal class/configuration, historical figures and checkpoints | Byte-identical inputs |
| R0–R6 revisions, responses, reviewer diagnostics and results | Preserved on the descendant branch; not regenerated or rebranded as R7 experiments |

Materials used in preparing the response include the full R6 report, its comparison proof and execution record, the complete R6 manuscript and supplement, the R6 response to R5, the historical R4/R5 economic and solver specifications, the full R6 transition and mechanism implementations, and their numerical outputs. Preservation does not imply a fresh rederivation or retraining of every historical extension.

The active main manuscript is not merely an R7 appendix stapled to an unspecified earlier version: its root entry point specifies every included section, including revised introduction, comparative interpretation, new theory, new results, conclusion, and complete references. The supplement similarly contains the complete inherited proofs plus new proofs. No original scientific content is hidden by changing the compilation target.
