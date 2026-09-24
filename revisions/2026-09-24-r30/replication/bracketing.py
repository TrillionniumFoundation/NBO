"""Matched-precision classical bracketing against the inherited scalar poll.
Both solvers share the identical validated oracle and concavity audit. Setup
is charged to each standalone use, not silently amortized away.
"""
import sys,json,time
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/2026-09-24-r28/replication'))
import slice as s
OUT=Path(__file__).resolve().parents[1]/'results/bracketing.json'

def main():
 rows=[]
 for k in (F(1,2),F(2)):
  o=s.Oracle(k);begin=time.perf_counter();smooth=o.smoothness();audit=time.perf_counter()-begin
  # Matched target on projected gradient, not matched number of iterations.
  target=F(1,200);calls0=o.calls;start=time.perf_counter();a,b=F(-1,5),F(1,5)
  ga,gb=o.evaluate(a,1),o.evaluate(b,1);history=[]
  if gb.lo>0: x=b;kind='upper-face';bound=0.
  elif ga.hi<0:x=a;kind='lower-face';bound=0.
  else:
   kind='interior'
   for it in range(100):
    x=(a+b)/2;g=o.evaluate(x,1);history.append({'a':str(a),'b':str(b),'x':str(x),'gradient':g.pair()})
    bound=max(abs(float(g.lo)),abs(float(g.hi)))
    if bound<=float(target):break
    if g.lo>0:a=x
    elif g.hi<0:b=x
    else:raise ArithmeticError('oracle width prevents the requested derivative decision')
   else:raise ArithmeticError('bracket cap reached')
  derivative_seconds=time.perf_counter()-start;derivative_calls=o.calls-calls0
  start=time.perf_counter();xpoll=F(0);polls=[]
  for h in (F(1,25),F(1,50),F(1,100),F(1,200)):
   xpoll,rec=s.poll(o,h,xpoll,smooth['lipschitz_gradient_bound']);polls.append(rec)
  poll_seconds=time.perf_counter()-start
  rows.append({'k':str(k),'setup_seconds':o.setup_seconds,'concavity_audit_seconds':audit,
   'strong_concavity_lower':smooth['strong_concavity_lower'],
   'derivative_bracket':{'theta':str(x),'kind':kind,'projected_gradient_upper':bound,'oracle_calls':derivative_calls,'search_seconds':derivative_seconds,'history':history},
   'poll':{'theta':str(xpoll),'projected_gradient_upper':polls[-1]['projected_gradient_tau1_bound'],
   'oracle_calls':sum(p['oracle_calls'] for p in polls),'search_seconds':poll_seconds,'meshes':polls},
   'scope':'same central restart and scalar class as R28; no claim about active-boundary concavity or original full domain'})
  print(k,'bracket calls',derivative_calls,'poll calls',sum(p['oracle_calls'] for p in polls),flush=True)
 OUT.write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
