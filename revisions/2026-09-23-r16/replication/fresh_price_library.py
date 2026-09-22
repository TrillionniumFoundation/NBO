"""Generate, fit, certify and adapt price nodes from model-only starts.
Historical algorithm code is reused; historical policies, pilots, nodes and
computed bounds are not inputs. Every fresh witness and optimizer log is saved.
"""
from pathlib import Path
import sys,json,time,resource,argparse,traceback
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'revisions/2026-09-22-r14/replication'))
from fresh_time_frontier import generate_policy,generate_dual
from independent_primal import evaluate
from independent_dual import run,primitives
from state_cost_certificate import full_budget
from exact_price_audit import audit
from interval64 import I,exp
Q=I.rational

def main(out):
    out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();rows=[];attempts=[];todo=[F(1,2),F(8)]
    (out/'primitives.json').write_text(json.dumps(primitives(),indent=2)+'\n')
    for iteration in range(30):
        k=todo.pop(0);kf=float(k);tag=f'{kf:g}';clock=time.perf_counter()
        try:
            actor=generate_policy(16,kf);pilot=generate_dual(kf);ap=out/f'actor_k{tag}.json';dp=out/f'dual_pilot_k{tag}.json'
            ap.write_text(json.dumps(actor,indent=2)+'\n');dp.write_text(json.dumps(pilot,indent=2)+'\n')
            p=evaluate(ap,str(k));d=run(dp,str(k),32,512)
            (out/f'primal_k{tag}.json').write_text(json.dumps(p,indent=2)+'\n');(out/f'dual_k{tag}.json').write_text(json.dumps(d,indent=2)+'\n')
            B=(full_budget(ap)+I(-float((Q('.02')*2*exp(-Q('.58').square()/(2*Q('.05').square()))).hi),0)).pair()
            row={'k':kf,'L':p['value_interval'][0],'U':d['optimal_value_upper'],'B':B,'actor_path':str(ap.relative_to(ROOT)),
                 'policy_generation_seconds':actor['seconds'],'dual_generation_seconds':pilot['seconds'],'primal_verification_seconds':p['seconds'],
                 'dual_verification_seconds':d['seconds'],'total_seconds':time.perf_counter()-clock,'optimizer_success':actor['optimizer_success'],
                 'fresh_input_contract':'no inherited actor, pilot or node list'}
            rows.append(row);rows.sort(key=lambda r:r['k']);attempts.append({'iteration':iteration,'k_rational':str(k),'status':'completed','seconds':time.perf_counter()-clock})
            (out/'nodes.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'attempts.json').write_text(json.dumps(attempts,indent=2)+'\n')
            if len(rows)<2:continue
            e=audit(rows);(out/'envelope.json').write_text(json.dumps(e,indent=2)+'\n')
            print(json.dumps({'nodes':len(rows),'k':kf,'uniform_regret_upper':e['uniform_regret_upper']}),flush=True)
            if F(e['uniform_regret_rational'])<F('.01'):break
            nxt=F(round(F(e['maximizer_rational'])*1024),1024)
            if nxt in [F(r['k']) for r in rows]:
                a,b=max(zip(rows,rows[1:]),key=lambda ab:ab[1]['k']-ab[0]['k']);nxt=(F(a['k'])+F(b['k']))/2
            todo.append(nxt)
        except Exception as exc:
            attempts.append({'iteration':iteration,'k_rational':str(k),'status':'failed','exception':repr(exc),'traceback':traceback.format_exc()})
            (out/'attempts.json').write_text(json.dumps(attempts,indent=2)+'\n');raise
    (out/'resources.json').write_text(json.dumps({'status':'completed','nodes':len(rows),'uniform_target_met':e['uniform_regret_upper']<.01,
      'wall_seconds':time.perf_counter()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      'stopping_rule':'proved uniform gap < .01 or 30 freshly generated nodes','inherited_policy_inputs':False,'inherited_dual_inputs':False,
      'arithmetic':'R14 rational-Taylor intervals; separate historical MPFR audit is not reassigned to this fresh object'},indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();main(a.out.resolve())
