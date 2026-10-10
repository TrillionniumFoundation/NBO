# R63 prospective protocol: state-grid-free Neural Bellman queries

The original scalar investment economy, beta=15/16, cyclic bilinear dynamics,
capacity c(x)=1/8+mean(x)/8, stage and terminal costs, and continuous uniform
innovation law are unchanged. The controlling review is R62 commit
eb02fdb321fe6f26de9caa3afcbe2f84531faef2, reviewing
cfecc5ffcdeb836b1c70e9b98d1dc87f6f8cd097. Old policies/results are immutable.

## Primary object

A complete callable policy returns a 32-bit downward action at the 40-bit
acquired state. At every date it requests a certified bracket for the ORIGINAL
continuous-action Bellman value and a feasible action whose true-optimal-future
Q value lies below that bracket's upper endpoint. The local tolerance is half
the requested full-policy tolerance divided by the discounted horizon sum.
Theorem query63 accounts for the policy's own future and acquisition. There is
no stored state lattice and no precomputed common policy at the queried states.

The learned arm predicts an ACTION query from Bellman-generated training labels;
it is a new NBO selector implementation, not a relabeling of the unsuccessful
pure value-fit actors in R62. Prediction weights have no role in lower bounds.
All arms share the same exact-law terminal derivative certificate.

## Fixed comparison

Task cells: (d,T,path count)=(2,2,128),(8,2,128),(16,2,128),(8,3,32).
Accuracy contracts: 1/32 and 1/128. Methods: curvature-adaptive parabolic bounds;
bisection with the same bounds; trained one-hidden-layer ReLU proposals;
full quadratic proposals on the same state features. Learned seeds: 6301,6302.
Every exact task/target/method/seed service runs twice in an isolated process.
This is 96 services. No failed service, warning, or exhausted cap is suppressed.

Each fitting service uses 96 independently generated training states, with
specified boundary replacements. Labels use q=2 conditional quadrature and
bounded floating minimization of the original nested Bellman problem. These are
unverified training targets, not certificate endpoints. A 24-unit ReLU network
is fitted by capped L-BFGS (160 iterations/2000 function evaluations); the
quadratic arm uses ridge-regularized least squares with all cross terms.
No statewise fallback policy is trained, stored, or queried. Fitting and all
training labels are charged to each complete service. No validation-state
selection or successful-seed selection is performed. Warnings are retained.

## Work and reliability endpoints

Primary endpoint: complete parent-observed process wall time, from launch
through imports, training, deployment queries, exact workload costing, durable
arrays/JSON, final clock write and process exit. Each child is pinned to one CPU
and BLAS/OpenMP thread counts are one. Frequency is not controlled. Report both
repetitions, all seeds, process peak RSS, training nodes, Bellman Q queries,
terminal queries, shock descendants, maximum working batch and stored state
nodes. No residual time is allocated across methods after execution.

Reliability estimand: deterministic finite-catalogue certificate-return count
and worst recorded work across BOTH declared seeds, not a population probability
of neural optimizer success. Optimizer convergence and a successful certified
service are different events. The proof tolerates an arbitrary prediction;
floating precision/cap failures invoke separately counted exact-rational queries. If that exact fallback cannot meet the declared action-precision condition, the service fails without a certificate.

## Digital deployment workload versus the continuous-law theorem

Initial states are fixed 20-bit dyadic vectors. Eight named boundary states are
included. Innovation streams are fixed 20-bit dyadic values in the original
shock support and shared across all arms. Exact rational state propagation and
cost evaluation are used; only observed states and implemented actions are
quantized. Store every observed state, selected action, Bellman bracket, local
gap, fitted-witness flag, and every exact path cost. The workload is deliberately
NOT an IID sample from the original continuous law because it includes boundary
paths and uses finite dyadic shocks. Its mean is a finite-workload diagnostic,
not a confidence interval for original expected policy cost. No new independent
continuous-law cost samples are claimed. The uniform policy theorem supplies the
original-law guarantee; the unchanged R62 study retains its direct cost evidence.

## Validation and release

Before production, run exact rational boundary, derivative, quadrature,
semiconcavity, capacity, action-rounding and exact-rational recovery tests. Engineering tests
use seed 999 or fixed named states, not the frozen workload generator. Freeze
this protocol, query engine, service script, tests, theorem and imported sources
before any production service. Scientific code changes require a new freeze and
fresh complete execution; an old measurement is never retimed or overwritten.

The audit independently reconstructs all exact workload trajectories, verifies
all true-state feasibility checks and every recorded endpoint gap, checks
same-seed repeat identities, and re-evaluates original Bellman brackets on fixed
first/middle/last records. Retain old R62 adverse findings and old manuscripts.
No claimed neural dominance, sparse-grid execution, stochastic training theorem,
calibrated welfare gain, or broad nonlinear-preference extension is predetermined.
