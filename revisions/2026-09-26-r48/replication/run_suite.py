"""Generate the frozen suite, solve without inherited inputs, and replay exactly."""
from pathlib import Path
import sys,time,json,gzip,hashlib,platform,resource
from fractions import Fraction as F
import core,check,models
HERE=Path(__file__).resolve().parent; OUT=HERE.parent; TARGET=F(1,1000)
def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(core.enc(obj),indent=2,sort_keys=True)+'\n')

def run_case(family,level):
    started=time.perf_counter(); d=models.generate(family,level); raw=core.enc(d); name=d['name'];save(OUT/'models'/f'{name}.json',raw)
    for method in ['direct','price']:
        start=time.perf_counter(); result=core.run(d,method,TARGET,seconds=30,nodes=255)
        encoded=core.enc(result); content=json.dumps(encoded,separators=(',',':'),sort_keys=True).encode()
        ts=time.perf_counter(); binary=gzip.compress(content,compresslevel=6,mtime=0); path=OUT/'proofs'/f'{name}_{method}.json.gz';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(binary)
        serialization=time.perf_counter()-ts; verification=check.verify(encoded,raw)
        summary={k:v for k,v in result.items() if k not in ['model','tree','policy','witness','prices']}
        prices=[v for row in result['prices']['field'][:-1] for v in row]; widths=result['witness']['widths'];w=result['witness'];beta=d['beta']
        summary.update(name=name,family=family,level=level,n=d['n'],T=d['T'],m=d['m'],beta=beta,epsilon=d['epsilon'],nodes=len(result['tree']),proof_bytes=len(binary),proof_sha256=hashlib.sha256(binary).hexdigest(),model_sha256=hashlib.sha256(json.dumps(raw,sort_keys=True).encode()).hexdigest(),verification=verification,serialization_seconds=serialization,all_in_seconds=time.perf_counter()-start,peak_process_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,oracle_bits=w['bits'],oracle_history=w['history'],max_price=max(prices),mean_price=sum(prices)/len(prices),price_amplification=sum((beta**t*max(result['prices']['field'][t])*(widths[t]+beta*widths[t+1]) for t in range(d['T'])),F(0)),witness_guard_ratio=max(widths[:-1])/((1-beta)*d['epsilon']),initial_incumbent_source='current-run greedy continuation with upper witness',inherited_incumbents=0,exact_operating_value_used=False)
        save(OUT/'results'/f'{name}_{method}.json',summary)
        print(name,method,'gap',float(result['upper']-result['lower']),'nodes',len(result['tree']),'target',verification['target_met'],flush=True)
    return time.perf_counter()-started

if __name__=='__main__':
    family=sys.argv[1] if len(sys.argv)>1 else 'all'
    for f,i in models.CASES:
        if family=='all' or family==f: run_case(f,i)
