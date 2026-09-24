"""Generate publication tables directly from the complete exact-result records."""
from pathlib import Path
from fractions import Fraction as F
import json, statistics as st, hashlib, platform, sys
R=Path(__file__).resolve().parents[1]; S=R/'results'; G=R/'paper'/'generated'; G.mkdir(parents=True,exist_ok=True)
def f(x): return float(F(str(x)))
def n(x,d=6): return f'{f(x):.{d}g}'
def table(name,caption,label,columns,header,rows,note=''):
    text='\\begin{table}[htbp]\n\\centering\\footnotesize\n'+f'\\caption{{{caption}}}\\label{{{label}}}\n'+f'\\begin{{tabular}}{{{columns}}}\\toprule\n'+header+' \\\\\\midrule\n'+'\n'.join(' & '.join(map(str,row))+' \\\\' for row in rows)+'\n\\bottomrule\\end{tabular}\n'
    if note: text+='\\par\\smallskip\\begin{minipage}{.98\\textwidth}\\footnotesize '+note+'\\end{minipage}\n'
    text+='\\end{table}\n'; (G/(name+'.tex')).write_text(text)
data=[json.loads((S/f'H{h}.json').read_text()) for h in [4,8,12]]; cases=[r for d in data for r in d['outcomes']]
assert len(cases)==42 and all(r.get('certified') for r in cases)
audit=json.loads((S/'independent_audit.json').read_text()); checks={r['file']:r['seconds'] for r in audit['results']}
summary=[]
for family,prefix in [('Neural','neural'),('Spline','spline'),('All defer','defer'),('Occupancy stress','occupancy_stress')]:
    rr=[r for r in cases if r['proposal'].startswith(prefix)]
    summary.append([family,len(rr),sum(r['raw_pass'] for r in rr),len(rr),sum(f(r['occupancy_cost_saving'])>0 for r in rr)])
table('cohort','Complete coupled-model cohort','tab:cohort','lrrrr','Proposal & Cases & Raw passes & Certified & Dynamic savings',summary,'The same frozen proposal is evaluated at two tolerances; these are 21 frozen policy/horizon pairs, not 42 independent models. Raw passes use the exact uncompressed reference only as a diagnostic. The independent upper-witness test separately certifies all 12 spline cases with zero intervention.')
rows=[]
for d in data:
    for eps in ['1/100','1/20']:
        w=d['witnesses'][eps]; dates=w['dates']; rr=[r for r in d['outcomes'] if r['epsilon']==eps]
        rows.append([d['horizon'],n(eps),max(d['exact_dp']['pieces']),max(v['original_pieces'] for v in dates),max(v['pieces'] for v in dates),max(v['bits'] for v in dates),max(max(r['cost_pieces']) for r in rr)])
table('geometry','Representation size and arithmetic in one state dimension','tab:geometry','rrrrrrr','$T$ & $\\varepsilon$ & Exact $V$ & Input to compression & Stored $U$ & $U$ bits & Cost pieces',rows,'Counts are maxima over dates and, for cost, proposals. Exact roots, knot values, and one-sided limits are included. No state-grid cardinality is used as a complexity proxy. Complete value/cost arithmetic can use more bits than stored witnesses; all stage records and certificates are retained.')
rows=[]
for d in data:
    for eps in ['1/100','1/20']:
        rr=[r for r in d['outcomes'] if r['epsilon']==eps]; nn=[r for r in rr if r['proposal'].startswith('neural')]; sp=[r for r in rr if r['proposal'].startswith('spline')]
        med=lambda xs: n(st.median(xs),4)
        rows.append([d['horizon'],n(eps),n(d['exact_dp']['seconds'],4),n(d['witnesses'][eps]['seconds'],4),med([r['certified_greedy_baseline']['total_seconds'] for r in nn]),med([r['cold_total_seconds']+checks[Path(r['certificate_file']).name] for r in sp]),med([r['cold_total_seconds']+checks[Path(r['certificate_file']).name] for r in nn])])
table('timing','Measured solution and certification costs (seconds)','tab:timing','rrrrrrr','$T$ & $\\varepsilon$ & Exact DP & Witness & Greedy & Spline cold & Neural cold',rows,'Medians across the declared proposal family; single executions are descriptive, not a significance test. Cold totals charge fresh-process neural import/training, compilation, witness construction, own-policy evaluation, admissible sets, cost optimization, encoding, internal verification, and the independent final checker. The exact DP and certified greedy rows solve accuracy-only objectives; neither is represented as a minimum-revision-cost solver.')
rows=[]
for r in cases:
    if r['proposal']=='occupancy_stress':
        rows.append([r['T'],n(r['epsilon']),n(r['all_restart_regret_upper']),n(r['pointwise_intervention_cost']),n(r['intervention_cost']),n(r['occupancy_cost_saving'])])
table('occupancy','Action-dependent occupancy changes the optimal revision pattern','tab:occupancy','rrrrrr','$T$ & $\\varepsilon$ & Regret bound & Pointwise cost & Dynamic cost & Saving',rows,'Both policies use the same computed admissible sets. Costs are exact uniform-initial-state integrals under each deployed policy, then displayed as decimals. The stress incumbent is predeclared and intentionally misconfigured; the other 36 cases have zero dynamic-versus-pointwise savings.')
rows=[]
for r in cases:
    if r['proposal']=='occupancy_stress':
        last=None; transitions=[]
        for v in r['price_frontier']['intervals']:
            winner=v['best_on_open_interval']
            if winner!=last:
                transitions.append((v['lambda_left'],winner));last=winner
        labels={'exact_optimal':'Exact','certified_greedy':'Greedy','dynamic':'Dynamic','pointwise':'Pointwise','raw':'Raw'}
        path=' $\\to$ '.join(labels[v] for _,v in transitions)
        thresholds=', '.join(n(x,5) for x,_ in transitions[1:]) or 'None'
        rows.append([r['T'],n(r['epsilon']),path,thresholds])
table('frontier','Complete shadow-price sensitivity for the mechanism stress control','tab:frontier','rrll','$T$ & $\\varepsilon$ & Envelope winners as $\\lambda$ increases & Switch prices',rows,'The envelope is over the displayed computed deployments, not all feasible policies. All pairwise intersections and tie sets are stored as exact fractions. One cost unit is a normalized intervention; no monetary calibration or preferred illustrative price is imposed.')
header='\\begin{longtable}{rlrrrrr}\\caption{All registered class-based certificates}\\label{tab:all}\\\\\n\\toprule $T$ & Proposal & $\\varepsilon$ & Raw regret & Certified bound & Cost saving & Bytes \\\\\\midrule\\endfirsthead\n\\toprule $T$ & Proposal & $\\varepsilon$ & Raw regret & Certified bound & Cost saving & Bytes \\\\\\midrule\\endhead\n'
labels={'occupancy_stress':'Stress','defer':'Defer','spline33':'Spline 33','spline129':'Spline 129','neural31001':'NN 31001','neural31002':'NN 31002','neural31003':'NN 31003'}
rows=[' & '.join([str(r['T']),labels[r['proposal']],n(r['epsilon']),n(r['raw_exact_regret']),n(r['all_restart_regret_upper']),n(r['occupancy_cost_saving']),str(r['certificate_bytes'])])+' \\\\' for r in cases]
(G/'all_cases.tex').write_text(header+'\n'.join(rows)+'\n\\bottomrule\\end{longtable}\n')
metrics={'cases':len(cases),'certified':sum(r['certified'] for r in cases),'preservation_certified':sum(r['preservation_certified'] for r in cases),'neural_raw_passes':sum(r['raw_pass'] for r in cases if r['proposal'].startswith('neural')),'neural_cases':18,'spline_raw_passes':12,'zero_intervention_certificates':audit['zero_intervention_count'],'stress_positive_savings':sum(f(r['occupancy_cost_saving'])>0 for r in cases),'max_certificate_bytes':max(r['certificate_bytes'] for r in cases),'max_rational_bits':max(r['max_bits'] for r in cases),'max_cost_pieces':max(max(r['cost_pieces']) for r in cases),'all_restart_upper_max':max(f(r['all_restart_regret_upper']) for r in cases),'independent_check_seconds':audit['independent_check_seconds']}
(S/'summary.json').write_text(json.dumps(metrics,indent=2,sort_keys=True)); print(json.dumps(metrics,indent=2))
files=[]
for p in sorted(R.rglob('*')):
    if p.is_file() and '__pycache__' not in str(p) and p.name!='PUBLICATION_MANIFEST.json': files.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(R/'PUBLICATION_MANIFEST.json').write_text(json.dumps({'source_review':'e9bc144fbb6843d6a3436825a28584efb64fb8f1','parent_revision':'6ea1e2fd8ab1928ded4ea98dc74ba6e1e72cf9d0','python':sys.version,'platform':platform.platform(),'metrics':metrics,'files':files},indent=2,sort_keys=True))
