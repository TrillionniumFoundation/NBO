"""Pure continuation/controller and gzip fixtures; zero original economics.

No original model, terminal optimizer, production service or rational economic
validator is executed. The mathematical reader receives separate source QA.
"""
from __future__ import annotations
import argparse,copy,gzip,hashlib,json,tempfile,time,traceback,zlib
from fractions import Fraction as Q
from pathlib import Path
import resume_independent122 as r
import validate_cached_witness122 as v


def run():
 checks=0
 def check(ok,message):
  nonlocal checks
  checks+=1
  if not ok:raise AssertionError(message)
 def rejected(call,exception=Exception):
  try:call()
  except exception:return True
  return False
 def key(i):return ((float(i/8).hex(),float(1/2).hex()),float(i/64).hex(),float(1/2).hex())
 def values(k):return {'x':tuple(Q(float.fromhex(z)) for z in k[0]),'a':Q(float.fromhex(k[1])),'alpha':Q(float.fromhex(k[2]))}
 def row(i,bins=64):
  k=key(i);z={'key_id':v.kid(k),'state_hex':list(k[0]),'action_hex':k[1],'alpha':float.fromhex(k[2]),'bins':bins,'seconds':0.25,'terminal_contexts':2*bins+1}
  z.update({f:'1/3' for f in v.FRACTION_FIELDS});return z
 class Trace:
  def __init__(self):self.records=[];self.flushes=0
  def write(self,z):self.records.append(dict(z))
  def flush(self):self.flushes+=1
 calls=[]
 def original(ir,k,vals,trace):calls.append(k);return row(round(float.fromhex(k[1])*64))
 saved=[row(0),row(1)];before=copy.deepcopy(saved);times=iter([10.,309.,310.,312.])
 controller=r.Controller(original,saved,'segment',clock=lambda:next(times));controller.bins=lambda:64;trace=Trace()
 for i in (0,1):
  out=controller.evaluate(None,key(i),values(key(i)),trace)
  check(all(isinstance(out[f],Q) for f in v.FRACTION_FIELDS),'cached exact Fraction conversion')
 check(not calls and not trace.records and controller.position==2,'historical reuse performs no original calls or trace copies')
 check(saved==before and controller.reused_seconds==Q(1,2),'native cache and original historical seconds preserved')
 controller.evaluate(None,key(2),values(key(2)),trace)
 check(controller.new_seconds==299 and len(calls)==1,'first complete call below budget returns')
 controller.evaluate(None,key(3),values(key(3)),trace)
 check(controller.new_seconds==301 and len(calls)==2,'crossing complete call returns before checkpoint')
 check(rejected(lambda:controller.evaluate(None,key(4),values(key(4)),trace),r.PlannedCheckpoint),'next uncached request planned checkpoint')
 check(len(calls)==2 and len(controller.fresh)==2 and len(controller.attempts)==2,'checkpoint performs no third call')
 wrong=r.Controller(original,saved,'segment',clock=lambda:0.);wrong.bins=lambda:64
 check(rejected(lambda:wrong.evaluate(None,key(1),values(key(1)),trace),ValueError),'wrong cached request rejected')
 def meshes():
  for i in (0,1):
   yield (v.kid(key(i)),64),[{'sequence':n+17,'key_id':v.kid(key(i)),'node':n,'opaque_rational':'17/19'} for n in range(129)]
 final=r.Controller(original,saved,'finalize',iter(meshes()),clock=lambda:0.);final.bins=lambda:64;full=Trace();startcalls=len(calls)
 for i in (0,1):final.evaluate(None,key(i),values(key(i)),full)
 check(len(calls)==startcalls and final.replayed_meshes==2 and final.replayed_contexts==258,'cache-only finalizer has zero new calls')
 check(len(full.records)==258 and full.flushes==2 and all('sequence' not in z and z['opaque_rational']=='17/19' for z in full.records),'finalizer strips only old sequence and preserves every witness')
 check(rejected(lambda:final.evaluate(None,key(2),values(key(2)),full),ValueError),'uncached finalizer request rejected')
 empty=r.Controller(original,[],'finalize',iter(()),clock=lambda:0.);empty.bins=lambda:64
 check(rejected(lambda:empty.evaluate(None,key(0),values(key(0)),trace),ValueError),'empty finalizer cannot compute economics')
 def failed(*args):raise ArithmeticError('synthetic original-call failure')
 ftimes=iter([2.,5.]);failed_controller=r.Controller(failed,[],'segment',clock=lambda:next(ftimes));failed_controller.bins=lambda:64
 check(rejected(lambda:failed_controller.evaluate(None,key(0),values(key(0)),trace),ArithmeticError),'unexpected original exception preserved')
 check(failed_controller.new_seconds==3 and not failed_controller.fresh and failed_controller.attempts[0]['status']=='raised_exception','failed new work retains actual duration and attempted-call metadata')
 with tempfile.TemporaryDirectory(prefix='nbo-r122-resume-pure-') as temp:
  p=Path(temp)/'part00000.jsonl.gz';raw=b''.join(json.dumps({'sequence':j,'node':j}).encode()+b'\n' for j in range(3));blob=gzip.compress(raw,mtime=0);p.write_bytes(blob)
  diag=[];result=list(v.stream_part(p,True,diag));check(len(result)==3 and diag[0]['gzip_footer_validated'] is True,'sealed gzip CRC and complete line census')
  p.write_bytes(blob[:-8]);diag=[];result=list(v.stream_part(p,False,diag));check(len(result)==3 and diag[0]['gzip_footer_validated'] is False,'unsealed complete prefix does not invent footer success')
  check(rejected(lambda:list(v.stream_part(p,True,[])),ValueError),'unsealed prefix rejected as a sealed part')
  corrupt=bytearray(blob);corrupt[-8]^=1;p.write_bytes(corrupt)
  check(rejected(lambda:list(v.stream_part(p,True,[])),zlib.error),'invalid sealed CRC rejected')
  p.write_bytes(gzip.compress(b'{"sequence":1,"node":0}\n',mtime=0))
  check(rejected(lambda:list(v.stream_part(p,True,[])),ValueError),'per-part sequence tamper rejected')
 # Synthetic cache ancestry verifies each native source exactly once and rejects conflicting manifests.
 with tempfile.TemporaryDirectory(prefix='nbo-r122-cache-hashes-pure-') as temp:
  root=Path(temp);(root/'verification122').mkdir();(root/'verification122/validate_cached_witness122.py').write_bytes(Path(v.__file__).read_bytes())
  for name in ('native1','native2'):
   (root/name).mkdir();(root/name/'saved.txt').write_text(name)
  source1={'directory':'native1','files':r.fingerprint(root/'native1')}
  source2={'directory':'native2','files':r.fingerprint(root/'native2')}
  base={'resume_commit':'a'*40,'source_commit':r.F,'state_commit':r.D,'repair_commit':r.I,'primary_sha256':'fixture',
        'entries':[{'key_id':'one','bins':64}],'evaluation_count':1,'sources':[source1],'previous_cache':None}
  def put(name,index):
   d=root/name;d.mkdir();r.write(d/'CACHE_INDEX122.json',index);r.write(d/'CACHE_VALIDATION122.json',
    {'status':'validated','index_sha256':r.sha(d/'CACHE_INDEX122.json'),'validator_sha256':r.sha(Path(v.__file__))});return d
  first=put('cache1',base);second_index=dict(base,entries=base['entries']+[{'key_id':'two','bins':64}],evaluation_count=2,
   sources=[source1,source2],previous_cache={'path':'cache1','receipt_sha256':r.sha(first/'CACHE_VALIDATION122.json'),'index_sha256':r.sha(first/'CACHE_INDEX122.json')})
  second=put('cache2',second_index);oldroot=r.ROOT;oldverify=r.verify_files;verified=[]
  def observed(directory,files):verified.append(str(directory));return oldverify(directory,files)
  try:
   r.ROOT=root;r.verify_files=observed;r.load_cache(second,'a'*40,'fixture')
   check(len(verified)==2 and len(set(verified))==2,'shared source manifests hashed only once across ancestry')
   conflict=dict(second_index,sources=[source1,{'directory':'native1','files':source2['files']}]);bad=put('cache-conflict',conflict)
   check(rejected(lambda:r.load_cache(bad,'a'*40,'fixture'),ValueError),'conflicting manifests for same source directory rejected')
  finally:r.ROOT=oldroot;r.verify_files=oldverify
 return {'status':'passed','assertions':checks,'synthetic_cache_rows':2,'synthetic_replayed_contexts':258,
  'synthetic_complete_new_calls':2,'synthetic_failed_new_call':1,'original_economic_calls':0,
  'original_scientific_modules_imported':False,'source_hashes':{str(p.relative_to(r.ROOT)):r.sha(p) for p in (Path(r.__file__),Path(v.__file__),Path(__file__))}}


def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);tick=time.perf_counter()
 try:
  result=run();result['seconds']=time.perf_counter()-tick;r.write(a.output/'RESULT122.json',result);print(json.dumps(result,sort_keys=True),flush=True)
 except BaseException:
  r.write(a.output/'FAILURE122.json',{'status':'failed','seconds':time.perf_counter()-tick,'traceback':traceback.format_exc()});raise

if __name__=='__main__':main()
