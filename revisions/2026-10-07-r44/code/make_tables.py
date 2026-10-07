"""Generate publication tables from frozen records, never from hand-entered results."""
from pathlib import Path
import json, statistics, collections, hashlib
R=Path(__file__).resolve().parents[1]
load=lambda p:json.loads(p.read_text())
def save(name,text): (R/'tables'/name).write_text(text+'\n')
def table(caption,label,head,rows,cols):
 return '\n'.join([r'\begin{table}[htbp]',r'\centering\small',r'\caption{'+caption+'}',r'\label{'+label+'}',r'\begin{tabular}{'+cols+'}',r'\toprule',head+r'\\',r'\midrule',*rows,r'\bottomrule',r'\end{tabular}',r'\end{table}'])
a=load(R/'results/R42_REPLAY.json')
rows=[]
for name,method,targets,n in [('Scalar neural','direct-neural',(.06,.04),12),('Scalar spline','spline',(.06,.04),12),('Coupled neural','convex-neural',(.25,.1),6),('Coupled ridge','ridge-projection',(.25,.1),6),('Coupled quadratic','quadratic-projection',(.25,.1),6)]:
 for e in targets:rows.append(f'{name} & {e:.2f} & {a["attainment"][method+"@"+str(e)]}/{n}'+r'\\')
save('attainment.tex',table('Original capped-service target attainment','tab:attainment','Method & All-state target & Certified',rows,'lrr'))
rec=[load(p) for p in sorted((R/'results').glob('recertify-???.json'))]
rows=[f'{x["service_id"]:03d} & {x["original_bound"]:.8f} & {x["retained_policy_bound"]:.8f} & {x["target"]:.2f} & Yes'+r'\\' for x in rec]
save('recertification.tex',table('Additional verification of unchanged neural policies','tab:recertification','Service & Original bound & Refined bound & Target & Attained',rows,'lrrrr'))
pairs=[load(p) for p in sorted((R/'results').glob('paired-?-?.json'))]
if len(pairs)!=24:raise ValueError('Paired study incomplete')
rows=[]
for p in (1,4):
 z=[x for x in pairs if x['price']==p]
 rows.append(f'{p} & {len(z)} & {sum(x["confidence_lower"]>0 for x in z)} & {sum(x["confidence_upper"]<0 for x in z)} & {sum(x["sign"]=="unresolved" for x in z)}'+r'\\')
save('paired_summary.tex',table('Direct neural-minus-ridge cost comparisons, simultaneous 99 percent intervals','tab:paired','Price & Comparisons & Positive & Negative & Unresolved',rows,'rrrrr'))
rows=[]
for x in pairs:
 rows.append(f'{x["price"]} & {x["training_seed"]} & {x["state_index"]+1} & {x["confidence_lower"]*1e4:.6f} & {x["confidence_upper"]*1e4:.6f}'+r'\\')
save('paired_full.tex','\n'.join([r'\begin{center}\small',r'\begin{longtable}{rrrrr}',r'\caption{All direct cost intervals. Endpoints are multiplied by $10^4$. States are ordered as in the main article.}\label{tab:pairedfull}\\',r'\toprule Price & Training seed & State & Lower & Upper\\\midrule\endfirsthead',r'\toprule Price & Training seed & State & Lower & Upper\\\midrule\endhead',*rows,r'\bottomrule\end{longtable}\end{center}']))
precision=collections.defaultdict(list)
for x in a['precision_services']:precision[x['record']['method']].append(x)
pr={}
for method,items in precision.items():
 pr[method]={'services':len(items),'certified':sum(x['record']['certified'] for x in items),'seconds':sum(x['clock']['seconds_through_fsync'] for x in items)}
 for mode in ('32','64'):
  for key in ('accepted','rejected','attempts'):
   pr[method][key+mode]=sum(x['clock']['precision_work'][mode][key] for x in items)
rows=[]
for method,name in [('fixed32-cached','Fixed32'),('fixed64-cached','Fixed64'),('adaptive-cached','Adaptive')]:
 z=pr[method];rows.append(f'{name} & {z["certified"]}/36 & {z["accepted32"]} & {z["rejected32"]} & {z["accepted64"]}'+r'\\')
save('precision.tex',table('Original repeated precision catalogue','tab:precision','Method & Certified & Accepted32 & Rejected32 & Accepted64',rows,'lrrrr'))
by={}
for m,xs in precision.items():
 by[m]={ (x['clock']['spec']['service']['name'],x['clock']['spec']['repeat']):x['clock']['seconds_through_fsync'] for x in xs}
ratios=[v/by['fixed64-cached'][k] for k,v in by['adaptive-cached'].items()]
rows=[]
for x in rec:
 w=x['verification_work'];c=load(R/'results'/f'recertify-{x["service_id"]:03d}.clock.json')
 operations=w.get('bellman_transition_evaluations',w.get('neural_neuron_expectations'))
 rows.append(f'{x["service_id"]:03d} & {x["verification_N"]} & {operations:,} & {x["original_actor_scalar_storage"]:,} & {c["seconds_through_fsync"]:.3f}'+r'\\')
save('diagnostic_work.tex',table('Additional verification work and local diagnostic clocks','tab:diagwork','Service & Mesh & Operations & Retained actor & Seconds',rows,'lrrrr')+'\nOperations count Bellman transitions for scalar services and neuron expectations for the coupled service; these are different units, not cross-method speed estimates.')
summary={'original_records_verified':a['original_records_verified'],'original_sources_verified':len(a['original_source_hashes']), 'recertified_unchanged_policies':sum(x['target_attained'] for x in rec),'original_failures_reclassified':0,'paired_comparisons':len(pairs),'paired_unresolved':sum(x['sign']=='unresolved' for x in pairs),'paired_width_min':min(x['confidence_upper']-x['confidence_lower'] for x in pairs),'paired_width_max':max(x['confidence_upper']-x['confidence_lower'] for x in pairs),'ambiguous_actions_total':sum(x['ambiguous_actions_neural']+x['ambiguous_actions_ridge'] for x in pairs),'precision':pr,'adaptive_faster':sum(v<1 for v in ratios),'adaptive_slower':sum(v>1 for v in ratios),'adaptive_ratio_median':statistics.median(ratios),'adaptive_aggregate_percent':100*(pr['adaptive-cached']['seconds']/pr['fixed64-cached']['seconds']-1)}
(R/'audit/PUBLICATION_SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps(summary,indent=2))
