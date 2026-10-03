# Post-review comparisons, R8

These are post-R7-review experiments, not retrospectively preregistered R7 results.
The economic grids, utility normalization, exit/terminal rules and control sets
are unchanged. Fixed seeds are 11, 29 and 47. Main neural critics receive 480
Adam steps and 300 L-BFGS iterations per time level; R7 NBO used 320 critic and
160 actor steps. Actual closures, oracle queries, construction, optimization and
verification are reported separately. This is matched nominal update work, not
an assertion of matched wall time, parameter count, or achieved economic error.

The additional NDU critics are a two-block, width-32 DGM-style gated architecture
(finite Bellman regression, not a mesh-free differential DGM implementation) and
tensor Chebyshev degrees 6, 10 and 14 with the same hard wealth-boundary lifting.
The game compares actor-free neural continuation fitting against classical
backward selection, for market sizes 1 and 2. Complete dynamic best responses
are recomputed in every case. A missing pure stage equilibrium uses the minimum
joint-defect action and remains visible. Every executed failure is retained.

The R8 continuous-action study does not receive exhaustive argmax training
labels. Raw actors, continuous local improvement, eight-restart direct control
optimization, and an actor-free local-search ablation are distinct deployments.
The initial failed runs and conservative action-cover outputs are retained.
Refining the interval cover after seeing a loose bound is development, not a
new independent efficacy trial. Unresolved boxes retain their upper bounds.
