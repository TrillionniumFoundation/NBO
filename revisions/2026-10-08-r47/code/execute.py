"""Run the frozen R47 design. All output paths are create-only."""
from __future__ import annotations
import itertools,json,os,platform,subprocess,sys,time
from pathlib import Path
import numpy as np
from common import R,I,fi,F,BETA,bins,confidence,quantize_interval,save_npz,write,hfile
from constrained import Model,METHODS,stage,terminal,transition,grid

def multidim_cost(payload,initial,shocks,bits=12):
    x=initial;v=I.point(np.zeros(len(x.lo)));stats=[]
    for t,m in enumerate(payload['models']):
        model=Model(m);a,record=model.interval_action(x,bits);stats.append(record)
        v=v+fi(BETA**t)*stage(x,a,payload['price'])
        a=I(a.lo[:,None],a.hi[:,None]);z=2*shocks[t]-1
        z=I(z.lo[:,None],z.hi[:,None])
        x=transition(x,a,z).clip(0,1)
    return v+fi(BETA**payload['T'])*terminal(x),stats

def new_pairs(out):
    out.mkdir();rows=[];representations=[]
    for d,T,p in itertools.product((2,3),(2,4),(.25,1.)):
        key=f'd{d}-T{T}-p{p:g}';N=16 if d==2 else 8;payloads={};identities={}
        for method in METHODS:
            path=R/'results/constrained'/f'{key}-{method}-r0'/f'checkpoint-N{N}.json'
            payloads[method]=json.loads(path.read_text());identities[method]=hfile(path)
        start=time.perf_counter();seed=471000+100*d+10*T+int(4*p)
        rng=np.random.Generator(np.random.PCG64(seed));n=65536
        initial=bins(rng,(n,d));shocks=[bins(rng,(n,)) for _ in range(T)]
        costs={};stats={}
        for method,payload in payloads.items():costs[method],stats[method]=multidim_cost(payload,initial,shocks)
        lo,hi=quantize_interval(costs['witness']-costs['multilinear-fvi'])
        M=sum(BETA**t*(F(1,32)+F(p)/8) for t in range(T))+BETA**T*F(9,8)
        digest=save_npz(out/(key+'.npz'),lo=lo,hi=hi)
        row={'d':d,'T':T,'price':p,'N':N,'n':n,'seed':seed,'left':'witness','right':'multilinear-fvi',
             'acquisition_bits':12,'policy_sha256':identities,'stats':stats,'cost_upper_exact':str(M),
             'raw_endpoints':key+'.npz','raw_sha256':digest,'seconds':time.perf_counter()-start,
             **confidence(lo,hi,M,8)}
        write(out/(key+'.json'),row);rows.append(row)
        # Query engines see exactly the same immutable arrays and states.
        rng=np.random.default_rng(479000+d*100+T*10+int(p*4))
        query=np.vstack((rng.uniform(size=(1024,d)),grid(d,N),grid(d,N)*.5+1/(4*N)))
        query=np.clip(query,0,1)
        for t,data in enumerate(payloads['witness']['models']):
            model=Model(data);values={};clocks={};counts={}
            for backend in ('flat-min-plus','compiled-min-plus','compiled-ReLU'):
                model.score_evaluations=0;begin=time.perf_counter();values[backend]=model.point(query,backend)
                clocks[backend]=time.perf_counter()-begin;counts[backend]=model.score_evaluations
            ref=values['flat-min-plus'];overlap=True
            for v in values.values():overlap=overlap and bool(np.all(ref.lo<=v.hi) and np.all(v.lo<=ref.hi))
            deployment={}
            for bits in (12,20):
                a,st=model.deploy(query,bits);true_capacity=.25+query.sum(axis=1)/(4*d)
                if not np.all(a<=true_capacity):raise AssertionError('Infeasible action')
                st['queries']=len(query);st['max_repair_shortfall']=float(np.max(true_capacity-a))
                deployment[str(bits)]=st
            representations.append({'d':d,'T':T,'price':p,'date':t,'N':N,'queries':len(query),
                    'same_object_sha256':hfile(R/'results/constrained'/f'{key}-witness-r0'/f'checkpoint-N{N}.json'),
                    'enclosures_overlap':overlap,'seconds':clocks,'cone_scores':counts,
                    'maximum_interval_width':{k:float((v.hi-v.lo).max()) for k,v in values.items()},'deployment':deployment})
            assert overlap
    write(out/'summary.json',{'contrasts':rows,'family_size':8,'within_margin':sum(r['within_margin'] for r in rows)})
    write(out/'representations.json',{'records':representations,'scope':'Same-object query-engine observations; not independent training comparisons.'})

def main():
    results=R/'results'
    if results.exists():raise FileExistsError('Never overwrite an executed study')
    results.mkdir()
    write(R/'audit/EXECUTION_FREEZE.json',{'source_commit':os.environ.get('GITHUB_SHA','local-new-observation'),
        'workflow_run':os.environ.get('GITHUB_RUN_ID'),'protocol_commit':'bcaa6bc42cb9dcbdf0b05d66d4978236e63293b0',
        'amendment_commit':'08c075a79f90b38faa63a4d7f093689c145fe24b',
        'sources':{p.name:hfile(p) for p in sorted((R/'code').glob('*.py'))},
        'python':platform.python_version(),'numpy':np.__version__,'planned_services':48,'planned_rungs':144,
        'scope':'New observations. Local development tests are not catalogue rows. No checkpoint or policy is imported as a training label.'})
    from scalar import main as scalar_main
    scalar_main(results/'scalar')
    work=results/'constrained';work.mkdir();processes=[]
    cells=list(itertools.product((2,3),(2,4),(.25,1.)))
    for rep in range(3):
        for cell,(d,T,p) in enumerate(cells):
            methods=METHODS if (rep+cell)%2==0 else METHODS[::-1]
            for method in methods:
                key=f'd{d}-T{T}-p{p:g}-{method}-r{rep}'
                cmd=[sys.executable,str(R/'code/constrained.py'),'--d',str(d),'--T',str(T),'--price',str(p),'--method',method,'--repeat',str(rep),'--out',str(work/key)]
                start=time.perf_counter()
                with (work/(key+'.log')).open('x') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
                row={'key':key,'returncode':r.returncode,'process_seconds':time.perf_counter()-start};processes.append(row)
                write(work/(key+'.process.json'),row)
                if r.returncode:raise RuntimeError(key)
                print(key,round(row['process_seconds'],3),flush=True)
    new_pairs(results/'pairs')
    write(R/'audit/EXECUTION_COMPLETE.json',{'services':48,'rungs':144,'processes':processes,'scalar_comparisons':30,'multidimensional_comparisons':8})

if __name__=='__main__':main()
