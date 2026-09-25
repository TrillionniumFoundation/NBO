"""R44 complete common-Markov search. Numerical LP output is only a proposal.

The exact contract uses rational Bellman equations. All LP multipliers are
rounded to a dyadic grid and their residual is enclosed outwards. The final
certificate contains a covering binary tree, every leaf bound, and one common
feasible policy. No LP infeasibility status is used to discard a region.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import importlib.util, sys, time, heapq, json, gzip, hashlib, resource
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from local_proposal import improve
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('r43_constructor',ROOT/'revisions/2026-09-25-r43/replication/regret.py')
old=importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
ZERO=F(0); ONE=F(1); GRID=2**44
enc=old.enc; dot=old.dot; Program=old.Program

def floorq(x): return F((x.numerator*GRID)//x.denominator,GRID)
def ceilq(x): return -floorq(-x)
def quantize(x): return F(round(float(x)*GRID),GRID)

def prepare(d,enhanced=True):
    ref=old.reference(d); V,H,star,loss,gain,*_=ref
    n,T,m=d['n'],d['T'],d['m']; b=d['beta']; eps=d['epsilon']
    # All support prices are fixed independently of the proposal; no division
    # by an action disadvantage is involved in the Bellman envelopes.
    prices=[F(0)] + [F(s)*F(2)**j for s in [-1,1] for j in [-2,0,2,4,6,8,10,12]] if enhanced else []
    env=[]
    for lam in prices:
        lo=[[ZERO]*n for _ in range(T+1)]; hi=[[ZERO]*n for _ in range(T+1)]
        for t in reversed(range(T)):
            for i in range(n):
                lo[t][i]=floorq(min(gain[t][i][a]-lam*loss[t][i][a]+b*dot(d['P'][i][a],lo[t+1]) for a in range(m)))
                hi[t][i]=ceilq(max(gain[t][i][a]-lam*loss[t][i][a]+b*dot(d['P'][i][a],hi[t+1]) for a in range(m)))
        env.append((lam,lo,hi))
    coords=[]; bounds=[]
    for t in range(T):
        for i in range(n):
            for a in range(m):
                if a!=star[t][i]:
                    coords.append((t,i,a)); bounds.append((ZERO,min(ONE,eps/loss[t][i][a]) if loss[t][i][a]>0 else ONE))
    return dict(ref=ref,env=env,coords=coords,root=bounds,enhanced=enhanced)

def linear_extreme(q0,qs,bounds,maximize=False):
    """Extreme on {l<=p<=u, sum p<=1}; the reference has remaining mass."""
    amount=sum((l for l,u in bounds),ZERO)
    if amount>1: return None
    value=q0+sum((l*(q-q0) for q,(l,u) in zip(qs,bounds)),ZERO)
    left=ONE-amount
    order=sorted(range(len(qs)),key=lambda j:qs[j]-q0,reverse=maximize)
    for j in order:
        c=qs[j]-q0
        if (maximize and c<=0) or (not maximize and c>=0): break
        use=min(left,bounds[j][1]-bounds[j][0]); value+=use*c; left-=use
        if left==0: break
    return value

def rectangular(d,cache,box):
    n,T,m=d['n'],d['T'],d['m']; b=d['beta']; V,H,star,loss,gain,*_=cache['ref']
    at={key:z for key,z in zip(cache['coords'],box)}
    dlo=[[ZERO]*n for _ in range(T+1)]; dhi=[[ZERO]*n for _ in range(T+1)]
    clo=[[ZERO]*n for _ in range(T+1)]; chi=[[ZERO]*n for _ in range(T+1)]
    for t in reversed(range(T)):
        for i in range(n):
            st=star[t][i]; acts=[a for a in range(m) if a!=st]; bs=[at[t,i,a] for a in acts]
            if sum((l for l,u in bs),ZERO)>1: return dict(infeasible=True,reason='simplex')
            for out,stage,nxt,maximize,rounder in [(dlo,loss[t][i],dlo,False,floorq),(dhi,loss[t][i],dhi,True,ceilq),(clo,d['k'][i],clo,False,floorq),(chi,d['k'][i],chi,True,ceilq)]:
                q=[stage[a]+b*dot(d['P'][i][a],nxt[t+1]) for a in range(m)]
                out[t][i]=rounder(linear_extreme(q[st],[q[a] for a in acts],bs,maximize))
            if dlo[t][i]>d['epsilon']: return dict(infeasible=True,reason='operating')
    return dict(infeasible=False,dlo=dlo,dhi=dhi,clo=clo,chi=chi,lower=dot(d['nu'],clo[0]))

def build(d,cache,box,rect):
    n,T,m=d['n'],d['T'],d['m']; b=d['beta']; eps=d['epsilon']
    V,H,star,loss,gain,*_=cache['ref']; lp=Program()
    for key,(lo,hi) in zip(cache['coords'],box): lp.var(('p',)+key,lo,hi)
    if cache['enhanced']:
        edges=dict(zip(cache['coords'],box))
        for t in range(T):
            for i in range(n):
                bds=[edges[t,i,a] for a in range(m) if a!=star[t][i]]
                lp.var(('pref',t,i),max(ZERO,ONE-sum((u for l,u in bds),ZERO)),ONE-sum((l for l,u in bds),ZERO))
    for t in range(T):
        for i in range(n):
            dl=max(ZERO,rect['dlo'][t][i]); du=min(eps,rect['dhi'][t][i])
            sl=H[t][i]-rect['chi'][t][i]; su=H[t][i]-rect['clo'][t][i]
            for lam,lo,hi in cache['env']:
                sl=max(sl,lo[t][i]+min(lam*dl,lam*du))
                su=min(su,hi[t][i]+max(lam*dl,lam*du))
            # An empty implied interval is a rational infeasibility certificate.
            if cache['enhanced'] and cache['ref'][-1]:
                sl=max(sl,cache['ref'][-3]*du); su=min(su,cache['ref'][-2]*du)
            if dl>du or sl>su: return None
            lp.var(('D',t,i),dl,du); lp.var(('S',t,i),sl,su)
    for t in range(T):
        for i in range(n):
            st=star[t][i]; acts=[a for a in range(m) if a!=st]
            pp={a:lp.idx[('p',t,i,a)] for a in acts}
            lp.row({p:1 for p in pp.values()},1)
            if cache['enhanced']: lp.row({lp.idx[('pref',t,i)]:1,**{p:1 for p in pp.values()}},1,eq=True)
            lp.row({pp[a]:loss[t][i][a] for a in acts},eps)
            if cache['enhanced'] and cache['ref'][-1]:
                lm,lu=cache['ref'][-3:-1]
                lp.row({lp.idx[('S',t,i)]:1,lp.idx[('D',t,i)]:-lu},0)
                lp.row({lp.idx[('S',t,i)]:-1,lp.idx[('D',t,i)]:lm},0)
            for lam,lo,hi in cache['env']:
                lp.row({lp.idx[('S',t,i)]:1,lp.idx[('D',t,i)]:-lam},hi[t][i])
                lp.row({lp.idx[('S',t,i)]:-1,lp.idx[('D',t,i)]:lam},-lo[t][i])
            for kind,stage in [('D',loss),('S',gain)]:
                row={lp.idx[(kind,t,i)]:ONE}
                for a in acts: row[pp[a]]=-stage[t][i][a]
                if t<T-1:
                    p0=d['P'][i][st]
                    for j in range(n):
                        if p0[j]: row[lp.idx[(kind,t+1,j)]]=-b*p0[j]
                    if cache['enhanced']:
                        for j in range(n):
                            if not any(d['P'][i][a][j]!=p0[j] for a in acts): continue
                            v=lp.idx[(kind,t+1,j)]; products={}
                            for a in acts:
                                w=lp.product(pp[a],v,('w',kind,t,i,a,j)); products[w]=ONE
                                delta=d['P'][i][a][j]-p0[j]
                                if delta: row[w]=-b*delta
                            wr=lp.product(lp.idx[('pref',t,i)],v,('wr',kind,t,i,j)); products[wr]=ONE
                            products[v]=-ONE; lp.row(products,0,eq=True)
                    else:
                        for a in acts:
                            terms={lp.idx[(kind,t+1,j)]:d['P'][i][a][j]-p0[j] for j in range(n) if d['P'][i][a][j]!=p0[j]}
                            if not terms: continue
                            qlo=sum((min(c*lp.bounds[j][0],c*lp.bounds[j][1]) for j,c in terms.items()),ZERO)
                            qhi=sum((max(c*lp.bounds[j][0],c*lp.bounds[j][1]) for j,c in terms.items()),ZERO)
                            q=lp.var(('q',kind,t,i,a),qlo,qhi)
                            lp.row({q:ONE,**{j:-c for j,c in terms.items()}},0,eq=True)
                            w=lp.product(pp[a],q,('w',kind,t,i,a))
                            row[w]=-b
                lp.row(row,0,eq=True)
    lp.obj={lp.idx[('S',0,i)]:-d['nu'][i] for i in range(n)}
    return lp

def lower_residual(lp,y,lam):
    lo=[ZERO]*len(lp.keys); hi=[ZERO]*len(lp.keys); cst=ZERO
    for j,v in lp.obj.items(): lo[j]=hi[j]=v
    for u,(row,rhs) in zip(y,lp.eq):
        cst+=floorq(u*rhs)
        for j,c in row.items(): lo[j]+=floorq(-u*c); hi[j]+=ceilq(-u*c)
    for u,(row,rhs) in zip(lam,lp.ub):
        cst+=floorq(-u*rhs)
        for j,c in row.items(): lo[j]+=floorq(u*c); hi[j]+=ceilq(u*c)
    return cst+sum((floorq(min(cl*l,cl*u,cu*l,cu*u)) for cl,cu,(l,u) in zip(lo,hi,lp.bounds)),ZERO)

def propose(lp,seconds):
    def sparse(rows):
        ii=[]; jj=[]; vv=[]
        for i,(row,rhs) in enumerate(rows):
            for j,v in row.items(): ii.append(i); jj.append(j); vv.append(float(v))
        return coo_matrix((vv,(ii,jj)),shape=(len(rows),len(lp.keys))).tocsr(),np.array([float(rhs) for row,rhs in rows])
    a,b=sparse(lp.ub); e,f=sparse(lp.eq); c=np.zeros(len(lp.keys))
    for j,v in lp.obj.items(): c[j]=float(v)
    res=linprog(c,A_ub=a,b_ub=b,A_eq=e,b_eq=f,bounds=[(float(l),float(u)) for l,u in lp.bounds],method='highs',options={'time_limit':max(.01,seconds),'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
    good=res.x is not None and res.eqlin.marginals is not None
    y=[quantize(x) for x in res.eqlin.marginals] if good else [ZERO]*len(lp.eq)
    lam=[max(ZERO,quantize(-x)) for x in res.ineqlin.marginals] if good else [ZERO]*len(lp.ub)
    return res,y,lam

def search(d,enhanced=True,seconds=120,nodes=2047,target=F(1,1000),node_seconds=15,progress=None):
    start=time.perf_counter(); cache=prepare(d,enhanced); prep=time.perf_counter()-start
    initial=[[[ZERO]*d['m'] for _ in range(d['n'])] for _ in range(d['T'])]
    policy,U,*_=old.repair(d,initial,cache['ref']); bestpolicy=policy
    tree=[]; active=[]; leaves={}; trace=[]; nlp=0; lpseconds=0.; rootgap=None
    def evaluate(box,parent,depth):
        nonlocal U,bestpolicy,nlp,lpseconds,rootgap
        idx=len(tree); rec=dict(id=idx,parent=parent,depth=depth,box=[[str(l),str(u)] for l,u in box]); tree.append(rec)
        rect=rectangular(d,cache,box)
        if rect['infeasible']:
            rec.update(kind='infeasible',reason=rect['reason']); return
        lp=build(d,cache,box,rect)
        if lp is None:
            rec.update(kind='envelope_infeasible'); return
        ts=time.perf_counter(); remaining=max(.01,min(node_seconds,seconds-(time.perf_counter()-start)))
        res,y,lam=propose(lp,remaining); lpseconds+=time.perf_counter()-ts; nlp+=1
        lb=max(ZERO,rect['lower'],dot(d['nu'],cache['ref'][1][0])+lower_residual(lp,y,lam))
        if parent is not None: lb=max(lb,F(tree[parent]['lower']))
        proposal=[[[ZERO]*d['m'] for _ in range(d['n'])] for _ in range(d['T'])]
        if res.x is not None:
            for key in cache['coords']: proposal[key[0]][key[1]][key[2]]=max(ZERO,quantize(res.x[lp.idx[('p',)+key]]))
        else:
            for key,(lo,hi) in zip(cache['coords'],box): proposal[key[0]][key[1]][key[2]]=(lo+hi)/2
        candidate,cu,*_=old.repair(d,proposal,cache['ref'])
        if cu<U: U=cu; bestpolicy=candidate
        if idx==0 and time.perf_counter()-start<seconds-1:
            local,local_meta=improve(d,cache,candidate,seconds=min(5,max(.1,seconds-(time.perf_counter()-start))))
            local=[[ [quantize(x) for x in row] for row in period] for period in local]
            local_policy,local_cost,*_=old.repair(d,local,cache['ref'])
            rec['local_proposal']=local_meta
            if local_cost<U: U=local_cost; bestpolicy=local_policy
        # A deterministic lower corner is always in every nonempty simplex box.
        # Evaluating it makes completeness independent of the LP proposal.
        corner=[[[ZERO]*d['m'] for _ in range(d['n'])] for _ in range(d['T'])]
        for key,(lo,hi) in zip(cache['coords'],box): corner[key[0]][key[1]][key[2]]=lo
        corner_policy,corner_cost,*_=old.repair(d,corner,cache['ref'])
        if corner_cost<U: U=corner_cost; bestpolicy=corner_policy
        widths=[hi-lo for lo,hi in box]
        # Every eighth level uses a widest coordinate: continued refinement
        # cannot permanently ignore a probability coordinate.
        if depth%8==0 or res.x is None:
            coord=max(range(len(widths)),key=lambda j:widths[j])
        else:
            score={key:0. for key in cache['coords']}
            for key,j in lp.idx.items():
                if key[0]=='w':
                    _,kind,t,i,a=key[:5]
                    pv=res.x[lp.idx[('p',t,i,a)]]
                    qv=res.x[lp.idx[(kind,t+1,key[5])]] if len(key)==6 else res.x[lp.idx[('q',kind,t,i,a)]]
                    scale=float(d['epsilon']) if kind=='D' else max(1.,float(U))
                    score[t,i,a]+=abs(res.x[j]-pv*qv)/max(scale,1e-12)
            coord=max(range(len(widths)),key=lambda j:(score[cache['coords'][j]],float(widths[j])))
            if widths[coord]==0: coord=max(range(len(widths)),key=lambda j:widths[j])
        rec.update(kind='leaf',lower=str(lb),eq_dual=[str(x) for x in y],ineq_dual=[str(x) for x in lam],lp_status=int(res.status),primal_available=res.x is not None,dual_available=res.eqlin.marginals is not None,variables=len(lp.keys),branch_coordinate=coord)
        leaves[idx]=lb
        if lb<U-target and widths[coord]>0: heapq.heappush(active,(lb,idx))
        if idx==0: rootgap=float(U-lb)
    evaluate(cache['root'],None,0)
    def lower(): return min([U]+list(leaves.values()))
    def log():
        l=lower(); row=dict(nodes=len(tree),lp_nodes=nlp,seconds=time.perf_counter()-start,lower=float(l),upper=float(U),gap=float(U-l),live=len(active))
        trace.append(row)
        if progress: progress(row)
    log()
    while active and U-lower()>target and len(tree)+2<=nodes and time.perf_counter()-start<seconds:
        lb,idx=heapq.heappop(active)
        if lb>=U-target: continue
        rec=tree[idx]; box=[tuple(map(F,b)) for b in rec['box']]; j=rec['branch_coordinate']; lo,hi=box[j]; mid=(lo+hi)/2
        rec['kind']='split'; rec['coordinate']=j; rec['cut']=str(mid); rec['children']=[len(tree),len(tree)+1]
        del leaves[idx]
        left=box[:]; right=box[:]; left[j]=(lo,mid); right[j]=(mid,hi)
        evaluate(left,idx,rec['depth']+1); evaluate(right,idx,rec['depth']+1)
        if len(tree)<32 or len(tree)%16==1: log()
    log(); L=lower(); assert L<=U
    stop='target' if U-L<=target else ('time_cap' if time.perf_counter()-start>=seconds else ('node_cap' if len(tree)+2>nodes else 'exhausted'))
    record=dict(schema='nbo-r44-tree-v1',model=d,enhanced=enhanced,target=target,lower=L,upper=U,policy=bestpolicy,tree=tree,trace=trace,
        summary=dict(stop=stop,target_met=U-L<=target,nodes=len(tree),lp_nodes=nlp,root_gap=rootgap,gap=float(U-L),relative_gap=float((U-L)/U) if U else 0,seconds=time.perf_counter()-start,prepare_seconds=prep,lp_seconds=lpseconds,maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
    return record

def save(obj,path):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    raw=json.dumps(obj,default=enc,separators=(',',':')).encode()
    path.write_bytes(gzip.compress(raw,mtime=0))
    return hashlib.sha256(raw).hexdigest()

if __name__=='__main__':
    d=old.model(430001,3,4,3,'19/20','1/100')
    o=search(d,seconds=30,nodes=255,progress=lambda r:print(r,flush=True))
    save(o,ROOT/'revisions/2026-09-25-r44/proofs/development.json.gz')
    print(json.dumps(o['summary'],indent=2))
