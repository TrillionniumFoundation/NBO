"""Pre-execution table layout only; numerical expressions and rows are unchanged."""
from pathlib import Path
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
print('Table headings wrapped; all numerical expressions and row generation retained.')
