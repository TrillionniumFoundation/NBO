"""A separately frozen graded-grid block; the original study stays immutable."""
from __future__ import annotations
import argparse,itertools,subprocess,sys,time,os
from pathlib import Path
import service49 as s
F=s.F; np=s.np; HERE=s.HERE
BASE_RUNG=s.rung
METHODS=('compiled-witness','tensor-fvi','graded-fvi')

def graded_axes(values,N,d):
    v=np.asarray(values).reshape((9,)*d);axes=[];weights=[]
    for j in range(d):
        curvature=[]
        for k in range(1,8):
            a=np.take(v,k-1,axis=j).ravel();b=np.take(v,k,axis=j).ravel();cc=np.take(v,k+1,axis=j).ravel()
            curvature.append(max(abs(F(float(x))-2*F(float(y))+F(float(z))) for x,y,z in zip(a,b,cc)))
        w=[max(curvature[max(1,k)-1],curvature[min(7,k+1)-1],F(1,2**40)) for k in range(8)]
        cumulative=[F(0)]
        for ww in w:cumulative.append(cumulative[-1]+ww/8)
        knots=[F(0)]
        for i in range(1,N):
            target=cumulative[-1]*i/N
            k=next(k for k in range(8) if target<=cumulative[k+1])
            exact=F(k,8)+(target-cumulative[k])/w[k]
            knots.append(F(round(exact*2**24),2**24))
        knots.append(F(1))
        if any(a>=b for a,b in zip(knots,knots[1:])):raise ValueError('Graded quantiles collide on declared lattice')
        axes.append(np.array(list(map(float,knots))));weights.append(list(map(str,w)))
    return axes,weights

def rung(N,K,M,T,p,method,d=2):
    if method!='graded-fvi':return BASE_RUNG(N,K,M,T,p,method,d)
    original=s.adaptive_axes
    try:
        s.adaptive_axes=graded_axes
        payload=BASE_RUNG(N,K,M,T,p,'curvature-fvi',d)
    finally:s.adaptive_axes=original
    payload['method']='graded-fvi'
    payload['axis_rule']='equal exact pilot-curvature mass; nearest 2^-24 interior knots, ties even'
    return payload

def service(method,T,p,repeat,out):
    if method not in METHODS:raise ValueError(method)
    original=s.rung
    try:
        s.rung=rung
        return s.service(method,T,p,repeat,2,out)
    finally:s.rung=original

def execute():
    root=HERE/'graded'
    if (root/'results').exists():raise FileExistsError('Fresh graded block required')
    freeze=s.read(HERE/'GRADED_SOURCE_SHA256.json')
    for name,digest in freeze.items():assert s.H(HERE/name)==digest,name
    (root/'results').mkdir(parents=True);(root/'audit').mkdir(exist_ok=True)
    if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
    start=time.perf_counter();jobs=[]
    for rep in range(3):
        for cell,(T,p) in enumerate(itertools.product((2,3),(1,4))):
            k=(rep+cell)%3;order=METHODS[k:]+METHODS[:k]
            for method in order:
                key=f'{method}-d2-T{T}-p{p}-r{rep}';begin=time.perf_counter()
                proc=subprocess.run([sys.executable,__file__,'--method',method,'--T',str(T),'--p',str(p),'--repeat',str(rep),'--out',str(root/'results/services'/key)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
                with (root/'audit/execution.log').open('a') as f:f.write(proc.stdout);f.flush();os.fsync(f.fileno())
                jobs.append({'key':key,'returncode':proc.returncode,'process_seconds':time.perf_counter()-begin});print(s.json.dumps(jobs[-1]),flush=True)
                if proc.returncode:raise RuntimeError(proc.stdout[-6000:])
    hashes={str(p.relative_to(HERE)):s.H(p) for p in sorted((root/'results').rglob('*.json'))}
    s.save(root/'audit/EXECUTION_COMPLETE.json',{'source_commit':os.environ.get('GITHUB_SHA','local'),'workflow_run':os.environ.get('GITHUB_RUN_ID'),'amendment_commit':'31d24767c40780d766fd38045d65afd466cc9562','source_hashes':freeze,'result_hashes':hashes,'jobs':jobs,'total_seconds':time.perf_counter()-start,'scope':'separate complete matched block; do not splice clocks across blocks'})

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--execute',action='store_true');a.add_argument('--method',choices=METHODS);a.add_argument('--T',type=int);a.add_argument('--p',type=int);a.add_argument('--repeat',type=int);a.add_argument('--out');v=a.parse_args()
    if v.execute:execute()
    else:service(v.method,v.T,v.p,v.repeat,v.out)
