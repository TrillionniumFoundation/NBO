"""Cost identities and numerical-result invariance for the publication audit."""
import copy,hashlib,json,sys,unittest
from pathlib import Path
from accounting import R,correct
class CostTests(unittest.TestCase):
 def test_standalone_initializer_is_charged(self):
  d=json.loads((R/'results/COMMON_ACCOUNTS.json').read_text());cost=d['cost_accounting_correction']['initializer_construction_seconds']
  for r in d['records']:
   own=r['training_seconds']+r['original_reference_seconds']+r['original_policy_evaluation_seconds']+r['policy_evaluation_seconds']
   extra=0. if r['method']=='actor' and r['seed']==29 else cost
   self.assertAlmostEqual(r['total_cost_by_number_policies']['1'],own+d['shared_cover_seconds']+extra,places=9)
   self.assertAlmostEqual(r['total_cost_by_number_policies']['9'],own+d['shared_cover_seconds']/9,places=9)
  self.assertIn('hypothetical',d['cost_accounting_correction']['N100'])
 def test_idempotent_and_numerical_fields_unchanged(self):
  p=R/'results/COMMON_ACCOUNTS.json';before=p.read_bytes();correct();self.assertEqual(before,p.read_bytes())
  old=json.loads((R/'archive/COMMON_ACCOUNTS_before_cost_correction.json').read_text());now=json.loads(p.read_text())
  for a,b in zip(old['records'],now['records']):
   for key in ['method','seed','raw','input_sha256','regret_upper','initial_center_upper','policy_bracket','target_pass','compensation','continuous_state_time_error']:
    self.assertEqual(a[key],b[key],key)
  self.assertEqual(old['raw_sha256'],now['raw_sha256']);self.assertEqual(old['upper_source_sha256'],now['upper_source_sha256'])
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CostTests))
 (R/'results/ACCOUNTING_TESTS.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'success':result.wasSuccessful()},indent=2)+'\n')
 sys.exit(not result.wasSuccessful())
