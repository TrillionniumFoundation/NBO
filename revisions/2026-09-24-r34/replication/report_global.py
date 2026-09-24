"""Generate every R34 table directly from checked exact rational outputs."""
from pathlib import Path
from fractions import Fraction as F
import argparse, json, statistics, hashlib


def write_table(path,caption,label,header,rows,note):
    n=header.count('&')+1
    text='\\begin{table}[htbp]\n\\centering\\footnotesize\n'
    text+=f'\\caption{{{caption}}}\\label{{{label}}}\n'
    text+='\\begin{tabular}{'+'r'*n+'}\\toprule\n'+header+' \\\\\\midrule\n'
    text+='\n'.join(' & '.join(r)+' \\\\' for r in rows)
    text+='\n\\bottomrule\\end{tabular}\n\\par\\smallskip\\begin{minipage}{.98\\textwidth}\\footnotesize '+note+'\\end{minipage}\n\\end{table}\n'
    path.write_text(text)


def generate(root:Path):
    results=root/'results';out=root/'paper/generated';out.mkdir(parents=True,exist_ok=True)
    datasets=[json.loads((results/f'H{T}.json').read_text()) for T in (4,8,12)]
    audit=json.loads((results/'independent_audit.json').read_text());assert audit['passed']
    cases=[x for d in datasets for x in d['outcomes']];supports=[s for d in datasets for s in d['supports']]
    assert len(cases)==42 and all(x['certified'] and x['preservation_certified'] for x in cases)
    neural=[x for x in cases if x['proposal'].startswith('neural')]
    assert len(neural)==18 and all(F(x['saving_vs_class'])>0 for x in neural)
    f=lambda x:float(F(x));fmt=lambda x:f'{f(x):.6f}'
    rows=[]
    for T in (4,8,12):
        for eps in ('1/100','1/20'):
            rs=[x for x in neural if x['T']==T and x['epsilon']==eps]
            saves=[f(x['saving_vs_class']) for x in rs];pct=[100*f(x['saving_vs_class'])/f(x['class_cost']) for x in rs];gaps=[f(x['global_cost_gap']) for x in rs]
            rows.append([str(T),str(f(eps)),'3/3',f'{min(saves):.4f}--{max(saves):.4f}',f'{min(pct):.2f}--{max(pct):.2f}',f'{min(gaps):.4f}--{max(gaps):.4f}'])
    write_table(out/'global_neural.tex','Positive-cost improvements and global uncertainty for installed neural rules','tab:global-neural',
                '$T$ & $\\varepsilon$ & Improved & Cost saved & Saved (\\%) & Global gap',rows,
                'Ranges cover the three fixed installed seeds, not new independent replications. Cost saved compares the selected globally feasible portfolio policy with the freshly reconstructed local-class minimum. The last column is the certified upper bound on excess cost relative to the unrestricted constrained optimum, not relative to that class. All 18 operating-preservation checks pass. Normalized intervention units; uniform initial distribution.')
    rows=[]
    for d in datasets:
        cs=d['outcomes'];ss=d['supports'];T=d['horizon']
        rows.append([str(T),f"{statistics.median(x['total_installed_seconds_including_fresh_class_construction'] for x in cs):.3f}",
                     f"{statistics.median(x['fresh_class_baseline_seconds'] for x in cs):.3f}",
                     str(max(max(x['max_support_pieces'],x['max_value_pieces']) for x in ss)),
                     str(max(x['max_bits'] for x in ss)),f"{d['peak_process_rss_kib']/1024:.1f}"])
    write_table(out/'global_work.tex','Charged portfolio construction and finite representation','tab:global-work',
                '$T$ & Portfolio (s) & Class (s) & Max. pieces & Max. bits & RSS (MiB)',rows,
                'Per-configuration medians across the complete seven-rule, two-budget cohort. Portfolio time includes witness construction, all eight support solves and evaluations, internal checks, exact lower-bound construction, encoding, and a freshly rebuilt class candidate. Class time is included in, not added to, portfolio time. The additional final read-only audit is recorded separately. Maxima cover stored support and own-value representations; they are not bounds on all intermediate overlays. RSS is peak process memory, not deployed-certificate memory. Installed proposal fitting is inherited and excluded from these incremental revision timings.')
    lines=['\\begingroup\\footnotesize','\\setlength{\\tabcolsep}{3pt}',
           '\\begin{longtable}{rrlrrrrr}','\\caption{Complete globally bounded portfolio; all 42 declared configurations}\\label{tab:global-all}\\\\',
           '\\toprule $T$ & $\\varepsilon$ & Installed & $\\lambda$ & Cost lower & Cost upper & Gap & Saved \\\\ \\midrule',
           '\\endfirsthead','\\toprule $T$ & $\\varepsilon$ & Installed & $\\lambda$ & Cost lower & Cost upper & Gap & Saved \\\\ \\midrule','\\endhead']
    names={'occupancy_stress':'Stress','defer':'Defer','spline33':'Spline 33','spline129':'Spline 129','neural31001':'NN 31001','neural31002':'NN 31002','neural31003':'NN 31003'}
    for x in cases:
        price=x['selected'] if x['selected']!='inherited_class' else 'Class'
        lines.append(' & '.join([str(x['T']),str(f(x['epsilon'])),names[x['proposal']],price,fmt(x['global_cost_lower']),fmt(x['cost_upper']),fmt(x['global_cost_gap']),fmt(x['saving_vs_class'])])+' \\\\')
    lines+=['\\bottomrule','\\end{longtable}','\\endgroup',
            'Displayed decimals are descriptive rounded summaries of exact rational bounds. The machine-readable fractions, not outward rounding of these printed decimals, define the certificates. ``Class'' denotes the freshly reconstructed local-class candidate. Saved cost is relative to that class, not a claim that a positive-cost deployment is globally optimal. The $12$ spline cases have identically zero cost and exact zero global gap. All selected deployments satisfy their original all-restart operating tolerance and separately preserve installed operating values.']
    (out/'global_all_cases.tex').write_text('\n'.join(lines)+'\n')
    # Nonduplicated work excludes diagnostic operating DP, which is separately
    # included below. Per-case times intentionally duplicate shared portfolios.
    unique=sum(d['witness']['total_constructive_input_seconds'] for d in datasets)
    unique+=sum(s[k] for s in supports for k in ('solve_seconds','evaluation_seconds','encoding_seconds','check_seconds'))
    unique+=sum(c[k] for c in cases for k in ('class_candidate_recheck_and_bound_construction_seconds','summary_check_seconds','summary_encoding_seconds'))
    summary={'cases':len(cases),'support_solves':len(supports),'new_class_baselines':42,'independent_certificates':audit['total_certificates'],
             'passed':sum(x['certified'] for x in cases),'preservation_passed':sum(x['preservation_certified'] for x in cases),
             'neural_cases':len(neural),'neural_strictly_lower_than_class':sum(F(x['saving_vs_class'])>0 for x in neural),
             'all_cases_strictly_lower_than_class':sum(F(x['saving_vs_class'])>0 for x in cases),
             'zero_global_gap':sum(F(x['global_cost_gap'])==0 for x in cases),
             'neural_saving_min':min(f(x['saving_vs_class']) for x in neural),'neural_saving_max':max(f(x['saving_vs_class']) for x in neural),
             'neural_saving_percent_min':min(100*f(x['saving_vs_class'])/f(x['class_cost']) for x in neural),
             'neural_saving_percent_max':max(100*f(x['saving_vs_class'])/f(x['class_cost']) for x in neural),
             'unique_measured_construction_and_internal_check_seconds':unique,'diagnostic_exact_operating_dp_seconds':sum(d['exact_operating_control']['seconds'] for d in datasets),
             'additional_independent_audit_seconds':audit['whole_audit_seconds'],
             'failures':[x for d in datasets for x in d['failures']],
             'scope':'Fixed installed proposals; no newly measured fitting time. Global gaps concern the unrestricted all-restart feasible set.',
             'max_stored_support_or_value_pieces':max(max(s['max_support_pieces'],s['max_value_pieces']) for s in supports),
             'max_support_integer_bits':max(s['max_bits'] for s in supports),
             'compressed_certificate_bytes':sum(p.stat().st_size for p in (results/'certificates').glob('*.json.gz')),
             'source_result_sha256':{f'H{d["horizon"]}.json':hashlib.sha256((results/f'H{d["horizon"]}.json').read_bytes()).hexdigest() for d in datasets}}
    (results/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True))
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);args=ap.parse_args();print(json.dumps(generate(args.root),indent=2))
