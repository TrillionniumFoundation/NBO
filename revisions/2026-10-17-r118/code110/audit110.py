"""Independent exact arithmetic re-accounting, not a risk-oracle implementation.
This module imports neither the acquisition nor the production service.
"""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,argparse,time
ARMS=('online','quadratic','relu','hinge','spline','poly2','poly3','grid')
KEYS=('lower','upper','optimum_lower','loss','width')

def require(ok,what):
    if not ok:raise ArithmeticError(what)

def fr(v):return F(float(v))
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def certificate(r,prefix=''):
    lo,hi,opt,loss,width=(fr(r[prefix+k]) for k in KEYS)
    require(lo<=hi and opt<=hi,'ordered certificate')
    require(0<=hi-opt<=loss<=F(1,256),'original-policy loss')
    require(0<=hi-lo<=width<=F(1,8192),'original-policy width')
    return lo,hi,opt,loss,width


def audit(out,inherited):
    out=Path(out);inherited=Path(inherited);count=0;decisions=0;slots=0;skipped=0;stop_rows=0;beg=time.perf_counter()
    files=[]
    for name in ['CATALOGUE110.json']+[f'timing/PROCESS-{r}.json' for r in range(7)]:
        manifest=read(out/name)
        for ent in manifest['records']:
            p=out/ent['path'];require(digest(p)==ent['sha256'],'raw content hash');count+=1
            data=read(p);theta=None if data['theta'] is None else fr(data['theta'])
            states={}
            for r in data['rows']:
                certificate(r);certificate(r,'baseline_');count+=6
                cap=F(1,8)+(fr(r['x0'])+fr(r['x1']))/16
                require(0<=fr(r['action'])<=cap,'original feasibility');count+=1
                require(fr(r['action_distance_upper'])**2>=fr(r['loss']),'outward action distance');count+=1
                states[r['row']]={'action':fr(r['completed_baseline_action']),
                    **{k:fr(r['baseline_'+k]) for k in KEYS},'changes':0,'stopped':False,'first_stop':None}
            for t in data['trials']:
                slots+=1;s=states[t['row']]
                require(s['action']==fr(t['incumbent_action']),'incumbent action custody');count+=1
                for k in ('lower','upper'):
                    require(s[k]==fr(t['incumbent_'+k]),'incumbent interval custody');count+=1
                if t.get('skipped',False):
                    require(theta is not None and s['loss']<=theta,'remaining-gain stop authority');count+=1
                    require(not t['accepted'],'no action change when skipped');count+=1
                    if not s['stopped']:s['first_stop']=t['trial'];stop_rows+=1
                    s['stopped']=True;skipped+=1
                else:
                    if theta is not None:
                        require(not s['stopped'] and s['loss']>theta,'registered allocation mask');count+=1
                    lo,hi,opt,loss,width=(fr(t['candidate_'+k]) for k in KEYS)
                    require(lo<=hi and 0<=hi-opt<=loss and 0<=hi-lo<=width,'candidate arithmetic');count+=1
                    qualifies=(loss<=F(1,256) and width<=F(1,8192))
                    gate=hi<s['lower'] and qualifies and fr(t['candidate_action'])!=s['action']
                    require(gate==t['accepted'],'strict original-policy descent gate');count+=1
                    if gate:
                        s.update(action=fr(t['candidate_action']),lower=lo,upper=hi,optimum_lower=opt,loss=loss,width=width,changes=s['changes']+1)
            for r in data['rows']:
                s=states[r['row']]
                require(s['action']==fr(r['action']) and s['changes']==r['safe_changes'],'returned trace');count+=1
                for k in KEYS:require(s[k]==fr(r[k]),'returned cost custody');count+=1
                if theta is not None:
                    require(s['stopped']==r['stopped'],'stop flag');count+=1
                    if s['stopped']:
                        z=r['stop_certificate'];certificate(z)
                        require(fr(z['loss'])<=theta and z['action']==r['action'],'immutable stopped action');count+=1
                        require(s['first_stop']==r['first_stop_round'],'first stop time');count+=1
            decisions+=len(data['rows']);files.append({'path':ent['path'],'decisions':len(data['rows']),'trial_slots':len(data['trials'])})
    paired=[];budgets=[]
    for i in range(2):
        for arm in ARMS:
            for name in ('compiled','compiled-safe'):
                old=read(inherited/'catalogue'/f'{i}-{arm}-{name}.json');new=read(out/'catalogue'/f'{i}-{arm}-{name}.json')
                equal=old['rows']==new['rows'] and old['trials']==new['trials']
                paired.append({'risk_index':i,'arm':arm,'service':name,'all_rows_and_trials_exact':equal})
            full=read(out/'catalogue'/f'{i}-{arm}-compiled-safe.json')['rows']
            for k in (12,14,16,18):
                data=read(out/'catalogue'/f'{i}-{arm}-gain-{k}.json');theta=F(1,2**k);allowances=[];unstopped_equal=True
                for r,s in zip(data['rows'],full):
                    if r['action']==s['action']:allowances.append(F(0));continue
                    if r['stopped']:
                        z=r['stop_certificate'];allowance=fr(z['loss'])
                        require(allowance<=theta,'actual stopped allowance');count+=1
                        require(fr(r['lower'])-fr(s['upper'])<=allowance,'independent cost comparison compatible with stop theorem');count+=1
                        allowances.append(min(allowance,max(F(0),fr(r['upper'])-fr(s['lower']))))
                    else:
                        unstopped_equal=False;allowances.append(max(F(0),fr(r['upper'])-fr(s['lower'])))
                budgets.append({'risk_index':i,'arm':arm,'theta':str(theta),
                  'unstopped_actions_exact_full_safe':unstopped_equal,'mean_foregone_gain_upper':str(sum(allowances,F(0))/len(allowances)),
                  'all_within_registered_budget':all(v<=theta for v in allowances)})
    require(decisions==27648,'all primary and seven timing decisions present')
    require(slots==69120,'every prescribed active/omitted trial slot present')
    receipt={'status':'passed','exact_arithmetic_checks':count,'decision_rows':decisions,'trial_slots':slots,
             'omitted_trial_slots':skipped,'stopping_events':stop_rows,'source_sha256':digest(__file__),
             'paired_inherited_controls':paired,'budget_checks':budgets,'files':files,'seconds':time.perf_counter()-beg,
             'scope':'independent Fraction checks of stored gates, masks, feasibility, cost intervals and hashes; not a formal proof or independent full floating risk oracle'}
    save(out/'AUDIT110.json',receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('files','paired_inherited_controls','budget_checks')},indent=2))
    print('Exact inherited controls',sum(r['all_rows_and_trials_exact'] for r in paired),'/',len(paired))
    print('Budget cases',sum(r['all_within_registered_budget'] for r in budgets),'/',len(budgets))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--inherited',required=True,type=Path)
    a=p.parse_args();audit(a.output,a.inherited)
