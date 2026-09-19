# Referee Report — Neural Bellman Operators, Revision R17

**Journal standard used:** Econometrica-style external assessment. This is an owner-commissioned advisory report, not an official editorial decision and not a representation of appointment by Econometrica.

**Date:** 19 September 2026

**Repository:** TrillionniumFoundation/NBO

**Reviewed revision branch:** revision/econometrica-r17-full-response-2026-09-19

**Frozen reviewed SHA:** 80c8a743efb5ff60826c15b0bc3369965957af68

**Immediate prior scientific branch:** revision/econometrica-r16-development-2026-09-19

**Immediate prior scientific SHA:** 5dbff2e29c05dd0eeef48db4fd34a6d80260d0ad

**Immediate prior report:** reviews/2026-09-19-econometrica-r16-harsh/referee_report.md

**Review branch:** review/econometrica-r17-harsh-2026-09-19

---

## Recommendation

**Reject in the present form. R17 is not a new scientific revision and, despite the branch name “full-response,” it contains no scientific response to the R16 referee report.**

The Git record is dispositive.

Relative to R16, R17 is one commit ahead and changes exactly one file:

- reviews/2026-09-19-econometrica-r16-harsh/referee_report.md

The R17 head commit is titled:

> Add harsh Econometrica-style referee report for R16

There is no R17 manuscript, no R17 supplement, no R17 response letter, no R17 bibliography, no new theorem, no new proof, no new economic model, no new table, no new numerical output, no new replication evidence, no new release manifest, and no new referee-facing index.

This is not a matter of an incomplete response. There is no response.

The branch is therefore a transport mechanism for the previous referee report, not a paper revision.

A journal referee should not infer unpublished or uncommitted scientific work from a branch name. I evaluate only the frozen repository object at the SHA above.

---

# 1. The branch name and the deposited object are inconsistent

The reviewed branch is named:

revision/econometrica-r17-full-response-2026-09-19

Nothing in the scientific tree corresponds to that description.

The branch contains no:

- ECTA_R17.tex;
- SUPP_R17.tex;
- RESPONSE_R17.tex;
- R17 manuscript directory;
- R17 release PDF;
- R17 release manifest;
- R17 response-to-referee document;
- R17 evidence package; or
- R17 validation receipt.

The sole R17 delta is the R16 referee report.

Calling this a “full response” creates exactly the ambiguity that the previous reports asked the repository to eliminate.

For an Econometrica-style revision cycle, the revision number should advance only when the scientific object advances.

**Required response:** do not create R18 merely to move this report. The next revision number should be attached to an actual frozen paper release.

---

# 2. R17 does not answer any R16 objection

The R16 report required a complete and auditable scientific revision before another substantive review.

R17 answers none of those requirements because it does not modify any scientific file.

The following remain unchanged:

| R16 requirement | R17 status |
|---|---|
| Complete current manuscript | Not addressed |
| Complete current supplement | Not addressed |
| Point-by-point response | Not addressed |
| Current bibliography | Not addressed |
| Missing numerical tables | Not addressed |
| Release manifest | Not addressed |
| Build receipt | Not addressed |
| Scientific validation command | Not addressed |
| Continuous-model bridge | Not addressed |
| Neural computational frontier or reframing | Not addressed |
| Distinct novelty theorem | Not addressed |
| Enforcement evidence | Not addressed |
| Institutional robustness evidence | Not addressed |
| Clear current-paper identity | Not addressed |

This is an exact consequence of the zero scientific delta.

The correct inference is not “the authors attempted these items but fell short.” The correct inference is “none of these items was submitted in R17.”

---

# 3. The repository still says R14 is the current referee-facing paper

At the frozen R17 SHA, the repository-level entry points still identify R14 as current.

README.md begins:

**Neural Bellman Operators — Revision R14**

It states:

**Current paper: Neural Bellman Operators: Certified Response Sets and Operating Commitments (September 19, 2026).**

It directs the reader to:

- revisions/2026-09-19-r14-referee-response/ECTA_R14.pdf;
- revisions/2026-09-19-r14-referee-response/SUPP_R14.pdf;
- revisions/2026-09-19-r14-referee-response/RESPONSE_R14.pdf; and
- revisions/2026-09-19-r14-referee-response/COMPENDIUM_R14.pdf.

REVISION_INDEX.md likewise begins:

**Current referee-facing revision: R14 — September 19, 2026**

The editable root entry points remain ECTA_R14.tex, SUPP_R14.tex, RESPONSE_R14.tex, and COMPENDIUM_R14.tex.

This is internally coherent for R14.

It is not coherent with a branch labeled R17 full response.

A referee cannot be asked to review R17 while the repository itself says the current paper is R14 and provides no R17 paper.

**Required response:** the next actual revision must update the README, revision index, manuscript entry point, supplement, response, release manifest, and validation command atomically in one frozen scientific release.

---

# 4. The incomplete R15 development manuscript remains incomplete

The R15 development directory is still present under:

revisions/2026-09-19-r15-referee-response/paper/

The substantive fragments that exist include:

- introduction.tex;
- information.tex;
- operator_bridge.tex; and
- enforcement.tex.

The following expected integration files are still absent at R17:

- paper/main.tex;
- paper/response.tex;
- paper/references.tex.

There is therefore still no complete R15 manuscript graph that a referee can compile and read as the successor to R14.

The R15 fragments are scientifically meaningful development notes, but they are not a deposited paper.

This matters because the fragments change concepts that must be checked globally:

- response-set semantics;
- exact versus near-optimal behavior;
- occupancy representations;
- open mandate attainability;
- enforcement thresholds;
- continuous-fee comparisons;
- operator-to-certificate logic;
- and continuous-state verification.

Without a single integrated manuscript, one cannot verify consistency of definitions, assumptions, theorem numbering, citations, cross-references, or economic interpretation.

R17 does not integrate them.

---

# 5. The three R15 tables referenced by the scientific text remain absent

Three explicit TeX inputs used by the R15 development fragments still do not exist:

- table_repeated_proposals.tex;
- table_enforcement.tex;
- table_continuous_institutions.tex.

These are not decorative tables.

They are invoked precisely where the R15 text makes quantitative claims about:

- repeated neural proposals;
- action and horizon scaling;
- matched nonneural controls;
- initial-state enforcement thresholds;
- uniform enforcement thresholds;
- zero-surrender comparisons;
- fee incidence;
- capacity curvature;
- enforcement efficiency; and
- continuous institutional counterfactuals.

The prose cannot substitute for the missing evidence.

The current R17 branch supplies none of the missing tables and none of the generation or validation package required to support them.

For a computational paper, a numerical statement is not referee-ready merely because a number appears in prose.

**Required response:** each quantitative claim in the next scientific release must be bound to committed code, machine-readable output, target identity, seeds where relevant, environment, independent check, rendered table source, and manuscript location.

---

# 6. The continuous-model-to-finite-target bridge remains scientifically unresolved

This is still the most important scientific issue.

The paper derives economic interpretation from a continuous stopped-control model while its strongest deposited certificates are attached to a finite stored target.

The R15 development text improves the conceptual separation. In operator_bridge.tex it explicitly introduces a continuous Bellman-barrier route and correctly states that sampled residuals are not uniform verification.

But the same text also explicitly concedes:

**“The deposited settlement results do not yet include numerical continuous barriers satisfying a decision-separating budget.”**

That sentence remains true at R17.

No R17 scientific file changes it.

There is still no deposited numerical object that jointly closes:

- the continuous action supremum;
- derivative error;
- interpolation error;
- stopping and obstacle error;
- terminal and boundary error;
- constructor discrepancy;
- state discretization;
- action discretization;
- and decision-margin preservation.

The paper therefore continues to have two distinct objects:

1. a continuous economic model supplying interpretation; and
2. a finite target supplying certified numerical statements.

A theorem explaining how a bridge would work is not itself a numerical bridge for the reported economy.

For Econometrica, the paper must either execute the bridge at the precision needed by the economic conclusions or sharply redefine the finite target as the economic model being studied.

A certification claim cannot borrow interpretation from the continuous model and rigor from the finite model while leaving their quantitative relationship open.

---

# 7. The title-level neural claim remains stronger than the evidence

The title remains **Neural Bellman Operators**.

The current evidence does not establish that neural approximation is the economically or computationally essential part of the method.

The R15 operator-bridge development text itself is unusually candid:

- the experiments have two state variables;
- they are not a state-dimension experiment;
- exact dynamic programming remains decisive at the reported sizes;
- the neural method has substantial failures;
- and a demonstrated state-dimension or end-to-end neural computational advantage would require another experiment.

Those limitations are scientifically responsible.

They also weaken the title-level claim.

The certification results apply to trial values and independently checked policies. The economic response-set arguments do not become specifically neural merely because a neural network is one source of proposals.

A top-journal computational contribution needs the method identity and the evidence to match.

There are two acceptable directions:

### Direction A: make neurality essential

Demonstrate a matched regime in which:

- state representation becomes the bottleneck;
- exact or standard nonneural methods become materially costly;
- neural proposals improve the feasible end-to-end frontier;
- certification remains independent;
- failure rates are reported;
- and total wall time, memory, teacher cost, training cost, evaluation cost, and verification cost are counted.

### Direction B: make neurality secondary

Present the central contribution as certified dynamic response information / contract choice, with neural approximation as one proposal mechanism among several.

R17 does neither because it changes no paper text.

---

# 8. The novelty statement still needs a theorem-level separation from standard machinery

The strongest conceptual pieces in the R15 development material are:

- finite-query response sets;
- occupancy-based near-optimal response characterization;
- directed reward queries;
- support-function calculations;
- decision-directed error charges;
- whole-interval response graphs;
- and enforcement frontiers.

These are potentially useful.

But at present the paper still does not isolate sharply enough what is new relative to established combinations of:

- occupancy-measure linear programming;
- performance-difference identities;
- Lagrangian duality;
- inverse optimization;
- revealed-preference style inequalities;
- support functions and robust optimization;
- Bellman monotonicity;
- obstacle comparison;
- and numerical verification.

Econometrica does not require every mathematical ingredient to be new. It does require the paper's main theorem-level contribution to be economically consequential and intellectually distinct.

The current development text often shows how known tools can be assembled into a careful certificate. That is valuable engineering and methodology.

It is not yet obvious that the main general theorem is stronger than that synthesis.

The most promising route remains a genuine information-design result:

- characterize which value queries are sufficient for a target response functional;
- prove necessity or lower bounds;
- compare adaptive and nonadaptive query designs;
- characterize minimax query complexity;
- or show how dynamic structure changes the information requirement.

That would turn “directed queries are useful” into a theorem about the economics of information acquisition.

R17 adds no such result.

---

# 9. The enforcement contribution is promising but still not deposited as a complete result

The R15 enforcement fragment is the strongest economic reframing in the development tree.

It distinguishes:

- an initial-state surrender-elimination threshold;
- a uniform all-live-state enforcement threshold;
- and a purchaser comparison under binding participation.

It also avoids a weak narrative based only on a coarse contract menu.

That is progress in the development material.

But it is not yet a complete revision.

First, the enforcement table it explicitly inputs is absent.

Second, the theorem is not integrated into a complete current manuscript and supplement.

Third, the text must maintain a single consistent convention for:

- attained versus nonattained suprema;
- exact responses versus eta-responses;
- open positive mandates;
- ties at the threshold;
- randomized versus deterministic policies;
- legal fee ceilings;
- and the distinction between initial-state and uniform implementation.

Fourth, the continuous-time sentence inherits the unresolved continuous verification problem.

Fifth, the institutional counterfactual section again invokes an absent table.

The economic idea deserves a full release.

R17 does not supply one.

---

# 10. R17 makes the revision-history problem worse

There is now a recurring pattern:

- a scientific development branch is created;
- a referee report is deposited;
- a new revision branch is created;
- but the new branch may contain only preservation machinery or the prior referee report;
- while the repository's authoritative current paper remains an older revision.

This creates revision-number inflation without scientific revision.

That is not merely cosmetic.

It makes it harder to establish:

- which paper a report evaluated;
- which report a revision answered;
- which SHA is a scientific release;
- which files are authoritative;
- and whether a later branch contains new science or only process artifacts.

The repository has unusually good provenance ambitions, but the current branch discipline undermines them.

**Required response:** separate the two namespaces rigorously.

Use revision/... only for a complete scientific release.

Use review/... only for referee reports.

Use archival or preservation branches for provenance-only changes.

Do not increment the scientific revision number for a branch whose scientific delta is zero.

---

# 11. Minimum standard before another substantive Econometrica-style review

I would not conduct another full scientific rereview until the repository contains all of the following in one frozen revision:

1. **One complete main manuscript.** No reconstruction from development fragments.
2. **One complete supplement.** All proofs for current claims.
3. **One point-by-point response.** Each R16/R17 objection mapped to an actual change.
4. **One complete bibliography.** All current citations resolve.
5. **All referenced tables and figures.** No missing TeX inputs.
6. **All generating numerical evidence.** Code, machine-readable outputs, seeds, hashes, environment, and independent checks.
7. **One immutable release manifest.** It must bind manuscript, supplement, code, numerical targets, tables, and PDFs.
8. **One current referee-facing README.** It must name the reviewed branch and release object unambiguously.
9. **One current revision index.** It must not say R14 is current if the submitted paper is R18 or later.
10. **One scientific validation command.** It must verify, not merely preserve, the release.
11. **A resolved model-scope choice.** Execute a quantitative continuous bridge or define the finite target as the model.
12. **A resolved method-scope choice.** Demonstrate neural necessity or demote neurality from the central claim.
13. **A theorem-level novelty statement.** Distinguish the central result from standard occupancy, duality, inverse-optimization, and verification machinery.
14. **A complete enforcement result.** Integrate assumptions, proofs, evidence, and institutional scope.
15. **A nonzero scientific delta.** A new review branch or copied referee report is not a revision.

Until these conditions are satisfied, repeated rereview does not generate new information.

---

# 12. Evidence reviewed

This report freezes:

80c8a743efb5ff60826c15b0bc3369965957af68

on:

revision/econometrica-r17-full-response-2026-09-19

The R17 head commit is:

**Add harsh Econometrica-style referee report for R16**

I compared R17 directly with:

revision/econometrica-r16-development-2026-09-19

at:

5dbff2e29c05dd0eeef48db4fd34a6d80260d0ad

The comparison reports one commit and one changed file, namely:

reviews/2026-09-19-econometrica-r16-harsh/referee_report.md

I also inspected at the frozen R17 state:

- README.md;
- REVISION_INDEX.md;
- ECTA_R14.tex;
- SUPP_R14.tex;
- RESPONSE_R14.tex;
- COMPENDIUM_R14.tex;
- reviews/2026-09-19-econometrica-r16-harsh/referee_report.md;
- revisions/2026-09-19-r15-referee-response/paper/introduction.tex;
- revisions/2026-09-19-r15-referee-response/paper/information.tex;
- revisions/2026-09-19-r15-referee-response/paper/operator_bridge.tex; and
- revisions/2026-09-19-r15-referee-response/paper/enforcement.tex.

I separately checked that the following files do not exist at the frozen R17 state:

- revisions/2026-09-19-r15-referee-response/paper/main.tex;
- revisions/2026-09-19-r15-referee-response/paper/response.tex;
- revisions/2026-09-19-r15-referee-response/paper/references.tex;
- revisions/2026-09-19-r15-referee-response/paper/table_repeated_proposals.tex;
- revisions/2026-09-19-r15-referee-response/paper/table_enforcement.tex;
- revisions/2026-09-19-r15-referee-response/paper/table_continuous_institutions.tex;
- ECTA_R17.tex;
- SUPP_R17.tex; and
- RESPONSE_R17.tex.

I do not infer any uncommitted work, unpublished tables, local PDFs, intended future integration, or external scientific artifacts.

---

# 13. Final assessment

R17 should not be treated as a successful or unsuccessful scientific response.

It is not a scientific response at all.

Its only change relative to R16 is the addition of the R16 referee report.

The authoritative repository metadata still names R14 as the current paper.

The R15 development tree remains a collection of fragments rather than a complete release.

The numerical tables explicitly required by those fragments remain absent.

The continuous-model transfer remains unexecuted at a decision-separating numerical precision.

The neural framing remains stronger than the demonstrated computational advantage.

The novelty claim still needs a theorem-level separation from standard occupancy, duality, inverse-optimization, and verification machinery.

The enforcement direction is promising but is not integrated into a complete, evidenced manuscript.

Accordingly, my recommendation remains **reject in the present form**.

More importantly, I recommend that the revision cycle stop advancing until there is a genuine new scientific release. The next referee round should begin from a frozen, self-contained manuscript with a nonzero scientific delta, not from another branch whose principal change is a review or preservation artifact.
