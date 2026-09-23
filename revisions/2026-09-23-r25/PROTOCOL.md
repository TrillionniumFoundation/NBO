# R25 prospective protocol

Date: 2026-09-23. Repository: TrillionniumFoundation/NBO.
Base: latest R24 review 0eb0400ae311333fb77826ef9e2f067718926ae8, reviewing manuscript 14ce582e188f437cc8d99f310edd4f06515936a4.
This protocol is recorded after reading the report, R24 sources, and historical proof/checker dependencies, and before R25 scientific execution. Development uses a new branch; the original model, title, author attribution, full-domain 0.01 target, and all historical files are retained. The stale root revision index will be updated with its prior content preserved.

## A. Expanded calibration

Original central state (0,2,1.25), adjustment price k=2, inherited 16-slab financed policy family and unchanged directed stopped-payoff checker. Tuning seeds 25001 and 25002. Each of neural, direct, diagonal, tangent, whitening Adam and a new moving-transport direct arm receives rates {0.005,0.02,0.08,0.32,1.28,5.12,20.48}, 200 objective/gradient calls, and proposal orders (8,16). Select the highest mean certified endpoint payoff lower bound; any failed endpoint makes that rate ineligible. Ties within 1e-10 use the smaller rate. Preserve every trial. Report whether the selected rate is strictly interior with a worse larger rate, on a certified plateau, or censored; do not call a boundary choice bracketed. No held-out retuning.

## B. Moving historical output transport

The new arm has 47 economic quotient coordinates and an explicitly charged 355-parameter chart carrier. At each step recompute the quotient Jacobian of the carrier. Pull the current direct-output gradient back through this Jacobian; maintain parameter-space Adam first and second moments; push the resulting direction forward through the current Jacobian. Add an isotropic quotient regularizer 1e-6 and cap the norm of the combined output displacement at 0.5, scaling the carrier displacement by the same factor. Update the economic quotient linearly and the carrier in parameter space. This preserves historical Jacobian/moment transport, but intentionally omits the finite-step nonlinear output remainder. It is not an autonomous 47-memory-coordinate optimizer; all carrier differentiation and storage costs must be reported. The isotropic term and step cap are fixed before evaluation.

## C. Held-out factorial

Seeds 25101 and 25102, orders (8,16) and (12,24), the six selected first-order arms plus neural/direct L-BFGS-B. Cap 400 calls and retain checkpoints 25,50,100,200,400. L-BFGS-B: maxls=40, ftol=1e-13, gtol=1e-8; checkpoints use last accepted iterates, explicitly carrying forward early convergence. All endpoints and checkpoints are certified with the unchanged checker. Record pairwise payoff intervals, regret, calls, preprocessing, geometry, generation, certification, and total elapsed costs. Earlier R24 outcomes remain historical, not pooled replications.

## D. Online-coupled acceptance

At the coarse rule and held-out seeds, execute neural Adam, direct Adam, and moving transport in four successive 100-call blocks. Certify synchronously after each block. Accept only when the candidate payoff lower bound exceeds the incumbent upper bound. On rejection restore economic coordinates, neural/carrier parameters and all optimizer moments to the incumbent snapshot; halve the rate for the next block. Record the actual interleaved wall clock, candidate and restored-state hashes, all decisions, and all costs. Compare against the uncoupled four-block trajectory; do not infer convergence solely from monotone deployment.

## E. Stronger stochastic reference and restart verification

Add an explicitly separate manufactured investment/productivity economy with two independent Brownian shocks, an unspanned productivity factor, first-exit/terminal stopping, and a bounded current-state investment action. Construct a smooth independently known value and a quadratic Hamiltonian completion, so policy regret is an exact stopped integral of squared action error. Train a current-state neural actor on a declared deterministic tensor rule and retain a direct approximation control. Verify the entire closed state-time box by directed arithmetic, including all stopping faces, rather than certify only sampled starts. Report uniform error, actual cover size, runtime and selected restart evaluations. This is a nonreplicable stochastic verification benchmark, not a replacement for or solution of the original consumption-portfolio economy. Its complete coefficients, construction, training rule and verification settings will be recorded before its execution.

## F. Mathematical repair and error accounting

Prove the moving-transport identity, an online verified-improvement/termination statement with explicit assumptions, and the stronger stochastic reference's exact regret identity. Correct the R24 perturbation theorem by bounding both exact and numerical derivative factors explicitly. Investigate an instantiated derivative enclosure or derivative-free certified secant alternative using the inherited stopped checker. Any original-stopped-gradient component that is not rigorously enclosed remains explicitly unresolved; two-rule differences must not be called gradient certificates. Preserve the original full-state result 7.241462443133396 unless a new valid certificate improves it; no auxiliary-model number substitutes for this target.

## G. Publication

Use retained Econometrica econsocart class and original author/title. Main manuscript: economic question, model, assumptions, method, theorems, evidence and interpretation. Put historical derivations and full trial/checkpoint ledgers in the technical supplement without deleting their files. Supply ECTA_R25, SUPP_R25, RESPONSE_R25, a finding-by-finding response covering R24-F1--F12, T1--T6 and N1--N8, executable replication, frozen results, source/data hashes, a current root index and a separate referee-copy branch. Record failures and scientific nonclosure without downgrading the original research objective or claiming evidence not obtained.
