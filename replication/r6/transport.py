#!/usr/bin/env python3
"""Count-information relaxation for a continuum of transition laws.
Exact finite-state Bernstein recursions; no interpolation of optimal values in
transition parameters. A complete count-informed solve gives an upper bound;
count-BLIND feasible policies give lower bounds. All calculations are float64.
"""
from __future__ import annotations
from common import *
import argparse,math
import contracts as c

def bernstein_value(coeff,t):
    """de Casteljau evaluation along the first axis, t in [0,1]."""
    a=np.array(coeff,copy=True)
    for _ in range(len(a)-1):a=(1-t)*a[:-1]+t*a[1:]
    return a[0]

def split(coeff,t=.5):
    levels=[np.asarray(coeff)]
    while len(levels[-1])>1:
        a=levels[-1];levels.append((1-t)*a[:-1]+t*a[1:])
    return np.stack([a[0] for a in levels]),np.stack([a[-1] for a in levels[::-1]])

def restrict(coeff,left,right):
    """Exact Bernstein coefficients on the closed subinterval."""
    if not 0<=left<right<=1:raise ValueError('invalid interval')
    if right<1:coeff=split(coeff,right)[0]
    if left>0:coeff=split(coeff,left/right)[1]
    return coeff

class Mixture:
    """Same actions/states, iid per-step mixture of two killed kernels."""
    def __init__(self,e0,e1):
        if e0.steps!=e1.steps or not np.array_equal(e0.states,e1.states) or not np.array_equal(e0.menu,e1.menu):
            raise ValueError('mixture requires common states, dates and menus')
        self.backend_checks=[accelerate_kernel(e0),accelerate_kernel(e1)]
        self.e=(e0,e1);self.steps=e0.steps;self.ns=e0.ns
        self.terminal=c.old.terminal(e0.states)
    def q(self,k,n,v,d,cost=2.):
        e=self.e[k];kernel=e.common
        out=kernel.base+d*kernel.duration-cost*kernel.effort+kernel.continuation(v)
        if e.extra:
            z=e.extra[n]
            out=np.concatenate([out,z.base+d*z.duration-cost*z.effort+z.continuation(v)],axis=1)
        return out
    def selected(self,k,n,pol,v,d,cost=2.):
        e=self.e[k];r=np.arange(self.ns);a=np.minimum(pol,len(e.menu)-1);z=e.common
        out=z.base[r,a]+d*z.duration[r,a]-cost*z.effort[r,a]+z.selected(a,v)
        mask=pol>=len(e.menu)
        if e.extra and mask.any():
            a=np.maximum(pol-len(e.menu),0);z=e.extra[n]
            other=z.base[r,a]+d*z.duration[r,a]-cost*z.effort[r,a]+z.selected(a,v)
            out[mask]=other[mask]
        return out
    def solve(self,t,d,allowed=None):
        start=time.perf_counter();v=np.empty((self.steps+1,self.ns));v[-1]=self.terminal
        p=np.zeros((self.steps,self.ns),np.int32)
        for n in range(self.steps-1,-1,-1):
            q=(1-t)*self.q(0,n,v[n+1],d)+t*self.q(1,n,v[n+1],d)
            if allowed is not None:q=np.where(allowed,q,-np.inf)
            p[n]=q.argmax(1);v[n]=q[np.arange(self.ns),p[n]]
        return dict(value=v,policy=p,seconds=time.perf_counter()-start)
    def evaluate(self,pol,t,d):
        v=np.empty((self.steps+1,self.ns));v[-1]=self.terminal
        for n in range(self.steps-1,-1,-1):
            v[n]=(1-t)*self.selected(0,n,pol[n],v[n+1],d)+t*self.selected(1,n,pol[n],v[n+1],d)
        return v
    def policy_coefficients(self,pol,d):
        coeff=[None]*(self.steps+1);coeff[-1]=self.terminal[None,:]
        for n in range(self.steps-1,-1,-1):
            h=self.steps-n;z=[]
            for j in range(h+1):
                v=np.zeros(self.ns)
                if j<h:v+=(1-j/h)*self.selected(0,n,pol[n],coeff[n+1][j],d)
                if j>0:v+=j/h*self.selected(1,n,pol[n],coeff[n+1][j-1],d)
                z.append(v)
            coeff[n]=np.stack(z)
        return coeff
    def upper_coefficients(self,d,first_sign=None):
        """Optimal values with future regime-count information, not a feasible
        original-model policy. The max is taken only AFTER combining branches.
        """
        coeff=[None]*(self.steps+1);coeff[-1]=self.terminal[None,:]
        for n in range(self.steps-1,-1,-1):
            h=self.steps-n;z=[]
            for j in range(h+1):
                q=None
                if j<h:q=(1-j/h)*self.q(0,n,coeff[n+1][j],d)
                if j>0:
                    add=j/h*self.q(1,n,coeff[n+1][j-1],d)
                    q=add if q is None else q+add
                if n==0 and first_sign is not None:q=np.where(first_sign,q,-np.inf)
                z.append(q.max(1))
            coeff[n]=np.stack(z)
        return coeff

def envelope_certificate(upper,lower,left=0.,right=1.,depth=5):
    """min_i max_j(U_j-J_ij) bounds U-max_i J_i at every state and date.
    Subdivision tightens the bound without solving another target MDP.
    """
    cells=[];worst=0.
    grid=np.linspace(left,right,2**depth+1)
    for a,b in zip(grid[:-1],grid[1:]):
        local=0.;where=None
        for n,u in enumerate(upper):
            ur=restrict(u,a,b);g=np.stack([(ur-restrict(x[n],a,b)).max(0) for x in lower])
            best=g.min(0);j=int(best.argmax())
            if float(best[j])>local:local=float(best[j]);where=[n,j]
        cells.append(dict(left=a,right=b,bound=max(0.,local),location=where));worst=max(worst,local)
    return dict(bound=max(0.,worst),cells=cells)

def run(full=True):
    build=time.perf_counter()
    args={} if full else dict(shape=(17,25),steps=4,counts=(5,5,7),include_neural=False)
    e0=c.Economy(correlation=-.25,**args);e1=c.Economy(correlation=.25,**args)
    mix=Mixture(e0,e1);center=int(np.linalg.norm(e0.states-[2,1.25],axis=1).argmin())
    result=dict(target='same-state/action killed-chain mixture; regime iid at each date and unknown before control',
        interpretation='theta is the probability of the +0.25-correlation quadrature law rather than the -0.25 law; not a Brownian correlation interpolation',
        states=e0.ns,dates=e0.steps,common_actions=len(e0.menu),extra_actions=3 if e0.extra else 0,
        theta_interval=[0.,1.],backend_checks=mix.backend_checks,kernel_build_seconds=time.perf_counter()-build,rows=[],source_sha256=sha(__file__))
    for d in (0.,.5,1.):
        print('TRANSPORT d',d,flush=True);start=time.perf_counter()
        solved=[mix.solve(t,d) for t in (0.,.5,1.)]
        lower=[mix.policy_coefficients(z['policy'],d) for z in solved]
        upper=mix.upper_coefficients(d);offline=time.perf_counter()-start
        cert=envelope_certificate(upper,lower,depth=5);validations=[];saved={}
        for n in range(mix.steps+1):
            saved[f'upper.{n}']=upper[n]
            for i,co in enumerate(lower):saved[f'lower.{i}.{n}']=co[n]
        for i,z in enumerate(solved):saved[f'policy.{i}']=z['policy']
        for t in (0.,.125,.25,.375,.5,.625,.75,.875,1.):
            direct=mix.solve(t,d);vals=np.stack([[bernstein_value(x,t) for x in co] for co in lower])
            chosen=vals[:,:-1].argmax(0);pols=np.stack([z['policy'] for z in solved])
            sw=np.take_along_axis(pols,chosen[None],0)[0];sv=mix.evaluate(sw,t,d)
            uv=np.stack([bernstein_value(x,t) for x in upper])
            replay=max(float(abs(vals[i]-mix.evaluate(z['policy'],t,d)).max()) for i,z in enumerate(solved))
            assert replay<1e-11 and (uv-direct['value']).min()>-1e-10
            assert (sv-vals.max(0)).min()>-1e-10
            gap=direct['value']-sv
            assert gap.min()>-1e-10 and gap.max()<=cert['bound']+1e-10
            validations.append(dict(theta=t,focal_value=direct['value'][0,center],focal_control=e0.controls(direct['policy'])[0,center],
                actual_max_loss=gap.max(),upper_slack_max=(uv-direct['value']).max(),coefficient_replay_error=replay))
        np.savez_compressed(OUT/f'transport_{d:g}.npz',**saved)
        result['rows'].append(dict(d=d,offline_seconds=offline,optimal_target_solves_for_bank=3,
            count_informed_states_per_physical_state=(mix.steps+1)*(mix.steps+2)//2,
            uniform_all_theta_date_state_bound=cert['bound'],subdivisions=32,certificates=cert['cells'],validations=validations))
        print('TRANSPORT bound',d,cert['bound'],flush=True);save('transport.json',result)
    return result

def unit_tests():
    rng=np.random.default_rng(416);mx=0.
    for h in range(1,10):
        coeff=rng.normal(size=(h+1,7));l,r=split(coeff,.37)
        for t in np.linspace(0,1,17):
            mx=max(mx,float(abs(bernstein_value(l,t)-bernstein_value(coeff,.37*t)).max()))
            mx=max(mx,float(abs(bernstein_value(r,t)-bernstein_value(coeff,.37+.63*t)).max()))
    assert mx<1e-12
    vals=[t*(1-t) for t in (0.,.5,1.)]
    assert vals[1]>.5*(vals[0]+vals[-1])
    return dict(de_casteljau_max_error=mx,invalid_kernel_chord_counterexample=vals)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--small',action='store_true');a=ap.parse_args()
    save('transport_unit_tests.json',unit_tests());run(not a.small)
