# R31 prospective, referee-informed protocol

Date: 2026-09-24. Baseline review e9bc144fbb6843d6a3436825a28584efb64fb8f1; reviewed article 3394815f4ccbf5917582c8f756b535adf87783cc. This is an exploratory revision, not an independent preregistered confirmation. No R30 or earlier scientific file will be overwritten. All failed configurations and any amendments will be retained.

## 1. Constructive, coupled economic problem

Finite-horizon capital-condition/maintenance economy, state x in [0,1], discount 19/20, terminal payoff x/2. The three actions are defer (0), maintain (1), and replace (2). Current reward is x minus action cost, with costs (0, 3/20, 9/20). Under each action two next-state branches have probabilities (3/5, 2/5):

- defer: (3x/4, 3x/4+1/20);
- maintain: (17x/20+1/10, 17x/20+7/50);
- replace: (x/10+4/5, x/10+17/20).

These maps remain in [0,1]. Every positive-cost action is myopically inferior; its merit must arise from its effect on continuation. No optimal-value or optimal-action file is supplied. Primary horizons are 4, 8 and 12; tolerances are 1/100 and 1/20. The model is not a discretization of the original stopped diffusion. Its one-dimensional, piecewise-affine structure must remain explicit.

Construct upper Bellman witnesses by backward action-dependent expectation, affine-envelope maximization and rational, globally checked polygonal compression. Charge every construction step, intermediate breakpoint, rational bit length, serialization and verification. Use a per-step compression allowance chosen analytically from the requested uniform regret budget. A separate uncompressed piecewise-affine DP is a strong information-matched comparator, not a naive enormous grid. Add linear-spline fitted-Q controls on 33 and 129 nodes and neural fitted-Q proposals (one hidden ReLU layer, width 16, 257 midpoint training states, Adam 200 steps per date, learning rate 0.02, seeds 31001, 31002, 31003). Terminal continuation is the stated settlement. Compile saved binary64 neural coefficients as exact rational piecewise-affine functions and retain all raw failures; do not claim hardware floating-point deployment is verified.

Record training, compilation, upper-witness construction, installed-policy evaluation, admissible-set construction, cost minimization, final policy evaluation, encoding and final verification separately. Report both newly trained and already installed regimes; do not assign zero cost to training in a cold pipeline. Cap any exact intermediate representation at 200000 pieces and report a cap hit as unresolved, not a certificate. Comparator outcomes may not be selected by sign.

## 2. Endogenous occupancy and economic units

Use revision cost (1+x) times the indicator that the deployed action differs from the installed action. One unit denotes one normalized implementation intervention, not dollars. Construct certified local action sets from the computed upper witness and a uniform all-restart regret budget. Minimize discounted intervention cost with the action-dependent transition kernel. Evaluate the installed and deployed operating values and intervention costs as piecewise-affine functions, integrating against the initial uniform state distribution exactly.

Compare the dynamic minimum with a pointwise rule that retains the installed action whenever admissible and otherwise minimizes current intervention cost with action-order tie breaking. Include the myopic all-defer incumbent as a non-neural stress control. State explicitly whether operating-value preservation is also certified; cost minimization is only within the displayed admissible class. Report whole sensitivity curves in the shadow price, break-even thresholds, occupancy-induced differences and certificate conservatism, not a chosen-price universal-win headline.

## 3. Full scalar optimization in the unchanged stopped economy

Retain the R30 active-boundary restart (0,61/50,5/4), k=2, c=3/4, p=0 and theta in [-1/5,1/5]. Reuse the validated killed-kernel oracle with all analytic remainders. Extend the five-point diagnostic to a complete interval covering: combine validated point derivatives with a proved uniform second-derivative bound, subdividing until derivative sign is certified, or retain unresolved intervals and use payoff bounds for global branch-and-bound. Do not transfer central-state concavity. Produce a global scalar optimum certificate if the covering succeeds. This does not substitute for the original 47-coordinate or all-domain current-state result.

## 4. Theory, tests and preservation

Prove constructive finite-representation witnesses including compression error, the all-restart action class, a policy-dependent minimum-cost certificate, and a margin/proposal-error work statement that includes witness and proposal construction costs. Distinguish classical comparison/DP arguments from the new construction and execution. Include exact endpoint/tie checks, malformed/missing-cell and changed-model rejection, zero-tolerance finite checks, independent Bellman inequalities, and brute-force small-model policy checks.

Produce ECTA_R31, SUPP_R31, RESPONSE_R31, COMPUTATION_R31 and a lossless historical annex with the unmodified Econometric Society class. Address R30-F1--F12 and T1--T10 separately, distinguishing completed mathematical/computational results from empirical claims not established. The original full-domain target stays 0.01 and its existing bound is not silently replaced by an auxiliary-model number. Publication must be confined to this new R31 branch and its exact remote head checked.
