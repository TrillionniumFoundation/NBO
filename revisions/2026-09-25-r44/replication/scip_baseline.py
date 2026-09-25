"""External global solver, given the identical common-policy problem and cuts.
SCIP's lower bound is solver-reported, not an independent rational certificate.
A returned policy is repaired and independently reevaluated before publication.
"""
from fractions import Fraction as F
import time, json
import global_solver as core

def solve(d,seconds=120,nodes=2047,target=F(1,1000),logfile=None):
    from pyscipopt import Model,quicksum
    import pyscipopt
    begin=time.perf_counter(); cache=core.prepare(d,True); V,H,star,loss,gain,*_=cache['ref']
    n,T,m=d['n'],d['T'],d['m']; beta=float(d['beta']); eps=float(d['epsilon'])
    rect=core.rectangular(d,cache,cache['root']); lp=core.build(d,cache,cache['root'],rect)
    model=Model('same-object-common-Markov'); model.hideOutput()
    if logfile: model.setLogfile(str(logfile))
    model.setIntParam('parallel/maxnthreads',1); model.setIntParam('randomization/randomseedshift',0)
    model.setRealParam('numerics/feastol',1e-9); model.setLongintParam('limits/nodes',nodes); model.setRealParam('limits/absgap',float(target))
    x={}
    for key in cache['coords']:
        lo,hi=lp.bounds[lp.idx[('p',)+key]]; x[key]=model.addVar(name='p_%s_%s_%s'%key,lb=float(lo),ub=float(hi))
    D={}; S={}
    for t in range(T):
        for i in range(n):
            for name,target_dict in [('D',D),('S',S)]:
                lo,hi=lp.bounds[lp.idx[(name,t,i)]]; target_dict[t,i]=model.addVar(name=f'{name}_{t}_{i}',lb=float(lo),ub=float(hi))
    for t in range(T):
        for i in range(n):
            aa=[a for a in range(m) if a!=star[t][i]]; total=quicksum(x[t,i,a] for a in aa); model.addCons(total<=1)
            prob={a:(1-total if a==star[t][i] else x[t,i,a]) for a in range(m)}
            model.addCons(quicksum(float(loss[t][i][a])*prob[a] for a in range(m))<=eps)
            for lam,lo,hi in cache['env']:
                model.addCons(S[t,i]-float(lam)*D[t,i]<=float(hi[t][i])); model.addCons(S[t,i]-float(lam)*D[t,i]>=float(lo[t][i]))
            if cache['ref'][-1]:
                lm,lu=cache['ref'][-3:-1]; model.addCons(S[t,i]<=float(lu)*D[t,i]); model.addCons(S[t,i]>=float(lm)*D[t,i])
            for value,stage in [(D,loss),(S,gain)]:
                expression=quicksum(prob[a]*(float(stage[t][i][a])+(beta*quicksum(float(d['P'][i][a][j])*value[t+1,j] for j in range(n) if d['P'][i][a][j]) if t<T-1 else 0)) for a in range(m))
                model.addCons(value[t,i]==expression)
    const=float(core.dot(d['nu'],H[0])); model.setObjective(const-quicksum(float(d['nu'][i])*S[0,i] for i in range(n)),'minimize')
    initial=model.createSol()
    for var in list(x.values())+list(D.values())+list(S.values()): model.setSolVal(initial,var,0.)
    model.addSol(initial)
    build_seconds=time.perf_counter()-begin
    model.setRealParam('limits/time',max(.01,seconds-build_seconds)); model.optimize()
    proposal=[[[F(0)]*m for i in range(n)] for t in range(T)]
    sol=model.getBestSol()
    if sol is not None:
        for key,var in x.items(): proposal[key[0]][key[1]][key[2]]=max(F(0),core.quantize(model.getSolVal(sol,var)))
    policy,upper,*_=core.old.repair(d,proposal,cache['ref'])
    status=str(model.getStatus()); native_lower=float(model.getDualbound()); native_upper=float(model.getPrimalbound())
    return dict(schema='nbo-r44-scip-v1',model=d,policy=policy,verified_candidate_upper=upper,
        summary=dict(status=status,native_lower=native_lower,native_upper=native_upper,native_gap=max(0.,native_upper-native_lower),native_target_met=native_upper-native_lower<=float(target),
                     nodes=int(model.getNNodes()),solve_seconds=float(model.getSolvingTime()),seconds=time.perf_counter()-begin,build_seconds=build_seconds,pyscipopt_version=pyscipopt.__version__,
                     lower_bound_status='solver-reported floating-point; not independently certified'))
