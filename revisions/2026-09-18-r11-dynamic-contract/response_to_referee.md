# Response to the latest advisory referee report

**Revision:** R11, 18 September 2026.  
**Report:** `reviews/2026-09-18-econometrica-r9-r10-independent-harsh/referee_report.md`, pinned at `30548ad06852cc0a447dedf1e63cc9e7f79f6c06`.  
**Prior complete manuscript:** R9, `8c1e0472279fb66a2419b63b3e35df028ecfdd78`.  
**New branch:** `revision/econometrica-r11-dynamic-contract-response-2026-09-18`.

We thank the referee for distinguishing correct mathematical repairs from missing economic conclusions. The revision supplies new dynamic and institutional results rather than revising the recommendation by assertion. The complete main paper adds a central section, “Dynamic Adjustment and the Price of Commitment,” and the complete supplement adds S.14. The operator theory, two-stage primitive theorem, historical applications, unfavorable experiments, and earlier reviews remain intact. A source map is provided separately.

## A. The actual dynamic mechanism

### A.1. A two-stage example does not explain the eight-date direction

We agree with the distinction. The two-stage consumption-exposure theorem and its cardinal-tilt robustness are retained as separate results, including their adjustment directions and cost domain. They are not used as premises for the new dynamic result.

The new reachable-state transport proposition compares each negative-drift operating action with a feasible action having the same consumption and risky share and zero drift. Let the signed difference of discounted live kernels be D, and let certified upward-continuation bounds have midpoint v and radius e. The upper comparison is the current reward difference plus Dv + |D|e, maximized over the endpoint laws and benefit endpoints, with an explicit evaluation allowance. The surrender fee enters the continuation enclosure. Strict negativity eliminates the negative action. Backward induction on a support set closed under **all** feasible transitions, not merely under the selected policy, proves equality of unrestricted and upward-only values.

This is a verifiable dynamic sufficient condition. It charges current adjustment costs, boundary discharge, future consumption opportunities, wealth transitions, and stopping incentives through the same reward and continuation primitives. Neither a positive flow derivative nor the sign of an initial selected control is substituted for the continuation test. The interval recursion used to certify the condition does not assume that the optimal selector remains fixed over the parameter box.

### A.2. Directional tests, the state domain, and the adverse initial state

We freshly reoptimized all nine law/benefit contracts in the report with full, upward-only, downward-only, and zero adjustment. The initial equalities are reproduced. These nine points are explicitly described as diagnostics, not a continuum proof.

The new continuum result concerns x0=(2,1.25), one compulsory interval, and the joint box

| Primitive | Interval |
|---|---|
| Law probability | [0.12, 0.13] |
| Operating benefit | [0.424, 0.4245] |
| Surrender charge | [0.7999, 0.8001] |
| Long permission | [0.7999, 0.8001] |
| Short permission | [0.4999, 0.5001] |

The full feasible-support counts by date are 1, 30, 100, 203, 342, 495, 637, 735, and 833. At every reachable live state and all eight decision dates, the negative-minus-zero upper comparison is strictly negative. Its least slack exceeds 0.000070902 after the numerical allowance. The frozen proposals have nonnegative drift at every such node; this is checked, not presumed. Thus the new theorem proves upward sufficiency on a stated dynamic state/parameter domain, without extrapolating to the whole grid.

We preserve and freshly reproduce the alternative initial state (1.25,1.59375). In the nonpositive class at the central noncancellable contract, full minus upward-only value is 1.221130888309406 and downward-only minus zero value is 1.302731114145440, up to the reported replay tolerance. The continuation decomposition identifies the discharge margin: holding the full policy's first financial controls fixed, negative drift raises discounted next-settlement mass at the lower preference boundary from approximately 0.17589502 to 0.49750624. This is a settlement-lottery incidence, not a diffusion hitting probability. That state is outside the certified support tube.

### A.3. The class differential is decomposed, not renamed

The central first financial controls coincide across the adjusted and unadjusted comparisons. This permits an exact decomposition of each adjustment option into the gain from current drift evaluated at adjusted continuation and exposure to future adjustment value under the zero-drift action. The code verifies the premise and refuses to drop a financial-replacement term if it is not zero.

At the noncancellable center, the relative local component is approximately 0.0000503943 and the relative future component is 0.0003556734, adding to 0.0004060676. The common current adjustment cost is approximately 0.00498752; it is not the source of the class differential. With fee 0.80, the positive unadjusted class acquires an elective surrender option, reducing its exposure to future adjustment gains. The local/future calculations use the same stochastic economy as the class comparison and are independently reconstructed from selected controls.

**Locations:** Main Section 2.2 and the reachable-state transport proposition; Supplement S.14.1–S.14.2; `replication/r11/core.py` (`interval_up`, `dominance`), `run.py` (`directional`, `mechanism`); `output/directional.json`, `mechanism.json`, `dominance.json`, and `certificate_arrays.npz`.

## B. Pricing compulsory terms and guarantee capacity on the same footing

The zero-cost full-term alternative is now a result to be recovered, not an omitted competitor. We specify capacity cost C(E) paid by the agent and direct compulsory-term execution cost D(m) paid by the principal. Both use the separate utility numeraire. The principal chooses among all eight terms and sufficient financial capacities implementing a selected noncancellable allocation, with a stated selection among operating-policy ties.

For regime r, the minimum procurement cost is

P_r = min_m { [G(x0) - W^r + C(F*_r(m))]_+ + D(m) }.

The statewise threshold F*_r(m) is computed on the common feasible-support tube. It is not represented as a necessary threshold for reproducing only the initial value. The procurement condition is b A_r >= P_r, where A_r is delivered discounted service under the selected operating policy. At the exact threshold, continued operation is the specified best response among stopping ties. Fees 1e-5 above each threshold provide separate strict implementation tests. The threshold formula gives the infimum for a requirement of strict incentives; we do not silently equate weak implementation and strict attainment.

When participation binds, the choice minimizes C(F*)+D(m). When it does not, the grant increment from capacity is [z+C(E)]_+ - [z]_+, between zero and C(E), not automatically C(E). The proposition includes this qualification. With a freely selectable full term and D=0, the model recovers the referee's conditional dominance conclusion.

For the transparent theoretical technology C(E)=0.02 E² and D(m)=kappa(m-1)/8, the central economy chooses term 8 at kappa=0, term 7 at kappa=0.01, and term 1 at kappa=0.02, in both adjustment regimes. The short-term statewise capacities are approximately 0.77675422 and 0.81353318. The complete record reports every term's cost, signing grant, delivered service, selected class, and break-even principal benefit, not just the winning institution. These cost coefficients are explicit theoretical primitives, not estimated enforcement technologies.

Fees accrue to an external enforcement sector, and are inactive on the implemented allocation. No hidden fee revenue funds the signing grant. The result is an endogenous instrument choice **within the specified implementation technology**. It is not an unrestricted optimal mechanism or a claim that the active-surrender contract below is the selected implementation contract.

**Locations:** Main Section 2.4, priced implementation proposition; Supplement S.14.4; `run.py` (`institutions`); `output/institutions.json`. The earlier zero-cost table remains unchanged as the limiting comparison.

## C. Connecting inactive implementation, active surrender, and permissions

The revised paper explicitly separates three economic claims. The earlier fee interval [0.85,0.90] implements the original finite-menu noncancellable mandate with an inactive elective stop margin. The new joint box has a strictly valuable surrender margin in a particular constrained class. The position ordering is simultaneously evaluated over the permission intervals in that same box. These are connected through the same continuation primitives, not by combining independent favorable slices.

The new joint theorem gives the following outward-rounded intervals, already including 2e-7 per class difference:

| Comparison on the entire five-dimensional box | Bound |
|---|---:|
| Adjusted positive minus nonpositive value | [0.00018762, 0.00020240] |
| Unadjusted positive minus nonpositive value | [-0.00017930, -0.00012218] |
| Unadjusted positive class: surrender minus noncancellable value | at least 0.000034708 |

The relative adjustment option consequently exceeds 0.0003098. The third inequality is stronger than displaying a positive surrender exposure for one selected policy: every policy in the constrained positive class within that strict gap of its surrender supremum must have positive elective-surrender incidence. A policy that never elects surrender is feasible in the noncancellable economy and cannot attain the higher value.

The qualification matters: the **unconstrained** unadjusted agent chooses the nonpositive class in this region. We do not assert that this agent elects surrender. The economically active object is a counterfactual surrender option that enters the comparison between financial positions. The theorem does not treat an inactive fee dimension as an active stopping mechanism.

The proof holds a feasible lower policy fixed across all benefit/fee corners and all Bernstein coefficients before minimizing. It uses the smallest permissions for lower policies and the largest permissions for upper values. The signed transition-law correction or the count-information recursion supplies the law-parameter upper bound. Six independently reoptimized interior contracts are validation checks only. The finite first-date consumption/drift pairs, original proposals, continuous first risky share, and unchanged later menus are specified throughout.

All twelve joint fee/permission interventions were freshly reoptimized: both fee levels, the central and adverse law/benefit contracts, and each of the three permission pairs. At the center, expanding the long permission to 0.82 makes both regimes choose the positive class; expanding the short permission to 0.51 makes both choose the nonpositive class. The unfavorable fee-0.80 corner remains unfavorable. These cases are neither deleted nor claimed to contradict the earlier target-specific fee certificate. The new certified region is not claimed to be maximal.

**Locations:** Main Section 2.3 and joint economic theorem; Supplement S.14.3; `core.py` (`region`, `coefficients`, `upper`); `output/chord_certificate.json`, `count_certificate.json`, `stress.json`, `certificate_arrays.npz`.

## D. A central economic result that uses changing-law certification

The abstract, introduction, opening result section, and conclusion now organize the paper around continuation incentives, the joint financial/stopping decision, and the price of implementing operation. Generic participation and envelope identities are not presented as sufficient explanations. The new dynamic transport condition and its verified domain explain when downward adjustment can be eliminated; the joint value certificate establishes the class reversal and active counterfactual surrender; the priced implementation theorem compares institutions under common primitives.

The computational increment remains the signed cross-operator correction for repeatedly changing transition laws, compared with the sharper count-information construction. The affine reward-policy geometry and its relationship to optimistic linear support and successor features remain credited. The revised result needs bounds over a law continuum, not just reuse over linearly parameterized rewards with a common transition kernel. The paper retains the existing direct correspondence with Alegre, Bazzan, and da Silva (2022), as well as the information-relaxation and regional verification comparators. No exhaustive novelty claim is added.

Both regional upper methods are executed with the same target, policy bank, law endpoints, reward corners, and decision accuracy. The work account charges construction, endpoint optimization, and independent validation to each method and separates additional certificate work. The resulting coefficients happen to give the same reported three regional intervals; this is not a theorem that chord and count always coincide. Earlier full precision/work frontiers and structural or neural-free countercomparisons remain available and are not called new runs. Kernel payload is not labeled process peak memory, and no neural-necessity conclusion is drawn from this finite-array audit.

**Locations:** Main Sections 1, 2.5, retained transition-law/comparative-oracle/correspondence sections, and conclusion; `output/work_account.json`; executed summary and source manifest.

## Numerical targets, preservation, and a complete revision

The arithmetic audit derives a per-compared-value bound below the charged 1e-7 for the identified stored arrays. Difference certificates include twice that allowance; continuation enclosures and signed transport comparisons have their own pads. The first-date target is the piecewise-affine interpolation of deposited knot rows. Arbitrary caps are evaluated between bracketing rows, not rounded down to an available knot. Independent direct selected-control and first-date moment checks test this representation.

The initial three value signs would transfer to another target with an additional common error below 1.7354e-5 per compared initial value. We state this as the required budget, not as a measured constructor or diffusion error. Directional dominance requires a separate all-state transition/reward transfer argument. Last-bit replay is not a substitute for either obligation.

The new R11 branch contains new readable main and supplement sources, full compiled PDFs, proofs, executable science, coefficient/policy/support arrays, checks, and this response. The source-package workflow refuses missing science or failed certificates and commits its actual outputs. It does not label a source archive as a new paper. Every inherited file except the append-only revision index is checked against the latest review parent; all older index contents remain verbatim.

These are owner-commissioned advisory review and revision materials. No appointment, submission, acceptance, or editorial decision by Econometrica is asserted. The revised propositions, explicit domains, and reproducible evidence are submitted for the next substantive assessment.
