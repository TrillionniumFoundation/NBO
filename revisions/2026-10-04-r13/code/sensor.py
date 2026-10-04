"""Finite noisy sensing: a weight-dependent deterministic transfer allowance.
Euler simulations below are implementation diagnostics, not proofs or uniform
performance certificates. The allowance is computed separately with the inherited
conditional outward-arithmetic kernel.
"""
from __future__ import annotations
import hashlib,math,time
from common import *
from tube_certificate import spectral_bound,sqrt_i,sum_i

def allowance(path,cells,noise_rms,initial_spread=.5):
    actor,_,st=old.load(Path(path));d=st['dimension'];eps=st['epsilon'];I=pc.I
    if cells<1 or noise_rms<0 or initial_spread<0:raise ValueError('invalid sensor parameters')
    matrices=[p.detach().numpy() for p in actor.parameters() if p.ndim==2]
    lip=I(eps)
    for matrix in matrices:lip=lip*sqrt_i(sum_i(I(matrix).square()))
    L=I(float(lip.hi));sp=spectral_bound(old.coupling(d));beta=I(P['coupling'])*I(sp['norm_upper']);T=I(P['T']);h=T/cells
    wt=pc.weights(cells);mlo=I(float(pc.down(np.min(wt['center'].lo)-eps)));mhi=I(float(pc.up(np.max(wt['center'].hi)+eps)))
    if mlo.lo<=0:raise ValueError('nonpositive consumption lower bound')
    c=I(P['productivity'])-(I(P['idiosyncratic_sigma']).square()+I(P['common_sigma']).square())/2
    cabs=I(float(c.absmax()));drift=cabs+I(P['coupling'])+mhi
    sigma=sqrt_i(I(P['idiosyncratic_sigma']).square()+I(P['common_sigma']).square())
    op=sqrt_i(I(P['idiosyncratic_sigma']).square()+d*I(P['common_sigma']).square())
    pi=I(math.pi-1e-15,math.pi+1e-15)
    tail_second=2*(I(10.)+I(.1))*pc.exp_i(I(-50.))/sqrt_i(2*pi)
    clipping=sqrt_i(h)*op*sqrt_i(I((d+1)/d)*tail_second)
    local=beta*(drift*h.square()/2+I(2.)/3*sigma*h*sqrt_i(h))+clipping
    e=I(0.);nu=I(noise_rms)
    for _ in range(cells):e=(1+h*(beta+L))*e+L*nu*h+local
    action=L*(e+nu);physical=T*pc.exp_i(beta*T)*action
    Q=I(initial_spread)+(I(P['coupling'])+I(eps))*T+I(P['idiosyncratic_sigma'])*sqrt_i((1-I(1.)/d)*T)
    reward_lip=1/mlo+I(P['adjustment'])*mhi
    loss=T*(physical+reward_lip*action)+(1+2*I(CHI)*Q)*physical
    return dict(record_type='sensor_allowance',source_commit=source(),dimension=d,cells=cells,noise_rms=noise_rms,
        initial_spread_upper=initial_spread,actor_lipschitz_upper=float(L.hi),drift_lipschitz_upper=float(beta.hi),
        node_error_upper=float(e.hi),action_error_upper=float(action.hi),physical_error_upper=float(physical.hi),payoff_difference_upper=float(loss.hi),
        weights_sha256=digest(path),spectral_matrix_sha256=sp['matrix_sha256'],
        scope='Two sampled controllers at the same cell count: finite state observations with L2 sensor error versus the clipped-innovation controller. Original physical diffusion in both cases. Conditional arithmetic; no claim that this allowance is small enough to sign improvement.')

def audit(path,out):
    path=Path(path);out=Path(out);actor,_,st=old.load(path);d=st['dimension'];eps=st['epsilon'];B=old.coupling(d)
    paths=PROTOCOL['observation_paths'];fine=PROTOCOL['observation_fine_cells'];dt=P['T']/fine
    seed=PROTOCOL['fixed_work_noise_seed']+919+d;rng=np.random.default_rng(seed)
    noise=rng.standard_normal((fine,paths,d+1));noisehash=hashlib.sha256(noise.tobytes()).hexdigest()
    support=profiles(d);ids=rng.integers(len(support),size=paths);initial=support[ids].copy();rows=[];raw={'initial_indices':ids}
    c=P['productivity']-(P['idiosyncratic_sigma']**2+P['common_sigma']**2)/2
    def prod(y):return P['coupling']*np.tanh(y@B.T)
    def flow(y,m):return (np.log(m)+y).mean(1)-P['adjustment']/2*m.mean(1)**2
    def terminal(y):return y.mean(1)-CHI*((y-y.mean(1,keepdims=True))**2).mean(1)
    for cells in PROTOCOL['observation_cells']:
        if fine%cells:raise ValueError('sensor diagnostic grids must be nested')
        ratio=fine//cells;h=P['T']/cells;wt=pc.weights(cells);lo=pc.up(wt['center'].hi-eps);hi=pc.down(wt['center'].lo+eps)
        coarse=noise.reshape(cells,ratio,paths,d+1).sum(1)/math.sqrt(ratio)
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
            rows.append(dict(id=key,dimension=d,cells=cells,sensor_noise_rms=nu,mean_sensor_minus_ideal=float(delta.mean()),
                mc_standard_error=float(delta.std(ddof=1)/math.sqrt(paths)),fine_euler_cells=fine,paths=paths,seconds=time.perf_counter()-start,allowance=bound))
    rp=out/f'{path.stem}_sensor.npz';np.savez_compressed(rp,**raw)
    result=dict(record_type='sensor',source_commit=source(),weights=str(path.relative_to(ROOT)),weights_sha256=digest(path),
        raw_sha256=digest(rp),raw_file=str(rp.relative_to(ROOT)),noise_seed=seed,noise_sha256=noisehash,rows=rows,
        interpretation='Shared-noise fine-Euler implementation check, not a continuous-time confidence interval. The theorem allowance is a separate global bound; no missing bias is set to zero.')
    write(rp.with_suffix('.json'),result);return result
