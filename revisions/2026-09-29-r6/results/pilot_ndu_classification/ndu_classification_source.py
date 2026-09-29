"""Multilayer positive-weight NBO for the original two-state NDU economy.

The transition, stopping payoff, reflection, discount and CRRA normalization
are exactly the R2 scheme, factored once for repeated Bellman evaluations.
Neural fitting uses its own next-period critic, never the reference array.
Certificates enumerate EVERY finite-model state, action and time level.
"""
from __future__ import annotations
import argparse, copy, itertools, json, math, resource, time
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator
import torch
from torch import nn
OUT=Path(__file__).resolve().parents[1]/'results'
torch.set_default_dtype(torch.float64);torch.set_num_threads(1)

def action_set(name):
    if name=='r2': axes=([.02,.05,.1],[0,.375,.75],[-.15,0,.15])
    elif name=='adjustment': axes=([.02,.05,.1],[0,.375,.75],[-.45,-.30,-.15,0,.15,.30,.45])
    elif name=='expanded': axes=([.02,.05,.1,.2,.3],[0,.375,.75,1.125,1.5],[-.45,-.30,-.15,0,.15,.30,.45])
    elif name=='refined': axes=(np.linspace(.02,.3,9),np.linspace(0,1.5,9),np.linspace(-.45,.45,13))
    elif name=='expanded_domain': axes=([.02,.05,.1,.3,.6],[0,.75,1.5,2.25,3],[-.9,-.6,-.3,0,.3,.6,.9])
    else:raise ValueError(name)
    return np.array(list(itertools.product(*axes)),dtype=float)

class NDU:
    def __init__(self,nu=17,nx=25,steps=20,cost=1.,actions='expanded',wealth=(.5,2.)):
        self.us=np.linspace(1.2,3.,nu);self.ys=np.linspace(math.log(wealth[0]),math.log(wealth[1]),nx)
        self.nu,self.nx,self.steps,self.cost=nu,nx,steps,cost
        self.actions=action_set(actions);self.action_name=actions;self.h=1/steps;self.q=math.exp(-.04*self.h)
        U,Y=np.meshgrid(self.us,self.ys,indexing='ij');self.points=np.c_[U.ravel(),Y.ravel()]
        self.N=U.size;self.A=len(self.actions);self.g=self.terminal(*self.points.T)
        self.boundary=(self.points[:,1]==self.ys[0])|(self.points[:,1]==self.ys[-1])
        m,p,theta=self.actions.T
        reward=np.exp((1-U.ravel()[:,None])*(np.log(m)[None,:]+Y.ravel()[:,None]))/(1-U.ravel()[:,None])-.5*cost*theta[None,:]**2
        self.reward=self.h*reward;self.constant=np.zeros((self.N,self.A));indices=[];weights=[]
        for z1,z2 in [(math.sqrt(2),0),(-math.sqrt(2),0),(0,math.sqrt(2)),(0,-math.sqrt(2))]:
            up=self.reflect(self.points[:,0,None]+theta*self.h+.08*math.sqrt(self.h)*z1)
            yp=self.points[:,1,None]+(.02+p*.06-m-.5*p*p*.2**2)*self.h+p*.2*math.sqrt(self.h)*(-.3*z1+math.sqrt(.91)*z2)
            outside=(yp<self.ys[0])|(yp>self.ys[-1]);yp=np.clip(yp,self.ys[0],self.ys[-1])
            fu=(up-self.us[0])/(self.us[1]-self.us[0]);fy=(yp-self.ys[0])/(self.ys[1]-self.ys[0])
            iu=np.clip(np.floor(fu).astype(int),0,nu-2);iy=np.clip(np.floor(fy).astype(int),0,nx-2)
            wu=np.clip(fu-iu,0,1);wy=np.clip(fy-iy,0,1)
            for a,b,w in [(0,0,(1-wu)*(1-wy)),(1,0,wu*(1-wy)),(0,1,(1-wu)*wy),(1,1,wu*wy)]:
                indices.append((iu+a)*nx+iy+b);weights.append(np.where(outside,0,w/4))
            self.constant+=np.where(outside,self.terminal(up,yp)/4,0)
        self.index=np.stack(indices,axis=2).astype(np.int32);self.weights=np.stack(weights,axis=2)
        self.reward[self.boundary,:]=self.g[self.boundary,None];self.constant[self.boundary,:]=0;self.weights[self.boundary,:,:]=0
        if np.min(self.weights)<0 or np.max(self.weights.sum(axis=2))>1+1e-12:raise AssertionError('non-Markov weights')
        self.beta=self.q*max(1.,float(np.max(self.weights.sum(axis=2))))
    def reflect(self,u):
        L=self.us[-1]-self.us[0];z=(u-self.us[0])%(2*L)
        return self.us[0]+np.where(z<=L,z,2*L-z)
    @staticmethod
    def terminal(u,y):return np.exp((1-u)*y)/(1-u)
    def Q(self,v):
        v=np.asarray(v,dtype=float)
        if v.shape!=(self.N,) or not np.isfinite(v).all():raise ValueError('invalid continuation array')
        return self.reward+self.q*((self.weights*v[self.index]).sum(axis=2)+self.constant)
    def reference(self):
        start=time.perf_counter();v=np.empty((self.steps+1,self.N));a=np.empty((self.steps,self.N),int);v[-1]=self.g
        for n in range(self.steps-1,-1,-1):
            q=self.Q(v[n+1]);a[n]=q.argmax(axis=1);v[n]=q.max(axis=1)
        return v,a,time.perf_counter()-start
    def evaluate_policy(self,policy):
        policy=np.asarray(policy)
        if policy.shape!=(self.steps,self.N) or not np.issubdtype(policy.dtype,np.integer) or np.min(policy)<0 or np.max(policy)>=self.A:raise ValueError('invalid policy')
        v=np.empty((self.steps+1,self.N));v[-1]=self.g
        for n in range(self.steps-1,-1,-1):v[n]=self.Q(v[n+1])[np.arange(self.N),policy[n]]
        return v
    def certificate(self,values,policy):
        values=np.asarray(values)
        if values.shape!=(self.steps+1,self.N) or not np.isfinite(values).all():raise ValueError('invalid candidate values')
        self.evaluate_policy(policy) # also validates the policy before indexing
        terminal=float(np.max(abs(values[-1]-self.g)));deltas=[];gaps=[];faces=[]
        for n in range(self.steps):
            q=self.Q(values[n+1]);qa=q[np.arange(self.N),policy[n]]
            deltas.append(float(np.max(abs(values[n]-qa))));gaps.append(float(max(0,np.max(q.max(axis=1)-qa))))
            face=abs(values[n]-self.g).reshape(self.nu,self.nx)
            faces.append([float(np.max(face[:,0])),float(np.max(face[:,-1]))])
        ev=terminal;ov=terminal;reg=2*terminal;accounts=[]
        for n in range(self.steps-1,-1,-1):
            ev=deltas[n]+self.beta*ev;ov=deltas[n]+gaps[n]+self.beta*ov;reg=2*deltas[n]+gaps[n]+self.beta*reg
            accounts.append([n,ev,ov,reg])
        return dict(scope='all grid states, finite actions and time levels of the stated R2 scheme',
            state_grid=[self.nu,self.nx],steps=self.steps,action_count=self.A,
            evaluation_by_time=deltas,action_gap_by_time=gaps,boundary_by_time=faces,terminal_error=terminal,
            one_step_lipschitz=self.beta,policy_value_error_upper=ev,optimal_value_error_upper=ov,policy_regret_upper=reg,
            accounts=accounts[::-1],continuous_action_error=None,time_state_discretization_error=None,
            unchecked=['continuous-action coverage','continuous-time discretization','reflected PDE compatibility at terminal corners'])

def model_spec(m):
    return dict(state_grid=[m.nu,m.nx],steps=m.steps,T=1.,cost=m.cost,actions=m.action_name,
       action_count=m.A,action_bounds=np.c_[m.actions.min(axis=0),m.actions.max(axis=0)].tolist(),
       preference_interval=[1.2,3.],wealth_interval=np.exp(m.ys[[0,-1]]).tolist(),
       correlation=-.3,discount=.04,flow='(m X)^(1-u)/(1-u)-k theta^2/2',bequest='X^(1-u)/(1-u)',
       reflection='folded cubature endpoints',stopping='discretely observed wealth exit with exact analytical payoff',
       normalization='original unnormalized CRRA, reference consumption unit one')

class Net(nn.Module):
    def __init__(self,width=32,outputs=1):
        super().__init__();self.f=nn.Sequential(nn.Linear(2,width),nn.Tanh(),nn.Linear(width,width),nn.Tanh(),nn.Linear(width,outputs))
    def forward(self,x):return self.f(x)

class Critic(nn.Module):
    def __init__(self,model,width=32):
        super().__init__();self.net=Net(width);self.lo=float(model.ys[0]);self.hi=float(model.ys[-1])
    def forward(self,points):
        u,y=points[:,0:1],points[:,1:2];z=torch.cat([(u-2.1)/.9,2*(y-self.lo)/(self.hi-self.lo)-1],axis=1)
        return torch.exp((1-u)*y)/(1-u)+(y-self.lo)*(self.hi-y)*self.net(z)

def train(model,seed,method='nbo',width=32,critic_steps=100,actor_steps=60):
    if method not in ['nbo','direct']:raise ValueError(method)
    torch.manual_seed(seed);start=time.perf_counter();points=torch.tensor(model.points);norm=torch.tensor(np.c_[(model.points[:,0]-2.1)/.9,2*(model.points[:,1]-model.ys[0])/(model.ys[-1]-model.ys[0])-1])
    critic=Critic(model,width);actor=Net(width,model.A);values=np.empty((model.steps+1,model.N));values[-1]=model.g
    policies=np.empty((model.steps,model.N),int);history=[];models=[];failure=None
    for n in range(model.steps-1,-1,-1):
        q=model.Q(values[n+1]);qt=torch.tensor(q);choice=q.argmax(axis=1)
        actor_closures=0;critic_closures=0
        if method=='nbo':
            labels=torch.tensor(choice)
            opt=torch.optim.LBFGS(actor.parameters(),max_iter=actor_steps,history_size=15,line_search_fn='strong_wolfe',tolerance_grad=1e-8,tolerance_change=1e-10)
            def actor_closure():
                nonlocal actor_closures
                opt.zero_grad(set_to_none=True);loss=nn.functional.cross_entropy(actor(norm),labels)
                if not torch.isfinite(loss):raise FloatingPointError('nonfinite actor loss')
                loss.backward();actor_closures+=1;return loss
            try:opt.step(actor_closure)
            except Exception as exc:failure=f'actor step {n}: {type(exc).__name__}: {exc}';raise
            choice=actor(norm).detach().numpy().argmax(axis=1)
        policies[n]=choice;target=torch.tensor(q[np.arange(model.N),choice,None])
        # Direct Bellman has no actor; its saved policy is the exact finite-net maximizer.
        steps=critic_steps if method=='nbo' else critic_steps+actor_steps
        optc=torch.optim.LBFGS(critic.parameters(),max_iter=steps,history_size=20,line_search_fn='strong_wolfe',tolerance_grad=1e-9,tolerance_change=1e-11)
        def critic_closure():
            nonlocal critic_closures
            optc.zero_grad(set_to_none=True);loss=(critic(points)-target).square().mean()
            if not torch.isfinite(loss):raise FloatingPointError('nonfinite critic loss')
            loss.backward();critic_closures+=1;return loss
        optc.step(critic_closure);values[n]=critic(points).detach().numpy().ravel()
        history.append(dict(time_index=n,seconds=time.perf_counter()-start,critic_residual=float(np.max(abs(values[n]-target.numpy().ravel()))),actor_gap=float(np.max(q.max(axis=1)-q[np.arange(model.N),choice])),actor_closures=actor_closures,critic_closures=critic_closures))
        models.append(dict(time_index=n,critic=copy.deepcopy(critic.state_dict()),actor=copy.deepcopy(actor.state_dict()) if method=='nbo' else None))
    seconds=time.perf_counter()-start;cert=model.certificate(values,policies);optimal,reference_policy,refsec=model.reference();pv=model.evaluate_policy(policies)
    # Evaluate the actual off-grid multilayer critic; its target is explicitly the
    # finite-reference interpolant, not an exact continuous economic value.
    u_mid=(model.us[:-1]+model.us[1:])/2;y_mid=(model.ys[:-1]+model.ys[1:])/2
    U,Y=np.meshgrid(u_mid,y_mid,indexing='ij');held=np.c_[U.ravel(),Y.ravel()]
    pred=critic(torch.tensor(held)).detach().numpy().ravel();truth=RegularGridInterpolator((model.us,model.ys),optimal[0].reshape(model.nu,model.nx))(held)
    x=points.detach().clone().requires_grad_(True);output=critic(x)
    derivative=torch.autograd.grad(output.sum(),x,create_graph=True)[0]
    field=values[0].reshape(model.nu,model.nx)
    refu,refy=np.gradient(optimal[0].reshape(model.nu,model.nx),model.us,model.ys,edge_order=2)
    grad=derivative.detach().numpy().reshape(model.nu,model.nx,2)
    interior=(slice(2,-2),slice(2,-2))
    name=f'ndu_{method}_s{seed}_{model.nu}x{model.nx}_n{model.steps}_k{model.cost:g}_{model.action_name}'
    result=dict(model_id=name,method=method,seed=seed,width=width,depth=2,model=model_spec(model),seconds=seconds,reference_seconds=refsec,
      failure=failure,value_error_max=float(np.max(abs(values-optimal))),policy_regret_max=float(np.max(optimal-pv)),
      heldout_value_error_max=float(np.max(abs(pred-truth))),heldout_value_error_rms=float(np.sqrt(np.mean((pred-truth)**2))),
      heldout_scope='midpoints versus the finite-reference interpolant at t=0',
      gradient_u_error_max=float(np.max(abs(grad[:,:,0][interior]-refu[interior]))),
      gradient_logwealth_error_max=float(np.max(abs(grad[:,:,1][interior]-refy[interior]))),
      certificate=cert,peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      diagnostic_target=dict(value_error=.2,policy_regret=.1),
      diagnostic_pass=bool(np.max(abs(values-optimal))<=.2 and np.max(optimal-pv)<=.1),history=history)
    if np.max(abs(values-pv))>cert['policy_value_error_upper']+1e-8 or np.max(optimal-pv)>cert['policy_regret_upper']+1e-8:raise AssertionError('certificate violation')
    np.savez_compressed(OUT/f'{name}.npz',u=model.us,logwealth=model.ys,actions=model.actions,values=values,policy_indices=policies,policy_values=pv,reference_values=optimal,reference_policy=reference_policy,heldout_states=held,heldout_values=pred,heldout_reference=truth)
    torch.save(models,OUT/f'{name}_weights.pt');(OUT/f'{name}.json').write_text(json.dumps(result,indent=2))
    return result

def sensitivity():
    records=[]
    configs=[(17,25,20,actions,wealth) for actions,wealth in [('r2',(.5,2.)),('adjustment',(.5,2.)),('expanded',(.5,2.)),('refined',(.5,2.)),('expanded_domain',(.5,2.)),('expanded',(.25,4.))]]
    configs += [(25,37,40,'expanded',(.5,2.)),(33,49,80,'expanded',(.5,2.))]
    for nu,nx,steps,actions,wealth in configs:
        for cost in [1.,5.]:
            m=NDU(nu,nx,steps,cost,actions,wealth);v,a,seconds=m.reference();selected=m.actions[a[:,~m.boundary]]
            lo=m.actions.min(axis=0);hi=m.actions.max(axis=0);ci=(nu//2)*nx+nx//2
            result=model_spec(m)|dict(center_value=float(v[0,ci]),center_action=m.actions[a[0,ci]].tolist(),seconds=seconds,
               action_lower_frequency=np.mean(np.isclose(selected,lo),axis=(0,1)).tolist(),
               action_upper_frequency=np.mean(np.isclose(selected,hi),axis=(0,1)).tolist())
            label=f'ndu_reference_{nu}x{nx}_n{steps}_k{cost:g}_{actions}_x{wealth[0]:g}-{wealth[1]:g}'
            np.savez_compressed(OUT/f'{label}.npz',u=m.us,logwealth=m.ys,values=v,policy_indices=a,actions=m.actions)
            records.append(result);print(json.dumps(result),flush=True)
            (OUT/'ndu_sensitivity.json').write_text(json.dumps(records,indent=2))
    return records

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--suite',choices=['primary','sensitivity','smoke'],default='primary');args=parser.parse_args();OUT.mkdir(exist_ok=True,parents=True)
    if args.suite=='sensitivity':sensitivity();return
    records=[];seeds=[11] if args.suite=='smoke' else [11,29,47]
    for method in ['nbo','direct']:
        for seed in seeds:
            model=NDU(13,17,10) if args.suite=='smoke' else NDU()
            record=train(model,seed,method,critic_steps=100,actor_steps=60);records.append(record)
            print(json.dumps({k:v for k,v in record.items() if k not in ['certificate','history']}),flush=True)
            (OUT/f'ndu_{args.suite}.json').write_text(json.dumps(records,indent=2))
if __name__=='__main__':main()
