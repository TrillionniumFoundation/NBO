# Second-Pass Referee Report — Neural Bellman Operators (R23)

**Venue standard:** Econometrica-level numerical / computational methodology  
**Recommendation:** **Reject in the present form.**  
**Review date:** 2026-09-23  
**Reviewed referee-copy branch:** `revision/econometrica-r23-referee-copy-2026-09-23`  
**Equivalent development branch:** `revision/econometrica-r23-referee-resolution-2026-09-23`  
**Reviewed sealed commit:** `c09835c92042cb881d0bbdd3cab99b98d0a9d225`  
**Second-pass review branch:** `review/econometrica-r23-second-pass-numerical-methods-2026-09-23-c09835c`

---

## 1. Executive assessment

I have re-read R23 as an independent second-pass numerical-method referee, including the current manuscript, the R23 protocol, the complete 72-configuration ledger, the proposal code, the continuum certification code, the inherited R22/R21 policy semantics, and the full-state verification record.

R23 is unusually transparent and substantially more careful than the earlier versions. It now states several limitations that a referee previously had to infer. That transparency is valuable. It does not, however, supply the missing numerical-method result.

The central difficulty is now sharper:

1. the **successful high-accuracy object is not a current-state Bellman policy on the original Markov state**. It is a local four-expert, model-assisted, path-dependent implementation with stored initial-state context and observable subaccounts;
2. the **full-state current-state actor/witness remains approximately 724 times above the declared 0.01 target**, and there is still no separately certified payoff improvement for that actor;
3. the positive neural result is a **fixed-learning-rate Adam outcome in a massively overparameterized coordinate system**, while the same finite-node policy class is solved more accurately and much more cheaply by direct L-BFGS-B;
4. the finite-node class-equivalence result makes the interpretation of the neural result more, not less, demanding: once expressiveness is equalized, the 355-parameter neural map acts primarily as a nonlinear, state-dependent **implicit preconditioner** for a 48-output problem. R23 does not identify, analyze, or benchmark that preconditioner against explicit 47/48-dimensional alternatives;
5. the primary optimizer is trained on a finite proposal quadrature while publication accuracy is certified by a different continuous-model checker. The endpoint certificates are valid, but there is no controlled gradient/surrogate-error analysis showing that the observed optimizer ordering is robust to the proposal discretization;
6. the main 72-run experiment never exercises the acceptance operator: **72/72 final proposals are accepted**. Thus the “operator” component is operationally inert in the principal result.

The manuscript therefore contains several strong ingredients—validated payoff comparisons, careful financing, a useful nonsynchronized Jensen argument, and excellent audit trails—but they do not yet establish a competitive Neural Bellman Operator as a numerical method.

My recommendation remains **reject in the present form**.

---

## 2. Scope of this second-pass audit

This report is not a restatement of the existing R23 referee report. I specifically re-audited the following issues at source-code and theorem level:

- whether the local successful policy is a feedback policy on the original Markov state;
- what the finite-node class-equality theorem does and does not identify;
- the geometry induced by the 355-to-48 neural output map;
- whether the 47-coordinate quotient control is a substantive conditioning control;
- whether “optimizer matching” with a common Adam step size is a fair numerical comparison;
- the relation between the proposal quadrature objective and the independently certified continuous payoff;
- whether the acceptance gate changes the primary R23 computation;
- whether the reported regret frontier is solver-limited or verifier/dual-limited;
- whether the R23 held-out design is genuinely external to the qualitative pattern already observed in R22;
- whether the cost accounting establishes an end-to-end numerical advantage.

I did not find a simple algebraic contradiction that invalidates the R23 budget quotient theorem, the explicit sixteen-node interpolation construction, or the nonsynchronized Jensen proof. The blocking issues are methodological and numerical.

---

## 3. Decisive numerical facts

The manuscript itself reports the following held-out regional systems:

| Ensemble | Neural–Adam regret | Direct–L-BFGS-B regret | Neural–Adam evals | Direct–L-BFGS-B evals | Neural gen. sec. | Direct gen. sec. |
|---|---:|---:|---:|---:|---:|---:|
| 23000 | 0.00302112 | 0.00283871 | 1600 | 405 | 5.994 | 1.176 |
| 23100 | 0.00300570 | 0.00283872 | 1600 | 452 | 5.644 | 1.276 |
| 23200 | 0.00301599 | 0.00283871 | 1600 | 362 | 5.676 | 1.029 |

Thus the direct deterministic optimizer is simultaneously:

- more accurate in all three ensembles;
- about 3.5–4.4 times cheaper in objective/gradient evaluations;
- about 4.4–5.5 times cheaper in measured generation time.

The adverse neural L-BFGS-B case remains informative: one regional system has regret upper bound (0.01050307), whereas direct L-BFGS-B remains near (0.00283871).

The positive neural statement is instead conditional on Adam with the single fixed learning rate (0.005):

- neural–Adam regional regret is about (0.00301);
- direct–Adam and quotient–Adam remain around (0.012);
- the certified uniform neural–Adam actual-payoff advantage over those two fixed Adam configurations is above (0.003044).

For the original full-state current-state object:

- target: (0.01);
- previous complete-domain bound: (7.2783190635);
- R23 inherited/refined bound: about (7.241462444).

The latter is roughly (724) times the target.

The primary R23 study reports:

- 72 configurations;
- 72 accepted final proposals;
- 21,541 objective evaluations and 21,541 gradient evaluations;
- 68.729 seconds policy generation;
- 188.034 seconds final checking;
- 290.946 seconds total elapsed;
- an additional inherited dual-library construction cost of 415.789 seconds.

These numbers are sufficient to judge the main numerical-method claim.

---

## 4. Blocking second-pass findings

### R23-SP-F1 — The successful regional object is not a Bellman feedback policy on the original Markov state

The retained R21/R23 deployment semantics are explicit. The regional construction carries four financed subaccounts and fixed weights determined by the **initial** point in the rectangle. The policy uses the individual subaccount wealths and their corresponding expert controls, then aggregates them.

That is an admissible path-dependent control. It may be economically legitimate and its payoff can be certified.

It is not the same object as a feedback map
[
(t,u,x)longmapsto(c,	heta,p)
]
on the original Markov state.

Two histories can reach the same aggregate ((t,u,x)) while retaining different subaccount decompositions and initial interpolation weights, and hence need not deliver the same control. The manuscript itself effectively acknowledges this by describing “stored initial-state context and observable subaccounts.”

This distinction is decisive for a paper titled **Neural Bellman Operators**. Bellman operators are state-based dynamic-programming objects. A successful path-dependent expert portfolio does not become a Bellman policy merely because its payoff is compared to the Bellman value.

The authors have two scientifically coherent options:

- deliver a successful current-state policy on the original state variables; or
- formally redefine the state to include the expert/subaccount memory and then state exactly what Bellman problem is being solved on that augmented state.

At present the accurate numerical result and the named Bellman object are different computational objects.

### R23-SP-F2 — After class equality, the neural advantage is best interpreted as an uncharacterized implicit preconditioner

Proposition r23class proves that the neural and direct representations attain the same (16	imes3) finite-node raw-output arrays.

That removes an expressiveness explanation. It does **not** identify a neural numerical method.

The neural map has 355 trainable parameters and only 48 raw outputs at the sixteen nodes. Its Jacobian from parameter space to those outputs therefore has rank at most 48 and a null space of dimension at least 307. After financing, the effective policy family has another common-intercept quotient.

For a common policy-space objective (L(y)), neural gradient descent/Adam evolves through
[

abla_	heta L = J(	heta)^	op 
abla_y L.
]
Mapping a parameter update back to output space produces a state-dependent metric/preconditioner involving the neural Jacobian and, under Adam, the coordinatewise adaptive accumulator.

This is the most natural explanation of the observed neural–Adam/direct–Adam difference once the represented policies are equal.

R23 does not quantify that induced metric. It provides no:

- singular spectrum of the actual training Jacobian;
- output-space conditioning through training;
- effective preconditioner (J D^{-1}J^	op) under Adam;
- comparison to a direct optimizer using the induced or approximated preconditioner;
- invariance test under hidden-unit rescalings or equivalent network reparameterizations.

Consequently “parameterization effect” is descriptively true but scientifically incomplete. The paper has shown that **one nonlinear redundant coordinate system changes Adam’s trajectory**. It has not shown that neural representation contributes something that cannot be reproduced by a simpler explicit direct preconditioner.

For a top numerical-method paper, this mechanism must be isolated rather than named after the representation.

### R23-SP-F3 — Using the same scalar Adam learning rate is not a fair optimizer calibration

R23 calls the neural/direct comparison optimizer matched because both use Adam with learning rate (0.005).

Adam is not invariant to a nonlinear reparameterization, and even under simple coordinate scaling the same nominal scalar learning rate need not represent comparable steps in policy space.

That problem is especially severe here because the neural arm is deliberately overparameterized and the direct arm is not.

The experiment therefore establishes only:

> With this architecture, these initial weights, this common scalar learning rate, this finite proposal objective, and this 400-call cap, neural coordinates reach a better endpoint than the direct coordinates.

It does not establish a first-order solver advantage.

A publishable comparison needs, at minimum:

- a disjoint tuning set;
- a prospectively declared learning-rate/schedule family for each representation;
- a common tuning cost;
- a fixed selection rule;
- final held-out accuracy–work curves.

Better still, include direct diagonal scaling, whitening, quasi-Newton preconditioning, and an explicit approximation to the neural-induced output-space metric.

Until that is done, the main positive neural result is compatible with a poorly calibrated direct Adam baseline.

### R23-SP-F4 — The 47-coordinate quotient control is much weaker than the text suggests

The source code already centers the direct intercepts before pricing:
`b = b - b.mean()`.

Thus the 48-coordinate direct proposal objective is evaluated through a map that already annihilates the common-intercept direction before the financing offset is solved. The 47-coordinate quotient arm removes that redundant stored degree of freedom explicitly, but it does not create a fundamentally new conditioning test.

The nearly identical direct–Adam and quotient–Adam outcomes are therefore unsurprising.

This control rules out one bookkeeping null direction. It does **not** rule out:

- heterogeneous output scaling;
- slope/drift curvature;
- policy-space anisotropy;
- direct-variable whitening;
- diagonal or block preconditioning;
- neural-Jacobian-induced geometry.

The manuscript should not let the quotient experiment carry more identification weight than it deserves.

### R23-SP-F5 — The strongest tested accuracy–work frontier is classical/direct, not neural

The direct L-BFGS-B results are not a side note. They are the dominant numerical finding.

Across all three held-out ensembles, direct L-BFGS-B is more accurate, far cheaper in objective/gradient calls, and far faster in generation time than neural–Adam. It also exhibits striking stability across ensembles.

The most favorable interpretation of R23 is therefore not “the neural method is computationally superior,” but:

- neural overparameterization rescues one fixed Adam configuration;
- a strong direct deterministic optimizer still solves the tested policy class better.

For an Econometrica-level numerical-method contribution centered on the neural construction, the manuscript needs a regime where the neural mechanism changes the efficient accuracy–work frontier, not merely one where it improves a deliberately fixed first-order configuration.

### R23-SP-F6 — The full-state Neural Bellman Operator remains unresolved by orders of magnitude

The manuscript correctly retains the original (0.01) full-domain objective.

That makes the numerical shortfall impossible to treat as secondary. The current all-start-time bound near (7.24146) is roughly (724) times the target, and the revision still does not separately certify a strict payoff increase for the jointly changed full-state actor.

The improvement from (7.2783) to (7.2415) is a small tightening of a loose comparison, not evidence that the flagship current-state numerical problem is nearing resolution.

This alone prevents the full-state component from supporting the title-level claim.

### R23-SP-F7 — The optimizer is trained on a different numerical objective from the one used for publication accuracy

The R23 proposal objective in `budget_coordinates.py` uses a finite Gauss–Legendre/Gauss–Hermite quadrature and a finite-quadrature financing root. The final policy is then checked by the inherited directed continuous stopped-model certifier with different error accounting.

This separation is defensible for candidate generation. The endpoint payoff comparisons remain valid because the independent checker certifies the delivered policies.

But a numerical-method claim about **optimization behavior** needs more.

The observed neural/direct Adam ordering can depend on the surrogate gradient field. R23 gives no quantitative bound on:

- the error between the proposal gradient and the gradient of the continuous objective;
- how that error changes across representations along their different trajectories;
- whether the optimizer ordering survives quadrature refinement;
- whether the induced financing-root derivative is stable under refinement.

A basic robustness experiment should rerun the crossed comparison at multiple proposal quadrature orders, with the final continuous checker unchanged. An even stronger paper would bound the gradient mismatch.

Without that analysis, the claimed parameterization effect is partly a statement about optimization of one discretized surrogate.

### R23-SP-F8 — The acceptance operator is inactive in the primary R23 experiment

Every one of the 72 R23 final proposals is accepted.

Therefore the acceptance rule does not alter a single primary R23 endpoint.

The main numerical experiment is, operationally:

1. optimize a proposal objective;
2. certify the final policy;
3. observe that every final policy improves its incumbent.

The active rejection evidence comes from a separate stress test with deliberately different settings. That is useful software validation, but it does not establish that the acceptance operator contributes to the main accuracy or convergence result.

This matters because the word “operator” carries algorithmic content. In the principal R23 result, the gate is a post hoc verifier, not an iterated mechanism driving convergence or accuracy.

### R23-SP-F9 — The “held-out” evidence is a new-seed replication after the qualitative effect was already known

The R23 protocol is commendably explicit: it was fixed after inspection of all available R22 outcomes.

The architecture, optimizer pair, common Adam learning rate, work cap, economic problem, local rectangle, and qualitative contrast were therefore chosen with knowledge of the prior pattern.

The new seeds 23000, 23100, and 23200 are genuinely unused seeds, and no R23 configuration is dropped. That is good.

But this is a **held-out-seed replication of an already observed configuration**, not an independent validation of a numerical method across new problems or regimes.

The manuscript should use that exact description. A top-methodology claim needs an external dimension: new economic models, different horizons, different state regions, different discretizations, or a predeclared benchmark suite.

### R23-SP-F10 — Endpoint tables do not establish an anytime accuracy–work frontier

Adam is always run to the 400-call cap. Direct L-BFGS-B often reaches its endpoint in far fewer calls.

R23 reports final certified outcomes, but the primary package does not provide a common set of **certified checkpoints** showing regret/payoff versus:

- gradient calls;
- objective calls;
- wall time;
- total time including certification.

This matters because the central question is numerical efficiency. A single endpoint at a cap cannot show whether neural Adam reaches (0.01), (0.005), or (0.0035) earlier or later than a tuned direct method.

The next revision should report full anytime curves under a prospective checkpoint protocol.

### R23-SP-F11 — The successful local construction does not solve the state-coverage problem

The four-expert continuum theorem is mathematically useful. The cover-complexity proposition is also honest about the exponential worst case.

But the executed success remains one small two-dimensional initial-state rectangle at (t=0), with four experts and strong analytic model structure.

The paper does not execute:

- a multicell cover on the original economy;
- a higher-dimensional expert library;
- a regime where adaptive covering materially reduces the vertex burden;
- a case where the current exact pricing/hedging structure is unavailable.

Duplicating experts for latency is not a scaling experiment in the economic problem.

Thus the local success cannot support a broad numerical method for state-global dynamic economics.

### R23-SP-F12 — The certification system is a major separate algorithm whose slack and cost are not disentangled from solver quality

Regional regret depends on an inherited unrestricted dual upper library. Its historical construction cost is 415.789 seconds, larger than the new 290.946-second R23 study itself.

Moreover, the direct L-BFGS-B regional maxima repeatedly settle near (0.00283871). That may reflect genuine policy error, verifier/dual slack, or a combination. R23 does not decompose the certificate into these components tightly enough to know which part is limiting the apparent accuracy frontier.

For a certified solver, the verifier is legitimately part of the method. But then the paper should report:

1. policy-to-policy payoff differences, which do not require the dual;
2. policy lower-bound uncertainty;
3. dual upper-bound slack;
4. generator time;
5. final-policy verifier time;
6. dual construction time with and without amortization.

The current paper contains many of these ingredients, but it does not yet turn them into a clean end-to-end frontier.

---

## 5. Additional technical findings

### R23-SP-T1 — The exact-price bracket audit is an existence/conditioning certificate, not a delivered-root accuracy certificate

`continuous_budget_brackets.py` takes a frozen delivered policy and brackets an **additional common offset** under the exact continuous pricing measure.

That is a valid instantiation of the existence/conditioning theorem. It does not, by itself, show that the finite proposal offset was already close to the exact continuous offset.

The manuscript mostly acknowledges this distinction. It should be maintained rigidly in every table and dependency map. Feasibility of the delivered policy comes from the independent economic checker, not from a small proposal residual or from existence of a corrective exact-price root.

### R23-SP-T2 — The class-equivalence theorem should be paired with a local-rank/conditioning audit of the actual trained networks

The explicit (16	imes16) MPFR determinant certificate proves one constructed feature matrix is nonsingular and hence proves representational surjectivity.

It says nothing about the Jacobian of the randomly initialized/trained networks used in the experiment.

Because the claimed contribution is now optimizer geometry rather than expressiveness, the relevant numerical objects are:

- singular values of the actual output Jacobian;
- their evolution during optimization;
- the effective Adam metric in output space;
- sensitivity to hidden-unit rescaling/permutation;
- distance in delivered policy space per optimization step.

These diagnostics are no longer optional background. They are central to the claim.

### R23-SP-T3 — “Same gradient-call cap” must not be called “same work budget”

A gradient through 355 neural parameters and two hidden layers is not the same work as a gradient in 47 or 48 direct coordinates.

R23 reports wall time, which exposes this difference. The manuscript should consistently say “same objective/gradient-call cap,” not “same work budget,” unless work is normalized by an actual cost measure.

### R23-SP-T4 — The failed neural L-BFGS-B run should be diagnosed in policy space

The 23200 / vertex-3 neural L-BFGS-B run stops after roughly 100 evaluations with a much worse certified policy than the direct solution.

Because the finite-node output class is the same, this is a valuable test case for the claimed geometry.

Report, for this run:

- objective and certified-payoff trajectories;
- projected gradient norm;
- neural output Jacobian spectrum;
- distance to the direct solution in the 48 raw outputs and in financed policy coefficients;
- outcome under a restart;
- outcome under a benign hidden-layer rescaling;
- outcome under a direct preconditioner inferred from the neural Jacobian.

A paper about parameterization should explain its largest parameterization-induced failure.

### R23-SP-T5 — Training reproducibility still relies on transitive inherited code

The R23 environment record hashes the principal current scripts, but `run_study.py` imports R22 code and the checker reaches further into inherited revisions.

The publication manifest is extensive, which helps. For scientific reproduction of the training experiment, the review object should additionally expose one transitive dependency lock or machine-readable source DAG that identifies the exact inherited Python modules used by the scientific run.

Frozen-output replay is not the same thing as independent regeneration.

### R23-SP-T6 — A verifier-limited benchmark problem is needed

The paper would be much easier to assess if the same generator/certifier machinery were run on at least one closely related problem with a known or independently high-accuracy solution.

That would separate:

- optimizer error;
- policy-class approximation error;
- proposal quadrature error;
- checker lower-bound width;
- dual upper-bound slack.

At present all of these interact in the same bespoke economy.

### R23-SP-T7 — Certification checkpoints should be prospective

If anytime curves are added, checkpoint times must be fixed before looking at outcomes. Otherwise the paper risks replacing seed selection with checkpoint selection.

A simple rule such as certification after calls (25,50,100,200,400) for every arm would be adequate.

### R23-SP-T8 — The numerical-method identity must be stated as a complete algorithm

A reproducible method definition should specify, in one place:

- state supplied to the deployed policy;
- whether stored initial context/subaccounts are part of that state;
- policy parameterization;
- proposal objective and quadrature;
- optimizer and tuning rule;
- financing operation;
- acceptance rule;
- policy certifier;
- unrestricted upper verifier;
- reuse/amortization assumptions.

R23 contains these pieces across several revisions, but the reader still has to reconstruct which pieces are the method and which are only validators.

---

## 6. What would constitute a materially new revision

A new round should not add another layer of bookkeeping to the same fixed-(0.005), four-corner experiment. It needs new numerical evidence.

### N1 — Produce a successful current-state policy on the original state variables

The actor should be a genuine feedback policy on the declared Markov state, or the state augmentation required by the method should be made explicit.

The full-state certificate should improve by orders of magnitude and should include a separately certified policy-payoff improvement.

### N2 — Replace the fixed-learning-rate comparison by a tuned, prospective accuracy–work envelope

Tune neural and direct first-order methods separately on a disjoint tuning set with equal tuning resources.

Report final held-out frontiers versus calls, generation time, and end-to-end certified time.

### N3 — Benchmark the neural-induced metric against explicit direct preconditioning

Compute the output Jacobian/metric of the neural map and compare against at least:

- diagonally scaled direct Adam;
- a whitened/preconditioned direct method;
- a direct method using an approximation to the neural-induced output metric.

If these reproduce the neural advantage, the contribution should be stated as preconditioning rather than neural representation.

### N4 — Demonstrate robustness to proposal discretization

Repeat the crossed experiment under multiple prospectively fixed quadrature orders. Show that the ordering is stable, or provide a controlled gradient-error analysis.

### N5 — Add certified anytime curves

Use common predeclared checkpoints for every method and retain every checkpoint.

### N6 — Separate solver error from certificate slack

Include a benchmark with a known/high-accuracy reference and decompose the lower/upper certificate gap.

### N7 — Test a genuinely external problem dimension

Use at least one new economic model, a materially larger state region, a multicell cover, or a setting without the current exact financial replication structure.

New random seeds on the same local problem are not sufficient.

### N8 — Resolve the title-level identity

Either establish a competitive current-state Neural Bellman Operator, or reframe the paper around what is actually demonstrated:

> certified policy optimization with nonlinear overparameterization, exact financing, expert mixtures, and external dual verification.

The latter could still be interesting, but it is a different numerical-method claim.

---

## 7. Editorial points

1. The abstract should state that the successful regional policy uses four experts, stored initial-state context, and subaccount state.
2. “Held-out design” should be qualified as “held-out-seed replication after inspection of R22.”
3. “Optimizer matched” should not imply calibration matched; the common Adam learning rate is only a common hyperparameter value.
4. Replace “same work budget” by “same objective/gradient-call cap” wherever applicable.
5. “Parameterization effect” should be narrowed to “fixed-configuration Adam endpoint difference” until tuning and metric analyses are supplied.
6. The quotient experiment should be described as removal of one explicit gauge coordinate, not a general conditioning control.
7. The direct L-BFGS-B result should remain prominent; it is the strongest numerical solver in the present evidence.
8. The main text should state that all 72 primary proposals were accepted and hence the gate did not alter the principal R23 endpoints.
9. The full-state (7.241) bound should never be rhetorically combined with the local (0.003) result as though they were accuracy measurements of the same policy object.
10. The paper should distinguish an admissible path-dependent control from a Markov feedback policy whenever Bellman language is used.

---

## 8. Recommendation

**Reject in the present form.**

R23 is careful, reproducible by contemporary standards, and substantially stronger than its predecessors. The remaining issue is not presentation. It is that the numerical evidence does not yet support the named method.

The successful local construction is an analytically financed, path-dependent four-expert policy with stored state context. The actual current-state actor misses the declared target by roughly two to three orders of magnitude. The strongest end-to-end solver in the tested policy class is direct L-BFGS-B. The positive neural result is a fixed-learning-rate Adam comparison in a 355-dimensional redundant parameterization whose main numerical role is plausibly an implicit preconditioner, but that preconditioner is neither characterized nor compared against direct alternatives. The proposal and certified objectives are also numerically distinct, and the primary acceptance operator is never exercised.

These are publication-level barriers for an Econometrica-standard numerical-method paper. A scientifically compelling next revision requires a new algorithmic result and a new comparison design, not further certification of the same local endpoint.

---

## 9. Source map inspected in this second pass

### Current R23 referee object

- `ECTA_R23.tex`
- `SUPP_R23.tex`
- `RESPONSE_R23.tex`
- `revisions/2026-09-23-r23/PROTOCOL.md`
- `revisions/2026-09-23-r23/REPRODUCE.md`
- `revisions/2026-09-23-r23/PUBLICATION_MANIFEST.json`

### Current R23 manuscript and generated tables

- `revisions/2026-09-23-r23/paper/introduction.tex`
- `revisions/2026-09-23-r23/paper/method.tex`
- `revisions/2026-09-23-r23/paper/results.tex`
- `revisions/2026-09-23-r23/paper/conclusion.tex`
- `revisions/2026-09-23-r23/paper/proofs.tex`
- `revisions/2026-09-23-r23/paper/supplement.tex`
- `revisions/2026-09-23-r23/paper/crossed_table.tex`
- `revisions/2026-09-23-r23/paper/conditional_table.tex`
- `revisions/2026-09-23-r23/paper/full_ledger.tex`
- `revisions/2026-09-23-r23/paper/dependency_table.tex`

### Current R23 numerical source and records

- `revisions/2026-09-23-r23/replication/run_study.py`
- `revisions/2026-09-23-r23/replication/budget_coordinates.py`
- `revisions/2026-09-23-r23/replication/continuum_audit.py`
- `revisions/2026-09-23-r23/replication/continuous_budget_brackets.py`
- `revisions/2026-09-23-r23/replication/interpolation_certificate.py`
- `revisions/2026-09-23-r23/replication/tests.py`
- `revisions/2026-09-23-r23/results/study_summary.json`
- `revisions/2026-09-23-r23/results/continuum.json`
- `revisions/2026-09-23-r23/results/interpolation_certificate.json`
- `revisions/2026-09-23-r23/results/environment.json`

### Inherited policy semantics and continuum proof chain

- `revisions/2026-09-23-r22/replication/crossed.py`
- `revisions/2026-09-23-r22/replication/continuum.py`
- `revisions/2026-09-23-r22/replication/moment_jensen.py`
- `revisions/2026-09-23-r22/paper/method.tex`
- `revisions/2026-09-23-r22/paper/proofs.tex`
- `revisions/2026-09-23-r22/paper/results.tex`
- `revisions/2026-09-23-r22/paper/retained_r21_method.tex`
- `revisions/2026-09-23-r18/paper/retained_foundations.tex`
- `revisions/2026-09-23-r18/paper/aligned_proofs.tex`

The R23 referee-copy and development branches are byte-identical at the reviewed sealed commit `c09835c92042cb881d0bbdd3cab99b98d0a9d225`.
