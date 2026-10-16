"""Exact finite-catalogue accounting of the frozen R108-source reproduction.
No new fit, sample, policy choice, or clock measurement is made here.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
import argparse, json, hashlib, statistics

ARMS=('online','quadratic','relu','hinge','spline','poly2','poly3','grid')
SERVICES=('legacy','compiled','legacy-safe','compiled-safe')
NAMES={'online':'Online','quadratic':'Quadratic (rank 6)','relu':'ReLU (rank 6)','hinge':'Same-geometry hinge','spline':'Coordinate spline','poly2':'Full quadratic','poly3':'Full cubic','grid':'Bilinear grid'}
def f(x): return F(float(x))
def mean(xs): return sum(xs,F(0))/len(xs)
def exact(x):return str(x)
def outward(x,places=6,upper=False):
    with localcontext() as c:
        c.prec=100
        return format((Decimal(x.numerator)/Decimal(x.denominator)).quantize(Decimal(10)**-places,rounding=ROUND_CEILING if upper else ROUND_FLOOR),'f')
def inter(lo,hi,places=6):return '['+outward(lo,places)+', '+outward(hi,places,True)+']'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,sort_keys=True,indent=2,allow_nan=False)+'\n')
def analyze(out,root):
    reference=read(out/'REFERENCE.json')['records'];summaries=[];pairs=[];acquisition=[];identities=[]
    for i,alpha in enumerate((.5,.75)):
        ref=reference[i]
        for arm in ARMS:
            ar=read(out/'models'/f'{i}-{arm}'/'acquisition.json')
            shared=read(out/'models'/f'{i}-relu'/'acquisition.json') if arm=='hinge' else ar
            # Standalone published engineering charge includes labels, production
            # fitting, independent audit and actually executed serialization.
            # For hinge include the parent ReLU work and its own extra encoding.
            label=ar['label_cost_if_standalone_seconds']
            charge=label+sum(shared.get(k,0) for k in ('fit_seconds','audit_seconds','serialization_seconds'))
            if arm=='hinge':charge+=ar['serialization_seconds']
            ac={'risk_index':i,'alpha':alpha,'arm':arm,'standalone_acquisition_seconds':charge,
                'label_seconds':label,'payload_bytes':ar['payload_bytes'],'record_sha256':digest(out/'models'/f'{i}-{arm}'/'acquisition.json'),
                'not_a_complete_research_selection_charge':True,'complete_research_work_reported_separately':True}
            for k in ('fit_seconds','audit_seconds','coefficients','features','audit','fit'):
                if k in shared:ac[k]=shared[k]
            acquisition.append(ac)
            for service in SERVICES:
                p=out/'catalogue'/f'{i}-{arm}-{service}.json';data=read(p);rows=data['rows']
                costlo=mean([f(r['lower']) for r in rows]);costhi=mean([f(r['upper']) for r in rows])
                rl=[];ru=[]
                for j,r in enumerate(rows):
                    lower=max(F(0),f(r['lower'])-f(ref['upper'][j]))
                    upper=min(f(r['loss']), f(r['upper'])-max(f(r['optimum_lower']),f(ref['optimum_lower'][j])))
                    if not 0<=lower<=upper:raise ArithmeticError('Contradictory original-optimum brackets')
                    rl.append(lower);ru.append(upper)
                timing=[read(out/'timing'/f'{j}-{i}-{arm}-{service}.json') for j in range(7)]
                clock=[a['seconds'] for a in timing]
                entry={'risk_index':i,'alpha':alpha,'arm':arm,'service':service,'states':len(rows),
                    'cost_mean_lower':exact(costlo),'cost_mean_upper':exact(costhi),'cost_mean_display':inter(costlo,costhi),
                    'reference_sharpened_mean_regret_lower':exact(mean(rl)), 'reference_sharpened_mean_regret_upper':exact(mean(ru)),
                    'reference_sharpened_regret_display':inter(mean(rl),mean(ru)),
                    'maximum_native_regret_bound':max(r['loss'] for r in rows),
                    'maximum_action_distance_bound':max(r['action_distance_upper'] for r in rows),
                    'maximum_policy_width':max(r['width'] for r in rows),
                    'first_rejections':sum(r['first_rejected'] for r in rows),
                    'safe_change_events':sum(r['safe_changes'] for r in rows),
                    'safe_changed_states':sum(r['safe_changes']>0 for r in rows),
                    'exact_fallback_states':sum(r['exact_fallback'] for r in rows),
                    'bin_counts':{str(n):sum(r['bins']==n for r in rows) for n in sorted({r['bins'] for r in rows})},
                    'catalogue_seconds':data['seconds'],'counts':data['counts'],
                    'clock_32_states_all_seven_seconds':clock,'clock_median':statistics.median(clock),
                    'clock_minimum':min(clock),'clock_maximum':max(clock),
                    'standalone_acquisition_plus_median_32_seconds':charge+statistics.median(clock),
                    'peak_process_rss_kib_in_timing':max(t['max_rss_kib'] for t in timing),
                    'rss_is_cumulative_process_not_isolated_arm':True,
                    'source_file_sha256':digest(p)}
                gainlo=[];gainhi=[]
                for r in rows:
                    if r['action']==r['completed_baseline_action']:
                        gainlo.append(F(0));gainhi.append(F(0))
                    else:
                        if not r['safe_changes']>0:raise ArithmeticError('Unexplained changed action')
                        lo=f(r['baseline_lower'])-f(r['upper']);hi=f(r['baseline_upper'])-f(r['lower'])
                        if not 0<lo<=hi:raise ArithmeticError('Strict improvement not certified')
                        gainlo.append(lo);gainhi.append(hi)
                entry['same_backend_baseline_mean_gain_lower']=exact(mean(gainlo))
                entry['same_backend_baseline_mean_gain_upper']=exact(mean(gainhi))
                entry['same_backend_gain_display']=inter(mean(gainlo),mean(gainhi),8)
                summaries.append(entry)
            # True matched policy contrasts to online and quadratic at same backend.
            for service in SERVICES:
                own=read(out/'catalogue'/f'{i}-{arm}-{service}.json')['rows']
                for control in ('online','quadratic'):
                    base=read(out/'catalogue'/f'{i}-{control}-{service}.json')['rows'];l=[];u=[];identical=0
                    for x,y in zip(own,base):
                        if x['action']==y['action']:l.append(F(0));u.append(F(0));identical+=1
                        else:l.append(f(x['lower'])-f(y['upper']));u.append(f(x['upper'])-f(y['lower']))
                    ml,mu=mean(l),mean(u)
                    pairs.append({'alpha':alpha,'arm':arm,'service':service,'control':control,'mean_cost_difference_lower':str(ml),
                                  'mean_cost_difference_upper':str(mu),'display':inter(ml,mu,8),
                                  'identical_policy_rows':identical,'catalogue_cost_order':'lower' if mu<0 else 'higher' if ml>0 else 'identity' if ml==mu==0 else 'unresolved',
                                  'not_population_inference':True})
        for service in SERVICES:
            relu=read(out/'catalogue'/f'{i}-relu-{service}.json');hinge=read(out/'catalogue'/f'{i}-hinge-{service}.json')
            keys=('action','proposed','lower','upper','optimum_lower','loss','width','safe_changes')
            identities.append({'alpha':alpha,'service':service,'policy_and_bound_fields_exactly_equal':all(a[k]==b[k] for a,b in zip(relu['rows'],hinge['rows']) for k in keys),
                               'all_rows_exactly_equal':relu['rows']==hinge['rows'],'all_trials_exactly_equal':relu['trials']==hinge['trials']})
    historical=read(root/'evidence109/failed-inherited-replay/TESTS95.json')
    failures={'test_cases':sum(v['tests'] for v in historical.values()),'failure_assertions':sum(v['failures'] for v in historical.values()),
              'errors':sum(v['errors'] for v in historical.values()),'suites_passed':sum(v['passed'] for v in historical.values()),
              'suites_total':len(historical),'status':'failed; missing archival dependencies and pinned-file assertion retained, no green full-history claim'}
    report={'scope':'R109 finite-catalogue reproduction of unchanged R108 source; no other experiment substituted; no new random population sample',
            'source_commit':'29180a4ce4a6db7298e7458ecdfff3da08abb08f','manuscript_baseline':'f78d7fcec9f657dfec56a0af7899fe967948652d',
            'record_audit':{k:v for k,v in read(out/'AUDIT108.json').items() if k!='files'},
            'kernel_audit':{k:v for k,v in read(out/'KERNEL_AUDIT108.json').items() if k!='rows'},
            'campaign':read(out/'CAMPAIGN108.json'),'machine':read(out/'START.json')['machine'],
            'historical_replay':failures,'summary_rows':summaries,'acquisition':acquisition,'pairwise_costs':pairs,'hinge_identities':identities,
            'reference_expense_seconds':sum(v['seconds'] for v in reference),
            'statistical_confidence_intervals':False,'neural_specific_frontier_claim':False,'calibrated_adoption_claim':False}
    write(root/'evidence109/SUMMARY109.json',report)
    index={(r['risk_index'],r['arm'],r['service']):r for r in summaries}
    # All-arm timing/resource frontier, both risk levels and acquisition fully visible.
    t=r'''\begin{table}[htbp]\caption{Complete-service clocks and standalone acquisition}\label{tab:clocks109}
\centering\small
\begin{tabular}{@{}lrrrrrr@{}}\toprule
&\multicolumn{3}{c}{$\alpha=1/2$}&\multicolumn{3}{c}{$\alpha=3/4$}\\
Representation&Acquire&Legacy&Compiled&Acquire&Legacy&Compiled\\\midrule
'''
    for arm in ARMS:
        vals=[]
        for i in range(2):
            a=next(r for r in acquisition if r['risk_index']==i and r['arm']==arm)
            vals += [a['standalone_acquisition_seconds'],index[i,arm,'legacy']['clock_median'],index[i,arm,'compiled']['clock_median']]
        t+=NAMES[arm]+' & '+' & '.join(f'{v:.4f}' for v in vals)+r'\\'+'\n'
    t+=r'''\bottomrule\end{tabular}
\par\smallskip\begin{minipage}{.98\linewidth}\footnotesize
Seconds. Service entries are medians of all seven sequential fresh-process 32-state repetitions, including qualification and fallback. Acquisition includes paid common labels, fitting, independent numerical audit and serialization; it is charged in full to each standalone fitted arm. Hinge pays its shared ReLU acquisition. All clock ranges and cumulative process memory are in the Development Appendix. Full research, comparator selection, reference and timing work is separately recorded; these standalone charges are not the cost of selecting the best arm after seeing this table. Full polynomial and grid arms are strong resource-frontier controls, not equal-memory comparisons.
\end{minipage}\end{table}
'''
    (root/'new109/clocks.tex').write_text(t)
    t=r'''\begin{table}[htbp]\caption{Actual policy costs and paid safeguarded improvement}\label{tab:economics109}
\centering\scriptsize
\begin{tabular}{@{}llrrr@{}}\toprule
$\alpha$&Representation&Compiled mean cost&Mean cost reduction&Changed states\\\midrule
'''
    for i in range(2):
        for arm in ARMS:
            r=index[i,arm,'compiled'];s=index[i,arm,'compiled-safe']
            t+=('$1/2$' if i==0 else '$3/4$')+' & '+NAMES[arm]+' & '+r['cost_mean_display']+' & '+s['same_backend_gain_display']+' & '+str(s['safe_changed_states'])+r'/64\\'+'\n'
    t+=r'''\bottomrule\end{tabular}
\par\smallskip\begin{minipage}{.98\linewidth}\footnotesize
Outward numerical intervals average all 64 declared states, not a random sample. Cost reductions compare the improved policy with its completed same-backend incumbent and the same actual terminal policy. Identical actions have exactly zero contrast; every changed action passes strict interval separation. Every refused trial is charged. These gains do not assert that the extra computation is economical at an unmeasured compute price. Full safe-service clocks, both backends, sharpened regret and all pairwise original-cost contrasts are retained.
\end{minipage}\end{table}
'''
    (root/'new109/economics.tex').write_text(t)
    t=r'''\section{Full current finite-catalogue accounts}\label{dev:catalogue109}
\begingroup\scriptsize
\begin{longtable}{@{}llrrrrr@{}}\caption{All arms and services: seven-clock ranges and action qualification}\label{tab:all109}\\
\toprule $\alpha$ / arm & Service & Min sec & Median & Max sec & Reject & Changes\\\midrule\endfirsthead
\toprule $\alpha$ / arm & Service & Min sec & Median & Max sec & Reject & Changes\\\midrule\endhead
'''
    for r in summaries:
        t+=f"{r['alpha']} / {r['arm']} & {r['service']} & {r['clock_minimum']:.5f} & {r['clock_median']:.5f} & {r['clock_maximum']:.5f} & {r['first_rejections']} & {r['safe_change_events']}"+r'\\'+'\n'
    t+=r'\bottomrule\end{longtable}\endgroup'+'\nChanges are accepted update events, not necessarily distinct states. Clocks cover 32 states; rejection and change counts cover all 64 catalogue states. Process RSS is cumulative, not an isolated per-arm allocation. All primitive and query-event categories remain separate in the machine-readable ledger and are not added up as FLOPs.\n'
    t+=r'''\begingroup\scriptsize
\begin{longtable}{@{}lllrr@{}}\caption{All original-policy cost and reference-sharpened regret intervals}\\
\toprule $\alpha$ / arm & Service & Mean policy cost & Mean regret upper & Max action bound\\\midrule\endfirsthead
\toprule $\alpha$ / arm & Service & Mean policy cost & Mean regret upper & Max action bound\\\midrule\endhead
'''
    for r in summaries:
        t+=f"{r['alpha']} / {r['arm']} & {r['service']} & {r['cost_mean_display']} & {outward(F(r['reference_sharpened_mean_regret_upper']),7,True)} & {r['maximum_action_distance_bound']:.6f}"+r'\\'+'\n'
    t+=r'\bottomrule\end{longtable}\endgroup'+'\nMean regret bounds intersect native qualification with the separately charged reference bracket. Action-distance entries are bounds, not observed exact action errors. All pairwise cost-difference intervals, including unresolved signs, are in SUMMARY109.json.\n'
    (root/'new109/full_tables.tex').write_text(t)
    print(json.dumps({'summary_rows':len(summaries),'pairs':len(pairs),'safe_updates':sum(r['safe_change_events'] for r in summaries),'all_hinge_exact':all(r['all_rows_exactly_equal'] for r in identities),'historical_replay':failures},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args();analyze(a.results,a.root)
