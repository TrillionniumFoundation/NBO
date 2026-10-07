"""R47 coupled constrained economy, tensor witness compilation and robust deployment."""
from __future__ import annotations
import argparse,itertools,json,math,os,platform,resource,time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from common import R,I,dn,up,fi,fup,isum,absolute,write,hfile,BETA
METHODS=('witness','multilinear-fvi')
ACTION_BITS=20

def grid(d,N):return np.stack(np.meshgrid(*([np.arange(N+1)/N]*d),indexing='ij'),axis=-1).reshape(-1,d)

def capacity(x):return I.point(.25)+isum(x,axis=-1)/(4*x.lo.shape[-1])

def stage(x,a,p):return isum((x-.5).square())/(8*x.lo.shape[-1])+p*a.square()/2

def terminal(x):
    d=x.lo.shape[-1];mean=isum(x)/d
    cyclic=I(np.roll(x.lo,-1,axis=-1),np.roll(x.hi,-1,axis=-1))
    return (1-mean).square()+isum((x-cyclic).square())/(8*d)

def transition(x,a,z):
    return I.point(1/16)+x/2+I(np.roll(x.lo,-1,axis=-1),np.roll(x.hi,-1,axis=-1)).square()/8+a/4+z/16

def tensor_compile(labels,d,N,L):
    """Exact separable L1 closure, carrying ORIGINAL label indices through every pass."""
    shape=(N+1,)*d;values=np.array([F(float(v)) for v in labels],dtype=object).reshape(shape)
    owners=np.arange(len(labels),dtype=np.int64).reshape(shape);step=F(L)/N;ops=0
    for axis in range(d):
        for other in itertools.product(range(N+1),repeat=d-1):
            def loc(j):return tuple(other[:axis])+(j,)+tuple(other[axis:])
            for forward in (True,False):
                order=range(1,N+1) if forward else range(N-1,-1,-1)
                for j in order:
                    at=loc(j);prev=loc(j-1 if forward else j+1)
                    candidate=(values[prev]+step,int(owners[prev]));current=(values[at],int(owners[at]))
                    if candidate<current:values[at],owners[at]=candidate
                    ops+=1
    bit=max(max(q.numerator.bit_length(),q.denominator.bit_length()) for q in values.flat)
    return owners.reshape(-1),{'rational_additions':ops,'rational_comparisons':ops,'max_rational_bits':bit}

class Model:
    def __init__(self,data):
        self.data=data;self.d=data['d'];self.N=data['N'];self.method=data['method']
        self.x=grid(self.d,self.N);self.y=np.asarray(data['labels'],dtype=float)
        self.actions=np.asarray(data['actions'],dtype=float);self.L=float(data['L'])
        self.owners=np.asarray(data.get('owners',range(len(self.y))),dtype=int)
        self.bits=np.array(list(itertools.product((0,1),repeat=self.d)))
        self.strides=(self.N+1)**np.arange(self.d-1,-1,-1)
        self.evaluations=0;self.score_evaluations=0
    def corner_ids(self,x):
        cells=np.clip(np.floor(x*self.N).astype(int),0,self.N-1)
        ids=((cells[:,None,:]+self.bits[None,:,:])*self.strides).sum(axis=-1)
        return cells,ids
    def scores(self,x,flat=False):
        if flat:ids=np.broadcast_to(np.arange(len(self.y)),(len(x),len(self.y)))
        else:ids=self.owners[self.corner_ids(x)[1]]
        distance=I.point(np.zeros(ids.shape))
        for j in range(self.d):distance=distance+absolute(I.point(x[:,j,None])-self.x[ids,j])
        self.score_evaluations+=ids.size
        return I.point(self.y[ids])+self.L*distance,ids
    def point(self,x,backend='compiled-min-plus'):
        x=np.asarray(x,dtype=float).reshape(-1,self.d);self.evaluations+=len(x)
        if self.method=='witness':
            scores,ids=self.scores(x,flat=backend=='flat-min-plus')
            if backend=='compiled-ReLU':
                lo=scores.lo;hi=scores.hi
                while lo.shape[1]>1:
                    a=I(lo[:,::2],hi[:,::2]);b=I(lo[:,1::2],hi[:,1::2]);delta=a-b
                    m=a-I(np.maximum(0,delta.lo),np.maximum(0,delta.hi))
                    lo,hi=m.lo,m.hi
                return I(lo[:,0],hi[:,0])
            return I(scores.lo.min(axis=1),scores.hi.min(axis=1))
        cells,ids=self.corner_ids(x)
        theta=I.point(x*self.N-cells)
        result=I.point(np.zeros(len(x)))
        for k,bit in enumerate(self.bits):
            weight=I.point(np.ones(len(x)))
            for j,b in enumerate(bit):
                tj=I(theta.lo[:,j],theta.hi[:,j]);weight=weight*(tj if b else 1-tj)
            result=result+weight*self.y[ids[:,k]]
        return result
    def evaluate(self,x):
        shape=x.lo.shape[:-1];lo=x.lo.reshape(-1,self.d);hi=x.hi.reshape(-1,self.d)
        mid=np.clip(lo+(hi-lo)*.5,0,1)
        radius=isum(I.point(np.maximum(up(mid-lo),up(hi-mid)))).hi
        v=self.point(mid);err=up(self.L*radius)
        return I(dn(v.lo-err).reshape(shape),up(v.hi+err).reshape(shape))
    def numerical_excess(self):
        return fup(F(1,2**36)*(1+max(F(abs(float(y))) for y in self.y)+self.d*F(self.L)))
    def deploy(self,x,bits):
        """Return the actual dyadic action, robustly feasible throughout each acquired cell."""
        x=np.asarray(x,dtype=float);scale=2**bits
        q=np.clip(np.floor(x*scale).astype(np.int64),0,scale-1)
        mid=(q+.5)/scale
        if self.method=='witness':
            score,ids=self.scores(mid);pick=np.argmin(score.hi,axis=1)
            owner=ids[np.arange(len(x)),pick]
            actual_excess=up(score.hi[np.arange(len(x)),pick]-score.lo.min(axis=1))
            if np.any(actual_excess>self.numerical_excess()):raise ArithmeticError('Score allowance exceeded')
        else:
            near=np.floor(mid*self.N+.5).astype(int);near=np.clip(near,0,self.N)
            owner=(near*self.strides).sum(axis=1);actual_excess=np.zeros(len(x))
        # Exact integer floor of 2^20 times inf_U capacity; all products < 2^63.
        cap_units=(2**ACTION_BITS*(self.d*scale+q.sum(axis=1)))//(4*self.d*scale)
        stored_units=np.rint(self.actions[owner]*2**ACTION_BITS).astype(np.int64)
        units=np.minimum(stored_units,cap_units)
        return units.astype(float)/2**ACTION_BITS,{'repaired':int(np.count_nonzero(units<stored_units)),
                 'max_score_excess':float(actual_excess.max(initial=0)),
                 'min_capacity_slack_units':int((cap_units-units).min(initial=0))}
    def interval_action(self,x,bits):
        scale=2**bits
        ql=np.clip(np.floor(x.lo*scale).astype(np.int64),0,scale-1)
        qh=np.clip(np.floor(x.hi*scale).astype(np.int64),0,scale-1)
        bad=np.any(ql!=qh,axis=1)
        a,stats=self.deploy(x.midpoint(),bits)
        lo=a.copy();hi=a.copy();lo[bad]=0;hi[bad]=.5
        stats['acquisition_ambiguities']=int(np.count_nonzero(bad))
        return I(lo,hi),stats

def moduli(d,p,Lnext):
    A=F(1,8*d)+BETA*F(3,4)*F(Lnext)
    D=F(p)/2+BETA*F(d,4)*F(Lnext)
    return A,D,A+D/F(4*d)

def nearest_excess(model,Lq):
    points=grid(model.d,2*model.N);q=np.rint(points*(2*model.N)).astype(int)
    low=q//2;high=(q+1)//2
    v=model.point(points);best=-math.inf
    dist=I.point((q%2).sum(axis=1)/(2*model.N))
    for bit in model.bits:
        ids=(np.where(bit,high,low)*model.strides).sum(axis=1)
        excess=I.point(model.y[ids])+fi(Lq)*dist-v
        best=max(best,float(excess.hi.max()))
    return F(best),len(points)*2**model.d

def rung(d,T,p,N,method):
    x=grid(d,N);K=len(x);J=N+1;M=2*N
    # Exact rational capacity/action fractions, rounded downward into feasible dyadics.
    q=np.rint(x*N).astype(np.int64);s=q.sum(axis=1)
    numer=(d*N+s)[:,None]*np.arange(J)[None,:]*2**ACTION_BITS
    a_units=numer//(4*d*N*N)
    actions=a_units.astype(float)/2**ACTION_BITS
    Lnext=fup(F(5,2*d));future=None;models=[None]*T;rows=[None]*T;counts={'q_queries':0,'innovation_evaluations':0,'cone_scores':0,'rational_additions':0,'rational_comparisons':0,'actor_enclosure_points':0}
    for t in reversed(range(T)):
        A,D,Lq=moduli(d,p,Lnext);Lq_float=fup(Lq)
        # Use the upward dyadic modulus as the defining cone slope and in all bounds.
        Lq=F(Lq_float);midqueries=np.empty((K,J));errors=[]
        for begin in range(0,K,64):
            xb=x[begin:begin+64];ab=actions[begin:begin+64]
            xp=np.broadcast_to(xb[:,None,None,:],(len(xb),J,M,d))
            ap=np.broadcast_to(ab[:,:,None,None],xp.shape)
            z=(2*np.arange(M)+1)/M-1
            zp=np.broadcast_to(z[None,None,:,None],xp.shape)
            f=transition(I.point(xp),I.point(ap),I.point(zp)).clip(0,1)
            v=terminal(f) if future is None else future.evaluate(f)
            expectation=isum(v,axis=-1)/M
            rem=BETA*F(Lnext)*F(d,32*M)
            query=stage(I.point(np.broadcast_to(xb[:,None,:],(len(xb),J,d))),I.point(ab),p)+fi(BETA)*expectation
            query=query+I(-fup(rem),fup(rem))
            y=query.midpoint();err=np.maximum(up(y-query.lo),up(query.hi-y))
            midqueries[begin:begin+len(xb)]=y;errors.append(float(err.max()))
        e=F(max(errors));select=np.argmin(midqueries,axis=1)
        labels=midqueries[np.arange(K),select];chosen=actions[np.arange(K),select]
        data={'d':d,'N':N,'method':method,'labels':labels.tolist(),'actions':chosen.tolist(),'L':Lq_float}
        compile_counts={}
        if method=='witness':
            owners,compile_counts=tensor_compile(labels,d,N,Lq);data['owners']=owners.tolist()
            counts['rational_additions']+=compile_counts['rational_additions'];counts['rational_comparisons']+=compile_counts['rational_comparisons']
            Lf=Lq;u=D*(F(1,4*N)+F(1,2**ACTION_BITS))+e+Lq*F(d,N);selected=e
        else:
            y=labels.reshape((N+1,)*d);Lfloat=0.
            for j in range(d):
                v1=np.take(y,np.arange(1,N+1),axis=j);v0=np.take(y,np.arange(N),axis=j)
                slope=absolute(I.point(v1)-I.point(v0))*N
                Lfloat=max(Lfloat,float(slope.hi.max()))
            Lf=F(Lfloat);data['L']=Lfloat
            u=D*(F(1,4*N)+F(1,2**ACTION_BITS))+e+Lq*F(d,2*N)
        model=Model(data)
        if method!='witness':
            excess,work=nearest_excess(model,Lq);selected=e+excess;counts['actor_enclosure_points']+=work
        counts['q_queries']+=K*J;counts['innovation_evaluations']+=K*J*M
        if future is not None:counts['cone_scores']+=future.score_evaluations
        data['compiler']=compile_counts
        row={'date':t,'L_future':str(F(Lnext)),'A':str(A),'D':str(D),'Lq':str(Lq),'Lf':str(Lf),'query_error':str(e),'residual_upper':str(u),'selected_upper':str(selected),'ideal_component':str(u+selected)}
        for bits in (12,20):
            radius=F(d,2**(bits+1));diam=F(d,2**bits)
            delta=(2*Lf if method=='witness' else Lq+Lf)*radius+D*(diam/F(4*d)+F(1,2**ACTION_BITS))
            if method=='witness':delta+=F(model.numerical_excess())
            row[f'deployment_allowance_{bits}']=str(delta)
        rows[t]=row;models[t]=data;future=model;Lnext=float(Lf)
    gaps={}
    ideal=sum(BETA**t*F(r['ideal_component']) for t,r in enumerate(rows));gaps['ideal']=fup(ideal)
    for bits in (12,20):gaps[str(bits)]=fup(sum(BETA**t*(F(r['ideal_component'])+F(r[f'deployment_allowance_{bits}'])) for t,r in enumerate(rows)))
    payload={'d':d,'T':T,'price':p,'N':N,'method':method,'models':models,'rows':rows,'gaps':gaps,'counts':counts,
             'terminal':'Exact primitive quadratic, evaluated with outward arithmetic; no terminal interpolation error',
             'action_cover_radius_exact':str(F(1,4*N)+F(1,2**ACTION_BITS)),'innovation_bins':M}
    return payload

def service(d,T,p,method,repeat,out):
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True)
    if hasattr(os,'sched_getaffinity'):
        allowed=os.sched_getaffinity(0);os.sched_setaffinity(0,{min(allowed)})
    start=time.perf_counter();cpu=time.process_time();attempts=[];prefix_q=0
    for N in ((4,8,16) if d==2 else (2,4,8)):
        before=time.perf_counter();payload=rung(d,T,p,N,method)
        path=out/f'checkpoint-N{N}.json';digest=write(path,payload);prefix_q+=payload['counts']['q_queries']
        attempts.append({'N':N,'gaps':payload['gaps'],'rung_seconds':time.perf_counter()-before,'prefix_seconds':time.perf_counter()-start,'prefix_q_queries':prefix_q,'checkpoint_sha256':digest,'checkpoint_bytes':path.stat().st_size,'counts':payload['counts']})
    crossings={str(F(j,32)):next((a['N'] for a in attempts if F(a['gaps']['12'])<=F(j,32)),None) for j in range(1,33)}
    record={'d':d,'T':T,'price':p,'method':method,'repeat':repeat,'attempts':attempts,'first_crossings':crossings,'cpu_seconds':time.process_time()-cpu,
            'internal_seconds_before_record':time.perf_counter()-start,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'python':platform.python_version(),'numpy':np.__version__,'platform':platform.platform(),'cpu_frequency_controlled':False,
            'cpu_affinity':sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None}
    write(out/'record.json',record)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--d',type=int,required=True);ap.add_argument('--T',type=int,required=True);ap.add_argument('--price',type=float,required=True);ap.add_argument('--method',choices=METHODS,required=True);ap.add_argument('--repeat',type=int,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();service(a.d,a.T,a.price,a.method,a.repeat,a.out)
