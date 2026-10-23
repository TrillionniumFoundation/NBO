"""Source-bound R95 tables; interval endpoints are rounded outwards."""
from __future__ import annotations
import json,pathlib,itertools,math,hashlib
from fractions import Fraction
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
import numpy as np
R=pathlib.Path(__file__).resolve().parents[1];T=R/'tables';T.mkdir(exist_ok=True)
c=json.loads((R/'results94/CALIBRATION94.json').read_text());r=json.loads((R/'results94/evaluation-local95/RESULTS94.json').read_text())
assert hashlib.sha256((R/'results94/CALIBRATION94.json').read_bytes()).hexdigest()==r['calibration_sha256']
labels={'online-risk-dp':'Online risk-DP','quadratic':'Quadratic','relu':'ReLU','spline':'Spline'}
def decimal(x,upper=False,places=6):
 d=Decimal.from_float(float(x));return format(d.quantize(Decimal(10)**-places,rounding=ROUND_CEILING if upper else ROUND_FLOOR),'f')
def interval(a,p=6):return '['+decimal(a[0],False,p)+', '+decimal(a[1],True,p)+']'
def table(name,caption,label,cols,head,rows,note=''):
 s='\\begin{table}[htbp]\n\\caption{'+caption+'}\\label{'+label+'}\n\\centering\\small\n\\begin{tabular}{@{}'+cols+'@{}}\n\\toprule\n'+head+'\\\\\\midrule\n'+'\n'.join(' & '.join(row)+r'\\' for row in rows)+'\n\\bottomrule\n\\end{tabular}\n'
 if note:s+='\\par\\smallskip\\begin{minipage}{.98\\linewidth}\\footnotesize '+note+'\\end{minipage}\n'
 s+='\\end{table}\n';(T/name).write_text(s)
fits=[];cost=[];pairs=[];work=[];screens=[]
for idx,lev in r['levels'].items():
 alpha=lev['alpha'];cl=c['levels'][idx]
 for arm in ('quadratic','relu','spline'):
  x=cl['constructions'][arm];f=x['fit_record'];b=x['uniform_residual']
  fits.append([str(alpha),labels[arm],str(f['effective_rank']),f"{f['training_rmse']:.5f}",interval([b['lower'],b['upper']],5)])
 for arm,aa in lev['arms'].items():
  d=aa['data'];w=aa['complete_evaluation_work']
  cost.append([str(alpha),labels[arm],interval(d['mean_cost_interval']),decimal(d['original_optimum_loss_distribution']['1'],True),str(d['failed_Q_targets']+d['failed_original_optimum_targets'])])
  counts=w['counts']
  work.append([str(alpha),labels[arm],f"{w['seconds']:.3f}",f"{counts.get('terminal_proposal_queries',0):,}",f"{counts.get('all_action_lower_witnesses',0):,}"])
  s=lev['screening'][arm]
  screens.append([str(alpha),labels[arm],f"{s['excluded_bins']:,}/4,096",str(s['no_cut_rows']),f"{1000*s['mean_full_bound_and_sort_seconds']:.3f}",f"{1000*s['mean_pruned_bound_proof_sort_seconds']:.3f}"])
 for key,p in lev['pairwise'].items():
  a,b=key.split(' minus ')
  pairs.append([str(alpha),labels[a]+' $-$ '+labels[b],interval(p['interval']),f"{p['sampling_radius_empirical_bernstein']:.6f}",'Yes' if p['equivalent_within_margin'] else 'No'])
table('fits95.tex','Fitted continuations and whole-square residual enclosures','tab:fits95','llrrl',r'$\alpha$ & Continuation & Rank & Training RMSE & $V_1-f$ on the whole square',fits,'Each fit uses the same 1,024 labels and 32 nonlinear features plus an affine part. The quadratic feature matrix has rank six, not 35; the experiment matches nominal features and labels, not independent parameter rank. The residual enclosures cover every state in the continuous square.')
table('cost95.tex','Original nested-risk cost and qualification at 2,048 evaluation states per risk level','tab:cost95','lllrr',r'$\alpha$ & Continuation & Mean cost enclosure & Maximum loss bound & Failures',cost,'Cost enclosures here contain numerical uncertainty only. Simultaneous sampling intervals for all paired differences appear in Table~\\ref{tab:pairs95}. The maximum loss bound is against the original Bellman optimum; all displayed endpoints are rounded outwards. A failure is a failed own-continuation or original-optimum target, with every row retained.')
table('pairs95.tex','All prespecified simultaneous paired policy-cost comparisons','tab:pairs95','lllrl',r'$\alpha$ & Contrast & 95\% interval & Sampling & Equiv.',pairs,'The unit is an independent initial state under the declared dyadic uniform distribution. There are twelve fixed comparisons in one family. Equivalence uses the prespecified margin $1/16$ in normalized cost units. Every interval includes zero: none identifies strict superiority. The calibration selector is online risk-DP at both risk levels.')
table('work95.tex','Measured work of the completed evaluation attempt','tab:work95','llrrr',r'$\alpha$ & Continuation & Seconds & Terminal proposals & All-action witnesses',work,'Every arm processes all 2,048 initial states. Timings include first-action proposals, qualification, the original-value witness, complete-policy cost enclosures and CSV output. They exclude preparation, the independent audit, diagnostic screening and failed earlier execution starts, all reported separately. Counts are instrumented work units, not every arithmetic instruction. This is a single x86-64 execution, not a cross-architecture speed guarantee.')
table('screens95.tex','Strict continuum-bin exclusions with their construction costs','tab:screens95','llrrrr',r'$\alpha$ & Continuation & Excluded/candidate & No-cut rows & Full (ms) & Pruned (ms)',screens,'The first 32 prespecified rows of every arm are retained, with 128 bins each. Full includes unpruned bound construction and sorting. Pruned additionally pays for the strict proof and retained-bin sorting. Both return identical upper-tail values. Repeated sorts are timing diagnostics, not new economic observations; these measurements show no end-to-end gain from screening.')
s=json.loads((R/'results92/SUMMARY92.json').read_text());raw=[]
for case in s['cases']:
 for b in case['bounds']:
  scalar=Fraction(b['scalar_bound']);state=Fraction(b['max_state_bound']);improve=scalar-state
  raw.append({'T':case['T'],'alpha':case['alpha'],'theta':case['theta'],'radius':b['radius'],'scalar':str(scalar),'state':str(state),'improvement':str(improve),'relative_improvement':float(improve/scalar) if scalar else None,'pieces_before':b['pieces_before'],'pieces_after':b['pieces_after'],'no_cut':b['pieces_before']==b['pieces_after']})
assert len(raw)==252
rel=np.array([x['relative_improvement'] for x in raw if x['relative_improvement'] is not None]);diff=np.array([float(Fraction(x['improvement'])) for x in raw])
old={'configurations':len(raw),'strict_improvements':sum(Fraction(x['improvement'])>0 for x in raw),'equal_bounds':sum(Fraction(x['improvement'])==0 for x in raw),'looser_state_bounds':sum(Fraction(x['improvement'])<0 for x in raw),'no_cut_configurations':sum(x['no_cut'] for x in raw),'candidate_pieces_total':sum(x['pieces_before'] for x in raw),'retained_pieces_total':sum(x['pieces_after'] for x in raw),'relative_improvement_quantiles':{str(q):float(np.quantile(rel,q)) for q in (0,.25,.5,.75,1)},'absolute_improvement_quantiles':{str(q):float(np.quantile(diff,q)) for q in (0,.25,.5,.75,1)},'new_independent_observations':0,'source_summary_sha256':hashlib.sha256((R/'results92/SUMMARY92.json').read_bytes()).hexdigest(),'rows':raw}
(R/'audit/local95/DIAGNOSTICS92-IN95.json').write_text(json.dumps(old,indent=2)+'\n')
rows0=[['All configurations',str(old['configurations'])],['Strictly tighter state-dependent bound',str(old['strict_improvements'])],['Equal bounds',str(old['equal_bounds'])],['Looser state-dependent bound',str(old['looser_state_bounds'])],['No-cut configurations',str(old['no_cut_configurations'])],['Candidate / retained pieces',f"{old['candidate_pieces_total']:,} / {old['retained_pieces_total']:,}"]]
table('diagnostics95.tex','Complete distribution audit of the inherited finite-risk catalogue','tab:diagnostics95','lr','Diagnostic & Count',rows0,'Recomputed from every one of the 252 retained configurations, not from an improved subset. These are deterministic finite-risk diagnostics, not new fits, continuous-law experiments or independent economic observations. Detailed absolute and relative quantiles are retained in the source-bound audit.')
(R/'audit/local95/TABLES95.json').write_text(json.dumps({'calibration_sha256':r['calibration_sha256'],'evaluation_sha256':hashlib.sha256((R/'results94/evaluation-local95/RESULTS94.json').read_bytes()).hexdigest(),'tables':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(T.glob('*95.tex'))},'all_intervals_equivalent':all(x['equivalent_within_margin'] for v in r['levels'].values() for x in v['pairwise'].values()),'strict_superiority_contrasts':sum(x['left_superior'] or x['right_superior'] for v in r['levels'].values() for x in v['pairwise'].values())},indent=2)+'\n')
print(json.dumps({k:v for k,v in old.items() if k!='rows'},indent=2))
