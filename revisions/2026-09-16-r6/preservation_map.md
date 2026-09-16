# R6 preservation and manuscript map

R6 starts from the R5 review commit `0d0e79a52e540bd0647801ce316f051d667c6797`. Every inherited tracked file is protected byte-for-byte except `REVISION_INDEX.md`, whose entire former content is retained below the R6 pointer. The root README is unchanged. The workflow and validator reject changes to old manuscript, review, code, data, weights, PDF, and log paths.

| Inherited content | Current R6 location | Treatment |
|---|---|---|
| Operator definition, approximate-operator theory and proofs | Main Sections in `02_operators`, `03_approximation`; Supplement S.1–S.2 | Preserved in full. |
| Endogenous preferences, admissibility, stopped boundary and verification | `04_preferences`; Supplement S.3 | Preserved in full. |
| Contract reduction, reward transfer, action separation and proofs | `04b_contract_transfer`; Supplement S.7 | Preserved; terminology clarified; exact scalar-OLS correspondence added. |
| Every R5 numerical table and historical actor/resource result | `05_computation` and all inherited `table_*.tex` / `r5_numbers.tex` | Retained. The original-reference crossover is explicitly separated from the stronger structural-QP comparison. |
| Recursive utility, temporal selves, persistent capacity and full-date deviations | `06_extensions`; Supplement S.4–S.5 and S.8 | Preserved in full with original finite/learned scope distinctions. |
| R4/R5 source provenance and deployment accounting | Supplement S.6, S.8 | Preserved; “authoritative R4 source record” clarifies historical status. |
| Introduction, abstract, conclusion and literature | R6 entry points, `01_introduction`, `07_conclusion`, `references` | Rewritten to integrate the additional results and exact comparator attribution, without deleting the substantive sections they introduce. Every prior bibliography entry remains. |
| New transition-law theorem, proof, algorithm and evidence | `04c_kernel_transfer`, `05b_incremental_evidence`, Supplement S.9 | Added. |
| New risk-class theorem, preference-option identity and matched experiment | `04d_risk_frontier`, `05b_incremental_evidence`, Supplement S.9 | Added. |

`output/validation.json` and `build_report.json` contain the executed historical-file count and byte comparison. The authoritative R6 includes actual main/supplement PDFs and readable LaTeX, not only archived source or a list of proposed edits. Earlier entry points remain historical manuscripts; their continued existence does not make them the R6 reading order.
