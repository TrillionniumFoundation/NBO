"""Deterministic R72 publication tables from completed, independently checked records."""
from pathlib import Path
import json,statistics,hashlib
R=Path(__file__).resolve().parents[1]
MODE={'none':'Fresh','exact':'Exact','geometric':'Geometric'}
TASK={'scalar-d2-T2':'S2/2','scalar-d8-T3':'S8/3','vector-d2-T2':'V2/2','vector-d2-T3':'V2/3','vector-d2-T4':'V2/4'}
def save(name,text):
    if any(ord(x)<32 and x not in '\t\n\r' for x in text):raise AssertionError('Nonprintable LaTeX')
    p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def table(name,caption,label,heads,rows,note,columns,wide=False):
    if wide:
        text='\\begingroup\\small\\setlength{\\tabcolsep}{3pt}\n\\begin{longtable}{'+columns+'}\n\\caption{'+caption+'}\\label{'+label+'}\\\\\n\\hline\n'+' & '.join(heads)+r' \\'+'\n\\hline\\endfirsthead\n\\hline\n'+' & '.join(heads)+r' \\'+'\n\\hline\\endhead\n'
        text+='\n'.join(' & '.join(map(str,x))+r' \\' for x in rows)+'\n\\hline\n\\end{longtable}\\endgroup\n{\\footnotesize '+note+'}\n'
    else:
        text='\\begin{table}[htbp]\n\\centering\n\\caption{'+caption+'}\\label{'+label+'}\n{\\small\\setlength{\\tabcolsep}{4pt}\n\\begin{tabular}{'+columns+'}\n\\hline\n'+' & '.join(heads)+r' \\'+'\n\\hline\n'
        text+='\n'.join(' & '.join(map(str,x))+r' \\' for x in rows)+'\n\\hline\n\\end{tabular}}\n\\par\\smallskip\n{\\footnotesize '+note+'}\n\\end{table}\n'
    save('tables/'+name+'.tex',text)
def main():
    a=json.loads((R/'audit/INDEPENDENT72.json').read_text());need=a['services']+a['failed_services']
    if a['status']!='passed' or need!=36:raise AssertionError('Incomplete catalogue')
    groups=[];rows=[]
    for task in TASK:
        for mode in MODE:
            values=[x for x in a['rows'] if x['task']==task and x['mode']==mode]
            if not values:
                rows.append([TASK[task],MODE[mode],'--','--','--','failed']);continue
            q=[x['q_queries'] for x in values];hits=[x['hits'] for x in values];fills=[x['fills'] for x in values]
            if len(set(q))!=1 or len(set(hits))!=1 or len(set(fills))!=1:raise AssertionError('Nonidentical operation repetitions require an explicit range')
            s=[x['complete_seconds'] for x in values]
            rows.append([TASK[task],MODE[mode],fills[0],hits[0],f'{q[0]:,}',f'{statistics.median(s):.3f}'])
            groups.append(dict(task=task,mode=mode,repetitions=len(values),q_queries=q[0],fills=fills[0],hits=hits[0],geometric_hits=values[0]['geometric_hits'],seconds=s,median_seconds=statistics.median(s)))
    table('reuse-summary72','Complete original-law query workloads with and without reuse','tab:reuse-summary72',
          ['Task','Rule','Fills','Hits','Bellman queries','Seconds'],rows,
          'S and V denote scalar and two-control tasks; numbers are state dimension and horizon. Queries include every recursive descendant. Seconds are medians of complete processes: three repetitions for S2/2, S8/3 and V2/2, two for V2/3, and one stress observation for V2/4. All prescribed records are retained. These are localized workload comparisons, not population policy-cost samples.','llrrrr')
    rows=[]
    for x in a['rows']:
        if x['task']=='vector-d2-T4':
            folder=R/'results72'/f"{x['task']}-{x['mode']}-r{x['rep']}";s=json.loads((folder/'summary.json').read_text())
            rows.append([MODE[x['mode']],f"{s['blocks'][0]['additional_q_queries']:,}",f"{x['q_queries']:,}",f"{x['complete_seconds']:.3f}",f"{x['peak_rss_kib']:,}"])
    table('horizon72','Four-date, two-control first-fill and complete workload account','tab:horizon72',
          ['Rule','First-fill queries','All queries','Seconds','RSS (KiB)'],rows,
          'Four requested root states, two independent innovations, and common local tolerance $512/14911$. The first-fill column counts its full descendant tree. Exact reuse recognizes identical states; geometric reuse additionally transfers a valid witness to a nearby state. RSS is total process peak memory, not logical cache bytes. One repetition is descriptive only.','lrrrr')
    rows=[['Prescribed complete processes',36],['Returned / failed',f"{a['services']} / {a['failed_services']}"],['Checked root returns',a['checked_query_returns']],['Checked reuse returns',a['checked_transport_returns']],['Different-state reuse returns',a['checked_geometric_returns']],['Repaired-action reuse returns',a['capacity_repairs']],['Independent exact neuron integrals',a['exact_conditional_integrals']],['New independent policy-cost rows',0]]
    table('audit-summary72','Independent checks of the new operations','tab:audit-summary72',
          ['Quantity','Count'],rows,
          'The checker imports no production numerical kernel. It verifies each new transfer against a prior paid fill and independently integrates each rational neuron on the original innovation support. It does not independently regenerate the internal optimal-value trees of inherited fills.','lr')
    rows=[];ops=[]
    for x in a['rows']:
        folder=R/'results72'/f"{x['task']}-{x['mode']}-r{x['rep']}";s=json.loads((folder/'summary.json').read_text());c=s['cache_counts']
        rows.append([TASK[x['task']],MODE[x['mode']],x['rep']+1,f"{x['complete_seconds']:.6f}",f"{x['q_queries']:,}",x['hits'],f"{x['peak_rss_kib']:,}"])
        ops.append([TASK[x['task']],MODE[x['mode']],x['rep']+1,c['checks'],c['max_records'],c['rejected_stale_records'],f"{c['fill_seconds']:.4f}",f"{c['lookup_seconds']:.4f}"])
    table('repetition-ledger72','Every new complete-process repetition','tab:repetition-ledger72',
          ['Task','Rule','Rep.','Seconds','Queries','Hits','RSS'],rows,
          'Each row is one separately launched and completed process. No clock repetition is a new fitting seed or an independent policy-cost observation. All stage and source identities remain in its receipt.','llrrrrr',True)
    table('operation-ledger72','Paid fills, rejected records and lookup overhead','tab:operation-ledger72',
          ['Task','Rule','Rep.','Checks','Stored','Stale','Fill (s)','Lookup (s)'],ops,
          'Stored is the maximum number of retained witnesses. Stale counts discarded records at the declared context invalidation. Fill and lookup are internal subclocks, not the complete process boundary. The lookup account includes record-load validation. Repeated storage, hashing, output and shutdown are additionally included in complete receipts.','llrrrrrr',True)
    ratios=[]
    for task in TASK:
        ns=next(x for x in groups if x['task']==task and x['mode']=='none')
        gs=next(x for x in groups if x['task']==task and x['mode']=='geometric')
        ratios.append(dict(task=task,query_reduction=1-gs['q_queries']/ns['q_queries'],median_complete_seconds_ratio=gs['median_seconds']/ns['median_seconds']))
    out=dict(status='passed',groups=groups,comparisons=ratios,independent_audit_sha256=hashlib.sha256((R/'audit/INDEPENDENT72.json').read_bytes()).hexdigest(),scope='descriptive complete-process observations under the frozen localized workload; no timing confidence interval or new independent policy-cost observation')
    save('audit/TABLES72.json',json.dumps(out,sort_keys=True,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
