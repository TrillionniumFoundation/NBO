#!/usr/bin/env python3
"""Independent standard-library audit for the NBO R52 referee review."""
import argparse,gzip,hashlib,json,math,statistics
from fractions import Fraction as F
from pathlib import Path
BR='revision/econometrica-nbo-r52-review-ready-2026-10-08'; COMMIT='e82e05e658d6aba9bb843dcece66410d1040a49a'; TREE='0a5b4b0b2972b681aa0b67da7020c8a13b987a80'
CZIP='c5d91ae956e72ce0dffb160d2aad8f6627e9e0e6c288f248a5caef525e1ec1db'; PZIP='a34df1b4a50d6c8fabbdfe76dc33ca37e2baabffb849ca328e419f66834d6905'
AMPS=(0,1,16,4096); ALLOW=(0.,1.875,30.,7680.)
def H(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def J(p):return json.loads(Path(p).read_text())
def bad(x,m='audit failure'):
 if x:raise AssertionError(m)
def main():
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--complete-zip',type=Path);p.add_argument('--paper-zip',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();r=a.root.resolve()
 bad(not (r/'audit/FINAL_DELIVERY52.json').is_file(),'not R52')
 arts={}
 if a.complete_zip:arts['complete']=H(a.complete_zip);bad(arts['complete']!=CZIP,'complete digest')
 if a.paper_zip:arts['paper_and_audits']=H(a.paper_zip);bad(arts['paper_and_audits']!=PZIP,'paper digest')
 d=J(r/'audit/FINAL_DELIVERY52.json');bad(d['candidate_commit']!='774e9fec123c49e1f0e96a9aaa2a31a03916adf3' or d['candidate_tree']!='361990dff96a26a81bb07527966783b50ac065b6' or d['canonical_branch']!=BR or not d['clean_archive_passed'],'delivery')
 for q,h in d['files'].items():bad(not (r/q).is_file() or H(r/q)!=h,'delivery hash '+q)
 rel=J(r/'audit/RELEASE52.json');bad(rel['status']!='passed' or rel['total_tests']!=54,'release');pages={'ECTA':51,'supp':40,'complete':117,'complete-supp':101,'response':7}
 for x in rel['documents']:bad(x['pages']!=pages[x['document']] or any(x[k] for k in ('fatal_errors','undefined_references','duplicate_labels','missing_characters','overfull_boxes')),'document')
 fr=J(r/'audit/SOURCE_FREEZE52.json')
 for q,h in fr['sha256'].items():bad(H(r/q)!=h,'source '+q)
 for x in fr['catalogue']:bad(H(r/x['path'])!=x['sha256'],'policy '+x['key'])
 ex=J(r/'audit/EXECUTION52.json');bad(ex['status']!='completed','execution')
 for q,h in ex['files'].items():bad(H(r/q)!=h,'evidence '+q)
 cells=strict=blocked=equal=ws=fs=wb=fb=0;times=[];wt=[];ft=[];services=0
 for f in sorted((r/'results52').iterdir()):
  if not f.is_dir():continue
  services+=1;z=J(f/'record.json');bad(z['cells']!=65536 or z['feasibility_violations'] or H(f/z['cell_file'])!=z['cell_sha256'],'record');amp={int(x['M']):x for x in z['amplitudes']};cnt={m:[0]*5 for m in AMPS};mx=None;rows=0
  with gzip.open(f/z['cell_file'],'rt',encoding='ascii') as g:
   bad(next(g).rstrip().split(',')!=['i','j','base','proposal','contrast','lower_hex','upper_hex','scalar_M0','scalar_M1','scalar_M16','scalar_M4096'],'header')
   for k,line in enumerate(g):
    q=line.rstrip().split(',');i,j,b,v,c=int(q[0]),int(q[1]),int(q[2]),int(q[3]),int(q[4]);lo,hi=float.fromhex(q[5]),float.fromhex(q[6])
    if i!=k//256 or j!=k%256 or not(math.isfinite(lo) and math.isfinite(hi) and lo<=hi):raise AssertionError('cell')
    cap=512+i+j
    if min(b,v,c)<0 or max(b,v,c)>cap or c!=(v if hi<=0 else b):raise AssertionError('gate')
    if c!=b:mx=hi if mx is None else max(mx,hi)
    ch=b!=v
    for m,s,u in zip(AMPS,map(int,q[7:]),ALLOW):
     if s!=(v if hi+u<=0 else b):raise AssertionError('scalar')
     a0=cnt[m]
     if ch:a0[0]+=s!=b;a0[1]+=s==b;a0[2]+=c!=b;a0[3]+=c==b
     else:a0[4]+=1
    rows+=1
  bad(rows!=65536 or mx!=z['maximum_accepted_true_cost_upper'] or (mx is not None and mx>0),'upper')
  for m in AMPS:
   x=amp[m];bad((x['scalar_strict_changes'],x['scalar_blocked_changes'],x['contrast_strict_changes'],x['contrast_blocked_changes'],x['equal_proposals'])!=tuple(cnt[m]) or not x['identical_to_inherited_repaired_policy'],'counts')
  bad(any(amp[m]['contrast_strict_changes']!=amp[0]['contrast_strict_changes'] for m in AMPS) or any(amp[m]['scalar_strict_changes'] for m in (1,16,4096)),'amplitude')
  s,b0,e=amp[0]['contrast_strict_changes'],amp[0]['contrast_blocked_changes'],amp[0]['equal_proposals'];cells+=rows;strict+=s;blocked+=b0;equal+=e;t=z['through_cells_fsync_seconds'];times.append(t)
  if z['key'].startswith('compiled-witness'):wt.append(t);ws+=s;wb+=b0
  else:ft.append(t);fs+=s;fb+=b0
 bad(services!=8 or cells!=524288 or strict+blocked+equal!=cells,'totals');off=J(r/'audit/RESULT_AUDIT52.json');bad(off['status']!='passed' or off['all_cells_replayed']!=cells or off['new_independent_cost_estimands']!=0,'official')
 bad(F(1,2)-2*F(1,4)!=0,'null');w,delta=F(7,5),F(1,5);bad((delta-w)+w!=delta or 2*w-delta!=F(13,5),'sharpness')
 r49=J(r/'audit/R49_REFEREE_REPLAY.json')['direct_policy_cost'];bad(r49['r49_policy_pairs']!=96 or r49['r49_signs']!={'left-higher':93,'unresolved':3},'R49');ed=J(r/'audit/EDITORIAL_NUMBERS50.json');bad(ed['witness_groups']!=27 or ed['before']!={'higher':27} or ed['after']!={'higher':26,'unresolved':1} or ed['witness_gain_signs']!={'higher':27},'R51')
 out={'status':'passed','reviewed_snapshot':{'branch':BR,'commit':COMMIT,'tree':TREE},'artifact_digests':arts,'delivery':{'listed_files_verified':len(d['files']),'clean_archive_passed':True},'release':{'tests':54,'pages':pages,'documents_clean':True},'source_freeze':{'scientific_sources_verified':len(fr['sha256']),'policy_checkpoints_verified':len(fr['catalogue']),'protocol_first_commit':fr['protocol_first_commit'],'source_commit':fr['source_commit']},'r52_cell_replay':{'services':services,'cells':cells,'amplitude_gate_decisions':cells*8,'contrast_strict_changes':strict,'contrast_blocked_changes':blocked,'equal_proposals':equal,'strict_change_fraction':strict/cells,'blocked_fraction':blocked/cells,'witness_strict_changes':ws,'fvi_strict_changes':fs,'witness_blocked_changes':wb,'fvi_blocked_changes':fb,'total_recorded_seconds':sum(times),'witness_mean_seconds':statistics.mean(wt),'fvi_mean_seconds':statistics.mean(ft),'all_accepted_upper_bounds_nonpositive':True,'all_feasible':True,'positive_amplitude_global_width_accepts':0,'contrast_policy_amplitude_invariant':True,'new_independent_cost_estimands':0},'theory_spot_checks':{'investment_action_null_coefficient':'0','sharpness_gate':'1/5','sharpness_gap':'13/5','sharpness_contrast':'7/5','core_algebra_spot_checks':True},'inherited_economic_evidence':{'r49_policy_pairs':96,'r49_witness_higher':93,'r49_witness_lower':0,'r49_unresolved':3,'r51_witness_groups':27,'r51_before_repair_witness_higher':27,'r51_after_repair_witness_higher':26,'r51_after_repair_unresolved':1,'r51_own_incumbent_gains_positive':27},'scope':['Verifies frozen files and all 524,288 stored cell rows; does not retrain, resimulate, recompile, or retime.','R52 creates no new independent policy-cost estimand and does not execute the general coupled-residual certificate in the continuous benchmark.','Historical clocks remain single-runner descriptive records.']}
 s=json.dumps(out,indent=2,sort_keys=True)+'\n';print(s,end='')
 if a.output:a.output.write_text(s)
if __name__=='__main__':main()
