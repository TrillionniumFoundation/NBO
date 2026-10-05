"""R23 prospective all-state policy experiment; no reference-policy labels.

A square-activation critic is trained against its OWN policy evaluation.
Population derivative regression is available analytically in this stress test.
It is not a simulation-efficiency or neural-necessity experiment. The strongest
structure-exploiting Riccati procedure is a separately timed competitor and is
never an argument of the common a posteriori verifier.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, resource, time
from pathlib import Path
import numpy as np
from policy_certificate import certify, up, down, gamma, positive_sum

HERE=Path(__file__).resolve().parents[1]
THREADS=1
os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')


def economy(d: int, regime: str, horizon: int=24) -> dict:
    if d<1 or horizon<1 or regime not in ('anchor','technology','valuation'):
        raise ValueError('invalid economy')
    I=np.eye(d); shift=np.roll(I,1,axis=1)
    A0=.92*I+.025*shift+.015*np.ones((d,d))/d
    B0=.20*I+.005*shift
    q=1+np.arange(d)/d; r=.40+.10*np.arange(d)/d
    A=np.stack([A0.copy() for _ in range(horizon)])
    B=np.stack([B0.copy() for _ in range(horizon)])
    Q=np.stack([np.diag(q/d) for _ in range(horizon)])
    R=np.stack([np.diag(r/d) for _ in range(horizon)])
    Qf=np.diag(q/d)
    if regime=='technology': A[4:]+= .02*I
    if regime=='valuation': Q[4:]*=1.25; Qf*=1.25
    Sigma=.05**2*(I+.25*np.ones((d,d))/d)
    return dict(A=A,B=B,Q=Q,R=R,Qf=Qf,Sigma=Sigma,beta=.96,
                initial_radius_sq=float(d),regime=regime,d=d,horizon=horizon)


def evaluate(model, gains):
    """Analytic evaluation of the specified linear policy, not optimization."""
    T,d=model['horizon'],model['d'];beta=model['beta']
    P=np.zeros((T+1,d,d)); c=np.zeros(T+1); P[-1]=model['Qf']
    for t in range(T-1,-1,-1):
        A,B,Q,R=(model[n][t] for n in ('A','B','Q','R'))
        K=gains[t]; F=A-B@K
        P[t]=Q+K.T@R@K+beta*F.T@P[t+1]@F
        P[t]=(P[t]+P[t].T)/2
        c[t]=beta*(c[t+1]+np.trace(P[t+1]@model['Sigma']))
    return P,c


def improve(model, coefficients):
    T,d=model['horizon'],model['d'];beta=model['beta']
    gains=np.zeros((T,d,d))
    for t in range(T):
        A,B,R=(model[n][t] for n in ('A','B','R'))
        P=coefficients[t+1]
        gains[t]=np.linalg.solve(R+beta*B.T@P@B,beta*B.T@P@A)
    return gains


def riccati(model):
    """Strong comparator only. The verifier does not call this function."""
    T,d=model['horizon'],model['d'];beta=model['beta']
    P=np.zeros((T+1,d,d));P[-1]=model['Qf'];K=np.zeros((T,d,d))
    for t in range(T-1,-1,-1):
        A,B,Q,R=(model[n][t] for n in ('A','B','Q','R'))
        K[t]=np.linalg.solve(R+beta*B.T@P[t+1]@B,beta*B.T@P[t+1]@A)
        F=A-B@K[t]
        P[t]=Q+K[t].T@R@K[t]+beta*F.T@P[t+1]@F
        P[t]=(P[t]+P[t].T)/2
    return K


def fit_square_critic(W, policy_values, d, steps):
    """Train ALL hidden weights; c_t is the exact own-policy value constant.

    For X~N(0,I), derivative risk is proportional to ||W'W-d*P^pi||_F^2.
    We use that exact population loss; no fitted value is substituted for a
    certificate. The hidden factor is not fixed or supplied by Riccati.
    """
    target=d*policy_values[:-1]
    W=W.copy()
    lr=1/(8*np.maximum(np.ones(len(target)),np.max(np.sum(np.abs(target),axis=2),axis=1)))
    for _ in range(steps):
        err=np.swapaxes(W,1,2)@W-target
        grad=W@err
        W-=lr[:,None,None]*grad
        if not np.all(np.isfinite(W)):
            raise ArithmeticError('nonfinite critic iterate')
    coefficients=np.empty_like(policy_values)
    coefficients[:-1]=(np.swapaxes(W,1,2)@W)/d
    coefficients[-1]=policy_values[-1]
    last_loss=float(np.sum((np.swapaxes(W,1,2)@W-target)**2)/4)
    return W,coefficients,last_loss


def initial_state(d,T,seed):
    rng=np.random.default_rng(seed)
    W=np.broadcast_to(np.eye(d),(T,d,d)).copy()+.02*rng.normal(size=(T,d,d))/np.sqrt(d)
    return W,np.zeros((T,d,d))


def append_record(path,record):
    with path.open('a',encoding='utf8') as f:
        f.write(json.dumps(record,sort_keys=True,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())


def run(output: Path, protocol: dict):
    output.mkdir(parents=True,exist_ok=False)
    events=output/'attempts.jsonl';results=[]
    metadata=dict(python=platform.python_version(),numpy=np.__version__,
                  platform=platform.platform(),threads=THREADS,started_ns=time.time_ns(),
                  protocol_sha256=hashlib.sha256(json.dumps(protocol,sort_keys=True).encode()).hexdigest(),
                  clocks='realized wall clocks; not confidence intervals or population expected clocks',
                  operation_counts='declared dense algebra and gradient-update counts, not hardware instruction measurements')
    (output/'environment.json').write_text(json.dumps(metadata,indent=2)+'\n')
    started=time.perf_counter()
    for d in protocol['dimensions']:
      for seed in protocol['seeds']:
       for method in protocol['methods']:
        warm_W=warm_K=None
        for regime in protocol['regimes']:
          key=f'd{d}_s{seed}_{method}_{regime}'
          tic=time.perf_counter();model=economy(d,regime,protocol['horizon'])
          if method.endswith('warm') and warm_K is not None:
            W,K=(warm_W.copy() if warm_W is not None else None),warm_K.copy()
          elif method.startswith('NBO'):
            W,K=initial_state(d,model['horizon'],seed)
          else:
            W,K=None,np.zeros((model['horizon'],d,d))
          count=0;updates=0;eval_calls=0;solve_calls=0;checks=0;last_loss=None
          stage_times=[];fitting_seconds=0.;evaluation_seconds=0.;checking_seconds=0.
          passed=False;certificate=None
          budget_list=[0] if method=='Riccati' else protocol['check_passes']
          for target_passes in budget_list:
            if method=='Riccati':
                st=time.perf_counter();K=riccati(model);solve_calls+=model['horizon'];fitting_seconds+=time.perf_counter()-st
            else:
                while count<target_passes:
                    st=time.perf_counter();P,c=evaluate(model,K);eval_calls+=1;evaluation_seconds+=time.perf_counter()-st
                    st=time.perf_counter()
                    if method.startswith('NBO'):
                        W,Pfit,last_loss=fit_square_critic(W,P,d,protocol['gradient_steps_per_pass'])
                        updates+=protocol['gradient_steps_per_pass']
                    else:
                        # Same population evaluation information; exact quadratic
                        # regression is the competitive closed-form minimizer.
                        Pfit=P
                    K=improve(model,Pfit);solve_calls+=model['horizon'];count+=1
                    fitting_seconds+=time.perf_counter()-st
            st=time.perf_counter();certificate=certify(model,K,protocol['execution_error_budget']);checking_seconds+=time.perf_counter()-st;checks+=1
            passed=certificate['policy_gap_upper']<=protocol['policy_tolerance']
            candidate_path=output/(key+f'_p{count}.npz')
            stored={'gains':K,**{n:model[n] for n in ('A','B','Q','R','Qf','Sigma')}}
            if W is not None:stored['critic_factor']=W
            elif method.startswith('quadratic'):stored['critic_coefficients']=Pfit
            np.savez_compressed(candidate_path,**stored)
            record=dict(key=key,dimension=d,seed=seed,method=method,regime=regime,
                        passes=count,gradient_updates=updates,evaluation_calls=eval_calls,
                        linear_solve_calls=solve_calls,checks=checks,certified=bool(passed),
                        elapsed_before_record_seconds=time.perf_counter()-tic,
                        evaluation_seconds=evaluation_seconds,fitting_seconds=fitting_seconds,
                        verification_seconds=checking_seconds,
                        candidate_file=candidate_path.name,
                        candidate_sha256=hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
                        stored_parameter_bytes=int(K.nbytes+(W.nbytes if W is not None else Pfit.nbytes if method.startswith('quadratic') else 0)),
                        final_population_fitting_loss=last_loss,certificate=certificate)
            append_record(events,record)
            stage_times.append(time.perf_counter()-tic)
            if passed:break
          warm_W,warm_K=(W.copy() if W is not None else None),K.copy()
          # Counterfactual is the first-period action from a FULL reoptimized policy.
          u0=K[0]@np.ones(d)
          rmin=float(np.min(np.diag(model['R'][0])))
          center=float(np.sum(K[0])/d)
          center_error=float(up(up(gamma(d*d+2)*positive_sum(np.abs(K[0])))/d))
          action_radius=float(up(np.sqrt(float(up(certificate['policy_gap_upper']/float(down(rmin*d)))))))
          radius=float(up(up(action_radius+protocol['execution_error_budget'])+center_error))
          result=dict(key=key,dimension=d,seed=seed,method=method,regime=regime,
                      certified=bool(passed),passes=count,gradient_updates=updates,
                      evaluation_calls=eval_calls,linear_solve_calls=solve_calls,checks=checks,
                      failed_checks=checks-int(passed),complete_service_seconds=time.perf_counter()-tic,
                      clock_includes='initialization, all fits/updates/checks, compressed candidate writes and fsynced attempt records; final summary write is job overhead',
                      evaluation_seconds=evaluation_seconds,fitting_seconds=fitting_seconds,
                      verification_seconds=checking_seconds,policy_gap_upper=certificate['policy_gap_upper'],
                      ideal_gap_upper=certificate['ideal_gap_upper'],implementation_gap_upper=certificate['implementation_gap_upper'],
                      initial_mean_investment=center,initial_mean_investment_radius=radius,
                      final_candidate_file=candidate_path.name,final_candidate_sha256=record['candidate_sha256'])
          results.append(result);append_record(output/'services.jsonl',result)
          print(key,passed,f"gap={certificate['policy_gap_upper']:.6g}",f"seconds={result['complete_service_seconds']:.3f}",flush=True)
    summary={'services':len(results),'certified':sum(r['certified'] for r in results),'total_attempts':sum(r['checks'] for r in results),
             'failed_checks':sum(r['failed_checks'] for r in results),'runtime_seconds_before_final_summary':time.perf_counter()-started,
             'process_high_water_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
             'rss_scope':'whole experiment process, not per-method peak memory','cells':[],'method_randomizer':protocol['randomizer']}
    for d in protocol['dimensions']:
      for method in protocol['methods']:
       for regime in protocol['regimes']:
        rows=[r for r in results if (r['dimension'],r['method'],r['regime'])==(d,method,regime)]
        cell={'dimension':d,'method':method,'regime':regime,'n':len(rows),'success_probability':sum(r['certified'] for r in rows)/len(rows)}
        for field in ['complete_service_seconds','gradient_updates','evaluation_calls','linear_solve_calls','checks','failed_checks','policy_gap_upper','implementation_gap_upper']:
            vals=[r[field] for r in rows];cell['mean_'+field]=float(np.mean(vals));cell['max_'+field]=float(max(vals))
        summary['cells'].append(cell)
    (output/'SUMMARY.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--protocol',type=Path,default=HERE/'protocols/PROTOCOL.json');args=p.parse_args()
    run(args.output,json.loads(args.protocol.read_text()))
