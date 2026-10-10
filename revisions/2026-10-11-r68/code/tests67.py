"""Independent rational and primitive tests, not scientific observations."""
import unittest,itertools,math
from fractions import Fraction as F
import numpy as np
import kernel66 as k
import vector66 as v
import science67 as s

class OperationalTests(unittest.TestCase):
    def test_strong_chord_rational_quadratics(self):
        for H,mu,l,u,a in itertools.product((F(2),F(5)),(F(1),F(2)),(F(0),F(1,16)),(F(1,8),F(1,4)),(F(0),F(1,2),F(1))):
            point=l+a*(u-l);f=lambda x:H*x*x/2-F(1,7)*x+1
            bound=k.chord_upper(np.array([float(l)]),np.array([float(u)]),np.array([k.q.up(f(l))]),np.array([k.q.up(f(u))]),np.array([float(point)]),mu)
            self.assertGreaterEqual(F(float(bound[0])),f(point))
    def test_boundary_chord_does_not_invent_interior(self):
        for a in (0.,.25):
            z=k.chord_upper(np.array([0.]),np.array([.25]),np.array([1.]),np.array([2.]),np.array([a]))
            self.assertGreaterEqual(z[0],1 if a==0 else 2)
    def test_screen_can_close_without_a_query(self):
        # f(a)=(a-1/8)^2 with mu=H=2. Endpoints are both 1/64.
        U=k.chord_upper(np.array([0.]),np.array([.25]),np.array([1/64]),np.array([1/64]),np.array([.125]))[0]
        L=k.q.parabola_lower(np.array([1/64]),np.array([1/64]),np.array([.25]),F(2))[0]
        self.assertLess(U-L,1e-12);self.assertGreater(1/64-L,.01)
    def test_all_predictor_interfaces(self):
        x=np.array([[.1,.7],[.9,.2],[.4,.5]])
        for kind in k.KINDS:
            models,_=k.fit(2,2,13,kind,rows=12);o=k.Oracle(kind,models,record=True)
            r=o.solve(x,2,.005);self.assertTrue((r['gap']<=.005).all());self.assertTrue((r['action']<=k.q.cap_point(x)).all())
            self.assertLessEqual(o.counts['routed_queries'],o.counts['refinements'])
            for rows in o.progress:self.assertTrue((rows[:,8:10]>=-1e-14).all())
    def test_model_roundtrip(self):
        x=np.array([[.2,.6],[.1,.9]])
        for kind in k.LEARNED:
            m,_=k.fit(2,2,14,kind,rows=12);loaded=k.load_models(kind,k.dump_models(kind,m))
            self.assertTrue(np.array_equal(k.predict(kind,m[2],x,k.q.cap_point(x)),k.predict(kind,loaded[2],x,k.q.cap_point(x))))
    def test_nonfinite_prediction_is_only_proposal(self):
        x=np.array([[.3,.8]]);z=k.q.clamp(np.array([np.nan]),k.q.cap_point(x));self.assertTrue(np.isfinite(z).all())
    def test_anchor_transfer_bound(self):
        # Q(x,a)=(a-x/8)^2+x, with feasible fixed small actions.
        f=lambda x,a:(a-x/8)**2+x
        for x,y,a,b in itertools.product((F(0),F(1,2),F(1)),repeat=4):
            a/=4;b/=4
            gamma=f(x,a)-x
            upper=gamma+F(3)*abs(y-x)+abs(a-b)
            self.assertLessEqual(f(y,b)-y,upper)
    def test_gaussian_free_log_upper(self):
        self.assertGreater(sum(F(9)**j/math.factorial(j) for j in range(50)),8000)
    def test_inference_contains_constant(self):
        z=np.full(100,.75);L,U=s.infer_interval(z,z,F(1));self.assertLessEqual(L,.75);self.assertGreaterEqual(U,.75)
    def test_acquisition_budget(self):
        for T in (2,3,4):
            for eps in ('1/4','1/64','1/128'):
                _,value=s.budget(T,eps);self.assertLessEqual(F(value),F(eps))
    def test_source_catalogue_count(self):
        records=s.specs();self.assertEqual(len(records),212);self.assertEqual(len({x['key'] for x in records}),212)
    def test_continuous_bin_path_enclosure(self):
        rng,x=s.workload(2,2,8,997,True);o=k.Oracle();a,account=s.paths(o,x,rng,2,'1/128')
        self.assertTrue((a['cost_lo']<=a['cost_hi']).all());self.assertEqual(account['ambiguous_paths'],0)
    def test_vector_terminal_exact_moments(self):
        for x,a in (([F(1,4),F(3,4)],[F(1,16),F(1,32)]),([F(1,8)]*4,[F(1,16)]*2)):
            d=len(x);y=[F(1,16)+x[j]/2+x[(j+1)%d]/8+x[j]*(1-x[(j+1)%d])/16+(F(1,2) if j%2==0 else F(1,4))*a[0]+(F(1,4) if j%2==0 else F(1,2))*a[1] for j in range(d)]
            radius=F(1,32);b=F(1,2)-2*sum(y)/d;moment=(max(F(0),b+radius)**3-max(F(0),b-radius)**3)/(6*radius)
            exact=v.exact_stage(x,a)+k.B*(4*sum((z-F(5,8))**2 for z in y)/d+sum((y[j]-y[(j+1)%d])**2 for j in range(d))/(4*d)+2*moment+F(1,512))
            # Rational input points must be evaluated at their actual binary64 values.
            xf=np.array([[float(z) for z in x]]);af=np.array([[float(z) for z in a]])
            value,_=v.terminal_value_grad(xf,af)
            self.assertLessEqual(F(float(value.lo[0])),exact);self.assertGreaterEqual(F(float(value.hi[0])),exact)
    def test_vector_terminal_gradient(self):
        x=np.array([[.2,.7],[.1,.1]]);a=np.array([[.07,.04],[.04,.06]])
        _,g=v.terminal_value_grad(x,a)
        for j in range(2):
            e=np.zeros_like(a);e[:,j]=1e-6
            numerical=(v.terminal_value_grad(x,a+e)[0].midpoint()-v.terminal_value_grad(x,a-e)[0].midpoint())/(2e-6)
            self.assertTrue(np.max(abs(numerical-g.midpoint()[:,j]))<1e-8)
    def test_triangular_dual_lower(self):
        vertices=np.array([[[0.,0.],[.25,0.],[0.,.25]]]);H=F(4)
        f=lambda z:2*np.sum((z-np.array([.06,.08]))**2,axis=-1)+.5
        lb=v.parabolic_triangle_lower(vertices,f(vertices),H)[0]
        self.assertLessEqual(lb,.5);self.assertGreater(lb,.49999999)
    def test_vector_policy_and_precision(self):
        x=np.array([[.2,.7],[.75,.5]]);o=v.Oracle();r=o.solve(x,2,.04)
        self.assertTrue((r['gap']<=.04).all());self.assertTrue((r['action'].sum(axis=1)<=k.q.cap_point(x)).all());self.assertEqual(o.counts['stored_state_nodes'],0)
    def test_simplex_rounding(self):
        cap=np.array([.2,.15]);a=v.project(np.array([[1.,-.1],[.2,.3]]),cap)
        self.assertTrue((a>=0).all());self.assertTrue((a.sum(axis=1)<=cap).all());self.assertTrue((a*2**32==np.floor(a*2**32)).all())

class AccumulatorRegressionTests(unittest.TestCase):
    def test_point_endpoints_must_not_be_mutated_as_independent_buffers(self):
        z=s.I.point(np.zeros(3))
        self.assertTrue(np.shares_memory(z.lo,z.hi))
        fixed=s.I(np.zeros(3),np.zeros(3))
        self.assertFalse(np.shares_memory(fixed.lo,fixed.hi))
        fixed.lo[:]=-1.;fixed.hi[:]=1.
        self.assertTrue(np.all(fixed.lo==-1.))

    def test_repaired_path_contains_independent_rational_midpoint(self):
        F=s.F;B=s.B;den=2**s.BINBITS
        randoms,initial=s.workload(2,2,4,661204)
        trace,account=s.paths(k.Oracle('adaptive'),initial,randoms,2,'1/128')
        for row in range(4):
            x=[[F(0)]*2,[F(1)]*2,[F(1,4)]*2,[F(3,4)]*2][row];total=F(0)
            def cost(x,a=None):
                d=len(x);short=max(F(0),F(1,2)-2*sum(x)/d)
                value=(4 if a is None else 2)*sum((v-F(5,8))**2 for v in x)/d
                value+=sum((x[j]-x[(j+1)%d])**2 for j in range(d))/(4*d)+2*short**2
                return value if a is None else value+a*a+4*a**4
            for t in range(2):
                a=F(float(trace[f't{t}_action'][row]));total+=B**t*cost(x,a)
                z=F(2*int(randoms['shock_index'][t,row])+1,32*den)-F(1,32)
                x=[F(1,16)+F(9,16)*v+x[(j+1)%2]/8-v*x[(j+1)%2]/16+(F(1,2) if j%2==0 else F(1,4))*a+(z if j%2==0 else -z) for j,v in enumerate(x)]
            total+=B**2*cost(x)
            self.assertLessEqual(F(float(trace['cost_lo'][row])),total)
            self.assertLessEqual(total,F(float(trace['cost_hi'][row])))

if __name__=='__main__':unittest.main(verbosity=2)
