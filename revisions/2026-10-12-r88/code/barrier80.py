"""All-cell action-switch barriers with independently replayable exact duals.

A failed/nonpositive lower certificate is reported as unresolved, never as
instability. The 20,480 finite LP proposals are not statistical observations.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse,itertools,json,math,time
from calibrated80 import Calibrated
from qualification73 import dot
from study80 import problem,save,encode,sha
import study73 as primitive
R=Path(__file__).resolve().parents[1]
TOLERANCES=(F(0),F(1,65536),F(1,4096))

def sparse(values):return [[i,str(v)] for i,v in enumerate(values) if v]
def dense(values,n):
    out=[F(0)]*n
    for i,v in values:
        if not 0<=i<n or out[i]:raise ValueError('Invalid sparse probability')
        out[i]=F(v)
    return out

def contrast(x,a,b,kind):
    left=primitive.feature_means(x,b,kind);right=primitive.feature_means(x,a,kind)
    return tuple(primitive.BETA*(u-v) for u,v in zip(left,right)),primitive.cost(x,b)-primitive.cost(x,a)

def menu(n,i,j):
    cap=math.floor(primitive.capacity((F(i,n),F(j,n)))*4096)
    return tuple(F((cap*k)//32,4096) for k in range(33))

def run_service(n,kind,replay=False):
    folder=R/'results80/construction'/f'{kind}-n{n}';source=json.loads((folder/'service.json').read_text())
    model=Calibrated(problem(source['stages'][1]['problem']),kind);fit=source['stages'][1]['attained'];upper=F(fit['objective'])
    theta=tuple(map(F,fit['theta']));actions=list(map(F,source['stages'][0]['data']['actions']));arrays=model.arrays();records=[];cell_bounds=[]
    target=R/'results80/barriers'/f'{kind}-n{n}.json';saved=json.loads(target.read_text()) if replay else None
    begin=time.perf_counter();index=0;failures=0
    for i,j in itertools.product(range(n),repeat=2):
        x=(F(2*i+1,2*n),F(2*j+1,2*n));a=actions[i*n+j];bounds=[]
        for b in menu(n,i,j):
            if b==a:continue
            d,c=contrast(x,a,b,kind)
            if c+dot(d,theta)<0:raise AssertionError('Reference actor not greedy for frozen continuation')
            if replay:
                row=saved['records'][index]
                if (row['cell'],row['competitor'])!=([i,j],str(b)):raise AssertionError('Incomplete action catalogue')
                p=dense(row['p'],len(model.problem.lower));q=dense(row['q'],len(p));xi=list(map(F,row['xi']));nu=F(row['nu'])
                lower=model.dual(p,q,xi,nu,d,c)
                if lower!=F(row['lower']):raise AssertionError('Exact action-barrier lower bound')
            else:
                answer=model.solve(d,c,arrays,primal=False);lower=answer['dual_lower']
                row=dict(cell=[i,j],reference=str(a),competitor=str(b),lower=str(lower),
                    p=sparse(answer['p']),q=sparse(answer['q']),xi=list(map(str,answer['xi'])),nu=str(answer['nu']),
                    solver_success=answer['solver_success'],solver_status=answer['solver_status'])
            if row['reference']!=str(a):raise AssertionError('Reference identity')
            if not row['solver_success']:failures+=1
            records.append(row);bounds.append(lower);index+=1
        if len(bounds)!=32:raise AssertionError('The entire robust alternative menu must be covered')
        cell_bounds.append(min(bounds))
        if not replay and (i*n+j+1)%64==0:print(kind,n,'verified root cells',i*n+j+1,flush=True)
    summary=dict(name=f'{kind}-n{n}',source_sha256=sha(folder/'service.json'),reference_objective=upper,
        global_switch_lower=min(cell_bounds),global_action_preserving_surplus=min(cell_bounds)-upper,
        total_cells=n*n,total_competitors=index,lp_solver_failures=failures,
        certified_cells_by_optimization_tolerance={str(tol):sum(v>upper+tol for v in cell_bounds) for tol in TOLERANCES},
        definition='Strict sublevel certificate relative to the fixed terminal-label qualification problem. Zero or negative surplus is unresolved, not a counterexample.',
        seconds=time.perf_counter()-begin)
    if replay:
        old=dict(saved['summary']);new=encode(dict(summary));old.pop('seconds');new.pop('seconds')
        if old!=new:raise AssertionError('Barrier summary replay')
    else:save(target,dict(summary=summary,records=records))
    return summary

def main(replay=False):
    begin=time.perf_counter();root=R/'results80/barriers'
    if root.exists() and not replay:raise FileExistsError('Preserve existing barrier run')
    summaries=[run_service(n,k,replay) for n,k in itertools.product((8,16),('relu','bernstein'))]
    out=dict(status='passed',services=summaries,total_action_switch_problems=sum(s['total_competitors'] for s in summaries),
        total_cells=sum(s['total_cells'] for s in summaries),new_statistical_observations=0,seconds=time.perf_counter()-begin,
        replay_reoptimizes=False if replay else None)
    save(R/'audit'/('BARRIER_REPLAY80.json' if replay else 'BARRIER80.json'),out)
    print(json.dumps(encode(out),indent=2),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--replay',action='store_true');a=p.parse_args();main(a.replay)
