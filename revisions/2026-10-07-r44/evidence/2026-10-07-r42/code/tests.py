"""Exact-rational fixtures for new analytic moments, duals, and coverage gates."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,hashlib,math,inspect
import numpy as np
R=Path(__file__).resolve().parents[1]
import coupled_training as c

def positive(x):return max(F(0),x)
def exact_moment(p,u,v):
    if u==0 and v==0:return positive(p)**2,2*positive(p)
    if u==0 or v==0:
        r=max(u,v);a,b=positive(p+r),positive(p-r)
        return (a**3-b**3)/(6*r),(a**2-b**2)/(2*r)
    z=[positive(p+u+v),positive(p+u-v),positive(p-u+v),positive(p-u-v)]
    return (z[0]**4-z[1]**4-z[2]**4+z[3]**4)/(48*u*v),(z[0]**3-z[1]**3-z[2]**3+z[3]**3)/(12*u*v)
def contains(interval,value):
    assert F(float(interval.lo))<=value<=F(float(interval.hi)),(interval,value)
def main():
    coefficients=np.array([1e-10,1e-6,.01,1.,20.,700.,1000.,1e6])
    raw=c.inverse_softplus(coefficients)
    assert np.isfinite(raw).all()
    assert np.allclose(np.logaddexp(0,raw),coefficients,rtol=2e-14,atol=1e-14)
    for bad in (0.,-1.,float('inf'),float('nan')):
        try:c.inverse_softplus(np.array([bad]));raise AssertionError('Invalid coefficient accepted')
        except ValueError:pass
    moment_checks=0
    for uu,vv in [(0,0),(1,0),(0,2),(1,1),(1,3),(3,2),(1/16,2)]:
      u,v=F(uu)/16,F(vv)/16
      for i in range(-40,41):
        p=F(i)/64;m,g=c.imoment(c.I.point(float(p)),float(u),float(v));ex,eg=exact_moment(p,u,v)
        contains(m,ex);contains(g,eg);moment_checks+=2
    rng=np.random.default_rng(421007);N=17
    pp=rng.normal(size=(N,9));uu=rng.uniform(.005,.05,9);vv=rng.uniform(.005,.05,9)
    fm,fg=c.moment(pp,uu,vv)
    # Float proposals are not certificates: this check is diagnostic only.
    for j in range(9):
        im,ig=c.imoment(c.I.point(pp[:,j]),uu[j],vv[j]);assert np.max(abs(fm[:,j]-im.midpoint()))<1e-9;assert np.max(abs(fg[:,j]-ig.midpoint()))<1e-8
    # Exact continuous simplex dual, arbitrary nonnegative multipliers.
    dual_checks=0
    for n in range(100):
        mu=F(rng.integers(1,20),4);q=F(rng.integers(-20,20),8)
        a=[F(rng.integers(0,9),128),F(rng.integers(0,9),128)];g=[F(rng.integers(-20,20),8) for _ in range(2)];nu=F(rng.integers(0,20),8)
        L=q-sum(g[j]*a[j] for j in range(2))+mu*sum(z*z for z in a)/2-nu*F(1,8)-sum(min(g[j]-mu*a[j]+nu,0)**2 for j in range(2))/(2*mu)
        for i in range(9):
          for j in range(9-i):
            b=[F(i,64),F(j,64)]
            lower_model=q+sum(g[k]*(b[k]-a[k]) for k in range(2))+mu*sum((b[k]-a[k])**2 for k in range(2))/2
            assert L<=lower_model;dual_checks+=1
    # Actual compiled oracle against high-precision exact formulas at dyadic data.
    net=dict(w=[[1.,0.],[0.,1.],[-1.,-1.],[1.,-1.]],b=[0.,0.,.5,-.25],c=[.5,.25,2.,.125],linear=[-.75,-.25],intercept=.5)
    xx=c.grid(8);aa=c.project(rng.normal(size=xx.shape));aa=np.floor(aa*2**24)/2**24
    assert np.all(aa>=0) and np.all(aa.sum(1)<=c.CAP)
    interval_q,interval_g=c.iq(net,[c.I.point(xx[:,j]) for j in range(2)],[c.I.point(aa[:,j]) for j in range(2)],1)
    oracle_checks=0
    for idx in range(len(xx)):
        x=[F(z) for z in xx[idx]];a=[F(z) for z in aa[idx]]
        base=[F(1,8)+x[j]/2+x[1-j]/8+x[j]*(1-x[1-j])/16+a[j] for j in range(2)]
        val=F(net['intercept'])+sum(F(net['linear'][j])*base[j] for j in range(2));grad=[F(z) for z in net['linear']]
        for w,b,co in zip(net['w'],net['b'],net['c']):
            p=F(b)+sum(F(w[j])*base[j] for j in range(2));m,g=exact_moment(p,F(abs(w[0]))/32,F(abs(w[1]))/32)
            val+=F(co)*m
            for j in range(2):grad[j]+=F(co)*F(w[j])*g
        cost=sum((z-F(11,16))**2 for z in x)+2*positive(F(1,2)-sum(x))**2+(x[0]-x[1])**4/4+sum(z*z for z in a)+a[0]*a[1]/2+4*sum(z**4 for z in a)
        contains(c.I(interval_q.lo[idx],interval_q.hi[idx]),cost+F(15,16)*val)
        for j in range(2):contains(c.I(interval_g[j].lo[idx],interval_g[j].hi[idx]),2*a[j]+a[1-j]/2+16*a[j]**3+F(15,16)*grad[j])
        oracle_checks+=3
    C=c.constants(net,1)
    for x in rng.random((128,2)):
        w=np.asarray(net['w']);b=np.asarray(net['b']);co=np.asarray(net['c']);H=2*(w.T*(co*(w@x+b>0)))@w
        assert np.linalg.eigvalsh(H).min()>-1e-12 and np.linalg.eigvalsh(H).max()<=C['M']
    # Neural training does not call conventional value construction or spline labels.
    import scalar_training as st
    old_construct,old_spline=st.nl.construct,st.nl.spline
    def forbidden(*args,**kw):raise AssertionError('Conventional teacher/evaluator was called')
    st.nl.construct=forbidden;st.nl.spline=forbidden
    try:
        nets,logs,_=st.train(1,0,104729)
        result=st.nc.certify_chain(nets,1,0,32,16)
        assert math.isfinite(result['policy_gap_upper']) and all(n['hidden_weight_change']>0 for n in nets)
    finally:st.nl.construct=old_construct;st.nl.spline=old_spline
    bad=dict(net,c=[-1.,.25,2.,.125])
    try:c.constants(bad,1)
    except ValueError:pass
    else:raise AssertionError('Negative convex coefficient admitted')
    report=dict(exact_positive_part_moment_and_derivative_checks=moment_checks,exact_simplex_dual_checks=dual_checks,exact_continuous_oracle_checks=oracle_checks,hessian_envelope_checks=128,scalar_fresh_training_and_certification_with_spline_disabled=True,invalid_convexity_rejected=True,interpretation='Exact-rational fixtures and dependency guards; not a proof of optimizer convergence or a substitute for the analytic theorems',sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'code').glob('*.py')})
    (R/'audit').mkdir(exist_ok=True);(R/'audit/TESTS.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
