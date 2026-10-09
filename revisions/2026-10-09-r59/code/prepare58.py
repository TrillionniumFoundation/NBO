"""Create the new ordinary revision without changing any preceding directory."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-09-r57'
BASE='44f18a784f35f48565cb3060635c076f0b5bb2ed'

def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    marker=R/'audit/ASSEMBLY58.json'
    if marker.exists():return
    if not OLD.exists():raise FileNotFoundError(OLD)
    before=json.loads((OLD/'audit/FINAL_DELIVERY57.json').read_text())['file_sha256']
    for name,h in before.items():
        if digest(OLD/name)!=h:raise AssertionError('Baseline file differs: '+name)
    own={str(p.relative_to(R)):p.read_bytes() for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    shutil.copytree(OLD,R,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    for name,data in own.items():(R/name).write_bytes(data)
    preserved=R/'preserved/R57-active';preserved.mkdir(parents=True,exist_ok=True)
    for name in ('ECTA.tex','supp.tex','development.tex','development-supp.tex','complete.tex','complete-supp.tex','response.md','README.md'):
        shutil.copy2(OLD/name,preserved/name)
    import sys,re
    sys.path.insert(0,str(R/'code'))
    from assemble56 import expanded
    labels={name:sorted(set(re.findall(r'\\label\{([^}]+)\}',expanded(OLD,OLD/(name+'.tex'))))) for name in ('ECTA','supp','development','development-supp','complete','complete-supp')}
    protected={k:h for k,h in before.items() if k.split('/')[0] in ('code','inputs','evidence','results','results52','results53','results53-extension','results55','results55-tube','results57','attempts','preserved') or ('FREEZE' in k) or k.endswith('PROTOCOL57.md')}
    (R/'audit').mkdir(exist_ok=True)
    marker.write_text(json.dumps(dict(baseline_commit=BASE,review_commit='adf1256cff9cde365246a3db2dac90c72fda3b13',baseline_files_checked=len(before),protected_sha256=protected,baseline_labels=labels),sort_keys=True,indent=2)+'\n')
    (R/'README.md').write_text('# Neural Bellman Operators — R58\n\nSource-frozen revision in progress. The final publication is identified only by FINAL_DELIVERY58.json. Prior revisions and evidence are unchanged.\n')
    print(json.dumps({'baseline_files_checked':len(before),'protected':len(protected)}))
if __name__=='__main__':main()
