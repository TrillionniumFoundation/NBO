"""Deterministic editorial integration; all displaced text is preserved."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1]

def sha(b):return hashlib.sha256(b).hexdigest()
def integrate():
    a=(R/'archive/ECTA.r11.tex').read_text();s=(R/'archive/supp.r11.tex').read_text()
    current=(ROOT/'ECTA.tex').read_text()
    if current!=a and 'sec:r12study' not in current and 'r12/manuscript/study.tex' not in current:raise ValueError('unexpected manuscript root; refuse overwrite')
    abstract=r'''We develop Neural Bellman Operators for economic control, separating policy evaluation, feasible improvement and independent verification. A costate-error bound connects the Bellman evaluation block to constrained Hamiltonian loss. Direct common-path comparisons measure the economic contribution of that block rather than infer it from separate improvements over a schedule. A finite-population extension of a policy-specific continuous-time certificate accounts for initial-state heterogeneity, diffusion transfer, clipping and simultaneous sampling uncertainty. An observation theorem implements the sampled controller from continuously observed capital histories and private randomization. In the unchanged nonlinear capital economy, new budgeted actor--critic, direct-policy and affine fits are compared across dimensions ten, twenty and fifty, with fresh-radius and critic ablations, explicit state stresses and an independent scalar HJB reference. A self-financed management-fee calculation turns policy differences into a precise adoption decision. The original recursive-utility, preference, temporal-self and strategic applications retain their distinct equations and verification domains. Neither numerical completion nor improvement over a feasible schedule is identified with optimizer convergence, near optimality or universal superiority.'''
    a=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:'\\begin{abstract}\n'+abstract+'\n\\end{abstract}',a,flags=re.S)
    moved=[]
    for name in ['learning','study']:
        line='\\input{revisions/2026-10-04-r11/manuscript/'+name+'.tex}'
        if a.count(line)!=1:raise ValueError('expected one historical input '+name)
        a=a.replace(line,'');moved.append(line)
    section=r'''\input{revisions/2026-10-04-r12/manuscript/theory.tex}
\input{revisions/2026-10-04-r12/manuscript/study.tex}
'''
    a=a.replace('\\section{Conclusion}',section+'\\section{Conclusion}',1)
    intro=r'''The present comparison asks what the Bellman evaluation block adds to direct policy optimization at a declared work budget. A costate-error inequality makes the evaluation--improvement mechanism explicit. Direct paired endpoints, rather than differences of schedule-relative bounds, evaluate competing fitted policies. A finite initial-state population, fresh radius fits, state stresses, an independent nonlinear HJB reference and a resource-financed management-fee experiment make the scope of the numerical and economic conclusions explicit. The exact observed-history implementation and its information assumptions are stated separately from the latent-innovation formulation.

'''
    a=a.replace('\\subsection{Relation to the literature}',intro+'\\subsection{Relation to the literature}',1)
    a=a.replace('Sections~\\ref{sec:r11specific}--\\ref{sec:r11study} complete the policy-specific verification, algorithm, and economic comparison.','Section~\\ref{sec:r11specific} supplies policy-specific verification; Sections~\\ref{sec:r12theory}--\\ref{sec:r12study} develop the method comparison, observation model and new economic experiment. The earlier rollout implementation and R11 study are retained intact in the supplement.')
    oldcon=a[a.index('\\section{Conclusion}'):a.index('\\bibliographystyle')]
    (R/'manuscript/retained_r11_conclusion.tex').write_text(oldcon)
    conclusion=r'''\section{Conclusion}\label{sec:conclusion}
Neural Bellman Operators distinguish the accuracy of policy evaluation, the quality of feasible improvement and the economic performance of the deployed policy. The costate-error bound identifies the channel through which a Bellman critic can improve decisions; direct paired comparisons test whether that channel justifies its computational cost. These are complementary objects. A method-agnostic certificate does not establish a method-specific advantage, and a small gain over a feasible schedule is not a certificate of near optimality.

The capital study now has an explicit initial-state population, a state-history observation implementation, equal-announced-budget fits, direct method endpoints, fresh-radius and critic ablations, severe state stresses and an independent nonlinear reference. Its self-financed fee experiment converts verified utility differences into a specified resource decision. Both positive and inconclusive comparisons remain part of the numerical result. The inherited continuous-time comparison and the new finite-family inference retain their stated assumptions; neither is extrapolated to noisy observations, all initial states or arbitrary future training procedures.

Recursive utility, endogenous preferences, temporal selves, viscosity selection and dynamic games remain part of the paper's original economic program. Their complete models, previous results and domain-specific error accounts are preserved in the supplement. Extending the capital implementation and transfer results to those problems requires their own additional hypotheses, not a change of title or a hidden change of economic problem.

'''
    a=a[:a.index('\\section{Conclusion}')]+conclusion+a[a.index('\\bibliographystyle'):]
    a=a.replace('revisions/2026-10-04-r11/build/supp_refs','revisions/2026-10-04-r12/build/supp_refs')
    s=s.replace('revisions/2026-10-04-r11/build/ECTA_refs','revisions/2026-10-04-r12/build/ECTA_refs')
    marker='\\section{Organization of the Revised Supplement}'
    insert='\\input{revisions/2026-10-04-r12/manuscript/proofs.tex}\n\\input{revisions/2026-10-04-r12/manuscript/full_results.tex}\n'
    s=s.replace(marker,insert+marker,1)
    tail='\n\\section{Retained R11 Learning and Experimental Record}\nThe following sections are reproduced from the reviewed R11 main article without changing their content. Their reported mean gains are pre-adjustment paired numerical statistics. Their original protocol and historical comparisons do not replace the new R12 method and population experiment.\n'+'\n'.join(moved)+'\n'
    s=s.replace('\\bibliographystyle',tail+'\\bibliographystyle',1)
    before=set(re.findall(r'\\label\{([^}]+)\}',(R/'archive/ECTA.r11.tex').read_text()))
    after=set(re.findall(r'\\label\{([^}]+)\}',a))
    if not before<=after:raise ValueError('root labels lost: '+str(before-after))
    (ROOT/'ECTA.tex').write_text(a);(ROOT/'supp.tex').write_text(s)
    preamble=a.split('\\begin{document}')[0]
    response=preamble.replace('\\externaldocument{revisions/2026-10-04-r12/build/supp_refs}','')+'\\begin{document}\n\\input{revisions/2026-10-04-r12/manuscript/response_body.tex}\n\\end{document}\n'
    (R/'response.tex').write_text(response)
    (R/'EDITORIAL_MAP.json').write_text(json.dumps(dict(base='840565f451be6103aeb325a8fc548a57507a8fb2',title_preserved='Neural Bellman Operators',archived_roots={p.name:sha(p.read_bytes()) for p in (R/'archive').iterdir()},retained_r11_inputs=moved,root_labels_preserved=len(before),original_conclusion_archived=True,historical_application_files_modified=False),indent=2)+'\n')
if __name__=='__main__':integrate()
