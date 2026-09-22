# Neural Bellman Operators — R12 referee entry

**Branch:** `revision/econometrica-r12-uniform-cost-certification-2026-09-22`  
**Complete base:** R11, `85e27ad0c9cdcb68645d62788e1fad2f59ea1a48`  
**Latest referee report:** `251ad29668788b2a911c4ca6f9c0a226886518d6`, blob `42cee0954515e5578dc579a4ca0428bb4e399b2e`.

## Read

- [Complete main paper](ECTA_R12.pdf) and [ordinary LaTeX source](ECTA_R12.tex).
- [Complete preservation supplement](SUPP_R12.pdf) and [source](SUPP_R12.tex).
- [Fourteen-point response](revisions/2026-09-22-r12/response_to_referee.md).
- [Exact rational continuum certificate](revisions/2026-09-22-r12/results/envelope.json).
- [Refinement frontier](revisions/2026-09-22-r12/results/frontier.json), [all planned attempts](revisions/2026-09-22-r12/results/refinement_history.json), and [interruption archives](revisions/2026-09-22-r12/archive/).
- [Validation](revisions/2026-09-22-r12/validation_report.json), [independent replay](revisions/2026-09-22-r12/ci_results/status.json), and [immutable publication identities](revisions/2026-09-22-r12/publication_receipt.json).

## New result

Eighteen frozen policies, with fifteen newly constructed price certificates, give **regret at most 0.009994024846927508 for every real adjustment cost in [0.5,8]**, at `(t,u,x)=(0,2,1.25)`. The full original adaptive control set, payoff and first-exit contract are retained. A finite exact rational envelope test certifies the entire parameter interval; checking only the eighteen node prices would not suffice. The manuscript includes the full theorem, conditional finite-refinement proof, all cost-transfer signs, stopped expenditure bounds and economic interpretation. Every R11 main-text line is retained in order; earlier sources and full PDFs are preserved.

## Reproduce

Use Python 3.11, `numpy==2.3.5`, `mpmath==1.3.0`. Repeating policy fitting also uses `scipy==1.17.0` and CPU `torch==2.10.0`.

```sh
python revisions/2026-09-22-r12/replication/make_tables.py
python revisions/2026-09-22-r12/replication/test_revision.py
# Replay all frozen policy and dual enclosures; no retraining:
for group in 0 1 2 3 4 5; do
  python revisions/2026-09-22-r12/replication/recheck.py --group "$group"
done
python revisions/2026-09-22-r12/replication/recheck.py --collect
bash revisions/2026-09-22-r12/replication/build.sh
python revisions/2026-09-22-r12/replication/validate_revision.py --require-ci
```

`price_envelope.query("4.1234567890123456789")` accepts an exact decimal price and returns a stored actor path, value enclosure and rational regret bound without retraining. The new study is adaptive mathematical verification, not a newly preregistered external performance experiment. Local development and interrupted attempts retain their original provenance; the separate pinned clean-checkout replay is the execution check for the final package.
