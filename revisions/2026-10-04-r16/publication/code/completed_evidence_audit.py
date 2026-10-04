"""Audit reading claims from immutable complete reports, without new random draws.

This independently recomputes reported primary interval arithmetic from retained
moments/allowances and recounts all decision classifications. It does not claim
to regenerate the raw numerical study or to turn unresolved tests into wins.
"""
from __future__ import annotations
import hashlib,json,math
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
from pathlib import Path
P=Path(__file__).resolve().parents[1]; ROOT=P.parents[2]
RESULTS=ROOT/'revisions/2026-10-04-r16/results'
EXPECTED={'continuation_menu/report/REPORT.json':'2a729aff851dc7060beb18e7fb8c1e0e9bb94d2b7d239c53f15cdd66a584cb63','robustness/report/REPORT.json':'2b675db41f2827d987c3ceae3e3ee01627a0e80228e0b9f54f85d2922d7e17fd'}

def close(a:float,b:float)->None:
    assert math.isfinite(a) and math.isfinite(b)
    assert math.isclose(a,b,rel_tol=5e-11,abs_tol=1e-13),(a,b)

def classify(lo:float,hi:float,eps:float)->dict[str,bool]:
    return {'positive':lo>0,'negative':hi<0,'materially_superior':lo>eps,'equivalent':lo>=-eps and hi<=eps}

def support(s:float,lo:float,hi:float,k:float)->float:
    """Sup g*t + k*t**2/2 over t in [-s,1-s], g in [lo,hi]."""
    values=[0.0]
    for g in [lo,hi]:
        for t in [-s,1-s]:values.append(g*t+0.5*k*t*t)
        if k<0:
            t=max(-s,min(1-s,-g/k));values.append(g*t+0.5*k*t*t)
    return max(values)

def interval(e:dict)->str:
    q=Decimal('0.000001')
    lo=Decimal(str(e['lower'])).quantize(q,rounding=ROUND_FLOOR)
    hi=Decimal(str(e['upper'])).quantize(q,rounding=ROUND_CEILING)
    return f'$[{lo:.6f},{hi:.6f}]$'

def main()->None:
    for name,expected in EXPECTED.items():
        assert hashlib.sha256((RESULTS/name).read_bytes()).hexdigest()==expected,name
    m=json.loads((RESULTS/'continuation_menu/report/REPORT.json').read_text())
    r=json.loads((RESULTS/'robustness/report/REPORT.json').read_text())
    assert m['complete'] and r['complete']
    assert (m['trial_count'],m['method_fits'],m['stage_candidates'])==(128,640,1920)
    assert (m['primary_event_count'],m['scalar_event_count'])==(216,128)
    assert (r['trials'],r['policy_outputs'],r['confidence_event_count_verified'])==(64,320,648)
    methods=['vector_costate','raw_actor','dpo_actor','raw_saa']
    totals={method:dict(total=0,positive=0,negative=0,materially_superior=0,equivalent=0) for method in methods}
    checked=0;final=[]
    for cell,stages in m['all_stages'].items():
        assert set(stages)=={'1','2','3'}
        for stage,events in stages.items():
            for name,e in events.items():
                n=e['paths'];a=e['event_alpha'];v=e['variance'];width=e['range_upper']-e['range_lower']
                assert n==16*384*512 and e['seed_count']==16 and e['query_count']==384
                close(a,.018/216)
                margin=math.sqrt(2*v*math.log(4/a)/n)+7*width*math.log(4/a)/(3*(n-1))
                close(margin,e['empirical_bernstein_margin'])
                offset=e['known_offset_interval'];b=e['bias']+e['clipping_tail']
                close(e['lower'],e['clipped_mean']+offset[0]-margin-b)
                close(e['upper'],e['clipped_mean']+offset[1]+margin+b)
                close(e['mean'],e['clipped_mean']+sum(offset)/2)
                if name.startswith('nbo_minus_'):
                    method=name[len('nbo_minus_'):];d=classify(e['lower'],e['upper'],m['economic_margin'])
                    totals[method]['total']+=1
                    for key,value in d.items():totals[method][key]+=int(value)
                    assert d['positive']==e['economic_decision']['statistical_superiority']
                    assert d['equivalent']==e['economic_decision']['practical_equivalence']
                    assert d['materially_superior']==e['economic_decision']['economically_material_superiority']
                checked+=1
        e=stages['3']['nbo_minus_raw_saa'];w=m['work'][cell]['3']
        nbo=w['nbo_scalar'];saa=w['raw_saa']
        assert nbo['mean_construction_and_query_seconds']==nbo['mean_actual_all_stage_fit_process_seconds']
        assert saa['mean_construction_and_query_seconds']==saa['mean_actual_all_stage_fit_process_seconds']
        for method in methods+['nbo_scalar']:
            close(w[method]['mean_complete_shared_confirmation_seconds'],nbo['mean_complete_shared_confirmation_seconds'])
        final.append({'cell':cell,'lower':e['lower'],'upper':e['upper'],'equivalent':e['economic_decision']['practical_equivalence'],'nbo_construction_query_seconds':nbo['mean_construction_and_query_seconds'],'saa_construction_query_seconds':saa['mean_construction_and_query_seconds'],'lower_nbo_construction_query_work':nbo['mean_construction_and_query_seconds']<saa['mean_construction_and_query_seconds'],'full_common_confirmation_seconds':nbo['mean_complete_shared_confirmation_seconds']})
    assert checked==216 and totals==m['all_stage_direct_decisions']
    assert sum(x['equivalent'] and x['lower_nbo_construction_query_work'] for x in final)==6
    assert all(x['lower_nbo_construction_query_work'] for x in final)
    scalar_checked=0;scalar_attained=0
    for cell,group in m['scalar_events'].items():
        attained=0
        assert len(group['events'])==16
        for e in group['events']:
            assert e['complete'] and e['independent_antithetic_pairs']==65536
            gap=e['scalar_optimum_gap'];s=gap['candidate_s'];lo,hi=gap['gradient_interval'];k=gap['curvature_upper']
            close(support(s,lo,hi,k),gap['gap_upper'])
            close(gap['gap_upper']+e['numerical_action_roundoff_allowances']['candidate'],e['implemented_candidate_gap_upper'])
            assert e['accuracy_at_margin']==(e['implemented_candidate_gap_upper']<=1e-4)
            attained+=int(e['accuracy_at_margin']);scalar_checked+=1
        assert attained==group['attained'];scalar_attained+=attained
    assert (scalar_checked,scalar_attained)==(128,80)
    ep={(x['calibration_id'],x['dimension'],x['endpoint']):x for x in r['method_endpoints']}
    assert len(ep)==72
    hjb=[x for x in ep.values() if x['endpoint'].startswith('nbo__minus__hjb')]
    assert sum(x['lower']>1e-4 for x in hjb)==2
    assert sum(x['lower']<=0<=x['upper'] for x in hjb)==14
    assert all(ep[(c,d,'nbo')]['lower']>0 for c in ['high','low','long','stress'] for d in [10,50])
    assert all(ep[(c,d,'nbo__minus__raw_costate')]['lower']<0<ep[(c,d,'nbo__minus__raw_costate')]['upper'] for c in ['high','low','long','stress'] for d in [10,50])
    table=[r'\begin{table}[!htbp]',r'\centering\footnotesize',r'\caption{NBO Relative to Both Strengthened HJB Deployments}\label{tab:r16readinghjb}',r'\begin{tabular}{llrr}',r'\toprule',r'Economy & $d$ & NBO minus greedy HJB & NBO minus distilled HJB \\',r'\midrule']
    for c,label in [('high','High volatility'),('low','Low volatility'),('long','Longer horizon'),('stress','Joint stress')]:
        for d in [10,50]:table.append(f'{label} & {d} & '+interval(ep[(c,d,'nbo__minus__hjb_greedy')])+' & '+interval(ep[(c,d,'nbo__minus__hjb_distilled')])+r' \\')
    table.extend([r'\bottomrule',r'\end{tabular}',r'\begin{minipage}{0.97\linewidth}\footnotesize\emph{Notes:} Outward-rounded continuous-payoff intervals. Every cell includes all eight new training streams. The two-sided family has 648 events and probability budget $0.01$. Candidate and deployment selection do not use final payoffs. The materiality margin is $10^{-4}$. These are fixed-envelope comparisons, not historical online stopping results.',r'\end{minipage}',r'\end{table}'])
    out=P/'results';out.mkdir(exist_ok=True)
    (out/'robustness_reading_table.tex').write_text('\n'.join(table)+'\n')
    record={'schema':'nbo-r16-completed-reading-audit-v1','complete':True,'report_sha256':EXPECTED,'menu_primary_interval_arithmetic_recomputed':checked,'menu_all_stage_direct_decisions':totals,'final_nbo_cached_saa_comparisons':final,'scalar_support_formulas_checked':scalar_checked,'scalar_attained':scalar_attained,'scalar_nonattained':128-scalar_attained,'strengthened_hjb_contrasts':16,'strengthened_hjb_material_positive':2,'strengthened_hjb_unresolved':14,'no_raw_numerical_reexecution_claim':True,'raw_evidence_preservation':'Immutable original evidence trees checked separately by publication_audit.py; the complete menu Git payload receipt covers 22272 files and 12203666768 bytes.','scope':'Stored complete reports, interval arithmetic, decision semantics, scalar support calculation and reading-table generation only; no new randomness, selection or evidence-family alteration.'}
    (out/'COMPLETED_EVIDENCE_READING_AUDIT.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k not in ['final_nbo_cached_saa_comparisons','menu_all_stage_direct_decisions']},indent=2))
if __name__=='__main__':main()
