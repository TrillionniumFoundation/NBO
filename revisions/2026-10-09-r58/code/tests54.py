"""Exact finite-model theorem checks and continuous primitive regressions.
These are correctness tests, not additional economic observations.
"""
from fractions import Fraction as F
from itertools import product
import random
import unittest
import numpy as np
import directed53 as d

B=F(3,4)

def economy(T,seed=19):
    rng=random.Random(seed+T);S=3;A=3
    costs=[[[F(rng.randrange(0,20),16) for a in range(A)] for x in range(S)] for t in range(T)]
    kernels=[]
    for t in range(T):
        layer=[]
        for x in range(S):
            actions=[]
            for a in range(A):
                weights=[rng.randrange(1,5) for y in range(S)];z=sum(weights)
                actions.append([F(w,z) for w in weights])
            layer.append(actions)
        kernels.append(layer)
    return costs,kernels,[F(1,4),F(1,2),F(3,4)]

def evaluate(c,p,g,pi):
    T=len(c);v=[[F(0) for x in g] for t in range(T)]+[list(g)]
    for t in reversed(range(T)):
        for x in range(len(g)):
            a=pi[t][x];v[t][x]=c[t][x][a]+B*sum(w*z for w,z in zip(p[t][x][a],v[t+1]))
    return v

def optimum(c,p,g):
    T=len(c);v=[[F(0) for x in g] for t in range(T)]+[list(g)]
    for t in reversed(range(T)):
        for x in range(len(g)):
            v[t][x]=min(c[t][x][a]+B*sum(w*z for w,z in zip(p[t][x][a],v[t+1])) for a in range(len(c[t][x])))
    return v

def update(c,p,g,pi,margin=F(0),cellwise=False):
    v=evaluate(c,p,g,pi);new=[row[:] for row in pi];eps=[]
    for t in range(len(c)):
        advantage=[[c[t][x][a]+B*sum(w*z for w,z in zip(p[t][x][a],v[t+1]))-v[t][x] for a in range(len(c[t][x]))] for x in range(len(g))]
        cells=[list(range(len(g)))] if cellwise else [[x] for x in range(len(g))]
        gaps=[]
        for cell in cells:
            lower=min(F(0),min(advantage[x][a]-margin for x in cell for a in range(len(c[t][x]))))
            upper=F(0);chosen=None
            for a in range(len(c[t][0])):
                u=max(advantage[x][a]+margin for x in cell)
                if u<upper:upper=u;chosen=a
            if chosen is not None:
                for x in cell:new[t][x]=chosen
            gaps.append(upper-lower)
        eps.append(max(gaps))
    return new,eps

class DirectedCertificateTests(unittest.TestCase):
    def test_exact_full_sweeps_reach_bellman_optimum(self):
        for T in range(1,6):
            c,p,g=economy(T);pi=[[2,1,0] for t in range(T)];star=optimum(c,p,g)
            for k in range(T):
                old=evaluate(c,p,g,pi);new,eps=update(c,p,g,pi);v=evaluate(c,p,g,new)
                self.assertEqual(eps,[F(0)]*T)
                for t in range(T):
                    self.assertTrue(all(a<=b for a,b in zip(v[t],old[t])))
                    self.assertLessEqual(max(a-b for a,b in zip(v[t],star[t])),B*max(a-b for a,b in zip(old[t+1],star[t+1])))
                pi=new
            self.assertEqual(evaluate(c,p,g,pi),star)

    def test_whole_cell_conservative_endpoints(self):
        for T in range(1,5):
            c,p,g=economy(T);pi=[[1,1,1] for t in range(T)];star=optimum(c,p,g)
            for k in range(T):
                old=evaluate(c,p,g,pi);new,eps=update(c,p,g,pi,F(1,32),True);v=evaluate(c,p,g,new)
                for t in range(T):
                    self.assertTrue(all(a<=b for a,b in zip(v[t],old[t])))
                    self.assertLessEqual(max(a-b for a,b in zip(v[t],star[t])),B*max(a-b for a,b in zip(old[t+1],star[t+1]))+eps[t])
                pi=new

    def test_coefficient_one_is_sharp(self):
        delta=F(7,19);incumbent=delta;opt=F(0);U=F(0);L=-delta
        self.assertEqual(incumbent-opt,U-L)
        self.assertGreater(incumbent-opt,F(99,100)*(U-L))

    def test_menu_only_gap_is_not_continuous_accuracy(self):
        actual_costs=[F(1),F(0)];menu=[0]
        reported_menu_gap=actual_costs[0]-min(actual_costs[a] for a in menu)
        self.assertEqual(reported_menu_gap,0)
        self.assertGreater(actual_costs[0]-min(actual_costs),reported_menu_gap)

    def test_signed_gate_retains_useful_direction(self):
        current=F(1,10);continuation=-F(1,5)
        self.assertLess(current+continuation,0)
        self.assertGreater(current+abs(continuation),0)

    def test_product_coupling_signed_residual_identity(self):
        c,p,g=economy(4);pi=[[2,1,0] for t in c];J=evaluate(c,p,g,pi)
        h=[[F((t+1)*(x-1),3) for x in range(3)] for t in range(5)]
        r=[[c[t][x][pi[t][x]]+B*sum(w*z for w,z in zip(p[t][x][pi[t][x]],h[t+1]))-h[t][x] for x in range(3)] for t in range(4)]
        r.append([g[x]-h[4][x] for x in range(3)])
        D=[[[F(0) for y in range(3)] for x in range(3)] for t in range(5)]
        D[4]=[[r[4][x]-r[4][y] for y in range(3)] for x in range(3)]
        for t in reversed(range(4)):
            for x,y in product(range(3),repeat=2):
                paired=sum(p[t][x][pi[t][x]][u]*p[t][y][pi[t][y]][v]*D[t+1][u][v] for u,v in product(range(3),repeat=2))
                D[t][x][y]=r[t][x]-r[t][y]+B*paired
                self.assertEqual(D[t][x][y],J[t][x]-h[t][x]-J[t][y]+h[t][y])

    def test_approximate_relu_null_bound(self):
        grid=[F(0),F(1,4096),F(1,256),F(1,16)]
        for eta,xi,lam in product(grid,repeat=3):
            ga=F(1,2)+xi+lam;gb=F(1,4)-xi/2-lam;slope=ga-(2+eta)*gb
            for a,b,z in product([F(0),F(1,8),F(1,4)],repeat=3):
                for M in (1,16,4096):
                    left=M*max(F(0),z+ga*a-(2+eta)*gb*a)
                    right=M*max(F(0),z+ga*b-(2+eta)*gb*b)
                    self.assertLessEqual(abs(left-right),abs(M*slope*(a-b)))

    def test_perturbed_coefficient_expansion(self):
        v0=[F(1),F(-2)];B0=[F(1,2),F(1,4)]
        for eta,xi in product([F(-1,16),F(0),F(1,16)],repeat=2):
            dv=[F(0),eta];db=[xi,-xi/2]
            lhs=sum((v0[j]+dv[j])*(B0[j]+db[j]) for j in range(2))
            rhs=sum(dv[j]*B0[j]+v0[j]*db[j]+dv[j]*db[j] for j in range(2))
            self.assertEqual(lhs,rhs)

    def test_local_error_expansion(self):
        eta=[F(1,7),F(1,11),F(1,13),F(1,17)];b=eta[-1]
        for x in reversed(eta[:-1]):b=x+B*b
        self.assertEqual(b,sum(B**j*x for j,x in enumerate(eta)))

    def test_rectangle_extrema_include_boundary_cells(self):
        a=np.arange(16,dtype=np.uint16).reshape(4,4)*16;actor=d.RectangleActor(a,2)
        for i,j,k,l in product(range(4),repeat=4):
            if i>k or j>l:continue
            box=d.I(np.array([[i/4,j/4]]),np.array([[(k+1)/4,(l+1)/4]]))
            val=actor.action(box);right=min(k+1,3);top=min(l+1,3)
            self.assertEqual(val.lo[0],a[i:right+1,j:top+1].min()/4096)
            self.assertEqual(val.hi[0],a[i:right+1,j:top+1].max()/4096)

    def test_rectangle_storage_account(self):
        actor=d.RectangleActor(np.zeros((32,32),dtype=np.uint16),5)
        self.assertEqual(actor.bytes,149760)

    def test_streamed_work_upper_bound(self):
        policies=np.zeros((2,2,2),dtype=np.uint16)
        new,report,raw=d.sweep(policies,bits=1,q=2,p=1)
        bound=17*4*(1+(1+2))
        self.assertLessEqual(report['work']['pair_nodes'],bound)
        self.assertTrue(np.all(new>=0))
        for t in range(2):self.assertTrue(np.all(raw[f't{t}_accepted_upper']<=0))

if __name__=='__main__':unittest.main(verbosity=2)
