"""Materialize ordinary publication dependencies without changing frozen science."""
from pathlib import Path
import shutil,re,json,hashlib
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-10-r65'
def main():
    for name in ('econsocart.cls','econsocart.cfg','ecta-fullname.bst'):
        dest=R/name
        if not dest.exists():shutil.copy2(OLD/name,dest)
    for folder in ('sections','tables','publication'):
        (R/folder).mkdir(exist_ok=True)
        for source in (OLD/folder).rglob('*'):
            if source.is_file():
                dest=R/folder/source.relative_to(OLD/folder)
                if not dest.exists():dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
    marker=R/'audit/PROOF_LOCATIONS67.json'
    if not marker.exists():
        proofs=['\\section{Proofs of the inherited NBO results}\\label{supp:proofs67}\nThese proofs retain the original statements and arguments. Their placement in the supplement changes the reading order, not their hypotheses.\n']
        locations={};retained={}
        for name in ('core49','accuracy62-print','query63','gated64','localization65','decisions49'):
            source=(OLD/'sections'/(name+'.tex')).read_text();retained[name]=hashlib.sha256(source.encode()).hexdigest();index=[0]
            def move(m):
                index[0]+=1;before=source[:m.start()]
                labels=re.findall(r'\\label\{([^}]+)\}',before)
                theorems=re.findall(r'\\begin\{(?:theorem|proposition|lemma|corollary)\}.*?\\label\{([^}]+)\}',before,re.S)
                label=theorems[-1] if theorems else (labels[-1] if labels else name)
                plabel=f'supp:proof-{name}-{index[0]}'
                proofs.append('\\subsection{Proof of '+('Proposition' if name=='localization65' else 'the result')+' \\ref{'+label+'}}\\label{'+plabel+'}\n'+m[0]+'\n')
                locations[label]=plabel
                return '\\noindent The proof is in Supplement, Section~\\ref{'+plabel+'}.\n'
            (R/'sections'/(name+'.tex')).write_text(re.sub(r'\\begin\{proof\}.*?\\end\{proof\}',move,source,flags=re.S))
        (R/'sections/proofs67.tex').write_text('\n'.join(proofs))
        marker.parent.mkdir(exist_ok=True);marker.write_text(json.dumps(dict(prior_section_sha256=retained,proof_locations=locations),indent=2)+'\n')
    pre=(OLD/'preamble.tex').read_text().replace('\\RequirePackage[colorlinks','\\usepackage{xr-hyper}\n\\RequirePackage[colorlinks')
    (R/'preamble.tex').write_text(pre)
    entries=json.loads((OLD/'publication/bibliography-entries.json').read_text())
    entries['hoeffding1963']=r'''\bibitem[Hoeffding(1963)]{hoeffding1963}
\textsc{Hoeffding, Wassily} (1963): \enquote{Probability Inequalities for Sums of Bounded Random Variables,} \emph{Journal of the American Statistical Association}, 58 (301), 13--30.'''
    entries['sambharya2023']=r'''\bibitem[Sambharya, Hall, Amos, and Stellato(2023)]{sambharya2023}
\textsc{Sambharya, Rajiv, Georgina Hall, Brandon Amos, and Bartolomeo Stellato} (2023): \enquote{End-to-End Learning to Warm-Start for Real-Time Quadratic Optimization,} in \emph{Proceedings of the 5th Annual Learning for Dynamics and Control Conference}, 211, 220--234.'''
    (R/'publication/bibliography-entries.json').write_text(json.dumps(entries,indent=2,sort_keys=True)+'\n')
    bib=(OLD/'references.bib').read_text()+r'''
@article{hoeffding1963,author={Hoeffding, Wassily},title={Probability Inequalities for Sums of Bounded Random Variables},journal={Journal of the American Statistical Association},volume={58},number={301},pages={13--30},year={1963},doi={10.1080/01621459.1963.10500830}}
@inproceedings{sambharya2023,author={Sambharya, Rajiv and Hall, Georgina and Amos, Brandon and Stellato, Bartolomeo},title={End-to-End Learning to Warm-Start for Real-Time Quadratic Optimization},booktitle={Proceedings of the 5th Annual Learning for Dynamics and Control Conference},volume={211},pages={220--234},year={2023}}
'''
    (R/'references.bib').write_text(bib)
    (R/'build').mkdir(exist_ok=True);(R/'audit/build-logs').mkdir(parents=True,exist_ok=True)
    print('Ordinary publication dependencies present; frozen scientific sources unchanged.')
if __name__=='__main__':main()
