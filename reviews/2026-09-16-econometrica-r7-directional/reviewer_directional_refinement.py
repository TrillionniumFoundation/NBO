#!/usr/bin/env python3
"""R7 re-review: fixed-calendar, one-coordinate spatial diagnostics.

Use the exact no-deliberate-adjustment subproblem of the original full menu.
Before reducing to its common actions, verify that every admissible frozen
proposal duplicates a common action exactly. Reuse the author's transition law,
but implement Bellman maximization and selected-policy replay here. These are
finite-menu point solves, not new continuum certificates or diffusion proofs.
"""
from __future__ import annotations
import argparse
import gc
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path
from types import SimpleNamespace

for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
from scipy.sparse import csr_matrix


def serial(obj):
    if isinstance(obj, dict): return {str(k): serial(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)): return [serial(v) for v in obj]
    if isinstance(obj, np.ndarray): return obj.tolist()
    if isinstance(obj, np.generic): return obj.item()
    return obj


def run(root: Path, output: Path):
    sys.path[:0] = [str(root/'replication/r5'), str(root/'replication/r4')]
    import contracts as c
    import solver as old
    full = np.unique(np.concatenate((old.action_mesh((9,9,13)), old.action_mesh((7,7,11)))), axis=0)
    menu = full[np.abs(full[:,1]) <= 1e-14]
    assert np.all(menu[:,1] == 0)
    triples = set(map(tuple, menu))
    proposal_audit = []
    for seed in (101,202,303):
        with np.load(root/f'replication/r4/output/safe_policy_{seed}.npz') as z:
            p = z['policies'].reshape(8,-1,3)
        allowed = p[np.abs(p[:,:,1]) <= 1e-14]
        unique = np.unique(allowed,axis=0)
        missing = [a.tolist() for a in unique if tuple(a) not in triples]
        assert not missing, 'Cannot drop a nonduplicated zero-adjustment proposal'
        assert np.all(allowed[:,1] == 0)
        proposal_audit.append(dict(seed=seed, admissible_proposals=len(allowed),
                                   distinct=len(unique), nonduplicates=missing))
    author = json.loads((root/'replication/r7/output/decision.json').read_text())
    author_values = {(r['theta'],r['d'],r['sign']): r['value'] for r in author['checks'] if not r['adjustment']}
    points = [(0.,.4),(0.,.45),(.25,.4),(.25,.45),(.125,.425)]
    shapes = [(33,49),(65,49),(33,97),(65,97),(97,49),(33,145),(97,145)]
    results = dict(manuscript_commit='fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17',
                   states=['preference index u','wealth X'], horizon=1., dates=8,
                   target='exact no-adjustment common menu after exact duplicate audit of frozen proposals',
                   common_full_actions=len(full), no_adjustment_actions=len(menu),
                   proposal_audit=proposal_audit, points=points, grids=[],
                   environment=dict(python=sys.version, numpy=np.__version__, platform=platform.platform()),
                   scope='same eight dates, fixed common action menu, author transition law; pointwise finite solves, not regional/diffusion certification')
    def save():
        output.write_text(json.dumps(serial(results), indent=2, allow_nan=False)+'\n')
    save()
    for shape in shapes:
        started = time.perf_counter()
        ss,bd = old.grid(*shape); states = ss.reshape(-1,2); ns=len(states)
        center = int(np.linalg.norm(states-[2.,1.25],axis=1).argmin())
        assert np.max(np.abs(states[center]-[2.,1.25])) < 2e-15
        kernels=[]; matrices=[]; backend=[]
        for corr in (-.25,.25):
            k=c.Kernel(states, menu, shape, 1/8, old.Model(correlation=corr))
            n,a,w=k.index.shape
            matrix=csr_matrix((k.weight.reshape(-1),k.index.reshape(-1).astype(np.int32),
                               np.arange(0,n*a*w+1,w,dtype=np.int32)),shape=(n*a,n))
            test=np.sin(np.arange(n,dtype=float))
            error=float(np.max(np.abs((matrix@test).reshape(n,a)-k.continuation(test))))
            assert error < 2e-12
            kernels.append(k);matrices.append(matrix);backend.append(error)
        terminal=old.terminal(states); rows=np.arange(ns)
        def qvalue(v,lam,d):
            return sum(weight*(k.base+d*k.duration-2*k.effort+(matrix@v).reshape(ns,len(menu)))
                       for weight,k,matrix in zip((1-lam,lam),kernels,matrices))
        def evaluate(policy,lam,d):
            v=terminal.copy()
            for n in range(7,-1,-1):
                p=policy[n]
                v=sum(weight*(k.base[rows,p]+d*k.duration[rows,p]-2*k.effort[rows,p]+k.selected(p,v))
                      for weight,k in zip((1-lam,lam),kernels))
            return v
        grid_result=dict(shape=shape,states=ns,backend_replay_max=max(backend),rows=[])
        for lam,d in points:
            v=terminal.copy(); policies=np.empty((8,ns),dtype=np.int32)
            for n in range(7,0,-1):
                q=qvalue(v,lam,d);p=q.argmax(1);policies[n]=p;v=q[rows,p]
            q=qvalue(v,lam,d);record=dict(lam=lam,d=d)
            for sign,allowed in [('positive',menu[:,2]>0),('nonpositive',menu[:,2]<=0)]:
                candidate=np.where(allowed,q,-np.inf);p=candidate.argmax(1);value=candidate[rows,p]
                policies[0]=p
                replay=evaluate(policies,lam,d)
                error=float(np.max(np.abs(replay-value)))
                assert error < 2e-11
                record[sign]=dict(value=float(value[center]), first_action=menu[p[center]],
                                  selected_policy_replay_max=error)
                if shape==(33,49) and (lam,d,sign) in author_values:
                    err=abs(value[center]-author_values[(lam,d,sign)])
                    record[sign]['author_full_target_value_error']=float(err)
                    assert err < 2e-11
            record['delta']=record['positive']['value']-record['nonpositive']['value']
            grid_result['rows'].append(record)
            print(json.dumps(serial(dict(shape=shape,lam=lam,d=d,delta=record['delta']))),flush=True)
        grid_result['reviewer_elapsed_seconds']=time.perf_counter()-started
        results['grids'].append(grid_result);save()
        del q,candidate,value,replay,v,policies,kernels,matrices,k,matrix
        gc.collect()
    return results


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True)
    run(args.root.resolve(),args.output.resolve())
