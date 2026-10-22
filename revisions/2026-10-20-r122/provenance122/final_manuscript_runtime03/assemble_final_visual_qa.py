"""Bind the actually completed selected-page visual review and preserve PDFs.

Running this script binds evidence; it cannot reproduce a human/model visual
review. The inspection scope below records pages actually viewed by the author
agent and the separately recorded response agent.
"""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json
import shutil
import time

start = time.perf_counter()
base = Path("provenance122/final_manuscript_runtime03")
build_path = Path("build_receipts122/final-runtime03-origin/20261022T025302.033102Z/BUILD_RECEIPT122.json")
build = json.loads(build_path.read_text())
assert build["status"] == "compiled_clean" and not build["issues"] and not build["placeholders"]
assert all(r["exit_code"] == 0 for r in build["commands"])
for group in ("source_sha256", "graphic_asset_sha256"):
    for name, digest in build[group].items():
        assert sha256(Path(name).read_bytes()).hexdigest() == digest, name
inspection_path = base / "pdf-inspection02/PDF_INSPECTION122.json"
inspection = json.loads(inspection_path.read_text())
assert inspection["build_receipt_sha256"] == sha256(build_path.read_bytes()).hexdigest()
assert not inspection["physical_page_boundary_exceptions"]
response_path = Path("provenance122/runtime_recovery_after_upload_reset/RESPONSE_PREFLIGHT_VISUAL_QA122.json")
response = json.loads(response_path.read_text())
assert response["pdf"]["sha256"] == next(x["sha256"] for x in inspection["pdfs"] if x["path"] == "build/RESPONSE_TO_REFEREE.pdf")
copy_dir = base / "successful_preflight04"
copy_dir.mkdir(exist_ok=False)


def bind(path):
    p = Path(path)
    return {"path": str(p), "bytes": p.stat().st_size, "sha256": sha256(p.read_bytes()).hexdigest()}


snapshots = []
for row in inspection["pdfs"]:
    src = Path(row["path"])
    assert sha256(src.read_bytes()).hexdigest() == row["sha256"]
    dst = copy_dir / src.name
    shutil.copyfile(src, dst)
    assert sha256(dst.read_bytes()).hexdigest() == row["sha256"]
    snapshots.append({**bind(dst), "pages": row["pages"], "source_path_at_copy": str(src)})
viewed = []
for doc, num in (("ECTA", 8), ("supp", 7), ("appendix", 5)):
    for i in range(1, num + 1):
        viewed.append(bind(base / f"pdf-inspection02/{doc}-contact-{i:02d}.png"))
for page in (1, 25, 26, 27):
    viewed.append(bind(base / f"pdf-inspection01/ECTA-{page:04d}.png"))
for page in (6, 9, 10):
    viewed.append(bind(base / f"pdf-inspection02/appendix-{page:04d}.png"))
for page in (106, 107):
    viewed.append(bind(base / f"supp_tail_visual/supp-{page:04d}.png"))
for p in sorted(Path("figures122/runtime03-display").glob("catalogue_*.png")):
    viewed.append(bind(p))
receipt = {
    "schema": "nbo.r122.final-author-preflight-visual-review.v1",
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "status": "selected-page_visual_review_and_all-page_geometry_passed",
    "assembly_source": bind(Path(__file__)),
    "build_receipt": bind(build_path),
    "automatic_inspection_receipt": bind(inspection_path),
    "supplement_tail_render_receipt": bind(base / "supp_tail_visual/SUPP_TAIL_RENDER122.json"),
    "independent_response_visual_review_receipt": bind(response_path),
    "unchanged_response_pdf_identity_confirmed": True,
    "successful_preflight_pdf_copies": snapshots,
    "all_current_build_sources_and_graphic_hashes_rechecked": True,
    "all_pdf_pages_automatically_geometry_checked": sum(x["pages"] for x in inspection["pdfs"]),
    "physical_page_boundary_exceptions": [],
    "primary_inspection_rendered_pages": len(inspection["rendered_pages"]),
    "supplementary_rendered_pages": [106, 107],
    "visually_reviewed_scope": {
        "ECTA": {"contact_sheet_pages": list(range(1, 30)), "full_page_renders": [1, 25, 26, 27], "earlier_full_page_images_have_identical_pdf_sha256": True},
        "supp": {"contact_sheet_pages": [1] + list(range(82, 106)), "full_page_renders": [106, 107]},
        "appendix": {"contact_sheet_pages": list(range(1, 19)), "full_page_renders": [6, 9, 10], "all_eight_actual_imported_figure_pages": list(range(10, 18))},
        "RESPONSE_TO_REFEREE": {"separately_reviewed_by_response_agent_pages": [1, 2, 37, 38, 42], "same_final_pdf_bytes": True},
        "standalone_catalogue": {"all_eight_png_pages_reviewed_at_full_resolution": True},
    },
    "viewed_image_bindings": viewed,
    "findings": [
        "The complete 29-page main paper has legible equations, narrative, tables and references; the actual results tables and abstract were also inspected at full-page scale.",
        "The current paid-support, minimax, dynamic-gain and inference sections of the supplement have readable formulas, resolved references and no visible overlap on the inspected pages.",
        "The complete 174-row development table is present in fixed catalogue order with outward-rounded economic endpoints. Dense table pages6 and9 were inspected at full-page scale.",
        "All eight complete-catalogue pages are embedded as actual landscape plots on appendix pages10-17. Text, titles, legend and lower disclosure lines are visible; the standard article origin and page size resume on page18.",
        "The earlier draft-mode figure placeholders and minus-one-inch page-origin clipping are actual retained failed renderings. The final independent check confirms exact whitespace-normalized source plot text and matching page sizes for all eight included pages.",
        "The exact retained response paragraph that previously overran the margin is repaired solely by the wrapper emergency stretch; the independently reviewed response PDF is byte-identical to the final preflight response.",
    ],
    "limits": [
        "This is local preflight evidence. It does not claim future runner PDF identity, final package completion or a successful final-author GitHub CI run.",
        "The 926-page development companion was geometry-checked throughout, but its archival pages19-926 were not all visually inspected in this final pass.",
        "Contact-sheet layout review is distinguished from full-page review; no claim is made that every glyph on all1104 pages was manually read.",
        "No scientific experiment, model, sampling rule, original objective, confidence interval or service timing was changed by this administrative review.",
    ],
    "prior_administrative_assembly_failure": {
        "actual_error": "KeyError: returncode",
        "cause": "The one-off receipt-assembly command used the wrong key for build122 command exits; the actual saved schema is exit_code.",
        "scope": "Failed before any PDF copy or final receipt write. No build, scientific reader or author-source change occurred.",
        "complete_elapsed_seconds": None,
        "disclosure_kind": "Retrospective factual disclosure of the observed command failure, not a reconstructed execution log or invented clock.",
    },
    "manual_visual_review_elapsed_seconds": None,
    "receipt_operation_seconds_before_write": time.perf_counter() - start,
    "clock_scope": "Actual source/hash readback, preflight copy and receipt assembly only. Manual review has no complete measured clock; renderer/launch clocks are stored separately and must not be added twice.",
}
path = base / "AUTHOR_FINAL_VISUAL_QA122.json"
with path.open("x") as f:
    json.dump(receipt, f, indent=2, sort_keys=True)
    f.write("\n")
print(json.dumps({"receipt": str(path), "sha256": sha256(path.read_bytes()).hexdigest(), "copied_pdf_bytes": sum(x["bytes"] for x in snapshots), "operation_seconds": receipt["receipt_operation_seconds_before_write"], "viewed_image_bindings": len(viewed)}, indent=2))
