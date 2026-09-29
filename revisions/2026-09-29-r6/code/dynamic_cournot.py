"""Finite-horizon capital Cournot game with independent dynamic best responses.

Positive cubature, stopped boundaries and a finite investment set are explicit.
Every state/action/time is enumerated; absence of a pure stage equilibrium is
reported, never replaced by a false Nash claim. This is a grid game, not a
trained neural game or a continuous-control equilibrium certificate.
"""
from __future__ import annotations
import argparse,itertools,json,math,time
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parents[1]/'results'

class Game:
    def __init__(self,n=17,steps=30,actions=11,market=1.,asymmetric=False,tie='low'):
        self.n,self.steps,self.A=n,steps,actions;self.M=market;self.T=3.;self.h=self.T/steps;self.q=math.exp(-.04*self.h);self.tie=tie
        self.grid=np.linspace(.05,1.5,n);K1,K2=np.meshgrid(self.grid,self.grid,indexing='ij');self.points=np.c_[K1.ravel(),K2.ravel()];self.N=n*n
        self.invest=np.linspace(0,.8,actions);self.pairs=np.array(list(itertools.product(self.invest,repeat=2)));self.b=np.array([1.,1.2 if asymmetric else 1.])
        self.g=.5*self.points;price=np.maximum(0,2-self.points.sum(axis=1)/market)
        payoff=price[:,None,None]*self.points[:,None,:]-self.pairs[None,:,:]-.5*self.b*self.pairs[None,:,:]**2
        self.reward=self.h*payoff;self.constant=np.zeros((self.N,actions**2,2));indices=[];weights=[]
        self.boundary=np.any((self.points==self.grid[0])|(self.points==self.grid[-1]),axis=1)
        for z in [(math.sqrt(2),0),(-math.sqrt(2),0),(0,math.sqrt(2)),(0,-math.sqrt(2))]:
            nextk=self.points[:,None,:]+(self.pairs[None,:,:]-.1*self.points[:,None,:])*self.h+.15*self.points[:,None,:]*math.sqrt(self.h)*np.array(z)
            outside=np.any((nextk<self.grid[0])|(nextk>self.grid[-1]),axis=2);nk=np.clip(nextk,self.grid[0],self.grid[-1])
            f=(nk-self.grid[0])/(self.grid[1]-self.grid[0]);ind=np.clip(np.floor(f).astype(int),0,n-2);w=np.clip(f-ind,0,1)
            for a,b,ww in [(0,0,(1-w[:,:,0])*(1-w[:,:,1])),(1,0,w[:,:,0]*(1-w[:,:,1])),(0,1,(1-w[:,:,0])*w[:,:,1]),(1,1,w[:,:,0]*w[:,:,1])]:
                indices.append((ind[:,:,0]+a)*n+ind[:,:,1]+b);weights.append(np.where(outside,0,ww/4))
            self.constant+=np.where(outside[:,:,None],.5*nk/4,0)
        self.index=np.stack(indices,axis=2).astype(np.int32);self.weights=np.stack(weights,axis=2)
        self.reward[self.boundary]=self.g[self.boundary,None,:];self.weights[self.boundary]=0;self.constant[self.boundary]=0
        if np.min(self.weights)<0 or np.max(self.weights.sum(axis=2))>1+1e-12:raise AssertionError('invalid transition weights')
    def Q(self,v,player):
        return (self.reward[:,:,player]+self.q*((self.weights*np.asarray(v)[self.index]).sum(axis=2)+self.constant[:,:,player])).reshape(self.N,self.A,self.A)
    def solve(self):
        start=time.perf_counter();v=np.empty((self.steps+1,self.N,2));v[-1]=self.g;policy=np.empty((self.steps,self.N,2),int);stagegap=np.empty((self.steps,self.N,2));missing=[]
        for t in range(self.steps-1,-1,-1):
            q1=self.Q(v[t+1,:,0],0);q2=self.Q(v[t+1,:,1],1)
            g1=q1.max(axis=1,keepdims=True)-q1;g2=q2.max(axis=2,keepdims=True)-q2
            maximum=np.maximum(g1,g2);pure=maximum<=1e-11
            missing.append(int(np.sum(~pure.any(axis=(1,2)))))
            cost=maximum.reshape(self.N,-1);exists=pure.reshape(self.N,-1)
            # Tie rule selects only among pure equilibria when they exist.
            if self.tie=='high': idx=self.A**2-1-np.argmax(exists[:,::-1],axis=1)
            else:idx=np.argmax(exists,axis=1)
            idx=np.where(exists.any(axis=1),idx,cost.argmin(axis=1));i,j=idx//self.A,idx%self.A;rows=np.arange(self.N)
            policy[t]=np.c_[i,j];v[t,:,0]=q1[rows,i,j];v[t,:,1]=q2[rows,i,j];stagegap[t]=np.c_[g1[rows,i,j],g2[rows,i,j]]
        # Independent policy evaluation and global, dynamic fixed-rival BR.
        pv=np.empty_like(v);pv[-1]=self.g;br=np.empty_like(v);br[-1]=self.g;brpolicy=np.empty_like(policy)
        for t in range(self.steps-1,-1,-1):
            rows=np.arange(self.N);i,j=policy[t].T
            for player in [0,1]:
                qa=self.Q(pv[t+1,:,player],player);pv[t,:,player]=qa[rows,i,j]
                qb=self.Q(br[t+1,:,player],player)
                candidates=qb[rows,:,j] if player==0 else qb[rows,i,:]
                brpolicy[t,:,player]=candidates.argmax(axis=1);br[t,:,player]=candidates.max(axis=1)
        exploit=br-pv;bound=np.zeros(2);bounds=np.zeros((self.steps+1,2))
        for t in range(self.steps-1,-1,-1):
            bound=stagegap[t].max(axis=0)+self.q*bound;bounds[t]=bound
        if np.max(abs(pv-v))>1e-11 or np.any(exploit.max(axis=1)>bounds+1e-9):raise AssertionError('independent best-response verification failed')
        label=f'cournot_n{self.n}_t{self.steps}_a{self.A}_M{self.M:g}_b{self.b[1]:g}_{self.tie}'
        ci=(self.n//2)*self.n+self.n//2
        result=dict(model_id=label,grid=self.n,steps=self.steps,horizon=self.T,investment_actions=self.A,investment_bounds=[0,.8],capital_bounds=[.05,1.5],market_size=self.M,
          demand_intercept=2.,capital_productivity=1.,depreciation=.1,volatility=.15,discount=.04,adjustment_cost=self.b.tolist(),liquidation='0.5 K_i on terminal and all joint stopping faces',tie_rule=self.tie,
          seconds=time.perf_counter()-start,pure_stage_failures=sum(missing),pure_stage_failures_by_time=missing[::-1],
          exploitability_max=exploit.max(axis=(0,1)).tolist(),stage_gap_max=stagegap.max(axis=(0,1)).tolist(),dynamic_gap_bound=bound.tolist(),dynamic_gap_bound_by_time=bounds.tolist(),
          center_value=v[0,ci].tolist(),center_investment=self.invest[policy[0,ci]].tolist(),
          lower_action_frequency=np.mean(policy[:,~self.boundary]==0,axis=(0,1)).tolist(),upper_action_frequency=np.mean(policy[:,~self.boundary]==self.A-1,axis=(0,1)).tolist(),
          scope='all states, all unilateral actions and all time levels of the specified finite dynamic game',
          independent_best_response=True,continuous_equilibrium_bound=None,neural_training=False)
        np.savez_compressed(OUT/f'{label}.npz',capital=self.grid,actions=self.invest,values=v,policy_indices=policy,policy_values=pv,best_response_values=br,best_response_policy=brpolicy,exploitability=exploit,stage_gaps=stagegap,exploitability_bounds_by_time=bounds)
        (OUT/f'{label}.json').write_text(json.dumps(result,indent=2));return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--smoke',action='store_true');a=p.parse_args();OUT.mkdir(exist_ok=True,parents=True)
    cases=[(13,15,9,1.,False,'low')] if a.smoke else [(17,30,11,1.,False,'low'),(17,30,11,1.,False,'high'),(17,30,11,1.,True,'low'),(17,30,11,2.,False,'low'),(25,60,17,1.,False,'low'),(25,60,17,2.,False,'low')]
    results=[]
    for case in cases:
        r=Game(*case).solve();results.append(r);print(json.dumps(r),flush=True)
        (OUT/('cournot_smoke.json' if a.smoke else 'cournot_primary.json')).write_text(json.dumps(results,indent=2))
if __name__=='__main__':main()
