"""Nonlinear heterogeneous multi-product control with full-state neural plans.
Unknown value; no Riccati labels. Exact-real correction has a state-uniform
convexity certificate. Stored floating-point plans are independently checked
with MPFR KKT residuals at each retained initial state.
"""
from pathlib import Path
from fractions import Fraction as F
import sys,json,time,resource,hashlib,argparse,platform
import numpy as np
import torch
from torch import nn
from scipy.optimize import minimize
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r16/replication'))
import mpfr_interval as M
I,Q=M.I,M.I.rational
H=12;STEP=16/209;MASS=4.;L=177/8;RATIO=145/209

def constants(d):
    q=1+np.arange(d)/(5*(d-1));b=((np.arange(H)[:,None]+np.arange(d))%7-3)/100
    return q,b

def torch_cost(x,u):
    d=x.shape[-1];q,b=constants(d);q=torch.tensor(q);b=torch.tensor(b);z=x;cost=torch.zeros(x.shape[:-1])
    for h in range(H):
        z=.6*z+u[...,h,:]-b[h]
        lc=lambda a:torch.logaddexp(a,-a)-np.log(2.)
        cost=cost+2*u[...,h,:].square().sum(-1)+(q*z.square()/2+.5*lc(z)+.3*lc(z-torch.roll(z,-1,-1))).sum(-1)
    return cost

def cost_gradient(x,u):
    d=len(x);q,b=constants(d);z=np.array(x);zs=[];cost=0.
    lc=lambda a:np.logaddexp(a,-a)-np.log(2.)
    for h in range(H):
        z=.6*z+u[h]-b[h];zs.append(z);cost+=2*np.sum(u[h]**2)+np.sum(q*z*z/2+.5*lc(z)+.3*lc(z-np.roll(z,-1)))
    adj=np.zeros(d);grad=np.empty_like(u)
    for h in reversed(range(H)):
        z=zs[h];diff=np.tanh(z-np.roll(z,-1));g=q*z+.5*np.tanh(z)+.3*(diff-np.roll(diff,1));adj=g+.6*adj;grad[h]=4*u[h]+adj
    return float(cost),grad

def rational_array(a):
    a=np.asarray(a,dtype=object);lo=np.empty(a.shape);hi=np.empty(a.shape)
    for ix in np.ndindex(a.shape):v=Q(a[ix]);lo[ix]=v.lo;hi[ix]=v.hi
    return I(lo,hi)

def directed_check(x,u):
    start=time.perf_counter();d=len(x);q=rational_array([1+F(i,5*(d-1)) for i in range(d)]);b=rational_array([[F((h+i)%7-3,100) for i in range(d)] for h in range(H)])
    z=I(x);uu=I(u);zs=[];cost=I(0)
    def roll(z,k):return I(np.roll(z.lo,k),np.roll(z.hi,k))
    def lc(z):return M.log((M.exp(z)+M.exp(-z))/2)
    for h in range(H):
        z=Q('.6')*z+uu[h]-b[h];zs.append(z)
        value=2*uu[h].square()+q*z.square()/2+Q('.5')*lc(z)+Q('.3')*lc(z-roll(z,-1))
        cost=cost+M.add_reduce(value)
    adj=I(np.zeros(d));gs=[]
    for h in reversed(range(H)):
        z=zs[h];diff=M.tanh(z-roll(z,-1));g=q*z+Q('.5')*M.tanh(z)+Q('.3')*(diff-roll(diff,1));adj=g+Q('.6')*adj;gs.append(4*uu[h]+adj)
    grad=M.stack(list(reversed(gs)));norm2=M.add_reduce(M.add_reduce(I(grad.maxabs()).square(),axis=0),axis=0);gap=norm2/8
    denom=I(float(cost.lo))-gap
    return {'status':'DIRECTED_CONVEX_POLICY_CERTIFICATE','objective_interval':cost.pair(),'gradient_norm_squared_upper':float(norm2.hi),'total_cost_loss_upper':float(gap.hi),'relative_excess_cost_upper':float((gap/denom).hi) if denom.lo>0 else None,'per_coordinate_loss_upper':float((gap/d).hi),'verification_seconds':time.perf_counter()-start,'scope':'This exact stored plan at this exact stored initial vector; no optimizer output is treated as the true value','arithmetic':f'MPFR {M.VERSION}, 128-bit directed endpoints; exact rational model constants'}

class PlanNet(nn.Module):
    def __init__(self,d,width):
        super().__init__();self.d=d;self.layers=nn.Sequential(nn.Linear(d,width),nn.Tanh(),nn.Linear(width,width),nn.Tanh(),nn.Linear(width,H*d))
    def forward(self,x):return .25*torch.tanh(self.layers(x)).reshape(*x.shape[:-1],H,self.d)

def serialize(net):return [{'weight':m.weight.detach().tolist(),'bias':m.bias.detach().tolist()} for m in net.layers if isinstance(m,nn.Linear)]

def uniform_bound(d,k,amplitude=F(1,4)):
    a=Q(amplitude);state=1+(a+Q('.03'))/(1-Q('.6'));g0=4*a+(Q('1.2')*state+Q('.5')+2*Q('.3'))/(1-Q('.6'));r=Q(F(145,209));loss=H*d*g0.square()/8*(r**(2*k))
    return {'d':d,'H':H,'corrections':k,'initial_gradient_coordinate_bound':float(g0.hi),'total_cost_loss_upper':float(loss.hi),'per_coordinate_loss_upper':float((loss/d).hi),'scope':'Every initial x in [-1,1]^d; exact-real neural map and exact rational-step correction; no tensor state cover','amplitude_rational':str(amplitude),'relative_cost_scope':'Absolute total loss is state-uniform; a relative percentage requires a positive value lower bound at the state'}

def experiment(d,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);torch.set_num_threads(1);torch.set_default_dtype(torch.float64);torch.use_deterministic_algorithms(True);records=[]
    xalt=np.array([1. if i%2==0 else -1. for i in range(d)]);xr=np.random.default_rng(17499+d).uniform(-1,1,d);queries={'alternating':xalt,'uniform':xr}
    (out/'initial_states.json').write_text(json.dumps({k:v.tolist() for k,v in queries.items()},indent=2)+'\n')
    bounds=[uniform_bound(d,k) for k in [0,8,16,24,32]]
    (out/'uniform_certificates.json').write_text(json.dumps(bounds,indent=2)+'\n')
    for seed in [17400,17401,17402]:
        torch.manual_seed(seed);width=min(64,2*d);net=PlanNet(d,width).double();opt=torch.optim.Adam(net.parameters(),lr=.003);clock=time.perf_counter();hist=[]
        for step in range(1,401):
            x=2*torch.rand(32,d)-1;u=net(x);loss=torch_cost(x,u).mean()/d
            if not torch.isfinite(loss):raise ArithmeticError('Nonfinite nonlinear cost')
            opt.zero_grad();loss.backward();opt.step()
            if step%100==0:hist.append({'step':step,'sample_cost_per_coordinate':float(loss.detach())})
        training=time.perf_counter()-clock;payload={'d':d,'H':H,'seed':seed,'width':width,'steps':400,'layers':serialize(net),'bounded_output':'.25*tanh','training_seconds':training,'training_history':hist,'supervised_solution_labels':False,'input':'full d-dimensional state'}
        pf=out/f'network_s{seed}.json';pf.write_text(json.dumps(payload,indent=2)+'\n')
        for tag,x in queries.items():
            tick=time.perf_counter()
            with torch.no_grad():u=net(torch.tensor(x)).numpy()
            online=time.perf_counter()-tick
            for k in range(33):
                if k in [0,8,16,24,32]:
                    cp=out/f'plan_neural_s{seed}_{tag}_k{k}.json';cp.write_text(json.dumps({'x':x.tolist(),'u':u.tolist()},indent=2)+'\n');r=directed_check(x,u);r.update({'method':'neural_plus_gradient','seed':seed,'d':d,'query':tag,'corrections':k,'online_seconds':online,'training_seconds':training,'plan_sha256':hashlib.sha256(cp.read_bytes()).hexdigest()});records.append(r)
                if k<32:
                    tick=time.perf_counter();_,g=cost_gradient(x,u);u=u-STEP*g;online+=time.perf_counter()-tick
        print(json.dumps({'d':d,'seed':seed,'training_seconds':training,'uniform_final_total':bounds[-1]['total_cost_loss_upper']}),flush=True)
    for method in ['zero_gradient','accelerated_gradient','L-BFGS']:
      for tag,x in queries.items():
        u=np.zeros((H,d));online=0.
        if method=='L-BFGS':
            tick=time.perf_counter();r=minimize(lambda a:(lambda fg:(fg[0],fg[1].ravel()))(cost_gradient(x,a.reshape(H,d))),u.ravel(),jac=True,method='L-BFGS-B',options={'maxiter':400,'ftol':1e-15,'gtol':1e-10,'maxls':30});u=r.x.reshape(H,d);online=time.perf_counter()-tick;check=directed_check(x,u);check.update({'method':method,'d':d,'query':tag,'corrections':int(r.nit),'online_seconds':online,'success':bool(r.success)});records.append(check);cp=out/f'plan_{method}_{tag}.json';cp.write_text(json.dumps({'x':x.tolist(),'u':u.tolist()},indent=2)+'\n')
        else:
            y=u.copy();momentum=(np.sqrt(L)-np.sqrt(MASS))/(np.sqrt(L)+np.sqrt(MASS))
            for k in range(33):
                if k in [0,8,16,24,32]:
                    cp=out/f'plan_{method}_{tag}_k{k}.json';cp.write_text(json.dumps({'x':x.tolist(),'u':u.tolist()},indent=2)+'\n');check=directed_check(x,u);check.update({'method':method,'d':d,'query':tag,'corrections':k,'online_seconds':online,'training_seconds':0.,'plan_sha256':hashlib.sha256(cp.read_bytes()).hexdigest()});records.append(check)
                if k<32:
                    tick=time.perf_counter()
                    if method=='zero_gradient':_,g=cost_gradient(x,u);u=u-STEP*g
                    else:
                        _,g=cost_gradient(x,y);un=y-g/L;y=un+momentum*(un-u);u=un
                    online+=time.perf_counter()-tick
    (out/'records.json').write_text(json.dumps(records,indent=2)+'\n');(out/'resources.json').write_text(json.dumps({'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'platform':platform.platform(),'torch':torch.__version__,'torch_threads':1,'seed_count':3,'test_query_count':2,'uniform_state_certificate_separate':True},indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--d',type=int,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();experiment(a.d,a.out)
