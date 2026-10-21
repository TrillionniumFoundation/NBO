"""Independent negative custody checks for the additive R122 package binding."""
import copy, datetime as dt, hashlib, importlib.util, io, json, subprocess, time, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def load(name):
 p=ROOT/'verification122'/name;spec=importlib.util.spec_from_file_location(name.replace('.','_'),p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 start=time.perf_counter();b=load('make_referee_package122.py');v=load('verify_referee_archive122.py')
 names=sorted({b.INDEPENDENT_PUBLICATION,*b.INDEPENDENT_SOURCE_PATHS,b.RESUME_PUBLICATION,*(x['path'] for x in b.RESUME_SOURCE_ROWS)})
 data={x:(REPO/x).read_bytes() for x in names};native=[{'path':x,'bytes':len(data[x]),'sha256':hashlib.sha256(data[x]).hexdigest()} for x in names];members={r['path']:r for r in native}
 value={'path_root':'repository','source_commit_F':b.SOURCE_F,'state_commit_D':b.STATE_D,'reporting_adapter_commit':b.ADAPTER,'independent_initial_state_units':32,'new_population_observations':0,'new_training':0,'new_economic_evaluations':0,'new_service_timing_processes':0,**b.independent_publication_binding(native),**b.resume_publication_binding(native)}
 def check(value,members,data):
  raw=io.BytesIO()
  with zipfile.ZipFile(raw,'w') as z:
   for name,body in data.items():z.writestr(name,body)
  raw.seek(0)
  with zipfile.ZipFile(raw) as z:
   v.identities(value);v.independent_publication_binding(value,members,z);v.resume_publication_binding(value,members,z)
 check(value,members,data);cases=[]
 def reject(name,mutate):
  vv,mm,dd=copy.deepcopy(value),copy.deepcopy(members),dict(data);mutate(vv,mm,dd)
  try:check(vv,mm,dd)
  except (ValueError,KeyError):cases.append({'case':name,'rejected':True});return
  raise AssertionError('Custody corruption accepted: '+name)
 reject('wrong_R_commit',lambda x,y,z:x.update(resume_adapter_commit='0'*40))
 reject('wrong_R_tree',lambda x,y,z:x.update(resume_adapter_tree='1'*40))
 reject('missing_Git_attestation',lambda x,y,z:x.update(resume_adapter_git_membership_verified=False))
 n=b.RESUME_SOURCE_ROWS[0]['path']
 reject('omitted_R_source',lambda x,y,z:y.pop(n))
 reject('changed_source_manifest_hash',lambda x,y,z:y[n].update(sha256='0'*64))
 reject('changed_pinned_source_Git_blob',lambda x,y,z:x['resume_adapter_source_files'][0].update(git_blob='0'*40))
 reject('altered_source_native_bytes',lambda x,y,z:z.update({n:z[n]+b'\n'}))
 def receipt_rewrite(x,y,z):
  p=b.RESUME_PUBLICATION;j=json.loads(z[p]);j['tree']='0'*40;z[p]=(json.dumps(j)+'\n').encode();row={'path':p,'bytes':len(z[p]),'sha256':hashlib.sha256(z[p]).hexdigest()};y[p]=row;x['resume_adapter_publication']=row
 reject('self_consistent_forged_receipt',receipt_rewrite)
 core=ROOT/'verification122/verify_package122.py';assert sha(core)=='ac5656f350fb126ccb096fc1ba71565ba0a37fa71fe2521bfd2a1e93da3e9a07'
 files=['make_referee_package122.py','verify_referee_archive122.py','ci_verify122.py','ci_saved_replay122.py','test_runtime_package_binding122.py']
 result={'status':'passed','scope':'Actual immutable I/R Git binding and offline source-custody corruption checks only; no final ZIP or CI success claimed.','positive_binding_cases':1,'negative_cases':cases,'negative_cases_count':len(cases),'native_source_files_bound':7,'publications_bound':2,'source_files':[{'path':'verification122/'+x,'bytes':(ROOT/'verification122'/x).stat().st_size,'sha256':sha(ROOT/'verification122'/x)} for x in files],'immutable_core_sha256':sha(core),'elapsed_seconds':time.perf_counter()-start,'ended_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'new_economic_evaluations':0,'cost_clock_components':[{'category':'publication_source_qa','clock_fields':[['elapsed_seconds']],'scope':'This actual binding/corruption-check invocation only.','partial_lower_bound_only':False,'overlaps_counted_parent':False}]}
 out=ROOT/'provenance122/runtime_recovery/R_PACKAGE_BINDING_REVIEW122.json'
 with out.open('x') as f:f.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'negative_cases':len(cases),'receipt_sha256':sha(out),'elapsed_seconds':result['elapsed_seconds']}))
if __name__=='__main__':main()
