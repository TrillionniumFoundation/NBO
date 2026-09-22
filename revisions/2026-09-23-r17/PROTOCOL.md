# R17 protocol: certificate-guided Neural Bellman Operators

Review input: `82af00bc296da59e8a3a28ef1bf86c1d6fca2367`.
Reviewed R16 publication: `2932b74dad6d8d9efce5a114d5098a99ea17ab1f`.
Date: 2026-09-23.

The original stopped economy, action comparison, settlement, horizon, and accuracy targets are unchanged. This protocol is committed before the new confirmatory experiment. Exploratory implementation diagnostics, including unsuccessful trials, will be reported separately and may not be substituted for confirmatory observations.

## Certificate-guided neural experiment

Ten deterministic independent initialization seeds, 17100 through 17109, use width 16 for even seeds and width 32 for odd seeds. Both accessibility-preserving and all-face hard-trace witnesses are considered with identical initialization, actor parameterization, sampling/cell selection, optimizer budget, and audit cover within each seed. The action comparison always uses the full original continuous action set, not the candidate architecture's restricted portfolio head.

The proposal objective is the time-integrated positive optimal-residual and negative policy-residual upper surrogate on a complete state-time cell cover. Floating-point differentiation is proposal generation only. Every retained checkpoint is separately enclosed by the historical MPFR directed-arithmetic verifier. The implementation diagnostics will set optimizer parameters before the confirmatory suite and record them. Checkpoints are 0, 100, and 400 joint optimization steps. All proposals are retained whether accepted or rejected. Nonfinite proposals are rejected and recorded. The acceptance rule retains a new actor/witness pair only if its independently computed complete certificate is strictly below the incumbent certificate. A nonincreasing incumbent certificate is not claimed to imply monotone actual policy values or convergence to zero.

The primary common cover is 4 x 16 x 16 time/preference/wealth cells. Fixed-object refinement for the designated seed 17100 is performed on 8 x 32 x 32 and 16 x 64 x 64 covers when executable; any unavailable level is explicitly reported, not interpolated. The accuracy targets remain 0.01, 0.005, 0.0025, and 0.001; crossing a target is never inferred from sampled losses, an auxiliary economy, or a non-neural comparator.

Report all seed-level raw proposals and incumbent bounds, signed residual decomposition, action gap, wall time for generation and audit, memory, architecture, failures, and the full-domain versus initial-state scope. Matched architecture ablations use identical resolution and work. Training-side numerical arithmetic is not asserted to certify the inference implementation.

## Other referee responses

Preserve the complete R16 manuscript, supplementary derivations, neural checkpoints, negative results, sharp non-neural price libraries, and MPFR arithmetic audit. New comparison objects must have separate identifiers and disclose policy restrictions and witness sources. Any unrestricted classical experiment is distinguished from the restricted R16 baselines and from a continuous-time accuracy claim. A validated Riccati comparator reports both per-coordinate and total loss. Any nonlinear high-dimensional extension must disclose whether its value is known analytically and may not be used to certify the original economy. General algorithmic theorems state their checkable hypotheses; no stochastic optimizer convergence is assumed.

The response matrix will distinguish mathematical corrections, implemented and executed algorithmic changes, and numerical targets actually achieved. It will not treat a manuscript edit or a test pass as closure of an unachieved numerical requirement.
