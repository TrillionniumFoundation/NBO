"""Create ordinary R72 sources, preserving the entire preceding active text.

Run once before author editing. The frozen scientific sources and observations
are not overwritten. Manuscript reorganization is recorded at byte level.
"""
from pathlib import Path
import hashlib,json,re,shutil
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-11-r70'
MAIN=('core49','accuracy62-print','query63','operational67','vector67','centered69')
SUPP=('proofs67','proofs70')
APP=('decisions49','gated64','localization65','training69-retained70','deployment70','study70','supp70')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def main():
    if (R/'audit/PREPARATION72.json').exists():
        print('R72 ordinary sources exist; preserving author edits.');return
    for name in ('sections','tables','publication'):
        shutil.copytree(OLD/name,R/name,dirs_exist_ok=True)
    for p in OLD.iterdir():
        if p.is_file() and p.suffix in ('.cls','.cfg','.sty','.bst','.bib') or p.name=='preamble.tex':
            if p.is_file():shutil.copy2(p,R/p.name)
    prior=R/'preserved/R70';prior.mkdir(parents=True,exist_ok=True)
    for name in ('ECTA.tex','supp.tex','response.md','README.md','CONTENT_MAP70.md'):
        shutil.copy2(OLD/name,prior/name)
    own={}
    for doc,names in (('ECTA',MAIN),('supp',SUPP),('appendix',APP)):
        for name in names:
            path='sections/'+name+'.tex';own[path]=dict(document=doc,sha256=sha(OLD/path))
    old_inputs=set(re.findall(r'\\input\{(sections/[^}]+)\}',(OLD/'ECTA.tex').read_text()+(OLD/'supp.tex').read_text()))
    if old_inputs!={k[:-4] for k in own}:raise AssertionError(('Unassigned old text',old_inputs-{k[:-4] for k in own}))
    front=(OLD/'ECTA.tex').read_text().split('\\begin{abstract}',1)[0]
    # New front matter and ordinary source files are authored separately.
    save(R/'audit/PREPARATION72.json',dict(baseline_commit='b576584cb5b1ff5ceccbcf37a3fa6e1ac613aca6',
        controlling_review_commit='4b27b56f4514f6c1d77b69fe707f7202f8b06b19',
        unchanged_active_sections=own,prior_files={str(p.relative_to(R)):sha(p) for p in prior.iterdir()},
        original_main_sha256=sha(OLD/'ECTA.tex'),original_supp_sha256=sha(OLD/'supp.tex'),
        statement_preservation='Every prior active section is compiled unchanged in exactly one of main article, technical supplement or numerical/development appendix.',
        historical_directories_modified=False))
    entries=json.loads((R/'publication/bibliography-entries.json').read_text())
    entries['munos2006variance']=r'\bibitem[\protect\citeauthoryear{Munos}{Munos}{2006}]{munos2006variance}'+'\n'+r'\textsc{Munos, R\'{e}mi} (2006): \enquote{Geometric Variance Reduction in Markov Chains: Application to Value Function and Gradient Estimation,} \emph{Journal of Machine Learning Research}, 7 (14), 413--427.'
    save(R/'publication/bibliography-entries.json',entries)
    bib=R/'references.bib'
    bib.write_text(bib.read_text()+'''\n@article{munos2006variance,
 author={R{\\'e}mi Munos},
 title={Geometric Variance Reduction in Markov Chains: Application to Value Function and Gradient Estimation},
 journal={Journal of Machine Learning Research}, year={2006}, volume={7}, number={14}, pages={413--427}
}\n''')
    print(json.dumps(dict(status='prepared',unchanged_active_sections=len(own))))
if __name__=='__main__':main()
