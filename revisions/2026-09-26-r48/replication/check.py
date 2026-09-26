"""Independent exact reader. Imports neither core nor any optimization library.
The reader reconstructs both mathematical programs, all Bellman inequalities,
the binary cover, and the common deployed policy directly from raw primitives.
"""
from fractions import Fraction as Q
from pathlib import Path
import json,gzip,sys,time,re,hashlib
ZERO=Q(0); ONE=Q(1)
def numbers(v):
    if isinstance(v,str) and re.fullmatch(r'-?\d+(?:/\d+)?',v): return Q(v)
    if isinstance(v,list): return [numbers(x) for x in v]
    if isinstance(v,dict): return {k:numbers(x) for k,x in v.items()}
    return v

def inner(a,b): return sum((x*y for x,y in zip(a,b)),ZERO)
def extremum(q,intervals,maximal):
    if sum((x[0] for x in intervals),ZERO)>1 or sum((x[1] for x in intervals),ZERO)<1: return None
    answer=inner(q,[x[0] for x in intervals]); free=1-sum((x[0] for x in intervals),ZERO)
    for a in sorted(range(len(q)),key=lambda a:q[a],reverse=maximal):
        take=min(free,intervals[a][1]-intervals[a][0]); free-=take; answer+=take*q[a]
    assert free==0
    return answer

def enclosures(model,w,box):
    n,T,m=model['n'],model['T'],model['m']; beta=model['beta']; result={}
    for kind in ['jmin','jmax','cmin','cmax']:
        z=[[ZERO]*n for _ in range(T+1)]; z[-1]=list(model['g']) if kind[0]=='j' else [ZERO]*n
        for t in reversed(range(T)):
            for i in range(n):
                intervals=box[(t*n+i)*m:(t*n+i+1)*m]
                stage=model['r'] if kind[0]=='j' else model['k']
                v=[stage[t][i][a]+beta*inner(model['P'][t][i][a],z[t+1]) for a in range(m)]
                e=extremum(v,intervals,kind.endswith('max'))
                if e is None: return None,'simplex'
                z[t][i]=e
        result[kind]=z
    if any(result['jmax'][t][i]<w['lo'][t][i]-model['epsilon'] for t in range(T) for i in range(n)): return None,'operating'
    result['lower']=inner(model['nu'],result['cmin'][0]); return result,None

class Rows:
    def __init__(self): self.id={}; self.bounds=[]; self.equal=[]; self.ineq=[]; self.cost={}
    def variable(self,key,l,u):
        assert l<=u; j=len(self.bounds); self.id[key]=j; self.bounds.append((Q(l),Q(u))); return j
    def constraint(self,coeff,rhs,equal=False):
        (self.equal if equal else self.ineq).append(({j:Q(v) for j,v in coeff.items() if v},Q(rhs)))
    def multiply(self,p,v,key):
        pl,pu=self.bounds[p]; vl,vu=self.bounds[v]; j=self.variable(key,min(pl*vl,pl*vu,pu*vl,pu*vu),max(pl*vl,pl*vu,pu*vl,pu*vu))
        for row,b in [({j:-1,p:vl,v:pl},pl*vl),({j:-1,p:vu,v:pu},pu*vu),({j:1,p:-vl,v:-pu},-pu*vl),({j:1,p:-vu,v:-pl},-pl*vu)]: self.constraint(row,b)
        return j

def reconstruct(model,w,box,e,kind,price):
    n,T,m=model['n'],model['T'],model['m']; beta=model['beta']; eps=model['epsilon']; mat=Rows()
    for j,(l,u) in enumerate(box): mat.variable(('p',j//(n*m),(j//m)%n,j%m),l,u)
    for t in range(T):
        for i in range(n):
            left=max(e['jmin'][t][i],w['lo'][t][i]-eps); right=min(e['jmax'][t][i],w['hi'][t][i])
            if left>right: return None
            if kind=='price': mat.variable(('R',t,i),w['lo'][t][i]-right,w['lo'][t][i]-left)
            else: mat.variable(('J',t,i),left,right)
            mat.variable(('C',t,i),e['cmin'][t][i],e['cmax'][t][i])
            mat.constraint({mat.id['p',t,i,a]:ONE for a in range(m)},1,True)
            mat.constraint({mat.id['p',t,i,a]:w['dl'][t][i][a] for a in range(m)},eps)
            if kind=='price':
                v=price['field'][t][i]; value=price['u'][t][i]; width=w['hi'][t][i]-w['lo'][t][i]
                mat.constraint({mat.id['C',t,i]:-1,mat.id['R',t,i]:-v},-value+v*(width-eps))
                mat.constraint({mat.id['C',t,i]:-1},-max(ZERO,value))
    for t in range(T):
        for i in range(n):
            for name in (['R','C'] if kind=='price' else ['J','C']):
                row={mat.id[name,t,i]:ONE}
                if t+1==T:
                    for a in range(m):
                        q=model['k'][t][i][a] if name=='C' else model['r'][t][i][a]+beta*inner(model['P'][t][i][a],model['g'])
                        if name=='R': q=w['lo'][t][i]-q
                        row[mat.id['p',t,i,a]]=-q
                elif kind=='price':
                    for a in range(m): row[mat.id['p',t,i,a]]=-(w['d0'][t][i][a] if name=='R' else model['k'][t][i][a])
                    for j in range(n):
                        if not any(model['P'][t][i][a][j] for a in range(m)): continue
                        x=mat.id[name,t+1,j]; conserve={x:-ONE}
                        for a in range(m):
                            v=mat.multiply(mat.id['p',t,i,a],x,('w',name,t,i,a,j)); conserve[v]=ONE
                            if model['P'][t][i][a][j]: row[v]=-beta*model['P'][t][i][a][j]
                        mat.constraint(conserve,0,True)
                else:
                    for a in range(m):
                        v0=model['k'][t][i][a] if name=='C' else model['r'][t][i][a]
                        coeff={mat.id[name,t+1,j]:beta*x for j,x in enumerate(model['P'][t][i][a]) if x}
                        ql=v0+sum((x*mat.bounds[j][0] for j,x in coeff.items()),ZERO); qu=v0+sum((x*mat.bounds[j][1] for j,x in coeff.items()),ZERO)
                        v=mat.variable(('q',name,t,i,a),ql,qu); mat.constraint({v:1,**{j:-x for j,x in coeff.items()}},v0,True)
                        z=mat.multiply(mat.id['p',t,i,a],v,('w',name,t,i,a)); row[z]=-1
                mat.constraint(row,0,True)
    mat.cost={mat.id['C',0,i]:model['nu'][i] for i in range(n)}; return mat

def dual_bound(mat,y,z):
    assert len(y)==len(mat.equal) and len(z)==len(mat.ineq) and min(z,default=ZERO)>=0
    coeff=[ZERO]*len(mat.bounds); rhs=ZERO
    for j,v in mat.cost.items(): coeff[j]=v
    for multiplier,(row,b) in zip(y,mat.equal):
        rhs+=multiplier*b
        for j,v in row.items(): coeff[j]-=multiplier*v
    for multiplier,(row,b) in zip(z,mat.ineq):
        rhs-=multiplier*b
        for j,v in row.items(): coeff[j]+=multiplier*v
    return rhs+sum((min(v*l,v*u) for v,(l,u) in zip(coeff,mat.bounds)),ZERO)

def verify(raw,expected_model=None):
    start=time.perf_counter(); data=numbers(raw); model=data['model']; w=data['witness']; n,T,m=model['n'],model['T'],model['m']; beta=model['beta']; eps=model['epsilon']
    if expected_model is not None: assert raw['model']==expected_model,'primitive identity'
    assert data['version']=='r48-1' and data['method'] in ['direct','price']
    assert 0<beta<1 and eps>0 and sum(model['nu'])==1 and min(model['nu'])>=0
    for t in range(T):
        for i in range(n):
            for a in range(m): assert min(model['P'][t][i][a])>=0 and sum(model['P'][t][i][a])==1 and model['k'][t][i][a]>=0
    for i in range(n): assert w['lo'][T][i]<=model['g'][i]<=w['hi'][T][i]
    for t in reversed(range(T)):
        for i in range(n):
            assert w['lo'][t][i]<=w['hi'][t][i]
            assert w['lo'][t][i]<=max(model['r'][t][i][a]+beta*inner(model['P'][t][i][a],w['lo'][t+1]) for a in range(m))
            assert w['hi'][t][i]>=max(model['r'][t][i][a]+beta*inner(model['P'][t][i][a],w['hi'][t+1]) for a in range(m))
            for a in range(m):
                assert w['dl'][t][i][a]==max(ZERO,w['lo'][t][i]-model['r'][t][i][a]-beta*inner(model['P'][t][i][a],w['hi'][t+1]))
                assert w['d0'][t][i][a]==w['lo'][t][i]-model['r'][t][i][a]-beta*inner(model['P'][t][i][a],w['lo'][t+1])
    p=data['policy']; J=[[ZERO]*n for _ in range(T+1)]; C=[[ZERO]*n for _ in range(T+1)]; J[T]=list(model['g'])
    for t in reversed(range(T)):
        for i in range(n):
            assert min(p[t][i])>=0 and sum(p[t][i])==1
            J[t][i]=sum((p[t][i][a]*(model['r'][t][i][a]+beta*inner(model['P'][t][i][a],J[t+1])) for a in range(m)),ZERO)
            C[t][i]=sum((p[t][i][a]*(model['k'][t][i][a]+beta*inner(model['P'][t][i][a],C[t+1])) for a in range(m)),ZERO)
            assert J[t][i]>=w['hi'][t][i]-eps,'policy feasibility'
    U=inner(model['nu'],C[0]); assert U==data['upper']
    price=data['prices']; field=price['field']; u=[[ZERO]*n for _ in range(T+1)]
    assert len(field)==T+1 and all(x==0 for x in field[-1]) and all(x>=0 for row in field for x in row)
    for t in reversed(range(T)):
        for i in range(n):
            u[t][i]=min(model['k'][t][i][a]+field[t][i]*(w['dl'][t][i][a]-eps)+beta*sum((model['P'][t][i][a][j]*(u[t+1][j]+eps*min(field[t][i],field[t+1][j])) for j in range(n)),ZERO) for a in range(m))
    assert u==price['u']; plower=inner(model['nu'],[max(ZERO,v) for v in u[0]])
    assert price['lower']==(plower if data['method']=='price' else ZERO)
    root=[[ZERO,min(ONE,eps/w['dl'][t][i][a]) if w['dl'][t][i][a]>0 else ONE] for t in range(T) for i in range(n) for a in range(m)]
    tree=data['tree']; seen=set(); leafbounds=[]
    def walk(idx,box,parent,depth,inherited):
        assert 0<=idx<len(tree) and idx not in seen,'cover duplicate/omission'; seen.add(idx); node=tree[idx]
        assert node['id']==idx and node['parent']==parent and node['depth']==depth and node['box']==box,'branch cover'
        assert all(0<=l<=h<=1 for l,h in box)
        rect,reason=enclosures(model,w,box)
        if reason:
            assert node['kind']=='infeasible' and node['reason']==reason; return
        mat=reconstruct(model,w,box,rect,data['method'],price)
        if mat is None:
            assert node['kind']=='infeasible' and node['reason']=='witness_box'; return
        value=dual_bound(mat,node['y'],node['multipliers']); assert value==node['raw_lower']
        lb=max(ZERO,rect['lower'],value,price['lower'],inherited)
        assert node['lower']==lb
        if node['kind']=='leaf': leafbounds.append(lb); return
        assert node['kind']=='split'; c,mid=node['split']; l,h=box[c]; assert l<mid<h
        left=[list(x) for x in box]; right=[list(x) for x in box]; left[c]=[l,mid]; right[c]=[mid,h]
        assert len(node['children'])==2
        walk(node['children'][0],left,idx,depth+1,lb); walk(node['children'][1],right,idx,depth+1,lb)
    walk(0,root,None,0,ZERO); assert seen==set(range(len(tree)))
    L=min([U]+leafbounds); assert L==data['lower'] and 0<=L<=U
    return dict(passed=True,lower=str(L),upper=str(U),gap=str(U-L),target_met=U-L<=data['target'],nodes=len(tree),seconds=time.perf_counter()-start)

if __name__=='__main__':
    path=Path(sys.argv[1]); content=gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes()
    print(json.dumps(verify(json.loads(content)),indent=2))
