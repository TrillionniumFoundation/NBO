# Neural Bellman Operators

**R14 Econometrica revision — 4 October 2026**

This repository develops *Neural Bellman Operators* by Qian QI: policy evaluation, feasible improvement, and independent economic verification for continuous-time control and equilibrium models. Endogenous preference formation, recursive utility, temporal selves, and dynamic games remain part of the paper. The current capital results add policy-specific continuous-time verification, a costate-to-welfare account, and a finite-observation transfer.

## Read the revision

1. [Main article](ECTA.tex) and [complete supplement](supp.tex).
2. [Response to the latest R12 advisory referee report](revisions/2026-10-04-r14/manuscript/response_body.tex).
3. [R14 evidence, interpretation, and reproduction guide](revisions/2026-10-04-r14/README.md).
4. [Main PDF](revisions/2026-10-04-r14/build/ECTA.pdf), [supplement PDF](revisions/2026-10-04-r14/build/supp.pdf), and [response PDF](revisions/2026-10-04-r14/build/response.pdf), produced by the R14 build.
5. [Latest referee report](revisions/2026-10-04-r14/review_source/referee_report.md), retained at review commit `65110ed2991f4b955d2df37b2ab8635b12df5d1c`.

The root TeX files are the authoritative integrated reading copy. The integration program is also retained, and the prior roots are archived exactly.

## What the completed record establishes

| Evidence | Recorded result and scope |
|---|---|
| Primary study | 90 fitted policies; 180 origin/population comparisons with the analytical schedule; all 180 lower improvement endpoints are positive. |
| Direct primary comparisons | All 120 NBO-minus-DPO or NBO-minus-affine intervals contain zero. Positive schedule improvement does not establish a direct method ranking. |
| Fixed-work extension | 28 fits, 56 evaluations, 42 direct comparisons, exact 20/80-iteration checkpoints, simulator-visit accounts, and common certified-gain targets. |
| Critic mechanism | The corrected independent-reference critic MSE and critic-greedy Hamiltonian gap are larger than their raw-costate counterparts in all six principal panels. These diagnostics are reported with their reference noise and state-distribution scope. |
| Scalar reference | Four frozen-policy grids replayed; 28 original arrays reproduced exactly in the recorded environment; residual, boundary, action, refinement, and five-state diagnostics added. NBO has the lower loss at the origin; DPO has the lower loss at initial state one on the finest domain-six grid. |
| Finite observations | 18 executed sensing cells accompany a conditional continuous-economy transfer theorem. Their fine-Euler differences are diagnostics, and no old certificate is assigned to a different parent or time grid. |

The primary and fixed-work inference records use **924 of 4,000 allocated one-sided statements**. New mechanism, scalar, and sensing diagnostics do not add confidence endpoints. Initial-state population results are integrated over the specified finite population; they are not uniform over all states or calibrated empirical welfare estimates.

## Sources and evidence

The numerical studies were executed at two distinct committed sources. R14 integrates their complete recovered evidence and adds independent replay, corrected mechanism postprocessing, new mathematics, reference instrumentation, and sensing diagnostics. It does not relabel the historical fits as new R14 training.

| Study | Generating source | Worker run | Raw results |
|---|---|---:|---|
| Primary, auxiliary, and original scalar calculation | `95053e722e57523c1a61c71f2f8bb7a6afbf09a7` | `37173328744` | [R12 results](revisions/2026-10-04-r12/results/) |
| Fixed-work and second-environment extension | `c8299feb2a3af0f147295d50036c8d8acca8f65c` | `37173700379` | [R13 results](revisions/2026-10-04-r13/results/) |

[Artifact restoration](revisions/2026-10-04-r14/ARTIFACT_RESTORE_MANIFEST.json), [primary replay provenance](revisions/2026-10-04-r14/results/PRIMARY_REPLAY_PROVENANCE.json), [extension audit](revisions/2026-10-04-r14/results/EXTENSION_AUDIT.json), and [raw identity audit](revisions/2026-10-04-r14/results/RAW_IDENTITY_AUDIT.json) bind sources, inputs, outputs, and interpretation. Original worker environments and protocols remain with their records.

## Reproduction and publication checks

Follow the [R14 guide](revisions/2026-10-04-r14/README.md) for source-aware replay and build commands. The recorded regression replays pass 19 current R12 assertions and 104 inherited assertions. Historical suites use their exact historical source view. Current-tree preservation and current-manuscript compilation are separate publication checks; their reports should be read alongside the numerical audits.

The delivery branches are:

- `revision/econometrica-nbo-r14-source-2026-10-04` — integrated source and reproducibility programs.
- `revision/econometrica-nbo-r14-evidence-2026-10-04` — complete source, numerical evidence, manifests, and compiled documents.
- `revision/econometrica-nbo-r14-referee-2026-10-04` — the corresponding versioned review copy.

These names describe the delivery targets; branch publication status and the final commit should be checked from the remote refs and publication record. A passing repository check does not constitute an Econometrica editorial decision.
