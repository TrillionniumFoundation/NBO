# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r11-evidence-2026-10-04`  
**Pinned evidence commit:** `840565f451be6103aeb325a8fc548a57507a8fb2`  
**Pinned evidence tree:** `ddc50a0c11429a6400dbc7f94c5d5f532e6b4065`  
**Pinned source commit:** `55691da9dc000443bf9c55caf3a58d507b2072d3`  
**Pinned manuscript blob:** `2b2a36d07e368f92c29868ff7afcf98ad8f24d89` (`ECTA.tex`)  
**Pinned supplement blob:** `bb3e1ea468d8b109e186b127e4f499a0e229385b` (`supp.tex`)  
**Pinned response blob:** `eb89d6f7afa0ba486f8dd8bfe3302ecf4361eba3` (`revisions/2026-10-04-r11/response.tex`)  
**Report date:** 4 October 2026  
**Recommendation:** **Reject in the present form; encourage a substantially focused new submission rather than another ordinary revision of the current manuscript.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R11 is a substantial and technically serious response to the R10 report. The revision no longer relies only on a schedule-centred architectural tube to characterize a trained policy. It introduces a policy-specific post-training certificate for an explicitly defined innovation-driven sampled controller. The certificate combines an exact payoff-difference identity, an explicit continuous-time transfer bound, a Gaussian clipping-tail account, finite-family empirical Bernstein inference, and the inherited deterministic regret bound for the analytical schedule. The endpoint changes with the deployed policy and can distinguish a useful policy from a poor policy inside the same action tube.

The numerical design is also materially stronger. The evidence contains ten training seeds in each of dimensions 10, 20, and 50; NBO, direct-policy, and affine methods; 8,192-path and 1,024-cell primary evaluations; checkpoint frontiers; radius, architecture, initial-state, and heavy-tail stresses; tuned critic-greedy variants; adverse policies; raw arrays; fitted weights; exact-source manifests; and a remote execution ledger. The primary record reports positive simultaneous lower improvement endpoints for all 30 NBO policies. I found no immediate algebraic contradiction in the stated transfer, clipping, and concentration chain, and the repository’s internal audit is unusually complete.

These are major improvements. In particular, R11 resolves the most important logical objection to R10: the strongest reported post-training statement now depends on the fitted policy rather than assigning the same result to every member of an architectural tube.

The remaining obstacle is no longer basic correctness or provenance. It is whether the paper establishes a sufficiently distinct and economically consequential **Neural Bellman Operators** contribution. On the evidence supplied, it does not.

The same policy-specific certificate is method-agnostic. It verifies direct policy optimization as readily as it verifies NBO. In every reported dimension, direct policy optimization also meets the declared target in all ten seeds, uses the same deployed actor architecture, requires no learned critic, and has lower recorded training and verification cost. NBO’s aggregate mean advantage over direct policy is only \(7.6\times10^{-5}\), \(8.4\times10^{-5}\), and \(1.1\times10^{-4}\) utility units in dimensions 10, 20, and 50. The paper supplies no direct paired confidence or certification statement for these NBO-minus-direct-policy differences. Separate positive lower bounds relative to the schedule do not establish an ordering between the two methods.

Moreover, the policy-specific improvement tightens the inherited anchor regret bound only modestly. Using the least favorable NBO lower endpoint in each dimension, the tightening is approximately 6.3%, 2.8%, and 3.2% of the schedule’s deterministic regret bound. The resulting regret upper endpoints remain approximately 0.0176, 0.0248, and 0.0267. Thus the new result certifies a small improvement over a feasible schedule; it does not demonstrate that NBO approximately solves the high-dimensional control problem.

The economic application remains stylized and pointwise. At the primary initial state \(y=0\), the least favorable certified NBO improvements correspond to externally financed flow-equivalent changes of only about 0.121%, 0.073%, and 0.089%. Under many shifted or dispersed initial states, the lower endpoint becomes negative, and at a positive mean shift the measured gain itself is negative in dimensions 10 and 20. The controller additionally assumes observation of Brownian innovations, an information structure that is stronger and less standard than state-only feedback unless an observation model is supplied.

R11 is therefore best understood as a credible model-specific policy-verification study, accompanied by a competitive actor–critic implementation. That is valuable. It is not yet an Econometrica-level general numerical-method contribution, and the stylized application is not sufficiently substantive to carry the paper on its own.

## 2. What R11 successfully resolves

### 2.1 The post-training certificate is genuinely policy-specific

R10’s structural tube bound could not distinguish a successful actor from a poor actor. R11 now constructs a lower endpoint \(L_\phi\) from the saved policy’s paired outcomes, explicit discretization transfer, arithmetic account, and finite-family sampling bound. The resulting regret endpoint \(G_d-L_\phi\) changes with the policy. The deliberately saturated correction and the zero correction receive adverse assessments, confirming that the new procedure does not automatically approve every feasible tube policy.

This directly addresses the earlier B1 and B4 objections.

### 2.2 The implementation object is stated explicitly

The controller acts at a deterministic time grid, maintains an internal numerical state, observes innovations, applies an inward feasibility projection, and holds its action between dates. The economic state continues to evolve under the original continuous diffusion. The manuscript does not silently equate this object with continuously observed-state neural feedback.

This precision is important. It makes the transfer theorem interpretable, even though the information assumption raises a separate economic concern below.

### 2.3 The transfer argument is materially more credible than a grid-difference heuristic

The proof uses the cancellation of the common action sequence between the economic and internal states, stochastic Fubini, Itô isometry, generator bounds, and discrete Gronwall. The leading transfer account is \(O(h)\), apart from separately stated clipping, quadrature, and forward-arithmetic terms. It does not infer continuous-time accuracy from the difference between two Euler grids, nor does it require a sampled global derivative bound for the trained network.

### 2.4 Training uncertainty and final simulation uncertainty are separated

The revision reports ten seed-level fitted policies rather than averaging three actors before constructing a pathwise confidence interval. Seed ranges and standard deviations are described as algorithmic variability, while the empirical Bernstein endpoints are conditional on the fitted objects. This is the correct conceptual separation.

### 2.5 Stronger baselines and adverse outcomes are retained

The primary experiment includes direct policy optimization with the same nonlinear actor and an affine policy. Longer direct-policy and affine runs, critic-greedy variants, checkpoint frontiers, adverse policies, and R10’s negative results are preserved. The paper no longer relies primarily on the failure of one untuned greedy critic as evidence for the actor.

### 2.6 The evidence and provenance record is strong

The evidence snapshot contains 90 primary policies and 230 two-sided evaluation records. The audit recomputes saved statistics and checks raw-array and weight hashes. Only 460 of the allocated 2,000 one-sided statements are used. The main paper, supplement, and response compile without reported undefined references or overfull boxes. The nine failed initial-state evaluations are disclosed and recovered without refitting policies or replacing seeds.

These practices are unusually good and should be retained in any future paper.

## 3. Blocking concerns

### B1. The new certificate validates a policy, not the NBO numerical method

The policy-specific theorem is an important verification result, but it is deliberately agnostic about how the candidate was obtained. It applies to NBO, direct policy optimization, an affine actor, a hand-designed correction, or any other admissible sampled controller for which the paired statistic is generated.

That generality is mathematically attractive. It also means that the theorem does not establish the value of Bellman evaluation, the critic, or the NBO actor update.

This distinction is decisive in the reported data:

| Dimension | NBO mean gain | Direct-policy mean gain | Difference |
|---:|---:|---:|---:|
| 10 | 0.0019626 | 0.0018863 | 0.0000763 |
| 20 | 0.0015822 | 0.0014980 | 0.0000843 |
| 50 | 0.0017520 | 0.0016455 | 0.0001065 |

Both methods meet the declared \(L_\phi\geq 0.0005\) target in all ten seeds and both are independently certified against the schedule. Direct policy uses no critic and is cheaper to train. The central theorem therefore supports the verification layer, not the claimed superiority or necessity of NBO.

A publishable numerical-method paper must isolate what is gained by Bellman evaluation and costate regression. At present the strongest defensible statement is that NBO is one successful candidate generator among at least two successful nonlinear candidate generators.

### B2. The paper does not certify the small NBO advantage over direct policy

The final noise bank is shared across policies in a dimension, so the repository is well positioned to form a high-precision paired comparison between NBO and direct policy. Yet the reported theorem and tables certify each policy only relative to the schedule. They do not report a simultaneous lower bound for

\[
J(a^{\mathrm{NBO}})-J(a^{\mathrm{DPO}}).
\]

The difference between two separately positive schedule-relative lower endpoints is not a lower bound on the difference between the methods. Nor do the descriptive across-seed standard deviations supply inferential uncertainty for a new training run.

This omission matters because the incremental method difference is small. NBO’s mean gain exceeds direct policy by only 4.0%, 5.6%, and 6.5% of the direct-policy gain, while its median recorded training time is higher by approximately 46.7%, 42.1%, and 36.5%. Its verification time is also higher by approximately 20.4%, 14.3%, and 6.3%. Deployment times are essentially identical.

The paper should include a predeclared, family-adjusted, paired NBO-minus-direct-policy analysis at matched compute and accuracy. It should also report whether the difference persists across independent training replications, not merely whether each method beats the schedule.

Without this comparison, the paper establishes that state-dependent nonlinear policies are useful in this example, not that NBO is the numerical reason.

### B3. The certificate proves only a small tightening of a still-loose optimality bound

The inherited schedule bound \(G_d\) is approximately 0.01875, 0.02553, and 0.02754. The least favorable primary NBO lower endpoints are approximately 0.001183, 0.000716, and 0.000868. Thus training reduces the certified regret upper bound by only about:

- 6.3% of the anchor bound in dimension 10;
- 2.8% in dimension 20; and
- 3.2% in dimension 50.

The final regret upper endpoints remain 0.01756, 0.02481, and 0.02667. These are not small relative to the certified gain. The numerical experiment therefore does not show that NBO has computed a near-optimal policy. It shows that the policy is slightly better than the schedule and inherits a broad global comparison through the schedule.

This is a legitimate safe-improvement result, but it should not be presented as an accurate numerical solution of the underlying HJB problem. A stronger paper needs either:

1. a substantially tighter lower or upper benchmark for the optimum;
2. an independent high-accuracy reference in a smaller but nontrivial instance;
3. a policy-specific bound that closes a meaningful fraction of \(G_d\); or
4. an economic question for which the certified schedule improvement itself is substantively important.

### B4. The primary result is local to one initial state and is not robust across the reported state stresses

The primary theorem is correctly stated pointwise, and the main experiment uses \(y=0\). The stress table, however, shows that the positive certificate often disappears outside the training region.

For seed 11:

- with mean \(-2\), every reported dimension has a negative lower endpoint;
- with mean \(+2\), the mean gain is negative in dimensions 10 and 20 and approximately zero in dimension 50;
- with standard deviation 1, the lower endpoint is negative in dimensions 10 and 20 and only \(1.3\times10^{-5}\) in dimension 50;
- with the mean \(-1\), standard deviation 1.5, and Student-\(t\) profiles, the lower endpoints are negative;
- the internal trajectory is outside the training box essentially all the time in many of these tests.

These results do not invalidate the pointwise theorem. They do show that the central economic conclusion is fragile with respect to the initial state. A top-journal computational application needs an economically motivated initial-state distribution or region, not one favorable point accompanied by mostly inconclusive stress certificates.

The next study should predefine an economically relevant state population and either verify integrated performance over that population or establish a uniform result on a meaningful region. Negative and inconclusive stress outcomes should be central rather than supplementary.

### B5. The innovation-observation assumption changes the economic implementation problem

The new controller observes Brownian innovations at the grid dates and updates an internal state using those innovations. This assumption is what permits the same actions to cancel in the economic/internal-state comparison and avoids a global Lipschitz bound for the neural actor.

Mathematically, this produces an admissible policy in the enlarged filtration used by the model. Economically and computationally, however, it is not the standard state-feedback implementation suggested by much of the paper. In many applications, Brownian shocks are latent and must be inferred from noisy or discrete observations of the state. Even with continuously observed state and known coefficients, recovering innovations requires a specific observation and measurement convention.

The manuscript labels the assumption, but it does not justify it for the capital application or compare it with a state-observed implementation. The claimed numerical contribution therefore depends on an information structure that may be materially stronger than the economic problem of interest.

A future paper should state an observation model and either:

- implement a state-only sampled feedback rule with its own transfer account;
- show how the innovations are recovered from admissible observations; or
- recast the application explicitly as shock-observed control and explain its economic relevance.

### B6. The manuscript remains too broad and the application too stylized for the contribution established

R11 reorganizes the material, but the paper remains titled “Neural Bellman Operators,” spans recursive utility, endogenous preferences, viscosity selection, temporal selves, dynamic games, stochastic traces, interval action covers, and the capital study, and is accompanied by a 105-page supplement. The new theorem applies only to the additive-noise capital model and the specified sampled controller.

At the same time, the capital economy is not calibrated to data, does not answer a substantive policy or quantitative-economic question, and yields small certified gains. The least favorable NBO lower endpoints correspond to externally financed flow-equivalent changes of about 0.121%, 0.073%, and 0.089%. These are valid numerical quantities, but the paper does not explain why differences of this size in this stylized economy change an economic conclusion.

Econometrica can publish a broadly useful numerical method or a narrower method that unlocks an important economic result. R11 currently delivers neither at the required depth:

- the verification theorem is narrow and method-agnostic;
- NBO’s advantage over direct optimization is not certified;
- the application is stylized and pointwise; and
- the manuscript continues to carry a much broader research program than the central result supports.

The appropriate remedy is a genuinely focused new paper, not another layer of revision around the current cumulative manuscript.

## 4. Major comments

### M1. Rename “Mean gain” as the mean paired numerical statistic

The table’s “Mean gain” is the sample mean of \(X_{\phi,h}\), before subtracting the full transfer, clipping, quadrature, and arithmetic allowance. The rigorous continuous-time statement is the lower endpoint \(L_\phi\), not the raw sample mean.

For the representative dimension-10 seed-11 NBO policy, the recorded mean is approximately 0.001961, while the empirical Bernstein margin is approximately 0.000366 and the aggregate deterministic bias allowance is approximately 0.000409. The label “Mean gain” risks suggesting a direct estimate of the continuous-time gain. “Mean paired statistic” or “pre-adjustment paired estimate” would be more accurate.

### M2. Report direct paired method comparisons

Because common shocks are already reused, the paper should report pathwise NBO-minus-direct-policy and NBO-minus-affine differences, with the transfer terms appropriate to those differences and with family allocation fixed in advance. This is the most relevant numerical comparison and will often have much lower variance than comparing two separate schedule-relative intervals.

### M3. Match methods by economic accuracy and total work

The primary design equalizes simulator-state visits but not optimizer steps or total work. NBO performs five critic and five actor steps per batch; direct policy performs one direct gradient step. Longer direct-policy runs are reported, but the main comparison is still organized around a common iteration count and a post hoc cost table.

A method paper should present Pareto frontiers in total CPU/GPU time, simulation calls, peak memory, and certified economic error. The seed-11 checkpoint table uses fewer final paths and therefore has negative lower endpoints for every row; it is useful diagnostically but does not yet provide a certified cost–accuracy frontier.

### M4. Clarify the role of the critic through ablation

The descriptive correlation between the costate-target discrepancy and payoff is weak in dimensions 10 and 50 and strong only in dimension 20. The current evidence does not establish that the critic loss is a useful stopping or model-selection statistic.

Useful ablations would include:

- actor training with exact or higher-accuracy rollout costates where feasible;
- the same actor update using Monte Carlo policy gradients without a critic;
- varying the value-versus-costate weight in the critic loss;
- one, five, and more critic/actor updates per batch;
- removing the value-level term;
- an oracle small-dimensional reference for critic derivatives; and
- reporting whether critic diagnostics predict the independently certified policy gain.

### M5. Treat training-seed variation as a design object, not only a descriptive table

Ten seeds are a major improvement. They are nevertheless ten fixed seeds after exploratory development, and the final evidence supplies no population model for optimizer randomness. The exceptionally small across-seed standard deviations are encouraging but do not alone establish robustness to broader initialization, minibatch, architecture, or hyperparameter variation.

A future contribution-isolating study should prespecify a seed population, report method-level uncertainty across independent fits, and separate hyperparameter selection from final method comparison.

### M6. Run one clean end-to-end workflow from the final source snapshot

The nine initial-state stress evaluations failed before simulation because an integer-valued JSON mean produced an integer NumPy array. The authors transparently converted the numerically identical initial-state values to floating point, reran only those nine evaluations, and report no policy refit or seed replacement. This repair is benign in substance.

For archival clarity, however, a final paper should also provide one clean workflow that starts from the exact published source commit and regenerates all primary, stress, audit, and compilation artifacts without a recovery layer or source-manifest exceptions. The current split among numerical-source, source, evidence, referee, and delivery commits is carefully documented but unnecessarily difficult for an outside reader to audit.

### M7. Retrain the radius frontier

The radius 0.05 and 0.15 rows rescale a frozen correction rather than training policies for those radii. This is useful for studying the verified envelope, but it does not answer how the learning algorithm trades policy flexibility against trainability and certification. The radius frontier should include fresh fits at every radius with matched tuning and cost.

### M8. Put the state-stress failures in the main paper

The primary table presents uniformly positive results, while most large state shifts and dispersions have negative lower endpoints. Those results are not secondary robustness details. They define the domain in which the learned state dependence is useful. At least one compact stress table and a clear statement of the failure region belong in the main article.

### M9. Update the repository’s public-facing root README

At the pinned R11 evidence commit, the root `README.md` still describes the September 28 revision, 29 experiments, and eight tests. It does not identify R11, the source/evidence commits, the 90 primary policies, the policy-specific theorem, or the current reproduction commands. The detailed R11 README exists under the revision directory, but the repository landing page is stale and can mislead readers about the authoritative version.

### M10. Narrow the title, abstract, and literature claim

The abstract is more careful than before, but the title and retained application program still imply a general neural Bellman methodology. The most defensible new contribution is narrower: policy-specific statistical verification for a shock-observed sampled controller in one dense capital economy, with NBO as one candidate-generation method.

The paper should be positioned explicitly against:

- simulation-based policy evaluation and direct policy optimization;
- conservative and safe policy improvement;
- approximate policy iteration with error propagation;
- probabilistic numerical certificates;
- a posteriori control-performance bounds; and
- sample-average optimization under common random numbers.

The novel object should be stated precisely: the model-specific continuous-time transfer and finite-family post-training certificate, not the general principle of alternating evaluation and improvement.

## 5. Reviewer arithmetic and evidence checks

I performed an independent arithmetic check using the committed machine-readable audit, primary summary, cost table, protocol, compilation record, and representative policy record. I did not retrain the networks or independently replay all 230 raw arrays. The accompanying `review_diagnostics.py` reproduces the ledger calculations from a complete checkout.

### 5.1 Method comparison

| \(d\) | NBO–DPO mean difference | NBO training overhead | NBO verification overhead | Least-favorable NBO \(L_\phi/G_d\) |
|---:|---:|---:|---:|---:|
| 10 | 0.0000763 | 46.7% | 20.4% | 6.31% |
| 20 | 0.0000843 | 42.1% | 14.3% | 2.80% |
| 50 | 0.0001065 | 36.5% | 6.3% | 3.15% |

The direct-policy method meets the declared gain target in all ten seeds in every dimension, just as NBO does. The paper contains no separate simultaneous lower endpoint for the differences in the first numeric column.

### 5.2 Economic scale

Using \(A=\int_0^1 e^{-0.04t}\,dt\), the least favorable NBO lower endpoints imply externally financed flow-equivalent improvements of approximately:

| \(d\) | Least-favorable \(L_\phi\) | Flow equivalent |
|---:|---:|---:|
| 10 | 0.0011834 | 0.1208% |
| 20 | 0.0007160 | 0.0731% |
| 50 | 0.0008683 | 0.0886% |

These are certified improvements relative to the schedule, not welfare estimates for a calibrated population.

### 5.3 Evidence binding and disclosed recovery

The audit reports 90 primary policies, 230 two-sided rows, 460 used one-sided statements out of 2,000 allocated, and no training failures. The compilation record reports 39 main-paper pages, 105 supplement pages, and 5 response pages, with no flagged undefined references or overfull boxes. The remote-execution ledger records nine pre-simulation initial-state failures, all recovered without refitting policies or changing numerical values.

### 5.4 Limits of this review

I did not:

- independently retrain the 90 primary policies;
- independently regenerate all 230 raw path arrays;
- formally verify the interval and polynomial-arithmetic runtime;
- verify the ideal-iid property of the pseudorandom streams;
- prove a theorem beyond the assumptions stated in the manuscript; or
- infer journal acceptance from the successful repository workflow.

My conclusions about method comparison use committed summaries and source inspection. The report distinguishes those checks from an independent full numerical replication.

## 6. Conditions for a potentially publishable new submission

A future paper could be worth serious reconsideration if it completes a narrower and contribution-isolating chain.

1. **Choose the central contribution.** Present the policy-specific continuous-time verification method as the main result, or establish a genuinely NBO-specific numerical result. Do not rely on the broad cumulative title to join distinct contributions.
2. **Certify method differences directly.** Use common-path paired endpoints for NBO versus direct policy and strong classical alternatives, with family allocation and compute budgets fixed before the final run.
3. **Show value added by the critic.** Provide ablations and a setting in which Bellman/costate evaluation yields a material, reproducible, and cost-justified improvement over direct policy optimization.
4. **Tighten the optimality assessment.** Close a meaningful fraction of the anchor regret bound or provide an independent high-accuracy reference showing that the learned policy is near optimal.
5. **Use an economically meaningful state design.** Predefine an initial-state distribution or region and demonstrate robust gains there. Do not center the economic conclusion on one favorable state.
6. **Resolve the observation model.** Implement state-observed control or justify shock observation as an economic primitive.
7. **Connect to a substantive economic question.** Calibrate or otherwise motivate the model so that the certified gain changes a quantitative conclusion, policy comparison, or decision.
8. **Run one final immutable pipeline.** Reproduce every primary and sensitivity result from the exact publication source without post-run recovery exceptions.
9. **Reduce and refocus the manuscript.** Move the inherited research program to separate papers or archival appendices and update the repository landing page.

These changes would constitute a focused new contribution rather than another ordinary repair of the current cumulative manuscript.

## 7. Recommendation

R11 is the strongest and most credible version of this project that I have reviewed. It contains a real policy-specific continuous-time certificate, explicit implementation semantics, ten-seed neural and direct comparisons, strong provenance, and a commendably candid record of adverse and inconclusive results. The authors have resolved several serious objections from R10.

Nevertheless, the paper still does not meet the standard of an Econometrica numerical-methods contribution. The verification theorem is method-agnostic; direct policy optimization receives essentially the same certified economic result at lower cost; the small NBO advantage is not itself certified; the remaining optimality bounds are loose; the positive result is pointwise and fragile under state stress; the controller relies on observed innovations; and the stylized application does not supply enough economic substance to compensate for the narrow theory. The manuscript also remains far broader than its strongest theorem.

I therefore recommend **rejection in the present form and a substantially focused new submission rather than another ordinary revision of the current paper**. The most promising route is a shorter paper centered on the policy-specific verification theorem, with direct paired method comparisons, a justified observation structure, and an economically meaningful application in which Bellman-based learning has demonstrable value beyond direct policy optimization.
