# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Latest source-and-evidence revision reviewed:** `revision/econometrica-nbo-r47-integrated-source-2026-10-08`  
**Pinned revision commit:** `27f3c36984f00ff060d0586712a01b87355914ba`  
**Pinned revision tree:** `c75871b821aa3f3e540b627c60891766c1f302b6`  
**Intended but absent canonical branch:** `revision/econometrica-nbo-r47-review-ready-2026-10-08`  
**Inherited review-ready manuscript:** R46 commit `c3930399e3b8267451096d0e70ea67f49510065e`  
**R47 protocol commit:** `7d2329406b53047eb6fa35fe366d94f2fcb37a12`  
**R47 scientific source:** `04d0638169ae7adbdd8bb21f9d1fea5b1ef68de2`  
**R47 evidence commit:** `4da0b2c286793f75a56ad6d8228cb0da82aabc60`  
**R47 study run / artifact:** `37663771622` / `11502335616`  
**Report date:** 8 October 2026  
**Recommendation:** **Reject in the present form and do not invite another ordinary revision of the cumulative manuscript. A new, sharply focused paper on acquisition-aware, witness-preserving Bellman certification for constrained Lipschitz dynamic programs could merit evaluation after the contribution is isolated, the publication object is made canonical, and direct constrained-policy and total-work comparisons are supplied.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R47 is a serious response to the R46 report. It addresses several objections with new mathematics and new evidence rather than by changing terminology. The revision now:

1. evaluates the actual frozen witness, nearest-cone, and spline policies through direct expected-cost differences rather than subtracting separate regret bounds;
2. incorporates numerical selector error, state acquisition, capacity repair, and action quantization into one feasible policy-loss account without assuming continuity of the witness actor;
3. executes the state-dependent feasible-witness construction in a two-state nonlinear investment economy with continuous innovations and endogenous capacity;
4. proves and tests that the native min-plus envelope and its affine--ReLU representation are the same policy construction when they share labels, witnesses, and tie rules; and
5. reconstructs the complete scalar certificate frontier rather than reporting only the original coarse target list.

The main new theorems appear internally coherent under their stated assumptions. I found no immediate algebraic contradiction in the acquisition-aware one-sided policy comparison, the capacity-repair corollary, the direct policy-cost telescoping identity, the deterministic support calculation, or the explicit primitive bounds for the two-state constrained economy. The numerical record is also unusually transparent. Failed targets, ambiguous actor queries, active repairs, unfavorable timings, and unresolved signed comparisons are retained.

The resulting evidence is informative, but it is not favorable to the broad method claim.

The direct scalar comparison comprises forty groups and 120 pairwise contrasts, with 131,072 common paths per group. Every simultaneous interval lies inside the predeclared band `±1/1024`; every interval also contains zero. This establishes tolerance-based proximity for the frozen policies and declared initial laws under the stated independent-bin model. It establishes no signed ranking, no equality, and no calibrated welfare equivalence.

The new constrained experiment contains twenty-four services and seventy-two rungs. Both witness and bilinear fitted-value iteration reach only the coarse target `4` in all twelve services and reach none of `2`, `1`, or `1/2` within the cap. The witness certificate is 13.3--17.2 percent smaller at the finest rung, but bilinear fitted-value iteration is faster in all twelve matched services. On median recorded times, the witness is approximately 21.2--21.6 times slower. The new constrained policies are not compared by a direct expected-policy-cost experiment, so the smaller witness bound does not establish a lower actual cost.

The acquisition study is a meaningful implementation exercise: repair is active in 36,070 state--date cases. It also shows that acquisition error can consume a material part of the certificate. At coordinate radius `1/256`, the added policy-loss allowance is as large as approximately `0.3602` without quantization and `0.3648` with the declared action spacing. Those are theoretical uniform allowances, not average losses; nonetheless they are economically non-negligible relative to the already coarse constrained bounds.

The representation-control result resolves an attribution question in the unfavorable direction for a neural-method claim. The paper proves that the native min-plus implementation and its exact ReLU realization return the same continuation, actor, certificate, and policy cost. The executed diagnostic finds zero binary64 difference on the declared grid, within its arithmetic allowance. Thus the central witness construction is a classical Lipschitz-envelope algorithm with a neural circuit representation, not an identified neural computational advantage.

There is also a threshold publication problem. The R47 README names `revision/econometrica-nbo-r47-review-ready-2026-10-08` as the authoritative object, but that branch does not exist. The repository root on the latest R47 source branch still identifies R46 as canonical. The first R47 publication run completed all 69 tests and all three LaTeX passes, then stopped because `pdfinfo` was unavailable. The correction run was cancelled during dependency installation; all reconstruction, validation, clean-rebuild, commit, and review-ready-branch steps were skipped. A preserved artifact contains a 50-page article, 41-page supplement, and 11-page response, but that failed-run artifact is not a completed canonical submission.

R47 therefore improves the underlying science while reinforcing the substantive conclusion of the preceding review. The strongest successful contribution is a method-neutral, acquisition-aware policy-certification construction for a specified class of Lipschitz dynamic programs. It is not evidence that Neural Bellman Operators dominate strong conventional methods, scale beyond low-dimensional tensor covers, or unlock an Econometrica-level economic result.

## 2. What R47 successfully repairs

### 2.1 The actual policy difference is now the estimand

R46 correctly noted that tighter regret upper bounds do not rank realized policy costs. R47 now compares the frozen policies directly through an own-continuation telescoping score whose expectation is the actual expected policy cost. Common innovations are used correctly to reduce variance, and the support account retains the signs of optimal and selected-policy residuals rather than subtracting two nonnegative regret bounds.

The study includes every common original crossing and all three policy pairs. It does not select only favorable initial states. The uniform initial-state law is treated as a distributional estimand, while `1/8`, `1/2`, and `7/8` remain separate declared states.

### 2.2 Discontinuous witness selection is handled at the objective level

The acquisition theorem does not impose a fictitious Lipschitz condition on the selected actor. It permits a numerical selector with an objective excess, an acquisition set containing the true state, and a repaired action feasible throughout that set. The policy-loss account charges selector error, twice the continuation modulus times the acquisition radius, repair displacement, and action quantization.

This is the right conceptual way to treat a discontinuous witness index.

### 2.3 State-dependent feasibility is executed, not merely stated

The new two-state economy has an endogenous capacity interval, coupled nonlinear transitions, continuous common uncertainty with opposite exposures, nonlinear state and action costs, and a continuous feasible action set. The paper supplies explicit invariant-domain, Lipschitz, cover, integration, and repair constants. The executed deployment checks feasibility on the whole acquisition box, not only at its midpoint.

This resolves the purely algebraic status of the corresponding R46 extension.

### 2.4 The continuous innovation law is not silently replaced by a finite law

The constrained study uses midpoint integration together with the explicit deterministic remainder `L/(32M)`. Numerical integration error and label rounding are additional allowances. This is a credible and transparent treatment of the stated uniform innovation law.

### 2.5 The identical non-neural control is made explicit

R47 proves representation equality between the native minimum of cones and its ReLU reduction tree. The same witness index and tie rule are carried through both representations. The paper does not count the two encodings as independently trained methods, and it states that the representation label does not alter covering or Bellman-query factors.

This is an important correction to method attribution.

### 2.6 The complete frozen certificate frontier is reconstructed

The union of exact rational certificate breakpoints partitions the full positive tolerance axis. The reconstruction reports favorable, unfavorable, tied, one-sided-attainment, and jointly unattained intervals. It does not replace the original prospective targets with favorable retrospective targets.

### 2.7 Adverse evidence and publication failures are preserved

R47 reports that:

- all 120 direct intervals contain zero;
- bilinear FVI is faster in every constrained common crossing;
- neither constrained method attains the three tighter targets;
- the native and ReLU versions are the same mathematical construction;
- no neural speed advantage is established;
- no new calibrated application is supplied; and
- the publication workflow did not complete.

This level of disclosure is exemplary.

## 3. Blocking concerns

### B1. R47 is not a canonical, completed submitted manuscript

The intended `r47-review-ready` branch is absent. The root README at the latest source commit still designates R46 as canonical. The R47 directory contains source fragments, response, results, and audits, but the assembled `ECTA.tex` and `supp.tex` are not committed there as ordinary authoritative files.

The first publication run produced assembled sources and PDFs but stopped after compilation because `pdfinfo` was missing. The next run verified source identities, then was cancelled during dependency installation. It skipped result reconstruction, tests, compilation, manuscript verification, clean rebuild, final delivery binding, and the branch push.

A failed-run artifact can assist a referee, but it is not a substitute for a single immutable review-ready branch whose head, tree, sources, PDFs, release audit, and evidence identities agree. This threshold issue must be resolved before any journal submission.

### B2. The central witness backend is not a distinctively neural numerical method

The mathematical continuation is a finite minimum of Lipschitz cones. Its witness policy is the action index attached to the active cone. Proposition 47 explicitly proves that a conventional min-plus implementation and the affine--ReLU realization return the same continuation and policy.

Consequently, the new certificate, acquisition theorem, direct policy cost, and constrained performance are properties of the underlying envelope-and-witness algorithm. R47 establishes no computational saving from the neural representation. Indeed, the publication summary records `neural_speed_advantage_established: false`.

The term “Neural Bellman Operators” may remain as a broader research program, but the current central theorem should not be presented as method-specific neural evidence.

### B3. The direct scalar comparison establishes only a declared tolerance band, not a ranking or calibrated economic equivalence

All 120 intervals contain zero. The largest absolute endpoint is approximately `0.00020777`, inside the declared `1/1024 ≈ 0.00097656` band. This is a valid simultaneous proximity statement under the frozen-policy, independent-bin model.

The economic interpretation is nevertheless limited:

- zero remains unresolved in every comparison;
- `1/1024` is a stated numerical decision tolerance, not a calibrated welfare threshold;
- the result concerns the declared initial laws, not all states;
- it is conditional on fixed policies and the independent-bin sampling model; and
- it says nothing about the cost distribution of newly constructed policies.

The comparison repairs an inferential defect. It does not establish an Econometrica-level economic result or a method advantage.

### B4. The new constrained evidence favors the conventional comparator on work and does not compare actual policy costs

At the finest rung the witness bound is smaller in all four economic cells, by approximately 13.3--17.2 percent. But both methods cross only target `4`, at the same final resolution, and both miss `2`, `1`, and `1/2`.

The conventional bilinear FVI implementation is faster in 12/12 matched services. Median witness/FVI time ratios are approximately:

- `21.60` for `T=2, p=1`;
- `21.56` for `T=2, p=4`;
- `21.47` for `T=3, p=1`; and
- `21.21` for `T=3, p=4`.

The study explicitly excludes an independent direct cost comparison from these constrained service clocks, and no separate comparison is supplied. A smaller worst-case bound therefore cannot be translated into a lower actual policy cost. The principal empirical conclusion is a bound-versus-work tradeoff that strongly favors FVI on work.

### B5. The advertised scalar work-to-bound frontier is a Bellman-query frontier, not a complete-work frontier

The reconstructed partition reports nineteen intervals with fewer witness prefix Bellman queries, one with fewer spline queries, twenty ties, four attainable only by witness, and four unattained by both. This is useful descriptive information.

But Bellman-query counts are not complete work. Native cone evaluation, spline evaluation, selector construction, arithmetic precision, storage, and verification costs differ. Earlier matched clocks favored the spline. The R47 frontier therefore cannot be described as a complete resource frontier unless it reports a common, method-inclusive cost metric at every breakpoint.

This distinction matters because the central empirical claim is precisely whether certificate sharpness translates into lower work at a target.

### B6. The nonlinear construction remains low-dimensional and tensor-cover dependent

The new executed economy has two state coordinates, one scalar action, horizons two and three, and a three-rung uniform tensor ladder ending at `N=16`. The paper itself derives leading work of:

- `O(TN^6)` for direct cone construction; and
- `O(TN^4)` for bilinear FVI,

with `O(TN^2)` stored labels and actions.

The theorem leaves the state and action covering factors explicit in general dimension. No adaptive partition, sparse grid, low-rank representation, or dimension-scaling experiment is executed. The two-state example is a useful minimum test of feasibility and acquisition; it is not evidence for the broad high-dimensional NBO program.

### B7. Acquisition can consume a material part of the certificate, and the sensor contract is not economically calibrated

The deployment study successfully exercises repairs and quantization. It also shows the sensitivity of the guarantee:

- coordinate radius `1/4096` adds as much as approximately `0.0225` without quantization and `0.0271` with it;
- coordinate radius `1/256` adds as much as approximately `0.3602` without quantization and `0.3648` with it.

These are uniform upper bounds rather than expected losses, but they are substantial relative to the constrained certificates. The radii are numerical scenarios, not derived from a sensor, observation technology, or economic information cost. The paper therefore establishes how to charge acquisition error, not that the resulting acquired policy is sufficiently accurate in an economically relevant implementation.

### B8. The reliability evidence is finite-object and deterministic

The three constrained repetitions have identical checkpoint hashes. They are timing repetitions of the same deterministic construction, not independent trained policies. CPU affinity and library threads are controlled, but CPU frequency is not. The direct comparison freezes previously constructed policies.

Accordingly, R47 supports:

- deterministic theorem reliability under its premises;
- correctness of specified stored objects; and
- descriptive timing variation on one runner class.

It does not support a population success probability for neural training, a hardware-general timing distribution, or robustness across economic tasks.

### B9. The broad application framing is not supported by the R47 theorem or experiment

The acquisition-aware theorem uses monotone, cash-invariant recursive evaluation, while the direct sampling theorem is expectation-specific. The new constrained experiment is a compact finite-horizon control problem. It does not establish the separate transversality, utility-domain, equilibrium, observation, or diffusion-approximation obligations of recursive utility, endogenous preferences, temporal selves, games, and controlled diffusions.

The manuscript states many of these qualifications, but the title and cumulative scope still invite a platform-level interpretation. Preservation of historical applications is not new validation of those applications by R47.

### B10. The economic contribution remains too small for Econometrica

The new constrained economy is explicitly normalized and theoretical. The direct scalar tolerance is not calibrated. The constrained tight targets are not attained. There is no direct constrained-policy value ranking. The conventional method is substantially faster. The native/ReLU representations are equivalent.

R47 makes a credible numerical-certification contribution, but it does not use that contribution to obtain a substantive economic result that strong conventional methods cannot obtain, nor does it establish a broadly useful efficiency frontier. That is the decisive journal-level shortfall.

## 4. Major comments and required changes

### M1. Create one canonical review-ready object

Commit the assembled main article, supplement, response, tables, audit, and PDFs on the branch named by the README. Complete the clean rebuild and final-delivery gates. Make the root README point to that branch. Do not ask a referee to infer the submitted paper from a failed workflow artifact.

### M2. Reframe the central contribution around the underlying algorithm

Present the witness method first as a min-plus/Lipschitz Bellman construction with a feasible witness actor. Treat the ReLU circuit as one exact representation. Any neural-specific claim should identify a computational or approximation property unavailable to the identical native implementation.

### M3. Add a direct constrained-policy comparison

Evaluate the new two-state witness and bilinear-FVI policies on common innovations and declared initial laws. Report actual expected-cost differences with a prespecified economic margin. A comparison of separate all-state bounds is not a substitute.

### M4. Report total work-to-certificate curves

For every bound breakpoint, report a common total-work metric including target construction, continuous-law integration, representation evaluation, policy selection, certification, failed rungs, repair, arithmetic, storage, and durable output. Keep Bellman queries as a component, not the headline measure.

### M5. Add adaptive conventional baselines

The current comparison uses uniform tensor grids. Include at least one adaptive-partition, sparse-grid, or error-driven fitted-value method facing the same continuous law, state-dependent capacity, and final verifier. The purpose is to test whether the certificate construction improves the frontier rather than merely changing the interpolation basis.

### M6. Demonstrate scaling beyond the two-state tensor laboratory

A useful next design would vary state dimension, horizon, action dimension, capacity geometry, and acquisition radius. If tensor covers become infeasible, that is itself an important result and should motivate a different approximation architecture rather than be hidden by theorem notation.

### M7. Tie acquisition error to an economic observation model

Specify a sensor or data-acquisition technology, its cost, and its error set. Report the policy bound as a function of that cost and compare it with the economic value differences at issue. The current dyadic radii are implementation stress cases, not an economic information design.

### M8. Use economically meaningful targets

Explain why a target such as `4`, `1/1024`, or the chosen acquisition allowance is relevant to a decision. A normalized numerical tolerance may be legitimate, but Econometrica readers need either a welfare interpretation, a decision threshold, or a substantive comparative-static conclusion.

### M9. Separate deterministic theorem claims from method-level empirical claims

Keep exact construction guarantees, finite-catalogue attainment, timing repetitions, and policy-sampling inference in separate statements. If optimizer reliability is part of the contribution, define a training-randomness distribution and execute enough independent training objects to estimate it.

### M10. Focus the paper

A focused submission should contain one model class, one witness construction, one acquisition contract, one direct constrained-policy experiment, and one complete work frontier. The historical platform can remain archived without making the active article responsible for every prior application.

## 5. A focused publishable route

The strongest paper latent in R47 would be approximately:

> **Acquisition-Aware Witness-Preserving Bellman Certification for Constrained Lipschitz Dynamic Programs**

Its main theorem chain would be:

1. a one-sided policy sandwich;
2. witness-preserving Lipschitz extension;
3. state-dependent feasible repair;
4. acquired-state and finite-precision realization;
5. direct expected-policy-cost comparison; and
6. total work-to-certified-accuracy accounting.

The numerical study should include:

- a native min-plus implementation as the primary algorithm;
- a ReLU representation as a representation experiment, not a separate method;
- direct policy-cost comparisons in the constrained economy;
- adaptive conventional baselines;
- dimensions and tolerances sufficient to reveal scaling;
- calibrated or decision-relevant acquisition errors; and
- complete, repeated end-to-end work measurements.

Such a paper could make a useful contribution to reliable computational economics. It would be substantially narrower and stronger than the current cumulative NBO manuscript.

## 6. Independent verification performed for this report

I performed the following checks against the pinned R47 source-and-evidence snapshot.

1. **Study artifact identity.** The downloaded study artifact has SHA-256 `782e437ccb4886a18f6692b02d0e4a109abe67d729e53f5c266cf1f5df2428db`, matching GitHub.
2. **Frozen sources.** All five source hashes in `SOURCE_SHA256.json` match.
3. **Direct records.** All forty direct record hashes match the complete ledger. The catalogue contains 120 contrasts, 5,242,880 total paths, thirty unique policy checkpoints, and 44,040,192 actor queries. The ambiguity enclosure is active in 3,932,160 queries, approximately 8.93 percent.
4. **Direct conclusions.** All 120 intervals contain zero and all 120 lie inside `±1/1024`. The largest absolute endpoint is approximately `0.00020777`; the largest interval width is approximately `0.00034328`.
5. **Constrained records.** All twenty-four service records and seventy-two checkpoint hashes agree with their ledgers. The three timing repetitions share identical checkpoints.
6. **Constrained attainment.** Each method reaches target `4` in 12/12 services and reaches none of `2`, `1`, or `1/2`. Bilinear FVI is faster in all twelve matched services.
7. **Bound/work tradeoff.** At the finest rung, witness bounds are approximately 13.3--17.2 percent smaller; median witness/FVI time ratios are approximately 21.2--21.6.
8. **Deployment.** The seventy-two acquisition cases cover twelve policies and record 36,070 active repair events. The largest added bound rises to approximately `0.3648` in the coarsest acquired-state and quantized-action case.
9. **Representation control.** The twenty-four representation checkpoints contain ninety-six function-date comparisons. The maximum stored native/ReLU binary64 difference is zero; the records explicitly state that no neural acceleration is established.
10. **Publication artifact.** The preserved first publication artifact has SHA-256 `65a3c49014b58f1708802496106175631b0bb0cba9b1bfc6f00128e6afbc1bbf`. Its assembled `ECTA.tex` and `supp.tex` match the committed source bindings. It contains compiled 50-page and 41-page PDFs, but it belongs to the failed run that stopped before final delivery.
11. **Publication status.** The latest workflow verified source identities and then was cancelled during dependency installation. It skipped reconstruction, tests, compilation, clean rebuild, final binding, and the review-ready branch push.
12. **Scope.** I did not rerun the scientific simulation or timing services. A new run would create new observations rather than verify the frozen clocks. The review directory includes a standard-library script and its machine-readable output for the checks above.

## 7. Recommendation

R47 is mathematically and computationally more complete than R46. It closes the direct-cost gap for the scalar policies, executes state-dependent feasibility and acquisition, and openly separates a classical envelope from its ReLU representation. These are meaningful advances.

They do not, however, establish the contribution claimed by the cumulative manuscript. The central construction is not specifically neural; the direct comparisons identify no signed ranking; the new constrained policies lack a direct cost comparison; the conventional FVI comparator is more than twenty times faster in the recorded study; the tighter targets remain unattained; acquisition can materially widen the bound; and the method remains a low-dimensional tensor-cover construction. The intended canonical R47 branch was also never produced because the publication gate did not complete.

I therefore recommend **rejection in the present form and no further ordinary revision of this cumulative submission**. A new, focused paper on acquisition-aware witness-preserving Bellman certification could merit serious evaluation after the publication object, comparative design, scaling evidence, and economic interpretation are rebuilt around that narrower contribution.
