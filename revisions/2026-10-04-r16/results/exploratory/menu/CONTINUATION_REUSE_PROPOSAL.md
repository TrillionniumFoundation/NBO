# R16 continuation-reuse proposal (exploratory design, not a registered experiment)

## Finding and decision

The original R15 actor calls cannot create a credible amortization result: Raw
already caches all continuation labels, and both methods return materialized
actors. Recounting the same queries would manufacture a work advantage.

A new finite-period capital decision problem gives genuine reuse. A temporary
current-quarter consumption-utility weight, adjustment charge, or feasibility
constraint changes the current action problem. All primitives, payoff terms,
and the fixed reference policy after that quarter remain exactly common. The
postdecision continuation is consequently the *same mathematical function* for
all current tasks, although its evaluation point changes with the chosen action.

The first fixed exploratory implementation gives positive NBO payoff differences
against all five included candidate classes, but only the difference against
four-path Raw SAA is approximately 1e-4. The strongest learned vector-costate
surrogate is only 8.92e-6 below NBO and costs less. The pilot does not support a
material superiority or work-dominance claim against that comparator.

## Economic problem

Retain the capital drift, correlated Gaussian shocks, log consumption, aggregate
adjustment cost, and terminal dispersion penalty already studied in the paper.
Define a quarterly finite Bellman instance explicitly, rather than asserting
that a coarse finite model is the original diffusion without a transfer proof.

For d sectors, let h=1/4 and K=T/h. Let the unchanged R15 transformed one-period
weights be A_k and B_k, now evaluated for the declared horizon T. The candidate
chooses a current vector a in [0.02,2]^d. Its postdecision mean is

    x(y,a) = y + h {c0 + kappa tanh(B y) - a}.

The task z=(w,eta) changes only the first-period consumption weight and aggregate
adjustment coefficient. After the first step, the process follows the common
fixed cell-average analytical schedule pi_k. Thus

    Q_z(y,a) = A_0 {w mean(log a) - eta (mean a)^2/2}
               - B_0 mean(a) + C(x(y,a)) + known task/state constant,

where C is the expected sum of every remaining transformed reward and the
terminal dispersion penalty, including the current Gaussian state transition.
The omitted constant cancels between every pair of feasible actions for the
same task and initial state. C is independent of w and eta. A change in future
utility weights, future policy, diffusion, coupling, horizon, or terminal
preference would require a different C and a separately charged evaluation.

The first pilot uses d=10,T=2,K=8,kappa=.3,CHI=.1,sigma_I=.6,sigma_C=.3,
and otherwise the original primitive values. Its 9 tasks are the Cartesian
product w in {.8,1,1.2}, eta in {.1,.2,.4}. Initial states have uniform mean
[-.5,.5], uniform standard deviation [0,.5], and a centered normalized Gaussian
direction. All 9 tasks are evaluated at every new initial state.

This is a short-lived preference or administrative-cost counterfactual followed
by the same mandated/committed continuation schedule. It does not treat a
persistent structural counterfactual as if its continuation were unchanged.

## Baselines that must remain

1. **NBO scalar continuation.** Fit a scalar two-hidden-layer tanh continuation
   to the shared value/costate rollouts, retain the exact quadratic terminal
   lift, and differentiate it at the action-dependent postdecision point.
2. **Cached Raw SAA.** Cache all initial states, innovations, common random
   numbers, and already evaluated quantities. Solve each new action problem
   against the complete sample-average continuation. Do not charge fictional
   regenerated innovations or repeated simulation for identical cached points.
   Include at least 4/16/64 antithetic paths in the fixed work frontier.
3. **Materialized Raw task actor.** Fit one policy conditioned jointly on state,
   consumption weight, and adjustment charge from cached raw costates. Every
   task can reuse the same labels and all existing actor information.
4. **Materialized DPO task actor.** Fit one conditional policy against the actual
   full finite continuation rollout; all paths are cached and reused. This is
   the nonlinear stronger alternative to a single reference-costate
   linearization. Its fitting and complete rollout differentiation are charged.
5. **Learned vector-costate surrogate.** Fit a two-hidden-layer vector network
   to exactly the same labels with the same exact terminal lift. It may query
   new postdecision points and materialize a conditional actor. This controls
   for generic regression/smoothing and for amortization available without a
   scalar learned value. A claim that omits this comparator is not persuasive.

The pilot's action optimizer uses the same 180 projected-parameter Adam updates
for NBO, vector-costate and SAA. A registered comparison must add an independent
optimization check or the same prespecified L-BFGS refinement for scalar-valued
objectives, retain failures, and measure the deployed candidate itself. The
vector field can use a declared root/projection procedure; it must not silently
be assumed to be a gradient field.

Both NBO and the vector surrogate may distill a task actor. Any query-work
comparison must compare the best declared, verified deployment representation
for each method. NBO should not be credited with actor materialization that its
comparators are forbidden to use.

## First exploratory result, full disclosure

One seed, 380711, was fixed in the script before its execution. There were 512
training states, four antithetic paths per state, 32 new initial states times
nine tasks (288 queries), and 64 independent common evaluation paths per query.
These are *unprotected descriptive pilot results*, not confidence statements.

| comparator | mean NBO minus comparator | smallest task-average difference |
|---|---:|---:|
| cached Raw SAA, four paths | 0.000101690476 | 0.000066182045 |
| materialized Raw actor | 0.000025636974 | 0.000015965167 |
| materialized DPO | 0.000024613292 | 0.000018197883 |
| learned vector costate | 0.000008920720 | 0.000005175860 |

NBO field fitting took 2.833 seconds, vector fitting 1.373 seconds, and their
288-query action solves took 0.237 and 0.135 seconds. Cached Raw SAA action solves
took 1.363 seconds; the materialized DPO and Raw actor fits took 7.818 and 0.978
seconds. These are component clocks only. They exclude process startup, imports,
common evaluation, archive writes and several common operations, and are not
publication-ready total-work comparisons.

The first execution failed at construction of the vector network because the
historical imported module did not export its `Net` helper. The error and its
preceding NBO fit output are retained in `MENU_EXPLORATORY_PILOT.first_attempt.stdout`.
The repair inserted the explicitly identical-width vector MLP and reran the
same seed and unchanged scientific parameters. No successful candidate or
economic outcome was selected from alternate seeds.

An earlier purely exploratory random-feature exercise reused existing R15
replay. In all 12 prespecified cells, the fixed random-feature scalar-gradient
ridge predictor was less accurate than a same-feature unconstrained vector
ridge. Its approximation bias exceeded its potential pooling benefit. All 12
rows are retained in `RF_REPLAY_PILOT.json` and cannot be used as affirmative
evidence for the new scalar critic.

## Proposed confirmatory structure, for root approval and later freezing

Keep the 1e-4 economic materiality margin used previously visible. Do not lower
it because this pilot's vector contrast is smaller. Distinguish a positive
incremental payoff, superiority beyond 1e-4, practical equivalence at a declared
margin, and a work-to-verified-accuracy result.

Use a small complete economic family, not further seed search at the pilot
point. A suitable candidate family contains the original low-volatility and
R15 high-volatility primitives at T=1, the explicitly explored T=2 point, and an
untouched intermediate-horizon/intermediate-coupling calibration. A longer
T=4 point may be included because additional continuation periods are the
economic reuse/variance mechanism; it must be fixed together with the others,
before inspecting any payoff there. Original and R15 configurations remain
first-class rows even if they favor Raw.

Recommended method schedules are complete budget frontiers (e.g. 128/512/2048
shared labeled states and 4/16/64 antithetic paths for direct SAA), selected by
independent costate/action diagnostics only, never final test payoff. Different
networks should receive their prespecified optimizer/capacity choices rather
than a common nominal update count being called equal work.

Freeze an entire finite query catalog (all initial states and all tasks) before
the fitted methods exist. Execute every member, and then use genuinely new
independent continuation banks to certify the catalog-average direct payoff
differences. Separately sample new training streams from an explicitly declared
seed law; report both conditional finite executed-stream conclusions and the
actual across-stream variation. The former must not be described as inference
to generic future optimizer draws.

Certification should be query-conditional: all actions and queried critic
coefficients are fixed after fitting, so local continuation/flow bounds may be
computed for those actual action pairs. This avoids importing the R15 global
network spectral range that overwhelmed its occupation-risk experiment. The
Gaussian tails, terminal dispersion, and numerical representation errors still
require explicit treatment.

## Mechanism and exact interpretive limits

For a strongly concave current Bellman objective, curvature-weighted gradient
error bounds action regret. The comparison must evaluate errors at actual
action-dependent query points, not substitute training MSE. A direct paired
payoff interval can establish incremental value independently of an imprecise
sufficient risk bound, but it does not retrospectively make that bound positive.

For fixed neural gradient features, the mathematics agent has an exact nested
projection identity: removing nonintegrable feature directions trades omitted
signal energy against removed noise energy. This explains a possible advantage
of a scalar continuation representation and also the negative random-feature
pilot. It does not apply verbatim to the fully optimized nonlinear MLP or imply
that a generic vector surrogate must lose.

If stronger Raw/vector configurations erase the pilot gain at lower complete
work, the comparison must report that result. Additional independent regimes
can be studied only as the frozen whole family, not as repeated searches for a
favorable seed or a post hoc materiality margin.

## Source proposal

The exploratory runnable prototype is `menu_pilot.py`. A publication source
should be split into independently audited modules:

* `menu_economy.py`: immutable primitive/task/query identities, weights,
  transition, complete continuation payoff and exact shared-target checks;
* `menu_methods.py`: the five methods, caches, conditional actors, complete
  optimizer state, no final-test access;
* `menu_worker.py`: isolated method/stream execution and complete parent clock;
* `menu_verify.py`: fixed-query paired return accounts, numerical/tail enclosures,
  independent risk diagnostics and prespecified stopping events;
* `report_menu.py`: simultaneous event allocation, all frontier points, actual
  failures, original/explored/untouched calibration labels, and direct contrasts;
* tests for changed future policy or primitive invalidating the continuation
  cache, current-task changes preserving it, cache-hit accounting, derivative
  identity, realized candidate feasibility, and complete failed-run retention.

No confirmatory source or remote branch is created by this proposal.
