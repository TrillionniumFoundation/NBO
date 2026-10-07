"""Audit the immutable study, materialize tables, and build the current paper."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-07-r41'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def cmd(args,log,cwd=R,env=None):
 with log.open('w') as f:p=subprocess.run(args,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError('Command failed: '+str(args)+'; '+str(log))
def response():
 # Pandoc writes only the body; the journal class controls document style.
 body=subprocess.check_output(['pandoc','-f','gfm','-t','latex',str(R/'response.md')],text=True)
 # Permit line breaks inside source identities; no shrink-to-fit text.
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
def preservation():
 docs={}
 for name in ('ECTA.tex','supp.tex','applications.tex','build/ECTA.pdf','build/supp.pdf','build/applications.pdf'):
  p=OLD/name
  if not p.exists():raise FileNotFoundError(p)
  docs[str(p.relative_to(R.parents[1]))]={'sha256':sha(p)}
  if p.suffix=='.tex':docs[str(p.relative_to(R.parents[1]))]['labels']=re.findall(r'\\label\{([^}]+)\}',p.read_text())
 data={'retained_manuscript_commit':'06a104a8db06b76464165899d817b303cb2aaa01','review_commit':'770ad3a9db05002c0165bf26b58be71d0f1319e1','original_sources':docs,'historical_deletions':[],'historical_overwrites':[],'current_empirical_precedence':'R44 main article; full R42 catalogue and separately labeled R44 diagnostics','relocations':'No source relocation or deletion; complete unchanged R41 files are linked companions.'}
 (R/'audit/PRESERVATION.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
def manifest():
 files={str(p.relative_to(R)):sha(p) for p in sorted(R.rglob('*')) if p.is_file() and not p.is_symlink() and not any(x in p.parts for x in ('__pycache__','input_artifacts','publication')) and p.name!='FILES_SHA256.json' and (p.suffix not in ('.aux','.out','.toc','.blg','.bbl') or 'evidence' in p.parts)}
 (R/'audit/FILES_SHA256.json').write_text(json.dumps(files,indent=2,sort_keys=True)+'\n')
def main():
 (R/'build').mkdir(exist_ok=True);(R/'audit').mkdir(exist_ok=True)
 if not (R/'results/R42_REPLAY.json').exists():cmd([sys.executable,str(R/'code/study.py'),'audit'],R/'audit/replay.log')
 cmd([sys.executable,str(R/'code/tests.py')],R/'audit/tests.log')
 cmd([sys.executable,str(R/'code/make_tables.py')],R/'audit/tables.log')
 response();preservation()
 env=os.environ.copy()
 for key in ('TEXINPUTS','BIBINPUTS','BSTINPUTS'):env[key]=str(R)+':'+str(OLD)+':'+env.get(key,'')
 for iteration in range(3):
  for doc in ('ECTA','supp','response'):
   cmd(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory='+str(R/'build'),str(R/(doc+'.tex'))],R/'audit'/f'tex-{doc}-{iteration}.log',env=env)
   if iteration==0 and r'\bibdata' in (R/'build'/(doc+'.aux')).read_text():
    cmd([shutil.which('bibtex.original') or 'bibtex','build/'+doc],R/'audit'/f'bib-{doc}.log',env=env)
 reports=[]
 for doc in ('ECTA','supp','response'):
  txt=(R/'build'/(doc+'.log')).read_text(errors='replace')
  bad=[l for l in txt.splitlines() if ('undefined' in l.lower() and ('reference' in l.lower() or 'citation' in l.lower())) or any(x in l for x in ('multiply-defined labels','Missing character:','Overfull \\hbox','Overfull \\vbox'))]
  if bad:raise RuntimeError(doc+': '+repr(bad))
  m=re.search(r'Output written on .*?\((\d+) pages?',txt,re.S)
  reports.append({'document':doc,'pages':int(m[1]) if m else None,'pdf_sha256':sha(R/'build'/(doc+'.pdf')),'undefined_references':[],'overfull_boxes':0,'duplicate_labels':False})
 release={'revision':'R44','publication_source_commit':os.environ.get('GITHUB_SHA'),'publication_run_id':os.environ.get('GITHUB_RUN_ID'),'compilation':reports,'tests':json.loads((R/'audit/TEST_AUDIT.json').read_text()),'summary':json.loads((R/'audit/PUBLICATION_SUMMARY.json').read_text()),'qualification':'Manuscript build and numerical/source audit, not editorial approval. New diagnostic clocks are not comparative service timings.'}
 (R/'audit/RELEASE_AUDIT.json').write_text(json.dumps(release,indent=2,sort_keys=True)+'\n');manifest();print(json.dumps(reports,indent=2))
if __name__=='__main__':main()
