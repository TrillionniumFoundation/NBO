"""Exact arithmetic spot checks of the new sufficient resource allocation.

These are proof-account checks, not executed training or timing observations.
The universal statement is established by the manuscript's inequalities.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib,itertools,json
R=Path(__file__).resolve().parents[1]
def dyadic_exponent(q):
    k=0
    while F(2)**k<q:k+=1
    return k

def main():
    beta=F(15,16);Cx=F(13,4);Lg=F(9,2);Fx=F(11,16);Fa=F(3,4);Ka=F(1,16)
    rows=[]
    for T,p,epsilon in itertools.product((1,2,3,8),(1,4),(F(1),F(1,4),F(1,64))):
        S=sum((beta**t for t in range(T)),F(0));Ca=F(p,2)+F(1,4)
        contraction=beta*(Fx+Fa*Ka);assert contraction==F(705,1024)<1
        L=max(Lg,(Cx+Ka*Ca)/(1-contraction));D=Ca+beta*Fa*L
        C=S*(D/8+2*L+beta*L/16)+2*beta**T*Lg
        N=2**dyadic_exponent(4*C/epsilon);xi=epsilon/(8*(S+beta**T))
        A=2*S*(L+D*Ka);K=S*D;b=dyadic_exponent(4*A/epsilon);a_bits=dyadic_exponent(4*K/epsilon)
        Delta=F(1,2**a_bits);base=C/N+2*(S+beta**T)*xi;acquired=A/F(2)**b+K*Delta
        assert base<=epsilon/2 and acquired<=epsilon/2 and base+acquired<=epsilon
        power=dyadic_exponent(N);ladder=sum(2**(4*j) for j in range(power+1))
        assert ladder<=F(16,15)*N**4
        rows.append({'T':T,'price':p,'epsilon':str(epsilon),'sufficient_N':N,'query_accuracy':str(xi),'sensor_bits':b,'action_bits':a_bits,'base_upper':str(base),'acquisition_upper':str(acquired),'total_upper':str(base+acquired),'dyadic_work_factor_at_most':'16/15','executed_economic_service':False})
    out={'passed':True,'cases':len(rows),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Exact rational spot checks of the sufficient accuracy allocation and geometric work sum, not a substitute for the universal proof and not training or timing data.','checks':rows}
    (R/'audit').mkdir(exist_ok=True);(R/'audit/PROOF_BUDGET_CHECK.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'passed':True,'cases':len(rows)}))
if __name__=='__main__':main()
