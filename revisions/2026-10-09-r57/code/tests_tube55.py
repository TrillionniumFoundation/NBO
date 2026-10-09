"""Exact rational derivative tests on disjoint tiny development tasks."""
import unittest
from fractions import Fraction as F
from itertools import product
import numpy as np
import neural55 as n
import tube55 as t

def state(x,z):
    d=len(x)
    return [F(1,16)+x[j]/2+x[(j+1)%d]/8+x[j]*(1-x[(j+1)%d])/16+(1 if j%2==0 else -1)*z for j in range(d)]
def gradient(x,terminal=False):
    d=len(x);short=max(F(0),F(1,2)-2*sum(x)/d)
    return [(F(8 if terminal else 4,d))*(x[j]-F(5,8))+(2*x[j]-x[(j+1)%d]-x[(j-1)%d])/(2*d)-F(8,d)*short for j in range(d)]
def exact_path(x,innovations):
    states=[x]
    for z in innovations:states.append(state(states[-1],z))
    g=gradient(states[-1],True)
    for x in reversed(states[:-1]):
        local=gradient(x)
        g=[local[j]+n.BETA*(g[j]*(F(1,2)+(1-x[(j+1)%len(x)])/16)+g[(j-1)%len(x)]*(F(1,8)-x[(j-1)%len(x)]/16)) for j in range(len(x))]
    return g

class TubeTests(unittest.TestCase):
    def test_monotone_state_enclosure(self):
        x=n.I(np.array([[.125,.25]]),np.array([[.75,.875]]));a=n.I(np.array([0.]),np.array([.125]));z=n.I(np.array([-1/32]),np.array([1/32]));box=t.monotone_next(x,a,z)
        for xx,yy,aa,zz in product((F(1,8),F(3,4)),(F(1,4),F(7,8)),(F(0),F(1,8)),(F(-1,32),F(1,32))):
            exact=state([xx,yy],zz);exact=[exact[0]+aa/2,exact[1]+aa/4]
            for j in range(2):
                self.assertLessEqual(F(float(box.lo[0,j])),exact[j]);self.assertGreaterEqual(F(float(box.hi[0,j])),exact[j])
    def test_exact_path_gradient(self):
        for d in (2,4):
            for remaining in range(4):
                x=[F(2+j,8) for j in range(d)];box=n.I.point(np.array([list(map(float,x))]));enclosure=t.gradient_tube(box,remaining)
                for noise in product((F(-1,32),F(0),F(1,32)),repeat=remaining):
                    exact=exact_path(x,list(noise))
                    for j in range(d):
                        self.assertLessEqual(F(float(enclosure.lo[0,j])),exact[j]);self.assertGreaterEqual(F(float(enclosure.hi[0,j])),exact[j])
    def test_gradient_entire_initial_box(self):
        x=n.I(np.array([[.25,.375]]),np.array([[.5,.625]]));box=t.gradient_tube(x,3)
        for xx,yy in product((F(1,4),F(3,8),F(1,2)),(F(3,8),F(1,2),F(5,8))):
            g=exact_path([xx,yy],[F(-1,32),F(1,32),F(0)])
            for j in range(2):self.assertLessEqual(F(float(box.lo[0,j])),g[j]);self.assertGreaterEqual(F(float(box.hi[0,j])),g[j])
    def test_terminal_contrast_matches_original(self):
        x=n.I.point(np.array([[.125,.25],[.5,.75]]));a=n.I.point(np.array([.0625,.125]));tube=t.signed_zero_advantage(x,a,0,2)
        direct=n.o.final_difference(x,a,n.I.point(np.zeros(2)),1)
        self.assertTrue(np.all(tube.lo<=direct.hi) and np.all(tube.hi>=direct.lo))
    def test_only_smooth_reference_uses_tubes(self):
        part=n.Partition(2,7);pol=np.ones((2,7),dtype=np.uint16)*64;h=[n.Critic.zero(2),n.Critic.zero(2),n.Critic.terminal(2)]
        cache=t.TubeCache(h,part,pol,q=2);out,report,raw=cache.sweep()
        self.assertFalse(cache.zero_reference);self.assertFalse(any(z['tube_enabled'] for z in report));self.assertEqual(cache.tube_work,{})
    def test_nonterminal_changes_and_safe_intersection(self):
        part=n.Partition(2,11);pol=np.zeros((3,11),dtype=np.uint16);h=[n.Critic.zero(2)]*3+[n.Critic.terminal(2)]
        cache=t.TubeCache(h,part,pol,q=2);out,report,raw=cache.sweep()
        self.assertGreater(sum(x['changed'] for x in report[:-1]),0)
        for date in range(3):
            self.assertTrue(np.all(raw[f't{date}_U']<=0));self.assertTrue(np.all(out[date]<=part.capindex))
            for base,tube,final,enabled in cache.trace[date]:
                self.assertTrue(np.all(final.lo>=base.lo) and np.all(final.hi<=base.hi))
    def test_linear_horizon_gradient_work(self):
        x=n.I.point(np.full((5,4),.5));work={};t.gradient_tube(x,7,work)
        self.assertEqual(work['tube_state_rows'],40);self.assertEqual(work['tube_jacobian_coordinates'],140)
    def test_sparse_drift_derivative_bound(self):
        for a,b in product((F(0),F(1,3),F(1)),repeat=2):
            row=F(1,2)+(1-b)/16+F(1,8)-a/16
            self.assertLessEqual(row,F(11,16));self.assertGreaterEqual(row,0)
if __name__=='__main__':unittest.main(verbosity=2)
