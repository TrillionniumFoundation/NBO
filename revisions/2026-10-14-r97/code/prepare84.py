"""R84 ordinary-source materialization and additive editorial integration."""
from pathlib import Path
import argparse,hashlib,json,re,shutil
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-12-r83'
BASE='0f807677ac6f2a47455f49f061ddbc9710b28738'
FORBIDDEN={'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.afm','.tfm'}
def sha(p):
    with Path(p).open('rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def science():
    marker=R/'audit/PREPARATION84.json'
    if marker.exists():print('R84 already materialized; ordinary author sources retained.');return
    own={str(p.relative_to(R)):p.read_bytes() for p in R.rglob('*') if p.is_file()}
    if not (OLD/'results83/EXECUTION83.json').exists():raise FileNotFoundError('Pinned completed R83 recovery missing')
    shutil.copytree(OLD,R,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    for p in R.rglob('*'):
        if p.is_file() and p.suffix.lower() in FORBIDDEN:raise AssertionError('Standalone font cannot enter publication')
    for name,raw in own.items():p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    preserved=R/'preserved/R83-original';preserved.mkdir(parents=True,exist_ok=True)
    wrappers={};sections={}
    for doc in ('ECTA.tex','supp.tex','appendix.tex','response.md'):
        shutil.copy2(OLD/doc,preserved/doc);wrappers[doc]=sha(OLD/doc)
        if doc.endswith('.tex'):
            for name in re.findall(r'\\input\{(sections/[^}]+)\}',(OLD/doc).read_text()):
                if name in sections:raise AssertionError('Previously duplicated active section '+name)
                sections[name]=dict(document=doc,sha256=sha(OLD/(name+'.tex')))
    if (R/'build').exists():
        target=preserved/'build';target.mkdir(exist_ok=True)
        for p in (R/'build').glob('*.pdf'):shutil.copy2(p,target/p.name)
        shutil.rmtree(R/'build')
    (R/'build').mkdir();(R/'audit/build-logs').mkdir(parents=True,exist_ok=True)
    protected={}
    for p in OLD.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts:continue
        relative=p.relative_to(OLD)
        if relative.parts[0].startswith('results') or relative.parts[0] in ('code','preserved','inputs') or p.name.startswith(('SOURCE_FREEZE','ACTOR_FREEZE','OWN_SOURCE')):
            protected[str(relative)]=sha(p)
    save(marker,dict(baseline_commit=BASE,controlling_review='4b27b56f4514f6c1d77b69fe707f7202f8b06b19',original_wrappers=wrappers,active_sections=sections,protected_files=protected))
    (R/'README.md').write_text('# Neural Bellman Operators — R84 source revision\n\nOriginal-paper sources and pinned evidence are materialized. New full-menu and\ncommon-readout certificates are qualified by code/compatible84.py and independently\nchecked by code/verify84.py. A source push is not a completed publication.\n\nThe review-ready claim requires audit/FINAL_DELIVERY84.json, the four current PDFs,\nclean-archive reproduction, explicit PDF inspection and verified remote refs.\n')
    print('Preserved',len(sections),'active sections and',len(protected),'inherited source/evidence files.')

def editorial():
    marker=R/'audit/EDITORIAL84.json'
    if marker.exists():print('R84 ordinary editorial sources already integrated.');return
    a=json.loads((R/'audit/PREPARATION84.json').read_text())
    p=R/'ECTA.tex';text=p.read_text()
    insertions=[('\\input{sections/frontier83}','\\input{sections/compatible84}'),('\\input{sections/study83}','\\input{sections/study84}')]
    for needle,addition in insertions:
        if text.count(needle)!=1:raise AssertionError('Original main section missing '+needle)
        text=text.replace(needle,needle+'\n'+addition,1)
    abstract='This paper develops Neural Bellman Operators for constructive policy evaluation and feasible improvement under the original economic law. Attained continuations retain action witnesses and a quantified original-optimum error account. Representation-calibrated residual qualification and actionwise cost transfer connect approximate optimization to economic decisions. We strengthen that transfer by requiring an action to win its complete feasible menu and by retaining compatibility restrictions implied by one shared readout. Rational winner, separation and assignment duals certify the resulting policy-cost intervals without retraining or additional sampling. A deterministic study qualifies all previously admitted alternatives of four attained investment controllers and a fixed budget of joint events. The original factorial evidence, its reversal of the matched basis ranking, and every unresolved comparison remain visible. The resulting economic guarantees concern declared optimizer classes and resource charges, not universal neural dominance or a fitting success probability.'
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+abstract+'\n'+m[2],text,count=1,flags=re.S)
    bridge=r'''The same readout coefficients determine actions in every observation cell. Separate switch tests can therefore admit an alternative that never wins its full menu, or combinations of alternatives that no common readout can select. Section~\ref{sec:compatible84} retains both restrictions. An exact support dual certifies each winner event and selected joint events; a second, cell-assignment dual transfers the resulting compatibility information to original-law cost. This strengthens the existing NBO optimization-to-policy account without changing a fitted label, future controller or economic primitive.

The additional calculation is deterministic qualification of previously purchased evidence. It reports the incremental work of full-menu and shared-readout checks separately from construction, integration and policy-cost inference. The economic enclosure remains valid when a numerical solver is inconclusive, because only independently verified multipliers may exclude an event. Standard convex duality supplies the lower-bound principle \citep{boyd2004}; the contribution here is its connection to acquired NBO actions, common coefficients and the paid attained-policy cost event.

'''
    needle=r'\paragraph{Reading path.}'
    if text.count(needle)!=1:raise AssertionError('Original reading path missing')
    text=text.replace(needle,bridge+needle,1)
    ending=r'''\paragraph{Shared coefficients and economic accuracy.}
A qualified output is one controller, not an arbitrary independent choice in every observation cell. Full-menu and shared-readout certificates respect this distinction and supply a constructive refinement of the original actionwise stopping regions. The assignment relaxation need not be an attainable optimizer policy, and every numerical upper bound is therefore identified as an enclosure rather than an observed worst-case loss. The verified common-coefficient restriction strengthens the economic use of the original NBO construction while preserving its original scope and all adverse evidence.
'''
    text=text.replace(r'\bibliographystyle{ecta-fullname}',ending+'\n'+r'\bibliographystyle{ecta-fullname}',1)
    text=text.replace(r'\bibliography{references,references78}',r'\bibliography{references,references78,references84}')
    p.write_text(text)
    p=R/'appendix.tex';text=p.read_text();needle=r'\bibliographystyle{ecta-fullname}'
    if text.count(needle)!=1:raise AssertionError('Appendix bibliography marker')
    text=text.replace(needle,r'\input{sections/proof84}'+'\n'+needle,1);p.write_text(text)
    if not (R/'response84.md').exists():raise FileNotFoundError('Point-by-point R84 response')
    shutil.copy2(R/'response84.md',R/'response.md')
    (R/'references84.bib').write_text('@book{boyd2004, author={Stephen Boyd and Lieven Vandenberghe}, title={Convex Optimization}, publisher={Cambridge University Press}, year={2004}}\n')
    entries=R/'publication/bibliography-entries.json'
    if entries.exists():
        data=json.loads(entries.read_text());data['boyd2004']=r'\bibitem[Boyd and Vandenberghe(2004)]{boyd2004}'+'\n'+r'\textsc{Boyd, Stephen, and Lieven Vandenberghe} (2004): \emph{Convex Optimization}. Cambridge: Cambridge University Press.';save(entries,data)
    (R/'CONTENT_MAP84.md').write_text('# R84 content map\n\nAll '+str(len(a['active_sections']))+' inherited active sections remain byte-identical and compiled once in their original document. Original wrappers and any inherited PDFs are explicitly preserved under preserved/R83-original.\n\nNew main sections: sections/compatible84.tex (full theorem and proof) and sections/study84.tex (complete numerical comparison). New appendix section: sections/proof84.tex (dual construction, relaxation limits and catalogue records). ECTA.tex, supp.tex, appendix.tex and response.md are the ordinary active sources.\n\nNew exact source, output, verification and publication manifests are separate from inherited execution clocks.\n')
    save(marker,dict(status='integrated',preserved_active_sections=len(a['active_sections']),new_main=['sections/compatible84.tex','sections/study84.tex'],new_appendix=['sections/proof84.tex'],original_title=True))
    print('R84 ordinary editorial sources integrated without deleting an inherited section.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('science','editorial'));a=p.parse_args();science() if a.mode=='science' else editorial()
