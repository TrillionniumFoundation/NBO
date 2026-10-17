"""Narrow editorial repair; preserve the failed attempt and all scientific rows."""
from pathlib import Path
import hashlib,json,re,shutil
R=Path(__file__).resolve().parents[1]

def main():
    marker=R/'audit/LAYOUT92.json'
    if marker.exists():
        print('R92 editorial repair already integrated; no overwrite.');return
    backup=R/'preserved/R92-before-layout';backup.mkdir(parents=True,exist_ok=True)
    for name in ('response.md','references92.bib','references92-canonical.bib','sections/centeredrisk92.tex','LITERATURE92.md'):
        p=R/name;q=backup/name;q.parent.mkdir(parents=True,exist_ok=True)
        if q.exists():raise AssertionError('Conflicting preserved editorial input '+name)
        shutil.copy2(p,q)
    # Preserve every actual failure and its document hashes before the rerun.
    old=R/'audit/reproduction92'
    if old.exists():shutil.copytree(old,backup/'reproduction92')
    p=R/'response.md';text=p.read_text()
    hashes=('b030d87d7e96440eb25a3178c94ee6a87940cdb0','368a9e754f5de04eb1957e152f22d6ef2c34f2fe')
    for h in hashes:
        if text.count(h)!=1:raise AssertionError('Unexpected response provenance occurrence')
        text=text.replace(h,r'\nolinkurl{'+h+'}')
    p.write_text(text)
    extra=r'''
@article{ruszczynski2014erratum,
  author = {Ruszczy{\'n}ski, Andrzej},
  title = {Erratum to: Risk-Averse Dynamic Programming for {Markov} Decision Processes},
  journal = {Mathematical Programming},
  volume = {145},
  pages = {601--604},
  year = {2014},
  doi = {10.1007/s10107-014-0783-z}
}
'''
    for name in ('references92.bib','references92-canonical.bib'):
        p=R/name;text=p.read_text()
        if 'ruszczynski2014erratum' in text:raise AssertionError('Erratum key already present; inspect before integrating')
        p.write_text(text+extra)
    p=R/'sections/centeredrisk92.tex';text=p.read_text()
    oldcite=r'\citep{ruszczynski2010risk}'
    if text.count(oldcite)!=1:raise AssertionError('Risk attribution occurrence')
    text=text.replace(oldcite,r'\citep{ruszczynski2010risk,ruszczynski2014erratum}')
    p.write_text(text)
    p=R/'LITERATURE92.md';p.write_text(p.read_text()+'''\nThe publisher record was additionally checked directly: https://link.springer.com/article/10.1007/s10107-010-0393-3 . Its linked 2014 erratum, Mathematical Programming 145, 601--604, DOI 10.1007/s10107-014-0783-z, acknowledges a gap in the original Theorem 2: https://link.springer.com/article/10.1007/s10107-014-0783-z . The R92 attribution now cites the erratum as well. The new proof assumes the stated measurable original recursions and selection conditions explicitly and does not import an unconditional existence result from the uncorrected theorem.\n''')
    marker.parent.mkdir(parents=True,exist_ok=True)
    marker.write_text(json.dumps({'status':'integrated','scope':'Breakable provenance hashes in response; corrected prior-work attribution. No diagnostic primitive or certificate algorithm changed.',
        'preserved_failure':'preserved/R92-before-layout/reproduction92',
        'preserved_inputs':{str(p.relative_to(backup)):hashlib.sha256(p.read_bytes()).hexdigest() for p in backup.rglob('*') if p.is_file() and 'reproduction92' not in p.parts}},indent=2)+'\n')
    print('R92 response typography and erratum attribution integrated; previous failure retained.',flush=True)
if __name__=='__main__':main()
