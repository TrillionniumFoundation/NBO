"""Frozen simultaneous inference for new 32-state R122 policies.

Exact binomial inversions and rational Taylor witnesses authorize reported
bounds. Numerical endpoint uncertainty is retained; no sample is replaced.
"""
from __future__ import annotations
import argparse,math
from functools import lru_cache
from pathlib import Path
from fractions import Fraction as F
from common122 import *
TAU=F(1,256)
SAFE_RADIUS=13*TAU/32
SIGNED_RADIUS=13*TAU/16
THRESHOLDS=(F(1,2**24),F(1,2**20))
EVENT_DELTA=F(1,23200)


def require(c,m):
 if not c:raise ArithmeticError(m)


def binomial_small(p,k):
 c,d=p.numerator,p.denominator
 total=sum(math.comb(N,j)*c**j*(d-c)**(N-j) for j in range(k,N+1))
 return total*EVENT_DELTA.denominator<=EVENT_DELTA.numerator*d**N


@lru_cache(maxsize=None)
def cp(k):
 if k==0:return {'successes':0,'lower':F(0),'inversion_upper':F(0)}
 lo,hi=F(0),F(1)
 for _ in range(48):
  mid=(lo+hi)/2
  if binomial_small(mid,k):lo=mid
  else:hi=mid
 require(binomial_small(lo,k) and not binomial_small(hi,k),'Exact binomial bracket')
 return {'successes':k,'lower':lo,'inversion_upper':hi,'delta':EVENT_DELTA,'bisections':48}


def radius_witness():
 exponent=2*N*(SAFE_RADIUS/TAU)**2
 require(exponent==2*N*(SIGNED_RADIUS/(2*TAU))**2==F(169,16),'Declared exact Hoeffding exponent')
 exp_lower=sum(exponent**j/math.factorial(j) for j in range(31))
 require(exp_lower>23200,'Exact exponential Taylor lower bound for all intervals')
 require(116*(2/exp_lower)<F(1,100),'Safe mean family failure allocation')
 require(348*(2/exp_lower)<F(3,100),'Signed mean family failure allocation')
 require(232*EVENT_DELTA==F(1,100),'Safe event family failure allocation')
 return {'exponent':exponent,'exp_lower':exp_lower,'Taylor_degree':30,'safe_radius':SAFE_RADIUS,'signed_radius':SIGNED_RADIUS,'mean_safe_failure_at_most':F(1,100),'event_failure_at_most':F(1,100),'mean_signed_failure_at_most':F(3,100),'joint_failure_at_most':F(1,20),'independent_state_units':N}


def main():
 p=argparse.ArgumentParser();p.add_argument('--source-commit',required=True);p.add_argument('--primary',required=True,type=Path);p.add_argument('--independent',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
 out,initial,tick=start(a.output,'statistics',{'claimed_source_commit':a.source_commit})
 try:
  source=verify_source(a.source_commit);dump(out/'VERIFIED_SOURCE122.json',source)
  raw,binding=validated_primary(a.primary,a.source_commit);evaluated=rows(a.independent/'COMPARISONS122.jsonl');pmap={key(r):r for r in raw};imap={key(r):r for r in evaluated}
  require(len(raw)==len(evaluated)==len(pmap)==len(imap)==len(identities()) and set(pmap)==set(imap)==identities(),'Complete original fixed catalogue')
  independent_inputs=json.loads((a.independent/'INPUTS122.json').read_text())
  require(independent_inputs['primary_sha256']==digest(a.primary/'records122.jsonl') and independent_inputs['primary_state_binding']==binding,'Independent evidence binds the identical original primary')
  for r in evaluated:
   require(r['source_commit']==a.source_commit and r['state_commit']==binding['state_commit'] and r['actor_commit']==ACTOR_COMMIT,'Independent scientific identities agree')
   require(r['original_action_hex']==pmap[key(r)]['action_hex'] and r['state_hex']==pmap[key(r)]['state_hex'],'Independent policy/state identity agrees')
  dump(out/'INPUTS122.json',{'primary_state_binding':binding,'independent_inputs_sha256':digest(a.independent/'INPUTS122.json'),'independent_source_receipt_sha256':digest(a.independent/'VERIFIED_SOURCE122.json'),'primary_sha256':digest(a.primary/'records122.jsonl'),'independent_sha256':digest(a.independent/'COMPARISONS122.jsonl'),'primary_states':N})
  dump(out/'RADIUS_WITNESS122.json',radius_witness())
  safe_count=0;signed_count=0
  for i,b,arm,loss in catalog():
   for service in ('recycled','adaptive'):
    ids=[(i,j,b,arm,loss,service) for j in range(N)];bounds=[];certified=[]
    for ident in ids:
     d=imap[ident];g=F(d['theorem_gain_lower']);lo=max(g,F(d['independent_gain_lower']),F(0));hi=min(TAU,F(d['independent_gain_upper']))
     require(F(0)<=lo<=hi<=TAU,'Proof and independent gain enclosure intersection')
     bounds.append((lo,hi));certified.append(g)
    ml,mh=sum(l for l,h in bounds)/N,sum(h for l,h in bounds)/N
    events=[]
    for threshold in THRESHOLDS:
     event=cp(sum(g>=threshold for g in certified));events.append({'threshold':threshold,**event,'mean_gain_lower_from_event':threshold*event['lower']})
    pl=max(F(0),ml-SAFE_RADIUS,*[e['mean_gain_lower_from_event'] for e in events]);pu=min(TAU,mh+SAFE_RADIUS)
    require(pl<=pu,'Joint population gain interval order')
    result=dict(index=i,budget=b,arm=arm,loss=loss,service=service,n=N,sample_gain_lower=ml,sample_gain_upper=mh,population_gain_lower=pl,population_gain_upper=pu,
     hoeffding_radius_upper=SAFE_RADIUS,simultaneous_family_size=116,delta=F(1,100),support=[F(0),TAU],threshold_events=events,
     observed_positive_certified_gains=sum(g>0 for g in certified),source_proof_and_independent_intersection=True,
     raw_independent_sample_gain_lower=sum(F(imap[k]['independent_gain_lower']) for k in ids)/N,
     raw_independent_sample_gain_upper=sum(F(imap[k]['independent_gain_upper']) for k in ids)/N,
     joint_failure_at_most=F(1,20),adaptive_refinement_does_not_change_independent_state_count=True)
    append(out/'STATS122.jsonl',result);safe_count+=1
   for service in SERVICES:
    for comparator in ('online-control','quadratic-value-control'):
     ck=(i,0,'online','online','control') if comparator=='online-control' else (i,b if b else 5,'quadratic','value','control')
     bounds=[]
     for j in range(N):
      k=(i,j,b,arm,loss,service);ref=(ck[0],j,ck[1],ck[2],ck[3],ck[4]);z,c=imap[k],imap[ref]
      if pmap[k]['action_hex']==pmap[ref]['action_hex']:lo=hi=F(0)
      else:
       lo=max(-TAU,F(c['independent_policy_lower'])-F(z['independent_policy_upper']))
       hi=min(TAU,F(c['independent_policy_upper'])-F(z['independent_policy_lower']))
      require(-TAU<=lo<=hi<=TAU,'Paired signed original policy support')
      bounds.append((lo,hi))
     ml,mh=sum(l for l,h in bounds)/N,sum(h for l,h in bounds)/N
     identity=(i,b,arm,loss,service)==ck
     pl,pu=(F(0),F(0)) if identity else (max(-TAU,ml-SIGNED_RADIUS),min(TAU,mh+SIGNED_RADIUS))
     append(out/'SIGNED_COMPARISONS122.jsonl',dict(index=i,budget=b,arm=arm,loss=loss,service=service,comparator=comparator,comparator_key=ck,n=N,
       sample_gain_lower=ml,sample_gain_upper=mh,population_gain_lower=pl,population_gain_upper=pu,hoeffding_radius_upper=SIGNED_RADIUS,
       exact_identical_method=identity,simultaneous_family_size=348,delta=F(3,100),support=[-TAU,TAU],joint_failure_at_most=F(1,20)))
     signed_count+=1
  require(safe_count==116 and signed_count==348,'Prospective inference family complete')
  finish(out,initial,tick,{'safe_mean_intervals':safe_count,'threshold_event_bounds':232,'signed_mean_intervals':signed_count,'joint_failure_at_most':F(1,20),'actual_state_units':N})
 except BaseException:fail(out,tick);raise

if __name__=='__main__':main()
