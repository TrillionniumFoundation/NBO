"""Publication tables from verified immutable records, with outward display bounds."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import hashlib,json,math,statistics
R=Path(__file__).resolve().parents[1]
MODES=('common-only','quadratic-native','relu-screened','relu-native')
SHORT=dict(zip(MODES,('C','Q','S','N')))
ALG={'sympy':'SY','reduced-sympy':'RS','vector-exhaustive':'VE','screen-unreduced':'SU','screen-reduced':'SR','native-exhaustive':'UE','native-piecewise':'RP','adaptive':'AD'}

def read(p):return json.loads(Path(p).read_text())
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(name,text):
    p=R/name;p.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix=='.tex' and any(ord(x)<32 and x not in '\n\r\t' for x in text):raise ValueError('Control character in TeX: '+name)
    p.write_text(text)
def dec(x,d=3):return f'{float(x):.{d}f}'
def outward(x,lower=False,d=5):
    x=F(x);unit=10**d;k=math.floor(x*unit) if lower else math.ceil(x*unit);sign='-' if k<0 else '';k=abs(k)
    return sign+str(k//unit)+'.'+str(k%unit).zfill(d)
def band(pair,d=5):return '['+outward(pair[0],True,d)+', '+outward(pair[1],False,d)+']'
def interval(rec):return rec.get('exact',rec.get('interval'))
def kind(rec):
    if rec.get('identity'):return 'identity'
    a,b=map(F,interval(rec))
    return 'lower' if b<0 else 'higher' if a>0 else 'unresolved'
def table(name,caption,heads,rows,note,cols=None,long=False):
    cols=cols or 'l'+'r'*(len(heads)-1);head=' & '.join(heads)+r' \\'+'\n';body='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
    if long:
        text='\\begingroup\\small\\setlength{\\tabcolsep}{3pt}\n\\begin{longtable}{'+cols+'}\n\\caption{'+caption+'}\\label{tab:'+name+'}\\\\\n\\hline\n'+head+'\\hline\\endfirsthead\n\\hline\n'+head+'\\hline\\endhead\n'+body+'\n\\hline\n\\end{longtable}\n\\endgroup\n\\noindent{\\footnotesize '+note+'}\n\\par\\medskip\n'
    else:
        text='\\begin{table}[htbp]\n\\centering\n\\caption{'+caption+'}\\label{tab:'+name+'}\n{\\small\\setlength{\\tabcolsep}{3pt}\n\\begin{tabular}{'+cols+'}\n\\hline\n'+head+'\\hline\n'+body+'\n\\hline\\end{tabular}}\n\\par\\smallskip\n{\\footnotesize '+note+'}\n\\end{table}\n'
    put('tables/'+name+'.tex',text)

def main():
    a=read(R/'audit/SCIENCE_REPLAY61.json');f=read(R/'audit/FACTORIAL_AUDIT61.json');v=read(R/'results61-revalidation/summary.json')
    if any(x['status']!='passed' for x in (a,f,v)):raise AssertionError('Unverified results')
    groups=sorted({(x['d'],x['T'],x['target']) for x in a['rows']},key=lambda z:(z[0],-F(z[2])))
    services={(x['worker'],x['key']):x for x in a['rows']};service_rows=[];registry=[];matched=[];winner=[]
    for d,T,q in groups:
        block=[]
        for mode in MODES:
            pair=[[x for x in a['rows'] if (x['worker'],x['d'],x['T'],x['target'],x['mode'])==(w,d,T,q,mode)] for w in (0,1)]
            if any(len(x)!=2 for x in pair):raise AssertionError('Incomplete two-seed service cell')
            warm=[statistics.median(x['complete_return_seconds'] for x in z) for z in pair];cold=[statistics.median(x['cold_return_seconds'] for x in z) for z in pair];success=[sum(x['status']=='target_attained' for x in z) for z in pair]
            service_rows.append([f'{d}/{T}',q,SHORT[mode],str(success[0])+'/'+str(success[1]),*map(dec,warm),*map(dec,cold)])
            block.append(dict(mode=mode,attained_by_worker=success,warm_medians=warm,cold_medians=cold))
        winner.append(dict(d=d,T=T,target=q,by_worker=[min(block,key=lambda x:x['warm_medians'][w])['mode'] for w in (0,1)]))
        ratios=[]
        for w in (0,1):
            subset=[x for x in a['rows'] if (x['worker'],x['d'],x['T'],x['target'],x['mode'])==(w,d,T,q,'relu-native')];rr=[]
            for native in subset:
                screened=next(x for x in a['rows'] if (x['worker'],x['d'],x['T'],x['target'],x['mode'],x['seed'])==(w,d,T,q,'relu-screened',native['seed']))
                if native['final_policy_sha256']!=screened['final_policy_sha256']:raise AssertionError('Matched policy changed')
                rr.append(100*(screened['complete_return_seconds']-native['complete_return_seconds'])/screened['complete_return_seconds'])
            ratios.append(dict(median=statistics.median(rr),minimum=min(rr),maximum=max(rr),faster=sum(x>0 for x in rr)))
        matched.append(dict(d=d,T=T,target=q,workers=ratios))
    table('services61','Complete return work at the same economic targets',['$d/T$','$q$','Mode','Met 0/1','Warm 0 (s)','Warm 1 (s)','Cold 0 (s)','Cold 1 (s)'],service_rows,
        'C uses the common verified action family without a fitted continuation; Q uses native quadratic witnesses; S and N use the screened and native ReLU witnesses. The target is expected policy cost at most q times zero-policy cost. Each worker has two declared seeds; Met 0/1 gives the attained counts separately, each out of two. Warm and cold entries are within-worker two-seed medians of the complete durable-return clock. Cold work additionally charges that worker\'s measured native compilation for Q and N. Worker repetitions are not new independent economic samples. Failed targets remain in the table.','lcccrrrr')
    table('matched61','Complete-service effect of replacing screened with native ReLU search',['$d/T$','$q$','Saving 0 (\%)','Saving 1 (\%)','Faster 0/1'],[[f'{x["d"]}/{x["T"]}',x['target'],dec(x['workers'][0]['median'],2),dec(x['workers'][1]['median'],2),str(x['workers'][0]['faster'])+'/'+str(x['workers'][1]['faster'])] for x in matched],
        'Savings are paired relative reductions in complete warm return time, summarized by the median of the two seeds within each worker. Negative values mean slower native service. Faster counts are out of two per worker. The exact returned policy, fitted parameters, stopping stage, inference looks and intervals coincide. These are descriptive timings, not a frequency-controlled or cross-platform speed theorem.','lcccl')
    for x in sorted(a['rows'],key=lambda z:(z['worker'],z['d'],-F(z['target']),z['seed'],z['mode'])):
        last=x['stages'][-1]
        registry.append([x['worker'],f'{x["d"]}/{x["T"]}',x['target'],x['seed'],SHORT[x['mode']],len(x['stages']),'Y' if x['status']=='target_attained' else 'N',dec(x['complete_return_seconds']),outward(last['cost'][1]),outward(last['maximum_loss_bound'])])
    table('service-registry61','All ninety-six original R60 service returns',['Host','$d/T$','$q$','Seed','Mode','Stages','Met','Work (s)','Cost upper','Old gap'],registry,
        'No service is omitted. Cost upper is the final original-law simultaneous confidence endpoint; Old gap is the maximum datewise original certificate before the new fixed-policy revalidation. The two are different estimands. Modes and complete-work semantics are those of the main service table. A failed target still incurs all executed work. Raw lower endpoints, all intermediate looks, nonterminal changes and stage costs remain in the ordinary result registry.','rlrrcccrrr',True)
    costs=[];categories={m:{k:0 for k in ('identity','lower','higher','unresolved')} for m in MODES[:3]}
    for x in sorted([z for z in a['paired'] if z['worker']==0],key=lambda z:(z['d'],-F(z['target']),z['seed'])):
        other=next(z for z in a['paired'] if z['worker']==1 and (z['d'],z['T'],z['target'],z['seed'])==(x['d'],x['T'],x['target'],x['seed']))
        if other['contrasts']!=x['contrasts']:raise AssertionError('Repeated paired-family numerical identity differs')
        for m in MODES[:3]:categories[m][kind(x['contrasts'][m])]+=1
        costs.append([f'{x["d"]}/{x["T"]}',x['target'],x['seed'],band(interval(x['contrasts']['common-only'])),band(interval(x['contrasts']['quadratic-native']))])
    table('cost61','Actual returned-policy cost: native ReLU minus conventional comparators',['$d/T$','$q$','Seed','N minus C','N minus Q'],costs,
        'Intervals use the fresh final-policy comparison stream, conditional on the original selection. Endpoints are rounded outward. Positive intervals identify higher native-ReLU cost; an interval containing zero is unresolved. Exact policy identities have an exact zero interval. There are twelve mathematical designs, each repeated on two workers with the same policies and stream, not twenty-four independent comparisons. N minus S is identically zero.','lcrcc')
    paired_action=[]
    for x in f['reduced_representation_search_contrasts']:
        if x['worker']!=0:continue
        y=next(z for z in f['reduced_representation_search_contrasts'] if z['worker']==1 and (z['width'],z['size'])==(x['width'],x['size']))
        paired_action.append([x['width'],x['size'],str(x['reduced_piecewise_faster'])+'/15',str(y['reduced_piecewise_faster'])+'/15',dec(100*x['median_fraction_saved'],2),dec(100*y['median_fraction_saved'],2)])
    table('native-factorial61','Finite-difference versus exhaustive search at the same reduced representation',['Width','Lattice','Faster 0','Faster 1','Saving 0 (\%)','Saving 1 (\%)'],paired_action,
        'Both methods use the same C++ arbitrary-size rational engine, identical reduced objective and original-value postcheck. Each row includes three fixed seeds and all five regimes. Savings are medians of paired per-instance relative timings, not ratios of unrelated medians. Reduction, process creation, serialization and parsing are charged to both methods. The unreduced pair and all four-cell repeated-query results are retained in the supplement.','rrrrrr')
    repeated=[]
    for x in f['repeated_subset']:
        repeated.append([x['worker'],x['regime'],*[dec(1000*x['methods'][m]['median_seconds'],3) for m in ('UE','RE','UP','RP')]])
    table('native-repeats61','Matched native two-by-two repetition medians',['Host','Regime','UE (ms)','RE (ms)','UP (ms)','RP (ms)'],repeated,
        'U/R indicates unreduced/reduced activation representation; E/P indicates exhaustive/finite-difference native search. All four use the same exact engine, lattice, tie rule and timing boundary. Seven additional shuffled repetitions use seed 60103, width 32 and lattice 129 in every regime. Full min/max ranges and per-repetition orders are in FACTORIAL\_AUDIT61.json and the two source summaries. No repeated instance is counted as a new learned policy.','rlrrrr')
    batchrows=[]
    for w,size in product((0,1),(1,8,32)):
        z=[next(x for x in f['batches'] if (x['worker'],x['batch_size'],x['method'])==(w,size,m)) for m in ('UE','RE','UP','RP')]
        batchrows.append([w,size,z[0]['subprocesses'],*[dec(x['seconds'],4) for x in z]])
    table('batch61','Work for the same ninety-query catalogue at different native batch sizes',['Host','Batch','Processes','UE (s)','RE (s)','UP (s)','RP (s)'],batchrows,
        'Each entry covers all ninety heterogeneous fixed queries, including exact reduction when applicable, serialization, process creation, parsing and original-objective checks. It is not a per-query median or a complete policy-service clock. The entire answer arrays coincide with Fraction exhaustive references for every batch size. Compilation is separately recorded.','rrrrrrr')
    stressrows=[];fallbacks=0;peakbits=0
    for host in a['stress']:
        for x in host['aggregate']:
            stressrows.append([x['worker'],x['regime'],ALG[x['method']],dec(1000*x['median_seconds'],3),dec(1000*x['repeated_median_seconds'],3),x['fallbacks'],x['maximum_survivors'],(x['maximum_operand_bits'] or '--'),(x['largest_pair_array_bytes'] or '--')])
            fallbacks+=x['fallbacks'];peakbits=max(peakbits,x['maximum_operand_bits'])
    table('stress61','Complete eight-method stress summary',['Host','Regime','Method','Grid ms','Repeat ms','Fallback','Survive','Bits','Bytes'],stressrows,
        'SY and RS are unreduced and reduced symbolic searches; VE computes the vector enclosure but evaluates every lattice action exactly; SU and SR screen the unreduced and reduced objectives; UE is unreduced native exhaustive search; RP is reduced native finite-difference search; AD is reduced adaptive interval subdivision with an exact fallback. Grid ms is the median over all eighteen seed/width/lattice instances in that regime; Repeat ms is the fixed seven-repeat subset median. Survive, Bits and Bytes are maxima of the named diagnostics, not maxima over every hidden arithmetic temporary or whole-process memory. The observed endpoint intervention coarsens exact bounds to 8 or 24 fractional bits; it does not change internal binary64 precision.','rllrrrrrr',True)
    guardrows=[]
    for host in a['stress']:
        for x in host['guards']:
            guardrows.append([x['worker'],x['size'],x['regime'],ALG[x['method']],'Y' if x.get('fallback') else 'N',x.get('pair_nodes',0),x.get('pre_fallback_exact_evaluations',0)+x.get('exact_evaluations',0),dec(x['seconds'],4)])
    table('guards61','Every large-lattice and node-budget guard case',['Host','Lattice','Regime','Method','Fallback','Nodes','Exact total','Time (s)'],guardrows,
        'The lattice sizes exceed the declared screening threshold. An exact fallback preserves the original value and smallest witness but incurs the already spent prefix work. Exact total adds the explicitly recorded pre-fallback evaluations. Native rational operation counts remain distinct from wall time.','rrllcrrr',True)
    multirows=[]
    for cap,shocks in product((8,16),(1,2)):
        block=[x for x in a['two_controls'] if (x['cap'],x['shocks'])==(cap,shocks)]
        multirows.append([cap,shocks,len(block)//2,int(statistics.median(x['exhaustive_evaluations'] for x in block)),dec(statistics.median(x['adaptive_evaluations'] for x in block),1),max(x['nodes'] for x in block),sum(x['fallback'] for x in block),dec(statistics.median(x['adaptive_seconds']/x['exhaustive_seconds'] for x in block),2)])
    table('multi61','Constrained two-control exact witness recovery',['Cap index','Shocks','Designs','Exhaustive','Adaptive','Max nodes','Fallback','Time ratio'],multirows,
        'Each of four mathematical designs per row uses a saved genuinely fitted ReLU continuation, two state points and two training seeds, repeated on two workers. Shared capacity is 1/8, with quantum denominator eight times Cap index. Adaptive counts are selected exact evaluations; node-bound computation is additional work. Time ratio is the median paired adaptive/exhaustive query time over the eight records. A ratio above one means slower adaptive execution despite fewer exact evaluations. These are action-search results, not complete two-control welfare comparisons.','rrrrrrrr')
    multi_detail=[[x['worker'],x['seed'],','.join(x['state']),x['cap'],x['shocks'],','.join(map(str,x['index'])),x['exhaustive_evaluations'],x['adaptive_evaluations'],x['nodes'],'Y' if x['fallback'] else 'N'] for x in a['two_controls']]
    table('multi-registry61','All two-control exact query records',['Host','Seed','State','Cap','Shocks','Witness','Exhaust.','Adaptive','Nodes','Fall.'],multi_detail,
        'Each original rational objective, trained-parameter payload, full exhaustive reference, adaptive answer and clock is retained. The additional action and optional second shock are explicit nested model extensions; the original scalar-action economy is recovered by zero second action with the second shock disabled.','rrcrrcrrrc',True)
    bellrows=[]
    for x in a['centered']['rows']:
        orig=next((z for z in a['uncentered'] if z['worker']==0 and z['N']==x['N']),None)
        bellrows.append([x['N'],x['A'],x['q'],outward(orig['maximum_date_gap_upper']) if orig else '--',outward(x['maximum_date_gap_upper']),dec(x['cumulative_seconds'],3)])
    table('bellman61','Original-model whole-domain Bellman accuracy',['$N$','$A$','$q$','Uncentered gap','Centered gap','Centered work (s)'],bellrows,
        'The model remains the original two-state, two-date investment economy with its continuous feasible actions and innovation law. N is the number of verification cells per state coordinate. The common-reference lower and upper endpoints cancel the same reference value pointwise. Centered work includes every preceding declared rung and endpoint serialization on that execution. The uncentered gap is the corresponding separately executed numerical bracket, not a same-host timing comparator. Tolerances 1/2, 1/4, 1/8 and 1/16 are attained; 1/32 is not.','rrrrrr')
    fixed=[]
    for x in v['rows']:
        fixed.append([r'\texttt{'+x['policy_sha256'][:8]+'}',x['leaves'],'/'.join(sorted(set(SHORT[z['mode']] for z in x['aliases']))),len(x['aliases']),outward(x['dates'][0]['gap_upper']),outward(x['maximum_date_gap_upper']),outward(x['maximum_unclipped_date_gap_upper']),dec(x['seconds_through_endpoint_archive'],3)])
    table('fixed-policy61','Revalidation of every distinct actually returned two-date actor',['Actor','Leaves','Modes','Aliases','Date 0 gap','All-date gap','Unclipped','Own work (s)'],fixed,
        'All thirty-two returned service records are represented by five complete policy-plus-partition identities. No actor is retrained, improved or replaced. Verification uses N=128 and q=32 with the deposited centered lower Bellman table. Closed actor ranges include every intersecting leaf. The independent global nonworsening bound is intersected with upper excess endpoints, but the maximum gaps here coincide with the retained unclipped calculation. Own work covers each fixed-actor recursion through its endpoint archive; the shared lower-table reconstruction and process-return overhead are separate audit records.','lrcrrrrr')
    facts=dict(status='passed',services=a['services'],attained=a['attained'],budget_exhausted=a['budget_exhausted'],exact_records=a['counts']['scalar_solver_records'],checked_cells=a['counts']['cell_decisions'],original_law_rows_reconstructed=a['counts']['distinct_path_rows'],native_factorial_exact_answers=f['checked_exact_answers'],unique_fixed_actors=v['distinct_actors'],fixed_aliases=v['original_actor_aliases'],fixed_bounds=[dict(policy=x['policy_sha256'][:12],bound=x['maximum_date_gap_upper'],leaves=x['leaves'],modes=sorted(set(z['mode'] for z in x['aliases']))) for x in v['rows']],paired_classifications=categories,warm_fastest_modes=winner,matched_service_savings=matched,factorial=f['reduced_representation_search_contrasts'],centered_final_gap=a['centered']['rows'][-1]['maximum_date_gap_upper'],centered_total_work=a['centered']['rows'][-1]['cumulative_seconds'],distinct_extra_witness_cell_changes=a['counts']['distinct_extra_witness_cell_changes'],replay_seconds=a['replay_seconds'],fallback_record_count=fallbacks,maximum_reported_stress_operand_bits=peakbits,source_hashes={name:digest(R/name) for name in ('audit/SCIENCE_REPLAY61.json','audit/FACTORIAL_AUDIT61.json','results61-revalidation/summary.json')})
    put('audit/PUBLICATION_FACTS61.json',json.dumps(facts,indent=2,sort_keys=True)+'\n')
    put('tables/facts61.tex','% Automatically derived from verified result records.\n'+''.join(('\\providecommand{'+chr(92)+key)+'}{'+str(value)+'}\n' for key,value in [('NBOServices',a['services']),('NBOAttained',a['attained']),('NBOExhausted',a['budget_exhausted']),('NBOFixedActors',v['distinct_actors']),('NBOFixedAliases',v['original_actor_aliases']),('NBOFactorialAnswers',f['checked_exact_answers']),('NBOCenteredGap',outward(facts['centered_final_gap'])),('NBOExtraChanges',facts['distinct_extra_witness_cell_changes'])]))
    print(json.dumps(facts,indent=2),flush=True)
if __name__=='__main__':main()
