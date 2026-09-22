# Response to the R14 referee report

**Paper:** Neural Bellman Operators  
**Revision:** R16, September 23, 2026  
**Review input:** `bb09ac177fc766aea8aba26cb6a40b8aff68528c`, `reviews/2026-09-22-econometrica-r14/referee_report.md`  
**Canonical manuscript:** `ECTA_R16.tex` / `ECTA_R16.pdf`  
**Canonical supplement:** `SUPP_R16.tex` / `SUPP_R16.pdf`

We thank the referee for distinguishing correctness of verification from success of a numerical solver. This revision retains the neural numerical-method objective and the original economic problem. It adds mathematical constructions and executed experiments, rather than assigning the sharp time-control result to a neural policy or rewriting an unmet numerical target as a successful test. No preceding manuscript, proof, empirical comparison, adverse result, or review has been deleted.

The new central mathematical finding is that the unchanged economy has a strictly positive continuation-value jump at the upper wealth boundary. A fully hard-Dirichlet continuous neural critic is therefore inconsistent with vanishing uniform positive Bellman residual on that domain. The correction is a signed, accessibility-weighted verification theorem and an admissible neural architecture whose trace budget is exactly zero. This is not a change of stopping contract or a restriction of the controls used in the upper comparison. The current nonlinear residual certificates nevertheless remain above the requested tolerance. The accurate neural result added in this revision belongs to a separately defined coupled inventory economy, not to the nonlinear flagship model.

## General and scientific findings

### F0 and Gate A — Immutable, materialized review object
The new branch is based on the complete R14 review commit, not on an incomplete staged R15 source delivery. The R15 branch is left unchanged. Both R16 documents, readable sources, new implementations, all retained numerical objects, exact envelopes, compiler logs, and a checksum manifest are materialized in the new branch. The publication receipt distinguishes source and result commits from document compilation and later metadata. Source transport files are removed before publication; they are not the review artifact. `R16_REVIEW.md` is the single review entry point.

### F1 — Successful original-economy neural solution
The revision implements a substantive boundary correction and expands the full-horizon experiment to ten independent seeds, two widths, and twenty prescribed checkpoints. Every checkpoint is independently certified over the complete original state-time cylinder, using the original continuous control maximum, and every target miss is retained. The accessible-face architecture makes the trace contribution exactly zero by proof, rather than a small empirical boundary loss. The first final checkpoint is also re-certified on a finer complete cover.

**Numerical status:** the nonlinear full-horizon certificates still do not attain 0.01. Removing the trace inconsistency does not eliminate the residual or interval-overestimation terms. The main table, complete cell records, signed/unsigned decomposition, and all-face ablation make that distinction explicit. We do not call this original-economy accuracy gate closed. See main sections “Stopping accessibility and the neural approximation space” and “Full-horizon neural and classical experiments”; `results/neural/`.

### F2 — Identity of the accurate method
The neural objective and paper title are retained. The original-economy time-control/dual certificate remains explicitly non-neural. New neural accuracy evidence is supplied by ten freshly trained gain networks, with both checkpoints verified in a coupled inventory diffusion. The gain functions are trained from differential Riccati residuals, not optimal-value labels; a state-global performance-difference theorem certifies their actual continuous-time feedback. Every final checkpoint meets the declared 0.001 **per-coordinate** target in that model. This does not establish original-economy neural accuracy or superiority over a structure-aware Riccati solver. See “A coupled high-dimensional inventory economy”; `results/inventory/`.

### F3 — State-time significance
The new original-economy certificates cover the entire state-time cylinder, include later initial times through the signed residual theorem, and store complete cellwise evidence rather than extrapolating from a tiny initial-state rectangle. Their bounds are valid but not economically sharp. The inventory proof covers unbounded state dynamics and all initial states with mean squared inventory at most one, and its feedback is defined over the full time horizon. The original small initial-state/price theorem is preserved and is not redescribed as a broad accurate feedback surface. A sharp original-economy state-time accuracy surface remains unestablished.

### F4 — Same-problem classical baselines
Two distinct implementations are added: a positive-weight controlled Markov-chain approximation and a semi-Lagrangian weak Euler approximation. Both solve the same unchanged economy with its original utility, discount, first-exit fee, and terminal settlement. Three refinements of each method are retained. Their bilinearly interpolated state-dependent policies are certified as continuous-time controls using the same original-control upper oracle and a protocol-fixed common critic. Discrete values are stored only as diagnostics. Generation time, verification time, policy arrays, grid specifications, action grids, and memory records are included.

**Comparison status:** none of the six policies achieves 0.01 under the present common witness, so the table is not a matched-0.01 efficiency frontier. These are transparent implementations, not a claim to the strongest possible classical tuning. This qualification prevents a loose neural witness from producing a spurious superiority claim. See the state-space subsection and `results/baselines/`.

### F5 — Convergence and accuracy versus work
A quantitative certified policy-iteration theorem now gives

`E[n+1] <= q E[n] + 2 q epsilon[n]/(1-q)^2 + eta[n]/(1-q)`.

Its hypotheses are complete evaluation and improvement defects. The proof explicitly separates finite Bellman convergence from continuous-time discretization/transfer errors. Geometric defect schedules yield an explicit convergence rate, but the neural optimizer is not assumed to attain those schedules. The contraction ingredients are identified as classical.

The experiments distinguish changed training budget, changed policy discretization, and fixed-object enclosure refinement. The inventory experiment supplies a genuine trained-object accuracy sequence with all seeds; the nonlinear experiment records failures at 0.01, 0.005, 0.0025, and 0.001. The old fixed-dual 16/32/64-slab floor is retained. We do not claim that price-node or quadrature refinement alone removes that floor, nor that an original-economy vanishing-error work law has been demonstrated.

### F6 — High-dimensional dynamic certification
A coupled 4-, 8-, 16-, 32-, 64-, and 128-state inventory economy is added. Its drift and holding cost contain a nonzero mean-field coupling. The actual neural feedback controls the evolving state, not an action oracle at frozen jets. A quadratic performance-difference identity and a Lyapunov second-moment inequality give a complete state-global certificate. The time-enclosure cost avoids a state tensor grid because the model has two invariant modes. Applying the policy requires linear work in dimension.

The structure-aware classical reduction is reported explicitly. One gain pair is reused across dimensions and is not counted as six independent trainings. Both total and per-coordinate losses are stored. The result does not imply dimension-free certification of a generic nonlinear HJB equation; the original nonlinear verifier still uses a rectangular cover.

### F7 — Fresh end-to-end generation
`fresh_price_library.py` begins with model constants, deterministic policy/dual initializations, and the endpoint prices 0.5 and 8. It reads no inherited policy or dual-pilot file and no historical intermediate node selection. A predeclared exact-envelope rule adaptively selects subsequent nodes and terminates only at the verified tolerance or the node cap. The completed run rebuilds a full price-uniform certificate below 0.01. All optimizer attempts, generated policies, fitted witnesses, intermediate node additions, final exact breakpoints, and resources are retained. The single clean-checkout command runs this together with the other new experiments. Reusing a published algorithm is distinguished from reusing historical fitted inputs.

### F8 — Neural design study
The original model now has ten seeds, two widths, two materially larger retained budgets, an accessibility-aware boundary architecture, a boundary-layer sampling mixture, a protocol-fixed architecture ablation, and a fixed-object cover refinement. All twenty checkpoints are certified; none is selected after seeing a desired conclusion. The same records include individual seed training and verification resources.

The design study does not exhaust changes in depth, learning rate, actor/critic ratio, or adaptive residual-based sampling. The boundary-layer mixture is fixed, not falsely described as an adaptive algorithm. The revision establishes what these prescribed configurations attain and does not generalize their failures to the entire NBO concept.

### F9 — Established rigorous arithmetic
The decisive eighteen-node historical library is re-evaluated in full with MPFR-directed basic and elementary arithmetic at 128 bits, including directed conversion to binary64 endpoints. All policy lower intervals, dual upper values, expenditure intervals, and the exact final continuum envelope are recomputed. The final envelope remains below 0.01. This is not a three-point high-precision diagnostic.

The independent arithmetic implementation shares the original analytic decomposition, rational Gauss-root construction, derivative remainder lemmas, and stopping inequalities. That shared mathematical trusted base is disclosed. The code includes 450 exact-rational arithmetic regression checks, but no test suite is called a formal proof. The fresh model-generated library is separately certified with the rational--Taylor arithmetic and is not relabeled as an MPFR result. See `replication/mpfr_bridge.c`, `mpfr_interval.py`, `mpfr_library.py`, and `results/mpfr_library/`.

### F10 — Economic normalization
The paper defines an externally financed proportional consumption-top-up experiment while holding preference, wealth, adjustment cost, and stopping paths fixed. A marginal-utility bound and a rigorous discounted alive-time lower bound convert the fresh price-uniform policy loss into a sufficient top-up of approximately one percent. The exact computation is in `results/foundation_checks.json` and the bound is rounded upward in the paper.

This is a scale-normalized in-kind welfare comparison, not a budget-feasible wealth equivalent, a change to the original action cap, or empirical calibration. It is invariant to common positive rescaling of the whole welfare criterion; arbitrary additive shifts are not claimed innocuous when stopping time varies. The previous strict-loss and relative-resolution counterfactual diagnostics are retained.

### F11 — Methodological contribution
The new mathematical content includes a proved stopping-trace inconsistency in the unchanged economic model, its constructive resolution by signed policy-specific accessibility, the resulting exactly zero trace budget for an executable neural architecture, a complete state-global quadratic neural policy certificate, and explicit certified policy-iteration error accounting. Full proofs appear in the appendix. Classical verification and contraction ingredients are acknowledged rather than presented as newly discovered identities. The finite Bellman theorem is not a proof of Adam convergence; the original nonlinear solver's high-accuracy numerical gate remains distinct.

### F12 — Mathematical policy versus deployment
The new certificates concern real-valued network functions with exact dyadic stored weights and a specified bounded head-output perturbation. For the portfolio, this perturbation must precede the wealth-distance factor. The paper does not certify an undocumented machine tanh error, simulator, or final additive portfolio error. The classical transferred policies are precisely defined bilinear state heads, piecewise constant in time. The deployment claim is not silently enlarged beyond these contracts.

### F13 — Economic scope
The coupled inventory-adjustment economy adds a recognizable higher-dimensional dynamic application with drift-coupled aggregate and idiosyncratic inventory modes, independent shocks, holding costs, and adjustment costs. Its state dimension genuinely grows to 128 and its neural feedback is globally certified. It remains structured and uncalibrated; the classical two-mode reduction is available to both methods. This addition does not supply an empirical application or establish neural advantage on a generic high-dimensional economy.

## Technical comments

| Comment | Revision and remaining distinction |
|---|---|
| T1: verification versus convergence | Separate signed verification and conditional certified policy-iteration theorems, with distinct hypotheses and complete proofs. |
| T2: conservatism decomposition | Every original neural cell/slab retains signed upper/policy residuals, unsigned residual budget, action gap, output contract, and zero trace budget. Fixed-network refinement is separate. The exact true residual and exact wrapping excess remain unknown, not estimated as proof quantities. |
| T3: hard boundaries | A strict trace-jump proof explains why hard equality at every face is inconsistent. The accessible-face architecture and all-face finite-budget ablation are both executed and retained. |
| T4: node selection | Endpoint initialization, exact worst-breakpoint selection, 1/1024 rounding, duplicate fallback, tolerance, and node cap are predeclared. All generated nodes retained. |
| T5: small state rectangle | The old rectangle remains explicitly initial-state-indexed and small. It is not relabeled as broad accurate feedback. |
| T6: specialized dual | Time-control/dual generation and audit remain separately identified, including resource costs and model-specific premises. |
| T7: policy differences | Inventory residuals give explicit gain-error bounds; stored policies define all original-economy action ranges. Value regret is not used to infer an unproved optimal-control error bound. |
| T8: coefficient transport | The old 23.53-scale transport result is retained with its original limitations. No new sharp nonlinear robustness claim is made. |
| T9: upper-bound frontier | The unchanged-dual floor is retained and identified. New policy, node, and cover refinements are not misreported as relaxation convergence. |
| T10: high precision | The historical point cross-check remains diagnostic. The new complete MPFR node calculation is separately identified. |
| T11: adverse history | The clipped-feedback comparator, unstable seed orderings, unsuccessful neural runs, and all old sources are preserved. |
| T12: exact endpoints | All new displayed bound decimals round upward from retained endpoints; final price envelopes also store exact rational fractions and breakpoints. |

## Review-gate summary

Materialized review identity, a full established-arithmetic node audit, fresh model-to-continuum generation, and a precise welfare interpretation are supplied. A successful, state-global neural certificate is supplied for the structured coupled inventory model. The original nonlinear full-horizon neural 0.01 gate, a matched-accuracy nonlinear neural/classical frontier, and an empirical higher-dimensional application are **not** claimed complete. The revision reports substantive executed progress without replacing those scientific questions with editorial relabeling.
