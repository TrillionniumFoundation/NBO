"""Signed, stopping-accessibility-aware complete-box certification of R16.
MPFR provides all basic/elementary interval operations. All action branches of
THE ORIGINAL ECONOMY remain in the upper comparison. No cell can be skipped.
"""
from pathlib import Path
import sys,json,time,hashlib,gzip,resource,argparse
from fractions import Fraction as F
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE));import mpfr_interval as M
sys.modules['interval64']=M
sys.path.insert(0,str(ROOT/'revisions/2026-09-22-r14/replication'))
from neural_certificate import network_jet,network_value,cell_grid,action_h,oracle
I,exp,log,tanh,stack,clip=M.I,M.exp,M.log,M.tanh,M.stack,M.exact_clip
Q=I.rational

def product(a,b):
    v,t,u,x,uu,ux,xx=a;w,wt,wu,wx,wuu,wux,wxx=b
    return [v*w,t*w+v*wt,u*w+v*wu,x*w+v*wx,uu*w+2*u*wu+v*wuu,
            ux*w+u*wx+x*wu+v*wux,xx*w+2*x*wx+v*wxx]

def coordinate(s,axis):
    z=I(np.zeros(len(s.lo)));o=I(np.ones(len(s.lo)));j=[s[:,axis],z,z,z,z,z,z];j[axis+1]=o;return j

def factor(s,axis,rate,origin):
    # 1-exp(rate*(coordinate-origin)), with full jets.
    z=I(np.zeros(len(s.lo)));r=Q(rate);e=exp(r*(s[:,axis]-Q(origin)))
    j=[1-e,z,z,z,z,z,z];j[axis+1]=-r*e
    if axis==1:j[4]=-r.square()*e
    if axis==2:j[6]=-r.square()*e
    return j

def softplus_jet(j):
    y,yt,yu,yx,yuu,yux,yxx=j
    # Deliberately fail closed on overflow; no unproved truncation of softplus.
    z=log(1+exp(y));sig=1/(1+exp(-y));dd=sig*(1-sig)
    return [z,sig*yt,sig*yu,sig*yx,dd*yu.square()+sig*yuu,dd*yu*yx+sig*yux,dd*yx.square()+sig*yxx]

def critic_jet(s,d):
    B=product(product(factor(s,1,'-12','1.2'),factor(s,1,'12','2.8')),factor(s,2,'-4','.5'))
    if d.get('all_faces_ablation'):B=product(B,factor(s,2,'4','2'))
    j=product(B,softplus_jet(network_jet(s,d['critic'])));j[0]=j[0]-8
    t,u,x=s[:,0],s[:,1],s[:,2];h=1-t
    y,yt,yu,yx,yuu,yux,yxx=j
    return [-Q('.02')*(u-2).square()+Q('.1')*log(x)+h*y,-y+h*yt,
      -Q('.04')*(u-2)+h*yu,Q('.1')/x+h*yx,-Q('.04')+h*yuu,h*yux,-Q('.1')/x.square()+h*yxx]

def actions(s,d,delta):
    y=tanh(network_value(s,d['actor']));r=I(-delta,delta)
    c=clip(Q('.425')+Q('.375')*y[:,0]+r,'.05','.8')
    th=clip(Q('.2')*y[:,1]+r,'-.2','.2')
    p=(2-s[:,2])/Q('1.5')*clip(Q('.15')+Q('.65')*y[:,2]+r,'-.5','.8')
    return [c,th,p]

def audit(path,out,grid=(4,16,16),delta=2**-24,chunk=64):
    start=time.perf_counter();d=json.loads(Path(path).read_text());nt,nu,nx=grid
    s,idx=cell_grid(nt,nu,nx);rows=[]
    for off in range(0,len(idx),chunk):
        z=s[off:off+chunk];j=critic_jet(z,d);a=actions(z,d,delta);ha=action_h(z,j,a,'2');hs=oracle(z,j,'2')
        common=j[1]+Q('.02')*z[:,2]*j[3]+Q('.00125')*j[4]-Q('.04')*j[0]
        rp=common+ha;ru=common+hs
        for n in range(len(z.lo)):
            rows.append({'cell':idx[off+n],'positive_optimal_residual':float(max(0,ru.hi[n])),
              'negative_policy_residual':float(max(0,-rp.lo[n])),
              'absolute_policy_residual':float(rp.maxabs()[n]),'action_gap_upper':float(max(0,(hs-ha).hi[n])),
              'policy_residual_interval':[float(rp.lo[n]),float(rp.hi[n])]})
    total=I(0);unsigned=I(0);slabs=[];alltime=I(0)
    for it in range(nt):
        rs=[r for r in rows if r['cell'][0]==it];a=max(r['positive_optimal_residual'] for r in rs);b=max(r['negative_policy_residual'] for r in rs)
        e=max(r['absolute_policy_residual'] for r in rs);q=max(r['action_gap_upper'] for r in rs)
        mass=(exp(-Q('.04')*Q(F(it,nt)))-exp(-Q('.04')*Q(F(it+1,nt))))/Q('.04')
        total=total+mass*(I(a)+I(b));unsigned=unsigned+mass*(2*I(e)+I(q));alltime=alltime+Q(F(1,nt))*(I(a)+I(b))
        slabs.append({'slab':it,'positive_upper':a,'negative_policy':b,'unsigned_e':e,'action_gap_q':q})
    r={'version':'R16','status':'VALID_ENCLOSURE','network_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
       'seed':d['seed'],'width':d['width'],'step':d['step'],'all_faces_ablation':d.get('all_faces_ablation',False),'grid':list(grid),
       'interior_cells':len(rows),'skipped_cells':0,'failed_cells':0,'t0_regret_upper':float(total.hi),
       'all_initial_times_regret_upper':float(alltime.hi),'unsigned_residual_budget_upper':float(unsigned.hi),
       'boundary_budget':0,'boundary_proof':'exact trace on u faces, lower wealth, terminal; v>=g on upper wealth and policy upper-exit probability zero',
       'domain':'entire [0,1] x (1.2,2.8) x (0.5,2), original continuous action comparison',
       'implementation_contract':'delta before multiplication of portfolio output by (2-x)/1.5; no additive deployed portfolio error is asserted',
       'output_delta':delta,'targets':{str(q):bool(total.hi<Q(str(q)).lo) for q in [.01,.005,.0025,.001]},
       'arithmetic':f'MPFR {M.VERSION}, 128 bits, directed binary64 endpoints; shared R14 action algebra',
       'slabs':slabs,'wall_seconds':time.perf_counter()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2)+'\n')
    with gzip.open(out.with_suffix('.cells.json.gz'),'wt') as f:json.dump(rows,f)
    print(json.dumps({k:r[k] for k in ['seed','step','grid','t0_regret_upper','wall_seconds']}),flush=True)
    return r

def test(path):
    import torch
    import accessibility_neural as A
    torch.set_num_threads(1);torch.set_default_dtype(torch.float64)
    actor,critic,d=A.load_model(path);rng=np.random.default_rng(1611)
    pts=np.array([0,1.2,.5])+rng.uniform(.01,.99,(24,3))*np.array([1,1.6,1.5]);s=torch.tensor(pts,requires_grad=True)
    v,g,uu,ux,xx=A.jets(critic,s,d.get('all_faces_ablation',False));expected=[v,g[:,0],g[:,1],g[:,2],uu,ux,xx]
    actual=critic_jet(I(pts),d);error=0
    for x,y in zip(expected,actual):
        z=x.detach().numpy();error=max(error,float(np.maximum(np.maximum(y.lo-z,z-y.hi),0).max()))
    assert error<1e-9, error
    acts=A.actor_action(actor,s).detach().numpy();ai=actions(I(pts),d,2**-24)
    assert all(np.all((q.lo<=acts[:,i])&(acts[:,i]<=q.hi)) for i,q in enumerate(ai))
    return {'status':'PASS','jet_components':168,'actor_components':72,'max_float_ad_discrepancy':error,'scope':'diagnostic only, not proof by sampling'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--network',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--grid',type=int,nargs=3,default=[4,16,16]);p.add_argument('--test-only',action='store_true')
    a=p.parse_args()
    if a.test_only:a.out.write_text(json.dumps(test(a.network),indent=2)+'\n')
    else:audit(a.network,a.out,a.grid)
