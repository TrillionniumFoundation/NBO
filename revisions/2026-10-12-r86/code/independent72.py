"""Independent rational audit of new witness transfers and ReLU integrals.

No production cache, interval, query, or moment routine is imported. The
large inherited optimal-value fills remain explicit trusted dependencies;
this checker does not relabel their serialized endpoints as independent
regeneration of their descendant trees.
"""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,json,time
R=Path(__file__).resolve().parents[1]

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def need(ok,label):
    if not ok:raise AssertionError(label)
def model_bounds(r,d):
    g=Q(10,d)
    for _ in range(r-1):g=Q(1037,128*d)+Q(705,1024)*g
    return Q(1037,128*d)+Q(705,1024)*g,Q(8,d)+Q(165,256)*g,Q(13,16)+Q(45*d,128)*g

def check_trace(rows):
    hits=0;geometric=0;repairs=0;fills=0;known={}
    for row in rows:
        x=list(map(Q,row['state']));a=list(map(Q,row['action']));cap=Q(1,8)+sum(x)/(8*len(x));L=Q(row['lower']);U=Q(row['upper']);tol=Q(row['tolerance'])
        need(all(0<=z<=1 for z in x) and all(z>=0 and (z*2**32).denominator==1 for z in a) and sum(a)<=cap,'feasible lattice action')
        need(L<=U and U-L<=tol,'returned width')
        if row['kind']=='fill':
            fills+=1;known[(row['context'],row['remaining'],tuple(x),tuple(a),L,U)]=True;continue
        need(row['kind']=='hit','trace kind');hits+=1
        y=list(map(Q,row['source_state']));old=list(map(Q,row['source_action']));ell=Q(row['source_lower']);upper=Q(row['source_upper'])
        need((row['context'],row['remaining'],tuple(y),tuple(old),ell,upper) in known,'transport source has no paid fill in this process')
        dist=sum(abs(p-q) for p,q in zip(x,y));move=sum(abs(p-q) for p,q in zip(a,old));lv,lx,la=model_bounds(row['remaining'],len(x))
        expected_l=max(Q(0),ell-lv*dist);expected_u=upper+lx*dist+la*move
        need(L<=expected_l and U>=expected_u,'independent outward transport')
        need(Q(row['exact_lower'])==expected_l and Q(row['exact_upper'])==expected_u,'exact transport formulas')
        geometric+=int(dist>0);repairs+=int(move>0)
    return dict(hits=hits,geometric_hits=geometric,capacity_repairs=repairs,fills=fills,queries=len(rows))

def polygon(c,radii):
    rr=[abs(v) for v in radii if v]
    if not rr:return max(Q(0),c)
    if len(rr)==1:
        v=rr[0];cut=max(-v,min(v,-c));return (c*(v-cut)+(v*v-cut*cut)/2)/(2*v)
    a,b=rr;vertices=[(-a,-b),(a,-b),(a,b),(-a,b)];positive=[]
    f=lambda z:c+z[0]+z[1]
    for j,p in enumerate(vertices):
        q=vertices[(j+1)%4];pval=f(p);qval=f(q)
        if pval>=0:positive.append(p)
        if (pval<0<qval) or (qval<0<pval):
            weight=pval/(pval-qval);positive.append(tuple(p[k]+weight*(q[k]-p[k]) for k in (0,1)))
    if len(positive)<3:return Q(0)
    # Integrate affine c+x+y through oriented area and first moments.
    area2=Q(0);mx6=Q(0);my6=Q(0)
    for j,p in enumerate(positive):
        q=positive[(j+1)%len(positive)];cross=p[0]*q[1]-q[0]*p[1]
        area2+=cross;mx6+=(p[0]+q[0])*cross;my6+=(p[1]+q[1])*cross
    return (c*area2/2+mx6/6+my6/6)/(4*a*b)

def main():
    begin=time.perf_counter();freeze=json.loads((R/'SOURCE_FREEZE72.json').read_text())
    for file,h in freeze['source_files'].items():need(sha(R.parent/file)==h,'source freeze '+file)
    rows=[];failed=[]
    for index,task in enumerate(freeze['tasks']):
        receipts=json.loads((R/'results72'/f'catalogue-{index}.json').read_text())
        need(len(receipts)==task['repetitions']*3,'catalogue count')
        for receipt in receipts:
            folder=R/'results72'/f"{task['name']}-{receipt['mode']}-r{receipt['repetition']}"
            for name,h in receipt['files_sha256'].items():need(sha(folder/name)==h,'process record hash')
            if receipt['returncode']!=0:failed.append(receipt);continue
            summary=json.loads((folder/'summary.json').read_text());trace=json.loads((folder/'trace.json').read_text());check=check_trace(trace)
            need(check['queries']==task['blocks'],'query count');need(check['hits']==summary['cache_counts']['hits'],'hit count')
            need(check['fills']==summary['cache_counts']['misses'],'fill count');need(summary['cache_counts']['max_records']<=128,'storage cap')
            rows.append(dict(task=task['name'],mode=receipt['mode'],rep=receipt['repetition'],complete_seconds=receipt['complete_process_seconds'],
                q_queries=summary['recursive_counts'].get('q_queries',0),peak_rss_kib=summary['peak_rss_kib'],**check))
    integrals=json.loads((R/'results72/conditional-integrals.json').read_text());groups={}
    for row in integrals:
        d=row['d'];m=row['m'];x=list(map(Q,row['state']));a=list(map(Q,row['action']));w=list(map(Q,row['weights']));bias=Q(row['bias'])
        need(sum(a)<=Q(1,8)+sum(x)/(8*d),'integration action feasibility')
        center=bias
        for j in range(d):
            drift=Q(1,16)+Q(9,16)*x[j]+x[(j+1)%d]/8-x[j]*x[(j+1)%d]/16
            drift+=(Q(1,2) if j%2==0 else Q(1,4))*a[0]
            if m==2:drift+=(Q(1,4) if j%2==0 else Q(1,2))*a[1]
            center+=w[j]*drift
        shocks=[sum((w[j] if j%2==0 else -w[j]) for j in range(d))/32]
        if m==2:shocks.append(sum(w)/64)
        need(center==Q(row['center']) and shocks==list(map(Q,row['radii'])),'original transition projections')
        need(polygon(center,shocks)==Q(row['mean_exact']),'independent polygon conditional integral')
        key=f'd{d}-m{m}';groups[key]=groups.get(key,0)+1
    report=dict(status='passed',services=len(rows),failed_services=len(failed),failures=failed,rows=rows,
        checked_query_returns=sum(x['queries'] for x in rows),checked_transport_returns=sum(x['hits'] for x in rows),
        checked_geometric_returns=sum(x['geometric_hits'] for x in rows),capacity_repairs=sum(x['capacity_repairs'] for x in rows),
        exact_conditional_integrals=len(integrals),conditional_groups=groups,seconds=time.perf_counter()-begin,
        new_independent_policy_cost_samples=0,
        scope='Every new transport acceptance and rational ReLU conditional moment checked independently; inherited recursive fill internals not independently regenerated.')
    p=R/'audit/INDEPENDENT72.json';p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('rows','failures')},indent=2))
if __name__=='__main__':main()
