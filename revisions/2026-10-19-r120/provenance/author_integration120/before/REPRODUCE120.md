# Reproducing the R120 author revision

This is the original **Neural Bellman Operators** author revision. The economic
objective, continuous innovation law, terminal controller, constraints and
representation controls are defined in the frozen protocols. A reproduction
must distinguish checking saved evidence from running a new economic campaign.
Historical R98, R108, R110, R115 and R119 experiments retain their own identities;
the commands below do not complete a different independently constrained study.

## Immutable scientific and information barriers

| Role | Actual GitHub commit |
|---|---|
| Complete inherited R119 publication | `82618f037540233dda7d1ba8bfd3ddfdc88afbf9` |
| F: R120 scientific source, mathematics and protocols | `369d02724cf12ae0e54390b4e7b5f894f703892e` |
| M: all newly acquired original-value labels and models | `1c5e4dc7e04c108fe698d4c247a144b625db301c` |
| D: single independent state-byte acquisition | `aebc7a0175c0729b9ff5e833a7facc1ed5c4c2fd` |
| Reporting rules, published before primary outcomes | `594d9336d89bedfd360e942146ae490e0fabd3a0` |

The branch is
`revision/econometrica-nbo-r120-certified-policy-improvement-2026-10-19` in
`TrillionniumFoundation/NBO`. F is an ancestor of M, and M is an ancestor of D.
The separate actual GitHub update receipts and local byte checks are in
`provenance/SOURCE_PUBLICATION120.json`, `ACTOR_PUBLICATION120.json`, and
`STATE_PUBLICATION120.json`. Their times distinguish a prepared transport
request from a completed remote publication. The reporting specification has
its own later source identity; it does not amend the earlier scientific source.

The frozen source manifest contains 157 scientific inputs and is itself checked
as the 158th file against F. Its SHA-256 is
`29dc408eaa4a37bf2465f7a6f91ffbc8ffcd55efc27394a77c7785df20fb0f54`.
Each scientific entry point checks local bytes against the manifest and the
actual Git commit before importing numerical packages or acquiring sample bytes.
Use a Git checkout containing these commits for a fresh scientific execution.
An extracted archive alone can verify its file hashes and recorded evidence;
it does not recreate a Git commit object or turn a saved receipt into a new run.

## Runtime and working directory

Run commands from `revisions/2026-10-19-r120` in that checkout. The original
execution uses Python 3.12.14, NumPy 2.3.5 and SciPy 1.17.0. The complete pinned
Python list is `requirements120.txt`. All scientific commands set
`OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, and `MKL_NUM_THREADS=1`.
`provenance/launch120.py` applies these settings and preserves an exclusive launch
directory, exact command, start/end clocks, process exit code and full output.
It is an execution recorder prepared after F, and changes no scientific input.
The campaign also writes its own source-gated receipts and all numerical events.

PDF construction additionally requires pdfLaTeX, BibTeX and Poppler, with the
supplied Econometric Society class, bibliography styles and preamble. The build
receipt identifies the actual installed tool versions and final TeX recorder
input closure. No numerical experiment or table generation is hidden in a build.

## Replay the saved independent state sample

The primary replay uses the original M models and D state bytes. Choose new,
nonexistent attempt names; never overwrite the retained attempt directories.

```bash
python -u provenance/launch120.py primary-replay01 -- \
  python -u code120/campaign120.py primary \
  --source-commit 369d02724cf12ae0e54390b4e7b5f894f703892e \
  --actors results120/acquisition-attempt01 \
  --actor-commit 1c5e4dc7e04c108fe698d4c247a144b625db301c \
  --states results120/states-attempt01 \
  --state-commit aebc7a0175c0729b9ff5e833a7facc1ed5c4c2fd \
  --output results120/primary-replay01
```

The command executes all 4,096 primary decisions and then three fresh serial
timing processes, each with 2,048 decisions. The 6,144 timing decisions reuse the
fixed first 32 initial-state rows and do not enlarge the independent sample.
Do not run the rational validator, a PDF build, another solver, or a replay in
parallel with those timing processes. External machine load and frequency remain
uncontrolled, so recorded wall clocks are descriptive. Preserve every clock and
all exact-action disagreements between the primary run and timing repetitions.

After the entire primary/timing command has finished, execute the separately
implemented exact rational reconstruction:

```bash
python -u provenance/launch120.py independent-replay01 -- \
  python -u code120/independent120.py \
  --source-commit 369d02724cf12ae0e54390b4e7b5f894f703892e \
  --primary results120/primary-replay01/records120.jsonl \
  --output results120/independent-replay01
```

Every unique returned state/action/risk key is evaluated with the same 64-cell
full-support mesh and 32-step rational terminal solve, retaining all 129 terminal
contexts per key. No result-dependent key selection or extra resolution is
authorized. This reconstructs original-policy bounds and independent all-action
lower supports for the original optimum. The deployed terminal controller's
uniform error is paid once; the validator does not pretend that its rational
optimizer is the deployed future controller.

Then execute the fixed statistical calculation:

```bash
python -u provenance/launch120.py statistics-replay01 -- \
  python -u code120/stats120.py \
  --source-commit 369d02724cf12ae0e54390b4e7b5f894f703892e \
  --primary results120/primary-replay01/records120.jsonl \
  --independent results120/independent-replay01/comparisons120.jsonl \
  --output results120/stats-replay01
```

The 48 within-incumbent gain groups and 192 fixed-threshold events retain their
prespecified simultaneous error allocation. Missing independent comparisons are
kept conservatively and explicitly, never dropped. A state-sample replay gives
no new independent observations. A saved-record audit gives no new execution of
the economic solvers. Runtime scenarios obtained by amortizing saved clocks are
reported as scenarios, not measured scaling experiments.

## A genuinely new sample is a different study instance

To acquire new models, run the frozen `acquire` mode into a new exclusive
directory. Publish all its labels, fitted models, failed candidates, audits and
cost records to a real new model commit before invoking `sample`. The sampler
must verify that exact model commit and obtains one new 640-byte OS sample.
Publish those bytes to a distinct state commit before running `primary` with
the new M/D identities. A changed seed, model, grid, dimension, population,
parameter, service menu, stopping rule or numerical source is an explicit new
protocol or amendment, not a replay of the original preregistration.

The byte law is the product uniform 40-bit coordinate law conditional on the
stated ideal independent uniform OS-byte assumption. Duplicate rows are retained.
The file `entropy120.bin` is scientific sample material, not an account credential.
Its 640 bytes have already been publicly committed with the state manifest.

## Author sources, audits and publication

`ECTA.tex` is the current main article; `supp.tex` contains full proofs;
`appendix.tex` preserves the historical development and complete numerical
accounts; `RESPONSE_TO_REFEREE.tex` provides the current author response and its
historical response routes. `CONTENT_RETENTION_MAP120.md` identifies moved and
retained material. The immutable R119 package remains separately identified for
historical raw records and source/PDF hashes.

R120-INTEGRATION-PENDING: the exact saved-evidence audit, reporting, final build,
archive verification and actual CI commands and receipts are added after their
successful execution. Until then this document makes no completion claim for
those stages.
