"""Generate R10 tables from full-precision certificate records, rounding outward.
The frozen external experiment and all R9 results are read, never overwritten.
"""
from __future__ import annotations
import json, math, pathlib, sys
from fractions import Fraction
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3]
REV=ROOT/'revisions/2026-09-22-r10'; OLD=ROOT/'revisions/2026-09-22-r9/results'
OUT=REV/'results'; TABLES=REV/'paper/tables'
sys.path.insert(0,str(ROOT/'revisions/2026-09-22-r9/replication'))
from bernstein import I,iv,bounds
from original_policy_certificate import minus,point

def load(p):return json.loads(p.read_text())
def display(x,n=8,upper=False):
    q=Fraction(float(x))*10**n
    z=math.ceil(q) if upper else math.floor(q)
    return f'{z/10**n:.{n}f}'
def interval(x,n=8):return '$['+display(x[0],n)+','+display(x[1],n,True)+']$'
def sub(a,b):return minus(point(a),point(b)).tolist()
def table(name,columns,header,rows):
    body='\\begin{tabular}{'+columns+'}\n\\toprule\n'+header+' \\\\\n\\midrule\n'
    body+='\n'.join(' & '.join(row)+' \\\\' for row in rows)
    body+='\n\\bottomrule\n\\end{tabular}\n'
    (TABLES/(name+'.tex')).write_text(body)

def run():
    TABLES.mkdir(parents=True,exist_ok=True)
    R=load(OLD/'restricted_dual_certificate.json')['records'][-1]['restricted_optimal_value_upper']
    RL=load(OLD/'policy_certificate_restricted.json')['records'][-1]['policy_value_interval'][0]
    values=[]; frontier=[]
    for k in [.5,2,8]:
        p=load(OUT/f'policy_certificate_k{k:g}.json'); d=load(OUT/f'flexible_dual_k{k:g}.json')
        J=p['records'][-1]['policy_value_interval']; U=d['records'][-1]['optimal_value_upper']; gap=sub(U,J[0])[1]
        access=[sub(J[0],R)[0],sub(U,RL)[1]]
        budget=p['adjustment_budget_interval']
        values.append({'k':k,'policy_value_interval':J,'optimal_value_interval':[J[0],U],
                       'regret_upper':gap,'target':.01,'target_met':gap<.01,
                       'optimal_access_welfare_interval':access,'policy_adjustment_budget_interval':budget,
                       'scope':'original stopped model; central state; polished time-control policy, unrestricted continuous-action optimum'})
        preparation=max(0,d['total_seconds']-sum(x['seconds'] for x in d['records']))
        elapsed=p['total_seconds']+preparation
        for r in d['records']:
            elapsed+=r['seconds']
            frontier.append({'k':k,'source_boxes':r['source_boxes'],'time_cells':r['time_cells'],
                'normal_cells':r['normal_cells'],'optimal_value_upper':r['optimal_value_upper'],
                'regret_upper':r['certified_regret_upper'],'verification_seconds_cumulative':elapsed,
                'meets_0_01':r['certified_regret_upper']<.01,
                'clock_scope':'policy evaluation and cumulative dual certification; excludes inherited training, fitting, imports, and setup'})
    effects=[]
    for i,j in [(0,1),(1,2),(0,2)]:
        a,b=values[i],values[j]
        z=[sub(a['optimal_value_interval'][0],b['optimal_value_interval'][1])[0],
           sub(a['optimal_value_interval'][1],b['optimal_value_interval'][0])[1]]
        w=sub(z[1],z[0])[1]
        effects.append({'cost_pair':[a['k'],b['k']],'optimal_welfare_loss_interval':z,'width_upper':w,
                        'positive':z[0]>0,'entire_effect_exceeds_interval_width':z[0]>w})
    Bmax=bounds(I('.02')*(1-iv.exp(-I('.04')))/I('.04'))[1]
    B2=[bounds((I(values[1]['optimal_value_interval'][0])-I(values[2]['optimal_value_interval'][1]))/6)[0],
        min(Bmax,bounds((I(values[0]['optimal_value_interval'][1])-I(values[1]['optimal_value_interval'][0]))/I('1.5'))[1])]
    summary={'status':'PASS' if all(v['target_met'] for v in values) else 'FAIL','economy':values,
       'restricted_optimal_value_interval':[RL,R],'cost_effects':effects,'optimal_budget_k2_interval':B2,
       'verification_frontier':frontier,'tolerance':.01,'all_three_central_targets_met':all(v['target_met'] for v in values),
       'not_claimed':['uniform state certificate','convergence of Adam','external matched-accuracy dominance','tight identification of an optimal policy surface']}
    (OUT/'scientific_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    table('original','rrrr',r'$k$ & Feasible policy payoff & Optimal-value upper & Regret upper',
          [[f"{v['k']:g}",interval(v['policy_value_interval']),display(v['optimal_value_interval'][1],8,True),display(v['regret_upper'],8,True)] for v in values])
    table('economics','rrrr',r'$k$ & Policy adjustment budget & Optimal access-value interval & Regret target',
          [[f"{v['k']:g}",interval(v['policy_adjustment_budget_interval']),interval(v['optimal_access_welfare_interval']),r'$<.01$'] for v in values])
    table('cost_effects','rrrr',r'Cost change & Optimal welfare loss & Interval width & Width below loss',
          [[f"${e['cost_pair'][0]:g}\\to{e['cost_pair'][1]:g}$",interval(e['optimal_welfare_loss_interval']),display(e['width_upper'],8,True),'Yes' if e['entire_effect_exceeds_interval_width'] else 'Sign resolved'] for e in effects])
    table('frontier','rrrrr',r'$k$ & Source boxes & Regret upper & Verification seconds & $.01$ met',
          [[f"{r['k']:g}",f"{r['source_boxes']:,}",display(r['regret_upper'],8,True),f"{r['verification_seconds_cumulative']:.2f}",'Yes' if r['meets_0_01'] else 'No'] for r in frontier])
    row2=load(OUT/'flexible_dual_k2.json')['records']
    table('error_budget','rrrrr',r'Boxes & Source remainder & Control gap & Variance allowance & Localization',
          [[f"{r['source_boxes']:,}",display(r['source_taylor_remainder_upper'],9,True),display(r['tangent_control_gap_upper'],9,True),display(r['variance_allowance_upper'],9,True),display(r['localization_upper'],9,True)] for r in row2])
    print(json.dumps({'status':summary['status'],'regrets':[v['regret_upper'] for v in values], 'cost_effects':effects,'optimal_budget_k2':B2},indent=2))
    return summary
if __name__=='__main__':run()
