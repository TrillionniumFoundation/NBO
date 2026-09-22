# R14: current manuscript and computational evidence

Start with root `ECTA_R14.pdf` (18 pages), `SUPP_R14.pdf` (11 pages), and `response_to_referee.md`. Root `R14_REVIEW.md` is the canonical reading entry point. The title, author, original economic model and first-exit contract are retained.

## Numerical objects (do not interchange them)

| Object | Verified quantity | Scope |
|---|---:|---|
| Independently audited original policy library | 0.009969007710640541 | All k in [0.5,8], central initial state |
| Same library, perturbed duals and enlarged allowances | 0.009970977449945498 | Same central state and price continuum |
| Budget-shifted initial-state policy library | 0.012095431553888848 | t=0, u in [1.98,2.02], x in [1.24,1.26], all k in [0.5,8] |
| Actual fresh neural actor/critic, finest complete cover | 23.493172462829243 | Entire original state rectangle at t=0, k=2; separate all-time bound recorded |

The neural certificate is complete but does not meet 0.01. The fresh 16/32/64-interval classical experiment passes 0.01 but not 0.005, 0.0025 or 0.001. These false accuracy predicates are deliberate scientific results, not build failures. No claim of two matched-accuracy classical HJB baselines or general neural superiority is made.

## Replication

Python/package versions and hardware are recorded in `environment.json`; exact tested package releases are in `requirements.txt`. Install them in an isolated environment. A recent TeX installation with the packages used by the root manuscript is needed for PDFs. The supplied `econsocart.cls` and `.cfg` are unchanged publisher files.

From the repository root:

```bash
# Build and reject unresolved references/citations or overfull boxes.
bash revisions/2026-09-22-r14/replication/build_papers.sh

# Check included data, mathematical primitives, hashes and recorded enclosures.
python revisions/2026-09-22-r14/replication/validate_revision.py

# Independent library audit, state extension, robustness and high-precision checks.
# The output directory must not already exist.
python revisions/2026-09-22-r14/replication/reproduce.py \
  --out revisions/2026-09-22-r14/results/rerun_audit

# Also freshly regenerate the actual neural run and classical policy frontier.
python revisions/2026-09-22-r14/replication/reproduce.py --full \
  --out revisions/2026-09-22-r14/results/rerun_full
```

The individual stages were executed and their logs are included. The source-frozen 18-node replay was also executed, with exact equality of all 54 decisive node fields. `reproduce.py` is a convenience orchestrator over those entry points; the delivery does not pretend that an unexecuted combined command has its own executed timing. New neural outputs include timing fields, so file-level byte identity is not an acceptance criterion for retraining. Valid certificates and explicit tolerance predicates are the acceptance criteria.

The audit of the inherited price library starts from frozen historical proposals. Its generation cost is unknown, not zero. The fresh neural and classical-generation experiments are distinct and fully recorded. High-precision closed-form quadrature is diagnostic; it is not the interval proof.

## Publication and local history

The complete R12 archive was obtained through the GitHub workflow artifact. All 1,830 files matched it before revision work. A synthetic local root commit reconstructs that archive for a portable local branch; **it is not the original Git commit**. The original R12 and R13 review commit IDs are separately pinned.

The delivered R14 tree has now been published on two new GitHub revision branches: revision/econometrica-r14-independent-state-audit-2026-09-22 and revision/econometrica-r14-referee-copy-2026-09-22. Both descend from the exact latest remote review commit 857bfeab28ca1b7a7f732edf180126f3ded6b451. The earlier publishing helper and local reconstructed commits remain provenance records; no synthetic reconstructed history was force-pushed over existing branches.

## Preservation

Prior manuscripts, technical extensions, negative comparisons, unsuccessful certificates and all old experiment data remain at their original paths. The root index is the only deliberately replaced historical file; its original bytes are stored in `archive/REVISION_INDEX_before_R14.md`. `preservation_manifest.json` records every baseline file hash. The new main text is not required to contain every old line as an ordered subsequence.
