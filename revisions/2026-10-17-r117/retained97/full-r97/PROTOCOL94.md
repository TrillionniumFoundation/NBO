# R94: frozen continuous-risk investment revision

Controlling review: `bd2945b4b4e76b6a997dbcf7548f5fe24d3e92e6`.
Original manuscript: `d1d1fc1f2208023a65419a616bccae0e4cdf7aa4`.
Continuation baseline: R93, `8640884d3f645953c89578870416d7dd3c18382f`.

The title, author, original economic primitives, complete-policy optimum,
broader applications, adverse results, and every inherited active section
are retained. Editorial moves have an exact source-preservation map. The
new main argument concerns NBO construction, continuous-risk qualification,
and a matched prospective experiment, not a replacement topic.

## Amendment before evaluation

The R93 rule adds the risk-level index to three consecutive seed integers.
Consequently the second training stream equals the first calibration stream,
and the second calibration stream equals the first evaluation stream. R94
retains R93 unchanged and replaces that rule BEFORE opening any primary
stream. Use `PCG64(SeedSequence([2026101394, stream, risk_index]))`, with
stream 1 for training, 2 for calibration, 3 for evaluation, and 4 for fixed
supplementary construction diagnostics. This is a new domain-separated
protocol; no primary evaluation from R93 or R94 preceded this amendment.
A development smoke test used seed 31 and 64 states; it was not evaluation.

## Original model and fixed scientific menu

Use the original even-dimensional scalar-capacity investment model, original
uniform shock [-1/32,1/32], beta=15/16, two decision dates, and nested AVaR at
alpha=1/2 and 3/4. The primary dimension is two. Each risk level has 1,024
training states, 128 calibration states, and 2,048 evaluation states, sampled
uniformly on the 20-bit dyadic state grid. Dimensions four and eight receive
16 supplementary diagnostic states each and no primary inferential weight.

Fit exactly three convex continuations: 32 oblique ReLU features, 32 additive
linear-spline features, and 32 projected quadratic features. All have an
unrestricted affine part and nonnegative nonlinear readouts, identical label
rows, `lsq_linear` TRF/exact with tolerance 1e-10 and cap 1,000, and 30-bit
dyadic readouts. Feature directions are primitive-only and fixed by code.
Report effective rank: 32 features do not imply 32 independent parameters.
The fourth arm is an online conventional original-risk Bellman continuation,
not an additional learned model and not a free optimal-value oracle.
Training targets are computed from the actual terminal cost and original law.

The first action is proposed with 16 convex bisections and a 128-bin proposal
integration, then rounded down to 30 bits. A shared outward interval verifier
checks the entire feasible action interval via a feasible original-risk
witness and a quadratic supporting lower function. Innovation certification
starts at 128 bins and doubles to 4096 without changing the proposed action.
The own-continuation gap target is 1/64. Every failed target is retained;
failure does not silently substitute a different arm. The terminal optimizer
uses a separately paid original-law certificate with gap at most 2^-20.
All displayed bounds concern the continuous law; bins enclose innovations.
No discrete grid minimum alone is an original-action certificate.

Uniform continuation residuals are certified on a 32-by-32 state cover using
convex interpolation and global affine minorants. These are whole-cell
inequalities, not empirical residuals or a changed state law. Their cost is
paid separately. Continuum tail exclusions use previously unpruned original
value enclosures. Strict inequality is required; equality stays in the menu.
Entropic preferences remain analytical, not numerically validated here.

## Prospective economic inference

Choose the arm with smallest calibration mean cost-interval midpoint;
lexicographic arm-name ties. Freeze its identity and all fitted coefficients
before loading the independent evaluation stream. Report every pairwise
comparison, including comparisons not involving the selected arm. The
estimand is the mean, over the declared initial-state distribution, of the
original nested-risk complete-policy value. It is not average realized cash
cost, field data, money, or an estimated utility price.

The superiority threshold is zero. Equivalence and noninferiority use 1/16
in the original normalized cost units. The sample size never increases after
inspection. There are twelve fixed two-sided comparisons across both risk
levels. Report both a conservative Hoeffding interval and a simultaneous
empirical-Bernstein interval, with numerical and sampling parts separate.
The latter is the primary interval, declared before evaluation. It uses the
proved paired support radius `5/64 + (15/16)*(45/32 + 2^-20)`, and an outward
upper bound on sample variance computed from the full numerical intervals.
The logarithmic allowance is the rational upper bound 7 on log(960).
No observed extremum is substituted for a global support bound. Only paired
initial states are observation units; inner integration bins are not samples.

## Work, independence and release

The ledger charges labels, three fitting attempts per risk level, rank checks,
state qualification, serialization/loading, proposals, primitive/continuation
queries, risk sorting, all-action certification, actual policy evaluation,
tail-cut proof, output and whole-process memory/time. Common costs and per-arm
costs are separate; repeats and failures remain recorded. Single-machine
figures are not cross-architecture or energy evidence. No amortization,
monetary calibration or neural superiority is inferred from certificate width.

A separately coded Fraction checker reconstructs the original primitives and
continuous AVaR by a threshold integral, and checks whole-action witnesses,
equality cases, serialized fits and continuous-policy enclosures. This is an
independent kernel implementation, not an externally authored reimplementation
of all fitting and largest-vector code. The old two-control/two-shock horizon
frontier remains an independent obligation, never replaced by this scalar
experiment. Publication gates distinguish new tests, inherited replay,
source-preservation, clean document compilation, and visual inspection.
