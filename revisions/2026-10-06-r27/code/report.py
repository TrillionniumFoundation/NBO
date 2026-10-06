"""Prespecified deterministic summaries; no refitting or clock replacement."""
from pathlib import Path
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING
import hashlib
import json
import math
import sys
import numpy as np
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
sys.path.insert(0,str(ROOT/'revisions/2026-10-05-r23/code'))
from policy_certificate import Ball,up,down,positive_sum,gamma


def rounded_bound(x, direction, places=None):
    value=Decimal.from_float(float(x))
    quantum=Decimal('0.000001') if places==6 else Decimal(1).scaleb(value.adjusted()-2)
    return str(value.quantize(quantum,rounding=direction))


def summarize():
    root=R/'results/primary'
    rows=[json.loads(x) for x in (root/'services.jsonl').read_text().splitlines()]
    groups=[];intervals={};hashes=0
    for row in rows:
        if 'candidate_sha256' not in row:continue
        p=root/(row['key']+'.npz')
        assert hashlib.sha256(p.read_bytes()).hexdigest()==row['candidate_sha256']
        hashes+=1
        if row['family']!='entropic' or row['status']!='certified':continue
        with np.load(p) as z:
            d=row['dimension'];v=(-Ball.exact(z['gains'][0]))@Ball.exact(np.ones(d))
            center=float(np.mean(v.c))
            error=float(up((positive_sum(v.r)+gamma(2*d+2)*positive_sum(np.abs(v.c)))/d))
            r=float(np.min(np.diag(z['R'][0])))
        radius=float(up(math.sqrt(float(up(row['certificate']['policy_gap_upper']/float(down(d*r)))))))
        intervals[row['key']]=[float(down(center-error-radius)),float(up(center+error+radius))]
    for family in ('primitive','entropic'):
      for d in (10,50):
       methods=('NBO-primitive','structural') if family=='primitive' else ('NBO','structural')
       for method in methods:
        selected=[x for x in rows if x['family']==family and x['dimension']==d and x['method']==method]
        certified=[x for x in selected if x['status']=='certified']
        groups.append(dict(family=family,dimension=d,method=method,services=len(selected),certified=len(certified),
            mean_service_seconds=sum(x['complete_service_seconds'] for x in selected)/len(selected),
            maximum_policy_gap_upper=max((x['certificate']['policy_gap_upper'] for x in certified),default=None),
            minimum_domain_margin=min((x['certificate'].get('minimum_domain_margin',1.) for x in certified),default=None),
            hidden_updates=sum(x.get('counters',{}).get('hidden_updates',0) for x in selected),
            gram_checks=sum(x.get('counters',{}).get('gram_checks',0) for x in selected),
            candidate_bytes=sum(x.get('candidate_bytes',0) for x in selected)))
    contrasts=[]
    for d in (10,50):
     for regime in ('anchor','technology','valuation'):
      for method in ('NBO','structural'):
       for risk in (2.,4.):
        keys=[f'entropic_d{d}_{regime}_risk{v:g}_{method}' for v in (0.,risk)]
        if not all(k in intervals for k in keys):
            contrasts.append(dict(dimension=d,regime=regime,method=method,risk_per_dimension=risk,status='unresolved'));continue
        base,changed=[intervals[k] for k in keys]
        lo=float(down(changed[0]-base[1]));hi=float(up(changed[1]-base[0]))
        contrasts.append(dict(dimension=d,regime=regime,method=method,risk_per_dimension=risk,
                              lower=lo,upper=hi,status='negative' if hi<0 else ('positive' if lo>0 else 'unresolved')))
    out=dict(groups=groups,contrasts=contrasts,candidate_hashes_verified=hashes,
             interpretation='Complete deterministic catalogue and prespecified risk responses, not population confidence intervals')
    (R/'results/SUMMARY_TABLES.json').write_text(json.dumps(out,indent=2)+'\n')
    lines=[r'\begin{table}[htbp]\centering\small',r'\caption{Source-frozen full-policy services}\label{tab:r27services}',
           r'\begin{tabular}{llrrrr}\toprule',r'Family and dimension & Method & Passed & Seconds & Gap bound & Domain \\ \midrule']
    for g in groups:
        family=('Additive' if g['family']=='primitive' else 'Recursive')+f", $d={g['dimension']}$"
        name='NBO' if g['method'].startswith('NBO') else 'Structural'
        bound='--' if g['maximum_policy_gap_upper'] is None else rounded_bound(g['maximum_policy_gap_upper'],ROUND_CEILING)
        domain='--' if g['family']=='primitive' else str(Decimal.from_float(g['minimum_domain_margin']).quantize(Decimal('.001'),rounding=ROUND_FLOOR))
        lines.append(f"{family} & {name} & {g['certified']}/{g['services']} & {g['mean_service_seconds']:.3f} & {bound} & {domain} \\\\")
    lines += [r'\bottomrule\end{tabular}',r'\par\smallskip\parbox{0.97\linewidth}{\footnotesize Seconds include allocation, fitting, all inner checks, policy verification, candidate compression and durable candidate/attempt writes. Closing service-ledger writes and common startup are recorded as whole-job overhead. The bound is the maximum certified lifetime gap in the group; the domain entry is its smallest verified exponential-moment margin. Every failed service remains in the denominator. Certificate columns are rounded outward.}',r'\end{table}']
    (R/'results/services_main.tex').write_text('\n'.join(lines)+'\n')
    lines=[r'\begin{table}[htbp]\centering\small',r'\caption{Optimal current-action responses to recursive risk preferences}\label{tab:r27riskresponses}',
           r'\begin{tabular}{rlrr}\toprule',r'Dimension & Future regime & Lower endpoint & Upper endpoint \\ \midrule']
    for c in contrasts:
        if c['method']!='NBO' or c['risk_per_dimension']!=4.:continue
        if 'lower' in c:lines.append(f"{c['dimension']} & {c['regime'].capitalize()} & {rounded_bound(c['lower'],ROUND_FLOOR,6)} & {rounded_bound(c['upper'],ROUND_CEILING,6)} \\\\")
        else:lines.append(f"{c['dimension']} & {c['regime'].capitalize()} & -- & -- \\\\")
    lines += [r'\bottomrule\end{tabular}',r'\par\smallskip\parbox{0.97\linewidth}{\footnotesize Change in the mean optimal current adjustment at $x_0=\mathbf 1$ when $\theta/d$ rises from zero to four. Every future policy is reoptimized. These are outward deterministic bands obtained from NBO policy certificates, not sampling confidence intervals. Both prespecified risk changes and both candidate generators are reported in the complete record.}',r'\end{table}']
    (R/'results/risk_responses_main.tex').write_text('\n'.join(lines)+'\n')
    print(json.dumps(out,indent=2),flush=True)


if __name__=='__main__':summarize()
