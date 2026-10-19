#!/usr/bin/env python3
"""Append-only delivery of actual R119 CI recovery and artifact-verification evidence."""
from pathlib import Path
import datetime as dt, hashlib, json, shutil, re
ROOT=Path("/workspace/scratch/913249553838/audit/review_lineage/resumption119")
REV=Path("/workspace/scratch/913249553838/NBO/revisions/2026-10-18-r119")
DEST=REV/"provenance/final_publication119/ci_final"
def sha(data):return hashlib.sha256(data).hexdigest()
def utc():return dt.datetime.now(dt.timezone.utc).isoformat()
def obj(path):return json.loads(path.read_text())
def newjson(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("x",encoding="utf-8") as f:json.dump(data,f,indent=2,sort_keys=True);f.write("\n")
def bind(path):return {"bytes":path.stat().st_size,"sha256":sha(path.read_bytes())}
verification=obj(ROOT/"ARTIFACT_CONTENT_VERIFICATION119.json")
api=obj(ROOT/"TERMINAL_API_SUMMARY119.json")
assert len(api["runs"])==2 and all(r["status"]=="completed" and r["conclusion"]=="success" for r in api["runs"])
assert verification["status"]=="passed_read_only_artifact_member_receipt_and_source_identity_verification"
protected=sorted(set([x["path"] for x in verification["immutable_source_checks"]]+["SOURCE_PDF_MANIFEST119.json"]+[x["path"] for x in verification["build"]["pdfs"]]))
before={p:bind(REV/p) for p in protected}
assert not (REV/"FINAL_CI_STATUS119.json").exists()
assert not (DEST/"NATIVE_COPY_RECEIPT119.json").exists()
loss={"schema":"nbo-r119-local-loss-and-genuine-recovery-v1","recorded_utc":utc(),
 "observation":"On resumption the former local 151-file monitoring bundle was unavailable; its directory survived without regular files. No absent historical payload is asserted recovered.",
 "pre_interruption_bundle":{"previously_recorded_files":151,"previously_captured_api_envelopes":133,"available_as_original_local_files":0},
 "genuine_retained_orchestration_recovery":{"complete_api_envelopes":6,"other_api_envelopes_unavailable":127,"actual_gzip_save_receipts":24,"receipt_is_payload":False,
 "prior_hash_verifiable_envelopes":4,"prior_raw_hash_matches":4,"two_remaining_envelopes":"Full original captured objects with original request/observation time and raw tool response; no lost individual-file hash independently available."},
 "serialization_boundary":"The initial recovery write added one trailing newline; those initial serializations and both verifier failures are retained. Separate exact_envelopes remove only that introduced newline. Four exact files match retained historical raw-byte hashes.",
 "old_queued_observations":"Not reconstructed from current terminal API states. Any genuinely retained old object is kept at its original observation time.",
 "fresh_api_observations":6,"actual_downloaded_artifact_id":12143895724,
 "security_scope":"Ephemeral signed download URL and encoded private execution source are excluded. Canonical GitHub API/Actions URLs and actual artifact bytes/digests are retained.",
 "scientific_execution":False,"workflow_mutation":False}
if not (ROOT/"LOCAL_LOSS_AND_V8_RECOVERY119.json").exists():newjson(ROOT/"LOCAL_LOSS_AND_V8_RECOVERY119.json",loss)
key_members=[
"ci119/verification/VALIDATION119.json",
"ci119/build-receipts/20261018T164344.436761Z/BUILD_RECEIPT119.json",
"ci119/verification/independent-D-record-replay/R119D_REPORTER_EXECUTION.json",
"ci119/verification/independent-D-record-replay/R119D_NUMERICAL_REVIEW.json",
"ci119/verification/declared-fused-fixtures/EXECUTION119C.json",
"ci119/verification/proof-algebra/original_correctness_regression119.json"]
for p in key_members:
 target=ROOT/"key_receipts"/p;target.parent.mkdir(parents=True,exist_ok=True)
 data=(ROOT/"artifact_contents"/p).read_bytes()
 if target.exists():assert target.read_bytes()==data
 else:
  with target.open("xb") as f:f.write(data)
selected=[p for p in sorted(ROOT.rglob("*")) if p.is_file() and "artifact_contents" not in p.relative_to(ROOT).parts]
rows=[]
DEST.mkdir(parents=True,exist_ok=True)
for source in selected:
 rel=source.relative_to(ROOT);data=source.read_bytes()
 if source.suffix in {".json",".py",".md"}:
  text=data.decode("utf-8")
  urls=re.findall(r'https?://[^\s"<>\\]+',text)
  assert not any(marker in url for url in urls for marker in ["X-Amz-Signature=","X-Goog-Signature=","&sig=","?sig="]),("unexpected signed URL",str(rel))
 target=DEST/rel;target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert target.read_bytes()==data
 else:
  with target.open("xb") as f:f.write(data)
 assert target.read_bytes()==data
 rows.append({"path":str(rel),"source_audit_path":str(source),"bytes":len(data),"sha256":sha(data)})
after={p:bind(REV/p) for p in protected}
assert before==after
copy={"schema":"nbo-r119-final-ci-append-only-copy-v1","copied_utc":utc(),"status":"all_selected_bytes_copied_and_readback_verified","source_audit_root":str(ROOT),"destination_revision_relative":"provenance/final_publication119/ci_final",
 "copied_files":len(rows),"copied_bytes":sum(r["bytes"] for r in rows),"files":rows,
 "scope":"New CI evidence only. Complete downloaded ZIP and all 56 member hashes are retained; expanded CI PDFs remain audit-only. No existing P source, PDF, SOURCE_PDF_MANIFEST119 or scientific evidence was overwritten.",
 "protected_native_files_unchanged":len(protected),"protected_native_bindings":before}
copy_path=DEST/"NATIVE_COPY_RECEIPT119.json";newjson(copy_path,copy)
status={"schema":"nbo-r119-final-ci-status-after-resumption-v1","created_utc":utc(),
 "author_source_sha":"6250abfd317f3b2a56cb1303eb5ce78249bf4042",
 "observation_scope":"Fresh 2026-10-19 terminal GitHub observations and actual downloaded artifact verification after loss of local-only monitoring files. Correctly dated historical snapshots are not rewritten.",
 "runs":api["runs"],
 "author_artifact_content":{"id":12143895724,"bytes":verification["archive_bytes"],"sha256":verification["archive_sha256"],"members":verification["members"],"expanded_bytes":verification["expanded_bytes"],
 "archive":"provenance/final_publication119/ci_final/author_artifact_12143895724.zip",
 "member_hashes":"provenance/final_publication119/ci_final/ARTIFACT_MEMBERS119.json",
 "verification_receipt":"provenance/final_publication119/ci_final/ARTIFACT_CONTENT_VERIFICATION119.json",
 "verification_receipt_sha256":bind(DEST/"ARTIFACT_CONTENT_VERIFICATION119.json")["sha256"],
 "validation_status":verification["validation"]["status"],"build_status":verification["build"]["status"],
 "successful_commands_and_log_hashes_verified":26,"immutable_source_files_byte_and_git_blob_verified":343,
 "four_ci_pdfs_byte_identical_to_published_p_pdfs":all(p["byte_identical_to_native_published_pdf"] for p in verification["build"]["pdfs"]),
 "generated_auxiliary_scope":verification["build"]["generated_input_scope"],
 "scientific_scope":verification["validation"]["scope"]},
 "historical_artifact_scope":"All 16 jobs and their 16 artifact metadata records are source-bound completed/success. Historical artifact contents were not independently downloaded in this resumption task.",
 "local_loss_and_recovery_receipt":"provenance/final_publication119/ci_final/LOCAL_LOSS_AND_V8_RECOVERY119.json",
 "unavailable_pre_interruption_api_envelopes":127,"genuinely_recovered_complete_api_envelopes":6,
 "native_copy_receipt":"provenance/final_publication119/ci_final/NATIVE_COPY_RECEIPT119.json",
 "native_copy_receipt_sha256":bind(copy_path)["sha256"],
 "no_scientific_rerun":True,"no_native_build_rerun":True,"no_workflow_or_ref_mutation":True}
newjson(ROOT/"FINAL_CI_STATUS119.json",status)
data=(ROOT/"FINAL_CI_STATUS119.json").read_bytes()
with (REV/"FINAL_CI_STATUS119.json").open("xb") as f:f.write(data)
assert (REV/"FINAL_CI_STATUS119.json").read_bytes()==data
done={"schema":"nbo-r119-ci-delivery-completion-v1","completed_utc":utc(),"status":"delivered","native_final_status":bind(REV/"FINAL_CI_STATUS119.json"),
 "native_copy_receipt":bind(copy_path),"copied_files":len(rows),"copied_bytes":sum(r["bytes"] for r in rows),"protected_files_unchanged":len(protected)}
newjson(ROOT/"DELIVERY_COMPLETION119.json",done)
print(json.dumps(done,indent=2))

