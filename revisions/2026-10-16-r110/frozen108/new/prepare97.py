"""Integrate R97 without changing any historical scientific section file."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1]
for doc in ('ECTA','supp','appendix'):
    p=R/'new'/('original-'+doc+'96.tex')
    if not p.exists():shutil.copyfile(R/(doc+'.tex'),p)
original=(R/'new/original-ECTA96.tex').read_text()
start=original.index('\\begin{abstract}')+len('\\begin{abstract}');end=original.index('\\end{abstract}')
abstract='''
This paper develops Neural Bellman Operators for constructing feasible dynamic policies and bounding their loss against the original economic optimum. Own-future neural construction retains feasible witnesses and explicit acquisition errors. Under recursive risk, reference-centered qualification gives complete-policy comparisons. We establish a second-order continuous-law AVaR enclosure and a matching deterministic adaptive information exponent at fixed risk level. An exact oblique-continuation comparison separates representation classes, and an executable certificate-oriented readout guarantees nonworsening attained residual spans after numerical validation. The retained frozen investment comparison is supplemented by a rank--label campaign that charges acquisition, rejected proposals, repair, and whole-workload execution. A workload-consistent interval frontier translates policy and resource bounds into conditional purchase decisions. Neural representation, certificate improvement, and economic gain are distinguished by their assumptions and observable implications; the original NBO construction and adverse historical evidence are retained.
'''
s=original[:start]+abstract+original[end:]
s=s.replace('sections/introduction96','new/introduction97').replace('sections/precision96','new/precision96-revised').replace('sections/conclusion96','new/conclusion97')
s=s.replace('\\input{sections/accuracy62-print}','''\\paragraph{Primitive accuracy and resource growth.}
The complete primitive investment construction, its original-optimum accuracy theorem, and the dated horizon allocation are retained in Appendix Sections~\\ref{sec:accuracy62} and~\\ref{sec:complexity86}. Their state, action, innovation, and bit-growth costs remain explicit. The continuous recursive-risk investment analysis below supplies the corresponding original-law qualification used in the current comparison.''')
s=s.replace('\\input{sections/complexity86}','')
s=s.replace('\\input{sections/study96}','\\input{new/theory97}\n\\input{sections/study96}\n\\input{new/study97}')
s=s.replace('references92-canonical','references97');(R/'ECTA.tex').write_text(s)
s=(R/'sections/precision96.tex').read_text()
s=s.replace('Let $d=\\mathbb E[J^a-J^b]$ be the original policy-cost contrast,', 'Let a workload contain $B$ initial-state decisions and let $d=\\mathbb E[J^a-J^b]$ be the per-decision original policy-cost contrast,')
s=s.replace('m\\{d+\\lambda(c_a-c_b)\\}', 'm\\{B d+\\lambda(c_a-c_b)\\}')
s=s.replace('\\lambda s^- -d^+', '\\lambda s^- -B d^+')
s=s.replace('This expression distinguishes a policy-quality loss', 'For the recorded timing workloads $B=32$; for a single decision $B=1$. This expression distinguishes a policy-quality loss')
(R/'new/precision96-revised.tex').write_text(s)
move=['centered69','proofs70','proofs72','proofs73','proofs77','proofs89','proofs90']
s=(R/'new/original-supp96.tex').read_text()
for name in move:s=s.replace('\\input{sections/'+name+'}\n','')
s=s.replace('\\bibliographystyle','\\input{new/proofs97}\n\\bibliographystyle').replace('references92-canonical','references97')
a=s.index('\\begin{abstract}')+len('\\begin{abstract}');b=s.index('\\end{abstract}')
s=s[:a]+'''\nThis focused supplement gives the complete construction, complete-policy, signed-risk, reference-centered-risk, continuous investment, and decision-resolution proofs used by the article. It adds proofs of the deterministic adaptive information lower bound, exact representation comparisons, verified readout improvement, and the workload-consistent purchase frontier. Intervening historical proofs are preserved as complete sections in the Numerical and Development Appendix.\n'''+s[b:]
(R/'supp.tex').write_text(s)
s=(R/'new/original-appendix96.tex').read_text();add='\\input{new/evidence97}\n\\input{sections/accuracy62-print}\n\\input{sections/complexity86}\n'+''.join('\\input{sections/'+n+'}\n' for n in move)
s=s.replace('\\bibliographystyle',add+'\\bibliographystyle').replace('references92-canonical','references97');(R/'appendix.tex').write_text(s)
b=(R/'references92-canonical.bib').read_text()
(R/'references97.bib').write_text(b+'\n@misc{Novak2015Integration97,\n author={Novak, Erich},\n title={Some Results on the Complexity of Numerical Integration},\n year={2015},\n note={arXiv:1409.6714, version 2, 18 November 2015},\n url={https://arxiv.org/abs/1409.6714}\n}\n')
b=(R/'code/build95.py').read_text().replace('audit/reproduction96/build','audit97/build').replace('BUILD95.json','BUILD97.json')
b=b.replace("list((R/'tables').glob('*.tex'))", "list((R/'tables').glob('*.tex'))+list((R/'new').glob('*.tex'))+list((R/'new').glob('*.py'))")
(R/'code/build97.py').write_text(b)
(R/'audit97').mkdir(exist_ok=True)
source={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in list((R/'sections').glob('*.tex'))+list((R/'code').glob('*.py')) if p.name!='build97.py'}
(R/'audit97/INHERITED_SCIENTIFIC_SOURCES97.json').write_text(json.dumps(source,indent=2,sort_keys=True)+'\n')
