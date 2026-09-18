# R12: canonical targets and witness-driven procurement verification

The authoritative main is `ECTA_R12.tex`; `SUPP_R12.tex` contains complete S.1–S.14 plus new S.15; `COMPENDIUM_R12.tex` retains every inherited R11 main-paper scientific input. The response and preservation map are in `revisions/2026-09-18-r12-procurement-witness/`.

## Check the committed target

Use Python 3.13, NumPy 2.3.5 and SciPy 1.17.0. From the repository root:

```sh
python replication/r12/verify.py
```

The default loads every date's committed canonical arrays, checks the immutable expected identities, independently reconstructs mathematical witnesses and writes only `output/independent_validation.json`. It does not run the primitive constructor or overwrite `output/expected.json`. The original R11 manifest is untouched.

For a separate full witness reconstruction on exactly the same canonical inputs:

```sh
python replication/r12/science.py --out /tmp/nbo-r12-replay
python replication/r12/verify.py --out /tmp/nbo-r12-replay
```

The output directory must not exist. A replay seal identifies the replay witnesses and does not replace the committed expected seal. Both sets can be checked against the same committed target. Wall-clock measurements need not be byte-identical.

## Explicitly create a different target

```sh
python replication/r12/science.py --build-target --target /tmp/nbo-new-canonical --out /tmp/nbo-new-witness
python replication/r12/verify.py --target /tmp/nbo-new-canonical --out /tmp/nbo-new-witness
```

Both directories must be new. This explicit operation runs the inherited constructor and freezes a separately identified target. It is not described as exact R11 or R12 reproduction. Primitive differences against the retained R11 manifest are listed separately; agreement or small differences do not constitute an operator-transfer proof.

## Verifier scope

`engine.py` independently implements Bellman optimization, first-date knot optimization, selected-policy polynomial construction, Bernstein restriction and both upper recursions directly on canonical rows. `verify.py` does not call the generator's `solve`, `upper`, `region`, `dominance` or coefficient routines.

The check reconstructs every regional lower-policy coefficient and feasibility condition, all upper corner recursions, fixed-policy extrema ordering, complete feasible support and signed transport, all 288 procurement continuation-parameter queries and both initial classes, all-response service and participation bounds, price-box and pointwise menu selection, opportunity exposure and broader-law precision diagnostics. Timings are measurements, not independently equal cross-machine quantities.

Disposable tests reject the referee's destroyed upper array (`-1e6`), invalid policies, stale summaries, altered continuation enclosures, negative/excess transition mass and wrong target identities. The destroyed coefficient has both a file-identity and a semantic interval test.

This is separately recoded binary64 witness reconstruction plus the analytic error allowance, not a second real-interval implementation, neural retraining, an audit of every possible software fault or a diffusion-target certificate. Nominal policy moments are not substituted for service bounds covering every exact or `1e-8`-optimal economic response.

## Build

After successful verification, with the repository's Econometric Society LaTeX class and PyMuPDF installed:

```sh
python replication/r12/materialize.py
python replication/r12/build.py
```

`materialize.py` creates the new wrappers and bibliography from preserved inputs; it refuses to replace an existing nonidentical generated source. `build.py` creates tables from checked witnesses, compiles the main, complete compendium and supplement, checks references/overflows and PDF text, renders inspection pages, and prepares an execution/preservation receipt. The canonical archives themselves are committed with the revision, not left only in an expiring workflow artifact.
