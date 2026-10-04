# R14: Neural Bellman Operators

**Revision date:** 4 October 2026  
**Latest report:** [R12 referee report](review_source/referee_report.md)  
**Review commit:** `65110ed2991f4b955d2df37b2ab8635b12df5d1c`  
**Integration base:** `c8299feb2a3af0f147295d50036c8d8acca8f65c`

R14 continues the original NBO paper. It assembles the completed primary and fixed-work evidence, independently replays the economic endpoints, adds a costate-to-welfare inequality and finite-observation transfer, instruments the frozen scalar reference, and reports the evidence through a single integrated manuscript and supplement. No new training is represented as part of R14.

## Authoritative documents

| Item | Location |
|---|---|
| Main article | [Root ECTA.tex](../../ECTA.tex) and [compiled main PDF](build/ECTA.pdf) |
| Full supplement | [Root supp.tex](../../supp.tex) and [compiled supplement PDF](build/supp.pdf) |
| Response | [Response source](manuscript/response_body.tex), [wrapper](response.tex), and [compiled response PDF](build/response.pdf) |
| Comment-by-comment locator | [RESPONSE_MAP.json](RESPONSE_MAP.json) |
| Original-scope preservation and integration | [EDITORIAL_MAP.json](EDITORIAL_MAP.json) and [archived roots](archive/) |
| Revision design and source identities | [REVISION_PLAN.json](REVISION_PLAN.json) |
| Mathematical additions and audit | [MATHEMATICAL_AUDIT.md](MATHEMATICAL_AUDIT.md) |

The main text preserves the title *Neural Bellman Operators* and states the original preference, recursive-utility, temporal-self, and game applications. Their complete derivations, historical numerical outcomes, and proof material remain in the supplement. The capital guarantee is not used to supply an unproved continuous-transfer term for another model.

## Evidence sources

| Evidence family | Generating commit | Workflow run | Original record directory |
|---|---|---:|---|
| Primary, auxiliary, and original scalar experiments | `95053e722e57523c1a61c71f2f8bb7a6afbf09a7` | `37173328744` | [R12 results](../2026-10-04-r12/results/) |
| Fixed-work and repeated-environment extension | `c8299feb2a3af0f147295d50036c8d8acca8f65c` | `37173700379` | [R13 results](../2026-10-04-r13/results/) |

The [restoration manifest](ARTIFACT_RESTORE_MANIFEST.json) records retained artifact identities, archive hashes, source commits, and destinations. The numerical dependency checks compare current historical source files against the exact blobs at their generating commits. A publication snapshot binds both studies, without pretending that they were executed by one common numerical commit or by the later publication commit.

The primary [protocol](../2026-10-04-r12/PROTOCOL.json) and fixed-work [protocol](../2026-10-04-r13/PROTOCOL.json) remain unchanged. Worker environment files and executed package lists are preserved alongside the corresponding result shards. The original final paths are not rerun or replaced while materializing tables.

## Results and interpretation

### Primary policy and method comparisons

There are 90 primary fitted objects: ten fixed training streams, dimensions 10/20/50, and NBO/DPO/affine policies. Both the origin and the finite initial-state population are evaluated, producing 180 primary schedule comparisons. All 180 simultaneous lower improvement endpoints are positive. Every final row uses 8,192 paths and 1,024 time cells.

All 120 direct NBO-minus-DPO or NBO-minus-affine intervals contain zero. Their means, lower and upper endpoints, and input identities are reported seed by seed. The complete primary and auxiliary record contains 244 policy evaluations and 120 method comparisons; 364 statistical raw arrays are independently replayed. Across-stream summaries describe the recorded fitted policies, without assuming a probability population of optimizer initializations.

### Fixed work and common economic targets

The extension contains 28 fits, 56 policy evaluations, and 42 direct comparisons, including one repeated environment. Its principal design has two fixed streams in each dimension and four methods: NBO, DPO, affine, and raw-costate improvement. Every fit completes 80 iterations; checkpoints at 20 and 80 are verified using 8,192 paths and 1,024 cells.

One training iteration uses 128 states and 32 rollout cells. The 20/80 checkpoints therefore use 81,920/327,680 training-state visits and 8,192/32,768 validation-state visits. Methods differ in actor and critic update counts and derivative work. These simulator counts are not floating-point-operation counts.

The common targets are strict schedule-improvement lower endpoints above 0, 0.0005, and 0.001. Each full policy-plus-schedule verification adds 16,777,216 state transitions, and earlier attempted verifications are charged. Unreached targets remain visible. The experiment completed each 80-iteration fit before verification; the checkpoint-prefix frontier is retrospective. Saved evaluation clocks exclude weight loading and deterministic interval-account construction, so sums of recorded clocks are accounted components rather than full end-to-end elapsed time.

The repeated environment has matching initial-state hashes but different innovation hashes. Comparisons within each environment use common paths. The cross-environment repetition is an execution-sensitivity check, not a paired estimator across operating systems or an additional optimizer-population observation.

### Mechanism diagnostics

The corrected reference uses fine rollout replicates 1–15 and excludes the fine replicate paired with the raw action's coarse replicate zero. All stored actions are compared against that common independent reference; original arrays and original diagnostics are retained. In all six principal panels, the critic has larger MSE and its greedy action has a larger reference Hamiltonian gap than the raw-costate alternative. Critic/raw MSE ratios range approximately from 1.06 to 1.99.

Reference sampling variation, nested 32/128-cell sensitivity, and the held-out state design are reported separately. These are descriptive mechanism diagnostics. They do not constitute a continuous-time costate certificate or supply the candidate-occupation errors in the new welfare proposition automatically. The separately trained raw-costate comparator is distinct from the diagnostic raw greedy action of a frozen NBO policy.

### Scalar reference

The frozen policies are replayed on `(401, 256, 6)`, `(801, 512, 6)`, `(1601, 1024, 6)`, and `(1601, 1024, 8)`, where the final coordinate is the log-capital domain half-width. All 28 original arrays reproduce exactly in the recorded environment. The new account records fixed-policy/HJB residuals, Howard histories, action-bound frequencies, boundary values, complete refinement changes and locations, and losses at five initial states.

NBO has a smaller finite-grid policy loss than DPO at zero on the finest domain-six grid; DPO has a smaller loss at initial state one. Shared asymptotic boundary functions are prescribed boundary data, not verified unbounded fixed-policy values. The wider-domain comparison also changes grid spacing. The reference remains a scalar Markov-feedback diagnostic; high-dimensional randomized-history controllers use their own continuous-economy arguments.

### Finite observations

The [sensing protocol](results/sensing/PROTOCOL.json) evaluates the original 80-iteration NBO checkpoint at dimensions 10/20/50, 64/128 decision cells, and sensor RMS 0/0.001/0.01, with 128 paths and eight fine Euler steps per decision. All 18 cells are recorded in the [sensing index](results/sensing/INDEX.json), [final audit](FINAL_AUDIT.json), [complete file manifest](EVIDENCE_MANIFEST.json), and [base preservation](PRESERVATION.json).

The mathematical result bounds the payoff difference from the exact protected parent through global actor/reference-map bounds, arithmetic, accumulated clipping and recurrence error, and the sensor moment bound. The simulated shared-noise differences are fine-Euler diagnostics. A confidence interval transfers only from a certificate for that exact protected parent and decision mesh. No certificate from the original 1,024-cell run is assigned to these different parent meshes.

## Statistical allocation

The primary record uses 728 one-sided statements and the extension uses 196, for **924 of 4,000** at the declared family level `alpha = 0.05`. Both signs of an interval are counted. The new mechanism, scalar, and sensing diagnostics add no stochastic confidence endpoints. The allocation and union check are recorded in [EXTENSION_AUDIT.json](results/EXTENSION_AUDIT.json).

## Reproduction

Run commands from the repository root in a compatible environment. The original generating environments are recorded in the source-bound worker records; current replay and diagnostic environments are recorded separately. Use the executed package lists and the corresponding `ENVIRONMENT.json` files for environment reconstruction. A source-aware replay is distinct from retraining a time-budgeted experiment on another machine.

### Complete reproduction command

```bash
python revisions/2026-10-04-r14/code/reproduce.py --repo-root .
```

This runs artifact verification or restoration, both endpoint reporters, the scalar and sensing diagnostics, all 123 regression assertions, integration, compilation, and finalization in dependency order. On a complete evidence branch, the original records are already present. If records are missing, restoration uses `GITHUB_TOKEN` only to retrieve the pinned original GitHub Actions artifacts and verifies every archive and member hash. The delivery workflow publishes the complete tree only after all stages and the committed-source check pass.

### Replay existing endpoints and tables

```bash
python revisions/2026-10-04-r14/code/report_primary.py --repo-root .
python revisions/2026-10-04-r14/code/report_extension.py --repo . \
  --primary-audit revisions/2026-10-04-r14/results/AUDIT.json
python revisions/2026-10-04-r14/code/run_tests.py --repo-root . --inherited
```

The primary replay checks all source dependencies and raw rows before materializing current tables. The extension replay checks its own generating source, original arrays and weights, direct differences, corrected mechanism reference, work targets, and family allocation. They write derived R14 outputs and preserve the original records.

### Recompute the instrumented scalar reference

```bash
python revisions/2026-10-04-r14/code/reference_diagnostics.py \
  --repo . \
  --reference-dir revisions/2026-10-04-r12/results/reference \
  --output-dir revisions/2026-10-04-r14/results/reference
```

This operation evaluates the frozen actors; it does not retrain them. Replay tolerances are a computational identity check, not an economic error bound.

### Recompute finite-observation diagnostics

```bash
python revisions/2026-10-04-r14/code/sensing_diagnostic.py \
  --repo . \
  --weights \
    revisions/2026-10-04-r13/results/ubuntu24_d10_s7919/nbo_d10_s7919_fixed_nbo_k80.pt \
    revisions/2026-10-04-r13/results/ubuntu24_d20_s7919/nbo_d20_s7919_fixed_nbo_k80.pt \
    revisions/2026-10-04-r13/results/ubuntu24_d50_s7919/nbo_d50_s7919_fixed_nbo_k80.pt \
  --out revisions/2026-10-04-r14/results/sensing
python revisions/2026-10-04-r14/code/diagnostic_tables.py
```

The protocol is written before inspecting weights or computing diagnostic results. It fixes the complete 18-cell design. The output index requires all three dimensions.

### Integrate and build the reading copy

```bash
python revisions/2026-10-04-r14/code/integrate.py
python revisions/2026-10-04-r14/code/build.py
```

The build requires the repository's Econometric Society class/bibliography files, `pdflatex`, `bibtex`, and `pdftotext`. It compiles the mutually cross-referenced article, supplement, and response, and records [COMPILATION.json](results/COMPILATION.json). Undefined references, duplicate labels, and unresolved overfull material are publication-check failures.

## Preservation and validation

The recorded regression replays pass 19 unchanged R12 assertions plus 104 inherited assertions. Historical layout/hash assertions execute in an isolated exact historical source view. The current roots are not overwritten with that view, and historical assertions are not edited to accept new hashes.

Current-tree preservation is separate: every base-tree blob must remain at its path or its explicitly declared archive. The integration records all preserved root labels and intact relocations. Original numerical source, weights, arrays, failed experiments, and advisory reports retain their identities. Current compilation, table-input checks, and preservation records must accompany the final publication snapshot.

Key records are [AUDIT.json](results/AUDIT.json), [PRIMARY_REPLAY_PROVENANCE.json](results/PRIMARY_REPLAY_PROVENANCE.json), [EXTENSION_AUDIT.json](results/EXTENSION_AUDIT.json), [RAW_IDENTITY_AUDIT.json](results/RAW_IDENTITY_AUDIT.json), [TESTS.json](results/TESTS.json), [INHERITED_TESTS.json](results/INHERITED_TESTS.json), [TABLE_MANIFEST.json](TABLE_MANIFEST.json), [EXTENSION_TABLE_MANIFEST.json](EXTENSION_TABLE_MANIFEST.json), [reference diagnostics](results/reference/REFERENCE_DIAGNOSTICS.json), and [sensing index](results/sensing/INDEX.json), [final audit](FINAL_AUDIT.json), [complete file manifest](EVIDENCE_MANIFEST.json), and [base preservation](PRESERVATION.json).

## Delivery branches

| Target branch | Role |
|---|---|
| `revision/econometrica-nbo-r14-source-2026-10-04` | Integrated article and reproducibility source. |
| `revision/econometrica-nbo-r14-evidence-2026-10-04` | Complete evidence, source, manifests, and compiled documents after publication checks. |
| `revision/econometrica-nbo-r14-referee-2026-10-04` | The corresponding versioned copy for subsequent referee review. |

These are delivery targets; actual publication status is determined by the remote refs and final publication record. The research title, original economic applications, and historical evidence remain intact. Repository validation and an advisory referee response are not an Econometrica editorial decision.
