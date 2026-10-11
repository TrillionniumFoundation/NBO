"""Preserve the pinned original manuscript around ordinary edited R75 sources."""
from pathlib import Path
import hashlib,json,re,shutil
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-11-r74'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    marker=R/'audit/PREPARATION75.json'
    if marker.exists():return
    wrappers={n:(OLD/n).read_bytes() for n in ('ECTA.tex','supp.tex','appendix.tex','response.md','response.tex','README.md')};active={}
    for d in ('ECTA','supp','appendix'):
        for name in re.findall(r'\\input\{(sections/[^}]+)\}',wrappers[d+'.tex'].decode()):active[name+'.tex']=sha(OLD/(name+'.tex'))
    dest=R/'preserved/R74-base';dest.mkdir(parents=True,exist_ok=True)
    for n,data in wrappers.items():(dest/n).write_bytes(data)
    a={'status':'integrated','base_commit':'5b6bb84fe02e6c7295624c1d9ba5266eef6c5717','review_commit':'4b27b56f4514f6c1d77b69fe707f7202f8b06b19','active_sections':active,'prior_wrapper_sha256':{n:hashlib.sha256(v).hexdigest() for n,v in wrappers.items()},'old_wrapper_labels':{d:re.findall(r'\\label\{([^}]+)\}',wrappers[d+'.tex'].decode()) for d in ('ECTA','supp','appendix')},'old_branches_modified':False}
    marker.parent.mkdir(exist_ok=True);marker.write_text(json.dumps(a,indent=2,sort_keys=True)+'\n')
    lines=['# R75 content preservation map','','The original title, author, economic model and optimum remain. All 25 preceding active sections are compiled byte-identically once. Original wrappers are retained in preserved/R74-base.','','| Prior section | Current document | SHA-256 |','|---|---|---|']
    for name,h in active.items():
        if sha(R/name)!=h:raise AssertionError('Inherited section altered: '+name)
        ds=[d for d in ('ECTA','supp','appendix') if r'\input{'+name[:-4]+'}' in (R/(d+'.tex')).read_text()]
        if len(ds)!=1:raise AssertionError((name,ds))
        lines.append('| '+name+' | '+ds[0]+' | '+h+' |')
    (R/'CONTENT_MAP75.md').write_text('\n'.join(lines)+'\n')
    (R/'README.md').write_text('''# Neural Bellman Operators — R75

Active manuscripts: build/ECTA.pdf, build/supp.pdf, build/appendix.pdf and
build/response.pdf. Ordinary sources have the same stems. The new theorem and
primitive details are sections/displacement75.tex and sections/proofs75.tex.
All original-law costs and precision outcomes are in sections/study75.tex and
tables/*75.tex. CONTENT_MAP75.md binds all preceding active content.

The controlling report is the 11 October 2026 advisory report on R67. The
pinned development base is 5b6bb84fe02e6c7295624c1d9ba5266eef6c5717.
R75 executes the previously frozen R74 design on the four attained R73
controllers, without refitting, changing the sample or counting replays as
new samples. Both attained ReLU controllers have lower original-law cost than
their matched Bernstein controllers. Seven of eight paired width targets
pass; the failed target is retained. This is not universal neural superiority.

SOURCE_FREEZE74.json binds the prospective scientific code and controllers.
results74 contains the complete bins and both path-enclosure implementations.
audit/RESULT_AUDIT75.json additionally re-evaluates every integer path,
acquired range, support and exact confidence endpoint. The final manifest is
 audit/FINAL_DELIVERY75.json and is valid only with status passed after a
full build, clean archive rebuild and actual hash-bound PDF visual review.

Full offline build: python3 revisions/2026-10-11-r75/code/build75.py --full

Old review and revision branches and historical adverse observations remain
unchanged. Source and staged branches are not substitutes for the final
review-ready branch and its completed manifest.
''')
    print(json.dumps({'preserved_active_sections':len(active),'status':'prepared'}))
if __name__=='__main__':main()
