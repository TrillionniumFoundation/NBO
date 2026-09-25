#!/usr/bin/env python3
"""Execute the predeclared structural suite, retaining all outcomes."""
import gzip,hashlib,json,os,subprocess,sys,time
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
CASES=[(8,8,3,'band','19/20','1/100'),(16,16,3,'band','19/20','1/100'),
(32,32,3,'band','19/20','1/100'),(64,64,3,'band','19/20','1/100'),
(8,8,3,'cycle','99/100','1/20'),(16,16,3,'cycle','99/100','1/20'),
(32,32,3,'cycle','99/100','1/20'),(16,16,3,'dense','19/20','1/100'),
(8,8,3,'band','1','1/100'),(16,16,3,'band','1','1/100'),
(32,32,3,'cycle','1','1/20'),(16,16,5,'band','19/20','1/100')]
protocol=BASE/'PROTOCOL.json'
if protocol.exists():
    assert json.loads(protocol.read_text())['cases']==[list(c) for c in CASES], 'case-registration mismatch'
rows=[]
for i,case in enumerate(CASES):
    proof=BASE/'proofs'/f'case{i:02d}.json.gz';out=BASE/'results'/f'check{i:02d}.json'
    st=time.perf_counter()
    try:
        if not proof.exists():
            run=subprocess.run([sys.executable,str(HERE/'structured.py'),'--case',*map(str,case),'--out',str(proof)],capture_output=True,text=True,timeout=180)
            (BASE/'results'/f'constructor{i:02d}.log').write_text(run.stdout+run.stderr)
            if run.returncode:raise RuntimeError('constructor failed')
        with gzip.open(proof,'rt') as f:o=json.load(f)
        md=o.get('model',{})
        assert [md.get(k) for k in ('n','T','m','kind','beta','epsilon')]==list(case), 'proof/case mismatch'
        if o.get('results',{}).get('status')!='certified':raise RuntimeError('no certificate')
        run=subprocess.run([sys.executable,str(HERE/'verify_structured.py'),str(proof),'--out',str(out)],capture_output=True,text=True,timeout=180)
        if run.returncode:raise RuntimeError('verification failed: '+run.stderr)
        check=json.loads(out.read_text());r=o['results'].copy();r.update(case=list(case),proof=proof.name,proof_sha256=hashlib.sha256(proof.read_bytes()).hexdigest(),proof_bytes=proof.stat().st_size,independent=check)
        print(i,case,'gap',float(F(r['gap'])),'LP',round(r['lp_seconds'],3),'exact',round(r['exact_certificate_seconds'],3),'check',round(check['seconds'],3),flush=True)
    except Exception as e:r=dict(case=list(case),status='failed',error=str(e)); print(r,flush=True)
    r['driver_seconds']=time.perf_counter()-st;rows.append(r)
    (BASE/'results'/'structured_suite.json').write_text(json.dumps(dict(protocol_commit='a6c6440b67210a4e6d1d75b372b5c4e59c6691a0',classification='Predeclared designed structural experiments; not a fully code-frozen holdout or empirical validation',outcomes=rows),indent=2)+'\n')
