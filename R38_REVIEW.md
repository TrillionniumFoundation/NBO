# R38 review package — completed scientific revision

**Article:** Certified Bellman Operators for Costly Policy Revision  
**Repository:** TrillionniumFoundation/NBO  
**Branch:** revision/econometrica-r38-verified-global-bounds-2026-09-24  
**Addressed review:** R36, at c81410887bca5c16975beabb2ca8d6be7f235a19  
**Executed science commit:** 589b4a765d5d52de9a13b8a3058f1146f29f9519

## Read these actual submission files

[Article](ECTA_R38.pdf) · [Technical supplement](SUPP_R38.pdf) ·
[Point-by-point referee response](RESPONSE_R38.pdf) ·
[Computation and verification report](COMPUTATION_R38.pdf) ·
[Lossless historical annex](HISTORY_R38.pdf).

Each PDF has a matching root TeX entry point. The complete paper modules,
replication source, proof objects, all configuration ledgers, and provenance are
in [revisions/2026-09-24-r38](revisions/2026-09-24-r38).
The [publication manifest](revisions/2026-09-24-r38/PUBLICATION_MANIFEST.json)
records actual completed builds and artifact hashes, rather than planned outputs.

## What changed scientifically

The original 42 configurations, 0.01/0.05 all-restart tolerances, frozen incumbents,
and horizons 4/8/12 are retained. Fresh exact operating and necessary-action cost
recursions, independently feasible upper policies, and a separate SymPy verifier
certify 24 initial-distribution deterministic optima, including 12 positive-cost
cases. Only 23 additionally have all-state/date cost-function equality; the 18
remaining deterministic intervals are preserved with per-case diagnostics.

A safe L/U outer-class theorem removes exact-V dependence from the general lower
bound. An exact continuation-frontier reference solves 70 fixed-restart
history-conditioned objectives; 24 separate randomized-versus-deterministic
comparisons are strict. A two-period continuum example solves the randomized
Markov and deterministic uniform-initial objectives separately, proving that
randomization cannot be dismissed by a deterministic-sufficiency assertion.

A three-action exact local LP and adaptive whole-cell certificates replace the
sampled local dual. Twelve executed diagnostics quantify approximation to the
continuous local relaxation; no global strong-duality conclusion is inferred.
All 42 configurations receive controlled support/witness/upper-search diagnostics.

All 66 economic sensitivities are published (22 strict savings, 44 zero effects).
A bilinear two-state experiment publishes 76 candidate records, including failed
certificates and a same-grid classical comparator. Its 1/2 operating tolerance is
separate from the primary target. The killed-operator connection retains the
original stopped-control problem and complete scalar proof without misreporting
the original all-domain 0.01 target as attained.

## Verification scope and remaining intervals

42 primary objects and 70 finite-frontier objects pass a separate SymPy
implementation; 20 primary mutation categories are rejected. 187 exact scientific
objects match the development and remote executions. Local LP/nonlinear/sensitivity
checks have their own, explicitly non-independent arithmetic boundaries.

The full primary randomized Markov optimum, the 18 remaining deterministic gaps,
empirical dollar calibration, neural-specific acceleration, and the stopped
all-domain 0.01 target are not declared solved. They are not substituted by a
changed primary cohort. Exact lower/upper fractions, all failures, proof hashes,
and the policy-class distinctions are available for the next referee.

## Preservation and reproduction

See [README](revisions/2026-09-24-r38/README.md) for executable commands.
Every inherited file is checked unchanged except the root revision pointer,
whose former bytes are preserved. No main, review, R35/R36/R37, or other revision
branch is modified. The historical PDF annex retains all earlier R34-package
pages, including the recursive historical material.
