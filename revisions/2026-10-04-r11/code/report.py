"""Recompute raw statistics, audit finite families, and generate all new tables."""
from __future__ import annotations
import csv,hashlib,json,math,re,sys
from pathlib import Path
import numpy as np
from bellman_study import ROOT,R,P
from policy_certificate import empirical_lower


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def f(x):return f'{float(x):.6f}'
def low(x):return f'{math.floor(float(x)*1e6)/1e6:.6f}'
def high(x):return f'{math.ceil(float(x)*1e6)/1e6:.6f}'
def esc(s):return str(s).replace('_',r'\_')

def table(path,caption,label,columns,heads,rows,long=False):
    cols=''.join(columns);body='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
    if long:
        text=r'{\small\setlength{\tabcolsep}{4pt}'+'\n'+r'\begin{longtable}{'+cols+'}\n'+r'\caption{'+caption+r'}\label{'+label+r'}\\'+'\n'+r'\toprule'+'\n'+' & '.join(heads)+r'\\\midrule\endfirsthead'+'\n'+' & '.join(heads)+r'\\\midrule\endhead'+'\n'+body+'\n'+r'\bottomrule\end{longtable}}'+'\n'
    else:
        text=r'\begin{table}[htbp]\centering\small\setlength{\tabcolsep}{4pt}'+'\n'+r'\caption{'+caption+r'}\label{'+label+'}\n'+r'\begin{tabular}{'+cols+r'}\toprule'+'\n'+' & '.join(heads)+r'\\\midrule'+'\n'+body+'\n'+r'\bottomrule\end{tabular}\end{table}'+'\n'
    path.write_text(text)


def report():
    rows=[];fits=[];tunes=[];inputs={}
    for p in sorted((R/'results').rglob('*.json')):
        r=json.loads(p.read_text())
        if 'bound' in r and 'constants' in r:
            raw=p.with_suffix('.npz');a=np.load(raw);assert sha(raw)==r['raw_sha256'],raw
            assert sha(ROOT/r['source_path'])==r['weights_sha256'],r['source_path']
            np.testing.assert_allclose(a['paired_gain'],a['production']-a['consumption_deficit']+a['terminal_gain'],rtol=0,atol=1e-15)
            c=r['constants'];z=empirical_lower(a['paired_gain'],c['clipping_threshold'],c['bias_upper'],c['clipping_bias'],r['bound']['family_size'],r['bound']['alpha'])
            for k in ['mean','sample_sd','lower','upper','empirical_bernstein_margin']:
                assert abs(z[k]-r['bound'][k])<1e-14,(r['id'],k)
            assert c['bias_upper']>=c['actor_bias']['total']+c['anchor_bias']['total']
            assert r['steps']*r['paths']>0 and c['scope'].startswith('fixed initial state')
            assert r['policy_regret_upper']>=c['anchor_upper']-z['lower']-1e-18
            rows.append(r);inputs[str(p.relative_to(ROOT))]=sha(p);inputs[str(raw.relative_to(ROOT))]=sha(raw)
        if 'requested_iterations' in r:fits.append(r);inputs[str(p.relative_to(ROOT))]=sha(p)
        if p.name.startswith('TUNING_'):tunes.append(r);inputs[str(p.relative_to(ROOT))]=sha(p)
    primary=[r for r in rows if re.fullmatch(r'(nbo|dpo|linear)_d(10|20|50)_s\d+_n1024_r1_mean0_sd0',r['id'])]
    assert len(primary)==90,('primary missing or duplicated',len(primary))
    assert len(rows)*2<=2000,('family overrun',len(rows))
    protocol=json.loads((R/'PROTOCOL.json').read_text())
    names={'nbo':'NBO','dpo':'Direct policy','linear':'Affine'}
    m=R/'manuscript';m.mkdir(exist_ok=True);summary=[];cost=[];outcome={}
    for d in [10,20,50]:
        for method in ['nbo','dpo','linear']:
            g=sorted([r for r in primary if r['dimension']==d and r['method']==method],key=lambda r:r['id'])
            assert len(g)==10
            gain=[r['bound']['mean'] for r in g];lower=[r['bound']['lower'] for r in g];regret=[r['policy_regret_upper'] for r in g]
            summary.append([d,names[method],f(np.mean(gain)),f(np.std(gain,ddof=1)),low(min(lower)),high(max(regret))])
            t=[r for r in fits if r.get('method')==method and r['dimension']==d and r['requested_iterations']==120 and r['width']==32 and re.fullmatch(fr'{method}_d{d}_s\d+',r['id'])]
            assert len(t)==10
            cost.append([d,names[method],f'{np.median([r["seconds"] for r in t]):.2f}',f'{np.median([r["seconds"] for r in g]):.2f}',f'{1e3*np.median([r["decision_batch256_seconds"] for r in g]):.3f}',sum(r['bound']['lower']>=.0005 for r in g)])
            outcome[f'{method}_{d}']=dict(mean_gain=float(np.mean(gain)),seed_sd=float(np.std(gain,ddof=1)),min_gain_lower=min(lower),max_regret=max(regret),positive=sum(v>0 for v in lower),target_count=sum(v>=.0005 for v in lower))
    table(m/'table_primary.tex','Primary continuous-economy comparison. Ten training seeds per row; all policies start at $y=0$. Gain is in discounted utility units. Lower endpoints are rounded down and upper endpoints up.','tab:r11primary','rlrrrr',['$d$','Method','Mean gain','Seed s.d.','Min. $L_\phi$','Max. regret'],summary)
    table(m/'table_cost.tex','Recorded CPU costs and the declared improvement target. Verification includes setup, simulation, and arithmetic. Decision time includes a batch of 256 action and internal-drift updates. The last column counts $L_\phi\geq.0005$ among ten seeds.','tab:r11cost','rlrrrr',['$d$','Method','Train (s)','Verify (s)','Decision (ms)','Target / 10'],cost)
    nbo=[r for r in primary if r['method']=='nbo'];Lmin=min(r['bound']['lower'] for r in nbo);Lmax=max(r['bound']['lower'] for r in nbo);positive=sum(r['bound']['lower']>0 for r in nbo)
    allfailed=[r.get('id',str(r)) for r in fits if r.get('failure')]
    text=(f'Of the 30 primary NBO policies, {positive} have a strictly positive simultaneous lower improvement endpoint. '
          f'The lower endpoints range from ${low(Lmin)}$ to ${low(Lmax)}$ in discounted utility units. '
          f'The number meeting the declared improvement target $.0005$ is {sum(r["bound"]["lower"]>=.0005 for r in nbo)}. '
          f'The largest policy-specific NBO regret upper endpoint is ${high(max(r["policy_regret_upper"] for r in nbo))}$. '
          f'These are results for the stated implementation, initial state, and conditional sampling contract. '
          f'The archive contains {len(rows)} two-sided evaluation records and {len(allfailed)} logged training failures; an unmet gain target is recorded separately from a training exception.\n')
    (m/'results_text.tex').write_text(text)
    A=(1-math.exp(-P['discount']*P['T']))/P['discount']
    r10=json.loads((ROOT/'revisions/2026-10-04-r10/results/CONTINUOUS_CERTIFICATES.json').read_text())
    anchors=[]
    for d in [10,20,50]:
        c=next(r['constants'] for r in primary if r['dimension']==d)
        tube=next(r for r in r10['records'] if r['dimension']==d and r['epsilon']==.1 and r['initial_std_upper']==0 and r['panels']==16384)
        anchors.append([d,high(c['anchor_upper']),high(tube['regret_upper']),f'{math.ceil(100000*math.expm1(c["anchor_upper"]/A))/1000:.3f}',f'{math.ceil(100000*math.expm1(tube["regret_upper"]/A))/1000:.3f}'])
    table(m/'table_anchors.tex','Analytical comparators before policy-specific improvement. The last two columns are externally financed flow-equivalent percentages, not empirical population welfare effects.','tab:r11anchors','rrrrr',['$d$','$G_d$','$G_d+D_{d,.1}$','Anchor (\\%)','Tube (\\%)'],anchors)
    frontier=[r for r in rows if re.fullmatch(r'(nbo|dpo|linear)_d(10|20|50)_s11_k(20|40|80|120)_n512_r1_mean0_sd0',r['id'])]
    assert len(frontier)==36,len(frontier)
    fr=[[r['dimension'],names[r['method']],r['iteration'],f(r['bound']['mean']),low(r['bound']['lower']),high(r['policy_regret_upper'])] for r in sorted(frontier,key=lambda r:(r['dimension'],r['method'],r['iteration']))]
    table(m/'table_frontier.tex','Checkpoint frontier in dimension fifty, seed 11. Each checkpoint has 2,048 paths and 512 cells; the explicit transfer bound is retained. A negative lower endpoint is not replaced by a pass.','tab:r11frontier','rlrrrr',['$d$','Method','Iteration','Mean gain','$L_\phi$','Regret upper'],[r for r in fr if r[0]==50])
    table(m/'table_all_frontiers.tex','Complete checkpoint frontiers; seed 11, 2,048 paths and 512 cells.','tab:r11allfront','rlrrrr',['$d$','Method','Iteration','Mean gain','$L_\phi$','Regret upper'],fr,True)
    rad=[r for r in rows if re.fullmatch(r'nbo_d(10|20|50)_s11_n1024_r(0.5|1|1.5)_mean0_sd0',r['id'])]
    sr=[[r['dimension'],f'{.1*r["radius_scale"]:.2f}',f(r['bound']['mean']),low(r['bound']['lower']),high(r['policy_regret_upper'])] for r in sorted(rad,key=lambda r:(r['dimension'],r['radius_scale']))]
    table(m/'table_sensitivity.tex','Frozen-correction radius comparison, seed 11. Radius $.10$ uses 8,192 paths; the rescaled radii use 4,096. All use 1,024 cells and their own simultaneous error account.','tab:r11radius','rrrrr',['$d$','Radius','Mean gain','$L_\phi$','Regret upper'],sr)
    allseed=[]
    for r in sorted(primary,key=lambda r:(r['dimension'],r['method'],int(re.search('_s(\d+)_',r['id'])[1]))):
        seed=int(re.search('_s(\d+)_',r['id'])[1]);allseed.append([r['dimension'],names[r['method']],seed,r['iteration'],f(r['bound']['mean']),low(r['bound']['lower']),high(r['policy_regret_upper'])])
    table(m/'table_all_seeds.tex','All primary policies. The utility endpoints include time, sampling, clipping, and arithmetic errors.','tab:r11allseeds','rlrrrrr',['$d$','Method','Seed','Iter.','Mean gain','$L_\phi$','Regret upper'],allseed,True)
    stress=[r for r in rows if (r['shift']!=0 or r['spread']!=0 or 'width' in r['id'] or '_long_' in r['id'] or r['id'].startswith('adversary'))]
    st=[]
    for r in sorted(stress,key=lambda r:r['id']):
        label=('t3 profile' if r.get('profile')=='student3' else f'mean {r["shift"]:g}, sd {r["spread"]:g}')
        if 'width' in r['id']:label='width '+re.search('width(\d+)',r['id'])[1]
        if '_long_' in r['id']:label=names[r['method']]+' 600'
        if 'adversary' in r['id']:label='zero correction' if 'zero' in r['id'] else 'saturated correction'
        st.append([r['dimension'],label,f(r['bound']['mean']),low(r['bound']['lower']),f'{r["outside_training_box_frequency"]:.3f}',f'{r["action_saturation_frequency"]:.3f}'])
    table(m/'table_all_sensitivity.tex','Initial-state, architecture, extended-budget, and adverse-policy records. Outside-box frequency is measured on internal states and is not a domain guarantee.','tab:r11allstress','rlrrrr',['$d$','Configuration','Mean gain','$L_\phi$','Outside','Saturated'],st,True)
    gr=[]
    for r in sorted([r for r in rows if r['method']=='greedy'],key=lambda r:r['id']):
        mode='direct_full' if 'direct_full' in r['id'] else 'direct_tube';t=next(t for t in tunes if t['dimension']==r['dimension'] and t['mode']==mode)
        gr.append([r['dimension'],'Full+projection' if mode=='direct_full' else 'Tube',t['selected_steps'],f'{t["selected_mix"]:.2f}',f(r['bound']['mean']),low(r['bound']['lower'])])
    assert len(gr)==6,len(gr)
    table(m/'table_greedy.tex','Validation-tuned critic greedification. Full+projection is explicitly a conservative hybrid. Budgets and mixing fractions are chosen without the final noise bank.','tab:r11greedy','rlrrrr',['$d$','Critic family','Steps','Mix','Mean gain','$L_\phi$'],gr)
    # Diagnostics are retained at the stochastic-target level; report correlations descriptively.
    correlations=[]
    for d in [10,20,50]:
        xx=[];yy=[]
        for r in nbo:
            if r['dimension']!=d:continue
            seed=int(re.search('_s(\d+)_',r['id'])[1]);dp=R/'results'/f'seed_{seed}'/f'DIAGNOSTIC_d{d}.json';diag=json.loads(dp.read_text());xx.append(diag['costate_target_mse']);yy.append(r['bound']['mean']);inputs[str(dp.relative_to(ROOT))]=sha(dp)
        correlations.append(dict(dimension=d,costate_target_payoff_correlation=float(np.corrcoef(xx,yy)[0,1]),interpretation='descriptive across ten seeds; noisy target discrepancy, not verified derivative bias'))
    audit=dict(primary_policies=len(primary),all_two_sided_rows=len(rows),allocated_one_sided_statements=2000,used_one_sided_statements=2*len(rows),confidence_contract='conditional 95% finite-family coverage; initial states fixed as recorded',raw_arrays_replayed=len(rows),training_failures=allfailed,primary_nbo_positive=positive,primary_nbo_lower_range=[Lmin,Lmax],groups=outcome,diagnostic_correlations=correlations,remaining_scope=['not an optimizer convergence proof','not a uniform initial-state PDE certificate','not machine-formal RNG verification','not calibrated population welfare','not a continuous-transfer certificate for the preference model'])
    (R/'results/AUDIT.json').write_text(json.dumps(audit,indent=2,allow_nan=False)+'\n')
    response=(f'The final raw-data replay contains {len(primary)} primary policies and {len(rows)} two-sided evaluation records. '
              f'Among the 30 primary NBO policies, {positive} have positive lower improvement endpoints; their lower endpoints range from ${low(Lmin)}$ to ${low(Lmax)}$. '
              f'The largest NBO regret upper endpoint is ${high(max(r["policy_regret_upper"] for r in nbo))}$. '
              f'The archive reports {len(allfailed)} training failures separately from unmet economic accuracy targets. '
              'The main tables and the complete supplement report direct and affine comparisons without suppressing competitive baseline outcomes.\n')
    (m/'response_results.tex').write_text(response)
    outputs={str(p.relative_to(ROOT)):sha(p) for p in m.glob('table_*.tex')}
    for p in [m/'results_text.tex',m/'response_results.tex']:outputs[str(p.relative_to(ROOT))]=sha(p)
    (R/'TABLE_MANIFEST.json').write_text(json.dumps(dict(inputs=inputs,outputs=outputs),indent=2)+'\n')
    with (R/'results/PRIMARY.csv').open('w',newline='') as file:
        writer=csv.writer(file);writer.writerow(['d','method','mean_gain','seed_sd','min_lower','max_regret']);writer.writerows(summary)
    print(json.dumps(audit,indent=2))

if __name__=='__main__':report()
