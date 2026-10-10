"""Materialize a new ordinary R60 directory; never change earlier revisions."""
from pathlib import Path
import hashlib,json,shutil,sys
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-09-r59'
BASE='00412e6a4f43100996b324ea1ace097232c3fbbf'
REVIEW='8f56a3ae24ef3ce4383d0e9d1d757bd3ed7378c6'

def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def main():
    marker=R/'audit/PREPARATION60.json'
    if marker.exists():return
    own={str(p.relative_to(R)):p.read_bytes() for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    old=json.loads((OLD/'audit/FINAL_DELIVERY59.json').read_text())
    for name,h in old['file_sha256'].items():
        if digest(OLD/name)!=h:raise AssertionError('Pinned R59 file differs: '+name)
    shutil.copytree(OLD,R,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    for name,data in own.items():p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    p=R/'preserved/R59-before-R60';p.mkdir(parents=True,exist_ok=True)
    for name in ('ECTA.tex','supp.tex','complete.tex','complete-supp.tex','development.tex','development-supp.tex','response.md','README.md'):shutil.copy2(OLD/name,p/name)
    sys.path.insert(0,str(R/'code'));from assemble56 import labels
    retained={}
    for folder in ('code','sections','results','results52','results53','results53-extension','results55','results55-tube','results57','results58','inputs','evidence','preserved','attempts'):
        for f in (OLD/folder).rglob('*'):
            if f.is_file() and '__pycache__' not in f.parts:
                name=str(f.relative_to(OLD));h=digest(f)
                if digest(R/name)!=h:raise AssertionError('Inherited file overwritten: '+name)
                retained[name]=h
    labelsets={d:labels(OLD,d) for d in ('ECTA','supp','complete','complete-supp','development','development-supp')}
    save(marker,dict(baseline_commit=BASE,controlling_review_commit=REVIEW,verified_prior_manifest_files=len(old['file_sha256']),retained_sha256=retained,baseline_labels=labelsets,earlier_branches_modified=False))
    (R/'README.md').write_text('# Neural Bellman Operators — R60\n\nOriginal-paper revision in development. Completed publication requires audit/FINAL_DELIVERY60.json. R59 and all historical evidence are retained.\n')
    print(json.dumps(dict(status='prepared',inherited_files=len(retained),labels={k:len(v) for k,v in labelsets.items()})))
if __name__=='__main__':main()
