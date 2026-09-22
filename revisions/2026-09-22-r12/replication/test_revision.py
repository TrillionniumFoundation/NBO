"""Independent finite-geometry tests; tests supplement, not replace, proofs."""
import copy,json,random
from fractions import Fraction as F
import price_envelope as e

def check_raises(fn):
 try:fn()
 except (ValueError,AssertionError):return
 raise AssertionError('Invalid case accepted')
def main():
 checks=[];rng=random.Random(120922);nodes=e.load_nodes();r=e.certify(nodes)
 assert r['status']=='PASS' and F(r['uniform_regret_rational'])<F('0.01')
 assert r['certified_prices']==18 and len(r['cells'])==17
 checks.append('complete_18_node_continuum_target')
 # Independent brute-force ALL pair intersections, including non-envelope ones.
 for cell in r['cells']:
  a,b=F(cell['left']),F(cell['right']);lines=e.lines_on(nodes,a,b);points={a,b}
  for m,c,i in lines:
   for n,d,j in lines:
    if m!=n:
     x=(d-c)/(m-n)
     if a<x<b:points.add(x)
  worst=max(F(e.query(x,nodes)['regret_rational']) for x in points)
  assert worst==F(cell['max_gap_rational'])
 checks.append('exact_hull_vs_independent_all_pair_intersections')
 for _ in range(80):
  lines=[(F(rng.randint(-20,0)),F(rng.randint(-50,50)),i) for i in range(20)]
  hull=e.upper_hull(lines)
  for q in range(-20,21):
   x=F(q,7);valid=[l for l in hull if l[3] is None or l[3]<=x];m,c,*_=valid[-1]
   assert m*x+c==max(a*x+b for a,b,i in lines)
 checks.append('randomized_equal_slope_and_redundant_line_geometry')
 n={'k':2,'L':0,'U':1,'B':[.1,.2]}
 assert e.lines_on([n],F(1),F(2))[0][:2]==(-F(.1),2*F(.1))
 assert e.lines_on([n],F(2),F(3))[0][:2]==(-F(.2),2*F(.2))
 checks.append('cost_transfer_uses_opposite_budget_endpoints')
 for i,cell in enumerate(r['cells']):
  a,b=nodes[i],nodes[i+1];allow=max(F(a['U'])-F(a['L']),F(b['U'])-F(b['L']))+F('.02')*(F(b['k'])-F(a['k']))/4
  assert F(cell['max_gap_rational'])<=allow
 checks.append('conditional_slack_bound_for_every_cell')
 check_raises(lambda:e.certify(nodes[1:]));check_raises(lambda:e.certify(list(reversed(nodes))))
 bad=copy.deepcopy(nodes);bad[2]['U']=float('nan');check_raises(lambda:e.certify(bad))
 bad=copy.deepcopy(nodes);bad[2]['L']=bad[2]['U']+1;check_raises(lambda:e.certify(bad))
 for x in ['.49','8.001']:check_raises(lambda:e.query(x,nodes))
 checks.append('missing_endpoint_order_nonfinite_contradiction_and_out_of_range_rejected')
 for x in ['0.501','1.333333333333333333333333','2.05','4.1234567890123456789','7.99']:
  q=e.query(x,nodes);assert F(q['regret_rational'])<=F(r['uniform_regret_rational'])
  assert F(q['regret_upper'])>=F(q['regret_rational'])
 checks.append('unseen_decimal_queries_and_outward_display')
 h=json.loads((e.REV/'results/refinement_history.json').read_text())
 for row in h['rounds']:
  for k in row['planned_prices']:
   p=e.REV/f'results/cases/k{k:g}/status.json';assert p.is_file() and json.loads(p.read_text())['status']=='success'
 for a in ['interrupted-round2','interrupted-round3']:
  assert any((e.REV/'archive'/a).glob('*/status.json'))
 checks.append('all_planned_cells_completed_and_interrupted_attempts_retained')
 result={'status':'PASS','checks':checks,'random_seed':120922,'review_scope':'exact algebra and evidence acceptance; not a claim of formal proof-assistant verification'}
 e.dump(e.REV/'validation_tests.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
