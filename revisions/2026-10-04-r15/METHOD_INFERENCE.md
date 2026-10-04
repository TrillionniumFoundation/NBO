# R15 method distribution, inference, and complete work protocol

The executable `PROTOCOL.json` and trainer were frozen at commit
`9142f404bb9c5163aa94d3a4ded4d0fa48a49c50` before confirmatory streams were
executed. This document explains the statistical contract; the JSON
contains the exact seed list, primitives, counts, and algorithm budgets. Algorithm feasibility work is exploratory and cannot be relabelled
confirmation. Numerical outcomes are never software acceptance criteria.

## 1. Population and estimands

Let S be a published set of 16 new complete execution-stream identifiers. Each
identifier fixes model initialization, minibatches, training simulation,
validation, and the online checking random stream by domain-separated mappings.
The deployment algorithm draws one identifier uniformly from S and executes the
announced trainer, fallback rule, and stopping algorithm. Every identifier is
executed for every stochastic method. Deterministic methods are deterministic
members, not 16 fictitious independent training fits. They may nevertheless be
evaluated on the 16 independent confirmation strata for paired comparison.

For the original capital economy and prespecified initial-state population,

    G_m = (1/|S|) sum_s [J(pi_m,s) - J(schedule)],
    Delta_m,b = (1/|S|) sum_s [J(pi_m,s) - J(pi_b,s)].

The complete random stream includes stopping randomness. The finite stream
distribution is therefore part of the implemented method definition. Its whole
support is enumerated; it is not a random sample from the law of arbitrary
32-bit seeds. No standard error, t-test, bootstrap, or binomial interval over the
16 enumerated identifiers is appropriate. Training variation is included by
the exact finite mixture, and simulation error receives a probability bound.
Claims concern this specified randomized implementation and environment.
They do not extrapolate to unobserved initialization laws or hardware noise.

The implemented trainer must be deterministic conditional on the complete
execution identifier and environment (deterministic CPU kernels, pinned thread
count, versions, and operation-count budgets). Elapsed wall time is observed,
not a source of training selection. Unexpected nondeterminism is a protocol
violation requiring disclosure, not a seed replacement. Re-executing a member
uses its declared complete pseudorandom stream, including checking data; a
trainer that resamples its checking bank from a larger law is a different
method-level target. Final certificate probability is conditional on the
complete executed ensemble and unconditional by integration over its execution.

Secondary objects are the fraction of the finite stream population with gain
at least g, its worst-stream gain, and the complete finite distribution of
measured work to the prespecified certified target. Failures deploy the feasible
schedule and remain in all denominators. Failure statuses remain visible.

## 2. Paired, stratified confirmation

After all online decisions for a stream have been made, evaluate every returned
policy on an independent confirmation bank. Each stream receives the same
fixed N paths. The chosen N and mesh are fixed in PROTOCOL.json before execution.
Within a stream, all methods use identical initial profiles and
Brownian innovations; across streams, confirmation banks are independent.
Record noise hashes, initial-profile hashes, and the domain-separation key.

Direct contrast observations are numerical payoff differences on the same path,
not differences of separate confidence endpoints. The common schedule cancels
algebraically. Combine only the two policy transfer allowances and the relevant
roundoff/tail accounts; do not charge the schedule transfer twice.
This cancellation applies to two simulated candidate gains. A fallback returns
the analytical schedule with the exact numerical gain zero; comparison against
that exact zero retains the other candidate's full schedule-relative bias,
including reference transfer. Two analytical fallbacks have exact difference
zero. Both initial-state and terminal-reference hashes must match before any
simulated-reference cancellation is used.

For one endpoint, let X_sj be its numerical statistic and let
Y_sj = clip(X_sj, -C_s, C_s). Supply certified beta_s satisfying

    |J_s - E Y_sj| <= beta_s

where beta_s includes the appropriate diffusion/implementation, clipping-tail,
and arithmetic terms. With C=max_s C_s, n=|S|N, sample mean ybar and unbiased
pooled sample variance v, use the simultaneous two-sided interval

    ybar +/- {sqrt(2 v log(4/delta)/n)
              + 14 C log(4/delta)/(3(n-1))
              + (1/|S|) sum_s beta_s}.

Maurer and Pontil (2009), Theorem 11, applies to independent, nonidentically
distributed bounded observations. Thus deterministic balanced stratification is
valid, and the target is exactly the finite uniform method mean. Its sample
variance may conservatively include differences across stream means. All
strata must have equal N; missing or unequal strata cannot simply be flattened.

If instead one common Brownian path is reused across ALL training streams, the
independent unit is one averaged path block Z_j=|S|^-1 sum_s Y_sj. The sample
size is N, not |S|N. The implementation rejects cross-stream noise-key reuse in
the flattened estimator.

For per-stream statements, use the same formula with n=N and the separately
allocated error probability. If [L_s,U_s] hold simultaneously, the fraction of
streams truly meeting target g is enclosed by

    #{s:L_s>=g}/|S| <= p_g <= #{s:U_s>=g}/|S|.

Likewise min_s L_s <= min_s J_s <= min_s U_s. These are consequences of the
joint confidence event, not new statistical tests. All economic statements
must identify whether their object is a single policy or the method mixture.

## 3. Confidence allocation and online stopping

Reserve alpha_stop=0.01 and alpha_confirm=0.02. The other R15 families reserve
0.01 for mechanism accounts and 0.01 for protected-observation certificates,
giving a total R15 error budget of 0.05. Historical R14 statements retain their
separate historical 0.05 event and are not claimed jointly with R15 at 0.05.
Enumerate every two-sided
event in a committed ledger before execution, including dimensions, methods,
streams, target-specific execution arms, checkpoints, sample-size looks, and
contrasts. Each event in family f receives delta_f=alpha_f/E_f, where E_f is
the exact maximum event count. Missing/stopped events do not recycle alpha.
Both tails are included through log(4/delta_f). Multiple economic decisions
based on the same registered interval do not spend alpha again.

Each actual stopping run has one primary target (g=0.0005) and
at most three prespecified operation-count checkpoints. After each checkpoint,
training pauses and a genuinely executed fresh checking bank produces the
certified lower endpoint. If it exceeds the target, training stops and the
policy is written and reloaded. Otherwise training continues. The cumulative
clock and counters retain unsuccessful checks. If no checkpoint attains the
target, return the declared final feasible policy with status 'target not
attained'; fitting failure returns the schedule with its failure status.

Fresh checkpoint banks make the conditional probability argument immediate
even when continuation depends on previous check results. A finite union over
the registered looks handles selection. The independent final confirmation
bank is mandatory: arrays that triggered stopping are not ordinary unbiased
fixed-policy samples and cannot be pooled for the final method mean.

The 0.001 target is a secondary final-attainment endpoint, not a separately
executed stopping arm. A lower-target run stopped early does not measure work
to the higher target; no early-stopping frontier for 0.001 is inferred from
retrospective prefixes.

The three checkpoints record the progress of the executed stopping procedure.
No separate fixed-budget arm is inferred from them. The primary early-stopping
arm is not retrospectively replaced with the best fixed-budget checkpoint.

## 4. Economic margin and decisions

For the log-flow capital model let A=(1-exp(-rho*T))/rho. A proportional flow
consumption fee q corresponds to utility threshold -A log(1-q). The primary
economic margin is delta_e=0.0001 in payoff units, fixed before confirmation.
At rho=0.04 and T=1 this corresponds to 1.0200812979 basis points of gross
consumption through q=1-exp(-delta_e/A). Keep the utility targets 0.0005 and
0.001 explicitly distinct from fee rates; both receive the exact conversion.

For the direct method interval [L,U]:

* statistical superiority requires L>0;
* economically material superiority requires L>delta_e;
* noninferiority requires L>-delta_e;
* practical equivalence requires L>-delta_e and U<delta_e;
* economically material inferiority requires U<-delta_e;
* an interval containing zero alone establishes none of equivalence or
  superiority; report unresolved comparisons explicitly.

This margin is a numerical/economic accuracy convention for the stated stylized
economy, not an empirically calibrated welfare preference. Gain relative to the
schedule, direct method difference, and regret relative to the optimum remain
different endpoints. A broad regret upper bound cannot be renamed accuracy.

## 5. Complete measured work

Launch each method/stream/target arm in its own process. Start the parent clock
before child launch; stop after the final independent certificate and atomic
result files are durable. Retain both the complete parent-clock total and
stages for import/setup, deterministic constants, initialization, fitting,
validation, checkpoint writes, unsuccessful checks, successful check,
checkpoint reload, final confirmation, and result I/O. Process dispatch and
library import are part of the cold-run total. Also report a separately labelled
warm or amortized total when useful, with an explicit denominator.

Report process peak resident memory from the same fresh process, CPU seconds,
simulator transitions, rollout starts, actor/critic forward evaluations,
first- and second-derivative evaluations, backward passes, optimizer updates,
action-search iterations/candidates, and all verification paths and transitions.
Machine-independent counters are proxies, not claims of identical FLOPs.
The HJB greedy baseline must include its derivative and action-search deployment
cost. A structured solver must include reference/table construction and storage.

The method's finite work distribution retains every stream. Report attained
fraction, median work-to-target with unattained runs treated as +infinity, and
restricted mean work at a fixed cap. Never report the successful-runs-only
median as the method median. Record censored/unattained status in machine-readable
form rather than serializing infinity into JSON. Measured clock comparisons are
conditional on the stated environment, with the paired execution order fixed or
balanced beforehand. Replicate-environment studies are robustness checks, not
additional independent economic observations.

## 6. Feasibility and freezing

The primary scope is the same capital economy in dimensions 10 and 50, with
idiosyncratic volatility 0.6 and common volatility 0.3, primary actor width 32,
and 16 complete streams. Methods are NBO, raw_costate with four antithetic
rollouts per label, direct_policy, and neural_hjb. The exact trial identifiers
and all primitive values are in PROTOCOL.json. R14 remains the separate original
volatility-regime evidence. No width-64 confirmation family is included. No method is dropped because its
economic outcome is inconvenient. Final N, mesh, budgets/checkpoints, stream
identifiers, primitive hashes, algorithm fingerprints, all target arms, economic
margin, and confidence-event ledger must be fixed after exploratory feasibility
and before any confirmatory bank is inspected.

Power cannot remove numerical transfer bias. The frozen deterministic
allowance floor and the equivalence margin remain in their original records.
The subsequent paired-transfer theorem tightens the direct normal-policy
comparison on the same simultaneous finite-expectation event, using common
innovations and the model's derivatives. Its timing and proof are disclosed in
`PAIRED_TRANSFER_REFINEMENT.md`. It introduces no new samples, fitted objects,
stopping decisions, statistical events, or enlarged margin. Both original and
refined endpoints remain available. The finite-time method result may be
positive, negative, equivalent, or unresolved; all are retained.

Reference: Andreas Maurer and Massimiliano Pontil (2009), "Empirical Bernstein
Bounds and Sample Variance Penalization," Theorem 11, arXiv:0907.3740.
https://arxiv.org/pdf/0907.3740
