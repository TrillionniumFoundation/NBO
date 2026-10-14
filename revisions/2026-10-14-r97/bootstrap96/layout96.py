"""Pre-construction completion; the comparison design and empirical rules remain fixed."""
from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1]
p=R/'code/report96.py'
s=p.read_text()
replacements={
    r'Risk & Service & Mean cost midpoint & Mean numerical width & Max. loss & Rejected proposals\\':r'Risk & Service & \shortstack{Mean cost\\midpoint} & \shortstack{Mean numerical\\width} & \shortstack{Maximum\\loss} & \shortstack{Rejected\\proposals}\\',
    r'\begin{longtable}{l p{.30\linewidth} r r r}':r'\begingroup\small\setlength{\tabcolsep}{3pt}'+'\n'+r'\begin{longtable}{@{}l p{.24\linewidth} r r r@{}}',
    r'\toprule Risk & Left minus right & Paired midpoint & Numerical half-width & Simultaneous interval\\':r'\toprule Risk & Left minus right & \shortstack{Paired\\midpoint} & \shortstack{Numerical\\half-width} & \shortstack{Simultaneous\\interval}\\',
    r'\bottomrule\end{longtable}':r'\bottomrule\end{longtable}\endgroup',
    r'Risk & Stored representation & Design rank & Active nonlinear & Search seconds & Cover seconds\\':r'Risk & Representation & \shortstack{Design\\rank} & \shortstack{Active\\nonlinear} & \shortstack{Search\\seconds} & \shortstack{Cover\\seconds}\\'
}
for old,new in replacements.items():
    if old not in s:raise RuntimeError('Unexpected report source; refusing an unreviewed layout rewrite')
    s=s.replace(old,new)
p.write_text(s)
precision=R/'sections/precision96.tex';text=precision.read_text()
anchor='The same argument applies to a rectangular product innovation law'
if text.count(anchor)!=1:raise RuntimeError('Unexpected precision statement location')
precision.write_text(text.replace(anchor,'\\input{sections/sharpness96}\n\n'+anchor))
proof=R/'sections/proofs96.tex';proof.write_text(proof.read_text()+'\n\\input{sections/sharpness_proof96}\n')
response=R/'response.md';text=response.read_text()
anchor='## M1 / B9.'
if text.count(anchor)!=1:raise RuntimeError('Unexpected response structure')
text=text.replace(anchor,'The exact equality in [[Corollary cor:sharpness96]] also shows that the integration-rate exponent and leading constant are sharp for the stated midpoint and endpoint rules, already on explicit two-unit convex ReLU continuations. The full threshold proof and exact-rational witnesses are retained. This is not a lower bound for every possible integration algorithm or a claim of neural empirical superiority.\n\n'+anchor)
response.write_text(text)
subprocess.run([sys.executable,str(R/'bootstrap96/parallel_audit_patch96.py')],check=True,cwd=R)
print('Table typography, exact sharpness and deterministic audit scheduling complete; primary comparison rules unchanged.')
