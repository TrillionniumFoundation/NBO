"""Synthetic quadratic records for the independent serialized-algebra audit.

These are constructed functions q(a+d)=1+p*d+d*d, not calls or observations
of the investment economy. The production module is never configured.
"""
from fractions import Fraction as F
from pathlib import Path
from types import SimpleNamespace
import argparse, copy, hashlib, json, sys, time

REVISION = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REVISION/'code122'))
import algebra_audit122 as independent
import service122 as producer

producer.up = lambda v: producer.np.nextafter(producer.np.asarray(v, dtype=float), producer.np.inf)
producer.lab = SimpleNamespace(smoothness_rational=lambda alpha: {'L_action': independent.smoothness(F(alpha))})


def fixture(state, alpha, a, slope, gap, failed=False):
    cap = F(1, 8) + sum(map(F, state))/16
    w, u = F(1)-gap, F(1)+gap
    optimum = independent.quadratic_minimum(w, slope, F(2), -a, cap-a)
    upper = producer.directed_float(u+producer.DELTA, True)
    lower = producer.directed_float(w, False)
    bound = producer.directed_float(optimum, False)
    c = dict(original_action=float(a), original_state=[state], alpha=alpha, bins=128,
             support_anchor_lower=float(w), original_q_upper=float(u),
             support_slope_lower=float(slope), support_slope_upper=float(slope),
             optimum_lower=bound, support_curvature=2, full_support_continuous_risk=True)
    g = producer.recover(c, state, alpha)
    assert g['lower'] <= slope <= g['upper']
    record = dict(stage='recycled', bins=128, certificate=c, gradient=g,
                  proposal_capacity=float(cap), remaining_original_q_gain_upper=producer.constrained_regret(g),
                  candidate_menu=[])
    eligible=[]
    for j, fraction in enumerate(independent.FRACTIONS):
        p = producer.proposal(g, float(cap), fraction)
        z = dict(fraction_index=j, proposal=p)
        record['candidate_menu'].append(z)
        if failed and j == 1:
            break
        if p['unchanged_action']:
            z['reason']='unchanged-action'
        elif p['original_policy_gain_lower'] <= 0:
            z['reason']='future-policy-allowance-not-separated'
        else:
            new = producer.candidate_certificate(c, g, p, bound)
            z.update(candidate_certificate=new, candidate_qualified=new['qualified'])
            if new['qualified']:
                eligible.append((p, z, new))
    row = dict(index=0 if alpha==.5 else 1, row=0, budget=0, arm='synthetic', loss='synthetic',
               service='recycled', alpha=alpha, state=state, baseline_action=float(a),
               baseline_lower=lower, baseline_upper=upper, baseline_optimum_lower=bound,
               action=float(a), action_hex=float(a).hex(), complete_policy_lower=lower,
               complete_policy_upper=upper, original_optimum_lower=bound, qualified=True,
               accepted_improvement=False, certified_policy_gain_lower='0',
               initial_support_certificates=[c], support_attempts=[record],
               extra_candidate_economic_queries=0, paid_refinement_levels_started=[],
               paid_refinement_attempt_count=0, refinement_count=0, enhancement_numerical_failure=None,
               improvement_stop=('original-q-potential-no-larger-than-future-allowance'
                    if producer.constrained_regret(g)<=producer.DELTA else 'no-qualified-strict-improvement-in-frozen-six-step-menu'))
    if eligible and not failed:
        p, entry, new = min(eligible, key=lambda t: (-t[0]['original_policy_gain_lower'],t[0]['candidate'],t[1]['fraction_index']))
        record['selected_fraction_index']=entry['fraction_index']
        b=p['candidate']
        # The truth is the separately constructed quadratic and an arbitrary
        # admissible future-controller error, maximized at the new action.
        d=b-a
        true_gain=-(slope*d+d*d)-producer.DELTA
        assert true_gain >= p['original_policy_gain_lower'] > 0
        assert F(new['lower']) <= 1+slope*d+d*d <= 1+slope*d+d*d+producer.DELTA <= F(new['upper'])
        assert F(new['exact_optimum_lower']) <= independent.quadratic_minimum(F(1), slope, F(2), -a, cap-a)
        row.update(action=float(b),action_hex=float(b).hex(),accepted_improvement=True,
                   certified_policy_gain_lower=str(p['original_policy_gain_lower']),
                   complete_policy_lower=new['lower'],complete_policy_upper=new['upper'],
                   original_optimum_lower=new['optimum_lower'],certified_regret_upper=new['loss'],
                   improvement_stop='strict-original-policy-descent-certified',
                   **{key:new[key] for key in ('lower','upper','optimum_lower','loss','width')})
    row['candidate_algebra_attempts']=len(record['candidate_menu'])
    row['candidate_bound_attempts']=sum('candidate_certificate' in z for z in record['candidate_menu'])
    row['refused_candidate_bound_attempts']=sum('candidate_certificate' in z and not z['candidate_qualified'] for z in record['candidate_menu'])
    row['candidate_rejected']=row['refused_candidate_bound_attempts']>0
    if failed:
        row['enhancement_numerical_failure']=dict(exception_type='ArithmeticError',
               exception='synthetic failure after the second algebraic proposal',
               all_partial_attempts=producer.plain([record]))
        row['improvement_stop']='recorded-enhancement-numerical-failure-retain-completed-incumbent'
    # Make the data cross the same JSON type boundary as the independent audit.
    return json.loads(json.dumps(producer.plain(row), allow_nan=False))


def run():
    started=time.perf_counter()
    counts={};accepted=None;boundary=0
    for state in ([0.,0.],[1.,1.]):
      cap=F(1,8)+sum(map(F,state))/16
      for alpha in (.5,.75):
       for a in (F(0),cap/2,cap):
        for slope in (F(-1,16),F(-1,32),F(0),F(1,32),F(1,16)):
         for gap in (F(0),F(1,2**22)):
          row=fixture(state,alpha,a,slope,gap)
          result=independent.audit(row)
          for key,value in result.items():counts[key]=counts.get(key,0)+value
          boundary+=a in (0,cap)
          if row['accepted_improvement']:accepted=row
    assert accepted is not None
    # A completed eligible candidate before a later arithmetic failure must
    # still leave the completed incumbent untouched and retain its prefix.
    row=fixture([1.,1.],.5,F(1,8),F(1,16),F(0),failed=True)
    result=independent.audit(row)
    for key,value in result.items():counts[key]=counts.get(key,0)+value
    # Fixed adaptive schedules discard levels no finer than an already-paid
    # certificate; a finer mesh need not improve the numerical bound itself.
    for initial_bins in (128,256,512,1024):
        row=fixture([1.,1.],.5,F(1,8),F(0),F(1,2**22))
        row['service']='adaptive'
        row['support_attempts'][0]['bins']=initial_bins
        row['support_attempts'][0]['certificate']['bins']=initial_bins
        row['initial_support_certificates'][0]['bins']=initial_bins
        levels=[b for b in (256,512) if b>initial_bins]
        for level in levels:
            record=copy.deepcopy(row['support_attempts'][0])
            record.update(stage='paid-precision-refinement',bins=level)
            record['certificate']['bins']=level
            row['support_attempts'].append(record)
        row.update(paid_refinement_levels_started=levels,paid_refinement_attempt_count=len(levels),
                   refinement_count=len(levels),candidate_algebra_attempts=6*(1+len(levels)))
        result=independent.audit(row)
        for key,value in result.items():counts[key]=counts.get(key,0)+value
    # The paid refinement can fail before yielding a new certificate record.
    row=fixture([1.,1.],.5,F(1,8),F(0),F(1,2**22))
    row.update(service='adaptive',paid_refinement_levels_started=[256],paid_refinement_attempt_count=1,
               improvement_stop='recorded-enhancement-numerical-failure-retain-completed-incumbent',
               enhancement_numerical_failure=dict(exception_type='ArithmeticError',
                   exception='synthetic paid query failure before a support record',
                   all_partial_attempts=copy.deepcopy(row['support_attempts'])))
    result=independent.audit(row)
    for key,value in result.items():counts[key]=counts.get(key,0)+value
    detected=0
    for field in ('gradient','gain','action'):
        bad=copy.deepcopy(accepted)
        if field=='gradient':bad['support_attempts'][0]['gradient']['lower']='7'
        elif field=='gain':bad['support_attempts'][0]['candidate_menu'][0]['proposal']['original_policy_gain_lower']='1'
        else:bad['action_hex']='0x0.0p+0'
        try:independent.audit(bad)
        except ArithmeticError:detected+=1
        else:raise AssertionError('Corrupt synthetic record was not rejected: '+field)
    assert detected==3 and counts['accepted_actions']>0 and counts['retained_failure_rows']==2
    return dict(kind='synthetic_serialized_support_arithmetic_audit',status='passed',
                economic_experiment=False,population_observations=0,original_economic_calls=0,
                production_module_configured=False,boundary_quadratic_cases=boundary,
                counters=counts,corrupt_record_kinds_detected=detected,
                objective='constructed q(a+d)=1+p*d+d*d, with worst admissible future-error change',
                action_rounding_bits=30,source_sha256={
                    p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                    (Path(__file__),Path(independent.__file__),Path(producer.__file__))},
                elapsed_wall_seconds=time.perf_counter()-started)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=run();args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(result,indent=2))
