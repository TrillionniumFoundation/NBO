"""Clean current-document build, source identities and fail-closed diagnostics."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys,time
R=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--audit-dir',default='audit97/build')
args=parser.parse_args();B=R/'build';A=(R/args.audit_dir).resolve()
if not A.is_relative_to(R.resolve()) or A.is_relative_to(B.resolve()):
    parser.error('Audit directory must be inside the revision and outside build')
A.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths=list(R.glob('*.tex'))+list(R.glob('*.bib'))+list((R/'sections').glob('*.tex'))+list((R/'tables').glob('*.tex'))+list((R/'new').glob('*.tex'))+list((R/'new').glob('*.py'))+[R/'response.md',R/'econsocart.cls',R/'econsocart.cfg',R/'ecta-fullname.bst',Path(__file__)]
result=dict(status='started',source_sha256={str(p.relative_to(R)):sha(p) for p in paths},commands=[],documents={})
start=time.perf_counter()
def save():
    result['seconds']=time.perf_counter()-start
    (A/'BUILD97.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
def run(cmd,name):
    t=time.perf_counter();p=subprocess.run(cmd,cwd=R,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log=A/(name+'.log');log.write_text(p.stdout)
    result['commands'].append(dict(command=cmd,returncode=p.returncode,seconds=time.perf_counter()-t,log=str(log.relative_to(R))));save()
    if p.returncode:raise RuntimeError('Build failed: '+name+'\n'+p.stdout[-3000:])
    return p.stdout
try:
    for tool in ('pdflatex','bibtex','pandoc','pdftotext','pdfinfo'):
        if shutil.which(tool) is None:raise RuntimeError('Missing tool: '+tool)
        ver=subprocess.run([tool,'-v' if tool in ('pdfinfo','pdftotext') else '--version'],text=True,capture_output=True)
        result.setdefault('tool_versions',{})[tool]=(ver.stdout+ver.stderr).splitlines()[:2]
    if B.exists():shutil.rmtree(B)
    B.mkdir()
    for n in range(4):
        for doc in ('ECTA','supp','appendix'):
            run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory=build',doc+'.tex'],doc+'-'+str(n))
            if n==0:run(['bibtex','build/'+doc],doc+'-bibtex')
    labels={}
    for doc in ('ECTA','supp','appendix'):
        for key,num in re.findall(r'\\newlabel\{([^{}]+)\}\{\{([^{}]*)\}',(B/(doc+'.aux')).read_text()):
            labels[key]=num
    text=(R/'response.md').read_text()
    text=re.sub(r'`([0-9a-f]{40,64})`',lambda m:r'\path{'+m[1]+'}',text)
    def resolve(m):
        if m[2] not in labels:raise RuntimeError('Unresolved response reference: '+m[2])
        return m[1]+' '+labels[m[2]]
    text=re.sub(r'\[\[([A-Za-z][^\[\]]+?)\s+([^\s\[\]]+)\]\]',resolve,text)
    (B/'response-resolved.md').write_text(text)
    run(['pandoc','build/response-resolved.md','-f','markdown','-t','latex','-o','build/response-body.tex'],'response-convert')
    for n in range(2):
        run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory=build','response.tex'],'response-'+str(n))
    bad=False
    for doc in ('ECTA','supp','appendix','response'):
        p=B/(doc+'.pdf');info=run(['pdfinfo',str(p)],doc+'-info')
        run(['pdftotext','-layout',str(p),str(B/(doc+'.txt'))],doc+'-text')
        log=(B/(doc+'.log')).read_text();txt=(B/(doc+'.txt')).read_text()
        unresolved=bool(re.search(r'(Reference .*undefined|Citation .*undefined|There were undefined|There were multiply-defined|Rerun to get cross-references right)',log))
        unresolved|=bool(re.search(r'(Theorem|Proposition|Section|Table|Corollary)\s+\?\?',txt))
        overflow=re.findall(r'Overfull \\hbox \(([^)]*)\)',log)
        result['documents'][doc]=dict(pages=int(re.search(r'Pages:\s+(\d+)',info)[1]),sha256=sha(p),bytes=p.stat().st_size,unresolved_references=unresolved,overfull_hbox=overflow)
        bad|=unresolved or bool(overflow)
    result['status']='compiled-with-diagnostics' if bad else 'compiled'
except Exception as e:
    result.update(status='failed',error=str(e))
save();print(json.dumps({'status':result['status'],'documents':result['documents'],'error':result.get('error')},indent=2),flush=True)
sys.exit(0 if result['status']=='compiled' else 1)
