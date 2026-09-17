"""Generate manuscript tables exclusively from executed R8 evidence."""
from pathlib import Path
import json
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'replication/r8/output';P=ROOT/'revisions/2026-09-17-r8-full-response/paper'
def read(name):return json.loads((OUT/name).read_text())
def table(name,caption,label,cols,header,rows,notes=''):
    text='\\begin{table}[htbp]\n\\centering\n\\caption{'+caption+'}\\label{'+label+'}\n\\small\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+header+r' \\'+'\n\\midrule\n'+'\n'.join(r+r' \\' for r in rows)+'\n\\bottomrule\n\\end{tabular}\n'
    if notes:text+='\\par\\vspace{3pt}\\begin{minipage}{0.96\\textwidth}\\footnotesize '+notes+'\\end{minipage}\n'
    (P/name).write_text(text+'\\end{table}\n')
def sci(x):
    if x==0:return '$0$'
    s=f'{x:.4e}';v,e=s.split('e');return '$'+v+r'\times10^{'+str(int(e))+'}$'
def run():
    result=read('decision_contest.json');rows=[]
    for r in result['rows']:
        rows.append(' & '.join([r['method'].capitalize(),'Full' if r['lower_bank']=='full_menu' else 'Mesh only',sci(r['bounds']['adjusted'][0]),sci(r['bounds']['fixed'][1]),f"{r['upper_seconds']:.2f}",f"{r['total_seconds']:.2f}"]))
    table('table_r8_contest.tex','A common-target economic decision certificate','tab:r8_contest','llrrrr',r'Upper & Lower bank & Lower $\Delta^{\rm adj}$ & Upper $\Delta^0$ & Upper sec. & Total sec.',rows,r'The target is the original 1,568-action economy on $[0,0.25]\times[0.4,0.45]$. Every arm is charged for kernel and proposal loading, full-menu upper-anchor optimization, feasible-policy evaluation, the arithmetic audit, and independent replay. The mesh-only bank additionally pays for its own lower-policy construction. Common setup is measured once and charged identically; these are serial single-pass measurements, not independent-machine medians. The per-class arithmetic allowance is $10^{-7}$.')
    spatial=[read(f'spatial_{n}.json') for n in (49,97,145)];rows=[]
    for s in spatial:
        for menu in ('common_1565','full_prolonged_1568'):
            r=next(r for r in s['rows'] if r['menu']==menu and r['lambda_']==.25 and r['d']==.45)
            rows.append(' & '.join([str(s['nx']),'Common' if menu=='common_1565' else 'Full',sci(r['delta_fixed']),sci(r['delta_adjusted']),sci(r['relative_option'])]))
    table('table_r8_spatial.tex','The original decision corner under wealth-lottery perturbations','tab:r8_spatial','rlrrr',r'Wealth nodes & Menu & $\Delta^0$ & $\Delta^{\rm adj}$ & Relative option',rows,r'All rows retain 33 preference tiers, eight dates, and $(\lambda,d)=(0.25,0.45)$. Common uses the identical 1,565-action union. Full also uses the three unchanged proposals at original nodes and their specified wealth interpolation at new nodes. Both classes and both adjustment regimes are reoptimized. The original region is not silently replaced by a favorable subset.')
    rows=[]
    for s in spatial:
        for t in (0.,.125,.25):
            pairs=[next(r for r in s['frontiers'] if r['lambda_']==t and r['adjustment']==a)['bracket'] for a in (True,False)]
            rows.append(' & '.join([str(s['nx']),f'{t:g}']+['$['+f'{p[0]:.6f}, {p[1]:.6f}'+']$' for p in pairs]))
    table('table_r8_frontiers.tex','Local indifference brackets with the calendar held fixed','tab:r8_frontiers','rrrr',r'Wealth nodes & $\lambda$ & Adjusted contract bracket & No-adjustment bracket',rows,r'All brackets use the full prolonged menu. Bisection begins on $[0.2,0.6]$ and retains every evaluated difference. Opposite signs and continuity locate a crossing; global uniqueness is not inferred. Changing the wealth lottery shifts both boundaries without changing the one-eighth-year commitment interval.')
    rows=[]
    for n in (49,97,145):
        d=read(f'spatial_nested_certificate_{n}.json')
        assert d['region']==[0.,.125,.4,.425]
        assert all(r['signs_certified'] for r in d['rows'])
        r=d['rows'][0];rows.append(f"{n} & {sci(r['bounds']['adjusted'][0])} & {sci(r['bounds']['fixed'][1])} & Yes")
    table('table_r8_nested.tex','A common nested decision region across three settlement protocols','tab:r8_nested','rrrr',r'Wealth nodes & Lower $\Delta^{\rm adj}$ & Upper $\Delta^0$ & Both signs certified',rows,r'The same closed region is $[0,0.125]\times[0.4,0.425]$. Bounds shown use the full-menu bank and corrected chord. Count and mesh-only lower-bank checks are also retained. This is a continuum certificate in $(\lambda,d)$ for each of three specified finite protocols, not a continuum claim over every wealth grid or the limiting diffusion. The region was selected after inspecting the earlier robustness results; it was not preregistered.')
    mechanisms=read('mechanisms.json');rows=[]
    selections=[('Baseline','baseline'),(r'Tilt $a=-0.25$','cardinal_tilt_-0.25'),(r'Tilt $a=0.25$','cardinal_tilt_0.25'),(r'Tilt $a=1$','cardinal_tilt_1'),(r'Normalization $s=0$','normalization_scale_0'),(r'Normalization $s=0.5$','normalization_scale_0.5'),(r'Normalization $s=1.5$','normalization_scale_1.5'),(r'Liquidation $z=0$','settlement_scale_0'),(r'Liquidation $z=2$','settlement_scale_2'),('Zero-covariance law','zero_covariance_law')]
    for label,name in selections:
        r=next(x for x in mechanisms['rows'] if x['intervention']==name and x['lambda_']==.125 and x['d']==.425)
        rows.append(label+' & '+' & '.join(f'{r[k]*1e4:.4f}' for k in ('delta_adjusted','delta_fixed','relative_option')))
    table('table_r8_mechanisms.tex','Dynamic mechanisms at the original region center','tab:r8_mechanisms','lrrr',r'Intervention & $10^4\Delta^{\rm adj}$ & $10^4\Delta^0$ & $10^4$ relative option',rows,r'Except for the named intervention, parameters are the original $(\lambda,d,k)=(0.125,0.425,2)$. Every entry reoptimizes both risk classes in both adjustment regimes. The normalization multiplier changes $b_0(u)=1/(1-u)$, not marginal consumption utility. Values shown as zero at $s=0$ are numerically negligible, not an asserted exact zero theorem. These model counterfactuals are not empirically identified causal effects.')
    r=next(x for x in mechanisms['rows'] if x['intervention']=='baseline' and x['lambda_']==.125 and x['d']==.425)
    features=np.array(r['relative_option_features'])*[1,1,0,.425,-2,1]
    rows=[name+' & '+sci(float(v)) for name,v in zip(['Consumption exposure','Cardinal preference-state payoff','Tilt exposure at baseline','Operating duration','Adjustment effort','Liquidation payoff'],features)]
    table('table_r8_features.tex','Optimized-moment accounting for the relative adjustment option','tab:r8_features','lr','Component & Contribution in baseline utility units',rows,r'The sum is the baseline relative option. Each moment is evaluated at its own class--regime optimizer. This accounting does not assign invariant causal shares; policy changes and primitive interactions are reported separately through reoptimization.')
    print('Rendered seven R8 evidence tables from executed JSON.')
if __name__=='__main__':run()
