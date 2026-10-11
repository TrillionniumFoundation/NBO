"""R73 tables derived from frozen services and independently replayed bounds."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext,ROUND_CEILING
import json
R=Path(__file__).resolve().parents[1]

def read(p):return json.loads(p.read_text())
def upper(x,d=5):
    q=F(x)
    with localcontext() as ctx:
        ctx.prec=70
        z=Decimal(q.numerator)/Decimal(q.denominator)
        return format(z.quantize(Decimal(10)**(-d),rounding=ROUND_CEILING),'f')
def table(name,title,label,headers,rows,note,cols):
    text='\\begin{table}[htbp]\n\\centering\n\\caption{'+title+'}\\label{'+label+'}\n{\\small\\setlength{\\tabcolsep}{4pt}\n\\begin{tabular}{'+cols+'}\n\\hline\n'
    text+=' & '.join(headers)+r' \\'+'\n\\hline\n'
    text+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
    text+='\n\\hline\n\\end{tabular}}\n\\par\\smallskip\n{\\footnotesize '+note+'}\n\\end{table}\n'
    if any(ord(c)<32 and c not in '\n\r\t' for c in text):raise AssertionError('LaTeX control character')
    p=R/'tables'/(name+'.tex');p.parent.mkdir(exist_ok=True);p.write_text(text)
def main():
    audit=read(R/'audit/INDEPENDENT73.json');assert audit['status']=='passed'
    primary=[];stages=[];work=[];exact=[]
    for s in audit['summary']:
        n=s['n'];kind=s['basis'];name='ReLU' if kind=='relu' else 'Bernstein'
        obj=read(R/'results73'/f'{kind}-n{n}/service.json')
        gap=max(F(x['dual_gap']) for x in s['stages'])
        primary.append([n,name,upper(s['omega']),upper(s['regret_upper']),upper(gap,9)])
        for stage in s['stages']:
            t=stage['date'];W=F(stage['qualified_range']);Wls=F(stage['label_loss_range'])
            stages.append([n,name,t,upper(W),upper(Wls),upper(stage['dual_gap'],9)])
            exact.append(dict(n=n,basis=kind,date=t,qualified_range=str(W),label_loss_range=str(Wls),reduction=str(1-W/Wls)))
        work.append([n,name,obj['exact_action_evaluations'],obj['expected_feature_evaluations'],f"{s['service_seconds']:.3f}",0])
    table('qualification73','Attained continuation qualification in the original investment economy','tab:qualification73',
          ['$n$','Basis',r'$\Omega_h$ upper','Regret upper','Max. dual gap'],primary,
          'Each row is one predeclared, complete two-date construction. Bounds are rounded upward; the exact fractions and dates are retained. Regret upper denotes the proved original-optimum account, not an estimated loss or an attained economic equivalence margin. The maximum dual gap concerns only the declared fixed-feature, fixed-future readout objectives.','rlrrr')
    table('readouts73','Every attained readout and its fixed-label least-squares ablation','tab:readouts73',
          ['$n$','Basis','Date',r'$\mathcal W$ upper','LS bound upper','Dual gap'],stages,
          'LS is bounded least squares on the identical features and exact fixed-future interval midpoints. Its bound is evaluated by the same residual-qualification formula. It is not a separately propagated controller. The primal and dual calculations are exact rational checks, independently reconstructed without relying on the optimizer status.','rlrrrr')
    table('work73','Complete new construction work and observation scope','tab:work73',
          ['$n$','Basis','Action values','Feature means','Seconds','Cost rows'],work,
          'Action values include continuous-action covering and whole-cell feasible proposals at both dates. Feature means count evaluations for the fitted future, not terminal formulas. Seconds include both fits, qualification, matched least-squares ablations and the service output; the independent checker has a separate clock. There are no recursive optimal-value queries and no new independent policy-cost observations. Single-service times are descriptive.','rlrrrr')
    summary=dict(status='passed',services=4,stage_readouts=8,exact_stage_comparison=exact,
                 maximum_exact_dual_gap=str(max(F(x['dual_gap']) for s in audit['summary'] for x in s['stages'])),
                 all_qualified_bounds_strictly_below_matched_ls=all(F(x['reduction'])>0 for x in exact),
                 minimum_fractional_bound_reduction=str(min(F(x['reduction']) for x in exact)),
                 maximum_fractional_bound_reduction=str(max(F(x['reduction']) for x in exact)),
                 new_independent_policy_cost_rows=0)
    (R/'audit/TABLE_SUMMARY73.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
