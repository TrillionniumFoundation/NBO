# R8 replication

From the repository root, with Python 3.13 and the pinned NumPy/SciPy versions:

```sh
python -m pip install -r replication/r8/requirements.txt
bash replication/r8/run_all.sh
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build-r8 ECTA_R8.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build-r8 SUPP_R8.tex
python replication/r8/build_report.py
```

`numerical_core.py` loads unchanged, explicitly inventoried numerical AST definitions from the preserved R4, R6, and R7 source files. It does not import the unused neural-training runtime or rewrite their formulas. The three historical proposals are read as frozen policies. `model.py` constructs identical sparse finite transitions, independently checks every CSR block against weighted gathering, and supplies selected-control direct replay. Large kernels remain blockwise to avoid duplicating a complete concatenated CSR matrix.

`spatial.py` keeps eight dates and 33 preference tiers, uses exactly the union of both common meshes, and separately records full-menu wealth-prolonged proposals. Each grid contains all original corners and the center for both regimes and both menu treatments, local frontier brackets, and a common nested-region certificate. `mechanisms.py` retains all 144 reoptimized class values and fixed-policy counterfactuals. `primitive.py` retains the reviewer counterexamples as well as checks of the analytically robust family. `validate.py` implements an independent dense conditional-count recursion for the new paired streaming code.

`certificate.py` compares chord, count, and a mesh-only lower bank on one common full target. Setup, optimization, evaluation, auditing, and replay are charged. These are serial single-pass timings, not a universal speed claim. Historical neural training is a sunk common target-construction input, not newly executed or silently charged as zero-cost learning. Arithmetic is round-to-nearest relative to stored finite arrays; `arithmetic.py` separately propagates signed-correction error and checks the 1e-7 per-class allowance. Neither replay nor this allowance certifies diffusion or kernel-construction error.

The 145-node run is memory intensive. The source uses blockwise CSR storage and no neural runtime; the workflow provides a larger-memory runner. Any earlier memory-limited local attempts are not counted as completed evidence. Only complete JSON outputs passing the build audit generate manuscript tables.
