# Neural Bellman Operators: R119 reproduction and evidence protocol

This is an author revision of **Neural Bellman Operators** for the Econometrica numerical methods direction. The original recursive investment objective, implemented future controller, feasible actions and original continuous innovation law determine every current policy-cost statement. This document separates the reconstruction of recorded evidence from a new execution. It also preserves the independent experimental commitments of the earlier research episodes.

## Scientific identity

The latest complete author baseline established by native dependencies and content is R110, commit `4ba2bbaa11b5fa59f83705b28b35bf82a63ca169`, revision tree `5885983fdef89cdc11fe471753cccfa46160956f`. Its main source SHA-256 is `565666c40cdb321322adbdfb45c4d225cb5748a60f6981d18b2cf4ac872b80a9`. The 184 native manuscript dependencies were restored and verified before modification. Original master wrappers are retained under `retained110/wrappers/`; the remaining old manuscript sources are preserved under their existing paths. The retention map records their actual current roles.

The controlling persisted substantive advisory report is at commit `9723c6cd2cc8b3e071422f3e522d4a843946db63`, report blob `33ba8b144e2f7816b19b036404341402d23a582f`, reviewing author commit `f802fe64d91d9f5c1c8f86123b0fbe114e622279`. It is an owner-commissioned advisory report and is not a Society editorial decision or a report on the subsequently completed R110 or R119 manuscripts. The branch, report and historical response registries preserve every report identity and the continuing requirements.

The later R118 compressed source delta is truncated and is not a complete manuscript. Independent R98 selected-actor, R115 actor/sample and other frozen or unfinished episodes retain their own protocols. No current deterministic catalogue is described as their missing independent sample. The R117 and R118 programs reproduced on this host are explicitly unchanged-source reproductions.

## Current experiments

| Phase | Immutable execution source | Services | Primary decisions | Seven-process timing decisions |
|---|---|---|---:|---:|
| A | `1f33c2667e0dff89699c6d6a01d03eacfecf3f4e` | Compiled, geometric, active tail | 6,912 | 10,752 |
| B | `357b2c56727cd57b9696cd6e07e115a35f5fdedb` | The three A controls, masked tail, budgeted tail | 11,520 | 17,920 |
| C | `095936f1a7556d90d74809e63d75d9959d118360` | The five B controls, packed tail | 13,824 | 21,504 |

Each phase has its own protocol and source freeze (`PROTOCOL119.md`, `PROTOCOL119B.md`, `PROTOCOL119C.md` and the corresponding `SOURCE_FREEZE` JSON). The exact code/protocol hashes remain unchanged after execution. Phase B was developed after observing phase A's negative work comparison; phase C after observing phase B's overhead. These are prospectively committed implementations on the same already observed deterministic catalogue. They are not unseen selection-validation samples, and no phase substitutes for another phase's clocks.

All eight representations are retained: online semi-analytic Bellman, rank-six quadratic, ReLU, the equivalent ordinary hinge representation, coordinate spline, full quadratic polynomial, cubic polynomial and tensor-grid interpolation. Every service compares the same proposed complete policies in the same two-date economy and has the same certificate targets: policy regret at most `1/256` and value-interval width at most `1/8192`. The future-controller allowance remains `2**-20`. Original-policy reference intervals distinguish policy cost, regret bounds and action-distance bounds, with the independent-partition/shared-compiler scope specified below. The reported bounds are not exact regret observations.

The numerical catalogues are deterministic. They do not support population confidence intervals. Seven separate timing processes characterize observed machine variation; all seven clocks, ranges and paired comparisons are reported without a timing confidence interval. Any future independent randomized experiment needs its own frozen sampling protocol, sample independence and statistical analysis before its outcomes are observed.

## Restore and verify the actual evidence

Use a Git checkout with the immutable experimental commits available. The frozen preflights compare actual bytes with `git show <prospective-commit>:<path>` before scientific imports. A downloaded document package alone does not manufacture those Git objects. A sparse checkout avoids downloading unrelated historical working trees:

```bash
git clone --filter=blob:none --sparse --branch revision/econometrica-nbo-r119-active-tail-author-revision-2026-10-18 https://github.com/TrillionniumFoundation/NBO.git NBO
cd NBO
git sparse-checkout set revisions/2026-10-18-r119
cd revisions/2026-10-18-r119
python -m pip install -r requirements119.txt
```

Run commands from this revision directory. The evidence is divided into byte-preserving transport parts so the complete raw record can remain in Git without a large-file service. Under `evidence119/`, `ARCHIVE_PARTS119.json` records the unchanged A/B/C and R110 containers, and `VALIDATION_D_ARCHIVE_PARTS119.json` records the separate D container. Each gives all part hashes, concatenation order and the container hash; the three member manifests give every archived path, size and SHA-256.

```bash
python archive119.py verify
python archive119.py extract-current --destination .
python archive119.py extract-validationd --destination .
python archive119.py extract-r110 --destination recovered110
```

Verification reconstructs the archive in a temporary directory, checks every part and container hash, and reads every regular member body. Extraction rejects absolute paths, traversal and non-regular archive members. It never overwrites an existing file: an existing member must already have the exact declared bytes. The complete current archive includes every primary/timing record, acquisition and reference record, failed attempt, command log, unchanged-source reproduction and complete read-only reporting output. Neither archive selects by whether an outcome is favorable.

The recovered R110 archive contains all 1,418 members absent from the immutable 8,218-file source export. Those generated members include the original execution manifest, all original generated scientific outputs and originally logged PDFs. The original source export and original Git object identities remain available, allowing the generated delta and original source tree to reconstruct the selected original package. The full original artifact custody receipt lists all twelve omitted bytecode caches. No scientific file was omitted by that cache rule.

These commands recover recorded evidence. They do not rerun an economic method. Current raw file counts and container hashes are in `evidence119/CURRENT_RESULTS_ARCHIVE119.json`; the original R110 generated-file account is in `evidence119/R110_GENERATED_ARCHIVE119.json`.

## Replay exact record audits without changing archived observations

The three native auditors use standard-library exact rational arithmetic on the saved binary64 endpoints and trace identities. They do not import the production fit, actor, risk or interval implementations. To preserve the originally recorded audit receipt, replay them in a fresh extraction directory:

After installing the pinned requirements below, use the package validator:

```bash
python verify_package119.py --output verification119/attempt01
```

It verifies all three complete archives and the complete portable historical index, extracts an isolated observation copy, and preserves that copy's original A/B/C audit receipts separately before asking the unchanged auditors to create new receipts. It also replays D's saved exact aggregation through the portable read-only reporter, checking all 49 immutable source files and 97 original inputs. The declared fused-tail exact fixture suite and original-proof algebra have separate stages. No stage reruns a primary policy campaign, the 983-policy independent solve or a competitive performance clock. Every attempted wrapper run has a fresh output directory and retains its command status, log hash and any launch/timeout failure.

The original successful native audit counts are 444,053, 1,031,933 and 1,325,935, respectively. Complete mathematical validity follows from the stated continuum proofs and outward implementation assumptions; a finite record check is not a replacement for those proofs. The separate reporting and packing-identity checks have their own source hashes and receipts, and do not create further independent economic observations.

## Execute a fresh experiment

The actual host used CPython 3.12.14, NumPy 2.3.5 and SciPy 1.17.0, with one numerical-library thread. The exact runtime/environment records are inside each campaign. The pinned requirements also include plotting and the historical streaming parser; these are separate from the economic evaluator. Use a fresh virtual environment when installing the requirements.

```bash
python -m pip install -r requirements119.txt
```

Retain Git history for the three immutable execution commits, because preflight checks compare each declared file to its committed source before importing scientific code. The fresh output locations below must not contain a previous experiment. If an execution fails, preserve that directory and use a new attempt directory; do not erase it or selectively resume the favorable cells.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
NBO_SOURCE119=1f33c2667e0dff89699c6d6a01d03eacfecf3f4e \
python code119/independent_tail119.py audit \
  --custody-commit 1f33c2667e0dff89699c6d6a01d03eacfecf3f4e \
  --output fresh119/A-preflight

OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
NBO_SOURCE119=1f33c2667e0dff89699c6d6a01d03eacfecf3f4e \
python code119/campaign119.py all --output fresh119/A-campaign
```

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
NBO_SOURCE119=357b2c56727cd57b9696cd6e07e115a35f5fdedb \
python code119/independent_budgeted119.py \
  --custody-commit 357b2c56727cd57b9696cd6e07e115a35f5fdedb \
  --output fresh119/B-preflight

OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
NBO_SOURCE119=357b2c56727cd57b9696cd6e07e115a35f5fdedb \
python code119/campaign119b.py all --output fresh119/B-campaign
```

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
NBO_SOURCE119=095936f1a7556d90d74809e63d75d9959d118360 \
python code119/independent_fused119.py \
  --custody-commit 095936f1a7556d90d74809e63d75d9959d118360 \
  --output fresh119/C-preflight

OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
NBO_SOURCE119=095936f1a7556d90d74809e63d75d9959d118360 \
python code119/campaign119c.py all --output fresh119/C-campaign
```

Run each corresponding native record audit on its fresh campaign directory. Every fresh experiment must retain the complete state/arm/risk/service catalogue, fresh acquisition and references, all seven process clocks and actual outer command logs. Do not use the original recorded elapsed times as if they had been reproduced on the new host.

The preflight intentionally repeats the same declared 22,220 diagnostic checks. It is not a fresh random validation sample. The original phase-B first attempt stopped before scientific imports because a transport normalized a predeclared CSV's CRLF bytes. The exact bytes were restored in the successful source commit; the failed preflight remains in the current archive. No protocol, parameter, sample or algorithm was changed to obtain that transport repair.

## Independent original-policy validation D

D has a separate immutable execution source, `cafd38aedc5bcbddf5aafee2481fbf5e9a267bab`. `PROTOCOL119_VALIDATION_D.md`, `VALIDATION_D119_KEYS.json` and `VALIDATION_D119_MANIFEST.json` were committed before its first economic evaluation. The design was made after A/B/C results were known: all 983 actual C state/action/risk keys are included, with exact binary64 identities converted to their precise rational values. The fixed protocol uses 64 whole-support cells and 32 terminal bisections, with no selected subset, adaptive precision or favorable-sign condition. Its pre-execution status fields remain intact; later event, summary, execution and external launcher receipts establish completion.

The standard-library program reconstructs the original economic primitives, exact quadratic terminal shock cost, continuous AVaR and feasible strong-convexity node bounds. The supplement proves the outer hinge-convexity enclosure and the single `beta * 2^-20` implemented-future allowance. D imports no production terminal compiler. It encloses the original policy value without directly evaluating the floating future controller or determining a new global action optimum or regret certificate.

The actual run passed all 983 keys, 126,807 terminal contexts and 652,774 checks, with 1,697.331508 elapsed seconds and 1,693.603548 CPU seconds. The subsequent read-only reporter passed 590,818 checks in 7.705036 seconds. These two separate scopes have their own receipts. Their 1,003 files contain 60,150,443 uncompressed bytes; the six-part container is 49,644,124 bytes with SHA-256 `89ccf40eb1bbb470369df479e6441946ef4ef83587d139bd1f0d05a0607ec127`. The original A/B/C and R110 containers are unchanged.

For a read-only replay, restore the current and D records into one isolated destination:

```bash
python archive119.py extract-current --destination /tmp/nbo-r119-evidence
python archive119.py extract-validationd --destination /tmp/nbo-r119-evidence
python code119/analyze119d.py --revision "$(pwd)" \
  --evidence-root /tmp/nbo-r119-evidence \
  --output verification119/D-record-replay01
```

This checks all 49 committed source files, 97 original inputs, every saved primitive stream, 96 means, 56 contrasts and 240 service-pair identities. Its output audits old observations; it does not rerun an economic solver.

To reproduce the independent solve, restore the frozen C inputs into this revision and choose fresh scientific output and external log names:

```bash
python archive119.py extract-current --destination .
python provenance/execution_tools119/run_command119.py \
  --root "$(pwd)" --stage validation119d-reproduction01 \
  --source cafd38aedc5bcbddf5aafee2481fbf5e9a267bab -- \
  python code119/independent_catalogue119.py \
  --custody-commit cafd38aedc5bcbddf5aafee2481fbf5e9a267bab \
  --output results119/validation119d_reproduction01
```

The unchanged external recorder is preserved by SHA-256 `bfd2fcc8d99a0e5d611b92f4ba291831b3ed19f4da4d8a4c32e7e19aaf4a6a6a` at its published location. A fresh run's costs and outcomes belong to that execution. Keep every failure directory and the original key/input bytes intact.

All 56 economic comparisons remain: 32 negative, 20 positive, two exact-zero and two unresolved. Independent ReLU-minus-quadratic intervals are `[17.4360,19.2238] * 10^-6` and `[17.5331,19.3595] * 10^-6`, both adverse to ReLU. All 983 finer shared-compiler reference intervals are contained within D's enclosures; this direction does not establish those fine endpoints. Both unresolved Q/P2 contrasts remain unresolved. ReLU/hinge and every service change within an arm have exact-zero economic effects.

## Complete work and adoption interpretation

The full component tables charge fresh standalone information acquisition, fitting and fit audits, actual model loading, proposal work, all attempted certificates, rejected candidates, fallback and serving. Original-policy references are separately paid and identified. Their 1,024-bin partition is independent of the qualification mesh, but they share the verified production terminal compiler. The exact-rational primitive suite independently reconstructs 24 original reference cases and 72 certificates; this does not constitute a fully independent implementation of all 983 distinct catalogue references. The measured 32-decision service clock starts after the separately recorded load; interpreter/source/process startup has broader recorded boundaries. The outer campaign clocks and actual loading records remain available. Do not silently combine incompatible timing scopes or compare a new host's narrow kernel time with a different phase's complete workload.

Phase C's packed service beats the geometric control in ten of sixteen contemporaneous median cells and loses in six. It beats its budgeted control in all sixteen median cells but loses two complete 144-state service comparisons. These two workloads have separate observations. All service policies are identical within an arm, giving exact zero original economic contrast across services. The quadratic control still has the better original mean economic cost and complete component cost than ReLU at both risks. ReLU and ordinary hinge give identical policies and information. None of these facts certifies neural-exclusive representation or calibrated adoption.

The main text's economic adoption inequality combines a stated value of original-policy improvement with a stated price of complete computational resources. A result on a different recursive utility, information set, horizon or economic technology cannot be entered as an improvement in this investment objective. The Brownian recursive-utility result has its own driver, information, regularity, terminal and stopping-boundary assumptions. The original-correctness companion preserves the earlier incorrect claims and their counterexamples or corrected algebra.

## Build and inspect the four English documents

The native main uses the repository's Econometrica class and bibliography style. A TeX installation needs the LaTeX extra/recommended, Palatino and standard mathematics/font packages, BibTeX and PDF utilities. The builder does not regenerate historical source or execute a scientific experiment.

```bash
python build119.py
```

This compiles `ECTA.pdf`, `supp.pdf`, `appendix.pdf` and `RESPONSE_TO_REFEREE.pdf` under `build/`, resolves external document references, records actual command logs and PDF hashes, and fails on unresolved references, overfull boxes or integration placeholders. A fixed `SOURCE_DATE_EPOCH` controls PDF build dates; the receipt separately records actual wall-clock execution. Different TeX/font distributions can produce different PDF bytes, so the published source/PDF identity manifest is authoritative for the distributed package.

The main gives the current economic question, own-future NBO construction, original-law certificates, action-dependent information result and full current empirical interpretation. The supplement contains the complete proofs. The development companion retains the historical models, credible theorems, proofs, illustrative failures, all comparison tables and every historical author response. The response document addresses the controlling report's thirty numbered requests. The historical section registry and detailed major/minor/actionable-section maps retain the broader report coverage without implying wholesale closure.

## CI and preservation

Remote CI receipts identify the exact workflow commit, job, source and executed commands. A queued workflow, transport-only custody operation, archive verification or local build is not labeled a successful remote economic experiment. The final package records these scopes separately. The historical source reader checks immutable content and safely parses declared formats; it does not execute historical code or unpickle saved arrays. Its exact coverage, retained transport failures and retries are in the historical custody receipts.

Only the new isolated R119 branch is changed. A final head comparison retains all 359 original branch heads unchanged and records the single added revision branch. Historical unfavorable results and unfinished independent protocols retain their original identities. The current mathematical and numerical improvements continue the original NBO research program; unproved neural-specific advantages and unexecuted applications remain explicit scientific requirements.
