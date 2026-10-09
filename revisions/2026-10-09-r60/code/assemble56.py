"""Integrate the original NBO paper and preserved R55 evidence into R56.

An ordinary manuscript and four complete/historical companions are committed
before verification. No scientific source or prior revision is modified.
"""
from pathlib import Path
import hashlib,json,re,shutil
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-09-r55'
ABSTRACT=r'''This paper develops Neural Bellman Operators that construct continuations from their own fitted futures and return feasible economic policies. A constructive backend gives a primitive error account against the Bellman optimum and retains original action witnesses through exact neural compilation. For trained ReLU continuations, analytic innovation integration reduces scalar investment search to finitely many algebraic action witnesses. Directed whole-cell certificates protect a complete incumbent policy and propagate full-action errors through finite sweeps. A non-tensor residual cache and signed sensitivity of a smooth installed reference make verification executable without a full state-pair table or exponential shock-path enumeration. A prospective stopping theorem connects the returned policy to an expected-cost target, and a sample-split confidence box qualifies learned approximately null structure. In the original nonlinear investment family, a separately frozen sensitivity extension attains two- and ten-percent cost-reduction targets in all declared two-, four- and eight-dimensional services. All construction, verification and own inference are charged. Policy identities and comparative work separate the trained neural construction from benefits supplied by common verification; no uniform neural ranking is inferred.'''
CONCLUSION=r'''\section{Conclusion}\label{sec:conclusion56}
Neural Bellman Operators connect an own-future continuation to a feasible action and an economic cost account. The constructive backend retains the original Bellman-accuracy objective. The trained backend now has analytic innovation integration and a terminating exact action-lattice search, while its proposals remain subject to whole-cell true-advantage verification. These are complementary parts of the same numerical method, not interchangeable claims about the name of a function class.

The non-tensor cache and signed reference calculation turn the policy account into an executable prospective service. Their proofs retain the cost of leaf membership, critic evaluation, state dimension and horizon. The declared expected-cost targets are attained in the sensitivity experiment, with genuine nonterminal action changes and complete own-service clocks. Conventional generators share the same verification treatment, and policy identities make their role observable. The finite experiments identify successful returns and their costs; they do not establish universal neural dominance or calibrated welfare effects.

The full-action gap, the actual expected cost and the price of acquiring or verifying a policy remain separate economic quantities. Keeping all three explicit permits a decision maker to choose the appropriate contract without treating fitting accuracy, certificate sharpness or a favorable timing observation as a substitute for the cost of the implemented policy.

\appendix
\section{Development and reproducibility map}\label{sec:map56}
The complete development article and proof companion preserve every preceding theorem, economic application and numerical comparison, including adverse results. The prior active article and supplement are also retained as separate development documents. The present main article reorganizes the original constructive core around trained action witnesses, non-tensor verification and prospective economic stopping; it does not replace the NBO subject with a different model.

The publication audit regenerates all unique recorded certificates from their saved fitted critics, replays all stopping decisions and verifies original moment bounds against exact rational sample moments. New solver regressions compare rational action witnesses with exhaustive lattice minimization. These operations do not create new policy-cost samples or replace historical service clocks. The source freezes, ordinary manuscript sources, complete service registry, raw arrays, response and release manifests are included in the revision directory. Mathematical peer review remains distinct from executable regression and document reproduction.
'''
REFS={
'munos2008':r'\bibitem[Munos and Szepesv\'{a}ri(2008)]{munos2008}'+'\n'+r'\textsc{Munos, R\'{e}mi, and Csaba Szepesv\'{a}ri} (2008): \enquote{Finite-Time Bounds for Fitted Value Iteration,} \emph{Journal of Machine Learning Research}, 9 (27), 815--857.',
'hoeffding1963':r'\bibitem[Hoeffding(1963)]{hoeffding1963}'+'\n'+r'\textsc{Hoeffding, Wassily} (1963): \enquote{Probability Inequalities for Sums of Bounded Random Variables,} \emph{Journal of the American Statistical Association}, 58 (301), 13--30.'}
BIB=r'''
@article{munos2008,
 author={R{\'e}mi Munos and Csaba Szepesv{\'a}ri},
 title={Finite-Time Bounds for Fitted Value Iteration},
 journal={Journal of Machine Learning Research},year={2008},volume={9},number={27},pages={815--857}}
@article{hoeffding1963,
 author={Wassily Hoeffding},title={Probability Inequalities for Sums of Bounded Random Variables},
 journal={Journal of the American Statistical Association},year={1963},volume={58},number={301},pages={13--30},doi={10.1080/01621459.1963.10500830}}
'''
def digest(f):
    with f.open('rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()
def put(f,t):f.parent.mkdir(parents=True,exist_ok=True);f.write_text(t)
def expanded(root,file,seen=None):
    seen=set() if seen is None else seen;file=file.resolve()
    if file in seen:return ''
    seen.add(file);text=file.read_text()
    def sub(m):
        p=root/(m[1]+('' if m[1].endswith('.tex') else '.tex'))
        return expanded(root,p,seen) if p.exists() else m[0]
    return re.sub(r'\\input\{([^}]+)\}',sub,text)
def labels(root,name):return sorted(set(re.findall(r'\\label\{([^}]+)\}',expanded(root,root/(name+'.tex')))))
def git_tree(path):
    def obj(kind,data):return hashlib.sha1(kind+b' '+str(len(data)).encode()+b'\0'+data).digest()
    entries=[]
    for f in path.iterdir():
        if f.name=='__pycache__':continue
        directory=f.is_dir();data=git_tree(f) if directory else obj(b'blob',f.read_bytes())
        entries.append((f.name+('/' if directory else ''),b'40000' if directory else b'100644',f.name,data))
    entries.sort(key=lambda z:z[0].encode())
    return obj(b'tree',b''.join(mode+b' '+name.encode()+b'\0'+data for _,mode,name,data in entries))

def main():
    marker=R/'audit/ASSEMBLY56.json'
    if marker.exists():print('Ordinary R56 manuscript already assembled; existing edits retained.');return
    if not OLD.exists():raise FileNotFoundError(OLD)
    pinned=git_tree(OLD).hex()
    if pinned!='7ab1ccc3b81d9b393b494fe13a6aeb6f6a1436ce':raise AssertionError('Pinned R55 revision tree differs: '+pinned)
    own={str(p.relative_to(R)):p.read_bytes() for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    shutil.copytree(OLD,R,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    for name,data in own.items():
        p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    put(R/'sections/resources56.tex',(OLD/'sections/resources49.tex').read_text().replace(r'\ref{sec:study49}',r'\ref{sec:legacy56}'))
    file=R/'sections/certificates56.tex';text=file.read_text()
    for before,after in [
        ('only nonzero state derivatives','only state derivatives'),
        ('$O(r)$ state boxes and $O(Ndr)$','$O(Nr)$ state rows and $O(Ndr)$'),
        ('across all current dates','across current dates'),
        ('it does not remove that a fixed 32-leaf partition becomes very coarse as dimensional economic complexity grows.','it does not prove that a fixed 32-leaf partition resolves every eight-dimensional economic policy.'),
        ('let $C(C)$ be the greater of $L(C)$ and the minimum of the lower endpoints','let $C_t(C)$ be the greater of $L_t(C)$ and the minimum of their lower endpoints')]:text=text.replace(before,after)
    put(file,text)
    backup=R/'preserved/R54-before-R56';backup.mkdir(parents=True,exist_ok=True)
    for name in ('ECTA.tex','supp.tex','complete.tex','complete-supp.tex','response.md','README.md','references.bib'):
        shutil.copyfile(OLD/name,backup/name)
    put(R/'development.tex',(OLD/'ECTA.tex').read_text())
    text=(OLD/'supp.tex').read_text().replace(r'{build/ECTA}[ECTA.pdf]',r'{build/development}[development.pdf]')
    put(R/'development-supp.tex',text)
    header=(OLD/'ECTA.tex').read_text().split(r'\section{Introduction}')[0]
    header=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+ABSTRACT+'\n'+m[2],header,count=1,flags=re.S)
    body='\n'.join(r'\input{sections/'+s+'}' for s in ('intro56','core49','resources56','primitives56','learned56','certificates56','decisions49','prospective56','study56'))
    tail='\n'+CONCLUSION+'\n'+r'\bibliographystyle{ecta-fullname}'+'\n'+r'\bibliography{references}'+'\n'+r'\end{document}'+'\n'
    put(R/'ECTA.tex',header+body+tail)
    supp=(OLD/'supp.tex').read_text().split(r'\section{Primitive domain')[0]
    supp=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'This supplement records the complete prospective-service registry, numerical semantics, confidence intervals, datewise error accounts and source-preservation map for Neural Bellman Operators. The active mathematical statements are proved in the article; all preceding proofs and applications remain in the complete companions.'+m[2],supp,count=1,flags=re.S)
    put(R/'supp.tex',supp+r'\input{sections/supp56}'+'\n'+r'\bibliographystyle{ecta-fullname}'+'\n'+r'\bibliography{references}'+'\n'+r'\end{document}'+'\n')
    for name in ('complete','complete-supp'):
        text=(OLD/(name+'.tex')).read_text()
        note='\n'+r'\section*{Current reading map}'+'\nThe active R56 article is the current exposition of Neural Bellman Operators. This companion preserves the preceding body and adds the current results without deleting its earlier assumptions, proofs, applications or adverse observations. Historical uses of the word current below identify their own editions.\n'
        text=text.replace(r'\end{frontmatter}',r'\end{frontmatter}'+note,1)
        additions=('primitives56','learned56','certificates56','prospective56','study56') if name=='complete' else ('supp56',)
        insertion='\n'.join(r'\input{sections/'+s+'}' for s in additions)+'\n'
        text=text.replace(r'\bibliographystyle{ecta-fullname}',insertion+r'\bibliographystyle{ecta-fullname}',1)
        if name=='complete-supp':text=text.replace(r'{build/complete}[ECTA.pdf]',r'{build/complete}[complete.pdf]')
        put(R/(name+'.tex'),text)
    put(R/'response.md',(R/'response56.md').read_text())
    entries=R/'publication/bibliography-entries.json';j=json.loads(entries.read_text());j.update(REFS);put(entries,json.dumps(j,indent=2,sort_keys=True)+'\n')
    put(R/'references.bib',(OLD/'references.bib').read_text()+BIB)
    mapping={'ECTA':'development','supp':'development-supp','complete':'complete','complete-supp':'complete-supp'}
    before={out:labels(OLD,old) for old,out in mapping.items()}
    retained={}
    for folder in ('sections','code','inputs','evidence','results','results52','results53','results53-extension','results55','results55-tube','attempts','preserved'):
        for p in (OLD/folder).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:
                name=str(p.relative_to(OLD));h=digest(p)
                if not (R/name).exists() or digest(R/name)!=h:raise AssertionError('Inherited source or evidence changed: '+name)
                retained[name]=h
    j=dict(baseline_commit='7f4de488134e93b6cfb5dd95a3e6d7e14b45ac2a',controlling_review_commit='adf1256cff9cde365246a3db2dac90c72fda3b13',prior_manuscript_commit='00e837adb431f4d4b5248fc6d5ff1fc927dd3b65',baseline_tree=pinned,baseline_git_tree_identity_verified=True,baseline_labels=before,retained_sha256=retained,old_revisions_modified=False,new_scientific_services=0,reading_map=mapping)
    put(marker,json.dumps(j,indent=2,sort_keys=True)+'\n')
    put(R/'README.md',r'''# Neural Bellman Operators — R56

Active submission: [main article](build/ECTA.pdf), [technical supplement](build/supp.pdf), and [point-by-point response](build/response.pdf).

Full prior content is retained in [complete development](build/complete.pdf), [complete proofs](build/complete-supp.pdf), [previous active article](build/development.pdf), and [previous active supplement](build/development-supp.pdf). The title, economic model and original constructive Bellman-accuracy target remain unchanged.

New theory includes analytic fitted-neural integration and exact lattice action witnesses, non-tensor residual caches, signed smooth-reference sensitivity with explicit work bounds, prospective economic stopping, and validation-qualified learned structure. Existing R55 primary and sensitivity executions are integrated without new samples, retraining or rewritten service clocks.

The publication audit re-evaluates 33 unique certificates from saved fitted models; all 132 service decisions and stopping paths are replayed. Exact rational endpoint moments validate the stored confidence accounts across numerical-library versions. Learned exposure boxes and all 81 learned-null cases remain separate from the earlier known-perturbation catalogue. New rational action-search regressions do not license cost claims about unexecuted replacement policies.

A complete release requires `audit/FINAL_DELIVERY56.json`. The standalone offline build is:

    python3 revisions/2026-10-09-r56/code/build56.py

Dependencies: Python 3, numpy, scipy, scikit-learn, sympy, pandoc, poppler-utils, and the LaTeX packages used by econsocart. The build does not access the network or perform new training. `--publication-only` verifies the complete science binding and regenerates tables and documents; it is the explicitly scoped clean-archive document reproduction, not a second scientific execution.

All historical unfavorable comparisons and interrupted executions are retained. Same-seed timing repetitions are not independent training draws. The sampled directions concern a maintained unknown-exposure model, not an arbitrary unknown kernel. Compilation and executable tests are not an external acceptance decision.
''')
    print(json.dumps(dict(status='assembled',retained_files=len(retained),old_labels={k:len(v) for k,v in before.items()})))
if __name__=='__main__':main()
