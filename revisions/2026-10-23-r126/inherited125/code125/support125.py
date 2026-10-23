"""Standard-library rational checker for full original-support interpolation.

This is an algebraic witness checker, not a conic solver and not a claimed
computational improvement over the original-economy conventional controls.
"""
from fractions import Fraction as F

def phi(K,v,left,right):
 K,v,left,right=map(F,(K,v,left,right))
 if K<0 or left>right:raise ValueError('Invalid truncated quadratic conjugate')
 t=max(left,min(right,v/K)) if K else (right if v>=0 else left)
 return v*t-K*t*t/2,t

def verify_interpolation(A,mu,L,nodes,supports):
 A,mu,L=map(F,(A,mu,L));K=L-mu
 if not 0<mu<=L or A<=0:raise ValueError('Invalid original curvature')
 ns=[tuple(map(F,n)) for n in nodes]
 if not ns or any(not 0<=x<=A for x,f,g in ns):raise ValueError('Invalid nodes')
 residuals=[]
 for (x,f,g),(y,h,k) in zip(ns,ns[1:]):
  d=k-g;t=y-x
  if t<=0:raise ValueError('Nodes must be strictly increasing')
  residuals.extend((d,K*t-d))
  if K:
   area=h-f-g*t
   residuals.extend((area-d*d/(2*K),d*t-d*d/(2*K)-area))
  else:residuals.extend((-(h-f-g*t)**2,-d*d))
 raw=[]
 for support in supports:
  a,W,p,pl,pu=map(F,support)
  if not 0<=a<=A or not pl<=p<=pu:raise ValueError('Unshared or infeasible original support slope')
  slope=p-mu*a;constant=W-p*a+mu*a*a/2
  for x,f,g in ns:
   value,t=phi(K,slope-g,-x,A-x)
   gap=f-(constant+slope*x)-value
   raw.append(dict(anchor=a,node=x,shared_slope=p,phi=value,maximizing_offset=t,slack=gap))
   residuals.append(gap)
 return dict(feasible=all(v>=0 for v in residuals),minimum_slack=min(residuals) if residuals else F(0),constraints=len(residuals),raw_support_constraints=raw)

def residual_lower_bound(c,z,constraint_values,constraint_gradients,multipliers,box_lower,box_upper):
 """Exact convex Lagrangian box correction for f_j(z)<=0, lambda_j>=0."""
 c,z=tuple(map(F,c)),tuple(map(F,z));lam=tuple(map(F,multipliers))
 if any(v<0 for v in lam):raise ValueError('Negative dual multiplier')
 if not len(lam)==len(constraint_values)==len(constraint_gradients):raise ValueError('Dual dimensions')
 lo,hi=tuple(map(F,box_lower)),tuple(map(F,box_upper))
 if not(len(c)==len(z)==len(lo)==len(hi)) or any(a>b for a,b in zip(lo,hi)):raise ValueError('Finite box required')
 value=sum(a*b for a,b in zip(c,z))+sum(a*F(b) for a,b in zip(lam,constraint_values))
 gradient=[c[i]+sum(a*F(g[i]) for a,g in zip(lam,constraint_gradients)) for i in range(len(z))]
 correction=sum(min(g*(a-v),g*(b-v)) for g,v,a,b in zip(gradient,z,lo,hi))
 return value+correction
