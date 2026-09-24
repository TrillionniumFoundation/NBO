"""Frozen R31 model/cohort, executed on the isolated R32 revision.
Usage: python study.py OUTPUT --horizon 4 (then 8 and 12).
This retains failures and writes exact compiled policies before their evaluation.
"""
from coupled import *
import numpy as np
import resource, gzip, subprocess, tempfile


def neural(T,seed):
    import torch
    torch.set_num_threads(1); torch.manual_seed(seed)
    states=torch.tensor((np.arange(257)+.5)/257,dtype=torch.float64).reshape(-1,1)
    nets=[None]*T; arrays=[None]*T; fit_seconds=0.; compile_seconds=0.; policies=[None]*T
    def continuation(x,t):
        return x[:,0]/2 if t==T else nets[t](x).max(1).values
    for t in reversed(range(T)):
        tic=time.perf_counter()
        with torch.no_grad():
            labels=[]
            for a in range(3):
                value=states[:,0]-float(COSTS[a])
                for prob,(s,b) in zip(PROBS,MAPS[a]): value=value+float(BETA*prob)*continuation(float(s)*states+float(b),t+1)
                labels.append(value)
            y=torch.stack(labels,dim=1)
        net=torch.nn.Sequential(torch.nn.Linear(1,16),torch.nn.ReLU(),torch.nn.Linear(16,3)).double()
        opt=torch.optim.Adam(net.parameters(),lr=.02)
        for _ in range(200):
            opt.zero_grad(); loss=((net(states)-y)**2).mean(); loss.backward(); opt.step()
        net.eval(); nets[t]=net
        with torch.no_grad(): loss=float(((net(states)-y)**2).mean())
        params=[p.detach().numpy().copy() for p in net.parameters()]
        fit_seconds+=time.perf_counter()-tic
        arrays[t]={'W1':params[0].tolist(),'b1':params[1].tolist(),'W2':params[2].tolist(),'b2':params[3].tolist(),'loss':loss}
        tic=time.perf_counter(); policies[t]=compile_neural(arrays[t]); compile_seconds+=time.perf_counter()-tic
    return policies,{'fit_seconds':fit_seconds,'compile_seconds':compile_seconds,'seed':seed,'nodes':257,'width':16,'steps_per_date':200,'dtype':'binary64'},arrays


def compile_neural(d):
    w=[F.from_float(row[0]) for row in d['W1']]; b=list(map(F.from_float,d['b1']))
    out=[[F.from_float(v) for v in row] for row in d['W2']]; bias=list(map(F.from_float,d['b2']))
    xs=sorted({ZERO,ONE}|{-c/a for a,c in zip(w,b) if a and 0<-c/a<1})
    fs=[]
    for a in range(3):
        ab=[]
        for l,r in zip(xs,xs[1:]):
            z=(l+r)/2; active=[j for j in range(16) if w[j]*z+b[j]>0]
            ab.append((sum((out[a][j]*w[j] for j in active),ZERO),bias[a]+sum((out[a][j]*b[j] for j in active),ZERO)))
        ys=[bias[a]+sum((out[a][j]*max(ZERO,w[j]*x+b[j]) for j in range(16)),ZERO) for x in xs]
        fs.append(PW(xs,ab,ys).norm())
    _,p=envelope(fs)
    # Compare the compiled selector against exact stored-coefficient evaluation.
    for x in p.xs+[(l+r)/2 for l,r in zip(p.xs,p.xs[1:])]:
        qq=[bias[a]+sum((out[a][j]*max(ZERO,w[j]*x+b[j]) for j in range(16)),ZERO) for a in range(3)]
        assert p.at(x)==min(range(3),key=lambda a:(-qq[a],a))
    return p


def spline(T,n):
    x=np.linspace(0,1,n); nxt=None; values=[None]*T; policies=[None]*T
    fit=0.; comp=0.
    for t in reversed(range(T)):
        tic=time.perf_counter(); qs=[]
        for a in range(3):
            q=x-float(COSTS[a])
            for prob,(s,b) in zip(PROBS,MAPS[a]):
                y=float(s)*x+float(b)
                continuation=y/2 if nxt is None else np.max(np.stack([np.interp(y,x,v) for v in nxt]),axis=0)
                q=q+float(BETA*prob)*continuation
            qs.append(q)
        nxt=np.array(qs); values[t]=nxt.tolist(); fit+=time.perf_counter()-tic
        tic=time.perf_counter(); rational_x=list(map(F.from_float,x.tolist()))
        fs=[interpolate(rational_x,list(map(F.from_float,v.tolist()))) for v in nxt]
        _,policies[t]=envelope(fs); comp+=time.perf_counter()-tic
    return policies,{'fit_seconds':fit,'compile_seconds':comp,'nodes':n,'dtype':'binary64'},values


def greedy_baseline(U,qs,raw):
    tic=time.perf_counter(); policies=[envelope(row)[1] for row in qs]
    values=evaluate(policies); costs=evaluate(policies,raw)
    for t in range(len(raw)):
        # Complete all-state error check; no pointwise test replaces this.
        assert linear_comb([U[t],select(q_functions(U[t+1]),policies[t])],[ONE,-ONE]).extent()[0]>=0
    return {'seconds_excluding_witness':time.perf_counter()-tic,'operating_value':str(values[0].integral()),'intervention_cost':str(costs[0].integral()),'all_restart_regret_upper':str(max(linear_comb([u,v],[ONE,-ONE]).extent()[1] for u,v in zip(U,values)))}


def price_frontier(options):
    """Complete upper envelope J-lambda C for lambda>=0, among listed policies."""
    cuts={ZERO}
    for i,(n,j,c) in enumerate(options):
        for m,k,d in options[i+1:]:
            if c!=d and (j-k)/(c-d)>0: cuts.add((j-k)/(c-d))
    cuts=sorted(cuts); rows=[]
    for i,l in enumerate(cuts):
        r=cuts[i+1] if i+1<len(cuts) else None; z=(l+r)/2 if r is not None else l+1
        winner=min(options,key=lambda a:(-(a[1]-z*a[2]),a[2],a[0]))[0]
        ties=[name for name,j,c in options if j-l*c==max(k-l*d for _,k,d in options)]
        rows.append({'lambda_left':str(l),'lambda_right':str(r) if r is not None else 'infinity','best_on_open_interval':winner,'ties_at_left':ties})
    return {'options':[{'policy':n,'operating_value':str(j),'intervention_cost':str(c)} for n,j,c in options], 'intervals':rows}


def run(out:Path,T:int):
    out.mkdir(parents=True,exist_ok=True); (out/'certificates').mkdir(exist_ok=True); (out/'proposals').mkdir(exist_ok=True)
    manifest={'python':sys.version,'platform':platform.platform(),'model':model(),'horizon':T,'measure':'uniform initial state, actual deployed-policy occupancy','timing':'single-process descriptive wall time; not a statistical speedup study','outcomes':[]}
    V,opt,exact_log=exact_dp(T); manifest['exact_dp']=exact_log
    wdata={str(eps):witnesses(T,eps) for eps in (F(1,100),F(1,20))}
    manifest['witnesses']={e:d[2] for e,d in wdata.items()}
    names=['defer','occupancy_stress','spline33','spline129','neural31001','neural31002','neural31003']
    for name in names:
        try:
            if name=='defer': raw,stats,params=[affine()]*T,{},None
            elif name=='occupancy_stress': raw,stats,params=stress_policy(T),{},None
            elif name.startswith('spline'): raw,stats,params=spline(T,int(name[6:]))
            else:
                fp=out/'proposals'/f'H{T}_{name}_fresh.json'
                tic=time.perf_counter()
                subprocess.run([sys.executable,__file__,str(fp),'--horizon',str(T),'--fit-only',name[6:]],check=True)
                process_seconds=time.perf_counter()-tic
                tic=time.perf_counter(); frozen=json.loads(fp.read_text())
                raw=[PW.load(p) for p in frozen['compiled']]; params=frozen['parameters']; stats=frozen['stats']
                load_seconds=time.perf_counter()-tic
                stats['in_process_fit_seconds']=stats['fit_seconds']
                stats['fit_seconds']=max(0.,process_seconds-stats['compile_seconds'])
                stats['compile_seconds']+=load_seconds
                stats['fresh_process_wall_seconds']=process_seconds
                stats['includes_interpreter_and_torch_import']=True
            frozen={'name':name,'horizon':T,'stats':stats,'parameters':params,'compiled':[p.dump() for p in raw]}
            (out/'proposals'/f'H{T}_{name}.json').write_text(json.dumps(frozen,sort_keys=True),encoding='utf8')
            for eps in (F(1,100),F(1,20)):
                key=f'H{T}_{name}_e{eps.numerator}_{eps.denominator}'
                try:
                    U,qs,wl=wdata[str(eps)]; r,cert=summary_case(T,eps,U,qs,wl,raw,name,stats,V)
                    baseline=greedy_baseline(U,qs,raw); baseline['total_seconds']=baseline['seconds_excluding_witness']+wl['seconds']; r['certified_greedy_baseline']=baseline
                    exact_cost=evaluate(opt,raw)[0].integral()
                    options=[('dynamic',F(r['operating_value']),F(r['intervention_cost'])),('pointwise',F(r['pointwise_operating_value']),F(r['pointwise_intervention_cost'])),('certified_greedy',F(baseline['operating_value']),F(baseline['intervention_cost'])),('exact_optimal',V[0].integral(),exact_cost)]
                    if r['raw_pass']: options.append(('raw',F(r['raw_operating_value']),ZERO))
                    r['price_frontier']=price_frontier(options)
                    r['process_peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                    encoded=json.dumps(cert,sort_keys=True,separators=(',',':')).encode()
                    with gzip.GzipFile(filename=str(out/'certificates'/f'{key}.json.gz'),mode='wb',mtime=0) as f: f.write(encoded)
                    r['certificate_file']=f'certificates/{key}.json.gz'; manifest['outcomes'].append(r)
                    print(T,name,str(eps),'regret',float(F(r['all_restart_regret_upper'])),'saving',float(F(r['occupancy_cost_saving'])),'raw',r['raw_pass'],'cold',round(r['cold_total_seconds'],4),flush=True)
                except Exception as exc:
                    manifest['outcomes'].append({'T':T,'proposal':name,'epsilon':str(eps),'status':'unresolved','exception':repr(exc)})
                    print('UNRESOLVED',T,name,eps,repr(exc),flush=True)
                (out/f'H{T}.json').write_text(json.dumps(manifest,indent=2,sort_keys=True),encoding='utf8')
        except Exception as exc:
            manifest['outcomes'].append({'T':T,'proposal':name,'status':'proposal_failure','exception':repr(exc)})
            (out/f'H{T}.json').write_text(json.dumps(manifest,indent=2,sort_keys=True),encoding='utf8')
            print('PROPOSAL FAILURE',T,name,repr(exc),flush=True)
    return manifest

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('output',type=Path); ap.add_argument('--horizon',type=int,required=True,choices=[4,8,12]); ap.add_argument('--fit-only',type=int); args=ap.parse_args()
    if args.fit_only is not None:
        p,s,v=neural(args.horizon,args.fit_only)
        args.output.write_text(json.dumps({'compiled':[x.dump() for x in p],'stats':s,'parameters':v},sort_keys=True),encoding='utf8')
    else: run(args.output,args.horizon)
