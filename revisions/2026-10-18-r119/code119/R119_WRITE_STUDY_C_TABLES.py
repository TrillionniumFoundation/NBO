"""Typeset complete already-executed A/B records; no scientific execution."""
from pathlib import Path
from fractions import Fraction as F
import json

HERE = Path(__file__).resolve().parent
A = json.loads((HERE/'R119_NUMERICAL_REVIEW.json').read_text())
B = json.loads((HERE/'R119C_NUMERICAL_REVIEW.json').read_text())
ECON = json.loads((HERE/'R119C_ECONOMIC_COMPARISONS.json').read_text())
ARMS = ('online','quadratic','relu','hinge','spline','poly2','poly3','grid')
SERVICES = ('compiled','geometric','active-tail','masked-tail','budgeted-tail','fused-tail')
NAMES = dict(online='Online',quadratic='Quadratic',relu='ReLU',hinge='Hinge',
             spline='Spline',poly2='Polynomial 2',poly3='Polynomial 3',grid='Grid')
SN = dict(compiled='C',geometric='G',**{'active-tail':'T','masked-tail':'M','budgeted-tail':'B','fused-tail':'F'})


def bound(value, digits, upper=True, scale=1):
    x = F(float(value))*scale*10**digits
    n = -((-x.numerator)//x.denominator) if upper else x.numerator//x.denominator
    sign = '-' if n < 0 else ''
    s = str(abs(n)).zfill(digits+1)
    return sign+(s[:-digits]+'.'+s[-digits:] if digits else s)


def write(name, text):
    (HERE/name).write_text(text.rstrip()+'\n')


def longtable(caption, label, columns, header, rows, note):
    n = len(columns)
    return '\n'.join([
        r'\begingroup\footnotesize\setlength{\tabcolsep}{3pt}',
        r'\begin{longtable}{'+columns+'}',
        r'\caption{'+caption+r'}\label{'+label+r'}\\',
        r'\toprule',header+r'\\\midrule',r'\endfirsthead',
        r'\multicolumn{'+str(n)+r'}{l}{\textit{Continued: '+caption+r'}}\\',
        r'\toprule',header+r'\\\midrule',r'\endhead',
        r'\midrule\multicolumn{'+str(n)+r'}{r}{\textit{Continued on next page}}\\',r'\endfoot',
        r'\bottomrule',r'\endlastfoot',*rows,r'\end{longtable}',
        r'\noindent '+note,r'\endgroup'])


lookup={(r['index'],r['arm'],r['service']):r for r in B['frontier']}
rows=[]
for i in range(2):
    for arm in ARMS:
        rr=[lookup[i,arm,s] for s in SERVICES]
        rows.append(('1/2' if i==0 else '3/4')+' & '+NAMES[arm]+' & '+
                    ' & '.join(f"{r['timing32_median_seconds']:.4f}" for r in rr)+r' \\')
write('R119_TABLE119C_TIMING.tex','\n'.join([
    r'\begin{table}[t]\centering\small',
    r'\caption{Phase C: complete 32-state service times, all arms and services}',
    r'\label{tab:timing119c}',r'\begin{tabular}{llrrrrrr}\toprule',
    r'$\alpha$ & Representation & C & G & T & M & B & F\\\midrule',
    *rows,r'\bottomrule\end{tabular}',r'\par\smallskip\footnotesize',
    r'Medians in seconds from all seven fresh sequential processes. C: 128-bin compiled; G: geometric whole-support; T: original active tail; M: positive-tail masking with the full ladder; B: masked two-level budget; F: the same budget with one packed compiler call per resolution. Every service pays its proposal, refusals, repairs and certificates. Acquisition is reported separately. Observed ranges and every clock are retained in the development companion.',
    r'\end{table}']))

rows=[]
for i in range(2):
    for arm in ARMS:
        g,b=lookup[i,arm,'geometric'],lookup[i,arm,'fused-tail']
        rows.append(('1/2' if i==0 else '3/4')+' & '+NAMES[arm]+' & '+
                    f"{g['acquisition_seconds']:.4f} & {g['component_sum_acquisition_loading_primary144_seconds']:.4f} & {b['component_sum_acquisition_loading_primary144_seconds']:.4f} & "+
                    bound(g['primary_mean_regret_upper'],3,scale=10**6)+' & '+
                    bound(g['primary_max_action_distance_upper'],3,scale=10**3)+r' \\')
write('R119_TABLE119C_COST.tex','\n'.join([
    r'\begin{table}[t]\centering\small',
    r'\caption{Phase C: paid acquisition, complete 144-state cost and economic bounds}',
    r'\label{tab:cost119c}',r'\begin{tabular}{llrrrrr}\toprule',
    r'$\alpha$ & Representation & $A$ & $F_G$ & $F_F$ & $10^6\overline L$ & $10^3\overline d_{\max}$\\\midrule',
    *rows,r'\bottomrule\end{tabular}',r'\par\smallskip\footnotesize',
    r'$A$ includes original labels, every fit and candidate audit, and serialization; hinge includes the full ReLU acquisition. $F_s=A+\text{actual load time}+\text{actual 144-state service time}$, in seconds. These are recorded component sums, not new clocks. $\overline L$ is an outward upper bound for catalogue-mean original-policy regret; $\overline d_{\max}$ bounds the largest distance to the original optimal action. All six services have the same returned policies, so their economic bounds coincide. Displayed bound endpoints are rounded outward.',
    r'\end{table}']))

for phase,source in [('C',B)]:
    rows=[]
    for r in source['frontier']:
        cells=[('1/2' if r['index']==0 else '3/4'),NAMES[r['arm']],SN[r['service']],
            f"{r['acquisition_seconds']:.4f}",f"{r['primary144_service_seconds']:.4f}",
            f"{r['component_sum_acquisition_loading_primary144_seconds']:.4f}",
            f"{r['timing32_median_seconds']:.4f}",f"[{r['timing32_min_seconds']:.4f},{r['timing32_max_seconds']:.4f}]",
            str(r['original_risk_point_queries']),str(r['rejected_attempted_certificates'])]
        rows.append(' & '.join(cells)+r' \\')
    write(f'R119_TABLE119{phase}_FRONTIER.tex',longtable(
        f'Phase {phase}: complete {len(rows)}-row numerical frontier',f'tab:frontier119{phase.lower()}',
        'lllrrrrlrr',r'$\alpha$ & Arm & Service & $A$ & $C_{144}$ & $F_{144}$ & $M_{32}$ & Range$_{32}$ & Queries & Refused',rows,
        'Times are seconds. $A$ is standalone acquisition, $C_{144}$ the observed primary service, '
        '$F_{144}$ its sum with acquisition and actual model loading, and $M_{32}$ the median of all seven 32-state clocks. '
        'Queries are actual original terminal-risk point evaluations for the full 144-state service; Refused counts every '
        'rejected certificate attempt, including repeated refusals at the same action. '
        'C, G, T, M, B, F are defined in Table~\\ref{tab:timing119c}. '
        + ('All original phase-A clocks are retained, including the disclosed document-formatting overlap; they are not replaced or pooled with phase C.' if phase=='A' else 'Phase C uses fresh acquisition and clocks; its state catalogue was already observed in phases A/B.')))

rows=[]
for r in B['frontier']:
    rows.append(' & '.join([('1/2' if r['index']==0 else '3/4'),NAMES[r['arm']],SN[r['service']]]+
                          [f'{1000*t:.2f}' for t in r['timing32_all_seconds']])+r' \\')
write('R119_TABLE119C_ALL_CLOCKS.tex',longtable('Phase C: every recorded timing repeat',
    'tab:allclocks119c','lllrrrrrrr',r'$\alpha$ & Arm & Service & 0 & 1 & 2 & 3 & 4 & 5 & 6',rows,
    'Milliseconds per complete 32-state service. No warm-up, discarded repeat, timing confidence interval, or new timing execution is used. '
    'The columns identify the seven actual sequential subprocesses, with the prospectively declared rotation within each process.'))

rows=[]
for i in range(2):
    for arm in ARMS:
        r=lookup[i,arm,'compiled']
        interval='['+bound(r['primary_mean_original_cost_lower'],8,False)+','+bound(r['primary_mean_original_cost_upper'],8)+']'
        regret='['+bound(r['primary_mean_regret_lower'],3,False,10**6)+','+bound(r['primary_mean_regret_upper'],3,True,10**6)+']'
        rows.append(' & '.join([('1/2' if i==0 else '3/4'),NAMES[arm],interval,regret,
            bound(r['primary_max_regret_upper'],3,True,10**6),
            bound(r['primary_mean_action_distance_upper'],3,True,10**3),
            bound(r['primary_max_action_distance_upper'],3,True,10**3)])+r' \\')
write('R119_TABLE119C_ECONOMICS.tex',longtable('Original-policy costs, regret and action bounds',
    'tab:economics119c','llllrrr',r'$\alpha$ & Arm & Mean original $J$ & $10^6$ mean regret & $10^6 L_{\max}$ & $10^3d_{\rm mean}$ & $10^3d_{\max}$',rows,
    'All endpoints are rounded outward. The same returned action and unchanged future controller occur under all six services '
    'for each arm and state. Thus this 16-row economic table applies to the complete 96-row service table without omitting any distinct policy. '
    'The separate 1024-bin full-support references use the shared verified terminal compiler and retain numerical bounds, not exact regret or population uncertainty.'))

rows=[]
for r in B['acquisition']:
    c=r['components']
    serial=c.get('serialization_seconds',0)+c.get('underlying_relu_serialization_seconds',0)
    rows.append(' & '.join([('1/2' if r['index']==0 else '3/4'),NAMES[r['arm']],str(r['label_sites']),
        f"{c['label_cost_if_standalone_seconds']:.5f}",f"{c['fit_seconds']:.5f}",f"{c['audit_seconds']:.5f}",
        f'{serial:.5f}',f"{r['seconds']:.5f}",str(r['payload_bytes'])])+r' \\')
write('R119_TABLE119C_ACQUISITION.tex',longtable('Phase C: standalone acquisition components',
    'tab:acquisition119c','llrrrrrrr',r'$\alpha$ & Arm & Labels & Label sec & Fit sec & Audit sec & Serial sec & Total sec & Bytes',rows,
    'Serialization for hinge includes its own encoding and the underlying ReLU serialization. Hinge also receives the complete '
    'underlying ReLU fit and audit charges. The shared tournament acquisition is 0.323457444 seconds; shared costs are not summed '
    'again and called that elapsed campaign cost. Polynomial and grid ranks/storage are not described as equal to the rank-six models.'))

rows=[]
for r in ECON:
    if r['same']==144:
        interval='[0,0]'
    else:
        interval='['+bound(r['mean_difference_lower'],3,False,10**6)+','+bound(r['mean_difference_upper'],3,True,10**6)+']'
    rows.append(' & '.join([('1/2' if r['alpha']==.5 else '3/4'),NAMES[r['control']],NAMES[r['treatment']],interval,
        str(r['same']),str(r['treatment_strictly_lower_cost']),str(r['treatment_strictly_higher_cost']),str(r['not_resolved'])])+r' \\')
write('R119_TABLE119C_ALL_ECONOMIC_CONTRASTS.tex',longtable('Every between-representation original-cost contrast',
    'tab:crossarm119c','llllrrrr',r'$\alpha$ & Control & Treatment & $10^6\overline{(J_T-J_C)}$ & Equal & Better & Worse & Unresolved',rows,
    'All 56 representation-by-risk contrasts are retained. Mean bounds use every state and exact zero for identical policies. '
    'Better and Worse are per-state strict interval certificates; they are neither a significance test nor a majority-vote criterion for mean economic benefit.'))

rows=[]
for r in B['comparisons']:
    rows.append(' & '.join([('1/2' if r['index']==0 else '3/4'),NAMES[r['arm']],SN[r['control']],SN[r['treatment']],
        f"{r['median_time_ratio']:.4f}",f"{r['primary_time_ratio']:.4f}",f"{r['full144_component_ratio']:.4f}",
        str(r['faster_timing_repeats']),f"{r['risk_query_ratio']:.4f}"])+r' \\')
write('R119_TABLE119C_ALL_SERVICE_CONTRASTS.tex',longtable('Every within-representation service comparison',
    'tab:allservices119c','llllrrrrr',r'$\alpha$ & Arm & Ctl & Trt & $M_T/M_C$ & $C_T/C_C$ & $F_T/F_C$ & Wins/7 & Query ratio',rows,
    'Ratios use treatment over control and contemporaneous phase-C records. All 240 comparisons are shown. '
    'Each one has 144 identical complete policies and exact zero original-cost contrast; ratios therefore describe resource use only.'))

print('Generated complete C tables from existing numerical records only.')
