# Referee Report — Neural Bellman Operators, R12 Independent Harsh Re-Review

**Journal standard used:** Econometrica-style external assessment (owner-commissioned advisory review; not an editorial decision and not a representation of appointment by Econometrica).

**Date:** 18 September 2026

**Repository:** `TrillionniumFoundation/NBO`

**Reviewed revision branch:** `revision/econometrica-r12-procurement-witness-response-2026-09-18`

**Reviewed revision SHA:** `5f729aebb334d7861fd19b2ad1861f4949ad6b8f`

**This review branch:** `review/econometrica-r12-independent-harsh-rereview-2026-09-18-5f729ae`

**Prior R12 review:** `review/econometrica-r12-harsh-2026-09-18`

## Recommendation

**Reject in the present form. Do not treat the current source state as a review-complete Econometrica revision.**

R12 contains real improvements. The service-versus-private-value distinction is now correctly formulated; participation is treated explicitly; the purchaser has a no-procurement option; the all-response secant bound is valid; the finite-menu selection theorem uses adverse bounds rather than favorable tie-breaking; the dynamic exposure decomposition restores the financial-replacement term; and the proposed canonical-array / witness architecture is materially more disciplined than the earlier post-processing validator.

Those improvements do not close the top-journal gap. This independent re-review confirms the broad concerns raised in the existing R12 report, but it also identifies two source-level technical blockers that are more serious than presentation or missing PDFs:

1. **the numerical error allowance used by the procurement theorem is trusted, not independently verified; and**
2. **the procurement generator and verifier do not enforce the strict positivity required by the paper's positive financial mandate.**

These are theorem-to-code gaps. They must be closed before the numerical procurement theorem can be treated as certified even on the finite R12 array target.

In addition, the branch currently reviewed still is not the deposited R12 object described by the manuscript: the final wrappers, canonical target, witness outputs, generated tables, PDFs, and updated revision index are absent at the reviewed SHA. The economic and methodological objections also remain: an engineered discrete contract menu, no applied bridge from the stored finite target to the intended continuous economic model, a headline calculation that does not require a neural method, a mechanism discussion that is still largely accounting plus pointwise evidence, and no convincing external computational benchmark.

I would not recommend an incremental revision that merely causes the workflow to finish. The next version should first close the numerical-certification chain, then decide what the paper is fundamentally about.

---

# 1. What I regard as genuine progress

The negative recommendation should not be read as saying that R12 failed to answer the previous report.

### 1.1 The purchaser's decision is now a real decision problem

The paper no longer equates the agent's private ranking with the purchaser's allocation choice. It distinguishes the service price (b) from the agent's operating-benefit parameter (d), retains the participation positive part, charges compulsory duration, states who receives surrender fees, and includes no procurement.

That repairs a central economic defect of the earlier implementation-frontier framing.

### 1.2 Proposition 1 is logically valid

For
[
J_j(pi;d+t)=J_j(pi;d)+tA_j(pi),
]
the lower and upper service bounds for every (eta)-optimal response follow directly from the value enclosures at (d-h,d,d+h). Uniqueness and differentiability are not required. This is a legitimate way to avoid certifying service from a numerically convenient best response.

### 1.3 The menu theorem uses the correct adverse comparison

The selected item receives a lower purchaser-surplus bound and each rival an upper bound. It is valid that the favorable service and favorable payment used in a rival's upper bound need not be jointly attainable: joint attainability is unnecessary for an upper bound.

The rectangle argument in ((b,kappa)) is also valid conditional on the fixed enclosure endpoints.

### 1.4 The dynamic decomposition is more honest

R12 correctly retains
[
B_+-B_-
]
in the decomposition of the class-specific adjustment effect. Nonnegative option value does not sign a signed kernel expectation. This is materially better than attributing the class comparison to downward-drift elimination alone.

### 1.5 The intended verification architecture is directionally correct

Separating canonical primitives, lower witnesses, upper witnesses, transport, procurement values, economic summaries, and negative fixtures is the right design. The problem is not the architecture's philosophy; it is that the present theorem chain still has unverified links.

---

# 2. T1 — The (10^{-7}) arithmetic allowance is assumed by the independent verifier rather than verified by it

This is the most important new technical objection.

The numerical procurement theorem relies on a per-value allowance
[
epsilon=10^{-7}.
]
That allowance enters the service bounds as (2epsilon/h), enters the payment bounds, and therefore directly affects the strict surplus separation that identifies the winning contract.

In the source:

- `replication/r12/science.py` calls `arithmetic_audit(...)` imported from `replication/r9/contracts.py` and writes `arithmetic.json`;
- `replication/r12/engine.py` simply defines `EPS=1e-7`;
- `replication/r12/verify.py` imports that hard-coded `EPS` and uses it throughout;
- `verify.py` does **not** independently recompute the arithmetic audit;
- `verify.py` does **not** read `arithmetic.json` and check that the derived bound is below the charged allowance;
- the negative tests do not attack the arithmetic-bound premises.

Thus the so-called independent witness check can pass while the numerical error budget is wrong. Hashing `arithmetic.json` would prove only that the file was not changed; it would not prove that the bound inside it is valid.

This matters especially because the service step deliberately magnifies value error by (1/h). With (h=0.01), an understated value-error allowance directly contaminates the service interval and therefore the procurement ranking.

There is a second concern. The arithmetic audit is inherited from R9 and is expressed as a compact gamma-bound over the stored arrays. It may well be conservative, but the present R12 reviewer is not given an independently checked derivation that maps every relevant R12 operation to that bound: sparse matrix-vector accumulation, endpoint mixtures, maximization, stopping, first-date breakpoint rows, fixed-policy Bernstein recursion, restriction, upper recursion, and the subtraction operations entering class differences and service secants.

### Required response

The next revision should make the error budget part of the independently verified theorem chain.

At minimum:

1. recompute the arithmetic bound from the committed canonical target inside the independent verifier;
2. independently check every numerical premise used by the bound, including row-mass and magnitude assumptions for the first-date operator as well as later kernels;
3. fail verification unless the **derived** bound is below the advertised (epsilon);
4. deposit the derived constants used by each theorem, not only one global number;
5. ideally add a higher-precision or interval-arithmetic cross-check on the initial values and the smallest procurement separation margins.

A source-level constant named `EPS` is not a certificate.

---

# 3. T2 — The positive mandate is an open set in the paper but a closed set in the procurement generator and verifier

The economic definition in the manuscript is explicit:

[
0<pi_0le L
]

for the positive mandate.

The manuscript then says that the closure at zero may be used to bound a **supremum**, while an attained lower witness for the positive class must be strictly positive. That distinction is mathematically important.

The R12 procurement path does not currently enforce it.

In `replication/r12/engine.py`, `first_mask` admits zero for the positive class:

`a[:,2] >= 0 - tolerance`.

In `Engine.first`, the positive optimum is therefore taken over the closed class.

In `replication/r12/verify.py`, the procurement first action is checked only for membership in `first_mask`. That check also permits zero.

There is a stricter routine, `Engine.first_index`, which rejects `action[2] <= 0` for a positive lower witness. But that routine is used in the regional coefficient path; it is **not** the procurement verification path.

The generator has the same issue. `replication/r11/core.py`'s `Joint.mask` uses the positive closure at zero, and `replication/r12/science.py::procurement` stores the resulting first action without an explicit strict-positivity assertion.

Therefore the present source can, in principle, label an item “positive” and certify its value and procurement surplus even if the maximizing first risky share is exactly zero. If that occurs, the two purported financial classes meet at the boundary and the chosen item is not an attained positive-mandate contract as defined by the paper.

The manuscript states that “the selected positive first shares are strictly feasible,” but the source presently does not make that statement a verification condition.

This is not a stylistic mismatch. It is a theorem-domain mismatch.

### Required response

For every numerical claim involving an **attained** positive contract:

1. assert and independently verify (pi_0>0);
2. store the margin to zero in the witness record;
3. distinguish an upper supremum over the closure from a feasible lower value over the open class;
4. if the closure optimum is at zero, do not silently call it an attained positive optimum. Construct an explicitly positive (eta)-optimal action and propagate the resulting value/service/payment slack, or reformulate the class.

The next reviewer should be able to mutate the chosen positive action to zero and see the procurement certificate fail for the correct economic reason.

---

# 4. T3 — The branch being reviewed is still not the complete R12 object described by the paper

At reviewed SHA `5f729aebb334d7861fd19b2ad1861f4949ad6b8f`, the repository does not contain:

- `ECTA_R12.tex`;
- `SUPP_R12.tex`;
- `COMPENDIUM_R12.tex`;
- `replication/r12/canonical/manifest.json`;
- `replication/r12/output/expected.json`;
- the R12 witness arrays and procurement output;
- the generated procurement/region/exposure tables;
- the final R12 PDFs.

`REVISION_INDEX.md` still begins with **“Current complete revision: R11.”**

This contradicts several present-tense statements in the R12 source saying that the R12 target and evidence are “deposited” or “committed.”

The workflow is designed to materialize and then self-commit these objects to the same revision branch. Until that happens, however, the reviewer does not have the object that Theorem R12 numerical purports to describe.

### Required response

The review target must be one immutable post-execution SHA containing all of the following simultaneously:

1. final manuscript sources;
2. final PDFs;
3. canonical target;
4. witness seal;
5. independent validation;
6. generated tables;
7. build / execution receipt;
8. an updated revision index naming that exact state as current.

Do not ask a referee to review a branch whose scientific meaning is intended to change after the review begins.

---

# 5. T4 — The “independent” verification claim should be narrowed further

R12 is already more careful than earlier versions about this, but the present language can still invite over-reading.

The verifier is independently recoded Bellman arithmetic on the **same committed array target** and under the **same mathematical definitions**. It is not:

- an independent reconstruction of the economic primitives;
- a proof that the finite target approximates the intended continuous model;
- a real-interval implementation;
- a formally verified program;
- or an independent derivation of the numerical error allowance.

This last item is especially important after T1.

The paper should describe the result as something like:

> separately recoded witness reconstruction on a hash-identified finite array target, conditional on an independently checked floating-point error budget.

At present the final clause is not yet true.

---

# 6. E1 — The economic theorem is still too dependent on a bespoke finite contract menu

The central menu is

[
{+,-}	imes{0,.2,.4,.6,.8,1}	imes{1,ldots,8}.
]

The result chooses ((+,0.6,3)) with adjustment and ((+,0.6,4)) without adjustment.

The paper is explicit that this is not unrestricted mechanism design. That honesty is necessary, but it does not establish economic importance.

I still do not know whether the one-period commitment shift is a structural result or a consequence of:

- the six-point capacity grid;
- the equality (F=E);
- the quadratic capacity-cost coefficient;
- the linear term-cost function;
- the chosen service normalization near (b=1);
- the permissions (L=.8,S=.5);
- the eight-date horizon;
- or the specific outside value.

The reported rectangle in ((b,kappa)) is too narrow to answer those questions.

There is also a revealing structural redundancy: for (m=8), surrender is unavailable inside the operating horizon, so the operating value is independent of (F). Yet positive capacity still raises (C(E)). Under the stated institution, (E>0,m=8) offers are therefore weakly or strictly dominated by the corresponding (E=0,m=8) offer, depending on participation. The code itself recognizes the operational irrelevance of (F) at (m=8) by caching that case with fee zero. This is not an error, but it emphasizes that the menu has not been reduced or derived from an economically primitive institution.

### Required response

Either justify the standardized menu institutionally, or move toward a continuous/refined contract theorem.

A convincing response would include several of:

- refine the grid around (E=.6);
- decouple fee from capacity;
- vary the capacity-cost curvature;
- vary the term-cost functional form;
- vary fee incidence;
- vary outside value;
- vary permissions and horizon;
- report the exact second-best contract at each key point;
- show whether the 3-vs-4 result survives those changes.

---

# 7. E2 — The headline theorem is still a theorem about one stored finite array economy

R12 deserves credit for being explicit: the new numerical theorem concerns a 1,617-state stored target, finite later-date control menus, and a stored first-date piecewise-affine operator.

That clarity creates a sharp limitation.

The paper repeatedly uses economic language suggesting a stochastic settlement model with continuous underlying primitives. But the headline procurement result does not include a quantitative approximation allowance from those primitives to the R12 finite target.

Generic operator-transfer or diffusion-approximation theory preserved elsewhere in the compendium does not solve this. The relevant constants and assumptions must be applied to the exact procurement separation margin.

Without that bridge, the strongest economic statement is:

> on this stored finite array target and this finite contract menu, this discrete item has certified surplus separation.

That can be a useful computational theorem. It is not yet a theorem about the intended continuous economic model.

### Required response

Either apply a model-to-target approximation theorem quantitatively to the headline procurement choice, or reposition the paper as a finite-state verified-computation paper.

---

# 8. M1 — The title “Neural Bellman Operators” remains misaligned with the R12 headline result

The central R12 procurement calculation is solved and reconstructed by exact finite-state dynamic programming on committed arrays.

The certificate is deliberately independent of a neural proposal.

That is mathematically attractive, but editorially it leaves the obvious question: what is specifically **neural** about the result that now carries the paper?

A method can use neural policies as proposals while certifying them independently. But then the paper must show that the neural proposal materially expands the problem sizes, policy classes, or economically relevant environments that can be solved relative to nonneural alternatives.

R12 does not do that in the main theorem.

### Required response

Choose one identity:

- **neural proposal + rigorous certification:** then demonstrate end-to-end scaling where the neural proposal is necessary or decisively useful; or
- **verified parametric dynamic programming / economic procurement:** then retitle and reposition, with neural proposal as one implementation option.

The current paper is strongest where the neural component is least necessary.

---

# 9. M2 — The service theorem solves a real problem but is too elementary to carry the theoretical contribution

Proposition 1 is useful. It is also essentially the finite-difference/subgradient geometry of a supremum of affine functions in (d), augmented with value-error and near-optimality slack.

That is an excellent lemma for the application. It is not, by itself, an Econometrica-level theoretical innovation.

If the authors want this direction to be a major contribution, they need something materially deeper: multidimensional services, sharp identified service sets from noisy value queries, endogenous transition perturbations, equilibrium response correspondences, or an implementability theorem built on these bounds.

Otherwise, present it as a clean tool rather than a headline theory result.

---

# 10. M3 — The “mechanism” remains an accounting decomposition plus pointwise computation

The corrected identity
[
Omega_+-Omega_-=(g_+-g_-)+(K_+-K_-)O_1+(B_+-B_-)
]
is valid and useful.

But it does not explain the sign without additional structure.

The opportunity-tail condition is a summation-by-parts / stochastic-order condition. The manuscript explicitly declines to derive the required opportunity ordering from wealth or other primitive economic variables. The numerical evidence is pointwise.

So the paper currently provides:

- a correct decomposition;
- a sufficient abstract ordering condition; and
- several pointwise computed decompositions.

That is not yet a transferable economic mechanism.

### Required response

Derive economically interpretable primitive conditions that imply the relevant ordering, or show a broad calibrated region where one component is stable and dominant and explain why.

Adverse cases should be part of that mechanism analysis, not only historical preservation.

---

# 11. C1 — The computational novelty is still benchmarked mainly against the authors' own alternatives

The broader-law exercise compares the count-information bound and signed compression on the same internal target. That is useful engineering evidence.

It does not establish field-level computational advantage.

A convincing computational-method contribution should compare against appropriate external or standard baselines, including exact DP where feasible and standard robust / interval / parametric methods where comparable.

Important dimensions include:

- total wall time;
- memory;
- certificate width;
- number of uncertain parameters;
- state, horizon, and action scaling;
- refinement behavior;
- failure regimes;
- proposal cost;
- verification cost.

The paper is commendably careful not to claim universal superiority. But once it gives up that claim, it needs another reason why the computational method is top-journal significant.

---

# 12. E3 — The economic interpretation of “service” remains unusually convenient for the mathematics

The purchaser's service measure is exactly the coefficient (A) on the agent's benefit parameter (d). That is why the value-query secant bound works so cleanly.

This may be economically appropriate, but the paper has not yet convinced me that it is institutionally natural rather than chosen because it is the statistic exposed by the perturbation.

The same issue applies to:

- the split between capacity cost and purchaser term cost;
- the external recipient of surrender fees;
- the one-for-one link (F=E);
- the normalization of (b);
- and the outside value.

### Required response

Either give a concrete institutional interpretation with calibrated primitives or prove which conclusions survive alternative service and transfer definitions.

---

# 13. Paper architecture

R12 is cleaner than its predecessors, but the project still carries too many candidate “main contributions”:

- neural proposal and certification;
- changing-law regional bounds;
- signed compression;
- finite-menu procurement;
- robust-to-ties service bounds;
- dynamic preference adjustment;
- signed opportunity exposure;
- canonical witness verification.

A top-journal main paper needs one dominant theorem chain.

The authors should be able to answer in one sentence:

> What can an economist prove or compute after reading this paper that could not previously be proved or computed?

I do not yet see one answer dominating the others.

---

# 14. Additional technical comments

1. **State the exact-best-response theorem first.** The economic object is exact optimal response. Treat (eta)-optimality as robustness, not as if (10^{-8}) were behaviorally primitive.

2. **Report (h)-sensitivity.** Since the service certificate trades curvature against (2epsilon/h), show multiple perturbation sizes and the resulting winning-contract margin.

3. **Report the binding rival.** The economically relevant object is not only the winner but the competitor that sets the certified separation.

4. **Separate supremum and attainment everywhere.** This is particularly important for the open positive class.

5. **Verify strict-positive selected actions in the independent output.** Include the actual (pi_0) and a strict margin above zero.

6. **Verify the arithmetic audit in the independent output.** Deposit the derived bound and fail if it exceeds the theorem allowance.

7. **Do not call `arithmetic.json` evidence merely because it is hashed.** Integrity and correctness are different.

8. **Clarify the (m=8) redundancy.** If surrender is impossible, explain why positive capacity is even a meaningful standardized product in that term.

9. **Vary fee incidence.** If fees accrue to the purchaser rather than an external sector, the objective changes materially.

10. **Vary capacity incidence.** If capacity cost is borne by the purchaser directly rather than compensated through participation, the ranking may change.

11. **Provide continuous-grid diagnostics.** At minimum refine (E) locally and report whether the term switch persists.

12. **Pin every table to the target identity.** Historical R8/R9/R11 results and new R12 arrays must never be visually conflated.

13. **Do not use workflow success as mathematical evidence.** The evidence is the deposited target, witness, reconstructed inequalities, and error budget.

14. **Seal output-directory inventory or state that it is intentionally extensible.** The canonical directory rejects unlisted files; the witness identity check verifies listed hashes but does not reject unlisted output files. This is not presently a theorem flaw, but the “sealed witness” terminology should match the actual invariant.

15. **Add an adversarial test for the error budget.** A deliberately reduced `EPS` should cause the verifier to fail because the independently derived arithmetic bound exceeds it.

16. **Add an adversarial test for the positive boundary.** A zero-share “positive” chosen witness should be rejected.

---

# 15. Minimum standard before another Econometrica-style review

I would want all of the following before treating the next version as a fundamentally new submission rather than another incremental repository revision.

| Area | Minimum convincing response |
|---|---|
| Review object | One immutable post-execution SHA with final manuscripts, target, witnesses, validation, tables and receipts. |
| Arithmetic | Independent recomputation/check of the numerical error bound; no hard-coded theorem allowance accepted on trust. |
| Positive mandate | Strict ( pi_0>0 ) enforced for every attained positive lower/chosen contract; closure used only for supremum upper bounds. |
| Model-to-target | Quantitative approximation bridge applied to the procurement separation, or an explicit finite-target repositioning. |
| Contract choice | Institutionally justified menu or refinement/continuous robustness. |
| Method identity | Demonstrate why neural proposal is materially needed, or retitle/reposition. |
| Mechanism | Primitive economic conditions or broad stable mechanism region. |
| Computation | External baselines and scaling, including full proposal + certification cost. |
| Economic interpretation | Robustness to service definition, cost incidence, fee recipient, permissions, outside option and horizon. |
| Paper center | One primary contribution and one coherent theorem chain. |

---

# 16. Evidence reviewed

This report is based on the exact R12 source commit `5f729aebb334d7861fd19b2ad1861f4949ad6b8f`, including:

- `revisions/2026-09-18-r12-procurement-witness/paper/main.tex`
- `revisions/2026-09-18-r12-procurement-witness/paper/S15_proofs.tex`
- `revisions/2026-09-18-r12-procurement-witness/response_to_referee.md`
- `revisions/2026-09-18-r12-procurement-witness/preservation_map.md`
- `replication/r12/science.py`
- `replication/r12/verify.py`
- `replication/r12/engine.py`
- `replication/r12/canonical.py`
- `replication/r12/README.md`
- `replication/r11/core.py`
- `replication/r9/contracts.py`
- `replication/r8/model.py`
- `replication/r7/core.py`
- `REVISION_INDEX.md`
- `.github/workflows/r12-procurement-witness.yml`
- prior report `reviews/2026-09-18-econometrica-r12-harsh/referee_report.md`

At the reviewed SHA, the final R12 wrappers, canonical manifest, witness outputs, generated tables and PDFs are not present.

---

# 17. Final assessment

R12 has improved enough that the remaining objections are now sharper.

The procurement formulation is more coherent. The service bound is valid. The adverse menu comparison is valid. The dynamic accounting is more careful. The authors have also moved in the right direction on reproducibility and witness semantics.

But the paper is not yet review-complete, and the numerical theorem is not yet source-secure.

The two immediate technical blockers are concrete:

1. the verifier trusts the theorem's floating-point allowance instead of independently certifying it; and
2. the procurement path does not enforce the strict positivity required by the positive financial mandate.

Even if both are repaired and the workflow finally deposits the intended artifacts, the deeper Econometrica questions remain: the economic result is highly menu-specific, the finite target is not quantitatively connected to the intended continuous model, the main calculation does not require a neural method, the mechanism is not yet primitive, and the computational comparison lacks external benchmarks.

For those reasons I recommend **rejection in the present form** and a substantial reconception rather than another narrow patch release.
