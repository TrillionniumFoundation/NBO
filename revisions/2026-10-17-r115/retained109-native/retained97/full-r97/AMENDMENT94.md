# R94 pre-evaluation completion of the common accuracy comparison

This amendment is fixed before the first primary training, calibration or
evaluation stream is opened. It does not change the four arms, fitting rule,
feature budget, selector, primary sample sizes, streams or inference margin.

An own-continuation gap of 1/64 is not a common original-optimum policy-loss
accuracy. In addition to that qualification, every returned first action now
receives an all-original-action lower witness for the original Bellman value,
using the analytically integrated original terminal problem. Subtract this
lower bound from the actual complete-policy upper cost. The common
original-optimum loss target is 1/16 at every queried initial state. Retain all
failures of either target and all actions, not only successfully certified
rows. Extra integration refinement can sharpen a lower bound, but cannot
change an arm's action or silently replace an unsuccessful policy.

The conventional online-risk-DP arm reuses its already paid original lower
witness. A fitted arm pays for one additional original-continuation witness
calculation at its proposed action, with a 128-to-4096 innovation ladder if
needed. The ledger explicitly includes that extra original-optimum work.
The policy-cost evaluation, inference rule and common terminal controller are
unchanged. These are pointwise certificates for every reported query, not a
claim that a finite catalogue alone verifies every continuous initial state.
The separate whole-state residual cover remains reported for that purpose.

The complete terminal controller is explicit: it receives a downward 40-bit
state observation, accepts a floating proposal only through an outward
all-action gap at most 2^-21 at that observation, and otherwise uses an exact
rational bisection fallback. The original-state transfer adds less than
30*2^-40, so its full error is below 2^-20 everywhere. The policy-value
integrator encloses this entire controller, including sensor and fallback,
without treating integration midpoints as the only possible future states.
The independent checker does not import this rational fallback.
