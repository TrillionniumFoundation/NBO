"""A second-library, optimizer-free check of every fixed-restart frontier node."""
import itertools,time,json
from pathlib import Path
from sympy import Rational as Q
from verify_primary import ROOT,read,rat,parse,value,PROBS,BETA,COST,TRANS,sha

def verify(d,primary):
    T=d['T'];eps=rat(d['epsilon']);V=list(map(parse,primary['V']));raw=list(map(parse,primary['raw']))
    assert T==4 and d['policy_class']=='randomized_history_conditioned' and d['whole_state_uniform_objective'] is False
    index={};checks=0
    for node in sorted(d['nodes'],key=lambda n:-n['t']):
        t=node['t'];x=rat(node['x']);assert 0<=x<=1
        floor=value(V[t],x)-eps;assert floor==rat(node['operating_floor'])
        candidates=[]
        for a in range(3):
            child=[]
            for m,b in TRANS[a]:
                y=m*x+b;child.append([(y/2,Q(0))] if t+1==T else index[(t+1,y)])
            for u,v in itertools.product(*child):
                j=x-COST[a]+BETA*(PROBS[0]*u[0]+PROBS[1]*v[0])
                c=(1+x if a!=value(raw[t],x) else 0)+BETA*(PROBS[0]*u[1]+PROBS[1]*v[1]);candidates.append((j,c))
        assert len(candidates)==node['candidate_count'] and sha([[str(j),str(c)] for j,c in candidates])==node['candidate_sha256']
        fr=[tuple(map(rat,p)) for p in node['frontier']];assert fr and len(fr)==len(node['primal_dual'])
        assert all(j>=floor and c>=0 for j,c in fr) and fr[-1][0]==value(V[t],x)==max(j for j,c in candidates)
        assert all(a[0]<b[0] and a[1]<b[1] for a,b in zip(fr,fr[1:]))
        for n,((j,c),cert) in enumerate(zip(fr,node['primal_dual'])):
            mu=rat(cert['mu']);eta=rat(cert['intercept']);assert mu>=0
            if n:assert mu==(c-fr[n-1][1])/(j-fr[n-1][0])
            elif j>floor:assert mu==0
            assert c==mu*j+eta
            for jj,cc in candidates:assert cc>=mu*jj+eta;checks+=1
            p=cert['primal'];a=tuple(map(rat,p['left']));b=tuple(map(rat,p['right']));w=rat(p['left_weight'])
            assert a in candidates and b in candidates and 0<=w<=1
            assert (w*a[0]+(1-w)*b[0],w*a[1]+(1-w)*b[1])==(j,c)
        index[(t,x)]=fr
    root=index[(0,rat(d['initial_state']))];assert [[str(j),str(c)] for j,c in root]==d['frontier'] and str(root[0][1])==d['value']
    return {'nodes':len(index),'support_inequalities':checks,'passed':True}
def run():
    tic=time.perf_counter();rows=[]
    for p in sorted((ROOT/'results/frontiers').glob('*.json.gz')):
        d=read(p);ep=d['epsilon'].replace('/','_');source=next((ROOT/'results/primary').glob(f"H4_{d['proposal']}_epsilon{ep}_*"));primary=read(source)
        result=verify(d,primary);result.update({'proof_file':p.name,'proof_sha256':sha(d)});rows.append(result)
    assert len(rows)==70
    (ROOT/'results/frontier_independent_verification.json').write_text(json.dumps({'passed':True,'objects':70,'records':rows,'seconds':time.perf_counter()-tic,'scope':'All serialized fixed-restart frontier nodes; not the primary uniform-initial randomized Markov optimum.'},indent=2))
    print('Independent frontier verification passed:',len(rows),flush=True)
if __name__=='__main__':run()
