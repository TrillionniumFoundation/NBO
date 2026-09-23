# External Referee Report — Neural Bellman Operators (R26)

**Venue standard:** Econometrica-level numerical / computational methodology  
**Recommendation:** **Reject in the present form. R26 is substantially more auditable than the earlier revisions, but the paper still does not deliver the numerical-method result advertised by its title on the original problem.**  
**Review date:** 2026-09-23  
**Reviewed repository:** TrillionniumFoundation/NBO  
**Reviewed revision branch:** revision/econometrica-r26-referee-copy-2026-09-23  
**Reviewed head:** ec845cb2f350bf902d10d789cde17fb69b841ffa  
**Equivalent science branch:** revision/econometrica-r26-certified-descent-2026-09-23 (identical head)  
**Review branch:** review/econometrica-r26-numerical-methods-2026-09-23-ec845cb

I read the R26 article source, supplement, response, revision index, protocol and reproduction notes, the new online rollback implementation, the second-order interval verifier, the exact Bernstein verifier, the R26 tests and frozen numerical summaries, and the extant R25 second-pass referee report. I also compared the R26 referee-copy branch with the R26 certified-descent branch and verified that they are identical.

The review below evaluates the submission as a numerical-method paper, not as a software-audit exercise. The repository is unusually explicit about negative findings and unresolved goals. That is a strength. It is not, however, a substitute for solving the central numerical problem or for demonstrating a method whose theory and computational evidence meet an Econometrica standard.

---

## 1. Executive assessment

R26 makes several real improvements over the scientific state represented by R25:

1. the submission is now an integrated manuscript rather than merely an integration protocol;
2. optimizer rollback is actually exercised, with five rejected proposals and exact restoration of saved optimizer state;
3. the manufactured stochastic benchmark receives a sharper second-order whole-box verifier;
4. the classical polynomial comparator is re-certified by an exact-rational Bernstein argument;
5. the paper adds a derivative-free quotient-polling theorem with an explicit interval-oracle accuracy requirement;
6. the manuscript no longer hides the fact that direct L-BFGS-B remains the strongest tested central-state method;
7. the original full-domain target is kept visible rather than being silently replaced by the easier auxiliary model.

These are constructive changes.

They still do not resolve the central publication problem.

The submission is titled **Neural Bellman Operators**, but the original Neural Bellman Operator objective is not achieved. The original current-state whole-domain regret certificate is **7.181834580823298** against the declared target **0.01**, a gap of roughly **718-fold**. No separate whole-domain policy-payoff improvement is certified. The exact stopped-gradient bridge remains uninstantiated. The strongest tested solver in the central comparison remains direct L-BFGS-B. The strongest new theorem is a generic certified direct-search result in quotient coordinates whose key regularity and oracle assumptions are not established for the original stopped problem. The strongest new numerical success is a verifier improvement on a deliberately manufactured problem whose exact witness is known and used to train the neural policies.

That collection is scientifically useful, but it is not yet a completed Econometrica-level numerical method.

A concise way to state the problem is:

> R26 has become a careful paper about how to certify, reject, and verify candidate policies, but it still does not show that the proposed neural Bellman methodology solves the difficult Bellman problem for which the paper is named, nor that the neural component supplies a numerical advantage unavailable to simpler classical methods.

---

## 2. The decisive numerical record

### 2.1 Original whole-domain objective

The manuscript retains the original target:

- original economy;
- current-state actor;
- all starting states and times;
- regret target 0.01.

The retained certificate is

\[
7.181834580823298.
\]

Therefore the current bound is approximately 718.18 times the target.

The paper is admirably explicit that this does **not** establish the target and that no separate policy-payoff improvement has been proved. That honesty is important, but it also fixes the publication-level conclusion: the principal numerical objective remains open by orders of magnitude.

### 2.2 Central held-out frontier

At proposal orders (8,16), the R26 article reports:

| Method | Worst regret upper | Calls | Generation (s) | Checking (s) |
|---|---:|---:|---:|---:|
| Neural Adam | 0.0019264 | 400 | 1.144 | 13.836 |
| Direct Adam | 0.0019367 | 400 | 1.016 | 13.887 |
| Moving transport Adam | 0.0019275 | 400 | 1.687 | 13.897 |
| Neural L-BFGS-B | 0.0096083 | 243 | 0.671 | 13.840 |
| **Direct L-BFGS-B** | **0.0019235** | **123** | **0.307** | **13.891** |

At proposal orders (12,24), direct L-BFGS-B again has the best regret upper bound, uses only 104 calls, and has 0.499 s proposal time, versus 400 calls and 2.113 s for neural Adam.

The paper also reports strictly negative matched neural-minus-direct L-BFGS-B payoff intervals.

Thus R26 does not merely lack evidence of neural superiority. Its strongest matched central experiment continues to favor the classical solver.

### 2.3 R26 rollback stress experiment

Across six trajectories and 18 block decisions:

- 13 proposals are accepted;
- 5 proposals are rejected;
- rejected states are restored exactly;
- four aggressive rejected candidates receive isolated shadow continuations;
- the shadow states differ from the actual restored trajectories.

This is a valid implementation test of synchronous rollback.

It is not evidence that rollback improves a prospectively tuned production method, and it is not evidence that the neural proposal mechanism is better. The protocol deliberately injects a rate of 20.48 to provoke adverse behavior. The experiment therefore demonstrates that the safety mechanism functions when stressed; it does not establish that the safety mechanism materially improves an economically relevant optimization frontier.

### 2.4 Manufactured stochastic verifier

For the two fixed neural policies, the second-order verifier obtains:

- seed 25201: 0.0008343368 on 32,768 cells;
- seed 25202: 0.0007884142 on 32,768 cells.

The same-cell first-order bounds are 0.00137310 and 0.00133294, respectively, so the second-order enclosure is genuinely sharper and crosses the 0.001 target at that cover.

The exact direct comparator obtains

\[
1.2978908373252045\times10^{-7}
\]

on only 64 one-dimensional cells.

This is a useful verified-numerics result. It is not an end-to-end neural Bellman solution. The benchmark is manufactured, the value witness is known, the neural policies are trained from known optimal actions, and the direct method is dramatically stronger on the same constructed problem.

---

## 3. Blocking findings

### R26-F1 — The referee lineage is internally inconsistent with the current repository

The R26 revision index states:

> Latest report addressed: reviews/2026-09-23-econometrica-r24/referee_report.md.

The R26 supplement and response likewise organize the rebuttal around R24-F1 through R24-F12.

But the repository currently contains the later branch

review/econometrica-r25-second-pass-numerical-methods-2026-09-23-cbb4c48

with the report

reviews/2026-09-23-econometrica-r25-second-pass/referee_report.md.

That second-pass report contains findings R25-SP-F1 through R25-SP-F12 and requested actions N1 through N7. R26 does not provide a finding-by-finding crosswalk to that report. Some items are incidentally addressed, but several of its central objections remain live.

I do not need to infer which report was available at which local preparation instant to identify the present defect: **the current referee copy calls R24 the latest report addressed even though the repository now exposes a more recent numerical-method review, and the response is not keyed to the latest extant review record.**

For a revision whose major selling point is auditability, this is a material process inconsistency.

A reconsiderable revision should include an explicit R25-SP disposition table and should state which findings are closed, partially closed, or still open.

### R26-F2 — The original numerical objective is still missed by approximately 718×

This remains the decisive scientific blocker.

The original target is 0.01. The retained all-start-time whole-domain bound is 7.181834580823298.

The paper therefore has not demonstrated that its named method solves its named problem.

The manuscript attempts to convert this into an honest “organizing objective” while emphasizing local methodological advances. That is better than overclaiming, but it creates a title-level mismatch. A top numerical-method paper cannot indefinitely retain the most ambitious title and central objective while the actual demonstrated result remains two to three orders of magnitude away.

The issue is not presentation. The computation has not closed the problem.

### R26-F3 — The numerical evidence still does not identify a neural advantage

The current central-state frontier favors direct L-BFGS-B in both accuracy and optimization work.

The auxiliary stochastic benchmark favors the direct polynomial comparator by several orders of magnitude.

The quotient-poll theorem is explicitly chart independent and does not require a neural parameterization.

The online rollback theorem is a generic certified acceptance statement and likewise does not require a neural representation.

Thus the strongest theory is not neural-specific, and the strongest experiments do not favor the neural solver.

This raises a basic contribution question:

> What numerical difficulty is solved by the neural representation that the direct representation cannot solve at comparable or lower certified cost?

R26 still has no convincing answer.

### R26-F4 — The finite-work quotient-poll theorem is conditional, not an instantiated complexity theorem for the original problem

The new theorem is mathematically reasonable as a direct-search statement under its assumptions. The problem is its relevance to the paper's actual hard computation.

The theorem assumes, among other things:

- continuously differentiable exact stopped payoff F on every poll segment;
- an L-Lipschitz gradient;
- complete feasibility of all prescribed poll points and segments;
- a valid interval oracle of width at most kappa h^2;
- an explicit oracle work function W(kappa h^2);
- a global upper payoff bound M over the relevant region.

The paper explicitly concedes that the original stopped checker has **not** been shown to provide arbitrarily shrinking intervals along every relevant trajectory and that the theorem has **not** been run as a 47-dimensional original-economy poll.

Consequently the displayed O(epsilon^-2) poll count is not an end-to-end complexity result for NBO. The real work is

\[
O(\varepsilon^{-2})\times W(c\varepsilon^2),
\]

and the behavior of W at the required precision is not established. If W grows rapidly, the poll-count statement can be computationally irrelevant.

For an Econometrica numerical-method contribution, the theorem must either be instantiated on the target computation or be presented as background theory rather than as a central resolution of the optimizer/certificate gap.

### R26-F5 — The stationarity theorem avoids the constrained-boundary problem by assumption

The economic coordinates are constrained. The control system itself has box constraints, financing restrictions, and implementation-specific feasible sets.

The poll theorem assumes that every direction in the positive spanning set can be evaluated on a feasible segment. The paper then explicitly states that a missing feasible direction at a boundary is not counted as an unsuccessful complete poll.

This means the theorem does not provide a first-order stationarity guarantee at precisely the points where economic optima often occur: active constraints and boundaries.

A numerical economics paper needs a constrained stationarity notion, for example:

- projected-gradient stationarity;
- tangent-cone / Clarke stationarity;
- KKT-compatible direct search;
- or a MADS-style boundary analysis.

Without that extension, the theorem applies to an interior regularity region, not to the full constrained economic optimization problem.

### R26-F6 — The original stopped-gradient bridge remains unresolved

R26 correctly refuses to claim that finite secants are derivative certificates.

The reduced-gradient perturbation proposition is also cleaner than earlier versions.

But the relevant constants are still not numerically instantiated along the original optimizer trajectory. Therefore the paper still does not know how accurately the differentiable proposal objective represents the economic gradient of the exact stopped objective.

This is not a secondary issue. Much of the narrative about neural geometry, Adam transport, and parameterization is meaningful only if the optimized surrogate direction can be related quantitatively to the exact economic objective.

The paper offers two escapes:

1. rigorous finite payoff comparisons;
2. a conditional derivative-free poll.

The first is useful but does not characterize the optimization direction. The second has not been instantiated on the original problem.

The bridge is therefore still open.

### R26-F7 — The moving historical-transport control still does not isolate the neural mechanism

The R25 second-pass report identified a specific mechanism problem:

- the moving arm is heavily affected by an output cap;
- carrier and economic quotient states drift;
- the nonlinear finite-step output remainder is omitted;
- the recorded carrier/economic mismatch is material.

R26 does not repair that experiment. It explains the omission more clearly and labels the control honestly as a moving-transport approximation.

That is good scientific hygiene, but it does not resolve the mechanism question.

The R26 response even says that the moving control “meets the requested moving/historical-transport comparison.” That is too strong relative to the second-pass finding. It supplies **a** historical-transport comparison, but not a faithful isolation of the neural trajectory.

A convincing control still needs one of the following:

- recenter economic coordinates on realized carrier outputs after each step;
- solve a local inverse problem that keeps the carrier aligned;
- rigorously bound the accumulated mismatch and nonlinear remainder;
- or show that the cap is inactive in the regime used for mechanism interpretation.

Until then, no irreducible neural-geometry conclusion is identified.

### R26-F8 — The rollback result is an engineering stress test, not an algorithmic performance result

The new rollback execution is correctly coupled and materially better than replaying a completed trajectory.

However, the stress block is deliberately set to the extreme rate 20.48 after the authors have inspected the R25 behavior. The R26 protocol itself correctly labels the seeds “diagnostic stress seeds” and says the study is not a tuned frontier.

Therefore the conclusion supported by the evidence is narrow:

> If an adverse candidate is generated, the implementation can reject it and exactly restore the saved optimizer state.

That is valuable.

What is not established is:

- how often harmful proposals arise under a prospectively selected production schedule;
- whether rollback improves final certified payoff relative to an uncoupled but otherwise identical optimizer;
- whether the certification overhead is justified by avoided losses;
- whether direct L-BFGS-B with the same certification gate would dominate the neural/Adam pipeline;
- whether the rollback design changes scaling in larger state spaces.

For a top numerical-method paper, a safety mechanism should be evaluated as part of an actual solver, not only as a fault-injection test.

### R26-F9 — The stochastic benchmark is still a verifier benchmark, not an unknown-solution Bellman benchmark

The manufactured stochastic example has real virtues:

- stopping;
- two Brownian sources;
- unspanned risk;
- whole state-time coverage;
- nontrivial interval propagation.

But the transfer is chosen so that the value is known, and the neural actors are fitted from the known optimal actions.

Thus the benchmark removes the main difficulty of Bellman computation: discovering the solution.

The direct comparator also uses exact structure and is vastly superior.

The experiment therefore validates:

- interval propagation;
- action approximation;
- restart certification;
- and the second-order enclosure.

It does not validate the paper's end-to-end Neural Bellman Operator as a solver for an unknown stochastic control problem.

R26 still lacks the unknown-solution stochastic benchmark requested in the R25 second-pass review.

### R26-F10 — The second-order verifier improvement has no demonstrated high-dimensional scaling story

Reducing the successful cover from 262,144 cells to 32,768 cells is a real improvement for the fixed three-dimensional manufactured benchmark.

But the method propagates interval first and second derivatives through a network and stores complete cell data. The paper gives no complexity study as state dimension, network width, or domain anisotropy increases.

That omission matters because interval Hessian methods are particularly vulnerable to:

- dependency inflation;
- quadratic growth in mixed derivative terms;
- exponential growth in rectangular covers;
- memory growth from per-cell certificate storage.

A three-dimensional benchmark does not establish that the proposed verifier is suitable for the high-dimensional problems that motivate neural approximators.

A credible scaling section should vary at least state dimension, architecture size, and tolerance, and should compare total verification work against sparse-grid, adaptive partition, or other validated baselines.

### R26-F11 — End-to-end computational cost remains incompletely measured

R26 improves the accounting language. It now states a complete cost formula and explicitly identifies excluded setup and shared-dual costs.

But the main tables still do not report that complete cost.

The held-out tables exclude common preprocessing and dual construction. The online table excludes inherited common dual construction and initial model construction. Different environments are correctly not compared as hardware speedups.

This means the paper is still unable to answer the practical question:

> What is the end-to-end cost of obtaining a certified policy from scratch?

That is the relevant quantity for a numerical method.

The current data are sufficient to say that checking dominates proposal generation. They are not sufficient to make a complete efficiency claim.

### R26-F12 — Robustness remains too narrow for a parameterization-sensitive method

The central held-out comparison uses two evaluation seeds and two proposal quadrature rules.

The stochastic verification uses two fixed neural policies.

The architecture is essentially fixed.

The paper itself documents severe parameterization sensitivity in prior revisions.

This is not a statistical-inference objection; these are deterministic computational experiments. It is a numerical robustness objection. A method whose performance depends strongly on initialization, chart, cap, learning rate, and optimizer requires a structured sensitivity study.

At minimum, the paper should separate robustness to:

- initialization;
- architecture;
- parameter chart;
- learning-rate schedule;
- trust/output cap;
- proposal quadrature;
- verification tolerance;
- state dimension;
- domain geometry.

Two seeds do not characterize these dimensions.

### R26-F13 — The literature positioning is not remotely adequate for an Econometrica numerical-method paper

The R26 article bibliography contains only four references:

- Brown, Smith, and Sun (2010);
- Brumm and Scheidegger (2017);
- Judd (1998);
- Kushner and Dupuis (2001).

This is far too sparse to support a novelty claim for a paper combining:

- derivative-free direct search;
- certified/validated numerics;
- interval arithmetic;
- neural approximation;
- stochastic control;
- policy iteration;
- Bellman operators;
- computational economics.

The paper needs to position its contribution relative to modern direct-search and derivative-free optimization theory, verified numerical computation, neural HJB/PDE and stochastic-control solvers, approximate dynamic programming, policy iteration, and high-dimensional computational economics.

At present the novelty boundary is impossible to assess from the manuscript itself.

### R26-F14 — The reported 0.823% “progress” on the original bound mixes distinct sources of improvement

R26 repeatedly compares 7.181834580823298 to the reviewed R24 value 7.241462443133396 and reports a reduction of about 0.823%.

The R25 second-pass audit identified an untouched fine warm-start bound of 7.2004087464242685. Relative to that immediate computational baseline, the retained actor improves the bound by only about 0.0185742, roughly 0.258%.

The difference between 0.823% and 0.258% is not cosmetic. It appears to combine changes in certification/reference treatment with the policy continuation itself.

Because the manuscript already concedes that it has no separate payoff-improvement certificate, it should decompose the numerical change into:

1. verification tightening;
2. witness/reference changes, if any;
3. actual policy changes;
4. optimization continuation.

Otherwise the “progress” percentage can be read as optimizer progress when it is not.

---

## 4. Additional technical findings

### R26-T1 — The poll work bound should be reported as oracle work, not as an epsilon-squared complexity headline

The theorem correctly retains W(kappa h^2), but the prose still emphasizes O(epsilon^-2) polls. For the target application, oracle refinement is the expensive object. The manuscript should give the combined asymptotic statement first and should not let the poll count visually dominate the actual verification complexity.

### R26-T2 — A failed checker cannot be silently treated as an unsuccessful optimization direction

The executed online algorithm treats checker failure as rejection, which is safe for deployment.

The stationarity theorem is different: it requires a valid interval at every prescribed poll point. If the checker cannot produce the required width, the direction is not evidence of stationarity.

The paper mostly respects this distinction, but the algorithmic pseudocode and discussion should make it impossible to confuse “not certified” with “non-improving” in the theoretical poll.

### R26-T3 — The exact-real interpretation of stored binary64 weights should remain narrowly scoped

The interval certificate treats saved binary64 weights as exact real coefficients. That is legitimate for certifying the mathematical function represented by the saved numbers.

It is not a floating-point execution certificate for arbitrary deployment hardware.

The manuscript says this, and that qualification should remain prominent.

### R26-T4 — The direct Bernstein comparator is appropriate as a verifier control, not as a general solver comparison

The direct comparator knows the exact portfolio action and approximates only a one-dimensional reciprocal structure.

Its extremely strong certificate is useful because it prevents false claims of neural superiority.

It should not be promoted into a general statement that polynomial control dominates neural methods. Conversely, its structural advantage does not rescue the neural benchmark as a fair discovery task.

### R26-T5 — The test suite validates implementation invariants, not the original theorem hypotheses

The 11 R26 tests are useful. In particular, they check symbolic completion, jet propagation, exact Bernstein conversion, cover completeness, rollback identity, and preservation.

But the quotient-poll theorem is tested only on a small exact quadratic example. There is no test or certified audit that the original stopped objective satisfies the theorem's differentiability, Lipschitz, feasibility, or shrinking-oracle assumptions.

Passing the test suite therefore does not materially close R26-F4.

### R26-T6 — Table-level regret summaries are insufficient for solver diagnostics

The paper reports worst regret, calls, and times. For a method with strong path dependence, the supplement should also expose distributions or trajectories for:

- accepted/rejected block margins;
- interval widths;
- actual payoff lower/upper endpoints;
- effective step norms;
- cap activity;
- carrier mismatch;
- checker refinement levels.

The raw files may contain much of this information; the paper should summarize it in the scientific presentation.

### R26-T7 — The paper needs a clean distinction between “safe monotonic deployment” and “optimization convergence”

The verified-improvement proposition is a monotonic deployment guarantee.

The poll theorem is a conditional stationarity result.

Adam has no convergence theorem here.

These are three different claims. The current manuscript is better than earlier revisions, but it still packages them under a common “certified policy improvement” narrative that can suggest a stronger integrated convergence result than is actually proved.

### R26-T8 — The paper is short on economic insight relative to its technical machinery

The original economic model is stylized, and the manuscript's main conclusions are about numerical certification, optimizer geometry, and verification.

That can be acceptable for a computational-method paper, but then the method must carry the contribution.

Because the method still fails on the original target and the neural component lacks an identified advantage, the paper currently has neither a solved economically substantive application nor a decisive general numerical theorem.

---

## 5. What R26 did successfully close

For clarity, several earlier objections are genuinely improved or closed.

### Closed / substantially closed

- **Integrated submission object:** R26 now has article, supplement, response, review entry, PDFs, protocol, reproduction notes, and a current revision index.
- **Actual rollback execution:** five real rejections are exercised and complete optimizer state restoration is checked.
- **Exact direct verifier arithmetic:** the new Bernstein calculation removes the old floating derivative-coefficient shortcut.
- **Sharper fixed-policy neural verification:** second-order intervals reduce the cell count needed to cross the 0.001 target on the manufactured benchmark.
- **Negative-result disclosure:** the paper clearly states that direct L-BFGS-B is stronger on the tested central frontier and that the original objective is still missed.

### Only partially closed

- **Gradient/certificate gap:** theorem added, original constants not instantiated.
- **Finite-work optimization:** conditional poll theorem added, original oracle/regularity assumptions not established.
- **Neural geometry mechanism:** moving historical transport exists, but the faithful mechanism-isolation problem remains.
- **Restart coverage:** solved only in the auxiliary manufactured economy, not in the original financed setting.
- **Scaling:** better verifier in 3D, no high-dimensional evidence.
- **Online coupling:** rollback works under stress, but production value is unproven.

---

## 6. Requirements for a materially reconsiderable next revision

### N1 — Address the actual latest extant referee report

Provide a line-by-line disposition of R25-SP-F1 through R25-SP-F12 and N1 through N7.

Do not call R24 the latest report addressed while a later numerical-method report is present in the repository.

### N2 — Close the original 0.01 target by orders of magnitude

A move from 7.18 to, for example, 6.9 would not change the conclusion.

The next revision needs a qualitatively different result on the original current-state whole-domain problem.

### N3 — Produce a genuine unknown-solution stochastic control benchmark

The training procedure must not receive the exact value or exact optimal actions.

Neural and classical methods should receive the same information set.

A high-accuracy independent reference can be generated afterward for evaluation and certification.

### N4 — Instantiate the direct-search theorem on the original economy

At minimum:

- prove or certify a relevant Lipschitz-gradient bound;
- establish an implementable constrained poll;
- certify the required interval widths;
- report W(delta) empirically and, if possible, theoretically;
- execute the 47-dimensional poll or an economically meaningful reduced version.

### N5 — Extend the theory to constrained stationarity

Use projected, tangent-cone, KKT, or MADS-compatible stationarity so that active economic constraints are part of the theorem rather than excluded by the feasibility assumption.

### N6 — Repair the mechanism-isolation experiment

Recenter or invert the carrier, or rigorously control:

- carrier/economic mismatch;
- nonlinear output remainder;
- cap activity;
- effective step size.

Then repeat the held-out comparison.

### N7 — Evaluate rollback as part of a prospectively selected solver

Use a schedule fixed before outcomes, compare coupled and uncoupled variants, and include the strongest classical solver with the same certification gate.

Report whether rollback changes final certified payoff and total work, not merely whether state restoration functions.

### N8 — Add dimensional scaling experiments

At least vary:

- state dimension;
- network width/depth;
- domain resolution;
- target tolerance.

Report proposal cost, interval-verification cost, memory, and total certified cost.

### N9 — Report a complete from-scratch cost ledger

Include:

- model construction;
- dual/reference construction;
- proposal generation;
- geometry/Jacobian work;
- verification;
- refinement;
- rollback bookkeeping;
- memory footprint.

Amortization should be shown separately rather than assumed.

### N10 — Expand the literature review and sharpen the novelty claim

The paper needs a serious related-work section. Four references are not enough for this contribution area.

The authors should explain precisely which theorem or algorithm is new relative to established derivative-free optimization, validated numerics, neural stochastic-control methods, and computational-economics solvers.

### N11 — Decompose original-bound improvement

Separate verification improvement from policy improvement and optimizer continuation. Do not use a single percentage that pools them.

### N12 — Decide whether the title is still scientifically accurate

If the next revision still cannot demonstrate a Neural Bellman Operator on the original problem or a neural-specific numerical advantage, then the title and central framing should be reconsidered.

The current evidence supports a paper about **certified policy comparison, rollback, and validated neural-policy verification** more directly than it supports the broad title **Neural Bellman Operators**.

---

## 7. Recommendation

**Reject in the present form.**

R26 is better organized, more candid, and more reproducible than the earlier revisions. The second-order verifier and exact Bernstein correction are legitimate numerical contributions. The synchronous rollback implementation is real. The conditional poll theorem is mathematically useful.

But an Econometrica-level numerical-method article needs the theory and computation to meet on the difficult target problem.

Here they still do not.

- The original whole-domain target is missed by roughly 718×.
- No separate original whole-domain payoff improvement is certified.
- Direct L-BFGS-B remains the strongest tested central-state method.
- The main direct-search theorem is not instantiated on the original stopped objective.
- Constrained-boundary stationarity is not covered.
- The exact stopped-gradient bridge is still absent.
- The moving-transport control still does not isolate the neural mechanism.
- The rollback result is a deliberate stress test rather than a demonstrated production advantage.
- The successful stochastic experiment uses a known witness and is primarily a verifier benchmark.
- High-dimensional verifier scaling is not shown.
- End-to-end certified cost is not measured.
- The literature positioning is much too thin.
- The R26 response is keyed to R24 even though a later R25 second-pass report exists in the repository.

The repository now demonstrates that the authors can build an unusually auditable computational record. The remaining obstacle is no longer auditability. It is scientific closure: the named method still has not solved, outperformed, or theoretically covered the problem that motivates the paper.

---

## 8. Source map inspected

### R26 manuscript and response

- ECTA_R26.tex
- R26_REVIEW.md
- REVISION_INDEX.md
- revisions/2026-09-23-r26/paper/model.tex
- revisions/2026-09-23-r26/paper/method.tex
- revisions/2026-09-23-r26/paper/stochastic.tex
- revisions/2026-09-23-r26/paper/evidence.tex
- revisions/2026-09-23-r26/paper/proofs.tex
- revisions/2026-09-23-r26/paper/conclusion.tex
- revisions/2026-09-23-r26/paper/response.tex
- revisions/2026-09-23-r26/paper/supplement.tex
- revisions/2026-09-23-r26/paper/references.tex

### R26 protocol and reproduction

- revisions/2026-09-23-r26/PROTOCOL.md
- revisions/2026-09-23-r26/REPRODUCE.md

### R26 implementation

- revisions/2026-09-23-r26/replication/online_stress.py
- revisions/2026-09-23-r26/replication/jet_certificate.py
- revisions/2026-09-23-r26/replication/test_revision.py

### R26 numerical summaries

- revisions/2026-09-23-r26/results/test_summary.json
- revisions/2026-09-23-r26/results/local_environment.json
- revisions/2026-09-23-r26/results/jet_summary.json
- revisions/2026-09-23-r26/results/online_summary.json
- revisions/2026-09-23-r26/paper/heldout_8_16.tex
- revisions/2026-09-23-r26/paper/heldout_12_24.tex
- revisions/2026-09-23-r26/paper/online_table.tex
- revisions/2026-09-23-r26/paper/jet_table.tex

### Prior referee context

- review/econometrica-r25-second-pass-numerical-methods-2026-09-23-cbb4c48
- reviews/2026-09-23-econometrica-r25-second-pass/referee_report.md

### Branch identity checked

- revision/econometrica-r26-certified-descent-2026-09-23
- revision/econometrica-r26-referee-copy-2026-09-23

These two R26 branches resolve to the same reviewed head ec845cb2f350bf902d10d789cde17fb69b841ffa.
