"""Manufactured source, finite-family, lossless-transport and work tests.

No fitted candidate or confirmatory innovation bank is generated here.
"""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import menu_pipeline as pipe
from menu_report import cost_record

ROOT=Path(__file__).resolve().parents[3]

class SourceProtocolTests(unittest.TestCase):
    def test_complete_registered_matrix_and_rotations(self):
        p=pipe.read(ROOT/pipe.PROTOCOL);pipe.validate_protocol(p)
        rows=pipe.trials(p)
        self.assertEqual(len(rows),128);self.assertEqual(len({r['trial_id'] for r in rows}),128)
        self.assertTrue(all(set(r['method_order'])==set(pipe.METHODS) for r in rows))
        self.assertGreater(len({tuple(r['method_order']) for r in rows}),1)
    def test_missing_method_stage_seed_and_changed_budget_rejected(self):
        p=pipe.read(ROOT/pipe.PROTOCOL)
        for modify in [lambda z:z['methods'].pop(),lambda z:z['training_streams']['seeds'].pop(),
                       lambda z:z['training']['cumulative_replay_states'].pop(),
                       lambda z:z['confidence'].__setitem__('alpha',.02)]:
            q=copy.deepcopy(p);modify(q)
            with self.assertRaises(ValueError):pipe.validate_protocol(q)
    def test_complete_source_closure_has_no_missing_dependency(self):
        self.assertTrue(pipe.check(ROOT)['complete'])
    def test_timeout_fits_the_prescribed_remote_job(self):
        p=pipe.read(ROOT/pipe.PROTOCOL);e=p['execution']
        self.assertLess(5*(e['method_timeout_seconds']+180)+e['confirmation_timeout_seconds']+1800,300*60)

class LosslessEvidenceTests(unittest.TestCase):
    def fixture(self,root):
        p=copy.deepcopy(pipe.read(ROOT/pipe.PROTOCOL));p['calibrations']=p['calibrations'][:1]
        p['dimensions']=[10];p['training_streams']['seeds']=p['training_streams']['seeds'][:2]
        m=dict(numerical_source_commit='a'*40,assessment_fingerprint='b'*64,protocol_sha256='c'*64,
               environment_contract={'packages':{}})
        for t in pipe.trials(p):
            folder=root/'trials'/t['trial_id'];folder.mkdir(parents=True)
            for method in pipe.METHODS:
                f=folder/'fits'/method;f.mkdir(parents=True)
                (f/'manufactured.bin').write_bytes(bytes(range(256)))
                fit=dict(source_commit=m['numerical_source_commit'],protocol_sha256=m['protocol_sha256'],
                    method=method,calibration=t['calibration'],dimension=t['dimension'],seed=t['stream_seed'],
                    final_confirmation_read=False,payload_inventory={'manufactured.bin':{'sha256':pipe.sha(f/'manufactured.bin'),'bytes':256}})
                pipe.write(f/'FIT_WORK.json',fit)
            env=dict(packages={})
            r=dict(complete=True,trial=t,numerical_source_commit=m['numerical_source_commit'],
                assessment_fingerprint=m['assessment_fingerprint'],protocol_sha256=m['protocol_sha256'],
                all_fitting_finished_before_confirmation=True,final_confirmation_used_for_selection=False,
                environment=env,environment_fingerprint=pipe.digest(pipe.canonical(env)),
                method_process_work={method:dict(returncode=0,end_to_end_seconds=1.) for method in pipe.METHODS},
                confirmation_process_work={'returncode':0},files=pipe.inventory(folder))
            pipe.write(folder/'TRIAL.json',r)
            pipe.partition(folder,root/'parts'/t['trial_id'],t['trial_id'],m['numerical_source_commit'],m['assessment_fingerprint'])
        return p,m
    def test_all_bytes_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p,m=self.fixture(root)
            self.assertEqual(pipe.reassemble(root/'parts',root/'restored',m,p),2)
            self.assertEqual(pipe.inventory(root/'trials'),pipe.inventory(root/'restored'))
    def test_changed_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p,m=self.fixture(root)
            f=next((root/'parts').rglob('manufactured.bin'));f.write_bytes(b'changed')
            with self.assertRaises(ValueError):pipe.reassemble(root/'parts',root/'restored',m,p)
    def test_missing_part_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p,m=self.fixture(root)
            next((root/'parts').rglob('PART.json')).unlink()
            with self.assertRaises(ValueError):pipe.reassemble(root/'parts',root/'restored',m,p)
    def test_duplicate_part_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p,m=self.fixture(root)
            f=next((root/'parts').rglob('PART.json'));shutil.copytree(f.parent,root/'parts'/'duplicate')
            with self.assertRaises(ValueError):pipe.reassemble(root/'parts',root/'restored',m,p)
    def test_files_are_partitioned_without_omission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'trial';folder.mkdir()
            for i in range(5):(folder/f'{i}.bin').write_bytes(bytes([i])*100)
            with patch.object(pipe,'PART_PAYLOAD',220):
                receipt=pipe.partition(folder,root/'parts','manufactured','a'*40,'b'*64)
            self.assertEqual(receipt['parts'],3);self.assertEqual(receipt['files'],5)
            files={}
            for f in (root/'parts').rglob('PART.json'):files.update(pipe.read(f)['files'])
            self.assertEqual({k:v['sha256'] for k,v in files.items()},pipe.inventory(folder))

class WorkAccountingTests(unittest.TestCase):
    def test_actual_final_clock_and_conservative_earlier_prefix_are_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'fits/nbo_scalar';folder.mkdir(parents=True)
            pipe.write(folder/'FIT_WORK.json',dict(complete_fit_seconds=100.,failed_fit=False,
                counters_complete=True,counter_scope='complete',clock_scope='manufactured'))
            for stage,prefix in [(1,20.),(2,50.),(3,90.)]:
                pipe.write(folder/f'stage{stage}.json',dict(parent_prefix_seconds=prefix,fallback=False,counters={'queries':384}))
            t=dict(method_process_work={'nbo_scalar':dict(end_to_end_seconds=102.,cpu_seconds=90.,peak_rss_kib=1000)},
                confirmation_process_work={'end_to_end_seconds':9.})
            first=cost_record(root,t,'nbo_scalar',1);last=cost_record(root,t,'nbo_scalar',3)
            self.assertEqual(first['construction_and_query_seconds'],32.)
            self.assertFalse(first['construction_clock_is_actual_complete_process'])
            self.assertEqual(last['construction_and_query_seconds'],102.)
            self.assertTrue(last['construction_clock_is_actual_complete_process'])
            self.assertEqual(last['complete_shared_confirmation_process_seconds'],9.)
            self.assertEqual(last['conservative_construction_plus_full_audit_seconds'],111.)

if __name__=='__main__':unittest.main()
