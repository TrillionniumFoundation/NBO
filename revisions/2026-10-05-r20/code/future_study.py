"""Frozen R20 future-change services: no outcome-dependent task selection.

The R19 numerical modules and finite-law inputs are immutable dependencies.
New code changes future primitives, not the inherited fitting architecture.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, os, platform, sys, time, traceback
from pathlib import Path
START = time.perf_counter()
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent / '2026-10-05-r19-integrated'
sys.path.insert(0, str(BASE / 'code'))
import numpy as np
import torch
from economy import Economy, tasks, checksum
from methods import construct, select
from intervals import I, environment_check

DEPENDENCIES = {
 'code/economy.py':'41d04275ba9bdfb499a2f8888c837f1bac397b19a01fffd633b6a93388ec4fee',
 'code/methods.py':'c231d193803da3fe9de02b176e284dcda04431d3434c86a8cd0cb9a8ae4dde53',
 'code/intervals.py':'6e1fa54dcaf322a8c91eef02f8d1927cf68535dfc2f512f91689a4ad992e8a63',
 'protocols/economy_d10.json':'5ffa90b2352deff7f573c489eac6f1ea7f435572ab227b29552950c78e13d7e9',
 'protocols/economy_d50.json':'da843bf2b56334c305be67eb121c7096c0aa5e80e0be2a7dd941875b9a1a5217'}
REGIMES = [('anchor',.55,.08,1.), ('future_withdrawal_low',.25,.08,1.),
           ('future_withdrawal_high',.85,.08,1.), ('future_production',.55,.24,1.),
           ('future_utility',.55,.08,2.)]
SERVICES = ['NBO-reuse','NBO-adaptive','NBO-refit','quadratic-adaptive',
            'rbf-adaptive','SAA','enumerated']
VOLUMES = [1,16,256,1024]
STREAMS = [200501,200502,200503]
TOLERANCE = 1e-4


def save(path, obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('w') as f:
        json.dump(obj,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
        f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)
    fd=os.open(path.parent,os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)


def check_source():
    for name,h in DEPENDENCIES.items():
        if hashlib.sha256((BASE/name).read_bytes()).hexdigest()!=h:
            raise RuntimeError('inherited source changed: '+name)
    environment_check()
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


class FutureEconomy(Economy):
    """Only future primitives vary; the current postdecision map stays fixed."""
    def __init__(self, inputs, regime):
        x=copy.deepcopy(inputs);name,u,lam,mult=regime
        self.current_lam=inputs['coupling'];self.regime=name
        x['reference']=u;x['coupling']=lam
        for k in range(1,4):
            # Resulting stored binary64 coefficients define this finite model.
            x['constants'][k]=float(mult*(inputs['W'][k]*(-u)+inputs['A'][k]*(np.log(u)-.1*u*u/2)))
            x['W'][k]=float(mult*inputs['W'][k])
        x['terminal_gamma']=float(mult*inputs['terminal_gamma'])
        if name=='anchor': x=copy.deepcopy(inputs)
        super().__init__(x)
    def post(self,y,a):
        return y+self.h*(self.c0+self.current_lam*torch.tanh(self.mix_state(y))-a[:,None])
    def interval_derivative(self,y,a,t):
        yn=y.detach().numpy();an=a.detach().numpy();tn=t.detach().numpy()
        mix=lambda q:(1-I(self.mix))*q+self.mix*q.mean(-1,True)
        yy=I(yn)+self.h*(self.c0+self.current_lam*mix(I(yn)).tanh()-I(an)[:,None])
        yy=yy[None,:,:]+I(self.noise[:,0,None,:])
        pp=I(np.full(yy.lo.shape,-self.h));der=I(np.zeros(yy.lo.shape[:-1]))
        for k in range(1,4):
            tan=mix(yy).tanh();prod=self.lam*tan
            dp=self.lam*(1-tan.square())*mix(pp)
            der=der+self.W[k]*dp.mean(-1)
            yy=yy+self.h*(self.c0+prod-self.ref)+I(self.noise[:,k,None,:])
            pp=pp+self.h*dp
        der=der-self.gamma*((yy-yy.mean(-1,True))*pp).mean(-1)
        cur=self.A[0]*(I(tn[:,0])/I(an)-I(tn[:,1])*I(an)-I(tn[:,2]))-self.W[0]
        return cur+der.mean(0)
    def curvature_lower(self,y,t):
        # The inherited bound uses lam to bound both initial spread and future
        # curvature. It remains an upper bound since every lam >= current_lam.
        if self.lam<self.current_lam: raise ValueError('initial-spread bound invalid')
        return super().curvature_lower(y,t)


def optimal_action_interval(a,t,cert):
    """Strong concavity gives |a-a*| <= residual/kappa, outward evaluated."""
    av=a.detach().numpy();cap=t[:,3].numpy()
    lo=np.asarray(cert['derivative_lower']);hi=np.asarray(cert['derivative_upper'])
    r=np.maximum(np.abs(lo),np.abs(hi))
    r=np.where(av==.05,np.maximum(0,hi),r)
    r=np.where(av==cap,np.maximum(0,-lo),r)
    radius=(I(r)/I(cert['kappa_lower'])).hi
    band=I(av)+I(-radius,radius)
    return I(np.maximum(.05,band.lo),np.minimum(cap,band.hi))


def mechanism(e,model,y,t,a):
    """Descriptive exact-finite-law risks, outside the service stopping clock."""
    with torch.no_grad():
        grid=torch.stack([torch.full_like(a,.05),(.05+t[:,3])/2,t[:,3]],1)
        truth=torch.stack([e.future(e.post(y,grid[:,j])).mean(0) for j in range(3)],1)
        pred=torch.stack([model(e.post(y,grid[:,j])) for j in range(3)],1)
        err=pred-truth;rewards=torch.stack([e.current(grid[:,j],t) for j in range(3)],1)
        trueq=truth+rewards;predq=pred+rewards
        chosen=predq.argmax(1);best=trueq.argmax(1)
        own=model(e.post(y,a))-e.future(e.post(y,a)).mean(0)
        loss=trueq.max(1).values-trueq[torch.arange(len(y)),chosen]
        binary=(predq[:,2]>=predq[:,0])!=(trueq[:,2]>=trueq[:,0])
        return dict(absolute_risk=float(err.square().mean()),centered_risk=float((err-err.mean(1,keepdim=True)).square().mean()),
            own_action_risk=float(own.square().mean()),three_action_loss=float(loss.mean()),
            misclassification=float((chosen!=best).double().mean()),binary_misclassification=float(binary.double().mean()),
            binary_loss=float((torch.abs(trueq[:,2]-trueq[:,0])*binary).mean()))


def run_service(d,q,seed,service,out):
    begin=time.perf_counter();record=dict(dimension=d,queries_per_regime=q,total_queries=5*q,stream=seed,service=service,regimes=[])
    data=json.loads((BASE/f'protocols/economy_d{d}.json').read_text())
    economies=[FutureEconomy(data,r) for r in REGIMES]
    y,t=tasks(q,d,200700+d)
    record['task_sha256']=checksum(np.c_[y.numpy(),t.numpy()])
    record['finite_inputs']={e.regime:e.inputs for e in economies}
    record['initialization_seconds']=time.perf_counter()-begin
    kind=service.split('-')[0];adaptive=service.endswith('-adaptive')
    reused=adaptive or service.endswith('-reuse')
    initial_fit=time.perf_counter()
    anchor,ids=construct(economies[0],kind,seed,0) if reused else (None,[])
    record['anchor_fit_seconds']=time.perf_counter()-initial_fit if reused else 0.
    record['anchor_cache_ids']=ids;diagnostic_seconds=0.;total_regime_service=0.
    for e in economies:
        start=time.perf_counter();row=dict(regime=e.regime,attempts=[]);model=anchor
        attempts=[('reuse',None)] if reused else [('fit',0)]
        if adaptive: attempts.append(('refresh',1))
        if not reused and kind!='enumerated': attempts.append(('fit',1))
        for label,stage in attempts:
            b=time.perf_counter()
            if stage is not None: model,cache=construct(e,kind,seed,stage)
            else: cache=ids
            fit=time.perf_counter()-b if stage is not None else 0.
            b=time.perf_counter();a=select(e,kind,model,y,t);query=time.perf_counter()-b
            b=time.perf_counter();cert=e.certify(y,a,t);verification=time.perf_counter()-b
            item=dict(kind=label,stage=stage,cache_ids=cache,fit_seconds=fit,query_seconds=query,
                      verification_seconds=verification,actions=a.tolist(),certificate=cert)
            row['attempts'].append(item);row['certified']=cert['mean_regret_upper']<=TOLERANCE
            # Charge durable failed checks before the service clock is read.
            save(out.with_name(out.stem+'_'+e.regime+'.json'),row)
            if row['certified']: break
        row['service_seconds']=time.perf_counter()-start
        total_regime_service+=row['service_seconds']
        b=time.perf_counter();row['mechanism']=mechanism(e,model,y,t,a)
        if kind=='enumerated':
            band=optimal_action_interval(a,t,cert);zero=t.clone();zero[:,2]=0.
            az=select(e,kind,model,y,zero);cz=e.certify(y,az,zero)
            bz=optimal_action_interval(az,zero,cz);response=(bz-band).mean()
            mean=band.mean()
            row['economic_certificate']=dict(mean_optimal_action=[float(mean.lo),float(mean.hi)],
                mean_withdrawal_reduction_due_to_charge=[float(response.lo),float(response.hi)],
                zero_charge_actions=az.tolist(),zero_charge_certificate=cz)
        row['diagnostic_seconds']=time.perf_counter()-b;diagnostic_seconds+=row['diagnostic_seconds']
        record['regimes'].append(row)
    record['all_regimes_certified']=all(x['certified'] for x in record['regimes'])
    record['accounted_service_seconds']=record['initialization_seconds']+record['anchor_fit_seconds']+total_regime_service
    record['diagnostic_seconds']=diagnostic_seconds
    record['wall_before_final_record_seconds']=time.perf_counter()-begin
    b=time.perf_counter();save(out,record);record['final_record_write_seconds']=time.perf_counter()-b
    record['accounted_service_seconds']+=record['final_record_write_seconds']
    # This metadata-only rewrite is charged to the full comparison, not hidden.
    save(out,record)
    return record


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/future-study');args=p.parse_args()
    if args.out.exists(): raise RuntimeError('refusing to overwrite an execution directory')
    args.out.mkdir(parents=True);digest=check_source()
    env=dict(source_sha256=digest,source_commit=os.environ.get('GITHUB_SHA','local'),run_id=os.environ.get('GITHUB_RUN_ID'),
        python=sys.version,numpy=np.__version__,torch=torch.__version__,platform=platform.platform(),threads=torch.get_num_threads(),
        dependencies=DEPENDENCIES,regimes=REGIMES,services=SERVICES,volumes=VOLUMES,streams=STREAMS,tolerance=TOLERANCE)
    save(args.out/'DESIGN_AND_ENVIRONMENT.json',env)
    rows=[];failed=[]
    for d in [10,50]:
        for q in VOLUMES:
            for seed in STREAMS:
                for service in SERVICES:
                    b=time.perf_counter();name=f'd{d}_q{q}_s{seed}_{service}.json'
                    try:
                        row=run_service(d,q,seed,service,args.out/name);rows.append(row)
                        print(d,q,seed,service,row['all_regimes_certified'],row['accounted_service_seconds'],flush=True)
                    except Exception:
                        failure=dict(dimension=d,queries_per_regime=q,stream=seed,service=service,
                            elapsed_seconds=time.perf_counter()-b,traceback=traceback.format_exc())
                        failed.append(failure);save(args.out/(name+'.failure.json'),failure);print('FAIL',failure,flush=True)
    summary=dict(environment=env,records=rows,failures=failed,expected_services=168,expected_regime_outcomes=840,
        full_comparative_seconds=time.perf_counter()-START,scope='finite stored laws; three new fixed streams; all tasks and failed checks retained')
    save(args.out/'SUMMARY.json',summary)
    print('COMPLETE',len(rows),'FAILURES',len(failed),flush=True)
    if failed: raise SystemExit(1)

if __name__=='__main__': main()
