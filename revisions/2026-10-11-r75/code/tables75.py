"""Outward-rounded publication tables from the fixed thirteen-estimand family."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
import json
R=Path(__file__).resolve().parents[1]
ORDER=['relu-n8-minus-zero','bernstein-n8-minus-zero','relu-n16-minus-zero','bernstein-n16-minus-zero','relu-n8-minus-bernstein-n8','relu-n16-minus-bernstein-n16','relu-n16-minus-relu-n8','bernstein-n16-minus-bernstein-n8']
LABELS=['ReLU 8 vs. zero','Bernstein 8 vs. zero','ReLU 16 vs. zero','Bernstein 16 vs. zero','ReLU 8 vs. Bernstein 8','ReLU 16 vs. Bernstein 16','ReLU 16 vs. ReLU 8','Bernstein 16 vs. Bernstein 8']
def endpoint(x,up,d=6):
    x=F(x);scale=10**d;k=-((-x.numerator*scale)//x.denominator) if up else x.numerator*scale//x.denominator
    sign='-' if k<0 else '';k=abs(k);return sign+str(k//scale)+'.'+str(k%scale).zfill(d)
def band(v,d=6):return '['+endpoint(v[0],False,d)+', '+endpoint(v[1],True,d)+']'
def table(name,caption,columns,head,rows,note):
    s='\\begin{table}[htbp]\n\\centering\n\\caption{'+caption+'}\\label{tab:'+name+'}\n{\\small\\setlength{\\tabcolsep}{4pt}\n\\begin{tabular}{'+columns+'}\n\\hline\n'
    s+=' & '.join(head)+r' \\'+'\n\\hline\n'
    s+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
    s+='\n\\hline\n\\end{tabular}}\n\\par\\smallskip\n{\\footnotesize '+note+'}\n\\end{table}\n'
    if any(ord(c)<32 and c not in '\n\t\r' for c in s):raise AssertionError('Invalid TeX control character')
    (R/'tables'/(name+'.tex')).write_text(s)
def main():
    r=json.loads((R/'results74/study.json').read_text());a=json.loads((R/'audit/RESULT_AUDIT75.json').read_text());inf=r['inference'];rows=[]
    names=['zero','relu-n8','bernstein-n8','relu-n16','bernstein-n16'];labels=['Zero investment','ReLU, 8','Bernstein, 8','ReLU, 16','Bernstein, 16']
    for key,label in zip(names,labels):
        gain='--' if key=='zero' else band(a['gains'][key+'-minus-zero']['gain_interval'])
        rows.append([label,band(inf['absolute_costs'][key]['interval']),gain])
    table('cost75','Actual original-law costs and gains over the feasible incumbent','lcc',['Controller','Expected cost','Zero minus controller'],rows,'All thirteen estimands share one simultaneous coverage event of at least 99 percent under the independent-bin model. Endpoints are rounded outward. Paired gains use paired observations, not subtraction of marginal intervals. There are 131,072 joint rows, not five independent datasets.')
    rows=[]
    for j,(key,label) in enumerate(zip(ORDER,LABELS),1):
        v=inf['contrasts'][key];rows.append([j,label,band(v['interval']),'Yes' if v['precision_met'] else 'No','Yes' if v['equivalent'] else 'No'])
    table('contrasts75','Every predeclared complete-policy contrast','rlccc',['ID','First minus second','Cost difference','Width','Equiv.'],rows,'Width denotes attainment of the predeclared total-width target 1/256. Equiv. denotes containment in the separately declared band [-1/256,1/256]. An interval can establish a strict sign and equivalence at a positive margin. Every listed contrast is negative; the width failure in row 3 is retained.')
    rows=[]
    for j,key in enumerate(ORDER,1):
        v=a['ledgers'][key];rows.append([j,endpoint(v['sampling'],True,7),endpoint(v['range'],True,7),r'$<1.5\!\times\!10^{-11}$',endpoint(v['width'],True,7)])
        if F(v['mean_enclosure'])>=F(15,10**12):raise AssertionError('Printed enclosure bound violated')
    table('width75','Paired width decomposition in original loss units','rrrrr',['ID','Sampling terms','Range terms','Mean enclosure','Total width'],rows,'The sum of the two sampling radii, twice the range radius, and the mean endpoint width gives the unclipped width exactly. All displayed numerical terms are rounded upward. Exact unrounded ledgers and any support-clipping reduction are deposited. Arithmetic and continuous-bin effects are included in the enclosure; sampled acquisition ambiguity is zero, not assumed globally.')
    rows=[]
    for key,label in [('support_seconds','Finite support calculation'),('independent_support_seconds','Independent support reconstruction'),('production_seconds','Production path enclosures'),('integer_seconds','Independent integer path enclosures'),('inference_seconds','Exact confidence calculation')]:rows.append([label,f"{r['times'][key]:.4f}"])
    clock=json.loads((R/'results74/clock.json').read_text());rows.append(['Through final scientific record',f"{clock['seconds_through_study_output']:.4f}"])
    p=R/'audit/QUALIFICATION_PROCESS75.json';scope='The current full process clock was not available in this local preview.'
    if p.exists():
        proc=json.loads(p.read_text());rows.append(['Complete process, startup to shutdown',f"{proc['complete_process_seconds']:.4f}"]);scope='The complete process includes startup, shutdown and final durable scientific records.'
    rows.extend([['Support cell-pair checks','206,080'],['Production policy paths','655,360'],['Independent policy paths','655,360'],['Independent exact point/face checks','105']])
    table('work75','Qualification resource account','lr',['Operation or count','Seconds or count'],rows,scope+' The phase clocks do not exhaust the process: loading, identity checks, comparison, compression and serialization are included in the enclosing clock. Historical construction and later publication replay clocks are separate. These are one execution\'s timings, not population speed rankings.')
    out={'source':r['file_sha256'],'exact_inference':inf,'exact_width_and_adoption_ledgers':a['ledgers'],'gain_intervals':a['gains']}
    (R/'tables/tables75.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
