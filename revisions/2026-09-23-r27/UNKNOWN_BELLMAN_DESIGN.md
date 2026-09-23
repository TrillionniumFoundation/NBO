# Unknown-solution stopped inventory Bellman experiment

This design is fixed before executing the R27 inventory benchmark. It supplements, and never replaces, the original continuous-time economy. No exact value or externally supplied optimal-action labels are available to either fitted solver.

## Rational economic primitives

Horizon T=8, discount beta=99/100. State x is a d-vector with each inventory in {0,...,L-1}. Primary d in {2,3,4}, L=4. Actions order 0 units, or 1 or 2 units for one inventory, subject to capacity L-1. At every non-default state the d+2 equally likely demand vectors are: all zeros; all ones; and, for each coordinate j, all ones with coordinate j raised to two. The state after sales is y=max(x+order-demand,0). Sales are min(available,demand), shortages are max(demand-available,0). Per-period reward is

sum(sales) - (3/5)*order_units - (1/10)*1{order_units>0} - (1/50)*sum(y^2) - (2/5)*sum(shortages^2) - (1/(20d))*sum(shortages)^2.

The all-zero state is a stopped default state with settlement -2-d/5. At horizon 8, non-default inventory receives sum(x)/5-sum(x^2)/50. Model constants and transition/reward arrays are generated from rational/integer primitives. Demand is not chosen to produce a known solution.

## Candidate solvers and frozen evaluation

Backward neural fitted Bellman iteration uses the same states, one-step transitions, rewards, action constraints, terminal payoff and default payoff as total-degree polynomial fitted Bellman iteration. Each backward target is calculated from that solver's own next-stage approximant. No tabular optimal continuation is passed into either solver.

Neural cases: widths 16,32; one or two tanh hidden layers; seeds 27301,27302; 400 Adam steps per fitted stage at rate 0.01 followed by at most 150 L-BFGS objective/gradient calls, with no outcome-dependent retuning. Inputs are mapped to [-1,1], regression targets are centered/scaled using their own training values. The last-period policy can be computed directly from the known terminal payoff. Classical cases: all monomials of total degree at most 2 or 3, fitted by least squares with no exact-value labels. The action policy is greedy with respect to each method's own next-period approximant.

All 24 primary neural cases and six polynomial cases are retained. Resolution controls use d=4,L=5,width=32,depth=2,both seeds, plus both polynomial degrees. Every candidate policy table is written and SHA-256 frozen before any exact Bellman reference is computed for that model. Exact backward integer arithmetic then independently evaluates the optimal policy and each frozen candidate for every state and every restart time. Worst regret, exact rational witness, distribution, action disagreement, tolerance attainment at 0.01/0.05/0.1/0.5, and deployment-table bytes are reported. A compiled finite-state policy is the certified deployment object; it is not a floating-point neural execution certificate.

The tabular exact Bellman solver is reported as the strongest classical baseline, not hidden as an uncharged evaluator. Timings separately charge model construction, candidate generation, policy compilation/storage, exact reference generation and candidate verification. Shared reference cost is allocated in full for a standalone pipeline and separately amortized across a model's candidates. Peak resident memory and CPU affinity are recorded. Finite-graph certification scaling is not advertised as continuous-domain interval-Hessian scaling.
