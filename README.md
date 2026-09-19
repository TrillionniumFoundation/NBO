# Neural Bellman Operators — Revision R14

**Current paper:** *Neural Bellman Operators: Certified Response Sets and Operating Commitments* (September 19, 2026).

This revision responds to the [frozen R13 referee report](reviews/2026-09-19-econometrica-r13-certified-harsh/referee_report.md). That owner-commissioned advisory report is not an official Econometrica editorial decision.

## Read the paper

[Main manuscript](revisions/2026-09-19-r14-referee-response/ECTA_R14.pdf) · [Current proof supplement](revisions/2026-09-19-r14-referee-response/SUPP_R14.pdf) · [Point-by-point response](revisions/2026-09-19-r14-referee-response/RESPONSE_R14.pdf) · [Complete preserved compendium](revisions/2026-09-19-r14-referee-response/COMPENDIUM_R14.pdf)

Editable entry points are `ECTA_R14.tex`, `SUPP_R14.tex`, `RESPONSE_R14.tex`, and `COMPENDIUM_R14.tex`. Detailed [reading order, scope, and reproduction instructions](revisions/2026-09-19-r14-referee-response/README.md) identify the current evidence. Root **`ECTA.tex` is historical**, not the current paper. No old manuscript, review branch, or theoretical section is deleted by R14.

## Central result

Finite value queries constrain joint dynamic response moments. The response-set theorem, robust procurement theorem, efficient-capacity result, and continuous-fee certificate form one economic argument. On the unchanged stored settlement economy, the original enforcement menu gives compulsory terms 3 versus 4; a 0.05 menu gives 2 versus 4; continuous fees identify term 1 in both regimes, with lower enforcement needed by the adjusted executable contract. The current paper retains all three findings and their distinct institutions.

The verification covers fixed-array arithmetic and all exact responses for the continuous calculation. It is **not** a quantitative diffusion-to-array inclusion result, a formal machine proof, or a demonstration of neural scaling superiority. The adverse neural benchmark and constructor variance diagnostic are retained.

## Review the frozen objects

```bash
python -m pip install numpy==2.3.5 scipy==1.17.0 pymupdf
python replication/r14/review.py
```

The authoritative command verifies the release hashes, reconstructs the deposited scientific witness independently, checks table identities, and builds the manuscripts in a temporary directory. It does not regenerate scientific results onto the branch. TeX Live with `latexmk`, the standard recommended fonts, and `texlive-latex-extra` is required for compilation.

The [release manifest](revisions/2026-09-19-r14-referee-response/release_manifest.json) and [independent validation](revisions/2026-09-19-r14-referee-response/logs/independent-validation.json) identify inputs, statements, checking scope, and output. Generation is separate from review. [Revision index](REVISION_INDEX.md) and [historical preservation record](revisions/2026-09-19-r14-referee-response/historical/provenance.json) retain the earlier chronology. The original template README remains [here](revisions/2026-09-19-r14-referee-response/historical/ROOT_README.md).
