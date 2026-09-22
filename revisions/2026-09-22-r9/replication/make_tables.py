"""Generate every R9 numerical table from retained raw JSON records."""
from __future__ import annotations
import json,pathlib,math
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-22-r9';OUT=REV/'results';TAB=REV/'paper/tables';TAB.mkdir(parents=True,exist_ok=True)
def load(p):return json.loads((OUT/p).read_text())
def down(x,n=8):return str(Decimal.from_float(float(x)).quantize(Decimal(1).scaleb(-n),rounding=ROUND_FLOOR))
def up(x,n=8):return str(Decimal.from_float(float(x)).quantize(Decimal(1).scaleb(-n),rounding=ROUND_CEILING))
def interval(x,n=8):return f'$[{down(x[0],n)},{up(x[1],n)}]$'
def table(name,heads,rows,cols):
 s='\\begin{tabular}{'+cols+'}\n\\toprule\n'+' & '.join(heads)+r' \\'+'\n\\midrule\n'
 s+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+'\n\\bottomrule\n\\end{tabular}\n'
 (TAB/(name+'.tex')).write_text(s)

def run():
 summary={'economy':[]};rows=[];rowsB=[];restricted=load('policy_certificate_restricted.json');rlo=restricted['records'][-1]['policy_value_interval'][0]
 dual=load('restricted_dual_certificate.json');rup=dual['records'][-1]['restricted_optimal_value_upper']
 for tag in ['0.5','2','8']:
  p=load(f'policy_certificate_k{tag}.json');u=load(f'upper_certificate_k{tag}.json');v=p['records'][-1]['policy_value_interval'];upper=u['reports'][-1]['upper_value_initial']
  gap=float(np.nextafter(upper-v[0],np.inf));wl=float(np.nextafter(v[0]-rup,-np.inf));wh=float(np.nextafter(upper-rlo,np.inf))
  rows.append([tag,interval(v),up(upper),up(gap)])
  rowsB.append([tag,interval(p['adjustment_budget_interval'],14),down(wl),interval([max(0,wl),wh])])
  summary['economy'].append({'k':float(tag),'policy_value_interval':v,'optimal_value_interval':[v[0],upper],'regret_upper':gap,'adjustment_budget_interval':p['adjustment_budget_interval'],'optimal_access_welfare_interval':[max(0,wl),wh],'precision_target':.01,'precision_target_met':gap<=.01})
 table('original',['$k$','Policy payoff enclosure','Optimal-value upper','Regret upper'],rows,'r r r r')
 table('economics',['$k$','Policy adjustment budget','Access gain: lower','Access gain: enclosure'],rowsB,'r r r r')
 p=load('policy_certificate_k2.json');u=load('upper_certificate_k2.json');rows=[]
 for a,b in zip(p['records'],u['reports']):rows.append([a['time_rectangles'],f"{a['width']:.3g}",f"{a['seconds']:.3f}",b['leaf_boxes'],f"{b['residual_upper_bound']+b['utility_approximation_error']:.3g}",f"{b['seconds']:.3f}",up(b['upper_value_initial']-a['policy_value_interval'][0],6)])
 table('refinement',['Time boxes','Payoff width','Sec.','Bernstein boxes','Residual upper','Sec.','Regret upper'],rows,'r r r r r r r')
 rows=[]
 for r in dual['records']:rows.append([r['weighted_boxes'],interval(r['dual_value_interval']),f"{r['width']:.3g}",f"{r['seconds']:.2f}"])
 table('restricted_dual',['Weighted boxes','Dual witness-value enclosure','Width','Seconds'],rows,'r r r r')
 jets={r['dimension']:r for r in load('neural_jet_certificates.json')};rows=[]
 for r in load('action_certificates.json'):
  gap=r['gap']
  if r['dimension'] in jets:gap=next(q['true_neural_action_gap_upper'] for q in jets[r['dimension']]['action_certificates'] if q['tolerance']==r['tolerance'])
  rows.append([r['dimension'],f"{r['tolerance']:.0e}",f"{gap:.3g}",r['node_evaluations'],r['scalar_inner_problems'],f"{r['seconds']:.3f}"])
 table('actions',['Action dim.','Tolerance','Verified gap','Scalar boxes','Convex subproblems','Seconds'],rows,'r r r r r r')
 rows=[]
 for d in [8,16,32]:
  for r in load(f'absolute_lower_d{d}.json')['records']:
   rows.append([d,r['cells'],interval(r['relaxed_value_interval']),down(r['lower_bound']),f"{r['seconds']:.3f}"])
 table('absolute',['$d$','Quadrature cells','Relaxed-value enclosure','Original-value lower','Seconds'],rows,'r r r r r')
 ext=OUT/'external/summary.json'
 if ext.exists():
  records=load('external/summary.json')['rows'];rows=[];detail=[]
  for r in records:
   low=load(f"absolute_lower_d{r['dimension']}.json")['records'][-1]['lower_bound']
   rows.append([r['dimension'],r['budget_seconds'],f"{r['means']['nbo']:.4f}",f"{r['means']['soc']:.4f}",f"{r['means']['lq']:.4f}",f"{r['median_difference']:.4f}",f"{r['bonferroni_six_panels_p']:.4g}"])
   detail.append([r['dimension'],r['budget_seconds'],down(low,5),f"{r['means']['nbo']-low:.4f}",f"{r['means']['soc']-low:.4f}",f"{r['training_clock_means']['nbo']:.3f}",f"{r['training_clock_means']['soc']:.3f}"])
  table('external',['$d$','Budget','NBO cost','SOC cost','LQ cost','Median difference','Adjusted $p$'],rows,'r r r r r r r')
  table('external_absolute',['$d$','Budget','Lower bound','NBO excess','SOC excess','NBO sec.','SOC sec.'],detail,'r r r r r r r')
  summary['external']=records
 (OUT/'scientific_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps(summary.get('economy'),indent=2))
if __name__=='__main__':run()
