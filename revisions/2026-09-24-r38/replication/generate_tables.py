"""Generate manuscript tables directly from completed ledgers, never handwritten outcomes."""
from pathlib import Path
from fractions import Fraction as F
import json,statistics,hashlib
ROOT=Path(__file__).resolve().parents[1];G=ROOT/'paper/generated';G.mkdir(parents=True,exist_ok=True)
def read(n):return json.loads((ROOT/'results'/f'{n}.json').read_text())
def f(x,d=6):return f'{float(F(str(x))):.{d}f}'
def esc(x):return str(x).replace('_',r'\_').replace('%',r'\%').replace('&',r'\&')
def table(name,caption,headers,rows,note='',long=False):
    align='l'+'r'*(len(headers)-1)
    header=' & '.join(headers)+r' \\'+'\n'
    body=''.join(' & '.join(map(str,row))+r' \\'+'\n' for row in rows)
    if long:
        text=r'{\small\setlength{\tabcolsep}{4pt}\begin{longtable}{'+align+'}\n'+r'\caption{'+caption+r'}\label{tab:'+name+r'}\\'+'\n'+r'\toprule'+'\n'+header+r'\midrule\endfirsthead'+'\n'+r'\multicolumn{'+str(len(headers))+r'}{l}{\emph{Continued}}\\\toprule'+'\n'+header+r'\midrule\endhead'+'\n'+body+r'\bottomrule\end{longtable}}'+'\n'
        if note:text+=r'\noindent\emph{Notes.} '+note+'\n'
    else:
        text=r'\begin{table}[t]\centering\small\caption{'+caption+r'}\label{tab:'+name+'}\n'+r'\begin{tabular}{'+align+'}\n'+r'\toprule'+'\n'+header+r'\midrule'+'\n'+body+r'\bottomrule\end{tabular}'+'\n'
        if note:text+=r'\par\smallskip\begin{minipage}{\linewidth}\footnotesize\emph{Notes.} '+note+r'\end{minipage}'+'\n'
        text+=r'\end{table}'+'\n'
    (G/(name+'.tex')).write_text(text)
def main():
    P=read('primary');S=read('sensitivity');M=read('multistate');L=read('local_lp');D=read('gap_study');FR=read('frontier');V=read('independent_verification');FV=read('frontier_independent_verification')
    rows=[]
    for T in (4,8,12):
        rr=[r for r in P['outcomes'] if r['T']==T]
        rows.append([T,len(rr),sum(r['exact_integrated'] for r in rr),sum(r['exact_integrated'] and F(r['upper_integral'])>0 for r in rr),sum(r['exact_pointwise'] for r in rr),f(max(F(r['gap']) for r in rr))])
    table('primary_summary','Deterministic optimality on the unchanged primary cohort',['Horizon','Cases','Exact initial','Positive exact','All-restart exact','Max. gap'],rows,'Exact initial means equality of rational uniform-initial costs. All-restart exact additionally means equality of every stored cost-to-go function. Both operating tolerances are included. The gap is a deterministic cost interval, not a randomized duality gap.')
    metrics=[('Support witness','support_floor_witness_improvement'),('Global price refinement','global_price_refinement_improvement'),('Deterministic witness','deterministic_witness_improvement'),('Feasible upper enrichment','upper_search_improvement')]
    table('gap_summary','Separate controlled improvement coordinates',['Coordinate','Strict improvements','Largest gain'],[[label,sum(F(r[key])>0 for r in D['outcomes']),f(max(F(r[key]) for r in D['outcomes']),8)] for label,key in metrics],'Each row compares identical initial distributions and installed rules within its own policy-class scope. Gains across rows are not additive. Global prices expand from eight to fifteen; the local LP study has its own zero floor.')
    table('local_summary','Continuous local restart relaxation: exact-value diagnostic',[r'$\varepsilon$',r'$\rho$','Eight-price lower','Adaptive lower','Adaptive upper'],[[f(r['epsilon'],2),r'$1/'+r['tolerance'].split('/')[1]+'$',f(r['grid_lower']),f(r['continuous_local_lower']),f(r['continuous_local_upper'])] for r in L['outcomes'] if r['witness']=='exact'],'Horizon four, frozen neural31001, zero support floor, 40-bit directed coefficients. The endpoints enclose the continuous local relaxation, not the global constrained optimum.')
    rows=[]
    for rule in ('condition','preventive','calendar'):
        rr=[r for r in S['outcomes'] if r['installed_rule']==rule]
        rows.append([rule,len(rr),sum(r['strict_saving'] for r in rr),sum(not r['strict_saving'] for r in rr),f(max(F(r['occupancy_saving']) for r in rr))])
    table('sensitivity_summary','Dynamic versus pointwise revision in designed economic scenarios',['Installed rule','Cases','Strict savings','Zero savings','Largest saving'],rows,'Both policies use identical sufficient action restrictions and their own transition occupancies. Eleven one-at-a-time specifications and two operating tolerances generate 22 cases per installed rule. These counts are not population frequencies.')
    rows=[]
    for T in (4,8,16,32):
        rr=[r for r in M['outcomes'] if r['T']==T]
        rows.append([T,str(sum(r['certified'] for r in rr if r['method']=='restart'))+'/10',str(sum(r['certified'] for r in rr if r['method']=='classical_scalarization'))+'/5',str(sum(r['certified'] for r in rr if r['method']=='pilot_raw'))+'/4'])
    table('multistate_summary','Nonlinear whole-box operating certificates',['Horizon','Restart generators','Classical portfolios','Compiled-rule pilot'],rows,'Each entry is certified/attempted. The separate operating tolerance is $1/2$. Restart and classical methods use meshes 16 through 256; the compiled-rule pilot uses meshes through 128. The two restart penalties are separate outputs, not two independent instances of one comparator.')
    rows=[]
    for T in (4,8,12):
        rr=[r for r in P['outcomes'] if r['T']==T];op=next(o for o in P['operating_solves'] if o['T']==T)
        # Kernel exact_dp uses seconds and peak pieces in its recorded stat.
        sec=op.get('seconds',op.get('exact_dp_seconds',0))
        rows.append([T,f(sec,4),f(statistics.median(sum(r[k] for k in ('necessary_lower_seconds','safe_lower_seconds','upper_portfolio_seconds')) for r in rr),4),max(r['max_lower_pieces'] for r in rr),max(r['max_bits'] for r in rr)])
    table('work_summary','Charged primary construction work and representation',['Horizon','Operating DP (s)','Median revision (s)','Max. lower pieces','Max. bits'],rows,'The operating DP is executed once per horizon. Revision time includes both exact-value and safe-witness outer bounds and the complete upper portfolio. Independent verification, support diagnostics, and supplementary studies are additional work, not omitted overhead. Timings are generated from this publication execution.')
    exact=[];rows=[]
    for i,r in enumerate(sorted(P['outcomes'],key=lambda x:(x['T'],x['proposal'],F(x['epsilon']))),1):
        label=f"{r['T']}/{r['proposal']}/{r['epsilon']}"
        exact.append({k:r[k] for k in ('T','proposal','epsilon','policy_class','objective','lower_integral','upper_integral','safe_lower_integral','gap','exact_integrated','exact_pointwise','policy_sha256','lower_sha256','raw_sha256','proof_file','proof_sha256')})
        rows.append([r['T'],esc(r['proposal']),f(r['epsilon'],2),f(r['lower_integral']),f(r['upper_integral']),f(r['gap']),'I/P' if r['exact_pointwise'] else ('I' if r['exact_integrated'] else '--')])
    table('all_primary','All 42 primary deterministic cost intervals',['$T$','Incumbent',r'$\varepsilon$','Lower','Upper','Gap','Exact'],rows,r'I denotes exact initial integrated equality; P additionally denotes all-restart function equality. Exact fractions and complete hashes are in results/primary\_exact\_values.json; no rounded equality is used.',True)
    (ROOT/'results/primary_exact_values.json').write_text(json.dumps(exact,indent=2,sort_keys=True)+'\n')
    rows=[]
    for r in S['outcomes']:
        rows.append([esc(r['specification']),r['installed_rule'],f(r['epsilon'],2),f(r['pointwise_cost']),f(r['dynamic_cost']),f(r['occupancy_saving'])])
    table('all_sensitivity','All 66 economic sensitivity outcomes',['Specification','Rule',r'$\varepsilon$','Pointwise','Dynamic','Saving'],rows,'Every displayed case passed the same-class operating check for both policies. All values are normalized discounted implementation costs; exact rational values, changed primitives, and policy hashes are in sensitivity.json and its proof objects.',True)
    rows=[]
    wm={(w['T'],w['mesh']):w for w in M['witnesses']}
    names={'restart':'R','pilot_raw':'P','classical_scalarization':'C'}
    for r in M['outcomes']:
        mode=names[r['method']]+(str(r['penalty']) if r['method']=='restart' else '')
        d=wm[(r['T'],r['mesh'])]['deterministic_lower_integral']
        rows.append([r['T'],r['mesh'],mode,'yes' if r['certified'] else 'no',f(r['all_restart_regret_bound'],4),f(d,4),f(r['revision_cost_upper'],4),f(r['seconds'],3)])
    table('all_multistate','All nonlinear candidates, including failed certificates',['$T$','$N$','Method','Pass','Regret bound','Global LB','Policy UB','Seconds'],rows,'R0/R4 are restart generators; C is the classical four-price portfolio; P is the midpoint-compiled installed-rule pilot. Global LB is the deterministic outer-class lower bound. Policy UB bounds the cost of that policy; it is an upper bound on the feasible optimum only when Pass is yes. A failed sufficient certificate does not prove policy infeasibility.',True)
    rows=[]
    for r in L['outcomes']:
        rows.append([r['witness'],f(r['epsilon'],2),r['tolerance'],f(r['grid_lower']),f(r['continuous_local_lower']),f(r['continuous_local_upper']),r['whole_cells_verified']])
    table('all_local','All adaptive local LP certificates',['Witness',r'$\varepsilon$',r'$\rho$','Grid LB','Adaptive LB','Adaptive UB','Cells'],rows,'Every accepted open cell passes exact feasibility and quadratic gap tests; stored isolated knots receive exact point-LP solutions. The floor is zero in all rows.',True)
    rows=[]
    for r in FR['outcomes']:
        rows.append([esc(r['proposal']),f(r['epsilon'],2),r['initial_state'],f(r['value']),f(r['deterministic_lower']),r['states'],r['vertices']])
    table('all_frontiers','All exact fixed-restart history-conditioned references',['Incumbent',r'$\varepsilon$','$x_0$','Randomized','Det. lower','Nodes','Vertices'],rows,'Each objective is a Dirac restart, not the uniform-initial Markov objective. Exact rational costs, all frontier nodes, and independent support checks are in the corresponding frontiers proof object.',True)
    rows=[]
    keys=[('Primary construction','primary'),('Primary independent check','independent_verification'),('Economic sensitivities','sensitivity'),('Fixed-restart frontiers','frontier'),('Frontier independent check','frontier_independent_verification'),('Adaptive local LP','local_lp'),('Nonlinear economy','multistate'),('Global support diagnostics','gap_study')]
    for label,name in keys:
        d=read(name);rows.append([label,f(d['seconds'],4)])
    table('all_work','Executed stage wall times',['Stage','Seconds'],rows,'These are complete stage process times as recorded by the ledgers, with shared operating and witness work charged in the constructing stage. The run-level ledger separately records subprocess and dependency overhead. Historical proposal training is not included and is not claimed to have been rerun.',True)
    src={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'results').glob('*.json')) if p.name!='publication_checks.json'}
    (G/'table_sources.json').write_text(json.dumps(src,indent=2,sort_keys=True)+'\n')
    print('Generated tables from completed exact ledgers',flush=True)
if __name__=='__main__':main()
