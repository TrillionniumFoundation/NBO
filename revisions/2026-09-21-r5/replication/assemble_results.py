"""Assemble the declared panels; retain target misses and distinguish pilots.
This script never changes a run result. Tables are generated from committed JSON.
"""
from pathlib import Path
import json, platform, sys, hashlib, os
import numpy as np
import scipy, torch
from run_panel import panel
D=Path(__file__).resolve().parents[1]; O=D/'results'; P=D/'paper'

def load(p): return json.loads(p.read_text())
def tag(c): return f"n{c['n']}_s{c['seed']}_w{c['width']}_a{c['actor_steps']}_c{c['critic_steps']}_lr{c['lr']:g}"
def table(path,headers,rows,align=None):
    align=align or 'l'+'r'*(len(headers)-1)
    text='\\begin{tabular}{'+align+'}\n\\toprule\n'+' & '.join(headers)+' \\\\\n\\midrule\n'
    text+=''.join(' & '.join(map(str,r))+' \\\\\n' for r in rows)
    text+='\\bottomrule\n\\end{tabular}\n';path.write_text(text)

def main():
    P.mkdir(exist_ok=True); ndu=[]; missing=[]
    for c in panel():
        f=O/(tag(c)+'.json')
        if f.exists(): ndu.append(dict(load(f),panel=c['panel']))
        else: missing.append(str(f.name))
    nonlinear=[load(O/f'nonlinear_d{d}_s{s}_{m}_o4_e800_a400_w192.json') for d in (8,16,32) for s in (40,41) for m in ('nbo','pinnpi') if (O/f'nonlinear_d{d}_s{s}_{m}_o4_e800_a400_w192.json').exists()]
    rec=[load(O/f'recursive_s{s}.json') for s in (51,52) if (O/f'recursive_s{s}.json').exists()]
    games=[load(O/f'game_s{s}.json') for s in (61,62) if (O/f'game_s{s}.json').exists()]
    bounds=load(O/'manufactured_boundary_bounds.json') if (O/'manufactured_boundary_bounds.json').exists() else []
    coupled=[load(f) for f in sorted(O.glob('coupled_*.json'))]
    summary=dict(record_kind='Executed R5 confirmatory snapshot',ndu=ndu,nonlinear=nonlinear,recursive=rec,games=games,boundary_bounds=bounds,coupled=coupled,missing_ndu=missing,
        counts=dict(ndu_completed=len(ndu),ndu_raw_pass=sum(x['raw_pass'] for x in ndu),ndu_safeguarded_pass=sum(x['safeguarded_pass'] for x in ndu),nonlinear_completed=len(nonlinear),recursive_completed=len(rec),game_completed=len(games)),
        scopes=dict(ndu='Candidate finite economy only; continuous actor training, finite action audit',boundary='Continuous stopped manufactured benchmark; analytic occupation-barrier domination',nonlinear='Initial-state rollout/Cole-Hopf comparison; sampling and time bias, not a uniform certificate',recursive='Positive finite recursive model, log-value certificate',game='Full continuous-action dynamic deviations in the finite Markov-state model'),
        pilots_excluded=dict(ndu=[0],nonlinear=[30],recursive=[50],game=[60]),
        numerical_arithmetic='float32 training and float64 finite audits; no interval-arithmetic certification',
        prespecification='Protocols were committed after pilot development and before their first confirmatory execution; reruns are computational reproductions, not new seed selection')
    (O/'summary.json').write_text(json.dumps(summary,indent=2))
    rows=[]
    for name in dict.fromkeys(x['panel'] for x in ndu):
        a=[x for x in ndu if x['panel']==name]
        label=name.replace('_',' ').replace('actor steps','actor steps').replace('critic steps','critic steps')
        rows.append([label,str(len(a)),str(sum(x['raw_pass'] for x in a)),str(sum(x['safeguarded_pass'] for x in a)),f"{max(x['certified_bound_t0'] for x in a):.4f}",f"{np.mean([x['training_seconds']+x['audit_seconds'] for x in a]):.2f}"])
    table(P/'table_ndu.tex',['Configuration','$n$','Raw','Safeguarded','Max. bound','Seconds'],rows)
    rows=[]
    for d in (8,16,32):
        for m in ('nbo','pinnpi'):
            a=[x for x in nonlinear if x['dimension']==d and x['method']==m]
            if not a: continue
            loss=[x['policy_audits'][-1]['loss_estimate_vs_reference'] for x in a]
            rows.append([str(d),'NBO' if m=='nbo' else 'PINN--PI',f"{np.mean(loss):.4f}",f"{max(x['policy_audits'][-1]['sampling_upper_95'] for x in a):.4f}",f"{np.mean([x['training_seconds'] for x in a]):.2f}",f"{np.mean([x['audit_seconds'] for x in a]):.2f}",f"{max(x['peak_rss_kib'] for x in a)/1024:.1f}"])
    table(P/'table_nonlinear.tex',['$d$','Method','Mean loss','Sampling upper','Train (s)','Audit (s)','MiB'],rows,'rlrrrrr')
    rows=[]
    for N in (16,32,64,128,256):
        f=O/f'manufactured_n{N}_bridge.json'; e=O/f'manufactured_n{N}_endpoint.json'
        if not f.exists():continue
        a=load(f); bb=next(x for x in bounds if x['tag']==f.stem)
        rows.append([str(N),f"{load(e)['t0_value_sup_error']:.4f}",f"{a['t0_value_sup_error']:.4f}",f"{a['policy_node_sup_error']:.4f}",f"{bb['continuous_policy_loss_upper']:.4f}"])
    table(P/'table_boundary.tex',['$N$','Endpoint value','Bridge value','Action sup error','Policy-loss bound'],rows)
    rows=[]
    for a in sorted([x for x in coupled if x['config']['k']==2],key=lambda x:x['config']['n']):
        c=a['config'];rows.append([str(c['n']),f"{c['nu']}\\times{c['nx']}",str(c['na']),f"{a['h2_over_dt']:.4f}",f"{a['center_value']:.6f}",f"{a['center_budget']:.6f}",f"{a['center_exit']:.4f}"])
    rows=[[r[0],'$'+r[1]+'$']+r[2:] for r in rows]
    table(P/'table_coupled.tex',['$N$','State grid','$n_a$','$h^2/\\Delta$','$V_0$','$B_0$','Exit'],rows)
    rows=[]
    for a in rec:
        rows.append([str(a['seed']),f"{a['raw_log_value_loss_t0']:.4f}",f"{a['certified_log_value_loss_bound']:.4f}",f"{a['safeguarded_log_value_loss_t0']:.4f}",f"{a['center_raw_consumption_fraction']:.3f}",f"{a['center_raw_portfolio']:.3f}"])
    table(P/'table_recursive.tex',['Seed','Raw log loss','Final bound','Final log loss','$m_0$','$p_0$'],rows)
    rows=[]
    for a in games:
        rows.append([str(a['seed']),f"{a['dynamic_best_response_gain_t0'][0]:.5f}",f"{a['dynamic_best_response_gain_t0'][1]:.5f}",f"{a['dynamic_best_response_gain_all_subgames']:.5f}",f"{a['training_seconds']+a['audit_seconds']:.2f}"])
    table(P/'table_game.tex',['Seed','Player 1, $t=0$','Player 2, $t=0$','All subgames','Seconds'],rows)
    env=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,torch=torch.__version__,platform=platform.platform(),machine=platform.machine(),processor=platform.processor(),cpu_count=os.cpu_count(),torch_threads=torch.get_num_threads(),execution_context=os.environ.get('GITHUB_ACTIONS','local'),source_commit=os.environ.get('GITHUB_SHA','local source; see repository manifest'),timing='One torch CPU thread per fresh training process; training and audit timed separately; interpreter startup excluded from those metrics, included in execution records; hardware and contention affect timings')
    (O/'environment.json').write_text(json.dumps(env,indent=2))
    print(json.dumps(summary['counts']),flush=True)
if __name__=='__main__':main()
