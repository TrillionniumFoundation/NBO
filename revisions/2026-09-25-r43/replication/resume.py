"""Resume an interrupted session without altering registered numerical code.
Reuses only v2 proof files that pass a fresh independent endpoint reconstruction.
Timings stored with a reused proof retain their original meaning.
"""
from pathlib import Path
import gzip,json
import run_suite as runner
original=runner.one

def cached(name,d,mode,cap):
    p=runner.ROOT/'proofs'/(name+'_'+mode+'.json.gz')
    r=runner.ROOT/'results'/(name+'_'+mode+'.json')
    if p.exists() and r.exists():
        record=json.loads(r.read_text()); proof=json.loads(gzip.decompress(p.read_bytes()))
        if proof.get('schema')=='nbo-r43-regret-v2' and 'failure' not in record:
            check=runner.verify(p)
            if check['sha256']==record['proof_sha256'] and check['lower']==record['lower'] and check['upper']==record['upper']:
                print('RECHECKED',name,mode,flush=True)
                return record
    return original(name,d,mode,cap)
runner.one=cached
if __name__=='__main__': runner.main()
