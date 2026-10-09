"""Disjoint, small development/regression tests; not production observations."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import math,sys,tempfile,unittest
import numpy as np
import neural55 as n
import prospective55 as p
import null55 as u

class Tests(unittest.TestCase):
    def test_exact_hinge_integral(self):
        for r in (F(0),F(1,16),F(1,2**30)):
            for x in (F(-1),-r,F(0),r,F(1),r/2):
                exact=max(F(0),x) if r==0 else (max(F(0),x+r)**2-max(F(0),x-r)**2)/(4*r)
                out=n.hinge_mean(n.I.point(np.array([float(x)])),r)
                self.assertLessEqual(F(float(out.lo[0])),exact);self.assertGreaterEqual(F(float(out.hi[0])),exact)
    def test_hinge_interval_monotonic(self):
        z=n.I(np.array([-.2,-.01,.1]),np.array([.1,.2,.7]));out=n.hinge_mean(z,F(1,32))
        for a in np.linspace(0,1,37):
            point=n.hinge_mean(n.I.point(np.clip(z.lo+a*(z.hi-z.lo),z.lo,z.hi)),F(1,32))
            self.assertTrue(np.all(out.lo<=point.hi));self.assertTrue(np.all(point.lo<=out.hi))
    def test_ridge_expectation_rational_reference(self):
        W=np.array([[.5,-.25],[.25,.5]]);b=np.array([-.125,-.25]);v=np.array([.25,.5]);weights=np.array([1.,-.5])
        model=n.Critic('relu',2,dict(W=W,b=b,v=v,u=weights,c=np.array(.125)))
        for xx,a in product(([F(1,8),F(3,4)],[F(7,8),F(1,4)]),(F(0),F(1,8))):
            y=[F(1,16)+xx[j]/2+xx[(j+1)%2]/8+xx[j]*(1-xx[(j+1)%2])/16+(F(1,2) if j==0 else F(1,4))*a for j in range(2)]
            exact=F(1,8)+sum(F(float(v[j]))*y[j] for j in range(2))
            for k in range(2):
                z=sum(F(float(W[j,k]))*y[j] for j in range(2))+F(float(b[k]));r=abs(F(float(W[0,k]))-F(float(W[1,k])))/32
                exact+=F(float(weights[k]))*(max(F(0),z+r)**2-max(F(0),z-r)**2)/(4*r)
            out=model.expected(n.I.point(np.array([list(map(float,xx))])),n.I.point(np.array([float(a)])))
            self.assertLessEqual(F(float(out.lo[0])),exact);self.assertGreaterEqual(F(float(out.hi[0])),exact)
    def test_quadratic_variance(self):
        Q=np.array([[1.,.25],[.25,2.]]);m=n.Critic('quadratic',2,dict(Q=Q,v=np.zeros(2),c=np.array(0.)))
        x=np.array([[.2,.7]]);a=np.array([.125]);center=n.next_point(x,a)
        exact=m.point(center)[0]+2.5/3072
        out=m.expected(n.I.point(x),n.I.point(a))
        self.assertLessEqual(out.lo[0],exact);self.assertGreaterEqual(out.hi[0],exact)
    def test_partition_full_volume_and_nontensor(self):
        part=n.Partition(4,13)
        self.assertEqual(sum((math.prod(F(float(v)) for v in b-a) for a,b in zip(part.lo,part.hi)),F(0)),1)
        points=np.random.default_rng(901).random((700,4));ids=part.locate(points)
        self.assertTrue(np.all(points>=part.lo[ids]) and np.all(points<=part.hi[ids]))
        tensor=math.prod(len(np.unique(np.r_[part.lo[:,j],part.hi[:,j]]))-1 for j in range(4))
        self.assertGreater(tensor,len(part.lo))
    def test_nested_acquisition(self):
        a=n.Partition(2,7);b=n.Partition(2,29);ids=a.locate(b.centers)
        self.assertTrue(np.all(b.lo>=a.lo[ids]) and np.all(b.hi<=a.hi[ids]))
    def test_actor_closed_range(self):
        part=n.Partition(2,13);pol=np.arange(13,dtype=np.uint16)*16
        box=n.I(np.array([[0.,0.]]),np.array([[1.,1.]]));out=part.actor(box,pol)
        self.assertEqual(out.lo[0],0);self.assertEqual(out.hi[0],192/4096)
    def test_learned_layer_moves(self):
        rng=np.random.default_rng(907);x=rng.random((48,2));y=(x[:,0]-.5)**2+x[:,1]**2
        m=n.fit('relu',x,y,908,width=8,epochs=15);W0=np.random.default_rng(908).normal(0,.7/(2**.5),(2,8))
        self.assertFalse(np.allclose(W0,m.params['W']))
        self.assertLess(np.mean((m.point(x)-y)**2),np.var(y))
    def test_centered_residual_contains_points(self):
        rng=np.random.default_rng(909);x=rng.random((48,2));y=n.primitive_point(x,0,terminal=True)
        c=n.fit('relu',x,y,910,width=8,epochs=12);future=n.Critic.terminal(2);part=n.Partition(2,11);policy=part.capindex//2
        res=n.residual(c,future,part,policy,q=2)
        for v in rng.random((12,2)):
            point=part.lo+(part.hi-part.lo)*v;a=n.I.point(policy/4096);xx=n.I.point(point)
            r=n.s.costs(xx,a,1)+float(n.BETA)*future.expected(xx,a)-c.interval(xx)
            self.assertTrue(np.all(res.lo<=r.hi) and np.all(r.lo<=res.hi))
    def test_cache_contains_constant_policy_value(self):
        part=n.Partition(2,11);pol=np.zeros((2,11),dtype=np.uint16);crit=[n.Critic.zero(2),n.Critic.zero(2),n.Critic.terminal(2)];cache=n.Cache(crit,part,pol,q=2)
        z,w=np.polynomial.legendre.leggauss(64)
        for k,x in enumerate(part.centers):
            yy=n.next_point(np.repeat(x[None,:],64,axis=0),np.zeros(64),z/32)
            future=n.o.final_q(n.I.point(yy),n.I.point(np.zeros(64)),1).midpoint()
            val=n.primitive_point(x[None,:],np.zeros(1))[0]+float(n.BETA)*np.dot(w,future)/2
            self.assertLessEqual(cache.direct[0].lo[k],val);self.assertGreaterEqual(cache.direct[0].hi[k],val)
    def test_final_safe_sweep_and_decomposition(self):
        part=n.Partition(2,19);pol=np.zeros((1,19),dtype=np.uint16);cache=n.Cache([n.Critic.zero(2),n.Critic.terminal(2)],part,pol,q=2)
        new,report,raw=cache.sweep();U=raw['t0_U'];L=raw['t0_L'];C=raw['t0_C']
        self.assertTrue(np.all(U<=0) and np.all(L<=C) and np.all(C<=U))
        self.assertTrue(np.all(new<=part.capindex));self.assertTrue(np.allclose(U-L,(U-C)+(C-L)))
        true=n.o.final_difference(part.box,n.I.point(new[0]/4096),n.I.point(np.zeros(19)),1)
        changed=new[0]!=0;self.assertTrue(np.all(true.hi[changed]<=0))
    def test_positive_exposure_uncertainty_bound(self):
        B=n.I(np.array([.4,.2]),np.array([.6,.3]));v=np.array([1.,-2.]);s=n.dot(n.I(B.lo[None,:],B.hi[None,:]),v)
        for x,y in product(np.linspace(.4,.6,9),np.linspace(.2,.3,9)):
            self.assertLessEqual(abs(x-2*y),max(abs(s.lo[0]),abs(s.hi[0])))
    def test_parameterized_cost_identity(self):
        rng=np.random.default_rng(911);x=n.I.point(rng.random((20,4)));a=n.I.point(np.full(20,.125));b=n.I.point(np.full(20,.0625));B=n.I.point(np.array([.5,.25,.5,.25]))
        direct=n.o.final_difference(x,a,b,1);other=u.terminal_difference(x,a,b,B)
        self.assertTrue(np.all(other.lo<=direct.hi) and np.all(direct.lo<=other.hi))
    def test_fitted_direction_not_truth_input(self):
        data,bins=u.estimate(4,32,912);v=u.direction(data);mean=data.mean(0)
        self.assertLess(abs(v@mean),1e-6);self.assertFalse(np.array_equal(mean,np.array([.5,.25,.5,.25])))
    def test_confidence_box_numerical_account(self):
        data=np.tile([.5,.25],(64,1));box,rad=u.confidence(data)
        self.assertTrue(np.all(box.lo<np.array([.5,.25])) and np.all(box.hi>np.array([.5,.25])))
    def test_inference_support_and_exact_stop(self):
        lo=np.full(64,.1);hi=np.full(64,.1);c=p.ci(lo,hi,F(0),F(1))
        self.assertLessEqual(F(c['exact'][0]),F(1,10));self.assertGreaterEqual(F(c['exact'][1]),F(1,10))
        self.assertGreaterEqual(F(c['exact'][0]),0);self.assertLessEqual(F(c['exact'][1]),1)
    def test_finite_error_family_is_sufficient(self):
        methods=5+3+3;slots=methods*2*3*2*3*3
        self.assertLessEqual(slots,p.FAMILY)
        self.assertGreater(sum((F(p.LOG)**j/math.factorial(j) for j in range(80)),F(0)),4*p.FAMILY/p.ALPHA)
    def test_nonconstant_neural_expected_gradient(self):
        rng=np.random.default_rng(913);m=n.fit('relu',rng.random((32,2)),rng.random(32),914,width=7,epochs=5)
        x=np.array([[.35,.55]]);a=np.array([.1]);g=m.expected_gradient(n.I.point(x),n.I.point(a))
        self.assertTrue(np.all(np.isfinite(g.lo)) and np.all(g.lo<=g.hi))

if __name__=='__main__':unittest.main(verbosity=2)
