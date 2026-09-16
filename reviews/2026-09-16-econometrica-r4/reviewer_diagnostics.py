#!/usr/bin/env python3
"""Selected independent review diagnostics for NBO R4, pinned to f20dcb1.

Run from the review branch with NumPy, SciPy and CPU PyTorch installed:
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python reviews/2026-09-16-econometrica-r4/reviewer_diagnostics.py

Only two author resource cases are retrained: d=4, seeds 101 and 202.
Files are written under this review's rerun/ directory, never author output/.
The actor-free ablation retains the trained convex critics and online optimizer.
The reward-level exercise deliberately changes the stopped economy; it is not
an equivalent utility representation. The game is independently solved by a
2x2 linear system and checked by full best responses at every date.
Successful assertions mean these selected checks reproduced, not publication
readiness, a continuum certificate, or replication of all manuscript runs.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import math
import os
import platform
import sys
import time
from pathlib import Path
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
import scipy
import torch

PIN = "f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32"
EXPECTED = {
    "solver.py": "e283614b137cd898d49a06f82d5938dc3c6a9cca",
    "coupled_resource.py": "7a8a82af0b343685b3edc8c5e24a6e86b0f5d9ad",
}

def source_identity(source_dir: Path) -> dict:
    result = {}
    for name, expected in EXPECTED.items():
        data = (source_dir / name).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if blob != expected:
            raise RuntimeError(f"Refusing unreviewed author source: {name}: {blob}")
        result[name] = {"bytes": len(data), "git_blob": blob,
                        "sha256": hashlib.sha256(data).hexdigest()}
    return result

def evaluate(d,seed):
    row=json.loads((ROOT/f'resource_results_{d}_{seed}.json').read_text());data=np.load(ROOT/f'resource_weights_{d}_{seed}.npz');rng=np.random.default_rng(0)
    critics=[];actors=[];A,shock,B=cr.primitives(d)
    for n in range(3):
        c=cr.Critic(d,rng)
        for key in ['W','b','c','lin','const']:setattr(c,key,data[f'critic.{n}.{key}'].copy())
        critics.append(c);a=cr.Actor(d,B)
        a.load_state_dict({k:torch.as_tensor(data[f'actor.{n}.{k}']) for k in a.state_dict()});actors.append(a)
    critics.append(cr.Critic(d,rng,terminal=True));x0=np.array(row['raw']['test_states']);records={}
    policies={}
    for mode in ['actor','zero']:
        states=x0[:,None,:];cost=np.zeros(len(x0));iters=[];gaps=[];common=[];start=time.perf_counter();policies[mode]=[]
        for n in range(3):
            flat=states.reshape(-1,d)
            with torch.no_grad():proposal=actors[n](torch.as_tensor(flat)).numpy() if mode=='actor' else np.zeros_like(flat)
            u,_,gap,it=cr.greedy(critics[n+1],flat,proposal,A,shock,B);policies[mode].append(u.copy());iters.append(it);gaps.append(float(gap.max()))
            if mode=='actor':
                z,_,_,_=cr.greedy(critics[n+1],flat,np.zeros_like(flat),A,shock,B)
                common.append(float(abs(u-z).max()))
            u=u.reshape(states.shape);zz=states-1
            cost+=((zz*zz).mean(-1)+.2*zz.mean(-1)**2+.1*(u*u).mean(-1)).mean(1)
            states=((states@A.T+u)[:,:,None,:]+shock[None,None,:,:]).reshape(len(x0),-1,d)
        zz=states-1;cost+=((zz*zz).mean(-1)+.2*zz.mean(-1)**2).mean(1)
        ref=np.array(row['raw']['reference_cost']);gapref=np.array(row['raw']['reference_gap'])
        records[mode]={'cost':cost.tolist(),'upper_loss_max':float((cost-ref+gapref).max()),'iterations_by_date':iters,'gap_by_date':gaps,'common_state_action_difference':common}
    result={'d':d,'seed':seed,'actor':records['actor'],'zero':records['zero'],'max_abs_lifetime_cost_difference':float(abs(np.array(records['actor']['cost'])-records['zero']['cost']).max()),'replay_vs_author_rerun_max':float(abs(np.array(records['actor']['cost'])-row['raw']['neural_cost']).max())}
    return result

def normalization(flow_shift, nu=33, nx=49, dates=8):
    m=s.Model();states,bd=s.grid(nu,nx);sf=states.reshape(-1,2);h=1/dates
    vals=s.terminal(states);duration=np.zeros_like(vals);pols=[]
    for n in range(dates-1,-1,-1):
        best=np.full(len(sf),-np.inf);pol=np.zeros((len(sf),3));acts=s.action_mesh((5,5,7))
        for aa in np.array_split(acts,math.ceil(len(acts)/32)):
            y,live,disc,flow,_,_,alpha=s.transition(sf[:,None,:],aa[None,:,:],h,m)
            ann=-np.expm1(-m.rho*h*alpha)/m.rho
            q=(flow+flow_shift*ann+disc*np.where(live,s.interpolate(vals,y),s.terminal(y))).mean(-1)
            j=q.argmax(1);v=q[np.arange(len(sf)),j];use=v>best;best[use]=v[use];pol[use]=aa[j[use]]
        y,live,disc,flow,_,_,alpha=s.transition(sf,pol,h,m)
        ann=-np.expm1(-m.rho*h*alpha)/m.rho
        dur=(ann+disc*live*s.interpolate(duration,y)).mean(-1).reshape(nu,nx);dur[bd]=0
        vals=best.reshape(nu,nx);vals[bd]=s.terminal(states)[bd];duration=dur;pols.append(pol.reshape(nu,nx,3))
    return {'flow_shift':flow_shift,'initial_value':float(vals[nu//2,nx//2]),'initial_policy':pols[-1][nu//2,nx//2].tolist(),'discounted_operating_duration':float(duration[nu//2,nx//2]),'grid':[nu,nx],'dates':dates,'action_counts':[5,5,7],'interpretation':'Deliberate alternative stopped economy: running reward + flow_shift, terminal G unchanged; not an equivalent utility representation.'}

def game_check(N=4):
    delta=.95;k=.4;P=np.array([[.8,.2],[.2,.8]]);D=np.array([1.,1.3]);states=list(itertools.product(range(2),repeat=3))
    V=np.zeros((N+1,2,2,2,2));policy=np.zeros((N,2,2,2,2))
    for i,j,z in states:V[N,:,i,j,z]=[.05*i,.05*j]
    def expect(w,x,y):return float(np.array([1-x,x])@w@np.array([1-y,y]))
    for n in range(N-1,-1,-1):
        for i,j,z in states:
            W=V[n+1,0]@P[z];Z=V[n+1,1]@P[z]
            a1=delta*(W[1,0]-W[0,0])/k;b1=delta*(W[1,1]-W[1,0]-W[0,1]+W[0,0])/k
            a2=delta*(Z[0,1]-Z[0,0])/k;b2=delta*(Z[1,1]-Z[1,0]-Z[0,1]+Z[0,0])/k
            # Solve the two interior affine best responses independently of the author's iteration.
            x,y=np.linalg.solve(np.array([[1.,-b1],[-b2,1.]]),np.array([a1,a2]));assert 0<x<1 and 0<y<1
            policy[n,:,i,j,z]=[x,y]
            V[n,0,i,j,z]=i/3*(D[z]-i/3-j/3)-k*x*x/2+delta*expect(W,x,y)
            V[n,1,i,j,z]=j/3*(D[z]-i/3-j/3)-k*y*y/2+delta*expect(Z,x,y)
    expected=np.tile(delta*((P@D)/3-1/9)/(k+delta/9),(N,1));expected[-1]=delta*.05/k
    formula_error=float(abs(policy-expected[:,None,None,None,:]).max())
    signed=np.zeros((N,2));br_policy_error=0.
    for player in range(2):
        br=V[-1,player].copy()
        for n in range(N-1,-1,-1):
            new=np.zeros((2,2,2))
            for i,j,z in states:
                W=br@P[z];r=policy[n,1-player,i,j,z]
                marginal=((1-r)*(W[1,0]-W[0,0])+r*(W[1,1]-W[0,1])) if player==0 else ((1-r)*(W[0,1]-W[0,0])+r*(W[1,1]-W[1,0]))
                own=float(np.clip(delta*marginal/k,0,1));x,y=(own,r) if player==0 else (r,own)
                qi=(i if player==0 else j)/3;qj=(j if player==0 else i)/3
                new[i,j,z]=qi*(D[z]-qi-qj)-k*own*own/2+delta*expect(W,x,y)
                br_policy_error=max(br_policy_error,abs(own-policy[n,player,i,j,z]))
            signed[n,player]=float((new-V[n,player]).max());br=new
    assert formula_error<1e-12 and np.max(signed)<1e-12
    return dict(horizon=N,derivation='Interior 2x2 affine best-response solve, followed by independent full unilateral backward induction at every date.',formula='a_n(D)=delta*(E[D_next|D]/3-1/9)/(kappa+delta/9), n<N-1; a_last=delta*0.05/kappa',policy_by_date_and_demand=expected.tolist(),max_formula_error=formula_error,max_capacity_dependence=float(np.ptp(policy,axis=(2,3)).max()),signed_best_response_value_max_by_date_player=signed.tolist(),positive_dynamic_gain_max=float(max(0.,signed.max())),max_best_response_policy_error=float(br_policy_error),author_metric_scope='Source diagnostics.py::game_test updates maxgain only after its date loop; this independent check covers every date. No profitable deviation is found.')

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path,
                        default=Path(__file__).resolve().parents[2] / "replication/r4")
    parser.add_argument("--out", type=Path,
                        default=Path(__file__).resolve().parent / "rerun")
    parser.add_argument("--reuse-existing", action="store_true",
                        help="Use prior reviewer resource reruns in OUT/resource; do not retrain.")
    args = parser.parse_args()
    source = args.source_dir.resolve(); out = args.out.resolve()
    if out == source or source in out.parents:
        raise ValueError("Output must not be inside the author source/replication directory")
    identities = source_identity(source)
    sys.path.insert(0, str(source))
    global s, cr, ROOT
    import solver as s
    import coupled_resource as cr
    ROOT = out / "resource"; ROOT.mkdir(parents=True, exist_ok=True)
    for seed in [101, 202]:
        if not args.reuse_existing:
            cr.run(4, seed, out=ROOT)
        for name in [f"resource_results_4_{seed}.json", f"resource_weights_4_{seed}.npz"]:
            if not (ROOT / name).is_file():
                raise FileNotFoundError(ROOT / name)
    removal = [evaluate(4, seed) for seed in [101, 202]]
    for row in removal:
        assert row["actor"]["upper_loss_max"] < 1e-3
        assert row["zero"]["upper_loss_max"] < 1e-3
        assert row["max_abs_lifetime_cost_difference"] < 1e-7
        assert row["replay_vs_author_rerun_max"] < 1e-10
    economy = [normalization(shift, nu, nx, dates)
               for nu, nx, dates in [(17, 25, 4), (33, 49, 8)]
               for shift in [0., 1.]]
    assert abs(economy[0]["initial_value"] + 1.1405481993348514) < 1e-10
    assert abs(economy[2]["initial_value"] + 1.1369156510361464) < 1e-10
    for i in [0, 2]:
        assert abs(economy[i]["initial_policy"][2] + .5) < 1e-12
        assert abs(economy[i+1]["initial_policy"][2] - .8) < 1e-12
    inputs = {}
    for path in sorted(ROOT.glob("*")):
        if path.is_file(): inputs[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    result = {
        "reviewed_commit": PIN,
        "status": "selected_review_checks_completed",
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "scipy": scipy.__version__, "torch": torch.__version__,
                        "torch_threads": torch.get_num_threads()},
        "verified_author_sources": identities,
        "resource_cases": [{"d":4,"seed":seed} for seed in [101,202]],
        "resource_reruns_reused": bool(args.reuse_existing),
        "resource_input_file_sha256": inputs,
        "actor_removal": removal,
        "stopped_economy_reward_level": economy,
        "game": game_check(),
        "cost_panel_arithmetic_from_rounded_manuscript_table": [
            {"k":k,"effort_C":c,"coefficient_weighted_cost_kC":k*c}
            for k,c in [(.5,.014614),(2.,.009888),(8.,.001432)]],
        "limits": ["Two of nine resource dimension-seed combinations were retrained.",
                   "No NDU neural retraining or all-manuscript replication is asserted.",
                   "NDU sensitivity uses the positive finite transition, not exact Brownian stopping.",
                   "The all-date game check solves the stated model independently; it does not repair author source.",
                   "No PDF build/render, interval arithmetic, or uniform PDE error certificate was performed."]
    }
    target = out / "diagnostic_results.json"
    target.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print("Reviewer results:", target)
    for row in removal:
        print("ACTOR_REMOVAL", row["seed"], row["max_abs_lifetime_cost_difference"],
              row["actor"]["upper_loss_max"], row["zero"]["upper_loss_max"])
    print("GAME_ALL_DATE_GAIN", result["game"]["positive_dynamic_gain_max"])

if __name__ == "__main__":
    main()
