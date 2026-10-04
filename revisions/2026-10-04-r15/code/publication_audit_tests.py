"""Independent publication gate tests; deliberately outside frozen main tests."""
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import tempfile
import unittest

import publication_audit as audit


class PublicationAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.repo=Path(self.temp.name)
        self.git('init','-q');self.git('config','user.email','audit@example.invalid');self.git('config','user.name','Audit fixture')
        for name,text in {'ECTA.tex':'original article\n','supp.tex':'original supplement\n','README.md':'original readme\n','code.py':'print(1)\n'}.items():
            (self.repo/name).write_text(text)
        self.git('add','.');self.git('commit','-qm','fixed original');self.commit=self.git('rev-parse','HEAD').strip()
        self.store=audit.GitStore(self.repo)
        for name,destination in audit.ROOT_ARCHIVE.items():
            destination=self.repo/destination;destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes((self.repo/name).read_bytes());(self.repo/name).write_text('current publication\n')

    def tearDown(self):self.store.close();self.temp.cleanup()
    def git(self,*args):return subprocess.check_output(['git',*args],cwd=self.repo).decode()

    def test_exact_original_bytes_and_only_declared_root_archives(self):
        result=audit.check_history(self.repo,self.store,self.commit,4)
        self.assertEqual(result['blobs'],4)
        self.assertEqual(result['files']['code.py']['destination'],'code.py')
        self.assertEqual(result['files']['ECTA.tex']['destination'],str(audit.ROOT_ARCHIVE['ECTA.tex']))

    def test_changed_historical_content_is_rejected_even_if_size_equal(self):
        (self.repo/'code.py').write_text('print(2)\n')
        with self.assertRaisesRegex(ValueError,'retained bytes differ'):
            audit.check_history(self.repo,self.store,self.commit,4)

    def test_missing_archive_is_rejected(self):
        (self.repo/audit.ROOT_ARCHIVE['ECTA.tex']).unlink()
        with self.assertRaisesRegex(ValueError,'missing/nonregular'):
            audit.check_history(self.repo,self.store,self.commit,4)

    def test_source_manifest_checks_git_blob_and_sha_and_assessment_fingerprint(self):
        path=self.repo/'code.py';oid=self.store.tree(self.commit)['code.py']['git_blob']
        inputs={'source':'fixture','files':{'code.py':audit.sha(path)}}
        manifest={'numerical_source_commit':self.commit,'files':{'code.py':{'git_blob':oid,'sha256':audit.sha(path),'bytes':path.stat().st_size}},
                  'fingerprint_input':inputs,'assessment_fingerprint':hashlib.sha256(audit.canonical(inputs)).hexdigest()}
        self.assertEqual(len(audit.check_source_manifest(self.repo,self.store,self.commit,manifest)),1)
        manifest['files']['code.py']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'source manifest bytes mismatch'):
            audit.check_source_manifest(self.repo,self.store,self.commit,manifest)
        manifest['files']['code.py']['sha256']=audit.sha(path)
        manifest['files']['code.py']['git_blob']='0'*40
        with self.assertRaisesRegex(ValueError,'blob mismatch'):
            audit.check_source_manifest(self.repo,self.store,self.commit,manifest)

    def test_inventory_rejects_self_reference_and_path_escape(self):
        manifest=self.repo/'EVIDENCE_MANIFEST.json'
        audit.write(manifest,{'files':{'code.py':audit.sha(self.repo/'code.py')}})
        self.assertEqual(len(audit.check_inventory(self.repo,manifest)),1)
        audit.write(manifest,{'files':{'EVIDENCE_MANIFEST.json':'0'*64}})
        with self.assertRaisesRegex(ValueError,'self-referencing'):
            audit.check_inventory(self.repo,manifest)
        for path in ['../outside','/absolute']:
            with self.assertRaisesRegex(ValueError,'unsafe'):
                audit.safe_path(self.repo,path)

    def test_original_work_inventory_exhaustive_and_detects_raw_tampering(self):
        folder=self.repo/'trial';folder.mkdir();(folder/'raw.npz').write_bytes(b'original raw bytes')
        environment={'python':'3.12','threads':1}
        work={'complete':True,'returncode':0,'numerical_source_commit':self.commit,'protocol_sha256':'p',
              'environment':environment,'environment_fingerprint':hashlib.sha256(audit.canonical(environment)).hexdigest(),
              'files':{'raw.npz':audit.sha(folder/'raw.npz')}}
        audit.write(folder/'WORK.json',work)
        self.assertEqual(audit.check_work(folder,self.commit,'p')['files'],1)
        (folder/'unlisted.txt').write_text('unlisted')
        with self.assertRaisesRegex(ValueError,'unlisted or missing'):
            audit.check_work(folder,self.commit,'p')
        (folder/'unlisted.txt').unlink();(folder/'raw.npz').write_bytes(b'changed raw bytes')
        with self.assertRaisesRegex(ValueError,'worker file mismatch'):
            audit.check_work(folder,self.commit,'p')

    def test_evidence_manifest_root_cannot_include_unrelated_file(self):
        folder=self.repo/'evidence';folder.mkdir();manifest=folder/'EVIDENCE_MANIFEST.json'
        audit.write(manifest,{'files':{'code.py':audit.sha(self.repo/'code.py')}})
        with self.assertRaisesRegex(ValueError,'outside declared root'):
            audit.check_inventory(self.repo,manifest,folder)

    def test_isolated_editorial_replay_checks_generated_bytes_without_writing_original(self):
        r=self.repo/audit.R15;(r/'code').mkdir(parents=True);(r/'manuscript').mkdir()
        audit.write(r/'SOURCE_INVENTORY.json',{'source_files':{'code.py':{}}})
        outputs={'ECTA.tex':'current publication\n','supp.tex':'current publication\n',
                 str(audit.R15/'response.tex'):'response\n',str(audit.R15/'EDITORIAL_MAP.json'):'{}\n',
                 str(audit.R15/'MATHEMATICAL_PRESERVATION.json'):'{}\n',str(audit.R15/'manuscript/generated.tex'):'derived content\n'}
        script='from pathlib import Path\noutputs='+repr(outputs)+'\nfor name,text in outputs.items():\n p=Path(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)\n'
        (r/'code/integrate.py').write_text(script)
        for name,text in outputs.items():(self.repo/name).write_text(text)
        self.assertEqual(audit.check_integration_replay(self.repo)['files_compared'],6)
        changed=r/'manuscript/generated.tex';changed.write_text('tampered derived content\n')
        with self.assertRaisesRegex(ValueError,'differs from independent replay'):
            audit.check_integration_replay(self.repo)
        self.assertEqual(changed.read_text(),'tampered derived content\n')

    def test_fresh_process_report_replay_detects_changed_numerical_publication(self):
        script=self.repo/'report.py';protocol=self.repo/'protocol.json';results=self.repo/'raw';published=self.repo/'published'
        results.mkdir();published.mkdir();protocol.write_text('{}\n');(results/'sample.txt').write_text('original array\n')
        script.write_text("import argparse\nfrom pathlib import Path\np=argparse.ArgumentParser()\nfor x in ['protocol','results','out']:p.add_argument('--'+x)\na=p.parse_args();out=Path(a.out);out.mkdir(parents=True)\n(out/'REPORT.json').write_bytes((Path(a.results)/'sample.txt').read_bytes())\n")
        (published/'REPORT.json').write_text('original array\n')
        result=audit.check_report_replay(self.repo,'report.py','protocol.json',results,published)
        self.assertEqual(result['files'],1)
        (published/'REPORT.json').write_text('changed endpoint\n')
        with self.assertRaisesRegex(ValueError,'differs from original-array replay'):
            audit.check_report_replay(self.repo,'report.py','protocol.json',results,published)

    def test_self_consistent_environment_hash_does_not_bypass_frozen_contract(self):
        folder=self.repo/'environment';folder.mkdir()
        environment={'python':'3.12.14','platform':'Linux-x86_64','threads':1,'packages':{'numpy':'2.3.5'}}
        work={'complete':True,'returncode':0,'numerical_source_commit':self.commit,'files':{},
              'environment':environment,'environment_fingerprint':hashlib.sha256(audit.canonical(environment)).hexdigest(),
              'end_to_end_seconds':1.,'peak_rss_kib':100}
        contract={'python':'3.12','platform':'Linux','numeric_threads':1,'packages':{'numpy':'2.3.5'}}
        audit.write(folder/'WORK.json',work);audit.check_work(folder,self.commit,environment_contract=contract)
        environment['packages']['numpy']='0.0.0'
        work['environment_fingerprint']=hashlib.sha256(audit.canonical(environment)).hexdigest()
        audit.write(folder/'WORK.json',work)
        with self.assertRaisesRegex(ValueError,'packages differ'):
            audit.check_work(folder,self.commit,environment_contract=contract)

    def narrative_fixture(self):
        r=self.repo/audit.R15;m=r/'manuscript';m.mkdir(parents=True,exist_ok=True)
        status={'primary_result_narrative_pending':False,'mechanism_numerical_narrative_pending':False}
        audit.write(r/'NARRATIVE_STATUS.json',status)
        for name in ['introduction.tex','conclusion.tex']:(m/name).write_text('Complete executed findings.\n')
        (m/'abstract.tex').write_text(r'\begin{abstract}A complete finite-stream economic comparison.\end{abstract}')
        response='\n'.join(r'\section*{'+name+': Reply}\nComplete response.' for name in [f'B{i}' for i in range(1,8)]+[f'M{i}' for i in range(1,10)])
        (m/'response_body.tex').write_text(response)
        (r/'archive/old_response.tex').write_text('This is a working response and is still pending.')
        return r,m,status,response

    def test_narrative_gate_is_scoped_and_rejects_pending_or_duplicate_responses(self):
        r,m,status,response=self.narrative_fixture()
        self.assertEqual(audit.check_narrative(self.repo)['abstract_words'],5)
        status['primary_result_narrative_pending']=True;audit.write(r/'NARRATIVE_STATUS.json',status)
        with self.assertRaisesRegex(ValueError,'remains pending'):audit.check_narrative(self.repo)
        status['primary_result_narrative_pending']=False;audit.write(r/'NARRATIVE_STATUS.json',status)
        (m/'response_body.tex').write_text(response+'\n'+r'\section*{B1: Duplicate}')
        with self.assertRaisesRegex(ValueError,'exactly one section'):audit.check_narrative(self.repo)

    def test_current_placeholder_and_abstract_word_limit_are_independent_gates(self):
        r,m,status,response=self.narrative_fixture()
        (m/'conclusion.tex').write_text('These results are still\n pending.')
        with self.assertRaisesRegex(ValueError,'placeholder'):audit.check_narrative(self.repo)
        (m/'conclusion.tex').write_text('Complete discussion.')
        (m/'abstract.tex').write_text(r'\begin{abstract}'+' '.join(['word']*151)+r'\end{abstract}')
        with self.assertRaisesRegex(ValueError,'150 words'):audit.check_narrative(self.repo)

    def paired_fixture(self):
        seeds=list(range(16));dims=[10,50];methods=['nbo','raw_costate','direct_policy','neural_hjb'];contrasts=[['nbo',x] for x in methods[1:]]
        protocol={'design':{'seeds':seeds,'dimensions':dims},'confirmation':{'direct_contrasts':contrasts},'economic_decision':{'equivalence_margin_payoff':.0001}}
        identity=[dict(dimension=d,stream_seed=s,method=m,fallback=(s==0 or (s==1 and m=='nbo'))) for d in dims for s in seeds for m in methods]
        flags={(x['dimension'],x['stream_seed'],x['method']):x['fallback'] for x in identity}
        def interval(zero=False,bias=.02):
            return dict(paths=8192,clipped_mean=0.,variance=0. if zero else .01,range_lower=0. if zero else -1.,range_upper=0. if zero else 1.,empirical_bernstein_margin=0. if zero else .1,clipping_tail=0.,event_alpha=.02/238,clipped_paths=0,bias=0. if zero else bias,lower=0. if zero else -.1-bias,upper=0. if zero else .1+bias)
        old_seeds=[];old_means=[];rows=[];means=[]
        for d in dims:
            for left,right in contrasts:
                name=left+'__minus__'+right
                for s in seeds:
                    fa,fb=flags[d,s,left],flags[d,s,right];old=dict(dimension=d,stream_seed=s,endpoint=name,**interval(fa and fb));old_seeds.append(old)
                    new=interval(fa and fb,.02 if fa or fb else .005)
                    rows.append(dict(dimension=d,stream_seed=s,endpoint=name,original=copy.deepcopy(old),refined=new,
                        eligibility='both_exact_reference' if fa and fb else 'mixed_fallback_original_transfer_retained' if fa or fb else 'two_simulated_total_held_policies',
                        refinement_applied=not(fa or fb),new_theorem_bias_candidate=None if fa or fb else .005,numerical_terms=None if fa or fb else {}))
                old=dict(dimension=d,endpoint=name,**interval());old_means.append(old)
                new=interval(bias=.005);new.update(declared_seeds=seeds,seed_count=16,decision={'statistical_superiority':False,'economically_material_superiority':False,'noninferiority':False,'practical_equivalence':False,'economically_material_inferiority':False,'unresolved':True})
                means.append(dict(dimension=d,endpoint=name,original=copy.deepcopy(old),refined=new,eligible_normal_normal_streams=14,refined_streams=14))
        original=dict(confidence={'event_count':238},identity_records=identity,seed_endpoints=old_seeds,method_endpoints=old_means,attainment=[],work=[])
        refined=dict(status='complete',reused_direct_events=102,additional_confidence_events=0,changed_payoff_observations=0,fitted_weights_read=False,original_trial_count=128,original_confidence=copy.deepcopy(original['confidence']),
            original_identity_records=copy.deepcopy(identity),original_unchanged_attainment=[],original_unchanged_work=[],seed_comparisons=rows,method_comparisons=means)
        return protocol,original,refined

    def test_paired_refinement_keeps_complete_event_family_and_fallback_cases(self):
        protocol,original,refined=self.paired_fixture()
        result=audit.check_paired_semantics(protocol,original,refined)
        self.assertEqual((result['seed_events'],result['method_events']),(96,6))
        mixed=next(x for x in refined['seed_comparisons'] if x['eligibility'].startswith('mixed_'))
        mixed['refined']['bias']=.001
        with self.assertRaisesRegex(ValueError,'fallback original transfer'):audit.check_paired_semantics(protocol,original,refined)

    def test_paired_refinement_rejects_changed_event_or_missing_stream(self):
        protocol,original,refined=self.paired_fixture()
        refined['seed_comparisons'][2]['refined']['variance']+=.00001
        with self.assertRaisesRegex(ValueError,'empirical-Bernstein event'):audit.check_paired_semantics(protocol,original,refined)
        protocol,original,refined=self.paired_fixture();refined['seed_comparisons'].pop()
        with self.assertRaisesRegex(ValueError,'omitted or duplicated'):audit.check_paired_semantics(protocol,original,refined)

    def test_every_python_replay_pins_hash_seed_independently_of_caller(self):
        environment=audit.replay_environment(self.repo/'cache')
        self.assertEqual(environment['PYTHONHASHSEED'],'0')
        self.assertEqual(environment['PYTHONDONTWRITEBYTECODE'],'1')
        self.assertEqual(environment['NUMBA_CACHE_DIR'],str(self.repo/'cache'))
        self.assertTrue(all(environment[x]=='1' for x in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMBA_NUM_THREADS']))


if __name__=='__main__':unittest.main()
