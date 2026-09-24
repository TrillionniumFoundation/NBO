# Historical algorithm reconstruction; the retained log records the original failed execution.
"""Whole-cell rational primal/dual certificates for the continuous local LP.
The support floor is ZERO throughout this diagnostic. Global strong duality is
not assumed or inferred. Every accepted open cell passes quadratic sign checks.
"""
from fractions import Fraction as F
from pathlib import Path
import itertools,json,time
import kernel as k
from primary import ROOT,OLD,load,save,dumps
Z,O=F(0),F(1)
PRICES=tuple(map(F,(0,1,4,16,64,256,1024,4096)))
def point_lp(q,z,b):
    primal=[]
    for i in range(3):
        if q[i]>=b:primal.append((z[i],(i,i)))
    for i,j in itertools.permutations(range(3),2):
        if q[i]<b<q[j]:primal.append((((q[j]-b)*z[i]+(b-q[i])*z[j])/(q[j]-q[i]),(i,j)))
    assert primal,'empty LP'
    pv,pair=min(primal)
    prices={Z}
    for i,j in itertools.combinations(range(3),2):
        if q[i]!=q[j]:
            mu=(z[i]-z[j])/(q[i]-q[j])
            if mu>=0:prices.add(mu)
    candidates=[(min(z[i]+mu*(b-q[i]) for i in range(3)),mu) for mu in prices]
    dv=max(x[0] for x in candidates);mu=min(m for v,m in candidates if v==dv)
    assert pv==dv
    return pv,pair,mu

def add(a,b):return a[0]+b[0],a[1]+b[1]
def sub(a,b):return a[0]-b[0],a[1]-b[1]
def sc(a,c):return a[0]*c,a[1]*c
def at(a,x):return a[0]*x+a[1]
def product(a,b):return a[1]*b[1],a[0]*b[1]+a[1]*b[0],a[0]*b[0]
def polymax(c,l,r):
    def val(x):return c[0]+c[1]*x+c[2]*x*x
    vals=[val(l),val(r)]
    if c[2]<0:
        x=-c[1]/(2*c[2])
        if l<x<r:vals.append(val(x))
    return max(vals)
def polyadd(a,b):return tuple(x+y for x,y in zip(a,b))
def polysub(a,b):return tuple(x-y for x,y in zip(a,b))
def cell_check(q,z,b,l,r,pair,mu,tol):
    i,j=pair
    if mu<0:return False
    if i==j:
        if min(at(sub(q[i],b),l),at(sub(q[i],b),r))<0:return False
        numerator=(z[i][1],z[i][0],Z);denom=(Z,O)
    else:
        left=sub(q[j],b);right=sub(b,q[i]);denom=sub(q[j],q[i])
        if min(at(left,l),at(left,r),at(right,l),at(right,r))<0:return False
        if at(denom,(l+r)/2)<=0 or min(at(denom,l),at(denom,r))<0:return False
        numerator=polyadd(product(left,z[i]),product(right,z[j]))
    for a in range(3):
        dual=add(z[a],sc(sub(b,q[a]),mu));dual=add(dual,(Z,tol))
        if polymax(polysub(numerator,product(denom,dual)),l,r)>0:return False
    return True

def solve_cell_lp(qs,zs,bs,tol):
    knots=set(bs.xs)
    for p in qs+zs:knots.update(p.xs)
    coarse=sorted(knots)
    # Align eligibility and denominator sign changes; no sampled feasibility.
    for l,r in zip(coarse,coarse[1:]):
        x=(l+r)/2;ql=[q.line(x) for q in qs];b=bs.line(x)
        expressions=[sub(q,b) for q in ql]+[sub(ql[i],ql[j]) for i,j in itertools.combinations(range(3),2)]
        for m,c in expressions:
            if m and l<-c/m<r:knots.add(-c/m)
    coarse=sorted(knots);accepted=[];stack=[(l,r,0) for l,r in zip(coarse,coarse[1:])]
    while stack:
        l,r,depth=stack.pop();x=(l+r)/2;q=[v.line(x) for v in qs];z=[v.line(x) for v in zs];b=bs.line(x)
        val,pair,mu=point_lp([at(v,x) for v in q],[at(v,x) for v in z],at(b,x))
        if cell_check(q,z,b,l,r,pair,mu,tol):accepted.append((l,r,pair,mu))
        else:
            if depth>=60:raise RuntimeError('Cell refinement cap reached; not a passing certificate')
            stack.extend(((l,x,depth+1),(x,r,depth+1)))
    accepted.sort();xs={Z,O};rows=[];audit=[]
    for l,r,pair,mu in accepted:
        x=(l+r)/2;lines=[add(z.line(x),sc(sub(bs.line(x),q.line(x)),mu)) for q,z in zip(qs,zs)]
        local={l,r}
        for i,j in itertools.combinations(range(3),2):
            m,c=sub(lines[i],lines[j])
            if m and l<-c/m<r:local.add(-c/m)
        local=sorted(local)
        for ll,rr in zip(local,local[1:]):rows.append((ll,rr,min(lines,key=lambda v:at(v,(ll+rr)/2))))
        xs.update(local);audit.append({'left':str(l),'right':str(r),'pair':list(pair),'mu':str(mu),'tolerance':str(tol)})
    rows.sort();xs=sorted(xs)
    assert len(rows)==len(xs)-1 and all(l==x and r==y for (l,r,_),x,y in zip(rows,xs,xs[1:]))
    points=[point_lp([q.at(x) for q in qs],[z.at(x) for z in zs],bs.at(x))[0] for x in xs]
    lower=k.PW(xs,[row[2] for row in rows],points).norm()
    return lower,audit

def grid_recursion(L,U,raw,eps):
    T=len(raw);A=[None]*(T+1);A[T]=k.affine()
    for t in reversed(range(T)):
        qs=k.q_functions(U[t+1]);zs=[k.linear_comb([q,k.intervention(raw[t],a)],[O,O]) for a,q in enumerate(k.q_functions(A[t+1],False))]
        b=k.linear_comb([L[t]],[O],b=-eps)
        terms=[k.affine()]
        for mu in PRICES:
            lines=[k.linear_comb([z,b,q],[O,mu,-mu]) for z,q in zip(zs,qs)]
            mn,_=k.envelope(lines,False);terms.append(mn)
        A[t],_=k.envelope(terms)
    return A

def adaptive(L,U,raw,eps,tol):
    T=len(raw);A=[None]*(T+1);A[T]=k.affine();audit=[]
    for t in reversed(range(T)):
        qs=k.q_functions(U[t+1]);zs=[k.linear_comb([q,k.intervention(raw[t],a)],[O,O]) for a,q in enumerate(k.q_functions(A[t+1],False))]
        b=k.linear_comb([L[t]],[O],b=-eps)
        lower,cert=solve_cell_lp(qs,zs,b,tol);A[t],_=k.envelope([lower,k.affine()])
        audit.append({'t':t,'cells':cert,'q':[p.dump() for p in qs],'z':[p.dump() for p in zs],'b':b.dump(),'lower_before_zero':lower.dump()})
    return A,audit

def verify_cells(audit):
    count=0
    for row in audit:
        qs=list(map(k.PW.load,row['q']));zs=list(map(k.PW.load,row['z']));b=k.PW.load(row['b']);lower=k.PW.load(row['lower_before_zero'])
        end=Z
        for c in sorted(row['cells'],key=lambda c:F(c['left'])):
            l,r=F(c['left']),F(c['right']);assert l==end and l<r;end=r;x=(l+r)/2
            assert cell_check([q.line(x) for q in qs],[z.line(x) for z in zs],b.line(x),l,r,tuple(c['pair']),F(c['mu']),F(c['tolerance']))
            mu=F(c['mu']);local=sorted({l,r}|{u for u in lower.xs if l<u<r})
            for ll,rr in zip(local,local[1:]):
                xx=(ll+rr)/2;stored=lower.line(xx)
                dual=[add(z.line(xx),sc(sub(b.line(xx),q.line(xx)),mu)) for q,z in zip(qs,zs)]
                chosen=min(dual,key=lambda a:at(a,xx))
                assert stored==chosen
                assert all(at(sub(stored,a),ll)<=0 and at(sub(stored,a),rr)<=0 for a in dual)
            count+=1
        assert end==1
        for x in lower.xs:
            val,pair,mu=point_lp([q.at(x) for q in qs],[z.at(x) for z in zs],b.at(x))
            assert lower.at(x)==val
    return count

def run():
    outcomes=[];start=time.perf_counter()
    for eps in (F(1,100),F(1,20)):
        p=next((ROOT/'results/primary').glob('H4_neural31001_epsilon'+str(eps).replace('/','_')+'*'));d=load(p)
        raw=list(map(k.PW.load,d['raw']));V=list(map(k.PW.load,d['V']))
        for witness in ('constructed','exact'):
            L=list(map(k.PW.load,d['L'])) if witness=='constructed' else V
            U=list(map(k.PW.load,d['U'])) if witness=='constructed' else V
            tic=time.perf_counter();G=grid_recursion(L,U,raw,eps);gridtime=time.perf_counter()-tic
            for tol in (F(1,100),F(1,200),F(1,400)):
                tic=time.perf_counter();A,audit=adaptive(L,U,raw,eps,tol);count=verify_cells(audit)
                err=tol*sum(k.BETA**j for j in range(4));lo=A[0].integral();hi=lo+err;grid=G[0].integral()
                assert grid<=hi
                filename='lp_'+witness+'_'+str(eps).replace('/','_')+'_'+str(tol).replace('/','_')+'.json.gz'
                obj={'schema':'NBO-R38-local-LP-v1','support_floor':'0','T':4,'epsilon':str(eps),'tolerance':str(tol),'witness':witness,
                     'L':dumps(L),'U':dumps(U),'raw':dumps(raw),'A':dumps(A),'grid':dumps(G),'cell_certificates':audit,
                     'integrated_lower':str(lo),'integrated_upper':str(hi),'uniform_error_bound':str(err)}
                h=save(ROOT/'results/local_lp'/filename,obj)
                row={'epsilon':str(eps),'witness':witness,'tolerance':str(tol),'support_floor':'0','grid_lower':str(grid),
                     'continuous_local_lower':str(lo),'continuous_local_upper':str(hi),'certified_grid_error_lower':str(max(Z,lo-grid)),
                     'certified_grid_error_upper':str(hi-grid),'whole_cells_verified':count,'seconds':time.perf_counter()-tic,
                     'grid_seconds':gridtime,'max_pieces':max(len(v.ab) for v in A),'proof_file':'local_lp/'+filename,'proof_sha256':h}
                outcomes.append(row);print(witness,eps,tol,float(lo),float(hi),count,flush=True)
    assert len(outcomes)==12
    save(ROOT/'results/local_lp.json',{'cases':12,'outcomes':outcomes,'seconds':time.perf_counter()-start,
        'scope':'Continuous local restart relaxation, zero support floor. Not a global strong-duality certificate and not an additive decomposition of the inherited nonzero-support bound.'})
if __name__=='__main__':run()
