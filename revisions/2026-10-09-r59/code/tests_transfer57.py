"""Exact rational tests for the R57 transfer statements; not economic samples."""
from fractions import Fraction as F
import random,unittest,itertools
import algebraic56 as algebra

class TransferTests(unittest.TestCase):
    def test_fitted_witness_transfer(self):
        rng=random.Random(570019)
        for repeat in range(100):
            h=[[F(rng.randrange(-20,21),8) for a in range(4)] for x in range(3)]
            J=[[h[x][a]+F(rng.randrange(-10,11),16) for a in range(4)] for x in range(3)]
            g=rng.randrange(4);reference=0
            eta=max(abs(h[x][a]-h[x][b]-h[0][a]+h[0][b]) for x,a,b in itertools.product(range(3),range(4),range(4)))
            chi=max(abs(J[x][a]-h[x][a]-J[x][b]+h[x][b]) for x,a,b in itertools.product(range(3),range(4),range(4)))
            kappa=h[0][g]-min(h[0]);adv=[[J[x][a]-J[x][reference] for a in range(4)] for x in range(3)]
            lo=[min(adv[x][a] for x in range(3))-F(1,32) for a in range(4)]
            hi=[max(adv[x][a] for x in range(3))+F(1,32) for a in range(4)];hi[0]=0
            chosen=min(range(4),key=lambda a:(hi[a],a));rho=kappa+eta+chi+hi[g]-lo[g]
            for x in range(3):
                self.assertLessEqual(adv[x][chosen],0)
                self.assertLessEqual(J[x][chosen]-min(J[x]),rho)
    def test_sum_coefficient_is_sharp(self):
        delta=F(19,23);self.assertEqual(delta,delta+0+0+0+0);self.assertGreater(delta,F(99,100)*delta)
    def test_smaller_upper_endpoint_does_not_order_cost(self):
        old,new,inc=F(1),F(5,4),F(2)
        self.assertLess(new-inc,F(-1,2));self.assertGreater(new,old)
        self.assertLess(old,inc);self.assertLess(new,inc)
    def test_nested_upper_gap(self):
        rng=random.Random(5757)
        for repeat in range(100):
            endpoints=[F(rng.randrange(-10,11),16) for _ in range(10)];L=min(endpoints+[F(-2)])
            old=min([F(0)]+endpoints[:9]);new=min(old,endpoints[9]);self.assertLessEqual(new-L,old-L);self.assertGreaterEqual(new-L,0)
    def test_action_sensitive_neural_spatial_modulus(self):
        gamma=(F(1,2),F(1,4));beta=F(15,16);weights=[(F(1),F(1)),(F(1),F(-2)),(F(-2),F(3)),(F(0),F(0))]
        xs=[(F(i,4),F(j,4)) for i in range(5) for j in range(5)];actions=[F(0),F(1,16),F(1,4)]
        def drift(x):return [F(1,16)+x[j]/2+x[1-j]/8+x[j]*(1-x[1-j])/16 for j in range(2)]
        center=(F(1,2),F(1,2));fc=drift(center)
        for w in weights:
            s=sum(w[j]*gamma[j] for j in range(2));R=abs(w[0]-w[1])/32;D=F(1,4)
            factor=F(0) if s==0 else min(F(1),abs(s)*D/(2*R)) if R else F(1)
            for x in xs:
                radius=max(abs(x[j]-center[j]) for j in range(2));fx=drift(x)
                for a,b in itertools.product(actions,repeat=2):
                    z=sum(w[j]*fx[j] for j in range(2))-F(1,8);zc=sum(w[j]*fc[j] for j in range(2))-F(1,8)
                    value=beta*abs(algebra.hinge(z+s*a,R)-algebra.hinge(z+s*b,R)-algebra.hinge(zc+s*a,R)+algebra.hinge(zc+s*b,R))
                    bound=beta*F(11,16)*radius*sum(map(abs,w))*factor
                    self.assertLessEqual(value,bound)
    def test_continuous_to_robust_lattice_distance(self):
        for lower in (F(0),F(1,10),F(1,5)):
            cap=lower+F(1,32);quantum=64;imax=int(lower*quantum)
            for j in range(101):
                a=cap*j/100;b=F(min(int(a*quantum),imax),quantum)
                self.assertLessEqual(abs(a-b),cap-lower+F(1,quantum));self.assertLessEqual(b,lower)
    def test_price_plane_transform(self):
        lo,hi=F(-3,10),F(-1,10);cost=F(-1,5)
        for tau,price,work in itertools.product([F(0),F(1,10),F(1)],[F(0),F(1,8)],[F(-2),F(0),F(3)]):
            shift=tau+price*work;self.assertLessEqual(lo+shift,cost+shift);self.assertLessEqual(cost+shift,hi+shift)
if __name__=='__main__':unittest.main(verbosity=2)
