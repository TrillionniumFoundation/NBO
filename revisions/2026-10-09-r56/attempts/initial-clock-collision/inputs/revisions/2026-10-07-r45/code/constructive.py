"""R45 deterministic own-future ReLU construction and matched spline service.

Rational PWL compilation is an exact accelerator for the defining min-plus
network. Uniform innovations are integrated analytically, with outward
arithmetic. A certificate is not a direct neural-minus-spline cost contrast.
"""
from __future__ import annotations
import os
for _key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[_key] = '1'
import argparse, bisect, hashlib, json, math, platform, resource, sys, time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from interval import I

ROOT = Path(__file__).resolve().parents[1]
BETA=F(15,16); SHOCK=F(1,32); CAP=F(1,4)
LADDER=(16,32,64,128,256,512); TARGETS=(F(1,2),F(1,4),F(1,8))
METHODS=('min-plus-ReLU','piecewise-linear-spline')
LABEL_SCALE=2**40


def frac(x):
    return x if isinstance(x,F) else F(float(x))


def enclosure(q):
    q=frac(q); v=float(q); fv=F(v)
    return (math.nextafter(v,-math.inf) if fv>q else v,
            math.nextafter(v,math.inf) if fv<q else v)


def rat_i(q):
    lo,hi=enclosure(q); return I(lo,hi)


def array_i(qs):
    bounds=[enclosure(q) for q in qs]
    return I(np.array([p[0] for p in bounds]),np.array([p[1] for p in bounds]))


def canonical(obj):
    return (json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def write_new(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    raw=canonical(obj)
    with path.open('xb') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    return hashlib.sha256(raw).hexdigest()


class PWL:
    """Exact rational knots and values, with a checked interval evaluator."""
    def __init__(self,knots,values,representation=None):
        self.k=list(map(frac,knots)); self.v=list(map(frac,values))
        if len(self.k)!=len(self.v) or len(self.k)<2:
            raise ValueError('Invalid PWL size')
        if self.k[0]!=0 or self.k[-1]!=1 or any(a>=b for a,b in zip(self.k,self.k[1:])):
            raise ValueError('Invalid PWL partition')
        self.s=[(b-a)/(y-x) for x,y,a,b in zip(self.k,self.k[1:],self.v,self.v[1:])]
        self.L=max(map(abs,self.s)); self.area=[F(0)]
        for x,y,a,b in zip(self.k,self.k[1:],self.v,self.v[1:]):
            self.area.append(self.area[-1]+(y-x)*(a+b)/2)
        self.ki=array_i(self.k); self.vi=array_i(self.v)
        self.si=array_i(self.s); self.ai=array_i(self.area)
        self.kf=np.array(list(map(float,self.k)))
        self.rep=representation
        self.stats={'point_evaluations':0,'antiderivative_evaluations':0,
                    'rational_boundary_resolutions':0,'binary_search_comparison_upper':0}
        self.max_abs=max(map(abs,self.v))

    @classmethod
    def from_labels(cls,knots,values,L,method):
        k=list(map(frac,knots)); v=list(map(frac,values)); L=frac(L)
        if method=='piecewise-linear-spline':
            return cls(k,v,{'method':method,'grid':list(map(str,k)),
                            'labels':list(map(str,v))})
        if method!='min-plus-ReLU' or L<0: raise ValueError('Invalid method or L')
        # Exact two-pass metric closure of arbitrary, possibly noisy labels.
        z=v.copy()
        for j in range(1,len(k)): z[j]=min(z[j],z[j-1]+L*(k[j]-k[j-1]))
        for j in range(len(k)-2,-1,-1): z[j]=min(z[j],z[j+1]+L*(k[j+1]-k[j]))
        kk=[k[0]]; vv=[z[0]]
        for j in range(len(k)-1):
            if L:
                cross=(k[j]+k[j+1])/2+(z[j+1]-z[j])/(2*L)
                if not k[j]<=cross<=k[j+1]: raise AssertionError('Lipschitz closure failed')
                if k[j]<cross<k[j+1]:
                    kk.append(cross);vv.append(z[j]+L*(cross-k[j]))
            kk.append(k[j+1]); vv.append(z[j+1])
        out=cls(kk,vv,{'method':method,'grid':list(map(str,k)),
                       'labels':list(map(str,v)),'L':str(L)})
        if out.L>L: raise AssertionError('Neural Lipschitz invariant failed')
        return out

    def index(self,x):
        x=np.asarray(x,dtype=float)
        if not np.isfinite(x).all() or np.any(x<0) or np.any(x>1):
            raise ValueError('Query outside [0,1]')
        j=np.asarray(np.clip(np.searchsorted(self.kf,x,side='right')-1,0,len(self.k)-2)).copy()
        # Conversion of a rational knot must not silently change its cell.
        bad=(x<self.ki.hi[j]) | (x>self.ki.lo[j+1])
        if np.any(bad):
            xf=x.reshape(-1); jf=j.reshape(-1)
            for idx in np.flatnonzero(bad.reshape(-1)):
                jf[idx]=min(len(self.k)-2,max(0,bisect.bisect_right(self.k,F(float(xf[idx])))-1))
            self.stats['rational_boundary_resolutions']+=int(np.count_nonzero(bad))
        self.stats['binary_search_comparison_upper']+=int(x.size)*math.ceil(math.log2(len(self.k))+1)
        return j

    def point(self,x,primitive=False):
        x=np.asarray(x,dtype=float);j=self.index(x)
        dx=I.point(x)-I(self.ki.lo[j],self.ki.hi[j])
        v=I(self.vi.lo[j],self.vi.hi[j]);s=I(self.si.lo[j],self.si.hi[j])
        if primitive:
            self.stats['antiderivative_evaluations']+=int(x.size)
            return I(self.ai.lo[j],self.ai.hi[j])+v*dx+s*dx.square()/2
        self.stats['point_evaluations']+=int(x.size)
        return v+s*dx

    def evaluate(self,x):
        x=x if isinstance(x,I) else I.point(x)
        center=np.clip(x.midpoint(),0,1)
        r=np.maximum(np.nextafter(center-x.lo,np.inf),np.nextafter(x.hi-center,np.inf))
        v=self.point(center);err=rat_i(self.L)*I.point(r)
        return v+I(-err.hi,err.hi)

    def uniform(self,base):
        """E f(base+U), U uniform[-1/32,1/32], original continuous law."""
        base=base if isinstance(base,I) else I.point(base)
        center=base.midpoint()
        if np.any(center<float(SHOCK)) or np.any(center>1-float(SHOCK)):
            raise ValueError('Innovation leaves domain')
        def primitive_arg(arg):
            # The exact argument is in [0,1]; intersect only rounding overhang.
            arg=arg.clip(0,1); c=arg.midpoint()
            rr=np.maximum(np.nextafter(c-arg.lo,np.inf),np.nextafter(arg.hi-c,np.inf))
            val=self.point(c,True); err=rat_i(self.max_abs)*I.point(rr)
            return val+I(-err.hi,err.hi)
        left=I.point(center)-rat_i(SHOCK); right=I.point(center)+rat_i(SHOCK)
        mid=(primitive_arg(right)-primitive_arg(left))/(2*float(SHOCK))
        rad=np.maximum(np.nextafter(center-base.lo,np.inf),np.nextafter(base.hi-center,np.inf))
        err=rat_i(self.L)*I.point(rad)
        return mid+I(-err.hi,err.hi)

    def exact(self,x,primitive=False):
        x=frac(x);j=min(len(self.k)-2,max(0,bisect.bisect_right(self.k,x)-1))
        h=x-self.k[j]
        return self.area[j]+self.v[j]*h+self.s[j]*h*h/2 if primitive else self.v[j]+self.s[j]*h

    def payload(self):
        return {'definition':self.rep,'knots':list(map(str,self.k)),
                'values':list(map(str,self.v)),'L':str(self.L)}


def stage(x,a,p):
    return (x-float(F(11,16))).square()+p*a.square()+4*a.square().square()+2*(float(F(3,8))-x).clip(0,1).square()


def terminal(x):
    return 2*(x-float(F(11,16))).square()+2*(float(F(3,8))-x).clip(0,1).square()


def base_state(x,a):
    # Protocol amendment: 1/32, not the preliminary erroneous 1/16.
    return float(F(1,32))+float(F(11,16))*x+float(F(1,16))*x*(1-x)+a


def rounded_labels(q):
    rounded=np.rint(q.midpoint()*LABEL_SCALE)/LABEL_SCALE
    err=np.maximum(np.nextafter(rounded-q.lo,np.inf),np.nextafter(q.hi-rounded,np.inf))
    return rounded,F(float(np.max(err)))


def upper(q):return enclosure(q)[1]


def rung(N,T,p,method):
    k=[F(j,N) for j in range(N+1)];x=np.array(list(map(float,k)))
    actions=np.arange(N+1,dtype=float)/(4*N)
    tv=terminal(I.point(x)); y,eT=rounded_labels(tv)
    Lg=F(17,4) # exact derivative bound on g; 4.25 at x=0
    future=PWL.from_labels(k,y,Lg,method)
    h=F(1,2*N);ha=F(1,8*N)
    terminal_width=2*eT+2*Lg*h
    models=[None]*T+[future]; actors=[None]*T; rows=[None]*T
    for t in range(T-1,-1,-1):
        Lx=F(23,8)+BETA*F(3,4)*future.L
        La=F(p,2)+F(1,4)+BETA*future.L
        xi=I.point(x[:,None]);ai=I.point(actions[None,:])
        b=base_state(xi,ai)
        q=stage(xi,ai,p)+float(BETA)*future.uniform(b)
        qhat,e=rounded_labels(q); index=np.argmin(qhat,axis=1)
        labels=qhat[np.arange(N+1),index]
        current=PWL.from_labels(k,labels,Lx,method)
        if method=='min-plus-ReLU':lo=-e;hi=La*ha+e+2*Lx*h
        else:lo=-e-Lx*h;hi=La*ha+e+Lx*h
        eta=La*ha+2*e+2*Lx*h
        rows[t]={'date':t,'L_future':str(future.L),'Lx':str(Lx),'La':str(La),
                 'oracle_error':str(e),'residual_lower':str(lo),'residual_upper':str(hi),
                 'actor_allowance':str(eta),'bound_component':str(hi-lo+eta)}
        actors[t]=actions[index].tolist();models[t]=current;future=current
    G=sum((BETA**t*F(r['bound_component']) for t,r in enumerate(rows)),F(0))+BETA**T*terminal_width
    payload={'method':method,'N':N,'T':T,'price':p,'models':[m.payload() for m in models],
             'actors':actors,'rows':rows,'terminal_width':str(terminal_width),
             'policy_bound_exact':str(G),'policy_bound_upper':upper(G)}
    counts={'q_evaluations':T*(N+1)**2,'own_future_uniform_integrals':T*(N+1)**2,
            'state_action_primitive_evaluations':T*(N+1)**2,
            'labels':(T+1)*(N+1),'actor_scalar_storage':T*(N+1),
            'compiled_knots':sum(len(m.k) for m in models),
            'compiled_rational_scalars':sum(2*len(m.k)+len(m.s)+len(m.area) for m in models),
            'max_rational_bit_length':max(max(abs(q.numerator).bit_length(),q.denominator.bit_length()) for m in models for seq in (m.k,m.v,m.s,m.area) for q in seq)}
    for key in models[0].stats:counts[key]=sum(m.stats[key] for m in models)
    # Native primitive counts are not presented as full FLOP or bit counts.
    counts['count_scope']='evaluated primitive objects and exact-storage quantities; not a complete FLOP count'
    return payload,counts


def service(method,T,p,rep,out):
    affinity=None
    if hasattr(os,'sched_getaffinity'):
        affinity=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{affinity})
    # Identical, non-economic warm-up, excluded explicitly from the service clock.
    z=np.arange(4096,dtype=float)/4096
    for _ in range(8): z=(z+1)*.5
    start=time.perf_counter();time_process=time.process_time()
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    attempts=[];first={str(e):None for e in TARGETS};cum_q=0
    for N in LADDER:
        begin=time.perf_counter()
        payload,counts=rung(N,T,p,method)
        rawhash=write_new(out/f'checkpoint-N{N}.json',payload)
        elapsed=time.perf_counter()-start; cum_q+=counts['q_evaluations']
        att={'N':N,'policy_bound_upper':payload['policy_bound_upper'],
             'policy_bound_exact':payload['policy_bound_exact'],
             'checkpoint_sha256':rawhash,'seconds_through_checkpoint_fsync':elapsed,
             'rung_seconds_through_fsync':time.perf_counter()-begin,
             'cumulative_q_evaluations':cum_q,'counts':counts,
             'checkpoint_bytes':(out/f'checkpoint-N{N}.json').stat().st_size}
        attempts.append(att)
        for e in TARGETS:
            if first[str(e)] is None and F(payload['policy_bound_exact'])<=e:
                first[str(e)]={'N':N,'seconds_through_checkpoint_fsync':elapsed,
                               'cumulative_q_evaluations':cum_q,'bound':payload['policy_bound_upper']}
    record={'method':method,'horizon':T,'price':p,'repeat':rep,'attempts':attempts,
            'first_crossings':first,'full_frontier_q_evaluations':cum_q,
            'seconds_before_final_serialization':time.perf_counter()-start,
            'cpu_seconds_before_final_serialization':time.process_time()-time_process,
            'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'cpu_affinity':affinity,'frequency_controlled':False,
            'platform':platform.platform(),'python':platform.python_version(),'numpy':np.__version__,
            'source_hashes':{n:hashlib.sha256((ROOT/'code'/n).read_bytes()).hexdigest() for n in ('constructive.py','interval.py')},
            'initialization_randomness':'none; deterministic construction',
            'independent_policy_comparison':'not executed and not included in this service',
            'timing_scope':'all fresh-rung target construction, exact compilation, actors, certificates and durable checkpoints; imports and common non-economic warm-up excluded'}
    h=write_new(out/'record.json',record)
    write_new(out/'clock.json',{'record_sha256':h,'seconds_through_record_fsync':time.perf_counter()-start})
    print(json.dumps({'method':method,'T':T,'p':p,'repeat':rep,'first':first,'seconds':time.perf_counter()-start}),flush=True)


if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('--method',choices=METHODS,required=True)
    pa.add_argument('--horizon',type=int,choices=(2,4),required=True);pa.add_argument('--price',type=int,choices=(1,4),required=True)
    pa.add_argument('--repeat',type=int,choices=(0,1,2),required=True);pa.add_argument('--out',required=True)
    a=pa.parse_args();service(a.method,a.horizon,a.price,a.repeat,a.out)
