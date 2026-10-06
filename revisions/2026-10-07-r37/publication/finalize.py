"""One-time publication migration; no scientific inputs or clocks are changed.

The resulting current manuscripts and publisher are committed as ordinary
source files. Rebuilding their PDFs does not require applying this migration
again. Historical source components remain byte-for-byte unchanged.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[3]
REL='revisions/2026-10-07-r37'
R=ROOT/REL

def replace(text,old,new):
    if old in text:return text.replace(old,new)
    if new in text:return text
    raise RuntimeError('Publication source anchor not found: '+old[:120])

p=ROOT/'revisions/2026-10-06-r27/manuscript/entropic_main.tex'
s=p.read_text()
old=r'''\begin{equation}\label{eq:r27gaussian}
 \mathcal R_\theta v(y)=y'\Psi_\theta(P)y+c+h_\theta(P),\quad
 \Psi_\theta(P)=P(I-2\theta\Sigma P)^{-1},\quad
 h_\theta(P)=-\frac{\log\det(I-2\theta\Sigma P)}{2\theta}.
\end{equation}'''
new=r'''\begin{align}
 \mathcal R_\theta v(y)&=y'\Psi_\theta(P)y+c+h_\theta(P),\notag\\
 \Psi_\theta(P)&=P(I-2\theta\Sigma P)^{-1},\qquad
 h_\theta(P)=-\frac{\log\det(I-2\theta\Sigma P)}{2\theta}.
 \label{eq:r27gaussian}
\end{align}'''
(R/'manuscript/entropic_main.tex').write_text(replace(s,old,new))
p=ROOT/'revisions/2026-10-06-r32/manuscript/curvature.tex'
s=p.read_text()
old=r'''\[
 \|W_j'W_j-M\|_F\leq(1-2\alpha c)^j\sqrt d\,L,
 \qquad 0<c\leq\lambda_{\min}(M),\quad
 0<\alpha\leq(4L)^{-1},\quad\|M\|_2\leq L.
\]'''
new=r'''\begin{gather*}
 \|W_j'W_j-M\|_F\leq(1-2\alpha c)^j\sqrt d\,L,\\
 0<c\leq\lambda_{\min}(M),\qquad
 0<\alpha\leq(4L)^{-1},\qquad\|M\|_2\leq L.
\end{gather*}'''
(R/'manuscript/curvature.tex').write_text(replace(s,old,new))
header='\n'+r'''\makeatletter
\g@addto@macro\econsocart@fmadd{\def\copyright@text{Prepared for referee review}}
\makeatother
'''
for doc in ('ECTA','supp','response'):
    p=R/(doc+'.tex');s=p.read_text()
    s=s.replace('revisions/2026-10-06-r27/manuscript/entropic_main.tex',REL+'/manuscript/entropic_main.tex')
    s=s.replace('revisions/2026-10-06-r32/manuscript/curvature.tex',REL+'/manuscript/curvature.tex')
    if 'Prepared for referee review' not in s:s=s.replace(r'\begin{document}',header+r'\begin{document}',1)
    p.write_text(s)

p=R/'publication/publish.py';s=p.read_text()
s=replace(s,"['bibtex',str(R/'build'/doc)]","['bibtex',str((R/'build'/doc).relative_to(ROOT))]")
s=replace(s,"'revisions/2026-10-06-r27/manuscript/entropic_main.tex'","REL+'/manuscript/entropic_main.tex'")
s=replace(s,"'revisions/2026-10-06-r32/manuscript/curvature.tex'","REL+'/manuscript/curvature.tex'")
anchor="    pre+='\\n'+r'\\setlength{\\emergencystretch}{2em}'+'\\n'"
if 'Prepared for referee review' not in s:s=replace(s,anchor,anchor+'\n    pre += '+repr(header))
p.write_text(s)
compile(s,str(p),'exec')

preservation=json.loads((R/'audit/PRESERVATION.json').read_text())
for path,h in preservation['old_component_sha256'].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
freeze=json.loads((R/'protocols/SOURCE_FREEZE.json').read_text())
for path,h in freeze['files'].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
summary=json.loads((R/'results/SUMMARY.json').read_text())
for row in summary['rows']:
    assert hashlib.sha256((R/'results/exact'/row['record']).read_bytes()).hexdigest()==row['record_sha256']
audit={'changes':['Relative repository path passed to BibTeX; no relaxation of file-output protection.','Gaussian transform display split over two lines in a current copy.','Gradient contraction display split over two lines in a current copy.','Current documents identify themselves as prepared for referee review; no claim of actual submission.'],'historical_components_unchanged':len(preservation['old_component_sha256']),'frozen_science_files_unchanged':len(freeze['files']),'eight_exact_records_unchanged':True,'current_source_copy_paths':['manuscript/entropic_main.tex','manuscript/curvature.tex'],'scope':'Publication layout and build only; no scientific retuning or replacement execution.'}
(R/'audit/PUBLICATION_PREFLIGHT.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(audit,indent=2))
