"""Direct constrained path costs of frozen R47 policies, not regret bounds."""
from __future__ import annotations
import argparse, itertools, math, time
from common import *
from tensor import Model
PATHS=262144;BITS=40;FAMILY=48;ALPHA=F(1,100);LOG=10;FEE=F(1,64)
LAWS=('uniform','1/8','1/2','7/8');SENSORS=(None,6,10)

class Policy:
    def __init__(self,path):
        self.path=Path(path);self.raw=read(path);self.T=self.raw['T'];self.p=self.raw['price'];self.N=self.raw['N']
        self.models=[]
        for m in self.raw['models'][:-1]:
            kind='witness' if m['kind']=='feasible-cone-witness' else 'fvi'
            self.models.append(Model([np.arange(m['N']+1)/m['N']]*2,m['labels'],kind,F(m['L'])))
        self.actors=self.raw['actors'];self.queries=0;self.ambiguities=0;self.measurement_ambiguities=0
    def action(self,t,x,bits):
        if bits is None:observed=x;capacity=cap(x)
        else:
            n=2**bits
            first=np.minimum(n-1,np.floor(x.lo*n).astype(int));last=np.minimum(n-1,np.floor(x.hi*n).astype(int))
            first=np.maximum(first,0);last=np.maximum(last,0)
            observed=I((first+.5)/n,(last+.5)/n)
            # Dyadic inputs and d=2 make these sums/divisions exact.
            capacity=I(1/8+np.sum(first,axis=1)/(16*n),1/8+np.sum(last,axis=1)/(16*n))
            self.measurement_ambiguities+=int(np.count_nonzero(np.any(first!=last,axis=1)))
        actor,amb=self.models[t].actor(observed,self.actors[t]);self.queries+=len(x.lo);self.ambiguities+=amb
        repaired=I(np.minimum(actor.lo,capacity.lo),np.minimum(actor.hi,capacity.hi))
        if bits is not None:repaired=I(np.maximum(0,np.floor(repaired.lo*4096)/4096),np.maximum(0,np.floor(repaired.hi*4096)/4096))
        return repaired
    def path_cost(self,x,z,bits):
        total=I.point(np.zeros(len(x.lo)))
        for t in range(self.T):
            a=self.action(t,x,bits);total=total+float(BETA**t)*costs(x,a,self.p);x=transition(x,a,z[t])
        return total+float(BETA**self.T)*costs(x,I.point(np.zeros(len(x.lo))),self.p,True)

def support(T,p):
    running=F(99+4*p,64);terminal=F(37,16)
    bound=sum((BETA**t*running for t in range(T)),F(0))+BETA**T*terminal
    return -bound,bound

def moments(x,a,b):
    n=len(x);u=F(1,2**53);gamma=(n+4)*u/(1-(n+4)*u);M=max(abs(F(a)),abs(F(b)))
    mu=F(float(np.mean(x)));sq=F(float(np.mean(x*x)));ml,mh=mu-gamma*M,mu+gamma*M
    qh=sq+gamma*M*M;minimum=F(0) if ml<=0<=mh else min(ml*ml,mh*mh)
    variance=max(F(0),F(n,n-1)*(qh-minimum))
    return {'n':n,'mean_lo':str(ml),'mean_hi':str(mh),'variance_upper':str(variance),'second_moment_upper':str(qh),'gamma':str(gamma),'endpoint_sha256':hashlib.sha256(x.tobytes()).hexdigest()}

def radius(stats,a,b):
    assert sum((F(LOG)**j/math.factorial(j) for j in range(41)),F(0))>4*FAMILY/ALPHA
    n=stats['n'];q=2*F(stats['variance_upper'])*LOG/n;root=math.sqrt(float(q))
    while F(root)**2<q:root=math.nextafter(root,math.inf)
    return F(root)+F(7*LOG,3*(n-1))*(F(b)-F(a))

def confidence(left,right,a,b):
    return max(F(a),F(left['mean_lo'])-radius(left,a,b)),min(F(b),F(right['mean_hi'])+radius(right,a,b))

def group(T,p,law,bits,out,npaths=PATHS):
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    start=time.perf_counter();cpu=time.process_time()
    paths=[P47/'results/constrained'/f'{m}-T{T}-p{p}-r0/checkpoint-N16.json' for m in ('feasible-cone-witness','bilinear-fvi')]
    for path in paths:
        record=read(path.parent/'record.json');a=next(v for v in record['attempts'] if v['N']==16);assert H(path)==a['checkpoint_sha256']
    policies=[Policy(q) for q in paths];a,b=support(T,p);A=c.enclosure(a)[0];B=c.enclosure(b)[1]
    key=f'T{T}-p{p}-law{law.replace("/","_")}-bits{bits}'
    seed=int.from_bytes(hashlib.sha256(('NBO-R48-CONSTRAINED-v1:'+key).encode()).digest()[:8],'big')
    rng=np.random.Generator(np.random.PCG64(seed));stream=hashlib.sha256();left=np.empty(npaths);right=np.empty(npaths)
    for begin in range(0,npaths,4096):
        n=min(4096,npaths-begin);bins=rng.integers(0,2**BITS,size=(T+2,n),dtype=np.uint64);stream.update(bins.tobytes());v=bins.astype(float)
        if law=='uniform':x=I(v[:2].T*2.**-BITS,(v[:2].T+1)*2.**-BITS)
        else:x=I.point(np.full((n,2),float(F(law))))
        z=[I(-1/32+v[t+2]*2.**(-BITS-4),-1/32+(v[t+2]+1)*2.**(-BITS-4)) for t in range(T)]
        score=[policy.path_cost(x,z,bits) for policy in policies];diff=score[0]-score[1]
        left[begin:begin+n]=np.maximum(A,diff.lo);right[begin:begin+n]=np.minimum(B,diff.hi)
        if np.any(left[begin:begin+n]>right[begin:begin+n]):raise AssertionError('Empty support intersection')
    lstat= moments(left,A,B);rstat=moments(right,A,B);lo,hi=confidence(lstat,rstat,A,B)
    record={'key':key,'T':T,'price':p,'initial_law':law,'sensor_bits':bits,'action_quantum':'0' if bits is None else '1/4096','paths':npaths,'bin_bits':BITS,'seed':seed,'stream_sha256':stream.hexdigest(),'family_size':FAMILY,'family_error':str(ALPHA),'log_upper':LOG,'replacement_fee':str(FEE),'estimand':'expected actual discounted witness cost minus expected actual discounted FVI cost, with the stated sensor and repair','support_exact':[str(a),str(b)],'lower_endpoint_moments':lstat,'upper_endpoint_moments':rstat,'interval_exact':[str(lo),str(hi)],'interval':[c.enclosure(lo)[0],c.enclosure(hi)[1]],'sign':'witness-lower' if hi<0 else ('witness-higher' if lo>0 else 'unresolved'),'neither_direction_recoups_fee':bool(-FEE<lo and hi<FEE),'mean_path_enclosure_width':float(np.mean(right-left)),'maximum_path_enclosure_width':float(np.max(right-left)),'policy_files':[{'path':str(q.relative_to(P47)),'sha256':H(q)} for q in paths],'actor_queries':[q.queries for q in policies],'ambiguous_actors':[q.ambiguities for q in policies],'ambiguous_measurements':[q.measurement_ambiguities for q in policies],'seconds_before_record':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,'clock_scope':'both frozen-policy loads and compilation, verified checkpoint hashes, common interval paths, repair, statistics; separate clock includes durable record output','development_only':npaths!=PATHS}
    digest=save(out,record);save(out.with_suffix('.clock.json'),{'record_sha256':digest,'seconds_through_record_fsync':time.perf_counter()-start,'joint_pair_cost_not_allocated_to_one_method':True})
    print(json.dumps({'key':key,'interval':record['interval'],'seconds':time.perf_counter()-start}),flush=True)
    return record

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--T',type=int,required=True);a.add_argument('--p',type=int,required=True);a.add_argument('--law',choices=LAWS,required=True);a.add_argument('--bits',type=int,required=True);a.add_argument('--out',required=True);v=a.parse_args();group(v.T,v.p,v.law,None if v.bits==0 else v.bits,v.out)
