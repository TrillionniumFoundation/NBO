# Referee Report — Neural Bellman Operators, latest R21 review snapshot

**Venue standard:** Econometrica-level numerical / computational methodology  
**Recommendation:** **Reject in the present form. The revision has made real progress on policy-sensitive verification, but the evidence now creates a sharper problem for the paper's methodological identity: the successful local policies are restricted neural-generated control schedules, while the actual full-state Neural Bellman Operator remains inaccurate; and the closest same-family non-neural optimizers are at least as accurate and materially cheaper.**  
**Review date:** 2026-09-23  
**Review snapshot branch:** revision/econometrica-r21-policy-sensitive-2026-09-23  
**Snapshot head:** 6951c3b01b5102ef3d743a6ab14f9cc595b08804  
**Latest materialized journal manuscript in the snapshot:** ECTA_R19.tex / ECTA_R19.pdf  
**Latest materialized supplement:** SUPP_R19.tex / SUPP_R19.pdf  
**Latest materialized response:** RESPONSE_R19.tex / RESPONSE_R19.pdf  
**R19 publication commit inherited by the snapshot:** 01aa2b410dca6f08489f68ada21fdf4b997944f7  
**Post-manuscript R20 evidence head inherited by the snapshot:** 6916f250ca2115399dccf2df125c0b13f304547b  
**Previous referee report:** reviews/2026-09-23-econometrica-r18/referee_report.md  
**Review branch:** review/econometrica-r21-numerical-methods-2026-09-23

## 1. Executive assessment

This is the first revision in this sequence that convincingly solves the narrow identification problem emphasized in my R18 report: a smaller joint actor/critic certificate is not, by itself, evidence that the actor improved. R19 introduces fixed-policy payoff intervals, separates policy evaluation from the unrestricted optimal upper comparison, and accepts a new actor only when its independently checked payoff lower bound exceeds the incumbent payoff upper bound. On the newly generated time-control policies, the reported reference-state regret bounds fall from roughly 0.039 to roughly 0.00976, and the initial-to-final policy payoff gain is certified on the small rectangle K. This is a substantive improvement.

The new R20 execution is also technically serious. It preregisters five seeds, four initial-state vertices, four work budgets, a policy-value acceptance gate, direct stochastic and deterministic comparators, and an independent MPFR arithmetic pass. All 20 final neural policies are certified by the production checker and by the MPFR path, with overlapping reported intervals. The final vertex regret bounds are roughly 0.00260–0.00291. I did not find an obvious local contradiction in the R19 policy-value separation proof or in the R20 directed-payoff checker during this audit.

These improvements do not, however, establish the paper's headline numerical-method claim.

The central full-state feedback Neural Bellman Operator remains where R18 left it: its best complete-domain certificate is about 7.2783 against the unchanged 0.01 target. The successful R19 policy is not a full-state feedback NBO. It is a neural-generated 16-slab time-control schedule with zero portfolio and a hand-specified initial-wealth shift. The successful R20 object is more adaptive, but the neural network itself takes only the time slab as input and outputs the parameters of a hand-specified logistic consumption rule; stochastic state dependence enters through the fixed decoder, and the portfolio is supplied by an analytic self-financing replication formula.

Most importantly, R20 contains the cleanest ablation of the neural representation in the repository, and it is unfavorable to the neural method. A direct L-BFGS-B optimizer over the same 16-slab stochastic logistic family, with no hidden neural layers, obtains a lower certified regret than every one of the five neural seeds at every one of the four vertices. Its four-vertex generation cost is about 1.14 seconds, versus about 10.63–10.79 seconds for one four-expert neural seed. Verification cost is essentially common. The direct parameterization therefore gives slightly better certified policies with much less policy-generation work in the closest matched R20 comparison.

R19 already contains the same warning in milder form. At the reference state, SLSQP-16 obtains a certified regret bound 0.009722 in 2.656 seconds, while the best reported neural run obtains 0.009757 in 11.727 seconds. SLSQP-32 and SLSQP-64 are sharper still. The manuscript correctly says that it does not establish a neural speed advantage. The problem is stronger: at present the evidence does not establish a numerical advantage of the neural parameterization at all on the problems where the sharp policy certificates are obtained.

My recommendation is therefore **Reject**. The revision is scientifically much stronger, but the strongest new evidence supports a paper about validated policy evaluation, policy-value-separated acceptance, and certification of restricted stochastic controls. It does not yet support an Econometrica-level claim that Neural Bellman Operators are an accurate or competitive numerical method for the original full dynamic problem.

---

## 2. Review-object integrity

The current branch is not yet a clean journal revision object.

The R21 head, 6951c3b..., adds only an immutable-source workflow. Its parent contains the executed R20 numerical evidence. There is no ECTA_R20 or ECTA_R21 manuscript, no corresponding technical supplement, no R20/R21 point-by-point response, and no current publication manifest tying the new experiments to a compiled referee copy. REVISION_INDEX.md is stale and still declares R16 as the current review object.

Consequently I have reviewed two layers:

1. the latest materialized manuscript, R19, including its supplement and response; and
2. the newer R20 preregistered execution inherited by the R21 snapshot.

That is enough to assess the scientific trajectory, but it is not acceptable as a final submission package.

### R21-F0 — Blocking: the latest numerical evidence is not materialized into a reviewer-facing paper

The R20 protocol says that the new results will be added to the main manuscript, supplement, proofs, and referee response. That step has not occurred in the reviewed snapshot. In particular, the R20 result records repeatedly state that a four-corner mixture separately proves K-uniform transfer, but no R20 paper/proof file containing that new mixture theorem is materialized in the branch.

A future round must provide one immutable review object: manuscript, supplement, response, proof sources, result manifest, exact source/result commits, and compiled PDFs.

---

## 3. What the revision genuinely fixes

### 3.1 Policy improvement is finally separated from witness improvement

R19's Proposition on separated acceptance is the correct conceptual response to the main R18 objection. The policy evaluator supplies L_pi and U_pi for one fixed policy. A different object supplies the unrestricted upper comparison. A proposal is accepted only through a payoff ordering, not through a joint actor/critic residual decrease.

This is the right distinction.

The new experiments then actually use it. At the reference state, all fifteen prescribed noninitial R19 checkpoints pass a strict fixed-policy value gate. R19 also certifies a positive initial-to-final payoff difference over K rather than inferring improvement from a smaller Bellman envelope.

### 3.2 The paper now acknowledges the old full-state attribution failure

The all-seed actor-critic factorial table is exactly the audit requested in the previous report. For all ten retained full-state feedback seeds, initial actor plus final critic reproduces the final certificate, and the final negative/policy component is zero. R19 correctly concludes that the old complete-cover experiment demonstrated witness improvement, not identified actor improvement.

This issue is now resolved as an attribution question.

### 3.3 The local policy certificates are numerically sharp

The R19 reference-state bounds 0.009756577–0.009774061 are genuinely close to the declared 0.01 threshold. The new R20 vertex bounds are much sharper, roughly 0.00260–0.00291. These are not the 7-unit feedback certificates of R18.

The production R20 checker is also accompanied by a distinct MPFR arithmetic path. All 20 final policies are certified and all reported interval families overlap. This is useful arithmetic redundancy, even though the two paths share the same mathematical derivations.

### 3.4 The continuation problem is diagnosed more constructively

R19 evaluates a fixed-policy one-sided continuation value and obtains a certified continuation excess exceeding 6.708771 on the stated preference segment. This gives a constructive policy-induced trace target without pretending to know the optimal value.

The scalar-bias intervention is also informative: forcing the old critic to satisfy the trace requirement worsens the global complete-cover bound to roughly 22.7–23.4. Thus the paper correctly demonstrates that repairing the boundary trace is necessary but not sufficient.

### 3.5 The high-dimensional warm-start section is more honest and more useful

The manuscript now separates the initialization-agnostic strong-convexity theorem from the learned-quality statement. It compares neural, zero, and accelerated starts at matched directed tolerances. At dimensions 8 and 32, the neural initializer reduces correction counts on the declared finite query sets. At dimension 128, the advantage is limited and acceleration wins at the strictest tolerance.

That is a scientifically appropriate result.

---

## 4. Decisive numerical facts

### 4.1 R19 localized original-economy results

| Object | Certified result |
|---|---:|
| Neural reference-state final regret | 0.0097566–0.0097741 |
| Neural K-uniform bound | 0.011816625 |
| Minimum certified initial-to-final gain over K | 0.016513 |
| Best full-state feedback certificate retained from R18 | about 7.278319 |
| SLSQP-16 reference-state regret | 0.009721598 |
| SLSQP-32 reference-state regret | 0.009703089 |
| SLSQP-64 reference-state regret | 0.009698614 |
| Best neural matched-table generation + evaluation | 11.727 s at bound 0.009757 |
| SLSQP-16 generation + evaluation | 2.656 s at bound 0.009722 |

The sharp R19 neural result therefore concerns a small localized time-control problem. The full-state feedback NBO remains inaccurate, and the direct classical transcription is already sharper and cheaper at the reference state.

### 4.2 R20 matched stochastic-family comparison

The R20 direct comparator optimizes the same 16-slab logistic stochastic-control family without hidden neural layers. At every vertex its final certified regret is lower than the best of the five neural seeds:

| Vertex (u,x) | Best neural final regret | Direct L-BFGS-B regret |
|---|---:|---:|
| (1.98, 1.24) | 0.00261423 | 0.00258714 |
| (1.98, 1.26) | 0.00289021 | 0.00283871 |
| (2.02, 1.24) | 0.00268963 | 0.00266465 |
| (2.02, 1.26) | 0.00260023 | 0.00255442 |

The comparison is not rescued by work accounting. Training the four experts for one neural seed through 1000 Adam steps costs about 10.63–10.79 seconds of generation time. The four direct L-BFGS-B solves together cost about 1.14 seconds. Verification is about 30 seconds in both cases because both are passed through essentially the same expensive checker sequence.

Even at early work, the direct optimizer is stronger: after only 10 L-BFGS-B iterations, every vertex has a lower certified regret than the best neural seed after 100 Adam updates.

This is the closest controlled experiment in the repository for the value of the neural parameterization itself. Its conclusion is adverse.

---

## 5. Blocking scientific findings

### R21-F1 — Blocking: the full-state Neural Bellman Operator still does not solve the flagship problem

The paper retains the title Neural Bellman Operators and repeatedly states that the ultimate objective is an accurate solution over the full state-time domain.

That object has not improved to the target regime.

The best retained complete-domain full-state feedback certificate remains about 7.2783, versus 0.01. R19 explicitly preserves this fact. R20 does not execute a new full-state complete-cover NBO. It executes a different restricted stochastic policy family.

The revision has therefore solved a local policy-computation problem without solving the central NBO problem.

For an Econometrica numerical-method paper, this distinction is dispositive. A strong restricted policy can be an important benchmark or subroutine. It cannot be used as evidence that the named full-state Bellman method is accurate.

### R21-F2 — Blocking: the successful R19/R20 policies are not the method named in the title

The R19 actor maps time-slab midpoints into a 16-slab deterministic time-control schedule, sets the portfolio to zero, and uses a hand-specified affine initial-wealth transfer. It is neural-generated, but it is not a state-feedback Bellman operator.

R20 is more sophisticated, but the same issue remains in a different form. The Actor network is evaluated on the time slab. It outputs the schedule parameters b, s, and theta. The stochastic dependence of consumption on the traded Brownian factor is hard-coded through the logistic decoder, and the portfolio is produced by a fixed analytic replication formula.

Thus the adaptive structure that makes R20 substantially better is not learned state feedback in the NBO sense. It is a hand-designed stochastic policy class whose coefficients are generated by a small network.

This can be a valid numerical method. But the paper must either show why this architecture is itself the intended NBO object, or stop using these local restricted-policy successes as evidence for the full-state neural Bellman method.

### R21-F3 — Blocking: the cleanest representation ablation favors the non-neural parameterization

R20 is particularly informative because its classical stochastic comparator removes only the hidden neural layers while retaining the same 16-slab stochastic logistic form and the same certifier.

It wins at all four vertices.

This is stronger evidence than saying no neural speedup is established. It says that, in the current controlled experiment, the hidden network is an inferior parameterization: slightly worse final certified policies and about nine times more policy-generation work per four-vertex solve.

A top numerical-method paper cannot treat the neural representation as a methodological contribution while the closest same-family ablation consistently improves both accuracy and generation cost.

A future revision needs a regime in which the learned representation changes the certified accuracy-work frontier, not merely a statement that the neural result is also accurate.

### R21-F4 — Blocking: the continuum claim for R20 is not reviewable in the current snapshot

The R20 protocol promises four-corner concavity and a self-financing mixture theorem to transfer vertex inequalities to all of K. The result JSON files state that four-corner mixing separately proves K-uniform transfer.

But the reviewed tree contains no R20 manuscript or proof directory and no materialized theorem establishing that claim for the new stochastic Y-dependent, hedged policies.

The R19 transfer theorem is for a different time-control construction and cannot simply be assumed to cover the R20 four-expert stochastic mixture.

Therefore the 20 vertex certificates are reviewable; the claimed K-uniform R20 conclusion is not yet reviewable as a theorem in this snapshot.

### R21-F5 — Major: the 0.01 success is local, not a full-domain solution

R19 meets 0.01 only at the single reference state. Its reported K-uniform bound is 0.011816625, above 0.01. The full-state feedback certificate is still about 7.28.

R20 has sub-0.003 vertex certificates and may ultimately support a stronger K result once its mixture theorem is materialized, but it remains a small initial-state rectangle and a restricted policy architecture.

The paper is careful about these scopes in several places. The title and numerical-method identity nevertheless continue to invite a broader interpretation than the evidence supports.

### R21-F6 — Major: the sharp policy certificates rely on an inherited non-neural unrestricted dual

Both R19 and R20 use the inherited R16 unrestricted dual as the optimal upper comparison. This is scientifically legitimate and the manuscript discloses it.

However, it matters for the numerical-method claim. The sharp regret certificate is not produced by the neural policy generator alone. It is produced by a restricted policy lower evaluation plus an externally constructed non-neural global upper comparison.

Because the same upper comparator is used for the classical policies, the policy-generation comparison remains fair. But the end-to-end NBO method is not self-certifying at this accuracy. A claimed standalone neural solver would need either to construct its own sharp unrestricted witness or to count the external dual solve as an essential component of the method.

### R21-F7 — Major: policy-value-separated acceptance is validated a posteriori, not yet established as a robust solver mechanism

The new gate is conceptually correct. On the executed R19 and R20 trajectories it works.

But the evidence is still narrow:

- five R19 seeds in a time-control class;
- five R20 seeds with four separately trained experts;
- a very small initial-state region;
- a shared pre-existing unrestricted upper comparison;
- no new full-state NBO execution using the policy-value gate.

There is no theorem that Adam with this parameterization reliably produces accepted improvements, and no broad empirical study showing how acceptance behaves as dimension, state coverage, or policy expressiveness grows.

The paper mostly avoids claiming such a theorem. It should therefore present the gate as a validated acceptance mechanism, not as evidence that the general NBO optimization problem is solved.

### R21-F8 — Major: the continuation-witness blocker remains open at the full-domain level

R19's continuation analysis is valuable, but it remains diagnostic.

The one-sided fixed-policy continuation target shows why the old critics were wrong near the inaccessible wealth face. The scalar-lift experiment then shows that satisfying that one trace condition can make the global residual substantially worse.

What is still missing is an algorithm that simultaneously learns:

1. the correct continuation geometry; and
2. a small complete-domain positive Bellman residual.

Until that exists, the full-state witness problem identified in R18 remains unsolved.

### R21-F9 — Major: the high-dimensional example is supportive but cannot carry the main claim

The revised high-dimensional section is much better framed. Neural initialization saves correction counts at d=8 and d=32 on the declared finite query sets. That is a real learned contribution.

But this remains a strongly convex finite-horizon plan-optimization problem with a powerful classical correction and acceleration baseline. The theorem giving the cube-uniform guarantee remains initialization agnostic, and the strictest 128-dimensional target favors acceleration.

This is useful secondary evidence for learned warm starts. It is not a substitute for an accurate full-state NBO on the flagship stochastic dynamic model.

### R21-F10 — Major: the paper's strongest current contribution is validated policy certification, not neural Bellman computation

The repository now contains several genuinely strong ingredients:

- fixed-policy directed payoff enclosures;
- a clean separation between policy value and unrestricted optimal comparison;
- continuum transfer for the R19 policy class;
- policy-induced continuation diagnostics;
- independent arithmetic replay;
- matched policy-class comparators;
- explicit economic compensation calculations.

These are coherent as a validated computational-economics contribution.

What is not coherent is using them to imply that the neural Bellman architecture has been shown numerically superior or even necessary. The current evidence repeatedly shows that the sharpest accurate policies come from restricted control families and that direct optimization is highly competitive or better.

The paper should choose its identity.

---

## 6. Technical and reproducibility comments

### R21-T1 — Update the revision index

REVISION_INDEX.md still names R16 as the current review object. A referee should not have to reconstruct the current paper from branch history.

### R21-T2 — Materialize the R20/R21 paper before another review

Provide ECTA_R20 or ECTA_R21, supplement, response, proofs, review entry file, publication manifest, result manifest, and PDF hashes. Pin the exact R19 publication input, R20 protocol commit, R20 result commit, and final manuscript commit.

### R21-T3 — Put the R20 direct stochastic comparator in the main text

This is the most informative new numerical comparison. The main paper should show that direct L-BFGS-B is better than all five neural seeds at all four vertices, with matched generation and verification accounting.

Hiding this in raw result JSON would materially distort the numerical interpretation.

### R21-T4 — State exactly what the R20 neural network observes

The implementation feeds the network the normalized time-slab coordinate. The stochastic factor enters through the fixed logistic decoder, not as a learned network input.

This must be explicit in the manuscript. Calling the object a stochastic neural policy without this detail can lead readers to infer learned state feedback that is not present.

### R21-T5 — Explain the role of the four expert networks

R20 trains one network per corner and then invokes a mixture argument for interior initial states. Report the exact deployed interior policy, not only the corner experts. State whether the mixture is deterministic control interpolation, randomized policy mixing, or another construction, and prove admissibility, self-financing, and payoff concavity for that exact object.

### R21-T6 — The R20 randomization code reuses the same initialization within a seed across all four vertices

run_study.py calls torch.manual_seed(seed) inside the vertex loop before constructing each network. Thus the four experts for a given seed begin from the same pseudorandom weights, although they are trained on different objectives.

This is not necessarily invalid, but it should be disclosed because the protocol says each expert starts from fresh random neural weights. If independent expert initializations were intended, the implementation does not do that.

### R21-T7 — Distinguish arithmetic independence from mathematical independence

The MPFR audit is useful. It is not an independent proof of the quadrature remainder, stopping correction, dual validity, or economic model derivation. The R20 records already say this; keep that wording.

### R21-T8 — Report the full cost ledger

For every method report separately:

- policy generation;
- checkpoint verification;
- final verification;
- shared dual construction and validation;
- neural offline training;
- MPFR audit;
- memory;
- threads and software versions.

The current generation comparison is already unfavorable to the neural representation. Complete accounting should not blur that conclusion by pooling common verification cost with method-specific generation cost.

### R21-T9 — The R19 K bound misses the paper's stated 0.01 threshold

The abstract and conclusion should keep this numerical distinction explicit: reference-state success is below 0.01; the reported K bound is 0.011816625.

### R21-T10 — Preserve the adverse complete-domain result in the main narrative

The full-state feedback result around 7.278 is not historical clutter. It is the direct evidence about the method named in the title and must remain visible whenever localized policy successes are summarized.

### R21-T11 — Do not infer a general neural advantage from the learned warm-start table

At d=8 and d=32 the correction-count advantage is real. At d=128 it narrows or disappears, and acceleration wins at the strictest target. Keep the claim regime-specific and include training amortization.

### R21-T12 — The direct stochastic comparator is a representation test, not merely another baseline

Because it optimizes the same hand-designed stochastic logistic policy family without hidden layers, it isolates what the network contributes. The paper should interpret it accordingly.

---

## 7. Status of the previous R18 gates

### Gate R19-A — Policy-sensitive progress on the flagship economy

**Closed for the new restricted policy classes, still open for the full-state NBO.**

R19 and R20 establish actual fixed-policy payoff improvement. They do not execute the full-state feedback architecture under the new gate.

### Gate R19-B — A witness that removes the 6.27-unit floor

**Open.**

R19 supplies a constructive continuation target and a negative scalar-lift experiment. It does not construct a globally sharp full-state witness.

### Gate R19-C — Full-domain neural accuracy in a useful range

**Open.**

The full-state feedback certificate remains about 7.278. Local restricted-policy certificates are sharp but are not full-domain NBO certificates.

### Gate R19-D — Matched-accuracy classical frontier

**Substantially improved, with an adverse result for the neural parameterization.**

R19 SLSQP and R20 direct stochastic L-BFGS-B are strong matched comparators. They are as accurate or more accurate and cheaper in the reported regimes.

### Gate R19-E — Neural contribution in the high-dimensional example

**Partially closed.**

There is a finite-query correction-count benefit at d=8 and d=32. There is no broad end-to-end dominance, and the strongest cube theorem remains initialization agnostic.

### Gate R19-F — Coherent paper identity

**Open.**

The validated successes now separate cleanly into:

- full-state NBO: still inaccurate;
- local neural-generated policies: accurate;
- same-family direct optimization: at least as good and cheaper;
- high-dimensional neural warm start: useful in limited regimes;
- global upper comparison: inherited non-neural dual.

These pieces do not yet support a single strong claim that Neural Bellman Operators are the successful numerical method.

---

## 8. What would justify another Econometrica-level round

I would not recommend another round based mainly on:

- more local seeds;
- another smaller K rectangle;
- more MPFR precision;
- finer verification of the same restricted actors;
- a new neural wrapper around the same 16-slab control family;
- more post-hoc tables without a new full-state solver.

A scientifically meaningful next revision should clear the following gates.

### Gate R22-A — Materialized submission integrity

One immutable manuscript/supplement/response package must incorporate all numerical claims actually being reviewed.

### Gate R22-B — Full-state policy-sensitive NBO execution

Run the state-feedback Neural Bellman Operator itself under a policy-sensitive acceptance/evaluation mechanism, with multiple seeds and declared work levels.

### Gate R22-C — Full-domain certified accuracy

Move the full-state original-economy certificate into a genuinely useful regime. A result still hundreds of times the declared tolerance is not enough.

### Gate R22-D — Demonstrated value of the neural representation

Against the direct same-family parameterization, show a certified regime in which the neural representation improves the accuracy-work frontier, scaling, amortization, or attainable policy class. If no such regime exists, reframe the neural network as one optional generator rather than the methodological centerpiece.

### Gate R22-E — A globally sharp continuation witness

Construct, do not merely diagnose, a witness whose continuation trace and complete-domain Bellman residual are simultaneously compatible with the target.

### Gate R22-F — Matched full-domain classical frontier

At least one conventional full-state solver should be carried to a sharp continuous-time certified accuracy with transparent generation, evaluation, verification, memory, and wall-time accounting.

### Gate R22-G — Coherent methodological identity

Either:

1. make the full-state Neural Bellman Operator itself the accurate and competitive method; or
2. reorganize the paper around validated policy certification and policy-value-separated computational economics, treating neural parameterizations as one candidate class whose successes and failures are documented.

The second route could be a strong paper. It would, however, be a different methodological claim from the current title-level implication.

---

## 9. Recommendation

**Reject.**

R19/R20 represent real scientific progress. The revision finally demonstrates actual policy-value improvement rather than witness improvement, reaches sharp local regret bounds, adds strong arithmetic checks, improves continuation diagnostics, and gives much better matched comparisons.

Those comparisons are also the reason for the negative recommendation.

The accurate policies are not the full-state Neural Bellman Operator. The full-state NBO remains at roughly 7.28 against a 0.01 target. The new sharp R19 policy is a restricted time-control schedule. The new R20 stochastic policy obtains its adaptivity primarily through a hard-coded logistic decoder and analytic self-financing hedge. And when the same R20 stochastic family is optimized directly without hidden neural layers, the non-neural method is better at every vertex and much cheaper to generate.

The paper has therefore advanced from

> a certificate-aware system that could not show actor improvement

to

> a validated policy-improvement and certification framework that can construct accurate restricted policies, but has not shown that the neural Bellman representation is the source of that success.

That is an important advance. It is not yet an Econometrica-level demonstration of a successful new neural numerical method for the full stochastic dynamic problem.
