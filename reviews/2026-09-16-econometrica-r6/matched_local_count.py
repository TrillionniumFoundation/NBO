#!/usr/bin/env python3
"""Matched localized-count diagnostic. Imports author kernels, not author outputs
as conclusions. It reuses the deposited bank and intervals; no autonomous
anchor selection, training, or speed superiority is claimed.
Run: python matched_local_count.py --repo /path/to/NBO --output results.json
"""
from __future__ import annotations
import argparse,hashlib,json,os,sys,time
from pathlib import Path
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np
from reviewer_diagnostics import certificate,restrict

def local_count(mix,left,right,d):
    coeff=[None]*(mix.steps+1); coeff[-1]=mix.terminal[None,:].copy()
    for n in range(mix.steps-1,-1,-1):
        h=mix.steps-n; layer=[]; previous_right=None
        for j in range(h):
            q0=mix.q(0,n,coeff[n+1][j],d); q1=mix.q(1,n,coeff[n+1][j],d)
            qa=(1-left)*q0+left*q1; qb=(1-right)*q0+right*q1
            q=(1-j/h)*qa
            if j: q+=(j/h)*previous_right
            layer.append(q.max(axis=1)); previous_right=qb
        layer.append(previous_right.max(axis=1)); coeff[n]=np.asarray(layer)
    return coeff

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--contracts',type=float,nargs='+',default=[0.,.5,1.]); args=ap.parse_args()
    sys.path.insert(0,str(args.repo/'replication/r6'))
    from transport import Mixture
    import contracts as c
    meta=json.loads((args.repo/'replication/r6/output/kernel_certificate.json').read_text())
    start=time.perf_counter(); mix=Mixture(c.Economy(correlation=-.25),c.Economy(correlation=.25))
    result={'reviewed_commit':'24011fef6da09bc05dc79946a3c1779e1fe7d8a8',
      'source_commit':'0727e4fec022c3aa8cff0363db918ad831431c6c',
      'scope':'Same deposited endpoint policies, intervals, eight Bernstein cells per interval; full 1568-action target, 1617 states, eight dates. Author model/executor, independently implemented local count optimization. No new anchor selection or retraining.',
      'kernel_build_seconds':time.perf_counter()-start,'rows':[],
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    for row in meta['rows']:
        d=row['d']
        if d not in args.contracts: continue
        data=np.load(args.repo/f'replication/r6/output/kernel_certificate_{d:g}.npz')
        intervals=[];original_worst=0.;local_worst=0.;start=time.perf_counter()
        result['rows'].append({'d':d,'anchors':len(data['anchors']),'complete':False,'intervals':intervals})
        for i,iv in enumerate(row['intervals']):
            a,b=iv['left'],iv['right'];t0=time.perf_counter()
            upper=[data[f'upper.{i}.{n}'] for n in range(mix.steps+1)]
            lower=[[restrict(data[f'lower.{p}.{n}'],a,b) for n in range(mix.steps+1)] for p in (i,i+1)]
            original=certificate(upper,lower,depth=3)
            w=local_count(mix,a,b,d);new=certificate(w,lower,depth=3)
            slack=min(float((u-v).min()) for u,v in zip(upper,w))
            assert abs(original-iv['bound'])<2e-11
            assert slack>=-2e-11 and new<=original+2e-11
            original_worst=max(original_worst,original);local_worst=max(local_worst,new)
            intervals.append({'left':a,'right':b,'original_bound':original,'localized_count_bound':new,
              'minimum_corrected_minus_count_coefficient':slack,'elapsed_seconds':time.perf_counter()-t0})
            args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
            print('INTERVAL',d,i,original,new,flush=True)
        result['rows'][-1].update({'d':d,'anchors':len(data['anchors']),'complete':True,
          'original_uniform_bound_replayed':original_worst,'localized_count_uniform_bound':local_worst,
          'fractional_bound_reduction':1-local_worst/original_worst,
          'localized_upper_and_both_certificate_replay_seconds':time.perf_counter()-start,'intervals':intervals})
        args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
        print('ROW',d,original_worst,local_worst,flush=True)
if __name__=='__main__':main()
