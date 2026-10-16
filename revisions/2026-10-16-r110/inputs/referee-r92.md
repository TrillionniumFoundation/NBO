# Referee Report on "Neural Bellman Operators"

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r92-referee-ready-2026-10-13`  
**Pinned revision commit:** `d1d1fc1f2208023a65419a616bccae0e4cdf7aa4`  
**Pinned revision tree:** `9ebf0f85293f434b12c83cfd74821e199b5b3a1b`  
**Pinned main manuscript:** `revisions/2026-10-13-r92/ECTA.tex`, Git blob `249d5ba6676c0c3bd5584333743b26a726981594`  
**Pinned technical supplement:** `revisions/2026-10-13-r92/supp.tex`, Git blob `44b188c2ea3d968a03b5c640863d0ec62001c0cb`  
**Pinned numerical and development appendix:** `revisions/2026-10-13-r92/appendix.tex`, Git blob `59925fa8503d743399e331bff0f1b681ff11ad1f`  
**Pinned response:** `revisions/2026-10-13-r92/response.md`, Git blob `303f8c193506f361301aa9b6239b6e1d978b863d`  
**Pinned release record:** `revisions/2026-10-13-r92/audit/reproduction92/RELEASE92.json`, Git blob `8d47542371c9c7fc8869807f354eb6f2f68cd86d`  
**Report date:** 13 October 2026  
**Recommendation:** **Reject in the present form and do not continue this cumulative manuscript through another ordinary revision round. The new reference-centered qualification result is a credible component for a focused paper on risk-averse dynamic programming, but R92 still does not identify an Econometrica-level neural, computational, or economic contribution for the full Neural Bellman Operators platform.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R92 is a serious and technically substantial revision. It decisively resolves the principal procedural defect of the R84 delivery: the current object is now a complete, source-bound, review-ready package. The active submission comprises a 90-page article, a 48-page technical supplement, a 125-page numerical and development appendix, and a 4-page response. The release record binds 360 tests with no skips, clean source-only reconstruction of all four PDFs, a separate new-science replay, bibliography and document checks, and visual inspection of all 267 page layouts. I regard the package construction and preservation discipline as exceptionally strong.

The new mathematical addition is also more substantial than the finite-menu bookkeeping emphasized in R84. The paper centers the original conditional risk dual at the actual stored continuation. It obtains the exact identity
\[
\mathcal E^f(z)=\rho(f+z)-\rho(f),
\]
retains the induced nonnegative dual penalty, and propagates state-dependent lower and upper potentials through the original Bellman recursion. The resulting theorem compares the complete implemented policy with the original Bellman optimum rather than with a changed objective. In a finite affine risk representation, the paper gives a penalized risk-occupation formulation, rational primal and dual witnesses, and a strict support-function test for excluding risk pieces on an independently verified error set. The proof correctly preserves the order \(\inf_a\sup_q\), distinguishes risk-distorted occupation from physical occupation, and retains equality at the exclusion threshold. I found no immediate algebraic contradiction in the centered identity, the state-dependent certificate, the finite occupation representation, or the support exclusion result under their stated assumptions.

The associated verification is unusually careful. The independent checker uses the threshold representation of average value at risk and separately coded original-value and descendant recursions. It reports 84 models, 252 interval configurations, 73,564 certificate inequalities, 17,711 strict kernel exclusions, 1,728 complete policies at the shortest horizons, and 5,184 initial-state tree/backward equalities. The adversarial catalogue tests changing risk maximizers, equality at the pruning boundary, invalid joint minimization over actions and risk kernels, zero discounts, state-dependent bias, corrupted flow masses, and reversed residual intervals. This is valuable evidence about the correctness of the new finite exact implementation.

These accomplishments materially improve the paper. They do not, however, resolve the central Econometrica question.

The first difficulty is identification. The centered guarantee depends on the stored continuation as a mathematical function, not on whether that function is represented by a neural network. The paper explicitly states that equivalent neural and non-neural representations receive identical centered guarantees. The new theorem therefore strengthens qualification for any supplied continuation; it does not identify a neural numerical method.

The second difficulty is empirical. R92 adds zero fit attempts and zero independent economic observations. The frozen shared-proposal experiment remains unfavorable to the ReLU proposal: adaptive search uses fewer action-value queries in every evaluation dimension, with totals \(975,993,969\) against ReLU totals \(987,1017,987\). The independently evaluated investment result selects the fine calibrated Bernstein controller. It identifies several improvements and noninferiority, but its comparison with fine calibrated ReLU still crosses zero. These are useful and honestly reported findings, yet they do not establish neural superiority or a new R92 economic result.

The third difficulty is computational scope. The new long-horizon catalogue reaches 64 dates only in prescribed three-state, two-action rational fixtures. It demonstrates that stored backward recursion avoids repeated descendant evaluation for a finite exact risk representation. It does not demonstrate tractability for the continuous-state, high-dimensional, multivariate-control problems used to motivate the platform. The inherited two-control experiment still rises from 44 Bellman action queries at two dates to roughly 8.1 million at four dates, with complete times of 530--841 seconds. The independent largest-vector implementation and matched vector tournament remain explicitly outstanding.

The fourth difficulty is scale and focus. The active package contains 267 pages and continues to carry a wide platform of expected-cost control, nonlinear recursive preferences, joint-domain construction, diffusions, endogenous preferences, temporal selves, games, training, deployment, economic assignment, and several generations of numerical evidence. The strongest new R92 contribution is much narrower: a reference-centered qualification and occupation account for recursive risk. That contribution may be publishable, but in the present cumulative article it is not sufficiently isolated, compared with the closest established risk-dynamic-programming objects, or tied to decisive computational and economic evidence.

I therefore recommend rejection in the present form. I would encourage a new, sharply focused submission built around reference-centered qualification for risk-averse dynamic programming, accompanied by an executed continuous-state benchmark, matched neural and non-neural representations, a complete resource ledger, and new prospective economic evaluation.

## 2. What R92 successfully repairs

### 2.1 The submission is now genuinely review ready

Unlike R84, R92 supplies a completed publication chain. The four current documents are compiled from one source-bound snapshot; the release gate passes; the PDFs have matching clean reconstructions; and the visual record is tied to the current hashes. This closes the earlier procedural blocking concern. The current referee assessment can therefore be substantive rather than conditional on a future build.

### 2.2 The recursive preference is retained rather than linearized away

The centered operator is defined from the original conditional risk evaluation and its dual penalty. The construction does not substitute expectation under the physical law, freeze one reference maximizer, or replace a static risk objective by a nested one. The theorem is correctly stated under explicit dual-representation, bounded-domain, measurability, and selection hypotheses.

### 2.3 The original-optimum orientation is explicit

The lower certificate is required for every original feasible action, while the upper certificate follows the supplied complete policy. This is the correct orientation for comparing the implemented policy with the original Bellman optimum. A sampled-action minimum or a favorable risk kernel cannot silently stand in for the required all-action inequality.

### 2.4 The state-dependent account can be strictly sharper than a scalar account

The exact recursion propagates where an error occurs and which risk kernels can make it consequential. The absorbing-state example shows a genuine distinction: the inherited scalar account grows with the horizon while the exact state-dependent policy-loss certificate is zero. This is a mathematical sharpening rather than a relabeling of the same scalar bound.

### 2.5 Risk occupations and support cuts are carefully oriented

The finite representation uses risk-distorted flows, not physical frequencies. It retains the \(\inf_a\sup_q\) order. The strict support inequality excludes a risk piece only over a previously verified error set, and equality is retained. These conventions avoid several common but serious numerical mistakes.

### 2.6 The independent checker is meaningfully different

The checker does not merely reload the production centered-risk calculation. It uses the scalar-threshold formula for AVaR, separate original-value recursions, complete-policy enumeration at the short horizons, and an un-memoized descendant evaluator. The exact failure tests and fail-closed release record are strong reproducibility features.

### 2.7 Evidence boundaries are disclosed rather than blurred

The paper expressly states that the new catalogue adds no fitting attempt and no independent economic row; it does not claim to complete the inherited largest-vector implementation; and it does not convert certificate tightening into a speed, welfare, energy, or monetary result. The negative held-out ReLU comparison and unfavorable historical records remain visible.

## 3. Blocking concerns

### B1. The new theorem is continuation-specific, not neural-specific

The centered penalty and all subsequent guarantees depend on the values of the stored continuation. Equivalent neural, polynomial, spline, tabular, or analytic representations of that continuation receive the same theorem. Correctness, original-optimum orientation, and support exclusion are therefore properties of the verifier and the represented function, not of the neural architecture.

This does not make the theorem unimportant. It means that the title and central numerical-method claim are not identified by the new result. R92 remains strongest as a paper about qualified approximate dynamic programming under recursive risk, not about a distinctively neural Bellman operator.

### B2. The incremental novelty relative to established risk dynamic programming is not yet sharply isolated

The paper properly attributes conditional risk duality, risk-averse dynamic programming, AVaR threshold formulas, entropic duality, weak duality, and finite backward recursion. The new contribution is said to be the reference-centered use of these objects for the stored NBO continuation, together with state-dependent original-optimum certificates, penalized occupations, support cuts, and paid precision.

That description is plausible, but the manuscript does not yet provide the theorem-by-theorem comparison needed for a top-field-journal novelty claim. Centering a convex dual around a reference function resembles an advantage or residual transformation; occupation measures and dual potentials are standard in finite dynamic programming and robust control; and support dominance among affine pieces is elementary convex analysis. The paper should identify exactly which existing theorem fails to provide the stated complete-policy bound and which additional NBO structure is indispensable. In the current form, the new chain reads as a careful and useful synthesis whose incremental conceptual novelty is narrower than the manuscript scale suggests.

### B3. Practical construction of the certificate is not demonstrated on the economically relevant continuous model

The theorem requires verified residual lower bounds for every original feasible action and upper control of the entire conditional risk envelope. For continuous actions, continuous successor states, and nonlinear risk, these can be the dominant numerical tasks. The finite exact catalogue sidesteps them by using three states, two actions, rational transitions, and exactly enumerated AVaR vertices.

The paper acknowledges this limitation, but acknowledgement does not supply the missing method. A numerical-method contribution should show how the all-action lower certificate, penalty enclosure, and support function are constructed in the original continuous investment model, with all discretization and integration errors carried through the theorem.

### B4. The new diagnostics validate identities, not computational advantage

The table of centered-risk diagnostics shows that the state-dependent bound is smaller than the scalar bound and records 11--22 cuts at the displayed radius. It does not compare complete runtimes against a strong alternative risk-DP implementation, measure the cost of generating the continuation and penalties, or determine whether support cuts reduce end-to-end work after their own verification cost is charged.

The 10-second independent audit of the rational catalogue is a verification receipt, not a performance benchmark. The paper needs an executed algorithmic comparison in which the centered method, an uncentered state-dependent method, a scalar method, and conventional risk-DP baselines solve the same economically relevant problem to the same original-optimum tolerance.

### B5. R92 adds no new evidence about learning, prediction, or generalization

The release record states zero new fits. The new continuations are prescribed mathematical fixtures. They do not test whether a learned continuation produces useful centered penalties, whether the support cuts survive estimation error, or whether a shared operator generalizes across endogenous states.

The only held-out shared-proposal experiment remains unfavorable to ReLU query work. Adaptive search is calibration-selected and uses the fewest evaluation queries in every dimension, tying only some comparators at dimension eight. A successful fit and a valid certificate remain distinct from incremental prediction value.

### B6. The economic evidence is inherited and does not establish a neural gain

The prospective investment evaluation is a genuine positive component of the broader project. Calibration selects fine calibrated Bernstein; seven of its eight evaluation comparisons have negative upper endpoints; and its regret is below the declared noninferiority margin. However, the comparison with fine calibrated ReLU crosses zero. The identified result is therefore a policy-quality result for a finite controller menu, not a neural-basis advantage.

R92 supplies no additional independent economic observations and does not narrow those intervals. The new risk diagnostics use synthetic rational primitives and are explicitly not investment-welfare observations. They cannot repair the absence of an R92 economic estimand tied to the new theorem.

### B7. The horizon result is conditional on a tiny exact state space

The finite risk-occupation recursion is an appropriate way to avoid repeated scenario-tree expansion once a finite exact affine risk representation and finite state aggregation are already available. Reaching 64 dates with three states demonstrates the recurrence, not high-dimensional scalability.

Risk-envelope enumeration, continuous-state aggregation, action minimization, residual construction, bit growth, and continuation evaluation are additional costs. The displayed maximum rational bit length rises to 359. The paper has not established a complexity frontier in the state dimension, action dimension, number of risk pieces, approximation tolerance, or continuous aggregation error.

### B8. The inherited large-vector bottleneck remains unresolved

The active appendix retains the two-control, two-innovation experiment: 44 action queries at two dates, 2,957 at three dates, and about 8.1 million at four dates. Complete time rises to 530 seconds for state dimension two and 841 seconds for state dimension eight. R92 does not change this experiment, independently reimplement its largest kernel, or compare matched vector proposal methods.

A separate three-state risk fixture cannot be used as evidence that the broader NBO platform has solved its dominant horizon bottleneck. The remaining obligation is stated honestly in the release record, but it remains a blocking numerical-method concern.

### B9. Resource prices and economic purchase conclusions remain externally supplied

The uniform price-fee region is a valid conditional decision formula. Computation prices, deployment fees, the value of normalized loss, energy, and application-specific monetary scales are not estimated by R92. The new occupation-sensitive precision budget prices allowable numerical error, not the economic value of computation.

This distinction should remain explicit. At present, the paper can tell a purchaser how to combine supplied prices with valid cost intervals; it does not identify those prices or establish that the NBO service changes a substantive economic decision under an empirically defended region.

### B10. Independent verification is strong but not end to end for the critical platform claims

The R92 checker is independent at the level of the new finite risk kernel, and this is a major positive. It remains authored within the same project, uses the same serialized diagnostic primitives, and deliberately does not reimplement the inherited largest-vector solver or every continuous-state economic kernel.

For the central platform claim, the missing object is a second end-to-end implementation that starts from the economic primitives and independently constructs the continuation, residual enclosures, original-action lower bounds, risk envelopes, policy values, and resource accounts. Internal exact agreement on a prescribed finite fixture is not a substitute for that broader replication.

### B11. The cumulative scope is disproportionate to the identified contribution

The active package contains 267 pages and multiple generations of theorems, experiments, responses, negative results, and preserved applications. This is admirable as an archive. It is not an effective Econometrica article. The main result of R92 must compete for attention with many distinct claims about construction, query search, actionwise qualification, common readouts, population selection, transport, recursive preferences, occupations, allocation, and games.

The paper's refusal to narrow its topic is understandable from a project-preservation perspective, but preservation and active journal presentation are different objectives. The present scale prevents a clear assessment of what is new, what is inherited, what is proved generally, and what is only executed in one model.

### B12. The empirical and theoretical claims still live on different problem classes

The strongest economic evidence concerns a two-date expected-cost investment menu. The new theorem concerns recursive conditional risk under a dual representation. The longest new diagnostics concern three-state AVaR fixtures. The held-out predictor experiment concerns query work in the original investment model. The inherited vector experiment concerns two controls and two innovations.

Each object is legitimate, but their observation units and primitives differ. R92 carefully avoids literally pooling them; nevertheless, the article's overall narrative still asks these separate pieces jointly to support the NBO platform. An Econometrica numerical-method paper needs one central model class on which theory, algorithm, prospective computation, and economic inference are all demonstrated together.

## 4. Major comments and required changes

### M1. Write a new focused paper around the actual R92 contribution

The natural title is **Reference-Centered Qualification for Risk-Averse Dynamic Programming** or **State-Dependent Qualification of Approximate Dynamic Programs under Recursive Risk**. The paper should contain the centered operator, original-optimum theorem, exact finite occupation result, support cuts, and one complete numerical application. Historical NBO material can remain archived and cited rather than reproduced in the active article.

### M2. Locate novelty theorem by theorem

Add a concise comparison table against risk-averse dynamic programming, robust/convex dual Bellman recursions, approximate policy evaluation, occupation-measure formulations, residual bounds, and affine-piece screening. For each new statement, identify the closest known result, the additional hypothesis, the new conclusion, and why centering at the stored continuation is essential rather than a change of variables.

### M3. Separate three levels of result

State separately:

1. the general bounded-function theorem under a conditional-risk dual;
2. the finite exact affine-risk implementation;
3. the numerically enclosed continuous-state implementation.

Do not let exact finite AVaR diagnostics stand in for an executed method for general continuous risk envelopes. Every claim about pruning or arithmetic work should identify which level it concerns.

### M4. Execute the method in the original continuous risk-averse economic model

Use a continuous-state, continuous-innovation investment or control problem with a genuinely recursive risk preference. Construct the stored continuation, all-action lower residual bound, policy upper residual, penalty enclosure, support cuts, and policy-cost interval from the original primitives. Report every source of error and every failed certificate.

### M5. Add matched representation experiments

Represent comparable continuations with ReLU, Bernstein/polynomial, spline, and analytic or conventional bases under matched approximation and training budgets. The verifier, error set, risk envelope, and stopping rule must be identical. Measure certificate width, retained risk pieces, complete work, memory, and policy cost. This is necessary to identify whether any benefit is neural, continuation-quality driven, or purely verifier driven.

### M6. Charge complete certificate-construction work

The operation ledger should include continuation construction, model loading, residual evaluation, all-action optimization, original-law integration, risk-envelope generation, penalty bounds, support-function evaluation, rational or interval recovery, policy rollout, serialization, and shutdown. Report machine-independent counts and wall-clock uncertainty on more than one architecture. Support cuts should be credited only after their own construction and verification cost is charged.

### M7. Demonstrate the all-action lower certificate rather than assuming it

For a nontrivial continuous action set, give an implementable branch-and-bound, convexity, semiconcavity, or interval method that proves the lower inequality over the complete feasible menu. Report how the effort scales with tolerance and action dimension. A sampled grid is not enough.

### M8. Complete an independent end-to-end implementation

The second implementation should independently construct the critical continuous-state kernels and the largest vector/risk example, not merely read the same exact finite cases. Preserve disagreements and failed enclosures. The current checker can remain as a valuable regression layer.

### M9. Add prospective evaluation for the learned component

Freeze the representation, calibration rule, and support-cut policy before an independent workload stream. Compare realized complete work and policy cost with adaptive, analytic, polynomial, and conventional risk-DP baselines. Report predictor failure, fallback, no-cut, wrong-cut-attempt rejection, and certificate closure separately.

### M10. Design economic inference around a declared margin

Choose a policy-cost superiority, equivalence, or noninferiority margin with an economic interpretation. Determine sample size and numerical precision before evaluation. Decompose the final interval into sampling, state aggregation, risk-envelope, acquisition, optimization, and arithmetic components. The new theorem should lead to a testable economic claim in the same risk-averse model.

### M11. Resolve or explicitly restrict the horizon claim

Either provide a method that changes the inherited vector horizon frontier or state a short-horizon/finite-state restriction. A stored three-state recurrence and a continuous two-innovation tree are not competing measurements of the same scalability claim.

### M12. Compress the active submission drastically

Move preserved historical papers, responses, and superseded numerical catalogues out of the active submission. A focused article should make one theorem--algorithm--evidence argument, with a supplement containing proofs and a reproducibility archive containing the full historical record. The current 267-page package is too cumulative for an ordinary journal revision.

## 5. Minor and technical comments

1. The statement that the centered penalty has infimum zero without attainment is correct; the implementation section should repeatedly distinguish this from the finite case in which a maximizing piece exists.

2. The terminology “risk occupation” should always be accompanied by “risk-distorted” when there is any possibility of confusion with physical or empirical occupation.

3. The theorem's measurable-selection and bounded-domain assumptions should be gathered in one formal assumption block rather than distributed between prose and inherited sections.

4. The paper should report the distribution, not only the maximum, of scalar versus state-dependent tightening across all 252 interval configurations. Include no-improvement, no-cut, and loose-bound cases in the main diagnostic summary.

5. Report the total number of candidate risk pieces before and after cuts, the time to prove cuts, and the complete time saved downstream. A cut count without a denominator is hard to interpret.

6. The bit-length table is useful. Add numerator/denominator growth by operation and identify the point at which exact arithmetic becomes less efficient than outward floating or interval arithmetic.

7. The absorbing example should be labeled explicitly as zero policy loss with a nonzero continuation bias, so readers do not confuse certificate sharpness with value-function accuracy.

8. Keep the strict inequality in the kernel cut and retain equality cases in all code paths. The adversarial equality test is important and should remain visible.

9. For entropic evaluation, numerical claims should include an actual outward implementation or remain analytical. The AVaR exact catalogue cannot validate floating exponential and logarithmic enclosure.

10. The complete-policy lower certificate should never be summarized as “checked actions” unless the text states whether the entire original continuous action set or only a finite exact menu was covered.

11. The population and joint-domain results should not be used as empirical generalization evidence for the prescribed R92 circuits. The present response recognizes this distinction; the main article should make it equally prominent.

12. The release package and historical preservation records are excellent, but many provenance paragraphs can be moved from the article to the reproducibility archive.

## 6. A focused publishable route

A credible new submission could be organized as follows:

1. one economically motivated recursive-risk control model;
2. the reference-centered risk operator and exact identity;
3. state-dependent original-optimum lower and upper certificates;
4. a practical continuous-action and continuous-state enclosure algorithm;
5. finite occupation and support-cut specializations;
6. a complete operation and error ledger;
7. matched neural and non-neural continuation experiments;
8. prospective independent policy-cost and work evaluation; and
9. an independent end-to-end implementation.

The central question should be whether centering at a stored continuation changes the attainable certificate--cost frontier in a risk-averse dynamic program. Neural representation can then be one comparator rather than the source of validity.

## 7. Recommendation

R92 is rigorous, transparent, and substantially stronger than R84. It closes the publication-package defect, adds a coherent state-dependent recursive-risk theorem, gives a useful exact occupation representation, and sets a very high internal audit standard. I encourage the author to publish this material in a form that makes its actual contribution visible.

For Econometrica, however, the present cumulative paper still lacks the required combination of sharply identified novelty, representation-specific numerical advantage, unified theory-to-application evidence, and economically consequential new inference. The strongest new result is method-neutral; the new catalogue adds no fit or economic observation; the held-out ReLU proposal remains inferior in query work; the inherited vector horizon bottleneck remains; and the active package is far broader than the result established in R92.

I therefore recommend **rejection in the present form**, while encouraging a new focused submission on reference-centered qualification for risk-averse dynamic programming.
