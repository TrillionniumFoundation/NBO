"""Execute the complete fixed catalogue, retaining caps and software exceptions."""
from pathlib import Path
import os,sys,json,time,subprocess,random,hashlib,platform
R=Path(__file__).resolve().parents[1]
def catalogue():
    specs=[]
    for price in (1,4):
      for theta in (0,1):
       for seed in (104729,130363,155921):
        for method in ('direct-neural','spline'):
         specs.append(dict(kind='scalar',price=price,theta=theta,seed=seed,method=method))
    for price in (1,4):
      for seed in (104729,130363,155921):
       for method in ('convex-neural','quadratic-projection','ridge-projection'):
        specs.append(dict(kind='coupled',price=price,seed=seed,method=method))
    for repeat in range(3):
      for d,c in ((2,1.),(2,16.),(8,1.),(8,16.)):
       for epsilon in (1e-10,1e-12,1e-14):
        for method in ('fixed32-cached','fixed64-cached','adaptive-cached'):
         specs.append(dict(kind='precision',repeat=repeat,service=dict(kind='policy',name=f'd{d}-c{c:g}-e{epsilon:g}',epsilon=epsilon,economy=dict(d=d,T=4,condition=c,valuation=1.,sigma=.001,theta=.1),method=method)))
    random.Random(421007).shuffle(specs);return specs
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--directory',default=str(R/'results/publication'));p.add_argument('--kind');p.add_argument('--limit',type=int);args=p.parse_args()
    root=Path(args.directory);root.mkdir(parents=True,exist_ok=True)
    specs=catalogue();selected=[(i,s) for i,s in enumerate(specs) if not args.kind or s['kind']==args.kind]
    if args.limit is not None:selected=selected[:args.limit]
    rows=[]
    for i,spec in selected:
        out=root/f'service-{i:03}'
        if out.exists():raise FileExistsError('Fresh execution required: '+str(out))
        out.mkdir();start=time.perf_counter()
        with (out/'stdout.log').open('w') as f:
            proc=subprocess.run([sys.executable,str(R/'code/execute.py'),'--spec',json.dumps(spec),'--directory',str(out)],stdout=f,stderr=subprocess.STDOUT)
        row=dict(id=i,spec=spec,exit_code=proc.returncode,process_wall_seconds=time.perf_counter()-start)
        if (out/'clock.json').exists():row['clock']=json.loads((out/'clock.json').read_text())
        else:row['status']='exception_before_clock'
        (out/'process.json').write_text(json.dumps(row,indent=2,sort_keys=True)+'\n');rows.append(row);print(json.dumps(row),flush=True)
    index=dict(protocol_commit='df8d6692c36213efc1d6dceea4947de7b7d5bb80',protocol_addendum_commit='e3b1a3612d845fecfbdbb38135dcb5e2414cb302',publication_source_commit=os.environ.get('GITHUB_SHA'),execution_location='GitHub Actions' if os.environ.get('GITHUB_ACTIONS') else 'local development',fixed_catalogue_size=len(specs),executed=len(rows),software_failures=sum(row['exit_code']!=0 for row in rows),services=rows,machine=platform.platform())
    (root/'INDEX.json').write_text(json.dumps(index,indent=2,sort_keys=True)+'\n')
    if index['software_failures']:raise RuntimeError('Software exceptions retained; publication gate failed')
