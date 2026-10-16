"""Lossless structural integration from retained R99 entry points."""
from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[1]
parts=[]
for source,marker,tag in [
 ('sections/core49.tex',r'\subsection{Original-owner compilation on a tensor cover}','core'),
 ('new/continuous95-active99.tex',r'\subsection{Residual covers and strict continuum screening}','continuous'),
 ('new/action99.tex',r'\subsection{Which training loss controls rejection?}','action')]:
 text=(R/source).read_text();cut=text.index(marker);head,tail=text[:cut],text[cut:]
 (R/f'new109/{tag}-main.tex').write_text(head);(R/f'new109/{tag}-archive.tex').write_text(tail)
 assert head+tail==text
 parts.append({'source':source,'main':f'new109/{tag}-main.tex','archive':f'new109/{tag}-archive.tex','sha256':hashlib.sha256(text.encode()).hexdigest()})
article=(R/'retained99/ECTA.tex').read_text()
article=article.replace('new/introduction99','new109/introduction').replace('new/conclusion99','new109/conclusion')
for old,new in [('sections/core49','new109/core-main'),('new/continuous95-active99','new109/continuous-main'),('new/action99','new109/action-main')]:article=article.replace(r'\input{'+old+'}',r'\input{'+new+'}')
article=article.replace(r'\input{new109/action-main}',r'\input{new109/action-main}'+'\n'+r'\input{new109/compiler}'+'\n'+r'\input{new109/tail}'+'\n'+r'\input{new109/improvement}'+r'''
\paragraph{Recursive utility, information and the computational graph.}
Supplement Section~\ref{supp:bridge109} proves a separate Brownian Markov BSDE verification result, including well-posedness, terminal or boundary errors and the critic graph $z=\sigma^{\mathsf T}\nabla u$. Its assumptions delimit a rigorous subcase of a connection to Neural Differential Utility; it is not an equivalence between different recursive objectives. The following information results retain their own oracle restrictions and do not assume free formula or derivative access.
''')
article=article.replace(r'\input{sections/study96}','').replace(r'\input{new/study97}',r'\input{new109/study}')
abstract='''This paper develops Neural Bellman Operators for feasible decisions under the original recursive economic objective. A centered tail-switch bound connects continuation accuracy to constrained action loss when nonlinear risk changes its maximizing density. An active-region compiler solves the original investment model's terminal Bellman action through at most four monotone cubic regions, with an outward witness retaining certification authority. Completed-incumbent safeguards guarantee actual policy improvement; recursive gain bounds and paid precision rules state the additional uniform conditions and computational costs. A Brownian BSDE result gives a separately delimited recursive-utility bridge. An executed common-information comparison retains 4,096 catalogue decisions, strong conventional representations and seven fresh-process timing repetitions. Compilation reduces observed complete work, and safeguards improve fitted policies at additional cost. Equivalent ReLU and conventional hinge geometry produces identical policies. Historical quadratic victories, adverse residual-fitting results and unresolved adoption regions remain visible. Neural-specific competitiveness and calibrated economic adoption are research claims still requiring their own evidence.'''
article=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}'+'\n'+abstract+'\n'+r'\end{abstract}',article,flags=re.S)
article=article.replace('references99}','references99,references109-additions}')
(R/'ECTA.tex').write_text(article)
supp=(R/'retained99/supp.tex').read_text().replace(r'\bibliographystyle',r'\input{new109/proofs}'+'\n'+r'\input{new109/recursive_bridge}'+'\n'+r'\bibliographystyle')
supp=supp.replace('references99}','references99,references109-additions}')
supp=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}Complete proofs of the retained NBO construction, original-risk qualification and information results are followed by proofs of the active-region compiler, centered tail-switch bound, safeguarded and recursive policy improvement, paid precision and a delimited Brownian recursive-utility verification theorem. Finite executable tests are separate evidence, not proof-assistant certificates.\end{abstract}',supp,flags=re.S)
(R/'supp.tex').write_text(supp)
app=(R/'retained99/appendix.tex').read_text()
extra=r'''\section{Current execution and historical custody}\label{dev:custody109}
This companion preserves historical mathematical and empirical objects under their own dates, models and source identities. The complete R99 source remains in Git history; changed entry points are retained byte for byte. R98 and R100--R108 protocols remain separate. Only the exact R108-source reproduction is new executed investment evidence here. Historical occurrences of ``new'' refer to their original revision, not to a fresh experiment in this edition. Source identities, report files, comment headings and the theorem inventory are in the machine-readable retention map. Reading and preserving a historical record is not an independent replay of every historical experiment.
\input{new109/full_tables}
\section{Retained original-owner compilation and acquired construction}\label{dev:core109}
\input{new109/core-archive}
\section{Retained residual screening and finite-menu selection}\label{dev:selection109}
\input{new109/continuous-archive}
\input{new109/action-archive}
\input{sections/study96}
\input{new/study97}
'''
app=app.replace(r'\input{sections/recursive86}',extra+'\n'+r'\input{sections/recursive86}',1).replace('references99}','references99,references109-additions}')
app=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}This archival companion retains the historical economic models, theorems, proofs, negative results, numerical catalogues and diagnostic material of Neural Bellman Operators. Current complete finite-catalogue tables are added with their separate execution identity. Historical evidence is preserved, not relabeled as a new experiment or a completed broader claim.\end{abstract}',app,flags=re.S)
(R/'appendix.tex').write_text(app)
old=(R/'references99.bib').read_text();new=(R/'references109.bib').read_text();assert new.startswith(old)
(R/'references109-additions.bib').write_text(new[len(old):])
(R/'evidence109/SECTION_SPLITS109.json').write_text(json.dumps(parts,indent=2)+'\n')
print('Integrated; all split source bytes preserved')
