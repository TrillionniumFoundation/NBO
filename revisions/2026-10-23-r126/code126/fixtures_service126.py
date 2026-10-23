"""Exact synthetic action/value-gate fixtures, never original economic outcomes."""
import argparse
from common126 import *


def run(output):
    import service126 as svc
    svc.configure()
    before=dict(svc.old.econ.COUNTS); cases=[]; checks=0
    for shift in (F(3),F(101)):
        for slope in (F(-3),F(-1),F(1)):
            for action in (F(0),F(1,4),F(1,2),F(1)):
                optimum=max(F(0),min(F(1),-slope/2))
                q=lambda x: x*x+slope*x+shift
                p=dict(a=action,W=q(action),U=q(action),p_lower=2*action+slope,
                       p_upper=2*action+slope,g_lower=2*action+slope,g_upper=2*action+slope)
                case=svc.env.normalize(dict(A=F(1),incumbent=action,mu=F(2),L=F(2),delta=DELTA,
                    tau=TAU,omega=OMEGA,old_optimum_lower=q(optimum),payloads=[p]))
                c=svc.terminal_certificate(case,action)
                truth=q(action)-q(optimum)+DELTA
                assert c['direct_regret']==truth; checks+=1
                assert c['width']==DELTA; checks+=1
                if action==optimum:
                    assert c['target_qualified']; checks+=1
                cases.append(dict(shift=shift,slope=slope,action=action,optimum=optimum,
                                  exact_regret=truth,certificate=c))
    # Exact derivative information must not defeat the independently required
    # absolute objective-width gate, even at a known original optimum.
    a=F(1,2); e=F(1,32); value=F(11,4)
    p=dict(a=a,W=value-e,U=value+e,p_lower=F(0),p_upper=F(0),g_lower=F(0),g_upper=F(0))
    wide=svc.env.normalize(dict(A=F(1),incumbent=a,mu=F(2),L=F(2),delta=DELTA,
        tau=TAU,omega=OMEGA,old_optimum_lower=value-e,payloads=[p]))
    c=svc.terminal_certificate(wide,a)
    assert c['direct_regret']==DELTA and not c['qualified'] and not c['target_qualified']; checks+=1
    assert c['width']==2*e+DELTA>OMEGA; checks+=1
    assert svc.old.econ.COUNTS==before=={}; checks+=1
    receipt=dict(status='executed',scope='prefreeze synthetic rational mathematics and import preflight only',
        completed_utc=dt.datetime.now(dt.timezone.utc).isoformat(),original_economic_evaluations=0,
        original_economic_counter_before=before,original_economic_counter_after=dict(svc.old.econ.COUNTS),
        checks=checks,quadratic_cases=len(cases),wide_value_counterexample=c,cases=cases,
        scientific_source_sha256={p.name:sha(p) for p in Path(__file__).parent.glob('*.py')},
        cohort_count=len(catalog()),state_count=len(STATES),models_exist=all(model_path(k) is None or model_path(k).is_file() for k in actors()),
        separate_original_economic_experiment=False)
    write(output,receipt)
    print(json.dumps(dict(checks=checks,quadratic_cases=len(cases),original_economic_evaluations=0,output=str(output))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();run(a.output)
