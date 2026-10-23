"""Fresh complete original-law services sharing the entire paid support ledger."""
from fractions import Fraction as F
from pathlib import Path
import json,sys,time,traceback
import numpy as np
import envelope123 as env

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor/2026-10-20-r122/code122'))
import service122 as old
from common122 import plain

MODES=('r122','best_single','fused','probe_fused')


def configure():
    old.configure()


def payload(record,state,alpha):
    g=old.recover(record,state,alpha)
    return dict(a=g['action'],W=F(record['support_anchor_lower']),U=F(record['original_q_upper']),
                p_lower=F(record['support_slope_lower']),p_upper=F(record['support_slope_upper']),
                g_lower=g['lower'],g_upper=g['upper'])


def make_case(records,state,alpha,baseline):
    A=F(1,8)+sum(map(F,state))/16
    for record in records:
        if record.get('alpha')!=alpha or record.get('original_state')!=[list(state)]:
            raise ValueError('Cannot recycle support from another original state or risk')
    return dict(A=A,incumbent=F(baseline['action']),mu=F(2),L=old.lab.smoothness_rational(alpha)['L_action'],
                delta=old.DELTA,tau=F(1,256),omega=F(1,8192),
                old_optimum_lower=F(baseline['original_optimum_lower']),
                payloads=[payload(c,state,alpha) for c in records],gradient_rule='r122-finite-radii',
                gradient_cap=7,radius_indices=[2,40])


def float_certificate(cert):
    lo=old.directed_float(cert['lower'],False)
    hi=old.directed_float(cert['upper'],True)
    B=old.directed_float(cert['optimum_lower'],False)
    loss=float(old.up(hi-B));width=float(old.up(hi-lo))
    return dict(lower=lo,upper=hi,optimum_lower=B,loss=loss,width=width,
                qualified=loss<=1/256 and width<=1/8192)


def choose(case,mode,progress=None):
    progress={} if progress is None else progress
    progress.update(case=case,mode=mode,stage='support-minimum',started_candidates=0,completed_candidates=[],failed_attempt=None)
    common=env.support_minimum(case)
    progress['stage']='menu-construction'
    menu=env.candidate_menu(case)
    entries=[];acceptable=[]
    for i,item in enumerate(menu):
        progress.update(stage='candidate-arithmetic',started_candidates=i+1)
        try:
            e=dict(item,certificate=env.candidate(case,item['b'],mode,common))
            progress['stage']='outward-conversion'
            f=float_certificate(e['certificate'])
            e['outward']=f
            e['outward_accepted']=e['certificate']['accepted'] and f['qualified']
            entries.append(e);progress['completed_candidates'].append(e)
            if e['outward_accepted']:acceptable.append((i,e))
        except (ArithmeticError,np.linalg.LinAlgError) as exc:
            progress['failed_attempt']=dict(index=i,**item,exception_type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
            raise
    progress['stage']='selection'
    selected=min(acceptable,key=lambda z:(-z[1]['certificate']['gain_lower'],z[1]['b'],z[0])) if acceptable else None
    progress['stage']='completed'
    return entries,selected


def service(state,alpha,model,mode):
    if mode not in MODES:raise ValueError('Undeclared prospective service')
    start=time.perf_counter()
    if mode=='r122':
        row=old.service(state,alpha,model,'recycled')
        row.update(mode=mode,complete_seconds=time.perf_counter()-start,new_risk_queries_started=0,
                   new_risk_queries_completed=0,multi_anchor_cases=[],policy_identity='inherited original future controller')
        return row
    before=old.econ.COUNTS.copy();records=[];cases=[];failure=None
    with old.capture_support(records):base=old.lab.service(state,alpha,model)
    baseline=base['row'];answer=dict(baseline);selected=None;entries=[]
    probes=[];accepted=False;reason='no-original-support-for-exact-fallback'
    queries_started=queries_completed=0;partial_menu=None
    try:
        if records:
            case=env.normalize(make_case(records,state,alpha,baseline))
            arithmetic_mode='best_single' if mode=='best_single' else 'fused'
            partial_menu={}
            entries,selected=choose(case,arithmetic_mode,partial_menu)
            cases.append(dict(case=case,mode=arithmetic_mode,candidates=entries,selected_index=None if selected is None else selected[0]))
            partial_menu=None
            if mode=='probe_fused' and selected is None:
                left=env.envelope_root(case,True);right=env.envelope_root(case,False)
                if left>right:raise ArithmeticError('Empty original-optimum bracket')
                c=env.rounded_action((left+right)/2,case['A'])
                rec=dict(bracket_lower=left,bracket_upper=right,midpoint=(left+right)/2,
                         rounded_probe=c,bins=128,performed=False)
                probes.append(rec)
                if left<right and all(c!=p['a'] for p in case['payloads']):
                    queries_started+=1;rec['performed']=True
                    with old.kern.backend(True):
                        fresh=old.enriched_certificate(np.asarray(state,float)[None,:],np.array([float(c)]),alpha,128)
                    queries_completed+=1
                    fresh=old.scalar_certificate(fresh);records.append(dict(alpha=alpha,**fresh))
                    case=env.normalize(make_case(records,state,alpha,baseline))
                    rec.update(new_bracket_lower=env.envelope_root(case,True),new_bracket_upper=env.envelope_root(case,False),payload=case['payloads'][-1])
                    partial_menu={}
                    entries,selected=choose(case,'fused',partial_menu)
                    cases.append(dict(case=case,mode='fused',candidates=entries,selected_index=None if selected is None else selected[0]))
                    partial_menu=None
            if selected is not None:
                index,e=selected;cert=e['certificate'];flo=e['outward'];b=float(e['b'])
                answer.update(action=b,action_hex=b.hex(),complete_policy_lower=flo['lower'],complete_policy_upper=flo['upper'],
                              original_optimum_lower=flo['optimum_lower'],certified_regret_upper=flo['loss'],
                              action_distance_upper=float(old.up(np.sqrt(flo['loss']))),**flo)
                accepted=True;reason='strict-original-policy-gain-with-regret-and-width'
            else:reason='no-qualified-strict-gain-in-complete-fixed-menu'
    except (ArithmeticError,np.linalg.LinAlgError) as exc:
        failure=dict(exception_type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),
                     elapsed_seconds=time.perf_counter()-start)
        answer=dict(baseline);selected=None;accepted=False;reason='recorded-enhancement-failure-retain-qualified-incumbent'
    gain=selected[1]['certificate']['gain_lower'] if selected else F(0)
    answer.update(mode=mode,baseline_action=baseline['action'],baseline_action_hex=baseline['action_hex'],
                  baseline_lower=baseline['complete_policy_lower'],baseline_upper=baseline['complete_policy_upper'],
                  baseline_optimum_lower=baseline['original_optimum_lower'],baseline_qualification_attempts=base['attempts'],
                  initial_support_certificates=records,baseline_actor_trace=base['actor_trace'],
                  accepted_improvement=accepted,certified_policy_gain_lower=str(gain),
                  raw_proposal_kept=baseline['first_proposal_action'],multi_anchor_cases=cases,probes=probes,
                  support_count=len(records),distinct_support_actions=len(set(c['original_action'] for c in records)),
                  new_risk_queries_started=queries_started,new_risk_queries_completed=queries_completed,
                  candidate_algebra_attempts=sum(len(c['candidates']) for c in cases)+(partial_menu or {}).get('started_candidates',0),
                  incomplete_menu_attempt=partial_menu,
                  candidate_refusals=sum(not r['outward_accepted'] for c in cases for r in c['candidates'])+sum(not r['outward_accepted'] for r in (partial_menu or {}).get('completed_candidates',[])),
                  enhancement_numerical_failure=failure,improvement_stop=reason,
                  complete_seconds=time.perf_counter()-start,counts=old.lab.inherited.base.counter_delta(before),
                  policy_identity='inherited original future controller')
    return plain(answer)
