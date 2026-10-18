"""Independent standard-library exact arithmetic audit of R119 phase-C output records.

No production fitting, actor, interval, risk or certificate routine is imported.
This checks recorded arithmetic/trace claims, not continuum validity by testing.
"""
from pathlib import Path
from fractions import Fraction as F
import json, hashlib, time, traceback


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p, value):
    Path(p).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def f(x):
    return F(float(x))


def audit(out):
    out = Path(out); start = time.perf_counter(); checks = 0; decisions = 0; attempts = 0; entries_all = []
    def check(condition, message):
        nonlocal checks
        checks += 1
        if not condition:
            raise ArithmeticError(message)
    def qualification(row):
        return f(row['loss']) <= F(1,256) and f(row['width']) <= F(1,8192)
    keys = ('lower','upper','optimum_lower','loss','width')
    manifests = ['CATALOGUE119.json']+[f'timing/PROCESS-{r}.json' for r in range(7)]
    for name in manifests:
        manifest = json.loads((out/name).read_text())
        for entry in manifest['entries']:
            path = out/entry['path']; check(digest(path)==entry['sha256'], 'Raw file content hash')
            data = json.loads(path.read_text()); entries_all.append(entry['path'])
            trace = {r['row']:[] for r in data['rows']}
            for attempt in data['attempts']:
                attempts += 1; trace[attempt['row']].append(attempt)
                lo,hi,opt = map(f,(attempt['lower'],attempt['upper'],attempt['optimum_lower']))
                check(lo<=hi and opt<=hi, 'Attempt interval ordering')
                check(f(attempt['loss'])>=hi-opt, 'Attempt outward loss')
                check(f(attempt['width'])>=hi-lo, 'Attempt outward width')
                check(qualification(attempt)==attempt['qualified'], 'Attempt qualification gate')
                if attempt['kind'] in ('active-tail','budgeted-tail'):
                    alpha = f(data['alpha']); cut=f(attempt['cut']); R=F(1,32); length=2*R*alpha
                    check(-R<=cut<=R-length, 'Original feasible tail cut')
                    check((cut*2**32).denominator==1, 'Original dyadic density identity')
                    check(f(attempt['kappa'])>=0, 'Nonnegative certified tail deficit')
                    check(f(attempt['selected_tail_lower'])<=f(attempt['selected_tail_upper']), 'Selected-tail ordering')
            if data['service'] in ('masked-tail','budgeted-tail','fused-tail'):
                schedule=(2,4) if data['service'] in ('budgeted-tail','fused-tail') else (2,4,8,16,32,64)
                expected_midpoints=0; expected_endpoints=0; expected_floating=0
                alpha=f(data['alpha']); length=alpha/16
                cache_keys=('cut','kappa','derivative_lower','derivative_upper')
                for row in data['rows']:
                    history=trace[row['row']]
                    tail_attempts=[a for a in history if a['kind']=='budgeted-tail']
                    check(bool(tail_attempts),'Every masked row has a preliminary certificate')
                    levels=tuple(a['bins_per_tail'] for a in tail_attempts)
                    check(1<=len(levels)<=len(schedule) and levels==schedule[:len(levels)],
                        'Per-row preliminary resolutions form the declared schedule prefix')
                    check(all(a['kind']=='budgeted-tail' for a in history[:len(tail_attempts)]),
                        'All preliminary attempts precede complete fallback')
                    first_tail=tail_attempts[0]
                    check(all(all(f(a[k])==f(first_tail[k]) for k in cache_keys) for a in tail_attempts),
                        'The original cut and outward defect are cached unchanged for each row')
                    check(all(f(a['action'])==f(row['proposed']) for a in tail_attempts),
                        'Every preliminary certificate concerns the same realized proposal')
                    check(all(not qualification(a) for a in tail_attempts[:-1]),
                        'A qualified preliminary row receives no later refinement')
                    if qualification(tail_attempts[-1]):
                        check(len(history)==len(tail_attempts),
                            'Preliminary acceptance ends this row without a fallback')
                    else:
                        check(levels==schedule and len(history)>len(tail_attempts),
                            'An exhausted preliminary schedule enters complete fallback')
                        first_fallback=history[len(tail_attempts)]
                        check(first_fallback['kind']=='full-support-fallback' and first_fallback['bins']==128
                            and f(first_fallback['action'])==f(row['proposed']),
                            'Fallback begins at the unchanged 128-bin gate and original proposal')
                    cut=f(first_tail['cut'])
                    tails=int(cut>F(-1,32))+int(cut<F(1,32)-length)
                    check(tails in (1,2),'Each row retains all positive-mass tails')
                    row_midpoints=tails*sum(levels)
                    row_endpoints=tails*sum(m+1 for m in levels)
                    row_outward=2+row_midpoints+row_endpoints
                    row_floating=4+12*int(F(-1,32)<cut<F(1,32)-length)
                    check(row_floating<=16,'Per-row 16-value floating proposal budget')
                    if data['service'] in ('budgeted-tail','fused-tail'):
                        check(row_outward<=30,'Per-row 30-payload outward preliminary budget')
                        if tails==1:
                            check(row_outward<=16,'Per-row boundary 16-payload outward preliminary budget')
                    else:
                        check(row_outward<=518,'Per-row full masked-ladder outward budget')
                    expected_midpoints+=row_midpoints; expected_endpoints+=row_endpoints
                    expected_floating+=row_floating
                check(data['counts'].get('r119b_tail_residual_point_values',0)==2*len(data['rows']),
                    'The two outward defect payloads are acquired exactly once per row')
                check(data['counts'].get('r119b_midpoint_terminal_rows',0)==expected_midpoints,
                    'Exact positive-tail midpoint payload account')
                check(data['counts'].get('r119b_endpoint_terminal_rows',0)==expected_endpoints,
                    'Exact positive-tail endpoint payload account')
                expected_outward=2*len(data['rows'])+expected_midpoints+expected_endpoints
                actual_outward=sum(data['counts'].get(k,0) for k in ('r119b_tail_residual_point_values','r119b_midpoint_terminal_rows','r119b_endpoint_terminal_rows'))
                check(actual_outward==expected_outward,'All and only positive-tail original point payloads charged')
                if data['service']=='fused-tail':
                    resolutions={a['bins_per_tail'] for a in data['attempts'] if a['kind']=='budgeted-tail'}
                    check(data['counts'].get('r119c_packed_compiler_calls',0)==len(resolutions),
                        'Exactly one packed original compiler call per attempted resolution')
                    check(data['counts'].get('r119c_packed_point_rows',0)==expected_midpoints+expected_endpoints,
                        'The packed compiler contains exactly all positive-mass payloads')
                floating=data['counts'].get('r119b_tail_proposal_point_values',0)
                check(floating==expected_floating,'Actual masked floating search account')
                if data['service'] in ('budgeted-tail','fused-tail'):
                    check(actual_outward<=30*len(data['rows']),'Proved 30-point preliminary outward budget')
                    check(floating<=16*len(data['rows']),'Proved 16-value floating proposal budget')
            for row in data['rows']:
                decisions += 1
                lo,hi,opt = map(f,(row['lower'],row['upper'],row['optimum_lower']))
                check(lo<=hi and opt<=hi, 'Returned interval ordering')
                check(f(row['loss'])>=hi-opt and f(row['loss'])<=F(1,256), 'Original regret qualification')
                check(f(row['width'])>=hi-lo and f(row['width'])<=F(1,8192), 'Original policy-width qualification')
                cap=F(1,8)+(f(row['x0'])+f(row['x1']))/16
                check(0<=f(row['action'])<=cap, 'Actual feasible original action')
                check(f(row['action_distance_upper'])**2>=f(row['loss']), 'Outward action-distance bound')
                history=trace[row['row']]; check(bool(history), 'Retained nonempty attempt history')
                check(all(f(history[0][k])==f(row['first_'+k]) for k in keys), 'First attempt identity')
                check(f(history[0]['action'])==f(row['proposed']), 'Original proposal identity')
                check(all(f(history[-1][k])==f(row[k]) for k in keys), 'Returned last certificate identity')
                check(f(history[-1]['action'])==f(row['action']), 'Returned last action identity')
                check(row['first_attempt_rejected']==(not qualification(history[0])), 'First attempt rejection label')
                repair=any(a['kind']=='online-repair' for a in history)
                check(repair==row['proposal_repaired']==row['first_rejected'], 'Inherited repair-gate semantics')
                check(row['returned_action_changed']==(f(row['action'])!=f(row['proposed'])), 'Actual action-change label')
        if name!='CATALOGUE119.json':
            check(len(manifest['entries'])==96, 'Complete timing process catalogue')
    check(decisions==35328, 'All 13824 primary and 21504 timing decisions')
    arms=('online','quadratic','relu','hinge','spline','poly2','poly3','grid')
    services=('compiled','geometric','active-tail','masked-tail','budgeted-tail','fused-tail')
    for i in range(2):
        for arm in arms:
            policies=[json.loads((out/'catalogue'/f'{i}-{arm}-{s}.json').read_text()) for s in services]
            check(len({p['model_sha256'] for p in policies})==1, 'Same paid actor across services')
            for rows in zip(*(p['rows'] for p in policies)):
                check(len({r['proposed'] for r in rows})==1, 'Same original actor proposal across services')
        for service in services:
            a=json.loads((out/'catalogue'/f'{i}-relu-{service}.json').read_text())['rows']
            b=json.loads((out/'catalogue'/f'{i}-hinge-{service}.json').read_text())['rows']
            for aa,bb in zip(a,b):
                check(all(aa[k]==bb[k] for k in keys+('action','proposed')), 'Equivalent ReLU and hinge records')
    reference=json.loads((out/'REFERENCE119.json').read_text()); reference_decisions=0
    expected_contrasts={(arm,services[j],services[k]) for arm in arms
        for j in range(len(services)) for k in range(j+1,len(services))}
    for record in reference['records']:
        i=record['index']; raw={}
        for arm in arms:
            for service in services:
                raw[arm+'/'+service]=json.loads((out/'catalogue'/f'{i}-{arm}-{service}.json').read_text())['rows']
        unique=record['unique']; refs_by_state={}
        check(len({(r['row'],f(r['action'])) for r in unique})==len(unique),
            'Original state-action reference keys are uniquely deduplicated')
        for ref in unique:
            refs_by_state.setdefault(ref['row'],[]).append(ref)
        for state in record['states']:
            lower,upper=map(f,(state['optimum_lower'],state['optimum_upper']))
            check(lower<=upper,'Independent original-optimum bracket')
            state_refs=refs_by_state.get(state['row'],[])
            check(bool(state_refs),'Every original state has unique-action reference records')
            check(lower==max(f(r['optimum_lower']) for r in state_refs),
                'Original-optimum lower endpoint is the maximum all-action reference lower bound')
            check(upper==min(f(r['upper']) for r in state_refs),
                'Original-optimum upper endpoint is the minimum feasible-policy reference upper bound')
            check(len(state['policies'])==len(raw) and {p['policy'] for p in state['policies']}==set(raw),
                'Every arm-service policy has exactly one current-state reference')
            policy_refs={}
            for policy in state['policies']:
                reference_decisions+=1
                row=raw[policy['policy']][state['row']]
                index=policy['reference_index']
                check(isinstance(index,int) and 0<=index<len(unique),'Valid unique-policy reference index')
                ref=unique[index]; policy_refs[policy['policy']]=ref
                check(ref['row']==state['row']==row['row'],'Reference and returned action share the original state index')
                check(tuple(map(f,ref['state']))==tuple(map(f,state['state']))==(f(row['x0']),f(row['x1'])),
                    'Reference and returned action share the exact original state')
                check(f(row['action'])==f(policy['action'])==f(ref['action']), 'Same-policy independent reference')
                check(all(f(policy[k])==f(ref[k]) for k in ('lower','upper')),
                    'Reported policy endpoints are the actual unique-action reference endpoints')
                check(max(f(row['lower']),f(policy['lower']))<=min(f(row['upper']),f(policy['upper'])), 'Independent policy enclosures overlap')
                check(f(policy['regret_lower'])<=max(0,f(policy['lower'])-upper), 'Regret lower interval')
                check(f(policy['regret_upper'])>=f(policy['upper'])-lower, 'Regret upper interval')
                check(f(policy['action_distance_upper'])**2>=f(policy['regret_upper']), 'Reference action-distance upper bound')
            check(len(state['contrasts'])==len(expected_contrasts)
                and {(c['arm'],c['control'],c['treatment']) for c in state['contrasts']}==expected_contrasts,
                'All fifteen service contrasts are present once for each arm and original state')
            for contrast in state['contrasts']:
                arm=contrast['arm']; aa=raw[arm+'/'+contrast['control']][state['row']]['action']; bb=raw[arm+'/'+contrast['treatment']][state['row']]['action']
                check(contrast['identical_policy']==(aa==bb),'Actual policy contrast identity')
                check(f(contrast['lower'])<=f(contrast['upper']), 'Economic contrast ordering')
                if aa==bb:
                    check(contrast['lower']==contrast['upper']==0, 'Identical complete policy has exact zero cost contrast')
                else:
                    control=policy_refs[arm+'/'+contrast['control']]
                    treatment=policy_refs[arm+'/'+contrast['treatment']]
                    check(f(contrast['lower'])<=f(treatment['lower'])-f(control['upper']),
                        'Economic contrast lower endpoint encloses the exact reference difference')
                    check(f(contrast['upper'])>=f(treatment['upper'])-f(control['lower']),
                        'Economic contrast upper endpoint encloses the exact reference difference')
                check(contrast['strictly_improved']==(f(contrast['upper'])<0), 'Strict economic improvement label')
                check(contrast['strictly_worse']==(f(contrast['lower'])>0), 'Strict economic deterioration label')
    check(reference_decisions==13824,'Every returned primary policy referenced')
    result=dict(status='passed', exact_record_checks=checks, decision_rows=decisions,
        attempted_certificates=attempts, referenced_primary_decisions=reference_decisions,
        source_sha256=digest(__file__), seconds=time.perf_counter()-start,
        checked_files=entries_all, reference_sha256=digest(out/'REFERENCE119.json'),
        scope='Exact binary-rational record and sequential-identity audit; continuum validity is proved separately')
    save(out/'AUDIT119C.json',result)
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if (args.output/'AUDIT119C.json').exists() or (args.output/'AUDIT119C_FAILED.json').exists():
        raise FileExistsError('Preserve each attempted audit receipt')
    try:
        result=audit(args.output); print(json.dumps({k:v for k,v in result.items() if k!='checked_files'}))
    except BaseException:
        save(args.output/'AUDIT119C_FAILED.json',dict(status='failed',exception=traceback.format_exc(),source_sha256=digest(__file__)))
        raise
