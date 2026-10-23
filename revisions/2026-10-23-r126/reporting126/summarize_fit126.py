import json
import sys
from pathlib import Path
from fractions import Fraction as Q
root=Path(sys.argv[1])
def q(x):
 return Q(int(x['numerator']),int(x['denominator']))
def fq(x):
 return {'numerator':str(x.numerator),'denominator':str(x.denominator),'approximation':float(x)}
records=[]
if (root/'records126.jsonl').exists():
 records=[json.loads(l) for l in (root/'records126.jsonl').read_text().splitlines() if l]
execution=json.loads((root/'EXECUTION126.json').read_text()) if (root/'EXECUTION126.json').exists() else None
summary={'scope':'R126 audit-only refits of frozen R121 data; not policy deployment or whole-domain validity','execution':execution,'completed_records':len(records),'declared_case_count':56,'all_successful_records_rounding_verified':all(r['historical_rounding_serialization_verified'] for r in records),'exact_coefficient_matches':sum(r['coefficient_exact_match_to_historical'] for r in records),'changed_readouts':sum(not r['coefficient_exact_match_to_historical'] for r in records),'signed_rounded_objective_comparison':{s:sum((q(r['actual_rounded_objective_difference'])<0 if s=='lower' else q(r['actual_rounded_objective_difference'])>0 if s=='higher' else q(r['actual_rounded_objective_difference'])==0) for r in records) for s in ('lower','equal','higher')},'max_historical_design_discrepancy':{k:fq(max((q(r['historical_design_exact_discrepancies'][k]) for r in records),default=Q(0))) for k in ('value','derivative')},'families':{},'rows':[]}
for family in ('quadratic','relu','hinge','spline','poly2','poly3','grid'):
 rows=[r for r in records if r['arm']==family]
 item={'case_count':len(rows),'max_elapsed_seconds':max((r['elapsed_seconds'] for r in rows),default=0),'solver_seconds':sum(r['solver_seconds'] for r in rows),'exact_coefficient_matches':sum(r['coefficient_exact_match_to_historical'] for r in rows)}
 for loss in ('value','marginal'):
  rr=[r for r in rows if r['loss']==loss]
  c='value_certificate' if loss=='value' else 'marginal_certificate'
  item[loss]={}
  for which in ('stored','independent'):
   vals=[q(r[which+'_'+c]['optimality_gap_upper']) for r in rr]
   item[loss][which+'_maximum_finite_design_gap']=fq(max(vals,default=Q(0)))
 summary['families'][family]=item
for r in records:
 c='value_certificate' if r['loss']=='value' else 'marginal_certificate'
 summary['rows'].append({k:r[k] for k in ('arm','loss','budget','risk_index','feature_count','value_rows','marginal_rows','elapsed_seconds','solver_seconds','coefficient_exact_match_to_historical')}|{'rounded_objective_difference':fq(q(r['actual_rounded_objective_difference'])),'stored_finite_design_gap':fq(q(r['stored_'+c]['optimality_gap_upper'])),'independent_finite_design_gap':fq(q(r['independent_'+c]['optimality_gap_upper']))})
print(json.dumps(summary,indent=2,sort_keys=True))
