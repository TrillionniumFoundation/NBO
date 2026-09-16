#!/usr/bin/env python3
"""Generate publication tables from executed records; no transcribed timings."""
from core import *
PAPER=ROOT/'revisions/2026-09-16-r7/paper';REV=PAPER.parent

def number(x,digits=6):
    s=f'{x:.{digits}g}'
    if 'e' in s:
        a,b=s.split('e');return rf'${a}\times10^{{{int(b)}}}$'
    return s

def table(name,caption,label,cols,head,rows,note):
    text='\\begin{table}[!htbp]\n\\centering\\small\n'+f'\\caption{{{caption}}}\n\\label{{{label}}}\n'+f'\\begin{{tabular}}{{{cols}}}\n\\toprule\n'+head+' \\\\\n\\midrule\n'
    text+='\n'.join(' & '.join(r)+' \\\\' for r in rows)
    text+='\n\\bottomrule\n\\end{tabular}\n\\par\\smallskip\n\\begin{minipage}{0.98\\linewidth}\\footnotesize\nNotes: '+note+'\n\\end{minipage}\n\\end{table}\n'
    (PAPER/name).write_text(text)

def run():
    matched=json.loads((OUT/'matched.json').read_text());decision=json.loads((OUT/'decision.json').read_text());primitive=json.loads((OUT/'primitive.json').read_text());adaptive=json.loads((OUT/'adaptive.json').read_text())
    rows=[]
    for r in matched['rows']:
        for i,(key,label) in enumerate((('chord','Compressed'),('count','Local count'),('rectangular','Rectangular'))):
            z=r['methods'][key]
            rows.append([f"{r['d']:g}" if i==0 else '',str(r['anchor_count']) if i==0 else '',label,number(z['bound']),f"{z['upper_seconds']:.2f}",f"{z['matched_total_seconds']:.2f}"])
    table('table_r7_matched.tex','Matched Upper-Oracle Precision and Work','tab:r7_matched','rrlrrr',r'$d$ & Anchors & Upper oracle & Bound & Upper sec. & Total sec.',rows,
        r'All states, dates, and $\lambda\in[0,1]$; identical two-policy lower banks and eight cells within each compared interval. The 19-, 18-, and 17-anchor banks are the original R6 banks; the 6- and 10-anchor banks coarsen the $d=0.5$ bank. Total time includes common kernel setup, anchor solves, policy evaluation, coefficient restriction, upper construction, and certification. Shared stages are attributed equally. One serial single-thread pass; diagnostic replay is excluded equally. Kernel-call and persistent-array counts, every interval bound, and stage times are in the replication records.')
    rows=[]
    for r in adaptive['rows']:
        rows.append([r['method'].capitalize(),str(r['anchor_count']),number(r['bound']),str(r['upper_kernel_applications']),f"{r['total_seconds']:.2f}"])
    table('table_r7_adaptive.tex','Autonomous Refinement from Empty Policy Caches','tab:r7_adaptive','lrrrr',r'Rule & Anchors & Final bound & Kernel calls & Total sec.',rows,
        r'Full target, $d=0.5$, tolerance $10^{-3}$. Each arm starts at $[0,1]$ and includes all rejected parent intervals. Kernel calls are action-wide upper-oracle applications, not anchor-solve calls. Total time includes both. Cascade tries local count only after compressed certification fails. All arms use identical dyadic split order, two endpoint policies, and eight certificate cells.')
    a,b,c=adaptive['rows'];reduction=a['anchor_count']-c['anchor_count']
    (PAPER/'r7_adaptive_interpretation.tex').write_text(f"The chord-only procedure requests {a['anchor_count']} anchors; local count requests {b['anchor_count']}; the cascade requests {c['anchor_count']}. Thus the cascade avoids {reduction} endpoint optimizations relative to chord-only refinement at the same certified tolerance. Its elapsed time is {c['total_seconds']:.2f} seconds, against {a['total_seconds']:.2f} and {b['total_seconds']:.2f} for the two single-oracle procedures, respectively. The measured costs, rather than the anchor reduction alone, determine the computational comparison.\n")
    rows=[]
    for arm,label in [('adjusted','Adjustment available'),('fixed','No deliberate adjustment')]:
        lo=min(z['delta'][arm][0] for z in decision['cells']);hi=max(z['delta'][arm][1] for z in decision['cells']);gap=max(v for z in decision['cells'] for v in z['class_gaps'][arm].values())
        rows.append([label,number(lo),number(hi),number(gap)])
    note=(r'Initial state $(u,X)=(2,1.25)$, $k=2$, full finite target, entire $(\lambda,d)\in[0,0.25]\times[0.4,0.45]$. Bounds include the arithmetic allowance. Maximum class gap is the larger of the two class-specific upper-minus-feasible-lower certificates in that regime. The per-class arithmetic allowance is '+number(decision['roundoff']['per_class_allowance'])+r'; the lower bound on the relative adjustment option is '+number(decision['minimum_relative_option'])+r'. Eight corner optimizations produce sixteen feasible class policies; eight count constructions certify the rectangle. No generic $10^{-3}$ welfare tolerance is used for these signs.')
    table('table_r7_decision.tex','A Joint-Region Certificate for the Adjustment Effect','tab:r7_decision','lrrr',r'Adjustment regime & Lower $\Delta$ & Upper $\Delta$ & Max. class gap',rows,note)
    rows=[[f"{r['downside_probability']:.2f}",f"{r['cost']:.0f}",number(r['relative_option_lower']),number(r['relative_option_exact']),number(r['guaranteed_threshold_shift']),number(r['declared_contract'])] for r in primitive['rows']]
    table('table_r7_primitive.tex','Primitive Predictions and Optimized Adjustment Options','tab:r7_primitive','rrrrrr',r'$p$ & $k$ & Lower option & Actual option & Min. shift & Test $d$',rows,
        r'Two-stage CRRA family: $u_0=2$, $|\theta|\leq0.2$, $C_-=0.5$, $C_+\in\{0.05,0.8\}$, and $A_+-A_-=0.5$. Option denotes $\Omega_+-\Omega_-$. The primitive lower bound determines the test contract, at which every row has $\Delta^0<0<\Delta^{\rm adj}$. The continuous-family proof covers all $p\in[0.06,0.10]$ and $k\in[20,80]$, not just these rows. Values are in fixed cardinal utility and operating-benefit units.')
    lines=['# R7 execution summary','', 'These records are generated from an actual run of the deposited code. They do not establish publication acceptance, a diffusion approximation theorem, or neural dominance.','', '## Matched full-model comparison','', '| d | anchors | chord bound | local-count bound | rectangular bound | chord total s | count total s |','|---:|---:|---:|---:|---:|---:|---:|']
    for r in matched['rows']:
        m=r['methods'];lines.append(f"| {r['d']} | {r['anchor_count']} | {m['chord']['bound']:.16g} | {m['count']['bound']:.16g} | {m['rectangular']['bound']:.16g} | {m['chord']['matched_total_seconds']:.6f} | {m['count']['matched_total_seconds']:.6f} |")
    lines+=['','All compared arms include setup, anchor optimization, policy evaluation, local restriction, upper construction and certificate subdivision. One pass, one machine, one thread. The 51 original intervals reproduce the sixth-round comparison; the two coarser banks are additional.','', '## Autonomous refinement','']
    for r in adaptive['rows']:lines.append(f"- {r['method']}: {r['anchor_count']} anchors; bound {r['bound']:.16g}; total {r['total_seconds']:.6f} s; {r['upper_kernel_applications']} upper kernel applications, including rejected parents.")
    lines+=['','## Joint economic decision','',f"Entire rectangle lambda in [0, 0.25], d in [0.4, 0.45], at (u,X)=(2,1.25), k=2. Minimum adjusted positive-class advantage: {decision['minimum_adjusted_advantage']:.16g}. Minimum fixed-adjustment nonpositive-class advantage: {decision['minimum_fixed_disadvantage']:.16g}. Minimum relative option: {decision['minimum_relative_option']:.16g}.",'',f"Per-class a priori floating-point allowance: {decision['roundoff']['per_class_allowance']:.16g}; scope is the stored finite target, not quadrature construction or diffusion discretization. Eight corner optimizations, sixteen class policies, eight count upper constructions. All tensor coefficients are deposited.",'','## Primitive family','',f"For all p in [0.06,0.10], k in [20,80], the computed exact-formula lower estimate for the relative option is {primitive['continuous_family']['relative_option_lower']:.16g}; the manuscript uses the conservatively rounded 0.00186 bound. The implied threshold shift exceeds 0.00372. This is an analytical two-stage specialization, not a calibration replacing the full economy.",'','## Validation scope','', 'Independent small-model recursions test count dominance, finite-horizon operation counts, upper validity, and the total coefficient-error bound. The mathematical proofs establish the general statements. Coefficient-only replay verifies the deposited decision intervals. Historical R4--R6 results are preserved inputs; the R7 run does not claim to retrain all historical networks.','']
    (REV/'execution_summary.md').write_text('\n'.join(lines))
    save('publication_tables.json',dict(tables={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in PAPER.glob('table_r7_*.tex')},generated_from=['matched.json','adaptive.json','decision.json','primitive.json']))
if __name__=='__main__':run()
