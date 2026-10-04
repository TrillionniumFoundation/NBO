"""Synthetic Git/source controls; no fitted-policy or simulation outcomes."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import pipeline_mechanism as pipe


class MechanismSourceControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="nbo-r15-mechanism-git-fixture-")
        self.addCleanup(self.temp.cleanup)
        self.temp_root = Path(self.temp.name)
        self.repo = self.temp_root / "repo"
        self.repo.mkdir()
        self.real = Path(pipe.__file__).resolve().parents[3]
        self.main_files = [pipe.PRIMARY_PROTOCOL, pipe.PROTOCOL,
                           pipe.R15 + "/code/training_core.py"]
        for name in self.main_files:
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.real / name, target)
        self.git("init", "--quiet")
        self.git("config", "user.name", "Synthetic source-control fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "Synthetic primary source; no experiment")
        self.primary = self.git("rev-parse", "HEAD").decode().strip()
        primary_inventory = {name: {"sha256": pipe.sha(self.repo / name)} for name in self.main_files}
        primary_manifest = {"numerical_source_commit": self.primary, "github_run_id": "1",
                            "protocol_sha256": pipe.sha(self.repo / pipe.PRIMARY_PROTOCOL),
                            "files": primary_inventory, "method_fingerprints": {"nbo": {"sha256": "b"*64}}}
        self.primary_bundle = self.temp_root / "primary-bundle"
        pipe.write(self.primary_bundle / "SOURCE_MANIFEST.json", primary_manifest)
        for name in pipe.source_files(self.real):
            if name in self.main_files:
                continue
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if (self.real / name).is_file():
                shutil.copyfile(self.real / name, target)
            else:
                # A missing, still-being-authored numerical module is a plain
                # fixture input here. It is never imported or executed.
                target.write_text('"""Synthetic packaging fixture; not a numerical producer."""\n')
        execution = pipe.read(self.repo / pipe.EXECUTION)
        execution["primary_numerical_source_commit"] = self.primary
        execution["primary_actions_run_id"] = 1
        pipe.write(self.repo / pipe.EXECUTION, execution)
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "Synthetic independent mechanism source; no assessment")
        self.source = self.git("rev-parse", "HEAD").decode().strip()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], stderr=subprocess.PIPE)

    def test_source_archive_retains_two_distinct_sources_and_rejects_tampering(self):
        bundle = self.temp_root / "bundle"
        pipe.pack(self.repo, bundle, self.primary_bundle, self.source)
        manifest, protocol = pipe.extract(bundle, self.temp_root / "unpacked")
        self.assertEqual(manifest["candidate_source_commit"], self.primary)
        self.assertEqual(manifest["numerical_source_commit"], self.source)
        self.assertNotEqual(self.primary, self.source)
        self.assertEqual(len(manifest["matrix"]["include"]), 32)
        self.assertEqual(protocol["bridges_per_stream"], 256)
        archive = bundle / "source.tar.gz"
        archive.write_bytes(archive.read_bytes()+b"tamper")
        with self.assertRaisesRegex(ValueError, "archive changed"):
            pipe.extract(bundle, self.temp_root / "tampered")

    def test_primary_source_design_and_shared_controller_are_immutable(self):
        path = self.repo / (pipe.R15 + "/code/training_core.py")
        path.write_bytes(path.read_bytes()+b"\n# synthetic input mutation\n")
        self.git("add", str(path.relative_to(self.repo)))
        self.git("commit", "--quiet", "-m", "Synthetic forbidden shared-controller mutation")
        changed = self.git("rev-parse", "HEAD").decode().strip()
        with self.assertRaisesRegex(ValueError, "shared primary numerical dependency changed"):
            pipe.pack(self.repo, self.temp_root / "rejected", self.primary_bundle, changed)

    def test_primary_result_subtree_is_reused_with_both_commit_parents(self):
        self.git("checkout", "--quiet", "--detach", self.primary)
        name = pipe.R15 + "/results/experiment/FIXTURE.json"
        pipe.write(self.repo / name, {"record_type": "synthetic Git-object fixture; no experimental data"})
        self.git("add", name)
        self.git("commit", "--quiet", "-m", "Synthetic primary evidence tree")
        evidence = self.git("rev-parse", "HEAD").decode().strip()
        tree = self.git("rev-parse", f"{evidence}:{pipe.R15}/results/experiment").decode().strip()
        self.git("checkout", "--quiet", "--detach", self.source)
        self.git("read-tree", "--prefix="+pipe.R15+"/results/experiment/", "-u", tree)
        pipe.verify_unchanged_source(self.repo, self.source)
        joined_tree = self.git("write-tree").decode().strip()
        joined = self.git("commit-tree", joined_tree, "-p", self.source, "-p", evidence,
                          "-m", "Synthetic joined provenance fixture").decode().strip()
        self.assertEqual(self.git("rev-parse", f"{joined}:{pipe.R15}/results/experiment").decode().strip(), tree)
        parents = self.git("show", "-s", "--format=%P", joined).decode().strip().split()
        self.assertEqual(parents, [self.source, evidence])
        self.assertEqual(self.git("show", f"{joined}:{pipe.PRIMARY_PROTOCOL}"),
                         self.git("show", f"{self.primary}:{pipe.PRIMARY_PROTOCOL}"))


if __name__ == "__main__":
    unittest.main()
