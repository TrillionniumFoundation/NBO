"""Audit all 18 retained proof objects with the new implementation, sequentially.
Frozen objects are INPUTS; this driver does not mislabel their generation as a
fresh training run. Every exception and timing is recorded and re-raised.
"""
from pathlib import Path
import argparse,json,time,sys,resource,platform,hashlib,traceback
from independent_primal import evaluate
from interval64 import I,exp
from validated_gauss import Q
from state_cost_certificate import full_budget
from independent_dual import run,primitives
ROOT=Path(__file__).resolve().parents[3]

def main(out,ns=32,nz=512):
    start=time.perf_counter();cpu=time.process_time();out.mkdir(parents=True,exist_ok=False)
    d=json.loads((ROOT/'revisions/2026-09-22-r12/results/envelope.json').read_text())
    (out/'primitives.json').write_text(json.dumps(primitives(),indent=2)+'\n')
    rows=[];attempts=[]
    for n in d['nodes']:
        k=str(n['k']);tag=f'{n["k"]:g}';actor=ROOT/n['actor_path'];pilot=actor.parent/f'dual_pilot_k{tag}.json'
        clock=time.perf_counter()
        try:
            p=evaluate(actor,k);q=run(pilot,k,ns,nz)
            assert p['value_interval'][0]<=n['U'] and p['value_interval'][1]>=n['L']
            r={'k':float(k),'L':p['value_interval'][0],'U':q['optimal_value_upper'],'B':(full_budget(actor)+I(-float((Q('.02')*2*exp(-Q('.58').square()/(2*Q('.05').square()))).hi),0)).pair(),'original_B':n['B'],'actor_path':n['actor_path'],
               'original_L':n['L'],'original_U':n['U'],'primal_width':p['width'],'dual_boxes':q['source_boxes'],
               'regret_upper':float(__import__('numpy').nextafter(q['optimal_value_upper']-p['value_interval'][0],float('inf'))),
               'input_generation':'inherited frozen proposal; new independent verification only'}
            (out/f'primal_k{tag}.json').write_text(json.dumps(p,indent=2)+'\n');(out/f'dual_k{tag}.json').write_text(json.dumps(q,indent=2)+'\n')
            rows.append(r);attempts.append({'k':float(k),'status':'success','wall_seconds':time.perf_counter()-clock})
            print(json.dumps({**r,'seconds':attempts[-1]['wall_seconds']}),flush=True)
        except Exception as e:
            attempts.append({'k':float(k),'status':'failed','wall_seconds':time.perf_counter()-clock,'exception':repr(e),'traceback':traceback.format_exc()})
            (out/'attempts.json').write_text(json.dumps(attempts,indent=2)+'\n');raise
        (out/'nodes.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'attempts.json').write_text(json.dumps(attempts,indent=2)+'\n')
    receipt={'status':'completed','nodes':len(rows),'wall_seconds':time.perf_counter()-start,'process_seconds':time.process_time()-cpu,
       'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'platform':platform.platform(),'failures':sum(r['status']!='success' for r in attempts),
       'scope':'Independent verification from frozen inputs; candidate generation not included or represented as zero cost',
       'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}}
    (out/'resource_ledger.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--ns',type=int,default=32);p.add_argument('--nz',type=int,default=512);a=p.parse_args();main(a.out,a.ns,a.nz)
