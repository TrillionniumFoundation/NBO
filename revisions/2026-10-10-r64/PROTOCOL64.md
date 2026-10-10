# R64 prospective protocol: certificate-gated Neural Bellman queries

Controlling review: R62 report, commit eb02fdb321fe6f26de9caa3afcbe2f84531faef2.
Original reviewed paper: cfecc5ffcdeb836b1c70e9b98d1dc87f6f8cd097.
Completed predecessor services: R63 commit 7128155b146d647adc39b0accd1ba483877853cc.
Neither predecessor source, measured record, manuscript nor branch is modified.

## Question and fixed scientific design

Does asking for a learned query only after an accuracy certificate fails reduce
work relative to unconditional insertion, and does it improve complete work
relative to a strong conventional parabolic search? The latter is not presumed.
A fitted proposal changes the location of a necessary query only if it belongs
to the protected central half of the current lowest-minorant interval.
Certification uses original-law Bellman brackets, not the fitted output.

Keep the original scalar investment economy, beta=15/16, cyclic bilinear
transition, state-dependent capacity, and continuous uniform innovations.
Tasks (dimension, horizon, workload rows) are (2,2,128), (8,2,128), (16,2,128),
(8,3,32). Accuracy contracts are 1/32 and 1/128. Methods are conventional
adaptive parabolic search, bisection, unconditional ReLU insertion, gated ReLU
routing, unconditional quadratic insertion and gated quadratic routing.
Each learned method uses BOTH seeds 6401 and 6402; each exact service has TWO
isolated-process repetitions. There are 160 services. No selection of successful
seeds, tasks, tolerances or repetitions is permitted.

Models use the retained R63 architecture, 96 training states, original nested
Bellman-generated labels, feature map, L-BFGS caps, quadratic regularization and
boundary replacements. All labels and fitting are independently paid by each
service. Model identities must agree across insert/route variants for the same
seed, task and repetition. Engine code imports pinned original primitives.
Training seed 999 and named states may be used for engineering checks only.
No production workload is executed before the source freeze is pushed.

## Objects and endpoints

The returned controller is the complete callable query algorithm with its
supplied fitted model, not the pure fitted action. No conventional action table
or whole-domain lattice is built. Every returned action is downward-rounded to
32 bits BEFORE evaluation. Observations are acquired downward to 40 bits; the
uniform policy theorem accounts for the policy's own future at every date.

Primary timing: parent-observed wall time from child launch through imports,
label construction, fitting, deployment, exact workload costing, fsynced arrays,
summary, final clock, process exit and join. Each child has fixed single-CPU
affinity and one numerical-library thread. CPU frequency is uncontrolled.
All services, both repetitions, all warnings and all failure records are kept.
Raw Q-query counts, training Q-query counts, routed and declined predictions,
prediction-free returns, peak RSS, maximum live batch and state-table nodes are
separate outcomes. Exact-rational recovery is separately counted.

Reliability estimand: return count and worst measured complete work over this
finite initialization catalogue. Workload rows are not optimizer replications;
no population training probability or hardware-independent clock claim is made.

Initial states and innovations form a fixed dyadic workload generated with
seed 640000+101*d+T. Eight named boundary initial states replace the first eight
rows. Original true states and path costs are propagated exactly as Fractions;
only observations and actions are quantized. This workload includes boundaries
and finite shocks: its average is NOT an IID estimate under the continuous law.
No new independent continuous-law policy-cost observations are claimed.
The original-law guarantee comes from the uniform theorem, not the workload.
R62's adverse pure-policy continuous-law comparisons remain unchanged.

## Freeze, audit and interpretation

Freeze this protocol, query64.py, science64.py, tests64.py and gated64.tex,
plus the inherited R63 freeze, before production. A scientific-source change
requires a new freeze and a fresh full execution; no old clock is retimed.
Audit every saved trace, exact rational trajectory, source/record hash,
feasibility check, local gap, uniform budget and complete catalogue membership.
Check repeat identities and matched model identities. Re-query every recorded
observation to validate the saved endpoints and actions without retraining.
Those replay calls are verification work, not new scientific observations.

The publication preserves the full R62 main article and supplement as complete
development companions and retains the original broader applications. The
active paper keeps the NBO title, original constructive core, model and Bellman
accuracy objective, but removes chronological duplication from its reading
path. A content-location map must cover every inherited main/supplement label.
No tensor-free multi-control execution, stochastic optimizer theorem, empirical
calibration, neural superiority or unmeasured amortization is predetermined.
