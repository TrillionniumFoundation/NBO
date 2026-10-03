from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1]
s=(ROOT/'supp.tex').read_text();p=s[:s.index(r'\section{Relation to the Main Text}')]
p=p.replace('Supplement to Neural Bellman Operators','Neural Bellman Operators: Response to the R7 Advisory Report')
p=p.replace('NBO Supplement','NBO Referee Response')
p+=r'\input{revisions/2026-10-03-r8/manuscript/response_body.tex}'+'\n'+r'\end{document}'+'\n'
(R/'response.tex').write_text(p)
