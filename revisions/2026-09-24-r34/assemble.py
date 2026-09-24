"""Assemble R34 without deleting any R32 main or supplementary source text."""
from pathlib import Path
import hashlib, json, shutil
ROOT=Path(__file__).resolve().parents[2]
R=ROOT/'revisions/2026-09-24-r34'; OLD=ROOT/'revisions/2026-09-24-r32'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def transform(s):return s.replace('2026-09-24-r32','2026-09-24-r34')

def main():
    (R/'paper/generated').mkdir(parents=True,exist_ok=True)
    for name in ('preamble.tex','references.tex'):
        (R/'paper'/name).write_text(transform((OLD/'paper'/name).read_text()).replace('Revision R32','Revision R34'))
    pre=R/'paper/preamble.tex'
    pre.write_text(pre.read_text()+'\\input{revisions/2026-09-24-r34/paper/generated/restart_macros}\n')
    refs=R/'paper/references.tex'
    refs.write_text(refs.read_text().replace('\\end{thebibliography}', '\\bibitem[Altman(1999)]{Altman1999}\nAltman, E. (1999): \\emph{Constrained Markov Decision Processes}. Chapman and Hall/CRC.\n\n\\end{thebibliography}'))
    import re
    reftext=refs.read_text()
    head,rest=reftext.split('\\bibitem',1)
    body,tail=rest.rsplit('\\end{thebibliography}',1)
    entries=['\\bibitem'+x for x in body.split('\\bibitem')]
    entries.sort(key=lambda e: re.search(r'\\bibitem\[[^]]*\]\{([^}]+)\}',e).group(1).lower())
    refs.write_text(head+''.join(entries)+'\\end{thebibliography}'+tail)
    for p in (OLD/'paper/generated').glob('*.tex'):shutil.copy2(p,R/'paper/generated'/p.name)
    source=(OLD/'paper/main.tex').read_text(); base=transform(source)
    text=base;inserts=[]
    def insert(marker,addition):
        nonlocal text
        assert text.count(marker)==1,marker
        text=text.replace(marker,addition+'\n\n'+marker);inserts.append(addition+'\n\n')
    insert('\\subsection{Relation to existing methods}',
       'A complementary global-cost result goes beyond the certified action class. We construct a lower operating witness from checked compression defects and solve unrestricted support Bellman problems for a fixed multiplier portfolio. Their values bound the implementation cost of every policy satisfying the original all-state operating constraint. A separately verified deployment supplies the upper bound and an explicit global cost gap. In the coupled application, all 18 installed-neural configurations receive less costly deployments than the conservative class minimum, without weakening the operating target. The remaining global gaps and the twelve zero-cost spline cases are reported alongside these improvements. A backward propagation then transmits future feasible intervention costs through the action-dependent transition law and enforces a necessary current operating inequality with local nonnegative multipliers. The propagated bound tightens 22 of the 42 global intervals while retaining every action and the same deployed policy. This step uses the simultaneous all-restart requirement and is distinct from simply adding a better scalarized candidate. The theory, cost account, and independent proof-object checks are developed together in Section~\\ref{sec:restart}. Classical constrained Markov control and its Lagrangian methods provide the underlying comparison principles \\citep{Altman1999}; our result constructs and checks their specific combination with the continuum of restart restrictions.')
    insert('\\section{Work, representation, and the role of proposals}',(R/'paper/global_theory.tex').read_text()+'\n'+(R/'paper/restart_theory.tex').read_text())
    insert('\\section{Coupled computational evidence}', 'The next section retains the original constructive-class benchmark and its execution records, including its fitting and timing evidence. Section~\\ref{sec:global-results} reports the newly executed unrestricted-cost study separately; inherited timings are not represented as measurements from the new machine.')
    insert('\\section{A global optimum at the active stopping boundary}',(R/'paper/global_results.tex').read_text()+'\n'+(R/'paper/restart_results.tex').read_text())
    text+='\nThe unrestricted support certificate further quantifies the distance between a feasible positive-cost revision and the true constrained cost optimum. Its lower bound concerns every feasible policy, while its upper bound comes from an independently checked deployment. This distinction allows substantial cost improvements to be reported together with their remaining global uncertainty, without equating exact scalarized computation with exact constrained optimality.\n'
    ending=text[len(text)-len('\nThe unrestricted support certificate further quantifies the distance between a feasible positive-cost revision and the true constrained cost optimum. Its lower bound concerns every feasible policy, while its upper bound comes from an independently checked deployment. This distinction allows substantial cost improvements to be reported together with their remaining global uncertainty, without equating exact scalarized computation with exact constrained optimality.\n'):]
    reverse=text.removesuffix(ending)
    for s in reversed(inserts):reverse=reverse.replace(s,'',1)
    assert reverse==base,'main source was deleted or altered beyond recorded path updates'
    (R/'paper/main.tex').write_text(text)
    suppbase=transform((OLD/'paper/supplement.tex').read_text())
    (R/'paper/supplement.tex').write_text(suppbase+'\n'+(R/'paper/global_supplement.tex').read_text()+'\n'+(R/'paper/restart_supplement.tex').read_text())
    author='\\begin{aug}\\author[id=au1,addressref={add1}]{\\fnms{Qian}~\\snm{QI}\\ead[label=e1]{qiqian@pku.edu.cn}}\\address[id=add1]{\\orgname{Peking University}}\\end{aug}'
    abstract='We study policy revision when implementation is costly and actions change future intervention exposure. We construct two-sided Bellman witnesses, unrestricted support problems, and a backward cost-bound propagation that uses operating feasibility at every restart. Their finite rational proof objects bound intervention cost over the full operating-feasible policy set, rather than only a certified local action class. In an action-dependent continuous-state maintenance economy, 42 deployments satisfy their uniform operating tolerances and preserve installed returns. All 18 installed-neural configurations reduce intervention cost relative to the class minimum. The restart propagation tightens 22 global cost intervals without changing the deployments or solving additional unrestricted support problems; twelve spline cases retain exact global optimality. An independent optimizer-free audit checks 294 certificates, and total construction and verification work is reported. We preserve the original stopped-control objective and its separately proved constant-control boundary optimum. Remaining positive global gaps are quantified.'
    docs={'ECTA':('Certified Bellman Operators with Neural Proposals: All-Restart Bounds for Costly Policy Revision','main'),
          'SUPP':('Supplement to Certified Bellman Operators: All-Restart Bounds for Costly Policy Revision','supplement'),
          'RESPONSE':('Response to the R30 Referee Report: Global Cost Bounds','response'),
          'COMPUTATION':('Computational Record for Revision R34','computation')}
    for stem,(title,body) in docs.items():
        s='\\input{revisions/2026-09-24-r34/paper/preamble}\n'
        if stem in ('SUPP','RESPONSE'):s+='\\usepackage{xr}\n\\externaldocument[art-]{ECTA_R34}\n'
        s+='\\begin{document}\\begin{frontmatter}\n\\title{'+title+'}\n\\runtitle{Certified Bellman Operators: R34}\n'+author+'\n'
        if stem=='ECTA':s+='\\begin{abstract}'+abstract+'\\end{abstract}\n\\begin{keyword}\\kwd{Bellman operators}\\kwd{Verified computation}\\kwd{Policy revision}\\kwd{Maintenance}\\kwd{Neural proposals}\\end{keyword}\n'
        s+='\\end{frontmatter}\n\\input{revisions/2026-09-24-r34/paper/'+body+'}\n'
        if stem=='ECTA':s+='\\clearpage\\input{revisions/2026-09-24-r34/paper/references}\n'
        s+='\\end{document}\n';(ROOT/f'{stem}_R34.tex').write_text(s)
    hist=R/'history';hist.mkdir(exist_ok=True)
    for stem in ('ECTA','SUPP','RESPONSE','COMPUTATION','HISTORY'):
        p=ROOT/f'{stem}_R32.pdf'
        if p.exists():shutil.copy2(p,hist/p.name)
        else:assert (hist/p.name).exists(),str(p)
    s='\\documentclass[11pt]{article}\n\\usepackage{pdfpages,hyperref}\n\\hypersetup{hidelinks,pdftitle={R34 historical annex}}\n\\begin{document}\n\\begin{center}\\Large Historical Annex to Revision R34\\end{center}\n'
    s+='This annex preserves the complete R32 article, supplement, referee response, computational record, and its existing historical annex. These are unchanged historical documents, not new R34 observations. Original sources and results remain on the frozen ancestor and in the inherited executed package. The current manuscript and global-cost evidence are in the separate R34 documents.\\clearpage\n'
    for stem in ('ECTA','SUPP','RESPONSE','COMPUTATION','HISTORY'):s+='\\includepdf[pages=-]{revisions/2026-09-24-r34/history/'+stem+'_R32.pdf}\n'
    s+='\\end{document}\n';(ROOT/'HISTORY_R34.tex').write_text(s)
    mapping={'parent':'88015b77a0c26e7b883156410b684b229fd7e86f','main_lossless_after_recorded_path_updates':True,
       'supplement_prefix_preserved':True,'path_updates':['2026-09-24-r32 -> 2026-09-24-r34 (input paths only)'],
       'source_sha256':{p.name:sha(p) for p in [OLD/'paper/main.tex',OLD/'paper/supplement.tex']},
       'new_sections':['paper/global_theory.tex','paper/global_results.tex','paper/global_supplement.tex','paper/restart_theory.tex','paper/restart_results.tex','paper/restart_supplement.tex'],
       'unchanged_historical_pdfs':{p.name:sha(p) for p in hist.glob('*.pdf')},
       'note':'No prior main/supplement text removed; new frontmatter and response are paired with unchanged full historical PDFs.'}
    (R/'PRESERVATION_MAP.json').write_text(json.dumps(mapping,indent=2,sort_keys=True))
    print('Assembled four Econometric Society documents and lossless historical annex.')

if __name__=='__main__':main()
