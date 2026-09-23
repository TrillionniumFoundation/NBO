"""R28 unknown-solution stopped inventory control and exact Bellman completion.
Training never receives the optimal reference. Policies/certificates are frozen
before a separately implemented rational optimal recursion is invoked.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json, math, os, platform, resource, sys, time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import minimize
import torch
ROOT=Path(__file__).resolve().parents[3]
REV=ROOT/'revisions/2026-09-24-r28'
OUT=REV/'results/inventory'
T=8; BETA=F(99,100); EPS=F(1,100)
ETA=EPS/sum(BETA**j for j in range(T))

def write(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rational_array(a):return [[str(int(v)) for v in row] for row in a]

class Model:
    def __init__(self,d:int,L:int=4):
        self.d=d;self.L=L;self.R=100*d;self.D=d+2
        self.states=np.array(list(itertools.product(range(L),repeat=d)),dtype=np.int64)
        self.N=len(self.states);self.A=1+2*d
        self.orders=np.zeros((self.A,d),dtype=np.int64)
        for j in range(d):self.orders[1+2*j,j]=1;self.orders[2+2*j,j]=2
        demand=[np.zeros(d,dtype=np.int64),np.ones(d,dtype=np.int64)]
        for j in range(d):v=np.ones(d,dtype=np.int64);v[j]=2;demand.append(v)
        self.demand=np.array(demand)
        available=self.states[:,None,:]+self.orders[None,:,:]
        self.feasible=np.all(available<L,axis=2);self.feasible[0,:]=False;self.feasible[0,0]=True
        y=np.maximum(available[:,:,None,:]-self.demand[None,None,:,:],0)
        self.next=(y*(L**np.arange(d-1,-1,-1))).sum(-1).clip(0,self.N-1)
        sales=np.minimum(available[:,:,None,:],self.demand[None,None,:,:])
        shortage=np.maximum(self.demand[None,None,:,:]-available[:,:,None,:],0)
        units=self.orders.sum(-1)
        self.reward=(self.R*sales.sum(-1)-(3*self.R//5)*units[None,:,None]
            -(self.R//10)*(units[None,:,None]>0)-(self.R//50)*(y*y).sum(-1)
            -(2*self.R//5)*(shortage*shortage).sum(-1)-5*shortage.sum(-1)**2).astype(np.int64)
        self.terminal=((self.R//5)*self.states.sum(-1)-(self.R//50)*(self.states*self.states).sum(-1)).astype(np.int64)
        self.stop_num=-2*self.R-d*self.R//5
        self.terminal[0]=self.stop_num
        self.den=[0]*(T+1);self.den[T]=self.R
        for t in reversed(range(T)):self.den[t]=100*self.D*self.den[t+1]
        self.row=np.arange(self.N)
        self.x=2*self.states/(L-1)-1
    def qfloat(self,v):
        q=self.reward.mean(-1)/self.R+float(BETA)*v[self.next].mean(-1)
        q[~self.feasible]=-np.inf;q[0,:]=-np.inf;q[0,0]=self.stop_num/self.R
        return q
    def qexact(self,t,vnext):
        r=self.reward.sum(-1).astype(object)
        q=100*(self.den[t+1]//self.R)*r+99*np.sum(vnext[self.next],axis=2)
        for s in range(self.N):
            for a in range(self.A):
                if not self.feasible[s,a]:q[s,a]=None
        q[0,0]=self.stop_num*(self.den[t]//self.R)
        return q
    def choose(self,q):
        a=np.zeros(self.N,dtype=np.int64);v=np.empty(self.N,dtype=object)
        for s in range(self.N):
            a[s]=max(np.flatnonzero(self.feasible[s]),key=lambda b:q[s,b]);v[s]=q[s,a[s]]
        return a,v
    def memory(self):return sum(x.nbytes for x in vars(self).values() if isinstance(x,np.ndarray))

class CallsExhausted(Exception):pass

def polynomial_features(x,degree):
    powers=[p for p in itertools.product(range(degree+1),repeat=x.shape[1]) if sum(p)<=degree]
    return np.column_stack([np.prod(x**np.array(p),axis=1) for p in powers]),powers

def train(model:Model,kind:str,width=0,depth=0,seed=0,degree=0):
    start=time.perf_counter();policy=np.zeros((T,model.N),dtype=np.int64)
    vnext=model.terminal/model.R;records=[];snapshots=[];compile_seconds=0.
    if kind=='polynomial':features,powers=polynomial_features(model.x,degree)
    else:x=torch.tensor(model.x,dtype=torch.float64)
    for t in reversed(range(T)):
        tc=time.perf_counter();q=model.qfloat(vnext);policy[t]=np.argmax(q,axis=1);target=q[model.row,policy[t]]
        compile_seconds+=time.perf_counter()-tc
        if t==0:continue # No predecessor uses a period-zero value approximation.
        mean=float(target.mean());scale=max(float(target.std()),1e-8);y=(target-mean)/scale
        if kind=='polynomial':
            coeff,*_=np.linalg.lstsq(features,y,rcond=None)
            pred=features@coeff
            rec={'t':t,'kind':kind,'least_squares_columns':features.shape[1],'mse':float(np.mean((pred-y)**2))}
            snapshots.append({'t':t,'powers':powers,'coefficients':coeff.tolist(),'mean':mean,'scale':scale})
        else:
            torch.manual_seed(seed+1000*t)
            layers=[];dim=model.d
            for _ in range(depth):layers.extend([torch.nn.Linear(dim,width),torch.nn.Tanh()]);dim=width
            layers.append(torch.nn.Linear(dim,1));net=torch.nn.Sequential(*layers).double()
            yt=torch.tensor(y,dtype=torch.float64);opt=torch.optim.Adam(net.parameters(),lr=.01)
            for _ in range(400):
                opt.zero_grad(set_to_none=True);loss=((net(x).squeeze(-1)-yt)**2).mean();loss.backward();opt.step()
            params=list(net.parameters());sizes=[p.numel() for p in params]
            def vector():return np.concatenate([p.detach().numpy().ravel() for p in params]).copy()
            def assign(z):
                off=0
                with torch.no_grad():
                    for p,n in zip(params,sizes):p.copy_(torch.tensor(z[off:off+n]).reshape(p.shape));off+=n
            count=0;accepted=vector();accepted_iter=0
            def fun(z):
                nonlocal count
                if count>=150:raise CallsExhausted()
                assign(z);net.zero_grad(set_to_none=True);loss=((net(x).squeeze(-1)-yt)**2).mean();loss.backward();count+=1
                g=np.concatenate([p.grad.detach().numpy().ravel() for p in params])
                if not np.isfinite(g).all() or not torch.isfinite(loss):raise ArithmeticError('Nonfinite training value')
                return float(loss.detach()),g
            def callback(z):
                nonlocal accepted,accepted_iter
                accepted=z.copy();accepted_iter+=1
            try:
                r=minimize(fun,accepted,jac=True,method='L-BFGS-B',callback=callback,
                    options={'maxfun':150,'maxiter':150,'maxls':30,'ftol':1e-13,'gtol':1e-9})
                assign(r.x);termination=str(r.message)
            except CallsExhausted:assign(accepted);termination='150-call cap; last accepted iterate restored'
            pred=net(x).detach().numpy().ravel()
            rec={'t':t,'kind':kind,'adam_steps':400,'lbfgs_calls':count,'accepted_lbfgs_iterations':accepted_iter,
                 'parameter_count':sum(sizes),'mse':float(np.mean((pred-y)**2)),'termination':termination}
            snapshots.append({'t':t,'mean':mean,'scale':scale,'weights':{k:v.detach().tolist() for k,v in net.state_dict().items()}})
        vnext=mean+scale*pred;vnext[0]=model.stop_num/model.R;records.append(rec)
    elapsed=time.perf_counter()-start
    return policy,{'kind':kind,'width':width,'depth':depth,'seed':seed,'degree':degree,
        'generation_seconds':elapsed-compile_seconds,'compilation_seconds':compile_seconds,'stages':records,
        'network_or_polynomial_snapshots':snapshots,'training_uses_optimal_reference':False,
        'fitted_stages':7,'period_zero_fit_omitted_as_unused':True}

def exact_policy(model,policy):
    values=[None]*(T+1);values[T]=model.terminal.astype(object)
    for t in reversed(range(T)):
        q=model.qexact(t,values[t+1]);values[t]=q[model.row,policy[t]].copy()
        assert all(v is not None for v in values[t])
    return values

def residual_certificate(model,policy):
    start=time.perf_counter();v=exact_policy(model,policy)
    b=[None]*(T+1);b[T]=np.zeros(model.N,dtype=object);deficits=[None]*T
    for t in reversed(range(T)):
        q=model.qexact(t,v[t+1]);_,best=model.choose(q);delta=best-v[t];assert min(delta)>=0;deficits[t]=delta
        future=99*np.sum(b[t+1][model.next],axis=2)
        b[t]=np.array([delta[s]+max(future[s,a] for a in np.flatnonzero(model.feasible[s])) for s in range(model.N)],dtype=object)
        b[t][0]=0
    bound=max(F(int(max(b[t])),model.den[t]) for t in range(T))
    return v,{'bound_rational':str(bound),'bound_upper':math.nextafter(float(bound),math.inf) if bound else 0.,
        'bound_at_restart': [str(F(int(max(b[t])),model.den[t])) for t in range(T+1)],
        'local_deficit_numerators':rational_array(deficits),'envelope_numerators':rational_array(b),
        'denominators':[str(d) for d in model.den], 'seconds':time.perf_counter()-start,
        'target_established_exact':bound<=EPS,'optimal_reference_used':False}

def complete(model,raw):
    start=time.perf_counter();p=raw.copy();vnext=model.terminal.astype(object);changes=[]
    for t in reversed(range(T)):
        q=model.qexact(t,vnext);greedy,best=model.choose(q);v=np.empty(model.N,dtype=object)
        for s in range(model.N):
            a=int(p[t,s]);gap=F(int(best[s]-q[s,a]),model.den[t])
            if gap>ETA:
                changes.append({'t':t,'state':s,'old_action':a,'new_action':int(greedy[s]),'old_local_deficit':str(gap)})
                a=int(greedy[s]);p[t,s]=a
            v[s]=q[s,a]
        vnext=v
    return p,{'seconds':time.perf_counter()-start,'changed_actions':len(changes),
        'changed_fraction_nonstopped':len(changes)/(T*(model.N-1)),'eta_rational':str(ETA),'changes':changes,
        'optimal_reference_used':False}

def independent_optimal(model):
    """Independent scalar integer recursion; does not call qexact or choose."""
    start=time.perf_counter();v=[None]*(T+1);v[T]=list(map(int,model.terminal));p=np.zeros((T,model.N),dtype=np.int64)
    for t in reversed(range(T)):
        w=[]
        for s in range(model.N):
            if s==0:w.append(model.stop_num*(model.den[t]//model.R));continue
            best=None;best_a=0
            for a in np.flatnonzero(model.feasible[s]):
                n=0
                for z in range(model.D):
                    n+=100*(model.den[t+1]//model.R)*int(model.reward[s,a,z])+99*v[t+1][int(model.next[s,a,z])]
                if best is None or n>best:best=n;best_a=int(a)
            w.append(best);p[t,s]=best_a
        v[t]=w
    return [np.array(w,dtype=object) for w in v],p,time.perf_counter()-start

def evaluate(model,values,opt,policy,optimal_policy):
    regrets=[];worst=F(0);witness=None;bytime=[]
    for t in range(T):
        local=[]
        for s in range(model.N):
            e=F(int(opt[t][s]-values[t][s]),model.den[t]);assert e>=0
            if e>worst:worst=e;witness={'t':t,'state_index':s,'state':model.states[s].tolist(),'regret_rational':str(e)}
            local.append(float(e));regrets.append(float(e))
        bytime.append(max(local))
    return {'worst_regret_rational':str(worst),'worst_regret':float(worst),'witness':witness,
        'regret_quantiles':dict(zip(['min','median','q90','q99','max'],np.quantile(regrets,[0,.5,.9,.99,1]).tolist())),
        'worst_regret_by_restart':bytime,'tolerances':{str(e):worst<=F(str(e)) for e in [.01,.05,.1,.5]},
        'action_disagreement_fraction':float(np.mean(policy[:,1:]!=optimal_policy[:,1:]))}

def cases(d,L):
    if L==4:
        specs=[dict(kind='neural',width=w,depth=h,seed=s) for w in (16,32) for h in (1,2) for s in (27301,27302)]
    else:specs=[dict(kind='neural',width=32,depth=2,seed=s) for s in (27301,27302)]
    return specs+[dict(kind='polynomial',degree=g) for g in (2,3)]

def run_model(d,L):
    root=OUT/f'd{d}_L{L}';root.mkdir(parents=True,exist_ok=True);all_start=time.perf_counter();frozen=[]
    for spec in cases(d,L):
        tag=(f"neural_w{spec['width']}_h{spec['depth']}_s{spec['seed']}" if spec['kind']=='neural' else f"polynomial_p{spec['degree']}")
        path=root/tag;path.mkdir(exist_ok=True)
        if (path/'pre_reference.json').exists():
            frozen.append(json.loads((path/'pre_reference.json').read_text()));continue
        started=time.perf_counter();ts=time.perf_counter();m=Model(d,L);setup=time.perf_counter()-ts
        raw,training=train(m,**spec);write(path/'training.json',training);write(path/'raw_policy.json',raw.tolist());rawsha=digest(path/'raw_policy.json')
        rawv,rawcert=residual_certificate(m,raw);write(path/'raw_certificate.json',rawcert)
        ts=time.perf_counter();fresh=Model(d,L);completion_setup=time.perf_counter()-ts
        comp,changes=complete(fresh,np.array(json.loads((path/'raw_policy.json').read_text()),dtype=np.int64))
        write(path/'completed_policy.json',comp.tolist());compsha=digest(path/'completed_policy.json')
        compv,cc=residual_certificate(fresh,comp);write(path/'completed_certificate.json',cc);write(path/'completion.json',changes)
        assert cc['target_established_exact']
        record={'d':d,'L':L,'tag':tag,'spec':spec,'states':m.N,'actions':m.A,'demand_outcomes':m.D,
            'raw_policy_sha256':rawsha,'completed_policy_sha256':compsha,'raw_certificate_sha256':digest(path/'raw_certificate.json'),
            'completed_certificate_sha256':digest(path/'completed_certificate.json'),
            'construction_seconds':setup,'completion_construction_seconds':completion_setup,
            'generation_seconds':training['generation_seconds'],'compilation_seconds':training['compilation_seconds'],
            'raw_certification_seconds':rawcert['seconds'],'completion_seconds':changes['seconds'],
            'completed_certification_seconds':cc['seconds'],'candidate_and_reference_free_certification_elapsed':time.perf_counter()-started,
            'model_array_bytes':m.memory(),'compiled_policy_bytes':int(raw.nbytes),'process_high_water_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'raw_residual_bound':rawcert['bound_upper'],'completed_residual_bound':cc['bound_upper'],
            'completed_target_established_exact':cc['target_established_exact'],'changed_actions':changes['changed_actions'],
            'changed_fraction_nonstopped':changes['changed_fraction_nonstopped'],'reference_has_been_constructed':False}
        write(path/'pre_reference.json',record);frozen.append(record)
        print('FROZEN',d,L,tag,cc['bound_upper'],flush=True)
    # All cases for this model, not merely the best case, have now been frozen.
    write(root/'FREEZE_MANIFEST.json',frozen);freeze_sha=digest(root/'FREEZE_MANIFEST.json')
    ts=time.perf_counter();m=Model(d,L);reference_setup=time.perf_counter()-ts
    opt,optimal_policy,reference_seconds=independent_optimal(m)
    write(root/'optimal_reference.json',{'values':rational_array(opt),'denominators':list(map(str,m.den)),
        'policy':optimal_policy.tolist(),'construction_seconds':reference_setup,'solve_seconds':reference_seconds,
        'candidate_freeze_sha256':freeze_sha,'generated_after_all_candidates_and_certificates':True})
    rows=[]
    for rec in frozen:
        path=root/rec['tag'];raw=np.array(json.loads((path/'raw_policy.json').read_text()));comp=np.array(json.loads((path/'completed_policy.json').read_text()))
        assert digest(path/'raw_policy.json')==rec['raw_policy_sha256']
        assert digest(path/'completed_policy.json')==rec['completed_policy_sha256']
        ts=time.perf_counter();rv=exact_policy(m,raw);cv=exact_policy(m,comp)
        raw_eval=evaluate(m,rv,opt,raw,optimal_policy);comp_eval=evaluate(m,cv,opt,comp,optimal_policy)
        eval_seconds=time.perf_counter()-ts
        for mode,vals in [('raw',rv),('completed',cv)]:
            cert=json.loads((path/f'{mode}_certificate.json').read_text())
            for t in range(T):
                for s in range(m.N):assert opt[t][s]-vals[t][s]<=int(cert['envelope_numerators'][t][s])
        rec={**rec,'raw':raw_eval,'completed':comp_eval,'reference_construction_seconds':reference_setup,
             'reference_solve_seconds':reference_seconds,'independent_reference_evaluation_seconds':eval_seconds,
             'standalone_completed_seconds':rec['candidate_and_reference_free_certification_elapsed']+reference_setup+reference_seconds+eval_seconds,
             'reference_cost_amortized_seconds':(reference_setup+reference_seconds)/len(frozen),
             'freeze_manifest_sha256':freeze_sha,'no_reference_leakage_order_enforced':True}
        write(path/'record.json',rec);rows.append(rec)
    write(root/'summary.json',rows);print('MODEL COMPLETE',d,L,'seconds',time.perf_counter()-all_start,flush=True)
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('--model',type=int,nargs=2);args=p.parse_args()
    torch.set_num_threads(1);torch.set_default_dtype(torch.float64);torch.use_deterministic_algorithms(True)
    models=[tuple(args.model)] if args.model else [(2,4),(3,4),(4,4),(4,5)]
    rows=[]
    for d,L in models:rows+=run_model(d,L)
    if not args.model:
        write(OUT/'summary.json',rows)
        write(OUT/'environment.json',{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'torch':torch.__version__,
            'platform':platform.platform(),'processor':platform.processor(),'cpu_affinity':sorted(os.sched_getaffinity(0)),
            'torch_threads':torch.get_num_threads(),'process_high_water_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'eta_rational':str(ETA),'all_34_cases_retained':len(rows)==34})
if __name__=='__main__':main()
