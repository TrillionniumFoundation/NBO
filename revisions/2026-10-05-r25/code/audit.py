"""Audit stored R25 candidates without fitting or replacing any measured clock."""
from pathlib import Path
from fractions import Fraction
import hashlib,json,math,time
import numpy as np
from constructive import ROOT,budget
from experiment import economy,evaluate
from policy_certificate import Ball,up,certify,value_balls
R=Path(__file__).resolve().parents[1]


def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def scientific(v):return f'{v:.2e}'


def audit():
    start=time.perf_counter();P=R/'results/primary'
    protocol=json.loads((R/'protocols/PROTOCOL.json').read_text());freeze=json.loads((R/'protocols/FREEZE.json').read_text())
    assert all(digest(R/p)==h for p,h in freeze['files'].items())
    original={p.name:digest(p) for p in P.iterdir() if p.is_file()}
    attempts=rows(P/'attempts.jsonl');services=rows(P/'services.jsonl')
    summary=json.loads((P/'SUMMARY.json').read_text())
    expected={(d,r,s,m) for d in protocol['dimensions'] for r in protocol['regimes'] for s in protocol['initial_scale_multipliers'] for m in protocol['methods']}
    assert len(attempts)==len(services)==len(expected)==protocol['services']
    assert {(x['dimension'],x['regime'],x['scale'],x['method']) for x in services}==expected
    exact=0;training=[];own_errors=[];max_target_difference=0.
    for row,service in zip(attempts,services):
        assert row['key']==service['key']
        file=P/row['candidate_file'];assert digest(file)==row['candidate_sha256']
        model=economy(row['dimension'],row['regime'],protocol['horizon'])
        with np.load(file,allow_pickle=False) as z:
            for name in ('A','B','Q','R','Qf','Sigma'):np.testing.assert_array_equal(z[name],model[name])
            K=z['gains'].copy();new=certify(model,K,protocol['execution_error_budget'])
            fields=('eta','ideal_gap_upper','implementation_gap_upper','policy_gap_upper','policy_value_upper')
            exact+=int(all(new[f]==row['certificate'][f] for f in fields))
            assert all(abs(new[f]-row['certificate'][f])<=1e-10*max(new[f],row['certificate'][f])+1e-12 for f in fields)
            assert (new['policy_gap_upper']<=protocol['tolerance'])==row['certified']==service['certified']
            if row['method']=='backward-NBO':
                W=z['critic_factor'].copy();nominal=z['own_target_matrices'].copy()
                actual,_=evaluate(model,K)
                delta=float(np.max(np.abs(actual-nominal)));max_target_difference=max(max_target_difference,delta)
                assert np.allclose(actual,nominal,atol=1e-13,rtol=1e-13)
                own,_=value_balls(*[model[n] for n in ('A','B','Q','R','Qf','Sigma','beta')],K)
                d=row['dimension'];inv=1./d
                inv_error=float(up(abs(float(Fraction(inv)-Fraction(1,d)))))
                for date in row['counters']['dates']:
                    t=date['continuation_date'];g=Ball.exact(W[t]).T@Ball.exact(W[t])
                    stored=(g-Ball.exact(d*nominal[t])).norm_f()
                    assert stored<=date['target']
                    fitted=g.scale(inv)
                    fitted=Ball(fitted.c,up(fitted.r+up(g.abs_upper()*inv_error)))
                    own_errors.append({'key':row['key'],'date':t,'own_coefficient_error_upper':(fitted-own[t]).norm_f()})
                    assert date['ideal_iteration_cap']==budget(date['initial_residual'],date['target']/2,date['alpha'],date['c'])
                    assert date['iterations']<=date['ideal_iteration_cap']
                    training.append(date)
        total=service['construction_seconds']+service['verification_seconds']+service['durable_write_and_audit_seconds']
        assert math.isclose(total,service['total_service_seconds'],abs_tol=1e-9,rel_tol=1e-12)
    assert original=={p.name:digest(p) for p in P.iterdir() if p.is_file()},'Primary bytes modified'
    cells=[]
    for d in protocol['dimensions']:
      for method in protocol['methods']:
        a=[x for x in services if x['dimension']==d and x['method']==method]
        cells.append({'dimension':d,'method':method,'services':len(a),'certified':sum(x['certified'] for x in a),
                      'mean_service_seconds':math.fsum(x['total_service_seconds'] for x in a)/len(a),
                      'mean_construction_seconds':math.fsum(x['construction_seconds'] for x in a)/len(a),
                      'mean_verification_seconds':math.fsum(x['verification_seconds'] for x in a)/len(a),
                      'mean_durable_seconds':math.fsum(x['durable_write_and_audit_seconds'] for x in a)/len(a),
                      'total_hidden_updates':sum(x['hidden_updates'] for x in a),
                      'total_ideal_hidden_update_cap':sum(x['ideal_hidden_update_cap'] for x in a),
                      'gram_checks':sum(x['gram_checks'] for x in a),'actor_solves':sum(x['actor_solves'] for x in a),
                      'max_policy_bound':max(x['policy_gap_upper'] for x in a),
                      'max_explicit_working_arrays_bytes':max(x['working_arrays_bytes'] for x in a),
                      'candidate_bytes':sum(x['candidate_bytes'] for x in a)})
    report={'frozen_source_commit':'9bf608d5154dfb61ff0ab209c2b66d1f8dbcc148',
            'services':len(services),'certified':sum(x['certified'] for x in services),
            'candidate_hashes_verified':len(attempts),'exact_numeric_replays':exact,
            'training_dates':len(training),'training_targets_met':sum(x['training_threshold_met'] for x in training),
            'initial_dates_outside_old_local_basin':sum(x['outside_previous_rank_basin'] for x in training),
            'hidden_updates':sum(x['iterations'] for x in training),
            'ideal_hidden_update_cap':sum(x['ideal_iteration_cap'] for x in training),
            'maximum_policy_bound':max(x['policy_gap_upper'] for x in services),
            'maximum_implementation_bound':max(x['implementation_gap_upper'] for x in services),
            'maximum_nominal_own_target_difference':max_target_difference,
            'primary_files_sha256':original,'cells':cells,'audit_seconds':time.perf_counter()-start,
            'all_original_primary_clocks_unchanged':True,
            'scope':'Deterministic complete-design execution. No inference from isometric orientations, no neural dominance claim, no use of optimal-policy values by verifier.'}
    save(R/'results/CONSTRUCTION_AUDIT.json',json.dumps(report,indent=2)+'\n')
    save(R/'results/OWN_TARGET_DIAGNOSTICS.json',json.dumps(own_errors,indent=2)+'\n')
    table=[r'\begin{table}[htbp]\centering\small',r'\caption{Finite backward construction: complete registered design}\label{tab:r25construction}',r'\begin{tabular}{rlrrr}\toprule $d$ & Procedure & Services & Seconds & Policy bound\\\midrule']
    for c in cells:
        table.append(f"{c['dimension']} & {c['method']} & {c['certified']}/{c['services']} & {c['mean_service_seconds']:.4f} & {scientific(c['max_policy_bound'])}"+r'\\')
    table.extend([r'\bottomrule\end{tabular}',r'\end{table}',r'\noindent\footnotesize Each row covers three declared future regimes and two prescribed initialization scales. Seconds are realized mean complete service clocks, not estimated population expectations. Bounds are maxima, include the execution allowance, and concern lifetime loss on the full initial domain. The structural method is repeated at both scale labels without treating those identical mathematical outputs as independent trials.\normalsize'])
    save(R/'results/construction_main.tex','\n'.join(table)+'\n')
    intro=r'''\subsection{Executing the finite construction}\label{sec:r25experiment}
The construction study freezes its source, two dyadic initialization scales,
three economic regimes, two dimensions and complete work account before any
primary execution. It uses the same 24-date capital economy and full-policy
tolerance $10^{-4}$ as the preceding study. A signed-permutation orientation
fixes the implementation; it is not counted as an independent random fit.
The future policy is reoptimized in every regime by the backward construction.
The matched structural recursion receives the same model coefficients and
is neither handicapped nor removed.

'''
    intro+=f"All {report['services']} services meet the declared tolerance. The {report['training_dates']} neural continuation dates meet their stored-target thresholds, and every initial critic lies outside the earlier sufficient local rank basin. The construction uses {report['hidden_updates']:,} hidden updates in total, below the sum of the conservative ideal caps, {report['ideal_hidden_update_cap']:,}. The actual rounded policy is checked independently; the ideal iteration inequality is not used as a numerical certificate.\n\n"
    intro+='\\input{revisions/2026-10-05-r25/results/construction_main.tex}\n'
    for d in protocol['dimensions']:
        n=next(c for c in cells if c['dimension']==d and c['method']=='backward-NBO')
        s=next(c for c in cells if c['dimension']==d and c['method']=='Riccati')
        intro+=f"At $d={d}$ the realized mean NBO-to-structural work ratio is ${n['mean_service_seconds']/s['mean_service_seconds']:.3f}$. "
    intro+='The structural recursion is cheaper in this execution. This result is retained together with the constructive neural guarantee: finite training and certified policy accuracy do not logically imply a total-work advantage. The experiment isolates the cost of factor training under common population information; it is not a simulation-efficiency comparison.\n'
    save(R/'manuscript/construction_experiment.tex',intro)
    lines=[r'\section{Finite-Construction Computational Record}\label{sec:r25record}',f"All {len(attempts)} candidate hashes and final certificates are replayed without refitting. {exact} of the certificates reproduce all five audited numeric fields exactly. Primary clocks and candidate bytes are unchanged.",r'\begin{longtable}{rllrrrr}',r'\caption{Complete construction and verification work}\label{tab:r25work}\\',r'\toprule $d$ & Method & Scale & Build & Verify & Write & Total\\\midrule\endfirsthead',r'\toprule $d$ & Method & Scale & Build & Verify & Write & Total\\\midrule\endhead']
    for x in services:
        lines.append(f"{x['dimension']} & {x['method']} & {x['scale']} & {x['construction_seconds']:.4f} & {x['verification_seconds']:.4f} & {x['durable_write_and_audit_seconds']:.4f} & {x['total_service_seconds']:.4f}"+r'\\')
    lines.extend([r'\bottomrule\end{longtable}',r'Rows occur in the registered regime order: anchor, technology, valuation within each dimension. Build includes initialization, reference evaluation, factor updates and Gram checks, and actor solves. Verify is the final outward policy check. Write includes compression, candidate hashing, fsync and the attempted-service ledger. All units are seconds.',f"The complete execution loop takes {summary['runtime_seconds_before_summary']:.6f} seconds before final summary writing; {summary['sum_service_seconds']:.6f} seconds are allocated to service clocks. The process-wide maximum resident set is {summary['process_high_water_rss_kib']} KiB; this is not a per-method peak. Explicit array-byte counts and saved candidate sizes are in the machine-readable record. Imports, environment setup and the final summary are not hidden inside per-service clocks.",r'There are zero simulated transitions in this population-information experiment. Derivative work is the reported hidden-update count; each update evaluates the complete matrix derivative. Every date has its own actor solve. Gram checks and final policy checks are reported separately. Failed final policy checks remain failures rather than being dropped from an accuracy-conditioned cost sample.',r'The archived local execution and the independently clocked remote execution use the same frozen design. They are distinct machine executions, not new independent draws of training randomness; their primary records are not mixed. Publication tables identify the execution supplied in the accompanying execution-identity record.'])
    save(R/'results/construction_record.tex','\n\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('primary_files_sha256','cells')},indent=2))

if __name__=='__main__':audit()
