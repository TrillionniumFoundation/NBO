"""Cardinal-primitive robustness, including the referee's contrary examples."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import brentq, minimize_scalar
from model import save

def U(c,u):return c**(1-u)/(1-u)
def Uu(c,u):
    y=1-u;l=np.log(c);return c**y*(1-y*l)/y**2

def option(p,k,a,positive):
    c=np.array([.05,.8]) if positive else np.array([.5]);w=np.array([p,1-p]) if positive else np.array([1.])
    base=float(w@U(c,2.))
    def value(x):return float(w@U(c,2+x))+a*x-.5*k*x*x-base
    def derivative(x):return float(w@Uu(c,2+x))+a-k*x
    lo,hi=-.2,.2
    x=lo if derivative(lo)<=0 else hi if derivative(hi)>=0 else brentq(derivative,lo,hi,xtol=1e-14)
    check=minimize_scalar(lambda x:-value(x),bounds=(lo,hi),method='bounded',options={'xatol':1e-14})
    error=abs(value(x)+check.fun);assert error<2e-11
    return dict(option=value(x),adjustment=x,optimization_check_error=error)

def run():
    # Conservative rounded constants from the inherited continuum-family proof.
    Gp,Gm,M=1.482,.6138,17.342;kmin,kmax=20.,80.
    A=.25
    numerator=(Gp-A)**2*kmin/(kmin+M)-(Gm+A)**2
    bound=numerator/(2*kmax)
    assert bound>0 and (3.118+A)/kmin<.2
    radius=brentq(lambda a:(Gp-a)**2*kmin/(kmin+M)-(Gm+a)**2,0.,Gp)
    rows=[]
    for p in (.06,.08,.10):
        for k in (20.,40.,80.):
            for a in (-.25,0.,.25,1.,2.):
                plus=option(p,k,a,True);minus=option(p,k,a,False)
                d0=(float(U(.5,2))-float(np.array([p,1-p])@U(np.array([.05,.8]),2)))/.5
                premium=plus['option']-minus['option']
                rows.append(dict(p=p,k=k,a=a,positive=plus,nonpositive=minus,relative_option=premium,d_unadjusted=d0,d_adjusted=d0-premium/.5))
    for row in rows:
        if abs(row['a'])<=A:assert row['relative_option']>=bound-1e-12
    out=dict(cardinal_tilt_radius=A,uniform_lower_bound=bound,sufficient_radius_supremum=radius,
             family=dict(p=[.06,.1],k=[20,80],c_positive=[.05,.8],c_nonpositive=.5,u0=2,adjustment_cap=.2),rows=rows,
             evidence='uniform result is analytic with conservative rounded bounds; the 45 rows are implementation checks, not its proof')
    save('primitive_robustness.json',out);print('uniform bound',bound,'sufficient radius',radius)
    for r in rows:
        if r['p']==.08 and r['k']==40:print(r)
    return out
if __name__=='__main__':run()
