#!/usr/bin/env python3
"""Independent R7 formula checks; no author modules, training, or large-model replay.
Run: python reviewer_checks.py --output diagnostic_results.json
Requires NumPy and SciPy. Source of tested formulas: pinned manuscript in manifest.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import platform
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import minimize_scalar

SEED = 20260917

def utility(c: float, u: float) -> float:
    return c ** (1.0-u) / (1.0-u)

def utility_u(c: float, u: float) -> float:
    z = u-1.0
    return c**(-z)*(1.0+z*math.log(c))/(z*z)

def curvature(c: float, u: float) -> float:
    z = u-1.0
    return c**(-z)*((1.0+z*math.log(c))**2+1.0)/(z**3)

def option(cs: list[float], ps: list[float], k: float, tilt: float) -> dict:
    """Strict concavity yields a unique maximizer, found by derivative bisection.
    tilt adds tilt*(u-2), NOT a harmless utility reparametrization when u is chosen.
    """
    def objective(theta: float) -> float:
        return sum(p*(utility(c,2.0+theta)-utility(c,2.0))
                   for c,p in zip(cs,ps)) + tilt*theta-0.5*k*theta*theta
    def deriv(theta: float) -> float:
        return sum(p*utility_u(c,2.0+theta) for c,p in zip(cs,ps))+tilt-k*theta
    lo,hi=-0.2,0.2
    if deriv(lo)<=0:
        theta=lo
    elif deriv(hi)>=0:
        theta=hi
    else:
        for _ in range(90):
            mid=(lo+hi)/2
            if deriv(mid)>0: lo=mid
            else: hi=mid
        theta=(lo+hi)/2
    check=minimize_scalar(lambda x:-objective(x),bounds=(-0.2,0.2),
                          method='bounded',options={'xatol':1e-14})
    if not check.success: raise RuntimeError('Independent scalar check failed')
    return {'theta':theta,'option':objective(theta),
            'abs_derivative':abs(deriv(theta)),
            'objective_crosscheck_error':abs(objective(theta)+float(check.fun))}

def primitive_checks() -> dict:
    rows=[]
    for p in (0.06,0.08,0.10):
        for k in (20.0,40.0,80.0):
            for tilt in (0.0,1.0,2.0):
                plus=option([0.05,0.8],[p,1-p],k,tilt)
                minus=option([0.5],[1.0],k,tilt)
                relative=plus['option']-minus['option']
                gp=p*utility_u(0.05,2)+(1-p)*utility_u(0.8,2)+tilt
                gm=utility_u(0.5,2)+tilt
                mp=max(p*curvature(0.05,u)+(1-p)*curvature(0.8,u)
                       for u in (1.8,2.2))
                mm=max(curvature(0.5,u) for u in (1.8,2.2))
                # Endpoint curvature maximum follows from the manuscript integral proof.
                reverse_sufficient=gm*gm/(2*(k+mm))-gp*gp/(2*k)
                d0=(utility(0.5,2)-(p*utility(0.05,2)+(1-p)*utility(0.8,2)))/0.5
                rows.append({'p':p,'k':k,'tilt':tilt,'g_plus':gp,'g_minus':gm,
                             'M_plus':mp,'M_minus':mm,'plus':plus,'minus':minus,
                             'relative_option':relative,'no_adjustment_threshold':d0,
                             'adjusted_threshold':d0-relative/0.5,
                             'reverse_premium_sufficient_bound':reverse_sufficient,
                             'minus_lower_trial_feasible':abs(gm)/(k+mm)<=0.2})
    baseline=[r for r in rows if r['tilt']==0.0]
    assert min(r['relative_option'] for r in baseline)>0.00186
    witness=[r for r in rows if r['p']==0.08 and r['k']==40.0 and r['tilt']==2.0][0]
    assert witness['relative_option']<0 and witness['reverse_premium_sufficient_bound']>0
    assert witness['minus_lower_trial_feasible']
    assert max(max(r[s]['objective_crosscheck_error'] for s in ('plus','minus')) for r in rows)<1e-11
    return {'scope':'27 pointwise two-stage economies, two classes each; not a stopped-economy rerun',
            'normalization_change_is_new_primitive':True,'rows':rows,
            'witness':witness,
            'original_family_lower_bound_recomputed':1.4820**2/(2*(80+17.342))-0.6138**2/(2*20)}

def solve(R: np.ndarray,K: np.ndarray,g: np.ndarray) -> tuple[list, list]:
    H=R.shape[0]; vals=[None]*(H+1); pol=[None]*H; vals[H]=g.copy()
    for n in range(H-1,-1,-1):
        q=R[n]+np.einsum('sak,k->sa',K[n],vals[n+1])
        pol[n]=np.argmax(q,axis=1); vals[n]=q.max(axis=1)
    return vals,pol

def coefficients(Ra,Ka,Rb,Kb,g,policy=None):
    H=Ra.shape[0]; out=[None]*(H+1); out[H]=g[None,:].copy()
    for n in range(H-1,-1,-1):
        h=H-n; rows=[]
        for j in range(h+1):
            q=np.zeros_like(Ra[n])
            if j<h: q+=(1-j/h)*(Ra[n]+np.einsum('sak,k->sa',Ka[n],out[n+1][j]))
            if j>0: q+=(j/h)*(Rb[n]+np.einsum('sak,k->sa',Kb[n],out[n+1][j-1]))
            rows.append(q.max(axis=1) if policy is None else q[np.arange(q.shape[0]),policy[n]])
        out[n]=np.asarray(rows)
    return out

def bernstein(c: np.ndarray,t: float) -> np.ndarray:
    h=len(c)-1
    weights=np.array([math.comb(h,j)*t**j*(1-t)**(h-j) for j in range(h+1)])
    return weights@c

def oracle_checks() -> dict:
    rng=np.random.default_rng(SEED); rows=[]
    for H in (1,2,3,4,6,8):
        for rep in range(10):
            S=2+rep%4; A=2+rep%3
            R=rng.uniform(-1.0,1.0,(2,H,S,A))
            K=rng.uniform(0.0,1.0,(2,H,S,A,S))
            K/=K.sum(axis=-1,keepdims=True)
            K*=rng.uniform(0.5,1.0,(2,H,S,A,1))
            g=rng.uniform(-1.0,1.0,S)
            a,b=sorted(rng.uniform(0.0,1.0,2)); w=b-a
            Ra,Rb=(1-a)*R[0]+a*R[1],(1-b)*R[0]+b*R[1]
            Ka,Kb=(1-a)*K[0]+a*K[1],(1-b)*K[0]+b*K[1]
            va,pa=solve(Ra,Ka,g); vb,pb=solve(Rb,Kb,g)
            W=coefficients(Ra,Ka,Rb,Kb,g)
            Fs=[coefficients(Ra,Ka,Rb,Kb,g,p) for p in (pa,pb)]
            M=[None]*(H+1); U=[None]*(H+1); B=[None]*(H+1)
            M[H]=np.zeros(S); U[H]=g[None,:].copy(); B[H]=g.copy()
            V=np.zeros(H+1); L=np.zeros(H+1); Q=np.zeros(H+1); V[H]=np.max(abs(g))
            for n in range(H-1,-1,-1):
                D=np.einsum('sak,k->sa',Ka[n]-Kb[n],vb[n+1]-va[n+1])
                carry=np.maximum(np.einsum('sak,k->sa',Ka[n],M[n+1]),
                                 np.einsum('sak,k->sa',Kb[n],M[n+1]))
                M[n]=np.maximum(0,(D+carry).max(axis=1))
                h=H-n
                U[n]=np.array([(1-j/h)*va[n]+j/h*vb[n]+
                              (j*(h-j)/(h*(h-1)) if h>1 else 0)*M[n] for j in range(h+1)])
                B[n]=np.maximum(Ra[n]+np.einsum('sak,k->sa',Ka[n],B[n+1]),
                                 Rb[n]+np.einsum('sak,k->sa',Kb[n],B[n+1])).max(axis=1)
                beta=K[:,n].sum(axis=-1).max()
                kap=abs(K[1,n]-K[0,n]).sum(axis=-1).max()
                rho=abs(R[1,n]-R[0,n]).max()
                V[n]=abs(R[:,n]).max()+beta*V[n+1]
                L[n]=rho+kap*V[n+1]+beta*L[n+1]
                Q[n]=kap*L[n+1]+beta*Q[n+1]
            order=max(float(np.max(W[n]-U[n])) for n in range(H+1))
            rect=max(float(np.max(W[n]-B[n])) for n in range(H+1))
            cert=max(0.0,max(float(np.max(np.minimum(*[(U[n]-F[n]).max(axis=0) for F in Fs]))) for n in range(H)))
            limit=float(np.max(2*L*w+0.5*Q*w*w))
            under=0.0; replay=0.0; lower=0.0
            for t in np.linspace(0.0,1.0,17):
                Rt=(1-t)*Ra+t*Rb; Kt=(1-t)*Ka+t*Kb
                true,_=solve(Rt,Kt,g)
                for n in range(H+1):
                    under=max(under,float(np.max(true[n]-bernstein(W[n],float(t)))))
                    lower=max(lower,float(np.max(bernstein(Fs[0][n],float(t))-true[n])))
                # A separate fixed-policy backup validates the coefficient representation.
                fixed=g.copy()
                for n in range(H-1,-1,-1):
                    q=Rt[n]+np.einsum('sak,k->sa',Kt[n],fixed)
                    fixed=q[np.arange(S),pa[n]]
                    replay=max(replay,float(np.max(abs(fixed-bernstein(Fs[0][n],float(t))))))
            assert max(order,rect,under,lower,replay,cert-limit)<1e-10
            rows.append({'H':H,'states':S,'actions':A,'a':a,'b':b,
                         'count_minus_chord_max':order,'count_minus_rectangular_max':rect,
                         'optimal_minus_count_max':under,'policy_minus_optimal_max':lower,
                         'policy_coefficient_replay_abs_error':replay,
                         'chord_certificate':cert,'total_error_upper_bound':limit})
    return {'scope':'independent dense random substochastic models; numerical tests are not proofs',
            'seed':SEED,'models':len(rows),'parameter_solves':17*len(rows),'rows':rows,
            'maximum_positive_violation':max(0.0,max(max(r['count_minus_chord_max'],r['count_minus_rectangular_max'],r['optimal_minus_count_max'],r['policy_minus_optimal_max'],r['chord_certificate']-r['total_error_upper_bound']) for r in rows)),
            'maximum_policy_replay_abs_error':max(r['policy_coefficient_replay_abs_error'] for r in rows)}

def accounting() -> dict:
    adjusted=6.888728805714623e-5; fixed=5.299365560501097e-5
    return {'source':'R7 execution_summary.md at 0f0b1d86a61cd741d2cf346f88acbf6ec3026416',
            'certified_array_adjusted_margin':adjusted,'certified_array_fixed_margin':fixed,
            'sufficient_uniform_additional_per_class_error_strictly_below':min(adjusted,fixed)/2,
            'not_an_estimate_of_actual_target_error':True,
            'coefficient_storage_illustrations':[{'H':8,'policy_count':m,'policy_coefficients_per_state':45*m,
                'saved_upper_coefficients_per_state':21,
                'max_fraction_saved_in_bank_plus_upper':21/(45*m+28)} for m in (2,18)],
            'storage_scope':'illustrative persistent arrays only, full H=8 coefficient bank retained; not measured RSS; ignores other common storage'}

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('diagnostic_results.json'))
    args=parser.parse_args()
    results={'manuscript_commit':'fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17',
             'latest_revision_head':'0f0b1d86a61cd741d2cf346f88acbf6ec3026416',
             'scope':'fresh independent formula checks only; no author source imported',
             'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
             'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'primitive':primitive_checks(),'oracles':oracle_checks(),'accounting':accounting()}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(results,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(args.output),'oracle_models':results['oracles']['models'],
                      'max_violation':results['oracles']['maximum_positive_violation'],
                      'max_replay_error':results['oracles']['maximum_policy_replay_abs_error'],
                      'normalization_witness':results['primitive']['witness']},indent=2))

if __name__=='__main__':
    main()
