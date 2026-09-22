"""Stress the entire 18-node certificate, not only a favorable selected node."""
import argparse,json,time,traceback,resource
from pathlib import Path
import numpy as np
from independent_dual import run
from exact_price_audit import audit
ROOT=Path(__file__).resolve().parents[3]

def main(library,out):
    start=time.perf_counter();out.mkdir(parents=True,exist_ok=False);nodes=json.loads((library/'nodes.json').read_text());rows=[]
    for i,n in enumerate(nodes):
        k=n['k'];tag=f'{k:g}';d=json.loads((library/f'dual_k{tag}.json').read_text());p=json.loads((ROOT/d['pilot_path']).read_text())
        p['y0']+=1e-6;p['theta']=np.clip(np.array(p['theta'])+np.where(np.arange(len(p['theta']))%2==0,1e-6,-1e-6),0,np.nextafter(.2,-np.inf)).tolist()
        p['stress']='y0+1e-6; alternating drift +/-1e-6; action bounds inward enforced'
        file=out/f'pilot_k{tag}.json';file.write_text(json.dumps(p,indent=2)+'\n')
        r=run(file,str(k),32,512,robust=True);(out/f'dual_k{tag}.json').write_text(json.dumps(r,indent=2)+'\n')
        row={**n,'U':r['optimal_value_upper'],'stress_dual_seconds':r['seconds']};rows.append(row)
        (out/'nodes.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({'k':k,'regret':r['optimal_value_upper']-n['L'],'seconds':r['seconds']}),flush=True)
    result=audit(rows);result.update({'primitive_source_floor':-7.11,'primitive_beta_absolute_bound':1.11,'gaussian_tail_multiplier':2,
       'variance_allowance_multiplier':1.1,'witness_perturbation':p['stress'],'seconds_total':time.perf_counter()-start,
       'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'scope':'Every original cost node, independent dual implementation, unchanged original model and policies'})
    (out/'envelope.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['uniform_regret_upper','seconds_total']},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--library',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();main(a.library,a.out)
