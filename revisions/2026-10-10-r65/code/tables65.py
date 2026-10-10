"""Publication tables from audited frozen services; no new observations."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from decimal import Decimal,ROUND_CEILING
import json,statistics
R=Path(__file__).resolve().parents[1]
MODES=['adaptive','bisection','relu-insert','relu-route','quadratic-insert','quadratic-route']
NAMES={'adaptive':'A','bisection':'B','relu':'RI','quadratic':'QI','relu-insert':'RI','relu-route':'RG','quadratic-insert':'QI','quadratic-route':'QG'}
def put(name,s):
    if any(ord(c)<32 and c not in '\n\r\t' for c in s):raise ValueError('Control character '+name)
    p=R/'tables'/name;p.parent.mkdir(exist_ok=True);p.write_text(s)
def table(name,caption,label,headers,rows,note,cols=None,long=False):
    cols=cols or 'l'+'r'*(len(headers)-1)
    if long:
        s='\\begingroup\\small\\setlength{\\tabcolsep}{3pt}\n\\begin{longtable}{'+cols+'}\n\\caption{'+caption+'}\\label{'+label+'}\\\\\n\\toprule\n'
        h=' & '.join(headers)+r' \\'+'\n\\midrule\n';s+=h+'\\endfirsthead\n'+h+'\\endhead\n\\bottomrule\n\\endfoot\n'
        s+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+'\n\\end{longtable}\n\\endgroup\n'
    else:
        s='\\begin{table}[htbp]\n\\centering\\caption{'+caption+'}\\label{'+label+'}\n{\\small\\setlength{\\tabcolsep}{4pt}\n\\begin{tabular}{'+cols+'}\n\\toprule\n'
        s+=' & '.join(headers)+r' \\'+'\n\\midrule\n'+'\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+'\n\\bottomrule\n\\end{tabular}}\n'
        s+='\\par\\smallskip{\\footnotesize '+note+'}\n\\end{table}\n'
    put(name+'.tex',s)
def main():
    a=json.loads((R/'audit/RESULT_AUDIT65.json').read_text());groups=a['summary']['groups'];rows=a['R64']['rows'];out=[]
    heads=['$d$','$T$','$\\epsilon$','A','B','RI','RG','QI','QG']
    for g in groups:out.append([g['d'],g['T'],g['target']]+[f"{g['methods'][k]['median_wall']:.3f}" for k in MODES])
    note='A: adaptive parabolic search; B: bisection; RI and RG: ReLU insertion and gating; QI and QG: quadratic insertion and gating. Seconds are parent-observed complete-process times, including imports, training, queries, exact workload costing, durable output and process join. Each conventional median uses two repetitions; each learned median uses two seeds and two repetitions. Single-host descriptive clocks are not significance tests. All individual observations are retained in the supplement.'
    table('clocks65','Complete cold-start service times','tab:clocks65',heads,out,note)
    out=[]
    for g in groups:out.append([g['d'],g['T'],g['target']]+[f"{g['methods'][k]['median_queries']:,.1f}".replace('.0','') for k in MODES])
    table('queries65','Deployment Bellman query counts on identical workloads','tab:queries65',heads,out,
        'Counts exclude training and are not a complete work measure. They include the recursive descendants and the common terminal kernel. Within a task and tolerance the workload is fixed across methods. Half-integer medians arise from two different seed transcripts. Insertion and gating share identical fitted parameters for each matched seed and repetition.','rrrrrrrrr')
    comparisons={}
    for kind in ('relu','quadratic'):
        matched=[]
        for r in rows:
            if r['repeat'] or r['mode']!=kind+'-route':continue
            common=next(x for x in rows if x['mode']=='adaptive' and all(x[k]==r[k] for k in ('d','T','target','repeat')))
            ins=next(x for x in rows if x['mode']==kind+'-insert' and all(x[k]==r[k] for k in ('d','T','target','seed','repeat')))
            matched.append(dict(d=r['d'],T=r['T'],target=r['target'],seed=r['seed'],
                query_difference_from_insert=r['counts']['q_queries']-ins['counts']['q_queries'],
                query_difference_from_adaptive=r['counts']['q_queries']-common['counts']['q_queries'],
                training_queries=r['training_counts']['training_q_queries']))
        comparisons[kind]={key:{'lower':sum(x[key]<0 for x in matched),'equal':sum(x[key]==0 for x in matched),'higher':sum(x[key]>0 for x in matched)} for key in ('query_difference_from_insert','query_difference_from_adaptive')}
        comparisons[kind]['rows']=matched
    out=[]
    for kind in ('relu','quadratic'):
        for comparator,key in [('Insertion','query_difference_from_insert'),('Adaptive','query_difference_from_adaptive')]:
            c=comparisons[kind][key];out.append([kind.capitalize(),comparator,c['lower'],c['equal'],c['higher']])
    table('matched65','Matched query differences: gated minus comparator','tab:matched65',['Predictor','Comparator','Lower','Equal','Higher'],out,
        'One row comparison per task, target and fitting seed: sixteen for each predictor and comparator. Repetitions have identical models and numerical transcripts and do not double this count. These are query-count classifications, not signs of expected policy-cost differences.','llrrr')
    out=[]
    for g in groups:
        rr=[x for x in rows if (x['d'],x['T'],x['target'])==(g['d'],g['T'],g['target'])]
        out.append([g['d'],g['T'],g['target'],len(rr),format(Decimal.from_float(float(max(x['uniform_gap'] for x in rr))).quantize(Decimal('0.00000001'),rounding=ROUND_CEILING),'f'),max(x['counts']['max_batch'] for x in rr),max(x['peak_rss_kib'] for x in rr),f"{max(x['wall'] for x in rr):.3f}"])
    table('reliability65','Accuracy, memory and finite-catalogue return','tab:reliability65',['$d$','$T$','Target','Returns','Gap bound','Batch','RSS (KiB)','Max (s)'],out,
        'Every cell has twenty isolated-process returns: two conventional methods with two repetitions and four learned methods with two seeds and two repetitions. Gap bounds are rounded upward for display; exact binary64 values are retained in the audit and checked against the rational target. RSS is the largest recorded process peak, not only model storage. No service built a stored state lattice or invoked exact-rational recovery.','rrrrrrrr')
    for cohort in ('R63','R64'):
        out=[]
        for r in a[cohort]['rows']:
            out.append([r['d'],r['T'],r['target'],NAMES[r['mode']],r['seed'],r['repeat'],f"{r['wall']:.4f}",r['training_counts']['training_q_queries'],r['counts']['q_queries'],r['fit_warnings']])
        table('all-'+cohort+'-65',cohort+' complete individual service observations','tab:all-'+cohort+'-65',
            ['$d$','$T$','Target','Method','Seed','Rep.','Seconds','Train Q','Deploy Q','Warn.'],out,'',long=True)
    allrows=a['R63']['rows']+a['R64']['rows'];analysis=dict(status='derived',comparisons=comparisons,
        wall_winner_counts=dict(Counter(g['median_wall_winner'] for g in groups)),
        worst_process_seconds=max(x['wall'] for x in allrows),maximum_batch=max(x['counts']['max_batch'] for x in allrows),
        maximum_rss_kib=max(x['peak_rss_kib'] for x in allrows),path_rows=sum(x['N'] for x in allrows),
        R64_fit_warnings=sum(x['fit_warnings'] for x in rows),R63_fit_warnings=sum(x['fit_warnings'] for x in a['R63']['rows']),
        count_scope='Distinct task-target-seed transcripts; repetitions remain individual runtime observations.')
    (R/'audit/ANALYSIS65.json').write_text(json.dumps(analysis,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in analysis.items() if k!='comparisons'},indent=2))
if __name__=='__main__':main()
