"""Synchronous stopped-payoff certification with real optimizer rollback.
An intentionally aggressive block tests state restoration, not solver efficiency.
The separately timed shadow arm never changes the actual incumbent.
"""
from __future__ import annotations
import copy, hashlib, importlib.util, json, sys, time
from pathlib import Path
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r26'
spec=importlib.util.spec_from_file_location('r25_study',ROOT/'revisions/2026-09-23-r25/replication/study.py')
M=importlib.util.module_from_spec(spec);sys.modules[spec.name]=M;spec.loader.exec_module(M);S=M.S

def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(M.clean(x),indent=2,allow_nan=False)+'\n')

def run(seed:int,arm:str)->dict:
    path=REV/f'results/online/seed{seed}/{arm}'
    base=.08 if arm=='neural' else .32
    actor=S.network(seed);moving=M.Moving(actor) if arm=='moving' else None
    net=moving.net if moving else (copy.deepcopy(actor) if arm=='neural' else S.Coordinates(actor(S.NODES),S.CHART))
    opt=None if moving else torch.optim.Adam(S.parameters(net),lr=base)
    def state():
        return copy.deepcopy(moving.state() if moving else {'parameters':S.vector(net),'optimizer':opt.state_dict()})
    def restore(st):
        if moving:moving.restore(st)
        else:S.assign(net,st['parameters']);opt.load_state_dict(copy.deepcopy(st['optimizer']))
    def block(calls:int,lr:float):
        obj=S.setup();actual=0;failure=None;t0=time.perf_counter()
        try:
            if opt:
                for group in opt.param_groups:group['lr']=lr
            for _ in range(calls):
                if moving:moving.step(obj,lr)
                else:
                    opt.zero_grad(set_to_none=True);loss=-obj(net)
                    if not torch.isfinite(loss):raise FloatingPointError('nonfinite objective')
                    loss.backward()
                    if not all(torch.isfinite(p.grad).all() for p in S.parameters(net)):raise FloatingPointError('nonfinite gradient')
                    opt.step()
                    if not np.isfinite(S.vector(net)).all():raise FloatingPointError('nonfinite parameter')
                actual+=1
            candidate=obj(net,True)
        except (ArithmeticError,ValueError,RuntimeError) as exc:
            failure=type(exc).__name__+': '+str(exc);candidate=None
        generation=time.perf_counter()-t0
        cert,check=S.cert(candidate) if candidate is not None else ({'status':'REJECTED_CHECK','error':failure},0.)
        return {'calls':actual,'requested_calls':calls,'rate':lr,'actor':candidate,'certificate':cert,
                'failure':failure,'generation_seconds':generation,'checker_seconds':check}
    t0=time.perf_counter();incactor=S.setup()(net,True);incert,initialcheck=S.cert(incactor)
    if incert['status']!='CERTIFIED':raise RuntimeError(('invalid initial policy',seed,arm,incert))
    incumbent=state();initial=incert;rows=[];shadow_candidate=None;stress_accepted=False;production_shadow_pause=0.
    for j,calls in enumerate((200,50,100)):
        rate=base if j==0 else 20.48 if j==1 else base if stress_accepted else base/2
        saved=copy.deepcopy(incumbent);old=incert;start_hash=M.sha(saved)
        proposal=block(calls,rate);candidate_state=state();c=proposal['certificate']
        accepted=c['status']=='CERTIFIED' and c['value_interval'][0]>incert['value_interval'][1]
        if accepted:incert=c;incactor=proposal['actor'];incumbent=state()
        else:restore(saved)
        restored=state();after_hash=M.sha(restored)
        if not accepted:assert after_hash==start_hash,'optimizer state rollback is incomplete'
        if j==1:
            stress_accepted=accepted
            if not accepted and proposal['actor'] is not None:shadow_candidate=copy.deepcopy(candidate_state)
        row={'block':j+1,**proposal,'accepted':accepted,'old_certificate':old,'deployed_certificate':incert,
             'state_before_sha256':start_hash,'candidate_state_sha256':M.sha(candidate_state),'state_after_sha256':after_hash,
             'rollback_verified':not accepted and after_hash==start_hash,'elapsed_after_decision':time.perf_counter()-t0}
        rows.append(row)
        write(path/f'block{j+1}.json',row);write(path/f'block{j+1}_before_state.json',saved)
        write(path/f'block{j+1}_candidate_state.json',candidate_state);write(path/f'block{j+1}_after_state.json',restored)
        print('ONLINE',seed,arm,j+1,accepted,c.get('regret_upper'),flush=True)
    elapsed=time.perf_counter()-t0;final=state();shadow=None
    if shadow_candidate is not None:
        restore(shadow_candidate);shadow=block(100,base/2);shadow_state=state()
        shadow['state_sha256']=M.sha(shadow_state);shadow['coupled_final_sha256']=M.sha(final)
        shadow['trajectory_differs']=M.sha(shadow_state)!=M.sha(final)
        write(path/'shadow_final_state.json',shadow_state);write(path/'shadow.json',shadow)
        restore(final)
    out={'seed':seed,'arm':arm,'purpose':'declared aggressive-block rollback stress test, not heldout ranking',
         'original_economy':True,'current_state_only':False,'initial_certificate':initial,'initial_checker_seconds':initialcheck,
         'blocks':rows,'shadow':shadow,'final_deployed_certificate':incert,
         'actual_coupled_seconds':elapsed,'generation_seconds':sum(r['generation_seconds'] for r in rows),
         'checkpoint_check_seconds':sum(r['checker_seconds'] for r in rows),'gradient_calls':sum(r['calls'] for r in rows),
         'shadow_seconds_excluded':0. if shadow is None else shadow['generation_seconds']+shadow['checker_seconds'],
         'accepted_count':sum(r['accepted'] for r in rows),'rejected_count':sum(not r['accepted'] for r in rows)}
    write(path/'record.json',out);return out

def main():
    rows=[run(seed,arm) for seed in (26101,26102) for arm in ('neural','direct','moving')]
    write(REV/'results/online_summary.json',rows)
if __name__=='__main__':main()
