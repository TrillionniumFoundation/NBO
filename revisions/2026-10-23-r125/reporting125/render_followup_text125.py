"""Render a separate author-text addendum from completed verification receipts."""
from pathlib import Path
import hashlib, json, time

ROOT = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    tick = time.perf_counter()
    out = ROOT/'results125/followup-presentation'
    reconciliation = out/'RECONCILIATION125.json'
    r = json.loads(reconciliation.read_text())
    summary_path = ROOT/'results125/independent-followup512/SUMMARY125.json'
    summary = json.loads(summary_path.read_text())
    c = r['combined_followup_counts']; work = r['exact_trace_work']
    phase = next(z for z in r['scientific_phase_costs'] if z['phase']=='independent-followup512')
    main_lines = [r'\paragraph{Separately frozen post-primary independent verification.}',
        'After the original capped audit, a separately published protocol selected both actual final and completed-prefix actions for every unresolved check. Its complete union contains 110 distinct state/risk/action keys; each received one 512-bin independent original-law evaluation. This is an explicitly post-primary verification follow-up, with no changed economic state, model, policy, training sample or production target.',
        f"Combining the additional independently valid intervals with the original audit confirms {c['contained']}/936 production interval containments and {c['gain_confirmed']}/251 accepted gain bounds, leaving {r['unresolved_containment']} and {r['unresolved_gain_bounds']} unresolved, respectively. There are {summary['contradictions']} contradictions. The original capped result remains 850/936 and 193/251, separately reported. No frozen success count is relabeled.",
        f"The additional audit requests {work['requested_contexts']:,} terminal contexts, reuses {work['reused_contexts']:,} exact original witnesses at identical rational states and risks, and computes {work['new_contexts']:,} new terminal contexts with {work['new_terminal_bisections']:,} actual bisection iterations. Its complete parent-process clock is {phase['complete_parent_seconds']:.6f} seconds, charged in addition to the original audit. These are research-verification costs; neither production-service clocks nor the first-state adoption comparisons are re-timed or revised."]
    dev = [r'\subsection{Separately frozen 512-bin verification follow-up}',
           r'\label{dev:followupaudit125}',
           'The follow-up protocol was fixed after the primary census and original 128-bin audit. It selects the union of the actual final and completed-prefix action keys for every row whose original containment or accepted-gain check remained unresolved. All 110 selected keys are retained. The addendum authorizes exactly one 512-bin evaluation with 32 terminal bisection steps for each key; it authorizes no further adaptive level or changed production action.',
           f"The actual remote source boundary is \\texttt{{{r['source_commit'][:12]}}}. Its complete SHA, manifest, byte readback and before-execution timestamp are retained in the addendum boundary record. The original source freeze and the original audit evidence remain unchanged.",
           r'\begin{center}\small', r'\begin{tabular}{lrrrrr}', r'\hline',
           r'Service & Decisions & \shortstack{Initial\\containment} & \shortstack{Combined\\containment} & \shortstack{Initial\\gain checks} & \shortstack{Combined\\gain checks} \\', r'\hline']
    names = {'fused_control':'Strong fused', 'warm_adaptive':'Warm adaptive',
             'cold_adaptive':'Cold adaptive', 'warm_fixed512':'Warm fixed 512', 'grid33':'Uniform DP'}
    for mode in ('fused_control','warm_adaptive','cold_adaptive','warm_fixed512','grid33'):
        a = r['by_mode'][mode]
        initial_gain = f"{a['initial_gain_confirmed']}/{a['accepted']}" if a['accepted'] else '---'
        combined_gain = f"{a['gain_confirmed']}/{a['accepted']}" if a['accepted'] else '---'
        dev.append(f"{names[mode]} & {a['decisions']} & {a['initial_contained']} & {a['contained']} & {initial_gain} & {combined_gain} " + chr(92)*2)
    dev.extend([r'\hline\end{tabular}', r'\end{center}',
        f"The follow-up newly confirms {r['newly_confirmed_containment']} containments and {r['newly_confirmed_gains']} gain bounds. The original audit remains 850/936 and 193/251; combined verification leaves {r['unresolved_containment']} containment checks and {r['unresolved_gain_bounds']} gain bounds unresolved. Neither absence of contradiction nor completion of a fixed computational protocol is substituted for a confirmed bound.",
        r'The two unresolved containments are the uniform-DP decisions at risk $\alpha=1/2$ and states $(3/4,1/4)$ and $(3/4,3/4)$. They are not accepted policy-improvement rows. Their unresolved status is retained; there is no contradiction and no unplanned refinement.',
        f"The raw terminal trace has exactly {work['requested_contexts']:,} records: {work['reused_contexts']:,} cite an exact original witness and {work['new_contexts']:,} record newly computed terminal problems. New bisection work totals {work['new_terminal_bisections']:,} iterations; the independent primitive records {summary['counts'].get('executed_assertions',0):,} exact assertions. Cache loading takes {r['cache_loading_seconds']:.6f} seconds within the {phase['child_seconds']:.6f}-second child process. The complete parent clock is {phase['complete_parent_seconds']:.6f} seconds. Original witness costs remain charged in the first audit, while exact reuse incurs no newly claimed terminal solve.",
        'The reporting reconciliation separately streams every terminal record, checks the new/reused work counts and bisections against the primitive counters, reconstructs the old/new interval intersections, and recomputes all 936 containment and gain flags. It makes no economic call. All production actions, original regret/width gates, the 231/232 warm target counts, and the original adoption regions remain unchanged.',
        r'\subsection{Observed numerical experiment process costs}',
        r'\begin{center}\small', r'\begin{tabular}{lrrr}', r'\hline',
        r'Process & Child seconds & Complete parent seconds & Peak child MiB \\', r'\hline'])
    for a in r['scientific_phase_costs']:
        name = a['phase'].replace('_',r'\_')
        dev.append(f"{name} & {a['child_seconds']:.6f} & {a['complete_parent_seconds']:.6f} & {a['peak_child_rss_kib']/1024:.3f} " + chr(92)*2)
    dev.extend([r'\hline\end{tabular}',r'\end{center}',
        f"The sum of the listed complete parent-process clocks is {r['sum_complete_scientific_process_seconds']:.6f} seconds. Parent time includes child time, so these two columns are never added. This is a sum of the listed numerical process durations, not a measured total research elapsed time. The separately measured reporting, transport, terminal-gate and bookkeeping receipts remain charged in the machine-readable ledger. Initial theory-diagnostic and historical interrupted process clocks were not all recorded; missing durations are unavailable, not zero. Publication, interactive analysis and document-building clocks are outside this numerical subtotal.",
        'The original and follow-up witness gzip files remain byte-identical to their execution artifacts. For the connector request limit, ordered binary parts of at most 7,000,000 bytes transport the exact original streams. The materializers verify every part, the concatenated byte count and the original SHA256 before any witness is consumed. A transport split is not a modified observation or new economic experiment.'])
    for name, lines in [('MAIN_FOLLOWUP_FRAGMENT125.txt',main_lines),('DEVELOPMENT_FOLLOWUP_FRAGMENT125.txt',dev)]:
        with (out/name).open('x') as f:
            f.write('\n'.join(lines)+'\n')
    receipt = dict(status='executed', economic_evaluations=0, services_retimed=0,
        source_sha256=sha(Path(__file__)), reconciliation_sha256=sha(reconciliation),
        followup_summary_sha256=sha(summary_path),
        outputs={name:sha(out/name) for name in ('MAIN_FOLLOWUP_FRAGMENT125.txt','DEVELOPMENT_FOLLOWUP_FRAGMENT125.txt')},
        seconds=time.perf_counter()-tick)
    with (out/'TEXT_RENDER125.json').open('x') as f:
        json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(receipt,sort_keys=True))


if __name__=='__main__':
    main()
