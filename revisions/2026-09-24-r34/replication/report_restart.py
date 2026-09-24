"""Generate outward-rounded restart tables from independently checked fractions."""
from pathlib import Path
from fractions import Fraction as F
import argparse,json,statistics
from report_global import write_table

def down(v,n=6):
    x=F(v); z=x.numerator*10**n//x.denominator
    return f'{z//10**n}.{z%10**n:0{n}d}'
def up(v,n=6):
    x=F(v); z=-(-x.numerator*10**n//x.denominator)
    return f'{z//10**n}.{z%10**n:0{n}d}'

def generate(root):
    out=root/'paper/generated';out.mkdir(parents=True,exist_ok=True);r=root/'results'
    ds=json.loads((r/'restart_closure.json').read_text());audit=json.loads((r/'restart_independent_audit.json').read_text());test=json.loads((r/'restart_tests.json').read_text())
    xs=ds['outcomes'];assert len(xs)==42 and not ds['failures'] and audit['passed'] and test['passed']
    rows=[]
    for T in (4,8,12):
        for ep in ('1/100','1/20'):
            rs=[x for x in xs if x['T']==T and x['epsilon']==ep]
            pos=[F(x['integrated_improvement']) for x in rs if F(x['integrated_improvement'])>0]
            gain='0' if not pos else down(min(pos))+'--'+up(max(pos))
            rows.append([str(T),str(float(F(ep))),f'{len(pos)}/7',gain,
                         f"{statistics.median(x['construction_seconds']+x['internal_check_seconds']+x['serialization_seconds'] for x in rs):.3f}",str(max(x['max_stored_closure_pieces'] for x in rs))])
    write_table(out/'restart_summary.tex','Tightening the global cost interval with the same certified deployments','tab:restart-summary',
                r'$T$ & $\varepsilon$ & Tightened & Positive gain & Added (s) & Max. pieces',rows,
                'Every row contains the same seven installed rules. Gain is the increase in the integrated cost lower bound, and therefore the decrease in the excess-cost bound; displayed range endpoints are rounded outwards. Added time is the median construction, internal verification, and serialization time, excluding the separately timed read-only final audit. No additional unrestricted support problem is solved. Max. pieces refers to the stored propagated lower bound, not all intermediate overlays. Positive counts are exact, including gains below display precision.')
    names={'occupancy_stress':'Stress','defer':'Defer','spline33':'Spline 33','spline129':'Spline 129','neural31001':'NN 31001','neural31002':'NN 31002','neural31003':'NN 31003'}
    ss=['\\begingroup\\footnotesize','\\setlength{\\tabcolsep}{3pt}',
        '\\begin{longtable}{rrlrrrrr}',
        '\\caption{All restart-propagated cost intervals}\\label{tab:restart-all}\\\\',
        '\\toprule $T$ & $\\varepsilon$ & Installed & Old lower & New lower & Upper & New gap & Gain \\\\ \\midrule',
        '\\endfirsthead','\\toprule $T$ & $\\varepsilon$ & Installed & Old lower & New lower & Upper & New gap & Gain \\\\ \\midrule','\\endhead']
    for x in xs:ss.append(' & '.join([str(x['T']),str(float(F(x['epsilon']))),names[x['proposal']],down(x['old_global_lower']),down(x['new_global_lower']),up(x['upper_cost']),up(x['new_global_gap']),down(x['integrated_improvement'])])+' \\\\')
    ss+=['\\bottomrule','\\end{longtable}','\\endgroup',
         'Lower bounds and gains are rounded downward; upper costs and excess-cost bounds are rounded upward. Exact fractions and all knot values are retained in the machine-readable certificates. The upper deployment is unchanged. A printed zero gain can conceal a positive gain smaller than $10^{-6}$; exact positivity is recorded in the summary.']
    (out/'restart_all.tex').write_text('\n'.join(ss)+'\n')
    pos=[x for x in xs if F(x['integrated_improvement'])>0];best=max(xs,key=lambda x:F(x['integrated_improvement']))
    nonzero=[x for x in xs if F(x['old_global_gap'])>0]
    data={'passed':True,'cases':len(xs),'strictly_tightened':len(pos),'unchanged':len(xs)-len(pos),
          'zero_global_gap':sum(F(x['new_global_gap'])==0 for x in xs),
          'newly_closed_positive_gaps':sum(F(x['old_global_gap'])>0 and F(x['new_global_gap'])==0 for x in xs),
          'minimum_positive_improvement':str(min(F(x['integrated_improvement']) for x in pos)),
          'maximum_improvement':best['integrated_improvement'],
          'max_relative_gap_reduction':str(max(F(x['integrated_improvement'])/F(x['old_global_gap']) for x in nonzero)),
          'strongest_case':{k:best[k] for k in ('T','proposal','epsilon','old_global_lower','new_global_lower','upper_cost','old_global_gap','new_global_gap','integrated_improvement')},
          'additional_support_solves':sum(x['extra_support_solves'] for x in xs),
          'construction_internal_check_serialization_seconds':sum(x[k] for x in xs for k in ('construction_seconds','internal_check_seconds','serialization_seconds')),
          'independent_closure_seconds':audit['closure_only_seconds'],'independent_full_audit_seconds':audit['whole_seconds'],
          'max_stored_closure_pieces':max(x['max_stored_closure_pieces'] for x in xs),
          'max_local_function_pieces':max(x['max_local_function_pieces'] for x in xs),
          'max_bits':max(x['max_bits'] for x in xs),
          'uncompressed_bytes':sum(x['uncompressed_bytes'] for x in xs),
          'compressed_bytes':sum(x['compressed_bytes'] for x in xs),
          'total_independent_certificates':audit['total_certificates'],
          'rejected_closure_mutations':len(audit['mutation_rejections']),
          'tests':test}
    (r/'restart_summary.json').write_text(json.dumps(data,indent=2,sort_keys=True))
    percent=100*float(F(data['max_relative_gap_reduction']))
    macros={'RestartTightened':str(len(pos)),'RestartUnchanged':str(len(xs)-len(pos)),
            'RestartMaxGain':up(best['integrated_improvement']),
            'RestartMaxPercent':f'{percent:.2f}',
            'RestartOldLower':down(best['old_global_lower']),'RestartNewLower':down(best['new_global_lower']),
            'RestartUpper':up(best['upper_cost']),'RestartOldGap':up(best['old_global_gap']),'RestartNewGap':up(best['new_global_gap']),
            'RestartBestHorizon':str(best['T']),'RestartBestEpsilon':str(float(F(best['epsilon']))),
            'RestartBestProposal':names[best['proposal']],
            'RestartConstructionSeconds':f"{data['construction_internal_check_serialization_seconds']:.3f}",
            'RestartAuditSeconds':f"{data['independent_closure_seconds']:.3f}",
            'RestartFullAuditSeconds':f"{data['independent_full_audit_seconds']:.3f}",
            'RestartMaxPieces':str(data['max_stored_closure_pieces']),'RestartMaxBits':str(data['max_bits']),
            'RestartCompressedMiB':f"{data['compressed_bytes']/2**20:.3f}",
            'RestartTreeFeasible':str(test['restart_feasible_deterministic_plans']),
            'RestartMixtureFeasible':str(test['restart_feasible_equal_mixtures'])}
    (out/'restart_macros.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+v+'}' for k,v in macros.items())+'\n')
    print(json.dumps(data,indent=2))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);args=ap.parse_args();generate(args.root)
