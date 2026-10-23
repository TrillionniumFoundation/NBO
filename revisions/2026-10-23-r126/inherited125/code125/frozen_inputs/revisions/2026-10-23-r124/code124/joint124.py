"""Joint Bellman value/derivative information with exact dual certificates.

SciPy only proposes a point and multipliers. Every supplied bound is obtained
from an exact rational convex-Lagrangian tangent and its box residual. Neither
primal feasibility nor solver success is accepted as a numerical proof.
"""
from fractions import Fraction as F
import math,time,traceback
import numpy as np
from scipy.optimize import minimize
import envelope123 as env


def problem(case,b):
 mu,L=case['mu'],case['L'];K=L-mu
 if K<=0:raise ValueError('This implementation requires strict L > mu')
 nodes=sorted({p['a'] for p in case['payloads']}|{F(0),case['A'],case['incumbent'],F(b)})
 lower=[];upper=[]
 for x in nodes:
  pairs=[(p,env.contrast(case,p['a'],x)) for p in case['payloads']]
  lower.append(max(p['W']+c[0] for p,c in pairs))
  upper.append(min(p['U']+c[1] for p,c in pairs))
 for x in nodes:
  lower.append(env.gradient(case,x,False));upper.append(env.gradient(case,x,True))
 if any(l>u for l,u in zip(lower,upper)):raise ArithmeticError('Empty exact interpolation box')
 return dict(nodes=nodes,lower=lower,upper=upper,mu=mu,L=L,K=K,
  origin_index=nodes.index(case['incumbent']),target_index=nodes.index(F(b)))


def exact_constraints(p,z):
 """Return c_j<=0 and their exact gradients, in immutable edge order."""
 n=len(p['nodes']);mu,K=p['mu'],p['K'];out=[]
 for i in range(n-1):
  d=p['nodes'][i+1]-p['nodes'][i]
  s=z[n+i+1]-z[n+i]-mu*d
  w=z[i+1]-z[i]-z[n+i]*d-mu*d*d/2
  r=s*s/(2*K)
  ds=[F(0)]*(2*n);ds[n+i+1]=1;ds[n+i]=-1
  dw=[F(0)]*(2*n);dw[i+1]=1;dw[i]=-1;dw[n+i]=-d
  out.extend([(r-w,[s/K*v-u for v,u in zip(ds,dw)]),
              (r+w-s*d,[s/K*v+u-v*d for v,u in zip(ds,dw)]),
              (-s,[-v for v in ds]),(s-K*d,ds)])
 return out


def exact_bound(p,z,multipliers):
 n=len(p['nodes']);h=z[p['origin_index']]-z[p['target_index']]
 gradient=[F(0)]*(2*n);gradient[p['origin_index']]+=1;gradient[p['target_index']]-=1
 cons=exact_constraints(p,z)
 if len(multipliers)!=len(cons) or any(v<0 for v in multipliers):raise ValueError('Nonnegative complete dual vector required')
 lag=h
 for lam,(c,g) in zip(multipliers,cons):
  lag+=lam*c;gradient=[r+lam*v for r,v in zip(gradient,g)]
 residual=sum((min(r*(lo-v),r*(hi-v)) for r,lo,hi,v in zip(gradient,p['lower'],p['upper'],z)),F(0))
 bound=lag+residual
 return dict(objective_at_point=h,lagrangian_at_point=lag,gradient=gradient,
  box_residual_correction=residual,lower_bound=bound,contrast_upper=-bound,
  primal_feasibility_or_solver_success_required=False)


def solve(case,b,progress=None):
 tick=time.perf_counter();progress={} if progress is None else progress
 progress.update(stage='problem-construction',started=True)
 p=problem(case,b);n=len(p['nodes']);progress.update(problem=p,stage='floating-proposal')
 lo=np.array([float(v) for v in p['lower']]);hi=np.array([float(v) for v in p['upper']])
 center=(lo+hi)/2;scale=np.maximum((hi-lo)/2,1e-8)
 u_lo=(lo-center)/scale;u_hi=(hi-center)/scale
 ai,bi=p['origin_index'],p['target_index'];mu,K=float(p['mu']),float(p['K'])
 lengths=np.diff(np.array([float(x) for x in p['nodes']]))
 cs=np.array([v for d in lengths for v in (max(K*d*d,1e-18),max(K*d*d,1e-18),max(K*d,1e-12),max(K*d,1e-12))])
 objscale=max(abs(float(env.contrast(case,case['incumbent'],F(b))[1]-env.contrast(case,case['incumbent'],F(b))[0])),1e-6)
 objective_jac=np.zeros(2*n);objective_jac[ai]+=1/objscale;objective_jac[bi]-=1/objscale
 def con(u):
  z=center+scale*u;vals=[];jac=[]
  for i,d in enumerate(lengths):
   s=z[n+i+1]-z[n+i]-mu*d;w=z[i+1]-z[i]-z[n+i]*d-mu*d*d/2
   ds=np.zeros(2*n);ds[n+i+1]=1;ds[n+i]=-1
   dw=np.zeros(2*n);dw[i+1]=1;dw[i]=-1;dw[n+i]=-d
   vals.extend((s*s/(2*K)-w,s*s/(2*K)+w-s*d,-s,s-K*d))
   jac.extend((s/K*ds-dw,s/K*ds+dw-ds*d,-ds,ds))
  return -np.array(vals)/cs,-np.array(jac)*scale[None,:]/cs[:,None]
 failure=None
 try:
  result=minimize(lambda u:((center+scale*u)[ai]-(center+scale*u)[bi])/objscale,
   np.zeros(2*n),jac=lambda u:objective_jac*scale,
   method='SLSQP',bounds=list(zip(u_lo,u_hi)),
   constraints=[{'type':'ineq','fun':lambda u:con(u)[0],'jac':lambda u:con(u)[1]}],
   options={'ftol':1e-10,'maxiter':160,'disp':False})
  point=center+scale*result.x
  raw=getattr(result,'multipliers',np.zeros(len(cs)))
  if not np.all(np.isfinite(point)) or len(raw)!=len(cs) or not np.all(np.isfinite(raw)):raise ArithmeticError('Nonfinite solver proposal')
  multipliers=np.maximum(raw,0)*objscale/cs
  if not np.all(np.isfinite(multipliers)):raise ArithmeticError('Nonfinite rescaled multipliers')
  status=dict(success=bool(result.success),status=int(result.status),message=str(result.message),
   nit=int(result.nit),nfev=int(result.nfev),njev=int(result.njev),floating_minimum=float(result.fun)*objscale,
   all_fields_are_proposals=True)
 except (ArithmeticError,ValueError,np.linalg.LinAlgError) as exc:
  point=center;multipliers=np.zeros(len(cs));status=dict(success=False,all_fields_are_proposals=True)
  failure=dict(exception_type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
 # Binary64 values become exact rationals; clipping negative multipliers is
 # legitimate because ANY nonnegative dual vector yields a lower bound.
 z=list(map(F,map(float,point)));lam=list(map(F,map(float,multipliers)))
 progress.update(stage='exact-rational-bound',point=z,multipliers=lam,solver=status,solver_failure=failure)
 dual=exact_bound(p,z,lam);progress.update(stage='completed',exact_dual_completed=True)
 return dict(problem=p,point=z,multipliers=lam,dual=dual,solver=status,failure=failure,
  seconds=time.perf_counter()-tick,nodes=n,nonnegative_dual_clipping=True)
