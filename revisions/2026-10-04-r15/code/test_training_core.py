"""Manufactured/global-grid and common-information tests, not payoff gates."""
from __future__ import annotations
import copy
import json
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np
import torch

import training_core as core


class TrainingCoreContracts(unittest.TestCase):
    def setUp(self):
        self.original_params = dict(core.legacy.P, CHI=core.legacy.CHI)
        self.protocol = json.loads((Path(__file__).resolve().parents[1]/"PROTOCOL.json").read_text())
        self.protocol["status"] = "manufactured_functional_fixture"
        self.protocol["training"].update(global_steps=4, cumulative_replay_states=[8, 16, 24], batch=4,
            critic_adam_updates_per_stage=2, critic_time_updates_per_stage=2,
            actor_updates_per_stage=[2, 2, 2], direct_updates_per_stage=[2, 2, 2], hjb_updates_per_stage=[2, 2, 2])
        self.protocol["training"]["critic_lbfgs"].update(max_iter=2, max_eval=3)

    def tearDown(self):
        core.configure_primitives(self.original_params)

    def test_global_grid_excludes_current_reward_and_uses_remaining_nodes(self):
        params = dict(self.protocol["design"]["primitives"], coupling=0.)
        weights = core.training_weights(4)
        d, h = 3, .25
        nodes = torch.arange(4)
        y = torch.tensor([[.2, -.1, .5], [.0, .3, -.2], [.5, -.5, .0], [.2, .1, -.3]])
        post = torch.cat([((nodes+1)*h)[:, None], y], 1)
        B = torch.from_numpy(core.old.coupling(d))
        value, q = core.postdecision_target(post, nodes, torch.zeros(4, 4, d+1), params, weights, B)
        coefficient = params["CHI"]*math.exp(-params["discount"]*params["T"])
        dispersion = ((y-y.mean(1, keepdim=True))**2).mean(1)
        expected_value = -coefficient*dispersion
        for k in range(4):
            for j in range(k+1, 4):
                pi = weights["M"][j]/h
                expected_value[k] += weights["A"][j]*(torch.log(pi)-params["adjustment"]/2*pi*pi)-weights["B"][j]*pi
        expected_q = -2*coefficient*(y-y.mean(1, keepdim=True))
        np.testing.assert_allclose(value[:, 0], expected_value, rtol=1e-12, atol=2e-14)
        np.testing.assert_allclose(q, expected_q, rtol=1e-12, atol=2e-14)

    def test_four_antithetic_last_node_costate(self):
        params = core.configure_primitives(self.protocol["design"]["primitives"])
        weights = core.training_weights(4)
        B = torch.from_numpy(core.old.coupling(3))
        post = torch.tensor([[1., .3, -.1, .2], [1., -.4, .2, .7]])
        _, q = core.postdecision_labels(post, torch.full((2,), 3, dtype=torch.long), 9983, params, weights, B)
        expected = -2*params["CHI"]*math.exp(-params["discount"])*(post[:, 1:]-post[:, 1:].mean(1, keepdim=True))
        np.testing.assert_allclose(q.mean(0), expected, rtol=1e-12, atol=2e-14)

    def test_time_level_cannot_change_spatial_costate(self):
        params = self.protocol["design"]["primitives"]
        critic = core.SplitCritic(3, params, kind="postdecision", step=.25)
        x = torch.tensor([[.25, .3, -.1, .2], [.75, -.4, .2, .7]])
        before = core.first_jet(critic, x, create_graph=False)[3]
        with torch.no_grad():
            for p in critic.time.parameters():
                p.add_(torch.randn_like(p)*3)
        after = core.first_jet(critic, x, create_graph=False)[3]
        np.testing.assert_array_equal(before, after)

    def test_complete_method_interfaces_and_common_labels(self):
        with tempfile.TemporaryDirectory(prefix="nbo-r15-contract-") as tmp:
            runs = {}
            metadata = dict(protocol_sha256="fixture-protocol", source_commit="fixture-source", method_fingerprint="fixture-full-method")
            for method in self.protocol["design"]["methods"]:
                run = core.TrainingRun(self.protocol, 3, 730019, method, Path(tmp)/method, metadata)
                row = run.advance(1)
                if method == "neural_hjb":
                    self.assertEqual(len(row["hjb_training_losses"]), 2)
                    self.assertEqual(row["negative_hjb_losses"], sum(v["loss"] < 0 for v in row["hjb_training_losses"]))
                file = Path(tmp)/(method+".pt")
                run.save_checkpoint(file)
                actor, critic, state = core.load_candidate(file)
                self.assertEqual(state["protocol_sha256"], metadata["protocol_sha256"])
                self.assertEqual(state["method_fingerprint"], metadata["method_fingerprint"])
                self.assertEqual(state["numerical_source_commit"], metadata["source_commit"])
                with torch.no_grad():
                    np.testing.assert_array_equal(actor(run.train_states), run.actor(run.train_states))
                runs[method] = run
            np.testing.assert_array_equal(runs["nbo"].q_replicates, runs["raw_costate"].q_replicates)
            self.assertEqual(runs["nbo"].counters["simulator_transitions"], runs["raw_costate"].counters["simulator_transitions"])
            self.assertEqual(runs["nbo"].counters["actor_updates"], runs["raw_costate"].counters["actor_updates"])
            fallback = Path(tmp)/"fallback.pt"
            core.save_fallback(fallback, self.protocol, 3, 730019, "neural_hjb", metadata=metadata, failure="manufactured failure")
            actor, _, state = core.load_candidate(fallback)
            self.assertTrue(actor.is_analytical_schedule)
            self.assertTrue(state["fallback"])
            self.assertEqual(state["method_fingerprint"], metadata["method_fingerprint"])


if __name__ == "__main__":
    unittest.main()
