"""Additive R59 integration of the original NBO manuscript.
All R58 scientific code/results and prior manuscript snapshots are retained.
The assembler runs once, then refuses to overwrite ordinary author edits.
"""
from pathlib import Path
import difflib,json,re,shutil,subprocess
from prepare59 import main as prepare,digest,save,BASE,BASE_SHA,REVIEW_SHA
from assemble56 import labels
R=Path(__file__).resolve().parents[1]
ABSTRACT=r'''We develop Neural Bellman Operators that construct continuations from their own fitted futures and return feasible economic policies. A constructive backend relates primitive approximation resources to loss against the original Bellman optimum. For trained affine--ReLU continuations in the investment model, analytic innovation integration yields exact action witnesses. We prove that lossless interval screening preserves these witnesses, the resulting whole-cell certificates and a prospective controller's stopping decisions, while controlling the number of exact comparisons under explicit separation conditions. The fitted-witness transfer theorem keeps optimization, acquisition, continuation and verification errors distinct. In the original nonlinear investment family, non-tensor services in two, four and eight dimensions evaluate prespecified economic targets. A matched execution compares complete computation costs for identical returned policies; separate conventional-method comparisons retain their own policy-cost evidence. All failed targets, earlier applications and adverse outcomes are preserved.'''
INTRO=r'''\paragraph{Computing the same economic answer at lower recorded cost.}
An exact trained-neural action witness also raises an implementation question. Analytically integrated ReLU features can be reduced exactly on an action region and used to eliminate nonminimizing lattice points through outward bounds. Section~\ref{sec:lossless59} proves that rational comparison of the survivors returns the original exact witness. It then proves that replacing the solver inside a mathematical prospective controller preserves its entire policy and stopping history. Section~\ref{sec:study59} tests this intervention with independently reconstructed, matched services in the original investment family. Its economic object is the complete cost of returning an identical policy, not a welfare difference between equivalent encodings. This extends the original construction--witness--verification--return chain while retaining the conventional comparisons and their actual cost classifications.
'''
CONCLUSION=r'''The lossless-search result makes that distinction operational at an unchanged answer. Exact activation-region reduction and outward screening preserve the trained-neural witness; conditional transcript invariance preserves the returned policy, all-state certificate and first-attainment rule. The separately frozen matched execution records lower complete-process median work in each declared task--target group, while retaining the unsuccessful target as unsuccessful. Its equal-policy resource comparison is distinct from the earlier comparisons between different neural and conventional policies. The original Bellman objective, feasibility requirements and economic laws are unchanged.

'''

def put(path,text):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
def insert_once(text,needle,extra,after=True):
    if text.count(needle)!=1:raise AssertionError('Expected one insertion point: '+needle)
    return text.replace(needle,needle+'\n'+extra if after else extra+'\n'+needle,1)
def main():
    marker=R/'audit/ASSEMBLY59.json'
    if marker.exists():print('R59 ordinary sources already assembled; author edits retained.');return
    prepare();prep=json.loads((R/'audit/PREPARATION59.json').read_text())
    # A main-article map reference is unnecessary in the complete companion.
    p=R/'sections/lossless59.tex';text=p.read_text().replace(', as in Section~\\ref{sec:map56}', '');put(p,text)
    put(R/'sections/intro59.tex',INTRO)
    p=R/'ECTA.tex';text=p.read_text()
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+ABSTRACT+'\n'+m[2],text,count=1,flags=re.S)
    text=insert_once(text,r'\input{sections/intro57}',r'\input{sections/intro59}')
    text=insert_once(text,r'\input{sections/moduli57}',r'\input{sections/lossless59}')
    text=insert_once(text,r'\input{sections/study57}',r'\input{sections/study59}')
    text=insert_once(text,r'\appendix',CONCLUSION,False);put(p,text)
    p=R/'supp.tex';text=insert_once(p.read_text(),r'\input{sections/supp57}',r'\input{sections/supp59}');put(p,text)
    for name,sections in [('complete',('lossless59','study59')),('complete-supp',('supp59',))]:
        p=R/(name+'.tex');text=p.read_text();extra='\n'.join(r'\input{sections/'+s+'}' for s in sections)
        text=insert_once(text,r'\bibliographystyle{ecta-fullname}',extra,False)
        notice=r'\section*{Current reading notice}'+'\nThe R59 article and response form the current submission. This companion retains the preceding NBO development and adds lossless trained-neural action recovery and its matched prospective work study. Historical claims refer to their own cohorts and hypotheses.\n'
        text=insert_once(text,r'\end{frontmatter}',notice);put(p,text)
    put(R/'response.md',(R/'response59.md').read_text())
    # Retain the exact controlling advisory report when it is present in the
    # pinned repository; absence is reported, never filled by an invented text.
    review=R.parents[1]/'reviews/2026-10-09-econometrica-numerical-methods-r54/referee_report.md'
    review_record=None
    if review.exists():
        dest=R/'inputs/reviews/R54-2026-10-09/referee_report.md';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(review,dest)
        review_record=dict(path=str(dest.relative_to(R)),sha256=digest(dest))
    retained=dict(prep['retained_sha256'])
    for p in (BASE/'sections').rglob('*'):
        if p.is_file():
            name=str(p.relative_to(BASE));h=digest(p)
            if digest(R/name)!=h:raise AssertionError('Inherited section changed: '+name)
            retained[name]=h
    preservation={}
    for name,before in prep['baseline_labels'].items():
        now=set(labels(R,name));missing=sorted(set(before)-now)
        if missing:raise AssertionError((name,'Inherited labels missing',missing))
        preservation[name]=dict(before=len(before),after=len(now),missing=[])
    save(marker,dict(baseline_commit=BASE_SHA,controlling_review_commit=REVIEW_SHA,baseline_labels=prep['baseline_labels'],retained_sha256=retained,initial_label_check=preservation,review_copy=review_record,previous_branches_modified=False,new_independent_observations=0,scope='Original title and mathematical/economic core retained; ordinary manuscript sources extended with proved lossless computation and audited existing R58 execution.'))
    for name in ('ECTA','supp','complete','complete-supp'):
        put(R/'audit'/(name+'-R58-to-R59.diff'),''.join(difflib.unified_diff((BASE/(name+'.tex')).read_text().splitlines(True),(R/(name+'.tex')).read_text().splitlines(True),fromfile='R58/'+name+'.tex',tofile='R59/'+name+'.tex')))
    put(R/'README.md',r'''# Neural Bellman Operators — R59

The active submission consists of [the main paper](build/ECTA.pdf),
[technical supplement](build/supp.pdf), and [point-by-point response](build/response.pdf).
The complete/development companions retain the original applications, proofs,
failed attempts and adverse comparisons. The title, economic laws, constructive
own-future backend and original Bellman-accuracy target remain unchanged.

R59 proves lossless integrated-neural action screening, explicit survivor/work
bounds and prospective policy/stopping invariance. It integrates and fully
replays the already executed, separately frozen R58 36-service matched study.
It creates no new training services or independent policy-cost observations.

## Reading and evidence

The new theory is in `sections/lossless59.tex`; the matched original-law
experiment is in `sections/study59.tex`. The supplement displays every timing
repetition, service return, operation count and datewise certificate. The
controlling R54 advisory report, R57 conventional comparisons and all earlier
scientific sources retain their own provenance.

The completed publication requires `audit/FINAL_DELIVERY59.json`, together with
`audit/RELEASE59.json` and `audit/CLEAN_REBUILD59.json`. Merely having ordinary
sources or a descriptive inspection file is not a completed publication.
`audit/RESULT_AUDIT59.json` records full saved-model, solver, certificate, path,
exact-moment and prospective-decision reconstruction. A recorded repeated stream
is checked for identity, not counted as a new independent sample.

## Offline reproduction

From the repository root:

    python3 revisions/2026-10-09-r59/code/build59.py

Dependencies are Python 3 with numpy, scipy, sympy and scikit-learn; pandoc,
poppler-utils, and the LaTeX packages used by econsocart. The full build repeats
scientific reconstruction and all inherited tests without training or drawing
new samples. `--publication-only` validates the full scientific binding and
rebuilds documents, rather than claiming another scientific execution.

The fixed-seed matched workload identifies equal-policy recorded computation
costs. The conventional-policy comparison, universal hardware/instance claims,
and externally calibrated welfare are different questions. Every target that
exhausts its budget remains labeled as such. Mathematical or editorial peer
acceptance is not asserted by successful code and document checks.
''')
    print(json.dumps(dict(status='assembled',retained_files=len(retained),labels=preservation,review_copy=review_record),indent=2))
if __name__=='__main__':main()
