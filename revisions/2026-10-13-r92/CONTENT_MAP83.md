# Neural Bellman Operators — R83 reading map

The active submission is `ECTA.tex`, `supp.tex`, `appendix.tex`, and `response.md`.
The title and all 35 previously active sections are retained in the same
compiled document with identical bytes.

Main additions: `sections/actionwise82.tex` proves actionwise class-cost
transfer; `sections/frontier83.tex` proves economic stopping for the continuum
of verified optimization tolerances; `sections/study83.tex` reports original-law
class gains, orderings and equivalence. New main tables round cost endpoints
outward and guaranteed tolerance endpoints inward.

Appendix additions: `sections/proof82.tex` gives complete-bin validity,
refinement and complexity with every declared discrete record;
`sections/proof83.tex` gives the exact monotone frontier algorithm and all target
and reference results; `sections/study82.tex` retains the full actionwise study.
The original unintegrated editorial files are in `preserved/R82-editorial/`.
The original failed audit and wrappers are in `preserved/R82-attempt-audit/`
and `preserved/R82-attempt/`. Historical companion editions remain preserved.

Numerical entry points: `code/replay83.py --execute` creates the first complete
source-bound R83 recovery; `code/replay83.py --full` independently regenerates
all paired bins. `code/frontier83.py` computes exact boundaries and checks every
stratum pair. `code/build83.py` runs the complete inherited and new pipeline.
`code/publish83.py` performs clean-archive reproduction without retiming the
stored execution. Visual qualification is a separate hash-bound final step.
