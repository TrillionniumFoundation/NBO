"""R25 publication assembly with immutable inherited sources.

Only the CONTENT transformation prefixes of the archived R23/R24 assemblers
are reused, in a disposable scratch directory. Their historical Git audit
blocks are not executed or forged. A fresh, explicit preservation audit below
checks this revision's actual source closure and original working-tree bytes.
"""
from pathlib import Path
import ast, hashlib, importlib.util, json, os, re, shutil, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[3]
R=Path(__file__).resolve().parents[1]
OLD=ROOT/'revisions/2026-10-05-r21'
BASE='00f834b2d0ad259a0ffc70868dce416d183002ba'
PREFIX='revisions/2026-10-05-r25'
DOCS=('ECTA','supp','applications','evidence','response')


def save(p,text):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def dependencies(p,seen=None):
    seen=set() if seen is None else seen;p=p.resolve()
    if p in seen:return seen
    seen.add(p)
    for name in re.findall(r'\\(?:input|include)\{([^}]+)\}',p.read_text()):
        child=ROOT/name
        if not child.suffix:child=child.with_suffix('.tex')
        if child.exists():dependencies(child,seen)
        elif '#' not in name and '\\' not in name:raise FileNotFoundError(child)
    return seen


def content_prefix(source):
    """Remove old audit/output tail at its explicit olddeps marker, not checks
    inside the publication transformations. The old source remains unchanged."""
    tree=ast.parse(source)
    for node in tree.body:
        if isinstance(node,ast.FunctionDef) and node.name=='assemble':
            for i,statement in enumerate(node.body):
                if isinstance(statement,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='olddeps' for t in statement.targets):
                    node.body=node.body[:i];break
            else:raise RuntimeError('Archived assembler boundary changed')
    return ast.unparse(tree)+'\n'


def rebind(text):
    for part in ('manuscript/','results/','build/'):
        text=text.replace('revisions/2026-10-05-r24/'+part,PREFIX+'/'+part)
    return text


def assemble():
    before={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*')
            if p.is_file() and p.suffix in ('.tex','.bib','.cls','.cfg','.bst','.py')
            and PREFIX not in str(p) and '/build/' not in str(p) and '__pycache__' not in str(p)}
    # All scientific numeric replay is separately completed before assembly.
    for short,origin in [('r23','revisions/2026-10-05-r23/results/generated'),('r24','revisions/2026-10-05-r24/results')]:
        dest=R/'results'/('inherited_'+short)
        if not dest.exists():shutil.copytree(ROOT/origin,dest)
    with tempfile.TemporaryDirectory(prefix='nbo-r25-assembly-') as td:
        tmp=Path(td)
        # Only input texts and archived assembly programs are needed; no raw
        # candidate or native class is altered. Large raw arrays stay in place.
        for rel in before:
            p=ROOT/rel;q=tmp/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
        p23=tmp/'revisions/2026-10-05-r23';p24=tmp/'revisions/2026-10-05-r24'
        for name in ('SUMMARY.json','services.jsonl'):
            dest=p23/'results/primary'/name;dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/'revisions/2026-10-05-r23/results/primary'/name,dest)
        shutil.copytree(R/'results/inherited_r23',p23/'results/generated',dirs_exist_ok=True)
        shutil.copytree(R/'results/inherited_r24',p24/'results',dirs_exist_ok=True)
        for p in (p23/'code/assemble_publication.py',p24/'code/assemble.py'):
            p.write_text(content_prefix(p.read_text()))
        spec=importlib.util.spec_from_file_location('r25_content_assembly',p24/'code/assemble.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.assemble()
        for p in (p24/'manuscript').glob('*.tex'):
            if p.name=='response_body.tex':save(R/'archive/r24_response_body.tex',p.read_text());continue
            save(R/'manuscript'/p.name,rebind(p.read_text()))
        for p in (p24/'results/inherited_r23').glob('*'):
            q=R/'results/inherited_r23'/p.name
            if p.suffix=='.tex':save(q,rebind(p.read_text()))
            else:shutil.copyfile(p,q)
        for name in DOCS:save(R/(name+'.tex'),rebind((p24/(name+'.tex')).read_text()))
    # These are mathematical line breaks, not relaxed overflow thresholds.
    p=R/'manuscript/learning_main.tex';s=p.read_text()
    s=s.replace('On the line segment joining $W$ and $W-\\alpha WE(W)$,\n$\\|V\\|_2\\leq(3/2)\\sqrt{L+m/2}$.',
                'On the segment joining the current and updated factors,\n\\[\\|V\\|_2\\leq(3/2)\\sqrt{L+m/2}.\\]')
    save(p,s)
    p=R/'manuscript/full_policy_proofs.tex';s=p.read_text()
    s=s.replace("$u_t^g=-H_t^{-1}\\beta B_t'P_{t+1}A_tx$. Evaluating", "\\[u_t^g=-H_t^{-1}\\beta B_t'P_{t+1}A_tx.\\]\nEvaluating")
    save(p,s)
    p=R/'manuscript/introduction.tex';save(p,p.read_text()+r'''
\paragraph{From initialization to a returned policy.}
The constructive NBO result in Section~\ref{sec:r25constructive} removes the
local cold-start premise for an explicitly initialized trainable factor.
A backward construction fixes the implemented future before it is fitted,
and a feasible reference policy supplies an a priori lifetime error scale.
This gives a finite learning-to-policy implication, rather than only a
certificate conditional on a small terminal gradient. The new frozen
construction study reports complete work alongside the structural method;
its accuracy result is not substituted for the retained comparative costs.
''')
    p=R/'manuscript/conclusion.tex';save(p,p.read_text()+r'''
An isotropic initialization and reverse-time construction complete a finite
neural learning-to-policy argument for the declared capital class. The
starting critic need not lie in a local rank basin, and the training target
is the future of the returned policy. The all-state certificate continues
to compare with every adapted finite-cost policy. The accompanying complete
work account retains the stronger structural comparator, so a constructive
neural guarantee and a numerical advantage remain distinct conclusions.
''')
    p=R/'ECTA.tex';s=p.read_text()
    anchor=r'\input{'+PREFIX+'/manuscript/learning_main.tex}'
    assert anchor in s;s=s.replace(anchor,anchor+'\n'+r'\input{'+PREFIX+'/manuscript/constructive_main.tex}',1)
    anchor=r'\input{'+PREFIX+'/manuscript/full_policy_experiment.tex}'
    assert anchor in s;s=s.replace(anchor,anchor+'\n'+r'\input{'+PREFIX+'/manuscript/construction_experiment.tex}',1)
    abstract=r'''\begin{abstract}
This paper develops Neural Bellman Operators for policy evaluation and feasible
improvement in controlled economies. Centered continuation errors and economic
transport bounds govern reuse of learned futures. An all-state residual
certificate connects neural continuation accuracy to lifetime policy loss.
For a trainable square-activation continuation, an isotropic initialization
gives an explicit finite learning budget; a backward construction fixes the
implemented future before fitting and attains a prescribed policy tolerance
without an optimal-policy oracle. The guarantee covers all adapted finite-cost
policies in a multisector capital economy with continuous Gaussian shocks,
24 reoptimized dates, and ten or fifty vector controls. Source-frozen numerical
studies report full policy certificates, failed checks, implementation
allowances, and complete measured work. Matched quadratic and structural
comparators remain visible; candidate accuracy is not identified with neural
cost superiority. The original nonlinear capital studies, recursive utility,
endogenous preferences, temporal selves, and games retain their full accounts.
The constructive discrete-time guarantee is distinguished from the separate
continuous-economy and strategic transfer conditions.
\end{abstract}'''
    s=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:abstract,s,flags=re.S)
    s=re.sub(r'\\bibliography\{([^}]+)\}',lambda m:r'\bibliography{'+m[1]+','+PREFIX+'/references}',s)
    save(p,s)
    p=R/'supp.tex';s=p.read_text().replace(r'\bibliographystyle',r'\clearpage'+'\n'+r'\input{'+PREFIX+'/manuscript/constructive_proofs.tex}\n'+r'\input{'+PREFIX+'/results/construction_record.tex}\n'+r'\bibliographystyle',1)
    save(p,s)
    # R24 result text was rebound by the wrapper; keep the derived copy here.
    save(R/'results/refinement_record.tex',rebind((R/'results/inherited_r24/refinement_record.tex').read_text()))
    olddeps=set();newdeps=set()
    for name in ('ECTA','supp','applications'):olddeps|=dependencies(OLD/(name+'.tex'))
    for name in DOCS:newdeps|=dependencies(R/(name+'.tex'))
    getlabels=lambda ds:set().union(*(set(re.findall(r'\\label\{([^}]+)\}',p.read_text())) for p in ds))
    missing=sorted(getlabels(olddeps)-getlabels(newdeps));assert not missing,missing
    changed=[p for p,h in before.items() if sha(ROOT/p)!=h];assert not changed,changed
    provenance={'mode':'working-copy SHA256 preservation','inherited_sources_checked':len(before),'changed_inherited_source_files':changed}
    if (ROOT/'.git').exists():
        changes=subprocess.check_output(['git','diff','--name-only','--diff-filter=MDT',BASE,'--'],cwd=ROOT,text=True).splitlines()
        assert not changes,changes;provenance.update(mode='Git base and working-copy SHA256 preservation',base_commit=BASE,changed_inherited_tracked_files=changes)
    elif (ROOT/'R25_SNAPSHOT_SHA256.json').exists():
        manifest=json.loads((ROOT/'R25_SNAPSHOT_SHA256.json').read_text())
        bad=[p for p,h in manifest.items() if sha(ROOT/p)!=h];assert not bad,bad
        provenance.update(snapshot_commit=(ROOT/'R25_SNAPSHOT_COMMIT.txt').read_text().strip(),snapshot_files_verified=len(manifest))
    audit={'review_commit':'281e57b18a2d88de68d2219da1a7194e90570d13','integration_base_commit':BASE,
           'reviewed_source_components':len(olddeps),'reviewed_labels':len(getlabels(olddeps)),
           'current_labels':len(getlabels(newdeps)),'missing_inherited_labels':missing,'preservation':provenance,
           'content_reconstruction':'Archived content transformations run only in an isolated scratch directory. Their historical audit tails are replaced by this explicit current audit, never reported as newly executed old Git checks.',
           'source_copies':[{'path':p,'sha256':h} for p,h in before.items()]}
    save(R/'PRESERVATION.json',json.dumps(audit,indent=2)+'\n')
    print(json.dumps({k:v for k,v in audit.items() if k!='source_copies'},indent=2))

if __name__=='__main__':assemble()
