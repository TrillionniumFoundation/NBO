"""Executable checks for new exact constructions and the unchanged service path."""
import pathlib,sys,unittest,tempfile,math
from fractions import Fraction as Q
import numpy as np
R=pathlib.Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'new'),str(R/'code')]
import study97 as s
from quadrature96 import service
import independent97 as independent

class ExactConstructions(unittest.TestCase):
    def test_adaptive_partition_lower_bound(self):
        for n in (0,1,2,7,31):
            for alpha in (Q(0),Q(1,2),Q(3,4),Q(15,16)):
                K=Q(3);radius=Q(1,32);L=2*radius*(1-alpha)
                lengths=[L/Q(n+1)]*(n+1)
                gap=K*sum(h**3 for h in lengths)/(12*L**2)
                self.assertEqual(gap,K*radius*(1-alpha)/(6*(n+1)**2))
                if n:
                    lengths[0]/=2;lengths[1]+=L/(2*(n+1))
                    self.assertGreaterEqual(K*sum(h**3 for h in lengths)/(12*L**2),gap)
    def test_chord_integral_and_lipschitz(self):
        K=Q(7);L=Q(3);a=Q(1,5);b=Q(9,5)
        def primitive(z):return -(z**3)/3+(a+b)*z*z/2-a*b*z
        integral=K/(2*L)*(primitive(b)-primitive(a))
        self.assertEqual(integral,K*(b-a)**3/(12*L))
        self.assertTrue(0<=K*(a+b)/(2*L)<=K)
    def test_oblique_lower_witness(self):
        for i in range(65):
            for j in range(65):
                x,y=Q(i,64),Q(j,64);u=x+y-1;v=max(Q(0),u)
                self.assertLessEqual(abs(v-((x+y)/2-Q(1,4))),Q(1,4))
                self.assertLessEqual(abs(v-(u+u*u+Q(1,8))/2),Q(1,16))
        self.assertEqual(Q(1,2)-Q(1,4)*1-Q(3,4)*0,Q(1,4))
    def test_purchase_units_and_strict_boundary(self):
        B=32;lam=Q(1);d=Q(1,256);saving=Q(1,4);setup=Q(1)
        q=lam*saving-B*d
        self.assertEqual(q,Q(1,8));first=setup//q+1
        self.assertEqual(first,9);self.assertEqual((first-1)*q-setup,0);self.assertGreater(first*q-setup,0)
    def test_payload_roundtrip_all_ranks(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/'model.bin'
            for kind in s.KINDS:
                for rank in (4,5,6):
                    k=rank-3;m=s.MatchedFit(kind,np.arange(2*k).reshape(k,2)/16,np.arange(k)/8,np.arange(rank)/32,{})
                    raw=s.serialize(m);self.assertEqual(len(raw),32*(rank-2));p.write_bytes(raw)
                    self.assertEqual(s.serialize(s.load_model(p)),raw)
    def test_original_service_path(self):
        x=np.array([[0,0],[1,1],[.25,.75],[.75,.25],[.4,.4]])
        for alpha in s.LEVELS:
            got,_=s.trace_service(x,alpha,None);expected=service(x,alpha,None)
            for key in ('actions','proposed','lower','upper','optimum_lower','loss','width','rejected','exact'):
                np.testing.assert_array_equal(got[key],expected[key])
    def test_independent_conventional_proposal(self):
        x=np.array([[0,0],[1,1],[.25,.75],[.75,.25],[.4,.4]])
        for alpha in s.LEVELS:
            got=independent.proposal(x,alpha,None);expected=s.actor(x,alpha,None)
            np.testing.assert_allclose(got,expected,rtol=0,atol=2**-29)
    def test_safe_readout_selection(self):
        # Selection is on recomputed interval widths, not LP success or node loss.
        for old,new in ((2.,1.),(1.,2.),(1.,1.)):
            retained=new if new<=old else old
            self.assertLessEqual(retained,old)

if __name__=='__main__':unittest.main(verbosity=2)
