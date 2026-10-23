"""Rebuild the six frozen R96 payloads and preserve every difference.

No new actors replace a frozen confirmation actor. Exact monomial expansion
bounds quadratic function differences without confusing geometry bytes with
function values. This is a construction replay, not an independent optimizer.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,sys,time
import numpy as np
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'code'))
from matched96 import construct,encode,decode

def monomials(m):
    c=list(map(lambda x:F(float(x)),m.coefficients))
    v=c[:3]+[F(0)]*3
    for w,b,t in zip(m.directions,m.offsets,c[3:]):
        x,y=map(lambda x:F(float(x)),w);b=F(float(b))
        v[0]+=t*b*b;v[1]+=2*t*b*x;v[2]+=2*t*b*y
        v[3]+=t*x*x;v[4]+=2*t*x*y;v[5]+=t*y*y
    return v

def main():
    A=R/'audit97/reconstruction';A.mkdir(parents=True,exist_ok=True);records=[]
    for i in range(2):
        d=R/f'results96/alpha-{i}';a=np.load(d/'training.npz')
        x=a['x'];y=(a['lower']+a['upper'])/2
        for kind in ('quadratic','relu','spline'):
            t=time.perf_counter();m=construct(kind,x,y);new=encode(m);old=(d/(kind+'.bin')).read_bytes()
            (A/f'{i}-{kind}.bin').write_bytes(new)
            (A/f'{i}-{kind}-construction.json').write_text(json.dumps(m.record,indent=2,sort_keys=True)+'\n')
            item=dict(index=i,kind=kind,seconds=time.perf_counter()-t,identical=old==new,
              original_sha256=hashlib.sha256(old).hexdigest(),reconstructed_sha256=hashlib.sha256(new).hexdigest(),
              training_sha256=hashlib.sha256((d/'training.npz').read_bytes()).hexdigest(),selected_features=m.record['selected_features'])
            if kind=='quadratic':
                delta=[b-a for a,b in zip(monomials(decode(old)),monomials(m))]
                item.update(monomial_order=['1','x0','x1','x0^2','x0*x1','x1^2'],
                  exact_coefficient_difference=list(map(str,delta)),uniform_absolute_function_difference_bound=str(sum(map(abs,delta))),
                  interpretation='Triangle bound on [0,1]^2; not an action-identity guarantee.')
            records.append(item)
    out=dict(status='recorded',records=records,scope='All six original construction replays; no replacement of frozen actors and no claim of independent fitting.')
    (R/'audit97/RECONSTRUCTION97.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
