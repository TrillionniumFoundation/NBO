"""Replay all R15 finite-stream method accounts from complete worker evidence.

No training, checkpoint selection, alpha recycling, or seed deletion occurs.
The input is 128 RESULT/WORK records and their original confirmation NPZ arrays.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from method_statistics import (ConfidenceBudget, empirical_bernstein,
    finite_stream_mean, paired_difference, economic_decision,
    certified_attainment_fraction, work_distribution,
    audit_descriptive_decomposition, _mean_upper)

ROOT=Path(__file__).resolve().parents[3]
NAMES={'nbo':'NBO','raw_costate':'Raw','direct_policy':'Direct policy','neural_hjb':'Neural HJB'}


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')


def pick(record,*keys):
    for k in keys:
        if k in record:return record[k]
    raise ValueError('missing record field: '+ '/'.join(keys))


def allowance(c,key):
    aliases={'clip':('clip','clipping_threshold'),
             'bias':('bias','bias_upper'),
             'tail':('clipping_tail','clipping_bias'),
             'actor_bias':('actor_bias_upper',),
             'statistic_error':('statistic_error_upper','quadrature_and_statistic_roundoff')}
    sources=[c,c.get('constants',{})]
    for data in sources:
        for name in aliases[key]:
            if name in data:
                value=float(data[name])
                if not math.isfinite(value) or value<0:raise ValueError('invalid allowance '+name)
                return value
    if key=='clip' and isinstance(c.get('bound'),(int,float)):
        return float(c['bound'])
    raise ValueError('missing certified allowance '+key)


def contrast_allowances(left,right):
    """Cancellation requires TWO simulated policy-minus-reference statistics.

    An analytical fallback has an exact zero statistic. Subtracting it leaves
    the other policy's complete reference-relative transfer error in place.
    """
    ca,cb=left['constants'],right['constants']
    fa,fb=bool(left['record']['fallback']),bool(right['record']['fallback'])
    if fa and fb:
        return dict(clip=0.,bias=0.,tail=0.,transfer_case='both_exact_reference')
    if fa or fb:
        c=cb if fa else ca
        return dict(clip=c['clip'],bias=c['bias'],tail=c['tail'],
                    transfer_case='one_exact_reference_full_schedule_relative_transfer')
    terms=[ca['actor_bias'],cb['actor_bias'],ca['statistic_error'],cb['statistic_error'],1e-12]
    return dict(clip=math.nextafter(ca['clip']+cb['clip'],math.inf),
                bias=math.nextafter(_mean_upper(terms)*len(terms),math.inf),
                tail=math.nextafter(ca['tail']+cb['tail'],math.inf),
                transfer_case='two_simulated_policies_common_reference_cancelled')


def raw_file(c,trial_dir,results):
    value=Path(pick(c,'raw_path','raw_file'))
    candidates=[value] if value.is_absolute() else [trial_dir/value,results/value,ROOT/value]
    paths=[p for p in candidates if p.is_file()]
    if not paths:raise ValueError(f'confirmation array unavailable: {value}')
    identities={digest(p) for p in paths}
    if len(identities)>1:raise ValueError(f'ambiguous raw path: {value}')
    if c.get('raw_sha256') and c['raw_sha256']!=next(iter(identities)):
        raise ValueError('raw array SHA256 mismatch')
    return paths[0]


def normalize_identity(c,r,protocol):
    result={}
    aliases={'initial_profile_hash':('initial_profile_hash','initial_index_hash','initial_state_hash'),
             'initial_state_hash':('initial_state_hash',),
             'terminal_anchor_hash':('terminal_anchor_hash',),
             'noise_hash':('noise_hash','noise_sha256'),
             'steps':('steps',),'paths':('paths',),'stream_seed':('stream_seed','seed'),
             'confirmation_bank':('confirmation_bank',),'primitives_sha256':('primitives_sha256',)}
    for key,names in aliases.items():
        sources=[c,c.get('paired_identity',{}),r]
        vals=[data[n] for data in sources for n in names if n in data]
        if not vals:raise ValueError('missing paired identity '+key)
        result[key]=vals[0]
    if result['primitives_sha256']!=protocol['design']['primitives_sha256']:
        raise ValueError('confirmation primitives mismatch')
    return result


def fmt(x,digits=6):
    if x is None:return r'--'
    if isinstance(x,(int,np.integer)):return str(x)
    return f'{float(x):.{digits}f}'


def latex_table(path,caption,label,headers,rows,note,long=False):
    columns='l'+'r'*(len(headers)-1)
    if long:
        lines=[r'\begingroup\small',r'\begin{longtable}{'+columns+'}',r'\caption{'+caption+r'}\label{'+label+r'}\\',r'\toprule', ' & '.join(headers)+r' \\',r'\midrule',r'\endfirsthead',r'\toprule',' & '.join(headers)+r' \\',r'\midrule',r'\endhead']
    else:
        lines=[r'\begin{table}[!htbp]',r'\centering\small',r'\caption{'+caption+'}',r'\label{'+label+'}',r'\begin{tabular}{'+columns+'}',r'\toprule',' & '.join(headers)+r' \\',r'\midrule']
    lines += [' & '.join(str(v) for v in row)+r' \\' for row in rows]
    lines += [r'\bottomrule',r'\end{longtable}' if long else r'\end{tabular}']
    lines += [r'\par\medskip\noindent\footnotesize '+note]
    lines += [r'\endgroup' if long else r'\end{table}']
    Path(path).write_text('\n'.join(lines)+'\n')


def report(protocol_path,results,out):
    protocol_path=Path(protocol_path);results=Path(results);out=Path(out)
    p=json.loads(protocol_path.read_text());design=p['design'];seeds=design['seeds'];dims=design['dimensions'];methods=design['methods']
    if p['status']!='frozen_before_confirmatory_execution':raise ValueError('confirmatory protocol is not frozen')
    contrasts=p['confirmation']['direct_contrasts'];count=len(dims)*(len(methods)+len(contrasts))*(len(seeds)+1)
    if count!=p['inference']['method_confirmation_events']:raise ValueError('confidence event ledger differs from design')
    delta=ConfidenceBudget(p['inference']['alpha_allocation']['method_confirmation'],count).event_alpha
    protocol_hash=digest(protocol_path);primitive_hash=design['primitives_sha256']
    loaded={};source_hashes=set();records=[];work_records={};method_fingerprints={m:set() for m in methods}
    for d in dims:
        for seed in seeds:
            for m in methods:
                trial=results/f'd{d}_s{seed}'/m
                rpath,wpath=trial/'RESULT.json',trial/'WORK.json'
                if not rpath.is_file() or not wpath.is_file():raise ValueError(f'missing complete trial {d}/{seed}/{m}')
                r=json.loads(rpath.read_text());w=json.loads(wpath.read_text())
                if r.get('complete') is not True or w.get('complete') is not True:
                    raise ValueError('incomplete worker/result record')
                for key,expected in [('method_id',m),('dimension',d),('stream_seed',seed),('primitives_sha256',primitive_hash),('protocol_sha256',protocol_hash)]:
                    if r.get(key)!=expected:raise ValueError(f'trial identity mismatch {key}: {trial}')
                source=pick(r,'numerical_source_commit','source_commit','source')
                if not isinstance(source,str) or len(source)!=40:raise ValueError('missing full source commit')
                source_hashes.add(source)
                fingerprint=r.get('method_fingerprint')
                if not isinstance(fingerprint,str) or len(fingerprint)!=64:raise ValueError('missing algorithm fingerprint')
                method_fingerprints[m].add(fingerprint)
                c=r['final_confirmation'];identity=normalize_identity(c,r,p)
                if r.get('confirmation_independent_of_selection') is not True or c.get('confirmation_independent_of_selection') is not True:
                    raise ValueError('final bank is not certified independent of selection')
                if identity['paths']!=p['confirmation']['paths_per_seed'] or identity['steps']!=p['confirmation']['steps']:
                    raise ValueError('undeclared final path count or mesh')
                if identity['stream_seed']!=seed:raise ValueError('confirmation belongs to another stream')
                rp=raw_file(c,trial,results)
                with np.load(rp,allow_pickle=False) as bank:
                    arrays={k:bank[k].copy() for k in ['paired_gain','production','consumption_deficit','terminal_gain']}
                    if 'initial_profile' in bank:arrays['initial_profile']=bank['initial_profile'].copy()
                    if 'terminal_anchor' in bank:arrays['terminal_anchor']=bank['terminal_anchor'].copy()
                if len(arrays['paired_gain'])!=identity['paths']:raise ValueError('raw paths differ from manifest')
                constants={key:allowance(c,key) for key in ['clip','bias','tail','actor_bias','statistic_error']}
                if bool(r['fallback'])!=bool(c.get('analytic_schedule',False)):
                    raise ValueError('fallback/analytical-reference identities differ')
                if r['fallback'] and (np.count_nonzero(arrays['paired_gain']) or any(constants.values())):
                    raise ValueError('analytical fallback must carry exact zero gain and allowance')
                loaded[d,seed,m]=dict(record=r,work=w,identity=identity,arrays=arrays,constants=constants,raw_sha256=digest(rp))
                online=bool(r.get('attained_online',False))
                work_records[d,seed,m]=dict(actual_early_stopping_execution=r.get('actual_early_stopping_execution',False),attained=online,end_to_end_seconds=float(w['end_to_end_seconds']))
                records.append(dict(dimension=d,stream_seed=seed,method=m,result_sha256=digest(rpath),work_sha256=digest(wpath),raw_sha256=digest(rp),method_fingerprint=fingerprint,fallback=r.get('fallback'),attained_online=online))
    if len(source_hashes)!=1:raise ValueError('mixed generating source commits')
    if any(len(v)!=1 for v in method_fingerprints.values()):raise ValueError('mixed algorithm fingerprints within a method')
    # Confirm every common-stream identity before any endpoint is generated.
    for d in dims:
        for seed in seeds:
            reference=loaded[d,seed,methods[0]]
            for m in methods[1:]:
                z=loaded[d,seed,m]
                paired_difference(reference['arrays']['paired_gain'],z['arrays']['paired_gain'],left_identity=reference['identity'],right_identity=z['identity'])
                for key in ['initial_profile','terminal_anchor']:
                    if key in reference['arrays'] and key in z['arrays'] and not np.array_equal(reference['arrays'][key],z['arrays'][key]):
                        raise ValueError('common-path raw identity failed: '+key)
    endpoints=[];mixtures=[];attainment=[];work=[];decompositions=[];checkpoint_progress=[]
    endpoint_arrays={};endpoint_constants={};names=methods+[a+'__minus__'+b for a,b in contrasts]
    for d in dims:
        for seed in seeds:
            for m in methods:
                z=loaded[d,seed,m];c=z['constants']
                endpoint_arrays[d,seed,m]=z['arrays']['paired_gain']
                endpoint_constants[d,seed,m]=c
            for a,b in contrasts:
                za,zb=loaded[d,seed,a],loaded[d,seed,b];name=a+'__minus__'+b
                endpoint_arrays[d,seed,name]=paired_difference(za['arrays']['paired_gain'],zb['arrays']['paired_gain'],left_identity=za['identity'],right_identity=zb['identity'])
                endpoint_constants[d,seed,name]=contrast_allowances(za,zb)
            for name in names:
                c=endpoint_constants[d,seed,name]
                ci=empirical_bernstein(endpoint_arrays[d,seed,name],bound=c['clip'],bias=c['bias'],clipping_tail=c['tail'],event_alpha=delta)
                endpoints.append(dict(dimension=d,stream_seed=seed,endpoint=name,transfer_case=c.get('transfer_case','schedule_relative'),**ci))
        for name in names:
            c={s:endpoint_constants[d,s,name] for s in seeds}
            ci=finite_stream_mean({s:endpoint_arrays[d,s,name] for s in seeds},declared_seeds=seeds,
                noise_keys={s:loaded[d,s,methods[0]]['identity']['noise_hash'] for s in seeds},
                bounds={s:c[s]['clip'] for s in seeds},biases={s:c[s]['bias'] for s in seeds},
                clipping_tails={s:c[s]['tail'] for s in seeds},event_alpha=delta,confirmation_independent_of_selection=True)
            row=dict(dimension=d,endpoint=name,**ci)
            if '__minus__' in name:row['decision']=economic_decision(ci['lower'],ci['upper'],p['economic_decision']['equivalence_margin_payoff'])
            mixtures.append(row)
        for m in methods:
            intervals={e['stream_seed']:e for e in endpoints if e['dimension']==d and e['endpoint']==m}
            for target in [p['stopping']['primary_certified_gain_target'],p['stopping']['secondary_final_gain_target']]:
                attainment.append(dict(dimension=d,method=m,**certified_attainment_fraction(intervals,declared_seeds=seeds,target=target)))
            wr=work_distribution({s:work_records[d,s,m] for s in seeds},seeds,seconds_cap=p['work_accounting']['restricted_mean_wall_cap_seconds'])
            wr['dimension']=d;wr['method']=m
            wr['peak_rss_kib']=max(float(pick(loaded[d,s,m]['work'],'peak_rss_kib','max_rss_kib')) for s in seeds)
            # Worker `counters` ALREADY combines training and completed
            # verification. Adding verification_work again would double count.
            counters=[loaded[d,s,m]['record']['counters'] for s in seeds]
            keys=set().union(*(x.keys() for x in counters))
            means={}
            for key in keys:
                values=[float(a.get(key,0)) for a in counters]
                if not all(math.isfinite(v) and v>=0 for v in values):raise ValueError('invalid work counter')
                means[key]=sum(values)/len(values)
            wr['mean_work_counters']=means
            wr['complete_verification_counter_streams']=sum(loaded[d,s,m]['record']['verification_counters_complete'] for s in seeds)
            wr['mean_cpu_seconds']=sum(float(loaded[d,s,m]['work']['cpu_seconds']) for s in seeds)/len(seeds)
            wr['counter_scope']='Recorded training and completed-verification work proxies; complete parent-clock work includes all failures and I/O.'
            work.append(wr)
            decompositions.append(dict(dimension=d,method=m,**audit_descriptive_decomposition({s:loaded[d,s,m]['arrays'] for s in seeds},seeds)))
            for stage in range(1,p['stopping']['maximum_checkpoint_checks']+1):
                rows=[loaded[d,s,m]['record'] for s in seeds]
                checks=[c for row in rows for c in row['online_checks'] if c['stage']==stage]
                checkpoint_progress.append(dict(dimension=d,method=m,stage=stage,checks_attempted=len(checks),
                    checks_completed=sum(bool(c['complete']) for c in checks),
                    streams_certified_by_stage=sum(bool(row['attained_online']) and row.get('attainment_stage',10**9)<=stage for row in rows),
                    total_streams=len(seeds),scope='Observed actual online certificate history; no retrospective or fixed-budget payoff inference.'))
    if len(endpoints)+len(mixtures)!=count:raise AssertionError('reported event count differs from registered family')
    result=dict(status='complete',protocol_sha256=protocol_hash,source_commit=next(iter(source_hashes)),primitives_sha256=primitive_hash,
        trial_count=len(records),confidence=ConfidenceBudget(p['inference']['alpha_allocation']['method_confirmation'],count).as_dict(),
        seed_endpoints=endpoints,method_endpoints=mixtures,attainment=attainment,work=work,decomposition=decompositions,checkpoint_progress=checkpoint_progress,identity_records=records)
    out.mkdir(parents=True,exist_ok=True);write(out/'REPORT.json',result)
    generate_tables(result,p,out)
    return result


def generate_tables(r,p,out):
    mean_rows=[];direct_rows=[];work_rows=[];decomp_rows=[];seed_rows=[];operation_rows=[];progress_rows=[]
    for z in r['method_endpoints']:
        name=z['endpoint']
        if '__minus__' not in name:
            att=next(a for a in r['attainment'] if a['dimension']==z['dimension'] and a['method']==name and a['target']==p['stopping']['primary_certified_gain_target'])
            mean_rows.append([z['dimension'],NAMES[name],fmt(z['raw_mean']),fmt(z['lower']),fmt(z['upper']),f"{att['definitely_attaining']}/{att['seed_count']}"])
        else:
            comparator=name.split('__minus__')[1];decision=z['decision']
            status='Equivalent' if decision['practical_equivalence'] else 'Superior' if decision['economically_material_superiority'] else 'Inferior' if decision['economically_material_inferiority'] else 'Unresolved'
            direct_rows.append([z['dimension'],'NBO--'+NAMES[comparator],fmt(z['raw_mean']),fmt(z['lower']),fmt(z['upper']),status])
    for z in r['work']:
        work_rows.append([z['dimension'],NAMES[z['method']],f"{z['attained_count']}/{z['seed_count']}",fmt(z['mean_consumed_seconds'],2),fmt(z['median_time_to_target'],2),fmt(z['restricted_mean_time'],2),fmt(z['peak_rss_kib']/1024,1)])
        c=z['mean_work_counters']
        operation_rows.append([z['dimension'],NAMES[z['method']],fmt(c.get('simulator_transitions',0)/1e6,2),fmt(c.get('verification_transitions',0)/1e6,2),fmt(c.get('actor_updates',0),0),fmt(c.get('critic_updates',0),0),fmt(c.get('first_derivative_rows',0)/1e6,2),fmt(c.get('action_search_iterations',0)/1e6,2)])
    for z in r['checkpoint_progress']:
        progress_rows.append([z['dimension'],NAMES[z['method']],z['stage'],z['checks_attempted'],z['checks_completed'],f"{z['streams_certified_by_stage']}/{z['total_streams']}"])
    for z in r['decomposition']:
        a=z['method_means'];decomp_rows.append([z['dimension'],NAMES[z['method']]]+[fmt(a[k]) for k in ['production','consumption_contribution','terminal_dispersion_contribution','total_numerical_gain']])
    for z in r['seed_endpoints']:
        label=NAMES.get(z['endpoint'],z['endpoint'].replace('nbo__minus__','NBO--').replace('raw_costate','Raw').replace('direct_policy','Direct').replace('neural_hjb','HJB'))
        seed_rows.append([z['dimension'],z['stream_seed'],label,fmt(z['mean']),fmt(z['lower']),fmt(z['upper'])])
    latex_table(out/'table_method_summary.tex','Payoff of the finite-distribution computational methods','tab:r15methodmeans',
        ['$d$','Method','Mean gain','Lower','Upper','At least target'],mean_rows,
        'Means average all sixteen declared execution streams. Endpoints enclose continuous-time payoff gains on the analytical schedule. The last column counts streams whose simultaneous final lower endpoint attains 0.0005; it is a lower bound on attainment under the declared finite distribution. No stream is excluded.')
    latex_table(out/'table_method_comparisons.tex','Direct method comparisons at the declared economic margin','tab:r15methodcontrasts',
        ['$d$','Comparison','Mean','Lower','Upper','Decision'],direct_rows,
        r'Pathwise differences use common profiles and innovations within each stream. The equivalence margin is $10^{-4}$ payoff units. Superior and inferior refer to economic differences exceeding that margin. An unresolved comparison is not evidence of equivalence. The schedule transfer cancels between two simulated candidates; comparison with an exact analytical fallback retains the other candidate\textquotesingle s full schedule-relative transfer.')
    latex_table(out/'table_method_work.tex','Complete measured work of the stopping procedures','tab:r15methodwork',
        ['$d$','Method','Stopped','Mean (s)','Median (s)','Restricted (s)','MiB'],work_rows,
        'Stopped counts actual online certificates at the 0.0005 target. Mean is total consumed parent-clock time through independent final confirmation. Median is the lower 0.5 quantile of work to target, with failures assigned infinity; a dash denotes an unattained median. Restricted work is the mean of min(time to target,900 seconds), retaining failures at 900. Memory is the maximum fresh-worker peak resident size over streams. These clocks describe the recorded execution environment.')
    latex_table(out/'table_method_decomposition.tex','Descriptive decomposition of the numerical payoff gain','tab:r15methoddecomposition',
        ['$d$','Method','Production','Consumption','Dispersion','Total'],decomp_rows,
        'Entries are observed finite-step common-path contributions, averaged uniformly over the complete stream set. Consumption is minus the consumption deficit; dispersion is the terminal contribution. Their pathwise sum equals the numerical gain. No component continuous-time confidence interval or causal attribution is asserted; the separate total-payoff account remains authoritative.')
    latex_table(out/'table_method_operations.tex','Recorded operation counts of the complete stopping procedures','tab:r15methodoperations',
        ['$d$','Method','Train $10^6$','Verify $10^6$','Actor','Critic','Grad. $10^6$','Search $10^6$'],operation_rows,
        'Entries are means over all sixteen streams. Train and verify count simulator transitions; actor and critic count optimizer updates; grad. counts first-derivative rows; search counts action-search iterations, including HJB deployment. These are work proxies, not equivalent FLOPs. Full first- and second-derivative, forward, backward, and other counters are retained in the machine-readable report. The parent clock additionally includes every failed operation and all I/O.')
    latex_table(out/'table_method_checkpoint_progress.tex','Actual online certification by work checkpoint','tab:r15methodcheckpoints',
        ['$d$','Method','Checkpoint','Attempted','Completed','Certified by then'],progress_rows,
        'Every listed check was executed before the continuation or stopping decision. The last column counts all streams that had attained the primary 0.0005 lower-gain target by the checkpoint, retaining earlier stopped streams. Missing later checks represent actual stopping or recorded failures. This table does not infer an unexecuted fixed-budget payoff frontier.',long=True)
    latex_table(out/'table_method_seed_endpoints.tex','Every R15 stream payoff and direct contrast','tab:r15methodstreams',
        ['$d$','Stream','Endpoint','Mean','Lower','Upper'],seed_rows,
        'Every declared stream and endpoint is retained. These conditional-policy intervals and the method averages belong to the single registered confirmation family; their simulation banks are independent of stopping.',long=True)
    relative=(out.relative_to(ROOT) if out.is_relative_to(ROOT) else out).as_posix()
    text=[r'\subsection{Method performance, robustness, and complete work}',r'\label{sec:r15methodresults}',
          'The confirmation record contains all '+str(r['trial_count'])+' declared method--dimension--stream executions. Tables~\\ref{tab:r15methodmeans} and~\\ref{tab:r15methodcontrasts} report the finite-distribution payoff objects defined in Section~\\ref{sec:r15methoddistribution}. Every endpoint is reconstructed from the original final arrays after checking their common-path identities and source manifests.',
          r'Tables~\ref{tab:r15methodwork} and~\ref{tab:r15methodoperations} measure the executed stopping procedures, including unsuccessful checks and final confirmation. Table~\ref{tab:r15methoddecomposition} describes the numerical channels of the payoff change without assigning the total continuous-time certificate to its separate components.']
    for name in ['summary','comparisons','work','operations','decomposition']:
        text.append(r'\input{'+relative+'/table_method_'+name+'.tex}')
    (out/'method_evidence.tex').write_text('\n\n'.join(text)+'\n')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--protocol',required=True);ap.add_argument('--results',required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
    result=report(args.protocol,args.results,args.out)
    print(json.dumps(dict(status=result['status'],trials=result['trial_count'],events=result['confidence']['event_count'],out=args.out)))
