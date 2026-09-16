#!/usr/bin/env python3
"""Persistent stochastic capacity game, exact active-set equilibrium and
independent unilateral dynamic deviations at EVERY date/state/player.
The historical renewal economy is preserved as the survival=0 regression.
"""
from __future__ import annotations
import itertools,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'replication/r5/output'
STATES=list(itertools.product(range(2),repeat=3))
P=np.array([[.8,.2],[.2,.8]]);D=np.array([1.,1.3]);DELTA=.95;KAPPA=.4

def expectation(W,p1,p2):return float((W*np.outer([1-p1,p1],[1-p2,p2])).sum())

def clipped_fixed_point(a,b,c,d):
    """Enumerate all nine active sets, rather than assuming interiority."""
    candidates=[]
    for sx,sy in itertools.product((-1,0,1),repeat=2):
        if sx==sy==0:
            if abs(1-b*d)<1e-12:continue
            x=(a+b*c)/(1-b*d);y=c+d*x
        elif sx!=0:
            x=0. if sx<0 else 1.;y=c+d*x if sy==0 else 0. if sy<0 else 1.
        else:
            y=0. if sy<0 else 1.;x=a+b*y
        if -1e-12<=x<=1+1e-12 and -1e-12<=y<=1+1e-12 and max(abs(x-np.clip(a+b*y,0,1)),abs(y-np.clip(c+d*x,0,1)))<1e-11:
            candidates.append(np.clip([x,y],0,1))
    assert candidates and np.max(np.ptp(candidates,axis=0))<1e-9
    return candidates[0]

def evaluated_values(policy,survival):
    N=len(policy);V=np.zeros((N+1,2,2,2,2))
    for k1,k2,z in STATES:V[-1,:,k1,k2,z]=[.05*k1,.05*k2]
    for n in range(N-1,-1,-1):
        for k1,k2,z in STATES:
            a=policy[n,:,k1,k2,z];p1=survival*k1+(1-survival*k1)*a[0];p2=survival*k2+(1-survival*k2)*a[1]
            q=np.array([k1,k2])/3
            for i in (0,1):
                W=np.einsum('ijk,k->ij',V[n+1,i],P[z])
                V[n,i,k1,k2,z]=q[i]*(D[z]-q.sum())-.5*KAPPA*a[i]**2+DELTA*expectation(W,p1,p2)
    return V

def all_date_best_response(policy,survival):
    baseline=evaluated_values(policy,survival);N=len(policy);gain=np.zeros_like(policy);deviation=np.zeros_like(policy)
    for player in (0,1):
        BR=baseline[-1,player].copy()
        for n in range(N-1,-1,-1):
            new=np.empty((2,2,2))
            for k1,k2,z in STATES:
                W=np.einsum('ijk,k->ij',BR,P[z]);kk=[k1,k2];rival=policy[n,1-player,k1,k2,z]
                rp=survival*kk[1-player]+(1-survival*kk[1-player])*rival
                scale=1-survival*kk[player]
                marginal=((1-rp)*(W[1,0]-W[0,0])+rp*(W[1,1]-W[0,1])) if player==0 else ((1-rp)*(W[0,1]-W[0,0])+rp*(W[1,1]-W[1,0]))
                a=float(np.clip(DELTA*scale*marginal/KAPPA,0,1));op=survival*kk[player]+scale*a
                p1,p2=(op,rp) if player==0 else (rp,op)
                qi=kk[player]/3;qj=kk[1-player]/3
                new[k1,k2,z]=qi*(D[z]-qi-qj)-.5*KAPPA*a*a+DELTA*expectation(W,p1,p2)
                deviation[n,player,k1,k2,z]=a
            # This comparison belongs INSIDE the backward date loop.
            gain[n,player]=new-baseline[n,player];BR=new
    loc=np.unravel_index(np.argmax(gain),gain.shape)
    return dict(max_positive_gain=float(max(gain.max(),0)),signed_max=float(gain.max()),signed_min=float(gain.min()),
        gains_by_date_player=gain.reshape(N,2,-1).max(2).tolist(),
        largest_location=dict(date=int(loc[0]),player=int(loc[1]),capacities=[int(loc[2]),int(loc[3])],demand_state=int(loc[4])),
        gains=gain.tolist(),best_response_actions=deviation.tolist(),baseline=baseline)

def solve(survival=.8,steps=12):
    V=np.zeros((steps+1,2,2,2,2));pol=np.zeros((steps,2,2,2,2));contraction=0.
    for k1,k2,z in STATES:V[-1,:,k1,k2,z]=[.05*k1,.05*k2]
    for n in range(steps-1,-1,-1):
        for k1,k2,z in STATES:
            W=np.einsum('ijk,k->ij',V[n+1,0],P[z]);Z=np.einsum('ijk,k->ij',V[n+1,1],P[z])
            p10=survival*k1;p20=survival*k2;s1=1-p10;s2=1-p20
            cross1=W[1,1]-W[1,0]-W[0,1]+W[0,0];cross2=Z[1,1]-Z[1,0]-Z[0,1]+Z[0,0]
            a=DELTA*s1*(W[1,0]-W[0,0]+p20*cross1)/KAPPA;b=DELTA*s1*s2*cross1/KAPPA
            c=DELTA*s2*(Z[0,1]-Z[0,0]+p10*cross2)/KAPPA;d=DELTA*s1*s2*cross2/KAPPA
            contraction=max(contraction,abs(b*d));x,y=clipped_fixed_point(a,b,c,d)
            pol[n,:,k1,k2,z]=x,y;p1=p10+s1*x;p2=p20+s2*y;q1=k1/3;q2=k2/3
            V[n,0,k1,k2,z]=q1*(D[z]-q1-q2)-.5*KAPPA*x*x+DELTA*expectation(W,p1,p2)
            V[n,1,k1,k2,z]=q2*(D[z]-q1-q2)-.5*KAPPA*y*y+DELTA*expectation(Z,p1,p2)
    assert contraction<1
    br=all_date_best_response(pol,survival);assert np.max(abs(br.pop('baseline')-V))<1e-12
    assert br['max_positive_gain']<1e-10
    distorted=pol.copy();distorted[-1,0,1,1,0]=1.
    neg=all_date_best_response(distorted,survival);neg.pop('baseline');assert neg['max_positive_gain']>.1
    return dict(survival=survival,steps=steps,states=8,discount=DELTA,investment_cost=KAPPA,
        probability='s*K_i+(1-s*K_i)*a_i',policies=pol.tolist(),values=V.tolist(),best_response=br,
        max_best_response_product=contraction,capacity_policy_range=float(np.max(np.ptp(pol,axis=(2,3)))),
        early_date_policy_range=float(np.max(np.ptp(pol[:-1],axis=0))),
        deliberately_distorted_late_policy=neg,root_policies=pol[0].tolist(),
        interpretation='Exact finite-state Markov-perfect reference; continuous investments, persistent capacities; not a trained neural equilibrium experiment.')

def main():
    reset=solve(0.,4);persistent=solve(.8,12)
    # Independent closed form for the historical reset regression.
    expected=DELTA*(P@D/3-1/9)/(KAPPA+DELTA/9)
    pol=np.array(reset['policies']);assert np.max(abs(pol[:3]-expected))<1e-12
    assert np.max(abs(pol[3]-.05*DELTA/KAPPA))<1e-12
    result=dict(reset=reset,persistent=persistent,renewal_closed_form=expected.tolist(),
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'persistent_game.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:persistent[k] for k in ('capacity_policy_range','early_date_policy_range','max_best_response_product')},indent=2))
    print('all-date gain',persistent['best_response']['max_positive_gain'])
if __name__=='__main__':main()
