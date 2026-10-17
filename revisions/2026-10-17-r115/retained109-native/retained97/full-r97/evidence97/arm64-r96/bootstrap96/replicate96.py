"""Frozen-model ARM64 replication; no fitting or independent new observations."""
from pathlib import Path
import argparse,csv,hashlib,json,os,platform,subprocess,sys,time
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'code'))
ARMS=('online-risk-dp','quadratic','relu','spline')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2,sort_keys=True,allow_nan=False)+'\n')
def timing():
    from experiment96 import load_freeze,head,machine
    load_freeze();out=R/'results96/timing-arm64';out.mkdir(parents=True,exist_ok=True)
    receipt=dict(source_commit=head(),machine=machine(),records=[],new_fits=0,additional_independent_observations=0,
        scope='Five fresh child processes per arm/risk on unchanged stream 5. Original primary timings are retained separately. Descriptive, not a future-runtime confidence interval.')
    for index in range(2):
        for arm in ARMS:
            for rep in range(5):
                p=out/f'{index}-{arm}-{rep}.json'
                if p.exists():raise RuntimeError('Refuse to replace an existing timing repetition')
                start=time.perf_counter()
                cmd=[sys.executable,str(R/'code/experiment96.py'),'timing-one','--index',str(index),'--arm',arm,'--out',str(p)]
                result=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
                receipt['records'].append(dict(index=index,arm=arm,repetition=rep,complete_process_seconds=time.perf_counter()-start,
                    exit_code=result.returncode,stderr=result.stderr,record_sha256=sha(p) if p.exists() else None))
                save(out/'TIMING96.json',receipt)
                if result.returncode:raise RuntimeError('Independent-architecture timing failed')
    return receipt

def compare():
    import numpy as np
    from experiment96 import load_freeze,head,machine
    load_freeze();f=R/'results96/FREEZE96.json'
    original=R/'results96/evaluation-primary';replica=R/'results96/evaluation-arm64'
    a=json.loads((original/'RESULTS96.json').read_text());b=json.loads((replica/'RESULTS96.json').read_text())
    if not a['freeze_sha256']==b['freeze_sha256']==sha(f):raise RuntimeError('Architectures did not use the same frozen models and selector')
    comparison=[];equal_actions=True
    for index in range(2):
        for arm in ARMS:
            name=f'alpha-{index}-{arm}.csv';pa=original/name;pb=replica/name
            with pa.open() as x:ra=list(csv.DictReader(x))
            with pb.open() as x:rb=list(csv.DictReader(x))
            if len(ra)!=4096 or len(rb)!=4096:raise RuntimeError('Replication sample count differs')
            numeric=[k for k in ra[0] if k not in ('rejected','exact')]
            differences={k:max(abs(float(x[k])-float(y[k])) for x,y in zip(ra,rb)) for k in numeric}
            for k in ('row','x0','x1'):
                if differences[k]!=0:raise RuntimeError('Replication changed initial states or pairing')
            same_action=differences['actions']==0;equal_actions &= same_action
            same_flags={k:all(x[k]==y[k] for x,y in zip(ra,rb)) for k in ('rejected','exact')}
            comparison.append(dict(index=index,arm=arm,rows=4096,primary_sha256=sha(pa),arm64_sha256=sha(pb),
                max_absolute_column_differences=differences,same_first_actions=same_action,same_flags=same_flags))
    independent=R/'audit/reproduction96/INDEPENDENT96-arm64.json';ind=json.loads(independent.read_text())
    tests=json.loads((R/'audit/arm64-96/tests/TESTS95.json').read_text())
    tim=json.loads((R/'results96/timing-arm64/TIMING96.json').read_text())
    gates=dict(same_frozen_models=True,same_initial_states=True,all_rows_qualified=b['all_rows_qualified'],
        independent_statistics=ind['success'] and ind['all_rows_checked']==32768 and len(ind['exact_statistics'])==12,
        independent_endpoints=ind['success'] and ind['endpoint_count']==64,
        all_tests=all(v['passed'] and v['tests'] and not v['skipped'] for v in tests.values()),
        complete_timing=len(tim['records'])==40 and all(v['exit_code']==0 for v in tim['records']))
    result=dict(status='passed' if all(gates.values()) else 'incomplete',gates=gates,source_commit=head(),freeze_sha256=sha(f),
        machine=machine(),new_fits=0,additional_independent_observations=0,same_first_actions=equal_actions,
        comparisons=comparison,tests_total=sum(v['tests'] for v in tests.values()),independent_receipt_sha256=sha(independent),
        primary_result_sha256=sha(original/'RESULTS96.json'),arm64_result_sha256=sha(replica/'RESULTS96.json'),
        scope='Source-identical frozen-model service replication. Any arithmetic, action or admission differences are reported, not replaced. The common terminal-controller error remains enclosed. Primary acquisition is not re-fitted on ARM64; no full-construction or energy replication is claimed.')
    save(R/'audit/arm64-96/ARCHITECTURE96.json',result)
    print(json.dumps({'status':result['status'],'gates':gates,'same_first_actions':equal_actions,'tests':result['tests_total']},indent=2))
    if not all(gates.values()):raise RuntimeError('Architecture replication gate failed')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['timing','compare']);args=p.parse_args()
    timing() if args.mode=='timing' else compare()
