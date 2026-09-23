"""Reproduce every declared R19 scientific object, retaining all proposals."""
from pathlib import Path
import subprocess,sys,os,time,json
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;R=HERE.parent

def main():
    env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
    logs=R/'build_logs';logs.mkdir(exist_ok=True,parents=True);records=[]
    scripts=[('policy_sensitive.py',['--phase','all']),('attribution.py',[]),('warm_frontier.py',[]),
             ('state_gain.py',[]),('neural_compensation.py',[]),('contraction_audit.py',[]),('make_tables.py',[]),('validate.py',[])]
    for name,args in scripts:
        start=time.perf_counter();print('RUN',name,flush=True)
        with (logs/(name.removesuffix('.py')+'.log')).open('w') as f:
            subprocess.run([sys.executable,str(HERE/name),*args],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
        records.append({'script':name,'wall_seconds':time.perf_counter()-start,'status':'PASS'})
        (R/'results/reproduction.json').write_text(json.dumps(records,indent=2)+'\n')
        print('PASS',name,records[-1]['wall_seconds'],flush=True)
if __name__=='__main__':main()
