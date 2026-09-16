#!/usr/bin/env python3
"""Second-order, endpoint-residual-corrected certificates for changing kernels.
No convexity of the optimal value in the transition mixture is assumed.
A fixed-policy Bernstein bank supplies feasible lower values. All bounds are
all-state, all-date, closed-interval bounds for the declared finite model.
"""
from common import *
from transport import Mixture,restrict,bernstein_value,envelope_certificate
import contracts as c

def continuation(mix,k,n,v):
    e=mix.e[k];out=e.common.continuation(v)
    if e.extra:out=np.concatenate([out,e.extra[n].continuation(v)],axis=1)
    return out

def corrected_chord(mix,a,b,va,vb):
    """Statewise correction M_n=max_a[D_n+max(K_a M_next,K_b M_next)]_+.
    U_n(t)=(1-t)V_a+t V_b+t(1-t)M_n is a supersolution.
    """
    upper=[None]*(mix.steps+1);upper[-1]=mix.terminal[None,:]
    m=np.zeros(mix.ns);maxima=[]
    for n in range(mix.steps-1,-1,-1):
        diff=vb[n+1]-va[n+1]
        D=(b-a)*(continuation(mix,0,n,diff)-continuation(mix,1,n,diff))
        k0=continuation(mix,0,n,m);k1=continuation(mix,1,n,m)
        ka=(1-a)*k0+a*k1;kb=(1-b)*k0+b*k1
        m=np.maximum(0.,(D+np.maximum(ka,kb)).max(1));h=mix.steps-n
        j=np.arange(h+1)[:,None];u=(1-j/h)*va[n]+j/h*vb[n]
        if h>=2:u=u+j*(h-j)/(h*(h-1))*m
        else:assert abs(m).max()<1e-10
        upper[n]=u;maxima.append(float(m.max()))
    return upper,maxima[::-1]

def run(epsilon=1e-3):
    start=time.perf_counter();e0=c.Economy(correlation=-.25);e1=c.Economy(correlation=.25);mix=Mixture(e0,e1)
    result=dict(states=e0.ns,dates=e0.steps,actions=len(e0.menu)+3,epsilon=epsilon,
        backend_checks=mix.backend_checks,kernel_build_seconds=time.perf_counter()-start,source_sha256=sha(__file__),rows=[])
    for d in (0.,.5,1.):
        start=time.perf_counter();cache={};history=[];interval_cache={}
        def solve(t):
            if t not in cache:
                z=mix.solve(t,d);z['coeff']=mix.policy_coefficients(z['policy'],d);cache[t]=z
            return cache[t]
        for t in (0.,1.):solve(t)
        while True:
            anchors=sorted(cache);intervals=[]
            for a,b in zip(anchors[:-1],anchors[1:]):
                if (a,b) not in interval_cache:
                    u,ms=corrected_chord(mix,a,b,cache[a]['value'],cache[b]['value'])
                    lo=[[restrict(x,a,b) for x in cache[t]['coeff']] for t in (a,b)]
                    cert=envelope_certificate(u,lo,depth=3)
                    interval_cache[a,b]=dict(left=a,right=b,bound=cert['bound'],correction_max_by_date=ms,
                        cells=cert['cells'],upper=u)
                intervals.append(dict(interval_cache[a,b]))
            worst=max(intervals,key=lambda x:x['bound']);bound=worst['bound']
            history.append(dict(anchors=len(anchors),bound=bound));print('KERNEL',d,len(anchors),bound,flush=True)
            if bound<=epsilon:break
            if len(anchors)>=65:raise RuntimeError('Declared accuracy not reached within 65 anchors')
            solve((worst['left']+worst['right'])/2)
        offline=time.perf_counter()-start;checks=[];saved={}
        policies=np.stack([cache[t]['policy'] for t in anchors])
        for i,t in enumerate(anchors):
            saved[f'policy.{i}']=cache[t]['policy'];saved[f'value.{i}']=cache[t]['value']
            for n,co in enumerate(cache[t]['coeff']):saved[f'lower.{i}.{n}']=co
        for i,iv in enumerate(intervals):
            a,b=iv['left'],iv['right'];u=iv.pop('upper')
            for n,co in enumerate(u):saved[f'upper.{i}.{n}']=co
            for t in (a,(a+b)/2,b):
                direct=mix.solve(t,d)['value'];q=(t-a)/(b-a)
                uv=np.stack([bernstein_value(x,q) for x in u]);pv=np.stack([[bernstein_value(x,t) for x in cache[z]['coeff']] for z in anchors])
                sel=pv[:,:-1].argmax(0);pol=np.take_along_axis(policies,sel[None],0)[0];sv=mix.evaluate(pol,t,d)
                loss=float((direct-sv).max());slack=float((uv-direct).min())
                assert loss<=bound+2e-10 and slack>=-2e-10 and (sv-pv.max(0)).min()>=-2e-10
                checks.append(dict(theta=t,actual_max_loss=loss,minimum_upper_slack=slack))
        saved['anchors']=np.array(anchors);np.savez_compressed(OUT/f'kernel_certificate_{d:g}.npz',**saved)
        result['rows'].append(dict(d=d,anchors=anchors,anchor_count=len(anchors),offline_seconds=offline,
            uniform_bound=bound,history=history,intervals=intervals,validation_checks=checks))
        save('kernel_certificate.json',result)
    return result
if __name__=='__main__':run()
