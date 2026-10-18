"""Exact catalogue accounting and current tables, never fitting or retiming.

Outputs are arithmetic summaries of every recorded row. Observed clocks are
engineering descriptions. No selection of theta, samples, actors or repetitions
is performed. Use python code110/analyze110.py from the delivered package.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
import json,statistics,hashlib,csv
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'raw110/r108-reproduction';NEW=ROOT/'raw110/gain-budget'
ARMS=('online','quadratic','relu','hinge','spline','poly2','poly3','grid')
SERVICES=('compiled','compiled-safe','gain-12','gain-14','gain-16','gain-18')
NAMES={'online':'Online','quadratic':'Quadratic (rank 6)','relu':'ReLU (rank 6)','hinge':'Equivalent hinge','spline':'Coordinate spline','poly2':'Full quadratic','poly3':'Full cubic','grid':'Bilinear grid'}
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def f(x):return F(float(x))
def mean(a):return sum(a,F(0))/len(a)
def dec(x,n=7,upper=False):
 x=F(x)
 with localcontext() as c:
  c.prec=110
  return format((Decimal(x.numerator)/Decimal(x.denominator)).quantize(Decimal(10)**-n,rounding=ROUND_CEILING if upper else ROUND_FLOOR),'f')
def interval(a,b,n=8):return '['+dec(a,n)+', '+dec(b,n,True)+']'
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n')
def contrast(a,b):
 # Both policies use exactly the same future controller and original law.
 lo=[];hi=[];ids=0
 for x,y in zip(a,b):
  if (x['x0'],x['x1'])!=(y['x0'],y['x1']):raise ValueError('Unmatched economic contexts')
  if x['action']==y['action']:lo.append(F(0));hi.append(F(0));ids+=1
  else:lo.append(f(x['lower'])-f(y['upper']));hi.append(f(x['upper'])-f(y['lower']))
 ml,mh=mean(lo),mean(hi)
 return {'lower':str(ml),'upper':str(mh),'display':interval(ml,mh),'identity_rows':ids,
   'ordering':'lower' if mh<0 else 'higher' if ml>0 else 'identity' if ml==mh==0 else 'unresolved',
   'finite_catalogue_not_population':True}
def main():
 ref=read(OLD/'REFERENCE.json')['records'];allrows=[];ac=[];ident=[]
 for i,alpha in enumerate((.5,.75)):
  for arm in ARMS:
   ar=read(OLD/'models'/f'{i}-{arm}'/'acquisition.json')
   shared=read(OLD/'models'/f'{i}-relu'/'acquisition.json') if arm=='hinge' else ar
   charge=ar['label_cost_if_standalone_seconds']+sum(shared.get(k,0) for k in ('fit_seconds','audit_seconds','serialization_seconds'))
   if arm=='hinge':charge+=ar['serialization_seconds']
   ac.append({'risk_index':i,'arm':arm,'source':ar,'shared_acquisition_record':shared if arm=='hinge' else None,
      'standalone_charge_seconds':charge,'actual_model_sha256':ar['model_sha256']})
   full=read(NEW/'catalogue'/f'{i}-{arm}-compiled-safe.json')['rows']
   plain=read(NEW/'catalogue'/f'{i}-{arm}-compiled.json')['rows']
   for svc in SERVICES:
    p=NEW/'catalogue'/f'{i}-{arm}-{svc}.json';d=read(p);rr=d['rows']
    timing=[read(NEW/'timing'/f'{r}-{i}-{arm}-{svc}.json') for r in range(7)]
    clocks=[v['seconds'] for v in timing]
    stop=[v for v in rr if v.get('stopped',False)];allow=[];regretlo=[];regrethi=[]
    for j,(x,y) in enumerate(zip(rr,full)):
     if x['action']==y['action']:allow.append(F(0))
     else:
      hi=max(F(0),f(x['upper'])-f(y['lower']))
      if x.get('stopped',False):hi=min(hi,f(x['stop_certificate']['loss']))
      allow.append(hi)
     lb=max(f(x['optimum_lower']),f(ref[i]['optimum_lower'][j]))
     ul=f(x['upper'])-lb
     ll=max(F(0),f(x['lower'])-f(ref[i]['upper'][j]))
     if not 0<=ll<=ul:raise ArithmeticError('Contradictory original reference')
     regretlo.append(ll);regrethi.append(min(ul,f(x['loss'])))
    stopbudget=mean([f(v['stop_certificate']['loss']) if v.get('stopped',False) else F(0) for v in rr])
    rec={'risk_index':i,'alpha':alpha,'arm':arm,'service':svc,'theta':d['theta'],
      'state_count':len(rr),'original_cost_lower':str(mean([f(v['lower']) for v in rr])),
      'original_cost_upper':str(mean([f(v['upper']) for v in rr])),
      'original_cost_display':interval(mean([f(v['lower']) for v in rr]),mean([f(v['upper']) for v in rr]),7),
      'reference_sharpened_mean_regret_lower':str(mean(regretlo)),
      'reference_sharpened_mean_regret_upper':str(mean(regrethi)),
      'max_native_regret_upper':max(v['loss'] for v in rr),
      'max_width':max(v['width'] for v in rr),'max_action_distance_bound':max(v['action_distance_upper'] for v in rr),
      'first_rejections':sum(v['first_rejected'] for v in rr),
      'update_events':sum(v['safe_changes'] for v in rr),
      'changed_states':sum(v['safe_changes']>0 for v in rr),'stopped_states':len(stop),
      'skipped_pairs':sum(v.get('skipped',False) for v in d['trials']),
      'active_pairs':sum(not v.get('skipped',False) for v in d['trials']),
      'stop_checks':d.get('stop_checks',0),'counts':d['counts'],
      'cost_minus_plain':contrast(rr,plain),'cost_minus_full_safe':contrast(rr,full),
      'mean_foregone_gain_upper':str(mean(allow)),
      'weighted_stop_budget':str(stopbudget),
      'all_seven_clocks':clocks,'clock_median':statistics.median(clocks),
      'clock_min':min(clocks),'clock_max':max(clocks),
      'standalone_acquisition_charge':charge,
      'standalone_acquisition_plus_32_median':charge+statistics.median(clocks),
      'cumulative_process_rss_kib':max(v['max_rss_kib'] for v in timing),
      'rss_is_not_isolated_arm_allocation':True,'raw_sha256':sha(p)}
    allrows.append(rec)
  for svc in SERVICES:
   a=read(NEW/'catalogue'/f'{i}-relu-{svc}.json');b=read(NEW/'catalogue'/f'{i}-hinge-{svc}.json')
   ident.append({'risk_index':i,'service':svc,'rows_exactly_equal':a['rows']==b['rows'],'trials_exactly_equal':a['trials']==b['trials']})
 idx={(x['risk_index'],x['arm'],x['service']):x for x in allrows}
 comparisons=[]
 for i in range(2):
  for svc in SERVICES:
   for a in ARMS:
    for b in ARMS:
     if a>=b:continue
     comparisons.append({'risk_index':i,'service':svc,'arm':a,'comparator':b,
       **contrast(read(NEW/'catalogue'/f'{i}-{a}-{svc}.json')['rows'],read(NEW/'catalogue'/f'{i}-{b}-{svc}.json')['rows'])})
 history=read(ROOT/'evidence110/failed-inherited-replay/TESTS95.json')
 oldaudit=read(OLD/'AUDIT108.json');newaudit=read(NEW/'AUDIT110.json');kaudit=read(OLD/'KERNEL_AUDIT108.json')
 report={'revision':'R110','protocol_commit':'f43602de6a29132feceb36d4b323c4c21a9e6ebe',
   'source_freeze_commit':'5e1eae8a7017dd728b71440de3368062700fd747',
   'frozen_reproduced_source':'29180a4ce4a6db7298e7458ecdfff3da08abb08f',
   'primary_theta':'1/65536','unseen_sample_claim':False,'population_inference_claim':False,
   'neural_exclusive_advantage_claim':False,'calibrated_adoption_claim':False,
   'complete_experiment_other_episodes_claim':False,
   'reproduction_campaign':read(OLD/'CAMPAIGN108.json'),
   'gain_campaign':read(NEW/'CAMPAIGN110.json'),
   'reproduction_audit':{k:v for k,v in oldaudit.items() if k!='files'},
   'gain_audit':{k:v for k,v in newaudit.items() if k!='files'},
   'kernel_audit':{k:v for k,v in kaudit.items() if k!='rows'},
   'inherited_replay':{'tests':sum(v['tests'] for v in history.values()),'errors':sum(v['errors'] for v in history.values()),
      'failures':sum(v['failures'] for v in history.values()),'passed_suites':sum(v['passed'] for v in history.values()),'suites':len(history)},
   'machine':read(OLD/'START.json')['machine'],'summary_rows':allrows,'acquisition':ac,
   'equivalent_hinge_checks':ident,'all_pairwise_catalogue_costs':comparisons,
   'reference_benchmark_seconds':sum(r['seconds'] for r in ref),
   'raw_directory_manifest':{str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'raw110').rglob('*')) if p.is_file()}}
 save(ROOT/'evidence110/SUMMARY110.json',report)
 # Core table: every arm at both risks, primary theta only, no selected winner.
 t=r'''\begin{table}[htbp]\caption{Primary remaining-gain budget: complete work and actual foregone improvement}\label{tab:budget110}
\centering\scriptsize
\begin{tabular}{@{}llrrrrr@{}}\toprule
$\alpha$ & Arm & Full-safe & Budgeted & Omitted & Updates & Extra mean cost $\times10^6$\\\midrule
'''
 for i in range(2):
  for arm in ARMS:
   a=idx[i,arm,'compiled-safe'];b=idx[i,arm,'gain-16'];co=b['cost_minus_full_safe']
   t+=('$1/2$' if i==0 else '$3/4$')+' & '+NAMES[arm]+f" & {a['clock_median']:.4f} & {b['clock_median']:.4f} & {b['skipped_pairs']}/192 & {b['update_events']} & "+interval(F(co['lower'])*10**6,F(co['upper'])*10**6,3)+r'\\'+'\n'
 t+=r'''\bottomrule\end{tabular}
\par\smallskip\begin{minipage}{.98\linewidth}\footnotesize
Times are medians of all seven fresh-process 32-state repetitions, in seconds. Omitted support/trial pairs and update events refer to all 64 catalogue states. Extra mean cost is budgeted minus full-safe actual original-policy cost; outward numerical intervals, not confidence intervals. The declared primary budget is $2^{-16}$; the original loss target remains $1/256$ and width target $1/8192$. A positive extra cost is foregone improvement, not concealed as equal accuracy. All acquisition is additional and reported separately. Identical actions give exactly zero contrast. Update events can exceed the number of distinct changed states.
\end{minipage}\end{table}
'''
 (ROOT/'new110/budget_table.tex').write_text(t)
 # Primary original objectives, regret, action bounds and acquisition frontier.
 t=r'''\begin{table}[htbp]\caption{Original-policy quality and standalone acquisition at the primary budget}\label{tab:quality110}
\centering\scriptsize
\begin{tabular}{@{}llrrrr@{}}\toprule
$\alpha$ & Arm & Mean original cost & Mean regret upper & Max action bound & Acquire sec\\\midrule
'''
 for i in range(2):
  for arm in ARMS:
   b=idx[i,arm,'gain-16']
   t+=('$1/2$' if i==0 else '$3/4$')+' & '+NAMES[arm]+' & '+b['original_cost_display']+' & '+dec(b['reference_sharpened_mean_regret_upper'],8,True)+' & '+dec(f(b['max_action_distance_bound']),6,True)+f" & {b['standalone_acquisition_charge']:.4f}"+r'\\'+'\n'
 t+=r'''\bottomrule\end{tabular}
\par\smallskip\begin{minipage}{.98\linewidth}\footnotesize
All 64 states, equal weights. Regret is sharpened with a separately charged original-law reference bracket; no exact optimum is provided for free. Action-distance entries are outward bounds from original action curvature two, not measured errors against an exact actor. Acquisition includes paid labels, all fitting trials, independent numerical fitting audit and serialization. Hinge pays the same shared ReLU acquisition; larger polynomial and grid payloads are explicit resource-frontier controls. Cumulative process RSS is not mislabeled isolated arm memory. No population welfare ordering or calibrated adoption is claimed.
\end{minipage}\end{table}
'''
 (ROOT/'new110/quality_table.tex').write_text(t)
 # All sensitivities; include adverse opportunity cost and every clock range.
 t=r'''\section{Complete current catalogue and sensitivity ledger}\label{dev:catalogue110}
The following entries cover every prespecified arm, risk level and gain budget. All numerical intervals are outward bounds on the declared deterministic catalogue. Timing extrema are observed ranges, not confidence intervals. Full operation-category and memory records, fitted payloads and all pairwise cost contrasts are in the machine-readable package.
\begingroup\scriptsize
\begin{longtable}{@{}llrrrr@{}}\caption{All six services: complete clocks, trial allocation and foregone gain}\\
\toprule $\alpha$ / arm & Service & Clock range & Median & Omitted & Extra mean cost $\times10^6$\\\midrule\endfirsthead
\toprule $\alpha$ / arm & Service & Clock range & Median & Omitted & Extra mean cost $\times10^6$\\\midrule\endhead
'''
 for b in allrows:
  co=b['cost_minus_full_safe']
  t+=f"{b['alpha']} / {b['arm']} & {b['service']} & [{b['clock_min']:.4f}, {b['clock_max']:.4f}] & {b['clock_median']:.4f} & {b['skipped_pairs']} & "+interval(F(co['lower'])*10**6,F(co['upper'])*10**6,3)+r'\\'+'\n'
 t+=r'\bottomrule\end{longtable}\endgroup'+'\n'
 t+=r'''\begingroup\scriptsize
\begin{longtable}{@{}lllrrr@{}}\caption{Every current original-policy cost, regret and action bound}\\
\toprule $\alpha$ / arm & Service & Mean original cost & Mean regret upper & Max action bound & Updates\\\midrule\endfirsthead
\toprule $\alpha$ / arm & Service & Mean original cost & Mean regret upper & Max action bound & Updates\\\midrule\endhead
'''
 for b in allrows:
  t+=f"{b['alpha']} / {b['arm']} & {b['service']} & {b['original_cost_display']} & "+dec(b['reference_sharpened_mean_regret_upper'],8,True)+' & '+dec(f(b['max_action_distance_bound']),6,True)+f" & {b['update_events']}"+r'\\'+'\n'
 t+=r'\bottomrule\end{longtable}\endgroup'+'\n'
 # Current reproduction, all four services, not historical R109 clocks.
 t+=r'''\begingroup\scriptsize
\begin{longtable}{@{}llrrrr@{}}\caption{Separate unchanged-R108-source reproduction: all four complete services}\\
\toprule $\alpha$ / arm & Service & Clock min & Median & Clock max & Update events\\\midrule\endfirsthead
\toprule $\alpha$ / arm & Service & Clock min & Median & Clock max & Update events\\\midrule\endhead
'''
 repro=[]
 for i,alpha in enumerate((.5,.75)):
  for arm in ARMS:
   for svc in ('legacy','compiled','legacy-safe','compiled-safe'):
    p=OLD/'catalogue'/f'{i}-{arm}-{svc}.json';d=read(p);cc=[read(OLD/'timing'/f'{j}-{i}-{arm}-{svc}.json')['seconds'] for j in range(7)]
    updates=sum(v['safe_changes'] for v in d['rows'])
    repro.append({'risk_index':i,'arm':arm,'service':svc,'clock_seven':cc,'counts':d['counts'],'updates':updates,'rows':len(d['rows']),'raw_sha256':sha(p)})
    t+=f'{alpha} / {arm} & {svc} & {min(cc):.4f} & {statistics.median(cc):.4f} & {max(cc):.4f} & {updates}'+r'\\'+'\n'
 t+=r'\bottomrule\end{longtable}\endgroup'+'\n'
 (ROOT/'new110/full_tables.tex').write_text(t)
 save(ROOT/'evidence110/REPRODUCTION_SUMMARY110.json',repro)
 with (ROOT/'evidence110/MAIN_TABLE110.csv').open('w') as fp:
  fields=['risk_index','arm','service','theta','original_cost_display','reference_sharpened_mean_regret_upper','max_action_distance_bound','clock_min','clock_median','clock_max','standalone_acquisition_charge','skipped_pairs','update_events','stopped_states','mean_foregone_gain_upper']
  w=csv.DictWriter(fp,fieldnames=fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in allrows)
 primary=[x for x in allrows if x['service']=='gain-16'];full=[x for x in allrows if x['service']=='compiled-safe']
 print(json.dumps({'summaries':len(allrows),'pairwise_comparisons':len(comparisons),'all_hinge_identities':all(x['rows_exactly_equal'] and x['trials_exactly_equal'] for x in ident),
   'primary_skipped':sum(x['skipped_pairs'] for x in primary),'primary_update_events':sum(x['update_events'] for x in primary),
   'full_update_events':sum(x['update_events'] for x in full),'primary_extra_cost_largest_upper':max(float(F(x['cost_minus_full_safe']['upper'])) for x in primary),
   'historical_replay':report['inherited_replay']},indent=2))
if __name__=='__main__':main()
