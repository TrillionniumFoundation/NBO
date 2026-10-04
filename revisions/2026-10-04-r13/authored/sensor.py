"""Finite noisy sensing with explicit network-roundoff and state-transfer accounts.
The physical state is never clipped. The protected actor uses the inherited
polynomial tanh kernel, not an assumed exact platform activation. Fine-Euler
comparisons are diagnostics; deterministic allowances are separate objects.
"""
from __future__ import annotations
import functools,hashlib,math,time
from common import *
from tube_certificate import spectral_bound,sqrt_i,sum_i

@functools.lru_cache(maxsize=4096)
def center(t):
    t=float(t)
    if not 0<=t<=P['T']:raise ValueError('clock outside horizon')
    return float(pc.midpoint(pc.schedule_i(pc.I(t))))

class ProtectedActor(torch.nn.Module):
    def __init__(self,actor,epsilon):
        super().__init__();self.epsilon=float(epsilon)
        self.layers=[(m.weight.detach().numpy().copy(),m.bias.detach().numpy().copy()) for m in actor.modules() if isinstance(m,torch.nn.Linear)]
        if not self.layers:raise ValueError('no affine layers')
    def forward(self,x):
        a=x.detach().cpu().numpy();t=a[:,0];h=np.c_[t,np.clip(a[:,1:],-100.,100.)]
        for w,b in self.layers:h=pc.safe_tanh(h@w.T+b)
        clocks=np.array([center(v) for v in t])[:,None]
        out=clocks+self.epsilon*h
        return torch.from_numpy(out)

def protected_load(path):
    actor,critic,st=old.load(Path(path));st=dict(st,policy_implementation='protected polynomial-tanh actor with exact saved weights')
    return ProtectedActor(actor,st['epsilon']),critic,st

def network_account(actor,d,epsilon):
    I=pc.I;layers=[m for m in actor.modules() if isinstance(m,torch.nn.Linear)];errors=I(np.zeros(d+1));bounds=I(np.r_[1.,np.full(d,100.)]);lip=I(epsilon)
    for layer in layers:
        W=layer.weight.detach().numpy();b=layer.bias.detach().numpy();aw=I(abs(W));ab=I(abs(b))
        sums=pc.sum_axis(aw*bounds,axis=1)+ab
        propagated=pc.sum_axis(aw*errors,axis=1)
        rounding=I(pc.gamma(W.shape[1]+2))*sums
        errors=propagated+rounding+I(2.**-34)
        bounds=I(np.full(W.shape[0],float(pc.up(1.+2.**-34))))
        frob=sqrt_i(sum_i(I(W).square()))
        one=float(np.max(pc.sum_axis(aw,axis=0).hi));infinity=float(np.max(pc.sum_axis(aw,axis=1).hi))
        induced=sqrt_i(I(one)*I(infinity));lip=lip*I(min(float(frob.hi),float(induced.hi)))
    errors=I(epsilon)*errors+I(pc.gamma(4))*(I(P['upper'])+I(epsilon)*bounds)
    kappa=sqrt_i(pc.mean_i(errors.square()))
    return dict(lipschitz_upper=float(lip.hi),actor_roundoff_rms_upper=float(kappa.hi),
        interpretation='Ideal real tanh network with saved binary64 coefficients and clipped network input; implemented polynomial tanh differs uniformly by the stated amount before the common nonexpansive inward action projection.')

def allowance(path,cells,noise_rms,initial_spread=.5,initial_max_abs=2.):
    actor,_,st=old.load(Path(path));d=st['dimension'];eps=st['epsilon'];I=pc.I
    if cells<2 or noise_rms<0 or initial_spread<0:raise ValueError('invalid sensor parameters')
    net=network_account(actor,d,eps);L=I(net['lipschitz_upper']);kappa=I(net['actor_roundoff_rms_upper'])
    B=old.coupling(d);sp=spectral_bound(B);beta=I(P['coupling'])*I(sp['norm_upper']);T=I(P['T']);h=T/cells
    wt=pc.weights(cells);mlo=I(float(pc.down(np.min(wt['center'].lo)-eps)));mhi=I(float(pc.up(np.max(wt['center'].hi)+eps)))
    if mlo.lo<=P['lower'] or mhi.hi>=P['upper']:raise ValueError('invalid action enclosure')
    c=I(P['productivity'])-(I(P['idiosyncratic_sigma']).square()+I(P['common_sigma']).square())/2
    cabs=I(float(c.absmax()));speed=cabs+I(P['coupling'])+mhi
    sigma=sqrt_i(I(P['idiosyncratic_sigma']).square()+I(P['common_sigma']).square())
    op=sqrt_i(I(P['idiosyncratic_sigma']).square()+d*I(P['common_sigma']).square())
    pi=I(math.pi-1e-15,math.pi+1e-15)
    tail_second=2*(I(10.)+I(1.)/10)*pc.exp_i(I(-50.))/sqrt_i(2*pi)
    clipping=sqrt_i(h)*op*sqrt_i((I(d+1)/d)*tail_second)
    statecap=2*(I(initial_max_abs)+speed*T+(I(P['idiosyncratic_sigma'])+I(P['common_sigma']))*10*T/sqrt_i(h)+1)
    rownorm=I(float(np.max(pc.sum_axis(I(abs(B)),axis=1).hi)))
    doterr=I(pc.gamma(d+2))*statecap*rownorm
    ferr=I(P['coupling'])*(I(2.**-34)+doterr)+I(pc.gamma(8))*speed
    noisecap=(I(P['idiosyncratic_sigma'])+I(P['common_sigma']))*10*sqrt_i(h)
    recurrence_round=h*ferr+I(pc.gamma(20))*(statecap+h*speed+noisecap)+I(16*np.finfo(float).eps)*noisecap
    local=beta*(speed*h.square()/2+(I(2.)/3)*sigma*h*sqrt_i(h))+clipping+recurrence_round
    e=I(0.);nu=I(noise_rms);cap=I(2.)*I(eps);action=I(0.)
    for _ in range(cells):
        a=L*(e+nu)+2*kappa
        action=I(0.,min(float(cap.hi),float(a.hi)))
        e=(1+h*beta)*e+h*action+local
    action=I(0.,min(float(cap.hi),float((L*(e+nu)+2*kappa).hi)))
    physical=T*pc.exp_i(beta*T)*action
    Q=I(initial_spread)+(I(P['coupling'])+I(eps))*T+I(P['idiosyncratic_sigma'])*sqrt_i((1-I(1.)/d)*T)
    reward_lip=1/mlo+I(P['adjustment'])*mhi
    loss=T*(physical+reward_lip*action)+(1+2*I(CHI)*Q)*physical
    return dict(record_type='sensor_allowance',source_commit=source(),dimension=d,cells=cells,noise_rms=noise_rms,
        initial_spread_upper=initial_spread,initial_max_abs_upper=initial_max_abs,network=net,drift_lipschitz_upper=float(beta.hi),
        internal_state_cap=float(statecap.hi),recurrence_roundoff_per_cell_upper=float(recurrence_round.hi),clipped_noise_per_cell_upper=float(clipping.hi),
        node_error_upper=float(e.hi),action_error_upper=float(action.hi),physical_error_upper=float(physical.hi),payoff_difference_upper=float(loss.hi),
        weights_sha256=digest(path),spectral_matrix_sha256=sp['matrix_sha256'],
        scope='Original physical diffusion; finite observations with causal L2 sensor error versus the protected clipped-innovation controller at the SAME cell count. Network input is clipped, economic state is not. Conditional binary64/sampling account; no claim that the allowance signs improvement.')

def audit(path,out):
    import evaluation
    path=Path(path);out=Path(out);actor,_,st=protected_load(path);d=st['dimension'];eps=st['epsilon'];B=old.coupling(d)
    paths=PROTOCOL['observation_paths'];fine=PROTOCOL['observation_fine_cells'];dt=P['T']/fine
    seed=PROTOCOL['fixed_work_noise_seed']+919+d;rng=np.random.default_rng(seed)
    noise=rng.standard_normal((fine,paths,d+1));noisehash=hashlib.sha256(noise.tobytes()).hexdigest()
    support=profiles(d);ids=rng.integers(len(support),size=paths);initial=support[ids].copy();rows=[];raw={'initial_indices':ids}
    c=P['productivity']-(P['idiosyncratic_sigma']**2+P['common_sigma']**2)/2
    def prod(y):return P['coupling']*pc.safe_tanh(y@B.T)
    def flow(y,m):return (pc.safe_log(m)+y).mean(1)-P['adjustment']/2*m.mean(1)**2
    def terminal(y):return y.mean(1)-CHI*((y-y.mean(1,keepdims=True))**2).mean(1)
    for cells in PROTOCOL['observation_cells']:
        if fine%cells:raise ValueError('sensor diagnostic grids must be nested')
        ratio=fine//cells;h=P['T']/cells;wt=pc.weights(cells);lo=pc.up(wt['center'].hi-eps);hi=pc.down(wt['center'].lo+eps)
        coarse=noise.reshape(cells,ratio,paths,d+1).sum(1)/math.sqrt(ratio)
        alias=out/f'{path.stem}_protected_n{cells}.pt';alias.write_bytes(path.read_bytes())
        parent=evaluation.evaluate(alias,out,design='population',steps=cells,paths=PROTOCOL['final_paths'],test_seed=PROTOCOL['fixed_work_noise_seed']+777000,policy_loader=protected_load)
        for nu in PROTOCOL['observation_noise_rms']:
            start=time.perf_counter();z=initial.copy();ideal=initial.copy();sensor=initial.copy();ri=np.zeros(paths);rs=np.zeros(paths)
            erng=np.random.default_rng(seed+100000+cells)
            for k in range(cells):
                t=k*h;obs=sensor+nu*erng.standard_normal(sensor.shape)
                with torch.no_grad():
                    ai=actor(torch.tensor(np.c_[np.full(paths,t),z])).numpy();ass=actor(torch.tensor(np.c_[np.full(paths,t),obs])).numpy()
                ai=np.maximum(lo[k],np.minimum(hi[k],ai));ass=np.maximum(lo[k],np.minimum(hi[k],ass))
                for j in range(ratio):
                    n=k*ratio+j;discount=math.exp(-P['discount']*n*dt)
                    ri+=discount*dt*flow(ideal,ai);rs+=discount*dt*flow(sensor,ass)
                    dw=math.sqrt(dt)*(P['idiosyncratic_sigma']*noise[n,:,:d]+P['common_sigma']*noise[n,:,d:])
                    ideal+=dt*(c+prod(ideal)-ai)+dw;sensor+=dt*(c+prod(sensor)-ass)+dw
                zz=np.clip(coarse[k],-10.,10.);dw=math.sqrt(h)*(P['idiosyncratic_sigma']*zz[:,:d]+P['common_sigma']*zz[:,d:])
                z+=h*(c+prod(z)-ai)+dw
            delta=rs-ri+math.exp(-P['discount']*P['T'])*(terminal(sensor)-terminal(ideal))
            key=f'n{cells}_noise{nu:g}';raw[key]=delta;bound=allowance(path,cells,nu)
            lower=float((pc.I(parent['bound']['lower'])-pc.I(bound['payoff_difference_upper'])).lo)
            upper=float((pc.I(parent['bound']['upper'])+pc.I(bound['payoff_difference_upper'])).hi)
            rows.append(dict(id=key,dimension=d,cells=cells,sensor_noise_rms=nu,mean_sensor_minus_ideal=float(delta.mean()),
                mc_standard_error=float(delta.std(ddof=1)/math.sqrt(paths)),fine_euler_cells=fine,paths=paths,seconds=time.perf_counter()-start,allowance=bound,
                protected_parent=str((out/(parent['id']+'.json')).relative_to(ROOT)),transferred_improvement_lower=lower,transferred_improvement_upper=upper))
    rp=out/f'{path.stem}_sensor.npz';np.savez_compressed(rp,**raw)
    result=dict(record_type='sensor',source_commit=source(),weights=str(path.relative_to(ROOT)),weights_sha256=digest(path),
        raw_sha256=digest(rp),raw_file=str(rp.relative_to(ROOT)),noise_seed=seed,noise_sha256=noisehash,rows=rows,
        interpretation='Shared-noise fine-Euler implementation diagnostic, not a bias-free estimate. The original-diffusion payoff allowance and the separately verified protected parent at the same cell count determine the transferred endpoints. No unknown bias is replaced by zero.')
    write(rp.with_suffix('.json'),result);return result
