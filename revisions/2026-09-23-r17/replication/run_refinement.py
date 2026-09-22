from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,os,json,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=HERE.parent/'results'
def one(arch):
    rows=[];p=OUT/arch/'seed17100'
    for g in [(8,32,32),(16,64,64)]:
        dest=p/f'refinement_{g[0]}_{g[1]}_{g[2]}.json'
        if dest.exists():continue
        cmd=['python',str(ROOT/'revisions/2026-09-23-r16/replication/accessibility_certificate.py'),'--network',str(p/'network_step0400.json'),'--out',str(dest),'--grid',*map(str,g)];start=time.perf_counter()
        with open(dest.with_suffix('.log'),'w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'})
        rows.append({'architecture':arch,'grid':g,'returncode':r.returncode,'wall_including_startup':time.perf_counter()-start})
        if r.returncode:break
    return rows
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=2) as ex:rows=sum(list(ex.map(one,['accessible','allface'])),[])
    (OUT/'refinement_execution.json').write_text(json.dumps(rows,indent=2)+'\n')
    if any(r['returncode'] for r in rows):raise SystemExit(1)
