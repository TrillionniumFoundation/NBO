"""Publication tables from the corrected, completely replayed R67 catalogue."""
from pathlib import Path
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
import json,statistics,collections,math
R=Path(__file__).resolve().parents[1]
LABEL={'adaptive':'Adaptive','bisection':'Bisection','upper-minimizer':'Upper chord','relu':'ReLU','quadratic':'Quadratic','linear':'Linear','spline':'Spline','nearest':'Nearest','derivative':'Derivative','heuristic':'Midpoint','simplicial':'Triangle'}
ORDER=tuple(LABEL)[:-1]
def read(p):return json.loads(Path(p).read_text())
def write(p,text):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix=='.tex' and any(ord(c)<32 and c not in '\n\r\t' for c in text):raise ValueError('LaTeX control byte')
    p.write_text(text)
def med(x):return statistics.median(x)
def num(x,d=3):return f'{x:.{d}f}'
def out(x,lower=False,d=5):
    return format(Decimal.from_float(float(x)).quantize(Decimal(10)**(-d),rounding=ROUND_FLOOR if lower else ROUND_CEILING),'f')
def band(x,d=5):return '['+out(x[0],True,d)+', '+out(x[1],False,d)+']'
def table(name,caption,heads,rows,note,cols=None,long=False):
    cols=cols or 'l'+'r'*(len(heads)-1);label='tab:'+name
    if long:
        start='\\begingroup\\small\\setlength{\\tabcolsep}{4pt}\n\\begin{longtable}{'+cols+'}\n\\caption{'+caption+'}\\label{'+label+'}\\\\\n\\toprule\n'
        head=' & '.join(heads)+r' \\'+'\n\\midrule\n';start+=head+'\\endfirsthead\n'+head+'\\endhead\n'
        end='\n\\bottomrule\n\\end{longtable}\n\\endgroup\n\\noindent '+note+'\n'
    else:
        start='\\begin{table}[htbp]\n\\centering\n\\caption{'+caption+'}\\label{'+label+'}\n{\\small\\setlength{\\tabcolsep}{4pt}\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+' & '.join(heads)+r' \\'+'\n\\midrule\n'
        end='\n\\bottomrule\n\\end{tabular}}\n\\par\\smallskip\n{\\footnotesize '+note+'}\n\\end{table}\n'
    write(R/'tables'/(name+'.tex'),start+'\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+end)

def main():
    audit=read(R/'audit/RESULT_AUDIT67.json');rows=audit['summaries'];groups={g:[x for x in rows if x['spec']['group']==g] for g in ('comparison','reuse','inference','vector')}
    cold=[];cold_summary=[]
    for d,T in ((2,2),(8,3)):
        for kind in ORDER:
            part=[x for x in groups['comparison'] if (x['spec']['d'],x['spec']['T'],x['spec']['kind'])==(d,T,kind)]
            if not part:continue
            warns=sum(len(z['warnings']) for x in part for z in x['training']['dates']);q=med([x['counts']['q_queries'] for x in part]);seconds=med([x['complete_seconds'] for x in part]);train=med([x['training']['seconds'] for x in part])
            cold.append([f'{d}/{T}',LABEL[kind],len(part),int(q),num(train),num(seconds),warns])
            cold_summary.append(dict(d=d,T=T,kind=kind,processes=len(part),queries_median=q,full_seconds_median=seconds,full_seconds_min=min(x['complete_seconds'] for x in part),full_seconds_max=max(x['complete_seconds'] for x in part),warnings=warns))
    table('comparison67','Ten selectors at the same original-optimum contract',
        ['$d/T$','Selector','Runs','Queries','Fit (s)','Full (s)','Warnings'],cold,
        'Targets are $1/128$ for $d/T=2/2$ and $1/64$ for $8/3$. Full time is the parent launch-through-join receipt. Fitted selectors use eight declared seeds and two process repetitions; unfitted controls have two repetitions. Fit includes labels. Query and time entries are medians, not optimizer-success probabilities. Warning counts retain every executed fit. All arms use the same outward pre-query screen.','rlrrrrr')
    cost=[];differences=[]
    for x in groups['inference']:
        for kind,v in x['absolute_cost'].items():cost.append([f"{x['spec']['d']}/{x['spec']['T']}",LABEL[kind],band(v)])
        for key,v in x['contrasts'].items():differences.append([f"{x['spec']['d']}/{x['spec']['T']}",key.replace('-minus-',' $-$ ').replace('quadratic','Quadratic').replace('adaptive','Adaptive').replace('bisection','Bisection').replace('relu','ReLU'),band(v)])
    table('cost67','Expected cost of the actual callable controllers', ['$d/T$','Controller','Expected-cost interval'],cost,
        'There are 8,192 distinct IID-model common-path rows per task, with continuous 48-bit initial and innovation bins and full tail bounds on ambiguous acquisition. The simultaneous family error is $1/100$ across both tasks, all absolute costs and paired differences. Endpoints are rounded outward. Repeated R66/R67 streams are counted only once.','rlc')
    table('differences67','All paired expected-cost differences', ['$d/T$','Difference','Simultaneous interval'],differences,
        'Every interval is formed from paired path endpoints, not by subtracting the printed marginal confidence intervals. All six contrasts per task are retained. The sample stream is common within a task; method arms are not additional independent rows.','rlc')
    reuse=[];crossings=[]
    for d,T in ((2,2),(8,3)):
        for kind in ('adaptive','bisection','relu','quadratic'):
            part=[x for x in groups['reuse'] if (x['spec']['d'],x['spec']['T'],x['spec']['kind'])==(d,T,kind)]
            if not part:continue
            for x in part:
                ctrl=next(v for v in groups['reuse'] if (v['spec']['d'],v['spec']['T'],v['spec']['kind'],v['spec']['repeat'])==(d,T,'adaptive',x['spec']['repeat']))
                wins=[a['cumulative_seconds']<b['cumulative_seconds'] for a,b in zip(x['blocks'],ctrl['blocks'])]
                crossings.append(dict(key=x['spec']['key'],matched_control=ctrl['spec']['key'],first_prefix_crossing=next((i+1 for i,z in enumerate(wins) if z),None),
                    persistent_prefix_crossing_within_window=next((i+1 for i in range(len(wins)) if all(wins[i:])),None),full_process_win=x['complete_seconds']<ctrl['complete_seconds'],
                    prefix_scope='through each durable block record, before final summary and process exit; not an unexecuted full-process stopping cost'))
            full=[x['complete_seconds'] for x in part];wins=sum(z['full_process_win'] for z in crossings if z['key'] in [x['spec']['key'] for x in part])
            reuse.append([f'{d}/{T}',LABEL[kind],len(part),num(med(full)),f'{min(full):.3f}--{max(full):.3f}',f'{wins}/{len(part)}',sum(not b['identity_valid'] for x in part for b in x['blocks'])])
    table('reuse67','Prospective twenty-four-block model reuse', ['$d/T$','Selector','Runs','Full (s)','Full range (s)','Wins','Declines'],reuse,
        'Full time includes imports, fitting, model serialization, all loads and identity checks, twenty-four new workloads, the stale-contract fallback, all durable records and process exit. Wins compare matched repetition numbers with adaptive search; trained methods retain both declared seeds. Each service declines block index 7. Prefix crossings are separately recorded and are not labeled full-process break-even times.','rlrrcrr')
    progress=[]
    for d,T in ((2,2),(8,3)):
        for kind in ORDER:
            part=[x for x in groups['comparison'] if (x['spec']['d'],x['spec']['T'],x['spec']['kind'],x['spec']['repeat'])==(d,T,kind,0)]
            if not part:continue
            total=lambda key:sum(x['diagnostics'][key] for x in part)
            progress.append([f'{d}/{T}',LABEL[kind],total('refinements'),total('routed'),total('routed_zero_progress'),total('upper_only'),total('lower_only'),total('both_progress'),total('screen_returns')])
    table('progress67','Where verification work makes progress', ['$d/T$','Selector','Queries','Routed','Zero','Upper','Lower','Both','Screen'],progress,
        'Only one copy of each distinct transcript is counted. Queries denotes new refinements, not initial boundary queries. Zero counts routed queries that improve neither global endpoint; Upper, Lower and Both classify all refinements. Screen counts returns without a new endpoint query. Numeric upper and lower increments and every zero-progress row remain in the raw records.','rlrrrrrrr',True)
    vector=[]
    for x in groups['vector']:
        co=x['counts'];vector.append([x['spec']['d'],x['spec']['T'],num(x['complete_seconds']),co['q_queries'],co['shock_children'],co['max_batch'],x['peak_rss_kib'],co['rational_fallbacks']])
    table('vector67','Coupled two-control, two-innovation query scaling', ['$d$','$T$','Full (s)','Queries','Descendants','Batch','RSS (KiB)','Recovery'],vector,
        'Each service evaluates four designed initial states (all coordinates 0, 1, $1/4$ or $3/4$), with continuous-bin innovations, at target $1/4$. No state lattice or trained two-output selector is loaded. Batch is the largest recorded query batch, not the total number of live descendant states. RSS is process peak memory. Horizon-four cost is retained rather than extrapolated from the shorter horizons.','rrrrrrrr')
    # Full seed-level medians and warnings; the two repetitions remain in JSON.
    seeds=[]
    for d,T in ((2,2),(8,3)):
        for kind in ('relu','quadratic','linear','spline','nearest'):
            for seed in range(6601,6609):
                part=[x for x in groups['comparison'] if (x['spec']['d'],x['spec']['T'],x['spec']['kind'],x['spec']['seed'])==(d,T,kind,seed)]
                if not part:continue
                seeds.append([f'{d}/{T}',LABEL[kind],seed,med([x['counts']['q_queries'] for x in part]),num(med([x['complete_seconds'] for x in part])),sum(len(z['warnings']) for x in part for z in x['training']['dates'])])
    table('seeds67','Every fitting seed and its complete process cost', ['$d/T$','Selector','Seed','Queries','Full (s)','Warnings'],seeds,
        'Each row contains the median of two clock repetitions of that declared fitting seed. The repetitions reproduce a model and transcript and are not two independent fitting initializations. All warnings, including lack of optimizer convergence, are retained.','rlrrrr',True)
    crossrows=[]
    for x in crossings:
        if '-adaptive-' in x['key']:continue
        spec=next(z['spec'] for z in groups['reuse'] if z['spec']['key']==x['key'])
        crossrows.append([f"{spec['d']}/{spec['T']}",LABEL[spec['kind']],spec['seed'],spec['repeat'],x['first_prefix_crossing'] or '--',x['persistent_prefix_crossing_within_window'] or '--','yes' if x['full_process_win'] else 'no'])
    table('crossings67','Measured reuse crossings without extrapolation', ['$d/T$','Selector','Seed','Rep.','First','Persistent','Full win'],crossrows,
        'First and Persistent are block counts within the fixed twenty-four-block window, for cumulative clocks through durable block records. Persistent means no reversal within the observed remainder, not beyond it. Full win uses the separately recorded launch-through-exit process time. A dash means no crossing observed.','rlrrrrc',True)
    analysis=dict(status='derived_from_passed_corrected_audit',cold=cold_summary,reuse_crossings=crossings,
        expected_cost_contrasts_all_unresolved=all(v[0]<=0<=v[1] for x in groups['inference'] for v in x['contrasts'].values()),
        inference_rows=audit['independent_continuous_law_rows'],fitting_seeds=8,
        warnings_total=sum(len(z['warnings']) for x in rows if 'training' in x for z in x['training']['dates'])+sum(len(z['warnings']) for x in groups['inference'] for arm in x['arms'] for z in arm['training']['dates']),
        all_state_tables_zero=all(x['counts']['stored_state_nodes']==0 for x in rows if 'counts' in x),
        vector_services=len(groups['vector']),new_data_scope='Corrected rerun; old R66 streams not counted twice')
    write(R/'audit/ANALYSIS67.json',json.dumps(analysis,sort_keys=True,indent=2)+'\n')
    print(json.dumps({key:val for key,val in analysis.items() if key not in ('cold','reuse_crossings')},indent=2))
if __name__=='__main__':main()
