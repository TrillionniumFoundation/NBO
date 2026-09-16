#!/usr/bin/env python3
"""Generate every current numerical table from executed JSON, never archival arrays."""
import argparse,json
from pathlib import Path
import numpy as np

def load(p):return json.loads(p.read_text())
def f(x,d=6):return f'{x:.{d}f}'
def e(x):return f'{x:.2e}'
def table(path,caption,label,heads,rows,note):
    spec='l'+'r'*(len(heads)-1)
    s='\\begin{table}[tbp]\n\\centering\n\\caption{'+caption+'}\n\\label{'+label+'}\n\\small\n'
    s+='\\begin{tabular}{@{}'+spec+'@{}}\n\\toprule\n'+' & '.join(heads)+r' \\'+'\n\\midrule\n'
    s+='\n'.join(' & '.join(map(str,r))+r' \\' for r in rows)+'\n\\bottomrule\n\\end{tabular}\n'
    s+='\\par\\smallskip\\begin{minipage}{\\linewidth}\\footnotesize '+note+'\\end{minipage}\n\\end{table}\n'
    path.write_text(s)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='replication/r4/output');ap.add_argument('--paper',default='revisions/2026-09-16-r4/paper');a=ap.parse_args()
    out=Path(a.out);p=Path(a.paper);p.mkdir(parents=True,exist_ok=True)
    test=load(out/'tests_results.json');refs=load(out/'reference_results.json')['reference'];analysis=load(out/'analysis_results.json')
    table(p/'table_ndu_refinement.tex','Joint State--Time Refinement of the Stopped Preference Model','tab:ndu_refine',
          ['Grid','Dates','$V_0$','$C_0$','Seconds'],
          [[f"${r['grid'][0]}\\times {r['grid'][1]}$",r['steps'],f(r['initial_value']),f(r['initial_effort']),f(r['seconds'],2)] for r in refs if r['run'] in ['ref_17_25_4_5_2','ref_33_49_8_5_2','ref_65_97_16_5_2']],
          r'Initial state $(2,1.25)$; $k=2$. All rows optimize $5\times5\times7$ consumption, adjustment, and portfolio actions. $C_0$ is discounted integrated $\theta^2/2$. These are finite-approximation values, not certified continuous-time errors.')
    rr=sorted([r for r in refs if r['grid']==[25,37] and r['counts']==[9,9,13]],key=lambda r:r['k'])
    table(p/'table_ndu_k.tex','Re-solved Preference-Adjustment Cost Panel','tab:ndu_k',
          ['$k$','$V_0$','$C_0$','$c_0$','$\\theta_0$','$\\pi_0$'],
          [[f(r['k'],1),f(r['initial_value']),f(r['initial_effort'])]+[f(x,3) for x in r['initial_policy']] for r in rr],
          r'Each row re-solves all dates and all three control coordinates on the same $25\times37$ grid, eight dates, and $9\times9\times13$ action mesh. The initial state is $(2,1.25)$. The comparison concerns cumulative effort, not a universal pointwise policy ordering.')
    nn=load(out/'neural_results.json')['neural'][0];alln=[('Pilot 101',nn)]+[(f"Safe {seed}",load(out/f'safe_results_{seed}.json')) for seed in [101,202,303]]
    cmap={r['run']:r for r in analysis['comparisons']}
    rows=[];pol=[]
    for name,r in alln:
        key='neural_policy_seed_101' if name.startswith('Pilot') else 'safe_policy_'+str(r['seed']);q=cmap[key]
        rows.append([name,f(q['initial_value_difference']),f(r['critic_vs_policy_rmse']),f(r['critic_vs_policy_max']),f(r['sampled_feasible_gain_max']),f(r.get('end_to_end_seconds',r.get('elapsed')),1)])
        pol.append([name]+[f(x,4) for x in q['policy_mae_c_theta_pi']]+[f(x,3) for x in q['policy_max_c_theta_pi']])
    table(p/'table_ndu_neural.tex','Neural Policies and Independent Evaluation in the Stopped Economy','tab:ndu_neural',
          ['Run','$V_R-J_0$','Critic RMSE','Critic max.','Gain max.','Seconds'],rows,
          r'$V_R$ is the separately solved $33\times49$, eight-date, $9\times9\times13$ reference at $(2,1.25)$. Critic errors compare the initial critic with its independently evaluated policy over the whole grid. Gain is the largest feasible one-step improvement over all interior states and dates against the evaluated continuation. The pilot has a smaller critic and training budget; it is not a matched ablation. Hard boundary discrepancies are evaluated separately in the raw record.')
    table(p/'table_ndu_policy.tex','Full-Vector Policy Discrepancies against the Matched Reference','tab:ndu_policy',
          ['Run','MAE $c$','MAE $\\theta$','MAE $\\pi$','Max. $c$','Max. $\\theta$','Max. $\\pi$'],pol,
          r'Mean absolute and maximum discrepancies include every interior common node and all eight dates. Coordinates have different economic units and are not added together or called a Hamiltonian gain. Both policies use their stated finite approximations; these are not errors against a continuous-time oracle.')
    resources=[load(out/f'resource_results_{d}_{seed}.json') for d in [4,8,16] for seed in [101,202,303]]
    rows=[]
    for d in [4,8,16]:
        group=[r for r in resources if r['d']==d]
        rows.append([d,f(max(r['cost_excess_upper_max'] for r in group),6),f(max(r['proposal_only_cost_excess_upper_max'] for r in group),5),f(np.median([r['neural_end_to_end_seconds'] for r in group]),3),f(np.median([r['matched_reference_seconds'] for r in group]),3),str(sum(r['neural_target_passed'] for r in group))+'/3'])
    table(p/'table_resource.tex','Coupled Stochastic Resource Allocation at a Common Accuracy Target','tab:resource',
          ['$d$','NBO upper loss','Proposal only','NBO sec.','Reference sec.','Passed'],rows,
          r'Loss columns are worst held-out cost-loss upper bounds across three seeds and 32 initial states per seed. Proposal only removes deployment improvement from the same fitted actor weights. Timing is the median across seeds at a $10^{-3}$ cost-loss target; NBO includes fitting and full evaluation, and the reference solves the same initial-state batch to its $10^{-3}$ gap target. A separate $10^{-7}$ reference gap is used for auditing, not for the timing comparison. The reference is a convex nonanticipative scenario tree, not a sparse grid.')
    table(p/'table_resource_all.tex','All Resource Runs and the Matched Deployment Ablation','tab:resource_all',
          ['$d$','Seed','NBO upper loss','Proposal only','Reference gap','Binding at $0$'],
          [[r['d'],r['seed'],e(r['cost_excess_upper_max']),e(r['proposal_only_cost_excess_upper_max']),e(r['reference_gap_max']),f(r['binding_frequency_by_date'][0],3)] for r in resources],
          r'Each row uses the stored 32 initial states and every one of the 64 terminal shock branches. The reference gap is the complete scenario-tree linear minimization gap at the tighter audit tolerance. Binding is the fraction of initial actions exhausting the common budget. All declared dimension--seed combinations are included.')
    table(p/'table_recursive.tex','Executed Homothetic Policy Evaluation and Improvement','tab:recursive',
          ['Model','Learned $m$','Learned $\\pi$','Policy max. error','Relative $A$ error'],
          [[name,f(test[key]['m'],8),f(test[key]['pi'],8),e(test[key]['policy_max_error']),e(test[key]['relative_value_coefficient_error'])] for name,key in [('Merton','merton'),('Epstein--Zin','epstein_zin')]],
          r'The coefficient $A=\exp(q)$ and bounded actor parameters are learned by separated updates. Analytical values are used only to compute the displayed errors. The sign condition and normalized HJB are tested separately. These runs use homothetic features rather than an unrestricted neural value class.')
    table(p/'table_temporal.tex','Sophisticated Consumption Ratios and Independent Deviations','tab:temporal',
          ['$\\beta$','$c_0/w$','$c_1/w$','$c_2/w$','$c_3/w$','Eval. residual'],
          [[f(r['beta'],1)]+[f(x,7) for x in r['ratios']]+[e(r['evaluation_residual'])] for r in test['temporal']['runs']],
          r'Four consumption dates and terminal log wealth, $\Delta=1$, $\rho=0.04$. Continuation is evaluated without multiplying by $\beta$ again. Independent bounded one-shot optimizations against these frozen continuation values give no gain exceeding $10^{-9}$ on the tested wealth levels.')
    table(p/'table_trace.tex','Independent-Batch Stochastic-Trace Losses','tab:trace',
          ['$K$','Correct mean','Population','MC s.e.','Old mean','Debiased mean'],
          [[r['k'],f(r['mean_squared_batch_residual'],5),f(r['expected_loss'],5),f(r['mc_standard_error'],5),f(r['mean_individual_squares'],5),f(r['debiased_mean'],5) if 'debiased_mean' in r else '--'] for r in test['trace']['runs']],
          r'20,000 independent Gaussian batches per row; the exact-trace squared residual is 1.5625. Correct mean averages probes before squaring; old mean averages individual squared residuals. The debiased off-diagonal statistic requires at least two probes. Its standard errors and both variance estimands are retained in the JSON record.')
    table(p/'table_lqr.tex','Structured Stochastic LQR Regression','tab:lqr',
          ['$d$','Actor coeff. error','Cost excess max.','Neural sec.','Riccati sec.'],
          [[r['d'],e(r['actor_coefficient_max_error']),e(r['evaluated_cost_excess_max']),f(r['neural_seconds'],4),f(r['baseline_seconds'],5)] for r in test['lqr']],
          r'Six periods, linear actors and quadratic feature critics, independent Riccati reference, and separate frozen-policy evaluation. Cost excess is normalized per dimension in the implementation. This structured unconstrained regression is not the main binding-resource experiment and supplies no generic neural speed advantage.')
    print('Generated',len(list(p.glob('table_*.tex'))),'tables')
if __name__=='__main__':main()
