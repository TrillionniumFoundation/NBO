# Referee Report: Neural Bellman Operators

**Review date:** September 15, 2026  
**Author of the manuscript:** Qian QI  
**Recommendation:** **Reject in its present form.**  
**Review status:** Repository-owner-commissioned, AI-assisted, Econometrica-style advisory review. This is not a report commissioned by Econometrica, an actual editorial decision, or a certification of reviewer independence. The repository is public; this document is not confidential correspondence with a journal.

## 1. Version, scope, and evidentiary standard

The object of this report is the latest manuscript actually available in `TrillionniumFoundation/NBO` when the repository was inspected and rechecked on September 15, 2026:

- Base commit: `bf049e302e9ed38303084e8da16b13717b052a70`.
- Base tree: `c7fc1b26457d0a37aef54bb74c337d6433acfde4`.
- Main manuscript: `ECTA.tex`, blob `2278f19fb009911d810d420722d75a298dd84096`.
- Separate supplement: `supp.tex`, blob `9ba390ec3b4f34f69a11de9db9201e60b4e6ba76`.

At both branch checks, the repository contained only `main`, pointing to this commit. Its available history contains the manuscript import and a merge, not an identifiable sequence of revision and referee-response branches. `comments.tex` contains informal comments about positioning preference-formation research; it is not a point-by-point response to an authenticated previous report. Accordingly, this review does **not** certify that any particular previous referee objection has been addressed. It reviews the current submission on its merits rather than inventing a revision history.

The review covers the mathematical model, the stated training objective, the main proposition and convergence argument, the numerical claims and their TeX data sources, the inline supplementary appendix, and the separate `supp.tex`. The recursive repository tree was inspected for replication materials. External primary literature was checked for the methodological comparisons and recursive-utility and stochastic-approximation formulations.

The numerical checks supplied with this report are independently constructed arithmetic and counterexample checks. They are **not replications of the author's training experiments**. No author training program, raw multi-seed run logs, or environment specification was present in the inspected tree. No manuscript PDF was supplied in that tree or compiled for this review. Statements about figure construction concern the actual TeX plotting instructions and embedded data, not an inspected PDF rendering. Unused PNG files cannot establish the provenance of figures that the main manuscript generates from different inline sources.

All manuscript line ranges below refer to the pinned commit, not to a moving branch. TeX labels are included where useful because they identify the mathematical object more reliably than a subsequently changing equation number.

## 2. Overall assessment

The problem the paper wants to solve is worthwhile: a reusable neural policy/value solver for continuous-time economic models with recursive objectives, constraints, endogenous preferences, and strategic interaction. Smooth automatic differentiation, explicit feasible policy parameterizations, and a separation between policy evaluation and policy improvement are sensible ingredients. The formal cross-derivative term in the NDU Hamiltonian is also a useful starting point for a substantive application.

The submitted paper does not, however, establish that its proposed algorithm solves these problems. The difficulty is not merely a lack of a global convergence theorem for neural-network optimization. The **population objective itself is inconsistent with the claimed solution**, including in a smooth scalar problem with an exactly imposed terminal condition. The purported viscosity-selection argument fails independently of optimization. The main analytical benchmark uses incorrect constants. The recursive-utility aggregator reverses the marginal utility of consumption in the numerical parameter regime. The central stability comparison figure is constructed using an unrelated curve plus artificial oscillation rather than demonstrated independent training runs.

These defects invalidate the main chain of evidence: correct objective, correct theoretical solution, successful validation, and then economically meaningful applications. More polished prose, additional references, or additional neural-network capacity would not repair that chain. I would not recommend an ordinary revise-and-resubmit based on the present record. A substantially rebuilt and fully auditable submission could be evaluated anew; the report gives concrete conditions for such a submission without requiring that the research ambition be abandoned.

### Decision-relevant issues

| ID | Severity for the current submission | Finding |
|---|---|---|
| R1 | Blocking | The global-minimizer proposition is false for the specified composite loss. |
| R2 | Blocking | Boundary, terminal, and well-posedness conditions are not implemented or established. |
| R3 | Blocking | Vanishing population residual does not establish viscosity selection. |
| R4 | Blocking | Merton benchmark constants are wrong; the constrained example has no claimed wealth kink. |
| R5 | Blocking | The empirical evidence has demonstrable source/provenance inconsistencies. |
| R6 | Blocking | The stated Epstein–Zin aggregator has the wrong consumption monotonicity. |
| R7 | Blocking | The stability and convergence arguments do not cover the actual algorithm. |
| R8 | Major | The endogenous-preference model and its economic interpretation are not sufficiently defined. |
| R9 | Major | The time-inconsistency equations do not establish the stated equilibrium. |
| R10 | Major | The game algorithm conflates joint optimization with unilateral best responses. |
| R11 | Major | The scalability experiment is separable and the claimed contribution is not isolated. |
| R12 | Major | The stochastic-Hessian discussion misses objective bias and overstates its complexity conclusions. |

“Blocking” means that a central claim cannot be relied upon in its submitted form. “Major” does not mean optional: the corresponding application or methodological claim also needs substantive repair. The evidence distinguishes direct counterexamples, algebraic errors, missing hypotheses, and unverified experimental assertions; these categories should not be conflated.

## 3. Detailed comments

### R1. The proposed composite loss does not have the asserted correct minimizer

**Locations:** [ECTA.tex, lines 600–690](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L600-L690), `eq:loss_total`, `eq:loss_perf`, `eq:loss_hjb`; [lines 831–879](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L831-L879), `prop:optimality`; [proof, lines 1690–1790](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L1690-L1790).

The paper defines

\[
L(\pi,V)=-\mathbb E H^\pi[V]+\omega\mathbb E\bigl(-V_t-H^\pi[V]\bigr)^2
\]

and explicitly differentiates this total loss with respect to both actor and critic parameters. Proposition 1 claims that a global minimizer gives the correct viscosity solution. Step 1 of its proof reasons that minimization of the sum forces the nonnegative residual term to be zero. That implication is false. A sum trades off its components, and the performance term is not even required to be nonnegative.

This is not a technical omission that can be resolved by adding a citation. Consider the following finite-horizon counterexample. There is one feasible action, no state evolution, terminal date 1, aggregator `f(v)=-v`, terminal utility 1, and uniform sampling on `[0,1]`. The data are smooth and Lipschitz. The correct value is

\[
V^*(t)=e^{t-1},\qquad -V_t+V=0,\qquad V(1)=1.
\]

With the paper's default weight `omega=1`, its population loss becomes

\[
L(V)=\int_0^1\left[V(t)+\{-V'(t)+V(t)\}^2\right]dt.
\]

Now take the smooth perturbation

\[
V_\varepsilon(t)=e^{t-1}-\varepsilon(1-t).
\]

It preserves the terminal condition **exactly**. Its residual is `-epsilon(2-t)`, and direct integration gives

\[
L(V_\varepsilon)-L(V^*)=-\frac{\varepsilon}{2}
 +\frac{7\varepsilon^2}{3}<0
 \quad\text{for }0<\varepsilon<3/14.
\]

At `epsilon=3/28`, the decrease is `-3/112`. Thus the correct value is **not even a local minimizer** of the advertised loss. This example does not rely on a missing terminal penalty, finite-sample overfitting, nonsmoothness, an inaccurate actor, or failure of an optimizer. The strict inequality persists under sufficiently accurate smooth approximations of the functions and their derivatives. Invoking universal approximation therefore cannot rescue the proposition.

The stationary analogue makes the distortion transparent. With `H=q-rho*v`,

\[
-H+\omega H^2=\omega\left(H-\frac{1}{2\omega}\right)^2-\frac{1}{4\omega}.
\]

The loss is minimized at a **nonzero** Hamiltonian, `H=1/(2 omega)`, rather than the Bellman root. For `q=rho=omega=1`, the correct value is 1 but the composite loss prefers 0.5.

The prose also describes a different algorithm in which the critic minimizes only policy-evaluation error and the actor maximizes the Hamiltonian while treating the critic as fixed. That block-update algorithm is not equivalent to joint differentiation of the stated scalar loss. The subsequent assertion that the critic's performance gradient usefully anchors its level is precisely the source of the bias above. Moreover, the displayed formula for that gradient omits derivative-channel contributions from the generator in general.

**Required response:** Specify the actual computational graph, including every detached quantity and every parameter block's objective. Replace the false proposition with a valid theorem for that exact algorithm or a correctly formulated constrained optimization problem. Supply the counterexample above as a mandatory regression test. A response saying that separate actor–critic updates were intended is insufficient unless the definitions, proofs, pseudocode, implementation, and reported experiments are all reconciled.

### R2. The target boundary-value problem is not enforced, and its generality is overstated

**Locations:** [ECTA.tex, lines 565–650](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L565-L650); [implementation and assumptions, lines 1595–1710](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L1595-L1710).

The mathematical control problem has a terminal payoff, but the main loss has no terminal-condition term, boundary-condition term, or explicitly hard-constrained value architecture. The implementation describes a generic value network. Learning a differential equation is not the same as learning its prescribed boundary-value solution. For example, with zero flow payoff and zero dynamics, every constant value network has zero interior residual, although terminal payoff zero selects only the zero function.

The infinite-horizon applications need their own growth and transversality conditions. The paper moves between finite- and infinite-horizon equations and stationary policies without consistently specifying these conditions. Continuity and Lipschitz assumptions on primitive functions plus compact controls do not, by themselves, establish the claimed uniqueness on an unspecified unbounded domain and function class. Nor do they establish that the CRRA and recursive examples satisfy the hypotheses near their singularities.

There are two additional problems with the general formulation. First, an arbitrary predictable covariance process `Q_t` need not be determined by `(t,S_t)`. A deterministic Markov HJB in that state requires a Markov closure assumption or an augmented state. A general continuous martingale also does not have conditionally Gaussian increments merely because its quadratic variation is known; a Brownian-diffusion approximation requires a specified representation and convergence conditions. Second, recursive utility should be defined for each admissible policy through its own utility process, with suitable existence and comparison conditions, before taking the supremum. Inserting the optimal value into every candidate control's objective is not a substitute for establishing this construction.

**Required response:** State a precise controlled Markov model, admissibility class, value-function class, boundary and terminal conditions, and the relevant comparison/verification result. Show how those conditions enter training and independent evaluation. Identify which applications actually meet the assumptions. This requirement is independent of R1: adding boundary penalties alone does not remove the composite-loss bias.

### R3. The viscosity-selection argument is not valid

**Locations:** [ECTA.tex, lines 815–879](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L815-L879), `sec:vanishing_viscosity`; [lines 1800–1845](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L1800-L1845), `thm:uat_derivatives`.

The paper identifies integral residual minimization and neural spectral bias with an implicit vanishing-viscosity scheme. No such equivalence is established. There is no defined positive viscosity parameter generated by network capacity, no consistency analysis for that parameter, and no comparison-compatible selection argument. The text's own estimate gives squared residual contribution proportional to `1/delta` for a layer of width `delta`. That contribution increases, rather than decreases, as the layer is sharpened. An unsupported appeal to semiconcavity does not reverse the calculation.

A simple counterexample demonstrates why a population `L2` residual is insufficient even with exact boundary values. Consider the deterministic exit-time control problem on `(-1,1)` with speed `a in [-1,1]`, payoff minus elapsed time, and zero payoff at exit. Its HJB is

\[
F(V')=1-|V'|=0,\qquad V(-1)=V(1)=0,
\]

and the value is `V*(x)=|x|-1`. Define smooth functions

\[
W_\varepsilon(x)=\sqrt{1+\varepsilon^2}-\sqrt{x^2+\varepsilon^2}.
\]

They satisfy the boundary values exactly, are uniformly bounded and 1-Lipschitz, and converge uniformly to the **wrong** function `W(x)=1-|x|`. Under uniform probability on `[-1,1]`,

\[
\mathbb E\{1-|W_\varepsilon'|\}^2
=2-2\sqrt{1+\varepsilon^2}+2\varepsilon
 -\varepsilon\arctan(1/\varepsilon)\longrightarrow0.
\]

Nevertheless, at zero the smooth test function `phi(x)=1` touches `W` from above, and `F(phi')=1>0`; the viscosity subsolution inequality fails. At `epsilon=0.0001`, the mean squared residual is about `4.292e-5`, while the value error at zero is about `1.9999`.

This example concerns the paper's generic residual-to-viscosity inference for degenerate control equations; it is not presented as a second finite-horizon counterexample to precisely the same proposition. R1 already provides that counterexample. Importantly, the exit-time example uses the **exact supremized operator**, so replacing an imperfect actor by exact Hamiltonian maximization would not resolve this selection problem.

The derivative approximation theorem is also used beyond its scope. Approximation of a `C2` target and its derivatives does not establish uniform approximation of nonexistent classical derivatives at a kink. Density of an increasing family of networks does not imply that a fixed three-layer, 256-neuron architecture attains a zero minimum. Smooth activation functions are appropriate for classical automatic differentiation; they do not supply the missing selection theorem.

**Required response:** Supply an actual convergence mechanism for the relevant PDE class, with boundary treatment, comparison, compactness, sampling coverage, and actor maximization error addressed. Alternatively, present precisely delimited empirical evidence rather than asserting a theorem that the objective does not support. A genuine nonsmooth benchmark must distinguish the economically correct viscosity solution from small-residual alternatives.

### R4. The analytical validation is numerically wrong and the constrained test has no stated kink

**Locations:** [ECTA.tex, lines 879–999](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L879-L999), `tab:merton_results`, `tab:merton_constrained`, `sec:viscosity_test`.

For the stated unconstrained Merton parameters, the risky-asset share is

\[
\pi^*=\frac{\mu-r}{\gamma\sigma^2}
=\frac{0.08-0.02}{2(0.2)^2}=0.75,
\]

not the reported analytical value 0.50. Under the stationary infinite-horizon interpretation used to justify constant consumption, the consumption–wealth ratio is

\[
m=\frac{\rho+(\gamma-1)\left[r+\frac{(\mu-r)^2}{2\gamma\sigma^2}\right]}{\gamma}
=0.04125,
\]

not 0.030. The manuscript actually writes a finite-horizon objective, so it must first specify the horizon and bequest/terminal condition before claiming a constant consumption benchmark. The stationary calculation is a conditional diagnostic, not an assertion that an unspecified finite-horizon problem has this same consumption rule.

The constrained test uses `mu=0.01`, `r=0.02`, `gamma=2`, and `sigma=0.2`. Its unconstrained allocation is `-0.125`, not `-0.25`. With the no-short-sale restriction, the optimal allocation is zero at **every positive wealth level**. There is no wealth threshold at which the risky allocation changes from an interior optimum to a binding constraint in this constant-parameter homothetic example. It therefore cannot verify the claimed wealth-dependent kink mechanism.

A bound on a regular control does not automatically turn the HJB equation into an obstacle variational inequality. The maximized HJB remains an equality at the optimum; action-space KKT inequalities are not strict inequality of the HJB itself at `pi=0`. Similarly, a binding control constraint does not automatically imply a discontinuous value gradient. The paper repeatedly conflates these different objects.

**Required response:** Derive the benchmark independently, reconcile horizon and payoff conventions, and regenerate every associated result. Use a genuinely state-dependent switching or free-boundary problem to test nonsmooth solution selection. Convergence of ten runs to the same wrong benchmark is not validation.

### R5. The source does not support the reported experimental evidence

**Locations:** [embedded data, ECTA.tex, lines 1–211](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L1-L211); [constrained plot, lines 950–999](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L950-L999); [stability plot, lines 1190–1235](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L1190-L1235), `fig:ez_comparison`; [replication note, lines 1580–1605](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L1580-L1605).

The central comparison of NBO against DDPG is not supported by the figure-generation source. The moderate-risk-aversion NBO curve reads `c_mean` from `merton_convergence.dat`. The purported DDPG curve is generated from the same column plus `0.005*sin(deg(epoch/500))`. The accompanying comments explicitly identify placeholder logic and simulated DDPG noise. The high-risk-aversion panel consists of a few directly entered coordinates for each method. These are not evidence of independently trained NBO and DDPG runs. Yet the surrounding text interprets them as an empirical stress test demonstrating structural instability of the competing method.

This is a substantive evidentiary failure, not a graph-style issue. An illustrative construction can be useful when clearly identified as an illustration; it cannot establish an observed failure rate, a convergence trajectory, or robustness to high risk aversion. The source establishes how this figure was constructed. It does **not** establish intent, and this report makes no allegation about the author's motives or conduct beyond the documented mismatch.

The constrained-portfolio figure has another independently checkable inconsistency. Its y-axis is limited to `[-0.05,0.1]`, but all 11 submitted data points lie between `0.363228` and `0.608903`, outside those limits. The caption describes 100 wealth evaluations and a near-zero allocation, while the table reports a mean of 0.0001. The numerical values used by the figure are inconsistent with both statements. This source-level conclusion does not require claiming that a PDF was rendered or inspected.

The inspected repository contains TeX, bibliography and template files, and PNGs, but no solver implementation, run configurations, raw seed-level logs, or scripts connecting a saved model to each table and figure. Several captions describe replication code as publicly available, whereas the conclusion promises availability only upon publication. The README remains a LaTeX-template README. Embedded arrays are not a substitute for experimental provenance.

Additional inconsistencies reinforce the need for a complete audit: the Cournot table gives capital 8.1 for two firms and 5.5 for five firms, whereas the plotting data give 8.0 and 5.0. The Merton and constrained-policy data files each have repeated `filecontents` definitions. These may reflect stale editing, but the current package gives no authoritative data-generation path that resolves them.

**Required response:** Provide the executable solver and baseline implementations, locked dependencies, complete parameters and domains, seed list, saved raw training/evaluation outputs, and deterministic figure/table generation. Every numerical claim must be traced to a run and artifact checksum. Report failed runs and stopping criteria, not just successful averages. Replace the constructed stability comparison with actual matched experiments, or withdraw its status as experimental evidence. No conclusion about relative solver stability should survive solely on the existing illustration.

### R6. The Epstein–Zin aggregator has incorrect monotonicity in the reported regime

**Locations:** [ECTA.tex, lines 1090–1145](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L1090-L1145), `eq:ez_aggregator`, `eq:ez_hjb_full`, `tab:ez_results`.

Write `a=1-1/psi`, `b=1-gamma`, and `Y=bV>0`. The submitted aggregator is

\[
f_{\rm paper}(c,V)=\frac{\rho b}{a}c^aY^{1-a/b}-\rho V.
\]

Consequently,

\[
\partial_c f_{\rm paper}=\rho b c^{a-1}Y^{1-a/b}.
\]

For the reported `gamma=5`, this derivative is negative. At `c=1` and `V=-1/4`, it equals `-0.16`. With an economically admissible increasing wealth value, `V_X>0`, the consumption derivative of the Hamiltonian is `f_c-V_X<0`. The positive interior consumption rule claimed in the table therefore cannot satisfy the maximization problem as written.

For comparison, under a conventional difference-form normalization one writes

\[
f_{\rm std}(c,V)=\frac{\rho}{a}
\left[c^a(bV)^{1-a/b}-bV\right].
\]

This has positive marginal utility of consumption and the appropriate time-additive specialization when `gamma=1/psi`. The difference-form aggregator and parameter-domain issues are discussed explicitly in Herdegen, Hobson, and Jerome [B3, Section 4, equation (4.3)]. The comparison is about normalization and algebra, not an assertion that their global verification theorem covers the manuscript's parameter regime.

Under this conventional normalization, substituting a stationary homothetic candidate gives

\[
\pi=\frac{\mu-r}{\gamma\sigma^2}=0.3,
\qquad
m=\psi\rho+(1-\psi)
\left[r+\frac{(\mu-r)^2}{2\gamma\sigma^2}\right]=0.0455.
\]

The latter is not 0.0278. This is a **formal stationary candidate calculation**, not a verification theorem for an infinite-horizon recursive utility problem. Admissibility, integrability, parameter restrictions, and the selected utility solution still require justification. Those distinctions matter especially for recursive utility and cannot be settled by a small training residual.

**Required response:** Re-derive the aggregator, its sign/domain restrictions, the homothetic benchmark, and the verification conditions before retraining. Specify how the value-network output remains in the domain of the fractional powers. A typographical explanation must be supported by the actual implementation and regenerated evidence; it cannot be assumed.

### R7. Zero-centered residuals do not imply stability, and the convergence proof does not cover the implementation

**Locations:** [ECTA.tex, lines 660–724](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L660-L724); [lines 1145–1205](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L1145-L1205); [implementation and convergence, lines 1600–1875](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L1600-L1875).

Writing a learning target as zero does not make the residual independent of the current critic, policy, or rival policies. Even the scalar zero-target loss `a^2*x^2/2` has gradient-descent stability restriction `0<eta*a^2<2`. Sensitivity of the operator and the update Jacobian, not the printed target value, determines local stability. Minimizing a squared residual by Adam is not a Newton method: no inverse residual Jacobian is being applied.

The TD-loss calculation also has a direct sign error. For `L=delta^2/2`, the derivative is `delta*grad(delta)`, not `-delta*grad(delta)` as displayed. The analysis must distinguish full residual differentiation from semi-gradient TD with detached targets. Moreover, the recursive target adds an exponential discount to a continuation term while its aggregator already contains a discount component; a consistent time discretization is needed before making a stability comparison. The present derivation does not establish a structural impossibility for the baseline.

The asymptotic argument invokes two-timescale stochastic approximation. Its stated conditions include square-summable but nonsummable learning rates and an actor/critic step-size ratio tending to zero. The actual implementation instead uses constant-step Adam with learning rate `1e-4` and `omega=1`. A fixed large loss weight would not create an asymptotically vanishing step-size ratio either; it also changes both block gradients in the stated composite loss. Borkar's formulation [B4, Section 1] makes the step-size, noise, stability, and attracting-ODE assumptions explicit. Those assumptions need verification, not the phrase “standard conditions.”

Several subsequent implications are invalid. A stationary critic gradient does not imply zero policy-evaluation residual. A stationary point of coupled gradient dynamics does not imply a local Nash equilibrium. A local Nash equilibrium of a parameterized surrogate game does not by itself imply an optimal control policy. R1 prevents the first population-objective identification even before these additional gaps arise.

Finally, expected Hamiltonian ascent under an arbitrary state-sampling distribution is not automatically the policy gradient of lifetime utility from a specified initial state. Occupancy or adjoint weights, the recursive utility derivative, and any differentiation through trajectory sampling must be derived. The paper alternates between domain sampling and policy-generated trajectories, without specifying the distribution or stop-gradient convention needed for either interpretation. On-policy small residuals also do not certify accuracy in rarely visited or counterfactual states.

**Required response:** Analyze a fully specified update rule. State and verify the hypotheses of any asymptotic theorem, and distinguish it from finite-step Adam evidence. Report stability using actual runs, sensitivity to initialization, step sizes, residual conditioning, sampling distributions, and failed seeds. Neither a zero target nor a low average residual is a stability theorem.

### R8. The NDU application has unresolved well-posedness and economic-content problems

**Locations:** [ECTA.tex, lines 1230–1390](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L1230-L1390), `eq:ndu_u_sde`, `eq:ndu_hjb`, and `eq:ndu_foc_theta`.

The application declares a positive risk-aversion state but gives it additive Brownian dynamics `du=theta*dt+sigma_u*dZ`. No boundary mechanism prevents it from leaving the positive domain or approaching the singular point `u=1` of `c^(1-u)/(1-u)`. Bounded actor outputs constrain controls, not the state diffusion. A valid model needs a specified state space, boundary/viability mechanism, and utility definition on every reachable state.

The economic rationale for preference adjustment also contains an algebraic error. For the actual flow utility,

\[
\partial_u\frac{c^{1-u}}{1-u}
=\frac{c^{1-u}\{1-(1-u)\log c\}}{(1-u)^2}.
\]

For `c>1` and `u>1`, this is positive, not negative as the text's argument suggests. At `c=u=2`, it is approximately 0.84657. This does not prove that the full endogenous value derivative `V_u` must be positive; it proves that the reason offered for asserting `V_u<0` is incorrect. The sign of that derivative and the resulting adjustment policy require analysis of the complete model.

Endogenizing a parameter indexing utility functions also makes their relative cardinal levels consequential. Subtracting the usual normalization term to obtain a logarithmic limit at `u=1` changes the rewards for selecting the preference state; it is not an innocuous normalization of this endogenous-control problem. The paper needs an economically meaningful normalization and an account of consumption units before interpreting a desire to alter risk aversion as a behavioral discovery.

The interior FOCs assume suitable signs and concavity and must be reconciled with the actual bounded control set. The asserted cross-derivative sign underlying the hedging interpretation is not established. The formula `theta=V_u/k` does not by itself prove a comparative-static sign with respect to `k`, because `V_u` changes with `k`. The discounting notation also uses the evaluation time `t` inside an integral over `s`; the intended running-payoff convention must be made consistent with the HJB.

This application has two state variables, not a demonstrated high-dimensional state space. It is not evidence that the proposed economic mechanism is inaccessible to a well-designed two-dimensional numerical benchmark. Nor does variation of a policy with one structural parameter establish identification of that parameter in data with latent states and other unknown parameters. Identification needs a specified observation model and, for example, a suitable rank or injectivity argument for the chosen moments.

**Required response:** Make the preference-control problem well defined, justify its cardinal interpretation, check FOCs and state constraints, and validate against an independent two-dimensional solver. Separate numerical policy patterns, comparative-static theorems, and econometric identification. The endogenous-preference application can be retained, but it requires substantive economic foundations rather than assertions that a plausible-looking surface confirms them.

### R9. The time-inconsistency extension is not a derived sophisticated-agent equilibrium

**Locations:** [ECTA.tex, lines 1391–1478](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L1391-L1478); [inline supplement, lines 1901–2020](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L1901-L2020); [separate supp.tex, lines 65–160](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/supp.tex#L65-L160).

The main application and inline supplement maximize `beta*u(c)+V_X(rX-c)`. For CRRA utility this gives

\[
\beta c^{-\gamma}=V_X,
\qquad c=(\beta/V_X)^{1/\gamma}.
\]

Holding the continuation shadow price fixed, reducing `beta` reduces current consumption. This is the opposite local incentive to the claimed overweighting of present consumption. It is not a full equilibrium comparative-static result, because the shadow price can change; it is a diagnostic that the proposed preference distortion requires an actual derivation rather than a label. No continuous-time discount kernel, duration-of-the-present construction, or equilibrium deviation argument is supplied to resolve it. The continuation equation also omits the discount term needed for the stated exponential benchmark under its apparent interpretation.

The separate supplement is not merely a differently formatted copy. It writes a deviation term `sup_c {u(c)-u(c*)}` while keeping all dynamic effects evaluated at `c*`. With increasing utility, this selects the highest feasible consumption, or fails to attain a supremum, independently of the foregone wealth from consuming. It also lacks the stated present-bias parameter. Its performance loss is a lifetime integral, whereas the inline version uses a local distorted Hamiltonian. These are materially different models and algorithms.

A slowly updated target policy can be a numerical device; it does not establish subgame perfection. General continuous-time time-inconsistent control requires an equilibrium formulation and associated extended equations, as illustrated by Björk, Khapko, and Murgoci [B5]. That observation is not a demand to use one particular model, but to derive the equations of the model actually claimed.

**Required response:** Specify the economic objective for each temporal self, derive the limiting deviation condition, and reconcile both supplements with one authoritative implementation. Test the no-present-bias limit and independent one-shot deviations. Check whether the plotted columns are consumption levels or consumption–wealth ratios; the current labeling is not a substitute for that calculation.

### R10. The dynamic-game algorithm is not, as written, a Nash solver

**Locations:** [ECTA.tex, lines 1480–1580](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L1480-L1580); [inline game algorithm, lines 2021–end](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L2021); [supp.tex, lines 180–end](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/supp.tex#L180).

A unilateral gradient for player `i` is not the gradient of the sum of every player's objective with respect to player `i`'s parameters. The prose says rival policies are treated as fixed, but the pseudocode accumulates a global scalar loss and differentiates it with respect to all networks without specifying the required detachments. Cross-player terms survive under the literal computational graph. This distinction is essential, not an implementation detail that can be left implicit.

The basic economic error can be seen without any critic approximation. In a static two-firm Cournot problem with payoffs `u_i=q_i(1-q_i-q_j)`, the symmetric Nash quantity is `1/3` per firm. Maximizing the sum of profits instead admits the symmetric allocation `1/4` per firm. At that joint optimum, a firm's own marginal profit is `1/4`, so it wants to deviate. Joint minimization cannot generally be identified with the Nash condition. Explicit player-specific computational graphs could avoid this particular error, but would be a different, precisely specified algorithm requiring its own analysis.

Zero policy-evaluation residuals are also insufficient: they may value a non-equilibrium policy profile perfectly. The missing quantity is a unilateral best-response or Hamiltonian optimality gap. Symmetric weight initialization does not guarantee permutation-equivariant policies, uniqueness of a symmetric equilibrium, or convergence to that equilibrium. A stationary point need not be a best response, and a zero printed target does not remove rotational dynamics from a game.

The competitive-limit table requires further explanation. It sends the number of firms to infinity while retaining positive capital per firm and fixed market-demand primitives, hence unbounded aggregate output and zero price under the specified truncated demand. Maintaining positive capital entails investment/depreciation costs. This cannot simply be asserted to be the conventional competitive benchmark without market scaling and a best-response argument. The table also conflicts with its plotting data, as noted in R5.

**Required response:** Publish the player-specific derivative graph; certify unilateral deviations with a separate solver; report exploitability and multiple-initialization outcomes; and define the market-size normalization used in comparisons across firm counts. Verify low-dimensional games against an independent equilibrium computation before making high-dimensional MPNE claims.

### R11. The scalability experiment does not identify a high-dimensional advantage, and novelty remains unisolated

**Locations:** [ECTA.tex, related literature, lines 544–567](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L544-L567); [method comparison, lines 697–827](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L697-L827); [ASG benchmark, lines 997–1085](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L997-L1085).

The scaling model has additive utility across capital stocks, independent state transitions, and no stated cross-stock resource or control constraint. As written, it decomposes into one-dimensional problems:

\[
V(k_1,\ldots,k_d)=\sum_{i=1}^d v_i(k_i),
\]

with a diagonal Hessian. If the primitives are identical, a single one-dimensional solution can be reused. Forcing a sparse-grid method to solve the unreduced joint problem and then observing combinatorial cost does not establish that the economic problem is intrinsically hard in high dimension. The appropriate comparator first exploits the separability available to both methods.

The reported comparison also uses different hardware and different convergence definitions: neural loss stabilization versus solution of a projection system at a stated grid level. Hardware differences can be reported honestly, but they do not isolate an algorithmic scaling law. Fixed-accuracy runtime, memory, failure rate, and economically meaningful policy or welfare error need to be measured on the same problem and test domain. An unexplained “maximum Euler error” is not interchangeable with mean squared HJB residual or value error.

Per-iteration derivative cost is not total complexity at a fixed accuracy. Network size, sample count, optimizer iterations, covariance operations, conditioning, and their dependence on dimension and accuracy are absent from the asserted polynomial bound. No general escape from the curse of dimensionality follows from using a mesh-free representation.

The contribution also needs a closer comparison with existing neural PDE/control methods. DGM already trains mesh-free neural approximations using differential, boundary, and initial conditions, including HJB and free-boundary examples [B1]. The original Deep BSDE paper includes an HJB application [B2]. The potentially distinctive contribution here would be a validated actor-factorized constrained solver and its economic applications, not the bare use of neural residual minimization. A direct implementation comparison and ablation are necessary to isolate that contribution.

Finally, recursive dependence on `V` is a nonlinear zeroth-order term; it does not by itself make a PDE fully nonlinear in its highest derivatives. Likewise, the inability to write an analytic control rule does not itself define the semilinear/fully nonlinear boundary. The categorical table assigning NBO to constrained economics and Deep BSDE to smooth physics is not a defensible methodological classification.

**Required response:** Add separability-aware baselines and genuinely coupled problems with independently checkable solutions or certificates. Compare matched accuracy and resource budgets. State a precise novelty claim relative to neural HJB solvers, and demonstrate it through ablations of the actor, constraint treatment, recursive aggregator, and residual formulation. Do not present a two-state application or a reducible 50-stock model as sufficient evidence of general high-dimensional capability.

### R12. Unbiased trace estimation creates a biased squared-residual objective

**Locations:** [ECTA.tex, lines 712–827](https://github.com/TrillionniumFoundation/NBO/blob/bf049e302e9ed38303084e8da16b13717b052a70/ECTA.tex#L712-L827), `eq:hutchinson` and the exact-versus-stochastic Hessian discussion.

The discussion treats stochastic trace estimation mainly as additional gradient noise. Let `q_hat` be an unbiased estimator of the diffusion trace `q`. Squaring a residual containing that estimator gives

\[
\mathbb E(a-\widehat q/2)^2
=(a-q/2)^2+\tfrac14\operatorname{Var}(\widehat q).
\]

The variance depends on the learned derivatives, so this is generally a **different population objective**. Increasing the number of training steps at fixed probe count does not remove the extra term.

For an elementary demonstration, take `q_hat=h*z^2`, with a single standard Gaussian probe, and `a=1`. The true residual is minimized at `h=2`, while

\[
\mathbb E(1-hz^2/2)^2=1-h+3h^2/4
\]

is minimized at `h=2/3`. This does not mean stochastic Hessian methods cannot work. It means probe design, independent-product estimators, variance correction, or a growing probe budget must be analyzed rather than calling the squared objective unbiased.

The stated Gaussian variance formula also must be applied to the matrix actually probed. For a product `C D2V` that need not be symmetric, the quadratic form depends on its symmetric part; using a symmetric factorization gives a different weighted matrix. A formula for the unweighted Hessian is not a general formula for the diffusion-weighted trace. Dense covariance multiplication and network derivative cost must also be included in the computational accounting.

The claimed necessity of a probe count proportional to state dimension at all constraints is unproved. Not every active control bound creates a value-gradient discontinuity, as R4 already shows. The stated experiment in which noisy Hessians cause a policy to violate a box constraint is also inconsistent with the claim that the policy is always mapped into that box by its output activation, unless a different constraint or different implementation was used.

**Required response:** Analyze the expected training objective, not just the trace estimator. Report accuracy and bias against probe count and exact low-dimensional derivatives, specify the covariance/Hessian implementation, and reconcile feasibility claims with the actual policy architecture.

## 4. What a substantively reconsiderable submission would need

The following are evidentiary conditions, not promises that meeting them guarantees acceptance.

**First: mathematical coherence.** There must be one authoritative economic model and computational graph per application. Actor improvement, policy evaluation, parameter optimization, and equilibrium conditions must be distinguished. Boundary and terminal data must be enforced. The false global-minimizer theorem must be replaced by a correct statement supported by a proof that survives R1. Any viscosity-selection claim must survive a diagnostic of the type in R3.

**Second: correct analytical anchors.** Independently derive and verify the Merton and recursive-utility benchmarks before training. Check utility signs and domains, discount conventions, wealth homogeneity where applicable, and constraints. Report errors in value, policy, boundary data, and the maximized Hamiltonian separately. For games, add unilateral deviation gains rather than only policy-evaluation residuals.

**Third: a complete experiment trail.** A clean execution environment must reproduce the numerical tables and plots from configurations and seeds. Every plotted curve must identify its originating run. Constructed illustrations must not be presented as experiments. Include all attempted runs, stopping criteria, runtime and memory measurement procedures, and fixed held-out state distributions, including boundary and counterfactual regions.

**Fourth: evidence for the incremental contribution.** Use direct neural-PDE and separability-aware classical baselines at matched accuracy. Demonstrate a genuinely coupled high-dimensional case. For NDU, separate the economic novelty from solver novelty and from identification claims. For time inconsistency and games, derive the appropriate equilibrium system and validate against an independent small instance.

These requirements do not require deleting applications or suppressing the paper's ambition. They require each retained claim to have the mathematical and numerical support that its current presentation asserts but does not supply. Replacing “guaranteed” with “empirically robust” would not fix the false benchmark, invalid aggregator, or constructed experimental comparison.

## 5. Reproducible reviewer checks and their limits

The accompanying `verify_counterexamples.py` requires only Python 3.9 or later and the standard library. It produces `verification_results.json`:

```sh
python3 reviews/2026-09-15-econometrica/verify_counterexamples.py \
  --output /tmp/nbo-review-verification.json
```

For a checkout retaining the reviewed manuscript blobs, an additional source-integrity check is available:

```sh
python3 reviews/2026-09-15-econometrica/verify_counterexamples.py \
  --source-root . --output /tmp/nbo-review-verification-with-source.json
```

The default run was executed for this review and all **12 reviewer diagnostics** were reproduced. The committed JSON records that its manuscript inputs were transcribed from the pinned source, not loaded from a local checkout. The optional local-source mode was not run for the recorded result; it checks Git blob hashes and the two embedded constrained-policy data definitions when a matching checkout is supplied. The pinned source was read through the GitHub connector for this review.

The checks cover the finite-horizon and stationary composite-loss counterexamples, the small-residual wrong viscosity limit, Merton arithmetic, the constrained plot's source range, the recursive aggregator sign, the endogenous-CRRA derivative, the fixed-shadow-price present-bias margin, the Cournot distinction between joint and unilateral optimization, stochastic-trace objective bias, and the TD derivative sign. Successful execution validates these diagnostics; it does not mean that an NBO solver has passed twelve tests or that the author's experiments have been replicated.

The report does not infer that every neural residual method fails, that every reported number was deliberately constructed, or that the proposed economic agenda is unworthy. It identifies specific failures of the submission actually reviewed. The recommendation follows from those failures, not from a generic objection to machine learning in economics.

## 6. Primary literature consulted

These references support the methodological comparisons and definitions indicated above. The counterexamples and arithmetic in this report are derived explicitly rather than attributed to these papers.

**[B1]** Sirignano, J., and K. Spiliopoulos (2018), *DGM: A Deep Learning Algorithm for Solving Partial Differential Equations*. Journal of Computational Physics. [Primary preprint, arXiv:1708.07469v5](https://arxiv.org/abs/1708.07469v5). Consulted for the mesh-free differential/boundary residual approach and stated HJB/free-boundary applications.

**[B2]** Han, J., A. Jentzen, and W. E (2018), *Solving High-Dimensional Partial Differential Equations Using Deep Learning*. Proceedings of the National Academy of Sciences, 115(34), 8505–8510. [Primary preprint, arXiv:1707.02568v3](https://arxiv.org/abs/1707.02568v3). Consulted for the original BSDE formulation and HJB application, not for a blanket comparison of all subsequent solvers.

**[B3]** Herdegen, M., D. Hobson, and J. Jerome (2021), *The Infinite Horizon Investment-Consumption Problem for Epstein–Zin Stochastic Differential Utility*. [Primary preprint, arXiv:2107.06593v1](https://arxiv.org/html/2107.06593v1), especially Section 4 and equation (4.3). Its parameter restrictions and distinctions between formulations are important; this report does not claim its verification theorem applies to the manuscript's numerical parameters.

**[B4]** Borkar, V. S. (2024 preprint), *Stochastic Approximation with Two Time Scales: The General Case*. [Primary text, arXiv:2412.19872v1](https://arxiv.org/html/2412.19872v1), especially Section 1. Consulted for explicit step-size, noise, boundedness, and ODE-attractor conditions, not as a convergence certificate for constant-step Adam.

**[B5]** Björk, T., M. Khapko, and A. Murgoci (2016 preprint), *Time Inconsistent Stochastic Control in Continuous Time: Theory and Examples*. [Primary preprint, arXiv:1612.03650v1](https://arxiv.org/abs/1612.03650v1). Consulted for the equilibrium/extended-HJB framework, not to substitute a different preference model for the one the author needs to specify.

---

**Bottom line:** The present paper cannot support an Econometrica-level methodological claim because the proposed objective is wrong in an elementary admissible case and the purported validation does not establish numerical correctness. The most productive next step is not additional rhetorical defense of a zero-centered target; it is a corrected algorithm, a valid verification argument, and an auditable experimental record.
