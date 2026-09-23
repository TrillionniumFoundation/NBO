# External Referee Report — Neural Bellman Operators (R25, second-pass numerical-methods review)

**Venue standard:** Econometrica-level numerical / computational methodology  
**Recommendation:** **Reject in the present form; the reviewed branch is not yet a completed R25 submission and the central numerical-method claim remains unsupported by the strongest executed evidence.**  
**Review date:** 2026-09-23  
**Reviewed repository:** TrillionniumFoundation/NBO  
**Reviewed revision branch:** `revision/econometrica-r25-integrated-response-2026-09-23`  
**Reviewed head:** `cbb4c4826978fc228ad89f693eb369b75cb89fd6`  
**Review branch:** `review/econometrica-r25-second-pass-numerical-methods-2026-09-23-cbb4c48`

This is an independent second-pass review of the same R25 head. I read the R25 prospective protocols, the executed R25 numerical evidence, the relevant R24 referee baseline, the full-state continuation, the stochastic reference, the held-out ledger, the online ledger, the certified secants, and the moving-transport implementation/history. I do not treat the pre-existing R25 referee report as a substitute for this review.

---

## 1. Executive assessment

R25 is a serious scientific iteration. It fixes several weaknesses of R24: the first-order rate grid is expanded prospectively; the selected rates are no longer at the upper boundary; the paper now contains a moving historical-transport direct control; certification is inserted into an online optimizer loop; a nonreplicable stochastic stopped benchmark is globally interval-verified; and the original current-state full-domain actor/witness problem is revisited rather than replaced by an auxiliary benchmark.

Those are meaningful improvements.

They do not, however, resolve the central Econometrica-level question: **does the Neural Bellman Operator construction deliver a numerically superior or uniquely enabling method for the original difficult Bellman problem, once accuracy, work, parameterization, certification, and classical controls are treated on equal terms?**

The answer supported by the current R25 evidence is still no.

Three facts are decisive.

1. **The original full-domain target remains missed by about a factor of 718.** The retained fine all-start-time regret certificate is (7.181834580823298), versus the stated target (0.01). Relative to the untouched fine warm start (7.2004087464242685), the improvement is only (0.0185741656), about (0.258%). After the first proposal block, the next three L-BFGS-B blocks execute one gradient call, accept zero optimizer iterations, and produce no further certificate improvement.

2. **The held-out accuracy/work frontier remains classical.** Direct L-BFGS-B has worst certified regret (0.0019235324), mean 113.5 gradient calls, and about 0.403 seconds of proposal generation. Neural Adam has worst regret (0.0019263760), 400 calls, and about 1.629 seconds. The new moving historical-transport arm has worst regret (0.0019278023), 400 calls, and about 2.163 seconds. Neural L-BFGS-B remains fragile, with worst regret about (0.00960835).

3. **The new moving-transport control is not yet a faithful mechanism-isolation experiment.** In the four held-out moving runs, the fixed output cap is active in 112, 112, 137, and 185 of 400 steps. The smallest trust scales are about 0.0160, 0.0160, 0.0145, and 0.0145. The cumulative carrier/economic-quotient mismatch reaches approximately 0.324, 0.324, 0.432, and 0.719, while the implementation explicitly drops the finite-step nonlinear output remainder. Thus the control is a heavily clipped, linearly pushed historical-Jacobian method whose carrier can drift materially away from the economic coordinates on which the objective gradient is evaluated. It is useful, but it does not identify an irreducible neural contribution.

There is also a threshold packaging problem: the reviewed head is an **integration protocol**, not an integrated R25 paper. The protocol says that an R25 manuscript, supplement, response, independent audit, rollback stress execution, compiled PDFs, revised index, and sealed referee copy still need to be produced. At the reviewed head, `ECTA_R25.tex`, `SUPP_R25.tex`, and `RESPONSE_R25.tex` are absent, and `REVISION_INDEX.md` still says that R23 is the current review object.

Accordingly, this branch is not review-ready as a completed paper revision, and the executed science does not yet support the strongest numerical-method interpretation of the title.

---

## 2. What R25 genuinely improves

### 2.1 The first-order tuning design is materially better

The prospective rate family is expanded to

[
{0.005,0.02,0.08,0.32,1.28,5.12,20.48}.
]

The selected nominal rates are interior:

- neural Adam: 0.08;
- direct Adam: 0.32;
- diagonal Adam: 0.32;
- tangent Adam: 0.32;
- whitening Adam: 0.08;
- moving historical transport Adam: 0.32.

This resolves the simple R24 objection that all first-order methods were tuned at the largest tested rate.

### 2.2 A moving historical-transport direct control now exists

The new arm recomputes a quotient Jacobian, pulls a quotient gradient back into the 355-parameter carrier, applies Adam moments in carrier coordinates, and pushes the resulting parameter displacement forward through the current Jacobian.

This is substantially more informative than the earlier static tangent/whitening controls.

### 2.3 Certification is coupled to optimization online

The R25 online experiment snapshots parameters and optimizer moments, certifies each 100-call candidate, accepts only on strict lower-bound/upper-bound separation, and restores state on rejection.

This is the correct architecture for a certificate-coupled optimizer.

### 2.4 The stochastic reference is a real verification stress test

The manufactured economy has two independent Brownian shocks, an unspanned productivity state, first-exit/terminal stopping, a current-state control, and a complete state-time interval certificate. This is much more informative for verification than the earlier simple analytic benchmark.

### 2.5 The original state-time problem is not abandoned

R25 restarts the original current-state actor/witness and audits it with the inherited MPFR checker on both coarse and fixed finer covers. This is the right research direction.

---

## 3. Decisive numerical record

### 3.1 Held-out frontier

Across the four held-out cells (two seeds times two proposal quadrature orders):

| Method | Worst certified regret | Mean gradient calls | Mean proposal generation (s) | Mean checker time (s) |
|---|---:|---:|---:|---:|
| neural Adam | 0.0019263760 | 400.0 | 1.6286 | 13.8777 |
| direct Adam | 0.0019366958 | 400.0 | 1.4789 | 13.9310 |
| diagonal Adam | 0.0019328550 | 400.0 | 1.4849 | 13.9298 |
| tangent Adam | 0.0020834795 | 400.0 | 1.4924 | 13.8593 |
| whitening Adam | 0.0179100178 | 400.0 | 1.4708 | 13.9013 |
| moving historical transport Adam | 0.0019278023 | 400.0 | 2.1632 | 13.8617 |
| neural L-BFGS-B | 0.0096083472 | 242.5 | 0.9445 | 13.8309 |
| **direct L-BFGS-B** | **0.0019235324** | **113.5** | **0.4029** | 13.8126 |

The checker dominates end-to-end time, so the proposal-generation gaps should not be exaggerated. But there is also no neural end-to-end advantage to report: the neural representation does not improve the certified frontier, and it requires more optimization work.

### 3.2 Original full-state target

Target:

[
0.01.
]

Fine fixed-cover results:

- untouched warm start: (7.2004087464242685);
- retained R25 actor: (7.181834580823298).

The retained certificate is therefore about **718.18 times the target**.

The fine-cover improvement is only (0.0185741656), about **0.258%** of the untouched bound.

The proposal sequence is also diagnostic:

- block 1: 82 gradient calls, 48 accepted optimizer iterations, bound improves to 7.2116293096 on the coarse audit;
- blocks 2–4: one gradient call each, zero accepted optimizer iterations, identical candidate and incumbent hashes, no further progress.

The artifact correctly records `payoff_improvement_proved = false`.

### 3.3 Stochastic reference

Neural seed 25201:

- 4,096-cell cover: regret 0.00939394;
- 32,768-cell cover: 0.00137310;
- 262,144-cell cover: 0.000766312;
- generation about 1.59 s;
- final verification about 42.72 s.

Neural seed 25202:

- 4,096-cell cover: 0.01128653;
- 32,768-cell cover: 0.00133294;
- 262,144-cell cover: 0.000685539;
- generation about 1.54 s;
- final verification about 42.85 s.

Direct degree-eight control:

- 4,096-cell cover: 0.000193498;
- generation about 0.0015 s;
- verification about 0.043 s.

The neural actors are certified, which is useful. The benchmark does not demonstrate neural discovery of an unknown Bellman solution: the exact witness is used in training, and the direct control exploits the known structure.

### 3.4 Moving historical transport diagnostics

Held-out moving-arm histories:

| Seed / quadrature | Capped steps / 400 | Minimum trust scale | Max carrier/economic mismatch | Max dropped nonlinear remainder |
|---|---:|---:|---:|---:|
| 25101 / (8,16) | 112 | 0.01601 | 0.32417 | 0.05671 |
| 25101 / (12,24) | 112 | 0.01601 | 0.32401 | 0.05671 |
| 25102 / (8,16) | 137 | 0.01450 | 0.43198 | 0.07336 |
| 25102 / (12,24) | 185 | 0.01450 | 0.71863 | 0.07336 |

This is not a negligible implementation detail. The mechanism control spends a substantial share of its trajectory under the artificial displacement cap, and its carrier ceases to coincide closely with the quotient coordinates that define the actual candidate.

For tuning seed 25001, the nominal moving-arm rates 1.28, 5.12, and 20.48 are capped on **all 200 steps** and produce the same certified tuning score. That means the high-rate portion of the nominal grid is not identifying a genuine learning-rate response; it is identifying the same capped update regime.

---

## 4. Blocking findings

### R25-SP-F1 — The reviewed head is not an integrated R25 manuscript

This is a threshold submission problem.

The head commit adds `INTEGRATION_PROTOCOL.md`. That protocol itself says the following remain to be done:

- produce the complete Econometrica-style R25 manuscript;
- produce R25 supplement and response;
- execute the independent audit;
- execute the fixed rollback stress experiment;
- add the finite-poll theorem and corrected error accounting;
- update the revision index;
- compile and inspect all PDFs;
- publish hashes/manifests;
- create a sealed referee-copy branch.

At the reviewed head:

- `ECTA_R25.tex` is absent;
- `SUPP_R25.tex` is absent;
- `RESPONSE_R25.tex` is absent;
- no R25 integrated paper directory is present;
- `REVISION_INDEX.md` still says **Current review object: R23**.

The strongest R25 numerical results exist, but the R25 paper that states and interprets them does not.

A referee cannot sign off on scope, theorem-to-code consistency, or claims language before the integrated manuscript exists.

### R25-SP-F2 — The original full-domain problem remains quantitatively open by orders of magnitude

The retained fine all-start-time certificate is (7.181834580823298) against target (0.01).

This is not a near miss.

It is an approximately 718-fold gap.

Moreover, the continuation does not show a trajectory toward closing the gap: after one modest improvement, the proposal optimizer is immediately stationary for the next three blocks.

For the paper's original current-state objective, the central numerical problem is still unresolved.

### R25-SP-F3 — The neural representation still does not improve the held-out accuracy/work frontier

Direct L-BFGS-B is slightly more accurate in worst certified regret and vastly cheaper in gradient calls and proposal generation than neural Adam.

The new moving arm also fails to beat direct L-BFGS-B.

The fact that checker time dominates the full wall clock does not rescue the neural claim. It means that the paper should compare complete certified pipelines. On that basis, neural parameterization still provides no demonstrated advantage.

For a top numerical-method contribution, one needs a regime in which the neural construction either:

- attains accuracy unavailable to classical coordinates at comparable work;
- scales to a dimension/geometry where the classical control fails;
- materially reduces total certified cost;
- or enables a theorem/certificate that cannot be obtained for the direct method.

R25 shows none of these on the central experiment.

### R25-SP-F4 — The moving historical-transport experiment does not yet isolate the neural mechanism

This is the most important new finding from the second-pass audit.

The moving arm is intended to ask whether neural Adam's advantage is explained by historical Jacobian/moment transport.

But the executed control is not simply “neural transport without the neural representation.”

It evaluates the economic objective on quotient coordinates (z), computes a quotient gradient there, evaluates the Jacobian on a separate carrier network, takes an Adam step in carrier parameters, linearly pushes that step into quotient space, explicitly drops the nonlinear output remainder, and allows carrier outputs and quotient coordinates to diverge.

That divergence is empirically material: max mismatch reaches about 0.72 in one held-out run.

The output cap is also active for 28%–46% of held-out steps.

Therefore the experiment confounds at least four effects:

1. historical neural Jacobian transport;
2. linearization error from the dropped nonlinear remainder;
3. carrier/quotient state mismatch;
4. a hard output trust cap.

The correct conclusion is that this **particular regularized/capped linearized historical transport** does not beat the tested neural or direct methods.

It does not establish that the neural map contributes an irreducible mechanism beyond output geometry.

A convincing mechanism control should either reproject/recenter the economic quotient onto the carrier outputs after every step, control the nonlinear remainder rigorously, or demonstrate that the carrier mismatch is uniformly negligible in the regime used for interpretation.

### R25-SP-F5 — The moving-arm “bracketed learning rate” is partly an artifact of the displacement cap

The tuning ledger labels 0.32 as an interior optimum and larger rates as deterioration.

That statement is numerically true for the **capped algorithm**, but it should not be interpreted as clean learning-rate identification.

For seed 25001:

- rate 0.32 is capped on 99/200 steps;
- rates 1.28, 5.12, and 20.48 are capped on 200/200 steps;
- those three rates produce the same certified tuning score;
- the final update remains exactly at the 0.5 step cap.

Thus nominal rates differing by a factor of 16 collapse to the same effective dynamics.

The next version should report the distribution of effective step norms and trust scales in the tuning table. For the moving method, a tuning parameter is not identified once the trust cap binds almost everywhere.

### R25-SP-F6 — The stochastic benchmark validates the verifier much more strongly than it validates NBO

The benchmark is mathematically well designed for verification:

- exact smooth value;
- exact optimal actions;
- exact Hamiltonian-square completion;
- stopping;
- unspanned risk;
- whole-box interval verification.

But the exact witness is explicitly used in neural training.

The neural actor is therefore learning an oracle-defined action target through a known-witness Hamiltonian deficit. It is not discovering an unknown value function or solving an unknown Bellman fixed point.

The direct comparator also uses the known structure and is far more efficient.

This experiment should be sold as:

- a global verifier stress test;
- a certified approximation experiment;
- a test of interval scaling for frozen neural policies.

It should not be used as evidence that NBO is an efficient end-to-end stochastic Bellman solver.

### R25-SP-F7 — The exact stopped-objective gradient bridge remains unresolved

The directed secants are legitimate finite economic comparisons.

They are not a gradient certificate.

Three of the four adjacent certified secant intervals contain zero, and the artifact explicitly sets

`rigorous_stopped_gradient_error_established = false`.

Thus the paper still lacks a verified quantitative bridge between:

- the differentiable proposal objective used to drive optimization, and
- the exact stopped continuous objective used for certification.

For a paper whose interpretation depends on optimizer geometry and representation, this gap remains fundamental.

Either instantiate the perturbation theorem with certified constants along the relevant trajectory, or replace the gradient-dependent methodological claim with a genuinely certified derivative-free refinement argument.

### R25-SP-F8 — The main prospective online study does not exercise rollback

The online implementation is now correctly coupled.

But every one of the 24 prospective block decisions is an acceptance.

Hence the principal safety mechanism is still untested in the main experiment:

- no harmful candidate is rejected;
- no optimizer moments are restored after an actual adverse candidate;
- no rate-halving path is followed because of rejection.

The integration protocol prescribes a deliberately adverse post-observation stress experiment starting at rate 20.48. That is a reasonable engineering test, but at the reviewed head it is still a protocol, not a result.

Even once executed, it should be labeled correctly: it is a post-selection rollback stress test, not held-out evidence about how frequently rollback is needed under the prospectively selected method.

### R25-SP-F9 — Certificate tightening is not policy-payoff improvement

The full-state continuation correctly records `payoff_improvement_proved = false`.

That qualification must survive into the integrated manuscript.

A lower regret upper bound on a new network, even under a common fine cover, is not the same result as a certified lower/upper comparison proving that the new policy's economic payoff is higher over the full domain.

The current evidence supports “tighter certified regret upper bound.”

It does not support “better policy” without the separate payoff comparison prescribed by the protocol.

### R25-SP-F10 — Verification dominates total cost, and the scaling story is therefore incomplete

The held-out checker costs about 13.8–13.9 seconds per method, while proposal generation is mostly below 2.2 seconds.

The stochastic neural certificates cost more than 42 seconds each at the required fine cover.

This is not an objection to certified numerics. It is an objection to incomplete efficiency rhetoric.

The relevant computational object is:

[
	ext{proposal}+	ext{geometry}+	ext{tuning}+	ext{certification}+	ext{rollback bookkeeping}+	ext{dual/reference infrastructure}.
]

The paper needs complexity and scaling evidence for that whole pipeline.

At present, the dominant cost is independent certification, not the neural optimizer.

### R25-SP-F11 — The empirical robustness basis is still narrow for a parameterization-sensitive optimizer

The central held-out study uses two seeds and two proposal quadrature rules.

That is adequate for a deterministic debugging comparison. It is thin evidence for a method known from the repository's own experiments to be strongly parameterization dependent.

Neural L-BFGS-B remains unstable across initializations, and the moving arm itself shows substantial geometry/cap sensitivity.

A top numerical paper should separate:

- initialization robustness;
- hyperparameter robustness;
- representation robustness;
- quadrature/proposal robustness;
- checker robustness.

Two seeds do not establish those separately.

### R25-SP-F12 — The theory remains explanatory rather than performance-guaranteeing

R25's analytical direction is useful:

- moving-transport identities;
- verified finite-poll improvement/termination;
- derivative error accounting;
- exact regret identity for the manufactured reference.

But at the reviewed head the integration protocol still lists part of this theory as work to be added, and the executed evidence does not convert it into a convergence/complexity result for the original problem.

The key theorem a numerical-method paper still lacks is something of the form:

> under stated approximation, optimization, and verification assumptions, the certified NBO iteration reaches an (arepsilon)-accurate original-state policy with explicit work or convergence guarantees.

Nothing in R25 establishes that.

---

## 5. Additional technical findings

### R25-SP-T1 — The revision index is stale by two full revision generations

`REVISION_INDEX.md` still declares R23 as the current review object.

This is a reproducibility and referee-copy defect. The branch cannot be called sealed or self-describing until the index points to the actual review object.

### R25-SP-T2 — The branch chronology is scientifically clean but publication-incomplete

The R25 sequence is unusually good in one respect:

- prospective protocol;
- reference/full-state protocols;
- implementation;
- CI execution;
- frozen results;
- later integration protocol.

That chronology should be preserved.

But the final integration step has not yet been executed at the reviewed head. The manuscript should not cite post-integration claims until the corresponding source/result commits exist.

### R25-SP-T3 — Report effective, not merely nominal, moving-step sizes

Because the trust cap is frequently active, tables should include:

- fraction of capped steps;
- min/median/95th percentile trust scale;
- min/median/95th percentile effective output displacement;
- carrier/economic mismatch;
- dropped nonlinear remainder norm.

Without these, the moving-arm rate comparison is not interpretable.

### R25-SP-T4 — Recenter or certify the moving carrier mismatch

The current algorithm evaluates (J) at a carrier state whose actual outputs may differ materially from the economic quotient (z).

A future mechanism experiment should do one of:

1. recenter (z) to the realized carrier output after each parameter step;
2. solve a local inverse problem keeping carrier outputs aligned with (z);
3. certify a uniform mismatch tolerance under which the Jacobian transport interpretation remains valid.

Logging the mismatch is useful, but logging alone does not make the control faithful.

### R25-SP-T5 — The stochastic direct comparator is intentionally advantaged and must remain labeled as such

The direct control knows the exact portfolio formula and approximates only the (1/x) component.

This is acceptable for a verifier benchmark.

It is not an apples-to-apples discovery benchmark.

The final manuscript should avoid both opposite errors:

- do not claim neural inferiority in general from this constructed control;
- do not claim neural efficiency from a benchmark where the direct method uses the known solution structure.

### R25-SP-T6 — The all-start-time full-state envelope needs a self-contained proof in the paper/supplement

The R25 postprocessor forms a discounted suffix envelope from slabwise nonnegative residual bounds and states that the maximum within a slab is attained at a boundary.

That appears to be a reasonable tightening over the inherited cruder `all_initial_times_regret_upper`, but the integrated manuscript should prove the exact monotonicity argument and explain why the postprocessed envelope is the reported all-start-time number rather than the larger legacy field in the underlying certificate.

A referee should not have to infer that logic from `full_state.py`.

### R25-SP-T7 — The acceptance test is conservative but should be interpreted as a deployment test

The strict condition

[
L_{mathrm{candidate}} > U_{mathrm{incumbent}}
]

is a valid certified improvement rule.

It is deliberately stronger than “candidate has lower regret upper bound.”

The paper should keep those two notions separate. The full-state continuation uses regret-bound improvement, whereas the financed online study uses payoff-interval dominance. These are distinct operators with distinct guarantees.

### R25-SP-T8 — Do not use aggregate run counts as pseudo-replication

Tuning runs, held-out runs, verification cells, checkpoint audits, stochastic covers, and full-state slabs are not independent replications of one statistical effect.

The final manuscript should report them as computational coverage, not as a sample size.

---

## 6. What a materially reconsiderable next revision would need

### N1 — Deliver an actual integrated R25/R26 submission object

At minimum:

- manuscript source and PDF;
- supplement source and PDF;
- response source and PDF;
- complete source/result manifest;
- current revision index;
- independent audit output;
- executed rollback stress result;
- sealed referee-copy branch.

### N2 — Produce orders-of-magnitude progress on the original current-state full-domain target

Moving from 7.20 to 7.18 is scientifically useful as a diagnostic, but it does not alter the publication-level conclusion.

The original (0.01) target needs either:

- a genuinely successful numerical result, or
- an explicit narrowing/reformulation of the title-level claim.

### N3 — Run a faithful neural-geometry mechanism control

A convincing control should preserve alignment between economic coordinates and the carrier and should either retain or rigorously bound nonlinear output transport.

The current heavily capped, drifting carrier is not enough to identify the neural mechanism.

### N4 — Close the proposal-gradient/certificate gap

Either:

- instantiate the stopped-gradient perturbation bound numerically along the actual trajectory, or
- use a certified derivative-free refinement scheme whose correctness does not depend on an uncontrolled surrogate gradient.

### N5 — Add an unknown-solution stochastic benchmark

Keep the current manufactured benchmark as a verifier test.

Add a second stochastic stopped problem where:

- the exact value/policy is not supplied to training;
- the favorable exact decoder is unavailable;
- a high-accuracy classical or validated reference is obtained independently;
- neural and direct methods are compared on the same information set.

### N6 — Exercise rejection prospectively

The adverse rollback stress is worth executing.

Beyond that, a stronger result would define a prospective regime in which harmful proposals occur naturally and show that certificate-coupled rollback improves the realized trajectory relative to the uncoupled optimizer.

### N7 — Broaden robustness and scaling evidence

At minimum, report more initializations and a structured perturbation study across:

- network chart;
- optimizer;
- rate/trust cap;
- quadrature;
- state-domain size;
- verification cover;
- dimension.

The paper needs to show where the neural method becomes necessary or beneficial, not merely that it is one feasible parameterization.

---

## 7. Recommendation

**Reject in the present form.**

R25 is scientifically better than R24. The expanded tuning, online certification architecture, stochastic whole-state verifier test, and original-state continuation are all constructive advances.

But the strongest evidence still points away from the paper's central numerical-method claim.

- The original full-domain target remains missed by about 718×.
- The original continuation improves the certificate by only about 0.258% and then stalls.
- Direct L-BFGS-B remains the best tested held-out accuracy/work method.
- The moving historical-transport control is heavily capped and develops substantial carrier/economic-coordinate mismatch, so it does not cleanly identify a uniquely neural mechanism.
- The manufactured stochastic benchmark uses a known witness in training and primarily validates the verifier.
- The exact stopped-gradient bridge remains unresolved.
- The prospective online experiment never exercises rollback.
- The reviewed head is an integration protocol rather than a completed R25 manuscript.

The repository is becoming unusually auditable, which is valuable. The remaining problem is not auditability. It is that the audited numerical evidence does not yet demonstrate the performance, convergence, scaling, or mechanism advantage required for an Econometrica-level neural numerical-method contribution.

---

## 8. Source map inspected

### R25 protocols

- `revisions/2026-09-23-r25/PROTOCOL.md`
- `revisions/2026-09-23-r25/REFERENCE_PROTOCOL.md`
- `revisions/2026-09-23-r25/FULL_STATE_PROTOCOL.md`
- `revisions/2026-09-23-r25/INTEGRATION_PROTOCOL.md`

### R25 execution / replication

- `revisions/2026-09-23-r25/replication/study.py`
- `revisions/2026-09-23-r25/replication/full_state.py`
- `revisions/2026-09-23-r25/replication/stochastic_reference.py`
- `revisions/2026-09-23-r25/replication/secants.py`

### R25 primary results

- `revisions/2026-09-23-r25/results/tuning_selection.json`
- `revisions/2026-09-23-r25/results/tuning_ledger.json`
- `revisions/2026-09-23-r25/results/heldout_ledger.json`
- `revisions/2026-09-23-r25/results/online_ledger.json`
- `revisions/2026-09-23-r25/results/full_state/summary.json`
- `revisions/2026-09-23-r25/results/stochastic_reference_summary.json`
- `revisions/2026-09-23-r25/results/secants.json`
- `revisions/2026-09-23-r25/results/EXECUTION_COMPLETENESS.json`

### Moving-transport diagnostics audited

- all four held-out `moving_adam/history.json` files for seeds 25101/25102 and quadrature orders (8,16)/(12,24);
- tuning history for seed 25001 at rates 0.32, 1.28, 5.12, 20.48.

### Packaging / manuscript state

- root `ECTA.tex`
- root `supp.tex`
- `REVISION_INDEX.md`
- R24 review baseline and R24 publication artifacts.

