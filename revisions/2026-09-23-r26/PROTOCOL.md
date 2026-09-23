# R26 local execution protocol — 2026-09-23

Source review: R24 head `0eb0400ae311333fb77826ef9e2f067718926ae8`.
Reviewed manuscript: `14ce582e188f437cc8d99f310edd4f06515936a4`.
Imported evidence, not generated here: R25 science artifact 10742814762,
result commit `c78d934c0b3b8d346a40c7ddcaf415e167462265`.
Written locally before the executions below, after inspecting R25 outcomes.
This is NOT a remotely preregistered protocol. Keep original title, author,
economy, full-domain 0.01 objective, and every inherited source file unchanged.

## Certification-coupled optimizer stress test
Fresh diagnostic seeds 26101 and 26102; original economy at (0,2,1.25), k=2,
16 financed slabs; orders (8,16); unchanged stopped-payoff checker.
Neural Adam, direct Adam, R25 moving transport; base rates 0.08,0.32,0.32.
Three synchronously checked blocks: 200 calls at base rate; 50 at deliberately
aggressive rate 20.48; 100 at base/2 after stress rejection, else base.
This is a rollback stress test, NOT a tuned frontier. Accept strict certified
payoff dominance only. Rejection restores economic coordinates, carrier/network,
first/second moments, and counters. Save and hash complete states.
After stress rejection also run one separate uncoupled shadow continuation
for 100 calls at the SAME recovery rate from the rejected state. Certify it and
record trajectory difference. Charge shadow cost separately. Retain failures.

## Second-order verification of fixed stochastic-reference actors
Use exact R25 stored neural policies 25201 and 25202; no retraining.
Keep inherited outward binary64/rational-Taylor arithmetic unchanged.
Bound action error by the minimum of the prior centered first-order enclosure
and a centered second-order enclosure. Differentiate every layer with interval
first/second jets. Covers (4,16,8),(8,32,16),(16,64,32), in that order; stop at
first full-domain regret upper <=0.001, else keep final failure. Store every
attempt's full cell arrays. Compare bounds at matched covers. Historical CI
times and local times are not controlled same-machine speed comparisons.
The degree-eight direct comparator is fixed, not refitted. Use exact-rational
Bernstein bounds for x P((x-1.25)/0.75)-1 on 64 dyadic x-cells. Portfolio error
is exactly zero algebraically. Convert rational extrema outward and apply a
directed discounted horizon. This avoids unrounded derivative coefficients.
No changed policy or neural-efficiency advantage is inferred.

## Theory and checks
Prove precision-adaptive payoff dominance with an undecided outcome, a
certified derivative-free poll theorem under explicit smoothness/oracle
hypotheses, and centered-jet/Bernstein certification. Separate hypotheses from
instantiated facts. Check symbolic Hamiltonian completion, automatic derivatives
(diagnostic only), exact Bernstein identities, cover/hash completeness, rollback
identity and preservation. Do not infer stopped-gradient accuracy from secants.
