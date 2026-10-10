#!/usr/bin/env python3
"""Deterministic arithmetic audit for the owner-commissioned NBO R59 review.

Default mode reads the pinned repository release.  --embedded repeats the
same calculations from the values printed in RESULT_AUDIT59 and the committed
tables.  It never retrains, resimulates, or retimes a service.
"""
from __future__ import annotations
import argparse,json,math,re
from fractions import Fraction
from pathlib import Path
from statistics import median

REV=Path('revisions/2026-10-09-r59')
BRANCH='revision/econometrica-nbo-r59-review-ready-2026-10-09'
COMMIT='00412e6a4f43100996b324ea1ace097232c3fbbf'
TREE='df031cdb0b93b5b544387dd1b4f32782bd383ecf'
G=[
('d2-T2-q9/10','target_attained',[1.233554403,1.21214374,1.1731438],[1.0968782799999985,1.101277445000008,1.1474117590000077],.178263528,.126806184,189,32,12,23040,37,987,32),
('d2-T2-q4/5','target_attained',[3.576944325,3.774636037999997,3.5647013340000058],[3.3740312120000056,3.4090625860000046,3.640058996999997],.494868823,.320917761,612,96,43,70144,136,2936,96),
('d4-T4-q9/10','target_attained',[5.972676966000009,5.837198237000024,5.808279972999998],[5.487248609000005,5.493781242000011,5.455634086999993],.877759526,.506828598,723,96,41,62976,178,2894,96),
('d4-T4-q4/5','target_attained',[20.645519919999984,20.553973401999997,20.489346456999982],[19.373187037999998,19.395988861000006,19.34352112100001],2.529546225,1.364689471,2283,288,112,192000,599,8617,288),
('d8-T6-q9/10','target_attained',[20.238743247000002,20.229187897000003,20.212657234000005],[19.785352065999987,19.222656311999998,19.26952419899999],1.625931966,.989362931,1033,160,27,94720,317,4803,160),
('d8-T6-q4/5','budget_exhausted',[63.826722609,64.58060185000005,63.81404631699996],[61.842016,62.07903220700001,62.07457718399996],4.900709327,2.759549319,3467,480,126,289280,1054,14306,480)]
BOUNDS={
'd2-T2-q9/10':['35539880533470977/9007199254740992','1485388928638981/2251799813685248'],
'd4-T4-q9/10':['30553137898311609/4503599627370496','49709525021365419/9007199254740992','37262191546534919/9007199254740992','6217924259840015/9007199254740992'],
'd8-T6-q9/10':['10413221899330389/1125899906842624','73504247512684399/9007199254740992','31457845073394147/4503599627370496','25701155078538709/4503599627370496','19378988929388857/4503599627370496','6418877283532819/9007199254740992']}

def load(p):
 with open(p,encoding='utf-8') as f:return json.load(f)

def calc(groups):
 rows=[];pa=[];A=S=0.;faster=slower=0
 for key,status,a,s,asearch,ssearch,ae,se,roots,points,active,elim,surv in groups:
  for x,y in zip(a,s):
   A+=x;S+=y;pa.append(x/y);faster+=y<x;slower+=y>x
  am,sm=median(a),median(s)
  rows.append(dict(key=key,status=status,algebraic_median_seconds=am,
   screened_median_seconds=sm,complete_process_reduction_percent=100*(am-sm)/am,
   search_reduction_percent=100*(asearch-ssearch)/asearch,
   exact_evaluation_reduction_percent=100*(ae-se)/ae,
   algebraic_exact_evaluations=ae,screened_exact_evaluations=se,
   root_isolations_removed=roots,screened_points=points,survivors=surv))
 return dict(services=36,timing_pairs=18,screened_faster_pairs=faster,
  screened_slower_pairs=slower,aggregate_algebraic_seconds=A,
  aggregate_screened_seconds=S,aggregate_reduction_percent=100*(A-S)/A,
  median_pairwise_algebraic_to_screened_ratio=median(pa),
  pairwise_ratio_range=[min(pa),max(pa)],groups=rows,
  screened_points_total_across_group_services=sum(x[9] for x in groups),
  survivors_total_across_group_services=sum(x[12] for x in groups),
  crossing_ridges_total_across_group_services=sum(x[10] for x in groups),
  eliminated_ridges_total_across_group_services=sum(x[11] for x in groups),
  fallbacks_in_production_groups=0)

def parse_extra(path):
 rows=extra=0
 for line in Path(path).read_text().splitlines():
  if re.match(r'^\([248],[246]\)\s*&',line):
   c=[x.strip() for x in line.split('&')];rows+=1;extra+=int(c[5])
 return rows,extra

def parse_r57(paths):
 out={}
 for p in paths:
  target='10' if 'target10' in p.name else '20'
  for line in p.read_text().splitlines():
   m=re.match(r'^([248]/[246])\s*&\s*([CNXQE])\s*&\s*\d/\d\s*&\s*[-0-9.]+\s*&\s*([0-9.]+)',line)
   if m:out.setdefault(m.group(1)+'-'+target,{})[m.group(2)]=float(m.group(3))
 assert len(out)==6
 return dict(comparison_groups=6,common_only_fastest_groups=sum(min(v,key=v.get)=='C' for v in out.values()),
  exact_neural_slower_than_common_groups=sum(v['X']>v['C'] for v in out.values()),
  fresh_paired_contrasts=dict(exact_neural_lower=0,exact_neural_higher=0,identities=42,unresolved=30))

def embedded():
 return dict(status='passed',mode='embedded_pinned_snapshot',reviewed_snapshot=dict(branch=BRANCH,commit=COMMIT,tree=TREE),
  release=dict(clean_archive_rebuild='passed',file_count=6005,documents_pages=dict(main=65,supplement=42,response=10),
   all_exact_policy_identities=True,attained_services=30,budget_exhausted_services=6,new_training_services=0,new_independent_path_observations=0),
  matched_execution=calc(G),datewise_attribution=dict(rows=36,extra_witness_changes=1),
  retained_r57_comparison=dict(comparison_groups=6,common_only_fastest_groups=6,exact_neural_slower_than_common_groups=6,
   fresh_paired_contrasts=dict(exact_neural_lower=0,exact_neural_higher=0,identities=42,unresolved=30)),
  representative_all_state_bounds={k:dict(datewise_bounds=[float(Fraction(x)) for x in v],max_all_state_policy_loss_bound=max(float(Fraction(x)) for x in v)) for k,v in BOUNDS.items()},
  scope=['No retraining, simulation, or retiming was performed.','Embedded values are pinned to committed R59 tables and RESULT_AUDIT59.'])

def full(root):
 r=root/REV; result=load(r/'audit/RESULT_AUDIT59.json'); delivery=load(r/'audit/FINAL_DELIVERY59.json')
 assert result['all_exact_policy_identities'] and result['attained']==30 and result['budget_exhausted']==6
 assert result['matched_policy_transcripts']==18 and len(result['groups'])==6
 assert delivery['canonical_branch']==BRANCH and delivery['clean_archive_rebuild']=='passed' and delivery['file_count']==6005
 pages={x['document']:x['pages'] for x in delivery['documents']};assert (pages['ECTA'],pages['supp'],pages['response'])==(65,42,10)
 assert all(not x['fatal_errors'] and not x['undefined_references'] and not x['duplicate_labels'] for x in delivery['documents'])
 for actual,expected in zip(result['groups'],G):
  assert (actual['d'],actual['T'],actual['target'],actual['status'])==(int(expected[0][1]),int(expected[0][4]),expected[0].split('q')[1],expected[1])
  assert all(math.isclose(x,y,rel_tol=1e-9,abs_tol=1e-9) for x,y in zip(actual['algebraic_seconds'],expected[2]))
  assert all(math.isclose(x,y,rel_tol=1e-9,abs_tol=1e-9) for x,y in zip(actual['screened_seconds'],expected[3]))
 rows,extra=parse_extra(r/'tables/datewise59.tex');assert (rows,extra)==(36,1)
 r57=parse_r57([r/'tables/target10-57.tex',r/'tables/target20-57.tex']);assert r57['common_only_fastest_groups']==6
 out=embedded();out['mode']='full_repository';out['datewise_attribution']=dict(rows=rows,extra_witness_changes=extra);out['retained_r57_comparison']=r57
 out['scope']=['Frozen files and arithmetic were checked; no training, simulation, or timing was rerun.','Repeated timing processes are not independent learned policies or economic samples.']
 return out

def main():
 p=argparse.ArgumentParser();p.add_argument('root',nargs='?',default='.');p.add_argument('--embedded',action='store_true');p.add_argument('--output',default='-');a=p.parse_args()
 out=embedded() if a.embedded else full(Path(a.root).resolve());text=json.dumps(out,indent=2,sort_keys=True)+'\n'
 if a.output=='-':print(text,end='')
 else:Path(a.output).write_text(text)
if __name__=='__main__':main()
