"""Execute the unchanged R114 population protocol under R115 author custody.

The original R110 acquisition, actors, cost certificates and safeguards are
imported without modification. This driver adds barriers and records only.
"""
from __future__ import annotations
from pathlib import Path
import argparse, base64, hashlib, json, os, resource, struct, subprocess, sys, time, traceback
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'code110'))
import gain_budget110 as control
base, rep, kern = control.base, control.rep, control.kern
SERVICES = ('compiled', 'compiled-safe', 'gain-16')
PROTOCOL_BLOB = '1b4f4451fdca812d4ad5024050c83704fdc4b33b'

def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def sha(s):
    if len(s) != 40 or any(c not in '0123456789abcdef' for c in s):
        raise ValueError('An actual remote commit SHA is required')
    return s

def source():
    m = json.loads((ROOT/'SOURCE_FREEZE115.json').read_text())
    for name, h in m['files'].items():
        if digest(ROOT/name) != h:
            raise ValueError('Frozen source mismatch: '+name)
    return {'execution_source_commit': sha(os.environ['NBO115_SOURCE_COMMIT']),
            'protocol_git_blob': PROTOCOL_BLOB,
            'source_manifest_sha256': digest(ROOT/'SOURCE_FREEZE115.json'),
            'inherited_control_source': control.source(),
            'experiment': 'R114 protocol executed in isolated R115 author branch'}

def acquire(out):
    if out.exists():
        raise FileExistsError('Acquisition output must be new; preserve previous runs')
    src = source(); out.mkdir(parents=True)
    base.dump(out/'START115.json', {'source':src, 'unix':time.time(), 'machine':base.machine()})
    started = time.perf_counter()
    try:
        base.acquire(out)
        entries = {}
        for p in sorted(out.rglob('*')):
            if p.is_file():
                entries[str(p.relative_to(out))] = digest(p)
        base.dump(out/'ACTORS115.json', {'source':src, 'files':entries,
                  'seconds':time.perf_counter()-started, 'fitted_before_test_bytes':True,
                  'sample_seen':False, 'population': 'independent uniform 20-bit dyadic unit square'})
    except BaseException:
        base.dump(out/'FAILED_ACQUISITION115.json', {'exception':traceback.format_exc()})
        raise

def sample(out, actor_commit):
    source(); sha(actor_commit)
    if (out/'sample-bytes.bin').exists():
        raise FileExistsError('Do not replace an independently drawn sample')
    info = json.loads((out/'ACTORS115.json').read_text())
    for name, h in info['files'].items():
        if digest(out/name) != h: raise ValueError('Actor/acquisition custody changed')
    raw = os.urandom(8192)
    states = [[(v % 2**20)/2**20 for v in pair]
              for pair in np.array(struct.unpack('<2048I', raw), dtype=np.uint64).reshape(1024,2).tolist()]
    (out/'sample-bytes.bin').write_bytes(raw)
    base.dump(out/'states.json', states)
    base.dump(out/'SAMPLE115.json', {'actor_commit':actor_commit,
      'actor_manifest_sha256':digest(out/'ACTORS115.json'), 'bytes_sha256':digest(out/'sample-bytes.bin'),
      'states_sha256':digest(out/'states.json'), 'bytes_b64':base64.b64encode(raw).decode(),
      'bytes':8192, 'states':1024, 'state_law':'iid uniform dyadic 20-bit coordinates',
      'unix':time.time(), 'source':source(), 'evaluation_started':False})

def inputs(out):
    src = source(); act = json.loads((out/'ACTORS115.json').read_text())
    smp = json.loads((out/'SAMPLE115.json').read_text())
    for name,h in act['files'].items():
        if digest(out/name)!=h: raise ValueError('Frozen actor changed: '+name)
    if digest(out/'ACTORS115.json') != smp['actor_manifest_sha256']: raise ValueError('Actor manifest mismatch')
    if digest(out/'sample-bytes.bin') != smp['bytes_sha256']: raise ValueError('Random bytes mismatch')
    if digest(out/'states.json') != smp['states_sha256']: raise ValueError('States mismatch')
    x = np.array(json.loads((out/'states.json').read_text()), dtype=float)
    if x.shape != (1024,2): raise ValueError('Wrong population sample size')
    return x, src

def execute(out, repeat=None):
    x, src = inputs(out)
    sample_commit = sha(os.environ['NBO115_SAMPLE_COMMIT'])
    if repeat is not None: x=x[:32]
    folder = out/'primary' if repeat is None else out/'timing'/str(repeat)
    if folder.exists(): raise FileExistsError('Never overwrite a primary or timing execution')
    folder.mkdir(parents=True); start=time.perf_counter(); records=[]
    base.dump(folder/'START.json', {'source':src,'sample_commit':sample_commit,'unix':time.time(),
                                  'machine':base.machine(),'states':len(x)})
    try:
        for i, alpha in enumerate(base.LEVELS):
            models=base.load_models(out,i)
            for arm in rep.ARMS:
                for name in SERVICES:
                    d=control.service(x,alpha,models[arm],name)
                    d.update(risk_index=i,alpha=alpha,arm=arm,service=name,
                             model_sha256=digest(out/'models'/f'{i}-{arm}'/'model.json'))
                    p=folder/f'{i}-{arm}-{name}.json';base.dump(p,d)
                    records.append({'path':str(p.relative_to(out)),'sha256':digest(p),'risk_index':i,
                                    'alpha':alpha,'arm':arm,'service':name,'decisions':len(x),
                                    'seconds':d['seconds'],'counts':d['counts']})
                    base.dump(folder/'PROGRESS.json', {'status':'running','records':records})
                    print(i,arm,name,len(x),round(d['seconds'],3),flush=True)
        base.dump(folder/'MANIFEST.json', {'source':src,'sample_commit':sample_commit,'records':records,
                   'seconds':time.perf_counter()-start,'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   'status':'executed','timing_repetition':repeat,'machine':base.machine()})
    except BaseException:
        base.dump(folder/'FAILED.json', {'source':src,'exception':traceback.format_exc(),
                                        'seconds':time.perf_counter()-start,'records':records})
        raise

def timing(out):
    source(); records=[]
    if (out/'TIMING115.json').exists(): raise FileExistsError('Do not replace timing evidence')
    for repeat in range(7):
        cmd=[sys.executable,__file__,'timing-one','--output',str(out),'--repeat',str(repeat)]
        t=time.perf_counter();run=subprocess.run(cmd,capture_output=True,text=True)
        p=out/'timing'/f'PROCESS-{repeat}.log';p.parent.mkdir(exist_ok=True);p.write_text(run.stdout+run.stderr)
        records.append({'repeat':repeat,'command':cmd,'exit_code':run.returncode,
                        'process_seconds':time.perf_counter()-t,'log_sha256':digest(p)})
        base.dump(out/'TIMING_PROGRESS115.json', {'records':records})
        if run.returncode: raise RuntimeError('Timing failure retained')
        print('TIMING',repeat,'complete',flush=True)
    base.dump(out/'TIMING115.json', {'records':records,'source':source(),'status':'executed'})

def reference(out):
    x, src=inputs(out); x=x[:32]; records=[]
    if (out/'REFERENCE115.json').exists(): raise FileExistsError('Reference already executed')
    for i,alpha in enumerate(base.LEVELS):
        before=control.COUNTS.copy(); t=time.perf_counter()
        with kern.backend(True):
            a=control.cont.actor(x,alpha,None); r=control.quad.certificate(x,a,alpha,4096)
        records.append({'risk_index':i,'alpha':alpha,'states':x.tolist(),'actions':a.tolist(),
          **{k:r[k].tolist() for k in base.KEYS},'seconds':time.perf_counter()-t,
          'counts':base.counter_delta(before),'not_exact_optimum':True})
    base.dump(out/'REFERENCE115.json', {'source':src,'records':records,'charged_benchmark_work':True})

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('acquire','sample','primary','timing','timing-one','reference'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--actor-commit',default='');p.add_argument('--repeat',type=int)
    a=p.parse_args();out=a.output.resolve()
    if a.mode=='sample': return sample(out,a.actor_commit)
    if a.mode=='primary': return execute(out)
    if a.mode=='timing-one': return execute(out,a.repeat)
    return globals()[a.mode](out)

if __name__=='__main__':main()
