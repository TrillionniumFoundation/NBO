# Subsequent deterministic refinement of the R15 paired payoff transfer

## Chronology and scope

This refinement was developed **after** the main numerical source had been
frozen at `9142f404bb9c5163aa94d3a4ded4d0fa48a49c50`, and after the first
completed trial's deterministic transfer width had been inspected. The
original main protocol was frozen on 2026-10-04 at 08:17:45 UTC. This document
does not retrospectively call the new theorem or its postprocessor
preregistered.

The issue was mathematical: the original direct comparison added the two
valid individual-policy diffusion-transfer bounds. At the original 2048-cell
mesh their sum exceeded the fixed economic margin of 0.0001. Additional
independent payoff paths could reduce sampling error but could not reduce
that deterministic term. The new proof bounds the **difference of the two
errors on common innovations** and retains its dependence on the common
action-tube radius. No fitted weight, payoff sign, method ranking, or selected
stream was used to derive or choose its constants.

The refinement uses the same capital interaction matrices, high-volatility
primitives, nine-profile initial law, original 2048-cell grid, total-held
actions, and original paired payoff vectors. The full proof is
`manuscript/paired_transfer.tex`. The calculation and complete-report replay
are in `code/report_paired_transfer.py`. The independent deterministic gates
are in `code/paired_transfer_checks.py`.

The proof and its translation were independently reviewed by the mathematical
revision agent and the root reviewer. The review checked the four-point
decomposition, normalized vector and scalar generator bounds, diffusion
Hilbert--Schmidt bound, opposite-order Chebyshev inequalities, discrete
Gronwall recurrence, profile-conditional terminal bound, positive-series
remainders, interval spectral norms, and the original numerical-statistic
linkage. The review also required the original direct-subtraction cushion,
the endpoint drift monotonicity guard, the coupling-matrix byte identity, and
directed rounding of displayed interval endpoints.

## What changes

For a direct comparison of two simulated policies, let the original
deterministic allowance be `bias_original`. The postprocessor constructs the
proved `bias_paired` and uses

```
bias_refined = min(bias_original, bias_paired)
```

It separately reports both original and refined confidence endpoints. The
new term contains the paired ideal-Euler production and terminal errors,
both saved forward-arithmetic and innovation-clipping state allowances,
both saved complete statistic-arithmetic allowances, and the original
`1e-12` direct-subtraction cushion. It does not silently remove a saved
rounding term because two paths happen to be paired. Common-reference
cancellation is checked through the original reference-state hash and path
identities; the saved complete statistic quadrature allowances remain.

The theorem is applied only when **both policies are simulated total-held
controllers**. A comparison with exactly one analytical-schedule fallback
retains the original complete schedule-relative allowance. Two analytical
fallbacks retain the exact zero identity. Every declared method, dimension,
and stream is required; missing records, changed matrices, changed primitive
dictionaries, incomplete confirmations, or mismatched common-path identities
are errors.

All original individual schedule-relative method endpoints, actual stopping
decisions, target-attainment records, fitting costs, unsuccessful checks, and
complete per-method work records remain authoritative and unchanged. The
postprocessor has its own elapsed-work record. Its cost is not inserted into
or subtracted from the historical execution clocks, and its refined final
contrasts are not used to claim earlier stopping.

## Why no additional confidence probability is spent

The original empirical Bernstein event controls the expectation of a
particular bounded, clipped finite-grid statistic. That event and the new
deterministic payoff-transfer theorem can hold simultaneously without a
new random event. The theorem changes the deterministic connection between
the **same** finite expectation and the **same** continuous-economy payoff
contrast.

The postprocessor therefore keeps each path vector, clipping threshold,
clipping-tail bound, empirical variance, empirical Bernstein margin, event
alpha, method population, and stream population exactly as in the original
report. It replays each original direct endpoint and requires its original
lower and upper endpoints to agree exactly. It separately checks that the
refined calculation has the same clipped moments, range, tail, sampling
margin, and alpha. The complete mean over sixteen declared streams retains
the original equal-stratum calculation, original maximum range, and original
average clipping tail; only the average deterministic transfer can shrink.

There are 96 direct per-stream events and 6 direct finite-method-mean events
within the existing 238-event confirmation family. The refinement reuses
these 102 events and creates **zero** additional confidence events. No unused
stopping or failure probability is recycled. The original total R15
allocation and its distinct historical-family scope remain unchanged.

## Mathematical details that matter for implementation

1. Actions are the original total actions held over a cell. They may have
   been computed from rounded internal states. The same realized actions
   are used when coupling each continuous economy with its ideal Euler
   economy. No actor derivative or recomputation at ideal states is assumed.
2. The vector four-point drift term retains its `sqrt(d)` factor. The scalar
   mean-production Hessian and the normalized Hilbert--Schmidt diffusion
   derivative term do not acquire that factor.
3. The martingale is accumulated before taking its second moment. A future
   random state-propagation matrix is not moved inside an isometry.
4. The initial-spread average is taken after applying conditional
   Cauchy--Schwarz separately to each of the nine initial profiles. It is not
   treated as the unconditional mixture's root-mean-square dispersion.
5. Positive series enclose the state-distance function and its two integrals,
   avoiding cancellation in the first grid cells. Their geometric remainder
   ratios are included. The implementation requires the original horizon,
   dyadic grid, fixed primitives, and `beta*T < 1` domain.
6. An interval-matrix spectral bound includes both the verified midpoint
   operator norm and an outward Frobenius bound on its radius. Weighted
   matrices are not silently rounded before a spectral certificate is used.
7. The drift bound using the terminal schedule value requires and checks
   `c < m0(0)`, together with the inherited increasing schedule. Original
   component records must carry the same exact binary64 coupling-matrix
   SHA256 as the new account.
8. Saved arithmetic and clipping errors are charged policy by policy. The
   complete original `1e-12` paired-subtraction allowance remains. Displayed
   lower endpoints round downward and displayed upper endpoints upward;
   decisions use the complete JSON endpoints.

The original individual transfer was already first order in the mesh. The
new result improves paired cancellation and constants; it does not claim a
new convergence order for the original additive-noise Euler scheme.

## Reproduction and output contract

From the repository root, calculate the model-only account in a new empty
directory:

```bash
python revisions/2026-10-04-r15/code/report_paired_transfer.py \
  --constants-only \
  --out revisions/2026-10-04-r15/results/paired_transfer_constants
```

The resulting `PAIRED_TRANSFER_CONSTANTS.json` contains all coefficient
certificates, individual error components, primitive and matrix fingerprints,
and the source-file bindings. This command reads no fitted weights or payoff
arrays and performs no policy simulation or fitting.

Run the independent deterministic checks in a fresh process:

```bash
python revisions/2026-10-04-r15/code/paired_transfer_checks.py \
  --out /tmp/nbo-r15-paired-transfer-checks.json
```

After the complete original experiment and original report exist, produce
the comparison report in a separate new directory:

```bash
python revisions/2026-10-04-r15/code/report_paired_transfer.py \
  --results revisions/2026-10-04-r15/results/experiment/trials \
  --original-report revisions/2026-10-04-r15/results/experiment/report/REPORT.json \
  --out revisions/2026-10-04-r15/results/paired_transfer
```

The actual original report location may be supplied explicitly. It is never
overwritten. The derived output consists of:

- `PAIRED_TRANSFER_REPORT.json`: complete original and refined direct
  endpoints, all original identity records, saved numerical allowances,
  model accounts, exact input-file hashes, and an independent work record.
- `paired_transfer_main.tex`: all six original and refined direct
  finite-method-mean comparisons.
- `paired_transfer_supplement.tex`: all 96 original and refined direct
  stream comparisons, including fallback status.

For an independent replay, append
`--coefficient-record <original PAIRED_TRANSFER_REPORT.json>`. The stored
spectral majorants are proposals only: the code requires exact matrix SHA256
identity and recomputes the outward interval LDL proof and the upper square
root. The original deterministic formulas are recomputed using those same
verified majorants. The same treatment applies to each weighted interval
matrix. The replay therefore does not depend on the last bits of a new
platform's SVD proposal. It permits **no** tolerance on an economic endpoint.
The complete scientific JSON and the two tables must agree exactly; only
the top-level `generated_utc` and `postprocessing_seconds_before_writes`
runtime receipt fields differ. The independent audit records the replay
command and coefficient-record path. All accepted coefficient proposals are
themselves contained and re-proved in the resulting model accounts.

In constants-only mode, the corresponding runtime field is
`postprocessing_seconds`. Supplying its earlier constants file through
`--coefficient-record` likewise requires complete exact scientific replay.

The code verifies every imported repository source file and the original
protocol against the generating Git commit. It separately hashes the new
postprocessor, checks, proof, and this chronology record. Result, work, and
payoff-array hashes must match the unchanged original report. Every input is
checked again before output is finalized. The new output directory must be
empty and outside the original trial and report directories.

## Development record

The exploratory derivation was evaluated only on fixed model coefficients
under `r15-verification/paired_transfer_proposal.py` outside the repository.
An early deterministic implementation had an off-by-one geometric-tail
ratio in two series remainders. It was corrected before independent review
and before any official endpoint used the refinement. Both superseded
scratch files were retained. The corrected tail terms are far below the
outward floating-point accumulation widths; no policy, payoff vector,
stream selection, or statistical event was involved in that correction.

The committed calculation does not import that scratch proposal. It contains
the full corrected calculation, validates the unchanged historical source,
and includes independent high-precision checks of the enclosed functions.
The complete proof is part of the revision source. Model-only bounds are
reported as deterministic calculations, never as additional confirmatory
policy outcomes.
