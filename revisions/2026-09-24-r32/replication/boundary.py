"""Rational certificate for an interval-wide derivative, not a derivative grid.
The analytic reduction is proved in the R32 supplement. Only elementary
rational enclosures are used here; no floating tolerance is a proof premise.
"""
from fractions import Fraction as F
from pathlib import Path
import json, argparse, time


def exp_bounds(x:F,n=48):
    assert x>=0 and n+2>x
    term=F(1); total=term
    for k in range(1,n+1): term*=x/k; total+=term
    following=term*x/(n+1)
    return total,total+following/(1-x/(n+2))


def down(x:F,bits=64):
    return F((x.numerator*(1<<bits))//x.denominator,1<<bits)


def exp_minus_lower(x:F):
    return down(1/exp_bounds(x)[1])


def atan_bounds(x:F,n=18):
    terms=[(-1)**k*x**(2*k+1)/F(2*k+1) for k in range(n)]
    s=sum(terms,F(0)); other=s+(-1)**n*x**(2*n+1)/F(2*n+1)
    return min(s,other),max(s,other)


def gaussian_interval_lower(a:F,b:F,step=F(1,100)):
    """Right Riemann sum on positive half-line: phi is decreasing."""
    assert 0<=a<b and (b-a)/step==int((b-a)/step)
    # Machin's identity gives pi<22/7; hence sqrt(2*pi)<251/100.
    n=int((b-a)/step)
    return step*F(100,251)*sum((exp_minus_lower((a+i*step)**2/2) for i in range(1,n+1)),F(0))


def certify():
    tic=time.perf_counter(); a,b=atan_bounds(F(1,5)),atan_bounds(F(1,239))
    pi_lo=16*a[0]-4*b[1]; pi_hi=16*a[1]-4*b[0]
    assert F(25,8)<pi_lo<pi_hi<F(22,7)
    assert F(44,7)<F(251,100)**2
    ex=exp_bounds(F(16,5)); assert 24<ex[0]<ex[1]<25
    tails={'Phi_minus_2':gaussian_interval_lower(F(2),F(4)),
           'Phi_minus_14_5':gaussian_interval_lower(F(14,5),F(4)),
           'Phi_minus_4_5':gaussian_interval_lower(F(4,5),F(4)),
           'Phi_plus_6_5':F(1,2)+gaussian_interval_lower(F(0),F(6,5))}
    assert tails['Phi_minus_2']>F(1,50)
    assert tails['Phi_minus_14_5']>F(1,500)
    assert tails['Phi_minus_4_5']>F(1,5)
    assert tails['Phi_plus_6_5']>F(22,25)
    # Original deterministic wealth remains strictly inside its stopping bounds.
    wealth_lower=F(75,2)-F(145,4)*F(50,49); assert wealth_lower>F(1,2)
    h_lower=8-F(1,20000)-F(3,20)-F(1,1000)-F(4,625)-F(1,25)-F(75,14)
    h_y_lower=F(10,81)-F(4,3125)-F(1,125)
    assert h_lower>2 and h_y_lower>0
    negative_half=2*F(4,25)*F(24,25)*F(8,25)-F(4,125)
    positive_half=2*F(3,4)*F(24,25)*F(352,625)-F(54,125)
    # Upper exit probability < 2 exp(-380.88) < 2^-379; sqrt(P)<2^-189.
    assert (F(14,5)-F(61,50)-F(1,5))**2/(2*F(1,20)**2)>380
    error=400*F(1,2**189)+2*F(1,2**379)
    assert error<F(1,1000)
    bounds=[negative_half-F(1,1000),positive_half-F(1,1000)]
    assert min(bounds)>0
    return {'certified':True,'arithmetic':'exact fractions; rational Taylor and Riemann bounds',
        'gaussian_lower_bounds':{k:str(v) for k,v in tails.items()},'wealth_lower':str(wealth_lower),
        'dynkin_integrand_lower':str(h_lower),'state_derivative_lower':str(h_y_lower),
        'theta_subintervals':[['-1/5','0'],['0','1/5']],
        'uniform_derivative_lower_bounds':list(map(str,bounds)),
        'opposite_boundary_score_error_upper':str(error),
        'unique_global_maximizer':'1/5',
        'scope':'one original-model restart, k=2,c=3/4,p=0,constant theta in [-1/5,1/5]',
        'inherited_optimal_payoff_enclosure':['-3.7609','-3.7607'],
        'payoff_provenance':{'ref':'6ea1e2fd8ab1928ded4ea98dc74ba6e1e72cf9d0','path':'revisions/2026-09-24-r30/paper/generated/stopping.tex','blob':'a840cb904798a5f911ed576dc160b7157e46596d','recomputed':False},
        'seconds':time.perf_counter()-tic}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path); a=p.parse_args(); r=certify(); text=json.dumps(r,indent=2,sort_keys=True)
    if a.output: a.output.write_text(text,encoding='utf8')
    print(text)
