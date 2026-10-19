# R120 author mathematical construction and source-only review

Recorded on 2026-10-19 before the prospective R120 scientific freeze.

This note records proofs and read-only source inspection. It is not a numerical execution receipt, a build result, a CI result, or an external referee report. This agent executed no economic model, optimizer, fitting routine, certificate, scientific experiment, or typesetting command. The only Python command used by this agent read and hashed the two new LaTeX files and counted their environments; it imported no scientific source.

## Baseline and ownership

The complete R119 author source is 6250abfd317f3b2a56cb1303eb5ce78249bf4042, carried through final publication 82618f into the isolated R120 revision. This agent wrote only the authorized new mathematical files in revisions/2026-10-19-r120/new120 and this scratch audit note. R119 was not edited.

The economic problem remains the original two-date investment model: d=2; original nonlinear transition; original capacity; h(a)=a²+4a⁴; beta=15/16; continuous uniform innovations on [-1/32,1/32]; separately fixed nested AVaR levels 1/2 and 3/4; unchanged deployed terminal controller. Its actual root-policy correction relative to the original optimal continuation remains in [0,beta*2^-20].

Three projected support proposals at fractions 1,1/2,1/4, the completed-incumbent safeguard, original global lower witnesses, and gain budgets retain R108–R110 ownership. The common-risk density identity retains R111/R119 ownership. The distinct R112/R113 finite-anchor protocols are not renamed or represented as this experiment. Current critic fitting is unchanged; no action-aware training or neural convergence result is claimed.

## New mathematical content and boundaries

1. Theorem thm:modulus120 proves the original AVaR terminal-value gradient modulus

   M_alpha = 1413/128 + (15/16)*(127/16 + 19625*alpha/[20480*(1-alpha)]).

   Normalizing action by A(y)v handles capacity changes on a fixed interval. The proof includes tail movement, semiconcavity, original convexity, continuous gradients, and boundary switches. The original action continuation difference has innovation modulus E=(4/5)*M_alpha*abs(b-a). This particular constant is only claimed for d=2.

2. Theorem thm:paired120 intersects a valid paired Lipschitz midpoint interval with separately valid convex midpoint/secant intervals. Radius is E*sum(h_i²)/(4B), B=2R(1-alpha). With exact points and h_i<=B/n, width is at most min(2KRt/n²,ERt/n). Original additional smoothness strengthens it to min(min(2KRt,2M_alpha*R²t²)/n²,ERt/n). This uses the same already acquired values; no implementation change or new query advantage is inferred. Node errors, arithmetic enlargement, both tail deficits and one +/-beta*epsilon1 contrast allowance remain explicit. The difference is never treated as convex.

3. Proposition prop:pairinformation120 proves an upper algorithm with at most 4n+8 scalar function values and a lower interval-width bound min(KRt/[48(N+1)²],ERt/[12(N+1)]). A value of one chosen function costs one; paired values cost two. The lower bound is only for the stated generic convex K-Lipschitz, difference-E-Lipschitz class at a known fixed density. It is not a lower bound for the fixed parametric original economy with all its additional smoothness and formulas; it is not a full unknown-AVaR-tail contrast complexity result or a neural separation.

4. Theorem thm:tailtransfer120 proves

   k_a(q_u) <= (sqrt(kappa_b) + E*sqrt(alpha/[2*m_z*(1-alpha)]))²,
   with original m_z=181/64.

   The proof preserves constrained endpoint optimality. At an exact candidate tail, mismatch is quadratic in action distance. The staged algorithm retains and pays direct endpoint deficits, then intersects the incumbent upper bound with the transfer. This directly tightens lower-contrast refusal; it does not tighten the candidate term of the upper acceptance gate. The proof includes the exact integer/dyadic upper-square-root construction and its outward conversion check.

5. Proposition prop:safe120 gives uniform original-policy monotonicity conditional on valid outward premises and a completed statewise incumbent. Total gain is between the outward telescoped accepted lower gains and tau=1/256. Proposition prop:resolution120 gives finite refinement only above the complete tail/node/future margin and with separate original candidate qualification. The work bound is non-strict and valid even when c=0. Prop:futurefloor120 proves the sharp distinct-action correction interval [-delta,delta] for the stated information interface. Known optimal-future gain needs margin delta; a sufficient worst-case condition stated only in actual gain is 2delta. Same realized actions cancel exactly. None of these bounds establishes global policy-iteration convergence.

6. Proposition prop:independentopt120 strengthens independent fixed-action validation with original-optimum, regret and squared action-error bounds. Exact primitive gradients under a fixed feasible density and the e²/4 stationarity allowance give a global affine state support. Symmetric-bin integration and root action curvature two give a quadratic lower witness over the full original capacity interval. The Lagrange-support intercept c is kept distinct from any larger scalar fixed-state terminal lower value. Already paid lower witnesses may be combined only at the same original state/risk. The original actual-future allowance is added once to fixed-action upper values.

7. Proposition prop:population120 proves the prespecified conditional 95% family result for 64 independent initial-state draws, 48 gain groups and four thresholds. The declared population is the finite product-uniform 40-bit dyadic state law; 4,096 service observations do not become 4,096 independent states. One complete service is called separately per initial state. Internal innovation batching is allowed.

   Certified threshold counts are pointwise dominated by latent true-gain binomial counts. Monotonic exact binomial inversion therefore stays conservative even for incomplete or adaptive valid numerical enclosures. Missing independent validation can use [0,tau] but cannot be dropped or described as successful. Forty-eight exact rational bisections return a lower quantile bracket. The 192 event bounds use 1/7680 each; 48 two-sided mean intervals use a total 1/40. The fixed radius r=33*tau/128 has exact exponent1089/128, and a displayed positive Taylor argument proves its tail allowance. The two families use at most 1/20 total failure probability. Interval uncertainty is retained.

   Stored entropy bytes establish reproducibility. Independent uniform entropy, conditional on frozen actors/protocol, remains an explicit probability assumption rather than a conclusion from an operating-system log.

## Concrete pre-execution defects found and resolved

- An initial _tail_density call passed an interval into the inherited scalar constructor of constrained_gain. The staged source now passes the exact dyadic product tail.MZ*(alpha/16), consistent with the inherited implementation and proof.
- The inherited terminal compiler has a whole-batch fallback. Batched initial states could therefore couple the returned policies and invalidate the intended iid-state analysis. The prospective campaign now calls imp.service(state[None,:],...) for each initial state. The actual campaign source and its batch-size metadata were read to verify this correction.
- Independent mathematical challenge found the strict work bound at c=0. The statement now uses <= c*(2n_J-n0)+c0*(J+1), with explicit positive integer resolutions.
- The statistical proof was strengthened from asserting iid certified events to the valid domination by iid latent true-gain events, matching the conservative missing-validation implementation.

## Source paths actually reviewed

The source-only review covered code120/improvement120.py: original modulus, paired geometry and both action payloads, valid interval intersection, stage-cost factorization, both tail deficits, exact upper square roots, transfer intersection, unchanged-future allowance, original qualification, identical-action shortcut, accepted-gain accumulation and complete refusal/exhaustion.

It covered code120/independent120.py: exact tail mean, independently integrated state/action gradients, boundary multipliers, global support c, feasible finite-bin risk masses, all-action quadratic minimization, original regret/action error, one future-policy allowance, and same-state-only optimum sharing.

It covered code120/stats120.py: exact binomial polynomial comparisons, lower-bracket return, multiplicity, rational mean radius, complete sample identities, and conservative missing rows. Campaign source was read for singleton service calls and actor/entropy/state-stage ordering. No remaining mathematical blocker was found in these reviewed paths.

## Final new mathematical file identities

| Native R120 relative path | SHA256 |
|---|---|
| new120/policy_improvement_main.tex | 30cc48e2307b587977614caaa23598879f0ee80ab55414bea9da56a2a6508d3b |
| new120/policy_improvement_proofs.tex | ae2398ad13f9e11c3a2cf8038ea6523e58776e1238a204e9611527ed636fbd18 |

Read source snapshots included independent120.py SHA256 8b86260b41659ea2a73fd0a5666bd03cefd9228aff4867196b20913ba58dc808, stats120.py SHA256 61ea66a7d57e6501ff68c5866958e63aaeafa80ec1986bd9fb6f63f6d4b1594b, and independent94.py SHA256 a1a0e4ce5563d1105c3cea9eaad6678c609229446ba6794f7b8a7c03df01ebad. Improvement source was actively being finalized by its owner; reviewed mathematical paths included its ef0eeda2ed589e1b1a498241be60e293f26296a6bf9ec209cb3e0184abe0b26f snapshot and subsequent transfer delta. The prospective source freeze must bind its own final byte set and commit; this note makes no execution claim about those files.

## Independent challenge and remaining obligations

Peer /root/review_lineage independently checked the constants, query counts, lower construction, constrained transfer, full refinement margin, original-optimum witness, exact square-root enclosure, dominated latent-count proof and population family account. Parent /root separately checked the modulus, lower construction, transfer and independent optimum witness. This is independent derivation within the author workflow, not external authorship or formal proof-assistant verification.

Observed policy gains, rejection savings, runtime advantages, population positivity, complete-cost adoption and CI success remain matters for the actual frozen experiment and receipts. Neural advantage over equal hinge information and strong conventional alternatives, scalable higher-dimensional or longer-horizon decision service, empirical economic applications, improved knowledge of the unchanged future-policy correction and original-objective action-aware training remain substantive research obligations.

Classical binomial attribution was verified from Oxford's primary page:
https://academic.oup.com/biomet/article-abstract/26/4/404/291538
and DOI https://doi.org/10.1093/biomet/26.4.404 .
Clopper and Pearson (1934), Biometrika26(4):404–413, and the existing Hoeffding reference receive credit. Full proofs are supplied; these standard probability tools are not presented as new numerical-method contributions.
