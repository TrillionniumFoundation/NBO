"""R7: regret-budgeted neural policies on the unchanged R6 finite economies.

An actor supplies a shortlist; an exhaustive OFFLINE guard repairs violations.
The guard cost is recorded. The online finite controller consists of stored
actor-generated indices plus an explicit correction map. No speed or continuous
model certificate is inferred from the finite result. Historical R6 is read-only.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, math, resource, sys, time
from pathlib import Path
import numpy as np
import torch
from torch import nn
ROOT = Path(__file__).resolve().parents[3]
R6 = ROOT / 'revisions/2026-09-29-r6'
sys.path.insert(0, str(R6 / 'code'))
from ndu_neural import NDU, model_spec
from dynamic_cournot import Game
from interval_certificate import I
OUT = Path(__file__).resolve().parents[1] / 'results'
torch.set_default_dtype(torch.float64)
torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

class Net(nn.Module):
    def __init__(self, out: int, width: int = 32):
        super().__init__()
        self.f = nn.Sequential(nn.Linear(2, width), nn.Tanh(), nn.Linear(width, width), nn.Tanh(), nn.Linear(width, out))
    def forward(self, x):
        return self.f(x)

def subset(x: I, rows, actions) -> I:
    return I(x.lo[rows, actions], x.hi[rows, actions])

def interval_q(m, v: I, player=None) -> I:
    """Exact-real interpretation of the stored R6 binary64 primitives."""
    shape = m.weights.shape[:2]
    continuation = I(np.zeros(shape))
    for j in range(m.weights.shape[2]):
        continuation = continuation + I(m.weights[:, :, j]) * I(v.lo[m.index[:, :, j]], v.hi[m.index[:, :, j]])
    reward = m.reward if player is None else m.reward[:, :, player]
    constant = m.constant if player is None else m.constant[:, :, player]
    return I(reward) + I(m.q) * (continuation + I(constant))

def finite_certificate(m, policies: np.ndarray, game=False):
    """Full dynamic policy and optimal/best-response envelopes, not samples."""
    start = time.perf_counter()
    if not np.issubdtype(policies.dtype, np.integer):
        raise ValueError('policy must contain integer action indices')
    expected = (m.steps, m.N, 2) if game else (m.steps, m.N)
    if policies.shape != expected or np.any(policies < 0) or np.any(policies >= m.A):
        raise ValueError('policy shape or index is invalid')
    players = 2 if game else 1
    all_lower, all_upper, all_bestlo, all_besthi, gaps = [], [], [], [], []
    rows = np.arange(m.N)
    for player in range(players):
        terminal = m.g[:, player] if game else m.g
        pv = I(terminal); best = I(terminal)
        lowers = [pv.lo.copy()]; uppers = [pv.hi.copy()]
        blo = [best.lo.copy()]; bhi = [best.hi.copy()]
        for t in range(m.steps - 1, -1, -1):
            qv = interval_q(m, pv, player if game else None)
            qb = interval_q(m, best, player if game else None)
            if game:
                i, j = policies[t].T
                pv = subset(qv, rows, i * m.A + j)
                lo = qb.lo.reshape(m.N, m.A, m.A); hi = qb.hi.reshape(m.N, m.A, m.A)
                candidates_lo = lo[rows, :, j] if player == 0 else lo[rows, i, :]
                candidates_hi = hi[rows, :, j] if player == 0 else hi[rows, i, :]
            else:
                pv = subset(qv, rows, policies[t])
                candidates_lo, candidates_hi = qb.lo, qb.hi
            best = I(candidates_lo.max(axis=1), candidates_hi.max(axis=1))
            lowers.append(pv.lo.copy()); uppers.append(pv.hi.copy())
            blo.append(best.lo.copy()); bhi.append(best.hi.copy())
        lo, hi, bl, bh = [np.array(x[::-1]) for x in [lowers, uppers, blo, bhi]]
        regret = I(bl, bh) - I(lo, hi)
        gaps.append(float(np.maximum(0, regret.hi).max()))
        all_lower.append(lo); all_upper.append(hi); all_bestlo.append(bl); all_besthi.append(bh)
    arrays = dict(policy_lower=np.stack(all_lower, axis=-1), policy_upper=np.stack(all_upper, axis=-1),
                  best_lower=np.stack(all_bestlo, axis=-1), best_upper=np.stack(all_besthi, axis=-1))
    return dict(full_domain=True, scope='every stored finite-model state and time, every feasible deviation',
                payoff_loss_upper=gaps, seconds=time.perf_counter()-start,
                arithmetic='outward binary64 elementary operations on stored primitives; not a formal proof',
                continuous_transfer=None), arrays

def fit_actor(net, x, q, labels, active, steps, counters):
    """Own-objective update; all continuation and rival channels detached."""
    qt = torch.as_tensor(q.copy())
    losses = (qt.max(dim=1, keepdim=True).values - qt).detach()
    scale = 1 + qt.max(dim=1, keepdim=True).values.abs()
    labels = torch.as_tensor(labels.copy())
    opt = torch.optim.Adam(net.parameters(), lr=.006)
    for _ in range(steps):
        opt.zero_grad(set_to_none=True)
        logits = net(x)[active]
        expected = (logits.softmax(dim=1) * (losses / scale)[active]).sum(dim=1)
        ce = nn.functional.cross_entropy(logits, labels[active], reduction='none')
        loss = expected.mean() + .04 * ce.mean() + expected.topk(max(1,len(expected)//10)).values.mean()
        if not torch.isfinite(loss):
            raise FloatingPointError('nonfinite actor loss')
        loss.backward(); opt.step(); counters['actor_gradients'] += 1

def fit_critic(net, x, terminal, lifting, target, adam_steps, polish, counters):
    g = torch.tensor(terminal[:, None]); lift = torch.tensor(lifting[:, None]); y = torch.tensor(target[:, None])
    def prediction(): return g + lift * net(x)
    def objective():
        e = ((prediction()-y)/10).square().ravel()
        return e.mean() + e.topk(max(1,len(e)//10)).values.mean()
    opt = torch.optim.Adam(net.parameters(), lr=.006)
    for _ in range(adam_steps):
        opt.zero_grad(set_to_none=True); loss=objective()
        if not torch.isfinite(loss): raise FloatingPointError('nonfinite critic loss')
        loss.backward(); opt.step(); counters['critic_gradients'] += 1
    saved=copy.deepcopy(net.state_dict()); initial=float(objective().detach())
    opt=torch.optim.LBFGS(net.parameters(), lr=.5, max_iter=polish, max_eval=polish*2,
        history_size=30, line_search_fn='strong_wolfe', tolerance_grad=1e-11, tolerance_change=1e-13)
    def closure():
        opt.zero_grad(set_to_none=True); loss=objective()
        if not torch.isfinite(loss): raise FloatingPointError('nonfinite critic polish')
        loss.backward(); counters['critic_closures'] += 1; return loss
    opt.step(closure)
    final=float(objective().detach())
    if not np.isfinite(final) or final>initial:
        net.load_state_dict(saved); counters['polish_rollbacks'] += 1
    return prediction().detach().numpy().ravel()

def put_weights(saved, net, prefix):
    for name, tensor in net.state_dict().items():
        saved[prefix+name]=tensor.detach().cpu().numpy().copy()

def persist(tag, report, arrays, history):
    OUT.mkdir(parents=True, exist_ok=True)
    path=OUT/f'{tag}.npz'; np.savez_compressed(path, **arrays)
    report['raw_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    report['raw_file']=path.name
    report['history']=history
    (OUT/f'{tag}.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='history'}, allow_nan=False), flush=True)
    return report

def ndu(seed=11, method='guarded_nbo', smoke=False):
    if method not in ['guarded_nbo','direct']: raise ValueError(method)
    torch.manual_seed(seed)
    m=NDU(9,13,5) if smoke else NDU()
    steps=30 if smoke else 160; polish=40 if smoke else 300
    x=torch.tensor(np.c_[(m.points[:,0]-2.1)/.9,2*(m.points[:,1]-m.ys[0])/(m.ys[-1]-m.ys[0])-1])
    lift=(m.points[:,1]-m.ys[0])*(m.ys[-1]-m.points[:,1])
    active=torch.tensor(~m.boundary); rows=np.arange(m.N)
    critic=Net(1); actor=Net(m.A)
    values=np.empty((m.steps+1,m.N));values[-1]=m.g
    policies=np.empty((m.steps,m.N),int); raw=np.empty_like(policies); short=np.empty_like(policies)
    saved={}; history=[]; counters=dict(actor_gradients=0,critic_gradients=0,critic_closures=0,polish_rollbacks=0,all_action_backups=0)
    start=time.perf_counter()
    for t in range(m.steps-1,-1,-1):
        q=m.Q(values[t+1]); counters['all_action_backups']+=1; best=q.argmax(axis=1)
        if method=='guarded_nbo':
            fit_actor(actor,x,q,best,active,steps,counters)
            logits=actor(x).detach().numpy(); raw[t]=logits.argmax(axis=1)
            candidates=np.argsort(logits,axis=1)[:,-4:]
            short[t]=candidates[rows,q[rows[:,None],candidates].argmax(axis=1)]
            loss=q.max(axis=1)-q[rows,short[t]]
            policies[t]=np.where(loss>.0025,best,short[t])
        else: raw[t]=short[t]=policies[t]=best
        target=q[rows,policies[t]]
        values[t]=fit_critic(critic,x,m.g,lift,target,(2 if method=='guarded_nbo' else 3)*steps,polish,counters)
        put_weights(saved,critic,f'critic_t{t}_')
        if method=='guarded_nbo': put_weights(saved,actor,f'actor_t{t}_')
        history.append(dict(time_index=t,seconds=time.perf_counter()-start,
            max_residual=float(abs(values[t]-target).max()),
            raw_gap=float((q.max(axis=1)-q[rows,raw[t]]).max()),
            shortlist_gap=float((q.max(axis=1)-q[rows,short[t]]).max()),
            final_gap=float((q.max(axis=1)-q[rows,policies[t]]).max()),**counters))
    training=time.perf_counter()-start
    ref, refpol, classical=m.reference()
    results={}; arr={}
    for label, pi in [('raw',raw),('shortlist',short),('final',policies)]:
        cert, env=finite_certificate(m,pi); results[label]=cert
        arr.update({label+'_'+k:v for k,v in env.items()})
    final_loss=results['final']['payoff_loss_upper'][0]
    value_error=float(np.max(abs(values-ref)))
    report=dict(study='ndu',seed=seed,method=method,model=model_spec(m),
        training_seconds=training,verification_seconds=sum(x['seconds'] for x in results.values()),
        classical_seconds=classical,counters=counters,
        raw_is_same_learner_ablation=True,certificates=results,
        shortlist_fraction_changed=float(np.mean(raw[:,~m.boundary]!=short[:,~m.boundary])),
        guard_fraction=float(np.mean(short[:,~m.boundary]!=policies[:,~m.boundary])),
        value_error_max=value_error,policy_target=.1,value_target=.2,
        target_pass=bool(final_loss<=.1 and value_error<=.2),
        process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        continuous_state_action_time_error=None)
    arr.update(values=values,policy=policies,raw_policy=raw,shortlist_policy=short,reference=ref,reference_policy=refpol,**saved)
    return persist(f'ndu_{method}_s{seed}'+('_smoke' if smoke else ''),report,arr,history)

def game(seed=11,market=1.,smoke=False):
    torch.manual_seed(seed)
    m=Game(n=9,steps=5,actions=7,market=market) if smoke else Game(market=market)
    steps=30 if smoke else 160;polish=40 if smoke else 300
    x=torch.tensor(2*(m.points-m.grid[0])/(m.grid[-1]-m.grid[0])-1)
    one=4*(m.points-m.grid[0])*(m.grid[-1]-m.points)/(m.grid[-1]-m.grid[0])**2
    lift=one.prod(axis=1);active=torch.tensor(~m.boundary);rows=np.arange(m.N)
    critics=[Net(1),Net(1)];actors=[Net(m.A),Net(m.A)]
    values=np.empty((m.steps+1,m.N,2));values[-1]=m.g
    policies=np.empty((m.steps,m.N,2),int); raw=np.empty_like(policies);short=np.empty_like(policies)
    history=[];saved={};missing=[];counters=dict(actor_gradients=0,critic_gradients=0,critic_closures=0,polish_rollbacks=0,all_action_backups=0)
    start=time.perf_counter()
    for t in range(m.steps-1,-1,-1):
        q=[m.Q(values[t+1,:,i],i) for i in range(2)];counters['all_action_backups']+=2
        gaps=[q[0].max(axis=1,keepdims=True)-q[0],q[1].max(axis=2,keepdims=True)-q[1]]
        joint=np.maximum(*gaps);pure=joint<=1e-11;exists=pure.any(axis=(1,2))
        index=np.where(exists,pure.reshape(m.N,-1).argmax(axis=1),joint.reshape(m.N,-1).argmin(axis=1))
        labels=np.c_[index//m.A,index%m.A];missing.append(int((~exists).sum()))
        logits=[]
        for player in range(2):
            own=q[player][rows,:,labels[:,1]] if player==0 else q[player][rows,labels[:,0],:]
            fit_actor(actors[player],x,own,labels[:,player],active,steps,counters)
            logits.append(actors[player](x).detach().numpy())
        raw[t]=np.c_[logits[0].argmax(axis=1),logits[1].argmax(axis=1)]
        candidates=[np.argsort(z,axis=1)[:,-3:] for z in logits]
        ia=np.repeat(candidates[0],3,axis=1);ja=np.tile(candidates[1],(1,3))
        scores=joint[rows[:,None],ia,ja];pick=scores.argmin(axis=1)
        short[t]=np.c_[ia[rows,pick],ja[rows,pick]]
        defect=joint[rows,short[t,:,0],short[t,:,1]]
        policies[t]=np.where((defect>.001)[:,None],labels,short[t])
        residuals=[]
        for player in range(2):
            target=q[player][rows,policies[t,:,0],policies[t,:,1]]
            values[t,:,player]=fit_critic(critics[player],x,m.g[:,player],lift,target,2*steps,polish,counters)
            residuals.append(float(abs(values[t,:,player]-target).max()))
            put_weights(saved,critics[player],f'critic{player}_t{t}_');put_weights(saved,actors[player],f'actor{player}_t{t}_')
        history.append(dict(time_index=t,seconds=time.perf_counter()-start,max_residual=residuals,
            raw_gap=float(joint[rows,raw[t,:,0],raw[t,:,1]].max()),
            final_gap=float(joint[rows,policies[t,:,0],policies[t,:,1]].max()),missing_pure=int((~exists).sum()),**counters))
    training=time.perf_counter()-start;results={};arr={}
    for label,pi in [('raw',raw),('shortlist',short),('final',policies)]:
        cert,env=finite_certificate(m,pi,game=True);results[label]=cert
        arr.update({label+'_'+k:v for k,v in env.items()})
    report=dict(study='game',seed=seed,market=market,grid=m.n,steps=m.steps,actions_per_player=m.A,
        training_seconds=training,verification_seconds=sum(z['seconds'] for z in results.values()),
        raw_is_same_learner_ablation=True,certificates=results,counters=counters,
        missing_pure_stages=sum(missing),
        guard_fraction=float(np.mean(np.any(short[:,~m.boundary]!=policies[:,~m.boundary],axis=2))),
        target=.1,target_pass=bool(max(results['final']['payoff_loss_upper'])<=.1),
        process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        neural_training=True,continuous_equilibrium_error=None)
    arr.update(values=values,policy=policies,raw_policy=raw,shortlist_policy=short,**saved)
    return persist(f'game_M{market:g}_s{seed}'+('_smoke' if smoke else ''),report,arr,history)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('study',choices=['ndu','game']);p.add_argument('--seed',type=int,default=11)
    p.add_argument('--method',default='guarded_nbo');p.add_argument('--market',type=float,default=1.)
    p.add_argument('--smoke',action='store_true');a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    if a.study=='ndu': ndu(a.seed,a.method,a.smoke)
    else: game(a.seed,a.market,a.smoke)
