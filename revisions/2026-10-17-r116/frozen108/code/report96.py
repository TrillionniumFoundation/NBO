"""Generate only source-bound R96 tables from actual retained outcomes."""
import argparse,hashlib,json,math,pathlib,statistics
ROOT=pathlib.Path(__file__).resolve().parents[1]
ARMS=('online-risk-dp','quadratic','relu','spline')
LABEL={'online-risk-dp':'Online risk-DP','quadratic':'Quadratic','relu':'ReLU','spline':'Adaptive spline'}

def main(tag):
    path=ROOT/f'results96/evaluation-{tag}/RESULTS96.json';data=json.loads(path.read_text())
    frozen=json.loads((ROOT/'results96/FREEZE96.json').read_text())
    tables=ROOT/'tables';tables.mkdir(exist_ok=True)
    header='% Source commit: '+data['source_commit']+'; freeze SHA-256: '+data['freeze_sha256']+'\n'
    output=header+r'''\begin{table}[htbp]
\caption{New-stream complete services at the original-optimum target}\label{tab:services96}
\centering\small
\begin{tabular}{l l r r r r}\toprule
Risk & Service & \shortstack{Mean cost\\midpoint} & \shortstack{Mean numerical\\width} & \shortstack{Maximum\\loss} & \shortstack{Rejected\\proposals}\\
\midrule
'''
    for index,level in data['levels'].items():
        for arm in ARMS:
            a=level['arms'][arm];lo,hi=a['mean_cost']
            output+=f"{level['alpha']:.2f} & {LABEL[arm]} & {(lo+hi)/2:.7f} & {hi-lo:.7f} & {a['maximum_loss']:.7f} & {a['rejected_proposals']} \\\\\n"
    output+=r'''\bottomrule\end{tabular}
\par\smallskip\parbox{.97\linewidth}{\footnotesize Each row has 4,096 independent initial states, paired across services. Mean cost uncertainty here is numerical, not a sampling interval. Rejected first proposals receive the separately paid conventional fallback; their original actions and loss bounds remain in the raw data. The target distribution is the declared 20-bit dyadic initial law, with continuous innovations.}
\end{table}
'''
    pairs=[]
    output+=r'''\begingroup\small\setlength{\tabcolsep}{3pt}
\begin{longtable}{@{}l p{.24\linewidth} r r r@{}}
\caption{All prespecified paired mean-cost comparisons}\label{tab:pairs96}\\
\toprule Risk & Left minus right & \shortstack{Paired\\midpoint} & \shortstack{Numerical\\half-width} & \shortstack{Simultaneous\\interval}\\
\midrule\endfirsthead
\toprule Risk & Left minus right & \shortstack{Paired\\midpoint} & \shortstack{Numerical\\half-width} & \shortstack{Simultaneous\\interval}\\
\midrule\endhead
'''
    for level in data['levels'].values():
        for name,p in level['pairs'].items():
            left,right=name.split(' minus ');lo,hi=p['interval'];pairs.append(p)
            output+=f"{level['alpha']:.2f} & {LABEL[left]} minus {LABEL[right]} & {p['midpoint']:.7f} & {p['numerical_half_width']:.7f} & $[{lo:.7f},{hi:.7f}]$ \\\\\n"
    output+=r'''\bottomrule\end{longtable}\endgroup
\noindent The sampling radius is the predeclared $1/4096$ for every contrast; the family has coverage at least 95 percent. The exact comparison margin is $1/1280$, and the code rounds it inward when classifying a contrast.
'''
    equivalent=sum(p['equivalent'] for p in pairs);superior=sum(p['left_superior'] or p['right_superior'] for p in pairs)
    maxhalf=max(p['half_width'] for p in pairs);rejections=sum(a['rejected_proposals'] for l in data['levels'].values() for a in l['arms'].values());exact=sum(a['exact_fallbacks'] for l in data['levels'].values() for a in l['arms'].values())
    output+=f"\nThe retained execution contains 32,768 arm--state records. Of the twelve fixed contrasts, {equivalent} establish equivalence at the declared margin and {superior} exclude zero. The largest simultaneous half-width is {maxhalf:.8f}. There are {rejections} rejected first proposals and {exact} entries to the final exact fallback. These counts refer to the new complete services, not the historical R95 actors.\n"
    (tables/'outcomes96.tex').write_text(output)
    timing_path=ROOT/'results96/timing/TIMING96.json'
    extra=header
    if timing_path.exists():
        timing=json.loads(timing_path.read_text());records=timing['records']
        extra+=r'''\begin{table}[htbp]
\caption{Fresh-process workload times, including startup and shutdown}\label{tab:timing96}
\centering\small\begin{tabular}{l l r r}\toprule
Risk & Service & Median seconds & Observed range\\
\midrule
'''
        scenarios=[]
        for index in range(2):
            baseline=[r['complete_process_seconds'] for r in records if r['index']==index and r['arm']=='online-risk-dp']
            for arm in ARMS:
                v=[r['complete_process_seconds'] for r in records if r['index']==index and r['arm']==arm]
                if len(v)!=5:raise ValueError('Incomplete timing family')
                extra+=f"{(.5,.75)[index]:.2f} & {LABEL[arm]} & {statistics.median(v):.5f} & $[{min(v):.5f},{max(v):.5f}]$ \\\\\n"
                if arm!='online-risk-dp':
                    rec=frozen['levels'][str(index)];m=rec['models'][arm]
                    k=rec['labels']['seconds']+m['construction']['seconds']+m['cover_work']['seconds']+m['serialization_reload_seconds']+rec['calibration'][arm]['seconds']
                    saving=min(baseline)-max(v)
                    scenarios.append(dict(index=index,arm=arm,measured_model_acquisition_seconds=k,
                        observed_lower_saving_seconds=saving,conditional_workload_break_even=math.ceil(k/saving) if saving>0 else None,
                        scope='Descriptive timing-envelope scenario, without independent campaign audit cost or additional service fees; those must be added explicitly. Not a future-runtime confidence bound.'))
        extra+=r'''\bottomrule\end{tabular}
\par\smallskip\parbox{.97\linewidth}{\footnotesize Five fresh processes per arm--risk pair on the same fixed 32-state workload. CPU frequency is recorded, not controlled. Ranges are descriptive, not confidence intervals for other workloads or hardware. Primary evaluation has a different, larger sample and is not timed by scaling these rows.}
\end{table}
'''
        (ROOT/'results96/REUSE_SCENARIOS96.json').write_text(json.dumps(scenarios,indent=2)+'\n')
    extra+=r'''\begin{table}[htbp]
\caption{Matched construction and its paid components}\label{tab:prepare96}
\centering\small\begin{tabular}{l l r r r r}\toprule
Risk & Representation & \shortstack{Design\\rank} & \shortstack{Active\\nonlinear} & \shortstack{Search\\seconds} & \shortstack{Cover\\seconds}\\
\midrule
'''
    for index,lev in frozen['levels'].items():
        for arm in ARMS[1:]:
            m=lev['models'][arm];rec=m['fit_record']
            extra+=f"{lev['alpha']:.2f} & {LABEL[arm]} & {rec['effective_design_rank']} & {rec['active_nonlinear_coefficients']} & {m['construction']['seconds']:.5f} & {m['cover_work']['seconds']:.5f} \\\\\n"
    extra+=r'''\bottomrule\end{tabular}
\par\smallskip\parbox{.97\linewidth}{\footnotesize Every executable model uses 128 bytes. The full record additionally reports common-label construction, each calibration, serialization/reload, condition numbers, every candidate solver call, and process memory. The table columns are components, not an assertion that they sum to the entire preparation campaign. The independent endpoint audit is a separate paid campaign.}
\end{table}
'''
    (tables/'work96.tex').write_text(extra)
    identity=dict(source_commit=data['source_commit'],freeze_sha256=data['freeze_sha256'],input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (tables/'outcomes96.tex',tables/'work96.tex')},counts=dict(equivalent=equivalent,strict_contrasts=superior,maximum_half_width=maxhalf,rejected_proposals=rejections,exact_fallbacks=exact))
    (ROOT/'results96/TABLES96.json').write_text(json.dumps(identity,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tag',default='primary');main(p.parse_args().tag)
