"""Final ordinary author edits based on the immutable completed catalogue.

No scientific output, original clock, fitted policy or frozen source changes.
Every explicit numerical interpretation is derived from the full five-task,
four-seed catalogue, not from a selected favorable observation.
"""
from pathlib import Path
from decimal import Decimal,ROUND_CEILING
import hashlib,json
R=Path(__file__).resolve().parents[1]
SEEDS=(6201,6202,6203,6204)
TASKS=('d2-m1-T2','d2-m1-T3','d4-m1-T3','d8-m1-T2','d2-m2-T2')

def read(p):return json.loads(Path(p).read_text())
def sha(text):return hashlib.sha256(text.encode()).hexdigest()
def upper(v):return format(Decimal.from_float(float(v)).quantize(Decimal('0.00001'),rounding=ROUND_CEILING),'f')
def main():
    marker=R/'audit/RESULT_INTERPRETATION62.json'
    if marker.exists():print('Full-catalogue interpretation and supplementary layout already retained.');return
    if (R/'audit/SOURCE_BINDING62.json').exists():raise RuntimeError('Do not silently replace a final source binding')
    import science62
    fz=science62.verify();records={};bounds={};counts={'pure_higher':0,'pure_lower':0,'pure_unresolved':0,'augmented_unresolved':0,'augmented_identity':0,'augmented_higher':0,'augmented_lower':0,'pure_minus_augmented_positive':0};reference_files={}
    for task in TASKS:
        folder=R/'results62'/task;s=read(folder/'summary.json');cost=read(folder/'costs.json')
        reference_files[task]={'summary_sha256':science62.c.digest(folder/'summary.json'),'costs_sha256':science62.c.digest(folder/'costs.json')}
        ref=read(folder/('n'+str(s['ladder'][-1]))/'reference.json');bounds[task]=ref['policy_certificate']['maximum_date_gap_upper']
        for seed in SEEDS:
            for variant in ('pure','guarded'):
                rec=cost['contrasts'][f'relu-{seed}-{variant}-minus-common'];lo,hi=rec['interval'];prefix='pure' if variant=='pure' else 'augmented'
                outcome='higher' if lo>0 else 'lower' if hi<0 else 'identity' if rec.get('identity',False) else 'unresolved'
                counts[prefix+'_'+outcome]=counts.get(prefix+'_'+outcome,0)+1
            gain=cost['contrasts'][f'relu-{seed}-pure-minus-guarded']['interval']
            counts['pure_minus_augmented_positive']+=int(gain[0]>0)
        records[task]={'common_final_all_state_bound':bounds[task],'targets':s['targets']['common']}
    if counts['pure_higher']!=20 or counts['augmented_unresolved']!=20:raise AssertionError('The interpreted result pattern differs from the complete frozen catalogue')
    accuracy=('At the final declared rungs, the common and common-augmented policies attain the $1/32$ target in both two-state scalar cells and in the complete two-control cell. The four-state, three-date bound is $'+upper(bounds['d4-m1-T3'])+'$, which attains $1/16$. The eight-state bound is $'+upper(bounds['d8-m1-T2'])+'$: that cell attains $1/2$ but exhausts its declared budget at the four smaller targets. These are whole-domain, all-date loss bounds for the actual acquired actors, rather than initial-law average gains. The pure ReLU bounds remain distinct and materially larger; finer verification alone does not remove the loss of a fixed fitted proposal.')
    economic=('The full catalogue gives a clear empirical ordering. All twenty pure-ReLU-minus-common intervals are strictly positive: in each declared task and seed, the pure fitted controller has higher expected cost than the common comparator. All twenty augmented-ReLU-minus-common intervals contain zero and therefore do not rank those two controllers. The augmented variants attain the shared original-optimum accuracy contracts, but this is not evidence of a neural cost advantage. The improvement is in completing a verifiable NBO policy construction and in quantifying the contribution and cost of its fallback, not in overturning the observed conventional ranking.')
    if counts['pure_minus_augmented_positive']>0:
        economic+=(' In '+str(counts['pure_minus_augmented_positive'])+' of the twenty pure-versus-augmented comparisons, the paired gain interval has a positive lower endpoint. These identified replacement gains concern the actual fitted incumbent and its augmented replacement; they are not gains over the common comparator.')
    changes=[]
    def edit(name,before,after):
        path=R/name;old=path.read_text()
        if old.count(before)!=1:raise AssertionError('Expected unique author text not found: '+name)
        new=old.replace(before,after,1);path.write_text(new);changes.append({'file':name,'before_sha256':sha(old),'after_sha256':sha(new)})
    edit('sections/study62.tex',r'\input{tables/accuracy62}',r'\input{tables/accuracy62}'+'\n\n'+r'\paragraph{Attained accuracy and exhausted budgets.}'+'\n'+accuracy+'\n')
    edit('sections/study62.tex',r'\input{tables/comparisons62}',r'\input{tables/comparisons62}'+'\n\n'+r'\paragraph{Economic findings.}'+'\n'+economic+'\n')
    response=('## Full-catalogue findings submitted for review\n\n'+accuracy.replace('$','')+'\n\n'+economic+'\n\n')
    for name in ('response62.md','response.md'):
        title='## Verification, preservation and renewed review';edit(name,title,response+title)
    edit('code/tables62.py','retained in PUBLICATION_FACTS62.json.','retained in the machine-readable publication facts.')
    old="""            rows.append([names[t['task']],r['n'],dec(r['common_gap']),span([r['methods'][f'relu-{s}-pure'] for s in seeds]),span([r['methods'][f'relu-{s}-guarded'] for s in seeds]),span([r['methods'][f'quadratic-{s}-pure'] for s in seeds]),span([r['methods'][f'quadratic-{s}-guarded'] for s in seeds])])
    longtable('rungs62','All original-optimum refinement rungs','tab:rungs62',
        ['$d/m/T$','$n$','Common','Pure R','Aug. R','Pure Q','Aug. Q'],rows,
        'Upper-bound ranges cover every fixed seed. Complete nodal arrays, exact error recursions, interpolation and quadrature allowances, action discretization allowances, and deployment errors are retained for each entry.','rrrcccc')"""
    new="""            for variant in ('pure','guarded'):
                rows.append([names[t['task']],r['n'],'Pure' if variant=='pure' else 'Augmented',dec(r['common_gap']),span([r['methods'][f'relu-{s}-{variant}'] for s in seeds]),span([r['methods'][f'quadratic-{s}-{variant}'] for s in seeds])])
    longtable('rungs62','All original-optimum refinement rungs','tab:rungs62',
        ['$d/m/T$','$n$','Variant','Common','ReLU range','Quadratic range'],rows,
        'Both variants and every rung are retained. Upper-bound ranges cover every fixed seed. Complete nodal arrays, exact error recursions, interpolation and quadrature allowances, action discretization allowances, and deployment errors are retained for each entry.','rrlrcc')"""
    edit('code/tables62.py',old,new)
    if science62.verify()!=fz:raise AssertionError('Author edits changed frozen science')
    marker.write_text(json.dumps(dict(status='retained',source_freeze_sha256=fz,cost_comparison_counts=counts,task_findings=records,source_records=reference_files,changes=changes,scope='Interpretations derived from every declared task and seed. Printed whole-domain upper bounds round upward. Ordinary manuscript and table layout only; frozen theory, production data, actions, target definitions and clocks are unchanged.'),sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(status='retained',counts=counts,common_final_bounds=bounds)),flush=True)
if __name__=='__main__':main()
