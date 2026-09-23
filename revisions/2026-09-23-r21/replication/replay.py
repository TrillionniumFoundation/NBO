"""Replay frozen R20 actors; fresh processes prevent backend contamination."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import argparse,subprocess,sys,os,time,json,hashlib
ROOT=Path(__file__).resolve().parents[3]; OLD=ROOT/'revisions/2026-09-23-r20'; REV=ROOT/'revisions/2026-09-23-r21'
def load(p):return json.loads(p.read_text())
def run_one(job):
 backend,actor,out,reference=job;env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
 env.pop('BACKEND',None)
 if backend=='mpfr':env['BACKEND']='mpfr'
 out.parent.mkdir(parents=True,exist_ok=True)
 p=subprocess.run([sys.executable,str(OLD/'replication/certify_stochastic.py'),str(actor),'--out',str(out)],env=env,cwd=ROOT,capture_output=True,text=True)
 if p.returncode:raise RuntimeError(f'{actor}: {p.stderr[-3000:]}')
 new,prev=load(out),load(reference)
 for key in ['value_interval','price_interval','reserve_interval','initial_portfolio_interval']:
  a,b=new[key],prev[key]
  if max(a[0],b[0])>min(a[1],b[1]):raise AssertionError((str(actor),key,a,b))
 return {'backend':backend,'actor':str(actor.relative_to(ROOT)),'actor_sha256':hashlib.sha256(actor.read_bytes()).hexdigest(),
  'result':str(out.relative_to(ROOT)),'overlap_with_inherited':True,'seconds':new['seconds']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=3);a=p.parse_args();start=time.perf_counter();jobs=[]
 for actor in sorted((OLD/'results/neural').glob('seed*/vertex*/actor_*.json')):
  rel=actor.relative_to(OLD/'results');out=REV/'results/replay/binary'/rel
  jobs.append(('binary',actor,out,actor.with_name(actor.name.replace('actor_','certificate_'))))
  if actor.name=='actor_1000.json':
   seed=int(actor.parent.parent.name[4:]);v=int(actor.parent.name[6:]);ref=OLD/f'results/mpfr/seed{seed}_vertex{v}.json'
   jobs.append(('mpfr',actor,REV/'results/replay/mpfr'/rel,ref))
 for actor in sorted((OLD/'results/classical_stochastic').glob('vertex*/actor_*.json')):
  jobs.append(('binary',actor,REV/'results/replay/binary'/actor.relative_to(OLD/'results'),actor.with_name(actor.name.replace('actor_','certificate_'))))
 for actor in sorted((OLD/'results/wealth').glob('actor_*.json')):
  jobs.append(('binary',actor,REV/'results/replay/binary'/actor.relative_to(OLD/'results'),actor.with_name(actor.name.replace('actor_','certificate_'))))
 records=[]
 with ThreadPoolExecutor(max_workers=a.workers) as pool:
  for future in as_completed([pool.submit(run_one,j) for j in jobs]):
   r=future.result();records.append(r);print(len(records),len(jobs),r['backend'],r['actor'],flush=True)
 records.sort(key=lambda r:(r['backend'],r['actor']))
 report={'status':'PASS','checks':len(records),'binary_checks':sum(r['backend']=='binary' for r in records),'mpfr_checks':sum(r['backend']=='mpfr' for r in records),
 'wall_seconds':time.perf_counter()-start,'workers':a.workers,'semantics':'independent execution and arithmetic replay of frozen policies; not new training or independent mathematics','records':records}
 (REV/'results/replay_summary.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
