"""Integrate the new theorem and deterministic evidence into the original NBO paper."""
from pathlib import Path
import difflib,hashlib,json,re,shutil
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-12-r81'
ABSTRACT='''Neural Bellman Operators construct feasible policies from fitted own-future continuations. We connect attained residual qualification, acquired-state feasibility and original-optimum policy loss to the cost of the implemented controller. Affine-calibrated derivative bounds permit comparable fixed-feature qualification, while exact action-switch duals constrain the policies induced by approximately optimized readouts. We prove a directed economic transfer that prices every action not excluded by these duals and bounds complete policy costs uniformly over entire optimization sublevels. The bound can retain economic information when exact action stability is unavailable. In the original nonlinear investment economy, independent whole-bin implementations evaluate the complete actionwise refinement catalogue. Existing simultaneous controller-cost intervals then extend to the qualified classes without new observations or a probability bound over optimizers. The construction preserves the original Bellman problem and provides explicit verification costs and conditional deployment decisions.'''
INTRO=r'''The economic conclusion can also survive approximate optimization without exact agreement of every acquired action. We retain the alternative actions that are not excluded by their objective barriers, integrate their signed economic effects under the original law, and form a cost enclosure for the entire readout sublevel. This actionwise bound refines the uncertified-cell mass bound rather than declaring the remaining cells safe. Its complete two-date execution and independent arithmetic checks extend the original attained-continuation argument to approximately optimized controller classes, while retaining the same cost observations and conventional comparators.

'''
CONCLUSION=r'''The actionwise transfer strengthens this conclusion when qualification leaves some decisions unresolved. Signed economic enclosures for the remaining actions produce a uniform cost band for every readout in the specified objective sublevel, not just for the displayed optimizer output. Exhaustive dyadic integration and independent arithmetic give a finite realization in the original investment law. The remaining numerical width, the original statistical uncertainty and the work of verification are charged separately; none is inferred to vanish from the validity of a fallback controller.

'''

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    marker=R/'audit/INTEGRATION82.json'
    if marker.exists():print('Ordinary R82 manuscript already integrated; author edits preserved.');return
    for name in ('actionwise82','study82','proof82'):
        if not (R/'sections'/(name+'.tex')).exists():raise FileNotFoundError(name)
    original=R/'preserved/R81-original'
    for folder in ('audit','tables'):
        if (OLD/folder).exists():shutil.copytree(OLD/folder,original/folder,dirs_exist_ok=True)
    for n in ('ECTA','supp','appendix'):
        p=R/(n+'.tex');before=p.read_text();text=before
        if n=='ECTA':
            for previous,new in (('calibration81','actionwise82'),('study81','study82')):
                needle=r'\input{sections/'+previous+'}'
                if text.count(needle)!=1:raise AssertionError('Unexpected manuscript input '+needle)
                text=text.replace(needle,needle+'\n'+r'\input{sections/'+new+'}',1)
            text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+ABSTRACT+'\n'+m[2],text,count=1,flags=re.S)
            needle=r'\paragraph{Reading path.}';text=text.replace(needle,INTRO+needle,1)
            needle=r'\bibliographystyle{ecta-fullname}';text=text.replace(needle,CONCLUSION+needle,1)
        elif n=='appendix':
            needle=r'\input{sections/proof81}'
            if text.count(needle)!=1:raise AssertionError('Original dual proof input')
            text=text.replace(needle,needle+'\n'+r'\input{sections/proof82}',1)
        p.write_text(text)
        (R/'audit'/(n+'-R81-to-R82.diff')).write_text(''.join(difflib.unified_diff(before.splitlines(True),text.splitlines(True),fromfile='R81/'+n+'.tex',tofile='R82/'+n+'.tex')))
    shutil.copy2(R/'response82.md',R/'response.md')
    old=json.loads((R/'audit/PREPARATION82.json').read_text())
    lines=['# R82 content and provenance map','','Baseline: c411bfb2badac2981f001f4c84d99c8c3c306c5e. Controlling R67 advisory review: 4b27b56f4514f6c1d77b69fe707f7202f8b06b19.','','Every inherited active section is retained byte-identically in its original R81 document. Original wrappers, PDF outputs, audit records and tables are copied under preserved/R81-original.','','| Section | R81 document | R82 document |','|---|---|---|']
    for name,item in sorted(old['active_sections'].items()):lines.append('| `'+name+'.tex` | '+item['document']+' | '+item['document']+' |')
    lines+=['','New main sections: actionwise82.tex and study82.tex. New complete integration, convergence and work proofs: proof82.tex in the appendix.','The 976-action, four-level catalogue is deterministic verification. It adds no fitted controllers and no independent cost-observation rows.','The original expected-cost, vector, recursive-query and broader companion results retain their own assumptions and evidence.','']
    (R/'CONTENT_MAP82.md').write_text('\n'.join(lines))
    (R/'README.md').write_text('''# Neural Bellman Operators — R82

The original paper is revised in place within a new independent revision.
The active reading set is [ECTA.pdf](build/ECTA.pdf), [supp.pdf](build/supp.pdf),
[appendix.pdf](build/appendix.pdf), and [response.pdf](build/response.pdf).
Ordinary sources are ECTA.tex, supp.tex, appendix.tex and response.md.

The new theorem is in sections/actionwise82.tex. Complete proofs and every
refinement outcome are in sections/proof82.tex. The complete deterministic
execution is results82/; SOURCE_FREEZE82.json binds its code and inputs.
CONTENT_MAP82.md records preservation. The old R81 wrappers, PDF outputs,
audits and tables are in preserved/R81-original/.

Run `python3 revisions/2026-10-12-r82/code/build82.py` from the repository root
with Python/numpy/scipy/scikit-learn, pandoc, poppler and the retained LaTeX class
dependencies. The complete repository dependency directories are required as
listed in code/publish82.py. Reproduction re-evaluates every new paired subbox
and the inherited full-bin costs. It does not refit or resample controllers.

Publication status is determined by audit/RELEASE82.json, audit/CLEAN_REBUILD82.json
and the separately bound audit/FINAL_DELIVERY82.json. A queued workflow, a PDF
left by an incomplete build, or the mere existence of a revision branch is not
a successful release. No external peer-review acceptance is asserted.
''')
    marker.write_text(json.dumps(dict(baseline_commit=old['baseline_commit'],new_main_sections=['actionwise82','study82'],new_appendix='proof82',abstract_words=len(ABSTRACT.split()),original_title_preserved=True,inherited_active_sections=len(old['active_sections'])),indent=2)+'\n')
    print(marker.read_text())
if __name__=='__main__':main()
