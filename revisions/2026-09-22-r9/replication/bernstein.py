"""Outward Bernstein certificates for low-degree multivariate polynomials.
Input binary64 coefficients are exact real constants. Transcendentals and
power-to-Bernstein conversion use mpmath.iv; subdivisions use outward-rounded
binary64 arithmetic, with an additional nextafter at every elementary step.
"""
from __future__ import annotations
import math,heapq,time
import numpy as np
from mpmath import iv
iv.dps=70

def I(x):return iv.mpf(x)
def bounds(x):return [np.nextafter(float(x.a),-np.inf),np.nextafter(float(x.b),np.inf)]
def zeros(n,m):return [[I(0) for _ in range(m)] for _ in range(n)]
def add(A,B,scale=1):
 n=max(len(A),len(B));m=max(len(A[0]),len(B[0]));R=zeros(n,m)
 for i in range(n):
  for j in range(m):
   if i<len(A) and j<len(A[0]):R[i][j]+=A[i][j]
   if i<len(B) and j<len(B[0]):R[i][j]+=I(scale)*B[i][j]
 return R

def mul(A,B):
 R=zeros(len(A)+len(B)-1,len(A[0])+len(B[0])-1)
 for i in range(len(A)):
  for j in range(len(A[0])):
   for k in range(len(B)):
    for l in range(len(B[0])):R[i+k][j+l]+=A[i][j]*B[k][l]
 return R

def deriv(A,axis):
 if axis==0:return [[I(i)*x for x in A[i]] for i in range(1,len(A))]
 return [[I(j)*row[j] for j in range(1,len(row))] for row in A]

def scale(A,s):return [[x*I(s) for x in row] for row in A]

def shifted_cheb(n):
 T=[[1],[ -1,2]]
 for k in range(2,n+1):
  a=[0]*(k+1)
  for j,x in enumerate(T[-1]):a[j]-=2*x;a[j+1]+=4*x
  for j,x in enumerate(T[-2]):a[j]-=x
  T.append(a)
 return T[:n+1]

def from_cheb(cc):
 cc=np.asarray(cc);Ts=shifted_cheb(max(cc.shape)-1);A=zeros(*cc.shape)
 for i in range(cc.shape[0]):
  for j in range(cc.shape[1]):
   c=I(float(cc[i,j]))
   for k,x in enumerate(Ts[i]):
    for l,y in enumerate(Ts[j]):A[k][l]+=c*x*y
 return A

def bern(A,degrees=None):
 n,m=degrees or (len(A)-1,len(A[0])-1)
 # Separable exact conversion b_ij=sum a_kl binom(i,k)/binom(n,k) binom(j,l)/binom(m,l).
 tmp=zeros(n+1,len(A[0]))
 for i in range(n+1):
  for k in range(min(i,len(A)-1)+1):
   w=I(math.comb(i,k))/math.comb(n,k)
   for l in range(len(A[0])):tmp[i][l]+=w*A[k][l]
 B=np.zeros((n+1,m+1,2))
 for i in range(n+1):
  for j in range(m+1):
   x=I(0)
   for l in range(min(j,len(A[0])-1)+1):x+=tmp[i][l]*math.comb(j,l)/math.comb(m,l)
   B[i,j]=bounds(x)
 return B

def split(B,axis):
 # B has shape (polynomials, h coefficient, u coefficient, lower/upper).
 ax=axis+1;P=np.moveaxis(B,ax,1).copy();L=np.empty_like(P);R=np.empty_like(P)
 n=P.shape[1]-1;L[:,0]=P[:,0];R[:,n]=P[:,n]
 for j in range(n):
  s=P[:,:n-j]+P[:,1:n-j+1]
  s[...,0]=np.nextafter(s[...,0],-np.inf);s[...,1]=np.nextafter(s[...,1],np.inf)
  P[:,:n-j]=s*.5
  P[:,:n-j,...,0]=np.nextafter(P[:,:n-j,...,0],-np.inf)
  P[:,:n-j,...,1]=np.nextafter(P[:,:n-j,...,1],np.inf)
  L[:,j+1]=P[:,0];R[:,n-j-1]=P[:,n-j-1]
 return np.moveaxis(L,1,ax),np.moveaxis(R,1,ax)

def certify_hamiltonian(polys,k,epsilon,max_nodes=250000):
 """polys = q, R_plus, R_minus, R_interior Bernstein enclosures."""
 threshold_lo,threshold_hi=bounds(I('.2')*I(k))
 def bound(P):
  lo=P[0,...,0].min();hi=P[0,...,1].max();v=[]
  if hi>=threshold_lo:v.append(P[1,...,1].max())
  if lo<=-threshold_lo:v.append(P[2,...,1].max())
  if lo<=threshold_hi and hi>=-threshold_hi:v.append(P[3,...,1].max())
  return max(v)
 start=time.perf_counter();seq=0;heap=[(-bound(polys),seq,0,0,polys)];visited=1
 while -heap[0][0]>epsilon and visited<max_nodes:
  neg,_,dh,du,P=heapq.heappop(heap);axis=0 if dh<=du else 1
  for Q in split(P,axis):
   seq+=1;heapq.heappush(heap,(-bound(Q),seq,dh+(axis==0),du+(axis==1),Q));visited+=1
 return {'residual_upper_bound':float(np.nextafter(-heap[0][0],np.inf)),
         'requested_residual_ceiling':epsilon,'leaf_boxes':len(heap),'visited_boxes':visited,
         'max_depth':max(x[2]+x[3] for x in heap),'seconds':time.perf_counter()-start,
         'ceiling_met':bool(-heap[0][0]<=epsilon)}

def certify_min(B,threshold,max_depth=20):
 stack=[(B[None],0)];lower=np.inf;leaves=0
 while stack:
  P,depth=stack.pop();lo=P[...,0].min()
  if lo>=threshold or depth>=max_depth:lower=min(lower,lo);leaves+=1
  else:stack.extend((Q,depth+1) for Q in split(P,depth%2))
 return float(lower),leaves
