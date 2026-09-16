#!/usr/bin/env python3
"""Generate every R6 numerical table and the execution summary from JSON."""
from common import *
PAPER=ROOT/'revisions/2026-09-16-r6/paper'

def read(name):return json.loads((OUT/(name+'.json')).read_text())
def num(x,digits=6):
    if x is None:return '--'
    return f'{x:.{digits}g}'
def table(name,label,caption,headers,rows,note,align=None):
    align=align or ('l'+'r'*(len(headers)-1))
    s='\\begin{table}[!htbp]\n\\centering\\small\n\\caption{'+caption+'}\n\\label{'+label+'}\n'
    s+='\\begin{tabular}{'+align+'}\n\\toprule\n'+' & '.join(headers)+' \\\\\n\\midrule\n'
    for row in rows:s+=' & '.join(str(v) for v in row)+' \\\\\n'
    s+='\\bottomrule\n\\end{tabular}\n\\par\\smallskip\n\\begin{minipage}{0.98\\linewidth}\\footnotesize\nNotes: '+note+'\n\\end{minipage}\n\\end{table}\n'
    (PAPER/(name+'.tex')).write_text(s)

def run():
    bank=read('bank_comparison');a=bank['initial_distribution_ols'];b=bank['statewise_ols'];m=bank['restricted_neural_free_bank']
    table('table_r6_ols','tab:r6_ols','Exact-Oracle Scalar Optimistic Support',
          ['Coverage objective','Anchors','Seconds','MiB','Global bound'],
          [['Initial state/date',a['anchors'],num(a['preparation_seconds']),num(a['memory_bytes']/2**20),num(a['all_state_date_bound'])],
           ['All states/dates',b['anchors'],num(b['preparation_seconds']),num(b['memory_bytes']/2**20),num(b['uniform_bound'])]],
          'Same exact full-menu oracle and $10^{-3}$ target. The initial-state bound is '+num(a['focal_bound'])+'. Global means all finite states, dates, and $d\\in[0,1]$. Common kernel setup costs '+num(bank['kernel_build_seconds'])+' seconds and is excluded from both preparation columns. MiB counts policies and features, not shared kernels or upper buffers. The independent full-line/adjacent-line discrepancy is '+num(b['independent_full_envelope_check']['full_envelope_minus_adjacent_pair_max'])+'.')
    loss=max(r['maximum_full_target_loss'] for r in m['anchor_losses'])
    table('table_r6_mesh','tab:r6_mesh','Removing Neural Actions from the Feasible Policy Bank',
          ['Feasible lower policies','Anchors','Anchor loss','Interval bound'],
          [['Full menu',b['anchors'],'0',num(b['uniform_bound'])],['Common mesh only',m['anchors'],num(loss),num(m['uniform_bound_vs_original_full_target'])]],
          'Both rows use the original neural-inclusive optimal upper target at the same anchors. The second row removes all three neural candidates only from the lower policies. The interval bound covers all states, dates, and $d\\in[0,1]$. Mesh-policy construction costs '+num(m['policy_construction_seconds'])+' seconds; this is not an autonomous mesh-anchor-discovery time.')
    qp=read('structural_qp')
    table('table_r6_qp','tab:r6_qp','Fresh Queries with Reusable Quadratic Structure',
          ['Queries','Learned total','QP total','QP query','QP max gap'],
          [[r['queries'],num(r['learned_total_seconds']),num(r['qp_total_seconds']),num(r['qp_query_seconds']),num(r['qp_max_gap'])] for r in qp['rows']],
          'Times are seconds, single-thread, query medians of three. The learned total includes critic retraining and full policy evaluation; QP total includes structural setup and independent full-tree gradient/gap evaluation. All queries start at zero controls. The largest learned policy-loss upper bound is '+num(max(r['learned_loss_upper_vs_tight'] for r in qp['rows']))+'. The original reference timings and all timing samples remain in the JSON record.')
    ker=read('kernel_certificate');tr=read('transport')
    table('table_r6_kernel','tab:r6_kernel','Uniform Policy Reuse across Transition Mixtures',
          ['$d$','Anchors','Corrected bound','Count bound','Prep. seconds'],
          [[num(r['d']),r['anchor_count'],num(r['uniform_bound']),num(tr['rows'][i]['uniform_all_theta_date_state_bound']),num(r['offline_seconds'])] for i,r in enumerate(ker['rows'])],
          'Each row covers every $\\lambda\\in[0,1]$, all 1,617 states, and eight decision dates at the displayed fixed contract. Corrected preparation includes endpoint solves, policy-coefficient construction, and interval certification, excluding the common two-kernel build ('+num(ker['kernel_build_seconds'])+' seconds) and subsequent independent replay. The count bound uses its separate informed upper oracle and three feasible anchor policies. It is valid but does not meet the $10^{-3}$ target. No joint $(d,\\lambda)$-continuum or diffusion guarantee is asserted.')
    me=read('mechanism')
    table('table_r6_option','tab:r6_option','Deliberate Preference Formation and Risk-Class Values',
          ['$d$','$\\Delta^{\\rm adj}$','$\\Delta^0$','$\\Omega_+-\\Omega_-$'],
          [[num(r['d']),num(r['adjustable']['delta']),num(r['no_deliberate_adjustment']['delta']),num(r['preference_contribution_to_risk_advantage'])] for r in me['rows']],
          'Positive $\\Delta$ favors a positive first risky position; negative $\\Delta$ favors the nonpositive class. Both classes optimize every subsequent action. The restricted arm sets deliberate adjustment to zero at all states and dates but retains preference shocks and every financial and stopping primitive. Each reported value is independently evaluated in the same cardinal utility units.')
    rows=[]
    for r in me['brackets']:
        if r['bracket']:
            mid=r['midpoint'];rows.append([num(r['k']) if r['adjustment_enabled'] else 'No adjustment',
              '['+num(r['bracket'][0],8)+', '+num(r['bracket'][1],8)+']',num(mid['delta_duration']),num(mid['delta_effort']),num(r['local_regular_branch_slope'])])
        else:rows.append([num(r['k']) if r['adjustment_enabled'] else 'No adjustment','No bracket','--','--','--'])
    table('table_r6_frontier','tab:r6_frontier','Risk Indifference and the Duration--Effort Comparison',
          ['$k$ / restriction','Opposite-sign bracket','$A_+-A_-$','$C_+-C_-$','Ratio'],rows,
          'Each bracket has opposite risk-advantage signs at its endpoints and width at most $2\\times10^{-5}$. It proves existence of a crossing, not global uniqueness. Features and their ratio are evaluated at the midpoint. The ratio predicts a regular local branch slope only under the stated nonzero-duration and differentiability conditions. A zero-adjustment policy has zero adjustment effort. Bracket endpoints and their signed values are stored, rather than inferred from rounded table entries.')
    summary=['# R6 executed evidence','',
       'All numbers below are generated from the actual JSON outputs. Timing is not a scientific superiority claim.','',
       f"- Exact-oracle scalar OLS: initial-distribution {a['anchors']} anchors, all-state/date {b['anchors']} anchors; respective global bounds {a['all_state_date_bound']:.16g} and {b['uniform_bound']:.16g}.",
       f"- Removing neural lower actions: same original-target uniform bound {m['uniform_bound_vs_original_full_target']:.16g}; maximum anchor loss {loss:.16g}.",
       '- Reusable QP (query count; learned total seconds; QP total seconds; independent maximum gap):']
    summary += [f"  - {r['queries']}; {r['learned_total_seconds']:.9g}; {r['qp_total_seconds']:.9g}; {r['qp_max_gap']:.12g}" for r in qp['rows']]
    summary += ['- Corrected transition-law certificates (fixed d; anchors; all-state/date/lambda bound):']
    summary += [f"  - {r['d']}; {r['anchor_count']}; {r['uniform_bound']:.16g}" for r in ker['rows']]
    summary += ['- Matched adjustment restriction (d; adjustable risk advantage; no-adjustment risk advantage):']
    summary += [f"  - {r['d']}; {r['adjustable']['delta']:.12g}; {r['no_deliberate_adjustment']['delta']:.12g}" for r in me['rows']]
    summary += ['','The policy values, upper certificates, finite-model scope, timing samples, conditional slope interpretation, and unresolved global-uniqueness question are retained in the underlying records.','']
    (ROOT/'revisions/2026-09-16-r6/execution_summary.md').write_text('\n'.join(summary))
if __name__=='__main__':run()
