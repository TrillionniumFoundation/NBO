"""Assemble ordinary R77 sources without editing a historical revision.

Every prior active section remains byte-identical and is compiled exactly
once. The fixed R77 scientific code and records are never overwritten.
"""
from pathlib import Path
import hashlib,json,re,shutil
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-11-r73'
DOCS=('ECTA','supp','appendix','response')
BASE='2d7d9c4e62abc2230087f3a092a5c493b8ca6cb0'
REVIEW='4b27b56f4514f6c1d77b69fe707f7202f8b06b19'
ABSTRACT='''This paper develops Neural Bellman Operators for constructive policy evaluation and feasible improvement. A witness-preserving continuation connects approximation resources to the original economic optimum. Qualification-optimal fixed-feature readouts have exact primal--dual certificates and use their actual fitted futures. We connect the resulting complete controllers to independent original-law cost observations, with exact conditional integration and explicit numerical, sampling and support allowances. Simultaneous cost intervals support priced controller selection and replacement over a declared deployment horizon. A fixed nonlinear-investment experiment evaluates the attained ReLU and conventional constructions using two independently implemented full-bin arithmetic procedures. The original recursive verifier, predictable qualification and witnessed-reuse results remain available with their complete proofs and separate computational accounts. All earlier conventional comparisons, adverse findings and broader applications are retained under their original hypotheses.'''
BRIDGE=r'''\paragraph{From the attained fit to an economic controller.}
A qualified continuation and a precisely evaluated complete policy are not interchangeable. Section~\ref{sec:cost77} evaluates the very actors returned by the backward continuation constructions. Their original fitted futures and acquired actions are frozen before new original-law observations. Exact final-innovation integration preserves the estimand, while a full-bin endpoint calculation keeps acquisition and numerical uncertainty explicit. A simultaneous width account and priced-selection result connect this evaluation to a controller choice. Two independent arithmetic implementations and an exhaustive replay make the additional economic calculation checkable without querying another optimal-value descendant tree.
'''
READING=r'''\paragraph{Reading path.}
Sections~\ref{sec:core49}--\ref{sec:query63} retain the constructive operator, original investment primitives and recursive guarantee. Sections~\ref{sec:operational67}--\ref{sec:vector67} give operational and vector certificates. Sections~\ref{sec:frozen72}--\ref{sec:sequential73} connect attained continuation qualification to original-law observations and valid stopping. Section~\ref{sec:cost77} gives the new complete-controller cost qualification and experiment. The Technical Supplement supplies the complete proofs. The Numerical and Development Appendix retains all earlier numerical, deployment, economic and witnessed-reuse sections unchanged, including Sections~\ref{sec:reuse72}, \ref{sec:study72} and \ref{sec:study73}, and reports every new contrast and numerical allowance. The original broader applications and complete editions remain historical companions.
'''
CONCLUSION=r'''The final link is the cost of the actual constructed controller. Original-law cash observations and exact conditional integration refer to the same frozen acquired actors, rather than to a replacement search policy. Their simultaneous intervals distinguish a precision target, equivalence at a declared loss band and strict improvement. Priced selection and replacement use those intervals on one coverage event for all nonnegative resource prices. These are decisions within the original NBO economy; they neither infer a universal neural ranking nor assign an empirical monetary calibration to normalized losses. The complete interval and work records allow the attained continuation fit and its economic consequences to be assessed together.
'''

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,record):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
def main():
    marker=R/'audit/PREPARATION77.json'
    if marker.exists():print('R77 ordinary reading sources already assembled; author edits retained.');return
    if not OLD.exists():raise FileNotFoundError(OLD)
    new_hashes={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file()}
    for source in OLD.rglob('*'):
        if not source.is_file() or '__pycache__' in source.parts or source.relative_to(OLD).parts[0]=='build':continue
        target=R/source.relative_to(OLD)
        if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    (R/'build').mkdir(exist_ok=True);(R/'audit/build-logs').mkdir(parents=True,exist_ok=True)
    inherited={};oldlabels={};wrappers={}
    preserved=R/'preserved/R73-original';preserved.mkdir(parents=True,exist_ok=True)
    for name in ('ECTA.tex','supp.tex','appendix.tex','response.md','response.tex','README.md'):
        shutil.copy2(OLD/name,preserved/name);wrappers[name]=sha(preserved/name)
    for doc in DOCS[:-1]:
        text=(OLD/(doc+'.tex')).read_text();oldlabels[doc]=re.findall(r'\\label\{([^}]+)\}',text)
        for name in re.findall(r'\\input\{(sections/[^}]+)\}',text):
            file=name+'.tex';inherited[file]=dict(sha256=sha(OLD/file),original_document=doc)
    moved=('sections/reuse72','sections/study72','sections/study73')
    mainfile=R/'ECTA.tex';text=mainfile.read_text()
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+ABSTRACT+'\n'+m[2],text,count=1,flags=re.S)
    for section in moved:
        needle='\\input{'+section+'}'
        if text.count(needle)!=1:raise AssertionError('Expected single inherited input: '+section)
        text=text.replace(needle+'\n','',1)
    text=text.replace(r'\paragraph{Reading path.}',BRIDGE+'\n'+r'\paragraph{Reading path.}',1)
    text=re.sub(r'\\paragraph\{Reading path\.\}.*?(?=\\input\{sections/core49\})',lambda m:READING+'\n',text,count=1,flags=re.S)
    text=text.replace(r'\section{Conclusion}\label{sec:conclusion65}',r'\input{sections/cost77}'+'\n'+r'\section{Conclusion}\label{sec:conclusion65}',1)
    text=text.replace(r'\bibliographystyle{ecta-fullname}',CONCLUSION+'\n'+r'\bibliographystyle{ecta-fullname}',1)
    text=text.replace('label=e73ECTA','label=e77ECTA');mainfile.write_text(text)
    supplement=R/'supp.tex';text=supplement.read_text().replace('label=e73supp','label=e77supp')
    needle=r'\bibliographystyle{ecta-fullname}'
    if needle not in text:raise AssertionError('Supplement bibliography missing')
    text=text.replace(needle,r'\input{sections/proofs77}'+'\n'+needle,1);supplement.write_text(text)
    appendix=R/'appendix.tex';text=appendix.read_text().replace('label=e73appendix','label=e77appendix')
    if needle not in text:raise AssertionError('Appendix bibliography missing')
    additions='\n'.join('\\input{'+name+'}' for name in moved)+'\n'+r'\input{sections/numerical77}'+'\n'
    text=text.replace(needle,additions+needle,1);appendix.write_text(text)
    (R/'response.md').write_text((R/'response77.md').read_text())
    companions=[]
    for p in sorted((OLD/'build').glob('*.pdf')):
        name='prior-'+p.stem+'73.pdf' if p.stem in DOCS else p.name
        if name in tuple(d+'.pdf' for d in DOCS):raise AssertionError('Companion collision')
        shutil.copy2(p,R/'build'/name);companions.append(dict(file='build/'+name,source=str(p.relative_to(R.parent.parent)),sha256=sha(p)))
    for file,record in inherited.items():
        if sha(R/file)!=record['sha256']:raise AssertionError('Inherited section bytes altered')
        needle='\\input{'+file[:-4]+'}'
        docs=[doc for doc in DOCS[:-1] if needle in (R/(doc+'.tex')).read_text()]
        if len(docs)!=1:raise AssertionError('Section missing or duplicated: '+file)
        record['current_document']=docs[0]
    for name,h in new_hashes.items():
        if sha(R/name)!=h:raise AssertionError('New scientific or authored source overwritten: '+name)
    evidence={str(p.relative_to(OLD)):sha(p) for folder in ('results72','results73') for p in (OLD/folder).rglob('*') if p.is_file()}
    record=dict(base_commit=BASE,controlling_review_commit=REVIEW,inherited_active_sections=inherited,
        original_wrappers=wrappers,wrapper_labels=oldlabels,inherited_evidence=evidence,companions=companions,
        all_inherited_sections_compiled_once=True,scientific_code_or_records_overwritten=False)
    save(marker,record)
    lines=['# R77 content preservation','',f'Base commit: `{BASE}`. Controlling advisory review: `{REVIEW}`.','',
        'The title, author, primitives and original optimum are unchanged. Every R73 active section is compiled byte-identically exactly once. The following moves change organization, not content.','',
        '| Retained source | Previous document | Current document |','|---|---|---|']
    lines += ['| `'+name+'` | '+v['original_document']+' | '+v['current_document']+' |' for name,v in inherited.items()]
    lines += ['','Original wrappers and the prior response are preserved in `preserved/R73-original`. Prior complete PDFs remain unchanged companions. New statements are in `sections/cost77.tex`, complete additional proofs in `sections/proofs77.tex`, and all new numerical details in `sections/numerical77.tex`.','',
        'The source-only R74--R76 commitments are not counted as executed scientific results. The current build checks both the inherited preservation ledgers and this exact section/evidence map.']
    (R/'CONTENT_MAP77.md').write_text('\n'.join(lines)+'\n')
    (R/'README.md').write_text('''# Neural Bellman Operators — R77

The same original paper, author, economic primitives and Bellman optimum are retained.
The controlling advisory review is the R67 report dated 11 October 2026.

## Reading set

[Main article](build/ECTA.pdf), [Technical Supplement](build/supp.pdf),
[Numerical and Development Appendix](build/appendix.pdf), and
[point-by-point response](build/response.pdf).
Ordinary editable sources are ECTA.tex, supp.tex, appendix.tex and response.md.
All prior active section bytes, results and broader companions are preserved;
see CONTENT_MAP77.md and audit/PREPARATION77.json.

## Additional contribution

The costs evaluated are those of the actual four qualified backward NBO
constructions, not substitute recursive controllers. Exact final-innovation
integration, explicit precision components and simultaneous priced selection
connect attained fitting to an original-law economic decision. The prospectively
fixed 524,288-row catalogue uses two independently implemented full-bin evaluators.
Every marginal and paired interval, including failed or adverse comparisons,
is retained. The zero-investment reference is not a strong conventional optimizer.

## Verification

With the repository numerical and LaTeX dependencies, run from the repository root:

    python3 revisions/2026-10-11-r77/code/build77.py --full

The publication build replays both new evaluators and the exact confidence
intervals, not the original scientific clocks. The archive includes all transitive
numerical sources and test data. Compiled PDFs and visual inspection have separate
hash-bound records. audit/FINAL_DELIVERY77.json is created only for a completed
publication; a source branch alone is not proof that its release checks passed.

Conditional economic prices are not an empirical currency calibration; finite
matched comparisons do not establish universal neural or long-horizon superiority.
''')
    print(json.dumps(dict(status='ordinary_sources_assembled',inherited_sections=len(inherited),evidence_files=len(evidence),companions=len(companions),abstract_words=len(ABSTRACT.split()))))
if __name__=='__main__':main()
