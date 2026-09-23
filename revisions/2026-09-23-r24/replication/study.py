"""R24 prospectively specified study. Proposal diagnostics are NOT certificates.

Run from a complete NBO checkout. All source/data dependencies and failed trials
are retained. The checker is imported, never modified. Single-thread generation
and serial certification make the new timing comparisons internally interpretable.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, math, os, platform, sys, time
from pathlib import Path
from dataclasses import asdict
import numpy as np
import scipy
from scipy.optimize import minimize
import torch
from torch.func import functional_call, jacrev
from numpy.polynomial.legendre import leggauss
from numpy.polynomial.hermite import hermgauss
ROOT=Path(__file__).resolve().parents[3]
REV=ROOT/'revisions/2026-09-23-r24'
sys.path[:0]=[str(ROOT/'revisions/2026-09-23-r23/replication'),str(ROOT/'revisions/2026-09-23-r22/replication')]
from budget_coordinates import implicit_offset,RootAccounting
from crossed import Actor,Slab,check,canon
from certify_stochastic import A,I,Q,log,sqrt
PROTOCOL_COMMIT='b54afa8c9107d70094a1d84be4a3c0279916530c'
METHODS=('neural','direct','diagonal','tangent','white')
CHECKPOINTS=(25,50,100,200,400)
NODES=(2*(torch.arange(16,dtype=torch.float64)+.5)/16-1).reshape(16,1)
torch.set_default_dtype(torch.float64);torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)


def write(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    s=json.dumps(obj,indent=2,allow_nan=False)+'\n'
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(s);tmp.replace(path)


def digest(x):
    return hashlib.sha256(json.dumps(canon(x),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def chart():
    q=np.zeros((48,47))
    for k in range(15):
        q[3*np.arange(k+1),k]=1/math.sqrt((k+1)*(k+2))
        q[3*(k+1),k]=-(k+1)/math.sqrt((k+1)*(k+2))
    for k in range(16):q[3*k+1,15+k]=1;q[3*k+2,31+k]=1
    assert np.max(np.abs(q.T@q-np.eye(47)))<2e-14
    return torch.from_numpy(q)
CHART=chart()


def setup(u0=2.,x0=1.25,orders=(8,16),reference=False):
    nt,nz=orders;tg,tw=leggauss(nt);zg,zw=hermgauss(nz)
    z=torch.tensor(zg*np.sqrt(2));zw=torch.tensor(zw/np.sqrt(np.pi))
    t=torch.tensor((np.arange(16)[:,None]+(tg+1)/2)/16);w=torch.tensor(tw/32)
    tt=t[:,:,None];v=torch.sqrt(tt);lp=-.025*tt+.3*v*z;lq=.065*tt+.3*v*z
    weights=(torch.exp(-.02*t)*w)[:,:,None]*zw
    budget=x0-.50001*np.exp(-.02);mass=float(weights.sum());target=(budget-.5*mass)/.3
    account=RootAccounting()
    def objective(net,details=False):
        h=net(NODES)
        if reference:
            c=.05+.70*torch.sigmoid(h[:,0]);reserve=1.25-c.mean()
            payoff=-(1/c).mean()+torch.log(reserve)
            if details:return {'c':c.detach().tolist(),'reserve':float(reserve.detach()),'approx_value':float(payoff.detach()),'reference':True}
            return payoff
        b=.3*h[:,0,None,None];b=b-b.mean()
        s=(.1+6.4*torch.sigmoid(h[:,1]))[:,None,None];theta=.2*torch.sigmoid(h[:,2])
        offset=implicit_offset(b-s*lq,weights,target,account)
        cq=.5+.3*torch.sigmoid(b-s*lq+offset)
        c=.5+.3*torch.sigmoid(b-s*lp+offset)
        mean=u0+(torch.cumsum(theta,0)-theta)[:,None]/16+theta[:,None]*(t-torch.arange(16)[:,None]/16)
        U=mean[:,:,None,None]+.05*torch.sqrt(t)[:,:,None,None]*(.25*z[None,None,:,None]+np.sqrt(.9375)*z[None,None,None,:])
        # This defines an integrable extension. It does not change the stopped
        # economy or justify a stopped-objective gradient approximation.
        clipped=torch.clamp(U,1.2,2.8)
        flow=(-torch.exp(-(clipped-1)*torch.log(c[:,:,:,None]))/(clipped-1)*zw[None,None,:,None]*zw[None,None,None,:]).sum((-1,-2))-theta[:,None]**2
        payoff=(torch.exp(-.04*t)*flow*w).sum()+np.exp(-.04)*(-.02*((u0-2+theta.mean())**2+.0025)+.1*np.log(.50001))
        if not torch.isfinite(payoff):raise FloatingPointError('nonfinite proposal payoff')
        if details:
            return {'b':(b[:,0,0]+offset).detach().tolist(),'s':s[:,0,0].detach().tolist(),'theta':theta.detach().tolist(),'u0':u0,'x0':x0,'n':16,'reserve':.50001,'approx_value':float(payoff.detach()),'approx_budget':float((cq*weights).sum().detach()),'proposal_orders':list(orders),'proposal_offset':float(offset.detach()),'clipped_nodes':int((U!=clipped).sum())}
        return payoff
    objective.accounting=account
    return objective


class Coordinates(torch.nn.Module):
    def __init__(self,raw,matrix):
        super().__init__();self.register_buffer('base',raw.detach().flatten().clone());self.register_buffer('matrix',matrix.clone());self.z=torch.nn.Parameter(torch.zeros(matrix.shape[1]))
    def forward(self,_):return (self.base+self.matrix@self.z).reshape(16,3)


class ScaledActor(torch.nn.Module):
    """Equivalent parameter chart theta=S phi; not rescaling tanh arguments."""
    def __init__(self,actor):
        super().__init__();self.template=copy.deepcopy(actor)
        for p in self.template.parameters():p.requires_grad_(False)
        self.names=[];self.scales={};self.phi=torch.nn.ParameterList()
        for name,p in actor.named_parameters():
            s=.25 if name.startswith('net.0') else (4. if name.startswith('net.4') else 1.)
            self.names.append(name);self.scales[name]=s;self.phi.append(torch.nn.Parameter(p.detach().clone()/s))
    def forward(self,t):return functional_call(self.template,{name:p*self.scales[name] for name,p in zip(self.names,self.phi)},(t,))


def flat_jacobian(net):
    named={n:p for n,p in net.named_parameters() if p.requires_grad}
    frozen={n:p for n,p in net.named_parameters() if not p.requires_grad}
    blocks=jacrev(lambda d:functional_call(net,{**frozen,**d},(NODES,)).flatten())(named)
    return torch.cat([blocks[n].reshape(48,-1) for n in named],dim=1).detach()


def geometries(actor,reference=False):
    start=time.perf_counter();j=flat_jacobian(actor);q=torch.eye(48) if reference else CHART;dim=q.shape[1];g=q.T@j@j.T@q
    ev,U=torch.linalg.eigh((g+g.T)/2);floor=max(float(ev[-1])*1e-5,1e-12)
    reg=ev.clamp_min(floor)
    mats={'direct':q,'diagonal':q@torch.diag(torch.diag(g).clamp_min(floor).sqrt()),'tangent':q@(U@torch.diag(reg.sqrt())@U.T),'white':q@(U@torch.diag(reg.rsqrt())@U.T)}
    mats={k:v*math.sqrt(dim/float((v*v).sum())) for k,v in mats.items()}
    return mats,{'seconds':time.perf_counter()-start,'raw_jacobian_singular_values':torch.linalg.svdvals(j).tolist(),'quotient_metric_eigenvalues':ev.tolist(),'regularization_floor':floor,'effective_rank_relative_1e_10':int((torch.linalg.svdvals(j)>torch.linalg.svdvals(j)[0]*1e-10).sum())}


def parameters(net):return [p for p in net.parameters() if p.requires_grad]
def vector(net):return np.concatenate([p.detach().numpy().ravel() for p in parameters(net)]).copy()
def assign(net,x):
    pos=0
    with torch.no_grad():
        for p in parameters(net):
            n=p.numel();p.copy_(torch.tensor(x[pos:pos+n]).reshape(p.shape));pos+=n


class CallLimit(Exception):pass


def optimize(net,obj,optimizer,lr,cap=400,checkpoints=CHECKPOINTS,diagnostics=False,gtol=1e-8):
    params=parameters(net);start=time.perf_counter();history=[];accepted=[];snaps={};count=0
    accepted.append((0,vector(net),0.))
    metric_seconds=0.;transport=[]
    try:
        if optimizer=='adam':
            opt=torch.optim.Adam(params,lr=lr)
            for count in range(1,cap+1):
                opt.zero_grad(set_to_none=True);loss=-obj(net);loss.backward()
                grad=np.concatenate([p.grad.detach().numpy().ravel() for p in params])
                if not np.isfinite(grad).all():raise FloatingPointError('nonfinite gradient')
                diagnostic=diagnostics and count in checkpoints
                if diagnostic:
                    ms=time.perf_counter();j=flat_jacobian(net);old=vector(net);oldh=net(NODES).detach().flatten();metric_seconds+=time.perf_counter()-ms
                opt.step()
                if not np.isfinite(vector(net)).all():raise FloatingPointError('nonfinite iterate')
                elapsed=time.perf_counter()-start-metric_seconds
                history.append({'call':count,'loss':float(loss.detach()),'gradient_norm':float(np.linalg.norm(grad)),'generation_seconds':elapsed})
                if count in checkpoints:
                    snaps[count]={'parameters':vector(net),'actual_calls':count,'generation_seconds':elapsed,'raw':net(NODES).detach().numpy().copy()}
                if diagnostic:
                    ms=time.perf_counter();delta=torch.tensor(vector(net)-old);actual=net(NODES).detach().flatten()-oldh;pred=j@delta
                    den=torch.cat([(opt.state[p]['exp_avg_sq']/(1-.999**count)).sqrt().flatten()+1e-8 for p in params])
                    metric=(j/den[None,:])@j.T;ev=torch.linalg.eigvalsh((metric+metric.T)/2)
                    transport.append({'call':count,'jacobian_singular_values':torch.linalg.svdvals(j).tolist(),'adam_metric_eigenvalues':ev.tolist(),'parameter_step_norm':float(torch.linalg.norm(delta)),'raw_output_step_norm':float(torch.linalg.norm(actual)),'linearization_remainder_norm':float(torch.linalg.norm(actual-pred)),'linearized_step_norm':float(torch.linalg.norm(pred)),'momentum_included_in_actual_parameter_step':True})
                    metric_seconds+=time.perf_counter()-ms
            status='call_cap'
        else:
            def fun(x):
                nonlocal count
                if count>=cap:raise CallLimit()
                assign(net,x);net.zero_grad(set_to_none=True);loss=-obj(net);loss.backward();count+=1
                g=np.concatenate([p.grad.detach().numpy().ravel() for p in params]).copy()
                if not np.isfinite(g).all():raise FloatingPointError('nonfinite gradient')
                history.append({'call':count,'loss':float(loss.detach()),'gradient_norm':float(np.linalg.norm(g)),'generation_seconds':time.perf_counter()-start})
                return float(loss.detach()),g
            def cb(x):accepted.append((count,x.copy(),time.perf_counter()-start))
            result=minimize(fun,vector(net),method='L-BFGS-B',jac=True,callback=cb,options={'maxiter':cap,'maxfun':cap,'maxls':40,'ftol':1e-13,'gtol':gtol})
            assign(net,result.x);accepted.append((count,result.x.copy(),time.perf_counter()-start));status=str(result.message)
    except CallLimit:
        assign(net,accepted[-1][1]);status='call_cap_last_accepted_iterate'
    except (FloatingPointError,ArithmeticError,ValueError) as exc:
        status=type(exc).__name__+': '+str(exc)
        if optimizer=='lbfgsb':assign(net,accepted[-1][1])
        elif snaps:assign(net,snaps[max(snaps)]['parameters'])
        else:assign(net,accepted[0][1])
    generation_seconds=time.perf_counter()-start-metric_seconds
    final=vector(net)
    if optimizer=='lbfgsb':
        for c in checkpoints:
            eligible=[a for a in accepted if a[0]<=c];a=eligible[-1]
            assign(net,a[1]);snaps[c]={'parameters':a[1],'actual_calls':min(c,count),'accepted_iterate_call':a[0],'generation_seconds':next((h['generation_seconds'] for h in reversed(history) if h['call']<=c),0.),'raw':net(NODES).detach().numpy().copy(),'carried_forward_after_termination':count<c}
    else:
        for c in checkpoints:
            if c not in snaps:
                prev=snaps[max(snaps)] if snaps else {'parameters':final,'actual_calls':count,'generation_seconds':generation_seconds,'raw':net(NODES).detach().numpy().copy()}
                snaps[c]=copy.deepcopy(prev);snaps[c]['carried_forward_after_termination']=True
    assign(net,final)
    return {'termination':status,'function_calls':count,'gradient_calls':count,'generation_seconds':generation_seconds,'diagnostic_seconds':metric_seconds,'history':history,'transport':transport,'snapshots':snaps,'final_parameters':final,'parameter_dimension':sum(p.numel() for p in params),'root_accounting':{k:(v if not isinstance(v,float) or math.isfinite(v) else None) for k,v in asdict(obj.accounting).items()}}


def reference_check(actor):
    start=time.perf_counter();c=I(actor['c']);reserve=Q('1.25')-A.add_reduce(c)/16
    if reserve.lo<=.5:return {'status':'REJECTED_CHECK','error':'reference reserve <= .5'},time.perf_counter()-start
    payoff=-A.add_reduce(1/c)/16+log(reserve)
    star=(sqrt(Q(6))-1)/2;optimal=-1/star+2*log(star)
    gap=optimal-payoff
    return {'status':'CERTIFIED','value_interval':payoff.pair(),'optimal_value_interval':optimal.pair(),'optimal_value_upper':float(optimal.hi),'regret_upper':float(gap.hi),'solver_error_interval':gap.pair(),'policy_lower_width':float((I(payoff.hi)-I(payoff.lo)).hi),'policy_class_approximation_error':0,'temporal_quadrature_error':0,'reserve_interval':reserve.pair(),'reference_consumption_interval':star.pair(),'reference_economy_not_original':True},time.perf_counter()-start


def cert(actor,reference=False):
    started=time.perf_counter()
    try:return reference_check(actor) if reference else check(actor)
    except Exception as exc:return {'status':'REJECTED_CHECK','error':type(exc).__name__+': '+str(exc)},time.perf_counter()-started


def gradient_refinement(raw,u,x):
    vals=[]
    for orders in ((8,16),(12,24)):
        net=Slab(torch.tensor(raw));obj=setup(u,x,orders);loss=-obj(net);loss.backward();d=obj(net,True)
        vals.append({'orders':list(orders),'loss':float(loss.detach()),'gradient':net.coefficients.grad.detach().flatten().tolist(),'offset':d['proposal_offset'],'discrete_min_price_derivative':obj.accounting.minimum_discrete_price_derivative})
    g0=np.array(vals[0]['gradient']);g1=np.array(vals[1]['gradient'])
    return {'rules':vals,'raw_gradient_difference_l2':float(np.linalg.norm(g0-g1)),'relative_gradient_difference_l2':float(np.linalg.norm(g0-g1)/max(np.linalg.norm(g1),1e-14)),'offset_difference':abs(vals[0]['offset']-vals[1]['offset']),'status':'ordinary floating-point diagnostic; not a bound on the stopped-objective gradient'}


def network(seed):torch.manual_seed(seed);return Actor()


def run_one(path,template,obj,optimizer,lr,initial_cert,initial_actor,cap=400,checkpoints=CHECKPOINTS,diagnostics=False,u=2.,x=1.25,reference=False,meta=None,gtol=1e-8):
    path=Path(path)
    if (path/'record.json').exists():return json.loads((path/'record.json').read_text())
    net=copy.deepcopy(template);r=optimize(net,obj,optimizer,lr,cap,checkpoints,diagnostics,gtol)
    record={k:v for k,v in r.items() if k not in ('snapshots','history','transport','final_parameters')};record.update(meta or {})
    rows=[];inc=initial_cert;inc_actor=initial_actor;cumcheck=0.
    for c,snap in sorted(r['snapshots'].items()):
        assign(net,snap['parameters']);actor=obj(net,True);certificate,secs=cert(actor,reference);cumcheck+=secs
        accepted=certificate['status']=='CERTIFIED' and (inc.get('status')!='CERTIFIED' or certificate['value_interval'][0]>inc['value_interval'][1])
        if accepted:inc=certificate;inc_actor=actor
        row={k:v for k,v in snap.items() if k not in ('parameters','raw')}
        row.update({'raw_outputs':snap['raw'].tolist(),'checkpoint':c,'candidate_actor':actor,'certificate':certificate,'accepted_for_deployment':accepted,'deployed_certificate':inc,'deployed_actor':inc_actor,'checker_seconds':secs,'cumulative_checker_seconds':cumcheck})
        if diagnostics and not reference:
            dt=time.perf_counter();jj=flat_jacobian(net);sv=torch.linalg.svdvals(jj);row['actual_output_jacobian_singular_values']=sv.tolist();row['actual_output_jacobian_rank_relative_1e_10']=int((sv>sv[0]*1e-10).sum());row['quadrature_gradient_diagnostic']=gradient_refinement(snap['raw'],u,x);row['gradient_diagnostic_seconds']=time.perf_counter()-dt;row['diagnostic_objective_gradient_calls']=2;row['diagnostic_reporting_forward_calls']=2
        write(path/f'checkpoint_{c:03d}.json',row);rows.append(row)
    assign(net,r['final_parameters']);final_actor=obj(net,True)
    record.update({'optimizer':optimizer,'learning_rate':lr,'initial_certificate':initial_cert,'initial_actor':initial_actor,'checkpoints':[{k:v for k,v in a.items() if k not in ('candidate_actor','deployed_actor','quadrature_gradient_diagnostic')} for a in rows],'final_actor':final_actor,'final_candidate_certificate':rows[-1]['certificate'],'final_deployed_certificate':rows[-1]['deployed_certificate'],'checker_seconds':cumcheck,'deployed_actor_sha256':digest(rows[-1]['deployed_actor']),'candidate_actor_sha256':digest(final_actor),'execution_did_not_rollback_proposal_optimizer':True,'extra_reporting_forward_calls':len(rows)+1,'extra_gradient_diagnostic_calls':sum(a.get('diagnostic_objective_gradient_calls',0) for a in rows),'gradient_diagnostic_seconds':sum(a.get('gradient_diagnostic_seconds',0.) for a in rows)})
    write(path/'history.json',r['history']);write(path/'geometry.json',r['transport']);write(path/'final_parameters.json',canon(net.state_dict()));write(path/'record.json',record)
    print(str(path.relative_to(REV)),record['gradient_calls'],record['final_candidate_certificate'].get('regret_upper'),record['termination'],flush=True)
    return record


def prepared(seed,reference=False):
    actor=network(seed);mats,geo=geometries(actor,reference);raw=actor(NODES).detach()
    templates={'neural':actor,**{k:Coordinates(raw,v) for k,v in mats.items()}}
    return templates,geo


def run_tuning():
    allrows=[]
    for seed in (24001,24002):
        ts,geo=prepared(seed);obj=setup();initial=obj(ts['neural'],True);ci,cs=cert(initial)
        write(REV/f'results/tuning/seed{seed}/initial.json',{'actor':initial,'certificate':ci,'checker_seconds':cs,'geometry':geo})
        for m in METHODS:
            for lr in (.005,.02,.08):
                r=run_one(REV/f'results/tuning/seed{seed}/{m}_{lr:g}',ts[m],setup(),'adam',lr,ci,initial,200,(200,),meta={'method':m,'seed':seed,'preprocessing_seconds':geo['seconds'] if m not in ('neural','direct') else 0.})
                allrows.append(r)
    selected={};scores={}
    for m in METHODS:
        candidates=[]
        for lr in (.005,.02,.08):
            rs=[r for r in allrows if r['method']==m and r['learning_rate']==lr]
            feasible=all(r['final_candidate_certificate']['status']=='CERTIFIED' for r in rs)
            score=float(np.mean([r['final_candidate_certificate']['value_interval'][0] for r in rs])) if feasible else None
            candidates.append({'lr':lr,'score':score,'feasible':feasible})
        valid=[r for r in candidates if r['feasible']]
        if not valid:raise RuntimeError('No feasible tuning configuration: '+m)
        best=max(r['score'] for r in valid);selected[m]=min(r['lr'] for r in valid if r['score']>=best-1e-10);scores[m]=candidates
    result={'selected':selected,'scores':scores,'trials':len(allrows),'total_gradient_calls':sum(r['gradient_calls'] for r in allrows),'generation_seconds':sum(r['generation_seconds'] for r in allrows),'checking_seconds':sum(r['checker_seconds'] for r in allrows),'selection_uses_only_tuning_seeds':True}
    write(REV/'results/tuning_selection.json',result);return selected


def heldout(selected):
    for seed in (24101,24102):
        ts,geo=prepared(seed)
        for orders in ((8,16),(12,24)):
            name=f'q{orders[0]}_{orders[1]}';obj=setup(orders=orders);initial=obj(ts['neural'],True);ci,cs=cert(initial)
            write(REV/f'results/heldout/seed{seed}/{name}/initial.json',{'actor':initial,'certificate':ci,'checker_seconds':cs,'geometry':geo})
            for m,opt in [(m,'adam') for m in METHODS]+[('neural','lbfgsb'),('direct','lbfgsb')]:
                run_one(REV/f'results/heldout/seed{seed}/{name}/{m}_{opt}',ts[m],setup(orders=orders),opt,selected.get(m,.005),ci,initial,diagnostics=True,meta={'method':m,'seed':seed,'orders':list(orders),'preprocessing_seconds':geo['seconds'] if m not in ('neural','direct') else 0.})


def multicell(selected):
    points=[(u,x) for u in (1.98,2.,2.02) for x in (1.24,1.255,1.27)]
    for idx,(u,x) in enumerate(points):
        seed=24300+idx;ts,geo=prepared(seed);obj=setup(u,x);initial=obj(ts['neural'],True);ci,cs=cert(initial)
        write(REV/f'results/multicell/vertex{idx}/initial.json',{'actor':initial,'certificate':ci,'checker_seconds':cs,'geometry':geo})
        for m,opt in (('neural','adam'),('direct','adam'),('tangent','adam'),('direct','lbfgsb')):
            run_one(REV/f'results/multicell/vertex{idx}/{m}_{opt}',ts[m],setup(u,x),opt,selected.get(m,.005),ci,initial,checkpoints=(400,),u=u,x=x,meta={'method':m,'vertex':idx,'seed':seed,'u0':u,'x0':x,'preprocessing_seconds':geo['seconds'] if m=='tangent' else 0.})
    rows=[];pexit=2*A.exp(-Q('.58')**2/(2*Q('.0025')))
    for m,opt in (('neural','adam'),('direct','adam'),('tangent','adam'),('direct','lbfgsb')):
        records=[json.loads((REV/f'results/multicell/vertex{i}/{m}_{opt}/record.json').read_text()) for i in range(9)]
        cells=[]
        for iu in range(2):
            for ix in range(2):
                ids=[3*iu+ix,3*iu+ix+1,3*(iu+1)+ix,3*(iu+1)+ix+1]
                cs=[records[i]['final_deployed_certificate'] for i in ids]
                ok=all(c['status']=='CERTIFIED' for c in cs)
                bound=float((I(max(c['regret_upper'] for c in cs))+16*pexit).hi) if ok else None
                cells.append({'vertices':ids,'certified':ok,'regret_upper':bound})
        rows.append({'method':m+'_'+opt,'cells':cells,'region_regret_upper':max(c['regret_upper'] for c in cells) if all(c['certified'] for c in cells) else None,'generation_seconds':sum(r['generation_seconds'] for r in records),'checker_seconds':sum(r['checker_seconds'] for r in records),'gradient_calls':sum(r['gradient_calls'] for r in records)})
    write(REV/'results/multicell_summary.json',{'points':points,'cells':4,'unique_experts_per_method':9,'rows':rows,'scope':'t=0; u in [1.98,2.02], x in [1.24,1.27]; augmented-state expert policy','proof':'retained common-shock concavity and stopping correction with the same u range; convex unrestricted upper applied separately on each cell; no high-dimensional scaling claim'})


def reference(selected):
    for seed in (24501,24502):
        ts,geo=prepared(seed,reference=True);obj=setup(reference=True);initial=obj(ts['neural'],True);ci,cs=cert(initial,True)
        for m,opt in [(m,'adam') for m in METHODS]+[('direct','lbfgsb')]:
            run_one(REV/f'results/reference/seed{seed}/{m}_{opt}',ts[m],setup(reference=True),opt,selected.get(m,.005),ci,initial,reference=True,meta={'method':m,'seed':seed,'reference_economy':True,'preprocessing_seconds':geo['seconds'] if m not in ('neural','direct') else 0.})


def failure(selected):
    frozen=ROOT/'revisions/2026-09-23-r23/results/crossed/seed23200/vertex3'
    net=Actor();state=json.loads((frozen/'initial_network.json').read_text())
    net.load_state_dict({k:torch.tensor(v['tensor']) for k,v in state.items()})
    old=json.loads((frozen/'neural_lbfgsb/record.json').read_text())
    obj=setup(2.02,1.26);initial=obj(net,True);ci,cs=cert(initial)
    baseline=run_one(REV/'results/failure/regenerated',net,setup(2.02,1.26),'lbfgsb',.005,ci,initial,diagnostics=True,u=2.02,x=1.26,meta={'post_hoc_diagnostic':True})
    scaled=ScaledActor(net)
    matching=float(torch.max(torch.abs(scaled(NODES)-net(NODES))).detach())
    run_one(REV/'results/failure/scaled',scaled,setup(2.02,1.26),'lbfgsb',.005,ci,initial,diagnostics=True,u=2.02,x=1.26,meta={'post_hoc_diagnostic':True,'initial_output_matching_error':matching})
    trained=Actor();sd=json.loads((REV/'results/failure/regenerated/final_parameters.json').read_text())
    trained.load_state_dict({k:torch.tensor(v['tensor']) for k,v in sd.items()})
    di=setup(2.02,1.26)(trained,True);ic,_=cert(di)
    run_one(REV/'results/failure/restart_tighter',trained,setup(2.02,1.26),'lbfgsb',.005,ic,di,diagnostics=True,u=2.02,x=1.26,meta={'post_hoc_diagnostic':True,'additional_restart_budget':400},gtol=1e-12)
    direct=Coordinates(trained(NODES).detach(),CHART)
    run_one(REV/'results/failure/direct_restart',direct,setup(2.02,1.26),'lbfgsb',.005,ic,di,diagnostics=True,u=2.02,x=1.26,meta={'post_hoc_diagnostic':True,'additional_restart_budget':400})
    ref=json.loads((frozen/'direct_lbfgsb/candidate_parameters.json').read_text())['coefficients']['tensor'];ref=np.array(ref)
    distances={}
    for case in ('regenerated','scaled','restart_tighter','direct_restart'):
        r=json.loads((REV/f'results/failure/{case}/record.json').read_text());act=r['final_actor'];dref=json.loads((frozen/'direct_lbfgsb/candidate_actor.json').read_text())
        distances[case]={'raw_outputs_l2_to_frozen_direct':float(np.linalg.norm(np.array(json.loads((REV/f'results/failure/{case}/checkpoint_400.json').read_text())['raw_outputs'])-ref)),'financed_coefficients_l2_to_frozen_direct':float(np.linalg.norm(np.array([act[k] for k in ('b','s','theta')])-np.array([dref[k] for k in ('b','s','theta')]))),'regret_upper':r['final_candidate_certificate'].get('regret_upper'),'termination':r['termination'],'gradient_calls':r['gradient_calls']}
    write(REV/'results/failure_summary.json',{'inherited_record_retained_at':str((frozen/'neural_lbfgsb/record.json').relative_to(ROOT)),'inherited_termination':old['termination'],'inherited_regret_upper':old['candidate_certificate']['regret_upper'],'diagnostic_results':distances,'interpretation':'post-hoc mechanism diagnostics, not tuning or held-out selection'})


def dependency_lock():
    modules={}
    for name,m in list(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if not p:continue
        p=Path(p).resolve()
        if ROOT in p.parents and p.is_file():modules[name]={'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    data={}
    for folder in ('revisions/2026-09-23-r16/results/fresh_library','revisions/2026-09-23-r23/results/crossed/seed23200/vertex3','revisions/2026-09-23-r22/results/full_state'):
        for p in (ROOT/folder).rglob('*.json'):data[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    write(REV/'results/DEPENDENCY_LOCK.json',{'protocol_commit':PROTOCOL_COMMIT,'runtime_imported_repository_modules':modules,'inherited_data_sha256':data,'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'torch':torch.__version__,'platform':platform.platform(),'torch_threads':torch.get_num_threads(),'source_commit':os.getenv('GITHUB_SHA','local source snapshot'),'module_resolution':'actual runtime module paths after complete study; all repository imports are transitively included; data files separately hashed'})
    old=json.loads((ROOT/'revisions/2026-09-23-r22/results/full_state/summary.json').read_text());env=json.loads((ROOT/'revisions/2026-09-23-r22/results/full_state/time_envelope.json').read_text())
    cur=next(r for r in env if r['phase']=='candidate')
    write(REV/'results/full_state_canonical.json',{'schema_version':2,'source':'R22 frozen discounted suffix envelope, not a newly trained R24 global policy','all_start_times_regret_upper':cur['all_start_times_regret_upper'],'t0_regret_upper':old['candidate_bound'],'deprecated_undiscounted_all_times_bound':old['candidate_all_initial_times_bound'],'deprecated_field_path':'revisions/2026-09-23-r22/results/full_state/summary.json:candidate_all_initial_times_bound','target':.01,'target_established':False,'separate_actor_payoff_improvement_established':False})


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--phase',default='all',choices=('all','tuning','heldout','multicell','reference','failure'));a=parser.parse_args()
    t=time.perf_counter()
    if a.phase in ('all','tuning'):selected=run_tuning()
    else:selected=json.loads((REV/'results/tuning_selection.json').read_text())['selected']
    for phase,fn in [('heldout',heldout),('multicell',multicell),('reference',reference),('failure',failure)]:
        if a.phase in ('all',phase):fn(selected)
    dependency_lock();write(REV/f'results/execution_{a.phase}.json',{'seconds':time.perf_counter()-t,'protocol_commit':PROTOCOL_COMMIT,'phase':a.phase,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'exit_status':'completed'})
if __name__=='__main__':main()
