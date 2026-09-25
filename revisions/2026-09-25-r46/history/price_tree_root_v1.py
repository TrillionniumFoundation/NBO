"""R46 development extension: aggregate tree strengthened by certified price planes.

This extension was written after observing the first R46 price diagnostic. It is
not an untouched holdout. All sixteen original models are retained. Root and
small-tree runs are stored separately from the source-frozen R44 evaluation.
"""
from pathlib import Path
from fractions import Fraction as F
import gzip,json,sys,time,hashlib,importlib.util
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'revisions/2026-09-25-r46';B=ROOT/'revisions/2026-09-25-r44'
sys.path.insert(0,str(B/'replication'))
import global_solver as core
from verify_prices import verify as verify_price
old_rect=core.rectangular;old_build=core.build;Z=F(0)

def run(name,nodes=1,seconds=120):
    source=[];envelopes=[]
    for label in ['constant','restart']:
        path=R/'proofs'/name/f'{label}.json.gz';verify_price(path)
        obj=json.loads(gzip.decompress(path.read_bytes()))
        source.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        envelopes.append(([[F(z) for z in row] for row in obj['prices']],[[F(z) for z in row] for row in obj['transformed_lower']]))
    raw=json.loads((B/'models'/f'{name}.json').read_text());d=core.old.parse_model(raw)
    def rectangular(d,cache,box):
        out=old_rect(d,cache,box)
        if not out['infeasible']:
            for t in range(d['T']):
                for i in range(d['n']):out['clo'][t][i]=max([out['clo'][t][i]]+[u[t][i] for lam,u in envelopes])
            out['lower']=core.dot(d['nu'],out['clo'][0])
        return out
    def build(d,cache,box,rect):
        lp=old_build(d,cache,box,rect)
        if lp is not None:
            H=cache['ref'][1]
            for lam,u in envelopes:
                for t in range(d['T']):
                    for i in range(d['n']):lp.row({lp.idx['S',t,i]:1,lp.idx['D',t,i]:-lam[t][i]},H[t][i]-u[t][i]-lam[t][i]*d['epsilon'])
        return lp
    core.rectangular=rectangular;core.build=build
    core.improve=lambda d,cache,p,seconds:(p,{'skipped':True,'reason':'inherited incumbent supplied separately'})
    started=time.perf_counter();obj=core.search(d,enhanced=False,seconds=seconds,nodes=nodes,target=F(1,1000),node_seconds=15)
    # An independently feasible inherited policy may improve the incumbent.
    inherited=json.loads(gzip.decompress((R/'proofs'/name/'restart.json.gz').read_bytes()))
    U=min(F(obj['upper']),F(inherited['upper']))
    if U<F(obj['upper']):obj['policy']=inherited['policy']
    obj['upper']=U;obj['lower']=min(F(obj['lower']),U)
    obj['summary'].update(target_met=U-obj['lower']<=F(1,1000),gap=float(U-obj['lower']),relative_gap=float((U-obj['lower'])/U) if U else 0)
    obj['price_sources']=source;obj['r46_extension']='certified-price-planes-v1'
    method='price_root' if nodes==1 else 'price_search'
    out=R/'proofs'/name/f'{method}.json.gz';core.save(obj,out)
    result=dict(name=name,method=method,summary=obj['summary'],lower=str(obj['lower']),upper=str(U),proof_bytes=out.stat().st_size,seconds=time.perf_counter()-started,requested_nodes=nodes,requested_seconds=seconds)
    (R/'results'/f'{name}_{method}.json').write_text(json.dumps(result,indent=2)+'\n');print(name,method,json.dumps(result['summary']),flush=True)

if __name__=='__main__':
    for name in sys.argv[1:]:run(name)
