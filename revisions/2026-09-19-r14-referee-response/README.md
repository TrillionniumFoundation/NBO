# R14 referee package

## Reading order

Begin with **ECTA_R14.pdf**, the new main paper. **SUPP_R14.pdf** contains the complete new proofs and replication semantics (Sections S.16–S.21). **RESPONSE_R14.pdf** maps each principal referee comment to the changes. **COMPENDIUM_R14.pdf** joins the current paper and supplement with the unchanged R12 main paper, full historical compendium, and earlier S.1–S.15 supplement. The older theory, recursive-utility and game material, experiments, references, and adverse cases remain available rather than being silently cut.

The fixed report is `reviews/2026-09-19-econometrica-r13-certified-harsh/referee_report.md` at review snapshot `13c946c4e9a352612647cd75a6930c5d86d7a564`. It assessed science `dd9e0c755b743efdea2a7637f7620bb8ebc3b3c6`. R13 extension source `2db9996fee66a799870154bdc56d46dc80a89dc9` completed as deposit `59024a9bccfcc71feecec310b690fb181da44386` after the report’s freeze. We import it explicitly; we do not claim it was available earlier.

## Current evidence and scope

The canonical target is the stored-array manifest SHA-256 `54adb353c5b85210dca143aa7af44fb0b64023a6415be341cdb45e0953b0141d`. Continuous contract instruments are not continuous-state diffusion approximation. `replication/r14/output/continuum_certificate.json` and its NPZ archive establish a full fee cover, all-response executable lower bounds, rational upper inequalities, and per-term exclusions. The continuous result concerns exact best responses (eta zero); the original menu has its separate near-optimality and price-region certificate.

`economic_extensions.json` records the actual joint duration–surrender query gains, 54-point signed exposure map, and exact stored-row moment diagnostic. The imported `replication/r13/extensions` supplies refined menus, institutional counterfactuals, fitted proposals, and wider-law and lifting controls. Neural timings are historical executed measurements; they are not repeated-seed estimates. The independent receipt’s scope excludes neural performance superiority and diffusion inclusion.

## Authoritative review command

From repository root, install the recorded Python versions and standard TeX packages, then run:

```bash
python replication/r14/review.py
```

This checks the immutable release inventory, checks deterministic table content against the deposited data, independently verifies the numerical/economic objects, and compiles all four PDFs in a temporary source view. It never calls the target constructor or science producer. `--integrity-only` is a fast checksum/table check; `--compile-only` builds the documents without repeating the dynamic reconstruction. Neither shortened command substitutes for the full scientific check.

## Explicit scientific regeneration (not review)

```bash
python replication/r14/replay.py
python replication/r14/economic_extensions.py
python replication/r14/verify.py --receipt /tmp/r14-validation.json
python replication/r14/build_tables.py
```

Replay regenerates only a sufficient set of discovery queries and rational fee cells from `blueprint.json`. The blueprint contains query parameters, interval boundaries, and nonnegative dual proposals, not desired values or bound conclusions. The actual dynamic values, supports, inequality coefficients, and residual-charged rational bounds are recomputed. A proposal is not a trusted certificate: every coefficient, multiplier sign, and stationarity residual is checked independently. Reusing dual proposals avoids reliance on a fresh floating-point optimizer status on nearly degenerate cells. The independent checker uses different dynamic and LP-semantic implementations. A new scientific generation changes the objects and requires a new release seal; it must not be mistaken for checking the old one. `continuous_fees.py` is also retained for a fresh adaptive discovery run, including failure when the requested tolerance cannot be met.

## Identity and preservation

The release manifest hashes the reviewed report, relevant source and target files, output arrays, exact rational certificates, paper inputs, tables, PDFs, and execution receipts. Source SHA and deposit SHA are separate. A subsequent Git commit identifies the final immutable tree; the manifest does not claim to contain its own commit hash. Historical PDF copies are verified byte-for-byte against the R12 artifact by `historical/provenance.json`.

The current manuscript uses the unmodified Econometric Society `econsocart` class. The original template README and index are preserved in `historical/`. The root historical manuscript remains untouched. No statement of journal acceptance or official review appointment is made.

## Reproduction correction

The first R14 remote reproduction attempt (run `35419322937`) stopped at a floating-point LP infeasibility status and did not deposit verified results. The current replay separates a proposed dual multiplier vector from its exact weak-duality bound. It recomputes the latter against the freshly evaluated target. The completed release records its own source, execution, and independent verification, rather than treating the failed attempt as evidence. The original failed workflow remains in the development history.
