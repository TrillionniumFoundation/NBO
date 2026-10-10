"""Offline original-paper revision build, preserving all earlier sources.

Scientific services are never run by this builder. The corrected catalogue
must already exist, bound by its source freeze and parent receipts.
"""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-10-r65'
ENV={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1','SOURCE_DATE_EPOCH':'1791590400','FORCE_SOURCE_DATE':'1'}
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,sort_keys=True,indent=2)+'\n')
def run(args,label,cwd=R):
    log=R/'audit/build-logs'/(label+'.log');log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('w') as f:result=subprocess.run(args,cwd=cwd,env=ENV,stdout=f,stderr=subprocess.STDOUT)
    text=log.read_text(errors='replace')
    if result.returncode:raise RuntimeError(label+' failed:\n'+text[-9000:])
    return text

def preservation():
    allowed={'.tex','.bib','.cls','.cfg','.bst','.sty'};files={};locations={}
    for p in OLD.rglob('*'):
        if not p.is_file() or p.suffix not in allowed or 'build' in p.relative_to(OLD).parts:continue
        rel=str(p.relative_to(OLD));files[rel]=sha(p)
        if p.suffix=='.tex':
            for label in re.findall(r'\\label\{([^}]+)\}',p.read_text()):locations.setdefault(label,[]).append('../2026-10-10-r65/'+rel)
    previous=json.loads((OLD/'audit/PRESERVATION65.json').read_text())
    for name,digest in previous['retained_source_sha256'].items():
        if sha(OLD/'retained62'/name)!=digest:raise AssertionError('Changed retained development: '+name)
    theorem_count=proof_count=0
    for name in ('core49','accuracy62-print','query63','gated64','localization65','decisions49'):
        old=(OLD/'sections'/(name+'.tex')).read_text();new=(R/'sections'/(name+'.tex')).read_text();bundle=(R/'sections/proofs67.tex').read_text()
        for text in re.findall(r'\\begin\{(theorem|proposition|lemma|corollary)\}.*?\\end\{\1\}',old,re.S):pass
        matches=list(re.finditer(r'\\begin\{(?P<kind>theorem|proposition|lemma|corollary)\}.*?\\end\{(?P=kind)\}',old,re.S))
        for match in matches:
            if match[0] not in new:raise AssertionError('Inherited statement changed: '+name)
            theorem_count+=1
        for proof in re.findall(r'\\begin\{proof\}.*?\\end\{proof\}',old,re.S):
            if proof not in bundle:raise AssertionError('Inherited proof missing: '+name)
            proof_count+=1
    record=dict(status='passed',prior_r65_commit='34a5ce17dc3ac4681b6d004eca00637f28104e28',prior_sources_sha256=files,label_locations=locations,
        retained_r62_sources=len(previous['retained_source_sha256']),active_inherited_statements=theorem_count,verbatim_relocated_proofs=proof_count,
        scope='R65 and its retained complete development are unchanged. All six inherited active theorem sections preserve their statements; their proofs are reproduced verbatim in the current supplement.')
    save(R/'audit/PRESERVATION67.json',record)
    lines=['# R65 to R67 content map','',record['scope'],'','| Prior label | Unchanged source location |','|---|---|']
    for label,paths in sorted(locations.items()):lines.append('| `'+label+'` | '+'; '.join('`'+p+'`' for p in paths)+' |')
    (R/'CONTENT_MAP67.md').write_text('\n'.join(lines)+'\n')
    return record

def bibliography(root,name):
    entries=json.loads((root/'publication/bibliography-entries.json').read_text());aux=(root/'build'/(name+'.aux')).read_text()
    keys={key for line in re.findall(r'\\citation\{([^}]+)\}',aux) for key in line.split(',')}
    if '*' in keys:keys=set(entries)
    if keys-set(entries):raise ValueError('Missing reference '+str(keys-set(entries)))
    keys=sorted(keys,key=lambda key:re.search(r'\\textsc\{([^}]+)',entries[key])[1].lower())
    text='\\begin{thebibliography}{'+str(len(keys))+'}\n'+r"\providecommand{\enquote}[1]{``#1''}"+'\n'+r'\providecommand{\natexlab}[1]{#1}'+'\n\n'
    (root/'build'/(name+'.bbl')).write_text(text+'\n\n'.join(entries[key] for key in keys)+'\n\\end{thebibliography}\n')

def response():
    run(['pandoc','-f','markdown','-t','latex','--wrap=auto','response.md','-o','build/response-body.tex'],'response-convert')
    body=(R/'build/response-body.tex').read_text();body=re.sub(r'\\texttt\{([^{}]*)\}',lambda m:r'\nolinkurl{'+m[1].replace(r'\_','_')+'}',body)
    head=(R/'supp.tex').read_text().split(r'\input{sections/proofs67}')[0]
    head=head.replace(r'\externaldocument{build/ECTA}[ECTA.pdf]','').replace('Technical Supplement to Neural Bellman Operators','Response to the Referee: Neural Bellman Operators').replace('Neural Bellman Operators: Supplement','Response to the Referee')
    head=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'Revision R67 responds to the 10 October 2026 advisory report on R65. It retains the original NBO paper and adds operational prediction certificates, corrected complete-service evidence and a point-by-point response.'+m[2],head,flags=re.S)
    (R/'response.tex').write_text(head+r'\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}'+'\n'+body+'\n\\end{document}\n')

def check_pdf(root,name,output):
    log=(root/'build'/(name+'.log')).read_text(errors='replace');patterns={'undefined':r'(?:Reference|Citation).*undefined|There were undefined references','duplicate_labels':r'multiply defined|multiply-defined labels','missing_glyphs':r'Missing character:','overfull':r'Overfull \\[hv]box','fatal':r'^!|Fatal error'}
    bad={key:re.findall(pattern,log,re.M) for key,pattern in patterns.items()}
    if any(bad.values()):raise AssertionError((output,bad))
    src=root/'build'/(name+'.pdf');dest=R/'build'/(output+'.pdf')
    if src!=dest:shutil.copy2(src,dest)
    info=subprocess.check_output(['pdfinfo',str(dest)],text=True);raw=subprocess.check_output(['pdftotext','-layout',str(dest),'-'])
    (R/'build'/(output+'.txt')).write_bytes(raw)
    return dict(document=output,pages=int(re.search(r'^Pages:\s*(\d+)',info,re.M)[1]),sha256=sha(dest),text_sha256=hashlib.sha256(raw).hexdigest(),checks=bad,font_substitution_warnings=re.findall(r"Font shape `[^']+' undefined",log))

def compile_pair():
    names=('ECTA','supp','response')
    for name in names:(R/'build'/(name+'.bbl')).unlink(missing_ok=True)
    for iteration in range(4):
        for name in names:
            run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build',name+'.tex'],name+'-pass'+str(iteration))
            if iteration==0 and name!='response':bibliography(R,name)
    return [check_pdf(R,name,name) for name in names]

def companion(root,name,output):
    (root/'build').mkdir(exist_ok=True)
    (root/'build'/(name+'.bbl')).unlink(missing_ok=True)
    for iteration in range(4):
        run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build',name+'.tex'],output+'-pass'+str(iteration),root)
        if iteration==0:bibliography(root,name)
    return check_pdf(root,name,output)

def inherited_audit():
    # Only the output root changes. Frozen R63/R64 scientific sources and
    # records are read in their original directories and remain untouched.
    script="import sys;from pathlib import Path;sys.path.insert(0,"+repr(str(OLD/'code'))+");import audit65 as a;a.R=Path("+repr(str(R))+ ");a.main()"
    run([sys.executable,'-c',script],'inherited-full-replay65')

def main():
    start=time.perf_counter();(R/'build').mkdir(exist_ok=True);keep=preservation();docs_only='--documents' in sys.argv;active_only='--active-only' in sys.argv
    if not docs_only:
        inherited_audit();run([sys.executable,'code/audit67.py'],'corrected-complete-replay67')
        run([sys.executable,'code/erratum67.py'],'original-counterexample67')
        tests={}
        for label,file in [(str(n),R.parent/f'2026-10-10-r{n}'/'code'/f'tests{n}.py') for n in (63,64,65,66)]+[('67-scientific',R/'code/tests67.py'),('67-mathematical',R/'code/tests_math67.py'),('67-records',R/'code/tests_records67.py')]:
            text=run([sys.executable,str(file)],'tests-'+label);m=re.search(r'Ran (\d+) tests?',text)
            if not m or not re.search(r'^OK\s*$',text,re.M):raise AssertionError('Missing test success '+label)
            tests[label]=int(m[1])
        save(R/'audit/TESTS67.json',dict(status='passed',counts=tests,total=sum(tests.values())))
    run([sys.executable,'code/tables67.py'],'corrected-tables67');response();documents=compile_pair()
    if not active_only:
        with tempfile.TemporaryDirectory(prefix='nbo67-prior-documents-') as tmp:
            root=Path(tmp)/'r65'
            shutil.copytree(OLD,root,ignore=shutil.ignore_patterns('build','audit','inputs','code','__pycache__','*.npz','*.zip','*.pdf','*.log'))
            for name,output in [('ECTA','prior-ECTA65'),('supp','prior-supp65')]:documents.append(companion(root,name,output))
            for name,output in [('ECTA','development62'),('supp','development-supp62'),('complete','complete62'),('complete-supp','complete-supp62')]:documents.append(companion(root/'retained62',name,output))
    # Page discipline is checked rather than achieved by deleting historical
    # content; complete earlier editions remain as separate companions.
    for d in documents:
        if d['document']=='ECTA' and d['pages']>45:raise AssertionError('Main article exceeds 45-page publication target')
        if d['document']=='supp' and d['pages']>25:raise AssertionError('Technical supplement exceeds 25-page publication target')
    for name,digest in keep['prior_sources_sha256'].items():
        if sha(OLD/name)!=digest:raise AssertionError('Prior source mutated by build '+name)
    out=dict(status='passed',documents=documents,preservation=dict(source_files=len(keep['prior_sources_sha256']),labels=len(keep['label_locations']),inherited_statements=keep['active_inherited_statements'],verbatim_proofs=keep['verbatim_relocated_proofs']),
        tests=json.loads((R/'audit/TESTS67.json').read_text()) if (R/'audit/TESTS67.json').exists() else None,
        corrected_record_audit_sha256=sha(R/'audit/RESULT_AUDIT67.json'),seconds=time.perf_counter()-start,
        new_scientific_services_in_builder=0,additional_independent_rows_in_builder=0,network_used_by_builder=False,
        scope='Ordinary source build; complete corrected-record and inherited replay when not documents-only. Visual inspection is separate from log checks. No formal proof-checker or external acceptance claim.')
    save(R/'audit'/('DOCUMENT_REBUILD67.json' if docs_only else 'RELEASE67.json'),out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
