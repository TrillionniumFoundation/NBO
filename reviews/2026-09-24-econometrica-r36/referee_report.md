# External Referee Report — R36

**Venue perspective:** Econometrica-level numerical and computational methods  
**Article inherited on the reviewed branch:** *Certified Bellman Operators with Neural Proposals: All-Restart Bounds for Costly Policy Revision*  
**Repository:** TrillionniumFoundation/NBO  
**Reviewed branch:** `revision/econometrica-r36-certified-global-revision-2026-09-24`  
**Reviewed HEAD:** `c6cb75418f4d903750d001265f36ff4d568a9330`  
**Last materialized manuscript head:** `d0cfe1b17cc66cde393f4e2d1700270975bb7e30` (R34)  
**Review branch:** `review/econometrica-r36-numerical-methods-2026-09-24-c6cb754`  
**Date:** 2026-09-24

## 1. Recommendation

**Reject in the present form.**

The principal reason is unusually concrete: R36 is not a materialized scientific revision. The reviewed R36 commit adds only a 31-line protocol file. Relative to the R34 manuscript that was previously reviewed, the branch contains the R34 referee report plus the R35 and R36 protocol files, but no R36 manuscript, supplement, point-by-point response, computation report, executable implementation, numerical result objects, proof objects, verifier, build artifacts, or publication manifest.

That distinction is decisive because the R36 protocol makes strong empirical and verification claims. It states that a fresh exact operating dynamic program and a necessary-action cost recursion have been executed for all 42 primary configurations; that lower and upper costs agree exactly in 24 cases, including 12 strictly positive-cost cases; that all 14 horizon-four cases are exact; and that a separately implemented SymPy Rational verifier checked 42 proof objects and rejected 15 corruption categories. None of those new objects is present on the reviewed branch. The reader therefore cannot reproduce, inspect, or even identify the purported 24 exact solutions.

The protocol also describes further referee-directed studies: an exact three-action one-constraint local LP, adaptive whole-cell primal/dual certificates, multiplier-tolerance studies, 66 economic-sensitivity configurations, and a nonlinear multistate extension. Those are sensible responses to earlier objections. On the reviewed branch they are plans, not results.

The inherited R34 paper remains a careful verified-computation paper, but the prior blocking concerns remain materially in force: the positive-cost unrestricted problem was not globally solved, the benchmark was one-dimensional and exceptionally favorable to exact piecewise-affine algebra, the randomized/history-dependent problem was not closed, and the original stopped consumption-portfolio target remained unsolved. R36 supplies no reviewable evidence sufficient to change those conclusions.

There is one potentially important idea in the R35/R36 protocol: using the exact operating value to form a pointwise necessary-action outer class and then solving the implementation-cost Bellman recursion on that outer class. That construction can provide a valid lower bound for the deterministic Markov revision problem, and equality with a separately feasible upper policy can certify a deterministic optimum. If the claimed 12 positive-cost exact cases are actually materialized and independently verified, that would be a genuine improvement over R34. But a protocol assertion is not a computational result, and a benchmark-specific argument that requires exact access to the operating value is not yet an Econometrica-level general numerical method.

I therefore recommend rejection of the submitted R36 object as both scientifically incomplete and substantively unchanged at the manuscript level.

## 2. What actually changed from R34 to R36

The repository delta is small and should be stated explicitly.

From the R34 manuscript head `d0cfe1b17cc66cde393f4e2d1700270975bb7e30` to R36 HEAD `c6cb75418f4d903750d001265f36ff4d568a9330`, the branch adds only:

1. `reviews/2026-09-24-econometrica-r34/referee_report.md`;
2. `revisions/2026-09-24-r35/PROTOCOL.md`;
3. `revisions/2026-09-24-r36/PROTOCOL.md`.

The inherited R34 publication objects are still present:

- `ECTA_R34.tex` / `ECTA_R34.pdf`;
- `SUPP_R34.tex` / `SUPP_R34.pdf`;
- `RESPONSE_R34.tex` / `RESPONSE_R34.pdf`;
- `COMPUTATION_R34.tex` / `COMPUTATION_R34.pdf`;
- the R34 source tree, results, replication code, and publication manifest.

By contrast, the following natural R36 submission objects do not exist on the reviewed branch:

- `ECTA_R36.tex`;
- `SUPP_R36.tex`;
- `RESPONSE_R36.tex`;
- `COMPUTATION_R36.tex`;
- `revisions/2026-09-24-r36/paper/main.tex`;
- `revisions/2026-09-24-r36/results/summary.json`;
- `revisions/2026-09-24-r36/PUBLICATION_MANIFEST.json`.

This is not a stylistic complaint about naming. The R36 protocol itself promises a new Econometrica-format manuscript, full technical supplement, point-by-point response, computation report, source manifest, historical annex, executed numerical results, completed builds, and precise publication provenance. None is materialized.

Accordingly, the only scientifically reviewable paper on R36 is still R34.

## 3. What the R35/R36 necessary-action idea could establish

The new protocol contains one mathematically meaningful direction that deserves a precise assessment.

Let (V_t) denote the exact optimal operating value, and let
[
T^a V_{t+1}(x)
]
be the one-step operating value from action (a) followed by optimal continuation. Suppose a deterministic Markov policy (pi) satisfies the all-restart operating constraint
[
V_t(x)-J_t^pi(x)le arepsilon
]
for every ((t,x)). At a state where (a=pi_t(x)),
[
J_t^pi(x)=T^a J_{t+1}^pi(x)le T^a V_{t+1}(x).
]
Therefore
[
V_t(x)-T^a V_{t+1}(x)
le
V_t(x)-J_t^pi(x)
le arepsilon.
]

Hence every action used by a feasible deterministic Markov policy lies in the necessary set
[
mathcal N_t(x)
=
left{
a:
V_t(x)-T^aV_{t+1}(x)learepsilon
ight}.
]

A Bellman recursion minimizing implementation cost over (mathcal N_t(x)) therefore optimizes over a **superset** of the feasible deterministic policies. Its value is a lower bound on the true deterministic constrained revision cost. If a separately evaluated feasible policy has exactly the same initial integrated cost, then the deterministic constrained optimum is certified.

This is a useful observation. It directly targets the R34 criticism that the paper did not solve positive-cost cases.

However, four qualifications are essential.

First, this is a deterministic-policy lower bound unless an additional argument is supplied. The R35/R36 protocols correctly warn that it is not automatically a randomized lower bound. The manuscript must preserve that distinction everywhere, including title, abstract, tables, and conclusions.

Second, equality of an **integrated** lower bound and an integrated feasible upper cost certifies the stated initial-distribution objective. It does not by itself establish that the deployed policy is cost-minimizing from every restart. If the paper wants a stronger statewise optimality claim, it must prove equality of the cost functions or give a separate argument.

Third, construction of (mathcal N) requires the exact operating value (V). In the present one-dimensional affine benchmark that value is cheap. In the difficult dynamic programs motivating the numerical paper, exact (V) is precisely the object that is generally unavailable. The necessary-action method is therefore a strong benchmark/reference method unless the authors explain how it remains usable when exact operating DP is not available.

Fourth, the necessary set can be substantially larger than the truly feasible constrained set because it ignores accumulation of future operating loss. Equality with a feasible upper policy can overcome that looseness case by case, but absent equality the method gives no convergence mechanism on its own.

If the claimed 24 equalities are real, they are worth reporting. They still do not establish a general globally convergent revision algorithm.

## 4. Blocking scientific findings

### R36-F1 — The claimed revision is not present

A referee cannot review a computation that exists only in a protocol paragraph.

R36 says that 42 exact constructions were executed, 24 deterministic global optima were certified, 12 of those have strictly positive implementation cost, all 14 horizon-four cases are exact, and 42 proof objects passed an independent verifier.

There are no R36 result JSON files, no proof-object archive, no exact-cost tables, no source code implementing the necessary-action recursion, no verifier source, no mutation-test record, no execution ledger, and no publication manifest.

The branch therefore contains assertions of results without the results themselves.

**Required correction:** materialize the complete R36 scientific object. The minimum acceptable package is the new manuscript, technical supplement, response, computation report, exact result files, proof objects or canonical hashes, executable source, independent verifier, mutation-test results, build logs, and publication manifest.

### R36-F2 — The manuscript is unchanged from the version that received a rejection recommendation

The paper object inherited on R36 is still R34.

The title remains *Certified Bellman Operators with Neural Proposals: All-Restart Bounds for Costly Policy Revision*. The abstract still reports 42 deployments, 22 tightened intervals, 12 zero-cost global optima, 294 audited R34 certificates, and remaining positive global gaps. It does not report the claimed R35/R36 result that 24 deterministic cases are now exact, including 12 positive-cost cases.

Thus even if the protocol's local execution really occurred, it has not been incorporated into the paper.

This matters editorially and scientifically. A submission is not revised merely because a branch contains a plan for a future revision.

**Required correction:** update the actual article and supplement, with the new theorems, policy-class distinctions, tables, numerical evidence, limitations, and response to the previous report.

### R36-F3 — The exact-value necessary-action method is a reference solver unless scalability is demonstrated

The proposed deterministic lower bound uses exact (V_t).

On the current maintenance benchmark, exact operating dynamic programming was already reported to take only milliseconds to tenths of a second. Exploiting that exact (V) to derive necessary actions is perfectly legitimate as a **same-object reference computation**. Indeed, this is closer to the strong comparator requested in the R34 report.

It is not yet evidence of a numerical method that makes difficult high-dimensional economic models tractable. Exact (V) is the main unavailable object in those settings.

The paper must therefore choose its interpretation.

If this is a benchmark/reference method, say so and use it to measure sharpness of the certificate framework.

If it is proposed as the new main algorithm, explain how the exact-(V) requirement is replaced by certified approximations without invalidating the outer-class lower bound.

**Required correction:** separate “exact benchmark certification” from the scalable method. Charge the exact operating solve, report its complexity, and do not let exact-(V) benchmark success stand in for high-dimensional capability.

### R36-F4 — Deterministic exactness does not close the randomized/history-dependent problem

The inherited R34 article emphasized lower bounds over a broad operating-feasible set, including randomized Markov policies and a stated history-conditioned extension.

The R35/R36 necessary-action lower bound is explicitly deterministic. That is scientifically cleaner than conflating policy classes, but it changes the solved object.

A randomized policy can mix actions whose individual deterministic behavior does not reproduce the same operating-cost tradeoff. The exact local LP proposed later in the protocol acknowledges this issue.

Therefore a statement such as “24 global optima” is incomplete unless it always reads “24 deterministic Markov optima under the specified initial objective” or an equally precise formulation.

**Required correction:** provide a formal policy-class theorem. Either prove deterministic sufficiency for the stated constrained objective under the model's structure, or keep deterministic and randomized optima separate in every theorem and table. Do not allow deterministic equality to inherit the R34 paper's broader “full feasible policy set” language.

### R36-F5 — The meaning of “exact” is not fully specified

R35 says exact deterministic optimality is declared when the **integrated** necessary-action lower cost and feasible upper cost agree.

That is enough to solve the initial-distribution objective if both quantities are valid. It is not automatically enough to claim that the deployed policy is optimal from every state and restart.

The paper's operating constraint is all-state/all-restart, but its reported economic cost is integrated under a specified initial distribution. Those two scopes must not be blurred.

**Required correction:** for every “exact” case report:

- the exact policy class;
- the exact objective being optimized;
- whether equality is only at the initial integrated objective or pointwise in the cost-to-go function;
- the exact rational lower and upper values;
- the deployed feasible policy hash;
- the lower-bound function hash;
- the proof that all-restart operating feasibility holds.

### R36-F6 — The same-object classical comparison remains incomplete for the broad problem

The necessary-action recursion may become an excellent deterministic reference solver on the present benchmark. That would materially improve R34.

But it still does not provide the strong same-object comparison for the randomized/global constrained problem that the R34 paper discusses.

On a one-dimensional, three-action, finite-horizon, piecewise-affine benchmark, the paper should make an unusually strong effort to solve the actual constrained problem directly or to explain rigorously why it remains difficult.

Potential routes include exact parametric constrained dynamic programming, occupation-measure formulations on a verified partition, augmented-state budget recursions, or an exact LP formulation after finite structural reduction. The particular method is less important than solving the same objective and policy class.

**Required correction:** include a direct comparator for the exact constrained problem the headline claims concern, or narrow the paper explicitly to deterministic policy revision.

### R36-F7 — The exact local LP repairs only a local discretization defect

R34 used an eight-point multiplier grid in the restart propagation. The R35/R36 protocol proposes replacing the statewise three-action one-constraint relaxation by an exact primal/dual LP and adaptive whole-cell certificates.

This is a good correction.

It does not establish global strong duality for the original constrained revision problem. The protocol itself correctly says the convergence theorem concerns approximation to the continuous **local restart relaxation**, not the structural global duality gap.

Therefore this improvement cannot be used to imply that the remaining global support/restart interval converges to zero.

The protocol also says the local cost floor is held at zero in the diagnostic and explicitly warns that this does not decompose the R34 nonzero support floor. That limitation should remain prominent.

**Required correction:** quantify separately:

1. error from local multiplier discretization;
2. error from operating-witness approximation;
3. error from the global support lower bound;
4. looseness from the necessary current operating inequality;
5. upper-policy search error.

Then state exactly which component the local LP eliminates.

### R36-F8 — Eighteen primary cases remain unresolved even under the protocol's own headline

The R36 protocol says 24 of 42 configurations are exact and the remaining 18 retain nonzero intervals.

That would be substantial progress if documented, especially because 12 newly exact cases reportedly have positive cost.

It still leaves almost half of the declared primary cohort unresolved. No convergence rate or certified stopping rule is provided for those 18 cases.

All 14 horizon-four cases are said to be exact, which strongly suggests that model size is central to closure. The paper should use that pattern to identify precisely what prevents exactness at horizons 8 and 12: action-set geometry, upper-candidate insufficiency, cost-function complexity, or lower-bound looseness.

**Required correction:** provide a gap decomposition for all 18 unresolved cases and a horizon-scaling study that shows whether the failure is algorithmic, representational, or computational.

### R36-F9 — The nonlinear multistate extension is only a protocol target

R34's most serious external-validity limitation was the one-dimensional exact affine geometry.

R35/R36 proposes a two-state nonlinear maintenance economy with bilinear transitions, four actions, two shocks, meshes up to 256 per dimension, outward integer enclosures, and horizons up to 32. This is exactly the kind of extension needed to test whether the method survives loss of one-dimensional piecewise-affine closure.

But none of it is present on R36.

The protocol itself records that an initial zero-penalty pilot failed all sixteen configurations through mesh 128. That is scientifically useful information and should be retained. The later operating-priority generator and mesh-256 amendment must be reported as exploratory, not as if prospectively fixed.

**Required correction:** publish the complete multistate experiment, including failed certificates, discretization error, enclosure logic, memory, runtime, mesh sensitivity, and a strong numerical baseline. Do not use a looser operating tolerance in the multistate example to imply comparability with the primary cohort.

### R36-F10 — The economic-sensitivity program is sensible but absent and still uncalibrated

The R35/R36 protocol proposes 66 one-at-a-time sensitivity configurations varying discounting, revision weights, initial density, maintenance cost, defer persistence, and installed rules.

That is a useful response to the criticism that the occupancy result was concentrated in an engineered stress policy and that the revision cost lacked economic interpretation.

Again, there are no R36 sensitivity results.

Even if the 66 normalized examples are eventually supplied, the protocol correctly notes that they are not a dollar calibration and not a random population sample. The paper should not convert frequency across those hand-chosen cases into an empirical prevalence claim.

**Required correction:** report all sensitivity outcomes, including zero effects and failed certificates, and distinguish illustrative comparative statics from empirical calibration.

### R36-F11 — The claimed independent verifier cannot be evaluated

R36 says a separate SymPy Rational row/partition verifier imports no Fraction/PW constructor, affine-composition routine, or optimizing-envelope routine, and rejects 15 corruption categories.

If true, that would materially improve the R34 concern about common-mode implementation errors.

No verifier source or R36 mutation-test artifact is present.

Independence is a property of code and dependencies, not a prose description.

**Required correction:** commit the verifier, dependency manifest, exact input contract, mutation generator, expected failures, and per-object verification record. The paper should identify any shared model primitive definitions or serialized representation code so that residual common-mode risk is transparent.

### R36-F12 — The protocol contradicts its own publication discipline

R36 states: “Only actual executed numerical results and actual completed builds may be reported as passing.”

Yet the same protocol reports 42 completed primary executions, 24 exact cases, 12 positive-cost exact cases, all 14 horizon-four cases exact, 42 passed proof objects, and 15 rejected corruption categories without materializing the underlying results or builds.

This is precisely the separation between assertion and evidence that a verified-computation paper should avoid.

**Required correction:** do not report a run as a publication-level result until its exact outputs, source hashes, verifier results, and build provenance are in the reviewed commit.

### R36-F13 — Neural proposals remain peripheral to the strongest numerical content

The R34 article is admirably candid that it establishes no neural speed advantage and that none of the 18 raw neural proposals meets its operating target.

Nothing in R35/R36 changes that evidence. The proposed exact deterministic lower bound relies on exact operating dynamic programming, not a neural representation. The exact local LP and independent rational verifier are also classical numerical objects.

The title still gives “Neural Proposals” a defining role.

**Required correction:** either demonstrate a measurable neural-specific advantage in constructing, tightening, or scaling the certificates, or further demote neural language from the paper's identity.

### R36-F14 — The original stopped consumption-portfolio problem remains outside the solved method

The R34 paper retains the original all-domain stopped control target and proves only a scalar constant-control optimum at one active-boundary restart.

R35/R36 explicitly says the stopped program is retained unchanged and must not be represented as solved by the maintenance results.

That is correct scientific discipline. It also means the paper still contains two research programs: a certified maintenance-revision method and an unresolved stopped-control objective.

**Required correction:** either provide a genuine method-level connection to the original stopped-control target or move the stopped-control program to a historical/auxiliary document. The main Econometrica article should have one coherent solved object.

## 5. Technical comments that should be addressed in a real R36 manuscript

### R36-T1 — State and prove the necessary-action lemma explicitly

The proof is short but central. It should be a formal proposition with an exact policy class and filtration. The paper should not rely on the protocol's prose description.

### R36-T2 — Clarify history-dependent deterministic policies

If the lower bound is claimed for deterministic history-dependent policies, define feasibility after every admissible history, not merely by state. Then show why the Markov cost recursion over the necessary outer set remains a lower bound.

### R36-T3 — Report exact reference values, not only counts

“24 exact” is not enough. Publish the exact lower and upper rational costs for all 42 configurations, plus decimal renderings for readability.

### R36-T4 — Explain why all 14 horizon-four cases close

This pattern is scientifically informative. Identify whether closure is due to upper-candidate richness, exact necessary-set geometry, short-horizon coincidence, or another property.

### R36-T5 — Charge the exact operating solve

The new deterministic lower bound consumes exact (V). Its runtime, memory, piece count, and bit growth belong in the total computational account.

### R36-T6 — Separate diagnostic exact-(V) results from deployable certification

If exact (V) is used only to establish benchmark truth, that is valuable. Do not present the diagnostic solver as the scalable deployment procedure.

### R36-T7 — Define the exact LP frontier carefully

With three actions and one linear operating inequality, the statewise randomized relaxation can be solved by primal vertices or dual line intersections. The manuscript should state degeneracy handling, ties, isolated partition points, and exact rational arithmetic rules.

### R36-T8 — Prove the whole-cell adaptive certificate

If the local frontier becomes rational rather than piecewise affine, the adaptive cell proof must control the entire cell, not sampled points. State the quadratic sign test and the certified termination condition.

### R36-T9 — Keep global and local multipliers conceptually separate

The exact local LP does not automatically optimize the global support multiplier portfolio. Use different notation and separate error tables.

### R36-T10 — Provide a true gap decomposition

For each unresolved case, report how much lower-bound improvement comes from exact (V), local LP exactness, restart propagation, and any expanded upper-candidate portfolio.

### R36-T11 — Report warm and cold costs consistently

Inherited installed policies should remain explicitly amortized inputs. Fresh exact operating solves, cost recursions, verifiers, multistate constructions, and all R36-specific code must be charged.

### R36-T12 — Audit the independent verifier's parser and model primitives

A different arithmetic kernel is useful, but a verifier can still share erroneous serialized transitions or action labels. Mutation tests should target those fields directly.

### R36-T13 — Preserve unsuccessful multistate runs

The protocol promises this. The final archive should include the sixteen failed pilot configurations and any parameter amendments in chronological order.

### R36-T14 — Do not turn the 66 sensitivity cases into a pseudo-sample

The eleven specifications and three installed rules are designed scenarios. Report sensitivity, not prevalence.

### R36-T15 — Tighten terminology around “global”

Use “global over deterministic Markov policies,” “global over randomized Markov policies,” and “global over the stated history-conditioned class” separately. The word “global” without a policy-class qualifier is no longer acceptable in this revision.

## 6. Minimum bar for a materially stronger submission

I would not recommend another revision branch that contains only protocols, intentions, or locally asserted execution counts.

A materially reviewable next submission should satisfy the following.

1. **Materialize the paper revision.** Commit the new Econometrica manuscript, supplement, response, computation report, and source tree.

2. **Materialize every headline numerical claim.** The 42-case table, 24 exact deterministic cases, 12 positive-cost exact cases, 18 unresolved intervals, and all horizon-four results must exist as exact machine-readable outputs.

3. **Provide the executable necessary-action solver.** The code must construct exact (V), the necessary action sets, the cost lower recursion, feasible upper candidates, and exact integrated comparisons.

4. **Provide the genuinely separate verifier.** Commit the SymPy implementation, dependency information, 15 corruption tests, and complete verification ledger.

5. **State the policy class exactly.** Deterministic Markov, randomized Markov, and history-dependent claims must never be pooled.

6. **Use the exact deterministic solver as a benchmark, not as unqualified scalability evidence.** Report its full cost and explain its dependence on exact operating (V).

7. **Address the randomized constrained optimum.** Either solve it on the present benchmark or prove a model-specific deterministic-sufficiency result. Otherwise narrow the headline contribution.

8. **Convert the local multiplier correction into a theorem and experiment.** Show certified convergence to the continuous local relaxation and quantify the residual global duality gap separately.

9. **Execute the nonlinear multistate extension.** Include discretization error, mesh refinement, runtime, memory, failed cases, and a strong baseline.

10. **Publish the economic sensitivities.** Include all declared scenarios and preserve null results.

11. **Resolve the paper's identity.** If neural proposals remain nonessential, remove them from the title-level contribution. If they are essential, show a numerical advantage.

12. **Focus the article.** The unresolved stopped consumption-portfolio program should not compete with the maintenance-certification contribution unless the new method materially advances it.

## 7. Recommendation to the editor

**Reject in the present form.**

The R36 protocol points toward several changes that could make the work materially stronger. In particular, exact deterministic certification of positive-cost cases would address a central weakness of R34, and a truly independent rational verifier would strengthen the computational evidence.

But those are not the contents of the submitted branch. The scientific manuscript is unchanged from R34, while the new results exist only as protocol assertions. A verified-computation paper must hold itself to a higher standard than this: the proof objects, code, outputs, and build provenance are part of the scientific claim.

Even if the missing artifacts are later supplied, the methodological bar remains substantial. The exact-(V) necessary-action method is strongest as a benchmark/reference solver on the present small model; deterministic exactness does not automatically solve the randomized problem; the local exact LP does not establish global strong duality; the multistate and sensitivity studies must be executed rather than proposed; and the original stopped-control target remains outside the solved scope.

A future submission containing the promised material should be evaluated as a new scientific revision, not as a minor update to R36.

## 8. Source map inspected

### Reviewed R36 state

- `revisions/2026-09-24-r36/PROTOCOL.md`
- R36 commit `c6cb75418f4d903750d001265f36ff4d568a9330`
- `revisions/2026-09-24-r35/PROTOCOL.md`
- R35 commit `39d160ec712c33c8ce965721c80055f1b94b4825`

### Inherited R34 publication object

- `ECTA_R34.tex` / `ECTA_R34.pdf`
- `SUPP_R34.tex` / `SUPP_R34.pdf`
- `RESPONSE_R34.tex` / `RESPONSE_R34.pdf`
- `COMPUTATION_R34.tex` / `COMPUTATION_R34.pdf`
- `R34_REVIEW.md`
- `revisions/2026-09-24-r34/PUBLICATION_MANIFEST.json`

### Main inherited R34 sources inspected

- `revisions/2026-09-24-r34/paper/main.tex`
- `revisions/2026-09-24-r34/paper/global_theory.tex`
- `revisions/2026-09-24-r34/paper/restart_theory.tex`
- `revisions/2026-09-24-r34/paper/global_results.tex`
- `revisions/2026-09-24-r34/paper/restart_results.tex`
- `revisions/2026-09-24-r34/paper/response.tex`
- `revisions/2026-09-24-r34/paper/generated/timing.tex`
- `revisions/2026-09-24-r34/paper/generated/occupancy.tex`

### Prior referee baseline

- `reviews/2026-09-24-econometrica-r34/referee_report.md`

This report reviews the exact R36 branch state identified above and intentionally modifies no revision branch.
