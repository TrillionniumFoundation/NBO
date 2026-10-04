"""Recover a distributionally equivalent driver from continuous state history.
The extra one-dimensional driver is private randomization, not latent economic
information. Componentwise clipping makes this null-space term indispensable.
"""
from __future__ import annotations
from common import *

def matrices(d):
    if d<1 or P['idiosyncratic_sigma']<=0:raise ValueError('full row rank required')
    si=P['idiosyncratic_sigma'];sc=P['common_sigma']
    S=np.concatenate([si*np.eye(d),sc*np.ones((d,1))],axis=1)
    Q=S@S.T;right=S.T@np.linalg.inv(Q)
    null=np.r_[np.full(d,-sc/si),1.];null/=np.linalg.norm(null)
    return S,right,null

def recover(state_increment,integrated_drift,private_increment):
    x=np.asarray(state_increment,dtype=float);b=np.asarray(integrated_drift,dtype=float)
    if x.shape!=b.shape or x.ndim!=2:raise ValueError('expected matching batch by state arrays')
    S,right,null=matrices(x.shape[1]);z=np.asarray(private_increment,dtype=float)
    if z.shape!=(len(x),) or not np.isfinite(x).all() or not np.isfinite(b).all() or not np.isfinite(z).all():raise ValueError('invalid observations')
    return (x-b)@right.T+z[:,None]*null

def audit(out):
    rows=[]
    for d in PROTOCOL['dimensions']:
        S,A,n=matrices(d);Q=S@S.T
        rng=np.random.default_rng(12124000+d);w=rng.normal(size=(4096,d+1));private=rng.normal(size=4096)
        drift=rng.normal(size=(4096,d))*.01;dy=w@S.T+drift
        reconstructed=recover(dy,drift,private)
        rows.append(dict(dimension=d,aggregate_reconstruction_error=float(np.max(abs(reconstructed@S.T-(dy-drift)))),covariance_identity_error=float(np.max(abs(A@Q@A.T+np.outer(n,n)-np.eye(d+1)))),null_projection_error=float(np.max(abs(S@n))),sample_covariance_error=float(np.max(abs(np.cov(reconstructed,rowvar=False)-np.eye(d+1)))),naive_right_inverse_covariance_rank=int(np.linalg.matrix_rank(A@Q@A.T))))
    result=dict(records=rows,assumptions=['continuous noiseless observation of the full state path','known drift, model coefficients and own held actions','exact time-integrated drift in the mathematical observation model','one independent private Brownian randomization'],not_implied=['recovery from discrete noisy observations','pathwise recovery of the original unobserved null component','state-only deterministic Markov implementation'],meaning='The right-inverse plus independent null component has identity bracket; Levy characterization gives Brownian drivers. The closed-loop law equals the prescribed R11 controller law. Numerical identities are regression checks, not the proof.')
    write(Path(out)/'OBSERVATION.json',result);return result
