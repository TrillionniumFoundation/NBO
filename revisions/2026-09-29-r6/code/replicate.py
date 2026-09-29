"""Execute all declared R6 runs and save the raw evidence, including failures.

Numerical accuracy misses do not abort the suite; exceptions and violated
regression/provenance assertions do. No acceptance flag is rewritten.
"""
from __future__ import annotations
import datetime,hashlib,importlib.util,json,os,platform,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'revisions/2026-09-29-r6';C=P/'code';R=P/'results';L=P/'logs'
R.mkdir(exist_ok=True,parents=True);L.mkdir(exist_ok=True,parents=True)
def run(args,log):
    print('RUN',*args,flush=True);start=time.perf_counter()
    with (L/log).open('w') as out:
        result=subprocess.run(args,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT)
    if result.returncode:
        print((L/log).read_text()[-12000:],flush=True);raise RuntimeError(f'{log}: process exit {result.returncode}')
    return time.perf_counter()-start

def main():
    source=os.environ.get('NBO_SOURCE_COMMIT')
    if source is None:
        try:source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        except Exception:source='local-source-hashes'
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();times={}
    times['legacy']=run([sys.executable,'revisions/2026-09-28/code/experiments.py'],'legacy_reproduction.log')
    run([sys.executable,'revisions/2026-09-28/code/test_revision.py'],'legacy_tests.log')
    shutil.copytree(ROOT/'revisions/2026-09-28/results',R/'legacy_reproduction',dirs_exist_ok=True)
    for suite in ['smoke','primary','sensitivity']:
        times['consumption_'+suite]=run([sys.executable,str(C/'stopped_consumption.py'),'--suite',suite],'consumption_'+suite+'.log')
    paths=sorted(str(f) for f in R.glob('consumption_*_s*_w16_d2_r8_c60_a40.json') if '_joint_' not in f.name)
    if len(paths)!=6:raise ValueError('expected exactly six primary models')
    times['interval']=run([sys.executable,str(C/'interval_certificate.py'),*paths],'interval_primary.log')
    # Replay the unweighted classification pilot in a separate, permanent folder.
    spec=importlib.util.spec_from_file_location('pilot',C/'pilot_ndu_classification.py');pilot=importlib.util.module_from_spec(spec);spec.loader.exec_module(pilot)
    pilot.OUT=R/'pilot_ndu_classification';pilot.OUT.mkdir(exist_ok=True)
    records=[]
    for method in ['nbo','direct']:
        records.append(pilot.train(pilot.NDU(13,17,10),11,method,critic_steps=100,actor_steps=60))
    (pilot.OUT/'ndu_smoke.json').write_text(json.dumps(records,indent=2));shutil.copy2(C/'pilot_ndu_classification.py',pilot.OUT/'ndu_classification_source.py')
    for suite in ['smoke','primary','sensitivity']:
        times['ndu_'+suite]=run([sys.executable,str(C/'ndu_neural.py'),'--suite',suite],'ndu_'+suite+'.log')
    for suite in ['smoke','primary','trace','coverage']:
        times['coupled_'+suite]=run([sys.executable,str(C/'coupled_diffusion.py'),'--suite',suite],'coupled_'+suite+'.log')
    times['cournot']=run([sys.executable,str(C/'dynamic_cournot.py')],'cournot_primary.log')
    run([sys.executable,str(C/'test_r6.py')],'test_r6.log')
    run([sys.executable,str(C/'build_tables.py')],'tables_build.log')
    run([sys.executable,str(C/'assemble_revision.py')],'assembly.log')
    freeze=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True)
    (P/'environment.lock').write_text(freeze)
    info=dict(computational_source_commit=source,started_utc=start,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=platform.python_version(),platform=platform.platform(),machine=platform.machine(),cpu_count=os.cpu_count(),torch_threads=1,wall_seconds_by_suite=times,legacy_tests=8,r6_tests=12,regression_tests_passed=True,accuracy_failures_preserved=True,workflow_run=os.environ.get('GITHUB_RUN_ID'))
    (P/('REMOTE_EXECUTION.json' if os.environ.get('GITHUB_ACTIONS') else 'REPLICATION_EXECUTION.json')).write_text(json.dumps(info,indent=2))
    manifest={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.rglob('*')) if f.is_file() and '__pycache__' not in str(f) and f.name!='MANIFEST.json' and 'bootstrap' not in f.parts}
    (P/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(info),flush=True)
if __name__=='__main__':main()
