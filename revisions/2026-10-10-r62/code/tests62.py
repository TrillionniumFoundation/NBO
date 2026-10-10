"""Disjoint R62 mathematical/numerical fixtures, not economic observations."""
from fractions import Fraction as F
import itertools,unittest
import numpy as np
from scipy.optimize import minimize_scalar
import core62 as c

class R62Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (c.R/'build/interpolate62.so').exists():c.compile_kernel()
    def test_uniform_regularities(self):
        for d,m,T in itertools.product((2,4,8,16),(1,2),(1,2,3,10,100)):
            k=c.constants(d,m,T,4,16,4)
            self.assertTrue(all(z<=F(19,d) for z in k['G']))
            self.assertTrue(all(z<=F(42,d) for z in k['M']))
            self.assertTrue(all(F(4,d)-c.B*z/8>=F(71,32*d) for z in k['G']))
    def test_native_signed_interpolation_exact_rationals(self):
        rng=np.random.default_rng(620099)
        for d,sub in ((2,4),(4,2),(8,2)):
            values=rng.integers(-1024,1025,size=(sub+1)**d).astype(float)/64;tab=c.Table(values,d,sub)
            points=rng.integers(0,257,size=(6,d))/256;computed=tab.interval(c.I.point(points));cube=values.reshape((sub+1,)*d)
            for k,x in enumerate(points):
                loc=[min(int(z*sub),sub-1) for z in x];f=[F(float(z))*sub-loc[j] for j,z in enumerate(x)];total=F(0)
                for bits in itertools.product((0,1),repeat=d):
                    w=F(1)
                    for j,b in enumerate(bits):w*=f[j] if b else 1-f[j]
                    total+=w*F(float(cube[tuple(loc[j]+bits[j] for j in range(d))]))
                self.assertLessEqual(F(float(computed.lo[k])),total);self.assertGreaterEqual(F(float(computed.hi[k])),total)
    def test_native_boundary_and_constant(self):
        tab=c.Table(np.ones(3**4)*7,4,2);x=np.array(list(itertools.product((0,.5,1),repeat=4)))
        v=tab.interval(c.I.point(x));self.assertTrue(np.all(v.lo<=7) and np.all(v.hi>=7))
    def test_native_rejects_domain_violation(self):
        tab=c.Table(np.zeros(9),2,2)
        with self.assertRaises(AssertionError):tab.point(np.array([[1.01,0.]]))
    def test_native_box_contains_corner_values(self):
        rng=np.random.default_rng(92);tab=c.Table(rng.normal(size=25),2,4)
        lo=np.array([[.1,.2],[.24,.49],[0.,0.]]);hi=lo+.2;v=tab.interval(c.I(lo,hi))
        for b in itertools.product((0,1),repeat=2):
            x=np.where(np.array(b),hi,lo);a=tab.point(x)
            self.assertTrue(np.all(a>=v.lo) and np.all(a<=v.hi))
    def test_second_order_convex_interpolation(self):
        for d in (2,4):
            sub=4;points=np.array(list(itertools.product(np.arange(sub+1)/sub,repeat=d)))
            vals=np.sum(points**2,axis=1)/d;tab=c.Table(vals,d,sub)
            x=np.random.default_rng(d).random((32,d));v=tab.point(x);exact=np.sum(x*x,axis=1)/d
            self.assertTrue(np.all(v>=exact-1e-12));self.assertTrue(np.all(v-exact<=1/(4*sub*sub)+1e-12))
    def test_scalar_action_cover_constant(self):
        for A in (2,4,8):
            for target in (F(1,13),F(1,7),F(1,4)):
                cap=F(1,4);vals=[(cap*k/A-target)**2 for k in range(A+1)]
                self.assertLessEqual(min(vals),2*cap*cap/(8*A*A))
    def test_simplex_action_cover_interior_and_face(self):
        for A in (2,4,8):
            cap=F(1,4)
            for target in ((F(1,13),F(1,11)),(F(1,7),cap-F(1,7)),(F(0),F(1,9))):
                vals=[sum((cap*F(k,A)-target[j])**2 for j,k in enumerate((i,l))) for i in range(A+1) for l in range(A-i+1)]
                self.assertLessEqual(min(vals),2*2*cap*cap/(8*A*A))
    def test_primitive_state_domain(self):
        for d,m in itertools.product((2,4,8),(1,2)):
            x=np.array(list(itertools.product((0.,1.),repeat=d)));cap=c.cap_points(x)
            for f in c.fractions_menu(m,2):
                a=c.I.point(cap[:,None]*np.array(f))
                for z,w in itertools.product((-1/32,1/32),((-1/64,1/64) if m==2 else (0.,))):
                    y=c.transition(c.I.point(x),a,z,w);self.assertGreater(y.lo.min(),0);self.assertLess(y.hi.max(),1)
    def test_primitive_joint_convexity_margin(self):
        rng=np.random.default_rng(62007)
        for d,m in itertools.product((2,4,8),(1,2)):
            x=rng.random((24,d));y=rng.random((24,d));u=rng.dirichlet(np.ones(m+1),24)[:,:m];v=rng.dirichlet(np.ones(m+1),24)[:,:m]
            a=c.cap_points(x)[:,None]*u;b=c.cap_points(y)[:,None]*v;theta=.375
            def fun(x,a):
                xx=c.I.point(x);aa=c.I.point(a)
                return (c.stage(xx,aa)+c.rat(c.B)*c.terminal(c.transition(xx,aa,0.,0.))).midpoint()
            lhs=fun(theta*x+(1-theta)*y,theta*a+(1-theta)*b)
            rhs=theta*fun(x,a)+(1-theta)*fun(y,b)-theta*(1-theta)*(float(F(71,64*d))*np.sum((x-y)**2,axis=1)+7/8*np.sum((a-b)**2,axis=1))
            self.assertTrue(np.all(lhs<=rhs+1e-11))
    def test_known_cost_support(self):
        for d,m in itertools.product((2,4,8),(1,2)):
            x=np.array(list(itertools.product((0.,1.),repeat=d)));cap=c.cap_points(x)
            for f in c.fractions_menu(m,2):
                val=c.stage(c.I.point(x),c.I.point(cap[:,None]*np.array(f)));self.assertLessEqual(val.hi.max(),float(F(103,64))+1e-12)
            self.assertLessEqual(c.terminal(c.I.point(x)).hi.max(),float(F(37,16))+1e-12)
    def test_one_date_reference_contains_optimized_original_value(self):
        ref,arr=c.reference(2,1,1,2,4,2)
        for first,last,points in c.grid(2,2):
            for j,x in enumerate(points):
                cap=c.cap_points(x[None,:])[0]
                def objective(a):return float(c.n.o.final_q(c.I.point(x[None,:]),c.I.point(np.array([a])),1).midpoint()[0])
                ans=minimize_scalar(objective,bounds=(0,cap),method='bounded',options={'xatol':1e-13})
                value=min(objective(0),objective(cap),float(ans.fun))
                self.assertLessEqual(arr['lower'][0,first+j],value+1e-10);self.assertGreaterEqual(arr['upper'][0,first+j],value-1e-10)
    def test_barycentric_actor_acquisition_and_simplex_feasibility(self):
        rng=np.random.default_rng(33);d=2;sub=4;N=25
        x=np.array(list(itertools.product(np.arange(5)/4,repeat=2)));cap=c.cap_points(x)
        pol=np.empty((2,N,2))
        for t in range(2):pol[t]=cap[:,None]*rng.dirichlet(np.ones(3),N)[:,:2]
        actor=c.Actor(pol,d,sub);states=rng.random((100,d))
        for t in range(2):
            a=actor.point(t,states);self.assertTrue(np.all(a>=0));self.assertTrue(np.all(a.sum(axis=1)<=c.cap_points(states)+1e-14))
            bound=actor.interval(t,c.I.point(states));self.assertTrue(np.all(a>=bound.lo) and np.all(a<=bound.hi))
    def test_actual_one_date_policy_bound_off_grid(self):
        ref,arr=c.reference(2,1,1,4,8,4);cert,actor=c.certificate(arr['policy'],arr['selected_upper'],arr['lower'],2,1,1,4,8,4)
        x=np.random.default_rng(88).random((12,2));actions=actor.point(0,x)
        for j,z in enumerate(x):
            cap=c.cap_points(z[None,:])[0]
            def obj(a):return float(c.n.o.final_q(c.I.point(z[None,:]),c.I.point(np.array([a])),1).midpoint()[0])
            sol=minimize_scalar(obj,bounds=(0,cap),method='bounded');star=min(sol.fun,obj(0),obj(cap));gap=obj(actions[j,0])-star
            self.assertLessEqual(gap,cert['initial_gap_upper']+1e-10)
    def test_two_control_full_reference_and_policy_shape(self):
        ref,arr=c.reference(2,2,2,2,2,2);cert,actor=c.certificate(arr['policy'],arr['selected_upper'],arr['lower'],2,2,2,2,2,2)
        self.assertEqual(arr['policy'].shape,(2,9,2));self.assertGreater(cert['initial_gap_upper'],0)
        self.assertTrue(np.all(arr['lower']<=arr['upper']))
    def test_coarse_actor_transfer_is_feasible(self):
        part=c.n.Partition(4,8,551);actions=np.repeat((part.capindex/4096)[None,:,None],2,axis=0)
        prop={'partition':part,'actions':actions};x=np.random.default_rng(62).random((50,4))
        for t in range(2):self.assertTrue(np.all(c.transferred_actions(prop,x,t).sum(axis=1)<=c.cap_points(x)))
    def test_quadrature_allowance_for_exact_quadratic(self):
        for q in (2,4,8):
            z=[F(-1,32)+F(2*j+1,32*q) for j in range(q)];mid=sum((a*a for a in z),F(0))/q
            exact=F(1,3072);bound=F(2,1)*F(1,1024)/(6*q*q)
            self.assertEqual(exact-mid,bound)
    def test_policy_error_is_not_just_node_bracket_width(self):
        ref,arr=c.reference(2,1,2,2,2,2);cert,_=c.certificate(arr['policy'],arr['selected_upper'],arr['lower'],2,1,2,2,2,2)
        node=float((c.I.point(arr['upper'][0])-c.I.point(arr['lower'][0])).hi.max())
        self.assertGreater(cert['initial_gap_upper'],node)
    def test_zero_actor_original_path_enclosure(self):
        actor=c.Actor(np.zeros((2,9,1)),2,2);x=c.I(np.array([[.2,.3]]),np.array([[.200001,.300001]]));z=[c.I.point(np.array([0.])),c.I.point(np.array([0.]))]
        val=c.path_cost(actor,x,z,[]);self.assertTrue(val.lo[0]>=0);self.assertLess(val.hi[0],float(c.support(2)))
    def test_family_union_bound_is_conservative(self):
        import math
        self.assertLess(8*512*math.exp(-16),.01)

if __name__=='__main__':unittest.main(verbosity=2)
