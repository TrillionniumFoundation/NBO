#!/usr/bin/env python3
"""Reproduce R4, with content-addressed provenance and distinct evidence classes."""
import argparse,hashlib,json,platform,resource,time
from dataclasses import asdict
from pathlib import Path
import numpy as np
import scipy,torch
from solver import *
from diagnostics import *


def compact(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {k:compact(v) for k,v in x.items() if k!='evaluated'}
    if isinstance(x,(list,tuple)):return [compact(v) for v in x]
    return x


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='replication/r4/output')
    ap.add_argument('--mode',choices=['tests','reference','neural','all'],default='all')
    ap.add_argument('--seeds',default='101,202,303');ap.add_argument('--steps',type=int,default=8)
    ap.add_argument('--source-commit',default=None);args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True);results={};start=time.perf_counter()
    if args.mode in ['tests','all']:
        results.update(generator=generator_tests(),temporal=temporal_tests(),trace=trace_tests(),merton=stationary_utility(),epstein_zin=stationary_utility(recursive=True),game=game_test())
        results['lqr']=[lqr_test(d) for d in [4,8,16]]
    if args.mode in ['reference','all']:
        rows=[]
        specs=[(17,25,4,(5,5,7),2.),(25,37,8,(5,5,7),2.),(33,49,16,(5,5,7),2.),(33,49,8,(5,5,7),2.),(65,97,16,(5,5,7),2.),
               (25,37,8,(9,9,13),2.),(25,37,8,(9,9,13),.5),(25,37,8,(9,9,13),8.)]
        for nu,nx,N,counts,k in specs:
            ans=solve_grid(nu,nx,N,counts,Model(k=k));name=f'ref_{nu}_{nx}_{N}_{counts[0]}_{k:g}'
            np.savez_compressed(out/(name+'.npz'),values=np.array(ans['values']),policies=np.array(ans['policies']),efforts=np.array(ans['efforts']))
            point=np.array([[2.,1.25]])
            row=dict(run=name,k=k,grid=[nu,nx],steps=N,counts=counts,seconds=ans['elapsed'],initial_value=float(interpolate(ans['values'][0],point)[0]),
                     initial_effort=float(interpolate(ans['efforts'][0],point)[0]),mean_branch_exit=ans['mean_branch_exit'],initial_policy=ans['policies'][0][nu//2,nx//2].tolist())
            rows.append(row);print(row,flush=True)
        results['reference']=rows
    if args.mode in ['neural','all']:
        results['neural']=[]
        for seed in map(int,args.seeds.split(',')):
            ans=solve_neural(seed,steps=args.steps,outdir=out);results['neural'].append(compact(ans));print(compact(ans),flush=True)
    results=compact(results);payload=json.dumps(results,sort_keys=True,indent=2,allow_nan=False)
    (out/f'{args.mode}_results.json').write_text(payload+'\n')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('*.py'))}
    # Timing is deliberately excluded from the scientific hash.
    def scientific(x):
        if isinstance(x,dict):return {k:scientific(v) for k,v in x.items() if not(k.endswith('seconds') or k in ['elapsed','seconds'])}
        if isinstance(x,list):return [scientific(v) for v in x]
        return x
    digest=hashlib.sha256(json.dumps(scientific(results),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    manifest=dict(base_review_commit='79a7d84be2cbbf9bd5d181599ee110540128e3b5',source_commit=args.source_commit,
                  source_commit_status='provided_commit' if args.source_commit else 'content_addressed_local_run',source_sha256=hashes,
                  python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,torch=torch.__version__,model=asdict(Model()),
                  bounds=dict(state=[LO.tolist(),HI.tolist()],action=[ALO.tolist(),AHI.tolist()]),execution_status='completed',
                  tolerance_status='individual_test_assertions_and_reported_errors',scientific_payload_sha256=digest,
                  elapsed_seconds=time.perf_counter()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    (out/f'{args.mode}_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('OUTPUT',out,flush=True)

if __name__=='__main__':main()
