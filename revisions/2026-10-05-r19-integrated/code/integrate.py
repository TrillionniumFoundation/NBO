"""Integrate the new revision without deleting or editing historical components."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1];REL=R.relative_to(ROOT).as_posix()

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def blob(p):
 b=p.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def main():
 archive=R/'archive';archive.mkdir(exist_ok=True)
 expected={'ECTA.tex':'7079c00c344f410de0730bd1e8dcfed169650687','supp.tex':'a8c90baf5f80c403b501d3f2a07c4550aa72e3d0'}
 for name,h in expected.items():
  if not (archive/name).exists():
   if blob(ROOT/name)!=h:raise RuntimeError('publication baseline mismatch: '+name)
   shutil.copy2(ROOT/name,archive/name)
 if not (archive/'README.md').exists():shutil.copy2(ROOT/'README.md',archive/'README.md')
 baseline=R/'BASELINE_TEXT_HASHES.json'
 if not baseline.exists():
  paths=[p for p in ROOT.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.cls','.cfg','.bst'} and R not in p.parents]
  baseline.write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in paths},indent=2,sort_keys=True)+'\n')
 old=(archive/'ECTA.tex').read_text()
 text=old.replace('revisions/2026-10-05-r18/build/',REL+'/build/')
 start=text.index('\\begin{abstract}');end=text.index('\\end{abstract}',start)+len('\\end{abstract}')
 abstract=r'''\begin{abstract}
This paper develops Neural Bellman Operators for policy evaluation and feasible
improvement in controlled economies. A common continuation connects current
choices to policy-specific future payoffs. We derive decision-loss bounds from
centered continuation errors, a transport bound for changes in future economic
primitives, and a true-objective certificate for continuous scalar decisions.
These results give explicit conditions for reuse and refresh while retaining
the boundary, utility-domain, and deviation requirements of the original
economic applications. The capital evidence includes protected high-dimensional
payoff comparisons, conditional prediction-risk assessment, and simultaneous
finite-catalogue bounds. A new prospective experiment varies one to 1,024
queries and compares seven complete procedures at a common economic tolerance,
charging fitting, querying, failed checks, and verification. NBO attains the
scalar-interval target in every declared stream; conventional surrogates remain
competitive and are not excluded from the cost frontier. The results distinguish
a reusable learned continuation from a claim of uniform neural dominance or
an unverified solution of the full diffusion control problem.
\end{abstract}'''
 text=text[:start]+abstract+text[end:]
 text=text.replace('revisions/2026-10-05-r18/manuscript/introduction.tex',REL+'/manuscript/introduction.tex')
 oldlit='\\input{revisions/2026-10-04-r16/manuscript/literature.tex}'
 text=text.replace(oldlit,oldlit+'\n'+f'\\input{{{REL}/manuscript/literature_addition.tex}}\n\\input{{{REL}/manuscript/targets.tex}}\n\\input{{{REL}/manuscript/decision_main.tex}}')
 oldcat='\\input{revisions/2026-10-05-r18/manuscript/catalogue_main.tex}'
 text=text.replace(oldcat,oldcat+'\n'+f'\\input{{{REL}/manuscript/prospective_main.tex}}')
 text=text.replace('revisions/2026-10-05-r18/manuscript/conclusion.tex',REL+'/manuscript/conclusion.tex')
 text=text.replace('\\bibliography{revision_reference}',f'\\bibliography{{revision_reference,{REL}/references}}')
 moved=[
  'revisions/2026-10-04-r16/retained/manuscript/capital.tex',
  'revisions/2026-10-04-r16/retained/manuscript/new_theory.tex',
  'revisions/2026-10-04-r16/retained/manuscript/implementation_summary.tex',
  'revisions/2026-10-04-r16/retained/manuscript/fees.tex']
 for name in moved:
  token='\\input{'+name+'}'
  if text.count(token)!=1:raise RuntimeError('missing inherited main component '+name)
  text=text.replace(token+'\n','')
 guide=r'''\section{Detailed Capital and Implementation Accounts}\label{app:r19retained}
The following four components are retained without textual edits from the
previous main article. They supply the full capital specification, operational
Bellman bridge, implementation account, and fee normalization. Their relocation
places the common economic question and complete primary comparisons first;
it removes no theorem, proof block, economic model, or numerical observation.
'''
 (R/'manuscript/retained_accounts.tex').write_text(guide+'\n'.join('\\input{'+x+'}' for x in moved)+'\n')
 (R/'REORGANIZATION.json').write_text(json.dumps({'moved_unchanged_from_main_to_supplement':moved,'all_other_substantive_main_components_retained':True,'editorial_replacements':['introduction','conclusion','abstract'],'previous_editorial_sources_preserved':True},indent=2)+'\n')
 (R/'ECTA.tex').write_text(text);(ROOT/'ECTA.tex').write_text(text)
 supp=(archive/'supp.tex').read_text().replace('revisions/2026-10-05-r18/build/',REL+'/build/')
 supp=supp.replace('\\bibliographystyle{ecta-fullname}',f'\\clearpage\n\\input{{{REL}/manuscript/retained_accounts.tex}}\n\\input{{{REL}/manuscript/decision_proofs.tex}}\n\\input{{{REL}/results/generated/record.tex}}\n\\bibliographystyle{{ecta-fullname}}')
 supp=supp.replace('\\bibliography{revision_reference}',f'\\bibliography{{revision_reference,{REL}/references}}')
 (R/'supp.tex').write_text(supp);(ROOT/'supp.tex').write_text(supp)
 apps=ROOT/'revisions/2026-10-05-r18/applications.tex'
 if not (archive/'applications.tex').exists():shutil.copy2(apps,archive/'applications.tex')
 (R/'applications.tex').write_text(apps.read_text().replace('revisions/2026-10-05-r18/build/',REL+'/build/'))
 report=ROOT/'reviews/2026-10-05-econometrica-numerical-methods-r18/referee_report.md'
 shutil.copy2(report,archive/'referee_report_r18.md')
 source={'execution_replay_freeze':'50ffdd59032e6216a7834d1ecf1c8388d3038682','parent_response_head':'0d3b370a6d8fdd725c2c6beb0858e1f8eb0e2f8d','paper':'Neural Bellman Operators','review_branch':'review/econometrica-numerical-methods-r18-2026-10-05-20afc6c','review_commit':'74f0a278aeeb5c62fa556a65f758092621cedf02','reviewed_publication':'20afc6c1c4828e3c469e7906366bcc8730cc04d0','freeze_commit':'6171912994009ee56520bc7e294a1960083f71c7','new_scope':REL,'independent_branch':'revision/econometrica-nbo-r19-integrated-2026-10-05','other_r19_source_not_overwritten':'6c516364965dd2e3e174bf97a2e7ab947914c9af','original_components':'All historical manuscript, proof and application files remain unmodified; replaced publication roots are archived exactly.'}
 (R/'SOURCE_BASELINE.json').write_text(json.dumps(source,indent=2,sort_keys=True)+'\n')
 readme=f'''# Neural Bellman Operators\n\n## R19 integrated revision — 5 October 2026\n\nThis revision answers the R18 advisory referee report at `74f0a278aeeb5c62fa556a65f758092621cedf02`, on the reviewed R18 paper `20afc6c1c4828e3c469e7906366bcc8730cc04d0`. It retains the original title, author, general controlled-economy problem, all historical results, and the complete economic applications. It builds on the pre-existing R19 response head and adds a complete integrated publication on a new branch; neither prior R19 branch is overwritten.\n\n- [Main article]({REL}/build/ECTA.pdf), [LaTeX source]({REL}/ECTA.tex).\n- [Technical supplement]({REL}/build/supp.pdf), [source]({REL}/supp.tex).\n- [Complete economic applications]({REL}/build/applications.pdf), [source]({REL}/applications.tex).\n- [Point-by-point response]({REL}/build/response.pdf), [response text]({REL}/RESPONSE_TO_REFEREE.md).\n- [Execution and report audit]({REL}/results/REPORT_AUDIT.json), [all 252 records]({REL}/results/registered/), [complete protocol]({REL}/protocols/DESIGN.json).\n\n### Additions\n\nThe revision proves a centered-risk decision-loss bound, a continuation-transport theorem for bounded changes in future economic primitives, an explicit sufficient amortization class with fitting and cache costs, and a true-objective strong-concavity certificate with explicit interval arithmetic. An exact replay of the already-frozen capital design executes seven procedures at query volumes 1, 4, 16, 64, 256, and 1024 in dimensions 10 and 50, across three complete fitting/cache streams. Every failed check and attempted fit is charged. Conventional quadratic and radial-basis continuation regressions, a shared conditional actor, cached SAA, and full-support enumeration remain in the comparison. Prediction risk, scalar-interval decision loss, original vector-catalogue regret, and full diffusion or equilibrium targets are not conflated.\n\n### Replication\n\nFrom the repository root, install the documented NumPy, CPU PyTorch and LaTeX dependencies, then run:\n\n```sh\npython {REL}/code/study.py --out {REL}/results/registered-replay\npython -m unittest discover -s {REL}/code -p 'test*.py' -v\npython {REL}/code/build.py\n```\n\nDo not overwrite an existing evidence directory. `report.py` generates publication tables from the declared `results/registered/SUMMARY.json`; a new timing environment must be labeled as a replay, not silently substituted into an old table.\n\nThe new integrated replay is not counted as extra independent streams. Its seven methods use three original streams, two dimensions, and six query volumes. The readable descriptive design is reconstructed from the frozen code, not a backdated replacement for the missing original design file.

The final publication uses the native `econsocart` class. Exact replaced roots and the answered report are retained in [{REL}/archive/]({REL}/archive/). No claim is made that the new finite-support scalar certificate validates an uncomputed continuous-time HJB or an unmeasured training-stream population.\n'''
 (ROOT/'README.md').write_text(readme);(R/'README.md').write_text(readme.replace(REL+'/', './'))
 base=json.loads(baseline.read_text());checks={}
 for name,h in base.items():
  target=archive/name if name in expected else ROOT/name
  checks[name]=target.is_file() and sha(target)==h
 if not all(checks.values()):raise RuntimeError('historical scientific source changed')
 (R/'results/PRESERVATION.json').write_text(json.dumps({'source_files_checked':len(checks),'all_preserved':all(checks.values()),'archived_roots':list(expected),'checks':checks},indent=2,sort_keys=True)+'\n')
 print('Preserved',len(checks),'scientific source files')
if __name__=='__main__':main()
