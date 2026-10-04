"""Execution-control fixtures only: no policy fitting or economic simulation."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

import worker
import method_statistics  # Load before sys.modules fixtures restore their snapshot.


class ActualStoppingTests(unittest.TestCase):
    def exercise(self, lowers, *, fail_training=None, fail_check=None, fail_final=False):
        events = []
        source, fingerprint = "a" * 40, "b" * 64
        protocol = json.loads((Path(__file__).resolve().parents[1] / "PROTOCOL.json").read_text())
        protocol["status"] = "frozen_before_confirmatory_execution"
        core = ModuleType("training_core")
        verifier = ModuleType("actor_verifier")

        class FixtureRun:
            def __init__(self, p, dimension, seed, method, out, metadata):
                self.p, self.d, self.seed, self.method = p, dimension, seed, method
                self.metadata = metadata
                self.method_fingerprint = metadata["method_fingerprint"]
                self.counters = {"simulator_transitions": 0}
                self.history, self.train_states, self.stage = [], None, 0

            def advance(self, stage):
                events.append(("train", stage))
                self.counters["simulator_transitions"] += 5
                if stage == fail_training:
                    raise FloatingPointError("synthetic training failure")
                self.stage = stage
                row = {"stage": stage, "counters": dict(self.counters)}
                self.history.append(row)
                return row

            def save_checkpoint(self, path):
                state = dict(self.metadata, method_id=self.method, stage=self.stage,
                             primitives_sha256=self.p["design"]["primitives_sha256"], analytic=False)
                worker.write(path, state)
                return worker.sha(path)

        def load_candidate(path):
            state = json.loads(Path(path).read_text())
            return SimpleNamespace(is_analytical_schedule=state["analytic"]), None, state

        def save_fallback(path, p, dimension, seed, method_id, *, metadata, failure, counters):
            events.append(("fallback", None))
            worker.write(path, dict(metadata, analytic=True, stage=0,
                                    primitives_sha256=p["design"]["primitives_sha256"]))

        def verify(actor, *, dimension, steps, paths, noise_seed, event_alpha,
                   primitives, out, record_id, metadata):
            final = metadata["is_confirmation"]
            stage = metadata.get("stage")
            events.append(("final" if final else "check", stage))
            if (not final and stage == fail_check) or (final and fail_final):
                raise ArithmeticError("synthetic verification failure")
            value = 0. if metadata["analytic_schedule"] else (.0007 if final else lowers[stage-1])
            out = Path(out)
            out.mkdir(parents=True, exist_ok=True)
            raw_path, json_path = record_id + ".fixture", record_id + ".json"
            (out / raw_path).write_text("unit-test fixture; no simulated economic observations\n")
            row = dict(metadata, lower=value, upper=value + .0001, mean=value,
                       clipping_threshold=1., bias=0., clipping_tail=0.,
                       raw_path=raw_path, json_path=json_path,
                       work={"verification_transitions": 7, "verification_paths": 2,
                             "actor_forward_rows": 3, "constants_seconds": .1})
            worker.write(out / json_path, row)
            return row

        core.TrainingRun = FixtureRun
        core.load_candidate = load_candidate
        core.save_fallback = save_fallback
        core.stream_seed = lambda seed, d, domain, stage=0: int.from_bytes(
            hashlib.sha256(f"{seed}/{d}/{domain}/{stage}".encode()).digest()[:8], "big")
        verifier.verify = verify
        seed = protocol["design"]["seeds"][0]
        with tempfile.TemporaryDirectory(prefix="nbo-r15-execution-fixture-") as temp:
            temp = Path(temp)
            worker.write(temp / "PROTOCOL.json", protocol)
            with patch.dict(os.environ, {"NBO_R15_NUMERICAL_SOURCE_COMMIT": source,
                                         "NBO_R15_METHOD_FINGERPRINT": fingerprint}), \
                 patch.dict("sys.modules", {"training_core": core, "actor_verifier": verifier}):
                if fail_final:
                    with self.assertRaisesRegex(RuntimeError, "no valid final confirmation"):
                        worker.execute(temp / "PROTOCOL.json", f"d10_s{seed}", "nbo", temp / "result")
                else:
                    worker.execute(temp / "PROTOCOL.json", f"d10_s{seed}", "nbo", temp / "result")
            result = json.loads((temp / "result/RESULT.json").read_text())
        return events, result

    def test_first_attainment_prevents_future_training_and_uses_fresh_final_bank(self):
        events, result = self.exercise([.0006, 1., 1.])
        self.assertEqual(events, [("train", 1), ("check", 1), ("final", None)])
        self.assertTrue(result["complete"] and result["attained_online"])
        self.assertEqual(result["counters"]["total_state_transitions"], 19)
        self.assertNotEqual(result["online_checks"][0]["noise_key"], result["final_confirmation"]["noise_key"])

    def test_unattained_stream_executes_all_registered_checks(self):
        events, result = self.exercise([0., .0002, .0004])
        self.assertEqual(events, [("train", 1), ("check", 1), ("train", 2), ("check", 2),
                                  ("train", 3), ("check", 3), ("final", None)])
        self.assertFalse(result["attained_online"])
        self.assertEqual(result["attempted_online_checks"], 3)
        # A favorable independent final result must not relabel a previous
        # unsuccessful online process as an actual successful early stop.
        self.assertGreater(result["final_confirmation"]["lower"], .0005)

    def test_failed_fit_keeps_seed_costs_and_exact_schedule_fallback(self):
        events, result = self.exercise([0., 0., 0.], fail_training=2)
        self.assertEqual(events, [("train", 1), ("check", 1), ("train", 2), ("fallback", None), ("final", None)])
        self.assertTrue(result["complete"] and result["fallback"])
        self.assertFalse(result["attained_online"])
        self.assertTrue(result["final_confirmation"]["analytic_schedule"])
        self.assertEqual(result["training_counters"]["simulator_transitions"], 10)
        self.assertEqual(result["final_confirmation"]["lower"], 0.)

    def test_failed_check_is_retained_and_never_creates_attainment(self):
        events, result = self.exercise([1., .0006, 1.], fail_check=1)
        self.assertEqual(events, [("train", 1), ("check", 1), ("train", 2), ("check", 2), ("final", None)])
        self.assertEqual(result["attainment_stage"], 2)
        self.assertFalse(result["verification_counters_complete"])
        self.assertEqual(result["completed_online_checks"], 1)

    def test_final_failure_is_preserved_and_fails_completeness(self):
        events, result = self.exercise([.0006, 0., 0.], fail_final=True)
        self.assertFalse(result["complete"])
        self.assertTrue(result["attained_online"])
        self.assertIsNone(result["final_confirmation"])
        self.assertEqual(events[-1], ("final", None))


if __name__ == "__main__":
    unittest.main()
