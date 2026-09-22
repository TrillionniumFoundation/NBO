"""R18: check the trainable-envelope/MPFR-certificate bridge at all 60 checkpoints.

This is a new audit of immutable R17 experiments, not a new training experiment.
All retained cell certificates and networks are checked against the R17 source/
result manifest. The floating proposal graph is re-evaluated, then its exact
stored binary64 logits are enclosed by MPFR. Two designated full certificates
are re-executed separately by reproduce.py. No sampled point can establish a
complete-domain claim here.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
import argparse, csv, gzip, hashlib, json, platform, sys, time
import numpy as np
import torch
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
R17=ROOT/'revisions/2026-09-23-r17'
R16=ROOT/'revisions/2026-09-23-r16'
sys.path[:0]=[str(R16/'replication'), str(R17/'replication')]
import mpfr_interval as M
import accessibility_certificate as C
from accessibility_neural import load_model
import interval_objective as D
I,Q=M.I,M.I.rational

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_inputs() -> dict:
    manifest=json.loads((R17/'SCIENTIFIC_REPRODUCTION.json').read_text())
    checked=0
    for path, expected in manifest['sha256'].items():
        p=ROOT/path
        if not p.is_file() or sha(p)!=expected:
            raise RuntimeError(f'Immutable scientific input changed or missing: {path}')
        checked+=1
    return {'files_checked':checked, 'manifest_sha256':sha(R17/'SCIENTIFIC_REPRODUCTION.json'),
            'source_commit':manifest['source_commit'], 'review_commit':manifest['review_base']}

def softmax_interval(logits: np.ndarray, tau: F=F(3,20)) -> I:
    """Enclose tau*log(1+sum(exp(logits/tau))), including its exact zero logit."""
    logits=np.asarray(logits,dtype=np.float64).reshape(-1)
    if not np.isfinite(logits).all():
        raise ArithmeticError('Nonfinite proposal logits')
    values=np.concatenate((logits,np.array([0.])))
    shift=float(max(values))
    return I(shift)+Q(tau)*M.log(M.add_reduce(M.exp((I(values)-I(shift))/Q(tau))))

def bridge(certified: np.ndarray, proposal: np.ndarray, nt: int=4) -> dict:
    """certified: [nt,nspace,2], nonnegative directed cell upper endpoints.

    The discrepancy is an implementation/rounding correction, not a claim that
    the float proposal graph is itself an enclosure. Zero is a common logit;
    comparing against clipped logits leaves the maximum unchanged.
    """
    certified=np.asarray(certified,dtype=np.float64)
    proposal=np.asarray(proposal,dtype=np.float64)
    if certified.shape!=proposal.shape or certified.shape[0]!=nt or certified.shape[-1]!=2:
        raise ValueError('Shape mismatch or incomplete sign pair')
    if not (np.isfinite(certified).all() and np.isfinite(proposal).all()) or np.any(certified<0):
        raise ArithmeticError('Invalid certificate endpoint')
    total=I(0); smooth=I(0); correction=I(0); entropy=I(0); floatmax=I(0)
    slabs=[]
    for j in range(nt):
        mass=(M.exp(-Q('.04')*Q(F(j,nt)))-M.exp(-Q('.04')*Q(F(j+1,nt))))/Q('.04')
        bc=I(0);ls=I(0);df=I(0);fm=I(0);detail=[]
        for sign in range(2):
            b=certified[j,:,sign];a=proposal[j,:,sign]
            delta=np.maximum((I(b)-I(np.maximum(a,0))).hi,0)
            d=float(delta.max());e=float(b.max());mx=float(max(0,a.max()))
            l=softmax_interval(a)
            bc=bc+I(e); ls=ls+l;df=df+I(d);fm=fm+I(mx)
            detail.append({'certified_maximum':e, 'proposal_maximum':mx,
                           'softmax_interval':l.pair(),'endpoint_correction_upper':d})
        total=total+mass*bc;smooth=smooth+mass*ls;correction=correction+mass*df;floatmax=floatmax+mass*fm
        entropy=entropy+mass*2*Q(F(3,20))*M.log(I(certified.shape[1]+1))
        slabs.append({'slab':j,'mass':mass.pair(),'signs':detail})
    bound=smooth+I(float(correction.hi))
    # A strict interval separation is used for these archived examples. General
    # theorem validity does not require that a computer resolve equality cases.
    if float(total.hi)>float(bound.lo):
        raise AssertionError('Unable to resolve the proposed objective bridge')
    if float(smooth.hi) > float((floatmax+entropy).hi)+1e-12:
        raise AssertionError('Softmax entropy bound failed')
    return {'directed_certificate_reconstruction':total.pair(),
            'directed_proposal_smoothmax':smooth.pair(),
            'endpoint_correction_upper':float(correction.hi),
            'certified_objective_upper':float(bound.hi),
            'float_maximum_sum_interval':floatmax.pair(),
            'entropy_allowance_upper':float(entropy.hi),'slabs':slabs}

def audit_all(out: Path) -> list[dict]:
    out.mkdir(parents=True,exist_ok=True)
    torch.set_num_threads(1);torch.set_default_dtype(torch.float64)
    provenance=validate_inputs();tick=time.perf_counter()
    exact,indices=C.cell_grid(4,16,16)
    s=D.I(torch.tensor(exact.lo),torch.tensor(exact.hi));rows=[]
    expected_indices=[tuple(i) for i in indices]
    for arch in ['accessible','allface']:
      for seed in range(17100,17110):
        folder=R17/'results'/arch/f'seed{seed}'
        for k in [0,100,400]:
            cp=folder/f'certificate{k}.json';npth=folder/f'network_step{k:04d}.json'
            cert=json.loads(cp.read_text())
            if cert['network_sha256']!=sha(npth) or cert['failed_cells'] or cert['skipped_cells']:
                raise RuntimeError('Mismatched or incomplete input certificate')
            with gzip.open(cp.with_suffix('.cells.json.gz'),'rt') as f:cells=json.load(f)
            if [tuple(r['cell']) for r in cells]!=expected_indices or len(cells)!=1024:
                raise RuntimeError('Missing, duplicate, reordered, or unaccounted domain cell')
            actor,critic,network=load_model(npth)
            with torch.no_grad():
                ru,rp=D.residuals(s,actor,critic,all_faces=(arch=='allface'))
            logits=np.stack([ru.hi.numpy(),-rp.lo.numpy()],axis=-1).reshape(4,256,2)
            endpoints=np.array([[r['positive_optimal_residual'],r['negative_policy_residual']] for r in cells]).reshape(4,256,2)
            v=bridge(endpoints,logits)
            if not v['directed_certificate_reconstruction'][0]<=cert['t0_regret_upper']<=v['directed_certificate_reconstruction'][1]+1e-12:
                raise RuntimeError('Stored certificate not reproduced by its cell record')
            # Preserve exact logits: independently executable post-hoc comparison.
            lp=out/f'logits_{arch}_{seed}_{k}.npz'
            np.savez_compressed(lp,proposal=logits,certified=endpoints)
            v.update({'architecture':arch,'seed':seed,'step':k,'width':network['width'],
                      'historical_certificate':cert['t0_regret_upper'],'complete_cells':1024,
                      'network_sha256':sha(npth),'certificate_sha256':sha(cp),'logits_sha256':sha(lp),
                      'status':'PASS_COMPLETE_COVER_OBJECTIVE_BRIDGE'})
            rows.append(v)
    (out/'objective_bridge.json').write_text(json.dumps(rows,indent=2)+'\n')
    fields=['architecture','seed','step','width','historical_certificate','certified_objective_upper','endpoint_correction_upper','entropy_allowance_upper']
    with (out/'objective_bridge.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    summary={'status':'PASS','objects':len(rows),'cells_checked':sum(r['complete_cells'] for r in rows),
             'new_training':False,'role':'Post-hoc theorem audit of immutable, predeclared R17 training runs',
             'correction_min':min(r['endpoint_correction_upper'] for r in rows),
             'correction_max':max(r['endpoint_correction_upper'] for r in rows),
             'entropy_allowance_upper':rows[0]['entropy_allowance_upper'],
             'provenance':provenance,'torch':torch.__version__,'numpy':np.__version__,
             'mpfr':M.VERSION,'python':platform.python_version(),'platform':platform.platform(),
             'wall_seconds':time.perf_counter()-tick,'threads':1}
    (out/'objective_bridge_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=HERE.parent/'results/objective_bridge')
    a=p.parse_args();audit_all(a.out)
