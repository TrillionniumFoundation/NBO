# Referee Report — Neural Bellman Operators (complete R21 publication)

**Venue standard:** Econometrica-level numerical / computational methodology  
**Recommendation:** **Reject in the present form.** R21 resolves the prior review-object and continuum-proof deficiencies, and I did not find an obvious algebraic contradiction in the new local self-financing / continuum / price-transport chain. The remaining problem is more fundamental: the complete R21 object demonstrates a carefully certified **restricted stochastic policy construction**, not an accurate or competitive full-state Neural Bellman Operator; the closest end-to-end non-neural configuration remains more accurate and much cheaper to generate; and the paper's advertised "representation ablation" does not actually isolate the neural representation because it simultaneously changes optimizer, initialization, and parameterization.

**Review date:** 2026-09-23  
**Review branch:** `review/econometrica-r21-final-numerical-methods-2026-09-23`  
**Reviewed publication branch:** `revision/econometrica-r21-referee-copy-2026-09-23`  
**R21 scientific source commit recorded in the publication manifest:** `e8d197fd6658a5954f7b9053eec9eaeffd417790`  
**R20 confirmatory training source:** `b1a2ea39d895b330e5a11b4e55d86b7a4985b101`  
**R20 preregistration / protocol commit:** `238ecc0052dc418e1fe6fd06c3daa4a93da1a335`  
**Previous R21 intermediate-snapshot report:** `bc118f20f6361cdeae668141e45f64c436ee6a2a`  
**Intermediate snapshot reviewed there:** `6951c3b01b5102ef3d743a6ab14f9cc595b08804`

---

## 1. Executive assessment

R21 is a materially stronger and much cleaner revision than the intermediate snapshot I previously reviewed.

The authors have now done several things correctly and explicitly:

1. They materialize a complete manuscript, supplement, response, proof chain, publication manifest, replay record, and referee-facing index.
2. They prove the self-financing decoder in continuous time rather than relying on sampled wealth trajectories.
3. They provide a continuum theorem for the four-expert mixture on
   [
   K=[1.98,2.02]	imes[1.24,1.26].
   ]
4. They address the nontrivial fact that improving four corner experts does not by itself prove improvement of the interior mixture, by bounding the old mixture's Jensen gain.
5. They keep the unrestricted dual comparison separate from fixed-policy payoff evaluation.
6. They disclose that the network input is time only; the stochastic factor dependence is supplied by a prescribed logistic decoder and the portfolio by analytic conditional pricing.
7. They put the adverse direct stochastic comparison in the main paper.
8. They explicitly state that the full-domain 0.01 objective is not closed.

Those are substantive improvements. The earlier blocking complaint that "the R20/R21 theorem is not materialized" is resolved.

My negative recommendation therefore does **not** rest on missing files or on a claim that the new local theorem is obviously false. On the contrary, the new R21 proof architecture is considerably more reviewable than before.

The central difficulty is now the paper's methodological identity.

The strongest R21 result is a local, fixed-initial-time, four-expert, model-assisted stochastic policy construction. Its neural network observes only a time index. State dependence in consumption is imposed by a hand-designed logistic rule, while the portfolio is recovered from an exact contingent-claim price. Interior initial states are handled by a bilinear mixture of four separately trained corner experts with stored initial-state context. The sharp regret certificate additionally depends on an inherited non-neural dual upper library.

Meanwhile:

- the best inherited full-state complete-domain feedback certificate remains about **7.278319** against the unchanged **0.01** objective;
- the new sub-0.003 result is only on the small rectangle (K), at (t=0);
- the direct non-neural stochastic configuration is **strictly more accurate at every tested vertex** and has a sharper uniform (K) bound;
- direct policy generation takes about **1.143 seconds** for four experts, versus **10.63–10.79 seconds** for one four-expert neural seed;
- the claimed "representation ablation" does **not** isolate representation, because neural and direct runs use different optimizers (Adam versus L-BFGS-B), different initializations, and different parameterizations.

Thus R21 establishes that a neural-generated restricted policy can be accurate and certifiably improved. It does not establish that a Neural Bellman Operator is the accurate numerical method, nor that hidden neural layers contribute positively to the accuracy-work frontier.

For an Econometrica-level numerical-method paper, that gap remains decisive.

---

## 2. What R21 genuinely fixes

### 2.1 The review object is now complete

The present branch contains `ECTA_R21`, `SUPP_R21`, `RESPONSE_R21`, readable R21 proof files, replay outputs, the continuum audit, the representation audit, and a publication manifest. The root revision index points to the correct object.

This resolves the prior report's R21-F0/T1/T2 complaints.

### 2.2 The continuum theorem is now reviewable

The new main text explicitly defines the four-subaccount policy:
[
u_t=sum_ilambda_i u_t^i,quad
X_t=sum_ilambda_i X_t^i,quad
c_t=sum_ilambda_i c_t^i,quad
	heta_t=sum_ilambda_i	heta_t^i,quad
p_t=rac{sum_ilambda_i p_t^iX_t^i}{X_t}.
]

The proof explains why the combined wealth process is self-financing, why the wealth-weighted portfolio stays admissible, how common-no-exit paths permit concavity, and how the complement event is paid for by an explicit error term.

This is substantially better than a JSON-level assertion that "four-corner mixing gives K-uniform transfer."

### 2.3 The old-mixture Jensen problem is correctly recognized

R21 correctly observes that strict payoff improvement at the four vertices does not automatically imply strict payoff improvement of the bilinear mixture throughout the interior. The authors therefore derive a separate upper bound (Gamma_0) for the old mixture's Jensen benefit and combine it with final lower bounds.

That is the right conceptual fix.

### 2.4 The paper is more honest about architecture

R21 now states plainly that:

- the neural network input is only the normalized time-slab coordinate;
- the factor dependence enters a prescribed logistic control form;
- the portfolio is supplied by a conditional-price decoder;
- the interior policy uses fixed initial-state context;
- the resulting feedback is restricted, not a single learned map on all current states.

This removes an important ambiguity from earlier revisions.

### 2.5 The adverse classical comparison is no longer hidden

The main text now reports that the direct stochastic configuration has smaller certified regret at every vertex, strictly larger actual payoff than every final neural policy at those vertices, and much lower generation time.

That is exactly the comparison a referee needs to see.

---

## 3. Decisive numerical facts in the complete R21 object

The central local neural result is:

| Seed | Uniform (K) regret at 1,000 updates |
|---|---:|
| 20100 | 0.00290848 |
| 20101 | 0.00290261 |
| 20102 | 0.00289514 |
| 20103 | 0.00289022 |
| 20104 | 0.00289318 |

The certified initial-to-final mixture payoff gain is between about 0.01762 and 0.01840, and the reported pointwise true-regret ratio upper is at most about 0.1411.

The direct stochastic method has final uniform (K) regret about:

[
0.00283871,
]

which is sharper than every final neural seed.

At the four vertices, R21's own representation table gives:

| ((u,x)) | Best neural regret | Direct regret | Certified direct payoff advantage |
|---|---:|---:|---:|
| (1.98,1.24) | 0.00261425 | 0.00258714 | (ge 2.670	imes 10^{-5}) |
| (1.98,1.26) | 0.00289022 | 0.00283871 | (ge 5.111	imes 10^{-5}) |
| (2.02,1.24) | 0.00268964 | 0.00266465 | (ge 2.459	imes 10^{-5}) |
| (2.02,1.26) | 0.00260024 | 0.00255442 | (ge 4.542	imes 10^{-5}) |

At the final retained work level, policy-generation cost is:

| Method | Four-expert generation seconds |
|---|---:|
| Neural seed 20100 | 10.631 |
| Neural seed 20101 | 10.730 |
| Neural seed 20102 | 10.788 |
| Neural seed 20103 | 10.627 |
| Neural seed 20104 | 10.638 |
| Direct | 1.143 |

The shared checker dominates total elapsed verified work, so the first-hit end-to-end gap is much smaller than the generation gap. That does not change the methodological fact: the neural generator is not improving the policy frontier in this experiment.

The old complete-domain full-state feedback result remains about **7.278319**, not 0.0029. The paper now says this explicitly, which is good; it is also why the local R21 success cannot be treated as closure of the flagship problem.

---

## 4. Blocking scientific findings

### R21F-F1 — The accurate R21 object is not the full-state Neural Bellman Operator named in the title

The paper's strongest result is for a restricted policy family:
[
c_j(y)=0.5+0.3,sigma(b_j-s_jlog y),
]
with time-slab coefficients generated by a network and a portfolio supplied by analytic pricing.

The network does **not** observe current preference or current wealth. It does not learn the portfolio. It does not learn the state transition structure. It does not learn a Bellman upper witness. Interior-state deployment is not produced by a state-conditioned network but by a four-expert mixture using fixed initial-state context.

The authors are now careful about these facts. But the methodological implication remains: the sub-0.003 result is not evidence that the full-state Neural Bellman Operator has become accurate.

The actual full-state complete-domain object remains hundreds of times above the declared 0.01 target.

For a paper whose title and framing continue to center "Neural Bellman Operators," this is still the main publication-level problem.

### R21F-F2 — The advertised "representation ablation" is not a clean representation ablation

This is the most important new methodological defect in the complete R21 presentation.

The main text says that the same-family comparison tests the neural parameterization itself. The code does not isolate that factor.

In `revisions/2026-09-23-r20/replication/run_study.py`:

- the neural policy uses the `Actor` network and **Adam** with learning rate 0.005;
- the direct policy uses a 16-by-3 free `Slab` tensor and **L-BFGS-B**;
- the direct run starts from the fixed raw coefficient vector ([0,-1,-1]) in every slab;
- the neural run starts from random network weights whose final layer is only partially standardized;
- the parameterizations have different geometry and effective conditioning;
- the stopping rules and iteration semantics differ.

Therefore the experiment compares two **end-to-end optimization configurations**:

> neural shared parameterization + Adam + neural initialization

versus

> direct slab parameterization + L-BFGS-B + fixed direct initialization.

It does **not** identify the causal contribution of hidden layers.

This distinction matters in both directions:

- The authors cannot conclude that hidden layers themselves cause the adverse result.
- More importantly for the paper, they also cannot use the comparison to characterize what the neural representation contributes.

A genuine representation study should cross at least the principal factors:

1. neural parameterization optimized by L-BFGS / trust-region or another strong deterministic optimizer;
2. direct slab parameterization optimized by Adam under comparable gradient budgets;
3. matched or explicitly mapped initial policies;
4. function/gradient evaluation counts in addition to iteration counts and wall time.

Without that crossed design, "representation ablation" is too strong a label.

The present comparison remains a valid and important **practical baseline**. As such, it is adverse to the neural end-to-end configuration. It is not a clean representation identification experiment.

### R21F-F3 — Even as an end-to-end configuration, the direct method dominates the neural configuration in the tested regime

The confounding above does not rescue the neural method.

As an end-to-end solver comparison, R21's direct configuration is better in exactly the quantities that matter:

- lower certified regret at every vertex;
- strictly higher certified actual payoff at every vertex;
- sharper uniform (K) bound;
- much lower policy-generation time;
- the same expensive verification machinery.

Thus the current evidence does not show a certified regime in which the neural configuration improves the accuracy-work frontier.

A top numerical-method paper centered on the neural architecture needs at least one meaningful regime in which the architecture earns its complexity: higher dimension, larger state coverage, amortized repeated solution, richer policy class, transfer across parameters, or a frontier not reachable by direct optimization.

R21 does not yet provide such a regime.

### R21F-F4 — The continuum improvement theorem depends on synchronized corner initialization

The final uniform accuracy theorem does not require identical initial experts. The **initial-to-final mixture improvement** theorem effectively does.

In `audit.py`, `jensen_initial` begins by asserting that all four initial experts within a seed have exactly equal slope and preference-drift vectors. That equality is then used to make the initial mixture's Jensen-gap bound small enough to establish the 0.0176+ uniform payoff improvement.

Why are those initial vectors equal? Because `run_study.py` executes:

`torch.manual_seed(seed)`

inside the vertex loop before constructing each corner network. Thus all four vertex networks within a seed start from the same parameter dictionary.

R21 now discloses this. But the methodological dependence remains substantial.

The headline "policy-sensitive continuum improvement" is therefore not currently a generic consequence of the acceptance mechanism. It is a consequence of:

- strict corner payoff improvement;
- plus a special synchronized initialization structure;
- plus a problem-specific Hessian/Jensen bound.

If the four experts were independently initialized, the present (Gamma_0) argument would generally change and might be too loose.

A future version should either:

1. derive a general initial-mixture Jensen bound that handles independently initialized experts; or
2. run an independent-initialization design and show the continuum-improvement theorem still closes; or
3. explicitly present synchronized initialization as a required part of the algorithm and justify why that is the intended scalable construction.

At present the paper risks presenting a specially engineered proof device as a general solver property.

### R21F-F5 — The continuum result is interpolation of separately trained experts, not learned state generalization

The network sees time only.

To cover a two-dimensional initial-state rectangle, R21 trains four experts separately and then constructs a bilinear mixture. The continuum guarantee comes from analytical concavity and convexity, not from the neural network learning a state-conditioned mapping.

This is a valid verified control construction. It is not evidence of neural generalization across state.

That distinction becomes important for scaling.

In higher-dimensional state spaces, a corner-mixture strategy can require a rapidly growing number of experts/cells unless additional structure is used. R21 contains no complexity theorem for extending the method from one small rectangle at one start time to the full state-time domain.

The paper therefore needs a scaling story, not merely another local rectangle:

- a single state-conditioned network;
- a sparse adaptive cover;
- a triangulation with complexity control;
- a monotonicity/convexity decomposition;
- or another mechanism that avoids an essentially cell-by-cell expert library.

Without this, the local continuum theorem does not address the computational bottleneck of the global problem.

### R21F-F6 — The successful adaptivity is primarily model-based, not learned

The strongest R21 policy obtains factor adaptivity from the prescribed logistic form and financial feasibility from exact conditional pricing.

The self-financing theorem is elegant, but it also shows how much of the successful construction comes from analytic model structure:

- the factor process is known;
- an equivalent martingale measure is available;
- the policy is embedded in a one-factor replicable consumption stream;
- the portfolio is the analytic hedge of that stream;
- global portfolio admissibility is proved from a closed-form derivative bound.

This is excellent model-specific numerical design. It is not a generic neural Bellman mechanism.

For an Econometrica-level numerical methodology claim, the paper should establish whether the method survives beyond this analytically hedgeable structure: incomplete markets, multiple financial shocks, additional endogenous states, nonreplicable constraints, or models where the decoder itself must be learned/numerically solved.

Otherwise the appropriate framing is a validated policy method for a special stochastic-control class, not a general Neural Bellman Operator.

### R21F-F7 — The sharp regret certificate remains a hybrid construction with an essential non-neural dual

The local policy lower bounds are compared to an inherited unrestricted dual upper library. The paper correctly charges the library separately and reports its construction cost of about 415.789 seconds.

This is scientifically legitimate.

But it means the sub-0.003 regret certificate is not an end-to-end output of the neural policy generator. It is a hybrid certificate:

> restricted learned-policy lower bound + model-based decoder + inherited non-neural unrestricted upper.

The same upper is also used for the direct comparator, so the neural-versus-direct comparison remains fair.

The issue is one of method definition. If the paper wants to claim a complete NBO numerical method, the unrestricted comparison object is an essential component and must be treated as part of the algorithmic system. If the paper wants to claim a policy generator evaluated by an external certifier, that is a different and more defensible methodological identity.

R21 has improved the disclosure but has not resolved the identity choice.

### R21F-F8 — The all-domain continuation witness blocker remains open

The retained complete-domain result remains roughly 7.278 against a 0.01 objective. The historical continuation-trace diagnosis remains informative, and R21 correctly does not pretend that a local dual bypass has repaired the global critic.

But for the full-state NBO problem, the key mathematical object is still missing: a globally sharp continuation upper witness whose boundary trace and interior residual can be controlled simultaneously.

The new local unrestricted dual is a different comparison device. It does not solve the original global witness problem.

This gate remains open exactly where the paper's title is strongest.

### R21F-F9 — The price-transport theorem is useful, but it does not materially broaden the state-space claim

R21 proves a clean post-training sensitivity result on
[
K	imes[1.5,2.5]
]
for fixed policies.

That is worthwhile.

But (k) enters the payoff affinely for a fixed policy, and the unrestricted value is convex in (k). The new theorem therefore exploits a favorable one-dimensional parametric structure. It does not establish robustness across the missing state dimensions, starting times, or global state domain.

This should remain a sensitivity result, not be used to imply broad policy generalization.

### R21F-F10 — The compensation result needs more careful economic interpretation

The paper says an additional 0.002 of initial wealth is sufficient compensation for each learned stochastic policy. The construction, however, does not merely evaluate the **same fixed policy** at higher initial wealth. It retains learned slopes and preference-drift shapes while modifying a consumption intercept / budget offset and re-verifying the financed stream.

That is a reasonable "same learned shape, re-budgeted policy" experiment. It is not literally the welfare loss of freezing the original decision rule and adding wealth.

The paper already says the number is not a minimum compensating variation. I would go further:

- call it a **sufficient re-budgeted wealth increment**;
- distinguish it from compensating variation for an unchanged policy map;
- avoid language suggesting a structural welfare estimate unless the exact policy counterfactual is defined economically.

The 0.00004475 margin is also small enough that this interpretation should be stated with exceptional precision.

### R21F-F11 — The policy-acceptance mechanism has not yet been stress-tested as a general optimizer

The acceptance rule itself is conceptually correct:
[
L^{n+1}>U^n.
]

But all sixty noninitial neural proposals in the confirmatory run are accepted. Thus the empirically executed study does not meaningfully test the difficult branch of the algorithm: frequent rejection, rollback, stagnation, or proposal noise under tighter/high-dimensional certification.

The code contains rollback logic, but the confirmatory evidence does not show how the solver behaves when the gate becomes active rather than permissive.

For a general method, I would want at least one stress regime in which:

- some proposals are rejected;
- optimizer/network state restoration is exercised;
- progress does not depend on hand-picked checkpoint spacing;
- rejection frequency and cost are reported.

This is not a correctness objection to the current accepted trajectories. It is a robustness objection to treating the gate as a demonstrated general solver mechanism.

### R21F-F12 — The five-seed study is useful replication but not a broad robustness study

There are five independent seed dictionaries. There are not twenty independent vertex initializations. The four corner experts within a seed intentionally share initialization.

No architecture sensitivity, learning-rate sensitivity, checkpoint sensitivity, or optimizer sensitivity is reported for the neural system in the successful stochastic experiment.

Given that the direct baseline changes optimizer and wins, optimizer sensitivity is especially important.

The current five-seed evidence is enough to show that the reported local phenomenon is not a one-seed accident. It is not enough to establish robust neural numerical superiority.

---

## 5. Proof-level and certification comments

I do **not** find an obvious fatal algebraic contradiction in the following R21 chain:

1. conditional-price self-financing identity;
2. global portfolio admissibility bound;
3. joint concavity of the running CRRA term on the stated rectangle;
4. common-no-exit event plus complement correction;
5. convex dual transfer over (K);
6. old-mixture Jensen upper bound;
7. affine fixed-policy transport in (k).

That is a meaningful improvement over earlier versions.

The following proof/certification issues should nevertheless be tightened before publication in a top methods venue.

### R21F-T1 — Separate theorem proof from executable certification more systematically

Some constants are justified analytically in the appendix, some are generated by interval code, and some rely on inherited validation utilities. The paper should provide a single table mapping each headline bound to:

- the exact theorem;
- the exact analytic assumptions;
- the exact script/function;
- the exact result file;
- the arithmetic backend(s);
- whether the check is proof-critical or only a replay consistency check.

The current manifest is good provenance. It is not yet a compact proof-dependency graph.

### R21F-T2 — The MPFR replay is arithmetic redundancy, not mathematical independence

R21 says this correctly. Keep that language.

The binary and MPFR paths share the same economic derivation, stopping correction, quadrature architecture, and theorem structure. Overlap therefore detects implementation/arithmetic inconsistency; it does not independently validate the mathematical model reduction.

This is not a defect if stated precisely.

### R21F-T3 — Report objective/gradient evaluations for the neural/direct comparison

The direct code already records `objective_calls`. The neural code can also count objective / backward evaluations.

Because Adam steps and L-BFGS-B iterations are not comparable units, the main comparison should report:

- wall time;
- function evaluations;
- gradient evaluations;
- line-search evaluations;
- checker calls;
- parameter dimension.

This is especially necessary if the paper continues to discuss representation rather than only end-to-end wall-clock performance.

### R21F-T4 — Match initial policies in the representation study

The direct run starts from a fixed slab vector while the neural run starts from random network parameters.

A representation comparison should attempt to initialize the two parameterizations to the same delivered policy (or as close as analytically possible), then optimize them under crossed algorithms.

Otherwise initialization quality is another confounder.

### R21F-T5 — Do not call the direct comparison a "same-family representation ablation" without qualification

It is the same **delivered stochastic policy family** in the sense that both ultimately produce slabwise (b,s,	heta) coefficients. It is not the same optimization problem in parameter coordinates.

A more accurate description is:

> matched delivered-policy-class end-to-end baseline.

That wording is strong enough and scientifically cleaner.

### R21F-T6 — Quantify scaling of the four-subaccount implementation

At an interior initial state, the deployed policy maintains four subaccounts and conditional-price objects.

Report:

- per-time-step evaluation cost;
- memory cost;
- whether the four conditional prices are evaluated analytically or quadrature/interpolation is required online;
- how this cost would grow with a multi-cell cover.

The present generation ledger does not answer runtime scalability.

### R21F-T7 — Clarify what is fixed before observing the R21 results

The R20 seeds/work levels were preregistered. The R21 continuum Jensen argument, price transport, representation audit, and compensation calculations are post-training analyses of frozen policies.

That is acceptable. They should be labeled explicitly as **a posteriori certified properties** rather than confirmatory experimental endpoints.

---

## 6. Status of the previous report's principal gates

### Previous materialization gate

**Closed.**

The final R21 object is complete and reviewable.

### Previous continuum-transfer gate

**Closed for the stated local mixture theorem.**

The exact four-subaccount policy is now defined and proved admissible.

### Full-state policy-sensitive NBO gate

**Open.**

The successful R21 policy is not a new full-state NBO execution.

### Full-domain 0.01 accuracy gate

**Open.**

The complete-domain full-state certificate remains about 7.278319.

### Neural representation-advantage gate

**Not closed; the current evidence is adverse.**

Moreover, the new "representation ablation" is causally confounded by optimizer and initialization changes.

### Global continuation-witness gate

**Open.**

R21 bypasses the old critic locally but does not construct the missing global sharp witness.

### Matched global classical frontier

**Open.**

The local direct stochastic comparator is strong and adverse to the neural configuration. A sharp full-domain classical comparator is still missing.

### Coherent paper identity gate

**Open.**

The paper now contains a strong verified-policy story, but not yet a successful full-state Neural Bellman Operator story.

---

## 7. What would justify a genuinely new round

I would not view the following as sufficient for another major round:

- more seeds on the same (K);
- a slightly larger (K);
- more arithmetic precision;
- more post-hoc price nodes;
- another neural wrapper around the same decoder;
- another local table where direct optimization remains better.

A new round should change the methodological evidence.

### Gate N1 — Crossed optimizer / representation experiment

At minimum, run:

- neural + Adam;
- neural + L-BFGS/trust-region;
- direct slab + Adam;
- direct slab + L-BFGS/trust-region;

with matched delivered initial policies where possible and with function/gradient evaluation accounting.

This is necessary before attributing outcomes to representation.

### Gate N2 — State-conditioned neural policy execution

Train and certify a network that actually consumes current state variables relevant to the Bellman problem, rather than only a time index.

The policy may still use analytic feasibility layers, but the learned object should do genuine state generalization.

### Gate N3 — Independent-corner initialization or a general Jensen theorem

Either remove the synchronized-initialization dependence from the continuum improvement proof, or demonstrate that independently initialized experts still yield a certified interior improvement.

### Gate N4 — Scaling beyond one four-corner rectangle

Provide either:

- a substantially larger domain with a controlled cover;
- a multi-cell adaptive algorithm with complexity accounting;
- or a theorem showing how certification cost scales with state dimension and tolerance.

### Gate N5 — A neural regime that improves the certified frontier

Show a regime in which the neural method is not merely accurate but **usefully changes what can be achieved** relative to direct optimization:

- higher-dimensional policy family;
- amortization across many states/parameters;
- transfer to new (k) or model parameters without retraining every expert;
- richer admissible control geometry;
- or materially better accuracy-work scaling.

### Gate N6 — Full-state witness progress

Construct a substantially sharper complete-domain continuation/witness object rather than bypassing the critic only on the local rectangle.

### Gate N7 — Reframe if the neural advantage does not appear

If the direct parameterization continues to dominate, the scientifically strongest paper may be about:

- policy-value-separated acceptance;
- validated stochastic policy certification;
- continuum transfer;
- exact financial feasibility layers;
- and rigorous economic policy comparisons.

In that paper, neural networks would be one candidate generator, not the claimed source of the numerical advance.

That could be a coherent and potentially strong computational-economics contribution.

---

## 8. Recommendation

**Reject in the present form.**

R21 deserves credit for resolving several real technical deficiencies. The complete publication object is now reviewable. The local self-financing and continuum arguments are substantially stronger. The paper correctly distinguishes policy payoff from witness quality. It gives a real certified initial-to-final policy improvement and a sharp local regret bound. It also presents the adverse direct comparator instead of hiding it.

Those improvements clarify, rather than remove, the main methodological problem.

The accurate R21 policy is a restricted, analytically decoded, four-expert stochastic control construction. The full-state NBO remains far from the global target. The learned network sees only time. Interior-state coverage is supplied by analytical mixture, not learned state generalization. The sharp upper comparison is inherited from a non-neural dual. The direct non-neural configuration remains more accurate and much cheaper to generate.

Finally, the new "representation ablation" is not a true representation ablation: it changes Adam to L-BFGS-B, changes initialization, and changes parameter coordinates at the same time. Thus the paper neither demonstrates a neural advantage nor cleanly identifies why the neural configuration underperforms.

The strongest defensible conclusion from R21 is now:

> A rigorously certified, model-assisted restricted stochastic policy system can deliver useful local accuracy and genuine policy-value improvement, and a neural generator is one workable way to produce such policies.

That is scientifically meaningful.

It is still different from:

> Neural Bellman Operators have been demonstrated to be an accurate and competitive numerical method for the full stochastic dynamic problem.

The latter claim is not supported by the complete R21 evidence.
