# External Referee Report — R38

**Venue perspective:** Econometrica-level numerical and computational methods  
**Article:** *Certified Bellman Operators for Costly Policy Revision*  
**Repository:** `TrillionniumFoundation/NBO`  
**Reviewed branch:** `revision/econometrica-r38-verified-global-bounds-2026-09-24`  
**Reviewed HEAD:** `2cd8a26b113a8811975637d29f7116f077d70814`  
**Prior report addressed by the revision:** `reviews/2026-09-24-econometrica-r36/referee_report.md` at `c81410887bca5c16975beabb2ca8d6be7f235a19`  
**Review branch:** `review/econometrica-r38-numerical-methods-2026-09-25-2cd8a26`  
**Date:** 2026-09-25

## 1. Recommendation

**Reject in the present form.**

R38 is a real and substantial revision. It cures the decisive defect of R36, which asserted numerical results in a protocol without materializing the manuscript, proof objects, implementation, or execution records. The present branch contains a new article, supplement, response, computation report, executable constructors, separate rational verifiers, machine-readable result objects, failed-run records, build logs, manifests, and preservation checks. The authors have also become much more disciplined about policy classes, initial-distribution objectives, pointwise versus integrated equality, and the distinction between a verified finite computation and a theorem about a broader continuous problem. This is an unusually careful computational archive.

That improvement does not, however, make the paper suitable for Econometrica. Once the record-keeping problem is removed, the substantive limitation becomes clearer. The paper establishes exact deterministic certificates for a subset of a synthetic, one-dimensional, three-action, finite-horizon, piecewise-affine benchmark. Half of the 24 reported exact cases have zero revision cost and are therefore economically and computationally trivial once feasibility of the incumbent is checked. The 12 positive-cost exact cases are concentrated almost entirely at horizon four; no positive-cost case is closed at horizon twelve. The paper's own randomized example proves that deterministic policies are not sufficient even in its basic model family, yet the primary randomized Markov objective is not solved or tightly bounded. The nonlinear two-state extension reports a zero lower bound in every row, so it verifies feasibility of selected candidates but provides no informative optimality certificate. The local-LP theorem converges to a local one-step relaxation, not to the original constrained control problem. The upper-bound search remains a finite portfolio of problem-specific heuristics, with no end-to-end convergence theorem or stopping guarantee.

Thus the package is stronger as an audit artifact than as an Econometrica contribution. Exact arithmetic, hashes, mutation tests, and preservation manifests can establish that a declared finite object was computed consistently. They cannot substitute for a method that solves an economically important class of problems, for a convergence theory to the stated constrained optimum, for convincing performance beyond a favorable low-dimensional benchmark, or for a substantive economic application. I did not find an obvious contradiction in the inspected deterministic constructor and independent verifier; my recommendation is not based on alleging a hidden arithmetic error. It is based on the much more fundamental mismatch between the scope of what is certified and the breadth suggested by the paper's title, architecture, and target journal.

A further incremental revision that adds more ledgers, more certificates on the same development cohort, or another auxiliary theorem would not resolve this concern. A viable paper would require a redesigned central contribution: either a genuinely convergent method for the relevant randomized constrained problem, a nontrivial high-dimensional certification result with informative lower and upper bounds, or a serious economic application for which the proposed certificates change a substantive conclusion.

## 2. Overall assessment

| Dimension | Assessment |
|---|---|
| Correctness of the stated deterministic outer-bound logic | Strong and plausibly correct within the declared assumptions |
| Computational transparency and reproducibility | Unusually strong |
| Independence of verification | Strong for the one-dimensional primary and fixed-restart frontier objects; incomplete elsewhere |
| Novelty of the mathematical ingredients | Modest; the contribution is mainly an engineered combination of established tools |
| End-to-end convergence to the stated constrained optimum | Not established |
| Evidence for randomized policies | Insufficient for the primary problem |
| Evidence beyond the one-dimensional affine benchmark | Insufficient; the nonlinear lower bound is identically zero |
| Economic significance and external validity | Weak |
| Suitability for Econometrica | Insufficient |

## 3. What R38 genuinely accomplishes

The rejection recommendation should not obscure the material progress from R36.

First, the revision is fully materialized. The repository now contains the R38 paper and supplement, a point-by-point response, a computation report, exact proof objects, execution ledgers, independent-verification records, publication manifests, and reproducible entry points. The paper no longer asks the referee to treat a protocol as an executed result.

Second, the deterministic lower-bound theorem is useful and stated with considerably better scope control. Given checked witnesses \(L_t\leq V_t\leq U_t\), the necessary-action set

\[
\mathcal N_t^{L,U}(x)=\{a:L_t(x)-T_t^aU_{t+1}(x)\leq\varepsilon\}
\]

contains every action used by an all-restart feasible deterministic policy. Minimizing revision cost over this outer class gives a valid deterministic lower bound. Equality with a separately verified feasible policy certifies the specified initial-distribution optimum; equality of the full cost functions gives the stronger restart-by-restart statement. The manuscript now correctly separates these two notions.

Third, the authors do not silently extend deterministic conclusions to randomized policies. The two-period analytic example demonstrates that randomization can strictly reduce revision cost, and the fixed-restart frontier recursion is explicitly described as history-conditioned rather than as the uniform-initial randomized Markov solution. This is scientifically honest and mathematically important.

Fourth, the one-dimensional proof objects receive a serious independent check. The SymPy verifier does not import the constructor's piecewise-affine arithmetic, envelope, composition, or optimizer routines. It rebuilds partitions, transition pullbacks, endpoint limits, isolated-point values, Bellman equations and inequalities, exact integrals, and exactness flags. The separate frontier verifier likewise checks the finite-tree objects. The mutation tests are not a proof of correctness, but they are useful and substantially better than a second execution of the same code.

Fifth, the revision preserves negative evidence. The 18 unresolved deterministic intervals are reported rather than rounded away; failed nonlinear certificates and the failed unquantized local-LP attempt are retained; the stopped-control target is not relabeled as solved. This discipline should be maintained.

These are real strengths. They are not enough to overcome the blocking scientific findings below.

## 4. Blocking scientific findings

### R38-F1 — The main theorem certifies a relaxation case by case; it is not an algorithm that converges to the constrained optimum

The core deterministic theorem is a lower-bound result. The exact-value necessary set uses the one-step condition

\[
V_t(x)-T_t^aV_{t+1}(x)\leq\varepsilon.
\]

This condition is necessary for a feasible deterministic action, but it ignores the accumulation of future operating losses under the selected continuation. Consequently, minimizing revision cost over the necessary-action set solves an outer relaxation, not the original constrained problem. The paper is explicit about this, and the 19 infeasible necessary-set selectors at longer horizons empirically demonstrate the distinction.

The witness-refinement proposition does not fix the issue. As \(L\uparrow V\) and \(U\downarrow V\), the lower bound converges to the exact necessary-action relaxation \(B^{V,V}\). It does not converge to the true constrained optimum unless a feasible upper policy happens to attain the same value. Exactness is therefore opportunistic: it is declared when the finite upper portfolio meets the relaxation, and otherwise the method supplies an interval with no theorem forcing it to close.

For an Econometrica numerical-methods paper, the central approximation parameter should control distance to the actual economic object of interest. Here the controlled approximations terminate at intermediate relaxations. The remaining structural gap is not governed by a refinement theorem, a rate, or a complete stopping criterion. The paper therefore offers a valid certification device, not a generally convergent solution method.

**Required correction:** either prove convergence of computable lower and upper sequences to the stated deterministic constrained optimum under economically meaningful assumptions, or narrow the paper to a benchmark-specific verification procedure and remove claims suggesting a general global numerical method. A convergence statement to the necessary-action relaxation is not a substitute for convergence to the constrained optimum.

### R38-F2 — The primary policy class is economically incomplete, and the paper itself proves this incompleteness matters

The 24 headline equalities solve a deterministic Markov objective under the uniform initial distribution. They do not solve the randomized Markov problem. They also do not solve a common-continuation randomized problem through the fixed-restart frontier calculations, because the latter allow history-specific continuation choices and use Dirac initial states.

This is not a technical corner case. The paper's own two-period example shows strict randomized improvement under the same maintenance primitives and the same uniform initial objective: the deterministic cost is \(3/2\), while the randomized costs are approximately \(1.3720\) and \(0.8600\) at the two tolerances. Thus the deterministic restriction can materially alter the economic optimum even in the simplest member of the model family.

Once this counterexample is established, the reader needs an economic reason to exclude randomization from the primary problem or a method that treats randomized Markov policies directly. Neither is supplied. The fixed-restart frontier study is valuable as a policy-class warning, but it solves 70 horizon-four Dirac objectives, not the 42 uniform-initial primary objectives. The two-period analytic calculation is too special to fill that gap.

**Required correction:** solve or tightly certify the uniform-initial randomized Markov problem for the primary horizons, or provide a compelling institutional restriction that makes deterministic policies the actual economic object. Every title, abstract, theorem, table, and conclusion should then be centered on that restricted object. At present the paper both demonstrates that randomization matters and leaves the economically broader problem unresolved.

### R38-F3 — The headline “24 exact cases” materially overstates the substantive closure

The primary summary reports:

| Horizon | Cases | Exact initial | Positive-cost exact | Functionwise exact | Maximum gap |
|---:|---:|---:|---:|---:|---:|
| 4 | 14 | 14 | 10 | 14 | 0 |
| 8 | 14 | 6 | 2 | 5 | 0.103473 |
| 12 | 14 | 4 | 0 | 4 | 0.248472 |

Twelve of the 24 exact cases have zero revision cost. Because revision costs are nonnegative, a feasible installed policy with zero changes is automatically optimal. Those rows require a feasibility certificate, but they do not demonstrate that the proposed lower-bound machinery solves a nontrivial revision optimization problem. The substantive exact set is therefore the 12 positive-cost cases.

Those 12 cases are highly concentrated: ten occur at horizon four, two at horizon eight, and none at horizon twelve. Beyond horizon four, only one positive-cost case has full cost-function equality at every restart; the other positive horizon-eight equality is integrated only. This pattern is consistent with the paper's own explanation that accumulated operating losses break feasibility of the pointwise necessary selector as the horizon grows.

The unresolved intervals are not uniformly negligible relative to the claimed costs. For example:

- horizon 8, neural31001, ε=0.05: gap \(0.103473\) against upper cost \(0.227986\), about 45%;
- horizon 8, neural31002, ε=0.05: gap \(0.069935\) against upper cost \(0.114248\), about 61%;
- horizon 12, neural31003, ε=0.05: gap \(0.248472\) against upper cost \(0.388955\), about 64%.

Reporting only the maximum absolute gap in normalized units obscures this heterogeneity. The strongest nontrivial exactness result is essentially “the pointwise outer relaxation happens to be feasible at short horizon.” That is useful diagnostic evidence, but not broad global closure.

**Required correction:** reorganize the headline evidence around nonzero-cost cases, report relative as well as absolute gaps, and make horizon dependence central. The paper must explain why the method should remain useful when the necessary-action selector ceases to be feasible, rather than treating the unresolved longer-horizon rows as secondary residuals.

### R38-F4 — The nonlinear two-state extension does not provide an informative optimality certificate

The nonlinear extension is presented as evidence that the method survives loss of one-dimensional piecewise-affine closure. It does demonstrate that outward whole-box feasibility calculations can be executed on a bilinear two-state model. It does not demonstrate that the proposed method computes a near-optimal revision policy.

In every row of `paper/generated/all_multistate.tex`, the reported global lower bound is \(0.0000\). Therefore every certified policy interval is of the form \([0,\text{positive upper cost}]\). At horizon 32 and mesh 256, for example, the certified candidate costs are roughly 11.85, 12.10, and 13.16, while the lower bound remains zero. No ranking, approximation ratio, or meaningful optimality statement follows.

The operating tolerance is \(1/2\), compared with \(0.01\) and \(0.05\) in the primary cohort. Many restart-generator regret bounds sit essentially at \(0.5000\), indicating that the certificate is operating at the edge of this much looser requirement. The success counts—26 of 40 restart candidates and 15 of 20 classical candidates—measure whether selected policies pass a sufficient feasibility test. They do not measure solution quality. Candidate counts differ, penalties differ, and failed sufficient certificates do not imply actual infeasibility, so the success fractions cannot support a method comparison.

The nonlinear checker also shares the construction arithmetic rather than providing the independent verification used for the one-dimensional primary objects. The extension is therefore weaker both economically and computationally than the main experiment.

**Required correction:** produce nonzero, informative lower bounds and certified end-to-end gaps for the nonlinear model; use tolerances comparable to the primary problem or justify the economic scale of \(1/2\); compare algorithms under matched information and computational budgets; and independently verify at least a representative subset of the nonlinear proof objects. Without these changes, the extension should be described as a feasibility-enclosure demonstration, not as evidence for global numerical optimization.

### R38-F5 — The paper has no unified end-to-end error theorem

R38 contains several correct-looking error statements, but they concern different intermediate objects:

1. operating witnesses approximate the operating value;
2. nested witnesses converge to the exact necessary-action relaxation;
3. the adaptive local LP approximates a continuous local restart relaxation;
4. finite support-price sets give valid randomized lower floors;
5. whole-box arithmetic encloses a fixed nonlinear candidate;
6. a finite heuristic portfolio supplies feasible upper policies.

There is no theorem combining these components into a bound that converges to the original deterministic or randomized constrained optimum. In particular:

- exact operating values do not eliminate the structural looseness of the necessary-action relaxation;
- denser local multiplier certification does not establish global strong duality;
- more global support prices are not shown to exhaust the relevant dual;
- more boxes in the nonlinear model do not improve the zero global lower bound;
- adding upper candidates does not provide a complete or convergent search.

The paper's gap diagnostics are careful precisely because the errors are not additive and belong to different policy classes. That honesty also reveals that the manuscript lacks the central theorem expected of a numerical-methods contribution: a sequence of computable objects whose total certified error for the economic target tends to zero under stated assumptions.

**Required correction:** supply an end-to-end approximation theorem with a computable global error budget and a termination condition for the actual constrained objective. If such a theorem is unavailable, the paper must be reframed as a collection of one-sided verification tools, with correspondingly narrower claims.

### R38-F6 — The direct comparators do not solve the same main object

The paper has improved its comparator set, but the comparisons remain fragmented.

The exact operating Bellman program is not a comparator for constrained revision. The deterministic necessary-action recursion is a lower relaxation. The fixed-restart frontier is exact for a history-conditioned finite tree at five Dirac states and horizon four, not for the uniform-initial randomized Markov problem. The analytic randomized solution is only two periods. The nonlinear “classical” baseline is a four-price scalarization portfolio whose output is merely proposed and then checked; it is not a strong direct solver for the same constrained objective.

On a one-dimensional finite-horizon model with three actions, the paper should be able to benchmark against substantially stronger same-object methods. Depending on the chosen policy class, possibilities include verified state/budget augmentation, occupation-measure or semi-infinite LP approximations with rigorous residual bounds, exact parametric constrained dynamic programming, mixed-integer formulations on a common certified partition, or convergent Lagrangian schemes. The paper need not implement every alternative, but it must show where its certificates improve on a credible direct method rather than on a deliberately sparse price portfolio.

**Required correction:** include at least one strong comparator that targets the same initial distribution, policy class, operating constraint, and revision objective as the headline experiment. Report accuracy, runtime, memory, and certification strength under matched computational budgets. A collection of adjacent but nonidentical reference problems is not enough.

### R38-F7 — The claimed general numerical method is tested where exact dynamic programming is exceptionally easy

The main benchmark is deliberately favorable to exact symbolic computation:

- one continuous state on \([0,1]\);
- three discrete actions;
- two discrete shocks;
- affine transitions;
- finite horizons of 4, 8, and 12;
- convex piecewise-affine value structure;
- rational primitives;
- an exact uniform integral.

The exact operating solves take approximately 0.0046, 0.0141, and 0.1198 seconds at the three horizons. Thus the key operating object \(V\), which is unavailable in the high-dimensional applications that motivate approximate dynamic programming, is essentially free here. The paper does execute approximate witnesses as well, but the safe and exact deterministic lower bounds differ by at most roughly \(1.2\times10^{-5}\). On this cohort, operating approximation is not the hard numerical problem.

Representation complexity nevertheless grows: the reported maximum lower-bound pieces increase from 11 to 90 to 430, and rational bit lengths from 143 to 186 to 242. No complexity theorem or scaling law explains how this behaves with horizon, state dimension, action count, or shock support. The two-state regular-grid experiment avoids symbolic partitions, but, as noted above, yields only zero lower bounds and a loose operating tolerance.

**Required correction:** demonstrate the method on problems where operating value approximation is genuinely nontrivial and where the resulting global revision bounds remain informative. Provide scaling experiments and theoretical complexity discussion. A method whose strongest guarantees require an exact operating solution should not be sold as evidence for settings in which that solution is the bottleneck.

### R38-F8 — The adaptive local-LP result is mathematically isolated from the primary economic conclusion

The adaptive local-LP theorem is one of the technically more elaborate additions. It correctly distinguishes the local multiplier μ from the global support price λ and provides whole-cell primal/dual checks. However, the executed study covers only two horizon-four neural31001 cases, two witness choices, and three local tolerances, all with the global support floor fixed at zero.

The diagnostic does not close any of the 18 primary deterministic intervals, solve the primary randomized problem, or quantify the global duality gap. At the finest reported tolerance, the exact-witness intervals remain approximately \([0.088121,0.092759]\) and \([0.025665,0.030302]\). The number of accepted cells reaches roughly 12,500 in the first case, and the adaptive local stage consumes about 274 seconds—more than five times the entire primary-construction stage—on a horizon-four, one-dimensional problem.

This is evidence that the local relaxation can be certified, not evidence that the full method is effective. The paper devotes substantial conceptual and computational weight to a component that is not integrated into the headline optimization result.

**Required correction:** connect the local theorem to a global bound that changes the main economic conclusion, or move it to a separate methodological paper. Report error versus work curves, compare against direct exact local LP evaluation, and show how local refinement affects an end-to-end certified interval.

### R38-F9 — The economic content is too synthetic for the target journal

The maintenance environment is normalized and hand designed. The revision weight \(1+x\), transition maps, operating costs, tolerances, initial distribution, installed policies, and sensitivity perturbations are not calibrated to an economic setting. The neural and spline incumbents are inherited computational objects rather than estimated policies from data. There is no model uncertainty, estimation error, or welfare interpretation in economic units.

The 66 sensitivity cases are transparent, but they are one-at-a-time designed scenarios. Forty-four of the 66 show exactly zero dynamic-versus-pointwise savings. The remaining effects depend heavily on the chosen installed rule: 2 of 22 condition-rule cases, 16 of 22 preventive-rule cases, and 4 of 22 calendar-rule cases show positive savings. These counts have no sampling interpretation, as the authors correctly state. They therefore do not establish prevalence, empirical importance, or robustness in a class of economic environments.

A pure numerical-methods paper can be suitable for Econometrica without empirical calibration if it delivers a broadly applicable and theoretically decisive method. This paper does not yet do so. Conversely, a narrower verification method could be compelling if it changed a serious economic application. The manuscript currently occupies neither position.

**Required correction:** either add a substantive economic application with disciplined primitives and meaningful welfare units, including model/parameter uncertainty, or substantially strengthen the general convergence and scalability theory. More synthetic one-at-a-time scenarios on the same maintenance template will not resolve the journal-fit problem.

### R38-F10 — Novelty is underdeveloped and the literature review is far too thin

The bibliography contains only ten items. It covers general constrained MDPs, numerical economics, information relaxations, safe policy improvement, approximate dynamic programming, interval verification, and stochastic control, but it does not adequately position the paper against the broad literatures on occupation-measure formulations, constrained and risk-sensitive dynamic programming, switching and adjustment-cost models, verified Bellman computation, robust/safe control, semi-infinite optimization, and numerical error certification.

The paper itself acknowledges that Bellman comparison, weak duality, convexification, and constrained backward induction are established. Its claimed contribution is the constructive combination of these tools with exact proof objects and policy-revision costs. Such a combination can be valuable, but for Econometrica it must either produce a theorem unavailable from established formulations or solve an important economic problem that existing methods cannot handle. The current one-dimensional exactness results and zero-bound nonlinear feasibility experiment do not establish that level of novelty.

**Required correction:** provide a comprehensive literature map and formulate the precise theorem-level advance relative to existing constrained-control and verified-computation methods. Demonstrate empirically or theoretically why standard formulations cannot deliver the same certificate at comparable cost. Repository engineering, however excellent, is not by itself the scientific novelty criterion.

### R38-F11 — Verification independence is strong where the problem is easiest and weak where it is most consequential

The independent SymPy checks for the 42 one-dimensional primary objects and the 70 finite-tree frontiers are a major strength. The verification boundary is also described honestly. But the local-LP, sensitivity, analytic logarithm, and nonlinear experiments do not receive comparable independent implementations. The nonlinear study is the only evidence beyond one dimension, yet it is checked within the same arithmetic and modeling framework as its constructor.

The 187-object canonical comparison establishes cross-run identity. It does not establish mathematical correctness. Mutation tests show that selected corruptions are rejected; they do not measure false acceptance under unanticipated common-mode errors. Both constructor and verifier share the paper's mathematical specification and manually encoded primitives, so a paper-to-code mismatch can survive both.

**Required correction:** independently implement and verify representative local-LP and nonlinear cases, preferably with a different arithmetic stack or language; add paper-to-code contract tests; and report which theorem assumptions are machine checked versus trusted. The manuscript should not allow the strength of the primary verifier to lend an implicit “independent” label to experiments outside its coverage.

### R38-F12 — The stopped-control section does not support the paper's main claims

The killed-operator observation is mathematically standard: positivity and subprobability continuation permit Bellman comparison and witness propagation with an appropriate mass factor. This provides a conceptual bridge, but not a verified numerical solution of the retained diffusion problem.

The continuous-action, stopped consumption–portfolio target remains unsolved. The inherited full-domain bound is approximately 7.1818 against a target of 0.01. The paper correctly states that action coverage, time discretization, boundary settlement, quadrature, and diffusion approximation errors remain to be controlled. That admission means the section does not provide external validation of the proposed method.

Retaining the entire historical program may be useful for provenance, but it weakens the scientific focus of the submission. The article currently moves among a deterministic maintenance problem, randomized finite-tree frontiers, a local LP, a synthetic two-state feasibility experiment, and an unsolved stopped diffusion. These are not yet unified by an end-to-end theorem.

**Required correction:** either solve a meaningful instance of the stopped-control problem with complete action and discretization coverage, or remove this material from the main paper and preserve it only in the repository history. A generic operator analogy should not be used to imply applicability that has not been numerically demonstrated.

### R38-F13 — The manuscript is an accretion of differently scoped contributions rather than one coherent method paper

The article combines:

- deterministic outer restrictions for a uniform-initial objective;
- exact fixed-restart history-conditioned frontiers;
- a two-period randomized Markov example;
- local randomized restart relaxations;
- global finite-price support bounds;
- synthetic comparative statics;
- a two-state feasibility enclosure;
- a killed-operator bridge to an unsolved diffusion.

Each component has a different policy class, initial condition, approximation target, or verification strength. The authors now label these distinctions carefully, but careful labeling does not create a unified contribution. The paper lacks a single theorem and experiment pair showing that the proposed method solves one economically significant problem from assumptions through approximation to a tight certified answer.

**Required correction:** choose one central object and organize the paper around it. A deterministic revision paper should prove convergence and test out-of-sample deterministic problems. A randomized constrained-control paper should solve the uniform-initial randomized Markov objective. An applied economics paper should use the certificates to establish a substantive economic result. The current omnibus structure dilutes all three possibilities.

### R38-F14 — Repeated development on the same cohort creates a serious generalization problem

The repository documents a long sequence of revisions and referee-directed changes on the same 42 primary configurations. Freezing the incumbent files prevents silent replacement of the data, but it does not make the cohort an out-of-sample test. Lower-bound constructions, upper-policy generators, penalty portfolios, price sets, and diagnostics have been repeatedly adjusted after inspecting failures on this cohort.

This is not misconduct; iterative method development is normal. It does mean that closure rates on the primary table cannot be interpreted as evidence of general performance. In particular, all 14 horizon-four cases closing after repeated method development is much less informative than the same result on a prospectively specified holdout suite.

**Required correction:** evaluate the finalized method on a new, preregistered or otherwise untouched benchmark suite, with economically varied transitions, costs, horizons, dimensions, and policy classes. Report all failures and use fixed computational budgets. The current cohort should be described as a development benchmark.

## 5. Minimum scientific requirements for a future submission

The paper is not one minor revision away from acceptance. A future submission would need to satisfy a coherent subset of the following requirements.

1. **Define the central policy class and solve that object.** If deterministic policies are economically intended, justify the restriction. If randomization is admissible, provide certified bounds for the primary randomized Markov objective rather than adjacent Dirac/history-dependent problems.

2. **Provide end-to-end convergence.** Construct computable lower and upper sequences for the actual constrained objective and prove that their gap vanishes under explicit assumptions, with a usable stopping rule and at least an informative rate or complexity bound.

3. **Demonstrate nontrivial high-dimensional certification.** The nonlinear experiment must produce positive lower bounds and meaningful certified optimality gaps, not only feasible policy checks. Tolerances and computational budgets should be economically justified.

4. **Use strong same-object baselines.** Compare with direct constrained dynamic programming, occupation-measure/LP, state-augmentation, mixed-integer, or other credible methods on the identical objective and policy class.

5. **Establish economic relevance.** Either analyze a serious economic model with calibrated or otherwise disciplined primitives, or show a broad theorem and benchmark suite that makes an application unnecessary.

6. **Separate development and evaluation.** Freeze the final algorithm and test it on new holdout environments, retaining all failures.

7. **Expand and sharpen the literature positioning.** The novelty claim must be stated relative to the full constrained-control, numerical economics, switching-cost, and verified-computation literatures.

8. **Extend independent verification to the hardest components.** At minimum, the nonlinear and local-LP claims should receive independent arithmetic and model-contract checks.

Without these changes, the paper is better viewed as a meticulously documented research codebase for exact low-dimensional policy-revision certificates than as an Econometrica article.

## 6. Additional technical and presentation comments

1. Report relative gaps, not only absolute gaps. A gap of 0.10 is small beside a cost of 10 and very large beside a cost of 0.23.

2. Separate zero-cost exactness from positive-cost exactness in the abstract. The former follows immediately from nonnegative revision costs once the unchanged policy is feasible.

3. State in the abstract that ten of the twelve positive-cost exact cases are at horizon four, two at horizon eight, and none at horizon twelve.

4. The phrase “global bounds” should always name the policy class and objective. A deterministic lower bound for a uniform-initial objective is not a global bound for the randomized problem.

5. Explain the economic choice of the uniform initial distribution and report sensitivity to nonuniform distributions in the primary, not only in a separate sufficient-action sensitivity exercise.

6. The exceptional horizon-eight neural31003 case has integrated equality without full function equality. Show the exact locus of disagreement and explain whether it is isolated, off-support, or reached under alternative restarts.

7. For every unresolved case, report the gap as a fraction of the upper bound and of the installed-policy cost, together with the maximum operating violation of the outer selector.

8. Provide a theorem-assumption table mapping each result to: policy class, initial distribution, state dimension, exact/approximate arithmetic, source of lower bound, source of upper bound, and independent verifier coverage.

9. The general Borel-state theorem should explicitly state measurability of the necessary-action correspondence, the lower recursion, and the selected minimizer. Finiteness of the action set makes this manageable, but it should not be left implicit.

10. Distinguish attainment from infimum throughout. The finite-action, finite-horizon represented models attain minima, while the general function-space statement may require additional regularity.

11. The local-LP finite-termination theorem is conditional at degeneracies. Quantify how often degeneracies occurred in the executed objects and whether termination depended on exact rational coincidences specific to the benchmark.

12. Plot certified interval width against cell count and runtime for the local LP. The current three-point table hides the steep computational growth.

13. For the nonlinear model, report lower-bound diagnostics that explain why every global lower bound is zero. Is the support floor structurally zero, numerically weak, or dominated by the incumbent cost definition?

14. Compare nonlinear candidates at matched mesh, horizon, proposal count, and wall-clock budget. The current success-count table is not a controlled comparison.

15. Report memory scaling for the \(N^2\) arrays in the main text, not only in machine-readable metadata.

16. A failed sufficient box certificate should remain labeled “uncertified,” not “infeasible,” throughout figures and generated tables.

17. Clarify whether revision costs are paid on threshold-crossing boxes because of conservative enclosure or because the implemented policy genuinely changes there. This matters for interpreting nonlinear upper costs.

18. The sensitivity study should include joint perturbations. One-at-a-time changes cannot reveal interactions among discounting, persistence, intervention cost, and installed-policy geometry.

19. If neural incumbents remain, explain what economic information they encode. Otherwise they function only as complicated threshold generators and add little to the economic interpretation.

20. The computation report should provide a fully pinned environment, including exact Python build, package hashes, operating system image or container recipe, and CPU information. Version strings and object hashes are helpful but do not guarantee long-run executable reproducibility.

21. The historical annex is valuable for preservation but should not be part of the scientific burden placed on a journal reader. Keep it archival and make the current paper self-contained.

22. The paper should distinguish “independent arithmetic verification,” “same-code read-only validation,” “cross-run object identity,” and “publication-integrity checks” in every summary table, not only in prose.

23. Mutation categories should be supplemented by property-based or randomized adversarial tests of partitions, tie points, and threshold crossings. The current mutations are useful but largely hand selected.

24. The literature section needs substantially more than a paragraph per broad field. The authors should state what existing constrained-MDP or semi-infinite formulations would return on the exact maintenance problem and why the proposed construction is preferable.

25. The conclusion should not treat the nonlinear and sensitivity sections as evidence of broad external validity. They are exploratory diagnostics under synthetic primitives.

## 7. Final editorial view

R38 deserves credit for turning an unverifiable protocol into a serious computational record. The authors have also responded constructively to prior criticism by narrowing claims, separating policy classes, retaining failures, and implementing genuinely separate rational verification for the one-dimensional core. These are exemplary research practices.

The scientific result, however, remains too narrow for Econometrica. The paper closes nontrivial deterministic cases mainly where the horizon is shortest, leaves the economically broader randomized primary objective unsolved, offers no end-to-end convergence theorem, and provides no informative lower bound in the only nonlinear multi-state experiment. Its economic examples are synthetic and its literature positioning is sparse. The archive demonstrates that the reported finite objects are carefully constructed; it does not demonstrate that the proposed approach is a generally useful numerical method for important economic dynamic programs.

**Recommendation: Reject.**