# Neural Bellman Operators — R12 Econometrica revision

This revision continues **Neural Bellman Operators** by Qian QI. It addresses the advisory R11 referee report committed at `7e4393a6cae766b55975996a68515dc3e3b390e4`, on the R11 evidence snapshot `840565f451be6103aeb325a8fc548a57507a8fb2`.

## Authoritative reading order

1. [Main article](ECTA.tex) and [full supplement](supp.tex).
2. [R12 response](revisions/2026-10-04-r12/manuscript/response_body.tex).
3. [Fixed R12 protocol](revisions/2026-10-04-r12/PROTOCOL.json).
4. [R12 reproduction and interpretation](revisions/2026-10-04-r12/README.md).
5. Generated `revisions/2026-10-04-r12/REMOTE_EXECUTION.json`, `results/AUDIT.json`, `TABLE_MANIFEST.json` and `build/` on the evidence/referee branch.

## Research changes

R12 adds direct common-path NBO-versus-direct-policy and NBO-versus-affine endpoints; an explicit finite initial-capital population; a continuous-state-history observation implementation with private null-space randomization; a costate-error/feasible-improvement bound; time-budgeted candidate generation; raw-costate and critic ablations; newly trained radius frontiers; full-path checkpoint and state-stress comparisons; an independent nonlinear one-state HJB reference; and a self-financed management-fee calculation. The existing title, original applications, historical adverse evidence and review reports are preserved.

A source branch specifies the computation. The evidence/referee branches add its executed weights, raw arrays, tables, compiled documents, source identity and audit. Numerical completion is not a positive economic finding. Direct method intervals may be inconclusive; population results are not uniform state-domain certificates or calibrated welfare estimates. The observation theorem assumes continuous noiseless capital history and exact known-drift integration, not discrete noisy observations.

## Reproduction

Use the pinned environment and commands in the R12 guide. The final workflow starts all numerical workers from one immutable source and does not use a post-run numerical recovery layer. Development failures and exploratory work are described separately in [DEVELOPMENT_LOG.md](revisions/2026-10-04-r12/DEVELOPMENT_LOG.md). The current results and test counts are in the generated audit rather than the obsolete September 28 ledger. The former root README and reviewed manuscript roots are archived exactly under `revisions/2026-10-04-r12/archive/`.

No successful repository workflow constitutes an Econometrica editorial decision.
