"""Small constructed reporting fixture; reads no actual economic records.

Two synthetic service cells and 32 fabricated interval observations isolate
the difference between the first 16 mean and the full 32 mean. Fixture-only
catalogue/census substitution never enters the production adapter.
"""
from fractions import Fraction as F
import json
from types import SimpleNamespace
import unittest

import report123 as frozen
import report_adapter123 as adapter


def fixture():
    neural = (0,5,'relu','value','fused')
    baseline = (0,5,'quadratic','value','r122')
    keys = [neural,baseline]
    primary,values = {},{}
    for j in range(32):
        state = [float(j/32).hex(),float(0).hex()]
        for key,action in ((neural,float(0).hex()),(baseline,float(1).hex())):
            row = dict(index=0,row=j,state_hex=state,action_hex=action)
            primary[key+(j,)] = row
            # Comparator minus neural equals +tau/4 for first16, -tau/4 last16.
            v = F(1) if key==baseline else F(1)+(F(-1) if j<16 else F(1))*frozen.TAU/4
            values[frozen.action_key(0,state,action)] = dict(j_lower=v,j_upper=v)
    clocks = {}
    for scenario in frozen.SCENARIOS:
        for key in keys:
            clocks[scenario,key] = dict(n=32 if scenario=='primary32' else 16,
                historical_complete_acquisition_seconds=F(0),shared_process_residual_seconds=F(0),
                cold_load_seconds=F(0),complete_cohort_seconds=F(1))
    data = dict(primary=primary,independent=dict(values=values))
    return keys,data,clocks


def tiny_environment(keys):
    namespace = dict(vars(frozen))
    namespace['common'] = SimpleNamespace(groups=lambda:list(keys))
    def require(condition,message):
        if message == 'Complete cost/adoption census failed':
            # Only the tiny fixture changes the catalogue. Its complete output
            # census is checked independently by the assertions below.
            return
        frozen.require(condition,message)
    namespace['require'] = require
    return namespace


class ReportingAdapterFixture(unittest.TestCase):
    def test_original_defect_and_matching_scenario_fix(self):
        keys,data,clocks = fixture()
        namespace = tiny_environment(keys)
        original,_ = adapter.patched_source()
        exec(compile(original,'<unmodified frozen fixture>','exec'),namespace)
        old = namespace['price_tables'](data,clocks)
        self.assertTrue(all(r['sample_gain_lower']==r['sample_gain_upper']==0 for r in old[1]))
        volumes,constraints,menus,intersections = adapter.make_price_tables(tiny_environment(keys))(data,clocks)
        self.assertEqual((len(volumes),len(constraints),len(menus),len(intersections)),(32,16,16,4))
        for row in constraints:
            expected = F(0) if row['scenario']=='primary32' else frozen.TAU/4
            self.assertEqual(row['sample_gain_lower'],expected)
            self.assertEqual(row['sample_gain_upper'],expected)
            self.assertEqual(row['policy_means_saved_state_units'],32 if row['scenario']=='primary32' else 16)
            self.assertEqual(row['policy_means_conditional_on_32_saved_states'],row['scenario']=='primary32')
            self.assertTrue(row['matching_scenario_sample'])
        for row in menus:
            self.assertEqual(row['sufficient_price_domain']['empty'],row['scenario']=='primary32')
        self.assertTrue(all(not row['sufficient_price_domain']['empty'] for row in intersections))

    def test_inconsistent_clock_sample_is_rejected(self):
        keys,data,clocks = fixture()
        clocks['timing1',keys[0]]['n'] = 32
        with self.assertRaisesRegex(ValueError,'match the declared scenario cohort'):
            adapter.make_price_tables(tiny_environment(keys))(data,clocks)

    def test_primary_outputs_and_frozen_nonprice_functions_are_retained(self):
        keys,data,clocks = fixture()
        namespace = tiny_environment(keys)
        original,_ = adapter.patched_source()
        exec(compile(original,'<unmodified frozen fixture>','exec'),namespace)
        old = namespace['price_tables'](data,clocks)
        new = adapter.make_price_tables(tiny_environment(keys))(data,clocks)
        self.assertEqual(old[0],new[0])  # All original clock/cost calculations.
        for left,right in zip(old[1],new[1]):
            if left['scenario']=='primary32':
                reduced = dict(right)
                reduced.pop('policy_means_saved_state_units')
                reduced.pop('matching_scenario_sample')
                self.assertEqual(left,reduced)
        self.assertEqual(frozen.self_check()['status'],'passed')


if __name__ == '__main__':
    unittest.main(verbosity=2)
