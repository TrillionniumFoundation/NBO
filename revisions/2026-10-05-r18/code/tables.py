"""Generate publication tables only from complete, immutable report families."""
from pathlib import Path
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
import json
R=Path(__file__).resolve().parents[1]
ROOT=R.parents[1]
NAMES={'original_low':'Low','quarterly_reuse':'Quarterly','long_reuse':'Long','untouched_intermediate':'Intermediate'}
METHODS={'reference':'Reference','nbo_scalar':'NBO','vector_costate':'Vector','raw_actor':'Raw actor','dpo_actor':'DPO','raw_saa':'SAA'}
def directed(x,upper,scale=1,significant=3):
 with localcontext() as ctx:
  ctx.prec=60
  d=Decimal.from_float(float(x))*Decimal(scale)
  if not d:return '0'
  quantum=Decimal(1).scaleb(d.adjusted()-significant+1)
  return format(d.quantize(quantum,rounding=ROUND_CEILING if upper else ROUND_FLOOR),'f')
def candidate(s):
 m,_,stage=s.partition('@');return METHODS[m]+(f' ({stage})' if stage else '')
def generate():
 risk=json.loads((ROOT/'revisions/2026-10-05-r17/results/RISK_REPORT.json').read_text())
 cat=json.loads((R/'results/CATALOGUE_REPORT.json').read_text())
 if not risk['complete'] or len(risk['rows'])!=24 or len(cat['rows'])!=8:raise ValueError('incomplete evidence')
 lines=[r'\begin{table}[htbp]\centering',r'\caption{Conditional Continuation-Risk Differences}\label{tab:r18risk}',r'\small\setlength{\tabcolsep}{4pt}',r'\begin{tabular}{lrccc}\toprule',r'Design & $d$ & Raw: 4 paths & Raw: 16 paths & Raw: 64 paths\\\midrule']
 for name in NAMES:
  for d in (10,50):
   rr=[next(z for z in risk['rows'] if z['calibration']==name and z['dimension']==d and z['raw_paths']==k) for k in (4,16,64)]
   cells=[f"$[{directed(z['lower'],False,100000000)},\\,{directed(z['upper'],True,100000000)}]$" for z in rr]
   lines.append(f'{NAMES[name]} & {d} & '+' & '.join(cells)+r'\\')
 lines += [r'\bottomrule\end{tabular}',r'\par\vspace{4pt}\begin{minipage}{.97\textwidth}\footnotesize',r'Notes: All intervals are for $R_N-R_R$, in units of $10^{-8}$. Negative intervals favor NBO. Endpoints are rounded outward to three significant digits; the complete precision is retained in the report. The 24-event family has simultaneous coverage at least $.99$. Predictions, action pairs, and realized Raw caches are fixed before the independent assessment.',r'\end{minipage}\end{table}']
 (R/'manuscript/risk_table.tex').write_text('\n'.join(lines)+'\n')
 lines=[r'\begin{table}[htbp]\centering',r'\caption{Least Accounted Cost with a Catalogue Accuracy Certificate}\label{tab:r18catalogue}',r'\small\setlength{\tabcolsep}{4pt}',r'\begin{tabular}{lrlrrr}\toprule',r'Design & $d$ & Certified choice & $\overline g$ & Seconds & NBO (3): $\overline g$\\\midrule']
 order={k:i for i,k in enumerate(NAMES)}
 rows=sorted(cat['rows'],key=lambda z:(order[z['cell'].rsplit('_d',1)[0]],int(z['cell'].rsplit('_d',1)[1])))
 for z in rows:
  name,d=z['cell'].rsplit('_d',1);n=next(y for y in z['candidates'] if y['candidate']=='nbo_scalar@3')
  lines.append(f"{NAMES[name]} & {d} & {candidate(z['selected_certified_candidate'])} & {directed(z['selected_regret_upper'],True,10000,4)} & {z['selected_accounted_seconds']:.2f} & {directed(n['regret_upper'],True,10000,4)}"+r'\\')
 lines +=[r'\bottomrule\end{tabular}',r'\par\vspace{4pt}\begin{minipage}{.97\textwidth}\footnotesize',r'Notes: Regret bounds are in units of $10^{-4}$; the target is at most one. Parentheses identify the original stage. The catalogue is the reference plus fifteen method-stage procedures, not the full action space. Early-stage seconds are prefix allocations; stage-three seconds are complete construction/query clocks. Shared assessment and the complete comparative bill are reported separately. The selected cost is least among certified candidates only.',r'\end{minipage}\end{table}']
 (R/'manuscript/catalogue_table.tex').write_text('\n'.join(lines)+'\n')
 lines=[r'\small',r'\begin{longtable}{llrrrl}',r'\caption{Complete Candidate Accuracy and Accounted Work}\label{tab:r18complete}\\',r'\toprule Design & Candidate & Lower & Upper & Seconds & Clock\\\midrule\endfirsthead',r'\toprule Design & Candidate & Lower & Upper & Seconds & Clock\\\midrule\endhead',r'\bottomrule\endfoot']
 for z in rows:
  name,d=z['cell'].rsplit('_d',1)
  for i,c in enumerate(z['candidates']):
   clock='Full' if c['construction_clock_is_actual_complete_process'] else ('Base' if c['candidate']=='reference' else 'Prefix')
   lines.append(f"{NAMES[name]} {d} & {candidate(c['candidate'])} & {directed(c['regret_lower'],False,10000,5)} & {directed(c['regret_upper'],True,10000,5)} & {c['mean_accounted_construction_seconds']:.3f} & {clock}"+r'\\')
  lines.append(r'\addlinespace')
 lines +=[r'\end{longtable}\normalsize',r'\noindent\textit{Notes:} Regret bounds are in units of $10^{-4}$. Full denotes the actual complete construction/query process; Prefix denotes its allocated early-stage component; Base denotes the zero reference construction allocation. No cost confidence interval is claimed.',r'\begin{table}[htbp]\centering\small',r'\caption{Complete Comparative Work Retained after Selection}\label{tab:r18bills}',r'\begin{tabular}{lrrr}\toprule Design & $d$ & Shared assessment & All construction plus assessment\\\midrule']
 for z in rows:
  name,d=z['cell'].rsplit('_d',1)
  lines.append(f"{NAMES[name]} & {d} & {z['shared_confirmation_seconds']:.3f} & {z['complete_comparative_study_seconds']:.3f}"+r'\\')
 lines +=[r'\bottomrule\end{tabular}',r'\par\vspace{4pt}\begin{minipage}{.95\textwidth}\footnotesize Notes: Mean seconds over the complete sixteen-stream population. The shared assessment is the original complete five-method, three-stage confirmation process. The last column also includes all five final construction/query processes. It is not replaced by the selected procedure\textquoteright s construction cost.\end{minipage}\end{table}']
 (R/'manuscript/catalogue_complete.tex').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':generate()
