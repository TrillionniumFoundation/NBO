"""Deterministic editorial integration; immutable roots and byte-exact moves."""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1]

def integrate():
    archive=R/'archive';archive.mkdir(parents=True,exist_ok=True)
    for name,target in [('ECTA.tex','ECTA.r10.tex'),('supp.tex','supp.r10.tex'),('revision_reference.bib','revision_reference.r10.bib')]:
        if not (archive/target).exists():(archive/target).write_bytes((ROOT/name).read_bytes())
    old=(archive/'ECTA.r10.tex').read_text();supp=(archive/'supp.r10.tex').read_text()
    if hashlib.sha1(b'blob '+str(len(old.encode())).encode()+b'\0'+old.encode()).hexdigest()!='890669be4a9ab17f1e6a280eb8cbdca9bdb4cce2':raise RuntimeError('not the pinned R10 main root')
    begin=old.index('\\section{Analytical and Nonsmooth Benchmarks}')
    end=old.index('\\input{revisions/2026-10-04-r10/manuscript/continuous.tex}')
    applications=old[begin:end]
    ap=old.index('\\begin{appendix}');bib=old.index('\\bibliographystyle{ecta-fullname}')
    proofs=old[ap:bib]
    (R/'manuscript/retained_applications.tex').write_text(applications)
    (R/'manuscript/retained_proofs.tex').write_text(proofs)
    source=old[:begin]+old[end:ap]
    # Main bibliography follows the new conclusion; all previous proofs are moved intact.
    source=source.replace('\\input{revisions/2026-10-04-r10/manuscript/study.tex}', '\\input{revisions/2026-10-04-r11/manuscript/policy_specific.tex}\n\\input{revisions/2026-10-04-r11/manuscript/learning.tex}\n\\input{revisions/2026-10-04-r11/manuscript/study.tex}')
    concl=source.index('\\section{Conclusion}');priorcon=source[concl:]
    (R/'manuscript/retained_conclusion.tex').write_text('\\section{Prior Concluding Discussion (R10)}\n'+priorcon.split('\n',1)[1])
    source=source[:concl]+r'''\section{Conclusion}\label{sec:conclusion}
Neural Bellman Operators connect policy evaluation, feasible improvement, and independent economic error accounting. The capital application now distinguishes an architectural performance envelope from a policy-specific post-training certificate. A paired payoff identity, explicit diffusion-transfer estimate, and finite-family sampling bound identify the value of a deployed neural correction relative to an analytical schedule. The economic comparison remains the original continuous problem and its full adapted policy class.

The rollout-costate implementation evaluates the current policy before improving its Hamiltonian. Direct-policy, affine, and tuned critic-greedy comparisons expose the cost and accuracy of that implementation without presuming its superiority. A positive verified gain is evidence about a particular deployed policy; it is neither an optimizer convergence theorem nor a claim about every initialization. The reported improvement is a quantitative result in the stated stylized economy, not an empirical calibration.

Recursive utility, endogenous preferences, sophisticated temporal selves, dynamic games, viscosity selection, and stochastic traces remain within the paper's economic program. Their full equations and evidence are retained in the supplement, with their own domains and verification hypotheses. Extending the new diffusion-transfer calculation to other observation rules, state-dependent diffusion, recursive utility, or stopping boundaries requires those additional error terms to be verified. The present theorem does not silently supply them.

'''+old[bib:]
    abstract=r'''We develop Neural Bellman Operators for economic control with recursive utility, endogenous preferences, and strategic interaction. Policy evaluation, feasible improvement, and verification are separate maps. A policy-specific continuous-time certificate connects a trained capital policy to the original economic optimum through a paired payoff identity, an explicit diffusion-transfer bound, and finite-family statistical inference. The deployed controller is specified by its observed innovations and sampled implementation; the economic state is not discretized or truncated in the guarantee. Unlike an architectural tube bound, the new endpoint depends on the fitted policy and can become tighter than the analytical schedule's bound. A rollout-costate implementation trains generic actors and critics in dense nonquadratic economies of dimensions ten, twenty, and fifty. Ten-seed comparisons include direct policy optimization, affine policies, tuned critic greedification, and accuracy--cost frontiers. The remaining economic applications retain their separate verification accounts. The results distinguish learned economic improvement, numerical safety, and method comparison without presuming optimizer convergence or universal neural superiority.'''
    source=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:'\\begin{abstract}\n'+abstract+'\n\\end{abstract}',source,flags=re.S)
    source=source.replace('The paper makes three connected contributions.', 'The paper makes four connected contributions.')
    marker='The numerical program uses generic multilayer critics and actors'
    where=source.index(marker)
    source=source[:where]+r'''Fourth, an independently verified paired improvement tightens the continuous-capital policy bound after training. The evaluation block uses current-policy rollout and costate targets, while verification refers to a separately specified innovation-driven sampled controller. A new transfer estimate does not require a global derivative bound for the learned policy. The final experiment measures improvement relative to the analytical schedule with ten training seeds, explicit time-discretization and sampling uncertainty, and stronger tuned baselines. It preserves all earlier adverse evidence.

'''+source[where:]
    source=source.replace('The continuous-capital result closes a different part of the error account:', 'The inherited continuous-capital result closes a different part of the error account:')
    a=source.index('Section~\\ref{sec:model} specifies');b=source.index('\\section{The Controlled Economy}',a)
    source=source[:a]+r'''Section~\ref{sec:model} specifies the controlled economy, Section~\ref{sec:method} defines the NBO map, and Section~\ref{sec:theory} establishes the general error accounts. The continuous-capital theorem supplies an analytical benchmark. Sections~\ref{sec:r11specific}--\ref{sec:r11study} complete the policy-specific verification, algorithm, and economic comparison. The supplement retains the full recursive-utility, preference, temporal-self, game, and scalability applications, all previous proofs, and the new transfer and arithmetic proofs.

'''+source[b:]
    # Add the two-way reference import before the document starts.
    source=source.replace('\\begin{document}',r'\usepackage{xr}'+'\n'+r'\externaldocument{revisions/2026-10-04-r11/build/supp_refs}'+'\n'+r'\begin{document}',1)
    (ROOT/'ECTA.tex').write_text(source)
    # Use the full main mathematical preamble so relocated material needs no editing.
    pre=old.split('\\begin{document}',1)[0]
    body=supp.split('\\begin{document}',1)[1]
    body=body.replace('\\section{Relation to the Main Text}',r'''\section{Organization of the Revised Supplement}
The new policy-specific proofs appear first. The inherited supplement follows, with its historical iteration labels retained. Full application sections, prior proofs, and the R10 comparison are reproduced later without deleting their mathematical content. The corresponding main-text roots are archived by exact byte identity. Historical statements about the then-current revision are read in that temporal context; the R11 protocol, results, and response identify the present evidence.
\input{revisions/2026-10-04-r11/manuscript/proofs.tex}
\section{Relation to the Main Text}''',1)
    # Relabel historical repetitions and repair repeated longtable captions in
    # new copies only. Every original source remains unchanged in its folder.
    rel=str(R.relative_to(ROOT))
    history_map={
      'revisions/2026-10-03-r8/manuscript/history_ndu.tex':('history_ndu_layout.tex','sec:ndu-neural','sec:ndu-neural-r6-history'),
      'revisions/2026-09-29-r6/manuscript/games.tex':('history_games_layout.tex','sec:dynamic-computation','sec:dynamic-computation-r6-history')}
    r8path='revisions/2026-10-03-r8/manuscript/supplement.tex'
    r8text=(ROOT/r8path).read_text()
    for oldpath,(name,oldlabel,newlabel) in history_map.items():
        copy=(ROOT/oldpath).read_text().replace('{'+oldlabel+'}','{'+newlabel+'}')
        (R/'manuscript'/name).write_text(copy)
        r8text=r8text.replace(oldpath,rel+'/manuscript/'+name)
    (R/'manuscript/r8_supplement_layout.tex').write_text(r8text)
    body=body.replace(r8path,rel+'/manuscript/r8_supplement_layout.tex')
    r10path='revisions/2026-10-04-r10/manuscript/supplement.tex'
    r10text=(ROOT/r10path).read_text()
    for name in ['table_all_fits.tex','table_all_bounds.tex']:
        oldpath='revisions/2026-10-04-r10/manuscript/'+name
        text=(ROOT/oldpath).read_text()
        head=text.split('\\toprule',1)[1].split('\\midrule\\endhead',1)[0]
        text=text.replace('\\midrule\\endhead','\\midrule\\endfirsthead\n\\toprule'+head+'\\midrule\\endhead',1)
        target='r10_layout_'+name
        (R/'manuscript'/target).write_text(text)
        r10text=r10text.replace(oldpath,rel+'/manuscript/'+target)
    (R/'manuscript/r10_supplement_layout.tex').write_text(r10text)
    body=body.replace(r10path,rel+'/manuscript/r10_supplement_layout.tex')
    extra=r'''
\input{revisions/2026-10-04-r11/manuscript/retained_applications.tex}
\input{revisions/2026-10-04-r10/manuscript/study.tex}
\input{revisions/2026-10-04-r11/manuscript/retained_conclusion.tex}
\input{revisions/2026-10-04-r11/manuscript/retained_proofs.tex}
\section{R11 Complete Numerical Record}\label{app:r11record}
\input{revisions/2026-10-04-r11/manuscript/table_all_seeds.tex}
\input{revisions/2026-10-04-r11/manuscript/table_all_frontiers.tex}
\input{revisions/2026-10-04-r11/manuscript/table_all_sensitivity.tex}
\input{revisions/2026-10-04-r11/manuscript/table_greedy.tex}
\bibliographystyle{ecta-fullname}
\bibliography{revision_reference}
'''
    body=body.replace('\\end{document}',extra+'\n\\end{document}')
    new_supp=pre+'\\usepackage{xr}\n\\externaldocument{revisions/2026-10-04-r11/build/ECTA_refs}\n\\begin{document}'+body
    (ROOT/'supp.tex').write_text(new_supp)
    (ROOT/'revision_reference.bib').write_text((archive/'revision_reference.r10.bib').read_text()+'\n'+(R/'manuscript/references.bib').read_text())
    old_labels=set(re.findall(r'\\label\{([^}]+)\}',old))
    included=source+new_supp+applications+proofs+(R/'manuscript/retained_conclusion.tex').read_text()
    new_labels=set(re.findall(r'\\label\{([^}]+)\}',included))
    assert old_labels<=new_labels,old_labels-new_labels
    record=dict(base='8ded2629289c4633141b9fac1aa9b41a8c1595af',roots={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in archive.glob('*.r10.*')},relocations=[dict(source='R10 ECTA sections: Analytical and Nonsmooth Benchmarks through R9 numerical evidence',destination='manuscript/retained_applications.tex',byte_exact=True,sha256=hashlib.sha256(applications.encode()).hexdigest()),dict(source='R10 ECTA appendix and revision records',destination='manuscript/retained_proofs.tex',byte_exact=True,sha256=hashlib.sha256(proofs.encode()).hexdigest())],root_labels_preserved=len(old_labels),title_preserved='Neural Bellman Operators',historical_folders_modified=False)
    (R/'EDITORIAL_MAP.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))

if __name__=='__main__':integrate()
