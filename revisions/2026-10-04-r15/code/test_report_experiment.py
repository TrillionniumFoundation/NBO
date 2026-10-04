"""Synthetic evidence verifies completeness, pair identity, and report counts."""
from pathlib import Path
import hashlib,json,tempfile,unittest
import numpy as np
from report_experiment import report


class ReportContracts(unittest.TestCase):
    def fixture(self,base):
        protocol=json.loads((Path(__file__).resolve().parents[1]/'PROTOCOL.json').read_text())
        protocol['status']='frozen_before_confirmatory_execution'
        protocol['confirmation']['paths_per_seed']=8
        pp=base/'PROTOCOL.json';pp.write_text(json.dumps(protocol))
        ph=hashlib.sha256(pp.read_bytes()).hexdigest();primitive=protocol['design']['primitives_sha256']
        results=base/'trials'
        for d in protocol['design']['dimensions']:
            for seed in protocol['design']['seeds']:
                for i,m in enumerate(protocol['design']['methods']):
                    trial=results/f'd{d}_s{seed}'/m;directory=trial/'confirmation';directory.mkdir(parents=True)
                    production=np.arange(8)*1e-6+(i+1)*.001;consumption=np.full(8,.0005);terminal=np.full(8,.0001)
                    raw=directory/'raw.npz';np.savez(raw,paired_gain=production-consumption+terminal,production=production,consumption_deficit=consumption,terminal_gain=terminal,initial_profile=np.arange(8),terminal_anchor=np.zeros((8,d)))
                    confirmation=dict(confirmation_independent_of_selection=True,raw_path='confirmation/raw.npz',raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),clipping_threshold=.1,bias=1e-5,clipping_tail=1e-8,actor_bias_upper=4e-6,statistic_error_upper=1e-10,
                        initial_profile_hash=f'profiles-{d}-{seed}',initial_state_hash=f'states-{d}-{seed}',terminal_anchor_hash=f'anchor-{d}-{seed}',noise_hash=f'noise-{d}-{seed}',steps=protocol['confirmation']['steps'],paths=8,stream_seed=seed,confirmation_bank=f'final-{d}-{seed}',primitives_sha256=primitive)
                    row=dict(complete=True,confirmation_independent_of_selection=True,counters={'actor_forward_rows':130,'verification_transitions':200},training_counters={'actor_forward_rows':30},verification_work={'actor_forward_rows':100,'verification_transitions':200},verification_counters_complete=True,online_checks=[],method_id=m,method_fingerprint=hashlib.sha256(m.encode()).hexdigest(),dimension=d,stream_seed=seed,primitives_sha256=primitive,protocol_sha256=ph,source_commit='a'*40,final_confirmation=confirmation,attained_online=False,fallback=False,actual_early_stopping_execution=True)
                    (trial/'RESULT.json').write_text(json.dumps(row));(trial/'WORK.json').write_text(json.dumps(dict(complete=True,end_to_end_seconds=12+i,peak_rss_kib=2048,cpu_seconds=10)))
        return pp,results,protocol

    def test_complete_evidence_generates_exact_registered_family(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);pp,results,p=self.fixture(base)
            r=report(pp,results,base/'report')
            self.assertEqual(r['trial_count'],128)
            self.assertEqual(len(r['seed_endpoints']),224)
            self.assertEqual(len(r['method_endpoints']),14)
            self.assertEqual(r['confidence']['event_count'],238)
            self.assertEqual(len(r['decomposition']),8)
            self.assertTrue(all(z['median_not_attained'] for z in r['work']))
            self.assertTrue(all(z['mean_work_counters']['actor_forward_rows']==130 for z in r['work']))
            self.assertTrue((base/'report/table_method_comparisons.tex').is_file())

    def test_missing_trial_and_wrong_primitive_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);pp,results,p=self.fixture(base)
            trial=results/f"d{p['design']['dimensions'][0]}_s{p['design']['seeds'][0]}"/p['design']['methods'][0]
            wp=trial/'WORK.json';original=wp.read_text();wp.unlink()
            with self.assertRaises(ValueError):report(pp,results,base/'report')
            wp.write_text(original)
            rp=trial/'RESULT.json';r=json.loads(rp.read_text());r['primitives_sha256']='wrong';rp.write_text(json.dumps(r))
            with self.assertRaises(ValueError):report(pp,results,base/'report')

    def test_mixed_analytical_fallback_retains_reference_transfer(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);pp,results,p=self.fixture(base)
            d=p['design']['dimensions'][0];s0,s1,s2=p['design']['seeds'][:3]
            for seed,method in [(s0,'nbo'),(s0,'raw_costate'),(s1,'raw_costate'),(s2,'nbo')]:
                trial=results/f'd{d}_s{seed}'/method;rp=trial/'RESULT.json';r=json.loads(rp.read_text())
                raw=trial/r['final_confirmation']['raw_path']
                with np.load(raw) as data:arrays={k:data[k].copy() for k in data.files}
                for k in ['paired_gain','production','consumption_deficit','terminal_gain']:arrays[k][:]=0
                np.savez(raw,**arrays)
                r['fallback']=True;c=r['final_confirmation'];c['analytic_schedule']=True
                for k in ['clipping_threshold','bias','clipping_tail','actor_bias_upper','statistic_error_upper']:c[k]=0.
                c['raw_sha256']=hashlib.sha256(raw.read_bytes()).hexdigest();rp.write_text(json.dumps(r))
            result=report(pp,results,base/'report')
            def endpoint(seed,name):return next(e for e in result['seed_endpoints'] if e['dimension']==d and e['stream_seed']==seed and e['endpoint']==name)
            both=endpoint(s0,'nbo__minus__raw_costate')
            self.assertEqual((both['lower'],both['upper'],both['bias']),(0.,0.,0.))
            mixed=endpoint(s1,'nbo__minus__raw_costate')
            self.assertEqual(mixed['bias'],1e-5)
            self.assertEqual(mixed['transfer_case'],'one_exact_reference_full_schedule_relative_transfer')
            reverse=endpoint(s2,'nbo__minus__direct_policy')
            self.assertEqual(reverse['bias'],1e-5)


if __name__=='__main__':unittest.main()
