"""Compile and audit the complete R19 publication from checked sources.

Produces a release manifest only after every required publication compiles and
all current references resolve. Historical inputs are checked for mutation.
"""
from __future__ import annotations
import hashlib,json,os,re,subprocess,sys,time
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[2];REL='revisions/2026-09-20-r19';R=ROOT/REL
BASE='d15591aff0bed68334cbb205294edfb04297427c';REVIEW='a17c867624e34f1264ff5cba60e51a850026803f'
DOCS=('ECTA_R19','SUPP_R19','RESPONSE_R19','COMPENDIUM_R19')

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def require(x,msg):
    if not x:raise RuntimeError(msg)
def dependencies(path,seen):
    path=path.resolve()
    if path in seen:return
    require(path.is_file(),'missing input '+str(path));seen.add(path)
    for name in re.findall(r'\\(?:input|include)\{([^}]+)\}',path.read_text()):
      if '#' in name:continue
      p=ROOT/name
      if not p.suffix:p=p.with_suffix('.tex')
      dependencies(p,seen)

def main():
    start=time.perf_counter();seen=set();reports=[]
    for name in DOCS:dependencies(ROOT/(name+'.tex'),seen)
    for file,key in (('validation.json','passed'),('final_checks.json','passed'),('inherited_validation.json','all_passed')):
      require(json.loads((ROOT/'replication/r19/output'/file).read_text())[key],file+' is not successful')
    preserved=['replication/r13/canonical','replication/r13/output','replication/r13/extensions','replication/r14','revisions/2026-09-19-r14-referee-response','revisions/2026-09-19-r15-referee-response']
    changed=subprocess.check_output(['git','diff','--name-only',BASE,'--',*preserved],cwd=ROOT,text=True).strip()
    require(not changed,'historical scientific content changed: '+changed)
    for name in DOCS:
      cmd=['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error','-file-line-error','-outdir='+REL,name+'.tex']
      result=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
      logs=R/'build_logs';logs.mkdir(parents=True,exist_ok=True);(logs/(name+'.txt')).write_text(result.stdout)
      if result.returncode:
        print(result.stdout[-18000:]);raise RuntimeError(name+' did not compile')
      log=(R/(name+'.log')).read_text(errors='replace')
      bad=[]
      for pattern in (r'LaTeX Warning: Reference .*?undefined',r'LaTeX Warning: Citation .*?undefined',r'There were undefined references',r'Label .*?multiply defined',r'Undefined control sequence'):
        bad.extend(re.findall(pattern,log,re.S if pattern.startswith('Label ') else 0))
      require(not bad,name+' unresolved references: '+str(bad)[:2000])
      pdf=R/(name+'.pdf');require(pdf.is_file() and pdf.stat().st_size>1000,'empty '+name)
      doc=fitz.open(pdf);text='\n'.join(page.get_text() for page in doc)
      require(len(text)>500 and len(doc)>1,'incomplete publication '+name)
      if name=='ECTA_R19':
        for phrase in ('Institution-dependent minimal information','global response-loss','Brownian','Initial implementation'):
          require(phrase.lower() in text.lower(),name+' missing current argument '+phrase)
      outside=[]
      for page in doc:
        for block in page.get_text('dict')['blocks']:
          if block.get('type')!=0:continue
          for line in block.get('lines',[]):
            for span in line.get('spans',[]):
              x0,y0,x1,y1=span['bbox']
              if x0 < -1 or y0 < -1 or x1>page.rect.width+1 or y1>page.rect.height+1:
                outside.append(dict(page=page.number+1,bbox=list(span['bbox']),text=span['text'][:120]))
      require(not outside,name+' has clipped text '+str(outside[:4]))
      overfull=re.findall(r'Overfull \\hbox \(([^)]+)\).*',log)
      underfull=len(re.findall(r'Underfull \\hbox',log))
      # Render current arguments and dense tables, not a decorative image.
      previews=[]
      if name!='COMPENDIUM_R19':
        selected={0,1,len(doc)-1}
        for phrase in ('Initial implementation in the unchanged','Repeated proposals and complete','continuous-diffusion procurement','Institution-dependent minimal information'):
          for page in doc:
            if phrase.lower() in page.get_text().lower():selected.add(page.number)
        for number in sorted(selected):
          path=R/'preview'/f'{name}-{number+1:03d}.png';path.parent.mkdir(parents=True,exist_ok=True)
          doc[number].get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False).save(path)
          previews.append(str(path.relative_to(ROOT)))
        target=R/'pdf_text'/(name+'.txt');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
      reports.append(dict(name=name,pages=len(doc),bytes=pdf.stat().st_size,sha256=digest(pdf),unresolved_references=[],clipped_text=outside,overfull_hboxes=overfull,underfull_hboxes=underfull,preview=previews))
      print('COMPILED',name,'pages',len(doc),'overfull hboxes',len(overfull),flush=True)
    report=dict(schema='nbo-r19-publication-check-v1',passed=True,documents=reports,
      dependencies=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p)) for p in sorted(seen)],
      historical_scientific_paths_unchanged=preserved,
      source_commit=os.environ.get('R19_SOURCE_COMMIT',subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()),
      workflow_run=os.environ.get('GITHUB_RUN_ID'),python=sys.version,elapsed_seconds=time.perf_counter()-start,
      scope='Clean LaTeX compilation, resolved references, current-text presence, page-boundary clipping checks, preview rendering, source dependency and preservation checks. Programmatic layout checks do not replace substantive referee review.')
    put(R/'build_report.json',report)
    included=[]
    for base in (R,ROOT/'replication/r19'):
      for path in sorted(base.rglob('*')):
        if path.is_file() and path.suffix in ('.tex','.pdf','.json','.md','.py','.png','.txt','.npz') and '__pycache__' not in str(path) and path.name!='release_manifest.json':
          included.append(dict(path=str(path.relative_to(ROOT)),bytes=path.stat().st_size,sha256=digest(path)))
    for name in ('README.md','REVISION_INDEX.md',*(n+'.tex' for n in DOCS)):
      p=ROOT/name;included.append(dict(path=name,bytes=p.stat().st_size,sha256=digest(p)))
    manifest=dict(schema='nbo-r19-release-v1',revision='R19',date='2026-09-20',reviewed_author=BASE,referee_report_commit=REVIEW,
      source_commit=report['source_commit'],workflow_run=report['workflow_run'],
      canonical_manifest_sha256=digest(ROOT/'replication/r13/canonical/manifest.json'),
      entrypoints=[REL+'/'+n+'.pdf' for n in DOCS],files=included,
      checked_receipts=['replication/r19/output/validation.json','replication/r19/output/final_checks.json','replication/r19/output/inherited_validation.json',REL+'/build_report.json'],
      note='The source commit plus the recorded idempotent checker correction reproduces this generated payload. The release branch identifies the final publication commit; no self-referential commit hash is fabricated.',
      unresolved_scientific_extensions=['CRRA diffusion constructor inclusion within the decision budget','High-dimensional end-to-end neural computational advantage'])
    put(R/'release_manifest.json',manifest)
    print(json.dumps(dict(passed=True,documents=reports,source_commit=report['source_commit']),indent=2),flush=True)
if __name__=='__main__':main()
