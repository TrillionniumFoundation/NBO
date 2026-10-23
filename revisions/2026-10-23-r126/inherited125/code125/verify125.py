"""Exact saved-certificate and design verification; not independent economics."""
import argparse,collections,sys
from common125 import *

def run(primary,timings,output):
 out,tick,info=start(output,'exact-certificate-and-census-audit')
 try:
  verified=verify_inputs();import service125 as svc;svc.configure()
  data=rows(Path(primary)/'records125.jsonl.gz');assert len(data)==936
  key=lambda r:tuple(r[k] for k in ('index','budget','arm','training_loss','mode','row'))
  table={key(r):r for r in data};assert len(table)==936
  expected={c+(j,) for c in catalog() for j in range(4)};assert set(table)==expected
  n=0;queries=0;contractions=0;gain=0
  for r in data:
   assert tuple(r['state125'])==STATES[r['row']];n+=1
   A=F(1,8)+sum(map(F,r['state125']))/16
   assert 0<=F(r['action'])<=A;n+=1
   assert F(r['certified_regret_upper'])<=TAU and F(r['width'])<=OMEGA;n+=1
   assert r['new_terminal_nodes125']<=NODE_BUDGET or r['mode']=='grid33';n+=1
   if r['mode'] not in ('fused_control','grid33'):
    assert r['new_terminal_nodes125']==sum(q['requested_terminal_nodes'] for q in r['new_queries125']);n+=1
    for q in r['new_queries125']:
     if not q['completed']:continue
     c=q['certificate'];g=svc.old.recover(c,r['state125'],r['alpha'])
     assert plain(g)==q['gradient'];n+=1
     lo,hi=map(F,q['bracket_after']);l0,r0=map(F,q['bracket_before']);a=F(q['action'])
     assert l0<=lo<=hi<=r0 and l0<=a<=r0;n+=1
     if q['contracted']:assert hi-lo<=(r0-l0)/2+abs(a-(l0+r0)/2);contractions+=1;n+=1
     queries+=1
    if r['accepted125']:
     c=r['selected_certificate125'];assert F(c['gain_lower'])>0 and F(c['change_upper'])+DELTA<0;n+=2
     assert F(c['loss'])<=TAU and F(c['width'])<=OMEGA;n+=1;gain+=1
  matched=0
  for k,r in table.items():
   if r['arm']!='relu':continue
   pair=list(k);pair[2]='hinge';h=table[tuple(pair)]
   for f in ('action_hex','complete_policy_lower','complete_policy_upper','certified_regret_upper','width','accepted125','gain_lower125','new_terminal_nodes125','stop125'):
    assert r[f]==h[f],(f,k);n+=1
   assert r['counts125']==h['counts125'];n+=1;matched+=1
  repeats=0
  for path in timings:
   timed=rows(Path(path)/'records125.jsonl.gz');assert len(timed)==234;n+=1
   for r in timed:
    p=table[key(r)]
    for f in ('action_hex','complete_policy_lower','complete_policy_upper','certified_regret_upper','width','accepted125','gain_lower125','new_terminal_nodes125','stop125'):
     assert r[f]==p[f],(path,f,key(r));n+=1
    assert r['counts125']==p['counts125'];n+=1
   repeats+=1
  assert repeats==3;n+=1
  finish(out,tick,checks=n,primary_decisions=len(data),timing_decisions=repeats*234,original_queries=queries,certified_contractions=contractions,strict_improvements=gain,matched_relu_hinge_pairs=matched,verified_source=verified,scope='design and exact reported algebra; independent125 separately checks original economics')
 except BaseException:fail(out,tick);raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--primary',required=True);p.add_argument('--timing',action='append',required=True);p.add_argument('--output',required=True);a=p.parse_args();run(a.primary,a.timing,a.output)
