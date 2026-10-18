"""Read-only verification of the deposited R110 package and all current raw hashes.

This does not refit models, retime services, re-execute a historical experiment,
or claim that finite tests are proofs. Optional --receipt writes only a new
verification receipt and refuses to replace an existing one.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,json,datetime,sys
R=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def need(ok,why):
 if not ok:raise AssertionError(why)
def main():
 p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path);a=p.parse_args()
 if a.receipt is not None and a.receipt.exists():raise FileExistsError('Keep every verification attempt')
 s=read(R/'evidence110/SUMMARY110.json');checks=0
 for rel,want in s['raw_directory_manifest'].items():
  need(h(R/rel)==want,'Raw record hash: '+rel);checks+=1
 for base,manifest in [(R,'SOURCE_FREEZE110.json'),(R/'frozen108','SOURCE_FREEZE108.json')]:
  d=read(base/manifest)
  for rel,want in d['scientific_files'].items():need(h(base/rel)==want,'Frozen source: '+rel);checks+=1
  if 'protocol_sha256' in d:need(h(base/'PROTOCOL108.md')==d['protocol_sha256'],'Inherited protocol');checks+=1
 expected_protocol_blob='8b10a39707876306e8814f11b072a603cb889129'
 b=(R/'PROTOCOL110.md').read_bytes()
 need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==expected_protocol_blob,'Exact remote new protocol blob');checks+=1
 for c in ('gain_campaign','reproduction_campaign'):
  need(s[c]['status']=='executed','Actual campaign exit')
  need(len(s[c]['processes'])==7 and all(x['exit_code']==0 for x in s[c]['processes']),'Every fresh-process exit');checks+=2
 need(s['gain_audit']['status']=='passed' and s['gain_audit']['decision_rows']==27648,'New actual audit')
 need(s['reproduction_audit']['status']=='passed' and s['reproduction_audit']['decision_rows']==18432,'Actual inherited-source audit');checks+=2
 need(s['kernel_audit']['status']=='passed' and s['kernel_audit']['states_risks']==384,'Independent exact kernel');checks+=1
 need(all(x['all_rows_and_trials_exact'] for x in s['gain_audit']['paired_inherited_controls']),'Paired complete controls');checks+=32
 need(all(x['all_within_registered_budget'] and x['unstopped_actions_exact_full_safe'] for x in s['gain_audit']['budget_checks']),'All registered budget/trace cases');checks+=64
 need(len(s['summary_rows'])==96,'Every service/budget/arm/risk is reported')
 need(all(len(x['all_seven_clocks'])==7 for x in s['summary_rows']),'No clock trimming');checks+=97
 need(all(x['rows_exactly_equal'] and x['trials_exactly_equal'] for x in s['equivalent_hinge_checks']),'Equal-information hinge equivalence');checks+=12
 for x in s['summary_rows']:
  need(F(x['original_cost_lower'])<=F(x['original_cost_upper']),'Mean original cost order')
  need(x['max_native_regret_upper']<=1/256 and x['max_width']<=1/8192,'Original unchanged qualification');checks+=2
 start=read(R/'raw110/gain-budget/START110.json')['started_unix']
 freeze_time=datetime.datetime(2026,10,16,10,54,7,tzinfo=datetime.timezone.utc).timestamp()
 need(start>freeze_time,'New source freeze precedes primary execution');checks+=1
 need(not s['population_inference_claim'] and not s['unseen_sample_claim'],'No false sampling identity');checks+=1
 need(not s['neural_exclusive_advantage_claim'] and not s['calibrated_adoption_claim'],'No unsupported adoption/exclusivity');checks+=1
 hist=s['inherited_replay'];need(hist['tests']==435 and hist['errors']==20 and hist['failures']==1,'Historical failure preservation');checks+=1
 retention=read(R/'evidence110/BASELINE_RETENTION110.json')
 for x in retention['files']:need(h(R/x['current_location'])==x['sha256'],'Historical source byte preservation '+x['path']);checks+=1
 splits=read(R/'evidence110/SECTION_SPLITS110.json')
 for x in splits:
  old=R/x['source'];new=(R/x['main']).read_bytes()+(R/x['archive']).read_bytes()
  need(new==old.read_bytes(),'Lossless split '+x['source']);checks+=1
 pub=read(R/'evidence110/PUBLICATION110.json')
 for rel,want in pub['source_sha256'].items():need(h(R/rel)==want,'Active TeX hash '+rel);checks+=1
 for rel,want in pub['bibliography_sha256'].items():need(h(R/rel)==want,'Bibliography hash '+rel);checks+=1
 for name,d in pub['documents'].items():
  need(h(R/'build'/(name+'.pdf'))==d['sha256'],'Actual current PDF '+name)
  need(not d['overfull_warnings'] and not d['pages_with_no_text'],'Typesetting checks '+name);checks+=2
 visual=read(R/'evidence110/VISUAL_REVIEW110.json')
 for name,d in pub['documents'].items():need(visual['documents'][name]['sha256']==d['sha256'],'Visual review same actual PDF');checks+=1
 report={'status':'passed','read_only_checks':checks,'raw_files':len(s['raw_directory_manifest']),
  'baseline_files':len(retention['files']),'active_tex_files':len(pub['source_sha256']),
  'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'primary_started_utc':datetime.datetime.fromtimestamp(start,datetime.timezone.utc).isoformat(),
  'new_source_committed_utc':'2026-10-16T10:54:07Z',
  'summary_sha256':h(R/'evidence110/SUMMARY110.json'),'publication_sha256':h(R/'evidence110/PUBLICATION110.json'),
  'scope':'Read-only byte, chronology, declared-catalogue, bounds and publication-account validation; not a scientific claim of full-history replay or a remote CI result'}
 if a.receipt is not None:a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
