"""Integrate R13 additions after numerical tables are generated.
No historical source folder is rewritten. The authoritative roots themselves
are committed in the evidence snapshot, not left as an integration intention.
"""
from pathlib import Path
import hashlib,json,re
import integrate
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1]
def main():
    integrate.integrate()
    a=(ROOT/'ECTA.tex').read_text();s=(ROOT/'supp.tex').read_text()
    a=a.replace('\\section{Conclusion}','\\input{revisions/2026-10-04-r13/manuscript/work_and_sensing.tex}\n\\input{revisions/2026-10-04-r13/manuscript/extra_summary.tex}\n\\section{Conclusion}',1)
    marker='\\section{Organization of the Revised Supplement}'
    if s.count(marker)!=1:raise RuntimeError('supplement integration marker')
    s=s.replace(marker,'\\input{revisions/2026-10-04-r13/manuscript/sensing_proof.tex}\n\\input{revisions/2026-10-04-r13/manuscript/extra_full_results.tex}\n'+marker,1)
    # All numerical tables appear once; the supplement uses only additional tables.
    abstract=r'''We develop Neural Bellman Operators for economic control by separating policy evaluation, feasible improvement and independent verification. A costate-error bound connects evaluation to constrained Hamiltonian loss. Direct common-path comparisons distinguish improvement over a feasible schedule from improvement over competing numerical methods. In the original nonlinear capital economy, actor--critic, direct-policy and affine policies are evaluated in dimensions ten, twenty and fifty under both announced-time and fixed-simulator-work budgets. Policy-specific continuous-time endpoints account for initial-state heterogeneity, diffusion transfer, clipping, arithmetic and simultaneous sampling uncertainty. Work-to-target comparisons include the cost of unsuccessful verification attempts. Independent costate banks, nested rollout grids and an independent scalar HJB reference test the evaluation mechanism and absolute numerical accuracy. A finite-observation controller is connected to its verified implementation through weight-dependent sensing and arithmetic error bounds. The original recursive-utility, preference, temporal-self and strategic applications retain their equations and verification domains. Numerical completion, safe improvement, method superiority and proximity to the economic optimum remain separate claims.'''
    a=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:'\\begin{abstract}\n'+abstract+'\n\\end{abstract}',a,flags=re.S)
    (ROOT/'ECTA.tex').write_text(a);(ROOT/'supp.tex').write_text(s)
    for file in ['ECTA.tex','supp.tex',str((R/'response.tex').relative_to(ROOT))]:
        p=ROOT/file;text=p.read_text()
        # Paragraph flexibility changes line breaking, not the font or overflow gate.
        text=text.replace('\\begin{document}','\\emergencystretch=1.5em\n\\begin{document}',1);p.write_text(text)
    mapping=json.loads((R/'EDITORIAL_MAP.json').read_text())
    mapping['latest_review_commit']='65110ed2991f4b955d2df37b2ab8635b12df5d1c'
    mapping['new_inputs']=['work_and_sensing.tex','sensing_proof.tex','extra_full_results.tex']
    mapping['source_scope']='R12 and all previous directories preserved unchanged; latest root and previous integrated roots separately archived'
    (R/'EDITORIAL_MAP.json').write_text(json.dumps(mapping,indent=2)+'\n')
if __name__=='__main__':main()
