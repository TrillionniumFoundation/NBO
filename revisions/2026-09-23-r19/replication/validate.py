"""Fail-closed arithmetic, acceptance, evidence-integrity and retention tests.
These checks are not a formal proof of the shared mathematical derivations.
"""
from pathlib import Path
from fractions import Fraction as F
import sys,json,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'revisions/2026-09-23-r19'
sys.path.insert(0,str(Path(__file__).resolve().parent))
import policy_sensitive as P
I,Q=P.I,P.Q

def read(p):return json.loads(p.read_text())
def check(condition,message):
    if not condition:raise AssertionError(message)
def main():
    out=R/'results/policy_sensitive';rows=read(out/'results.json');check(len(rows)==20,'Need every policy checkpoint')
    counts={'primitive_arithmetic':P.M.test(),'policy_checkpoints':len(rows)}
    for seed in P.SEEDS:
        seq=sorted([r for r in rows if r['seed']==seed],key=lambda r:r['step']);check([r['step'] for r in seq]==list(P.CHECKPOINTS),'Checkpoint set changed')
        inline=read(out/f'seed{seed}/inline_gate.json');check(len(inline)==4,'Missing inline decisions')
        for r,g in zip(seq,inline):
            ap=ROOT/r['actor_path'];check(P.sha(ap)==r['actor_sha256']==g['actor_sha256'],'Actor hash mismatch')
            a=read(ap);check(P.sha(ROOT/a['network_path'])==a['network_sha256'],'Network hash mismatch')
            check(g['accepted'] and g['verification_finished_before_next_adam_update'],'Inline value gate not passed')
            check(r['value_interval']==g['value_interval'],'Gate value mismatch')
            check(len(a['c'])==len(a['theta'])==len(a['p'])==16,'Wrong policy shape')
            check(all(v==0 for v in a['p']),'Portfolio changed')
        for a,b in zip(seq,seq[1:]):check(F(b['value_interval'][0])>F(a['value_interval'][1]),'No strict policy value improvement')
        check(seq[-1]['target_0.01'],'Target not attained at reference state')
    counts['strict_policy_transitions']=15
    # Regression examples prevent confusing better lower bounds with actual ordering.
    check(not (F('1.1')>F('1.3')),'Overlapping intervals must not pass')
    check(F('1.4')>F('1.3'),'Disjoint improving intervals must pass')
    check(not (F('1.3')>F('1.3')),'Touching intervals must not pass strict gate')
    gains=read(out/'uniform_policy_gain.json');states=read(out/'uniform_state_regret.json');con=read(out/'true_regret_contraction.json')
    check(len(gains)==len(states)==len(con)==5,'Incomplete deterministic extension')
    for g,s,c in zip(gains,states,con):
        check(g['uniform_payoff_gain_interval'][0]>0,'Uniform gain not positive')
        check(s['uniform_K_regret_upper']<.012,'K regret outside reported range')
        check(c['uniform_K_final_to_initial_true_regret_ratio_upper']<.42,'True-regret contraction failed')
    check(all(r['compensation_sufficient'] for r in read(out/'neural_wealth_compensation.json')),'Compensation failed')
    traces=read(out/'continuation_value_traces.json');check(all(r['uniform_u_segment_trace_excess_lower']>6.708 for r in traces),'Continuation trace not established')
    check(all(r['covered_trace_second_derivative_upper']<0 for r in traces),'Discounted continuation curvature not certified')
    a=R/'results/attribution';fa=read(a/'factorial.json')
    check(len(fa)==40 and len(read(a/'trace_trajectories.json'))==30 and len(read(a/'trace_interventions.json'))==5,'Incomplete attribution')
    check(len(read(a/'classical_signed.json'))==6,'Incomplete original feedback comparison')
    for seed in range(17100,17110):
        sub=[r for r in fa if r['seed']==seed];x=next(r for r in sub if r['actor_step']==0 and r['critic_step']==400);y=next(r for r in sub if r['actor_step']==400 and r['critic_step']==400)
        check(x['total']==y['total'] and y['negative_component_interval']==[0.,0.],'Historical attribution changed')
        for r in sub:check(P.sha(ROOT/r['certificate_path'])==r['certificate_sha256'],'Certificate hash mismatch')
    counts.update({'factorial_objects':40,'trace_checkpoints':30,'trace_interventions':5,'classical_feedback_decompositions':6})
    total=0
    for d in [8,32,128]:
        wd=R/f'results/warm_frontier/d{d}';rr=read(wd/'records.json');check(len(rr)==640,'Missing query records')
        plans=np.load(wd/'plans.npz',allow_pickle=False);res=read(wd/'resources.json')
        check(P.sha(wd/'plans.npz')==res['plan_archive_sha256'],'Plan archive mismatch')
        for r in rr:
            check(r['status']=='PASS','A target failed')
            check(r['gradient_calls']==r['corrections']+1,'Gradient work miscount')
            check(F(r['certificate']['total_cost_loss_upper'])<=F(str(r['tolerance'])),'Directed target inequality failed')
            check(hashlib.sha256(plans[r['plan_key']].tobytes()).hexdigest()==r['plan_sha256'],'Stored plan mismatch')
        total+=len(rr)
    check(len(read(R/'results/warm_frontier/summary.json'))==36,'Incomplete all-seed frontier')
    counts['directed_query_targets']=total;counts['all_seed_frontier_rows']=36
    # Response coverage is not equated with mathematical closure of an objection.
    response=(R/'paper/response.tex').read_text()
    for prefix,n in [('F',11),('T',10)]:
        for i in range(1,n+1):check(f'R18-{prefix}{i} ---' in response,f'Missing response {prefix}{i}')
    counts.update({'referee_findings_addressed':11,'technical_comments_addressed':10,'status':'PASS','formal_proof':False,
       'scope':'Arithmetic and evidence consistency checks; independent numerical validation, not independent mathematics or closure of all scientific gates'})
    P.write(R/'results/validation.json',counts);print(json.dumps(counts,indent=2))
if __name__=='__main__':main()
