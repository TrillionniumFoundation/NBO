# Response to the R96 referee report

## Neural Bellman Operators — Revision 97

14 October 2026

We thank the referee for distinguishing the validity of the original-model qualification from the numerical contribution of its neural representation. We have revised the existing *Neural Bellman Operators* paper, rather than replacing it with a differently titled paper. The revision retains the original construction problem, own-future neural construction, complete-policy guarantees, all adverse comparisons, and the historical scientific sections. We respond to the substantive identification, accounting, proof, and verification concerns directly.

The reviewed scientific snapshot is \path{9a80ab7d4de97c9a61747899766fab43ec3c2598}. The report is pinned at review commit \path{e91a0702a4f1df4baa7b43fdfdd1305d0d62940c}. The R97 rank–label and complete-process protocol was committed before its campaign at \path{673d29e48922ae59908cdde245f312e077442539}. The current revision does not modify either historical branch. This response distinguishes completed results from the larger experiments and validation boundaries that remain open for evaluation; a successful software gate is not represented as an editorial judgment.

## 1. Central contribution and neural identification (B1, M1)

The title and topic are unchanged. The introduction now separates original-model validity, acquired representation, attained certificate precision, and the delivered economic decision. Representation-neutral qualification is an essential property of the NBO policy construction, not evidence that all representations have the same acquisition or evaluation cost.

We add Proposition 18 with an exact, proved comparison. The oblique continuation $(x_1+x_2-1)_+$ has a one-ReLU representation, whereas the best errors among arbitrary additive continuations and total-degree-two polynomials are $1/4$ and $1/16$. The proof gives matching lower bounds and attaining approximants. It explicitly states that an ordinary oblique-hinge implementation also represents the function exactly. The result therefore identifies geometry, not a label attached to equivalent code. It is not presented as the investment value function, a policy-regret separation, or a universal separation from conventional approximation.

For the actual investment model, we execute certificate-oriented neural readouts and paired conventional controls across budgets. These provide a direct test of whether a better attained certificate translates into better proposals and less total work. The retained R96 quadratic winner and its zero rejected first proposals remain in the article. No theoretical example is used to reverse those data.

## 2. Novelty and information complexity of the risk enclosure (B2, M2)

The revised treatment separates four statements: classical AVaR and convexity ingredients; the midpoint–endpoint enclosure and its specified-rule constant; recursive policy composition and prospective decision precision; and an information-class lower bound.

Theorem 17 is new. For convex $K$-Lipschitz functions on $[-R,R]$, under the uniform law, every deterministic procedure using at most $N$ exact function values, with adaptive sampling allowed, has a worst-case enclosing interval of width at least $KR(1-\alpha)/(6(N+1)^2)$. The proof runs the procedure on a quadratic tail and constructs a chord interpolant that has the same adaptive transcript. Their AVaR values differ by an exactly computed tail integral. A valid enclosing interval must contain both values. Point estimation has half the stated lower bound.

The retained upper bracket uses $2n+1$ distinct values and has second-order width. Thus the deterministic information exponent is optimal for each fixed risk level. We do not claim a uniformly optimal constant as the risk level approaches one, a randomized lower bound, a bound for derivative or formula oracles, or a dimension-free result. Classical information-based reasoning is credited to Novak, and the AVaR variational formula to Rockafellar and Uryasev. The Cartesian point counts accompany the product-error discussion. The earlier sharpness example remains intact and is not relabeled a minimax proof.

## 3. Economic equivalence and the meaning of the margin (B3, B10, M6)

All twelve R96 simultaneous paired intervals, including their containment of zero, remain visible. The finding is equivalence at the specified engineering margin, not welfare superiority. We preserve the point estimates favoring online solution and the qualified-service interpretation.

The margin $1/1280$ is one percent of the maximal first-date investment charge $5/64$, not an externally calibrated one-percent welfare effect. The revised introduction and interpretation do not infer economic materiality from this normalization. The purchase calculation is given in normalized model-cost units and as a parameterized price–fee sensitivity analysis. It does not fabricate external compute prices, adoption fees, welfare weights, or an empirical calibration.

The new actors do not inherit the old actors' statistical intervals. Their purchase calculations use the valid complete-service bound $d\in[-1/256,1/256]$. The new 64-state cell samples are diagnostics, not a powered population confirmation or an opportunity to select a favorable sign. A calibrated large-scale application remains an additional empirical obligation, not a conclusion supplied by the present normalization.

## 4. Complete acquisition and workload accounting (B4, M3)

We add Theorem 20 and correct the corresponding purchase formula in a current copy of the original precision section. A workload has $B$ decisions, while its clock measures the entire process. The correct gain contains $B d$, not just the per-decision policy difference $d$. The current timing workload has $B=32$. The original historical section is retained unchanged for audit.

Each fitted configuration starts from the frozen economic primitives and pays for its own labels, all feature-search candidates, fitting, whole-domain coverage, candidate readout optimization, validation, serialization, identity checks, and durable deployment. An unsuccessful candidate is not free. A fixed-family LS–CA pair receives the same selected geometry and available labels. Equal payloads are not equated with equal fitting cost.

The acquisition record reports an internal construction time and a conservative full-process time. The latter also charges imports, output, and the subsequent diagnostic probe. We do not subtract a noisy diagnostic duration to create an artificially small acquisition figure. The two values form a deliberately broad measured acquisition bracket. Differences use interval subtraction, including the comparator's acquisition uncertainty; they do not subtract two upper endpoints as if that produced an upper bound.

The remotely frozen workload counts are 1, 10, 100, 1,000, and 10,000; compute prices are 0, 0.01, 0.1, 1, and 10 normalized cost units per second; fixed fees are 0, 0.01, and 0.1. The complete grid has 1,800 candidate–comparator classifications. The source-bound tables and JSON retain adoption, rejection, and unresolved regions. Strict inequalities are used; exact equality is not rounded into adoption. The theorem gives the first strict integer workload count when its sufficient slope is positive.

Measured clock ranges are descriptive, not confidence intervals for future hardware or workloads. Hence a purchase decision using these envelopes is explicitly conditional on their applicability. Research authoring and a purchaser's optional additional independent audit are not silently priced as zero: the separate audit execution is recorded, and additional deployment audit cost must be added to acquisition or the fee.

## 5. Matched budgets and executable certificate-oriented fitting (M4)

The fixed experiment has two risk levels, three ranks, two training-label budgets, and seven arms: online solution and LS and CA readouts for quadratic, ReLU, and spline continuations. It contains 84 complete acquisition processes, 36 within-family readout comparisons, and 5,376 new diagnostic arm–state rows. At ranks four, five, and six, the deployed payloads are respectively 64, 96, and 128 bytes across the fitted families. Construction metadata are retained separately; they are not misrepresented as executable model coefficients.

The CA arm solves a finite interval-residual-span program on acquired sites. It then rounds coefficients and recomputes the whole-domain residual enclosure. Proposition 19 proves the nonworsening guarantee of the actual validated accept-or-retain rule, independently of the numerical optimizer's success flag. Neither a nodewise program nor its floating-point output is represented as a proof of global optimality. All rejected constructions remain charged.

The comparison distinguishes a neural geometry effect from an objective effect by applying the same CA intervention to all three families. Every rank–label cell remains in the development appendix. The first complete campaign finds strictly improved validated residual spans in all 36 pairs but nonmonotone changes in proposal rejection. This is a substantive result about the distinction between residual precision and decision quality, not a hidden failed arm. A broader tournament including additional nearest-neighbor, derivative, and oblique conventional approximations is not claimed completed.

## 6. Proposal quality, admission, repair, and resources (B5, M5)

Each row records first-proposal loss and width, separate loss and width reason codes, whether repair is invoked, refinement counts, final rational fallback, endpoint work, and component clocks. A repaired service is credited to the complete algorithm; its reliability is not attributed to an already rejected predictor. The current article displays rejected first proposals by arm and risk level, and the appendix retains every paired budget cell.

The machine-readable state map uses sixteen fixed rectangles and retains empty regions. Primitive-call and continuation-feature counts accompany clocks. Whole-process comparisons include model loading, certificate work, and failed proposals. The source-bound report refuses to generate tables from an incomplete configuration or row catalogue. These additions address predictor reliability separately from verifier resilience.

## 7. Scaling scope and retained vector results (B6, M7)

The original NBO construction, its horizon allocation, and the inherited two-control and vector analyses remain complete in the revision and archive. The product quadrature formula now states the Cartesian evaluation burden beside its coordinatewise error interpretation. No additive error expression is used to imply an additive or dimension-free node count.

The new 84-cell campaign expands representation and acquisition budgets, not the number of economic decision dates or controls. We have not relabeled it as a longer-horizon, multicontrol, multi-innovation continuous-risk experiment. Such a complete tournament remains an unresolved empirical part of the referee's request. The retained results support only their own stated scopes. This boundary does not change the NBO topic or replace its general construction with a smaller research question.

## 8. Independent replay and construction discrepancies (B7, M8)

The new proposal evaluator imports none of the production interval, actor, fitting, or quadrature modules. It separately derives continuous terminal risk from the economic primitives, integrates the tail polynomial, differentiates the optimized value with the capacity multiplier, performs stable discrete AVaR selection, and bisects the action problem. It replays all 32,768 R96 first proposals, including all 8,192 online conventional proposals, rather than only stored-model predictions. Binary64 action differences are checked against the explicit $2^{-29}$ tolerance and retained; this is not a claim of exact bit identity.

The rational implementation independently recomputes all twelve statistical contrasts from the complete original row catalogue. It also checks 24 difficult endpoint cases selected by recorded extremal criteria, including boundary and poor-proposal states. These are additional to the retained historical random 64-case audit; we do not add the counts as if overlap were excluded, or imply that every original-law endpoint was recomputed rationally. Discrepancies are fail-closed and remain in the receipt.

The development reconstruction of the six original payloads found byte-identical ReLU and spline models but differing quadratic feature geometry. We retain those differences. A new exact monomial expansion bounds the quadratic function difference uniformly on the state square. This does not imply identical actions, and no reconstruction replaces a frozen confirmation model. The new campaign's explicit numerical tie rule is a new declared recipe, not retroactive evidence of byte-identical R96 fitting.

The fitting optimizer itself is not independently reimplemented. Consequently, this is a materially broader independent critical-path audit, not a claim of independent authorship, proof-assistant verification, or independence of the entire learning-to-action stack.

## 9. Architecture evidence and a common release (B8, M9)

The separate R96 ARM64 evidence is incorporated without modifying its historical source or replacing the primary results. Its immutable source is \path{462fb1564dd99d4c3ad31881836fc6486b630899}. The new lineage ledger binds the imported source, the actual model and catalogue identities, the R97 protocol, and the current source and execution commits.

The ARM record concerns the same frozen R96 models and states, with identical production CSV bytes, zero new fits, and zero additional independent economic observations. It is not pooled with the new diagnostic campaign. Neither a full ARM64 acquisition replay nor energy measurement is claimed. Processor frequency is not controlled. Operation counts and stage clocks improve interpretability but do not turn uncontrolled clock ranges into hardware-general performance guarantees.

## 10. Submission organization and preservation (B9, M10)

The article and technical supplement have been reorganized rather than replaced. Complete primitive-accuracy and horizon-allocation sections are moved from the article to the development appendix. Seven intervening historical proof sections are moved intact from the supplement to that appendix. Their scientific source files and data remain byte-preserved. The current article retains the original NBO construction and complete-policy chain, the recursive-risk and precision results, the original R96 comparison, and the new identification and acquisition results.

The content map identifies every moved section and the one intentionally corrected current precision copy. The original source remains in the historical revision and is never overwritten. The reading guide separates the active article and focused proof supplement from the cumulative development appendix. PDF build receipts contain source hashes, page counts, unresolved-reference checks, and overflow diagnostics. Visual inspection is recorded separately after rendering the actual final PDFs; a successful compiler exit is not mislabeled visual inspection.

## 11. Minor and technical points

**Initial law and pairing (comments 1 and 3).** The new and retained experiments explicitly use the declared 20-bit dyadic initial support. Within each cell, services share the same initial states and deterministic integration rules. R96 sampling independence concerns independently drawn initial states, not independent outcomes from paired services. New streams and seeds are recorded before their campaign.

**Enclosure widths (comment 2).** The one-service width and the two-service difference contribution remain distinct. The new distribution-free purchase bound uses complete-service regret rather than reusing a deterministic endpoint width as a confidence half-width.

**Coefficients, selection, and conditioning (comment 4).** Every executable coefficient, direction, offset, selected feature, candidate fit, condition diagnostic, payload digest, and numerical tie convention is deposited. Failed or rank-deficient candidates are retained in the construction log.

**Acquisition and all-stage costs (comments 5 and 6).** Internal stage records, full fresh-process charges, validation and serialization steps, and rejected proposals are included. None of the selected stage columns is described as the entire purchase boundary.

**Rule sharpness and product work (comments 7 and 8).** Specified-rule sharpness is retained under that name. The new adaptive information lower bound has its own admissible class and constants. Midpoint and endpoint Cartesian counts are explicit.

**Architecture, visual inspection, and lineage (comments 9–11).** These have distinct evidence records and are not inferred from a successful scientific computation. The imported ARM record is a frozen-model replay, not a new R97 fit. The actual visual receipt identifies the final PDF digests and inspected page ranges.

**Economic terminology (comment 12).** The engineering normalization and parameterized purchase region are distinguished from external welfare calibration. We do not describe the normalized margin as an established one-percent economic effect.

## Concluding statement

This revision strengthens the original NBO paper with an adaptive information lower bound, exact representation comparisons, executable verified readout acquisition, a complete matched-budget campaign, workload-consistent purchase intervals, and expanded independent replay. It retains the adverse quadratic comparison and the distinction between residual improvement and delivered decisions. The remaining boundaries—external economic calibration, a new longer-horizon vector-risk tournament, a broader conventional frontier, and an independent fitting implementation—are specified rather than silently declared closed. We submit the continuing NBO manuscript and its complete evidence for renewed substantive evaluation.
