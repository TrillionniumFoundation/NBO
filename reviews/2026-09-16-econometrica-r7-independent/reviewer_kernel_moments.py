#!/usr/bin/env python3
"""Audit raw and interpolated one-step moments at an interior economic state.

Reuses the author's transition constructor and Kernel; calculates moments and
an independent one-dimensional interpolation identity. This is a local
consistency diagnostic, not a value-error or diffusion convergence proof.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
import numpy as np


def audit(root: Path) -> dict:
    sys.path.insert(0, str(root / 'replication/r5'))
    import contracts as c
    old = c.old
    focal = np.array([[2.0, 1.25]])
    rows = []
    # Include fixed-time spatial and fixed-space temporal paths, and both
    # available endpoint laws. The economic controls and state stay fixed.
    cases = [(33,49,8,t) for t in (-.2, 0., .1, .2)]
    cases += [(33,49,H,0.) for H in (4,16,32)]
    cases += [(nu,nx,8,0.) for nu,nx in ((49,73),(65,97),(129,193))]
    cases += [(49,73,8,.2),(65,97,8,.2)]
    for nu,nx,H,theta in cases:
        h=1.0/H
        for corr in (-.25,.25):
            shape=(nu,nx); action=np.array([[.8,theta,.8]])
            model=old.Model(k=2.,correlation=corr)
            kernel=c.Kernel(focal,action,shape,h,model)
            y,live,disc,flow,effort,d,alpha=old.transition(focal[:,None,:],action[None,:,:],h,model)
            assert bool(live.all()) and np.allclose(alpha,1.)
            raw=y.reshape(-1,2)
            raw_mean=raw.mean(axis=0)
            raw_cov=(raw-raw_mean).T @ (raw-raw_mean)/len(raw)
            ss,_=old.grid(*shape); states=ss.reshape(-1,2)
            indices=kernel.index[0,0].astype(int)
            weights=kernel.weight[0,0]
            assert abs(weights.sum()-np.exp(-model.rho*h))<2e-14
            weights=weights/weights.sum() # undo common discount; no killing
            nodes=states[indices]
            mean=weights@nodes
            cov=(nodes-mean).T @ (weights[:,None]*(nodes-mean))
            du=(old.HI[0]-old.LO[0])/(nu-1)
            # Exact variance increase for barycentric interpolation on a
            # uniform grid: E[(Y-left)(right-Y)] >= 0, at the same mean.
            coord=(raw[:,0]-old.LO[0])/du
            left=old.LO[0]+np.floor(coord)*du
            extra=float(np.mean((raw[:,0]-left)*(left+du-raw[:,0])))
            assert np.max(abs(mean-raw_mean))<2e-14
            assert abs(cov[0,0]-raw_cov[0,0]-extra)<2e-14
            if theta==0 and model.sigma_u*np.sqrt(h)<=du:
                analytic_var=model.sigma_u*np.sqrt(h)*du
                assert abs(cov[0,0]-analytic_var)<2e-14
            else:
                analytic_var=None
            rows.append(dict(shape=list(shape),steps=H,h=h,theta=theta,correlation=corr,
                state=focal[0].tolist(),action=action[0].tolist(),raw_mean=raw_mean.tolist(),
                interpolated_mean=mean.tolist(),raw_covariance=raw_cov.tolist(),
                interpolated_covariance=cov.tolist(),preference_variance_inflation=float(cov[0,0]/raw_cov[0,0]),
                preference_variance_extra=extra,preference_variance_rate=float(cov[0,0]/h),
                analytic_zero_drift_variance=analytic_var,
                minimum_probability=float(weights.min()),probability_sum=float(weights.sum())))
    paths=['replication/r4/solver.py','replication/r5/contracts.py']
    return dict(scope='Local interior moments of the author-generated finite kernel versus its pre-interpolation quadrature, not an independent transition-law implementation or a value-error certificate.',
                formulas={'zero_drift_one_cell':'Var_grid = sigma_u * sqrt(h) * Delta_u when sigma_u*sqrt(h) <= Delta_u',
                          'general_variance_increment':'E[(Y-left(Y))*(right(Y)-Y)]'},
                source_sha256={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},rows=rows)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();result=audit(args.root.resolve());args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    for r in result['rows']:
        if r['correlation']==-.25: print(r['shape'],r['steps'],r['theta'],r['preference_variance_inflation'])
