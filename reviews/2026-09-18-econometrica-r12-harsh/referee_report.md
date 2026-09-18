# Referee Report — Neural Bellman Operators, Revision R12

**Journal standard used:** Econometrica-style external assessment (owner-commissioned advisory review; not an editorial decision or a representation that the reviewer was appointed by Econometrica).

**Date:** 18 September 2026

**Repository:** `TrillionniumFoundation/NBO`

**Reviewed revision branch:** `revision/econometrica-r12-procurement-witness-response-2026-09-18`

**Reviewed revision SHA:** `5f729aebb334d7861fd19b2ad1861f4949ad6b8f`

**Review branch:** `review/econometrica-r12-harsh-2026-09-18`

**Prior report answered by R12:** `reviews/2026-09-18-econometrica-r11-service-certificate-audit/referee_report.md`, review commit `442b009379402df7da354eacb4ff8f82d44cdce7`.

**Important scope note.** At the time of this review, GitHub Actions run `35321946562` (“R12 procurement and witness deposit”) was still **queued**. The reviewed SHA therefore contains the R12 scientific source, response, verifier code, and deposit workflow, but not the workflow-generated final wrappers, canonical arrays, witness outputs, tables, PDFs, or execution receipt. Any later self-commit by that workflow is a different revision state and is not numerically certified by this report.

---

## Recommendation

**Reject in the present form.**

R12 is a serious improvement over R11. The authors have understood the central economic objection in the previous report: a ranking of the agent’s financial classes is not a procurement decision because the purchaser values service, must satisfy participation, and pays for implementation. The new finite-menu procurement formulation is coherent; Proposition 1’s all-response service enclosure is mathematically valid; Theorem 2 correctly uses adverse lower/upper surplus bounds rather than a favorable tie-breaking rule; the opportunity-exposure identity fixes an earlier omitted financial-replacement term; and the source architecture now attempts to separate immutable primitives, mathematical witnesses, and independently recoded checking.

Those are real advances. They do not, however, produce an Econometrica paper in the present version. The current submission faces a combination of **review-readiness, economic significance, model-to-computation, methodological identity, and novelty** problems. Most importantly:

1. the reviewed revision is not yet a complete, executable deposit;
2. the headline procurement result is tied to an engineered 96-point-per-regime institutional menu and narrow cost/price perturbations;
3. the numerical theorem is explicitly a theorem about a newly stored 1,617-state array target, with no applied enclosure connecting this R12 target to the underlying continuous economic model;
4. the central R12 computation is exact finite-state dynamic programming, so the paper’s title and headline methodological identity as *Neural Bellman Operators* are not borne out by the result that now carries the economics;
5. the new service theorem is useful but essentially a convex secant/subgradient inequality;
6. the “mechanism” result remains primarily an accounting decomposition unless its signed exposure ordering is derived from economic primitives; and
7. the computational comparison remains internal to two variants of the authors’ own bound rather than a convincing comparison to the existing parametric Markov-model / regional-synthesis literature or to standard exact/robust dynamic-programming baselines.

I would not recommend another incremental “R13” that only widens one rectangle, adds another table, or deposits the currently queued artifacts. A publishable resubmission would need a more fundamental consolidation around one economically general question and one computational contribution that is demonstrably necessary for solving it.

---

# 1. What R12 successfully repairs

Before detailing the objections, I want to distinguish genuine progress from unresolved issues.

### 1.1 The procurement accounting problem is finally formulated correctly

R11 priced implementation after fixing an allocation. R12 instead lets the purchaser select ((\sigma,E,m,q)) from an explicit menu and retains a no-procurement outside option. It keeps the service price (b) distinct from the agent’s operating-benefit parameter (d), retains the positive part in participation, prices compulsory duration, assigns surrender fees to a stated recipient, and recognizes that private-value rankings need not equal purchaser rankings.

That is the correct direction. Equation (accounting) and the discussion around the positive mandate make the economic distinction transparent.

### 1.2 The all-response service bound is logically sound

If
[
J_j(\pi;d+t)=J_j(\pi;d)+tA_j(\pi)
]
with (0\le A\le \bar A), the stated lower and upper secants follow immediately from (eta)-optimality and value enclosures at (d-h,d,d+h). The proof does not require a differentiable envelope or unique optimizer. It is therefore legitimate to use the interval for every exact or near-optimal response rather than a numerically selected policy.

This directly answers one important concern from R11.

### 1.3 The menu-selection theorem uses the right adverse ordering

The selected contract is evaluated at a lower bound on its surplus while rivals receive upper bounds. The proof correctly notes that the rival’s favorable service and favorable payment need not be jointly attainable for their combination to be a valid upper bound. Vertex checking for an affine ((b,\kappa)) rectangle is also valid.

### 1.4 R12 no longer claims that downward-drift elimination itself explains the class difference

The decomposition
[
\Omega_+-\Omega_-=(g_+-g_-)+(K_+-K_-)O_1+(B_+-B_-)
]
is a correct identity under the stated definitions, and retaining (B_+-B_-) is essential. The text explicitly says that nonnegative option values do not sign a signed kernel expectation. That is materially more careful than the earlier mechanism discussion.

### 1.5 The proposed verifier architecture is substantially better

The new source attempts to separate:
- primitive-array identity;
- lower-policy feasibility and polynomial reconstruction;
- upper recursions;
- transport checks;
- procurement Bellman values;
- service/participation accounting; and
- stale-summary / corrupted-witness negative fixtures.

The exact mutation that defeated the R11 validator is now explicitly included as a negative fixture. This is the correct philosophy.

These repairs matter. My negative recommendation is therefore not based on the old R11 objections simply being repeated unchanged.

---

# 2. F1 — The reviewed R12 is not a complete deposited revision

This is a threshold problem.

At reviewed SHA `5f729aebb334d7861fd19b2ad1861f4949ad6b8f`, the repository does **not** contain the objects that the README and response describe as already committed:

- `ECTA_R12.tex`
- `SUPP_R12.tex`
- `COMPENDIUM_R12.tex`
- the five generated table files imported by the new main source;
- `replication/r12/canonical/manifest.json`;
- `replication/r12/output/expected.json`;
- `certificate_arrays.npz`;
- `procurement.json`;
- `procurement_witness.npz`;
- `independent_validation.json`;
- `exposure.json`;
- `broader.json`;
- `execution.json`;
- the final R12 PDFs and execution receipt.

The default command advertised by `replication/r12/README.md`,
```
python replication/r12/verify.py
```
cannot run on the reviewed commit because both its default target directory and its default sealed witness directory are absent.

Likewise, `revisions/.../paper/main.tex` imports generated tables that are absent at the reviewed SHA. `REVISION_INDEX.md` still identifies R11 as the “Current complete revision.” That description is consistent with the repository state and inconsistent with treating this SHA as the completed R12 deposit.

I traced the intended process. `.github/workflows/r12-procurement-witness.yml` is designed to (i) generate and commit wrappers, then (ii) construct/freeze the new target, run the science and independent verifier, build the manuscripts, and commit all arrays/results/PDFs back to the same branch. At the time of review, Actions run `35321946562` and job `105526185435` were queued with no runner assigned and no steps executed.

This is not a cosmetic complaint. R12’s strongest claims are *numerical certification claims*. Until the immutable target, witnesses, validation output, and final manuscript are actually deposited at one identified commit, there is no reviewable numerical theorem package.

### Required response

Do not describe generated artifacts as “committed” until they are present in the branch being presented for review. A future revision should have one immutable review target containing:

1. final main, supplement, and compendium sources and PDFs;
2. canonical primitives and immutable expected identity;
3. all numerical witnesses;
4. independent validation output;
5. all generated tables;
6. execution/build receipts; and
7. a revision index that names that exact commit as current.

The final review request should identify the **post-workflow deposit SHA**, not the pre-execution source SHA.

---

# 3. F2 — The procurement theorem is too dependent on an engineered finite menu

The new central economic theorem chooses among
[
\{+,-\}\times\{0,.2,.4,.6,.8,1\}\times\{1,\ldots,8\}.
]

The paper is commendably explicit that this is not unrestricted mechanism design and is not certified as an approximation to a continuous contract space. But that disclaimer does not establish that this is an economically important institutional environment.

The central result is that adjustment selects ((+,0.6,3)) while no adjustment selects ((+,0.6,4)). At present I do not know whether this is a structural economic result or a consequence of:

- the six-point capacity grid;
- the forced equality (F=E);
- the quadratic coefficient (0.02) in (C(E)=0.02E^2);
- the linear term-cost schedule (D_\kappa(m)=\kappa(m-1)/8);
- the chosen value of (kappa=0.02);
- the fixed permissions (L=0.8,S=0.5);
- the eight-period horizon; or
- the particular service price normalization near (b=1).

The uniform price box
[
b\in[0.998,1.02],\qquad \kappa\in[0.0198,0.0202]
]
does little to answer that question. In particular, the term-cost interval varies by only one percent around its center, and the headline difference is exactly one discrete compulsory interval.

A top general-interest theory/econometrics journal needs either a compelling institutional reason for this contract space or a theorem showing that the qualitative result survives economically meaningful variation in the contracting technology.

### Required response

At minimum, I would want one of the following.

**Route A: economically justified finite institution.** Tie the six capacities, eight terms, fee assignment, and cost schedules to an actual institution or a clear model of standardization, with quantitatively meaningful calibration and counterfactual variation.

**Route B: continuous/refined contract result.** Show convergence or robustness as the capacity grid is refined; decouple (F) and (E); allow a useful class of capacity and term cost functions; and establish whether the three-vs-four-period shift is stable or merely a grid crossing.

**Route C: general comparative statics.** Give primitive conditions under which adjustment changes the optimal commitment duration or enforcement intensity, and use the finite computation as an illustration rather than the theorem itself.

The present “we explicitly restrict the menu” language is necessary but not sufficient.

---

# 4. F3 — The numerical theorem is about a 1,617-state stored-array object, not yet the underlying economic model

R12 is unusually clear on this point, and I credit the clarity. The main paper states that the mathematical object for the new numerical results is the deposited array system, not an unstated diffusion approximation. The new target has 1,617 states; consumption and adjustment are finite-menu controls; the first-date risky share is optimized over a stored piecewise-affine operator; later controls remain finite.

This makes the finite theorem reviewable **once the arrays are actually deposited**. But it also sharply limits the economic interpretation.

The manuscript repeatedly speaks about a “stochastic settlement economy,” adjustment technology, financial mandates, surrender, and purchaser choice. Yet no applied R12 theorem bounds the difference between the claimed finite target and the intended continuous-state/continuous-control economic problem. Earlier general operator-transfer and approximation results are “preserved in the compendium,” but R12 explicitly does not apply an R11-to-R12 transfer and does not automatically discharge diffusion approximation assumptions.

Therefore the headline economic theorem currently has the logical form:

> for one newly stored finite array economy, under one finite contract menu, the certified discrete choice is X.

That can be a useful computational result, but it is substantially weaker than a result about the underlying economic model.

### Required response

Either:

1. provide a rigorous, quantitatively used approximation bridge from the economic primitives to the R12 finite target, with the resulting choice robust to the approximation allowance; or
2. recast the paper honestly as a finite-state computational-method paper and stop drawing stronger economic conclusions from the continuous model language.

A generic approximation theorem somewhere in the compendium is not enough. Its assumptions and constants must be applied to the **headline R12 choice**.

---

# 5. F4 — The headline R12 result does not require a neural method

This is now an increasingly serious identity problem for a paper titled **Neural Bellman Operators**.

The R12 central procurement computations are reconstructed by `replication/r12/engine.py`, which performs direct finite-state Bellman optimization over the stored action rows. The independent verifier does not need a neural network. The main text itself says that policy proposal “can be neural or nonneural without changing the validity of these witnesses.”

That statement is mathematically sensible. It also raises the obvious editorial question: **why is the paper called Neural Bellman Operators, and what does the neural component contribute to the headline result?**

The final economic theorem is not a high-dimensional problem for which an approximate neural actor is indispensable. It is a 1,617-state finite target that the paper directly solves and checks. The certification methods—policy polynomials, count-information recursion, signed endpoint correction, secant service bounds—do not intrinsically require neural approximation.

Earlier versions appear to contain neural actors, approximation theory, high-dimensional examples, and neural-free ablations. R12 moves those materials into a compendium while making exact finite-array procurement the main paper. This improves organization but leaves the title and claimed methodological contribution misaligned with the main result.

### Required response

The authors need to choose.

- If the paper is fundamentally about **neural proposal + exact certification**, demonstrate a setting where the neural proposal materially expands the set of economically relevant problems that can be solved/certified relative to exact DP, nonneural proposal methods, and standard approximations. Show end-to-end scaling, not just that the final certificate is independent of the proposal.
- If the strongest result is really about **verified parametric dynamic programming and economic procurement**, retitle and reposition the paper. Neural policy proposal can then be one implementation option, not the defining contribution.

At present, the paper’s strongest theorem is strongest precisely where the “Neural” part is least necessary.

---

# 6. F5 — The all-response service theorem is useful but mathematically elementary

Proposition 1 is correct, but its novelty should not be overstated. Once
[
W(d)=\sup_\pi\{B(\pi)+dA(\pi)\}
]
is recognized as a convex supremum of affine functions, the stated bounds are finite-difference/subgradient bounds with value and near-optimality error. The proof is a few lines of inequalities.

That is a good tool. It solves a real tie-breaking problem in the application. But it is not, by itself, a major theoretical contribution at Econometrica level.

There are ways to make this direction more substantial:
- vector-valued services and multidimensional perturbations;
- identification of the set of service vectors supported by value queries;
- sharpness/minimax results for noisy value oracles;
- endogenous perturbations that also affect transition laws;
- equilibrium rather than single-agent response correspondences; or
- economic identification results that use these intervals to characterize implementability/procurement regions.

At present the paper sometimes gives this lemma too much conceptual burden.

---

# 7. F6 — The opportunity-exposure decomposition is accounting, not yet a primitive economic mechanism

The corrected identity is valuable:
[
\Omega_+-\Omega_-=(g_+-g_-)+(K_+-K_-)O_1+(B_+-B_-).
]

But an identity does not explain the sign of the class difference.

The proposed tail condition says, essentially, that if future option values are monotone in an ordering and the signed kernel difference has the appropriate cumulative-tail ordering, then the signed exposure term is nonnegative. This is a finite summation-by-parts / stochastic-dominance statement. It becomes an economic mechanism only if the two required orderings are derived from economic primitives.

The paper explicitly declines to assert that wealth itself induces the required ordering, and the numerical application uses pointwise signed exposure intervals instead. That is cautious but leaves the mechanism unfinished.

I therefore still do not see a transferable result of the form:

> these primitives of preference adjustment, financial exposure, and surrender imply that class (+) has greater/lower future adjustment exposure than class (-).

What I see is:
- a valid decomposition;
- a generic sufficient dominance condition; and
- several computed pointwise decompositions.

That is not the same thing.

### Required response

Derive at least one nontrivial primitive condition that yields the opportunity ordering and the signed exposure ordering in an economically interpretable class of models. Alternatively, show a broad calibrated region in which the decomposition has a stable dominant component and explain why.

The report should also show cases where the ordering fails. The existing adverse permission and alternative-state cases are useful and should be integrated into this analysis rather than relegated to preservation history.

---

# 8. F7 — The computational comparison is still too internal

The related-work revision is better. The manuscript now acknowledges:
- Alegre, Bazzan, and da Silva (2022) on successor features / optimistic linear support for linearly expressible rewards;
- Quatmann et al. (2016) on regional parameter lifting for parametric probabilistic models; and
- Junges et al. on parameter synthesis / region analysis for parametric Markov chains and MDPs.

These are relevant precedents, and the manuscript appropriately avoids claiming that regional expected-reward control originated here.

But the empirical comparison does not yet meet the implication of that literature discussion. The new “broader law” exercise compares two internal upper constructions—signed chord compression and count-information—on the same model. That is useful engineering evidence, not a field-positioning benchmark.

Quatmann et al. explicitly develop refinable regional upper/lower bounds through parameter lifting; Junges et al. develop and experimentally evaluate algorithms for covering parameter spaces in parametric Markov models; Alegre et al. provide a distinct linearly-expressible-task transfer baseline. The current paper does not compare:

- wall time;
- memory;
- certificate width;
- scaling in state count;
- scaling in horizon;
- scaling in action count;
- scaling in number of uncertain parameters;
- refinement behavior;
- or failure regimes

against any established external implementation or a faithful reimplementation of those relevant approaches.

Nor does it establish a complexity theorem that would make such a comparison unnecessary.

### Required response

Provide a matched benchmark suite with at least:
1. exact DP where feasible;
2. a standard robust/interval DP baseline;
3. an implementation of an appropriate parameter-lifting/regional-synthesis baseline or a careful reason it cannot represent the same object;
4. the count-information method;
5. the signed compression; and
6. neural and nonneural proposal banks where proposal matters.

Report total end-to-end cost, including proposal, endpoint solves, certificate construction, refinement, canonical loading, and verification. A top-journal computational-method claim cannot rest on a single internal method-vs-method table.

**Literature checked for this report:**  
Alegre, L. N., A. Bazzan, and B. C. da Silva (2022), “Optimistic Linear Support and Successor Features as a Basis for Optimal Policy Transfer,” ICML/PMLR 162:394–413.  
Quatmann, T., C. Dehnert, N. Jansen, S. Junges, and J.-P. Katoen (2016), “Parameter Synthesis for Markov Models: Faster Than Ever.”  
Junges, S., E. Ábrahám, C. Hensel, N. Jansen, J.-P. Katoen, T. Quatmann, and M. Volk, “Parameter Synthesis for Markov Models: Covering the Parameter Space,” later published in *Formal Methods in System Design*.

---

# 9. F8 — The economic calibration/generalization remains too synthetic

The procurement environment has many explicit primitives, which is better than an implicit institutional story. But the current numerical values still look designed around the computational example rather than motivated by an economic application:

- (G(u,X)=-0.02(u-2)^2+0.1\log X);
- (C(E)=0.02E^2);
- (D_\kappa(m)=\kappa(m-1)/8);
- (b\approx1);
- (L=0.8,S=0.5);
- (d=0.42425);
- a particular eight-date settlement structure.

The paper calls (A) “service,” but (A) is also deliberately the coefficient on (d), which is exactly why the secant theorem works. That is mathematically elegant, but economically it risks looking reverse-engineered: the metric of purchaser service is chosen to coincide with the sufficient statistic exposed by a perturbation of the agent’s payoff.

What institution has this structure? Why should the purchaser’s service value be proportional to exactly the discounted operating-duration coefficient in the agent’s benefit? Why are capacity cost and term cost split between agent and purchaser in this precise way? Why is the surrender fee external rather than rebated? How sensitive is the procurement result to these assignments?

None of these choices is illegitimate. At Econometrica level they need either a theory showing which of them do not matter or an application giving them institutional content.

### Required response

Give economic primitives or institutional evidence supporting the contract and payment structure, and report sensitivity to:
- fee recipient;
- capacity payer;
- curvature of capacity cost;
- term-cost shape;
- outside option;
- service valuation;
- permission standard;
- and horizon.

Do not treat a tiny ((b,\kappa)) rectangle as a substitute for this.

---

# 10. F9 — The new verifier still has a claim/scope edge that should be closed

The proposed verifier is much stronger than R11’s. I nevertheless see a concrete small mismatch between prose and checking.

For the positive mandate, the economic definition requires a **strictly positive** first risky share (0<\pi_0\le L). The code’s generic `first_mask` uses the closed set at zero for positive-class optimization, which the manuscript correctly explains may be used for an upper supremum. The lower-witness path `first_index` separately rejects a nonpositive positive-class action.

However, in the R12 procurement verification routine, the supplied first action is checked by membership in `first_mask`; that mask itself permits zero. The manuscript then states that the selected positive first shares are strictly feasible.

Because the committed procurement witness is absent at the reviewed SHA, I cannot inspect whether the selected action actually has positive share. The generator probably does select one, but the verifier should check the exact property that the theorem text claims.

### Required response

For every claimed **attained** positive-class lower value / chosen contract, explicitly check (\pi_0>0). Use the closure only where the result is intentionally a supremum upper bound. Deposit that assertion in the independent validation record.

More broadly, continue to describe the checker accurately. It is separately recoded Bellman arithmetic over shared canonical data and shared mathematical definitions. It is not an independent proof assistant, not real interval arithmetic, and not an independent reconstruction of the continuous economic primitives. The current prose generally recognizes this; retain that discipline.

---

# 11. F10 — The paper still needs a single top-journal contribution, not a preserved research program

R12 improves the reader path by moving prior results to a compendium. That is the right editorial move.

But the underlying project remains extremely broad: neural approximation, Bellman operators, policy improvement, preference adjustment, equilibrium extensions, changing-law certificates, reward transfer, regional bounds, surrender, procurement, participation, dynamic transport, and verification. Preserving all historical science in the repository is admirable. It is not a reason to make all of it part of one paper’s claim set.

The new main paper should answer a simple question:

**What is the one result that changes what an economist can prove or compute?**

Right now there are several candidates:
- finite-menu procurement robust to best-response multiplicity;
- changing-law regional certification;
- signed compression of a count-information relaxation;
- neural proposal with exact verification;
- preference-adjustment comparative statics.

None is yet developed deeply enough in the R12 main paper to dominate the others.

For Econometrica, breadth does not compensate for a missing center.

---

# 12. Technical and presentation comments

These are secondary to F1–F10 but should be addressed in any rewrite.

1. **Strict positive mandate.** As noted above, separate the positive-class closure used for upper suprema from actually feasible positive first actions everywhere, including procurement.

2. **(eta)-optimal behavioral interpretation.** Explain why (10^{-8})-optimality is the economically relevant response class rather than merely a numerical tolerance. If it is numerical only, state the economic theorem for exact best responses first and use (eta) as a robustness extension.

3. **Secant step (h).** The text correctly notes the (2\epsilon/h) tradeoff. Show a sensitivity table over several (h)’s and report whether the procurement choice and certified margin are stable.

4. **Second-best contracts.** For each price/cost case, report the actual rival that determines the certified margin. This is economically more informative than only listing the winner.

5. **Grid refinement.** Refine (E) at least around 0.6 and show whether the term switch persists. Otherwise the central “adjustment changes the chosen term” result may be a coarse-grid coincidence.

6. **(F=E).** Explain why fee and capacity are tied one-for-one. If “capacity” means a maximum enforceable fee, one expects the chosen fee to be a decision below the cap rather than mechanically equal to it.

7. **Outside option.** Vary the outside value or derive which part of the result depends on participation binding.

8. **Fee recipient.** The external-sector assumption materially affects purchaser surplus. Show the purchaser-retains-fee case or explain the institution.

9. **Randomized responses.** Proposition 1 allows them. Clarify whether the procurement contract and finite DP admit randomization and whether randomization can strictly change the service set under ties.

10. **Uniqueness language.** The numerical theorem may identify a unique discrete instrument under interval separation. It does not imply a unique optimal agent policy or exact signing payment.

11. **Broader-law stress tests.** Report where and why policy switching occurs. The number of endpoint policy-switching states is more informative if linked to certificate widening.

12. **External benchmarks.** The statement “no comparison here is a benchmark against an entire external parameter-synthesis system” is honest, but it also concedes a central missing experiment.

13. **Array target nomenclature.** Every table and theorem based on R12 arrays should carry the target identity or a short target label so historical R8/R9/R11 results cannot be silently mixed.

14. **Final-deposit provenance.** Once the workflow runs, quote both scientific-source SHA and final-deposit SHA in the paper’s replication note. A self-modifying branch is workable only if that distinction remains explicit.

15. **Workflow as evidence.** A green Actions badge is not a theorem. The deposited validation file and exact identities are the evidence. The manuscript already gestures at this distinction; keep it.

---

# 13. Minimum standard for a fundamentally new submission

I do not recommend treating the following as a mechanical checklist for “R13.” They describe the scale of revision needed before another Econometrica-style assessment would be useful.

| Area | Minimum convincing response |
|---|---|
| Reviewable object | One immutable post-execution commit containing final manuscripts, primitives, witnesses, validation, tables, and receipts. |
| Economic decision | Either a substantively justified institutional menu or a robust/refined/continuous contracting result. |
| Model-target link | A quantitative approximation/transfer argument applied to the headline procurement choice, not only preserved general theory. |
| Method identity | Show why neural proposal is materially needed, or reposition the paper around verified parametric DP rather than neural branding. |
| Mechanism | Derive the signed exposure ordering from economic primitives or demonstrate a broad, interpretable, stable mechanism region. |
| Computational novelty | External baselines plus state/horizon/action/parameter scaling and total end-to-end cost. |
| Economic significance | Calibrated or primitive-based robustness to costs, permissions, service values, fee incidence, outside option, and horizon. |
| Paper architecture | One main question, one primary theorem chain, and one clearly measured computational contribution. |

Depositing the currently queued arrays would resolve only the first row.

---

# 14. Evidence map for this report

All repository references below are at reviewed SHA `5f729aebb334d7861fd19b2ad1861f4949ad6b8f` unless stated otherwise.

**R12 main source**
- `revisions/2026-09-18-r12-procurement-witness/paper/main.tex`
- `revisions/2026-09-18-r12-procurement-witness/paper/S15_proofs.tex`

**Author response and preservation claims**
- `revisions/2026-09-18-r12-procurement-witness/response_to_referee.md`
- `revisions/2026-09-18-r12-procurement-witness/preservation_map.md`
- `REVISION_INDEX.md`

**Canonical-target and verification source**
- `replication/r12/canonical.py`
- `replication/r12/engine.py`
- `replication/r12/science.py`
- `replication/r12/verify.py`
- `replication/r12/render_tables.py`
- `replication/r12/materialize.py`
- `replication/r12/build.py`
- `replication/r12/README.md`

**Deposit workflow**
- `.github/workflows/r12-procurement-witness.yml`
- Actions run `35321946562`; at review time status = `queued`, conclusion = null.
- Job `105526185435`; at review time status = `queued`, runner id = 0, no executed steps.

**Prior report**
- `reviews/2026-09-18-econometrica-r11-service-certificate-audit/referee_report.md`
- response target review commit `442b009379402df7da354eacb4ff8f82d44cdce7`.

**Not present at reviewed SHA**
- `ECTA_R12.tex`, `SUPP_R12.tex`, `COMPENDIUM_R12.tex`;
- the five generated R12 table sources;
- `replication/r12/canonical/manifest.json`;
- `replication/r12/output/expected.json` and all R12 witness/validation output;
- final R12 PDFs and execution receipt.

---

# 15. Final assessment

R12 should not be dismissed as mere repackaging. It makes the economic decision cleaner, corrects the service-versus-value distinction, supplies a valid best-response-robust procurement comparison, repairs the exposure decomposition, and proposes a substantially stronger witness-checking architecture.

But those improvements expose rather than solve the paper’s deeper issue. Once the procurement problem is formulated correctly and the finite-array target is stated honestly, the Econometrica question becomes much sharper:

**Is the resulting economic theorem general and important enough, and is the computational method sufficiently novel and necessary, to justify the paper’s scope and title?**

On the present record, my answer is no. The procurement result is too tied to a synthetic discrete contract menu, the economic theorem is still confined to an unbridged finite target, the headline calculation does not need neural approximation, the mechanism result is not yet primitive, and the computational novelty is not externally benchmarked. In addition, the actual R12 evidence deposit had not completed at the reviewed commit.

I therefore recommend **rejection of R12 in its present form**, while explicitly recognizing that several R11 objections have been substantively answered and should not be reintroduced in future work as if no progress had occurred.
