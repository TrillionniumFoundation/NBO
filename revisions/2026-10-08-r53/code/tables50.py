"""Generate manuscript tables only from audited frozen results."""
from pathlib import Path
import json,statistics,itertools,csv
from collections import defaultdict,Counter
from fractions import Fraction as F
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
SHORT={'compiled-witness':'W','tensor-fvi':'F','surplus-fvi':'A','graded-fvi':'G','curvature-fvi':'B'}
BLOCK={'legacy':'O','planned':'P','surplus':'A','isotropic':'I','commonaccuracy':'C'}
LAW={'uniform':'U','1/8':'L','1/2':'M','7/8':'H'}
num=lambda x:f'{float(F(x)):.5g}'
def interval(j):return '['+','.join(num(v) for v in j['interval_exact'])+']'
def case(j):
 s=j['spec'];block="Q" if s["block"]=="planned" and s["target"]==2 else BLOCK[s["block"]]
 return f"{block}{s['d']};{s['T']};{s['p']};{LAW[s['law']]}"
def table(name,caption,headers,rows,align,notes=''):
 text='{\\small\n\\setlength{\\tabcolsep}{3pt}\n\\begin{longtable}{@{}'+align+'@{}}\n'
 h=' & '.join(headers)+r' \\'+'\n'
 text+='\\caption{'+caption+'}\\label{tab:'+name+'}\\\\\n\\toprule\n'+h+'\\midrule\n\\endfirsthead\n\\toprule\n'+h+'\\midrule\n\\endhead\n\\bottomrule\n\\endfoot\n'
 text+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+'\n\\end{longtable}\n}\n'
 if notes:text+='\\noindent{\\footnotesize '+notes+'\\par}\n'
 (R/'tables'/f'{name}.tex').write_text(text)

def main():
 a=read(R/'audit/RESULT_AUDIT.json');assert a['direct_estimands']==280
 ledger=read(R/'audit/COMPARISON_LEDGER.json');services=ledger['services'];common=ledger['common_services'];direct=ledger['direct']
 assert len({case(j) for j in direct})==len(direct), 'Printed direct-group identities must be unique'
 (R/'audit/PRINTED_CASE_MAP.json').write_text(json.dumps({case(j):j['spec'] for j in direct},indent=2)+'\n')
 groups=defaultdict(list)
 for j in services:groups[j['spec']['key']].append(j)
 rows=[]
 for key,js in sorted(groups.items()):
  j=js[0];sp=j['spec'];al=j['allocation'];times=[v['seconds_through_checkpoint_fsync'] for v in js]
  rows.append([f"{sp['d']};{sp['T']};{sp['p']}",SHORT[sp['method']]+(' I' if sp['allocation']=='isotropic' else ''),f"{al['N']},{al['K']},{al['M']}",sp['epsilon'],num(j['policy_bound_exact']),f"{sum(q['attained'] for q in js)}/3",f'{statistics.median(times):.4f}',f'[{min(times):.4f},{max(times):.4f}]'])
 table('services50','Primary prospective allocations and realized certificates',['$d;T;p$','Method','$N,K,M$',r'$\varepsilon$','Bound','Pass','Sec.','Sec. range'],rows,'llrrrrrr','W: native witness with equivalent ReLU realization; F: uniform FVI; A: residual-driven FVI; I: isotropic allocation. Each specification has three identical mathematical checkpoints and three distinct clocks. The primitive planning guarantee is witness-specific; FVI uses its actual critic modulus and certificate. Decimal rounding never determines attainment.')
 counts=a['primary_attainment_by_method'];su=next(v for v in services if v['spec']['method']=='surplus-fvi' and not v['repetition']);wf=next(v for v in services if v['spec']['key']=='tensor-fvi-d2-T2-p1-e5-planned' and not v['repetition']);w=next(v for v in services if v['spec']['key']=='compiled-witness-d2-T2-p1-e5-planned' and not v['repetition']);wi=next(v for v in services if v['spec']['key']=='compiled-witness-d2-T2-p1-e5-isotropic' and not v['repetition'])
 text=f"The primary block certifies {counts['compiled-witness'].get('success',0)} of 24 witness services, {counts['tensor-fvi'].get('success',0)} of 24 uniform FVI services and {counts['surplus-fvi'].get('success',0)} of three residual-driven services. These counts include timing repetitions, not independent policy draws. The residual comparator has nonuniform axes in all {su['nonuniform_date_models']} date models of its repeated checkpoint. Its bound is {num(su['policy_bound_exact'])}, compared with {num(wf['policy_bound_exact'])} for uniform FVI at the same quota. Its pilot work is retained.\n\n"
 text+=f"In the isotropic comparison cell, the planned witness uses {w['counts']['innovation_midpoints']:,} target innovation evaluations, versus {wi['counts']['innovation_midpoints']:,} for the isotropic service. The latter has fewer state nodes; query savings are therefore not a claim of less work in every category. The table reports measured complete clocks rather than inferring a speed ratio from this count.\n"
 (R/'tables/primary-discussion50.tex').write_text(text)
 cg=defaultdict(list)
 for j in common:cg[(j['dimension'],j['method'])].append(j)
 rows=[]
 for (d,m),js in sorted(cg.items()):
  j=js[0];times=[v['seconds_before_record'] for v in js];last=j['attempts'][-1]
  rows.append([d,SHORT[m],f"{j['attempts'][0]['N']}--{last['N']}",len(j['attempts']),num(last['policy_bound_exact']),f"{sum(v['attained'] for v in js)}/3",f'{statistics.median(times):.4f}',f'[{min(times):.4f},{max(times):.4f}]',f"{max(v['peak_rss_kib'] for v in js)/1024:.1f}"])
 table('common50','Separate common-target completion: horizon two, price one, target five',['$d$','Method','$N$ range','Tries','Bound','Pass','Sec.','Sec. range','MiB'],rows,'rlrrrrrrr','All failed state refinements are included in the complete prefix. MiB is the maximum process peak over three repetitions, not just model storage. The amendment followed the primary outcomes and was frozen before its own execution. Neither block overwrites the other. Host exclusivity and CPU frequency were not controlled.')
 rows=[]
 for j in direct:
  c=j['contrasts'];rows.append([case(j),interval(c['left-minus-right']),interval(c['left-repaired-minus-right-repaired']),interval(c['left-minus-left-repaired'])])
 table('policy50','Actual policy differences and removable final-action loss',['Case',r'$J_L-J_R$',r'$J_{L^+}-J_{R^+}$',r'$J_L-J_{L^+}$'],rows,'lrrr','A case is block/dimension; horizon; price; initial law. O: original R49 target-two policies; P: primary target-five plan; Q: primary target-two plan; C: common-accuracy amendment; I: isotropic; A: surplus FVI versus uniform FVI. Except A, left is witness and right is uniform FVI. U is uniform; L,M,H are point states 1/8,1/2,7/8. Superscript + denotes the identical terminal safety rule. Five-significant-digit display is not an exact endpoint; the rational records govern all conclusions.')
 wrows=[j for j in direct if j['spec']['block']!='surplus'];before=Counter(j['contrasts']['left-minus-right']['sign'] for j in wrows);after=Counter(j['contrasts']['left-repaired-minus-right-repaired']['sign'] for j in wrows);gain=Counter(j['contrasts']['left-minus-left-repaired']['sign'] for j in wrows)
 gl=[F(j['contrasts']['left-minus-left-repaired']['interval_exact'][0]) for j in wrows];gu=[F(j['contrasts']['left-minus-left-repaired']['interval_exact'][1]) for j in wrows]
 text=f"All {len(wrows)} declared witness comparison groups identify a strictly positive reduction of the witness incumbent's actual expected cost. The simultaneous gain lower endpoints range from {num(min(gl))} to {num(max(gl))}; upper endpoints range from {num(min(gu))} to {num(max(gu))}. This is a law-specific statement for the stated policies, not strict improvement at every initial state or {len(wrows)} independent training successes.\n\n"
 text+=f"Before repair, witness cost is identified as higher in {before['higher']} groups. After both methods receive the same repair, it remains higher in {after['higher']}, is lower in {after['lower']}, and is unresolved in {after['unresolved']}. The residual-driven FVI comparison is unresolved both before and after repair. Thus the terminal construction repairs a genuine economic loss without manufacturing a reversal of the strong conventional comparison.\n\n"
 text+=f"The active evaluator records {a['total_paths']:,} interval paths, {sum(a['gate_queries'].values()):,} cell-gate queries and {sum(a['accepted_changes'].values()):,} accepted changes across the two incumbents. No acquisition ambiguity or broad-hull fallback is recorded. Its joint direct-evaluation time before durable record output is {a['direct_seconds']:.2f} seconds. That total is evaluation work, not a speed comparison between independently executed policies.\n"
 (R/'tables/policy-discussion50.tex').write_text(text)
 rows=[];work=[];mechanism=[];csvrows=[]
 for j in direct:
  if j['spec']['block']=='legacy':continue
  for k,p in enumerate(j['spec']['paths']):
   folder=(R/p).parent
   if 'commonaccuracy' in folder.parts:
    rec=read(folder/'record.json');js=cg[(rec['dimension'],rec['method'])];ct=statistics.median(v['seconds_before_record'] for v in js);attempt=rec['returned'];counts=attempt['counts'];allcounts=rec['prefix_counts'];peak=rec['peak_rss_kib'];bytes_=attempt['checkpoint_bytes'];bits=max(v['counts']['maximum_coefficient_bits'] for v in rec['attempts'])
   else:
    rec=read(folder/'record.json');js=groups[rec['spec']['key']];ct=statistics.median(v['seconds_through_checkpoint_fsync'] for v in js);counts=rec['counts'];allcounts=counts;peak=rec['peak_rss_kib'];bytes_=rec['checkpoint_bytes'];bits=counts['maximum_coefficient_bits']
   name='left' if k==0 else 'right';policy=SHORT[read(R/p)['method']]
   rows.append([case(j),policy,f'{ct:.4f}',interval(j['absolute_cost'][name]),interval(j['absolute_cost'][name+'-repaired']),f"{j['seconds_before_record']:.3f}"])
   work.append([case(j),policy,f"{allcounts['innovation_midpoints']:,}",f"{counts['stored_actor_scalars']:,}",f"{bytes_/1024:.1f}",bits,f'{peak/1024:.1f}'])
   csvrows.append(dict(case=case(j),method=policy,construction_median_seconds=ct,joint_direct_seconds=j['seconds_before_record'],original_cost=j['absolute_cost'][name]['interval_exact'],repaired_cost=j['absolute_cost'][name+'-repaired']['interval_exact'],target_innovation_evaluations=allcounts['innovation_midpoints'],actor_scalars=counts['stored_actor_scalars'],checkpoint_bytes=bytes_,maximum_coefficient_bits=bits,peak_rss_kib=peak,counts=allcounts))
 table('joint50','Construction work and actual cost of new implementations',['Case','Method','Build sec.','Original cost','Repaired cost','Pair sec.'],rows,'llrrrr','Pair sec. is a shared cost of the whole four-policy comparison, repeated in the display for clarity, not independently attributable to each row. Construction medians use the same cell and fresh records; no historical clocks are spliced. Absolute-cost intervals are wider than centered pair intervals. Charges enter Proposition~\\ref{prop:joint50} with their explicitly chosen shared or marginal accounting convention.')
 table('work50','New-construction operation and storage account',['Case','Method','Target eval.','Actor scalars','KiB','Coeff. bits','MiB'],work,'llrrrrr','Target evaluations include every failed common-accuracy attempt. Actor scalars and checkpoint KiB describe the returned model. Coefficient bits are the true maximum, not the additive descriptor in the raw prefix map; MiB is process peak memory. Full operation categories, including terminal gates and exact fallbacks, remain in JSON.')
 for j in direct:
  for k,name in enumerate(('L','R')):
   c=j['actor_and_gate_counts'][k];di=j['chunk_mechanism_diagnostics'][k]
   mechanism.append([case(j),name,c.get('strict_action_changes',0),c.get('blocked_action_changes',0),f"{statistics.mean(v['last_old_action_mean'] for v in di):.5f}",f"{statistics.mean(v['last_new_action_mean'] for v in di):.5f}",c.get('derivative_queries',0)])
 table('mechanism50','Final-action mechanism diagnostics',['Case','Policy','Accepted','Blocked','Old action','New action','Derivative calls'],mechanism,'llrrrrr','Means are descriptive over the recorded paths, not confidence intervals for separate mechanism parameters. Complete date-wise earlier actions, terminal state vectors, capacity and quantum repair counts, and exact fallbacks are deposited.')
 allc=[];alld=[]
 for j in direct:
  for name,val in j['absolute_cost'].items():allc.append([case(j),name,num(val['interval_exact'][0]),num(val['interval_exact'][1])])
  for name,val in j['contrasts'].items():alld.append([case(j),name.replace('left','L').replace('right','R').replace('-repaired','+').replace('-minus-',' minus '),num(val['interval_exact'][0]),num(val['interval_exact'][1])])
 table('all-costs50','Every new absolute expected policy-cost interval',['Case','Policy','Lower','Upper'],allc,'llrr')
 table('all-contrasts50','Every new direct expected policy-cost contrast',['Case','Contrast','Lower','Upper'],alld,'llrr','Both tables are reconstructed from stored outward means, variance bounds and deterministic supports. Numerical replay uses the same original samples. Statistical interpretation requires the independent-bin model.')
 with (R/'audit/JOINT_COST_RESOURCE.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=csvrows[0].keys());writer.writeheader();writer.writerows(csvrows)
 (R/'audit/EDITORIAL_NUMBERS50.json').write_text(json.dumps(dict(witness_groups=len(wrows),before=dict(before),after=dict(after),witness_gain_signs=dict(gain),gain_lower_range=list(map(str,(min(gl),max(gl)))),gain_upper_range=list(map(str,(min(gu),max(gu))))),indent=2)+'\n')
 print(text)
if __name__=='__main__':main()
