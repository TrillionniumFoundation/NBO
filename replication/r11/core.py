"""R11: joint contract certificates and reachable-state transport dominance.

Inherited arrays and scientific sources are read-only. The certified target is
those stored arrays and the stored piecewise-affine first-date knot operator.
"""
from __future__ import annotations
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import sys, time, hashlib, json, itertools
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'replication/r9'))
from contracts import (Model, Specification, Contract, FirstDateMenu,
                       first_moments, r7, old, SIGNS)
EPS=1e-7
BOX={'law':[.12,.13], 'benefit':[.424,.4245], 'fee':[.7999,.8001],
     'long':[.7999,.8001], 'short':[.4999,.5001]}

class Directional(Contract):
    def __init__(self,base,fee=0.,min_term=8,direction='full'):
        super().__init__(base,fee,min_term)
        if direction not in ('full','up','down'): raise ValueError(direction)
        self.direction=direction
    def allowed(self,n,adjust=True,sign=None):
        ans=super().allowed(n,adjust,sign)
        if self.direction=='full': return ans
        ans=ans.copy(); e=self.e[0]; common=e.menu[:,1]
        keep=common>=-1e-14 if self.direction=='up' else common<=1e-14
        ans[:,:len(common)] &= keep[None,:]
        if e.extra:
            th=e.extra[n].actions[:,:,1]
            ans[:,len(common):self.na] &= th>=-1e-14 if self.direction=='up' else th<=1e-14
        return ans

class Joint:
    def __init__(self,base,box=BOX):
        self.base=base; self.box=box
        self.fm=FirstDateMenu(base,extra_points=(*box['long'],*[-x for x in box['short']]))
        self.groups=[]
        for pair in self.fm.pairs:
            ix=np.where(np.all(self.fm.actions[:,:2]==pair,axis=1))[0]
            ix=ix[np.argsort(self.fm.actions[ix,2])]
            self.groups.append((pair,ix))
        self.cache={}; self.solve_seconds=0.; self.solve_count=0; self.artifacts={}
    def mask(self,adj,sign,L,S,direction='full'):
        a=self.fm.actions
        mask=(a[:,2]>=(-S if sign=='nonpositive' else 0)-1e-13)&(a[:,2]<=(0 if sign=='nonpositive' else L)+1e-13)
        if not adj: mask &= abs(a[:,1])<1e-14
        if direction=='up': mask &= a[:,1]>=-1e-14
        if direction=='down': mask &= a[:,1]<=1e-14
        return mask
    def q(self,k,v,d):
        return self.fm.reward[k]+d*self.fm.duration[k]+self.fm.rows[k]@v
    def k(self,k,v): return self.fm.rows[k]@v
    def solve(self,lam,d,F,adj,L,S,m=1,direction='full'):
        # Continuations do not depend on first-date permissions.
        key=(lam,d,F,adj,m,direction)
        if key not in self.cache:
            t=time.perf_counter(); c=Directional(self.base,F,m,direction)
            z=c.pair(lam,d,adj)['positive']
            self.cache[key]=(z,c); self.solve_count+=1
            self.solve_seconds+=time.perf_counter()-t
        z,c=self.cache[key]
        q=(1-lam)*self.q(0,z['value'][1],d)+lam*self.q(1,z['value'][1],d)
        first={}
        for s in SIGNS:
            ix=np.where(self.mask(adj,s,L,S,direction))[0]; i=int(ix[q[ix].argmax()])
            best={'index':i,'indices':np.array([i]),'weights':np.array([1.]),
                  'value':float(q[i]),'action':self.fm.actions[i].copy()}
            # A permission endpoint need not be a deposited knot. The economic
            # target between consecutive knots is the affine interpolation of
            # the stored rows, not a projection to the nearest feasible knot.
            edge=L if s=='positive' else -S
            if not self.fm.lower<=edge<=self.fm.upper: raise ValueError('permission outside envelope')
            for pair,ids in self.groups:
                th=pair[1]
                if (not adj and abs(th)>1e-14) or (direction=='up' and th<-1e-14) or (direction=='down' and th>1e-14):continue
                ps=self.fm.actions[ids,2];at=int(np.searchsorted(ps,edge))
                if at<len(ps) and ps[at]==edge:
                    jj=np.array([ids[at]]);ww=np.array([1.])
                else:
                    if not 0<at<len(ps):raise ValueError('unbracketed permission')
                    w=(edge-ps[at-1])/(ps[at]-ps[at-1]);jj=ids[at-1:at+1];ww=np.array([1-w,w])
                val=float(ww@q[jj])
                if val>best['value']:
                    best={'index':int(jj[0]) if len(jj)==1 else -1,'indices':jj,'weights':ww,
                          'value':val,'action':np.array([*pair,edge])}
            first[s]=best
        return {'v':z['value'],'p':z['policy'],'first':first,'c':c}
    def coefficients(self,z,sign,d,F):
        """Global-law Bernstein coefficients for one feasible stopping policy."""
        c=z['c']; prev=c.coefficients(z['p'],d,F,all_dates=True)[1]
        ix=z['first'][sign]['indices']; w=z['first'][sign]['weights']; h=self.base.steps; out=[]
        for j in range(h+1):
            val=0.
            if j<h: val+=(1-j/h)*float(w@self.q(0,prev[j],d)[ix])
            if j>0: val+=j/h*float(w@self.q(1,prev[j-1],d)[ix])
            out.append(val)
        return np.asarray(out)
    def upper(self,za,zb,a,b,d,F,adj,L,S,method='chord',m=1):
        """Same first-date permissions for both upper oracles; later menus unchanged."""
        c=za['c'];N=self.base.steps
        if method=='chord':
            M=np.zeros(self.base.ns)
            for n in range(N-2,-1,-1):
                diff=zb['v'][n+1]-za['v'][n+1]
                if n:
                    D=(b-a)*(c.continuation(0,n,diff)-c.continuation(1,n,diff))
                    if n<N-2:
                        k0=c.continuation(0,n,M);k1=c.continuation(1,n,M)
                        D+=np.maximum((1-a)*k0+a*k1,(1-b)*k0+b*k1)
                    M=np.maximum(0.,np.where(c.allowed(n,adj),D,-np.inf).max(1))
                else:
                    D=(b-a)*(self.k(0,diff)-self.k(1,diff))
                    k0=self.k(0,M);k1=self.k(1,M)
                    D+=np.maximum((1-a)*k0+a*k1,(1-b)*k0+b*k1)
                    out={};j=np.arange(N+1)
                    for s in SIGNS:
                        mm=max(0.,float(D[self.mask(adj,s,L,S)].max()))
                        out[s]=(1-j/N)*za['first'][s]['value']+j/N*zb['first'][s]['value']+j*(N-j)/(N*(N-1))*mm
                    return out
        elif method=='count':
            prev=c.terminal[None,:]
            for n in range(N-1,-1,-1):
                h=N-n
                if n:
                    z=np.empty((h+1,c.ns));z[0]=za['v'][n];z[h]=zb['v'][n]
                    for j in range(1,h):
                        q0=c.q(0,n,prev[j],d,F);q1=c.q(1,n,prev[j],d,F)
                        p0=c.q(0,n,prev[j-1],d,F);p1=c.q(1,n,prev[j-1],d,F)
                        q=(1-j/h)*((1-a)*q0+a*q1)+j/h*((1-b)*p0+b*p1)
                        z[j]=np.where(c.allowed(n,adj),q,-np.inf).max(1)
                    prev=z
                else:
                    out={s:np.empty(N+1) for s in SIGNS}
                    for s in SIGNS:
                        out[s][0]=za['first'][s]['value'];out[s][-1]=zb['first'][s]['value']
                    for j in range(1,h):
                        q0=self.q(0,prev[j],d);q1=self.q(1,prev[j],d)
                        p0=self.q(0,prev[j-1],d);p1=self.q(1,prev[j-1],d)
                        q=(1-j/h)*((1-a)*q0+a*q1)+j/h*((1-b)*p0+b*p1)
                        for s in SIGNS:out[s][j]=q[self.mask(adj,s,L,S)].max()
                    return out
        raise ValueError(method)
    def region(self,method='chord',cells=1):
        """Joint 5D sign and active-surrender certificate, not point interpolation."""
        before_solve=self.solve_seconds; before_count=self.solve_count
        B=self.box; corners=list(itertools.product(B['benefit'],B['fee']))
        L0,L1=B['long'];S0,S1=B['short'];cuts=np.linspace(*B['law'],cells+1)
        bank={};upp={};tim=time.perf_counter();detail=[]
        # Three targets: adjusted, no-adjustment with surrender, noncancellable zero.
        for target,(adj,m) in enumerate(((True,1),(False,1),(False,8))):
            bank[target]={s:[] for s in SIGNS}
            seen={s:set() for s in SIGNS}
            for lam in cuts:
                for d,F in corners:
                    z=self.solve(float(lam),d,F,adj,L0,S0,m)
                    for s in SIGNS:
                        key=hashlib.sha256(z['p'][1:].tobytes()+z['first'][s]['action'].tobytes()).hexdigest()
                        if key not in seen[s]: bank[target][s].append(z);seen[s].add(key)
        lower={}
        for target in bank:
            for s in SIGNS:
                lower[target,s]=np.stack([[self.coefficients(z,s,d,F) for d,F in corners] for z in bank[target][s]])
        for (t,s),co in lower.items(): self.artifacts[f'{method}.lower.{t}.{s}']=co
        for t,bb in bank.items():
            for s,pols in bb.items():
                for i,z in enumerate(pols):
                    self.artifacts[f'{method}.policy.{t}.{s}.{i}']=z['p']
                    self.artifacts[f'{method}.first.{t}.{s}.{i}']=z['first'][s]['action']
        for ia,(a,b) in enumerate(zip(cuts[:-1],cuts[1:])):
            UC={}
            for target,(adj,m) in enumerate(((True,1),(False,1),(False,8))):
                arr=[]
                for d,F in corners:
                    za=self.solve(float(a),d,F,adj,L1,S1,m);zb=self.solve(float(b),d,F,adj,L1,S1,m)
                    arr.append(self.upper(za,zb,a,b,d,F,adj,L1,S1,method,m))
                for s in SIGNS: UC[target,s]=np.stack([v[s] for v in arr])
            for (t,s),co in UC.items(): self.artifacts[f'{method}.upper.{ia}.{t}.{s}']=co
            LC={key:np.stack([[r7.restrict(co,float(a),float(b)) for co in pol] for pol in val]) for key,val in lower.items()}
            def difference(t1,s1,t2,s2):
                low=max(float((p-UC[t2,s2]).min()) for p in LC[t1,s1])-2*EPS
                high=min(float((UC[t1,s1]-p).max()) for p in LC[t2,s2])+2*EPS
                return [low,high]
            detail.append({'law_cell':[float(a),float(b)],
                'adjusted':difference(0,'positive',0,'nonpositive'),
                'zero':difference(1,'positive',1,'nonpositive'),
                'active_surrender_gain':difference(1,'positive',2,'positive')})
        result={'method':method,'box':B,'cells':detail,'policy_bank_sizes':{f'{t}.{s}':len(v) for t,z in bank.items() for s,v in z.items()},
                'construction_and_validation_excluded_seconds':time.perf_counter()-tim,'per_value_allowance':EPS}
        result['endpoint_seconds_in_invocation']=self.solve_seconds-before_solve
        result['endpoint_solves_in_invocation']=self.solve_count-before_count
        result['nonendpoint_seconds']=result['construction_and_validation_excluded_seconds']-result['endpoint_seconds_in_invocation']
        result['bounds']={k:[min(x[k][0] for x in detail),max(x[k][1] for x in detail)] for k in ('adjusted','zero','active_surrender_gain')}
        result['certified']=result['bounds']['adjusted'][0]>0 and result['bounds']['zero'][1]<0 and result['bounds']['active_surrender_gain'][0]>0
        return result
    def reachability(self):
        N=self.base.steps;R=np.zeros((N+1,self.base.ns),bool);R[0,self.base.center]=True
        keep=self.mask(True,'positive',self.box['long'][1],self.box['short'][1])|self.mask(True,'nonpositive',self.box['long'][1],self.box['short'][1])
        for k in (0,1):R[1]|=np.asarray(self.fm.rows[k][keep].sum(0)).ravel()>0
        for n in range(1,N):
            for e in self.base.e:
                for ker in [e.common]+([e.extra[n]] if e.extra else []):
                    R[n+1]|=np.asarray(ker.matrix.T@np.repeat(R[n].astype(float),ker.na)).ravel()>0
        return R
    def interval_up(self):
        B=self.box;c=Directional(self.base,0,1,'up');lo=np.empty((9,c.ns));hi=np.empty_like(lo);lo[-1]=hi[-1]=c.terminal
        for n in range(7,0,-1):
            q0=c.q(0,n,lo[n+1],B['benefit'][0],B['fee'][1]);q1=c.q(1,n,lo[n+1],B['benefit'][0],B['fee'][1])
            low=np.minimum(*[(1-l)*q0+l*q1 for l in B['law']])
            q0=c.q(0,n,hi[n+1],B['benefit'][1],B['fee'][0]);q1=c.q(1,n,hi[n+1],B['benefit'][1],B['fee'][0])
            high=np.maximum(*[(1-l)*q0+l*q1 for l in B['law']])
            lo[n]=np.where(c.allowed(n,True),low,-np.inf).max(1)-EPS
            hi[n]=np.where(c.allowed(n,True),high,-np.inf).max(1)+EPS
        lo[0]=hi[0]=0.  # Date zero is handled by the first-date operator.
        return lo,hi
    def dominance(self):
        """Signed row transport bound comparing each negative drift with drift zero."""
        B=self.box;R=self.reachability();lo,hi=self.interval_up();e=self.base.e[0]
        self.artifacts.update(reachable=R,interval_lower=lo,interval_upper=hi)
        common=e.menu;lookup={tuple(np.round(a,13)):i for i,a in enumerate(common)}
        neg=np.where(common[:,1]<-1e-14)[0]
        zero=np.array([lookup[(round(common[i,0],13),0.,round(common[i,2],13))] for i in neg])
        records=[]
        for n in range(7,-1,-1):
            mid=(lo[n+1]+hi[n+1])/2;rad=(hi[n+1]-lo[n+1])/2
            ix=np.where(R[n]&~e.boundary)[0];components=[]
            if n:
                # Deposited frozen proposals are nonnegative on this whole support.
                th=e.extra[n].actions[ix,:,1] if e.extra else np.empty((len(ix),0))
                if np.any(th<-1e-14):raise AssertionError('negative frozen proposal needs a counterpart')
                rn=(ix[:,None]*len(common)+neg).ravel();rz=(ix[:,None]*len(common)+zero).ravel()
                for end in self.base.e:
                    ker=end.common;D=(ker.matrix[rn]-ker.matrix[rz]).tocsr()
                    reward=ker.base-self.base.spec.cost*ker.effort
                    rr=(reward[ix[:,None],neg]-reward[ix[:,None],zero]).ravel()
                    aa=(ker.duration[ix[:,None],neg]-ker.duration[ix[:,None],zero]).ravel()
                    components.append(rr+np.maximum(B['benefit'][0]*aa,B['benefit'][1]*aa)+D@mid+abs(D)@rad)
            else:
                
                if e.extra and np.any(e.extra[0].actions[self.base.center,:,1]<-1e-14):
                    raise AssertionError('initial negative frozen proposal needs separate checking')
                actions=self.fm.actions;lookup0={tuple(np.round(a,13)):i for i,a in enumerate(actions)}
                mask=(self.mask(True,'positive',B['long'][1],B['short'][1])|self.mask(True,'nonpositive',B['long'][1],B['short'][1]))&(actions[:,1]<-1e-14)
                ni=np.where(mask)[0];zi=np.array([lookup0[(round(actions[i,0],13),0.,round(actions[i,2],13))] for i in ni])
                for k in (0,1):
                    D=(self.fm.rows[k][ni]-self.fm.rows[k][zi]).tocsr()
                    rr=self.fm.reward[k][ni]-self.fm.reward[k][zi]
                    aa=self.fm.duration[k][ni]-self.fm.duration[k][zi]
                    components.append(rr+np.maximum(B['benefit'][0]*aa,B['benefit'][1]*aa)+D@mid+abs(D)@rad)
            bound=max(float(((1-l)*components[0]+l*components[1]).max()) for l in B['law'])+2*EPS
            records.append({'date':n,'live_reachable_nodes':len(ix),'negative_minus_zero_upper':bound,'tested_pairs':len(components[0])})
        return {'box':B,'reachable_counts':R.sum(1).tolist(),'dates':records,'certified':all(x['negative_minus_zero_upper']<0 for x in records),'allowance_per_comparison':2*EPS}
