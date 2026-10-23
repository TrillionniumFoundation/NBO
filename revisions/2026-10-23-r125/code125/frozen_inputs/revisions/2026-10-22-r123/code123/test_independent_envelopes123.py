"""Analytic exact witnesses and rejection cases for the independent reader."""
from copy import deepcopy
from fractions import Fraction as F
import unittest

from independent_envelopes123 import RationalCertificate, analyze_case, validate_case


def quadratic_case():
    a = F(3, 4)
    center = F(1, 3)
    q = (a-center)**2
    g = 2*(a-center)
    return {"A": "1", "incumbent": str(a), "mu": "2", "L": "2",
            "delta": "1/1000", "tau": "1", "omega": "1",
            "old_optimum_lower": "-10",
            "payloads": [{"a": str(a), "W": str(q), "U": str(q),
                          "p_lower": str(g), "p_upper": str(g),
                          "g_lower": str(g), "g_upper": str(g)}],
            "candidates": [{"b": "1/3"}, {"b": str(a)}]}


def crossing_case():
    # Q(x)=x^2, mu=1, L=3. The gradient transports are loose but valid.
    return {"A": "1", "incumbent": "1", "mu": "1", "L": "3",
            "delta": "0", "tau": "10", "omega": "10",
            "old_optimum_lower": "-10",
            "payloads": [{"a": "0", "W": "0", "U": "0",
                          "p_lower": "0", "p_upper": "0",
                          "g_lower": "0", "g_upper": "0"},
                         {"a": "1", "W": "1", "U": "1",
                          "p_lower": "2", "p_upper": "2",
                          "g_lower": "2", "g_upper": "2"}],
            "candidates": [{"b": "0"}, {"b": "1/2"}, {"b": "1"}]}


class ExactWitnesses(unittest.TestCase):
    def test_exact_quadratic_and_future_allowance(self):
        e = RationalCertificate(quadratic_case())
        c = e.candidate(F(1, 3), "fused")
        self.assertEqual(e.B, 0)
        self.assertEqual(c["q_lower"], 0)
        self.assertEqual(c["q_upper"], 0)
        self.assertEqual(c["regret_upper"], F(1, 1000))
        self.assertEqual(c["gain_lower"], F(25, 144)-F(1, 1000))
        self.assertEqual(e.fused_minimizer(), F(1, 3))
        self.assertTrue(c["eligible"])

    def test_identity_does_not_pay_future_allowance(self):
        c = RationalCertificate(quadratic_case()).candidate(F(3, 4), "fused")
        self.assertEqual(c["policy_contrast_lower"], 0)
        self.assertEqual(c["policy_contrast_upper"], 0)
        self.assertEqual(c["gain_lower"], 0)
        self.assertFalse(c["eligible"])

    def test_strict_crossing_improvement_with_same_information(self):
        e = RationalCertificate(crossing_case())
        self.assertEqual(e.contrast(0, 1, "fused"), (F(3, 4), F(5, 4)))
        self.assertEqual(e.contrast(0, 1, "best_single"), (F(1, 2), F(3, 2)))
        self.assertEqual(e.contrast(1, 0, "fused"), (F(-5, 4), F(-3, 4)))
        self.assertEqual(e.contrast(1, 0, "best_single"), (F(-3, 2), F(-1, 2)))
        r = analyze_case(crossing_case())
        self.assertEqual(r["candidates"][0]["modes"]["fused"]["gain_lower"], F(3, 4))
        self.assertEqual(r["candidates"][0]["modes"]["best_single"]["gain_lower"], F(1, 2))

    def test_strict_reduced_gradient_interface_minimax_witness(self):
        c = {"A": "3/2", "incumbent": "1/4", "mu": "1", "L": "4",
             "delta": "0", "tau": "10", "omega": "10",
             "old_optimum_lower": "-10",
             "payloads": [{"a": "1/4", "W": "0", "U": "0",
                           "p_lower": "-2", "p_upper": "-2",
                           "g_lower": "-2", "g_upper": "-2"},
                          {"a": "5/4", "W": "-25/24", "U": "-25/24",
                           "p_lower": "-1/2", "p_upper": "-1/2",
                           "g_lower": "-1/2", "g_upper": "-1/2"}],
             "candidates": [{"b": "11/8"}]}
        e = RationalCertificate(c)
        # These are derivative-interface contrasts only. Exact anchor values
        # permit other comparisons and are NOT asserted to retain strictness.
        self.assertEqual(e.fused_minimizer(), F(11, 8))
        self.assertEqual(e.contrast(F(1, 4), F(11, 8), "fused")[1], F(-103, 96))
        self.assertEqual(e.contrast(F(1, 4), F(11, 8), "best_single")[1], F(-33, 32))
        self.assertEqual(F(-33, 32)-F(-103, 96), F(1, 24))

    def test_all_ordered_rational_contrasts_enclose_original_quadratic(self):
        e = RationalCertificate(crossing_case())
        for ai in range(17):
            for bi in range(17):
                a, b = F(ai, 16), F(bi, 16)
                true = b*b-a*a
                for mode in ("fused", "best_single"):
                    lo, hi = e.contrast(a, b, mode)
                    self.assertLessEqual(lo, true)
                    self.assertLessEqual(true, hi)
        for i in range(65):
            x = F(i, 64)
            self.assertLessEqual(e.absolute_lower(x), x*x)
            self.assertLessEqual(x*x, e.absolute_upper_q(x, "fused"))

    def test_nonconvex_interval_slope_support_global_minimum(self):
        c = quadratic_case()
        c["incumbent"] = "1/2"
        c["payloads"] = [{"a": "1/2", "W": "0", "U": "0",
                          "p_lower": "-1", "p_upper": "1",
                          "g_lower": "0", "g_upper": "0"}]
        # The raw lower support is d^2-|d|. Assuming convexity would be wrong.
        e = RationalCertificate(c)
        self.assertEqual(e.support_minimum, F(-1, 4))
        self.assertEqual(e.support_minimizers, [F(0), F(1)])

    def test_finite_radius_recovery_rejects_tighter_unproved_interval(self):
        c = quadratic_case()
        c["gradient_rule"] = "r122-finite-radii"
        RationalCertificate(c)
        c["payloads"][0]["g_lower"] = "1"
        with self.assertRaises(ValueError):
            RationalCertificate(c)

    def test_exact_feasible_rounding_and_failed_query_charge(self):
        c = quadratic_case()
        c["rounding_bits"] = 4
        c["safe_capacity"] = "15/16"
        c["candidates"] = [{"b": "5/16", "proposal_raw": "1/3"}]
        c["query_ledger"] = [{"query_id": "first", "charge": "128", "completed": True},
                              {"query_id": "failed", "charge": "256", "completed": False}]
        c["query_charge"] = "384"
        c["query_budget"] = "384"
        result = analyze_case(c)
        self.assertEqual(result["budget"]["charge"], 384)
        self.assertEqual(result["budget"]["failed_charged_queries"], 1)
        c["query_charge"] = "128"
        with self.assertRaises(ValueError):
            analyze_case(c)

    def test_bad_claim_and_inconsistent_payload_fail(self):
        c = quadratic_case()
        c["candidates"][0]["modes"] = {"fused": {"regret_upper": "0"}}
        report = validate_case(c)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["compared_fields"], 1)
        c = crossing_case()
        c["payloads"][1]["g_lower"] = "100"
        c["payloads"][1]["g_upper"] = "101"
        with self.assertRaises(ValueError):
            RationalCertificate(c)

    def test_outside_domain_and_duplicate_query_are_rejected(self):
        c = quadratic_case()
        c["candidates"] = [{"b": "-1/100"}]
        with self.assertRaises(ValueError):
            analyze_case(c)
        c = quadratic_case()
        q = {"query_id": "duplicate", "charge": "1"}
        c["query_ledger"] = [q, deepcopy(q)]
        with self.assertRaises(ValueError):
            analyze_case(c)


if __name__ == "__main__":
    unittest.main(verbosity=2)
