"""Exact arithmetic and adversarial development tests; no catalogue execution."""
import itertools,json,unittest
from fractions import Fraction as F
import numpy as np
from common import *
from constrained import *
from scalar import Actor,cost

class Checks(unittest.TestCase):
    def example(self,d=2,N=2,L=F(3,2)):
        y=[F((i*7)%13-7,8) for i in range((N+1)**d)]
        owners,counts=tensor_compile(list(map(float,y)),d,N,L)
        return Model({'d':d,'N':N,'method':'witness','labels':list(map(float,y)),
            'actions':[.25]*len(y),'L':float(L),'owners':owners.tolist()}),y
    def test_tensor_closure_exact_2d(self):
        m,y=self.example()
        for i,x in enumerate(m.x):
            vals=[y[j]+F(m.L)*sum(abs(F(float(a))-F(float(b))) for a,b in zip(x,z)) for j,z in enumerate(m.x)]
            self.assertEqual(vals[m.owners[i]],min(vals))
    def test_tensor_closure_exact_3d(self):
        m,y=self.example(3)
        for i,x in enumerate(m.x):
            vals=[y[j]+F(m.L)*sum(abs(F(float(a))-F(float(b))) for a,b in zip(x,z)) for j,z in enumerate(m.x)]
            self.assertEqual(vals[m.owners[i]],min(vals))
    def test_offgrid_witness_identity(self):
        for d in (2,3):
            m,y=self.example(d)
            for x in np.random.default_rng(31+d).uniform(size=(30,d)):
                ids=m.owners[m.corner_ids(x[None,:])[1][0]]
                vals=[y[j]+F(m.L)*sum(abs(F(float(a))-F(float(b))) for a,b in zip(x,z)) for j,z in enumerate(m.x)]
                self.assertEqual(min(vals[j] for j in ids),min(vals))
                for backend in ('flat-min-plus','compiled-min-plus','compiled-ReLU'):
                    v=m.point(x[None,:],backend);self.assertLessEqual(F(float(v.lo[0])),min(vals));self.assertGreaterEqual(F(float(v.hi[0])),min(vals))
    def test_zero_modulus_and_ties(self):
        m,y=self.example(2,L=F(0));self.assertTrue(np.all(m.owners==min(range(len(y)),key=lambda j:(y[j],j))))
    def test_robust_integer_repair(self):
        m,_=self.example()
        m.actions[:]=.5
        for bits in (12,20):
            q=np.array([[0.,0.],[1.,1.],[1/8,7/8],[.5,.5]])
            a,st=m.deploy(q,bits)
            for x,u in zip(q,a):
                indices=[min(2**bits-1,int(F(float(v))*2**bits)) for v in x]
                lower=F(1,4)+F(sum(indices),4*2*2**bits)
                self.assertLessEqual(F(float(u)),lower)
                self.assertGreaterEqual(F(float(u)),0)
    def test_ambiguous_acquisition_not_discarded(self):
        m,_=self.example();v,st=m.interval_action(I(np.array([[.5-1e-12,.25]]),np.array([[.5+1e-12,.25]])),12)
        self.assertEqual(st['acquisition_ambiguities'],1);self.assertEqual(v.lo[0],0);self.assertEqual(v.hi[0],.5)
    def test_exact_state_invariance(self):
        self.assertEqual(F(1,16)-F(1,16),0)
        self.assertEqual(F(1,16)+F(1,2)+F(1,8)+F(1,8)+F(1,16),F(7,8))
    def test_feasible_net_cover(self):
        for d in (2,3):
            for x in grid(d,2):
                b=F(1,4)+sum(F(float(v)) for v in x)/(4*d)
                aa=[F(int((b*j/2)*2**20),2**20) for j in range(3)]
                self.assertTrue(all(0<=a<=b for a in aa))
                for a in [b*j/37 for j in range(38)]:self.assertLessEqual(min(abs(a-v) for v in aa),F(1,8)+F(1,2**20))
    def test_one_date_query_containment(self):
        for method in METHODS:
            p=rung(2,1,.5,2,method)
            m=Model(p['models'][0]);e=F(p['rows'][0]['query_error'])
            for i,x in enumerate(m.x):
                a=F(float(m.actions[i]));xx=list(map(lambda z:F(float(z)),x))
                base=[F(1,16)+xx[j]/2+xx[(j+1)%2]**2/8+a/4 for j in range(2)]
                # Common additive innovation cancels in the dispersion term.
                eg=(1-sum(base)/2)**2+F(1,3*256)+sum((base[j]-base[(j+1)%2])**2 for j in range(2))/16
                c=sum((v-F(1,2))**2 for v in xx)/16+F(1,2)*a*a/2
                self.assertLessEqual(abs(F(float(m.y[i]))-(c+BETA*eg)),e)
    def test_continuous_midpoint_error(self):
        # Uniform [-1,1]: E |Z-mid-bin| = 1/(2M), not 1/M or zero.
        for M in (4,8,16):
            self.assertEqual(M*F(1,M)**2/F(2),F(1,2*M))
    def test_fvi_interpolates_nodes(self):
        p=rung(2,1,.5,2,'multilinear-fvi');m=Model(p['models'][0]);v=m.point(m.x)
        self.assertTrue(np.all(v.lo<=m.y));self.assertTrue(np.all(v.hi>=m.y))
    def test_integer_moments(self):
        a=np.array([-2,1,4],dtype=np.int64);m=moments(a)
        self.assertEqual(F(m['mean_exact']),F(1,2**32));self.assertEqual(F(m['variance_exact']),F(9,2**64))
    def test_confidence_zero_is_not_exact_equality(self):
        a=np.zeros(1024,dtype=np.int64);q=confidence(a,a,F(2),30)
        self.assertLess(q['lower'],0);self.assertGreater(q['upper'],0);self.assertEqual(q['sign'],'sign-unresolved')
    def test_outward_dyadic_quantization(self):
        q=I(np.array([-.1,.123456789]),np.array([.2,.1234567891]));lo,hi=quantize_interval(q)
        for j in range(2):self.assertLessEqual(F(int(lo[j]),2**32),F(float(q.lo[j])));self.assertGreaterEqual(F(int(hi[j]),2**32),F(float(q.hi[j])))
    def test_scalar_exact_path(self):
        p=json.loads((R.parent/'2026-10-07-r46/results/services/cone-witness-T2-p1-r0/checkpoint-N16.json').read_text())
        x=F(1,2);z=[F(0),F(1,2)];true=F(0)
        for t in range(2):
            a=Actor(p,t)(I.point(np.array([float(x)])));u=F(float(a.lo[0]));self.assertEqual(a.lo[0],a.hi[0])
            true+=BETA**t*((x-F(11,16))**2+u*u+4*u**4+2*max(F(3,8)-x,0)**2)
            x=F(1,32)+F(11,16)*x+F(1,16)*x*(1-x)+u+z[t]/32
        true+=BETA**2*(2*(x-F(11,16))**2+2*max(F(3,8)-x,0)**2)
        v,_=cost(p,I.point(np.array([.5])),[I.point(np.array([.5])),I.point(np.array([.75]))])
        self.assertLessEqual(F(float(v.lo[0])),true);self.assertGreaterEqual(F(float(v.hi[0])),true)

if __name__=='__main__':unittest.main(verbosity=2)
