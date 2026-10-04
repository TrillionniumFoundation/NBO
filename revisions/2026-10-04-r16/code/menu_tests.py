"""Manufactured identities and lifecycle tests; no confirmatory menu fitting.

The tiny optimizer test uses an artificial deterministic, zero-coupling economy
outside the four registered designs. It tests persistence and cache reuse, not
method efficacy. Registered query catalogs are only checked for identity/domain.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

import numpy as np
import torch

from menu_economy import (MenuEconomy, array_hash, coefficient_proposal, fixed_queries,
    load_economy, noise_bank, scalar_query_spec, task_tensors, write_json)
from menu_methods import METHODS, MenuRun, ScalarContinuation, TaskActor, save_shards
import menu_worker

R16 = Path(__file__).resolve().parents[1]


def manufactured(coupling=0., sigma=.2):
    p = dict(T=1., discount=.04, productivity=.1, coupling=coupling,
        idiosyncratic_sigma=sigma, common_sigma=.1 if sigma else 0., adjustment=.2,
        lower=.02, upper=2., CHI=.07)
    co = coefficient_proposal(p, 4)
    c = dict(id="manufactured_identity_only", primitives=p, steps=4, coefficients=co)
    B = np.asarray([[.8, -.6, 0.], [.2, .7, np.sqrt(.47)], [-.5, .5, np.sqrt(.5)]])
    return MenuEconomy(c, 3, B)


def tiny_protocol(e):
    states = np.asarray([[.1, -.1, .2], [-.3, .2, .1]])
    tasks = [dict(id="manufactured_a", utility_weight=1., adjustment=.2, lower=.02, upper=2.),
             dict(id="manufactured_b", utility_weight=.9, adjustment=.3, lower=.02, upper=.6)]
    return dict(methods=list(METHODS), tasks=tasks,
        query_catalogs={"3": dict(states=states.tolist(), states_sha256=array_hash(states))},
        training=dict(cumulative_replay_states=[4, 8], label_antithetic_paths=2,
            field_width=4, actor_width=4, batch_size=4, field_learning_rate=.003,
            field_adam_updates_per_stage=1, field_lbfgs_iterations=2, field_lbfgs_evaluations=3,
            actor_learning_rate=.003, actor_updates_per_stage=1, query_learning_rate=.06,
            query_updates=2, query_lbfgs_iterations=2, query_lbfgs_evaluations=3,
            saa_antithetic_paths=[2, 4]),
        scalar_accuracy=dict(state_index=0, task_index=0, action_radius=.1, candidate_grid_points=5))


class EconomicIdentities(unittest.TestCase):
    def test_antithetic_quadratic_costate_is_exact(self):
        e = manufactured()
        x = torch.tensor([[.2, -.3, .1], [-.4, .2, .5]])
        z = noise_bank(e, 2, 101, 4)
        _, q = e.labels(x, z)
        np.testing.assert_allclose(q.mean(0).numpy(), e.base_costate(x).numpy(), rtol=0, atol=2e-15)

    def test_known_quadratic_difference_removes_all_randomness_when_uncoupled(self):
        e = manufactured()
        x = torch.tensor([[.2, -.3, .1], [-.4, .2, .5]])
        y = x+torch.tensor([[.1, -.2, .05], [.03, -.1, .2]])
        z = noise_bank(e, 2, 103, 8)
        dx = e.continuation(x, z).reshape(4, 2, 2, 1).mean(1)
        dy = e.continuation(y, z).reshape(4, 2, 2, 1).mean(1)
        expected = e.base_value(x)-e.base_value(y)
        np.testing.assert_allclose((dx-dy).numpy(), expected[None].expand(4, -1, -1).numpy(), rtol=0, atol=3e-15)

    def test_cache_task_invariance_and_future_invalidation(self):
        e = manufactured(coupling=.2)
        x = torch.tensor([[.2, -.3, .1]])
        z = noise_bank(e, 1, 109, 2)
        key = e.cache_key(x, z)
        protocol = tiny_protocol(e)
        # Current task changes do not enter the continuation object.
        a = torch.tensor([[.4, .5, .6]])
        old = e.current_payoff(x, a, task_tensors(protocol["tasks"], torch.tensor([0])))
        new = e.current_payoff(x, a, task_tensors(protocol["tasks"], torch.tensor([1])))
        self.assertFalse(torch.equal(old, new))
        self.assertEqual(key, e.cache_key(x, z))
        changed = copy.deepcopy(e.calibration)
        changed["coefficients"]["schedule"][1] *= .99
        other = MenuEconomy(changed, 3, e.B)
        self.assertNotEqual(key, other.cache_key(x, z))
        self.assertNotEqual(key, e.cache_key(x+.01, z))

    def test_finite_Q_chain_rule_has_correct_normalization(self):
        e = manufactured(coupling=.2)
        y = torch.tensor([[.2, -.3, .1], [-.4, .2, .5]])
        a = torch.tensor([[.4, .6, .5], [.3, .8, .4]], requires_grad=True)
        task = task_tensors(tiny_protocol(e)["tasks"], torch.tensor([0, 1]))
        z = noise_bank(e, 2, 127, 4)
        full = e.current_payoff(y, a, task)+e.continuation(e.postdecision(y, a), z).mean(0)
        derivative = e.dimension*torch.autograd.grad(full.sum(), a)[0]
        _, q = e.labels(e.postdecision(y, a.detach()), z)
        predicted = (e.A[0]*task["utility_weight"]/a.detach()
            - e.A[0]*task["adjustment"]*a.detach().mean(1, keepdim=True)-e.W[0]-e.h*q.mean(0))
        np.testing.assert_allclose(derivative.numpy(), predicted.numpy(), rtol=0, atol=3e-15)

    def test_scalar_field_gradient_matches_value(self):
        e = manufactured(coupling=.2)
        torch.manual_seed(131)
        field = ScalarContinuation(e, 4)
        with torch.no_grad():
            field.space[-1].weight.fill_(.07)
        x = torch.tensor([[.2, -.3, .1]])
        q = field.costate(x).numpy()[0]
        eps = 1e-5
        approximate = []
        with torch.no_grad():
            for j in range(3):
                step = torch.zeros_like(x); step[0, j] = eps
                approximate.append(float((field(x+step)-field(x-step))/(2*eps))*3)
        np.testing.assert_allclose(q, approximate, rtol=0, atol=1e-10)

    def test_temporary_constraint_is_enforced_by_materialized_actor(self):
        e = manufactured()
        p = tiny_protocol(e)
        tasks = task_tensors(p["tasks"], torch.tensor([0, 1]))
        actor = TaskActor(e, 4)
        y = torch.tensor([[.2, -.3, .1], [-.4, .2, .5]])
        for v in [-100., 100.]:
            with torch.no_grad():
                actor.space[-1].bias.fill_(v)
                a = actor(y, tasks)
            self.assertTrue(bool(torch.all(a >= tasks["lower"])))
            self.assertTrue(bool(torch.all(a <= tasks["upper"])))


class PersistenceAndSource(unittest.TestCase):
    def test_lossless_pair_cache_shards(self):
        z = np.random.default_rng(137).normal(size=(3, 4, 9, 4))
        q = np.random.default_rng(139).normal(size=(6, 9, 3))
        with tempfile.TemporaryDirectory() as directory:
            path = save_shards(Path(directory)/"bank", dict(independent_innovations=z, costate_replicates=q),
                dict(independent_innovations=2, costate_replicates=1), 4)
            manifest = json.loads(path.read_text())
            shards = [np.load(Path(directory)/x["path"]) for x in manifest["parts"]]
            np.testing.assert_array_equal(np.concatenate([s["independent_innovations"] for s in shards], axis=2), z)
            np.testing.assert_array_equal(np.concatenate([s["costate_replicates"] for s in shards], axis=1), q)
            for s in shards: s.close()

    def test_all_methods_keep_two_tiny_manufactured_prefixes(self):
        e = manufactured(sigma=0.)
        protocol = tiny_protocol(e)
        with tempfile.TemporaryDirectory() as directory:
            label_keys = {}
            for method in METHODS:
                run = MenuRun(e, protocol, method, 149, Path(directory)/method)
                first = run.advance(1)
                cached = run.saa_innovations.clone() if method == "raw_saa" else None
                second = run.advance(2)
                self.assertEqual(second["stage"], 2)
                self.assertTrue((Path(directory)/method/"actions_stage1.npz").is_file())
                self.assertTrue((Path(directory)/method/"actions_stage2.npz").is_file())
                if method in ["nbo_scalar", "vector_costate"]:
                    label_keys[method] = first["new_cache"]["cache_key"]
                if method == "raw_saa":
                    self.assertTrue(torch.equal(cached, run.saa_innovations[:len(cached)]))
                    self.assertEqual(run.counters["independent_gaussian_scalars_generated"], 2*4*4*4)
                if method == "nbo_scalar":
                    candidate = json.loads((Path(directory)/method/"SCALAR_CANDIDATE.json").read_text())
                    self.assertTrue(0 <= candidate["candidate_s"] <= 1)
                    self.assertTrue(candidate["class_selected_before_fitting"])
            self.assertEqual(label_keys["nbo_scalar"], label_keys["vector_costate"])

    def test_bound_manifest_rejects_changed_source_bytes(self):
        # A synthetic source identity tests validation only. No scientific
        # fitting is launched from this test manifest.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root/"example.py"; source.write_text("x = 1\n")
            protocol_path = root/"protocol.json"
            protocol = dict(execution=dict(source_files=["example.py", "protocol.json"]))
            protocol_path.write_text(json.dumps(protocol))
            items = {}
            for path in [source, protocol_path]:
                data = path.read_bytes()
                items[path.name] = dict(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
                    git_blob_sha=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest())
            manifest = root/"source_manifest.json"
            manifest.write_text(json.dumps(dict(source_commit="0"*40, files=items)))
            env = dict(NBO_R16_MENU_SOURCE_COMMIT="0"*40,
                NBO_R16_MENU_SOURCE_MANIFEST=str(manifest),
                NBO_R16_MENU_SOURCE_MANIFEST_SHA256=hashlib.sha256(manifest.read_bytes()).hexdigest())
            with mock.patch.object(menu_worker, "ROOT", root), mock.patch.dict(os.environ, env):
                self.assertEqual(menu_worker.verify_source(protocol_path, protocol)[0], "0"*40)
                source.write_text("x = 2\n")
                with self.assertRaises(RuntimeError):
                    menu_worker.verify_source(protocol_path, protocol)

    def test_fallback_scalar_is_declared_and_keeps_seed(self):
        e = manufactured(sigma=0.)
        protocol = tiny_protocol(e)
        args = type("Args", (), dict(method="nbo_scalar", seed=157))()
        with tempfile.TemporaryDirectory() as directory:
            menu_worker.fallback_scalar(args, protocol, e, Path(directory), dict(type="manufactured_failure"))
            z = json.loads((Path(directory)/"SCALAR_CANDIDATE.json").read_text())
            self.assertEqual(z["seed"], 157)
            self.assertTrue(z["failed_fit"])
            self.assertTrue(0 <= z["candidate_s"] <= 1)


class FrozenDesign(unittest.TestCase):
    def test_protocol_complete_family_and_disjoint_alpha(self):
        p = json.loads((R16/"protocols/menu_protocol.json").read_text())
        events = len(p["calibrations"])*len(p["dimensions"])*len(p["training"]["cumulative_replay_states"])*(5+4)
        self.assertEqual(events, 216)
        self.assertEqual(p["confidence"]["event_count"], events)
        self.assertAlmostEqual(p["confidence"]["alpha"]+p["scalar_accuracy"]["alpha"], .02)
        self.assertEqual(p["scalar_accuracy"]["event_count"], 128)
        self.assertEqual(p["confidence"]["economic_margin"], .0001)
        self.assertEqual(len(p["training_streams"]["seeds"]), 16)
        for d in p["dimensions"]:
            q = fixed_queries(p, d)
            self.assertEqual(q["states"].shape, (384, d))
            for c in p["calibrations"]:
                e = load_economy(p, c["id"], d)
                spec = scalar_query_spec(p, e)
                self.assertEqual(spec["task"]["utility_weight"], 1.)
                self.assertEqual(spec["task"]["adjustment"], .2)

    def test_every_exploratory_result_and_failure_is_retained(self):
        archive = R16/"results/exploratory/menu"
        manifest = json.loads((archive/"MANIFEST.json").read_text())
        for name, info in manifest["files"].items():
            path = archive/name
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), info["sha256"])
            self.assertEqual(path.stat().st_size, info["bytes"])
        rows = json.loads((archive/"RF_REPLAY_PILOT.json").read_text())["rows"]
        self.assertEqual(len(rows), 12)
        self.assertTrue(all(r["scalar_minus_vector_test_loss"] > 0 for r in rows))
        self.assertIn("AttributeError", (archive/"MENU_EXPLORATORY_PILOT.first_attempt.stdout").read_text())


class InterruptedPrefixRecovery(unittest.TestCase):
    def exercise_parent_kill_window(self, variant):
        """Manufacture only interrupted file writes; no scientific fit runs."""
        e = manufactured(sigma=0.)
        p = tiny_protocol(e)
        p.update(dimensions=[3], calibrations=[e.calibration],
            coupling_matrices={"3": dict(values=e.B.tolist(), sha256=array_hash(e.B))},
            training_streams=dict(seeds=[173]), execution=dict(method_timeout_seconds=1))
        with tempfile.TemporaryDirectory() as directory:
            top = Path(directory); out = top/"fit"
            protocol_path = top/"protocol.json"; protocol_path.write_text(json.dumps(p))
            args = type("Args", (), dict(protocol=str(protocol_path), calibration=e.calibration["id"],
                dimension=3, seed=173, method="raw_actor", out=str(out)))()
            queries = fixed_queries(p, 3)
            originals = {}
            def killed_child(command, **kwargs):
                action_path = out/"actions_stage1.npz"
                np.savez_compressed(action_path, actions=np.full((4, 3), .3),
                    **{k: queries[k] for k in ["states", "task_id", "state_id", "utility_weight", "adjustment", "lower", "upper"]})
                row = dict(stage=1, method="raw_actor", actions_file=action_path.name,
                    actions_sha256=menu_worker.sha(action_path), counters=dict(actor_updates=1),
                    continuation_sha256=e.continuation_sha256, query_catalog_sha256=queries["catalog_sha256"])
                record_path = out/"stage1.json"
                if variant in ["sealed", "action_hash_changed", "wrong_target"]:
                    row["fallback"] = False
                    menu_worker.seal_stage(out, row, args, e, queries,
                        int(kwargs["env"]["NBO_R16_MENU_PARENT_PERF_NS"]), "0"*40)
                    if variant == "action_hash_changed":
                        action_path.write_bytes(action_path.read_bytes()+b"interrupted-tail")
                    elif variant == "wrong_target":
                        z = json.loads(record_path.read_text()); z["continuation_sha256"] = "f"*64
                        menu_worker.write(record_path, z)
                elif variant == "partial_json":
                    record_path.write_bytes(b'{"stage": 1, "method":')
                    (out/".stage1.json.abandoned.tmp").write_bytes(b'{"sealed":tr')
                else:
                    # Exact bug window: advance() has emitted its draft but
                    # the child has not yet added fallback/clock or sealed it.
                    record_path.write_text(json.dumps(row))
                originals["json"] = record_path.read_bytes()
                originals["actions"] = action_path.read_bytes()
                return type("Result", (), dict(returncode=-9))()
            with mock.patch.object(menu_worker, "verify_source", return_value=("0"*40, {})), \
                    mock.patch.object(menu_worker.subprocess, "run", side_effect=killed_child):
                menu_worker.parent(args)
            row, reason = menu_worker.preserved_prefix(out, 1, args, e, queries, "0"*40)
            self.assertIsNone(reason)
            self.assertTrue(row["sealed"])
            work = json.loads((out/"FIT_WORK.json").read_text())
            self.assertTrue(work["failed_fit"])
            self.assertFalse(work["counters_complete"])
            if variant == "sealed":
                self.assertFalse(row["fallback"])
                self.assertEqual((out/"stage1.json").read_bytes(), originals["json"])
                self.assertEqual((out/"actions_stage1.npz").read_bytes(), originals["actions"])
                self.assertFalse((out/"failure_recovery/stage1").exists())
            else:
                self.assertTrue(row["fallback"])
                recovery = out/row["recovery_archive"]
                self.assertEqual((recovery/"stage1.json").read_bytes(), originals["json"])
                self.assertEqual((recovery/"actions_stage1.npz").read_bytes(), originals["actions"])
                if variant == "partial_json":
                    self.assertEqual((recovery/".stage1.json.abandoned.tmp").read_bytes(), b'{"sealed":tr')
            second, reason = menu_worker.preserved_prefix(out, 2, args, e, queries, "0"*40)
            self.assertIsNone(reason)
            self.assertTrue(second["fallback"])
            self.assertEqual(second["seed"], 173)

    def test_unsealed_partial_mismatched_prefixes_are_archived_and_recovered(self):
        for variant in ["unsealed", "partial_json", "action_hash_changed", "wrong_target"]:
            with self.subTest(window=variant):
                self.exercise_parent_kill_window(variant)

    def test_completed_sealed_prefix_remains_byte_identical_after_child_kill(self):
        self.exercise_parent_kill_window("sealed")

    def test_atomic_seal_failure_cannot_replace_previous_record(self):
        for writer in [menu_worker.write, write_json]:
            with self.subTest(writer=writer.__module__), tempfile.TemporaryDirectory() as directory:
                path = Path(directory)/"stage1.json"
                before = b'{"old_complete_record":true}\n'; path.write_bytes(before)
                with mock.patch.object(menu_worker.os, "replace", side_effect=OSError("manufactured pre-rename interruption")):
                    with self.assertRaises(OSError):
                        writer(path, dict(sealed=True))
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(list(Path(directory).glob("*.tmp")), [])

    def scalar_fixture(self, directory):
        e = manufactured(sigma=0.); p = tiny_protocol(e)
        args = type("Args", (), dict(method="nbo_scalar", seed=181))()
        grid = np.linspace(0., 1., 5); values = -np.square(grid-.25)[:, None]
        row = scalar_query_spec(p, e)
        row.update(candidate_s=.25, selected_grid_index=1, candidate_grid_points=5,
            selected_critic_values_sha256=array_hash(values), failed_fit=False,
            stage=2, seed=181, primary_vector_candidate_unchanged=True)
        out = Path(directory)
        np.savez_compressed(out/"scalar_candidate_grid.npz", scalar_parameters=grid, critic_values=values)
        menu_worker.write(out/"SCALAR_CANDIDATE.json", row)
        return e, p, args, row

    def test_interrupted_scalar_metadata_and_grid_are_archived_before_same_seed_fallback(self):
        for variant in ["partial_json", "corrupt_grid", "wrong_seed", "orphan_grid"]:
            with self.subTest(window=variant), tempfile.TemporaryDirectory() as directory:
                out = Path(directory); e, p, args, row = self.scalar_fixture(directory)
                record = out/"SCALAR_CANDIDATE.json"; grid = out/"scalar_candidate_grid.npz"
                if variant == "partial_json":
                    record.write_bytes(b'{"candidate_s":')
                    (out/".SCALAR_CANDIDATE.json.abandoned.tmp").write_bytes(b'{"seed":18')
                elif variant == "corrupt_grid":
                    grid.write_bytes(b'PK\x03\x04invalid-interrupted-grid')
                elif variant == "wrong_seed":
                    row["seed"] = 182; menu_worker.write(record, row)
                else:
                    record.unlink()
                originals = {path.name:path.read_bytes() for path in out.iterdir() if path.is_file()}
                menu_worker.fallback_scalar(args, p, e, out, dict(type="manufactured_kill"))
                fallback = json.loads(record.read_text())
                self.assertEqual(fallback["seed"], 181)
                self.assertTrue(fallback["failed_fit"])
                self.assertTrue(0 <= fallback["candidate_s"] <= 1)
                archive = out/fallback["recovery_archive"]
                for name, data in originals.items():
                    self.assertEqual((archive/name).read_bytes(), data)
                self.assertFalse(grid.exists())
                # A durable fallback is itself a completed prefix on recovery.
                before = record.read_bytes()
                menu_worker.fallback_scalar(args, p, e, out, dict(type="second_recovery"))
                self.assertEqual(record.read_bytes(), before)

    def test_completed_scalar_candidate_and_grid_remain_byte_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory); e, p, args, row = self.scalar_fixture(directory)
            before = {path.name:path.read_bytes() for path in out.iterdir()}
            menu_worker.fallback_scalar(args, p, e, out, dict(type="later_child_kill"))
            self.assertEqual({path.name:path.read_bytes() for path in out.iterdir()}, before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
