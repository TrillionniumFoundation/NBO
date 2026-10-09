"""Add the R57 theorem and executed study to the original NBO paper.

This materializes ordinary author-editable sources; it never changes a frozen
scientific source, result, earlier revision or prior branch.
"""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,difflib
from assemble56 import labels
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-09-r56';REPO=R.parents[1]
BASE='c269f421a2938e59bd1e83bcee7218ba19a064ca'
ABSTRACT=r'''This paper develops Neural Bellman Operators that construct continuations from their own fitted futures and return feasible economic policies. A constructive backend supplies a primitive error account against the original Bellman optimum and retains action witnesses through exact neural compilation. For trained ReLU continuations, analytic innovation integration yields a terminating algebraic action search. A fitted-witness transfer theorem separates optimization, acquisition, continuation, continuous-action and verification errors, with explicit action-sensitive moduli for the learned features. Directed whole-cell adoption preserves an installed policy and connects those errors to finite-sweep accuracy. Non-tensor verification and prospective inference make the economic return executable. In the original nonlinear investment family, new separately seeded services deploy the exact neural search in two, four and eight dimensions at prespecified ten- and twenty-percent cost-reduction targets. Common-action, quadratic and tree-based controls receive the same verification treatment. Complete own-service work, candidate attribution and fresh policy-cost contrasts distinguish exact fitted optimization from demonstrated economic advantage.'''
BRIDGE=r'''The additional comparison in Section~\ref{sec:study57} executes the exact fitted action solver inside the prospective service, rather than assigning old cost observations to new policies. A nested-candidate design keeps the verifier and shared actions fixed, and genuinely different training seeds produce matched fitted objects for the menu and exact-search modes. Theorem~\ref{thm:transfer57} identifies how center optimization loss enters full-action Bellman accuracy; Proposition~\ref{prop:moduli57} supplies explicit action-sensitive acquisition and evaluation moduli. The experiment then separately asks whether the additional witness changes a certified decision and whether its returned policy has a lower actual economic cost.

'''
CONCLUSION=r'''The new action-search execution completes another part of that chain. Exact rational witnesses eliminate the stored critic's lattice optimization loss, and the transfer theorem identifies the remaining acquisition, evaluation, continuous-cover and verification obligations. The nested-candidate comparison makes a stricter certified upper endpoint attributable to an added witness under a fixed verifier. New prospective services and independent returned-policy contrasts determine the actual economic consequences. Neither exact fitted minimization nor a tighter upper endpoint is substituted for those contrasts. The complete records retain all modes, seeds, targets, attempted refinements and computational costs.

'''
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(p,text):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def main():
    marker=R/'audit/ASSEMBLY57.json'
    if marker.exists():print('Ordinary R57 manuscript already assembled; author edits retained.');return
    if not OLD.exists():raise FileNotFoundError(OLD)
    tree=subprocess.check_output(['git','rev-parse','HEAD:revisions/2026-10-09-r56'],cwd=REPO,text=True).strip()
    if tree!='1c5d76d4ac09c42f7c33e0783834a9c2ef700130':raise AssertionError('Pinned R56 source tree differs')
    before={name:labels(OLD,name) for name in ('ECTA','supp','development','development-supp','complete','complete-supp')}
    backup=R/'preserved/R56-before-R57';backup.mkdir(parents=True,exist_ok=True)
    for name in ('ECTA.tex','supp.tex','development.tex','development-supp.tex','complete.tex','complete-supp.tex','response.md','README.md','references.bib'):
        shutil.copy2(OLD/name,backup/name)
    for name in ('RELEASE56.json','RESULT_AUDIT56.json','CLEAN_REBUILD56.json','FINAL_DELIVERY56.json'):
        shutil.copy2(OLD/'audit'/name,backup/name)
    intro=(OLD/'sections/intro56.tex').read_text().replace('The economic experiment compares','The preceding prospective experiment compares')
    intro=intro.replace(r'\paragraph{Related methods.}',BRIDGE+r'\paragraph{Related methods.}',1);put(R/'sections/intro57.tex',intro)
    learned=(OLD/'sections/learned56.tex').read_text().replace('The recorded economic experiment used','The preceding R55 economic experiment used')
    learned+='\nThe new experiment in Section~\\ref{sec:study57} executes the algebraic solver in independently reconstructed prospective services. Its policies, complete work and validation streams are recorded separately from that preceding experiment.\n'
    put(R/'sections/learned57.tex',learned)
    text=(OLD/'ECTA.tex').read_text().replace('{sections/intro56}','{sections/intro57}').replace('{sections/learned56}','{sections/learned57}')
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+ABSTRACT+'\n'+m[2],text,count=1,flags=re.S)
    text=text.replace(r'\input{sections/certificates56}',r'\input{sections/certificates56}'+'\n'+r'\input{sections/action_transfer57}'+'\n'+r'\input{sections/moduli57}',1)
    text=text.replace(r'\input{sections/study56}',r'\input{sections/study56}'+'\n'+r'\input{sections/study57}',1)
    text=text.replace(r'\appendix',CONCLUSION+r'\appendix',1);put(R/'ECTA.tex',text)
    text=(OLD/'supp.tex').read_text().replace(r'\input{sections/supp56}',r'\input{sections/supp56}'+'\n'+r'\input{sections/supp57}',1);put(R/'supp.tex',text)
    for name,sections in [('complete',('action_transfer57','moduli57','study57')),('complete-supp',('supp57',))]:
        text=(OLD/(name+'.tex')).read_text()
        text=text.replace(r'\end{frontmatter}',r'\end{frontmatter}'+'\n'+r'\section*{R57 reading notice}'+'\nThe R57 active article and response are the current submission. This companion preserves all earlier statements and adds the new fitted-witness transfer and executed action-search comparison. Historical uses of current refer to their own editions.\n',1)
        insertion='\n'.join(r'\input{sections/'+s+'}' for s in sections)+'\n'
        text=text.replace(r'\bibliographystyle{ecta-fullname}',insertion+r'\bibliographystyle{ecta-fullname}',1);put(R/(name+'.tex'),text)
    file=R/'sections/study57.tex';put(file,file.read_text().replace(r'\ref{thm:prospective56}',r'\ref{thm:stop56}'))
    put(R/'response.md',(R/'response57.md').read_text())
    retained={}
    for folder in ('code','sections','inputs','evidence','results','results52','results53','results53-extension','results55','results55-tube','attempts','preserved'):
        for f in (OLD/folder).rglob('*'):
            if f.is_file() and '__pycache__' not in f.parts:
                path=str(f.relative_to(OLD));h=digest(f)
                if not (R/path).exists() or digest(R/path)!=h:raise AssertionError('Inherited source/evidence changed: '+path)
                retained[path]=h
    j=dict(baseline_commit=BASE,baseline_tree=tree,controlling_review_commit='adf1256cff9cde365246a3db2dac90c72fda3b13',baseline_labels=before,retained_sha256=retained,earlier_revision_directories_modified=False,scope='Additive ordinary-source revision; prior article, supplement, response, theory and unfavorable evidence retained; new R57 science has its own pre-execution freeze.')
    put(marker,json.dumps(j,indent=2,sort_keys=True)+'\n')
    for name in ('ECTA','supp','complete','complete-supp'):
        put(R/'audit'/(name+'-R56-to-R57.diff'),''.join(difflib.unified_diff((OLD/(name+'.tex')).read_text().splitlines(True),(R/(name+'.tex')).read_text().splitlines(True),fromfile='R56/'+name+'.tex',tofile='R57/'+name+'.tex')))
    put(R/'README.md','''# Neural Bellman Operators — R57

Active submission: [main article](build/ECTA.pdf), [technical supplement](build/supp.pdf), and [referee response](build/response.pdf). All prior theory, applications and adverse evidence remain in the four complete/development companions and `preserved/R56-before-R57`.

R57 adds a fitted-witness-to-Bellman transfer theorem, explicit action-sensitive neural moduli, and a new prospective experiment that actually deploys exact trained neural action search. Five modes, three economic tasks, three different training seeds and two targets are fixed before production. The original NBO title, economic laws, constructive backend and Bellman optimum remain unchanged.

The complete release requires `audit/FINAL_DELIVERY57.json`. The scientific execution is bound by `audit/SOURCE_FREEZE57.json` and `audit/EXECUTION57.json`; complete replay and publication are in `audit/RESULT_AUDIT57.json`, `audit/RELEASE57.json` and `audit/CLEAN_REBUILD57.json`.

Offline build from the repository root:

    python3 revisions/2026-10-09-r57/code/build57.py

Dependencies: Python 3 with numpy, scipy, scikit-learn and sympy; pandoc, poppler-utils and the LaTeX packages used by econsocart. No network, retraining or new samples are used by this build. `--publication-only` checks the full source/evidence binding and rebuilds documents; it is not a new scientific execution.

Complete target-service clocks and partial additional comparison clocks are explicitly distinguished. Different training seeds are not pure timing repetitions, and unresolved cost contrasts are not neural superiority. Numerical and publication audits are not an external editorial decision.
''')
    print(json.dumps(dict(status='assembled',retained_files=len(retained),baseline_labels={k:len(v) for k,v in before.items()})))
if __name__=='__main__':main()
