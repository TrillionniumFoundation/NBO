"""Non-enumerative global certificate for the coupled nonconvex Hamiltonian.
The global partition is one-dimensional (sum of actions). Inner scalar
convex programs are bounded by strong convexity using outward arithmetic.
Floating-point root finding merely proposes dual multipliers and feasible acts.
"""
from __future__ import annotations
import heapq,json,time,pathlib,argparse,hashlib,importlib.util
import numpy as np
from mpmath import iv
iv.dps=50
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=ROOT/'revisions/2026-09-22-r9/results'

def I(x):return iv.mpf(x)
def lo(x):return float(np.nextafter(float(x.a),-np.inf))
def hi(x):return float(np.nextafter(float(x.b),np.inf))
def propose(p,z):
 d=len(p);left=float(np.min(2*p-2.2/d));right=float(np.max(2*p+2.2/d))
 for _ in range(45):
  lam=(left+right)/2;a=np.clip(d*(lam-2*p)/2,-1,1)
  for __ in range(5):a=np.clip(a-((2*a+.1*np.sin(2*a))/d+2*p-lam)/((2+.2*np.cos(2*a))/d),-1,1)
  if a.sum()<z:left=lam
  else:right=lam
 return float(lam),a

def node(p,left,right):
 d=len(p);center=(left+right)/2;radius=I(right-left)/2;lam,a=propose(p,center)
 dual=I(0);primal=I(0);total=I(0);m=I('1.8')/d
 for pp,aa in zip(p,a):
  x=I(float(aa));s=I(2)*I(float(pp));q=(x*x+I('.1')*iv.sin(x)**2)/d+(s-I(lam))*x
  g=(2*x+I('.1')*iv.sin(2*x))/d+s-I(lam)
  if aa==-1:err=max(0,-lo(g))
  elif aa==1:err=max(0,hi(g))
  else:err=max(abs(lo(g)),abs(hi(g)))
  dual+=q-I(err)**2/(2*m)
  primal+=(x*x+I('.1')*iv.sin(x)**2)/d+s*x;total+=x
 primal+=I('.3')*iv.sin(total)
 z=I(center);slope=I(lam)+I('.3')*iv.cos(z)
 lower=dual+I(lam)*z+I('.3')*iv.sin(z)-I(max(abs(lo(slope)),abs(hi(slope))))*radius-I('.15')*radius**2
 return lo(lower),hi(primal),a

def certify(p,tolerance=1e-5,max_nodes=100000):
 p=np.asarray(p,dtype=float);assert np.isfinite(p).all();d=len(p);start=time.perf_counter()
 lower,upper,a=node(p,-float(d),float(d));best=a.tolist();counter=0;heap=[(lower,counter,-float(d),float(d))];calls=1
 while heap and np.nextafter(upper-heap[0][0],np.inf)>tolerance and calls<max_nodes:
  lb,_,left,right=heapq.heappop(heap);mid=(left+right)/2
  for l,r in [(left,mid),(mid,right)]:
   low,up,aa=node(p,l,r);calls+=1;counter+=1
   if up<upper:upper=up;best=aa.tolist()
   if low<=upper:heapq.heappush(heap,(low,counter,l,r))
 lower=min(upper,heap[0][0]) if heap else upper
 gap=float(np.nextafter(upper-lower,np.inf))
 return {'dimension':d,'tolerance':tolerance,'lower_bound':lower,'upper_bound':upper,'gap':gap,
  'meets_tolerance':bool(gap<=tolerance),'node_evaluations':calls,'active_intervals':len(heap),
  'scalar_inner_problems':calls*d,'seconds':time.perf_counter()-start,'action':best,
  'gradient':p.tolist(),'arithmetic':'mpmath.iv 50 decimal digits; outward binary64 endpoints',
  'scope':'full continuous action box for the stored exact-real gradient vector, not a whole-state PDE certificate'}

def suite():
 import torch
 spec=importlib.util.spec_from_file_location('r8external',ROOT/'revisions/2026-09-22-r8/replication/external_comparison.py');r8=importlib.util.module_from_spec(spec);spec.loader.exec_module(r8)
 rows=[];rng=np.random.default_rng(9911)
 for d in [8,16,32,64,128]:
  if d in [8,16]:
   path=ROOT/f'revisions/2026-09-22-r8/results/external_d{d}_s400_nbo.pt'
   data=torch.load(path,map_location='cpu',weights_only=True);v=r8.Net(d,False).double();v.load_state_dict(data['critic'])
   x=torch.tensor(rng.normal(size=(1,d))*.2,dtype=torch.float64,requires_grad=True);t=torch.full((1,1),.5,dtype=torch.float64)
   p=torch.autograd.grad(v(t,x).sum(),x)[0].detach().numpy()[0]
   provenance={'checkpoint':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'state':x.detach().numpy()[0].tolist(),'time':.5}
  else:
   p=rng.normal(size=d)/d;provenance={'gradient_design':'independent centered Gaussian jet scaled by 1/d; same nonconvex Hamiltonian'}
  for eps in [.001,.00001]:
   result=certify(p,eps);result['provenance']=provenance;rows.append(result);print(d,eps,result['gap'],result['node_evaluations'],result['seconds'],flush=True)
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'action_certificates.json').write_text(json.dumps(rows,indent=2)+'\n')
 return rows
if __name__=='__main__':suite()
