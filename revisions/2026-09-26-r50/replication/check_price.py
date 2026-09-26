"""Uncapped occupation-flow verifier; stdlib only, no constructor imports."""
from fractions import Fraction as Q
from itertools import combinations

def verify(e,raw):
 assert e['schema']=='nbo-r50-price-audit-v1' and e['model']==raw
 n,T,m=raw['n'],raw['T'],raw['m'];b=Q(raw['beta']);eps=Q(raw['epsilon']);nu=list(map(Q,raw['nu']))
 P=[[[list(map(Q,row)) for row in state] for state in date] for date in raw['P']];r=[[[Q(z) for z in state] for state in date] for date in raw['r']];k=[[[Q(z) for z in state] for state in date] for date in raw['k']]
 assert n>0 and T>0 and m>1 and 0<b<1 and eps>0 and len(nu)==n and min(nu)>=0 and sum(nu)==1
 assert len(P)==len(r)==len(k)==T
 for t in range(T):
  assert len(P[t])==len(r[t])==len(k[t])==n
  for i in range(n):
   assert len(P[t][i])==len(r[t][i])==len(k[t][i])==m
   for a in range(m):assert len(P[t][i][a])==n and min(P[t][i][a])>=0 and sum(P[t][i][a])==1 and k[t][i][a]>=0
 V=[[Q(0)]*n for _ in range(T+1)];V[T]=list(map(Q,raw['g']));C=[[Q(0)]*n for _ in range(T+1)];J=[row[:] for row in V];J[T]=V[T][:]
 p=[[[Q(z) for z in state] for state in date] for date in e['policy']]
 def dot(x,y):return sum((a*v for a,v in zip(x,y)),Q(0))
 d=[[[Q(0)]*m for _ in range(n)] for _ in range(T)]
 for t in reversed(range(T)):
  for i in range(n):
   val=[r[t][i][a]+b*dot(P[t][i][a],V[t+1]) for a in range(m)];V[t][i]=max(val);d[t][i]=[V[t][i]-z for z in val]
   assert min(p[t][i])>=0 and sum(p[t][i])==1
   J[t][i]=dot(p[t][i],[r[t][i][a]+b*dot(P[t][i][a],J[t+1]) for a in range(m)]);assert V[t][i]-J[t][i]<=eps
   C[t][i]=dot(p[t][i],[k[t][i][a]+b*dot(P[t][i][a],C[t+1]) for a in range(m)])
 support=[i for i,z in enumerate(nu) if z];expected={tuple(s) for size in range(1,len(support)+1) for s in combinations(support,size)}
 seen=set();L=Q(0);upper=[]
 for cert in e['certificates']:
  mask=tuple(cert['mask']);assert mask in expected and mask not in seen;seen.add(mask);mu=[nu[i] if i in mask else Q(0) for i in range(n)]
  if cert['skipped'] or not cert.get('certified'):U=dot(mu,C[0])
  else:
   z={tuple(item['label']):Q(item['value']) for item in cert['occupation']};assert min(z.values(),default=Q(0))>=0
   def v(*key):return z.get(tuple(key),Q(0))
   U=Q(0)
   for t in range(T):
    for i in range(n):
     mass=sum(v('y',t,i,a) for a in range(m))
     inflow=mu[i] if t==0 else b*sum(v('y',t-1,h,a)*P[t-1][h][a][i] for h in range(n) for a in range(m))
     assert mass==inflow
     available=sum(v('y',t,i,a)*(eps-d[t][i][a]) for a in range(m))
     spending=sum(v('alpha',t,i,j) for j in range(n))+ (sum(v('gamma',t-1,h,i) for h in range(n)) if t else 0)
     assert available>=spending
     if t<T-1:
      for j in range(n):assert v('alpha',t,i,j)+v('gamma',t,i,j)>=b*eps*sum(v('y',t,i,a)*P[t][i][a][j] for a in range(m))
     U+=sum(v('y',t,i,a)*k[t][i][a] for a in range(m))
  if cert.get('certified'):
   assert U==Q(cert['occupation_upper']);U=min(U,dot(mu,C[0]))
  assert U==Q(cert['upper']);upper.append(U)
  if 'field' in cert:
   lam=[list(map(Q,row)) for row in cert['field']];assert len(lam)==T+1 and all(len(row)==n and min(row)>=0 for row in lam) and max(lam[T])==0
   u=[[Q(0)]*n for _ in range(T+1)]
   for t in reversed(range(T)):
    for i in range(n):u[t][i]=min(k[t][i][a]+lam[t][i]*(d[t][i][a]-eps)+b*sum(P[t][i][a][j]*(u[t+1][j]+eps*min(lam[t][i],lam[t+1][j])) for j in range(n)) for a in range(m))
   assert dot(mu,u[0])==Q(cert['masked_lower'])<=U
   cl=dot(nu,[max(Q(0),z) for z in u[0]]);assert cl==Q(cert['clipped_lower']);L=max(L,cl)
 assert seen==expected and L==Q(e['ideal_lower']) and max(upper)==Q(e['ideal_upper']) and L<=max(upper)
 for c in e['cap_rows']:
  lam=[list(map(Q,row)) for row in c['field']];cap=Q(c['cap']);assert all(len(row)==n and min(row)>=0 and max(row)<=cap for row in lam) and max(lam[T])==0
  u=[[Q(0)]*n for _ in range(T+1)]
  for t in reversed(range(T)):
   for i in range(n):u[t][i]=min(k[t][i][a]+lam[t][i]*(d[t][i][a]-eps)+b*sum(P[t][i][a][j]*(u[t+1][j]+eps*min(lam[t][i],lam[t+1][j])) for j in range(n)) for a in range(m))
  cl=dot(nu,[max(Q(0),z) for z in u[0]]);assert cl==Q(c['lower']) and Q(c['loss_upper'])==max(upper)-cl>=0
 return {'valid':True,'all_support_masks_covered':True,'uncapped_loss_width':str(max(upper)-L)}
