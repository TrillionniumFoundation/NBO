"""Exact source retention and issue provenance, not an automatic proof verdict."""
from pathlib import Path
import json,re,hashlib,shutil
R=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
inv=R/'archive110/inventory100';idx=json.loads((inv/'review_blob_index.json').read_text());review_rows=[]
# Responses identify current changes and preserve the residual obligation.
routes=[
 (('information complexity','information-complexity','lower bound','oracle restriction','bit-complexity','continuous-risk complexity'),
  ['new/information99.tex','new/precision99-link.tex','new110/budget.tex','new110/budget_proofs.tex','new109/improvement.tex'],
  'The retained information theorems keep their law, dimension, point-value and random-coverage quantifiers. Formula-derived Bellman computation is explicitly a different information interface. The current stopping ceiling and paid positive-gap resolution state the exact restricted lower/upper claim; no universal randomized, multivariate or end-to-end Bellman optimal rate is inferred.',
  'Partial: precise current information claims and proofs; broader randomized/multivariate/end-to-end optimality remains open.'),
 (('composite loss','monotonicity','convergence proof','convergence theorem','stability','bellman consistency','asserted correct minimizer'),
  ['new110/core-main.tex','new109/improvement.tex','new109/proofs.tex','new110/recursive_bridge.tex'],
  'The active construction uses explicit feasible own-future Bellman queries and an original-policy sandwich, not an assertion that an arbitrary composite training loss has the correct minimizer. Stability and policy-iteration claims have uniform original-operator assumptions and complete proofs. A zero-centered sampled residual or convergence of a numerical optimizer does not establish those premises. Earlier failed examples remain separately identified.',
  'Partial: current claims avoid and mathematically delimit the identified inference; no unexecuted historical training convergence or preference-sign correction is claimed.'),
 (('boundary','viscosity','hjb','continuous-time','continuous/discrete','trace estimation','squared-residual'),
  ['new110/recursive_bridge.tex','new109/proofs.tex','sections/proofs67.tex'],
  'The current continuous-time certificate has explicit smoothness, admissibility, original driver, terminal/stopping-boundary and all-action residual assumptions, with a full proof. A sampled residual or a training optimizer is not a viscosity-convergence certificate. The original historical run is not relabeled as this conditional result.',
  'Partial: current mathematical claim delimited and proved; original historical experiment or viscosity-learning convergence is not newly established.'),
 (('ndu','endogenous','epstein','preference','time-inconsistency','equilibrium','nash','cournot','game'),
  ['new110/recursive_bridge.tex','sections/coupled89.tex','sections/decisions49.tex'],
  'The original preference/game episode, objective and information structure retain their identities. The new Brownian recursive-utility bridge proves only its declared decoupled subcase. Investment AVaR results are not transferred to NDU, sophisticated-agent equilibrium or a dynamic game; no continuous-game or general coupled-FBSDE success is asserted.',
  'Open for the original application unless its separate historical proof/evidence already supplies the claim; this campaign supplies no substitute experiment.'),
 (('statistical','population','confidence','random','estimand','selection','training distribution'),
  ['new110/study.tex','new/action99.tex','new/information99.tex','sections/study96.tex'],
  'Every current actor has its own original-policy numerical cost intervals on the full declared catalogue. The catalogue is deterministic; no historical confidence interval or independently frozen random test is transferred. Oracle randomization quantifiers and finite-menu validation independence remain explicit.',
  'Partial: present inference is correctly scoped; independent new-actor population ordering and training-distribution reliability remain open.'),
 (('neural','actor contribution','representation','geometry','novelty','method-specific','distinct capability','generic screening','unique','distinct numerical'),
  ['new110/study.tex','new110/budget.tex','new109/tail.tex','new/decision99.tex','new110/core-main.tex'],
  'The current construction and action bound retain their original Bellman target. Equivalent conventional hinges are evaluated with exactly the same acquired geometry and all twelve policy/trial comparisons agree. Strong polynomial, spline, grid and semi-analytic controls receive the same algorithms. No ordinary geometric advantage or method-neutral certificate is labeled neural-exclusive.',
  'Partial: attribution and complete comparisons corrected; neural-exclusive competitiveness is not established by the current catalogue.'),
 (('horizon','scal','dimension','vector','multi-action','multi-control','coverage','off-grid'),
  ['new109/compiler.tex','new110/study.tex','new/continuous95-tail99.tex','sections/vector67.tex','sections/complexity86.tex'],
  'The current original-law compiler has a proved finite region count after O(d) coefficient preparation and a separate d=2,4,8 rational kernel diagnostic. The active learned comparison stays at its declared two-date/two-coordinate problem. Existing adverse horizon, tensor and coverage results are retained; the kernel diagnostic is not a learned high-dimensional tournament.',
  'Partial: analytical kernel scaling and explicit source limits; genuine learned longer-horizon/vector/multiple-innovation competition remains open.'),
 (('cost','work','timing','resource','oracle','crossover','baseline','compar','cold-start','reuse','frontier','operational','certificate','critic','residual','witness','stationarity'),
  ['new110/study.tex','new110/budget.tex','new110/budget_proofs.tex','new109/tail.tex','new109/improvement.tex'],
  'The current experiment retains paid original labels, every feature trial and fitting audit, complete incumbent construction, all refused improvements and seven fresh-process repetitions. Actual policy-cost differences, regret, action-distance bounds and operation categories accompany clocks. Remaining-gain stopping is prospectively executed at every declared budget and has a proved original-cost opportunity bound; it does not transform earlier residual reductions into service gains.',
  'Substantive current change demonstrated on the original investment catalogue; no claim that every earlier baseline, reuse law or optimizer distribution is resolved.'),
 (('economic','welfare','purchase','adoption','calibrat','application','margin','consequential'),
  ['new110/study.tex','new110/budget.tex','sections/decisions49.tex','new/decision99.tex'],
  'Original-policy cost improvements and the positive sacrifice from earlier stopping are reported with numerical intervals and complete paid work. The stopping budget is an engineering parameter, not a calibrated welfare margin. Prices, fees and workloads are not invented, and zero historical learned adoption over quadratic remains explicit.',
  'Partial: original-objective comparison established; consequential externally calibrated adoption remains open.'),
 (('reproduc','source','provenance','deliver','freeze','package','manifest','independent','canonical','evidence','durable'),
  ['PROTOCOL110.md','SOURCE_FREEZE110.json','code110/audit110.py','code110/verify110.py','REPRODUCE110.md'],
  'Current actual source bytes were remotely frozen before the new algorithm campaign, with independent run identities, raw payloads, logs and hashes. The new record audit and unchanged-source audit execute separately. The complete current dependency closure is supplied. The attempted 435-case historical replay retains twenty errors and one pinned-file failure rather than reporting a false green archive.',
  'Current execution and publication closure independently checkable; full historical missing-dependency repair and unrelated CI remain separate obligations.'),
 (('title','abstract','scope','broad','reorganiz','cumulative','paper','submission','presentation','shorten','tighten','center','synthesis','language'),
  ['ECTA.tex','supp.tex','appendix.tex','new110/introduction.tex','CONTENT_RETENTION_MAP.md'],
  'The English main narrative is reorganized around original Bellman decisions, action error and paid improvement. Full current proofs are in the supplement. Earlier sections are moved by byte-exact splits into the development companion, with source/hash retention. The original NBO title, economic target and Econometrica research objective are retained, without using the title as evidence of neural exclusivity.',
  'Editorial and source-retention changes implemented; the scientific ambition is not relabeled completed by shortening the text.')]
issues=[]
for ent in idx:
 if not ent['path'].endswith('referee_report.md'):continue
 p=inv/'blobs'/Path(ent['local']).name
 assert h(p)==ent['sha256']
 dest=R/'archive110/reports'/ent['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 text=p.read_text();lines=text.splitlines();path=str(dest.relative_to(R))
 heads=[]
 for i,line in enumerate(lines):
  if re.match(r'#{2,4}\s+(?:B|M|R)\d+[\.: ]',line):heads.append((i,line))
 for n,(i,title) in enumerate(heads):
  # Keep the exact complete comment block for a reviewer, not a guessed paraphrase.
  end=next((j for j in range(i+1,len(lines)) if re.match(r'#{1,4}\s',lines[j])),len(lines))
  body='\n'.join(lines[i:end]);k=title.lower();chosen=None
  # Financial interpretation takes priority when the heading explicitly concerns adoption/calibration.
  if any(x in k for x in ('purchase','adoption','economic margin','calibrated','welfare')):chosen=next(r for r in routes if 'purchase' in r[0])
  if chosen is None:chosen=next((r for r in routes if any(w in k for w in r[0])),routes[-1])
  issues.append({'report_path':path,'report_git_blob':ent['git_blob'],'report_sha256':ent['sha256'],
    'heading':title.lstrip('# '),'start_line':i+1,'end_line':end,'comment_sha256':hashlib.sha256(body.encode()).hexdigest(),
    'exact_comment':body,'current_response':chosen[2],'current_locations':chosen[1],
    'status_and_remaining_scope':chosen[3],
    'automatic_location_routing_not_independent_scientific_closure':True})
 # preserve all numbered minor items and all headings as searchable context regardless of routing.
 minor=[];mode=False
 for i,l in enumerate(lines):
  if l.startswith('## '):mode=bool(re.search('minor|additional comments',l,re.I))
  if mode and re.match(r'\s*\d+[.)]\s',l):minor.append({'line':i+1,'text':l})
 review_rows.append({**ent,'local_current':path,'major_issue_count':len(heads),'minor_items':minor,
   'all_headings':[{'line':i+1,'heading':l} for i,l in enumerate(lines) if re.match(r'#{2,4} ',l)]})
save(R/'evidence110/ALL_REPORT_ISSUES110.json',{'reports':review_rows,'issue_responses':issues,
 'controlling_report_commit':'9723c6cd2cc8b3e071422f3e522d4a843946db63',
 'scope':'All recovered major B/M/R comment blocks retained verbatim with source lines and a current response/location. Routing is a transparent location aid; it is not a claim of independent proof or experiment closure for every historic issue. The full controlling report receives the point-by-point author response.',
 'review_named_r16_branch':'No new report in the recovered review subtree; it equals author commit 0b15260752b8e988236f82cc0ee7752b44f326f1 and is not the controlling review.'})
md=['# All recovered referee reports: author response/location ledger','',
 'The full reports are preserved in `archive110/reports/`. The current R97 response is in `RESPONSE_TO_REFEREE.tex`. Each entry below identifies an actual earlier comment, current mathematical/numerical changes and the unclosed part. It is not a claim that a current investment experiment completes a different historical application.','']
for rep in review_rows:
 md+=['## '+rep['path'],'','Git blob `'+rep['git_blob']+'`; SHA-256 `'+rep['sha256']+'`.','']
 for x in issues:
  if x['report_git_blob']!=rep['git_blob']:continue
  md+=['### '+x['heading'],'',f"Original lines {x['start_line']}–{x['end_line']}. "+x['current_response'],'',x['status_and_remaining_scope'],'','Current locations: '+', '.join('`'+p+'`' for p in x['current_locations'])+'.','']
 if rep['minor_items']:md+=['Minor items remain line-indexed in `evidence110/ALL_REPORT_ISSUES110.json`; the complete original text is retained.','']
(R/'RESPONSE_TO_ALL_REPORTS.md').write_text('\n'.join(md)+'\n')
# Snapshot every known baseline member and locate it unchanged or in the archive.
baseline=R.parent/'baseline99/NBO_R99'
if baseline.exists():
 basefiles=[]
 for p in sorted(baseline.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(baseline);d=h(p);now=R/rel;arc=R/'retained99'/rel
  if now.exists() and h(now)==d:status='unchanged in active source';loc=str(rel)
  elif arc.exists() and h(arc)==d:status='byte-preserved historical entry/artifact';loc=str(arc.relative_to(R))
  else:raise AssertionError('Unaccounted baseline mutation: '+str(rel))
  basefiles.append({'path':str(rel),'sha256':d,'bytes':p.stat().st_size,'status':status,'current_location':loc})
 save(R/'evidence110/BASELINE_RETENTION110.json',{'commit':'f78d7fcec9f657dfec56a0af7899fe967948652d','files':basefiles})
else:basefiles=json.loads((R/'evidence110/BASELINE_RETENTION110.json').read_text())['files']
for rec in basefiles:
 p=R/rec['current_location'];assert h(p)==rec['sha256'],p
split=json.loads((R/'evidence110/SECTION_SPLITS110.json').read_text())
for s in split:assert (R/s['main']).read_bytes()+(R/s['archive']).read_bytes()==(R/s['source']).read_bytes()
statements=[]
for folder in ('sections','new','new109','new110'):
 for p in sorted((R/folder).glob('*.tex')):
  t=p.read_text()
  for m in re.finditer(r'\\begin\{(theorem|proposition|lemma|corollary)\}(?:\[([^]]*)\])?(.*?)\\end\{\1\}',t,re.S):
   statements.append({'path':str(p.relative_to(R)),'line':t[:m.start()].count('\n')+1,'type':m.group(1),'title':m.group(2),
    'labels':re.findall(r'\\label\{([^}]+)\}',m.group(3)),'file_sha256':h(p),
    'statement_sha256':hashlib.sha256(m.group(0).encode()).hexdigest(),'index_not_proof_verdict':True})
save(R/'evidence110/THEOREM_INDEX110.json',statements)
save(R/'evidence110/RETENTION_SUMMARY110.json',{'baseline_files':len(basefiles),'recovered_reports':len(review_rows),
 'major_issue_entries':len(issues),'theorem_environment_entries':len(statements),'exact_splits':len(split),
 'full_historical_proof_reverification_claim':False,'full_historical_replay_success':False,
 'unattached_r109_preservation':'Immutable source tree 7c45e1fab219289b89df42d7ff0e22039f4d93d6 is attached in the new isolated branch under retained109-native; unchanged recovered compiler/tail/improvement/proof sources are carried forward; old raw run claims are not substituted for current actual records.'})
print('BASELINE',len(basefiles),'REPORTS',len(review_rows),'ISSUES',len(issues),'THEOREM ENTRIES',len(statements))
