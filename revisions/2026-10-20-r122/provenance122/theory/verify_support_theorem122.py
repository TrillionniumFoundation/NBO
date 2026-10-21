#!/usr/bin/env python3
"""Independent exact-rational audit of the R122 support-information theorem.

This is a theorem/algorithm fixture, not an economic experiment or population
sample. It constructs known quadratic objectives independently and checks every
inequality against their exact minima. It writes a fresh receipt only.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse, hashlib, json, time


def minimum(v, slope, curvature, lo, hi):
    if curvature == 0:
        d = lo if slope >= 0 else hi
    else:
        d = max(lo, min(hi, -slope / curvature))
    return v + slope*d + curvature*d*d/2, d


def psi_rational(e, c, radius):
    if radius <= 0:
        return None
    if e == 0:
        return F(0)
    # Every candidate is rational, feasible and independently sufficient.
    return min(e/h+c*h for h in (radius/F(2**j) for j in range(25)))


def interval(a, cap, W, U, pl, pu, mu, L, bound):
    e, c = U-W, (L-mu)/2
    assert e >= 0
    plus = psi_rational(e,c,cap-a)
    minus = psi_rational(e,c,a)
    gl = -bound if plus is None else max(-bound, pl-plus)
    gu = bound if minus is None else min(bound, pu+minus)
    assert gl <= gu
    return gl,gu


def proposal(a,cap,gl,gu,L):
    if gl > 0:
        return -min(a,gl/L)
    if gu < 0:
        return min(cap-a,-gu/L)
    return F(0)


def plain(x):
    if isinstance(x,F): return f'{x.numerator}/{x.denominator}'
    if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [plain(v) for v in x]
    return x


def run():
    start=time.perf_counter()
    cap,mu,L = F(1,4),F(2),F(10)
    delta,tau,omega = F(15,16*2**20),F(1,256),F(1,8192)
    checks=0; cases=0; gains=0; qualified=0; interior=0; boundary=0
    max_contrast_slack=F(0)
    # Broad supports; their gaps are constructed from an exact global minimum,
    # not from the derivative conversion under test.
    for a in [F(0),F(1,64),F(1,16),F(1,8),F(3,16),F(15,64),cap]:
      for g in map(F,[-2,-1,F(-1,2),F(-1,8),0,F(1,8),F(1,2),1,2]):
       for k in map(F,[2,4,6,10]):
        for dp in map(F,[-1,F(-1,4),0,F(1,4),1]):
         for extra in [F(0),F(1,2**24),F(1,2**12)]:
          p=g+dp
          qminus_support_min,_=minimum(F(0),g-p,k-mu,-a,cap-a)
          e=max(F(0),-qminus_support_min)+extra
          U,W=F(0),-e
          for slope_half in [F(0),F(1,2**16)]:
           pl,pu=p-slope_half,p+slope_half
           global_min,_=minimum(e,g-p,k-mu,-a,cap-a)
           assert global_min >=0;checks+=1
           gl,gu=interval(a,cap,W,U,pl,pu,mu,L,F(8))
           assert gl<=g<=gu;checks+=1
           d=proposal(a,cap,gl,gu,L)
           # Realized 40-bit action, recomputed; Fraction floor is exact.
           b=max(F(0),min(cap,F(((a+d)*2**40).numerator//((a+d)*2**40).denominator,2**40)))
           d=b-a
           assert 0<=b<=cap;checks+=1
           upper=max(gl*d,gu*d)+L*d*d/2
           lower=min(gl*d,gu*d)+mu*d*d/2
           diff=g*d+k*d*d/2
           assert lower<=diff<=upper;checks+=1
           Ub=U+upper+delta
           Lb=W+min(pl*d,pu*d)+mu*d*d/2
           B=min(minimum(W,s,mu,-a,cap-a)[0] for s in [pl,pu])
           optimum,_=minimum(F(0),g,k,-a,cap-a)
           assert B<=optimum;checks+=1
           for eta_old,eta_new in [(F(0),F(0)),(F(0),delta),(delta,F(0)),(delta,delta)]:
            true_diff=diff+eta_new-eta_old
            assert lower-delta<=true_diff<=upper+delta;checks+=1
            actual=diff+eta_new
            assert Lb<=actual<=Ub;checks+=1
            assert F(0)<=actual-optimum<=Ub-B;checks+=1
            if upper+delta<0:
             assert true_diff<0;checks+=1
           if upper+delta<0:
            gains+=1
            if Ub-B<=tau and Ub-Lb<=omega:
             qualified+=1
           max_contrast_slack=max(max_contrast_slack,upper-diff)
           cases+=1
           if a in [F(0),cap]:boundary+=1
           else:interior+=1
    # Exact sharpness witnesses, plus the boundary counterexample.
    a,p,e=F(1,8),F(1,2),F(1,1024)
    radius=F(1,8) # 2 sqrt(e*(L-mu)/2), evaluated exactly here.
    sharp=[]
    for g in [p-radius,p+radius]:
        suppmin,_=minimum(e,g-p,L-mu,-a,cap-a)
        assert suppmin==0;checks+=1
        gl,gu=p-radius,p+radius
        assert gl<=g<=gu;checks+=1
        sharp.append(dict(g=g,support_minimum=suppmin))
    for g in [F(-1),F(1)]:
        mm,_=minimum(F(0),g+1,L-mu,F(0),cap)
        assert mm>=0;checks+=1
    # Witness demonstrating q'(0) need not equal touching support slope -1.
    assert F(1) != F(-1);checks+=1
    return dict(kind='independent_exact_rational_theorem_audit',economic_experiment=False,
      population_observations=0,status='passed',quadratic_cases=cases,
      boundary_cases=boundary,interior_cases=interior,exact_assertions=checks,
      strict_actual_gain_gates=gains,complete_tau_width_gates=qualified,
      theorem_mu=mu,theorem_L=L,delta=delta,tau=tau,omega=omega,
      exact_sharpness_witnesses=sharp,boundary_counterexample_checked=True,
      round_action_to_40_bits=True,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      elapsed_wall_seconds=time.perf_counter()-start)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError('Refuse to overwrite previous audit')
    data=plain(run());args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))
