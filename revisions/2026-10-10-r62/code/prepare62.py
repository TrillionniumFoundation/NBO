"""One-time preparation of a new, self-contained R62 directory."""
from pathlib import Path
import hashlib,json,shutil,sys
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-09-r61'
DOCS=('ECTA','supp','development','development-supp','complete','complete-supp','response')
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    marker=R/'audit/PREPARATION62.json'
    if marker.exists():print('R62 ordinary sources already prepared; predecessor will not overwrite them.');return
    own={str(p.relative_to(R)):p.read_bytes() for p in R.rglob('*') if p.is_file()}
    shutil.copytree(OLD,R,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    for name,data in own.items():p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    keep=R/'preserved/predecessor61';keep.mkdir(parents=True,exist_ok=True)
    for name in [*(d+'.tex' for d in DOCS),'response.md','README.md','references.bib','preamble.tex']:
        if (OLD/name).exists():shutil.copy2(OLD/name,keep/name)
    (keep/'build').mkdir(exist_ok=True)
    for p in (OLD/'build').glob('*.pdf'):shutil.copy2(p,keep/'build'/p.name)
    if (R/'build').exists():shutil.rmtree(R/'build')
    (R/'build').mkdir();(R/'audit').mkdir(exist_ok=True)
    sys.path.insert(0,str(OLD/'code'));from assemble56 import labels
    labelsets={d:labels(OLD,d) for d in DOCS if d!='response'}
    protected={}
    for p in OLD.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts:continue
        rel=p.relative_to(OLD)
        if rel.parts[0] in ('build','audit','tables','publication'):continue
        if len(rel.parts)==1:continue
        protected[str(rel)]=digest(p)
        if digest(R/rel)!=protected[str(rel)]:raise AssertionError('Predecessor changed: '+str(rel))
    marker.write_text(json.dumps(dict(baseline_commit='19f17cef194b620cfbf9d33e7c78ee051a2dddf0',review_commit='08ca068d318ce159401b36655eccea1e05490d01',baseline_labels=labelsets,protected_sha256=protected,scope='Original branches and predecessor scientific files are unchanged; ordinary R62 wrappers are separate author sources.'),indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(prepared=True,protected_files=len(protected),inherited_labels={d:len(v) for d,v in labelsets.items()})),flush=True)
if __name__=='__main__':main()
