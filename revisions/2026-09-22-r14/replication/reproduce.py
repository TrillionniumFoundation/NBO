"""Run the complete R14 scientific pipeline into a NEW directory.

The full run regenerates the actual neural experiment and the classical frontier,
then independently verifies the frozen historical library and its state extension.
A frozen-input library audit is not mislabeled as regeneration of its old training.
"""
from __future__ import annotations
import argparse,hashlib,json,os,platform,resource,subprocess,sys,time,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def main(out:Path,full:bool)->None:
    out=out.resolve()
    if not out.is_relative_to(ROOT):raise ValueError('Output must be a new directory under the repository, for relative proof-object identities.')
    out.mkdir(parents=True,exist_ok=False)
    source={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.py')}
    (out/'source_snapshot.json').write_text(json.dumps(source,indent=2)+'\n')
    env=os.environ.copy();env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    attempts=[];started=time.perf_counter()
    def run(label:str,args:list[str])->None:
        wall=time.perf_counter();before=resource.getrusage(resource.RUSAGE_CHILDREN)
        cmd=[sys.executable,str(HERE/args[0]),*map(str,args[1:])]
        with (out/(label+'.log')).open('w') as log:
            proc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        attempts.append({'stage':label,'command':cmd,'returncode':proc.returncode,'wall_seconds':time.perf_counter()-wall,
          'child_user_seconds':after.ru_utime-before.ru_utime,'child_system_seconds':after.ru_stime-before.ru_stime,'child_peak_rss_kib':after.ru_maxrss})
        (out/'attempts.json').write_text(json.dumps(attempts,indent=2)+'\n')
        if proc.returncode:raise RuntimeError(f'{label} failed; full log preserved')
    try:
        run('arithmetic',['interval64.py'])
        run('gauss_rule',['validated_gauss.py'])
        if full:
            run('neural_training',['neural_economy.py','--out',out/'neural_run'])
            for step,grid in [(100,[8,16,16]),(300,[8,16,16]),(800,[4,8,8]),(800,[8,16,16]),(800,[16,32,32])]:
                name=f'neural_{step:04d}_'+ '_'.join(map(str,grid))
                run(name,['neural_certificate.py','--network',out/f'neural_run/network_step{step:04d}.json','--out',out/(name+'.json'),'--grid',*map(str,grid)])
            run('fresh_frontier',['fresh_time_frontier.py','--out',out/'fresh_frontier'])
        library=out/'independent_library'
        run('independent_library',['run_independent_library.py','--out',library])
        run('price_envelope',['exact_price_audit.py','--nodes',library/'nodes.json','--out',out/'price_envelope.json'])
        run('state_cost',['state_cost_certificate.py','--library',library,'--out',out/'state_cost'])
        run('robust_library',['robust_library.py','--library',library,'--out',out/'robust_library'])
        run('high_precision',['high_precision_crosscheck.py','--library',library,'--out',out/'high_precision'])
        price=json.loads((out/'price_envelope.json').read_text())
        stress=json.loads((out/'robust_library/envelope.json').read_text())
        state=json.loads((out/'state_cost/envelope.json').read_text())
        assert price['uniform_regret_upper']<.01 and stress['uniform_regret_upper']<.01
        assert state['uniform_regret_upper']<.0121
        status={'status':'PASS','price_bound':price['uniform_regret_upper'],'stress_bound':stress['uniform_regret_upper'],'state_bound':state['uniform_regret_upper'],
          'neural_accuracy_0.01_claimed':False,'full_generation_executed':full}
    except Exception as exc:
        status={'status':'FAILED','exception':repr(exc),'traceback':traceback.format_exc()};raise
    finally:
        status.update({'wall_seconds':time.perf_counter()-started,'source_snapshot':source,'attempts':attempts,'platform':platform.platform(),
          'all_initial_sources_unchanged':all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in source.items()),
          'scope':'New neural and classical runs when --full; historical library proposal generation remains inherited and is not priced as zero.'})
        (out/'execution_receipt.json').write_text(json.dumps(status,indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--full',action='store_true');a=p.parse_args();main(a.out,a.full)
