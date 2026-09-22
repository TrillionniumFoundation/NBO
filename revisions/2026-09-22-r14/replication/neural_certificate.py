"""Independent full-box continuous-time/action audit of an actual R14 network.

Every cell is enclosed, not sampled. All scalar economic constants are exact
rationals. JSON weights denote exact binary64 numbers, real tanh defines the
mathematical feedback. Elementary-function bounds come from interval64 only.
The robust action allowance covers ANY action within delta of that feedback;
it does not assert a floating-point library's undocumented tanh accuracy.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
import argparse, json, time, resource, hashlib, gzip
import numpy as np
from interval64 import I, exp, log, tanh, affine, stack, exact_clip, up

Q=I.rational

def network_value(s,layers):
    z=stack([2*s[:,0]-1,(s[:,1]-2)/Q('.8'),(s[:,2]-Q('1.25'))/Q('.75')],axis=-1)
    for i,r in enumerate(layers):
        z=affine(z,r['weight'],r['bias'])
        if i<2:z=tanh(z)
    return z

def network_jet(s,layers):
    """value,t,u,x,uu,ux,xx; affine arithmetic reduces each product outward."""
    n=len(s.lo);zero=I(np.zeros((n,3)))
    z=stack([2*s[:,0]-1,(s[:,1]-2)/Q('.8'),(s[:,2]-Q('1.25'))/Q('.75')],axis=-1)
    def constrow(v):return I(np.broadcast_to(np.asarray(v,float),(n,3)))
    j=[z,constrow([2,0,0]),constrow([0,1,0])/Q('.8'),constrow([0,0,1])/Q('.75'),zero,zero,zero]
    for i,r in enumerate(layers):
        a=affine(stack(j,axis=1),r['weight'])
        j=[a[:,k] for k in range(7)];j[0]=j[0]+I(r['bias'])
        if i<2:
            v=tanh(j[0]);d=1-v.square();dd=-2*v*d
            j=[v,d*j[1],d*j[2],d*j[3],dd*j[2].square()+d*j[4],dd*j[2]*j[3]+d*j[5],dd*j[3].square()+d*j[6]]
    return [v[:,0] for v in j]

def critic_jet(s,layers):
    y,yt,yu,yx,yuu,yux,yxx=network_jet(s,layers);t,u,x=s[:,0],s[:,1],s[:,2];h=1-t
    G=-Q('.02')*(u-2).square()+Q('.1')*log(x)
    return [G+h*y,-y+h*yt,-Q('.04')*(u-2)+h*yu,Q('.1')/x+h*yx,
        -Q('.04')+h*yuu,h*yux,-Q('.1')/x.square()+h*yxx]

def actions(s,layers,delta):
    a=tanh(network_value(s,layers));d=I(-delta,delta)
    return [exact_clip(Q('.425')+Q('.375')*a[:,0]+d,'.05','.8'),
      exact_clip(Q('.2')*a[:,1]+d,'-.2','.2'),exact_clip(Q('.15')+Q('.65')*a[:,2]+d,'-.5','.8')]

def utility(c,u):return -exp((u-1)*(-log(c)))/(u-1)

def action_h(s,j,a,k):
    _,_,vu,vx,_,vux,vxx=j;x=s[:,2];u=s[:,1];c,theta,p=a
    return utility(c,u)-Q(k)/2*theta.square()+theta*vu+(Q('.06')*p*x-c)*vx+Q('.02')*p.square()*x.square()*vxx-Q('.0025')*p*x*vux

def oracle(s,j,k):
    _,_,vu,vx,_,vux,vxx=j;x=s[:,2];u=s[:,1];n=len(x.lo)
    # Interior consumption critical point if marginal value is positive.
    c=I(np.full(n,Q('.05').lo),np.full(n,Q('.8').hi));positive=vx.lo>0
    if positive.any():
        cp=exact_clip(exp(-log(vx[positive])/u[positive]),'.05','.8')
        c.lo[positive]=cp.lo;c.hi[positive]=cp.hi
    nonpositive=vx.hi<=0
    c.lo[nonpositive]=Q('.8').lo;c.hi[nonpositive]=Q('.8').hi
    hc=utility(c,u)-c*vx
    theta=exact_clip(vu/Q(k),'-.2','.2');ht=theta*vu-Q(k)/2*theta.square()
    h1=Q('.06')*x*vx-Q('.0025')*x*vux;h2=Q('.04')*x.square()*vxx
    def hp(p):return h1*p+h2/2*p.square()
    a,b=hp(Q('-.5')),hp(Q('.8'));pl=np.maximum(a.lo,b.lo);ph=np.maximum(a.hi,b.hi)
    concave=h2.hi<0
    if concave.any():
        p=exact_clip(-h1[concave]/h2[concave],'-.5','.8')
        v=h1[concave]*p+h2[concave]/2*p.square()
        pl[concave]=np.maximum(pl[concave],v.lo);ph[concave]=np.maximum(ph[concave],v.hi)
    uncertain=(h2.lo<0)&(h2.hi>=0)
    if uncertain.any():
        p=I(Q('-.5').lo,Q('.8').hi)
        v=h1[uncertain]*p+h2[uncertain]/2*p.square();ph[uncertain]=np.maximum(ph[uncertain],v.hi)
    return hc+ht+I(pl,ph)

def transported_residual(s,j):
    """Uniform coefficient perturbation, common domain/control/payoff trace.
    r in [.019,.021], risk premium [.058,.062], sigma_u [.049,.051],
    sigma_x [.195,.205], discount [.039,.041], cost [1.9,2.1], corr=-.25.
    """
    v,_,_,vx,vuu,vux,vxx=j;x=s[:,2];p=I(Q('-.5').lo,Q('.8').hi)
    absI=lambda a:I(a.maxabs())
    drift=(I(Q('-.001').lo,Q('.001').hi)+I(Q('-.002').lo,Q('.002').hi)*p)*x*vx
    du=(I(Q('.049').lo,Q('.051').hi).square()-Q('.05').square())/2*vuu
    dx=(I(Q('.195').lo,Q('.205').hi).square()-Q('.2').square())/2*p.square()*x.square()*vxx
    cross=-Q('.25')*(I(Q('.049').lo,Q('.051').hi)*I(Q('.195').lo,Q('.205').hi)-Q('.05')*Q('.2'))*p*x*vux
    disc=I(Q('-.001').lo,Q('.001').hi)*v
    cost=I(Q('-.1').lo,Q('.1').hi)*Q('.2').square()/2
    return absI(drift)+absI(du)+absI(dx)+absI(cross)+absI(disc)+absI(cost)

def cell_grid(nt,nu,nx,face=None):
    tl=[F(i,nt) for i in range(nt+1)];ul=[F(6,5)+F(8*i,5*nu) for i in range(nu+1)];xl=[F(1,2)+F(3*i,2*nx) for i in range(nx+1)]
    out=[];indices=[]
    for it in range(nt):
      for iu in range(nu):
       for ix in range(nx):
        a=[tl[it],ul[iu],xl[ix]];b=[tl[it+1],ul[iu+1],xl[ix+1]]
        if face:
            axis,end=face
            if axis==1 and iu!=0:continue
            if axis==2 and ix!=0:continue
            a[axis]=b[axis]=[ul,xl][axis-1][0 if end==0 else -1]
        out.append(([float(Q(q).lo) for q in a],[float(Q(q).hi) for q in b]));indices.append([it,iu,ix])
    arr=np.asarray(out);return I(arr[:,0,:],arr[:,1,:]),indices

def audit(path,out,grid,delta=2**-24,chunk=128):
    started=time.perf_counter();cpu=time.process_time();d=json.loads(path.read_text());nt,nu,nx=grid
    s,idx=cell_grid(nt,nu,nx);records=[];slab=[]
    for i in range(0,len(idx),chunk):
        c=s[i:i+chunk];j=critic_jet(c,d['critic']);a=actions(c,d['actor'],delta)
        ha=action_h(c,j,a,'2');hs=oracle(c,j,'2')
        common=j[1]+Q('.02')*c[:,2]*j[3]+Q('.00125')*j[4]-Q('.04')*j[0]
        res=common+ha;gap=np.maximum(0,(hs-ha).hi);transport=transported_residual(c,j).hi
        for h,(e,q,dt) in enumerate(zip(res.maxabs(),gap,transport)):
            records.append({'cell':idx[i+h],'evaluation_residual_upper':float(e),'action_gap_upper':float(q),'transport_residual_upper':float(dt),
              'residual_interval':[float(res.lo[h]),float(res.hi[h])]})
    boundary=[]
    for face in [(1,0),(1,1),(2,0),(2,1)]:
        bs,_=cell_grid(nt,nu,nx,face);maximum=0.
        for i in range(0,len(bs.lo),chunk):
            c=bs[i:i+chunk];y=network_value(c,d['critic'])[:,0]
            maximum=max(maximum,float(((1-c[:,0])*(y+8)).maxabs().max()))
        boundary.append({'face':face,'cells':len(bs.lo),'trace_error_upper':maximum})
    b=max(r['trace_error_upper'] for r in boundary)
    t0=I(0);uniform=I(0);transfer=I(0)
    for it in range(nt):
        rs=[r for r in records if r['cell'][0]==it]
        e=max(r['evaluation_residual_upper'] for r in rs);q=max(r['action_gap_upper'] for r in rs);dr=max(r['transport_residual_upper'] for r in rs)
        factor=2*I(e)+I(q)
        mass=(exp(-Q('.04')*Q(F(it,nt)))-exp(-Q('.04')*Q(F(it+1,nt))))/Q('.04')
        massnew=(exp(-Q('.039')*Q(F(it,nt)))-exp(-Q('.039')*Q(F(it+1,nt))))/Q('.039')
        t0=t0+mass*factor;uniform=uniform+Q(F(1,nt))*factor;transfer=transfer+massnew*(factor+2*I(dr))
        slab.append({'time_slab':it,'e':e,'q':q,'d':dr,'discount_mass':mass.pair()})
    total=2*I(b)+t0;alltime=2*I(b)+uniform;changed=2*I(b)+transfer
    result={'version':'R14','status':'VALID_ENCLOSURE','network_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'network_file':path.name,
      'training_step':d['step'],'width':d['width'],'grid':grid,'interior_cells':len(records),'boundary':boundary,'terminal_trace_error':0.,
      'domain':'[0,1] x [1.2,2.8] x [0.5,2]; complete continuous state-time domain; original k=2',
      'certificate_object':'Real tanh network with exact stored binary64 weights; robustness for any admissible actions within delta of it',
      'action_allowance_linf':delta,'deployment_scope':'Mathematical output-error contract; no unsupported libm accuracy assumption or certified SDE simulator',
      'error_budget':{'two_sided_trace':float((2*I(b)).hi),'integrated_residual_and_action':float(t0.hi),
        't0_regret_upper':float(total.hi),'all_initial_times_regret_upper':float(alltime.hi),
        'coefficient_box_t0_regret_upper':float(changed.hi)},
      'meets_0.01':bool(total.hi<Q('.01').lo),'cellwise':slab,'arithmetic':'Independent rational-Taylor outward binary64; no production certifier imports',
      'wall_seconds':time.perf_counter()-started,'process_seconds':time.process_time()-cpu,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      'failed_cells':0,'skipped_cells':0,'sampled_grid_claim':False}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    with gzip.open(out.with_suffix('.cells.json.gz'),'wt') as f:json.dump(records,f)
    print(json.dumps({k:result[k] for k in ['network_file','grid','error_budget','meets_0.01','wall_seconds']},indent=2))
    return result

def check_jets(path):
    import torch
    from neural_economy import load_model,jets,actor_action
    torch.set_num_threads(1);a,v,d=load_model(path);rng=np.random.default_rng(1421)
    pts=np.array([0,1.2,.5])+rng.random((20,3))*np.array([1,1.6,1.5]);s=torch.tensor(pts,dtype=torch.float64,requires_grad=True)
    tv,tg,tuu,tux,txx=jets(v,s);expected=[tv,tg[:,0],tg[:,1],tg[:,2],tuu,tux,txx]
    ji=critic_jet(I(pts),d['critic']);n=0;max_outside=0.
    # Torch is a diagnostic only; its elementary-function/roundoff error is not a proof oracle.
    for r,z in zip(expected,ji):
        r=r.detach().numpy();outside=np.maximum(np.maximum(z.lo-r,r-z.hi),0);max_outside=max(max_outside,float(outside.max()))
        if np.any(outside>1e-10):raise AssertionError('Jet implementation disagreement')
        n+=len(r)
    av=actor_action(a,s).detach().numpy();ai=actions(I(pts),d['actor'],2**-24)
    for i,z in enumerate(ai):assert ((z.lo<=av[:,i])&(av[:,i]<=z.hi)).all()
    return {'status':'PASS','jet_components_checked':n,'actor_components_checked':60,'max_torch_value_outside_enclosure':max_outside,
      'scope':'diagnostic against independent automatic differentiation, not proof from finite sampling'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--network',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--grid',nargs=3,type=int,default=[4,8,8]);p.add_argument('--test-only',action='store_true');p.add_argument('--delta',type=float,default=2**-24)
    a=p.parse_args()
    if a.test_only:
        r=check_jets(a.network);a.out.write_text(json.dumps(r,indent=2)+'\n');print(r)
    else:audit(a.network,a.out,a.grid,a.delta)
