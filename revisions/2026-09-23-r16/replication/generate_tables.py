"""Build paper tables from complete canonical records; round every bound upward."""
from pathlib import Path
from decimal import Decimal, ROUND_CEILING
import json
P=Path(__file__).resolve().parent.parent; R=P/'results'; O=P/'paper'; O.mkdir(exist_ok=True)
def read(p): return json.loads((R/p).read_text())
def up(x,n=8):
    return format(Decimal.from_float(float(x)).quantize(Decimal(1).scaleb(-n),rounding=ROUND_CEILING),'f')
def table(name,caption,label,columns,header,rows,note):
    text=r'\begin{table}[htbp]\centering\small'+'\n'+r'\caption{'+caption+r'}\label{'+label+'}\n'+r'\begin{tabular}{'+columns+'}\n'+r'\toprule'+'\n'+header+r'\\\midrule'+'\n'
    text+='\n'.join(' & '.join(map(str,row))+r'\\' for row in rows)+'\n'+r'\bottomrule\end{tabular}'+'\n'+r'\par\smallskip\footnotesize '+note+'\n'+r'\end{table}'+'\n'
    (O/(name+'.tex')).write_text(text)
def main():
    ns=[]
    for seed in range(16100,16110):
        for step in [800,2400]:
            row=read(f'neural/seed{seed}/certificate{step}.json')
            assert row['failed_cells']==row['skipped_cells']==0 and row['boundary_budget']==0
            row['training_seconds']=read(f'neural/seed{seed}/resources.json')['wall_seconds']
            ns.append(row)
    inv=read('inventory/summary.json'); assert len(inv)==20
    bs=read('baselines/summary.json');assert len(bs)==6
    fresh=read('fresh_library/envelope.json');mpfr=read('mpfr_library/envelope.json')
    fc=read('foundation_checks.json')
    assert fresh['node_count']==read('fresh_library/resources.json')['nodes']
    assert mpfr['node_count']==18
    for r in inv+bs: assert r['failed_cells']==r['skipped_cells']==0
    final=[r for r in inv if r['step']==1000]
    macros={'RNNMin':(min(r['t0_regret_upper'] for r in ns),6),'RNNMax':(max(r['t0_regret_upper'] for r in ns),6),
     'RFreshGap':(fresh['uniform_regret_upper'],12),'RMPFRGap':(mpfr['uniform_regret_upper'],12),
     'RInventoryFinalMax':(max(r['per_coordinate_regret_upper'] for r in final),9),
     'RFreshTopupPercent':(fc['fresh_library']['percent_upper'],6)}
    text='% Generated exclusively from retained numerical records. Bound decimals rounded upward.\n'
    text+='\n'.join('\\newcommand{\\'+k+'}{'+up(v,n)+'}' for k,(v,n) in macros.items())+'\n'
    text+='\\newcommand{\\RFreshNodes}{'+str(fresh['node_count'])+'}\n'
    (O/'result_macros.tex').write_text(text)
    rows=[]
    for seed in range(16100,16110):
        a,b=[r for r in ns if r['seed']==seed]
        rows.append([seed,a['width'],up(a['t0_regret_upper'],5),up(b['t0_regret_upper'],5),up(a['training_seconds'],2),up(a['wall_seconds']+b['wall_seconds'],2)])
    table('neural_table','Full-horizon neural checkpoints in the original economy','tab:r16neural','rrrrrr',r'Seed & Width & 800 updates & 2,400 updates & Train (s) & Verify (s)',rows,
      r'Each bound is uniform over the original interior state rectangle at time zero, $k=2$, and uses 1,024 cells with the original continuous action maximum. The trace contribution is exactly zero. Training time covers both checkpoints in one trajectory; verification time sums their two audits. No checkpoint meets $10^{-2}$. Resource measurements are descriptive, not matched-accuracy efficiency comparisons.')
    rows=[[r['method'].replace('markov_chain','Markov chain').replace('semi_lagrangian','Semi-Lagrangian'),r['state_nodes_per_axis'],r['time_steps'],up(r['t0_regret_upper'],5),up(r['generation_wall_seconds'],2),up(r['verification_wall_seconds'],2)] for r in bs]
    table('baseline_table','Same-economy state-space candidate generation and verification','tab:r16baselines','lrrrrr',r'Method & Nodes/axis & Time steps & Regret bound & Generate (s) & Verify (s)',rows,
      r'All six policies are continuous bilinear state interpolants of bounded heads, piecewise constant in time, with the portfolio-distance factor. The common witness is the predeclared seed 16100 final critic, not a fitted value from either baseline. Generation discretizes the model; the separate certificate evaluates the continuous-time policy and unchanged stopping contract. None meets $10^{-2}$, so this is not a matched-accuracy ranking.')
    rows=[]
    for seed in range(16200,16210):
        a,b=[r for r in inv if r['seed']==seed]
        rows.append([seed,a['width'],up(a['per_coordinate_regret_upper'],8),up(b['per_coordinate_regret_upper'],8),up(b['training_wall_seconds'],2),up(a['verification_wall_seconds']+b['verification_wall_seconds'],2)])
    table('inventory_table','Certified neural policy loss per inventory coordinate','tab:inventory','rrrrrr',r'Seed & Width & 250 updates & 1,000 updates & Train (s) & Verify (s)',rows,
      r'Each checkpoint uses a complete 512-cell time cover and a state-global quadratic proof. Bounds hold for every $|x_0|^2/d\leq1$. Multiply the reported bound by $d$ for total loss at $d=4,8,16,32,64,128$. One gain pair is reused across dimensions. Timings cover one training trajectory and its two checks, not six duplicated runs.')
    rows=[]
    for folder,label in [('mpfr_library','Historical policies; MPFR'),('fresh_library','Fresh model-to-library')]:
        e=read(folder+'/envelope.json');rs=read(folder+'/resources.json')
        rows.append([label,e['node_count'],up(e['uniform_regret_upper'],12),up(rs['wall_seconds'],2),up(rs.get('max_rss_kib',rs.get('max_worker_rss_kib',0))/1024,1)])
    table('price_table','Complete price-continuum calculations on the original economy','tab:r16price','lrrrr',r'Calculation & Nodes & Uniform regret & Wall time (s) & Peak RSS (MiB)',rows,
      r'Both cover $(t,u,x)=(0,2,1.25)$ and every $k\in[.5,8]$. Historical inputs are frozen policies and dual pilots, not inherited endpoints; MPFR recomputes every node. The fresh calculation starts from model constants and deterministic initializations, with no historical policy or pilot. Its arithmetic is the retained rational--Taylor implementation; the MPFR label does not apply to the fresh library. Peak MPFR RSS is the largest worker, not summed concurrent memory.')
    # A compact machine-readable anchor for source-to-prose checks.
    summary={'original_neural_checkpoints':20,'original_neural_target_met':any(r['targets']['0.01'] for r in ns),
     'original_neural_bounds':[r['t0_regret_upper'] for r in ns], 'classical_candidates':6,'classical_target_met':any(r['targets']['0.01'] for r in bs),
     'inventory_checkpoints':20,'inventory_final_max_per_coordinate':max(r['per_coordinate_regret_upper'] for r in final),
     'fresh_nodes':fresh['node_count'],'fresh_gap':fresh['uniform_regret_upper'],'mpfr_nodes':18,'mpfr_gap':mpfr['uniform_regret_upper'],
     'all_reported_bounds_rounded_up':True,'source_scope':'generated from canonical retained JSON records, not handwritten numbers'}
    (R/'paper_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
if __name__=='__main__':main()
# Additional audit tables use the identical stored objects, never selected seeds.
if __name__=='__main__':
    rows=[]
    for name,f in [('Accessible, coarse','neural/seed16100/certificate2400.json'),('Accessible, refined','neural/seed16100/refinement.json'),('All-face ablation','neural/all_face_ablation/certificate.json')]:
        r=read(f);rows.append([name,r['step'],r['interior_cells'],up(r['t0_regret_upper'],6),up(r['unsigned_residual_budget_upper'],6),up(r['wall_seconds'],2)])
    table('neural_refinement_table','Fixed-object cover refinement and separate architecture ablation','tab:supprefinement','lrrrrr',r'Object & Updates & Cells & Signed budget & Unsigned budget & Seconds',rows,
      r'Signed means the integrated positive optimal residual plus negative policy residual. Unsigned is the separately recorded $2e+q$ budget. Every trace budget is zero. The ablation is a different 800-update network, not a cover refinement of the 2,400-update candidate. Differences between enclosures are not certified estimates of the exact policy loss.')
    inv=read('inventory/summary.json');rows=[]
    base=[r for r in inv if r['seed']==16200 and r['step']==1000][0]
    for r in [read('inventory/refinement_128.json'),base,read('inventory/refinement_2048.json')]:
        rows.append([r['cells'],up(r['mode_residual_upper'][0],8),up(r['mode_residual_upper'][1],8),up(r['per_coordinate_regret_upper'],9)])
    table('inventory_refinement_table','Fixed neural gain functions: complete time-cover refinement','tab:suppinventoryrefine','rrrr',r'Time cells & Orthogonal residual & Mean residual & Loss/coordinate',rows,
      r'The same seed 16200 final gain pair is used in every row. This isolates enclosure refinement from training-budget changes. All state dimensions share the same two-mode proof; total loss is dimension times the per-coordinate bound.')
    rows=[]
    for folder,label in [('neural','Original neural'),('inventory','Inventory neural'),('fresh_library','Fresh price library'),('mpfr_library','MPFR historical nodes'),('baselines','Six classical candidates')]:
        f='suite_resources.json' if folder=='neural' else 'resources.json';r=read(folder+'/'+f)
        rows.append([label,up(r['wall_seconds'],2),up(r.get('max_rss_kib',r.get('max_worker_rss_kib',0))/1024,2) if ('max_rss_kib' in r or 'max_worker_rss_kib' in r) else r'\textemdash'])
    table('resource_table','Measured experiment resources','tab:suppresources','lrr',r'Experiment & Wall seconds & Reported peak RSS (MiB)',rows,
      r'Per-experiment timings exclude package installation. Neural seeds and arithmetic nodes may run concurrently; peaks are process-local where stated in JSON and must not be summed as simultaneous memory. A dash means no aggregate peak was measured; seed/process peaks remain in their individual records. The root pipeline receipt reports end-to-end wall time and the execution environment identifies hardware and package versions.')
if __name__=='__main__':
    from decimal import ROUND_FLOOR, localcontext
    from fractions import Fraction
    import sys
    def lower(x,n=10): return format(Decimal.from_float(float(x)).quantize(Decimal(1).scaleb(-n),rounding=ROUND_FLOOR),'f')
    def gap(u,l,n=10):
        q=Fraction(u)-Fraction(l)
        with localcontext() as ctx:
            ctx.prec=100;ctx.rounding=ROUND_CEILING
            return format((Decimal(q.numerator)/Decimal(q.denominator)).quantize(Decimal(1).scaleb(-n),rounding=ROUND_CEILING),'f')
    rows=[[format(r['k'],'.9g'),lower(r['L']),up(r['U'],10),gap(r['U'],r['L'])] for r in read('mpfr_library/nodes.json')]
    table('mpfr_nodes_table','Complete MPFR re-evaluation of all eighteen historical price nodes','tab:suppmpfrnodes','rrrr',r'Price & Policy lower & Optimal upper & Node gap',rows,
      r'Lower endpoints are rounded downward and upper bounds upward. Differences are computed from exact dyadic endpoint fractions, not from the displayed decimals. Every original adapted control is covered by the upper bound; every lower bound belongs to its identified stored time-control policy. The exact all-price envelope is computed from unrounded endpoints and expenditure intervals.')
    finals=[r for r in read('inventory/summary.json') if r['step']==1000];rows=[]
    for d in [4,8,16,32,64,128]:
        vals=[next(v['total_regret_upper'] for v in r['dimensions'] if v['d']==d) for r in finals]
        rows.append([d,up(min(vals),8),up(max(vals),8)])
    table('inventory_dimension_table','Inventory total policy-loss bounds across state dimension','tab:suppinventorydimension','rrr',r'States & Smallest final bound & Largest final bound',rows,
      r'The range is over all ten prescribed final checkpoints, not a selected training result. These are total loss bounds. The initial region scales as $|x_0|^2/d\leq1$; the full diffusion is state-global. Every dimension reuses the same gain functions and invariant-mode proof, so these rows are not six independent training/verification cost measurements.')
    # Reconstruct all intermediate exact envelopes from retained generation order.
    # This is deterministic postprocessing, not a new fit or a selection change.
    root=P.parents[1];sys.path.insert(0,str(root/'revisions/2026-09-22-r14/replication'))
    from exact_price_audit import audit
    by_k={Fraction(r['k']):r for r in read('fresh_library/nodes.json')};prefix=[];history=[]
    for a in read('fresh_library/attempts.json'):
        if a['status']!='completed':continue
        prefix.append(by_k[Fraction(a['k_rational'])])
        if len(prefix)>=2:
            e=audit(sorted(prefix,key=lambda r:r['k']));history.append({'iteration':a['iteration'],'new_k_rational':a['k_rational'],'envelope':e})
    assert history[-1]['envelope']['uniform_regret_rational']==read('fresh_library/envelope.json')['uniform_regret_rational']
    (R/'fresh_library/envelope_history.json').write_text(json.dumps({'origin':'exact reconstruction from retained generated nodes and attempt order; no refitting','history':history},indent=2)+'\n')
