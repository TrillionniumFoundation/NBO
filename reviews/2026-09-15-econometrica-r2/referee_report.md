# Referee Report: Neural Bellman Operators — R2

**Review date:** September 15, 2026
**Manuscript:** `ECTA_R2.tex` with `SUPP_R2.tex`
**Revision branch:** `revision/econometrica-r2-2026-09-15`
**Revision commit:** `4267424c529e9c07966b1fe7660bcaaa35209881`
**Recommendation:** **Reject in its present form.**

This is a repository-owner-commissioned, AI-assisted advisory report written in the style of an Econometrica report. It is not a report commissioned by Econometrica and is not an editorial decision. The review is based on the R2 commit above, its response to the earlier report, the standalone supplement, the replication directory, and the historical sources retained in the repository.

## 1. Overall assessment

R2 makes several intellectually correct concessions. It removes the false identification of the former composite loss with the control solution; records the finite-horizon composite-loss counterexample and the small-residual wrong-viscosity-limit example; corrects the Merton arithmetic; changes the Epstein–Zin aggregator; separates finite-step Adam from a conditional stochastic-approximation statement; and labels historical curves as negative controls. R2 also supplies the previously missing main and supplementary sources. These are real improvements and the prior missing-manuscript objection is closed for R2.

They do not establish a publishable method. R2 repeatedly describes an audited numerical method and a new coupled scalability experiment, but the repository contains no author solver, training configuration, coupled benchmark implementation, author run, probe-count experiment, NDU collocation output, temporal-self deviation output, or Cournot exploitability output. `replication/results.jsonl` contains one row, explicitly labelled `analytical_check`, with every substantive metric null. The paper still draws economic conclusions from historical arrays that it says must not be treated as current evidence.

There are independent mathematical blockers. The central NDU objective discounts only consumption utility while its HJB discounts the entire continuation value. The temporal-self objective puts beta on continuation in the main text but on current utility in the supplement. The exact-operator proposition is missing the topological and verification conditions needed to pass from policy improvement to an optimal accumulation point. The separation of parameter blocks is sensible, but it is not a theorem about a neural implementation, and no implementation is supplied.

I would reject this version in its present form. A future submission needs an actual method, a coherent model specification, and executed evidence, rather than a more elaborate description of what an audit should contain.

## 2. Status of the earlier objections

| Earlier issue | R2 status | Assessment |
|---|---|---|
| R0 missing manuscript | Closed for R2 | Main, supplement, response and index now exist and can be compiled. |
| R1 composite-loss minimizer | Textually addressed | Old loss removed from the authoritative method; no executed separated solver. |
| R2 boundary/well-posedness | Partially addressed | Generic assumptions added; application domains, boundary operators and terminal data remain unspecified. |
| R3 viscosity selection | Correctly narrowed | Invalid selection claim withdrawn; no new solver result on a nonsmooth problem. |
| R4 Merton arithmetic/kink | Algebraically addressed | Correct targets and no-short classification; no author policy/value output reproduces them. |
| R5 provenance | Not closed | No replacement author experiments; historical plots still support economic prose. |
| R6 Epstein–Zin sign | Algebraically addressed | Positive marginal utility restored; no domain-enforcing implementation or verified recursive solution. |
| R7 convergence/stability | Correctly narrowed | Adam excluded from asymptotic claim; no finite-step evidence or new approximation theorem. |
| R8 endogenous preferences | Not closed | Discounting mismatch, ambiguous boundaries and interior-FOC issues remain. |
| R9 time inconsistency | Not closed | Main and supplementary equations are inconsistent. |
| R10 dynamic games | Partially addressed | Rival detachment described; no dynamic game or best-response evidence. |
| R11 scalability/novelty | Not closed | Coupled experiment and baselines absent. |
| R12 stochastic Hessian | Algebraically addressed | Variance identity corrected; no probe-count experiment. |

## 3. Detailed findings

### F1. The claimed empirical contribution has no author run behind it — blocking

**Sources:** `ECTA_R2.tex:526-568,812-859,1079-1081,1145`; `replication/results.jsonl:1`; `replication/README.md:20-35`.

The abstract and introduction say that R2 reports audited comparisons to analytical and independently solved benchmarks. The validation section says that it adds a coupled benchmark, matched sparse-grid comparisons, held-out tests, ablations, uncertainty across seeds, and value/policy/boundary/improvement errors. The repository contains none of these records. Its sole JSONL row has status `analytical_check`, code commit `bf049e3`, an all-zero configuration hash, null value/policy/boundary/improvement/exploitability metrics, and a null raw-output checksum. It expressly says that it is not an author training run.

A repeat of the referee's counterexamples is useful regression material, but it does not validate the corrected algorithm. There is no NBO training code, configuration, baseline code, trained parameter file, raw run log, or figure-generation program in the inspected tree. The central empirical assertions are therefore unsupported statements of planned work.

**Required response:** Supply the solver and configurations, execute the corrected benchmarks and applications, archive every declared seed and failure, and generate current tables/figures from actual result records. Replace present-tense claims of completed experiments with an accurate account until that evidence exists.

### F2. The central NDU objective is not represented by its HJB — blocking

**Sources:** `ECTA_R2.tex:913-930`, especially objective line 915 and HJB line 921.

The objective integrates `exp[-rho(s-t)] * c^(1-u)/(1-u) - k*theta^2/2` and then adds an undiscounted terminal payoff G. Only consumption utility is discounted. The HJB is `-V_t = sup{c^(1-u)/(1-u) - k*theta^2/2 + D V - rho V}`. This discounts the entire continuation value, including the adjustment cost and terminal payoff, and solves a different problem.

A terminal-only restriction makes the mismatch transparent. With zero running payoff and G=1, the undiscounted terminal functional has V(t)=1. The displayed HJB instead gives `-V_t=-rho V`, V(T)=1, hence `V(t)=exp[-rho(T-t)]`. These disagree whenever rho>0 and t<T. This is an algebraic diagnostic of the discount convention, independent of approximation and training.

**Required response:** Choose a coherent objective. If all utility and costs are exponentially discounted, discount the whole integrand and terminal payoff consistently. If different components have different discount rules, derive the appropriate enlarged/decomposed value system. Re-derive the HJB, terminal condition, FOCs and comparisons from that exact objective.

### F3. The temporal-self equations remain contradictory — blocking

**Sources:** `ECTA_R2.tex:1057-1066,1164-1172`; `SUPP_R2.tex:23-34`.

The main one-shot objective is `sup_c {u(c)+beta V^pi(s')}`, placing beta on continuation. The supplement instead maximizes `beta u(c)+D^c V`, placing beta on current utility, and evaluates `-V_t=u(c*)+D^{c*}V`. These equations are not equivalent. No value normalization or change of units is given that reconciles them. The generator was previously defined without discount killing, yet no discount rate/kernel appears in this supplementary evaluation equation. The main text says the two sources now use one authoritative equilibrium system; that assertion is contradicted by the equations.

For the simple resource transition s'=w-c and CRRA flow, the main form gives `u'(c)=beta V'(w-c)`, while the supplementary local form gives `beta u'(c)=V_x`. At a fixed unit continuation marginal and gamma=2, beta=.7 gives c=1/sqrt(.7) in the first expression and c=sqrt(.7) in the second. This calculation diagnoses non-equivalence; it is not a full equilibrium comparative static.

**Required response:** Specify one discrete- or continuous-time preference model, derive its equilibrium equations from the stated one-shot deviation criterion, provide the discount/continuation conventions and boundary data, and then execute the beta=1 and deviation-gain tests. Relabelling both formulas as extended HJB does not reconcile them.

### F4. The exact-operator theorem is under-specified and does not bridge to NBO — blocking

**Sources:** `ECTA_R2.tex:626-665,781-790,1127-1142`.

The proposition assumes exact evaluation, pointwise maximization, a monotone policy-iteration sequence and a compact admissible policy class. The proof then claims that compactness yields accumulation points and continuity passes the improvement inequality to the limit. The topology of policy compactness is unspecified; value precompactness/equicontinuity and derivative or generator convergence are absent; continuity of the evaluation map is not established; and no argument identifies the limit of the shifted sequence pi_(n+1) with the necessary improvement of the limiting evaluated policy. The appropriate conclusion may be provable under stronger hypotheses, but it is not proved here.

The recursive utility operator is named rather than fully defined with its existence, comparison, monotonicity/properness, integrability and verification conditions. Pointwise maximization requires an attained supremum, measurable selectors and closure of the feedback class under improvement. A finite bounded-parameter neural class is not generally closed under pointwise Hamiltonian maximization. Assuming the exact iteration succeeds does not show that the stated network/sampling algorithm approximates it with controlled error.

The actor remark also claims that frozen-Hamiltonian ascent under an arbitrary improvement measure is precisely policy-gradient ascent of J=V^pi(0,s0), and always improves the policy with lower variance. That is unsupported. A lifetime-objective gradient needs the appropriate policy-induced occupancy/adjoint weighting; an arbitrary sampling measure and a shared neural parameterization do not provide it. Local or expected Hamiltonian improvement is not a guarantee that a finite step improves every state's policy or the initial-state objective.

**Required response:** State the function spaces/topologies, recursive-generator conditions, selector/closure assumptions, convergence mechanism and verification inequalities. Distinguish an exact policy-iteration theorem from a neural approximation result. Add a quantitative link from critic, boundary and actor errors to value/policy performance, or establish the method empirically with honest scope.

### F5. The application does not define a unique admissible boundary-value problem — blocking

**Sources:** `ECTA_R2.tex:869-881,900-948`; `SUPP_R2.tex:24-30`.

The NDU section promises a reflected or viability-preserving diffusion, but gives neither mechanism. Reflection requires a local-time term and associated boundary condition; a state-constraint model requires admissibility and viscosity boundary conditions. They are different economic models. The equations remain additive Brownian dynamics without reflection, while numerical u/X bounds, borrowing rules, T and G are not specified. The interval for u is not required to avoid u=1 and no NDU log limit is given. The written CRRA level diverges at u=1; declaring cardinal normalization without providing it does not resolve that issue.

The FOCs are interior formulas requiring positive V_X, suitable concavity and inactive constraints. The model declares bounds and solvency constraints but writes an unrestricted supremum and provides no constrained maximizers/KKT conditions. Thus the policy functions and k-comparative statics are not defined for the promised constrained model.

Similarly, the EZ section says a monotone value transform enforces bV>0, but no transform, parameterization or compatible terminal G is supplied. For gamma>1, the terminal value must satisfy the stated sign-domain condition. The formal ratios (.3,.0455) are correctly labelled candidates; no verification or numerical solution converts them into a result about the method.

**Required response:** Supply actual parameters, domains, action sets, terminal payoff, normalization and boundary operator for each application, derive the boundary/control conditions, and solve those precise models.

### F6. The claimed coupled scalability experiment is absent — blocking

**Sources:** `ECTA_R2.tex:739-777,852-859`; repository tree at commit `4267424`.

R2 says that it adds a common-resource, correlated-shock, cross-stock benchmark and a matched sparse-grid comparison. The source contains no coupled resource equation, covariance specification, data generator, sparse-grid implementation, configuration, or output. The old `scaling_comparison.dat` array is only a hand-entered filecontents block. The source also claims that an exact Hessian step at d=50 takes milliseconds on an H100, but no hardware log, benchmark script or measured run is archived.

The original d-stock experiment is explicitly separable. A protocol paragraph does not demonstrate a cost–accuracy–certificate advantage on a genuinely coupled model.

**Required response:** Add the coupled model and independently verified reference solution; run NBO and a matched baseline at fixed accuracy and resource budgets; report wall time, memory, failures, value/policy/boundary/improvement errors and multiple seeds; include ablations. Remove the H100 timing claim until it is measured and archived.

### F7. Historical negative controls still carry substantive economic conclusions — major

**Sources:** `ECTA_R2.tex:6-198,951-1047`; `replication/README.md:33-35`.

R2 says historical arrays are negative controls and that figures must be generated from `results.jsonl`. Yet the authoritative TeX still embeds roughly fourteen `.dat` arrays and renders them directly. The text says the NDU surface “reveals” a house-money effect and “confirms” the derived policies; the comparative statics are called intuitive and economically meaningful. The alleged fine-grid policy surface has only 15 hand-entered points (three wealth values by five u values), and the paths have eleven points. These are substantive inferences from data the revision says must not be treated as R2 evidence.

Captions describing the arrays as historical do not cure the surrounding claims that they are learned policies evaluated from trained networks. No weights, code or run record exists. The old Merton array also jumps from c=5.430796 and pi=-0.270625 at epoch 10,000 to c=.0302 and pi=.5011 at epoch 15,000; it cannot substantiate convergence to the corrected targets.

**Required response:** Remove the historical plots from the evidentiary flow or supply the replacement runs. Generate current figures and tables only from the authoritative ledger, with run IDs and checksums joined to every curve.

### F8. The corrected Epstein–Zin expression is not an audited numerical result — major

**Sources:** `ECTA_R2.tex:868-893`.

Changing the aggregator and reporting the formal candidates pi=.3 and m=.0455 are genuine algebraic improvements. They do not establish a recursive-utility validation. The manuscript supplies no terminal/boundary data, value normalization, admissible wealth domain, parameter file, domain-violation count, or trained output. It asserts that a monotone value transform enforces bV>0, but no transform or architecture is given; for gamma>1, a compatible terminal payoff must satisfy the same sign condition. The finite-horizon notation and stationary benchmark are not reconciled.

The candidates should be labelled as algebraic targets until a complete recursive-utility experiment is supplied.

### F9. The dynamic-game correction is not an equilibrium result — major

**Sources:** `ECTA_R2.tex:1067-1075`; `SUPP_R2.tex:36-46`.

Detaching rivals is the right distinction, and the static 1/3 versus 1/4 Cournot arithmetic is correct. It is not evidence that the dynamic implementation computes a Markov-perfect equilibrium. There is no player-specific solver, state transition, terminal condition, initial-profile run, best-response code, exploitability output or market-size normalization record. The claimed competitive limit and multiple-initialization evidence are prose only.

**Required response:** Provide the game and player-specific implementation, independent best-response solver, exploitability metric, equilibrium assumptions, and run-level results from multiple initial profiles.

### F10. The stochastic-Hessian correction is algebraically right but unverified — major

**Sources:** `ECTA_R2.tex:739-777`; `SUPP_R2.tex:48-54`.

The identity
\[
\mathbb E(a-\widehat q/2)^2=(a-q/2)^2+\operatorname{Var}(\widehat q)/4
\]
is correct, as is the warning about the symmetric diffusion-weighted Hessian. R2 supplies no probe-count records, exact-versus-stochastic output, runtime/memory measurement, or value/policy/boundary comparison. It describes the experiment that should be run rather than reporting one. The O(Kd) statement also suppresses network width, batch, HVP, diffusion-loading and higher-order autodiff costs; it is not a complexity theorem without a cost model.

### F11. The NDU comparative statics remain unsupported — major

**Sources:** `ECTA_R2.tex:932-952,1019-1047`.

The response appropriately retracts the identification claim, but the paper still interprets the historical policy surface and k-comparative statics economically. The interior FOCs require V_X>0, V_XX<0, inactive controls and a valid interior optimum. None is proved or checked. The formula theta=V_u/k is presented “subject to bounds,” but no boundary/KKT solution is derived. With the reflected/viability mechanism unspecified, the adjustment policy is not determined by the displayed HJB.

A comparative-static illustration is informative only after the same fully specified model is solved for each k and its policy/value/boundary errors are reported. R2 contains none of these outputs.

### F12. Buildability is not the claimed clean, reproducible audit package — major

**Sources:** `revisions/2026-09-15-r2/revision_manifest.json:30-57`; `ECTA_R2.tex` build log.

The declared LaTeX/BibTeX sequence succeeds locally: the main source produces 38 pages and the standalone supplement 2 pages. This is a useful source-level check, but it does not validate the empirical claims. The manifest's ECTA_R2 SHA-256 is wrong: it records `e837f803...c66662`, whereas the committed file hashes to `dc61ba00ded25771ba3b8b49ef60bbd57a99ea80c1579d6d04c64fb923cbcc81`. The manifest claims that it records environment versions, domains, stopping criteria, failed pilots and held-out distributions; the JSON contains no such records. It also lists the R1 review directory as preserved, although that directory is absent from the R2 tree because it exists only on the separate review branch. Built PDFs and logs are not committed.

The build log also retains duplicate `merton_convergence.dat` and `viscosity_policy.dat` declarations, duplicate historical appendix PDF destinations, font/bookmark warnings, and overfull boxes of approximately 41pt in the Merton table, 82pt in the NDU path caption and 36pt in the policy-surface caption. The R2 source repeats the Application 2 subsection heading. These are fixable, but they contradict the claim that the repository is already an audit-ready package.

**Required response:** Correct the digest, generate the manifest from the committed tree, commit the environment/build transcript or a reproducible lockfile, remove duplicate data declarations and identifiers, and resolve the material layout warnings.

## 4. What would make a new submission reconsiderable

A reconsiderable submission needs one coherent formal object for each application: objective, discount convention, state/action domain, terminal payoff, boundary mechanism, admissibility and equilibrium definition. The exact HJB/extended-HJB equations must follow from those objects and include the properness, comparison, selector, closure and verification assumptions needed for the theorem.

It also needs an actual implementation: solver code, configurations, dependency record, deterministic data-generation scripts, matched baseline, tests for detached critics and rivals, boundary enforcement and probe modes. The theorem should be labelled conditional unless a quantitative approximation result connects finite networks and finite samples to the exact operator.

Finally, it needs executed evidence: multiple seeds and failed pilots for corrected Merton and exit-time tests; a recursive-utility run with domain audits; an NDU run with viability/boundary diagnostics; a temporal-self run with beta=1 and held-out one-shot deviation gains; a Cournot run with unilateral exploitability; a probe-count comparison; and a genuinely coupled scalability comparison. Every record must carry a valid code commit, configuration digest, raw-output digest and non-null error metrics. Historical curves can remain in an archive, but they cannot support current claims.

## 5. Verification and limitations

I compiled `ECTA_R2.tex` and `SUPP_R2.tex` locally with the declared LaTeX sequence and obtained 38-page and 2-page PDFs. I parsed the JSON/JSONL artifacts and independently checked the source hashes. One source digest is false. I inspected the complete R2 tree and found no solver, author run, baseline, raw output or coupled benchmark implementation. The twelve diagnostics in the earlier review remain reproducible, but they are reviewer arithmetic/counterexample checks rather than author-experiment replication.

For policy-improvement context, the report's missing topology, precompactness and generator-compatibility conditions are material: Jacka and Mijatović's primary treatment of continuous-time policy improvement explicitly separates payoff improvement, payoff convergence and policy convergence and imposes corresponding compactness and regularity conditions ([primary source](https://arxiv.org/abs/1509.09041)). For time inconsistency, the standard continuous-time framework is a game-theoretic extended-HJB system for equilibrium strategy and value, not an interchangeable placement of beta ([Björk, Khapko and Murgoci](https://arxiv.org/abs/1612.03650)). These references do not prove the NBO paper false by themselves; they show which omitted mathematical objects must be specified.

This is not an official Econometrica report or editorial decision. The recommendation is based on the source state at commit `4267424c`; it does not infer author intent. A later commit adding the missing solver, runs and corrected formal specifications should be reviewed as a new submission.

## 6. Recommendation

**Reject in its present form.** R2 genuinely repairs several statements and accepts decisive counterexamples, but it replaces the previous unsupported solver claim with a conditional operator description and an unexecuted audit protocol. The NDU objective/HJB mismatch and the contradictory temporal-self equations are independent mathematical blockers; the absence of any author experiment makes the claimed empirical contribution impossible to assess.
