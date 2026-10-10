"""Publication tables derived only from the passed full R59 replay."""
from pathlib import Path
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
import json,statistics
R=Path(__file__).resolve().parents[1]

def put(name,text):
    if any(ord(c)<32 and c not in '\n\r\t' for c in text):raise ValueError('Control character in '+name)
    p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def num(x,d=3):return f'{x:.{d}f}'
def end(x,lower,d=5):
    return format(Decimal.from_float(float(x)).quantize(Decimal(10)**(-d),rounding=ROUND_FLOOR if lower else ROUND_CEILING),'f')
def band(v,d=5):return '['+end(v[0],True,d)+', '+end(v[1],False,d)+']'
def target(q):return r'$10\%$' if q=='9/10' else r'$20\%$'
def task(row):return f"({row['d']},{row['T']})"
def table(name,title,heads,rows,note,long=False):
    cols='l'+'r'*(len(heads)-1);label='tab:'+name
    if long:
        body=r'\begingroup\footnotesize\setlength{\tabcolsep}{3pt}'+'\n'+r'\begin{longtable}{'+cols+'}\n'+r'\caption{'+title+'}'+r'\label{'+label+r'}\\'+'\n\\hline\n'
        header=' & '.join(heads)+r' \\'+'\n\\hline\n'
        body+=header+r'\endfirsthead'+'\n'+header+r'\endhead'+'\n'
        body+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
        body+='\n'+r'\hline\end{longtable}'+'\n'+r'\noindent '+note+'\n'+r'\endgroup'+'\n'
    else:
        body=r'\begin{table}[htbp]\centering'+'\n'+r'\caption{'+title+r'}\label{'+label+'}\n'+r'{\small\setlength{\tabcolsep}{3pt}\begin{tabular}{'+cols+'}\n\\hline\n'
        body+=' & '.join(heads)+r' \\'+'\n\\hline\n'
        body+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
        body+='\n'+r'\hline\end{tabular}}\par\smallskip'+'\n'+r'{\footnotesize '+note+'}\n'+r'\end{table}'+'\n'
    put('tables/'+name+'.tex',body)

def main():
    a=json.loads((R/'audit/RESULT_AUDIT59.json').read_text())
    if a['status']!='passed':raise AssertionError('Scientific replay not passed')
    gs=a['groups'];rows=a['rows']
    table('matched-work59','Complete service work for exactly matching policies',
        [r'$(d,T)$','Reduction','Return','Algebraic (s)','Screened (s)','Ratio'],
        [[task(g),target(g['target']),'Met' if g['status']=='target_attained' else 'Exhausted',num(g['algebraic_median']),num(g['screened_median']),num(g['process_speedup'])] for g in gs],
        'Each time is the median of all three separately reconstructed fixed-work process repetitions. The ratio is algebraic divided by screened. Corresponding policies, fitted parameters, verification endpoints and stopping histories agree exactly. Exhaustion is not successful target attainment. Different tasks use different runners; the comparison is within task and target.')
    table('matched-cost59','Original-law economic costs at the common return',
        [r'$(d,T)$','Reduction','Policy cost','Gain from installed','Target contrast'],
        [[task(g),target(g['target']),band(g['cost'],4),band(g['gain'],4),band(g['target_contrast'],4)] for g in gs],
        'The two modes have identical intervals, not independent estimates. Endpoints are rounded outward. The signed target contrast, rather than a ratio of estimated means, determines attainment. The twenty-percent target in eight dimensions remains unresolved at the final budget.')
    table('search-operations59','Nonterminal neural search work, including rejected lattice points',
        [r'$(d,T)$','Reduction','Queries','Exact A','Exact S','Roots A','Screened points'],
        [[task(g),target(g['target']),g['algebraic_operations']['neural_queries'],g['algebraic_operations']['exact_evaluations'],g['screened_operations']['exact_evaluations'],g['algebraic_operations']['root_isolations'],g['screened_operations']['screened_points']] for g in gs],
        'A denotes algebraic search and S screened search. Counts sum all attempted resolutions in one service; all three repetitions reproduce them. The screened mode retains one point per nonterminal neural query and performs zero root isolations and zero fallbacks in this catalogue. Terminal work is common and excluded from these neural counts.')
    tr=[];br=[];pr=[]
    for g in gs:
        for mode,name in [('algebraic','A'),('screened','S')]:
            subset=sorted([r for r in rows if (r['d'],r['T'],r['target'],r['mode'])==(g['d'],g['T'],g['target'],mode)],key=lambda r:r['rep'])
            times=[r['process_seconds'] for r in subset]
            tr.append([task(g),target(g['target']),name,*[num(t) for t in times],num(statistics.median(times))])
            components=[]
            for r in subset:
                service=json.loads((R/'results58/services'/r['key']/'service.json').read_text())
                inference=0.
                for stage in service['stages']:
                    look=stage['look_paths'][-1];rec=json.loads((R/'results58/services'/r['key']/f"stage{stage['stage']}-look{look}.json").read_text());inference+=rec['seconds_through_raw']
                remainder=r['process_seconds']-r['fit_seconds']-r['search_seconds']-r['verification_seconds']-inference
                components.append([r['fit_seconds'],r['search_seconds'],r['verification_seconds'],inference,remainder])
            br.append([task(g),target(g['target']),name,*[num(statistics.median(x[j] for x in components)) for j in range(5)]])
        op=g['screened_operations'];pr.append([task(g),target(g['target']),op['active_ridges'],op['eliminated_ridges'],op['retained_points'],op['fallbacks']])
    table('repetitions59','Every complete-process timing repetition',
        [r'$(d,T)$','Reduction','Mode','Rep. 1 (s)','Rep. 2 (s)','Rep. 3 (s)','Median (s)'],tr,
        'No timing trial is selected or removed. A is algebraic and S screened. Fits and inference streams deliberately repeat; these are timing repetitions, not independent learned objects or additional policy-cost samples.',True)
    table('components59','Recorded service components and surrounding-process remainder',
        [r'$(d,T)$','Reduction','Mode','Fit (s)','Search (s)','Verify (s)','Inference (s)','Other (s)'],br,
        'Entries are componentwise medians across the three services. Their sum need not equal the median complete-process clock. Other is calculated separately within each service as its surrounding clock minus the four component clocks; it includes imports, record handling, output and termination, not parent-controller checkpoint overhead. Search includes the common terminal solver.',True)
    table('reduction59','Exact activation-region reduction of trained ridges',
        [r'$(d,T)$','Reduction','Crossing ridges','Reduced ridges','Survivors','Fallbacks'],pr,
        'Counts aggregate ridge occurrences across neural queries and attempted resolutions, not the number of distinct trained features. Reduced ridges are incorporated exactly into polynomial coefficients or vanish identically. Their weights are not thresholded.',True)
    registry=[]
    for r in rows:
        registry.append([task(r),target(r['target']),'A' if r['mode']=='algebraic' else 'S',r['rep']+1,'M' if r['status']=='target_attained' else 'E',r['stages'],num(r['process_seconds']),num(r['bytes']/1048576,2),num(r['rss_kib']/1024,2)])
    table('services59','Complete 36-service return, work and storage registry',
        [r'$(d,T)$','Reduction','Mode','Rep.','Return','Attempts','Time (s)','MiB out','MiB RSS'],registry,
        'M means target attained and E budget exhausted. Output bytes are complete serialized own-service files; RSS is process peak resident memory. These are not the logical working storage of the screening kernel. Exact service keys, parameter and policy identities, stagewise endpoints, raw arrays and clocks remain in the machine-readable audit.',True)
    summaries=[]
    for r in a['replayed_services']:
        if r['mode']!='screened' or r['rep']!=0:continue
        for st in r['stages']:
            for d in st['dates']:
                summaries.append([task(r),target(r['target']),st['stage'],d['date'],d['changed'],d['extra_witness_changes'],end(d['gap_upper'],False,5),end(d['candidate_component_upper'],False,5),end(d['cover_component_upper'],False,5)])
    table('datewise59','Datewise decisions and unchanged full-action certificate components',
        [r'$(d,T)$','Reduction','Stage','Date','Changed','Extra',r'$U-L$',r'$U-C$',r'$C-L$'],summaries,
        'One of the exactly matching solver/repetition transcripts is printed to avoid duplicating numerical identities. Extra means a selected action changed by adding the exact fitted witness to the common plus critic-menu candidates. Each bound is rounded upward. The component maxima need not sum to the maximum total gap, and the local gap is not substituted for final Bellman loss.',True)
    put('tables/summary59.json',json.dumps({k:a[k] for k in ('groups','counts','services','attained','budget_exhausted')},indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status='generated',tables=8,services=len(rows))))
if __name__=='__main__':main()
