"""Full-horizon support prices and restart propagation in the unchanged 2D model.
The supports are upper bounds on max E[lambda operating reward - revision cost].
Their conversion uses LOWER operating witnesses; no deterministic-only floor is
used for a randomized claim. All array operations carry signed-int overflow checks.
"""
from pathlib import Path
from fractions import Fraction as F
import sys,json,time,hashlib,resource
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'2026-09-24-r38'
sys.path.insert(0,str(OLD/'replication'))
from multistate import Boxes,witnesses,S,ceildiv,MODEL
PRICES=[F(x) for x in ('0','1/4','1/2','1','2','4','8','16','32','64','128')]
MUS=(0,1,4,16,64)

def mul(v,lam,upper):
    z=v*lam.numerator;assert np.max(np.abs(z))<2**62
    return ceildiv(z,lam.denominator) if upper else z//lam.denominator

def integral(v):return F(int(v.sum(dtype=np.int64)),S*v.size)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')

def compute(T,n,eps=F(1,2),store=True):
    tic=time.perf_counter();b=Boxes(n);L,U,_,_=witnesses(b,T)
    # For an arbitrary rational epsilon, round subtraction conservatively.
    eps_up=-(-eps.numerator*S//eps.denominator)
    floor=[np.zeros_like(L[0]) for _ in range(T+1)];arrays={f'L_{t}':z for t,z in enumerate(L)}
    arrays.update({f'U_{t}':z for t,z in enumerate(U)})
    for lam in PRICES:
        W=[None]*T+[mul(b.terminal_hi,lam,True)]
        for t in reversed(range(T)):
            W[t]=(mul(b.reward_hi,lam,True)-b.kl+b.continuation(W[t+1],True)).max(axis=0)
            floor[t]=np.maximum(floor[t],mul(L[t]-eps_up,lam,False)-W[t])
        arrays.update({f'W_{str(lam).replace("/","_")}_{t}':z for t,z in enumerate(W)})
    B=[None]*T+[np.zeros_like(L[0])]
    for t in reversed(range(T)):
        z=b.kl+b.continuation(B[t+1],False);gap=L[t][None]-eps_up-b.q(U[t+1],True)
        candidates=[floor[t]]
        for mu in MUS:
            val=z+mu*gap;assert np.max(np.abs(val))<2**62;candidates.append(val.min(axis=0))
        B[t]=np.maximum.reduce(candidates);assert B[t].min()>=0
    arrays.update({f'F_{t}':z for t,z in enumerate(floor)});arrays.update({f'B_{t}':z for t,z in enumerate(B)})
    filename=f'nonlinear/support_T{T}_N{n}_eps{str(eps).replace("/","_")}.npz'
    p=ROOT/'results'/filename;p.parent.mkdir(parents=True,exist_ok=True)
    if store:np.savez_compressed(p,**arrays)
    return {'T':T,'mesh':n,'epsilon':str(eps),'support_only_lower':str(integral(floor[0])),
       'restart_support_lower':str(integral(B[0])),'operating_witness_width':str(F(max(int((u-l).max()) for u,l in zip(U,L)),S)),
       'prices':list(map(str,PRICES)),'local_multipliers':list(MUS),'seconds':time.perf_counter()-tic,
       'array_payload_bytes':sum(z.nbytes for z in arrays.values()),'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
       'proof_file':filename if store else None,'proof_sha256':digest(p) if store else None,
       'policy_class':'randomized_Markov_and_restart_feasible_history_conditioned',
       'objective':'uniform_square_initial_discounted_revision_cost'}

def run():
    old=json.loads((OLD/'results/multistate.json').read_text());rows=[]
    for T in (4,8,16,32):
        for n in (16,32,64,128,256):
            d=compute(T,n)
            candidates=[z for z in old['outcomes'] if z['T']==T and z['mesh']==n and z['certified']]
            # Only already feasible, separately reevaluated policies enter the upper bound.
            if candidates:
                best=min(candidates,key=lambda z:F(z['revision_cost_upper']));upper=F(best['revision_cost_upper']);lower=F(d['restart_support_lower']);assert lower<=upper
                d.update(upper=str(upper),gap=str(upper-lower),relative_gap=str((upper-lower)/upper) if upper else '0',
                         upper_source=best['policy_file'],upper_method=best['method'],upper_source_revision='R38',
                         upper_regret_bound=best['all_restart_regret_bound'])
            else:d.update(upper=None,gap=None,relative_gap=None,upper_source=None)
            rows.append(d);save(ROOT/'results/nonlinear_support.json',{'outcomes':rows,'scale':S,'model':MODEL,
               'candidate_search':'No new upper-candidate search; lower-bound improvement paired with identical retained feasible upper policies.',
               'verification':'Independent implementation covers specifically reported representative objects; see verification report.'})
            print(T,n,float(F(d['support_only_lower'])),float(F(d['restart_support_lower'])),d['upper'] and float(F(d['upper'])),d['seconds'],flush=True)
    tight=[]
    for T,n in ((4,64),(8,128),(16,128),(32,256)):
        d=compute(T,n,F(1,20));d['upper']=None;d['status']='lower-bound-only; inherited epsilon=1/2 policies not relabeled feasible at epsilon=1/20'
        tight.append(d)
    save(ROOT/'results/nonlinear_tight_tolerance.json',{'outcomes':tight,'purpose':'Comparable operating tolerance diagnostic, not a solved stricter policy problem.'})
if __name__=='__main__':run()
