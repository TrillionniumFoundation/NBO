"""Publication formatting from the completed frozen R126C report only."""
from pathlib import Path
import sys,json,hashlib
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'results126c/report01'
s=json.loads((P/'SUMMARY126C.json').read_text())
assert s['all_scientific_outcomes_and_economic_work_identical_to_F126'] and s['exact_records_compared']==4224
rows=[json.loads(x) for x in (P/'cohorts_summary126c.jsonl').read_text().splitlines()]
keyed={(r['variant'],tuple(r['cohort'])):r for r in rows}
m={(r['variant'],r['mode']):r for r in s['mode_summary']}
names={'fused_control':'Fused control','warm_adaptive':'Warm adaptive','direct_terminal':'Direct terminal','grid33':'Action-grid DP'}
order=list(names)
def number(x,n=3):return f'{float(F(x)):.{n}f}'
def pct(a,b):return float(100*(1-F(a)/F(b)))
C=s['source']['boundaries']['source_commit']
lines=[r'\subsection{Exact geometry reuse and complete computational cost}\label{sec:cache_results126}',
'After the initial excess cost of direct service was observed, a distinct algorithm was frozen prospectively at',
rf'\nolinkurl{{{C}}}. It reuses exact derivative-envelope geometry within each paid decision. Each full-domain partition, cumulative rational integral, gradient and constrained root can serve repeated candidate contrasts; the cache is destroyed at the end of that decision. Every conventional representation and strong control receives the same mechanism. The new experiment executes both the uncached and cached algorithms afresh, in fixed alternating cohort order, over all nine states and three further first-state timing processes.',
'',
'All 3,168 new primary decisions and 1,056 new timed decisions completed. The exact verifier matched every one of their 4,224 complete scientific records to the first study after removing only declared clocks and run metadata. This checks the acquired supports, rejected proposals, selected actions, certificates, original-model operation counts and stopping outcomes. Economic information is purchased again in each paid service; only exact algebra is reused within it.',
'',
r'\begin{table}[t]\caption{Fresh paired complete cost of exact geometry reuse}\label{tab:cache126}\centering',
r'\begin{tabular}{lrrrr}\toprule',
r'Service & Decisions & Uncached s & Cached s & Reduction (\%)\\\midrule']
for mode in order:
 u,c=m['uncached',mode],m['cached',mode]
 lines.append(f"{names[mode]} & {u['decisions']} & {number(u['complete_primary_service_seconds'])} & {number(c['complete_primary_service_seconds'])} & {pct(c['complete_primary_service_seconds'],u['complete_primary_service_seconds']):.1f}"+r'\\')
lines +=[r'\bottomrule\end{tabular}',
r'\par\smallskip\footnotesize The table allocates the whole paired primary parent process, including service execution, model loading, row serialization and an equal share of the residual overhead. Uncached and cached columns are fresh observations under the second source boundary. The first study in Table~\ref{tab:service126} remains unchanged; its displayed service component and this whole-process allocation have different accounting scopes. Shared-host clocks are descriptive. All original policy outcomes and economic-operation counts are identical between the paired variants.',r'\end{table}','']
du,dc=m['uncached','direct_terminal'],m['cached','direct_terminal'];wc=m['cached','warm_adaptive']
gap=float(100*(F(dc['complete_primary_service_seconds'])/F(wc['complete_primary_service_seconds'])-1))
lines +=[f"Exact geometry reuse reduces the direct route's fully allocated nine-state cost by {pct(dc['complete_primary_service_seconds'],du['complete_primary_service_seconds']):.1f} percent, from {number(du['complete_primary_service_seconds'])} to {number(dc['complete_primary_service_seconds'])} seconds. The same optimization also helps the warm control. Cached direct still costs {gap:.1f} percent more than cached warm, whose complete cost is {number(wc['complete_primary_service_seconds'])} seconds, while both meet the stronger target in all 522 decisions. The substantial reduction in certificate work therefore improves the direct implementation without establishing a universal advantage over the strongest service.",
'',
f"For the direct primary corpus, {dc['cache_counts']['contrast_requests']:,} contrast requests use {dc['cache_counts']['full_domain_partition_builds']:,} full-domain partition constructions and {dc['cache_counts']['primitive_new_evaluations']:,} new endpoint antiderivative evaluations; {dc['cache_counts']['primitive_hits']:,} additional primitive requests reuse exact values. These diagnostics account for algebraic reuse. The original {dc['counts']['compiled_terminal_rows']:,} compiled terminal rows remain fully charged and unchanged.",
'',
f"The first-state timing workload yields a different comparison: cached and uncached ranges are strictly separated in favor of caching in {s['cached_observed_range_speed_wins']} of 176 cohorts and against it in {s['uncached_observed_range_speed_wins']}; the other {176-s['cached_observed_range_speed_wins']-s['uncached_observed_range_speed_wins']} overlap. Cached direct has a strictly smaller observed range than its matched cached fused or warm control in {s['direct_observed_range_speed_wins_against_cached_controls']} of 116 comparisons, with {s['cached_control_observed_range_speed_wins']} reverse separations. These fixed-state ranges are not population confidence statements and do not supersede the nine-state totals.",
'',
f"The cost calculation is repeated against conventional services that receive the same cache. All {s['neural_adoption_scenarios']} sufficient neural adoption regions remain empty, all {s['neural_adoption_scenarios']-s['empty_optimistic_neural_regions']} optimistic interval-only regions remain nonempty, and all {s['same_policy_cost_blockers']} scenarios retain an exact identical-policy conventional cost blocker. The computation improvement is shared across representations. The original independent audit's 307 unresolved regret checks, 1,113 unresolved containment checks and 250 unresolved policy orderings remain unchanged, because the cached experiment returns exactly the same complete policies and certificates.",
'']
main=ROOT/'new126/cache_results126.tex';main.write_text('\n'.join(lines))

lines=[r'\section{Complete paired certificate-computation ledger}\label{sec:cachedev126}',
rf'This appendix reports the separately prospective cache experiment at source \nolinkurl{{{C}}}. The first uncached primary evidence remains in \texttt{{results126/primary01}}. All new paired records, three timing processes, full-record equality checks, cost reconciliation and conditional adoption comparisons appear under \texttt{{results126c}}. No original source file or result was replaced.',
'',
f"The complete paired primary parent process took {number(s['primary_parent_seconds'],6)} seconds. The three complete paired timing parents took {number(s['timing_parent_seconds'],6)} seconds in total. Every primary cohort receives an equal share of the measured parent residual; the separate service-only component is retained in the frozen report. Equality verification took {s['equality_verification_seconds']:.6f} internal seconds and purchased no economic observations. It verified all 4,224 full scientific records and exact squares of the action-distance bounds. All successful and failed development checks remain available.",
'',
'Before the second freeze, 660 synthetic rational identities checked partial partitions, both contrast modes, gradients, boundary and interior roots, support minima and candidate certificates. The first saved-record schema precheck failed because the inherited timing dictionary was not yet excluded. Its failure receipt was retained. The explicit clock dictionary was added before any cache economics, and all 528 already-published first-study timing records then matched the original full scientific records. The final second-study equality verifier uses that published exclusion set without alteration.',
'',
r'\subsection{Measured algebra work and unchanged economic work}',
r'\begin{table}[h]\centering\caption{Cached primary exact-geometry work}\label{tab:cachework126}',
r'\begin{tabular}{lrrrrr}\toprule',
r'Service & Full partitions & Pieces & Contrasts & New primitives & Reused primitives\\\midrule']
for mode in order:
 c=m['cached',mode]['cache_counts']
 lines.append(names[mode]+' & '+' & '.join(f"{c.get(k,0):,}" for k in ['full_domain_partition_builds','full_domain_pieces_built','contrast_requests','primitive_new_evaluations','primitive_hits'])+r'\\')
lines +=[r'\bottomrule\end{tabular}',r'\par\smallskip\footnotesize Counts include every paid primary service and are not divided by successful improvements. The zero DP row means that its decision route does not use this envelope cache; all of its economic work and context-manager costs are nevertheless charged.',r'\end{table}','',
'Complete cached primary model-operation counts equal the uncached counts exactly: 902,961 compiled terminal rows for fused control, 973,410 for warm adaptive, 418,957 for direct terminal, and 176,223 for action-grid DP. Matched ReLU and ordinary hinge representations retain identical scientific actions and work; no representation receives a free completed service, global memoized economic observation or differently fitted model.',
'',
r'\subsection{Every paired cohort}',
r'Table~\ref{tab:cacheall126} contains all 176 cohorts. Mesh denotes the number of coordinate nodes in the inherited acquisition; ON is the original online controller, Q quadratic, R ReLU, H its matched native hinge, S spline, P2/P3 polynomial degree, G the acquired grid and DP the 33-action control. V/M denote value/marginal fitting. Routes F/W/D/G denote fused, warm, direct and grid. Each primary time covers nine decisions, loading, output and the allocated parent residual. Each millisecond range covers the three complete first-state repetitions with their parent allocations. The widths of these ranges are descriptive. All policy, error and target outcomes equal the first-study cohort in the preceding ledger.',
'',r'{\scriptsize\setlength{\tabcolsep}{3pt}',
r'\begin{longtable}{rrlllrrll}',
r'\caption{All paired primary costs and first-state timing ranges}\label{tab:cacheall126}\\',
r'\toprule $\alpha$ & Mesh & Family & Loss & Route & Uncached s & Cached s & Uncached ms & Cached ms\\\midrule\endfirsthead',
r'\multicolumn{9}{l}{\textit{Continued: all paired cohorts}}\\',
r'\toprule $\alpha$ & Mesh & Family & Loss & Route & Uncached s & Cached s & Uncached ms & Cached ms\\\midrule\endhead',
r'\midrule\multicolumn{9}{r}{Continued on next page}\\\endfoot',r'\bottomrule\endlastfoot']
fam={'online':'ON','quadratic':'Q','relu':'R','hinge':'H','spline':'S','poly2':'P2','poly3':'P3','grid':'G','uniform_dp':'DP'}
loss={'value':'V','marginal':'M','online':'--','none':'--'}
route={'fused_control':'F','warm_adaptive':'W','direct_terminal':'D','grid33':'G'}
cohorts=sorted({tuple(r['cohort']) for r in rows})
for cohort in cohorts:
 u,c=(keyed[v,cohort] for v in ('uncached','cached'))
 i,b,a,l,mode=cohort
 ur=f"[{number(F(u['timing_min'])*1000,3)},{number(F(u['timing_max'])*1000,3)}]"
 cr=f"[{number(F(c['timing_min'])*1000,3)},{number(F(c['timing_max'])*1000,3)}]"
 lines.append(f"{('.50','.75')[i]} & {b} & {fam[a]} & {loss[l]} & {route[mode]} & {number(u['complete_primary_service_seconds'],4)} & {number(c['complete_primary_service_seconds'],4)} & {ur} & {cr}"+r'\\')
lines +=[r'\end{longtable}}','',r'\subsection{Adoption and research costs}',
'The frozen report preserves all 192 variant-specific neural price/amortization scenarios: each compares a neural service with every conventional service at the same risk and with the same cache variant. Each sufficient interval is empty; none of the optimistic interval-only outer intervals is empty. An exact identical-policy conventional cost blocker exists for every scenario. Historical acquisition allocations include the ReLU parent required by the matched hinge copy. Unknown earlier interrupted process clocks remain unknown. The current primary, timing, verification, reporting and publication-processing receipts record new research costs separately from conditional per-decision service costs.',
'']
dev=ROOT/'new126/cache_development126.tex';dev.write_text('\n'.join(lines))
receipt=dict(kind='publication formatting of completed frozen cache report',economic_evaluations=0,
    input_sha256=hashlib.sha256((P/'SUMMARY126C.json').read_bytes()).hexdigest(),
    source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    outputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (main,dev)})
(ROOT/'results126c/publication_render126c.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
print(json.dumps(receipt))
