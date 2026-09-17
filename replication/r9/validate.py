"""Independent checks of the R9 stop extension and economically relevant outputs.

Enumerated toy policies and selected-control reconstruction do not share the
production Bellman maximization. Neither is an interval transition constructor.
"""
from contracts import *
from run import verify_inputs
from itertools import product

class Toy(Contract):
    def __init__(self,rng,fee):
        self.ns=2;self.steps=3;self.center=0;self.na=2;self.stop=2;self.fee=fee;self.min_term=1
        self.terminal=rng.normal(size=2)*.2
        z=rng.uniform(.01,1,(2,3,2,2,2));self.K=.93*z/z.sum(-1,keepdims=True)
        self.R=rng.normal(size=(2,3,2,2))*.25
        self.A=rng.uniform(.03,.3,(2,3,2,2))
    def allowed(self,n,adjust=True,sign=None):
        a=np.ones((2,3),bool)
        if n==0:
            a[:,2]=False
            if sign=='positive':a[:,0]=False
            if sign=='nonpositive':a[:,1]=False
        return a
    def q(self,k,n,v,d,fee=None):
        fee=self.fee if fee is None else fee
        return np.column_stack((self.R[k,n]+d*self.A[k,n]+self.K[k,n]@v,self.terminal-fee))
    def continuation(self,k,n,v):return np.column_stack((self.K[k,n]@v,np.zeros(2)))
    def selected(self,k,n,p,v,d,fee=None):return self.q(k,n,v,d,fee)[np.arange(2),p]

def enumerate_toy(c,lam,d,sign):
    ans=np.full(c.ns,-np.inf)
    for tail in product(range(3),repeat=4):
        p=np.empty((3,2),np.int32);p[0]=1 if sign=='positive' else 0;p[1:]=np.array(tail).reshape(2,2)
        v=c.terminal.copy()
        # Separate dense expectation / reward code, not Contract.evaluate.
        for n in (2,1,0):
            out=np.empty(2)
            for x in range(2):
                a=p[n,x]
                out[x]=c.terminal[x]-c.fee if a==2 else sum(pr*(c.R[k,n,x,a]+d*c.A[k,n,x,a]+c.K[k,n,x,a]@v) for k,pr in enumerate((1-lam,lam)))
            v=out
        ans=np.maximum(ans,v)
    return ans

def toy_tests():
    rng=np.random.default_rng(20260917);err=0.;upper_violation=0.;order=0.;poly=0.;cases=0
    for _ in range(12):
        c=Toy(rng,float(rng.uniform(0,.4)));d=.37;a=.05;b=.8
        za=c.pair(a,d);zb=c.pair(b,d)
        ch=upper_pair(c,a,b,d,za,zb,True,'chord');ct=upper_pair(c,a,b,d,za,zb,True,'count')
        for s in SIGNS:order=max(order,float((ct[s]-ch[s]).max()))
        for lam in (.05,.13,.425,.72,.8):
            z=c.pair(lam,d)
            for s in SIGNS:
                ex=enumerate_toy(c,lam,d,s);err=max(err,float(np.max(abs(z[s]['value'][0]-ex))))
                p=z[s]['policy'];co=c.coefficients(p,d);poly=max(poly,abs(r7.bernstein_value(co,lam)-ex[0]))
                for u in (ch[s],ct[s]):upper_violation=max(upper_violation,ex[0]-r7.bernstein_value(u,(lam-a)/(b-a)))
                cases+=1
    assert max(err,upper_violation,order,poly)<2e-12
    return dict(random_models=12,class_point_comparisons=cases,policies_per_class_per_point=81,exhaustive_error=err,upper_violation=upper_violation,count_above_chord=order,polynomial_error=poly)

def direct_stop(c,policy,lam,d):
    base=c.base;actions=base.e[0].controls(np.minimum(policy,c.na-1));states=base.e[0].states
    values=np.empty((c.steps+1,c.ns));values[-1]=c.terminal
    for n in range(c.steps-1,-1,-1):
        out=np.zeros(c.ns)
        for prob,e in zip((1-lam,lam),base.e):
            y,live,disc,flow,_,_,alpha=old.transition(states,actions[n],1/c.steps,e.model)
            ann=-np.expm1(-e.model.rho*alpha/c.steps)/e.model.rho
            out+=prob*np.mean(flow+d*ann+disc*np.where(live,old.interpolate(values[n+1].reshape(e.shape),y),old.terminal(y)),axis=-1)
        stopped=policy[n]==c.stop;out[stopped]=c.terminal[stopped]-c.fee;values[n]=out
    return values

def full_tests(base):
    err=0.;polyerr=0.;order=0.;violation=0.;feasible=0;convex_violation=0.
    for adj in (True,False):
        for fee in (0.,.7,.8,.85):
            c=Contract(base,fee,1);d=.425;za=c.pair(0.,d,adj);zb=c.pair(.25,d,adj)
            ch=upper_pair(c,0.,.25,d,za,zb,adj,'chord');ct=upper_pair(c,0.,.25,d,za,zb,adj,'count')
            for s in SIGNS:order=max(order,float(np.max(ct[s]-ch[s])))
            for lam in (0.,.0625,.125,.1875,.25):
                z=c.pair(lam,d,adj)
                for s in SIGNS:
                    v=z[s]['value'][0,c.center]
                    for co in (ch[s],ct[s]):violation=max(violation,float(v-r7.bernstein_value(co,lam/.25)))
                    feasible+=1
                    if lam==.125:
                        pp=z[s]['policy'];replay=direct_stop(c,pp,lam,d)
                        err=max(err,float(np.max(abs(replay-z[s]['value']))))
                        coef=c.coefficients(pp,d)
                        for t in (0.,.07,.19,.25):
                            polyerr=max(polyerr,abs(float(r7.bernstein_value(coef,t))-float(c.evaluate(pp,t,d)[0,c.center])))
                        for n in range(c.steps):assert np.all(c.allowed(n,adj,s)[np.arange(c.ns),pp[n]])
            # Value convexity in the fixed fee / benefit pair.
            cl=Contract(base,fee,1);cr=Contract(base,fee+.1,1);cm=Contract(base,fee+.04,1)
            l=cl.pair(.125,.4,adj);r=cr.pair(.125,.5,adj);m=cm.pair(.125,.44,adj)
            for s in SIGNS:convex_violation=max(convex_violation,float((m[s]['value']-.6*l[s]['value']-.4*r[s]['value']).max()))
    # Date-zero surrender is a distinct contract, not a first-risk experiment.
    c=Contract(base,0.,0)
    zero=max(abs(c.pair(lam,d,adj)[s]['value'][0,c.center]-c.terminal[c.center]) for lam,d in ((0.,.4),(.125,.425),(.25,.45)) for adj in (True,False) for s in SIGNS)
    assert max(err,polyerr,order,violation,convex_violation,zero)<2e-11
    return dict(class_point_comparisons=feasible,selected_control_reconstruction_error=err,polynomial_evaluation_error=polyerr,count_above_chord=order,upper_violation=violation,convexity_violation=convex_violation,date_zero_free_exit_error=zero)

def procurement(base):
    data=json.loads((OUT/'surrender.json').read_text());rows=[]
    for r in data['center']:
        if not ((r['min_term']==1 and r['fee'] in (0.,.7,.8,.85)) or r['min_term']==8):continue
        for regime in ('adjusted','no_adjustment'):
            x=r[regime];s=max(SIGNS,key=lambda a:x[a]['value']);a=x[s]['duration'];q=x['participation_payment']
            rows.append(dict(fee=r['fee'],minimum_term=r['min_term'],regime=regime,chosen_class=s,duration=a,participation_grant=q,break_even_service_flow=q/a,collateral_capacity=r['fee']))
    reach=np.zeros((base.steps+1,base.ns),bool);reach[0,base.center]=True
    for n in range(base.steps):
        for e in base.e:
            for k in [e.common]+e.extra[n:n+1]:reach[n+1]|=(k.matrix.T@np.repeat(reach[n].astype(float),k.na))>0
    exact=[]
    for adj in (True,False):
        c=Contract(base,0.,8);v=c.pair(.125,.425,adj)['positive']['value']
        for m in range(1,9):
            bound=max([0.]+[float(np.max((base.terminal-v[n])[reach[n]&~base.e[0].boundary])) for n in range(m,8)])
            exact.append(dict(adjustment=adj,minimum_term=m,statewise_no_surrender_threshold=bound))
    for m in range(1,9):assert exact[m-1]['statewise_no_surrender_threshold']<=exact[m+7]['statewise_no_surrender_threshold']+2e-12
    example=[]
    for r in rows:
        if r['fee']==.85:
            grant=r['participation_grant']+.01
            example.append(dict(regime=r['regime'],capacity=.85,capacity_cost=.01,net_principal_service_flow=.9,grant=grant,principal_surplus=.9*r['duration']-grant,break_even_service_flow=grant/r['duration']))
    assert example[0]['principal_surplus']>0 and example[1]['principal_surplus']<0
    save('procurement.json',dict(center=[.125,.425],zero_collateral_carry_cost_rows=rows,center_statewise_thresholds=exact,positive_capacity_cost_example=example,scope='separate additive utility numeraire; principal service flow accrues while operating; not a monetary calibration or globally optimal contract design'))

def main():
    verify_inputs();tiny=toy_tests();print('TOY',tiny,flush=True)
    base=Model();full=full_tests(base);procurement(base)
    save('validation.json',dict(toy=tiny,full=full,input_files=verify_inputs()['checked_files'],scope='enumeration, dense checks, and selected-control reconstruction test implementations; they do not replace proofs or enclose the transition constructor'))
    print('FULL',full,flush=True)
if __name__=='__main__':main()
