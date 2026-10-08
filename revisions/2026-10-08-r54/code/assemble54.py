"""Materialize an ordinary R54 manuscript from immutable R53 inputs.

Only the new revision is modified. Scientific sources, records and complete
historical editions are retained; this is not a new experimental execution.
"""
from pathlib import Path
import difflib,hashlib,json,re,shutil
R=Path(__file__).resolve().parents[1]
OLD=R.parent/'2026-10-08-r53'
ABSTRACT=r'''This paper develops Neural Bellman Operators for policy evaluation and feasible improvement in controlled economies. A constructive continuation retains feasible action witnesses and admits policy-identical native and affine--ReLU realizations. Acquired-state feasibility and verified continuation contrasts connect numerical approximation to the cost of the implemented policy. We prove a directed finite-sweep bound that preserves the incumbent at every state and reaches the original Bellman optimum under exact greedy certificates. Signed residual transport makes the comparison computable without a policy-value oracle; explicit work and storage bounds expose its state-cover and horizon dependence. In the original nonlinear investment economy, complete two- and three-date sweeps are evaluated by independent continuous-law cost intervals. A genuinely nonuniform conventional comparator and a controlled approximately-null perturbation catalogue examine representation and verification choices. Own-incumbent gains are identified, while cross-method differences and complete catalogue work are reported without presuming neural dominance. All earlier theory, applications and adverse evidence remain available in the complete development editions.'''
BRIDGE=r'''\paragraph{From continuation construction to a complete improved policy.}
The current contribution completes a chain within the same NBO model. The constructive backend supplies a feasible acquired incumbent; verified signed differences compare that incumbent with implementable proposals; continuous-action covers give a bound against the original feasible infimum; and independent cost intervals evaluate the full policy returned after each pass. Section~\ref{sec:directed54} proves the directed recursion and supplies a streamed, common-innovation realization with explicit resource bounds. Section~\ref{sec:study54} executes all dates for the full horizon, not merely the last decision. The earlier final-date and exact-null experiments remain distinct observations rather than being relabeled as full-sweep evidence.

The empirical ordering starts from actual expected policy cost. A complete-catalogue work account includes primitive construction, all executed improvement passes, durable records and the shared cost-inference service. It is an observed cost of returning a policy from a finite catalogue, not an estimate of an unexecuted optimal stopping strategy. Own-incumbent improvement, conventional-method comparison and the robustness of a certificate are reported separately.
'''
LITERATURE=r'''\paragraph{Policy iteration, invariance, and state metrics.}
Approximate policy iteration already has a substantial error-propagation theory; \citet{munos2003} studies approximation errors in policy iteration. Conservative policy iteration connects improvement to an incumbent and a performance criterion \citep{kakade2002}, and safe policy iteration develops related monotonic-improvement guarantees \citep{pirottasafe2013}. We do not claim the general idea of safe improvement. Our finite-horizon statement requires an acquired-cell feasible action, a verified directed advantage enclosure, and a lower cover of the entire continuous feasible action set. Those conditions identify the error that enters each pass and make the economic cost of verification explicit.

Couplings also occur in bisimulation metrics: \citet{ferns2004} relate state distances to optimal values. Here the transported object is the signed evaluation error of a fixed incumbent, and the pair computation may use any verified coupling with the correct marginals. It is neither a proposed state-aggregation metric nor an assumption that a transport optimum can be obtained without cost. Potential-based reward shaping preserves policies by transforming the reward specification \citep{ng1999}; the action-null construction here leaves the economic reward and transition laws unchanged and concerns continuation components with identical feasible-action expectations. Value equivalence instead identifies models through their Bellman updates on specified functions and policies \citep{grimm2020}. Our contrast equivalence is a statement about continuation errors under the fixed actual kernels. These connections explain the inherited principles and locate the additional contribution in implementable certification, finite-sweep accuracy and complete policy-cost accounting.
'''
CONCLUSION=r'''\paragraph{Full-horizon execution and adoption.}
The new full-sweep calculation changes nonterminal as well as terminal decisions while retaining exact incumbents whenever the whole-cell comparison is inconclusive. Its directed recursion, continuous-action lower covers, and positive contrast bounds are evaluated in the original nonlinear two-state economy. The cost intervals identify cumulative gains for the witness incumbent after complete sweeps. They do not identify a uniform advantage over conventional policies; the adaptive and tensor comparators receive the same improvement and inference treatment. The recorded gain intervals determine the entire range of replacement fees supported by the experiment, in the normalized units of the model.

The paired recursion avoids storing a full state-pair table, but its demonstrated implementation still uses a tensor observation cover and has explicit horizon dependence. The nonuniform conventional experiment is not a non-tensor high-dimensional experiment. These distinctions leave the original NBO research objective intact while keeping each mathematical and empirical assertion tied to its actual assumptions and evidence.
'''
REFS=[
('munos2003','Munos(2003)',r'\textsc{Munos, R.} (2003): ``Error Bounds for Approximate Policy Iteration,'' in \emph{Proceedings of the Twentieth International Conference on Machine Learning}, 560--567.','Remi Munos','Error Bounds for Approximate Policy Iteration','Proceedings of the Twentieth International Conference on Machine Learning','2003','560--567'),
('kakade2002','Kakade and Langford(2002)',r'\textsc{Kakade, S., and J. Langford} (2002): ``Approximately Optimal Approximate Reinforcement Learning,'' in \emph{Proceedings of the Nineteenth International Conference on Machine Learning}, 267--274.','Sham Kakade and John Langford','Approximately Optimal Approximate Reinforcement Learning','Proceedings of the Nineteenth International Conference on Machine Learning','2002','267--274'),
('ferns2004','Ferns, Panangaden, and Precup(2004)',r'\textsc{Ferns, N., P. Panangaden, and D. Precup} (2004): ``Metrics for Finite Markov Decision Processes,'' in \emph{Proceedings of the Twentieth Conference on Uncertainty in Artificial Intelligence}, 162--169.','Norman Ferns and Prakash Panangaden and Doina Precup','Metrics for Finite Markov Decision Processes','Proceedings of the Twentieth Conference on Uncertainty in Artificial Intelligence','2004','162--169'),
('ng1999','Ng, Harada, and Russell(1999)',r'\textsc{Ng, A. Y., D. Harada, and S. Russell} (1999): ``Policy Invariance under Reward Transformations: Theory and Application to Reward Shaping,'' in \emph{Proceedings of the Sixteenth International Conference on Machine Learning}, 278--287.','Andrew Y. Ng and Daishi Harada and Stuart Russell','Policy Invariance under Reward Transformations: Theory and Application to Reward Shaping','Proceedings of the Sixteenth International Conference on Machine Learning','1999','278--287'),
('grimm2020','Grimm, Barreto, Singh, and Silver(2020)',r'\textsc{Grimm, C., A. Barreto, S. Singh, and D. Silver} (2020): ``The Value Equivalence Principle for Model-Based Reinforcement Learning,'' in \emph{Advances in Neural Information Processing Systems}, 33.','Christopher Grimm and Andre Barreto and Satinder Singh and David Silver','The Value Equivalence Principle for Model-Based Reinforcement Learning','Advances in Neural Information Processing Systems','2020',''),
('pirottasafe2013','Pirotta, Restelli, Pecorino, and Calandriello(2013)',r'\textsc{Pirotta, M., M. Restelli, A. Pecorino, and D. Calandriello} (2013): ``Safe Policy Iteration,'' in \emph{Proceedings of the Thirtieth International Conference on Machine Learning}, 28, 307--315.','Matteo Pirotta and Marcello Restelli and Alessio Pecorino and Daniele Calandriello','Safe Policy Iteration','Proceedings of the Thirtieth International Conference on Machine Learning','2013','307--315')]

def digest(f):
    with f.open('rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()
def put(f,text):f.parent.mkdir(parents=True,exist_ok=True);f.write_text(text)
def expanded(root,file,seen=None):
    seen=set() if seen is None else seen;file=file.resolve()
    if file in seen:return ''
    seen.add(file);text=file.read_text()
    def sub(m):
        p=root/(m[1]+('' if m[1].endswith('.tex') else '.tex'))
        return expanded(root,p,seen) if p.exists() else m[0]
    return re.sub(r'\\input\{([^}]+)\}',sub,text)
def main():
    marker=R/'audit/ASSEMBLY54.json'
    if marker.exists():
        print('R54 ordinary sources already assembled; refusing to overwrite author edits.');return
    if not OLD.exists():raise FileNotFoundError(OLD)
    own={str(f.relative_to(R)):f.read_bytes() for f in R.rglob('*') if f.is_file()}
    shutil.copytree(OLD,R,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    for name,data in own.items():
        target=R/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    preserved=R/'preserved/R53-unintegrated';preserved.mkdir(parents=True,exist_ok=True)
    for n in ('ECTA.tex','supp.tex','complete.tex','complete-supp.tex','response.md','README.md'):
        shutil.copy2(OLD/n,preserved/n)
    if (R/'build').exists():shutil.rmtree(R/'build')
    (R/'build').mkdir();(R/'audit').mkdir(exist_ok=True)
    baseline_labels={n:sorted(set(re.findall(r'\\label\{([^}]+)\}',expanded(OLD,OLD/(n+'.tex'))))) for n in ('ECTA','supp','complete','complete-supp')}
    for n in ('ECTA','complete'):
        file=R/(n+'.tex');text=file.read_text()
        needle=r'\input{sections/action_contrast52}'
        if needle not in text:raise AssertionError(('Missing contrast section',n))
        text=text.replace(needle,needle+'\n'+r'\input{sections/directed54}',1)
        needle=r'\input{sections/study52}'
        if needle not in text:raise AssertionError(('Missing study section',n))
        text=text.replace(needle,needle+'\n'+r'\input{sections/study54}',1)
        text=text.replace('active R52 exposition','active R54 exposition').replace('current R52 argument','current R54 argument')
        if n=='ECTA':
            text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+ABSTRACT+'\n'+m[2],text,count=1,flags=re.S)
            needle=r'\input{sections/core49}';text=text.replace(needle,BRIDGE+'\n'+LITERATURE+'\n'+needle,1)
            needle=r'\appendix';text=text.replace(needle,CONCLUSION+'\n'+needle,1)
        else:
            needle=r'\section*{Reading notice for the complete development edition}'
            text=text.replace(needle,needle+'\n'+r'The current additions are the directed full-sweep certificate and the complete policy-cost study. The historical body remains available without deleting its results or applications.'+'\n',1)
        put(file,text)
    for n in ('supp','complete-supp'):
        file=R/(n+'.tex');text=file.read_text()
        text=text.replace('and the R52 revision','and the R54 revision').replace('current R52 argument','current R54 argument')
        needle=r'\bibliographystyle{ecta-fullname}'
        if needle not in text:raise AssertionError(('Missing bibliography',n))
        text=text.replace(needle,r'\input{sections/supp54}'+'\n'+needle,1)
        put(file,text)
    put(R/'response.md',(R/'response54.md').read_text())
    entries_file=R/'publication/bibliography-entries.json';entries=json.loads(entries_file.read_text())
    bib=(R/'references.bib').read_text()
    for key,auth,body,names,title,venue,year,pages in REFS:
        entries[key]=r'\bibitem['+auth+']{'+key+'}\n'+body
        if not re.search(r'@\w+\s*\{\s*'+re.escape(key)+r'\s*,',bib):
            bib+='\n@inproceedings{'+key+',\n author={'+names+'},\n title={'+title+'},\n booktitle={'+venue+'},\n year={'+year+'},\n pages={'+pages+'}\n}\n'
    put(entries_file,json.dumps(entries,indent=2,sort_keys=True)+'\n');put(R/'references.bib',bib)
    retained={}
    for folder in ('results53','results53-extension','results','results52','evidence','inputs','preserved'):
        if not (OLD/folder).exists():continue
        for f in (OLD/folder).rglob('*'):
            if f.is_file() and '__pycache__' not in f.parts:
                name=str(f.relative_to(OLD));need=R/name
                if not need.exists() or digest(need)!=digest(f):raise AssertionError('Inherited bytes changed: '+name)
                retained[name]=digest(f)
    # Frozen files are also checked by study53.verify_freeze and extend53.verify.
    record=dict(baseline_commit='de82bbe365b1b2124ab2edcab7d9237182f51617',
        controlling_review_commit='8e811efb4e1b2e9d588472bce1d35bb93eaaf23a',
        baseline_labels=baseline_labels,retained_sha256=retained,
        scientific_services_reexecuted=False,old_branches_modified=False,
        source_revision='R54 integrates the original paper and already executed, separately frozen R53 studies')
    put(marker,json.dumps(record,indent=2,sort_keys=True)+'\n')
    for n in ('ECTA','supp','complete','complete-supp'):
        put(R/'audit'/(n+'-R52-to-R54.diff'),''.join(difflib.unified_diff((OLD/(n+'.tex')).read_text().splitlines(True),(R/(n+'.tex')).read_text().splitlines(True),fromfile='R52-unintegrated/'+n+'.tex',tofile='R54/'+n+'.tex')))
    put(R/'README.md',r'''# Neural Bellman Operators — R54 referee revision

The title, model and research program are unchanged. This revision responds to
all ten major comments of the pinned R52 advisory report and integrates the
subsequent, separately frozen R53 full-sweep and perturbation records.

## Reading order

[Main article](build/ECTA.pdf), [technical supplement](build/supp.pdf), and
[point-by-point response](build/response.pdf) form the active submission.
The [complete development article](build/complete.pdf) and
[complete proof supplement](build/complete-supp.pdf) preserve the broader theory,
applications and adverse numerical evidence. Ordinary sources are ECTA.tex,
supp.tex, complete.tex, complete-supp.tex and response.md in this directory.

The directed certificate and its proofs are in sections/directed54.tex.
All-date policy costs and work are in sections/study54.tex and tables/*54.tex.
The machine-readable audit is audit/RESULT_AUDIT54.json; the publication and
preservation record is audit/RELEASE54.json. FINAL_DELIVERY54.json binds the
final files after the clean-archive rebuild. Its existence is required before
this directory is described as a completed publication.

## Reproduction

Install Python 3 with numpy and scipy, pandoc, poppler-utils, and the LaTeX
packages used by econsocart (latex-extra, fonts-recommended, science on Ubuntu).
From the repository root, run:

    python3 revisions/2026-10-08-r54/code/build54.py

The build uses ordinary committed sources and frozen records without network,
training, new simulation, or service retiming. It reconstructs tables and
replays every saved decision and cost interval. Primitive enclosure identities
are exercised by exact and numerical tests; stored-endpoint replay is not
misdescribed as independently integrating every economic kernel again.

## Evidentiary scope

Full sweeps concern the original continuous-law two-state nonlinear economy,
with horizons two and three. The adaptive comparator is nonuniform, not
non-tensor. The 384 controlled perturbation cases are deterministic diagnostics,
not independent policy-cost observations. The observed complete-catalogue work
account is not a minimum-work sequential stopping frontier. No unexecuted
high-dimensional comparison, learned-null discovery result, empirical fee
calibration, or representation-specific superiority is claimed.
''')
    print(json.dumps(dict(ordinary_sources='assembled',retained_files=len(retained),baseline_labels={k:len(v) for k,v in baseline_labels.items()})))
if __name__=='__main__':main()
