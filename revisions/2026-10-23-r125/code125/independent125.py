"""Independent exact continuous-risk economics, with prospective precision budget.

No production economic module is imported.  All selected policies and completed
prefix policies receive their own rational original-law evaluation.  The audit
may be unresolved at its declared cap; that never becomes a successful check.
"""
import argparse,sys,time
from common125 import *
INDEPENDENT_LEVELS=(8,32,128)
INDEPENDENT_NODE_CAP=65536

def run(primary,output):
 out,tick,info=start(output,'independent-original-economic-audit')
 try:
  verified=verify_inputs()
  sys.path.insert(0,str(R121/'code121'));import exact121 as ex
  ir,identity=ex.load_primitives();ex.TERMINAL_STEPS=32
  data=rows(Path(primary)/'records125.jsonl.gz');keys={};links=[]
  for row in data:
   x=tuple(F(v) for v in row['state125']);alpha=F(row['alpha'])
   a=F(row['action']);key=ex.key(x,a,alpha);kid=ex.key_id(key)
   keys[kid]=(key,dict(x=x,a=a,alpha=alpha))
   b=F(row.get('baseline_action125',row['action']));bk=ex.key(x,b,alpha);bid=ex.key_id(bk)
   keys[bid]=(bk,dict(x=x,a=b,alpha=alpha))
   links.append(dict(final=kid,baseline=bid,row=row))
  if len(keys)*17>INDEPENDENT_NODE_CAP:raise RuntimeError('Declared baseline audit budget cannot cover all selected actions')
  trace=ex.ExactTrace(out/'terminal_witnesses125.jsonl.gz');evals={};nodes=0;level_by={}
  def checks(link):
   r=link['row'];v=evals[link['final']];b=evals[link['baseline']]
   q=lambda z:F(z)
   lo,hi=q(r['complete_policy_lower']),q(r['complete_policy_upper'])
   contained=lo<=v['j_lower']<=v['j_upper']<=hi
   overlap=not(v['j_upper']<lo or v['j_lower']>hi)
   gain=q(r.get('gain_lower125',0));accepted=r.get('accepted125',False)
   gain_lower=b['j_lower']-v['j_upper'] if link['final']!=link['baseline'] else F(0)
   gain_upper=b['j_upper']-v['j_lower'] if link['final']!=link['baseline'] else F(0)
   gain_ok=(not accepted) or gain_lower>=gain
   return dict(contained=contained,overlap=overlap,gain_confirmed=gain_ok,independent_gain_lower=gain_lower,independent_gain_upper=gain_upper,claimed_gain= gain,contradiction=(not overlap) or (accepted and gain_upper<gain))
  try:
   for level in INDEPENDENT_LEVELS:
    if level==8:pending=set(keys)
    else:
     pending=set()
     for link in links:
      c=checks(link)
      if not(c['contained'] and c['gain_confirmed']):pending.update((link['final'],link['baseline']))
    for kid in sorted(pending):
     needed=2*level+1
     if nodes+needed>INDEPENDENT_NODE_CAP:continue
     ex.BINS=level;k,v=keys[kid];answer=ex.evaluate_action(ir,k,v,trace)
     append(out/'evaluations125.jsonl.gz',answer);evals[kid]=answer;nodes+=needed;level_by[kid]=level
     print(json.dumps(dict(key_id=kid,bins=level,distinct_evaluated=len(evals),terminal_nodes=nodes)),flush=True)
   results=[]
   for link in links:
    r=link['row'];c=checks(link)
    rec=dict(index=r['index'],budget=r['budget'],arm=r['arm'],training_loss=r['training_loss'],mode=r['mode'],row=r['row'],final_key=link['final'],baseline_key=link['baseline'],accepted=r.get('accepted125',False),**c)
    append(out/'checks125.jsonl',rec);results.append(rec)
   counts=dict(ex.COUNTS)
   summary=dict(decisions=len(data),unique_actions=len(keys),audit_terminal_nodes=nodes,node_budget=INDEPENDENT_NODE_CAP,levels=INDEPENDENT_LEVELS,level_by_key=level_by,contained=sum(r['contained'] for r in results),unresolved_containment=sum(not r['contained'] for r in results),accepted=sum(r['accepted'] for r in results),accepted_gain_confirmed=sum(r['accepted'] and r['gain_confirmed'] for r in results),contradictions=sum(r['contradiction'] for r in results),counts=counts,primitive_identity=identity,verified_source=verified,independent_population_samples=0)
   write(out/'SUMMARY125.json',summary)
   if summary['contradictions']:raise ArithmeticError('Independent rational economics contradicts a production claim')
   finish(out,tick,**summary)
  finally:trace.close()
 except BaseException:fail(out,tick);raise

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--primary',required=True);p.add_argument('--output',required=True);a=p.parse_args();run(a.primary,a.output)
