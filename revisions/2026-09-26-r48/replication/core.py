"""R48 numerical proposals with exact, witness-only certification.
No routine computes an exact optimal operating value. All future operating
information used by prices, candidates and relaxations comes from certified
outward-rounded Bellman enclosures. The raw model contains no saved policies.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import time, json, gzip, hashlib, heapq, sys
import numpy as np
from scipy.optimize import linprog, minimize
from scipy.sparse import coo_matrix
Z=F(0); O=F(1)

def dot(a,b): return sum((x*y for x,y in zip(a,b)),Z)
def enc(x):
    if isinstance(x,F): return str(x)
    if isinstance(x,np.generic): return x.item()
    if isinstance(x,dict): return {str(k):enc(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [enc(v) for v in x]
    return x

def load(raw):
    d=dict(raw)
    def frac(x): return [frac(v) for v in x] if isinstance(x,list) else F(x)
    for k in ['beta','epsilon','r','k','P','g','nu']: d[k]=frac(raw[k])
    return d

def floorq(x,b): return F((x.numerator*(1<<b))//x.denominator,1<<b)
def ceilq(x,b): return -floorq(-x,b)
def dyad(x,b=40):
    if not np.isfinite(x): raise ValueError('nonfinite proposal')
    return F(round(float(x)*(1<<b)),1<<b)

def validate(d):
    n,T,m=d['n'],d['T'],d['m']
    assert n>0 and T>0 and m>1 and Z<d['beta']<O and d['epsilon']>Z
    assert len(d['g'])==n and len(d['nu'])==n
    assert min(d['nu'])>=0 and sum(d['nu'])==1
    for t in range(T):
        for i in range(n):
            assert len(d['P'][t][i])==m
            for a in range(m):
                assert len(d['P'][t][i][a])==n
                assert min(d['P'][t][i][a])>=0 and sum(d['P'][t][i][a])==1
                assert d['k'][t][i][a]>=0

def witness(d,target,cap=F(4096)):
    start=time.perf_counter(); n,T,m=d['n'],d['T'],d['m']; b=d['beta']
    K=max(x for t in d['k'] for row in t for x in row)
    sums=[sum((b**j for j in range(h)),Z) for h in range(T+1)]
    DC=K*sum((b**t*sums[T-t] for t in range(T)),Z)
    history=[]; bits=8
    while True:
        lo=[[Z]*n for _ in range(T+1)]; hi=[[Z]*n for _ in range(T+1)]
        lo[T]=[floorq(x,bits) for x in d['g']]; hi[T]=[ceilq(x,bits) for x in d['g']]
        for t in reversed(range(T)):
            for i in range(n):
                lo[t][i]=floorq(max(d['r'][t][i][a]+b*dot(d['P'][t][i][a],lo[t+1]) for a in range(m)),bits)
                hi[t][i]=ceilq(max(d['r'][t][i][a]+b*dot(d['P'][t][i][a],hi[t+1]) for a in range(m)),bits)
        widths=[max(hi[t][i]-lo[t][i] for i in range(n)) for t in range(T+1)]
        xi=max(widths[:-1]); s=(1-b)*d['epsilon']
        budget=cap*sum((b**t*(widths[t]+b*widths[t+1]) for t in range(T)),Z)
        policy_bits=max(bits,32)
        ubudget=DC*(xi/s+(m-1)*F(1,1<<policy_bits))
        history.append(dict(bits=bits,width=xi,price_budget=budget,repair_budget=ubudget))
        if xi<s and budget<=target/64 and ubudget<=target/64: break
        bits+=8
        if bits>256: raise ArithmeticError('requested precision exceeds supported safety limit')
    dl=[[[max(Z,lo[t][i]-d['r'][t][i][a]-b*dot(d['P'][t][i][a],hi[t+1])) for a in range(m)] for i in range(n)] for t in range(T)]
    d0=[[[lo[t][i]-d['r'][t][i][a]-b*dot(d['P'][t][i][a],lo[t+1]) for a in range(m)] for i in range(n)] for t in range(T)]
    return dict(lo=lo,hi=hi,widths=widths,dl=dl,d0=d0,bits=bits,policy_bits=policy_bits,history=history,seconds=time.perf_counter()-start,DC=DC)

def row_extreme(q,bounds,maximize=False):
    low=[l for l,u in bounds]; rem=O-sum(low)
    if rem<0 or sum((u for l,u in bounds),Z)<1: return None
    p=list(low)
    for a in sorted(range(len(q)),key=lambda a:q[a],reverse=maximize):
        z=min(rem,bounds[a][1]-p[a]); p[a]+=z; rem-=z
    assert rem==0
    return dot(p,q),p

def policy_value(d,p):
    n,T,m=d['n'],d['T'],d['m']; b=d['beta']
    J=[[Z]*n for _ in range(T+1)]; C=[[Z]*n for _ in range(T+1)]; J[T]=list(d['g'])
    for t in reversed(range(T)):
        for i in range(n):
            J[t][i]=sum((p[t][i][a]*(d['r'][t][i][a]+b*dot(d['P'][t][i][a],J[t+1])) for a in range(m)),Z)
            C[t][i]=sum((p[t][i][a]*(d['k'][t][i][a]+b*dot(d['P'][t][i][a],C[t+1])) for a in range(m)),Z)
    return J,C

def repair(d,w,proposal=None,greedy=False):
    n,T,m=d['n'],d['T'],d['m']; b=d['beta']; bits=w['policy_bits']
    J=[[Z]*n for _ in range(T+1)]; C=[[Z]*n for _ in range(T+1)]; J[T]=list(d['g'])
    p=[[[Z]*m for _ in range(n)] for _ in range(T)]; maxmove=Z; mass=Z; minmargin=None
    for t in reversed(range(T)):
        for i in range(n):
            q=[d['r'][t][i][a]+b*dot(d['P'][t][i][a],J[t+1]) for a in range(m)]
            c=[d['k'][t][i][a]+b*dot(d['P'][t][i][a],C[t+1]) for a in range(m)]
            best=max(range(m),key=lambda a:q[a]); threshold=w['hi'][t][i]-d['epsilon']
            margin=q[best]-threshold; minmargin=margin if minmargin is None else min(minmargin,margin)
            if margin<0: raise ArithmeticError('upper witness does not permit feasible continuation')
            if greedy:
                candidates=[]
                for a in range(m):
                    if q[a]>=threshold:
                        v=[Z]*m; v[a]=O; candidates.append((c[a],v))
                    for aa in range(a):
                        if (q[a]-threshold)*(q[aa]-threshold)<0:
                            z=(threshold-q[aa])/(q[a]-q[aa]); v=[Z]*m; v[a]=z; v[aa]=1-z
                            candidates.append((dot(v,c),v))
                row=min(candidates,key=lambda x:x[0])[1]
            else:
                row=[max(Z,F(x)) for x in proposal[t][i]]
                total=sum(row)
                row=[v/total for v in row] if total else [O if a==best else Z for a in range(m)]
            before=list(row); v=dot(row,q); alpha=Z
            if v<threshold:
                alpha=(threshold-v)/(q[best]-v); row=[(1-alpha)*z for z in row]; row[best]+=alpha
            rounded=[floorq(row[a],bits) if a!=best else Z for a in range(m)]
            rounded[best]=1-sum(rounded)
            assert min(rounded)>=0 and dot(rounded,q)>=threshold
            p[t][i]=rounded; J[t][i]=dot(rounded,q); C[t][i]=dot(rounded,c)
            maxmove=max(maxmove,sum((abs(rounded[a]-before[a]) for a in range(m)),Z)/2); mass+=alpha
    return p,dot(d['nu'],C[0]),dict(max_row_move=maxmove,repair_mass=mass,min_margin=minmargin)

def local_proposal(d,w,initial,seconds):
    n,T,m=d['n'],d['T'],d['m']; dim=n*T*(m-1); b=float(d['beta']); start=time.perf_counter()
    P=np.array(d['P'],float); r=np.array(d['r'],float); k=np.array(d['k'],float); g=np.array(d['g'],float); nu=np.array(d['nu'],float)
    bound=np.array(w['hi'][:-1],float)-float(d['epsilon']); saved=np.array(initial,float)[:,:,:-1].reshape(-1).copy()
    cache={}; simplex=np.zeros((n*T,dim))
    for j in range(n*T): simplex[j,j*(m-1):(j+1)*(m-1)]=-1
    class Budget(Exception): pass
    def calc(z):
        if time.perf_counter()-start>seconds: raise Budget()
        if 'z' in cache and np.array_equal(z,cache['z']): return cache['v']
        p=np.zeros((T,n,m)); p[:,:,:-1]=z.reshape(T,n,m-1); p[:,:,-1]=1-p[:,:,:-1].sum(2)
        J=np.zeros((T+1,n)); C=J.copy(); J[T]=g
        dj=np.zeros((T+1,n,dim)); dc=dj.copy()
        for t in reversed(range(T)):
            qj=r[t]+b*np.einsum('iaj,j->ia',P[t],J[t+1]); qc=k[t]+b*np.einsum('iaj,j->ia',P[t],C[t+1])
            J[t]=np.sum(p[t]*qj,1); C[t]=np.sum(p[t]*qc,1)
            trans=np.einsum('ia,iaj->ij',p[t],P[t]); dj[t]=b*trans@dj[t+1]; dc[t]=b*trans@dc[t+1]
            for i in range(n):
                sl=slice((t*n+i)*(m-1),(t*n+i+1)*(m-1)); dj[t,i,sl]+=qj[i,:-1]-qj[i,-1]; dc[t,i,sl]+=qc[i,:-1]-qc[i,-1]
        ans=(float(nu@C[0]),nu@dc[0],(J[:-1]-bound).reshape(-1),dj[:-1].reshape(n*T,dim))
        cache['z']=z.copy(); cache['v']=ans; return ans
    def cb(z):
        nonlocal saved
        saved=z.copy()
        if time.perf_counter()-start>seconds: raise Budget()
    status='time_budget'; iterations=0
    try:
        res=minimize(lambda z:calc(z)[0],saved,jac=lambda z:calc(z)[1],method='SLSQP',bounds=[(0,1)]*dim,
          constraints=[dict(type='ineq',fun=lambda z:calc(z)[2],jac=lambda z:calc(z)[3]),dict(type='ineq',fun=lambda z:1-z.reshape(n*T,m-1).sum(1),jac=lambda z:simplex)],
          callback=cb,options=dict(maxiter=200,ftol=1e-10,disp=False))
        saved=res.x; status=str(res.message); iterations=int(res.nit)
    except Budget: pass
    p=[]
    for t in range(T):
        rows=[]
        for i in range(n):
            row=[max(Z,dyad(v)) for v in saved.reshape(T,n,m-1)[t,i]]; row.append(max(Z,1-sum(row))); rows.append(row)
        p.append(rows)
    return p,dict(seconds=time.perf_counter()-start,status=status,iterations=iterations)

class Program:
    def __init__(self): self.keys=[]; self.idx={}; self.bounds=[]; self.eq=[]; self.ub=[]; self.obj={}
    def var(self,key,lo,hi):
        assert lo<=hi
        j=len(self.keys); self.keys.append(key); self.idx[key]=j; self.bounds.append((F(lo),F(hi))); return j
    def row(self,row,rhs,eq=False):
        row={j:F(v) for j,v in row.items() if v}; (self.eq if eq else self.ub).append((row,F(rhs)))
    def product(self,p,v,key):
        l,u=self.bounds[p]; a,b=self.bounds[v]; z=self.var(key,min(l*a,l*b,u*a,u*b),max(l*a,l*b,u*a,u*b))
        self.row({z:-1,p:a,v:l},l*a); self.row({z:-1,p:b,v:u},u*b)
        self.row({z:1,p:-a,v:-u},-u*a); self.row({z:1,p:-b,v:-l},-l*b)
        return z

def sparse(rows,n):
    ii=[]; jj=[]; vv=[]
    for i,(row,rhs) in enumerate(rows):
        for j,v in row.items(): ii.append(i); jj.append(j); vv.append(float(v))
    return coo_matrix((vv,(ii,jj)),shape=(len(rows),n)).tocsr(),np.array([float(v) for _,v in rows])

def solve_lp(lp,seconds):
    A,b=sparse(lp.ub,len(lp.keys)); E,f=sparse(lp.eq,len(lp.keys)); c=np.zeros(len(lp.keys))
    for j,v in lp.obj.items(): c[j]=float(v)
    res=linprog(c,A_ub=A,b_ub=b,A_eq=E,b_eq=f,bounds=[(float(l),float(u)) for l,u in lp.bounds],method='highs',options={'time_limit':max(.01,seconds),'dual_feasibility_tolerance':1e-8,'primal_feasibility_tolerance':1e-8})
    good=res.x is not None and res.eqlin.marginals is not None and res.ineqlin.marginals is not None
    y=[dyad(v) for v in res.eqlin.marginals] if good else [Z]*len(lp.eq)
    lam=[max(Z,dyad(-v)) for v in res.ineqlin.marginals] if good else [Z]*len(lp.ub)
    return res,y,lam

def residual(lp,y,lam):
    r=[Z]*len(lp.keys); c=Z
    for j,v in lp.obj.items(): r[j]=v
    for u,(row,rhs) in zip(y,lp.eq):
        c+=u*rhs
        for j,a in row.items(): r[j]-=u*a
    for u,(row,rhs) in zip(lam,lp.ub):
        assert u>=0; c-=u*rhs
        for j,a in row.items(): r[j]+=u*a
    return c+sum((min(z*l,z*u) for z,(l,u) in zip(r,lp.bounds)),Z)

def price_replay(d,w,lam):
    n,T,m=d['n'],d['T'],d['m']; b=d['beta']; e=d['epsilon']; u=[[Z]*n for _ in range(T+1)]
    for t in reversed(range(T)):
        for i in range(n):
            u[t][i]=min(d['k'][t][i][a]+lam[t][i]*(w['dl'][t][i][a]-e)+b*sum((d['P'][t][i][a][j]*(u[t+1][j]+e*min(lam[t][i],lam[t+1][j])) for j in range(n)),Z) for a in range(m))
    return u,dot(d['nu'],[max(Z,v) for v in u[0]])

def prices(d,w,seconds,cap=F(4096)):
    start=time.perf_counter(); n,T,m=d['n'],d['T'],d['m']; b=d['beta']; e=d['epsilon']
    masks=[list(range(n))]+[[i] for i in range(n) if d['nu'][i]>0]
    if n<=4: masks=[ [i for i in range(n) if mask>>i&1] for mask in range(1,1<<n)]
    best=[[Z]*n for _ in range(T+1)]; uu,L=price_replay(d,w,best); tried=[]
    for mask in masks:
        if time.perf_counter()-start>=seconds: break
        lp=Program(); B=(max(v for row in d['k'] for r in row for v in r)+cap*(max(v for row in w['dl'] for r in row for v in r)+e))*T+1
        for t in range(T):
            for i in range(n): lp.var(('u',t,i),-B,B); lp.var(('l',t,i),Z,cap)
        edges={}
        for t in range(T-1):
            for i in range(n):
                for j in range(n):
                    if any(d['P'][t][i][a][j] for a in range(m)):
                        z=lp.var(('z',t,i,j),Z,cap); edges[t,i,j]=z
                        lp.row({z:1,lp.idx['l',t,i]:-1},0); lp.row({z:1,lp.idx['l',t+1,j]:-1},0)
        for t in range(T):
            for i in range(n):
                for a in range(m):
                    row={lp.idx['u',t,i]:O,lp.idx['l',t,i]:e-w['dl'][t][i][a]}
                    if t<T-1:
                        for j,v in enumerate(d['P'][t][i][a]):
                            if v: row[lp.idx['u',t+1,j]]=-b*v; row[edges[t,i,j]]=-b*e*v
                    lp.row(row,d['k'][t][i][a])
        lp.obj={lp.idx['u',0,i]:-d['nu'][i] for i in mask}
        res,_,_=solve_lp(lp,min(2,seconds-(time.perf_counter()-start)))
        if res.x is not None:
            field=[[max(Z,min(cap,dyad(res.x[lp.idx['l',t,i]]))) for i in range(n)] for t in range(T)]+[[Z]*n]
            u,l=price_replay(d,w,field)
            if l>L: best,uu,L=field,u,l
        tried.append(dict(mask=mask,status=int(res.status)))
    return dict(field=best,u=uu,lower=L,seconds=time.perf_counter()-start,masks=tried,cap=cap)

def rectangular(d,w,box):
    n,T,m=d['n'],d['T'],d['m']; b=d['beta']; edge=np.array(box,dtype=object).reshape(T,n,m,2).tolist()
    jmin=[[Z]*n for _ in range(T+1)]; jmax=[[Z]*n for _ in range(T+1)]; cmin=[[Z]*n for _ in range(T+1)]; cmax=[[Z]*n for _ in range(T+1)]
    jmin[T]=list(d['g']); jmax[T]=list(d['g'])
    for t in reversed(range(T)):
        for i in range(n):
            bd=edge[t][i]
            if sum((v[0] for v in bd),Z)>1 or sum((v[1] for v in bd),Z)<1: return dict(infeasible='simplex')
            for arr,stage,ma in [(jmin,d['r'],False),(jmax,d['r'],True),(cmin,d['k'],False),(cmax,d['k'],True)]:
                q=[stage[t][i][a]+b*dot(d['P'][t][i][a],arr[t+1]) for a in range(m)]
                arr[t][i]=row_extreme(q,bd,ma)[0]
            if jmax[t][i]<w['lo'][t][i]-d['epsilon']: return dict(infeasible=True,reason='operating')
    return dict(infeasible=None,jmin=jmin,jmax=jmax,cmin=cmin,cmax=cmax,lower=dot(d['nu'],cmin[0]))

def build(d,w,box,rect,method,price):
    n,T,m=d['n'],d['T'],d['m']; b=d['beta']; e=d['epsilon']; lp=Program()
    for j,(lo,hi) in enumerate(box): lp.var(('p',j//(n*m),(j//m)%n,j%m),lo,hi)
    for t in range(T):
        for i in range(n):
            lo=max(rect['jmin'][t][i],w['lo'][t][i]-e); hi=min(rect['jmax'][t][i],w['hi'][t][i])
            if lo>hi: return None
            if method=='price': lp.var(('R',t,i),w['lo'][t][i]-hi,w['lo'][t][i]-lo)
            else: lp.var(('J',t,i),lo,hi)
            lp.var(('C',t,i),rect['cmin'][t][i],rect['cmax'][t][i])
            pp={lp.idx['p',t,i,a]:O for a in range(m)}; lp.row(pp,1,eq=True)
            lp.row({lp.idx['p',t,i,a]:w['dl'][t][i][a] for a in range(m)},e)
            if method=='price':
                lam=price['field'][t][i]; u=price['u'][t][i]; width=w['hi'][t][i]-w['lo'][t][i]
                lp.row({lp.idx['C',t,i]:-1,lp.idx['R',t,i]:-lam},-u+lam*(width-e))
                lp.row({lp.idx['C',t,i]:-1},-max(Z,u))
    for t in range(T):
        for i in range(n):
            for kind in (['R','C'] if method=='price' else ['J','C']):
                row={lp.idx[kind,t,i]:O}
                if t==T-1:
                    if kind=='R': q=[w['lo'][t][i]-d['r'][t][i][a]-b*dot(d['P'][t][i][a],d['g']) for a in range(m)]
                    elif kind=='J': q=[d['r'][t][i][a]+b*dot(d['P'][t][i][a],d['g']) for a in range(m)]
                    else: q=list(d['k'][t][i])
                    for a in range(m): row[lp.idx['p',t,i,a]]=-q[a]
                elif method=='price':
                    stage=w['d0'][t][i] if kind=='R' else d['k'][t][i]
                    for a in range(m): row[lp.idx['p',t,i,a]]=-stage[a]
                    for j in range(n):
                        if not any(d['P'][t][i][a][j] for a in range(m)): continue
                        v=lp.idx[kind,t+1,j]; identity={v:-O}
                        for a in range(m):
                            z=lp.product(lp.idx['p',t,i,a],v,('w',kind,t,i,a,j)); identity[z]=O
                            if d['P'][t][i][a][j]: row[z]=-b*d['P'][t][i][a][j]
                        lp.row(identity,0,eq=True)
                else:
                    for a in range(m):
                        stage=d['r'][t][i][a] if kind=='J' else d['k'][t][i][a]
                        terms={lp.idx[kind,t+1,j]:b*v for j,v in enumerate(d['P'][t][i][a]) if v}
                        qlo=stage+sum((v*lp.bounds[j][0] for j,v in terms.items()),Z); qhi=stage+sum((v*lp.bounds[j][1] for j,v in terms.items()),Z)
                        q=lp.var(('q',kind,t,i,a),qlo,qhi); lp.row({q:1,**{j:-v for j,v in terms.items()}},stage,eq=True)
                        z=lp.product(lp.idx['p',t,i,a],q,('w',kind,t,i,a)); row[z]=-1
                lp.row(row,0,eq=True)
    lp.obj={lp.idx['C',0,i]:d['nu'][i] for i in range(n)}
    return lp

def run(d,method='price',target=F(1,1000),seconds=30,nodes=255):
    validate(d); start=time.perf_counter(); n,T,m=d['n'],d['T'],d['m']; timings={k:0. for k in ['oracle','greedy','local','price','rectangular','build','lp','residual','repair']}
    w=witness(d,target); timings['oracle']=w['seconds']
    ts=time.perf_counter(); best,U,meta=repair(d,w,greedy=True); timings['greedy']=time.perf_counter()-ts
    initial_U=U
    proposal,localmeta=local_proposal(d,w,best,min(3,seconds/6)); timings['local']=localmeta['seconds']
    ts=time.perf_counter(); p,u,_=repair(d,w,proposal); timings['repair']+=time.perf_counter()-ts
    if u<U: best,U=p,u
    if method=='price': price=prices(d,w,min(5,seconds/5)); timings['price']=price['seconds']
    else:
        zeros=[[Z]*n for _ in range(T+1)]; uu,l=price_replay(d,w,zeros); price=dict(field=zeros,u=uu,lower=Z,seconds=0,masks=[],cap=F(4096))
    root=[(Z,min(O,d['epsilon']/w['dl'][t][i][a]) if w['dl'][t][i][a]>0 else O) for t in range(T) for i in range(n) for a in range(m)]
    tree=[]; active=[]; leaves={}; trace=[]
    def evaluate(box,parent,depth):
        nonlocal U,best
        idx=len(tree); rec=dict(id=idx,parent=parent,depth=depth,box=box); tree.append(rec)
        ts=time.perf_counter(); rect=rectangular(d,w,box); timings['rectangular']+=time.perf_counter()-ts
        if rect['infeasible']: rec.update(kind='infeasible',reason=rect['infeasible']); return idx
        ts=time.perf_counter(); lp=build(d,w,box,rect,method,price); timings['build']+=time.perf_counter()-ts
        if lp is None: rec.update(kind='infeasible',reason='witness_box'); return idx
        remaining=max(.01,min(3,seconds-(time.perf_counter()-start)))
        ts=time.perf_counter(); res,y,lam=solve_lp(lp,remaining); timings['lp']+=time.perf_counter()-ts
        ts=time.perf_counter(); raw=residual(lp,y,lam); lb=max(Z,rect['lower'],raw,price['lower']); timings['residual']+=time.perf_counter()-ts
        if parent is not None: lb=max(lb,tree[parent]['lower'])
        ts=time.perf_counter()
        # A box member is evaluated even when the numerical LP returns no primal.
        corner=[]
        for t in range(T):
            rows=[]
            for i in range(n):
                bd=box[(t*n+i)*m:(t*n+i+1)*m]; rows.append(row_extreme([F(a) for a in range(m)],bd)[1])
            corner.append(rows)
        candidates=[corner]
        if res.x is not None: candidates.append([[[max(Z,dyad(res.x[lp.idx['p',t,i,a]])) for a in range(m)] for i in range(n)] for t in range(T)])
        for proposal in candidates:
            p,u,_=repair(d,w,proposal)
            if u<U: best,U=p,u
        timings['repair']+=time.perf_counter()-ts
        widths=[hi-lo for lo,hi in box]; coord=max(range(len(box)),key=lambda j:widths[j]); reason='widest'
        if depth%4 and res.x is not None:
            scores=[0.]*len(box)
            for key,z in lp.idx.items():
                if key[0]!='w': continue
                _,kind,t,i,a,*tail=key; pidx=lp.idx['p',t,i,a]
                v=lp.idx[kind,t+1,tail[0]] if method=='price' else lp.idx['q',kind,t,i,a]
                scores[pidx]=max(scores[pidx],abs(res.x[z]-res.x[pidx]*res.x[v]))
            eligible=[j for j,z in enumerate(widths) if z>0]
            if eligible and max(scores)>1e-14: coord=max(eligible,key=lambda j:scores[j]); reason='product_defect'
        rec.update(kind='leaf',lower=lb,raw_lower=raw,y=y,multipliers=lam,status=int(res.status),primal_available=res.x is not None,variables=len(lp.keys),coord=coord,branch_rule=reason)
        leaves[idx]=lb; heapq.heappush(active,(lb,idx)); return idx
    evaluate(root,None,0)
    def bounds(): return min([U]+list(leaves.values()))
    def record():
        L=bounds(); trace.append(dict(seconds=time.perf_counter()-start,nodes=len(tree),lower=L,upper=U,gap=U-L))
    record()
    while active and U-bounds()>target and len(tree)+2<=nodes and time.perf_counter()-start<seconds:
        lb,idx=heapq.heappop(active)
        if idx not in leaves: continue
        if lb>=U: continue
        rec=tree[idx]; box=rec['box']; c=rec['coord']; l,h=box[c]
        if l==h: continue
        mid=(l+h)/2; left=list(box); right=list(box); left[c]=(l,mid); right[c]=(mid,h)
        a=evaluate(left,idx,rec['depth']+1); bb=evaluate(right,idx,rec['depth']+1)
        rec['children']=[a,bb]; rec['split']=(c,mid); rec['kind']='split'; del leaves[idx]; record()
    L=bounds(); assert L<=U
    if U-L<=target: stop='target'
    elif len(tree)+2>nodes: stop='node_cap'
    elif time.perf_counter()-start>=seconds: stop='time_cap'
    else: stop='cover_exhausted'
    J,C=policy_value(d,best)
    assert all(J[t][i]>=w['hi'][t][i]-d['epsilon'] for t in range(T) for i in range(n))
    elapsed=time.perf_counter()-start
    return dict(version='r48-1',model=enc(d),method=method,witness=w,prices=price,tree=tree,policy=best,lower=L,upper=U,target=target,initial_upper=initial_U,stop=stop,trace=trace,timings=timings,total_seconds=elapsed,local=localmeta,policy_source='generated in this run from raw primitives and witnesses',exact_operating_value_used=False)

if __name__=='__main__':
    raw=json.loads(Path(sys.argv[1]).read_text()); result=run(load(raw),method=sys.argv[2] if len(sys.argv)>2 else 'price')
    print(json.dumps(enc({k:v for k,v in result.items() if k not in ['tree','policy','model','witness','prices']}),indent=2))
