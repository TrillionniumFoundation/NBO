"""Deterministic R8 manuscript tables. Missing evidence is a build error."""
from __future__ import annotations
import json, pathlib, statistics
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE=ROOT/'revisions/2026-09-22-r8'
R=BASE/'results'; O=BASE/'paper/tables'
def read(name): return json.loads((R/name).read_text())
def table(name,caption,label,columns,header,rows,note):
    s='\\begin{table}[htbp]\n\\centering\\small\n'
    s+=f'\\caption{{{caption}}}\\label{{{label}}}\n'
    s+='\\begin{tabular}{@{}'+columns+'@{}}\n\\toprule\n'
    s+=' & '.join(header)+' \\\\\n\\midrule\n'
    s+=''.join(' & '.join(map(str,row))+' \\\\\n' for row in rows)
    s+='\\bottomrule\n\\end{tabular}\n\\par\\smallskip\\footnotesize '+note+'\n\\end{table}\n'
    (O/(name+'.tex')).write_text(s)
def run():
    O.mkdir(parents=True,exist_ok=True)
    z=read('continuum_witnesses.json')
    table('continuum','Original-payoff continuous NDU witness bounds','r8:tab:continuum','rrrrr',
       ['$N$','Interval cells','$\\alpha$','$\\beta$','Regret upper bound'],
       [[x['n'],x['cells'],f"{x['alpha']:.6f}",f"{x['beta']:.6f}",f"{x['continuous_regret_upper_bound_t0']:.6f}"] for x in z['records']],
       'Retained raw seed-10 nodal policies, deployed as continuously reevaluated bilinear feedback on each time slab. Bounds cover the original continuous Brownian model and exact first exit using outward interval arithmetic. Both bounds exceed the .01 precision target.')
    sg=read('safeguard_results.json')
    table('safeguard','Thresholded correction of retained NDU policies','r8:tab:safeguard','rrrrrrr',
       ['$N$','Target','Raw bound','Final bound','Override (\\%)','Audits','Seconds'],
       [[int(x['tag'].split('_')[0][1:]),f"{x['target']:.2f}",f"{x['history'][0]['localized_bound']:.6f}",f"{x['history'][-1]['localized_bound']:.6f}",f"{100*x['history'][-1]['overridden_fraction']:.3f}",x['audits'],f"{x['total_audit_seconds']:.3f}"] for x in sg],
       'Float64 finite-candidate envelopes, not continuous-model certificates. Seconds include all listed audits and envelope calculations on the current worker. Each audit still enumerates the full 125-action grid plus the proposal. Historical training time is not added across different environments.')
    rows=read('mesh_results.json')
    table('mesh','One-factor NDU approximation diagnostics','r8:tab:mesh','lrrrrrr',
       ['Factor','$N$','State nodes','$n_a$','Value','Exit prob.','$h^2/\\Delta$'],
       [[x['factor'],x['config']['n'],f"${x['config']['nu']}\\times{x['config']['nx']}$",x['config']['na'],f"{x['center_value']:.6f}",f"{x['center_exit']:.6f}",f"{x['h2_over_dt']:.4f}"] for x in rows if x['factor']!='joint_cost'],
       'All entries use $k=2$ and evaluate $(u,x)=(2,1.25)$. $n_a$ is the number of nodes per action component. Four-sign quadrature and straight-segment liquidation are unchanged; these differences do not bound continuous-model error.')
    table('cost','Finer finite-action preference-adjustment comparison','r8:tab:cost','rrrrrr',
       ['$k$','Value','Budget $B$','Exit prob.','$\\theta_0$','$p_0$'],
       [[f"{x['config']['k']:g}",f"{x['center_value']:.6f}",f"{x['center_budget']:.6f}",f"{x['center_exit']:.6f}",f"{x['nearest_node_action'][1]:.4f}",f"{x['nearest_node_action'][2]:.4f}"] for x in rows if x['factor']=='joint_cost'],
       '$N=96$, a $49\\times61$ state lattice, and nine nodes per action component (729 actions). Central consumption is .8 in these rows. Values and budgets belong to the declared numerical liquidation economy, without a continuous error enclosure.')
    geo=[read(f'geometry_s{s}.json') for s in range(300,306)]
    table('geometry','All-state continuous certificate for trained NDU-geometry actors','r8:tab:geometry','rrrrrr',
       ['Seed','Regret bound','$c$ error','$\\theta$ error','$p$ error','Train (s)'],
       [[x['seed'],f"{x['certificate']['regret_upper_bound']:.8f}",f"{x['certificate']['consumption_error_upper']:.7f}",f"{x['certificate']['adjustment_error_upper']:.7f}",f"{x['certificate']['portfolio_error_upper']:.7f}",f"{x['training_seconds']:.3f}"] for x in geo],
       'All-state upper bounds use outward interval arithmetic and the same state, action, covariance, and first-exit geometry as the economic model. Only the running payoff is manufactured. Four actor parameters are trained for 4,000 steps without optimal-action labels; the critic witness is known.')
    ext=read('external_summary.json')['rows']
    assert len(ext)==2
    table('external','Paired nonconvex-control comparison at a fixed training budget','r8:tab:external','rrrrl',
       ['$d$','NBO cost','SOC cost','Difference','Paired 95\\% interval'],
       [[x['dimension'],f"{x['mean_nbo_cost']:.5f}",f"{x['mean_soc_cost']:.5f}",f"{x['paired_mean']:.5f}",f"$[{x['paired_t_95'][0]:.5f},{x['paired_t_95'][1]:.5f}]$"] for x in ext],
       'Difference is NBO minus SOC-MartNet realized cost at 128 audit steps; negative favors NBO. Each dimension has six independent training/audit seeds, 4,096 common-random-number paths per pair, and ten seconds of training per method. Student intervals describe across-seed uncertainty, not optimality loss. Maximum paired path standard errors are '+', '.join(f"{x['max_paired_path_se']:.5f}" for x in ext)+', respectively.')
    resource=[]
    for d in [8,16]:
        records=[read(f'external_d{d}_s{s}.json') for s in range(400,406)]
        for method,label in [('nbo','NBO'),('soc','SOC-MartNet')]:
            mean=lambda key:statistics.mean(x['methods'][method][key] for x in records)
            resource.append([d,label,f"{mean('training_seconds'):.3f}",f"{mean('setup_and_training_seconds'):.3f}",f"{mean('outer_updates'):.1f}"])
    table('resources','Measured training and setup resources','r8:tab:resources','rlrrr',
       ['$d$','Method','Train (s)','Setup + train (s)','Outer updates'],resource,
       'Single-thread CPU means over six seeds. Identical actor/critic parameter counts within each dimension: 3,224/2,881 at $d=8$, and 4,000/3,265 at $d=16$. SOC-MartNet also trains its 600-output test network. Paired policy audit means are approximately .379 and .440 seconds. Outer-update definitions differ across algorithms and are not equal units of work.')
    print('Generated seven manuscript tables from complete executed records.')
if __name__=='__main__':run()
