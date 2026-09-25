"""Independent witness reader; standard library only, no constructor imports."""
from fractions import Fraction as Q
from pathlib import Path
import gzip,hashlib,json,sys,time,copy
ROOT=Path(__file__).resolve().parents[3]
B=ROOT/'revisions/2026-09-25-r44'; P=ROOT/'revisions/2026-09-25-r46'; R=ROOT/'revisions/2026-09-26-r47'
Z=Q(0);sys.set_int_max_str_digits(0)
def need(test,msg):
    if not test: raise ValueError(msg)
def dot(a,b):
    need(len(a)==len(b),'inner product dimension')
    return sum((x*y for x,y in zip(a,b)),Z)
def verify_object(o):
    need(o['schema']=='nbo-r47-witness-v1','schema');name=o['case']
    need(name in [f'{f}{i}' for f in ['maintenance','inventory','queue','tie'] for i in range(4)],'case')
    mb=(B/'models'/f'{name}.json').read_bytes();pb=(B/'PROTOCOL.json').read_bytes()
    prior=(P/'proofs'/name/'restart.json.gz').read_bytes();src=json.loads(gzip.decompress(prior))
    d=json.loads(mb);protocol=json.loads(pb);h=hashlib.sha256(mb).hexdigest()
    need(o['model']==d==src['model'],'primitive identity')
    need(o['model_sha256']==h==protocol['models_sha256'][name],'registered model hash')
    need(o['protocol_sha256']==hashlib.sha256(pb).hexdigest(),'protocol hash')
    need(o['source_price_sha256']==hashlib.sha256(prior).hexdigest(),'source hash')
    need(Q(o['target'])==Q(protocol['target'])==Q(1,1000),'target')
    n,T,m=d['n'],d['T'],d['m'];b,e=Q(d['beta']),Q(d['epsilon'])
    need(n>0 and T>0 and m>0 and 0<b<1 and e>0,'dimensions/discount')
    K=[[[Q(v) for v in row] for row in state] for state in d['P']]
    r=[[Q(v) for v in row] for row in d['r']];k=[[Q(v) for v in row] for row in d['k']]
    g=list(map(Q,d['terminal']));nu=list(map(Q,d['nu']))
    need(len(nu)==n and min(nu)>=0 and sum(nu)==1,'initial law')
    need(len(K)==n and all(len(state)==m for state in K),'kernel dimensions')
    need(all(len(row)==n and min(row)>=0 and sum(row)==1 for state in K for row in state),'kernel')
    need(all(len(row)==m and min(row)>=0 for row in k),'cost')
    lo=[list(map(Q,row)) for row in o['operating_lower']];hi=[list(map(Q,row)) for row in o['operating_upper']]
    need(len(lo)==len(hi)==T+1 and all(len(row)==n for row in lo+hi),'witness dimensions')
    need(all(lo[t][i]<=hi[t][i] for t in range(T+1) for i in range(n)),'witness ordering')
    need(all(lo[T][i]<=g[i]<=hi[T][i] for i in range(n)),'terminal enclosure')
    for t in reversed(range(T)):
        for i in range(n):
            need(lo[t][i]<=max(r[i][a]+b*dot(K[i][a],lo[t+1]) for a in range(m)),'operating subsolution')
            need(hi[t][i]>=max(r[i][a]+b*dot(K[i][a],hi[t+1]) for a in range(m)),'operating supersolution')
    wb=o['witness_bits']; ppb=o['policy_bits']
    need(isinstance(wb,int) and 1<=wb<=256 and isinstance(ppb,int) and 1<=ppb<=256,'witness/policy precision')
    need(all((v*2**wb).denominator==1 for row in lo+hi for v in row),'witness grid')
    widths=[max(hi[t][i]-lo[t][i] for i in range(n)) for t in range(T+1)]
    xi=max(widths[:-1]);s=(1-b)*e
    need(Q(o['witness_width'])==xi and o['uniform_guard_passed']==(xi<s),'witness guard')
    lam=[list(map(Q,row)) for row in src['prices']]+[[Z]*n]
    need(len(lam)==T+1 and all(len(row)==n and min(row)>=0 for row in lam),'nonnegative prices')
    u=[list(map(Q,row)) for row in o['lower_table']]
    need(len(u)==T+1 and all(len(row)==n for row in u) and u[T]==[Z]*n,'cost table')
    bits=o['lower_bits'];need(isinstance(bits,int) and 1<=bits<=256,'precision');scale=2**bits
    for t in reversed(range(T)):
        for i in range(n):
            # Unshifted W=C+lambda D, rather than the constructor's shifted table.
            wn=[u[t+1][j]+e*lam[t+1][j] for j in range(n)];outcomes=[]
            for a in range(m):
                dl=max(Z,lo[t][i]-r[i][a]-b*dot(K[i][a],hi[t+1]))
                change=[wn[j]-e*max(Z,lam[t+1][j]-lam[t][i]) for j in range(n)]
                outcomes.append(k[i][a]+lam[t][i]*dl+b*dot(K[i][a],change))
            v=min(outcomes)-e*lam[t][i]
            need(u[t][i]==Q(v.numerator*scale//v.denominator,scale),'transformed Bellman row')
    lower=dot(nu,[max(Z,v) for v in u[0]])
    need(Q(o['lower'])==lower,'lower endpoint')
    lb=sum((b**t*(max(lam[t])*(widths[t]+b*widths[t+1])+Q(1,scale)) for t in range(T)),Z)
    need(Q(o['lower_error_budget'])==lb,'lower error budget')
    need(Z<=Q(src['lower'])-lower<=lb,'lower perturbation')
    upper=None;checks=0
    if o['policy'] is None:
        need(o['upper'] is None and o['failure'] is not None and not o['uniform_guard_passed'],'missing upper disclosure')
    else:
        policy=o['policy'];need(len(policy)==T and all(len(period)==n for period in policy),'policy dimensions')
        J=g[:];C=[Z]*n
        for t in reversed(range(T)):
            nj=[];nc=[]
            for i in range(n):
                p=list(map(Q,policy[t][i]));need(len(p)==m and min(p)>=0 and sum(p)==1,'policy simplex')
                need(all((v*2**ppb).denominator==1 for v in p),'deployment grid')
                j=dot(p,[r[i][a]+b*dot(K[i][a],J) for a in range(m)])
                c=dot(p,[k[i][a]+b*dot(K[i][a],C) for a in range(m)])
                need(hi[t][i]-j<=e,'witness-certified all-restart inequality')
                nj.append(j);nc.append(c);checks+=1
            J,C=nj,nc
        upper=dot(nu,C);need(Q(o['upper'])==upper and lower<=upper,'upper endpoint')
    if xi<s:
        dc=max(v for row in k for v in row)*sum((b**t*sum((b**j for j in range(T-t)),Z) for t in range(T)),Z)
        ub=dc*min(Q(1),xi/s+Q(m-1,2**o['policy_bits']))
        need(Q(o['upper_error_budget'])==ub,'upper error budget')
        if upper is not None:need(upper-Q(src['upper'])<=ub,'upper perturbation')
    else:need(o['upper_error_budget'] is None,'unsupported error bound')
    return dict(passed=True,case=name,bits=o['witness_bits'],lower=str(lower),upper=str(upper) if upper is not None else None,
                gap=float(upper-lower) if upper is not None else None,target_met=upper is not None and upper-lower<=Q(1,1000),
                operating_inequalities=2*T*n,lower_action_checks=T*n*m,all_restart_checks=checks,guard_passed=xi<s)
def verify(path):
    start=time.perf_counter();data=Path(path).read_bytes();result=verify_object(json.loads(gzip.decompress(data)))
    result.update(proof_sha256=hashlib.sha256(data).hexdigest(),seconds=time.perf_counter()-start);return result
if __name__=='__main__':
    files=[Path(p) for p in sys.argv[1:]] or sorted((R/'proofs').glob('*_b*.json.gz'))
    rows=[verify(p) for p in files];result=dict(passed=all(x['passed'] for x in rows),objects=len(rows),results=rows)
    (R/'results/independent_witness.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'objects':len(rows),'seconds':sum(x['seconds'] for x in rows)}))
