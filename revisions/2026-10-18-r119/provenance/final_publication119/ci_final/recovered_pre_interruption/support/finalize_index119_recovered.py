from pathlib import Path
import json,gzip,hashlib,datetime,collections
base=Path("/workspace/scratch/913249553838/audit/review_lineage/final_ci119")
sha=lambda b:hashlib.sha256(b).hexdigest()
for name,wanted in {
 "SNAPSHOT_INDEX119.json":"2c2b9bc0fd59e231adeb8151ded5e009c65152640f95dfc32930338ce64d58b2",
 "SNAPSHOT_INDEX119_20261018T163450Z.json":"5d1ebd93f7b02c91eefa69a495f979da46a05b43f6c4f9945ccbd69e8c64d274",
 "AUTHOR_SOURCE_CI_SUCCESS119_20261018T164607Z.json":"5f6368cf6f018c219ca375effafd4a37368852bb4abfcdc10c37f02cd956e6b0",
}.items():
 assert sha((base/name).read_bytes())==wanted,name
records=[];invalid=[];latest={}
for p in sorted(base.iterdir()):
 if not (p.name.startswith("20") and (p.name.endswith(".json") or p.name.endswith(".json.gz"))):continue
 encoded=p.read_bytes()
 try:
  data=gzip.decompress(encoded) if p.name.endswith(".gz") else encoded
  obj=json.loads(data)
 except Exception as exc:
  invalid.append({"path":p.name,"bytes":len(encoded),"sha256":sha(encoded),
   "classification":"Preserved failed local write; not a complete API envelope.","parse_error":str(exc)})
  continue
 assert "raw_tool_response" in obj and "api_payload" in obj,p.name
 payload=obj["api_payload"]
 r={"path":p.name,"bytes":len(encoded),"sha256":sha(encoded),
  "representation":"gzip" if p.name.endswith(".gz") else "json",
  "inflated_bytes":len(data),"inflated_sha256":sha(data),
  "logical_filename":Path(obj.get("path",p.name[:-3] if p.name.endswith(".gz") else p.name)).name,
  "logical_filename_basis":"captured_path" if "path" in obj else "physical_container_filename",
  **{k:obj[k] for k in ["run_id","expected_source","url","request_started_utc","observed_at_utc"]}}
 if "jobs" in payload:
  assert len(payload["jobs"])==payload["total_count"]
  r["kind"]="jobs";r["job_count"]=len(payload["jobs"])
  r["status_counts"]=dict(collections.Counter(str(j.get("status"))+"/"+str(j.get("conclusion")) for j in payload["jobs"]))
 elif "artifacts" in payload:
  assert len(payload["artifacts"])==payload["total_count"]
  r["kind"]="artifacts";r["artifact_count"]=len(payload["artifacts"])
 else:
  r["kind"]="run"
  r["run_status"]={k:payload.get(k) for k in ["status","conclusion","head_sha","updated_at"]}
 records.append(r)
 if obj["url"] not in latest or obj["observed_at_utc"]>latest[obj["url"]][0]["observed_at_utc"]:
  latest[obj["url"]]=(obj,r)
expected_invalid={"20261018T153645Z-historical_corrected-jobs.json","20261018T170412Z-author_source-jobs.json"}
assert {r["path"] for r in invalid}==expected_invalid,invalid
assert all(r["bytes"]==0 for r in invalid)
assert sum(r["representation"]=="gzip" for r in records)==24
def terminal(run_id,head,num):
 root="https://api.github.com/repos/TrillionniumFoundation/NBO/actions/runs/"+str(run_id)
 r,rr=latest[root];j,jr=latest[root+"/jobs?per_page=100"];a,ar=latest[root+"/artifacts?per_page=100"]
 run=r["api_payload"];jobs=j["api_payload"]["jobs"];artifacts=a["api_payload"]["artifacts"]
 assert run["id"]==run_id and run["head_sha"]==head and run["status"]=="completed" and run["conclusion"]=="success"
 assert len(jobs)==num and all(x["head_sha"]==head and x["status"]=="completed" and x["conclusion"]=="success" for x in jobs)
 assert len(artifacts)==num and all(x["workflow_run"]["head_sha"]==head and not x["expired"] for x in artifacts)
 return {"run_id":run_id,"run_url":run["html_url"],"head_sha":head,"workflow_name":run["name"],
  "status":run["status"],"conclusion":run["conclusion"],"run_updated_at_utc":run["updated_at"],
  "final_run_observed_at_utc":r["observed_at_utc"],"jobs_observed_at_utc":j["observed_at_utc"],
  "artifacts_observed_at_utc":a["observed_at_utc"],"run_attempt":run["run_attempt"],
  "successful_jobs":len(jobs),"advertised_artifacts":len(artifacts),
  "last_job_completed_at_utc":max(x["completed_at"] for x in jobs),
  "raw_evidence":[rr,jr,ar],
  "jobs":[{k:x.get(k) for k in ["id","name","status","conclusion","started_at","completed_at","head_sha"]} for x in jobs],
  "artifacts":[{k:x.get(k) for k in ["id","name","size_in_bytes","digest","expired","created_at","workflow_run"]} for x in artifacts]}
author=terminal(39140983514,"6250abfd317f3b2a56cb1303eb5ce78249bf4042",1)
history=terminal(39136070575,"cafd38aedc5bcbddf5aafee2481fbf5e9a267bab",16)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
final={"schema":"nbo-r119-final-ci-status-v1","receipt_created_at_utc":now,
 "api_observation_cutoff_utc":max(x["observed_at_utc"] for x in records),
 "author_source":author,"corrected_historical":history,
 "artifact_scope":"Artifact IDs, sizes, digests and source heads are advertised GitHub API metadata. This monitor did not download, extract, or independently verify artifact contents.",
 "historical_scope":"The successful corrected historical-custody workflow is separate from the earlier failed run 39103777344. Its sixteen checkout failures and all accurately dated queued/running observations remain preserved; no earlier receipt or PDF was rewritten.",
 "monitor_scope":"Read-only GitHub monitoring. No dispatch, cancellation, rerun, workflow mutation, scientific evaluation, native manuscript edit, or PDF change.",
 "storage_recovery":{"complete_envelopes_in_gzip":24,"pending_memory_only_envelopes":0,
  "receipt":"COMPRESSED_SNAPSHOT_RECOVERY119.json","second_failure_receipt":"MONITOR_STORAGE_FAILURE119_ATTEMPT02.json",
  "first_failure_receipt":"MONITOR_STORAGE_FAILURE119.json","failed_targets_preserved":invalid},
 "whole_author_source_ci_success_observed":True,"whole_corrected_historical_ci_success_observed":True}
final_name="FINAL_CI_STATUS119_20261018T171839Z.json"
with (base/final_name).open("x") as f:json.dump(final,f,indent=2,sort_keys=True);f.write("\n")
readme="""# Final R119 CI monitoring snapshot

Both requested workflows reached completed/success at their exact recorded source heads.
The author-source run is 39140983514 (6250abfd317f3b2a56cb1303eb5ce78249bf4042).
The corrected historical-custody run is 39136070575 (cafd38aedc5bcbddf5aafee2481fbf5e9a267bab).
See FINAL_CI_STATUS119_20261018T171839Z.json for the actual observation times, job states and artifact IDs.

SNAPSHOT_INDEX119_FINAL_20261018T171839Z.json binds every saved API envelope and supporting file.
Older indices, pending observations and both zero-byte local-write failures are retained unchanged.
Twenty-four later complete envelopes use deterministic gzip with no original-filename header and mtime=0.
For a .json.gz record, the index supplies both compressed and inflated SHA-256 identities.
Inflate it into a separate directory if a plain JSON copy is needed; do not overwrite either retained
zero-byte failed-write target. The compressed envelope contains the full captured tool response
and parsed API payload. It is not an independently downloaded workflow artifact.
Artifact contents were not downloaded or independently verified by this monitor.

The storage-recovery receipt and execution record distinguish the default writer failure,
the bounded read-only capacity diagnostic, and successful direct escalated gzip persistence.
No original API snapshot, native source, PDF, scientific result or workflow was changed.
"""
with (base/"README_FINAL_CI119.md").open("x") as f:f.write(readme)
copy_files=[]
for p in sorted(base.iterdir()):
 if p.is_file():
  b=p.read_bytes();copy_files.append({"path":p.name,"bytes":len(b),"sha256":sha(b)})
index={"schema":"nbo-r119-final-ci-snapshot-index-v3","indexed_at_utc":now,
 "api_observation_cutoff_utc":final["api_observation_cutoff_utc"],
 "complete_api_envelopes":len(records),
 "complete_api_envelopes_stored_bytes":sum(x["bytes"] for x in records),
 "complete_api_envelopes_inflated_bytes":sum(x["inflated_bytes"] for x in records),
 "gzip_api_envelopes":sum(x["representation"]=="gzip" for x in records),
 "pending_memory_only_envelopes":0,
 "api_envelopes":records,"preserved_incomplete_writes":invalid,
 "latest_endpoint_observations":[r for o,r in latest.values()],
 "terminal_status_receipt":next(x for x in copy_files if x["path"]==final_name),
 "copy_files":copy_files,
 "scope":"Immutable final monitoring index; extends without replacing older indices or observations. Copy files preserve all complete captured API envelopes, local-write failures, recovery records, and terminal CI receipts. Advertised workflow artifacts were not downloaded by this monitor."}
index_name="SNAPSHOT_INDEX119_FINAL_20261018T171839Z.json"
with (base/index_name).open("x") as f:json.dump(index,f,indent=2,sort_keys=True);f.write("\n")
for name in [final_name,index_name,"README_FINAL_CI119.md"]:
 b=(base/name).read_bytes()
 print(json.dumps({"path":str(base/name),"bytes":len(b),"sha256":sha(b)}))
print(json.dumps({"complete_api_envelopes":len(records),"stored_bytes":index["complete_api_envelopes_stored_bytes"],
 "inflated_bytes":index["complete_api_envelopes_inflated_bytes"],"gzip_envelopes":index["gzip_api_envelopes"],
 "preserved_zero_byte_failed_writes":len(invalid),"copy_files":len(copy_files),"copy_bytes":sum(x["bytes"] for x in copy_files),
 "author_ci":"completed/success","historical_ci":"completed/success","pending_memory_only":0}))

