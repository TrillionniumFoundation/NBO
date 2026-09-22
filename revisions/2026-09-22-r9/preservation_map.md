# R9 preservation and provenance map

The exact inherited source is review commit `9749c3cf28f9438315b8f504a358bbe307ea89a5`. Its 556 tracked files are hashed in `inherited_manifest.json`. Validation compares every one against the current working tree, except that the stale root `REVISION_INDEX.md` is compared with its byte-identical archive at `archive/REVISION_INDEX_before_R9.md`. The current root index is the sole intentional replacement of an inherited path.

| Material | Unchanged source | R9 reading location |
|---|---|---|
| Latest report and reviewed-paper identification | `reviews/2026-09-22-econometrica-r8/` | Point-by-point R9 response |
| Complete R8 main paper, all numerical tables, and proofs | `revisions/2026-09-22-r8/paper/{main,numerics,proofs}.tex` and inputs | `SUPP_R9`, Part II |
| Complete R4 exposition and appendix | `revisions/2026-09-21-r4/paper/{main,appendix}.tex` | `SUPP_R9`, Part III |
| All six delivered R5 tables | `revisions/2026-09-21-r5/paper/table_{ndu,nonlinear,boundary,coupled,recursive,game}.tex` | `SUPP_R9`, Part IV |
| Merton derivation, nonlinear preference economy, control-selection cases, exit settlement, recursive utility, temporal selves, games, stochastic traces and counterexamples | Complete R8 and R4 source inputs above | Full retained supplement, not abridged summaries |
| Prior failed targets, mesh diagnostics, finite safeguards, manufactured-payoff tests, checkpoints, and earlier comparison outcomes | All corresponding R2–R8 source and results directories | Existing repository paths; historical interpretation retained in supplement |
| Original paper and earlier revision entry points | `ECTA.tex`, `ECTA_R2.tex`, `SUPP_R2.tex`, `ECTA_R8.tex`, `SUPP_R8.tex`, and existing review entries | Remain in repository unchanged |
| Stale R3 root index | Original bytes of `REVISION_INDEX.md` | R9 `archive/REVISION_INDEX_before_R9.md` |

R9 adds new wrappers, ordinary TeX sources, proofs, bibliography additions, replication programs, original-payoff certificates, comparison evidence, response, and manifests. The historical TeX sources are included directly, without rewriting their content. Historical section/theorem counters are reset at the part boundary for readability; hyperlink destinations are unique. Historical passages referring to a revision's “new” result remain historical claims, as explained in the supplement's reading guide.

The canonical current branch is `revision/econometrica-r9-constructive-certification-2026-09-22`. No historical review branch, R8 branch, or primary branch is advanced, deleted, or merged by this revision. Existing duplicate R8 referee/verified branches are left untouched; the new root index provides one canonical R9 pointer rather than destroying the review record.

The newly attempted wealth-sensitive fitting pilot is also retained. Its source, coefficients, computation logs, and `results/wealth_pilot_status.json` are explicitly separated from validated numerical evidence. It is not used in a bound or presented as a successful refinement. The full frozen external comparison retains all tuning and holdout outcomes, including the independent baseline's superior performance.
