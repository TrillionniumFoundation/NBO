"""Integrate the ordinary R73 manuscript without changing inherited sections.

The scientific source and data are already committed. This preparer supplies
editable publication sources and a byte-level reading-set preservation map.
It neither fits a model nor regenerates a scientific service.
"""
from pathlib import Path
import hashlib,json,re,shutil
R=Path(__file__).resolve().parents[1]
OLD=R.parent/'2026-10-11-r72'
DOCS=('ECTA','supp','appendix')
ABSTRACT='''This paper develops Neural Bellman Operators for constructive policy evaluation and feasible improvement. A witness-preserving continuation connects approximation resources to the original economic optimum. Verified comparisons permit trainable proposals without assuming successful unrestricted neural optimization. We prove that a frozen fitted continuation supplies original-law cost observations whose range is controlled by residual oscillation, and construct qualification-optimal fixed-feature readouts with exact primal--dual certificates. Conditional ReLU moments make their evaluation nonrecursive. A predictable cost certificate remains valid under optional stopping and distinguishes fixed-controller costs from adaptive conditional averages. Capacity-repaired witness transport supports paid computational reuse. Matched backward constructions in the nonlinear investment economy qualify actual fitted continuations; the retained scalar and two-control studies separately assess training, deployment and policy-cost equivalence. Complete proofs, economic cost accounts and all prior adverse evidence are retained.'''
ADDITION=r'''\paragraph{Fitting for the economic qualification.}
The continuation's attained fitting criterion should control a quantity that enters the policy decision. Section~\ref{sec:qualification73} minimizes a verified residual-oscillation bound over a fixed feature class, conditional on its actual fitted future. A finite linear program proposes the readout; an exact primal--dual calculation certifies its achieved objective gap. Backward construction links those attained bounds to original-optimum regret and to the range of the original-law cost observation. The matched ReLU and conventional constructions below execute this chain, including continuous-action coverage and whole-cell feasibility. They do not replace a verified uniform bound by a sampled training loss.

A second decision concerns when enough qualification has been purchased. Section~\ref{sec:sequential73} permits predictable continuations and range qualifications and remains valid when a cost comparison is stopped after inspection. It distinguishes repeated qualification of a fixed complete controller from the conditional average cost of changing controllers. Failed numerical evaluations consume their prequalified support and actual work instead of disappearing from the sample. The adoption account then prices qualification and replacement without treating processor seconds as money or the sample count as the deployment horizon.

'''
LITERATURE=r'''Time-uniform concentration through nonnegative supermartingales is established \citep{howard2020time}; off-policy confidence sequences have been developed for contextual-bandit evaluation \citep{karampatziakis2021}. We use those principles rather than claim them as new. Our observations are directly simulated original-law NBO contrasts, enclosed over continuous innovation cells and bounded by a qualified fitted continuation. The readout dual and the predictable support construction identify the numerical and economic objects to which optional stopping applies.

'''
READING=r'''\paragraph{Reading path.}
Sections~\ref{sec:core49}--\ref{sec:query63} give the original constructive operator, investment primitives and recursive guarantee. Sections~\ref{sec:operational67}--\ref{sec:vector67} state the operational readout and two-control certificates. Sections~\ref{sec:frozen72}--\ref{sec:sequential73} develop fitted-continuation evaluation, qualification-optimal readouts and sequential cost certification. Section~\ref{sec:reuse72} retains paid-witness transport and Section~\ref{sec:study72} reports the evidence. The Technical Supplement includes optimal-advantage centering and all complete proofs. The Numerical and Development Appendix retains the preceding economic, localization, deployment and empirical sections unchanged, and adds the detailed qualification records. Original broader applications and the preceding complete editions remain companions under their stated hypotheses.

'''
CONCLUSION=r'''The qualification-optimal readout gives a direct link from an attained fitting objective to a uniform NBO cost and regret certificate. Its exact dual distinguishes verified optimization accuracy from a solver's status. Predictable original-law cost intervals allow qualification to stop when a declared economic criterion is met, while keeping fixed-policy and adaptive-deployment targets separate. Both additions use the original investment primitives and pay for approximation, uniform qualification and numerical evaluation; neither infers a population ranking from a better training objective.

'''
REFS={
'howard2020time':r'''\bibitem[Howard, Ramdas, McAuliffe, and Sekhon(2020)]{howard2020time}
\textsc{Howard, Steven R., Aaditya Ramdas, Jon McAuliffe, and Jasjeet Sekhon} (2020): \enquote{Time-Uniform Chernoff Bounds via Nonnegative Supermartingales,} \emph{Probability Surveys}, 17, 257--317.''',
'karampatziakis2021':r'''\bibitem[Karampatziakis, Mineiro, and Ramdas(2021)]{karampatziakis2021}
\textsc{Karampatziakis, Nikos, Paul Mineiro, and Aaditya Ramdas} (2021): \enquote{Off-Policy Confidence Sequences,} in \emph{Proceedings of the 38th International Conference on Machine Learning}, vol.~139 of \emph{Proceedings of Machine Learning Research}, 5301--5310.'''}
BIB=r'''
@article{howard2020time,
 author={Steven R. Howard and Aaditya Ramdas and Jon McAuliffe and Jasjeet Sekhon},
 title={Time-Uniform Chernoff Bounds via Nonnegative Supermartingales},
 journal={Probability Surveys}, year={2020}, volume={17}, pages={257--317}, doi={10.1214/18-PS321}}
@inproceedings{karampatziakis2021,
 author={Nikos Karampatziakis and Paul Mineiro and Aaditya Ramdas},
 title={Off-Policy Confidence Sequences}, year={2021},
 booktitle={Proceedings of the 38th International Conference on Machine Learning},
 series={Proceedings of Machine Learning Research}, volume={139}, pages={5301--5310}}
'''

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
    marker=R/'audit/PREPARATION73.json'
    if marker.exists():print('R73 ordinary sources already prepared; author edits retained.');return
    if not (R/'SOURCE_FREEZE73.json').exists():raise RuntimeError('Scientific source freeze must precede publication preparation')
    preserved=R/'preserved/R72-original';preserved.mkdir(parents=True,exist_ok=True)
    for name in ('ECTA.tex','supp.tex','appendix.tex','response.md','README.md','CONTENT_MAP72.md'):
        shutil.copy2(OLD/name,preserved/name)
    paths=sorted(set(p for doc in DOCS for p in re.findall(r'\\input\{(sections/[^}]+)\}',(OLD/(doc+'.tex')).read_text())))
    sections={p+'.tex':sha(OLD/(p+'.tex')) for p in paths}
    for path,h in sections.items():
        if sha(R/path)!=h:raise AssertionError('Inherited scientific exposition modified: '+path)
    text=(OLD/'ECTA.tex').read_text()
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+ABSTRACT+'\n'+m[2],text,flags=re.S,count=1)
    text=text.replace(r'\paragraph{Relation to existing methods.}',ADDITION+r'\paragraph{Relation to existing methods.}',1)
    start=text.index(r'\paragraph{Reading path.}');end=text.index(r'\input{sections/core49}',start)
    text=text[:start]+LITERATURE+READING+text[end:]
    text=text.replace('\\input{sections/centered69}\n','')
    text=text.replace(r'\input{sections/frozen72}',r'\input{sections/frozen72}'+'\n'+r'\input{sections/qualification73}'+'\n'+r'\input{sections/sequential73}')
    text=text.replace(r'\input{sections/study72}',r'\input{sections/study72}'+'\n'+r'\input{sections/study73}')
    text=text.replace(r'\bibliographystyle{ecta-fullname}',CONCLUSION+r'\bibliographystyle{ecta-fullname}')
    (R/'ECTA.tex').write_text(text.replace('label=e72ECTA','label=e73ECTA'))
    text=(OLD/'supp.tex').read_text().replace('label=e72supp','label=e73supp')
    text=text.replace(r'\input{sections/proofs67}',r'\input{sections/centered69}'+'\n'+r'\input{sections/proofs67}')
    text=text.replace(r'\bibliographystyle{ecta-fullname}',r'\input{sections/proofs73}'+'\n'+r'\bibliographystyle{ecta-fullname}')
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\nThis supplement retains optimal-advantage centering and every preceding complete proof. It adds the qualification-readout primal and dual, the original investment cover and actor calculations, and the predictable original-law cost and optional-stopping proofs. Detailed scientific records and historical economic sections remain in the Numerical and Development Appendix.\n'+m[2],text,flags=re.S,count=1)
    (R/'supp.tex').write_text(text)
    text=(OLD/'appendix.tex').read_text().replace('label=e72appendix','label=e73appendix')
    text=text.replace(r'\bibliographystyle{ecta-fullname}',r'\input{sections/audit73}'+'\n'+r'\bibliographystyle{ecta-fullname}')
    (R/'appendix.tex').write_text(text)
    shutil.copy2(R/'response73.md',R/'response.md')
    entries_path=R/'publication/bibliography-entries.json';entries=json.loads(entries_path.read_text());entries.update(REFS);save(entries_path,entries)
    bib=R/'references.bib';bib.write_text(bib.read_text()+BIB)
    labels={doc:sorted(set(re.findall(r'\\label\{([^}]+)\}',(OLD/(doc+'.tex')).read_text()))) for doc in DOCS}
    record=dict(base_commit='5611b32978a2df5f32bff796f7dd209105cf28b0',review_commit='4b27b56f4514f6c1d77b69fe707f7202f8b06b19',
                inherited_sections=sections,wrapper_labels=labels,original_wrapper_sha256={p.name:sha(p) for p in preserved.iterdir() if p.is_file()},
                scope='All R72 active section files retained byte-identically and compiled once; original wrappers and response retained; no scientific reruns')
    save(marker,record)
    rows=['# R73 content-preservation map','', 'Original NBO title, author, model and broader companion editions are retained.',
          'The preceding optimal-advantage section moves intact into the supplement.', '', '| Original section | Current document | SHA256 |','|---|---|---|']
    for path,h in sections.items():
        target=[doc for doc in DOCS if ('\\input{'+path[:-4]+'}') in (R/(doc+'.tex')).read_text()]
        if len(target)!=1:raise AssertionError(('Missing/duplicate original section',path,target))
        rows.append('| `'+path+'` | '+target[0]+' | `'+h+'` |')
    (R/'CONTENT_MAP73.md').write_text('\n'.join(rows)+'\n')
    print(json.dumps({'status':'prepared','unchanged_sections':len(sections),'abstract_words':len(ABSTRACT.split())},indent=2))
if __name__=='__main__':main()
