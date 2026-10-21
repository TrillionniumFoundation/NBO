"""Prospective R122 fixed-actor support-recycling experiment; all attempts retained."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,time,traceback
from pathlib import Path
for _name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[_name]='1'
from common122 import *


def sample(a,out):
 actors=verify_actors()
 subprocess.run(['git','merge-base','--is-ancestor',ACTOR_COMMIT,a.source_commit],cwd=REPO,check=True)
 entropy=os.urandom(N*2*5)
 (out/'entropy122.bin').write_bytes(entropy)
 data=[]
 for j in range(N):
  integers=[int.from_bytes(entropy[(2*j+k)*5:(2*j+k+1)*5],'little') for k in range(2)]
  values=[n/2**40 for n in integers]
  data.append({'row':j,'integers':integers,'state':values,'hex':[v.hex() for v in values]})
 dump(out/'states122.json',{'source_commit':a.source_commit,'actor_commit':ACTOR_COMMIT,'states':data,'independent_state_units':N,'law':'32 independent pairs of 40-bit dyadic uniform initial coordinates from one 320-byte OS entropy draw','no_outcome_selection':True})
 dump(out/'ACTORS122.json',{'actor_commit':ACTOR_COMMIT,'models':actors,'acquired_here':False,'historical_costs_retained':True})
 manifest={'source_commit':a.source_commit,'actor_commit':ACTOR_COMMIT,'kind':'r122-independent-states-before-economic-evaluation','files':{n:digest(out/n) for n in ('entropy122.bin','states122.json','ACTORS122.json')}}
 dump(out/'STATE_MANIFEST122.json',manifest)
 return {'state_rows':N,'entropy_bytes':len(entropy),'no_economic_call':True}


def state_input(a):
 return validated_states(a.states,a.source_commit,a.state_commit)


def catalogue_run(a,out,repeat=None):
 states=state_input(a);verify_actors()
 dump(out/'STATES_USED122.json',dict(source_commit=a.source_commit,state_commit=a.state_commit,actor_commit=ACTOR_COMMIT,state_directory=str(Path(a.states).resolve().relative_to(REPO))))
 import service122 as solver
 solver.configure()
 n=N if repeat is None else 16
 ordered=[(k,s) for k in catalog() for s in SERVICES]
 if repeat is not None:
  shift=(11*repeat)%len(ordered);ordered=ordered[shift:]+ordered[:shift]
 controls={};allrows=[];cohorts=[]
 for ix,(k,s) in enumerate(ordered):
  tick=time.perf_counter();i,b,arm,loss=k;alpha=(.5,.75)[i]
  load=time.perf_counter();p=model_path(k);model=None if p is None else json.loads(p.read_text());load_seconds=time.perf_counter()-load
  service_sum=0.;serialize_sum=0.
  for j in range(n):
   r=solver.service(states[j]['state'],alpha,model,s)
   r.update(index=i,row=j,budget=b,arm=arm,loss=loss,alpha=alpha,population_observation=repeat is None,repeat=repeat,source_commit=a.source_commit,state_commit=a.state_commit,actor_commit=ACTOR_COMMIT)
   r['state']=states[j]['state'];r['state_hex']=states[j]['hex']
   service_sum+=r['complete_service_seconds']
   serialize=time.perf_counter();append(out/'records122.jsonl',r);serialize_sum+=time.perf_counter()-serialize
   allrows.append(r)
   controls[(i,j,b,arm,loss,s)]=r
  cohort={'index':i,'budget':b,'arm':arm,'loss':loss,'service':s,'repeat':repeat,'n':n,'cold_load_seconds':load_seconds,'service_sum_seconds':service_sum,'record_serialization_seconds':serialize_sum,'complete_cohort_seconds':time.perf_counter()-tick,'actor_sha256':None if p is None else digest(p)}
  cohorts.append(cohort);append(out/'cohorts122.jsonl',cohort)
  print('COHORT',repeat,ix+1,len(ordered),k,s,round(cohort['complete_cohort_seconds'],6),flush=True)
 if {key(r) for r in allrows}!=identities(n) or len(allrows)!=len(identities(n)):raise ValueError('Incomplete primary/timing service catalogue')
 for r in allrows:
  c=controls[(r['index'],r['row'],r['budget'],r['arm'],r['loss'],'control')]
  for x,y in [('baseline_action','action'),('baseline_lower','complete_policy_lower'),('baseline_upper','complete_policy_upper')]:
   if r[x]!=c[y]:raise ValueError('Intervention completed incumbent differs from its control: '+str(key(r)))
  if not r['qualified'] or F(r['certified_policy_gain_lower'])<0:raise ValueError('Invalid final qualification/safe gain')
  if r['accepted_improvement']!=(r['action']!=r['baseline_action']):raise ValueError('Recorded acceptance/action identity mismatch')
 return allrows,cohorts


def primary(a,out):
 primary_start=time.perf_counter();main,cohorts=catalogue_run(a,out);main_seconds=time.perf_counter()-primary_start
 timing=[]
 for r in range(3):
  path=out/'timing'/f'attempt{r:02d}';path.parent.mkdir(parents=True,exist_ok=True)
  command=[sys.executable,str(Path(__file__).resolve()),'timing','--source-commit',a.source_commit,'--state-commit',a.state_commit,'--states',str(Path(a.states).resolve()),'--repeat',str(r),'--output',str(path)]
  begin=time.perf_counter()
  with (path.parent/f'launcher{r:02d}.log').open('x') as f:proc=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT)
  rec={'repeat':r,'command':command,'exit_code':proc.returncode,'outer_seconds':time.perf_counter()-begin};timing.append(rec);dump(path.parent/f'launcher{r:02d}.json',rec)
  if proc.returncode:raise RuntimeError('Retained failed fresh timing process '+str(r))
 bykey={key(r):r for r in main};checks=0
 for r in range(3):
  timed=rows(out/'timing'/f'attempt{r:02d}'/'records122.jsonl')
  for row in timed:
   original=bykey[key(row)]
   for name in ('action','baseline_action','accepted_improvement','candidate_rejected','refinement_count','paid_refinement_attempt_count','paid_refinement_levels_started','candidate_algebra_attempts','candidate_bound_attempts','refused_candidate_bound_attempts','certified_policy_gain_lower','improvement_stop'):
    if row[name]!=original[name]:raise ValueError('Timing identity mismatch '+str((r,key(row),name)))
   checks+=1
 dump(out/'TIMINGS122.json',{'processes':timing,'primary_catalogue_seconds_excluding_children':main_seconds,'timing_identity_checks':checks,'timings_descriptive_not_new_population_observations':True})
 return {'primary_rows':len(main),'timed_rows':checks,'primary_states':N,'timing_states':16,'timing_processes':3,'all_records_retained':True}


def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=('sample','primary','timing'));p.add_argument('--source-commit',required=True);p.add_argument('--state-commit');p.add_argument('--states',type=Path);p.add_argument('--repeat',type=int);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
 out,initial,tick=start(a.output,a.mode,{'claimed_source_commit':a.source_commit})
 try:
  source=verify_source(a.source_commit);dump(out/'VERIFIED_SOURCE122.json',source)
  if a.mode=='sample':extra=sample(a,out)
  elif a.mode=='primary':extra=primary(a,out)
  else:
   if a.repeat not in (0,1,2):raise ValueError('Exactly the three prospective timing repetitions')
   data,cohorts=catalogue_run(a,out,a.repeat);extra={'timing_rows':len(data),'repeat':a.repeat,'new_population_units':0}
  finish(out,initial,tick,extra)
 except BaseException:fail(out,tick);raise

if __name__=='__main__':main()
