# R119 final mathematical and PDF audit

## Outcome and exact scope

The current new proofs remain coherent under their stated assumptions. No new mathematical defect or material page-layout defect was found in this final read. This is an author-side human audit of the actual files below, not formal verification, a new referee report, a scientific rerun, or a claim that every preserved historical theorem is correct.

The audit actually opened rasterized page images for **51 physical pages**: supplement pages **40–74**, main manuscript pages **21–29**, and development companion pages **6–12**. This includes the retained Brownian bridge, every new supplement proof, the main active-tail and bounded-service statements, and the original-formulation corrigendum. No claim is made to have visually inspected all 520 development pages. The saved contact sheets and page rasterizations identify what was viewed; the JSON receipt records their hashes.

| Reviewed PDF | Pages | Bytes | SHA-256 |
|---|---:|---:|---|
| `build/ECTA.pdf` | 42 | 313,011 | `a7a66d2d6693a759cbbbfc34ff384264d40e953bdc7b21286194f6f6d90dbda1` |
| `build/supp.pdf` | 74 | 432,898 | `f1604b74f9b589d9ccd1349236c0a54f719430400209e054415249cb80c20067` |
| `build/appendix.pdf` | 520 | 1,700,769 | `a6642444c61791f0eeab429cd4bab8842c09941a580f634ef76bf288cae28fae` |

All three current build files matched these saved snapshots when the receipt was made. The three build logs contain zero overfull boxes, undefined reference or citation warnings, multiply defined warnings, missing characters, or LaTeX errors. The ECTA class's ordinary font-shape substitutions remain: three font warnings in each of main and supplement, and 222 in the long development companion. The inspected images show no resulting missing text, clipping, overlapping equations, or unreadable displays. Draft line numbers are intentional.

## Mathematical dependency chain

| Current result and location | What the audit checked | Remaining boundary |
|---|---|---|
| Supplement Proposition 2, pages 43–47 | Compact continuous Bellman minimization, the explicit Borel kernel hypothesis and nested closed-ball selection proof, finite-horizon uniqueness, recursive policy validation, and correctly scoped terminal stability. | Standard foundations, explicitly not a novelty claim; arbitrary singular recursive utility requires separate assumptions. |
| Supplement Proposition 3 and following discussion, pages 47–53 | Original transition domain invariance; joint curvature retained through the affine capacity graph; state modulus `(4−5β/4)/d`, innovation modulus `181/64`; unique constrained actor and capacity-envelope term; implemented rounding and unchanged terminal allowance; complete derivative of the half-squared residual. | No convergence theorem for arbitrary training dynamics, no derivative through a rounded actor, and no convexity assumption on the implemented future-policy cost. |
| Supplement Proposition 4, pages 53–55 | The stopped Itô/BSDE derivation retains the actual terminal and lateral discrepancy and the separately stated original Brownian driver. | The bounded Lipschitz Brownian bridge does not make singular Epstein–Zin preferences, general NDU or a fully coupled FBSDE identical to the nested-AVaR investment objective. |
| Main Theorem 9 and supplement section 15, pages 55–58 | Atom-safe active-tail representation; the midpoint of the **final** bisection bracket; ordered secant-slope variation; full localization query count; retained indistinguishable chord lower bound; uniform asymptotic order scoped to `N≥32`. | Exact scalar point information is distinct from formula access, noisy signs, bit complexity, multivariate tractability and neural-specific representation claims. |
| Main Theorem 10 and supplement pages 58–61 | A feasible, possibly nonoptimal tail cut; outward strong-convexity defect; global original-`V1` supports under a fixed density; full feasible-action minimum with slope uncertainty; unchanged `ε1=2^-20`; paid precision and dated recursive allowances. | Better information about an unchanged policy does not improve its economic cost. A finite ladder may require the original fallback. Conditional allocation is for a declared graph and cost model. |
| Main Proposition 11 and supplement section 16, pages 61–68 | Exact zero-mass omission, dyadic representability, shared defect cache, bounds of 30 outward and 16 floating preliminary payloads, all rejected work and fallback, and the packing bijection with a singleton innovation axis. | These are preliminary information bounds. Batching can change valid intervals and fallback behavior. Complete elapsed cost and returned-policy comparisons require the separately executed records. |
| Supplement Theorem 5 and Proposition 6, pages 68–73 | Both dual-witness slack signs; atom-safe hinge remainder; one `βε1` allowance on each contrast endpoint; signed recursion with the original reference penalty; near-active restriction without attainment; nonexpansiveness only for a fixed retained kernel set. | Frozen R111/R112 research obligations retain attribution and their separate execution status. The proof is not a retroactive completion of those numerical episodes. |
| Development Appendix B, pages 6–11 | The original false joint-loss optimum, residual-only viscosity selection, incorrect portfolio/recursive-utility normalization, squared stochastic-trace bias, preference-state domain/sign, temporal-self deviation and Cournot interpretations are explicitly corrected. | The displayed diagnostics do not regenerate the original application experiments or establish a general equilibrium or global singular-utility verification theorem. |

The main text, supplement and development companion distinguish these mathematical roles. The historical incorrect statements are preserved as historical material and expressly excluded as premises for current results.

## Source changes inspected

The current active-tail main/proof, foundation main/supplement, coupled main and original-correctness sources exactly match the versions previously read and independently challenged. The current bounded-prelude main statement exactly matches the review-lineage draft.

The only differences in the compared proof drafts are layout changes. In `budgeted_tail_proofs119.tex`, two long displays were wrapped in `gathered`; every definition, coefficient and inequality is unchanged. In `coupled_proofs.tex`, a chained lower/upper inequality was split into two aligned inequalities, with the first direction correctly reversed to write the risk difference above the same lower bound. Its retained kernel sets, both penalty formulas and all quantifiers remain unchanged. The exact diffs and both source hashes are retained in the JSON receipt.

The final review also read the current packing proof and policy-improvement/stopping section. They do not claim that packing changes the original objective, that a query bound proves lower elapsed time, that an upper bound on forgone gain guarantees a discoverable improvement, or that a residual-fitting derivative is the utility gradient under an arbitrary sampling law.

## Claims that still need their own evidence

The method-neutral information theorem and original-policy certificate do not establish neural-specific superiority over conventional representations with identical information and features. The complete-cost comparisons must retain the conventional winners and every adverse phase. The exact point-query theorem does not establish a bit-cost optimum. The deterministic state and seed catalogue does not support population or calibrated adoption claims. Action-aligned training, broader matched-rank and acquisition frontiers, longer learned horizons, multivariate continuous-risk information, and the retained original applications remain substantive research requirements.

No scientific experiment, exact preflight, timing comparison or optimizer run was repeated for this audit. Only source, auxiliary and log reads; hashes; PDF extraction; rasterization; and human image inspection were performed. No manuscript source or frozen scientific source was modified by this audit. CI success is not asserted here.

## Portable receipt

`FINAL_PROOF_QA119.json` binds the exact PDF, source, log and rendered-image hashes to the reviewed pages and the detailed dependency checks. `make_receipt119.py` only collects that read-only metadata; its human assessment fields are explicitly identified as audit judgments. Copies of the reviewed PDFs and rasterizations remain available in this audit directory, while the compact JSON and this note can be included in the publication package.
