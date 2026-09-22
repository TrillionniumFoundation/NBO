"""Re-execute all independent nodes after the source freeze and compare proof data.
Timing/provenance fields are intentionally not treated as numerical identity.
"""
from pathlib import Path
import json,hashlib,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
R=HERE.parent

def main():
    out=R/'results/clean_recheck';start=time.perf_counter()
    sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.py')}
    subprocess.run([sys.executable,str(HERE/'run_independent_library.py'),'--out',str(out)],check=True)
    old=json.loads((R/'results/independent_library/nodes.json').read_text());new=json.loads((out/'nodes.json').read_text())
    checks=[]
    for a,b in zip(old,new):
        assert a['k']==b['k']
        for field in ['L','U','B']:
            assert a[field]==b[field],(a['k'],field,a[field],b[field])
            checks.append({'k':a['k'],'field':field,'exact_match':True})
    from exact_price_audit import audit
    result=audit(new)
    assert result['uniform_regret_rational']==json.loads((R/'results/independent_price_audit.json').read_text())['uniform_regret_rational']
    (out/'price_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    receipt={'status':'PASS','source_sha256_at_start':sources,'all_start_sources_unchanged':all(hashlib.sha256((HERE/k).read_bytes()).hexdigest()==v for k,v in sources.items()),'checks':checks,'exact_price_fraction_matches':True,'seconds':time.perf_counter()-start,'scope':'Fresh second-implementation verification of all frozen proposals after expenditure-input correction; not regeneration of their historical training.'}
    assert receipt['all_start_sources_unchanged']
    (R/'results/clean_recheck_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
