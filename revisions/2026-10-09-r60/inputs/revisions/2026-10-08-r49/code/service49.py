"""Separated state/action/integration budgets; R48 primitives stay immutable."""
from __future__ import annotations
import argparse, itertools, math, platform, resource, time, sys, os
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE.parent/'2026-10-08-r48/code'))
from common import *
from tensor import Model
import service as old
METHODS=('compiled-witness','tensor-fvi','curvature-fvi')
TARGETS=tuple(map(F,('5','4','2','1','1/2')))
LADDERS={2:((4,2,1),(8,2,1),(16,4,2),(32,4,2),(64,8,4),(128,16,8)),3:((4,2,1),(8,4,2),(16,8,4),(32,8,4)),4:((4,2,1),(8,4,2),(16,8,4))}

def adaptive_axes(values,N,d):
    """Pilot-curvature bisection, without a dominating unit baseline."""
    v=np.asarray(values).reshape((9,)*d);axes=[];weights=[]
    for j in range(d):
        curvature=[]
        for k in range(1,8):
            a=np.take(v,k-1,axis=j).ravel();b=np.take(v,k,axis=j).ravel();cc=np.take(v,k+1,axis=j).ravel()
            curvature.append(max(abs(F(float(x))-2*F(float(y))+F(float(z))) for x,y,z in zip(a,b,cc)))
        w=[max(curvature[max(1,k)-1],curvature[min(7,k+1)-1],F(1,2**40)) for k in range(8)]
        knots=[F(0),F(1)]
        while len(knots)<N+1:
            score=[]
            for i,(a,b) in enumerate(zip(knots,knots[1:])):
                cells=[k for k in range(8) if F(k,8)<b and F(k+1,8)>a]
                score.append((-(b-a)**2*max(w[k] for k in cells),a,i))
            i=min(score)[2];knots.insert(i+1,(knots[i]+knots[i+1])/2)
        axes.append(np.array(list(map(float,knots))));weights.append(list(map(str,w)))
    return axes,weights

def queries(nodes,K,M,p,future,counts):
    d=nodes.shape[1]
    caps=cap(I.point(nodes)).lo
    actions=np.maximum(0,np.nextafter(caps[:,None]*np.arange(K+1)[None,:]/K,-np.inf))
    assert np.all(actions<=caps[:,None])
    xx=np.repeat(nodes,K+1,axis=0);aa=actions.reshape(-1)
    low=np.empty(len(aa));high=np.empty(len(aa));zs=c.array_i([F(2*j+1-M,32*M) for j in range(M)])
    for begin in range(0,len(aa),1024):
        x=xx[begin:begin+1024];a=aa[begin:begin+1024];n=len(a)
        shock=I(np.tile(zs.lo,n),np.tile(zs.hi,n))
        nx=transition(I.point(np.repeat(x,M,axis=0)),I.point(np.repeat(a,M)),shock)
        vv=future.evaluate(nx);vv=I(vv.lo.reshape(n,M),vv.hi.reshape(n,M))
        mean=old.midpoint_sum(vv,1)/M;error=c.rat_i(future.L*F(d,64*M))
        q=costs(I.point(x),I.point(a),p)+float(BETA)*(mean+I(-error.hi,error.hi))
        low[begin:begin+n]=q.lo;high[begin:begin+n]=q.hi
    counts['bellman_queries']+=len(aa);counts['innovation_midpoints']+=len(aa)*M;counts['stage_cost_evaluations']+=len(aa)
    v,e=c.rounded_labels(I(low,high));v=v.reshape(len(nodes),K+1);idx=np.argmin(v,axis=1)
    return v[np.arange(len(nodes)),idx],actions[np.arange(len(nodes)),idx],e

def rung(N,K,M,T,p,method,d=2):
    if method not in METHODS or any(n<1 or n&(n-1) for n in (N,K,M)):raise ValueError('Invalid resources')
    if method=='curvature-fvi' and d!=2:raise ValueError('Adaptive pilot is declared in d=2')
    C,G,Fx,Fa,Ca,Ka=moduli(d,p);kind='witness' if method=='compiled-witness' else 'fvi'
    counts=dict(bellman_queries=0,innovation_midpoints=0,stage_cost_evaluations=0,terminal_cost_evaluations=0,pilot_bellman_queries=0,nearest_cell_vertices=0)
    pilots=[];axes=old.uniform_axes(N,d)
    if method=='curvature-fvi':
        pn=np.array(list(itertools.product(*old.uniform_axes(8,d))))
        py,_=c.rounded_labels(costs(I.point(pn),I.point(np.zeros(len(pn))),p,True))
        counts['terminal_cost_evaluations']+=len(pn);axes,w=adaptive_axes(py,N,d);pilots.append({'date':T,'weights':w})
    nodes=np.array(list(itertools.product(*axes)))
    labels,eT=c.rounded_labels(costs(I.point(nodes),I.point(np.zeros(len(nodes))),p,True));counts['terminal_cost_evaluations']+=len(nodes)
    future=Model(axes,labels,kind,G);models=[None]*T+[future];actors=[None]*T;rows=[None]*T
    terminal_width=2*eT+2*G*future.h;k=F(1,8*K)+F(1,2**48)
    for t in range(T-1,-1,-1):
        A=C+BETA*Fx*future.L;D=Ca+BETA*Fa*future.L;L=A+D*Ka;axes=old.uniform_axes(N,d)
        if method=='curvature-fvi':
            pn=np.array(list(itertools.product(*old.uniform_axes(8,d))));before=counts['bellman_queries']
            py,_,_=queries(pn,K,M,p,future,counts);counts['pilot_bellman_queries']+=counts['bellman_queries']-before
            axes,w=adaptive_axes(py,N,d);pilots.append({'date':t,'weights':w})
        nodes=np.array(list(itertools.product(*axes)));labels,actions,e=queries(nodes,K,M,p,future,counts)
        current=Model(axes,labels,kind,L)
        if kind=='witness':u=D*k+e+2*L*current.h;selected=e;extra=F(0)
        else:
            u=D*k+e+L*current.h;extra,n=old.nearest_excess(current,L);counts['nearest_cell_vertices']+=n;selected=e+extra
        rows[t]={'date':t,'A':str(A),'D':str(D),'L_graph':str(L),'query_error':str(e),'state_cover':str(current.h),'action_cover':str(k),'quadrature_remainder':str(BETA*future.L*F(d,64*M)),'optimal_residual_upper':str(u),'selected_policy_upper':str(selected),'nearest_excess':str(extra),'component':str(u+selected)}
        models[t]=current;actors[t]=actions.tolist();future=current
    bound=sum((BETA**t*F(row['component']) for t,row in enumerate(rows)),F(0))+BETA**T*terminal_width
    deployment=old.deployment_check(models[:-1],actors)
    for name in models[0].counts:counts[name]=sum(m.counts[name] for m in models)
    counts.update(stored_critic_labels=sum(m.S for m in models),stored_actor_scalars=sum(map(len,actors)),original_witness_indices=sum(m.S for m in models if m.kind=='witness'),maximum_coefficient_bits=max(m.bits for m in models))
    nonuniform=sum(any(len(set(map(lambda x:F(float(x)),np.diff(ax))))>1 for ax in model.axes) for model in models)
    return {'method':method,'N':N,'K':K,'M':M,'T':T,'price':p,'dimension':d,'models':[m.payload() for m in models],'actors':actors,'rows':rows,'terminal_error':str(eT),'terminal_width':str(terminal_width),'policy_bound_exact':str(bound),'policy_bound_upper':c.upper(bound),'pilot_weights':pilots,'nonuniform_date_models':nonuniform,'deployment':deployment,'counts':counts}

def coefficients(d,T,p):
    C,G,Fx,Fa,Ca,Ka=moduli(d,p);L=G;a=BETA**T*G*d;b=F(0);q=F(0)
    for t in range(T-1,-1,-1):
        D=Ca+BETA*Fa*L;q+=BETA**t*BETA*L*d/32
        L=C+BETA*Fx*L+D*Ka;a+=BETA**t*L*d;b+=BETA**t*D/8
    return a,b,q

def service(method,T,p,repeat,d,out):
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    affinity=None
    if hasattr(os,'sched_getaffinity'):
        affinity=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{affinity})
    warm=np.arange(4096)/4096
    for _ in range(8):warm=(warm+1)*.5
    start=time.perf_counter();cpu=time.process_time();out.mkdir(parents=True)
    attempts=[];first={str(q):None for q in TARGETS};cum={}
    for N,K,M in LADDERS[d]:
        begin=time.perf_counter();payload=rung(N,K,M,T,p,method,d)
        file=out/f'checkpoint-N{N}-K{K}-M{M}.json';digest=save(file,payload)
        for k,v in payload['counts'].items():cum[k]=max(cum.get(k,0),v) if k=='maximum_coefficient_bits' else cum.get(k,0)+v
        row={'N':N,'K':K,'M':M,'bound_exact':payload['policy_bound_exact'],'bound_upper':payload['policy_bound_upper'],'checkpoint':file.name,'checkpoint_sha256':digest,'checkpoint_bytes':file.stat().st_size,'prefix_seconds':time.perf_counter()-start,'prefix_cpu_seconds':time.process_time()-cpu,'rung_seconds':time.perf_counter()-begin,'counts':payload['counts'],'prefix_counts':dict(cum),'nonuniform_date_models':payload['nonuniform_date_models']}
        attempts.append(row)
        for q in TARGETS:
            if first[str(q)] is None and F(row['bound_exact'])<=q:first[str(q)]={k:row[k] for k in ('N','K','M','checkpoint','checkpoint_sha256','bound_exact','prefix_seconds','prefix_cpu_seconds')}
    record={'method':method,'dimension':d,'horizon':T,'price':p,'repeat':repeat,'attempts':attempts,'first_crossings':first,'cpu_affinity':affinity,'frequency_controlled':False,'platform':platform.platform(),'python':platform.python_version(),'numpy':np.__version__,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'clock_scope':'own primitives, pilots, compiler, integration, all failed rungs, actor, certificate, deployment checksum and checkpoint fsync; startup/warmup separately recorded','independent_direct_cost':'separate joint service','primitive_witness_coefficients':list(map(str,coefficients(d,T,p)))}
    digest=save(out/'record.json',record);save(out/'clock.json',{'record_sha256':digest,'seconds_through_record_fsync':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu})
    print(json.dumps({'method':method,'d':d,'T':T,'p':p,'repeat':repeat,'final_bound':attempts[-1]['bound_upper'],'seconds':time.perf_counter()-start}),flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--method',choices=METHODS,required=True);a.add_argument('--T',type=int,required=True);a.add_argument('--p',type=int,required=True);a.add_argument('--d',type=int,required=True);a.add_argument('--repeat',type=int,required=True);a.add_argument('--out',required=True);v=a.parse_args();service(v.method,v.T,v.p,v.repeat,v.d,v.out)
