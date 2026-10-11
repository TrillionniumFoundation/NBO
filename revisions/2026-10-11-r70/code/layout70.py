"""One-time ordinary-source layout repair, with exact content preservation."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[1]
def put(p,text):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    marker=R/'audit/LAYOUT70.json'
    if marker.exists():return
    unchanged={name:digest(R/name) for name in ('sections/decisions49.tex','sections/training69-retained70.tex','sections/proofs67.tex','sections/proofs70.tex')}
    p=R/'ECTA.tex';s=p.read_text()
    anchor=r'\input{sections/decisions49}'
    if s.count(anchor)!=1:raise AssertionError('Legacy inference input changed')
    s=s.replace(anchor,r'\paragraph{Retained economic inference.} The original cost-inference and information-choice results remain in the Supplement, Section~\ref{sec:decisions49}, with their statements and proofs unchanged. The following sections develop the new regret-scale comparison and its complete-deployment implications.')
    s=s.replace('The policy-inference contract in Section~\\ref{sec:decisions49}','The retained policy-inference contract in the Supplement, Section~\\ref{sec:decisions49}');put(p,s)
    p=R/'sections/study70.tex';s=p.read_text()
    s=s.replace(r'\input{tables/cold70}',r'The complete cold-start results are reported in Supplement Table~\ref{tab:cold70}.')
    s=s.replace(r'\input{tables/vector70}',r'Supplement Table~\ref{tab:vector70} reports every two-control workload.');put(p,s)
    p=R/'supp.tex';s=p.read_text();s=s.replace(r'\input{sections/proofs67}',r'\input{sections/decisions49}'+'\n'+r'\input{sections/proofs67}',1);put(p,s)
    p=R/'sections/supp70.tex';s=p.read_text();s+='\n'+r'''\section{Complete cold-start and vector workloads}\label{supp:workloads70}
\input{tables/cold70}
\input{tables/vector70}
The tables retain every declared method and task. They are relocated intact from the article to keep its reading path focused; no row, adverse comparison or timing repetition is removed.
''';put(p,s)
    p=R/'code/build70.py';s=p.read_text()
    old="+'\n\\end{thebibliography}\n'".replace('\n','\\n')
    # Backref scans a paragraph for each bibliography item, including the last.
    old="+'\\n\\end{thebibliography}\\n'"
    old=old.replace('\\end','\\\\end')
    new=old.replace("+'\\n", "+'\\n\\n",1)
    if old not in s:raise AssertionError('Bibliography paragraph anchor missing: '+repr(old))
    s=s.replace(old,new,1)
    old="head=(R/'supp.tex').read_text().split(r'\\input{sections/proofs67}')[0]"
    new="head=(R/'supp.tex').read_text().split(r'\\end{frontmatter}',1)[0]+r'\\end{frontmatter}'+'\\n'"
    if old not in s:raise AssertionError('Response frontmatter anchor')
    s=s.replace(old,new,1)
    anchor="    save(R/'audit/PRESERVATION70.json',record);return record"
    addition='''    intervening=json.loads((R/'audit/INTERVENING_SOURCE70.json').read_text())
    source=(R/'sections/training69-retained70.tex').read_text()
    statement_hashes=[hashlib.sha256(m[0].encode()).hexdigest() for m in re.finditer(r'\\\\begin\\{(?P<kind>theorem|proposition|lemma|corollary)\\}.*?\\\\end\\{(?P=kind)\\}',source,re.S)]
    proof_hashes=[hashlib.sha256(x.encode()).hexdigest() for x in re.findall(r'\\\\begin\\{proof\\}.*?\\\\end\\{proof\\}',(R/'sections/proofs70.tex').read_text(),re.S)]
    if not set(intervening['statement_sha256'])<=set(statement_hashes) or not set(intervening['proof_sha256'])<=set(proof_hashes):raise AssertionError('Intervening R69 statement/proof changed')
    layout=json.loads((R/'audit/LAYOUT70.json').read_text())
    for name,expected in layout['unchanged_content_sha256'].items():
        if sha(R/name)!=expected:raise AssertionError('Relocated full content changed '+name)
    record.update(intervening_propositions_preserved=len(intervening['statement_sha256']),intervening_proofs_preserved=len(intervening['proof_sha256']),relocated_full_content_verified=True)
'''
    if anchor not in s:raise AssertionError('Preservation audit anchor')
    s=s.replace(anchor,addition+anchor,1);put(p,s)
    for name,expected in unchanged.items():
        if digest(R/name)!=expected:raise AssertionError('Content changed during relocation '+name)
    record=dict(status='passed',unchanged_content_sha256=unchanged,relocations={'sections/decisions49.tex':'supp.tex, before the retained proof collection','tables/cold70.tex':'supp70.tex, complete workload section','tables/vector70.tex':'supp70.tex, complete workload section'},bibliography_fix='Explicit paragraph termination before end of bibliography; no entry content changed',response_fix='Use only frontmatter; do not inherit article sections into the response',scientific_records_modified=False)
    put(marker,json.dumps(record,sort_keys=True,indent=2)+'\n')
    p=R/'CONTENT_MAP70.md';put(p,p.read_text()+'\nThe complete legacy economic-inference section decisions49 is included unchanged in the active supplement. The cold70 and vector70 tables are included there without row deletion. Their current locations and source hashes are recorded in audit/LAYOUT70.json.\n')
    print(json.dumps(record,indent=2))
if __name__=='__main__':main()
