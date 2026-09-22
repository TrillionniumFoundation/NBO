"""Fresh direct time-control transcription on the unchanged original economy.
SLSQP proposals, closed-normal dual fitting, then the independent certificates.
This is a non-neural comparator and a policy-richness audit, not two classical
PDE baselines and not evidence that the tanh NBO architecture has converged.
"""
from pathlib import Path
import argparse,json,time,resource
import numpy as np
import torch
from scipy.optimize import minimize,minimize_scalar
from numpy.polynomial.legendre import leggauss
from numpy.polynomial.hermite import hermgauss
from closed_normal import moments
from independent_primal import evaluate
from independent_dual import run

def generate_policy(n,k):
    start=time.perf_counter();torch.set_num_threads(1);torch.set_default_dtype(torch.float64)
    tg,tw=leggauss(16);zg,zw=hermgauss(40);t=(np.arange(n)[:,None]+(tg+1)/2)/n
    TT=torch.tensor(t);W=torch.tensor(tw/(2*n));ZZ=torch.tensor(zg);ZW=torch.tensor(zw/np.sqrt(np.pi))
    edges=np.arange(n+1)/n;dw=(np.exp(-.02*edges[:-1])-np.exp(-.02*edges[1:]))/.02
    budget=1.25-.5*np.exp(-.02)-1e-7
    x0=np.r_[np.full(n,budget/dw.sum()),np.full(n,.05)];history=[];calls=0
    def fun(a):
        nonlocal calls
        calls+=1;a=torch.tensor(a,requires_grad=True);c=a[:n];theta=a[n:]
        mu=2+(torch.cumsum(theta,0)-theta)[:,None]/n+theta[:,None]*(TT-torch.tensor(edges[:-1,None]))
        u=mu[:,:,None]+.05*torch.sqrt(2*TT)[:,:,None]*ZZ
        running=(-torch.exp((u-1)*(-torch.log(c[:,None,None])))/(u-1)*ZW).sum(-1)-k/2*theta[:,None]**2
        xt=torch.exp(torch.tensor(.02))*(1.25-(c*torch.tensor(dw)).sum())
        val=(torch.exp(-.04*TT)*running*W).sum()+np.exp(-.04)*(-.02*((theta.sum()/n)**2+.0025)+.1*torch.log(xt))
        loss=-val;g=torch.autograd.grad(loss,a)[0];return float(loss.detach()),g.detach().numpy()
    con={'type':'ineq','fun':lambda a:budget-dw@a[:n],'jac':lambda a:np.r_[-dw,np.zeros(n)]}
    opt=minimize(fun,x0,jac=True,method='SLSQP',bounds=[(.7,np.nextafter(.8,-np.inf))]*n+[(0,np.nextafter(.2,-np.inf))]*n,
       constraints=[con],options={'ftol':1e-12,'maxiter':1000})
    c=np.clip(opt.x[:n],.7,np.nextafter(.8,-np.inf));theta=np.clip(opt.x[n:],0,np.nextafter(.2,-np.inf))
    # Guard the finite optimizer's budget, rather than accepting its feasibility flag.
    overshoot=max(0,float(dw@c-budget));c=c-(overshoot+1e-13)/dw.sum()
    return {'k':k,'slabs':n,'c':c.tolist(),'theta':theta.tolist(),'p':[0.]*n,'initial':[0,2,1.25],
       'algorithm':'fresh SLSQP direct time-control transcription','initialization':'constant consumption and theta=.05; no inherited policy',
       'optimizer_success':bool(opt.success),'optimizer_message':str(opt.message),'iterations':int(opt.nit),'objective_calls':calls,
       'training_value':-float(opt.fun),'seconds':time.perf_counter()-start,'training_scope':'non-neural proposal objective only; independent stopped certificate follows'}

def generate_dual(k,n=16):
    start=time.perf_counter();tg,tw=leggauss(16);t=((np.arange(n)[:,None]+(tg+1)/2)/n).ravel();w=np.tile(tw/(2*n),n)*np.exp(-.04*t)
    A=np.maximum(0,np.minimum(t[:,None]-np.arange(n)[None,:]/n,1/n));mass=w.reshape(n,-1).sum(1)
    attempts=[]
    def solve(y,full=False):
        def objective(th):
            m=2+A@th;s,b,_=moments(t,m,y)
            val=w@s-k/2*np.dot(mass,th*th)-.02*np.exp(-.04)*(th.sum()/n)**2
            grad=A.T@(w*b)-k*mass*th-.04*np.exp(-.04)*(th.sum()/n)/n
            return -val,-grad
        opt=minimize(objective,np.full(n,.05),jac=True,method='L-BFGS-B',bounds=[(0,np.nextafter(.2,-np.inf))]*n,
                    options={'ftol':1e-14,'gtol':1e-10,'maxiter':400})
        th=np.clip(opt.x,0,np.nextafter(.2,-np.inf));s,b,bl=moments(t,2+A@th,y);cov=np.dot(w*.00375*t,bl)
        value=.75*y+.1*np.log(.5)-opt.fun+cov
        attempts.append({'y0':float(y),'iterations':int(opt.nit),'success':bool(opt.success),'pilot_value':float(value)})
        return {'k':k,'y0':float(y),'theta':th.tolist(),'objective_pilot':float(value),'covariance_pilot':float(cov),
          'algorithm':'fresh closed-normal saddle pilot; fixed deterministic starts; certification independent','inner_success':bool(opt.success)} if full else float(value)
    opt=minimize_scalar(solve,bounds=(1.2,2.4),method='bounded',options={'xatol':1e-9});d=solve(opt.x,True);d.update({'seconds':time.perf_counter()-start,'outer_success':bool(opt.success),'fitting_attempts':attempts})
    return d

def main(out,ks,slabs):
    start=time.perf_counter();out.mkdir(parents=True,exist_ok=False);rows=[]
    for k in ks:
        for n in slabs:
            clock=time.perf_counter();prefix=f'k{k:g}_n{n}';a=generate_policy(n,k);ap=out/f'actor_{prefix}.json';ap.write_text(json.dumps(a,indent=2)+'\n')
            d=generate_dual(k);dp=out/f'dual_pilot_{prefix}.json';dp.write_text(json.dumps(d,indent=2)+'\n')
            p=evaluate(ap,str(k));u=run(dp,str(k),32,512)
            (out/f'primal_{prefix}.json').write_text(json.dumps(p,indent=2)+'\n');(out/f'dual_{prefix}.json').write_text(json.dumps(u,indent=2)+'\n')
            row={'k':k,'policy_slabs':n,'policy_generation_seconds':a['seconds'],'dual_fitting_seconds':d['seconds'],
               'primal_verification_seconds':p['seconds'],'dual_verification_seconds':u['seconds'],'total_case_seconds':time.perf_counter()-clock,
               'L':p['value_interval'][0],'U':u['optimal_value_upper'],'regret_upper':float(np.nextafter(u['optimal_value_upper']-p['value_interval'][0],np.inf)),
               'target_passes':{str(target):u['optimal_value_upper']-p['value_interval'][0]<target for target in [.01,.005,.0025,.001]},
               'optimizer_success':a['optimizer_success'],'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'scope':'All generation and certification newly executed; finite deterministic time-control class; no neural or global convergence claim'}
            rows.append(row);(out/'frontier.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
    (out/'resource_ledger.json').write_text(json.dumps({'wall_seconds':time.perf_counter()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
       'fresh_candidates':len(rows),'scope':'Fresh non-neural baseline pipeline; all scalar fitting attempts retained; imports separately shell-timed'},indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--ks',nargs='+',type=float,default=[2]);p.add_argument('--slabs',nargs='+',type=int,default=[16,32,64]);a=p.parse_args();main(a.out,a.ks,a.slabs)
