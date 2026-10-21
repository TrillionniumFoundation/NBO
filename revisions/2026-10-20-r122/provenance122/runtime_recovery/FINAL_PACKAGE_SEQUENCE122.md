# R122 final package execution sequence after runtime recovery

This is an execution checklist, not a completed-package or CI receipt. All scientific outcomes must come from the actual new `runtime-recovery-<run>-<attempt>` native stages. No lost earlier directory is repopulated under its old identity. The unchanged core verifier remains SHA256 `ac5656f350fb126ccb096fc1ba71565ba0a37fa71fe2521bfd2a1e93da3e9a07`.

## Actual evidence before manuscript freeze

Obtain the final recovery status from the actual GitHub run and hydrate every request in its updated registry. The source-bound canonical path, statistics path, original failed reporter path and adapted report path come from that status, not from an anticipated count. Read the composite and unchanged through-report verifier receipts. Retain all source-review, failed-execution, checkpoint and publication records; all older 32-state production/service clocks remain unchanged.

Execute the restrictive interrupted-primary sensitivity reader with the new actual report:

```sh
python verification122/interrupted_clock_sensitivity122.py --report results122/runtime-recovery-RUN-ATTEMPT-adapted-report --output results122/runtime-recovery-RUN-ATTEMPT-clock-sensitivity
```

Run it through the original `code122/launch122.py` so its actual outer receipt is preserved. `--report` is the only new scientific-input path; interrupted and restarted primary defaults remain the original published ones.

The unchanged research ledger accepts `--additional-receipts`. Supply the actually executed `recovery_cost_bridge122.py` receipt for one complete recovery status/artifact snapshot, fresh local readback receipts, and the separately recorded unavailable-prior-work disclosure. The bridge checks and counts all nested checkpoint publication attempts, otherwise uncounted preparation/validation stages and residual enclosing overhead exactly once. Do not also pass its nested checkpoint publication or stage receipts independently. The automatic publication scan covers only top-level `provenance122/*PUBLICATION122.json`; the bridge supplies the otherwise omitted nested clocks. Its automatic `LAUNCH122.json` scan includes the new scientific launchers, while its transport scan includes every actual request. Do not add the encompassing orchestrator wall clock to those component costs. Earlier per-policy cached clocks, both old aggregate ledgers and overlapping stage/parent clocks are not charged twice. The full research total remains unknown because interrupted parent clocks and the unavailable old suffix/admin clocks are not native-recoverable. A lower bound is not an exact total.

## Author-source and PDF closure

Integrate actual results into all seven pending manuscript slots and regenerate the exact 30-item response with explicit new independent/statistics/report/original-report paths. Preserve every exact request and nested historical response. Freeze the author text before the strict four-document build:

```sh
python build122.py --receipt-dir build_receipts122_runtime_final01
```

Accept only actual `compiled_clean`, empty issues, empty placeholders, and four real PDFs. Preserve failed builds under their own new receipt paths. The source/PDF manifest is revision-relative, excludes itself, and consists of ordinary-file records `{path, bytes, sha256}`. Include all four PDF records, every declared author source, all actual TeX recorder project inputs and every graphic asset identified by that actual build. No author/figure/table input may change afterward without another actual build.

## Publication-input schema

`PUBLICATION_INPUTS122.json` must bind the actual paths; `RUN`, `ATTEMPT` and `STAMP` below are placeholders in this checklist only:

```json
{
  "source_commit_F": "2f483615c8bc0037e43ec01a16cce05c724f8c60",
  "state_commit_D": "a3323b6f557315ea91b536637419ef6fd7984b61",
  "independent_directory": "results122/runtime-recovery-RUN-ATTEMPT-canonical",
  "stats_directory": "results122/runtime-recovery-RUN-ATTEMPT-statistics",
  "report_directory": "results122/runtime-recovery-RUN-ATTEMPT-adapted-report",
  "original_report_directory": "results122/runtime-recovery-RUN-ATTEMPT-original-report",
  "local_build_receipt": "build_receipts122_runtime_final01/STAMP/BUILD_RECEIPT122.json",
  "local_cost_ledger": "results122/runtime-recovery-RUN-ATTEMPT-cost-ledger/COST_LEDGER122.json",
  "local_clock_sensitivity": "results122/runtime-recovery-RUN-ATTEMPT-clock-sensitivity",
  "source_pdf_manifest": "SOURCE_PDF_HASHES122.json",
  "transport_registry": "transport122/REGISTRY122.json",
  "package_manifest": "referee_package122/NATIVE_MANIFEST122.json",
  "resume_publication": "provenance122/RESUME_INDEPENDENT_PUBLICATION122.json",
  "resume_verification_command": [
    "verification122/verify_independent_resume122.py",
    "--resume-publication", "provenance122/RESUME_INDEPENDENT_PUBLICATION122.json",
    "--primary", "results122/primary-attempt02",
    "--independent", "results122/runtime-recovery-RUN-ATTEMPT-canonical",
    "--output", "ci122/resume-verification"
  ]
}
```

The new unfrozen CI readers propagate all four stage paths and preserve the historical defaults only for backward compatibility. The actual GitHub CI guard still checks repository, workspace and exact event commit. The frozen core CLI supports explicit `--independent`, `--stats`, `--report`, and `--original-report` unchanged.

## Native archive and real verification

Create an explicit JSON list of repository-relative ordinary files. Include the complete 243-member F closure, scientific manifests/protocols, actual I and R receipts and all seven pinned adapter/continuation sources, current complete native science and failures, needed history/response sources, current author source closure, four PDFs, actual build receipt, source/PDF manifest, full current ledger/input manifest, sensitivity output/input manifest, and all actual source/validation/publication receipts used by the claims. Include native evidence once; compressed transport copies need not also be archive members. Historical content not in the ZIP retains an exact original Git route in the retention map and must not be described as included.

Use new, disjoint paths:

```sh
python verification122/make_referee_package122.py --paths EXPLICIT_PATHS.json --manifest referee_package122/NATIVE_MANIFEST122.json --archive /absolute/new/referee-package122.zip --parts-directory referee_package122/parts
python verification122/verify_referee_archive122.py --transport referee_package122/parts/PACKAGE_TRANSPORT122.json --repository /absolute/actual/repository --receipt referee_package122/OFFLINE_VERIFICATION122.json
```

The updated builder checks I and R against actual Git commits; the offline verifier independently pins both trees, seven source blobs and the observed R publication receipt hash. It must reject altered self-consistent attestation. The actual final ZIP is still required: the source-binding unit check is not its verification.

Run `verify_package122.py --through package` with F, D, all four explicit stage overrides, actual sensitivity directory, cost ledger, build receipt, source/PDF manifest, native package manifest, transport registry and a new verification-output directory. It checks all prerequisite science gates, every listed native package byte, full frozen closure, failed attempts, actual PDFs/recorder inputs, and the full transport archive census. All newly created results/launchers must have their own small transport bundle before remote source publication.

## Git, CI and hash-cycle boundaries

Commit source/PDF/package bytes on the isolated revision branch and trigger the author-package workflow with a concrete `CI_TRIGGER122.json`. Large outputs may be committed by the actual authorized GitHub job using a temporary index and non-force push, with explicit paths and actual commit/readback receipts; do not repeat the stalled large API payload transfer. The final workflow must check the actual event source commit S. Preserve its exact run/job IDs, conclusions, logs and downloadable artifacts. A later metadata publication P or delivery V is not covered by S's CI automatically.

Final cost updates after packaging are new cutoff-specific append-only ledgers; they cannot silently replace the ledger already hashed inside the archive. The publication receipt cannot contain its own commit or SHA as if known before writing; retain that identity in the next commit and verify it by remote readback. Refresh the full remote-head census at final delivery, verify no historical branch changed, and report only actual successful scientific stages, builds, archive checks and CI conclusions.
