"""Independent replay and work-frontier reporting for the R13 additions."""
from __future__ import annotations
import argparse,math,re
from collections import defaultdict
from common import *
import evaluation

def close(a,b):
    if not math.isclose(float(a),float(b),rel_tol=2e-11,abs_tol=3e-13):raise AssertionError(f'extra replay mismatch: {a} != {b}')

def collect(development=False):
    roots=[R/'extra_development'] if development else [R/'extra_results',R/'secondary_results']
    rows=[];inputs={}
    for root in roots:
        for p in sorted(root.rglob('*.json')):
            r=json.loads(p.read_text());r['_path']=str(p.relative_to(ROOT));rows.append(r);inputs[str(p.relative_to(ROOT))]=digest(p)
            if r.get('source_commit') not in [None,source()]:raise AssertionError('extra evidence executed another source')
        for p in sorted(root.rglob('*.pt')):inputs[str(p.relative_to(ROOT))]=digest(p)
        for p in sorted(root.rglob('*.npz')):inputs[str(p.relative_to(ROOT))]=digest(p)
    return rows,inputs

def verify(development=False):
    rows,inputs=collect(development);evaluations=[r for r in rows if 'bound' in r and 'constants' in r and 'weights' in r]
    pairs=[r for r in rows if 'bound' in r and 'left' in r];selections=[r for r in rows if r.get('record_type')=='work_selection']
    bypath={r['_path']:r for r in evaluations};mechanisms=[r for r in rows if r.get('record_type')=='mechanism']
    for r in selections:
        if digest(ROOT/r['weights'])!=r['weights_sha256']:raise AssertionError('fixed-work selected weights')
        if (ROOT/r['weights']).read_bytes()!=(ROOT/r['selected_checkpoint']).read_bytes():raise AssertionError('selection did not use saved prefix checkpoint')
        if r['training_state_visits']!=r['budget']*PROTOCOL['batch']*PROTOCOL['rollout_steps']:raise AssertionError('unequal announced simulator work')
        if r['selected_iteration']>r['budget']:raise AssertionError('future checkpoint leaked into prefix')
    for r in evaluations:
        p=ROOT/r['_path'];raw=p.with_suffix('.npz')
        if digest(raw)!=r['raw_sha256'] or digest(ROOT/r['weights'])!=r['weights_sha256']:raise AssertionError('extra raw/weight hash')
        with np.load(raw) as z:
            np.testing.assert_array_equal(z['production']-z['consumption_deficit']+z['terminal_gain'],z['paired_gain'])
            _,c=evaluation.account(r['dimension'],r['steps'],r['epsilon'],r['design'],r['shift'],r['spread'])
            for k in ['bias_upper','clipping_threshold','clipping_bias','anchor_upper']:close(c[k],r['constants'][k])
            b=pc.empirical_lower(z['paired_gain'],c['clipping_threshold'],c['bias_upper'],c['clipping_bias'],PROTOCOL['one_sided_family_size'],PROTOCOL['alpha'])
            for k in ['mean','lower','upper','sample_sd','empirical_bernstein_margin']:close(b[k],r['bound'][k])
    for r in pairs:
        a=bypath[r['left']];b=bypath[r['right']]
        for k in ['dimension','design','steps','paths','initial_state_hash','initial_index_hash','noise_seed','noise_sha256']:
            if a[k]!=b[k]:raise AssertionError('unpaired fixed-work rows')
        rp=(ROOT/r['_path']).with_suffix('.npz')
        if digest(rp)!=r['raw_sha256']:raise AssertionError('paired hash')
        with np.load((ROOT/a['_path']).with_suffix('.npz')) as x,np.load((ROOT/b['_path']).with_suffix('.npz')) as y,np.load(rp) as z:
            np.testing.assert_array_equal(x['terminal_anchor'],y['terminal_anchor']);np.testing.assert_array_equal(x['paired_gain']-y['paired_gain'],z['paired_difference'])
            I=pc.I;ca,cb=a['constants'],b['constants']
            bias=float((I(ca['actor_bias_upper'])+I(cb['actor_bias_upper'])+I(ca['statistic_error_upper'])+I(cb['statistic_error_upper'])+I(1e-12)).hi)
            clip=float((I(ca['clipping_threshold'])+I(cb['clipping_threshold'])).hi);tail=float((I(ca['clipping_bias'])+I(cb['clipping_bias'])).hi)
            bb=pc.empirical_lower(z['paired_difference'],clip,bias,tail,PROTOCOL['one_sided_family_size'],PROTOCOL['alpha'])
            for k in ['mean','lower','upper']:close(bb[k],r['bound'][k])
    for r in mechanisms:
        p=(ROOT/r['_path']).with_suffix('.npz')
        if digest(p)!=r['raw_sha256'] or digest(ROOT/r['weights'])!=r['weights_sha256']:raise AssertionError('mechanism identity')
        with np.load(p) as z:
            fine=max(int(k.split('_n')[1]) for k in z.files if k.startswith('q_b0_n'))
            a=z[f'q_b0_n{fine}'];b=z[f'q_b1_n{fine}'];q=z['critic_costate'];qa=a.mean(1);qb=b.mean(1)
            close(np.mean((a-b)**2)/2,r['rollout_costate_variance']);close(np.mean((q-qa)*(q-qb)),r['regression_mse_unbiased_estimate'])
            def H(q,m):return np.log(m).mean(1)-P['adjustment']/2*m.mean(1)**2-(q*m).mean(1)
            g=np.maximum(0,H(qa,z['reference_greedy'])-H(qa,z['actor_action']))
            np.testing.assert_allclose(g,z['action_loss'],atol=1e-12,rtol=1e-11)
            if np.any(g>z['mechanism_upper']+2e-10):raise AssertionError('mechanism bound violation')
            close(g.mean(),r['mean_actor_hamiltonian_loss'])
    sensors=[r for r in rows if r.get('record_type')=='sensor']
    from sensor import allowance
    for r in sensors:
        if digest(ROOT/r['raw_file'])!=r['raw_sha256'] or digest(ROOT/r['weights'])!=r['weights_sha256']:raise AssertionError('sensor source identity')
        with np.load(ROOT/r['raw_file']) as raw:
            for s in r['rows']:
                cc=allowance(ROOT/r['weights'],s['cells'],s['sensor_noise_rms'])
                for key in ['node_error_upper','action_error_upper','physical_error_upper','payoff_difference_upper']:close(cc[key],s['allowance'][key])
                close(raw[s['id']].mean(),s['mean_sensor_minus_ideal'])
                parent=bypath[s['protected_parent']]
                if parent['steps']!=s['cells'] or not parent.get('policy_implementation','').startswith('protected'):raise AssertionError('sensor parent is a different implementation')
                close((pc.I(parent['bound']['lower'])-pc.I(cc['payoff_difference_upper'])).lo,s['transferred_improvement_lower'])
    if not development:
        for folder,seeds in [('extra_results',PROTOCOL['seeds']),('secondary_results',[PROTOCOL['auxiliary_seed']])]:
            found={p.parent.name for p in (R/folder).glob('*/EXECUTION.json')}
            if found!=set(map(str,seeds)):raise AssertionError('missing fixed-work execution ledger')
        if len(sensors)!=2:raise AssertionError('missing finite-observation audit')
    primary=[r for r in selections if '/extra_results/' in r['_path']]
    secondary=[r for r in selections if '/secondary_results/' in r['_path']]
    if not development:
        expected={(d,s,m,n) for d in PROTOCOL['dimensions'] for s in PROTOCOL['seeds'] for m in PROTOCOL['methods'] for n in PROTOCOL['fixed_work_budgets']}
        found={(r['dimension'],r['seed'],r['method'],r['budget']) for r in primary}
        if found!=expected:raise AssertionError('fixed-work family incomplete')
        if len(secondary)!=12:raise AssertionError('secondary environment incomplete')
        for root in ['extra_results','secondary_results']:
            for p in (R/root).glob('*/EXECUTION.json'):
                if not json.loads(p.read_text())['success']:raise AssertionError('failed extra worker')
            for p in (R/root).glob('*/ENVIRONMENT.json'):
                env=json.loads(p.read_text());current={str(q.relative_to(ROOT)):digest(q) for q in (R/'code').glob('*.py')}
                if env['source_commit']!=source() or env['source_files']!=current or env['protocol_sha256']!=digest(R/'PROTOCOL.json'):raise AssertionError('worker source drift')
    base=R/('development' if development else 'results')/'AUDIT.json'
    original=json.loads(base.read_text())
    used=original['one_sided_used']+2*(len(evaluations)+len(pairs))
    if used>PROTOCOL['one_sided_family_size']:raise AssertionError('joint family exhausted')
    manifest=R/'EXTRA_TABLE_MANIFEST.json'
    if manifest.exists():
        mm=json.loads(manifest.read_text())
        for group in ['inputs','outputs']:
            for p,h in mm[group].items():
                if digest(ROOT/p)!=h:raise AssertionError('extra table binding '+p)
    return dict(source_commit=source(),development=development,fixed_work_selections=len(primary) if not development else len(selections),
        secondary_selections=len(secondary),additional_evaluations=len(evaluations),additional_pairs=len(pairs),mechanism_records=len(mechanisms),
        total_one_sided_used=used,allocated=PROTOCOL['one_sided_family_size'],all_raw_arrays_replayed=True,
        scope='Primary and fixed-work intervals share one preallocated family. Mechanism and finite-Euler sensing checks remain diagnostics; descriptive seed comparisons are not optimizer-population inference.')

def reference_details(base):
    p=base/'reference/REFERENCE.json'
    if not p.exists():return []
    record=json.loads(p.read_text());rows=[];arrays=[]
    for r in record['records']:
        path=p.parent/(r['id']+'.npz')
        with np.load(path) as z:
            y=z['state'];central=(y>=-1)&(y<=1);losses={m:float(np.max(z['optimal'][central]-z[m][central])) for m in ['nbo','dpo','linear','anchor']}
            points={m:np.interp([-1,-.5,0,.5,1],y,z['optimal']-z[m]).tolist() for m in ['nbo','dpo','linear','anchor']}
            rows.append(dict(id=r['id'],nx=r['nx'],nt=r['nt'],domain=r['L'],max_central_policy_loss=losses,point_losses=points,
                max_equation_residual=r['max_equation_residual'],fixed_policy_residuals=r.get('fixed_policy_residuals',{}),action_bound_counts=r.get('action_bound_counts',{})))
            arrays.append({k:z[k].copy() for k in z.files})
    for i in range(1,len(rows)):
        a,b=arrays[i-1],arrays[i];grid=np.linspace(-1,1,401)
        rows[i]['previous_grid_central_value_change']=float(np.max(abs(np.interp(grid,a['state'],a['optimal'])-np.interp(grid,b['state'],b['optimal']))))
        ya=a['state'][1:-1];yb=b['state'][1:-1]
        rows[i]['previous_grid_central_action_change']=float(np.max(abs(np.interp(grid,ya,a['optimal_action_t0'])-np.interp(grid,yb,b['optimal_action_t0']))))
    return rows

def run(development=False):
    from report import table,fixed
    # A previously generated manifest may not bind a newly generated table yet.
    old_manifest=R/'EXTRA_TABLE_MANIFEST.json'
    if old_manifest.exists():old_manifest.unlink()
    audit=verify(development);rows,inputs=collect(development);base=R/('development' if development else 'results')
    selections=[r for r in rows if r.get('record_type')=='work_selection' and '/secondary_results/' not in r['_path']]
    evaluations=[r for r in rows if 'constants' in r and 'bound' in r and 'weights' in r];byweights={r['weights']:r for r in evaluations}
    pairrows=[r for r in rows if 'left' in r and 'bound' in r];evbypath={r['_path']:r for r in evaluations}
    groups=[];tr=[]
    for d in PROTOCOL['dimensions']:
      for m in PROTOCOL['methods']:
       for n in ([4,8] if development else PROTOCOL['fixed_work_budgets']):
        ss=[r for r in selections if (r['dimension'],r['method'],r['budget'])==(d,m,n)]
        if not ss:continue
        ee=[byweights[s['weights']] for s in ss];fit=np.median([s['fit_seconds'] for s in ss]);vt=np.median([e['seconds'] for e in ee])
        g=dict(dimension=d,method=m,budget=n,seeds=len(ss),min_lower=min(e['bound']['lower'] for e in ee),max_regret=max(e['policy_regret_upper'] for e in ee),fit_seconds=float(fit),verify_seconds=float(vt));groups.append(g)
        tr.append([d,m.upper(),n,fixed(g['min_lower'],'lo'),fixed(g['max_regret'],'hi'),fixed(fit,digits=2),fixed(vt,digits=2)])
    table('table_fixed_work.tex','Fixed simulator-work and iteration comparisons','tab:r13fixed','rlrrrrr',['$d$','Method','Iterations','Min. lower','Max. regret','Fit s.','Verify s.'],tr,
        'Every iteration uses the same 128 state vectors and 32 rollout cells. Validation occurs every 20 iterations. Thus simulator visits, validation visits and iteration counts match; critic and actor updates, arithmetic work and wall time do not. Bounds include the full independent certification cost.')
    hitting=[];tr=[]
    for d in PROTOCOL['dimensions']:
      for m in PROTOCOL['methods']:
       for target in PROTOCOL['accuracy_gain_targets']:
        costs=[];visits=[];reached=0
        for seed in PROTOCOL['seeds']:
            ss=sorted([s for s in selections if (s['dimension'],s['method'],s['seed'])==(d,m,seed)],key=lambda s:s['budget'])
            verify_cost=0.;verify_visits=0
            for s in ss:
                e=byweights[s['weights']];verify_cost+=e['seconds'];verify_visits+=2*e['paths']*e['steps']
                if e['bound']['lower']>=target:
                    costs.append(s['fit_seconds']+verify_cost);visits.append(s['training_state_visits']+s['validation_state_visits']+verify_visits);reached+=1;break
        if not selections:continue
        hitting.append(dict(dimension=d,method=m,target_gain=target,reached=reached,streams=len(PROTOCOL['seeds']),median_total_seconds=float(np.median(costs)) if costs else None,median_total_state_visits=float(np.median(visits)) if visits else None))
        if target==.0005:tr.append([d,m.upper(),f'{reached}/{len(PROTOCOL["seeds"])}',fixed(np.median(costs),digits=2) if costs else '---',fixed(np.median(visits)/1e6,digits=2) if visits else '---'])
    table('table_accuracy_work.tex','Total tested work to a common improvement endpoint','tab:r13accuracy','rlrrr',['$d$','Method','Reached','Total s.','Visits, mln.'],tr,
        'Target: simultaneous schedule-improvement lower endpoint at least 0.0005. Test the 80- then 160-iteration prefixes in that order. Cost includes the consumed fitting prefix and every certificate inspected up to the first success, including earlier unsuccessful certificates. Medians condition on success; counts expose censoring. This is a tested-budget hitting-cost comparison, not an extrapolated optimum or evidence of HJB accuracy.')
    # The absolute criterion is reported separately and never replaced by safe improvement.
    regret_hitting=[]
    for d in PROTOCOL['dimensions']:
      for m in PROTOCOL['methods']:
       for target in PROTOCOL['accuracy_regret_targets']:
        count=0;costs=[]
        for seed in PROTOCOL['seeds']:
            ss=sorted([s for s in selections if (s['dimension'],s['method'],s['seed'])==(d,m,seed)],key=lambda s:s['budget']);vc=0.
            for s in ss:
                e=byweights[s['weights']];vc+=e['seconds']
                if e['policy_regret_upper']<=target:count+=1;costs.append(s['fit_seconds']+vc);break
        regret_hitting.append(dict(dimension=d,method=m,target_regret=target,reached=count,median_total_seconds=float(np.median(costs)) if costs else None))
    direct_work=[];workseed=[];workgroups=[]
    for d in PROTOCOL['dimensions']:
      for n in ([4,8] if development else PROTOCOL['fixed_work_budgets']):
       for other in ['dpo','linear']:
        pp=[r for r in pairrows if '/secondary_results/' not in r['_path'] and r['dimension']==d and evbypath[r['right']]['method']==other and f'_work{n}_' in r['id']]
        if not pp:continue
        g=dict(dimension=d,budget=n,comparator=other,pairs=len(pp),positive=sum(r['bound']['lower']>0 for r in pp),negative=sum(r['bound']['upper']<0 for r in pp),min_lower=min(r['bound']['lower'] for r in pp),max_upper=max(r['bound']['upper'] for r in pp),mean=float(np.mean([r['bound']['mean'] for r in pp])));workgroups.append(g)
        direct_work.append([d,n,other.upper(),fixed(g['mean']),fixed(g['min_lower'],'lo'),fixed(g['max_upper'],'hi'),f"{g['positive']}/{g['negative']}"])
        for rr in pp:
            seed=int(re.search(r'_s(\d+)',rr['id']).group(1));b=rr['bound']
            workseed.append([d,n,other.upper(),seed,fixed(b['mean']),fixed(b['lower'],'lo'),fixed(b['upper'],'hi')])
    table('table_fixed_pairs.tex','Direct paired comparisons at fixed work','tab:r13workpairs','rrlrrrr',['$d$','Iter.','Other','Mean','Lower','Upper','$+/-$'],direct_work,'NBO minus the indicated method. Endpoints summarize all fixed streams; the final column counts positive lower and negative upper endpoints. Remaining pairs are inconclusive. All pairs share initial profiles and innovations, but no independence across policies is assumed.')
    table('table_fixed_seed_pairs.tex','Every fixed-work paired endpoint','tab:r13workseed','rrlrrrr',['$d$','Iter.','Other','Seed','Mean','Lower','Upper'],workseed,'No stream is selected or replaced on the final bank. These are direct pathwise differences, not differences of separate lower endpoints.')
    table('table_absolute_work.tex','Work to a common absolute regret bound','tab:r13absolutework','rlrrr',['$d$','Method','Target','Reached','Total s.'],[[r['dimension'],r['method'].upper(),fixed(r['target_regret'],digits=2),f"{r['reached']}/{len(PROTOCOL['seeds'])}",fixed(r['median_total_seconds'],digits=2) if r['median_total_seconds'] is not None else '---'] for r in regret_hitting],'Each target concerns the actual continuous-time regret upper endpoint, not safe improvement alone. Work includes earlier certificates; medians condition on attainment. Counts show nonattainment at the tested budgets.')
    # Seed-specific primary method contrasts are presented before aggregate comparisons.
    primary_pairs=[];primary_evals={}
    for p in sorted(base.rglob('*.json')):
        r=json.loads(p.read_text())
        if 'weights' in r and 'constants' in r:primary_evals[str(p.relative_to(ROOT))]=r
        elif 'bound' in r and 'left' in r:primary_pairs.append(r)
    seedrows=[]
    for r in primary_pairs:
        other=primary_evals[r['right']]['method']
        if other!='dpo':continue
        seed=int(re.search(r'_s(\d+)',r['id']).group(1));b=r['bound'];sign='positive' if b['lower']>0 else ('negative' if b['upper']<0 else 'inconclusive')
        seedrows.append([r['dimension'],'P' if r['design']=='population' else '0',seed,fixed(b['mean']),fixed(b['lower'],'lo'),fixed(b['upper'],'hi'),sign])
    seedrows.sort(key=lambda r:(r[0],r[1],r[2]))
    table('table_direct_seeds.tex','Each primary NBO-minus-direct-policy comparison','tab:r13seeds','rlrrrrl',['$d$','State','Seed','Mean','Lower','Upper','Sign'],seedrows,
        'P is the nine-profile population and 0 is the origin. Every endpoint is formed from the direct pathwise difference and uses the joint finite-family allocation. All fixed streams are shown. The sign is a statement about the fitted pair, not the distribution of unseen optimization seeds.')
    mechanism_rows=[r for r in rows if r.get('record_type')=='mechanism'];tr=[]
    for r in mechanism_rows:
        if r['method']!='nbo':continue
        tag=Path(r['weights']).stem.split('_s')[1].split('_',1)[-1]
        tr.append([r['dimension'],tag.replace('_','-'),f"{r['rollout_costate_variance']:.2e}",f"{r['regression_mse_unbiased_estimate']:.2e}",f"{r['mean_actor_hamiltonian_loss']:.2e}"])
    table('table_mechanism.tex','Independent evaluation-to-improvement diagnostics','tab:r13mechanism','rlrrr',['$d$','Fit','Target variance','Cross-bank MSE','Action loss'],tr,
        'Targets use two independent banks at the same held-out states; nested time grids measure sensitivity of the rollout costate. The cross-bank estimate removes target-mean noise in expectation and may be negative. Action loss is relative to an independently estimated finite-rollout costate, not the continuous-time optimal costate. Full arrays, standard-error diagnostics and the pathwise mechanism inequality are retained.')
    ref=reference_details(base);write(R/'REFERENCE_DIAGNOSTICS.json',dict(source_commit=source(),records=ref));tr=[]
    for r in ref:tr.append([r['nx'],r['nt'],r['domain'],f"{r['max_equation_residual']:.2e}",fixed(r['max_central_policy_loss']['nbo']),fixed(r['max_central_policy_loss']['dpo'])])
    table('table_reference_audit.tex','Reference residuals and losses away from the center','tab:r13reference','rrrrrr',['Nodes','Cells','$L$','Residual','NBO max. loss','DPO max. loss'],tr,
        'Policy losses are maxima over grid nodes in [-1,1]. The machine-readable audit reports five distinct initial states, adjacent-grid value and action changes, each fixed-policy residual and action-bound frequencies. Boundary-domain changes remain a sensitivity check, not an unproved continuous-state error rate.')
    sensors=[r for r in rows if r.get('record_type')=='sensor'];tr=[]
    for r in sensors:
      for s in r['rows']:
        tr.append([s['dimension'],s['cells'],s['sensor_noise_rms'],f"{s['mean_sensor_minus_ideal']:.3e}",f"{s['allowance']['payoff_difference_upper']:.3e}"])
    table('table_sensor.tex','Finite-observation implementation and transfer allowance','tab:r13sensor','rrrrr',['$d$','Cells','Noise RMS','Euler difference','Transfer bound'],tr,
        'The fourth column is only a shared-noise fine-Euler diagnostic. The last column is a separate weight-dependent theoretical allowance under the stated sensing and arithmetic conditions. A large allowance is retained; no finite sensing error is silently set to zero.')
    primary_sel={s['weights'].split('/')[-1]:s for s in selections};secondary=[]
    for s in [r for r in rows if r.get('record_type')=='work_selection' and '/secondary_results/' in r['_path']]:
        a=primary_sel.get(Path(s['weights']).name)
        if a:
            w1=torch.load(ROOT/a['weights'],weights_only=True,map_location='cpu');w2=torch.load(ROOT/s['weights'],weights_only=True,map_location='cpu')
            diff=max(float((w1['actor'][k]-w2['actor'][k]).abs().max()) for k in w1['actor'])
            secondary.append(dict(dimension=s['dimension'],method=s['method'],budget=s['budget'],selected_iterations=[a['selected_iteration'],s['selected_iteration']],max_actor_weight_difference=diff,first_fit_seconds=a['fit_seconds'],second_fit_seconds=s['fit_seconds'],endpoint_difference=byweights[s['weights']]['bound']['lower']-byweights[a['weights']]['bound']['lower']))
    full='\\section{Fixed Work, Independent Costate Checks, and Sensing}\n'
    for f in ['table_direct_seeds.tex','table_fixed_seed_pairs.tex','table_absolute_work.tex','table_mechanism.tex','table_reference_audit.tex','table_sensor.tex']:
        full+='\\input{revisions/2026-10-04-r13/manuscript/'+f+'}\n'
    (R/'manuscript/extra_full_results.tex').write_text(full)
    summary=dict(**audit,direct_work_groups=workgroups,work_groups=groups,improvement_hitting_costs=hitting,absolute_regret_hitting_costs=regret_hitting,secondary_environment=secondary)
    write(R/'EXTRA_AUDIT.json',summary)
    narrative=(f'The fixed-work record contains {len(selections)} budget-specific selected policies and retains every prefix checkpoint. '
        f'The combined primary and additional verification uses {audit["total_one_sided_used"]} of the {audit["allocated"]} allocated one-sided statements. '
        'Work-to-target results include unsuccessful earlier verification attempts; unachieved targets are not assigned zero cost. '
        'The independent costate diagnostics and finite-Euler sensing checks are not substituted for the continuous-time policy endpoints.\n')
    for g in workgroups:
        if g['comparator']=='dpo':narrative+=f"At dimension {g['dimension']} and {g['budget']} iterations, the direct NBO-minus-policy comparison has {g['positive']} positive and {g['negative']} negative endpoints among {g['pairs']} fitted pairs. "
    (R/'manuscript/extra_summary.tex').write_text(narrative+'\n')
    outputs={str(p.relative_to(ROOT)):digest(p) for p in (R/'manuscript').glob('table_*.tex') if p.name in ['table_fixed_work.tex','table_accuracy_work.tex','table_fixed_pairs.tex','table_fixed_seed_pairs.tex','table_absolute_work.tex','table_direct_seeds.tex','table_mechanism.tex','table_reference_audit.tex','table_sensor.tex']}
    for name in ['extra_full_results.tex','extra_summary.tex']:outputs[str((R/'manuscript'/name).relative_to(ROOT))]=digest(R/'manuscript'/name)
    # Bind primary direct-seed and independent reference sources as well as extras.
    for p in base.rglob('*'):
        if p.is_file() and p.suffix in ['.json','.npz'] and p.name not in ['COMPILATION.json','TESTS.json','INHERITED_TESTS.json']:
            inputs[str(p.relative_to(ROOT))]=digest(p)
    write(R/'EXTRA_TABLE_MANIFEST.json',dict(source_commit=source(),development=development,inputs=inputs,outputs=outputs))
    print(json.dumps(summary,indent=2));return summary
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--development',action='store_true');a=p.parse_args();run(a.development)
