# Neural Bellman Operators — R21 referee copy

Canonical reading order: `ECTA_R21.pdf`, `SUPP_R21.pdf`, `RESPONSE_R21.pdf`. Editable sources have identical names; the new material is in `revisions/2026-09-23-r21/paper/`.

New source branch: `revision/econometrica-r21-policy-sensitive-2026-09-23`. The final publication is also pinned on `revision/econometrica-r21-referee-copy-2026-09-23`. Neither main nor prior review/revision branches is modified.

## Exact basis

Initial report: `reviews/2026-09-23-econometrica-r18/referee_report.md`, review commit `074849b9aad1812b59e25e1d3833383ed11aa401`.
Inherited R20 head: `6916f250ca2115399dccf2df125c0b13f304547b`.
Confirmatory protocol: `238ecc0052dc418e1fe6fd06c3daa4a93da1a335`.
Executed R20 science: `b1a2ea39d895b330e5a11b4e55d86b7a4985b101`, Actions run 35802793602.
R21 materializes the missing R20 stochastic-policy manuscript, adds new continuum and price proofs, and independently replays frozen policies; it does not claim new randomized R21 training.

Additional report discovered during this revision: `reviews/2026-09-23-econometrica-r21/referee_report.md`, commit `bc118f20f6361cdeae668141e45f64c436ee6a2a`. It reviewed the intermediate `6951c3b` snapshot. The combined response also addresses every R21-F0–F10 and R21-T1–T12 item, with an explicit R22 gate ledger. The new restricted-Markov-realization proposition and representation audit are in the main text.

## Main results

For five trained stochastic neural mixtures, the original-economy regret is below 0.002909 throughout K=[1.98,2.02] x [1.24,1.26], at time zero and k=2. An explicit upper bound on the initial mixture's Jensen gain proves actual payoff improvement at least 0.01762319 uniformly on K, and more than 85.8 percent pointwise true-regret reduction.

With the same fixed policies, a piecewise-affine price transport theorem gives regret below 0.003327 on K x [1.5,2.5]. The result is uniform in both state and price, not a sampled-grid assertion.

The self-financing decoder is proved admissible on every traded-factor path. Neural consumption is stochastic and the portfolio is nonzero. A budget-financed increment of 0.002 initial wealth is sufficient compensation for each learned mixture on K. A direct stochastic non-neural comparator reaches a sharper final regional bound (below 0.002839) and is faster at the first matched tolerance; it is not concealed. The neural mixtures uniformly outperform three named deterministic policies in actual payoff, not all non-neural solvers.

## Evidence and scope

The full response covers F0–F11, T1–T10, and R19-A–F. The current global 0.01 objective, original model and author attribution are retained. K at time zero is not all D and all starting times. A global sharp continuation upper witness and matched global MC/SL frontier are not certified by these local results. The original full-domain 7-unit feedback certificates, their critic-driven decomposition, all-seed swaps, trace diagnostics and high-dimensional classical advantages remain available.

`results/replay_summary.json` records 136 new frozen-policy executions: 80 neural checks, 20 MPFR checks, 16 classical stochastic checks and 20 compensation checks. Final intervals use hulls, not favorable intersections. `results/continuum_audit.json` contains all directed bounds and cost ledgers. `PUBLICATION_MANIFEST.json` pins source, input/result identities, PDF hashes and bytewise preservation of inherited files.

## Reproduction

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python revisions/2026-09-23-r21/replication/replay.py
python revisions/2026-09-23-r21/replication/audit.py
python revisions/2026-09-23-r21/replication/representation_audit.py
python revisions/2026-09-23-r21/replication/build.py
```

The source transport payload is SHA-checked before extraction; the ordinary readable sources are committed alongside the compiled PDFs and scientific results. All 3,934 inherited file identities are preserved: 3,933 at their original paths and the old navigation index in `history/REVISION_INDEX_before_R21.md`. Updating the root index is the only intentional inherited-path edit.
