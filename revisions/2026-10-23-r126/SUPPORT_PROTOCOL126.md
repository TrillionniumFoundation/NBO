# R126 complete-support finite computation protocol

This protocol is fixed before the new R126 economic census and before any new
support-solver numerical comparison. It implements a bounded, rationally
verified outer-cut calculation for the R125 complete-support information class.
It is not a claim of a new generic cutting-plane method or of neural-specific
representation power. No numerical pilot is used to select this study.

## Original information and exhaustive declared selection

Read only the completed, unchanged R126 primary file of all 1,584 decisions.
Select all 58 actor/online `fused_control` pools at the first fixed state
`(3/16,3/16)` and all 16 remaining online pools (two risks times eight states):
74 pools in total. Every pool is retained, including an empty support ledger or
a failed algebra calculation. This is a declared finite workload, not a random
population sample. It does not inspect protected R123/R124B outcomes.

The original continuous-risk model, root objective, fixed implemented future,
feasible interval and all already paid supports are unchanged. Global bounds
are the proved original `mu=2`, rational `L` and derivative cap `M=7`. Each
support's single slope variable is shared across all interpolation nodes.
All support anchors and both domain endpoints are included. Value boxes follow
from the derivative cap and original observed value bounds. Derivative boxes
follow from the original certified derivative intervals, strong monotonicity,
smoothness, and the cap. No fitted derivative can enter the information class.

## Fixed candidate and certificate computation

Candidate actions are the returned fused incumbent and exact capacity `A`,
deduplicated. The computational regret grid is `0,A/4,A/2,3A/4,A`, augmented
with the incumbent. These extra nodes are unknown variables in the same
information class, not new economic observations or free oracle queries.

For every grid origin and candidate target, compute the upper original
contrast in two ways. The strong conventional comparator is the smaller of
the exact globally capped derivative-envelope contrast and the original endpoint
level difference. The cap is the same proved M=7 available to the solver; the
endpoint lower bound also uses the saved original optimum lower bound. The
complete-support dual alone represents its declared support class; intersecting
with this separately valid original-model floor is an original-objective bound,
not a claim that the floor was encoded as a global conic constraint. The full-support solver retains that bound and intersects it with
the exact rational outer-cut dual bound. Thus unsuccessful dual proposals
cannot worsen a previously valid certificate.

The solver uses SciPy 1.17.0 HiGHS dual simplex. Its fixed budget is eight LP
calls per nonidentical contrast, each with at most 2,000 iterations. First
linearize every original convex constraint at the midpoint of its valid box.
After each solved LP, rationalize the proposed point to a dyadic grid `2^-36`,
clip it to the box, evaluate every original constraint exactly, and add up to
32 strictly violated tangents in decreasing exact violation order (ties follow
the serialized constraint index). All earlier cuts remain. Dual nonnegative
weights are rationalized at `2^-36` in the row-scaled LP and rescaled exactly.
All affine cuts and their box-residual corrections are then regenerated with
`fractions.Fraction`. No success flag, rounded solver objective or numerical
primal feasibility is certificate authority. Numerical LP failure is not proof
of inconsistent economic data. All failures and discarded iterations remain
in the raw record and charged work.

The exact quadratic cell envelope converts the pairwise contrast bounds to a
continuous-domain regret bound. Add the unchanged future-policy allowance
`delta=15/2^24` and intersect it with the stronger cheap terminal certificate.
Absolute objective width remains an independent gate. A candidate different
from the incumbent is classified as a certified improvement only if its
strict pairwise original-policy gain is positive, original regret is at most
`1/256`, and objective width is at most `1/8192`; the stronger regret target
`1/65536` is separate. This calculation never rewrites a primary policy or
retroactively relabels its success/failure.

## Independent authority, economic scope and costs

The separate standard-library checker imports no solver or inherited envelope
module. It rebuilds the finite box, original convex rows, exact tangents,
nonnegative multiplier sum and cheap comparator from the stored original
payload. It also checks the exact continuous cell maximization. This is
independent certificate algebra, conditional on source-bound economic inputs;
the separately implemented R126 original-economy audit supplies economic
checks. One does not substitute for the other.

Report every pool, every candidate, every refusal, all LP statuses and
iterations, cuts, exact arithmetic time, and whole-process clock. Original
paid support costs come from the newly measured primary fused prefix and are
added to the additional algebra as an explicit cost account. This sum is not
a freshly measured end-to-end wall clock, and reused support inputs are not
free information. Compare the full calculation with the strong cheap route
under the same already paid record. An expensive nonimprovement is a retained
negative result. Neither a tighter certificate nor a grid refinement alone
counts as a policy gain, population welfare estimate, or neural advantage.

The finite solver supplies valid upper bounds, not a claim of exact full-program
optimality. No primal matching witness is inferred for the economic pools.
Exact rational mathematical fixtures separately check boundary/interior
quadratics, degenerate `L=mu`, clipped conjugates, nonstationary duals and the
sharp `L h^2/8` regret interpolation constant. Their results are not additional
economic observations.

## Reproduction and failure handling

All code, the present protocol and imported source/actors belong to the public
R126 source freeze before execution. Use exclusive output directories.
Failures preserve their started records, partial output and elapsed work.
Scientific corrections after the freeze require a separately published amended
boundary and explicit attribution. Unfinished or unsuccessful outputs cannot
be called a successful original frozen experiment.

`python code126/support_campaign126.py --primary results126/primary-attempt01 --output results126/support-attempt01`

The independent checker then reads the exact generated `contrasts126.jsonl.gz`
and `pools126.jsonl.gz` and writes a distinct audit receipt.
