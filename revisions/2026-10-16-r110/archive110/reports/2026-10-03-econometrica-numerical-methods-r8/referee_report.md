# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r8-referee-2026-10-03`  
**Pinned revision commit:** `f9a7e32e23c0b4173390d4807da6eace46f42ba1`  
**Pinned revision tree:** `b5a59be205d09519f08d8acfb838c51915bcca90`  
**Pinned manuscript blob:** `8ad86c37b1019abdacacd76e521ec0a0e87d4264` (`ECTA.tex`)  
**Pinned supplement blob:** `a22a6591ccd2569a987ef1707dfffa2288e935cd` (`supp.tex`)  
**Report date:** 3 October 2026  
**Recommendation:** **Reject in the present form; encourage a substantially narrower new submission rather than another ordinary revision of this manuscript.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R8 is a major improvement over the earlier versions. The manuscript is now integrated, the numerical record is unusually transparent, the continuous-action actor is trained without exhaustive maximizing labels, raw and locally improved policies are separated, finite-game deviations are evaluated dynamically, and the complete-action verifier retains unresolved boxes rather than declaring false convergence. I found no evidence that the stored action enclosure is invalid. The exact remote workflow completed successfully; the fifteen new R8 tests and the twenty-three inherited R6/R7 tests pass; all thirty-seven recorded execution commands have zero return codes; and my independent stress checks found no enclosure violation.

Those advances resolve most of the earlier concerns about provenance, hidden action oracles, and incorrect interpretation of sampled diagnostics. They do not establish the central numerical-method contribution required for publication in Econometrica.

The decisive evidence in R8 points in the opposite direction from the proposed actor-based method:

1. local search changes essentially every active state-time action proposed by the continuous actor;
2. actor-free search and direct statewise optimization produce equal or better certified nodal policies;
3. all nine hybrid continuous-action policies fail the manuscript's own uniform `0.1` target;
4. the complete-action verifier is valid but budget-saturated at every time step and is far more expensive than training;
5. no continuous-state/time transfer error is computed; and
6. the machine-readable refinement study shows large off-center deterioration that is not visible in the center-only table printed in the supplement.

The paper has therefore become a careful framework for separating proposal, evaluation, search, and verification. That is useful. It has not shown that Neural Bellman Operators, as a numerical method, improve accuracy, computational cost, scalability, or economic scope relative to direct optimization, local policy search, classical dynamic programming, or projection methods. The main positive contribution is the discipline of the error account, not a demonstrated advantage of the actor architecture.

I do not view the remaining gap as a matter of exposition. Closing it would require either a different, tightly focused verification paper with a genuine continuous-economy theorem and scalable certificate, or a different algorithm paper with a problem on which the actor supplies a reproducible cost-to-accuracy advantage. Either route would be a new submission.

## 2. Scope and independent verification

I reviewed the exact R8 evidence snapshot at commit `f9a7e32e23c0b4173390d4807da6eace46f42ba1`. The corresponding materialized source is `db00f1e80c141c749e1769f99909a85255fdba1a`. The remote workflow is GitHub Actions run `37124422696`; it completed successfully and produced artifact `11275136290` with recorded digest `sha256:0249481a0fee6cd61ef728e2ab38c1114fd8e5af7bb308d531658e4f4ead41f3`.

The artifact contains the exact source, raw arrays, logs, tables, and compiled documents. The recorded document identities are:

| Artifact | SHA-256 | Pages |
|---|---|---:|
| `ECTA.pdf` | `a6d4a70c9a6a883211280695bdbcfda5c90bbb3956b2dafeda879191446d5e34` | 51 |
| `supp.pdf` | `e9db4cb4d71c70863d89f3c465e50d42b0f678b344136dc2e2c33f0116dea286` | 30 |
| `response.pdf` | `ffc697457d818398a99028c62592087e8986f7c09cd39797e565dcd1a0cad1f0` | 7 |

I independently performed the following checks in the pinned Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, PyTorch 2.10.0 CPU, and mpmath 1.3.0 environment:

- reran the fifteen R8 regression and accounting tests;
- reran the twelve R6 and eleven R7 inherited test cases;
- checked that all thirty-seven recorded commands have return code zero;
- reconstructed an independent point evaluator for the two-state preference economy and matched the project evaluator to `7.11e-15` in maximum absolute error;
- tested 170,000 randomly sampled point evaluations inside randomly generated action boxes, including point and interval continuation arrays, with no sampled value outside the stored cell-corner enclosure; and
- ran forty independently seeded differential-evolution searches at selected states and times. Every resulting feasible lower bound remained below the stored optimal upper envelope. The smallest observed envelope slack was `4.97e-4`; the largest was `1.29e-2`.

These checks support the implementation's inclusion property. They are not a formal machine proof and do not replace the maintained interval invariant. I did not independently rerun the entire approximately 1,450-second tight branch-and-bound cover from scratch; I inspected and stress-tested its exact stored source and arrays.

## 3. What R8 successfully repairs

The amount of substantive progress deserves explicit recognition.

1. **There is now an authoritative paper.** The root article and supplement incorporate the actual R7 and R8 evidence instead of leaving the numerical work on a detached protocol branch.

2. **The continuous actor no longer receives exhaustive labels.** Its updates differentiate its own positive-weight payoff. Reference maximization and global covering begin only after the policy is frozen.

3. **Deployment objects are separated.** Raw actor, actor-plus-search, direct optimization, and actor-free search have distinct arrays, costs, and diagnostics. The paper does not call a hybrid policy a raw network.

4. **The action cover is budget-safe.** Unresolved boxes retain outward upper bounds. A time, depth, or box budget cannot be converted into a false success.

5. **The scope of every certificate is substantially clearer.** The complete action cover is explicitly a certificate for the finite state/time nodal economy, not a continuous-diffusion theorem. The continuous transfer defects are displayed rather than silently set to zero.

6. **The comparison set is stronger.** The revision adds direct continuous optimization, actor-free search, gated finite Bellman regression, tensor Chebyshev projection, classical game recursion, and actor-free neural continuation fitting.

7. **The negative evidence is retained.** Raw actor failures, multi-head failures, narrow-domain capital failures, missing pure fitted stages, and unresolved action boxes remain in the record.

8. **Reproducibility is excellent.** Exact source identities, raw arrays, failed runs, query counts, closure counts, environment pins, generated-table manifests, build logs, and compiled PDFs are all available.

These improvements materially change my view of the reliability of the paper. My negative recommendation rests on the numerical and economic content that remains after those repairs.

## 4. Blocking concerns

### B1. The actor contribution is not identified; the ablations indicate that search, not the actor, produces the successful policy

The continuous-control experiment was designed to answer the earlier objection that the finite actor merely learned exhaustive maximizing labels. It succeeds in removing those labels. It does not show that the actor is useful.

For the three actor seeds, the raw finite-reference losses are `0.2596`, `0.0733`, and `0.2597`. The independently propagated raw full-action bounds are `0.2989`, `0.1417`, and `0.2991`. Local search changes the actor's action at `100.000%`, `99.974%`, and `99.987%` of active state-time nodes. The policy reported as the successful continuous result is therefore not a small correction of a trained actor.

The common-envelope results are more revealing:

| Method | Mean uniform nodal bound | Mean training time | Mean training queries | Runs passing `0.1` |
|---|---:|---:|---:|---:|
| Actor + search | `0.1274` | `23.32 s` | `2.261 million` | `0/3` |
| Direct + search | `0.1171` | `31.78 s` | `11.841 million` | `0/3` |
| Search only | `0.1195` | `13.52 s` | `0.961 million` | `0/3` |

The actor-free search ablation is faster, uses fewer action queries, and has a better mean certified bound than actor-plus-search. Direct optimization plus the same search also has a better mean bound. At the initial center state, all three methods have nearly indistinguishable bounds around `0.058`–`0.065`.

Thus R8 demonstrates that a feasible local search can repair poor proposals, not that the neural actor improves the policy search. The actor may still be valuable in a larger or more expensive problem, but that value is not established here. An Econometrica numerical-method paper needs a setting in which the proposed architectural ingredient produces a reproducible gain after total cost is counted. Otherwise the paper should be reframed as verified approximate dynamic programming with neural and non-neural proposal mechanisms, and the actor should not be the organizing contribution.

### B2. The complete-action certificate is valid but does not reach the declared accuracy and is not operational at a persuasive cost

All nine hybrid continuous-action policies fail the displayed uniform `0.1` target. Their bounds range from `0.1153` to `0.1301`. The center-state bounds are smaller, but the paper's verification claims are full-domain claims, not center-state claims.

The two action-cover implementations together require `40.96` million action-box evaluations and `1,624.59` seconds. The tighter cell-corner cover alone uses `27.36` million box evaluations and approximately `1,447.71` seconds. It exhausts its budget at every one of the twenty time levels, retains approximately `2.02` million unresolved leaves in total, and reports one-step optimization brackets as large as `0.0312`. The looser cover also exhausts every time level.

This is mathematically acceptable because unresolved upper bounds are retained. It is not evidence that the verification problem has been solved efficiently. The verification cost is roughly fifty to more than one hundred times the training cost of the compared policies on a problem with only 425 state nodes, twenty dates, and three controls. No complexity result or scaling experiment shows how the cover behaves as the action dimension, state grid, horizon, or requested tolerance grows.

A budget-safe bound is preferable to a false certificate, but the paper currently turns a failed global search into a valid loose interval. That is an important engineering result, not yet a competitive verification method. A publishable claim would need either a materially tighter certificate at the declared accuracy or a theorem and experiment demonstrating favorable scaling under economically meaningful structure.

### B3. The nodal certificate does not transfer to the continuous economy, and the recorded refinements reveal large off-grid policy losses

The manuscript correctly states that continuous-state interpolation, diffusion approximation, time discretization, reflection, and continuously monitored stopping defects remain uncomputed. Every relevant result file records `continuous_state_time_error: null`. The transfer proposition is therefore an accounting identity with unknown terms, not a bound for the economic diffusion.

The refinement evidence is more concerning than the center-only table suggests. The printed table reports only the center payoff, where the frozen policies look fairly stable. The machine-readable `REFINEMENT.json` also records the maximum finite-reference-minus-policy payoff over the full refined state-time grid. Recomputing those fields gives:

| Grid and steps | Largest recorded finite-reference advantage over a frozen policy |
|---|---:|
| `17 x 25`, 20 steps | `0.0612` |
| `25 x 37`, 40 steps | `1.5662` |
| `33 x 49`, 80 steps | `2.1234` |

The largest losses occur away from the center, often near high risk aversion and the lower wealth boundary. For example, the `2.1234` loss occurs for the direct seed-29 policy near `u=3`, `X=0.515`. The finite 175-action reference already beats the interpolated continuous policy by that amount; the continuous-action optimum could only make the comparison more demanding.

This is not merely absence of a convergence theorem. It is evidence that policies trained and certified on the coarse nodal economy can deteriorate severely under the paper's own frozen-policy refinement. Reporting only center values conceals the diagnostic most relevant to a full-domain claim. The full-domain maxima, their locations, and their economic scale must be printed and analyzed.

A future paper needs one of the following: controlled one-sided consistency bounds for the stopped/reflected scheme; retraining and recertification on nested grids with a demonstrated error trend; or a much narrower claim limited to the original finite nodal economy. The current manuscript cannot use the language of a continuous economic method while its principal two-state policy has no continuous-state/time bound and displays this refinement failure.

### B4. The strongest baselines dominate in the settings where complete verification is available

The additional comparisons are useful because they reveal the method's position rather than merely decorating it.

On the identical finite preference economy:

- degree-14 tensor Chebyshev projection obtains a policy bound of `0.0039`, value error `0.0165`, and training time `0.15` seconds;
- gated finite Bellman regression obtains policy bounds between `0.0079` and `0.0098`; and
- classical backward induction remains much cheaper on the small grid.

On the finite dynamic game, classical recursion obtains essentially zero player regret in approximately `0.22` seconds of construction, while the actor-free neural continuation fits require roughly `36`–`43` seconds and leave maximum player regrets between `0.027` and `0.069`.

In the continuous-action preference comparison, direct-plus-search and search-only match or improve the actor-plus-search certificate. In the one-dimensional stopped-consumption problem, the direct HJB baseline is comparable and sometimes faster. In the high-dimensional capital experiment, the paper explicitly reports policy-evaluation differences rather than an optimality comparison.

These results are not an embarrassment; they are exactly what a serious comparison should disclose. They imply, however, that the paper has not isolated a domain in which NBO is the preferred numerical method. The claim cannot be rescued by noting that some baselines exploit low dimension: exploiting structure is part of good computational economics. A neural method earns its place by solving a problem that the strong alternatives cannot solve at comparable accuracy and total cost. That demonstration is absent.

### B5. The theory is a careful synthesis, but the manuscript does not establish a distinct numerical principle or convergence result for NBO training

The finite-horizon residual bound, contraction residual bound, monotone-scheme viscosity argument, policy-improvement comparison, Bellman upper/lower sandwich, and transfer decomposition are useful and mostly correctly scoped. They are also standard ingredients of verification, approximate policy iteration, monotone dynamic programming, and interval branch-and-bound.

The paper does not prove convergence, sample complexity, stability, or rate results for the proposed actor-critic training. Proposition 1 remains valid for any feasible policy, whether neural, tabular, projected, random, or locally searched. The transfer proposition records unknown defects. The actor is not required for the certificate and, empirically, is not the best proposal mechanism in the principal continuous experiment.

Accordingly, the paper's novel object is primarily the implementation discipline: separate derivative graphs, explicit action-oracle accounting, and a reproducible verifier. That can be valuable, but at Econometrica it needs either a new theorem with substantive numerical consequences or an economic application that could not be handled competitively by established alternatives. R8 supplies neither.

### B6. The verifier and the high-dimensional evidence address different problems; there is no scalable certified experiment

The complete action cover applies to a two-state nodal economy with three controls. The continuous differential certificate applies to a special one-dimensional stopped problem. The dimensions ten and twenty capital experiments use common-noise Monte Carlo policy evaluation. They do not provide uniform residual bounds, action-gap bounds, continuous-domain certificates, or optimality comparisons.

The narrow-domain high-dimensional policies underperform the direct comparator materially; at the finest recorded Euler level, NBO-minus-direct payoff differences include `-0.0334`, `-0.0630`, and `-0.2016`. Wide-domain differences are mostly small, with both signs. These are useful state-coverage diagnostics. They do not show that the verification machinery, action cover, or actor scales to the problems that motivate neural methods.

The paper therefore has no experiment that is simultaneously:

- genuinely high-dimensional;
- nonlinear and economically nontrivial;
- trained with the proposed actor-critic mechanism;
- compared against a strong alternative at matched accuracy; and
- independently certified over the relevant domain.

Without such an experiment, the broad scalability motivation remains disconnected from the paper's strongest theorem and certificate.

### B7. The manuscript remains too broad relative to the depth of the established contribution

The 51-page article and 30-page supplement cover differential residuals, monotone schemes, recursive utility, portfolio benchmarks, endogenous preferences, temporal selves, dynamic games, stochastic traces, interval arithmetic, continuous action covering, projection methods, and high-dimensional Monte Carlo diagnostics.

The revision is now honest about the evidentiary status of each component, but honesty does not create a single deep theorem-algorithm-application chain. The reader must assemble a method from many special cases whose strongest conclusions live on different domains. The result is impressive as a research dossier and difficult to evaluate as one Econometrica paper.

A focused paper could be strong. The present omnibus manuscript dilutes the genuinely useful contribution—the disciplined separation of policy proposal, policy evaluation, improvement, and verification—while making the title suggest a general numerical method that the comparisons do not support.

## 5. Major comments

### M1. The title and abstract should not imply an actor advantage

The title “Neural Bellman Operators” is defensible only if the paper identifies what is gained by the neural actor. The present data show that the certificate is proposal-agnostic and that actor-free search performs at least as well on the central continuous experiment. The abstract should state this negative result directly or the paper should adopt a verification-centered title.

### M2. Full-domain refinement statistics must replace the center-only presentation

The center table is not an adequate summary when the paper's principal distinction is between sampled or local diagnostics and uniform economic error. At minimum, report the maximum and selected quantiles of `reference - policy`, the state-time locations of the maxima, boundary-region summaries, and action saturation rates at each refinement. The current center table is inconsistent with the paper's own methodological message.

### M3. Accuracy targets need an economic interpretation

The `0.1` threshold is reported in absolute utility or profit units. The paper correctly refuses to call it a common consumption-equivalent percentage. That leaves the reader without a criterion for whether `0.115` or `0.130` is economically adequate. A focused application should convert certified value differences into a model-specific welfare or policy metric, or justify the absolute scale from the economic question.

### M4. Comparisons must use total cost at achieved accuracy

Training time, reference time, local-search time, policy-evaluation time, shared upper-envelope cost, and per-policy verification cost are currently separated. This is transparent, but the main comparison tables still invite readers to compare training seconds while the certificate costs orders of magnitude more. Report total cost-to-certified-accuracy, with shared costs amortized under explicitly stated numbers of policies.

### M5. The action box remains an economic primitive, not merely a computational domain

The complete action cover verifies the chosen box, not an unconstrained economic optimum. Consumption and portfolio bounds remain active in sensitivity studies. The paper should provide an economic justification for `[0.02, 0.30] x [0, 1.5] x [-0.45, 0.45]`, or treat conclusions as conditional on that constrained economy. Expanding the box changes the model and may substantially change both cost and policy.

### M6. The hybrid policy needs a deployment specification

Actor-plus-search requires stored continuation representations and online action queries. A raw actor, a nodal lookup table, a locally searched hybrid, and an interpolated off-grid policy have different runtime, memory, smoothness, and robustness. The paper should choose one deployment object for its main method and report its online cost and off-grid behavior, rather than treating all four as nearby versions of the same policy.

### M7. Dynamic-game conclusions remain finite-grid conclusions

The player-specific best responses are a genuine improvement over one-step gradient tests. They cover a declared finite state/action game. Continuous actions, continuous capital states, and time-discretization errors remain uncomputed. The dynamic-game section should be shortened or explicitly retitled as a finite-game validation laboratory.

### M8. The high-dimensional comparison needs a decision-relevant benchmark

Paired pathwise differences are statistically well constructed, but they compare two frozen policies without a common lower or upper performance benchmark. A reader cannot infer which policy is close to optimal. A stronger experiment would include a problem-specific lower bound, relaxed control bound, policy-improvement certificate, or trusted low-dimensional slices.

### M9. Interval terminology should remain conditional

The paper is mostly careful to describe outward binary64 arithmetic under a stated execution model rather than formal verification. That language should remain uniform in the abstract, tables, and conclusion. Random stress tests—including mine—support the implementation but do not certify the Python interpreter, math library, processor, or transcendental routines.

### M10. The response history should not determine the final paper's architecture

R8 carries almost every historical application into the integrated article because each arose in an earlier round. A final paper should be organized around its strongest contribution, not around preserving the full sequence of referee exchanges. Historical experiments can remain in the repository without occupying the main scholarly argument.

## 6. What would constitute a publishable future paper

I see two viable directions, but they should not be combined into another omnibus revision.

### A. Verification-centered paper

A verification paper could focus on the budget-safe Bellman envelope. It would need:

1. a clear novelty theorem relative to monotone dynamic programming and interval branch-and-bound;
2. complexity or adaptive-refinement results showing when the cover is tractable;
3. a controlled continuous-state/time transfer bound, including stopped-boundary monitoring;
4. nested-grid retraining and recertification with a demonstrated full-domain trend;
5. comparison against projection, classical dynamic programming, and alternative validated numerics at total certified cost; and
6. one economic application for which the resulting bound changes a substantive conclusion.

The policy proposal could be neural, projected, or search-based. The certificate would be the contribution.

### B. Actor-based numerical-method paper

An actor paper would need:

1. a problem where statewise direct optimization or exhaustive action search is genuinely costly;
2. actor-only or actor-dominant performance, rather than correction at essentially every node;
3. matched direct, search, and actor-free ablations at equal total budgets;
4. multiple held-out models or parameter configurations fixed before tuning;
5. robust seed-level failure accounting; and
6. a cost-to-accuracy advantage that survives verification and deployment costs.

The current two-state preference economy does not supply that evidence.

## 7. Recommendation

R8 is technically serious, unusually reproducible, and far more trustworthy than the earlier manuscript. The authors have responded constructively to difficult criticism and have built a valuable numerical evidence package. I found the complete-action enclosure credible within its stated nodal scope.

Nevertheless, the paper does not establish an Econometrica-level numerical method. The actor is not shown to improve the central computation; the successful policies are produced primarily by local search; every continuous-action policy misses the stated uniform target; the verifier is budget-saturated and substantially more expensive than training; the continuous-state/time transfer is uncomputed and displays severe full-domain refinement deterioration; and strong classical or projection baselines dominate where complete comparisons are available.

I therefore recommend **rejection in the present form**. I would encourage a new, substantially narrower submission built around either a genuinely scalable verification theorem or a demonstrated actor advantage, but not another ordinary revision that preserves the current breadth.
