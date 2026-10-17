#!/bin/sh
set -eu
python3 - <<'PY'
import sys,numpy,scipy,fitz
print('Python',sys.version)
print('NumPy',numpy.__version__)
print('SciPy',scipy.__version__)
print('PyMuPDF',fitz.VersionBind)
PY
pdflatex --version | head -n 2
if command -v bibtex >/dev/null 2>&1; then bibtex --version | head -n 2; else bibtex.original --version | head -n 2; fi
