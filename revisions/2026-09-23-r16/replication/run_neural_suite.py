from pathlib import Path
import argparse,sys,json,time,traceback,subprocess,concurrent.futures,platform
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def run_one(seed,out):
    path=out/f'seed{seed}';width=16 if seed%2==0 else 32
    cmd=[sys.executable,str(HERE/'accessibility_neural.py'),'--out',str(path),'--seed',str(seed),'--width',str(width)]
    with (out/f'seed{seed}.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
    for step in [800,2400]:
        net=path/f'network_step{step:04d}.json'
        subprocess.run([sys.executable,str(HERE/'accessibility_certificate.py'),'--network',str(net),'--out',str(path/f'jet_test{step}.json'),'--test-only'],check=True)
        subprocess.run([sys.executable,str(HERE/'accessibility_certificate.py'),'--network',str(net),'--out',str(path/f'certificate{step}.json')],check=True)
    return {'seed':seed,'status':'completed'}
def main(out,workers):
    start=time.perf_counter();out.mkdir(parents=True,exist_ok=False);attempts=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        jobs={pool.submit(run_one,seed,out):seed for seed in range(16100,16110)}
        for future in concurrent.futures.as_completed(jobs):
            try:attempts.append(future.result())
            except Exception as e:attempts.append({'seed':jobs[future],'status':'failed','error':repr(e),'traceback':traceback.format_exc()})
            (out/'attempts.json').write_text(json.dumps(attempts,indent=2)+'\n')
    if any(a['status']!='completed' for a in attempts):raise RuntimeError('One or more full seed experiments failed')
    net=out/'seed16100/network_step2400.json'
    subprocess.run([sys.executable,str(HERE/'accessibility_certificate.py'),'--network',str(net),'--out',str(out/'seed16100/refinement.json'),'--grid','8','32','32'],check=True)
    ab=out/'all_face_ablation'
    subprocess.run([sys.executable,str(HERE/'accessibility_neural.py'),'--out',str(ab),'--seed','16100','--width','16','--steps','800','--all-faces'],check=True)
    subprocess.run([sys.executable,str(HERE/'accessibility_certificate.py'),'--network',str(ab/'network_step0800.json'),'--out',str(ab/'certificate.json')],check=True)
    (out/'suite_resources.json').write_text(json.dumps({'status':'completed','wall_seconds':time.perf_counter()-start,'parallel_seed_processes':workers,
      'torch_threads_per_seed':1,'platform':platform.platform(),'scope':'end-to-end suite including processes, training, independent interval audit and serialization'},indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--workers',type=int,default=2);a=p.parse_args();main(a.out,a.workers)
