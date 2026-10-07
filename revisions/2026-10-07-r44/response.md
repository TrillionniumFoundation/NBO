# Response to the R42 referee report

**Paper:** Neural Bellman Operators. **Author:** Qian QI. **Revision:** R44, 7 October 2026.

We thank the referee for distinguishing the progress in fresh own-future training from the separate requirements of a coherent manuscript and a method-specific economic comparison. We have revised the existing paper, retained its title and economic program, and preserved every original theory and application source. This is not a replacement paper on a different subject. We respond substantively to the report's objections while keeping unfavorable findings visible.

The reviewed science is fixed at `70bf2db76bf7c873be0d8748a5cc120001f347aa`; the report is fixed at `770ad3a9db05002c0165bf26b58be71d0f1319e1`. The last materialized manuscript is R41 at `06a104a8db06b76464165899d817b303cb2aaa01`. R43 at `3c9ad7a969bddf3c79ec5dc07e4b74704fed8615` contained a protocol and incomplete source capsule when this revision began. We did not overwrite that branch or represent its protocol as completed evidence. The new R44 protocol was committed at `32505809223124c6cd4968af1b216d88c25a3b41` before the added numerical diagnostics.

## Principal changes

The new main article follows the economic problem, the operator, centered economic transport, the full-policy theorem, construction, direct policy comparisons, and evidence. It reports the entire R42 catalogue. A new technical supplement proves the additional results and gives all 24 direct comparison intervals. The complete prior article, supplement, and applications remain unchanged as linked companions, with exact preservation hashes and a precedence map. The current manuscript, rather than a workflow artifact alone, now contains the results.

The principal new analytical result is retained-policy recertification. Refining a critic's residual enclosure does not require changing the deployed actor if its original uniform allowance is retained. We apply this result to all seven neural objects that missed their original tighter targets. All seven now meet those targets without any training update, weight change, or change to the deployed action arrays. We retain the original terminal enclosures and original actor allowances. Fine-grid action proposals generated internally by the verifier are discarded but their work is charged. The original capped-service failures remain failures in the original table.

The second addition is a direct paired policy-cost score. Its expectation is the actual neural-minus-ridge policy-cost difference; a signed Bellman telescoping argument supplies its support. Continuous innovations are enclosed inside uniform bins. Outward propagation includes possible nearest-node ambiguities, and empirical Bernstein bounds account simultaneously for all 24 comparisons. Every interval contains zero. The new analysis therefore supplies the previously missing estimand without asserting an unsupported method ranking.

## Blocking comments

### B1. Materialize the science as an internally coherent paper

**Response and disposition: addressed by the release.** R44 has an authoritative main article, new proof supplement, response, generated tables, all new result records, executable sources, deterministic audit, build instructions, and compiled documents. The root README points to this revision. The manuscript reports every R42 attainment rate, scalar signed comparison, coupled comparator result, and precision finding. The preserved R41 article is expressly identified as retained content, not as the current empirical account.

The source/evidence identities distinguish the original successful catalogue from its first failed run and from the new diagnostics. A current-state manifest binds the source tree and all published outputs. A workflow success is not described as editorial approval.

### B2. Scalar target failures and their binding components

**Response and disposition: the failure diagnosis and retained-policy target question are addressed; the original capped attainment rate is unchanged.** Main Sections 3.2, 4.2 and 6.4 and Supplement Sections 3–4 give the proof and component accounts. Original tight-target failures are scalar IDs 041, 089, 120, 124, 145 and 147. Their bounds were approximately 0.04092–0.04137. With unchanged networks and actors, a residual grid of 4096 and the original action resolution 1024 gives bounds 0.03068472, 0.03090917, 0.03085353, 0.03070697, 0.03108539 and 0.03077644, respectively, all below 0.04. The exact outward values are in the records.

This experiment isolates a verifier extension, not additional representation capacity or successful retraining. It shows that these failures do not identify inadequate deployed policies. We do not reclassify the original 6/12 tight-target service result as 12/12. The extra verification has its own charged work, transient storage and local clock.

We separately report state coverage, actor allowance, action-cover subcomponents, nodal residual enclosure and terminal error. A pure representation/optimization split is not identified by the frozen records; the revised paper explains why a fitting loss cannot supply it. We do not manufacture such a decomposition.

### B3. Scalar signed economic comparisons favor the spline

**Response and disposition: addressed in the interpretation and complete tables.** At 0.06 the original 48 intervals give 29 positive, zero negative and 19 overlapping-zero neural-minus-spline differences. At 0.04 the 24 common comparisons give 17 positive, zero negative and seven overlaps. The main article states these counts explicitly. Containment within the descriptive ±0.005 margin is not called equivalence, and the scalar catalogue is not evidence of neural superiority. The new verification-only diagnostic does not change any of these policies' costs.

### B4. The flexible coupled ridge is a strong competitor

**Response and disposition: addressed as a comparator and interpretation issue; no broad neural performance advantage is claimed.** Ridge remains in every original comparison. The manuscript reports its 6/6 attainment at both targets, its smaller final gap in four of six pairs, and the original target-crossing timing comparisons. It also distinguishes its fixed, date-specific dictionary seed from random neural training seeds. Repeated seed labels do not create independent random ridge representations.

For the single unresolved tight-target coupled neural policy, ID 128, the retained-policy theorem gives a bound 0.09775755108915223 after residual refinement, retaining its original 133,128 scalar actor entries. Its original 0.15223570219655133 bound and original failure remain recorded. This isolates certification resolution, not a claim that learned features now dominate a selectively unrefined ridge.

### B5. Supply direct neural-versus-ridge policy-value differences

**Response and disposition: addressed for all six pairs and four declared initial states.** Main Section 5 proves the direct score and support theorem; Supplement Section 5 proves coverage for the continuous-law interval simulation. We select each method's first original 0.25 crossing, use 65,536 common innovation-bin trajectories at each state, retain all 24 comparisons, and allocate family error 0.01 across 48 tails. Numerical mean, variance, logarithm and square-root bounds are outward controlled.

All direct intervals include zero. Their widths range from approximately 0.00019469 to 0.00026982. No equivalence or superiority follows. The support is derived from signed residuals, but the observations are direct own-policy scores, not a subtraction of regret upper bounds. The statistical guarantee is under the declared iid simulation model, not a claim that a fixed pseudorandom stream is literally independent.

### B6. Nonlinear dimension scaling

**Response and disposition: the analytical dimension account is explicit; a new nonlinear scaling experiment remains an evidence obligation.** Main Section 4.3 states the state, action, innovation, network and storage factors. The supplement specifies the finite-dimensional geometric certificate. The coupled experiment remains two states and two controls. Its additional grid has 66,049 states and is a costed diagnostic, not a high-dimensional benchmark. The original quadratic and precision experiments are not relabeled as nonlinear scaling evidence.

The original broad economic formulations and conditional theorems remain part of NBO. We have not changed the topic to avoid this comment. The empirical support for a nonlinear scaling frontier is not established by this revision's seven verification refinements.

### B7. Stable work-to-certified-accuracy advantage

**Response and disposition: complete-accounting interpretation is corrected and preserved; repeated isolated nonlinear timing remains an evidence obligation.** All original work records and clocks are unchanged. Original nonlinear timings remain descriptive singleton observations; new local diagnostic clocks are separately named and cannot be added across hosts to reconstruct a new end-to-end service. New diagnostics were scheduled concurrently, so their wall times are not a controlled comparative benchmark.

The publication reports machine-independent verification counts and retained/transient actor storage. It retains failed capped costs rather than conditioning a speed comparison on success. A stable neural timing advantage is not inferred from these measurements.

### B8. Adaptive precision does not save complete recorded work

**Response and disposition: addressed.** The manuscript reports fixed64 and adaptive 36/36, fixed32 6/36, the common 474 accepted updates, the 126 rejected binary32 proposals, and the actual complete recorded timing arithmetic. Adaptive is slower in 26/36 pairs and its aggregate time is 0.9763277185 percent higher. The conditional numerical acceptance analysis remains intact. Activation and certification are no longer described as evidence of an empirical work saving.

### B9. Fixed catalogues and nonlinear training reliability

**Response and disposition: addressed by an explicit estimand and separation of theorems.** Main Section 2.2 defines the deterministic capped-service array on the complete catalogue, including failures and their costs. The new selected diagnostic is not treated as an independent repetition. The original structured factor-training finite construction is retained under its own spectral and moment hypotheses, but is not extended to the unrestricted nonlinear optimizer. A probability of target attainment under an initialization law remains a different object requiring its own design.

### B10. Cumulative exposition and breadth

**Response and disposition: addressed editorially without deletion or topic replacement.** The active article has one economic-to-theorem-to-evidence order and consistent notation. The original controlled-economy formulation and its recursive and game applications remain in the paper; full original sources are byte-preserved in their existing paths. A preservation map and retained-companion links make every earlier result available. Historical material is not silently discarded, nor used to overstate what the new nonlinear experiment establishes. The new proofs and empirical account are in the current main article and supplement rather than another detached science addendum.

## Major comments crosswalk

**M1.** See B1: complete authoritative manuscript, supplement, response, tables, results, hashes and PDFs are materialized.

**M2.** See B9 and the main article's capped-service definition: the estimand is the complete fixed-catalogue capped-service performance array, not optimizer success probability. Equation numbering is generated by LaTeX; the labeled source is `eq:estimand`.

**M3.** See B2 and B4: all seven failures are diagnosed with source-bound available allowances and unchanged-policy residual refinement. Representation and optimization are not falsely claimed to be separately identified. Raw per-attempt decompositions remain available for the full ladder.

**M4.** See B5: all 24 direct coupled comparisons now target actual policy-cost differences under shared continuous innovations, with finite-sample and numerical error control.

**M5.** The flexible 96-feature ridge fitted-value comparator is retained and discussed as a substantive competitor, not a weak quadratic foil. We have not executed an additional adaptive sparse-grid or adaptive-partition method in this revision. We therefore do not claim that this request is fully empirically answered, or invent a technical incompatibility to exclude it. The same final verifier is specified as the appropriate comparison boundary.

**M6.** See B6: the dimension/horizon study remains an empirical obligation. The new manuscript exposes the tensor-cover and actor-storage costs explicitly and does not substitute the old matrix catalogue for nonlinear scaling.

**M7.** See B7: original isolated process identities, failed work and operation counts are retained; new clocks are diagnostic and separately charged. A repeated, isolated nonlinear timing catalogue has not been executed here.

**M8.** See B8: the observed adaptive precision finding is stated in the main evidence section, with its exact accounting. No favorable outcome is fabricated by changing the task or excluding rejected proposals.

**M9.** Main Sections 2, 3, 5 and 6 distinguish producing a policy, verifying its regret, and identifying a direct economic contrast. A certificate is method-neutral; fresh trainable hidden features are a construction choice; an economic comparison is an additional object. The economic experiment is explicitly stylized rather than a new calibrated welfare discovery.

**M10.** See B10: the active exposition is reorganized and condensed while all original theorem/application text remains in unchanged linked companions. We do not adopt the proposed replacement title or change the subject. The same NBO paper now has a coherent current manuscript and a complete preservation map.

## Scope of this response

R44 closes the missing-manuscript problem, proves and executes the retained-policy diagnostic for all seven unresolved tight targets, and supplies the previously absent direct coupled cost comparisons. It preserves the original catalogue and its adverse results. It does not claim that all publication judgments or comparative research obligations are thereby settled. In particular, an additional adaptive-grid comparator, nonlinear dimension/horizon scaling, and repeated isolated nonlinear timing remain clearly identified evidence requests. These are not reasons to abandon the NBO program; they are distinct claims that cannot be supplied by renaming the present diagnostics.
