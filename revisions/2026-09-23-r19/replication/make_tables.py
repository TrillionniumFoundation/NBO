"""Render manuscript tables only from materialized numerical records."""
from pathlib import Path
from decimal import Decimal,ROUND_CEILING,ROUND_FLOOR
import json,numpy as np
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'revisions/2026-09-23-r19';DATA=R/'results';OUT=R/'paper/tables'
def read(p):return json.loads((DATA/p).read_text())
def up(x,n=9):return format(Decimal.from_float(float(x)).quantize(Decimal(10)**-n,rounding=ROUND_CEILING),'f')
def down(x,n=6):return format(Decimal.from_float(float(x)).quantize(Decimal(10)**-n,rounding=ROUND_FLOOR),'f')
def tab(name,spec,header,rows,caption,label,note=''):
    OUT.mkdir(parents=True,exist_ok=True)
    text='\\begin{table}[htbp]\n\\centering\\small\n\\caption{'+caption+'}\\label{'+label+'}\n\\begin{tabular}{'+spec+'}\\toprule\n'+header+'\\\\\n\\midrule\n'
    text+='\n'.join(' & '.join(map(str,r))+'\\\\' for r in rows)+'\n\\bottomrule\n\\end{tabular}\n'
    if note:text+='\\par\\smallskip\\begin{minipage}{.98\\textwidth}\\footnotesize '+note+'\\end{minipage}\n'
    text+='\\end{table}\n';(OUT/(name+'.tex')).write_text(text)
def main():
    rows=read('policy_sensitive/results.json');g=read('policy_sensitive/uniform_policy_gain.json');u=read('policy_sensitive/uniform_state_regret.json');t=read('policy_sensitive/continuation_value_traces.json');b=read('policy_sensitive/classical_frontier.json');war=read('warm_frontier/summary.json');fa=read('attribution/factorial.json');tr=read('attribution/trace_trajectories.json');it=read('attribution/trace_interventions.json');cl=read('attribution/classical_signed.json')
    finals=[r for r in rows if r['step']==800]
    macros={'NineteenBest':up(min(r['regret_upper'] for r in finals)),'NineteenWorst':up(max(r['regret_upper'] for r in finals)),
      'NineteenK':up(max(r['uniform_K_regret_upper'] for r in u)),'NineteenGain':down(min(r['uniform_payoff_gain_interval'][0] for r in g)),
      'NineteenTrace':down(min(r['uniform_u_segment_trace_excess_lower'] for r in t)),
      'NineteenClassicalLoss':up(max(r['uniform_classical_minus_neural_interval'][1] for r in g)),
      'NineteenUpper':up(read('policy_sensitive/upper_comparator.json')['optimal_upper'])}
    (R/'paper/result_macros.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+v+'}' for k,v in macros.items())+'\n')
    tab('neural_values','rrrrrrr','Seed & $B_0$ & $B_{50}$ & $B_{200}$ & $B_{800}$ & $\\inf_K\\Delta J$ & $B_K$',
        [[s]+[up(next(r['regret_upper'] for r in rows if r['seed']==s and r['step']==k),6) for k in [0,50,200,800]]+
        [down(next(r['uniform_payoff_gain_interval'][0] for r in g if r['seed']==s),6),up(next(r['uniform_K_regret_upper'] for r in u if r['seed']==s),6)] for s in range(19100,19105)],
        'New neural policies: policy-sensitive progress and optimal comparison','tab:r19values',
        '$B_k$ is the original-economy regret upper bound at $(0,2,1.25)$, adjustment price 2, after $k$ Adam updates. The last two columns are uniform over $K=[1.98,2.02]\\times[1.24,1.26]$, at time zero. All upper bounds are rounded upward and gain lower bounds downward. These policies are neural-generated time controls with an initial-wealth budget map; they are not the full-state feedback benchmark.')
    frows=[]
    for s in range(17100,17110):
        rr=[r for r in fa if r['seed']==s]
        frows.append([s]+[f"{next(r['total'] for r in rr if r['actor_step']==a and r['critic_step']==v):.6f}" for a,v in [(0,0),(400,0),(0,400),(400,400)]]+[up(next(r['negative_component_interval'][1] for r in rr if r['actor_step']==400 and r['critic_step']==400),1)])
    tab('factorial','rrrrrr','Seed & $A_0,C_0$ & $A_1,C_0$ & $A_0,C_1$ & $A_1,C_1$ & Final $B^-$',frows,
        'Full-domain actor--critic interchange: all ten frozen feedback runs','tab:r19factorial',
        'Entries are complete time-zero regret bounds on the original spatial domain, not policy values. The final positive component equals the total in every row; the final negative component is zero. This table audits the earlier full-state experiment and is not relabeled as new training.')
    tab('trace_intervention','rrrrr','Seed & Bias lift & Trace excess & $B^+$ & $B^-$',
        [[r['seed'],f"{r['bias_lift']:.5f}",down(r['trace_excess'][0],6),up(r['positive_component_interval'][1],6),up(r['negative_component_interval'][1],6)] for r in it],
        'A continuation-trace constraint is necessary, not sufficient','tab:r19intervention',
        'Only the final critic bias changes; actors and all other weights remain fixed. Each lifted critic satisfies the directed point-trace constraint. The recomputed global bound worsens, so the intervention is not described as a successful global witness solve.')
    # Per-seed end-to-end proposal/evaluation costs, conditional on shared upper witness.
    f=[]
    for s in range(19100,19105):
        seq=sorted([r for r in rows if r['seed']==s],key=lambda r:r['step']);hit=next(r for r in seq if r['target_0.01']);v=sum(r['verification_seconds'] for r in seq if r['step']<=hit['step'])
        f.append([str(s),hit['step'],f"{hit['generation_seconds']:.3f}",f'{v:.3f}',f"{hit['generation_seconds']+v:.3f}",up(hit['regret_upper'],6)])
    for r in b:f.append([f"SLSQP-{r['slabs']}",'--',f"{r['generation_seconds']:.3f}",f"{r['verification_seconds']:.3f}",f"{r['generation_seconds']+r['verification_seconds']:.3f}",up(r['regret_upper'],6)])
    tab('matched_economy','lrrrrr','Generator & Updates & Gen. s & Eval. s & Sum s & Bound',f,
        'Matched reference-state accuracy, with a shared independently certified upper comparator','tab:r19frontier',
        'Neural evaluation cost includes all retained checkpoint checks through first attainment of $.01$; SLSQP has one final check. Generation includes neural compilation. Costs are conditional on the shared fixed upper comparator. Its historical fitting and verification costs are reported separately in the ledger, not represented as newly executed or silently free. All candidates target the original stopped payoff. SLSQP time transcription is not a Markov-chain or semi-Lagrangian solver.')
    wr=[]
    for d in [8,32,128]:
        for tol in [1e-2,1e-3,1e-4,1e-6]:
            rr=[r for r in war if r['d']==d and r['tolerance']==tol]
            wr.append([d,f'$10^{{{int(np.log10(tol))}}}$',f"{np.mean([r['mean_neural_corrections'] for r in rr]):.2f}",f"{rr[0]['comparisons']['zero']['mean_corrections']:.2f}",f"{rr[0]['comparisons']['accelerated']['mean_corrections']:.2f}",
                       sum(r['comparisons']['accelerated']['queries_neural_uses_fewer_gradients'] for r in rr)])
    tab('warm_main','rrrrrr','$d$ & Target & Neural GD & Zero GD & Accelerated & Wins / 96',wr,
        'Matched directed tolerance on a new finite query distribution','tab:r19warm',
        'Mean correction counts; each method uses one gradient evaluation per correction and one final gradient evaluation. Neural means pool three frozen initializers and 32 predeclared queries. Classical means use the same 32 queries. A win means strictly fewer gradient evaluations than acceleration for the paired query; it is not a wall-time claim. Acceleration returns its independently checked search point. The set of 32 queries is not a cover of the state cube.')
    tab('classical_signed','lrrr','Candidate & $B^+$ & $B^-$ & Total',
        [[r['path'].split('/')[-2].replace('_evaluation','').replace('markov_chain','MC').replace('semi_lagrangian','SL').replace('_','-'),up(r['positive_component_interval'][1],6),up(r['negative_component_interval'][1],6),up(r['total'],6)] for r in cl],
        'Signed decomposition of unrestricted classical feedback candidates','tab:r19classical',
        'The medium-to-fine deterioration coincides with a positive policy-side term. This separates the terms in the reported bound, but by itself does not identify interpolation error, witness fit, or true policy deterioration.')
    # Long technical tables: ordinary tabular split to avoid fragile longtable floats.
    for k,part in enumerate([tr[:15],tr[15:]]):
        tab(f'traces{k}','rrrrrr','Seed & Update & Trace lower & Trace upper & Floor lower & $B^+$',
          [[r['seed'],r['step'],down(r['trace_excess'][0],6),up(r['trace_excess'][1],6),down(r['fixed_witness_floor_lower'],6),up(r['positive_component_interval'][1],6)] for r in part],
          'Continuation trace trajectories, part '+str(k+1),'tab:r19traces'+str(k),
          'All 30 accessible checkpoints are included. A fixed-witness floor is not a lower bound on actual policy regret.')
    for d in [8,32,128]:
        rr=[r for r in war if r['d']==d];w=[]
        for r in rr:
            a=r['comparisons']['accelerated'];be=a['estimated_solver_only_break_even_queries'];bf=a['estimated_full_query_break_even_queries']
            w.append([r['seed'],f'$10^{{{int(np.log10(r["tolerance"]))}}}$',f"{r['mean_neural_online_seconds']*1000:.3f}",f"{a['mean_online_seconds']*1000:.3f}",str(be) if be else '--',str(bf) if bf else '--',f"{r['finite_query_uniform_gd_corrections_neural']}/{r['finite_query_uniform_gd_corrections_zero']}"])
        tab(f'warm_details_{d}','rrrrrrr','Seed & Target & NN ms & AG ms & $Q_{\\rm solve}$ & $Q_{\\rm all}$ & GD bound N/Z',w,
          f'Online work and conditional amortization at dimension {d}','tab:r19timing'+str(d),
          'Times are mean five-repeat per-query medians. Break-even counts combine the recorded historical training time with this query execution; they are transferred-cost estimates, not matched-hardware or certified speedups. A dash means no positive measured saving. The all-cost count includes final directed checking. The last column is a proved exact-real GD correction budget using the maximum independently enclosed initial gradient over this finite query set; N and Z denote neural and zero initialization.')
    manifest={'source':'materialized R19 result records','neural_checkpoint_count':len(rows),'factorial_count':len(fa),'trace_checkpoints':len(tr),'warm_summary_rows':len(war),'macros':macros}
    (R/'paper/table_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
