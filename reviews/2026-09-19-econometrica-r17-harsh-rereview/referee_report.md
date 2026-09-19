# Referee Report — Neural Bellman Operators, Revision R17

**Journal standard used:** Econometrica-style external assessment. This is an owner-commissioned advisory report, not an official Econometrica editorial decision and not a representation of appointment by Econometrica.

**Date:** 19 September 2026

**Repository:** `TrillionniumFoundation/NBO`

**Reviewed branch:** `revision/econometrica-r17-full-response-2026-09-19`

**Frozen reviewed SHA:** `80c8a743efb5ff60826c15b0bc3369965957af68`

**Immediate predecessor:** `revision/econometrica-r16-development-2026-09-19` at `5dbff2e29c05dd0eeef48db4fd34a6d80260d0ad`

**Immediate prior report:** `reviews/2026-09-19-econometrica-r16-harsh/referee_report.md`

**This review branch:** `review/econometrica-r17-harsh-rereview-2026-09-19-80c8a74`

## Recommendation

**Reject in the present form. I would not treat R17 as a scientific revision at all.**

The branch name says **full-response**. The Git object says the opposite.

A direct comparison of the frozen R16 and R17 heads shows:

- R17 is exactly one commit ahead of R16;
- exactly one file changed;
- the only changed file is `reviews/2026-09-19-econometrica-r16-harsh/referee_report.md`;
- there are no changes to the main paper;
- no changes to the supplement;
- no changes to a response letter;
- no changes to the bibliography;
- no changes to any table or figure;
- no changes to replication code or numerical output;
- no changes to the release manifest;
- no changes to README or revision index;
- no new scientific validation;
- and no new economic result.

The sole R17 commit is titled:

> Add harsh Econometrica-style referee report for R16

That description is accurate. R17 imports the prior referee report. It does not respond to it.

Accordingly, there is no scientific delta to referee. The correct substantive assessment is therefore inherited from R16, with an additional R17-specific submission-integrity objection: a branch labeled as a full response contains no response.

A top-journal revision cycle cannot be advanced by renaming a branch and adding the previous referee report.

---

# 1. R17 is not a revision of the paper

A revision should change the scientific object being reviewed.

R17 does not.

Relative to R16, the scientific delta is exactly zero.

No theorem changed.

No proof changed.

No model changed.

No mechanism changed.

No quantitative claim changed.

No numerical certificate changed.

No experiment changed.

No replication artifact changed.

No current-paper entry point changed.

No response letter was added.

No referee objection was answered in the manuscript.

No release object was created.

No evidence package was extended.

No scientific CI or verification command was added.

The only new content is the R16 referee report itself.

This is not a partial response. It is not an incomplete response. It is **no scientific response**.

---

# 2. The label “full-response” is materially inconsistent with the contents

The reviewed branch is named:

`revision/econometrica-r17-full-response-2026-09-19`

Yet there is no R17 response letter and no R17 scientific modification.

That discrepancy matters because version identity is part of a refereeable object.

A reader encountering a branch labeled “full-response” is entitled to expect at least:

1. a complete revised manuscript;
2. a point-by-point response;
3. an updated supplement where relevant;
4. updated evidence for revised quantitative claims;
5. a release index identifying the revision as current;
6. a frozen release manifest;
7. and a reproducibility path tied to that exact revision.

None of these is added in R17.

The branch therefore fails at the most basic level of submission identity.

If the purpose of R17 was merely to preserve the R16 report, the branch should have been named as a review-preservation or archival branch. Calling it a full response creates a false expectation about what changed.

---

# 3. The repository still identifies R14, not R17, as the current referee-facing paper

At the frozen R17 SHA:

- `README.md` begins **“Neural Bellman Operators — Revision R14”**;
- the README explicitly says the **current paper** is the R14 paper;
- it points to the R14 main manuscript, proof supplement, response, and compendium;
- `REVISION_INDEX.md` begins **“Current referee-facing revision: R14 — September 19, 2026”**;
- the README states that root `ECTA.tex` is historical;
- there is no `ECTA_R17.tex`;
- there is no `SUPP_R17.tex`;
- there is no `RESPONSE_R17.tex`;
- there is no R17 release manifest;
- there is no R17 build receipt;
- there is no R17 release PDF set;
- and there is no R17 referee-facing README.

Thus the repository itself does not recognize R17 as a scientific paper release.

A referee should not reconstruct an implied submission from branch names while the repository metadata says that an older version is current.

---

# 4. R17 does not answer a single substantive R16 objection

The R16 report identified a set of scientific and evidentiary blockers.

R17 changes none of the files that could answer them.

Therefore every substantive R16 objection remains open.

| R16 objection | R17 status |
|---|---|
| No complete current revision object | **Unchanged** |
| No current-paper identity beyond R14 | **Unchanged** |
| Missing response package for post-R14 development | **Unchanged** |
| Missing numerical evidence for newer claims | **Unchanged** |
| Continuous-model-to-finite-target bridge not quantitatively closed | **Unchanged** |
| Neural-method necessity/frontier not demonstrated | **Unchanged** |
| Distinct novelty theorem below the required bar | **Unchanged** |
| Enforcement/mechanism contribution incomplete | **Unchanged** |
| Exact versus approximate response conventions not unified | **Unchanged** |
| No commit-bound scientific release validation for the alleged new revision | **Unchanged** |
| No R17 release manifest | **Unchanged** |
| No R17 response letter | **Unchanged** |

There is no basis for upgrading any scientific assessment.

---

# 5. The continuous-model-to-target gap remains the central technical blocker

The prior reviews correctly separated two objects:

1. the continuous economic model used for interpretation; and
2. the finite stored target on which the strongest certificates are actually established.

That distinction remains unresolved in R17 because R17 adds no scientific content.

No continuous supersolution/subsolution pair is added.

No verified derivative envelope is added.

No continuous-domain action supremum is certified.

No stopping-boundary error is closed.

No terminal or boundary residual budget is closed.

No constructor-to-target uncertainty set is quantitatively bounded.

No decision margin is shown to survive the complete continuous-to-discrete error budget.

The paper therefore still obtains economic interpretation from a continuous model while obtaining rigorous computational certification from a different finite object, without a sufficiently sharp quantitative transfer theorem connecting them.

That is not a minor numerical-analysis detail. It is a scope-of-theorem issue.

If the economic conclusions are meant to be claims about the continuous model, the bridge must be executed at the precision needed to preserve the economically relevant decisions.

If the finite target is the true economic model, the paper must say so and narrow the continuous-model interpretation accordingly.

R17 does neither.

---

# 6. The “Neural Bellman Operators” title-level claim remains insufficiently supported

The strongest certification statements in this research program do not appear to be inherently neural.

The prior report noted that:

- exact dynamic programming remains decisive at the reported target sizes;
- several proposal families are low-dimensional;
- the certification logic applies to trial value functions more generally;
- and the deposited experiments do not establish a regime where neural approximation changes the feasible computational frontier relative to strong nonneural methods.

R17 adds no experiment and no matched computational comparison.

Accordingly, the central neural branding remains stronger than the demonstrated necessity of the neural component.

For a title-level methodological claim, the paper needs evidence aligned with that claim.

At minimum, one would want an economically meaningful regime in which:

- representation complexity genuinely becomes binding;
- strong nonneural baselines become materially less attractive;
- the neural proposal mechanism yields a reproducible advantage;
- certification remains independent of the neural proposal;
- and full end-to-end resource accounting favors the proposed architecture.

That comparison should include training cost, teacher/data-generation cost, proposal cost, policy-evaluation cost, certification cost, memory, target queries, repeated seeds, failure frequency, certificate width, and wall time.

R17 supplies none of this.

---

# 7. The novelty case remains insufficiently isolated

The paper contains useful combinations of:

- Bellman inequalities;
- occupancy or response-set reasoning;
- support-function ideas;
- Lagrangian representations;
- robust error charges;
- inverse or revealed-response logic;
- and enforcement/contracting applications.

But a top-field-journal theory contribution requires a sharply isolated theorem whose content is not merely a recombination of familiar tools applied to a new environment.

The prior report identified a potentially stronger direction: treat value queries themselves as an information-design object.

For example:

- Which queries are sufficient for a target economic functional?
- What is the minimal number of queries?
- Are there lower bounds?
- Does adaptive query selection improve complexity?
- Is there a minimax-optimal query design?
- How does query complexity depend on dynamic structure or admissible policy classes?

A theorem of that kind could make the information content of Bellman/value queries the central economic-theoretical object.

R17 contributes nothing new here.

Therefore the novelty objection remains unchanged.

---

# 8. The enforcement and implementation contribution remains incomplete

The move from coarse contract terms toward a fee/enforcement frontier is one of the more promising economic directions in the paper.

However, the contribution still requires a unified treatment of:

- exact versus approximate responses;
- attainment versus supremum;
- open versus closed mandate sets;
- threshold equality;
- randomized versus deterministic responses;
- legally admissible fee sets;
- initial-state versus uniform implementation;
- and the distinction between diagnostic and executable enforcement levels.

The numerical claims tied to enforcement also require complete, deposited, auditable evidence.

R17 changes no theorem, no table, no code, and no evidence on these points.

Thus the mechanism-design contribution remains conceptually promising but not yet complete at an Econometrica-style standard.

---

# 9. R17 worsens submission hygiene by mixing review artifacts with revision identity

The repository has made serious efforts at preservation and provenance.

That is useful.

But preservation, revision, and referee review should be separate object classes.

The R17 branch is especially problematic because it advances the revision number while adding only a review artifact.

This creates avoidable ambiguity:

- Is R17 a paper revision?
- Is it a review-preservation branch?
- Is R16 the last scientific state?
- Is R14 still the current release?
- Is the referee meant to read R14, R15 fragments, R16 workflows, or an implied R17 object?

The repository metadata answers one of those questions: R14 is current.

The branch name answers another: R17 is supposedly a full response.

The Git delta answers a third: R17 only adds a referee report.

Those three signals are inconsistent.

A research repository intended for repeated external review should enforce a simple invariant:

**A revision number advances only when the scientific release object advances.**

Review artifacts should live on review branches or under review directories without masquerading as a new paper revision.

---

# 10. The current package remains non-refereeable as a new revision

A refereeable revision should make it possible to answer, unambiguously:

- What exact manuscript am I reading?
- What changed?
- Why did it change?
- Which referee comment does each change answer?
- Which theorem statements are new?
- Which numerical claims are new?
- Which evidence supports them?
- Can I reproduce the release?
- Can I verify that the PDF corresponds to the frozen sources?
- Can I distinguish development material from the submitted object?

R17 fails this basic test because it does not provide a new submitted object at all.

The scientific object is unchanged from R16.

The repo-level current object remains R14.

The branch-level delta is a referee report.

Therefore I do not regard R17 as a scientific submission.

---

# 11. Minimum conditions before another substantive rereview

I would not recommend spending another full referee cycle on a new branch label unless the next branch contains a nonzero and complete scientific delta.

At minimum, the next revision should contain:

1. **One authoritative current manuscript.** A complete paper, not development fragments.
2. **One authoritative supplement.** All proofs needed for current claims.
3. **One point-by-point response.** Every R16/R17 objection mapped to a concrete scientific or evidentiary change.
4. **One current bibliography.** Every citation resolves in the frozen build.
5. **All current tables and figures.** No missing or implied inputs.
6. **All numerical source evidence.** Code, machine-readable output, target identities, seeds, and environment.
7. **Independent checks.** Verification should not depend on trusting the same generator that produced the claim.
8. **One release manifest.** Hash-bound identities for every scientific input and output.
9. **One current README and revision index.** Both should name the same frozen revision as current.
10. **One scientific validation command.** It should verify the frozen release without mutating scientific inputs.
11. **A resolved continuous-model scope.** Either quantitatively certify the continuous-to-finite bridge or narrow the claims.
12. **A resolved neural scope.** Either demonstrate neural necessity on a genuine hard frontier or reframe the method.
13. **A distinct novelty theorem.** State clearly what is new relative to standard Bellman, occupancy, duality, inverse-optimization, and robust-support machinery.
14. **A complete mechanism result.** Enforcement/implementation claims should use one coherent behavioral and legal convention.
15. **A release PDF package.** The exact frozen paper and supplement should be readable without reconstructing a development tree.

Only after those conditions are met would another substantive Econometrica-style rereview be meaningful.

---

# 12. Evidence reviewed

This report freezes and evaluates:

`80c8a743efb5ff60826c15b0bc3369965957af68`

on:

`revision/econometrica-r17-full-response-2026-09-19`.

I compared that head directly against R16:

`5dbff2e29c05dd0eeef48db4fd34a6d80260d0ad`.

The Git comparison reports:

- status: ahead;
- commits ahead: 1;
- changed files: 1;
- additions: 576;
- deletions: 0;
- sole changed file: `reviews/2026-09-19-econometrica-r16-harsh/referee_report.md`.

I also checked:

- the R17 commit metadata;
- `README.md`;
- `REVISION_INDEX.md`;
- root `ECTA.tex`;
- `supp.tex`;
- and the full R16 harsh referee report now imported into R17.

The R17 commit message is:

`Add harsh Econometrica-style referee report for R16`.

I do not infer any uncommitted local changes, intended future response, unstored evidence, or off-branch manuscript revision.

The review is based only on the frozen repository state.

---

# 13. Final assessment

R17 is not a response to the R16 referee report.

It is the R16 referee report added to a branch called “full-response.”

That is the entire delta.

There is no new paper.

There is no new supplement.

There is no response letter.

There is no new theorem.

There is no new proof.

There is no new economic result.

There is no new numerical evidence.

There is no new experiment.

There is no new continuous-model certificate.

There is no new neural frontier result.

There is no new novelty theorem.

There is no new release manifest.

There is no new referee-facing release identity.

The repository still identifies R14 as current.

Every scientific objection from R16 therefore remains open.

My recommendation is **reject in the present form**.

More importantly, I would not regard another incremented revision branch as worthy of substantive rereview until the repository contains a genuinely new, complete, frozen scientific object with a nonzero manuscript delta and a point-by-point response tied to auditable evidence.

A revision number is not a scientific revision.

A branch name is not a response.

A preserved referee report is not a paper.
