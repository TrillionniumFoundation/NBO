"""Generate manuscript tables from the executed R9 deposit, with no estimates."""
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'replication/r9/output';PAPER=ROOT/'revisions/2026-09-17-r9-participation-permissions/paper'
def load(n):return json.loads((OUT/n).read_text())
def table(name,title,label,fmt,headers,rows,note):
    s='\\begin{table}[tbp]\n\\centering\\small\n\\caption{'+title+'}\n\\label{'+label+'}\n\\begin{tabular}{'+fmt+'}\n\\toprule\n'
    s+=' & '.join(headers)+r' \\'+'\n\\midrule\n'
    s+='\n'.join(' & '.join(map(str,r))+r' \\' for r in rows)+'\n\\bottomrule\n\\end{tabular}\n'
    s+='\\begin{minipage}{0.98\\textwidth}\\footnotesize\\medskip\n'+note+'\n\\end{minipage}\n\\end{table}\n'
    (PAPER/(name+'.tex')).write_text(s)
def main():
    PAPER.mkdir(parents=True,exist_ok=True);s=load('surrender.json');p=load('permissions.json');e=load('reachable_fee.json');q=load('procurement.json')
    nominal=next(r for r in s['center'] if r['min_term']==8);rows=[]
    for regime,label in [('adjusted','Adjustment'),('no_adjustment','No adjustment')]:
        for sig in ['positive','nonpositive']:
            z=nominal[regime][sig];a=z['action'];rows.append([label,'$+$' if sig=='positive' else '$-$',f"{z['value']:.9f}",*[f'{x:.1f}' for x in a]])
    table('table_r9_initial','Initial Optimizers Beside the Original Decision Certificate','tab:r9_initial','llrrrr',['Regime','Class','Value','$c$','$\\theta$','$\\pi$'],rows,r'Original center $(\lambda,d)=(0.125,0.425)$, noncancellable mandate, complete finite menu. Both the long permission $0.8$ and the short permission $0.5$ bind. Consumption is also at its upper limit; deliberate adjustment is at its upper limit when permitted. The nonpositive position is risky, and the no-adjustment regime retains stochastic preferences.')
    rows=[]
    for r in q['zero_collateral_carry_cost_rows']:
        if r['fee']==.8 or (r['fee']==0 and r['minimum_term']==1 and r['regime']=='no_adjustment'):continue
        nm='$m=8$' if r['minimum_term']==8 else f"$F={r['fee']:.2f},\\ m=1$"
        reg='Both' if r['fee']==0 and r['minimum_term']==1 else ('Adjustment' if r['regime']=='adjusted' else 'No adjustment')
        rows.append([nm,reg,f"{r['duration']:.6f}",f"{r['participation_grant']:.6f}",f"{r['break_even_service_flow']:.6f}"])
    table('table_r9_procurement','Participation and Service Procurement at the Original Center','tab:r9_procurement','llrrr',['Contract','Regime','Duration','Grant $q^*$','$b_{\\min}$'],rows,r'The agent chooses the better initial class in each regime. Grants and charges use a separate additive utility numeraire, not managed wealth. Here $C(E)=0$; for positive capacity cost add $C(E)$ to the grant and divide the added amount by duration for the change in $b_{\min}$. The principal obtains the reported flow only during operation. These are not empirical monetary compensating variations.')
    rows=[]
    for r in s['center']:
        if not ((r['min_term']==1 and r['fee'] in (0,.4,.7,.8,.85)) or (r['fee']==0 and r['min_term'] in (2,4,6,7,8))):continue
        rows.append([r['min_term'],f"{r['fee']:.2f}",f"{1e4*r['adjusted']['delta']:.4f}",f"{1e4*r['no_adjustment']['delta']:.4f}",f"{(1e4*r['relative_option'] if abs(1e4*r['relative_option'])>=.00005 else 0.):.4f}"])
    table('table_r9_surrender','Surrender Changes Both the Level and the Sign of the Relative Option','tab:r9_surrender','rrrrr',['$m$','$F$','$10^4\\Delta^{\\rm adj}$','$10^4\\Delta^0$','$10^4\\mathcal O$'],rows,r'Original center, full finite operating menu, four reoptimized class values per row. The first interval remains compulsory. $m=8$ is the original mandate and has no eligible surrender date. Absolute values are monotone in $F$ and $m$ in the required directions; the displayed differences need not be. All 19 center specifications remain in the numerical deposit.')
    rows=[]
    for m,f,g in zip(e['minimum_terms'],e['sufficient_fee_bounds'],e['all_node_sufficient_bounds']):
        rows.append([m,f'{m/8:.3f}',f'{math.ceil(f*1e6)/1e6:.6f}',f'{math.ceil(g*1e6)/1e6:.6f}'])
    table('table_r9_enforcement','Sufficient Enforcement Capacity and the Minimum Operating Term','tab:r9_enforcement','rrrr',['$m$','Term (years)','Reachable-state bound','All-node bound'],rows,r'Uniform over $(\lambda,d)\in[0,0.25]\times[0.4,0.45]$ and both adjustment regimes, on the original finite menu. Bounds are rounded upward to six decimals after the $10^{-7}$ allowance. A capacity $E$ at least the stated bound implements the original mandatory continuation values with charge $F=E$, provided $E\leq\bar E$. These are sufficient statewise bounds, not the smallest initial-state fees or an optimal contract-design solution.')
    rows=[]
    for fn,nm in [('noncancellable_certificate.json','$m=8$'),('fee_080_certificate.json','$F=0.80,\\ m=1$'),('fee_085_090_certificate.json','$F\\in[0.85,0.90],\\ m=1$')]:
        rr=load(fn)['methods'];a=rr[0];assert a['bounds']==rr[1]['bounds']
        bounds=a['bounds'];rows.append([nm,'['+', '.join(f'{1e4*x:.4f}' for x in bounds['adjusted'])+']','['+', '.join(f'{1e4*x:.4f}' for x in bounds['no_adjustment'])+']','Yes' if a['signs_certified'] else 'No'])
    table('table_r9_fee_certificate','The Original Region with a Finite Surrender Charge','tab:r9_fee_certificate','lrrc',['Contract','$10^4\\Delta^{\\rm adj}$ bound','$10^4\\Delta^0$ bound','Both signs'],rows,r'Each row uses the original rectangle $[0,0.25]\times[0.4,0.45]$, both adjustment regimes, and four law subcells. Chord and count are executed separately and give the same displayed bounds. Every unscaled difference includes $2\times10^{-7}$ arithmetic padding relative to the stored arrays. The fee interval uses a joint fee--benefit--law coefficient bound. The failed $F=0.80$ row and its adverse reoptimized corner are retained.')
    rows=[]
    for r in p['permission_roots']:
        if r['d']!=.425:continue
        a=r['adjusted'];z=r['no_adjustment'];rows.append([f"{r['lam']:.3f}",f"{a['long_switch']:.6f}",f"{z['long_switch']:.6f}",f"{a['short_switch']:.6f}",f"{z['short_switch']:.6f}"])
    table('table_r9_permissions','The Two Regime-Specific Permission Boundaries','tab:r9_permissions','rrrrr',['$\\lambda$','$L^*_{\\rm adj}$','$L^*_0$','$S^*_{\\rm adj}$','$S^*_0$'],rows,r'Here $d=0.425$, with no voluntary surrender. The $L$ roots hold $S=0.5$; the $S$ roots hold $L=0.8$. Only the first-date risky-share permission changes. Search is exact over the breakpoint reduction conditional on 121 finite consumption--adjustment pairs and feasible original proposals. Reported roots are floating-point computations, not interval enclosures or continuously optimized consumption and preference-adjustment policies.')
    rows=[]
    for lam in (0.,.125,.25):
        for L,S in ((.8,.5),(.82,.5),(.8,.51)):
            rr=[r for r in p['benefit_roots'] if r['lam']==lam and r['long']==L and r['short']==S];a=next(r for r in rr if r['adjustment']);z=next(r for r in rr if not r['adjustment'])
            assert a['duration_difference']>0 and z['duration_difference']>0
            for r in rr:assert r['initial_actions']['positive'][2]>0
            rows.append([f'{lam:.3f}',f'{L:.2f}',f'{S:.2f}',f"{a['root']:.6f}",f"{z['root']:.6f}"])
    table('table_r9_benefit_frontiers','Reoptimized Benefit Crossings under Changed Permissions','tab:r9_benefit_frontiers','rrrrr',['$\\lambda$','$L$','$S$','$d^*_{\\rm adj}$','$d^*_0$'],rows,r'No voluntary surrender. Later-date policies are reoptimized at every trial benefit on the unchanged full menu. All reported local crossings have positive optimizing duration differences. Local numerical brackets and feature values are deposited; they do not establish global uniqueness or a directed-rounding root enclosure. The original permissions and both adverse first-date extensions are shown at every inspected law probability.')
    rows=[]
    for m in range(1,9):
        rr=[r for r in q['center_statewise_thresholds'] if r['minimum_term']==m];a=next(r for r in rr if r['adjustment']);z=next(r for r in rr if not r['adjustment'])
        rows.append([m,f"{a['statewise_no_surrender_threshold']:.7f}",f"{z['statewise_no_surrender_threshold']:.7f}"])
    table('table_r9_center_capacity','Statewise No-Surrender Thresholds at the Original Center','tab:r9_center_capacity','rrr',['$m$','Adjustment','No adjustment'],rows,r'Direct evaluations of $\max_{n\geq m,\,x\in R_n}[G(x)-V_n^r(x)]_+$ at $(\lambda,d)=(0.125,0.425)$. Both use the same all-action reachable support. The initial point alone can require a smaller charge than statewise equality. These point calculations are distinct from the upward-rounded sufficient regional bounds in the main paper.')
    val=load('validation.json')
    def mathup(x):
        if x==0:return '0'
        power=math.floor(math.log10(abs(x)));mant=math.ceil(abs(x)*10**(2-power))/100
        return f'{mant:.2f}'+r'\times10^{'+str(power)+'}'
    numbers={'RnineToyReplay':val['toy']['exhaustive_error'],'RnineFullReplay':val['full']['selected_control_reconstruction_error'],'RninePolicyReplay':val['full']['polynomial_evaluation_error']}
    commands=[chr(92)+'newcommand{'+chr(92)+k+'}{'+mathup(v)+'}' for k,v in numbers.items()]
    (PAPER/'r9_numbers.tex').write_text('\n'.join(commands)+'\n')
    print('Generated 8 R9 tables and validation macros from executed JSON.')
if __name__=='__main__':main()
