"""Generate evidence tables, compile the Econometrica documents, verify provenance."""
from pathlib import Path
from decimal import Decimal,ROUND_CEILING
import hashlib,json,re,subprocess,sys,os,tarfile,platform
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r21'
BASE='6951c3b01b5102ef3d743a6ab14f9cc595b08804'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def rnd(x,places=3):return str(Decimal.from_float(float(x)).quantize(Decimal(10)**(-places),rounding=ROUND_CEILING))
def tables():
 d=read(REV/'results/continuum_audit.json')
 ss=[r'\begin{table}[htbp]\centering\small',r'\caption{First retained $.005$ hit on $K$. Generation and checking are measured seconds; shared-upper and additional publication audits are charged separately in the text.}',r'\setlength{\tabcolsep}{3pt}\begin{tabular}{lrrrrr}\toprule',r'Method & Budget & Generation & Checking & Sum & RSS (KiB) \\ \midrule']
 for s in d['seeds']:
  r=[r for r in s['frontier'] if r['tolerance']==.005][0]
  ss.append(f"Seed {s['seed']} & {r['step']} & {rnd(r['generation_seconds'])} & {rnd(r['verification_seconds'])} & {rnd(r['generation_plus_verification_seconds'])} & {s['resources']['max_rss_kib']}"+r' \\')
 r=[r for r in d['classical_stochastic']['frontier'] if r['tolerance']==.005][0]
 ss.append(f"Direct & 10 & {rnd(r['generation_seconds'])} & {rnd(r['verification_seconds'])} & {rnd(r['generation_plus_verification_seconds'])} & n.r."+r' \\')
 ss+=[r'\bottomrule\end{tabular}',r'\end{table}']
 (REV/'paper/table_cost.tex').write_text('\n'.join(ss)+'\n')
 ss=[r'\begin{table}[htbp]\centering',r'\caption{Fixed-policy price transport: endpoint bounds uniform over all five neural mixtures and all initial states in $K$. Endpoints bound each entire intervening segment.}',r'\begin{tabular}{rr}\toprule',r'Adjustment price $k$ & Regret upper bound \\ \midrule']
 from fractions import Fraction
 for row in d['fixed_policy_price_transport']['knots']:
  ss.append(str(float(Fraction(row['k'])))+' & '+rnd(row['all_five_K_regret_upper'],8)+r' \\')
 ss+=[r'\bottomrule\end{tabular}',r'\end{table}'];(REV/'paper/table_price.tex').write_text('\n'.join(ss)+'\n')
def escape(text):
 mapping={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
 return ''.join(mapping.get(c,c) for c in text)
def inline(text):
 parts=re.split('(`[^`]+`)',text)
 return ''.join(r'\nolinkurl{'+p[1:-1]+'}' if p.startswith('`') else escape(p) for p in parts)
def response():
 old=(ROOT/'ECTA_R21.tex').read_text().split(r'\begin{document}')[0]
 old=old.replace('Revision R21 --- working manuscript','Revision R21 --- response to referee')
 front=r'''\begin{document}
\begin{frontmatter}
\title{Response to the Referee: Neural Bellman Operators}
\runtitle{Neural Bellman Operators: Response}
\begin{aug}
\author[id=au1,addressref={add1}]{\fnms{Qian}~\snm{QI}\ead[label=e1]{qiqian@pku.edu.cn}}
\address[id=add1]{\orgname{Peking University}}
\end{aug}
\begin{abstract}
This response addresses the R18 report and the further R21 intermediate-snapshot report, and distinguishes the new policy-sensitive continuum results from outstanding whole-domain objectives. The accompanying manuscript, supplement, and reproducible evidence retain all prior substantive material.
\end{abstract}
\end{frontmatter}
'''
 out=[]
 for para in ((REV/'RESPONSE_TO_R18.md').read_text()+'\n\n'+(REV/'RESPONSE_TO_R21_SNAPSHOT.md').read_text()).split('\n\n'):
  if para.startswith('# '):continue
  if para.startswith('## '):out.append('\\section{'+inline(para[3:])+'}')
  else:out.append(inline(para.replace('\n',' '))+'\n')
 (ROOT/'RESPONSE_R21.tex').write_text(old+front+'\n'.join(out)+'\n\\end{document}\n')
def preservation():
 p=REV/'INHERITED_SHA256.json'
 if not p.exists():
  proc=subprocess.Popen(['git','archive',BASE],cwd=ROOT,stdout=subprocess.PIPE)
  manifest={}
  with tarfile.open(fileobj=proc.stdout,mode='r|') as t:
   for item in t:
    if item.isfile():manifest[item.name]=hashlib.sha256(t.extractfile(item).read()).hexdigest()
  assert proc.wait()==0;save(p,manifest)
 manifest=read(p);assert len(manifest)==3934
 archived=REV/'history/REVISION_INDEX_before_R21.md'
 assert sha(archived)==manifest['REVISION_INDEX.md']
 assert sha(ROOT/'REVISION_INDEX.md')=='6bfb750a3236b15eff194827e27acc36f3a62b224e05ab422768ab4e0f5d14e1'
 bad=[name for name,digest in manifest.items() if name!='REVISION_INDEX.md' and (not (ROOT/name).is_file() or sha(ROOT/name)!=digest)]
 assert not bad,('Inherited changes',bad[:20])
 return {'status':'PASS','base_commit':BASE,'files_checked':3934,'original_paths_byte_identical':3933,'intentional_navigation_index_update':1,'original_index_archived_byte_identical':str(archived.relative_to(ROOT)),'unpreserved_or_deleted':0}
def main():
 tables();response();preserved=preservation();logs=REV/'build_logs';logs.mkdir(exist_ok=True)
 validation={'historical_preservation':preserved,'documents':[]}
 for name in ['ECTA_R21','SUPP_R21','RESPONSE_R21']:
  for i in range(3):
   proc=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'],cwd=ROOT,text=True,capture_output=True)
   (logs/f'{name}_pass{i+1}.txt').write_text(proc.stdout+proc.stderr)
   if proc.returncode:raise RuntimeError(f'{name} pass {i+1}: '+proc.stdout[-2500:])
  text=(ROOT/(name+'.log')).read_text(errors='replace')
  undefined=[l for l in text.splitlines() if ('undefined' in l.lower() and ('reference' in l.lower() or 'citation' in l.lower()))]
  over=[float(x) for x in re.findall(r'Overfull \\hbox \(([0-9.]+)pt too wide\)',text)]
  assert not undefined,(name,undefined)
  assert max(over,default=0)<3,(name,'overfull',max(over))
  inf=subprocess.check_output(['pdfinfo',str(ROOT/(name+'.pdf'))],text=True)
  pages=int(re.search(r'Pages:\s+(\d+)',inf)[1])
  validation['documents'].append({'file':name+'.pdf','pages':pages,'sha256':sha(ROOT/(name+'.pdf')),'undefined_references_or_citations':0,'max_overfull_hbox_pt':max(over,default=0)})
 save(logs/'pdf_validation.json',validation)
 print(json.dumps(validation,indent=2))
if __name__=='__main__':main()
