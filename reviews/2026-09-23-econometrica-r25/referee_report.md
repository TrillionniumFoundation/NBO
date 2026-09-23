# External Referee Report — Neural Bellman Operators (R25 revision package)

**Venue standard:** Econometrica-level numerical / computational methodology  
**Recommendation:** **Reject in the present form / not review-ready as a completed R25 manuscript.**  
**Review date:** 2026-09-23  
**Reviewed development branch:** revision/econometrica-r25-integrated-response-2026-09-23  
**Reviewed head commit:** cbb4c4826978fc228ad89f693eb369b75cb89fd6  
**Latest completed manuscript in the branch:** R24, sealed manuscript commit 14ce582e188f437cc8d99f310edd4f06515936a4  
**Review branch:** review/econometrica-r25-numerical-methods-2026-09-23-cbb4c48

---

## 1. Executive assessment

R25 contains substantial new numerical work. It is not a cosmetic iteration on R24.

The expanded first-order calibration is now prospectively bracketed. A moving historical-transport direct arm is implemented. The acceptance rule is coupled online to optimization rather than replayed only after the fact. A stronger stochastic stopped benchmark with two independent Brownian shocks and an unspanned state variable is executed and globally interval-certified. The original current-state full-domain actor/witness problem is also continued with an independent MPFR audit. These are meaningful responses to several R24 requests.

However, the R25 evidence still does not establish the title-level numerical-method claim at an Econometrica standard, and the branch is not yet a completed paper revision.

There are two separate problems.

First, the branch head is an integration protocol, not a completed integrated manuscript. The protocol explicitly requires ECTA_R25, SUPP_R25, RESPONSE_R25, a current revision index, an independent audit, a rollback stress execution, compiled PDFs, publication hashes, and a sealed referee-copy branch. None of those R25 publication roots is present at the reviewed head. ECTA_R25.tex, SUPP_R25.tex, RESPONSE_R25.tex and the expected r25/paper sources are absent. REVISION_INDEX.md still declares R23 as the current review object. The integration protocol is one commit ahead of its parent and has not been executed. Thus there is no self-contained R25 manuscript for a referee to accept or reject on the merits as a finished submission.

Second, even treating the R25 science package as the intended substantive revision, the central numerical conclusion remains adverse to the paper's strongest claim. The original full-state 0.01 target is still missed by roughly three orders of magnitude. The retained fine all-start-time certificate is 7.181834580823298, about 718 times the target. The new continuation improves the certificate only modestly and then stalls. No policy-specific payoff improvement is proved for that original full-state actor.

The central held-out optimizer comparison also remains unfavorable to a neural-efficiency claim. Across both held-out seeds and both quadrature orders, direct L-BFGS-B has worst regret upper bound 0.0019235324, mean generation time about 0.403 seconds, and mean 113.5 gradient calls. Neural Adam has worst regret upper bound 0.0019263760, about 1.629 seconds of generation, and 400 calls. The new moving historical-transport arm has worst regret upper bound 0.0019278023, about 2.163 seconds of generation, and 400 calls. Neural L-BFGS-B remains unstable across seeds, with worst regret about 0.00960835. Thus the new mechanism experiment does not move the efficient frontier in favor of the neural representation.

The new stochastic reference is a useful verifier stress test, but it is deliberately manufactured from a known value/witness and does not demonstrate numerical discovery of an unknown Bellman solution. Both neural actors require the finest 262,144-cell cover to certify below 0.001, with bounds about 0.0007663 and 0.0006855, while the direct degree-eight control certifies at about 0.0001935 already on the coarsest 4,096-cell cover and is generated essentially instantaneously. This experiment validates the certification infrastructure much more strongly than it validates neural numerical efficiency.

The new online acceptance experiment is now genuinely interleaved with optimization, which is a real advance. But all 24 prospective block decisions are acceptances. Therefore the main experiment still does not test the rollback branch of the algorithm. The reviewed head contains only a protocol for a deliberately adverse rollback stress test; that stress test has not yet been executed.

Finally, the original stopped-objective gradient bridge remains unresolved. The new directed secants are legitimate finite payoff comparisons, but three of four adjacent secant intervals contain zero and the artifact explicitly records that no rigorous pointwise stopped-gradient error certificate is established.

In short: R25 improves calibration, mechanism isolation, online coupling, and verifier scope. It does not solve the original full-domain problem, it does not establish a neural accuracy/work advantage, it does not close the stopped-gradient gap, and it is not yet packaged as a completed R25 manuscript.

---

## 2. What R25 genuinely fixes relative to R24

### 2.1 First-order tuning is no longer censored at the grid boundary

This is the cleanest resolved R24 objection.

The prospective R25 grid expands rates from the earlier narrow family to

0.005, 0.02, 0.08, 0.32, 1.28, 5.12, 20.48.

The selected rates are now interior for all six first-order arms:

- neural: 0.08;
- direct: 0.32;
- diagonal: 0.32;
- tangent: 0.32;
- whitening: 0.08;
- moving historical transport: 0.32.

Larger tested rates yield lower certified tuning scores. The previous R24 statement that all methods chose the largest rate is therefore no longer applicable.

This substantially resolves R24-F2 / T1 / N1.

### 2.2 A prospectively specified moving historical-transport direct arm now exists

R25 no longer compares neural Adam only against frozen initial tangent/whitening charts.

The new moving arm:

- recomputes the quotient Jacobian;
- pulls the current direct-output gradient back through the carrier;
- maintains parameter-space Adam first and second moments;
- pushes the direction forward through the current Jacobian;
- charges the 355-parameter carrier;
- uses a prespecified isotropic regularizer and step cap.

This is a materially better mechanism control than the R24 static tangent experiment.

It partially addresses R24-F4 / T3 / N2.

### 2.3 The acceptance rule is now coupled online

The R25 online study no longer merely replays a deployment filter after an independent optimizer trajectory.

Each 100-call block is followed synchronously by certification. Rejection would restore economic coordinates, network/carrier parameters, and optimizer moments, and reduce the subsequent step size.

That is the correct architecture for testing whether certification can actually influence the optimization state.

This materially advances R24-F6.

### 2.4 The stronger stochastic benchmark is scientifically more relevant than the old deterministic reference

The manufactured benchmark contains:

- two independent Brownian shocks;
- an unspanned productivity factor;
- first-exit / terminal stopping;
- current-state controls;
- no exact financing decoder;
- complete state-time certification by directed arithmetic.

This is much closer to the type of stochastic verification problem requested in R24-F9 / N5 / N7.

### 2.5 The original current-state full-domain problem is explicitly revisited

R25 does not substitute the manufactured benchmark for the original economy.

It restarts from the R22 actor/witness, runs certificate-coupled L-BFGS-B proposal blocks, independently audits candidates, and rechecks both the untouched and retained networks on a finer fixed cover with zero skipped cells.

This is the correct direction for addressing R24-F1 / N4.

---

## 3. Decisive numerical facts from R25

### 3.1 Held-out optimizer frontier

Aggregating the four held-out cells defined by two seeds times two proposal quadrature orders:

| Method | Worst regret upper | Mean calls | Mean generation sec. | Mean checker sec. |
|---|---:|---:|---:|---:|
| neural Adam | 0.0019263760 | 400.0 | 1.6286 | 13.8777 |
| direct Adam | 0.0019366958 | 400.0 | 1.4789 | 13.9310 |
| diagonal Adam | 0.0019328550 | 400.0 | 1.4849 | 13.9298 |
| tangent Adam | 0.0020834795 | 400.0 | 1.4924 | 13.8593 |
| whitening Adam | 0.0179100178 | 400.0 | 1.4708 | 13.9013 |
| moving historical transport Adam | 0.0019278023 | 400.0 | 2.1632 | 13.8617 |
| neural L-BFGS-B | 0.0096083472 | 242.5 | 0.9445 | 13.8309 |
| **direct L-BFGS-B** | **0.0019235324** | **113.5** | **0.4029** | 13.8126 |

Direct L-BFGS-B remains the most robust point on the observed accuracy/work frontier.

The new moving arm does not beat neural Adam on worst regret and is slower in proposal generation. It is useful as a mechanism control, but it does not provide evidence that historical neural transport yields a superior solver.

### 3.2 Original full-state target

The original publication target remains 0.01.

On the fine fixed cover:

- untouched warm start, all-start envelope: 7.2004087464242685;
- retained R25 actor, all-start envelope: 7.181834580823298.

The absolute improvement is about 0.01857, roughly 0.26 percent of the bound.

The target remains missed by approximately a factor of 718.

The continuation behavior is also revealing:

- block 1 uses 82 gradient calls and improves the coarse certificate from 7.2414624431 to 7.2116293096;
- blocks 2, 3 and 4 each terminate after one gradient call with zero accepted optimizer iterations and no further certificate improvement.

This looks like rapid saturation of the current proposal/checker combination, not an orders-of-magnitude breakthrough.

The artifact explicitly records payoff_improvement_proved = false.

### 3.3 Stochastic manufactured reference

The two neural actors achieve complete state-time certification below the reference target only on the finest cover:

- seed 25201: regret upper 0.0007663119;
- seed 25202: regret upper 0.0006855391.

The direct polynomial control certifies:

- regret upper 0.0001934982

already on the coarsest cover.

The neural fits use 2,500 optimization calls each and roughly 1.5 seconds of generation. Their finest verification requires about 42 seconds cumulatively. The direct control is generated in about 0.0015 seconds and verifies on the coarse cover in roughly 0.03 seconds.

This is strong evidence that the verifier can certify a nonreplicable stochastic stopped control problem. It is not evidence of a neural efficiency advantage.

### 3.4 Online coupled acceptance

For both held-out seeds and each of neural, direct and moving transport, all four 100-call blocks are accepted.

Thus:

- 24 accepted blocks;
- 0 rejected blocks;
- no rollback branch exercised in the main prospective online study.

The online architecture is now correct, but the central safety mechanism is not behaviorally stress-tested by these runs.

### 3.5 Directed stopped-payoff secants

For the fixed neural-Adam to direct-L-BFGS-B path, the four adjacent certified secant intervals are approximately:

1. [5.33e-6, 8.38e-6];
2. [-3.34e-7, 2.72e-6];
3. [-1.02e-6, 2.03e-6];
4. [-1.37e-6, 1.68e-6].

Only the first interval has a sign separated from zero.

The artifact correctly states that these are finite economic payoff comparisons, not a pointwise stopped-gradient certificate, and records rigorous_stopped_gradient_error_established = false.

---

## 4. Blocking findings

### R25-F1 — The reviewed branch is not a completed R25 paper revision

This is a threshold problem.

The head commit is an integration protocol. That protocol itself says the following deliverables still need to be produced:

- a complete Econometrica-style R25 manuscript;
- supplement;
- response;
- finding-by-finding disposition;
- independent evidence audit;
- rollback stress execution;
- updated revision index;
- compiled and inspected PDFs;
- publication manifests / hashes;
- sealed referee-copy branch.

At the reviewed head:

- ECTA_R25.tex is absent;
- SUPP_R25.tex is absent;
- RESPONSE_R25.tex is absent;
- r25/paper/introduction.tex is absent;
- r25/paper/results.tex is absent;
- r25/paper/conclusion.tex is absent;
- r25/paper/response.tex is absent;
- r25/paper/supplement.tex is absent.

The formal manuscript remains R24.

A referee cannot evaluate whether the authors have stated the new evidence with correct scope, whether theorems match the executed code, whether adverse outcomes remain prominent, or whether conclusions overclaim, because the R25 paper text does not yet exist.

This alone makes the present branch not review-ready.

### R25-F2 — The original full-domain numerical problem remains essentially unsolved

The central R24 publication barrier was not the absence of any numerical progress. It was the enormous gap between the original full-domain objective and the available certificate.

R25 moves the fine all-start-time bound from about 7.2004 to 7.1818.

That is directionally favorable but quantitatively tiny relative to the target 0.01.

The remaining factor is about 718.

Moreover, after the first refinement block, the optimizer/checker loop stalls immediately for the next three blocks. There is no evidence in the present package of a mechanism capable of closing the remaining orders of magnitude.

This is still the main substantive barrier to a title-level claim about solving the original Bellman problem.

### R25-F3 — Direct L-BFGS-B remains the strongest tested accuracy/work method

The R25 tuning repair makes this conclusion stronger, not weaker, because the first-order arms are now prospectively calibrated over a wider range.

Direct L-BFGS-B remains:

- more accurate in worst-case regret than neural Adam;
- more accurate than the moving historical-transport arm;
- far cheaper in gradient calls;
- faster in proposal generation;
- stable across both seeds and both quadrature rules.

Neural L-BFGS-B is still parameterization-sensitive, with one held-out seed near the frontier and another failing by a large margin.

The R25 package therefore still lacks a regime in the original central study where the neural representation improves the observed accuracy/work frontier.

For a paper centered on a neural numerical mechanism, that is a core issue, not a presentation issue.

### R25-F4 — The new moving-transport control is valuable, but its result does not identify a neural advantage

The moving arm is the right experiment to add.

Its empirical outcome, however, is not favorable to the interpretation that neural parameterization contributes an efficiency gain beyond induced geometry.

Its worst regret is about 0.00192780, close to but slightly worse than neural Adam's 0.00192638, while generation is slower.

The protocol also explicitly acknowledges that the moving arm:

- retains a 355-parameter carrier;
- is not an autonomous 47-memory-coordinate optimizer;
- omits the finite-step nonlinear output remainder.

Thus the experiment shows that a substantial portion of the neural historical transport can be emulated directly, but it does not isolate an irreducible neural contribution.

A future paper should report effective displacement caps and clipping frequency. The fact that moving-arm tuning scores at 1.28, 5.12 and 20.48 are numerically identical is consistent with rate information being partly erased by the fixed step cap. Calling the nominal learning-rate optimum fully bracketed is formally defensible because 0.32 has a better certified score, but mechanism interpretation requires the effective-step distribution, not only nominal rates.

### R25-F5 — The stronger stochastic reference validates the verifier more than the solver

The new reference solves an important R24 weakness: it is genuinely stochastic, stopped, and nonreplicable.

But the benchmark is deliberately manufactured from a known smooth value and exact optimal actions. Neural training minimizes a known-witness Hamiltonian deficit. The direct control explicitly approximates the known 1/x structure and uses the exact portfolio formula.

That design is perfectly legitimate for verification testing.

It does not demonstrate that NBO discovers an unknown value/policy pair in a difficult stochastic economy.

The direct control is also dramatically stronger on this benchmark.

Therefore this experiment should be presented as:

- a global interval-verification stress test;
- a demonstration that frozen neural actors can be certified on a nonreplicable stopped problem;
- evidence about approximation and verifier scaling.

It should not be presented as a competitive end-to-end neural Bellman solution of a previously unknown stochastic control problem.

### R25-F6 — The original stopped-gradient bridge remains unresolved

R25 adds a legitimate derivative-free diagnostic using certified payoff secants.

That is useful.

But it does not instantiate the continuous stopped-gradient perturbation bound along the optimizer trajectory. The artifact explicitly says so.

Three of four adjacent secant intervals contain zero, and the intervals are finite differences along one fixed path between two endpoints. They do not identify the full gradient vector field that drove the optimizer.

Therefore the methodological question raised in R24-F5 / N3 remains open:

How robust are optimizer comparisons to error between the discretized proposal objective's gradient and the exact stopped continuous objective?

Until that is bounded or bypassed by a genuinely derivative-free certified refinement scheme, claims about optimizer geometry remain partly surrogate-specific.

### R25-F7 — The online acceptance architecture is now real, but the main experiment never exercises rejection

All 24 blocks are accepted.

This shows that certification can be inserted into the optimization loop at manageable cost.

It does not show:

- correct restoration after a failed candidate in the main prospective study;
- behavior after Adam moments are rolled back;
- adaptation after the prescribed rate halving;
- whether the coupled operator avoids harmful proposal steps;
- whether repeated rejections induce stable termination.

The head commit contains a sensible adverse-rate rollback stress protocol. But that protocol is not executed at the reviewed commit.

The paper therefore cannot yet cite an observed rollback as evidence.

### R25-F8 — The original full-state continuation improves a certificate, not policy payoff

The full-state protocol correctly distinguishes regret-bound improvement from policy-specific payoff improvement.

The execution follows that rule and records payoff_improvement_proved = false.

That distinction matters.

A smaller upper bound can arise from a changed candidate, a changed proof tightness, or both. The fine comparison reduces some ambiguity by checking both networks on the same cover, but no lower/upper direct payoff comparison establishes that the R25 policy itself is economically better over the full state-time domain.

The next revision should not translate certificate tightening into welfare improvement without the separate comparison the protocol itself requires.

### R25-F9 — Verification cost still dominates end-to-end runtime

In the held-out study, proposal generation is typically below a few seconds. A single certification is roughly 14 seconds.

This is acceptable for validated numerics, but it changes what the relevant efficiency metric is.

The numerical method is not just the proposal optimizer.

For deployment claims, the relevant cost includes:

- tuning;
- proposal generation;
- repeated certification;
- preprocessing / geometry construction;
- rollback bookkeeping;
- dual or upper-bound infrastructure.

The paper should not use sub-second direct versus one-to-two-second neural generation gaps as if they were the entire method, but it also should not ignore that direct L-BFGS-B achieves better proposal quality using far fewer calls before the same expensive checker is applied.

### R25-F10 — The R25 science still does not establish high-dimensional scaling of the certified method

The stronger stochastic reference is three-dimensional in state-time coordinates. The original held-out policy class is low-dimensional after quotienting. The full-state certificate is computationally expensive but not a high-dimensional scaling study.

The old broad NBO manuscript makes strong claims about high-dimensional tractability and polynomial scaling. The R24/R25 validated-numerics program is much narrower and more careful.

A completed R25 manuscript must decide which evidentiary standard it is claiming:

- a certified numerical method for this stopped economy and closely related low-dimensional problems; or
- a scalable high-dimensional Bellman solver.

The current R25 evidence supports the former much more directly than the latter.

### R25-F11 — The current repository entry point is still stale

REVISION_INDEX.md still says:

Current review object: R23.

This was already identified as R24-T5.

The R25 protocol explicitly says the index will be updated with the old version archived byte-for-byte. That has not happened.

At R25 this is no longer a small cosmetic issue. It is evidence that the integration/publication stage remains unfinished.

### R25-F12 — The integration protocol is post-observation and must not be mixed with prospective R25 science

The integration protocol is admirably explicit that it was written after observing:

- all six interior rate selections;
- all 24 main online acceptances;
- the two sub-0.001 stochastic neural certificates;
- the 7.18183458 full-state bound.

Any subsequent audit, rollback stress, theorem polishing or table reconstruction may be useful, but it is not part of the original prospective R25 scientific prediction.

A final response should preserve this distinction very clearly.

In particular, the deliberately adverse 20.48 rollback stress test should be labeled an engineering stress diagnostic, not a new held-out optimizer result.

---

## 5. Status of the previous R24 requests

### N1 — Bracket first-order hyperparameter performance

**Substantially resolved.**

The expanded rate grid is prospective and selections are interior.

The moving arm's step cap should still be reported in effective-step terms because large nominal rates appear to saturate.

### N2 — Implement a direct method following measured neural geometry

**Partially resolved.**

The moving historical-transport arm is a serious improvement over static tangent charts.

But it keeps a neural-style carrier, omits the finite-step nonlinear remainder, and does not outperform neural Adam or direct L-BFGS-B. It therefore clarifies mechanism without establishing a neural advantage.

### N3 — Certify or tightly control proposal-gradient error

**Unresolved.**

The secant diagnostic is useful but is explicitly not a stopped-gradient certificate.

### N4 — Produce a successful current-state full-domain result

**Unresolved by a very large margin.**

The fine all-start-time bound is about 7.1818 against target 0.01.

### N5 — Execute a nonreplicable stochastic problem

**Partially resolved.**

The manufactured benchmark is genuinely stochastic, stopped and unspanned.

However, it is an oracle-witness manufactured problem, not an unknown-value end-to-end Bellman discovery problem.

### N6 — Add restart/state-time coverage

**Improved only in the auxiliary benchmark.**

The stochastic reference certifies the complete state-time box.

The original consumption-portfolio economy still lacks a successful global current-state numerical result.

### N7 — Use a stronger known-solution benchmark

**Substantially improved as a verifier benchmark.**

The new reference is far stronger than the prior deterministic toy problem.

Its role must still be described narrowly because the witness is built into training.

### N8 — Decide what the paper is actually about

**Unresolved.**

There is no R25 manuscript text yet, so the central framing question has not been answered.

---

## 6. Required changes for a materially reviewable next submission

A future referee copy should not merely add another layer of archived experiments. It should deliver a coherent paper with a claim matched to the strongest established evidence.

At minimum:

1. Produce the actual R25 manuscript, supplement and response, with the R25 evidence integrated and all claims scoped to what was executed.
2. Update the root revision index and publish a sealed referee-copy branch with reproducible manifests.
3. Keep the original 0.01 full-domain target visible and explain that 7.1818 remains far from it.
4. Either achieve orders-of-magnitude progress on the original current-state full-domain certificate, or narrow the title-level methodological claim to the certified regional / verification results actually demonstrated.
5. Treat direct L-BFGS-B as a first-class baseline and organize the numerical discussion around the observed accuracy/work frontier rather than around the neural method by construction.
6. Report moving-arm clipping frequency, effective step norms, carrier costs and memory costs so the geometry experiment is interpretable.
7. Close the stopped-gradient issue with an instantiated rigorous bound or a certified derivative-free optimization argument that does not depend on the unverified gradient.
8. Execute the already frozen rollback stress protocol and report every rejection/restore hash without presenting it as held-out scientific evidence.
9. Add a benchmark in which the value/policy is not supplied to the training objective as an oracle witness, while retaining an independently accurate external reference for evaluation.
10. Separate proposal-generation cost from certification and total end-to-end cost throughout.

---

## 7. Recommendation

**Reject in the present form / return as not yet review-ready.**

R25 is scientifically more serious than R24 in several dimensions. The tuning design is repaired. The mechanism experiment is better. The online architecture is genuinely coupled. The stochastic verifier test is much stronger. The full-state problem is revisited rather than avoided.

But the central numerical facts remain unfavorable to the strongest interpretation of the paper:

- the original full-domain target is still missed by about a factor of 718;
- the new full-state continuation quickly stalls;
- direct L-BFGS-B remains the strongest tested accuracy/work method;
- the moving neural-geometry control does not improve the frontier;
- the manufactured stochastic benchmark is oracle-witness based and is dominated by the direct control;
- the stopped-gradient bridge remains unproved;
- the online main study never rejects a block;
- the planned rollback stress and independent audit are not yet executed;
- and there is no completed R25 manuscript at all.

A future submission could be materially stronger if it converts this large body of careful numerical infrastructure into one coherent theorem/evidence story. At present, the repository contains an R25 research program and protocol, not a finished Econometrica-level R25 paper.

---

## 8. Source map inspected

### Reviewed R25 branch and protocol

- revisions/2026-09-23-r25/PROTOCOL.md
- revisions/2026-09-23-r25/INTEGRATION_PROTOCOL.md
- revisions/2026-09-23-r25/REFERENCE_PROTOCOL.md
- revisions/2026-09-23-r25/FULL_STATE_PROTOCOL.md
- revisions/2026-09-23-r25/replication/study.py
- revisions/2026-09-23-r25/replication/stochastic_reference.py
- revisions/2026-09-23-r25/replication/secants.py
- revisions/2026-09-23-r25/replication/full_state.py
- revisions/2026-09-23-r25/results/EXECUTION_COMPLETENESS.json
- revisions/2026-09-23-r25/results/tuning_selection.json
- revisions/2026-09-23-r25/results/heldout_ledger.json
- revisions/2026-09-23-r25/results/online_ledger.json
- revisions/2026-09-23-r25/results/stochastic_reference_summary.json
- revisions/2026-09-23-r25/results/secants.json
- revisions/2026-09-23-r25/results/full_state/summary.json

### Previous R24 referee object

- ECTA_R24.tex
- SUPP_R24.tex
- RESPONSE_R24.tex
- R24_REVIEW.md
- reviews/2026-09-23-econometrica-r24/referee_report.md
- REVISION_INDEX.md

### Additional repository cross-check

The branch head cbb4c4826978fc228ad89f693eb369b75cb89fd6 is exactly one commit ahead of integration parent c78d934c0b3b8d346a40c7ddcaf415e167462265, and that commit only adds INTEGRATION_PROTOCOL.md. No completed integration/publication execution is present at the reviewed head.
