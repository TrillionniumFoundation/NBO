"""R16 source, work and inference gates using only manufactured fixtures.

The process fixture never imports a simulator. Its source, checkpoints,
observations and timing phases are explicitly manufactured, and its outputs
are created only inside a disposable directory. No registered bank is drawn.
"""
from __future__ import annotations
import copy
from pathlib import Path
import tempfile
import unittest

import robustness_pipeline as pipe

ROOT=Path(__file__).resolve().parents[3]

MANUFACTURED_WORKER=r'''
import argparse,json,os,pathlib
p=argparse.ArgumentParser()
for name in ['protocol','trial-id','group','out']:p.add_argument('--'+name,required=True)
a=p.parse_args();out=pathlib.Path(a.out)
assert not out.exists(), 'parent contaminated strict-empty worker destination'
out.mkdir(parents=True)
methods=['hjb_greedy','hjb_distilled'] if a.group=='hjb_family' else [a.group]
r=dict(manufactured_infrastructure_fixture=True,complete=True,group=a.group,trial_id=a.trial_id,
 numerical_source_commit=os.environ['NBO_R16_SOURCE_COMMIT'],protocol_sha256='0'*64,
 method_fingerprint=os.environ['NBO_R16_METHOD_FINGERPRINT'],online_payoff_checks=0,
 final_payoff_used_for_selection=False,shared_prerequisite_seconds_since_entry=0.,
 outputs={m:dict(complete=True,deployment_and_confirmation_seconds=0.,operation_counters_complete=True) for m in methods})
(out/'RESULT.json').write_text(json.dumps(r))
print('manufactured fixture only; no economic simulation or bank generation')
'''

class SourceAndDesign(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=pipe.read(ROOT/pipe.PROTOCOL)

    def test_complete_fixed_family_and_rotations(self):
        rows=pipe.validate_protocol(self.p)
        self.assertEqual(len(rows),64)
        self.assertEqual(len({r['trial_id'] for r in rows}),64)
        self.assertEqual(len({r['noise_seed'] for r in rows}),64)
        self.assertEqual(sum(len(pipe.outputs(g)) for r in rows for g in r['group_order']),320)
        for r in rows:self.assertEqual(set(r['group_order']),set(pipe.GROUPS))
        self.assertEqual(4*2*(5+4)*(8+1),648)

    def test_missing_stream_calibration_or_method_is_rejected(self):
        for field in ['seeds','calibrations','methods','execution_groups']:
            p=copy.deepcopy(self.p);p[field].pop()
            with self.assertRaises(ValueError):pipe.validate_protocol(p)

    def test_modified_event_sample_or_margin_budget_is_rejected(self):
        changes=[('inference','alpha',.02),('inference','two_sided_event_count',647),
            ('confirmation','paths_per_stream',16384),('confirmation','steps',4096),
            ('economic_decisions','material_payoff_margin',0.),('economic_decisions','equivalence_margin',.001)]
        for section,key,value in changes:
            p=copy.deepcopy(self.p);p[section][key]=value
            with self.assertRaises(ValueError):pipe.validate_protocol(p)

    def test_economic_fingerprints_and_distinct_development_domain(self):
        production={r['noise_seed'] for r in pipe.trials(self.p)}
        development={int.from_bytes(__import__('hashlib').sha256(
            ('NBO-R16-robustness-development-only-v1/'+r['trial_id']).encode()).digest()[:8],'big') for r in pipe.trials(self.p)}
        self.assertFalse(production&development)
        p=copy.deepcopy(self.p);p['calibrations'][0]['primitives']['T']=2.
        with self.assertRaises(ValueError):pipe.validate_protocol(p)

    def test_source_and_eight_independent_accounts_are_complete(self):
        result=pipe.check(ROOT)
        self.assertTrue(result['complete'])
        self.assertEqual(result['independent_formula_enclosures'],168)
        self.assertEqual(result['confirmation_observations_evaluated'],0)
        self.assertFalse(any(n.endswith('.pt') for n in pipe.source_files(ROOT)))

    def test_creation_only_source_and_evidence_contract(self):
        workflow=(ROOT/pipe.WORKFLOW).read_text()
        self.assertIn('--force-with-lease="refs/heads/$evidence_branch:"',workflow)
        self.assertIn('git push --atomic',workflow)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = 1',workflow)
        self.assertIn('max-parallel: 12',workflow)
        self.assertIn('revision/econometrica-nbo-r16-robustness-source-2026-10-04',workflow)
        self.assertIn('revision/econometrica-nbo-r16-robustness-evidence-2026-10-04',workflow)
        self.assertIn('git diff --exit-code',workflow)

class CompleteWorkAccounting(unittest.TestCase):
    def test_hjb_includes_shared_fit_and_all_process_overhead(self):
        r=dict(shared_prerequisite_seconds_since_entry=20.,outputs={
            'hjb_greedy':dict(deployment_and_confirmation_seconds=30.),
            'hjb_distilled':dict(deployment_and_confirmation_seconds=10.)})
        work=pipe.standalone_work(100.,r)
        self.assertEqual(work['hjb_greedy']['standalone_end_to_end_seconds'],90.)
        self.assertEqual(work['hjb_distilled']['standalone_end_to_end_seconds'],70.)
        self.assertEqual(work['hjb_greedy']['shared_launch_and_finalization_seconds'],40.)
        self.assertEqual(work['hjb_distilled']['excluded_other_deployment_seconds'],30.)

    def test_single_method_receives_the_entire_parent_clock(self):
        r=dict(shared_prerequisite_seconds_since_entry=20.,outputs={'nbo':dict(deployment_and_confirmation_seconds=30.)})
        self.assertEqual(pipe.standalone_work(100.,r)['nbo']['standalone_end_to_end_seconds'],100.)

    def test_inconsistent_group_clock_is_rejected(self):
        r=dict(shared_prerequisite_seconds_since_entry=20.,outputs={'nbo':dict(deployment_and_confirmation_seconds=30.)})
        with self.assertRaises(ValueError):pipe.standalone_work(49.,r)

    def test_fresh_process_keeps_parent_log_outside_empty_worker_directory(self):
        with tempfile.TemporaryDirectory(prefix='r16-manufactured-infrastructure-') as temp:
            root=Path(temp);workspace=root/'workspace';worker=workspace/pipe.WORKER
            worker.parent.mkdir(parents=True);worker.write_text(MANUFACTURED_WORKER)
            p=pipe.read(ROOT/pipe.PROTOCOL);trial=pipe.trials(p)[0]
            m=dict(numerical_source_commit='0'*40,protocol_sha256='0'*64,
                files={str(pipe.WORKER):dict(sha256=pipe.sha(worker))},
                method_fingerprints={g:dict(sha256='1'*64) for g in pipe.GROUPS},
                environment_contract=dict(python='3.12',platform='Linux',packages=pipe.PACKAGES,numeric_threads=1))
            for group in ['nbo','hjb_family']:
                out=root/group;work=pipe.execute_child(workspace,out,m,trial,group)
                self.assertTrue(work['complete'],work.get('failure'))
                self.assertTrue(pipe.read(out/'RESULT.json')['manufactured_infrastructure_fixture'])
                self.assertIn('no economic simulation',(out/'process.log').read_text())
                self.assertEqual(pipe.verify_work(out,m,trial,group),work)
                with self.assertRaises(ValueError):pipe.execute_child(workspace,out,m,trial,group)
                (out/'undeclared.txt').write_text('manufactured evidence tamper')
                with self.assertRaises(ValueError):pipe.verify_work(out,m,trial,group)

class InferenceAndTables(unittest.TestCase):
    def test_outward_table_rounding_and_complete_finite_law(self):
        import robustness_report as report
        self.assertEqual(report.number(.0000001,'lower'),'0.000000')
        self.assertEqual(report.number(.0000001,'upper'),'0.000001')
        self.assertEqual(report.number(-.0000001,'lower'),'-0.000001')
        stats,_,_=report.scientific_modules()
        import numpy as np
        seeds=[10,20];v={s:np.array([-.1,.1]) for s in seeds}
        c={s:dict(clip=.2,bias=0.,tail=0.) for s in seeds};ident={10:dict(noise_hash='a'),20:dict(noise_hash='b')}
        e=report.pooled(stats,v,c,ident,seeds,.01/648)
        self.assertEqual(e['paths'],4)
        with self.assertRaises(ValueError):report.pooled(stats,{10:v[10]},c,ident,seeds,.01/648)

if __name__=='__main__':unittest.main()
