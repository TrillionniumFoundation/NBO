"""From-primitives R48 services; no recorded observation is overwritten."""
from __future__ import annotations
import argparse, itertools, math, platform, resource, time
from common import *
from tensor import Model
METHODS=('compiled-witness','tensor-fvi','adaptive-fvi')
TARGETS=tuple(map(F,('4','2','1','1/2','1/4')))

def uniform_axes(N,d):return [np.arange(N+1,dtype=float)/N for _ in range(d)]
def adaptive_axes(pilot,axes,N):
    """Exact ranking of a fixed, positive pilot-curvature heuristic."""
    d=len(axes);values=np.asarray(pilot).reshape((5,)*d);out=[];weights=[]
    for j in range(d):
        curvature=[]
        for k in (1,2,3):
            a=np.take(values,k-1,axis=j).ravel();b=np.take(values,k,axis=j).ravel();cc=np.take(values,k+1,axis=j).ravel()
            curvature.append(max(abs(F(float(x))-2*F(float(y))+F(float(z))) for x,y,z in zip(a,b,cc)))
        w=[1+64*max(curvature[max(1,k)-1],curvature[min(3,k+1)-1]) for k in range(4)]
        knots=list(map(lambda k:F(k,4),range(5)))
        while len(knots)<N+1:
            candidates=[]
            for i,(a,b) in enumerate(zip(knots,knots[1:])):
                cell=min(3,int(4*(a+b)/2));candidates.append((-(b-a)**2*w[cell],a,i))
            i=min(candidates)[2];knots.insert(i+1,(knots[i]+knots[i+1])/2)
        out.append(np.array(list(map(float,knots))));weights.append(list(map(str,w)))
    return out,weights

def midpoint_sum(x,axis):
    n=x.lo.shape[axis];u=F(1,2**53);gamma=F(n+2)*u/(1-F(n+2)*u)
    magnitude=np.max(np.maximum(abs(x.lo),abs(x.hi)),axis=axis)
    err=c.rat_i(gamma*n)*I.point(magnitude)
    return I(np.nextafter(np.sum(x.lo,axis=axis)-err.hi,-np.inf),np.nextafter(np.sum(x.hi,axis=axis)+err.hi,np.inf))

def queries(nodes,N,p,future,counts):
    d=nodes.shape[1];caps=np.array([c.enclosure(F(1,8)+sum(map(lambda v:F(float(v)),x),F(0))/F(8*d))[0] for x in nodes])
    # The capacity lower endpoint is rounded down again after multiplication.
    actions=(caps[:,None]*np.arange(N+1)[None,:]/N)
    if d==3:actions=np.maximum(0,np.nextafter(actions,-np.inf))
    xi=np.repeat(nodes,N+1,axis=0);flat=actions.reshape(-1);low=np.empty(len(flat));high=np.empty(len(flat))
    zs=c.array_i([F(2*j+1-N,32*N) for j in range(N)])
    for begin in range(0,len(flat),1024):
        xx=xi[begin:begin+1024];aa=flat[begin:begin+1024];m=len(aa)
        shocks=I(np.tile(zs.lo,m),np.tile(zs.hi,m))
        nx=transition(I.point(np.repeat(xx,N,axis=0)),I.point(np.repeat(aa,N)),shocks)
        value=future.evaluate(nx);value=I(value.lo.reshape(m,N),value.hi.reshape(m,N))
        mean=midpoint_sum(value,1)/N
        err=c.rat_i(future.L*F(d,64*N))
        q=costs(I.point(xx),I.point(aa),p)+float(BETA)*(mean+I(-err.hi,err.hi))
        low[begin:begin+m]=q.lo;high[begin:begin+m]=q.hi
    counts['bellman_queries']+=len(flat);counts['innovation_midpoints']+=len(flat)*N
    counts['stage_cost_evaluations']+=len(flat)
    v,e=c.rounded_labels(I(low,high));v=v.reshape(len(nodes),N+1);indices=np.argmin(v,axis=1)
    return v[np.arange(len(nodes)),indices],actions[np.arange(len(nodes)),indices],e

def nearest_excess(model,L):
    ij=np.stack(np.unravel_index(np.arange(model.S),model.shape),axis=-1);choices=[]
    for j,ax in enumerate(model.axes):
        k=ij[:,j];left=(ax[k]+ax[np.maximum(k-1,0)])/2;right=(ax[k]+ax[np.minimum(k+1,len(ax)-1)])/2
        choices.append(np.stack((left,ax[k],right),axis=-1))
    best=-math.inf
    for offset in itertools.product((0,1,2),repeat=model.d):
        points=np.stack([choices[j][:,k] for j,k in enumerate(offset)],axis=-1)
        distance=isum(abs_i(I.point(points)-I.point(model.nodes)))
        diff=I.point(model.v)+c.rat_i(L)*distance-model.point(points)
        best=max(best,float(np.max(diff.hi)))
    return F(best),model.S*3**model.d

def deployment_check(models,actors):
    """A fixed finite checksum, IN the measured service, not an all-state proof."""
    d=models[0].d;grid=np.array(list(itertools.product(np.arange(5)/4,repeat=d)))
    # b=8 midpoint reports including boundary cells; the cell, not the center,
    # determines robust feasibility. True states may lie anywhere in the cell.
    bins=np.minimum(255,np.floor(grid*256).astype(int));lo=bins/256;center=(bins+.5)/256
    caps=cap(I.point(lo));out=[];repairs=0;ambiguities=0
    for model,a in zip(models,actors):
        raw,amb=model.actor(I.point(center),a);ambiguities+=amb
        if np.any(raw.lo!=raw.hi):raise AssertionError('Unresolved exact selector')
        repaired=np.minimum(raw.lo,caps.lo);executed=np.maximum(0,np.floor(repaired*4096)/4096)
        assert np.all(executed>=0) and np.all(executed<=caps.lo)
        repairs+=int(np.count_nonzero(executed<raw.lo));out.append(executed.tolist())
    return {'grid_states':len(grid),'bits':8,'quantum':'1/4096','repair_events':repairs,'ambiguities':ambiguities,'actions_sha256':hashlib.sha256(c.canonical(out)).hexdigest(),'scope':'finite deployment checksum; uniform theorem is separate'}

def rung(N,T,p,method,d=2):
    if N<2 or N&(N-1) or method not in METHODS or (method=='adaptive-fvi' and d!=2):raise ValueError('Invalid rung')
    C,G,Fx,Fa,Ca,Ka=moduli(d,p);kind='witness' if method=='compiled-witness' else 'fvi'
    counts={'bellman_queries':0,'innovation_midpoints':0,'stage_cost_evaluations':0,'terminal_cost_evaluations':0,'pilot_bellman_queries':0,'nearest_cell_vertices':0}
    axes=uniform_axes(N,d);pilot_weights=[]
    if method=='adaptive-fvi' and N>4:
        pn=np.array(list(itertools.product(*uniform_axes(4,d))))
        y,_=c.rounded_labels(costs(I.point(pn),I.point(np.zeros(len(pn))),p,True));counts['terminal_cost_evaluations']+=len(pn)
        axes,w=adaptive_axes(y,uniform_axes(4,d),N);pilot_weights.append({'date':T,'weights':w})
    nodes=np.array(list(itertools.product(*axes)))
    labels,eT=c.rounded_labels(costs(I.point(nodes),I.point(np.zeros(len(nodes))),p,True));counts['terminal_cost_evaluations']+=len(nodes)
    future=Model(axes,labels,kind,G);models=[None]*T+[future];actors=[None]*T;rows=[None]*T
    terminal_width=2*eT+2*G*future.h
    # Extra rounding at non-dyadic capacity in dimension three is bounded by
    # four binary64 ulps on [0,1]; zero extra is valid at dyadic capacities.
    k=F(1,8*N)+(F(1,2**50) if d==3 else 0)
    for t in range(T-1,-1,-1):
        A=C+BETA*Fx*future.L;D=Ca+BETA*Fa*future.L;L=A+D*Ka
        axes=uniform_axes(N,d)
        if method=='adaptive-fvi' and N>4:
            pn=np.array(list(itertools.product(*uniform_axes(4,d))))
            before=counts['bellman_queries'];py,_,_=queries(pn,N,p,future,counts)
            counts['pilot_bellman_queries']+=counts['bellman_queries']-before
            axes,w=adaptive_axes(py,uniform_axes(4,d),N);pilot_weights.append({'date':t,'weights':w})
        nodes=np.array(list(itertools.product(*axes)));labels,actions,e=queries(nodes,N,p,future,counts)
        current=Model(axes,labels,kind,L)
        if kind=='witness':u=D*k+e+2*L*current.h;selected=e;extra=F(0)
        else:
            u=D*k+e+L*current.h;extra,n=nearest_excess(current,L);counts['nearest_cell_vertices']+=n;selected=e+extra
        rows[t]={'date':t,'A':str(A),'D':str(D),'L_graph':str(L),'query_error':str(e),'state_cover':str(current.h),'action_cover':str(k),'quadrature_remainder':str(BETA*future.L*F(d,64*N)),'optimal_residual_upper':str(u),'selected_policy_upper':str(selected),'nearest_excess':str(extra),'component':str(u+selected)}
        models[t]=current;actors[t]=actions.tolist();future=current
    bound=sum((BETA**t*F(row['component']) for t,row in enumerate(rows)),F(0))+BETA**T*terminal_width
    deployment=deployment_check(models[:-1],actors)
    for name in models[0].counts:counts[name]=sum(m.counts[name] for m in models)
    counts.update(stored_critic_labels=sum(m.S for m in models),stored_actor_scalars=sum(len(a) for a in actors),original_witness_indices=sum(m.S for m in models if m.kind=='witness'),maximum_coefficient_bits=max(m.bits for m in models))
    payload={'method':method,'N':N,'T':T,'price':p,'dimension':d,'models':[m.payload() for m in models],'actors':actors,'rows':rows,'terminal_error':str(eT),'terminal_width':str(terminal_width),'policy_bound_exact':str(bound),'policy_bound_upper':c.upper(bound),'pilot_weights':pilot_weights,'deployment':deployment,'counts':counts}
    return payload

def service(method,T,p,repeat,d,out):
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    if hasattr(os,'sched_getaffinity'):
        affinity=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{affinity})
    else:affinity=None
    warm=np.arange(4096)/4096
    for _ in range(8):warm=(warm+1)*.5
    ladder=(4,8,16,32,64) if d==2 else ((4,8,16) if d==3 else (2,4,8))
    start=time.perf_counter();cpu=time.process_time();out.mkdir(parents=True)
    attempts=[];first={str(q):None for q in TARGETS};cum={}
    for N in ladder:
        begin=time.perf_counter();payload=rung(N,T,p,method,d)
        file=out/f'checkpoint-N{N}.json';digest=save(file,payload)
        for k,v in payload['counts'].items():cum[k]=max(cum.get(k,0),v) if k=='maximum_coefficient_bits' else cum.get(k,0)+v
        row={'N':N,'bound_exact':payload['policy_bound_exact'],'bound_upper':payload['policy_bound_upper'],'checkpoint_sha256':digest,'checkpoint_bytes':file.stat().st_size,'prefix_seconds':time.perf_counter()-start,'prefix_cpu_seconds':time.process_time()-cpu,'rung_seconds':time.perf_counter()-begin,'counts':payload['counts'],'prefix_counts':dict(cum)}
        attempts.append(row)
        for q in TARGETS:
            if first[str(q)] is None and F(row['bound_exact'])<=q:first[str(q)]={k:row[k] for k in ('N','bound_exact','prefix_seconds','prefix_cpu_seconds')}
    record={'method':method,'dimension':d,'horizon':T,'price':p,'repeat':repeat,'attempts':attempts,'first_crossings':first,'cpu_affinity':affinity,'frequency_controlled':False,'platform':platform.platform(),'python':platform.python_version(),'numpy':np.__version__,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'clock_scope':'primitives, pilot and compiler, integration, all failed rungs, actor, all-state certificate, finite acquired-state deployment checksum, fsync; startup/warmup separately recorded','arithmetic_counts_scope':'components, not complete FLOPs or bit operations','independent_direct_cost':'separate joint comparison service; not a zero-cost component'}
    digest=save(out/'record.json',record);save(out/'clock.json',{'record_sha256':digest,'seconds_through_record_fsync':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu})
    print(json.dumps({'method':method,'d':d,'T':T,'p':p,'repeat':repeat,'final_bound':attempts[-1]['bound_upper'],'seconds':time.perf_counter()-start}),flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--method',choices=METHODS,required=True);a.add_argument('--T',type=int,required=True);a.add_argument('--p',type=int,required=True);a.add_argument('--d',type=int,required=True);a.add_argument('--repeat',type=int,required=True);a.add_argument('--out',required=True);j=a.parse_args();service(j.method,j.T,j.p,j.repeat,j.d,j.out)
