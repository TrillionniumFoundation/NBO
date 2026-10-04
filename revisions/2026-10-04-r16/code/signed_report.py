"""Complete source-bound R16 signed Bellman report; all signs are retained."""
from __future__ import annotations
import argparse
from decimal import Decimal,ROUND_CEILING,ROUND_FLOOR,localcontext
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'revisions/2026-10-04-r15/code'))
import costate_bridge as bridge
from method_statistics import ConfidenceBudget
from signed_pipeline import read,write,sha,digest,canonical,require,validate_protocol,bank
I,pc=bridge.I,bridge.pc


def number(value,digits=6,side=None):
    with localcontext() as c:
        c.prec=60;x=Decimal.from_float(float(value))
        if side:x=x.quantize(Decimal(10)**-digits,rounding=ROUND_FLOOR if side=='lower' else ROUND_CEILING)
        return f'{x:.{digits}f}'


def average_upper(values):
    return bridge.iu(pc.mean_i(I(np.asarray(values,dtype=float))))


def pooled_interval(rows,arrays,key,event_alpha):
    lo=[];hi=[];tails=[];centers=[];radii=[];raw=[];clipped=0
    for row,a in zip(rows,arrays):
        frozen=row['frozen_constants'];g=row['frozen_G_range']
        if key=='M':center=0.;radius=frozen['M_bound'];tail=frozen['M_tail']
        elif key=='C':center=frozen['C_center'];radius=frozen['C_bound'];tail=frozen['C_tail']
        else:center=g['clip_center'];radius=g['clip_radius'];tail=g['clipping_expectation_allowance']
        centers.append(center);radii.append(radius);tails.append(tail);raw.append(a[key])
        # The shift is enclosed outward, then the unknown exact observation
        # is projected onto its own predeclared centered clipping interval.
        left=(I(a[key+'_lower'])-I(center)).lo;right=(I(a[key+'_upper'])-I(center)).hi
        lo.append(np.clip(left,-radius,radius));hi.append(np.clip(right,-radius,radius))
        clipped+=int(np.sum((a[key]<center-radius)|(a[key]>center+radius)))
    require(len(set(centers))==1,'pooled clipping center differs between fixed streams')
    ans=bridge.interval_empirical_bernstein(np.concatenate(lo),np.concatenate(hi),bound=max(radii),event_alpha=event_alpha,clipping_tail=average_upper(tails))
    center=centers[0]
    ans['lower']=bridge.il(I(ans['lower'])+I(center));ans['upper']=bridge.iu(I(ans['upper'])+I(center))
    ans['mean']=float(ans['mean']+center);ans['clipped_mean']=float(ans['clipped_mean']+center)
    ans.update(clip_center=center,clip_radius=max(radii),range_lower=bridge.il(I(center)-I(max(radii))),range_upper=bridge.iu(I(center)+I(max(radii))),
        raw_descriptive_mean=float(np.concatenate(raw).mean()),clipped_paths=clipped,
        stream_count=len(rows),paths_per_stream=len(raw[0]),scope='Complete finite uniform distribution of selected original NBO streams; independent fresh occupation paths and future banks.')
    return ans


def table(caption,label,cols,header,rows,notes):
    return ('\\begin{table}[!htbp]\n\\centering\n\\footnotesize\n\\caption{'+caption+'}\\label{'+label+'}\n'
        +'\\begin{tabular}{'+cols+'}\n\\toprule\n'+header+r' \\'+'\n\\midrule\n'+'\n'.join(rows)
        +'\n\\bottomrule\n\\end{tabular}\n\\begin{minipage}{0.97\\linewidth}\\footnotesize\n\\emph{Notes:} '+notes
        +'\n\\end{minipage}\n\\end{table}\n')


def render(repo,results,out):
    repo=Path(repo).resolve();results=Path(results).resolve();out=Path(out).resolve()
    r16=repo/'revisions/2026-10-04-r16';protocol=r16/'protocols/signed_mechanism.json'
    p=read(protocol);cand=read(repo/p['candidate_inventory']);validate_protocol(p,cand)
    frozen=read(repo/p['signed_constants']);require(sha(repo/p['signed_constants'])==p['signed_constants_sha256'],'frozen constants hash mismatch')
    found={}
    for f in sorted(results.rglob('RESULT.json')):
        row=read(f);ident=row['trial_id'];require(ident not in found,'duplicate signed record')
        require(row['complete'] and row['method_id']=='nbo' and row['protocol_sha256']==sha(protocol),'incomplete signed assessment')
        require(row['paths']==1024 and row['steps']==2048 and row['antithetic_pairs']==2 and row['future_paths_per_bridge']==4,'registered precision changed')
        expected=next(c for c in cand['files'] if c['trial_id']==ident)
        require(row['checkpoint_sha256']==row['selected_checkpoint_sha256']==expected['sha256'],'original candidate changed')
        noise,key=bank(p,row['dimension'],row['stream_seed']);require(row['noise_seed']==noise and row['noise_key']==key,'not the registered new bank')
        require(row['frozen_constants']==frozen['trials'][ident] and row['frozen_G_range']==frozen['dimensions'][str(row['dimension'])],'frozen scientific allowance changed')
        raw=f.parent/row['raw_path'];require(sha(raw)==row['raw_sha256'],'raw signed evidence hash mismatch')
        a=np.load(raw,allow_pickle=False)
        for key in ['M','C','G']:
            require(a[key].shape==(1024,) and np.all(a[key+'_lower']<=a[key]) and np.all(a[key]<=a[key+'_upper']),'invalid interval sample arrays')
            require(np.isfinite(a[key+'_lower']).all() and np.isfinite(a[key+'_upper']).all(),'nonfinite raw evidence')
        require(a['terminal_a'].shape==a['terminal_pi'].shape==(4,1024,row['dimension']),'incomplete future endpoint bank')
        # G is built independently from stage plus the protected scalar
        # endpoint difference, and C is its interval difference from M.
        exactG=2048*(I(a['stage_lower'],a['stage_upper'])+I(a['future_difference_lower'],a['future_difference_upper']))
        require(np.array_equal(exactG.lo,a['G_lower']) and np.array_equal(exactG.hi,a['G_upper']),'joint G arithmetic identity changed')
        exactC=I(a['M_lower'],a['M_upper'])-exactG
        require(np.array_equal(exactC.lo,a['C_lower']) and np.array_equal(exactC.hi,a['C_upper']),'signed C arithmetic identity changed')
        work=read(f.parent/'WORK.json');require(work['complete'] and work['returncode']==0,'missing complete additional assessment work')
        found[ident]=(row,a,work,sha(f))
    require(set(found)=={r['trial_id'] for r in cand['files']},'all 32 original NBO streams required')
    sources={v[0]['numerical_source_commit'] for v in found.values()};fingerprints={v[0]['assessment_fingerprint'] for v in found.values()}
    require(len(sources)==len(fingerprints)==1,'mixed frozen numerical source or assessment')
    budget=ConfidenceBudget(.01,6)
    report=dict(record_type='Complete prospective signed occupation Bellman evidence',complete=True,policy_executions=32,total_bridges=32768,
        numerical_source_commit=next(iter(sources)),candidate_source_commit=p['candidate_source_commit'],candidate_evidence_commit=p['candidate_evidence_commit'],
        assessment_fingerprint=next(iter(fingerprints)),protocol_sha256=sha(protocol),constants_sha256=sha(repo/p['signed_constants']),confidence=budget.as_dict(),dimensions={},
        historical_mechanism_unchanged=True,interpretation='A positive signed occupation account validates the selected NBO policy mechanism identity. Critic-versus-Raw risk and incremental value require their distinct comparisons.')
    fullrows=[];gainrows=[];workrows=[];statements=[]
    for d in [10,50]:
        items=[found[f'd{d}_s{s}'] for s in p['design']['seeds']];rows=[z[0] for z in items];arrays=[z[1] for z in items];workers=[z[2] for z in items]
        intervals={key:pooled_interval(rows,arrays,key,budget.event_alpha) for key in ['M','C','G']}
        reprs={key:average_upper([r['frozen_constants'][key+'_representation'] for r in rows]) for key in ['M','C','G']}
        finite={key:dict(lower=bridge.il(I(intervals[key]['lower'])-I(reprs[key])),upper=bridge.iu(I(intervals[key]['upper'])+I(reprs[key]))) for key in ['M','C','G']}
        hold=average_upper([r['frozen_constants']['holding_deficit'] for r in rows]);transfer=average_upper([r['frozen_constants']['payoff_transfer'] for r in rows])
        lower=bridge.il(I(finite['G']['lower'])-I(hold)-I(transfer))
        upper=bridge.iu(I(finite['G']['upper'])+I(transfer))
        work=dict(complete_process_seconds=sum(w['end_to_end_seconds'] for w in workers),cpu_seconds=sum(w['cpu_seconds'] for w in workers),peak_rss_kib=max(w['peak_rss_kib'] for w in workers),
            reference_endpoint_transitions=sum(r['counters']['reference_endpoint_transitions'] for r in rows),candidate_transitions=sum(r['counters']['candidate_simulator_transitions'] for r in rows),
            assessment_only=True)
        result=dict(dimension=d,stream_count=16,bridges_per_stream=1024,total_bridges=16384,intervals=intervals,representation_allowances=reprs,
            finite_grid_intervals=finite,holding_deficit_upper=hold,paired_payoff_transfer_upper=transfer,
            continuous_gain_lower=lower,continuous_gain_upper=upper,positive_gain_verified=lower>0,primary_target_attained=lower>=.0005,secondary_target_attained=lower>=.001,
            critic_risk_ranking='not an estimand of this signed assessment',work=work,record_hashes={r['trial_id']:z[3] for r,z in zip(rows,items)},raw_hashes={r['trial_id']:r['raw_sha256'] for r in rows})
        report['dimensions'][str(d)]=result
        gainrows.append(' & '.join([str(d),number(intervals['M']['raw_descriptive_mean']),number(intervals['C']['raw_descriptive_mean']),number(finite['G']['lower'],side='lower'),number(bridge.iu(I(hold)+I(transfer)),side='upper'),number(lower,side='lower')])+r' \\')
        for key in ['M','C','G']:
            ci=intervals[key]
            fullrows.append(' & '.join([str(d),'$'+key+'$',number(ci['raw_descriptive_mean'],7),number(finite[key]['lower'],7,'lower'),number(finite[key]['upper'],7,'upper'),number(ci['clip_radius'],6,'upper'),number(ci['sample_moment_arithmetic_cushion'],8,'upper')])+r' \\')
        workrows.append(' & '.join([str(d),number(work['complete_process_seconds'],2),number(work['cpu_seconds'],2),number(work['peak_rss_kib']/1024,1),f"{work['reference_endpoint_transitions']:,}"])+r' \\')
        if lower>0:statements.append(f'In dimension {d}, the signed occupation account certifies a continuous-economy gain of at least '+number(lower,6,'lower')+'.')
        else:statements.append(f'In dimension {d}, the signed occupation lower endpoint is '+number(lower,6,'lower')+'; this sufficient account does not certify a positive gain.')
    out.mkdir(parents=True,exist_ok=True);write(out/'REPORT.json',report)
    outputs={}
    def save(name,text):
        (out/name).write_text(text);outputs[name]=sha(out/name)
    save('table_signed_main.tex',table('A Fresh Signed Bellman Mechanism Account','tab:r16signedmain','rrrrrr',r'$d$ & $M$ mean & $C$ mean & $L_G$ & Hold/transfer & Economy lower',gainrows,
        r'Each dimension fully enumerates the original sixteen selected NBO streams, with 1,024 independent occupation bridges per stream. One bank of two antithetic pairs supplies the common-noise continuation endpoints. The fitted scalar continuation cancels in $G=M-C$ before inference. All six two-sided $(d,M,C,G)$ statements share a new familywise error probability of $0.01$. The finite lower endpoint includes numerical sample and prefix-representation allowances. The final column additionally retains the original holding deficit and full continuous-payoff transfer. This result does not rank the critic against Raw.'))
    save('table_signed_full.tex',table('Every Signed Bellman Interval and Numerical Account','tab:r16signedfull','rlrrrrr',r'$d$ & Statistic & Mean & Lower & Upper & Clip radius & Arithmetic',fullrows,
        r'All six registered intervals appear, including inconclusive correction intervals. Endpoints include the additional shared-prefix representation allowance. The centered clipping intervals are fixed before new confirmation and can be asymmetric about zero. The arithmetic column is the interval-sample mean and standard-deviation perturbation allowance, not an empirical population range. Every endpoint is rounded outward.'))
    save('table_signed_work.tex',table('Additional Work for the Fresh Signed Assessment','tab:r16signedwork','rrrrr',r'$d$ & Process seconds & CPU seconds & Peak MiB & Endpoint updates',workrows,
        r'Process and CPU times sum all sixteen fresh processes per dimension; memory is their maximum. The clock includes imports, original weight reload, constants, candidate occupation paths, paired future paths, interval arithmetic and durable evidence. These are additional scientific assessment costs and do not alter the original method work-to-target records.'))
    save('signed_main.tex',r'''\subsection{A prospective signed occupation account}
\label{sec:r16signedevidence}
The new assessment evaluates every original selected NBO policy on fresh
occupation paths. Its proof, clipping interval, confidence family, and 1,024
bridges per stream were fixed before the new bank was drawn. The paired
continuation calculation uses the same innovations at the candidate and
reference action endpoints. It evaluates the signed continuation correction
and applies Proposition~\ref{prop:r16signedbridge} directly to their joint
Bellman gain, rather than subtracting separately estimated endpoints.

\input{revisions/2026-10-04-r16/results/signed_mechanism/report/table_signed_main.tex}

'''+ '\n\n'.join(statements)+r'''

The original negative Cauchy--Schwarz mechanism bounds remain part of the
record. The present calculation changes the sufficient error account and uses
an independently frozen confirmation bank. Its positive endpoints, when
obtained, concern the occupation Bellman identity of the returned policy.
They do not establish lower prediction risk than Raw or identify a unique
incremental contribution of the learned critic. The separate common-data
method comparison addresses that question.
''')
    save('signed_supplement.tex',r'''\subsection{Complete fresh signed mechanism evidence}
\label{app:r16signedrecord}
\input{revisions/2026-10-04-r16/results/signed_mechanism/report/table_signed_full.tex}
\input{revisions/2026-10-04-r16/results/signed_mechanism/report/table_signed_work.tex}
''')
    write(out/'REPORT_MANIFEST.json',dict(complete=True,numerical_source_commit=report['numerical_source_commit'],protocol_sha256=sha(protocol),report_sha256=sha(out/'REPORT.json'),tex_files=outputs,
        input_raw_hashes={ident:row[0]['raw_sha256'] for ident,row in sorted(found.items())},report_source_sha256=sha(__file__),no_favorable_sign_gate=True))
    return dict(complete=True,policy_executions=32,confidence_events=6,lower={d:r['continuous_gain_lower'] for d,r in report['dimensions'].items()})


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,required=True);p.add_argument('--results',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    print(json.dumps(render(**vars(p.parse_args())),indent=2,allow_nan=False))

if __name__=='__main__':main()
