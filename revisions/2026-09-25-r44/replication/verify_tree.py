"""Independent R44 tree checker: Python standard library only.

Reconstructs the original economic Bellman equations, tie-safe support
transforms, aggregated-product rectangles, every node's rational residual,
and the entire binary cover. It does not import a constructor or optimizer.
"""
from fractions import Fraction as Q
from pathlib import Path
import gzip, hashlib, json, sys, time
DEN=2**44
Z=Q(0); O=Q(1)
def fl(v): return Q((v.numerator*DEN)//v.denominator,DEN)
def ce(v): return -fl(-v)
def ip(a,b): return sum((x*y for x,y in zip(a,b)),Z)

class Reader:
    def __init__(self,raw,enhanced):
        self.n=raw['n']; self.T=raw['T']; self.m=raw['m']; self.b=Q(raw['beta']); self.e=Q(raw['epsilon'])
        n,T,m,b,e=self.n,self.T,self.m,self.b,self.e
        assert n>=2 and T>=1 and m>=2 and 0<b<1 and e>0
        self.P=[[[Q(z) for z in row] for row in state] for state in raw['P']]
        self.r=[list(map(Q,row)) for row in raw['r']]; self.k=[list(map(Q,row)) for row in raw['k']]
        self.g=list(map(Q,raw['terminal'])); self.nu=list(map(Q,raw['nu']))
        P,r,k=self.P,self.r,self.k
        assert len(P)==len(r)==len(k)==len(self.g)==len(self.nu)==n and min(self.nu)>=0 and sum(self.nu)==1
        for i in range(n):
            assert len(P[i])==len(r[i])==len(k[i])==m and min(k[i])>=0
            for row in P[i]: assert len(row)==n and min(row)>=0 and sum(row)==1
        self.V=[None]*(T+1); self.H=[None]*(T+1); self.V[T]=self.g; self.H[T]=[Z]*n
        self.a={}; self.d={}; self.s={}
        for t in reversed(range(T)):
            self.V[t]=[]; self.H[t]=[]
            for i in range(n):
                values=[r[i][a]+b*ip(P[i][a],self.V[t+1]) for a in range(m)]
                v=max(values); st=values.index(v); self.a[t,i]=st; self.V[t].append(v)
                h=k[i][st]+b*ip(P[i][st],self.H[t+1]); self.H[t].append(h)
                for a in range(m):
                    self.d[t,i,a]=v-values[a]
                    self.s[t,i,a]=h-k[i][a]-b*ip(P[i][a],self.H[t+1])
        self.coords=[(t,i,a) for t in range(T) for i in range(n) for a in range(m) if a!=self.a[t,i]]
        self.root=[(Z,min(O,e/self.d[key]) if self.d[key]>0 else O) for key in self.coords]
        self.enhanced=enhanced
        self.strict=all(self.d[t,i,a]>0 for t in range(T) for i in range(n) for a in range(m) if a!=self.a[t,i])
        ratios=[self.s[k]/v for k,v in self.d.items() if v>0]
        self.lm=min([Z]+ratios); self.lu=max([Z]+ratios)
        self.envelopes=[]
        lambdas=([Q(0)]+[Q(s)*Q(2)**j for s in [-1,1] for j in [-2,0,2,4,6,8,10,12]]) if enhanced else []
        for lam in lambdas:
            down=[[Z]*n for _ in range(T+1)]; up=[[Z]*n for _ in range(T+1)]
            for t in reversed(range(T)):
                for i in range(n):
                    down[t][i]=fl(min(self.s[t,i,a]-lam*self.d[t,i,a]+b*ip(P[i][a],down[t+1]) for a in range(m)))
                    up[t][i]=ce(max(self.s[t,i,a]-lam*self.d[t,i,a]+b*ip(P[i][a],up[t+1]) for a in range(m)))
            self.envelopes.append((lam,down,up))

    def extremes(self,box):
        n,T,m,b=self.n,self.T,self.m,self.b
        edges=dict(zip(self.coords,box)); tables=[[[Z]*n for _ in range(T+1)] for _ in range(4)]
        for t in reversed(range(T)):
            for i in range(n):
                st=self.a[t,i]; choices=[a for a in range(m) if a!=st]; bounds=[edges[t,i,a] for a in choices]
                used=sum((v[0] for v in bounds),Z)
                if used>1: return None
                for h,table in enumerate(tables):
                    stage=self.d if h<2 else None
                    q=[(stage[t,i,a] if h<2 else self.k[i][a])+b*ip(self.P[i][a],table[t+1]) for a in range(m)]
                    value=q[st]; capacity=O-used
                    deltas=[]
                    for a,(lo,hi) in zip(choices,bounds):
                        value+=lo*(q[a]-q[st]); deltas.append((q[a]-q[st],hi-lo))
                    for coefficient,room in sorted(deltas,reverse=bool(h%2)):
                        if (h%2 and coefficient<=0) or (h%2==0 and coefficient>=0): break
                        change=min(capacity,room); value+=coefficient*change; capacity-=change
                        if not capacity: break
                    table[t][i]=ce(value) if h%2 else fl(value)
                if tables[0][t][i]>self.e: return None
        return tables

    def program(self,box,tab):
        n,T,m,b,e=self.n,self.T,self.m,self.b,self.e
        names={}; bounds=[]; equal=[]; less=[]
        def var(key,lo,hi):
            assert lo<=hi; j=len(bounds); bounds.append((lo,hi)); names[key]=j; return j
        def row(coeff,rhs,eq=False):
            (equal if eq else less).append(({j:Q(c) for j,c in coeff.items() if c},Q(rhs)))
        for key,(lo,hi) in zip(self.coords,box): var(('p',)+key,lo,hi)
        if self.enhanced:
            edges=dict(zip(self.coords,box))
            for t in range(T):
                for i in range(n):
                    bd=[edges[t,i,a] for a in range(m) if a!=self.a[t,i]]
                    var(('pref',t,i),max(Z,O-sum((u for l,u in bd),Z)),O-sum((l for l,u in bd),Z))
        for t in range(T):
            for i in range(n):
                dl=max(Z,tab[0][t][i]); du=min(e,tab[1][t][i]); sl=self.H[t][i]-tab[3][t][i]; su=self.H[t][i]-tab[2][t][i]
                for lam,low,high in self.envelopes:
                    sl=max(sl,low[t][i]+min(lam*dl,lam*du)); su=min(su,high[t][i]+max(lam*dl,lam*du))
                if self.enhanced and self.strict: sl=max(sl,self.lm*du); su=min(su,self.lu*du)
                if dl>du or sl>su: return None
                var(('D',t,i),dl,du); var(('S',t,i),sl,su)
        for t in range(T):
            for i in range(n):
                st=self.a[t,i]; aa=[a for a in range(m) if a!=st]; p={a:names['p',t,i,a] for a in aa}
                row({j:1 for j in p.values()},1)
                if self.enhanced: row({names['pref',t,i]:1,**{j:1 for j in p.values()}},1,True)
                row({p[a]:self.d[t,i,a] for a in aa},e)
                if self.enhanced and self.strict:
                    row({names['S',t,i]:1,names['D',t,i]:-self.lu},0)
                    row({names['S',t,i]:-1,names['D',t,i]:self.lm},0)
                for lam,low,high in self.envelopes:
                    row({names['S',t,i]:1,names['D',t,i]:-lam},high[t][i]); row({names['S',t,i]:-1,names['D',t,i]:lam},-low[t][i])
                for kind,stage in [('D',self.d),('S',self.s)]:
                    equation={names[kind,t,i]:O}; equation.update({p[a]:-stage[t,i,a] for a in aa})
                    if t<T-1:
                        base=self.P[i][st]
                        for j in range(n):
                            if base[j]: equation[names[kind,t+1,j]]=-b*base[j]
                        def product(xx,yy,key):
                            xl,xu=bounds[xx]; yl,yu=bounds[yy]; candidates=[xl*yl,xl*yu,xu*yl,xu*yu]
                            w=var(key,min(candidates),max(candidates))
                            row({w:-1,yy:xl,xx:yl},xl*yl); row({w:-1,yy:xu,xx:yu},xu*yu)
                            row({w:1,yy:-xu,xx:-yl},-xu*yl); row({w:1,yy:-xl,xx:-yu},-xl*yu)
                            return w
                        if self.enhanced:
                            for j in range(n):
                                if not any(self.P[i][a][j]!=base[j] for a in aa): continue
                                v=names[kind,t+1,j]; total={}
                                for a in aa:
                                    w=product(p[a],v,('w',kind,t,i,a,j)); total[w]=O
                                    delta=self.P[i][a][j]-base[j]
                                    if delta: equation[w]=-b*delta
                                wr=product(names['pref',t,i],v,('wr',kind,t,i,j)); total[wr]=O; total[v]=-O
                                row(total,0,True)
                        else:
                            for a in aa:
                                terms={names[kind,t+1,j]:self.P[i][a][j]-base[j] for j in range(n) if self.P[i][a][j]!=base[j]}
                                if not terms: continue
                                yl=sum((min(c*bounds[j][0],c*bounds[j][1]) for j,c in terms.items()),Z)
                                yu=sum((max(c*bounds[j][0],c*bounds[j][1]) for j,c in terms.items()),Z)
                                yy=var(('q',kind,t,i,a),yl,yu); row({yy:1,**{j:-c for j,c in terms.items()}},0,True)
                                w=product(p[a],yy,('w',kind,t,i,a)); equation[w]=-b
                    row(equation,0,True)
        obj={names['S',0,i]:-self.nu[i] for i in range(n)}
        return names,bounds,equal,less,obj

    def bound(self,rec,box,inherited=None):
        tab=self.extremes(box)
        if tab is None:
            assert rec['kind']=='infeasible'; return None
        lp=self.program(box,tab)
        if lp is None:
            assert rec['kind']=='envelope_infeasible'; return None
        assert rec['kind'] in ['leaf','split']
        names,bounds,equal,less,obj=lp
        y=list(map(Q,rec['eq_dual'])); lam=list(map(Q,rec['ineq_dual']))
        assert len(y)==len(equal) and len(lam)==len(less) and min(lam,default=Z)>=0
        lower=[Z]*len(bounds); upper=[Z]*len(bounds); constant=Z
        for j,c in obj.items(): lower[j]=upper[j]=c
        for multiplier,(coeff,rhs) in zip(y,equal):
            constant+=fl(multiplier*rhs)
            for j,c in coeff.items(): lower[j]+=fl(-multiplier*c); upper[j]+=ce(-multiplier*c)
        for multiplier,(coeff,rhs) in zip(lam,less):
            constant+=fl(-multiplier*rhs)
            for j,c in coeff.items(): lower[j]+=fl(multiplier*c); upper[j]+=ce(multiplier*c)
        ans=ip(self.nu,self.H[0])+constant
        for cl,cu,(lo,hi) in zip(lower,upper,bounds): ans+=fl(min(cl*lo,cl*hi,cu*lo,cu*hi))
        ans=max(Z,ans,ip(self.nu,tab[2][0]))
        if inherited is not None: ans=max(ans,inherited)
        assert Q(rec['lower'])==ans,(rec['id'],'lower')
        assert rec['variables']==len(bounds)
        return ans

    def policy(self,raw):
        n,T,m,b=self.n,self.T,self.m,self.b
        assert len(raw)==T; J=self.g; C=[Z]*n; maximum=Z
        for t in reversed(range(T)):
            assert len(raw[t])==n; nj=[]; nc=[]
            for i in range(n):
                p=list(map(Q,raw[t][i])); assert len(p)==m and min(p)>=0 and sum(p)==1
                j=ip(p,[self.r[i][a]+b*ip(self.P[i][a],J) for a in range(m)])
                c=ip(p,[self.k[i][a]+b*ip(self.P[i][a],C) for a in range(m)])
                loss=self.V[t][i]-j; assert 0<=loss<=self.e,(t,i,'operating constraint')
                maximum=max(maximum,loss); nj.append(j); nc.append(c)
            J,C=nj,nc
        return ip(self.nu,C),maximum

def verify(path,expected_model=None):
    started=time.perf_counter(); data=Path(path).read_bytes(); o=json.loads(gzip.decompress(data))
    assert o['schema']=='nbo-r44-tree-v1' and isinstance(o['enhanced'],bool)
    if expected_model is not None:
        assert o['model']==json.loads(Path(expected_model).read_text()),'frozen model identity'
    model=Reader(o['model'],o['enhanced']); U,maximum=model.policy(o['policy']); assert U==Q(o['upper'])
    tree=o['tree']; assert tree and tree[0]['parent'] is None
    pending=[(0,model.root,None,0)]; seen=set(); lbs=[]; nodes=0; infeasible=0
    while pending:
        idx,box,parent,depth=pending.pop(); assert 0<=idx<len(tree) and idx not in seen; seen.add(idx)
        rec=tree[idx]; assert rec['id']==idx and rec['parent']==parent and rec['depth']==depth
        assert [tuple(map(Q,z)) for z in rec['box']]==box
        value=model.bound(rec,box,Q(tree[parent]['lower']) if parent is not None else None); nodes+=1
        if rec['kind']=='split':
            assert value is not None; j=rec['coordinate']; cut=Q(rec['cut']); assert 0<=j<len(box)
            lo,hi=box[j]; assert lo<cut<hi; c=rec['children']; assert len(c)==2 and c[0]!=c[1]
            left=box[:]; right=box[:]; left[j]=(lo,cut); right[j]=(cut,hi)
            pending.extend([(c[0],left,idx,depth+1),(c[1],right,idx,depth+1)])
        elif value is not None: lbs.append(value)
        else: infeasible+=1
    assert seen==set(range(len(tree))),'unreachable or omitted node'
    L=min([U]+lbs); assert L==Q(o['lower']) and L<=U
    met=U-L<=Q(o['target']); assert bool(o['summary']['target_met'])==met
    return dict(passed=True,proof_sha256=hashlib.sha256(data).hexdigest(),lower=str(L),upper=str(U),gap=float(U-L),relative_gap=float((U-L)/U) if U else 0,target_met=met,nodes_checked=nodes,terminal_leaves=len(lbs),infeasible_leaves=infeasible,all_restart_checks=model.T*model.n,max_regret=str(maximum),seconds=time.perf_counter()-started)

if __name__=='__main__': print(json.dumps(verify(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else None),indent=2))
