"""Independent SymPy verification of common-policy rational search trees.
No constructor, optimizer, Fraction kernel, LP solver, or repair code is imported.
The independent LP equations are assembled directly from economic primitives.
"""
from pathlib import Path
import json,gzip,time,re,copy,hashlib,random
from sympy import Rational as Q
ROOT=Path(__file__).resolve().parents[1];Z=Q(0);O=Q(1)
PAT=re.compile(r'^-?[0-9]+(?:/[1-9][0-9]*)?$')
def convert(x):
    if isinstance(x,str) and PAT.fullmatch(x):return Q(x)
    if isinstance(x,list):return [convert(v) for v in x]
    if isinstance(x,dict):return {k:convert(v) for k,v in x.items()}
    return x

def dot(a,b):return sum((x*y for x,y in zip(a,b)),Z)
def evaluate(m,p):
    n,T,b=m['n'],m['T'],m['beta'];J=[None]*T+[m['g']];C=[None]*T+[[Z]*n]
    for t in range(T-1,-1,-1):
        J[t]=[];C[t]=[]
        for i in range(n):
            prob=[1-p[t*n+i],p[t*n+i]]
            J[t].append(sum(prob[a]*(m['r'][a][i]+b*dot(m['P'][a][i],J[t+1])) for a in (0,1)))
            C[t].append(sum(prob[a]*(m['k'][a][i]+b*dot(m['P'][a][i],C[t+1])) for a in (0,1)))
    return J,C

def interval(m,V,box):
    n,T,b,e=m['n'],m['T'],m['beta'],m['epsilon'];caps=copy.deepcopy(box)
    jl=ju=m['g'];cl=cu=[Z]*n
    for t in range(T-1,-1,-1):
        Jl=[];Ju=[];Cl=[];Cu=[]
        for i in range(n):
            l,u=caps[t*n+i]
            ql=[m['r'][a][i]+b*dot(m['P'][a][i],jl) for a in (0,1)]
            qh=[m['r'][a][i]+b*dot(m['P'][a][i],ju) for a in (0,1)]
            target=V[t][i]-e;delta=qh[1]-qh[0]
            if delta>0:l=max(l,(target-qh[0])/delta)
            elif delta<0:u=min(u,(target-qh[0])/delta)
            elif qh[0]<target:return None
            if l>u:return None
            caps[t*n+i]=[l,u]
            vl=max(target,min((1-x)*ql[0]+x*ql[1] for x in (l,u)))
            vu=min(V[t][i],max((1-x)*qh[0]+x*qh[1] for x in (l,u)))
            if vl>vu:return None
            Jl.append(vl);Ju.append(vu)
            zl=[m['k'][a][i]+b*dot(m['P'][a][i],cl) for a in (0,1)]
            zu=[m['k'][a][i]+b*dot(m['P'][a][i],cu) for a in (0,1)]
            Cl.append(min((1-x)*zl[0]+x*zl[1] for x in (l,u)))
            Cu.append(max((1-x)*zu[0]+x*zu[1] for x in (l,u)))
        jl,ju,cl,cu=Jl,Ju,Cl,Cu
    return dot(m['nu'],cl),caps

def lp_certificate(m,V,caps,multipliers):
    n,T,b=m['n'],m['T'],m['beta'];d=n*T;K=max(v for a in m['k'] for v in a)
    bounds=caps+[[V[t][i]-m['epsilon'],V[t][i]] for t in range(T) for i in range(n)]
    bounds+=[[Z,K*sum(b**j for j in range(T-t))] for t in range(T) for i in range(n)]
    residual=[Z]*(3*d)
    for i,v in enumerate(m['nu']):residual[2*d+i]=v
    constant=Z;counter=0
    for t in range(T):
        for i in range(n):
            l,u=caps[t*n+i]
            for cost,offset in ((False,d),(True,2*d)):
                pay=m['k'] if cost else m['r'];r0=pay[0][i];dr=pay[1][i]-pay[0][i]
                diff=[b*(m['P'][1][i][j]-m['P'][0][i][j]) for j in range(n)]
                if t==T-1:
                    if not cost:r0+=b*dot(m['P'][0][i],m['g']);dr+=dot(diff,m['g'])
                    yl=yu=dr
                else:
                    yl=dr+sum(min(diff[j]*bounds[offset+(t+1)*n+j][h] for h in (0,1)) for j in range(n))
                    yu=dr+sum(max(diff[j]*bounds[offset+(t+1)*n+j][h] for h in (0,1)) for j in range(n))
                for pval,yval,sign in ((l,yl,-1),(u,yu,-1),(u,yl,1),(l,yu,1)):
                    lam=multipliers[counter];counter+=1;assert lam>=0
                    rhs=sign*(r0+pval*dr-pval*yval)
                    constant-=lam*rhs
                    residual[offset+t*n+i]+=lam*sign
                    residual[t*n+i]-=lam*sign*yval
                    if t<T-1:
                        for j in range(n):residual[offset+(t+1)*n+j]-=lam*sign*(b*m['P'][0][i][j]+pval*diff[j])
    assert counter==len(multipliers)
    return constant+sum(min(a*l,a*u) for a,(l,u) in zip(residual,bounds))

def verify(raw):
    tic=time.perf_counter();d=convert(raw);m=d['model'];n,T,b=m['n'],m['T'],m['beta']
    assert n in (2,4) and T>0 and 0<b<1 and m['epsilon']>0
    assert len(m['g'])==n and len(m['nu'])==n and min(m['nu'])>=0 and sum(m['nu'])==1
    for a in (0,1):
        assert len(m['P'][a])==n and len(m['r'][a])==n and len(m['k'][a])==n
        for i in range(n):assert len(m['P'][a][i])==n and min(m['P'][a][i])>=0 and sum(m['P'][a][i])==1
    for i in range(n):
        assert m['r'][0][i]==2*m['g'][i] and m['r'][1][i]==m['r'][0][i]-m['operation_price']
        assert m['k'][0][i]==0 and m['k'][1][i]==1+m['r'][0][i] and m['raw'][i]==0
    V=[None]*T+[m['g']]
    for t in range(T-1,-1,-1):V[t]=[max(m['r'][a][i]+b*dot(m['P'][a][i],V[t+1]) for a in (0,1)) for i in range(n)]
    assert V==d['V']
    p=d['policy'];assert len(p)==n*T and all(0<=x<=1 for x in p)
    J,C=evaluate(m,p);assert J==d['J'] and C==d['C']
    assert all(J[t][i]>=V[t][i]-m['epsilon'] for t in range(T) for i in range(n))
    upper=dot(m['nu'],C[0]);assert upper==d['upper']
    assert d['policy_class']=='randomized_Markov_common_continuation' and d['constraint']=='every_time_every_state'
    assert d['objective']=='specified_initial_distribution_discounted_revision_cost'
    nodes=d['nodes'];assert len(nodes)==d['evaluations'] and nodes[0]['box']==[[Z,O] for _ in range(n*T)]
    seen=set();stack=[0];leaves=[];lpc=0
    while stack:
        i=stack.pop();assert i not in seen;seen.add(i);node=nodes[i];box=node['box'];assert len(box)==n*T
        assert all(0<=l<=u<=1 for l,u in box)
        res=interval(m,V,box)
        if res is None:assert node['kind']=='infeasible';continue
        ilb,caps=res;assert caps==node['caps'];lb=ilb
        if 'lp' in node:
            assert ilb==node['interval_lower'];cert=node['lp']
            if cert['status']==0:
                val=lp_certificate(m,V,caps,cert['multipliers']);assert val==cert['lower'];lb=max(lb,val);lpc+=1
        assert node['lower']==lb
        if node['kind']=='split':
            v=node['variable'];cut=node['cut'];left,right=node['children'];assert left>i and right>i and left!=right
            assert caps[v][0]<cut<caps[v][1]
            wanted_l=copy.deepcopy(caps);wanted_r=copy.deepcopy(caps);wanted_l[v][1]=cut;wanted_r[v][0]=cut
            assert nodes[left]['box']==wanted_l and nodes[right]['box']==wanted_r
            stack.extend((left,right))
        else:
            assert node['kind'] in ('open','pruned');leaves.append(lb)
            if node['kind']=='pruned':assert lb>=upper
    assert len(seen)==len(nodes)
    lower=min(leaves+[upper]);assert lower==d['lower'] and upper-lower==d['gap']
    assert d['closed']==(d['gap']<=d['tolerance'])
    return {'passed':True,'nodes':len(nodes),'lp_residual_certificates':lpc,'seconds':time.perf_counter()-tic}

def main():
    rows=[]
    for p in sorted((ROOT/'results/finite').glob('*.json.gz')):
        raw=json.loads(gzip.decompress(p.read_bytes()));v=verify(raw);v['file']=str(p.relative_to(ROOT));v['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();rows.append(v)
        print(p.name,v,flush=True)
    # Mutations are distinct from proof: each corruption below must be rejected.
    p=next((ROOT/'results/finite').glob('*_lp.json.gz'));base=json.loads(gzip.decompress(p.read_bytes()));mutations={
      'upper_cost':lambda d:d.__setitem__('upper','999'),
      'policy_probability':lambda d:d['policy'].__setitem__(0,'2'),
      'terminal_value':lambda d:d['V'][-1].__setitem__(0,'999'),
      'policy_class':lambda d:d.__setitem__('policy_class','history_conditioned'),
      'initial_distribution':lambda d:d['model']['nu'].__setitem__(0,'2'),
      'revision_contract':lambda d:d['model']['k'][1].__setitem__(0,'0'),
      'node_lower':lambda d:d['nodes'][0].__setitem__('lower','999'),
      'negative_dual':lambda d:d['nodes'][0]['lp']['multipliers'].__setitem__(0,'-1'),
      'root_coverage':lambda d:d['nodes'][0]['box'][0].__setitem__(0,'1/2')}
    rejected=[]
    for name,mutate in mutations.items():
        bad=copy.deepcopy(base);mutate(bad)
        try:verify(bad)
        except (AssertionError,ValueError,IndexError,KeyError,ZeroDivisionError):rejected.append(name)
        else:raise AssertionError('accepted corruption '+name)
    report={'independent_arithmetic':'SymPy Rational; no constructor/optimizer imports','outcomes':rows,'mutation_rejections':rejected}
    (ROOT/'results/verify_finite.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
if __name__=='__main__':main()
