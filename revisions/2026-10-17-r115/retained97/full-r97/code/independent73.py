"""Independent R73 checks: original terminal primitive, segmented/Boole integrals,
continuous-action lower covers, whole-cell actor gaps, and rational LP duals.
Does not rerun or retime the fitting services.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib,itertools,json,math,sys,time
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R.parent/'2026-10-10-r62/code'))
import operators50 as original
B=F(15,16)

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inner(a,b):return sum((F(x)*F(y) for x,y in zip(a,b)),F(0))
def basis(x,kind):
    answer=[F(1)]
    for z in x:
        if kind=='relu':answer.extend([z]+[max(F(0),z-F(k,4)) for k in (1,2,3)])
        else:
            levels=[F(1)]
            for _ in range(4):levels=[(1-z)*levels[0]]+[z*levels[j-1]+(1-z)*levels[j] for j in range(1,len(levels))]+[z*levels[-1]]
            answer.extend(levels[1:])
    return tuple(answer)

def point(x,a,future,kind):
    if future is None:return original.exact_q(x,a,1)
    y=[F(1,16)+x[j]/2+x[1-j]/8+x[j]*(1-x[1-j])/16+F(2-j,4)*a for j in (0,1)]
    def h(z):return inner(basis((y[0]+z,y[1]-z),kind),future)
    rad=F(1,32)
    if kind=='bernstein':mean=sum(F(w,90)*h(rad*k/2) for w,k in zip((7,32,12,32,7),(-2,-1,0,1,2)))
    else:
        cuts={-rad,rad}
        for j in (0,1):
            for k in (1,2,3):
                root=(F(k,4)-y[j])*(1 if j==0 else -1)
                if -rad<root<rad:cuts.add(root)
        cuts=sorted(cuts)
        mean=sum(((b-a)*(h(a)+h(b))/2 for a,b in zip(cuts,cuts[1:])),F(0))/(2*rad)
    state_cost=sum((z-F(5,8))**2 for z in x)+(x[0]-x[1])**2/4+2*max(F(0),F(1,2)-sum(x))**2+a*a+4*a**4
    return state_cost+B*mean

def main():
    start=time.perf_counter();files=[];total_queries=nodes=dual_checks=0;summary=[]
    for n,kind in itertools.product((8,16),('relu','bernstein')):
        folder=R/'results73'/f'{kind}-n{n}';file=folder/'service.json';obj=read(file);clock=read(folder/'clock.json')
        assert sha(file)==clock['service_sha256']
        assert obj['n']==n and obj['basis']==kind and obj['dimension']==obj['horizon']==2
        assert len(obj['stages'])==2
        stage_objects=[]
        for t,stage in enumerate(obj['stages']):
            assert stage['date']==t
            data=stage['data'];P=stage['problem'];theta=tuple(map(F,stage['attained']['theta']))
            future=None if t==1 else tuple(map(F,obj['stages'][1]['attained']['theta']))
            assert (None if stage['future'] is None else tuple(map(F,stage['future'])))==future
            Lk=(F(0),)+(F(1 if kind=='relu' else 4),)*8;rho=F(1,n)
            Lfuture=F(5) if future is None else inner(Lk,[abs(x) for x in future])
            Lx=4+B*F(11,16)*Lfuture;La=F(13,16)+B*F(3,4)*Lfuture;C=Lx+La/16
            assert F(data['rho'])==rho and F(data['Lx'])==Lx and F(data['La'])==La and F(data['C'])==C
            assert tuple(map(F,P['lipschitz']))==Lk and all(F(v)==8 for v in P['bounds'])
            assert F(P['radius'])==rho and F(P['bellman_lipschitz'])==C
            lows=[];highs=[];matrix=[];gaps=[];zero=[]
            for index,(i,j) in enumerate(itertools.product(range(n),repeat=2)):
                x=(F(2*i+1,2*n),F(2*j+1,2*n));cap=F(1,8)+sum(x)/16
                assert tuple(map(F,data['nodes'][index]))==x
                row=basis(x,kind);assert tuple(map(F,P['features'][index]))==row
                values=[point(x,cap*k/32,future,kind) for k in range(33)]
                lo=min(values)-La*cap/64;up=min(values)
                assert lo==F(data['lower'][index])==F(P['lower'][index]);assert up==F(data['upper'][index])==F(P['upper'][index])
                caplow=F(1,8)+F(i+j,16*n);capidx=math.floor(caplow*4096)
                actions=[F((capidx*k)//32,4096) for k in range(33)]
                imp=[point(x,a,future,kind) for a in actions]
                k=min(range(33),key=lambda k:(imp[k],actions[k]));assert F(data['actions'][index])==actions[k]<=caplow
                gaps.append(imp[k]-lo);zero.append(values[0]-lo)
                lows.append(lo);highs.append(up);matrix.append(row);total_queries+=66;nodes+=1
            assert F(data['eta_policy'])==max(gaps)+(Lx+C)*rho
            assert F(data['eta_zero'])==max(zero)+(Lx+C)*rho
            p=tuple(map(F,stage['attained']['p']));q=tuple(map(F,stage['attained']['q']))
            assert len(p)==len(q)==n*n and min(p+q)>=0 and sum(p)==sum(q)==1
            def objective(coefs):
                assert len(coefs)==9 and all(abs(v)<=8 for v in coefs)
                reslo=min(v-inner(row,coefs) for v,row in zip(lows,matrix));reshi=max(v-inner(row,coefs) for v,row in zip(highs,matrix))
                pad=rho*(C+inner(Lk,[abs(v) for v in coefs]))
                return reslo-pad,reshi+pad,reshi-reslo+2*pad
            lo,up,W=objective(theta)
            slopes=[sum(row[k]*(qj-pj) for row,pj,qj in zip(matrix,p,q)) for k in range(9)]
            dual=inner(p,highs)-inner(q,lows)+2*rho*C-sum(8*max(F(0),abs(g)-2*rho*L) for g,L in zip(slopes,Lk))
            assert F(stage['attained']['objective'])==W and F(stage['attained']['dual_lower'])==dual
            assert F(stage['attained']['residual_lower'])==lo and F(stage['attained']['residual_upper'])==up
            assert F(stage['attained']['optimization_gap'])==W-dual>=0
            assert W-dual<=F(1,65536)
            ls=stage['label_loss_ablation'];_,_,Wls=objective(tuple(map(F,ls['theta'])))
            assert F(ls['objective'])==Wls
            assert W<=Wls+(W-dual)
            dual_checks+=1
            stage_objects.append(dict(date=t,qualified_range=str(W),label_loss_range=str(Wls),dual_gap=str(W-dual),eta_policy=data['eta_policy']))
        omega=sum(B**s['date']*F(s['attained']['objective']) for s in obj['stages'])
        H=sum(B**s['date']*F(s['data']['eta_policy']) for s in obj['stages'])
        Hz=sum(B**s['date']*F(s['data']['eta_zero']) for s in obj['stages'])
        assert F(obj['omega'])==omega and F(obj['original_optimum_regret_upper'])==omega+H
        assert tuple(map(F,obj['centered_cost_support']))==(-omega-Hz,omega+H)
        assert obj['exact_action_evaluations']==132*n*n and obj['recursive_optimal_value_queries']==0
        summary.append(dict(n=n,basis=kind,stages=stage_objects,omega=str(omega),regret_upper=str(omega+H),service_seconds=clock['seconds_through_service_output']))
        files.append(dict(path=str(file.relative_to(R)),sha256=sha(file)))
    result=dict(status='passed',complete_services=4,checked_state_date_nodes=nodes,
                independent_action_evaluations=total_queries,exact_primal_dual_checks=dual_checks,
                new_independent_policy_cost_rows=0,scientific_service_retiming=False,
                scope='all new terminal values checked against retained original exact primitive; all fitted continuation action values checked by segmented or exact Boole integration; original continuous action and whole-cell bounds recomputed',
                files=files,summary=summary,replay_seconds=time.perf_counter()-start)
    (R/'audit').mkdir(exist_ok=True);(R/'audit/INDEPENDENT73.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','complete_services','checked_state_date_nodes','independent_action_evaluations','exact_primal_dual_checks','replay_seconds')},indent=2))
if __name__=='__main__':main()
