"""New exact mathematical and numerical regressions; not economic observations."""
from fractions import Fraction as F
import itertools,unittest
import compatible84 as p
import verify84 as v
from qualification73 import Problem
from calibrated80 import Calibrated

def model():
    return Calibrated(Problem(features=((F(1),)+(F(0),)*8,),lower=(F(0),),upper=(F(0),),lipschitz=(F(0),)*9,bounds=(F(1),)*9,radius=F(1,4),bellman_lipschitz=F(0)),'relu')
def direction(sign):return (F(0),F(sign))+(F(0),)*7

class CompatibleEconomicTests(unittest.TestCase):
    def test_reference_defeat_need_not_be_winner(self):
        scores={'reference':F(0),'alternative':F(-1),'other':F(-2)}
        self.assertLess(scores['alternative'],scores['reference'])
        self.assertNotEqual(min(scores,key=scores.get),'alternative')

    def test_actual_winner_satisfies_all_weak_inequalities(self):
        for theta in map(F,(-2,-1,0,1,2)):
            scores=[F(0),1-theta,1+theta];chosen=min(range(3),key=lambda i:(scores[i],i))
            self.assertTrue(all(scores[chosen]<=s for s in scores))

    def test_single_events_possible_joint_impossible(self):
        grid=list(map(F,(-1,0,1)))
        self.assertTrue(any(x>=1 for x in grid));self.assertTrue(any(x<=-1 for x in grid))
        self.assertFalse(any(x>=1 and x<=-1 for x in grid))

    def test_exact_farkas_separates_joint_event(self):
        ds=(direction(-1),direction(1));cs=(F(1),F(1));cert=p.infeasibility((F(1),)*9,ds,cs)
        self.assertIsNotNone(cert);self.assertGreater(cert['separation'],0)
        w=v.unpack(p.encode(cert['weights']),2)
        self.assertLessEqual(sum(w),1)
        slope=tuple(sum((q*d[k] for q,d in zip(w,ds)),F(0)) for k in range(9))
        gap=sum(w)-sum(map(abs,slope));self.assertEqual(gap,cert['separation'])

    def test_feasible_intersection_not_declared_infeasible(self):
        self.assertIsNone(p.infeasibility((F(1),)*9,(direction(1),),(F(-1),)))

    def test_qualification_dual_and_independent_check(self):
        m=model();ds=(direction(-1),);cs=(F(1),);raw=p.qualify(m,ds,cs,m.arrays());raw['effective_lower']=raw['lower']
        P=(m.problem.features,m.problem.lower,m.problem.upper,m.problem.bounds,m.problem.radius,m.problem.bellman_lipschitz)
        self.assertEqual(v.certificate(P,'relu',ds,cs,p.encode(raw),[]),raw['lower'])
        theta=(F(0),F(1))+(F(0),)*7;self.assertLessEqual(raw['lower'],m.primal(theta)['objective'])

    def test_infeasible_solver_requires_support_certificate(self):
        m=model();raw=p.qualify(m,(direction(-1),direction(1)),(F(1),F(1)),m.arrays())
        self.assertIsNotNone(raw['infeasibility']);self.assertGreater(raw['infeasibility']['separation'],0)
        raw['effective_lower']=raw['lower'];self.assertFalse(p.is_allowed(raw,F(1000)))

    def test_status_alone_cannot_exclude(self):
        raw={'infeasibility':None,'effective_lower':'-1','solver_success':False,'solver_status':2}
        self.assertTrue(p.is_allowed(raw,F(0)))

    def test_exact_threshold_equality_is_included(self):
        raw={'infeasibility':None,'effective_lower':'1/3'}
        self.assertTrue(p.is_allowed(raw,F(1,3)));self.assertFalse(p.is_allowed(raw,F(1,3)-F(1,10**20)))

    def test_independent_sparse_rejects_duplicates(self):
        with self.assertRaises(AssertionError):v.unpack([[0,'1/2'],[0,'1/2']],1)

    def test_independent_sparse_rejects_negative(self):
        with self.assertRaises(AssertionError):v.unpack([[0,'-1']],1)

    def test_assignment_strictly_sharpens_rectangular_bound(self):
        weights=[F(0),F(0),F(1,2),F(1,2)];cells=[0,1,0,1];edges=[(2,3)]
        cert=p.assignment(weights,cells,edges,2)
        self.assertEqual(cert['upper'],F(1,2));self.assertLess(cert['upper'],1)
        self.assertEqual(v.assignment_dual(weights,cells,edges,2,p.encode(cert)),cert['upper'])
        costs=[sum(weights[i] for i in chosen) for chosen in itertools.product((0,2),(1,3)) if not(2 in chosen and 3 in chosen)]
        self.assertEqual(max(costs),cert['upper'])

    def test_fractional_relaxation_not_exact_policy_attainment(self):
        weights=[F(0)]*3+[F(1,3)]*3;cells=[0,1,2,0,1,2];edges=[(3,4),(3,5),(4,5)]
        cert=p.assignment(weights,cells,edges,3)
        self.assertGreater(cert['upper'],F(1,3));self.assertLessEqual(cert['upper'],F(1,2)+F(1,10**10))

    def test_empty_conflicts_recover_cell_extrema(self):
        weights=[F(0),F(0),F(-1),F(2),F(3)];cells=[0,1,0,0,1]
        cert=p.assignment(weights,cells,[],2);self.assertEqual(cert['upper'],5)

    def test_economic_dual_rejects_forged_upper(self):
        weights=[F(0),F(1)];cells=[0,0];cert=p.encode(p.assignment(weights,cells,[],1));cert['upper']='0'
        with self.assertRaises(AssertionError):v.assignment_dual(weights,cells,[],1,cert)

    def test_economic_dual_rejects_missing_node_coverage(self):
        cert={'cell_dual':['0'],'edge_dual':[],'upper':'0'}
        with self.assertRaises(AssertionError):v.assignment_dual([F(0),F(1)],[0,0],[],1,cert)

    def test_negative_cost_changes_remain_signed(self):
        lo,hi=-F(3,4),F(1,8)
        self.assertEqual(-p.assignment([F(0),-lo],[0,0],[],1)['upper'],lo)
        self.assertEqual(p.assignment([F(0),hi],[0,0],[],1)['upper'],hi)

    def test_primal_dual_gap_places_output_in_class(self):
        optimum=F(7,11);reference=optimum+F(1,100);dual=optimum-F(1,1000);value=optimum+F(1,2000);eps=value-dual
        self.assertLessEqual(value,reference+eps)

    def test_cost_difference_transfer_for_all_enclosed_points(self):
        baseline=(F(1,10),F(1,5));a=(-F(1,100),F(2,100));b=(-F(3,100),F(1,100))
        lo=baseline[0]+a[0]-b[1];hi=baseline[1]+a[1]-b[0]
        for x,y,z in itertools.product(baseline,a,b):self.assertLessEqual(lo,x+y-z);self.assertLessEqual(x+y-z,hi)

    def test_protocol_retains_all_six_tolerances(self):
        self.assertEqual(p.EPS,v.EPS);self.assertEqual(len(p.EPS),6);self.assertEqual(p.PAIR_BUDGET,512)

if __name__=='__main__':unittest.main(verbosity=2)
