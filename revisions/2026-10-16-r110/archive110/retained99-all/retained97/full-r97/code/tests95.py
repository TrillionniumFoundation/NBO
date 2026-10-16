"""R95 checks: exact primitive identities, full retained rows and preservation.

The mathematical theorems are proved in the supplement; these tests are
regression checks and evidence validation, not a finite proof of the continuum.
"""
from __future__ import annotations
import hashlib,itertools,json,pathlib,unittest
from fractions import Fraction as F
import numpy as np
from interval94 import I
from investment94 import BETA,S,terminal_certificate
from continuum94 import strict_tail_cuts
from study94 import ARMS,LEVELS,ROOT,rows,sha,source_files,paired_interval
import independent94 as exact

class PrimitiveProofRegression(unittest.TestCase):
    def test_positive_joint_curvature(self):
        self.assertEqual(4-F(5,4)*F(15,16),F(181,64))
        self.assertGreater(F(181,64),0)
    def test_complete_state_modulus(self):
        bound=F(15,2)+F(15,16)*(F(55,8)+F(15,32))
        self.assertEqual(bound,F(7365,512));self.assertLess(bound,15)
    def test_state_transfer_fits_terminal_budget(self):
        self.assertLess(F(1,2**21)+30*F(1,2**40),F(1,2**20))
    def test_original_transition_domain(self):
        for d in (2,4,8):
            for vals in itertools.product((F(0),F(1)),repeat=d):
                for a,z in itertools.product((F(0),F(1,4)),(F(-1,32),F(1,32))):
                    y=exact.next_state(vals,a,z)
                    self.assertTrue(all(F(1,32)<=v<=F(27,32) for v in y))
    def test_exact_original_terminal_polynomial(self):
        for d in (2,4,8):
            for j in range(5):
                x=[F((k*3+j)%9,8) for k in range(d)];a=F(j,32)
                poly=exact.polynomial_from_primitives(x,a)
                self.assertEqual(poly[2],5)
                for z in (F(-1,32),F(-1,96),F(0),F(1,128),F(1,32)):
                    self.assertEqual(exact.evaluate(poly,z),exact.economic_S(exact.next_state(x,a,z),True))
    def test_exact_joint_midpoint_curvature(self):
        for d in (2,4):
            mu=F(181,64*d)
            for j in range(12):
                x=[F((k+j)%5,4) for k in range(d)];y=[F((2*k+3*j)%5,4) for k in range(d)]
                a,b=F(j%5,16),F((j+2)%5,16);z=F((j%3)-1,32)
                def obj(v,u):return exact.economic_S(v)+u*u+4*u**4+F(15,16)*exact.economic_S(exact.next_state(v,u,z),True)
                mid=[(v+w)/2 for v,w in zip(x,y)]
                reserve=(mu*sum((v-w)**2 for v,w in zip(x,y))+2*(a-b)**2)/8
                self.assertLessEqual(obj(mid,(a+b)/2),(obj(x,a)+obj(y,b))/2-reserve)
    def test_horizon_modulus_invariant(self):
        C=F(10)
        for _ in range(256):
            C=F(1037,128)+F(15,16)*F(47,64)*C
            self.assertLess(C,27)
    def test_horizon_joint_curvature_constant(self):
        self.assertEqual(4-F(15,16)*F(27,8),F(107,128))
        self.assertGreater(F(107,128),0);self.assertEqual(2-F(1,4),F(7,4))
    def test_horizon_action_and_innovation_constants(self):
        self.assertEqual(F(13,16)+F(15,16)*F(3,8)*27,F(1319,128))
        self.assertEqual(F(15,16)*27*(F(1,32)+F(1,64)),F(1215,1024))
    def test_horizon_geometric_account(self):
        a,b,c=F(27,1296),F(1319,512*124),F(1215,512*116)
        for horizon in (1,2,4,16,64):
            bound=sum(F(15,16)**t*(a+b+c) for t in range(horizon))+F(15,16)**horizon*a
            self.assertLessEqual(bound,16*(a+b+c))
    def test_sufficient_fixed_accuracy_resolutions(self):
        def ceil(q):return -(-q.numerator//q.denominator)
        for eps in (F(1,4),F(1,16),F(1,64)):
            nx=ceil(1296/eps);m=ceil(F(3957,32)/eps);nz=4*ceil(F(3645,128)/eps)
            self.assertEqual(nz%4,0)
            bound=16*(F(27,nx)+F(1319,512*m)+F(1215,512*nz))
            self.assertLessEqual(bound,eps)
    def test_original_simplex_net_cover_regression(self):
        for m in range(1,9):
            grid=[(F(i,m),F(j,m)) for i in range(m+1) for j in range(m+1-i)]
            for i in range(17):
                for j in range(17-i):
                    x,y=F(i,16),F(j,16)
                    self.assertLessEqual(min(abs(x-a)+abs(y-b) for a,b in grid),F(1,m))
    def test_global_support_at_independent_states(self):
        anchors=np.array([[0.,0.],[.25,.75],[.75,.25],[1.,1.]])
        for alpha in LEVELS:
            rec=terminal_certificate(I(anchors),alpha)
            for target in ([.125,.625],[.5,.5],[.875,.125]):
                lower,_,_=exact.terminal_bounds(target,alpha)
                bound=I(rec['lower'])+(rec['slope']*(I(np.asarray(target))-I(anchors))).sum()
                self.assertTrue(np.all(bound.lo<=float(lower)))
    def test_strict_screen_equality_retained(self):
        lo=np.array([[0.,1.,1.,2.]]);hi=lo.copy()
        cuts=strict_tail_cuts(lo,hi,.5)
        self.assertTrue(np.array_equal(cuts,[[True,False,False,False]]))
    def test_screen_rejects_reversed_or_nonfinite(self):
        with self.assertRaises(ValueError):strict_tail_cuts(np.array([1.,2.]),np.array([0.,3.]),.5)
        with self.assertRaises(ValueError):strict_tail_cuts(np.array([0.,np.nan]),np.array([1.,3.]),.5)

class FrozenEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out=ROOT/'results94';cls.dest=cls.out/'evaluation-local95'
        cls.cal=json.loads((cls.out/'CALIBRATION94.json').read_text())
        cls.res=json.loads((cls.dest/'RESULTS94.json').read_text())
    def test_source_freeze_matches(self):
        self.assertEqual(self.cal['source_files'],source_files())
        self.assertEqual(self.res['source_files'],source_files())
        self.assertEqual(self.res['calibration_sha256'],sha(self.out/'CALIBRATION94.json'))
    def test_every_arm_every_frozen_initial_state(self):
        count=0
        for idx in range(2):
            x=rows(3,idx,2048)
            for arm in ARMS:
                p=self.dest/f'alpha-{idx}-{arm}.csv';a=np.genfromtxt(p,delimiter=',',names=True)
                self.assertEqual(len(a),2048);self.assertTrue(np.array_equal(a['row'],np.arange(2048)))
                self.assertTrue(np.array_equal(a['x0'],x[:,0]));self.assertTrue(np.array_equal(a['x1'],x[:,1]))
                self.assertEqual(sha(p),self.res['levels'][str(idx)]['arms'][arm]['data']['raw_sha256']);count+=len(a)
        self.assertEqual(count,16384)
    def test_original_capacity_and_both_targets_all_rows(self):
        for p in self.dest.glob('alpha-*.csv'):
            a=np.genfromtxt(p,delimiter=',',names=True)
            self.assertTrue(np.all(a['action']>=0));self.assertTrue(np.all(a['action']<=.125+(a['x0']+a['x1'])/16))
            self.assertTrue(np.all(a['own_Q_gap_upper']<=1/64));self.assertTrue(np.all(a['original_optimum_loss_upper']<=1/16))
            self.assertTrue(np.all(a['cost_lower']<=a['cost_upper']))
    def test_calibration_selected_without_using_evaluation(self):
        self.assertEqual(self.cal['evaluation_rows_opened'],0)
        for idx in range(2):
            lev=self.cal['levels'][str(idx)];select=min(ARMS,key=lambda a:(sum(lev['calibration'][a]['mean_cost_interval'])/2,a))
            self.assertEqual(select,lev['selected_arm']);self.assertEqual(select,self.res['levels'][str(idx)]['selected_arm'])
    def test_all_twelve_pairwise_results_replay(self):
        for idx in range(2):
            data={}
            for arm in ARMS:
                a=np.genfromtxt(self.dest/f'alpha-{idx}-{arm}.csv',delimiter=',',names=True)
                data[arm]={'lower':a['cost_lower'],'upper':a['cost_upper']}
            for a,b in itertools.combinations(ARMS,2):
                self.assertEqual(paired_interval(data[a],data[b]),self.res['levels'][str(idx)]['pairwise'][a+' minus '+b])
    def test_stream_domains_do_not_collide(self):
        arrays=[rows(stream,idx,32) for stream in (1,2,3) for idx in (0,1)]
        for a,b in itertools.combinations(arrays,2):self.assertFalse(np.array_equal(a,b))
    def test_continuous_screen_denominators(self):
        for lev in self.res['levels'].values():
            for arm in ARMS:
                s=lev['screening'][arm];self.assertEqual(s['candidate_bins'],4096)
                self.assertEqual(s['candidate_bins'],s['retained_bins']+s['excluded_bins'])
                self.assertTrue(s['identical_tail_values']);self.assertEqual(s['new_economic_observations'],0)
    def test_no_deleted_inherited_main_section(self):
        import re
        before=(ROOT/'preserved/R92-wrappers/ECTA.tex').read_text()
        current=(ROOT/'ECTA.tex').read_text()+(ROOT/'appendix.tex').read_text()
        for sec in re.findall(r'\\input\{(sections/[^}]+)\}',before):
            self.assertEqual(current.count('\\input{'+sec+'}'),1)
    def test_exact_editorial_moves(self):
        for rec in json.loads((ROOT/'audit/local95/CONTENT_MAP95.json').read_text()):
            if rec['new_document']=='appendix.tex':
                self.assertTrue(rec['text_unchanged']);self.assertEqual(rec['baseline_sha256'],rec['current_sha256'])
    def test_original_title_and_author_retained(self):
        main=(ROOT/'ECTA.tex').read_text()
        self.assertIn('\\title{Neural Bellman Operators}',main)
        self.assertIn('\\fnms{Qian}',main);self.assertIn('\\snm{QI}',main)

if __name__=='__main__':unittest.main(verbosity=2)
