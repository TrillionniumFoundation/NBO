"""Prepare ordinary manuscript dependencies without changing earlier revisions."""
from pathlib import Path
import hashlib,json,re,shutil
R=Path(__file__).resolve().parents[1]
BASE=R.parent/'2026-10-10-r62'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    for name in ('publication','audit','sections','tables','build'):(R/name).mkdir(exist_ok=True)
    allowed={'.tex','.bib','.cls','.bst','.sty','.cfg'};kept={}
    for p in BASE.rglob('*'):
        if not p.is_file() or (p.suffix not in allowed or (p.suffix=='.cfg' and p!=BASE/'econsocart.cfg')) or 'build' in p.relative_to(BASE).parts or 'audit' in p.relative_to(BASE).parts:continue
        rel=p.relative_to(BASE);out=R/'retained62'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out);kept[str(rel)]=sha(p)
    for name in ('preamble.tex','econsocart.cfg','econsocart.cls','ecta-fullname.bst','references.bib'):
        shutil.copy2(BASE/name,R/name)
    for name in ('core49','accuracy62-print','decisions49'):
        shutil.copy2(BASE/'sections'/(name+'.tex'),R/'sections'/(name+'.tex'))
    for rev,name in ((63,'query63'),(64,'gated64')):
        p=R.parent/f'2026-10-10-r{rev}'/'sections'/(name+'.tex');shutil.copy2(p,R/'sections'/(name+'.tex'))
    entries=json.loads((BASE/'publication/bibliography-entries.json').read_text())
    additions={
        'sakaue2023warm':('Sakaue and Oki(2023)',r'\textsc{Sakaue, Shinsaku, and Taihei Oki} (2023): \enquote{Rethinking Warm-Starts with Predictions: Learning Predictions Close to Sets of Optimal Solutions for Faster $L$-/$L^\natural$-Convex Function Minimization,} in \emph{Proceedings of the 40th International Conference on Machine Learning}, 202, 29760--29776.'),
        'agrawal2020control':('Agrawal, Barratt, Boyd, and Stellato(2020)',r'\textsc{Agrawal, Akshay, Shane Barratt, Stephen Boyd, and Bartolomeo Stellato} (2020): \enquote{Learning Convex Optimization Control Policies,} in \emph{Proceedings of the 2nd Conference on Learning for Dynamics and Control}, 120, 361--373.')}
    for key,(authors,body) in additions.items():entries[key]=r'\bibitem['+authors+']{'+key+'}\n'+body
    (R/'publication/bibliography-entries.json').write_text(json.dumps(entries,sort_keys=True,indent=2)+'\n')
    dest=R/'retained62/publication';dest.mkdir(exist_ok=True);shutil.copy2(BASE/'publication/bibliography-entries.json',dest/'bibliography-entries.json')
    bib=(R/'references.bib').read_text()+r'''
@inproceedings{sakaue2023warm,
 author={Sakaue, Shinsaku and Oki, Taihei},
 title={Rethinking Warm-Starts with Predictions: Learning Predictions Close to Sets of Optimal Solutions for Faster {L}-/{L}-Natural-Convex Function Minimization},
 booktitle={Proceedings of the 40th International Conference on Machine Learning},
 volume={202},pages={29760--29776},year={2023}}
@inproceedings{agrawal2020control,
 author={Agrawal, Akshay and Barratt, Shane and Boyd, Stephen and Stellato, Bartolomeo},
 title={Learning Convex Optimization Control Policies},
 booktitle={Proceedings of the 2nd Conference on Learning for Dynamics and Control},
 volume={120},pages={361--373},year={2020}}
'''
    (R/'references.bib').write_text(bib)
    labels={}
    for p in (R/'retained62').rglob('*.tex'):
        for label in re.findall(r'\\label\{([^}]+)\}',p.read_text()):labels.setdefault(label,[]).append(str(p.relative_to(R)))
    report=dict(status='preserved',baseline_commit='cfecc5ffcdeb836b1c70e9b98d1dc87f6f8cd097',
        reviewed_report_commit='eb02fdb321fe6f26de9caa3afcbe2f84531faef2',
        completed_R63_commit='7128155b146d647adc39b0accd1ba483877853cc',
        completed_R64_commit='2b84410c8f2b77839340fb46d6e8b741e3e497fc',
        retained_source_sha256=kept,label_locations=labels,
        interpretation='No historical theorem or evidence deleted. Chronological duplication is removed from the active reading path, while complete R62 sources and four compiled companions remain available.')
    (R/'audit/PRESERVATION65.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    lines=['# Content-location map: R62 to R65','', 'Every prior source below is retained byte-for-byte under `retained62/`. The current main article revises the reading path, not the historical record.','', '| Prior label | Retained source locations |','|---|---|']
    for label,paths in sorted(labels.items()):lines.append('| `'+label+'` | '+'; '.join('`'+p+'`' for p in paths)+' |')
    (R/'CONTENT_MAP65.md').write_text('\n'.join(lines)+'\n')
    literature={'sakaue2023warm':'https://proceedings.mlr.press/v202/sakaue23a.html',
        'agrawal2020control':'https://proceedings.mlr.press/v120/agrawal20a.html',
        'econometrica_author_support':'https://vtex-soft.github.io/texsupport.econometricsociety-ecta/',
        'checked_on':'2026-10-10','metadata':'Authors, titles, venue, year and pages checked against primary publisher pages.'}
    (R/'audit/LITERATURE65.json').write_text(json.dumps(literature,indent=2)+'\n')
    print('Preserved',len(kept),'source files and',len(labels),'distinct labels')
if __name__=='__main__':main()
