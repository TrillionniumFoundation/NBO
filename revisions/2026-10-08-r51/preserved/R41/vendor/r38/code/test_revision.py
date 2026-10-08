"""Deterministic regression checks; tests supplement, not replace, the proofs."""
from pathlib import Path
import sys,json,math,hashlib
import numpy as np
import mpmath as mp
from verified_refresh import FixedTarget,cold_factor,gram_error,fit
from nonlinear import I,exp_bound,log_bound,construct,own_value,action
from policy_study import model,solve


def run():
    checks=[];mp.mp.dps=100
    for x in [-16.,-2.,-.1,0.,.1,2.,16.]:
        a=exp_bound(I.point(x));truth=mp.exp(mp.mpf(x));assert mp.mpf(float(a.lo))<=truth<=mp.mpf(float(a.hi))
        checks.append('exp:'+str(x))
    for x in [.0001,.01,.5,1.,2.,20.,1e6]:
        a=log_bound(I.point(x));truth=mp.log(mp.mpf(x));assert mp.mpf(float(a.lo))<=truth<=mp.mpf(float(a.hi))
        checks.append('log:'+str(x))
    for d in [2,4,8]:
        M=np.diag(np.linspace(1,4,d))+.015625*(np.eye(d,k=1)+np.eye(d,k=-1))
        W,rho,m,L=cold_factor(M,d+2)
        for precision in [32,64]:
            target=FixedTarget(M);V,info=target.propose(W,precision)
            wm=mp.matrix(W.tolist());mm=mp.matrix(M.tolist())
            ideal=wm*(3*mp.eye(d)-mm**-1*wm.T*wm)*mp.mpf('.5')
            error=mp.norm(mp.matrix(V.tolist())-ideal)/mp.sqrt(mp.mpf(m))
            assert error<=mp.mpf(info['relative_step_error']);checks.append(f'whole-step:{d}:{precision}')
        wf,rec=fit(M,1e-9);assert rec['certified'] and rec['relative_gram_upper']<=1e-9
        checks.append('factor-stop:'+str(d))
    for method in ['fixed64-cached','fixed64-uncached','adaptive-cached','adaptive-uncached','fixed32-cached','structural']:
        r=solve(model(condition=4.),1e-4,method);assert r['certified']
        assert r['checkpoints'][-1]['passed'] and not any(x['passed'] for x in r['checkpoints'][:-1])
        checks.append('first-policy-check:'+method)
    a=solve(model(condition=4.),1e-4,'adaptive-cached')
    b=solve(model(condition=4.),1e-4,'adaptive-uncached')
    assert np.array_equal(a['state']['K'],b['state']['K'])
    assert a['counts']['inverse_builds']<b['counts']['inverse_builds'];checks.append('cache-isolates-proposals')
    bad=model();bad['Sigma']*=10000
    r=solve(bad,1e-4,'adaptive-cached');assert not r['certified'];checks.append('moment-domain-fails-closed')
    r=construct(32,16,3);v=own_value(r,[.125,.25,.5,.75]);assert np.all(v.lo<=v.hi)
    assert np.all((action(r,0,np.linspace(0,1,2001))>=0)&(action(r,0,np.linspace(0,1,2001))<=.25))
    checks+=['nonlinear-policy-interval','continuous-state-feasibility']
    return dict(passed=len(checks),failed=0,checks=checks,qualification='Finite regression checks; mathematical validity rests on the stated arithmetic and comparison assumptions')

if __name__=='__main__':
    result=run();print(json.dumps(result,indent=2))
    if len(sys.argv)>1:Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')
