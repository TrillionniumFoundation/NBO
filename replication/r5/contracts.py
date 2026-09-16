#!/usr/bin/env python3
"""Contract transfer for an explicitly finite killed Markov chain.
All controls and kernels are explicit. R4 arrays are immutable inputs.
Certificates are double-precision, not interval-arithmetic or diffusion bounds.
"""
from __future__ import annotations
import argparse, hashlib, json, sys, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'replication/r4'))
import solver as old

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

class Kernel:
    """Positive interpolation kernel and base, duration, effort rewards."""
    def __init__(self, states, actions, shape, h, model):
        self.shape, self.ns = shape, len(states)
        if self.ns >= 65536:
            raise ValueError('uint16 indices require fewer than 65536 states')
        if actions.ndim == 2:
            actions = np.broadcast_to(actions, (self.ns,) + actions.shape)
        self.actions = actions
        na = actions.shape[1]
        self.index = np.empty((self.ns, na, 16), dtype=np.uint16)
        self.weight = np.empty((self.ns, na, 16))
        self.base = np.empty((self.ns, na))
        self.duration = np.empty_like(self.base)
        self.effort = np.empty_like(self.base)
        self.exit_discount = np.empty_like(self.base)
        size = np.array(shape) - 1
        for first in range(0, self.ns, 64):
            sl = slice(first, min(first + 64, self.ns))
            s, a = states[sl, None, :], actions[sl]
            y, live, disc, flow, effort, _, alpha = old.transition(s, a, h, model)
            ann = -np.expm1(-model.rho * h * alpha) / model.rho
            self.base[sl] = (flow + model.k * effort + disc * (~live) * old.terminal(y)).mean(-1)
            self.duration[sl] = ann.mean(-1)
            self.effort[sl] = effort.mean(-1)
            self.exit_discount[sl] = (disc * (~live)).mean(-1)
            z = (y - old.LO) / (old.HI - old.LO) * size
            ij = np.minimum(np.maximum(np.floor(z).astype(int), 0), size - 1)
            f = z - ij
            p, q = f[..., 0], f[..., 1]
            for corner, (di, dj, w) in enumerate(((0, 0, (1-p)*(1-q)), (1, 0, p*(1-q)),
                                                 (0, 1, (1-p)*q), (1, 1, p*q))):
                self.index[sl, :, corner::4] = ((ij[..., 0]+di)*shape[1]+ij[..., 1]+dj)
                self.weight[sl, :, corner::4] = disc * live * w / 4
        assert self.weight.min() >= -1e-14
        assert self.weight.sum(-1).max() <= np.exp(-model.rho*h)+1e-12
    def continuation(self, value):
        out = np.empty(self.base.shape)
        for first in range(0, self.ns, 128):
            sl = slice(first, min(first+128, self.ns))
            out[sl] = (self.weight[sl] * value[self.index[sl]]).sum(-1)
        return out
    def selected(self, policy, value):
        row = np.arange(self.ns)
        return (self.weight[row, policy] * value[self.index[row, policy]]).sum(-1)

class Economy:
    def __init__(self, shape=(33,49), steps=8, counts=(9,9,13), k=2., correlation=-.25,
                 include_neural=True):
        start = time.perf_counter()
        self.shape, self.steps, self.k = tuple(shape), steps, k
        self.model = old.Model(k=k, correlation=correlation)
        ss, bd = old.grid(*shape)
        self.states, self.boundary = ss.reshape(-1,2), bd.ravel()
        self.ns = len(self.states)
        self.menu = old.action_mesh(counts)
        if include_neural:
            # Include EVERY published R4 diagnostic action, not just a nonnested
            # finer-looking reference mesh. Both menus stay fixed across contracts.
            self.menu=np.unique(np.concatenate([self.menu,old.action_mesh((7,7,11))]),axis=0)
        self.common = Kernel(self.states, self.menu, shape, 1/steps, self.model)
        self.extra, self.r4 = [], []
        if include_neural:
            if tuple(shape) != (33,49) or steps != 8:
                raise ValueError('R4 frozen proposals require the 33x49, eight-date chain')
            for seed in (101,202,303):
                path = ROOT / f'replication/r4/output/safe_policy_{seed}.npz'
                self.r4.append(np.load(path)['policies'].reshape(steps,self.ns,3))
            for n in range(steps):
                self.extra.append(Kernel(self.states, np.stack([p[n] for p in self.r4],1),
                                         shape, 1/steps, self.model))
        self.build_seconds = time.perf_counter()-start
        self.counts = list(counts)
    def optimal(self, d, k=None):
        k = self.k if k is None else k
        start = time.perf_counter()
        value = np.empty((self.steps+1,self.ns)); value[-1] = old.terminal(self.states)
        policy = np.empty((self.steps,self.ns),dtype=np.int32)
        for n in range(self.steps-1,-1,-1):
            q = self.common.base+d*self.common.duration-k*self.common.effort+self.common.continuation(value[n+1])
            if self.extra:
                e = self.extra[n]
                q = np.concatenate((q, e.base+d*e.duration-k*e.effort+e.continuation(value[n+1])),1)
            policy[n] = np.argmax(q,1)
            value[n] = q[np.arange(self.ns),policy[n]]
        feature = self.evaluate(policy)
        assert np.max(abs(value-(feature[0]+d*feature[1]-k*feature[2]))) < 2e-11
        return dict(d=float(d),k=float(k),value=value,policy=policy,feature=feature,
                    seconds=time.perf_counter()-start)
    def evaluate(self, policy):
        result = np.zeros((3,self.steps+1,self.ns))
        result[0,-1] = old.terminal(self.states)
        rows = np.arange(self.ns)
        for n in range(self.steps-1,-1,-1):
            use = policy[n] < len(self.menu)
            a = np.minimum(policy[n],len(self.menu)-1)
            for j, name in enumerate(('base','duration','effort')):
                v = getattr(self.common,name)[rows,a]+self.common.selected(a,result[j,n+1])
                if self.extra and np.any(~use):
                    e = self.extra[n]; ea = np.maximum(policy[n]-len(self.menu),0)
                    w = getattr(e,name)[rows,ea]+e.selected(ea,result[j,n+1])
                    v[~use] = w[~use]
                result[j,n] = v
        return result
    def endpoint_discount(self, policy):
        """Independently evaluate E exp(-rho tau), including terminal stopping."""
        value=np.ones((self.steps+1,self.ns)); rows=np.arange(self.ns)
        for n in range(self.steps-1,-1,-1):
            act=np.minimum(policy[n],len(self.menu)-1)
            value[n]=self.common.exit_discount[rows,act]+self.common.selected(act,value[n+1])
            use=policy[n]>=len(self.menu)
            if self.extra and np.any(use):
                e=self.extra[n]; a=np.maximum(policy[n]-len(self.menu),0)
                other=e.exit_discount[rows,a]+e.selected(a,value[n+1])
                value[n,use]=other[use]
        return value
    def controls(self, policy):
        out = self.menu[np.minimum(policy,len(self.menu)-1)].copy()
        for n in range(self.steps):
            use = policy[n] >= len(self.menu)
            if np.any(use):
                out[n,use] = self.extra[n].actions[np.where(use)[0],policy[n,use]-len(self.menu)]
        return out
    def one_step_gain(self, value, d=0., k=None):
        k = self.k if k is None else k
        gain = np.zeros((self.steps,self.ns))
        for n in range(self.steps):
            q = self.common.base+d*self.common.duration-k*self.common.effort+self.common.continuation(value[n+1])
            best = q.max(1)
            if self.extra:
                e = self.extra[n]
                qe = e.base+d*e.duration-k*e.effort+e.continuation(value[n+1])
                best = np.maximum(best,qe.max(1))
            gain[n] = np.maximum(best-value[n],0)
        return gain
    def occupation(self, policy, initial):
        """Undiscounted decision-node masses; boundary mass is killed."""
        mass = np.asarray(initial,dtype=float).copy(); out=[]; exits=[]
        rows=np.arange(self.ns); beta=np.exp(-self.model.rho/self.steps)
        assert abs(mass.sum()-1)<1e-12 and mass.min()>=0
        for n in range(self.steps):
            out.append(mass.copy()); new=np.zeros(self.ns)
            kernels=[(self.common,policy[n]<len(self.menu),np.minimum(policy[n],len(self.menu)-1))]
            if self.extra:
                kernels.append((self.extra[n],policy[n]>=len(self.menu),np.maximum(policy[n]-len(self.menu),0)))
            for kernel,mask,act in kernels:
                ix=kernel.index[rows,act]; wt=kernel.weight[rows,act]/beta
                np.add.at(new,ix.ravel(),(mass[:,None]*mask[:,None]*wt).ravel())
            new[self.boundary]=0
            exits.append(float(mass.sum()-new.sum())); mass=new
        assert abs(sum(exits)+mass.sum()-1)<1e-11
        return np.array(out),dict(exit_probability=sum(exits),survival_probability=float(mass.sum()))

def interval_certificate(bank, left, right):
    """An endpoint chord minus the maximum of two feasible endpoint policies.
    For each date/state its maximum is at an endpoint or at the intersection
    of the two policy-value lines. No parameter sampling enters this bound.
    More library policies can only improve the certified lower envelope.
    """
    a,b=bank[left]['d'],bank[right]['d']; k=bank[left]['k']
    F=np.stack([bank[left]['feature'],bank[right]['feature']])
    intercept=(F[:,0]-k*F[:,2]).reshape(2,-1);slope=F[:,1].reshape(2,-1)
    va,vb=bank[left]['value'].ravel(),bank[right]['value'].ravel()
    uslope=(vb-va)/(b-a);uintercept=va-uslope*a
    den=slope[0]-slope[1]
    cross=np.divide(intercept[1]-intercept[0],den,out=np.full_like(den,a),where=abs(den)>1e-14)
    candidates=np.stack([np.full_like(den,a),np.full_like(den,b),np.clip(cross,a,b)])
    gaps=np.stack([uintercept+uslope*d-np.maximum(intercept[0]+slope[0]*d,intercept[1]+slope[1]*d) for d in candidates])
    j=np.argmax(gaps,axis=0);maximum=gaps[j,np.arange(len(va))];location=candidates[j,np.arange(len(va))]
    worst=int(np.argmax(maximum))
    return dict(left=float(a),right=float(b),upper_loss=float(max(0,maximum[worst])),
                worst_d=float(location[worst]),flat_location=worst,nodewise_gap=maximum)

def switching(bank,d,k):
    F=np.stack([r['feature'] for r in bank])
    winner=np.argmax(F[:,0,:-1]+d*F[:,1,:-1]-k*F[:,2,:-1],axis=0)
    policies=np.stack([r['policy'] for r in bank])
    return np.take_along_axis(policies,winner[None,:,:],axis=0)[0]

def adaptive_bank(economy,epsilon=1e-3,max_anchors=80):
    bank=[economy.optimal(0.),economy.optimal(1.)]; history=[]
    while True:
        bank.sort(key=lambda x:x['d'])
        cert=[interval_certificate(bank,i,i+1) for i in range(len(bank)-1)]
        worst=max(cert,key=lambda x:x['upper_loss'])
        history.append(dict(anchors=len(bank),gap=worst['upper_loss'],query=worst['worst_d']))
        print('BANK',history[-1],flush=True)
        if worst['upper_loss']<=epsilon:break
        if len(bank)>=max_anchors:raise RuntimeError('certificate tolerance not reached')
        if min(abs(r['d']-worst['worst_d']) for r in bank)<1e-10:raise ArithmeticError('refinement stagnated')
        bank.append(economy.optimal(worst['worst_d']))
    return bank,cert,history

def contract_run(out,epsilon=1e-3):
    e=Economy(); center=int(np.argmin(np.linalg.norm(e.states-[2,1.25],axis=1)))
    population=((e.states[:,0]>=1.6)&(e.states[:,0]<=2.4)&(e.states[:,1]>=.8)&(e.states[:,1]<=1.6)).astype(float)
    population/=population.sum(); initial=np.zeros(e.ns);initial[center]=1
    start_bank=time.perf_counter()
    bank,cert,history=adaptive_bank(e,epsilon)
    bank_seconds=time.perf_counter()-start_bank
    base=bank[0];diagnostics=[]
    for i,seed in enumerate((101,202,303)):
        policy=np.full((e.steps,e.ns),len(e.menu)+i,dtype=np.int32)
        f=e.evaluate(policy);v=f[0]-2*f[2];gain=e.one_step_gain(v)
        stored=np.load(ROOT/f'replication/r4/output/safe_policy_{seed}.npz')['values'].reshape(e.steps+1,e.ns)
        assert np.max(abs(v-stored))<2e-11
        loc=np.unravel_index(np.argmax(gain),gain.shape)
        occ,stop=e.occupation(policy,population);focal,_=e.occupation(policy,initial)
        err=base['value']-v
        diagnostics.append(dict(seed=seed,feasible_gain_max=float(gain.max()),
            gain_location=dict(date=int(loc[0]),state=e.states[loc[1]].tolist()),
            loss_focal=float(err[0,center]),loss_population=float(population@err[0]),loss_all_dates_states=float(err.max()),
            occupied_gain_sum_population=float(np.sum(occ*gain*np.exp(-e.model.rho*np.arange(e.steps)[:,None]/e.steps))),
            occupied_gain_sum_focal=float(np.sum(focal*gain*np.exp(-e.model.rho*np.arange(e.steps)[:,None]/e.steps))),
            focal_mass_at_gain_location=float(focal[loc]),population_mass_at_gain_location=float(occ[loc]),**stop))
    repaired_gain=e.one_step_gain(base['feature'][0]-2*base['feature'][2])
    tested=[]; start=time.perf_counter()
    for d in np.linspace(0,1,101):
        pol=switching(bank,d,2.); f=e.evaluate(pol); v=f[0]+d*f[1]-2*f[2]
        j=max(0,min(len(bank)-2,np.searchsorted([r['d'] for r in bank],d,side='right')-1))
        lam=(d-bank[j]['d'])/(bank[j+1]['d']-bank[j]['d'])
        upper=(1-lam)*bank[j]['value']+lam*bank[j+1]['value']
        err=upper-v
        assert err.min()>-2e-10 and err.max()<=epsilon+2e-10
        tested.append(dict(d=float(d),value=float(v[0,center]),duration=float(f[1,0,center]),effort=float(f[2,0,center]),
                           initial_controls=e.controls(pol)[0,center].tolist(),upper_loss_all_nodes=float(err.max())))
    reuse_seconds=time.perf_counter()-start
    rng=np.random.default_rng(905);invariance=[]
    for _ in range(25):
        d=float(rng.uniform(0,1));ell=float(rng.uniform(-3,3));m=d+e.model.rho*ell
        pol=switching(bank,d,2.);f=e.evaluate(pol);z=e.endpoint_discount(pol)
        assert abs(e.model.rho*f[1]+z-1).max()<2e-12
        original=f[0]+m*f[1]-2*f[2]+ell*z
        reduced=ell+f[0]+d*f[1]-2*f[2]
        invariance.append(float(abs(original-reduced).max()))
    roots=[]
    for d in (0.,.25,.5,.75,1.):
        r=e.optimal(d)
        q=e.common.base+d*e.common.duration-2*e.common.effort+e.common.continuation(r['value'][1])
        extra=e.extra[0];qe=extra.base+d*extra.duration-2*extra.effort+extra.continuation(r['value'][1])
        q=np.r_[q[center],qe[center]];acts=np.vstack([e.menu,extra.actions[center]])
        positive=q[acts[:,2]>=0].max();negative=q[acts[:,2]<=0].max()
        roots.append(dict(d=d,value=float(r['value'][0,center]),duration=float(r['feature'][1,0,center]),
                          controls=e.controls(r['policy'])[0,center].tolist(),positive_minus_nonpositive=float(positive-negative),
                          seconds=r['seconds']))
    np.savez_compressed(out/'contract_bank.npz',d=np.array([r['d'] for r in bank]),
        features=np.array([r['feature'] for r in bank]),policies=np.array([r['policy'] for r in bank]),
        values=np.array([r['value'] for r in bank]),states=e.states,menu=e.menu)
    result=dict(target='33x49 interpolation-defined killed chain; eight dates; union of 9x9x13 reference and 7x7x11 diagnostic meshes plus three frozen R4 proposals per node',
        common_action_count=len(e.menu),total_action_count=len(e.menu)+3,
        parameters=dict(k=2.,d_interval=[0.,1.],rho=.04),epsilon=epsilon,anchors=[r['d'] for r in bank],
        uniform_certificate=max(r['upper_loss'] for r in cert),
        intervals=[{k:v for k,v in r.items() if k!='nodewise_gap'} for r in cert],history=history,
        baseline=diagnostics,repaired_max_gain=float(repaired_gain.max()),
        initial_population='uniform over grid nodes in [1.6,2.4] x [0.8,1.6]',roots=roots,query_results=tested,
        normalization_max_error=max(invariance),
        timing=dict(kernel_build_seconds=e.build_seconds,anchor_solve_seconds=sum(r['seconds'] for r in bank),
                    bank_seconds_including_certification=bank_seconds,preparation_seconds=e.build_seconds+bank_seconds,
                    queries=101,reuse_with_full_policy_evaluation_seconds=reuse_seconds,
                    mean_direct_solve_seconds=float(np.mean([r['seconds'] for r in roots]))),
        certificate_scope='All dates and grid states, all d in [0,1], fixed finite action menu; double precision, not interval arithmetic or a diffusion bound.',
        source_sha256=digest(__file__))
    (out/'contracts.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default=str(ROOT/'replication/r5/output'));a=ap.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True);r=contract_run(out)
    print(json.dumps({k:v for k,v in r.items() if k not in ('query_results','intervals')},indent=2))
if __name__=='__main__':main()
