#!/usr/bin/env python3
"""Replay R7 author checks and independently verify interior interpolation moments.
Author algorithms and reviewer calculations are labeled separately in output.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np


def run(root: Path, destination: Path):
    destination.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(root/'replication/r7'))
    import core
    import importlib.util
    def load(name, filename):
        spec=importlib.util.spec_from_file_location(name, root/"replication/r7"/filename)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module
    validate=load("review_r7_validate", "validate.py")
    primitive=load("review_r7_primitive", "primitive.py")
    # Redirect every writer before execution; never change author evidence.
    core.OUT=destination;validate.OUT=destination;primitive.OUT=destination
    for name in ('decision.json','decision_coefficients.npz'):
        shutil.copy2(root/'replication/r7/output'/name,destination/name)
    dense=validate.run();primitive_result=primitive.run();validate.replay_decision()
    replay=json.loads((destination/'decision_replay.json').read_text())
    old=core.c.old
    moment_rows=[]
    actions=np.array([[.8,0.,-.5],[.8,0.,.8],[.8,.2,.8]])
    for shape in ((33,49),(65,49),(33,97),(65,97),(97,145)):
        all_states,_=old.grid(*shape);all_states=all_states.reshape(-1,2)
        state=np.array([[2.,1.25]])
        for corr in (-.25,.25):
            model=old.Model(correlation=corr)
            k=core.c.Kernel(state,actions,shape,1/8,model)
            raw,live,disc,flow,effort,_,alpha=old.transition(state[:,None,:],actions[None,:,:],1/8,model)
            assert np.all(live) and np.all(alpha==1)
            for j,action in enumerate(actions):
                y=raw[0,j];mu=y.mean(0);centered=y-mu;raw_cov=centered.T@centered/4
                w=k.weight[0,j]/k.weight[0,j].sum();nodes=all_states[k.index[0,j]]
                grid_mu=w@nodes;z=nodes-grid_mu;grid_cov=(z*w[:,None]).T@z
                spacing=(old.HI-old.LO)/(np.array(shape)-1)
                coord=(y-old.LO)/spacing
                low=old.LO+np.floor(coord)*spacing;high=low+spacing
                inflation=((y-low)*(high-y)).mean(0)
                covariance_error=float(np.max(np.abs(grid_cov-raw_cov-np.diag(inflation))))
                assert covariance_error<2e-14
                assert np.max(np.abs(grid_mu-mu))<2e-14
                moment_rows.append(dict(shape=shape,endpoint_correlation=corr,action=action.tolist(),
                    raw_variance=np.diag(raw_cov).tolist(),grid_variance=np.diag(grid_cov).tolist(),
                    variance_ratio=(np.diag(grid_cov)/np.diag(raw_cov)).tolist(),
                    independent_interpolation_variance_increment=inflation.tolist(),
                    raw_covariance=float(raw_cov[0,1]),grid_covariance=float(grid_cov[0,1]),
                    effective_correlation=float(grid_cov[0,1]/np.sqrt(np.prod(np.diag(grid_cov)))),
                    identity_max_error=covariance_error))
    result=dict(author_dense_replay=dense,author_primitive_replay=primitive_result,
                author_deposited_tensor_replay=replay,reviewer_interior_moments=moment_rows,
                scope='author test reruns are not independent proofs; reviewer moment identity is independently derived and checked against author finite kernel')
    (destination/'replay_and_moments.json').write_text(json.dumps(core.serial(result),indent=2,allow_nan=False)+'\n')
    # Large unchanged author arrays are inputs, not review deliverables.
    (destination/'decision_coefficients.npz').unlink()
    (destination/'decision.json').unlink()
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.root.resolve(),a.out.resolve())
