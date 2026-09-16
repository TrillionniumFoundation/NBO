"""R6 utilities. Historical sources and evidence are immutable inputs."""
from __future__ import annotations
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import hashlib,json,sys,time,platform
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'replication/r6/output'
OUT.mkdir(parents=True,exist_ok=True)
sys.path[:0]=[str(ROOT/'replication/r5'),str(ROOT/'replication/r4')]
def jsonable(x):
    if isinstance(x,dict):return {str(k):jsonable(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [jsonable(v) for v in x]
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    return x
def save(name,data):
    p=OUT/name;p.write_text(json.dumps(jsonable(data),indent=2,allow_nan=False)+'\n');return p
def timed(fn,repeats=3):
    runs=[];values=[]
    for _ in range(repeats):
        t=time.perf_counter();values.append(fn());runs.append(time.perf_counter()-t)
    return values[0],dict(seconds=float(np.median(runs)),samples=runs)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def accelerate_kernel(e):
    """CSR execution of the IDENTICAL positive interpolation rows.
    Keep the original selected-policy evaluator for an independent arithmetic
    path. The equality check is recorded; no precision or model is changed.
    """
    k=e.common
    if not hasattr(k,'index') or getattr(k,'csr_verified',False):return None
    from scipy.sparse import csr_matrix
    start=time.perf_counter();ns,na,w=k.index.shape
    matrix=csr_matrix((k.weight.reshape(-1),k.index.reshape(-1).astype(np.int32),
        np.arange(0,ns*na*w+1,w,dtype=np.int32)),shape=(ns*na,ns))
    original=k.continuation;v=np.sin(np.arange(ns,dtype=float))
    err=float(abs((matrix@v).reshape(ns,na)-original(v)).max())
    assert err<2e-12
    k.original_continuation=original
    k.continuation=lambda value:(matrix@value).reshape(ns,na)
    k.csr_verified=True;k.csr_check=dict(max_discrepancy=err,setup_seconds=time.perf_counter()-start,
        model_change=False,precision='float64',extra_index_bytes=int(matrix.indices.nbytes+matrix.indptr.nbytes))
    e.build_seconds=getattr(e,'build_seconds',0.)+k.csr_check['setup_seconds']
    return k.csr_check
