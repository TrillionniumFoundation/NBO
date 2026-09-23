"""R25: expanded calibration, moving historical transport, online verification.
The unchanged directed checker, not the proposal gradient, certifies payoffs.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,math,os,platform,sys,time
from pathlib import Path
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r25'
spec=importlib.util.spec_from_file_location('r24study',ROOT/'revisions/2026-09-23-r24/replication/study.py')
S=importlib.util.module_from_spec(spec);sys.modules[spec.name]=S;spec.loader.exec_module(S);S.REV=REV
METHODS=('neural','direct','diagonal','tangent','white','moving');RATES=(.005,.02,.08,.32,1.28,5.12,20.48)
PROTOCOL='44e53219b66e75cc1c343dbe3464eebeb4f6c94e';Q=S.CHART;NODES=S.NODES;write=S.write

def clean(x):
    if isinstance(x,torch.Tensor):return x.detach().cpu().tolist()
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return clean(x.item())
    if isinstance(x,float) and not math.isfinite(x):return None
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    return x

def sha(x):return hashlib.sha256(json.dumps(clean(x),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def initial(seed):
    a=S.network(seed);obj=S.setup();actor=obj(a,True);c,sec=S.cert(actor)
    if c['status']!='CERTIFIED':raise RuntimeError(('initial',seed,c))
    mats,geom=S.geometries(a);return a,actor,c,sec,mats,geom

def make(arm,a,mats):return copy.deepcopy(a) if arm=='neural' else S.Coordinates(a(NODES),mats['direct' if arm=='moving' else arm])

class Moving:
    """47 economic coordinates and an explicitly charged 355-parameter carrier."""
    def __init__(self,actor):
        self.carrier=copy.deepcopy(actor);self.net=S.Coordinates(actor(NODES),Q)
        p=torch.tensor(S.vector(self.carrier));self.m=torch.zeros_like(p);self.v=torch.zeros_like(p);self.n=0
        self.jacobian_calls=0;self.geometry_seconds=0.
    def state(self):return {'carrier':S.vector(self.carrier),'z':self.net.z.detach().clone(),'m':self.m.clone(),'v':self.v.clone(),'n':self.n}
    def restore(self,s):
        S.assign(self.carrier,np.asarray(s['carrier']));self.net.z.data.copy_(s['z']);self.m=s['m'].clone();self.v=s['v'].clone();self.n=s['n']
    def step(self,obj,lr):
        self.net.zero_grad(set_to_none=True);loss=-obj(self.net);loss.backward();g=self.net.z.grad.detach().clone()
        start=time.perf_counter();j=Q.T@S.flat_jacobian(self.carrier);self.geometry_seconds+=time.perf_counter()-start;self.jacobian_calls+=1
        gp=j.T@g;self.n+=1;self.m=.9*self.m+.1*gp;self.v=.999*self.v+.001*gp.square()
        dp=-lr*(self.m/(1-.9**self.n))/((self.v/(1-.999**self.n)).sqrt()+1e-8)
        dy=j@dp-lr*1e-6*g;scale=min(1.,.5/max(float(dy.norm()),1e-300));dp=dp*scale;dy=dy*scale
        if not torch.isfinite(dp).all() or not torch.isfinite(dy).all():raise FloatingPointError('nonfinite moving step')
        old=self.carrier(NODES).detach().flatten();S.assign(self.carrier,S.vector(self.carrier)+dp.numpy());self.net.z.data.add_(dy)
        nonlinear=Q.T@(self.carrier(NODES).detach().flatten()-old)-j@dp
        return {'loss':float(loss.detach()),'quotient_gradient_norm':float(g.norm()),'output_step_norm':float(dy.norm()),'trust_scale':scale,
                'dropped_nonlinear_remainder_norm':float(nonlinear.norm()),'carrier_mismatch_norm':float((Q.T@(self.carrier(NODES).detach().flatten()-self.net(NODES).detach().flatten())).norm())}

def moving_run(path,a,obj,lr,ic,ia,cap,cps,meta):
    path=Path(path)
    if (path/'record.json').exists():return json.loads((path/'record.json').read_text())
    m=Moving(a);history=[];snaps={};start=time.perf_counter();status='call_cap';calls=0;initial_state=m.state()
    try:
        for i in range(1,cap+1):
            d=m.step(obj,lr);calls=i;history.append({'call':i,'elapsed_generation':time.perf_counter()-start,**d})
            if i in cps:snaps[i]={'state':m.state(),'seconds':time.perf_counter()-start,'actual_calls':i}
    except (ArithmeticError,ValueError,FloatingPointError,RuntimeError) as e:
        status=type(e).__name__+': '+str(e);m.restore(snaps[max(snaps)]['state'] if snaps else initial_state)
    generation=time.perf_counter()-start;final=m.state()
    for cp in cps:
        if cp not in snaps:snaps[cp]={'state':copy.deepcopy(final),'seconds':generation,'actual_calls':calls,'carried_forward_after_termination':True}
    inc=ic;incactor=ia;rows=[];checking=0.
    for cp,snap in sorted(snaps.items()):
        m.restore(snap['state']);actor=obj(m.net,True);cert,sec=S.cert(actor);checking+=sec
        accept=cert['status']=='CERTIFIED' and cert['value_interval'][0]>inc['value_interval'][1]
        if accept:inc=cert;incactor=actor
        row={'checkpoint':cp,'actual_calls':snap['actual_calls'],'generation_seconds':snap['seconds'],'raw_outputs':clean(m.net(NODES)),
             'candidate_actor':actor,'certificate':cert,'accepted_for_deployment':accept,'deployed_certificate':inc,'deployed_actor':incactor,
             'checker_seconds':sec,'cumulative_checker_seconds':checking}
        write(path/f'checkpoint_{cp:03d}.json',row);rows.append(row)
    m.restore(final)
    r={'optimizer':'historical_transport_adam','learning_rate':lr,'gradient_calls':calls,'function_calls':calls,'generation_seconds':generation,
       'diagnostic_seconds':0.,'geometry_seconds_included_in_generation':m.geometry_seconds,'jacobian_evaluations':m.jacobian_calls,
       'parameter_dimension':47,'carrier_dimension':355,'carrier_adam_moment_scalars':710,'isotropic_regularization':1e-6,'output_step_cap':.5,
       'termination':status,'initial_certificate':ic,'initial_actor':ia,'checkpoints':rows,'final_actor':obj(m.net,True),
       'final_candidate_certificate':rows[-1]['certificate'],'final_deployed_certificate':rows[-1]['deployed_certificate'],'checker_seconds':checking,
       'candidate_actor_sha256':sha(obj(m.net,True)),'deployed_actor_sha256':sha(incactor),'execution_did_not_rollback_proposal_optimizer':True,**meta}
    write(path/'history.json',history);write(path/'final_state.json',clean(final));write(path/'record.json',clean(r))
    print(str(path.relative_to(REV)),calls,rows[-1]['certificate'].get('regret_upper'),status,flush=True);return r

def run(path,arm,a,mats,obj,opt,lr,c,actor,cap,cps,meta):
    if arm=='moving':return moving_run(path,a,obj,lr,c,actor,cap,cps,meta)
    return S.run_one(path,make(arm,a,mats),obj,opt,lr,c,actor,cap,cps,False,meta=meta)

def tuning():
    records=[]
    for seed in (25001,25002):
        a,actor,c,secs,mats,geom=initial(seed)
        write(REV/f'results/tuning/seed{seed}/initial.json',{'actor':actor,'certificate':c,'checker_seconds':secs,'geometry':geom})
        for arm in METHODS:
            for lr in RATES:
                path=REV/f'results/tuning/seed{seed}/{arm}/rate{lr:g}'
                r=run(path,arm,a,mats,S.setup(),'adam',lr,c,actor,200,(200,),{'phase':'tuning','arm':arm,'seed':seed,'orders':[8,16],
                    'preprocessing_seconds':geom['seconds'] if arm not in ('neural','direct','moving') else 0.})
                cert=r['final_candidate_certificate'];records.append({'arm':arm,'seed':seed,'learning_rate':lr,'status':cert['status'],
                    'payoff_lower':cert.get('value_interval',[None,None])[0],'regret_upper':cert.get('regret_upper'),
                    'generation_seconds':r['generation_seconds'],'checker_seconds':r['checker_seconds'],'path':str(path.relative_to(ROOT))})
    selection={}
    for arm in METHODS:
        trials=[]
        for lr in RATES:
            rows=[r for r in records if r['arm']==arm and r['learning_rate']==lr]
            score=sum(r['payoff_lower'] for r in rows)/2 if all(r['status']=='CERTIFIED' for r in rows) else None
            trials.append({'learning_rate':lr,'mean_certified_lower':score,'all_feasible':score is not None})
        usable=[x for x in trials if x['mean_certified_lower'] is not None]
        if not usable:raise RuntimeError(('no feasible rate',arm))
        best=max(x['mean_certified_lower'] for x in usable);selected=min((x for x in usable if best-x['mean_certified_lower']<=1e-10),key=lambda x:x['learning_rate'])
        k=list(RATES).index(selected['learning_rate']);deteriorated=any(x['mean_certified_lower'] is None or x['mean_certified_lower']<selected['mean_certified_lower']-1e-10 for x in trials[k+1:])
        selection[arm]={'selected_rate':selected['learning_rate'],'selected_score':selected['mean_certified_lower'],
            'interior_with_larger_deterioration':0<k<len(RATES)-1 and deteriorated,'censored_at_upper_endpoint':k==len(RATES)-1,'trials':trials}
    write(REV/'results/tuning_selection.json',selection);write(REV/'results/tuning_ledger.json',records);print('SELECTION',json.dumps(selection),flush=True)

def heldout():
    selected=json.loads((REV/'results/tuning_selection.json').read_text());records=[]
    for seed in (25101,25102):
        a,actor,c,sec,mats,geom=initial(seed)
        for orders in ((8,16),(12,24)):
            obj=S.setup(orders=orders);ia=obj(a,True);ic,isec=S.cert(ia)
            if ic['status']!='CERTIFIED':raise RuntimeError(('heldout initial',ic))
            for arm,opt in [(x,'adam') for x in METHODS]+[('neural','lbfgsb'),('direct','lbfgsb')]:
                lr=selected[arm]['selected_rate'] if opt=='adam' else None
                path=REV/f'results/heldout/seed{seed}/q{orders[0]}_{orders[1]}/{arm}_{opt}'
                meta={'phase':'heldout','arm':arm,'seed':seed,'orders':list(orders),'initial_checker_seconds':isec,
                      'preprocessing_seconds':geom['seconds'] if arm not in ('neural','direct','moving') else 0.}
                r=run(path,arm,a,mats,S.setup(orders=orders),opt,lr,ic,ia,400,S.CHECKPOINTS,meta)
                records.append({'path':str(path.relative_to(ROOT)),**{k:r[k] for k in ('arm','seed','orders','optimizer','learning_rate','gradient_calls','generation_seconds','checker_seconds','final_deployed_certificate')}})
    write(REV/'results/heldout_ledger.json',records)

def online():
    selected=json.loads((REV/'results/tuning_selection.json').read_text());allrows=[]
    for seed in (25101,25102):
        a,actor,c,sec,mats,geom=initial(seed)
        for arm in ('neural','direct','moving'):
            path=REV/f'results/online/seed{seed}/{arm}'
            if (path/'record.json').exists():allrows.append(json.loads((path/'record.json').read_text()));continue
            obj=S.setup();ia=obj(a,True);ic,isec=S.cert(ia);lr=selected[arm]['selected_rate'];moving=Moving(a) if arm=='moving' else None
            net=moving.net if moving else make(arm,a,mats);opt=None if moving else torch.optim.Adam(net.parameters(),lr=lr)
            def state():return moving.state() if moving else {'parameters':S.vector(net),'optimizer':copy.deepcopy(opt.state_dict())}
            def restore(s):
                if moving:moving.restore(s)
                else:S.assign(net,s['parameters']);opt.load_state_dict(copy.deepcopy(s['optimizer']))
            incumbent_state=state();incert=ic;incactor=ia;rows=[];generation=checking=0.;start=time.perf_counter();calls=0
            for block in range(1,5):
                before_hash=sha(state());saved_hash=sha(incumbent_state);used_lr=lr;failure=None;t0=time.perf_counter()
                try:
                    if opt:
                        for group in opt.param_groups:group['lr']=lr
                    for _ in range(100):
                        if moving:moving.step(obj,lr)
                        else:
                            opt.zero_grad(set_to_none=True);loss=-obj(net);loss.backward();opt.step()
                            if not np.isfinite(S.vector(net)).all():raise FloatingPointError('online nonfinite')
                        calls+=1
                    cand=obj(net,True)
                except (ArithmeticError,ValueError,FloatingPointError,RuntimeError) as e:failure=type(e).__name__+': '+str(e);cand=None
                generation+=time.perf_counter()-t0;precheck=time.perf_counter()-start;candidate_hash=sha(state())
                cc,cs=S.cert(cand) if cand is not None else ({'status':'REJECTED_CHECK','error':failure},0.)
                checking+=cs;accept=cc['status']=='CERTIFIED' and cc['value_interval'][0]>incert['value_interval'][1];oldcert=incert
                if accept:incumbent_state=state();incert=cc;incactor=cand
                else:restore(incumbent_state);lr*=.5
                after_hash=sha(state())
                if not accept:assert after_hash==saved_hash,'rollback mismatch'
                row={'block':block,'cumulative_calls':calls,'learning_rate':used_lr,'next_learning_rate':lr,'state_hash_before_block':before_hash,
                     'incumbent_state_hash_before_block':saved_hash,'candidate_state_hash':candidate_hash,'state_hash_after_decision':after_hash,
                     'accepted':accept,'rollback_verified':not accept and after_hash==saved_hash,'candidate_actor':cand,'candidate_certificate':cc,
                     'previous_incumbent_certificate':oldcert,'deployed_certificate':incert,'elapsed_before_check':precheck,
                     'elapsed_after_decision':time.perf_counter()-start,'cumulative_generation_seconds':generation,
                     'cumulative_checker_seconds':checking,'checker_seconds':cs}
                rows.append(row);write(path/f'block_{block}.json',row);print('ONLINE',seed,arm,block,accept,cc.get('regret_upper'),flush=True)
            record={'seed':seed,'arm':arm,'gradient_calls':calls,'actual_online_elapsed_seconds':time.perf_counter()-start,'generation_seconds':generation,
                'checker_seconds':checking,'initial_checker_seconds':isec,'preprocessing_seconds':0.,'final_deployed_certificate':incert,
                'final_actor':incactor,'blocks':rows,'execution_did_not_rollback_proposal_optimizer':False,
                'jacobian_evaluations':moving.jacobian_calls if moving else 0,'geometry_seconds_included_in_generation':moving.geometry_seconds if moving else 0.}
            write(path/'record.json',record);allrows.append(record)
    write(REV/'results/online_ledger.json',allrows)

def main():
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['tuning','heldout','online','all'],default='all');args=p.parse_args()
    write(REV/'results/environment.json',{'protocol_commit':PROTOCOL,'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,
        'torch':torch.__version__,'torch_threads':torch.get_num_threads(),'serial_execution':True,'pid':os.getpid(),
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    if args.phase in ('tuning','all'):tuning()
    if args.phase in ('heldout','all'):heldout()
    if args.phase in ('online','all'):online()
if __name__=='__main__':main()
