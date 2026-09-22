"""Budget-financed original-economy wealth compensation and a validated
closed-form classical Riccati benchmark. Neither result is reassigned to NBO.
"""
from pathlib import Path
import sys,json,time,hashlib
from fractions import Fraction as F
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];R16=ROOT/'revisions/2026-09-23-r16';OUT=HERE.parent/'results'
sys.path.insert(0,str(R16/'replication'));import mpfr_interval as M
I,Q,exp,log,sqrt,tanh=M.I,M.I.rational,M.exp,M.log,M.sqrt,M.tanh

def wealth():
    start=time.perf_counter();out=OUT/'wealth_compensation';out.mkdir(parents=True,exist_ok=True)
    lib=R16/'results/fresh_library';env=json.loads((lib/'envelope.json').read_text());eps=I(env['uniform_regret_upper'])
    cr=(1-exp(-Q('.02')))/Q('.02');cd=(1-exp(-Q('.04')))/Q('.04');mu=exp(-Q('1.2')*log(Q('.8')))
    pe=2*exp(-Q('.58').square()/(2*Q('.05').square()));required=eps*cr/(mu*cd*(1-pe))
    # A simple rational rounded strictly above the analytic sufficient bound.
    delta=F(int(np.ceil(float(required.hi)*10000)),10000);shift=Q(delta)/cr
    paths=sorted(lib.glob('actor_k*.json'));rows=[]
    for p in paths:
        a=json.loads(p.read_text());c=I(a['c']);n=len(a['c']);cost=I(0)
        for j in range(n):cost=cost+c[j]*(exp(-Q('.02')*Q(F(j,n)))-exp(-Q('.02')*Q(F(j+1,n))))/Q('.02')
        terminal=exp(Q('.02'))*(Q('1.25')-cost);cnew=c+shift
        assert np.all(cnew.hi<=Q('.8').lo) and terminal.lo>Q('.5').hi
        # Base wealth decreases because r*x<=.025<c_min. The additional
        # wealth is <= exp(r)*delta until terminal and is exactly zero there.
        upper=Q('1.25')+exp(Q('.02'))*Q(delta);assert upper.hi<Q(2).lo
        rows.append({'actor':str(p.relative_to(ROOT)),'actor_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'k':a['k'],'compensated_consumption_hull':[float(cnew.lo.min()),float(cnew.hi.max())],'terminal_wealth_unchanged':terminal.pair(),'wealth_upper':float(upper.hi)})
    gain=shift*mu*cd*(1-pe);assert gain.lo>eps.hi
    r={'status':'VERIFIED_BUDGET_FINANCED_COMPENSATION','original_wealth':1.25,'wealth_increment_rational':str(delta),'wealth_increment':float(delta),'percent_of_initial_wealth_upper':float((Q(delta)/Q('1.25')*100).hi),'analytic_required_increment':required.pair(),'constant_consumption_increment':shift.pair(),'uniform_utility_gain_lower':float(gain.lo),'original_uniform_regret_upper':float(eps.hi),'slack_lower':float((gain-eps).lo),'preference_exit_probability_upper':float(pe.hi),'nodes_checked':len(rows),'all_price_scope':'Every k in [0.5,8], using the original certified library selector and its compensated selected policy','semantic_scope':'Sufficient initial wealth compensation with explicit budget-feasible policy adjustment. Not the exact minimum wealth equivalent of the unchanged feedback; no neural accuracy inference.','new_payoff_or_consumption_cap':False,'rows':rows,'wall_seconds':time.perf_counter()-start}
    (out/'certificate.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='rows'}),flush=True)
    # Independent replay with the retained original stopped-payoff evaluator.
    # It has its own exact budget-preserving transfer for x0 in [1.24,1.26].
    sys.modules['interval64']=M
    sys.path.insert(0,str(ROOT/'revisions/2026-09-22-r14/replication'))
    from independent_primal import evaluate
    from exact_price_audit import audit
    nodes=json.loads((lib/'nodes.json').read_text());replayed=[]
    for row in nodes:
        ap=ROOT/row['actor_path'];v=evaluate(ap,str(row['k']),u0='2',x0=str(F('1.25')+delta));tag=ap.stem.replace('actor_','')
        (out/f'primal_{tag}.json').write_text(json.dumps(v,indent=2)+'\n');z=dict(row);z['L']=v['value_interval'][0];replayed.append(z)
    audit_result=audit(replayed);(out/'direct_replay_envelope.json').write_text(json.dumps(audit_result,indent=2)+'\n')
    (out/'direct_replay_nodes.json').write_text(json.dumps(replayed,indent=2)+'\n')
    print('wealth direct replay',audit_result['uniform_regret_upper'],flush=True)

def pstar(h,a,q):
    a=Q(a);q=Q(q);k=sqrt(a.square()+q);y=(Q('.5')-a)/k;z=tanh(k*h)
    return a+k*(y+z)/(1+y*z)

def riccati():
    out=OUT/'validated_riccati';out.mkdir(parents=True,exist_ok=True);rows=[]
    C=(1-exp(-Q('.8')))/Q('.8');occupation=C+Q('.01')/Q('.8')*(1-C)
    for n in [32,128,512,2048]:
        start=time.perf_counter();pol=[];bounds=[]
        for a,q in [('-.2','1'),('.1','1.5')]:
            lo=I([float(Q(F(j,n)).lo) for j in range(n)]);hi=I([float(Q(F(j+1,n)).hi) for j in range(n)]);mid=I([float(Q(F(2*j+1,2*n)).lo) for j in range(n)],[float(Q(F(2*j+1,2*n)).hi) for j in range(n)])
            pm=pstar(mid,a,q);stored=(pm.lo+pm.hi)/2;lower=pstar(lo,a,q);upper=pstar(hi,a,q)
            error=I(lower.lo,upper.hi)-I(stored);bounds.append(float(error.maxabs().max()));pol.append(stored.tolist())
            assert min(stored)>.5
        delta=I(max(bounds));loss=delta.square()*occupation
        pf=out/f'policy_{n}.json';pf.write_text(json.dumps({'remaining_time_cells':n,'stored_mode_gains':pol,'format':'exact dyadic constants on each half-open remaining-time interval'},indent=2)+'\n')
        r={'method':'closed-form Riccati solution, MPFR point enclosures and monotone cell ranges','n':n,'mode_uniform_gain_errors':bounds,'per_coordinate_loss_upper':float(loss.hi),'total_loss_upper_d128':float((128*loss).hi),'time_seconds':time.perf_counter()-start,'policy_sha256':hashlib.sha256(pf.read_bytes()).hexdigest(),'scope':'Complete original R16 LQ inventory state domain; not a nonlinear high-dimensional benchmark','dimension_rows':[{'d':d,'total_loss_upper':float((d*loss).hi)} for d in [4,8,16,32,64,128]]}
        rows.append(r);print(json.dumps(r),flush=True)
    (out/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':
    riccati();wealth()
