"""Complete retained library: independent MPFR arithmetic, shared mathematics.
All nodes are recomputed; none of the old certified endpoints is used as an
input to a new bound. Four independent worker processes reduce wall time.
"""
from pathlib import Path
import sys,json,time,hashlib,argparse,resource,platform,traceback
import concurrent.futures
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE));import mpfr_interval as M
sys.modules['interval64']=M
sys.path.insert(0,str(ROOT/'revisions/2026-09-22-r14/replication'))
from independent_primal import evaluate
from independent_dual import run,primitives
from state_cost_certificate import full_budget
from exact_price_audit import audit
I,exp,Q=M.I,M.exp,M.I.rational
ARITH=f'MPFR {M.VERSION}, 128-bit directed operations and directed binary64 endpoints'
def worker(n,out):
    start=time.perf_counter();k=str(n['k']);tag=f'{n["k"]:g}';actor=ROOT/n['actor_path'];pilot=actor.parent/f'dual_pilot_k{tag}.json'
    p=evaluate(actor,k);d=run(pilot,k,32,512)
    p['arithmetic']=ARITH;d['arithmetic']=ARITH
    (out/f'primal_k{tag}.json').write_text(json.dumps(p,indent=2)+'\n');(out/f'dual_k{tag}.json').write_text(json.dumps(d,indent=2)+'\n')
    B=(full_budget(actor)+I(-float((Q('.02')*2*exp(-Q('.58').square()/(2*Q('.05').square()))).hi),0)).pair()
    return {'k':n['k'],'L':p['value_interval'][0],'U':d['optimal_value_upper'],'B':B,'actor_path':n['actor_path'],
      'seconds':time.perf_counter()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      'actor_sha256':hashlib.sha256(actor.read_bytes()).hexdigest(),'pilot_sha256':hashlib.sha256(pilot.read_bytes()).hexdigest(),
      'input_generation':'inherited proposal and dual pilot; fresh complete MPFR verification'}
def main(out,workers=4):
    start=time.perf_counter();out.mkdir(parents=True,exist_ok=False)
    raw=json.loads((ROOT/'revisions/2026-09-22-r12/results/envelope.json').read_text())['nodes'];rows=[];attempts=[]
    prim=primitives();prim['arithmetic']=ARITH;(out/'primitives.json').write_text(json.dumps(prim,indent=2)+'\n')
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        futures={pool.submit(worker,n,out):n['k'] for n in raw}
        for f in concurrent.futures.as_completed(futures):
            try:
                row=f.result();rows.append(row);attempts.append({'k':row['k'],'status':'completed','seconds':row['seconds']});print(json.dumps(row),flush=True)
            except Exception as exc:attempts.append({'k':futures[f],'status':'failed','error':repr(exc),'traceback':traceback.format_exc()})
            (out/'attempts.json').write_text(json.dumps(attempts,indent=2)+'\n');(out/'nodes.json').write_text(json.dumps(sorted(rows,key=lambda r:r['k']),indent=2)+'\n')
    if len(rows)!=len(raw):raise RuntimeError('Incomplete MPFR node set; no envelope claim permitted')
    rows.sort(key=lambda r:r['k']);original=json.loads((ROOT/'revisions/2026-09-22-r14/results/independent_library/nodes.json').read_text());checks=[]
    for n,o in zip(rows,original):
        assert n['k']==o['k']
        checks.append({'k':n['k'],'R14_lower':o['L'],'mpfr_lower':n['L'],'R14_upper':o['U'],'mpfr_upper':n['U'],
          'primal_difference':n['L']-o['L'],'upper_difference':n['U']-o['U'],'cost_intervals_overlap':max(n['B'][0],o['B'][0])<=min(n['B'][1],o['B'][1])})
    result=audit(rows);result['arithmetic']=ARITH
    result['shared_trusted_components']=['economic derivation','primal/dual analytic formulas','rational Gauss rule and remainders','exact rational envelope algorithm','Python/NumPy indexing','MPFR and C ABI']
    result['not_claimed']=['formal verification','fresh proposal generation','independent economic derivation']
    (out/'envelope.json').write_text(json.dumps(result,indent=2)+'\n');(out/'comparison.json').write_text(json.dumps(checks,indent=2)+'\n')
    (out/'kernel_tests.json').write_text(json.dumps(M.test(),indent=2)+'\n')
    (out/'resources.json').write_text(json.dumps({'status':'completed','nodes':len(rows),'worker_processes':workers,'wall_seconds':time.perf_counter()-start,
      'summed_node_seconds':sum(r['seconds'] for r in rows),'max_worker_rss_kib':max(r['max_rss_kib'] for r in rows),
      'platform':platform.platform(),'scope':'all inherited nodes re-evaluated with independent arithmetic; no proposal-generation cost represented as zero'},indent=2)+'\n')
    print(json.dumps({'nodes':len(rows),'regret_upper':result['uniform_regret_upper']}),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--workers',type=int,default=4);a=p.parse_args();main(a.out,a.workers)
