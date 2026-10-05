"""Replay original certificates without rerunning fits or replacing clocks.

The trainable-factor diagnostic is deterministic post-execution analysis,
not the frozen stopping rule. All original outcomes and hashes are retained.
"""
from pathlib import Path
from fractions import Fraction
import hashlib,json,math,time
import numpy as np
from policy_certificate import Ball,up,down,positive_sum,certify,value_balls
from experiment import economy
R=Path(__file__).resolve().parents[1]
P=R/'results/primary'
O=R/'results/generated'


def rows(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def norm2(b):
    a=b.abs_upper()
    n1=float(np.max(positive_sum(a,axis=0)))
    ni=float(np.max(positive_sum(a,axis=1)))
    return float(up(math.sqrt(float(up(n1*ni)))))


def factor_certificate(model,K,W,verified):
    beta=model['beta'];d=model['d'];T=model['horizon']
    own,_=value_balls(*[model[k] for k in ('A','B','Q','R','Qf','Sigma','beta')],K)
    grams=[Ball.exact(w).T@Ball.exact(w) for w in W]
    fitted=[g.scale(1.0/d) for g in grams]+[Ball.exact(model['Qf'])]
    # scale(1/d) alone represents the rounded reciprocal. Include its error
    # to enclose the exact mathematical quotient W'W/d in the proposition.
    inv=1.0/d
    inv_error=float(up(abs(float(Fraction(inv)-Fraction(1,d)))))
    for t,g in enumerate(grams):
        fitted[t]=Ball(fitted[t].c,up(fitted[t].r+up(g.abs_upper()*inv_error)))
    gradient_errors=[0.0]*(T+1);ranks=[]
    for t in range(1,T):
        g=grams[t];off=g.abs_upper().copy();np.fill_diagonal(off,0)
        low=float(np.min(down(down(np.diag(g.c)-np.diag(g.r))-positive_sum(off,axis=1))))
        if low<=0:
            return {'rank_verified':False,'failed_date':t,'factor_policy_gap_upper':None,'certified':False}
        s=float(down(math.sqrt(low)));ranks.append(s)
        grad=Ball.exact(W[t])@(g-own[t].scale(d))
        gradient_errors[t]=float(up(grad.norm_f()/float(down(d*s))))
    eta=0.0
    for t in range(T):
        a,b,r,k=[Ball.exact(v) for v in (model['A'][t],model['B'][t],model['R'][t],K[t])]
        f=a-b@k
        z=(r+(b.T@fitted[t+1]@b).scale(beta))@k-(b.T@fitted[t+1]@a).scale(beta)
        tail=float(up(beta*up(up(norm2(b)*norm2(f))*gradient_errors[t+1])))
        residual=float(up(z.norm_f()+tail))
        qmin=float(np.min(np.diag(model['Q'][t])));rmin=float(np.min(np.diag(model['R'][t])))
        eta=max(eta,float(up(up(residual*residual)/float(down(qmin*rmin)))))
    ratio=float(up(eta/float(down(1+eta))))
    bound=float(up(up(ratio*verified['policy_value_upper'])+verified['implementation_gap_upper']))
    return {'rank_verified':True,'min_singular_value_lower':min(ranks),'eta_upper':eta,
            'factor_policy_gap_upper':bound,'certified':bool(bound<=1e-4),
            'scope':'own returned-policy gradient; post-execution diagnostic, not stopping evidence'}


def scientific(x,digits=2):
    if x==0:return '$0$'
    e=int(math.floor(math.log10(abs(x))))
    return '$'+f'{x/10**e:.{digits}f}'+r'\!\times\!10^{'+str(e)+'}$'


def run():
    tic=time.perf_counter();O.mkdir(exist_ok=True)
    protocol=json.loads((R/'protocols/PROTOCOL.json').read_text())
    freeze=json.loads((R/'protocols/FREEZE.json').read_text())
    hashes={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in freeze['files']}
    assert hashes==freeze['files'],'Frozen implementation was changed'
    attempts=rows(P/'attempts.jsonl');services=rows(P/'services.jsonl')
    assert len(services)==480 and len(attempts)==1088
    expected={(d,s,m,r) for d in protocol['dimensions'] for s in protocol['seeds'] for m in protocol['methods'] for r in protocol['regimes']}
    actual={(x['dimension'],x['seed'],x['method'],x['regime']) for x in services}
    assert actual==expected and len(actual)==len(services)
    fields=('eta','policy_value_upper','ideal_gap_upper','implementation_gap_upper','policy_gap_upper')
    exact=0;max_abs=0.;max_rel=0.;bykey={};last={};factor=[]
    for i,row in enumerate(attempts):
        path=P/row['candidate_file']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['candidate_sha256']
        with np.load(path,allow_pickle=False) as z:
            model=economy(row['dimension'],row['regime'],protocol['horizon'])
            for n in ('A','B','Q','R','Qf','Sigma'):
                assert np.array_equal(model[n],z[n]),(path.name,n)
                model[n]=z[n].copy()
            K=z['gains'].copy();new=certify(model,K,protocol['execution_error_budget'])
            old=row['certificate']
            differences=[abs(new[k]-old[k]) for k in fields]
            exact+=int(all(new[k]==old[k] for k in fields))
            max_abs=max(max_abs,*differences)
            max_rel=max(max_rel,*[abs(new[k]-old[k])/max(abs(old[k]),1e-300) for k in fields])
            assert bool(new['policy_gap_upper']<=protocol['policy_tolerance'])==row['certified']
            assert all(abs(new[k]-old[k])<=1e-10*max(abs(new[k]),abs(old[k]))+1e-12 for k in fields)
            previous=bykey.setdefault(row['key'],[])
            assert not previous or not previous[-1]['certified'],'An outcome followed a successful stop'
            previous.append(row);last[row['key']]=(new,model,K)
            if row['certified'] and row['method'].startswith('NBO'):
                f=factor_certificate(model,K,z['critic_factor'].copy(),new)
                factor.append({'key':row['key'],'dimension':row['dimension'],'seed':row['seed'],'method':row['method'],'regime':row['regime'],**f})
        if i%100==0:print('replayed',i,flush=True)
    for s in services:
        seq=bykey[s['key']]
        assert len(seq)==s['checks'] and seq[-1]['certified']==s['certified']
        assert sum(not a['certified'] for a in seq)==s['failed_checks']
        assert seq[-1]['candidate_sha256']==s['final_candidate_sha256']
    cells=[]
    for d in protocol['dimensions']:
      for method in protocol['methods']:
       for regime in protocol['regimes']:
        a=[s for s in services if (s['dimension'],s['method'],s['regime'])==(d,method,regime)]
        c={'dimension':d,'method':method,'regime':regime,'n':len(a),
           'success_probability_exact':str(Fraction(sum(s['certified'] for s in a),len(a)))}
        for f in ('evaluation_calls','gradient_updates','linear_solve_calls','checks','failed_checks'):
            c['expected_'+f]=str(Fraction(sum(s[f] for s in a),len(a)))
        c['mean_seconds']=math.fsum(s['complete_service_seconds'] for s in a)/len(a)
        c['max_policy_bound']=max(s['policy_gap_upper'] for s in a)
        c['max_implementation_bound']=max(s['implementation_gap_upper'] for s in a)
        cells.append(c)
    bands=[]
    lookup={(s['dimension'],s['seed'],s['method'],s['regime']):s for s in services}
    for d in protocol['dimensions']:
      for method in protocol['methods']:
       for regime in protocol['regimes'][1:]:
        bs=[]
        for seed in protocol['seeds']:
            a=lookup[d,seed,method,'anchor'];b=lookup[d,seed,method,regime]
            al=float(down(a['initial_mean_investment']-a['initial_mean_investment_radius']))
            au=float(up(a['initial_mean_investment']+a['initial_mean_investment_radius']))
            bl=float(down(b['initial_mean_investment']-b['initial_mean_investment_radius']))
            bu=float(up(b['initial_mean_investment']+b['initial_mean_investment_radius']))
            bs.append([float(down(bl-au)),float(up(bu-al))])
        lo=min(b[0] for b in bs);hi=max(b[1] for b in bs)
        bands.append({'dimension':d,'method':method,'regime':regime,'lower':lo,'upper':hi,
                      'sign':'positive' if lo>0 else 'negative' if hi<0 else 'unresolved',
                      'interpretation':'hull of all sixteen paired optimum-response enclosures, not a confidence interval'})
    totals=[]
    for d in protocol['dimensions']:
      for method in protocol['methods']:
        a=[s for s in services if (s['dimension'],s['method'])==(d,method)]
        totals.append({'dimension':d,'method':method,'mean_three_regime_seconds':math.fsum(s['complete_service_seconds'] for s in a)/len(protocol['seeds']),
                       'expected_three_regime_evaluations':str(Fraction(sum(s['evaluation_calls'] for s in a),len(protocol['seeds']))),
                       'expected_three_regime_checks':str(Fraction(sum(s['checks'] for s in a),len(protocol['seeds'])))})
    report={'source_hashes':hashes,'services':len(services),'attempts':len(attempts),
            'certified':sum(s['certified'] for s in services),'failed_checks':sum(not a['certified'] for a in attempts),
            'candidate_hashes_verified':len(attempts),'replayed_decisions_agree':len(attempts),
            'exact_numeric_field_replays':exact,'max_numeric_absolute_difference':max_abs,'max_numeric_relative_difference':max_rel,
            'factor_diagnostics':len(factor),'factor_rank_verified':sum(f['rank_verified'] for f in factor),
            'factor_threshold_passes':sum(f['certified'] for f in factor),'cells':cells,'response_bands':bands,'stream_totals':totals,
            'postprocessing_seconds':time.perf_counter()-tic,
            'primary_clocks':'retained unchanged; fits not rerun; verification replay and factor analysis are separately charged publication work'}
    (O/'REPLAY.json').write_text(json.dumps(report,indent=2)+'\n')
    (O/'FACTOR_DIAGNOSTICS.json').write_text(json.dumps(factor,indent=2)+'\n')
    t=[r'\begin{longtable}{rllrrr}',r'\caption{Full-policy stopping: every cell has 16 of 16 certifications}\label{tab:r23frontier}\\',r'\toprule $d$ & Procedure & Future & Passes & Seconds & Maximum bound\\\midrule\endfirsthead',r'\toprule $d$ & Procedure & Future & Passes & Seconds & Maximum bound\\\midrule\endhead']
    for c in cells:t.append(f"{c['dimension']} & {c['method']} & {c['regime']} & {c['expected_evaluation_calls']} & {c['mean_seconds']:.4f} & {scientific(c['max_policy_bound'])}"+r'\\')
    t.extend([r'\bottomrule\end{longtable}',r'\noindent\footnotesize Passes are exact finite-randomizer expectations of own-policy evaluations. Riccati instead performs 24 backward solves. Seconds include initialization, all attempted fits, checks and candidate writes; they are realized mean clocks. Bounds are maxima across all 16 seeds and include the declared execution allowance.\normalsize'])
    (O/'frontier.tex').write_text('\n'.join(t)+'\n')
    t=[r'\begin{table}[htbp]\centering\small',r'\caption{Complete three-regime streams}\label{tab:r23streams}',r'\begin{tabular}{rlrrr}\toprule $d$ & Procedure & Evaluations & Checks & Seconds\\\midrule']
    for c in totals:t.append(f"{c['dimension']} & {c['method']} & {c['expected_three_regime_evaluations']} & {c['expected_three_regime_checks']} & {c['mean_three_regime_seconds']:.4f}"+r'\\')
    t.extend([r'\bottomrule\end{tabular}',r'\end{table}'])
    (O/'streams.tex').write_text('\n'.join(t)+'\n')
    t=[r'\begin{longtable}{rllrrl}',r'\caption{Mean investment responses with reoptimized futures}\label{tab:r23responses}\\',r'\toprule $d$ & Procedure & Future & Lower & Upper & Sign\\\midrule\endfirsthead',r'\toprule $d$ & Procedure & Future & Lower & Upper & Sign\\\midrule\endhead']
    for b in bands:
        # Outward decimal display, not round-to-nearest shrinking of bands.
        lo=math.floor(b['lower']*1e6)/1e6;hi=math.ceil(b['upper']*1e6)/1e6
        t.append(f"{b['dimension']} & {b['method']} & {b['regime']} & {lo:.6f} & {hi:.6f} & {b['sign']}"+r'\\')
    t.extend([r'\bottomrule\end{longtable}',r'\noindent\footnotesize Each interval is the hull over all registered initialization seeds of paired optimum-response enclosures at the common initial stock. Endpoints are printed outward. These are model enclosures, not population confidence intervals.\normalsize'])
    (O/'responses.tex').write_text('\n'.join(t)+'\n')
    # Compact native record: all detailed machine-readable fields remain above.
    text=r'\section{Full-Policy Computational Record}\label{sec:r23record}'+'\n'
    text+=f"The frozen execution contains {len(services)} complete services and {len(attempts)} attempted certificates. All {len(attempts)} candidate hashes and all stopping decisions were replayed. {exact} replayed certificates match all five audited numerical fields bit for bit; the remaining differences, where present, are retained in the machine-readable audit. No original fitting clock is replaced.\n\n"
    text+=f"The deterministic trained-factor diagnostic covers all {len(factor)} final neural policies. It verifies the rank premise for {report['factor_rank_verified']} and certifies the original threshold through the factor account for {report['factor_threshold_passes']}. This auxiliary calculation is not the original stopping rule. Failed auxiliary bounds remain in the record.\n\n"
    text+=r'\input{revisions/2026-10-05-r23/results/generated/responses.tex}'+'\n'
    (O/'record.tex').write_text(text)
    print(json.dumps({k:v for k,v in report.items() if k not in ('cells','response_bands','stream_totals')},indent=2))
    return report

if __name__=='__main__':run()
