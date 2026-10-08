"""Build four active documents from self-contained sources; fail on bad references."""
from pathlib import Path
import os,re,json,hashlib,shutil,subprocess
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
DOCS=['applications','supp','ECTA','response'];ALL=['ECTA','supp','applications','historical_article','historical_supplement','response']
LABEL=re.compile(r'\\label\{([^}]+)\}')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def manifest():
 m={str(p.relative_to(ROOT)):sha(p) for p in sorted(R.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in ['FILES_SHA256.json','STUDY_PID']}
 (R/'audit/FILES_SHA256.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
def refs():
 for doc in DOCS:
  used=set(LABEL.findall((R/(doc+'.tex')).read_text()))
  for other in ALL:
   if other==doc:continue
   lines=[];aux=R/'build'/(other+'.aux')
   if aux.exists():
    for line in aux.read_text(errors='replace').splitlines():
     m=re.match(r'\\newlabel\{([^}]+)\}',line)
     if m and m[1] not in used:used.add(m[1]);lines.append(line)
   (R/'build'/(doc+'_from_'+other+'.aux')).write_text('\\relax\n'+'\n'.join(lines)+'\n')
def main():
 env=os.environ.copy()
 for k in ['TEXINPUTS','BIBINPUTS','BSTINPUTS']:env[k]=str(R)+':'+str(ROOT)+':'+env.get(k,'')
 for iteration in range(4):
  refs()
  for doc in DOCS:
   log=R/'audit'/f'TEX_{doc}_{iteration}.log'
   with log.open('w') as f:p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory='+str(R/'build'),str(R/(doc+'.tex'))],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
   if p.returncode:raise RuntimeError('LaTeX '+doc+' failed; inspect '+str(log))
   if iteration==0 and '\\bibdata' in (R/'build'/(doc+'.aux')).read_text():
    with (R/'audit'/('BIB_'+doc+'.log')).open('w') as f:p=subprocess.run([shutil.which('bibtex.original') or 'bibtex',str((R/'build'/doc).relative_to(ROOT))],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
    if p.returncode:raise RuntimeError('BibTeX '+doc+' failed')
 reports=[]
 for doc in DOCS:
  txt=(R/'build'/(doc+'.log')).read_text(errors='replace')
  bad=[line for line in txt.splitlines() if ('undefined' in line.lower() and ('reference' in line.lower() or 'citation' in line.lower())) or any(x in line for x in ['multiply-defined labels','Missing character:','Overfull \\hbox','Overfull \\vbox'])]
  assert not bad,(doc,bad)
  match=re.search(r'Output written on .*?\(([\d\s]+)\s+pages?',txt,re.S)
  reports.append(dict(document=doc,pages=int(''.join(match[1].split())) if match else None,pdf_sha256=sha(R/'build'/(doc+'.pdf')),undefined_references=[],duplicate_labels=False,missing_characters=False,overfull_boxes=0))
 release=dict(revision='R41',publication_source_commit=os.environ.get('GITHUB_SHA'),publication_run_id=os.environ.get('GITHUB_RUN_ID'),review_commit='c95c0771c468db7d98ee9746a6bf5972de242569',reviewed_manuscript_commit='f472a7c21f2f9db5285f1bf7746edf2d9463638e',development_parent='a4ec3525a7184e2d2fe04953d131fbfd725ac941',compilation=reports,preservation=json.loads((R/'audit/PRESERVATION.json').read_text()),result_audit=json.loads((R/'audit/RESULT_AUDIT.json').read_text()),qualification='Source and numerical audit, not independent editorial approval; comparative high-dimensional efficiency not established')
 (R/'audit/RELEASE_AUDIT.json').write_text(json.dumps(release,indent=2,sort_keys=True)+'\n');manifest();print(json.dumps(reports,indent=2))
if __name__=='__main__':main()
