"""Offline R69 publication build; no training or scientific services are rerun."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,time
from prepare_paper69 import expanded
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-10-r67'
ENV={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1','SOURCE_DATE_EPOCH':'1791676800','FORCE_SOURCE_DATE':'1'}
DOCS=('ECTA','supp','complete','response')
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,sort_keys=True,indent=2)+'\n')
def run(args,label):
    file=R/'audit/build-logs'/(label+'.log');file.parent.mkdir(parents=True,exist_ok=True)
    with file.open('w') as out:p=subprocess.run(args,cwd=R,env=ENV,stdout=out,stderr=subprocess.STDOUT)
    text=file.read_text(errors='replace')
    if p.returncode:raise RuntimeError(label+' failed:\n'+text[-9000:])
    return text

def preserve():
    record=json.loads((R/'audit/PAPER_PREPARED69.json').read_text())
    for path,digest in record['prior_source_sha256'].items():
        if sha(OLD/path)!=digest:raise AssertionError('Changed R67 source '+path)
    prior=expanded(OLD,OLD/'ECTA.tex');full=expanded(R,R/'complete.tex');labels=set(re.findall(r'\\label\{([^}]+)\}',full))
    missing=set(record['prior_main_labels'])-labels
    if missing:raise AssertionError('Missing prior labels '+str(sorted(missing)))
    statements=list(re.finditer(r'\\begin\{(?P<kind>theorem|lemma|proposition|corollary|definition|assumption)\}.*?\\end\{(?P=kind)\}',prior,re.S))
    for m in statements:
        if m[0] not in full:raise AssertionError('Changed inherited statement: '+m[0][:150])
    proofs=re.findall(r'\\begin\{proof\}.*?\\end\{proof\}',prior,re.S)
    for proof in proofs:
        if proof not in full:raise AssertionError('Missing inherited proof')
    return dict(status='passed',source_files=len(record['prior_source_sha256']),labels=len(record['prior_main_labels']),statements=len(statements),proofs=len(proofs),
        scope='All R67 source files remain unchanged; each original active statement and proof is present verbatim in the complete R69 edition.')

def bibliography(name):
    entries=json.loads((R/'publication/bibliography-entries.json').read_text());aux=(R/'build'/(name+'.aux')).read_text()
    keys={key for line in re.findall(r'\\citation\{([^}]+)\}',aux) for key in line.split(',')}
    if '*' in keys:keys=set(entries)
    if keys-set(entries):raise AssertionError('Missing bibliography '+str(keys-set(entries)))
    keys=sorted(keys,key=lambda key:re.search(r'\\textsc\{([^}]+)',entries[key])[1].lower())
    text='\\begin{thebibliography}{'+str(len(keys))+'}\n'+r"\providecommand{\enquote}[1]{``#1''}"+'\n'+r'\providecommand{\natexlab}[1]{#1}'+'\n\n'
    (R/'build'/(name+'.bbl')).write_text(text+'\n\n'.join(entries[k] for k in keys)+'\n\n\\end{thebibliography}\n')

def response(a):
    successes=a['returned'];contrasts=a['centered_contrasts'];reuse=a['reuse_comparisons']
    extra='\n## Audited execution summary\n\n'
    extra+=f"The complete audit retained {a['receipt_count']} of {a['planned_services']} planned receipts: {successes} returned and {a['failed_or_timed_out']} failed or timed out. The independent rational implementation checked {a['independent_trajectory_checks']:,} represented mid-bin trajectories. The two new inference streams contain {a['new_independent_initial_path_rows']:,} independent initial path rows, conditional on the stated sampling model; policies and replay checks do not multiply this sample size.\n\n"
    extra+=f"Of {len(contrasts)} returned centered contrasts, {sum(x['equivalent_at_margin'] for x in contrasts)} lie inside the prespecified two-sided margin. Of {len(reuse)} matched returned reuse comparisons, {sum(x['complete_process_win'] for x in reuse)} have a lower final complete-process clock and {sum(x['early_persistent_crossing'] for x in reuse)} meet the early persistent-prefix criterion. These counts do not identify a population timing probability or a strict neural policy-cost gain.\n\n"
    extra+='| Task | Cost contrast | Simultaneous centered interval |\n|---|---|---|\n'
    for x in contrasts:extra+=f"| d={x['d']}, T={x['T']} | {x['contrast']} | [{x['interval'][0]:.8f}, {x['interval'][1]:.8f}] |\n"
    (R/'response-execution.md').write_text((R/'response.md').read_text()+extra)
    run(['pandoc','-f','markdown','-t','latex','--wrap=auto','response-execution.md','-o','build/response-body.tex'],'response-convert')
    body=(R/'build/response-body.tex').read_text();body=re.sub(r'\\texttt\{([^{}]*)\}',lambda m:r'\nolinkurl{'+m[1].replace(r'\_','_')+'}',body)
    # Long identifiers remain in the ordinary response source. The PDF table
    # uses method names in place of unbreakable serialized contrast keys.
    for key,value in [('hat-relu','ReLU-C'),('bernstein4','Bernstein-C'),('r67-relu','R67 ReLU'),('-minus-',' minus ')]:body=body.replace(key,value)
    head=(R/'supp.tex').read_text().split(r'\input{sections/proofs67}')[0]
    head=head.replace(r'\externaldocument{build/ECTA}[ECTA.pdf]','').replace('Technical Supplement to Neural Bellman Operators','Response to the Referee: Neural Bellman Operators').replace('Neural Bellman Operators: Supplement','Response to the Referee').replace('e69supp','e69response')
    head=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'Revision R69 responds to the 11 October 2026 advisory report on R67. It retains the original NBO paper and adds achieved readout certificates, independent validation, prospective deployment evidence and verified original-policy cost inference.'+m[2],head,flags=re.S)
    (R/'response.tex').write_text(head+r'\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}'+'\n'+body+'\n\\end{document}\n')

def compile_all():
    for name in DOCS:(R/'build'/(name+'.bbl')).unlink(missing_ok=True)
    for iteration in range(4):
        for name in DOCS:
            run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build',name+'.tex'],name+'-pass'+str(iteration))
            if not iteration and name!='response':bibliography(name)
    documents=[]
    for name in DOCS:
        log=(R/'build'/(name+'.log')).read_text(errors='replace')
        patterns={'undefined':r'(?:Reference|Citation).*undefined|There were undefined references','duplicate_labels':r'multiply defined|multiply-defined labels','missing_glyphs':r'Missing character:','overfull':r'Overfull \\[hv]box','fatal':r'^!|Fatal error'}
        bad={key:re.findall(pattern,log,re.M) for key,pattern in patterns.items()}
        if any(bad.values()):raise AssertionError((name,bad))
        path=R/'build'/(name+'.pdf');info=subprocess.check_output(['pdfinfo',str(path)],text=True)
        text=subprocess.check_output(['pdftotext','-layout',str(path),'-']);(R/'build'/(name+'.txt')).write_bytes(text)
        documents.append(dict(document=name,pages=int(re.search(r'^Pages:\s*(\d+)',info,re.M)[1]),sha256=sha(path),text_sha256=hashlib.sha256(text).hexdigest(),checks=bad,
            font_substitution_warnings=re.findall(r"Font shape `[^']+' undefined",log)))
    return documents

def main():
    start=time.perf_counter();(R/'build').mkdir(exist_ok=True);preservation=preserve();documents_only='--documents' in sys.argv
    if not documents_only:
        tests={}
        paths=[(str(n),R.parent/f'2026-10-10-r{n}'/'code'/f'tests{n}.py') for n in (63,64,65,66)]
        paths += [('67-science',OLD/'code/tests67.py'),('67-math',OLD/'code/tests_math67.py'),('67-records',OLD/'code/tests_records67.py'),('69',R/'code/tests69.py')]
        for label,path in paths:
            text=run([sys.executable,str(path)],'tests-'+label);m=re.search(r'Ran (\d+) tests?',text)
            if not m or not re.search(r'^OK\s*$',text,re.M):raise AssertionError('Missing test success '+label)
            tests[label]=int(m[1])
        save(R/'audit/TESTS69.json',dict(status='passed',counts=tests,total=sum(tests.values())))
        run([sys.executable,'code/audit69.py'],'complete-record-audit69')
    run([sys.executable,'code/tables69.py'],'derived-tables69');a=json.loads((R/'audit/RESULT_AUDIT69.json').read_text());response(a);documents=compile_all()
    pages={d['document']:d['pages'] for d in documents}
    if pages['ECTA']>45 or pages['supp']>25:raise AssertionError(('Active document page targets exceeded',pages))
    final=dict(status='passed',documents=documents,preservation=preservation,tests=json.loads((R/'audit/TESTS69.json').read_text()),
        record_audit_sha256=sha(R/'audit/RESULT_AUDIT69.json'),source_freeze_sha256=sha(R/'audit/SOURCE_FREEZE69.json'),
        new_scientific_services_in_builder=0,new_independent_rows_in_builder=0,network_used_by_builder=False,
        scientific_returns=a['returned'],scientific_failures=a['failed_or_timed_out'],seconds=time.perf_counter()-start,
        visual_inspection='Not implied by compilation, log checks or text extraction; document separately when performed.')
    save(R/'audit'/('DOCUMENT_REBUILD69.json' if documents_only else 'RELEASE69.json'),final);print(json.dumps(final,indent=2))
if __name__=='__main__':main()
