"""Directed exact-price root brackets, including the unbounded Gaussian tail.

This finite inequality check instantiates the R23 analytic pricing theorem.
It does not retrain, re-budget, or replace any delivered experimental policy.
Run with BACKEND=mpfr in a fresh process to select MPFR throughout.
"""
from pathlib import Path
from fractions import Fraction
import json,sys,os,time
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r23'
sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r20/replication'))
import certify_stochastic as C
I,Q,exp,log,sqrt,pi=C.I,C.Q,C.exp,C.log,C.sqrt,C.pi

def sigmoid(x):return 1/(1+exp(-x))
def logit(x):return log(x/(1-x))

def bracket(d):
 n=16;R=Q(8);M=(1-exp(-Q('.02')))/Q('.02')
 target=Q(str(d['x0']))-Q('.50001')*exp(-Q('.02'))
 nu=(target-Q('.5')*M)/(Q('.3')*M)
 p=I(float((2*exp(-R.square()/2)/(R*sqrt(2*pi()))).hi))
 assert float(p.hi)<min(float(nu.lo),float((1-nu).lo))
 ell=[]
 for j,(b,s) in enumerate(zip(d['b'],d['s'])):
  t=I(float(Q(Fraction(j,n)).lo),float(Q(Fraction(j+1,n)).hi))
  lq=Q('.065')*t+Q('.3')*sqrt(t)*I(-8,8)
  ell.append(I(b)-I(s)*lq)
 lo=min(float(z.lo) for z in ell);hi=max(float(z.hi) for z in ell)
 am=I(float((logit((nu-p)/(1-p))-I(hi)-Q('.00000001')).lo))
 ap=I(float((logit(nu/(1-p))-I(lo)+Q('.00000001')).hi))
 price_upper_at_lower=Q('.5')*M+Q('.3')*M*((1-p)*sigmoid(am+I(hi))+p)
 price_lower_at_upper=Q('.5')*M+Q('.3')*M*(1-p)*sigmoid(ap+I(lo))
 lower_margin=float((target-price_upper_at_lower).lo)
 upper_margin=float((price_lower_at_upper-target).lo)
 assert lower_margin>0 and upper_margin>0,(lower_margin,upper_margin)
 zlo=float((I(lo)+am).lo);zhi=float((I(hi)+ap).hi);z=I(max(abs(zlo),abs(zhi)))
 e=exp(-z);derivative=Q('.3')*M*(1-p)*e/(1+e).square()
 assert float(derivative.lo)>0
 return {'extra_common_offset_root_interval':[float(am.lo),float(ap.hi)],'continuous_price_target_interval':[float(target.lo),float(target.hi)],'normalized_target_interval':[float(nu.lo),float(nu.hi)],'normal_tail_probability_upper':float(p.hi),'logit_compact_range':[lo,hi],'strict_lower_endpoint_price_margin':lower_margin,'strict_upper_endpoint_price_margin':upper_margin,'continuous_price_derivative_lower_on_bracket':float(derivative.lo),'arithmetic':C.BACKEND,'normal_cutoff':8,'scope':'exact continuous discounted pricing measure, not the finite proposal quadrature; an existence/conditioning enclosure, not a sharp root-error claim'}

def main():
 start=time.perf_counter();rows=[]
 files=sorted((REV/'results/crossed').glob('seed*/vertex*/*/delivered_actor.json'))
 assert len(files)==72,len(files)
 for path in files:
  d=json.loads(path.read_text());rows.append({'actor':str(path.relative_to(REV)),**bracket(d)})
 result={'status':'PASS','policies':len(rows),'arithmetic':C.BACKEND,'rows':rows,'seconds':time.perf_counter()-start,'minimum_derivative_lower':min(r['continuous_price_derivative_lower_on_bracket'] for r in rows),'minimum_endpoint_margin':min(min(r['strict_lower_endpoint_price_margin'],r['strict_upper_endpoint_price_margin']) for r in rows),'retargeted_experimental_policies':False,'theorem':'R23 exact-price budget quotient, Gaussian-tail bracket and inverse conditioning','analysis_status':'a posteriori analytic certification of every frozen R23 delivered policy'}
 (REV/'results/continuous_budget_brackets.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
