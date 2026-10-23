"""Post-execution presentation adapter: no models, queries, or scientific edits.

Reads exclusively F125 saved campaign/audit/report evidence. Adds flat CSV,
main-paper and complete-catalog TeX, and further descriptive exact summaries.
The adapter identity is saved separately from the frozen scientific sources.
"""
from pathlib import Path
from fractions import Fraction as F
import collections,csv,gzip,hashlib,json,statistics,time
R=Path(__file__).resolve().parents[1];P=R/'results125';O=P/'presentation';T=R/'new125'
def load(p):return json.loads(p.read_text())
def rows(p):
 with (gzip.open(p,'rt') if p.suffix=='.gz' else p.open()) as f:return [json.loads(l) for l in f if l.strip()]
def mean(v):return sum((F(x) for x in v),F(0))/len(v)
def plain(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {str(k):plain(v) for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [plain(v) for v in x]
 return x
def save(p,x):
 with p.open('x') as f:json.dump(plain(x),f,indent=2,sort_keys=True);f.write('\n')
def fmt(x):return f'{float(F(x)):.7f}'
def tex(x):return str(x).replace('_',r'\_')
def csvwrite(path,rs,fields):
 with path.open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for r in rs:w.writerow({k:json.dumps(plain(r.get(k)),sort_keys=True) if isinstance(r.get(k),(dict,list,tuple)) else plain(r.get(k)) for k in fields})

def run():
 tick=time.perf_counter();O.mkdir(exist_ok=False);T.mkdir(exist_ok=True)
 data=rows(P/'primary/records125.jsonl.gz');cohorts=rows(P/'report/cohorts_summary125.jsonl');summary=load(P/'report/SUMMARY125.json')
 ind=load(P/'independent/SUMMARY125.json');checks=rows(P/'independent/checks125.jsonl')
 evalrows=rows(P/'independent/evaluations125.jsonl.gz');ev={r['key_id']:r for r in evalrows}
 control={(r['index'],r['budget'],r['arm'],r['training_loss'],r['row']):r for r in data if r['mode']=='fused_control'}
 ck=lambda r:tuple(r[k] for k in ('index','budget','arm','training_loss','mode','row'))
 checktable={ck(r):r for r in checks}
 qlower={}
 for v in ev.values():
  k=(tuple(v['state_hex']),v['alpha']);qlower[k]=max(qlower.get(k,F('-1000')),F(v['optimum_lower']))
 flattened=[];work_closure=[]
 for r in data:
  c=checktable[ck(r)];v=ev[c['final_key']];k=(tuple(v['state_hex']),v['alpha']);ir=F(v['j_upper'])-qlower[k]
  baseline=control.get((r['index'],r['budget'],r['arm'],r['training_loss'],r['row']))
  flattened.append(dict(**{k:r[k] for k in ('index','budget','arm','training_loss','mode','row','alpha','state125','action','complete_policy_lower','complete_policy_upper','certified_regret_upper','action_distance_upper','width','target_qualified125','accepted125','gain_lower125','new_terminal_nodes125','stop125','seconds125','counts125')},independent_j_lower=v['j_lower'],independent_j_upper=v['j_upper'],independent_regret_upper=ir,independent_action_distance_upper=float(ir)**.5,independent_contained=c['contained'],independent_gain_confirmed=c['gain_confirmed'],new_query_attempts=len(r['new_queries125']),baseline_same_return=baseline is not None and r['action_hex']==baseline['action_hex']))
  if r['mode'] in ('warm_adaptive','cold_adaptive','warm_fixed512'):
   actual=r['counts125'];prefix=r['complete_fused_prefix125']['counts']
   contexts=sum(actual.get(k,0)-prefix.get(k,0) for k in ('r96_midpoint_terminal_rows','r96_endpoint_terminal_rows'))
   queries=actual.get('r96_original_action_certificates',0)-prefix.get('r96_original_action_certificates',0)
   completed=sum(q['completed'] for q in r['new_queries125'])
   assert contexts==r['new_terminal_nodes125'] and queries==completed
   work_closure.append(dict(cohort=ck(r),actual_extra_terminal_contexts=contexts,actual_extra_queries=queries,reported_contexts=r['new_terminal_nodes125'],verified=True))
 save(O/'WORK_ACCOUNTING_CLOSURE125.json',dict(rows=len(work_closure),all_match=True,details=work_closure,scope='Post-execution exact identity between recorded operation-counter deltas and declared acquisition units; no new economics'))
 csvwrite(O/'decisions125.csv',flattened,list(flattened[0]))
 csvwrite(O/'cohorts125.csv',cohorts,list(cohorts[0]))
 primary_cohorts=rows(P/'primary/cohorts125.jsonl');primary_parent=load(P/'launch-primary/PROCESS125.json')
 primary_residual=F(primary_parent['seconds'])-sum((F(c['seconds']) for c in primary_cohorts),F(0))
 modes=('fused_control','warm_adaptive','cold_adaptive','warm_fixed512','grid33')
 ms=[]
 for m in modes:
  rr=[r for r in data if r['mode']==m];ss=[s for s in cohorts if s['mode']==m]
  pc=[c for c in primary_cohorts if c['mode']==m]
  ms.append(dict(mode=m,n=len(rr),accepted=sum(r['accepted125'] for r in rr),target=sum(r['target_qualified125'] for r in rr),new_queries=sum(len(r['new_queries125']) for r in rr),new_terminal_contexts=sum(r['new_terminal_nodes125'] for r in rr),complete_primary_parent_allocated_seconds=sum((F(c['seconds']) for c in pc),F(0))+primary_residual*len(pc)/len(primary_cohorts),measured_primary_cohort_seconds=sum((F(c['seconds']) for c in pc),F(0)),first_state_enhancement_queries=sum(len(r['new_queries125']) for r in rr if r['row']==0),cost_lower=mean([r['complete_policy_lower'] for r in rr]),cost_upper=mean([r['complete_policy_upper'] for r in rr]),regret_mean=mean([r['certified_regret_upper'] for r in rr]),regret_max=max(F(r['certified_regret_upper']) for r in rr),first_state_mean_timing_median=mean([s['timing_median'] for s in ss]),first_state_mean_timing_min=mean([s['timing_min'] for s in ss]),first_state_mean_timing_max=mean([s['timing_max'] for s in ss]),acquisition_mean=mean([s['acquisition'] for s in ss])))
 traditional=[]
 for arm in ('online','quadratic','relu','hinge','spline','poly2','poly3','grid','uniform_dp'):
  mode='grid33' if arm=='uniform_dp' else 'warm_adaptive'
  rr=[r for r in data if r['arm']==arm and r['mode']==mode];ss=[s for s in cohorts if s['arm']==arm and s['mode']==mode]
  traditional.append(dict(arm=arm,mode=mode,n=len(rr),cost_lower=mean([r['complete_policy_lower'] for r in rr]),cost_upper=mean([r['complete_policy_upper'] for r in rr]),regret_max=max(F(r['certified_regret_upper']) for r in rr),stronger_target=sum(r['target_qualified125'] for r in rr),accepted=sum(r['accepted125'] for r in rr),acquisition_mean=mean([s['acquisition'] for s in ss]),first_state_mean_timing_median=mean([s['timing_median'] for s in ss])))
 # Every neural-to-online comparison on the identical risk/state is retained;
 # aggregate only signed interval statements, without population inference.
 online={(r['index'],r['row']):r for r in data if r['arm']=='online' and r['mode']=='fused_control'}
 neural=[r for r in data if r['arm']=='relu'];comparisons=[]
 for r in neural:
  o=online[r['index'],r['row']]
  comparisons.append(dict(cohort=ck(r),difference_lower=F(r['complete_policy_lower'])-F(o['complete_policy_upper']),difference_upper=F(r['complete_policy_upper'])-F(o['complete_policy_lower'])))
 pairkey=lambda r:tuple(r[k] for k in ('index','budget','arm','training_loss','row'))
 warm={pairkey(r):r for r in data if r['mode']=='warm_adaptive'};fixed={pairkey(r):r for r in data if r['mode']=='warm_fixed512'}
 pairs=[dict(cohort=k,same_action=warm[k]['action_hex']==fixed[k]['action_hex'],same_target=warm[k]['target_qualified125']==fixed[k]['target_qualified125'],same_accepted=warm[k]['accepted125']==fixed[k]['accepted125'],same_cost_interval=warm[k]['complete_policy_lower']==fixed[k]['complete_policy_lower'] and warm[k]['complete_policy_upper']==fixed[k]['complete_policy_upper'],warm_minus_fixed_lower=F(warm[k]['complete_policy_lower'])-F(fixed[k]['complete_policy_upper']),warm_minus_fixed_upper=F(warm[k]['complete_policy_upper'])-F(fixed[k]['complete_policy_lower'])) for k in warm]
 paired_summary=dict(pairs=len(pairs),same_action=sum(p['same_action'] for p in pairs),same_target=sum(p['same_target'] for p in pairs),same_accepted=sum(p['same_accepted'] for p in pairs),same_cost_interval=sum(p['same_cost_interval'] for p in pairs),details=pairs)
 save(O/'descriptive125.json',dict(modes=ms,representations=traditional,warm_fixed_paired_comparison=paired_summary,neural_online_comparisons=comparisons,neural_strictly_worse=sum(r['difference_lower']>0 for r in comparisons),neural_strictly_better=sum(r['difference_upper']<0 for r in comparisons),neural_inconclusive=sum(r['difference_lower']<=0<=r['difference_upper'] for r in comparisons),scope='complete prespecified deterministic census; no population inference'))
 names={'fused_control':'Strong fused control','warm_adaptive':'Warm adaptive','cold_adaptive':'Cold adaptive','warm_fixed512':'Warm fixed 512','grid33':'Uniform 33-action DP'}
 lines=[r'\section{Original-economy action acquisition}',r'\label{sec:results125}',r'The prospectively frozen R125 census evaluates the four dyadic states $(1/4,1/4)$, $(1/4,3/4)$, $(3/4,1/4)$ and $(3/4,3/4)$ under both original risk levels. All 56 inherited actors, both original-model online controls, and both conventional action-grid controls are retained. These are fixed cases, not a population sample. The 936 original-service decisions all satisfy regret $1/256$ and value width $1/8192$; the separately specified stronger regret target is $1/65536$. The future controller and continuous-risk economic objective are unchanged.',r'\begin{table}[t]',r'\centering\small',r'\caption{Prospective original-action acquisition census}',r'\label{tab:acquisition125}',r'\begin{tabular}{lrrrrr}',r'\hline',r'Service & Decisions & Target & Gains & New contexts & Total seconds \\',r'\hline']
 for s in ms:lines.append(f"{names[s['mode']]} & {s['n']} & {s['target']} & {s['accepted']} & {s['new_terminal_contexts']:,} & {float(s['complete_primary_parent_allocated_seconds']):.3f} " + chr(92)*2)
 lines.extend([r'\hline',r'\end{tabular}',r'\par\smallskip\parbox{0.96\textwidth}{\footnotesize Strict gains are relative to the completed strong fused prefix. New contexts count every paid midpoint and endpoint at every attempted precision; all prefix and rejected-candidate work is additionally charged. Total seconds sum complete four-state cohort clocks and their equal share of the observed parent residual. This is one execution, not a timing confidence interval; historical acquisition is separately charged in the complete catalog. Uniform DP does not claim a strict gain over a prefix.}',r'\end{table}'])
 w=next(s for s in ms if s['mode']=='warm_adaptive');f=next(s for s in ms if s['mode']=='warm_fixed512');reduction=1-F(w['new_terminal_contexts'],f['new_terminal_contexts'])
 slow=F(w['complete_primary_parent_allocated_seconds'])/F(f['complete_primary_parent_allocated_seconds'])-1
 lines.append(f"Warm adaptive and fixed-512 localization both attain the stronger target in {w['target']} of 232 services and certify {w['accepted']} additional strict original-policy gains. Adaptive precision uses {float(reduction)*100:.2f} percent fewer extra terminal contexts, but requires {float(slow)*100:.2f} percent more complete elapsed time in this primary execution. Its extra interval algebra and coarse queries therefore matter economically. The two services return identical action bits in {paired_summary['same_action']}/232 pairs and identical cost intervals in {paired_summary['same_cost_interval']}/232; all 232 target and acceptance indicators agree. Thus equal target attainment does not imply identical policies. One singleton-bracket case remains below the stronger certification target for both methods; cold localization retains three maximum-center stops. No exceptions were recorded in the enhancement services.")
 lines.append(r'The singleton case isolates a remaining implementation issue. It is the risk-$1/2$, budget-5, marginal-fitted cubic actor at $(1/4,3/4)$, returning $a=3/16$ with the exact original-optimizer bracket $[3/16,3/16]$. Its retained level-based certificate is $1.7807343\times10^{-5}$, above the stronger target. The terminal action-radius bound of Theorem~\ref{thm:paidwork125} would give $\delta$ at this already optimal original action. That terminal gate is not implemented in the frozen service; we therefore retain the failed target and the count 231/232. The diagnostic distinguishes action uncertainty from absolute-value precision without changing an observed outcome.')
 lines.append(f"All 702 decisions in three serial timing passes reproduce the primary action, certificate, stopping reason and operation counts. The saved-algebra audit executes {summary['algebra_and_timing_audit']['checks']:,} assertions, including 128 matched ReLU/ordinary-hinge pairs. The independent rational original-law audit confirms {ind['contained']} of {ind['decisions']} production intervals by containment and {ind['accepted_gain_confirmed']} of {ind['accepted']} accepted gain bounds, with {ind['contradictions']} contradictions. Any unresolved check remains explicitly unresolved. The audit uses {ind['audit_terminal_nodes']:,} terminal contexts and retains all original continuous-risk primal--dual witnesses.")
 lines.append(f"Complete-cost neural adoption is assessed only on the first-state workload for which three complete timing processes were observed. Of {summary['neural_adoption_regions']} prespecified risk/budget/loss/service and amortization comparisons, {summary['empty_sufficient']} sufficient and {summary['empty_optimistic']} optimistic price regions are empty. These conditional timing comparisons are not statistical confidence statements. Full four-state original-value intervals, regret and action-distance bounds, acquisition charges, complete measured service costs and failures are provided in the development companion and machine-readable catalog.")
 lines.append(r'All 58 learned/online prefixes already meet the stronger target at that first state, so the three repeated timing passes execute zero additional localization queries in each of the four prefix-based services. They therefore do not measure the precision-acquisition tradeoff observed in the other census states. The complete primary clocks above retain that work, with one observed execution. Nonempty optimistic adoption regions express unresolved comparisons; no sufficient neural adoption region is certified.')
 lines.append(r'The support-complete interpolation theorem and its exact rational witnesses have a separate evidential role: the production services above use original-support and derivative-envelope acquisition, not an implemented full-support conic solver. The strict support witness verifies an economic contrast improvement relative to omitting paid information; its endpoint bound is also attained by cheap direct support evaluation. Neither result supplies a neural-specific separation from matched hinge features.')
 (T/'numerical_results125.tex').write_text('\n'.join(lines)+'\n')
 dev=[r'\section{Complete R125 execution and cohort catalog}',r'\label{dev:results125}',r'The following tables retain every prespecified cohort. Each economic row averages exactly the same four states; the value endpoints enclose the average original implemented-policy cost. Timing summaries refer only to $(1/4,1/4)$ and include equal allocation of each observed parent-process residual. Historical acquisition charges include labels, fitting and audits as allocated in the unchanged M121 ledger; they are not newly measured standalone clocks. The full historical research total remains unknown because earlier interrupted parent clocks are absent.',r'\subsection{Representation comparison under warm adaptive localization}',r'Both fitting losses and both information budgets enter each learned-representation row with equal weights; no best configuration is selected. Online and action-grid rows use the same state and risk weights.',r'\begin{center}\small',r'\begin{tabular}{lrrrr}',r'\hline',r'Representation & Mean original $J$ interval & Max regret & Target & Mean acquisition (s) \\',r'\hline']
 for s in traditional:dev.append(f"{tex(s['arm'])} & $[{fmt(s['cost_lower'])},{fmt(s['cost_upper'])}]$ & {float(s['regret_max']):.3g} & {s['stronger_target']}/{s['n']} & {float(s['acquisition_mean']):.4f} " + chr(92)*2)
 dev.extend([r'\hline\end{tabular}\end{center}',r'\subsection{Every frozen cohort}',r'Risk codes 0 and 1 denote $1/2$ and $3/4$. Loss codes V and M denote value and marginal fitting; O denotes online and D denotes action-grid DP. Service codes F,A,C,X,G denote strong fused, warm adaptive, cold adaptive, warm fixed-512 and uniform DP. The gain and target entries are counts out of four. The separate CSV records all source identities, operation counters, independent checks, action errors and stopping reasons.',r'\begingroup\scriptsize\setlength{\tabcolsep}{3pt}',r'\begin{longtable}{r r l c c l r r r}',r'\hline',r'Risk & Budget & Representation & Loss & Svc & Mean original $J$ interval & Gains & Target & New contexts \\',r'\hline\endfirsthead',r'\hline Risk & Budget & Representation & Loss & Svc & Mean original $J$ interval & Gains & Target & New contexts \\ \hline\endhead'])
 modesym={'fused_control':'F','warm_adaptive':'A','cold_adaptive':'C','warm_fixed512':'X','grid33':'G'};losssym={'value':'V','marginal':'M','online':'O','none':'D'}
 for s in cohorts:dev.append(f"{s['index']} & {s['budget']} & {tex(s['arm'])} & {losssym[s['training_loss']]} & {modesym[s['mode']]} & $[{fmt(s['cost_lower'])},{fmt(s['cost_upper'])}]$ & {s['accepted']} & {s['stronger_target']} & {s['new_terminal_nodes']} " + chr(92)*2)
 dev.extend([r'\hline\end{longtable}\endgroup',r'\subsection{Complete service costs}',r'All times below are seconds. The brackets are the minimum and maximum of three serial complete first-state service measurements after allocation of the whole parent-process residual; they have no coverage-probability interpretation. Fitting, acquisition, and earlier training-audit costs are charged separately. Each historical allocation is reproduced unchanged, including the parent ReLU cost needed to construct its matched hinge representation.',r'\begingroup\scriptsize\setlength{\tabcolsep}{4pt}',r'\begin{longtable}{r r l c c r l}',r'\hline',r'Risk & Budget & Representation & Loss & Svc & Acquisition & Complete first-state time \\',r'\hline\endfirsthead',r'\hline Risk & Budget & Representation & Loss & Svc & Acquisition & Complete first-state time \\ \hline\endhead'])
 for s in cohorts:dev.append(f"{s['index']} & {s['budget']} & {tex(s['arm'])} & {losssym[s['training_loss']]} & {modesym[s['mode']]} & {float(F(s['acquisition'])):.5f} & $[{float(F(s['timing_min'])):.6f},{float(F(s['timing_max'])):.6f}]$ " + chr(92)*2)
 dev.extend([r'\hline\end{longtable}\endgroup',r'\subsection{Failure and verification ledger}',r'The initial non-economic metadata probe requested the version of an optional package, \texttt{numba}, that was not installed. Its failed receipt is retained; the unchanged production kernel uses NumPy and does not require that package. A corrected static receipt verifies all nine new Python modules and all 56 acquired model hashes. No original economic pilot preceded the public F125 source boundary.'])
 for name in ('fixtures','primary','timing0','timing1','timing2','verification','independent','report'):
  e=load(P/f'launch-{name}/PROCESS125.json');dev.append(f"The {tex(name)} process exited with code {e['returncode']} and an observed whole-parent clock of {e['seconds']:.6f} seconds.")
 diagnostic=load(P/'postfreeze-terminal-diagnostic/EXECUTION125.json')
 dev.append(r'The separately identified post-freeze terminal-gate diagnostic independently transcribes the rational derivative-radius recovery from the saved support and verifies a strictly negative derivative at the upper action boundary. It confirms the analytic $J$-regret bound $15/16777216$ without another original economic query. The reported target failures and frozen service outputs are unchanged. Its measured diagnostic clock and source identity are retained separately from the experimental campaign.')
 (T/'development_results125.tex').write_text('\n'.join(dev)+'\n')
 identity={'adapter_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_manifest_sha256':hashlib.sha256((R/'SOURCE_FREEZE125.json').read_bytes()).hexdigest(),'input_report_sha256':hashlib.sha256((P/'report/SUMMARY125.json').read_bytes()).hexdigest(),'seconds':time.perf_counter()-tick,'economic_evaluations':0,'scientific_source_changed':False,'post_execution_reporting_adapter':True,'postfreeze_terminal_diagnostic_receipt':diagnostic,'outputs':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(list(O.glob('*'))+[T/'numerical_results125.tex',T/'development_results125.tex']) if p.is_file()}}
 save(O/'PRESENTATION125.json',identity)
 print(json.dumps(plain(identity),sort_keys=True))
if __name__=='__main__':run()
