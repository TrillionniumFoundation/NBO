"""Execute one frozen environment; every method and every cap is retained."""
from pathlib import Path
from fractions import Fraction as F
import json, sys, os, platform, time, hashlib, traceback, gzip, importlib.util
import numpy as np, scipy
import global_solver as core
from verify_tree import verify, Reader
from scip_baseline import solve as scip_solve
HERE=Path(__file__).resolve().parents[1]

def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,default=str,indent=2,allow_nan=False)+'\n')

def frozen():
    protocol=json.loads((HERE/'PROTOCOL.json').read_text())
    for rel,wanted in protocol['source_sha256'].items():
        assert hashlib.sha256((core.ROOT/rel).read_bytes()).hexdigest()==wanted,rel
    return protocol

def main(name):
    protocol=frozen(); raw=json.loads((HERE/'models'/f'{name}.json').read_text())
    assert hashlib.sha256((HERE/'models'/f'{name}.json').read_bytes()).hexdigest()==protocol['models_sha256'][name]
    d=core.old.parse_model(raw); d.update({k:v for k,v in raw.items() if k not in d})
    # Keep metadata exactly as registered; parse_model already retains it.
    expected=json.loads(json.dumps(d,default=core.enc)); assert expected==raw
    out=HERE/'results'/name; out.mkdir(parents=True,exist_ok=True)
    proofdir=HERE/'proofs'/name; proofdir.mkdir(parents=True,exist_ok=True)
    env=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform(),processor=platform.processor(),cpu_count=os.cpu_count(),threads={k:os.environ.get(k) for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']})
    write(out/'environment.json',env)
    summaries={}
    for label,enhanced in [('bellman',True),('aggregate',False)]:
        ts=time.perf_counter()
        try:
            obj=core.search(d,enhanced=enhanced,seconds=protocol['seconds_per_method'],nodes=protocol['nodes_per_method'],target=F(protocol['target']),node_seconds=protocol['node_lp_seconds'],progress=lambda r: print(name,label,json.dumps(r),flush=True))
            path=proofdir/f'{label}.json.gz'; core.save(obj,path)
            report=verify(path,HERE/'models'/f'{name}.json')
            result=dict(summary=obj['summary'],verification=report,total_with_verification=time.perf_counter()-ts,proof_bytes=path.stat().st_size,trace=obj['trace'],root_status={k:obj['tree'][0].get(k) for k in ['lp_status','primal_available','dual_available','variables','local_proposal']})
            write(out/f'{label}.json',result); summaries[label]=result
        except Exception as exc:
            err=dict(error=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),elapsed=time.perf_counter()-ts)
            write(out/f'{label}_ERROR.json',err); raise
    ts=time.perf_counter()
    try:
        native=scip_solve(d,seconds=protocol['seconds_per_method'],nodes=protocol['nodes_per_method'],target=F(protocol['target']),logfile=out/'scip.log')
        path=proofdir/'scip.json.gz'; core.save(native,path)
        stored=json.loads(gzip.decompress(path.read_bytes())); assert stored['model']==raw
        c,regret=Reader(raw,True).policy(stored['policy']); assert c==F(stored['verified_candidate_upper'])
        # A shared best rational lower endpoint allows a valid cross-solver
        # intersection without treating SCIP's floating bound as a proof.
        lower=max(F(summaries[x]['verification']['lower']) for x in ['bellman','aggregate'])
        upper=min([c]+[F(summaries[x]['verification']['upper']) for x in ['bellman','aggregate']])
        report=dict(passed=True,upper=str(c),max_regret=str(regret),all_restart_checks=d['n']*d['T'],proof_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        result=dict(summary=native['summary'],candidate_verification=report,shared_certified_interval=dict(lower=str(lower),upper=str(upper),gap=float(upper-lower),target_met=upper-lower<=F(protocol['target'])),total_with_verification=time.perf_counter()-ts,proof_bytes=path.stat().st_size)
        write(out/'scip.json',result); summaries['scip']=result
    except Exception as exc:
        err=dict(error=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),elapsed=time.perf_counter()-ts)
        write(out/'scip_ERROR.json',err); raise
    write(out/'COMPLETE.json',dict(name=name,all_completed=True,environment=env,model_sha256=protocol['models_sha256'][name],source_freeze_verified=True))
    print('COMPLETE',name,flush=True)

if __name__=='__main__': main(sys.argv[1])
