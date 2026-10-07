# Pre-execution amendment and development disclosure

This amendment precedes every execution in the R45 service catalogue. No study outcomes have been used to change the catalogue, budgets, targets, or stopping rule.

The preliminary protocol wrote the transition intercept as 1/16. At x=1, a=1/4 and z=1/32 this gives 33/32, contradicting its claimed invariant state domain. The corrected primitive is

F(x,a,z)=1/32+(11/16)x+(1/16)x(1-x)+a+z.

Its derivative in x lies in [5/8,3/4], and its extrema on the declared state/action/innovation domain are exactly 0 and 1. This is a primitive-domain correction, not a result-dependent calibration. The original protocol is retained verbatim with this amendment controlling the intercept.

Before execution, exact-arithmetic regression testing also found a scalar NumPy cell-index update that did not propagate through a reshaped scalar at a non-dyadic PWL knot. The evaluator now uses an explicit mutable ndarray for the checked cell index. The failed test log and its machine-readable summary are retained in the revision's audit directory. The same non-dyadic-boundary test passes after correction. A generic sampled-residual assertion was replaced with an explicit Lipschitz tent counterexample rather than counted as meaningful coverage.

Two N=16, horizon-2, price-1 development rung checks, one per method, were used to exercise interval integration and serialization inputs after the tests. They are not isolated full-catalogue services and are excluded from all timing and attainment summaries. The declared 24 services will be fresh process executions after source freeze. No targets, ladder entries, prices, horizons or method selections have been changed.
