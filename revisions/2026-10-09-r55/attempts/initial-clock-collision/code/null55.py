"""Sample-split learned null directions with uncertain action exposure.

The corrected gate sees training/validation data and the public B in [0,1]^d
prior, never the simulator's true B. True B is used only for data generation and
post-decision checks. Additive, action-invariant uniform noise is maintained.
"""
from __future__ import annotations
import hashlib,json,math,time
from fractions import Fraction as F
import numpy as np
import neural55 as n
import prospective55 as p
import directed53 as d53
R=p.R

def estimate(d,N,seed):
    rng=np.random.default_rng(seed);bins=rng.integers(0,2**40,size=(N,2),dtype=np.uint64)
    z=-1/32+(bins.astype(float)+.5)*2.**-44
    truth=np.where(np.arange(d)%2==0,.5,.25);sign=np.where(np.arange(d)%2==0,1.,-1.)
    observed=truth+(z[:,0]-z[:,1])[:,None]*sign/(1/4)
    return observed,bins

def direction(data):
    B=np.mean(data,axis=0);v=np.eye(1,len(B),0).ravel()-B[0]*B/(B@B)
    v=v/np.linalg.norm(v,ord=1)
    return np.round(v*2**24)/2**24

def confidence(data):
    N,d=data.shape;v=F(14,2*N);root=math.sqrt(float(v))
    while F(root)**2<v:root=math.nextafter(root,math.inf)
    rad=F(root)/2+F(1,2**40)
    low=[];high=[]
    for j in range(d):
        stat=p.old.inference.moments(data[:,j],-.25,1.25)
        low.append(n.s.c.enclosure(max(F(0),F(stat['mean_lo'])-rad))[0])
        high.append(n.s.c.enclosure(min(F(1),F(stat['mean_hi'])+rad))[1])
    return n.I(np.array(low),np.array(high)),str(rad)

def future(x,a,B):
    base=n.o.deterministic_next(x,n.I.point(np.zeros(len(a.lo))))
    return base+n.s.stack([a*n.I(B.lo[j],B.hi[j]) for j in range(x.lo.shape[-1])])

def terminal_difference(x,a,b,B):
    ya=future(x,a,B);yb=future(x,b,B);delta=n.s.stack([(a-b)*n.I(B.lo[j],B.hi[j]) for j in range(x.lo.shape[-1])]);dim=x.lo.shape[-1]
    target=n.s.isum(delta*(ya+yb-F(5,4)))*n.s.c.rat_i(F(4,dim))
    da=ya-n.I(np.roll(ya.lo,-1,axis=-1),np.roll(ya.hi,-1,axis=-1));db=yb-n.I(np.roll(yb.lo,-1,axis=-1),np.roll(yb.hi,-1,axis=-1))
    dd=delta-n.I(np.roll(delta.lo,-1,axis=-1),np.roll(delta.hi,-1,axis=-1))
    imbalance=n.s.isum(dd*(da+db))*n.s.c.rat_i(F(1,4*dim))
    sa=F(1,2)-n.s.isum(ya)*n.s.c.rat_i(F(2,dim));sb=F(1,2)-n.s.isum(yb)*n.s.c.rat_i(F(2,dim))
    ds=-n.s.isum(delta)*n.s.c.rat_i(F(2,dim))
    shortage=2*d53.positive_difference(sa,sb,ds)*(n.o.positive(sa)+n.o.positive(sb))
    return (a-b)*(a+b)*(1+4*(a.square()+b.square()))+float(n.BETA)*(target+imbalance+shortage)

def nuisance(x,a,b,B,v,M):
    radius=abs(sum((F(float(v[j]))*(1 if j%2==0 else -1) for j in range(len(v))),F(0)))/32
    va=n.dot(future(x,a,B),v)+F(1,8);vb=n.dot(future(x,b,B),v)+F(1,8)
    return M*(n.hinge_mean(va,radius)-n.hinge_mean(vb,radius))

def main():
    frozen=p.verify();start=time.perf_counter();folder=R/'results55/learned-null';folder.mkdir(parents=True,exist_ok=False);rows=[];fits=[]
    for dim in (2,4,8):
        part=n.Partition(dim,64);x=part.box;cap=part.capindex;b=n.I.point((cap*3//4)/4096);truth=n.I.point(np.where(np.arange(dim)%2==0,.5,.25))
        for seed in range(3):
            training,tbins=estimate(dim,256,57000+dim*100+seed);v=direction(training)
            for N in (512,4096,32768):
                validation,bins=estimate(dim,N,58000+dim*1000+N+seed);box,rad=confidence(validation)
                key=f'd{dim}-seed{seed}-N{N}';datahash=p.arrays(folder/(key+'-data.npz'),training_bins=tbins,validation_bins=bins,direction=v,validation_exposures=validation)
                fitted=n.I.point(np.mean(validation,axis=0));coefficient=n.dot(n.I(box.lo[None,:],box.hi[None,:]),v);sup=max(abs(coefficient.lo[0]),abs(coefficient.hi[0]))
                contains=bool(np.all(box.lo<=truth.lo)&np.all(truth.hi<=box.hi))
                fits.append(dict(key=key,dimension=dim,validation_rows=N,data_sha256=datahash,direction=v.tolist(),radius_exact=rad,box_lo=box.lo.tolist(),box_hi=box.hi.tolist(),true_exposure_contained=contains,estimated_direction_exposure=float(v@np.mean(validation,axis=0)),robust_direction_exposure_upper=float(sup)))
                for M in (1,16,4096):
                    selected=cap*3//4;bad=selected.copy();upper=np.zeros(len(cap));badupper=upper.copy();trueupper=upper.copy();badharm=upper.copy();raw={}
                    for j in range(9):
                        ai=cap*j//8;a=n.I.point(ai/4096);true=terminal_difference(x,a,b,truth)
                        crit=terminal_difference(x,a,b,box)+float(n.BETA)*nuisance(x,a,b,box,v,M)
                        allowance=n.s.abs_i(a-b)*float(sup)*M
                        corrected=crit+float(n.BETA)*allowance
                        naive=terminal_difference(x,a,b,fitted)+float(n.BETA)*nuisance(x,a,b,fitted,v,M)
                        take=corrected.hi<upper;wrong=naive.hi<badupper
                        upper[take]=corrected.hi[take];selected[take]=ai[take];trueupper[take]=true.hi[take]
                        badupper[wrong]=naive.hi[wrong];bad[wrong]=ai[wrong];badharm[wrong]=true.lo[wrong]
                        raw.update({f'j{j}_true_lo':true.lo,f'j{j}_true_hi':true.hi,f'j{j}_corrected_hi':corrected.hi,f'j{j}_naive_hi':naive.hi,f'j{j}_allowance_hi':allowance.hi})
                    if contains and np.any(trueupper>0):raise AssertionError('Corrected gate violated true model')
                    raw.update(selected=selected,false_null_selected=bad,selected_true_hi=trueupper,false_null_true_lo=badharm)
                    h=p.arrays(folder/(key+f'-M{M}.npz'),**raw)
                    rows.append(dict(key=key,amplitude=M,changed=int(np.count_nonzero(selected!=cap*3//4)),harmful_false_null=int(np.count_nonzero((bad!=cap*3//4)&(badharm>0))),max_allowance=max(float(raw[f'j{j}_allowance_hi'].max()) for j in range(9)),raw_sha256=h))
    p.save(folder/'summary.json',dict(status='passed',source_freeze_sha256=frozen,fits=fits,cases=rows,validation_boxes=len(fits),cell_cases=64*len(rows),alpha='1/200',hoeffding_log_upper=14,
        model='unknown deterministic action exposure B in [0,1]^d; known nonlinear drift and bounded action-invariant additive common noise; no arbitrary unknown-kernel claim',training_and_validation_disjoint=True,corrected_gate_has_true_parameter_access=False,seconds_before_record=time.perf_counter()-start))
    print(json.dumps(dict(fitted_boxes=len(fits),cases=len(rows),harmful_false_null=sum(x['harmful_false_null'] for x in rows),safe_changes=sum(x['changed'] for x in rows),seconds=time.perf_counter()-start)),flush=True)
if __name__=='__main__':main()
