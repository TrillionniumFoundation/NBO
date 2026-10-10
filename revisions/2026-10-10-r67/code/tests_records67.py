"""Mutation regressions for the corrected frozen record validator."""
import copy,unittest,numpy as np
import audit67 as a
class Records(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=a.s.specs()[0];cls.folder=a.S/'results67'/cls.spec['key'];cls.summary=a.read(cls.folder/'summary.json')
        with np.load(cls.folder/'trace.npz') as z:cls.trace={k:z[k].copy() for k in z.files}
        cls.rr,cls.initial=a.s.workload(2,2,64,661204)
    def validate(self,tr):return a.validate_path(self.spec,tr,self.rr,self.initial,self.summary['account'],named=True)
    def mutate(self,key,value):
        tr={k:v.copy() for k,v in self.trace.items()};tr[key].flat[0]=value;return tr
    def test_valid_path(self):self.assertEqual(self.validate(self.trace),(128,2))
    def test_infeasible_action_rejected(self):
        with self.assertRaises(AssertionError):self.validate(self.mutate('t0_action',1.))
    def test_nonlattice_action_rejected(self):
        with self.assertRaises(AssertionError):self.validate(self.mutate('t0_action',1/3))
    def test_observation_change_rejected(self):
        with self.assertRaises(AssertionError):self.validate(self.mutate('t0_observed',.5))
    def test_cost_lower_corruption_rejected(self):
        with self.assertRaises(AssertionError):self.validate(self.mutate('cost_lo',self.trace['cost_lo'][0]+.01))
    def test_cost_upper_corruption_rejected(self):
        with self.assertRaises(AssertionError):self.validate(self.mutate('cost_hi',self.trace['cost_hi'][0]-.01))
    def test_gap_corruption_rejected(self):
        with self.assertRaises(AssertionError):self.validate(self.mutate('t0_gap',0.5))
    def test_gap_rounding_direction_checked(self):
        with self.assertRaises(AssertionError):self.validate(self.mutate('t0_gap',0.))
    def test_digest_corruption_rejected(self):
        with self.assertRaises(AssertionError):a.checked(self.folder/'trace.npz','0'*64)
    def test_progress_arithmetic_corruption_rejected(self):
        tr={k:v.copy() for k,v in self.trace.items()};tr['progress'][0,8]+=1
        with self.assertRaises(AssertionError):a.progress(tr,self.summary['account']['local_tolerance'],self.summary['counts'],2)
    def test_screen_count_corruption_rejected(self):
        co=copy.deepcopy(self.summary['counts']);co['screen_returns']+=1
        with self.assertRaises(AssertionError):a.progress(self.trace,self.summary['account']['local_tolerance'],co,2)
    def test_old_counterexample_is_preserved(self):
        e=a.read(a.R/'audit/ERRATUM67.json')
        self.assertGreater(a.F(e['original_lower_excess_exact']),0)
        self.assertFalse(e['original_scientific_files_modified'])
if __name__=='__main__':unittest.main(verbosity=2)
