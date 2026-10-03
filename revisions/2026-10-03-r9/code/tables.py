"""Generate R9 numerical tables from recorded JSON and raw-array accounts."""
from pathlib import Path
import hashlib,json
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'results';M=R/'manuscript';inputs={};generated={}
def load(name):
 p=O/(name+'.json');inputs[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest();return json.loads(p.read_text())
def fmt(x,n=4):return '--' if x is None else f'{x:.{n}f}'
def table(name,caption,label,headers,rows,note=''):
 cols='l'+'r'*(len(headers)-1)
 size='\\footnotesize' if len(headers)>=7 else '\\small'
 text='\\begin{table}[htbp]\n\\centering'+size+'\\setlength{\\tabcolsep}{4pt}\n\\caption{'+caption+'}\\label{'+label+'}\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+' & '.join(headers)+r' \\'+'\n\\midrule\n'
 text+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+'\n\\bottomrule\n\\end{tabular}\n'
 if note:text+='\\par\\vspace{3pt}\\begin{minipage}{0.97\\linewidth}\\footnotesize '+note+'\\end{minipage}\n'
 text+='\\end{table}\n';p=M/(name+'.tex');p.write_text(text);generated[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()

def run():
 M.mkdir(exist_ok=True);common=load('COMMON_ACCOUNTS');rows=[]
 for r in common['records']:
  if not r['raw']:rows.append([{'actor':'Actor + search','direct':'Direct + search','search':'Search only'}[r['method']],r['seed'],fmt(r['regret_upper']),fmt(r['initial_center_upper']),'Yes' if r['target_pass'] else 'No'])
 cover=load('continuous_actor_s29_search_signed_cover');hist=cover['history']
 table('table_common','Complete-action bounds for the same frozen policies','tab:r9common',['Policy','Seed','Uniform bound','Centre bound','$\\leq0.1$'],rows,
 'Full $17\\times25$ state grid, twenty dates, unchanged three-control box. The common signed cover took '+fmt(cover['seconds'],2)+' seconds; '+str(sum(not h['budget_exhausted'] for h in hist))+' of twenty one-step covers closed at the requested tolerance. Other levels retain all unresolved upper bounds. Bounds are conditional on the stated outward-arithmetic execution model; continuous-state/time transfer is not included.')
 matched=load('MATCHED_COVER');rows=[]
 for r in matched['records']:rows.append([r['method'].capitalize(),r['time_index'],fmt(r['elapsed'],2),f"{r['box_evaluations']/1e6:.3f}",fmt(r['maximum_optimization_bracket'],5),'Yes' if r['budget_exhausted'] else 'No'])
 table('table_matched','Matched one-step action-cover computation','tab:r9matched',['Cover','Date','Seconds','$Q$ boxes, m.','Bracket','Budget hit'],rows,'Continuation, incumbent, tolerance, and budget are identical within each date. Wall time includes gradient work; a query count is not a hardware-independent speed measure.')
 nested=load('NESTED_CERTIFICATES');rows=[]
 for method in ['actor','search']:
  for guard in [False,True]:
   a=[r for r in nested['records'] if r['method']==method and r['guarded']==guard]
   rows.append([('Actor' if method=='actor' else 'Search')+(' + guard' if guard else ''),fmt(min(r['regret_upper'] for r in a))+'--'+fmt(max(r['regret_upper'] for r in a)),fmt(max(r['maximum'] for r in a)),fmt(np.mean([r['training_seconds'] for r in a]),2),str(sum(r['all_node_target_pass'] for r in a))+'/3'])
 table('table_nested','Fresh policies on the nested fine grid','tab:r9nested',['Method','Uniform bound range','Ref. advantage','Mean train s.','Passes'],rows,'Full $33\\times49$ state grid, forty dates; seeds 11, 29, and 47. Reference advantage is a lower regret diagnostic against the feasible 175-action reference, not an upper bound. Uniform bounds use a separately computed complete-action fine-grid envelope. The guard is a saved indexed correction, not an uncorrected network.')
 rows=[]
 for r in common['records']:
  if not r['raw']:rows.append([r['method'].capitalize(),r['seed'],fmt(r['compensation']['percent_upper'],2),fmt(r['compensation']['seconds'],2)])
 table('table_welfare','Sufficient financed flow-consumption supplements','tab:r9welfare',['Proposal','Seed','Supplement, percent','Verification seconds'],rows,'Uniform sufficient compensation over every active starting node and date. State dynamics, the original policy, terminal bequest, and adjustment cost stay fixed. Consumption is externally financed. These are not feasible self-financed policy improvements or common homothetic consumption equivalents.')
 capital=load('GLOBAL_CAPITAL_BENCHMARK');rows=[]
 for r in capital['bounds']:rows.append([r['dimension'],r['panels'],fmt(r['feasible_schedule_lower'],6),fmt(r['global_optimal_upper'],6),fmt(r['width'],6)])
 table('table_capital','Global bounds in the original continuous capital economy','tab:r9capital',['Dimension','Time panels','Feasible lower','Optimal upper','Width'],rows,'Initial log capital is zero in every coordinate; horizon one. The bounds cover every admissible control on $\\mathbb R^d$. They are not small loss bounds for neural policies. The same feasible schedule is evaluated on the saved Brownian paths in the supplement.')
 ref=load('FULL_DOMAIN_REFINEMENT');rows=[]
 for r in ref['records']:
  loc=r['location'];rows.append([r['method'][0].upper()+str(r['seed']),str(r['grid'][0])+'/'+str(r['grid'][1])+'/'+str(r['steps']),fmt(r['maximum']),fmt(r['positive_quantiles']['95']),fmt(r['positive_quantiles']['99']),fmt(loc['time'],3),fmt(loc['u'],2),fmt(loc['wealth'],3)])
 table('table_full_domain','Frozen-policy errors over every refinement node','tab:r9full',['Policy','Grid/dates','Max.','95th','99th','$t$','$u$','$X$'],rows,'A denotes actor-plus-search and D direct-plus-search. Quantiles concern the positive reference advantage over every state and date. Maximum locations include stopping-adjacent states. All eighteen historical configurations are retained; no centre-only selection is used.')
 rows=[]
 for r in ref['records']:rows.append([r['method'][0].upper()+str(r['seed']),str(r['grid'][0])+'/'+str(r['grid'][1])+'/'+str(r['steps']),fmt(r['lower_wealth_region_max']),fmt(r['upper_wealth_region_max']),fmt(r['interior_max']),fmt(100*r['fraction_above_point1'],2)])
 table('table_boundary','Boundary-region refinement diagnostics','tab:r9boundary',['Policy','Grid/dates','Lower region','Upper region','Interior','Above 0.1, \\%'],rows,'Each wealth boundary region spans two grid cells. Interior means the remaining wealth nodes. Values are maximum finite-reference advantages, not upper certificates.')
 rows=[]
 for r in ref['records']:
  lo=r['lower_action_frequency'];hi=r['upper_action_frequency'];rows.append([r['method'][0].upper()+str(r['seed']),str(r['grid'][0])+'/'+str(r['grid'][1])+'/'+str(r['steps'])]+[fmt(100*v,1) for v in lo+hi])
 table('table_saturation','Refinement action saturation rates, percent','tab:r9saturation',['Policy','Grid/dates','$c_-$','$p_-$','$\\theta_-$','$c_+$','$p_+$','$\\theta_+$'],rows,'Rates cover active state-time nodes; an action is counted within $10^{-4}$ of a bound. The box is an economic primitive, and saturation is not interpreted as an unconstrained first-order optimum.')
 nd=load('NESTED_RETRAINING');rows=[]
 for r in nd['records']:rows.append([r['method'][0].upper()+str(r['seed'])+('G' if r['guarded'] else ''),str(r['grid'][0])+'/'+str(r['steps']),fmt(r['maximum']),fmt(r['own_value_fit_error']),fmt(r['training_seconds'],2),fmt(None if r['guard_fraction'] is None else 100*r['guard_fraction'],1)])
 table('table_nested_all','Every fresh nested-grid training run','tab:r9nestedall',['Policy','Nodes $u$/dates','Ref. max.','Value fit','Seconds','Corrected \\%'],rows,'G denotes the indexed guard. All eighteen fresh runs appear. Value fit is a policy-value diagnostic, distinct from the one-step target residual. Unguarded failures are not excluded.')
 rows=[]
 for r in nested['records']:rows.append([r['method'][0].upper()+str(r['seed'])+('G' if r['guarded'] else ''),fmt(r['regret_upper']),fmt(r['independent_policy_residual_upper'],7),fmt(r['indexed_correction_uncompressed_bytes']/1024,1),fmt(r['policy_evaluation_seconds'],2)])
 table('table_nested_cert','Independent verification and correction storage','tab:r9nestedcert',['Policy','Uniform bound','Policy residual','Correction KiB','Evaluation s.'],rows,'Same fine-grid upper envelope for every row. Correction memory counts saved indexed corrections and masks over all dates, not only one network. Policy residuals use independent outward point-action evaluation. The complete source contains raw arrays and nodewise masks.')
 rows=[]
 for r in common['records']:
  if not r['raw']:rows.append([r['method'][0].upper()+str(r['seed']),fmt(r['training_seconds'],2),fmt(r['total_cost_by_number_policies']['1'],2),fmt(r['total_cost_by_number_policies']['9'],2),fmt(r['total_cost_by_number_policies']['100'],2),fmt(r['total_with_compensation_by_number_policies']['9'],2)])
 table('table_cost','Explicit shared-cost accounting, seconds','tab:r9cost',['Policy','Train','One policy','Nine policies','100 policies','Nine + welfare'],rows,'Training/reference/policy-evaluation times are archived R8 measurements; the new certificate and welfare measurements are current. This is an auditable mixed-provenance cost account, not a same-machine speed comparison. Each policy receives its own independent payoff interval. Shared-cover cost is amortized only within the identical economy.')
 rows=[]
 for sim in capital['simulations']:
  for r in sim['records']:rows.append([sim['dimension'],r['steps'],fmt(r['mean']),fmt(r['confidence_interval'][0]),fmt(r['confidence_interval'][1])])
 table('table_schedule','Feasible schedule on the matched Brownian paths','tab:r9schedule',['Dimension','Euler steps','Mean payoff','95\\% lower','95\\% upper'],rows,'512 paths per dimension. Pointwise Student intervals describe Monte Carlo error only; no continuous-time bias correction is assumed.')
 rows=[]
 for sim in capital['simulations']:
  for r in sim['comparisons']:
   s=r['learned_minus_schedule'];rows.append([sim['dimension'],('N' if r['method']=='nbo_exact' else 'D')+str(r['seed']),'Wide' if r['wide'] else 'Narrow',fmt(s['mean']),fmt(s['confidence_interval'][0]),fmt(s['confidence_interval'][1])])
 table('table_schedule_pairs','Learned-policy minus feasible-schedule payoffs','tab:r9schedulepairs',['Dimension','Policy','Training domain','Mean','95\\% lower','95\\% upper'],rows,'Every stored configuration is retained. Differences are paired on the same 160-step Euler paths; confidence intervals do not cover Euler discretization bias. They are not continuous neural-policy regret bounds.')
 (R/'TABLE_MANIFEST.json').write_text(json.dumps(dict(input_sha256=inputs,generated=generated),indent=2)+'\n')
if __name__=='__main__':run()
