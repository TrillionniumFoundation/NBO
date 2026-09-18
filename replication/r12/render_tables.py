"""Tables are generated only after the independent witness check succeeds."""
import json,math
from pathlib import Path
HERE=Path(__file__).parent;ROOT=HERE.parents[1];OUT=HERE/'output';PAPER=ROOT/'revisions/2026-09-18-r12-procurement-witness/paper'
def read(n):return json.loads((OUT/n).read_text())
def sci(x):
    if x==0:return '$0$'
    power=math.floor(math.log10(abs(x)));return f'${x/10**power:.3f}\\times10^{{{power}}}$'
def write(name,caption,label,columns,head,rows,note):
    text='\\begin{table}[tbp]\n\\centering\n\\caption{'+caption+'}\\label{'+label+'}\n\\begin{tabular}{'+columns+'}\n\\toprule\n'+head+' \\\\\n\\midrule\n'
    text+=' \\\\\n'.join(' & '.join(r) for r in rows)+' \\\\\n\\bottomrule\n\\end{tabular}\n\\par\\smallskip\n{\\footnotesize '+note+'}\n\\end{table}\n'
    (PAPER/(name+'.tex')).write_text(text)
validation=read('independent_validation.json');assert validation['all_passed']
p=read('procurement.json');byid={r['id']:r for r in p['rows']};center=[r for r in p['choices'] if r['b']==1.]
rows=[]
for choice in center:
    r=byid[choice['choice']];a='Adjustment' if r['adjustment'] else 'No adjustment'
    rows.append([a,f"$(+, {r['fee']:.1f}, {r['term']})$",f"{r['grant_executable']:.8f}",f"$[{math.floor(r['service_lower']*1e7)/1e7:.7f}, {math.ceil(r['service_upper']*1e7)/1e7:.7f}]$",sci(choice['margin'])])
write('procurement_table','Certified procurement choices at $b=1$ and $\\kappa=0.02$','tab:r12_procurement','lcrcr','Regime & $(\\sigma,E,m)$ & Grant & Service enclosure & Margin',rows,'The margin compares the chosen lower surplus with every rival upper surplus and zero. Service endpoints are displayed outward. Each regime has 96 offers. The minimum strict margin over the eight price-box/regime vertices is '+sci(min(r['margin'] for r in validation['procurement']['price_box_corners']))+'. Full precision is in the deposited witness record.')
rows=[]
for b in (.8,.9,.94,.98,1.,1.02,1.05):
    rr=[r for r in p['choices'] if r['b']==b];one=[f'{b:.2f}']
    for adj in (True,False):
        r=next(x for x in rr if x['adjustment']==adj)
        if r['choice']=='outside':name='No offer'
        else:
            q=byid[r['choice']];name=f"$(+, {q['fee']:.1f}, {q['term']})$" if q['sign']=='positive' else f"$(-, {q['fee']:.1f}, {q['term']})$"
        one += [name,sci(r['margin'])]
    rows.append(one)
write('price_table','Service price and procurement at $\\kappa=0.02$','tab:r12_prices','rcrcr','$b$ & Adjustment & Margin & No adjustment & Margin',rows,'A positive margin certifies the indicated point choice against the complete menu. A nonpositive margin would be explicitly inconclusive; it would not be labeled a certificate. These point comparisons do not establish behavior between displayed prices.')
rows=[]
for r in read('exposure.json')['rows']:
    z=r['relative'];rows.append([f"{r['law']:.3f}",f"{r['benefit']:.5f}",f"$({r['fee']:.1f},{r['term']})$",sci(z['local']),sci(z['future']),sci(z['financial_replacement']),sci(z['option'])])
write('exposure_table','Relative adjustment option: current drift, future exposure, and financial replacement','tab:r12_exposure','rrcrrrr','$\\lambda$ & $d$ & $(F,m)$ & Local & Future & Replacement & Total',rows,'Each row compares the positive and nonpositive classes. These are pointwise decompositions. The continuation uncertainty radius is approximately $2.1\\times10^{-7}$ per future-exposure comparison. The full signed intervals and wealth-bin contributions are deposited and independently reconstructed.')
rows=[]
for name,desc in [('adjusted','Adjusted positive minus nonpositive'),('zero','Unadjusted positive minus nonpositive'),('active_surrender_gain','Unadjusted positive: surrender gain')]:
    a,b=validation['regional']['bounds']['chord'][name];lo=math.floor(a*1e10)/1e10;hi=math.ceil(b*1e10)/1e10
    rows.append([desc,f'$[{lo:.10f},\\ {hi:.10f}]$'])
write('region_table','Joint regional comparisons on the canonical R12 target','tab:r12_region','lc','Comparison & Certified interval',rows,'Displayed endpoints are rounded outward. Both upper constructions independently reproduce these regional signs. Lower-policy feasibility, corner/degree ordering, upper recursions, and all support-tube transport inequalities are checked from canonical arrays.')
rows=[]
for r in read('broader.json')['rows']:
    rows.append([f"$[{r['law'][0]:g},{r['law'][1]:g}]$",'Adj.' if r['adjustment'] else 'Zero',sci(r['max_chord_correction']),sci(r['per_value_uniform_gap']['chord']),sci(r['per_value_uniform_gap']['count']),f"{r['nonendpoint_seconds']['chord']:.2f}/{r['nonendpoint_seconds']['count']:.2f}"])
write('broader_table','Matched law-range comparisons','tab:r12_broader','lcrrrr','Law range & Regime & Correction & Chord gap & Count gap & Work (s)',rows,'Gaps include $2\\times10^{-7}$ evaluation allowance. Work reports chord/count nonendpoint seconds; common endpoint and lower-policy costs are charged to both in the machine-readable account. Complete coefficient differences, endpoint actions and package-level load/validation costs are deposited. The broader gaps are not a financial-sign theorem.')
print('TABLES GENERATED FROM VERIFIED WITNESSES')
