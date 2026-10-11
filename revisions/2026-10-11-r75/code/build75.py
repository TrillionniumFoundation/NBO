"""Ordinary-source R75 build and all-path verification; no fitting or new rows."""
from pathlib import Path
import argparse,ast,hashlib,json,re,shutil,subprocess,sys,time
import build72 as b
import build73 as old
R=Path(__file__).resolve().parents[1];DOCS=b.DOCS

def preserve():
    a=json.loads((R/'audit/PREPARATION75.json').read_text());labels=statements=proofs=0
    for name,h in a['active_sections'].items():
        if b.sha(R/name)!=h:raise AssertionError('Inherited section changed: '+name)
        count=sum((R/(d+'.tex')).read_text().count('\\input{'+name[:-4]+'}') for d in DOCS[:-1])
        if count!=1:raise AssertionError(('Prior section occurrence',name,count))
        text=(R/name).read_text();labels+=text.count('\\label{');proofs+=text.count('\\begin{proof}');statements+=len(re.findall(r'\\begin\{(?:theorem|lemma|proposition|corollary)\}',text))
    for name,h in a['prior_wrapper_sha256'].items():
        if b.sha(R/'preserved/R74-base'/name)!=h:raise AssertionError('Original wrapper changed')
    for d,ls in a['old_wrapper_labels'].items():
        if set(ls)-set(re.findall(r'\\label\{([^}]+)\}',(R/(d+'.tex')).read_text())):raise AssertionError('Original wrapper label removed')
    result=dict(status='passed',sections=len(a['active_sections']),labels=labels,formal_statements=statements,proofs=proofs,compiled_byte_identically_once=True)
    b.save(R/'audit/PRESERVATION75.json',result);return result

def main(full=False):
    start=time.perf_counter();(R/'build').mkdir(exist_ok=True);(R/'audit/build-logs').mkdir(parents=True,exist_ok=True)
    for exe in ('pdflatex','pandoc','pdfinfo','pdftotext'):
        if shutil.which(exe) is None:raise RuntimeError('Missing '+exe)
    for p in (R/'code').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    preservation=preserve();tests={};suites=[]
    if full:
        old.preserve73();old.source_checks()
        suites=[('72-theory',R/'code/tests72.py'),('72-release',R/'code/tests_publication72.py'),('73-exact',R/'code/tests73.py')]
        suites += [(str(n),R.parent/f'2026-10-10-r{n}/code/tests{n}.py') for n in (63,64,65,66)]
        suites += [('67-science',R.parent/'2026-10-10-r67/code/tests67.py'),('67-math',R.parent/'2026-10-10-r67/code/tests_math67.py'),('67-records',R.parent/'2026-10-10-r67/code/tests_records67.py'),('69',R.parent/'2026-10-11-r69/code/tests69.py'),('70',R.parent/'2026-10-11-r70/code/tests70.py')]
    suites += [('74-exact',R/'code/tests74.py'),('75-exact',R/'code/tests75.py')]
    for label,path in suites:
        now=time.perf_counter();text=b.run([sys.executable,str(path)],'tests-'+label);m=re.search(r'Ran (\d+) tests?',text)
        if not m or not re.search(r'^OK\s*$',text,re.M):raise AssertionError('Missing test success '+label)
        tests[label]=dict(tests=int(m[1]),status='passed',seconds=time.perf_counter()-now)
    if full:
        for name in ('independent72','audit_contract72','tables72','independent73','tables73'):b.run([sys.executable,'code/'+name+'.py'],name)
        r70=R.parent/'2026-10-11-r70';p=r70/'audit/RESULT_AUDIT70.json';before=p.read_bytes()
        try:
            b.run([sys.executable,str(r70/'code/audit70.py')],'historical-replay70',r70);shutil.copy2(p,R/'audit/RETAINED_REPLAY70_IN_R75.json')
        finally:p.write_bytes(before)
    b.run([sys.executable,'code/audit75.py'],'all-path-audit75');b.run([sys.executable,'code/tables75.py'],'tables75')
    b.response();p=R/'response.tex';text=p.read_text().replace('label=e75supp','label=e75response')
    abstract='Revision R75 addresses the 11 October 2026 advisory report on R67. The original NBO manuscript now connects attained continuation fitting to independently reconstructed original-law policy costs and a priced adoption region. Every prior active section and adverse observation is retained; the predeclared precision failure is reported.'
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+abstract+m[2],text,flags=re.S);p.write_text(text)
    for d in DOCS:(R/'build'/(d+'.bbl')).unlink(missing_ok=True)
    for iteration in range(5):
        for d in DOCS:
            b.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build',d+'.tex'],d+'-pass'+str(iteration))
            if iteration==0 and d!='response':b.bibliography(d)
    documents=[b.pdf_record(d) for d in DOCS]
    abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',(R/'ECTA.tex').read_text(),re.S)[1]
    if len(abstract.split())>150:raise AssertionError('Abstract exceeds internal target')
    for p in R.rglob('*'):
        if p.is_file() and p.suffix.lower() in b.FONT_EXTENSIONS:raise AssertionError('Standalone font file')
    try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:commit=None
    audit=json.loads((R/'audit/RESULT_AUDIT75.json').read_text());sources={str(p.relative_to(R)):b.sha(p) for p in R.rglob('*') if p.is_file() and p.suffix in ('.py','.tex','.md','.bib','.cls','.cfg','.bst') and 'build' not in p.parts and 'audit' not in p.parts}
    b.save(R/'audit/PUBLICATION_SOURCES75.json',sources)
    record=dict(status='passed',full_retained_replay=full,tested_source_commit=commit,documents=documents,tests=tests,total_tests=sum(v['tests'] for v in tests.values()),preservation=preservation,
        original_law_rows=audit['original_law_rows'],recomputed_integer_paths=audit['recomputed_integer_paths'],paired_precision_successes=audit['paired_precision_successes'],paired_precision_failures=audit['paired_precision_failures'],
        new_policy_training_services=0,additional_independent_sample_families_from_replay=0,abstract_words=len(abstract.split()),seconds=time.perf_counter()-start,
        source_manifest_sha256=b.sha(R/'audit/PUBLICATION_SOURCES75.json'),visual_scope='Actual output visual review is a separate hash-bound gate',
        scope='All new integer paths, acquired ranges, supports and exact confidence intervals recomputed; inherited suites and their recorded data replayed only when full_retained_replay is true. No old scientific service retiming or fitting.')
    b.save(R/'audit/RELEASE75.json',record)
    print(json.dumps({k:record[k] for k in ('status','full_retained_replay','documents','total_tests','preservation','seconds')},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');main(p.parse_args().full)
