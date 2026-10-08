"""Independent exact examples and implementation regressions for R47."""
import itertools,math,unittest
from fractions import Fraction as F
import numpy as np
import direct as d
import constrained as z
import deployment as a
I=z.I

class Tests(unittest.TestCase):
    def test_family(self):self.assertEqual(len(d.catalogue())*len(d.LAWS)*3,120)
    def test_log_bound(self):
        self.assertGreater(sum((F(11)**j/math.factorial(j) for j in range(41)),F(0)),48000)
    def test_moments_enclose_exact(self):
        x=np.array([-.5,.125,.25,1.]);m=d.moments(x,-1,1)
        exact=sum(map(F,x))/len(x);v=sum((F(t)-exact)**2 for t in x)/(len(x)-1)
        self.assertLessEqual(F(m['mean_lo']),exact);self.assertGreaterEqual(F(m['mean_hi']),exact)
        self.assertGreaterEqual(F(m['variance_upper']),v)
    def test_zero_variance(self):
        m=d.moments(np.full(64,.125),0,1);self.assertGreaterEqual(F(m['variance_upper']),0)
        lo,hi=d.interval_from_stats(m,m,0,1);self.assertLess(lo,F(1,8));self.assertGreater(hi,F(1,8))
    def test_interval_classification(self):
        self.assertEqual(d.classify(F(-1,10000),F(1,10000))['sign'],'unresolved')
        self.assertTrue(d.classify(F(-1,10000),F(1,10000))['within_margin'])
        self.assertFalse(d.classify(F(-1),F(1))['within_margin'])
    def test_actor_boundary_hull(self):
        act=d.Actor({'kind':'nearest-node','N':2,'node_actions':[0,.25,0]})
        v=act.evaluate(I(np.array([.24]),np.array([.76])))
        self.assertEqual(float(v.lo[0]),0);self.assertEqual(float(v.hi[0]),.25)
    def test_actor_rational_cut(self):
        act=d.Actor({'kind':'cone-witness','cuts':['0','1/3','1'],'owners':[0,1],'node_actions':[0,.25]})
        l,h=d.c.enclosure(F(1,3));v=act.evaluate(I(np.array([l]),np.array([h])))
        self.assertEqual(float(v.lo[0]),0);self.assertEqual(float(v.hi[0]),.25)
    def test_reject_invalid_state(self):
        act=d.Actor({'kind':'nearest-node','N':1,'node_actions':[0,.25]})
        with self.assertRaises(ValueError):act.evaluate(I(np.array([-.1]),np.array([0.])))
    def test_exact_telescoping(self):
        beta=F(3,4);values=[[F(1,3),F(4,5)],[F(-1,2),F(2,3)],[F(4,3),F(7,5)]]
        costs=[];scores=[]
        for shocks in itertools.product((0,1),repeat=2):
            x=0;score=values[0][x];cost=F(0)
            for t,shock in enumerate(shocks):
                action=(x+t)%2
                continuation=sum(values[t+1])/2
                stage=F(x+2*action+t,7)
                score+=beta**t*(stage+beta*continuation-values[t][x]);cost+=beta**t*stage
                x=(action+shock)%2
            terminal=F(x+1,2);cost+=beta**2*terminal;score+=beta**2*(terminal-values[2][x])
            costs.append(cost);scores.append(score)
        self.assertEqual(sum(costs),sum(scores))
    def test_min_relu_identity(self):
        for x,y in itertools.product([F(-5),F(-1,3),F(0),F(7,9)],repeat=2):
            self.assertEqual(x-max(x-y,0),min(x,y))
    def test_state_modulus_vertices(self):
        for x,y in itertools.product([F(0),F(1,4),F(1,2),F(1)],repeat=2):
            col1=F(1,2)+F(1,16)*(1-y)+F(1,8)-y/16
            col2=F(1,2)+F(1,16)*(1-x)+F(1,8)-x/16
            self.assertLessEqual(max(col1,col2),z.FX)
    def test_cost_gradient_bounds(self):
        for x,y in itertools.product([F(j,8) for j in range(9)],repeat=2):
            short=max(F(1,2)-x-y,0)
            for scale,bound in [(1,z.CX),(2,z.LG)]:
                derivatives=[2*scale*(x-F(5,8))+(x-y)/2-4*short,
                             2*scale*(y-F(5,8))+(y-x)/2-4*short]
                self.assertLessEqual(max(map(abs,derivatives)),bound)
    def test_invariance_corners(self):
        for x,y in itertools.product([0.,1.],repeat=2):
            cap=1/8+(x+y)/16
            for action,shock in itertools.product([0.,cap],[-1/32,1/32]):
                v=z.transition(I.point(np.array([[x,y]])),I.point(np.array([action])),shock)
                self.assertTrue(np.all(v.lo>=0) and np.all(v.hi<=1))
    def test_repair_displacement(self):
        points=list(itertools.product([F(0),F(1,2),F(1)],repeat=2))
        cap=lambda x:F(1,8)+(x[0]+x[1])/16
        for node,x in itertools.product(points,repeat=2):
            original=cap(node);repaired=min(original,cap(x))
            self.assertLessEqual(original-repaired,z.KA*sum(abs(v-w) for v,w in zip(node,x)))
    def test_robust_box_feasibility(self):
        eta=F(1,256);q=F(1,4096)
        for node in itertools.product([F(0),F(1,2),F(1)],repeat=2):
            lower=[max(0,x-eta) for x in node];caplo=F(1,8)+sum(lower)/16
            executed=(caplo//q)*q
            for true in itertools.product(*[(max(0,x-eta),min(1,x+eta)) for x in node]):
                self.assertLessEqual(executed,F(1,8)+sum(true)/16)
    def test_midpoint_continuous_remainder(self):
        s=F(1,32)
        for M in (1,2,4,8):
            approx=sum(abs(F(2*j+1-M,32*M)) for j in range(M))/M
            self.assertLessEqual(abs(approx-s/2),F(1,64*M))
    def test_bilinear_exact_value(self):
        nodes=np.array(list(itertools.product(np.arange(3)/2,repeat=2)))
        vals=nodes[:,0]*nodes[:,1]+nodes[:,0];m=z.Model(2,vals,'bilinear-fvi')
        pts=np.array([[.125,.25],[.375,.625],[.75,.5]]);value=m.point(pts)
        exact=pts[:,0]*pts[:,1]+pts[:,0]
        self.assertTrue(np.all(value.lo<=exact) and np.all(exact<=value.hi))
    def test_cell_corner_allowance(self):
        nodes=np.array(list(itertools.product(np.arange(3)/2,repeat=2)))
        vals=nodes[:,0]*nodes[:,1]+nodes[:,0];m=z.Model(2,vals,'bilinear-fvi')
        D,_=z.nearest_excess(m,F(2))
        for x,y in itertools.product([F(j,16) for j in range(17)],repeat=2):
            i=min(2,int(2*x+F(1,2)));j=min(2,int(2*y+F(1,2)))
            value=F(i,2)*F(j,2)+F(i,2)+2*(abs(x-F(i,2))+abs(y-F(j,2)))-(x*y+x)
            self.assertLessEqual(value,D)
    def test_unexecuted_small_fixture(self):
        for method in z.METHODS:
            payload,counts=z.rung(2,1,1,method)
            expected=sum((z.BETA**i*F(r['component']) for i,r in enumerate(payload['rows'])),F(0))
            expected+=z.BETA*F(payload['terminal_width'])
            self.assertEqual(expected,F(payload['policy_bound_exact']))
            self.assertEqual(counts['bellman_queries'],27)
    def test_float_selector_bound(self):
        N=2;nodes=np.array(list(itertools.product(np.arange(N+1)/N,repeat=2)))
        labels=np.arange(9)/64;L=F(11,3);m=z.Model(N,labels,'feasible-cone-witness',L)
        for x,y in itertools.product([F(j,16) for j in range(17)],repeat=2):
            scores=labels+float(L)*np.sum(np.abs(np.array([float(x),float(y)])-nodes),axis=1)
            idx=int(np.argmin(scores));exact=[F(float(v))+L*(abs(x-F(float(n[0])))+abs(y-F(float(n[1])))) for n,v in zip(nodes,labels)]
            self.assertLessEqual(exact[idx]-min(exact),2*a.leaf_error(labels,L,2))

if __name__=='__main__':unittest.main(verbosity=2)
