"""Assemble ordinary source files; the active manuscript extends the R49 paper."""
from pathlib import Path
import re,json,shutil,hashlib,difflib
R=Path(__file__).resolve().parents[1]
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    old=(R/'preserved/R49/ECTA.tex').read_text();text=old
    abstract=r'''This paper develops Neural Bellman Operators for policy evaluation and feasible improvement in controlled economies. A constructive own-future continuation retains feasible action witnesses; exact native and affine--ReLU realizations preserve the same policy. A centered reference-policy advantage converts signed evaluation bands into a cell-wise acceptance rule that cannot increase the incumbent's cost. Its quantitative expectation version measures the discounted gain along the implemented policy. We execute an exact final-date specialization in the original nonlinear investment economies, with continuous uncertainty and acquired-state feasibility. Prospective resource allocation and complete work records separate construction, certification and direct policy evaluation. The experiments identify strictly positive cost reductions for every studied witness incumbent, while generally retaining the conventional method's lower cost. Simultaneous actual-cost intervals support finite-catalogue resource and replacement decisions without treating a sharper certificate as a better policy. The original theory, economic applications and adverse comparisons are preserved in the complete development edition.'''
    text=re.sub(r'(?<=\\begin\{abstract\}).*?(?=\\end\{abstract\})',lambda m:'\n'+abstract+'\n',text,flags=re.S)
    text=text.replace('and a curvature-refined conventional generator that can actually realize nonuniform axes.','and two separately recorded conventional refinement rules. The original curvature-bisection block remained uniform; the later graded block was nonuniform. A new residual-driven comparator below records its realized geometry and all pilot work.')
    text=text.replace('The evidence must determine where certificate sharpness compensates for construction cost; no uniform neural dominance is built into the design.','The evidence must determine the cost of the returned policy as well as certificate sharpness. No uniform neural dominance is built into the design.')
    anchor='\\input{sections/core49}'
    intro=r'''The additional improvement result addresses the economically important case where the certified construction returns a more costly policy than a conventional competitor. We preserve that incumbent and permit only actions whose actual reference advantage is certified nonpositive after the numerical and observation allowances. At the final date of the original investment model, exact continuous-law integration makes this gate executable without assuming a successful policy-value fit. Both generators receive the same repair. The resulting experiment isolates removable final-action loss from the policy gap that remains; it does not rename the compiler as a uniquely neural advantage.

'''
    text=text.replace(anchor,intro+anchor+'\n\\input{sections/improvement50}')
    text=text.replace('\\input{sections/decisions49}','\\input{sections/decisions49}\n\\input{sections/frontier50}')
    text=text.replace('\\input{sections/study49}','\\input{sections/study49}\n\\input{sections/study50}')
    conclusion=r'''The cost-directed result adds a further positive statement: a feasible acquired policy can be improved without sacrificing its incumbent cost guarantee, provided its centered advantage is verified. In the executed final-stage specialization every studied witness incumbent has a strictly positive identified reduction under the declared initial law. Most witness--FVI differences remain unfavorable after both methods are repaired. The improvement theorem and this comparative observation are consistent: safe improvement relative to an incumbent is not dominance over another method.

'''
    text=text.replace('Neural Bellman Operators therefore provide',conclusion+'Neural Bellman Operators therefore provide')
    before=text.index('This article and its technical supplement are the primary R49 exposition.')
    after=text.index('\\bibliographystyle',before)
    newmap=r'''This article and its technical supplement are the active R50 exposition of the same paper. Every R49 main-article and supplementary label is retained in its corresponding current document. The complete development editions retain the R48 main and supplementary bodies and add the current theory and evidence, with a reading notice distinguishing historical wording from the active empirical account. The original R49 sources remain unchanged under \texttt{preserved/R49}; R48 sources and earlier theory/application companions are likewise retained. Preservation is not a new mathematical validation of every historical application.

The local revision contains ordinary sources, both immutable R49 evidence archives, the R48 publication input, newly executed records, generated tables, a point-by-point response and compiled documents. The direct numerical correction retains its original observations and replays the same streams with explicitly outward cross-policy subtraction. The corrected intervals, not their raw predecessors, govern the active direct-cost tables. Source and evidence identities are checked before a clean offline Git-archive rebuild. The local delivery record distinguishes a completed build from a remote publication: no remote branch or commit is claimed without a confirmed push. This limitation is administrative, not a substitute for the substantive revised manuscript.

'''
    text=text[:before]+newmap+text[after:]
    (R/'ECTA.tex').write_text(text)
    supp=(R/'preserved/R49/supp.tex').read_text().replace('for the R49 revision','for the retained R49 evidence and the R50 revision')
    supp=supp.replace('All earlier proofs remain in the complete development supplement.','The added reference-advantage and terminal-improvement proofs are included here; all earlier proofs remain in the complete development supplement.')
    pos=supp.index('\\section{Complete construction records}')
    supp=supp[:pos]+'\\input{sections/proofs50}\n'+supp[pos:]
    supp=supp.replace('\\bibliographystyle',r'''\section{Every R50 actual-cost interval and mechanism record}\label{supp:records50}
The following tables use the corrected outward-subtraction replay. C denotes the separate common-accuracy block, P the primary target-five plan, Q the primary target-two plan, O the original R49 target-two policies, A residual-driven FVI, and I the isotropic block. U is the uniform initial law; L, M and H denote point laws at 1/8,1/2 and 7/8 in every coordinate. Each group has four absolute costs and six contrasts; the table lists all 280 estimands. Printed endpoints are rounded for display. Exact rational endpoints and source-bound moments govern inference.
\input{tables/all-costs50}
\input{tables/all-contrasts50}
\input{tables/mechanism50}
\input{tables/work50}

\section{Numerical correction and sequential common-accuracy design}\label{supp:corrections50}
The primary shared allocation is sufficient for the witness bound, not automatically for conventional FVI's actual interpolated modulus. Its failed certificates are retained. The common-accuracy amendment was specified after that outcome and frozen before its own execution; it charges every failed construction before doubling the state quota. It is not a retrospective recoding of the primary study.

During publication review, nearest-rounded subtraction of different policies' already outward path endpoints was replaced by directed outward subtraction. The same bin streams, policies and sample counts were replayed. Original sources and results remain unchanged; a separate correction manifest binds the new evaluator, and the audit checks identical streams and unchanged sign classifications. Replaying the same observations adds no statistical sample size. The additive raw prefix field for coefficient-bit descriptors is not interpreted as a maximum; maximum bit length and live storage are reconstructed separately. The correction and development logs are part of the release.

\bibliographystyle''',1)
    (R/'supp.tex').write_text(supp)
    # Complete editions preserve all baseline exposition and labels.
    for kind,basefile,active in [('complete','ECTA.tex',text),('complete-supp','supp.tex',supp)]:
        base=(R/'preserved/R48'/basefile).read_text()
        base=re.sub(r'\\input\{(sections|tables)/([^}]+)\}',r'\\input{preserved/R48/\1/\2}',base)
        if kind=='complete-supp':base=base.replace('{build/ECTA}','{build/complete}')
        body=active[active.index('\\section{'):active.index('\\bibliographystyle')]
        # Remove only the division command; all section text and labels remain.
        body=body.replace('\\appendix','')
        notice=r'''\section*{Reading notice for the complete development edition}
This volume retains the baseline development verbatim, including historical descriptions, followed by the current R50 argument. Its historical reference to a formerly authoritative revision is not a second current scientific claim. The active article, technical supplement and response govern the new evidence and numerical corrections. Every baseline result and its original assumptions remain available for examination.
'''
        base=base.replace('\\end{frontmatter}','\\end{frontmatter}\n'+notice,1)
        base=base.replace('\\bibliographystyle','\\clearpage\n\\section*{Current R50 development}\n'+body+'\n\\bibliographystyle',1)
        (R/(kind+'.tex')).write_text(base)
    labels=lambda t:set(re.findall(r'\\label\{([^}]+)\}',t))
    def expand(path,seen=None):
        seen=set() if seen is None else seen
        path=Path(path)
        if path in seen:return ''
        seen.add(path);v=path.read_text()
        def sub(m):
            f=R/(m[1]+('' if m[1].endswith('.tex') else '.tex'))
            return expand(f,seen) if f.exists() else m[0]
        return re.sub(r'\\input\{([^}]+)\}',sub,v)
    maps={}
    for name in ('ECTA','supp'):
        baseline=(R/'preserved/R49'/(name+'.tex')).read_text()
        for p in (R/'preserved/R49/sections').glob('*.tex'):baseline+='\n'+p.read_text() if name=='ECTA' else ''
        now=expand(R/(name+'.tex'));missing=labels(baseline)-labels(now)
        assert not missing,(name,missing)
        maps[name]={'R49_labels_retained':len(labels(baseline)),'new_total_labels':len(labels(now)),'missing':sorted(missing)}
    # Complete edition coverage, directly expanding baseline paths separately.
    for name,complete in [('ECTA','complete'),('supp','complete-supp')]:
        baseline=(R/'preserved/R48'/(name+'.tex')).read_text()
        for m in re.finditer(r'\\input\{([^}]+)\}',baseline):
            p=R/'preserved/R48'/(m[1]+'.tex')
            if p.exists():baseline+='\n'+p.read_text()
        missing=labels(baseline)-labels(expand(R/(complete+'.tex')));assert not missing,missing
        maps[complete]={'R48_labels_retained':len(labels(baseline)),'missing':sorted(missing)}
    files={str(p.relative_to(R)):H(p) for p in (R/'preserved').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    (R/'audit/PRESERVATION.json').write_text(json.dumps({'label_maps':maps,'preserved_sha256':files,'historical_files_modified':False},indent=2)+'\n')
    for name in ('ECTA','supp'):
        a=(R/'preserved/R49'/(name+'.tex')).read_text().splitlines(True);b=(R/(name+'.tex')).read_text().splitlines(True)
        (R/'audit'/(name+'-R49-to-R50.diff')).write_text(''.join(difflib.unified_diff(a,b,fromfile='R49/'+name+'.tex',tofile='R50/'+name+'.tex')))
    print(json.dumps(maps))
if __name__=='__main__':main()
