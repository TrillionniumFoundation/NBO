"""Independent standard-library arithmetic audit of R124 decision certificates.

Imports only custody and the separately written R123 rational envelope reader.
It imports no production envelope, original solver, NumPy, SciPy, or learned
representation. Original economic anchors remain premises for separate audit.
"""
from fractions import Fraction as F
import argparse,math,sys
from common124 import *
sys.path.insert(0,str(R123/'code123'))
from independent_envelopes123 import RationalCertificate
CHECKS=0

def require(ok,message):
 global CHECKS;CHECKS+=1
 if not ok:raise AssertionError(message)

def outward(q,up):
 v=float(q)
 if (F(v)<q if up else F(v)>q):v=math.nextafter(v,math.inf if up else -math.inf)
 return v

def checked_dual(engine,b,record):
 nodes=sorted({p['a'] for p in engine.payloads}|{F(0),engine.A,engine.a,b});n=len(nodes);K=engine.L-engine.mu
 lower=[max(p['W']+engine.contrast(p['a'],x)[0] for p in engine.payloads) for x in nodes]
 upper=[min(p['U']+engine.contrast(p['a'],x)[1] for p in engine.payloads) for x in nodes]
 lower += [engine._value('lower',x) for x in nodes];upper += [engine._value('upper',x) for x in nodes]
 pp=record['problem']
 require(list(map(F,pp['nodes']))==nodes,'Joint nodes differ from original paid nodes')
 require(list(map(F,pp['lower']))==lower and list(map(F,pp['upper']))==upper,'Exact derived interpolation box differs')
 require(all(l<=u for l,u in zip(lower,upper)),'Empty interpolation box')
 require(F(pp['mu'])==engine.mu and F(pp['L'])==engine.L and F(pp['K'])==K and K>0,'Original curvature mismatch')
 ai,bi=nodes.index(engine.a),nodes.index(b)
 require(pp['origin_index']==ai and pp['target_index']==bi,'Objective node identity differs')
 z=list(map(F,record['point']));lam=list(map(F,record['multipliers']))
 require(len(z)==2*n and len(lam)==4*(n-1) and all(v>=0 for v in lam),'Invalid exact point or multiplier census')
 h=z[ai]-z[bi];val=h;grad=[F(0)]*(2*n);grad[ai]+=1;grad[bi]-=1
 for i in range(n-1):
  d=nodes[i+1]-nodes[i];s=z[n+i+1]-z[n+i]-engine.mu*d
  w=z[i+1]-z[i]-z[n+i]*d-engine.mu*d*d/2
  l1,l2,l3,l4=lam[4*i:4*i+4]
  # Independently expand the combined quadratic Lagrangian block.
  val+=(l1+l2)*s*s/(2*K)+(l2-l1)*w-l2*s*d+(l4-l3)*s-l4*K*d
  ds=(l1+l2)*s/K-l2*d+l4-l3;dw=l2-l1
  grad[i]-=dw;grad[i+1]+=dw;grad[n+i]-=ds+d*dw;grad[n+i+1]+=ds
 residual=sum((r*((lo if r>=0 else hi)-v) for r,lo,hi,v in zip(grad,lower,upper,z)),F(0))
 bound=val+residual;dual=record['dual']
 for field,v in [('objective_at_point',h),('lagrangian_at_point',val),('box_residual_correction',residual),('lower_bound',bound),('contrast_upper',-bound)]:
  require(F(dual[field])==v,'Exact dual mismatch: '+field)
 require(list(map(F,dual['gradient']))==grad,'Exact dual gradient differs')
 return -bound

def reconstructed_menu(engine):
 proposals=[('fused',engine.fused_minimizer())]
 for i,p in enumerate(engine.original['payloads']):
  reduced=dict(engine.original,payloads=[p]);proposals.append(('anchor-'+str(i),RationalCertificate(reduced).fused_minimizer()))
 result=[]
 for label,point in proposals:
  for power in range(6):
   f=F(1,2**power);raw=engine.a+(point-engine.a)*f
   b=F(max(0,min(int(raw*2**30),int(engine.A*2**30))),2**30)
   result.append(dict(source=label,fraction=f,b=b,menu_index=len(result),certificate=engine.candidate(b,'fused')))
 return result

def bind_original_case(row):
 x=list(map(F,row['state']));alpha=F(row['alpha']);case=row['case'];supports=row['initial_support_certificates']
 require(len(x)==2 and all(0<=v<=1 for v in x),'Original state domain')
 require(alpha in (F(1,2),F(3,4)) and row['alpha']==(.5,.75)[row['index']],'Original risk identity')
 A=F(1,8)+sum(x)/16
 require(0<=F(row['baseline_action'])<=A and 0<=F(row['action'])<=A,'Original capacity feasibility')
 require(float(row['action']).hex()==row['action_hex'] and float(row['baseline_action']).hex()==row['baseline_action_hex'],'Actual action hex identity')
 require(0<=F(row['baseline_upper'])-F(row['baseline_lower'])<=F(1,8192),'Completed incumbent width')
 require(0<=F(row['baseline_upper'])-F(row['baseline_optimum_lower'])<=F(1,256),'Completed incumbent regret')
 if case is None:
  require(not supports or row['enhancement_failure'] is not None,'Original supports silently discarded')
  return
 beta=F(15,16);m=F(1413,128)+beta*(F(127,16)+F(19625,20480)*alpha/(1-alpha))
 L=5+beta*(F(5,16)*m+(F(4,5)*m)**2*alpha/(F(181,64)*(1-alpha)))
 for field,wanted in [('A',A),('incumbent',F(row['baseline_action'])),('mu',F(2)),('L',L),('delta',F(15,16777216)),('tau',F(1,256)),('omega',F(1,8192)),('old_optimum_lower',F(row['baseline_optimum_lower']))]:
  require(F(case[field])==wanted,'Original case identity: '+field)
 require(case.get('gradient_rule')=='r122-finite-radii' and case.get('gradient_cap')==7 and case.get('radius_indices')==[2,40],'Original derivative recovery specification')
 require(len(case['payloads'])==len(supports) and len(supports)>0,'Complete paid support census')
 for p,c in zip(case['payloads'],supports):
  require(c['original_state']==[row['state']] and F(c['alpha'])==alpha,'Support original state/risk identity')
  require(c['support_curvature']==2 and c['full_support_continuous_risk'] is True,'Original support curvature/law')
  for field,raw in [('a','original_action'),('W','support_anchor_lower'),('U','original_q_upper'),('p_lower','support_slope_lower'),('p_upper','support_slope_upper')]:
   require(F(p[field])==F(c[raw]),'Case/raw paid support mismatch: '+field)

def audit_row(row):
 require(row['qualified'] is True and row['additional_original_risk_queries']==0,'Unqualified or extra-query decision')
 require(row['lower']==row['complete_policy_lower'] and row['upper']==row['complete_policy_upper'] and row['optimum_lower']==row['original_optimum_lower'],'Returned original certificate aliases disagree')
 require(row['loss']==row['certified_regret_upper'] and row['loss']==math.nextafter(row['upper']-row['optimum_lower'],math.inf) and row['width']==math.nextafter(row['upper']-row['lower'],math.inf),'Returned outward regret/width differs from endpoints')
 bind_original_case(row)
 a=F(row['baseline_action']);b=F(row['action']);case=row['case']
 if case is None:
  require(a==b and not row['accepted_improvement'],'No-support action changed')
  require(row['complete_policy_lower']==row['baseline_lower'] and row['complete_policy_upper']==row['baseline_upper'] and row['original_optimum_lower']==row['baseline_optimum_lower'],'No-support incumbent endpoints changed');return
 engine=RationalCertificate(case)
 require(engine.a==a,'Incumbent interface mismatch')
 menu=reconstructed_menu(engine);require(len(row['full_common_menu'])<=len(menu) and (len(menu)==len(row['full_common_menu']) or row['enhancement_failure'] is not None),'Complete common menu missing without retained failure')
 distinct={}
 for actual,wanted in zip(row['full_common_menu'],menu):
  require(F(actual['b'])==wanted['b'] and actual['source']==wanted['source'] and F(actual['fraction'])==wanted['fraction'] and actual['menu_index']==wanted['menu_index'],'Frozen common menu mismatch')
  if actual['certificate'] is None:
   require(row['enhancement_failure'] is not None and actual is row['full_common_menu'][-1],'Unrecorded incomplete fused candidate');continue
  for k,target in [('change_lower','q_contrast_lower'),('change_upper','q_contrast_upper'),('gain_lower','gain_lower'),('lower','policy_lower'),('upper','policy_upper'),('optimum_lower','optimum_lower'),('loss','regret_upper'),('width','width')]:
   require(F(actual['certificate'][k])==wanted['certificate'][target],'Fused exact certificate mismatch: '+k)
 for wanted in menu:
  if wanted['b']!=a:distinct.setdefault(wanted['b'],wanted)
 chosen=sorted(distinct.values(),key=lambda r:(-r['certificate']['gain_lower'],r['b'],r['menu_index']))[:2]
 actuals=row['selected_common_menu']
 require(len(actuals)==len(chosen) or row['enhancement_failure'] is not None,'Incomplete selected menu without failure')
 eligible=[]
 for actual,wanted in zip(actuals,chosen):
  require(F(actual['b'])==wanted['b'] and actual['menu_index']==wanted['menu_index'],'Fixed two-candidate selection differs')
  c=wanted['certificate'];newhi=c['q_contrast_upper'];upper=c['policy_upper']
  if 'outward' not in actual:
   require(row['enhancement_failure'] is not None and actual is actuals[-1],'Unfinished candidate missing failure')
   require(actual['dual_elapsed_seconds']>=0 and actual['dual_started']==(row['mode']=='joint_two'),'Uncharged unfinished dual attempt')
   if actual['dual_witness'] is not None:checked_dual(engine,wanted['b'],actual['dual_witness'])
   continue
  if row['mode']=='joint_two':
   require(actual['dual_witness'] is not None,'Missing exact dual witness')
   newhi=min(newhi,checked_dual(engine,wanted['b'],actual['dual_witness']))
   upper=min(upper,engine.absolute_upper_q(a,'fused')+newhi+engine.delta)
  else:require(actual['dual_witness'] is None,'Fused comparator used joint solve')
  gain=-newhi-engine.delta;lower=c['policy_lower'];B=c['optimum_lower']
  expected=dict(change_upper=newhi,gain_lower=gain,lower=lower,upper=upper,optimum_lower=B,loss=upper-B,width=upper-lower)
  for field,v in expected.items():require(F(actual['certificate'][field])==v,'Joint candidate mismatch: '+field)
  lo,hi,bb=outward(lower,False),outward(upper,True),outward(B,False)
  loss=math.nextafter(hi-bb,math.inf);width=math.nextafter(hi-lo,math.inf)
  good=gain>0 and upper-B<=engine.tau and upper-lower<=engine.omega and loss<=float(engine.tau) and width<=float(engine.omega)
  for field,v in [('lower',lo),('upper',hi),('optimum_lower',bb),('loss',loss),('width',width)]:require(actual['outward'][field]==v,'Final outward endpoint mismatch')
  require(actual['accepted'] is good,'Acceptance changed')
  if good:eligible.append((gain,wanted['b'],wanted['menu_index'],lo,hi,bb,loss,width))
 require(row['dual_solves_started']==sum(r['dual_started'] for r in actuals),'Missing started dual solve charge')
 require(row['dual_solves_completed']==sum(r['dual_completed'] for r in actuals),'Missing completed dual solve count')
 require(row['dual_seconds']==sum(r['dual_elapsed_seconds'] for r in actuals),'Missing partial dual time')
 if row['enhancement_failure'] is not None:eligible=[]
 selected=min(eligible,key=lambda t:(-t[0],t[1],t[2])) if eligible else None
 require((selected is not None)==row['accepted_improvement'],'Selected acceptance differs')
 require(F(row['certified_policy_gain_lower'])==(selected[0] if selected else 0),'Selected gain differs')
 require(b==(selected[1] if selected else a),'Final original action differs')
 if selected:
  require(row['selected_menu_index']==selected[2],'Tie rule differs')
  for field,v in zip(('complete_policy_lower','complete_policy_upper','original_optimum_lower','loss','width'),selected[3:]):require(row[field]==v,'Returned certificate field differs')
 else:
  require(row['complete_policy_lower']==row['baseline_lower'] and row['complete_policy_upper']==row['baseline_upper'] and row['original_optimum_lower']==row['baseline_optimum_lower'],'Retained incumbent endpoints changed')


def run(primary,output,timings):
 out,tick,info=start(output,'independent-exact-dual-audit')
 try:
  verify_source();binding=boundaries();ss=states();data=rows(Path(primary)/'records124.jsonl');expected={(i,b,a,l,m,j) for i,b,a,l in catalog() for m in MODES for j in range(N)}
  key=lambda r:(r['index'],r['budget'],r['arm'],r['training_loss'],r['mode'],r['row'])
  require(len(data)==len(expected) and {key(r) for r in data}==expected,'Complete primary census differs')
  lookup={key(r):r for r in data};duals=0
  for row in data:
   require(row['state']==ss[row['row']]['state'] and row['state_hex']==ss[row['row']]['hex'],'State identity differs')
   require(row['source_commit']==binding['source_commit'] and row['state_commit']==binding['state_commit'] and row['actor_commit']==ACTOR_COMMIT and row['repeat'] is None and row['population_observation'] is True,'Primary immutable scientific identity differs')
   audit_row(row);duals+=row['dual_solves_started']
  fields=('action_hex','baseline_action_hex','complete_policy_lower','complete_policy_upper','original_optimum_lower','loss','width','accepted_improvement','certified_policy_gain_lower','selected_menu_index','counts')
  timed=0
  for index,p in enumerate(timings):
   rs=rows(Path(p)/'records124.jsonl');te={k for k in expected if k[-1]<4}
   require(len(rs)==len(te) and {key(r) for r in rs}==te,'Complete timing census differs')
   for r in rs:
    require(r['repeat']==index and all(r[f]==lookup[key(r)][f] for f in fields),'Timing changed a declared decision/certificate field');timed+=1
  finish(out,tick,info,status_detail='passed',assertions=CHECKS,primary_decisions=len(data),dual_witnesses=duals,timing_decisions=timed,
   production_optimizer_imported=False,original_economic_queries=0,primary_sha256=digest(Path(primary)/'records124.jsonl'))
 except BaseException:fail(out,tick);raise

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--primary',required=True);p.add_argument('--output',required=True);p.add_argument('--timing',action='append',default=[]);a=p.parse_args();run(a.primary,a.output,a.timing)
