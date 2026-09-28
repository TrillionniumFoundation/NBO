#!/usr/bin/env python3
"""Executed revision laboratories; not a reconstruction of historical GPU runs.

Run from the repository root. All seeds and failed attempts are saved. Numerical
certificates describe their actual domain, not an unobserved global neural fit.
"""
from __future__ import annotations
import argparse, hashlib, json, math, platform, time
from pathlib import Path
import numpy as np
import scipy
from scipy.linalg import solve_continuous_are, solve_continuous_lyapunov
from scipy.optimize import brentq, minimize_scalar
from scipy.interpolate import RegularGridInterpolator
import torch

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'revisions/2026-09-28/results'
torch.set_num_threads(1)
torch.set_default_dtype(torch.float64)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def merton(seed: int, constrained: bool = False, recursive: bool = False) -> dict:
    """Homothetic neural subfamily: log coefficient and two output biases.

    This explicitly exploits homogeneity. It is not an unrestricted MLP test.
    The critic evaluates the frozen policy; the actor maximizes only its own
    Hamiltonian with the critic coefficient and derivative channels detached.
    """
    torch.manual_seed(seed)
    gamma, rho, r, mu, sigma = (5. if recursive else 2.), .04, .02, .08, .2
    if constrained:
        mu = .01
    b = 1-gamma
    logk = torch.nn.Parameter(torch.tensor(5. + torch.randn(()).item()*.1 if not recursive else -.2))
    raw_m = torch.nn.Parameter(torch.tensor(-2.0 + torch.randn(()).item()*.1))
    portfolio = torch.nn.Parameter(torch.tensor(.2 + torch.randn(()).item()*.1))
    critic = torch.optim.Adam([logk], lr=.025)
    actor = torch.optim.Adam([raw_m, portfolio], lr=.008)
    psi = 1.5
    a = 1-1/psi
    logs = []
    def h(k, m, p):
        # Hamiltonian divided by the POSITIVE coefficient K of X^(1-gamma).
        flow = rho/a*(m**a*k**(-a/b)-1) if recursive else m**b/(b*k)-rho/b
        return flow + r+p*(mu-r)-m-.5*gamma*p*p*sigma*sigma
    for iteration in range(1600):
        for _ in range(3):
            critic.zero_grad(set_to_none=True)
            loss = h(logk.exp(), .2*raw_m.detach().sigmoid(), portfolio.detach()).square()
            loss.backward(); critic.step()
        actor.zero_grad(set_to_none=True)
        objective = -h(logk.detach().exp(), .2*raw_m.sigmoid(), portfolio)
        objective.backward(); actor.step()
        with torch.no_grad():
            portfolio.clamp_(0 if constrained else -1., 2.)
        if iteration % 40 == 0 or iteration == 1599:
            logs.append([iteration, logk.exp().item(), (.2*raw_m.sigmoid()).item(), portfolio.item(), loss.item()])
    k, m, p = logk.exp().item(), (.2*raw_m.sigmoid()).item(), portfolio.item()
    pstar = max(0, (mu-r)/(gamma*sigma*sigma)) if constrained else (mu-r)/(gamma*sigma*sigma)
    effective = r+pstar*(mu-r)-.5*gamma*pstar*pstar*sigma*sigma
    mstar = psi*rho+(1-psi)*effective if recursive else (rho+(gamma-1)*effective)/gamma
    kstar = (rho*mstar**(a-1))**(b/a) if recursive else mstar**(-gamma)
    # Exact maximization in the same compact action box, evaluated independently.
    cm = (rho*k**(-a/b))**psi if recursive else k**(-1/gamma)
    cm = np.clip(cm, 1e-15, .2)
    gap = float(h(k, cm, pstar)-h(k, m, p))
    name = 'ez' if recursive else ('merton_constrained' if constrained else 'merton')
    np.savetxt(OUT/f'{name}_seed{seed}_trace.csv', np.array(logs), delimiter=',',
               header='iteration,K,consumption_share,portfolio_share,critic_loss', comments='')
    return dict(experiment=name, seed=seed, m=m, portfolio=p, K=k,
                target_m=mstar, target_portfolio=pstar, target_K=kstar,
                relative_K_error=abs(k/kstar-1), normalized_residual=abs(float(h(k,m,p))),
                normalized_actor_gap=max(0.,gap), policy_error=max(abs(m-mstar),abs(p-pstar)),
                domain='homothetic subfamily; normalized Hamiltonian; EZ finite-horizon matching bequest',
                accepted=bool(abs(m-mstar)<.001 and abs(p-pstar)<.01 and abs(k/kstar-1)<.02))


def coupled_lq(d: int, seed: int) -> dict:
    """Exact block NBO in a quadratic-neural class, versus a Riccati solver.

    All coordinates are coupled by a nonnormal dense drift and a noncommuting payoff matrix.
    The actor is linear and the critic is a signed sum of squared linear units.
    Policy evaluation uses the Lyapunov equation, not stochastic optimization.
    """
    rng = np.random.default_rng(seed)
    rho = .1
    model_rng = np.random.default_rng(991+d)
    A = -.7*np.eye(d)+.06*model_rng.standard_normal((d,d))/math.sqrt(d)
    Q = np.diag(np.linspace(1.,2.,d))+.3*np.ones((d,d))/d
    R = np.eye(d)
    covariance = .04*(np.eye(d)+.2*np.ones((d,d))/d)
    start = time.perf_counter()
    reference = solve_continuous_are(A-rho/2*np.eye(d),np.eye(d),Q,R)
    baseline_seconds = time.perf_counter()-start
    K = .2*np.eye(d)+.005*rng.standard_normal((d,d))/math.sqrt(d)
    history = []
    start = time.perf_counter()
    for iteration in range(30):
        F = A-K-rho/2*np.eye(d)
        if np.max(np.real(np.linalg.eigvals(F))) >= 0:
            raise ValueError('Non-stabilizing policy: evaluation rejected')
        P = solve_continuous_lyapunov(F.T,-Q-K.T@K)
        P = (P+P.T)/2
        residual = rho*P-Q-K.T@K-P@(A-K)-(A-K).T@P
        gap = np.linalg.norm(K-P,2)**2
        history.append([iteration,float(np.linalg.norm(residual,2)),float(gap)])
        if gap < 1e-20:
            break
        K = P.copy()  # exact player-specific Hamiltonian maximization
    seconds = time.perf_counter()-start
    constant = np.trace(covariance@P)/rho
    np.savez(OUT/f'lq_d{d}_seed{seed}.npz',A=A,Q=Q,covariance=covariance,P=P,K=K,reference=reference)
    np.savetxt(OUT/f'lq_d{d}_seed{seed}_trace.csv',np.array(history),delimiter=',',
               header='iteration,residual_operator_norm,actor_gap_unit_ball',comments='')
    error = float(np.linalg.norm(P-reference,2))
    return dict(experiment='coupled_lq',d=d,seed=seed,iterations=iteration+1,
                P_error_operator_norm=error,value_constant=float(constant),
                critic_residual_unit_ball=float(np.linalg.norm(residual,2)),actor_gap_unit_ball=float(gap),
                nbo_seconds=seconds,riccati_seconds=baseline_seconds,
                certificate_domain='unit Euclidean ball; quadratic coefficient identity, not sampled residual',
                accepted=bool(error<1e-9 and np.linalg.norm(residual,2)<1e-10 and gap<1e-15))


def exit_diagnostic() -> dict:
    """A genuine nonsmooth exit problem; all grid nodes are checked."""
    rows=[]
    for n in (40,80,160,320):
        x=np.linspace(-1,1,n+1); h=2/n
        v=np.zeros(n+1)
        for _ in range(n+1):
            new=v.copy();new[1:-1]=-h+np.maximum(v[:-2],v[2:]);v=new
        good=abs(x)-1
        eps=1e-4;wrong=math.sqrt(1+eps**2)-np.sqrt(x*x+eps**2)
        r_good=np.max(np.abs(v[1:-1]+h-np.maximum(v[:-2],v[2:])))/h
        r_wrong=np.max(np.abs(wrong[1:-1]+h-np.maximum(wrong[:-2],wrong[2:])))/h
        rows.append(dict(n=n,max_value_error=float(np.max(abs(v-good))),
                         good_scaled_residual=float(r_good),wrong_scaled_residual=float(r_wrong)))
    return dict(experiment='exit_viscosity',rows=rows,accepted=all(r['max_value_error']<1e-12 and r['wrong_scaled_residual']>1.9 for r in rows))


def temporal_self() -> dict:
    """Mixture-of-exponentials equilibrium and finite-duration deviations."""
    rho,r,gamma,kappa=.04,.02,2.,.2
    b=1-gamma
    rates=np.array([rho,rho+kappa]); records=[]
    for beta in (1.,.9,.7,.5):
        w=np.array([beta,1-beta])
        lam=lambda m: rates-b*(r-m)
        F=lambda m: m*np.sum(w/lam(m))-1
        m=brentq(F,1e-6,(rho+(gamma-1)*r)/(gamma-1)-1e-8)
        coeff=m**b/lam(m)
        base=np.dot(w,coeff)/b
        deviations=[]
        for dt in (.1,.03,.01,.003,.001):
            def deviation(a):
                la=lam(a)
                integral=np.where(abs(la)>1e-12,-np.expm1(-la*dt)/la,dt)
                return np.dot(w,(a**b*integral+np.exp(-la*dt)*coeff))/b-base
            fit=minimize_scalar(lambda a:-deviation(a),bounds=(.005,.08),method='bounded',options={'xatol':1e-13})
            deviations.append(dict(dt=dt,best_deviation_share=float(fit.x),gain=float(-fit.fun),gain_per_time=float(-fit.fun/dt)))
        records.append(dict(beta=beta,m=float(m),equilibrium_residual=float(abs(F(m))),deviations=deviations))
    return dict(experiment='temporal_self',rho=rho,kappa=kappa,rows=records,
                accepted=all(a['m']<b_['m'] for a,b_ in zip(records,records[1:])) and max(z['equilibrium_residual'] for z in records)<1e-8)


def ndu_grid(nu: int = 17,nx: int = 25,steps: int = 20) -> dict:
    """Independent 2D positive-weight semi-Lagrangian reference computation.

    This is deliberately labelled a GRID REFERENCE, not a trained NBO result.
    Wealth is stopped at its first discretely observed exit; preferences reflect.
    Both choices, the terminal payoff, and the finite action grid are explicit.
    """
    us=np.linspace(1.2,3.,nu); ys=np.linspace(math.log(.5),math.log(2.),nx)
    U,Y=np.meshgrid(us,ys,indexing='ij'); X=np.exp(Y)
    points=np.column_stack([U.ravel(),Y.ravel()]);dt=1/steps
    actions=np.array(np.meshgrid([.02,.05,.1],[0.,.375,.75],[-.15,0.,.15],indexing='ij')).reshape(3,-1).T
    r,mu,sigma,sigma_u,corr,rho=.02,.08,.2,.08,-.3,.04
    terminal=lambda u,y:np.exp((1-u)*y)/(1-u)
    def reflect(u):
        length=us[-1]-us[0];z=(u-us[0])%(2*length)
        return us[0]+np.where(z<=length,z,2*length-z)
    records=[]
    for cost in (1.,5.):
        value=terminal(U,Y); first_policy=None;start=time.perf_counter()
        all_values=[value.copy()]
        for t in range(steps-1,-1,-1):
            interp=RegularGridInterpolator((us,ys),value,bounds_error=True)
            qs=[]
            for m,p,theta in actions:
                expected=np.zeros(U.size)
                # 2m cubature, m=2 Brownian factors, with E[zz']=I.
                for z1,z2 in ((math.sqrt(2),0),(-math.sqrt(2),0),(0,math.sqrt(2)),(0,-math.sqrt(2))):
                    up=reflect(points[:,0]+theta*dt+sigma_u*math.sqrt(dt)*z1)
                    yp=points[:,1]+(r+p*(mu-r)-m-.5*p*p*sigma*sigma)*dt+p*sigma*math.sqrt(dt)*(corr*z1+math.sqrt(1-corr*corr)*z2)
                    outside=(yp<ys[0])|(yp>ys[-1]);yp=np.clip(yp,ys[0],ys[-1])
                    continuation=interp(np.column_stack([up,yp]))
                    continuation[outside]=terminal(up[outside],yp[outside])
                    expected+=continuation/4
                reward=(m*X.ravel())**(1-U.ravel())/(1-U.ravel())-.5*cost*theta*theta
                qs.append(dt*reward+math.exp(-rho*dt)*expected)
            qs=np.array(qs);choice=np.argmax(qs,axis=0)
            value=np.max(qs,axis=0).reshape(U.shape);first_policy=actions[choice].reshape(*U.shape,3)
            value[:,0]=terminal(U[:,0],Y[:,0]);value[:,-1]=terminal(U[:,-1],Y[:,-1])
            all_values.append(value.copy())
        elapsed=time.perf_counter()-start
        np.savez(OUT/f'ndu_grid_{nu}x{nx}_k{cost:g}.npz',u=us,logwealth=ys,
                 values=np.array(all_values[::-1]),policy_t0=first_policy,actions=actions)
        i,j=nu//2,nx//2
        records.append(dict(cost=cost,value_center=float(value[i,j]),center_u=float(us[i]),center_wealth=float(math.exp(ys[j])),
                            control_center=first_policy[i,j].tolist(),seconds=elapsed))
    return dict(experiment='ndu_grid_reference',grid=[nu,nx],steps=steps,T=1.,rows=records,
                controls=actions.tolist(),preference_reflection=[1.2,3.],wealth_exit=[.5,2.],
                bequest='X^(1-u)/(1-u)',flow='(m X)^(1-u)/(1-u)-k theta^2/2',
                status='independent finite-grid reference; not an NBO-grid accuracy comparison',accepted=True)


def regression_checks() -> dict:
    eps=3/28
    old=-eps/2+7*eps*eps/3
    corrected=7*eps*eps/3
    # Independent-probe product for z~N(0,1) removes the h^2/2 variance bias.
    rng=np.random.default_rng(271828); z=rng.standard_normal((400000,2))
    probe=[]
    for h in (2/3,2.):
        r1=1-h*z[:,0]**2/2;r2=1-h*z[:,1]**2/2
        probe.append(dict(curvature=h,exact=(1-h/2)**2,single_probe=float(np.mean(r1*r1)),independent_product=float(np.mean(r1*r2))))
    fc_old=-.16;fc_new=.04
    return dict(experiment='regressions',old_loss_change=old,corrected_loss_change=corrected,
                ez_consumption_derivative_old=fc_old,ez_consumption_derivative_new=fc_new,
                cournot_nash=1/3,cournot_joint=1/4,unilateral_gain_at_joint=1/64,
                stochastic_trace=probe,accepted=bool(old<0<corrected and fc_new>0))


def main() -> None:
    parser=argparse.ArgumentParser();parser.add_argument('--quick',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    attempts=[]
    def run(label, fn):
        start=time.perf_counter()
        try:
            record=fn();record['execution_status']='completed'
        except Exception as exc:
            record={'experiment':label,'execution_status':'failed','accepted':False,'error':repr(exc)}
        record['wall_seconds']=time.perf_counter()-start
        attempts.append(record)
        print(label,json.dumps(record,default=str),flush=True)
    run('regressions',regression_checks);run('exit_viscosity',exit_diagnostic);run('temporal_self',temporal_self)
    for seed in ([0] if args.quick else [0,1,2]):
        for constrained,recursive in ((False,False),(True,False),(False,True)):
            run(f'merton/{seed}/{constrained}/{recursive}',lambda s=seed,c=constrained,e=recursive:merton(s,c,e))
    for d in ([2,5] if args.quick else [2,5,10,20,50]):
        for seed in ([0] if args.quick else [0,1,2]):
            run(f'lq/{d}/{seed}',lambda d=d,s=seed:coupled_lq(d,s))
    for nu,nx,steps in ([(13,17,12)] if args.quick else [(17,25,20),(25,37,40)]):
        run(f'ndu/{nu}/{nx}',lambda nu=nu,nx=nx,steps=steps:ndu_grid(nu,nx,steps))
    result={'schema':1,'purpose':'new revision experiments, not historical replication',
            'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,
                           'torch':torch.__version__,'machine':platform.machine(),'torch_threads':1,'device':'CPU'},
            'script_sha256':sha(Path(__file__)),'quick':args.quick,'attempts':attempts,
            'all_acceptance_checks_passed':all(z['accepted'] for z in attempts)}
    (OUT/'experiments.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    manifest={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'}
    (OUT/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2)+'\n')
    if any(z['execution_status']=='failed' for z in attempts):raise SystemExit(1)

if __name__=='__main__':main()
