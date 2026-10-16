"""Copy the pinned R81 development into an independent ordinary-source revision."""
from pathlib import Path
import hashlib,json,re,shutil
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-12-r81'

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    marker=R/'audit/PREPARATION82.json'
    if marker.exists():
        print('R82 ordinary sources already materialized; preserving author edits.');return
    own={str(p.relative_to(R)):p.read_bytes() for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    shutil.copytree(OLD,R,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    for n,v in own.items():
        p=R/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
    original=R/'preserved/R81-original';original.mkdir(parents=True,exist_ok=True)
    wrappers=('ECTA.tex','supp.tex','appendix.tex','response.md','response.tex','README.md','CONTENT_MAP81.md')
    for name in wrappers:shutil.copy2(OLD/name,original/name)
    if (R/'build').exists():
        shutil.copytree(R/'build',original/'build',dirs_exist_ok=True);shutil.rmtree(R/'build')
    (R/'build').mkdir()
    protected={str(p.relative_to(OLD)):sha(p) for p in OLD.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.relative_to(OLD).parts[0] not in ('build','audit','tables') and str(p.relative_to(OLD)) not in wrappers}
    active={}
    for name in ('ECTA.tex','supp.tex','appendix.tex'):
        for rel in re.findall(r'\\input\{(sections/[^}]+)\}',(OLD/name).read_text()):
            if rel in active:raise AssertionError('Duplicated inherited section')
            active[rel]=dict(document=name,sha256=sha(OLD/(rel+'.tex')))
    current=dict(baseline_commit='c411bfb2badac2981f001f4c84d99c8c3c306c5e',review_commit='4b27b56f4514f6c1d77b69fe707f7202f8b06b19',protected_files=protected,
        original_wrappers={n:sha(OLD/n) for n in wrappers},active_sections=active,
        wrapper_labels={n:re.findall(r'\\label\{([^}]+)\}',(OLD/n).read_text()) for n in ('ECTA.tex','supp.tex','appendix.tex')})
    marker.parent.mkdir(parents=True,exist_ok=True);marker.write_text(json.dumps(current,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(protected_inherited_files=len(protected),inherited_active_sections=len(active))))
if __name__=='__main__':main()
