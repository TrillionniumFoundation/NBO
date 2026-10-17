"""Common-information acquisition and strong conventional controls.

All candidates are proposals. None of their optimizer statuses or training
losses substitutes for an original-law action certificate.
"""
from __future__ import annotations
from pathlib import Path
import sys,json,time,itertools
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.linalg import lstsq as scipy_lstsq
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'));sys.path.insert(0,str(ROOT/'new'))
import study97
from matched96 import MatchedFit
import continuum94 as cont
import investment94 as econ

ARMS=('online','quadratic','relu','hinge','spline','poly2','poly3','grid')


def grid(n):
    v=(np.arange(n)+.5)/n
    return np.stack(np.meshgrid(v,v,indexing='ij'),axis=-1).reshape(-1,2)


def powers(degree):
    return [(j,k-j) for k in range(degree+1) for j in range(k+1)]


class Conventional:
    def __init__(self,kind,data):
        self.kind=kind;self.data=data
    def float_eval(self,x,gradient=False):
        x=np.asarray(x);kind=self.kind
        if kind=='hinge':
            W=np.array(self.data['directions']);b=np.array(self.data['offsets']);c=np.array(self.data['coefficients'])
            v=np.full(x.shape[:-1],c[0]);g=np.broadcast_to(c[1:3],x.shape).copy()
            v+=c[1]*x[...,0]+c[2]*x[...,1]
            for j in range(len(b)):
                z=x[...,0]*W[j,0]+x[...,1]*W[j,1]+b[j]
                v+=c[j+3]*np.maximum(z,0)
                g+=c[j+3]*(z>0)[...,None]*W[j]
            econ.count('conventional_hinge_feature_values',v.size*len(b))
        elif kind in ('poly2','poly3'):
            pp=powers(int(kind[-1]));c=np.array(self.data['coefficients'])
            v=np.zeros(x.shape[:-1]);g=np.zeros_like(x)
            for w,(p,q) in zip(c,pp):
                v+=w*x[...,0]**p*x[...,1]**q
                if p:g[...,0]+=w*p*x[...,0]**(p-1)*x[...,1]**q
                if q:g[...,1]+=w*q*x[...,0]**p*x[...,1]**(q-1)
            econ.count('polynomial_monomial_values',v.size*len(pp))
        elif kind=='grid':
            z=np.array(self.data['values']);n=z.shape[0]
            pos=x*n-.5;i=np.clip(np.floor(pos).astype(int),0,n-2);w=pos-i
            i0,i1=i[...,0],i[...,1];a,b=w[...,0],w[...,1]
            v00=z[i0,i1];v10=z[i0+1,i1];v01=z[i0,i1+1];v11=z[i0+1,i1+1]
            v=(1-a)*(1-b)*v00+a*(1-b)*v10+(1-a)*b*v01+a*b*v11
            g=np.stack((n*((1-b)*(v10-v00)+b*(v11-v01)),n*((1-a)*(v01-v00)+a*(v11-v10))),axis=-1)
            econ.count('grid_corner_lookups',4*v.size)
        else:raise ValueError(kind)
        if not np.all(np.isfinite(v)) or not np.all(np.isfinite(g)):raise ArithmeticError('Nonfinite conventional proposal')
        return (v,g) if gradient else v


def payload(model):
    if model is None:return {'kind':'online','parameters':{}}
    if isinstance(model,Conventional):return {'kind':model.kind,'parameters':model.data}
    return {'kind':model.kind,'parameters':{'directions':model.directions.tolist(),
           'offsets':model.offsets.tolist(),'coefficients':model.coefficients.tolist()}}


def restore(raw):
    kind=raw['kind'];d=raw['parameters']
    if kind=='online':return None
    if kind in ('quadratic','relu','spline'):
        return MatchedFit(kind,np.array(d['directions']),np.array(d['offsets']),np.array(d['coefficients']),{})
    return Conventional(kind,d)


def encoded(model):
    return (json.dumps(payload(model),sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def independent_matrix(kind,x,W,b):
    """Separate coordinate arithmetic, not the production design/evaluation."""
    rows=[]
    for row in x:
        values=[1.,float(row[0]),float(row[1])]
        for w,offset in zip(W,b):
            z=float(offset)+sum(float(u)*float(v) for u,v in zip(w,row))
            values.append(z*z if kind=='quadratic' else max(0.,z))
        rows.append(values)
    return np.array(rows)


def active_set_fit(A,y,nonnegative):
    """Enumerate faces, solve free coordinates by pivoted QR (gelsy).

This is algorithmically separate from scipy.optimize.lsq_linear's trust-region
production routine. Both use floating BLAS/LAPACK: no exact optimality claim.
"""
    best=None;k=A.shape[1];free_base=k-nonnegative;solves=0
    for bits in itertools.product((0,1),repeat=nonnegative):
        ids=list(range(free_base))+[free_base+j for j,v in enumerate(bits) if v]
        theta=np.zeros(k)
        v,_,rank,_=scipy_lstsq(A[:,ids],y,lapack_driver='gelsy');solves+=1
        if rank!=len(ids) or np.any(v[free_base:] < -1e-10):continue
        theta[ids]=v;theta[free_base:]=np.maximum(theta[free_base:],0)
        loss=float(np.sum((A@theta-y)**2))
        if best is None or loss<best[0]:best=(loss,theta)
    if best is None:raise ArithmeticError('Independent active-set enumeration found no feasible face')
    return best[0],best[1],solves


def audit_greedy(kind,x,lab,model):
    W,b=study97.features(kind,2)
    if kind=='spline':
        for j in range(len(b)):
            coord=int(np.argmax(W[j]));b[j]=-np.rint(np.quantile(x[:,coord],(j//2+1)/17)*2**16)/2**16
    full=independent_matrix(kind,x,W,b);y=lab['lower']+(lab['upper']-lab['lower'])/2
    chosen=model.record['selected'];records=[];solves=0
    for row in model.record['trials']:
        step,j=row['step'],row['candidate'];ids=[0,1,2]+[3+k for k in chosen[:step]]+[3+j]
        A=full[:,ids]
        if row.get('rank_rejected'):
            records.append(dict(row,independent_rank=int(np.linalg.matrix_rank(A))));continue
        loss,theta,n=active_set_fit(A,y,len(ids)-3);solves+=n
        diff=abs(loss-row['loss']);tol=1e-8*max(1.,abs(loss),abs(row['loss']))
        records.append(dict(row,independent_loss=loss,absolute_difference=diff,tolerance=tol,objective_agreement=diff<=tol))
        if diff>tol:raise ArithmeticError('Independent candidate objective mismatch')
    A=independent_matrix(kind,x,model.directions,model.offsets)
    loss,theta,n=active_set_fit(A,y,len(model.offsets));solves+=n
    rounded=np.rint(theta*2**30)/2**30;rounded[3:]=np.maximum(rounded[3:],0)
    independent_choices=[]
    for step in range(len(chosen)):
        pool=[r for r in records if r['step']==step and 'independent_loss' in r]
        low=min(r['independent_loss'] for r in pool)
        independent_choices.append(min(r['candidate'] for r in pool if r['independent_loss']<=low+1e-12*max(1.,abs(low))))
    return {'independent_step_choices':independent_choices,'step_choices_exactly_equal':independent_choices==chosen,
            'algorithm':'independent matrix assembly and complete nonlinear active-set enumeration; pivoted QR',
            'shared_numerical_libraries':True,'face_solves':solves,'trials':records,
            'rounded_coefficients_exactly_equal':bool(np.array_equal(rounded,model.coefficients)),
            'maximum_rounded_coefficient_difference':float(np.max(np.abs(rounded-model.coefficients))),
            'production_selected':chosen,'independent_final_loss':loss,
            'claim':'Numerical objective replication, not exact optimization or independent authorship.'}


def fit_all(x,lab):
    y=lab['lower']+(lab['upper']-lab['lower'])/2;models={'online':None};receipts={}
    for kind in ('quadratic','relu','spline'):
        t=time.perf_counter();m=study97.build(kind,x,lab,6);seconds=time.perf_counter()-t
        t=time.perf_counter();audit=audit_greedy(kind,x,lab,m);audit_seconds=time.perf_counter()-t
        models[kind]=m;receipts[kind]={'fit_seconds':seconds,'audit_seconds':audit_seconds,
                                     'fit':m.record,'audit':audit,'coefficients':len(m.coefficients),'features':len(m.offsets)}
    models['hinge']=Conventional('hinge',payload(models['relu'])['parameters'])
    receipts['hinge']={'shared_acquisition':'relu','standalone_full_acquisition_charge':True,
                       'not_an_independent_fit':True,'encoding':'coordinate-loop conventional hinges'}
    for kind in ('poly2','poly3'):
        degree=int(kind[-1]);t=time.perf_counter()
        A=np.column_stack([x[:,0]**p*x[:,1]**q for p,q in powers(degree)])
        c,_,rank,_=np.linalg.lstsq(A,y,rcond=None)
        if rank!=len(c):raise ArithmeticError('Rank deficient polynomial')
        c=np.rint(c*2**30)/2**30;seconds=time.perf_counter()-t
        t=time.perf_counter()
        Ai=np.array([[float(u)**p*float(v)**q for p,q in powers(degree)] for u,v in x])
        ca,_,ranki,_=scipy_lstsq(Ai,y,lapack_driver='gelsy');ca=np.rint(ca*2**30)/2**30
        l=float(np.sum((A@c-y)**2));li=float(np.sum((Ai@ca-y)**2))
        if abs(l-li)>1e-8*max(1.,abs(l),abs(li)):raise ArithmeticError('Polynomial independent audit failed')
        models[kind]=Conventional(kind,{'coefficients':c.tolist()})
        receipts[kind]={'fit_seconds':seconds,'audit_seconds':time.perf_counter()-t,'coefficients':len(c),
                         'fit_loss':l,'independent_loss':li,'independent_rank':int(ranki),
                         'rounding_exactly_equal':bool(np.array_equal(c,ca)),'two_factorizations':'SVD versus pivoted QR',
                         'equal_rank_claim':False}
    t=time.perf_counter();n=int(np.sqrt(len(x)))
    if n*n!=len(x) or not np.array_equal(x,grid(n)):raise ValueError('Complete ordered tensor midpoint design required')
    models['grid']=Conventional('grid',{'values':y.reshape(n,n).tolist()})
    receipts['grid']={'fit_seconds':time.perf_counter()-t,'coefficients':len(y),'equal_memory_claim':False,
                       'extrapolation':'linear in each boundary coordinate; proposal only'}
    for kind,m in models.items():
        t=time.perf_counter();raw=encoded(m);restored=restore(json.loads(raw))
        if encoded(restored)!=raw:raise ArithmeticError('Serialization mismatch')
        if m is not None and not np.array_equal(m.float_eval(x),restored.float_eval(x)):raise ArithmeticError('Prediction changed on reload')
        receipts.setdefault(kind,{})['serialization_seconds']=time.perf_counter()-t
        receipts[kind]['payload_bytes']=len(raw)
    return models,receipts


def proposal(x,alpha,model):
    if model is None or not isinstance(model,Conventional) or model.kind=='hinge':
        return cont.actor(x,alpha,model)
    cap=econ.capacity(study97.I(x)).lo;out=[]
    # Strong conventional controls are not constrained to convex rank-six heads.
    for j,row in enumerate(x):
        z=np.repeat(row[None,:],33,axis=0);aa=np.linspace(0,cap[j],33)
        values=cont.float_query(z,aa,alpha,model)[0]
        ix=int(np.argmin(values));low=aa[max(0,ix-1)];high=aa[min(32,ix+1)]
        if high==low:a=low
        else:
            def value(a):return float(cont.float_query(row[None,:],np.array([a]),alpha,model)[0][0])
            fit=minimize_scalar(value,bounds=(low,high),method='bounded',options={'xatol':2**-32,'maxiter':128})
            if not fit.success or not np.isfinite(fit.fun):raise ArithmeticError('Conventional proposal solve failed')
            candidates=[(float(values[ix]),float(aa[ix])),(float(fit.fun),float(fit.x))]
            a=min(candidates,key=lambda v:(v[0],v[1]))[1]
            econ.count('conventional_scalar_optimizer_evaluations',int(fit.nfev))
        out.append(min(np.floor(a*2**30)/2**30,np.floor(cap[j]*2**30)/2**30))
    return np.array(out)
