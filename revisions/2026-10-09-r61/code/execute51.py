"""Known-design R51 reproduction; no claim of new blind preregistration."""
from pathlib import Path
import hashlib,json,os,platform,subprocess,sys,time
R=Path(__file__).resolve().parents[1]
def run(module,arg):subprocess.run([sys.executable,str(R/'code'/module),arg],check=True)
def amend(name,scope):
    p=R/'audit'/name;j=json.loads(p.read_text());j['scope']=scope
    j['source_commit']=os.environ.get('NBO_SCIENCE_SOURCE','unpublished-local-check')
    p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def main():
    if (R/'results').exists() and any((R/'results').rglob('record.json')):raise RuntimeError('Refusing to overwrite existing science')
    (R/'audit').mkdir(parents=True,exist_ok=True)
    import numpy,scipy
    record=dict(source_commit=os.environ.get('NBO_SCIENCE_SOURCE'),started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),python=sys.version,numpy=numpy.__version__,scipy=scipy.__version__,platform=platform.platform(),github_run=os.environ.get('GITHUB_RUN_ID'),known_design=True,old_outcomes_available=True,new_independent_sample_size_claimed=False,recovered_package_sha256='fa1fe9690a389a6289bba728d6814b8cc7ee68942a6fc67539c1e9d3de53f4b6')
    (R/'audit/REPRODUCTION51.json').write_text(json.dumps(record,indent=2)+'\n')
    run('study50.py','--freeze');amend('SOURCE_FREEZE.json','R51 known-design reproduction: sources frozen before this execution, recovered R50 outcomes already available')
    run('study50.py','--execute')
    run('common50.py','--freeze');amend('COMMON_FREEZE.json','R51 reproduction of the recovered R50 post-primary common-accuracy amendment; not a new prospective decision')
    run('common50.py','--execute')
    run('replay50.py','--freeze');run('replay50.py','--execute')
    record['completed_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
    (R/'audit/REPRODUCTION51.json').write_text(json.dumps(record,indent=2)+'\n')
if __name__=='__main__':main()
