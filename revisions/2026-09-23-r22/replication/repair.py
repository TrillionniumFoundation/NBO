"""Post-observation root-safety and supervisory rollback recovery tests.

Primary prospective results remain unchanged. REPAIR_PROTOCOL identifies the
single selected diagnostic block and the prior observations motivating it.
"""
from pathlib import Path
import copy,json,random,time
import numpy as np
import torch
from crossed import Actor,Slab,NODES,CORNERS,REV,write,canon,sha,optimize,check,snapshot,restore
from proposal_safe import setup

def load_actor(p):
    data=json.loads(p.read_text());net=Actor()
    net.load_state_dict({k:torch.tensor(v['tensor']) for k,v in data.items()});return net

def root_repair():
    out=REV/'results/root_repair';old=REV/'results/crossed/seed22000/vertex1'
    obj=setup(*CORNERS[1]);bad=load_actor(REV/'fixtures/budget_failure_parameters.json')
    fixed=obj(bad,details=True);cert,seconds=check(fixed)
    write(out/'failed_parameters_rebudgeted_actor.json',fixed);write(out/'failed_parameters_rebudgeted_certificate.json',cert)
    torch.manual_seed(22001);initial=Actor();direct=Slab(initial(NODES));a0=obj(initial,details=True);d0=obj(direct,details=True)
    assert all(a0[k]==d0[k] for k in ('b','s','theta','approx_value','approx_budget'))
    shifted=copy.deepcopy(initial)
    with torch.no_grad():shifted.net[-1].bias[0]+=1000/0.3
    shifted_policy=obj(shifted,details=True)
    delta=max(abs(x-y) for x,y in zip(a0['b'],shifted_policy['b']))
    assert delta<1e-10
    ci,tci=check(a0);assert ci['status']=='CERTIFIED'
    write(out/'initial_certificate.json',ci);write(out/'initial_actor.json',a0)
    rows=[]
    for rep,net0 in [('neural',initial),('direct',direct)]:
        for optimizer in ('adam','lbfgsb'):
            net=copy.deepcopy(net0);stats=optimize(net,obj,optimizer)
            d=obj(net,details=True);c,sec=check(d)
            accepted=c['status']=='CERTIFIED' and c['value_interval'][0]>ci['value_interval'][1]
            record={'representation':rep,'optimizer':optimizer,'accepted':accepted,'certificate':c,
                    'checker_seconds':sec,'initial_checker_seconds':tci,**stats}
            rows.append(record);write(out/f'{rep}_{optimizer}_actor.json',d);write(out/f'{rep}_{optimizer}_parameters.json',canon(net.state_dict()))
            print('root-repair',rep,optimizer,accepted,c.get('regret_upper'),flush=True)
    write(out/'summary.json',{'protocol_commit':'98df6e83a2d0ccfae0aab65d5750344e8b629414',
          'post_observation_diagnostic':True,'selected_block':'base22000,vertex1',
          'common_intercept_shift':1000,'max_delivered_intercept_difference':delta,
          'raw_failed_parameter_rebudgeting_certificate':cert,'rows':rows})

def rejection_recovery():
    out=REV/'results/rejection_recovery';torch.manual_seed(22300);np.random.seed(22300);random.seed(22300)
    obj=setup(*CORNERS[0]);net=Actor();opt=torch.optim.Adam(net.parameters(),lr=.5)
    d=obj(net,details=True);inc,t0=check(d);assert inc['status']=='CERTIFIED'
    write(out/'initial_actor.json',d);write(out/'initial_certificate.json',inc);rows=[]
    for j in range(8):
        saved=snapshot(net,opt);before=sha(saved);lr=opt.param_groups[0]['lr'];start=time.perf_counter()
        for _ in range(25):
            opt.zero_grad(set_to_none=True);loss=-obj(net);loss.backward();opt.step()
        generation=time.perf_counter()-start
        d=obj(net,details=True);cert,seconds=check(d)
        accept=cert['status']=='CERTIFIED' and cert['value_interval'][0]>inc['value_interval'][1]
        old=inc['value_interval'][:]
        if accept:inc=cert;restored=False
        else:
            restore(net,opt,saved);assert sha(snapshot(net,opt))==before;restored=True
            # Supervisor changes only AFTER exact restoration has been checked.
            for group in opt.param_groups:group['lr']=lr/2
        row={'block':j+1,'learning_rate_before':lr,'learning_rate_after':opt.param_groups[0]['lr'],
             'accepted':accept,'restored_exactly_before_supervisor':restored,'candidate_certificate':cert,
             'incumbent_before':old,'incumbent_after':inc['value_interval'],'gradient_calls':25,
             'generation_seconds':generation,'checker_seconds':seconds,'restoration_hash':before if restored else None}
        rows.append(row);write(out/f'candidate_{j+1:02d}.json',d);write(out/'records.json',rows)
        print('recovery',j+1,accept,lr,opt.param_groups[0]['lr'],flush=True)
    rejected=[i for i,r in enumerate(rows) if not r['accepted']]
    recovered=bool(rejected and any(r['accepted'] for r in rows[rejected[0]+1:]))
    write(out/'summary.json',{'post_observation_diagnostic':True,'accepted':sum(r['accepted'] for r in rows),
         'rejected':len(rejected),'accepted_after_first_rejection':recovered,'final_value_interval':inc['value_interval'],
         'total_checker_seconds':t0+sum(r['checker_seconds'] for r in rows),
         'total_generation_seconds':sum(r['generation_seconds'] for r in rows),'supervisor_is_not_rolled_back':True})
if __name__=='__main__':root_repair();rejection_recovery()
