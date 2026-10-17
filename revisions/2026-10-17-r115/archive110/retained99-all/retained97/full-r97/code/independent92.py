"""Independent primal-threshold/original-value checker. No centered92 import."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product,permutations
import hashlib,json,time
R=Path(__file__).resolve().parents[1]

def need(ok,msg):
    if not ok:raise AssertionError(msg)
def qvec(v):
    v=tuple(map(F,v));need(bool(v) and min(v)>=0 and sum(v)==1,'Risk probability');return v

def tail(p,v,a):
    p=qvec(p);v=tuple(map(F,v));a=F(a)
    need(len(p)==len(v) and 0<=a<1,'Threshold input')
    # A minimizer is a support threshold; atoms are never discarded.
    return min(z+sum(w*max(x-z,0) for w,x in zip(p,v))/(1-a) for z in set(v))

def original(m,policy=None,tree=False):
    T=int(m['T']);S=len(m['g']);A=len(m['c'][0][0]);alpha=F(m['alpha']);g=list(map(F,m['g']));beta=list(map(F,m['beta']))
    if tree:
        def visit(t,s):
            if t==T:return g[s]
            aa=range(A) if policy is None else (policy[t][s],)
            return min(F(m['c'][t][s][a])+beta[t]*tail(m['p'][t][s][a],[visit(t+1,z) for z in range(S)],alpha) for a in aa)
        return [visit(0,s) for s in range(S)]
    v=[None]*(T+1);v[T]=g
    for t in range(T-1,-1,-1):
        v[t]=[]
        for s in range(S):
            aa=range(A) if policy is None else (policy[t][s],)
            v[t].append(min(F(m['c'][t][s][a])+beta[t]*tail(m['p'][t][s][a],v[t+1],alpha) for a in aa))
    return v

def verify_record(rec):
    m=rec['model'];T=int(m['T']);S=len(m['g']);A=len(m['c'][0][0]);alpha=F(m['alpha']);b=list(map(F,m['beta']));f=[list(map(F,row)) for row in m['f']]
    pi=rec['policy'];op=original(m);vp=original(m,pi);r=rec['residuals'];ks=rec['kernels'];checks=0;exclusions=0
    for t in range(T):
        for s in range(S):
            row=[]
            for a in range(A):
                p=qvec(m['p'][t][s][a]);rho=tail(p,f[t+1],alpha);rr=F(m['c'][t][s][a])+b[t]*rho-f[t][s]
                need(rr==F(r[t][s][a]),'Original residual');row.append(rr)
                k=ks[t][s][a];need(len(k['q'])==len(k['k']) and len(k['q'])>0,'Risk-piece dimensions')
                need(F(k['reference'])==rho,'Original risk reference')
                complete=set()
                for order in permutations(range(S)):
                    qq=[F(0)]*S;remaining=F(1)
                    for z in order:
                        qq[z]=min(remaining,p[z]/(1-alpha));remaining-=qq[z]
                    need(remaining==0,'Independent risk-envelope filling')
                    complete.add(tuple(qq))
                need(complete=={tuple(map(F,qq)) for qq in k['q']},'Complete independent risk envelope')

                for qq,kk in zip(k['q'],k['k']):
                    q=qvec(qq);need(len(q)==S,'Risk-piece state count')
                    need(all(x<=w/(1-alpha) for x,w in zip(q,p)),'Risk density cap')
                    gap=rho-sum(q[z]*f[t+1][z] for z in range(S));need(F(kk)==gap and gap>=0,'Centered penalty')
                    checks+=1
                need(min(map(F,k['k']))==0,'Reference attaining risk piece')
            need(pi[t][s]==min(range(A),key=lambda a:row[a]),'Complete original-menu greedy policy')
    for rr in rec['bounds']:
        radius=F(rr['radius']);need(radius>=0,'Negative uncertainty')
        L=[list(map(F,row)) for row in rr['L']];U=[list(map(F,row)) for row in rr['U']]
        need(len(L)==T+1 and len(U)==T+1 and all(len(v)==S for v in L+U),'Potential shape')
        for s in range(S):
            e=radius*F(s+1,S);d=F(m['g'][s])-f[T][s]
            need(L[T][s]==d-e and U[T][s]==d+e,'Terminal bounds')
        for t in reversed(range(T)):
            for s in range(S):
                e=radius*F(s+1,S)
                low=[]
                for a in range(A):
                    p=m['p'][t][s][a]
                    low.append(F(m['c'][t][s][a])-f[t][s]-e+b[t]*tail(p,[f[t+1][z]+L[t+1][z] for z in range(S)],alpha))
                a=pi[t][s]
                upper=F(m['c'][t][s][a])-f[t][s]+e+b[t]*tail(m['p'][t][s][a],[f[t+1][z]+U[t+1][z] for z in range(S)],alpha)
                need(L[t][s]==min(low) and U[t][s]==upper,'Independent original-law potential recursion')
                need(L[t][s]<=op[t][s]-f[t][s]<=vp[t][s]-f[t][s]<=U[t][s],'Original-optimum sandwich')
                if radius==0:need(L[t][s]==op[t][s]-f[t][s] and U[t][s]==vp[t][s]-f[t][s],'Exact centered identity')
                checks+=2
        scalar_l=min(L[T]);scalar_u=max(U[T])
        for t in reversed(range(T)):
            scalar_l=min(F(r[t][s][a])-radius*F(s+1,S) for s in range(S) for a in range(A))+b[t]*scalar_l
            scalar_u=max(F(r[t][s][pi[t][s]])+radius*F(s+1,S) for s in range(S))+b[t]*scalar_u
        need(F(rr['scalar_bound'])==scalar_u-scalar_l,'Scalar bound')
        need(list(map(F,rr['initial_loss_bounds']))==[u-l for l,u in zip(L[0],U[0])],'Initial reported bounds')
        need(all(u-l<=scalar_u-scalar_l for l,u in zip(L[0],U[0])),'No regression against scalar certificate')
        keys=set();before=after=0
        for cut in rr['cuts']:
            t,s,a=cut['t'],cut['state'],cut['action'];key=(t,s,a)
            need(key not in keys and 0<=t<T and 0<=s<S and 0<=a<A,'Risk-node coverage');keys.add(key)
            k=ks[t][s][a];n=len(k['q']);kept=cut['kept'];removed=cut['removed'];ids=[x['piece'] for x in removed]
            need(bool(kept) and len(set(kept+ids))==n and sorted(kept+ids)==list(range(n)),'Complete risk partition')
            before+=n;after+=len(kept)
            for x in removed:
                j,j0=x['piece'],x['witness'];need(j0 in kept,'Retained exclusion witness')
                d=[F(v)-F(w) for v,w in zip(k['q'][j],k['q'][j0])]
                support=sum(d[z]*(U[t+1][z] if d[z]>0 else L[t+1][z]) for z in range(S))
                gap=F(k['k'][j])-F(k['k'][j0])
                need(support==F(x['support']) and gap==F(x['gap']) and support<gap,'Strict support exclusion')
                exclusions+=1
        need(len(keys)==T*S*A and before==rr['pieces_before'] and after==rr['pieces_after'],'Complete cut catalogue')
    fl=rec['flow'];mass=[list(map(F,row)) for row in fl['masses']];choices=fl['choices'];exact=rec['bounds'][0]
    need(F(exact['radius'])==0,'Exact flow reference');U=[list(map(F,row)) for row in exact['U']]
    need(len(mass)==T+1 and mass[0]==[F(1,S)]*S and len(choices)==T,'Initial risk flow')
    B=F(1);obj=F(0);dual_checks=0
    for t in range(T):
        need(len(mass[t])==S and min(mass[t])>=0 and sum(mass[t])==1,'Risk occupation probability')
        nxt=[F(0)]*S;need(len(choices[t])==S,'Flow choice dimensions')
        for s in range(S):
            a=pi[t][s];k=ks[t][s][a];j=choices[t][s];need(0<=j<len(k['q']),'Risk choice')
            q=list(map(F,k['q'][j]));gap=F(k['k'][j]);res=F(r[t][s][a])
            obj+=B*mass[t][s]*(res-b[t]*gap)
            for z in range(S):nxt[z]+=mass[t][s]*q[z]
            for qq,kk in zip(k['q'],k['k']):
                rhs=res+b[t]*(sum(F(qq[z])*U[t+1][z] for z in range(S))-F(kk))
                need(U[t][s]>=rhs,'Every fixed-policy risk dual inequality');dual_checks+=1
        need(nxt==mass[t+1],'Risk flow conservation');B*=b[t]
    obj+=B*sum(mass[T][s]*(F(m['g'][s])-f[T][s]) for s in range(S))
    val=sum((vp[0][s]-f[0][s])/S for s in range(S))
    need(obj==F(fl['objective'])==F(fl['dual'])==val,'Independent primal-dual original value')
    need(dual_checks==fl['inequalities'],'Dual inequality count')
    return {'inequalities':checks+dual_checks,'exclusions':exclusions}


def main():
    start=time.perf_counter();d=R/'results92';summary=json.loads((d/'SUMMARY92.json').read_text());entries=summary['cases']
    expected={(T,str(a),str(th)) for T in (2,3,4,8,16,32,64) for a in (F(0),F(1,2),F(3,4)) for th in (-1,0,1,2)}
    seen=set();inequalities=exclusions=0;short={}
    for item in entries:
        p=d/item['file'];need(hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],'Record hash')
        rec=json.loads(p.read_text());m=rec['model'];key=(m['T'],str(m['alpha']),str(m['theta']))
        need(key not in seen,'Duplicate configuration');seen.add(key)
        need([F(v['radius']) for v in rec['bounds']]==[F(0),F(1,64),F(1,8)],'All radii retained')
        stats=verify_record(rec);inequalities+=stats['inequalities'];exclusions+=stats['exclusions']
        if m['T'] in (2,3) and F(m['theta'])==0:short[(m['T'],m['alpha'])]=m
    need(seen==expected and summary['case_count']==len(expected),'Full frozen catalogue')
    need(summary['interval_configurations']==3*len(expected),'Full radius count')
    policies=tree_states=0
    for (T,alpha),m in short.items():
        S=len(m['g']);opt=original(m)[0];need(opt==original(m,tree=True),'Independent descendant optimal recursion')
        for flat in product(range(2),repeat=T*S):
            pi=[list(flat[t*S:(t+1)*S]) for t in range(T)];v=original(m,pi)[0];tv=original(m,pi,tree=True)
            need(v==tv and all(x>=y for x,y in zip(v,opt)),'All-policy tree and backward agreement')
            policies+=1;tree_states+=S
    out={'status':'passed','case_count':len(seen),'interval_configurations':3*len(seen),'exact_certificate_inequalities':inequalities,
      'strict_kernel_exclusions_checked':exclusions,'complete_policies_enumerated':policies,'initial_state_tree_equalities':tree_states,
      'independent_method':'Primal threshold AVaR; independently coded original-value recursion and un-memoized descendant recursion',
      'new_fit_attempts':0,'new_independent_economic_rows':0,'largest_inherited_vector_reimplementation':False,'seconds':time.perf_counter()-start,
      'summary_sha256':hashlib.sha256((d/'SUMMARY92.json').read_bytes()).hexdigest()}
    dest=R/'audit/reproduction92';dest.mkdir(parents=True,exist_ok=True);(dest/'INDEPENDENT92.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2),flush=True)
if __name__=='__main__':main()
