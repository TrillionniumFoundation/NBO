"""Regress the actual JSON integer-mean failure and the value-preserving adapter."""
import unittest
import numpy as np
from initial_state_inputs import floating_initial_state
class InitialStateTests(unittest.TestCase):
    def test_declared_integer_means_accept_dispersion(self):
        for d in (10,20,50):
            for mean,sd in ((0,.5),(0,1),(-1,1.5)):
                k=floating_initial_state(dict(shift=mean,spread=sd))
                y=np.full(d,k['shift']);v=np.linspace(-1,1,d);v-=v.mean()
                y+=k['spread']*v/np.sqrt(np.mean(v*v))
                self.assertEqual(y.dtype,np.dtype('float64'))
                self.assertAlmostEqual(float(y.mean()),float(mean),places=14)
                self.assertAlmostEqual(float(y.std()),float(sd),places=14)
    def test_integer_and_float_configuration_values_match(self):
        for mean,sd in ((-2,0),(2,0),(0,.5),(0,1),(-1,1.5)):
            self.assertEqual(floating_initial_state(dict(shift=mean,spread=sd)),floating_initial_state(dict(shift=float(mean),spread=float(sd))))
        self.assertEqual(floating_initial_state(dict(profile='student3')),dict(profile='student3'))
    def test_invalid_initial_state_fails_explicitly(self):
        for kw in (dict(shift=float('nan')),dict(spread=float('inf')),dict(spread=-1)):
            with self.assertRaises(ValueError):floating_initial_state(kw)
if __name__=='__main__':unittest.main(verbosity=2)
