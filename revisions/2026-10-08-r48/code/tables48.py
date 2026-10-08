"""Deterministically typeset the audited, frozen study; never sample or retime."""
from __future__ import annotations
import collections,itertools,json,math,statistics
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING, localcontext
from fractions import Fraction as F
from pathlib import Path
R=Path(__file__).resolve().parents[1];OUT=R/'tables'
read=lambda p:json.loads(Path(p).read_text())
METHODS=('compiled-witness','tensor-fvi','adaptive-fvi');SHORT=dict(zip(METHODS,('C','U','A')))
def num(x,d=3):return f'{float(x):.{d}f}'
def sig(x):
    if x is None:return r'$\infty$'
    return f'{float(F(x)):.6g}'
def outward(x,upper=True,d=6):
    f=F(x)
    with localcontext() as ctx:
        ctx.prec=100
        z=Decimal(f.numerator)/Decimal(f.denominator)
        return format(z.quantize(Decimal(1).scaleb(-d),rounding=ROUND_CEILING if upper else ROUND_FLOOR),'f')
def table(file,caption,label,fmt,header,rows,note):
    s='\\begin{table}[htbp]\n\\centering\n\\caption{'+caption+'}\\label{'+label+'}\n\\footnotesize\n\\begin{tabular}{'+fmt+'}\n\\toprule\n'+header+'\\\\\n\\midrule\n'
    s+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
    s+='\n\\bottomrule\n\\end{tabular}\n\\begin{minipage}{0.97\\linewidth}\\footnotesize\\vspace{3pt}\n'+note+'\n\\end{minipage}\n\\end{table}\n'
    (OUT/file).write_text(s)
def main():
    OUT.mkdir(exist_ok=True);s=read(R/'audit/PUBLICATION_SUMMARY.json');assert s['services']==44 and s['rungs']==204
    cells=s['cells'];lookup={(c['dimension'],c['T'],c['p'],c['method']):c for c in cells};core=[c for c in cells if c['dimension']==2]
    rows=[]
    for T,p,m in itertools.product((2,3),(1,4),METHODS):
        c=lookup[2,T,p,m]
        rows.append([T,p,SHORT[m],num(c['bound']),num(c['median_seconds']),f"[{num(c['min_seconds'])}, {num(c['max_seconds'])}]",num(c['peak_rss_kib']/1024,1)])
    table('core48.tex','Complete two-state construction services at the declared cap','tab:core48','rrcrrrr',r'$T$ & $p$ & Method & Loss bound & Median (s) & Range (s) & Peak MiB',rows,
          'C denotes compiled witness, U uniform tensor FVI, and A error-driven coordinate FVI. Each entry ends at $N=M=64$ and includes the complete five-rung prefix through durable record output. The range is over three isolated repetitions with identical checkpoints, not three economic draws. Peak resident memory includes the interpreter and warm-up. Bounds are displayed to three decimals; exact rational tests determine attainment.')
    rows=[[SHORT[m]]+[f"{s['core_attainment_out_of_12'][m][v]}/12" for v in ('4','2','1','1/2','1/4')] for m in METHODS]
    table('attainment48.tex','Prospective target attainment in the two-state catalogue','tab:attainment48','crrrrr',r'Method & $4$ & $2$ & $1$ & $1/2$ & $1/4$',rows,
          'All failures and every prior rung are retained. Counts concern twelve deterministic services per method, crossing four economic cells and three timing repetitions. A repeated failure is not an independent estimate of optimizer reliability. No historical failure is reclassified.')
    # First-crossing times on the prospectively declared target set.
    records=[read(p) for p in sorted((R/'results/services').glob('*/record.json'))];paired={}
    for alt in METHODS[1:]:
        wins=losses=ties=common=0
        for T,p,rep,target in itertools.product((2,3),(1,4),range(3),('4','2','1','1/2','1/4')):
            rr={r['method']:r for r in records if (r['dimension'],r['horizon'],r['price'],r['repeat'])==(2,T,p,rep)}
            a,b=(rr[m]['first_crossings'][target] for m in ('compiled-witness',alt))
            if a is None or b is None:continue
            common+=1;wins+=a['prefix_seconds']<b['prefix_seconds'];losses+=a['prefix_seconds']>b['prefix_seconds'];ties+=a['prefix_seconds']==b['prefix_seconds']
        paired[alt]={'common':common,'compiled_faster':wins,'compiled_slower':losses,'equal':ties}
    parts=[]
    for m in METHODS[1:]:
        q=paired[m];word='uniform' if m=='tensor-fvi' else 'error-driven'
        parts.append(f"Against {word} FVI, compiled witness is earlier in {q['compiled_faster']} of {q['common']} common successful target/repetition comparisons, later in {q['compiled_slower']}, and tied in {q['equal']}.")
    parts.append('These are observed complete-prefix wall times, not a hardware-general speed law. The comparison uses the prospective targets rather than retrospectively selecting a favorable breakpoint. The full positive-tolerance partition, including one-sided and joint nonattainment, is reported in the supplement and machine-readable frontier.')
    adaptive={'checkpoints':0,'date_models':0,'nonuniform_date_models':0,'same_models_and_actors_as_uniform':0}
    for path in sorted((R/'results/services').glob('adaptive-fvi*/checkpoint*.json')):
        j=read(path);u=read(Path(str(path).replace('adaptive-fvi','tensor-fvi')));adaptive['checkpoints']+=1
        for model in j['models']:
            adaptive['date_models']+=1
            adaptive['nonuniform_date_models']+=any([F(float(x)) for x in a]!=[F(i,j['N']) for i in range(j['N']+1)] for a in model['axes'])
        adaptive['same_models_and_actors_as_uniform']+=j['models']==u['models'] and j['actors']==u['actors']
    assert adaptive=={'checkpoints':60,'date_models':210,'nonuniform_date_models':0,'same_models_and_actors_as_uniform':60}
    parts.append('The error-driven rule returns uniform grids in all 210 recorded date models; all 60 adaptive checkpoints have exactly the same continuations and actors as their uniform-FVI counterparts. Thus its additional observed cost is pilot and allocation overhead, not evidence of a realized nonuniform-grid improvement. The nonuniform verification theorem is proved and tested, but an effective spatial-adaptation advantage is not established by this catalogue.')
    ww=[read(R/f'results/services/compiled-witness-d2-T3-p4-r{i}/record.json')['first_crossings']['2'] for i in range(3)]
    uu=[read(R/f'results/services/tensor-fvi-d2-T3-p4-r{i}/record.json')['first_crossings']['2'] for i in range(3)]
    assert all(w['N']==32 and u['N']==64 for w,u in zip(ww,uu))
    example={'T':3,'p':4,'target':'2','compiled_N':32,'uniform_N':64,'compiled_median_prefix_seconds':statistics.median(w['prefix_seconds'] for w in ww),'uniform_median_prefix_seconds':statistics.median(u['prefix_seconds'] for u in uu)}
    parts.append(f"One prospective tolerance illustrates the distinction between common-resolution speed and target work. At horizon three, price four and target two, witness crosses at N=32 while uniform FVI first crosses at N=64. Median complete-prefix times are {example['compiled_median_prefix_seconds']:.3f} and {example['uniform_median_prefix_seconds']:.3f} seconds, respectively. This is one economic cell with three timing repetitions. At target one, witness attains all twelve services and each FVI implementation attains six; none attains one half or one quarter at its cap.")

    (OUT/'interpretation48.tex').write_text('\n'.join(parts)+'\n')
    comp=read(R/'results/diagnostics/compiler.json');rows=[]
    for N in (4,8,16):
        z=[r for c in comp if c['N']==N for r in c['repetitions']]
        ratios=[(r['dense_load_seconds']+r['dense_query_seconds'])/(r['compile_seconds']+r['compiled_query_seconds']) for r in z]
        rows.append([N,len(z),num(statistics.median(ratios),2),num(min(ratios),2),num(max(ratios),2),num(statistics.median(r['compile_seconds']+r['compiled_query_seconds'] for r in z),4)])
    table('compiler48.tex','Fixed-policy representation costs, including compiler setup','tab:compiler48','rrrrrr',r'$N$ & Observations & Median ratio & Minimum & Maximum & Compiled (s)',rows,
          'The ratio is dense load-plus-query time divided by compiled setup-plus-query time, over the same original continuation and points. Each resolution crosses four economic cells and three repetitions. This is a same-policy representation experiment, not a construction-to-certificate speedup or an independently trained native comparator. Exact witness-index checks accompany the numerical interval checks.')
    rows=[]
    for d,T,m in itertools.product((3,4),(2,3),METHODS[:2]):
        c=lookup[d,T,1,m];rows.append([d,T,SHORT[m],c['N'],(c['N']+1)**d,num(c['bound']),num(c['median_seconds']),num(c['peak_rss_kib']/1024,1)])
    table('dimension48.tex','Executed nonlinear dimension stress cases','tab:dimension48','rrcrrrrr',r'$d$ & $T$ & Method & $N$ & States & Loss bound & Seconds & MiB',rows,
          'Price is one. Each service includes all three declared rungs and has one repetition. The maximum resolution differs by dimension and is not a matched-accuracy scaling design. The common innovation remains continuous; its quadrature remainder, state-dependent capacity and all-state loss account are retained.')
    direct=read(R/'audit/DIRECT_INTERVALS.json');assert len(direct)==48;rows=[]
    for T,p,b in itertools.product((2,3),(1,4),(0,6,10)):
        aa=[x for x in direct if (x['T'],x['price'],x['sensor_bits'])==(T,p,None if b==0 else b)];assert len(aa)==4
        lo=min(x['interval'][0] for x in aa);hi=max(x['interval'][1] for x in aa)
        sign=sum(x['sign']!='unresolved' for x in aa)
        # Infer from endpoints rather than relying on a display-name convention.
        sign=sum(x['interval'][1]<0 or x['interval'][0]>0 for x in aa)
        fee=sum(x['neither_direction_recoups_fee'] for x in aa)
        rows.append([T,p,'exact' if b==0 else b,'['+outward(lo,False)+', '+outward(hi,True)+']',f'{sign}/4',f'{fee}/4'])
    table('direct-summary48.tex','Direct witness-minus-FVI constrained-policy costs','tab:direct48','rrclrr',r'$T$ & $p$ & Sensor & Interval hull over four laws & Signed & No fee recovery',rows,
          'Each hull contains the four separate simultaneous intervals for the declared initial laws; it is not an all-state band. There are 48 contrasts, each with 262,144 common interval paths, and family error at most 0.01 under the independent-bin model. Signed counts identify intervals excluding zero. The final column counts intervals strictly inside $(-1/64,1/64)$, ruling out recouping either replacement fee. Display endpoints are rounded outward. The observation fee cancels when the two controllers use the same sensor.')
    sensors=read(R/'results/diagnostics/sensors.json');rows=[]
    for c in sensors:
        if c['N']!=16:continue
        for curve in c['curves']:
            best=next(r for r in curve['rows'] if r['bits']==curve['selected_bits'])
            rows.append([c['T'],c['p'],'$'+r'\frac{1}{'+str(F(curve['price_per_coordinate_bit']).denominator)+'}$',best['bits'],outward(F(best['acquisition_allowance']),True,4),outward(F(best['observation_charge']),True,4),outward(F(best['augmented_upper']),True,4)])
    table('sensors48.tex','Priced precision for the original finest witness policies','tab:sensors48','rrcrrrr',r'$T$ & $p$ & Bit price & $b_*$ & Acquisition & Fee & Total account',rows,
          'The original $N=16$ checkpoint is fixed. Prices are per coordinate-bit per date; $b$ ranges from four to sixteen and action spacing is $1/4096$. The selected bit count minimizes the exact augmented uniform upper account, not measured policy cost. All thirteen candidate precisions and the coarser original checkpoints remain in the evidence. Displayed nonnegative accounts are rounded upward.')
    # Every direct interval, not only an aggregate hull.
    text=r'\section{Every direct constrained-policy interval}\label{supp:direct-table48}'+'\n'
    text+='Intervals concern witness minus FVI expected resource cost. The fee column records the two-direction no-recoupment decision at $k=1/64$. The familywise statement is conditional on the independent-bin model. Displayed endpoints are rounded outward.\n'
    for T,p in itertools.product((2,3),(1,4)):
        rows=[]
        for law,b in itertools.product(('uniform','1/8','1/2','7/8'),(0,6,10)):
            x=next(x for x in direct if (x['T'],x['price'],x['initial_law'],x['sensor_bits'])==(T,p,law,None if b==0 else b))
            rows.append([law,'exact' if b==0 else b,outward(x['interval'][0],False),outward(x['interval'][1],True),'yes' if x['neither_direction_recoups_fee'] else 'unresolved',num(x['total_pair_seconds'],2)])
        name=f'direct-full48-T{T}-p{p}.tex'
        table(name,f'Direct intervals: horizon {T}, price {p}',f'tab:direct-full48-{T}-{p}','lcrrlr',r'Initial law & Bits & Lower & Upper & Fee & Joint seconds',rows,
              'Exact-state policies are unquantized. The finite-bit policies use robust capacity and downward action quantization. Joint seconds charge both policies, source loading, common simulation, interval statistics and durable output; they are not assigned to one method. The total-path numerical enclosure is distinct from sampling uncertainty.')
        text+='\\input{tables/'+name[:-4]+'}\n'
    (OUT/'direct-full48.tex').write_text(text)
    front=read(R/'audit/COMPLETE_WORK_FRONTIERS.json');text=r'\section{Complete first-certificate time partitions}\label{supp:frontier-table48}'+'\n'
    text+='Each row is a left-closed, right-open tolerance interval. At the exact rational left endpoint, each method uses its first qualifying checkpoint; a dash denotes nonattainment. The final interval extends to infinity. Displayed endpoints have six significant digits; exact boundaries and complete component counts are in the deposited machine-readable frontier. Times are median prefix seconds for two-state services and singleton prefix seconds for dimension stress cases. These partitions are retrospective descriptions of the frozen complete ladders, not new prospective targets.\n'
    for cell in front:
        d,T,p=cell['dimension'],cell['T'],cell['p'];rows=[]
        for row in cell['intervals']:
            out=[sig(row['epsilon_left_closed']),sig(row['epsilon_right_open'])]
            for m in METHODS:
                a=row['methods'].get(m);out+=['--','--'] if a is None else [a['N'],num(a['median_prefix_seconds'],3)]
            rows.append(out)
        name=f'frontier-full48-d{d}-T{T}-p{p}.tex'
        table(name,f'Full tolerance partition: dimension {d}, horizon {T}, price {p}',f'tab:frontier-full48-{d}-{T}-{p}','rrrrrrrr',r'$\varepsilon_L$ & $\varepsilon_R$ & $N_C$ & C (s) & $N_U$ & U (s) & $N_A$ & A (s)',rows,
              'The all-state loss certificate is the common stopping criterion. Prefix time includes all earlier failed rungs, own-future construction, integration, compilation or adaptive pilots, repair checks and checkpoint fsync. Independent policy-cost inference is a separate joint service. The adaptive-coordinate comparator is executed only in dimension two.')
        text+='\\input{tables/'+name[:-4]+'}\n'
    historical=read(R/'results/diagnostics/historical_scalar_clock_frontier.json');rows=[];historycounts=[]
    for cell in historical:
        c=collections.Counter()
        for row in cell['rows']:
            w=row['methods']['cone-witness'];u=row['methods']['spline-nearest']
            if w[0] is None and u[0] is None:c['neither']+=1
            elif w[0] is None:c['spline_only']+=1
            elif u[0] is None:c['witness_only']+=1
            else:
                a=statistics.median(x['prefix_seconds'] for x in w);b=statistics.median(x['prefix_seconds'] for x in u)
                c['witness_faster' if a<b else 'spline_faster' if a>b else 'equal']+=1
        historycounts.append({'T':cell['T'],'p':cell['p'],**dict(c)})
        rows.append([cell['T'],cell['p'],c['witness_faster'],c['spline_faster'],c['equal'],c['witness_only'],c['spline_only'],c['neither']])
    table('historical-clock48.tex','Historical scalar frontier using its original complete-prefix clocks','tab:historical-clock48','rrrrrrrr',r'$T$ & $p$ & W earlier & S earlier & Tie & W only & S only & Neither',rows,
          'Counts are tolerance intervals, not probabilities or weighted economic tasks. W is the R46 witness and S its spline comparator. These are unaltered historical internal prefix clocks, not R48 timings; they are never added to new compiler or direct-comparison clocks. The exact partitions, selected checkpoints and all three repeated times are retained.')
    text+='\\input{tables/historical-clock48}\n';(OUT/'frontier-full48.tex').write_text(text)
    publication={'common_target_prefix_times':paired,'historical_scalar_clock_intervals':historycounts,'adaptive_realization':adaptive,'prospective_target_example':example,'display_rules':'direct endpoints rounded outward; exact attainment and interval boundaries in JSON; counts not probabilities'}
    (R/'audit/EDITORIAL_NUMBERS.json').write_text(json.dumps(publication,indent=2,sort_keys=True)+'\n')
    summary_text="## Completed evidence\n\nThe audited execution contains "+str(s['services'])+" services and "+str(s['rungs'])+" recorded rungs. The direct comparison contains "+str(s['direct']['total_paths'])+" paired paths in 48 tasks.\n\n"
    summary_text+="| Method | Target 4 | Target 2 | Target 1 | Target 1/2 | Target 1/4 |\n|---|---:|---:|---:|---:|---:|\n"
    for m in METHODS:
        summary_text+='| '+m+' | '+' | '.join(str(s['core_attainment_out_of_12'][m][v])+'/12' for v in ('4','2','1','1/2','1/4'))+' |\n'
    summary_text+='\n'+ ' '.join(parts)+'\n\n'
    q=s['compiler']
    summary_text+=f"Across the {q['repetitions']} fixed-object representation observations, the median dense/compiled time ratio including setup is {q['median_dense_over_compiled_including_setup']:.3f}; its range is {q['min_ratio']:.3f} to {q['max_ratio']:.3f}. This is a representation result for identical mathematical objects, not an independently trained method comparison.\n\n"
    q=s['direct']
    summary_text+=f"The direct sign counts are {q['signs']}. In {q['fee_not_recouped_both_directions']} of 48 tasks the simultaneous interval lies strictly inside the predeclared replacement-fee band. The largest absolute endpoint is {q['max_absolute_endpoint']:.8f}; the largest interval width is {q['max_width']:.8f}. The measured joint direct-comparison services sum to {q['total_joint_pair_seconds']:.3f} seconds on the study runner, separately from construction clocks. These are fixed-policy and declared-information results, not an all-state or calibrated welfare ranking.\n"
    template=(R/'response-source.md').read_text();assert template.count('@@RESULTS48@@')==1
    (R/'response.md').write_text(template.replace('@@RESULTS48@@',summary_text))
    print(json.dumps(publication,indent=2))
if __name__=='__main__':main()
