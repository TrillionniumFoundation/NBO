"""Independent interval certificate for original-payoff time-control policies.
No Euler paths, Brownian-bridge approximation, or learned critic is used.
Gaussian polynomial moments are integrated over outward time rectangles; an
explicit maximal-inequality bound accounts for the exact first preference exit.
"""
from __future__ import annotations
import json,pathlib,time,math,argparse
import numpy as np
from bernstein import I,iv,bounds
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=ROOT/'revisions/2026-09-22-r9/results'
DN=-np.inf;UP=np.inf

def point(x):
 a=np.asarray(x,dtype=float);return np.stack([a,a],axis=-1)
def around(x):return np.asarray(bounds(x),dtype=float)
def plus(a,b):
 return np.stack([np.nextafter(a[...,0]+b[...,0],DN),np.nextafter(a[...,1]+b[...,1],UP)],-1)
def minus(a,b):return plus(a,np.stack([-b[...,1],-b[...,0]],-1))
def times(a,b):
 q=np.stack([a[...,i]*b[...,j] for i,j in [(0,0),(0,1),(1,0),(1,1)]],-1)
 return np.stack([np.nextafter(q.min(-1),DN),np.nextafter(q.max(-1),UP)],-1)
def sum_out(a):
 a=np.asarray(a)
 while len(a)>1:
  n=len(a)//2;z=plus(a[:2*n:2],a[1:2*n:2]);a=np.vstack([z,a[-1:]]) if len(a)%2 else z
 return a[0]
def coeffs(c,M=80,K=10):
 L=-iv.ln(I(float(c)));ex=iv.exp(L);b=[]
 for n in range(M+K+1):
  s=I(0)
  for j in range(max(0,n-M),min(K,n)+1):s+=L**j/math.factorial(j)*(-1)**(n-j)
  b.append(-ex*s)
 rg=I('.8')**(M+1)/I('.2')
 re=iv.exp(I('.8')*L)*(I('.8')*L)**(K+1)/math.factorial(K+1)
 err=ex*(iv.exp(I('.8')*L)*rg+I(5)*re)
 return b,err

def discount(t):
 # Thirteen-term Taylor polynomial, plus a rigorous analytic remainder.
 a=point(np.zeros(t.shape[:-1]))
 for j in range(12,-1,-1):a=plus(times(a,t),around((-I('.04'))**j/math.factorial(j)))
 e=bounds(iv.exp(I('.04'))*I('.04')**13/math.factorial(13))[1]
 return plus(a,np.array([-e,e]))

def run(tag,resolutions=(64,256,1024)):
 start=time.perf_counter();p=json.loads((OUT/f'actor_{tag}.json').read_text());c=p['c'];th=p['theta'];k=p['k'];n=len(c)
 assert all(.05<=v<=.8 for v in c) and all(0<=v<=.2 for v in th) and all(v==0 for v in p['p'])
 debt=I(0);mu=I(0);B=I(0);mleft=[]
 for j in range(n):
  mleft.append(mu);mu+=I(float(th[j]))/n
  debt+=I(float(c[j]))*(iv.exp(-I('.02')*j/n)-iv.exp(-I('.02')*(j+1)/n))/I('.02')
  B+=I(float(th[j]))**2/2*(iv.exp(-I('.04')*j/n)-iv.exp(-I('.04')*(j+1)/n))/I('.04')
 xT=iv.exp(I('.02'))*(I('1.25')-debt);assert bounds(xT)[0]>.5
 coeff=[coeffs(v) for v in c];N=len(coeff[0][0]);delta=max(bounds(e)[1] for _,e in coeff)
 moments=[I(1),I('.2')]
 for j in range(2,2*N-1):moments.append(I('.2')*moments[-1]+(j-1)*I('.0025')*moments[-2])
 poly_norm=I(0)
 for j in range(N):
  a=max(max(abs(v) for v in bounds(cc[j])) for cc,_ in coeff)
  poly_norm+=I(a)*iv.sqrt(moments[2*j])
 prob=2*iv.exp(-I(72));sqrtp=iv.sqrt(prob)
 Gnorm=I('.02')*iv.sqrt(moments[4])+I('.1')*abs(iv.ln(xT))
 exit_error=sqrtp*(poly_norm+Gnorm)+prob*(I('.02')*k+I('8.1'))
 approximation_error=I(delta)*(1-iv.exp(-I('.04')))/I('.04')+exit_error
 terminal=iv.exp(-I('.04'))*(-I('.02')*(mu**2+I('.0025'))+I('.1')*iv.ln(xT))
 rows=[]
 for cells in resolutions:
  clock=time.perf_counter();pieces=[]
  for slab in range(n):
   il=slab*cells+np.arange(cells);den=n*cells
   t=np.stack([np.nextafter(il/den,DN),np.nextafter((il+1)/den,UP)],-1);t[:,0]=np.maximum(t[:,0],0.)
   local=minus(t,around(I(slab)/n));local[:,0]=np.maximum(0,local[:,0])
   mean=plus(around(mleft[slab]),times(point(th[slab]),local));mean[:,0]=np.maximum(0,mean[:,0])
   var=times(around(I('.0025')),t);var[:,0]=np.maximum(0,var[:,0])
   mom0=point(np.ones(cells));mom1=mean
   value=plus(times(around(coeff[slab][0][0]),mom0),times(around(coeff[slab][0][1]),mom1))
   for j in range(2,N):
    mom=plus(times(mean,mom1),times(point(j-1),times(var,mom0)))
    value=plus(value,times(around(coeff[slab][0][j]),mom));mom0,mom1=mom1,mom
   value=minus(value,around(I(k)*I(float(th[slab]))**2/2))
   mass=times(times(value,discount(t)),around(I(1)/den));pieces.append(sum_out(mass))
  total=plus(sum_out(np.array(pieces)),around(terminal));e=bounds(approximation_error)[1]
  total=plus(total,np.array([-e,e]));row={'cells_per_slab':cells,'time_rectangles':cells*n,'policy_value_interval':total.tolist(),'width':float(np.nextafter(total[1]-total[0],UP)),'seconds':time.perf_counter()-clock}
  rows.append(row);print(tag,row,flush=True)
 binterval=[bounds(B-I('.02')*prob)[0],bounds(B)[1]]
 result={'k':k,'tag':tag,'initial':[0,2,1.25],'original_payoff':True,'policy_source':f'actor_{tag}.json',
  'records':rows,'terminal_wealth_interval':bounds(xT),'adjustment_budget_interval':binterval,
  'exit_probability_upper':bounds(prob)[1],'exit_payoff_correction_upper':bounds(exit_error)[1],
  'uniform_utility_polynomial_error':delta,'polynomial_degree':N-1,'total_seconds':time.perf_counter()-start,
  'arithmetic':'mpmath.iv constants; outward binary64 operations and pairwise outward reductions',
  'scope':'continuous stopped original policy payoff and expenditure, not a claim of optimality'}
 (OUT/f'policy_certificate_{tag}.json').write_text(json.dumps(result,indent=2)+'\n')
 return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--tag',default='k2');a=ap.parse_args();run(a.tag)
