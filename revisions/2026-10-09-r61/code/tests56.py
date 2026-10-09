"""New R56 exact-action, stability, error-account and stopping regressions."""
from pathlib import Path
from fractions import Fraction as F
import itertools,json,unittest
import numpy as np
import algebraic56 as a
import neural55 as n
import audit56 as audit
R=Path(__file__).resolve().parents[1]
class Revisions(unittest.TestCase):
    def params(self,d=2):
        return dict(c=.25,v=np.arange(d)/8,W=np.array([[(-1)**(i+j)*(i+1)/8 for j in range(3)] for i in range(d)]),b=np.array([-.25,0,.125]),u=np.array([1.,-3.,.5]))
    def compare(self,x,p,cap=32,Q=128):
        z=a.minimize_lattice(x,p,cap,Q);value=a.reduce_critic(x,p)[-1];exact=min(range(cap+1),key=lambda k:(value(F(k,Q)),k))
        self.assertEqual(z['index'],exact);self.assertEqual(z['value_exact'],str(value(F(exact,Q))));self.assertLessEqual(len(z['candidate_indices']),22*len(p['u'])+13)
    def test_exact_hinge_branches(self):
        for z in (F(-1),F(-1,4),F(0),F(1,4),F(1)):
            for r in (F(0),F(1,4)):
                expected=max(F(0),z) if r==0 else (max(F(0),z+r)**2-max(F(0),z-r)**2)/(4*r)
                self.assertEqual(a.hinge(z,r),expected)
    def test_nonconvex_fitted_action(self):
        for d in (2,4,8):self.compare([F(i+1,d+2) for i in range(d)],self.params(d))
    def test_zero_innovation_projection(self):
        p=self.params();p['W']=np.array([[1.,-1.,2.],[1.,-1.,2.]])
        self.compare([F(1,4),F(3,4)],p)
    def test_zero_action_cap(self):self.compare([F(1,4),F(1,4)],self.params(),0)
    def test_exact_tie_selects_first(self):
        p=self.params();p['u']=np.zeros(3);p['v']=np.array([-4209/16384,0.]);z=a.minimize_lattice([F(0),F(0)],p,32,128);value=a.reduce_critic([F(0),F(0)],p)[-1];self.assertEqual(value(F(7,128)),value(F(8,128)));self.assertEqual(z['index'],7)
    def test_saved_neural_critics(self):
        records=[]
        for d,T in ((2,2),(4,4),(8,6)):
            file=R/'results55-tube/services'/f'relu-d{d}-T{T}-q9_10-r0/stage0-models.json';m=json.loads(file.read_text());part=n.Partition(d,32);x=part.centers[0];params=m['critics'][1]['params'];cap=int(part.capindex[0])
            z=a.minimize_lattice(x,params,cap);value=a.reduce_critic(x,params)[-1];brute=min(range(cap+1),key=lambda k:(value(F(k,4096)),k));self.assertEqual(z['index'],brute)
            old=int(m['proposals'][0][0]);self.assertLessEqual(F(z['value_exact']),value(F(old,4096)))
            records.append(dict(d=d,T=T,source=str(file.relative_to(R)),source_sha256=audit.digest(file),original_proposal=old,original_reduced_value_exact=str(value(F(old,4096))),**z))
        audit.save(R/'audit/ALGEBRAIC_REGRESSION56.json',dict(status='passed',fixtures=records,new_economic_observations=0,scope='Three saved critics, one declared acquired-cell center each; exhaustive rational lattice comparison, not new economic-policy evaluation'))
    def test_reference_jacobian_contraction(self):
        for d in (2,4,8):
            for x in itertools.product((F(0),F(1)),repeat=d):
                for j in range(d):self.assertLessEqual(F(1,2)+(1-x[(j+1)%d])/16+F(1,8)-x[j]/16,F(11,16))
    def test_dimension_uniform_geometric_bound(self):
        for r in range(31):
            c=F(165,256);bound=F(15,2)*sum(c**j for j in range(r))+10*c**r;self.assertLessEqual(bound,F(1920,91))
    def test_refinement_ledger_is_exact(self):
        L0,L1,C,U1,U0=map(F,(-7,-4,-2,-1,0));self.assertEqual(U1-L1,(U1-C)+(C-L1));self.assertEqual((U0-L0)-(U1-L1),(U0-U1)+(L1-L0))
    def test_first_attainment_and_fee_event(self):
        uppers=[F(1,3),F(1,9),F(-1,17),F(-1,8)];first=next(i for i,x in enumerate(uppers) if x<=0);self.assertEqual(first,2)
        lo,hi=F(1,10),F(1,5)
        for tau,lam,W in itertools.product((F(0),F(1,100)),(F(0),F(1,100)),(F(0),F(1))):self.assertLessEqual(lo-tau-lam*W,hi-tau-lam*W)
    def test_exact_endpoint_moments(self):
        _,(mu,sq,var)=audit.exact_moments(np.array([.125,.25,.5]));self.assertEqual(mu,F(7,24));self.assertEqual(sq,F(7,64));self.assertEqual(var,F(7,192))
    def test_joint_family_bound(self):
        import math
        lower=sum((F(14)**j/math.factorial(j) for j in range(80)),F(0));self.assertGreater(lower,4*2048/F(1,100));self.assertLess(F(2*27*8)/lower,F(1,200));self.assertEqual(F(1,100)*2+F(1,200),F(1,40))
if __name__=='__main__':unittest.main(verbosity=2)
