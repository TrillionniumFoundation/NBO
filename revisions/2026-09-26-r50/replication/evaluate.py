"""R50 source-frozen diffuse study and retrospective finite-model ablation."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import sys,json,time,gzip,resource,hashlib,subprocess
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;REPO=ROOT.parents[1]
CONFIGS=[('base',{}),('T4',{'T':4}),('T16',{'T':16}),('T32',{'T':32}),('m2',{'m':2}),('m5',{'m':5}),('beta50',{'beta':'1/2'}),('beta97',{'beta':'97/100'}),('beta99',{'beta':'99/100'}),('eps02',{'eps':'1/50'}),('eps15',{'eps':'3/20'}),('slope0',{'slope':'0'}),('slope80',{'slope':'4/5'})]

def worker(key,seed,method):
    start=time.perf_counter()
    from diffuse import generate,construct,enc
    from check_diffuse import verify
    opts=dict(CONFIGS)[key];raw=generate(seed=int(seed),**opts);case=f'{key}-{seed}'
    (ROOT/'models'/f'{case}.json').write_text(json.dumps(raw,indent=2)+'\n')
    traj=[];construction=verification=serialization=0
    for N in [16,64,256,1024]:
        r=construct(raw,N,method,16);construction+=r['construction_seconds'];e=enc(r)
        ts=time.perf_counter();blob=gzip.compress(json.dumps(e,sort_keys=True,separators=(',',':')).encode(),mtime=0)
        proof=ROOT/'proofs'/f'{case}-{method}-N{N}.json.gz';proof.write_bytes(blob);serialization+=time.perf_counter()-ts
        ts=time.perf_counter();v=verify(json.loads(gzip.decompress(proof.read_bytes())),raw);verification+=time.perf_counter()-ts
        traj.append(dict(N=N,lower=e['lower'],upper=e['upper'],width=v['width'],target_met=v['target_met'],cumulative_seconds=time.perf_counter()-start,proof_bytes=len(blob),proof_sha256=hashlib.sha256(blob).hexdigest(),proof=str(proof.relative_to(REPO)),lp_status=e['lp_status'],lp_variables=e['lp_variables'],lp_constraints=e['lp_constraints']))
        if v['target_met']:break
    full_cost=sum((F(raw['beta'])**t*(F(raw['k'][t][-1][0])+F(raw['k'][t][-1][1])/2) for t in range(raw['T'])),F(0))
    last=traj[-1];U=F(last['upper']);L=F(last['lower'])
    summary=dict(case=case,seed=int(seed),factor=key,method=method,model=raw,trajectory=traj,**{k:last[k] for k in ['N','lower','upper','width','target_met','proof_bytes','proof_sha256','lp_variables','lp_constraints']},construction_seconds=construction,verification_seconds=verification,serialization_seconds=serialization,all_in_seconds=time.perf_counter()-start,peak_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,relative_width=str((U-L)/U) if U else '0',preferred_policy_cost=str(full_cost),certified_saving_lower=str(full_cost-U),normalized_decision_loss=str((U-L)/full_cost))
    (ROOT/'results'/f'{case}-{method}.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(case,method,'N',last['N'],'width',float(U-L),'seconds',summary['all_in_seconds'],flush=True)

def study():
    for key,opts in CONFIGS:
        for seed in [401,503,607]:
            for method in ['highs-ds','highs-ipm']:
                subprocess.run([sys.executable,__file__,'worker',key,str(seed),method],check=True,cwd=REPO)

def finite():
    base=REPO/'revisions/2026-09-26-r48'
    models=sorted((base/'models').glob('*.json'))
    for p in models:
        raw=json.loads(p.read_text())
        if raw['n'] not in [3,5,8] or raw['T'] not in [4,8,12]:continue
        for seconds in [2,8]:
            for method in ['budget','price']:
                subprocess.run([sys.executable,__file__,'finite-worker',str(p),str(seconds),method],check=True,cwd=REPO)

def finite_worker(model,seconds,method):
    start=time.perf_counter();from budget import core,run
    from check_budget import verify as vb
    # Deliberately load R48 checker by its original module for the price ablation.
    import check as oldcheck
    raw=json.loads(Path(model).read_text());d=core.load(raw);core.validate(d)
    seconds=float(seconds)
    r=run(d,seconds=seconds,nodes=511,local_seconds=min(1,seconds/4)) if method=='budget' else core.run(d,method='price',seconds=seconds,nodes=511)
    e=core.enc(r);ts=time.perf_counter();blob=gzip.compress(json.dumps(e,sort_keys=True,separators=(',',':')).encode(),mtime=0)
    case=Path(model).stem;prefix=f'finite-{case}-{method}-{int(seconds)}s';proof=ROOT/'proofs'/f'{prefix}.json.gz';proof.write_bytes(blob);st=time.perf_counter()-ts
    ts=time.perf_counter();v=vb(e,raw) if method=='budget' else oldcheck.verify(e,raw);vt=time.perf_counter()-ts
    s={k:e[k] for k in ['lower','upper','target']};s.update(case=case,method=method,budget_seconds=seconds,verification=v,verify_seconds=vt,serialization_seconds=st,all_in_seconds=time.perf_counter()-start,proof_bytes=len(blob),proof_sha256=hashlib.sha256(blob).hexdigest(),proof=str(proof.relative_to(REPO)),peak_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,n=raw['n'],T=raw['T'],m=raw['m'],nodes=len(e['tree']),budget_dimension=raw['n']*(raw['T']-1),probability_dimension=raw['n']*raw['T']*raw['m'],trajectory=e.get('trajectory',e.get('trace',[])),stop=e.get('stop'))
    s['width']=str(F(s['upper'])-F(s['lower']));s['target_met']=F(s['width'])<=F(s['target'])
    (ROOT/'results'/f'{prefix}.json').write_text(json.dumps(s,indent=2)+'\n');print(prefix,'gap',float(F(s['width'])),'total',s['all_in_seconds'],flush=True)

if __name__=='__main__':
    for d in ['models','proofs','results','logs']:(ROOT/d).mkdir(exist_ok=True)
    if sys.argv[1]=='worker':worker(*sys.argv[2:])
    elif sys.argv[1]=='study':study()
    elif sys.argv[1]=='finite':finite()
    elif sys.argv[1]=='finite-worker':finite_worker(*sys.argv[2:])
