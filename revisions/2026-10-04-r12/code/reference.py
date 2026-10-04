"""Independent one-state monotone implicit HJB reference for the same family.
No neural critic enters the reference. Domain/grid changes are diagnostics,
not uniform continuous-time error certificates.
"""
from __future__ import annotations
import math,time
from pathlib import Path
from scipy.linalg import solve_banded
from scipy.integrate import cumulative_trapezoid
from common import *

def root(p):
    p=np.asarray(p);s=np.sqrt(p*p+4*P['adjustment'])
    return np.where(p>=0,2/(p+s),(s-p)/(2*P['adjustment']))

def best_action(v,y):
    dx=y[1]-y[0];pf=np.diff(v)[1:]/dx;pb=np.diff(v)[:-1]/dx
    d0=P['productivity']-(P['idiosyncratic_sigma']**2+P['common_sigma']**2)/2+P['coupling']*np.tanh(float(old.coupling(1)[0,0])*y[1:-1])
    lo=P['lower'];hi=P['upper']
    a=np.clip(root(pf),lo,np.maximum(lo,np.minimum(hi,d0)))
    b=np.clip(root(pb),np.minimum(hi,np.maximum(lo,d0)),hi)
    def H(m):
        mu=d0-m
        return np.log(m)-P['adjustment']*m*m/2+np.maximum(mu,0)*pf+np.minimum(mu,0)*pb
    ha=H(a);hb=H(b);ha=np.where(d0>=lo,ha,-np.inf);hb=np.where(d0<=hi,hb,-np.inf)
    return np.where(ha>=hb,a,b)

def implicit(vnext,y,m,h,boundaries):
    dx=y[1]-y[0];yi=y[1:-1]
    c=P['productivity']-(P['idiosyncratic_sigma']**2+P['common_sigma']**2)/2
    mu=c+P['coupling']*np.tanh(float(old.coupling(1)[0,0])*yi)-m
    diffusion=(P['idiosyncratic_sigma']**2+P['common_sigma']**2)/2
    low=diffusion/dx**2+np.maximum(-mu,0)/dx;high=diffusion/dx**2+np.maximum(mu,0)/dx
    band=np.zeros((3,len(yi)));band[1]=1/h+P['discount']+low+high;band[0,1:]=-high[:-1];band[2,:-1]=-low[1:]
    rhs=vnext[1:-1]/h+np.log(m)+yi-P['adjustment']*m*m/2
    rhs[0]+=low[0]*boundaries[0];rhs[-1]+=high[-1]*boundaries[1]
    vint=solve_banded((1,1),band,rhs,check_finite=True)
    v=np.r_[boundaries[0],vint,boundaries[1]]
    residual=(1/h+P['discount'])*vint-low*(v[:-2]-vint)-high*(v[2:]-vint)-rhs
    # rhs includes the boundary contributions; compute the original equation.
    original=(vint-vnext[1:-1])/h+P['discount']*vint-low*(v[:-2]-vint)-high*(v[2:]-vint)-(np.log(m)+yi-P['adjustment']*m*m/2)
    return v,float(np.max(abs(original)))

def boundaries(grid,L):
    rho=P['discount'];fine=np.linspace(0,P['T'],max(8193,8*len(grid)+1))
    w=-np.expm1(-rho*(P['T']-fine))/rho+np.exp(-rho*(P['T']-fine));m=2/(w+np.sqrt(w*w+4*P['adjustment']))
    c=P['productivity']-(P['idiosyncratic_sigma']**2+P['common_sigma']**2)/2;out=[]
    for sign,y in [(-1.,-L),(1.,L)]:
        fs=sign*float(old.coupling(1)[0,0])*P['coupling']
        q=np.exp(-rho*fine)*(np.log(m)-P['adjustment']*m*m/2+w*(c+fs-m))
        integral=cumulative_trapezoid(q,fine,initial=0);qback=np.exp(rho*fine)*(integral[-1]-integral)
        out.append(np.interp(grid,fine,w*y+qback))
    return out

def solve(nx,nt,L,policies,out):
    start=time.perf_counter();y=np.linspace(-L,L,nx);grid=np.linspace(0,P['T'],nt+1);h=P['T']/nt;bd=boundaries(grid,L)
    values={'optimal':y.copy(),**{name:y.copy() for name in policies}}
    initial={};residual=0.;iterations=0;converged=True;stored_policy=None
    for k in range(nt-1,-1,-1):
        b=(bd[0][k],bd[1][k]);vn=values['optimal'];v=vn.copy()
        for it in range(100):
            m=best_action(v,y);new,res=implicit(vn,y,m,h,b);iterations+=1
            gap=float(np.max(abs(new-v)));v=new
            if gap<1e-11:break
        else:converged=False
        m=best_action(v,y);check,res=implicit(vn,y,m,h,b);residual=max(residual,float(np.max(abs(check-v)))/h,res)
        values['optimal']=v
        for name,actor in policies.items():
            with torch.no_grad():m=actor(torch.from_numpy(np.c_[np.full(nx-2,grid[k]),y[1:-1]])).numpy().ravel()
            m=np.clip(m,P['lower'],P['upper']);vv,res=implicit(values[name],y,m,h,b);values[name]=vv;residual=max(residual,res)
        if k==0:stored_policy=best_action(v,y)
    ident=f'fd_nx{nx}_nt{nt}_L{L:g}';np.savez_compressed(Path(out)/(ident+'.npz'),state=y,optimal_action_t0=stored_policy,**values)
    center=nx//2
    row=dict(id=ident,nx=nx,nt=nt,L=L,center_values={k:float(v[center]) for k,v in values.items()},center_policy_losses={k:float(values['optimal'][center]-v[center]) for k,v in values.items() if k!='optimal'},max_equation_residual=residual,policy_iterations=iterations,converged=converged,seconds=time.perf_counter()-start,raw_sha256=digest(Path(out)/(ident+'.npz')),scope='independent monotone implicit finite-state and time approximation with declared asymptotic boundary data; actor evaluated as a Markov feedback on this grid; grid/domain sensitivity is not a continuous-time certificate')
    write(Path(out)/(ident+'.json'),row);print(ident,row['center_policy_losses'],flush=True);return row

def run(out,smoke=False):
    import training
    out=Path(out);out.mkdir(parents=True,exist_ok=True);actors={};fits=[]
    for method in ['nbo','dpo','linear']:
        r=training.train(1,PROTOCOL['auxiliary_seed'],method,out,seconds=.5 if smoke else PROTOCOL['fit_wall_seconds']);fits.append(r)
        if r.get('weights_sha256'):actors[method]=old.load(out/(r['id']+'.pt'))[0]
    class Anchor(torch.nn.Module):
        def forward(self,x):return old.schedule(x[:,:1])
    actors['anchor']=Anchor()
    grids=[(101,32,6.)] if smoke else [(401,256,6.),(801,512,6.),(1601,1024,6.),(1601,1024,8.)]
    rows=[solve(*g,actors,out) for g in grids]
    result=dict(records=rows,fits=fits,source_commit=source(),absolute_accuracy_scope='finite-grid policy loss and independent grid/domain stability; no substitution for a certified multidimensional optimum')
    write(out/'REFERENCE.json',result);return result
