"""R38 contribution-isolating floating-point policy services.

Every initial complete policy and every changed actor is certified. The service
stops at its FIRST passing economic check; local Gram tolerances never override
that check. All rejected precision proposals, failed checks, and tuning trials
are counted. Structural recursion has the same primitive information.
"""
from __future__ import annotations
import os
for _v in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[_v]='1'
from pathlib import Path
import sys, json, time, math, resource, argparse, hashlib
import numpy as np
from verified_refresh import FixedTarget, cold_factor, gram_error
from entropic_certificate import certify, nominal_transform


def model(d=2,T=4,condition=1.,valuation=1.,sigma=.001,theta=.1):
    A=.55*np.eye(d)+.025*np.eye(d,k=1)-.015*np.eye(d,k=-1)
    Q=np.diag(np.geomspace(1.,condition,d)*valuation)
    R=np.eye(d)
    return dict(A=np.tile(A,(T,1,1)),B=np.tile(np.eye(d),(T,1,1)),
        Q=np.tile(Q,(T,1,1)),R=np.tile(R,(T,1,1)),Qf=Q.copy(),
        Sigma=sigma*np.eye(d),beta=.95,initial_radius_sq=float(d),theta=theta)


def future_values(m,K):
    T,d=K.shape[:2];P=[None]*T+[m['Qf']]
    for t in range(T-1,-1,-1):
        S=nominal_transform(P[t+1],m['Sigma'],m['theta'])
        F=m['A'][t]-m['B'][t]@K[t]
        P[t]=m['Q'][t]+K[t].T@m['R'][t]@K[t]+m['beta']*F.T@S@F
        P[t]=(P[t]+P[t].T)/2
    return P


def solve(m,eps,method,warm=None):
    T,d=m['A'].shape[:2];start=time.perf_counter()
    K=np.zeros((T,d,d)) if warm is None else warm['K'].copy()
    W={} if warm is None else {int(k):v.copy() for k,v in warm['W'].items()}
    s=dict(checks=0,failed_checks=0,actor_solves=0,own_policy_evaluation_dates=0,
        inverse_builds=0,inverse_applications=0,updates=0,rejected_steps=0,terminal_gram_checks=0,
        multiply_adds=0,warm_gate_failures=0,target_fits=0,
        native32_updates=0,native64_updates=0)
    checkpoints=[];steps=[];last=None
    def check():
        nonlocal last
        s['checks']+=1;s['own_policy_evaluation_dates']+=T
        try:
            last=certify(m,K,m['theta'],execution_error=0.)
            passed=last['policy_gap_upper']<=eps
            checkpoints.append(dict(check=s['checks'],updates=s['updates'],
                bound=last['policy_gap_upper'],passed=bool(passed)))
        except (ArithmeticError,ValueError,np.linalg.LinAlgError) as exc:
            passed=False;checkpoints.append(dict(check=s['checks'],updates=s['updates'],
                bound=None,passed=False,error=str(exc)))
        s['failed_checks']+=not passed
        return passed
    def output(ok,error=None):
        return dict(certified=bool(ok),error=error,policy_gap_upper=None if last is None else last['policy_gap_upper'],
            requested_policy_tolerance=eps,slack=None if last is None else last['policy_gap_upper']/eps,
            counts=s,checkpoints=checkpoints,steps=steps,seconds=time.perf_counter()-start,
            minimum_domain_margin=None if last is None else last['minimum_domain_margin'],
            candidate_peak_stored_bytes=int(K.nbytes+sum(v.nbytes for v in W.values())),
            state={'K':K,'W':W})
    if check(): return output(True)
    mode='adaptive' if method.startswith('adaptive') else '32' if method.startswith('fixed32') else '64'
    cache=not method.endswith('uncached')
    try:
        for sweep in range(5):
            goal=max(1e-13,.4*math.sqrt(eps)/d*(.1**sweep))
            for t in range(T-1,-1,-1):
                P=future_values(m,K);s['own_policy_evaluation_dates']+=T
                S=nominal_transform(P[t+1],m['Sigma'],m['theta'])
                if method=='structural' or t==T-1:
                    phat=S;target=None
                else:
                    M=d*S;M=(M+M.T)/2
                    target=FixedTarget(M,cache=cache);s['target_fits']+=1
                    if t in W:
                        rho=gram_error(W[t],M,target.m)
                        if not rho<.9:
                            s['warm_gate_failures']+=1
                            W[t],rho,_,_=cold_factor(M)
                    else: W[t],rho,_,_=cold_factor(M)
                    phat=W[t].T@W[t]/d
                try:
                    for j in range(33):
                        A,B,R=m['A'][t],m['B'][t],m['R'][t]
                        K[t]=np.linalg.solve(R+m['beta']*B.T@phat@B,m['beta']*B.T@phat@A)
                        s['actor_solves']+=1
                        if check(): return output(True)
                        if target is None or gram_error(W[t],target.target,target.m)<=goal: break
                        if j==32: raise ArithmeticError('Per-fit update cap exhausted')
                        W[t],rho,rec=target.step(W[t],rho,mode,terminal_tolerance=goal)
                        rec.update(date=t,sweep=sweep)
                        steps.append(rec);s['updates']+=1
                        s['native32_updates' if rec['precision']==32 else 'native64_updates']+=1
                        phat=W[t].T@W[t]/d
                finally:
                    if target is not None:
                        for key,attr in [('inverse_builds','inverse_builds'),('inverse_applications','inverse_applications'),
                            ('rejected_steps','rejected_steps'),('terminal_gram_checks','terminal_gram_checks'),('multiply_adds','scalar_multiply_adds')]:
                            s[key]+=getattr(target,attr)
        return output(False,'Complete-policy pass cap exhausted')
    except (ArithmeticError,ValueError,np.linalg.LinAlgError) as exc:
        return output(False,str(exc))


def service(spec):
    started=time.perf_counter();anchor=None;prefix=None
    m=model(**spec['economy']);eps=spec['epsilon'];method=spec['method']
    if spec.get('warm',False):
        anchor_model=model(**{**spec['economy'],'valuation':1.})
        prefix=solve(anchor_model,min(eps,1e-8),'adaptive-cached')
        if not prefix['certified']: raise RuntimeError('The declared warm setup failed')
        anchor=prefix.pop('state')
    trials=[]
    methods=('fixed32-cached','fixed64-cached') if method=='tuned-cached' else (method,)
    for trial_method in methods:
        r=solve(m,eps,trial_method,anchor);r.pop('state');r['method']=trial_method;trials.append(r)
        if r['certified']:break
    r=dict(spec=spec,certified=trials[-1]['certified'],selected_method=trials[-1]['method'],
        trials=trials,warm_setup=prefix,policy_gap_upper=trials[-1]['policy_gap_upper'],
        target_seconds=sum(t['seconds'] for t in trials),
        complete_construction_seconds=time.perf_counter()-started,
        process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        scope='Exact stored binary model and policy; full-policy certificate against all adapted finite-cost policies. Native floating proposals; outward binary64 verification. Warm setup and failed tuning trials included.')
    return r


def json_default(v):
    if isinstance(v,np.ndarray):return v.tolist()
    if isinstance(v,np.generic):return v.item()
    raise TypeError(type(v).__name__)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('spec');ap.add_argument('output');args=ap.parse_args()
    spec=json.loads(Path(args.spec).read_text());out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();r=service(spec)
    payload=json.dumps(r,default=json_default,sort_keys=True,separators=(',',':'))+'\n'
    with out.open('w') as f:f.write(payload);f.flush();os.fsync(f.fileno())
    clock=dict(service_through_fsync_seconds=time.perf_counter()-started,
        record_sha256=hashlib.sha256(payload.encode()).hexdigest())
    out.with_suffix('.clock.json').write_text(json.dumps(clock)+'\n')
    print(json.dumps(dict(certified=r['certified'],gap=r['policy_gap_upper'],seconds=clock['service_through_fsync_seconds'])))
if __name__=='__main__':main()
