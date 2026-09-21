"""Compute a global continuous-control occupation barrier for the exact test.
For dX=a dt+sigma dW on (0,1), |a|<=A, w_b is C1, piecewise C2,
w_b(0)=w_b(1)=0 and sup_a L^a w_b <= -1_{dist(x,boundary)<b}.
Thus E integral 1_boundary dt <= w_b(x), without assuming the tested policy
is optimal or changing its occupation law. No Monte Carlo sample enters this
bound. Numeric evaluation uses float64, not formal interval arithmetic.
"""
from pathlib import Path
import json, math
import numpy as np
OUT=Path(__file__).resolve().parents[1]/'results'

def occupation_bound(b,x=.5,A=1.,sigma=.4):
    s=min(x,1-x,b); lam=2*A/(sigma*sigma)
    return (math.exp(lam*b)*(-math.expm1(-lam*s))/lam-s)/A

def main():
    rows=[]
    for f in sorted(OUT.glob('manufactured_n*.npz')):
        ar=np.load(f); pi=ar['policy']; astar=ar['actions_exact']; N=len(pi); h=1/(pi.shape[1]-1); k=.2
        node=abs(pi-astar)
        # Linear interpolation of k exp(-t) pi cos(pi x), and holding the date
        # policy fixed until the next time point, have these analytic errors.
        rem=k*math.pi/N+k*math.pi**3*h*h/8+1e-12
        gmax=float((node.max()+rem)**2/(2*k)); candidates=[]
        for j in range(1,N//2+1):
            b=j*h; gi=float((node[:,j:-j].max()+rem)**2/(2*k)); wb=occupation_bound(b)
            candidates.append((gi+gmax*wb,b,gi,wb))
        bound,b,gi,wb=min(candidates)
        row=dict(tag=f.stem,initial_state=.5,global_gain_upper=gmax,interior_gain_upper=gi,
          boundary_layer_width=b,worst_control_boundary_occupation_upper=wb,
          continuous_policy_loss_upper=bound,target=.05,pass_target=bound<=.05,
          reference_used='Analytic verification pair V*=exp(-t)sin(pi x), a*=.2 exp(-t) pi cos(pi x); not a learned or numerical optimal reference',
          arithmetic='analytic domination formulas evaluated in float64 with 1e-12 interpolation allowance; not interval arithmetic')
        rows.append(row)
    (OUT/'manufactured_boundary_bounds.json').write_text(json.dumps(rows,indent=2))
    print(json.dumps(rows,indent=2))
if __name__=='__main__': main()
