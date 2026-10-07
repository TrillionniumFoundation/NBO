"""Exact arithmetic tests; finite checks supplement, not replace, the proof."""
from fractions import Fraction as F
import itertools,json,random,unittest
from pathlib import Path
import numpy as np
from constructive import PWL,I,enclosure,rat_i,base_state,stage,terminal

class ConstructiveTests(unittest.TestCase):
    def assert_contains(self,iv,v):
        self.assertLessEqual(F(float(iv.lo)),v)
        self.assertGreaterEqual(F(float(iv.hi)),v)

    def test_rational_enclosure(self):
        for q in (F(1,3),F(-7,11),F(0),F(1,2**40)):
            lo,hi=enclosure(q);self.assertLessEqual(F(lo),q);self.assertGreaterEqual(F(hi),q)

    def test_noisy_neural_definition(self):
        k=[F(j,8) for j in range(9)]
        v=[F((j-3)**2,64)+F((-1)**j,128) for j in range(9)]
        net=PWL.from_labels(k,v,F(2),'min-plus-ReLU')
        for x in (F(j,97) for j in range(98)):
            self.assertEqual(net.exact(x),min(y+2*abs(x-z) for z,y in zip(k,v)))
        self.assertLessEqual(net.L,2)

    def test_metric_closure_with_inconsistent_labels(self):
        k=[F(0),F(1,2),F(1)];v=[F(0),F(10),F(-2)]
        f=PWL.from_labels(k,v,F(1),'min-plus-ReLU')
        self.assertLessEqual(f.L,1)
        for j in range(101):
            x=F(j,100);self.assertEqual(f.exact(x),min(y+abs(x-z) for z,y in zip(k,v)))

    def test_zero_lipschitz(self):
        f=PWL.from_labels([0,F(1,2),1],[3,-1,4],F(0),'min-plus-ReLU')
        self.assertEqual(f.L,0);self.assertEqual(f.exact(F(3,7)),F(-1))

    def test_shift_invariance(self):
        k=[F(j,4) for j in range(5)];v=[F(j*j,16) for j in range(5)]
        f=PWL.from_labels(k,v,F(3),'min-plus-ReLU')
        g=PWL.from_labels(k,[y-F(7,3) for y in v],F(3),'min-plus-ReLU')
        for j in range(33):self.assertEqual(g.exact(F(j,32)),f.exact(F(j,32))-F(7,3))

    def test_label_nonexpansiveness(self):
        k=[F(j,4) for j in range(5)];v=[F(j*j,16) for j in range(5)]
        f=PWL.from_labels(k,v,F(3),'min-plus-ReLU')
        g=PWL.from_labels(k,[y+F((-1)**j,100) for j,y in enumerate(v)],F(3),'min-plus-ReLU')
        for j in range(33):self.assertLessEqual(abs(g.exact(F(j,32))-f.exact(F(j,32))),F(1,100))

    def test_exact_integral_and_interval(self):
        k=[F(j,4) for j in range(5)];v=[F(j*j,16) for j in range(5)]
        for method in ('min-plus-ReLU','piecewise-linear-spline'):
            f=PWL.from_labels(k,v,F(3),method)
            for j in range(1,32):
                b=F(j,32);exact=(f.exact(b+F(1,32),True)-f.exact(b-F(1,32),True))*16
                self.assert_contains(f.uniform(float(b)),exact)
            for j in range(65):self.assert_contains(f.evaluate(float(F(j,64))),f.exact(F(j,64)))

    def test_non_dyadic_knots(self):
        f=PWL([0,F(1,3),F(2,3),1],[0,1,-1,0])
        for b in (F(float(F(1,3))),F(float(F(2,3))),F(1,2)):
            self.assert_contains(f.point(float(b)),f.exact(b))
            self.assert_contains(f.point(float(b),True),f.exact(b,True))

    def test_interval_state_input(self):
        f=PWL.from_labels([0,F(1,2),1],[0,1,0],F(3),'min-plus-ReLU')
        iv=I(.49,.51);out=f.evaluate(iv)
        for x in (F(49,100),F(1,2),F(51,100)):self.assert_contains(out,f.exact(x))
        out=f.uniform(iv)
        for x in (F(49,100),F(1,2),F(51,100)):
            exact=(f.exact(x+F(1,32),True)-f.exact(x-F(1,32),True))*16
            self.assert_contains(out,exact)

    def test_primitive_domain(self):
        # Derivative 3/4-x/8 is positive; endpoints prove whole-domain invariance.
        self.assertEqual(F(1,32)-F(1,32),0)
        self.assertEqual(F(1,32)+F(11,16)+F(1,4)+F(1,32),1)
        for x,a in itertools.product((F(0),F(1,2),F(1)),(F(0),F(1,4))):
            exact=F(1,32)+F(11,16)*x+F(1,16)*x*(1-x)+a
            self.assert_contains(base_state(I.point(float(x)),I.point(float(a))),exact)

    def test_multidimensional_residual_and_actor(self):
        e=F(1,100);L=F(2);La=F(2)
        for d in (1,2,3):
            nodes=list(itertools.product((F(0),F(1,2),F(1)),repeat=d));actions=(F(0),F(1,8),F(1,4))
            def h(x):return sum(z*z for z in x)/(4*d)
            def astar(x):return F(1,8)+sum(x)/(32*d)
            def q(x,a):return h(x)+2*(a-astar(x))**2
            labels=[];actors=[]
            for j,z in enumerate(nodes):
                values=[q(z,a)+((-1)**(j+k))*e for k,a in enumerate(actions)]
                idx=min(range(len(actions)),key=values.__getitem__);labels.append(values[idx]);actors.append(actions[idx])
            hx=F(d,4);ha=F(1,16)
            for x in itertools.product((F(1,8),F(3,8),F(7,8)),repeat=d):
                dist=lambda z:sum(abs(a-b) for a,b in zip(x,z))
                fit=min(y+L*dist(z) for z,y in zip(nodes,labels));res=fit-h(x)
                self.assertGreaterEqual(res,-e);self.assertLessEqual(res,La*ha+e+2*L*hx)
                j=min(range(len(nodes)),key=lambda i:dist(nodes[i]))
                self.assertLessEqual(q(x,actors[j])-h(x),La*ha+2*e+2*L*hx)

    def test_loss_budget(self):
        beta=F(15,16);T=5;eps=F(1,100);H=sum(beta**t for t in range(T+1));s=eps/H
        nonterminal=2*(s/8)+4*(s/8)+4*(s/16)
        terminal_width=2*(s/4)+2*(s/4)
        self.assertEqual(sum(beta**t*nonterminal for t in range(T))+beta**T*terminal_width,eps)

    def test_grid_only_residual_is_not_certificate(self):
        # A 1-Lipschitz tent is zero on a mesh and strictly positive off it.
        nodes=[F(j,4) for j in range(5)]
        residual=lambda x:min(abs(x-z) for z in nodes)
        self.assertTrue(all(residual(z)==0 for z in nodes))
        self.assertEqual(residual(F(1,8)),F(1,8))
        for x in (F(j,64) for j in range(65)):
            self.assertLessEqual(residual(x),F(1,8))

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ConstructiveTests))
    root=Path(__file__).resolve().parents[1];(root/'audit').mkdir(exist_ok=True)
    (root/'audit/NEW_TESTS.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'successful':result.wasSuccessful(),'scope':'exact arithmetic regression tests, not a formal proof'},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
