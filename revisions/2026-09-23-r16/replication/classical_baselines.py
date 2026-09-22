"""Two full-horizon state-space candidate generators on the unchanged economy.
Both use the invariant portfolio-head parameterization as a candidate class.
Neither discrete value is declared a continuous-time certificate. Bilinear
interpolated controls are checked separately with the common neural witness.
"""
from pathlib import Path
import sys,json,time,resource,argparse,platform
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]

def settle(t,u,x):return -.02*(u-2)**2+.1*np.log(np.maximum(x,.01))-8*(1-t)
def interpolate(v,u,x,ug,xg,t):
    # Bilinear inside; segment first-hit settlement outside is handled by jump().
    a=np.clip((u-ug[0])/(ug[1]-ug[0]),0,len(ug)-1);b=np.clip((x-xg[0])/(xg[1]-xg[0]),0,len(xg)-1)
    i=np.minimum(a.astype(int),len(ug)-2);j=np.minimum(b.astype(int),len(xg)-2);a=a-i;b=b-j
    return (1-a)*(1-b)*v[i,j]+a*(1-b)*v[i+1,j]+(1-a)*b*v[i,j+1]+a*b*v[i+1,j+1]
def jump(v,u,x,du,dx,ug,xg,t,dt):
    un=u+du;xn=x+dx;inside=(un>ug[0])&(un<ug[-1])&(xn>xg[0])&(xn<xg[-1]);lam=np.ones(np.broadcast_shapes(un.shape,xn.shape))
    for z,d,low,high in [(u,du,ug[0],ug[-1]),(x,dx,xg[0],xg[-1])]:
        z,d=np.broadcast_arrays(z,d)
        lower=(z+d<=low)&(d<0);upper=(z+d>=high)&(d>0)
        r=np.ones_like(d);np.divide(low-z,d,out=r,where=lower);lam=np.minimum(lam,np.where(lower,r,1))
        r=np.ones_like(d);np.divide(high-z,d,out=r,where=upper);lam=np.minimum(lam,np.where(upper,r,1))
    lam=np.clip(lam,0,1)
    value=interpolate(v,un,xn,ug,xg,t+dt)
    return np.where(inside,value,settle(t+dt*lam,u+du*lam,x+dx*lam))

def solve(method,n,nt,control_counts,out):
    start=time.perf_counter();ug=np.linspace(1.2,2.8,n);xg=np.linspace(.5,2,n);U,X=np.meshgrid(ug,xg,indexing='ij')
    u=U[1:-1,1:-1].ravel();x=X[1:-1,1:-1].ravel();hu=ug[1]-ug[0];hx=xg[1]-xg[0]
    cc,tt,pp=np.meshgrid(np.linspace(.05,.8,control_counts[0]),np.linspace(-.2,.2,control_counts[1]),np.linspace(-.5,.8,control_counts[2]),indexing='ij')
    heads=np.stack([cc.ravel(),tt.ravel(),pp.ravel()],axis=-1);c=heads[:,0,None];th=heads[:,1,None];p=heads[:,2,None]*(2-x)/1.5
    bx=(.02+.06*p)*x-c;bu=np.broadcast_to(th,bx.shape);ru=-np.exp((u-1)*(-np.log(c)))/(u-1)-th*th
    v=settle(1,U,X);dt=1/nt;policy=np.zeros((nt,n,n,3));cfl_min=1.
    # Wide jumps shrink as sqrt(mesh): interpolation error divided by jump^2
    # vanishes with mesh, unlike an unqualified nearest-grid covariance stencil.
    h=np.sqrt(max(hu,hx));rates=np.abs(bu)/hu+np.abs(bx)/hx+2/h**2
    sub=max(1,int(np.ceil(dt*rates.max())));ds=dt/sub
    for it in reversed(range(nt)):
        t=it/nt
        for subit in reversed(range(sub if method=='markov_chain' else 1)):
            st=t+subit*ds if method=='markov_chain' else t
            if method=='semi_lagrangian':
                q=np.zeros_like(bx)
                for a in [-1.,1.]:
                    for b in [-1.,1.]:
                        du=bu*dt+.05*np.sqrt(dt)*a;dx=bx*dt+.2*p*x*np.sqrt(dt)*(-.25*a+np.sqrt(15/16)*b)
                        q+=jump(v,u,x,du,dx,ug,xg,st,dt)/4
                q=ru*dt+np.exp(-.04*dt)*q
            else:
                rateu=np.abs(bu)/hu;ratex=np.abs(bx)/hx;mass=1-ds*rates;cfl_min=min(cfl_min,float(mass.min()))
                q=mass*v[1:-1,1:-1].ravel()
                q+=ds*rateu*jump(v,u,x,np.sign(bu)*hu,np.zeros_like(bx),ug,xg,st,ds)
                q+=ds*ratex*jump(v,u,x,np.zeros_like(bx),np.sign(bx)*hx,ug,xg,st,ds)
                # Sigma columns (.05,-.05 p x), (0,.2 sqrt(15/16) p x).
                for a in [-1.,1.]:
                    q+=ds/(2*h*h)*jump(v,u,x,a*h*.05,a*h*(-.05*p*x),ug,xg,st,ds)
                    q+=ds/(2*h*h)*jump(v,u,x,0.,a*h*.2*np.sqrt(15/16)*p*x,ug,xg,st,ds)
                q=ru*ds+np.exp(-.04*ds)*q
            choice=q.argmax(axis=0);new=settle(st,U,X);new[1:-1,1:-1]=q[choice,np.arange(len(u))].reshape(n-2,n-2);v=new
        agrid=np.zeros((n,n,3));agrid[1:-1,1:-1]=heads[choice].reshape(n-2,n-2,3)
        agrid[0]=agrid[1];agrid[-1]=agrid[-2];agrid[:,0]=agrid[:,1];agrid[:,-1]=agrid[:,-2]
        policy[it]=agrid
    path=out/f'{method}_{n}.npz';np.savez_compressed(path,policy=policy,ug=ug,xg=xg,nt=nt,value=v)
    rec={'method':method,'state_nodes_per_axis':n,'time_steps':nt,'internal_substeps':sub if method=='markov_chain' else 1,
      'control_head_counts':control_counts,'controls_per_node':len(heads),'minimum_markov_stay_probability':cfl_min if method=='markov_chain' else None,
      'discrete_central_value':float(interpolate(v,np.array(2.),np.array(1.25),ug,xg,0)),
      'generation_wall_seconds':time.perf_counter()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      'candidate_class':'bilinear continuous state control heads, piecewise constant in time, portfolio multiplied by (2-x)/1.5',
      'discrete_value_scope':'uncertified discretization diagnostic, not a lower/upper continuous-time bound',
      'same_economy':True,'payoff':'original utility, discount, first-exit fee and terminal settlement',
      'boundary_discretization':'straight-segment first exit on each approximate jump; exact contract used in separate verification',
      'path':str(path.relative_to(ROOT))}
    (out/f'{method}_{n}.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec),flush=True)
    return rec

def certify(policy_file,network_file,out,grid=(4,16,16)):
    import accessibility_certificate as C
    I,Q=C.I,C.Q;exp=C.exp
    from fractions import Fraction as F
    st=time.perf_counter();raw=np.load(policy_file);pol=raw['policy'];ug=raw['ug'];xg=raw['xg'];nsteps=int(raw['nt'])
    d=json.loads(Path(network_file).read_text());s,idx=C.cell_grid(*grid);nt=grid[0];ep=np.zeros(nt);em=np.zeros(nt)
    # Min/max of every node that can enter a bilinear interpolant over each cell.
    bounds=[]
    for lo,hi in zip(s.lo,s.hi):
        ta=max(0,int(np.floor(lo[0]*nsteps)));tb=min(nsteps-1,int(np.floor(hi[0]*nsteps)))
        ia=max(0,int(np.searchsorted(ug,lo[1],side='right')-1));ib=min(len(ug)-1,int(np.searchsorted(ug,hi[1],side='left')))
        ja=max(0,int(np.searchsorted(xg,lo[2],side='right')-1));jb=min(len(xg)-1,int(np.searchsorted(xg,hi[2],side='left')))
        block=pol[ta:tb+1,ia:ib+1,ja:jb+1];bounds.append((block.min(axis=(0,1,2)),block.max(axis=(0,1,2))))
    arr=np.array(bounds)
    for off in range(0,len(idx),64):
        z=s[off:off+64];j=C.critic_jet(z,d);a=[I(arr[off:off+64,0,k],arr[off:off+64,1,k]) for k in range(3)]
        # Stored grid coordinates/actions are exact dyadics; clip head hulls to exact A.
        a=[C.clip(a[0],'.05','.8'),C.clip(a[1],'-.2','.2'),(2-z[:,2])/Q('1.5')*C.clip(a[2],'-.5','.8')]
        common=j[1]+Q('.02')*z[:,2]*j[3]+Q('.00125')*j[4]-Q('.04')*j[0]
        rp=common+C.action_h(z,j,a,'2');ru=common+C.oracle(z,j,'2')
        for q,k in enumerate(idx[off:off+64]):ep[k[0]]=max(ep[k[0]],float(ru.hi[q]));em[k[0]]=max(em[k[0]],float(-rp.lo[q]))
    total=I(0)
    for it in range(nt):
        mass=(exp(-Q('.04')*Q(F(it,nt)))-exp(-Q('.04')*Q(F(it+1,nt))))/Q('.04')
        total=total+mass*(I(ep[it])+I(em[it]))
    r={'status':'VALID_CONTINUOUS_TIME_POLICY_BOUND','grid':list(grid),'interior_cells':len(idx),'failed_cells':0,'skipped_cells':0,
      't0_regret_upper':float(total.hi),'boundary_budget':0,'verification_wall_seconds':time.perf_counter()-st,
      'common_witness':str(Path(network_file).relative_to(ROOT)),'policy_file':str(Path(policy_file).relative_to(ROOT)),
      'targets':{str(e):bool(total.hi<Q(str(e)).lo) for e in [.01,.005,.0025,.001]},
      'scope':'same signed residual certificate and original continuous control upper oracle; no use of the discrete value as truth'}
    Path(out).write_text(json.dumps(r,indent=2)+'\n');return r

def main(out,network):
    out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();rows=[]
    for method in ['markov_chain','semi_lagrangian']:
        for n,nt,c in [(9,64,[3,3,4]),(17,128,[5,5,6]),(25,256,[7,7,8])]:
            row=solve(method,n,nt,c,out)
            if network:
                r=certify(ROOT/row['path'],network,out/f'{method}_{n}_certificate.json');row.update(r)
            rows.append(row);(out/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
    (out/'resources.json').write_text(json.dumps({'status':'completed','wall_seconds':time.perf_counter()-start,'platform':platform.platform(),
      'scope':'six independent candidate-generation cases and common continuous-time certification; shared interpolation helper, distinct transition schemes'},indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--network',type=Path);a=p.parse_args();main(a.out.resolve(),a.network.resolve() if a.network else None)
