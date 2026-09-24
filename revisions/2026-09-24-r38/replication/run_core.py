"""Execute and check every R38 experiment; fail before publication on any error."""
from pathlib import Path
import gzip,hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
PROGRAMS=('primary','verify_primary','sensitivity','frontier','verify_frontier','local_lp','multistate','gap_study')
def canonical_hash(path):
    d=json.loads(gzip.decompress(path.read_bytes()))
    return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
    start=time.perf_counter();out=ROOT/'results';out.mkdir(exist_ok=True);records=[]
    for name in PROGRAMS:
        tic=time.perf_counter();path=ROOT/'replication'/f'{name}.py'
        with (out/f'{name}_execution.log').open('w') as stream:
            proc=subprocess.run([sys.executable,str(path)],cwd=REPO,stdout=stream,stderr=subprocess.STDOUT)
        records.append({'program':name,'returncode':proc.returncode,'seconds':time.perf_counter()-tic})
        print(name,proc.returncode,records[-1]['seconds'],flush=True)
        if proc.returncode:raise RuntimeError(f'{name} failed; inspect retained execution log')
    read=lambda name:json.loads((out/(name+'.json')).read_text())
    p=read('primary');v=read('independent_verification');f=read('frontier');vf=read('frontier_independent_verification')
    s=read('sensitivity');m=read('multistate');l=read('local_lp');g=read('gap_study')
    assert (p['cases'],p['exact_integrated'],p['positive_cost_exact'],p['exact_pointwise'])==(42,24,12,23)
    assert v['passed'] and v['objects']==42 and len(v['mutation_categories'])==20 and all(x['rejected'] for x in v['mutation_categories'])
    assert (f['point_cases'],f['strict_class_separations'])==(70,24) and len(f['two_period_uniform_references'])==2
    assert vf['passed'] and vf['objects']==70
    assert s['cases']==66 and s['strict_savings']==22 and s['failed_certificates']==0
    assert m['cases']==76 and sum(x['certified'] for x in m['outcomes'] if x['method']=='restart')==26
    assert sum(x['certified'] for x in m['outcomes'] if x['method']=='pilot_raw')==0
    assert sum(x['certified'] for x in m['outcomes'] if x['method']=='classical_scalarization')==15
    assert l['cases']==12 and len(g['outcomes'])==42 and len(g['support_work'])==21
    expected=json.loads((ROOT/'replication/expected_objects.json').read_text())
    actual_map={}
    for directory in expected['directories']:
        for path in sorted((out/directory).glob('*.json.gz')):
            actual_map[str(path.relative_to(ROOT))]=canonical_hash(path)
    b=json.dumps(actual_map,sort_keys=True,separators=(',',':')).encode()
    assert len(actual_map)==expected['count']==187
    assert hashlib.sha256(b).hexdigest()==expected['canonical_manifest_sha256'], 'Exact scientific manifest differs'
    checks=[{'path':p,'canonical_sha256':sha,'passed':True} for p,sha in sorted(actual_map.items())]
    ledger={'passed':True,'programs':records,'canonical_scientific_objects':checks,'exact_object_count':len(checks),
            'seconds':time.perf_counter()-start,'python':sys.version,'platform':platform.platform(),
            'scope':'Exact cross-environment scientific-object comparison excludes timing fields and nonlinear NPZ container timestamps. SymPy independent verification covers the 42 primary and 70 fixed-restart frontier objects. Other arithmetic checks are explicitly not called independent.'}
    (out/'execution_ledger.json').write_text(json.dumps(ledger,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
