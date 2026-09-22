from pathlib import Path
import json,math
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
from fractions import Fraction
r=Path(__file__).resolve().parents[3]; d=r/'revisions/2026-09-22-r14'; t=d/'paper/tables';t.mkdir(exist_ok=True,parents=True)
load=lambda p:json.loads((d/'results'/p).read_text())
def fmt(x,n=8,upper=True):
 return str(Decimal.from_float(float(x)).quantize(Decimal(1).scaleb(-n),rounding=ROUND_CEILING if upper else ROUND_FLOOR))
def table(name,cols,head,rows):
 text='\\begin{tabular}{'+cols+'}\n\\toprule\n'+head+' \\\\\n\\midrule\n'+'\n'.join(' & '.join(row)+' \\\\' for row in rows)+'\n\\bottomrule\n\\end{tabular}\n';(t/(name+'.tex')).write_text(text)
ns=load('independent_library/nodes.json')
table('nodes','rrrrr','$k$ & Policy lower & Optimum upper & Regret upper & Policy width',[[f'{x["k"]:g}',fmt(x['L'],8,False),fmt(x['U'],8),fmt(x['regret_upper'],9),f'{x["primal_width"]:.2e}'] for x in ns])
rows=[]
for f in ['neural_audit_0100_8_16_16.json','neural_audit_0300_8_16_16.json','neural_audit_0800_4_8_8.json','neural_audit_0800_8_16_16.json','neural_audit_0800_16_32_32.json']:
 a=load(f);e=a['error_budget']; rows.append([str(a['training_step']),str(a['interior_cells']),fmt(e['two_sided_trace'],4),fmt(e['integrated_residual_and_action'],4),fmt(e['t0_regret_upper'],4),f'{a["wall_seconds"]:.2f}'])
table('neural','rrrrrr','Updates & Cells & $2b$ & $\\int e^{-\\rho s}(2e+q)ds$ & Regret upper & Seconds',rows)
a=load('neural_audit_0800_16_32_32.json');rows=[]
for x in a['boundary']:
 face={ (1,0):'$u=1.2$',(1,1):'$u=2.8$',(2,0):'$x=.5$',(2,1):'$x=2$'}[tuple(x['face'])]
 rows.append([face,str(x['cells']),fmt(x['trace_error_upper'],8)])
table('boundary','lrr','Stopping face & Cells & Trace error upper',rows)
fresh=load('fresh_frontier/frontier.json')
table('frontier','rrrrrr','Slabs & Generation & Dual fit & Primal audit & Dual audit & Regret upper',[[str(x['policy_slabs']),f'{x["policy_generation_seconds"]:.3f}',f'{x["dual_fitting_seconds"]:.3f}',f'{x["primal_verification_seconds"]:.3f}',f'{x["dual_verification_seconds"]:.3f}',fmt(x['regret_upper'],9)] for x in fresh])
price=load('independent_price_audit.json')
table('welfare','rrrrcc','$p$ & $q$ & Lower loss & Upper loss & Strict & Relative',[[f'{x["p"]:g}',f'{x["q"]:g}',fmt(x['welfare_loss_interval'][0],8,False),fmt(x['welfare_loss_interval'][1],8),'Yes' if x['strict_positive_certified'] else 'No','Yes' if x['relative_width_at_most_one'] else 'No'] for x in price['welfare_queries']])
rr=[]
for x in price['economic_resolution_regions']:
 def region(key):
  a=x[key]
  return '--' if not a else ', '.join(f'({float(Fraction(s)):.6f}, {float(Fraction(q)):.1f}]' for s,q in a)
 rr.append([f'{x["anchor"]:g}',region('strict_positive_loss_regions'),region('relative_width_at_most_one_regions')])
table('regions','rll','Anchor $p$ & Strictly positive loss & Relative width at most one',rr)
rr=[]
for x in price['active_policy_regions']:
 actor=json.loads((r/x['actor_path']).read_text());rr.append([f'{x["policy_k"]:g}',f'{x["left"]:.5f}',f'{x["right"]:.5f}',f'{x["width"]:.5f}',f'{min(actor["c"]):.5f}--{max(actor["c"]):.5f}',f'{sum(actor["theta"])/len(actor["theta"]):.5f}'])
table('policy_regions','rrrrlr','Policy $k_j$ & Left & Right & Width & Consumption range & Mean $\\theta$',rr)
q=load('independent_library/dual_k4.25.json');p=load('independent_library/primal_k4.25.json')
rr=[['Source integral',fmt(q['source_integral_interval'][0],11,False),fmt(q['source_integral_interval'][1],11)],['Covariance',fmt(q['covariance_interval'][0],11,False),fmt(q['covariance_interval'][1],11)],['Reference-control gap','0',fmt(q['control_gap_upper'],11)],['Conditional variance',fmt(q['variance_allowance'][0],11,False),fmt(q['variance_allowance'][1],11)],['Localization',fmt(q['localization'][0],11,False),fmt(q['localization'][1],11)],['Primal payoff',fmt(p['value_interval'][0],12,False),fmt(p['value_interval'][1],12)]]
table('dual_budget','lrr','Quantity & Lower & Upper',rr)
old=load('inherited_price_audit.json');rob=load('robust_library/envelope.json');st=load('state_cost/envelope.json')
table('robustness','lr','Certificate & Uniform regret upper',[[r'R12 retained implementation, original inputs',fmt(old['uniform_regret_upper'],12)],[r'R14 independent implementation, finer cover',fmt(price['uniform_regret_upper'],12)],[r'R14 perturbed witnesses and enlarged allowances',fmt(rob['uniform_regret_upper'],12)],[r'R14 joint state--cost rectangle',fmt(st['uniform_regret_upper'],12)]])
