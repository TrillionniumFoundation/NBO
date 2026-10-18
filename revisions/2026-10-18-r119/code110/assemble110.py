"""Build entry points with byte-exact retention of all split R99 material."""
from pathlib import Path
import re,json,hashlib
R=Path(__file__).resolve().parents[1]
parts=[]
for name,marker,tag in [('sections/core49.tex',r'\subsection{Original-owner compilation on a tensor cover}','core'),('new/continuous95-active99.tex',r'\subsection{Residual covers and strict continuum screening}','continuous'),('new/action99.tex',r'\subsection{Which training loss controls rejection?}','action')]:
 s=(R/name).read_text();cut=s.index(marker);head,tail=s[:cut],s[cut:]
 (R/f'new110/{tag}-main.tex').write_text(head);(R/f'new110/{tag}-archive.tex').write_text(tail)
 assert head+tail==s
 parts.append({'source':name,'main':f'new110/{tag}-main.tex','archive':f'new110/{tag}-archive.tex','sha256':hashlib.sha256(s.encode()).hexdigest()})
a=(R/'retained99/ECTA.tex').read_text().replace('new/introduction99','new110/introduction').replace('new/conclusion99','new110/conclusion')
for old,new in [('sections/core49','new110/core-main'),('new/continuous95-active99','new110/continuous-main'),('new/action99','new110/action-main')]:a=a.replace(r'\input{'+old+'}',r'\input{'+new+'}')
a=a.replace(r'\input{new110/action-main}',r'''\input{new110/action-main}
\input{new109/compiler}
\input{new109/tail}
\input{new109/improvement}
\input{new110/budget}
\paragraph{Recursive utility and the computational graph.}
Supplement Section~\ref{supp:bridge109} proves a Brownian Markov recursive-utility verification result, including well-posedness, the critic graph $z_u=\sigma^{\mathsf T}\nabla u$, and terminal or stopping-boundary errors. It is a delimited NDU/FBSDE research interface, not an equivalence between different economic objectives. The information statements below retain their declared oracle restrictions; formula or derivative access is not free point-value information.
''')
a=a.replace(r'\input{sections/study96}','').replace(r'\input{new/study97}',r'\input{new110/study}')
abstract='''This paper develops Neural Bellman Operators for continuation learning and feasible decisions under the original recursive economic objective. Centered tail-switch bounds connect nonlinear-risk continuation error to constrained action loss. An active-region Bellman compiler and outward witnesses separate numerical proposals from certificate authority. Completed-incumbent safeguards establish actual policy improvement; a remaining-gain rule stops further computation with a verified bound on foregone improvement. We prove its pointwise and recursive accounts, alongside retained own-future construction and information results. A separately delimited BSDE verification theorem connects the framework to recursive utility. Two complete original-investment comparisons retain 10,240 primary decisions and all fresh-process timing records. At the prespecified gain budget, 2,386 of 3,072 extra trial pairs are omitted, with actual original-policy cost sacrifices reported. Strong conventional controls receive identical information and algorithms; equivalent ReLU and hinge geometry gives identical policies. Historical adverse evidence remains visible. Neural-exclusive competitiveness and calibrated adoption require their own further evidence.'''
a=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}'+'\n'+abstract+'\n'+r'\end{abstract}',a,flags=re.S)
a=a.replace('references99}','references99,references110-additions}')
(R/'ECTA.tex').write_text(a)
s=(R/'retained99/supp.tex').read_text().replace(r'\bibliographystyle',r'''\input{new109/proofs}
\input{new110/budget_proofs}
\input{new110/recursive_bridge}
\bibliographystyle''')
s=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}Complete proofs of the retained own-future NBO construction, original-law qualification and information results are followed by proofs of the active-region Bellman compiler, centered tail-switch bound, completed-incumbent and recursive improvement, gain-budgeted stopping and risk-distorted composition. A separate Brownian Markov recursive-utility result proves its own well-posedness and residual certificate. Finite executable checks are implementation evidence, not substitutes for these continuum arguments.\end{abstract}',s,flags=re.S)
s=s.replace('references99}','references99,references110-additions}');(R/'supp.tex').write_text(s)
p=(R/'retained99/appendix.tex').read_text()
extra=r'''\section{Current execution, custody and retained scientific identities}\label{dev:custody110}
This companion preserves earlier theorems, economic models, proofs and positive or negative experiments under their original identities. Historical occurrences of ``new'' refer to their original revision, not to the present campaign. R98 and R100--R109 retain independent source, protocol and execution identities; none of their missing observations is supplied by relabeling current results. The complete released R99 manuscript is the author-source baseline. Recovered R109 theory is carried forward with its stated hypotheses, while historical execution summaries without their original raw files are not used as current observations.

The source archive includes the recovered branch/root inventory, 35 persisted report texts and their manifests, full current raw records, immutable source freezes and actual command logs. That inventory is not a claim to have independently replayed every scientific file in every historical branch. The broader inherited test attempt has twenty errors and one failed pinned-file assertion among 435 cases. Current-source success and full historical archive closure remain distinct assertions. Full command and source identities, all report headings, current response locations and unresolved obligations are recorded in the machine-readable retention and response maps.
\input{new110/full_tables}
\section{Retained original-owner compilation and acquired construction}\label{dev:core110}
\input{new110/core-archive}
\section{Retained residual screening and prospective finite-menu selection}\label{dev:selection110}
\input{new110/continuous-archive}
\input{new110/action-archive}
\input{sections/study96}
\input{new/study97}
'''
p=p.replace(r'\input{sections/recursive86}',extra+'\n'+r'\input{sections/recursive86}',1)
p=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}This archival companion retains the economic models, theorems, proofs, numerical programmes, negative results and diagnostic accounts of Neural Bellman Operators. Current complete-catalogue and sensitivity tables are added with their separate execution identity. Historical evidence is preserved, not relabeled as a new experiment. The current executable dependency closure and successful records are distinct from the still-incomplete full historical replay.\end{abstract}',p,flags=re.S)
p=p.replace('references99}','references99,references110-additions}');(R/'appendix.tex').write_text(p)
(R/'evidence110/SECTION_SPLITS110.json').write_text(json.dumps(parts,indent=2)+'\n')
print('Assembled active documents with',len(parts),'lossless historical splits')
