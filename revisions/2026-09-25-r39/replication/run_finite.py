"""Execute the prospectively frozen cases once, retaining every budget stop."""
import argparse,subprocess,sys,json,time,gzip,hashlib,os
from fractions import Fraction as F
from common_markov import ROOT,model,solve,encode,save

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def run_case(index,method):
    protocol=json.loads((ROOT/'protocol/holdout.json').read_text())
    for name,wanted in protocol['algorithm_sha256'].items():
        assert hashlib.sha256((ROOT/'replication'/name).read_bytes()).hexdigest()==wanted
    case=protocol['cases'][index];tic=time.perf_counter();m=model(**case)
    kwargs=dict(budget=protocol['node_budget'],tolerance=F(protocol['absolute_tolerance']),seconds_cap=protocol['seconds_cap_per_solver_case'])
    if method=='interval':out=solve(m,**kwargs)
    else:
        from verified_lp import solve_lp
        out=solve_lp(m,**kwargs)
    out['end_to_end_seconds']=time.perf_counter()-tic
    out['protocol_freeze_commit']='13fd3ee0eec78db5fa6aed34e63819c5ed546209'
    out['canonical_protocol_sha256']=hashlib.sha256(canonical(protocol)).hexdigest()
    folder=ROOT/'results/finite';folder.mkdir(parents=True,exist_ok=True)
    filename=f"finite_{case['seed']}_T{case['T']}_{method}.json.gz";p=folder/filename
    p.write_bytes(gzip.compress(json.dumps(encode(out),sort_keys=True).encode(),mtime=0))
    row={k:v for k,v in out.items() if k not in ('model','V','policy','J','C','nodes')};row.update(case,proof_file='finite/'+filename,proof_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    save(folder/f'{filename}.summary.json',row)
    print(case,method,float(out['lower']),float(out['upper']),float(out['relative_gap']),out['evaluations'],out['seconds'],flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--index',type=int);ap.add_argument('--method');args=ap.parse_args()
    if args.index is not None:run_case(args.index,args.method)
    else:
        protocol=json.loads((ROOT/'protocol/holdout.json').read_text());rows=[]
        for i,case in enumerate(protocol['cases']):
            for method in ('interval','lp'):
                subprocess.run([sys.executable,__file__,'--index',str(i),'--method',method],env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'},check=True)
        for p in sorted((ROOT/'results/finite').glob('*.summary.json')):rows.append(json.loads(p.read_text()))
        save(ROOT/'results/finite.json',{'outcomes':rows,'protocol_freeze_commit':'13fd3ee0eec78db5fa6aed34e63819c5ed546209'})
