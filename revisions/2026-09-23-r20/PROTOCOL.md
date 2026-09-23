# R20 pre-execution confirmatory protocol

Date: 2026-09-23. Latest referee input: 074849b9aad1812b59e25e1d3833383ed11aa401. Inherited R19 publication: 01aa2b410dca6f08489f68ada21fdf4b997944f7. No old manuscript, scientific result, or review file is replaced.

## Exploratory work explicitly separated

Seed 20000 was used only for a pilot on the center and four vertices of K=[1.98,2.02] x [1.24,1.26]. A 1-16-16-3 tanh network, 16 time slabs, and 1000 Adam updates produced a promising stochastic-consumption policy. A pilot directed check gave a center regret bound near 0.001962 and a nonzero initial portfolio near 0.179. This motivated the following design. Pilot observations are not confirmatory seeds and are not silently pooled with them.

## Frozen confirmatory design

Five new seeds 20100,20101,20102,20103,20104; four initial-state vertices (1.98,1.24), (1.98,1.26), (2.02,1.24), (2.02,1.26); k=2, t=0. Each seed defines a four-expert mixture. Each expert starts from fresh random neural weights, not inherited actor or value labels. The network has widths 1-16-16-3 with tanh hidden layers. It outputs 16 logistic-consumption intercepts/slopes and deterministic preference drifts. Consumption is c=.5+.3 sigmoid(b-s log Y), slope s in [.1,6.5], preference drift theta in [0,.2]. Y is the observable traded Brownian factor dY=.02Y dt-.3Y dW_x with Y_0=1. A risk-neutral pricing decoder finances consumption with terminal reserve at least .5 and defines the portfolio by exact self-financing replication. The original economy, stopping rule, full admissible action set and global 0.01 objective are not changed.

Adam step size .005, 1000 proposal updates, retained work levels 0/100/400/1000. A budget offset is computed inside each proposal objective with implicit differentiation. At each retained level, the frozen dyadic policy is evaluated by a separate directed payoff checker. An actor is accepted only when its policy-value lower bound exceeds the previous accepted policy-value upper bound, before the next proposal update; otherwise both network and optimizer return to the incumbent. Every proposal, failure, acceptance and cost is retained. No certificate-only critic update is substituted for this test.

The checker prices the consumption stream and encloses actual stopped expected utility. It uses rationally isolated Gauss nodes, explicit complex-disc quadrature remainders, an order-12 conditional Gaussian Taylor remainder, normal tails, and stopping corrections. The production arithmetic uses rational-Taylor outward binary64 intervals; all 20 final expert policies are additionally checked by independent MPFR-directed arithmetic. Arithmetic independence is not an independent proof of the common model derivations.

The original-economy dual upper bound is the inherited unrestricted dual at two bracketing k nodes, interpolated by convexity. It is not fitted to new neural values. Four-corner concavity and a self-financing mixture theorem will transfer the vertex inequalities to every initial state in K. The unchanged target is 0.01. The experiment will also report hits or misses at 0.005 and 0.002 without redefining the target. K-uniform accuracy is not whole-domain accuracy.

## Comparators and attribution

Reexecute fresh deterministic SLSQP time-control transcriptions at 16/32/64 slabs. Also optimize the same 16-slab stochastic logistic family without hidden neural layers using L-BFGS-B, with retained work levels 0/10/50/200 and convergence recorded if it occurs early. Give the stochastic comparator the identical four-vertex checker, upper bound and continuous-state mixture transfer. Report generation, verification and total work separately; charge inherited shared-upper cost explicitly. Failed target hits are retained. Do not claim a neural speedup unless measured.

Evaluate the fixed deterministic policies with policy-specific upper enclosures on K and compare them with the new stochastic neural mixture lower bounds. A claim of stochastic policy improvement must use independently ordered payoff bounds, not actor ranges or a changing critic. Any comparison is with the named policies/classes, not all conventional solvers.

## Publication and remaining scope

Retain R18 and R19 scientific content and adverse results. Add full self-financing, admissibility, conditional quadrature and continuum-mixture proofs, actual generated evidence, scripts, and a point-by-point response to F1-F11 and T1-T10. Build main manuscript, supplement and response using the unchanged econsocart class. Check preservation hashes and compiled references. Publish only on the new R20 revision branch. Full-domain accuracy, a globally sharp continuation upper witness and a matched global MC/SL frontier are not declared solved by a K-domain calculation.
