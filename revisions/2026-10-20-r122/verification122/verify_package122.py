"""Post-freeze read-only verification of the actual R122 evidence package.

No state draw, fitting, economic oracle, timing campaign or PDF build is run.
The frozen standard-library algebra auditor is replayed on saved primary rows;
probability, custody, cost and reporting accounts are independently recomputed.
A through-stage success verifies only that stage and its prerequisites.
"""
from __future__ import annotations
import argparse, collections, datetime as dt, gzip, hashlib, importlib.util
import json, math, os, re, subprocess, sys, tempfile, time, traceback, zipfile
from fractions import Fraction as Q
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
R121=ROOT.parent/'2026-10-20-r121'
M='796c5f2badf68b051ac6c144884c0e61b87faf5e'
RESTART='56cff43b088c7d6b1cee352d27fc9de8573c46ed'
REPORTING_REPAIR='af73f9bca8f2249da1601208a1921f50ea8fd074'
N=32
TAU=Q(1,256)
WIDTH=Q(1,8192)
SERVICES=('control','recycled','adaptive')
ARMS=('quadratic','relu','hinge','spline','poly2','poly3','grid')
STAGES=('freeze','states','primary','independent','stats','report','package')
FIELDS=('index','budget','arm','loss','service')
VOLUMES=(32,256,4096,65536)
SCENARIOS=('primary32','timing00','timing01','timing02')
IDENTITY_FIELDS=('action','baseline_action','accepted_improvement','candidate_rejected','refinement_count','paid_refinement_attempt_count','paid_refinement_levels_started','candidate_algebra_attempts','candidate_bound_attempts','refused_candidate_bound_attempts','certified_policy_gain_lower','improvement_stop')

def catalogue():return [(i,0,'online','online') for i in range(2)]+[(i,b,a,l) for i in range(2) for b in (5,9) for a in ARMS for l in ('value','marginal')]
def ident(r):return (r['index'],r['row'],r['budget'],r['arm'],r['loss'],r['service'])
def cell(r):return tuple(r[f] for f in FIELDS)
def expected(n):return {(i,j,b,a,l,s) for i,b,a,l in catalogue() for j in range(n) for s in SERVICES}
def cells():return {k+(s,) for k in catalogue() for s in SERVICES}
def exact(v):return Q(v)
def avg(v):return sum(v,Q(0))/N
def encode(v):
 if isinstance(v,Q):return str(v)
 if isinstance(v,Path):return str(v)
 if isinstance(v,dict):return {str(k):encode(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [encode(x) for x in v]
 return v
def write(p,v):
 with Path(p).open('x') as f:json.dump(encode(v),f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def git_bytes(commit,path):
 return subprocess.check_output(['git','show',commit+':'+str(path)],cwd=REPO,env={**os.environ,'GIT_NO_LAZY_FETCH':'1'})
def original_key(row,field='action'):
 value=row[field]
 if value is None:return None
 k=[row['state_hex'],float(value).hex(),float(row['alpha']).hex()]
 return hashlib.sha256(json.dumps(k,separators=(',',':')).encode()).hexdigest()

class Verification:
 def __init__(self,args):self.a=args;self.checks=0;self.inputs={};self.completed=[];self.counts={};self.receipts={}
 def check(self,c,m):
  self.checks+=1
  if not c:raise AssertionError(m)
 def bind(self,p):
  p=Path(p).resolve();self.check(p.is_file(),'Required file missing: '+str(p))
  rel=str(p.relative_to(REPO)) if p.is_relative_to(REPO) else str(p)
  self.inputs[rel]={'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)}
  return p
 def read(self,p):return json.loads(self.bind(p).read_text())
 def rows(self,p):
  p=self.bind(p);op=gzip.open if p.suffix=='.gz' else open
  with op(p,'rt') as f:return [json.loads(s) for s in f if s.strip()]
 def unique(self,rows,key,label):
  d={}
  for r in rows:
   k=key(r);self.check(k not in d,'Duplicate '+label+': '+str(k));d[k]=r
  return d
 def stage(self,name,p,outer=True):
  receipt=self.read(p/'EXECUTION122.json');verified=self.read(p/'VERIFIED_SOURCE122.json');start=self.read(p/'START122.json')
  self.check(receipt.get('status')=='executed' and receipt.get('exit_code')==0,'Original stage did not complete successfully: '+name)
  self.check(verified['source_commit']==self.a.source_commit and verified['manifest_sha256']==sha(ROOT/'SOURCE_FREEZE122.json'),'Stage source binding differs: '+name)
  self.check(start['source']['claimed_source_commit']==self.a.source_commit,'Stage launch source differs: '+name)
  self.check(not (p/'FAILURE122.json').exists(),'Success and failure receipt coexist: '+name)
  self.check(Q(receipt['seconds'])>=0,'Negative original process runtime')
  self.receipts[name]={'inner':receipt,'start':start}
  if outer:
   launch=self.read(p/'OUTER_EXECUTION122.json')
   self.check(launch['status']=='executed' and launch['exit_code']==0,'External launch failed: '+name)
   # Original absolute paths may be moved with the package. The relative stage
   # suffix and exact recorded source arguments remain part of its custody.
   self.check(Path(launch['child_output']).name==p.name,'External launch identifies a different stage')
   self.check(Q(launch['outer_seconds'])>=Q(receipt['seconds']),'External clock fails to enclose child: '+name)
   self.check(all(launch['threads'].get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')),'Declared single-thread launcher differs')
   command=launch['command'];self.check('--source-commit' in command and command[command.index('--source-commit')+1]==self.a.source_commit,'External launch F differs')
   self.receipts[name]['outer']=launch
  return receipt
 def freeze(self):
  a=self.a
  for name,value in [('F',a.source_commit),('D',a.state_commit)]:
   self.check(len(value)==40 and all(c in '0123456789abcdef' for c in value),'Full '+name+' identity required')
  manifest=self.read(ROOT/'SOURCE_FREEZE122.json');rel=(ROOT/'SOURCE_FREEZE122.json').relative_to(REPO)
  self.check(git_bytes(a.source_commit,rel)==(ROOT/'SOURCE_FREEZE122.json').read_bytes(),'Actual F manifest identity differs')
  for rel,expected_sha in sorted(manifest['scientific_files'].items()):
   p=self.bind(REPO/rel)
   self.check(sha(p)==expected_sha,'Changed frozen local source: '+rel)
   self.check(hashlib.sha256(git_bytes(a.source_commit,rel)).hexdigest()==expected_sha,'Actual F blob identity differs: '+rel)
  d=manifest['fixed_design']
  self.check(d['states']==N and d['primary_decisions']==5568 and d['timed_decisions']==8352 and d['risk_policy_cells']==58,'Frozen population/cell scope changed')
  self.check(d['services']==list(SERVICES) and d['adaptive_refinement_ladder']==[256,512] and d['skip_level_no_finer_than_already_paid_completed_certificate'] is True,'Frozen service/precision scope changed')
  self.check(Q(d['joint_failure_probability'])==Q(1,20),'Frozen confidence scope changed')
  self.check(manifest['inherited_actor_commit']==M,'Inherited actor commit changed')
  self.manifest=manifest;self.counts['frozen_files']=len(manifest['scientific_files']);self.completed.append('freeze')
 def states(self):
  a=self.a;p=a.states;self.stage('states',p)
  manifest=self.read(p/'STATE_MANIFEST122.json')
  self.check(manifest['source_commit']==a.source_commit and manifest['actor_commit']==M,'State F/M differs')
  self.check(set(manifest['files'])=={'ACTORS122.json','entropy122.bin','states122.json'},'Different frozen state file set')
  for name,expected_sha in manifest['files'].items():
   f=self.bind(p/name);self.check(sha(f)==expected_sha,'State member bytes differ: '+name)
   self.check(hashlib.sha256(git_bytes(a.state_commit,f.relative_to(REPO))).hexdigest()==expected_sha,'State member not actual D: '+name)
  self.check(git_bytes(a.state_commit,(p/'STATE_MANIFEST122.json').relative_to(REPO))==(p/'STATE_MANIFEST122.json').read_bytes(),'State manifest not actual D')
  for parent,child in ((M,a.source_commit),(a.source_commit,a.state_commit)):
   result=subprocess.run(['git','merge-base','--is-ancestor',parent,child],cwd=REPO,env={**os.environ,'GIT_NO_LAZY_FETCH':'1'})
   self.check(result.returncode==0,'Actual M/F/D ancestry differs')
  draw=self.read(p/'states122.json');states=draw['states'];entropy=(p/'entropy122.bin').read_bytes()
  self.check(draw['independent_state_units']==N and draw['source_commit']==a.source_commit and draw['actor_commit']==M and draw['no_outcome_selection'] is True,'State draw identity differs')
  self.check(len(states)==N and len(entropy)==320,'Incomplete one-draw state census')
  for j,r in enumerate(states):
   ns=[int.from_bytes(entropy[(2*j+k)*5:(2*j+k+1)*5],'little') for k in range(2)];values=[n/2**40 for n in ns]
   self.check(r['row']==j and r['integers']==ns and r['state']==values and r['hex']==[v.hex() for v in values],'Entropy-to-state formula differs')
  actors=self.read(p/'ACTORS122.json');self.check(actors['actor_commit']==M and actors['acquired_here'] is False and actors['historical_costs_retained'] is True,'Actor reuse mislabeled')
  models=self.unique(actors['models'],lambda r:tuple(r['key']),'actor')
  self.check(set(models)=={k for k in catalogue() if k[2]!='online'},'Exactly56 fitted actors required')
  for k,r in models.items():
   path=self.bind(REPO/r['path']);self.check(sha(path)==r['sha256'],'Actual model byte changed')
   self.check(hashlib.sha256(git_bytes(M,r['path'])).hexdigest()==r['sha256'],'Model differs from actual original M')
  self.states_data=states;self.models=models;self.counts.update(independent_states=N,entropy_bytes=320,actual_inherited_models=56);self.completed.append('states')
 def check_row(self,r,timed=None):
  self.check(r['source_commit']==self.a.source_commit and r['state_commit']==self.a.state_commit and r['actor_commit']==M,'Record F/D/M differs')
  self.check(r['state']==self.states_data[r['row']]['state'] and r['state_hex']==self.states_data[r['row']]['hex'],'Record state differs from actual D')
  self.check(r['alpha']==(.5,.75)[r['index']],'Original risk objective differs')
  self.check(r['population_observation']==(timed is None) and r['repeat']==timed,'Timing promoted to population observation')
  cap=Q(1,8)+sum(map(Q,r['state']))/16
  for field,hexfield in [('action','action_hex'),('baseline_action','baseline_action_hex')]:
   self.check(0<=Q(r[field])<=cap and float(r[field]).hex()==r[hexfield],'Original action feasibility or bit identity differs')
  self.check(r['qualified'] is True and Q(r['certified_regret_upper'])<=TAU and Q(r['complete_policy_upper'])-Q(r['complete_policy_lower'])<=WIDTH,'Original regret/width qualification differs')
  self.check(r['accepted_improvement']==(r['action']!=r['baseline_action']),'Actual acceptance/action mismatch')
  self.check(Q(r['certified_policy_gain_lower'])>0 if r['accepted_improvement'] else Q(r['certified_policy_gain_lower'])==0,'Nonpositive accepted gain or positive unchanged gain')
  self.check(r['extra_candidate_economic_queries']==0,'Undeclared second-action economic query')
  self.check(r['raw_proposal_kept']==r['baseline_first_proposal_action'],'Original raw proposal not retained')
  if r['raw_proposal_kept'] is None:self.check(bool(r.get('proposal_numerical_failure')),'Missing raw proposal without failure')
  else:self.check(0<=Q(r['raw_proposal_kept'])<=cap,'Raw action outside original constraints')
 def primary(self):
  a=self.a;p=a.primary;receipt=self.stage('primary',p)
  binding=self.read(p/'STATES_USED122.json');self.check(binding==dict(source_commit=a.source_commit,state_commit=a.state_commit,actor_commit=M,state_directory=str(a.states.relative_to(REPO))),'Original primary state binding differs')
  raw=self.rows(p/'records122.jsonl');data=self.unique(raw,ident,'primary')
  self.check(set(data)==expected(N),'Exactly5,568 primary records required')
  source=ROOT/'code122/algebra_audit122.py';self.check(sha(source)==self.manifest['scientific_files'][str(source.relative_to(REPO))],'Algebra auditor differs from F')
  spec=importlib.util.spec_from_file_location('r122_frozen_record_algebra',source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  algebra=collections.Counter()
  for r in raw:
   self.check_row(r);algebra.update(module.audit(r))
   k=ident(r);control=data[k[:-1]+('control',)]
   self.check(r['baseline_action']==control['action'] and r['baseline_lower']==control['complete_policy_lower'] and r['baseline_upper']==control['complete_policy_upper'],'Intervention received a different original baseline')
  tim=self.read(p/'TIMINGS122.json');self.check(len(tim['processes'])==3 and {r['repeat'] for r in tim['processes']}=={0,1,2},'All3 original clocks required')
  self.check(tim['timing_identity_checks']==8352 and tim['timings_descriptive_not_new_population_observations'] is True,'Timing scope/count differs')
  cohorts={};self.timing={};all_timing=0
  for scenario in SCENARIOS:
   j=None if scenario=='primary32' else int(scenario[-2:]);q=p if j is None else p/'timing'/f'attempt{j:02d}';n=N if j is None else 16
   cohort=self.unique(self.rows(q/'cohorts122.jsonl'),cell,'cohort '+scenario);self.check(set(cohort)==cells(),'All174 cohorts required in '+scenario)
   for k,r in cohort.items():
    self.check(r['n']==n and r['repeat']==j,'Cohort volume or repeat differs')
    self.check(r['actor_sha256']==(None if k[2]=='online' else self.models[k[:4]]['sha256']),'Cohort cost/model identity differs')
    self.check(Q(r['complete_cohort_seconds'])>=Q(r['cold_load_seconds'])>=0,'Cohort clock/load order differs')
   cohorts[scenario]=cohort
   if j is not None:
    inner=self.stage(scenario,q,False);launch=next(x for x in tim['processes'] if x['repeat']==j)
    self.check(launch['exit_code']==0 and Q(launch['outer_seconds'])>=Q(inner['seconds']),'Actual timing outer receipt differs')
    timed=self.unique(self.rows(q/'records122.jsonl'),ident,'timing '+scenario);self.check(set(timed)==expected(16),'All2,784 timing records required')
    for k,r in timed.items():
     self.check_row(r,j)
     for name in IDENTITY_FIELDS:self.check(r[name]==data[k][name],'Saved timing policy identity differs: '+name)
    self.timing[scenario]=timed;all_timing+=len(timed)
  self.check(all_timing==8352 and receipt['primary_rows']==5568 and receipt['timed_rows']==8352,'Execution receipt census differs')
  self.primary_data=data;self.binding=binding;self.algebra=dict(algebra);self.cohorts=cohorts;self.timings=tim
  self.counts.update(primary_rows=5568,timed_rows=8352,primary_algebra=algebra,accepted_actions=sum(r['accepted_improvement'] for r in raw),paid_refinement_attempts=sum(r['paid_refinement_attempt_count'] for r in raw))
  if a.interrupted_primary:self.interruption()
  self.completed.append('primary')
 def interruption(self):
  a=self.a;p=a.interrupted_primary;forensic=self.read(p/'INTERRUPTION_FORENSIC122.json');protocol=self.read(ROOT/'RESTART_PROTOCOL122.json')
  self.check(git_bytes(RESTART,(ROOT/'RESTART_PROTOCOL122.json').relative_to(REPO))==(ROOT/'RESTART_PROTOCOL122.json').read_bytes(),'Administrative restart protocol differs from actual published barrier')
  self.check(protocol['source_commit']==a.source_commit and protocol['state_commit']==a.state_commit and protocol['new_population_draws']==0,'Administrative restart changes F/D or population count')
  self.check(protocol['original_attempt']==str(p.relative_to(ROOT)) and protocol['new_attempt']==str(a.primary.relative_to(ROOT)),'Restart protocol identifies different old/new attempts')
  self.check(protocol['forensic_sha256']==sha(p/'INTERRUPTION_FORENSIC122.json'),'Restart forensic bytes changed')
  self.check(forensic['source_commit']==a.source_commit and forensic['state_commit']==a.state_commit and forensic['exit_code'] is None and forensic['actual_full_external_wall_seconds'] is None,'Interrupted campaign given an invented exit or full runtime')
  for name in ('EXECUTION122.json','FAILURE122.json','OUTER_EXECUTION122.json'):
   self.check(not (p/name).exists(),'Interrupted parent assigned an unavailable terminal receipt')
  self.check(not (ROOT/protocol['original_launcher']/'LAUNCH122.json').exists(),'Interrupted external launcher assigned an unavailable terminal receipt')
  for r in forensic['files']:
   q=self.bind(p/r['path']);self.check(q.is_relative_to(p) and q.stat().st_size==r['bytes'] and sha(q)==r['sha256'],'Interrupted original evidence changed')
  names=(('',None,5568),('timing/attempt00',0,2784),('timing/attempt01',1,1456));count=0;cost=Q(0)
  for relative,repeat,n in names:
   q=p/relative;path=self.bind(q/'records122.jsonl');seen=set()
   with path.open() as stream:
    for line in stream:
     r=json.loads(line);k=ident(r);self.check(k not in seen,'Duplicate interrupted record');seen.add(k);self.check_row(r,repeat)
     for name in IDENTITY_FIELDS+('complete_policy_lower','complete_policy_upper','certified_regret_upper','raw_proposal_kept'):
      self.check(r[name]==self.primary_data[k][name],'Interrupted/restarted policy mismatch: '+name)
   self.check(len(seen)==n,'Interrupted record census differs');count+=len(seen)
   cohort=self.rows(q/'cohorts122.jsonl');self.check(len(cohort)==(91 if repeat==1 else 174),'Interrupted completed cohort census differs')
   cost+=sum((Q(z['complete_cohort_seconds']) for z in cohort),Q(0))
  self.interruption_cost_lower=cost
  comparison_path=a.primary/'RESTART_COMPARISON122.json'
  if comparison_path.exists():
   comparison=self.read(comparison_path)
   self.check(comparison['status']=='identical' and comparison['source_commit']==a.source_commit and comparison['state_commit']==a.state_commit and comparison['actor_commit']==M,'Administrative restart comparison scientific identity differs')
   self.check(comparison['restart_protocol_commit']==RESTART and comparison['protocol_sha256']==sha(ROOT/'RESTART_PROTOCOL122.json') and comparison['original_forensic_sha256']==sha(p/'INTERRUPTION_FORENSIC122.json') and comparison['primary02_sha256']==sha(a.primary/'records122.jsonl'),'Administrative restart comparison byte identity differs')
   self.check(comparison['total_rows']==9808 and comparison['new_population_observations']==0 and comparison['original_parent_wall_seconds'] is None and Q(comparison['interrupted_completed_cohort_seconds_lower'])==cost,'Restart comparison cost/population scope differs')
   datasets=comparison['datasets'];self.check([r['rows'] for r in datasets]==[5568,2784,1456],'Saved restart comparison census differs')
   for r in datasets:
    q=self.bind(REPO/r['path']);self.check(r['status']=='identical' and sha(q)==r['sha256'] and r['identity_fields']==list(IDENTITY_FIELDS+('complete_policy_lower','complete_policy_upper','certified_regret_upper','raw_proposal_kept')),'Restart comparison field/source identity differs')
   reader=self.bind(ROOT/'verification122/restart_compare122.py');self.check(sha(reader)==comparison['reader_sha256'],'Administrative comparison reader changed after execution')
  self.counts.update(interrupted_rows_compared=count,interrupted_primary_rows=5568,interrupted_complete_timing0_rows=2784,interrupted_partial_timing1_rows=1456,interrupted_nonoverlapping_completed_cohort_seconds_lower=cost,interrupted_parent_full_clock_unknown=True)
 def independent(self):
  a=self.a;p=a.independent;receipt=self.stage('independent',p)
  inputs=self.read(p/'INPUTS122.json');self.check(inputs['primary_sha256']==sha(a.primary/'records122.jsonl') and inputs['primary_state_binding']==self.binding,'Independent result binds a different primary')
  algebra=self.read(p/'ALGEBRA_AUDIT122.json');self.check(algebra['counts']==self.algebra and algebra['primary_sha256']==inputs['primary_sha256'] and algebra['primary_state_binding']==self.binding,'Independent saved algebra audit differs from actual full replay')
  self.check(algebra['verifier_sha256']==sha(ROOT/'code122/algebra_audit122.py') and algebra['original_economic_queries']==0 and algebra['production_service_imported'] is False,'Algebra audit scope differs')
  evaluations=self.rows(p/'POLICY_EVALUATIONS122.jsonl');evmap=self.unique(evaluations,lambda r:(r['key_id'],r['bins']),'original independent evaluation')
  wanted={original_key(r,f) for r in self.primary_data.values() for f in ('action','baseline_action','raw_proposal_kept')};wanted.discard(None)
  self.check({r['key_id'] for r in evaluations}==wanted,'Final/baseline/raw original-policy census incomplete')
  self.check(all((k,64) in evmap for k in wanted),'Independent64-cell base required for every original action')
  best=self.unique(self.rows(p/'BEST_POLICY_BOUNDS122.jsonl'),lambda r:r['key_id'],'best original policy');self.check(set(best)==wanted,'Independent merged key census differs')
  for k,r in best.items():
   ev=[z for z in evaluations if z['key_id']==k]
   for field in ('q_lower','j_lower','optimum_lower'):self.check(Q(r[field])==max(Q(z[field]) for z in ev),'Independent lower mesh intersection differs')
   for field in ('q_upper','j_upper'):self.check(Q(r[field])==min(Q(z[field]) for z in ev),'Independent upper mesh intersection differs')
   self.check(r['bins']==max(z['bins'] for z in ev),'Independent finest mesh identity differs')
  optima={}
  for r in best.values():
   k=(tuple(r['state_hex']),r['alpha']);lo,hi=Q(r['optimum_lower']),Q(r['q_upper'])
   if k in optima:lo=max(lo,optima[k][0]);hi=min(hi,optima[k][1])
   self.check(lo<=hi,'Independent original optimum inconsistent');optima[k]=(lo,hi)
  comparisons=self.unique(self.rows(p/'COMPARISONS122.jsonl'),ident,'independent comparison');self.check(set(comparisons)==expected(N),'All5,568 independent comparisons required')
  accepted_confirmed=0;accepted_contained=0;accepted_unresolved=0
  for k,z in comparisons.items():
   r=self.primary_data[k];fk,bk=original_key(r),original_key(r,'baseline_action');new,old=best[fk],best[bk]
   self.check(z['source_commit']==a.source_commit and z['state_commit']==a.state_commit and z['actor_commit']==M,'Independent F/D/M differs')
   self.check(z['final_key_id']==fk and z['baseline_key_id']==bk and z['initial_raw_proposal_key_id']==original_key(r,'raw_proposal_kept'),'Independent final/baseline/raw action identity differs')
   self.check(z['original_action_hex']==r['action_hex'] and z['state_hex']==r['state_hex'],'Independent state/action bits differ')
   for prefix,source in [('independent_policy','j'),('independent_q','q')]:
    for side in ('lower','upper'):self.check(Q(z[prefix+'_'+side])==Q(new[source+'_'+side]),'Comparison policy interval differs from actual independent reconstruction')
   lo,hi=optima[(tuple(r['state_hex']),r['alpha'])];reglow=max(Q(0),Q(new['j_lower'])-hi);reghigh=Q(new['j_upper'])-lo
   self.check(Q(z['independent_optimum_lower'])==lo and Q(z['independent_optimum_upper'])==hi and Q(z['independent_regret_lower'])==reglow and Q(z['independent_regret_upper'])==reghigh,'Original optimum/regret reconstruction differs')
   cap=Q(1,8)+sum(map(Q,r['state']))/16;self.check(Q(z['squared_original_action_error_upper'])==min(cap*cap,reghigh),'Original action-error bound differs')
   same=fk==bk;gl,gu=(Q(0),Q(0)) if same else (Q(old['j_lower'])-Q(new['j_upper']),Q(old['j_upper'])-Q(new['j_lower']))
   claim=Q(r['certified_policy_gain_lower']);confirmed=same or gl>=claim;contained=Q(new['j_lower'])>=Q(r['complete_policy_lower']) and Q(new['j_upper'])<=Q(r['complete_policy_upper']);compatible=max(Q(new['j_lower']),Q(r['complete_policy_lower']))<=min(Q(new['j_upper']),Q(r['complete_policy_upper']))
   self.check((Q(z['independent_gain_lower']),Q(z['independent_gain_upper']))==(gl,gu) and Q(z['theorem_gain_lower'])==claim,'Raw independent/theorem gains differ')
   self.check(z['independent_gain_claim_confirmed']==confirmed and z['independent_candidate_interval_contained']==contained and z['independent_compatibility']==compatible and compatible,'Independent flags inconsistent with exact endpoints')
   self.check(gl<=TAU and gu>=claim,'Independent and proved gains incompatible')
   if r['accepted_improvement']:accepted_confirmed+=confirmed;accepted_contained+=contained;accepted_unresolved+=not(confirmed and contained)
  claims=self.unique(self.rows(p/'CLAIM_CHECKS122.jsonl'),lambda r:tuple(r['identity']),'accepted claim') if (p/'CLAIM_CHECKS122.jsonl').exists() else {}
  self.check(set(claims)=={k for k,r in self.primary_data.items() if r['accepted_improvement']},'Every accepted original claim needs independent ladder record')
  for r in claims.values():
   attempted=[z['requested_bins'] for z in r['attempts']];self.check(attempted==[64,128,256,512][:len(attempted)] and attempted,'Independent claim precision ladder differs')
  manifest=self.read(p/'WITNESS_MANIFEST122.json');self.check(manifest['no_record_omissions'] is True,'Witness omission declared')
  sealed=self.rows(p/'SEALED_WITNESS_PARTS122.jsonl');self.check(sealed==manifest['parts'],'Sealed and final witness manifests differ')
  lines=0
  for j,r in enumerate(manifest['parts']):
   path=self.bind(p/r['path']);self.check(path.name==f'part{j:05d}.jsonl.gz','Witness part sequence has a gap')
   self.check(path.stat().st_size==r['bytes'] and sha(path)==r['sha256'],'Original independent witness bytes differ')
   with gzip.open(path,'rb') as f:
    for line in f:self.check(line.endswith(b'\n'),'Incomplete independent witness record');lines+=1
  self.check(lines==manifest['records']==sum(r['terminal_contexts'] for r in evaluations),'Witness complete line/CRC and evaluation census differs')
  self.check(receipt['primary_rows']==5568 and receipt['unique_policy_keys']==len(wanted) and receipt['actual_independent_evaluations']==len(evmap),'Independent execution census differs')
  self.check(receipt['accepted_primary_decisions']==self.counts['accepted_actions'] and receipt['accepted_gain_claims_independently_confirmed']==accepted_confirmed and receipt['accepted_candidate_intervals_independently_contained']==accepted_contained and receipt['accepted_joint_checks_unresolved']==accepted_unresolved,'Accepted-only independent validation denominator/counters differ')
  self.independent_data=comparisons;self.counts.update(unique_independent_policy_keys=len(wanted),independent_evaluations=len(evmap),independent_witness_records=lines,accepted_independent_gain_confirmations=accepted_confirmed,accepted_independent_containments=accepted_contained,accepted_independent_joint_unresolved=accepted_unresolved);self.completed.append('independent')
 def stats(self):
  a=self.a;p=a.stats;self.stage('stats',p);inputs=self.read(p/'INPUTS122.json')
  self.check(inputs['primary_sha256']==sha(a.primary/'records122.jsonl') and inputs['independent_sha256']==sha(a.independent/'COMPARISONS122.jsonl') and inputs['primary_states']==N,'Statistics input bytes or sample differs')
  exponent=Q(169,16);exp_lower=sum((exponent**j/math.factorial(j) for j in range(31)),Q(0));radius=13*TAU/32;signed_radius=13*TAU/16
  witness=self.read(p/'RADIUS_WITNESS122.json');self.check(Q(witness['exponent'])==exponent and Q(witness['exp_lower'])==exp_lower and exp_lower>23200,'Exact Taylor probability witness differs')
  self.check(116*2/exp_lower<Q(1,100) and 348*2/exp_lower<Q(3,100) and 232*Q(1,23200)==Q(1,100),'Joint probability allocation fails')
  safe=self.unique(self.rows(p/'STATS122.jsonl'),cell,'safe statistic');signed=self.unique(self.rows(p/'SIGNED_COMPARISONS122.jsonl'),lambda r:(cell(r),r['comparator']),'signed statistic')
  self.check(set(safe)=={k+(s,) for k in catalogue() for s in SERVICES[1:]},'All116 safe cells required')
  self.check(set(signed)=={(k,c) for k in cells() for c in ('online-control','quadratic-value-control')},'All348 signed cells required')
  thresholds=(Q(1,2**24),Q(1,2**20));event_count=0
  for k,r in safe.items():
   rows=[self.independent_data[(k[0],j,*k[1:])] for j in range(N)];bounds=[(max(Q(z['theorem_gain_lower']),Q(z['independent_gain_lower']),Q(0)),min(TAU,Q(z['independent_gain_upper']))) for z in rows]
   self.check(all(Q(0)<=lo<=hi<=TAU for lo,hi in bounds),'Safe proof/independent intersection invalid')
   ml,mh=avg(lo for lo,hi in bounds),avg(hi for lo,hi in bounds);events=[]
   self.check(len(r['threshold_events'])==2,'Two prospective events per safe cell required')
   for threshold,event in zip(thresholds,r['threshold_events']):
    count=sum(Q(z['theorem_gain_lower'])>=threshold for z in rows);lo,hi=Q(event['lower']),Q(event['inversion_upper'])
    self.check(Q(event['threshold'])==threshold and event['successes']==count,'Threshold or certified event count changed')
    if count==0:self.check(lo==hi==0,'Zero-success exact bound differs')
    else:
     def tail(q):return sum((Q(math.comb(N,j))*q**j*(1-q)**(N-j) for j in range(count,N+1)),Q(0))
     self.check(Q(0)<=lo<hi<=1 and hi-lo==Q(1,2**48),'Exact binomial bisection bracket differs')
     self.check(tail(lo)<=Q(1,23200)<tail(hi) and Q(event['delta'])==Q(1,23200),'Exact one-sided binomial inversion fails')
    self.check(Q(event['mean_gain_lower_from_event'])==threshold*lo,'Event-to-economic-mean bound differs');events.append(threshold*lo);event_count+=1
   pl,pu=max(Q(0),ml-radius,*events),min(TAU,mh+radius)
   self.check(tuple(map(Q,(r['sample_gain_lower'],r['sample_gain_upper'],r['population_gain_lower'],r['population_gain_upper'])))==(ml,mh,pl,pu),'Safe numerical/population interval differs')
   self.check(r['n']==32 and r['simultaneous_family_size']==116 and Q(r['delta'])==Q(1,100) and list(map(Q,r['support']))==[Q(0),TAU] and Q(r['joint_failure_at_most'])==Q(1,20),'Safe confidence scope differs')
   self.check(Q(r['hoeffding_radius_upper'])==radius and r['source_proof_and_independent_intersection'] is True,'Safe theorem/independent scope mislabeled')
  for (k,kind),r in signed.items():
   ck=(k[0],0,'online','online','control') if kind=='online-control' else (k[0],k[1] or 5,'quadratic','value','control')
   self.check(tuple(r['comparator_key'])==ck,'Signed conventional comparator changed')
   bounds=[]
   for j in range(N):
    u=self.independent_data[(k[0],j,*k[1:])];v=self.independent_data[(ck[0],j,*ck[1:])]
    bounds.append((Q(0),Q(0)) if u['original_action_hex']==v['original_action_hex'] else (max(-TAU,Q(v['independent_policy_lower'])-Q(u['independent_policy_upper'])),min(TAU,Q(v['independent_policy_upper'])-Q(u['independent_policy_lower']))))
   self.check(all(-TAU<=lo<=hi<=TAU for lo,hi in bounds),'Signed support intersection invalid')
   ml,mh=avg(lo for lo,hi in bounds),avg(hi for lo,hi in bounds);pl,pu=(Q(0),Q(0)) if k==ck else (max(-TAU,ml-signed_radius),min(TAU,mh+signed_radius))
   self.check(tuple(map(Q,(r['sample_gain_lower'],r['sample_gain_upper'],r['population_gain_lower'],r['population_gain_upper'])))==(ml,mh,pl,pu),'Signed numerical/population interval differs')
   self.check(r['n']==N and r['simultaneous_family_size']==348 and Q(r['delta'])==Q(3,100) and list(map(Q,r['support']))==[-TAU,TAU] and Q(r['joint_failure_at_most'])==Q(1,20) and Q(r['hoeffding_radius_upper'])==signed_radius and r['exact_identical_method']==(k==ck),'Signed confidence scope differs')
  self.safe=safe;self.signed=signed;self.counts.update(safe_population_cells=116,threshold_event_bounds=event_count,signed_population_cells=348,joint_failure_probability='1/20',positive_safe_population_lower_bounds=sum(Q(r['population_gain_lower'])>0 for r in safe.values()));self.completed.append('stats')
 def reporting_repairs(self):
  a=self.a;p=a.report;schema=self.read(p/'REPORTING_ADAPTER122.json');protocol=self.read(p/'REPORTING_PROTOCOL_ADAPTER122.json')
  for label,r in (('schema',schema),('protocol',protocol)):
   self.check(r['status']=='executed' and r['source_commit_F']==a.source_commit,'Reporting correction did not execute on actual F: '+label)
   source=self.bind(REPO/r['adapter_path']);commit=r['reporting_adapter_commit']
   self.check(len(commit)==40 and all(c in '0123456789abcdef' for c in commit),'Full reporting correction commit missing')
   self.check(commit==REPORTING_REPAIR,'Reporting correction is not the actual published pre-execution barrier')
   self.check(sha(source)==r['adapter_sha256'] and git_bytes(commit,source.relative_to(REPO))==source.read_bytes(),'Reporting correction source differs from actual published commit')
   self.check(r['frozen_reporter_sha256']==sha(ROOT/'code122/report122.py') and r['original_frozen_files_changed'] is False and r['saved_input_files_changed'] is False,'Reporting correction changed a scientific/input byte')
   self.check(all(r[f]==0 for f in ('new_states','new_training','new_economic_evaluations')) and r['original_frozen_attempt_success_asserted'] is False,'Reporting correction claimed new economics or original success')
  self.check(schema['reporting_adapter_commit']==protocol['reporting_adapter_commit'],'Schema/protocol correction commit differs')
  amendment=self.bind(ROOT/'provenance122/REPORTING_AMENDMENT122.md')
  self.check(sha(amendment)==protocol['reporting_amendment_sha256'] and git_bytes(protocol['reporting_adapter_commit'],amendment.relative_to(REPO))==amendment.read_bytes(),'Reporting amendment not bound to actual correction commit')
  schema_source=self.bind(REPO/protocol['schema_adapter_path'])
  self.check(sha(schema_source)==protocol['schema_adapter_sha256']==schema['adapter_sha256'],'Nested schema correction identity differs')
  expected={'exact_redundant_value_equalities':232,'safe_cells_checked':116,'frozen_economics_calls':1}
  self.check(schema['checks']==protocol['schema_checks']==expected,'Duplicate fields not checked by all232 exact equalities')
  self.check(schema['elapsed_clock_shared_with_protocol_adapter_not_additive'] is True and schema['elapsed_seconds']==protocol['elapsed_seconds'],'Nested reporting component clock double count')
  expected={'unchanged_frozen_price_tables_calls':1,'original_diagnostic_rows':[2784,28800,384,96],'matched_timing_policy_pairs':1800,'matched_state_units':16,'matched_timing_constraint_rows':21600,'unchanged_primary_table_rows':[696,7200,96],'all_three_clock_intersections':96}
  self.check(all(protocol['protocol_checks'][k]==v for k,v in expected.items()),'Protocol correction census differs')
  self.check(protocol['primary32_tables_changed'] is False and protocol['statistical_rules_changed'] is False and protocol['cost_rules_changed'] is False and protocol['reporting_aggregation_changed_to_match_frozen_protocol'] is True,'Protocol correction scope concealed or changed')
  failed=a.original_report;failure=self.read(failed/'FAILURE122.json');outer=self.read(failed/'OUTER_EXECUTION122.json');start=self.read(failed/'START122.json');verified=self.read(failed/'VERIFIED_SOURCE122.json')
  self.check(not (failed/'EXECUTION122.json').exists() and failure['status']=='failed' and outer['status']=='failed' and outer['exit_code']!=0,'Original frozen report falsely marked successful')
  self.check("TypeError: dict() got multiple values for keyword argument 'raw_independent_sample_gain_lower'" in failure['traceback'],'Actual original reporter failure differs from disclosed schema defect')
  self.check(verified['source_commit']==a.source_commit and verified['manifest_sha256']==sha(ROOT/'SOURCE_FREEZE122.json'),'Original failed report source differs')
  command=start['argv'];self.check(Path(command[0]).name=='report122.py','Original failed attempt did not invoke untouched frozen reporter')
  self.check(command[command.index('--source-commit')+1]==a.source_commit,'Original failed report F differs')
  for argument,path in (('--primary',a.primary),('--independent',a.independent),('--stats',a.stats)):
   self.check(Path(command[command.index(argument)+1]).name==path.name,'Original/corrected reporting inputs differ: '+argument)
  self.check(Q(outer['outer_seconds'])>=Q(failure['seconds'])>=0,'Original reporting failure cost omitted or impossible')
  self.report_failure=outer;self.reporting_protocol=protocol
 def report(self):
  a=self.a;p=a.report;self.stage('report',p);self.reporting_repairs()
  inputs=self.read(p/'INPUTS_REPORT122.json')
  for r in inputs['files']:
   q=REPO/r['path'];self.bind(q);self.check(q.stat().st_size==r['bytes'] and sha(q)==r['sha256'],'Reporter input content changed: '+r['path'])
  manifest=self.read(p/'OUTPUT_MANIFEST122.json')
  for r in manifest['files']:
   q=self.bind(p/r['path']);self.check(q.is_relative_to(p.resolve()) and q.stat().st_size==r['bytes'] and sha(q)==r['sha256'],'Saved reporter output content changed')
  table=self.unique(self.rows(p/'POLICY_CELLS122.jsonl'),cell,'policy reporting cell');self.check(set(table)==cells(),'All174 report cells required')
  for k,r in table.items():
   saved=[self.primary_data[(k[0],j,*k[1:])] for j in range(N)];ind=[self.independent_data[(k[0],j,*k[1:])] for j in range(N)]
   self.check(Q(r['original_policy_mean_lower'])==avg(Q(z['independent_policy_lower']) for z in ind) and Q(r['original_policy_mean_upper'])==avg(Q(z['independent_policy_upper']) for z in ind),'Reported original objective differs')
   self.check(r['changed_actions']==sum(z['accepted_improvement'] for z in saved) and r['paid_anchor_refinement_attempts']==sum(z['paid_refinement_attempt_count'] for z in saved),'Reported accepted/paid work count differs')
   self.check(r['accepted_action_independent_gain_confirmations']==sum(z['independent_gain_claim_confirmed'] for q,z in zip(saved,ind) if q['accepted_improvement']),'Unchanged zero included in accepted validation denominator')
  safe=self.unique(self.rows(p/'SERVICE_CONTRASTS122.jsonl'),cell,'report safe');signed=self.unique(self.rows(p/'SIGNED_POPULATION_COMPARISONS122.jsonl'),lambda r:(cell(r),r['comparator']),'report signed')
  self.check(set(safe)==set(self.safe) and set(signed)==set(self.signed),'Reporter statistical family incomplete')
  for k,r in self.safe.items():self.check(all(safe[k][f]==v for f,v in r.items()),'Reporter altered original safe statistics')
  for k,r in self.signed.items():self.check(signed[k]==r,'Reporter altered original signed statistics')
  clocks=self.unique(self.rows(p/'CLOCKS122.jsonl'),lambda r:(r['scenario'],cell(r)),'report clock');self.check(set(clocks)=={(s,k) for s in SCENARIOS for k in cells()},'All696 clock rows required')
  allocations=self.unique(self.rows(p/'ACQUISITION_ALLOCATIONS122.jsonl'),lambda r:tuple(r[f] for f in FIELDS[:-1]),'acquisition allocation')
  historical=self.unique(self.rows(R121/'results121/report-attempt01/tables121/fit_and_acquisition121.jsonl'),lambda r:tuple(r[f] for f in FIELDS[:-1]),'historical allocation')
  self.check(set(historical)=={k for k in catalogue() if k[2]!='online'} and set(allocations)==set(catalogue()),'56 historical plus2 derived online acquisition accounts required')
  processes=self.unique(self.rows(p/'PROCESS_COSTS122.jsonl'),lambda r:r['scenario'],'process cost')
  child=sum(Q(z['outer_seconds']) for z in self.timings['processes']);totals={'primary32':Q(self.receipts['primary']['outer']['outer_seconds'])-child}
  totals.update({f'timing{z["repeat"]:02d}':Q(z['outer_seconds']) for z in self.timings['processes']})
  for scenario in SCENARIOS:
   residual=totals[scenario]-sum(Q(z['complete_cohort_seconds']) for z in self.cohorts[scenario].values());self.check(residual>=0 and Q(processes[scenario]['shared_process_residual_seconds'])==residual,'Common process residual omitted or double counted')
   for k in cells():
    c=clocks[scenario,k];cohort=self.cohorts[scenario][k];acq=Q(0) if k[2]=='online' else Q(historical[k[:4]]['complete_allocated_acquisition_seconds'])
    self.check(Q(allocations[k[:4]]['complete_allocated_acquisition_seconds'])==acq and Q(c['historical_complete_acquisition_seconds'])==acq,'Original acquisition charge differs')
    self.check(Q(c['cold_load_seconds'])==Q(cohort['cold_load_seconds']) and Q(c['complete_cohort_seconds'])==Q(cohort['complete_cohort_seconds']) and Q(c['shared_process_residual_seconds'])==residual,'Full service clock differs')
    self.check(Q(c['fully_allocated_matching_cohort_seconds'])==acq+Q(cohort['complete_cohort_seconds'])+residual,'Complete standalone bill differs')
  volumes=self.unique(self.rows(p/'COST_VOLUMES122.jsonl'),lambda r:(r['scenario'],r['volume'],cell(r)),'volume cost')
  self.check(set(volumes)=={(s,n,k) for s in SCENARIOS for n in VOLUMES for k in cells()},'All2,784 predeclared cost-volume cells required')
  for (s,n,k),r in volumes.items():
   c=clocks[s,k];cost=Q(c['historical_complete_acquisition_seconds'])+Q(c['shared_process_residual_seconds'])+Q(c['cold_load_seconds'])+(Q(c['complete_cohort_seconds'])-Q(c['cold_load_seconds']))*n/c['n']
   self.check(Q(r['total_allocated_seconds'])==cost and Q(r['seconds_per_decision'])==cost/n,'Conditional measured-cost extrapolation differs')
   self.check(r['economic_state_units']==(N if s=='primary32' else 16),'Timing cost paired with wrong state economics')
  self.price_menus(p,volumes)
  legacy_volumes=self.unique(self.rows(p/'FROZEN_CODE_DIAGNOSTIC_COST_VOLUMES122.jsonl'),lambda r:(r['scenario'],r['volume'],cell(r)),'original diagnostic volume')
  self.check(set(legacy_volumes)==set(volumes),'Frozen diagnostic cost-volume census differs')
  for k,r in legacy_volumes.items():
   expected=dict(volumes[k],economic_state_units=N)
   self.check(r==expected,'Diagnostic/corrected cost differs beyond declared state-count label')
  self.price_menus(p,legacy_volumes,'FROZEN_CODE_DIAGNOSTIC_',False)
  summary=self.read(p/'SUMMARY_REPORT122.json')
  for name,value in [('primary_decisions',5568),('timed_decisions',8352),('policy_cells',174),('treatment_population_cells',116),('signed_population_cells',348),('accepted_action_validation_denominator',self.counts['accepted_actions']),('accepted_action_independent_gain_confirmations',self.counts['accepted_independent_gain_confirmations']),('accepted_action_independent_candidate_containment',self.counts['accepted_independent_containments']),('positive_population_gain_cells',self.counts['positive_safe_population_lower_bounds'])]:self.check(summary[name]==value,'Reporter summary census differs: '+name)
  self.check(summary['source_commit']==a.source_commit and summary['state_commit']==a.state_commit and summary['actor_commit']==M and summary['population_adoption_claim'] is False and summary['neural_exclusive_advantage_claim'] is False,'Reporter source/adoption scope differs')
  total=sum(Q(self.receipts[s]['outer']['outer_seconds']) for s in ('states','primary','independent','stats'))
  self.check(Q(summary['actual_new_scientific_stage_seconds_excluding_current_report'])==total,'Actual stage cost double counted or omitted')
  self.report_summary=summary
  if a.cost_ledger:self.cost_ledger()
  self.completed.append('report')
 def cost_ledger(self):
  a=self.a;ledger=self.read(a.cost_ledger);inputs=self.read(a.cost_ledger.parent/'INPUTS_COST_LEDGER122.json')
  self.check(ledger['status']=='saved_receipt_cost_census' and ledger['source_commit']==a.source_commit and ledger['state_commit']==a.state_commit,'Whole-study cost ledger identity differs')
  reader=self.bind(ROOT/'verification122/research_cost_ledger122.py');self.check(sha(reader)==ledger['reader_sha256'],'Cost ledger reader changed after recorded execution')
  for r in inputs['files']:
   q=self.bind(REPO/r['path']);self.check(q.stat().st_size==r['bytes'] and sha(q)==r['sha256'],'Cost ledger input receipt changed')
  total=Q(0);categories=collections.defaultdict(Q);seen=set();outerhashes=set()
  for r in ledger['clock_rows']:
   p=self.bind(REPO/r['source_path']);obj=self.read(p);self.check(sha(p)==r['source_sha256'],'Cost clock receipt identity differs')
   fingerprint=(r['source_sha256'],tuple(tuple(x) for x in r['clock_fields']))
   self.check(fingerprint not in seen,'Nested/duplicate cost clock counted twice');seen.add(fingerprint)
   amount=Q(0)
   for fields in r['clock_fields']:
    value=obj
    for field in fields:value=value[field]
    self.check(Q(value)>=0,'Negative observed research clock');amount+=Q(value)
   self.check(amount==Q(r['seconds_exact']) and r['scientific_standalone_service_allocation_changed'] is False,'Cost ledger changed recorded clock or service allocation')
   self.check('/timing/' not in r['source_path'] and 'REPORTING_ADAPTER122.json' not in r['source_path'] and 'REPORTING_PROTOCOL_ADAPTER122.json' not in r['source_path'],'Nested timing/adapter clocks counted independently')
   total+=amount;categories[r['category']]+=amount
   if r['clock_fields']==[['outer_seconds']]:outerhashes.add(r['source_sha256'])
  self.check({k:str(v) for k,v in categories.items()}==ledger['category_sums_seconds_exact'] and total==Q(ledger['recorded_nonoverlapping_job_seconds_sum']),'Research clock exact aggregation differs')
  for p in [a.states,a.primary,a.independent,a.stats,a.report,a.original_report]:
   self.check(sha(p/'OUTER_EXECUTION122.json') in outerhashes,'Whole-study ledger omitted a completed scientific/reporting success or failure')
  lower=Q(ledger['interrupted_completed_cohort_seconds_lower']);self.check(lower==self.interruption_cost_lower,'Interrupted work lower bound omitted or misrepresented')
  self.check(Q(ledger['recorded_job_sum_plus_interruption_lower'])==total+lower and Q(ledger['observed_research_and_publication_job_seconds_lower_including_this_census'])==total+lower+Q(ledger['census_elapsed_seconds']),'Whole-study observed lower bound arithmetic differs')
  self.check(ledger['complete_interrupted_parent_outer_seconds'] is None and ledger['whole_study_exact_total_seconds'] is None and ledger['whole_study_exact_total_unavailable'] is True,'Unavailable complete study cost invented')
  self.check(ledger['standalone_scientific_service_allocation_unchanged'] is True and ledger['original_interruption_or_frozen_report_success_asserted'] is False,'Research ledger altered economic comparison or failed status')
  self.counts.update(recorded_research_and_publication_clock_rows=len(ledger['clock_rows']),recorded_nonoverlapping_job_seconds=total,whole_study_observed_seconds_lower=Q(ledger['observed_research_and_publication_job_seconds_lower_including_this_census']),whole_study_exact_total_unavailable=True)
 def price_menus(self,p,volumes,prefix='',matched=True):
  def whole():return {'empty':False,'lower':Q(0),'lower_closed':True,'upper':None,'upper_closed':False}
  def empty():return {'empty':True,'lower':None,'lower_closed':False,'upper':None,'upper_closed':False}
  def domain(g,t):
   if t==0:return whole() if g>0 else empty()
   if t>0:return empty() if g<=0 else dict(empty=False,lower=Q(0),lower_closed=True,upper=g/t,upper_closed=False)
   boundary=g/t
   return whole() if boundary<0 else dict(empty=False,lower=boundary,lower_closed=False,upper=None,upper_closed=False)
  def intersect(x,y):
   if x['empty'] or y['empty']:return empty()
   lo=max(x['lower'],y['lower']);lc=all(d['lower_closed'] for d in (x,y) if d['lower']==lo);ends=[d['upper'] for d in (x,y) if d['upper'] is not None];hi=min(ends) if ends else None;hc=all(d['upper_closed'] for d in (x,y) if d['upper']==hi) if hi is not None else False
   return empty() if hi is not None and (lo>hi or lo==hi and not(lc and hc)) else dict(empty=False,lower=lo,lower_closed=lc,upper=hi,upper_closed=hc)
  def decode(d):return {k:Q(v) if k in ('lower','upper') and v is not None else v for k,v in d.items()}
  rows=self.rows(p/(prefix+'PRICE_CONSTRAINTS122.jsonl.gz'));constraints=self.unique(rows,lambda r:(r['scenario'],r['volume'],cell(r['candidate']),cell(r['comparator'])),'full-menu price constraint')
  neural={k for k in cells() if k[2]=='relu'};pairs={(k,b) for k in neural for b in cells() if b[0]==k[0] and b[2]!='relu'}
  self.check(set(constraints)=={(s,n,k,b) for s in SCENARIOS for n in VOLUMES for k,b in pairs},'All28,800 full-menu conventional price constraints required')
  bounds={};menus={}
  for s,n,k,b in constraints:
   units=16 if matched and s!='primary32' else N
   if (units,k,b) not in bounds:
    paired=[]
    for j in range(units):
     x=self.independent_data[(k[0],j,*k[1:])];y=self.independent_data[(b[0],j,*b[1:])]
     paired.append((Q(0),Q(0)) if x['final_key_id']==y['final_key_id'] else (max(-TAU,Q(y['independent_policy_lower'])-Q(x['independent_policy_upper'])),min(TAU,Q(y['independent_policy_upper'])-Q(x['independent_policy_lower']))))
    bounds[units,k,b]=(sum((x[0] for x in paired),Q(0))/units,sum((x[1] for x in paired),Q(0))/units)
   lo,hi=bounds[units,k,b];extra=Q(volumes[s,n,k]['seconds_per_decision'])-Q(volumes[s,n,b]['seconds_per_decision']);r=constraints[s,n,k,b]
   lower,upper=domain(lo,extra),domain(hi,extra)
   self.check(Q(r['sample_gain_lower'])==lo and Q(r['sample_gain_upper'])==hi and Q(r['extra_seconds_per_decision'])==extra,'Price gain/cost premise differs')
   self.check(decode(r['sufficient_price_domain'])==lower and decode(r['upper_not_ruled_out_domain'])==upper and r['statistical_adoption_claim'] is False,'Exact strict price inequality or scope differs')
   self.check(r['policy_means_conditional_on_32_saved_states']==(units==N),'Menu economic cohort label contradicts exact row set')
   if units==16:self.check(r['policy_means_conditional_on_first_16_saved_states'] is True,'Fixed first16 timing cohort not disclosed')
   old=menus.get((s,n,k),(whole(),whole()));menus[s,n,k]=(intersect(old[0],lower),intersect(old[1],upper))
  saved=self.unique(self.rows(p/(prefix+'PRICE_MENUS122.jsonl')),lambda r:(r['scenario'],r['volume'],cell(r)),'full conventional menu');self.check(set(saved)==set(menus),'All384 full menus required')
  for k,(low,up) in menus.items():self.check(decode(saved[k]['sufficient_price_domain'])==low and decode(saved[k]['upper_not_ruled_out_domain'])==up,'Full menu intersection differs')
  allthree=self.unique(self.rows(p/(prefix+'ALL_THREE_CLOCK_INTERSECTIONS122.jsonl')),lambda r:(r['volume'],cell(r)),'all-clock intersection');self.check(set(allthree)=={(n,k) for n in VOLUMES for k in neural},'All96 three-clock intersections required')
  for (n,k),r in allthree.items():
   lo,hi=whole(),whole()
   for s in SCENARIOS[1:]:lo=intersect(lo,menus[s,n,k][0]);hi=intersect(hi,menus[s,n,k][1])
   self.check(decode(r['sufficient_price_domain'])==lo and decode(r['upper_not_ruled_out_domain'])==hi and r['clock_scenarios']==list(SCENARIOS[1:]),'All-clock intersection omitted an adverse clock')
  if matched:
   self.corrected_price_constraints=constraints;self.corrected_price_menus=saved
   self.counts.update(price_constraints=len(constraints),full_menus=len(saved),all_clock_intersections=len(allthree))
  else:
   changed=0
   for k,r in constraints.items():
    other=self.corrected_price_constraints[k]
    if k[0]=='primary32':self.check(r==other,'Primary32 constraint changed by post-freeze reporting repair')
    else:changed+=(r['sample_gain_lower'],r['sample_gain_upper'])!=(other['sample_gain_lower'],other['sample_gain_upper'])
   for k,r in saved.items():
    if k[0]=='primary32':self.check(r==self.corrected_price_menus[k],'Primary32 menu changed by post-freeze reporting repair')
   self.check(changed==self.reporting_protocol['protocol_checks']['changed_timing_mean_endpoint_rows'],'Reporting repair endpoint-change census differs')
   self.counts.update(preserved_frozen_diagnostic_price_constraints=len(constraints),preserved_frozen_diagnostic_menus=len(saved),protocol_corrected_timing_endpoint_rows=changed)
   del self.corrected_price_constraints,self.corrected_price_menus
 def package(self):
  a=self.a;self.check(a.build_receipt is not None,'Package verification requires actual --build-receipt');self.check(a.cost_ledger is not None,'Package verification requires the actual supplementary --cost-ledger')
  receipt=self.read(a.build_receipt);self.check(receipt['status']=='compiled_clean' and not receipt['issues'] and not receipt['placeholders'],'Actual four-document build is not clean')
  self.check(receipt['scientific_execution'] is False,'Typesetting mislabeled as science')
  documents={'ECTA','supp','appendix','RESPONSE_TO_REFEREE'}
  self.check({Path(r['path']).stem for r in receipt['pdfs']}==documents,'All four actual PDFs required')
  pdfs=[]
  for r in receipt['pdfs']:
   p=self.bind(ROOT/r['path']);self.check(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'] and p.read_bytes()[:5]==b'%PDF-','Actual PDF bytes differ')
   result=subprocess.run(['pdfinfo',str(p)],capture_output=True,text=True,check=True);match=re.search(r'^Pages:\s+(\d+)',result.stdout,re.M);self.check(bool(match),'Actual PDF page count unavailable');pdfs.append(dict(r,pages=int(match.group(1))))
  for doc,files in receipt['actual_project_inputs'].items():
   self.check(doc in documents,'Unexpected document recorder closure')
   for name,expected_sha in files.items():self.bind(ROOT/name);self.check(sha(ROOT/name)==expected_sha,'Built PDF source changed after actual build: '+name)
  for name,expected_sha in receipt['source_sha256'].items():self.bind(ROOT/name);self.check(sha(ROOT/name)==expected_sha,'Declared author source changed after actual build: '+name)
  for name,expected_sha in receipt.get('graphic_asset_sha256',{}).items():self.bind(ROOT/name);self.check(sha(ROOT/name)==expected_sha,'Built graphic asset changed')
  if a.pdf_manifest:
   manifest=self.read(a.pdf_manifest);self.check(bool(manifest['files']),'Empty source/PDF manifest')
   for r in manifest['files']:
    p=self.bind(ROOT/r['path']);self.check(p.is_relative_to(ROOT) and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'Source/PDF manifest mismatch')
   self.check({r['path'] for r in receipt['pdfs']}<={r['path'] for r in manifest['files']},'Source/PDF manifest omits a document')
  if a.package_manifest:
   manifest=self.read(a.package_manifest)
   self.check(manifest['path_root']=='repository' and manifest['self_excluded'] is True,'Package manifest root/self policy differs')
   for r in manifest['files']:
    p=self.bind(REPO/r['path']);self.check(p.is_relative_to(REPO) and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'Package byte manifest mismatch: '+r['path'])
   package_paths={r['path'] for r in manifest['files']}
   self.check(set(self.manifest['scientific_files'])<=package_paths,'Package omits a frozen transitive source dependency')
   required=[ROOT/'SOURCE_FREEZE122.json',a.states/'entropy122.bin',a.primary/'records122.jsonl',a.independent/'COMPARISONS122.jsonl',a.stats/'STATS122.jsonl',a.report/'SUMMARY_REPORT122.json',a.report/'REPORTING_ADAPTER122.json',a.report/'REPORTING_PROTOCOL_ADAPTER122.json',a.original_report/'FAILURE122.json',a.original_report/'OUTER_EXECUTION122.json',ROOT/'provenance122/REPORTING_AMENDMENT122.md',a.cost_ledger,a.cost_ledger.parent/'INPUTS_COST_LEDGER122.json']
   if a.interrupted_primary:
    required.extend([ROOT/'RESTART_PROTOCOL122.json',a.interrupted_primary/'INTERRUPTION_FORENSIC122.json',a.primary/'RESTART_COMPARISON122.json'])
    forensic=self.read(a.interrupted_primary/'INTERRUPTION_FORENSIC122.json')
    required.extend(a.interrupted_primary/r['path'] for r in forensic['files'])
   for q in required:
    self.check(str(q.relative_to(REPO)) in package_paths,'Package omits a required current/failure artifact: '+str(q))
  if a.transport_registry:self.transport()
  self.counts['pdfs']=pdfs;self.completed.append('package')
 def transport(self):
  registry=self.read(self.a.transport_registry);requests=registry['requests'];seen={};parts=0;bytes_total=0
  self.check(bool(requests),'Empty requested native-evidence transport registry')
  for name in requests:
   request=self.bind(ROOT/name);self.check(request.is_relative_to(ROOT/'transport122'),'Transport request outside declared transport directory')
   obj=self.read(request);self.check(obj['kind']=='lossless R122 executed-evidence transport' and obj['source_commit']==self.a.source_commit and obj['state_commit']==self.a.state_commit,'Transport scientific identity differs')
   files={r['path']:r for r in obj['files']};self.check(len(files)==len(obj['files'])==obj['native_file_count'] and sum(r['bytes'] for r in files.values())==obj['native_bytes'],'Transport native census differs')
   with tempfile.TemporaryDirectory(prefix='nbo122-readonly-transport-') as temporary:
    archive=Path(temporary)/'saved-evidence.zip';h=hashlib.sha256();size=0
    with archive.open('xb') as stream:
     for part in obj['parts']:
      p=self.bind(request.parent/part['path']);self.check(p.is_relative_to(request.parent) and p.stat().st_size==part['bytes'] and sha(p)==part['sha256'],'Transport part content differs')
      with p.open('rb') as original:
       for b in iter(lambda:original.read(1<<20),b''):stream.write(b);h.update(b);size+=len(b)
      parts+=1
    self.check(size==obj['archive_bytes'] and h.hexdigest()==obj['archive_sha256'],'Reconstructed transport archive differs');bytes_total+=size
    with zipfile.ZipFile(archive) as z:
     infos=z.infolist();self.check(len(infos)==len(files) and {r.filename for r in infos}==set(files),'Transport archive member census differs')
     for info in infos:
      r=files[info.filename];relative=Path(info.filename)
      self.check(not relative.is_absolute() and '..' not in relative.parts and info.filename.startswith('results122/') and '\\' not in info.filename and not info.is_dir() and ((info.external_attr>>16)&0o170000) in (0,0o100000),'Unsafe/nonregular transported member')
      p=self.bind(ROOT/relative);self.check(p.is_relative_to(ROOT/'results122') and p.stat().st_size==r['bytes']==info.file_size and sha(p)==r['sha256'],'Materialized native evidence differs from transport manifest')
      member=hashlib.sha256();n=0
      with z.open(info) as stream:
       for b in iter(lambda:stream.read(1<<20),b''):member.update(b);n+=len(b)
      self.check(n==r['bytes'] and member.hexdigest()==r['sha256'],'Archive-member/native byte identity differs')
      if info.filename in seen:self.check(seen[info.filename]==r,'Conflicting duplicated evidence across transport bundles')
      seen[info.filename]=r
  self.counts.update(evidence_transport_bundles=len(requests),evidence_transport_parts=parts,evidence_transport_compressed_bytes=bytes_total,evidence_transport_native_files=len(seen),evidence_transport_native_bytes=sum(r['bytes'] for r in seen.values()))

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-commit',required=True);p.add_argument('--state-commit',required=True);p.add_argument('--through',choices=STAGES,default='report')
 defaults={'states':'states-attempt01','primary':'primary-attempt02','independent':'independent-attempt01','stats':'statistics-attempt01','report':'report-attempt02'}
 for stage,name in defaults.items():p.add_argument('--'+stage,type=Path,default=ROOT/'results122'/name)
 p.add_argument('--interrupted-primary',type=Path,default=ROOT/'results122/primary-attempt01');p.add_argument('--original-report',type=Path,default=ROOT/'results122/report-attempt01')
 p.add_argument('--cost-ledger',type=Path);p.add_argument('--transport-registry',type=Path);p.add_argument('--build-receipt',type=Path);p.add_argument('--pdf-manifest',type=Path);p.add_argument('--package-manifest',type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
 for name in ('states','primary','independent','stats','report','interrupted_primary','original_report','cost_ledger','transport_registry','build_receipt','pdf_manifest','package_manifest','output'):
  if getattr(a,name) is not None:setattr(a,name,getattr(a,name).resolve())
 a.output.mkdir(parents=True,exist_ok=False);started=time.perf_counter();v=Verification(a)
 write(a.output/'START_VERIFICATION122.json',dict(argv=sys.argv,started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),source_commit=a.source_commit,state_commit=a.state_commit,through=a.through,verifier_sha256=sha(Path(__file__)),scope='Saved-evidence, exact algebra/probability/cost and optional PDF custody validation only; zero new states, training, economic evaluations or clocks.'))
 try:
  for stage in STAGES[:STAGES.index(a.through)+1]:
   getattr(v,stage)();print(json.dumps({'verified_through':stage,'assertions':v.checks,'elapsed_seconds':time.perf_counter()-started}),flush=True)
  write(a.output/'INPUTS_VERIFICATION122.json',{'files':sorted(v.inputs.values(),key=lambda r:r['path'])})
  write(a.output/'VERIFICATION122.json',dict(status='verified',verified_through=a.through,completed_stages=v.completed,assertions=v.checks,counts=v.counts,elapsed_seconds=time.perf_counter()-started,new_states=0,new_training=0,new_economic_evaluations=0,new_timing_processes=0,source_specific_CI_success_asserted=False,full_package_success=a.through=='package',scope='Only the requested through-stage and prerequisites are verified; future missing stages and old experiments are not claimed complete.'))
 except BaseException:
  write(a.output/'FAILURE_VERIFICATION122.json',dict(status='failed',verified_stages=v.completed,assertions_before_failure=v.checks,elapsed_seconds=time.perf_counter()-started,traceback=traceback.format_exc(),all_original_inputs_unchanged=True));raise

if __name__=='__main__':main()
