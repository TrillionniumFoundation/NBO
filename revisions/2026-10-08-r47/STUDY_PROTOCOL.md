# R47 execution protocol

8 October 2026. This protocol is prospective relative to the new executions, not independent preregistration. Small algebraic and software-development checks are allowed and must be distinguished from the catalogue. Scientific changes after this commit require an explicit amendment before catalogue execution.

## Immutable baseline

Repository: TrillionniumFoundation/NBO. Address the complete R46 referee report at review commit 0bf1ff6060bb9211762f191b6ead306ae4725beb, reviewing c3930399e3b8267451096d0e70ea67f49510065e. Extend the existing Neural Bellman Operators article, title, author, theorem chain and applications. Do not replace it by the referee's suggested differently titled paper. Preserve every prior revision, review and adverse observation. R46 is the manuscript baseline, not R43 or R45.

## A. Direct values of the R46 policies

Use the frozen repetition-zero policies at EVERY common successful first crossing of targets 1/4, 1/8 and 1/16 in the R46 two-horizon, two-price catalogue. Compare all three unordered pairs of cone-witness, cone-nearest and spline-nearest. There are ten common economic-cell/target objects and thirty pair contrasts; repeated identical policy objects can share simulated paths but may not be omitted from reporting. The initial state is uniform on the entire original scalar state domain; innovations follow the original independent continuous uniform law. The estimand is the expected discounted cost difference of the deployed policies, not a difference of certificate upper bounds.

Use 262144 independent bin draws per distinct policy comparison object and common innovations between policies. Represent each continuous uniform draw by a uniformly sampled dyadic bin with 48-bit index and enclose all within-bin uncertainty. Use outward arithmetic and include all actor indices compatible with an uncertain state; no boundary path may be silently discarded. Report two-sided empirical-Bernstein intervals for endpoint random variables, conditional on the stated IID simulation model, with familywise alpha 0.05 across the thirty contrasts. A fixed pseudorandom seed provides reproducibility, not a proof of independence. Fix the comparison margin at 0.005 discounted cost units before these results; this is a numerical decision tolerance in the uncalibrated original cost normalization, not an empirically estimated welfare threshold. Report superiority, interval inclusion within the margin, and unresolved cases separately. A confidence interval crossing zero is not called equality. Report exact structural equality separately where appropriate.

Also reconstruct the complete R46 work-to-certified-bound staircase from ALL frozen rungs, not new targets selected for a favorable crossing. New clocks may not be added to historical clocks.

## B. Multidimensional constrained construction

Execute dimensions d=2 and d=3, horizons T=2 and T=4, and investment-price coefficients p=1/4 and p=1. The state domain is [0,1]^d. The scalar investment constraint is 0<=a<=b(x)=1/4+sum(x)/(4d). With cyclic indices and one common continuous innovation z uniform on [-1,1], use

F_i(x,a,z)=1/16+x_i/2+x_(i+1)^2/8+a/4+z/16,

c(x,a)=sum((x_i-1/2)^2)/(8d)+p*a^2/2,

g(x)=(1-sum(x)/d)^2+sum((x_i-x_(i+1))^2)/(8d), beta=15/16.

This is a coupled nonlinear investment laboratory, not a calibrated empirical economy. Verify domain invariance and every primitive modulus analytically. Use state grids N=(4,8,16) for d=2 and N=(2,4,8) for d=3; action fractions j/N, j=0,...,N, multiply the local capacity. Use continuous-law midpoint integration with M=2N bins and an explicit Lipschitz remainder. Both candidate generators form their own future labels: the witness-preserving Lipschitz envelope and conventional multilinear fitted-value iteration. Give the conventional candidate a valid own-critic residual and repaired-actor certificate. Charge fitting, integration, actor construction, numerical enclosures, failed rungs, serialization and all prefix work. Report every rung whether or not it crosses a target. Use the fixed target grid {j/32: j=1,...,32}, including capped failures.

Use three fresh isolated process repetitions per dimension/horizon/price/generator cell, fixed single-thread numerical libraries, and one available CPU when supported. Record environment, process clocks, internal prefix clocks and peak resident memory; do not claim CPU-frequency control. Store the defining node labels/actions, Lipschitz constants, numerical-query errors, all certificate components and checkpoint hashes.

## C. Representation and deployment

Compare the SAME stored cone-and-witness object in native min-plus form and in its explicit affine/ReLU circuit form. Use identical node labels, action witnesses, arithmetic contract, tie convention and query states. Mathematical representation equality is not a neural performance advantage. Report operator counts, discrepancies, selection allowances and clocks. Keep representation benchmarking distinct from independently reconstructed candidate generators.

Implement finite-acquisition policies with dyadic state cells at 12 and 20 bits. For an acquisition cell U, repair actions to the lower capacity over U; quantize the action downward to 20 bits, so feasibility holds at EVERY true state in U. Enclose floating score evaluation and charge approximate-index excess and state uncertainty to the policy bound. Compare with ideal exact acquisition as a theoretical reference, not an ordinary-hardware observation. Exercise interior states, capacity boundaries, grid boundaries and ambiguous cone/switchpoint states. Never equate small objective error with feasibility.

For the new multidimensional policies, direct common-path contrasts at the finest fixed rung use uniform initial states on [0,1]^d and the original continuous innovation law. Use 65536 bin draws, the 12-bit robust deployment, the same 0.005 numerical comparison margin, and a separate familywise alpha 0.05 across the eight economic cells. Report inconclusive intervals without redesigning the margin or sample size.

## D. Theory and release

Prove a robust-acquisition feasible-witness theorem and a complete complexity statement including covers, action nets, integration, circuit or envelope evaluation, state acquisition, selection, repair, precision and storage. Supply explicit tolerance/dimension dependence under the benchmark's effective primitives. Separate deterministic termination with sufficient resources from finite-cap attainment.

Before publication, audit raw records, original R46 checkpoint identities, finite-arithmetic containment, confidence arithmetic, the full comparison family and preservation of manuscript labels. Build the extended ECTA.tex, technical supplement and a point-by-point B1-B9/M1-M10 response. Materialize ordinary source files, raw evidence and PDFs on a fresh review-ready branch. Rebuilding the final source must not require an expiring artifact or reexecution of scientific clocks. Tests and compilation do not constitute journal acceptance or mathematical peer approval.
