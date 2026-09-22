"""Original-action state-space generators, one-sided upper-wealth continuation,
and independent policy-specific neural evaluation witnesses. The numerical
Bellman values are diagnostics; only separate MPFR residuals certify CT loss.
"""
from pathlib import Path
import sys,json,time,resource,argparse,gzip,hashlib
from fractions import Fraction as F
import numpy as np
import torch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];R16=ROOT/'revisions/2026-09-23-r16/replication'
sys.path.insert(0,str(R16))
import classical_baselines as B
import accessibility_certificate as C
from accessibility_neural import Net,serialize
import interval_objective as D

def jump(v,u,x,du,dx,ug,xg,t,dt):
    un=u+du;xn=x+dx
    # The last grid column is the interior continuation trace, not settlement.
    # A tangent jump from that column is allowed only in the zero-p candidate;
    # all nonzero-p actions there are separately assigned immediate settlement.
    tangent=(x==xg[-1])&(dx==0)
    inside=(un>ug[0])&(un<ug[-1])&(xn>xg[0])&((xn<xg[-1])|tangent)
    lam=np.ones(np.broadcast_shapes(un.shape,xn.shape))
    for z,d,low,high in [(u,du,ug[0],ug[-1]),(x,dx,xg[0],xg[-1])]:
        z,d=np.broadcast_arrays(z,d);lower=(z+d<=low)&(d<0);upper=(z+d>=high)&(d>0)
        r=np.ones_like(d);np.divide(low-z,d,out=r,where=lower);lam=np.minimum(lam,np.where(lower,r,1))
        r=np.ones_like(d);np.divide(high-z,d,out=r,where=upper);lam=np.minimum(lam,np.where(upper,r,1))
    lam=np.clip(lam,0,1);value=B.interpolate(v,un,xn,ug,xg,t+dt)
    return np.where(inside,value,B.settle(t+dt*lam,u+du*lam,x+dx*lam))

def solve(method,n,nt,counts,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);start=time.perf_counter();ug=np.linspace(1.2,2.8,n);xg=np.linspace(.5,2,n);U,X=np.meshgrid(ug,xg,indexing='ij')
    u=U[1:-1,1:].ravel();x=X[1:-1,1:].ravel();hu=ug[1]-ug[0];hx=xg[1]-xg[0]
    # Zero portfolio is an essential action at an inward degenerate boundary.
    ps=np.unique(np.r_[np.linspace(-.5,.8,counts[2]),0.]);cs=np.linspace(.05,.8,counts[0]);ts=np.unique(np.r_[np.linspace(-.2,.2,counts[1]),0.])
    cc,tt,pp=np.meshgrid(cs,ts,ps,indexing='ij');acts=np.stack([cc.ravel(),tt.ravel(),pp.ravel()],-1)
    c=acts[:,0,None];th=acts[:,1,None];p=np.broadcast_to(acts[:,2,None],(len(acts),len(x)))
    bx=(.02+.06*p)*x-c;bu=np.broadcast_to(th,bx.shape);ru=-np.exp((u-1)*(-np.log(c)))/(u-1)-th*th
    v=B.settle(1,U,X);dt=1/nt;policy=np.zeros((nt,n,n,3));h=np.sqrt(max(hu,hx));rates=np.abs(bu)/hu+np.abs(bx)/hx+2/h**2
    sub=max(1,int(np.ceil(dt*rates.max())));ds=dt/sub;cfl=1.;min_boundary_margin=float('inf');bad_upper=0
    for it in reversed(range(nt)):
        t=it/nt
        for subit in reversed(range(sub if method=='markov_chain' else 1)):
            st=t+subit*ds if method=='markov_chain' else t
            if method=='semi_lagrangian':
                q=np.zeros_like(bx)
                for a in [-1.,1.]:
                    for b in [-1.,1.]:
                        q+=jump(v,u,x,bu*dt+.05*np.sqrt(dt)*a,bx*dt+.2*p*x*np.sqrt(dt)*(-.25*a+np.sqrt(15/16)*b),ug,xg,st,dt)/4
                q=ru*dt+np.exp(-.04*dt)*q
            else:
                rateu=np.abs(bu)/hu;ratex=np.abs(bx)/hx;mass=1-ds*rates;cfl=min(cfl,float(mass.min()));q=mass*v[1:-1,1:].ravel()
                q+=ds*rateu*jump(v,u,x,np.sign(bu)*hu,np.zeros_like(bx),ug,xg,st,ds)
                q+=ds*ratex*jump(v,u,x,np.zeros_like(bx),np.sign(bx)*hx,ug,xg,st,ds)
                for a in [-1.,1.]:
                    q+=ds/(2*h*h)*jump(v,u,x,a*h*.05,a*h*(-.05*p*x),ug,xg,st,ds)
                    q+=ds/(2*h*h)*jump(v,u,x,0.,a*h*.2*np.sqrt(15/16)*p*x,ug,xg,st,ds)
                q=ru*ds+np.exp(-.04*ds)*q
            upper=x==2.;nonzero=acts[:,2]!=0
            q[np.ix_(nonzero,upper)]=B.settle(st,u[upper],x[upper])
            # Check, rather than assume, that the continuation action wins.
            margin=q[np.ix_(~nonzero,upper)].max(0)-B.settle(st,u[upper],x[upper]);min_boundary_margin=min(min_boundary_margin,float(margin.min()))
            choice=q.argmax(0);bad_upper+=int(np.count_nonzero(acts[choice[upper],2]))
            new=B.settle(st,U,X);new[1:-1,1:]=q[choice,np.arange(len(u))].reshape(n-2,n-1);v=new
        ag=np.zeros((n,n,3));ag[1:-1,1:]=acts[choice].reshape(n-2,n-1,3);ag[0]=ag[1];ag[-1]=ag[-2];ag[:,0]=ag[:,1];policy[it]=ag
    if bad_upper:raise ArithmeticError(f'Nonzero portfolio chosen on continuation trace: {bad_upper}')
    path=out/f'{method}_{n}.npz';np.savez_compressed(path,policy=policy,ug=ug,xg=xg,nt=nt,value=v)
    r={'method':method,'n':n,'nt':nt,'action_counts':[len(cs),len(ts),len(ps)],'controls':len(acts),'grid_contains_zero_portfolio':True,'interior_portfolio_factor':False,'upper_trace':'Continuation computed with zero-p dynamics; nonzero-p immediate settlement compared explicitly','upper_zero_portfolio_violations':bad_upper,'minimum_numerical_continuation_margin':min_boundary_margin,'minimum_stay_probability':cfl if method=='markov_chain' else None,'discrete_central_value':float(B.interpolate(v,np.array(2.),np.array(1.25),ug,xg,0)),'generation_wall_seconds':time.perf_counter()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'scope':'Original unrestricted action grid, not a continuous-time value bound','file':path.name}
    path.with_suffix('.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True);return path,r

def hulls(policy_file,grid=(4,16,16)):
    raw=np.load(policy_file);pol=raw['policy'];ug=raw['ug'];xg=raw['xg'];ns=int(raw['nt']);s,idx=C.cell_grid(*grid);bounds=[]
    assert np.all(pol[:,:,-1,2]==0)
    for lo,hi in zip(s.lo,s.hi):
        ta=max(0,int(np.floor(lo[0]*ns)));tb=min(ns-1,int(np.floor(hi[0]*ns)))
        ia=max(0,int(np.searchsorted(ug,lo[1],side='right')-1));ib=min(len(ug)-1,int(np.searchsorted(ug,hi[1],side='left')))
        ja=max(0,int(np.searchsorted(xg,lo[2],side='right')-1));jb=min(len(xg)-1,int(np.searchsorted(xg,hi[2],side='left')))
        z=pol[ta:tb+1,ia:ib+1,ja:jb+1];bounds.append([z.min((0,1,2)),z.max((0,1,2))])
    return s,idx,np.asarray(bounds)

def evaluate(policy_file,out,steps=400,width=16,seed=17300):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);start=time.perf_counter();torch.set_num_threads(1);torch.set_default_dtype(torch.float64);torch.manual_seed(seed)
    critic=Net(1,width).double()
    with torch.no_grad():critic.layers[-1].weight.mul_(.1);critic.layers[-1].bias.fill_(6.7)
    opt=torch.optim.Adam(critic.parameters(),lr=.003);s,idx,ab=hulls(policy_file);ts=D.I(torch.tensor(s.lo),torch.tensor(s.hi));ta=[D.clip(D.I(ab[:,0,k],ab[:,1,k]),*[(.05,.8),(-.2,.2),(-.5,.8)][k]) for k in range(3)]
    mass=(torch.exp(-.04*torch.arange(4)/4)-torch.exp(-.04*(torch.arange(4)+1)/4))/.04
    hist=[]
    for step in range(steps):
        j=D.critic_jet(ts,critic);common=j[1]+.02*ts[:,2]*j[3]+.00125*j[4]-.04*j[0];ru=common+D.oracle(ts,j);rp=common+D.action_h(ts,j,ta)
        e=torch.cat([ru.hi.reshape(4,-1),torch.zeros(4,1)],1);n=torch.cat([-rp.lo.reshape(4,-1),torch.zeros(4,1)],1)
        loss=(mass*.15*(torch.logsumexp(e/.15,1)+torch.logsumexp(n/.15,1))).sum()
        if not torch.isfinite(loss):raise ArithmeticError('Nonfinite evaluation objective')
        opt.zero_grad();loss.backward();torch.nn.utils.clip_grad_norm_(critic.parameters(),100);opt.step()
        if (step+1)%50==0:hist.append({'step':step+1,'proposal_surrogate':float(loss.detach())})
    generation=time.perf_counter()-start;d={'version':'R17','seed':seed,'step':steps,'width':width,'critic':serialize(critic),'policy':str(policy_file),'critic_role':'method-specific evaluation-envelope witness; no inherited neural critic'}
    (out/'witness.json').write_text(json.dumps(d,indent=2)+'\n');(out/'history.json').write_text(json.dumps(hist,indent=2)+'\n')
    tick=time.perf_counter();rows=[]
    for off in range(0,len(idx),1024):
        z=s[off:off+1024];j=C.critic_jet(z,d);a=[C.clip(C.I(ab[off:off+1024,0,k],ab[off:off+1024,1,k]),*[(".05",".8"),("-.2",".2"),("-.5",".8")][k]) for k in range(3)]
        common=j[1]+C.Q('.02')*z[:,2]*j[3]+C.Q('.00125')*j[4]-C.Q('.04')*j[0];rp=common+C.action_h(z,j,a,'2');ru=common+C.oracle(z,j,'2')
        for h,k in enumerate(idx[off:off+1024]):rows.append({'cell':k,'ep':float(max(0,ru.hi[h])),'em':float(max(0,-rp.lo[h]))})
    total=C.I(0);slabs=[]
    for it in range(4):
        rr=[r for r in rows if r['cell'][0]==it];ep=max(r['ep'] for r in rr);em=max(r['em'] for r in rr);m=(C.exp(-C.Q('.04')*C.Q(F(it,4)))-C.exp(-C.Q('.04')*C.Q(F(it+1,4))))/C.Q('.04');total=total+m*(C.I(ep)+C.I(em));slabs.append({'slab':it,'ep':ep,'em':em})
    r={'status':'VALID_CONTINUOUS_TIME_BOUND','t0_regret_upper':float(total.hi),'grid':[4,16,16],'cells':len(idx),'failed_cells':0,'skipped_cells':0,'boundary_budget':0,'boundary_argument':'Bilinear p has zero upper-face nodes and bounded p/(2-x); c>=.05. No distance multiplier on interior controls.','witness_training_seconds':generation,'audit_seconds':time.perf_counter()-tick,'slabs':slabs,'target_0.01':bool(total.hi<C.Q('.01').lo),'method_specific_witness':True,'controls_linf_ranges':[[float(ab[:,0,k].min()),float(ab[:,1,k].max())] for k in range(3)],'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (out/'certificate.json').write_text(json.dumps(r,indent=2)+'\n')
    with gzip.open(out/'cells.json.gz','wt') as f:json.dump(rows,f)
    print(json.dumps(r),flush=True);return r
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--method',choices=['markov_chain','semi_lagrangian'],required=True);p.add_argument('--n',type=int,required=True);p.add_argument('--nt',type=int,required=True);p.add_argument('--counts',type=int,nargs=3,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    pf,r=solve(a.method,a.n,a.nt,a.counts,a.out);e=evaluate(pf,a.out/f'{a.method}_{a.n}_evaluation',seed=17300+a.n+(a.method=='semi_lagrangian'));r.update(e);(a.out/f'{a.method}_{a.n}_complete.json').write_text(json.dumps(r,indent=2)+'\n')
