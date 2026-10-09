"""Offline R51 publication: preserve R50 sources; integrate proved additions."""
from pathlib import Path
import difflib, hashlib, json, re, shutil, sys
import build as b
R=Path(__file__).resolve().parents[1]
ABSTRACT=r'''This paper develops Neural Bellman Operators for policy evaluation and feasible improvement in controlled economies. A constructive continuation retains feasible action witnesses, and its native and affine--ReLU realizations preserve the same policy. Signed own-policy evaluation bands yield a centered, acquisition-aware improvement rule that retains the incumbent unless a feasible change is certified nonworsening. We prove a finite-sweep accuracy bound for the original Bellman optimum in terms of policy-evaluation, action-search and comparison errors; the evaluation-width coefficient is sharp. In the exact case, optimality follows within the finite horizon without intermediate cost increases. A source-bound investment study executes an analytically integrated final-date specialization and separately records construction, certification, actual policy costs and verification work. Both witness and conventional policies receive the same improvement. The evidence identifies own-incumbent cost reductions while generally retaining FVI's lower cost. Simultaneous cost intervals support resource and replacement decisions. The original theory, economic applications and adverse comparisons are preserved in complete development editions.'''

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def expand(path,seen=None):
    seen=set() if seen is None else seen
    if path in seen:return ''
    seen.add(path);text=path.read_text()
    def sub(m):
        p=R/(m[1]+('' if m[1].endswith('.tex') else '.tex'))
        return expand(p,seen) if p.exists() else m[0]
    return re.sub(r'\\input\{([^}]+)\}',sub,text)

def integrate():
    # The recovered R50 generator is retained unchanged and remains replayable.
    # Its output is kept before preparing the new active R51 exposition.
    retained=R/'preserved/R50/generated';retained.mkdir(parents=True,exist_ok=True)
    for n in ('ECTA','supp','complete','complete-supp'):
        shutil.copy2(R/(n+'.tex'),retained/(n+'.tex'))
    old=(R/'sections/study50.tex').read_text()
    old=old.replace('The main experiment and a subsequent common-accuracy amendment have separate pre-execution source freezes.',
      'The recovered R50 main experiment and common-accuracy amendment had separate local pre-execution freezes. R51 is an explicitly known-design reproduction, with its own Git source identity and runner clocks; the same draws do not provide additional independent observations.')
    start='The source and protocol were frozen locally before their corresponding measured execution.'
    end='No completed primary service was overwritten.'
    i=old.index(start);j=old.index(end,i)+len(end)
    old=old[:i]+('The original R50 design and source were frozen locally before their measured execution. Its early bisection-only development test and subsequent equidistribution correction are retained with their original records. R51 freezes the recovered algorithm before a known-design reproduction; it is not presented as a new blind experiment. The present clocks belong only to this execution, and the earlier R49 evidence is unchanged.')+old[j:]
    old=old.replace('The supplemental draws are new and conditionally independent in the statistical model;',
      'The supplemental groups have their own conditional independent-bin model within the declared simultaneous family;')
    (R/'sections/study51.tex').write_text(old)
    for n in ('ECTA','supp','complete','complete-supp'):
        text=(R/(n+'.tex')).read_text()
        if n in ('ECTA','complete'):
            needle=r'\input{sections/improvement50}'
            if needle not in text:raise ValueError('Missing improvement insertion point: '+n)
            text=text.replace(needle,needle+'\n'+r'\input{sections/finite_sweeps51}',1)
        else:
            needle=r'\input{sections/proofs50}'
            if needle not in text:raise ValueError('Missing proof insertion point: '+n)
            text=text.replace(needle,needle+'\n'+r'\input{sections/finite_sweeps_proofs51}',1)
        text=text.replace(r'\input{sections/study50}',r'\input{sections/study51}')
        text=text.replace('active R50 exposition','active R51 exposition').replace('current R50 argument','current R51 argument').replace('Current R50 development','Current R51 development')
        if n=='ECTA':text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+ABSTRACT+'\n'+m[2],text,flags=re.S)
        if n=='supp':text=text.replace('and the R50 revision','and the R51 revision').replace('The added reference-advantage and terminal-improvement proofs are included here;', 'The reference-advantage, terminal-improvement and finite-sweep accuracy proofs are included here;')
        (R/(n+'.tex')).write_text(text)
    if (R/'response.tex').exists():
        response=(R/'response.tex').read_text().replace('Revision R50, 8 October 2026.','Revision R51, 8 October 2026.')
        (R/'response.tex').write_text(response)
    labels=lambda text:set(re.findall(r'\\label\{([^}]+)\}',text))
    maps={}
    for name in ('ECTA','supp','complete','complete-supp'):
        before=labels(expand(retained/(name+'.tex')))
        after=labels(expand(R/(name+'.tex')))
        missing=before-after
        if missing:raise ValueError((name,'lost labels',sorted(missing)))
        maps[name]={'recovered_labels':len(before),'current_labels':len(after),'missing':[]}
        old=(retained/(name+'.tex')).read_text().splitlines(True)
        new=(R/(name+'.tex')).read_text().splitlines(True)
        (R/'audit'/(name+'-R50-to-R51.diff')).write_text(''.join(difflib.unified_diff(old,new,fromfile='recovered-R50/'+name+'.tex',tofile='R51/'+name+'.tex')))
    for name in ('ECTA','supp'):
        old=(R/'preserved/R49'/(name+'.tex')).read_text().splitlines(True);new=(R/(name+'.tex')).read_text().splitlines(True)
        (R/'audit'/(name+'-R49-to-R51.diff')).write_text(''.join(difflib.unified_diff(old,new,fromfile='R49/'+name+'.tex',tofile='R51/'+name+'.tex')))
    save(R/'audit/PRESERVATION51.json',maps)

def main():
    for executable in ('pdflatex','pandoc','pdfinfo'):
        if shutil.which(executable) is None:raise RuntimeError('Missing publication dependency: '+executable)
    b.LOGS.mkdir(parents=True,exist_ok=True)
    (R/'build').mkdir(exist_ok=True);(R/'tables').mkdir(exist_ok=True)
    inherited=b.historical()
    recovered={'constructive':b.tests([sys.executable,'code/tests50.py'],'new-exact-tests'), 'publication':b.tests([sys.executable,'code/publication_tests50.py'],'new-publication-tests')}
    b.run([sys.executable,'code/audit50.py'],'new-record-audit')
    b.run([sys.executable,'code/tables50.py'],'new-tables')
    b.run([sys.executable,'code/assemble50.py'],'assemble')
    b.response()
    old_count=sum(j['tests'] for j in list(inherited.values())+list(recovered.values()))
    extra=b.tests([sys.executable,'code/tests51.py'],'finite-sweep-exact-tests')
    integrate()
    documents=[b.compile_document(n) for n in ('ECTA','supp','complete','complete-supp','response')]
    report={'status':'source_bound_build_passed','inherited_and_recovered_tests':old_count,'new_finite_sweep_tests':extra,'total_tests':old_count+extra['tests'],'compilation':documents,'record_audit':json.loads((R/'audit/RESULT_AUDIT.json').read_text()),'preservation':json.loads((R/'audit/PRESERVATION51.json').read_text()),'execution_scope':'known-design reproduction, not new independent sample size','all_state_theory_and_final_date_economic_execution_distinct':True,'historical_paths_deleted':False,'network_used_by_builder':False}
    save(R/'audit/RELEASE51.json',report)
    manifest={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and not any(v in p.parts for v in ('__pycache__','build','audit'))}
    save(R/'audit/PUBLICATION_FILES51.json',manifest)
    print(json.dumps({'total_tests':report['total_tests'],'documents':documents},indent=2))
if __name__=='__main__':main()
