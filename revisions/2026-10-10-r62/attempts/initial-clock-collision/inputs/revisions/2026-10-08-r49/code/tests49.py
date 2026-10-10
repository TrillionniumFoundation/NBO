"""Exact identities and small independent checks; not timing observations."""
import itertools,math,tempfile,unittest
from pathlib import Path
import service49 as s
import direct49 as d
F=s.F

class Tests(unittest.TestCase):
    def test_constant_curvature_uniform(self):
        nodes=s.np.array(list(itertools.product(s.np.arange(9)/8,repeat=2)))
        axes,_=s.adaptive_axes(s.np.sum(nodes**2,axis=1),16,2)
        self.assertTrue(all(s.np.array_equal(a,s.np.arange(17)/16) for a in axes))
    def test_curvature_actually_can_adapt(self):
        nodes=s.np.array(list(itertools.product(s.np.arange(9)/8,repeat=2)))
        axes,_=s.adaptive_axes(nodes[:,0]**4+nodes[:,1]**2,16,2)
        self.assertFalse(s.np.array_equal(axes[0],s.np.arange(17)/16))
        self.assertEqual(len(axes[0]),17)
    def test_resource_bound_reconstruction(self):
        for T,p in itertools.product((2,3),(1,4)):
            j=s.rung(4,2,1,T,p,'compiled-witness');a,b,q=s.coefficients(2,T,p)
            computed=sum((s.BETA**t*F(r['component']) for t,r in enumerate(j['rows'])),F(0))+s.BETA**T*F(j['terminal_width'])
            self.assertEqual(computed,F(j['policy_bound_exact']))
            self.assertGreaterEqual(computed,a/4+b/2+q)
            self.assertLess(computed-(a/4+b/2+q),F(1,10**9))
    def test_dyadic_rounding_guarantee(self):
        for x in [F(7,3),F(1),F(19),F(63,2)]:
            n=1
            while n<x:n*=2
            self.assertGreaterEqual(n,x);self.assertLess(n,2*x)
    def test_product_allocation(self):
        for dd in (2,3,4):
            a,b,c=F(3),F(2),F(1);e=F(1,4);S=dd+2
            n=a*S/(dd*e);k=b*S/e;m=c*S/e
            self.assertEqual(a/n+b/k+c/m,e)
            base=n**dd*k*m
            for f in (F(1,2),F(3,4),F(5,4)):
                x=a/n*f;y=(e-x)/2
                self.assertGreaterEqual((a/x)**dd*(b/y)*(c/y),base)
    def test_arbitrary_grid_witness_identity(self):
        model=s.Model([[0,.125,.5,1],[0,.25,1]],[float((7*i)%11)/16 for i in range(12)],'witness',F(3,2))
        for x in itertools.product((F(1,16),F(3,8),F(15,16)),repeat=2):
            value,index=model.exact(x);box=model.point([list(map(float,x))]);act,_=model.actor(s.I.point([list(map(float,x))]),s.np.arange(model.S))
            self.assertLessEqual(F(float(box.lo[0])),value);self.assertGreaterEqual(F(float(box.hi[0])),value);self.assertEqual(act.lo[0],index);self.assertEqual(act.hi[0],index)
    def test_capacity_every_dimension(self):
        for dd in (2,3,4):
            nodes=s.np.array(list(itertools.product((0.,.5,1.),repeat=dd)));lo=s.cap(s.I.point(nodes)).lo
            for x,c in zip(nodes,lo):self.assertLessEqual(F(float(c)),F(1,8)+sum(map(lambda v:F(float(v)),x))/(8*dd))
    def test_family_budget(self):
        lower=sum((F(13)**k/math.factorial(k) for k in range(50)),F(0));self.assertGreater(lower,4*300/F(1,100))
    def test_fee_accounts_distinct(self):
        a=d.fee_account(F(-2),F(3));self.assertEqual(a['fee_certifying_both_not_profitable'],'3');self.assertEqual(a['fee_removing_certified_profitability'],'0')
        a=d.fee_account(F(1),F(3));self.assertEqual(a['absolute_gain_interval'],['1','3'])
    def test_net_cost_selection_uniform_prices(self):
        low=[F(-1,5),F(-1,10),F(0)];high=[F(1,10),F(1,5),F(0)];bits=[4,8,16]
        for price in (F(0),F(1,100),F(1)):
            u=[x+price*b for x,b in zip(high,bits)];l=[x+price*b for x,b in zip(low,bits)];i=min(range(3),key=lambda j:(u[j],bits[j]));gap=u[i]-min(l)
            for truth in itertools.product(*[(a,b) for a,b in zip(low,high)]):
                net=[x+price*b for x,b in zip(truth,bits)];self.assertLessEqual(net[i]-min(net),gap)
    def test_model_roundtrip(self):
        for method in s.METHODS:
            j=s.rung(4,2,1,2,1,method)
            for m in j['models']:
                model=s.Model.load(m);self.assertEqual(model.payload(),m)
    def test_direct_modern_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'checkpoint.json';s.save(path,s.rung(4,2,1,2,1,'compiled-witness'))
            p=d.Policy(path);x=s.I.point([[.125,.875]]);a=p.action(0,x,8);self.assertLessEqual(a.hi[0],s.cap(x).hi[0]);self.assertGreaterEqual(a.lo[0],0)
    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'record.json';s.save(p,{'x':1})
            with self.assertRaises(FileExistsError):s.save(p,{'x':2})
    def test_invalid_resource_refused(self):
        with self.assertRaises(ValueError):s.rung(3,2,1,2,1,'compiled-witness')
    def test_support_contains_cost(self):
        for T,p in itertools.product((2,3),(1,4)):
            a,b=d.inherited.support(T,p);self.assertEqual(a,-b);self.assertGreater(b,0)

if __name__=='__main__':unittest.main()
