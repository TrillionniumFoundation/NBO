"""Complete exactly nine pre-declared evaluations that failed before simulation.

No actor is refitted and no completed array or original ledger is overwritten.
The original exceptions and all original result hashes are part of the record.
"""
from pathlib import Path
import hashlib,json,os,time
from bellman_study import ROOT,R
from policy_certificate import evaluate
from initial_state_inputs import floating_initial_state

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def recover():
    protocol=json.loads((R/'PROTOCOL.json').read_text())
    assert sha(R/'PROTOCOL.json')=='8757019b8359414a1499f9f2558c8aa6e74b780f7a12a100e917c9420f53d007'
    out=R/'results/seed_11';ledger=json.loads((out/'EXECUTION.json').read_text())
    failed=[x for x in ledger['commands'] if not x['success']]
    cases=[(d,mean,sd) for d in (10,20,50) for mean,sd in ((0,.5),(0,1),(-1,1.5))]
    identifiers={f'nbo_d{d}_s11'+str((1024,4096,dict(shift=mean,spread=sd))) for d,mean,sd in cases}
    assert len(failed)==9 and {x['id'] for x in failed}==identifiers
    assert all(x['kind']=='evaluation' and 'Cannot cast ufunc' in x['error'] and "y0+=spread*v" in x['traceback'] for x in failed)
    assert ledger['source_commit']=='83d4cb7fc934e98a577afe2a8e5c0e03e65bb571'
    folders=[p for p in (R/'results').iterdir() if p.is_dir() and (p.name.startswith('seed_') or p.name=='greedy')]
    before={str(p.relative_to(ROOT)):sha(p) for folder in folders for p in folder.rglob('*') if p.is_file()}
    record=dict(original_numerical_source=ledger['source_commit'],recovery_source=os.environ.get('NBO_SOURCE_COMMIT','local'),protocol_sha256=sha(R/'PROTOCOL.json'),original_failures=failed,original_result_hashes=before,recovered=[],unchanged_original_results=False,refitted_policies=0,replacement_seeds=0,scope='Numeric-value-preserving float conversion at the JSON configuration boundary. Nine failed initial-state allocations are completed using their original frozen actors and the originally declared final noise seed. The failures occurred before drawing final shocks or simulating any paths.')
    dest=R/'results/INITIAL_STATE_RECOVERY.json'
    dest.write_text(json.dumps(record,indent=2)+'\n')
    for d,mean,sd in cases:
        path=out/f'nbo_d{d}_s11.pt';training=json.loads(path.with_suffix('.json').read_text())
        assert sha(path)==training['weights_sha256']
        ident=f'nbo_d{d}_s11_n1024_r1_mean{mean:g}_sd{sd:g}'
        assert not (out/(ident+'.json')).exists() and not (out/(ident+'.npz')).exists(),ident
        start=time.perf_counter()
        data=evaluate(path,1024,4096,test_seed=protocol['final_noise_seed'],out=out,**floating_initial_state(dict(shift=mean,spread=sd)))
        assert data['id']==ident and data['weights_sha256']==training['weights_sha256']
        rec=dict(id=ident,success=True,seconds=time.perf_counter()-start,json_path=str((out/(ident+'.json')).relative_to(ROOT)),json_sha256=sha(out/(ident+'.json')),raw_path=str((out/(ident+'.npz')).relative_to(ROOT)),raw_sha256=sha(out/(ident+'.npz')),weights_sha256=data['weights_sha256'],noise_sha256=data['noise_sha256'])
        record['recovered'].append(rec);dest.write_text(json.dumps(record,indent=2)+'\n')
    assert all(sha(ROOT/path)==digest for path,digest in before.items()),'an original record was changed'
    record['unchanged_original_results']=True;dest.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'recovered':len(record['recovered']),'original_failures_retained':len(failed),'original_files_unchanged':len(before),'refitted_policies':0}))
if __name__=='__main__':recover()
