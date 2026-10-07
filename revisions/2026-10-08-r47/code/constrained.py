"""Oracle-explicit two-state NBO and bilinear fitted-value iteration.

All numerical queries enclose the original continuous-shock expectation.
No conventional value is provided to the cone generator, or conversely.
"""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse, hashlib, itertools, json, math, platform, resource, sys, time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R.parent/'2026-10-07-r45/code'))
import constructive as c
from interval import I
METHODS=('feasible-cone-witness','bilinear-fvi');LADDER=(4,8,16)
TARGETS=(F(4),F(2),F(1),F(1,2));BETA=F(15,16)
CX=F(13,4);LG=F(9,2);FX=F(11,16);FA=F(3,4);KA=F(1,16)


def col(x,j):return I(x.lo[...,j],x.hi[...,j])
def join(a,b):return I(np.stack((a.lo,b.lo),axis=-1),np.stack((a.hi,b.hi),axis=-1))
def abs_i(x):
    return I(np.where((x.lo<=0)&(x.hi>=0),0,np.minimum(abs(x.lo),abs(x.hi))),np.maximum(abs(x.lo),abs(x.hi)))
def capacity(x):return 1/8+(col(x,0)+col(x,1))/16

def costs(x,a,p,terminal=False):
    x1,x2=col(x,0),col(x,1)
    target=(x1-5/8).square()+(x2-5/8).square()
    state=(2 if terminal else 1)*target+(x1-x2).square()/4+2*(1/2-x1-x2).clip(0,1).square()
    return state if terminal else state+p*a.square()+4*a.square().square()

def transition(x,a,z):
    x1,x2=col(x,0),col(x,1)
    f1=1/16+x1/2+x2/8+x1*(1-x2)/16+a/2+z
    f2=1/16+x2/2+x1/8+x2*(1-x1)/16+a/4-z
    return join(f1,f2).clip(0,1)

class Model:
    def __init__(self,N,values,kind,L=None):
        self.N=N;self.kind=kind;self.v=np.asarray(values,dtype=float).reshape(-1)
        if self.v.size!=(N+1)**2:raise ValueError('Incomplete nodal model')
        self.nodes=np.array(list(itertools.product(np.arange(N+1)/N,repeat=2)))
        if kind=='feasible-cone-witness':
            self.L=F(L)
        elif kind=='bilinear-fvi':
            v=self.v.reshape((N+1,N+1))
            self.L=F(float(N*max(np.max(np.abs(np.diff(v,axis=0))),np.max(np.abs(np.diff(v,axis=1))))))
        else:raise ValueError('Unknown model')
        if self.L<0:raise ValueError('Negative modulus')
        self.counts={'point_values':0,'cone_terms':0,'bilinear_patches':0}
    def cones(self,x):
        d=abs_i(I.point(x[:,None,:])-I.point(self.nodes[None,:,:]))
        distance=col(d,0)+col(d,1)
        return I.point(self.v[None,:])+c.rat_i(self.L)*distance
    def point(self,x,representation='native'):
        x=np.asarray(x,dtype=float).reshape(-1,2)
        self.counts['point_values']+=len(x)
        if self.kind=='feasible-cone-witness':
            lows=[];highs=[]
            for begin in range(0,len(x),512):
                ci=self.cones(x[begin:begin+512]);self.counts['cone_terms']+=ci.lo.size
                if representation=='relu':
                    while ci.lo.shape[1]>1:
                        k=ci.lo.shape[1]//2
                        a=I(ci.lo[:,:2*k:2],ci.hi[:,:2*k:2]);b=I(ci.lo[:,1:2*k:2],ci.hi[:,1:2*k:2])
                        m=a-(a-b).clip(0,np.inf)
                        if ci.lo.shape[1]%2:
                            m=I(np.concatenate((m.lo,ci.lo[:,-1:]),axis=1),np.concatenate((m.hi,ci.hi[:,-1:]),axis=1))
                        ci=m
                    lows.append(ci.lo[:,0]);highs.append(ci.hi[:,0])
                else:
                    lows.append(np.min(ci.lo,axis=1));highs.append(np.min(ci.hi,axis=1))
            return I(np.concatenate(lows),np.concatenate(highs))
        self.counts['bilinear_patches']+=len(x)
        ij=np.clip(np.floor(x*self.N).astype(int),0,self.N-1)
        tx=I.point(x[:,0])*self.N-I.point(ij[:,0]);ty=I.point(x[:,1])*self.N-I.point(ij[:,1])
        v=self.v.reshape((self.N+1,self.N+1));i,j=ij[:,0],ij[:,1]
        a=I.point(v[i,j]);b=I.point(v[i+1,j]);d=I.point(v[i,j+1]);e=I.point(v[i+1,j+1])
        return a+tx*(b-a)+ty*(d-a)+tx*ty*(e-b-d+a)
    def evaluate(self,x):
        center=x.midpoint();v=self.point(center)
        radius=np.maximum(np.nextafter(center-x.lo,np.inf),np.nextafter(x.hi-center,np.inf))
        rad=I.point(radius[:,0])+I.point(radius[:,1]);err=c.rat_i(self.L)*rad
        return v+I(-err.hi,err.hi)
    def payload(self):return {'N':self.N,'kind':self.kind,'labels':self.v.tolist(),'L':str(self.L)}
    @classmethod
    def load(cls,j):return cls(j['N'],j['labels'],j['kind'],j['L'])

def query(x,a,p,future,M):
    value=I.point(np.zeros(a.lo.shape))
    for j in range(M):
        z=F(2*j+1-M,32*M)
        value=value+future.evaluate(transition(x,a,c.rat_i(z)))
    # E|Z-midpoint(Z)|=1/(64M), and ||dF/dZ||_1=2.
    error=c.rat_i(future.L/F(32*M))
    return costs(x,a,p)+float(BETA)*(value/M+I(-error.hi,error.hi))

def nearest_excess(model,L):
    """Maximum upper enclosure on ALL nearest-cell subrectangle vertices.

    Bilinear interpolation and all cone pieces have no interior strict
    maxima after subtracting the appropriate affine distance term.
    """
    points=[];owners=[]
    for i,node in enumerate(model.nodes):
        for dx,dy in itertools.product((-0.5,0,0.5),repeat=2):
            points.append(np.clip(node+np.array([dx,dy])/model.N,0,1));owners.append(i)
    points=np.asarray(points);owners=np.asarray(owners)
    dist=np.sum(np.abs(points-model.nodes[owners]),axis=1) # exact dyadics
    upper=I.point(model.v[owners])+c.rat_i(L)*I.point(dist)-model.point(points)
    return F(float(np.max(upper.hi))),len(points)

def rung(N,T,p,method):
    if N not in (2,4,8,16) or method not in METHODS:raise ValueError('Undeclared construction')
    nodes=np.array(list(itertools.product(np.arange(N+1)/N,repeat=2)))
    terminal=costs(I.point(nodes),I.point(np.zeros(len(nodes))),p,True)
    labels,eT=c.rounded_labels(terminal);future=Model(N,labels,method,LG)
    models=[None]*T+[future];actors=[None]*T;rows=[None]*T
    h=F(1,N);k=F(1,8*N);widthT=2*eT+2*LG*h
    qcount=0;corner_count=0
    for t in range(T-1,-1,-1):
        A=CX+BETA*FX*future.L;D=F(p,2)+F(1,4)+BETA*FA*future.L;L=A+D*KA
        xi=np.repeat(nodes,N+1,axis=0)
        caps=1/8+np.sum(nodes,axis=1)/16
        actions=(caps[:,None]*np.arange(N+1)[None,:]/N).reshape(-1)
        q=query(I.point(xi),I.point(actions),p,future,N);qcount+=len(actions)
        values,e=c.rounded_labels(q);v=values.reshape(len(nodes),N+1);idx=np.argmin(v,axis=1)
        labels=v[np.arange(len(nodes)),idx];current=Model(N,labels,method,L)
        node_actions=actions.reshape(len(nodes),N+1)[np.arange(len(nodes)),idx]
        if method=='feasible-cone-witness':
            lo=-e;u=D*k+e+2*L*h;d=e;excess=F(0)
        else:
            lo=-e-L*h;u=D*k+e+L*h
            excess,n=nearest_excess(current,L);corner_count+=n;d=e+excess
        rows[t]={'date':t,'A':str(A),'D':str(D),'L_graph':str(L),'e':str(e),
                 'integration_remainder':str(BETA*future.L/F(32*N)),
                 'residual_lower':str(lo),'residual_upper':str(u),
                 'selected_policy_upper':str(d),'nearest_excess_upper':str(excess),
                 'component':str(u+d)}
        models[t]=current;actors[t]=node_actions.tolist();future=current
    gap=sum((BETA**t*F(row['component']) for t,row in enumerate(rows)),F(0))+BETA**T*widthT
    counts={'state_nodes_per_date':len(nodes),'node_actions_per_state':N+1,
            'bellman_queries':qcount,'innovation_midpoints':qcount*N,
            'primitive_cost_evaluations':qcount+len(nodes),
            'nearest_cell_corner_enclosures':corner_count,
            'stored_critic_labels':sum(len(m.v) for m in models),
            'stored_actor_scalars':sum(len(a) for a in actors),
            'counts_scope':'evaluated primitive objects, not hardware-independent FLOPs or bit operations'}
    for key in models[0].counts:counts[key]=sum(m.counts[key] for m in models)
    return {'method':method,'N':N,'T':T,'price':p,'models':[m.payload() for m in models],
            'actors':actors,'rows':rows,'terminal_error':str(eT),'terminal_width':str(widthT),
            'policy_bound_exact':str(gap),'policy_bound_upper':c.upper(gap),
            'action_repair':'min(stored node action,1/8+(x1+x2)/16)',
            'state_cover_l1':str(h),'action_cover_l1':str(k),'shock_midpoints':N},counts

def service(method,T,p,rep,out):
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    affinity=None
    if hasattr(os,'sched_getaffinity'):
        affinity=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{affinity})
    z=np.arange(4096,dtype=float)/4096
    for _ in range(8):z=(z+1)*.5
    start=time.perf_counter();cpu=time.process_time();out.mkdir(parents=True)
    attempts=[];first={str(e):None for e in TARGETS};cum=0
    for N in LADDER:
        begin=time.perf_counter();payload,counts=rung(N,T,p,method)
        checkpoint=out/f'checkpoint-N{N}.json';digest=c.write_new(checkpoint,payload)
        cum+=counts['bellman_queries']
        attempt={'N':N,'bound_exact':payload['policy_bound_exact'],'bound_upper':payload['policy_bound_upper'],
                 'counts':counts,'prefix_bellman_queries':cum,'checkpoint_sha256':digest,
                 'checkpoint_bytes':checkpoint.stat().st_size,
                 'prefix_seconds':time.perf_counter()-start,'rung_seconds':time.perf_counter()-begin}
        attempts.append(attempt)
        for e in TARGETS:
            if first[str(e)] is None and F(payload['policy_bound_exact'])<=e:
                first[str(e)]={k:attempt[k] for k in ('N','bound_exact','prefix_seconds','prefix_bellman_queries')}
    record={'method':method,'horizon':T,'price':p,'repeat':rep,'attempts':attempts,'first_crossings':first,
            'cpu_affinity':affinity,'frequency_controlled':False,'python':platform.python_version(),
            'numpy':np.__version__,'platform':platform.platform(),
            'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'cpu_seconds':time.process_time()-cpu,'seconds_before_record':time.perf_counter()-start,
            'clock_scope':'fresh own-future targets, continuous integration, representation, actors, certificates, failed rungs, fsync; startup and identical warm-up separate',
            'independent_direct_cost_comparison':'not part of this constrained construction clock'}
    digest=c.write_new(out/'record.json',record)
    c.write_new(out/'clock.json',{'record_sha256':digest,'seconds_through_record_fsync':time.perf_counter()-start})
    print(json.dumps({'method':method,'T':T,'p':p,'repeat':rep,'first':first}),flush=True)
if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('--method',choices=METHODS,required=True)
    pa.add_argument('--horizon',type=int,choices=(2,3),required=True);pa.add_argument('--price',type=int,choices=(1,4),required=True)
    pa.add_argument('--repeat',type=int,choices=(0,1,2),required=True);pa.add_argument('--out',required=True)
    a=pa.parse_args();service(a.method,a.horizon,a.price,a.repeat,a.out)
