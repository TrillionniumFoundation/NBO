# R62 prospective protocol: the original optimum and complete policies

The controlling advisory report is the R61 report at commit
08ca068d318ce159401b36655eccea1e05490d01. The immutable manuscript base is
19f17cef194b620cfbf9d33e7c78ee051a2dddf0. This protocol is written after that
report and before any R62 production result. It does not retroactively make
R60 or R61 prospective.

## Economic objects and fixed catalogue

The original even-dimensional cyclic investment primitives, price p=1 and
beta=15/16 are unchanged. The second-control extension is exactly the previously
specified capacity simplex with exposure columns (1/2,1/4) and (1/4,1/2),
running action cost a1^2+a2^2+4(a1^4+a2^4)+a1*a2/4, and an additional independent
uniform common-direction shock of radius 1/64. Setting a2 and that second
shock to zero recovers the original model, not a newly selected substitute.

Execute these five cells, including every rung and every failed target:

| State dimension | Controls | Horizon | Grid subdivisions n | Action subdivisions A | Shock bins per component q |
|---|---:|---:|---|---:|---:|
| 2 | 1 | 2 | 8,16,32,64 | 16 | 4 |
| 2 | 1 | 3 | 8,16,32,64 | 16 | 4 |
| 4 | 1 | 3 | 4,8,16 | 16 | 4 |
| 8 | 1 | 2 | 2,4 | 8 | 2 |
| 2 | 2 | 2 | 8,16,32,64 | 16 | 4 |

The shared all-state targets are 1/2,1/4,1/8,1/16,1/32. Budget exhaustion is a
result, not permission to add a rung. All endpoints retain curvature,
action-cover, quadrature, interpolation arithmetic and deployment allowances.
An initial-law improvement does not count as attainment of these targets.

Compare common lattice Bellman construction, pure trained ReLU proposals,
pure fitted quadratic proposals, and each fitted proposal augmented by the
same common verified fallback. Four fitting seeds are fixed at 6201,6202,6203,
6204. Use 512 primitive training states per date, 32 learned ReLU units and
120 optimization iterations as in the retained fitter. Training labels use
the generator's own previously fitted future. The proposal state partition
has 32 leaves, fixed by seed 551 before choosing a generator. Scalar proposal
witnesses use the retained exact native R61 recovery. Two-control proposals
use constrained SLSQP with a fixed deterministic multistart list, retain all
termination messages, and receive the same original-optimum postcheck;
SLSQP success is not itself a certificate or an exact-search assertion.

At each verification node a coarse-partition proposal is transferred by its
fraction of capacity and rounded down to a 1/4096 action quantum. The executed
policy is the multilinear interpolation of these actual feasible nodal actions,
with lower-state 40-bit acquisition and downward 20-bit action rounding.
This is an explicitly new implementable actor contract. It is not a claim
that the discontinuous R61 actor has been left unchanged. Both pure and guarded
actors are preserved, rather than reporting only the successful guarded one.

## Mathematical and timing endpoints

Use the convexity and coordinate-semiconcavity bounds of the R62 theorem.
Grid-node Bellman lower values include the continuous-action covering loss;
upper values correspond to actual proposed actions. Midpoint samples of shocks
are accompanied by analytic continuous-law quadrature allowances. They do not
replace the law by discrete shocks. Actual-policy suboptimality is obtained
from the nodewise optimal-advantage allowance, barycentric transfer, acquisition
and rounding, and a complete finite-horizon recursion.

Charge each method its own primitive fitting/proposal work, its complete
verification/serialization work, and the entire shared reference construction.
For a rung, charge every earlier executed rung. Report cold compilation and
post-selection inference separately and also in complete-release totals.
Shared work is deliberately charged in full to each method. The finite target
frontier is reported for the actually executed catalogue, not an unexecuted
optimal stopping schedule. Machine frequency and physical architecture are
reported as observed; no controlled frequency or hardware-counter claim is made.

The four seeds define a finite reliability catalogue. Report its attained
fraction, not an estimated probability over unknown future tasks or seeds.
Failures and unresolved cost comparisons remain in the tables.

## Direct cost and economic decision

For every task, compare all final-rung policies on 65,536 fresh common paths,
including zero investment. The initial law is uniform over the whole state
cube. State and innovation bins have 40-bit resolution; outward path
propagation encloses every continuous realization in those bins. A single
family budget 1/100 covers at most 512 prespecified bounded empirical-Bernstein
intervals across the five cells, all four seeds and all returned actors. Gains
are paired differences; policy identities are exact zero contrasts. No negative
path gain is clipped. The deterministic model support is charged to inference.

Report every pure/guarded fitted-versus-common contrast, every guarded-versus-
pure contrast, and every policy-versus-zero gain. The break-even installation
fee range follows from these paired intervals and remains in normalized model
units; no empirical calibration is invented. A change in certificate or nodal
witness does not by itself identify a policy-cost gain.

## Freeze and publication

Commit ordinary source and SOURCE_FREEZE62.json before running the first
production rung. Preserve source hashes, fitted weights, training labels,
solver records, nodewise policies, lower/upper references, method-specific
upper advantages, all-state recursions, path endpoints and clocks. Verification
fixtures are disjoint from production and do not supply economic observations.
The new ordinary publication build does not retrain or resimulate. Recheck all
inherited regression tests and label preservation, generate tables from recorded
outputs, compile all seven inherited document roles, and rebuild from a clean
archive before updating a review-ready branch. No old branch is force-pushed.
