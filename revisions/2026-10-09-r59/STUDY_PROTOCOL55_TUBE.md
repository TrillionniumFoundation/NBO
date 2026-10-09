# R55 signed-sensitivity extension protocol

This extension is motivated by the completed R55 primary cache study, whose
nonterminal comparisons were often blocked. It is not claimed to have been
specified before those primary outcomes. The primary study, its interrupted
controller attempt, the corrected controller's 66 complete services, and the
learned-null study remain unchanged. Freeze this protocol, tube55.py,
execute_tube55.py, tests_tube55.py, and the common source-freeze identity before
any extension production or fresh cost inference.

## Mathematical and implementation change

For the globally zero installed policy, compute outward forward state tubes and
backward state-gradient tubes under the original nonlinear drift, stage cost,
terminal cost and complete innovation support. The drift is coordinatewise
monotone. Evaluate its lower and upper endpoints before adding the innovation
interval. Its sparse Jacobian propagates cost gradients backwards. This
constructs a signed interval for the expected continuation change along the
segment from the incumbent action zero to each proposed action.

Intersect this interval with the independently valid original residual/value
cache advantage. A disagreement must stop acceptance. The sensitivity tube is
used only when the complete incumbent is globally zero. Any changed acquired
actor is discontinuous, so later passes use the generic original cache unless
the complete incumbent remains zero. Do not differentiate a cellwise constant
actor while silently dropping its boundary jumps. The signed tube and the same
fallback are supplied to every method, not only to the neural generator.

The original nine robust candidates, generator-specific tenth proposal, eight
continuous-action lower covers, strict incumbent-preserving rule, acquisition
partition and reconstruction rule are unchanged. Retain both base and tube
intervals for every candidate and cover, their intersections, extra strict
candidate admissions, actual changed actions, all datewise directed gaps, and
tube state-row and Jacobian-coordinate counts. An interval reduction is not
itself a new policy-cost observation.

## Prospective design

Use exactly the primary tasks (d,T)=(2,2),(4,4),(8,6), targets q=9/10 and 49/50
of expected zero-investment cost, and two resource stages (256,32,4) and
(1024,128,8) for training rows, non-tensor leaves and innovation bins.
Every task has trained ReLU, quadratic and ExtraTrees Bellman generators; d=2
also has the original compiled witness and tensor FVI. Three isolated sequential
processes repeat each method/task/target with identical seeds and rotated order:
66 services in total. Training seeds and hyperparameters are unchanged so that
the candidate construction can be compared directly with the primary study.

Fresh inference seeds use the distinct string prefix NBO-R55-TUBE-INFERENCE.
No primary path stream is reused. At each stage the cumulative looks are
4096,16384,65536, with the same first-attainment rule: stop at nonpositive
upper J(policy)-q J(zero); move to the next construction stage at a strictly
positive lower endpoint or exhausted inference budget; after the last stage
return budget_exhausted unless the target has been certified. No further stage
or look is computed after success. All failed/exhausted records remain.

Each method pays its own primitive construction, training, actor acquisition,
residual cache, signed tube, path evaluation, inference, storage and durable
outputs. The external driver records complete process clocks and immutable
checkpoints. Affinity and single numerical-library threads are enforced;
frequency is recorded where available but not controlled. Three repetitions
measure timing variability, not a population of independently trained objects.

## Coverage and reporting

This is a separate finite inference family with alpha=1/100, maximum2048
intervals, logarithm upper bound14 and at most1188 planned interval evaluations.
The original outward empirical-Bernstein endpoint formula is retained. The
same family event covers cost, target contrast and gain at all declared looks.
Training-independent fresh stage streams justify conditional coverage; common
streams across methods and deterministic timing repetitions do not create
independent observations. All original-bin and pseudorandom-model qualifications
continue to apply. The primary, learned-null and extension family union error
is at most1/100+1/200+1/100=1/40.

Publish every service result and common economic target, whether attained or
not. Compare complete work within each task's controlled runner, and do not
interpret cross-runner clocks as a hardware-controlled ranking. Show whether
new changes occur before the terminal date. Report actual signed gains and the
full replacement-fee interval in normalized model units. No empirical fee
calibration, universal neural superiority, fixed-accuracy dimension-free claim,
or learned-model robustness beyond the specified exposure uncertainty is
presumed.

The sensitivity construction is mathematically representation neutral. The
newly trained neural critic and its analytic Bellman expectation are a distinct
implementation contribution; any numerical advantage must be established by
the complete observations, not inferred from the name of the representation.
