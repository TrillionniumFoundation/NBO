"""Create every new publication table from the full execution record."""
from pathlib import Path
import collections,hashlib,json,math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
NAMES={'myopic':'Current only','quadratic':'Quadratic','rbf':'Radial basis','NBO':'NBO','shared_actor':'Shared actor','SAA':'Cached SAA','enumerated':'Enumerated'}
METHODS=list(NAMES);QS=[1,4,16,64,256,1024]

def mean(rs,key):return float(np.mean([r[key] for r in rs]))
def sci(x):
    if x==0:return '$0$'
    e=math.floor(math.log10(abs(x)));v=x/10**e
    return f'${v:.2f}\\times10^{{{e}}}$'
def escape(s):return str(s).replace('_',r'\_')
def table(caption,label,cols,head,rows,note=''):
    return ('\\begin{table}[htbp]\n\\centering\\small\n\\caption{'+caption+'}\\label{'+label+'}\n'
      +'\\begin{tabular}{'+cols+'}\n\\toprule\n'+head+'\\\\\n\\midrule\n'
      +'\n'.join(' & '.join(row)+r'\\' for row in rows)+'\n\\bottomrule\n\\end{tabular}\n'
      +(r'\par\smallskip\begin{minipage}{.96\textwidth}\footnotesize '+note+r'\end{minipage}'+'\n' if note else '')+'\\end{table}\n')

def make():
    s=json.loads((ROOT/'results/registered/SUMMARY.json').read_text());rs=s['records'];out=ROOT/'results/generated';out.mkdir(exist_ok=True)
    if s['expected_count']!=252 or len(rs)!=252 or s['failures']:raise ValueError('incomplete registered study: publish failures explicitly before using tables')
    by={(r['dimension'],r['queries'],r['stream'],r['method']):r for r in rs}
    if len(by)!=252:raise ValueError('duplicate execution identities')
    def cell(d,m,q=None):return [r for r in rs if r['dimension']==d and r['method']==m and (q is None or r['queries']==q)]
    checks=[]
    for r in rs:
        passed=[j+1 for j,x in enumerate(r['stages']) if x['certificate']['mean_regret_upper']<=1e-4]
        checks.append((not passed or passed[0]==len(r['stages'])) and ((r['status']=='certified')==bool(passed)))
        for stage in r['stages']:
            c=stage['certificate'];g=np.array(c['regret_upper']);k=np.array(c['kappa_lower'])
            checks.append(len(g)==r['queries'] and np.all(k>0) and float(np.mean(g))<=c['mean_regret_upper']*(1+1e-13))
        components=r['task_initialization_seconds']+sum(x['fit_and_cache_seconds']+x['query_seconds']+x['verification_seconds'] for x in r['stages'])
        checks.append(r['accounted_service_seconds']>=components)
    if not all(checks):raise ValueError('record consistency check failed')
    def put(name,x):(out/name).write_text(x)
    rows=[]
    for m in METHODS:
        a=cell(10,m);b=cell(50,m)
        rows.append([NAMES[m],f'{sum(r["status"]=="certified" for r in a)}/18',f'{sum(r["status"]=="certified" for r in b)}/18',sci(max(r['final_certificate_upper'] for r in a)),sci(max(r['final_certificate_upper'] for r in b))])
    put('accuracy_table.tex',table('Prospective scalar-interval accuracy','tab:r19accuracy','lrrrr',r'Procedure & $d=10$ passes & $d=50$ passes & $d=10$ max. $U$ & $d=50$ max. $U$',rows,'Each dimension has six separately executed query volumes and three complete streams. A pass means the mean true scalar-regret upper bound is at most $10^{-4}$. Maxima retain unresolved outcomes and every declared stage.'))
    ft=''
    selected=['quadratic','rbf','NBO','shared_actor','SAA','enumerated']
    for d in [10,50]:
        rows=[]
        for q in QS:
            row=[str(q)]
            for m in selected:
                rr=cell(d,m,q);v=mean(rr,'accounted_service_seconds');n=sum(r['status']=='certified' for r in rr)
                row.append(f'{v:.3f}'+(r'$^{'+str(n)+r'/3}$' if n<3 else ''))
            rows.append(row)
        ft+=table(f'Executed work-to-tolerance frontier, dimension {d}',f'tab:r19frontier{d}','rrrrrrr',r'$Q$ & Quad. & RBF & NBO & Actor & SAA & Enum.',rows,'Mean complete warm-service seconds over three independent streams, including all fits, queries, failed checks, and durable stage records. A superscript reports fewer than three passes; such an entry is not a certified alternative for every stream. No superscript means three passes. Current-only costs and the complete stage decomposition appear in the technical record.')
    put('frontier_tables.tex',ft)
    nbo=[r for r in rs if r['method']=='NBO'];neuralpasses=sum(r['status']=='certified' for r in nbo)
    first=sum(r['status']=='certified' and r['selected_stage']==1 for r in nbo)
    actor=[r for r in rs if r['method']=='shared_actor'];ap=sum(r['status']=='certified' for r in actor)
    nr=max(r['final_certificate_upper'] for r in nbo)
    diag=sum(r['post_stop_diagnostics_seconds'] for r in rs);bill=sum(r['accounted_service_seconds'] for r in rs)
    wins=collections.Counter()
    for d in [10,50]:
        for q in QS:
            elig=[m for m in METHODS if all(r['status']=='certified' for r in cell(d,m,q))]
            wins[min(elig,key=lambda m:mean(cell(d,m,q),'accounted_service_seconds'))]+=1
    narrative=f'NBO attains the declared scalar-interval tolerance in {neuralpasses} of its 36 complete runs, including {first} at the first declared fitting stage. Its largest returned mean-regret upper bound is {sci(nr)}. The shared conditional actor attains the target in {ap} of 36 runs; all remaining outcomes stay unresolved rather than being replaced. The conventional regressions and structure-exploiting simulation procedures are retained on the same accuracy and cost basis.\n\n'
    narrative+='Across the twelve dimension--query-volume cells, the lowest mean service cost among methods certified in all three streams belongs to '+', '.join(f'{NAMES[m]} in {v} cells' for m,v in wins.items())+'. This is an observed comparison among the declared procedures on the reported machine, not a statistical assertion of minimum possible computation. Validation work is included in every entry and becomes a substantial part of the large-query bill. Consequently, reducing the query cost alone need not produce the same ranking as reducing the total work to the economic target.\n\n'
    narrative+=f'The complete comparison uses {s["full_comparative_wall_seconds"]:.3f} measured seconds in its reported service environment. The sum of all method service bills is {bill:.3f} seconds, and the separately identified post-stop mechanism calculations use {diag:.3f} seconds. Shared startup and remaining driver and individual-record overhead are part of the full comparison, not retrospectively assigned to a selected winner. Serialization of the final aggregate summary and publication generation are outside that clock.\n'
    put('results_narrative.tex',narrative)
    rows=[]
    for d in [10,50]:
        for m in ['quadratic','rbf','NBO','SAA','enumerated']:
            rr=cell(d,m,1024);mm=[r['mechanism'] for r in rr]
            rows.append([str(d),NAMES[m],sci(mean(mm,'exogenous_absolute_risk')),sci(mean(mm,'exogenous_centered_risk')),sci(mean(mm,'own_action_absolute_risk')),sci(mean(mm,'exogenous_catalogue_regret'))])
    put('risk_table.tex',table('Common-action and own-action assessment at 1,024 queries','tab:r19risk','rlrrrr',r'$d$ & Predictor & Absolute & Centered & Own-action & Menu loss',rows,'Prediction entries are squared continuation errors relative to full-support means. Menu loss is a payoff difference on the common three-action catalogue, not scalar-interval regret. Means cover all three independently regenerated caches. Current-only and shared-actor procedures do not define scalar predictors. These are finite-design descriptive averages, not confidence intervals over unobserved training streams.'))
    rows=[]
    for d in [10,50]:
        for m in METHODS:
            rr=cell(d,m,1024)
            fixed=np.mean([r['task_initialization_seconds']+sum(x['fit_and_cache_seconds'] for x in r['stages']) for r in rr]);query=np.mean([sum(x['query_seconds'] for x in r['stages']) for r in rr]);ver=np.mean([sum(x['verification_seconds'] for x in r['stages']) for r in rr]);total=mean(rr,'accounted_service_seconds')
            rows.append([str(d),NAMES[m],f'{fixed:.3f}',f'{query:.3f}',f'{ver:.3f}',f'{total:.3f}'])
    comp=table('Complete stage-cost decomposition at 1,024 queries','tab:r19components','rlrrrr',r'$d$ & Procedure & Fixed/cache/fit & Queries & All checks & Total',rows,'Seconds, averaged over all three streams. Fixed cost includes model and task initialization. Total additionally includes durable stage records and measured timing metadata. Multiple declared stages are all charged; the table is not a selected-fit clock.')
    rows=[]
    for d in [10,50]:
        for m in METHODS:
            rr=cell(d,m,1024);mm=[r['mechanism'] for r in rr]
            rows.append([str(d),NAMES[m],f'{mean(mm,"withdrawal_mean"):.5f}',f'{mean(mm,"withdrawal_change_from_zero_charge_mean"):.5f}',sci(mean(rr,'external_log_grant_bound_mean'))])
    econ=table('Temporary-charge decisions and external compensation','tab:r19economic','rlrrr',r'$d$ & Procedure & Withdrawal & Change vs. zero charge & Grant bound',rows,'All 1,024 tasks and three streams. The zero-charge query uses the same fitted object and changes only the current charge. The external grant uses $A_0w\\log(1+g)$ and does not change production or the future policy. Grant entries are descriptive binary64 conversions of the certified regret upper bounds; the primary machine certificate remains the regret bound itself.')
    # Complete aggregate frontier includes the otherwise omitted current-only method.
    lines=[r'\begin{longtable}{rrlrrr}',r'\caption{All complete procedure cells}\label{tab:r19allcells}\\',r'\toprule $d$ & $Q$ & Procedure & Passes & Mean seconds & Max. regret upper\\\midrule',r'\endfirsthead',r'\toprule $d$ & $Q$ & Procedure & Passes & Mean seconds & Max. regret upper\\\midrule',r'\endhead']
    for d in [10,50]:
        for q in QS:
            for m in METHODS:
                rr=cell(d,m,q)
                lines.append(' & '.join([str(d),str(q),NAMES[m],str(sum(r['status']=='certified' for r in rr))+'/3',f'{mean(rr,"accounted_service_seconds"):.4f}',sci(max(r['final_certificate_upper'] for r in rr))])+r'\\')
    lines+=[r'\bottomrule',r'\end{longtable}']
    record=r'''\section{Prospective Experiment: Complete Record}\label{app:r19record}
The execution modules and the two finite economic inputs match the original
implementation freeze. This integrated execution replays that fixed design;
it is not an additional independent experiment. The original descriptive
design file is not reconstructed byte for byte. Its replacement documents
the unchanged executable choices and is explicitly identified as such.
Three fitting/cache streams, two dimensions, six query volumes and seven
procedures give 252 actual service runs. Their task prefixes are deliberately
shared, so the 252 runs are not claimed to be statistically independent.
Synthetic dimension-three algebra checks are not economic observations.
No registered seed, budget, tolerance or architecture was changed using
integrated outcomes.

The stored JSON records contain every selected action, per-task lower curvature
bound, outward derivative endpoints, individual regret upper bounds, cache
indices, attempted stage, time component, failure status, and post-stop diagnostic.
The data report generator checks unique identities, the first-success stopping
rule, positive curvature, arithmetic summaries, and that reported service time
covers all timed components. These record-consistency checks supplement, rather
than replace, the mathematical enclosure proof.

'''+comp+econ+'\n'.join(lines)+'\n'
    put('record.tex',record)
    audit=dict(expected=252,completed=len(rs),failures=s['failures'],record_checks=len(checks),all_record_checks=all(checks),nbo_passes=neuralpasses,nbo_first_stage_passes=first,nbo_max_regret_upper=nr,cell_cost_winners=dict(wins),full_comparison_seconds=s['full_comparative_wall_seconds'],service_seconds=bill,post_stop_diagnostic_seconds=diag)
    (ROOT/'results/REPORT_AUDIT.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
    print(json.dumps(audit,indent=2))
if __name__=='__main__':make()
