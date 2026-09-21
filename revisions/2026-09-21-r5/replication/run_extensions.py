"""Fixed post-pilot extension matrix. Preserve every outcome and all timings."""
from pathlib import Path
import json,subprocess,sys,time
D=Path(__file__).resolve().parent;O=D.parent/'results'
commands=[]
for d in (8,16,32):
    for seed in (40,41):
        for method in ('nbo','pinnpi'):
            commands.append(('nonlinear_control.py',['--d',str(d),'--seed',str(seed),'--method',method]))
for seed in (51,52):commands.append(('recursive_neural.py',['--seed',str(seed)]))
for seed in (61,62):commands.append(('neural_game.py',['--seed',str(seed)]))
records=[]
for i,(script,args) in enumerate(commands):
    marker=O/f'extension_execution_{i}.json'
    if marker.exists():print('retained',marker,flush=True);continue
    start=time.perf_counter()
    with (O/f'extension_execution_{i}.log').open('w') as log:
        try:
            run=subprocess.run([sys.executable,str(D/script)]+args,stdout=log,stderr=subprocess.STDOUT,timeout=300)
            rec=dict(index=i,script=script,args=args,returncode=run.returncode,status='completed' if run.returncode==0 else 'failed')
        except subprocess.TimeoutExpired:rec=dict(index=i,script=script,args=args,status='timeout')
    rec['seconds']=time.perf_counter()-start;marker.write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)
