"""Idempotent editorial integration from immutable R16 roots; no scientific file deletion."""
from pathlib import Path
import hashlib,json,re,subprocess
from response_additions import ADDITIONS
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1]
OLD=ROOT/'revisions/2026-10-04-r16'
BASE='3a5bae12938077002d1619a0dd32be6071e9adab'
HASHES={'ECTA.tex':'a3ed2ba396ab6ea347ce64a4592da119408b8db046c9d66a5b09523adae5a596','supp.tex':'9ee61cd61ac48167d5f33eec0f46d339ce0906ed3760043fc6b0ad81ae57a2d9','README.md':'04a51a763aa9a12cf16c15ad4f60e03dd4c3840b99edcd5375c03edc879171aa','applications.tex':'781904c755a67bd32164e76591adcece6258e8cdab02b6ff4984d338390d768f','response.tex':'c07915e96eb54e516502c12998ab89cc7e3d15ef2c3469f4a2493f8800d568ed'}
def write(name,text):
 p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n')
def replace_once(text,old,new):
 if text.count(old)!=1:raise ValueError('Nonunique editorial anchor: '+old[:100])
 return text.replace(old,new,1)
def assemble():
 for folder in ('archive','results','build','manuscript'):(R/folder).mkdir(exist_ok=True)
 for name,h in HASHES.items():
  p=R/'archive'/name
  if not p.exists():
   origin=name if name in ('ECTA.tex','supp.tex','README.md') else 'revisions/2026-10-04-r16/'+name
   data=subprocess.check_output(['git','show',BASE+':'+origin],cwd=ROOT)
   if hashlib.sha256(data).hexdigest()!=h:raise ValueError('Original root identity mismatch')
   p.write_bytes(data)
  if hashlib.sha256(p.read_bytes()).hexdigest()!=h:raise ValueError('Archive changed: '+name)
 intro=(OLD/'manuscript/introduction.tex').read_text()
 intro=replace_once(intro,'They identify useful fitted-continuation decisions and their observed costs; they do not identify a unique variance-reduction mechanism or a minimum-work frontier over every simulation budget.','They identify useful fitted-continuation decisions and their observed costs. A separate assessment below tests continuation prediction directly, and a simultaneous catalogue calculation compares every declared budget; neither establishes a unique causal mechanism or a minimum-work frontier over all possible procedures.')
 extra=r'''Two further results connect this evidence to the learned object and the economic accuracy target. Independent prediction assessment compares the nonlinear scalar continuation with realized Raw caches at the same selected action pairs. Common future-path noise cancels from the difference of squared errors. Eight of 24 prespecified intervals establish lower NBO contrast risk, four favor Raw, and twelve remain unresolved. This measures a conditional prediction benefit without inferring payoff ordering from risk ordering. Separately, exact closure of all 216 simultaneous menu payoff intervals bounds regret relative to the complete sixteen-candidate budget catalogue. In the fifty-dimensional Intermediate design, final-stage NBO is the least-cost candidate certified within $10^{-4}$ of the best catalogue payoff. Its mean complete construction and query cost is 12.6993 seconds, rounded upward. Cheaper uncertified candidates remain possible competitors, and the full cost of conducting the comparison remains charged. This last calculation is an explicitly post-freeze deterministic use of simultaneous intervals, not a new prospective stopping experiment.

'''
 marker="The economic applications remain part of the paper's substantive scope."
 write('manuscript/introduction.tex',replace_once(intro,marker,extra+marker))
 con=(OLD/'manuscript/conclusion.tex').read_text()
 extra=r'''The continuation-risk comparison supplies separate evidence about the fitted nonlinear object. Cancellation of common simulation noise makes eight risk advantages and four reversals identifiable across the complete 24-event family. The economic payoff experiments, rather than risk ordering alone, establish the value of the returned decisions. Exact closure of the complete menu intervals further identifies the least-cost certified candidate at the common accuracy tolerance. NBO attains that distinction in the fifty-dimensional Intermediate design; other designs select simulation or cheaper fitted actors. The result concerns an explicit catalogue of computed procedures and observed accounting costs. It does not replace the broader adapted-class regret account or the full bill for producing the comparison.

'''
 marker='The economic applications retain their own utility domains, boundary'
 write('manuscript/conclusion.tex',replace_once(con,marker,extra+marker))
 current=(OLD/'manuscript/current_results.tex').read_text()
 write('manuscript/current_results.tex',replace_once(current,'The menu comparison measures economic decision values and work; it does not\nadd an independent estimate of continuation-risk reduction.','The menu comparison measures economic decision values and work.\nSection~\\ref{sec:r18risk} supplies the separate independent assessment of\ncontinuation-risk differences; the payoff comparisons alone do not imply it.'))
 main=(R/'archive/ECTA.tex').read_text().replace('revisions/2026-10-04-r16/build/','revisions/2026-10-05-r18/build/')
 abstract='''Neural Bellman Operators learn a common continuation value for repeated economic decisions. We characterize its reuse and assess nonlinear continuation contrasts with an independent statistic that cancels common simulation noise. In a nonlinear capital economy, two previously unpiloted fifty-dimensional decision menus establish material NBO payoff gains over materialized simulation and direct-policy actors. Eight of 24 conditional risk comparisons favor NBO, four favor simulation, and twelve remain unresolved. Exact closure of simultaneous payoff intervals bounds accuracy across every declared method and budget. In the fifty-dimensional Intermediate design, NBO is the least-cost candidate certified within $10^{-4}$ of the best catalogue payoff; cheaper uncertified alternatives remain unresolved. Independent paired confirmation, exact-trace neural-HJB comparisons, signed Bellman gains, and separate scalar and diffusion accounts retain their distinct economic targets. Complete applications preserve recursive utility, endogenous preferences, temporal selves, and strategic interaction.'''
 main=re.sub(r'(?s)(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+abstract+'\n'+m[2],main)
 for name in ('introduction','conclusion','current_results'):main=replace_once(main,f'revisions/2026-10-04-r16/manuscript/{name}.tex',f'revisions/2026-10-05-r18/manuscript/{name}.tex')
 needle=r'\input{revisions/2026-10-05-r18/manuscript/current_results.tex}'
 main=replace_once(main,needle,needle+'\n'+r'\input{revisions/2026-10-05-r18/manuscript/risk_main.tex}'+'\n'+r'\input{revisions/2026-10-05-r18/manuscript/catalogue_main.tex}')
 (ROOT/'ECTA.tex').write_text(main)
 supp=(R/'archive/supp.tex').read_text().replace('revisions/2026-10-04-r16/build/','revisions/2026-10-05-r18/build/')
 needle=r'\input{revisions/2026-10-04-r16/manuscript/source_index.tex}'
 supp=replace_once(supp,needle,r'\input{revisions/2026-10-05-r17/manuscript/contrast_proofs.tex}'+'\n'+r'\input{revisions/2026-10-05-r18/manuscript/catalogue_proofs.tex}'+'\n'+r'\input{revisions/2026-10-05-r18/manuscript/record.tex}'+'\n'+needle)
 (ROOT/'supp.tex').write_text(supp)
 for name in ('applications','response'):
  text=(R/'archive'/f'{name}.tex').read_text().replace('revisions/2026-10-04-r16/build/','revisions/2026-10-05-r18/build/')
  if name=='response':text=replace_once(text,'revisions/2026-10-04-r16/manuscript/response_body.tex','revisions/2026-10-05-r18/manuscript/response_body.tex')
  write(name+'.tex',text)
 t=(OLD/'manuscript/response_body.tex').read_text()
 preface=r'''\section*{Response to the Referee}
We thank the referee for identifying the economic contribution that the learned continuation must establish. The paper remains \emph{Neural Bellman Operators}. This revision incorporates the complete continuation-menu, independent paired confirmation, strengthened-HJB, and signed-Bellman studies from the intervening manuscript. It additionally integrates the completed independent contrast-risk assessment and develops a sharp finite-catalogue accuracy account using every declared method and budget. The economic applications, mathematical statements, full proofs, previous results, and contrary comparisons remain current.

The report answered here is the advisory report on publication \texttt{1cb3cc9e}, retained at review commit \texttt{cb4595bb}. At preparation, the review branch named for the next manuscript still pointed to publication \texttt{0b152607} and contained no further report. We therefore do not attribute new comments to that branch. The risk evidence at \texttt{3a5bae12} is independently replayed in this revision; it was not generated anew by the editorial integration. The catalogue analysis is new deterministic work on the existing simultaneous payoff family, expressly labelled post-freeze. The following response retains each earlier substantive answer and adds the present mathematical and evidentiary resolution where relevant.

'''
 t=preface+t[t.index(r'\section{Blocking comments}'):]
 for key,value in reversed(list(ADDITIONS.items())):
  pos=t.index(r'\label{resp:'+key+'}')
  m=re.search(r'\n\\(?:subsection\*|section)\{',t[pos+1:])
  end=pos+1+m.start() if m else len(t)
  t=t[:end]+'\n\n'+value+'\n'+t[end:]
 write('manuscript/response_body.tex',t)
 metadata={'report':'reviews/2026-10-04-econometrica-numerical-methods-r15/referee_report.md','report_blob':'0a108098e8fd0c6ab7467a6cb0b4e9ae02325','reviewed_publication':'1cb3cc9efe135966ec228dfaf51c6841a6dfc97c','inherited_publication':'0b15260752b8e988236f82cc0ee7752b44f326f1','inherited_risk_evidence':BASE,'new_analysis':'exact finite-catalogue closure, explicitly post-freeze','comments':[{'id':k,'response_label':'resp:'+k,'new_response':v} for k,v in ADDITIONS.items()]}
 # Compute the actual report identity rather than trusting a hand-entered digest.
 report=(ROOT/metadata['report']).read_bytes()
 metadata['report_blob']=hashlib.sha1(b'blob '+str(len(report)).encode()+b'\0'+report).hexdigest()
 write('RESPONSE_MAP.json',json.dumps(metadata,indent=2))
 (ROOT/'README.md').write_text((R/'README.current.md').read_text())
 print('Integrated article, supplement, applications, and all eighteen referee answers.')
if __name__=='__main__':assemble()
