"""Original-law action localization with separately charged integration precision.

All original economic evaluations use unchanged publicly frozen primitives.
The four services share the same completed strong R123 fused prefix. The
new branch is a separate deterministic study, never an R123 or R124B replay.
"""
from fractions import Fraction as F
import sys,time,traceback
import numpy as np
from common125 import *
sys.path.insert(0,str(R123/'code123'))
import service123 as prior
import envelope123 as env
old=prior.old

def configure():prior.configure()

def update_bracket(left,right,a,glo,ghi,mu=F(2)):
 """Exact enclosure of the constrained original q minimizer, including boundaries."""
 if not left<=right or glo>ghi or mu<=0:raise ValueError('Invalid localization data')
 a,glo,ghi=map(F,(a,glo,ghi))
 if glo>0:right=min(right,a)
 elif ghi<0:left=max(left,a)
 else:left=max(left,a-ghi/mu);right=min(right,a-glo/mu)
 if left>right:raise ArithmeticError('Sound original-gradient observations give empty bracket')
 return left,right

def q_query(state,alpha,a,n):
 with old.kern.backend(True):
  c=old.enriched_certificate(np.asarray(state,float)[None,:],np.array([float(a)]),alpha,n)
 return dict(alpha=alpha,**old.scalar_certificate(c))

def make_case(records,state,alpha,baseline):
 return env.normalize(prior.make_case(records,state,alpha,baseline))

def checked_candidate(case,b,common=None):
 c=env.candidate(case,b,'fused',common)
 # Intersect the derivative-path contrast with independently valid endpoint levels.
 a=case['incumbent'];ca=env.candidate(case,a,'fused',common)
 upper=min(c['change_upper'],c['upper']-case['delta']-ca['lower'])
 lower=max(c['change_lower'],c['lower']-(ca['upper']-case['delta']))
 if a==b:lower=upper=F(0)
 gain=F(0) if a==b else -upper-case['delta']
 c.update(change_lower=lower,change_upper=upper,gain_lower=gain)
 c['accepted']=a!=b and gain>0 and c['loss']<=TAU and c['width']<=OMEGA
 flo=prior.float_certificate(c)
 c['outward']=flo;c['accepted']=c['accepted'] and flo['qualified']
 c['target_qualified']=c['loss']<=TARGET and c['width']<=OMEGA and F(flo['loss'])<=TARGET and F(flo['width'])<=OMEGA
 return c

def final_from_candidate(baseline,c):
 r=dict(baseline);f=c['outward'];a=float(c['b'])
 r.update(action=a,action_hex=a.hex(),complete_policy_lower=f['lower'],complete_policy_upper=f['upper'],original_optimum_lower=f['optimum_lower'],certified_regret_upper=f['loss'],action_distance_upper=float(old.up(np.sqrt(f['loss']))),**f)
 return r

def service(state,alpha,model,mode):
 if mode not in MODES:raise ValueError('Undeclared service')
 start=time.perf_counter();before=old.econ.COUNTS.copy()
 base=prior.service(state,alpha,model,'fused');baseline=dict(base)
 if mode=='fused_control':
  return dict(base,service125=mode,baseline_action125=base['action'],baseline_lower125=base['complete_policy_lower'],baseline_upper125=base['complete_policy_upper'],new_queries125=[],localization125=[],new_terminal_nodes125=0,accepted125=False,gain_lower125='0',target_qualified125=base['certified_regret_upper']<=float(TARGET) and base['width']<=float(OMEGA),stop125='completed-strong-fused-control',seconds125=time.perf_counter()-start,counts125=old.lab.inherited.base.counter_delta(before))
 records=list(base['initial_support_certificates']);queries=[];history=[];candidates=[];failure=None;used=0;selected=None
 A=F(1,8)+sum(map(F,state))/16;a0=F(base['action']);left=F(0);right=A
 stop='maximum-action-centers'
 try:
  if not records:stop='completed-exact-prefix-without-original-support-ledger'
  else:
   case=make_case(records,state,alpha,baseline)
   if mode!='cold_adaptive':left=env.envelope_root(case,True);right=env.envelope_root(case,False)
   baseline_c=checked_candidate(case,a0)
   if baseline_c['target_qualified']:stop='inherited-qualified-policy-already-meets-stronger-target'
   else:
    for center in range(MAX_CENTERS):
     if left==right:stop='original-optimum-localized-to-singleton';break
     l0,r0=left,right;width=r0-l0
     a=env.rounded_action((l0+r0)/2,A)
     if a<l0:a=F(min(int(A*2**30),int(l0*2**30)+1),2**30)
     if not l0<=a<=r0:stop='action-lattice-resolution-floor';break
     levels=(512,) if mode=='warm_fixed512' else LADDER
     contracted=False
     for bins in levels:
      nodes=2*bins+1
      if used+nodes>NODE_BUDGET:stop='declared-terminal-node-budget-exhausted';break
      query=dict(center=center,action=a,bins=bins,requested_terminal_nodes=nodes,bracket_before=[l0,r0],started=True,completed=False)
      queries.append(query);used+=nodes;qt=time.perf_counter()
      c=q_query(state,alpha,a,bins);g=old.recover(c,state,alpha);records.append(c)
      left,right=update_bracket(left,right,a,g['lower'],g['upper'])
      query.update(completed=True,seconds=time.perf_counter()-qt,certificate=c,gradient=g,bracket_after=[left,right])
      case=make_case(records,state,alpha,baseline);common=env.support_minimum(case)
      cert=checked_candidate(case,a,common);candidates.append(cert)
      if cert['accepted'] and (selected is None or (-cert['gain_lower'],cert['b'])<(-selected['gain_lower'],selected['b'])):selected=cert
      target=(selected is not None and selected['target_qualified'])
      contracted=(right-left)<=width/F(2)+abs(a-(l0+r0)/2)
      query.update(target_met=target,original_gradient_resolved=(g['lower']>0 or g['upper']<0),precision_width_met=(g['upper']-g['lower']<=width),contracted=contracted)
      if target:stop='strict-original-policy-gain-and-stronger-regret-target';break
      if contracted:break
     history.append(dict(center=center,old_bracket=[l0,r0],new_bracket=[left,right],actual_action=a,rounding_error=abs(a-(l0+r0)/2),contracted=contracted))
     if selected is not None and selected['target_qualified']:break
     if stop=='declared-terminal-node-budget-exhausted':break
     if not contracted:stop='maximum-risk-precision-does-not-certify-contraction';break
 except (ArithmeticError,np.linalg.LinAlgError) as exc:
  failure=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),seconds=time.perf_counter()-start)
  stop='numerical-failure-retain-last-qualified-selection'
 # The actual last safe selection is preserved even if later work fails.
 answer=final_from_candidate(baseline,selected) if selected is not None else dict(baseline)
 answer.update(service125=mode,baseline_action125=float(a0),baseline_lower125=base['complete_policy_lower'],baseline_upper125=base['complete_policy_upper'],baseline_original_optimum_lower125=base['original_optimum_lower'],baseline_regret125=base['certified_regret_upper'],
  new_queries125=queries,localization125=history,new_terminal_nodes125=used,candidate_certificates125=candidates,accepted125=selected is not None,gain_lower125=F(0) if selected is None else selected['gain_lower'],selected_certificate125=selected,target_qualified125=answer['certified_regret_upper']<=float(TARGET) and answer['width']<=float(OMEGA),stop125=stop,failure125=failure,final_q_optimizer_bracket125=[left,right],
  complete_fused_prefix125=base,seconds125=time.perf_counter()-start,counts125=old.lab.inherited.base.counter_delta(before),same_original_future=True)
 return plain(answer)

def grid_service(state,alpha):
 """Strong conventional finite-action DP: all33 actions and fresh risk work."""
 tick=time.perf_counter();before=old.econ.COUNTS.copy();A=F(1,8)+sum(map(F,state))/16
 records=[];queries=[];nodes=0
 for i in range(33):
  a=env.rounded_action(A*F(i,32),A);n=128;ct=time.perf_counter();c=q_query(state,alpha,a,n);records.append(c);nodes+=2*n+1
  queries.append(dict(action=a,bins=n,certificate=c,seconds=time.perf_counter()-ct))
 def choose():
  B=max(F(c['optimum_lower']) for c in records);choices=[]
  for c in records:
   a=F(c['original_action']);lo=max(F(d['support_anchor_lower'])+min(F(d['support_slope_lower'])*(a-F(d['original_action'])),F(d['support_slope_upper'])*(a-F(d['original_action'])))+(a-F(d['original_action']))**2 for d in records)
   hi=F(c['original_q_upper'])+DELTA;loss=hi-B;width=hi-lo
   if loss<=TAU and width<=OMEGA:choices.append((hi,a,lo,B,loss,width))
  return min(choices) if choices else None
 answer=choose()
 best=min(records,key=lambda c:(c['original_q_upper'],c['original_action']))
 for n in (256,512,1024,2048):
  if answer is not None and answer[4]<=TARGET:break
  if nodes+2*n+1>NODE_BUDGET:break
  a=F(best['original_action']);ct=time.perf_counter();c=q_query(state,alpha,a,n);records.append(c);nodes+=2*n+1
  queries.append(dict(action=a,bins=n,certificate=c,seconds=time.perf_counter()-ct));answer=choose()
 if answer is None:
  # A full charged online fallback, not a silently unqualified deployed policy.
  fallback=prior.service(state,alpha,None,'fused');r=dict(fallback);fallback_used=True
 else:
  hi,a,lo,B,loss,width=answer
  flo={'lower':old.directed_float(lo,False),'upper':old.directed_float(hi,True),'optimum_lower':old.directed_float(B,False)}
  flo.update(loss=float(old.up(flo['upper']-flo['optimum_lower'])),width=float(old.up(flo['upper']-flo['lower'])))
  if flo['loss']>float(TAU) or flo['width']>float(OMEGA):raise ArithmeticError('DP outward qualification failed')
  r=dict(state=list(state),action=float(a),action_hex=float(a).hex(),complete_policy_lower=flo['lower'],complete_policy_upper=flo['upper'],original_optimum_lower=flo['optimum_lower'],certified_regret_upper=flo['loss'],action_distance_upper=float(old.up(np.sqrt(flo['loss']))),qualified=True,**flo);fallback_used=False
 r.update(service125='grid33',new_queries125=queries,new_terminal_nodes125=nodes,accepted125=False,gain_lower125='0',target_qualified125=r['certified_regret_upper']<=float(TARGET) and r['width']<=float(OMEGA),grid_fallback_used125=fallback_used,stop125='completed33-action-original-DP',seconds125=time.perf_counter()-tick,counts125=old.lab.inherited.base.counter_delta(before))
 return plain(r)
