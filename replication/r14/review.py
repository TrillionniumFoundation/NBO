"""Read-only, one-command review of the deposited R14 manuscript and evidence.

Default: verify the frozen file manifest, independently reconstruct science,
check generated tables, compile all four documents in a temporary directory,
and compare their extracted text with the deposited PDFs. No producer, target
constructor, witness generator, or training routine is called. The optional
--receipt writes only to a user-selected path outside this repository.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,shutil,subprocess,sys,tempfile,time
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
REL=Path('revisions/2026-09-19-r14-referee-response')
DOCS=('ECTA_R14','SUPP_R14','RESPONSE_R14','COMPENDIUM_R14')
MANIFEST=ROOT/REL/'release_manifest.json'
def digest(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def require(ok:bool,message:str)->None:
    if not ok:raise ValueError(message)
def integrity()->dict:
    m=json.loads(MANIFEST.read_text())
    require(m['schema']=='nbo-r14-release-v1','unknown release schema')
    for name,sha in m['files'].items():
        rel=Path(name)
        require(not rel.is_absolute() and '..' not in rel.parts,'unsafe manifest path')
        path=ROOT/rel
        require(path.is_file() and digest(path)==sha,'release hash mismatch: '+name)
    return m

def run(command:list[str],cwd:Path,env:dict|None=None)->str:
    p=subprocess.run(command,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if p.returncode:raise RuntimeError('Command failed: '+' '.join(command)+'\n'+p.stdout[-18000:])
    return p.stdout

def compile_documents(base:Path,log_dir:Path|None=None)->dict:
    """Compile ordered wrappers. The supplement resolves the main .aux file."""
    import fitz
    out=base/REL;out.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env['SOURCE_DATE_EPOCH']='1789776000';env['FORCE_SOURCE_DATE']='1'
    report={}
    for name in DOCS:
        cmd=['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error','-file-line-error','-outdir='+str(REL),name+'.tex']
        text=run(cmd,base,env)
        log=(out/(name+'.log')).read_text(errors='replace')
        errors=[s for s in ('There were undefined references','undefined citations','Overfull \\hbox','Overfull \\vbox') if s in log]
        require(not errors,'unresolved manuscript layout/reference issue: '+name+': '+str(errors))
        with fitz.open(out/(name+'.pdf')) as pdf:
            require(len(pdf)>0,'empty PDF '+name)
            pages=len(pdf);extracted='\n'.join(p.get_text(sort=True) for p in pdf)
        report[name]={'pages':pages,'text_sha256':hashlib.sha256(re.sub(r'\s+','',extracted).encode()).hexdigest(),'pdf_sha256':digest(out/(name+'.pdf'))}
        if log_dir:
            log_dir.mkdir(parents=True,exist_ok=True)
            (log_dir/(name+'-build.log')).write_text(text+'\n'+log)
    return report

def copy_build_inputs(destination:Path)->None:
    paths=set()
    for name in DOCS:paths.add(Path(name+'.tex'))
    for pattern in ('*.cls','*.cfg','*.sty','*.bst'):
        paths.update(p.relative_to(ROOT) for p in ROOT.glob(pattern))
    paths.add(Path('revisions/2026-09-17-r9-participation-permissions/paper/preamble.tex'))
    paths.update(p.relative_to(ROOT) for p in (ROOT/REL/'paper').glob('*.tex'))
    paths.update(p.relative_to(ROOT) for p in (ROOT/REL/'historical').glob('*.pdf'))
    for rel in paths:
        target=destination/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,target)

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__)
    mode=ap.add_mutually_exclusive_group();mode.add_argument('--integrity-only',action='store_true');mode.add_argument('--compile-only',action='store_true')
    ap.add_argument('--receipt',type=Path);args=ap.parse_args();start=time.perf_counter()
    if args.receipt:
        require(not args.receipt.resolve().is_relative_to(ROOT),'review receipt must be outside the repository')
    manifest=integrity();before={name:digest(ROOT/name) for name in manifest['files']}
    output=run([sys.executable,'replication/r14/build_tables.py','--check'],ROOT);print(output.strip(),flush=True)
    result={'schema':'nbo-r14-review-v1','release_manifest_sha256':digest(MANIFEST),'checked_files':len(before),'mode':'integrity-only' if args.integrity_only else ('compile-only' if args.compile_only else 'full'),'science':None,'documents':None}
    with tempfile.TemporaryDirectory(prefix='nbo-r14-review-') as tmp:
        temp=Path(tmp)
        if not args.integrity_only and not args.compile_only:
            receipt=temp/'science.json'
            print('Independently reconstructing deposited scientific objects.',flush=True)
            run([sys.executable,'replication/r14/verify.py','--receipt',str(receipt)],ROOT)
            result['science']=json.loads(receipt.read_text());require(result['science']['all_passed'],'scientific check failed')
        if not args.integrity_only:
            copy_build_inputs(temp)
            report=compile_documents(temp)
            import fitz
            for name,item in report.items():
                with fitz.open(ROOT/REL/(name+'.pdf')) as pdf:
                    text='\n'.join(p.get_text(sort=True) for p in pdf);pages=len(pdf)
                expected=hashlib.sha256(re.sub(r'\s+','',text).encode()).hexdigest()
                require(item['text_sha256']==expected and item['pages']==pages,'rebuilt PDF content differs: '+name)
                item['deposited_pdf_sha256']=digest(ROOT/REL/(name+'.pdf'))
            result['documents']=report
        result['negative_tests']=json.loads(run([sys.executable,'-O','replication/r14/verify.py','--fixtures-only'],ROOT))
    for name,sha in before.items():require(digest(ROOT/name)==sha,'review modified scientific or manuscript input: '+name)
    require(digest(MANIFEST)==result['release_manifest_sha256'],'review modified release manifest')
    result.update(read_only=True,all_passed=True,elapsed_seconds=time.perf_counter()-start)
    if args.receipt:
        args.receipt.parent.mkdir(parents=True,exist_ok=True);args.receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
