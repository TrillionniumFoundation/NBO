"""Coupled investment: convex squared-ReLU training and continuous-law certification.

No frozen neural objects or conventional labels enter the neural algorithm.
Uniform innovations are integrated analytically. Floating proposals are certified
by an outward primal-dual bound, not by trusting an optimizer success flag.
"""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import sys,time,json,hashlib,math
import numpy as np
R=Path(__file__).resolve().parents[1]; OLD=R.parent/'2026-10-07-r41'
sys.path.insert(0,str(OLD/'vendor/r38/code'))
from nonlinear import I,encode
BETA=15/16; CAP=1/8; SHOCK=1/32; SEEDS=(104729,130363,155921)
TARGETS=(.25,.10); LADDER=(16,32,64,128)

def grid(N):
    a=np.linspace(0,1,N+1);return np.stack(np.meshgrid(a,a,indexing='ij'),axis=-1).reshape(-1,2)
def terminal(x):
    return 2*((x-.6875)**2).sum(-1)+2*np.maximum(.5-x.sum(-1),0)**2+.25*(x[...,0]-x[...,1])**4
def stage(x,a,P):
    return ((x-.6875)**2).sum(-1)+2*np.maximum(.5-x.sum(-1),0)**2+.25*(x[...,0]-x[...,1])**4+P*(a*a).sum(-1)+.5*a[...,0]*a[...,1]+4*(a**4).sum(-1)
def base(x,a):return .125+.5*x+.125*x[...,::-1]+.0625*x*(1-x[...,::-1])+a

def params(net):return (np.asarray(net[k],dtype=float) for k in ('w','b','c','linear','intercept'))
def values(net,x):
    w,b,c,l,d=params(net);return d+x@l+np.maximum(x@w.T+b,0)**2@c

def moment(p,u,v):
    """E[(p+u U+v V)_+^2], and its p derivative; U,V uniform[-1,1]."""
    u=np.broadcast_to(np.asarray(u),p.shape);v=np.broadcast_to(np.asarray(v),p.shape)
    radius=u+v;full=p>=radius;zero=p<=-radius
    m=np.zeros_like(p);g=np.zeros_like(p)
    m[full]=p[full]**2+(u[full]**2+v[full]**2)/3;g[full]=2*p[full]
    mixed=~(full|zero);two=mixed&(u*v>0);one=mixed&~two
    if np.any(two):
        pp,uu,vv=p[two],u[two],v[two]
        zs=[np.maximum(pp+uu+vv,0),np.maximum(pp+uu-vv,0),np.maximum(pp-uu+vv,0),np.maximum(pp-uu-vv,0)]
        m[two]=(zs[0]**4-zs[1]**4-zs[2]**4+zs[3]**4)/(48*uu*vv)
        g[two]=(zs[0]**3-zs[1]**3-zs[2]**3+zs[3]**3)/(12*uu*vv)
    if np.any(one):
        pp=p[one];rr=radius[one];plus=np.maximum(pp+rr,0);minus=np.maximum(pp-rr,0)
        m[one]=(plus**3-minus**3)/(6*rr);g[one]=(plus**2-minus**2)/(2*rr)
    return m,g

def expect(net,z,gradient=False):
    w,b,c,l,d=params(net);p=z@w.T+b;m,g=moment(p,SHOCK*abs(w[:,0]),SHOCK*abs(w[:,1]))
    val=d+z@l+m@c
    return (val,l+(g*c)@w) if gradient else val

def constants(net,P):
    w,b,c,l,d=params(net)
    if np.any(c<0):raise ValueError('Convexity lost')
    if any(not np.isfinite(a).all() for a in (w,b,c,l,d)):raise ValueError('Nonfinite network')
    if any(np.any(abs(a)>2.**100) for a in (w,b,c,l,d)):raise ValueError('Network outside arithmetic contract')
    if np.any((abs(w)>0)&(abs(w)<2.**-100)):raise ValueError('Innovation moment denominator outside contract')
    # Interval row-sum norm bounds the PSD global Hessian envelope.
    H=[[I.point(0.) for j in range(2)] for i in range(2)]
    sg=[I.point(l[i]) for i in range(2)]
    for wi,bi,ci in zip(w,b,c):
        zz=I.point(bi)
        for j in range(2):zz=zz+I(0.,1.)*wi[j]
        zz=I(np.maximum(0,zz.lo),np.maximum(0,zz.hi))
        for i in range(2):
            sg[i]=sg[i]+2*ci*zz*wi[i]
            for j in range(2):H[i][j]=H[i][j]+2*I.point(ci)*wi[i]*wi[j]
    rows=[]
    for i in range(2):
        r=I.point(0.)
        for j in range(2):r=r+float(max(abs(H[i][j].lo),abs(H[i][j].hi)))
        rows.append(float(r.hi))
    M=max(rows); S=float((I.point(max(abs(sg[0].lo),abs(sg[0].hi)))+max(abs(sg[1].lo),abs(sg[1].hi))).hi)
    mu=2*P-.5
    Lxx=(I.point(16)+BETA*(I.point(M)*(11/16)**2+S/16)).hi.item()
    Lxa=(I.point(BETA)*M*(11/16)).hi.item()
    env=(I.point(Lxx)+I.point(Lxa).square()/mu).hi.item()
    Laa=(I.point(2*P+1.25)+BETA*M).hi.item()
    return dict(M=M,S=S,mu=mu,Lxx=Lxx,Lxa=Lxa,envelope_gradient_lipschitz=env,Laa=Laa)

def project(a):
    b=np.maximum(a,0);s=b.sum(1);idx=s>CAP
    if np.any(idx):
        z=a[idx]; hi=np.max(z,axis=1);lo=np.min(z,axis=1)
        t=np.where(hi-lo>=CAP,hi-CAP,(hi+lo-CAP)/2)
        b[idx]=np.maximum(z-t[:,None],0)
    return b

def optimize(net,x,P,steps=160):
    C=constants(net,P); L=C['Laa']; a=np.zeros_like(x); y=a.copy();t=1.
    for _ in range(steps):
        z=base(x,y);vv,g=expect(net,z,True)
        grad=2*P*y+.5*y[:,::-1]+16*y**3+BETA*g
        b=project(y-grad/L); tt=(1+math.sqrt(1+4*t*t))/2
        y=b+((t-1)/tt)*(b-a);a=b;t=tt
    # Every returned coordinate is an exact dyadic and feasibility is checked.
    a=np.floor(np.maximum(a,0)*2**24)/2**24
    over=a.sum(1)>CAP
    if np.any(over):a[over,1]=np.maximum(0,CAP-a[over,0])
    if np.any(a<0) or np.any(a.sum(1)>CAP):raise ArithmeticError('Infeasible actor')
    return a,stage(x,a,P)+BETA*expect(net,base(x,a))

def quadratic_fit(x,y):
    D=np.column_stack((np.ones(len(x)),x,x[:,0]**2,x[:,0]*x[:,1],x[:,1]**2))
    co=np.linalg.lstsq(D,y,rcond=1e-12)[0]
    H=np.array([[co[3],co[4]/2],[co[4]/2,co[5]]]);ev,U=np.linalg.eigh(H);ev=np.maximum(ev,0)
    W=(U*np.sqrt(ev)).T;w=np.concatenate((W,-W),axis=0);b=np.zeros(4);c=np.ones(4)
    q=(x@W.T)**2;lin=np.linalg.lstsq(D[:,:3],y-q.sum(1),rcond=1e-12)[0]
    return dict(w=w.tolist(),b=b.tolist(),c=c.tolist(),linear=lin[1:].tolist(),intercept=float(lin[0]),width=4,optimizer_steps=0,hidden_weight_change=0.,projection_coefficients=6)

def initial_dictionary(seed,width):
    rng=np.random.default_rng(seed)
    ww=[[1.,0.],[0.,1.],[-1.,-1.],[1.,-1.],[-1.,1.]];bb=[0.,0.,.5,0.,0.]
    for k in (np.arange(8)+.5)/8:
        ww.extend([[1.,-1.],[-1.,1.]]);bb.extend([-k,-k])
    while len(ww)<width:
        j=len(ww);direction=np.array([[1.,0.],[0.,1.],[-1.,-1.],[1.,1.],[1.,-1.],[-1.,1.]])[j%6]
        direction=direction+rng.normal(0,.035,2)
        low=np.minimum(direction,0).sum();high=np.maximum(direction,0).sum()
        ww.append(direction.tolist());bb.append(-rng.uniform(low,high))
    return np.asarray(ww),np.asarray(bb)

def projection_fit(x,y,seed,width=96,prune=False):
    from scipy.optimize import nnls
    w,b=initial_dictionary(seed,width)
    D=np.maximum(x@w.T+b,0)**2
    A=np.column_stack((np.ones(len(x)),x));proj=np.linalg.lstsq(A,D,rcond=1e-12)[0]
    yp=y-A@np.linalg.lstsq(A,y,rcond=1e-12)[0]
    c=nnls(D-A@proj,yp,maxiter=10000)[0]
    ll=np.linalg.lstsq(A,y-D@c,rcond=1e-12)[0];d=ll[0];l=ll[1:]
    active=np.flatnonzero(c>0) if prune else np.arange(len(c))
    w,b,c=w[active],b[active],c[active]
    out=dict(dictionary_width=width,active_indices=active.tolist(),w=w.tolist(),b=b.tolist(),c=c.tolist(),linear=l.tolist(),intercept=float(d),width=len(c),optimizer_steps=0,hidden_weight_change=0.,projection_coefficients=width+3,nnls_calls=1,least_squares_calls=3,training_points=len(x),dictionary_seed=seed)
    out['training_max_error']=float(np.max(abs(values(out,x)-y)))
    return out

def inverse_softplus(c):
    """log(exp(c)-1) without overflowing exp(c), for finite positive c."""
    c=np.asarray(c,dtype=float)
    if not np.isfinite(c).all() or np.any(c<=0):raise ValueError('Positive finite coefficient required')
    return c+np.log(-np.expm1(-c))

def fit(x,y,seed,width=48,steps=300):
    import torch
    torch.set_num_threads(1);torch.manual_seed(seed);rng=np.random.default_rng(seed)
    from scipy.optimize import nnls
    # Nonnegative output fit on primitive-directed initial features; no DP teacher.
    init=projection_fit(x,y,seed,width)
    w,b,c,l,d=[np.asarray(init[k]) for k in ('w','b','c','linear','intercept')]
    c=np.maximum(c,1e-10)
    raw=inverse_softplus(c); pars=[torch.nn.Parameter(torch.tensor(z,dtype=torch.float64)) for z in (w,b,raw,l,d)]
    initial=[p.detach().clone() for p in pars];xt=torch.tensor(x,dtype=torch.float64);yt=torch.tensor(y,dtype=torch.float64)
    opt=torch.optim.LBFGS(pars,lr=.7,max_iter=steps,max_eval=steps*2,history_size=25,tolerance_grad=1e-10,tolerance_change=1e-13,line_search_fn='strong_wolfe')
    calls=0
    def closure():
        nonlocal calls
        calls+=1;opt.zero_grad();W,B,C,L,D=pars
        cc=torch.nn.functional.softplus(C)
        pred=D+xt@L+torch.relu(xt@W.T+B).square()@cc
        # Fixed curvature regularization, disclosed; certification uses the actual fit.
        reg=(cc*W.square().sum(1)).sum()
        loss=((pred-yt)**2).mean()+1e-10*reg.square();loss.backward();return loss
    opt.step(closure)
    w,b,raw,l,d=[p.detach().numpy().copy() for p in pars];c=np.logaddexp(0,raw)
    out=dict(w=w.tolist(),b=b.tolist(),c=c.tolist(),linear=l.tolist(),intercept=float(d),width=width,optimizer_steps=steps,closure_calls=calls,
        hidden_weight_change=max(float((pars[i]-initial[i]).detach().abs().max()) for i in (0,1)),seed=seed,
        feature_training_evaluations=(calls+1)*len(x)*width,training_points=len(x),nnls_calls=1,least_squares_calls=3)
    out['training_mse']=float(np.mean((values(out,x)-y)**2));out['training_max_error']=float(np.max(abs(values(out,x)-y)))
    return out

def isum(xs):
    out=I.point(0.)
    for x in xs:out=out+x
    return out

def relu(x):return I(np.maximum(x.lo,0),np.maximum(x.hi,0))
def power(x,n):
    if n==2:return x.square()
    if n==3:return x.square()*x
    if n==4:return x.square().square()
    raise ValueError(n)
def imoment(p,u,v):
    # u,v are nonnegative exact dyadics (shock scaling is a power of two).
    if u==0 and v==0:return relu(p).square(),2*relu(p)
    if u==0 or v==0:
        r=max(u,v); z=relu(p+r);s=relu(p-r)
        m=(power(z,3)-power(s,3))/(6*I.point(r));g=(z.square()-s.square())/(2*I.point(r))
    else:
        zs=[relu(p+u+v),relu(p+u-v),relu(p-u+v),relu(p-u-v)]
        den=I.point(u)*v
        m=(power(zs[0],4)-power(zs[1],4)-power(zs[2],4)+power(zs[3],4))/(48*den)
        g=(power(zs[0],3)-power(zs[1],3)-power(zs[2],3)+power(zs[3],3))/(12*den)
    radius=I.point(u)+v; full=p.lo>=radius.hi; zero=p.hi<=-radius.hi
    fm=p.square()+(I.point(u).square()+I.point(v).square())/3;fg=2*p
    return I(np.where(zero,0,np.where(full,fm.lo,m.lo)),np.where(zero,0,np.where(full,fm.hi,m.hi))),I(np.where(zero,0,np.where(full,fg.lo,g.lo)),np.where(zero,0,np.where(full,fg.hi,g.hi)))

def ivalue(net,x):
    w,b,c,l,d=params(net);out=I.point(d)+isum([x[j]*l[j] for j in range(2)])
    for wi,bi,ci in zip(w,b,c):out=out+ci*relu(I.point(bi)+isum([x[j]*wi[j] for j in range(2)])).square()
    return out

def iexpect(net,z):
    w,b,c,l,d=params(net);out=I.point(d)+isum([z[j]*l[j] for j in range(2)]);grad=[I.point(l[j]) for j in range(2)]
    for wi,bi,ci in zip(w,b,c):
        p=I.point(bi)+isum([z[j]*wi[j] for j in range(2)])
        m,g=imoment(p,SHOCK*abs(wi[0]),SHOCK*abs(wi[1]));out=out+ci*m
        for j in range(2):grad[j]=grad[j]+ci*wi[j]*g
    return out,grad

def istatecost(x,terminal=False):
    return (2 if terminal else 1)*isum([(xx-.6875).square() for xx in x])+2*relu(.5-x[0]-x[1]).square()+.25*(x[0]-x[1]).square().square()

def iq(net,x,a,P):
    z=[.125+.5*x[j]+.125*x[1-j]+.0625*x[j]*(1-x[1-j])+a[j] for j in range(2)]
    future,fg=iexpect(net,z)
    q=istatecost(x)+P*isum([aa.square() for aa in a])+.5*a[0]*a[1]+4*isum([aa.square().square() for aa in a])+BETA*future
    g=[2*P*a[j]+.5*a[1-j]+16*a[j].square()*a[j]+BETA*fg[j] for j in range(2)]
    return q,g

def sqrt_upper(v):return math.nextafter(math.sqrt(max(0,float(v))),math.inf)

def certificate(nets,P,N):
    ts=time.perf_counter();x=grid(N);xi=[I.point(x[:,j]) for j in range(2)]
    records=[];actors=[];constants_list=[constants(net,P) for net in nets]
    for t in range(4):
        a,_=optimize(nets[t+1],x,P);ai=[I.point(a[:,j]) for j in range(2)]
        q,g=iq(nets[t+1],xi,ai,P);C=constants_list[t+1];mu=C['mu']
        gm=np.column_stack([gg.midpoint() for gg in g]);active=a>2**-23
        active_mean=(gm*active).sum(1)/np.maximum(active.sum(1),1)
        nu=np.where(a.sum(1)>=CAP-2**-22,np.maximum(0,-active_mean),0)
        # Any nonnegative dual multiplier is valid; no optimality flag is trusted.
        lower=q-isum([g[j]*ai[j] for j in range(2)])+(mu/2)*isum([aa.square() for aa in ai])-I.point(nu)*CAP
        for j in range(2):
            v=g[j]-mu*ai[j]+I.point(nu);neg=I(np.minimum(v.lo,0),np.minimum(v.hi,0))
            lower=lower-neg.square()/(2*mu)
        f=ivalue(nets[t],xi);r=f-I(lower.lo,q.hi)
        interpolation=(I.point(constants_list[t]['M'])+C['envelope_gradient_lipschitz'])/(4*N*N)
        ell=(I.point(np.min(r.lo))-interpolation).lo.item();uu=(I.point(np.max(r.hi))+interpolation).hi.item()
        delta=(q-I.point(lower.lo)).hi.max().item()
        distance=sqrt_upper(2)/(2*N)
        cross=I.point(C['Lxa'])*distance
        eta=(I.point(delta)+cross*sqrt_upper((I.point(2*delta)/mu).hi)+cross.square()/(2*mu)).hi.item()
        rounded_distance=(I.point(distance)+sqrt_upper(2)*2**-24).hi.item()
        cc=I.point(C['Lxa'])*rounded_distance
        rounded_eta=(I.point(delta)+cc*sqrt_upper((I.point(2*delta)/mu).hi)+cc.square()/(2*mu)).hi.item()
        records.append(dict(date=t,residual_lower=ell,residual_upper=uu,actor_allowance=eta,rounded_state_actor_allowance=rounded_eta,
                            nodal_primal_dual_gap=delta,interpolation_allowance=float(interpolation.hi),constants=C))
        actors.append(a)
    rr=ivalue(nets[-1],xi)-istatecost(xi,True)
    rem=(I.point(constants_list[-1]['M'])+18)/(4*N*N)
    term=dict(lower=(I.point(np.min(rr.lo))-rem).lo.item(),upper=(I.point(np.max(rr.hi))+rem).hi.item(),interpolation_allowance=float(rem.hi))
    total=I.point(0.);rounded=I.point(0.);lower_shift=I.point(0.);upper_shift=I.point(0.);disc=I.point(1.)
    for rec in records:
        osc=I.point(rec['residual_upper'])-rec['residual_lower']
        total=total+disc*(osc+rec['actor_allowance']);rounded=rounded+disc*(osc+rec['rounded_state_actor_allowance'])
        lower_shift=lower_shift+disc*rec['residual_upper'];upper_shift=upper_shift+disc*(I.point(rec['actor_allowance'])-rec['residual_lower']);disc=disc*BETA
    total=total+disc*(I.point(term['upper'])-term['lower']);rounded=rounded+disc*(I.point(term['upper'])-term['lower'])
    lower_shift=lower_shift+disc*term['upper'];upper_shift=upper_shift-disc*term['lower']
    states=np.array([[.125,.125],[.25,.5],[.5,.25],[.75,.75]])
    f0=ivalue(nets[0],[I.point(states[:,j]) for j in range(2)])
    return dict(N=N,price=P,policy_gap_upper=float(total.hi),rounded_state_policy_gap_upper=float(rounded.hi),
                records=records,terminal=term,actors=actors,states=states,
                optimal_value_lower=(f0-lower_shift).lo,own_policy_value_upper=(f0+upper_shift).hi,
                verification_seconds=time.perf_counter()-ts,state_nodes=len(x),action_grid_nodes=0,
                inner_iterations_per_node=160,innovation_law='independent uniform[-1/32,1/32]^2; analytic positive-part moments',
                squared_relu_expectation_calls=4*len(x)*(160+2),
                actor_scalar_storage=sum(a.size for a in actors),neural_scalar_storage=sum(4*len(net['c'])+3 for net in nets),
                neural_neuron_expectations=len(x)*(160+2)*sum(len(net['c']) for net in nets[1:]),
                expectation_gradient_float_calls=4*len(x)*160,expectation_value_float_calls=4*len(x),expectation_interval_calls=4*len(x),
                certificate='own-future network; continuous simplex via strongly convex dual; quadratic state and actor cover')

def service(P,seed,method,checkpoint=None):
    ts=time.perf_counter();x=grid(24);nets=[None]*5;training=[]
    for t in range(4,-1,-1):
        qstart=time.perf_counter()
        if t==4:y=terminal(x)
        else:_,y=optimize(nets[t+1],x,P)
        target_seconds=time.perf_counter()-qstart;fs=time.perf_counter()
        nets[t]=(fit(x,y,seed+t) if method=='convex-neural' else projection_fit(x,y,104729+t,prune=True) if method=='ridge-projection' else quadratic_fit(x,y))
        training.append(dict(date=t,target_seconds=target_seconds,fit_seconds=time.perf_counter()-fs,target_sha256=hashlib.sha256(y.tobytes()).hexdigest(),target_points=len(x)))
        print('TRAIN',method,P,seed,t,nets[t].get('training_max_error'),flush=True)
    fit_time=time.perf_counter()-ts;attempts=[];crossings={str(e):None for e in TARGETS}
    for N in LADDER:
        v=certificate(nets,P,N);attempts.append(v)
        if checkpoint is not None:checkpoint(dict(networks=nets,training=training,attempt=v),len(attempts)-1)
        print('VERIFY',method,P,seed,N,v['policy_gap_upper'],flush=True)
        for e in TARGETS:
            if crossings[str(e)] is None and v['policy_gap_upper']<=e:crossings[str(e)]=dict(attempt=len(attempts)-1,seconds_through_checkpoint_fsync=time.perf_counter()-ts)
        if all(v is not None for v in crossings.values()):break
    return dict(method=method,price=P,seed=seed,T=4,state_dimension=2,action_dimension=2,networks=nets,training=training,training_seconds=fit_time,
                attempts=attempts,crossings=crossings,conventional_training_labels=0,inherited_weights=0,
                all_state_gap=attempts[-1]['policy_gap_upper'],seconds_through_checkpoint_fsync=time.perf_counter()-ts)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--directory',required=True);p.add_argument('--pilot',action='store_true');args=p.parse_args()
    d=Path(args.directory);d.mkdir(parents=True,exist_ok=True)
    import torch
    torch.set_num_threads(1)
    for P in ([1] if args.pilot else [1,4]):
      for seed in (SEEDS[:1] if args.pilot else SEEDS):
       for method in ['convex-neural','quadratic-projection']:
        path=d/f'{method}-p{P}-s{seed}.json'
        if path.exists():raise FileExistsError(path)
        ts=time.perf_counter();r=service(P,seed,method);raw=(json.dumps(r,default=encode,sort_keys=True,separators=(',',':'))+'\n').encode()
        with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        row=dict(method=method,price=P,seed=seed,crossings=r['crossings'],all_state_gap=r['all_state_gap'],seconds_through_fsync=time.perf_counter()-ts,
                 record_sha256=hashlib.sha256(raw).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        path.with_suffix('.clock.json').write_text(json.dumps(row,indent=2,sort_keys=True)+'\n');print(json.dumps(row),flush=True)
