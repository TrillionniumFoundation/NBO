# R15 exploratory critic diagnosis

This directory preserves the exploratory work that motivated the subsequent frozen R15 design. It contains all 27 scientific pilot files, including unfavorable configurations, raw derivative/value banks, diagnostic predictions, model weights, and the current exploratory drivers. `ARCHIVE.json` inventories every original file with its byte count and SHA256 and collects the final diagnostics for all 12 displayed configurations. All original files are copied without editing their bytes.

These observations are development evidence. They are not observations from the prospectively declared 16-stream confirmation experiment. No final economic payoff bank, early-stopping procedure, or end-to-end attainment comparison was run in these pilots. Repeated inspection of a common diagnostic bank informed subsequent choices. The final R15 design therefore requires its own independent tests.

## What was learned

The historical critic already included the known linear aggregate-capital and quadratic dispersion terms. That centering is not introduced as a new contribution. The exploratory changes concerned how the unknown spatial derivatives were fitted: fixed-policy targets, reusable antithetic rollout labels, separate spatial and time-only residuals, and substantially longer optimization of the frozen Sobolev objective.

In the original calibration at dimension 20, additional replay optimization improved on the historical online critic in several configurations. It did not improve on a strong raw estimator that averaged four antithetic continuation paths. A fresh critic trained with the old joint value/costate loss was worse than the original critic. Those outcomes are retained.

In the higher-volatility calibration, with the analytical schedule held fixed, a split critic after 1,200 Adam updates had costate MSE approximately 6.86e-5 against the finite Monte Carlo reference. Four-antithetic Raw had MSE approximately 4.98e-5. Further optimization of the same fixed replay by L-BFGS reduced the generic split critic's displayed MSE to approximately 2.96e-5. A more specialized exposure architecture reduced it to approximately 2.59e-5 but used substantially more fit time. The generic split architecture was selected for the subsequent design; the specialized architecture and its results remain in this archive.

The high-volatility reference variance estimate was approximately 2.56e-5. Consequently, a large part of the displayed MSE is noise in the finite reference mean. The stored `costate_mse_mc_debiased` subtracts this estimated reference variance. It is a descriptive noise correction, not a confidence interval or an exact derivative error. It does not remove the difference between training and reference meshes.

The original gradient diagnostic also does not show that the weighted value loss dominates the derivative loss: the two parameter-gradient norms were of similar size and their cosine was about 0.166. Separating the time-only nuisance prevents it from changing the fitted state derivatives; it does not retroactively establish a single causal explanation for the historical failure.

## Numerical and provenance scope

Each pilot samples one state from an independently simulated occupation trajectory. The early target drivers divide each state's remaining time horizon into a fixed number of cells. Those state-dependent meshes differ from the single global grid used by `training_core.py` in the frozen R15 experiment. Pilot results are not used to claim an exact discrete Bellman identity or a continuous-time costate-gradient bias bound.

The high-volatility `PILOT.json` contains the exact primitive dictionary and an execution-time driver SHA256 that matches the preserved `critic_pilot.py`. The earliest original-calibration JSON predates those metadata fields; its exact driver revision was not independently snapshotted. The convergence driver was not separately hashed at execution. Current driver bytes, original outputs, banks, and weights are preserved, and these limits are explicit rather than filled with reconstructed provenance.

The drivers retain their original absolute workspace paths. They document the exploratory execution and are not the portable production runner. The production experiment uses the separately frozen R15 protocol and worker, source and method fingerprints, exact global-grid targets, fresh stopping banks, and independent final confirmation.

## File groups

- `d20_s7919/`: historical candidate in the original calibration; five replay variants and the historical online diagnostic.
- `d20_s7919_high_anchor/`: higher-volatility economy with a fixed analytical schedule; three Adam variants and the historical-weight diagnostic.
- `d20_s7919_high_anchor/converged/`: generic split and exposure L-BFGS fits on the already observed higher-volatility bank.
- `critic_pilot.py`, `converged_pilot.py`: the preserved exploratory drivers.
- `ARCHIVE.json`: immutable-file hashes, provenance limits, scope statements, and final diagnostic summaries.

The functional smoke outputs used to check the new production API are not scientific pilot observations and are excluded from this archive. The committed production unit tests cover that interface independently.
