"""Execute the post-pilot R5 protocol without replacing unsuccessful seeds.
Each run is a fresh process so peak RSS and failure costs remain interpretable.
Use --indices to run a slice; an existing completed record is never overwritten.
"""
from __future__ import annotations
import argparse, json, subprocess, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=HERE.parent/'results'

def panel():
    base=dict(n=6,width=48,actor_steps=600,critic_steps=800,lr=.004)
    runs=[dict(base,seed=s,panel='baseline') for s in range(10,20)]
    runs += [dict(base,n=12,seed=s,panel='longer_horizon') for s in (10,11,12)]
    for key,value in [('width',32),('width',64),('lr',.002),('lr',.008),('actor_steps',300),('critic_steps',400)]:
        for s in (20,21):
            cfg=dict(base,seed=s,panel=f'{key}_{value}'); cfg[key]=value; runs.append(cfg)
    return runs

def main():
    p=argparse.ArgumentParser(); p.add_argument('--indices',default='0:25'); p.add_argument('--timeout',type=int,default=300)
    a=p.parse_args(); first,last=map(int,a.indices.split(':')); OUT.mkdir(parents=True,exist_ok=True)
    for index,cfg in enumerate(panel()):
        if not first<=index<last: continue
        tag=f"n{cfg['n']}_s{cfg['seed']}_w{cfg['width']}_a{cfg['actor_steps']}_c{cfg['critic_steps']}_lr{cfg['lr']:g}"
        marker=OUT/(tag+'_execution.json')
        if marker.exists():
            print('retained existing execution',tag,flush=True); continue
        cmd=[sys.executable,str(HERE/'continuous_actor.py')]
        for k in ('n','seed','width','actor_steps','critic_steps','lr'): cmd += ['--'+k.replace('_','-'),str(cfg[k])]
        start=time.perf_counter(); rec=dict(index=index,panel=cfg['panel'],tag=tag,command=cmd[1:],configuration=cfg)
        try:
            with (OUT/(tag+'.log')).open('w') as log:
                run=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=a.timeout)
            rec.update(returncode=run.returncode,status='completed' if run.returncode==0 else 'failed')
        except subprocess.TimeoutExpired:
            rec.update(returncode=None,status='timeout')
        rec['elapsed_seconds']=time.perf_counter()-start
        marker.write_text(json.dumps(rec,indent=2))
        print(json.dumps(rec),flush=True)
if __name__=='__main__': main()
