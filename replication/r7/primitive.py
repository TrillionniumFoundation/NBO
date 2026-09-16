#!/usr/bin/env python3
"""Primitive CRRA adjustment mechanism; analytically bounded option premium."""
from core import *
from scipy.optimize import brentq

def run():
    u0=2.;cap=.2;safe=.5;low=.05;high=.8;da=.5;rows=[]
    def f(c,u):return c**(1-u)/(1-u)
    def g(c,u):return c**(1-u)*(1+(u-1)*np.log(c))/(u-1)**2
    def H(c,u):return c**(1-u)*((1+(u-1)*np.log(c))**2+1)/(u-1)**3
    for p in (.06,.08,.10):
        cs=np.array([low,high]);pr=np.array([p,1-p]);gs=float(pr@g(cs,u0));gm=float(g(safe,u0))
        Ms=max(float(pr@H(cs,u0-cap)),float(pr@H(cs,u0+cap)))
        Mm=max(float(H(safe,u0-cap)),float(H(safe,u0+cap)))
        Bp=float(pr@f(cs,u0));Bm=float(f(safe,u0))
        for k in (20.,40.,80.):
            assert abs(gs)/(k+Ms)<=cap and abs(gm)/(k+Mm)<=cap
            LB=gs**2/(2*(k+Ms))-gm**2/(2*k)
            def optimize(cons,prob):
                derivative=lambda th:float(prob@g(cons,u0+th)-k*th)
                th=-cap if derivative(-cap)<=0 else cap if derivative(cap)>=0 else brentq(derivative,-cap,cap,xtol=1e-14)
                option=float(prob@(f(cons,u0+th)-f(cons,u0))-.5*k*th*th)
                return th,option
            tp,op=optimize(cs,pr);tm,om=optimize(np.array([safe]),np.array([1.]))
            assert op-om>=LB-1e-12 and LB>0
            d0=(Bm-Bp)/da;dadj=(Bm-Bp-op+om)/da
            # A contract chosen by the bound, not by the optimized moments.
            test=d0-LB/(2*da);base_delta=Bp-Bm+test*da;adj_delta=base_delta+op-om
            assert base_delta<0<adj_delta
            rows.append(dict(downside_probability=p,cost=k,positive_shadow=gs,nonpositive_shadow=gm,positive_curvature_bound=Ms,
                relative_option_lower=LB,relative_option_exact=op-om,positive_adjustment=tp,nonpositive_adjustment=tm,
                baseline_threshold=d0,adjusted_threshold=dadj,guaranteed_threshold_shift=LB/da,
                declared_contract=test,fixed_delta=base_delta,adjusted_delta=adj_delta))
    result=dict(primitives=dict(u0=u0,adjustment_bound=cap,safe_consumption=safe,risky_consumption=[low,high],duration_difference=da),
        scope='two-stage analytical subeconomy; not a calibration or approximation claim for the eight-date portfolio chain',rows=rows)
    # A bound on the CONTINUUM of probabilities and costs, not interpolation of rows.
    shadows=[float(np.array([p,1-p])@g(np.array([low,high]),u0)) for p in (.06,.10)]
    curvature=max(float(np.array([p,1-p])@H(np.array([low,high]),u)) for p in (.06,.10) for u in (u0-cap,u0+cap))
    gmin=min(abs(x) for x in shadows);gmax=max(abs(x) for x in shadows)
    uniform=gmin*gmin/(2*(80+curvature))-gm*gm/(2*20)
    assert max(shadows)<0 and gmax/20<cap and uniform>0
    result['continuous_family']=dict(probability_interval=[.06,.10],cost_interval=[20.,80.],
        minimum_absolute_risky_shadow=gmin,maximum_absolute_risky_shadow=gmax,
        maximum_risky_curvature=curvature,relative_option_lower=uniform,
        guaranteed_threshold_shift=uniform/da,
        proof='risky shadow affine and negative in p; curvature convex in preference index and affine in p; endpoint extrema bound the entire rectangle')
    save('primitive.json',result);return result
if __name__=='__main__':run()
