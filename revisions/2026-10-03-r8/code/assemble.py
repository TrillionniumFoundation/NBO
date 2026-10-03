"""Integrate R7/R8 into the authoritative article while preserving its sources."""
from __future__ import annotations
import hashlib,json,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1]
EXPECTED={'ECTA.tex':'83a195c4b0dbde3b8aa356a5c83d143db3efa298','supp.tex':'b8b950657f4f4082353993e2b85e11168c55904f'}
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def paragraph(text,start,replacement):
    i=text.index(start);j=text.find('\n\n',i)
    if j<0:raise ValueError(start)
    return text[:i]+replacement+text[j:]
def assemble():
    (R/'archive').mkdir(exist_ok=True)
    sources={}
    for name,sha in EXPECTED.items():
        archive=R/'archive'/name.replace('.tex','.R7.tex')
        if not archive.exists():shutil.copyfile(ROOT/name,archive)
        b=archive.read_bytes();assert blob(b)==sha,(name,blob(b));sources[name]=b.decode()
    main=sources['ECTA.tex']
    abstract=r'''We develop Neural Bellman Operators for economic control with recursive utility, endogenous preferences, and strategic interaction. Policy evaluation and feasible improvement are separated from independent economic verification. A differential implementation yields full-domain certificates for trained nonlinear consumption policies. A positive-weight implementation trains preference policies and dynamic-game actors with full finite-model best responses. We then train continuous preference controls without exhaustive maximizing labels and construct budget-safe enclosures over the complete action box. These enclosures remain valid when action search is unresolved and distinguish numerical policy loss from continuous-economy approximation error. Matched direct, classical, gated-network, and projection comparisons identify the costs of actors and local improvement. Common-noise payoff comparisons diagnose state-coverage failures in coupled nonquadratic economies. The results connect learned policies to explicit value and deviation accounts while retaining separate conclusions for continuous-domain bounds, nodal certificates, and sampled high-dimensional diagnostics.'''
    main=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}'+'\n'+abstract+'\n'+r'\end{abstract}',main,flags=re.S)
    main=paragraph(main,'The paper makes three contributions.',r'''The paper makes three contributions. First, it specifies a map for policy evaluation and improvement whose derivative graph, feasible policy class, boundary data, and verification output are explicit. Second, it provides an operational error account that connects differential and positive-weight implementations: a complete-domain differential certificate for nonlinear consumption, and a budget-safe complete-action enclosure for a two-state endogenous-preference economy. The latter remains valid with unresolved action boxes and requires neither exact maximizing training labels nor concavity of the interpolated control objective. Third, it implements and compares these constructions for learned preference policies, coupled capital economies, and dynamic strategic agents. Recursive utility and temporal selves remain within the same economic formulation. Comparison, monotonicity, and approximate policy iteration are inherited mathematical ingredients; the implemented maps, explicit action-oracle distinction, and verified economic computations are the objects studied here.''')
    main=paragraph(main,'The numerical program now includes',r'''The numerical program uses generic multilayer critics and actors as well as clearly separated analytical laboratories. The finite preference and game studies train actors using exhaustively constructed continuation-payoff labels; their results establish neural policy representation, not avoided maximization. The continuous-action preference study instead differentiates the actor's own payoff, records local improvement as a hybrid policy, and reserves global action covering for independent verification after training. Direct optimization and an actor-free search ablation expose which parts of the computation produce the measured policy quality. Additional gated and projection comparisons exploit the same economic problem rather than weakening the baseline. Dense nonlinear capital experiments use paired pathwise payoffs to diagnose state coverage. Homothetic portfolios, temporal-self formulas, the nonsmooth exit problem, and the exact quadratic family remain distinct economic and algebraic checks. No matrix calculation is counted as neural training, and no grid refinement difference is silently converted into a continuous-time bound.''')
    main=main.replace(r'\input{revisions/2026-09-29-r6/manuscript/operator.tex}',r'\input{revisions/2026-09-29-r6/manuscript/operator.tex}'+'\n'+r'\input{revisions/2026-10-03-r8/manuscript/method.tex}')
    for name in ['ndu','games']:
        main=main.replace(r'\input{revisions/2026-09-29-r6/manuscript/'+name+'.tex}',r'\input{revisions/2026-10-03-r8/manuscript/'+name+'.tex}')
    main=main.replace(r'\input{revisions/2026-09-29-r6/manuscript/coupled.tex}',r'\input{revisions/2026-09-29-r6/manuscript/coupled.tex}'+'\n'+r'\input{revisions/2026-10-03-r8/manuscript/coverage.tex}')
    main=paragraph(main,'The computations now connect',r'''The computations connect trained multilayer policies to explicit economic error accounts. The stopped-consumption certificate covers the continuous differential domain; the preference-action cover verifies the entire control box on a two-state nodal economy; and the game calculation checks full dynamic unilateral deviations, including deviations from profiles with imperfect fitted one-step equilibria. Non-enumerative continuous actor training, direct control optimization, local-search ablation, gated regression, and projection comparisons disclose both successful policy computations and the cost of the actor. Paired high-dimensional payoff comparisons identify state-coverage failures without claiming an optimality certificate. The continuous economic agenda remains unchanged. Its numerical implementation is sharpened by distinguishing the policy proposed, the computation actually executed, and the domain over which its value or deviation bound has been established.''')
    marker=r'\section{Replication and Scope of Numerical Evidence}\label{app:replication}'
    addition=r'''\paragraph*{Integrated R8 candidate.}
The present article incorporates the following immutable repository inputs.
\begin{quote}\small
R7 source: \texttt{5bab4649728860fb655c5371f3705787f10b4a78}\\
R7 evidence: \texttt{b1409008625f550195ce9ead468391ad2449a240}\\
R7 advisory report: \texttt{c63f6817f498e1cfe9a653139f7a25bf44a4418a}
\end{quote}
The preceding main manuscript and supplement are preserved by exact Git blob identity in the R8 archive. R8 source, all executed development configurations, raw arrays, independent certificates, method-paired comparisons, generated tables, and compilation logs belong to the candidate itself. The response answers every B1--B7 and M1--M9 comment of the latest report. The later unexecuted R7 development protocol is not imported as evidence. A table manifest checks each printed number against its input file; the execution manifest identifies the exact R8 source and candidate workflow. Earlier review and revision branches remain unchanged.
'''
    main=main.replace(marker,marker+'\n'+addition)
    supp=sources['supp.tex']
    supp=paragraph(supp,'The inherited portfolio and quadratic laboratories',r'''The inherited portfolio and quadratic laboratories retain their declared exact-structure classes. R6 trains generic multilayer policies in stopped consumption, preference adjustment, and dense nonlinear capital economies. R7 adds successful finite preference actors, neural game policies with full dynamic best responses, common-noise coverage records, and an independent arithmetic replay. R8 integrates those results and adds continuous-action training without maximizing labels, complete-action enclosures, direct and projection comparisons, and a separate continuous-transfer theorem. These approximation and verification classes are distinguished throughout the supplement.''')
    supp=supp.replace('The broader deep-BSDE and neural-game comparisons remain distinct unexecuted alternatives; they are not counted as measured advantages.', 'The broader deep-BSDE comparison remains unexecuted and is not counted as a measured advantage. R7 neural-game evidence and the additional R8 comparisons are reported in the integrated sections below.')
    supp=supp.replace(r'\end{document}',r'\input{revisions/2026-10-03-r8/manuscript/supplement.tex}'+'\n'+r'\end{document}')
    # Historical paragraphs stay available in full, but their compiled copy
    # uses a textual cross-document pointer rather than an undefined label.
    old=(ROOT/'revisions/2026-09-29-r6/manuscript/ndu.tex').read_text()
    old=old.replace(r'\eqref{eq:accounts-r6}',r'the main-text Bellman error accounts')
    (R/'manuscript/history_ndu.tex').write_text(old)
    extra=R/'manuscript/supplement.tex';s=extra.read_text().replace(r'\input{revisions/2026-09-29-r6/manuscript/ndu.tex}',r'\input{revisions/2026-10-03-r8/manuscript/history_ndu.tex}');extra.write_text(s)
    main=re.sub(r'\\texttt\{([0-9a-f]{40})\}',lambda m:r'\texttt{'+r'\allowbreak '.join(m.group(1)[j:j+8] for j in range(0,40,8))+'}',main)
    (ROOT/'ECTA.tex').write_text(main);(ROOT/'supp.tex').write_text(supp)
    oldlabels=set(re.findall(r'\\label\{([^}]+)\}',sources['ECTA.tex']));newlabels=set(re.findall(r'\\label\{([^}]+)\}',main));assert oldlabels<=newlabels
    info=dict(archive_git_blobs=EXPECTED,root_labels_preserved=sorted(oldlabels),
        current_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in EXPECTED},
        topic_and_author_preserved=True,root_manuscripts_integrated=True)
    (R/'INTEGRATION_MANIFEST.json').write_text(json.dumps(info,indent=2)+'\n')
if __name__=='__main__':assemble()
