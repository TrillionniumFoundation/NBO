"""Generate all R8 manuscript numbers from immutable result JSON, never literals."""
from __future__ import annotations
import json,hashlib
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];R=BASE/'results';M=BASE/'manuscript';inputs={}
def read(name):
    p=R/name;inputs[str(p.relative_to(BASE))]=hashlib.sha256(p.read_bytes()).hexdigest();return json.loads(p.read_text())
def f(x,d=4):
    if x is None:return '--'
    return f'{x:.{d}f}'
def table(name,caption,headers,rows,note='',long=False):
    cols='l'+'r'*(len(headers)-1);head=' & '.join(headers)+r' \\'
    if long:
        text=r'\begin{small}'+'\n'+r'\begin{longtable}{'+cols+'}\n'+r'\caption{'+caption+r'}\\'+'\n'+r'\toprule'+'\n'+head+'\n'+r'\midrule\endfirsthead'+'\n'+r'\toprule'+'\n'+head+'\n'+r'\midrule\endhead'+'\n'
        text+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+'\n'+r'\bottomrule\end{longtable}\end{small}'+'\n'
    else:
        text=r'\begin{table}[htbp]\centering'+'\n'+r'\caption{'+caption+'}\n'+r'\begin{small}\begin{tabular}{'+cols+'}\n'+r'\toprule'+'\n'+head+'\n'+r'\midrule'+'\n'
        text+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+'\n'+r'\bottomrule\end{tabular}\end{small}'+'\n'
        if note:text+=r'\par\smallskip\begin{minipage}{.96\linewidth}\footnotesize '+note+r'\end{minipage}'+'\n'
        text+=r'\end{table}'+'\n'
    if long and note:text+=r'\noindent\textit{Notes.} '+note+'\n'
    (M/name).write_text(text)

def build():
    M.mkdir(exist_ok=True);a=read('R7_INTEGRATION.json');ndu=[d for d in a['finite_comparisons'] if d['study']=='ndu'];games=[d for d in a['finite_comparisons'] if d['study']=='game']
    rows=[]
    for d in ndu:
        rows.append(['NBO' if d['method']=='guarded_nbo' else 'Direct',d['seed'],f(d['raw_loss']),f(d['final_loss']),f(d['value_error']),f(d['training']+d['verification'],2),f(100*d['corrected_fraction'],3)])
    table('table_r7_ndu.tex','Finite preference policies: R7 evidence',['Method','Seed','Raw loss','Final loss','Value error','Seconds','Guard (\\%)'],rows,
      'Loss bounds cover every stored state and time of the same 175-action economy. Seconds include training and the three reported policy verifications; classical backward induction averages '+f(np.mean([d['classical'] for d in ndu]),3)+' seconds. A raw actor, shortlist, and corrected policy are distinct objects. Utility losses are absolute units.')
    rows=[];continuous=[]
    for method in ['actor','direct','local']:
      for seed in [11,29,47]:
        stem=f'continuous_{"direct" if method=="local" else method}_s{seed}'+('_steps0' if method=='local' else '')+'_search.json';d=read(stem);continuous.append(d)
        rows.append([{'actor':'Actor + search','direct':'Direct + search','local':'Search only'}[method],seed,f(d['raw_finite_reference_minus_policy_max']),f(d['augmented_grid_deviation_max']),f(d['training_seconds'],2),f(d['training_action_queries']/1e6,3)])
    table('table_continuous.tex','Continuous-control training without exact maximizing labels',['Method','Seed','Raw diagnostic','Hybrid gain','Train (s)','Queries ($10^6$)'],rows,
      'Raw diagnostic is the largest finite-reference payoff minus the raw policy payoff. Hybrid gain is the augmented finite-deviation gain, a lower bound on continuous-action regret, not a certificate. All methods use zero exhaustive training backups and zero exact argmax training labels. Search-only omits action-gradient updates. Training, reference, and full-cover verification costs are separate.')
    shared=read('SHARED_ACTION_CERTIFICATES.json');rows=[]
    for d in shared['records']:
        if d['raw']:continue
        rows.append([{'actor':'Actor + search','direct':'Direct + search','local':'Search only'}[d['method']],d['seed'],f(d['policy_regret_upper']),f(d['initial_state_regret_upper']),f(d['evaluation_seconds'],2),'Yes' if d['absolute_target_pass']['0.1'] else 'No'])
    certs=[read('continuous_actor_s11_search_action_certificate.json')]
    if (R/'continuous_actor_s11_search_corner_certificate.json').exists():certs.append(read('continuous_actor_s11_search_corner_certificate.json'))
    cost=sum(x['seconds'] for x in certs);queries=sum(h['box_evaluations'] for x in certs for h in x['history'])
    table('table_action_bounds.tex','Full continuous-action policy bounds on the two-state nodal economy',['Policy','Seed','Uniform bound','Center bound','Eval. (s)','Bound $\\leq .1$'],rows,
      'The full action box is covered at all 425 states and 20 times. The common optimal upper envelope costs '+f(cost,2)+' seconds across the retained implementations and '+f(queries/1e6,2)+' million action-box evaluations. Each row adds its own interval policy evaluation. Unresolved leaves retain their upper bounds. No continuous-state/time error is set to zero.')
    rows=[]
    for d in games:rows.append([d['market'],d['seed'],f(max(d['raw_loss'])),f(d['final_loss'][0]),f(d['final_loss'][1]),d['missing_pure'],f(d['training']+d['verification'],2)])
    table('table_r7_games.tex','R7 neural dynamic-game profiles and full best responses',['Market','Seed','Raw max','Firm 1','Firm 2','Missing','Seconds'],rows,
      'All bounds cover every stored finite state, time, and unilateral action, including deviations at the reported missing pure stages. The full-oracle guard is unused in these principal runs. Profit losses are absolute units; market normalizations are different economies.')
    rows=[]
    for p in sorted(R.glob('comparison_game_*.json')):
        d=read(p.name);rows.append([d['method'].capitalize(),f(d['market'],0),d['seed'],f(d['certificate']['payoff_loss_upper'][0]),f(d['certificate']['payoff_loss_upper'][1]),f(d['training_seconds'],2),f(d['timings']['verification'],2)])
    table('table_game_comparisons.tex','R8 actor-free dynamic-game comparisons',['Method','Market','Seed','Firm 1','Firm 2','Train (s)','Verify (s)'],rows,
      'The direct method fits two continuation networks with the same class and 480 critic Adam updates, versus R7\'s 320 critic and 160 actor updates. Classical selection uses no neural approximation. Every method receives a new full dynamic best response. R7 and R8 timings were measured in their recorded environments; cross-environment ratios are not a hardware-controlled speed experiment.')
    paired=a['paired_payoffs'];rows=[]
    for d in paired:
        rows.append([d['dimension'],d['seed'],'Wide' if d['wide'] else 'Narrow',d['steps'],f(d['mean'],5),f(d['ci95'][0],5),f(d['ci95'][1],5)])
    table('table_paired_all.tex','All method-paired policy-payoff comparisons',['Dim.','Seed','Domain','Steps','NBO $-$ direct','Lower','Upper'],rows,long=True,
      note='Pointwise 95 percent Monte Carlo intervals, 512 paired paths per row. They do not bound optimality, continuous-time bias, or simultaneous coverage.')
    table('table_paired_summary.tex','Paired payoff differences at the finest recorded Euler level',['Dim.','Seed','Domain','Difference','95\\% lower','95\\% upper'],
      [[d['dimension'],d['seed'],'Wide' if d['wide'] else 'Narrow',f(d['mean'],5),f(d['ci95'][0],5),f(d['ci95'][1],5)] for d in paired if d['steps']==160],
      'NBO minus direct payoff on the same 512 paths. Full 40/80/160-step comparisons are in the supplement. Confidence intervals quantify Monte Carlo variation only.')
    table('table_missing_pure.tex','Every missing pure fitted one-step equilibrium in R7',['Market','Seed','Time index','$K_1$','$K_2$','Minimum defect'],
      [[d['market'],d['seed'],d['t'],f(d['capital'][0],6),f(d['capital'][1],6),f"{d['minimum_stage_defect']:.3e}"] for d in a['missing_pure_nodes']],
      'Minimum defect is the smallest maximum unilateral one-step improvement over all joint finite actions. These nodes remain in full dynamic verification; they are not called exact stage equilibria.')
    rows=[]
    for p in sorted(R.glob('comparison_ndu_*.json')):
        d=read(p.name);rows.append(['Gated' if d['method']=='gated' else 'Chebyshev',d['seed'],d['parameter_count'],f(d['certificate']['payoff_loss_upper'][0]),f(d['value_error']),f(d['training_seconds'],2),f(d['timings']['verification'],2)])
    table('table_additional_comparisons.tex','Additional continuation representations, identical finite preference economy',['Method','Seed','Parameters','Policy bound','Value error','Train (s)','Verify (s)'],rows,
      'Gated denotes a DGM-style architecture fitted to finite Bellman targets, not a differential DGM solver. Chebyshev degrees are 6, 10, and 14. All actions are enumerated; construction and reference costs are separately retained in JSON. Deterministic projections are not replicated under fictitious random seeds.')
    refine=read('REFINEMENT.json')
    table('table_refinement.tex','Frozen continuous-policy refinement, common economic domain',['Method','Seed','Grid','Steps','Center payoff','Center reference'],
      [[d['method'].capitalize(),d['seed'],f"{d['grid'][0]}$\\times${d['grid'][1]}",d['steps'],f(d['center_policy_payoff'],6),f(d['center_finite_reference'],6)] for d in refine['records']],
      note='Policies are frozen on the original time schedule and bilinearly interpolated in state. References still use 175 actions. Differences are sensitivity diagnostics, not continuous-state/time upper bounds.',long=True)
    rows=[]
    for name,label in [('continuous_actor_s11_smoke.json','Actor smoke'),('continuous_actor_s11.json','Raw actor'),('continuous_actor_s11_h4_fresh1.json','Four-head reset'),('continuous_direct_s11.json','Direct gradient')]:
        d=read(name);rows.append([label,d['seed'],f(d['augmented_grid_deviation_max']),f(d['training_seconds'],2),'Pass' if d['diagnostic_target_pass'] else 'Fail'])
    table('table_failures.tex','Retained continuous-action development failures',['Configuration','Seed','Deviation gain','Train (s)','Target $.1$'],rows,
      'All executed pilot sources, raw arrays, and histories remain. The smoke grid and budget differ from the principal grid; it is not a principal-seed replicate. Pilot selection and subsequent improvements are explicitly post-review development.')
    manifest=dict(input_sha256=inputs,generated={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(M.glob('table_*.tex'))})
    (BASE/'TABLE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':build()
