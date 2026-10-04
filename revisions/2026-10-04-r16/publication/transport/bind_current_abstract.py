"""Correct a reading-root assembly omission found in visual proof review.

The R16 abstract was present as an editable source but the inherited root still
contained the R15 inline abstract. Bind the root to the new abstract, and require
that the new abstract is actually reachable in the compiled source graph.
No numerical source, observation, confidence allocation or old archive changes.
"""
from pathlib import Path
P=Path(__file__).resolve().parents[1]
assembly=P/'code/assemble_publication.py'
s=assembly.read_text()
marker=' # Bind the journal root to the R16 editorial abstract.\n'
if marker not in s:
    anchor=' for n in moved:\n'
    assert s.count(anchor)==1
    block=""" # Bind the journal root to the R16 editorial abstract.
 begin,end=r'\\begin{abstract}',r'\\end{abstract}'
 assert main.count(begin)==main.count(end)==1
 first,rest=main.split(begin,1)
 _,last=rest.split(end,1)
 main=first+begin+'\\n\\\\input{'+PREFIX+'/manuscript/abstract.tex}\\n'+end+last
"""
    s=s.replace(anchor,block+anchor)
    assembly.write_text(s)
audit=P/'code/publication_audit.py'
s=audit.read_text()
anchor=" current_labels=set()\n"
check=""" assert R16+'publication/manuscript/abstract.tex' in current_sources
 assert (P/'manuscript/abstract.tex').read_bytes()==(P/'editorial/abstract.tex').read_bytes()
"""
if check not in s:
    assert s.count(anchor)==1
    audit.write_text(s.replace(anchor,check+anchor))
print('Current abstract is bound to the reading root and required by publication audit.')
