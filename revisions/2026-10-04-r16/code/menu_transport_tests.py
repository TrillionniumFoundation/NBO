"""Manufactured local-bare transport tests; no scientific bank or remote push."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import menu_transport as tr


class LocalRemote(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        self.source = self.root/'source'; self.source.mkdir()
        subprocess.run(['git','init','--quiet',str(self.source)],check=True)
        # This old blob must never enter a transport object repository.
        old = bytes(range(256))*4096
        (self.source/'historical_raw.bin').write_bytes(old)
        self.old_oid = tr.facts(old)['git_blob']
        tr.git(self.source,'add','historical_raw.bin')
        tr.git(self.source,'commit','--quiet','-m','manufactured immutable source')
        self.S = tr.git(self.source,'rev-parse','HEAD').decode().strip()
        self.remote = self.root/'remote.git'
        subprocess.run(['git','init','--bare','--quiet',str(self.remote)],check=True)
        tr.git(self.remote,'config','uploadpack.allowFilter','true')
        tr.git(self.remote,'config','uploadpack.allowAnySHA1InWant','true')
        self.url = self.remote.as_uri()
        tr.git(self.source,'remote','add','origin',self.url)
        tr.git(self.source,'push','--quiet','origin',self.S+':refs/heads/'+tr.SOURCE_BRANCH)
        tr.initialize(self.source,self.S)
        self.trials = [dict(trial_id='manufactured_d2_s17',calibration='manufactured',dimension=2,stream_seed=17),
                       dict(trial_id='manufactured_d2_s29',calibration='manufactured',dimension=2,stream_seed=29)]
        self.manifest = dict(numerical_source_commit=self.S,assessment_fingerprint='b'*64,
                             protocol_sha256='c'*64,github_run_id='manufactured-only',
                             matrix={'include':self.trials})
        self.paths = {}
        for i,t in enumerate(self.trials):
            folder = self.root/'originals'/t['trial_id']; folder.mkdir(parents=True)
            (folder/'training').mkdir(); (folder/'training/cache.bin').write_bytes(bytes([100+i])*3001)
            (folder/'confirmation').mkdir()
            for stage in [1,2,3]:
                (folder/'confirmation'/f'stage{stage}.npz').write_bytes(bytes([stage,i])*501)
                tr.write(folder/'confirmation'/f'stage{stage}.json',dict(stage=stage,manufactured=True))
            f = folder/'fits/nbo_scalar'; f.mkdir(parents=True)
            tr.write(f/'FIT_WORK.json',dict(manufactured=True,seed=t['stream_seed']))
            tr.write(f/'stage1.json',dict(manufactured=True))
            data = dict(complete=True,trial=t,**{k:self.manifest[k] for k in ['numerical_source_commit','assessment_fingerprint','protocol_sha256']},
                        files={n:v['sha256'] for n,v in tr.inventory(folder).items()})
            tr.write(folder/'TRIAL.json',data); self.paths[t['trial_id']] = folder

    def tearDown(self):
        self.temp.cleanup()

    def client(self,name):
        repo=self.root/name;tr.prepare_repo(repo,self.url);return repo

    def publish_all(self):
        records={}; pubs={}
        for i,t in enumerate(self.trials):
            receipt,pub=tr.publish_trial(self.client('client'+str(i)),self.paths[t['trial_id']],self.manifest)
            records[t['trial_id']]=receipt;pubs[t['trial_id']]=pub
        return records,pubs

    def test_creation_only_root_and_evidence_refs(self):
        self.assertEqual(tr.remote_head(self.source),self.S)
        with self.assertRaises(ValueError):tr.initialize(self.source,self.S)
        self.assertEqual(tr.remote_head(self.source),self.S)

    def test_cas_race_preserves_both_complete_trials(self):
        a,b=self.client('a'),self.client('b'); other={}
        first,second=[t['trial_id'] for t in self.trials]
        def race(attempt,parent,commit):
            if attempt==0:other['value']=tr.publish_trial(b,self.paths[second],self.manifest)
        receipt,pub=tr.publish_trial(a,self.paths[first],self.manifest,before_push=race)
        self.assertEqual(pub['cas_attempts'],2)
        tip=tr.fetch_staging(a,self.S)
        proof=tr.assert_transport_tree(a,tip,{first:receipt,second:other['value'][0]},self.manifest)
        self.assertEqual(proof['trial_count'],2);self.assertTrue(proof['source_tree_preserved'])
        objects={line.split()[0] for line in tr.git(a,'cat-file','--batch-all-objects','--batch-check=%(objectname) %(objecttype)').decode().splitlines()}
        self.assertNotIn(tr.facts((self.paths[second]/'training/cache.bin').read_bytes())['git_blob'],objects)

    def test_exact_acknowledgment_replay_is_read_only_but_changed_payload_is_rejected(self):
        repo=self.client('a');ident=self.trials[0]['trial_id'];folder=self.paths[ident]
        receipt,pub=tr.publish_trial(repo,folder,self.manifest)
        before=tr.remote_head(repo)
        again,ack=tr.publish_trial(repo,folder,self.manifest)
        self.assertEqual(receipt,again);self.assertTrue(ack['identical_payload_already_present'])
        self.assertEqual(before,tr.remote_head(repo))
        (folder/'training/cache.bin').write_bytes(b'changed original')
        row=tr.read(folder/'TRIAL.json');row['files']={n:v['sha256'] for n,v in tr.inventory(folder).items() if n!='TRIAL.json'}
        tr.write(folder/'TRIAL.json',row)
        with self.assertRaises(ValueError):tr.publish_trial(repo,folder,self.manifest)
        self.assertEqual(before,tr.remote_head(repo))

    def test_partial_repository_never_downloads_old_raw_blob(self):
        repo=self.client('a');tr.fetch_staging(repo,self.S)
        def present():
            return {line.split()[0] for line in tr.git(repo,'cat-file','--batch-all-objects','--batch-check=%(objectname) %(objecttype)').decode().splitlines()}
        self.assertNotIn(self.old_oid,present())
        tr.publish_trial(repo,self.paths[self.trials[0]['trial_id']],self.manifest)
        self.assertNotIn(self.old_oid,present())

    def test_analysis_round_trip_and_full_future_checkout(self):
        records,pubs=self.publish_all();parts=self.root/'parts'
        for ident,receipt in records.items():
            folder=self.root/'analysis'/ident
            tr.make_analysis(self.paths[ident],receipt,pubs[ident],folder)
            tr.partition_analysis(folder,parts/ident)
        restored=self.root/'restored'
        result=tr.restore_analysis_parts(parts,restored,self.manifest)
        self.assertEqual(result,records)
        for ident in records:
            self.assertFalse((restored/ident/'training/cache.bin').exists())
            target=restored/ident/'training/cache.bin';target.parent.mkdir()
            shutil.copyfile(self.paths[ident]/'training/cache.bin',target)
            self.assertEqual(tr.verify_analysis_trial(restored/ident,self.manifest),records[ident])
            target.write_bytes(b'corrupted full-checkout raw')
            with self.assertRaises(ValueError):tr.verify_analysis_trial(restored/ident,self.manifest)

    def test_changed_missing_and_duplicate_analysis_parts_rejected(self):
        records,pubs=self.publish_all();parts=self.root/'parts'
        for ident,receipt in records.items():
            folder=self.root/'analysis'/ident
            tr.make_analysis(self.paths[ident],receipt,pubs[ident],folder);tr.partition_analysis(folder,parts/ident)
        original=next(parts.rglob('ANALYSIS_PART.json'))
        duplicate=parts/'duplicate';shutil.copytree(original.parent,duplicate)
        with self.assertRaises(ValueError):tr.restore_analysis_parts(parts,self.root/'bad-duplicate',self.manifest)
        shutil.rmtree(duplicate)
        data=original.read_bytes();original.unlink()
        with self.assertRaises(ValueError):tr.restore_analysis_parts(parts,self.root/'bad-missing',self.manifest)
        original.write_bytes(data)
        (original.parent/'payload/TRIAL.json').write_bytes(b'changed')
        with self.assertRaises(ValueError):tr.restore_analysis_parts(parts,self.root/'bad-changed',self.manifest)

    def test_final_evidence_uses_complete_staging_parent_and_small_append(self):
        records,pubs=self.publish_all()
        results=self.source/tr.R16/'results/continuation_menu';summary=self.source/tr.R16/'results/continuation_menu_summary'
        summary.mkdir(parents=True)
        for ident,receipt in records.items():tr.make_analysis(self.paths[ident],receipt,pubs[ident],results/'trials'/ident)
        tr.write(results/'FINAL_AUDIT.json',dict(complete=True,numerical_source_commit=self.S))
        tr.write(summary/'REPORT.json',dict(manufactured=True))
        manifest=self.root/'manifest.json';tr.write(manifest,self.manifest)
        previous=tr.remote_head(self.source)
        result=tr.finalize(self.source,manifest,results,summary)
        self.assertEqual(result['staging_parent'],previous)
        self.assertEqual(tr.remote_head(self.source,tr.EVIDENCE_BRANCH),result['evidence_commit'])
        self.assertEqual(tr.git(self.source,'rev-parse',result['evidence_commit']+'^').decode().strip(),previous)
        self.assertLess(result['new_payload_bytes'],100000)
        with self.assertRaises(ValueError):tr.finalize(self.source,manifest,results,summary)

    def test_unregistered_tree_addition_and_unsafe_path_rejected(self):
        records,pubs=self.publish_all();tip=tr.fetch_staging(self.source,self.S)
        bad=tr.append_commit(self.source,tip,tr._write_blobs(self.source,{'unregistered.txt':b'no'}),'manufactured forbidden addition')
        with self.assertRaises(ValueError):tr.assert_transport_tree(self.source,bad,records,self.manifest)
        for name in ['../escape','/absolute','x\tbad','x\nline']:
            with self.assertRaises(ValueError):tr.safe(self.root,name)


if __name__=='__main__':unittest.main(verbosity=2)
