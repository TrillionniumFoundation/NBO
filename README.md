# Neural Bellman Operators

## R13 revision of the original paper

R13 responds to the 4 October 2026 advisory referee report on the R12 development snapshot. The review is pinned at `65110ed2991f4b955d2df37b2ab8635b12df5d1c`. The title and original recursive-utility, endogenous-preference, temporal-self, viscosity and strategic applications are retained. All historical revision folders are unchanged; the reviewed root documents, including the preceding README, are archived under `revisions/2026-10-04-r13/archive/`.

The source branch is `revision/econometrica-nbo-r13-source-2026-10-04`. The publication workflow creates new `revision/econometrica-nbo-r13-evidence-2026-10-04` and `revision/econometrica-nbo-r13-referee-2026-10-04` branches only after execution, preservation, identity, test and compilation gates pass. A development or source branch is not itself a completed evidence submission.

On an evidence branch, the authoritative reading order is:

1. Root `ECTA.tex`, with compiled `revisions/2026-10-04-r13/build/ECTA.pdf`.
2. Root `supp.tex`, with compiled `revisions/2026-10-04-r13/build/supp.pdf`.
3. `revisions/2026-10-04-r13/response.tex` and `build/response.pdf`.
4. `REMOTE_EXECUTION.json`, `results/AUDIT.json`, `EXTRA_AUDIT.json`, the table manifests and the complete raw records in that revision folder.

R13 separates direct method comparisons from schedule-relative improvement and from absolute regret bounds. It adds fixed-simulator-work prefixes, total tested work to common endpoints, independent costate-bank diagnostics, a second environment, stronger scalar-reference diagnostics and a finite-measurement implementation with an explicit error allowance. No positive economic endpoint is a software acceptance condition.

The protocol and reproduction instructions are in `revisions/2026-10-04-r13/`. All earlier research artifacts and advisory reviews remain available in their original directories and branches. Repository verification is not an Econometrica editorial decision.
