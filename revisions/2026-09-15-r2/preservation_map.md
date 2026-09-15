# R1-to-R2 preservation and modification map

| Historical material | R2 treatment | Reason |
|---|---|---|
| `ECTA.tex` | Preserved byte-for-byte | Audit trail and source identity for R1 findings |
| `supp.tex` | Preserved byte-for-byte | Historical time-inconsistency/game formulations |
| `ECTA_R2.tex` | New authoritative main manuscript | Separated NBO algorithm, corrected theory, recalculated anchors, scoped evidence |
| `SUPP_R2.tex` | New authoritative standalone supplement | Extended-HJB and player-specific game updates; no composite Nash loss |
| `reviews/2026-09-15-econometrica-r1/` | Preserved | Latest referee report and manifest |
| Embedded `.dat` arrays in historical TeX | Retained only as historical/negative-control inputs | No run-level provenance; never used as R2 evidence |
| Merton target values | Corrected to `.75` and `.04125` under declared stationary interpretation | Arithmetic and horizon correction |
| Epstein--Zin aggregator | Replaced by canonical difference form with domain restriction | Restores positive consumption marginal utility and value-domain validity |
| Composite loss proposition | Removed from authoritative R2 method; finite counterexample retained | R1 counterexample is decisive |
| Viscosity claim | Replaced by conditional consistency plus exit-time negative diagnostic | Residual minimization does not select viscosity solutions |
| Adam/TTSA claim | Conditional asymptotic statement separated from finite-step evidence | Actual implementation uses constant-step optimizer |
| NDU identification language | Recast as preference-formation comparative statics | No observation model/rank condition in the manuscript |
| Time-inconsistency and game extensions | Unified around one-shot deviations and detached rivals | Original main/supplement formulations were inconsistent |
