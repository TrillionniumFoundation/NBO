"""Independent checks on a clean source checkout; preserve every planned outcome."""
from __future__ import annotations
import json,os,pathlib,subprocess,sys,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-22-r11';OUT=REV/'ci_results'
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def main():
 OUT.mkdir(parents=True,exist_ok=True);cells=[];source=os.environ['R11_MANUSCRIPT_SOURCE'];start=time.perf_counter()
 plan=[('accuracy',[sys.executable,str(REV/'replication/accuracy.py'),'--out',str(REV/'results/accuracy')])]
 for k in ['0.5','2','8']:plan.append(('original-k'+k,[sys.executable,str(ROOT/'revisions/2026-09-22-r10/replication/run_cell.py'),'--k',k,'--output',str(REV/f'results/original_recheck/k{k}')]))
 for name,args in plan:
  rec={'cell':name,'status':'started','source_commit':source};dump(OUT/f'{name}_status.json',rec)
  env=dict(os.environ,R10_SOURCE_COMMIT='d633bd60818998e53051cee6e7ad351c52a61795')
  try:
   r=subprocess.run(args,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=500)
   (OUT/f'{name}.log').write_text(r.stdout);rec.update(returncode=r.returncode,status='success' if r.returncode==0 else 'failed')
  except Exception as e:rec.update(status='failed',exception=str(e));(OUT/f'{name}.log').write_text(traceback.format_exc())
  dump(OUT/f'{name}_status.json',rec);cells.append(rec)
 check={'cell':'agreement-with-canonical','status':'started'}
 try:
  a=json.loads((REV/'development_execution.json').read_text())['accuracy'];b=json.loads((REV/'results/accuracy/summary.json').read_text())['rows'];assert len(a)==len(b)==30
  for x,y in zip(a,b):assert x['case']==y['case'] and x['method']==y['method'] and abs(x['absolute_regret'][1]-y['absolute_regret'][1])<1e-9
  for k in ['0.5','2','8']:
   a=json.loads((REV/f'results/original_recheck/k{k}/flexible_dual_k{k}.json').read_text())['records'][-1];assert a['target_met'] and a['certified_regret_upper']<.01
  subprocess.check_call([sys.executable,str(REV/'replication/test_revision.py')],cwd=ROOT)
  subprocess.check_call([sys.executable,str(REV/'replication/validate_revision.py'),'--skip-pdf'],cwd=ROOT)
  check['status']='success'
 except Exception as e:check.update(status='failed',exception=str(e),traceback=traceback.format_exc())
 cells.append(check);status={'status':'PASS' if all(c['status']=='success' for c in cells) else 'FAIL','source_commit':source,'cells':cells,'seconds':time.perf_counter()-start}
 dump(OUT/'status.json',status);print(json.dumps(status,indent=2));return status
if __name__=='__main__':main()
