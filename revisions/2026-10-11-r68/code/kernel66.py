"""R66 operational curvature screens and prediction diagnostics.

Inherited original-law kernels remain unchanged. Predictor output has no
certificate authority. Returned unqueried actions use an outward strong-
convexity chord, not a fitted value or a sampled derivative.
"""
from pathlib import Path
import sys,time,itertools,warnings
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'2026-10-10-r64/code'))
import query64 as old
q=old.q;F=q.F;I=q.I;B=q.B

def chord_upper(l,u,L,U,a,mu=F(2)):
    width=I.point(u)-I.point(l)
    s=(I.point(a)-I.point(l))/width
    value=(1-s)*I.point(L)+s*I.point(U)-q.rat(mu/2)*(I.point(a)-I.point(l))*(I.point(u)-I.point(a))
    return value.hi

def feature(x,kind):
    z=q.coefficients(x)
    if kind=='quadratic':return q.polynomial(z)
    if kind=='spline':
        # Continuous piecewise-linear additive spline, fixed knots.
        return np.column_stack([np.ones(len(z)),z]+[np.maximum(0,z-k) for k in (.25,.5,.75)])
    return np.column_stack([np.ones(len(z)),z])

def predict(kind,model,x,cap):
    if kind=='relu':
        W,b,u,c=model;value=np.maximum(0,q.coefficients(x)@W+b)@u+c
    elif kind=='nearest':
        states,actions=model
        # Finite training catalogue, not a stored policy on a state lattice.
        distance=((x[:,None,:]-states[None,:,:])**2).sum(axis=2)
        value=actions[np.argmin(distance,axis=1)]
    elif kind=='derivative':value=q.terminal_guess(x)
    elif kind=='heuristic':value=cap/2
    else:value=feature(x,kind)@model
    return q.clamp(value,cap)

LEARNED=('relu','quadratic','linear','spline','nearest')
KINDS=('adaptive','bisection','upper-minimizer','relu','quadratic','linear','spline','nearest','derivative','heuristic')

def fit(d,T,seed,kind,rows=96):
    if kind not in LEARNED:return {},dict(rows=0,dates=[],warnings=[],seconds=0.,labels=0)
    rng=np.random.default_rng(seed);states=rng.integers(0,2**16,size=(rows,d))/2**16
    states[:4]=np.array([np.zeros(d),np.ones(d),np.full(d,.25),np.full(d,.75)])
    models={};report=[];start=time.perf_counter();q.APPROX_COUNTS.update(training_value_nodes=0,training_q_queries=0)
    for r in range(2,T+1):
        begin=time.perf_counter();actions,_=q.approximate(states,r,q=2,iters=5 if r>=3 else 9)
        labeltime=time.perf_counter()-begin;begin=time.perf_counter();messages=[]
        if kind=='relu':
            from sklearn.neural_network import MLPRegressor
            m=MLPRegressor(hidden_layer_sizes=(24,),activation='relu',solver='lbfgs',alpha=1e-5,
                           max_iter=160,max_fun=2000,tol=1e-8,random_state=seed+r)
            with warnings.catch_warnings(record=True) as ws:
                warnings.simplefilter('always');m.fit(q.coefficients(states),actions)
            messages=[str(w.message) for w in ws]
            model=(m.coefs_[0],m.intercepts_[0],m.coefs_[1].ravel(),float(m.intercepts_[1][0]))
        elif kind=='nearest':model=(states.copy(),actions.copy())
        else:
            z=feature(states,kind);reg=np.eye(z.shape[1])*1e-6;reg[0,0]=0
            model=np.linalg.solve(z.T@z+reg,z.T@actions)
        models[r]=model;pred=predict(kind,model,states,q.cap_point(states))
        report.append(dict(r=r,label_seconds=labeltime,fit_seconds=time.perf_counter()-begin,
                           mse=float(np.mean((pred-actions)**2)),warnings=messages))
    return models,dict(rows=rows,dates=report,seconds=time.perf_counter()-start,
                       labels=(T-1)*rows,work=q.APPROX_COUNTS.copy())

def dump_models(kind,models):
    return {str(r):([np.asarray(v).tolist() for v in model] if kind in ('relu','nearest') else np.asarray(model).tolist()) for r,model in models.items()}

def load_models(kind,payload):
    return {int(r):(tuple(np.asarray(v) for v in model) if kind in ('relu','nearest') else np.asarray(model)) for r,model in payload.items()}

class Oracle(old.Oracle):
    def __init__(self,kind='adaptive',models=None,screen=True,record=False):
        mode=kind if kind in ('adaptive','bisection') else ('adaptive' if kind=='upper-minimizer' else 'relu')
        super().__init__(mode,models)
        self.kind=kind;self.screen=screen;self.record=record;self.progress=[];self.screens=[];self.calls=0
        self.counts.update(screen_attempts=0,screen_returns=0,prediction_seconds=0.,planned_routes=0)
    def propose(self,x,r,cap):
        start=time.perf_counter();self.counts['learned_proposals']+=len(x)
        answer=predict(self.kind,self.models.get(r),x,cap)
        self.counts['prediction_seconds']+=time.perf_counter()-start
        return answer
    def _solve(self,x,r,tol):
        x=np.asarray(x,dtype=float)
        if x.ndim!=2 or x.shape[1]%2 or r<1 or not np.all(np.isfinite(x)) or np.any(x<0) or np.any(x>1):
            raise ValueError('Invalid state')
        if not 0<tol<1:raise ValueError('Invalid tolerance')
        N,d=x.shape
        call=self.calls;self.calls+=1
        if r==1:return self.terminal(x,tol)
        self.counts['value_queries']+=N
        self.counts['max_batch']=max(N,self.counts['max_batch'])
        G,M=q.regularity(r-1,d);H=F(21,4)+B*M*F(5*d,32)
        lam=F(13,16)+B*G*F(3*d,8)
        capacity=q.cap_interval(x);cap=q.clamp(capacity.lo,capacity.lo)
        missing=q.rat(lam)*(I.point(capacity.hi)-I.point(cap))
        points=np.zeros((N,self.max_probes));lows=np.zeros_like(points);highs=np.zeros_like(points)
        points[:,1]=cap;size=np.full(N,2,dtype=int)
        left=self.q(x,points[:,0],r,tol);right=self.q(x,cap,r,tol)
        lows[:,0]=left.lo;highs[:,0]=left.hi;lows[:,1]=right.lo;highs[:,1]=right.hi
        running_lower=np.nextafter(q.parabola_lower(left.lo,right.lo,cap,H)-missing.hi,-np.inf)
        predicted=np.full(N,np.nan);asked=np.zeros(N,dtype=bool)
        active=np.arange(N);outlo=np.zeros(N);outup=np.zeros(N);outact=np.zeros(N)
        while len(active):
            width=int(size[active].max());cols=np.arange(width-1)[None,:]
            valid=cols<(size[active]-1)[:,None]
            p=points[active,:width];ll=lows[active,:width];hh=highs[active,:width]
            used=np.arange(width)[None,:]<size[active,None]
            endwidth=(I.point(hh)-I.point(ll)+I.point(missing.hi[active,None])).hi
            if np.any(used & (endwidth>5*tol/8)):
                raise RuntimeError('Precision budget exceeded; certificate withheld')
            h=I.point(p[:,1:])-I.point(p[:,:-1]);K=q.rat(H/2)*h.square()
            lft=I.point(ll[:,:-1]);rgt=I.point(ll[:,1:]);diff=rgt-lft
            safeK=np.where(valid,K.hi,1.);kk=I.point(safeK)
            mid=(lft+rgt)/2-kk/4-diff.square()/(4*kk)
            low=np.where(diff.lo>=safeK,lft.lo,np.where(diff.hi<=-safeK,rgt.lo,mid.lo))
            low=np.where(valid,low,np.inf)
            which=np.argmin(low,axis=1)
            lb=np.nextafter(np.maximum(0,low[np.arange(len(active)),which]-missing.hi[active]),-np.inf)
            running_lower[active]=np.maximum(running_lower[active],lb);lb=running_lower[active]
            candidate=np.where(used,hh,np.inf);best=np.argmin(candidate,axis=1)
            ub=candidate[np.arange(len(active)),best];gap=(I.point(ub)-I.point(lb)).hi
            done=gap<=tol;ids=active[done]
            outlo[ids]=lb[done];outup[ids]=ub[done];outact[ids]=p[np.flatnonzero(done),best[done]]
            first=done & (size[active]==2)
            self.counts['accepted_first_partition']+=int(first.sum())
            self.counts['prediction_free_returns']+=int(first.sum())
            todo=active[~done];interval=which[~done]
            if not len(todo):break
            if np.any(size[todo]>=self.max_probes):raise RuntimeError('Declared refinement cap exhausted')
            l=points[todo,interval];u=points[todo,interval+1];fraction=np.full(len(todo),.5)
            if self.mode!='bisection':
                k=q.up(H/2)*(u-l)**2;dif=lows[todo,interval+1]-lows[todo,interval]
                fraction=np.clip(.5-dif/(2*k),.25,.75)
            probe=q.clamp(l+fraction*(u-l),u)
            if self.mode in ('relu','quadratic'):
                new=todo[~asked[todo]]
                if len(new):predicted[new]=self.propose(x[new],r,cap[new]);asked[new]=True
                suggestion=predicted[todo]
                route=(suggestion>=l+.25*(u-l)) & (suggestion<=u-.25*(u-l))
                probe=np.where(route,suggestion,probe)
                self.counts['planned_routes']+=int(route.sum())
                self.counts['prediction_declined']+=int((~route).sum())
            # Compute a valid upper endpoint for the actual rounded proposal
            # from strong convexity, before spending a new Bellman query.
            if self.kind=='upper-minimizer':
                w=points[todo,interval+1]-points[todo,interval]
                slope=highs[todo,interval+1]-highs[todo,interval]
                probe=q.clamp((l+u)/2-slope/(2*w),u)
                probe=np.maximum(l,np.minimum(u,probe))
            if self.screen:
                screen_action=probe.copy()
                if self.mode in ('relu','quadratic'):
                    screen_action=predicted[todo]
                screen_action=q.clamp(screen_action,cap[todo])
                col=np.sum((points[todo,:width]<=screen_action[:,None]) &
                           (np.arange(width)[None,:]<size[todo,None]),axis=1)-1
                col=np.minimum(np.maximum(col,0),size[todo]-2)
                upper=chord_upper(points[todo,col],points[todo,col+1],
                                  highs[todo,col],highs[todo,col+1],screen_action)
                gap_screen=(I.point(upper)-I.point(running_lower[todo])).hi
                closed=gap_screen<=tol
                self.counts['screen_attempts']+=len(todo)
                self.counts['screen_returns']+=int(closed.sum())
                if self.record:
                    self.screens.append(np.column_stack([np.full(len(todo),call),np.full(len(todo),r),todo,
                      screen_action,upper,running_lower[todo],gap_screen,closed.astype(int)]))
                ids=todo[closed]
                outlo[ids]=running_lower[ids];outup[ids]=upper[closed];outact[ids]=screen_action[closed]
                todo=todo[~closed];interval=interval[~closed];probe=probe[~closed];l=l[~closed];u=u[~closed]
                if not len(todo):break
            if self.kind=='upper-minimizer':
                probe=q.clamp(np.maximum(l+.25*(u-l),np.minimum(u-.25*(u-l),probe)),u)
            if np.any((probe<=l)|(probe>=u)|(probe<l+.2*(u-l))|(probe>u-.2*(u-l))):
                raise RuntimeError('Rounded query violates protected interior')
            oldlower=running_lower[todo].copy()
            oldupper=np.array([highs[row,:size[row]].min() for row in todo])
            val=self.q(x[todo],probe,r,tol)
            self.counts['routed_queries']+=int(np.count_nonzero(np.isfinite(predicted[todo]) & (probe==predicted[todo])))
            for row,j,v,vl,vu in zip(todo,interval+1,probe,val.lo,val.hi):
                sz=size[row]
                points[row,j+1:sz+1]=points[row,j:sz].copy()
                lows[row,j+1:sz+1]=lows[row,j:sz].copy();highs[row,j+1:sz+1]=highs[row,j:sz].copy()
                points[row,j]=v;lows[row,j]=vl;highs[row,j]=vu;size[row]+=1
            if self.record:
                rows=[]
                for row,a,vl,vu,L0,U0 in zip(todo,probe,val.lo,val.hi,oldlower,oldupper):
                    k=size[row];xx=points[row,:k];ll=lows[row,:k];hh=highs[row,:k]
                    envelope=q.parabola_lower(ll[:-1],ll[1:],np.diff(xx),H)
                    L1=max(L0,float(np.nextafter(envelope.min()-missing.hi[row],-np.inf)),0.)
                    U1=min(U0,float(hh.min()))
                    routed=int(np.isfinite(predicted[row]) and a==predicted[row])
                    rows.append([call,r,row,a,L0,U0,L1,U1,U0-U1,L1-L0,routed,vl,vu])
                self.progress.append(np.asarray(rows,dtype=float))
            self.counts['refinements']+=len(todo);active=todo
        self.counts['max_probes']=max(self.counts['max_probes'],int(size.max()))
        if np.any(outup<outlo) or np.any(outact>capacity.lo):raise AssertionError('Invalid certificate')
        return dict(lower=outlo,upper=outup,action=outact,probes=size,
                    gap=(I.point(outup)-I.point(outlo)).hi,
                    fitted_selected=asked & np.isfinite(predicted) & (outact==predicted))
