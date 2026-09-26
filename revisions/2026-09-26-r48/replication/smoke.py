"""Development-only tests. No holdout model is generated here."""
from fractions import Fraction as F
import itertools,json,copy
import core,check
n,T,m=2,3,3
P=[[[[F(3,4),F(1,4)],[F(1,2),F(1,2)],[F(1,4),F(3,4)]] for i in range(n)] for t in range(T)]
r=[[[F(i)-F(a,8) for a in range(m)] for i in range(n)] for t in range(T)]
k=[[[F(0) if a==0 else F(1)+F(i,4) for a in range(m)] for i in range(n)] for t in range(T)]
d=dict(n=n,T=T,m=m,beta=F(7,8),epsilon=F(1,20),P=P,r=r,k=k,g=[F(0),F(1,2)],nu=[F(2,3),F(1,3)],name='development-only')
results=[]
for method in ['direct','price']:
 out=core.run(d,method,seconds=3,nodes=9); raw=core.enc(out); result=check.verify(raw,core.enc(d)); results.append(result)
 bad=copy.deepcopy(raw);bad['upper']='0'
 try: check.verify(bad);raise RuntimeError('forgery accepted')
 except AssertionError: pass
print(json.dumps(results,indent=2))
