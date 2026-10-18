"""Independent standard-library exact arithmetic audit of R119 output records.

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
                if attempt['kind']=='active-tail':
                    alpha = f(data['alpha']); cut=f(attempt['cut']); R=F(1,32); length=2*R*alpha
                    check(-R<=cut<=R-length, 'Original feasible tail cut')
                    check((cut*2**32).denominator==1, 'Original dyadic density identity')
                    check(f(attempt['kappa'])>=0, 'Nonnegative certified tail deficit')
                    check(f(attempt['selected_tail_lower'])<=f(attempt['selected_tail_upper']), 'Selected-tail ordering')
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
            check(len(manifest['entries'])==48, 'Complete timing process catalogue')
    check(decisions==17664, 'All 6912 primary and 10752 timing decisions')
    arms=('online','quadratic','relu','hinge','spline','poly2','poly3','grid')
    services=('compiled','geometric','active-tail')
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
    for record in reference['records']:
        i=record['index']; raw={}
        for arm in arms:
            for service in services:
                raw[arm+'/'+service]=json.loads((out/'catalogue'/f'{i}-{arm}-{service}.json').read_text())['rows']
        for state in record['states']:
            lower,upper=map(f,(state['optimum_lower'],state['optimum_upper']))
            check(lower<=upper,'Independent original-optimum bracket')
            for policy in state['policies']:
                reference_decisions+=1
                row=raw[policy['policy']][state['row']]
                ref=record['unique'][policy['reference_index']]
                check(f(row['action'])==f(policy['action'])==f(ref['action']), 'Same-policy independent reference')
                check(max(f(row['lower']),f(policy['lower']))<=min(f(row['upper']),f(policy['upper'])), 'Independent policy enclosures overlap')
                check(f(policy['regret_lower'])<=max(0,f(policy['lower'])-upper), 'Regret lower interval')
                check(f(policy['regret_upper'])>=f(policy['upper'])-lower, 'Regret upper interval')
                check(f(policy['action_distance_upper'])**2>=f(policy['regret_upper']), 'Reference action-distance upper bound')
            for contrast in state['contrasts']:
                arm=contrast['arm']; aa=raw[arm+'/'+contrast['control']][state['row']]['action']; bb=raw[arm+'/'+contrast['treatment']][state['row']]['action']
                check(contrast['identical_policy']==(aa==bb),'Actual policy contrast identity')
                check(f(contrast['lower'])<=f(contrast['upper']), 'Economic contrast ordering')
                if aa==bb:
                    check(contrast['lower']==contrast['upper']==0, 'Identical complete policy has exact zero cost contrast')
                check(contrast['strictly_improved']==(f(contrast['upper'])<0), 'Strict economic improvement label')
                check(contrast['strictly_worse']==(f(contrast['lower'])>0), 'Strict economic deterioration label')
    check(reference_decisions==6912,'Every returned primary policy referenced')
    result=dict(status='passed', exact_record_checks=checks, decision_rows=decisions,
        attempted_certificates=attempts, referenced_primary_decisions=reference_decisions,
        source_sha256=digest(__file__), seconds=time.perf_counter()-start,
        checked_files=entries_all, reference_sha256=digest(out/'REFERENCE119.json'),
        scope='Exact binary-rational record and sequential-identity audit; continuum validity is proved separately')
    save(out/'AUDIT119.json',result)
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if (args.output/'AUDIT119.json').exists() or (args.output/'AUDIT119_FAILED.json').exists():
        raise FileExistsError('Preserve each attempted audit receipt')
    try:
        result=audit(args.output); print(json.dumps({k:v for k,v in result.items() if k!='checked_files'}))
    except BaseException:
        save(args.output/'AUDIT119_FAILED.json',dict(status='failed',exception=traceback.format_exc(),source_sha256=digest(__file__)))
        raise
