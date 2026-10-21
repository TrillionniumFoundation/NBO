"""Boundary-aware original-marginal recovery and paid safe policy improvement.

No original economic value or actor is computed on import. Configure only after
F verification. All decisions apply to the original continuous nested AVaR Q.
"""
from __future__ import annotations
from contextlib import contextmanager
from fractions import Fraction as F
from pathlib import Path
import sys,time,traceback
import numpy as np
from common122 import R121,plain

lab=kern=econ=quad=cont=I=up=None
DELTA=F(15,16*2**20)
MU=F(2)


def configure():
 global lab,kern,econ,quad,cont,I,up
 sys.path.insert(0,str(R121/'code121'))
 import labels121
 lab=labels121;kern=lab.kern;econ=lab.econ;quad=lab.quad;cont=lab.cont;I=lab.I;up=lab.up


def enriched_certificate(x,a,alpha,bins=128):
 """The inherited certificate arithmetic, exposing its already-paid support.

Uq is recomputed without the *known separate* future-policy allowance; no
arbitrary interval subtraction is called an optimized-continuation upper bound.
"""
 x,a=I(x).checked(),I(a).checked()
 mids,edges=cont.shock_mesh(bins)
 mid=quad.terminal_certificate(econ.transition(x,a,I(mids)),alpha)
 end=quad.terminal_certificate(econ.transition(x,a,I(edges)),alpha)
 lr=econ.discrete_avar_interval(I(mid['lower']),alpha)
 ur=econ.discrete_avar_interval(I(quad.endpoint_mixture(end['upper'])),alpha)
 base=econ.S(x)+econ.action_cost(a)
 costs=I((base+econ.BETA*lr).lo,(base+econ.BETA*(ur+econ.TERMINAL_TOL)).hi).checked()
 weights=econ.tail_weights(mid['lower'],alpha)
 b,_=econ.exposures(x.lo.shape[-1])
 witness=base+econ.BETA*econ.weighted_sum(I(mid['lower']),weights)
 slope=econ.action_grad(a)+econ.BETA*econ.weighted_sum((mid['slope']*b).sum(),weights)
 optimum=econ.quadratic_minimum_lower(I(witness.lo),slope,a,econ.capacity(x))
 loss=up(costs.hi-optimum)
 if np.any(loss<0):raise ArithmeticError('Original optimum exceeds feasible policy upper bound')
 econ.count('r96_midpoint_terminal_rows',mid['lower'].size);econ.count('r96_endpoint_terminal_rows',end['upper'].size);econ.count('r96_original_action_certificates',a.lo.size)
 uq=(base+econ.BETA*ur).hi
 return dict(lower=costs.lo,upper=costs.hi,optimum_lower=optimum,loss=loss,width=up(costs.hi-costs.lo),bins=bins,
             maximum_terminal_gap=float(max(np.max(mid['gap']),np.max(end['gap']))),
             support_anchor_lower=witness.lo,support_slope_lower=slope.lo,support_slope_upper=slope.hi,
             original_q_upper=uq,original_action=a.lo.copy(),original_state=x.lo.copy(),
             support_curvature=2,full_support_continuous_risk=True)


def scalar_certificate(c):
 return {k:(float(v[0]) if isinstance(v,np.ndarray) and v.shape==(1,) else plain(v)) for k,v in c.items()}


@contextmanager
def capture_support(records):
 old=quad.certificate
 def wrapper(x,a,alpha,bins=128):
  c=enriched_certificate(x,a,alpha,bins)
  records.append(dict(alpha=alpha,**scalar_certificate(c)))
  return c
 quad.certificate=wrapper
 try:yield
 finally:quad.certificate=old


def _radius(e,k,available):
 """Any positive feasible displacement is valid; exact finite dyadic minimization."""
 if available<=0:return None
 hs={available}
 hs.update(F(1,2**j) for j in range(2,41) if F(1,2**j)<=available)
 h=min(hs,key=lambda z:(e/z+k*z/2,z))
 return {'h':h,'radius':e/h+k*h/2}


def recover(c,state,alpha):
 a=F(c['original_action']);cap=F(1,8)+sum(map(F,state))/16
 w=F(c['support_anchor_lower']);u=F(c['original_q_upper']);e=u-w
 if e<0 or not 0<=a<=cap:raise ArithmeticError('Invalid support anchor or original action')
 L=lab.smoothness_rational(alpha)['L_action'];k=L-MU
 right=_radius(e,k,cap-a);left=_radius(e,k,a)
 lower=max(F(-7),F(c['support_slope_lower'])-right['radius']) if right else F(-7)
 upper=min(F(7),F(c['support_slope_upper'])+left['radius']) if left else F(7)
 if lower>upper:raise ArithmeticError('Empty sound original derivative interval')
 return dict(action=a,capacity=cap,anchor_gap_upper=e,lower=lower,upper=upper,L=L,mu=MU,
             right_radius=right,left_radius=left,global_gradient_cap=7,
             missing_feasible_side_uses_proved_global_cap=True)


def constrained_regret(g):
 a,A,mu=g['action'],g['capacity'],g['mu']
 candidates=[]
 for z in (g['lower'],g['upper']):
  d=max(-a,min(A-a,-z/mu));candidates.append(-z*d-mu*d*d/2)
 return max(F(0),*candidates)


def proposal(g,safe_capacity,fraction=F(1)):
 a,A,L=g['action'],F(safe_capacity),g['L']
 if g['upper']<0:d=min(A-a,-g['upper']/L)
 elif g['lower']>0:d=max(-a,-g['lower']/L)
 else:d=F(0)
 raw=a+fraction*d
 # The returned action is the actual feasible 30-bit dyadic, not an ideal step.
 b=F(max(0,min(int(raw*2**30),int(A*2**30))),2**30)
 d=b-a
 model_upper=max(g['lower']*d,g['upper']*d)+L*d*d/2
 return dict(candidate=b,displacement=d,fraction=fraction,robust_original_q_gain_lower=-model_upper,
             original_policy_gain_lower=-model_upper-DELTA,
             unchanged_action=(b==a))


def directed_float(q,upper):
 v=float(q)
 if (upper and F(v)<q) or (not upper and F(v)>q):v=float(np.nextafter(v,np.inf if upper else -np.inf))
 return v


def candidate_certificate(c,g,p,old_optimum):
 """Certify candidate without evaluating any Bellman primitive at it."""
 d=p['displacement'];w=F(c['support_anchor_lower']);u=F(c['original_q_upper'])
 pl,pu=F(c['support_slope_lower']),F(c['support_slope_upper'])
 model_upper=-p['robust_original_q_gain_lower']
 lo=w+min(pl*d,pu*d)+d*d
 hi=u+model_upper+DELTA
 minima=[]
 for z in (pl,pu):
  t=max(-g['action'],min(g['capacity']-g['action'],-z/2))
  minima.append(w+z*t+t*t)
 optimum=max(min(minima),F(c['optimum_lower']),F(old_optimum))
 if hi<lo or hi<optimum:raise ArithmeticError('Contradictory reused candidate interval')
 lower=directed_float(lo,False);upper=directed_float(hi,True);bound=directed_float(optimum,False)
 loss=float(up(upper-bound));width=float(up(upper-lower))
 return dict(lower=lower,upper=upper,optimum_lower=bound,loss=loss,width=width,
   exact_policy_lower=str(lo),exact_policy_upper=str(hi),exact_optimum_lower=str(optimum),
   derived_without_candidate_economic_queries=True,
   qualified=loss<=1/256 and width<=1/8192,
   formula='Q upper plus robust smooth model plus one future allowance; quadratic support lower and common all-action optimum lower')


def service(state,alpha,model,name):
 if name not in ('control','recycled','adaptive'):raise ValueError('Undeclared service')
 tick=time.perf_counter();before=econ.COUNTS.copy();captured=[];attempts=[];paid_refinement_levels_started=[]
 if name=='control':base=lab.service(state,alpha,model)
 else:
  with capture_support(captured):base=lab.service(state,alpha,model)
 baseline=base['row'];a=float(baseline['action']);selected=dict(baseline)
 reason='control';accepted=False;gain=F(0);candidate_rejected=False
 enhancement_failure=None
 try:
  if name!='control':
   matches=[r for r in captured if r['original_action']==a and r['alpha']==alpha]
   if not matches:reason='exact-fallback-has-no-recyclable-quadratic-support'
   else:
    cert=matches[-1];x=np.asarray(state,float)[None,:]
    safe_cap=float(np.floor(econ.capacity(I(x)).lo[0]*2**30)/2**30)
    levels=(None,) if name=='recycled' else (None,256,512)
    for level in levels:
     if level is not None:
      if level<=cert['bins']:continue
      paid_refinement_levels_started.append(level)
      with kern.backend(True):fresh=enriched_certificate(x,np.array([a]),alpha,level)
      cert=scalar_certificate(fresh)
     g=recover(cert,state,alpha)
     record=dict(stage='recycled' if level is None else 'paid-precision-refinement',bins=cert['bins'],certificate=cert,gradient=g,proposal_capacity=safe_cap,
                 remaining_original_q_gain_upper=constrained_regret(g),candidate_menu=[])
     attempts.append(record);eligible=[]
     for fraction_index,fraction in enumerate((F(1),F(1,2),F(1,4),F(1,8),F(1,16),F(1,32))):
      p=proposal(g,safe_cap,fraction);entry=dict(fraction_index=fraction_index,proposal=p)
      record['candidate_menu'].append(entry)
      if p['unchanged_action']:
       entry['reason']='unchanged-action'
      elif p['original_policy_gain_lower']<=0:
       entry['reason']='future-policy-allowance-not-separated'
      else:
       new=candidate_certificate(cert,g,p,baseline['original_optimum_lower'])
       entry.update(candidate_certificate=new,candidate_qualified=new['qualified'])
       if new['qualified']:eligible.append((p,entry,new))
       else:candidate_rejected=True
     if eligible:
      p,entry,new=min(eligible,key=lambda item:(-item[0]['original_policy_gain_lower'],item[0]['candidate'],item[1]['fraction_index']))
      record['selected_fraction_index']=entry['fraction_index']
      b=float(p['candidate']);accepted=True;gain=p['original_policy_gain_lower'];reason='strict-original-policy-descent-certified'
      selected.update(action=b,action_hex=b.hex(),complete_policy_lower=new['lower'],complete_policy_upper=new['upper'],
        original_optimum_lower=new['optimum_lower'],certified_regret_upper=new['loss'],
        action_distance_upper=float(up(np.sqrt(new['loss']))),
        **{k:new[k] for k in ('lower','upper','optimum_lower','loss','width')})
      break
     reason='no-qualified-strict-improvement-in-frozen-six-step-menu'
     if constrained_regret(g)<=DELTA:
      reason='original-q-potential-no-larger-than-future-allowance';break
 except (ArithmeticError,np.linalg.LinAlgError) as exc:
  enhancement_failure={'exception_type':type(exc).__name__,'exception':str(exc),'traceback':traceback.format_exc(),'all_partial_attempts':plain(attempts),'failed_elapsed_seconds':time.perf_counter()-tick}
  selected=dict(baseline);accepted=False;gain=F(0);reason='recorded-enhancement-numerical-failure-retain-completed-incumbent'
 selected.update(enhancement_numerical_failure=enhancement_failure,service=name,baseline_action=a,baseline_action_hex=a.hex(),baseline_lower=baseline['complete_policy_lower'],baseline_upper=baseline['complete_policy_upper'],
   baseline_optimum_lower=baseline['original_optimum_lower'],baseline_first_proposal_action=baseline['first_proposal_action'],
   accepted_improvement=accepted,certified_policy_gain_lower=str(gain),candidate_rejected=candidate_rejected,
   improvement_stop=reason,refinement_count=sum(r['stage']=='paid-precision-refinement' for r in attempts),
   paid_refinement_levels_started=paid_refinement_levels_started,paid_refinement_attempt_count=len(paid_refinement_levels_started),
   extra_candidate_economic_queries=0,
   candidate_algebra_attempts=sum(len(r['candidate_menu']) for r in attempts),
   candidate_bound_attempts=sum('candidate_certificate' in z for r in attempts for z in r['candidate_menu']),
   refused_candidate_bound_attempts=sum('candidate_certificate' in z and not z['candidate_qualified'] for r in attempts for z in r['candidate_menu']),
   baseline_qualification_attempts=base['attempts'],support_attempts=plain(attempts),
   initial_support_certificates=captured,baseline_actor_trace=base['actor_trace'],
   complete_service_seconds=time.perf_counter()-tick,counts=lab.inherited.base.counter_delta(before),
   safe_gain_scope='same-state original implemented future policy; no future-policy derivative assumed',
   raw_proposal_kept=baseline['first_proposal_action'])
 return plain(selected)
