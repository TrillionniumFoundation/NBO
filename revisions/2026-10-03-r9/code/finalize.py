"""Publication-only audit after the complete pinned numerical run.

Preserves every raw array. The first numerical source and run remain explicit;
this stage audits standalone costs and frozen raw-actor deployment, regenerates tables/manuscripts,
and repeats all software checks and compilation. It does not retrain policies.
"""
from __future__ import annotations
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 old=json.loads((R/'REMOTE_EXECUTION.json').read_text());oldmanifest=json.loads((R/'EVIDENCE_MANIFEST.json').read_text())['files']
 allowed={'revisions/2026-10-03-r9/code/replicate.py','revisions/2026-10-03-r9/manuscript/supplement.tex'}
 for name,h in oldmanifest.items():
  if name not in allowed:assert digest(ROOT/name)==h,name
 a=R/'archive'
 for name in ['SOURCE_MANIFEST','EVIDENCE_MANIFEST','REMOTE_EXECUTION']:
  (a/(name+'.numerical_phase.json')).write_bytes((R/(name+'.json')).read_bytes())
 arrays={str(p.relative_to(ROOT)):digest(p) for p in (R/'results').rglob('*.npz')}
 source=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip()
 records=[];start=time.perf_counter()
 commands=[('accounting',[sys.executable,str(R/'code/accounting.py')]),
  ('raw_actor_deployment',[sys.executable,str(R/'code/deployment_audit.py')]),
  ('tables',[sys.executable,str(R/'code/tables.py')]),('assemble',[sys.executable,str(R/'code/assemble.py')]),
  ('inherited_tests',[sys.executable,str(R/'code/replay_inherited.py')]),
  ('r9_tests',[sys.executable,str(R/'code/test_r9.py')]),
  ('accounting_tests',[sys.executable,str(R/'code/test_accounting.py')]),
  ('compile',['bash',str(R/'code/build_pdf.sh')])]
 for i,(name,command) in enumerate(commands):
  log=R/f'logs/final_{i:02d}_{name}.log';begin=time.perf_counter()
  with log.open('w') as f:p=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
  rec={'name':name,'command':command,'returncode':p.returncode,'seconds':time.perf_counter()-begin,'log':str(log.relative_to(ROOT)),'log_sha256':digest(log)}
  records.append(rec);(R/'results/FINALIZATION_COMMANDS.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(rec),flush=True)
  if p.returncode:raise RuntimeError(name)
 for name,h in arrays.items():assert digest(ROOT/name)==h,name
 history=json.loads((R/'archive/R8_FILES_SHA256.json').read_text())
 for name,h in history.items():
  if name not in ['ECTA.tex','supp.tex']:assert digest(ROOT/name)==h,name
 compile=json.loads((R/'results/COMPILATION.json').read_text())
 assert all(not v['undefined'] and not v['overfull_hbox_pt'] for v in compile.values())
 paths=list((R/'code').glob('*.py'))+list((R/'code').glob('*.sh'))
 paths += [p for p in (R/'manuscript').glob('*.tex') if not p.name.startswith('table_')]
 paths += [R/'response.tex',R/'README.md',R/'PROTOCOL.json']
 paths += list((ROOT/'.github/workflows').glob('nbo-r9-*.yml'))
 (R/'SOURCE_MANIFEST.json').write_text(json.dumps({'source_commit':source,'numerical_source_commit':old['source_commit'],
  'files':{str(p.relative_to(ROOT)):digest(p) for p in paths}},indent=2)+'\n')
 inherited=json.loads((R/'results/INHERITED_TESTS.json').read_text())
 tests=[*inherited['suites'],json.loads((R/'results/TEST_RESULTS.json').read_text()),json.loads((R/'results/ACCOUNTING_TESTS.json').read_text())]
 assert all(t['success'] for t in tests)
 record={'source_commit':source,'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'workflow_attempt':os.environ.get('GITHUB_RUN_ATTEMPT'),
  'numerical_phase':old,'numerical_results_reused_by_hash':True,'numerical_retraining_in_finalization':False,
  'raw_arrays_preserved':len(arrays),'historical_files_preserved':len(history)-2,
  'post_protocol_deployment_audit':json.loads((R/'results/FINE_RAW_DEPLOYMENT.json').read_text()),
  'finalization_commands':records,'finalization_seconds':time.perf_counter()-start,
  'tests':tests,'total_unique_tests':sum(t['tests'] for t in tests),'compilation':compile,
  'scope':'complete R9 evidence plus standalone cost and frozen raw-actor deployment audits; no original economic results or failed cases removed',
  'interval_scope':'conditional outward arithmetic, not machine formal verification'}
 (R/'REMOTE_EXECUTION.json').write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps({'source':source,'unique_tests':record['total_unique_tests'],'arrays_preserved':len(arrays),'complete':True}),flush=True)
 paths=[ROOT/'ECTA.tex',ROOT/'supp.tex']+[p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=R/'EVIDENCE_MANIFEST.json']
 (R/'EVIDENCE_MANIFEST.json').write_text(json.dumps({'files':{str(p.relative_to(ROOT)):digest(p) for p in paths},'excludes':['revisions/2026-10-03-r9/EVIDENCE_MANIFEST.json']},indent=2)+'\n')
if __name__=='__main__':run()
