# Referee Report — Neural Bellman Operators, Revision R16

**Journal standard used:** Econometrica-style external assessment. This is an owner-commissioned advisory report, not an official editorial decision and not a representation of appointment by Econometrica.

**Date:** 19 September 2026

**Repository:** TrillionniumFoundation/NBO

**Reviewed revision branch:** `revision/econometrica-r16-development-2026-09-19`

**Frozen reviewed SHA:** `5dbff2e29c05dd0eeef48db4fd34a6d80260d0ad`

**Immediate prior review snapshot:** `23d42ca6d41ef3e1552327c60f8d29c0bbc6495a`

**Immediate prior report:** `reviews/2026-09-19-econometrica-r15-harsh/referee_report.md`

**Review branch:** `review/econometrica-r16-harsh-2026-09-19-5dbff2e`

## Recommendation

**Reject in the present form. More precisely: R16 is not a scientific revision of the paper at all, and therefore it cannot be evaluated as a successful response to the R15 referee report.**

The branch name suggests a new Econometrica revision. The Git history says otherwise.

Relative to the immediate prior review snapshot `23d42ca6d41ef3e1552327c60f8d29c0bbc6495a`, the reviewed R16 head is two commits ahead and changes exactly two files:

1. `.github/workflows/r16-source-preservation.yml`; and
2. `.github/workflows/r16-historical-pdfs.yml`.

There are **no changes to the manuscript, supplement, response letter, bibliography, tables, figures, numerical evidence, replication code, release manifest, or referee-facing README**.

The first R16 commit is explicitly titled:

> revision(r16): preserve exact R15 review inputs on a separate revision branch

The second is explicitly titled:

> revision(r16): export unchanged historical compendium for preservation checks

Those commit messages are accurate. R16 preserves material. It does not revise the scientific paper.

This distinction is not semantic. The prior R15 report rejected the submitted object because R15 itself was incomplete and because major scientific objections remained unresolved. Since R16 changes none of the scientific objects, every substantive objection from the R15 report remains open.

The correct referee conclusion is therefore not “the authors made partial progress.” They did not submit a scientific response in R16. They submitted an archival wrapper around the previously rejected state.

---

# 1. R16 contains no scientific response to the R15 report

A revision should be judged by what changed in response to the referee.

Here, the scientific delta is exactly zero.

No theorem changed.

No proof changed.

No economic model changed.

No quantitative result changed.

No experiment changed.

No numerical certificate changed.

No missing table was supplied.

No missing citation was repaired.

No response letter was added.

No current-paper entry point was changed.

No release manifest was added.

No continuous-model validation was executed.

No neural computational frontier was demonstrated.

No information-design novelty theorem was added.

No enforcement result was strengthened.

No institutional robustness calculation was deposited.

No executable R15 paper object was assembled.

The branch therefore supplies no basis for upgrading the scientific assessment.

A top-journal revision cannot consist of preserving a rejected revision more carefully.

---

# 2. The repository still does not identify R15 or R16 as the current referee-facing paper

The repository-level metadata remains inconsistent with the claim that a new referee-facing revision has been deposited.

At the reviewed R16 SHA:

- `README.md` begins **“Neural Bellman Operators — Revision R14”**.
- The README says the **current paper** is the R14 paper.
- The README points the reader to `ECTA_R14.pdf`, `SUPP_R14.pdf`, `RESPONSE_R14.pdf`, and `COMPENDIUM_R14.pdf`.
- `REVISION_INDEX.md` begins **“Current referee-facing revision: R14 — September 19, 2026.”**
- `ECTA.tex` is still explicitly described by the repository as historical rather than the current paper.
- There is no `ECTA_R15.tex` or `ECTA_R16.tex` current editable entry point.
- There is no `SUPP_R15.tex` or `SUPP_R16.tex`.
- There is no `RESPONSE_R15.tex` or `RESPONSE_R16.tex`.
- There is no complete R15 or R16 release README.
- There is no R15 or R16 release manifest.

A referee should not infer a current manuscript from development fragments while the repository itself names an older version as current.

This was already a central defect in R15. R16 leaves it unchanged.

## Required response

The next revision should have exactly one authoritative referee-facing object with:

- one current main manuscript;
- one current supplement;
- one point-by-point response;
- one bibliography;
- all included tables and figures;
- one immutable release manifest;
- one frozen reviewed commit;
- one referee-facing README;
- one revision index naming that version as current; and
- one check command that verifies the actual deposited release.

Anything less invites ambiguity about what the referee is supposed to read.

---

# 3. The R15 scientific package remains incomplete inside R16

The R16 branch still contains the same R15 development directory:

`revisions/2026-09-19-r15-referee-response/paper/`

with only four substantive TeX fragments:

- `introduction.tex`;
- `information.tex`;
- `operator_bridge.tex`; and
- `enforcement.tex`.

It still does **not** contain:

- `paper/main.tex`;
- `paper/response.tex`;
- `paper/references.tex`;
- a complete R15 supplement;
- an R15 release manifest;
- an R15 build receipt;
- an R15 PDF release;
- an R15 referee-facing README;
- an R15 evidence tree; or
- an R15 replication package.

This was the first objection in the R15 report. R16 does not address it.

The problem is not cosmetic. Without a complete manuscript object, one cannot verify that the new fragments are consistently integrated with the inherited theorems, definitions, behavior conventions, numerical claims, references, and earlier results.

---

# 4. The missing R15 numerical tables remain missing

The prior R15 report identified explicit TeX inputs for three new tables that did not exist:

- `table_repeated_proposals.tex`;
- `table_enforcement.tex`; and
- `table_continuous_institutions.tex`.

R16 does not add them.

Therefore the associated numerical claims remain unsupported in the reviewed branch.

This includes claims about:

- repeated neural proposal families;
- action/horizon scaling;
- no-surrender value changes;
- initial-state enforcement thresholds;
- uniform enforcement thresholds;
- common-fee comparisons;
- and continuous institutional counterfactuals.

A computational economics paper cannot resolve an evidentiary objection by preserving source text that references absent evidence.

## Required response

Every quantitative statement in the next revision must trace to:

1. committed code;
2. committed machine-readable output;
3. a documented target/input identity;
4. recorded seeds where randomness is present;
5. hardware/software environment;
6. independent validation;
7. committed table source; and
8. the exact manuscript location in which the number is used.

The release manifest should bind all of these.

---

# 5. The continuous-model-to-target gap remains the central scientific blocker

The most serious substantive objection remains exactly where the R15 report left it.

The paper wants to connect economic conclusions to a continuous controlled diffusion while the certified numerical conclusions are established on a finite stored target.

R15 correctly improved the language around this issue. It introduced a Bellman-barrier route, separated stored-array certification from continuous-model validation, and acknowledged that sampled residuals are not uniform verification.

That conceptual cleanup was welcome.

But R15 also explicitly conceded that the deposited settlement results did not include numerical continuous barriers satisfying a decision-separating budget.

R16 does not change that.

No continuous supersolution/subsolution pair is deposited.

No verified derivative envelope is added.

No action supremum is certified over the continuous domain.

No stopping-boundary error is closed.

No terminal/boundary residual budget is added.

No constructor-to-target uncertainty set is quantitatively established.

No decision margin is shown to survive the total continuous-to-discrete error budget.

Thus the paper still has two logically distinct objects:

- a continuous economic model used for interpretation; and
- a finite stored target used for certified conclusions.

The transfer between them remains unproved at the precision required by the economic decisions.

## Required response

The authors must choose one of two routes.

### Route A: execute the continuous bridge

Provide a numerical enclosure strong enough to preserve every economically relevant conclusion after accounting for:

- state discretization;
- action optimization;
- stopping;
- terminal conditions;
- interpolation;
- derivative approximation;
- model/constructor discrepancy;
- and all numerical rounding.

### Route B: define the finite target as the economic model

Then remove claims whose truth depends on the unverified diffusion interpretation and state clearly what economic object is actually certified.

The current paper cannot continue to obtain interpretation from one model and rigor from another without a quantitative bridge.

---

# 6. The neural-method identity remains unsupported

The title-level framing still emphasizes **Neural Bellman Operators**.

The evidence still does not show that neural approximation changes the feasible frontier of the economic problem relative to strong nonneural methods.

The prior R15 material itself acknowledged that:

- the tested families remain low-dimensional in state;
- exact dynamic programming remains decisive at the reported sizes;
- the experiment is not a state-dimension scaling experiment; and
- the certification theorem applies to arbitrary trial value functions, not specifically neural ones.

R16 adds no new experiment.

Accordingly, the title-level neural claim remains weaker than the certification and response-set content.

This is not a request for generic larger benchmarks. It is a request for evidence aligned with the methodological claim.

If neural approximation is essential, the paper should demonstrate a domain in which:

- the state representation becomes the computational bottleneck;
- exact or conventional methods become materially more expensive;
- the neural operator gives a reproducible proposal advantage;
- certification remains independently valid;
- and the total end-to-end resource accounting favors the proposed method in an economically relevant regime.

That experiment is still absent.

## Required response

Report matched end-to-end costs including:

- state dimension;
- state representation size;
- action complexity;
- horizon;
- number of target queries;
- training cost;
- teacher/data-generation cost;
- proposal cost;
- policy-evaluation cost;
- upper-bound/certification cost;
- memory;
- certificate width;
- repeated seeds;
- failure frequency; and
- total wall time.

If the neural actor is merely one proposal generator among many, the title and contribution statement should say so.

---

# 7. The novelty case remains below the Econometrica bar as presently stated

The R15 conceptual additions were sensible:

- occupancy-based global near-optimal response sets;
- directed reward queries;
- Lagrangian support representations;
- robust error charges;
- enforcement thresholds;
- and open-action behavioral conventions.

But the previous report correctly observed that many of these ingredients are close to established machinery:

- occupancy-measure linear programming;
- performance-difference identities;
- Lagrangian duality;
- inverse optimization;
- support functions in robust optimization;
- Bellman monotonicity;
- obstacle comparisons; and
- standard verification inequalities.

R16 contributes nothing new on this point.

The paper still needs to identify a theorem that is not merely a repackaging of standard primitives into the application.

A potentially stronger direction remains the information-design problem hinted at in R15:

- which value queries are sufficient for a target economic response functional;
- how many queries are necessary;
- whether adaptive query design helps;
- whether there are lower bounds;
- whether a minimax-optimal query rule exists;
- and how query complexity interacts with dynamic model structure.

That could become a distinctive econometric/economic theory contribution.

It is not yet delivered.

---

# 8. The enforcement reframing remains promising but incomplete

R15's best economic move was to replace the fragile coarse-menu “compulsory term” narrative with a fee/enforcement frontier tied to the value of eliminating surrender.

That is a more defensible economic object.

But the general comparative statics are still modest, and the sharper results are numerical.

Those numerical results still rely on the missing R15 enforcement table and absent R15 evidence package.

R16 adds neither.

The paper therefore still needs to separate three objects cleanly:

1. a general theorem about feasible-set inclusion and obstacle gaps;
2. an initial-state implementation threshold under the actual contract class; and
3. a uniform all-state diagnostic that may exceed the legal or executable fee set.

These should not be rhetorically merged.

The theorem assumptions also still need one consistent treatment of:

- attainment versus supremum;
- exact versus eta responses;
- open mandate classes;
- threshold equality cases;
- randomized versus deterministic policies; and
- legal fee constraints.

R16 makes no progress on this.

---

# 9. The preservation workflows are appropriately labeled, but they are not a referee validation system

One positive feature of R16 is that the new workflows do not falsely claim to be scientific validation.

The first is named:

**R16 source preservation (not scientific validation)**

and records its purpose as:

**preservation only; no scientific validation claimed**.

That labeling is correct.

But it also confirms why R16 does not answer the referee.

The source-preservation workflow:

- archives selected tracked text;
- computes hashes;
- stores a short-lived artifact;
- and records a source commit.

It does not:

- compile a current manuscript;
- verify that all TeX inputs exist;
- resolve citations;
- run the economic computations;
- regenerate or independently verify tables;
- check scientific invariants;
- verify theorem-linked claims;
- or bind an actual current release manifest.

The historical-PDF workflow merely checks that an **unchanged R14 compendium** exists and uploads it.

That is preservation, not revision.

There is also a practical CI weakness: both workflows trigger only when their own workflow files change. Changes to manuscript or scientific evidence would not trigger them unless the workflow file also changed.

This is unsuitable as a release check.

## Required response

Keep preservation and validation separate.

A referee-facing validation workflow should trigger on every scientific release-defining path and should, at minimum:

- verify the release manifest;
- fail on missing TeX inputs;
- build the current manuscript and supplement;
- fail on unresolved references;
- run the authoritative numerical check;
- compare committed tables with independently generated or verified values;
- validate hashes of scientific targets;
- and emit a commit-bound receipt.

Preservation artifacts can exist in addition to this. They are not a substitute for it.

---

# 10. R16 does not answer even one numbered R15 requirement

The prior R15 report gave a minimum standard before another Econometrica-style review.

R16 satisfies none of the scientific items.

| R15 requirement | R16 status |
|---|---|
| Complete current revision object | **Not addressed** |
| Build integrity of current paper | **Not addressed** |
| Numerical evidence for new claims | **Not addressed** |
| Continuous model-to-target bridge | **Not addressed** |
| Neural computational frontier or reframing | **Not addressed** |
| Distinct response-set novelty theorem | **Not addressed** |
| Query-design theory | **Not addressed** |
| Complete enforcement theorem + evidence | **Not addressed** |
| Continuous institutional robustness evidence | **Not addressed** |
| Unified exact/eta behavior convention across full paper | **Not demonstrated** |
| Commit-bound scientific validation | **Not addressed** |
| Clear paper identity | **Not addressed** |

The only new activity is archival preservation.

That is useful repository hygiene, but it is not a response to a scientific referee.

---

# 11. What should happen before another review

The next review should not be triggered by another development branch name.

It should be triggered only when the repository contains a complete, frozen, self-contained revision object.

At minimum, the next submission should include:

1. **A complete manuscript.** One file or one documented build graph that includes every current section.
2. **A complete supplement.** Every proof needed for the current claims.
3. **A point-by-point response.** Each R15/R16 objection should map to a concrete manuscript/evidence change.
4. **A complete bibliography.** Every current citation resolves.
5. **All numerical tables.** No missing `\input` targets.
6. **All generating evidence.** Code, arrays, seeds, outputs, target hashes, and independent checks.
7. **A release manifest.** Immutable identities for all scientific inputs and outputs.
8. **A current README/index.** The repository should say unambiguously what the referee is reviewing.
9. **A scientific validation command.** One command should verify the frozen release without modifying scientific inputs.
10. **A resolved model-scope decision.** Either certify the continuous model quantitatively or make the finite target the model.
11. **A resolved neural-scope decision.** Either demonstrate neural necessity on a genuine hard frontier or demote neurality from the central claim.
12. **A distinct novelty theorem.** State exactly what is new relative to occupancy LP, inverse optimization, robust duality, and numerical verification.
13. **A complete economic mechanism result.** The enforcement contribution must be stated under one coherent set of behavioral, legal, and attainment assumptions.
14. **A release PDF package.** The referee should be able to read the exact frozen manuscript without reconstructing a development tree.

Until these are present, another “revision” label does not change the editorial substance.

---

# 12. Evidence reviewed

This report freezes and evaluates:

`5dbff2e29c05dd0eeef48db4fd34a6d80260d0ad`

on:

`revision/econometrica-r16-development-2026-09-19`.

I compared it directly against the immediate prior R15 review snapshot:

`23d42ca6d41ef3e1552327c60f8d29c0bbc6495a`.

The GitHub comparison reports:

- status: ahead;
- commits ahead: 2;
- changed files: 2;
- both changed files are R16 preservation workflows.

I reviewed in particular:

- `reviews/2026-09-19-econometrica-r15-harsh/referee_report.md`;
- `.github/workflows/r16-source-preservation.yml`;
- `.github/workflows/r16-historical-pdfs.yml`;
- `README.md`;
- `REVISION_INDEX.md`;
- the R15 development tree under `revisions/2026-09-19-r15-referee-response/paper/`; and
- the unchanged current/historical entry-point structure.

The R16 source-preservation workflow itself records the prior review parent and explicitly disclaims scientific validation. The historical-PDF workflow checks and re-uploads an unchanged R14 compendium.

I therefore do not infer any uncommitted local work, unpublished tables, unstored outputs, or intended future manuscript integration.

---

# 13. Final assessment

The repository history is unusually clear in this round.

R15 was rejected because the submitted object was incomplete and because major scientific issues remained open.

R16 then preserves that exact state more carefully.

That is not a scientific revision.

No manuscript changed.

No theorem changed.

No proof changed.

No computation changed.

No missing evidence was supplied.

No response to the referee was written.

No central objection was resolved.

The repository still calls R14 the current referee-facing revision, while R15 remains a collection of development fragments and R16 adds only preservation machinery.

The preservation work is competently labeled and may be useful for provenance. But provenance cannot substitute for a paper.

My recommendation therefore remains **reject in the present form**.

More strongly, I would not invite another substantive rereview until there is a genuinely new frozen manuscript object. A new branch name, archival zip, or historical PDF export should not be treated as another revision cycle. The next review should begin only when the scientific delta is nonzero, complete, auditable, and directly responsive to the unresolved objections.
