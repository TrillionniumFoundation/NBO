"""Offline R69 record audit with a separate rational trajectory implementation.

Does not rerun training, retime services, or count repeated checks as samples.
Every missing receipt prevents completion. Failed services remain evidence.
"""
from pathlib import Path
from fractions import Fraction as F
import itertools,json,math,time
import numpy as np
import science69 as s
import readout69 as r
import center69 as center
import independent69 as independent
R=s.R;old=s.old

def need(test,message):
    if not test:raise AssertionError(message)
def check_files(root,record):
    for name,h in record.items():need(old.sha(root/name)==h,'File identity '+str(root/name))
def exact_models(root,summary):
    fit=summary.get('training',{});kind=summary['spec']['kind'];audits=[]
    if kind not in ('hat-relu','bernstein4'):return audits
    model=old.read(root/'model.json');model=model.get('models',model)
    with np.load(root/'training.npz') as raw:
        for report in fit['dates']:
            t=report['r'];prefix=f'r{t}_'
            c={name:raw[prefix+name] for name in ('x','cap','left_hi','right_hi','lower')}
            lam=F(13,16)+r.B*r.q.regularity(t-1,c['x'].shape[1])[0]*F(3*c['x'].shape[1],8)
            c.update(tol=report['tolerance'],allowance=r.q.up(lam*(F(1,2**32)+F(1,2**36))),K=report['recovery_root_cap'])
            weights=model[str(t)]['weights'];actual=r.exact_certificate(c,kind,weights,report['margin'],report['penalty'])
            for field in ('value_exact','dual_gap_exact','coefficient_count','feature_partition_verified'):
                need(actual[field]==report['exact_certificate'][field],'Exact readout replay '+field)
            proposals=r.prediction(kind,model,c['x'],t,c['cap']);max_rounding=F(0)
            for x,cap,l,u,lb,a in zip(c['x'],c['cap'],c['left_hi'],c['right_hi'],c['lower'],proposals):
                features=r.exact_phi(x,kind);z=sum(p*F(float(w)) for p,w in zip(features,weights))
                C=r.cert.Context(F(0),F(float(cap)),F(float(l)),F(float(u)),F(float(lb)),F(c['tol']))
                difference=C.chord(F(float(a))/F(float(cap)))-C.chord(z)
                need(difference<=F(c['allowance']),'Training rounding allowance not valid')
                max_rounding=max(max_rounding,difference)
            audits.append(dict(r=t,exact_certificate=actual,maximum_rounding_score_increase_exact=str(max_rounding)))
    return audits

def validation(root,summary):
    counts=[]
    with np.load(root/'validation.npz') as raw:
        for rec in summary['validation']:
            t=rec['r'];prefix=f'r{t}_';score=raw[prefix+'score'];loss=raw[prefix+'loss'];work=raw[prefix+'additional_root_queries']
            tol=float(raw[prefix+'cap'][0]*0+rec.get('tolerance',0)) if 'tolerance' in rec else old.budget(summary['spec']['T'],summary['spec']['target'])[0]
            tau=tol/4;surplus=(r.I.point(score)-r.I.point(tol)+r.I.point(tau))
            expected=np.minimum(1.,(r.I.point(np.maximum(0,surplus.hi)).square()/r.q.rat(F(tau)**2)).hi)
            need(np.array_equal(loss,expected),'Validation clipped loss')
            need(np.array_equal(work,np.where(score>tol,rec['K'],0)),'Executed validation recovery count')
            need(np.all(work<=rec['K']*loss),'Validation work-loss domination')
            need(np.all(raw[prefix+'gap']<=tol),'Validation full-action recovery gap')
            counts.append(dict(r=t,contexts=len(score),failures=int((score>tol).sum()),screen_returns=int((score<=tol).sum()),
                mean_root_queries=float(work.mean()),loss_mean=float(loss.mean()),distributional_root_upper=rec['validation_work_upper'],
                K=rec['K'],seconds=rec['seconds']))
    return counts

def trajectories(root,summary):
    spec=summary['spec'];T=spec['T'];answers=[]
    if spec['group'] in ('comparison','vector'):
        with np.load(root/'trace.npz') as a:answers.append(independent.audit_paths(a,a,T,spec['group']=='vector'))
    elif spec['group']=='reuse':
        need(len(summary['blocks'])==64,'Complete prospective block window')
        for rec in summary['blocks']:
            b=rec['block'];need(rec['identity_valid']==(b!=16),'Identity rejection schedule')
            need(rec['used_kind']==(spec['kind'] if b!=16 else 'adaptive'),'Stale-model fallback')
            need(old.sha(root/f'block{b:02d}.npz')==rec['trace_sha256'],'Reuse trace digest')
            with np.load(root/f'block{b:02d}.npz') as a:answers.append(independent.audit_paths(a,a,T))
    return answers

def inference(root,summary):
    lo={};hi={};cashlo={};cashhi={};G={};audits=[]
    with np.load(root/'randoms.npz') as randoms:
        for kind,arm in summary['arms'].items():
            need(old.sha(root/(kind+'-paths.npz'))==arm['trace_sha256'],'Inference path digest')
            need(old.sha(root/(kind+'-model.json'))==arm['model_sha256'],'Inference model digest')
            with np.load(root/(kind+'-paths.npz')) as trace:
                audits.append(independent.audit_paths(randoms,trace,summary['T']))
                lo[kind]=trace['center_lo'];hi[kind]=trace['center_hi'];cashlo[kind]=trace['cost_lo'];cashhi[kind]=trace['cost_hi']
                need(np.all(lo[kind]>=0) and np.all(lo[kind]<=hi[kind]),'Centered endpoint order')
                G[kind]=F(arm['accounts'][0]['center_upper_exact'])
                need(np.all(hi[kind]<=r.q.up(G[kind])),'Centered support')
                for account in arm['accounts']:
                    bounds=list(map(F,account['local_bounds_exact']))
                    need(sum(r.B**t*v for t,v in enumerate(bounds))==G[kind],'Local-to-global support')
    rows=[]
    for a,b in itertools.combinations(summary['arms'],2):
        name=a+'-minus-'+b;diff=r.I(lo[a],hi[a])-r.I(lo[b],hi[b])
        result=center.bounded_interval(diff.lo,diff.hi,-G[b],G[a]);need(result==summary['centered'][name],'Centered interval replay '+name)
        raw=r.I(cashlo[a],cashhi[a])-r.I(cashlo[b],cashhi[b]);H=old.support(summary['T'])
        expected=old.infer_interval(np.maximum(-r.q.up(H),raw.lo),np.minimum(r.q.up(H),raw.hi),2*H)
        need(expected==summary['raw_cost'][name]['interval'],'Cash-cost interval replay '+name)
        width=result['interval'][1]-result['interval'][0];raw_width=expected[1]-expected[0]
        rows.append(dict(contrast=name,**result,raw_cost_interval=expected,raw_width=raw_width,centered_width=width,
            width_ratio=raw_width/width if width else None,
            numerical_allocation_met=result['mean_numerical_width']/2<=1/512,
            sampling_allocation_met=result['sampling_radius']<=1/512))
    return rows,audits

def main():
    start=time.perf_counter();binding=s.verify();catalogue=s.specs();services=[];missing=[];trajectory_audits=[];exact=[];validations=[];contrasts=[]
    for spec in catalogue:
        receipt=R/'receipts69'/(spec['key']+'.json')
        if not receipt.exists():missing.append(spec['key']);continue
        rec=old.read(receipt);need(rec['spec']==spec,'Receipt catalogue match');need(rec['source_freeze_sha256']==binding,'Receipt source binding')
        root=R/'results69'/spec['key'];file=root/'summary.json'
        need(old.sha(R/'logs69'/(spec['key']+'.log'))==rec['log_sha256'],'Process log hash')
        if file.exists():need(old.sha(file)==rec['summary_sha256'],'Summary identity')
        summary=old.read(file) if file.exists() else {'status':'missing-after-timeout'}
        row=dict(spec=spec,returned=rec['returned'],status=summary['status'],complete_process_seconds=rec['complete_process_seconds'])
        if rec['returned']:
            need(summary['status']=='returned' and summary['spec']==spec,'Returned service identity')
            check_files(root,summary['files_sha256']);row.update(training=summary.get('training'),counts=summary.get('counts'),peak_rss_kib=summary['peak_rss_kib'])
            if spec['group']!='inference':
                exact.extend(dict(spec=spec,**x) for x in exact_models(root,summary))
                trajectory_audits.extend(trajectories(root,summary))
            if spec['group']=='validation':validations.extend(dict(spec=spec,**x) for x in validation(root,summary))
            elif spec['group']=='inference':
                rows,paths=inference(root,summary);contrasts.extend(dict(d=spec['d'],T=spec['T'],**x) for x in rows);trajectory_audits.extend(paths)
                row['inference_arms']=summary['arms']
            elif spec['group']=='reuse':row['blocks']=summary['blocks'];row['initial_seconds']=summary['initial_seconds']
        else:row['exception']=summary.get('exception')
        services.append(row)
    need(not missing,'Missing prospective receipts: '+str(missing))
    reuse=[]
    for row in services:
        spec=row['spec']
        if spec['group']!='reuse' or spec['kind']=='adaptive' or not row['returned']:continue
        baseline=next(x for x in services if x['spec']['group']=='reuse' and x['spec']['kind']=='adaptive' and x['spec']['d']==spec['d'] and x['spec']['T']==spec['T'] and x['spec']['repeat']==spec['repeat'])
        if not baseline['returned']:continue
        delta=[a['cumulative_from_entry']-b['cumulative_from_entry'] for a,b in zip(row['blocks'],baseline['blocks'])]
        persistent=next((i for i in range(64) if all(v<0 for v in delta[i:])),None)
        reuse.append(dict(spec=spec,complete_process_seconds=row['complete_process_seconds'],adaptive_seconds=baseline['complete_process_seconds'],
            complete_process_win=row['complete_process_seconds']<baseline['complete_process_seconds'],persistent_crossing=persistent,
            early_persistent_crossing=persistent is not None and persistent<=48,cumulative_difference=delta))
    result=dict(status='passed',planned_services=len(catalogue),receipt_count=len(services),returned=sum(x['returned'] for x in services),
        failed_or_timed_out=sum(not x['returned'] for x in services),services=services,exact_training=exact,validation=validations,
        centered_contrasts=contrasts,reuse_comparisons=reuse,
        independent_trajectory_checks=sum(x['complete_midbin_paths_checked'] for x in trajectory_audits),
        ambiguous_midbin_cases=sum(x['conservatively_ambiguous_paths'] for x in trajectory_audits),
        independent_scope='Separate Fraction implementation checks every represented new mid-bin trajectory. No independent full-bin proof or largest inherited vector-tree reintegration is claimed.',
        new_independent_initial_path_rows=sum(x['spec']['N'] for x in services if x['spec']['group']=='inference' and x['returned']),
        all_repetitions_preserved=True,source_freeze_sha256=binding,seconds=time.perf_counter()-start)
    old.save(R/'audit/RESULT_AUDIT69.json',result)
    print(json.dumps({k:result[k] for k in ('status','planned_services','returned','failed_or_timed_out','independent_trajectory_checks','new_independent_initial_path_rows','seconds')},indent=2))
if __name__=='__main__':main()
