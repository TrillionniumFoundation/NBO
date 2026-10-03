"""Integrate the revision without removing an inherited section or label."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1]
def prepare():
 a=R/'archive';a.mkdir(exist_ok=True)
 for name in ['ECTA','supp']:
  p=a/f'{name}.r8.tex'
  if not p.exists():p.write_bytes((ROOT/f'{name}.tex').read_bytes())
 p=a/'R8_FILES_SHA256.json'
 if not p.exists():
  files={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in ROOT.rglob('*') if f.is_file() and '.git' not in f.parts and '__pycache__' not in f.parts and R not in f.parents}
  p.write_text(json.dumps(files,indent=2)+'\n')

def run():
 prepare();old=(R/'archive/ECTA.r8.tex').read_text();s=old
 abstract=r'''We develop Neural Bellman Operators for economic control with recursive utility, endogenous preferences, and strategic interaction. Policy evaluation, feasible improvement, and independent verification are separate maps. An indexed critic guard supplies a prescribed nodal evaluation error without optimizing action labels. Signed interval derivatives reduce action boxes to verified maximizing faces while retaining valid upper bounds at stopping switches and interrupted searches. On the same two-state preference economy, the tighter cover recertifies frozen continuous-action policies; fresh nested-grid training separates continuation error from the documented failure of off-grid frozen policies. An externally financed consumption supplement gives the utility bounds a model-specific welfare interpretation. In a dense nonlinear capital economy, a feasible common-control schedule and a global relaxation bound benchmark the original continuous-time optimum. Direct, search-only, classical, and projection comparisons remain explicit: the low-dimensional evidence does not establish an actor speed advantage. The results connect neural proposals to verified value and deviation accounts without conflating nodal certificates, continuous-economy bounds, and simulation diagnostics.'''
 s=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:r'\begin{abstract}'+'\n'+abstract+'\n'+r'\end{abstract}',s,flags=re.S)
 start=s.index('The paper makes three contributions.');end=s.index('\n\nThe numerical program',start)
 s=s[:start]+r'''The paper makes three connected contributions. First, it specifies a neural policy-evaluation and improvement map with explicit derivative routing, boundary conditions, and an indexed evaluation guard. The guard bounds a selected-policy target residual by construction; it does not claim convergence of Adam or an uncorrected network. Second, it makes the complete-action error account operational through signed interval derivatives and verified face domination, with natural union bounds at stopping switches. A matched enclosure experiment isolates this calculation from policy training. Third, it carries the accounts through the original preference, capital, and strategic applications: nested-grid retraining, a model-specific compensating transfer, an absolute continuous-time capital benchmark, and finite dynamic best responses. Comparison, monotonicity, interval inclusion, and approximate policy iteration remain inherited principles. The new results concern the specified guarded map, its verified output, and its measured economic accuracy, not an unqualified claim that a neural actor dominates classical or actor-free alternatives.'''+s[end:]
 marker=r'\input{revisions/2026-10-03-r8/manuscript/ndu.tex}'
 s=s.replace(marker,'The next comparison is the retained R8 evidence under its original enclosure. The new signed envelope and fresh nested-grid policies are reported separately in Section~\\ref{sec:r9results}; historical failure counts are not overwritten.\n'+marker)
 marker=r'\section{Conclusion}\label{sec:conclusion}'
 s=s.replace(marker,r'\input{revisions/2026-10-03-r9/manuscript/method.tex}'+'\n'+r'\input{revisions/2026-10-03-r9/manuscript/results.tex}'+'\n'+marker)
 start=s.index(marker)+len(marker);end=s.index(r'\begin{appendix}',start)
 s=s[:start]+r'''
Neural Bellman Operators organize computation around policy evaluation, feasible improvement, and independent economic verification. Recursive utility, endogenous preferences, sophisticated temporal selves, and dynamic strategic interaction remain part of that economic formulation. The representation is neural, but an economic claim concerns the policy actually deployed and the error that has been bounded.

The guarded map specifies how a nodal evaluation tolerance is enforced and records the indexed corrections it requires. Signed derivative enclosures reduce complete-action verification work without dropping unresolved boxes or differentiating across a stopping discontinuity. Their numerical contribution is identified using identical frozen policies and matched one-step comparisons. Fresh training and recertification on genuinely nested grids are kept distinct from the full-domain failure of interpolated coarse policies. The compensation account translates utility accuracy into a stated financed-transfer experiment rather than a misleading common percentage.

The dense capital experiment now has a feasible-policy lower benchmark and a continuous-time optimal upper benchmark on the original state space. These bounds are materially wider than a tight neural-policy certificate. Paired simulations remain discretized policy comparisons. Likewise, the complete-action preference certificates do not yet bound all continuous-state, continuous-time, and stopping-monitoring defects. The evidence does not establish that actors outperform the strongest low-dimensional search and projection alternatives; those comparisons remain in the record. The contribution is a specified neural Bellman computation with verified evaluation and improvement outputs, measured costs, and separate economic domains for each conclusion.

'''+s[end:]
 s=s.replace(r'\section{Replication and Scope of Numerical Evidence}',r'\input{revisions/2026-10-03-r9/manuscript/proofs.tex}'+'\n'+r'\section{Replication and Scope of Numerical Evidence}')
 marker=r'\bibliographystyle{ecta-fullname}'
 addition=r'''\paragraph{Current revision.} The authoritative R9 source descends from the review of the R8 candidate, dated 3 October 2026. Its new material, all raw runs, complete-action arrays, full-domain refinement summaries, proofs, response, and execution identities are stored under \texttt{revisions/2026-10-03-r9}. The archived R8 main text and supplement preserve the pre-revision scholarly record. Every inherited section and label is retained. The new response addresses the R8 report's B1--B7 and M1--M10 comments. Earlier replication and response descriptions in this historical record refer to their respective R6--R8 rounds; historical workflow success is not substituted for a run of the current source.

'''
 s=s.replace(marker,addition+marker);(ROOT/'ECTA.tex').write_text(s)
 so=(R/'archive/supp.r8.tex').read_text();ss=so.replace(r'\end{document}',r'\input{revisions/2026-10-03-r9/manuscript/supplement.tex}'+'\n'+r'\end{document}');(ROOT/'supp.tex').write_text(ss)
 labels=lambda t:set(re.findall(r'\\label\{([^}]+)\}',t))
 assert labels(old)<=labels(s);assert labels(so)<=labels(ss)
 (R/'results/PRESERVATION.json').write_text(json.dumps(dict(main_labels_before=len(labels(old)),main_labels_after=len(labels(s)),all_previous_labels_preserved=True,all_previous_sections_preserved=True,
  archived_main_sha256=hashlib.sha256((R/'archive/ECTA.r8.tex').read_bytes()).hexdigest(),archived_supplement_sha256=hashlib.sha256((R/'archive/supp.r8.tex').read_bytes()).hexdigest()),indent=2)+'\n')
if __name__=='__main__':
 import sys
 prepare() if '--prepare' in sys.argv else run()
