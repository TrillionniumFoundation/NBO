"""Replay every deterministic cell record, independently of summary counts."""
from pathlib import Path
import csv, gzip, hashlib, json, math
import study52 as st
R=Path(__file__).resolve().parents[1]
def main():
    st.verify();execution=json.loads((R/'audit/EXECUTION52.json').read_text())
    for n,h in execution['files'].items():
        if st.sha(R/n)!=h:raise AssertionError('Evidence hash mismatch: '+n)
    records=[];total=0
    for spec in st.catalogue():
        folder=R/'results52'/spec['key'];rec=json.loads((folder/'record.json').read_text())
        if rec['input']!=spec or rec['cell_sha256']!=st.sha(folder/rec['cell_file']):raise AssertionError('Input or cell hash')
        counts={M:dict(scalar=0,contrast=0,scalar_blocked=0,contrast_blocked=0,equal=0) for M in st.AMPLITUDES}
        maximum=None
        with gzip.open(folder/rec['cell_file'],'rt') as f:
            for k,row in enumerate(csv.DictReader(f)):
                i,j=int(row['i']),int(row['j'])
                if (i,j)!=divmod(k,256):raise AssertionError('Missing or duplicate cell')
                b,v,n=(int(row[z]) for z in ('base','proposal','contrast'))
                lo,hi=(float.fromhex(row[z]) for z in ('lower_hex','upper_hex'))
                if not math.isfinite(lo) or not math.isfinite(hi) or lo>hi:raise AssertionError('Interval validity')
                cap=(4096*(512+i+j))//4096
                if not all(0<=a<=cap for a in (b,v,n)):raise AssertionError('Cell feasibility')
                if n!=(v if hi<=0 else b):raise AssertionError('Contrast gate mismatch')
                if n!=b:maximum=hi if maximum is None else max(maximum,hi)
                for M in st.AMPLITUDES:
                    allowed=(st.I(hi,hi)+st.o.s.c.rat_i(st.o.BETA*st.F(2*M))).hi<=0 if M else hi<=0
                    scalar=int(row[f'scalar_M{M}'])
                    if scalar!=(v if allowed else b):raise AssertionError('Scalar gate mismatch')
                    c=counts[M];c['scalar']+=scalar!=b;c['contrast']+=n!=b
                    c['scalar_blocked']+=(b!=v and scalar==b);c['contrast_blocked']+=(b!=v and n==b);c['equal']+=b==v
        if k+1!=65536:raise AssertionError('Incomplete grid')
        total+=k+1
        for row in rec['amplitudes']:
            c=counts[row['M']]
            for key,z in [('scalar_strict_changes','scalar'),('contrast_strict_changes','contrast'),('scalar_blocked_changes','scalar_blocked'),('contrast_blocked_changes','contrast_blocked'),('equal_proposals','equal')]:
                if row[key]!=c[z]:raise AssertionError((spec['key'],key))
        if maximum!=rec['maximum_accepted_true_cost_upper'] or (maximum is not None and maximum>0):raise AssertionError('Unsafe accepted contrast')
        if rec['through_cells_fsync_seconds']<rec['construction_seconds'] or rec['serialization_seconds']<0:raise AssertionError('Clock ordering')
        records.append(rec)
    if total!=524288:raise AssertionError('Incomplete catalogue')
    rows=[]
    for r in records:
        a=r['amplitudes'];rows.append({'key':r['key'],'T':r['T'],'price':r['price'],
          'scalar_changes':[v['scalar_strict_changes'] for v in a],
          'contrast_changes':a[0]['contrast_strict_changes'],'blocked':a[0]['contrast_blocked_changes'],
          'seconds':r['through_cells_fsync_seconds'],'peak_rss_mib':r['peak_rss_kib']/1024,
          'maximum_accepted_upper':r['maximum_accepted_true_cost_upper']})
    report={'status':'passed','services':8,'all_cells_replayed':total,'amplitude_gate_decisions':total*8,
            'all_feasible':True,'all_accepted_upper_bounds_nonpositive':True,
            'contrast_policies_identical_to_inherited':True,'new_independent_cost_estimands':0,
            'summary':rows,'execution_sha256':st.sha(R/'audit/EXECUTION52.json')}
    st.save(R/'audit/RESULT_AUDIT52.json',report)
    text=[r'\begin{table}[htbp]',r'\caption{Exhaustive action-null robustness on the original investment economy}',r'\label{tab:robustness52}',r'\centering\small',r'\begin{tabular}{lrrrrrr}',r'\toprule',r'Incumbent & $T$ & $p$ & $M=0$ & $M=1$ & $M=16$ & $M=4096$ \\',r'\midrule']
    for r in rows:
        name='Witness' if r['key'].startswith('compiled') else 'FVI'
        text.append(f"{name} & {r['T']} & {r['price']} & "+' & '.join(map(str,r['scalar_changes']))+r' \\')
    text += [r'\bottomrule',r'\end{tabular}',r'\parbox{0.96\textwidth}{\footnotesize Each row enumerates all 65,536 closed eight-bit cells. Entries count strict changes accepted by the global-width gate. The contrast-aware gate accepts exactly the $M=0$ column at every amplitude, with identical returned actions. Earlier policy dates are unchanged. Counts concern cells, not additional expected-cost observations.}',r'\end{table}']
    (R/'tables/robustness52.tex').write_text('\n'.join(text)+'\n')
    work=[r'\begin{table}[htbp]',r'\caption{Complete robustness-service work and memory}',r'\label{tab:work52}',r'\centering\small',r'\begin{tabular}{lrrrr}',r'\toprule',r'Incumbent & $T$ & $p$ & Seconds & Peak MiB \\',r'\midrule']
    for r in rows:
        name='Witness' if r['key'].startswith('compiled') else 'FVI'
        work.append(f"{name} & {r['T']} & {r['price']} & {r['seconds']:.2f} & {r['peak_rss_mib']:.1f}"+r' \\')
    work += [r'\bottomrule',r'\end{tabular}',r'\parbox{0.96\textwidth}{\footnotesize Each isolated service loads a frozen incumbent, computes all proposals and centered intervals, independently replays the inherited terminal gate, evaluates every amplitude gate, and durably serializes the cell records. Process startup is excluded; inherited construction time is not added. These are verification-service clocks, not a work-to-policy-cost superiority claim.}',r'\end{table}']
    (R/'tables/work52.tex').write_text('\n'.join(work)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
