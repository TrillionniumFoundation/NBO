"""Materialize and build the R39 review object from immutable deposited inputs.

No scientific service is rerun. audit.py checks frozen source/result hashes and
performs only the new endpoint verification. Run from any working directory.
"""
from pathlib import Path
import json,re,hashlib,shutil,subprocess,os,sys,math
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
OLD=ROOT/'revisions/2026-10-07-r37';REL=str(R.relative_to(ROOT))
INP=re.compile(r'\\input\{([^}]+)\}')
LABEL=re.compile(r'\\label\{([^}]+)\}')
DOCS=['applications','supp','ECTA','response']
ALLDOCS=['ECTA','supp','applications','historical_article','historical_supplement','response']
ledger={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):
 p=R/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def texnum(x):
 s=f'{x:.3g}'
 if 'e' in s:
  a,b=s.split('e');return '$'+a+r'\times10^{'+str(int(b))+'}$'
 return s

def table(label,caption,columns,rows,align,notes=''):
 return '\n'.join([r'\begin{table}[htbp]',r'\centering\small\setlength{\tabcolsep}{5pt}',r'\caption{'+caption+'}'+r'\label{'+label+'}',r'\begin{tabular}{'+align+'}',r'\toprule',' & '.join(columns)+r'\\',r'\midrule',*[' & '.join(row)+r'\\' for row in rows],r'\bottomrule',r'\end{tabular}',r'\par\smallskip\begin{minipage}{.96\linewidth}\footnotesize '+notes+r'\end{minipage}',r'\end{table}'])+'\n'

def tables():
 a=json.loads((R/'audit/R39_AUDIT.json').read_text());g=a['groups']
 get=lambda kind,name,method='':next(v for v in g if (v['kind'],v['name'],v['method'])==(kind,name,method))
 names={'fixed64-uncached':'Fixed64, rebuilt','fixed64-cached':'Fixed64, cached','adaptive-uncached':'Adaptive, rebuilt','adaptive-cached':'Adaptive, cached','tuned-cached':'Tuned native, cached','structural':'Structural'}
 rows=[]
 for method,name in names.items():
  v=get('policy','accuracy-0.0001',method);c=v['counts']
  rows.append([name,f"{v['service_seconds_median']:.3f}",f"[{v['service_seconds_min']:.3f}, {v['service_seconds_max']:.3f}]",str(c['updates']),str(c['inverse_builds']),texnum(v['policy_gap_upper'])])
 write('manuscript/factorial_table.tex',table('tab:r39factorial','Precision and caching at a common policy target', ['Method','Median (s)','Range (s)','Updates','Builds','Loss bound'],rows,'lrrrrr',r'$d=2$, $T=4$, target $10^{-4}$. Three isolated complete-service clocks per object. Builds count target inverses, not actor solves. All recorded failed checks and tuning are charged.'))
 rows=[]
 for eps in [1e-2,1e-4,1e-6,1e-8,1e-10]:
  v=get('policy','accuracy-'+str(eps),'adaptive-cached');f=get('policy','accuracy-'+str(eps),'fixed64-cached');s=get('policy','accuracy-'+str(eps),'structural')
  rows.append([texnum(eps),texnum(v['policy_gap_upper']),texnum(v['policy_gap_upper']/eps),f"{v['service_seconds_median']:.3f}",f"{f['service_seconds_median']:.3f}",f"{s['service_seconds_median']:.3f}"])
 write('manuscript/accuracy_table.tex',table('tab:r39accuracy','First certified policy across accuracy targets',['Target','Adaptive bound','Bound/target','Adaptive (s)','Fixed64 (s)','Structural (s)'],rows,'rrrrrr','Factor methods use caching. Times are medians; complete dispersion and all methods appear in the supplement. Discrete oversolving is displayed, not suppressed.'))
 rows=[]
 for price,theta in [(1.,0.),(1.,1.),(4.,0.),(4.,1.)]:
  n=get('neural',f'neural-{price}-{theta}');s=get('nonlinear',f'capital-{price}-{theta}')
  rows.append([f'{price:.0f}',f'{theta:.0f}',f"{n['policy_gap_upper']:.4f}",f"{s['policy_gap_upper']:.4f}",f"{n['service_seconds_median']:.3f}",f"{s['service_seconds_median']:.3f}"])
 write('manuscript/nonlinear_table.tex',table('tab:r39nonlinear','Nonlinear capital: policy bounds and complete work',['Price','Risk','Neural bound','Spline bound','Neural (s)','Spline (s)'],rows,'rrrrrr',r'$T=4$, $N=256$, $A=128$. Cost includes reference construction and, for neural services, all fitting and verification. Price-four services also include construction and evaluation of the old rule. Bounds are in model cost units.'))
 rows=[]
 for theta in [0.,1.]:
  v=get('neural',f'neural-4.0-{theta}');c=v['counterfactual']
  for i,x in enumerate(v['own_policy_values']['states']):
   lower=math.floor(c['improvement_lower'][i]*1e6)/1e6;upper=math.ceil(c['improvement_upper'][i]*1e6)/1e6
   rows.append([f'{theta:.0f}',str(x),f"{c['old_actions'][i]:.5f}",f"{v['initial_actions'][i]:.5f}",f'{lower:.6f}',f'{upper:.6f}'])
 write('manuscript/economic_table.tex',table('tab:r39economic','Cost saved by reoptimization after the investment-price change',['Risk','Capital','Old action','New action','Gain lower','Gain upper'],rows,'rrrrrr','Old: conventional rule constructed at price one, held fixed at price four. New: neural-selected rule at price four. Gains compare both rules under the new price. Displayed gain endpoints are rounded outward to six decimals; action entries are descriptive.'))
 lines=[r'\section{Complete factorial and timing ledger}\label{sec:r39ledger}',r'The following entries summarize all 96 quadratic economy--method objects. Each has three isolated repetitions. Times are complete-service seconds; the range gives the observed minimum and maximum. $U$ counts updates, $B$ target-inverse builds and $F$ failed policy checks in the final tuning trial. The machine-readable audit and original records additionally preserve all tuning trials, actor solves, own-policy evaluation dates, moment margins, native precision, process memory and startup-inclusive clocks. Methods: FR/FC are fixed64 rebuilt/cached; AR/AC are adaptive rebuilt/cached; TC is tuned native cached; S is structural.',r'\begin{longtable}{llrrrrrr}',r'\toprule Object & Method & Median & Min & Max & $U$ & $B$ & $F$\\\midrule\endhead']
 short={'fixed64-uncached':'FR','fixed64-cached':'FC','adaptive-uncached':'AR','adaptive-cached':'AC','tuned-cached':'TC','structural':'S'}
 for v in g:
  if v['kind']!='policy':continue
  c=v['counts'];name=v['name'].replace('accuracy-','tol ').replace('target-','change ').replace('scale-','grid ').replace('moment-margin','moment')
  lines.append(' & '.join([name,short[v['method']],f"{v['service_seconds_median']:.3f}",f"{v['service_seconds_min']:.3f}",f"{v['service_seconds_max']:.3f}",str(c['updates']),str(c['inverse_builds']),str(c['failed_checks'])])+r'\\')
 lines.extend([r'\bottomrule\end{longtable}',r'\subsection{Nonlinear timing dispersion}',r'\begin{tabular}{lrrrr}\toprule Object & Median & Min & Max & Peak RSS (KiB)\\\midrule'])
 for v in g:
  if v['kind']=='policy':continue
  lines.append(' & '.join([v['name'],f"{v['service_seconds_median']:.3f}",f"{v['service_seconds_min']:.3f}",f"{v['service_seconds_max']:.3f}",str(v['peak_process_rss_kib'])])+r'\\')
 lines.extend([r'\bottomrule\end{tabular}',r'\par\medskip The frontier is one complete four-mesh service per repetition. Its internal cumulative construction clocks are distinct from this full-service clock. Peak RSS is process high-water memory, not exclusive algorithm storage.'])
 write('manuscript/complete_ledger.tex','\n'.join(lines)+'\n')

def flatten(path):
 p=ROOT/path;s=p.read_text()
 if not p.is_relative_to(R):
  ledger[path]=sha(p)
  dest=R/'retained/source'/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 return INP.sub(lambda m:'\n% Materialized from '+m[1]+'\n'+flatten(m[1])+'\n',s)

def assemble():
 for n in ('build','audit','retained/source','manuscript'): (R/n).mkdir(parents=True,exist_ok=True)
 # Artifact differs from review-pinned entry points only in the copyright hook.
 for name,expected in [('ECTA.tex','7eb470685079f8d9a761aaca118298a3d9656aad'),('supp.tex','7a01a77fb29f5151296c64ab0eb7246b975cc942')]:
  p=OLD/name;s=p.read_text().replace(r'\g@addto@macro\econsocart@fmadd{\def\copyright@text{Prepared for referee review}}',r'\def\copyright@text{Prepared for referee review}')
  b=s.encode();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==expected
  p.write_text(s)
 subprocess.run([sys.executable,str(R/'code/audit.py')],check=True)
 tables()
 for doc in ('ECTA','supp','applications'):
  source=(OLD/(doc+'.tex')).read_text()
  flatten(str((OLD/(doc+'.tex')).relative_to(ROOT)))
  if doc=='ECTA':
   abstract='''This paper develops Neural Bellman Operators for policy evaluation and feasible improvement in controlled economies. Centered continuation errors and own-policy comparisons connect numerical approximation to full-policy loss. A constructive nonlinear theorem covers continuous states and constrained actions under recursive risk, and an endpoint verifier certifies trained ReLU continuations over all states. A complementary quadratic construction links hidden-factor updates to economic error budgets. Residual enclosures make its mixed-precision implementation verifiable without exact matrix solves. A factorial study separates precision from caching and reports first-pass economic accuracy, failed checks and complete work. In a nonlinear investment economy, independent policy evaluation certifies gains from reoptimization after a change in investment costs. Conventional structural and spline methods remain faster in the reported comparisons. The controlled-diffusion framework and applications to recursive utility, endogenous preferences, temporal selves and games remain part of the same operator theory, with explicit application-specific conditions.'''
   source=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:r'\begin{abstract}'+'\n'+abstract+'\n'+r'\end{abstract}',source,flags=re.S)
   mark=r'\input{revisions/2026-10-07-r37/manuscript/evidence.tex}'
   source=source.replace(mark,r'\input{'+REL+'/manuscript/nonlinear_theory.tex}\n'.replace('\\n','\n')+r'\input{'+REL+'/manuscript/finite_precision.tex}\n'.replace('\\n','\n')+r'\input{'+REL+'/manuscript/evidence_new.tex}\n'.replace('\\n','\n')+mark)
  text=INP.sub(lambda m:flatten(m[1]),source)
  text=text.replace('revisions/2026-10-07-r37/build/',REL+'/build/')
  text=text.replace(r'\begin{document}',r'\makeatletter\def\copyright@text{Prepared for referee review}\makeatother'+'\n'+r'\begin{document}')
  if doc=='ECTA':
   old='The application to which we give a\ncomplete constructive policy certificate is a directly specified recursive\ncapital economy with Gaussian innovations and vector controls. It is an\napplication of this framework, not a change in the paper\'s economic object.'
   new='Two distinct realizations now give constructive policy certificates: a recursive capital economy with Gaussian innovations and vector controls, and a nonlinear compact-state investment economy with constrained actions. The latter admits genuinely nonquadratic continuations and trained ReLU policies. Both are applications of the same operator framework.'
   assert old in text;text=text.replace(old,new)
   intro=r'''\paragraph{Contribution and roadmap.}
Section~\ref{sec:r39nonlinear} proves an all-adapted-policy comparison and a finite nonlinear construction with explicit off-grid and continuous-action allowances. It also supplies a breakpoint verifier for trained hidden units. Section~\ref{sec:r39floating} certifies the entire native matrix step and accounts for evaluation and verification work. Section~\ref{sec:r39evidence} uses the complete factorial design and develops a nonlinear investment-price counterfactual. References below to the eight earlier exact services describe a historical construction audit; their joint adaptive-cached contrast does not identify a precision effect. The new factorial does not establish a stable adaptive timing advantage.
'''
   text=text.replace(new,new+'\n\n'+intro)
   text=text.replace(r'\section{Numerical Evidence and Economic Accuracy}\label{sec:r37evidence}',r'\section{Retained construction evidence and earlier economic comparisons}\label{sec:r37evidence}'+'\n'+r'This section retains the earlier exact-construction evidence and adverse comparisons. The eight-service timing contrast changes precision and caching jointly and is descriptive, not a causal precision comparison. The identified current comparisons are in Section~\ref{sec:r39evidence}.'+'\n')
   old='the adaptive neural implementation improves on its inherited neural\ncomparators in the two specified regimes, whereas the structural procedure\nis faster still.'
   text=text.replace(old,'the earlier adaptive-cached implementation has smaller recorded clocks in its two exact regimes, whereas the structural procedure is faster. The factorial now separates those mechanisms and does not show a stable adaptive-precision advantage.')
   tail=r'''The nonlinear construction establishes the same decision-to-policy logic without quadratic closure. Its endpoint verifier certifies trained continuations on every state, and its investment experiment separates mechanical repricing from independently verified gains due to reoptimization. The structural and spline comparisons remain visible. These results extend the NBO paper through a second constructive economic realization while keeping numerical certification, learned-policy acceptance and empirical work superiority logically distinct.
'''
   text=text.replace(r'\bibliographystyle{ecta-fullname}',tail+'\n'+r'\bibliographystyle{ecta-fullname}')
  if doc=='supp':text=text.replace(r'\bibliographystyle{ecta-fullname}',flatten(REL+'/manuscript/complete_ledger.tex')+'\n'+r'\bibliographystyle{ecta-fullname}')
  bib=re.search(r'\\bibliography\{([^}]+)\}',text)
  if bib:
   parts=[(ROOT/(p+'.bib')).read_text() for p in bib[1].split(',')]
   if doc=='ECTA':parts.append((R/'references_new.bib').read_text())
   write(doc+'_references.bib','\n'.join(parts))
   text=text[:bib.start()]+r'\bibliography{'+REL+'/'+doc+'_references}'+text[bib.end():]
  assert not INP.search(text)
  write(doc+'.tex',text)
 for name in ('econsocart.cls','econsocart.cfg','ecta-fullname.bst'):shutil.copyfile(ROOT/name,R/name)
 for doc in ('historical_article','historical_supplement'):
  for ext in ('.pdf','.aux'):shutil.copyfile(OLD/'build'/(doc+ext),R/'build'/(doc+ext))
 for doc in ('ECTA','supp','applications'):
  shutil.copyfile(OLD/'build'/(doc+'.aux'),R/'build'/(doc+'.aux'))
 subprocess.run(['pandoc',str(R/'response.md'),'-f','markdown','-t','latex','--standalone','-V','geometry:margin=1in','-V','fontsize=11pt','-V','fontfamily=mathpazo','-o',str(R/'response.tex')],check=True)
 old_labels=set().union(*(set(LABEL.findall((ROOT/p).read_text())) for p in ledger))
 current_labels=set().union(*(set(LABEL.findall((R/(doc+'.tex')).read_text())) for doc in ('ECTA','supp','applications')))
 missing=sorted(old_labels-current_labels);assert not missing,missing
 write('audit/PRESERVATION.json',json.dumps(dict(inherited_active_component_sha256=ledger,
  inherited_active_labels=len(old_labels),missing_active_labels=missing,historical_source_deletions=[],historical_source_overwrites=[],root_entrypoint_updates=['ECTA.tex','supp.tex','README.md'],
  source_normalization='R37 entry-point copyright hook normalized to the two reviewed blob hashes before assembly; only runtime copies altered.',
  edited_current_copies=['abstract','introduction scope','historical evidence interpretation','conclusion'],
  active_sources_self_contained=True),indent=2,sort_keys=True)+'\n')
 (ROOT/'ECTA.tex').write_text(r'\input{'+REL+'/ECTA.tex}\n')
 (ROOT/'supp.tex').write_text(r'\input{'+REL+'/supp.tex}\n')
 (ROOT/'README.md').write_text('''# Neural Bellman Operators — R39

Current integrated revision responding to the R37 advisory report. Original topic and complete economic applications retained.

- [Main paper](revisions/2026-10-07-r39/build/ECTA.pdf), [self-contained TeX](revisions/2026-10-07-r39/ECTA.tex).
- [Technical supplement](revisions/2026-10-07-r39/build/supp.pdf).
- [Response](revisions/2026-10-07-r39/response.md), [PDF](revisions/2026-10-07-r39/build/response.pdf).
- [Complete applications](revisions/2026-10-07-r39/build/applications.pdf).
- [Retained historical article](revisions/2026-10-07-r39/build/historical_article.pdf) and [historical supplement](revisions/2026-10-07-r39/build/historical_supplement.pdf).
- [Release audit](revisions/2026-10-07-r39/audit/RELEASE_AUDIT.json) and [new endpoint/source audit](revisions/2026-10-07-r39/audit/R39_AUDIT.json).

R39 adds nonlinear full-policy construction, all-state trained-ReLU verification, native complete-step residual bounds, complete-work accounting and nonlinear investment-price policy comparisons. The 315 R38 economic services are re-audited, not rerun or retimed. The structural and spline baselines remain faster in the stated comparisons. No universal neural work advantage or journal acceptance is claimed.

Build from the repository root with `python revisions/2026-10-07-r39/publication/publish.py build`. Materialized active sources require no historical input expansion. The publication workflow restores pinned artifact dependencies when needed; hashes and source identities are recorded.
''')

def refs():
 for doc in DOCS:
  used=set(LABEL.findall((R/(doc+'.tex')).read_text()))
  for other in ALLDOCS:
   if other==doc:continue
   lines=[];aux=R/'build'/(other+'.aux')
   if aux.exists():
    for line in aux.read_text(errors='replace').splitlines():
     m=re.match(r'\\newlabel\{([^}]+)\}',line)
     if m and m[1] not in used:used.add(m[1]);lines.append(line)
   write('build/'+doc+'_from_'+other+'.aux','\\relax\n'+'\n'.join(lines)+'\n')

def build():
 env=os.environ.copy()
 for k in ('BIBINPUTS','BSTINPUTS','TEXINPUTS'):env[k]=str(R)+':'+str(ROOT)+':'+env.get(k,'')
 for iteration in range(4):
  refs()
  for doc in DOCS:
   with (R/'audit'/f'TEX_{doc}_{iteration}.log').open('w') as out:
    p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory='+str(R/'build'),str(R/(doc+'.tex'))],cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT)
   if p.returncode:raise RuntimeError('LaTeX failed '+doc)
   if iteration==0 and '\\bibdata' in (R/'build'/(doc+'.aux')).read_text():
    with (R/'audit'/('BIB_'+doc+'.log')).open('w') as out:
     p=subprocess.run([shutil.which('bibtex.original') or 'bibtex',str((R/'build'/doc).relative_to(ROOT))],cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT)
    if p.returncode:raise RuntimeError('BibTeX failed '+doc)
 reports=[]
 for doc in DOCS:
  text=(R/'build'/(doc+'.log')).read_text(errors='replace')
  bad=[s for s in text.splitlines() if 'undefined' in s.lower() and ('reference' in s.lower() or 'citation' in s.lower())]
  assert not bad,(doc,bad)
  assert 'There were multiply-defined labels' not in text,doc
  assert 'Missing character:' not in text,doc
  assert 'Overfull \\hbox' not in text and 'Overfull \\vbox' not in text,doc
  pages=re.search(r'Output written on .*?\(([\d\s]+)\s+pages?',text,re.S)
  reports.append(dict(document=doc,pages=int(''.join(pages[1].split())) if pages else None,undefined_references=[],duplicate_labels=False,missing_characters=False,overfull_hboxes=text.count('Overfull \\hbox'),overfull_vboxes=text.count('Overfull \\vbox'),pdf_sha256=sha(R/'build'/(doc+'.pdf'))))
 release=dict(revision='R39',publication_source_commit=os.environ.get('GITHUB_SHA'),
  review_commit='71949aa40c62c960dab824137bed12bb3516ff85',reviewed_commit='9792d3dee69351f672dcc09098422b35207060a7',
  evidence_commit='2bb7a39a16c558da8269becc642b180847b2eb5c',r38_science_freeze='264e02d77ca701f0489a361379cf3f05615aca0f',
  r37_input_artifact=11444691409,r38_input_artifact=11447232117,
  compilation=reports,preservation=json.loads((R/'audit/PRESERVATION.json').read_text()),
  scientific_service_reruns=0,clock_replacements=0,visual_inspection='Separate rendered-page review recorded after build',
  qualification='Numerical and source audit; not independent editorial acceptance')
 write('audit/RELEASE_AUDIT.json',json.dumps(release,indent=2,sort_keys=True)+'\n')
 manifest={str(p.relative_to(ROOT)):sha(p) for p in sorted(R.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='FILES_SHA256.json'}
 write('audit/FILES_SHA256.json',json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 print(json.dumps(reports,indent=2))

if __name__=='__main__':
 mode=sys.argv[1] if len(sys.argv)>1 else 'all'
 if mode in ('all','assemble'):assemble()
 if mode in ('all','build'):build()
