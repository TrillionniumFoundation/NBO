"""R73 predetermined backward continuation qualification in the original economy.

Four construction services: two covers and two nine-coefficient bases. Exact
conditional expectations, continuous-action lower covers and whole-cell actors
are charged. The label-loss readout is a matched, fixed-label ablation. There
are no new policy-cost samples, no retiming of historical services, and no
unrestricted hidden-feature training claim.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from dataclasses import asdict
import hashlib,itertools,json,math,os,platform,time
import numpy as np
from scipy.optimize import lsq_linear
from qualification73 import Problem,solve,dot
R=Path(__file__).resolve().parents[1]
BETA=F(15,16); D=2; HORIZON=2; ACTIONS=32; QUANTUM=4096; BITS=28


def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x

def save(path,x):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(encode(x),sort_keys=True,indent=2)+'\n')

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def capacity(x):return F(1,8)+sum(x)/16

def deterministic_next(x,a):
    return tuple(F(1,16)+x[j]/2+x[1-j]/8+x[j]*(1-x[1-j])/16+(F(1,2) if j==0 else F(1,4))*a for j in range(2))

def cost(x,a):
    return sum((z-F(5,8))**2 for z in x)+(x[0]-x[1])**2/4+2*max(F(0),F(1,2)-sum(x))**2+a*a+4*a**4

def terminal_expectation(x,a):
    y=deterministic_next(x,a)
    # Common opposite-signed U[-1/32,1/32] has variance 1/3072.
    return 2*sum((z-F(5,8))**2 for z in y)+(y[0]-y[1])**2/4+2*max(F(0),F(1,2)-sum(y))**2+F(5,3072)

def features(x,kind):
    if kind=='relu':return (F(1),)+tuple(v for z in x for v in (z,max(F(0),z-F(1,4)),max(F(0),z-F(1,2)),max(F(0),z-F(3,4))))
    if kind=='bernstein':return (F(1),)+tuple(F(math.comb(4,j))*z**j*(1-z)**(4-j) for z in x for j in range(1,5))
    raise ValueError('Unknown fixed basis')

def moment(z,p):
    return sum((F(math.comb(p,k))*z**(p-k)*F(1,32)**k/F(k+1) for k in range(0,p+1,2)),F(0))

def feature_means(x,a,kind):
    y=deterministic_next(x,a)
    if kind=='relu':
        out=[F(1)]
        for z in y:
            out.append(z)
            for knot in (F(1,4),F(1,2),F(3,4)):
                v=z-knot;r=F(1,32)
                out.append((max(F(0),v+r)**2-max(F(0),v-r)**2)/(4*r))
        return tuple(out)
    if kind=='bernstein':
        return (F(1),)+tuple(F(math.comb(4,j))*sum((F((-1)**k*math.comb(4-j,k))*moment(z,j+k) for k in range(5-j)),F(0)) for z in y for j in range(1,5))
    raise ValueError('Unknown fixed basis')

def qvalue(x,a,future,kind):
    continuation=terminal_expectation(x,a) if future is None else dot(feature_means(x,a,kind),future)
    return cost(x,a)+BETA*continuation

def label_data(n,future,kind):
    rho=F(1,n);Lf=F(5) if future is None else dot(([F(0)]+[F(1 if kind=='relu' else 4)]*8),[abs(v) for v in future])
    Lx=F(4)+BETA*F(11,16)*Lf;La=F(13,16)+BETA*F(3,4)*Lf
    C=Lx+La/16
    nodes=[];lower=[];upper=[];actions=[];selected=[];zero=[];calls=0
    for i,j in itertools.product(range(n),repeat=2):
        x=(F(2*i+1,2*n),F(2*j+1,2*n));cap=capacity(x)
        values=[qvalue(x,cap*k/ACTIONS,future,kind) for k in range(ACTIONS+1)];calls+=len(values)
        lo=min(values)-La*cap/(2*ACTIONS);up=min(values)
        # Robustly feasible downward-quantized proposals on the entire cell.
        cap_index=math.floor(capacity((F(i,n),F(j,n)))*QUANTUM)
        menu=tuple(F((cap_index*k)//ACTIONS,QUANTUM) for k in range(ACTIONS+1))
        implemented=[qvalue(x,a,future,kind) for a in menu];calls+=len(implemented)
        pick=min(range(len(menu)),key=lambda k:(implemented[k],menu[k]))
        nodes.append(x);lower.append(lo);upper.append(up);actions.append(menu[pick])
        selected.append(implemented[pick]-lo);zero.append(values[0]-lo)
    extra=(Lx+C)*rho
    return dict(nodes=nodes,lower=lower,upper=upper,actions=actions,
                rho=rho,Lx=Lx,La=La,C=C,Lfuture=Lf,
                eta_policy=max(selected)+extra,eta_zero=max(zero)+extra,
                exact_action_evaluations=calls,expected_feature_evaluations=0 if future is None else 9*calls,
                recursive_optimal_value_queries=0)

def service(n,kind):
    start=time.perf_counter();stages=[];future=None
    for t in (1,0):
        began=time.perf_counter();data=label_data(n,future,kind);label_seconds=time.perf_counter()-began
        features_table=tuple(features(x,kind) for x in data['nodes'])
        problem=Problem(features_table,tuple(data['lower']),tuple(data['upper']),
                        tuple([F(0)]+[F(1 if kind=='relu' else 4)]*8),tuple([F(8)]*9),data['rho'],data['C'])
        attained=solve(problem,BITS)
        # Fix only the constant gauge, preserving the qualification objective.
        theta=list(attained['theta'])
        center=sum((F(l+u,2)-dot(row[1:],theta[1:]) for row,l,u in zip(features_table,data['lower'],data['upper'])),F(0))/len(features_table)
        theta[0]=max(F(-8),min(F(8),F(round(center*2**BITS),2**BITS)))
        attained.update(problem.verify(theta,attained['p'],attained['q']))
        began=time.perf_counter();mid=np.asarray([(l+u)/2 for l,u in zip(data['lower'],data['upper'])],dtype=float)
        fitted=lsq_linear(np.asarray(features_table,dtype=float),mid,bounds=(-8,8),tol=1e-12,max_iter=10000)
        label_theta=tuple(max(F(-8),min(F(8),F(round(float(v)*2**BITS),2**BITS))) for v in fitted.x)
        ablation=problem.primal(label_theta)
        ablation.update(solver_success=bool(fitted.success),solver_status=int(fitted.status),solver_message=str(fitted.message),seconds=time.perf_counter()-began)
        record=dict(date=t,kind=kind,problem=asdict(problem),data=data,future=future,
                    attained=attained,label_loss_ablation=ablation,label_seconds=label_seconds,
                    state_nodes=n*n,coefficient_count=9,
                    optimization_within_declared_tolerance=attained['optimization_gap']<=F(1,65536))
        stages.append(record);future=tuple(theta)
    stages.sort(key=lambda z:z['date'])
    omega=sum((BETA**s['date']*s['attained']['objective'] for s in stages),F(0))
    Hp=sum((BETA**s['date']*s['data']['eta_policy'] for s in stages),F(0))
    Hz=sum((BETA**s['date']*s['data']['eta_zero'] for s in stages),F(0))
    result=dict(n=n,dimension=2,horizon=2,basis=kind,stages=stages,omega=omega,
                greedy_policy_allowance=Hp,zero_policy_allowance=Hz,
                original_optimum_regret_upper=omega+Hp,centered_cost_support=(-omega-Hz,omega+Hp),
                seconds_before_output=time.perf_counter()-start,
                exact_action_evaluations=sum(s['data']['exact_action_evaluations'] for s in stages),
                expected_feature_evaluations=sum(s['data']['expected_feature_evaluations'] for s in stages),
                recursive_optimal_value_queries=0,new_policy_cost_observations=0,
                all_optimization_gaps_pass=all(s['optimization_within_declared_tolerance'] for s in stages),
                accounting='both backward fits, all continuous-action and robust-actor queries, and matched label-loss ablations; output clock separately recorded')
    folder=R/'results73'/f'{kind}-n{n}'
    save(folder/'service.json',result)
    save(folder/'clock.json',dict(seconds_through_service_output=time.perf_counter()-start,service_sha256=digest(folder/'service.json')))
    return result

def verify_freeze():
    freeze=json.loads((R/'SOURCE_FREEZE73.json').read_text())
    for name,h in freeze['files'].items():
        if digest(R/name)!=h:raise AssertionError('Source freeze mismatch: '+name)
    return freeze

def main():
    freeze=verify_freeze();start=time.perf_counter();results=[]
    save(R/'audit/EXECUTION_STARTED73.json',dict(source_freeze_sha256=digest(R/'SOURCE_FREEZE73.json'),
         construction_design_commit=freeze['design_commit'],started_unix=time.time(),python=platform.python_version(),
         machine=platform.machine(),numpy=np.__version__,affinity=sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None))
    for n,kind in itertools.product((8,16),('relu','bernstein')):
        result=service(n,kind);results.append({k:result[k] for k in ('n','basis','omega','original_optimum_regret_upper','exact_action_evaluations','all_optimization_gaps_pass')})
        print(json.dumps(encode(results[-1])),flush=True)
    save(R/'audit/EXECUTION_FINISHED73.json',dict(status='passed' if all(r['all_optimization_gaps_pass'] for r in results) else 'optimization_tolerance_not_met',
        services=results,complete_construction_services=4,new_independent_policy_cost_rows=0,
        new_recursive_optimum_queries=0,seconds=time.perf_counter()-start))
if __name__=='__main__':main()
