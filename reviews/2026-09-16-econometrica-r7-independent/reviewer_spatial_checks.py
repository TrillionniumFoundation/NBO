#!/usr/bin/env python3
"""Fixed-calendar spatial sensitivity; does not approximate a diffusion limit.

Reuses the author's positive one-step Kernel construction; independently writes
Bellman maximization and selected-action replay. Both published common meshes
are retained, without frozen neural actions, on every grid. No author outputs
are overwritten. Output JSON is written only to the explicit --output path.
"""
from __future__ import annotations
import argparse, gc, hashlib, itertools, json, os, sys, time
from pathlib import Path
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np
from scipy.sparse import csr_matrix

def execute(root: Path, shape: tuple[int,int], points: list[tuple[float,float]], cache_dir: Path | None = None) -> dict:
    sys.path[:0]=[str(root/'replication/r5'),str(root/'replication/r4')]
    import contracts as c
    old=c.old
    h=1/8
    states, boundary=old.grid(*shape);states=states.reshape(-1,2);boundary=boundary.ravel()
    menu=np.unique(np.concatenate([old.action_mesh((9,9,13)),old.action_mesh((7,7,11))]),axis=0)
    ns,na=len(states),len(menu)
    terminal=old.terminal(states)
    focal=int(np.linalg.norm(states-[2.,1.25],axis=1).argmin())
    assert np.allclose(states[focal],[2.,1.25],rtol=0,atol=1e-14)
    endpoints=[];backend_checks=[];begin=time.perf_counter()
    for correlation in (-.25,.25):
        model=old.Model(k=2.,correlation=correlation)
        kernel=c.Kernel(states,menu,shape,h,model)
        probe=np.sin(np.arange(ns,dtype=float))
        expected=kernel.continuation(probe)
        matrix=csr_matrix((kernel.weight.ravel(),kernel.index.ravel().astype(np.int32),
            np.arange(0,ns*na*16+1,16,dtype=np.int32)),shape=(ns*na,ns))
        matrix.sum_duplicates();matrix.eliminate_zeros()
        error=float(abs((matrix@probe).reshape(ns,na)-expected).max())
        del expected
        assert error<2e-12
        entry=dict(matrix=matrix,base=kernel.base,duration=kernel.duration,effort=kernel.effort,model=model)
        if cache_dir is not None:
            # Disk-backed arrays bound anonymous RAM on larger grids. These
            # are the identical float64 CSR entries, not a compressed kernel.
            folder=cache_dir/f'{shape[0]}x{shape[1]}_{correlation:+.2f}'
            folder.mkdir(parents=True,exist_ok=True)
            for name,arr in [('data',matrix.data),('indices',matrix.indices),('indptr',matrix.indptr),
                             ('base',kernel.base),('duration',kernel.duration),('effort',kernel.effort)]:
                np.save(folder/f'{name}.npy',arr)
            del arr
            entry=dict(model=model,folder=folder)
        endpoints.append(entry)
        backend_checks.append(dict(correlation=correlation,probe_error=error,nnz=int(matrix.nnz)))
        del kernel,matrix;gc.collect()
        print('BUILT',shape,correlation,flush=True)
    if cache_dir is not None:
        for entry in endpoints:
            folder=entry.pop('folder')
            data,indices,indptr=[np.load(folder/f'{name}.npy',mmap_mode='r') for name in ('data','indices','indptr')]
            entry['matrix']=csr_matrix((data,indices,indptr),shape=(ns*na,ns),copy=False)
            for name in ('base','duration','effort'):
                entry[name]=np.load(folder/f'{name}.npy',mmap_mode='r')
    def qbackup(v,lam,d):
        result=None
        for weight,e in zip((1-lam,lam),endpoints):
            q=(e['matrix']@v).reshape(ns,na)
            q+=e['base'];q+=d*e['duration'];q-=2*e['effort']
            q*=weight
            if result is None:result=q
            else:result+=q
        return result
    def selected_replay(policy,lam,d):
        v=terminal.copy()
        for n in range(7,-1,-1):
            actions=menu[policy[n]];value=np.zeros(ns)
            for weight,e in zip((1-lam,lam),endpoints):
                y,live,disc,flow,effort,_,alpha=old.transition(states,actions,h,e['model'])
                ann=-np.expm1(-e['model'].rho*h*alpha)/e['model'].rho
                cont=old.interpolate(v.reshape(shape),y)
                value+=weight*np.mean(flow+d*ann+disc*np.where(live,cont,old.terminal(y)),axis=-1)
            v=value
        return v
    records=[]
    for lam,d in points:
        for adjust in (True,False):
            allowed=np.ones(na,bool) if adjust else abs(menu[:,1])<=1e-14
            values=np.empty((9,ns));values[8]=terminal
            policy=np.empty((8,ns),dtype=np.int32)
            for n in range(7,0,-1):
                q=qbackup(values[n+1],lam,d);q[:,~allowed]=-np.inf
                policy[n]=q.argmax(1);values[n]=q[np.arange(ns),policy[n]]
            q=qbackup(values[1],lam,d)
            classes={}
            for label,pos in [('positive',True),('nonpositive',False)]:
                valid=allowed & ((menu[:,2]>0) if pos else (menu[:,2]<=0))
                masked=np.where(valid,q,-np.inf);policy[0]=masked.argmax(1)
                value=masked[np.arange(ns),policy[0]]
                replay=selected_replay(policy,lam,d)
                error=float(abs(replay-value).max());assert error<2e-11
                classes[label]=dict(value=float(value[focal]),first_action=menu[policy[0,focal]].tolist(),
                    selected_replay_error=error)
            record=dict(lam=lam,d=d,adjustment=adjust,classes=classes,
                delta=classes['positive']['value']-classes['nonpositive']['value'])
            records.append(record);print('RESULT',shape,record,flush=True)
            del q,masked;gc.collect()
    return dict(scope='Fixed eight-date finite-target spatial sensitivity, same common union menu, no neural proposals. Point checks, not regional certificates or a diffusion convergence theorem.',
        shape=list(shape),states=ns,dates=8,physical_horizon=1.,common_actions=na,initial_state=states[focal].tolist(),
        menu_sha256=hashlib.sha256(menu.tobytes()).hexdigest(),backend_checks=backend_checks,
        records=records,storage_backend=('readonly_npy_mmap' if cache_dir is not None else 'memory'),seconds=time.perf_counter()-begin,versions=dict(python=sys.version,numpy=np.__version__))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--shape',default='33,49');ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--cache-dir',type=Path,default=None)
    ap.add_argument('--all-corners',action='store_true');args=ap.parse_args()
    shape=tuple(int(s) for s in args.shape.split(','))
    if len(shape)!=2 or any(s<3 or s%2==0 for s in shape):raise ValueError('two odd grid sizes >=3 required')
    points=[(0.,.4),(0.,.45),(.25,.4),(.25,.45),(.125,.425)] if args.all_corners else [(.25,.45),(0.,.4)]
    result=execute(args.root,shape,points,args.cache_dir);args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
