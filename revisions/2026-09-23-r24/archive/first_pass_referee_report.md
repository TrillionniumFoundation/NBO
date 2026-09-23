# Referee Report — Neural Bellman Operators (R23)

**Venue standard:** Econometrica-level numerical / computational methodology  
**Recommendation:** **Reject in the present form.**  
**Review date:** 2026-09-23  
**Reviewed publication branch:** revision/econometrica-r23-referee-copy-2026-09-23  
**Reviewed sealed commit:** c09835c92042cb881d0bbdd3cab99b98d0a9d225  
**Development branch:** revision/econometrica-r23-referee-resolution-2026-09-23  
**Review branch:** review/econometrica-r23-numerical-methods-2026-09-23

---

## 1. Executive assessment

R23 is a serious and technically much stronger response to the complete R21 report. It fixes several defects that were previously decisive. In particular, it no longer presents the old neural–Adam versus direct–L-BFGS-B comparison as a representation ablation; it introduces matched-initial-policy crossed optimizer/parameterization experiments; it removes the common financing-intercept redundancy with a 47-coordinate quotient control; it proves finite-node class equivalence; it replaces synchronized-corner initialization by a general pair-moment Jensen argument; and it supplies directed price-bracket and interpolation-rank instantiations.

I did not find an obvious algebraic contradiction in the new budget-quotient theorem, the finite-node interpolation construction, the re-budgeting monotonicity argument, or the nonsynchronized Jensen proof chain.

The publication-level problem is now more substantive than formal.

The object that actually meets a small numerical error bound remains a **local, time-only, model-assisted four-expert construction at t=0 on the small rectangle**
K = [1.98,2.02] x [1.24,1.26].
The current-state Neural Bellman Operator named by the paper remains nowhere near the declared full-domain objective: the certified all-start-time bound is 7.241462444 against a target of 0.01, a factor of about 724. The revision explicitly admits that it does not establish a separate payoff improvement for that full-state actor.

Moreover, the best numerical frontier in the new held-out experiment is still classical/direct. Direct L-BFGS-B achieves regional regret below about 0.002839 in all three ensembles, using roughly 362–452 objective/gradient evaluations per four-expert system and about 1.03–1.28 seconds of generation time. Neural–Adam uses 1,600 evaluations and about 5.64–5.99 seconds while reaching approximately 0.003006–0.003021. The new positive neural result is instead a conditional statement against **direct Adam with one fixed learning rate of 0.005**. That is a legitimate finite experiment, but it does not establish an accuracy–work advantage for the neural method.

Accordingly, R23 has converted several earlier objections from “the experiment does not identify what it claims” into “the experiment identifies a narrow optimizer-conditional phenomenon.” That is progress. It is still not the methodological result required for an Econometrica-level numerical-method paper centered on Neural Bellman Operators.

---

## 2. What R23 genuinely fixes

### 2.1 The former representation ablation is repaired conceptually

The R21 report objected that neural–Adam versus direct–L-BFGS-B simultaneously changed representation, optimizer, initialization, and parameter dimension.

R23 now crosses:

- neural vs direct vs direct-quotient coordinates;
- Adam vs L-BFGS-B;
- matched delivered initial policies for the primary neural/direct arms;
- separately certified quotient incumbents;
- common gradient-call caps and explicit function/gradient accounting.

This is the right experimental architecture for asking how a parameterization interacts with a fixed optimizer.

### 2.2 The redundant financing coordinate is understood correctly

Theorem r23budget identifies the common-intercept null direction, gives the implicit derivative

db^f/db = I - 1 omega^T,

and shows that fixing one raw intercept produces a complete 3m-1 coordinate chart for the financed family. The proof correctly treats the derivative as an oblique projection rather than an arbitrary normalization.

The continuous-price bracket also explicitly pays for the Gaussian tail rather than silently replacing an unbounded measure by finite support.

### 2.3 The finite-node class comparison is materially stronger

Proposition r23class proves that a 1–m–m–3 tanh network can interpolate an arbitrary m x 3 raw-output table at m distinct scalar time nodes. For the actual m=16 construction, the MPFR determinant enclosure is strictly separated from zero.

This removes an important ambiguity: the neural and direct finite-node arms are not being compared because one can represent arrays the other cannot.

### 2.4 Independent corner initialization is now handled

The R21 continuum-improvement theorem depended materially on synchronized corner initialization.

R22/R23 replace that with pair-moment bounds and independently initialized corner seeds. The proof uses weighted-variance identities, a joint time-probability Cauchy–Schwarz bound, explicit tail corrections, and a separate old-mixture Jensen allowance. This is a genuine improvement.

### 2.5 Adverse results remain visible

R23 keeps the facts that:

- direct L-BFGS-B is stronger overall;
- direct Adam remains above 0.01 under the chosen fixed configuration;
- one neural L-BFGS-B ensemble has regional regret 0.01050307;
- the full-state objective remains open;
- the unrestricted upper library is non-neural and costly;
- the successful regional decoder is model-based.

This transparency substantially improves the paper.

---

## 3. Decisive R23 numerical facts

The held-out regional table reports:

| Ensemble | Neural–Adam regret | Direct–L-BFGS-B regret | Neural–Adam evals | Direct–L-BFGS-B evals | Neural gen. sec | Direct gen. sec |
|---|---:|---:|---:|---:|---:|---:|
| 23000 | 0.00302112 | 0.00283871 | 1600 | 405 | 5.994 | 1.176 |
| 23100 | 0.00300570 | 0.00283872 | 1600 | 452 | 5.644 | 1.276 |
| 23200 | 0.00301599 | 0.00283871 | 1600 | 362 | 5.676 | 1.029 |

Thus the direct L-BFGS-B systems are more accurate while using about one quarter of the objective/gradient calls and about one fifth of the policy-generation wall time.

The new positive R23 comparison is instead:

- neural–Adam regional regret below 0.003022;
- neural–Adam initial-to-final uniform payoff gain above 0.026360;
- neural–Adam uniform actual-payoff advantage above 0.003044 over both direct–Adam coordinate systems.

Those are valid certified statements on the stated local region under the stated optimizer settings.

They do **not** overturn the end-to-end frontier result above.

The original current-state object remains:

- old bound: 7.2783190635;
- refined bound: 7.241462444;
- target: 0.01;
- certified payoff improvement for the refined full-state actor: not established.

That gap remains the central issue.

---

## 4. Blocking scientific findings

### R23F-F1 — The full-state Neural Bellman Operator remains numerically unresolved

The paper retains the full state-time problem and the 0.01 accuracy objective. That is appropriate.

But the achieved complete-domain certificate is 7.241462444, roughly 724 times the target. The revision does not prove that the jointly changed current-state actor has a higher payoff than the inherited actor.

Therefore the part of the paper that actually resembles a current-state Neural Bellman Operator remains numerically unsuccessful by the paper's own criterion.

This is not a cosmetic shortfall. It is the flagship numerical target.

A top numerical-method paper cannot substitute a small local certificate for failure of the declared full-domain object while retaining the stronger title and general framing.

### R23F-F2 — The strongest positive result is still not a current-state neural policy

The successful regional policy does not learn a map from current (t,u,x) to controls.

The network sees time only. State dependence is supplied by:

- a prescribed logistic consumption decoder;
- analytic conditional pricing;
- an analytic hedge;
- four separately trained corner experts;
- fixed initial-state mixture weights.

The continuum theorem validates an economically legitimate interpolated control construction. It does not show that a neural network learned state generalization.

R23 now says this more clearly, but the methodological mismatch remains. The high-accuracy object is still a restricted model-assisted policy library, not the full-state NBO suggested by the title.

### R23F-F3 — The new Adam result identifies one fixed hyperparameter configuration, not a numerical frontier

The direct and neural Adam arms both use learning rate 0.005.

Adam is not invariant to reparameterization. The whole point of the experiment is that the neural overparameterization induces a different optimization geometry. In that setting, using the same nominal scalar learning rate across coordinate systems is not a neutral calibration.

The experiment therefore proves:

> with this fixed learning rate, this initialization mapping, this architecture, this objective, and this 400-call cap, the neural coordinates produce a better Adam endpoint than the two direct coordinate charts.

That is a legitimate conditional finding.

It does **not** show that the direct policy class has a worse first-order optimization frontier. A different direct learning rate, schedule, diagonal rescaling, normalization, or tuned Adam configuration could change the result without changing the represented policies at all.

The fact that the quotient control leaves the result largely unchanged only rules out one common-intercept redundancy. It does not establish parameterization robustness.

For publication at this level, the paper needs an optimizer-tuning protocol or an accuracy–work envelope over a prospectively defined hyperparameter family, not one shared scalar learning rate.

### R23F-F4 — The evidence does not show a neural accuracy–work advantage

The end-to-end result remains adverse to the neural method.

Direct L-BFGS-B:

- is more accurate than neural–Adam in every held-out ensemble;
- uses far fewer objective/gradient evaluations;
- is roughly five times faster in policy generation;
- is also markedly more stable across ensembles.

The local direct solutions are nearly identical across independent ensembles. By contrast, neural L-BFGS-B has one held-out block that terminates by projected-gradient tolerance after 100 evaluations with regret 0.01050307.

Thus the current evidence supports the practical conclusion that the direct coordinates plus a strong deterministic optimizer are the better solver for this tested policy class.

A numerical-method paper centered on the neural construction still lacks a regime where the neural mechanism changes the best achievable accuracy–work frontier.

### R23F-F5 — Finite-node class equality does not explain or validate the claimed optimization mechanism

Proposition r23class proves surjectivity onto the same 16 x 3 raw-output arrays.

That is useful, but it is only a class-equivalence result.

If the scientific novelty is now the optimization geometry induced by overparameterization, then the paper should analyze that geometry quantitatively. At present there is no theorem or diagnostic for:

- the Jacobian from network parameters to slab outputs;
- its singular spectrum along training;
- the induced function-space preconditioner;
- sensitivity to hidden-layer rescaling;
- conditioning of the direct and neural Adam updates;
- whether the reported advantage survives equivalent reparameterizations of the same neural map.

Without such analysis, “parameterization effect” is descriptive: two coordinate systems gave different Adam outcomes. It is not yet a numerical-method explanation.

### R23F-F6 — The held-out status is narrower than the presentation suggests

The R23 protocol is admirably explicit that it was fixed **after inspecting all available R22 outcomes**.

The new base seeds 23000, 23100, and 23200 are held out, and all configurations are retained. That is good practice.

But the design choices—including architecture, learning rate, optimizer pair, call cap, coordinate comparison, and the very neural–Adam/direct–Adam contrast—were chosen after the qualitative R22 pattern was already known.

R23 is therefore a held-out-seed replication of an already observed configuration, not an independent confirmation of a newly specified method across new economic problems or numerical regimes.

The paper should describe it that way and should add a genuinely external test dimension if the claim is methodological robustness.

### R23F-F7 — The local continuum theorem still scales through an expert cover with exponential worst-case growth

The new cover-complexity proposition is honest:

- a regular d-dimensional grid has (n+1)^d vertices;
- the complete vertex library costs O((n+1)^d m);
- active simplex evaluation uses d+1 experts but does not remove the library cost.

This is a useful theorem because it states the limitation rather than hiding it.

It also confirms that the successful local four-expert construction does not solve the central high-dimensional state-coverage problem. No executed multicell original-economy study demonstrates that the proposed expert-cover mechanism remains competitive as dimension or domain size grows.

The duplicated-expert latency experiments do not answer that question.

### R23F-F8 — The successful regional method remains heavily model-assisted

The accurate regional construction uses exact conditional pricing and an analytic hedge for the selected factor-measurable consumption stream.

The paper correctly notes that the preference shock has an unspanned component and that the entire model is not thereby complete.

Nevertheless, the numerical success still relies on a particularly favorable analytic feasibility layer. The general residual-correction cone is mathematically broader, but its executed full-state instance remains extremely loose.

For a general numerical-method claim, the paper still needs an executed case in which feasibility and continuation cannot be supplied by the current exact-price/replication structure.

### R23F-F9 — The regret certificate remains a hybrid system with a dominant non-neural certification component

Regional regret uses an inherited non-neural unrestricted dual library whose reported construction cost is 415.789 seconds.

The new held-out experiment itself takes about 290.946 seconds in total, and policy generation is only 68.729 seconds.

This is scientifically acceptable if the object is defined as:

> policy generator + external verifier + reusable dual upper library.

But that decomposition must be the method definition, with explicit amortization assumptions.

If a new economic instance requires rebuilding the unrestricted upper library, the cost structure is materially different from a repeated solve that reuses it for free. A numerical paper should show both frontiers rather than leave the reusable-library interpretation as prose.

### R23F-F10 — Three held-out ensembles are too narrow for the remaining robustness claim

The results are certified rather than estimated, so this is not primarily a request for classical sampling standard errors.

The issue is algorithmic robustness.

There are only three new initialization ensembles under one architecture, one Adam learning rate, one horizon/discretization, one small rectangle, and one economic model. The neural L-BFGS-B failure in ensemble 23200 already shows material basin sensitivity.

For a paper whose remaining positive claim is optimizer–parameterization interaction, a much broader stress grid over independent initializations, learning-rate scales, widths/depths, and work budgets is necessary.

### R23F-F11 — The active acceptance gate is not what produces the main R23 result

All 72 R23 final proposals are accepted.

The rejection/rollback evidence comes from an inherited targeted stress study, with a deliberately high Adam learning rate and an external supervisory learning-rate change.

That study is useful implementation evidence. It does not establish that the acceptance operator provides convergence, nor that it materially changes the accuracy frontier in the main held-out design.

The paper should avoid letting “Bellman operator” language suggest a stronger fixed-point or monotone-improvement algorithmic theorem than has actually been proved.

### R23F-F12 — The current contribution is closer to certified policy optimization than to a Bellman-operator numerical method

The paper now separates:

- candidate policy generation;
- policy-specific payoff acceptance;
- analytic financing/hedging;
- continuum interpolation;
- an unrestricted dual upper comparison;
- a separate current-state actor/witness experiment.

That decomposition is scientifically useful.

It also reveals the identity problem more sharply. The local method does not learn a Bellman value operator, while the actual current-state actor/witness system does not meet the target.

The authors should either produce a successful current-state Bellman-operator result or substantially reframe the paper around certified policy optimization with neural overparameterization and model-based feasibility.

Keeping the strongest Bellman-operator framing while the Bellman-like object is the weakest numerical component is not convincing.

---

## 5. Technical findings

### R23T-T1 — The direct-Adam comparison needs parameterization-aware tuning

At minimum, pre-register a tuning set distinct from the final evaluation seeds and choose:

- learning rate or schedule separately for each representation;
- a common tuning budget;
- a fixed selection rule based only on the tuning set;
- final held-out accuracy–work curves.

A stronger design would add simple diagonal rescalings of the direct variables and neural hidden/output rescalings that preserve the represented policy class. If the sign of the “neural advantage” changes under harmless coordinate scaling, the claimed mechanism is not robust.

### R23T-T2 — The machine-readable full-state summaries contain a naming inconsistency

In revisions/2026-09-23-r22/results/full_state/summary.json, the field

candidate_all_initial_times_bound

is 7.386001245971047.

In revisions/2026-09-23-r22/results/full_state/time_envelope.json, the later discounted suffix calculation labels 7.241462443133396 as

all_start_times_regret_upper

and 7.386001245971047 as

earlier_undiscounted_all_times_bound.

The manuscript uses 7.241462444 as the current all-start-time bound.

The numerical logic may be valid, but the machine-readable publication object should not leave two incompatible field names for “all initial times.” The stale summary field should be deprecated or explicitly versioned in the current manifest and dependency map.

### R23T-T3 — Equal gradient-call caps are not equal computational work

A neural gradient evaluates 355 trainable coordinates through a two-hidden-layer network; the direct gradient has 48 or 47 coordinates.

The paper reports wall time, which is good. The positive neural statement should therefore be presented as an equal-gradient-call comparison, not an equal-work comparison.

For method claims, show regret/payoff versus:

- objective/gradient calls;
- wall time;
- and, if possible, a hardware-independent operation proxy.

### R23T-T4 — The interpolation theorem should be separated from conditioning

The exact rank certificate proves existence of an interpolating final layer for one explicit hidden construction.

It does not prove that this representation is numerically well conditioned, nor that training near the actual random networks inherits useful conditioning.

The paper already partly acknowledges this. The main text should make the distinction sharper because “same policy class” plus “different Adam result” naturally invites a conditioning interpretation that has not been established.

### R23T-T5 — The neural L-BFGS-B failure deserves a trajectory-level diagnosis

For seed 23203, vertex 3, neural L-BFGS-B terminates with

CONVERGENCE: NORM OF PROJECTED GRADIENT <= PGTOL

after 100 function/gradient evaluations and 87 accepted iterations, yet the certified regret is 0.01050307.

This is an informative failure, not merely an adverse table entry.

The paper should report:

- objective trajectory;
- certified payoff trajectory at selected checkpoints;
- gradient norm;
- distance in delivered slab-policy space to the direct solution;
- Jacobian conditioning;
- whether restart or simple coordinate rescaling escapes the basin.

That diagnosis would materially help establish what the neural parameterization is doing.

### R23T-T6 — The continuum theorem is strong enough that its hypotheses should be surfaced earlier

The current theorem depends on:

- finite policy payoff enclosures;
- Hessian bounds on the stated domain;
- pair-moment bounds;
- tail corrections;
- common-shock coupling;
- convexity of the unrestricted upper comparison;
- and model-specific stopping/payoff range controls.

These assumptions are spread across retained files. A compact theorem-assumption table in the main paper would help readers distinguish a general mixture argument from model-specific constants.

### R23T-T7 — The cost of certification should be incorporated into the principal frontier figure/table

The paper separates generation and checking, but the headline methodological comparison still foregrounds generation outcomes.

For a certified method, the verifier is part of the computation.

Report at least three frontiers:

1. generator only;
2. generator + final fixed-policy certification;
3. generator + certification + unamortized unrestricted upper construction.

This would make the economics of reuse explicit.

### R23T-T8 — The three levels of “proof” should remain sharply distinguished

R23 does this better than earlier revisions, but the distinction is important enough to preserve rigidly:

- analytic theorem;
- directed arithmetic instantiation for a frozen object;
- ordinary floating-point regression/diagnostic.

In particular, small proposal root residuals, finite-difference gradient agreement, and MPFR re-execution are not independent derivations of the economic model.

---

## 6. Publication-level requirements for a new round

A new revision should not respond by adding another layer of local bookkeeping around the same 16-slab rectangle. The remaining requirements are methodological.

### N1 — Close or substantially approach the full-state target with a current-state policy

The current-state actor/witness object should improve by orders of magnitude, not by 7.278 to 7.241.

A convincing revision should report a policy-sensitive full-state certificate and a separately certified payoff improvement for the current-state actor.

### N2 — Produce an accuracy–work frontier where the neural method is nontrivially competitive

The paper needs at least one regime where the neural construction is on the efficient frontier against a strong direct/classical method.

That comparison should use tuned baselines and should include wall time and certification cost.

### N3 — Replace the single-learning-rate Adam comparison by a prospective tuning protocol

Use a disjoint tuning set, predeclare the hyperparameter family and selection rule, and evaluate only once on held-out seeds/problems.

The direct and neural representations should each receive a reasonable optimizer calibration.

### N4 — Test robustness to equivalent rescalings and simple coordinate preconditioners

Because the claimed effect is geometric, it should survive or be explained by benign changes of coordinates that preserve the policy class.

At present the paper shows a coordinate-dependent optimizer phenomenon but does not characterize its invariants.

### N5 — Demonstrate scaling beyond one four-corner rectangle

A useful next test would be a multicell or higher-dimensional original-economy domain where the number of experts, verifier cost, and accuracy can be measured jointly.

The current conditional complexity proposition honestly predicts exponential worst-case growth; the numerical paper must show where the proposed method actually beats that burden.

### N6 — Add an executed nonreplicable / non-analytic-feasibility case

The residual-correction cone is theoretically broader than the exact-price decoder. Demonstrate it in a case where the portfolio/feasibility layer cannot be supplied by the present analytic replication structure.

### N7 — Resolve the methodological identity

Either:

- establish a successful current-state Neural Bellman Operator with a competitive numerical frontier,

or

- reframe the contribution as a certified policy-optimization framework with neural overparameterization, exact financing, continuum expert mixtures, and external dual verification.

The present manuscript contains valuable ingredients, but those two identities should not remain conflated.

---

## 7. Minor and editorial points

1. The phrase “held-out design” should specify that the seeds/configurations are held out after R22, while the algorithmic design and hyperparameters were chosen with knowledge of R22 outcomes.
2. “Same work budget” should be replaced by “same objective/gradient-call cap” unless wall-clock or operation-normalized work is intended.
3. The direct-quotient control is useful, but it rules out only the common-intercept redundancy. It should not be described as exhausting direct-coordinate conditioning issues.
4. The abstract is commendably cautious about direct L-BFGS-B being stronger overall. Keep that sentence.
5. The local rectangle and t=0 scope should remain in every headline numerical statement.
6. The unrestricted dual library should be named as an essential non-neural component whenever regret, rather than pairwise policy payoff, is discussed.
7. The full-state 7.241 result should never be presented as evidence of policy improvement unless a policy-specific lower bound is separately supplied.
8. The R23 rank certificate is an exact-matrix nonsingularity instantiation; it is not evidence that the learned neural features are well conditioned.
9. Preserve the failed neural L-BFGS-B case and the rejected R22 cases. They are scientifically informative.

---

## 8. Recommendation

**Reject in the present form.**

This recommendation is no longer driven by missing review objects, a confounded primary comparison, or an obvious gap in the new local proof chain. R23 fixes much of that.

The remaining barrier is the numerical-method contribution itself:

- the declared full-state NBO target remains missed by about two to three orders of magnitude;
- the accurate local object is a restricted time-only, analytically financed, four-expert construction;
- the best tested accuracy–work frontier remains direct L-BFGS-B;
- the new neural advantage is conditional on one fixed Adam calibration and does not establish a tuned first-order or end-to-end frontier advantage;
- scaling and nonreplicable execution remain largely theoretical rather than demonstrated.

A further revision can be scientifically meaningful, but it needs a new numerical result, not another repackaging of the existing regional certificate.

---

## 9. Reviewed source map

Primary referee object:

- ECTA_R23.tex / ECTA_R23.pdf
- SUPP_R23.tex / SUPP_R23.pdf
- RESPONSE_R23.tex / RESPONSE_R23.pdf
- R23_REVIEW.md
- revisions/2026-09-23-r23/PUBLICATION_MANIFEST.json

Key current files inspected:

- revisions/2026-09-23-r23/paper/introduction.tex
- revisions/2026-09-23-r23/paper/method.tex
- revisions/2026-09-23-r23/paper/results.tex
- revisions/2026-09-23-r23/paper/conclusion.tex
- revisions/2026-09-23-r23/paper/proofs.tex
- revisions/2026-09-23-r23/paper/supplement.tex
- revisions/2026-09-23-r23/paper/crossed_table.tex
- revisions/2026-09-23-r23/paper/conditional_table.tex
- revisions/2026-09-23-r23/paper/full_ledger.tex
- revisions/2026-09-23-r23/paper/dependency_table.tex
- revisions/2026-09-23-r23/PROTOCOL.md
- revisions/2026-09-23-r23/REPRODUCE.md
- revisions/2026-09-23-r23/replication/run_study.py
- revisions/2026-09-23-r23/results/continuum.json
- revisions/2026-09-23-r23/results/continuous_budget_brackets.json
- revisions/2026-09-23-r23/results/interpolation_certificate.json

Inherited proof/current-state files inspected:

- revisions/2026-09-23-r22/paper/method.tex
- revisions/2026-09-23-r22/paper/proofs.tex
- revisions/2026-09-23-r22/paper/results.tex
- revisions/2026-09-23-r22/results/full_state/summary.json
- revisions/2026-09-23-r22/results/full_state/time_envelope.json
- revisions/2026-09-23-r22/paper/retained_r21_method.tex
- reviews/2026-09-23-econometrica-r21-final/referee_report.md

The reviewed R23 development and referee-copy branches are byte-identical at sealed commit c09835c92042cb881d0bbdd3cab99b98d0a9d225.
