# External Referee Report — R43

**Venue perspective:** Econometrica-level numerical and computational methods  
**Article:** *Certified Bellman Operators for Costly Policy Revision*  
**Repository:** `TrillionniumFoundation/NBO`  
**Reviewed branch:** `revision/econometrica-r43-regret-scaled-atomic-2026-09-25`  
**Reviewed HEAD:** `50660fd5b5f37906920511a1c62fc20300c886c3`  
**Prior external report addressed by the revision:** `reviews/2026-09-25-econometrica-r40/referee_report.md`  
**Review branch:** `review/econometrica-r43-numerical-methods-2026-09-25-50660fd`  
**Date:** 2026-09-25

## 1. Recommendation

**Reject.**

R43 is a serious and technically substantive revision. It does not merely add another computational ledger. The paper now contains: (i) a finite-state complete-search framework for one common randomized Markov continuation; (ii) an exact exogenous-aggregation result; (iii) a new regret/savings formulation for controlled transitions; (iv) a conditional quadratic small-allowance bound for a root McCormick relaxation; (v) an observable-covariate disintegration theorem for a class of atomic continuous-state models; (vi) predeclared controlled computations with a disclosed arithmetic amendment; and (vii) unusually careful rational endpoint verification and preservation discipline. The authors have also become admirably explicit about what remains open. In particular, the abstract states that all 30 positive-cost randomized intervals in the original maintenance cohort remain open.

The paper is therefore much stronger than the object reviewed at R38 and stronger again than R40. Nevertheless, the central Econometrica-level objection remains. The manuscript has accumulated several exact or convergent results for specially structured model classes, but it still does not deliver a practically effective certified method for the action-dependent continuous-state problem that motivates the paper and dominates its long development history. The original positive-cost randomized optima are all unresolved. The finite complete method remains exponential. The new controlled computation is only a root-relaxation exercise: five of eight predeclared pairs improve, none of the eight reaches the registered absolute-width target of \(10^{-3}\), one pair is unchanged, and the two largest cases hit the 30-second LP cap in both formulations and fall back to \([0,U]\). The quadratic theorem is asymptotic at fixed primitives under strict action separation; its constants can be disastrous when action gaps are small, savings ratios are dispersed, the discount factor is high, or the horizon is long. The observed width-to-ε² ratios are not remotely stable over the four reported allowances. The observable-fiber theorem is mathematically correct-looking but obtains tractability by making a continuously indexed label perfectly observable, autonomous, invertible, and unaffected by actions, so that the continuum problem decomposes into independent finite problems. The original continuous condition process does not have that structure.

The strongest new numerical result is a useful tightening of a verified root relaxation in a designed finite model, not a solution algorithm that closes the constrained problem at economically relevant scales. The strongest new continuous result is a direct-integral reduction for separable observable fibers, not a method for generic controlled continuous dynamics. The exact service-economy examples similarly reduce to ordinary finite linear programs because all economically relevant variation is in a finite regime and the continuous coordinates are aggregation-compatible nuisance variables. These are legitimate contributions, but they do not jointly establish the broad numerical method suggested by the title and the length of the paper.

I did not find an obvious contradiction in the new disadvantage/savings recursions, the rare-departure repair argument, the McCormick-width proof, or the observable-fiber identity. My recommendation is not based on alleging an arithmetic defect hidden by the archive. It is based on scope, practical effectiveness, novelty relative to the amount of machinery, and economic importance. At this stage another incremental revision on the same collection of synthetic models is unlikely to be sufficient. A viable Econometrica submission would need either a genuinely effective certified method for the original action-dependent continuous-state class, a quantitatively important economic application, or a substantially narrower paper centered on one theorem whose novelty and usefulness can be established cleanly.

## 2. Overall assessment

| Dimension | Assessment |
|---|---|
| Correctness of the new finite regret/savings logic | Plausibly correct; no obvious contradiction found in the inspected proof and implementation |
| Correctness of observable-fiber disintegration | Plausibly correct under its stated separability and observability assumptions |
| Computational transparency | Exceptional |
| Independent endpoint verification | Strong for the declared finite objects; analytic theorems remain trusted mathematical arguments |
| Finite-state completeness | Genuine but exponential and largely formal at economically difficult scales |
| Practical controlled-transition performance | Mixed; five improvements, one tie, two complete time-cap failures, zero registered target hits |
| Original primary randomized optimization | All 30 positive-cost intervals remain open |
| Continuous-state generality | Restricted to exogenous aggregation, TV-reset models, or observable autonomous fibers; not the original controlled condition process |
| High-dimensional evidence | Weak; the nonlinear intervals remain 25%–76% wide at allowance 0.5 |
| Economic relevance | Designed known-model exercises without calibration, estimation, or welfare interpretation |
| Novelty relative to the size of the paper | Insufficiently demonstrated |
| Suitability for Econometrica | Insufficient |

## 3. What R43 genuinely contributes

The negative recommendation should not obscure substantial progress.

### 3.1 The policy-class target is now coherent

The central object is a common randomized Markov policy. One continuation kernel is used at every shared date and state, including after different restarts. The manuscript no longer substitutes independent restart-specific continuation choices for the stated economic object. The distinction between deterministic and randomized policies is also maintained correctly.

### 3.2 The finite-state theory reaches the original constrained object

The backward repair, rational lattice, and interval-search results inherited from R40 converge to the actual finite common-policy constrained optimum, rather than to a one-step necessary-action relaxation. This is an important conceptual correction relative to earlier revisions.

### 3.3 R43 supplies a nontrivial controlled-transition refinement

The new coordinates

\[
D^p=V-J^p,\qquad S^p=H-C^p
\]

lead to exact regret and savings recursions. Under a unique operating-maximizing action with a positive gap, the all-restart allowance bounds nonreference action mass. Savings lie in a cone relative to regret. These facts contract both factors of the remaining bilinear products. The resulting root-relaxation width theorem is not merely a restatement of ordinary McCormick validity.

### 3.4 The new continuum theorem preserves atomic transitions

The observable-fiber result does not smear moving atoms and does not misuse weak convergence as total-variation convergence. It allows action-dependent transitions in the finite regime coordinate and proves an identity over all Borel common Markov policies, not merely over a preselected policy sieve.

### 3.5 The audit boundaries are unusually honest

The paper discloses that the controlled cases were predeclared but the arithmetic implementation was amended after several initial executions. It retains the original source and partial records. It labels the exercise as predeclared with an amendment, not as an untouched code-frozen holdout. It also states that the 41 new endpoint objects comprise paired relaxations, repeated allowances, and fiber endpoints rather than 41 independent economic environments.

### 3.6 Arithmetic verification is serious

The independent reader reconstructs model dimensions, stochastic rows, operating values, disadvantage and savings coefficients, rational dual-residual lower endpoints, deployed policies, all original restart inequalities, and implementation objectives. Time-capped cases are also verified as sound wide intervals. This is materially stronger than relying on floating-point solver status or cross-run hash identity.

These are real contributions. The blocking findings concern what they establish economically and numerically.

## 4. Blocking scientific findings

### R43-F1 — The original motivating randomized problem remains unsolved in every nontrivial row

The original continuous maintenance cohort has 42 configurations. Twelve are exact zero-cost cases. All 30 positive-cost common randomized Markov intervals remain open. The maximum relative widths are still 14.61% at horizon 4, 32.29% at horizon 8, and 34.23% at horizon 12.

The 27 strict randomized improvements over deterministic lower bounds are valid and economically interesting. They establish that admissible lotteries can outperform every deterministic feasible rule in those configurations. They do not identify the randomized optimum or certify that the proposed lottery is close to it. The distinction is now stated correctly, but it remains fatal to the broad numerical claim: after many revisions, not one positive-cost randomized optimum in the paper's oldest and most intensively developed model has been closed.

R43 responds by adding new tractable classes rather than a convergence mechanism for that model. The authors explicitly admit that neither exogenous aggregation nor observable fibers applies to the original action-dependent continuous condition. The primary lower and upper constructions therefore remain structurally unmatched one-sided certificates, not iterates of a known convergent algorithm.

**Required correction:** provide a validated convergent scheme for the original atomic condition process or narrow the paper so that this model is no longer presented as central evidence for the general method. A collection of exact results on different model classes does not resolve the absence of convergence on the motivating class.

### R43-F2 — The controlled audit is a root-relaxation ablation, not an executed complete solver

The R43 controlled suite consists of 16 root LP computations: eight environments under unscaled and regret-scaled McCormick relaxations. No branching is performed. The 30-second cap applies to the LP proposal. If no usable primal/dual output is available, zero multipliers and the operating-optimal reference generate a sound fallback interval.

This is a legitimate experiment, but it is not evidence that the complete global search is practical. The results are:

| Case | \(n\) | \(T\) | \(m\) | Unscaled gap/upper | Scaled gap/upper | Status |
|---:|---:|---:|---:|---:|---:|---|
| 00 | 3 | 4 | 3 | 3.341% | 2.181% | solved |
| 01 | 8 | 8 | 3 | 6.358% | 1.306% | solved |
| 02 | 16 | 12 | 3 | 9.816% | 9.816% | solved |
| 03 | 16 | 24 | 4 | 9.168% | 4.635% | solved |
| 04 | 32 | 16 | 3 | 2.387% | 1.848% | solved |
| 05 | 8 | 32 | 4 | 1.867% | 0.279% | solved |
| 06 | 16 | 32 | 4 | 100% | 100% | cap |
| 07 | 32 | 32 | 3 | 100% | 100% | cap |

Five pairs improve materially, one is unchanged, and two fail completely under the cap. More importantly, **none of the eight reaches the registered absolute interval target of \(10^{-3}\)**. Even case 05, the best relative result, retains an absolute width of about 0.0452. Cases 06 and 07 return no positive lower endpoint at all.

The paper is transparent about these facts, but transparency does not turn mixed root bounds into a practically effective global method. The complete finite search remains a theorem whose executed evidence comes from much smaller binary-action cases and whose worst-case size is exponential.

**Required correction:** run an actual global algorithm using the tightened relaxation, report certified gap versus nodes and time, and demonstrate closure to a prospectively specified target on nontrivial three- and four-action problems. Root-node improvement alone is not sufficient.

### R43-F3 — The \(O(\varepsilon^2)\) theorem is highly conditional and nonuniform

The quadratic-width theorem is mathematically the most interesting addition. Its scope is much narrower than the headline may suggest. It requires:

1. a fixed finite model;
2. strict discounting, with β fixed below one;
3. a unique operating-maximizing action at every date and state;
4. a strictly positive minimum action disadvantage \(\underline d\);
5. bounded savings-to-regret ratios \(\lambda_-,\lambda_+\);
6. an exact root-LP optimizer for the clean theoretical width statement.

The constants contain inverse action gaps, transition differences, the spread \(\lambda_+-\lambda_-\), a horizon accumulation, a cost perturbation constant, and a repair denominator involving \((1-\beta)\varepsilon\). These constants can become enormous when actions nearly tie, when implementation savings are large relative to operating loss, when β is close to one, or when the horizon is long. Those are not pathological corner cases in economic dynamic programs; near-indifference and high discounting are common.

The theorem is therefore a pointwise asymptotic result, not a uniform complexity statement over an economically meaningful model class. It gives no useful guarantee if \(\underline d\) shrinks with model resolution or if the reference action changes under small parameter perturbations. In particular, it does not explain how a continuous model with switching surfaces should inherit the rate as the state grid is refined: grid cells near an action boundary will naturally have vanishing disadvantages.

**Required correction:** provide a robustness theory for approximate ties and state refinements, or state the result as a local sensitivity theorem for a strictly separated finite problem. The paper should not allow a fixed-model asymptotic rate to be read as a general small-tolerance algorithmic rate.

### R43-F4 — The reported allowance sequence does not empirically demonstrate a quadratic regime

For the one three-regime, eight-period scaling model, the reported scaled widths and width-to-ε² ratios are:

| ε | Scaled width | Width/ε² |
|---:|---:|---:|
| \(10^{-1}\) | 2.181330051 | 218.13 |
| \(10^{-2}\) | 0.174925073 | 1749.3 |
| \(10^{-3}\) | 0.004397164 | 4397.2 |
| \(10^{-4}\) | 0.000008657 | 865.63 |

The ratios vary by more than an order of magnitude and first increase sharply before falling. At ε=0.1 the scaled formulation is slightly worse than the unscaled formulation. The strongest improvement appears only at the smallest allowance in one tiny model.

The paper correctly says the ratio is descriptive and does not estimate a slope. That disclaimer is necessary. It also means the computation supplies no convincing numerical evidence that a practically relevant quadratic regime has been reached. The theoretical diagnostic further assumes an exact LP optimum and excludes rounding and dual-residual losses. For an inexact or capped solve, the LP objective gap must be added. Thus the clean rate does not automatically govern the actual published certificate widths.

**Required correction:** report the theorem's complete numerical upper bound and every component beside the measured width, extend the sequence by several additional allowances where arithmetic remains stable, repeat it on multiple models, and report log-log slopes only with clear asymptotic diagnostics. One favorable endpoint at \(10^{-4}\) is not enough.

### R43-F5 — Strict action separation is not stable under the economically relevant limits

The unique reference action is central to the probability cap and savings cone. A small parameter change can change the identity of that action or create a tie. The constants then jump or diverge. The manuscript notes this limitation but does not analyze it.

This is especially problematic when the finite model is itself an approximation to a continuous state problem. Optimal action regions are normally separated by switching surfaces. Refining the grid creates states arbitrarily close to those surfaces, where \(\underline d\) tends to zero. The finite-model \(O(\varepsilon^2)\) bound may therefore deteriorate exactly as the state approximation becomes more accurate. No joint limit in allowance and state resolution is supplied.

The result also depends on comparing implementation savings to operating disadvantages. Negative savings and very large positive ratios are permitted, but a wide cone makes the strengthening nearly useless. The controlled tables contain cases where the scaled and unscaled bounds are identical, illustrating that the assumptions may hold formally while the numerical contraction is negligible.

**Required correction:** establish conditions under which the action-gap and savings-cone constants remain controlled under discretization, or develop a multi-reference/tie-aware formulation. Without this, the rate is not a bridge to the paper's continuous-state goals.

### R43-F6 — Observable fibers obtain tractability by removing the hard continuous coupling

The observable-fiber theorem assumes state \((i,z)\), where the continuous covariate evolves through a Borel bijection \(\Phi_t\) that is autonomous and independent of the regime transition and the action. The initial label \(\zeta=F_t^{-1}(z)\) is exactly recoverable from the current state. Conditional on that label, the problem is finite. Different labels never interact.

Under these assumptions the continuum optimum is the integral of independent finite optima. This is a valid disintegration result, but it does not solve a genuinely coupled continuous-state control problem. It converts a continuum of observable types into a direct integral of finite MDPs. The executed example is still more special: establishment size is fixed over the horizon, and it merely rescales operating rewards, terminal rewards, implementation costs, and the effective allowance.

The original maintenance model is difficult precisely because actions move the continuous condition and hence alter future continuous-state occupancy. The observable-fiber assumption rules out that mechanism in the continuous coordinate. The action may change the finite regime transition, but not the covariate trajectory that labels the fiber. The authors state this boundary honestly; it remains a major scope limitation.

**Required correction:** demonstrate a certified method with interaction across continuous labels—e.g. action-dependent continuous dynamics, noninvertible mappings, or stochastic covariate innovations—or narrow the contribution to parametric families of finite constrained MDPs indexed by an observed type.

### R43-F7 — The controlled continuum computation is not close enough to validate broad numerical claims

The 16-cell controlled-fiber interval is approximately

\[
[10.074215,10.184476],
\]

with relative width 1.083%. The table decomposes the width into about 0.074982 from finite endpoint intervals and about 0.035279 from partition/value variation. This is a useful paired global certificate. It is not a near-exact result, and it does not show the stated convergence pipeline reaching a prescribed accuracy.

Only one scalar covariate, one horizon, one finite regime model, one discount factor, and one allowance are used. The finest partition has 16 cells and requires 17 endpoint solves. The experiment does not report work-versus-accuracy over enough refinements to establish practical convergence. Partition refinement alone cannot eliminate the surviving finite root widths, and the finite solvers are not run to progressively tighter global gaps.

The count of 17 independently checked fibers should not be interpreted as 17 independent model tests. They are endpoint evaluations of one one-parameter family generated from a single seed.

**Required correction:** refine both the covariate partition and finite global solves under a planned error budget, report complexity versus total certified width, and evaluate multiple covariate dynamics and dimensions. The current example verifies the theorem's bookkeeping, not scalable continuous-state optimization.

### R43-F8 — The exact exogenous-aggregation examples are economically finite problems with decorative continuous coordinates

The service-economy state is written as \((i,u,v)\), but operating rewards, implementation costs, and terminal payoffs depend only on the finite regime and action. The continuous coordinates undergo a measure-preserving shear and do not affect the economically relevant primitives. The aggregation identities therefore reduce the unrestricted Borel-policy problem exactly to a finite LP.

This is mathematically useful as a clean test of the aggregation theorem. It is not evidence that the method solves a high-dimensional continuous economic problem. The continuous coordinates are observable but economically irrelevant nuisance variables. All optimization is carried by the finite regime. The resulting LP is ordinary linear programming under exogenous transitions, which the paper itself acknowledges.

The density-transfer exercise is better as an error-budget demonstration, but it remains built around the same exact finite reference and reports a failed tightening condition for the largest perturbation. It does not address action-dependent continuous dynamics.

**Required correction:** either present these examples as theorem-validation exercises rather than substantive continuous-state applications, or supply a model in which continuous states materially affect rewards, costs, and controlled transitions while the proposed certificates remain informative.

### R43-F9 — Formal completeness is still being conflated with numerical usefulness

The inherited complete finite search is exponential in the number of policy coordinates. The prospective binary-action suite already showed the practical consequence. At the long horizons, the verified McCormick formulation produced stronger certificates than interval Bellman search, and neither method closed the difficult rows under the precommitted budget. R43 does not change those results.

The new tightening is valuable at the root, but no evidence shows that it changes global tree complexity. Stronger root bounds do not automatically imply a manageable branch-and-bound search. The two largest controlled cases time out before producing a usable root solution, so they cannot even begin such a search under the stated cap.

The paper repeatedly distinguishes completeness from cheap computation, which is good. The title and overall architecture nevertheless invite the reader to see a general certified numerical method. At present the method is a collection of valid certificates plus a formal finite enumeration theorem.

**Required correction:** provide global-search scaling, node counts, bound progress, and successful closure on substantially larger problems. If this is infeasible, center the paper on verification and structural lower bounds rather than on complete optimization.

### R43-F10 — The evaluation lacks a strong external global-optimization baseline

The new U-versus-S comparison is an internal ablation. Both use the same reference elimination, probability caps, HiGHS LP engine, rational residual construction, candidate repair, and root-only execution. The comparison isolates the savings-cone contribution, which is scientifically useful, but it does not establish competitive performance.

The paper does not compare a completed tightened branch-and-bound implementation with modern nonconvex solvers, spatial branch-and-bound, mixed-integer reformulations, dynamic-programming state augmentation, or occupation-measure formulations that preserve common-policy compatibility. The older finite comparison contrasts two custom methods but already showed that the stronger mathematical-programming formulation dominates on hard rows.

A top numerical-methods paper needs to show either decisive computational superiority or a certificate unavailable from standard methods. Here standard LP machinery supplies the proposal, classical McCormick inequalities supply the relaxation, and the principal new element is bound tightening plus repair. The incremental value should be evaluated against serious alternatives.

**Required correction:** benchmark the full method against strong external solvers and formulations on identical objectives, constraints, tolerances, and hardware. Report certified gap versus time, not only individual root intervals.

### R43-F11 — The predeclaration evidence is weaker than the paper's object count suggests

The protocol is commendably transparent. However, the source was amended after cases 00–02 and the unscaled case 03 had been observed, and after the scaled case 03 had run for 200 seconds before interruption. The amendment addresses denominator growth and integer-string conversion rather than changing case parameters, but the exercise is not code-frozen prospective validation. The manuscript acknowledges this.

Moreover, the “41 new endpoint objects” comprise:

- 16 outputs from eight finite cases under two related relaxations;
- 8 outputs from one model at four allowances under the same two relaxations;
- 17 endpoint solves from one controlled-fiber family.

This is not 41 independent environments. It is a small number of highly related experiments generated by one model constructor. The independent verification establishes arithmetic validity, not generalization.

**Required correction:** freeze the final implementation and evaluate it on a genuinely untouched suite from multiple model families, with no post-observation source change. Report performance by environment, not by proof-object count.

### R43-F12 — The difficult operating-oracle problem remains untested

The witness-driven theorem is retained, but the new regret-scaled experiments use exact finite operating dynamic programming. The service economies also use exact finite operating solutions. The original one-dimensional maintenance operating value is exceptionally cheap. Thus the paper still does not demonstrate a useful global revision certificate in a setting where operating-value approximation is itself difficult.

This matters because the broader motivation invokes complex economic dynamic programs. In such models, constructing tight, globally valid operating witnesses may dominate the entire computation. The current evidence isolates policy-search difficulty while assuming away the operating-oracle bottleneck.

**Required correction:** apply the method to a model with a genuinely approximate operating solution, charge witness construction, propagate the full error budget, and retain an informative final revision interval. Otherwise the witness-driven extension remains largely theorem-only.

### R43-F13 — The nonlinear two-state experiment remains exploratory rather than an optimality result

The inherited nonlinear intervals are still wide:

- \(T=8,N=64\): 76.01%;
- \(T=16,N=128\): 45.32%;
- \(T=32,N=64\): 61.05%;
- \(T=32,N=128\): 35.11%;
- \(T=32,N=256\): 25.13%.

The operating allowance is 0.5. At allowance 0.05, the reported exercises remain lower-bound-only because no matching feasible upper policy is certified. Independent replay of the finest object strengthens trust in the arithmetic; it does not make a 25% interval tight or establish convergence of the box sequence to the continuum optimum.

R43 does not improve these endpoints. The new fiber example is a different separable model and cannot substitute for the coupled nonlinear condition process.

**Required correction:** produce paired lower and upper certificates at economically meaningful tolerances, prove convergence for the controlled atomic box representation, and show a nontrivial reduction in the finest interval.

### R43-F14 — Economic content remains too thin for the target journal

All main experiments are designed known-model environments. Transition probabilities, intervention effects, revision weights, allowances, initial laws, and installed policies are synthetic. The paper includes no estimated model, sampling uncertainty, monetary welfare interpretation, or empirical implementation cost. Randomization is assumed administratively admissible and charged only through realized departures; fixed costs of maintaining a lottery, communication costs, compliance constraints, and persistent organizational heterogeneity are not modeled.

A pure methods paper can succeed without calibration if it introduces a broadly useful algorithm with convincing complexity and benchmark performance. R43 does not yet meet that standard. Conversely, a narrower certificate method could be compelling if it changed a substantive economic conclusion in a serious application. The paper currently offers neither a broadly effective solver nor such an application.

The strict-randomization findings are interesting, but they arise in a repeatedly developed synthetic cohort and do not establish that randomized organizational policies are economically relevant or implementable.

**Required correction:** either add a disciplined economic application with meaningful units, uncertainty, and institutional constraints, or substantially strengthen the general computational evidence and theory. Additional seeded maintenance variants will not resolve this objection.

### R43-F15 — The theorem-level novelty is not yet positioned sharply enough

The bibliography has improved, and the paper now cites constrained-MDP approximation, policy-gradient methods, safe control, semi-infinite programming, McCormick relaxations, and verified computation. The central novelty claim nevertheless remains diffuse.

- Exact exogenous aggregation is a strong lumpability/measure-compatibility result followed by ordinary LP.
- Observable-fiber disintegration is a direct-integral decomposition made possible by a perfectly recoverable autonomous label.
- The finite complete search is an exponential discretization/branch-and-bound construction with repair.
- The quadratic root-width theorem combines classical McCormick error, problem-specific variable contraction, and feasibility repair.

The last item appears to be the most distinctive theorem. It should be compared carefully with parametric nonconvex optimization, perturbation analysis of constrained MDPs, and bound-tightening results for bilinear dynamic formulations. The current paper claims no priority for the ingredients but does not convincingly isolate why the combination is sufficiently novel and important for Econometrica.

**Required correction:** identify one theorem as the central advance, state the closest known results and the precise mathematical difference, and remove peripheral material that obscures that contribution.

### R43-F16 — Independent arithmetic verification does not validate the analytic reductions

The independent reader is a major strength. It checks finite endpoints and all-restart inequalities. It does not machine-check:

- the disadvantage/savings cone theorem;
- the quadratic-width derivation;
- the measurable-selection argument in the fiber theorem;
- the exact aggregation identities as analytic statements;
- the economic appropriateness of the primitive contracts.

The four mutation tests—endpoint, negative probability, negative dual multiplier, and nonstochastic transition row—are useful smoke tests but provide limited adversarial coverage. Constructor and verifier still share the intended model and serialization contract.

The paper generally states these boundaries correctly. The presentation should nevertheless avoid letting “41 independently checked objects” sound like independent verification of the new theorems.

**Required correction:** expand property-based and adversarial testing, independently implement selected theoretical transformations, and provide a theorem-to-code contract table. Keep arithmetic validation and analytic validity separate in every summary.

### R43-F17 — The manuscript has become an omnibus of differently scoped results

The current article combines:

1. common-policy finite completeness;
2. witness-driven repair;
3. exact exogenous aggregation;
4. TV-reset transfer;
5. regret-scaled root bounds;
6. observable fibers;
7. a binary prospective suite;
8. a controlled root-ablation suite;
9. the original one-dimensional development cohort;
10. a nonlinear two-state box experiment;
11. service economies and density perturbations;
12. inherited stopped-control material.

These components use different policy structures, state dynamics, convergence mechanisms, approximation targets, and verification boundaries. The authors label the distinctions carefully, but careful labeling does not create one coherent numerical method. The original model remains open while new sections prove exactness for easier or differently structured classes.

The paper would be stronger if split. One focused article could develop common-policy repair and finite global certification. Another could study the strict-gap regret-scaled McCormick theorem. A third could treat exact aggregation and observable-fiber reductions. The present omnibus makes it difficult to identify the central result and dilutes the standards applied to each component.

**Required correction:** choose one main contribution, remove archival and orthogonal material from the article, and evaluate that contribution deeply. Repository preservation can retain the full research history without requiring one journal article to contain every branch of it.

## 5. What would be required for a future Econometrica submission

The present paper is not one incremental revision away from acceptance. A future submission would need a coherent redesign around at least one of the following paths.

### Path A: Solve the original controlled atomic continuum problem

Develop a convergent enclosure method for action-dependent continuous-state transitions, prove an end-to-end error bound, and close a substantial portion of the 30 positive-cost primary randomized intervals. Demonstrate useful rates as horizon and state complexity grow.

### Path B: Make the regret-scaled method a genuine global solver paper

Build the tightened relaxation into a complete spatial branch-and-bound implementation. Freeze it prospectively. Compare against strong external global solvers and common-policy formulations. Show target-level closure on three- and four-action problems substantially larger than the current root examples. Analyze near ties and joint state-resolution/allowance limits.

### Path C: Make observable fibers the central theorem

Narrow the paper to parametrically indexed constrained MDPs with recoverable observable types. Establish novelty relative to measurable selection and direct-integral control results, derive practical multidimensional approximation rates, and provide economically substantive applications in which the continuous covariate materially affects decisions and outcomes.

### Path D: Supply a serious economic application

Use the certificates in a calibrated or structurally disciplined model where implementation frictions, randomization feasibility, and operating guarantees have real economic meanings. Include estimation or uncertainty, monetary or welfare units, and a substantive conclusion that depends on the certification method.

Pursuing none of these fully while adding further auxiliary classes or proof inventories would leave the central objection unchanged.

## 6. Additional technical and presentation comments

1. The abstract should state that none of the eight new controlled cases meets the registered \(10^{-3}\) absolute-width target and that two cases return 100% intervals under both root relaxations.

2. Report absolute width beside relative width in the main controlled table. Case 05's 0.279% relative gap still has absolute width about 0.0452.

3. Add a “best valid intersection” column for U and S while retaining the individual rows. Individual ablations are useful, but the scientifically strongest certificate should also be visible.

4. For every controlled case, report the exact LP status, primal availability, dual availability, residual correction, and whether the upper policy is merely the operating-optimal fallback.

5. The phrase “solved” in the controlled table should be replaced by “root LP returned proposal” or equivalent. A nonzero certified interval is not a solved constrained optimization problem.

6. Report the registered target directly in the table and a Boolean target-met field.

7. Give the clean theoretical width bound numerically for every scaling row, not only the measured interval. Decompose \(E_D\), \(E_S\), the repair fraction, \(D_C\), and the numerical LP gap.

8. Show how \(\underline d\), \(\lambda_-\), and \(\lambda_+\) vary across all eight controlled environments. Formal strictness alone is not informative.

9. Add a tie-aware example demonstrating what happens when two operating actions are nearly equivalent.

10. State whether the reference action is stable under the rational rounding used to construct the proof objects.

11. Separate the theorem's exact-LP rate from the implemented certificate's rate in the abstract and conclusion.

12. For the observable-fiber theorem, discuss whether the initial regime law may depend measurably on the fiber label and whether the independence assumption is essential or merely convenient.

13. Give a complete measurable-selection proof or a precise citation for the uniform Borel construction over fibers. The current finite-lattice argument is plausible but compressed.

14. Quantify the covariate-cell primitive errors \(d_r,d_k,d_g,α\) in the executed continuum example, even where monotonicity yields a sharper special argument.

15. Report continuum width versus total finite-LP time and independent-check time for each partition size.

16. Extend the fiber computation beyond a fixed covariate. An invertible but nontrivial autonomous evolution should be tested explicitly.

17. The service-economy discussion should say plainly that the continuous coordinates do not enter rewards, costs, or regime transitions and hence are economically ancillary.

18. The phrase “closed atomic continuous-state service economies” risks overstating the role of the continuous variables. “Exact aggregation examples with atomic nuisance coordinates” would be more precise.

19. For the prospective binary suite, retain the unfavorable result that the McCormick formulation dominates interval search on every difficult pair in the main text, not only in the prior response history.

20. Report global-search progress curves rather than only final caps.

21. The primary table should include median as well as maximum positive-cost randomized width in the article, not solely the supplement.

22. For the 27 strict deterministic separations, report the guaranteed savings as a percentage of the deterministic lower bound and the randomized upper cost.

23. Explain the institutional meaning of drawing a new randomized action conditional on state at every date. In many organizations, randomization itself has fixed implementation and governance costs.

24. The nonlinear table should not mix independently checked and nonindependently checked rows without a visually prominent indicator.

25. For the 0.05 nonlinear lower-only exercise, report exactly why each upper candidate fails certification and whether failure is due to the policy or the box enclosure.

26. Provide a machine-readable theorem-assumption matrix mapping every headline claim to model class, policy class, state dynamics, allowance, convergence mechanism, and independent verification coverage.

27. The four mutation tests should be expanded to include incorrect action gaps, swapped reference actions, malformed product bounds, forged repair policies, altered discount factors, and fiber-weight errors.

28. Preserve reproducibility, but reduce the main article's dependence on historical narrative. The repository can retain the complete ancestry without making revision history part of the scientific argument.

29. The conclusion should distinguish “a theorem guarantees asymptotic width” from “the implemented computation attained a small width.”

30. Avoid counts such as “41 independently checked objects” without immediately decomposing them into environments, paired methods, allowance points, and fiber endpoints.

## 7. Final editorial view

R43 is the strongest version of this project so far. The authors have responded thoughtfully to prior criticism, converted several vague aspirations into explicit theorems, and maintained exemplary computational provenance. The regret/savings representation is a worthwhile idea. The observable-fiber theorem is a clean way to avoid invalid smoothing of atomic transitions. The independent rational checking is unusually careful.

The paper still falls short of Econometrica. The motivating positive-cost randomized problem remains unresolved in every row. The complete solver is exponential and not demonstrated at meaningful controlled-transition scales. The new root tightening misses its registered absolute target in all eight predeclared environments and fails completely on the two largest cases. The quadratic theorem is a nonuniform fixed-model asymptotic whose useful regime is demonstrated only in one tiny model at a very small allowance. The continuous-state extensions achieve tractability through exact aggregation or separable observable labels rather than by controlling generic action-dependent continuous dynamics. The economic exercises remain synthetic and uncalibrated.

The manuscript now contains several potentially publishable ingredients, but not yet one coherent Econometrica contribution. The appropriate next step is not another omnibus revision. It is to select the strongest theorem, narrow the paper, and demonstrate either decisive numerical performance or decisive economic value.

**Recommendation: Reject.**