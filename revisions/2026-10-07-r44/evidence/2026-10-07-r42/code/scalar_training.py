"""Capped own-future neural training; no conventional labels or frozen weights."""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
from pathlib import Path
import sys,time,json,hashlib,platform
import numpy as np
R=Path(__file__).resolve().parents[1]; OLD=R.parent/'2026-10-07-r41'
sys.path.insert(0,str(OLD/'code'))
import neural_chain as nc
import nonlinear as nl
TARGETS=(.06,.04); LADDER=((512,256),(1024,512),(2048,1024))
SEEDS=(104729,130363,155921)
def fit(x,y,seed,width=63,steps=400):
    import torch
    torch.set_num_threads(1); torch.manual_seed(seed)
    rng=np.random.default_rng(seed)
    # Randomized feature locations, not a conventional dynamic-programming teacher.
    b=-(np.arange(1,width+1)+rng.uniform(-.3,.3,width))/(width+1)
    w=np.exp(rng.normal(0,.025,width)); b=b*w
    X=np.column_stack((np.ones(len(x)),x,np.maximum(x[:,None]*w+b,0)))
    co=np.linalg.lstsq(X,y,rcond=1e-12)[0]
    params=[torch.nn.Parameter(torch.tensor(z,dtype=torch.float64)) for z in (w,b,co[2:],co[1],co[0])]
    initial=[p.detach().clone() for p in params]; xt=torch.tensor(x,dtype=torch.float64); yt=torch.tensor(y,dtype=torch.float64)
    opt=torch.optim.Adam(params,lr=5e-5)
    for _ in range(steps):
        opt.zero_grad(); W,B,C,L,D=params
        pred=D+L*xt+(torch.relu(xt[:,None]*W+B)*C).sum(1)
        loss=((pred-yt)**2).mean(); loss.backward(); opt.step()
    w,b,c,l,d=[p.detach().numpy().copy() for p in params]
    # A final output-layer least-squares calibration is charged as training.
    X=np.column_stack((np.ones(len(x)),x,np.maximum(x[:,None]*w+b,0)))
    co=np.linalg.lstsq(X,y,rcond=1e-12)[0]
    return dict(w=w.tolist(),b=b.tolist(),c=co[2:].tolist(),linear=float(co[1]),intercept=float(co[0]),
                seed=seed,width=width,optimizer_steps=steps,
                hidden_weight_change=max(float((params[j]-initial[j]).detach().abs().max()) for j in (0,1)),
                training_mse=float(np.mean((X@co-y)**2)),training_max_error=float(np.max(abs(X@co-y))),
                training_feature_evaluations=(steps+2)*len(x)*width,
                least_squares_shape=[len(x),width+2],least_squares_calls=2)

def train(price,theta,seed):
    start=time.perf_counter();x=np.linspace(0,1,513); a=np.linspace(0,.25,257); nets=[None]*5; logs=[]
    for t in range(4,-1,-1):
        ts=time.perf_counter()
        if t==4:y=nl.terminal(nl.I.point(x)).midpoint(); transitions=0
        else:
            ys=[]
            for j in range(0,len(x),32):
                q=nc.qvalues(nets[t+1],x[j:j+32],a,theta,price)
                ys.extend(nl.I(np.min(q.lo,axis=1),np.min(q.hi,axis=1)).midpoint())
            y=np.asarray(ys);transitions=len(x)*len(a)*3
        target_seconds=time.perf_counter()-ts; fs=time.perf_counter()
        nets[t]=fit(x,y,seed+t)
        logs.append(dict(date=t,target_seconds=target_seconds,fit_seconds=time.perf_counter()-fs,
                         target_sha256=hashlib.sha256(y.tobytes()).hexdigest(),transitions=transitions))
    return nets,logs,time.perf_counter()-start

def neural_service(price,theta,seed,checkpoint=None):
    ts=time.perf_counter(); nets,training,train_seconds=train(price,theta,seed); attempts=[]
    crossings={str(e):None for e in TARGETS}
    for N,A in LADDER:
        v=nc.certify_chain(nets,price,theta,N,A)
        import deployment
        v['numerical_execution']=deployment.apply(v)
        attempts.append(v)
        if checkpoint is not None:checkpoint(dict(networks=nets,training=training,attempt=v),len(attempts)-1)
        for eps in TARGETS:
            if crossings[str(eps)] is None and v['policy_gap_upper']<=eps:
                crossings[str(eps)]=dict(attempt=len(attempts)-1,seconds_through_checkpoint_fsync=time.perf_counter()-ts)
        if all(z is not None for z in crossings.values()):break
    return dict(method='direct-neural',price=price,theta=theta,seed=seed,networks=nets,
                training=training,training_seconds=train_seconds,attempts=attempts,crossings=crossings,
                conventional_training_labels=0,inherited_weights=0,spline_fallbacks=0,
                accepted_global_bound=attempts[-1]['policy_gap_upper'],
                target_transition_evaluations=sum(z['transitions'] for z in training),
                verification_transition_evaluations=sum(z['bellman_transition_evaluations'] for z in attempts),
                training_feature_evaluations=sum(z['training_feature_evaluations'] for z in nets),
                seconds_through_checkpoint_fsync=time.perf_counter()-ts)

def spline_service(price,theta,seed,checkpoint=None):
    ts=time.perf_counter();attempts=[];crossings={str(e):None for e in TARGETS}
    # Conventional method has its own lower starting resolution and no neural fit.
    for N,A in ((256,128),)+LADDER:
        v=nl.construct(N,A,4,theta,price); q=nl.own_value(v,[.125,.25,.5,.75])
        lower=nl.spline(nl.I.point([.125,.25,.5,.75]),v['knots'],v['values'][0])-v['lower_value_shift']
        v['own_policy_values']=dict(states=[.125,.25,.5,.75],lower=q.lo,upper=q.hi)
        v['statewise_policy_gap_upper']=(q-nl.I.point(lower.lo)).hi
        attempts.append(v)
        if checkpoint is not None:checkpoint(dict(attempt=v),len(attempts)-1)
        for eps in TARGETS:
            if crossings[str(eps)] is None and v['policy_gap_upper']<=eps:
                crossings[str(eps)]=dict(attempt=len(attempts)-1,seconds_through_checkpoint_fsync=time.perf_counter()-ts)
        if all(z is not None for z in crossings.values()):break
    return dict(method='spline',price=price,theta=theta,seed=seed,attempts=attempts,crossings=crossings,
                accepted_global_bound=attempts[-1]['policy_gap_upper'],
                verification_transition_evaluations=sum(z['bellman_transition_evaluations'] for z in attempts),
                seconds_through_checkpoint_fsync=time.perf_counter()-ts)

def save_service(path,result,start):
    raw=(json.dumps(result,default=nl.encode,sort_keys=True,separators=(',',':'))+'\n').encode()
    with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    clock=dict(seconds_through_fsync=time.perf_counter()-start,record_sha256=hashlib.sha256(raw).hexdigest(),
               crossings=result['crossings'],method=result['method'],price=result['price'],theta=result['theta'],seed=result['seed'],
               all_state_gap=result['accepted_global_bound'],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               python=platform.python_version(),numpy=np.__version__,process_initialization_in_clock=False,frequency_controlled=False)
    path.with_suffix('.clock.json').write_text(json.dumps(clock,indent=2,sort_keys=True)+'\n')
    print(json.dumps(clock),flush=True)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--directory',required=True);p.add_argument('--pilot',action='store_true'); args=p.parse_args()
    dest=Path(args.directory);dest.mkdir(parents=True,exist_ok=True)
    import torch
    torch.set_num_threads(1)
    for price in ([1] if args.pilot else [1,4]):
      for theta in ([0] if args.pilot else [0,1]):
       for seed in (SEEDS[:1] if args.pilot else SEEDS):
        for method in ['direct-neural','spline']:
         path=dest/f'{method}-p{price}-r{theta}-s{seed}.json'
         if path.exists():raise FileExistsError(path)
         ts=time.perf_counter();result=(neural_service if method=='direct-neural' else spline_service)(price,theta,seed)
         save_service(path,result,ts)
