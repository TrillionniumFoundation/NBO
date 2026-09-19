"""Deterministic tables from deposited scientific records; --check is read-only."""
from __future__ import annotations
import json,argparse,hashlib
from pathlib import Path
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PAPER=ROOT/'revisions/2026-09-19-r14-referee-response/paper'
def read(p):return json.loads((ROOT/p).read_text())
def dec(x,n=7,upper=False):
    d=Decimal.from_float(float(x)).quantize(Decimal(1).scaleb(-n),rounding=ROUND_CEILING if upper else ROUND_FLOOR);return f'{d:.{n}f}'
def sci(x):return ('%.3g'%x).replace('e-','\\times10^{-').replace('e+','\\times10^{')+'}' if 'e' in ('%.3g'%x) else '%.3g'%x
def reg(x):return 'Adjustment' if x else 'No adjustment'
def offer(f,m,s):return f'${f:.2f},{m},'+('+' if s=='positive' else '-')+'$'
def table(label,caption,cols,header,rows,note,size='\\footnotesize'):
    return '\\begin{table}[t]\n\\caption{'+caption+'}\\label{tab:'+label+'}\n\\centering\n'+size+'\n\\begin{tabular}{@{}'+cols+'@{}}\n\\toprule\n'+header+' \\\\\n\\midrule\n'+'\n'.join(r+' \\\\' for r in rows)+'\n\\bottomrule\n\\end{tabular}\n\\par\\smallskip\\begin{minipage}{\\linewidth}\\footnotesize '+note+'\\end{minipage}\n\\end{table}\n'
def outputs():
    ref=read('replication/r13/extensions/refinement.json');cont=read('replication/r14/output/continuum_certificate.json');econ=read('replication/r14/output/economic_extensions.json');prop=read('replication/r13/extensions/proposals.json');arith=read('replication/r13/output/arithmetic.json');stress=read('replication/r13/extensions/stress.json');broad=read('replication/r13/output/broader.json');out={}
    target='Target: canonical manifest \\texttt{54adb353c5b85210d} (full hash in the release manifest). '
    rows=[]
    for r in ref['nested_menu_choices']:
        rv=r['binding_rival'].split('.');# IDs contain decimal dots; use row lookup instead.
        rr=next(x for x in ref['rows'] if x['id']==r['binding_rival'])
        rows.append(f"{r['fee_step']:.2f} & {reg(r['adjustment'])} & {offer(r['fee'],r['term'],r['sign'])} & {dec(r['profit_interval'][0])} & {offer(rr['fee'],rr['term'],rr['sign'])} & {dec(r['margin'],8)}")
    out['table_menus.tex']=table('menus','Nested Enforcement Menus','rlcrcr','Step & Regime & $(F,m,\\sigma)$ & Surplus lower & Rival & Margin',rows,target+'Exact responses; value allowance $10^{-7}$ and support allowance $10^{-9}$. Lower bounds and margins are rounded down. Each margin compares the candidate lower bound against every other offer upper bound and nonprocurement.')
    rows=[];terms=[]
    for r in cont['results']:
        i=r['incumbent'];other=max(c['upper'] for c in r['leaves'] if c['term']!=i['term'])
        rows.append(f"{reg(r['adjustment'])} & {i['F']:.8f} & {i['term']} & {dec(i['lower'],9)} & {dec(r['global_upper'],9,True)} & {dec(r['regret_upper'],9,True)}")
        for m in range(1,9):terms.append(f"{reg(r['adjustment'])} & {m} & {dec(max(c['upper'] for c in r['leaves'] if c['term']==m),9,True)} & {dec(i['lower']-max(c['upper'] for c in r['leaves'] if c['term']==m),9)}")
    fees='; '.join(reg(r['adjustment'])+': $F='+repr(r['incumbent']['F'])+'$, $q='+dec(r['incumbent']['grant'],12,True)+'$' for r in cont['results'])
    out['table_continuous.tex']=table('continuous','Continuous-Fee Procurement','lrrrrr','Regime & Fee & Term & Surplus lower & Global upper & Regret upper',rows,target+'Both mandates, all eight terms, and every $F\\in[0,1]$ are covered; $E=F$ is derived from the capacity theorem. Behavioral tolerance is $\\eta=0$. Regret and upper bounds are rounded up. Exact input fees and outward grants: '+fees+'.')
    out['table_term_bounds.tex']=table('termbounds','Continuous-Fee Upper Bounds by Compulsory Term','lrrr','Regime & Term & Upper surplus & Incumbent minus upper',terms,target+'Each upper bound covers both mandates and the entire fee interval for its term. A negative same-term difference is the remaining regret bound, not a failure of term identification.')
    rows=[]
    for c in econ['joint_oracle']['cases']:
        a,b=[x['dual']['certified_upper'] for x in c['runs']];rows.append(f"{reg(c['adjustment'])} & {'+' if c['sign']=='positive' else '$-$'} & {c['eta']:.4f} & {dec(a,6,True)} & {dec(b,6,True)} & {dec(c['upper_reduction'],6)}")
    out['table_joint.tex']=table('joint','Joint Queries Bound Duration and Fee Receipts','lcrrrr','Regime & Mandate & $\\eta$ & Coordinate upper & Joint upper & Reduction',rows,target+'The objective is $A+FH$. Adjustment uses $(m,F)=(2,0.625)$ and no adjustment $(4,0.525)$. The coordinate oracle uses $h=0.02$ and five queries; the joint oracle adds $(h,Fh)$ and its negative. Query error is $10^{-10}$. Bounds concern the same policy feature vector, not independent coordinate selections.')
    labels={'baseline':'Baseline','fee_to_purchaser':'All fees to purchaser','half_fee_to_purchaser':'Half fees to purchaser','capacity_paid_directly':'Capacity paid by purchaser','capacity_cost_shared':'Capacity cost shared','lower_capacity_efficiency':'Efficiency $0.8$','higher_capacity_efficiency':'Efficiency $1.2$','low_capacity_cost':'Capacity coefficient $0.01$','high_capacity_cost':'Capacity coefficient $0.04$','cubic_capacity_cost':'Cubic capacity cost','quadratic_term_cost':'Quadratic term cost','quality_premium':'Quality premium $+0.05$','quality_penalty':'Quality premium $-0.05$','fee_and_quality':'Fees and quality premium','higher_outside_option':'Outside value $+0.05$','lower_outside_option':'Outside value $-0.05$','low_price':'Service price $0.9$','high_price':'Service price $1.1$'}
    rows=[]
    for case in ref['buyer_cases']:
        pair=[next(x for x in ref['counterfactuals'] if x['case']==case['name'] and x['adjustment']==adj) for adj in (True,False)]
        rows.append(labels[case['name']]+' & '+' & '.join(offer(x['fee'],x['term'],x['sign'])+(' $\\dagger$' if not x['certified'] else '')+' & '+dec(x['margin'],7) for x in pair))
    out['table_institutions.tex']=table('institutions','Institutional Counterfactuals in the Same Settlement Economy','lcrcr','Institution & Adjusted offer & Margin & Fixed offer & Margin',rows,target+'All rows use the 0.05 fee menu and exact-response graph supports. Offers are $(F,m,\\sigma)$. A dagger denotes an unresolved strict ordering, not a certified winner. Capacity is $F/\\zeta$, the charge ceiling remains one, and participation is evaluated with its positive part. These are finite-menu sensitivities; they are not continuous-fee claims.')
    rr=econ['mechanisms']['rows'];rows=[]
    for field,label in [('local','Current-gain difference'),('future','Future signed exposure'),('replacement','Financial replacement'),('option','Total option difference')]:
        vals=[r['difference'][field] for r in rr];rows.append(f"{label} & {sum(x>2e-9 for x in vals)} & {sum(x < -2e-9 for x in vals)} & {sum(abs(x)<=2e-9 for x in vals)} & {dec(min(vals),7)} & {dec(max(vals),7,True)}")
    out['table_mechanism.tex']=table('mechanism','Adjustment-Opportunity Map','lrrrrr','Component & Positive & Negative & Near zero & Minimum & Maximum',rows,target+'All 54 combinations of three laws, three benefits, three fees, and two terms are retained. Counts use a reporting tolerance of $2\\times10^{-9}$; full signed intervals and values are deposited. The map is not a proof of a sign between grid points.')
    rows=[]
    for f in prop['fits']:
        for method,label in [('neural','Neural'),('polynomial','Polynomial'),('nearest_anchor','Nearest')]:
            rr=[r for r in prop['rows'] if r['adjustment']==f['adjustment'] and r['method']==method];gap=max(max(r['gaps'].values()) for r in rr);train=f.get(method+'_training_seconds',0.);nbytes=f[{'neural':'neural_parameter_bytes','polynomial':'polynomial_parameter_bytes','nearest_anchor':'nearest_anchor_bytes'}[method]];online=max(r['online_certified_seconds'] for r in rr)
            rows.append(f"{reg(f['adjustment'])} & {label} & {f['teacher_seconds']:.3f} & {train:.3f} & {online:.3f} & ${sci(gap)}$ & {nbytes/1024:.1f}")
    out['table_proposals.tex']=table('proposals','Proposal Costs and Verified Policy Gaps','llrrrrr','Regime & Proposal & Teacher & Fit & Online max. & Gap max. & KiB',rows,target+'Seconds are from the completed R13 execution, not a timing rerun in R14. Online work includes proposal, policy evaluation, exact-DP upper reference, and independent verification. Maxima cover five test laws and both mandates. KiB reports stored proposal parameters or anchor policies, not process peak memory. No fitting step is needed for nearest-anchor lookup; teacher cost remains charged. The experiment uses one target size and one recorded neural seed.')
    rows=[name.replace('_',' ').capitalize()+' & $'+sci(v)+'$' for name,v in arith['bounds'].items()]
    out['table_arithmetic.tex']=table('arithmetic','Derived Stored-Array Arithmetic Bounds','lr','Operation & Error bound',rows,target+'All rows and the first-date operator are included. These values bound arithmetic under the stated operation model, not the model-to-array approximation. The full rational bound, row-mass envelopes, and operation counts are deposited.')
    rows=[]
    for r in broad['rows']:
        for meth in ('chord','count'):
            rows.append(f"{reg(r['adjustment'])} & $[{r['law'][0]:g},{r['law'][1]:g}]$ & {meth.capitalize()} & ${sci(r['per_value_uniform_gap'][meth])}$ & {r['matched_component_total_seconds'][meth]:.3f}")
    lift=stress['standard_baseline'];items=lift if isinstance(lift,list) else lift.get('rows',[])
    lifting_rows=[]
    for r in items:
        lifting_rows.append(f"{reg(r['adjustment'])} & {r['cells']} & {r['feasible_policy_coefficients']} & ${sci(r['uniform_value_gap'])}$ & {r['wall_seconds']:.3f}")
    out['table_lifting.tex']=table('lifting','Rectangular Parameter-Lifting Control','lrrrr','Regime & Cells & Lower coefficients & Uniform gap & Total seconds',lifting_rows,target+'Every row covers the full law interval $[0,1]$. The number of feasible lower-policy coefficients is reported explicitly. Timings include the recorded relaxation and matching lower-bound calculation; this is an in-repository implementation of the standard algorithm, not an external-package performance claim.')
    out['table_computational.tex']=table('computational','Changing-Law Certificates with Matched Components','lllrr','Regime & Law interval & Bound & Uniform gap & Total seconds',rows,target+'Both methods are charged their endpoint solves, common feasible-policy lower bank, and own upper calculation. Larger law intervals are retained. The rectangular-lifting execution is recorded separately in the stress file and uses this repository\'s implementation, not an external solver package.')
    out['numbers.tex']='% Generated by replication/r14/build_tables.py; do not hand edit.\n\\newcommand{\\RfourteenTarget}{54adb353c5b85210dca143aa7af44fb0b64023a6415be341cdb45e0953b0141d}\n'
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args();out=outputs()
    for name,text in out.items():
        path=PAPER/name
        if args.check:
            if not path.exists() or path.read_text()!=text:raise ValueError('table differs from deposited science: '+name)
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
    print(('CHECKED' if args.check else 'WROTE'),len(out),'table/number files')
if __name__=='__main__':main()
