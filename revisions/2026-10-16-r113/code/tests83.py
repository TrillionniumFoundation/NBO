"""Exact rational regressions for economic tolerance inversion; no samples."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import copy,unittest
import frontier83 as f

def example(events,n=1):
    pairs=[];intervals=[]
    for threshold,cell,lo,hi in events:
        pairs.append(dict(cell=list(cell),switch_lower=str(F(threshold)),reference_index=0,alternative_index=len(pairs)+1))
        intervals.append([str(F(lo)),str(F(hi))])
    return dict(n=n,reference_objective='0',admitted_switches=pairs,tiers=[dict(accumulated_intervals=intervals)])
def report():
    return dict(policies=['zero','calibrated-relu-n8','legacy-relu-n8'],controller_metadata={},inference={'conditional':{'contrasts':{
        'zero-minus-calibrated-relu-n8':{'interval_exact':['1/10','1/5']},
        'legacy-relu-n8-minus-calibrated-relu-n8':{'interval_exact':['1/100','1/50']}}}})

class EconomicToleranceTests(unittest.TestCase):
    def test_explicit_legacy_identity_no_prefix_guess(self):
        self.assertEqual(f.IDENTITIES['calibrated-relu-n8'],'legacy-relu-n8')
        with self.assertRaises(KeyError):f.pair_band(report(),'relu-n8','calibrated-relu-n8')
    def test_reverse_interval_changes_both_sign_and_order(self):
        self.assertEqual(f.pair_band(report(),'calibrated-relu-n8','zero'),(-F(1,5),-F(1,10)))
    def test_zero_controller_uses_roster_not_fit_metadata(self):
        self.assertEqual(f.pair_band(report(),'zero','calibrated-relu-n8'),(F(1,10),F(1,5)))
    def test_unknown_self_comparison_fails_closed(self):
        with self.assertRaises(KeyError):f.pair_band(report(),'unknown','unknown')
        self.assertEqual(f.pair_band(report(),'zero','zero'),(0,0))
    def test_inconsistent_opposite_comparison_is_rejected(self):
        r=report();r['inference']['conditional']['contrasts']['calibrated-relu-n8-minus-zero']={'interval_exact':['0','0']}
        with self.assertRaises(AssertionError):f.pair_band(r,'zero','calibrated-relu-n8')
    def test_tie_is_admitted_at_exact_barrier(self):
        b=F(1,65536);c=f.curve(example([(b,(0,0),-1,2)]))
        self.assertEqual(f.evaluate(c,b/2)['enabled'],0);self.assertEqual(f.evaluate(c,b)['enabled'],1)
        self.assertEqual(f.evaluate(c,b)['upper'],2)
    def test_multiple_equal_barriers_form_one_stratum(self):
        b=F(1,65536);c=f.curve(example([(b,(0,0),-1,1),(b,(0,0),-3,2)]))
        self.assertEqual(len(c),2);self.assertEqual(c[-1]['enabled'],2);self.assertEqual((c[-1]['lower'],c[-1]['upper']),(-3,2))
    def test_maximum_domain_is_closed_even_at_action_event(self):
        c=f.curve(example([(f.MAX_EXCESS,(0,0),-1,1)]))
        self.assertFalse(c[0]['right_closed']);self.assertTrue(c[-1]['right_closed']);self.assertEqual(c[-1]['left'],c[-1]['right'])
        self.assertEqual(f.evaluate(c,f.MAX_EXCESS)['enabled'],1)
        with self.assertRaises(ValueError):f.evaluate(c,f.MAX_EXCESS+F(1,2**30))
    def test_negative_barrier_is_active_at_zero(self):
        c=f.curve(example([(-1,(0,0),-2,-1)]))
        self.assertEqual(len(c),1);self.assertEqual(c[0]['lower'],-2);self.assertEqual(c[0]['upper'],0)
    def test_no_alternatives_preserves_identity_over_entire_domain(self):
        c=f.curve(example([]));self.assertEqual(len(c),1);self.assertEqual((c[0]['lower'],c[0]['upper']),(0,0));self.assertTrue(c[0]['right_closed'])
    def test_independent_cellwise_reconstruction_and_no_aliasing(self):
        s=example([(F(1,65536),(0,0),-2,1),(F(1,32768),(1,1),-3,4),(F(1,16384),(0,0),-1,7)],2);c=f.curve(s)
        first=copy.deepcopy(c[0]);f.audit_curve(s,c);self.assertEqual(c[0],first)
        for q in [F(0),F(1,65536),F(1,50000),F(1,32768),f.MAX_EXCESS]:
            self.assertEqual((f.evaluate(c,q)['lower'],f.evaluate(c,q)['upper']),f.slow_band(s,q))
    def test_every_qualified_toy_readout_is_enclosed(self):
        # F(theta)=theta^2 and exact switch lower value t^2. Both cells
        # share the same theta; independent cell extrema only enlarge its image.
        thresholds=[F(1,256),F(1,128)];effects=[F(-1,5),F(1,3)]
        events=[(t*t,(i,0),effect,effect) for i,(t,effect) in enumerate(zip(thresholds,effects))]
        c=f.curve(example(events,2))
        for theta in [F(k,4096) for k in range(-64,65)]:
            for eps in [F(0),F(1,65536),F(1,16384),f.MAX_EXCESS]:
                if theta*theta>eps:continue
                cost=sum((d for t,d in zip(thresholds,effects) if theta>=t),F(0))/4;row=f.evaluate(c,eps)
                self.assertLessEqual(row['lower'],cost);self.assertLessEqual(cost,row['upper'])
    def test_frontier_agrees_with_exhaustive_grid(self):
        a=f.curve(example([(F(1,65536),(0,0),-F(1,1000),F(1,800)),(F(1,8192),(0,0),-F(1,500),F(1,300))]))
        b=f.curve(example([(F(1,32768),(0,0),-F(1,900),F(1,600))]))
        for base,kind in product([(F(1,1000),F(1,500)),(-F(1,500),-F(1,1000)),(-F(1,2000),F(1,2000))],['positive','negative','equivalent']):
            out=f.frontier(a,b,base,kind);rows={s['first_index']:s['second_last_index'] for s in out['stripes']}
            for i,j in product(range(len(a)),range(len(b))):self.assertEqual(f.predicate(kind,*f.transferred(base,a[i],b[j])),i in rows and j<=rows[i])
            self.assertLessEqual(out['predicate_evaluations'],len(a)+len(b))
    def test_strict_positive_region_has_open_failure_endpoint(self):
        b=F(1,32768);a=f.curve(example([(b,(0,0),-F(1,100),0)]));z=f.curve(example([]))
        result=f.common_limit(a,z,(F(1,100),F(1,50)),'positive')
        self.assertEqual(result['supremum'],b);self.assertFalse(result['supremum_included']);self.assertEqual(result['first_failure_interval'][0],0)
    def test_equivalence_does_not_include_margin_equality(self):
        self.assertFalse(f.predicate('equivalent',-f.MARGIN,f.MARGIN/2));self.assertFalse(f.predicate('equivalent',-f.MARGIN/2,f.MARGIN))
        self.assertTrue(f.predicate('equivalent',-f.MARGIN/2,f.MARGIN/2))
    def test_cost_band_transfer_and_supremum_are_not_optimizer_attainment(self):
        a=dict(lower=-F(1,20),upper=F(1,30));b=dict(lower=-F(1,40),upper=F(1,50))
        self.assertEqual(f.transferred((F(1,10),F(1,5)),a,b),(F(3,100),F(31,120)))
    def test_original_three_tolerances_are_exact_slices(self):
        root=Path(__file__).resolve().parents[1]
        for n,kind in f.MODELS:
            service=f.read(root/'results82'/f'{kind}-n{n}.json');states=f.curve(service)
            for old in service['tiers'][-1]['sublevels']:
                row=f.evaluate(states,F(old['extra_objective']));self.assertEqual((row['lower'],row['upper']),(F(old['lower']),F(old['upper'])))
    def test_all_original_controller_comparisons_have_exact_names(self):
        r=f.read(Path(__file__).resolve().parents[1]/'results80/cost/summary.json')
        for name,legacy in f.IDENTITIES.items():
            lo,hi=f.pair_band(r,legacy,name);self.assertLessEqual(lo,hi)
            lo,hi=f.pair_band(r,'zero',name);self.assertLessEqual(lo,hi)
if __name__=='__main__':unittest.main(verbosity=2)
