"""All R81 tables are derived from R80 observations and exact R81 transfers."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
import json,itertools
from dual81 import pair_record,encode,save
R=Path(__file__).resolve().parents[1]

def out(x,lower=False,digits=6):
    x=F(x)
    with localcontext() as ctx:
        ctx.prec=110
        value=Decimal(x.numerator)/Decimal(x.denominator)
        return format(value.quantize(Decimal(10)**(-digits),rounding=ROUND_FLOOR if lower else ROUND_CEILING),'f')
def band(pair,digits=6):return '['+out(pair[0],True,digits)+', '+out(pair[1],False,digits)+']'
def short(name):
    if name=='zero':return 'Z'
    rule,kind,n=name.split('-');return ('L' if rule=='legacy' else 'C')+('R' if kind=='relu' else 'B')+n[1:]
def put(name,text):
    if any(ord(c)<32 and c not in '\n\r\t' for c in text):raise AssertionError('Control character '+name)
    p=R/'tables'/(name+'.tex');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def table(name,title,label,headers,rows,note,columns=None):
    columns=columns or 'l'+'r'*(len(headers)-1)
    text=r'\begin{table}[htbp]'+'\n'+r'\centering'+'\n'+r'\caption{'+title+r'}\label{'+label+'}\n'+r'{\small\setlength{\tabcolsep}{3.5pt}'+'\n'+r'\begin{tabular}{'+columns+'}\n'+r'\toprule'+'\n'
    text+=' & '.join(headers)+r' \\'+'\n'+r'\midrule'+'\n'
    text+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
    text+='\n'+r'\bottomrule\end{tabular}}'+'\n'+r'\par\smallskip{\footnotesize '+note+'}\n'+r'\end{table}'+'\n'
    put(name,text)

def main():
    j=json.loads((R/'results80/cost/summary.json').read_text());t=json.loads((R/'audit/TRANSFER81.json').read_text())
    cond=j['inference']['conditional'];pairs=cond['contrasts']
    rows=[]
    for rule in ('legacy','calibrated'):
        for n in (8,16):
            a=f'{rule}-relu-n{n}';b=f'{rule}-bernstein-n{n}';r=pair_record(pairs,a,b)
            rows.append([rule.title(),n,band(r),'R' if r[1]<0 else 'B' if r[0]>0 else '--'])
    table('basis81','Basis comparison before and after qualification calibration','tab:basis81',
        ['Qualification','$n$','ReLU minus Bernstein','Lower cost'],rows,
        'All entries are simultaneous paired original-law cost intervals from the same prospective R80 family, with exact last-innovation conditional integration. Positive values favor Bernstein. Equal coefficient counts and affine-exact modulus charging do not make the two nonlinear function classes identical. The old fits are evaluated, not overwritten.','lrcc')
    rows=[]
    for basis in ('relu','bernstein'):
        for n in (8,16):
            gain=pair_record(pairs,f'legacy-{basis}-n{n}',f'calibrated-{basis}-n{n}')
            rows.append([basis.title(),n,band(gain)])
    table('calibration-gains81','Actual controller gains from calibrated qualification','tab:calibration-gains81',
        ['Basis','$n$','Legacy minus calibrated cost'],rows,
        'Each comparison retains its basis, coefficient count and bounds, robust action menus, observation resolution and original economic primitives. Both attained future fits are reconstructed under the stated qualification rule. The displayed gains are not timing estimates or claims about unrestricted neural fitting.','lrc')
    rows=[]
    for n in (8,16):
        a=cond['interactions'][f'basis-by-modulus-n{n}'];rows.append([n,band(tuple(map(F,a['interval_exact'])))])
    table('interactions81','Predeclared basis-by-qualification interactions','tab:interactions81',['$n$','Change in Bernstein-minus-ReLU cost'],rows,
        'The interaction is (calibrated Bernstein minus calibrated ReLU) minus (legacy Bernstein minus legacy ReLU). These four-term contrasts were included in the source-frozen family before the new cost rows were generated. They are not obtained by treating the four marginal estimates as independent.','rc')
    rows=[]
    for s in t['services']:
        counts=[r['certified_cells'] for r in s['sublevel_bounds']]
        allowance=s['uniform_dyadic_allowance']
        eps='--' if allowance is None else '$'+str(F(allowance).numerator)+'/'+str(F(allowance).denominator)+'$'
        rows.append([short(s['name']),s['n']**2,*counts,eps])
    table('stability81','First-date action stability of qualification sublevels','tab:stability81',
        ['Actor','Cells',r'$\epsilon=0$',r'$1/65536$',r'$1/4096$','Uniform allowance'],rows,
        'Counts use the strict inequality D greater than U plus epsilon. U is the exact objective of the attained feasible reference fit. The last column is a dyadic allowance strictly below the smallest positive switch surplus, when such a surplus is certified. A dash is unresolved, not evidence of instability. The independent verifier checks every one of the 20,480 action-switch duals.','lrrrrc')
    rows=[]
    for x in t['exact_optimizer_class_comparisons']:
        rows.append([short(x['first'])+' minus '+short(x['second']),band(tuple(map(F,x['optimizer_class_interval'])))])
    table('optimizer-classes81','Cost comparisons uniform over exact qualification minimizers','tab:optimizer-classes81',
        ['Complete optimizer classes','Original-law cost difference'],rows,
        'CB8, CR16 and CB16 have fully stable first-date covers at epsilon zero. Their terminal actors are fixed by the common terminal payoff. Consequently each stated exact-minimizer class gives the attained complete policy and inherits its interval without enlargement. This is a deterministic transfer of the same finite statistical family, not new sampling over optimizers.','lc')
    rows=[];statistics={}
    for estimator in ('cash','conditional'):
        panel=j['inference'][estimator]
        for kind in ('costs','contrasts','interactions'):
            records=list(panel[kind].values());passcount=sum(x['paired_width_target_passed'] for x in records)
            maxwidth=max(F(x['width_exact']) for x in records)
            component={c:max(F(x['width_decomposition'][c]) for x in records) for c in ('finite_support','sampling_variance','numerical')}
            rows.append([estimator.title(),{'costs':'Marginal','contrasts':'Pair','interactions':'Interaction'}[kind],len(records),out(maxwidth),out(component['finite_support']),out(component['sampling_variance']),f"{float(component['numerical']):.2e}"])
            statistics[estimator+'-'+kind]=dict(estimands=len(records),strict_signs=sum(x['sign']!='unresolved' for x in records),width_target_passed=passcount,max_width=maxwidth,max_components=component)
    table('precision81','Observed width components for the complete frozen family','tab:precision81',
        ['Estimator','Type','Count','Max width','Support','Variance','Numerical'],rows,
        'Maxima are taken within each row and need not occur in the same estimand. Support and variance are the two-sided finite-sample allowances. Numerical is the mean endpoint-enclosure width, inclusive of propagated arithmetic and bin effects. The predeclared paired width target is 1/256; marginal intervals are not governed by that paired target. Components are not counted twice.','llrrrrr')
    rows=[]
    for name,meta in sorted(j['controller_metadata'].items()):
        rule,kind,nn=name.split('-');n=int(nn[1:]);folder=R/('results73' if rule=='legacy' else 'results80/construction')/f'{kind}-n{n}'
        c=json.loads((folder/'service.json').read_text())
        rows.append([short(name),c['exact_action_evaluations'],c['expected_feature_evaluations'],f"{meta['construction_seconds']:.3f}",'Yes' if rule=='legacy' else 'No'])
    table('work81','Construction operation counts and recorded service boundaries','tab:work81',
        ['Actor','Action values','Feature values','Seconds','Label ablation'],rows,
        'Legacy clocks include a matched fixed-label loss ablation; calibrated clocks do not. Hence this table does not compare identical end-to-end timing services. All reported counts and clocks come from their original construction records. The shared cost-inference service, independent replay, barrier verification and publication work have separate clocks and are not assigned zero cost.','lrrrc')
    text=r'{\small\setlength{\tabcolsep}{4pt}'+'\n'+r'\begin{longtable}{llcr}'+'\n'+r'\caption{Every original-law cost estimand in the R80 simultaneous family}\label{tab:all-factorial81}\\'+'\n'+r'\toprule Estimator & Estimand & Interval & Width target \\\midrule'+'\n'+r'\endfirsthead'+'\n'+r'\toprule Estimator & Estimand & Interval & Width target \\\midrule'+'\n'+r'\endhead'+'\n'
    total=0
    for estimator in ('cash','conditional'):
        panel=j['inference'][estimator]
        for kind in ('costs','contrasts','interactions'):
            for key,value in sorted(panel[kind].items()):
                if kind=='costs':name=short(key);target='--'
                elif kind=='contrasts':a,b=key.split('-minus-');name=short(a)+' minus '+short(b);target='Pass' if value['paired_width_target_passed'] else 'Fail'
                else:name='Interaction '+key.split('-n')[-1];target='Pass' if value['paired_width_target_passed'] else 'Fail'
                text+=' & '.join(['Cash' if estimator=='cash' else 'Conditional',name,band(tuple(map(F,value['interval_exact']))),target])+r' \\'+'\n';total+=1
    text+=r'\bottomrule\end{longtable}}'+'\n'+r'\noindent Codes: Z is zero control; L and C denote legacy and calibrated qualification, R and B denote ReLU and Bernstein, and the final number is the acquisition resolution. Display endpoints are rounded outward. Full exact endpoints, moments, equivalence flags and both numerical implementations remain in the machine-readable records.'+'\n'
    if total!=94:raise AssertionError('Incomplete simultaneous family')
    put('all-factorial81',text)
    c=t['choice'];record=dict(status='passed',statistical_rows=j['rows'],estimands=total,precision=statistics,
        conditional_matched={f'{rule}-n{n}':pair_record(pairs,f'{rule}-relu-n{n}',f'{rule}-bernstein-n{n}') for rule in ('legacy','calibrated') for n in (8,16)},
        conditional_gains={f'{basis}-n{n}':pair_record(pairs,f'legacy-{basis}-n{n}',f'calibrated-{basis}-n{n}') for basis in ('relu','bernstein') for n in (8,16)},
        calibrated_n16_premium_region_exact=c['calibrated_n16_R_minus_B'],zero_charge_minimax_policy=c['zero_charge_minimax_policy'],
        zero_charge_regret=c['zero_charge_regret'],new_statistical_observations=0,
        class_transfers=t['exact_optimizer_class_comparisons'],tables=9)
    save(R/'audit/TABLES81.json',record);print(json.dumps(encode(record),indent=2),flush=True)
if __name__=='__main__':main()
