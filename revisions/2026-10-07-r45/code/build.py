"""Build and audit an R45 referee package without altering frozen services."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1]
OLD=Path(os.environ.get('NBO_R44',str(R.parent/'2026-10-07-r44')))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,log,cwd=R,env=None):
 with log.open('w') as f:p=subprocess.run(args,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError('Failed: '+str(args)+'; log '+str(log))
def main():
 for n in ('build','audit','tables'):(R/n).mkdir(exist_ok=True)
 run([sys.executable,str(R/'code/assemble.py')],R/'audit/assemble.log')
 run([sys.executable,str(R/'code/make_tables.py')],R/'audit/tables.log')
 run([sys.executable,str(R/'code/tests.py')],R/'audit/tests.log')
 inherited_env=os.environ.copy()
 inherited_env['PYTHONPATH']=os.pathsep.join([str(R/'preserved/R41/code'),str(R/'preserved/R41/vendor/r38/code'),inherited_env.get('PYTHONPATH','')])
 run([sys.executable,str(OLD/'code/tests.py')],R/'audit/INHERITED_TESTS.log',env=inherited_env)
 inherited=json.loads((OLD/'audit/TEST_AUDIT.json').read_text())
 (R/'audit/INHERITED_TESTS.json').write_text(json.dumps(inherited,indent=2)+'\n')
 body=subprocess.check_output(['pandoc','-f','gfm','-t','latex',str(R/'response.md')],text=True)
 body=re.sub(r'\\texttt\{([^{}]*)\}',lambda m:r'\nolinkurl{'+m[1].replace(r'\_','_')+'}',body)
 front=r'''\documentclass[ecta,nameyear,draft]{econsocart}
\input{preamble}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\begin{document}
\begin{frontmatter}\title{Response to the Referee: Neural Bellman Operators}
\runtitle{Neural Bellman Operators: Response}
\begin{aug}\author[id=au1,addressref={add1}]{\fnms{Qian}~\snm{QI}}\address[id=add1]{Peking University}\end{aug}
\end{frontmatter}
'''
 (R/'response.tex').write_text(front+body+'\n\\end{document}\n')
 env=os.environ.copy()
 for key in ('TEXINPUTS','BIBINPUTS','BSTINPUTS'):env[key]=str(R)+':'+env.get(key,'')
 for iteration in range(3):
  for name in ('ECTA','supp','response'):
   run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory='+str(R/'build'),str(R/(name+'.tex'))],R/'audit'/f'tex-{name}-{iteration}.log',env=env)
   if iteration==0 and r'\bibdata' in (R/'build'/(name+'.aux')).read_text():
    run([shutil.which('bibtex.original') or 'bibtex','build/'+name],R/'audit'/f'bib-{name}.log',env=env)
 reports=[]
 for name in ('ECTA','supp','response'):
  text=(R/'build'/(name+'.log')).read_text(errors='replace')
  bad=[l for l in text.splitlines() if ('undefined' in l.lower() and ('reference' in l.lower() or 'citation' in l.lower())) or any(x in l for x in ('multiply-defined labels','Missing character:','Overfull \\hbox','Overfull \\vbox'))]
  if bad:raise RuntimeError(name+': '+repr(bad))
  m=re.search(r'Output written on .*?\((\d+) pages?',text,re.S)
  reports.append({'document':name,'pages':int(m[1]) if m else None,'pdf_sha256':sha(R/'build'/(name+'.pdf')),'undefined_references':[],'duplicate_labels':False,'overfull_boxes':0})
 release={'revision':'R45','review_baseline':'5d4eca82b5477c4f0305f0f90bf9adc1635ec5de',
  'study_source_commit':'dc071799c1b24e6f55822fe5799732eed3e74f61','study_evidence_commit':'49fdae7214693d21ff4bf313ae41e22cbceb8ece',
  'study_workflow_run':37612422495,'study_artifact_id':11477314888,
  'study_artifact_sha256':'9f071c2f2118fd5cb2dcfde26a8e9eab860d657bc3557882ed15ee67e5dd65a3',
  'publication_source_commit':os.environ.get('GITHUB_SHA','local-build'),'publication_run':os.environ.get('GITHUB_RUN_ID'),
  'compilation':reports,'new_tests':json.loads((R/'audit/NEW_TESTS.json').read_text()),'inherited_tests':inherited,
  'results':json.loads((R/'audit/PUBLICATION_SUMMARY.json').read_text()),
  'scientific_scope':'Constructive theorem and full matched finite catalogue; not neural superiority, a high-dimensional experiment, a calibrated application, or peer/editorial approval.'}
 (R/'audit/RELEASE_AUDIT.json').write_text(json.dumps(release,indent=2,sort_keys=True)+'\n')
 manifest={str(p.relative_to(R)):sha(p) for p in sorted(R.rglob('*')) if p.is_file() and not any(k in p.parts for k in ('__pycache__','publication')) and p.name!='FILES_SHA256.json'}
 (R/'audit/FILES_SHA256.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 print(json.dumps(reports,indent=2))
if __name__=='__main__':main()
