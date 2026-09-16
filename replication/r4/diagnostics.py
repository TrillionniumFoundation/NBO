"""Independent analytical, recursive, dynamic-control and game diagnostics."""
import math,time
import numpy as np
import torch
from torch import nn
from scipy.optimize import minimize_scalar,root_scalar
from solver import *


def generator_tests():
    m=Model();s=np.array([[2.,1.]]);a=np.array([[.2,.1,.8]]);out=[]
    for h in [1e-2,1e-3,1e-4]:
        *_,d,alpha=transition(s,a,h,m);y=s[:,None,:]+d
        drift=np.array([.1,.02+.06*.8-.2]);cov=np.array([[.0025,-.002],[-.002,.0256]])
        fs=[lambda x:np.ones(x.shape[:-1]),lambda x:x[...,0],lambda x:x[...,1],lambda x:x[...,0]**2,
            lambda x:x[...,1]**2,lambda x:x[...,0]*x[...,1]]
        exact=np.array([0,drift[0],drift[1],4*drift[0]+cov[0,0],2*drift[1]+cov[1,1],drift[0]+2*drift[1]+cov[0,1]])
        approx=np.array([(f(y).mean()-f(s)[0])/h for f in fs])
        out.append(dict(h=h,approx=approx.tolist(),exact=exact.tolist(),max_error=float(abs(approx-exact).max())))
    assert out[-1]['max_error']<2e-6
    *_,d,_=transition(s,np.array([[.2,0.,.8]]),1e-3,m)
    covariance=np.cov(d[0].T,bias=True)/1e-3
    assert np.allclose(covariance,[[.0025,-.002],[-.002,.0256]],atol=1e-12)
    rng=np.random.default_rng(991);ss=rng.uniform(LO,HI,(200,2));aa=rng.uniform(ALO,AHI,(200,3))
    y,live,disc,flow,_,d,alpha=transition(ss,aa,.125,m)
    direct=(flow+disc*terminal(y)).mean(-1)
    tq=torch_backup(torch_terminal,torch.tensor(ss),torch.tensor(aa),.125,m).detach().numpy()
    assert abs(tq-direct).max()<1e-12
    yp=transition(s,np.array([[.2,.2,0.]]),.125,m)[0]
    ym=transition(s,np.array([[.2,-.2,0.]]),.125,m)[0]
    reach=float(yp[...,0].mean()-ym[...,0].mean());assert abs(reach-.05)<1e-12
    pre=ss[:,None,:]+d
    overshoot=np.maximum(np.maximum(LO-pre,pre-HI),0).max()
    return dict(polynomials=out,covariance=covariance.tolist(),numpy_torch_max_difference=float(abs(tq-direct).max()),
                preference_mean_difference=reach,killed_branch_fraction=float(np.mean(alpha<1)),
                pre_exit_overshoot_max=float(overshoot),regulator_magnitude=None,
                regulator_reason='Killed model; no reflection or reinjection regulator is defined.')


def temporal_tests():
    rows=[]
    for beta in [.7,1.]:
        delta=math.exp(-.04);A=1.;B=0.;ratios=[];coeffs=[(A,B)]
        for n in range(3,-1,-1):
            z=1/(1+beta*delta*A);anew=1+delta*A
            bnew=math.log(z)+delta*(A*math.log(1-z)+B)
            ratios.append(z);coeffs.append((anew,bnew));A,B=anew,bnew
        ratios=ratios[::-1];coeffs=coeffs[::-1];errors=[];gains=[]
        for n,z in enumerate(ratios):
            an,bn=coeffs[n+1]
            for w in [.5,1.,2.,4.]:
                obj=lambda x:math.log(x*w)+beta*delta*(an*math.log((1-x)*w)+bn)
                ref=minimize_scalar(lambda x:-obj(x),bounds=(1e-9,1-1e-9),method='bounded')
                gains.append(max(0.,-ref.fun-obj(z)))
                lhs=coeffs[n][0]*math.log(w)+coeffs[n][1]
                rhs=math.log(z*w)+delta*(an*math.log((1-z)*w)+bn)
                errors.append(abs(lhs-rhs))
        assert max(errors)<1e-12 and max(gains)<1e-9
        rows.append(dict(beta=beta,delta=delta,ratios=ratios,evaluation_residual=max(errors),one_shot_gain=max(gains)))
    return dict(runs=rows,two_date_beta07_correct=1/2.4,two_date_beta07_old=1/2.19)


def trace_tests(seed=819,batches=20000):
    rng=np.random.default_rng(seed);mat=np.array([[2.,1.],[1.,3.]]);rows=[];a=1.25;exact=(a-2.5)**2
    for k in [1,4,16,64]:
        z=rng.standard_normal((batches,k,2));q=np.einsum('bki,ij,bkj->bk',z,mat,z)
        r=a-q/2;loss=r.mean(1)**2;old=(r*r).mean(1)
        mean=float(loss.mean());se=float(loss.std(ddof=1)/math.sqrt(batches))
        row=dict(k=k,mean_squared_batch_residual=mean,mean_individual_squares=float(old.mean()),exact_loss=exact,
                 expected_loss=exact+7.5/k,mc_standard_error=se,variance_individual_probe=float(q.var()),variance_batch_mean=float(q.mean(1).var()))
        assert abs(mean-(exact+7.5/k))<6*se
        if k>1:
            debias=(r.sum(1)**2-(r*r).sum(1))/(k*(k-1))
            row.update(debiased_mean=float(debias.mean()),debiased_se=float(debias.std(ddof=1)/math.sqrt(batches)))
            assert abs(debias.mean()-exact)<6*row['debiased_se']
        rows.append(row)
    return dict(seed=seed,batches=batches,runs=rows)


def stationary_utility(seed=101,recursive=False):
    """Executed homothetic-feature neural critic and separate numerical AD actor.
    The fixed features encode homogeneity, not the unknown coefficient or policy.
    Frozen-policy evaluation solves a scalar equation; target ratios are used
    only afterwards as independent checks. These are not unconstrained MLP runs.
    """
    torch.manual_seed(seed);gamma=5. if recursive else 2.;b=1-gamma
    psi=1.5;aa=1-1/psi;rho=.04;r=.02;mu=.06;sig=.2
    raw=nn.Parameter(torch.tensor([-3.,-.3]));q=0.;logs=[]
    def actions():return .001+.199*torch.sigmoid(raw[0]),-.5+1.5*torch.sigmoid(raw[1])
    def H(loga,m,p):
        util=rho/aa*(m**aa*math.exp(-aa/b*loga)-1) if recursive else m**b*math.exp(-loga)/b-rho/b
        return util+r+mu*p-m+.5*(b-1)*sig**2*p*p
    for iteration in range(35):
        m,p=[float(x.detach()) for x in actions()]
        if recursive:q=float(root_scalar(lambda l:H(l,m,p),bracket=(-100,100),xtol=1e-12).root)
        else:
            denominator=rho-b*(r+mu*p-m+.5*(b-1)*sig**2*p*p)
            if denominator<=0:raise ValueError('inadmissible frozen Merton policy')
            q=math.log(m**b/denominator)
        opt=torch.optim.LBFGS([raw],lr=.8,max_iter=30,line_search_fn='strong_wolfe',tolerance_grad=1e-12,tolerance_change=1e-14)
        def closure():
            opt.zero_grad();mt,pt=actions()
            util=rho/aa*(mt.pow(aa)*math.exp(-aa/b*q)-1) if recursive else mt.pow(b)*math.exp(-q)/b-rho/b
            loss=-(util+r+mu*pt-mt+.5*(b-1)*sig**2*pt.square());loss.backward();return loss
        opt.step(closure)
        logs.append(dict(iteration=iteration,log_value_coefficient=q,m=float(actions()[0].detach()),pi=float(actions()[1].detach())))
    m,p=[float(x.detach()) for x in actions()]
    mstar=psi*rho+(1-psi)*(r+mu**2/(2*gamma*sig**2)) if recursive else (rho+(gamma-1)*(r+mu**2/(2*gamma*sig**2)))/gamma
    pstar=mu/(gamma*sig**2);astar=(rho*mstar**(aa-1))**(b/aa) if recursive else mstar**(-gamma)
    x=torch.logspace(-1,1,101,requires_grad=True);v=math.exp(q)*x.pow(b)/b
    vx=torch.autograd.grad(v.sum(),x,create_graph=True)[0];vxx=torch.autograd.grad(vx.sum(),x)[0]
    utility=rho/aa*((m*x).pow(aa)*(b*v).pow(1-aa/b)-b*v) if recursive else (m*x).pow(b)/b-rho*v
    hjb=utility+(r+mu*p-m)*x*vx+.5*sig**2*p*p*x*x*vxx
    return dict(model='Epstein-Zin' if recursive else 'Merton',seed=seed,m=m,pi=p,m_target=mstar,pi_target=pstar,
                policy_max_error=max(abs(m-mstar),abs(p-pstar)),relative_value_coefficient_error=abs(math.exp(q)/astar-1),
                normalized_hjb_max=float((hjb.detach()/v.detach().abs()).abs().max()),
                domain_min=float((b*v).detach().min()) if recursive else None,
                log_value_coefficient=q,actor_raw=raw.detach().tolist(),logs=logs,
                evidence_class='executed_stationary_homothetic_feature_solver')


def lqr_test(d,seed=101,steps=6):
    """Coupled stochastic dynamics: quadratic-feature critic and linear actor.
    Independent Riccati baseline and independent frozen-policy evaluation.
    No claim about constrained or general nonlinear scalability is made.
    """
    rng=np.random.default_rng(seed);torch.manual_seed(seed);start=time.perf_counter()
    A=.82*np.eye(d)+.07*(np.eye(d,k=1)+np.eye(d,k=-1));B=.2*np.eye(d)
    Q=np.eye(d)+.3*np.ones((d,d))/d;R=.15*np.eye(d)
    Sigma=.08*(np.eye(d)+.3*np.ones((d,d))/d);cov=Sigma@Sigma.T
    Ps=[None]*(steps+1);Ks=[None]*steps;cs=[0.]*(steps+1);Ps[-1]=Q
    for n in range(steps-1,-1,-1):
        p=Ps[n+1];k=np.linalg.solve(R+B.T@p@B,B.T@p@A)
        Ks[n]=k;Ps[n]=Q+A.T@p@A-A.T@p@B@k;cs[n]=cs[n+1]+np.trace(p@cov)
    baseline_time=time.perf_counter()-start;train_start=time.perf_counter()
    x=torch.tensor(rng.standard_normal((max(512,3*d*d),d)));xx=x.numpy();il,jl=np.triu_indices(d)
    features=np.concatenate((np.ones((len(xx),1)),xx[:,il]*xx[:,jl]),1)
    lp=Q.copy();lc=0.;learned=[None]*steps;fits=[]
    for n in range(steps-1,-1,-1):
        actor=nn.Linear(d,d,bias=False);actor.weight.data.zero_()
        at=torch.tensor(A);bt=torch.tensor(B);qt=torch.tensor(Q);rt=torch.tensor(R);pt=torch.tensor(lp)
        def obj():
            u=actor(x);y=x@at.T+u@bt.T
            return (torch.einsum('bi,ij,bj->b',x,qt,x)+torch.einsum('bi,ij,bj->b',u,rt,u)+torch.einsum('bi,ij,bj->b',y,pt,y)).mean()/d
        fit_lbfgs(actor,obj,90);kk=-actor.weight.detach().numpy();learned[n]=kk
        u=-xx@kk.T;y=xx@A.T+u@B.T
        target=np.einsum('bi,ij,bj->b',xx,Q,xx)+np.einsum('bi,ij,bj->b',u,R,u)+np.einsum('bi,ij,bj->b',y,lp,y)+lc+np.trace(lp@cov)
        coeff=np.linalg.lstsq(features,target,rcond=None)[0];pnew=np.zeros((d,d));pnew[il,jl]=coeff[1:];pnew[jl,il]=coeff[1:]
        pnew[il[il!=jl],jl[il!=jl]]/=2;pnew[jl[il!=jl],il[il!=jl]]/=2
        lp=pnew;lc=float(coeff[0]);fits.append(float(abs(features@coeff-target).max()))
    elapsed=time.perf_counter()-train_start;pv=Q.copy();cv=0.
    for kk in learned[::-1]:
        F=A-B@kk;cv+=np.trace(pv@cov);pv=Q+kk.T@R@kk+F.T@pv@F
    test=rng.standard_normal((2048,d));err=np.einsum('bi,ij,bj->b',test,pv-Ps[0],test)+cv-cs[0]
    return dict(d=d,seed=seed,steps=steps,baseline_seconds=baseline_time,neural_seconds=elapsed,
                evaluated_cost_excess_max=float(err.max()/d),evaluated_cost_excess_mean=float(err.mean()/d),
                actor_coefficient_max_error=max(float(abs(a-b).max()) for a,b in zip(learned,Ks)),
                critic_fit_max=max(fits),stochastic_covariance_trace=float(np.trace(cov)),
                coupling_A_offdiagonal=.07,coupling_Q_rank_one=.3,
                constraints='unconstrained LQR',evidence_class='executed_quadratic_feature_neural_dynamic_control')


def game_test(steps=4):
    """Stochastic Cournot capacity-investment reference on all eight states.
    Demand follows a two-state Markov chain. Investment a_i is the probability
    of capacity one next period; .4*a_i^2/2 is a maintenance/investment cost.
    A full dynamic best response against the frozen rival is solved afterwards.
    """
    delta=.95;kappa=.4;demand=np.array([1.,1.3]);P=np.array([[.8,.2],[.2,.8]])
    states=list(itertools.product(range(2),repeat=3));V=np.zeros((steps+1,2,2,2,2));pol=np.zeros((steps,2,2,2,2))
    for k1,k2,z in states:V[-1,:,k1,k2,z]=[.05*k1,.05*k2]
    contraction=0.
    def expectation(table,x,y):return float((table*(np.array([[1-x],[x]])@np.array([[1-y,y]]))).sum())
    for n in range(steps-1,-1,-1):
        for k1,k2,z in states:
            W=np.einsum('ijk,k->ij',V[n+1,0],P[z]);Z=np.einsum('ijk,k->ij',V[n+1,1],P[z])
            a1=delta*(W[1,0]-W[0,0])/kappa;b1=delta*(W[1,1]-W[1,0]-W[0,1]+W[0,0])/kappa
            a2=delta*(Z[0,1]-Z[0,0])/kappa;b2=delta*(Z[1,1]-Z[1,0]-Z[0,1]+Z[0,0])/kappa
            contraction=max(contraction,abs(b1*b2));candidates=[]
            for init in [0.,.5,1.]:
                x=y=init
                for _ in range(500):
                    xn=np.clip(a1+b1*y,0,1);yn=np.clip(a2+b2*xn,0,1)
                    if max(abs(xn-x),abs(yn-y))<1e-14:break
                    x,y=xn,yn
                candidates.append((float(xn),float(yn)))
            assert np.max(np.ptp(candidates,axis=0))<1e-10
            x,y=candidates[0];pol[n,:,k1,k2,z]=x,y;q1=k1/3;q2=k2/3
            V[n,0,k1,k2,z]=q1*(demand[z]-q1-q2)-.5*kappa*x*x+delta*expectation(W,x,y)
            V[n,1,k1,k2,z]=q2*(demand[z]-q1-q2)-.5*kappa*y*y+delta*expectation(Z,x,y)
    maxgain=0.
    for player in [0,1]:
        BR=V[-1,player].copy()
        for n in range(steps-1,-1,-1):
            new=np.empty((2,2,2))
            for k1,k2,z in states:
                W=np.einsum('ijk,k->ij',BR,P[z]);rival=pol[n,1-player,k1,k2,z]
                marginal=((1-rival)*(W[1,0]-W[0,0])+rival*(W[1,1]-W[0,1])) if player==0 else ((1-rival)*(W[0,1]-W[0,0])+rival*(W[1,1]-W[1,0]))
                own=float(np.clip(delta*marginal/kappa,0,1));x,y=(own,rival) if player==0 else (rival,own)
                qi=(k1 if player==0 else k2)/3;qj=(k2 if player==0 else k1)/3
                new[k1,k2,z]=qi*(demand[z]-qi-qj)-.5*kappa*own**2+delta*expectation(W,x,y)
            BR=new
        maxgain=max(maxgain,float(np.max(BR-V[0,player])))
    own=torch.tensor(.4,requires_grad=True);rival=torch.tensor(.6,requires_grad=True)
    val=own*(1-own-rival.detach());go,gr=torch.autograd.grad(val,(own,rival),allow_unused=True)
    assert gr is None and maxgain<1e-10
    return dict(steps=steps,states=8,demand=demand.tolist(),transition=P.tolist(),discount=delta,investment_cost=kappa,
                max_dynamic_exploitability=maxgain,max_best_response_product=contraction,policies=pol.tolist(),values=V.tolist(),
                rival_gradient_is_none=gr is None,own_gradient=float(go.detach()),
                evidence_class='independent_dynamic_game_reference_and_autodiff_graph_test')
