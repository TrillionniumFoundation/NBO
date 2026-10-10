"""All R62 publication numbers are derived from the completed record replay."""
from pathlib import Path
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
from fractions import Fraction as F
import json
R=Path(__file__).resolve().parents[1]

def dec(x,lower=False,d=5):
    val=Decimal.from_float(float(x));quantum=Decimal(10)**(-d)
    return format(val.quantize(quantum,rounding=ROUND_FLOOR if lower else ROUND_CEILING),'f')
def band(v):return '['+dec(v[0],True)+', '+dec(v[1])+']'
def span(values):return dec(min(values))+'--'+dec(max(values))
def put(name,text):
    if name.endswith('.tex') and any(ord(z)<32 and z not in '\n\r\t' for z in text):raise ValueError(name)
    p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def table(name,caption,label,heads,rows,note,cols):
    text='\\begin{table}[htbp]\n\\centering\n\\caption{'+caption+'}\\label{'+label+'}\n{\\small\\setlength{\\tabcolsep}{3pt}\n\\begin{tabular}{'+cols+'}\n\\hline\n'
    text+=' & '.join(heads)+r' \\'+'\n\\hline\n'
    text+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
    text+='\n\\hline\n\\end{tabular}}\n\\par\\smallskip\n{\\footnotesize '+note+'}\n\\end{table}\n'
    put('tables/'+name+'.tex',text)
def longtable(name,caption,label,heads,rows,note,cols):
    head=' & '.join(heads)+r' \\'
    text='{\\small\\setlength{\\tabcolsep}{3pt}\n\\begin{longtable}{'+cols+'}\n\\caption{'+caption+'}\\label{'+label+r'} \\'+'\n\\hline\n'+head+'\n\\hline\\endfirsthead\n\\hline\n'+head+'\n\\hline\\endhead\n'
    text+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
    text+='\n\\hline\n\\end{longtable}}\n{\\footnotesize '+note+'}\n'
    put('tables/'+name+'.tex',text)
def main():
    a=json.loads((R/'audit/SCIENCE_REPLAY62.json').read_text());tasks=a['tasks'];seeds=(6201,6202,6203,6204)
    names={t['task']:f'{t["d"]}/{t["m"]}/{t["T"]}' for t in tasks};rows=[]
    for t in tasks:
        r=t['rungs'][-1]
        rows.append([names[t['task']],r['n'],dec(r['common_gap']),span([r['methods'][f'relu-{s}-pure'] for s in seeds]),span([r['methods'][f'relu-{s}-guarded'] for s in seeds]),span([r['methods'][f'quadratic-{s}-guarded'] for s in seeds])])
    table('accuracy62','Whole-domain loss against the original continuous-action optimum','tab:accuracy62',
        ['$d/m/T$','$n$','Common','Pure ReLU','Augmented ReLU','Augmented quad.'],rows,
        'Each number bounds the maximum loss over all true states and all dates of the actual acquired, downward-rounded policy. Ranges are the minimum and maximum bound over all four fitting seeds, not confidence intervals. All displayed upper bounds are rounded upward. The common construction and every fitted actor use the same original-optimum reference.','rrrccc')
    rows=[]
    for t in tasks:
        for seed in seeds:
            v=t['costs']['contrasts'];rows.append([names[t['task']],seed,band(v[f'relu-{seed}-pure-minus-common']['interval']),band(v[f'relu-{seed}-guarded-minus-common']['interval'])])
    table('comparisons62','Direct expected-cost contrasts for every neural seed','tab:comparisons62',
        ['$d/m/T$','Seed','Pure ReLU minus common','Augmented ReLU minus common'],rows,
        'Negative intervals identify lower neural-policy cost; intervals containing zero do not rank policies. These are paired original-law cost intervals for complete final-rung actors. All five tasks and four seeds are retained on one simultaneous coverage event. Exact identity intervals are zero, not new independent observations. The supplement also reports every quadratic contrast and every marginal cost.','rrcc')
    rows=[]
    for t in tasks:
        w=t['full_catalogue_release_work_seconds'];rl=[w[f'relu-{s}-guarded'] for s in seeds];ql=[w[f'quadratic-{s}-guarded'] for s in seeds]
        rows.append([names[t['task']],dec(w['common'],d=2),span(rl),span(ql),dec(t['reference_cumulative_seconds'],d=2)])
    table('release-work62','Recorded work through complete catalogue release','tab:release-work62',
        ['$d/m/T$','Common (s)','ReLU (s)','Quadratic (s)','Reference (s)'],rows,
        'Every method is charged the entire shared reference, all preceding rungs, its own fitting/proposal and verification work, full shared cost inference, and cold native compilation. Pure and augmented variants are jointly verified and each is conservatively charged the full joint work. This is measured catalogue-release work, not an unexecuted minimal stopping schedule. Times are one-host descriptive measurements; frequency was not controlled.','r r c c r')
    rows=[];frontier=[]
    for t in tasks:
        for tol in ('1/2','1/4','1/8','1/16','1/32'):
            counts={}
            for kind in ('relu','quadratic'):
                for v in ('pure','guarded'):
                    counts[kind+'-'+v]=sum(next(r for r in t['targets'][f'{kind}-{s}-{v}'] if r['tolerance']==tol)['status']=='attained' for s in seeds)
            common=next(r for r in t['targets']['common'] if r['tolerance']==tol)
            eligible=[k for k,rr in t['targets'].items() if next(r for r in rr if r['tolerance']==tol)['status']=='attained']
            best=min(eligible,key=lambda k:t['full_catalogue_release_work_seconds'][k]) if eligible else None
            frontier.append(dict(task=t['task'],tolerance=tol,eligible=eligible,least_recorded_complete_release_method=best))
            rows.append([names[t['task']],tol,'yes' if common['status']=='attained' else 'no',*(str(counts[k])+'/4' for k in ('relu-pure','relu-guarded','quadratic-pure','quadratic-guarded'))])
    longtable('targets62','Every declared tolerance and finite-seed attainment count','tab:targets62',
        ['$d/m/T$','Tolerance','Common','Pure R','Aug. R','Pure Q','Aug. Q'],rows,
        'R and Q denote trained ReLU and fitted quadratic proposals. A fraction is an exact count over the four declared seeds; it is not a population probability. The common comparator has no training seed. Every unsuccessful target remains budget exhausted. Exact first-rung identities and the least recorded full-release work among eligible methods are retained in PUBLICATION_FACTS62.json.','rrrrrrr')
    rows=[]
    for t in tasks:
        for r in t['rungs']:
            rows.append([names[t['task']],r['n'],dec(r['common_gap']),span([r['methods'][f'relu-{s}-pure'] for s in seeds]),span([r['methods'][f'relu-{s}-guarded'] for s in seeds]),span([r['methods'][f'quadratic-{s}-pure'] for s in seeds]),span([r['methods'][f'quadratic-{s}-guarded'] for s in seeds])])
    longtable('rungs62','All original-optimum refinement rungs','tab:rungs62',
        ['$d/m/T$','$n$','Common','Pure R','Aug. R','Pure Q','Aug. Q'],rows,
        'Upper-bound ranges cover every fixed seed. Complete nodal arrays, exact error recursions, interpolation and quadrature allowances, action discretization allowances, and deployment errors are retained for each entry.','rrrcccc')
    rows=[]
    for t in tasks:
        cost=t['costs']
        for key in cost['policy_keys']:
            label=key.replace('quadratic','Q').replace('relu','R').replace('guarded','aug.')
            gain='--' if key=='zero' else band(cost['contrasts']['zero-minus-'+key]['interval'])
            rows.append([names[t['task']],label,band(cost['absolute'][key]['interval']),gain])
    longtable('all-costs62','Actual expected costs and adoption gains of every returned actor','tab:all-costs62',
        ['$d/m/T$','Policy','Expected cost','Zero-policy cost minus policy cost'],rows,
        'A positive lower gain supports replacement for every nonnegative installation fee below that lower endpoint, in normalized model units. The range is not a calibrated installation fee. Each path is an outward enclosure under the original continuous law, not a discrete-shock substitute.','rlcc')
    rows=[]
    for t in tasks:
        for seed in seeds:
            v=t['costs']['contrasts']
            rows.append([names[t['task']],seed,band(v[f'quadratic-{seed}-pure-minus-common']['interval']),band(v[f'quadratic-{seed}-guarded-minus-common']['interval'])])
    longtable('quadratic-cost62','Every conventional fitted-policy contrast','tab:quadratic-cost62',
        ['$d/m/T$','Seed','Pure quadratic minus common','Augmented quadratic minus common'],rows,
        'The same continuous-law paths and coverage account are used for conventional and neural actors. All nonrankings and identities are retained.','rrcc')
    result=dict(status='passed',tables=7,source_replay_sha256=__import__('hashlib').sha256((R/'audit/SCIENCE_REPLAY62.json').read_bytes()).hexdigest(),frontiers=frontier,task_facts=[dict(task=t['task'],final_n=t['rungs'][-1]['n'],common_bound=t['rungs'][-1]['common_gap'],final_bounds=t['rungs'][-1]['methods'],cost_classifications=t['cost_classifications']) for t in tasks],checked_nodal_action_records=a['checked_nodal_action_records'],checked_interval_records=a['checked_interval_records'],fitting_services=a['fitting_services'],new_production_path_rows=a['new_production_path_rows'])
    put('audit/PUBLICATION_FACTS62.json',json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
