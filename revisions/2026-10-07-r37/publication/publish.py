"""Assemble and build the R37 paper without rerunning or retiming science.

Run from the repository root in the source-bound publication workspace.
The download workflow supplies immutable historical publication inputs.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
REL='revisions/2026-10-07-r37'
R=ROOT/REL
OLD='revisions/2026-10-05-r21'
DOCS=['historical_article','historical_supplement','applications','supp','ECTA','response']
LABEL=re.compile(r'\\label\s*\{([^}]+)\}')
INPUT=re.compile(r'(?m)^\s*\\(?:input|include)\s*\{([^}]+)\}')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,text):
    p=R/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def plain(s): return re.sub(r'(?m)(?<!\\)%.*$','',s)
def closure(path,seen=None):
    seen=set() if seen is None else seen
    if path in seen:return seen
    p=ROOT/path
    if not p.is_file():raise FileNotFoundError(path)
    seen.add(path)
    if p.suffix=='.tex':
        for q in INPUT.findall(plain(p.read_text())):
            closure(q if Path(q).suffix else q+'.tex',seen)
    return seen

def esc(s):
    table={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(table.get(c,c) for c in s)
def front(title):
    return '\n'.join([r'\begin{document}',r'\begin{frontmatter}','\\title{'+title+'}',r'\runtitle{Neural Bellman Operators}',r'\begin{aug}',r'\author[id=au1,addressref={add1}]{\fnms{Qian}~\snm{QI}}',r'\address[id=add1]{Peking University}',r'\end{aug}',r'\end{frontmatter}',''])
def inputs(paths):return ''.join('\\input{'+p+'}\n' for p in paths)
def external(text,doc):
    text=re.sub(r'(?m)^\\externaldocument[^\n]*\n','',text)
    ext=''.join('\\externaldocument{'+REL+'/build/'+doc+'_from_'+other+'}['+other+'.pdf]\n' for other in DOCS if other!=doc)
    return text.replace(r'\begin{document}',ext+r'\begin{document}',1)

def audit_science():
    freeze=json.loads((R/'protocols/SOURCE_FREEZE.json').read_text())
    for p,h in freeze['files'].items():
        if sha(ROOT/p)!=h:raise RuntimeError('Frozen source mismatch: '+p)
    summary=json.loads((R/'results/SUMMARY.json').read_text())
    assert summary['services']==8 and summary['certified']==8
    sys.path.insert(0,str(R/'code'))
    import adaptive_refresh as a
    def decode(x):
        if isinstance(x,dict):
            if set(x)=={'numerator_hex','denominator_hex'}:return F(int(x['numerator_hex'],16),int(x['denominator_hex'],16))
            return {k:decode(v) for k,v in x.items()}
        if isinstance(x,list):return [decode(v) for v in x]
        if isinstance(x,str):
            try:return F(x)
            except ValueError:return x
        return x
    checked=[]
    for row in summary['rows']:
        p=R/'results/exact'/row['record']
        assert sha(p)==row['record_sha256']
        record=decode(json.loads(p.read_text()))
        assert record['policy_gap_upper']<=F(1,10000)
        for stage in record['records']:
            if not stage['hidden_updates']:continue
            M=stage['center'];d=len(M)
            a.r.psd(a.r.add(M,a.r.eye(d,F(3,2)),-1))
            a.r.psd(a.r.add(a.r.eye(d,3),M,-1))
            checked.append({'record':row['record'],'date':stage['date'],'target_lower':'3/2','target_upper':'3'})
    write('audit/TARGET_BOUNDS.json',json.dumps({'checks':checked,'passed':len(checked),'scope':'Post-execution exact replay of target bounds; no new fits or replacement clocks.'},indent=2)+'\n')
    return summary

def table(summary):
    names={'linear-warm':'Linear warm','quadratic-refresh':'Quadratic, fixed','adaptive-cached':'Quadratic, adaptive','structural':'Structural'}
    lines=[r'\begin{table}[t]',r'\centering',r'\caption{Complete construction at a common policy tolerance}',r'\label{tab:r37construction}',r'\small\setlength{\tabcolsep}{3.2pt}',r'\begin{tabular}{llrrrrr}',r'\toprule',r'Construction & Economy & Updates & Inverses & Bits & Gap bound & Seconds\\',r'\midrule']
    for row in summary['rows']:
        gap=row['policy_gap_upper']
        if gap:
            coef,exp=f'{gap:.2e}'.split('e');sci='$'+coef+r'\!\times\!10^{'+str(int(exp))+'}$'
        else:sci='$0$'
        lines.append(f"{names[row['method']]} & {'Anchor' if row['regime']=='anchor' else 'Changed'} & {row['total_hidden_updates']} & {row['training_target_inverse_builds']} & {row['fractional_bits_sum']} & {sci} & {row['complete_service_seconds']:.4f}"+r'\\')
    lines += [r'\bottomrule',r'\end{tabular}',r'\par\smallskip\begin{minipage}{0.98\linewidth}\footnotesize',r'\emph{Notes:} All eight policies satisfy the tolerance $10^{-4}$ uniformly on $\|x_0\|^2\leq2$. Inverses count constructions for training targets only. Bits is the sum of fractional precisions across hidden updates, not total arithmetic work. Complete seconds include evaluation, training, checks, actor solves, serialization, and durable detailed output. Common startup and the final ledger are unallocated. These are deterministic construction objects, not population samples.',r'\end{minipage}',r'\end{table}']
    write('results/construction_table.tex','\n'.join(lines)+'\n')

def assemble():
    original_paths=set()
    for name in ('ECTA','supp','applications'):original_paths |= closure(OLD+'/'+name+'.tex')
    old_hash={p:sha(ROOT/p) for p in sorted(original_paths)}
    old_labels=set().union(*(set(LABEL.findall((ROOT/p).read_text())) for p in original_paths))
    summary=audit_science();table(summary)
    original=(ROOT/OLD/'ECTA.tex').read_text()
    pre=re.sub(r'(?m)^\\externaldocument[^\n]*\n','',original.split(r'\begin{document}')[0])
    pre+='\n'+r'\setlength{\emergencystretch}{2em}'+'\n'
    matter=original.split(r'\begin{document}',1)[1].split(r'\end{frontmatter}',1)[0]+r'\end{frontmatter}'+'\n'
    abstract='''This paper develops Neural Bellman Operators for policy evaluation and feasible
improvement in controlled economies. Centered continuation errors determine
decision accuracy, and own-policy Bellman comparisons connect local errors to
full-policy loss. For a trainable square continuation in a recursive capital
economy, primitive budgets and verified training conditions give a finite
construction against all adapted policies of finite cost. A precision-adaptive
refresh rule permits rectangular factors and noncommuting starts, allocates
whole-step arithmetic error, and links a finite hidden-weight schedule to the
policy tolerance. Eight source-frozen exact services instantiate this result.
Precision adaptation reduces stored precision and complete service time relative
to inherited neural implementations in both specified regimes; a structural
solution remains faster. The complete original controlled-diffusion framework,
economic applications, and adverse numerical comparisons are retained. The
results distinguish constructive neural accuracy from empirical work superiority
and keep model-specific economic and implementation conditions explicit.'''
    matter=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}'+'\n'+abstract+'\n'+r'\end{abstract}',matter,flags=re.S)
    bibs='revision_reference,revisions/2026-10-05-r19-integrated/references,revisions/2026-10-05-r21/references,revisions/2026-10-06-r27/references,'+REL+'/references'
    ending='\n\\bibliographystyle{ecta-fullname}\n\\bibliography{'+bibs+'}\n\\end{document}\n'
    p='revisions/2026-10-06-r31/manuscript/constructive_risk.tex'
    s=(ROOT/p).read_text();old='The terminal actor uses\n$Q_f$ directly.'
    assert old in s
    write('manuscript/constructive_risk.tex',s.replace(old,'The terminal actor uses the known transformed coefficient\n$\\Psi_\\theta(Q_f)$ without a factor fit, as in \\eqref{eq:r32terminal}.'))
    p='revisions/2026-10-04-r16/retained/manuscript/economic_scope.tex'
    s=(ROOT/p).read_text();old='The capital economy studied above provides a setting in which policy-specific verification can be carried through to a high-dimensional diffusion.'
    assert old in s
    write('manuscript/economic_scope.tex',s.replace(old,'The original diffusion applications and the directly specified recursive capital economy have distinct verification accounts. The latter provides the constructive full-policy instance studied above; it is not an unverified discretization certificate for the former.'))
    main=[REL+'/manuscript/introduction.tex','revisions/2026-10-04-r16/manuscript/literature.tex','revisions/2026-10-05-r19-integrated/manuscript/literature_addition.tex','revisions/2026-10-04-r16/retained/manuscript/model.tex','revisions/2026-10-04-r16/retained/manuscript/method.tex','revisions/2026-10-04-r16/retained/manuscript/algorithm.tex','revisions/2026-10-05-r19-integrated/manuscript/targets.tex','revisions/2026-10-05-r19-integrated/manuscript/decision_main.tex','revisions/2026-10-05-r23/manuscript/full_policy.tex','revisions/2026-10-06-r27/manuscript/entropic_main.tex',REL+'/manuscript/constructive_risk.tex','revisions/2026-10-06-r34/manuscript/robust_policy.tex',REL+'/manuscript/precision_refresh.tex',REL+'/manuscript/evidence.tex',REL+'/manuscript/economic_scope.tex',REL+'/manuscript/conclusion.tex']
    write('ECTA.tex',external(pre+r'\begin{document}'+matter+inputs(main)+ending,'ECTA'))
    supppre=pre.replace(r'\newtheorem{theorem}{Theorem}',r'\newtheorem{theorem}{Theorem}'+'\n'+r'\renewcommand{\thetheorem}{S.\arabic{theorem}}'+'\n'+r'\renewcommand{\theequation}{S.\arabic{equation}}'+'\n'+r'\renewcommand{\thesection}{S.\arabic{section}}')
    proof=['revisions/2026-10-05-r19-integrated/manuscript/decision_proofs.tex','revisions/2026-10-05-r21/manuscript/composition_main.tex','revisions/2026-10-05-r21/manuscript/composition_proofs.tex','revisions/2026-10-05-r23/manuscript/full_policy_proofs.tex','revisions/2026-10-06-r27/manuscript/entropic_proofs.tex','revisions/2026-10-06-r31/manuscript/constructive_proofs.tex','revisions/2026-10-06-r32/manuscript/curvature.tex','revisions/2026-10-06-r33/manuscript/warm_start.tex','revisions/2026-10-06-r33/manuscript/warm_start_proofs.tex','revisions/2026-10-06-r34/manuscript/robust_policy_proofs.tex',REL+'/manuscript/precision_proofs.tex']
    write('supp.tex',external(supppre+front('Technical Supplement to Neural Bellman Operators')+inputs(proof)+ending,'supp'))
    for new,old in [('historical_article','ECTA'),('historical_supplement','supp'),('applications','applications')]:
        write(new+'.tex',external((ROOT/OLD/(old+'.tex')).read_text(),new))
    blocks=[]
    for block in (R/'response.md').read_text().split('\n\n'):
        block=block.strip()
        if not block or block.startswith('# '):continue
        if block.startswith('### '):blocks.append('\\subsection*{'+esc(block[4:])+'}')
        elif block.startswith('## '):blocks.append('\\section*{'+esc(block[3:])+'}')
        else:blocks.append(esc(block))
    write('response.tex',external(pre+front('Response to the Referee on Neural Bellman Operators')+'\n\n'.join(blocks)+'\n\\end{document}\n','response'))
    all_paths=set().union(*(closure(REL+'/'+d+'.tex') for d in DOCS))
    new_labels=set().union(*(set(LABEL.findall((ROOT/p).read_text())) for p in all_paths))
    assert old_labels <= new_labels
    for p,h in old_hash.items():assert sha(ROOT/p)==h,p
    write('audit/PRESERVATION.json',json.dumps({'original_publication_components':len(old_hash),'original_publication_labels':len(old_labels),'missing_labels':[],'old_component_modifications':[],'old_component_sha256':old_hash,'current_copy_edits':['Terminal actor uses Psi_theta(Q_f).','Direct recursive economy distinguished from the original diffusion.'],'organization':'Current article and active proofs; complete previous article, supplement and all applications retained as companions.'},indent=2)+'\n')
    (ROOT/'ECTA.tex').write_text('\\input{'+REL+'/ECTA.tex}\n')
    (ROOT/'supp.tex').write_text('\\input{'+REL+'/supp.tex}\n')
    (ROOT/'README.md').write_text('''# Neural Bellman Operators — R37

Current revision: original NBO economic framework, constructive neural full-policy theory, and precision-adaptive continuation refresh.

## Read the current paper

- [Main article](revisions/2026-10-07-r37/build/ECTA.pdf) — [LaTeX](revisions/2026-10-07-r37/ECTA.tex).
- [Active technical supplement](revisions/2026-10-07-r37/build/supp.pdf).
- [Point-by-point referee response](revisions/2026-10-07-r37/response.md) — [PDF](revisions/2026-10-07-r37/build/response.pdf).
- [Complete economic applications](revisions/2026-10-07-r37/build/applications.pdf).
- [Retained previous article](revisions/2026-10-07-r37/build/historical_article.pdf) and [complete previous supplement](revisions/2026-10-07-r37/build/historical_supplement.pdf).

The original source components, labels, applications and adverse comparisons are preserved. Current root entry points no longer silently refer to R21. This revision addresses the independent advisory R21 report; it is not a journal editorial acceptance.

## New science and evidence

The precision-adaptive theorem supplies a finite hidden-weight cap and fractional-storage account, with whole-step error control, rectangular factors, noncommuting starts, fixed-target caching, and a full-policy implication. Classical polar iteration theory is credited.

Eight source-frozen services all certify the same full-policy tolerance. Adaptive precision improves on the two inherited neural implementations in both specified complete service clocks; the structural comparator remains faster. These are deterministic construction cases, not population samples or universal neural-superiority evidence.

See [protocol](revisions/2026-10-07-r37/protocols/PROTOCOL.json), [source hashes](revisions/2026-10-07-r37/protocols/SOURCE_FREEZE.json), [all outcomes](revisions/2026-10-07-r37/results/SUMMARY.json), [science audit](revisions/2026-10-07-r37/audit/SCIENCE_AUDIT.json), [preservation](revisions/2026-10-07-r37/audit/PRESERVATION.json), and [release audit](revisions/2026-10-07-r37/audit/RELEASE_AUDIT.json).

Rebuild the native publication with `python revisions/2026-10-07-r37/publication/publish.py build` from the repository root, with the documented source-bound inputs and a TeX installation supporting the repository's Econometrica class. The publication workflow restores the immutable historical input artifacts and materializes every current source before compilation. It never reruns or replaces the scientific clocks. A new scientific execution requires a clean, separately identified results directory.
''')

def doc_labels(doc):return set().union(*(set(LABEL.findall((ROOT/p).read_text())) for p in closure(REL+'/'+doc+'.tex')))
def refresh_refs():
    (R/'build').mkdir(exist_ok=True)
    for doc in DOCS:
        used=doc_labels(doc)
        for other in ['ECTA','supp','applications','historical_article','historical_supplement','response']:
            if other==doc:continue
            aux=R/'build'/(other+'.aux');lines=[]
            if aux.exists():
                for line in aux.read_text(errors='replace').splitlines():
                    m=re.match(r'\\newlabel\{([^}]+)\}',line)
                    if m and m[1] not in used:used.add(m[1]);lines.append(line)
            write('build/'+doc+'_from_'+other+'.aux','\\relax\n'+'\n'.join(lines)+'\n')

def build():
    env=os.environ.copy()
    for k in ('BIBINPUTS','BSTINPUTS'):env[k]=str(ROOT)+':'+env.get(k,'')
    for iteration in range(5):
        refresh_refs()
        for doc in DOCS:
            command=['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory='+str(R/'build'),str(R/(doc+'.tex'))]
            with (R/'audit'/f'TEX_{doc}_{iteration}.log').open('w') as h:
                p=subprocess.run(command,cwd=ROOT,env=env,stdout=h,stderr=subprocess.STDOUT)
            if p.returncode:raise RuntimeError('Native compilation failed: '+doc)
            if iteration==0 and '\\bibdata' in (R/'build'/(doc+'.aux')).read_text():
                with (R/'audit'/f'BIB_{doc}.log').open('w') as h:
                    p=subprocess.run(['bibtex',str(R/'build'/doc)],cwd=ROOT,env=env,stdout=h,stderr=subprocess.STDOUT)
                if p.returncode:raise RuntimeError('Bibliography failed: '+doc)
    reports=[]
    for doc in DOCS:
        text=(R/'build'/(doc+'.log')).read_text(errors='replace')
        bad=[s for s in text.splitlines() if 'undefined' in s.lower() and ('reference' in s.lower() or 'citation' in s.lower())]
        assert not bad,(doc,bad)
        assert 'There were multiply-defined labels' not in text,doc
        assert 'Missing character:' not in text,doc
        pages=re.search(r'Output written on .*?\((\d+) pages?',text,re.S)
        reports.append(dict(document=doc,pages=int(pages[1]) if pages else None,undefined_references=bad,multiply_defined_labels=False,missing_characters=False,overfull_hboxes=text.count('Overfull \\hbox'),overfull_vboxes=text.count('Overfull \\vbox'),pdf_sha256=sha(R/'build'/(doc+'.pdf'))))
    write('audit/COMPILATION.json',json.dumps(reports,indent=2)+'\n')
    audit=dict(publication_source_commit=os.environ.get('NBO_PUBLICATION_SHA'),inherited_commit='b274a8326915960c04697d181238908f0f6a261f',review_commit='281e57b18a2d88de68d2219da1a7194e90570d13',review_blob='947147612cc22f5e10ff15faf347fcb3de222656',reviewed_R21_commit='278916666b32e03081ffe8d4aa05d9766c259b85',science_freeze_commit='2b43dce935af3ee2e1b4cb2edb5e614f24f81ac9',evidence_commit='a5557b024379b2ec5c2ad28fe56e82fd74a2c89d',science=json.loads((R/'audit/SCIENCE_AUDIT.json').read_text()),preservation=json.loads((R/'audit/PRESERVATION.json').read_text()),target_bounds=json.loads((R/'audit/TARGET_BOUNDS.json').read_text()),compilation=reports,visual_inspection='Automated compilation only at this stage; separate page inspection may follow.',scope='No old scientific execution rerun or clock replaced. Native compilation and algebraic checks are not editorial acceptance.')
    write('audit/RELEASE_AUDIT.json',json.dumps(audit,indent=2)+'\n')
    paths=[p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.aux','.bbl','.blg','.out','.toc') and p.name!='PUBLICATION_FILES_SHA256.json']
    write('PUBLICATION_FILES_SHA256.json',json.dumps({str(p.relative_to(ROOT)):sha(p) for p in paths},indent=2,sort_keys=True)+'\n')
    print(json.dumps(reports,indent=2))
if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'assemble'
    if mode=='assemble':assemble()
    elif mode=='build':build()
    else:raise ValueError('Expected assemble or build')
