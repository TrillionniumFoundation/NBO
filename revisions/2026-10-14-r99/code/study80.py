"""Matched calibrated-modulus construction; no hidden-feature fitting.

The bases, coefficient limits, state cells, action menu and original laws are
inherited. Only the qualification modulus is changed. No historical scientific
clock or observation is replaced.
"""
from fractions import Fraction as F
from dataclasses import asdict
from pathlib import Path
import itertools,json,math,time,hashlib
from qualification73 import Problem,dot
from calibrated80 import Calibrated,modulus
import study73 as primitive
R=Path(__file__).resolve().parents[1]
BETA=primitive.BETA;ACTIONS=32;QUANTUM=4096;TOL=F(1,65536)

def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x

def save(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(encode(x),sort_keys=True,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def problem(raw):return Problem(tuple(tuple(map(F,r)) for r in raw['features']),tuple(map(F,raw['lower'])),tuple(map(F,raw['upper'])),tuple(map(F,raw['lipschitz'])),tuple(map(F,raw['bounds'])),F(raw['radius']),F(raw['bellman_lipschitz']))

def label_data(n,future,kind):
    rho=F(1,n);Lf=F(5) if future is None else modulus(future,kind)
    Lx=F(4)+BETA*F(11,16)*Lf;La=F(13,16)+BETA*F(3,4)*Lf;C=Lx+La/16
    nodes=[];lower=[];upper=[];actions=[];selected=[];zero=[];calls=0
    for i,j in itertools.product(range(n),repeat=2):
        x=(F(2*i+1,2*n),F(2*j+1,2*n));cap=primitive.capacity(x)
        values=[primitive.qvalue(x,cap*k/ACTIONS,future,kind) for k in range(ACTIONS+1)];calls+=len(values)
        lo=min(values)-La*cap/(2*ACTIONS);up=min(values)
        cap_index=math.floor(primitive.capacity((F(i,n),F(j,n)))*QUANTUM)
        menu=tuple(F((cap_index*k)//ACTIONS,QUANTUM) for k in range(ACTIONS+1))
        costs=[primitive.qvalue(x,a,future,kind) for a in menu];calls+=len(costs)
        pick=min(range(len(menu)),key=lambda k:(costs[k],menu[k]))
        nodes.append(x);lower.append(lo);upper.append(up);actions.append(menu[pick])
        selected.append(costs[pick]-lo);zero.append(values[0]-lo)
    extra=(Lx+C)*rho
    return dict(nodes=nodes,lower=lower,upper=upper,actions=actions,rho=rho,Lx=Lx,La=La,C=C,Lfuture=Lf,
        eta_policy=max(selected)+extra,eta_zero=max(zero)+extra,exact_action_evaluations=calls,
        expected_feature_evaluations=0 if future is None else 9*calls,recursive_optimal_value_queries=0)

def service(n,kind):
    start=time.perf_counter();stages=[];future=None
    for t in (1,0):
        before=time.perf_counter();data=label_data(n,future,kind);label_seconds=time.perf_counter()-before
        phi=tuple(primitive.features(x,kind) for x in data['nodes'])
        P=Problem(phi,tuple(data['lower']),tuple(data['upper']),tuple([F(0)]+[F(1 if kind=='relu' else 4)]*8),tuple([F(8)]*9),data['rho'],data['C'])
        model=Calibrated(P,kind);fit=model.solve()
        if not fit['solver_success']:raise AssertionError('Failed proposed fit is retained by the failed-attempt workflow')
        theta=list(fit['theta']);center=sum(((l+u)/2-dot(row[1:],theta[1:]) for row,l,u in zip(phi,data['lower'],data['upper'])),F(0))/len(phi)
        theta[0]=max(F(-8),min(F(8),F(round(center*2**40),2**40)))
        fit.update(model.primal(theta));fit['optimization_gap']=fit['objective']-fit['dual_lower']
        if fit['optimization_gap']<0:raise AssertionError('Exact negative gap after centering')
        old=json.loads((R/'results73'/f'{kind}-n{n}'/'service.json').read_text())['stages'][t]
        fixed_label_probe=model.primal(tuple(map(F,old['attained']['theta'])))
        stages.append(dict(date=t,kind=kind,problem=asdict(P),derivative_control_rows=model.rows,data=data,future=future,
            attained=fit,label_seconds=label_seconds,state_nodes=n*n,coefficient_count=9,
            optimization_within_declared_tolerance=fit['optimization_gap']<=TOL,
            legacy_readout_on_current_labels=fixed_label_probe))
        future=tuple(theta)
    stages.sort(key=lambda s:s['date'])
    omega=sum((BETA**s['date']*s['attained']['objective'] for s in stages),F(0));gap=sum((BETA**s['date']*s['data']['eta_policy'] for s in stages),F(0))
    out=dict(n=n,dimension=2,horizon=2,basis=kind,stages=stages,omega=omega,greedy_policy_allowance=gap,
        original_optimum_regret_upper=omega+gap,seconds_before_output=time.perf_counter()-start,
        exact_action_evaluations=sum(s['data']['exact_action_evaluations'] for s in stages),
        expected_feature_evaluations=sum(s['data']['expected_feature_evaluations'] for s in stages),
        all_optimization_gaps_pass=all(s['optimization_within_declared_tolerance'] for s in stages),
        new_policy_cost_observations=0,recursive_optimal_value_queries=0,
        accounting='Both own-future backward fits, robust actors, all labels and exact dual checks; no label-loss ablation is included or claimed.')
    folder=R/'results80/construction'/f'{kind}-n{n}'
    save(folder/'service.json',out);save(folder/'clock.json',dict(seconds_through_service_output=time.perf_counter()-start,service_sha256=sha(folder/'service.json')))
    return out

def verify(fits=True):
    rows=[]
    for n,kind in itertools.product((8,16),('relu','bernstein')):
        folder=R/'results80/construction'/f'{kind}-n{n}';j=json.loads((folder/'service.json').read_text());clock=json.loads((folder/'clock.json').read_text())
        if sha(folder/'service.json')!=clock['service_sha256']:raise AssertionError('Construction hash')
        future=None
        for stage in reversed(j['stages']):
            model=Calibrated(problem(stage['problem']),kind);fit=stage['attained'];theta=tuple(map(F,fit['theta']))
            value=model.primal(theta);D=model.dual(fit['p'],fit['q'],fit['xi'])
            for key in value:
                if encode(value[key])!=fit[key]:raise AssertionError('Exact primal disagreement '+key)
            if D!=F(fit['dual_lower']) or value['objective']-D!=F(fit['optimization_gap']):raise AssertionError('Exact dual disagreement')
            if value['objective']-D>TOL:raise AssertionError('Attained gap tolerance')
            if fits:
                data=label_data(n,future,kind)
                if encode(data)!=stage['data']:raise AssertionError('Full primitive-label and action reconstruction')
            future=theta
        rows.append(dict(name=f'{kind}-n{n}',stages=2,nodes=2*n*n,exact_action_evaluations=j['exact_action_evaluations']))
    save(R/'audit/CONSTRUCTION_REPLAY80.json',dict(status='passed',services=rows,refitted=False,complete_labels_and_actors_reconstructed=fits,new_cost_rows=0))
    return rows

def main():
    out=R/'results80/construction'
    if out.exists():raise FileExistsError('Do not overwrite an executed construction')
    begin=time.perf_counter();summaries=[]
    for n,kind in itertools.product((8,16),('relu','bernstein')):
        j=service(n,kind);s=dict(name=f'{kind}-n{n}',gap=j['original_optimum_regret_upper'],objectives=[t['attained']['objective'] for t in j['stages']],all_gaps_pass=j['all_optimization_gaps_pass'],seconds=j['seconds_before_output'])
        summaries.append(s);print(json.dumps(encode(s)),flush=True)
    save(R/'audit/CONSTRUCTION80.json',dict(status='passed' if all(x['all_gaps_pass'] for x in summaries) else 'gap_not_met',services=summaries,seconds=time.perf_counter()-begin,new_cost_rows=0))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');a=parser.parse_args();verify() if a.verify else main()
