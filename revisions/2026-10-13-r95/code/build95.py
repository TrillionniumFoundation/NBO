"""Compile current sources, never relabel inherited PDFs."""
from pathlib import Path
import json,os,subprocess,time,hashlib,re,sys,shutil,argparse
R=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--audit-dir',default='audit/current-build95');args=parser.parse_args()
B=R/'build';A=(R/args.audit_dir).resolve()
if not A.is_relative_to(R):parser.error('Audit directory must be inside this revision')
B.mkdir(exist_ok=True);A.mkdir(parents=True,exist_ok=True)
start=time.perf_counter();runs=[]
def run(cmd,name):
 p=subprocess.run(cmd,cwd=R,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (A/(name+'.log')).write_text(p.stdout);runs.append({'command':cmd,'returncode':p.returncode,'log':str((A/(name+'.log')).relative_to(R))})
 if p.returncode:raise RuntimeError('Build failed: '+name+'\n'+p.stdout[-4000:])
try:
 run(['pandoc','response.md','-f','markdown','-t','latex','-o','build/response-body.tex'],'response-convert')
 for n in range(4):
  for doc in ('ECTA','supp','appendix','response'):
   run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory=build',doc+'.tex'],doc+'-'+str(n))
   if n==0 and doc!='response':run([shutil.which('bibtex') or shutil.which('bibtex.original') or shutil.which('bibtex8') or 'bibtex','build/'+doc],doc+'-bibtex')
 record={}
 for doc in ('ECTA','supp','appendix','response'):
  p=B/(doc+'.pdf');info=subprocess.check_output(['pdfinfo',str(p)],text=True)
  run(['pdftotext','-layout',str(p),str(B/(doc+'.txt'))],doc+'-text')
  log=(B/(doc+'.log')).read_text();record[doc]={'pages':int(re.search(r'Pages:\s+(\d+)',info).group(1)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'unresolved_references':bool(re.search(r'(Reference .*undefined|Citation .*undefined|There were undefined)',log)),'overfull_hbox':re.findall(r'Overfull \\hbox \(([^)]*)\)',log)}
 result={'status':'compiled','documents':record,'seconds':time.perf_counter()-start,'commands':runs}
except Exception as e:
 result={'status':'failed','error':str(e),'commands':runs}
(A/'BUILD95.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
sys.exit(0 if result['status']=='compiled' else 1)
