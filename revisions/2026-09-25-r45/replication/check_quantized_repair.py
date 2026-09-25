"""Exact tests of the frozen reference-repair quantization contract.

The 256 seeded boxes match the ideal-repair tests; this is a second contract
check on those boxes, not 256 additional independent environments.
"""
from pathlib import Path
from fractions import Fraction as F
import json, random, sys
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
from check_search_modulus import constants, modulus, linmin, ip
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]/'results'
Z=F(0);O=F(1)
def qmod(w,bv,bp,beta,T,m,eps,dc,dj,dmax):
    S=sum((beta**t for t in range(T)),Z);theta=min(O,(m-1)*w)
    gamma=F(1,2**bv)*S;kappa=F(m-1,2**bp);mu=kappa*(dmax+beta*eps);slack=(1-beta)*eps
    if mu>=slack: return None
    delta=dj*theta+gamma;v=delta+mu*S
    return dc*theta+gamma+dc*min(O,kappa+v/(slack-mu+v))
def run():
    beta=F(9,10);T=3;n=2;m=3;eps=F(1,10)
    P=[[[F(3,4),F(1,4)],[F(1,4),F(3,4)],[O,Z]],[[F(1,4),F(3,4)],[F(3,4),F(1,4)],[O,Z]]]
    r=[[Z,Z,-F(1,4)],[Z,Z,-F(3,10)]];k=[[O,F(7,10),Z],[F(7,5),F(2,5),Z]]
    dc,dj=constants(beta,T,F(3,10),F(7,5),Z);rng=random.Random(450925);records=[]
    for test in range(256):
        bv=[8,12,20,44][test%4];bp=[8,12,20,40][test%4];w=F(1,2**(test%8));boxes=[]
        for t in range(T):
            layer=[]
            for i in range(n):
                l1=F(rng.randrange(0,5),8);l2=F(rng.randrange(0,2),32)
                layer.append(([Z,l1,l2],[O,min(O,l1+w),min(O,l2+w)]))
            boxes.append(layer)
        floor=lambda x,b:F((x.numerator*2**b)//x.denominator,2**b)
        lowD=[[Z]*n for _ in range(T+1)];lowC=[[Z]*n for _ in range(T+1)]
        for t in reversed(range(T)):
            for i in range(n):
                lo,hi=boxes[t][i]
                lowD[t][i]=floor(linmin([-r[i][a]+beta*ip(P[i][a],lowD[t+1]) for a in range(m)],lo,hi),bv)
                lowC[t][i]=floor(linmin([k[i][a]+beta*ip(P[i][a],lowC[t+1]) for a in range(m)],lo,hi),bv)
        assert all(v<=eps for layer in lowD for v in layer)
        D=[Z]*n;C=[Z]*n
        for t in reversed(range(T)):
            nd=[];nc=[]
            for i in range(n):
                lo,hi=boxes[t][i];p=[1-lo[1]-lo[2],lo[1],lo[2]]
                Q=[-r[i][a]+beta*ip(P[i][a],D) for a in range(m)]
                margin=F(m-1,2**bp)*max(abs(q-Q[0]) for q in Q);target=eps-margin
                assert target>Q[0]
                value=ip(p,Q)
                if value>target:
                    alpha=(value-target)/(value-Q[0]);p=[(1-alpha)*v+alpha*int(a==0) for a,v in enumerate(p)]
                p=[Z]+[floor(p[a],bp) for a in range(1,m)];p[0]=1-sum(p)
                value=ip(p,Q);assert 0<=value<=eps and min(p)>=0 and sum(p)==1
                nd.append(value);nc.append(ip(p,[k[i][a]+beta*ip(P[i][a],C) for a in range(m)]))
            D,C=nd,nc
        gap=sum(C,Z)/n-sum(lowC[0],Z)/n;bound=qmod(w,bv,bp,beta,T,m,eps,dc,dj,F(3,10))
        assert bound is not None and gap<=bound,(test,gap,bound)
        records.append(dict(test=test,value_bits=bv,probability_bits=bp,width=str(w),observed_difference=str(gap),bound=str(bound)))
    (OUT/'quantized_repair_tests.json').write_text(json.dumps(dict(passed=True,seed=450925,boxes=256,same_boxes_as_ideal_repair_test=True,analytic_proof=False,records=records),indent=2)+'\n')
    rows=[]
    proto=json.loads((ROOT/'revisions/2026-09-25-r44/PROTOCOL.json').read_text())
    for name in proto['models_sha256']:
        d=json.loads((ROOT/'revisions/2026-09-25-r44/models'/f'{name}.json').read_text());beta=F(d['beta']);eps=F(d['epsilon']);T=d['T'];m=d['m'];n=d['n']
        P=[[[F(v) for v in row] for row in st] for st in d['P']];r=[[F(v) for v in row] for row in d['r']];k=[[F(v) for v in row] for row in d['k']];V=list(map(F,d['terminal']));dmax=Z
        for t in reversed(range(T)):
            nxt=[]
            for i in range(n):
                q=[r[i][a]+beta*ip(P[i][a],V) for a in range(m)];v=max(q);nxt.append(v);dmax=max(dmax,max(v-qa for qa in q))
            V=nxt
        dc,dj=constants(beta,T,max(abs(v) for rr in r for v in rr),max(v for rr in k for v in rr),max(abs(F(v)) for v in d['terminal']))
        floor40=qmod(Z,44,40,beta,T,m,eps,dc,dj,dmax);target=F(1,1000)
        bp=40
        while qmod(Z,44,bp,beta,T,m,eps,dc,dj,dmax) is None or qmod(Z,44,bp,beta,T,m,eps,dc,dj,dmax)>=target:bp+=1
        level=0
        while qmod(F(1,2**level),44,bp,beta,T,m,eps,dc,dj,dmax)>target:level+=1
        rows.append(dict(name=name,maximum_disadvantage=str(dmax),value_bits=44,frozen_probability_bits=40,frozen_quantized_sufficient_floor=str(floor40) if floor40 is not None else None,floor_float=float(floor40) if floor40 is not None else None,sufficient_probability_bits=bp,width_level=level,sufficient_width=str(F(1,2**level)),sufficient_full_tree_depth=8*n*T*(m-1)*level,target=str(target),interpretation='Sufficient bound including reference-repair guard and probability rounding; not an observed search depth.'))
    (OUT/'quantized_precision_contract.json').write_text(json.dumps(dict(passed=True,rows=rows),indent=2)+'\n')
    print('PASS: quantized reference repair on all 256 boxes; dual-grid precision budgets for 16 models')
    for x in rows: print(x['name'],x['floor_float'],x['sufficient_probability_bits'])
if __name__=='__main__':run()
