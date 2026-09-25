"""Independent exact finite property tests for the new multi-action bound.

This checks examples, not the universal mathematical proof. No search engine,
optimizer, or frozen constructor is imported. All calculations are rational.
"""
from pathlib import Path
from fractions import Fraction as F
import json,random,itertools,sys
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]/'results'
Z=F(0);O=F(1)
def ip(a,b):return sum((x*y for x,y in zip(a,b)),Z)
def rho(delta,beta,eps):return delta/((1-beta)*eps+delta)
def constants(beta,T,R,K,G):
    dc=K*sum((F(s+1)*beta**s for s in range(T)),Z)
    dj=max(2*R*sum((F(s+1)*beta**s for s in range(h)),Z)+2*G*h*beta**h for h in range(1,T+1))
    return dc,dj
def modulus(w,bits,beta,T,m,eps,dc,dj):
    theta=min(O,(m-1)*w); gamma=F(1,2**bits)*sum((beta**j for j in range(T)),Z)
    return dc*theta+gamma+dc*rho(dj*theta+gamma,beta,eps)
def linmin(values,lo,hi):
    prob=list(lo);remain=1-sum(prob)
    assert remain>=0 and sum(hi)>=1
    for a in sorted(range(len(values)),key=lambda a:(values[a],a)):
        add=min(remain,hi[a]-prob[a]);prob[a]+=add;remain-=add
    assert remain==0
    return ip(prob,values)
def run():
    beta=F(9,10);T=3;n=2;m=3;eps=F(1,10)
    P=[[[F(3,4),F(1,4)],[F(1,4),F(3,4)],[O,Z]],[[F(1,4),F(3,4)],[F(3,4),F(1,4)],[O,Z]]]
    r=[[Z,Z,-F(1,4)],[Z,Z,-F(3,10)]];k=[[O,F(7,10),Z],[F(7,5),F(2,5),Z]]
    dc,dj=constants(beta,T,F(3,10),F(7,5),Z)
    rng=random.Random(450925);passed=0;discarded=0;records=[]
    for test in range(256):
        bits=[8,12,20,44][test%4];w=F(1,2**(test%8))
        boxes=[]
        for t in range(T):
            layer=[]
            for i in range(n):
                l1=F(rng.randrange(0,5),8);l2=F(rng.randrange(0,2),32)
                layer.append(([Z,l1,l2],[O,min(O,l1+w),min(O,l2+w)]))
            boxes.append(layer)
        lowD=[[Z]*n for _ in range(T+1)];lowC=[[Z]*n for _ in range(T+1)]
        quantum=2**bits
        floor=lambda x:F((x.numerator*quantum)//x.denominator,quantum)
        for t in reversed(range(T)):
            for i in range(n):
                lo,hi=boxes[t][i]
                lowD[t][i]=floor(linmin([-r[i][a]+beta*ip(P[i][a],lowD[t+1]) for a in range(m)],lo,hi))
                lowC[t][i]=floor(linmin([k[i][a]+beta*ip(P[i][a],lowC[t+1]) for a in range(m)],lo,hi))
        if any(v>eps for layer in lowD for v in layer):discarded+=1;continue
        J=[Z]*n;C=[Z]*n
        for t in reversed(range(T)):
            nj=[];nc=[]
            for i in range(n):
                lo,hi=boxes[t][i];prob=[1-lo[1]-lo[2],lo[1],lo[2]]
                Q=[r[i][a]+beta*ip(P[i][a],J) for a in range(m)];val=ip(prob,Q)
                if val < -eps:
                    star=max(range(m),key=lambda a:Q[a]);alpha=(-eps-val)/(Q[star]-val)
                    prob=[(1-alpha)*x+alpha*int(a==star) for a,x in enumerate(prob)]
                value=ip(prob,Q);assert value>=-eps and sum(prob)==1 and min(prob)>=0
                nj.append(value);nc.append(ip(prob,[k[i][a]+beta*ip(P[i][a],C) for a in range(m)]))
            J,C=nj,nc
        gap=sum(C,F(0))/n-sum(lowC[0],F(0))/n;bound=modulus(w,bits,beta,T,m,eps,dc,dj)
        assert gap<=bound,(test,str(gap),str(bound))
        passed+=1;records.append(dict(test=test,bits=bits,width=str(w),observed_difference=str(gap),bound=str(bound)))
    assert passed>200
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'search_modulus_tests.json').write_text(json.dumps(dict(passed=True,seed=450925,boxes_attempted=256,surviving_boxes_checked=passed,necessary_test_prunes=discarded,exact_operating_tie=True,analytic_proof=False,records=records),indent=2)+'\n')
    # Explicit sufficient arithmetic floors and widths for every frozen model.
    proto=json.loads((ROOT/'revisions/2026-09-25-r44/PROTOCOL.json').read_text());rows=[]
    for name in proto['models_sha256']:
        d=json.loads((ROOT/'revisions/2026-09-25-r44/models'/f'{name}.json').read_text());b=F(d['beta']);e=F(d['epsilon']);T=d['T'];m=d['m'];n=d['n']
        R=max(abs(F(x)) for row in d['r'] for x in row);K=max(F(x) for row in d['k'] for x in row);G=max(abs(F(x)) for x in d['terminal'])
        DC,DJ=constants(b,T,R,K,G);target=F(1,1000);floor44=modulus(Z,44,b,T,m,e,DC,DJ)
        assert floor44<target
        level=0
        while modulus(F(1,2**level),44,b,T,m,e,DC,DJ)>target:level+=1
        rows.append(dict(name=name,DC=str(DC),DJ=str(DJ),fixed_44_bit_sufficient_floor=str(floor44),floor_float=float(floor44),target=str(target),width_level=level,sufficient_width=str(F(1,2**level)),sufficient_full_tree_depth=8*n*T*(m-1)*level,interpretation='Worst-case analytic bound, not executed search depth.'))
    (OUT/'precision_contract.json').write_text(json.dumps(dict(passed=True,rows=rows),indent=2)+'\n')
    print('PASS:',passed,'surviving exact three-action boxes;',len(rows),'frozen-model precision budgets')
if __name__=='__main__':run()
