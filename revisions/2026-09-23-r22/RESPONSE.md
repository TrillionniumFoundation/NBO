# Response to the final R21 Econometrica referee report

We thank the referee for separating the now-correct local proof chain from the unresolved methodological questions. This revision does not replace the full-state 0.01 objective by a regional objective and does not suppress the direct stochastic comparator. It adds a prospective crossed experiment, a nonsynchronized pair-moment theorem, actual rejection and recovery executions, and a new complete-domain current-state witness refinement. The main manuscript, technical supplement, executable sources, raw failed proposals, and result manifests are materialized together.

## R21F-F1: identity of the accurate object

We keep the original title and global objective. The main introduction and global-results section now distinguish three objects explicitly: a time-input neural candidate generator, its exact model-assisted regional policy, and a current-state actor/witness whose inputs are (t,u,x). The last object is actually refined and independently checked on all 1,024 original-domain cells. Its certificate improves from 7.2783190635 to 7.2405032566; this is not a claim that it attains 0.01. The accurate regional result remains correctly identified as a contextual mixture, not as a globally accurate learned state map. The manuscript therefore supplies new current-state execution while retaining the outstanding global accuracy requirement.

## R21F-F2: optimizer and initialization confounding

The new primary design crosses neural/direct parameterizations with Adam/L-BFGS-B. At every seed/vertex block the direct array is the exact raw output of the initialized neural network, and delivered initial b, s, theta, approximate value, and budget coincide exactly. Both optimizers receive the same initial parameter state within each representation. All four cells use a 400-function/gradient-call cap, with accepted L-BFGS iterates distinguished from line-search trials. The complete 48-configuration record is retained. We characterize the result as a parameterization effect conditional on optimizer, not as an effect of hidden layers isolated from all changes in parameter geometry.

## R21F-F3: the adverse direct frontier

The adverse historical result remains in the main paper. The new crossed experiment changes the evidence: under Adam and the common gradient cap, all three neural mixtures have a certified uniform payoff advantage over the corresponding direct-Adam mixture. The smallest proven advantage is greater than 0.003112 on the whole rectangle, not merely at its vertices. The pair-moment theorem proves this comparison without an optimal-value upper. Direct L-BFGS-B nevertheless remains the stronger overall regional configuration, with a uniform regret bound about 0.00283871 and fewer objective calls. We do not promote an optimizer-conditional advantage into unconditional neural superiority.

## R21F-F4: synchronized initialization

The new theorem removes equality of slopes and preference drifts. It uses the weighted-variance identity, six certified pairwise consumption moments per slab, an absolute Hessian cover, Cauchy--Schwarz on the joint time-probability measure, and explicit stopping and Gaussian-tail allowances. The three ensembles use independent corner seeds. Every neural-Adam ensemble has certified uniform initial-to-final payoff improvement exceeding 0.026111. The earlier general range certificate also passes for these ensembles and is retained. Thus neither the theorem nor its new successful execution requires synchronized initialization.

## R21F-F5: state interpolation and scaling

The manuscript does not call expert interpolation learned state generalization. It now gives a simplex extension with d+1 active experts, shared-vertex storage, explicit (n+1)^d vertex and d! n^d simplex counts, conditional-price query cost, and an adaptive interval-cover termination bound under a stated strict margin and uniform-consistency assumption. The complexity result quantifies, rather than conceals, the worst-case dimension dependence. It applies to mixtures only when their affine admissibility and concavity conditions hold; it does not mix starting times without a theorem. A separate current-state execution and full-domain certificate are provided, but broad accurate learned generalization remains a further requirement.

## R21F-F6: dependence on exact financial replication

The self-financing decoder remains an essential and explicitly model-specific component of the regional calculation. We add a constructive residual-correction cone for an arbitrary controlled diffusion: interval-enclosed generator inequalities and stopping traces produce upper and policy-specific lower witnesses through a finite conic/linear feasibility problem. This argument does not require a martingale representation or complete markets. Its time-slab member is executed on the full-state residual certificate. We do not claim a new sharp incomplete-market experiment; the general mathematical mechanism and the executed complete-market application are distinguished.

## R21F-F7: essential non-neural upper comparison

The algorithmic system is now explicitly defined as proposal generation, feasibility/compilation, policy-specific value checking, unrestricted upper comparison, and acceptance control. The inherited non-neural dual is charged as an essential shared input to regret certification, not described as a neural output. It is unnecessary for the newly certified neural-Adam versus direct-Adam payoff ordering, but remains necessary for the reported regional regret bounds. Historical upper-library costs remain in the main paper and ledger.

## R21F-F8: the full-domain continuation witness

We carry out a new warm-start joint current-state actor/witness refinement with 400 L-BFGS-B gradient calls and a separate MPFR complete-domain audit. No original action is removed and no cell is skipped. The comparable bound decreases from 7.2783190635 to 7.2405032566. A discounted suffix theorem also certifies every starting time rather than using an undiscounted upper sum. This is a modest genuine refinement, not closure of the sharp continuation-witness requirement. We preserve the inaccessible-face/one-sided trace analysis and do not force the invalid liquidation trace onto an inaccessible continuation face.

## R21F-F9: price transport

The earlier price transport is retained as a fixed-policy, a posteriori sensitivity calculation on its stated price interval. It is not used to establish the new optimizer-conditional payoff ordering or to enlarge the current-state accuracy claim. The main discussion explicitly distinguishes changing price from changing state dimensions and starting time.

## R21F-F10: economic meaning of additional wealth

The current narrative uses 'sufficient re-budgeted wealth increment.' The counterfactual increases initial wealth, keeps learned slope and preference-drift shapes, recomputes the consumption intercept/budget offset, and checks the newly financed stream. It is not evaluation of an unchanged policy map, not a minimum compensating variation, and not a structural welfare estimate. The earlier margin is retained with its narrow scope. Original historical wording remains identifiable in the preserved archival exposition rather than overriding the new interpretation.

## R21F-F11: rejection, restoration, stagnation, and recovery

The predeclared stress test accepts three of eight blocks and rejects five, with exact restoration of network, optimizer, and all recorded random-number states. It also exposes deterministic repetition: exact rollback plus an unchanged deterministic proposal repeats the same failure. A separately specified recovery run restores the proposal state first, checks its hash, and then halves the learning rate in an external supervisory controller. That run accepts six blocks, rejects two, and resumes accepted improvement after the first rejection. All candidates and costs are retained. No-op and corruption tests are labeled fault injection, not naturally observed optimization evidence.

## R21F-F12: robustness and independent units

The new design has three independent ensembles and twelve independent vertex initializations, each crossed with four optimizer/representation configurations. Optimizer sensitivity and a high-learning-rate stress regime are actually executed. We retain the earlier five ensembles as five, not twenty, independent dictionaries. The paper does not claim a broad architecture or learning-rate robustness study, and does not combine the selected post-observation repair block with the prospective ensembles to inflate the number of independent units.

## R21F-T1: proof-to-code dependencies

The technical supplement now has a compact table mapping every headline claim to its theorem or analytic assumption, exact script/function, result path, arithmetic backend, and proof-critical or diagnostic status. Pair-moment complex-domain constants are separately proved and checked. A provenance manifest is retained but is no longer offered as a substitute for the proof-dependency table.

## R21F-T2: arithmetic redundancy

The binary64 and MPFR paths share economic and stopping mathematics. The manuscript continues to call replay arithmetic redundancy, not mathematical independence. State hashes, pointwise derivative diagnostics, and ordinary-float timing checks are likewise not called proofs of the economic result.

## R21F-T3: function and gradient accounting

Every configuration records function and gradient evaluations, accepted optimizer iterations, extra line-search calls, reporting forwards, checker calls, parameter dimension, generation seconds, and checking seconds. Primary Adam runs use 400 gradient calls per expert. L-BFGS-B may converge before the cap; on cap exhaustion the last accepted iterate is restored. We define the line-search counter explicitly and do not equate iterations across optimizers. Shared initial checks and historical dual costs are identified separately.

## R21F-T4: matched delivered initial policy

All twelve blocks pass exact equality of the delivered initial policy fields, not merely equality of seed labels. Neural and direct optimizers start from their matched state copies. The comparison also retains independently varying corners, so matching within a block does not reintroduce synchronization across corners.

## R21F-T5: terminology of the older comparison

The current main narrative calls the R20/R21 neural-Adam versus direct-L-BFGS-B result a matched delivered-policy-class end-to-end baseline. It does not call it a causal representation ablation. Historical sources are preserved without changing their data; the revised main copy supplies the corrected interpretation.

## R21F-T6: online implementation cost

We distinguish compilation, pricing, and verification. Compiled regional policies need no online neural forward call but do need conditional-price and derivative integrations. We state the node, active-expert, coefficient-memory, and whole-library scaling, and execute a 4/8/16/32-expert ordinary-float pricing timing diagnostic. Duplicate experts in that diagnostic are not additional economic evidence. The timing uses ordinary quadrature and reserve midpoints and therefore does not certify online numerical price or hedge errors; the mathematical deployment theorem concerns exact price-defined objects.

## R21F-T7: timing of specification and analysis

Three separate protocol commits identify the prospective crossed/stress design, the exploratory full-state refinement, and the post-observation root/recovery diagnostics. The pair-moment theorem and continuum comparisons are labeled a posteriori certified properties of frozen policies. R20 preregistration remains historical and is not retroactively applied to these analyses.

## Additional defect found and corrected during this revision

One local-preflight neural L-BFGS-B run of the registered design terminates with the original fixed budget-root bracket outside the true bracket. Its exact reserve enclosure falls below 0.5, and the checker correctly rejects it. We retain that raw candidate, its parameter state, and its failed check as a regression fixture. A root-safe implementation centers the redundant common intercept, expands the bracket, and uses80 bisections before the original implicit-gradient correction. The repair preserves the economic objective and independent certifier, and passes a common-intercept-shift diagnostic. Re-budgeting the failed frozen parameters yields a feasible but inferior policy. The selected four-cell diagnostic is reported in full, not substituted for the failed primary outcome.

## Status of the new-round requests

N1 is executed with matched initial policies and crossed optimizers. N3 is supplied by a general theorem and independent-corner execution. N4 has a conditional complexity theorem and actual online-cost accounting; it is not evidence of a certified high-dimensional global cover. N2 has an actual current-state refinement and complete-domain certificate, but not a sharp full-state policy-value separation. N5 has a rigorously certified optimizer-conditional regional advantage, while the strongest direct configuration still dominates overall. N6 has a modest independently checked witness refinement and a constructive correction formulation, not the full0.01 solution. We do not take N7 as a reason to abandon the original research objective or delete the difficult earlier evidence.
