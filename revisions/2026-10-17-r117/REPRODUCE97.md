# Reproducing R97 without overwriting the published evidence

This guide supplements the short command list in README97.md. It records the log redirections required by the release gate and uses a separate source-only worktree. The main campaign deliberately refuses to overwrite a completed CAMPAIGN97.json. A rerun is a numerical reproduction, not additional independent statistical evidence.

## Exact source

The primary experiment source snapshot is 19a708620bad5063076904aeced5d8c49e50cc16 on revision/econometrica-nbo-r97-source-frozen-2026-10-14. The earlier protocol is 673d29e48922ae59908cdde245f312e077442539. The study97.py hash must remain db947fbbe20a92f38d8b5b95e4f5d733f8a3162df30d2f670e13a472b493baba. The review and all old scientific branches remain unchanged.

From an existing NBO repository checkout with access to the remote:

```sh
set -eu
git fetch origin revision/econometrica-nbo-r97-source-frozen-2026-10-14
git worktree add --detach ../NBO-r97-reproduction 19a708620bad5063076904aeced5d8c49e50cc16
cd ../NBO-r97-reproduction
export NBO_SOURCE97=$(git rev-parse HEAD)
export NBO_SOURCE_COMMIT="$NBO_SOURCE97"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
cd revisions/2026-10-14-r97
python3.13 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements95.txt
mkdir -p audit97
python code/run_tests95.py --output-dir audit97/inherited-tests > audit97/INHERITED_TESTS97.log 2>&1
python new/test97.py > audit97/NEW_TESTS97.log 2>&1
python new/study97.py campaign > audit97/CAMPAIGN97.log 2>&1
python new/independent97.py > audit97/INDEPENDENT97.log 2>&1
python new/forensic97.py > audit97/RECONSTRUCTION97.log 2>&1
python new/report97.py > audit97/REPORT97.log 2>&1
python code/build97.py > audit97/BUILD97.log 2>&1
python new/release97.py > audit97/RELEASE97.log 2>&1
```

Run this block in a shell with `set -e` or stop at the first failing command. The Python version used by the remote job is 3.13.5. The build also requires pdflatex, BibTeX, Pandoc and pdfinfo; the Ubuntu workflow installs texlive-latex-extra, texlive-fonts-recommended, pandoc and poppler-utils. Historical tests need the original sibling revision code directories, R62 inputs, R73 results73 and the R77 results77/summary.json fixture. The workflow's sparse-checkout list is the reference when using a partial checkout; a standalone copy of the R97 directory is not a complete historical test environment.

The worktree is new and separate from the published results. Do not delete failed cases, old CI receipts or completed campaign files to force a favorable rerun. Keep the new timing processes sequential and separate from tests and independent replay. Do not pool clocks across hosts. The observed ranges are descriptive conditional inputs, not confidence intervals for future machines or monetary welfare estimates.

The remote build gate checks compilation, unresolved references and overflow. VISUAL97.json is a separate human-readable inspection record for the exact delivered PDF hashes. A newly rebuilt PDF must receive its own inspection receipt; an old visual receipt does not certify different bytes.
