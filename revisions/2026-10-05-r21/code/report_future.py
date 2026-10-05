"""Lossless, deterministic publication tables for the frozen R20 experiment."""
from __future__ import annotations
import json,hashlib,math
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
from pathlib import Path
from collections import defaultdict
from audit_future import records,f,R
import torch

LABELS={'NBO-reuse':'NBO, reuse only','NBO-adaptive':'NBO, check and refresh','NBO-refit':'NBO, refit each future','quadratic-adaptive':'Quadratic, check and refresh','rbf-adaptive':'RBF, check and refresh','SAA':'Cached SAA','enumerated':'Full-support enumeration'}
def interval_text(lo,hi,digits=7):
    unit=Decimal(1).scaleb(-digits)
    a=Decimal.from_float(float(lo)).quantize(unit,rounding=ROUND_FLOOR)
    b=Decimal.from_float(float(hi)).quantize(unit,rounding=ROUND_CEILING)
    return f'$[{a:.{digits}f},{b:.{digits}f}]$'
def scientific(v):
    a,b=f'{v:.2e}'.split('e');return a+r'\times10^{'+str(int(b))+'}'
def write(name,text):
    (R/'results/generated'/name).write_text(text.strip()+'\n')
def table(caption,label,cols,header,rows,note):
    return '\\begin{table}[htbp]\\centering\\small\n\\caption{'+caption+'}\\label{'+label+'}\n\\begin{tabular}{'+cols+'}\\toprule\n'+header+'\\\\ \\midrule\n'+'\n'.join(x+r'\\' for x in rows)+'\n\\bottomrule\\end{tabular}\n\\par\\smallskip\\begin{minipage}{.98\\textwidth}\\footnotesize '+note+'\\end{minipage}\n\\end{table}\n'
def main():
    rr=records();group=defaultdict(list)
    for x in rr:group[x['service']].append(x)
    summary=[];tab=[]
    for m in f.SERVICES:
        x=group[m];gs=[g for r in x for g in r['regimes']]
        passed=sum(r['all_regimes_certified'] for r in x);reg=sum(g['certified'] for g in gs)
        refresh=sum(a['kind']=='refresh' for g in gs for a in g['attempts'])
        upper=max(g['attempts'][-1]['certificate']['mean_regret_upper'] for g in gs)
        row={'service':m,'complete_services':len(x),'all_futures_certified':passed,'certified_regimes':reg,'refreshes':refresh,'largest_final_mean_regret_bound':upper}
        summary.append(row);tab.append(f"{LABELS[m]} & {passed}/24 & {reg}/120 & {refresh} & ${scientific(upper)}$")
    write('future_accuracy.tex',table('Accuracy after changes in future economic primitives','tab:r21accuracy','lrrrr','Procedure & Complete & Futures & Refreshes & Largest bound',tab,'A complete service contains all five futures. A successful future is certified against the full scalar interval at mean loss at most $10^{-4}$. A failed certificate is not a proof that the actual loss exceeds the tolerance. There are no execution exceptions. These are the original frozen outcomes, not new observations.'))
    cells=[];tab=[]
    for d in (10,50):
        for q in f.VOLUMES:
            sub=[r for r in rr if r['dimension']==d and r['queries_per_regime']==q]
            costs={m:sum(x['accounted_service_seconds'] for x in sub if x['service']==m)/3 for m in f.SERVICES}
            cells.append({'dimension':d,'queries_per_future':q,'costs':costs})
            tab.append(f'{d} & {q:,} & '+' & '.join(f'{costs[m]:.3f}' for m in f.SERVICES))
    write('future_costs.tex',table('Recorded work for a five-future service (seconds)','tab:r21cost','rr'+'r'*7,'$d$ & $q$ & Reuse & Adapt & Refit & Quad & RBF & SAA & Enum',tab,'Columns follow Table~\\ref{tab:r21accuracy}. Each cell is the arithmetic mean of three actually executed services, with $5q$ decisions per service. Costs include initialization, anchor fitting when used, all attempted fitting, queries, failed and successful checks, and charged durable writes. Reuse-only has unresolved futures and is not an accuracy-qualified winner. Common startup, post-stop diagnostics and the complete comparison remain separately recorded; no clock is replaced by a fitted line.'))
    econ=[];tab=[]
    for d in (10,50):
        exact=next(r for r in rr if r['dimension']==d and r['queries_per_regime']==1024 and r['service']=='enumerated' and r['stream']==200501)
        for g in exact['regimes']:
            h=g['economic_certificate'];a=h['mean_optimal_action'];z=h['mean_withdrawal_reduction_due_to_charge']
            econ.append({'dimension':d,'future':g['regime'],'mean_optimal_action':a,'mean_charge_reduction':z})
            tag={'anchor':'Anchor','future_withdrawal_low':'Lower future withdrawal','future_withdrawal_high':'Higher future withdrawal','future_production':'Higher future production','future_utility':'Higher future payoff weight'}[g['regime']]
            tab.append(f'{d} & {tag} & {interval_text(*a)} & {interval_text(*z)}')
    write('future_economics.tex',table('Certified current withdrawals and charge responses','tab:r21economic','@{}rlcc@{}','$d$ & Future & Mean optimal withdrawal & Reduction due to charge',tab,'The 1,024-task catalogue is fixed in each dimension. Intervals enclose the finite-law optimizers, not a population mean. Endpoints are rounded outwards. The zero-charge comparison holds the future and every other task primitive fixed. Enumeration gives the same deterministic target in every stream; one identical certificate is printed rather than treating duplicates as observations.'))
    contrasts=[];tab=[]
    for d in (10,50):
        for name in ['future_production','future_utility']:
            bands=[]
            for row in [r for r in rr if r['dimension']==d and r['queries_per_regime']==1024 and r['service']=='NBO-adaptive']:
                y,t=f.tasks(1024,d,200700+d);gg={g['regime']:g for g in row['regimes']}
                def band(g):
                    item=g['attempts'][-1];a=torch.tensor(item['actions'],dtype=torch.float64)
                    return f.optimal_action_interval(a,t,item['certificate'])
                b=(band(gg[name])-band(gg['anchor'])).mean();bands.append([float(b.lo),float(b.hi)])
            lo=min(b[0] for b in bands);hi=max(b[1] for b in bands)
            assert hi<0
            contrasts.append({'dimension':d,'future':name,'envelope_over_three_NBO_streams':[lo,hi]})
            tab.append(f"{d} & {'Production' if name=='future_production' else 'Payoff weight'} & {interval_text(lo,hi,6)}")
    write('future_nbo_contrasts.tex',table('Economic contrasts certified from NBO decisions','tab:r21nbocontrasts','rlc','$d$ & Future change & Mean optimal withdrawal minus anchor',tab,'Each band uses only the final NBO actions and their true-objective derivative/curvature certificates. It encloses the true optimum response over the common 1,024 tasks. The printed band is the envelope of the three stream-specific bands, not an inferential interval over training randomness. All four upper endpoints are negative.'))
    # Long-form appendix retains every service, including cheap unresolved ones.
    lines=[r'\section{Complete Future-Change Service Record}\label{app:r21record}',r'\small',r'\begin{longtable}{rrrlrrrr}',r'\caption{All frozen future-change services}\label{tab:r21all}\\',r'\toprule $d$ & $q$ & Stream & Procedure & Seconds & Futures & Attempts & Bound\\\midrule\endfirsthead',r'\toprule $d$ & $q$ & Stream & Procedure & Seconds & Futures & Attempts & Bound\\\midrule\endhead',r'\bottomrule\endfoot']
    short={'NBO-reuse':'Reuse','NBO-adaptive':'Adapt','NBO-refit':'Refit','quadratic-adaptive':'Quad','rbf-adaptive':'RBF','SAA':'SAA','enumerated':'Enum'}
    compact=[]
    for r in rr:
        gs=r['regimes'];bound=max(g['attempts'][-1]['certificate']['mean_regret_upper'] for g in gs)
        count=sum(g['certified'] for g in gs);attempts=sum(len(g['attempts']) for g in gs)
        lines.append(f"{r['dimension']} & {r['queries_per_regime']} & {r['stream']} & {short[r['service']]} & {r['accounted_service_seconds']:.3f} & {count}/5 & {attempts} & ${scientific(bound)}$"+r'\\')
        compact.append({k:r[k] for k in ['dimension','queries_per_regime','stream','service','accounted_service_seconds','all_regimes_certified']})
    lines += [r'\end{longtable}\normalsize',r'\subsection{Mechanism and complete work components}',r'The following finite-law diagnostics average the same fixed tasks and streams within each method and future. Absolute prediction risk, action-centered risk, and own-action risk are distinct from decision loss. Every stored per-service field remains available in the original execution records.',r'\small\begin{longtable}{rllrrrr}',r'\caption{Common-action and own-action prediction diagnostics}\label{tab:r21risk}\\',r'\toprule $d$ & Procedure & Future & Absolute & Centered & Own action & Menu loss\\\midrule\endfirsthead',r'\toprule $d$ & Procedure & Future & Absolute & Centered & Own action & Menu loss\\\midrule\endhead',r'\bottomrule\endfoot']
    risks=[]
    for d in (10,50):
        for m in f.SERVICES:
            for regime in f.REGIMES:
                gs=[g for r in rr if r['dimension']==d and r['queries_per_regime']==1024 and r['service']==m for g in r['regimes'] if g['regime']==regime[0]]
                fields=['absolute_risk','centered_risk','own_action_risk','three_action_loss']
                vals={k:sum(g['mechanism'][k] for g in gs)/3 for k in fields}
                risks.append({'dimension':d,'service':m,'future':regime[0],**vals})
                tag={'anchor':'Anchor','future_withdrawal_low':'Low','future_withdrawal_high':'High','future_production':'Production','future_utility':'Utility'}[regime[0]]
                lines.append(f'{d} & {short[m]} & {tag} & '+' & '.join(f'${scientific(vals[k])}$' for k in fields)+r'\\')
    lines += [r'\end{longtable}\normalsize']
    write('future_record.tex','\n'.join(lines))
    meta=json.loads((R/'protocols/FUTURE_EXECUTION_METADATA.json').read_text())
    total=sum(r['accounted_service_seconds'] for r in rr);diagnostic=sum(r['diagnostic_seconds'] for r in rr)
    report={'services':168,'regime_outcomes':840,'source_execution':meta['environment'],'service_summary':summary,'work_cells':cells,'economic_intervals':econ,'nbo_economic_contrasts':contrasts,'risk_rows':risks,'all_services':compact,'sum_accounted_service_seconds':total,'sum_post_stop_diagnostic_seconds':diagnostic,'original_full_comparative_seconds':meta['full_comparative_seconds'],'analysis_type':'post-freeze deterministic integration; original clocks and all service records retained'}
    (R/'results/FUTURE_TABLES.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'service_seconds':total,'diagnostics':diagnostic,'complete':meta['full_comparative_seconds'],'nbo_contrasts':contrasts},indent=2))
if __name__=='__main__':main()
