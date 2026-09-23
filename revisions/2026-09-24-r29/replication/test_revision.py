"""Executable R29 scientific checks. Passing tests is not a general economic proof."""
from __future__ import annotations
import argparse, os, hashlib, importlib.util, json, re, subprocess, tempfile, time, unittest
from fractions import Fraction as F
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-24-r29';OLD=ROOT/'revisions/2026-09-24-r28'
spec=importlib.util.spec_from_file_location('controls29',REV/'replication/controls.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
OUT=REV/'results/controls';ROWS=c.load(OUT/'summary.json')

def blob(path):
    raw=Path(path).read_bytes();return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def arr(z):return np.array([[int(v) for v in row] for row in z],dtype=object)

class RevisionTests(unittest.TestCase):
    def test_01_complete_fixed_cohorts(self):
        self.assertEqual(len(ROWS),115);self.assertEqual(sum(len(r['variants']) for r in ROWS),286)
        old=c.load(OLD/'results/inventory/summary.json')
        for d,L in c.MODELS:
            actual={r['tag'] for r in ROWS if (r['d'],r['L'])==(d,L)}
            self.assertEqual(actual,{tag for tag,_ in c.specs(d,L,old)})
        self.assertEqual(sum(r['inherited'] for r in ROWS),34)
        self.assertEqual(sum(len(r['variants'])>2 for r in ROWS),14)
        self.assertEqual(max(r['states'] for r in ROWS),16384)
        for r in ROWS:
            pairs={(v['rule'],F(v['epsilon'])) for v in r['variants']}
            expected={('fixed',F(1,100)),('budget',F(1,100))}
            if len(r['variants'])>2:expected|={(m,e) for m in ('fixed','budget') for e in (F(1,1000),F(1,20))}
            self.assertEqual(pairs,expected)

    def test_02_hashes_freeze_order_and_isolation(self):
        old={(x['d'],x['L'],x['tag']):x for x in c.load(OLD/'results/inventory/summary.json')}
        for d,L in c.MODELS:
            root=OUT/f'd{d}_L{L}';events=c.load(root/'events.json')
            self.assertEqual(events[-1]['event'],'independent_optimal_reference_created')
            self.assertEqual(events[-2]['event'],'all_candidates_frozen')
            self.assertEqual(events[-2]['manifest_sha256'],c.sha(root/'FREEZE_MANIFEST.json'))
            self.assertEqual(events[-1]['sha256'],c.sha(root/'optimal_reference.json.gz'))
            sealed=c.load(root/'FREEZE_MANIFEST.json')
            self.assertEqual(len(events),2*len(sealed)+2)
            for i,r in enumerate(sealed):
                p=root/r['tag'];self.assertEqual(events[2*i]['event'],'raw_candidate_frozen')
                self.assertEqual(events[2*i+1]['event'],'all_reference_free_variants_frozen')
                self.assertEqual(c.sha(p/'pre_reference.json'),events[2*i+1]['pre_reference_sha256'])
                self.assertEqual(c.sha(p/'raw_policy.json'),r['raw_policy_sha256'])
                audit=c.load(p/'input_audit.json');self.assertTrue(audit['reference_guard_enforced']);self.assertTrue(audit['full_horizon_solver_disabled'])
                self.assertEqual(c.sha(p/'input_audit.json'),r['training_input_audit_sha256'])
                self.assertFalse(any('optimal_reference' in s or '/reference/' in s for s in audit['opened_read_paths']))
                if r['inherited']:self.assertEqual(r['raw_policy_sha256'],old[(d,L,r['tag'])]['raw_policy_sha256'])
                for v in r['variants']:
                    self.assertEqual(c.sha(p/(v['key']+'_policy.json')),v['policy_sha256'])
                    self.assertEqual(c.sha(p/(v['key']+'_certificate.json.gz')),v['certificate_sha256'])
                    self.assertFalse(c.load(p/(v['key']+'_completion.json.gz'))['optimal_reference_used'])
            for path,h in c.load(root/'MODEL_EXECUTION.json')['files_sha256'].items():self.assertEqual(c.sha(root/path),h)
        for path,h in c.load(OUT/'environment.json')['source_sha256'].items():self.assertEqual(c.sha(ROOT/path),h)

    def test_03_all_exact_identities_and_policy_preservation(self):
        for d,L in c.MODELS:
            model=c.inv.Model(d,L);root=OUT/f'd{d}_L{L}'
            ref=c.load(root/'optimal_reference.json.gz');opt=arr(ref['values'])
            actual_opt,actual_policy,_=c.inv.independent_optimal(model)
            self.assertTrue(np.array_equal(opt,actual_opt))
            self.assertTrue(np.array_equal(np.array(ref['policy']),actual_policy))
            self.assertEqual(list(map(int,ref['denominators'])),model.den)
            for r in [x for x in ROWS if (x['d'],x['L'])==(d,L)]:
                p=root/r['tag'];raw=np.array(c.load(p/'raw_policy.json'),dtype=np.int64);c.validate_policy(model,raw)
                rv,rc=c.certificate(model,raw);saved=c.load(p/'raw_certificate.json.gz')
                for key in ('bound_rational','denominators','local_deficit_numerators','envelope_numerators'):self.assertEqual(rc[key],saved[key])
                self.assertTrue(np.all(opt[:c.T]-np.asarray(rv[:c.T])>=0))
                self.assertTrue(np.all(opt[:c.T]-np.asarray(rv[:c.T])<=arr(saved['envelope_numerators'])[:c.T]))
                for v in r['variants']:
                    pol=np.array(c.load(p/(v['key']+'_policy.json')),dtype=np.int64);c.validate_policy(model,pol)
                    cv,cc=c.certificate(model,pol);saved=c.load(p/(v['key']+'_certificate.json.gz'))
                    for key in ('bound_rational','denominators','local_deficit_numerators','envelope_numerators'):self.assertEqual(cc[key],saved[key])
                    self.assertLessEqual(F(cc['bound_rational']),F(v['epsilon']))
                    self.assertTrue(np.all(np.asarray(cv)>=np.asarray(rv)),(d,L,r['tag'],v['key'],'payoff preservation'))
                    self.assertTrue(np.all(opt[:c.T]-np.asarray(cv[:c.T])>=0))
                    self.assertTrue(np.all(opt[:c.T]-np.asarray(cv[:c.T])<=arr(cc['envelope_numerators'])[:c.T]))
                    self.assertEqual(int(np.count_nonzero(pol!=raw)),v['changed_actions'])
                    det=c.load(p/(v['key']+'_completion.json.gz'))
                    self.assertEqual(sum(z[-1] for z in det['topology']),v['changed_actions'])
                    self.assertEqual(len(det['changes']),v['changed_actions'])
                    self.assertEqual(sum(z['changed'] for z in det['by_time']),v['changed_actions'])
                    self.assertTrue(all(F(z['envelope_max'])<=F(v['epsilon']) for z in det['by_time']))
            print('AUDITED EXACT MODEL',d,L,flush=True)

    def test_04_completion_edge_cases_and_guards(self):
        m=c.inv.Model(2,3)
        for kind in ('myopic','random','base_stock','tabular2'):
            raw,_=c.generate(m,{'kind':kind,'seed':29001})
            rawvalues=c.inv.exact_policy(m,raw)
            for eps in (F(1,1000),F(1,100),F(1,20)):
                for rule in ('fixed','budget'):
                    p,record=c.completion(m,raw,eps,rule);v,cert=c.certificate(m,p)
                    self.assertLessEqual(F(cert['bound_rational']),eps)
                    self.assertTrue(np.all(np.asarray(v)>=np.asarray(rawvalues)))
                    self.assertTrue(np.all(p[:,0]==0))
                    if rule=='fixed' and eps==F(1,100):
                        inherited,_=c.inv.complete(m,raw);self.assertTrue(np.array_equal(p,inherited))
        bad=raw.copy();bad[0,0]=1
        with self.assertRaises(ValueError):c.validate_policy(m,bad)
        bad=raw.copy();bad[0,1]=m.A
        with self.assertRaises(ValueError):c.validate_policy(m,bad)
        with self.assertRaises(ValueError):c.completion(m,raw,F(0),'budget')
        with self.assertRaises(ValueError):c.validate_policy(m,raw.astype(float))
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'optimal_reference.json';p.write_text('{}')
            with c.isolated():
                with self.assertRaises(PermissionError):p.read_text()
                with self.assertRaises(RuntimeError):c.inv.independent_optimal(m)
        opt,pol,_=c.inv.independent_optimal(m)
        for rule in ('fixed','budget'):
            new,info=c.completion(m,pol,F(1,100),rule)
            self.assertEqual(info['changed_actions'],0)
            self.assertTrue(np.array_equal(new,pol))

    def test_05_inherited_stopped_slice_and_transport(self):
        slices=c.load(OLD/'results/slice_summary.json');self.assertEqual(len(slices),2)
        for x in slices:
            self.assertTrue(x['restricted_target_0_01_met']);self.assertFalse(x['original_full_state_target_met'])
            self.assertFalse(x['financed_47_dimensional_gradient_bridge_established'])
            self.assertGreater(x['smoothness']['strong_concavity_lower'],0)
            self.assertEqual(len(x['polls']),4)
            for p in x['polls']:
                self.assertLessEqual(p['payoff_interval'][1]-p['payoff_interval'][0],float(F(p['oracle_kappa'])*F(p['mesh'])**2))
                self.assertGreater(p['oracle_calls'],0)
        paths=c.load(OLD/'results/central/mechanism_summary.json');self.assertEqual(len(paths),6)
        for x in paths:
            self.assertEqual(x['capped_steps'],0);self.assertEqual(x['max_economic_carrier_mismatch'],0)
            self.assertLess(x['max_parameter_discrepancy'],1e-8)
            self.assertFalse(x['historical_dual_construction_included'])
            history=c.load(OLD/'results/central'/f"mechanism_s{x['seed']}_q{x['orders'][0]}_{x['orders'][1]}"/'history.json')
            self.assertEqual(len(history),200)

    def test_06_every_production_gate_and_restore(self):
        pro=c.load(OLD/'results/central/production_summary.json');self.assertEqual(len(pro),12)
        count=0
        for x in pro:
            self.assertEqual(len(x['decisions']),4);self.assertFalse(x['historical_dual_construction_included'])
            self.assertTrue(x['all_rejections_restored_exact'])
            for z in x['decisions']:
                a=z['candidate_certificate']['value_interval'];b=z['incumbent_before']['value_interval']
                self.assertEqual(z['gate_passed'],a[0]>b[1])
                if z['deployment']=='REJECT_AND_RESTORE':
                    count+=1;self.assertTrue(z['rollback_exact'])
                    self.assertEqual(z['saved_state_sha256'],z['restored_state_sha256'])
                    self.assertEqual(z['saved_state_sha256'],z['deployed_state_sha256'])
                    self.assertEqual(z['deployed_certificate'],z['incumbent_before'])
                elif x['gated']:
                    self.assertTrue(z['gate_passed'])
                    self.assertEqual(z['deployed_state_sha256'],z['candidate_state_sha256'])
        self.assertGreater(count,0)

    def test_07_complete_disposition_and_preservation(self):
        a=c.load(REV/'disposition.json');actual={x['id'] for x in a};expected=set()
        for prefix,limits in [('R27',(18,10,13)),('R26',(14,8,12)),('R25-SP',(12,8,7))]:
            for kind,n in zip('FTN',limits):expected|={f'{prefix}-{kind}{i}' for i in range(1,n+1)}
        self.assertEqual(actual,expected);self.assertEqual(len(a),102)
        for x in a:self.assertTrue(x['response'] and x['evidence'] and x['status'])
        p=REV/'source_audit/PRESERVATION.json'
        if p.exists():
            for x in c.load(p)['entries']:self.assertEqual(blob(ROOT/x['path']),x['git_blob'],x['path'])
        for path,h in [('reviews/2026-09-24-econometrica-r27/referee_report.md','c1cc275b6938ecd0dc85d1a68b88ba60437e3de4'),('reviews/2026-09-23-econometrica-r25-second-pass/referee_report.md','83cd53026d6cfae4591910c3c86387889aeaf6fb')]:
            if os.environ.get('CI'):self.assertTrue((ROOT/path).exists(),path)
            if (ROOT/path).exists():self.assertEqual(blob(ROOT/path),h)
        headline=REV/'results/R29_HEADLINE_RESULTS.json'
        if headline.exists():
            self.assertFalse(c.load(headline)['original_full_domain_target_closed'])
            self.assertEqual(c.load(headline)['original_target'],.01)
        for name in ['ECTA_R29','SUPP_R29','RESPONSE_R29','COMPUTATION_R29','HISTORY_R29']:
            p=ROOT/(name+'.tex')
            if os.environ.get('CI'):
                self.assertTrue(p.exists(),name);self.assertTrue((ROOT/(name+'.pdf')).exists(),name)
            if p.exists():
                for path in re.findall(r'\\input\{([^}]+)\}',p.read_text()):self.assertTrue((ROOT/(path if path.endswith('.tex') else path+'.tex')).exists(),path)
                if (ROOT/(name+'.log')).exists():
                    log=(ROOT/(name+'.log')).read_text(errors='replace')
                    self.assertNotIn('undefined',log)
                    self.assertNotIn('Overfull',log)
                    self.assertNotIn('multiply defined',log)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    started=time.perf_counter();suite=unittest.defaultTestLoader.loadTestsFromTestCase(RevisionTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        record={'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'passed':result.wasSuccessful(),'elapsed_seconds':time.perf_counter()-started,'candidate_count':115,'completion_count':286,'original_full_domain_target_closed':False}
        try:record['checked_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        except subprocess.CalledProcessError:record['checked_commit']=None
        args.output.write_text(json.dumps(record,indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
