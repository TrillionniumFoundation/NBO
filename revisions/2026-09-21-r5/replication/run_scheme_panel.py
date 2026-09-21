from pathlib import Path
import subprocess,sys,json,time
D=Path(__file__).resolve().parent; out=D.parent/'results'
commands=[]
for N in (16,32,64,128,256):
    for mode in ('endpoint','bridge'):
        commands.append(['--n',str(N),'--mode',mode])
for n,nu,nx,na in [(12,13,16,3),(24,25,31,3),(48,49,61,5),(96,97,121,5)]:
    commands.append(['--task','ndu','--n',str(n),'--nu',str(nu),'--nx',str(nx),'--na',str(na)])
for k in (.5,8):
    commands.append(['--task','ndu','--n','48','--nu','49','--nx','61','--na','5','--k',str(k)])
records=[]
for i,args in enumerate(commands):
    start=time.perf_counter()
    with (out/f'scheme_command_{i}.log').open('w') as log:
        try:
            r=subprocess.run([sys.executable,str(D/'scheme_validation.py')]+args,stdout=log,stderr=subprocess.STDOUT,timeout=300)
            rec=dict(index=i,args=args,returncode=r.returncode,status='completed' if r.returncode==0 else 'failed')
        except subprocess.TimeoutExpired: rec=dict(index=i,args=args,status='timeout')
    rec['seconds']=time.perf_counter()-start; records.append(rec)
    (out/'scheme_execution.json').write_text(json.dumps(records,indent=2)); print(json.dumps(rec),flush=True)
