"""R84 deterministic common-readout qualification. No refitting or resampling.

Floating linear programs propose multipliers only. Rational qualification,
Farkas and assignment duals determine every exclusion and economic endpoint.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import argparse,hashlib,itertools,json,os,platform,resource,subprocess,sys,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix
from calibrated80 import Calibrated
from qualification73 import simplex,dot
from study80 import problem
from barrier80 import menu,contrast,sparse
R=Path(__file__).resolve().parents[1]
MODELS=((8,'relu'),(8,'bernstein'),(16,'relu'),(16,'bernstein'))
EPS=tuple([F(0)]+[F(1,2**k) for k in (16,15,14,13,12)])
LIMIT=F(1,4096);PAIR_BUDGET=512

def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [encode(v) for v in x]
    if isinstance(x,np.generic):return x.item()
    return x

def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(encode(x),indent=2,sort_keys=True)+'\n')
def need(x,s):
    if not x:raise AssertionError(s)
def dyadic(v):return F(max(0,round(float(v)*2**40)),2**40)

def data(n,kind):
    source=R/f'results80/construction/{kind}-n{n}/service.json'
    original=R/f'results82/{kind}-n{n}.json'
    s=read(source);a=read(original)
    model=Calibrated(problem(s['stages'][1]['problem']),kind)
    need(F(s['stages'][1]['attained']['objective'])==F(a['reference_objective']),'Attained objective identity')
    return model,a,dict(construction_sha256=sha(source),actionwise_sha256=sha(original))

def event_constraints(n,kind,nodes,ids):
    ds=[];cs=[]
    for i in ids:
        node=nodes[i];cell=node['cell'];b=F(node['alternative_index'],4096)
        x=tuple(F(2*j+1,2*n) for j in cell)
        for a in menu(n,*cell):
            if a==b:continue
            d,c=contrast(x,a,b,kind);ds.append(d);cs.append(c)
    need(len(ds)==32*len(ids),'Full winner menu')
    return tuple(ds),tuple(cs)

def exact_dual(model,p,q,xi,nu,ds,cs):
    d=tuple(sum((w*row[k] for w,row in zip(nu,ds) if w),F(0)) for k in range(9))
    c=sum((w*z for w,z in zip(nu,cs) if w),F(0))
    return model.dual(p,q,xi,F(1),d,c)

def infeasibility(bounds,ds,cs):
    # min slack over the coefficient box. A positive exact support dual
    # excludes the whole event, independently of the qualification objective.
    A=np.zeros((len(ds),10));A[:,:9]=np.asarray(ds,dtype=float);A[:,-1]=-1
    c=np.zeros(10);c[-1]=1
    ans=linprog(c,A_ub=A,b_ub=-np.asarray(cs,dtype=float),bounds=[(-float(b),float(b)) for b in bounds]+[(0,None)],method='highs')
    if not ans.success:return None
    weights=tuple(dyadic(-x) for x in ans.ineqlin.marginals)
    if sum(weights)>1:weights=tuple(w/sum(weights) for w in weights)
    slopes=tuple(sum((w*d[k] for w,d in zip(weights,ds) if w),F(0)) for k in range(9))
    gap=sum((w*c for w,c in zip(weights,cs) if w),F(0))-dot(bounds,[abs(s) for s in slopes])
    return dict(weights=sparse(weights),separation=gap) if gap>0 else None

def qualify(model,ds,cs,arrays):
    P=model.problem;n=len(P.lower);A,rhs,c,bounds=arrays
    scales=tuple(max(max(map(abs,d)),abs(v),F(1,2**40)) for d,v in zip(ds,cs))
    extra=np.zeros((len(ds),12));extra[:,:9]=np.asarray([[v/s for v in d] for d,s in zip(ds,scales)],dtype=float)
    ans=linprog(c,A_ub=np.vstack((A,extra)),b_ub=np.r_[rhs,[-float(v/s) for v,s in zip(cs,scales)]],bounds=bounds,method='highs',options={'presolve':True,'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
    if ans.success:
        p=simplex(-ans.ineqlin.marginals[:n],40);q=simplex(-ans.ineqlin.marginals[n:2*n],40)
        xi=tuple(dyadic(-v) for v in ans.ineqlin.marginals[2*n:2*n+16]);alpha=2*P.radius
        if sum(xi)>alpha:xi=tuple(v*alpha/sum(xi) for v in xi)
        nu=tuple(F(max(0.,-float(v)))/s for v,s in zip(ans.ineqlin.marginals[-len(ds):],scales))
        farkas=None
    else:
        p=q=(F(1),)+(F(0),)*(n-1);xi=(F(0),)*16;nu=(F(0),)*len(ds)
        farkas=infeasibility(P.bounds,ds,cs) if int(ans.status)==2 else None
    value=exact_dual(model,p,q,xi,nu,ds,cs)
    return dict(lower=value,p=sparse(p),q=sparse(q),xi=sparse(xi),nu=sparse(nu),infeasibility=farkas,
        solver_success=bool(ans.success),solver_status=int(ans.status),solver_message=str(ans.message),winner_inequalities=len(ds))

def is_allowed(cert,cap):return cert['infeasibility'] is None and F(cert['effective_lower'])<=cap

def select_pairs(original,singles):
    U=F(original['reference_objective']);nodes=original['admitted_switches'];bands=original['tiers'][-1]['accumulated_intervals']
    active=[i for i,c in enumerate(singles) if is_allowed(c,U+LIMIT)]
    # A fixed deterministic cost-bound rule, not a new statistical selection.
    # For a large set retain both adverse interval extrema at each cell.
    if len(active)>128:
        chosen=set()
        for cell in sorted({tuple(nodes[i]['cell']) for i in active}):
            ids=[i for i in active if tuple(nodes[i]['cell'])==cell]
            chosen.add(min(ids,key=lambda i:(F(bands[i][0]),i)))
            chosen.add(max(ids,key=lambda i:(F(bands[i][1]),-i)))
        active=sorted(chosen)
    score={i:max(abs(F(bands[i][0])),abs(F(bands[i][1]))) for i in active}
    pairs=[(i,j) for i,j in itertools.combinations(active,2) if nodes[i]['cell']!=nodes[j]['cell']]
    pairs.sort(key=lambda ij:(-score[ij[0]]*score[ij[1]],ij))
    return pairs[:PAIR_BUDGET],dict(active_singletons=sum(is_allowed(c,U+LIMIT) for c in singles),pair_seed_nodes=len(active),eligible_pairs=len(pairs),pair_budget=PAIR_BUDGET)

def assignment(weights,cells,edges,ncells):
    # Primal: one action per cell, pair conflicts, nonnegative relaxed masses.
    # The recovered dual is verified by a max-over-actions in each cell.
    n=len(weights);eq=csr_matrix((np.ones(n),(cells,np.arange(n))),shape=(ncells,n))
    if edges:
        ii=[];jj=[]
        for k,(i,j) in enumerate(edges):ii.extend((k,k));jj.extend((i,j))
        A=csr_matrix((np.ones(len(ii)),(ii,jj)),shape=(len(edges),n))
        ans=linprog(-np.asarray(weights,dtype=float),A_ub=A,b_ub=np.ones(len(edges)),A_eq=eq,b_eq=np.ones(ncells),bounds=(0,None),method='highs')
        lam=tuple(dyadic(-v) for v in ans.ineqlin.marginals) if ans.success else (F(0),)*len(edges)
    else:ans=None;lam=()
    hit=[F(0)]*n
    for w,(i,j) in zip(lam,edges):hit[i]+=w;hit[j]+=w
    alpha=[F(0)]*ncells
    for k,cell in enumerate(cells):alpha[cell]=max(alpha[cell],weights[k]-hit[k])
    value=sum(alpha,F(0))+sum(lam,F(0));rect=[F(0)]*ncells
    for w,cell in zip(weights,cells):rect[cell]=max(rect[cell],w)
    if value>sum(rect,F(0)):lam=(F(0),)*len(edges);alpha=rect;value=sum(rect,F(0))
    need(value>=0,'Reference choice supplies zero')
    return dict(upper=value,cell_dual=alpha,edge_dual=sparse(lam),solver_success=True if ans is None else bool(ans.success))

def economic(original,singles,pairs):
    n=original['n'];N=n*n;nodes=original['admitted_switches'];bands=original['tiers'][-1]['accumulated_intervals'];U=F(original['reference_objective']);rows=[]
    for eps in EPS:
        active=[i for i,c in enumerate(singles) if is_allowed(c,U+eps)]
        ids=[-j-1 for j in range(N)]+active;index={v:i for i,v in enumerate(ids)}
        cells=list(range(N))+[nodes[i]['cell'][0]*n+nodes[i]['cell'][1] for i in active]
        upper=[F(0)]*N+[F(bands[i][1])/N for i in active]
        minuslower=[F(0)]*N+[-F(bands[i][0])/N for i in active]
        edge_ids=[k for k,e in enumerate(pairs) if all(i in index for i in e['nodes']) and (e['certificate']['infeasibility'] is not None or F(e['certificate']['effective_lower'])>U+eps)]
        edges=[tuple(index[i] for i in pairs[k]['nodes']) for k in edge_ids]
        up=assignment(upper,cells,edges,N);low=assignment(minuslower,cells,edges,N)
        oldlo=[F(0)]*N;oldhi=oldlo.copy();singlelo=oldlo.copy();singlehi=oldlo.copy()
        for i,node in enumerate(nodes):
            cell=node['cell'][0]*n+node['cell'][1];lo,hi=map(F,bands[i])
            if F(node['switch_lower'])<=U+eps:oldlo[cell]=min(oldlo[cell],lo/N);oldhi[cell]=max(oldhi[cell],hi/N)
            if i in index:singlelo[cell]=min(singlelo[cell],lo/N);singlehi[cell]=max(singlehi[cell],hi/N)
        band=(-low['upper'],up['upper']);legacy=(sum(oldlo,F(0)),sum(oldhi,F(0)));single=(sum(singlelo,F(0)),sum(singlehi,F(0)))
        need(legacy[0]<=single[0]<=band[0]<=0<=band[1]<=single[1]<=legacy[1],'Nested economic enclosures')
        rows.append(dict(extra_objective=eps,node_ids=ids,pair_ids=edge_ids,active_alternatives=len(active),active_conflicts=len(edges),
            original_actionwise_band=legacy,complete_menu_band=single,compatible_band=band,upper_dual=up,negative_lower_dual=low))
    return rows

def model_run(n,kind):
    started=time.perf_counter();model,old,binding=data(n,kind);nodes=old['admitted_switches'];U=F(old['reference_objective']);arrays=model.arrays();cache={}
    singles=[]
    for i,node in enumerate(nodes):
        ds,cs=event_constraints(n,kind,nodes,(i,));cache[i]=(ds,cs)
        c=qualify(model,ds,cs,arrays);c['effective_lower']=max(c['lower'],F(node['switch_lower']));singles.append(c)
    singleton_seconds=time.perf_counter()-started
    chosen,selection=select_pairs(old,singles);pairs=[];began=time.perf_counter()
    for number,(i,j) in enumerate(chosen):
        a,b=cache[i];c,d=cache[j];cert=qualify(model,a+c,b+d,arrays)
        cert['effective_lower']=max(cert['lower'],F(singles[i]['effective_lower']),F(singles[j]['effective_lower']))
        pairs.append(dict(nodes=[i,j],certificate=cert))
        if (number+1)%128==0:print(kind,n,'joint event certificates',number+1,flush=True)
    pair_seconds=time.perf_counter()-began;began=time.perf_counter();cost=economic(old,singles,pairs)
    record=dict(name=old['name'],n=n,basis=kind,source=binding,reference_objective=U,singletons=singles,pair_selection=selection,pairs=pairs,economic=cost)
    save(R/f'results84/{kind}-n{n}.json',record)
    timing=dict(singleton_seconds=singleton_seconds,pair_seconds=pair_seconds,economic_seconds=time.perf_counter()-began,total_seconds=time.perf_counter()-started)
    print(json.dumps(encode(dict(name=old['name'],singletons=len(singles),pairs=len(pairs),timing=timing,bands=[{k:x[k] for k in ('extra_objective','active_alternatives','active_conflicts','original_actionwise_band','complete_menu_band','compatible_band')} for x in cost])),indent=2),flush=True)
    return record,timing

def pair_band(contrasts,a,b):
    key=a+'-minus-'+b
    if key in contrasts:return tuple(map(F,contrasts[key]['interval_exact']))
    lo,hi=map(F,contrasts[b+'-minus-'+a]['interval_exact']);return -hi,-lo

def transfer(records):
    costs=read(R/'results80/cost/summary.json');contrasts=costs['inference']['conditional']['contrasts'];out=[]
    for a,b in itertools.combinations(records,2):
        l,u=pair_band(contrasts,a['name'],b['name'])
        for i,eps in enumerate(EPS):
            row=dict(first=a['name'],second=b['name'],extra_objective=eps,attained_band=[l,u])
            for method in ('original_actionwise_band','complete_menu_band','compatible_band'):
                al,au=map(F,a['economic'][i][method]);bl,bu=map(F,b['economic'][i][method]);row[method]=[l+al-bu,u+au-bl]
            L,U=row['compatible_band'];row['sign']='positive' if L>0 else 'negative' if U<0 else 'unresolved';row['equivalent_at_1_over_256']=(-F(1,256)<L and U<F(1,256));out.append(row)
    return dict(pairwise=out,new_independent_cost_rows=0,new_fits=0,original_cost_sha256=sha(R/'results80/cost/summary.json'))

def freeze():
    paths=['code/'+x+'.py' for x in ('compatible84','verify84','calibrated80','qualification73','barrier80','study80','study73','dual81')]
    paths+=['PROTOCOL84.md','results80/cost/summary.json']
    for n,k in MODELS:paths.extend([f'results80/construction/{k}-n{n}/service.json',f'results80/barriers/{k}-n{n}.json',f'results82/{k}-n{n}.json'])
    record=dict(files={p:sha(R/p) for p in paths},models=MODELS,tolerances=EPS,max_extra_objective=LIMIT,pair_budget=PAIR_BUDGET,
        scope='Deterministic postprocessing of a fixed simultaneous cost event; development pilot disclosed, no prospective statistical sampling claim.')
    path=R/'SOURCE_FREEZE84.json'
    if path.exists():need(read(path)==encode(record),'Locked source changed')
    else:save(path,record)
    return record

def execute():
    start=time.perf_counter();lock=freeze();out=R/'results84';need(not out.exists(),'Never overwrite a scientific execution');out.mkdir()
    records=[];timings={}
    for n,k in MODELS:
        rec,timing=model_run(n,k);records.append(rec);timings[rec['name']]=timing
    save(out/'transfer.json',transfer(records))
    certs=[c for r in records for c in r['singletons']]+[e['certificate'] for r in records for e in r['pairs']]
    try:head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
    except subprocess.CalledProcessError:head=None
    result=dict(status='passed',source_commit=head,source_freeze_sha256=sha(R/'SOURCE_FREEZE84.json'),
        singleton_certificates=sum(len(r['singletons']) for r in records),joint_event_certificates=sum(len(r['pairs']) for r in records),
        exact_infeasibility_certificates=sum(c['infeasibility'] is not None for c in certs),lp_non_success=sum(not c['solver_success'] for c in certs),
        model_tolerance_records=len(records)*len(EPS),phase_seconds=timings,seconds_before_summary=time.perf_counter()-start,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,python=sys.version,platform=platform.platform(),machine=platform.machine(),
        new_fit_attempts=0,new_independent_cost_rows=0,new_kernel_integration_boxes=0,
        inherited_bin_evidence='Previously source-qualified R82/R83 actionwise bins and R80 simultaneous attained costs; no new path simulation or relabeling as new independent data.',
        records_sha256={p.name:sha(p) for p in sorted(out.glob('*.json'))})
    save(out/'summary.json',result);save(out/'clock.json',dict(seconds_through_summary=time.perf_counter()-start,summary_sha256=sha(out/'summary.json')))
    print(json.dumps({k:result[k] for k in ('status','source_commit','singleton_certificates','joint_event_certificates','exact_infeasibility_certificates','lp_non_success','seconds_before_summary')},indent=2),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('freeze','execute'));a=p.parse_args();freeze() if a.mode=='freeze' else execute()
