#!/usr/bin/env python3
"""Execute the old TV-reset error budget against a new exact structural reference."""
import gzip,json,time
from fractions import Fraction as F
from pathlib import Path
from structured import model,solve
from verify_structured import verify
BASE=Path(__file__).resolve().parents[1]
n,T,m,kind,beta,eps=8,8,3,'band','19/20',F(1,20)
d=model(n,T,m,kind,beta,str(eps));B=d['beta'];R=max(abs(x) for row in d['r'] for x in row);K=max(x for row in d['k'] for x in row)
def compute(label,e):
    o=solve(model(n,T,m,kind,beta,str(e)),False); check=verify(o)
    with gzip.open(BASE/'proofs'/f'density_{label}.json.gz','wt') as f:json.dump(o,f,sort_keys=True)
    return o,check
ref,refcheck=compute('reference',eps);rows=[]
for zeta in (F(1,10),F(1,1000),F(1,1000000)):
    alpha=zeta/2;aj=F(0);bc=F(0);BJ=F(0);BC=F(0);avec=[F(0)];bvec=[F(0)]
    for t in reversed(range(T)):
        aj=B*aj+B*alpha*BJ;bc=B*bc+B*alpha*BC
        BJ=R+B*BJ;BC=K+B*BC;avec.append(aj);bvec.append(bc)
    a=max(avec);b=max(bvec);s=dict(zeta=str(zeta),operator_alpha=str(alpha),probability_tv=str(alpha/2),d_r='0',d_k='0',d_g='0',R=str(R),K=str(K),a=str(a),b=str(b),epsilon=str(eps),applicable=eps>2*a)
    if s['applicable']:
        op,cp=compute(str(zeta.denominator)+'_plus',eps+2*a);om,cm=compute(str(zeta.denominator)+'_minus',eps-2*a)
        rp,rm=op['results'],om['results'];L=max(F(0),F(rp['lower'])-b);U=F(rm['upper'])+b
        etaP=F(rp['gap']);etaM=F(rm['gap']);dc=K*sum((j+1)*B**j for j in range(T));repair=dc*(4*a)/((1-B)*(eps-2*a)+4*a)
        assert L<=F(ref['results']['upper']) and U>=F(ref['results']['lower'])
        assert U-L<=etaP+etaM+2*b+repair
        s.update(lower=str(L),upper=str(U),gap=str(U-L),finite_plus_gap=str(etaP),finite_minus_gap=str(etaM),cost_error_twice=str(2*b),repair_cost_bound=str(repair),total_theorem_bound=str(etaP+etaM+2*b+repair),plus_check=cp,minus_check=cm)
    else:s.update(status='reset_tightening_condition_failed; retained; exact structural reference remains valid')
    rows.append(s)
res=dict(schema='R42-executed-TV-transfer-v1',density='P_ij [1+zeta f(u)f(v)] dv, f(u)=2u_1-1 on [0,1)^2',initial='sum_i 2(i+1)/(n(n+1)) times uniform within-cell measure',reference=ref['results'],reference_check=refcheck,outcomes=rows)
(BASE/'results'/'density_transfer.json').write_text(json.dumps(res,indent=2)+'\n')
for r in rows:print(r['zeta'],r['applicable'],float(F(r['a'])),float(F(r['gap'])) if 'gap'in r else 'not-applicable')
