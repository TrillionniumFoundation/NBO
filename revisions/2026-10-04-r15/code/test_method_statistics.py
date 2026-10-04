"""Contract tests for inference errors that would change the estimand."""
import unittest
from fractions import Fraction
import numpy as np
from method_statistics import (empirical_bernstein, finite_stream_mean,
    paired_difference, economic_decision, certified_attainment_fraction,
    work_distribution, fee_to_utility, ConfidenceBudget, _exact_moments,
    audit_descriptive_decomposition)


class StatisticsContracts(unittest.TestCase):
    def setup_args(self):
        return dict(declared_seeds=[11,22],noise_keys={11:'bank11',22:'bank22'},
                    bounds={11:1.,22:1.},biases={11:.1,22:.3},
                    clipping_tails={11:0.,22:0.},event_alpha=.01,
                    confirmation_independent_of_selection=True)

    def test_exact_uniform_target_and_average_allowance(self):
        r=finite_stream_mean({11:np.ones(1000)*.2,22:np.ones(1000)*.8},**self.setup_args())
        self.assertAlmostEqual(r['clipped_mean'],.5)
        self.assertAlmostEqual(r['bias'],.2)
        self.assertEqual(r['paths'],2000)
        self.assertEqual(r['seed_count'],2)
        self.assertLessEqual(r['lower'],.3)
        self.assertGreaterEqual(r['upper'],.7)

    def test_rejects_seed_attrition_unequal_paths_and_reused_noise(self):
        with self.assertRaises(ValueError):finite_stream_mean({11:[0,0]},**self.setup_args())
        with self.assertRaises(ValueError):finite_stream_mean({11:[0,0],22:[0,0,0]},**self.setup_args())
        args=self.setup_args();args['noise_keys']={11:'same',22:'same'}
        with self.assertRaises(ValueError):finite_stream_mean({11:[0,0],22:[0,0]},**args)

    def test_rejects_stopping_array_as_confirmation(self):
        args=self.setup_args();args['confirmation_independent_of_selection']=False
        with self.assertRaises(ValueError):finite_stream_mean({11:[0,0],22:[0,0]},**args)

    def test_constant_observations_do_not_have_zero_sampling_radius(self):
        r=empirical_bernstein(np.zeros(100),bound=1,event_alpha=.01)
        self.assertGreater(r['empirical_bernstein_margin'],0)
        self.assertLess(r['lower'],0);self.assertGreater(r['upper'],0)
        rr=empirical_bernstein(np.zeros(1000),bound=1,event_alpha=.01)
        self.assertLess(rr['empirical_bernstein_margin'],r['empirical_bernstein_margin'])

    def test_clipping_and_bias_are_retained(self):
        r=empirical_bernstein([100]*100,bound=1,event_alpha=.01,bias=.4,clipping_tail=.6)
        self.assertEqual(r['clipped_paths'],100)
        self.assertEqual(r['mean'],100)
        self.assertEqual(r['clipped_mean'],1)
        self.assertLess(r['lower'],0)

    def test_equivalence_is_not_nonsignificance(self):
        wide=economic_decision(-.02,.02,.001)
        self.assertFalse(wide['practical_equivalence']);self.assertTrue(wide['unresolved'])
        tight=economic_decision(-.0001,.0002,.001)
        self.assertTrue(tight['practical_equivalence']);self.assertFalse(tight['statistical_superiority'])
        tiny=economic_decision(.0001,.0002,.001)
        self.assertTrue(tiny['practical_equivalence']);self.assertTrue(tiny['statistical_superiority'])
        self.assertFalse(tiny['economically_material_superiority'])

    def test_pairing_identity_prevents_unpaired_subtraction(self):
        ident=dict(initial_profile_hash='i',initial_state_hash='state',terminal_anchor_hash='anchor',noise_hash='n',steps=8,paths=2,stream_seed=11,confirmation_bank='c',primitives_sha256='p')
        np.testing.assert_array_equal(paired_difference([3,7],[1,2],left_identity=ident,right_identity=ident),[2,5])
        other=dict(ident,noise_hash='other')
        with self.assertRaises(ValueError):paired_difference([3,7],[1,2],left_identity=ident,right_identity=other)
        other=dict(ident,terminal_anchor_hash='different-anchor')
        with self.assertRaises(ValueError):paired_difference([3,7],[1,2],left_identity=ident,right_identity=other)

    def test_integer_moments_against_pairwise_rational_oracle(self):
        # A pairwise-difference variance oracle uses a different identity from
        # the production exact integer sums and catches cancellation mistakes.
        for values in [[.1,-.3,1e-12,4.],[2.**100,2.**100+2.**49,2.**-900]]:
            xs=list(map(Fraction.from_float,values));n=len(xs)
            expected_var=sum((xs[i]-xs[j])**2 for i in range(n) for j in range(i))/(n*(n-1))
            a,b,c,d=_exact_moments(values)
            self.assertEqual(Fraction(a,b),sum(xs)/n)
            self.assertEqual(Fraction(c,d),expected_var)

    def test_finite_success_fraction_and_failed_work(self):
        p=certified_attainment_fraction({11:{'lower':.2,'upper':.4},22:{'lower':0,'upper':.3}},declared_seeds=[11,22],target=.1)
        self.assertEqual(p['probability_lower'],.5);self.assertEqual(p['probability_upper'],1)
        records={s:dict(actual_early_stopping_execution=True,attained=False,end_to_end_seconds=3) for s in [11,22]}
        w=work_distribution(records,[11,22],seconds_cap=10)
        self.assertTrue(w['median_not_attained']);self.assertEqual(w['restricted_mean_time'],10)

    def test_fee_margin_and_confidence_convention(self):
        self.assertGreater(fee_to_utility(.001,.03,1),fee_to_utility(.0005,.03,1))
        self.assertAlmostEqual(ConfidenceBudget(.02,10).event_alpha,.002)

    def test_decomposition_checks_path_identity_without_component_inference(self):
        a=dict(production=np.array([.2,.4]),consumption_deficit=np.array([.1,.2]),terminal_gain=np.array([-.01,.03]))
        a['paired_gain']=a['production']-a['consumption_deficit']+a['terminal_gain']
        r=audit_descriptive_decomposition({11:a,22:a},[11,22])
        self.assertEqual(r['max_path_identity_error'],0)
        self.assertIn('descriptive only',r['inference'])
        self.assertAlmostEqual(sum(v for k,v in r['method_means'].items() if k!='total_numerical_gain'),r['method_means']['total_numerical_gain'])
        bad=dict(a,paired_gain=a['paired_gain']+.01)
        with self.assertRaises(ValueError):audit_descriptive_decomposition({11:a,22:bad},[11,22])


if __name__=='__main__':unittest.main()
