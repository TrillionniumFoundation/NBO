#!/usr/bin/env python3
"""Independent finite-MDP checks for the R6 advisory review.
Only NumPy is required. No author outputs or training routines are imported.
Run: python reviewer_diagnostics.py --output diagnostic_results.json
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import numpy as np

REVIEWED_COMMIT = '24011fef6da09bc05dc79946a3c1779e1fe7d8a8'
SOURCE_COMMIT = '0727e4fec022c3aa8cff0363db918ad831431c6c'

def at_parameter(rewards, kernels, t):
    return ((1-t)*rewards[:,0]+t*rewards[:,1],
            (1-t)*kernels[:,0]+t*kernels[:,1])

def bellman(rewards, kernels, terminal):
    horizon = len(rewards)
    values = [None]*(horizon+1)
    values[-1] = terminal.copy()
    policy = []
    for n in range(horizon-1, -1, -1):
        q = rewards[n] + np.einsum('sat,t->sa', kernels[n], values[n+1])
        values[n] = q.max(axis=1)
        policy.append(q.argmax(axis=1))
    return values, np.asarray(policy[::-1])

def fixed_policy(rewards, kernels, terminal, policy):
    vals=[None]*(len(rewards)+1); vals[-1]=terminal.copy()
    rows=np.arange(len(terminal))
    for n in range(len(rewards)-1,-1,-1):
        vals[n]=rewards[n,rows,policy[n]]+np.einsum(
            'st,t->s',kernels[n,rows,policy[n]],vals[n+1])
    return vals

def corrected_coefficients(r0,k0,r1,k1,va,vb):
    """R6 corrected chord, elevated to the remaining-horizon degree."""
    horizon=len(r0); states=len(va[-1]); m=np.zeros(states)
    coeff=[None]*(horizon+1); coeff[-1]=va[-1][None,:].copy()
    corrections=[None]*horizon
    for n in range(horizon-1,-1,-1):
        h=horizon-n
        d=np.einsum('sat,t->sa', k0[n]-k1[n], vb[n+1]-va[n+1])
        a=np.einsum('sat,t->sa',k0[n],m)
        b=np.einsum('sat,t->sa',k1[n],m)
        m=np.maximum(0,(d+np.maximum(a,b)).max(axis=1))
        j=np.arange(h+1)[:,None]
        u=(1-j/h)*va[n]+(j/h)*vb[n]
        if h>1:
            u=u+(j*(h-j)/(h*(h-1)))*m
        else:
            assert np.max(np.abs(m))<1e-12
        coeff[n]=u; corrections[n]=m.copy()
    return coeff,corrections

def count_coefficients(r0,k0,r1,k1,terminal,policy=None):
    """Locally conditioned count recursion on any endpoint pair.
    With policy=None, maximize AFTER combining the two branches.
    With a fixed policy, evaluate its exact local Bernstein coefficients.
    """
    horizon=len(r0); coeff=[None]*(horizon+1)
    coeff[-1]=terminal[None,:].copy(); rows=np.arange(len(terminal))
    for n in range(horizon-1,-1,-1):
        h=horizon-n; layer=[]
        for j in range(h+1):
            q=np.zeros_like(r0[n])
            if j<h:
                q+=(1-j/h)*(r0[n]+np.einsum('sat,t->sa',k0[n],coeff[n+1][j]))
            if j>0:
                q+=(j/h)*(r1[n]+np.einsum('sat,t->sa',k1[n],coeff[n+1][j-1]))
            layer.append(q.max(axis=1) if policy is None else q[rows,policy[n]])
        coeff[n]=np.asarray(layer)
    return coeff

def evaluate(coeff,t):
    z=coeff.copy()
    while len(z)>1:
        z=(1-t)*z[:-1]+t*z[1:]
    return z[0]

def split(coeff,t):
    levels=[coeff]
    while len(levels[-1])>1:
        z=levels[-1]; levels.append((1-t)*z[:-1]+t*z[1:])
    return np.asarray([z[0] for z in levels]),np.asarray([z[-1] for z in levels[::-1]])

def restrict(coeff,a,b):
    if b<1: coeff=split(coeff,b)[0]
    if a>0: coeff=split(coeff,a/b)[1]
    return coeff

def certificate(upper,policies,depth=3):
    result=0.0
    for a,b in zip(np.linspace(0,1,2**depth+1)[:-1], np.linspace(0,1,2**depth+1)[1:]):
        for n,u in enumerate(upper):
            uc=restrict(u,a,b)
            gaps=np.stack([(uc-restrict(p[n],a,b)).max(axis=0) for p in policies])
            result=max(result,float(gaps.min(axis=0).max()))
    return result

def strict_example():
    # At date zero choose x or y. At date one the parameter changes
    # the probability of a terminal payoff of one: x pays with probability t,
    # y with probability 1-t. No current regime is observed before an action.
    r=np.zeros((2,2,3,2)); k=np.zeros((2,2,3,2,3)); g=np.array([0.,1.,0.])
    for z in range(2):
        for s in range(3):
            k[0,z,s,0,1]=1; k[0,z,s,1,2]=1
        for a in range(2):
            k[1,z,0,a,2]=1
            k[1,z,1,a,1 if z else 2]=1
            k[1,z,2,a,2 if z else 1]=1
    r0,k0=at_parameter(r,k,0); r1,k1=at_parameter(r,k,1)
    va,pa=bellman(r0,k0,g); vb,pb=bellman(r1,k1,g)
    u,m=corrected_coefficients(r0,k0,r1,k1,va,vb)
    w=count_coefficients(r0,k0,r1,k1,g)
    lower=[count_coefficients(r0,k0,r1,k1,g,p) for p in (pa,pb)]
    v,_=bellman(*at_parameter(r,k,.5),g)
    cu=certificate(u,lower); cw=certificate(w,lower)
    assert abs(cu-.5)<1e-12 and abs(cw-.25)<1e-12
    return {'horizon':2,'states':3,'actions':2,
            'description':'genuine affine transition changes; V0(t)=max(t,1-t)',
            'at_midpoint':{'optimal_value':float(v[0][0]),
                           'corrected_upper':float(evaluate(u[0],.5)[0]),
                           'localized_count_upper':float(evaluate(w[0],.5)[0])},
            'same_endpoint_policy_bank_all_state_date_certificate':
                {'corrected_chord':cu,'localized_count':cw},
            'initial_bernstein_coefficients':{'corrected':u[0][:,0].tolist(),
                                               'localized_count':w[0][:,0].tolist()},
            'correction_maximum':max(float(x.max()) for x in m)}

def random_checks(seed=260916,cases=160):
    rng=np.random.default_rng(seed)
    min_coefficient_slack=float('inf'); min_upper_slack=float('inf')
    max_policy_error=0.; max_count_minus_chord_certificate=-float('inf')
    for case in range(cases):
        h=1+case%8; s=3; a=3
        r=rng.normal(size=(h,2,s,a))
        k=rng.random((h,2,s,a,s)); k/=k.sum(axis=-1,keepdims=True)
        k*=rng.uniform(.45,1.,size=(h,2,s,a,1))
        g=rng.normal(size=s)
        left,right=sorted(rng.uniform(0,1,size=2))
        r0,k0=at_parameter(r,k,left); r1,k1=at_parameter(r,k,right)
        va,pa=bellman(r0,k0,g); vb,pb=bellman(r1,k1,g)
        u,_=corrected_coefficients(r0,k0,r1,k1,va,vb)
        w=count_coefficients(r0,k0,r1,k1,g)
        lower=[count_coefficients(r0,k0,r1,k1,g,p) for p in (pa,pb)]
        slack=min(float(np.min(un-wn)) for un,wn in zip(u,w))
        min_coefficient_slack=min(min_coefficient_slack,slack)
        assert slack>=-2e-12, ('coefficient dominance failed',case,slack)
        cu=certificate(u,lower); cw=certificate(w,lower)
        max_count_minus_chord_certificate=max(max_count_minus_chord_certificate,cw-cu)
        assert cw<=cu+2e-12
        for t in np.linspace(0,1,11):
            rt=(1-t)*r0+t*r1; kt=(1-t)*k0+t*k1
            v,_=bellman(rt,kt,g)
            pval=fixed_policy(rt,kt,g,pa)
            for n in range(h+1):
                us=float(np.min(evaluate(w[n],t)-v[n]))
                min_upper_slack=min(min_upper_slack,us)
                assert us>=-2e-12
                err=float(np.max(np.abs(evaluate(lower[0][n],t)-pval[n])))
                max_policy_error=max(max_policy_error,err)
                assert err<2e-12
    return {'seed':seed,'cases':cases,'horizons':list(range(1,9)),
            'states':3,'actions':3,'parameter_samples_per_case':11,
            'minimum_corrected_minus_local_count_coefficient':min_coefficient_slack,
            'minimum_count_upper_minus_optimum_at_test_parameters':min_upper_slack,
            'maximum_fixed_policy_polynomial_replay_error':max_policy_error,
            'maximum_local_count_minus_corrected_certificate':max_count_minus_chord_certificate,
            'passed':True,
            'scope':'Independent randomized finite-MDP checks, not reruns of the 1617-state author experiment. The report supplies the general proof.'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,default=Path('diagnostic_results.json'))
    args=ap.parse_args()
    result={'reviewed_commit':REVIEWED_COMMIT, 'reviewed_source_commit':SOURCE_COMMIT,
            'environment':{'python':platform.python_version(),'numpy':np.__version__},
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'strict_example':strict_example(), 'random_checks':random_checks()}
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
