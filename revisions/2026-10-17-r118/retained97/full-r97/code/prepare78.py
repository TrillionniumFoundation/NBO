"""One-time ordinary-source R78 integration; all old branches stay unchanged."""
from pathlib import Path
import hashlib,json,re,shutil
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-11-r77'
BASE='21a99a92c9a8aed96b36931467a40cd7b82aeeb6'
REVIEW='4b27b56f4514f6c1d77b69fe707f7202f8b06b19'
ABSTRACT='''This paper develops Neural Bellman Operators for constructive policy evaluation and feasible improvement. Witness-preserving continuations and qualification-optimal readouts connect attained approximation to the original Bellman optimum. Exact conditional integration and independently implemented whole-bin evaluation qualify the original-law costs of the resulting complete controllers. A simultaneous choice theorem gives sharp catalogue-regret certificates and price-uniform selection regions from marginal and paired cost intervals. In the fixed nonlinear-investment experiment, attained ReLU controllers have lower expected cost than matched Bernstein controllers at both acquisition resolutions. The joint intervals also identify the cost ordering and the charge at which the regret-minimizing acquisition choice changes. These finite comparisons remain distinct from the adverse work findings for optional neural query proposals. The original recursive, vector, predictable-qualification and witnessed-reuse results retain their proofs, computational accounts and historical evidence.'''
INTRO=r'''\paragraph{Choosing among the attained controllers.}
The original-law evaluation now identifies strictly lower costs for the attained ReLU continuation controllers than for the matched Bernstein controllers at both acquisition resolutions. Section~\ref{sec:choice78} uses all jointly qualified marginal and paired costs to choose among these actual controllers. Its sharp regret certificate and exact refinement-fee region are valid for every assignment of resource charges on the same coverage event. This does not infer a neural work advantage for the different recursive-query policies, nor does it replace the original continuous Bellman optimum by the best member of a finite catalogue.
'''
CONCLUSION=r'''The attained-controller comparison is positive and specific: both matched ReLU policies have lower qualified original-law cost than their Bernstein counterparts. The joint evidence orders all five implemented controllers and identifies when the cost gain from finer acquisition pays its incremental charge. The new choice theorem uses the complete paired information and supplies attaining cost vectors for its worst-case guarantee. A calibrated monetary conclusion still requires an explicit loss scale and actual resource charges; no universal neural speed or representation ranking follows from this finite economic comparison.
'''

def sha(p):
    with p.open('rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
    marker=R/'audit/PREPARATION78.json'
    if marker.exists():print('Ordinary R78 sources already integrated; preserving later edits.');return
    own={str(p.relative_to(R)):p.read_bytes() for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    shutil.copytree(OLD,R,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    for name,content in own.items():
        p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
    saved=R/'preserved/R77-original';saved.mkdir(parents=True,exist_ok=True)
    wrappers={};labels={};sections={}
    for name in ('ECTA.tex','supp.tex','appendix.tex','response.md','README.md'):
        shutil.copy2(OLD/name,saved/name);wrappers[name]=sha(OLD/name)
        if name.endswith('.tex'):
            text=(OLD/name).read_text();labels[name]=re.findall(r'\\label\{([^}]+)\}',text)
            for relative in re.findall(r'\\input\{(sections/[^}]+)\}',text):
                path=relative+'.tex';sections[path]=sha(OLD/path)
    shutil.rmtree(R/'build');(R/'build').mkdir()
    p=R/'ECTA.tex';text=p.read_text()
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+ABSTRACT+'\n'+m[2],text,count=1,flags=re.S)
    needle=r'\paragraph{Reading path.}'
    if text.count(needle)!=1:raise AssertionError('Reading-path insertion anchor')
    text=text.replace(needle,INTRO+'\n'+needle,1)
    needle=r'\input{sections/cost77}'
    if text.count(needle)!=1:raise AssertionError('Original cost section missing')
    text=text.replace(needle,needle+'\n'+r'\input{sections/choice78}',1)
    text=text.replace(r'\bibliographystyle{ecta-fullname}',CONCLUSION+'\n'+r'\bibliographystyle{ecta-fullname}',1)
    text=text.replace('The retained cost-inference evidence identifies equivalence','The retained recursive-controller cost-inference evidence identifies equivalence')
    p.write_text(text)
    p=R/'appendix.tex';text=p.read_text();needle=r'\bibliographystyle{ecta-fullname}'
    if text.count(needle)!=1:raise AssertionError('Appendix bibliography insertion anchor')
    text=text.replace(needle,r'\input{sections/choice_proof78}'+'\n'+needle,1);p.write_text(text)
    (R/'response.md').write_text((R/'response78.md').read_text())
    # Publication-only adapter. Scientific sources and freezes are unchanged.
    p=R/'code/build77.py';text=p.read_text().replace('Revision R77 responds','Revision R78 responds')
    text=text.replace('and priced selection extend the retained theory and evidence.','and sharp price-uniform catalogue choice extend the retained theory and evidence.')
    p.write_text(text)
    p=R/'publication/bibliography-entries.json';entries=json.loads(p.read_text())
    entries['floyd1962']=r'\bibitem[\protect\citeauthoryear{Floyd}{Floyd}{1962}]{floyd1962}'+'\n'+r'\textsc{Floyd, Robert W.} (1962): \enquote{Algorithm 97: Shortest Path,} \emph{Communications of the ACM}, 5 (6), 345.'
    save(p,entries)
    p=R/'references.bib';text=p.read_text()
    if '@article{floyd1962' not in text:
        text+='\n@article{floyd1962,\n author={Robert W. Floyd},\n title={Algorithm 97: Shortest Path},\n journal={Communications of the ACM},\n volume={5},\n number={6},\n pages={345},\n year={1962},\n doi={10.1145/367766.368168}\n}\n'
    p.write_text(text)
    evidence={}
    for directory in ('results77','results73','results72','results69','receipts69','logs69','inputs','evidence'):
        for p in (OLD/directory).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:evidence[str(p.relative_to(OLD))]=sha(p)
    for p in OLD.glob('*FREEZE*.json'):evidence[p.name]=sha(p)
    save(marker,dict(base_commit=BASE,controlling_review_commit=REVIEW,original_wrappers=wrappers,
        wrapper_labels=labels,unchanged_active_sections=sections,unchanged_evidence=evidence,
        added_sections=['sections/choice78.tex','sections/choice_proof78.tex'],
        new_scientific_services=0,new_simulation_rows=0,scope='Original NBO paper with additional sharp catalogue-choice theorem and exact decision postprocessing; all historical models, evidence and unfavorable comparisons retained'))
    (R/'CONTENT_MAP78.md').write_text('''# R78 content preservation

The original title, author, investment law and Bellman target are unchanged.
All R77 active section files remain byte-identical and are compiled exactly
once across the main article, Technical Supplement and Numerical and Development
Appendix. Their R73/R72/R70 predecessors and complete historical companions
retain the inherited preservation checks. Original R77 wrappers and response
are in preserved/R77-original. Earlier repository branches are untouched.

The main article adds sections/choice78.tex; its full proof, attaining-vector
construction and exact decision tables are in sections/choice_proof78.tex in
the Numerical and Development Appendix. No old theorem or adverse experiment
is deleted to make room for the addition. The prior 524,288 cost rows are
re-evaluated but are not counted as new observations. DECISION78.json records
all 30 original estimands, exact graph constraints and attaining cost vectors.
''')
    (R/'README.md').write_text('''# Neural Bellman Operators — R78

[Main article](build/ECTA.pdf) · [Technical Supplement](build/supp.pdf) ·
[Numerical and Development Appendix](build/appendix.pdf) · [Response](build/response.pdf)

This is a revision of the original NBO paper responding to the 11 October 2026
R67 advisory report. It retains the attained continuation construction and its
actual original-law cost experiment. The new theorem gives sharp simultaneous
catalogue-choice certificates, an identified cost ordering and exact refinement
charge regions. The classical graph reduction is attributed, not claimed new.

Reproduction from the repository root:

    python3 revisions/2026-10-11-r78/code/build78.py

The full build repeats all inherited suites, independently recomputes every
R77 cost bin with both arithmetic implementations, and tests the new exact
choice calculation. No scientific service is retimed and no sample is added.
RELEASE78.json records compilation and replay. A separately hash-bound visual
record and FINAL_DELIVERY78.json are required before a review-ready release.
See CONTENT_MAP78.md for unchanged historical content.
''')
    print(json.dumps(dict(status='assembled',active_sections=len(sections),evidence_files=len(evidence),base=BASE)))
if __name__=='__main__':main()
