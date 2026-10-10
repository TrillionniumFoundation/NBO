"""Generate descriptive tables; retain every failed service in the audit."""
from pathlib import Path
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
import json,statistics
R=Path(__file__).resolve().parents[1]
LABEL={'adaptive':'Adaptive','upper-minimizer':'Chord','hat-relu':'ReLU-C','bernstein4':'Bernstein-C','label-relu':'ReLU-L','quadratic':'Quadratic','simplicial':'Adaptive triangle','uniform':'Uniform triangle','hat-vector':'ReLU vector','quadratic-vector':'Quadratic vector','r67-relu':'R67 ReLU'}
def fmt(x,n=4):return f'{x:.{n}f}'
def endpoint(x,lower):return format(Decimal.from_float(float(x)).quantize(Decimal('0.00001'),rounding=ROUND_FLOOR if lower else ROUND_CEILING),'f')
def interval(x):return '['+endpoint(x[0],True)+', '+endpoint(x[1],False)+']'
def write(name,text):
    p=R/'tables'/name;p.parent.mkdir(parents=True,exist_ok=True)
    if any(ord(c)<32 and c not in '\n\r\t' for c in text):raise ValueError('Invalid table text')
    p.write_text(text)
def table(name,title,heads,rows,note):
    if not rows:rows=[['Not returned']+['--']*(len(heads)-1)]
    text='\\begin{table}[htbp]\n\\centering\n\\caption{'+title+'}\\label{tab:'+name+'}\n{\\small\\setlength{\\tabcolsep}{3pt}\n\\begin{tabular}{'+'l'*len(heads)+'}\n\\hline\n'
    text+=' & '.join(heads)+r' \\'+'\n\\hline\n'
    text+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
    text+='\n\\hline\n\\end{tabular}}\n\\par\\smallskip\n{\\footnotesize '+note+'}\n\\end{table}\n'
    write(name+'.tex',text)
def main():
    a=json.loads((R/'audit/RESULT_AUDIT69.json').read_text());good=[x for x in a['services'] if x['returned']];median=statistics.median
    rows=[]
    for d,T in ((2,2),(8,3)):
        for kind in ('adaptive','upper-minimizer','hat-relu','bernstein4','label-relu','quadratic'):
            g=[x for x in good if x['spec']['group']=='comparison' and x['spec']['d']==d and x['spec']['kind']==kind]
            if not g:continue
            times=[x['complete_process_seconds'] for x in g]
            rows.append([d,T,LABEL[kind],len(g),fmt(median([x['counts']['q_queries'] for x in g]),0),fmt(median(times),3),fmt(min(times),3)+'--'+fmt(max(times),3)])
    table('cold69','Complete cold-start services',['$d$','$T$','Method','$n$','Queries','Median (s)','Range (s)'],rows,
          'C is the certificate objective and L action-label loss. Query counts and times are medians over all returned seeds and repetitions. Process clocks include construction, queries, path evaluation, output and shutdown. Four repetitions are descriptive timing evidence, not a population performance guarantee.')
    unique={}
    for x in a['exact_training']:
        z=x['spec'];key=(z['d'],z['T'],z['kind'],z['seed'],x['r']);v=x['exact_certificate']
        if key in unique and (unique[key]['value_exact']!=v['value_exact'] or unique[key]['dual_gap_exact']!=v['dual_gap_exact']):raise AssertionError('Nonreproducible fitted objective')
        unique[key]=v
    rows=[[d,T,LABEL[k],seed,r,v['coefficient_count'],fmt(v['value'],7),fmt(v['dual_gap'],7)] for (d,T,k,seed,r),v in sorted(unique.items())]
    table('readout69','Achieved convex readout certificates',['$d$','$T$','Method','Seed','$r$','$p$','$F(w)$','$D(w)$'],rows,
          'Exact rational values and every training endpoint are retained in the audit. Both representations have 5d coefficients and the same information and optimizer budget. The dual gap certifies the returned quantized weights; it does not assume optimizer convergence.')
    rows=[]
    for x in a['validation']:
        z=x['spec'];rows.append([z['d'],z['T'],LABEL[z['kind']],z['seed'],x['r'],x['screen_returns'],fmt(x['mean_root_queries'],2),fmt(x['distributional_root_upper'],2)])
    table('validation69','Independent context validation',['$d$','$T$','Method','Seed','$r$','Closed','Queries','Upper'],rows,
          'Each row uses 256 independent acquired-state contexts. Closed counts pre-query returns. Queries and Upper are the observed average root-query count and its declared distributional upper bound. The complete-action mesh recovery is executed; recursive deployment states are not treated as IID contexts.')
    rows=[]
    for d,T in ((2,2),(8,3)):
        for kind in ('hat-relu','bernstein4','quadratic'):
            g=[x for x in a['reuse_comparisons'] if x['spec']['d']==d and x['spec']['kind']==kind]
            if not g:continue
            rows.append([d,T,LABEL[kind],len(g),sum(x['complete_process_win'] for x in g),sum(x['early_persistent_crossing'] for x in g),fmt(median([x['complete_process_seconds']/x['adaptive_seconds'] for x in g]),3)])
    table('reuse69','Prospective sixty-four-block reuse',['$d$','$T$','Method','$n$','Final wins','Early stable','Time ratio'],rows,
          'Early stable requires a crossing by block 48 persisting through block 63, with zero-based indices. Final wins use full parent clocks. A stale acquisition identifier at block 16 invokes adaptive fallback. All construction, loading, checking, deployment and output costs are charged.')
    rows=[];precision=[]
    for x in a['centered_contrasts']:
        left,right=x['contrast'].split('-minus-');name=LABEL[left]+' / '+LABEL[right]
        rows.append([x['d'],x['T'],name,interval(x['interval']),fmt(x['raw_width'],5),'Yes' if x['equivalent_at_margin'] else 'No'])
        precision.append([x['d'],x['T'],name,fmt(x['sampling_radius'],6),fmt(x['mean_numerical_width']/2,6),'Yes' if x['sampling_allocation_met'] and x['numerical_allocation_met'] else 'No'])
    table('centered69','Original expected policy-cost differences',['$d$','$T$','First minus second','Centered interval','Cash width','Equiv.'],rows,
          'Every pairwise comparison is shown. Both estimators use the same 1,024 new path rows; the centered estimator additionally purchases finer Bellman evaluations. Equivalence is at the prespecified normalized margin 1/256, not exact equality or strict superiority. Displayed interval endpoints are rounded outward.')
    table('precision69','Prespecified inference precision',['$d$','$T$','First minus second','Sampling','Numerical','Both met'],precision,
          'Sampling and Numerical are half-width contributions before support intersection. Each has a prespecified allocation of 1/512. Conditional Bellman, state-transfer, acquisition-ambiguity and arithmetic components remain in the per-batch ledger.')
    rows=[]
    for d,T in ((2,2),(8,2),(2,3),(8,3),(2,4)):
        for kind in ('simplicial','uniform','hat-vector','quadratic-vector'):
            g=[x for x in good if x['spec']['group']=='vector' and x['spec']['d']==d and x['spec']['T']==T and x['spec']['kind']==kind]
            if not g:continue
            rows.append([d,T,LABEL[kind],g[0]['spec']['N'],fmt(median([x['counts']['q_queries'] for x in g]),0),fmt(median([x['complete_process_seconds'] for x in g]),3),max(x['peak_rss_kib'] for x in g)])
    table('vector69','Two-control and two-innovation comparisons',['$d$','$T$','Method','Paths','Queries','Time (s)','RSS (KiB)'],rows,
          'Two- and three-date services use eight paths and two repetitions. Four-date services use one path and one repetition; their neural proposal transfers the three-date readout. Teacher queries and rational recovery are separately counted. These finite comparisons do not establish long-horizon scalability.')
    eq=sum(x['equivalent_at_margin'] for x in a['centered_contrasts'])
    text=r'\paragraph{Complete execution and declared endpoints.} '+f"The catalogue contains {a['planned_services']} services: {a['returned']} returned and {a['failed_or_timed_out']} failed or timed out. Every planned receipt is retained. The centered account places {eq} of {len(a['centered_contrasts'])} returned contrasts inside the prespecified equivalence margin. This does not identify strict neural superiority. The independent rational implementation checks {a['independent_trajectory_checks']:,} represented mid-bin trajectories; conservatively ambiguous cases remain separately recorded.\n"
    write('findings69.tex',text)
    print(json.dumps(dict(tables=7,returned=a['returned'],failed=a['failed_or_timed_out'],equivalent=eq)))
if __name__=='__main__':main()
