"""Create new wrappers from preserved sources; never replace a nonidentical wrapper."""
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[2];os.chdir(ROOT)
P='revisions/2026-09-18-r12-procurement-witness/paper/'
def put(path,text):
    path=Path(path)
    if path.exists() and path.read_text()!=text:raise ValueError('nonidentical existing generated source: '+str(path))
    path.write_text(text)
front=r'''\documentclass[ecta]{econsocart}
\input{revisions/2026-09-17-r9-participation-permissions/paper/preamble}
\makeatletter
\def\copyright@text{Revision R12 --- September 18, 2026}
\def\@runjournal{Revision R12}
\def\form@runauthors{\def\@runjournal{Revision R12 --- September 18, 2026}}
\makeatother
\begin{document}
\begin{frontmatter}
\title{Neural Bellman Operators}
\runtitle{Neural Bellman Operators}
\begin{aug}
\author[id=au1,addressref={add1}]{\fnms{Qian}~\snm{QI}\ead[label=e1]{qiqian@pku.edu.cn}}
\address[id=add1]{\orgdiv{Peking University},\orgname{No.5 Yiheyuan Road, Haidian District, Beijing, P.R.China 100871}}
\end{aug}
\support{This paper develops the numerical framework accompanying \citet{qi2024}. The author thanks Darrell Duffie for discussions.}
\begin{abstract}
We study the purchase of operating commitments when an agent controls consumption, investment, preference adjustment, and surrender. A purchaser chooses a financial mandate, guarantee capacity, compulsory term, and participation payment from a specified institutional menu. Value perturbations bound delivered service for every near-optimal response, allowing a contract choice to be certified without selecting a favorable best response. In a stochastic settlement economy, adjustment changes the chosen compulsory term even when the purchaser selects the positive financial mandate in both regimes. A signed opportunity-exposure decomposition distinguishes this procurement comparison from the agent's class ranking. Neural Bellman Operators separate policy proposal from evaluation and certification. Feasible-policy polynomials preserve common transition-law dependence; a signed endpoint correction compresses a count-information upper bound. We certify regional financial and surrender comparisons and report matched broader-law computations. Complete canonical inputs and an independently recoded witness checker connect the economic inequalities to immutable arrays and reject corrupted certificates. Earlier operator, approximation, preference, and equilibrium results are preserved in the accompanying compendium and supplement.
\end{abstract}
\begin{keyword}
\kwd{Dynamic programming}\kwd{Procurement}\kwd{Preference adjustment}\kwd{Policy iteration}\kwd{Numerical verification}\kwd{Computational economics}
\end{keyword}
\end{frontmatter}
'''
put('ECTA_R12.tex',front+'\\input{'+P+'main}\n\\input{'+P+'references}\n\\end{document}\n')
comp=Path('ECTA_R11.tex').read_text().replace('Revision R11','R12 Compendium')
comp=comp.replace('\\title{Neural Bellman Operators}','\\title{Neural Bellman Operators: Complete Theoretical and Computational Compendium}')
comp=comp.replace('\\runtitle{Neural Bellman Operators}','\\runtitle{Neural Bellman Operators: Compendium}')
put('COMPENDIUM_R12.tex',comp)
supp=Path('SUPP_R11.tex').read_text().replace('Revision R11','Revision R12')
supp=supp.replace('\\begin{document}',r'\usepackage{xr}'+'\n'+r'\externaldocument{COMPENDIUM_R12_xrefs}'+'\n'+r'\externaldocument{ECTA_R12_xrefs}'+'\n'+r'\begin{document}')
supp=supp.replace('\\input{revisions/2026-09-17-r8-full-response/paper/references}', '\\input{'+P+'S15_proofs}\n\\input{'+P+'references}')
supp=supp.replace('This supplement gives complete proofs','The new Section S.15 proves the all-response service enclosure, joint procurement selection, signed opportunity-exposure identities, and the witness-reconstruction arguments. This supplement gives complete proofs')
put('SUPP_R12.tex',supp)
ref=Path('revisions/2026-09-17-r8-full-response/paper/references.tex').read_text()
ref=ref.replace('\\end{thebibliography}',r'''\bibitem[Junges et al.(2019)]{junges2019}
Junges, S., E. \'{A}brah\'{a}m, C. Hensel, N. Jansen, J.-P. Katoen, T. Quatmann, and M. Volk (2019): ``Parameter Synthesis for Markov Models: Covering the Parameter Space,'' arXiv:1903.07993, revised November 2023.

\end{thebibliography}''')
put(P+'references.tex',ref)
f=Path('replication/r12/science.py');text=f.read_text();old='from engine import EPS,restrict';new='EPS=core.EPS\nrestrict=core.r7.restrict'
if old in text:f.write_text(text.replace(old,new))
print('R12 WRAPPERS MATERIALIZED; INHERITED INPUTS UNCHANGED')
