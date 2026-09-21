"""R4 independent regression/economic audits. Run after solver.py is available.
All tests report computed numbers. Null means unmeasured, never an implicit pass.
"""
from __future__ import annotations
import hashlib,json,sys,time,platform, itertools
from dataclasses import asdict,replace
from pathlib import Path
import numpy as np
import torch
from scipy.optimize import brentq
from solver import Config,states,actions,reference,transition_numpy,q_numpy,q_torch,settlement,interp,Terminal,BASE


def generator_audit():
    cfg=Config(); s=np.array([2.,1.]); a=np.array([.4,.13,.65])
    b=np.array([a[1],(cfg.r+cfg.excess*a[2])*s[1]-a[0]])
    cov=np.array([[cfg.su**2,cfg.su*cfg.sx*a[2]*s[1]*cfg.corr],
                  [cfg.su*cfg.sx*a[2]*s[1]*cfg.corr,(cfg.sx*a[2]*s[1])**2]])
    fun=lambda y: np.stack([np.ones(y.shape[:-1]),y[...,0],y[...,1],y[...,0]**2,y[...,1]**2,y[...,0]*y[...,1]],-1)
    exact=np.array([0,b[0],b[1],2*s[0]*b[0]+cov[0,0],2*s[1]*b[1]+cov[1,1],s[0]*b[1]+s[1]*b[0]+cov[0,1]])
    rows=[]
    for n in [10,20,40,80]:
        c=replace(cfg,n=n); hit,tau,inc=transition_numpy(s,a,c)
        gen=(fun(s+inc).mean(0)-fun(s))/c.dt
        est_cov=(inc-inc.mean(0)).T@(inc-inc.mean(0))/4/c.dt
        rows.append({'dt':c.dt,'generator':gen.tolist(),'max_error':float(abs(gen-exact).max()),
                     'drift_error':float(abs(inc.mean(0)/c.dt-b).max()),
                     'covariance_error':float(abs(est_cov-cov).max())})
    assert rows[-1]['max_error']<rows[0]['max_error']*.14
    assert max(r['covariance_error'] for r in rows)<1e-12
    c=replace(cfg,n=4,nu=7,nx=9,na=3); ss,bd=states(c); aa=actions(c)
    vv=settlement(1.,ss,c)
    qn=q_numpy(ss[:,None,:],aa[None,:,:],vv,.75,c)
    with torch.no_grad(): qt=q_torch(torch.tensor(ss,dtype=torch.float64),torch.tensor(aa,dtype=torch.float64),Terminal(),.75,c).numpy()
    discrepancy=float(abs(qn-qt).max()); assert discrepancy<1e-10
    # An actual exit: no reset/continuation is applied at the crossing point.
    h,f,d=transition_numpy(np.array([2.,.51]),np.array([.8,0.,0.]),c)
    assert np.all(f<1) and np.max(abs(h[:,1]-.5))<1e-12
    return {'evidence_class':'operator_identity','exact_generator':exact.tolist(),'refinement':rows,
            'numpy_torch_Bellman_discrepancy':discrepancy,'exit_fraction':f.tolist(),
            'exit_wealth':h[:,1].tolist(),'theta_mean_displacement':float(.2*cfg.dt)}


def temporal():
    rows=[]
    for beta in [.7,1.]:
        delta=1.; N=2; A=np.zeros(N+1); B=np.zeros(N+1); A[-1]=1.
        alpha=[]; residual=[]; grid_gain=[]
        for n in reversed(range(N)):
            c=1/(1+beta*delta*A[n+1]); alpha.insert(0,c)
            A[n]=1+delta*A[n+1]; B[n]=np.log(c)+delta*(A[n+1]*np.log(1-c)+B[n+1])
            w=np.linspace(.5,3,101); val=A[n]*np.log(w)+B[n]
            rhs=np.log(c*w)+delta*(A[n+1]*np.log((1-c)*w)+B[n+1])
            residual.append(float(abs(val-rhs).max()))
            fr=np.linspace(.001,.999,10001)
            q=np.log(fr)+beta*delta*(A[n+1]*np.log(1-fr)+B[n+1])
            best=np.log(c)+beta*delta*(A[n+1]*np.log(1-c)+B[n+1])
            grid_gain.append(float(max(0,q.max()-best)))
        rows.append({'beta':beta,'sophisticated_c0_ratio':alpha[0],
          'geometric_beta_c0_ratio':1/(1+beta+beta**2),
          'evaluation_equation_residual':max(residual),'dense_grid_deviation_lower_bound':max(grid_gain),
          'global_optimality_reason':'strict concavity of log(c)+beta*A_next*log(w-c); analytic FOC',
          'alpha_by_date':alpha,'ordinary_value_A':A.tolist(),'ordinary_value_B':B.tolist()})
    assert abs(rows[0]['sophisticated_c0_ratio']-5/12)<1e-12
    assert max(r['evaluation_equation_residual'] for r in rows)<1e-12
    return rows


def traces():
    rng=np.random.default_rng(410); A=np.array([[2.,1.],[1.,3.]]); a=3.5
    R=30000; rows=[]
    for K in [1,2,8,64]:
        z=rng.standard_normal((R,K,2)); q=np.einsum('rki,ij,rkj->rk',z,A,z)
        mean=q.mean(1); loss=(a-mean/2)**2; exact=(a-np.trace(A)/2)**2
        se=float(loss.std(ddof=1)/np.sqrt(R)); theory=exact+7.5/K
        row={'K':K,'repetitions':R,'square_of_probe_mean':float(loss.mean()),
             'theoretical_expectation':theory,'standard_error':se,
             'mean_of_individual_squares':float(((a-q/2)**2).mean()),
             'theoretical_wrong_estimand':exact+7.5,
             'bias_standard_errors':float((loss.mean()-theory)/se)}
        if K>1:
            pair=((q.sum(1)**2-(q*q).sum(1))/(K*(K-1)))
            u=a*a-a*mean+.25*pair
            row.update(unbiased_U_statistic_mean=float(u.mean()),U_standard_error=float(u.std(ddof=1)/np.sqrt(R)),U_target=exact)
        assert abs(row['bias_standard_errors'])<5
        rows.append(row)
    return rows


def actor_counterexample_and_graph():
    roots=np.sort(np.roots([4,0,-4,-.2]).real)
    H=lambda a: -(a*a-1)**2+.2*a
    local=roots[0]; glob=roots[-1]; gap=H(glob)-H(local)
    # The exact problem from the report; both actor critical points are isolated.
    assert gap>.39 and (4-12*local**2)<0
    own=torch.tensor(1/3,requires_grad=True); rival=torch.tensor(1/3,requires_grad=True)
    val=own*(1-own-rival.detach()); val.backward()
    detached=(rival.grad is None); assert detached
    return {'stationary_points':roots.tolist(),'suboptimal_stable_gap':float(gap),
        'local_second_derivative':float(4-12*local**2),
        'own_gradient_at_Nash':float(own.grad),'rival_gradient_is_none':detached}


def solve_zero_theta(cfg):
    ss,bd=states(cfg); aa=actions(cfg); aa=aa[aa[:,1]==0]
    V=np.zeros((cfg.n+1,len(ss))); V[-1]=settlement(cfg.T,ss,cfg)
    for n in reversed(range(cfg.n)):
        q=q_numpy(ss[:,None,:],aa[None,:,:],V[n+1],n*cfg.dt,cfg)
        V[n]=q.max(-1); V[n,bd]=settlement(n*cfg.dt,ss[bd],cfg)
    return V


def economic_panel():
    cfg=Config(n=12,nu=25,nx=31,na=5); ss,bd=states(cfg); center=np.array([2.,1.25])
    rows=[]; objs=[]; v0=solve_zero_theta(cfg)
    for k in [.5,2.,8.]:
        c=replace(cfg,k=k); r=reference(c); objs.append(r)
        i=np.argmin(((ss-center)**2).sum(-1)); ap=actions(c)[r['P'][0,i]]
        rows.append({'k':k,'center_value':float(r['V'][0,i]),'center_discounted_half_theta_square':float(r['B'][0,i]),
            'center_theta':float(ap[1]),'center_c':float(ap[0]),'center_pi':float(ap[2]),
            'center_flexibility_value':float(r['V'][0,i]-v0[0,i]),
            'center_exit_probability':float(r['Exit'][0,i]),
            'theta_nonzero_interior_share':float((abs(actions(c)[r['P'][:,~bd],1])>1e-12).mean()),
            'seconds':r['seconds']})
        np.savez_compressed(BASE/'results'/f'reference_k{k:g}.npz',**{a:r[a] for a in ['V','P','B','Exit']})
    monotoneV=max(float((objs[i+1]['V']-objs[i]['V']).max()) for i in range(2))
    monotoneB=max(float((objs[i+1]['B']-objs[i]['B']).max()) for i in range(2))
    flexmin=min(float((r['V']-v0).min()) for r in objs)
    assert monotoneV<1e-10 and monotoneB<1e-10 and flexmin>-1e-10
    return {'config':asdict(cfg),'rows':rows,'value_monotonicity_violation':max(0,monotoneV),
        'adjustment_budget_monotonicity_violation':max(0,monotoneB),'flexibility_dominance_violation':max(0,-flexmin)}


def refinement_panel():
    cfg=Config(n=6,nu=13,nx=16,na=5); center=np.array([2.,1.25]); rows=[]; last=None
    # Vary axes separately; do NOT relabel successive differences certified error.
    specs=[(6,13,16,5),(12,13,16,5),(12,25,31,5),(24,25,31,5),(24,49,61,5),(12,25,31,7)]
    for n,nu,nx,na in specs:
        c=replace(cfg,n=n,nu=nu,nx=nx,na=na); r=reference(c)
        rows.append({'n':n,'nu':nu,'nx':nx,'na_per_control':na,
            'center_value':float(interp(r['V'][0],center,c)),'seconds':r['seconds'],
            'continuous_value_error':None,'metric_reason':'separate refinement, not a certified continuum error'})
    for fee in [6.,10.]:
        c=Config(n=12,nu=25,nx=31,na=5,fee=fee); r=reference(c)
        rows.append({'fee':fee,'n':12,'nu':25,'nx':31,'na_per_control':5,
            'center_value':float(interp(r['V'][0],center,c)),'seconds':r['seconds'],'comparison_type':'different settlement contract'})
    return rows


def recursive_utility():
    # A full finite-horizon recursive SAVING problem (not a single aggregator point).
    # Fractional consumption and deterministic wealth are a declared specialization;
    # no portfolio/neural/general diffusion certificate is claimed by this test.
    rho=.04; gamma=5.; psi=1.5; a=1-1/psi; b=1-gamma; dt=.05; N=10
    xs=np.linspace(.5,2.,101); fractions=np.linspace(.01,.6,80)
    f=lambda c,V: rho/a*c**a*(b*V)**(1-a/b)-rho*b/a*V
    V=xs**b/b; terminal=V.copy(); maxres=0.; minsign=float((b*V).min()); policies=[]
    for n in reversed(range(N)):
        out=[]; pp=[]
        for x in xs:
            vals=[]
            for frac in fractions:
                c=frac*x; xn=x+dt*(.02*x-c)
                # Explicit extrapolation uses the declared terminal homothetic tail.
                vn=float(np.interp(xn,xs,V)) if .5<=xn<=2 else float(xn**b/b)
                F=lambda y:y-vn-dt*f(c,y)
                lo=-1e4; hi=-1e-10
                y=brentq(F,lo,hi,xtol=1e-12); maxres=max(maxres,abs(F(y))); vals.append(y)
            j=int(np.argmax(vals)); out.append(vals[j]); pp.append(fractions[j])
        V=np.array(out); policies.append(pp); minsign=min(minsign,float((b*V).min()))
    # Executed sign transform, including terminal targets, has a strict domain margin.
    W=torch.log(torch.tensor(b*terminal)); transformed=W.exp()/b
    error=float(abs(transformed-torch.tensor(terminal)).max())
    return {'evidence_class':'recursive_reference','horizon':N*dt,'dt':dt,'states':len(xs),'actions':len(fractions),
        'implicit_evaluation_equation_residual':maxres,'minimum_bV':minsign,
        'terminal_sign_transform_error':error,'V_center':float(np.interp(1.,xs,V)),
        'c_over_x_center':float(np.interp(1.,xs,policies[-1])),
        'neural_solution_error':None,'neural_solution_error_reason':'this run is an implicit scalar reference, not neural training',
        'outside_grid_rule':'terminal homothetic tail at each step; numerical boundary data, not an infinite-domain solution'}


def dynamic_cournot():
    K=np.array([0.,.5,1.]); Z=np.array([2.5,3.5]); trans=np.array([[.8,.2],[.2,.8]])
    N=3; delta=.96; V=np.zeros((N+1,2,3,3,2)); profile={}; maxdev=0; multi=0
    for n in reversed(range(N)):
      for z in range(2):
       for i,j in itertools.product(range(3),repeat=2):
        act=lambda k:list(itertools.product(np.arange(k+1)*.5,range(2 if k<2 else 1)))
        aa,bb=act(i),act(j); pay=np.zeros((len(aa),len(bb),2))
        for ia,(q1,inv1) in enumerate(aa):
         for ib,(q2,inv2) in enumerate(bb):
          price=Z[z]-q1-q2
          future=trans[z]@V[n+1,:,i+inv1,j+inv2,:]
          pay[ia,ib]=[q1*price-.2*inv1+.96*future[0],q2*price-.2*inv2+.96*future[1]]
        eq=[]
        for ia,ib in itertools.product(range(len(aa)),range(len(bb))):
          d1=pay[:,ib,0].max()-pay[ia,ib,0]; d2=pay[ia,:,1].max()-pay[ia,ib,1]
          if max(d1,d2)<1e-10: eq.append((ia,ib))
        if not eq: raise AssertionError(f'No pure equilibrium at {(n,z,i,j)}')
        multi+=len(eq)>1; ia,ib=eq[0]; V[n,z,i,j]=pay[ia,ib]
        maxdev=max(maxdev,pay[:,ib,0].max()-pay[ia,ib,0],pay[ia,:,1].max()-pay[ia,ib,1])
        profile[str((n,z,i,j))]=[list(aa[ia]),list(bb[ib])]
    return {'evidence_class':'finite_dynamic_game_reference','horizon_dates':N,'states_per_date':18,
        'capacity_grid':K.tolist(),'demand_states':Z.tolist(),'demand_transition':trans.tolist(),
        'investment_cost':.2,'discount':delta,'one_shot_deviation_max':float(maxdev),
        'states_with_multiple_pure_equilibria':multi,'selection':'lexicographic pure equilibrium backward induction',
        'profile':profile,'V_initial_low_demand_half_capacity':V[0,0,1,1].tolist(),
        'neural_MPE_error':None,'neural_MPE_error_reason':'finite exact game and separate graph test, not a trained neural game'}


def coupled_dynamic():
    rows=[]; rng=np.random.default_rng(240)
    for d in [4,8,16]:
        A=.8*np.eye(d)+.04*(np.eye(d,k=1)+np.eye(d,k=-1)); Q=np.eye(d)+.12*np.ones((d,d))/d
        R=.3*np.eye(d); S=.1*np.eye(d)+.02*np.ones((d,d))/d; Sigma=S@S.T; N=8
        P=np.eye(d); cc=0.; optimal=[]; start=time.perf_counter()
        for n in reversed(range(N)):
            F=-np.linalg.solve(R+P,P@A); cc+=np.trace(P@Sigma)
            P=Q+F.T@R@F+(A+F).T@P@(A+F); optimal.insert(0,F)
        tR=time.perf_counter()-start; Pn=torch.eye(d,dtype=torch.float64); cn=0.; learned=[]; start=time.perf_counter()
        At=torch.tensor(A); Qt=torch.tensor(Q); Rt=torch.tensor(R)
        # A linear neural actor and exact quadratic neural critic family.
        # Each policy-evaluation quadratic is represented explicitly; no dense state grid.
        for n in reversed(range(N)):
            W=torch.nn.Parameter(torch.zeros((d,d),dtype=torch.float64)); opt=torch.optim.LBFGS([W],lr=1.,max_iter=60,tolerance_grad=1e-10,tolerance_change=1e-13,line_search_fn='strong_wolfe')
            frozen=Pn.detach()
            def closure():
                opt.zero_grad(); C=Qt+W.T@Rt@W+(At+W).T@frozen@(At+W)
                l=torch.trace(C); l.backward(); return l
            opt.step(closure)
            cn+=float(torch.trace(frozen@torch.tensor(Sigma)))
            with torch.no_grad(): Pn=Qt+W.T@Rt@W+(At+W).T@frozen@(At+W)
            learned.insert(0,W.detach().numpy())
        tN=time.perf_counter()-start; X=rng.normal(size=(1000,d))
        err=np.einsum('bi,ij,bj->b',X,Pn.numpy()-P,X)+(cn-cc)
        rows.append({'d':d,'dates':N,'evidence_class':'coupled_stochastic_LQ_neural_actor',
          'matrix_value_error':float(abs(Pn.numpy()-P).max()),'heldout_value_error_max':float(abs(err).max()),
          'feedback_matrix_error':float(max(abs(f-g).max() for f,g in zip(learned,optimal))),
          'Riccati_seconds':tR,'neural_actor_seconds':tN,'shock_covariance_offdiagonal':float(Sigma[0,1]),
          'constraints':'unconstrained LQ; no constrained sparse-grid superiority inferred','peak_memory':None,
          'peak_memory_reason':'not measured by this timer'})
    return rows


def main():
    out=BASE/'results'; out.mkdir(exist_ok=True)
    names=sys.argv[1:] or ['generator','temporal','trace','actor','economic','refinement','recursive','game','dynamic']
    funcs=dict(generator=generator_audit,temporal=temporal,trace=traces,actor=actor_counterexample_and_graph,
        economic=economic_panel,refinement=refinement_panel,recursive=recursive_utility,game=dynamic_cournot,dynamic=coupled_dynamic)
    for name in names:
        st=time.perf_counter()
        try: result=funcs[name](); status='completed'
        except Exception as e:
            (out/(name+'.json')).write_text(json.dumps({'execution_status':'failed','error':repr(e)},indent=2)); raise
        record={'execution_status':status,'audit':name,'result':result,
          'source_base_commit':'79a7d84be2cbbf9bd5d181599ee110540128e3b5',
          'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'solver_sha256':hashlib.sha256((Path(__file__).parent/'solver.py').read_bytes()).hexdigest(),
          'elapsed_seconds':time.perf_counter()-st}
        (out/(name+'.json')).write_text(json.dumps(record,indent=2)); print(name,json.dumps(result)[:250],flush=True)
    (out/'environment.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'torch':torch.__version__,'device':'CPU','torch_threads':torch.get_num_threads()},indent=2))

if __name__=='__main__': main()
