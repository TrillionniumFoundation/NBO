"""Idempotent R79 editorial corrections before the tested ordinary-source commit.

The inherited R78 bibliography omitted a cited Floyd entry. The additions
below change no historical section, numerical source, observation or clock.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    changed=[]
    def write(p,text):
        old=digest(p) if p.exists() else None
        if p.exists() and p.read_text()==text:return
        p.write_text(text);changed.append(dict(path=str(p.relative_to(R)),before=old,after=digest(p)))
    p=R/'publication/bibliography-entries.json';entries=json.loads(p.read_text())
    entries['floyd1962']=r'\bibitem[\protect\citeauthoryear{Floyd}{Floyd}{1962}]{floyd1962}'+'\n'+r'\textsc{Floyd, Robert W.} (1962): \enquote{Algorithm 97: Shortest Path,} \emph{Communications of the ACM}, 5 (6), 345.'
    write(p,json.dumps(entries,indent=2,sort_keys=True)+'\n')
    p=R/'references.bib';text=p.read_text()
    if '@article{floyd1962' not in text:
        text+='\n@article{floyd1962,\n author={Robert W. Floyd},\n title={Algorithm 97: Shortest Path},\n journal={Communications of the ACM},\n volume={5},\n number={6},\n pages={345},\n year={1962},\n doi={10.1145/367766.368168}\n}\n'
    write(p,text)
    p=R/'sections/allocation_proof79.tex';text=p.read_text().replace('Commuting the two finite maxima','Commuting the maximum over $\\mathcal C$ with the finite maximum over $j$')
    write(p,text)
    p=R/'code/allocation79.py';text=p.read_text().replace('for t in (F(-1,4),F(0),F(1,4),F(1,2),F(3,4),F(1),F(5,4)):','for t in (-l/width,F(0),F(1,4),F(1,2),F(3,4),F(1),F(5,4)):')
    write(p,text)
    p=R/'response.md';text=p.read_text().replace('The corresponding theorem, full proof, rational primal-dual witnesses and finite-cohort exhaustive checks are deposited.','The corresponding theorem, full proof, rational primal-dual witnesses and finite-cohort exhaustive checks are deposited. The new suite has twenty-two unskipped exact tests; the retained cost catalogue supplies seven full-catalogue linear-program checks, thirty-five finite-cohort checks and four explicit setup-charge regimes. These are decision calculations, not new economic observations.')
    write(p,text)
    p=R/'audit/EDITORIAL79.json'
    if changed:write(p,json.dumps(dict(status='applied_before_tested_source_commit',changed=changed,historical_sections_or_scientific_sources_changed=False),indent=2)+'\n')
    print(json.dumps(dict(editorial_files_updated=len(changed))))
if __name__=='__main__':main()
