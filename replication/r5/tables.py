#!/usr/bin/env python3
"""Generate every R5 numerical table and prose macro from executed JSON."""
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'replication/r5/output';PAPER=ROOT/'revisions/2026-09-16-r5/paper'
def read(name):return json.loads((OUT/name).read_text())
def sci(x):
    if x==0:return '0'
    mant,exp=f'{x:.3e}'.split('e');return rf'${mant}\times10^{{{int(exp)}}}$'
def table(name,caption,label,columns,header,rows,note):
    text='\\begin{table}[t]\n\\centering\n\\caption{'+caption+'}\n\\label{'+label+'}\n\\small\n\\begin{tabular}{'+columns+'}\n\\toprule\n'+header+' \\\\\n\\midrule\n'
    text+=''.join(' & '.join(map(str,r))+' \\\\\n' for r in rows)
    text+='\\bottomrule\n\\end{tabular}\n\\par\\medskip\n\\begin{minipage}{.97\\linewidth}\n\\footnotesize '+note+'\n\\end{minipage}\n\\end{table}\n'
    (PAPER/name).write_text(text)
def main():
    c=read('contracts.json');w=read('contract_workload.json');s=read('sign_certificate.json');res=read('resource_ablation.json');g=read('persistent_game.json')['persistent'];econ=read('economic_robustness.json')
    macro=dict(NBOAnchors=str(len(c['anchors'])),NBOActions=str(c['total_action_count']),NBOCommonActions=str(c['common_action_count']),
        NBOCertificate=f"{c['uniform_certificate']:.8f}",NBORepairGain=sci(c['repaired_max_gain']),
        NBOSignLow=f"{math.floor(s['groups'][0]['right']*1e6)/1e6:.6f}",NBOSignHigh=f"{math.ceil(s['groups'][-1]['left']*1e6)/1e6:.6f}",
        NBOContractPreparation=f"{c['timing']['preparation_seconds']:.2f}",NBOContractDirect=f"{w['direct_complete_policy_seconds']:.2f}",
        NBOContractReuse=f"{w['reuse_complete_policy_seconds']:.2f}",NBOContractRatio=f"{w['reuse_only_speed_ratio']:.1f}",
        NBOContractObservedLoss=sci(w['max_observed_loss']),NBOGameGain=sci(g['best_response']['max_positive_gain']),
        NBOGameContraction=f"{g['max_best_response_product']:.6f}",NBOGameCapacityRange=f"{g['capacity_policy_range']:.6f}",
        NBOGameTimeRange=f"{g['early_date_policy_range']:.6f}",NBOActorEquality=sci(max(x['actor_cost_difference_max'] for x in res['cases'])))
    last=res['workloads'][-1];macro.update(NBOResourceBigQueries=str(last['queries']),NBOResourceBigRatio=f"{last['end_to_end_speed_ratio']:.2f}",NBOResourceBigLoss=sci(last['loss_upper_max']))
    (PAPER/'r5_numbers.tex').write_text('% Generated from executed replication/r5/output JSON; do not edit.\n'+''.join('\\newcommand{\\'+k+'}{'+v+'}\n' for k,v in macro.items()))
    table('table_r5_repair.tex','Neural-policy loss before evaluated-continuation repair','tab:r5_repair','rrrrr',
        'Seed & Feasible gain & Initial loss & Population loss & All-node loss',
        [[x['seed'],f"{x['feasible_gain_max']:.6f}",f"{x['loss_focal']:.6f}",f"{x['loss_population']:.6f}",f"{x['loss_all_dates_states']:.6f}"] for x in c['baseline']],
        'All losses are value differences in the same finite economy, relative to exhaustive backward optimization. The action menu is the union of the reference and original diagnostic meshes and three frozen neural proposals at each node. The initial state is $(2,1.25)$; the population is uniform on grid nodes in $[1.6,2.4]\\times[0.8,1.6]$. ``All-node'' includes every date and state, not only occupied states. The repaired policy has zero remaining gain in the computed backups over this menu. The published diagnostic mesh is contained in the new menu.')
    table('table_r5_contracts.tex','Operating-benefit counterfactuals','tab:r5_contracts','rrrrrrr',
        '$d$ & Value & Duration & $c_0$ & $\\theta_0$ & $\\pi_0$ & Sign value gap',
        [[f"{x['d']:.2f}",f"{x['value']:.6f}",f"{x['duration']:.6f}"]+[f'{a:.2f}' for a in x['controls']]+[f"{x['positive_minus_nonpositive']:.6f}"] for x in c['roots']],
        'Initial state $(u,X)=(2,1.25)$, $k=2$. Duration is $A^p$, not the probability of survival. The final column is the best value among nonnegative-share first actions minus the best value among nonpositive-share first actions, using the optimal finite-model continuation. A positive entry favors the positive-share group. These five direct solves are distinct from the continuum certificate, which uses interval envelopes and fixed feasible action--continuation pairs.')
    rows=[]
    for d in (4,8,16):
        r=[x for x in res['cases'] if x['d']==d]
        rows.append([d,sci(max(x['actor']['loss_upper_max'] for x in r)),sci(max(x['zero']['loss_upper_max'] for x in r)),sci(min(x['quadratic']['loss_upper_max'] for x in r))+'--'+sci(max(x['quadratic']['loss_upper_max'] for x in r)),sci(max(x['actor_cost_difference_max'] for x in r))])
    table('table_r5_resource.tex','Representation and actor-free comparisons','tab:r5_resource','rrrrr',
          '$d$ & Actor-start loss & Zero-start loss & Quadratic loss range & Actor--zero difference',rows,
          'Each dimension includes seeds 101, 202, and 303 and the same 32 initial states per seed. The first two columns give the largest certified lifetime cost-loss upper bound across those seeds. The quadratic column spans the three maximum losses of a separately trained full positive-semidefinite quadratic critic. All use the same feasible controls and full shock trees; a reference Frank--Wolfe gap below $10^{-7}$ is added to each measured cost difference. Actor and zero starts use identical frozen nonlinear critic weights.')
    table('table_r5_workload.tex','Fresh-state query workloads at a common cost tolerance','tab:r5_workload','rrrrrr',
        'Queries & Max. loss bound & Training & Query & Reference & Cost ratio',
        [[x['queries'],sci(x['loss_upper_max']),f"{x['critic_training_seconds']:.3f}",f"{x['policy_query_seconds']:.3f}",f"{x['matched_reference_seconds']:.3f}",f"{x['end_to_end_speed_ratio']:.2f}"] for x in res['workloads']],
        'Dimension four, seed 101; held-out state seed 541021, uniform on $[0,1.2]^4$. Larger workloads extend the same fresh-state sequence. Times are seconds. Query time includes zero-start convex improvement and all 64 terminal paths per initial state. Reference time is for independent nonanticipative optimization to the common $10^{-3}$ cost tolerance. The cost ratio is reference time divided by critic training plus query time. Each reported maximum policy-loss bound is below $10^{-3}$. Timings are medians of three evaluations; the separate tighter validation reference is not charged to either competing solver.')
    table('table_r5_joint.tex','Joint time, state, and action refinements','tab:r5_joint','rrrrrrr',
        'State grid & Dates & Action grid & $d$ & Value & Duration & $\\pi_0$',
        [['$'+str(x['grid'][0])+'\\times'+str(x['grid'][1])+'$',x['steps'],'$'+'\\times'.join(map(str,x['actions']))+'$',f"{x['d']:.1f}",f"{x['value']:.6f}",f"{x['duration']:.6f}",f"{x['controls'][2]:.2f}"] for x in econ['joint_refinements']],
        'All controls are reoptimized at every resolution. These refinements use the displayed meshes without the extra frozen neural proposals. The endpoint reversal survives, whereas the midpoint changes sign between the first and second resolution. This table measures sensitivity of finite economies, not a certified bound for the continuous stopped diffusion.')
    table('table_r5_effort.tex','Adjustment quantity and coefficient-weighted expenditure','tab:r5_effort','rrrr',
        '$k$ & $C^{p_k}$ & $kC^{p_k}$ & Value',
        [[f"{x['k']:.1f}",f"{x['effort']:.6f}",f"{x['weighted_cost']:.6f}",f"{x['value']:.6f}"] for x in econ['cost_effort']],
        'The complete finite problem is solved separately at each coefficient on a $25\\times37$ grid with eight dates and $9\\times9\\times13$ actions. The unweighted quantity is decreasing; the coefficient-weighted charge is not. Stopping is included in both quantities.')
    table('table_r5_actor_timing.tex','Isolated actor costs and initialization savings','tab:r5_actor_timing','rrrrrr',
        '$d$ & Seed & Actor train & Actor query & Zero query & Projected break-even',
        [[x['d'],x['seed'],f"{x['isolated_actor_training']['seconds']:.3f}",f"{x['actor']['seconds']:.4f}",f"{x['zero']['seconds']:.4f}",str(x['actor_break_even_queries_linear_batch_projection']) if x['actor_break_even_queries_linear_batch_projection'] is not None else 'None'] for x in res['cases']],
        'Seconds per 32-state complete-tree query batch. Actor training is the distillation fit alone; common target construction and critic training are not charged twice. The last column is $32\\lceil T_{\\rm actor}/(t_{\\rm zero}-t_{\\rm actor})\\rceil$ when the measured saving is positive. It is a linear fixed-batch projection, not an observed crossover. ``None'' means that actor initialization was not faster in that timing comparison. Optimizer iteration counts and separated initialization times are saved in the machine-readable results.')
    P=__import__('numpy').array(g['policies']);rows=[]
    for k1 in (0,1):
        for k2 in (0,1):rows.append([k1,k2]+[f'{P[n,0,k1,k2,z]:.6f}' for n,z in [(0,0),(0,1),(10,0),(11,0)]])
    table('table_r5_game.tex','Investment with persistent capacities','tab:r5_game','rrrrrr',
        '$K_1$ & $K_2$ & $a_{1,0}(D=1)$ & $a_{1,0}(D=1.3)$ & $a_{1,10}(D=1)$ & $a_{1,11}(D=1)$',rows,
        'Twelve investment dates and capacity survival $s=0.8$. Capacity-one probability is $sK_i+(1-sK_i)a_i$. Investment therefore depends on installed capacity and on continuation opportunities. The largest independently computed full unilateral deviation gain over all 192 date--player--state combinations is '+sci(g['best_response']['max_positive_gain'])+'.')
if __name__=='__main__':main()
