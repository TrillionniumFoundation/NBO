"""All-state certificates for recursive entropic Gaussian capital costs.

The verifier evaluates only the returned policy. It never calls the structural
optimal-control comparator, and does not identify a small fitting loss with a
policy certificate. Scalar bounds and matrix operations are outward rounded.
The declared execution allowance is a mathematical action-error contract.
"""
from pathlib import Path
import math
import sys
import numpy as np
from policy_certificate import Ball, up, down, positive_sum
from constructive import train_factor


def add(*args):
    ans = 0.
    for x in args:
        if x < 0: raise ValueError('Nonnegative upper summands required')
        ans = float(up(ans+x))
    return ans


def mul(*args):
    ans = 1.
    for x in args:
        if x < 0: raise ValueError('Nonnegative upper factors required')
        ans = float(up(ans*x))
    return ans


def div(a, b):
    if a < 0 or b <= 0: raise ValueError('Invalid positive division')
    return float(up(a/float(down(b))))


def norm2(x: Ball) -> float:
    return min(x.norm_f(), float(up(math.sqrt(mul(x.norm_inf(), x.T.norm_inf())))))


def inverse(x: Ball) -> Ball:
    """Verified inverse via a proposed solve and its Neumann residual."""
    d = len(x.c)
    proposal = np.linalg.solve(x.c, np.eye(d))
    cb = Ball.exact(proposal)
    residual = (Ball.exact(np.eye(d))-x@cb).norm_inf()
    if not residual < 1:
        raise ArithmeticError('Inverse residual does not certify invertibility')
    error = div(mul(cb.norm_inf(), residual), float(down(1-residual)))
    return Ball(proposal, np.full_like(proposal, error))


def margin(theta: float, sigma: float, p: float) -> float:
    if theta == 0: return 1.
    ans = float(down(1-mul(2., theta, sigma, p)))
    if ans <= 0: raise ArithmeticError('Gaussian exponential-moment domain not certified')
    return ans


def transform(p: Ball, covariance: np.ndarray, theta: float) -> Ball:
    if not math.isfinite(theta) or theta < 0:
        raise ValueError('Nonnegative finite risk sensitivity required')
    if theta == 0: return p
    sb = Ball.exact(covariance)
    margin(theta, norm2(sb), p.norm_inf())
    out = p @ inverse(Ball.exact(np.eye(len(p.c))) - (sb@p).scale(2*theta))
    # The exact transform is symmetric; average both enclosing expressions.
    return (out+out.T).scale(.5)


def validate(model: dict, gains: np.ndarray, theta: float):
    if not math.isfinite(theta) or theta < 0: raise ValueError('Invalid risk parameter')
    T, d = model['A'].shape[:2]
    if T < 1 or d < 1 or gains.shape != (T,d,d): raise ValueError('Invalid dimensions')
    if not 0 < model['beta'] <= 1: raise ValueError('Invalid discount')
    if not math.isfinite(model['initial_radius_sq']) or model['initial_radius_sq'] < 0:
        raise ValueError('Invalid initial-state radius')
    for name in ('A','B','Q','R'):
        x = np.asarray(model[name])
        if x.shape != (T,d,d) or not np.isfinite(x).all(): raise ValueError('Invalid primitive '+name)
    for name in ('Q','R'):
        for x in model[name]:
            if not np.array_equal(x,np.diag(np.diag(x))) or np.min(np.diag(x)) <= 0:
                raise ValueError('Positive diagonal stage costs required by this implementation')
    qf = model['Qf']; sigma = model['Sigma']
    if qf.shape != (d,d) or not np.isfinite(qf).all() or not np.array_equal(qf,np.diag(np.diag(qf))) or np.min(np.diag(qf)) < 0:
        raise ValueError('Nonnegative diagonal terminal cost required')
    if sigma.shape != (d,d) or not np.isfinite(sigma).all() or not np.array_equal(sigma,sigma.T):
        raise ValueError('Symmetric finite covariance required')
    # A sufficient, openly stated PSD check; other covariances need another proof.
    for i in range(d):
        offdiag = np.abs(sigma[i]).copy(); offdiag[i] = 0.
        radius = float(positive_sum(offdiag))
        if sigma[i,i] < 0 or float(down(sigma[i,i])) < float(up(radius)):
            raise ValueError('Covariance diagonal-dominance certificate failed')
    if not np.isfinite(gains).all(): raise ValueError('Nonfinite policy')


def certify(model: dict, gains: np.ndarray, theta: float, execution_error: float = 1e-12) -> dict:
    validate(model, gains, theta)
    if not math.isfinite(execution_error) or execution_error < 0:
        raise ValueError('Invalid execution-error contract')
    T,d = gains.shape[:2]; beta = float(model['beta'])
    sigma = norm2(Ball.exact(model['Sigma']))
    trace = Ball.exact(model['Sigma']).trace().upper()
    values = [None]*(T+1); values[T] = Ball.exact(model['Qf'])
    diagnostics = [None]*T
    for t in range(T-1,-1,-1):
        a,b,q,r = [Ball.exact(model[n][t]) for n in ('A','B','Q','R')]
        k = Ball.exact(gains[t]); f = a-b@k
        psi = transform(values[t+1],model['Sigma'],theta)
        h = r+(b.T@psi@b).scale(beta)
        defect = h@k-(b.T@psi@a).scale(beta)
        values[t] = q+k.T@r@k+(f.T@psi@f).scale(beta)
        diagnostics[t] = dict(d=defect.norm_f(), f=norm2(f), b=norm2(b),
                              k=norm2(k), r=float(np.min(np.diag(model['R'][t]))),
                              rnorm=norm2(r), p=values[t+1].norm_inf())
    delta = kappa = delta_e = kappa_e = 0.
    records = []
    for t in range(T-1,-1,-1):
        rec=diagnostics[t]; p=rec['p']; f=rec['f']; b=rec['b']; r=rec['r']; dn=rec['d']
        if t+1 < T and delta > float(np.min(np.diag(model['Q'][t+1]))):
            raise ArithmeticError('Lower quadratic envelope lost positive semidefiniteness')
        gamma = margin(theta,sigma,p)
        drift = div(delta,float(down(gamma*gamma)))
        # The lower-envelope minimizing transition is bounded relative to the
        # stored policy, avoiding a needlessly expansive primitive-only norm.
        lower_f = add(f,mul(div(b,r),add(dn,mul(beta,b,f,drift))))
        new_delta = add(div(mul(dn,dn),r),mul(beta,lower_f,lower_f,drift))
        new_kappa = mul(beta,add(kappa,div(mul(delta,trace),gamma)))
        gamma_e = margin(theta,sigma,add(p,delta_e))
        psi_upper = div(add(p,delta_e),gamma_e)
        act = add(mul(2.,execution_error,rec['k'],rec['rnorm']),
                  mul(execution_error,execution_error,rec['rnorm']),
                  mul(beta,psi_upper,add(mul(2.,execution_error,f,b),
                                        mul(execution_error,execution_error,b,b))))
        new_delta_e = add(mul(beta,f,f,div(delta_e,float(down(gamma_e*gamma_e)))),act)
        new_kappa_e = mul(beta,add(kappa_e,div(mul(delta_e,trace),gamma_e)))
        delta,kappa,delta_e,kappa_e = new_delta,new_kappa,new_delta_e,new_kappa_e
        records.append(dict(date=t,domain_margin=gamma,implementation_domain_margin=gamma_e,
                            coefficient_allowance=delta,constant_allowance=kappa,
                            implementation_coefficient=delta_e,implementation_constant=kappa_e,
                            own_policy_defect_upper=dn))
    nominal=add(mul(delta,model['initial_radius_sq']),kappa)
    implementation=add(mul(delta_e,model['initial_radius_sq']),kappa_e)
    return dict(policy_gap_upper=add(nominal,implementation),nominal_policy_gap_upper=nominal,
                implementation_gap_upper=implementation,minimum_domain_margin=min(x['domain_margin'] for x in records),
                minimum_implementation_domain_margin=min(x['implementation_domain_margin'] for x in records),
                class_approximation_allowance=0.,value_transfer_allowance=0.,
                coverage='All real states and vector actions, and all adapted finite-cost comparison policies in the declared recursive model',
                dates=records)


def nominal_transform(p, covariance, theta):
    if theta == 0: return p.copy()
    out=np.linalg.solve(np.eye(len(p))-2*theta*p@covariance,p)
    return (out+out.T)/2


def candidate(model: dict, theta: float, method: str, gram_tolerance: float = 1e-7) -> tuple:
    """Analytic own-policy targets; structural comparison receives identical information."""
    if method not in ('NBO','structural'): raise ValueError('Unknown candidate generator')
    T,d=model['A'].shape[:2];beta=model['beta']
    K=np.zeros((T,d,d));P=np.empty((T+1,d,d));P[-1]=model['Qf']
    W=np.zeros_like(K);records=[]
    for t in range(T-1,-1,-1):
        psi=nominal_transform(P[t+1],model['Sigma'],theta)
        phat=psi
        if method=='NBO' and t<T-1:
            m=d*float(np.min(np.diag(model['Q'][t+1])))
            W[t+1],record=train_factor(d*psi,m,gram_tolerance,multiplier=.5,seed=27+t)
            record['date']=t;records.append(record)
            phat=W[t+1].T@W[t+1]/d
        A,B,Q,R=(model[n][t] for n in ('A','B','Q','R'))
        K[t]=np.linalg.solve(R+beta*B.T@phat@B,beta*B.T@phat@A)
        F=A-B@K[t]
        # Evaluation uses the finalized policy future, never a fitted value.
        P[t]=Q+K[t].T@R@K[t]+beta*F.T@psi@F
        P[t]=(P[t]+P[t].T)/2
    return K,W,dict(hidden_updates=sum(r['iterations'] for r in records),
                    ideal_hidden_update_cap=sum(r['ideal_iteration_cap'] for r in records),
                    gram_checks=sum(r['gram_checks'] for r in records),
                    all_training_thresholds_met=all(r['training_threshold_met'] for r in records),
                    actor_solves=T,own_policy_matrix_updates=T,entropic_transforms=T,
                    simulation_transitions=0,dates=records)
