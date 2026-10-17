"""Independent R84 certificate checker. No optimizer or production-code imports.

Uses the independently derived R81 antiderivative feature implementation.
Reconstructs all winner menus, support bounds, conflict cuts and cost transfers.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib,itertools,json,time
import dual81 as independent
R=Path(__file__).resolve().parents[1]
MODELS=((8,'relu'),(8,'bernstein'),(16,'relu'),(16,'bernstein'))
EPS=(F(0),F(1,65536),F(1,32768),F(1,16384),F(1,8192),F(1,4096))
MAX=F(1,4096);BUDGET=512

def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def need(x,s):
    if not x:raise AssertionError(s)
def unpack(raw,n):
    v=[F(0)]*n;seen=set()
    for i,w in raw:
        need(isinstance(i,int) and not isinstance(i,bool) and 0<=i<n and i not in seen,'Unique sparse index')
        v[i]=F(w);need(v[i]>=0,'Nonnegative multiplier');seen.add(i)
    return tuple(v)

def constraints(n,kind,nodes,ids):
    ds=[];cs=[]
    for k in ids:
        i,j=nodes[k]['cell'];b=F(nodes[k]['alternative_index'],4096)
        cap=(4096*(2*n+i+j))//(16*n);actions=tuple(F(cap*l//32,4096) for l in range(33))
        need(b in actions,'Candidate belongs to original robust menu')
        x=(F(2*i+1,2*n),F(2*j+1,2*n))
        for a in actions:
            if a==b:continue
            d,c=independent.action_contrast(x,a,b,kind);ds.append(d);cs.append(c)
    need(len(ds)==32*len(ids),'Entire independent winner menu')
    return ds,cs

def problem(raw):
    return (tuple(tuple(map(F,row)) for row in raw['features']),tuple(map(F,raw['lower'])),tuple(map(F,raw['upper'])),tuple(map(F,raw['bounds'])),F(raw['radius']),F(raw['bellman_lipschitz']))

def certificate(P,kind,ds,cs,record,prior):
    n=len(P[1]);xi=unpack(record['xi'],16);nu=unpack(record['nu'],len(ds))
    d=tuple(sum((w*row[k] for w,row in zip(nu,ds)),F(0)) for k in range(9));c=sum((w*x for w,x in zip(nu,cs)),F(0))
    lower=independent.lower_bound(P,record['p'],record['q'],xi,F(1),d,c,kind)
    need(lower==F(record['lower']),'Independent qualification support dual')
    need(max([lower]+list(map(F,prior)))==F(record['effective_lower']),'Barrier intersection')
    need(record['winner_inequalities']==len(ds),'Winner inequality count')
    f=record['infeasibility']
    if f is not None:
        w=unpack(f['weights'],len(ds));need(sum(w)<=1,'Slack dual normalization')
        slope=tuple(sum((a*row[k] for a,row in zip(w,ds)),F(0)) for k in range(9))
        gap=sum((a*b for a,b in zip(w,cs)),F(0))-sum((B*abs(g) for B,g in zip(P[3],slope)),F(0))
        need(gap==F(f['separation']) and gap>0,'Strict exact infeasibility separation')
    return lower

def allowed(cert,cap):return cert['infeasibility'] is None and F(cert['effective_lower'])<=cap

def pair_roster(old,singles):
    nodes=old['admitted_switches'];bands=old['tiers'][-1]['accumulated_intervals'];U=F(old['reference_objective'])
    active=[i for i,x in enumerate(singles) if allowed(x,U+MAX)];count=len(active)
    if count>128:
        grouped={}
        for i in active:grouped.setdefault(tuple(nodes[i]['cell']),[]).append(i)
        chosen=set()
        for cell,ids in sorted(grouped.items()):
            chosen.add(min(ids,key=lambda i:(F(bands[i][0]),i)))
            chosen.add(max(ids,key=lambda i:(F(bands[i][1]),-i)))
        active=sorted(chosen)
    weights={i:max(abs(F(bands[i][0])),abs(F(bands[i][1]))) for i in active}
    pairs=[(i,j) for i,j in itertools.combinations(active,2) if nodes[i]['cell']!=nodes[j]['cell']]
    pairs.sort(key=lambda e:(-weights[e[0]]*weights[e[1]],e))
    return pairs[:BUDGET],dict(active_singletons=count,pair_seed_nodes=len(active),eligible_pairs=len(pairs),pair_budget=BUDGET)

def assignment_dual(weights,cells,edges,ncells,raw):
    alpha=tuple(map(F,raw['cell_dual']));lam=unpack(raw['edge_dual'],len(edges));need(len(alpha)==ncells and min(alpha)>=0,'Cell dual dimensions and signs')
    hit=[F(0)]*len(weights)
    for v,(i,j) in zip(lam,edges):hit[i]+=v;hit[j]+=v
    for i,(w,cell) in enumerate(zip(weights,cells)):need(alpha[cell]+hit[i]>=w,'Every assignment-dual inequality')
    value=sum(alpha,F(0))+sum(lam,F(0));need(value==F(raw['upper']),'Exact economic support value')
    return value

def verify_model(n,kind):
    path=R/f'results84/{kind}-n{n}.json';r=read(path);old=read(R/f'results82/{kind}-n{n}.json');source=R/f'results80/construction/{kind}-n{n}/service.json';s=read(source)
    need(r['source']==dict(construction_sha256=sha(source),actionwise_sha256=sha(R/f'results82/{kind}-n{n}.json')),'Original-law input bindings')
    P=problem(s['stages'][1]['problem']);nodes=old['admitted_switches'];U=F(old['reference_objective']);need(U==F(r['reference_objective']),'Reference objective')
    need((r['n'],r['basis'],r['name'])==(n,kind,old['name']),'Model identity')
    singles=r['singletons'];need(len(singles)==len(nodes),'No singleton omitted');cache={}
    for i,c in enumerate(singles):
        ds,cs=constraints(n,kind,nodes,(i,));cache[i]=(ds,cs);certificate(P,kind,ds,cs,c,[nodes[i]['switch_lower']])
    selected,meta=pair_roster(old,singles);need(meta==r['pair_selection'] and len(selected)==len(r['pairs']),'Predetermined pair rule')
    for pair,(i,j) in zip(r['pairs'],selected):
        need(pair['nodes']==[i,j],'Pair order and identity')
        ds,cs=cache[i];dt,ct=cache[j];certificate(P,kind,ds+dt,cs+ct,pair['certificate'],[singles[i]['effective_lower'],singles[j]['effective_lower']])
    bands=old['tiers'][-1]['accumulated_intervals'];N=n*n;need(len(r['economic'])==len(EPS),'Every tolerance')
    tested_inequalities=0;stronger_single=stronger_joint=0
    for eps,row in zip(EPS,r['economic']):
        need(F(row['extra_objective'])==eps,'Tolerance identity')
        active=[i for i,c in enumerate(singles) if allowed(c,U+eps)];ids=[-i-1 for i in range(N)]+active;lookup={v:i for i,v in enumerate(ids)}
        need(row['node_ids']==ids,'Complete allowed assignment roster')
        cells=list(range(N))+[nodes[i]['cell'][0]*n+nodes[i]['cell'][1] for i in active]
        edges=[];edge_ids=[]
        for k,pair in enumerate(r['pairs']):
            cert=pair['certificate']
            if all(i in lookup for i in pair['nodes']) and (cert['infeasibility'] is not None or F(cert['effective_lower'])>U+eps):
                edges.append(tuple(lookup[i] for i in pair['nodes']));edge_ids.append(k)
        need(row['pair_ids']==edge_ids and row['active_alternatives']==len(active) and row['active_conflicts']==len(edges),'All strict conflict cuts')
        upweights=[F(0)]*N+[F(bands[i][1])/N for i in active];lowweights=[F(0)]*N+[-F(bands[i][0])/N for i in active]
        up=assignment_dual(upweights,cells,edges,N,row['upper_dual']);neglo=assignment_dual(lowweights,cells,edges,N,row['negative_lower_dual'])
        tested_inequalities+=2*len(ids)
        need(list(map(F,row['compatible_band']))==[-neglo,up],'Economic endpoint direction')
        oldlo=[F(0)]*N;oldhi=oldlo.copy();newlo=oldlo.copy();newhi=oldlo.copy()
        for i,node in enumerate(nodes):
            cell=node['cell'][0]*n+node['cell'][1];l,h=map(F,bands[i])
            if F(node['switch_lower'])<=U+eps:oldlo[cell]=min(oldlo[cell],l/N);oldhi[cell]=max(oldhi[cell],h/N)
            if i in lookup:newlo[cell]=min(newlo[cell],l/N);newhi[cell]=max(newhi[cell],h/N)
        before=[sum(oldlo,F(0)),sum(oldhi,F(0))];single=[sum(newlo,F(0)),sum(newhi,F(0))]
        need(list(map(F,row['original_actionwise_band']))==before,'Independent inherited actionwise enclosure')
        need(list(map(F,row['complete_menu_band']))==single,'Independent whole-menu enclosure')
        need(before[0]<=single[0]<=-neglo<=0<=up<=single[1]<=before[1],'Verified nonwidening')
        stronger_single+=single!=before;stronger_joint+=[-neglo,up]!=single
    return r,dict(name=r['name'],singletons=len(singles),joint_events=len(r['pairs']),assignment_inequalities=tested_inequalities,
        strictly_tighter_winner_tolerances=stronger_single,strictly_tighter_compatibility_tolerances=stronger_joint)

def band(contrasts,a,b):
    if a+'-minus-'+b in contrasts:return tuple(map(F,contrasts[a+'-minus-'+b]['interval_exact']))
    l,u=map(F,contrasts[b+'-minus-'+a]['interval_exact']);return -u,-l

def verify():
    start=time.perf_counter();lock=read(R/'SOURCE_FREEZE84.json')
    for p,h in lock['files'].items():need(sha(R/p)==h,'Frozen source/input '+p)
    need(lock['pair_budget']==BUDGET and tuple(map(F,lock['tolerances']))==EPS,'Independent declared design')
    records=[];summaries=[]
    for n,k in MODELS:
        record,summary=verify_model(n,k);records.append(record);summaries.append(summary)
    report=read(R/'results84/transfer.json');costpath=R/'results80/cost/summary.json';costs=read(costpath)['inference']['conditional']['contrasts'];need(report['original_cost_sha256']==sha(costpath),'Original cost event')
    pos=0
    for a,b in itertools.combinations(records,2):
        l,u=band(costs,a['name'],b['name'])
        for i,eps in enumerate(EPS):
            row=report['pairwise'][pos];pos+=1
            need((row['first'],row['second'],F(row['extra_objective']))==(a['name'],b['name'],eps),'Full comparison roster')
            need(list(map(F,row['attained_band']))==[l,u],'Attained cost interval')
            for method in ('original_actionwise_band','complete_menu_band','compatible_band'):
                al,au=map(F,a['economic'][i][method]);bl,bu=map(F,b['economic'][i][method]);need(list(map(F,row[method]))==[l+al-bu,u+au-bl],'Classwise interval transfer')
            L,U=map(F,row['compatible_band']);need(row['sign']==('positive' if L>0 else 'negative' if U<0 else 'unresolved'),'Strict sign')
            need(row['equivalent_at_1_over_256']==(-F(1,256)<L and U<F(1,256)),'Strict equivalence')
    need(pos==len(report['pairwise']) and report['new_independent_cost_rows']==0 and report['new_fits']==0,'No new observations')
    old=read(R/'results84/summary.json');clock=read(R/'results84/clock.json');need(sha(R/'results84/summary.json')==clock['summary_sha256'],'Execution clock binding')
    for p,h in old['records_sha256'].items():need(sha(R/'results84'/p)==h,'Output identity '+p)
    need(old['source_freeze_sha256']==sha(R/'SOURCE_FREEZE84.json'),'Execution source lock')
    result=dict(status='passed',services=summaries,independent_qualification_certificates=sum(s['singletons']+s['joint_events'] for s in summaries),
        independent_assignment_inequalities=sum(s['assignment_inequalities'] for s in summaries),class_cost_comparisons=pos,new_independent_rows=0,new_fit_attempts=0,
        independent_arithmetic='fractions; independent antiderivative feature means and sparse support dual; no LP solver or compatible84 import',
        seconds=time.perf_counter()-start,execution_summary_sha256=sha(R/'results84/summary.json'),scope='Every new winner, joint-event and economic dual; inherited bin qualification is separately rerun by the full publication build.')
    independent.save(R/'audit/VERIFY84.json',result);print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':verify()
