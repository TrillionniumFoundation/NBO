# R15 editorial implementation for Neural Bellman Operators

Status: the current structure, complete scientific narrative, and responses to all sixteen B/M comments are implemented. The paper retains NBO as its subject. Completion of a response does not assert that every stronger scientific conclusion requested by the referee has been established.

The reviewed object is commit `f5021cefa71492babfcbfa580e0c984f59a9de26`. Its recursively resolved source inventory contains 114 TeX files, 230 labels, and 4,896 source lines. The earlier prospective plan and response strategy are retained under `archive/editorial_development`; this file records the implemented reading copy.

## Current article and supplement

The main article proceeds from the economic problem to one NBO evaluation–improvement algorithm, general approximation results, the capital model and deployed controller, the exact payoff identity and policy-specific welfare theorem, the finite Bellman mechanism, the original economic applications, and the complete comparison design and findings. The abstract is 140 words under the independent publication-audit counting convention, within the 150-word limit.

The original recursive-utility, endogenous-preference, temporal-self, and strategic models remain visible in the main article and complete in the current supplement. Their different utility domains, normalization requirements, equilibrium conditions, and deviation criteria are explicit. No application is treated as empirical evidence for a numerical superiority claim established in another model.

Supporting capital details are consolidated in current Appendix C, `manuscript/appendix_capital_accounts.tex`: analytical anchor and tube bounds, their entire theorem and proof, spectral and quadrature costs, diffusion-transfer constants and proposition, Gaussian tails, and the complete implementation and numerical proofs. The main article retains the assumptions needed to interpret each central statement and points to exact supplementary equations. This is a relocation of supporting material, not an archive-only replacement of mathematical content.

The supplement is organized by mathematical and economic subject. It includes all current general proofs, the complete finite Bellman mechanism proof, the independent paired-transfer proof, method-distribution inference, original application derivations, implementation arguments, complete declared streams and checkpoint histories, scalar algebraic and restriction-loss results, and the full sensing and mechanism accounts. Complete duplicated historical configuration records and successive-version narrative remain at their exact reviewed paths, with explicit archive navigation.

## Executed scientific findings

The primary experiment is the same nonlinear capital economy at the declared higher-volatility parameters. It executes all 128 method–dimension–stream combinations, has no fallback, and retains all 238 confirmation events. Its target is the uniform distribution over sixteen complete, prospectively fixed streams, not an unstated population of future random initializations.

NBO's method gain lower endpoints exceed 0.000943 and 0.000957 in dimensions ten and fifty. The original NBO–HJB comparison is economically material in dimension fifty. The independently proved common-innovation transfer gives direct intervals contained in [0.000179, 0.000411] and [0.001347, 0.001650], establishing material superiority over the declared HJB procedure in both dimensions at the original 0.0001 margin. The original endpoints remain alongside the refinement; no paths, confidence events, training, or stopping decisions change. All four Raw/DPO contrasts remain unresolved, including under the refined account.

In dimension fifty, all NBO, Raw, and DPO streams reach the actual online 0.0005 target; HJB reaches it in none. NBO uses less measured complete process work than DPO, while Raw is cheaper. In dimension ten no method attains the online target, although independent final confirmation certifies every returned NBO/Raw/DPO policy above 0.0005. These final certificates do not rewrite the stopping history. Process clocks include imports, setup, constants, fitting, checks, reload, confirmation, and durable output; dependency installation and artifact extraction precede the clock.

The complete candidate-occupation mechanism assessment covers 32 returned NBO policies and 12 simultaneous events. All evaluation, action, holding, sampling, and arithmetic terms are instantiated. The resulting sufficient continuous-gain lower endpoints are approximately −0.006778 and −0.004800, and both protected critic-versus-Raw risk intervals cross zero. The manuscript does not substitute direct policy-payoff superiority for a positive critic-mechanism result.

The absolute full-adapted-class regret account remains explicit and broad: NBO upper bounds are at most 0.025971 and 0.036843. It does not establish proximity to the optimum within the 0.0001 comparison margin. The independent scalar study provides actual classical training and deployment, strict finite-grid residual and action-restriction bounds, and all observed neural/classical and state-specific ranking results. The finite-observation experiment retains all four positive parent comparisons and six positive lower endpoints among twelve sensor specifications, with outward reporting of bounds.

All unfavorable earlier capital comparisons remain in the main reference-evidence table and exact historical record. No interval containing zero is called equivalence, no scalar error bound becomes a high-dimensional reference, and no stylized population or fee experiment is called an empirical calibration.

## Preservation and evidence identities

`SOURCE_INVENTORY.json` pins the reviewed include closure. `EDITORIAL_MAP.json` maps all 230 labels: 174 remain in the current reading copy and 56 refer to the exact archive. Every original mathematical label remains current. `MATHEMATICAL_PRESERVATION.json` verifies normalized full-body equality for twenty prior mathematical statements and four explicit proof environments; it also indexes current new statements. Normalization is limited to documented editorial whitespace, heading, revision-name, and leading-zero changes.

`PUBLICATION_SOURCES.json` identifies the numerical sources and exact evidence commits for the primary, mechanism, and observation experiments. Raw evidence and frozen numerical code are unchanged. Publication presentation redirects the primary summary, contrast, and stream tables to the outward-printing versions; it retains the original report and all scientific fields. Paired-transfer table column spacing is adjusted only by local include wrappers, preserving canonical report bytes.

`RESPONSE_MAP.json` retains the exact report comments and supplies one completed source-bound response and current label map for each of B1–B7 and M1–M9. It records the material direct-method findings and the unresolved mechanism, Raw/DPO, and absolute-accuracy conclusions separately. The initial response generator and template survive only in `archive/editorial_development`; no active writer can replace the final response with placeholders.

## Journal style and verification

The maintained `econsocart` class and publisher configuration are unchanged. The current roots use the supplied Econometrica submission style, a self-contained abstract below 150 words, author–year citations, sequential result counters, unnumbered run-in headings, informative table notes, leading zeros, and no vertical table rules. Supplementary results and equations use distinct continuous S. sequences; tables retain the publisher's appendix-letter prefixes. Cross-PDF references identify their actual destination without ambiguous numeric ranges.

The official support sources are:

- https://www.econometricsociety.org/publications/econometrica/information-authors
- https://onlinelibrary.wiley.com/page/journal/14680262/homepage/forauthors.html
- https://www.e-publications.org/es/support/
- https://vtex-soft.github.io/texsupport.econometricsociety-ecta/
- https://github.com/vtex-soft/texsupport.econometricsociety-ecta/blob/master/ecta_template.tex
- https://github.com/vtex-soft/texsupport.econometricsociety-ecta/blob/master/ecta_sample.tex

No current hard page limit was verified, and no such limit is asserted. Organizing the article around an economic evaluation–action–payoff chain is an editorial response to this report, not a claimed publisher mandate.

The integrator requires the complete current scientific inputs before writing publication roots. It enforces one algorithm, source identity, mathematical preservation, unique current labels, and closed references. Compilation checks unresolved references, overfull material, and duplicate PDF destinations. Visual inspection covers the complete reading copies and the relocated mathematics and new tables; the actual preview hashes and page counts are recorded separately in `EDITORIAL_PREVIEW_CHECK.json`.
