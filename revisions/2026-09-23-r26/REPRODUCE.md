# R26 reproduction

## Inputs and scope

Use a checkout containing R25 commit `c78d934c0b3b8d346a40c7ddcaf415e167462265`, then apply the R26 commit or patch. The standalone reproduction snapshot also supplies the R24 source and imported R25 scientific artifact. No external dataset is needed for the new tests. The root index is the only changed pre-existing file; its prior bytes are archived.

Python dependencies are NumPy, SciPy, SymPy, and CPU PyTorch. The local environment is recorded in `results/local_environment.json`; imported R25 timings have their own environment and are not treated as same-machine speed comparisons. LaTeX requires the retained class plus `latexmk`, `pdfpages`, `natbib`, `booktabs`, `longtable`, `microtype`, `hyperref`, and `xurl` from a TeX installation. No font files are distributed.

## Fast verification of frozen evidence

```bash
export PYTHONDONTWRITEBYTECODE=1
python revisions/2026-09-23-r26/replication/test_revision.py
```

The 11 tests include one symbolic identity, exact rational polynomial conversion, a floating automatic-derivative diagnostic, full-cover checks, online dominance/rollback/shadow invariants, original-model scope, bracketed tuning, and source preservation. Passing them does not establish the original 0.01 target or a stopped-gradient certificate.

## Re-execute new science

Preserve the frozen `results` directory before rerunning, or use a separate checkout. All six online trajectories and both fixed neural policies are specified in `PROTOCOL.md`; do not retune after examining outcomes.

```bash
export PYTHONDONTWRITEBYTECODE=1
python revisions/2026-09-23-r26/replication/online_stress.py
python revisions/2026-09-23-r26/replication/jet_certificate.py
python revisions/2026-09-23-r26/replication/publication.py
python revisions/2026-09-23-r26/replication/test_revision.py
```

Every attempted verification cover and every online candidate is saved. The initial long online invocation hit an execution timeout after completing seed 26101; seed 26102 was executed arm by arm with exactly the declared settings. The resulting six `record.json` files were combined without selection. This execution detail and the initial test-manifest path correction do not change the protocol or scientific policies.

`jet_certificate.py` reads, but does not refit, the R25 stochastic-reference actors. The direct certificate uses exact rational coefficients of the stored polynomial. The imported R25 experiment can be rerun with its own `PROTOCOL.md`, `FULL_STATE_PROTOCOL.md`, `REFERENCE_PROTOCOL.md`, and four replication scripts. Its results are not represented as newly executed here.

## Compile manuscripts

```bash
for d in ECTA_R26 SUPP_R26 RESPONSE_R26; do
  latexmk -pdf -interaction=nonstopmode -halt-on-error \
    -outdir=revisions/2026-09-23-r26/build "$d.tex"
done
```

The supplement includes the complete original R24 PDFs. It temporarily resets the class's negative one-inch offsets for `pdfpages` and suppresses new page headers; otherwise historical pages would be cropped or acquire a second page number. The final 151-page text-preservation audit is retained. Original PDF bytes are also preserved separately in `history/`.

## Preservation and scientific interpretation

`source_audit/R24_BASE_SHA256.json` covers 5,760 original archive files. The old root index is verified at its archived location after its required update. `source_audit/R25_IMPORTED_SHA256.json` covers 781 imported files relative to `revisions/2026-09-23-r25/`.

The numerical policies use saved binary64 weights as exact real numbers and displayed rational decoder constants. The interval certificates concern that mathematical policy, not unspecified deployment hardware rounding. The original economy's current full-domain bound is 7.181834580823298; the sub-0.001 bounds concern a separate manufactured stopped stochastic model. They must not be pooled.
