#!/usr/bin/env python3
"""Read-only content and source-identity verification of a downloaded CI artifact.
This never imports a scientific program, starts a campaign, rebuilds, or mutates Git.
"""
from pathlib import Path
import datetime as dt, hashlib, json, os, subprocess, zipfile

ROOT=Path("/workspace/scratch/913249553838/audit/review_lineage/resumption119")
REPO=Path("/workspace/scratch/913249553838/NBO")
REV=REPO/"revisions/2026-10-18-r119"
SOURCE="6250abfd317f3b2a56cb1303eb5ce78249bf4042"
HIST="cafd38aedc5bcbddf5aafee2481fbf5e9a267bab"
PREFIX="revisions/2026-10-18-r119/"
OUT=ROOT/"ARTIFACT_CONTENT_VERIFICATION119.json"
def sha(b):return hashlib.sha256(b).hexdigest()
def readj(p):return json.loads(p.read_text())
def utc():return dt.datetime.now(dt.timezone.utc).isoformat()
def write_new(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("x",encoding="utf-8") as f:json.dump(d,f,indent=2,sort_keys=True);f.write("\n")
start=utc()
tree_run=subprocess.run(["git","-C",str(REPO),"ls-tree","-r","-z",SOURCE,"--",PREFIX],capture_output=True,check=True,env=dict(os.environ,GIT_NO_LAZY_FETCH="1"))
tree={}
for entry in tree_run.stdout.split(b"\0"):
 if not entry:continue
 meta,path=entry.split(b"\t",1);mode,kind,blob=meta.decode().split()
 if kind=="blob":tree[path.decode()[len(PREFIX):]]=blob
archive=ROOT/"author_artifact_12143895724.zip"
members=readj(ROOT/"ARTIFACT_MEMBERS119.json")
download=readj(ROOT/"ARTIFACT_DOWNLOAD119.json")
assert archive.stat().st_size==4305287 and sha(archive.read_bytes())==members["archive_sha256"]==download["actual_sha256"]=="668cf5c1cb438aa117debcd0e8c526ec76a1789749bf96d79e95119363593a0a"
with zipfile.ZipFile(archive) as z:
 payload={n:z.read(n) for n in z.namelist()}
assert len(payload)==len(members["members"])==56
member_key="path" if "path" in members["members"][0] else "member"
for row in members["members"]:
 b=payload[row[member_key]]
 assert sha(b)==row["sha256"]
def zj(name):return json.loads(payload[name])
v=zj("ci119/verification/VALIDATION119.json")
b=zj("ci119/build-receipts/20261018T164344.436761Z/BUILD_RECEIPT119.json")
d=zj("ci119/verification/independent-D-record-replay/R119D_REPORTER_EXECUTION.json")
n=zj("ci119/verification/independent-D-record-replay/R119D_NUMERICAL_REVIEW.json")
f=zj("ci119/verification/declared-fused-fixtures/EXECUTION119C.json")
assert v["checkout_sha"]==SOURCE and v["status"]=="passed"
assert b["status"]=="compiled_clean" and not b["diagnostic"] and not b["scientific_execution"] and b["issues"]=={} and b["placeholders"]==[]
assert d["status"]=="passed" and f["status"]=="passed"
log_checks=[]
for receipt,base in [(v,"ci119/verification/"),(b,"")]:
 for c in receipt["commands"]:
  assert c["exit_code"]==0 and c["status"]=="passed"
  path=base+c["log"]
  assert sha(payload[path])==c["log_sha256"],path
  log_checks.append({"path":path,"sha256":c["log_sha256"],"exit_code":0})
assert len(log_checks)==26
pdf_checks=[]
for row in b["pdfs"]:
 p=row["path"];data=payload[p]
 assert len(data)==row["bytes"] and sha(data)==row["sha256"]
 native=REV/p
 pdf_checks.append(dict(row,native_published_sha256=sha(native.read_bytes()) if native.is_file() else None,
  byte_identical_to_native_published_pdf=(native.is_file() and native.read_bytes()==data)))
source_expected=dict(b["source_sha256"])
def include(path,digest):
 if path in source_expected:assert source_expected[path]==digest,path
 source_expected[path]=digest
for p,h in b["graphic_asset_sha256"].items():include(p,h)
for mapping in b["actual_project_inputs"].values():
 for p,h in mapping.items():include(p,h)
for freeze in v["freezes"]:
 include(freeze["manifest"],freeze["manifest_sha256"])
 for row in freeze["checked"]:include(row["path"],row["sha256"])
for wanted,digest in [("validator",v["validator_sha256"]),("builder",b["builder_sha256"]),("reporter",d["reporter_sha256"])]:
 candidates=[p for p in REV.glob("*.py")]+([REV/"code119/analyze119d.py"] if wanted=="reporter" else [])
 matches=[str(p.relative_to(REV)) for p in candidates if sha(p.read_bytes())==digest]
 assert len(matches)==1,(wanted,matches)
 include(matches[0],digest)
source_checks=[]
for p,h in sorted(source_expected.items()):
 data=(REV/p).read_bytes()
 assert sha(data)==h,("native SHA",p)
 blob=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
 assert tree.get(p)==blob,("immutable source tree",p)
 source_checks.append({"path":p,"bytes":len(data),"sha256":h,"source_git_blob":blob})
d_outputs=[]
for row in d["outputs"]:
 p="ci119/verification/independent-D-record-replay/"+row["path"]
 assert len(payload[p])==row["bytes"] and sha(payload[p])==row["sha256"],p
 d_outputs.append({"path":p,"bytes":row["bytes"],"sha256":row["sha256"]})
for row in f["files"]:
 p="ci119/verification/declared-fused-fixtures/"+row["path"]
 assert sha(payload[p])==row["sha256"],p
assert n["checks"]==590818 and n["source_files"]==49 and n["input_files"]==97 and n["source_commit"]==HIST
assert n["policy_keys"]==983 and n["primary_records"]==13824 and n["all_240_service_identities_exactly_verified"] and n["all_56_contrasts_exactly_reaggregated"] and n["all_96_means_exactly_reaggregated"]
generated={}
for mapping in b["generated_build_inputs"].values():
 for p,h in mapping.items():
  if p in generated:assert generated[p]==h
  generated[p]=h
generated_scope=[{"path":p,"receipt_sha256":h,"included_in_artifact":p in payload,
 "hash_verified_from_artifact":p in payload and sha(payload[p])==h}
 for p,h in sorted(generated.items())]
oldchecks=[]
oldreceipts=readj(ROOT/"recovered_pre_interruption/support/GZIP_SAVE_RECEIPTS_RETAINED119.json")["retained_object"]
for p in sorted((ROOT/"recovered_pre_interruption/envelopes").glob("*.json")):
 raw=p.read_bytes();obj=json.loads(raw)
 prior=[r for r in oldreceipts if r["logical_path"]==obj["path"]]
 row={"recovered_path":str(p.relative_to(ROOT)),"original_path":obj["path"],"original_observed_at_utc":obj["observed_at_utc"],"bytes":len(raw),"sha256":sha(raw),"has_retained_pre_interruption_byte_hash":bool(prior)}
 if prior:
  assert len(prior)==1 and prior[0]["raw_sha256"]==sha(raw) and prior[0]["raw_bytes"]==len(raw),("recovered envelope mismatch",p)
  row["matches_retained_pre_interruption_byte_hash"]=True
 oldchecks.append(row)
assert len(oldchecks)==6
out={"schema":"nbo-r119-ci-artifact-content-verification-v1","started_utc":start,"finished_utc":utc(),"status":"passed_read_only_artifact_member_receipt_and_source_identity_verification",
 "source_sha":SOURCE,"artifact_id":12143895724,"archive_sha256":sha(archive.read_bytes()),"archive_bytes":archive.stat().st_size,
 "members":56,"expanded_bytes":members["expanded_bytes"],"member_manifest":{"path":"ARTIFACT_MEMBERS119.json","sha256":sha((ROOT/"ARTIFACT_MEMBERS119.json").read_bytes())},
 "validation":{"status":v["status"],"source_sha":v["checkout_sha"],"commands":len(v["commands"]),"scope":v["scope"],"started_utc":v["started_utc"],"finished_utc":v["finished_utc"],"archives":v["archives"]},
 "build":{"status":b["status"],"commands":len(b["commands"]),"source_date_epoch":b["source_date_epoch"],"declared_source_files":len(b["source_sha256"]),"graphic_assets":len(b["graphic_asset_sha256"]),"actual_project_input_counts":{k:len(x) for k,x in b["actual_project_inputs"].items()},"issues":b["issues"],"placeholders":b["placeholders"],"pdfs":pdf_checks,"generated_inputs":generated_scope,"generated_input_scope":"Receipt retains all 14 distinct auxiliary input hashes; those auxiliary bytes are not included in this artifact. They were not reconstructed or claimed verified. Published P PDFs remain unchanged."},
 "successful_command_log_checks":log_checks,"immutable_source_checks":source_checks,
 "independent_D_saved_record_replay":{"status":d["status"],"scope":d["scope"],"checks":n["checks"],"source_files":n["source_files"],"input_files":n["input_files"],"policy_keys":n["policy_keys"],"primary_records":n["primary_records"],"counts":{"means":96,"contrasts":56,"identities":240},"output_hash_checks":d_outputs},
 "declared_exact_fixtures":{"status":f["status"],"checks":f["checks"],"custody_commit":f["custody_commit"],"scope":"Declared exact fixture reuse in the actual CI job; no timed policy campaign is claimed rerun."},
 "recovered_historical_envelope_checks":oldchecks,
 "limitations":["No scientific campaign, independent 983-policy solve, competitive performance clock, native build or workflow was executed in this verification.","Historical run API completion and 16 artifact metadata records were checked; historical artifact CONTENT was not downloaded or independently verified in this resumption task.","Only six full pre-interruption API envelopes are recoverable from retained orchestration objects. The other 127 historical envelopes and lost 151-file bundle remain unavailable. Save receipts do not substitute for missing payload bytes."]}
write_new(OUT,out)
print(json.dumps({"status":out["status"],"source_checks":len(source_checks),"log_checks":len(log_checks),"pdfs":pdf_checks,"generated_input_count":len(generated),"recovered_hash_matches":sum(bool(x.get("matches_retained_pre_interruption_byte_hash")) for x in oldchecks),"receipt_sha256":sha(OUT.read_bytes())},indent=2))

