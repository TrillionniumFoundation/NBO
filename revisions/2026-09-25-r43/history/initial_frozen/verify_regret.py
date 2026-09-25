"""Independent R43 certificate reader: standard library only.
No import of the constructor, optimizer, NumPy, or SciPy. The reader rebuilds
all Bellman coefficients, probability caps, savings cones and product envelopes.
Publication endpoints must equal the independently recomputed rational values.
"""
from fractions import Fraction as Q
import gzip, hashlib, json, sys, time
from pathlib import Path

DEN=2**40
def floorq(x): return Q((x.numerator*DEN)//x.denominator,DEN)
def inner(x,y): return sum((a*b for a,b in zip(x,y)),Q(0))

def verify(path):
    begin=time.perf_counter(); raw=Path(path).read_bytes(); o=json.loads(gzip.decompress(raw)); a=o['model']
    assert o['schema']=='nbo-r43-regret-v1'
    n,h,m=a['n'],a['T'],a['m']; beta=Q(a['beta']); eps=Q(a['epsilon'])
    assert n>=2 and h>=1 and m>=2 and 0<beta<1 and eps>0
    ptrans=[[[Q(v) for v in row] for row in state] for state in a['P']]
    rew=[[Q(v) for v in row] for row in a['r']]; cost=[[Q(v) for v in row] for row in a['k']]
    terminal=list(map(Q,a['terminal'])); initial=list(map(Q,a['nu']))
    assert len(ptrans)==len(rew)==len(cost)==len(terminal)==len(initial)==n
    assert sum(initial)==1 and min(initial)>=0
    for i in range(n):
        assert len(ptrans[i])==len(rew[i])==len(cost[i])==m and min(cost[i])>=0
        for row in ptrans[i]: assert len(row)==n and sum(row)==1 and min(row)>=0
    val=[None]*(h+1); val[h]=terminal; refcost=[None]*(h+1); refcost[h]=[Q(0)]*n
    opt={}; d={}; g={}
    for t in reversed(range(h)):
        val[t]=[]; refcost[t]=[]
        for i in range(n):
            av=[rew[i][b]+beta*inner(ptrans[i][b],val[t+1]) for b in range(m)]
            best=max(av); b0=av.index(best); opt[t,i]=b0; val[t].append(best)
            z=cost[i][b0]+beta*inner(ptrans[i][b0],refcost[t+1]); refcost[t].append(z)
            for b in range(m):
                d[t,i,b]=best-av[b]
                g[t,i,b]=z-cost[i][b]-beta*inner(ptrans[i][b],refcost[t+1])
    strict=all(d[t,i,b]>0 for t in range(h) for i in range(n) for b in range(m) if b!=opt[t,i])
    ratios=[g[key]/dd for key,dd in d.items() if dd>0]
    neg=min([Q(0)]+ratios); pos=max([Q(0)]+ratios)
    scaled=o['mode']=='scaled' and strict
    assert o['mode'] in ('scaled','unscaled')
    names={}; boxes=[]; equal=[]; less=[]
    def new(name,lo,hi):
        assert lo<=hi; j=len(boxes); boxes.append((lo,hi)); names[name]=j; return j
    def constraint(row,rhs,eq=False):
        (equal if eq else less).append(({i:Q(x) for i,x in row.items() if x},Q(rhs)))
    for t in range(h):
        for i in range(n):
            for b in range(m):
                if b!=opt[t,i]: new(('p',t,i,b),Q(0),min(Q(1),eps/d[t,i,b]) if d[t,i,b]>0 else Q(1))
    maxcost=max(x for row in cost for x in row)
    for t in range(h):
        budget=maxcost*sum((beta**j for j in range(h-t)),Q(0))
        for i in range(n):
            new(('D',t,i),Q(0),eps)
            lo,hi=refcost[t][i]-budget,refcost[t][i]
            if scaled: lo=max(lo,neg*eps); hi=min(hi,pos*eps)
            new(('S',t,i),lo,hi)
    for t in range(h):
        for i in range(n):
            choices=[b for b in range(m) if b!=opt[t,i]]
            x={b:names['p',t,i,b] for b in choices}
            constraint({v:1 for v in x.values()},1)
            constraint({x[b]:d[t,i,b] for b in choices},eps)
            if scaled:
                constraint({names['S',t,i]:1,names['D',t,i]:-pos},0)
                constraint({names['S',t,i]:-1,names['D',t,i]:neg},0)
            for kind in ('D','S'):
                stage=d if kind=='D' else g
                equation={names[kind,t,i]:Q(1)}
                equation.update({x[b]:-stage[t,i,b] for b in choices})
                if t+1<h:
                    base=ptrans[i][opt[t,i]]
                    for j,prob in enumerate(base):
                        if prob: equation[names[kind,t+1,j]]=-beta*prob
                    for b in choices:
                        for j in range(n):
                            change=ptrans[i][b][j]-base[j]
                            if not change: continue
                            xx=x[b]; yy=names[kind,t+1,j]; lx,ux=boxes[xx]; ly,uy=boxes[yy]
                            products=[lx*ly,lx*uy,ux*ly,ux*uy]
                            w=new(('w',kind,t,i,b,j),min(products),max(products))
                            # Four rectangle facets, with the exact shared-continuation coordinates.
                            constraint({w:-1,yy:lx,xx:ly},lx*ly)
                            constraint({w:-1,yy:ux,xx:uy},ux*uy)
                            constraint({w:1,yy:-ux,xx:-ly},-ux*ly)
                            constraint({w:1,yy:-lx,xx:-uy},-lx*uy)
                            equation[w]=-beta*change
                constraint(equation,0,True)
    y=list(map(Q,o['y'])); multipliers=list(map(Q,o['lambda_nonnegative']))
    assert len(y)==len(equal) and len(multipliers)==len(less) and min(multipliers,default=0)>=0
    reduced=[Q(0)]*len(boxes); constant=Q(0)
    for i in range(n): reduced[names['S',0,i]]-=initial[i]
    for yy,(row,rhs) in zip(y,equal):
        constant+=yy*rhs
        for j,v in row.items(): reduced[j]-=yy*v
    for zz,(row,rhs) in zip(multipliers,less):
        constant-=zz*rhs
        for j,v in row.items(): reduced[j]+=zz*v
    lb=inner(initial,refcost[0])+floorq(constant)
    for c,(lo,hi) in zip(reduced,boxes): lb+=floorq(min(c*lo,c*hi))
    lb=max(Q(0),lb)
    # Check the deployed probabilities through the original J,C equations,
    # not through the relaxation or the constructor's repair implementation.
    policy=[[[Q(v) for v in row] for row in t] for t in o['policy']]
    assert len(policy)==h
    J=terminal; C=[Q(0)]*n; maximum=Q(0); checked=0
    for t in reversed(range(h)):
        assert len(policy[t])==n
        nxtJ=[]; nxtC=[]
        for i in range(n):
            row=policy[t][i]; assert len(row)==m and min(row)>=0 and sum(row)==1
            j=inner(row,[rew[i][b]+beta*inner(ptrans[i][b],J) for b in range(m)])
            c=inner(row,[cost[i][b]+beta*inner(ptrans[i][b],C) for b in range(m)])
            regret=val[t][i]-j; assert 0<=regret<=eps,(t,i,str(regret-eps))
            maximum=max(maximum,regret); nxtJ.append(j); nxtC.append(c); checked+=1
        J=nxtJ; C=nxtC
    ub=inner(initial,C)
    assert Q(o['lower'])==lb and Q(o['upper'])==ub and lb<=ub
    return dict(passed=True,sha256=hashlib.sha256(raw).hexdigest(),lower=str(lb),upper=str(ub),gap=float(ub-lb),relative_gap=float((ub-lb)/ub) if ub else 0.0,all_restart_checks=checked,lp_variables=len(boxes),lp_inequalities=len(less),lp_equalities=len(equal),max_regret=str(maximum),seconds=time.perf_counter()-begin,strict_gap=strict)

if __name__=='__main__':
    print(json.dumps(verify(sys.argv[1]),indent=2))
