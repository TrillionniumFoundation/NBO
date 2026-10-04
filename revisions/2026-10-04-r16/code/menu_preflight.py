"""Data-free curvature and economic-unit precision planning for the menu.

The only policies below are analytic action-distance fixtures. No learned
checkpoint, fit result, or confirmation draw is opened. Sample sizes and
economic margins are not changed by this calculation.
"""
from pathlib import Path
import argparse
import json
import math
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from menu_economy import load_economy,fixed_queries,scalar_query_spec,canonical_hash
from menu_curvature import scalar_curvature,model_constants,post_interval
from menu_verify import conditional_range,quadratic_value_interval,I,pc,upper,sqrt


def evaluate(protocol):
    rows=[]
    nstream=len(protocol['training_streams']['seeds'])
    budget=protocol['confidence']
    log=pc.log_i(4/(I(budget['alpha'])/budget['event_count']))
    for calibration in protocol['calibrations']:
        for dimension in protocol['dimensions']:
            economy=load_economy(protocol,calibration['id'],dimension)
            queries=fixed_queries(protocol,dimension);q=len(queries['states'])
            spec=scalar_query_spec(protocol,economy)
            c=scalar_curvature(economy,spec['state'],spec['a_left'],spec['a_right'],
                utility_weight=spec['task']['utility_weight'],adjustment=spec['task']['adjustment'])
            base=np.full_like(queries['states'],economy.schedule[0]);bp=post_interval(economy,queries['states'],base)
            constants=model_constants(economy)
            n=q*protocol['confirmation']['antithetic_pairs_per_query']*nstream
            examples=[]
            for distance in [.001,.01,.1]:
                action=np.minimum(np.maximum(base+distance,queries['lower']),queries['upper'])
                ap=post_interval(economy,queries['states'],action)
                q0=quadratic_value_interval(economy,ap)-quadratic_value_interval(economy,bp)
                center=pc.midpoint(q0)
                a=conditional_range(economy,action,base,ap,bp,I(center),constants,protocol['confirmation']['tail_v'])
                b=max(a['bounds']);vmax=I(n)*I(b).square()/(n-1)
                width=sqrt(2*vmax*log/n)+14*I(b)*log/(3*(n-1))
                examples.append(dict(analytic_uniform_action_distance=distance,
                    actual_maximum_action_distance=float(np.max(abs(action-base))),
                    clipping_radius_upper=b,worst_case_clipped_sample_variance=upper(vmax),
                    deterministic_worst_case_EB_halfwidth=upper(width),
                    clipping_tail_upper=max(a['tails']),
                    interpretation='adversarial variance bound for analytic geometry fixture; no predicted positive economic outcome'))
            rows.append(dict(calibration=calibration['id'],dimension=dimension,
                full_method_observations=n,query_count=q,complete_stream_count=nstream,
                primary_geometry_precision_examples=examples,scalar_curvature=c,
                scalar_gradient_pair_count=protocol['scalar_accuracy']['antithetic_pairs'],
                scalar_secant_halfwidth=protocol['scalar_accuracy']['secant_halfwidth']))
    return dict(schema='nbo-r16-menu-data-free-power-v1',status='complete',
        protocol_canonical_sha256=canonical_hash(protocol),
        primary_alpha=budget['alpha'],primary_events=budget['event_count'],
        scalar_alpha=protocol['scalar_accuracy']['alpha'],scalar_events=protocol['scalar_accuracy']['event_count'],
        total_alpha=budget['alpha']+protocol['scalar_accuracy']['alpha'],
        economic_margin=budget['economic_margin'],sample_size_changed=False,
        no_fitted_policy_or_confirmatory_observation_read=True,accounts=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--protocol',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.out.exists():raise FileExistsError('refusing to overwrite a power record')
    result=evaluate(json.loads(args.protocol.read_text()))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],cells=len(result['accounts']),
        scalar_curvature=[dict(calibration=r['calibration'],dimension=r['dimension'],
            strong_concavity=r['scalar_curvature']['strong_concavity_lower']) for r in result['accounts']]),indent=2))
