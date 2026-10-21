"""Published administrative continuation around unchanged F122/I122 sources.

Modes: cache validates a new complete native suffix; segment performs at most
300 measured seconds of new primitive calls before a boundary checkpoint;
finalize replays a complete validated cache through the unchanged driver.
Every native stage remains untouched. No state, actor or scientific rule is
chosen by this module.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, math, subprocess, sys, time, traceback
from fractions import Fraction as Q
from pathlib import Path
import validate_cached_witness122 as vw

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
F='2f483615c8bc0037e43ec01a16cce05c724f8c60'
D='a3323b6f557315ea91b536637419ef6fd7984b61'
I='1f19410305c707716135defd91d6644d70657d84'
PRIMARY_SHA='94fc7537e5020e464118c64076c8f6ace5ff3dd6d77b1e15d35dc3f2712e5044'
FORENSIC_SHA='58a899a4516a5df99ad712d5cb0fe94b699042424b055070acc19fe7d68e7ddd'
LIMIT=300.0
OWN_FILES=('verification122/resume_independent122.py','verification122/validate_cached_witness122.py',
 'verification122/test_resume_independent122.py','provenance122/RESUME_INDEPENDENT_PROTOCOL122.md')
EQUAL_OUTPUTS=('POLICY_EVALUATIONS122.jsonl','BEST_POLICY_BOUNDS122.jsonl','CLAIM_CHECKS122.jsonl',
 'COMPARISONS122.jsonl','ALGEBRA_AUDIT122.json','INPUTS122.json')


def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()

def write(path,obj):
 with Path(path).open('x') as f:json.dump(vw.enc(obj),f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')

def read(path):return json.loads(Path(path).read_text())
def rows(path):
 with Path(path).open() as f:return [json.loads(line) for line in f]

def relative(path):
 p=Path(path).resolve()
 if not p.is_relative_to(ROOT):raise ValueError('Administrative evidence must stay inside R122')
 return str(p.relative_to(ROOT))

def source_gate(commit):
 if len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):raise ValueError('Full actual continuation publication commit required')
 for name in OWN_FILES:
  p=ROOT/name
  if subprocess.check_output(['git','show',commit+':'+str(p.relative_to(REPO))],cwd=REPO)!=p.read_bytes():
   raise ValueError('Continuation source differs from published commit: '+name)
 return {name:sha(ROOT/name) for name in OWN_FILES}

def fingerprint(directory):
 p=Path(directory).resolve();out=[]
 for f in sorted(p.rglob('*')):
  if f.is_symlink():raise ValueError('Native source stage may not contain symlinks')
  if f.is_file():out.append({'path':str(f.relative_to(p)),'bytes':f.stat().st_size,'sha256':sha(f)})
 return out

def verify_files(directory,files):
 for row in files:
  p=(Path(directory)/row['path']).resolve()
  if not p.is_relative_to(Path(directory).resolve()) or p.stat().st_size!=row['bytes'] or sha(p)!=row['sha256']:
   raise ValueError('Bound native file changed: '+str(p))

def load_cache(directory,commit,primary_hash,seen=None):
 """Hash/read the completed validation chain; never rerun old mathematical work."""
 p=Path(directory).resolve();receipt=read(p/'CACHE_VALIDATION122.json');index=read(p/'CACHE_INDEX122.json')
 if receipt['status']!='validated' or receipt['index_sha256']!=sha(p/'CACHE_INDEX122.json'):
  raise ValueError('Cache index does not match its completed validation receipt')
 if index['resume_commit']!=commit or index['source_commit']!=F or index['state_commit']!=D or index['repair_commit']!=I or index['primary_sha256']!=primary_hash:
  raise ValueError('Cache scientific/source identity differs')
 if receipt['validator_sha256']!=sha(ROOT/'verification122/validate_cached_witness122.py'):
  raise ValueError('Cached validation used another mathematical reader')
 seen=set() if seen is None else seen
 if str(p) in seen:raise ValueError('Cache ancestry cycle')
 seen.add(str(p))
 previous=index.get('previous_cache')
 if previous:
  old=ROOT/previous['path']
  if sha(old/'CACHE_VALIDATION122.json')!=previous['receipt_sha256'] or sha(old/'CACHE_INDEX122.json')!=previous['index_sha256']:
   raise ValueError('Previous cache validation identity differs')
  prior=load_cache(old,commit,primary_hash,seen)
  if index['entries'][:len(prior['entries'])]!=prior['entries'] or index['sources'][:len(prior['sources'])]!=prior['sources']:
   raise ValueError('Previously validated cache prefix was modified')
 for source in index['sources']:verify_files(ROOT/source['directory'],source['files'])
 if index['evaluation_count']!=len(index['entries']) or len({(r['key_id'],r['bins']) for r in index['entries']})!=len(index['entries']):
  raise ValueError('Cache unique evaluation census differs')
 return index

def primary_actions(data):
 actions={}
 for row in data:
  for field in ('action','baseline_action','raw_proposal_kept'):
   a=row[field]
   if a is None:continue
   k=(tuple(row['state_hex']),float(a).hex(),float(row['alpha']).hex())
   actions[k]={'state':row['state'],'action':a,'alpha':row['alpha']}
 return actions

def check_result_identity(row,actions):
 k=vw.key_of_result(row)
 if k not in actions or row['key_id']!=vw.kid(k):raise ValueError('Cached result is not an original declared policy')
 z=actions[k]
 if row['state']!=z['state'] or row['action']!=z['action'] or row['alpha']!=z['alpha']:
  raise ValueError('Cached result changed state/action/risk bits')
 if row['bins'] not in (64,128,256,512):raise ValueError('Cached result changed fixed mesh ladder')


def cache_mode(a,source_hashes,common):
 out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);tick=time.perf_counter()
 write(out/'START_CACHE_VALIDATION122.json',{'argv':sys.argv,'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
  'resume_commit':a.resume_commit,'source_hashes':source_hashes,'source_commit':F,'repair_commit':I})
 try:
  common.verify_source(F);data,binding=common.validated_primary(a.primary,F)
  if binding['state_commit']!=D or sha(a.primary/'records122.jsonl')!=PRIMARY_SHA:raise ValueError('Fixed primary/D identity differs')
  actions=primary_actions(data);prior=load_cache(a.cache,a.resume_commit,PRIMARY_SHA) if a.cache else None
  old=[] if prior is None else prior['entries'];sources=[] if prior is None else list(prior['sources'])
  segment=a.segment.resolve();native=rows(segment/'POLICY_EVALUATIONS122.jsonl')
  if native[:len(old)]!=old or len(native)<len(old):raise ValueError('Native resumed evaluation prefix differs from prior cache')
  if len({(r['key_id'],r['bins']) for r in native})!=len(native):raise ValueError('Duplicate native evaluation')
  for row in native:check_result_identity(row,actions)
  if prior is None:
   if relative(segment)!='results122/independent-attempt02' or sha(segment/'INTERRUPTION_FORENSIC122.json')!=FORENSIC_SHA:
    raise ValueError('First cache must bind the declared interrupted native attempt')
   forensic=read(segment/'INTERRUPTION_FORENSIC122.json')
   if forensic['completed_policy_rows']!=716 or len(native)!=716 or forensic['actual_parent_exit_code'] is not None or forensic['actual_parent_wall_seconds'] is not None:
    raise ValueError('Interrupted attempt census/status differs')
   for r in forensic['native_files']:
    p=ROOT/r['path']
    if p.stat().st_size!=r['bytes'] or sha(p)!=r['sha256']:raise ValueError('Interrupted native forensic byte identity differs')
   ordered=sorted(actions)
   if len(ordered)!=865 or [(vw.key_of_result(r),r['bins']) for r in native]!=[(k,64) for k in ordered[:716]]:
    raise ValueError('Initial cache is not the exact declared ordered base prefix')
   allow_unsealed=True;completed_reference=None
  else:
   meta=read(segment/'RESUME_SEGMENT122.json')
   if meta['resume_commit']!=a.resume_commit or meta['cache_index_sha256']!=sha(a.cache/'CACHE_INDEX122.json') or meta['primary_sha256']!=PRIMARY_SHA:
    raise ValueError('New native segment does not bind this validated prefix')
   if meta['status'] not in ('planned_checkpoint','segment_complete_not_canonical') or meta['mode']!='segment':raise ValueError('Only declared segment outcomes can extend the cache')
   if meta['fresh_policy_calls']!=len(native)-len(old) or meta['reused_policy_calls']!=len(old):raise ValueError('Segment fresh/reuse census differs')
   if meta['status']=='planned_checkpoint':
    failure=read(segment/'FAILURE122.json')
    if 'PlannedCheckpoint' not in failure['traceback'] or (segment/'EXECUTION122.json').exists():raise ValueError('Planned checkpoint raw failure trace differs')
   else:
    if read(segment/'EXECUTION122.json')['status']!='executed' or read(segment/'INDEPENDENT_SCHEMA_ADAPTER122.json')['status']!='executed':raise ValueError('Naturally completed segment lacks successful native receipts')
   allow_unsealed=False;completed_reference=relative(segment) if meta['status']=='segment_complete_not_canonical' else None
  inputs=read(segment/'INPUTS122.json')
  if inputs['primary_sha256']!=PRIMARY_SHA or inputs['primary_state_binding']!=binding:raise ValueError('Native input binding differs')
  new=native[len(old):];counts={};diagnostics=[];stream=vw.witness_rows(segment,allow_unsealed,diagnostics)
  for j,row in enumerate(new):
   mesh=[]
   for node in range(2*row['bins']+1):
    try:z=next(stream)
    except StopIteration:raise ValueError('Recorded policy lacks a complete raw witness mesh')
    if z['key_id']!=row['key_id'] or z['node']!=node:raise ValueError('Raw witness request order differs')
    mesh.append(z)
   vw.validate_policy(row,mesh,counts)
   if (j+1)%16==0 or j+1==len(new):print('CACHE_VALIDATION',j+1,len(new),round(time.perf_counter()-tick,3),flush=True)
  trailing=sum(1 for _ in stream)
  if trailing and not allow_unsealed:raise ValueError('Planned segment has unexplained trailing witness records')
  if not allow_unsealed:
   manifest=read(segment/'WITNESS_MANIFEST122.json')
   if manifest['records']!=sum(2*r['bins']+1 for r in new):raise ValueError('Fresh-only native witness census differs')
  source={'directory':relative(segment),'first_index':len(old),'last_index_exclusive':len(native),
   'complete_fresh_evaluations':len(new),'allow_unsealed_prefix':allow_unsealed,'trailing_witness_records_not_reused':trailing,
   'witness_diagnostics':diagnostics,'files':fingerprint(segment)}
  sources.append(source)
  index={'resume_commit':a.resume_commit,'source_commit':F,'state_commit':D,'repair_commit':I,'primary_sha256':PRIMARY_SHA,
   'entries':native,'evaluation_count':len(native),'sources':sources,'completed_reference':completed_reference,
   'previous_cache':None if prior is None else {'path':relative(a.cache),'receipt_sha256':sha(a.cache/'CACHE_VALIDATION122.json'),'index_sha256':sha(a.cache/'CACHE_INDEX122.json')},
   'new_population_states':0,'new_primary_decisions':0,'historical_evaluation_seconds':str(sum((Q.from_float(float(r['seconds'])) for r in native),Q(0)))}
  write(out/'CACHE_INDEX122.json',index)
  write(out/'CACHE_VALIDATION122.json',{'status':'validated','resume_commit':a.resume_commit,'index_sha256':sha(out/'CACHE_INDEX122.json'),
   'validator_sha256':sha(ROOT/'verification122/validate_cached_witness122.py'),'source_hashes':source_hashes,
   'previous_policies_reused_without_revalidating_math':len(old),'new_policies_mathematically_validated':len(new),
   'exact_checks_this_extension':counts,'original_policy_optimization_calls':0,'terminal_bisection_optimization_steps_performed':0,
   'seconds':time.perf_counter()-tick,'elapsed_nested_in_outer_launcher':True,'trailing_witness_records_retained_not_reused':trailing})
 except BaseException:
  write(out/'FAILURE_CACHE_VALIDATION122.json',{'status':'failed','seconds':time.perf_counter()-tick,'traceback':traceback.format_exc(),'all_partial_outputs_retained':True});raise
 print(json.dumps({'status':'validated','output':str(out),'evaluations':len(native),'new_mathematically_validated':len(new)},sort_keys=True),flush=True)


class PlannedCheckpoint(RuntimeError):pass

class Controller:
 """Pure prefix/control logic; injectable original/clock supports non-economic QA."""
 def __init__(self,original,entries,mode,mesh_stream=None,clock=time.perf_counter,limit=LIMIT):
  self.original=original;self.entries=entries;self.mode=mode;self.mesh_stream=mesh_stream;self.clock=clock;self.limit=limit
  self.position=0;self.new_seconds=0.0;self.fresh=[];self.attempts=[];self.reused_seconds=Q(0);self.replayed_meshes=0;self.replayed_contexts=0
 def evaluate(self,ir,k,values,trace):
  pair=(vw.kid(k),self.bins())
  if self.position<len(self.entries):
   saved=self.entries[self.position]
   if pair!=(saved['key_id'],saved['bins']) or k!=vw.key_of_result(saved):raise ValueError('Frozen request differs from next exact cached prefix entry')
   if tuple(float(v).hex() for v in values['x'])!=k[0] or float(values['a']).hex()!=k[1] or float(values['alpha']).hex()!=k[2]:raise ValueError('Frozen request values differ from its policy key')
   if self.mode=='finalize':
    expected,mesh=next(self.mesh_stream)
    if expected!=(saved['key_id'],saved['bins']) or len(mesh)!=2*saved['bins']+1:raise ValueError('Canonical replay mesh identity differs')
    for row in mesh:
     z=dict(row);del z['sequence'];trace.write(z)
    trace.flush();self.replayed_meshes+=1;self.replayed_contexts+=len(mesh)
   self.position+=1;self.reused_seconds+=Q.from_float(float(saved['seconds']))
   return vw.decoded_result(saved)
  if self.mode=='finalize':raise ValueError('Cache-only finalizer received an uncached original-economic request')
  if self.new_seconds>=self.limit:raise PlannedCheckpoint('Prespecified300s new-primitive budget reached before next uncached request')
  started=self.clock();attempt={'key_id':pair[0],'bins':pair[1],'status':'started'};self.attempts.append(attempt)
  try:
   result=self.original(ir,k,values,trace);attempt['status']='returned_complete_result'
  except BaseException:
   attempt['status']='raised_exception';attempt['traceback']=traceback.format_exc();raise
  finally:
   elapsed=self.clock()-started
   if elapsed<0 or not math.isfinite(elapsed):raise ArithmeticError('Invalid measured primitive duration')
   self.new_seconds+=elapsed;attempt['actual_new_call_seconds']=elapsed
  self.fresh.append({'key_id':result['key_id'],'bins':result['bins'],'actual_new_call_seconds':elapsed,'terminal_contexts':result['terminal_contexts']})
  return result


def meshes_for_cache(index):
 for source in index['sources']:
  diagnostics=[];stream=vw.witness_rows(ROOT/source['directory'],source['allow_unsealed_prefix'],diagnostics)
  for row in index['entries'][source['first_index']:source['last_index_exclusive']]:
   mesh=[]
   for node in range(2*row['bins']+1):
    z=next(stream)
    if z['key_id']!=row['key_id'] or z['node']!=node:raise ValueError('Previously validated witness order changed')
    mesh.append(z)
   yield (row['key_id'],row['bins']),mesh
  trailing=sum(1 for _ in stream)
  if trailing!=source['trailing_witness_records_not_reused']:raise ValueError('Preserved trailing witness census changed')


def run_mode(a,source_hashes,common):
 if a.output.exists():raise ValueError('Continuation output must be a new exclusive directory')
 primary_hash=sha(a.primary/'records122.jsonl')
 if primary_hash!=PRIMARY_SHA:raise ValueError('Fixed primary bytes differ')
 common.verify_source(F);index=load_cache(a.cache,a.resume_commit,primary_hash)
 if a.mode=='finalize' and not index['completed_reference']:raise ValueError('Finalizer requires a naturally completed last segment')
 sys.path.insert(0,str(ROOT.parent/'2026-10-20-r121/code121'));import exact121 as ex
 import independent_schema_adapter122 as adapter
 original=ex.evaluate_action;controller=Controller(original,index['entries'],a.mode,meshes_for_cache(index) if a.mode=='finalize' else None)
 controller.bins=lambda:ex.BINS
 ex.evaluate_action=controller.evaluate
 original_argv=list(sys.argv);nested=[str(ROOT/'verification122/independent_schema_adapter122.py'),'--repair-commit',I,
  '--source-commit',F,'--primary',str(a.primary),'--output',str(a.output)]
 started=time.perf_counter();status='unexpected_failure';code=1;error=None;equal={}
 try:
  sys.argv=nested;adapter.main()
  if controller.position!=len(index['entries']):raise ValueError('Frozen driver did not consume the full validated prefix')
  if a.mode=='finalize':
   if controller.fresh or controller.replayed_meshes!=len(index['entries']):raise ValueError('Finalizer performed new work or omitted cached meshes')
   try:next(controller.mesh_stream)
   except StopIteration:pass
   else:raise ValueError('Finalizer has unused validated witness meshes')
   reference=ROOT/index['completed_reference']
   for name in EQUAL_OUTPUTS:
    if (a.output/name).read_bytes()!=(reference/name).read_bytes():raise ValueError('Finalizer changed native complete output: '+name)
    equal[name]={'sha256':sha(a.output/name),'reference_sha256':sha(reference/name),'exact_bytes_equal':True}
   status='canonical_complete'
  else:status='segment_complete_not_canonical'
  code=0
 except PlannedCheckpoint:
  status='planned_checkpoint';code=75;error=traceback.format_exc()
 except BaseException:
  error=traceback.format_exc();raise
 finally:
  ex.evaluate_action=original;sys.argv=original_argv
  if a.output.is_dir():
   receipt={'status':status,'mode':a.mode,'exit_code':code,'resume_commit':a.resume_commit,'source_commit':F,'state_commit':D,
    'repair_commit':I,'primary_sha256':primary_hash,'source_hashes':source_hashes,'cache_directory':relative(a.cache),
    'cache_index_sha256':sha(a.cache/'CACHE_INDEX122.json'),'cache_validation_sha256':sha(a.cache/'CACHE_VALIDATION122.json'),
    'actual_command':original_argv,'nested_unchanged_I_command':nested,'source_F_I_files_changed':False,
    'reused_policy_calls':controller.position,'fresh_policy_calls':len(controller.fresh),'fresh_calls':controller.fresh,
    'fresh_primitive_call_attempts':controller.attempts,'fresh_primitive_call_attempt_count':len(controller.attempts),
    'fresh_terminal_contexts':sum(z['terminal_contexts'] for z in controller.fresh),'fresh_primitive_seconds':controller.new_seconds,
    'reused_historical_evaluation_seconds':str(controller.reused_seconds),'historical_seconds_not_charged_as_current_execution':True,
    'checkpoint_new_primitive_seconds_threshold':LIMIT,'checkpoint_checked_before_next_uncached_request_only':True,
    'current_exact121_counts_scope':'actual fresh primitives and ordinary module source checks only; no replay inflation',
    'delivered_unique_evaluation_count':controller.position+len(controller.fresh),
    'frozen_actual_independent_evaluations_field_scope':'aggregate unique original evaluations represented across validated retained and new native evidence; not current-process new calls',
    'replayed_witness_meshes':controller.replayed_meshes,'replayed_witness_contexts':controller.replayed_contexts,
    'fresh_only_noncanonical_trace':a.mode=='segment','canonical_finalizer_new_economic_calls':len(controller.fresh) if a.mode=='finalize' else None,
    'final_reference':index['completed_reference'] if a.mode=='finalize' else None,'canonical_exact_equalities':equal,
    'planned_checkpoint_not_scientific_success_or_unexpected_failure':status=='planned_checkpoint',
    'raw_F_I_receipts_unchanged_and_retained':True,'error_or_checkpoint_traceback':error,
    'seconds':time.perf_counter()-started,'elapsed_nested_in_outer_launcher_not_additive':True,
    'new_population_states':0,'new_primary_decisions':0,'new_timing_replicates':0}
   write(a.output/'RESUME_SEGMENT122.json',receipt)
 print(json.dumps({'status':status,'output':str(a.output),'reused':controller.position,'fresh':len(controller.fresh),'fresh_seconds':controller.new_seconds},sort_keys=True),flush=True)
 if code:raise SystemExit(code)


def main():
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=('cache','segment','finalize'),required=True)
 p.add_argument('--resume-commit',required=True);p.add_argument('--repair-commit',required=True);p.add_argument('--source-commit',required=True)
 p.add_argument('--primary',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
 p.add_argument('--cache',type=Path);p.add_argument('--segment',type=Path);a=p.parse_args()
 a.primary=a.primary.resolve();a.output=a.output.resolve()
 if a.cache:a.cache=a.cache.resolve()
 if a.segment:a.segment=a.segment.resolve()
 relative(a.primary);relative(a.output)
 if a.cache:relative(a.cache)
 if a.segment:relative(a.segment)
 if a.source_commit!=F or a.repair_commit!=I:raise ValueError('Continuation must retain exact F/I identities')
 if (a.mode=='cache')!=(a.segment is not None) or (a.mode!='cache' and a.cache is None):raise ValueError('Cache construction requires --segment; execution/finalize requires --cache')
 hashes=source_gate(a.resume_commit)
 sys.path.insert(0,str(ROOT/'code122'));import common122 as common
 if a.mode=='cache':cache_mode(a,hashes,common)
 else:run_mode(a,hashes,common)

if __name__=='__main__':main()
