# R126 independent acquisition implementation audit

## Purpose and episode identity

This is a separately specified audit of the already published R121 acquisition datasets and 56 saved actors. It is part of the R126 author revision and directly addresses the acquisition-implementation component of R97 B8/M9. It does not acquire new original-economy labels, select new held-out observations, replace any current actor, or count a refit as a newly deployed policy experiment. Historical labels, coefficients, successes, failures and acquisition costs remain unchanged. The R126 production decision census retains the original frozen actors.

Historical acquisition source is `16bf21334efcbc719b83e2ccf10e8527f8b956f2`; complete actor-publication identity is `796c5f2badf68b051ac6c144884c0e61b87faf5e`. Input bytes were retrieved from the later complete immutable custody head `f6392f6909d280ecd310f152caab0fafe9091df7`, under `revisions/2026-10-20-r121`. `inherited_fit121/INPUT_MANIFEST126.json` pins the exact original path, Git blob, SHA-256 and byte length of each of 181 recovered files, and verifies that every one of the 56 model files is byte-identical to the R125/R126 frozen actors. The input set totals 9,823,176 bytes. This is a historical-data readback, not a prospective acquisition claim.

## Prospective execution boundary

The code `code126/independent_fit126.py`, this protocol, the input manifest and all bound input bytes must be committed on the new isolated R126 branch and read back before the first refit. The script requires an exact `--source-commit` and compares its full audit closure against that immutable commit before importing NumPy/SciPy or executing any historical fit. Only source inspection, syntax checks and abstract algebra/shape fixtures using synthetic constants are permitted before this boundary. No actual-label fit has been run when this protocol is written.

The complete audit is invoked once into a previously nonexistent attempt directory. Each raw solver result is written before exact objective certification. Failures retain the raw solver record, completed input checks, exception, elapsed work and any earlier results; later declared models continue to be inspected. There is no outcome-selected solver retry, deleted model or altered tolerance. An implementation correction, if necessary after F, must receive a separate failure record, explicit source delta, renewed immutable boundary and disclosure of which outcomes were already known.

## Exact complete input census and feature definition

The audit covers both original acquisition state-mesh sizes 5 and 9, both original risk levels 1/2 and 3/4, all seven representations, and both VALUE and MARGINAL objectives. These are 56 stored models but only 48 original/refit solver problems: the eight HINGE cases copy their corresponding paid ReLU readout. HINGE is never counted as an independent fitted observation.

The four label files contain the complete 2,756 original root Q label contexts and 1,060 main marginal contexts. The audit reconstructs the original 13 normalized-action probes and complete state grids, checks their ordering, and reads identical value and derivative interval payloads for every representation. It performs no new root-risk or terminal-primitive evaluation. Label validity continues to rely on its original separate primitive proofs and recorded economic audits.

Feature specifications are reconstructed from `PROTOCOL121.md`, not inferred by importing production functions. They include the four anchored quadratic/degree-two monomials, ten degree-three monomials, 36 fixed oblique hinge units plus three base terms, clamped tensor cubic B-splines and tensor linear hats. Exact rational feature evaluation uses monomials, explicit hinge branches, a separately written Cox–de Boor recurrence and explicit hat interpolation. Derivatives are in original-action units, dividing by the exact capacity. Every required feasible one-sided branch at an interior switch and inward endpoint is assembled independently.

The complete serialized basis, exponent/order lists, knot sequences, coefficient bounds and feature counts are checked against the original pre-label specification. R121 performed no learned hidden-feature selection or held-out hyperparameter search; verifying a fixed predeclared feature list does not become a new learned feature-selection algorithm.

## Independent numerical solve and disclosed shared dependencies

For VALUE, reconstruct the matrix independently from exact rational features and convert to binary64 for candidate generation. Solve the same boxed least-squares problem with SciPy's **BVLS active-set algorithm**, tolerance 1e-12 and at most 1,000 iterations. The historical implementation used SciPy's TRF algorithm. This supplies an independently assembled optimization path and different numerical algorithm, while sharing NumPy/SciPy numerical infrastructure. The candidate is not claimed to be an independently implemented linear-algebra library or an exact optimum.

For MARGINAL, independently formulate the same robust finite-node problem in shifted variables `z = theta - lower`, with `0 <= z <= upper-lower`. Form both robust inequality blocks and their shifted right-hand sides explicitly, with nonnegative epigraph variable. Solve using SciPy's explicit **HiGHS dual-simplex** route, presolve enabled, primal and dual feasibility tolerances both 1e-9. The original solver also used HiGHS. Therefore this is an independent problem assembly and candidate generation path, **not an independent LP-solver implementation**. The subsequent rational validity does not rely on floating stationarity or the solver success message.

A solver reports success only for its own numerical algorithm. All full raw coefficient vectors, multipliers, statuses, messages, iteration counts and solve clocks are retained. No result chooses a family, loss, box, tolerance, rank or precision after inspection. The declared coefficient box remains 128, with the original nonnegativity restrictions on the quadratic curvature and ReLU/hinge nonlinear readouts.

## Rounding, serialization and exact objective certificates

Both historical and independent unrounded binary64 readouts are converted exactly to rational numbers, rounded to nearest 30-bit dyadic with ties to even, then clipped to the original box. Historical dyadic numerators, denominators, binary64 values and hexadecimal strings must agree with that independent reconstruction. Independently produced audit-only model JSON is written and read back, and all equivalent coefficient encodings are checked. It is explicitly marked unavailable for deployment. It does not overwrite historical bytes.

For VALUE, compute the squared-loss objective and gradient exactly on the independently reconstructed finite design. Convexity gives a lower bound by minimizing its tangent over the original box; the exact rounded objective is the primal upper bound. Report their full gap without requiring it to be small. Nonuniqueness or a different candidate coefficient vector is not an audit failure and is never hidden. The exact difference between the two rounded objectives is reported separately.

For MARGINAL, compute the exact maximum robust node residual of each rounded readout. Take the nonnegative parts of the negative recorded inequality multipliers and normalize them to unit rational mass. If their mass is zero, use the prespecified uniform weights. The resulting weighted label term plus the exact box minimum of the aggregate feature gradient is a valid dual lower bound. The exact residual is the primal upper bound. All dual weights, aggregate box gradients and gaps are retained, including weak witnesses. No floating stationarity or approximate LP tolerance is promoted to an exact certificate.

The historical binary64 design matrices are compared entry by entry with independent rational assembly. All discrepancy magnitudes are reported exactly; no equality is presumed where original floating B-spline or capacity operations rounded. Complete label and actor identities are checked before every model audit.

## Scope, reporting and costs

Success requires that all 56 stored-model cases are inspected and serialized without source, specification, rational weak-duality or readback violations; a numerical fit failure remains a recorded failure and the aggregate exit code is nonzero. Neither matching coefficients nor a selected small objective gap defines success. Every gap and raw status is reported. Differences in a nonunique optimizer do not justify selecting whichever candidate gives favorable economic behavior, and no refitted candidate enters the R126 production census.

This audit establishes only the executed parts of independent feature/design reconstruction, finite-design refitting, rounding, exact finite-box objective bounds and serialization. It does not independently reacquire original labels, implement a new LP solver, verify the fitted critic over its entire continuous domain, supply a new original-policy regret certificate, or estimate population policy loss for new actors. The lack of whole-domain fit verification remains explicit; production Bellman qualification is a different layer. R97 B8/M9 is therefore addressed in these specified components rather than declared closed wholesale.

Record source verification, imports, every candidate solve, rational arithmetic, input/output, all failures, total audit wall time and maximum resident memory. The parent launcher records the complete external process clock, including startup and shutdown. These are **audit research costs**, additional to the preserved historical acquisition costs and separate from current production-service clocks. They cannot be omitted from the research ledger or counted as a newly measured standalone deployment training bill. No timing repeat is an independent policy sample.

## Commands

Abstract, pre-freeze synthetic algebra only:

```text
python code126/independent_fit126.py --self-test
```

After the R126 immutable source boundary, using the actual F126 SHA and a new output directory:

```text
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python code126/independent_fit126.py --source-commit F126 \
  --output results126/independent-fit-attempt01
```

This document records a prospective audit specification, not completed empirical refitting outcomes.
