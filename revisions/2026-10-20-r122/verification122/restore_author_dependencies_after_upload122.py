"""Restore declared original author dependencies from immutable Git objects."""
from pathlib import Path
import argparse,datetime as dt,hashlib,json,subprocess,time,traceback
R=Path(__file__).resolve().parents[1];REPO=R.parents[1]
F='2f483615c8bc0037e43ec01a16cce05c724f8c60';HEAD='80dec8acbfb8225be5f8dee135ed10efb5054d93';R97='9723c6cd2cc8b3e071422f3e522d4a843946db63'
def main():
 start=time.perf_counter();ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path);a=ap.parse_args();out=a.output.resolve();assert out.is_relative_to(R) and not out.exists();out.parent.mkdir(parents=True,exist_ok=True);baseline=json.loads((R/'BASELINE122.json').read_text());freeze=json.loads((R/'SOURCE_FREEZE122.json').read_text());jobs={p:(F,h) for p,h in freeze['scientific_files'].items()}
 for category in baseline['historical_custody'].values():
  if 'index' in category:
   x=category['index'];jobs[x['path']]=(HEAD,x['sha256'])
  for x in category['entries']:
   x=x['verified_file'];jobs[x['path']]=(HEAD,x['sha256'])
 for x in [*baseline['inputs'],baseline['inherited_report_reading']['receipt'],baseline['inherited_full_tree_census']['index']]:
  if x['path'].startswith('revisions/2026-10-20-r121/'):jobs[x['path']]=(HEAD,x['sha256'])
 jobs['revisions/2026-10-20-r121/provenance121/R97_REQUIREMENTS121.json']=(HEAD,'674ba384bd43cdfdb11106dd635cff9552a7caa7da1ce2d6c42510aa6b75f11e')
 jobs['revisions/2026-10-20-r121/new121/response121_body.tex']=(HEAD,'0db0fe5df55fff586d3ab2078ffbd18b9e2c9bb6dd96cb95f8642b4482b6d6d0')
 jobs[baseline['controlling_report']['file']['path']]=(R97,baseline['controlling_report']['file']['sha256'])
 receipt={'reader_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'published_reader_sha256':'11f3ece2b1e35429efd55af4912d31092bd37b096662f75e95608e38b2e7d5ff','source_reconstruction_scope':'New output-addressable reader derived from the published runtime restorer; not a claimed recovery of any lost unpublished helper.','status':'started','started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'records':[],'new_economic_evaluations':0,'new_states':0,'scope':'Actual byte/tree/hash readback of explicitly enumerated author and scientific dependencies from immutable commits; no fresh semantic reread claim for historical reports.'}
 try:
  for name,(source,expected) in sorted(jobs.items()):
   data=subprocess.check_output(['git','show',source+':'+name],cwd=REPO);h=hashlib.sha256(data).hexdigest();assert h==expected,name
   p=REPO/name;action='already_identical'
   if p.exists():assert p.is_file() and not p.is_symlink() and p.read_bytes()==data,name
   else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);action='restored_exact'
   blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert subprocess.check_output(['git','rev-parse',source+':'+name],cwd=REPO,text=True).strip()==blob
   receipt['records'].append({'path':name,'source_commit':source,'bytes':len(data),'sha256':h,'git_blob':blob,'action':action})
  receipt.update(status='verified',files=len(jobs),bytes=sum(x['bytes'] for x in receipt['records']),frozen_members=243,historical_reports=35,historical_boundaries=27)
 except BaseException:receipt.update(status='failed',traceback=traceback.format_exc());raise
 finally:
  receipt.update(ended_utc=dt.datetime.now(dt.timezone.utc).isoformat(),elapsed_seconds=time.perf_counter()-start,cost_clock_components=[{'category':'author_dependency_readback','clock_fields':[['elapsed_seconds']],'scope':'This actual immutable-object/native byte restoration only.','partial_lower_bound_only':False,'overlaps_counted_parent':False}]);out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:receipt[k] for k in ['status','files','bytes','elapsed_seconds']}),flush=True)
if __name__=='__main__':main()
