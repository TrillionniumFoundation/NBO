"""Exact independent checks for localization, primitive margins and record contracts.
Tests are deterministic counterexample/regression checks, not a formal proof system.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import copy,json,unittest
import numpy as np
import audit65 as a

B=F(15,16)
def minorant(ll,lu,h,H):
    K=H*h*h/2;D=lu-ll
    if not K:return min(ll,lu)
    if D>=K:return ll
    if D<=-K:return lu
    return (ll+lu)/2-K/4-D*D/(4*K)

def bracket(f,points,H,w,cap_allowance=F(0)):
    L=min(minorant(f(l)-w,f(u)-w,u-l,H) for l,u in zip(points,points[1:]))-cap_allowance
    U=min(f(x)+w for x in points)
    return L,U

class IndependentTests(unittest.TestCase):
    def test_localization_interior_and_boundary(self):
        for star in (F(0),F(1,3),F(1)):
            for curvature,w,k,mesh in product((F(0),F(1),F(3)),(F(0),F(1,100)),range(5),(4,8)):
                slope=F(1) if star==0 else (F(-1) if star==1 else F(0))
                f=lambda x:curvature*(x-star)**2/2+slope*(x-star)
                points=sorted(set([F(j,mesh) for j in range(mesh+1)]+[F(k,4)]))
                L,U=bracket(f,points,curvature,w);h=max(u-l for l,u in zip(points,points[1:]));e=abs(F(k,4)-star)
                self.assertLessEqual(L,f(star));self.assertGreaterEqual(U,f(star))
                self.assertLessEqual(U-L,2*w+curvature*h*h/8+abs(slope)*e+curvature*e*e/2)
    def test_capacity_remainder_in_localization(self):
        f=lambda x:(x-1)**2;points=[F(j,8) for j in range(7)];Delta=F(1,4);H=F(2);Lam=F(2);w=F(1,101)
        L,U=bracket(f,points,H,w,Lam*Delta);e=F(1,4)
        self.assertLessEqual(U-L,2*w+Lam*Delta+H*F(1,8)**2/8+H*e*e/2)
    def test_boundary_linear_term_is_necessary(self):
        f=lambda x:x;points=[F(1,8),F(1,4)];e=F(1,8)
        self.assertEqual(f(e)-f(0),e);self.assertGreater(f(e)-f(0),F(0))
    def test_good_witness_does_not_localize_lower_bound(self):
        f=lambda x:F(0);L,U=bracket(f,[F(0),F(1,2),F(1)],F(2),F(0))
        self.assertEqual(U,0);self.assertEqual(U-L,F(1,16))
    def test_running_certificate_progress_identity(self):
        for L,U,l,u in product(range(-2,1),range(1,4),range(-2,1),range(1,4)):
            newL=max(L,l);newU=min(U,u)
            self.assertEqual((U-L)-(newU-newL),(U-newU)+(newL-L));self.assertGreaterEqual((U-L)-(newU-newL),0)
    def test_extra_query_can_have_zero_progress(self):
        self.assertEqual((2-(-1))-(min(2,3)-max(-1,-2)),0)
    def test_parabolic_minorant_faces(self):
        self.assertEqual(minorant(F(0),F(2),F(1),F(2)),0)
        self.assertEqual(minorant(F(2),F(0),F(1),F(2)),0)
        self.assertEqual(minorant(F(0),F(0),F(1),F(2)),F(-1,4))
    def test_primitive_convexity_margin(self):
        for d in (2,4,8,16,32):self.assertEqual(F(4,d)-B*F(27,d)/8,F(107,128*d))
    def test_dimension_normalized_regularities(self):
        G,M=F(10),F(26)
        for r in range(32):
            for d in (2,8,16):self.assertEqual((G/d,M/d),a.q.regularity(r,d))
            self.assertLessEqual(G,27);self.assertLessEqual(M,54)
            G,M=F(1037,128)+B*F(47,64)*G,F(22)+F(21,256)+B*(F(9,16)*M+G/8)
    def test_scalar_budget_constants(self):
        self.assertEqual(F(21,4)+B*54*F(5,32),F(3369,256))
        self.assertEqual(F(13,16)+B*27*F(3,8),F(1319,128))
        self.assertEqual(B*54/F(6144),F(135,16384))
    def test_midpoint_variance_identity(self):
        for q in (1,2,4,8,16):
            mid=[F(2*j+1-q,32*q) for j in range(q)]
            self.assertEqual(F(1,3072)-sum(v*v for v in mid)/q,F(1,3072*q*q))
    def test_simplex_barycentric_feasibility_and_boundary(self):
        points=[(F(0),F(0)),(F(1),F(0)),(F(0),F(1)),(F(1),F(1))]
        caps=[F(1,8)+sum(x)/16 for x in points]
        for t in (F(0),F(1,7),F(1)):
            weights=[(1-t)**2,t*(1-t),t*(1-t),t*t]
            x=[sum(w*p[j] for w,p in zip(weights,points)) for j in range(2)]
            ac=sum(w*c for w,c in zip(weights,caps))
            self.assertEqual(ac,F(1,8)+sum(x)/16)
            for share in (F(0),F(1,3),F(1)):
                control=[share*ac,(1-share)*ac];self.assertEqual(sum(control),ac)
    def test_transition_and_capacity_domain_corners(self):
        for d in (2,4):
            for x in product((F(0),F(1)),repeat=d):
                cap=F(1,8)+sum(x)/(8*d)
                for action,z in product((F(0),cap),(F(-1,32),F(1,32))):self.assertTrue(all(0<=v<=1 for v in a.transition(x,action,z)))
    def test_actual_catalogue_precision_recovery(self):
        for T,target in product((2,3),('1/32','1/128')):
            delta=F(a.q.local_tolerance(T,target));S=sum((B**t for t in range(T)),F(0))
            upper=F(a.q.policy_allowance(T,target))
            self.assertGreaterEqual(upper,(delta+(F(8)+B*F(297,16)+27)/2**40)*S)
            self.assertLessEqual(upper,F(target))
            for depth in range(T):self.assertGreater(delta/(4*B)**depth,8*F(1319,128)/2**32)
    def test_complete_process_records_all_accounted(self):
        j=a.read(a.R/'audit/RESULT_AUDIT65.json')
        self.assertEqual(j['summary']['returned_services'],256);self.assertEqual(j['summary']['matched_model_pairs'],64)
        self.assertEqual(j['summary']['checked_policy_decisions'],55296)
    def fixture(self):
        spec=a.s64.catalogue()[0];p=a.s64.R/'results64'/spec['key'];summ=a.read(p/'summary.json');cost=a.read(p/'exact-costs.json')
        with np.load(p/'trace.npz') as z:trace={k:z[k].copy() for k in z.files}
        return spec,summ,trace,cost
    def test_trace_action_mutation_rejected(self):
        sp,s,tr,c=self.fixture();tr['t0_action'][0]=1.;self.assertRaises(AssertionError,a.validate_trace,sp,s,tr,c)
    def test_trace_observation_mutation_rejected(self):
        sp,s,tr,c=self.fixture();tr['t0_observed'][0,0]+=2**-20;self.assertRaises(AssertionError,a.validate_trace,sp,s,tr,c)
    def test_trace_gap_mutation_rejected(self):
        sp,s,tr,c=self.fixture();tr['t0_gap'][0]=1.;self.assertRaises(AssertionError,a.validate_trace,sp,s,tr,c)
    def test_trace_cost_mutation_rejected(self):
        sp,s,tr,c=self.fixture();c['cost'][0]='0';self.assertRaises(AssertionError,a.validate_trace,sp,s,tr,c)
    def test_target_request_mutation_rejected(self):
        sp,s,tr,c=self.fixture();sp=dict(sp,target='1/4096');self.assertRaises(AssertionError,a.validate_trace,sp,s,tr,c)
    def test_numeraire_purchase_sign(self):
        l,u=F(1,100),F(1,20);n,m=10,2;fee=F(1,10)
        self.assertGreater(n*m*l-fee,0);self.assertEqual(n*m*u-fee,F(9,10))
    def test_amortization_boundary_is_strict(self):
        B0,DC,DL=12,7,4
        self.assertEqual(B0+4*DL,4*DC);self.assertLess(B0+5*DL,5*DC)

if __name__=='__main__':unittest.main(verbosity=2)
