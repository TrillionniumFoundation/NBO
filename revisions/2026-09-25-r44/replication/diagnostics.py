"""Complete fixed-model theorem constants and additional allowance points."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,importlib.util,hashlib
import global_solver as core
from run_case import frozen,write
from models import create
HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('old_check',core.ROOT/'revisions/2026-09-25-r43/replication/verify_regret.py')
check=importlib.util.module_from_spec(spec);spec.loader.exec_module(check)

def constants(d):
    ref=core.old.reference(d); V,H,star,loss,gain,lm,lu,strict=ref
    n,T,m=d['n'],d['T'],d['m'];b=d['beta'];eps=d['epsilon']
    gaps=[loss[t][i][a] for t in range(T) for i in range(n) for a in range(m) if a!=star[t][i]]
    common=dict(strict=strict,d_min=str(min(gaps)),lambda_minus=str(lm),lambda_plus=str(lu))
    if not strict: return {**common,'theorem_applies':False,'reason':'operating tie: no inverse-gap rate asserted'}
    e=[F(0)]*T; ed=[F(0)]*(T+1); es=[F(0)]*(T+1)
    for t in range(T-1):
        sensitivity=max(sum((sum(abs(d['P'][i][a][j]-d['P'][i][star[t][i]][j]) for j in range(n))/loss[t][i][a] for a in range(m) if a!=star[t][i]),F(0)) for i in range(n))
        e[t]=b*eps*eps*sensitivity/4
    for t in reversed(range(T)): ed[t]=e[t]+b*ed[t+1];es[t]=(lu-lm)*e[t]+b*es[t+1]
    maxed=max(ed);dc=max(max(r) for r in d['k'])*sum((F(s+1)*b**s for s in range(T)),F(0));chi=min(F(1),eps/min(gaps));rho=maxed/((1-b)*eps+maxed)
    bound=es[0]+dc*chi*rho
    return {**common,'theorem_applies':True,'ED':list(map(str,ed)),'ES':list(map(str,es)),'ED_max':str(maxed),'ES0':str(es[0]),'DC':str(dc),'chi':str(chi),'rho':str(rho),'repair_term':str(dc*chi*rho),'exact_LP_theorem_bound':str(bound),'interpretation':'bound for an exact optimizing relaxed solution and exact repair; not an assertion that numerical output attains it'}

def main():
    p=frozen();rows=[]
    for family in ['maintenance','inventory','queue']:
        for denominator in [10,100,1000,10000,100000,1000000,10000000]:
            d=create(family,440301,3,8,3,'19/20',F(1,denominator))
            for mode in ['scaled','unscaled']:
                obj,meta=core.old.solve(d,mode,seconds=20)
                path=HERE/'proofs'/'scaling'/f'{family}_{denominator}_{mode}.json.gz'
                core.old.write_proof(path,obj)
                # R43 standalone verifier independently rebuilds its own LP.
                verified=check.verify(path)
                record=dict(family=family,epsilon=str(d['epsilon']),mode=mode,metadata=meta,verification=verified,constants=constants(d),measured_width_over_epsilon_squared=meta['gap']/float(d['epsilon'])**2)
                rows.append(record);print(family,denominator,mode,meta['gap'],flush=True)
    write(HERE/'results'/'scaling_diagnostics.json',rows)
    cases={}
    for name in p['models_sha256']:
        raw=json.loads((HERE/'models'/f'{name}.json').read_text());cases[name]=constants(core.old.parse_model(raw))
    write(HERE/'results'/'all_model_constants.json',cases)

if __name__=='__main__':main()
