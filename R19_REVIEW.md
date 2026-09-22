# R19 referee entry point — Neural Bellman Operators

## Current manuscripts

- Main paper: `ECTA_R19.tex` / `ECTA_R19.pdf`.
- Complete supplement: `SUPP_R19.tex` / `SUPP_R19.pdf`.
- Response to all R18 findings F1–F11 and comments T1–T10: `RESPONSE_R19.tex` / `RESPONSE_R19.pdf`.
- Revision source and complete new evidence: `revisions/2026-09-23-r19/`.

The title, original stopped economy, admissible action set, and full-domain 0.01 objective remain unchanged. New policy-sensitive neural results are not relabeled historical non-neural results.

## New scientific objects

Five freshly trained 1–16–16–2 tanh neural time-control generators have predeclared seeds 19100–19104 and work levels 0/50/200/800. Their training objective uses the original model payoff, no inherited actor/value labels. All 15 noninitial proposals pass the independent policy-payoff gate **before the next Adam update**. All five final reference-state regret bounds are below 0.01. A coupled-payoff theorem proves positive true policy gains uniformly on K = [1.98,2.02] × [1.24,1.26], at t=0,k=2. The new K-regret bounds are below 0.012 and imply at least 58% true-regret reduction uniformly; the reference-state reduction is at least 75%. These are a posteriori verified trajectory claims, not a universal Adam convergence theorem.

Fixed-policy interior continuation-value limits exceed settlement by more than 6.708 on the indicated upper-face preference segment. This is a constructive necessary target for an upper witness, **not a globally certified optimal upper witness**. A bias-only intervention on five old critics removes the pointwise necessary floor but worsens the full certificate; those adverse outcomes remain recorded.

The complete historical actor/critic factorial has 40 objects and all 30 trace checkpoints. A new finite-query study certifies 1,920 target plans at four tolerances, with zero/accelerated classical comparisons and explicit transferred-cost amortization. Learning reduces correction work in specified regimes, including 128 dimensions at tolerance 0.01; acceleration ties or wins at tighter tolerances. No universal neural necessity or 128-dimensional end-to-end speedup is claimed.

Fresh SLSQP transcriptions provide a same-accuracy reference-state comparator and direct policy comparison on K. A 0.0092 wealth increment (0.736% of reference wealth) finances sufficient compensation for the new neural policies on K. Historical non-neural compensation remains separate.

## Remaining full-domain requirements

The new time-control/state-transfer family is not the old full-state feedback architecture. The old full-domain best neural bound remains about 7.278; it is not declared 0.01. The new K bound is not rounded down to 0.01. A sharp full-domain optimal upper witness and a matched global MC/SL frontier remain unestablished. The paper retains these objectives and all prior content rather than substituting a narrower model or deleting adverse evidence. Numerical validation or PDF build success does not close these scientific gates.

## Reproduction

On a Linux CPU environment with Python 3.13, NumPy 2.3.5, SciPy 1.17.0, PyTorch 2.10.0 CPU, GCC, MPFR shared library, and TeX Live:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python revisions/2026-09-23-r19/replication/run_all.py
python revisions/2026-09-23-r19/replication/build.py
python revisions/2026-09-23-r19/replication/publication_manifest.py
```

Numerical results, all proposed networks, all compiled controls, checker cell records, all target plans, table-generation inputs, validation output, and logs remain under the revision directory. Tables are regenerated from those records. The inherited `econsocart` class is unchanged.

## Immutable provenance and preservation

- Latest R18 report: `074849b9aad1812b59e25e1d3833383ed11aa401`.
- R18 manuscript reviewed: `49d286a174a7d3f71293adc920284584673f390b`.
- Complete input archive: `b937ba65111cd2687401cb5d61d3fda3c5567bb5`.
- Pre-execution R19 protocol: `2e19256c5d40f7f0d090cccd6d86892958ae2147`.
- `PRESERVATION.json` checks every inherited tracked file against the review commit.
- `PUBLICATION_MANIFEST.json` distinguishes the source object from the publication commit containing the generated artifacts and hashes.

The main paper retains the substantive R18 sections and proofs. The complete prior supplements and the superseded R18 introduction/conclusion remain in the new supplement, clearly identified as historical exposition. The original manuscript PDFs, raw results, review reports, `main`, and all old review/revision branches are unchanged.
