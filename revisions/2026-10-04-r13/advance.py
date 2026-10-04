"""Apply the second, pre-final R13 development stage exactly once."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
def patch(path,old,new):
    t=path.read_text()
    if t.count(old)!=1:raise RuntimeError(f'patch site {path}: {old[:100]} ({t.count(old)})')
    path.write_text(t.replace(old,new))
def main():
    if (R/'STAGE2.json').exists():return
    files=['sensor.py','editorial.py','test_extensions.py','work_and_sensing.tex','sensing_proof.tex','response_body.tex']
    oldresponse=R/'manuscript/response_body.tex'
    (R/'archive/response_r12_template.tex').write_bytes(oldresponse.read_bytes())
    for name in files:
        p=R/'authored'/name;dest=R/('code' if name.endswith('.py') else 'manuscript')/name
        b=p.read_text().replace('prop:r12costate','prop:r13costate').replace('prop:r12observation','prop:r13observation');dest.write_text(b)
    proto=json.loads((R/'PROTOCOL.json').read_text());proto['observation_cells']=[32,128,1024];proto['observation_fine_cells']=4096
    (R/'PROTOCOL.json').write_text(json.dumps(proto,indent=2)+'\n')
    p=R/'code/evaluation.py'
    patch(p,"spread=0.):\n    path=Path(path)","spread=0.,policy_loader=None):\n    path=Path(path)")
    patch(p,"a,c,state=old.load(path);d=state['dimension']","a,c,state=(policy_loader or old.load)(path);d=state['dimension']")
    patch(p,"row=dict(id=ident,weights=", "row=dict(policy_implementation=state.get('policy_implementation','original fitted actor'),id=ident,weights=")
    p=R/'code/test_runner.py'
    patch(p,'import test_r13,test_extra','import test_r13,test_extra,test_extensions')
    patch(p,'unittest.defaultTestLoader.loadTestsFromModule(test_extra)])','unittest.defaultTestLoader.loadTestsFromModule(test_extra),unittest.defaultTestLoader.loadTestsFromModule(test_extensions)])')
    p=R/'code/report.py'
    text=p.read_text().replace("'Mean statistic'","'Mean'").replace("'Min. lower'","'Lower'").replace("'Max. upper'","'Upper'").replace("'Max. regret'","'Regret ub.'").replace("'Min. ceiling, bp'","'Floor, bp'")
    text=text.replace("r'\\begingroup\\small\\setlength{\\tabcolsep}{4pt}'","r'\\begingroup\\small\\setlength{\\tabcolsep}{3pt}'")
    p.write_text(text)
    p=R/'code/extra_report.py'
    point="    primary=[r for r in selections if '/extra_results/' in r['_path']]"
    sensorcheck="""    sensors=[r for r in rows if r.get('record_type')=='sensor']
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
"""
    patch(p,point,sensorcheck+point)
    point="    # Seed-specific primary method contrasts are presented before aggregate comparisons."
    extra_tables="""    direct_work=[];workseed=[];workgroups=[]
    for d in PROTOCOL['dimensions']:
      for n in ([4,8] if development else PROTOCOL['fixed_work_budgets']):
       for other in ['dpo','linear']:
        pp=[r for r in pairrows if '/secondary_results/' not in r['_path'] and r['dimension']==d and evbypath[r['right']]['method']==other and f'_work{n}_' in r['id']]
        if not pp:continue
        g=dict(dimension=d,budget=n,comparator=other,pairs=len(pp),positive=sum(r['bound']['lower']>0 for r in pp),negative=sum(r['bound']['upper']<0 for r in pp),min_lower=min(r['bound']['lower'] for r in pp),max_upper=max(r['bound']['upper'] for r in pp),mean=float(np.mean([r['bound']['mean'] for r in pp])));workgroups.append(g)
        direct_work.append([d,n,other.upper(),fixed(g['mean']),fixed(g['min_lower'],'lo'),fixed(g['max_upper'],'hi'),f"{g['positive']}/{g['negative']}"])
        for rr in pp:
            seed=int(re.search(r'_s(\\d+)',rr['id']).group(1));b=rr['bound']
            workseed.append([d,n,other.upper(),seed,fixed(b['mean']),fixed(b['lower'],'lo'),fixed(b['upper'],'hi')])
    table('table_fixed_pairs.tex','Direct paired comparisons at fixed work','tab:r13workpairs','rrlrrrr',['$d$','Iter.','Other','Mean','Lower','Upper','$+/-$'],direct_work,'NBO minus the indicated method. Endpoints summarize all fixed streams; the final column counts positive lower and negative upper endpoints. Remaining pairs are inconclusive. All pairs share initial profiles and innovations, but no independence across policies is assumed.')
    table('table_fixed_seed_pairs.tex','Every fixed-work paired endpoint','tab:r13workseed','rrlrrrr',['$d$','Iter.','Other','Seed','Mean','Lower','Upper'],workseed,'No stream is selected or replaced on the final bank. These are direct pathwise differences, not differences of separate lower endpoints.')
    table('table_absolute_work.tex','Work to a common absolute regret bound','tab:r13absolutework','rlrrr',['$d$','Method','Target','Reached','Total s.'],[[r['dimension'],r['method'].upper(),fixed(r['target_regret'],digits=2),f"{r['reached']}/{len(PROTOCOL['seeds'])}",fixed(r['median_total_seconds'],digits=2) if r['median_total_seconds'] is not None else '---'] for r in regret_hitting],'Each target concerns the actual continuous-time regret upper endpoint, not safe improvement alone. Work includes earlier certificates; medians condition on attainment. Counts show nonattainment at the tested budgets.')
"""
    patch(p,point,extra_tables+point)
    patch(p,"for f in ['table_fixed_work.tex','table_accuracy_work.tex','table_mechanism.tex','table_reference_audit.tex','table_sensor.tex']:","for f in ['table_direct_seeds.tex','table_fixed_seed_pairs.tex','table_absolute_work.tex','table_mechanism.tex','table_reference_audit.tex','table_sensor.tex']:")
    patch(p,'summary=dict(**audit,work_groups=groups,','summary=dict(**audit,direct_work_groups=workgroups,work_groups=groups,')
    patch(p,"'table_fixed_work.tex','table_accuracy_work.tex','table_direct_seeds.tex','table_mechanism.tex','table_reference_audit.tex','table_sensor.tex']}","'table_fixed_work.tex','table_accuracy_work.tex','table_fixed_pairs.tex','table_fixed_seed_pairs.tex','table_absolute_work.tex','table_direct_seeds.tex','table_mechanism.tex','table_reference_audit.tex','table_sensor.tex']}")
    patch(p,"    (R/'manuscript/extra_summary.tex').write_text(narrative)","    for g in workgroups:\n        if g['comparator']=='dpo':narrative+=f\"At dimension {g['dimension']} and {g['budget']} iterations, the direct NBO-minus-policy comparison has {g['positive']} positive and {g['negative']} negative endpoints among {g['pairs']} fitted pairs. \"\n    (R/'manuscript/extra_summary.tex').write_text(narrative+'\\n')")
    # Declaration and source materialization happen before any final data.
    (R/'STAGE2.json').write_text(json.dumps(dict(stage=2,changes='protected finite sensing, explicit arithmetic, independent sensor replay, direct fixed-work tables and all-seed presentation',before_final=True),indent=2)+'\n')
if __name__=='__main__':main()
