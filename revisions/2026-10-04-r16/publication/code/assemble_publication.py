"""Assemble the R16 NBO reading edition without changing scientific inputs.

Every inherited R15 section remains in the current article or supplement.
The exact preceding roots are archived. No numerical report is overwritten.
"""
from pathlib import Path
import hashlib, json, shutil, re, subprocess, argparse
ROOT=Path(__file__).resolve().parents[4]
P=ROOT/'revisions/2026-10-04-r16/publication'
OLD=ROOT/'revisions/2026-10-04-r15'
M=P/'manuscript'
PREFIX='revisions/2026-10-04-r16/publication'
OLDPREFIX='revisions/2026-10-04-r15'

def put(name,text):
 p=P/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n')
def main():
 M.mkdir(parents=True,exist_ok=True)
 for name in ('ECTA.tex','supp.tex','README.md'):
  p=P/'archive'/name;p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():p.write_bytes((ROOT/name).read_bytes())
 for p in (OLD/'manuscript').glob('*.tex'):
  text=p.read_text().replace(OLDPREFIX+'/manuscript/',PREFIX+'/manuscript/')
  (M/p.name).write_text(text)
 # New editorial components are separate from every numerical source file.
 for p in (P/'editorial').glob('*.tex'):
  (M/p.name).write_bytes(p.read_bytes())
 oldmain=(P/'archive/ECTA.tex').read_text()
 oldsupp=(P/'archive/supp.tex').read_text()
 moved=['general_theory','new_theory','fees','economic_scope','evidence_baseline']
 main=oldmain.replace(OLDPREFIX+'/manuscript/',PREFIX+'/manuscript/').replace(OLDPREFIX+'/build/',PREFIX+'/build/')
 # Bind the journal root to the R16 editorial abstract.
 begin,end=r'\begin{abstract}',r'\end{abstract}'
 assert main.count(begin)==main.count(end)==1
 first,rest=main.split(begin,1)
 _,last=rest.split(end,1)
 main=first+begin+'\n\\input{'+PREFIX+'/manuscript/abstract.tex}\n'+end+last
 for n in moved:
  needle='\\input{'+PREFIX+'/manuscript/'+n+'.tex}'
  assert main.count(needle)==1,n
  main=main.replace(needle,'')
 needle='\\input{'+PREFIX+'/manuscript/algorithm.tex}'
 main=main.replace(needle,needle+'\n\\input{'+PREFIX+'/manuscript/theory_guide.tex}')
 needle='\\input{'+PREFIX+'/manuscript/mechanism.tex}'
 main=main.replace(needle,needle+'\n\\input{'+PREFIX+'/manuscript/signed_main_theory.tex}\n\\input{'+PREFIX+'/manuscript/reuse_main.tex}')
 (ROOT/'ECTA.tex').write_text(main)
 supp=oldsupp.replace(OLDPREFIX+'/manuscript/',PREFIX+'/manuscript/').replace(OLDPREFIX+'/build/',PREFIX+'/build/')
 needle='\\begin{appendix}'
 supp=supp.replace(needle,needle+'\n'+ '\n'.join('\\input{'+PREFIX+'/manuscript/'+n+'.tex}' for n in ['general_theory','new_theory','fees','economic_scope']))
 needle='\\input{'+PREFIX+'/manuscript/new_proofs.tex}'
 supp=supp.replace(needle,needle+'\n\\input{revisions/2026-10-04-r16/manuscript/signed_bellman_bridge.tex}\n\\input{'+PREFIX+'/manuscript/reuse_details.tex}')
 needle='\\input{'+PREFIX+'/manuscript/appendix_diagnostics.tex}'
 supp=supp.replace(needle,'\\input{'+PREFIX+'/manuscript/evidence_baseline.tex}\n'+needle)
 needle='\\input{'+PREFIX+'/manuscript/archive_index.tex}'
 supp=supp.replace(needle,'\\input{'+PREFIX+'/manuscript/registered_extensions.tex}\n'+needle)
 (ROOT/'supp.tex').write_text(supp)
 # One fresh-bank report, not a rewriting of the original statistical family.
 evidence=(M/'new_evidence.tex').read_text()
 needle='\\input{'+PREFIX+'/manuscript/paired_comparison.tex}'
 assert evidence.count(needle)==1
 evidence=evidence.replace(needle,needle+'\n\\input{'+PREFIX+'/manuscript/replication_evidence.tex}')
 needle='\\input{'+PREFIX+'/manuscript/mechanism_evidence.tex}'
 evidence=evidence.replace(needle,needle+'\n\\input{revisions/2026-10-04-r16/results/signed_mechanism/report/signed_main.tex}')
 evidence=evidence.replace('\\section{Evaluation and Economic Performance}', '\\section{Economic Performance and Independent Confirmation}')
 evidence+='\n\\input{'+PREFIX+'/manuscript/completed_evidence.tex}\n'
 (M/'new_evidence.tex').write_text(evidence)
 # Keep the common-continuation propositions in the main article, with the
 # full query-conditional range and scalar curvature proofs in the supplement.
 menu=(ROOT/'revisions/2026-10-04-r16/manuscript/menu_theory.tex').read_text()
 marker='\\subsection{A direct conditional payoff statistic}'
 assert marker in menu
 front,back=menu.split(marker,1)
 front=front.replace('\\section{Reusable Continuation in a Family of Capital Decisions}','\\section{The Economic Value of Reusable Continuation}')
 front=front.replace('The twelve retained random-feature diagnostics and the\nnonlinear comparisons address this tradeoff;', 'The retained random-feature diagnostics and the\nregistered nonlinear comparisons are designed to address this tradeoff;')
 front=front.replace('is\nassessed by the independent economic comparisons below, rather than\nbeing identified with that linear projection.', 'requires\nindependent economic comparisons rather than identification with that\nlinear projection.')
 (M/'reuse_main.tex').write_text(front+'\n'+(P/'editorial/decision_value.tex').read_text())
 (M/'reuse_details.tex').write_text('\\section{Conditional Continuation Comparisons and Decision-Class Accuracy}\n'+marker+back+'\n'+(P/'editorial/reuse_scope.tex').read_text())
 # Detailed inference is retained; its outcome semantics are stated in the main text.
 oldresponse=(OLD/'response.tex').read_text()
 response=oldresponse.replace(OLDPREFIX+'/build/',PREFIX+'/build/').replace(OLDPREFIX+'/manuscript/response_body.tex',PREFIX+'/manuscript/response_body.tex')
 response=response.replace('R15','R16').replace('R14','R15')
 (P/'response.tex').write_text(response)
 source=[]
 for p in sorted((P/'archive').glob('*')):
  source.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 put('EDITORIAL_PRESERVATION.json',json.dumps({'schema':'nbo-r16-reading-edition-preservation-v1','reviewed_commit':'1cb3cc9efe135966ec228dfaf51c6841a6dfc97c','review_commit':'cb4595bbcc7147e47e44ba40cb2f5034510ae19f','original_roots':source,'current_supplement_relocations':moved,'original_manuscript_files_retained':len(list((OLD/'manuscript').glob('*.tex'))),'numerical_inputs_modified':False,'note':'Original sources remain byte-for-byte at their original paths; current reading copies organize rather than remove the economic applications and theorems.'},indent=2))
 print('Assembled current NBO article, complete supplement and R15-referee response.')
if __name__=='__main__':main()
