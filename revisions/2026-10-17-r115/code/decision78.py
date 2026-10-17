"""Exact simultaneous controller-choice certificates; no new observations.

Edge (a,b,c) means theta[b]-theta[a] <= c. All bounds are Fraction,
and every sharp contrast comes with a feasible attaining cost potential.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING
import hashlib,itertools,json,time

R=Path(__file__).resolve().parents[1]
SOURCE_SHA='e6ceaab6665b91d9224e6f8b77146b455ff5ce71f8cac5e838dec4778ba194f3'

def sha(p):
    with Path(p).open('rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()

def closure(n,edges):
    """Floyd closure with negative-cycle rejection, including self-loops."""
    if n<1:raise ValueError('Empty graph')
    d=[[None]*n for _ in range(n)]
    for i in range(n):d[i][i]=F(0)
    for a,b,c in edges:
        if not (0<=a<n and 0<=b<n):raise ValueError('Edge vertex outside graph')
        c=F(c)
        if d[a][b] is None or c<d[a][b]:d[a][b]=c
    for k in range(n):
        for a in range(n):
            for b in range(n):
                if d[a][k] is not None and d[k][b] is not None:
                    v=d[a][k]+d[k][b]
                    if d[a][b] is None or v<d[a][b]:d[a][b]=v
        if any(d[i][i]<0 for i in range(n)):
            raise ValueError('Inconsistent intervals: negative constraint cycle')
    if any(v is None for row in d for v in row):
        raise ValueError('Unbounded contrast: finite marginal anchor required')
    return d

def independent_closure(n,edges):
    """Separate single-source Bellman--Ford implementation."""
    rows=[]
    for s in range(n):
        d=[None]*n;d[s]=F(0)
        for _ in range(n-1):
            old=d[:]
            for a,b,c in edges:
                if old[a] is not None:
                    v=old[a]+F(c)
                    if d[b] is None or v<d[b]:d[b]=v
        for a,b,c in edges:
            if d[a] is not None and (d[b] is None or d[b]>d[a]+F(c)):
                raise ValueError('Negative cycle')
        if any(v is None for v in d):raise ValueError('Unbounded contrast')
        rows.append(d)
    return rows

def potentials(d,anchor=0):
    return [[v-row[anchor] for v in row] for row in d]

def regrets(d,charges):
    """Sharp worst-case regrets over exactly the retained difference system."""
    n=len(d)-1
    if len(charges)!=n:raise ValueError('Wrong charge vector')
    w=list(map(F,charges))
    return [max(d[j+1][i+1]+w[i]-w[j] for j in range(n)) for i in range(n)]

def edges_from_summary(s):
    names=s['policies'];index={name:i+1 for i,name in enumerate(names)}
    edges=[];ledger=[]
    for estimator in s['estimator_names']:
        block=s['inference'][estimator]
        for name,j in index.items():
            l,u=map(F,block['costs'][name]['interval_exact'])
            if l>u:raise ValueError('Reversed marginal')
            edges.extend([(0,j,u),(j,0,-l)])
            ledger.append(dict(estimator=estimator,estimand=name,lower=str(l),upper=str(u)))
        for name,rec in block['contrasts'].items():
            first,second=name.split('-minus-');i,j=index[first],index[second]
            l,u=map(F,rec['interval_exact'])
            if l>u:raise ValueError('Reversed contrast')
            edges.extend([(j,i,u),(i,j,-l)])
            ledger.append(dict(estimator=estimator,estimand=name,lower=str(l),upper=str(u)))
    return names,edges,ledger

def decimal(x,lower,places=7):
    x=F(x);y=Decimal(x.numerator)/Decimal(x.denominator)
    return format(y.quantize(Decimal(10)**(-places),rounding=ROUND_FLOOR if lower else ROUND_CEILING),'f')

def save(p,j):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')

def table(name,caption,header,rows,note):
    text='\\begin{table}[htbp]\n\\centering\n\\caption{'+caption+'}\\label{tab:'+name+'}\n{\\small\\setlength{\\tabcolsep}{4pt}\n\\begin{tabular}{lrr}\n\\hline\n'
    text+=' & '.join(header)+r' \\'+'\n\\hline\n'
    text+='\n'.join(' & '.join(row)+r' \\' for row in rows)
    text+='\n\\hline\n\\end{tabular}}\n\\par\\smallskip\n{\\footnotesize '+note+'}\n\\end{table}\n'
    p=R/'tables'/(name+'.tex');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)

def main(source=None):
    start=time.perf_counter();p=Path(source) if source else R/'results77/summary.json'
    if sha(p)!=SOURCE_SHA:raise AssertionError('Pinned R77 original cost summary changed')
    s=json.loads(p.read_text());names,edges,ledger=edges_from_summary(s);n=len(names)+1
    d=closure(n,edges)
    if d!=independent_closure(n,edges):raise AssertionError('Independent graph algorithms disagree')
    witnesses=potentials(d)
    for source,theta in enumerate(witnesses):
        if theta[0]!=0 or any(theta[b]-theta[a]>c for a,b,c in edges):raise AssertionError('Invalid attaining cost witness')
        if any(theta[i]-theta[source]!=d[source][i] for i in range(n)):raise AssertionError('Sharpness failure')
    zero=regrets(d,[0]*len(names));best=[names[i] for i,v in enumerate(zero) if v==0]
    orders=[order for order in itertools.permutations(range(1,n)) if all(d[b][a]<0 for a,b in zip(order,order[1:]))]
    if len(orders)!=1:raise AssertionError('No unique strict cost ordering in this fixed catalogue')
    order=orders[0];rank=[names[i-1] for i in order]
    a,b=names.index('relu-n16')+1,names.index('relu-n8')+1
    low=-d[b][a];high=d[a][b];switch=(low+high)/2
    if not 0<low<=high:raise AssertionError('Refinement gain not strictly identified')
    if any(d[j][b]>=0 for j in range(1,n) if j not in (a,b)):raise AssertionError('Two-policy fee reduction invalid')
    probes=sorted(set([F(0),low/2,low,switch,high,high*2]))
    fee_replay=[]
    for fee in probes:
        charges=[F(0)]*(n-1);charges[a-1]=fee;rr=regrets(d,charges)
        if rr[a-1]!=max(F(0),fee-low) or rr[b-1]!=max(F(0),high-fee):raise AssertionError('Fee regret formula')
        fee_replay.append(dict(fee=str(fee),regrets={k:str(v) for k,v in zip(names,rr)},minimizers=[k for k,v in zip(names,rr) if v==min(rr)]))
    contrasts=[]
    for i,j in itertools.combinations(range(1,n),2):
        contrasts.append(dict(first=names[i-1],second=names[j-1],lower=str(-d[i][j]),upper=str(d[j][i])))
    matched=[]
    for size in (8,16):
        i=names.index(f'relu-n{size}')+1;j=names.index(f'bernstein-n{size}')+1
        matched.append(dict(n=size,gain_lower=str(-d[j][i]),gain_upper=str(d[i][j])))
    original_pair_upper={}
    for i,j in itertools.permutations(range(1,n),2):
        original_pair_upper[(i,j)]=min(c for a0,b0,c in edges if a0==j and b0==i)
    transitive=sum(d[j][i]<original_pair_upper[(i,j)] for i,j in original_pair_upper)
    result=dict(status='passed',source_summary_sha256=sha(p),policies=names,estimands=s['estimands'],
        source_rows=s['rows'],new_simulation_rows=0,source_coverage=s['family_failure_upper'],
        edges=[[a0,b0,str(c)] for a0,b0,c in edges],endpoint_ledger=ledger,
        distance_matrix=[[str(x) for x in row] for row in d],attaining_potentials=[[str(x) for x in row] for row in witnesses],
        checked_attaining_potentials=n,independent_algorithms_agree=True,strict_cost_order=rank,
        zero_charge_regrets={k:str(v) for k,v in zip(names,zero)},zero_charge_winners=best,
        contrasts=contrasts,matched_gains=matched,strict_transitive_pair_improvements=transitive,
        refinement_fee=dict(lower=str(low),upper=str(high),minimax_switch=str(switch),probes=fee_replay),
        scope='Exact deterministic postprocessing of the jointly covered R77 finite family. Sharp only relative to these retained linear inequalities; no new evidence, neural generalization, or stochastic timing claim.',
        seconds=time.perf_counter()-start)
    save(R/'audit/DECISION78.json',result)
    labels={'zero':'Installed zero','relu-n8':'ReLU, $n=8$','relu-n16':'ReLU, $n=16$','bernstein-n8':'Bernstein, $n=8$','bernstein-n16':'Bernstein, $n=16$'}
    pairs=[(j,i) for i,j in zip(order,order[1:])]
    rows=[[labels[names[j-1]]+' minus '+labels[names[i-1]],decimal(-d[j][i],True),decimal(d[i][j],False)] for j,i in pairs]
    table('ordering78','Adjacent gaps in the constructed-policy cost ordering',['Higher minus lower cost','Lower','Upper'],rows,
        'All endpoints are rounded outward. Both original estimators and all marginal and paired intervals enter one consistent difference system. These are the same frozen actors and the same 524,288 rows, not a new experiment. Charges are set to zero only for this statistical cost ordering.')
    rows=[[f'ReLU versus Bernstein, $n={x["n"]}$',decimal(x['gain_lower'],True),decimal(x['gain_upper'],False)] for x in matched]
    rows.append(['Refinement from ReLU $n=8$ to $n=16$',decimal(low,True),decimal(high,False)])
    table('fees78','Per-deployment gains available to pay incremental charges',['Replacement','Lower','Upper'],rows,
        'A positive lower gain licenses any smaller incremental total charge in normalized cost units. For $m$ deployments and monetary scale $v$, multiply the endpoints by $mv$. Construction, acquisition, qualification and installation charges remain explicit; seconds are not assigned an unobserved monetary price.')
    print(json.dumps({k:result[k] for k in ('status','strict_cost_order','zero_charge_winners','matched_gains','strict_transitive_pair_improvements','refinement_fee','seconds')},indent=2))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--source');main(parser.parse_args().source)
