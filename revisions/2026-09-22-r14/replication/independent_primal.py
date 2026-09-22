"""Second rigorous evaluator of the original stopped time-control policy.

A tensor Gauss rule evaluates the original CRRA expression on |Z|<=8. Exact
rational root isolation, positive weights, Cauchy analyticity bounds, Gaussian
tails, and a stopped-event correction make the enclosure. No production
polynomial utility approximation or production certifier is imported.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
import argparse,json,time,hashlib
import numpy as np
from interval64 import I,exp,log,add_reduce,stack
from validated_gauss import Q,sqrt,pi,mapped_rule,cauchy_remainder
ROOT=Path(__file__).resolve().parents[3]

def policy_inputs(actor,u0='2',x0='1.25'):
    d=json.loads(Path(actor).read_text());c=I(np.array(d['c'],float));th=I(np.array(d['theta'],float))
    pp=np.array(d.get('p',[0]*len(c.lo)),float)
    if np.any(pp!=0):raise ValueError('This exact policy evaluator requires p=0')
    n=len(c.lo);discount=[]
    for j in range(n):discount.append((exp(-Q('.02')*Q(F(j,n)))-exp(-Q('.02')*Q(F(j+1,n))))/Q('.02'))
    weights=stack(discount);qsum=(1-exp(-Q('.02')))/Q('.02')
    shift=(Q(x0)-Q('1.25'))/qsum
    c=c+shift # budget-preserving initial-wealth transfer, exact mathematical controls
    if np.any(c.lo<Q('.7').hi) or np.any(c.hi>Q('.8').lo):raise ValueError('Outside proved consumption range')
    if np.any(th.lo<0) or np.any(th.hi>Q('.2').lo):raise ValueError('Outside proved drift range')
    if not F('1.98')<=F(u0)<=F('2.02') or not F('1.24')<=F(x0)<=F('1.26'):raise ValueError('Outside proved state rectangle')
    terminal=exp(Q('.02'))*(Q(x0)-add_reduce(c*weights))
    if not terminal.lo>Q('.5').hi:raise ArithmeticError('Terminal wealth feasibility not certified')
    return d,c,th,terminal

def evaluate(actor,k,ns=8,nz=32,u0='2',x0='1.25'):
    clock=time.perf_counter();d,c,th,xT=policy_inputs(actor,u0,x0);n=len(c.lo)
    total=I(0);quadrature_error=I(0);cost=I(0);mu=I(0);M_v=F(5);M_z=F(32)
    zleft=stack([Q(-8+F(16*j,nz)) for j in range(nz)]);zright=stack([Q(-8+F(16*(j+1),nz)) for j in range(nz)])
    zn,zw=mapped_rule(zleft,zright);z=zn.reshape(-1);wz=zw.reshape(-1);phi=exp(-z.square()/2)/sqrt(2*pi())
    for j in range(n):
        va,vb=sqrt(Q(F(j,n))),sqrt(Q(F(j+1,n)))
        left=stack([va+(vb-va)*Q(F(h,ns)) for h in range(ns)])
        right=stack([va+(vb-va)*Q(F(h+1,ns)) for h in range(ns)])
        vn,vw=mapped_rule(left,right);v=vn.reshape(-1,1);wv=vw.reshape(-1,1);t=v.square()
        r=Q(u0)-1+mu+th[j]*(t-Q(F(j,n)))+Q('.05')*v*z.reshape(1,-1)
        if np.any(r.lo<=0):raise ArithmeticError('CRRA pole entered integration rectangle')
        f=-exp(-r*log(c[j]))/r
        vals=wv*wz.reshape(1,-1)*(2*v)*exp(-Q('.04')*t)*f*phi.reshape(1,-1)
        total=total+add_reduce(vals.reshape(-1))
        # Tensor-product error: integration and the positive rule each have
        # their true interval length as norm. Bounds 5 and 32 include 2v and phi.
        ev=add_reduce(cauchy_remainder(right-left,(right-left)/2,F(1,8),M_v))*16
        ez=add_reduce(cauchy_remainder(zright-zleft,(zright-zleft)/2,F(2),M_z))*(vb-va)
        quadrature_error=quadrature_error+ev+ez
        mass=(exp(-Q('.04')*Q(F(j,n)))-exp(-Q('.04')*Q(F(j+1,n))))/Q('.04')
        cost=cost+Q(k)*th[j].square()/2*mass;mu=mu+th[j]/n
    gaussian_tail=6*2*exp(-Q(32)) # clipped utility lies in [-6,0]; C_rho(1)<=1
    initial_offset=Q(u0)-2+mu
    Gmean=-Q('.02')*(initial_offset.square()+Q('.0025'))+Q('.1')*log(xT)
    full=total-cost+exp(-Q('.04'))*Gmean
    pexit=2*exp(-Q('.58').square()/(2*Q('.05').square()))
    fourth=Q('.22')**4+6*Q('.22').square()*Q('.0025')+3*Q('.0025').square()
    exiterr=15*pexit+Q('.02')*sqrt(fourth*pexit)
    # One-sided normal truncation, symmetric quadrature/stopping allowances.
    value=full+I(-float((quadrature_error+gaussian_tail+exiterr).hi),float((quadrature_error+exiterr).hi))
    return {'status':'VALID_ENCLOSURE','method':'independent rational-root Gauss / analytic Cauchy / Gaussian tail / stopping correction',
      'actor_path':str(Path(actor).resolve().relative_to(ROOT)),'actor_sha256':hashlib.sha256(Path(actor).read_bytes()).hexdigest(),
      'k':float(F(k)),'u0':str(u0),'x0':str(x0),'time_subcells_per_slab':ns,'normal_cells':nz,'gauss_order':8,
      'function_evaluations':n*ns*nz*64,'value_interval':value.pair(),'width':float((I(value.hi)-I(value.lo)).hi),
      'quadrature_remainder_upper':float(quadrature_error.hi),'normal_truncation_upper':float(gaussian_tail.hi),
      'stopping_correction_upper':float(exiterr.hi),'terminal_wealth':xT.pair(),'full_quadrature_interval':full.pair(),
      'consumption_range':[float(c.lo.min()),float(c.hi.max())],'theta_range':[float(th.lo.min()),float(th.hi.max())],
      'seconds':time.perf_counter()-clock,'production_certifier_imports':False,
      'scope':'Original continuous stopped payoff of a feasible time-control policy; not a neural-training or optimal-value certificate'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--actor',type=Path,required=True);ap.add_argument('--k',required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--ns',type=int,default=8);ap.add_argument('--nz',type=int,default=32);ap.add_argument('--u0',default='2');ap.add_argument('--x0',default='1.25');a=ap.parse_args()
    r=evaluate(a.actor,a.k,a.ns,a.nz,a.u0,a.x0);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
