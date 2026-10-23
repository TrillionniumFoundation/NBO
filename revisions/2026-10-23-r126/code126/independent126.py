"""Independent original rational economics on every fresh R126 selected action.

No production actor, certificate, interval or optimization implementation is
imported. Exact original primitives have a separately checked frozen identity.
Saved production actions select what to evaluate; their values are recomputed.
"""
import argparse, collections
from common126 import *

LEVELS=(8,32,128)
NODE_CAP=32768


def original_smoothness(alpha):
    beta=F(15,16); mz=F(181,64)
    m=F(1413,128)+beta*(F(127,16)+F(19625,20480)*alpha/(1-alpha))
    c=F(4,5)*m
    return 5+beta*(F(5,16)*m+c*c*alpha/(mz*(1-alpha)))


def derivative_record(evaluation):
    a=F(evaluation['action']); state=tuple(F(x) for x in evaluation['state'])
    A=F(1,8)+sum(state)/16; L=original_smoothness(F(evaluation['alpha']))
    gap=F(evaluation['q_upper'])-F(evaluation['all_action_anchor'])
    slope=F(evaluation['all_action_gradient'])
    def error(available):
        if available<=0: return None
        radii={available}|{F(1,2**j) for j in range(2,41) if F(1,2**j)<=available}
        return min(gap/h+(L-2)*h/2 for h in radii)
    right,left=error(A-a),error(a)
    low=max(F(-7),slope-right) if right is not None else F(-7)
    high=min(F(7),slope+left) if left is not None else F(7)
    if gap<0 or low>high: raise ArithmeticError('Independent original derivative enclosure failed')
    return dict(a=a,A=A,L=L,lower=low,upper=high,gap=gap)


def economic_bounds(kid,evaluations,groups):
    value=evaluations[kid]; a=F(value['action']); A=F(1,8)+sum(F(x) for x in value['state'])/16
    peers=[evaluations[k] for k in groups[(tuple(value['state_hex']),float(value['alpha']).hex())]]
    derivatives=[derivative_record(v) for v in peers]
    lower=max(g['lower']+(2 if a>=g['a'] else g['L'])*(a-g['a']) for g in derivatives)
    upper=min(g['upper']+(g['L'] if a>=g['a'] else 2)*(a-g['a']) for g in derivatives)
    if lower>upper: raise ArithmeticError('Independent derivative records disagree')
    gaps=[]
    for gradient in (lower,upper):
        displacement=max(-a,min(A-a,-gradient/2))
        gaps.append(-gradient*displacement-displacement*displacement)
    projected=max(F(0),*gaps)
    best_optimum_lower=max(F(v['optimum_lower']) for v in peers)
    best_feasible_q_upper=min(F(v['q_upper']) for v in peers)
    lower_q=max(F(v['all_action_anchor'])+F(v['all_action_gradient'])*(a-F(v['action']))+(a-F(v['action']))**2 for v in peers)
    lower_j=max(F(value['j_lower']),lower_q)
    upper_j=F(value['j_upper'])
    return dict(j_lower=lower_j,j_upper=upper_j,original_optimum_lower=best_optimum_lower,
        regret_lower=max(F(0),lower_j-best_feasible_q_upper),
        regret_upper=min(upper_j-best_optimum_lower,DELTA+projected),
        original_derivative_interval=[lower,upper],projected_original_gap=projected,
        economic_scope='original Q optimum and unchanged implemented future J in [Q,Q+delta]')


def run(primary,output):
    out,tick,info=start(output,'independent-rational-original-economics')
    try:
        verified=verify_inputs()
        sys.path.insert(0,str(R121/'code121'))
        import exact121 as exact
        ir,identity=exact.load_primitives(); exact.TERMINAL_STEPS=32
        data=rows(Path(primary)/'records126.jsonl.gz'); keys={}; links=[]
        for row in data:
            x=tuple(F(v) for v in row['state126']); action=F(row['action']); alpha=F(row['alpha'])
            key=exact.key(x,action,alpha); kid=exact.key_id(key)
            keys[kid]=(key,dict(x=x,a=action,alpha=alpha)); links.append((row,kid))
        if len(keys)*17>NODE_CAP: raise RuntimeError('Fixed audit cap cannot cover every action at the minimum precision')
        trace=exact.ExactTrace(out/'terminal_witnesses126.jsonl.gz')
        evaluations={}; levels={}; nodes=0; groups=collections.defaultdict(set); bound_cache={}
        for kid,(key,values) in keys.items(): groups[(tuple(key[0]),key[2])].add(kid)
        def bound_for(kid):
            if kid not in bound_cache: bound_cache[kid]=economic_bounds(kid,evaluations,groups)
            return bound_cache[kid]
        def check(row,kid):
            bound=bound_for(kid)
            lo,hi=F(row['complete_policy_lower']),F(row['complete_policy_upper'])
            claimed=F(row['certified_regret_upper'])
            contained=lo<=bound['j_lower']<=bound['j_upper']<=hi
            overlap=not(bound['j_upper']<lo or bound['j_lower']>hi)
            return dict(**bound,interval_contained=contained,interval_overlap=overlap,
                regret_confirmed=bound['regret_upper']<=claimed,claimed_regret_upper=claimed,
                independent_ordinary_qualified=bound['regret_upper']<=TAU,
                independent_stronger_target=bound['regret_upper']<=TARGET,
                contradiction=(not overlap) or bound['regret_lower']>claimed)
        try:
            for bins in LEVELS:
                if bins==8: pending=set(keys)
                else:
                    pending=set()
                    for row,kid in links:
                        c=check(row,kid)
                        if not(c['interval_contained'] and c['regret_confirmed']): pending.add(kid)
                for kid in sorted(pending):
                    need=2*bins+1
                    if nodes+need>NODE_CAP: continue
                    exact.BINS=bins; key,values=keys[kid]
                    answer=exact.evaluate_action(ir,key,values,trace)
                    append(out/'evaluations126.jsonl.gz',answer)
                    evaluations[kid]=answer; levels[kid]=bins; nodes+=need
                    bound_cache.clear()
                    print(json.dumps(dict(key_id=kid,bins=bins,unique_evaluated=len(evaluations),requested_terminal_contexts=nodes)),flush=True)
            checks=[]
            for row,kid in links:
                c=check(row,kid)
                item={k:row[k] for k in ('index','budget','arm','training_loss','mode','row')}
                item.update(key_id=kid,**c); checks.append(item); append(out/'checks126.jsonl',item)
            # Every within-actor direct-versus-control difference is retained.
            keyed={tuple(r[k] for k in ('index','budget','arm','training_loss','mode','row')):(r,kid) for r,kid in links}
            pairs=[]
            for actor in actors():
                for row_index in range(len(STATES)):
                    direct,key_d=keyed[actor+('direct_terminal',row_index)]
                    for mode in ('fused_control','warm_adaptive'):
                        control,key_c=keyed[actor+(mode,row_index)]
                        bd=bound_for(key_d); bc=bound_for(key_c)
                        if key_d==key_c: lo=hi=F(0)
                        else: lo=bd['j_lower']-bc['j_upper']; hi=bd['j_upper']-bc['j_lower']
                        pair=dict(actor=actor,row=row_index,comparator=mode,direct_key=key_d,control_key=key_c,
                            same_complete_policy=key_d==key_c,direct_minus_control_lower=lo,direct_minus_control_upper=hi,
                            direct_strictly_better=hi<0,control_strictly_better=lo>0,unresolved_order=lo<=0<=hi and key_d!=key_c)
                        pairs.append(pair); append(out/'policy_pairs126.jsonl',pair)
            summary=dict(decisions=len(data),unique_actions=len(keys),requested_terminal_contexts=nodes,
                node_cap=NODE_CAP,levels=LEVELS,level_by_key=levels,
                interval_containments=sum(c['interval_contained'] for c in checks),
                regret_bounds_confirmed=sum(c['regret_confirmed'] for c in checks),
                unresolved_interval_containments=sum(not c['interval_contained'] for c in checks),
                unresolved_regret_checks=sum(not c['regret_confirmed'] for c in checks),
                independent_ordinary_qualified=sum(c['independent_ordinary_qualified'] for c in checks),
                independent_stronger_target=sum(c['independent_stronger_target'] for c in checks),
                contradictions=sum(c['contradiction'] for c in checks),policy_comparisons=len(pairs),
                exact_policy_ties=sum(c['same_complete_policy'] for c in pairs),
                direct_strict_policy_improvements=sum(c['direct_strictly_better'] for c in pairs),
                direct_strict_policy_losses=sum(c['control_strictly_better'] for c in pairs),
                unresolved_policy_order=sum(c['unresolved_order'] for c in pairs),
                counts=dict(exact.COUNTS),primitive_identity=identity,source=verified,independent_population_samples=0)
            write(out/'SUMMARY126.json',summary)
            if summary['contradictions']: raise ArithmeticError('Independent original economics contradicts production certificate')
            finish(out,tick,**summary)
        finally: trace.close()
    except BaseException: fail(out,tick); raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--primary',required=True); parser.add_argument('--output',required=True)
    args=parser.parse_args(); run(args.primary,args.output)
