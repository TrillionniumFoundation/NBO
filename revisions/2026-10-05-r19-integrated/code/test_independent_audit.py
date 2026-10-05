"""Post-freeze exact-arithmetic proof checks; no fitting or protocol changes."""
from fractions import Fraction as F
import unittest,math,json
from pathlib import Path
import numpy as np
from intervals import I

class ExactChecks(unittest.TestCase):
    def test_log_two_rational_bracket(self):
        z=F(1,3);s=2*sum(z**(2*j+1)/F(2*j+1) for j in range(32));tail=2*z**65/(65*(1-z*z))
        lower=F.from_float(float.fromhex('0x1.62e42fefa39eep-1'));upper=F.from_float(float.fromhex('0x1.62e42fefa39f0p-1'))
        self.assertLess(lower,s);self.assertGreater(upper,s+tail)
    def test_exp_tail_majorant(self):
        t=F(1,2);s=sum(t**j/math.factorial(j) for j in range(19));tail=t**19/math.factorial(19)/(1-t/20)
        partial=sum(t**j/math.factorial(j) for j in range(65))
        self.assertGreater(partial,s);self.assertLess(partial,s+tail)
    def test_centered_bound_exact(self):
        p=[F(1,5),F(3,10),F(1,2)];e=[F(1,2),F(-7,10),F(9,10)];mean=sum(a*b for a,b in zip(p,e));risk=sum(a*(b-mean)**2 for a,b in zip(p,e))
        for i in range(3):
            for j in range(3):self.assertLessEqual((e[i]-e[j])**2,(1/p[i]+1/p[j])*risk)
    def test_cost_envelopes_direction(self):
        # Two upper bounds do not establish a ranking; an upper/lower pair can.
        self.assertLess(10+100*1,0+100*2)
        self.assertGreater(10+1*1,0+1*2)
    def test_registered_stopping_and_costs(self):
        r=Path(__file__).resolve().parents[1]/'results/registered/SUMMARY.json'
        if not r.exists():self.skipTest('full economic record not yet generated')
        records=json.loads(r.read_text())['records'];self.assertEqual(len(records),252)
        for row in records:
            successes=[i+1 for i,x in enumerate(row['stages']) if x['certificate']['mean_regret_upper']<=1e-4]
            if successes:self.assertEqual(row['selected_stage'],successes[0])
            component=row['task_initialization_seconds']+sum(s['fit_and_cache_seconds']+s['query_seconds']+s['verification_seconds'] for s in row['stages'])
            self.assertGreaterEqual(row['accounted_service_seconds'],component)
    def test_nested_task_catalogues(self):
        from economy import tasks
        for d in (10,50):
            y,t=tasks(1024,d,195520+d)
            for n in (1,4,16,64,256):
                yy,tt=tasks(n,d,195520+d)
                np.testing.assert_array_equal(yy,y[:n]);np.testing.assert_array_equal(tt,t[:n])

if __name__=='__main__':unittest.main(verbosity=2)
