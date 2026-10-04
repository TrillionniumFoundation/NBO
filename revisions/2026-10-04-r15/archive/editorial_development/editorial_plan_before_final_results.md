# R15 editorial plan for Neural Bellman Operators

Status: the authoritative structure and source-preservation map are implemented. Final comparative prose awaits the complete primary and mechanism results; no favorable outcome is presumed.

The current capital presentation keeps the original model, admissible class, interior analytical schedule, feasible neural map, sampled controller, exact paired-payoff identity, and policy-specific welfare theorem in the main article. Supporting anchor/tube constants and their complete theorem, spectral and quadrature accounting, diffusion-transfer constants and proposition, Gaussian clipping envelope, and all corresponding proofs are grouped in the current `appendix_capital_accounts.tex`. These are current supplementary results, not archive-only material. Their old labels are unchanged; supplementary result numbers use the unambiguous continuous sequence S.1, S.2, and so forth. This reorganization reduced the evidence-incomplete main preview from 47 to 44 pages; final page counts will include all completed reports and are not journal limits.

Reviewed object: commit f5021cefa71492babfcbfa580e0c984f59a9de26, tree 5a0084d6ce3df47469125a7afe85c081cd29d94f. The latest advisory report is dated 4 October 2026. Its B1–B7 and M1–M9 are represented separately in RESPONSE_MAP.json. The recursively resolved source inventory records 114 distinct TeX files, 230 labels, and 4,896 source lines reachable from the two reviewed roots. The inventory is generated from the pinned commit, not from a changing worktree.

## Editorial decision

Retain the title Neural Bellman Operators, the evaluation–improvement research question, and the original recursive-utility, endogenous-preference, temporal-self, and strategic applications. Take the report's NBO-centered route as the organizing scientific task. A renamed, candidate-generator-agnostic verification paper would change the user's intended topic and would not answer the objection to the critic.

The current manuscript must nevertheless distinguish what is proved, what is implemented, and what is measured. Preserving NBO does not license turning a schedule-relative certificate into a comparative advantage. The new reading copy should explain the learned evaluation object, the actions it changes, the economic error account, and the evidence for its incremental value in that order. New positive mechanism or efficiency statements are contingent on the mathematical and experimental investigations. The R14 unfavorable findings remain visible.

This is substantive consolidation, not cosmetic compression. The desired reduction comes from stating the current algorithm and theorem chain once, eliminating repeated version narratives, unifying notation, and placing each complete proof beside its current result. Do not reduce type size, hide adverse rows, remove economic primitives, or detach a theorem from a hypothesis to hit a page count.

## What creates the current accumulation

1. ECTA.tex first defines the differential critic/actor algorithm, later inserts the R6 map and R8 envelope, and still later introduces rollout-costate fitting through the capital discussion. The reader has to reconstruct which evaluation variant generated which evidence.
2. The supplement begins with current proofs and experiments, then starts a second “Earlier Verification and Application Results” document. Its introductory text still says the R11 protocol identifies the present evidence.
3. The same supplement includes the R6/R8/R9/R10 historical narrative, a retained applications manuscript, a prior R10 conclusion, retained general proofs, all R11 tables, and the earlier R11 learning/study text. Some of these blocks contain indispensable unique models or proofs; some merely repeat development history. They cannot be removed wholesale by directory name.
4. R14's integration script preserves every old main-root label in the main root. That guard protects against accidental loss but also inhibits a coherent current reading copy. It checks only root labels rather than the full recursively included mathematical record.

Replace that guard with a preservation map: every old substantive result, proof, application, and unique numerical claim has a current destination; every duplicated historical passage has an exact archive destination. Preserve the pinned roots and their complete include closure as immutable evidence. Do not require a historical theorem to appear twice in the typeset publication merely to retain its old label.

## Proposed authoritative main article

The following section numbers are provisional editorial destinations. They become exact TeX labels only after the new mathematics and experiment design have been approved internally and integrated.

| Section | Reader's question | Required material |
|---|---|---|
| 1. Introduction | What does NBO add to economic computation? | Original internal/external choice motivation; concrete evaluation–improvement object; three contributions with their scopes; the decisive observed comparison, including unfavorable evidence; one short roadmap. |
| 2. Economic problems and admissible decisions | What is the economic object being approximated? | Finite-horizon recursive objective, controlled diffusion, utility domain, boundary/exit/reflection conditions, comparison class, and the separate meaning of temporal and strategic deviations. |
| 3. The Neural Bellman Operator | What exactly is run? | One Algorithm 1; frozen policy evaluation, detached value/derivative channels during improvement, feasible action routine, validation and final selection, verifier output, all evaluation variants explicitly indexed. |
| 4. Evaluation error, action quality, and economic accuracy | Why can the learned value improve a decision? | General evaluation/action error theorem; candidate-occupation performance difference; the route from a measured evaluation error to an economic term; separate finite-grid and viscosity corollaries. A new operational closure enters here only after proof and computation pass. |
| 5. The capital economy and its implemented controller | How is the main numerical economy defined and evaluated? | Primitives; analytical anchor; one integrated policy-specific certificate; common-path comparator interval; observed-history and finite-sensing implementations; economic interpretation of the controller and costs. |
| 6. Economic applications of NBO | Why the original broader topic remains economically meaningful | Subsections on recursive utility, costly preference adjustment and portfolio choice, temporal selves, and dynamic games. Each gives the distinctive continuation object, action condition, deviation/welfare criterion, approximation domain, and pointer to a complete current derivation. |
| 7. Computational design and results | Does the Bellman block improve accuracy or total work? | One comparison protocol, prespecified method-level estimand, common verifier and economic margins, actual work-to-target design, contribution-isolating baselines, mechanism chain, original R14 contrasts as a fixed reference study, scalar/classical convergence and sensing accounts. |
| 8. Conclusion | What has the NBO analysis established? | Economic and numerical findings supported by the final records; interpretation of application-specific scope; a concise remaining limitation rather than revision history. |

The article should be materially shorter than 63 pages after consolidation, with approximately 40–45 pages as an editorial working target, not a verified journal limit or permission to delete substantive content. Count pages after integrating the actual new results. Any further reduction must name the duplicate passage or the current appendix destination; never silently omit a unique result.

## One algorithm, with explicit evaluation variants

Use one implementation map with inputs: economic primitives and information; action/value classes; boundary and utility realization; evaluation variant; optimization budget; training-randomness design; validation rule; economic target; and final inference rule. Its outputs are a fitted value/policy object, complete deployment rule, measured work, and a typed accuracy record.

Its steps are:

1. Draw or fix the training stream according to the declared method-level design; initialize feasible policy and compatible value representation.
2. Freeze the entire deployed policy. Evaluate its own continuation object by the specified differential residual, positive-weight backup, or rollout value/costate target.
3. Freeze the critic value and derivative channels. Improve the feasible actor or solve its stated Hamiltonian problem. Any local correction is part of the named deployed policy.
4. Apply the predetermined validation/stopping rule and record all unsuccessful checkpoints and consumed work.
5. Freeze the selected fitted objects before final independent evaluation. Compute the declared economic endpoints, mechanism terms, and comparison intervals.
6. Return the approximation, implementation, scope, and all available bounds and measured diagnostics.

This unifies presentation, not numerical objects. The differential residual, nodal Bellman defect, and noisy rollout target are not interchangeable; record an evaluation_variant field and the exact mathematical target for each study. Do not retroactively rename a Raw run as NBO, or treat a finite action oracle as unlabeled actor training.

Keep the joint-loss counterexample as a current technical remark/proof if it is needed to identify the block graph. Its old-draft polemic and successive repairs belong in the development archive. Keep the viscosity counterexample and boundary/stopping qualifications as current mathematical content.

## One theorem chain, with explicit domains

Use a single notation table: policy pi; deployed candidate alpha; value V^pi; neural value v; true costate q^pi; estimated costate q-hat; evaluation defect r; action gap delta; terminal/boundary defect B; mesh h; occupation measure mu^alpha; economic payoff J; direct gain Delta(alpha,beta). Avoid using the same letter for a state, utility process, empirical mean, and budget.

The central order should be:

1. Policy evaluation identifies the continuation object for a fixed feasible policy.
2. Feasible Hamiltonian improvement turns evaluation/costate error and action suboptimality into a decision loss.
3. Performance difference integrates that loss under the deployed candidate's discounted occupation measure. Any weighting change requires an explicit bound.
4. A declared computation encloses or estimates each term. A nested-grid difference is not substituted for a discretization bound; the noise of the reference remains separate.
5. The capital theorem supplies a policy-specific continuous-time payoff interval and a separate anchor-based optimality account.
6. Simultaneous common-path contrasts compare methods' selected candidates. Method-level inference adds its own training-randomness layer.
7. Finite sensing transfers the certificate for the exact protected parent and its mesh to the measured-state implementation.

The differential/monotone/viscosity results remain in the current article and technical appendix with their original content and full proofs, but they are not represented as measured convergence of the executed optimizer. The sharp log-capital theorem must display its structural assumptions. A new tighter high-dimensional account belongs beside that theorem if established; scalar losses cannot supply it.

## Current supplement and archive boundary

The current supplement should contain subject-based appendices, not revision-based chapters:

| Current appendix | Content that must remain current |
|---|---|
| A. General Bellman and approximation arguments | Policy evaluation/recursive gradient, complete proofs of smooth and monotone certificates, viscosity selection, boundary/coverage accounts, guarded nodal evaluation, signed action envelopes. |
| B. Capital verification and information | Curvature/spectral anchor proof, exact payoff identity, diffusion/clipping/arithmetic/tail accounts, direct simultaneous inference, filtration/randomization and finite-sensing proofs. |
| C. Economic applications | Full recursive utility, preference normalization and reflection/stopping model, constrained policy conditions, welfare/compensation account, temporal equilibrium and spike proof, strategic game and complete unilateral deviations. |
| D. Numerical methods and evidence | Current protocol and full results, architecture and oracle accounting, reference convergence, method-level/work accounting, scalar stencil and residual diagnostics, sensing accounts, unique original laboratories and failure evidence. |
| E. Reproducibility index | One-page navigation to immutable sources, all run-level rows, artifacts, scripts, environments and schema definitions. Full row files remain accessible without being repeated in several typeset tables. |

Only duplicated historical iteration genealogy is assigned to the development archive. A file containing a unique theorem, application derivation, numerical counterexample, failed experiment, or a unique evidence row is not an archive-only candidate merely because it is in an old revision directory.

Safe initial archival units:

- supp.tex's successive revision-roadmap prose, including the stale assertion that R11 is current.
- The already duplicated R6 preference/game discussion within r8_supplement_layout.tex, but only after verifying the precise economic result is present in Appendix C or D.
- retained_conclusion.tex: a prior concluding interpretation, preserved intact in the pinned snapshot.
- Repeated learning, selection, and work-description paragraphs across R10/R11 studies, after their distinct algorithms, training protocols, and numerical rows have explicit current destinations.
- Multiple copies of the same theorem statement/proof: keep one authoritative current statement/proof and map each previous occurrence to it. Do not declare two mathematically different variants duplicates.

Do not classify retained_applications.tex or retained_proofs.tex as archival blocks. Split them by labeled section, retain their unique mathematics, and reorganize their nested inputs. The same caution applies to R8/R9 envelope and refinement material.

An archive map should record: reviewed commit; source path; line interval and enclosing label; exact content SHA-256; Git blob; classification (current, consolidated duplicate, historical narrative); current destination; archive destination; reason; and any change in notation or hypotheses. Prefer referencing the existing immutable revision path at the pinned commit over creating a second unexplained copy. Add an archive index and a preserved reviewed-root bundle so the entire R14 reading copy remains rebuildable.

## Evidence presentation and semantics

Give the reader one evidence design table with columns: economic model/domain, method and evaluation variant, target, selected checkpoint, training-randomness design, final paths, accuracy object, work boundaries, and theorem used. Report existing and new studies as distinct prespecified experiments under this common schema; do not pool incompatible budgets or imply the R14 streams were newly randomized.

Keep the following R14 findings adjacent to any new positive claim: 120 primary and 42 fixed-work direct intervals contain zero; the twelve principal NBO-minus-Raw means are negative; Raw's fitting clock and mean favor Raw in all six principal fixed-work cells; the six critic mechanism panels favor the raw costate diagnostic. Preserve the scalar ranking reversal off the origin and all unreached targets.

The new main tables should answer parallel questions: method-level economic accuracy; complete work to a common target; occupation-based mechanism terms in payoff units; high-dimensional anchor/optimality comparison; original application-specific results; scalar/classical reference convergence; implementation allowance relative to gain. Consolidation must retain the denominator, object, units, and uncertainty attached to every count.

Use distinct machine fields: method_id; source_method_id; evaluation_variant; policy_id; comparator_id; estimand; economic_domain; training_randomness_scope; sampling_scope; lower/upper endpoint; threshold; stopping_rule; total_wall_seconds; timed_components; simulator_transitions; derivative_evaluations; optimizer_updates; peak_memory; failures; source_commit. Raw's old method=nbo record is preserved and interpreted through a documented adapter; new records use raw_costate directly. A positive_schedule_gain flag must never be reused as positive_method_difference.

For finite sensing, describe the actual institution as a controller receiving specified capital measurements at scheduled dates, retaining an internal recurrent state, and supplying the stated private randomization. Distinguish that practical contract from the exact continuous-history representation. Report allowance/gain ratios for the same parent, mesh, population, and units; never divide an allowance for a coarse parent by a certificate for a different parent.

## Reply strategy and completion conditions

Open the response by acknowledging that the report accepts R14's source integrity and identifies a substantive incremental-value problem. Retain its verified adverse evidence. State the chosen NBO research center and identify the single new algorithm/theorem/evidence chain. Explain the preservation map and the removal of duplicate genealogy.

Then answer all B and M identifiers explicitly. Related replies may cross-reference one another, but no identifier should disappear inside a generic “addressed above.” Each final reply needs: the objection, the exact change, its current section/theorem/table, the evidence artifact and source identity, and any unresolved limit. The companion JSON supplies issue-specific closure checks. Until those checks pass, its scientific statuses remain pending.

Do not say the journal rejected the paper: this is an owner-commissioned advisory report, not an Econometric Society editorial decision. Do not present another compiled manuscript, a renamed method, or a new ledger as the scientific answer to B1–B6.

## Verified official style guidance

Checked from the current official author-support chain:

- Use the maintained econsocart package and the supplied article/supplement templates; do not edit the class or configuration. The template uses ecta,nameyear,draft for submission; final is for prepublication.
- The sample specifies an abstract of at most 150 words, recommends 3–8 keywords, and favors a self-contained abstract with little mathematics.
- Use sequential result counters, separate definition/axiom counters, paragraph* for unnumbered run-in headings, and equation numbers only where subsequently referenced.
- Use author–year citations with a complete, mutually consistent bibliography. Give tables informative notes, leading zeros on decimals, no vertical rules, and confidence intervals rather than significance stars.
- Keep figures intelligible in grayscale; use standard appendix headings and precise subsection references.

These are explicit support-document instructions. The recommendation to lead with an economic problem and an integrated theorem/evidence narrative is editorial judgment informed by this referee report, not a quoted journal rule.

Primary URLs:

1. https://onlinelibrary.wiley.com/page/journal/14680262/homepage/forauthors.html
2. https://www.econometricsociety.org/publications/econometrica/information-authors
3. https://www.e-publications.org/es/support/
4. https://vtex-soft.github.io/texsupport.econometricsociety-ecta/
5. https://github.com/vtex-soft/texsupport.econometricsociety-ecta/blob/master/ecta_template.tex
6. https://github.com/vtex-soft/texsupport.econometricsociety-ecta/blob/master/ecta_sample.tex

The Society index is retrievable and links its submission/publication instructions, but those deeper pages were blocked in this session. I therefore do not certify a current hard article or supplement page limit. A 2022 official committee record mentions a then-current 25-page typeset online-appendix policy, which is historical and insufficient to establish today's rule. Do not substitute Theoretical Economics' 45-page guidance for Econometrica's rules.

## Integration acceptance checks

The final editorial checks are substantive preservation and clarity: one Algorithm 1; one notation system; current proofs cover all cited theorems; all 230 reviewed labels have a classified destination or justified consolidation; all four original economic application families remain visible in the main article and complete in current appendices; no stale “R11 is current” language; no duplicated historical conclusion; all B1–B7/M1–M9 responses carry exact destinations and evidence statuses; all adverse and failed results remain accessible; no new claim outruns its artifact. Compile and visually check the resulting reading copy after the new mathematics and evidence are settled.
