"""Immutable actors, exact displacement supports and exact endpoint inference."""
from fractions import Fraction as F
from pathlib import Path
import hashlib,json,math
import numpy as np
R=Path(__file__).resolve().parents[1]
N=131072; BIN_BITS=40; SEED=20261011074; SCALE=1<<60
BETA=F(15,16); H=F(87,64)*(1+BETA)+BETA**2*F(33,16)
NAMES=('zero','relu-n8','bernstein-n8','relu-n16','bernstein-n16')
PAIRS=((1,0),(2,0),(3,0),(4,0),(1,2),(3,4),(3,1),(4,2))

def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [encode(v) for v in x]
    return x

def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(encode(x),sort_keys=True,indent=2)+'\n')

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def actors(root=R):
    out=[dict(name='zero',n=1,actions=np.zeros((2,1,1),dtype=np.uint16),construction_seconds=0,source_sha256=None)]
    for name in NAMES[1:]:
        folder=root/'results73'/name;path=folder/'service.json';v=json.loads(path.read_text());n=v['n']
        arr=np.array([[int(F(x)*4096) for x in stage['data']['actions']] for stage in sorted(v['stages'],key=lambda z:z['date'])],dtype=np.uint16).reshape(2,n,n)
        for stage in v['stages']:
            for x in stage['data']['actions']:
                assert (F(x)*4096).denominator==1
        for t,i,j in np.ndindex(arr.shape):
            assert F(int(arr[t,i,j]),4096)<=F(1,8)+F(i+j,16*n)
        clock=json.loads((folder/'clock.json').read_text());assert clock['service_sha256']==sha(path)
        out.append(dict(name=name,n=n,actions=arr,source_sha256=sha(path),construction_seconds=clock['seconds_through_service_output']))
    for a in out:a['policy_sha256']=hashlib.sha256(a['actions'].astype('<u2').tobytes()+str(a['n']).encode()).hexdigest()
    return out

def identical(a,b):
    n=math.lcm(a['n'],b['n'])
    def lift(x):return np.repeat(np.repeat(x['actions'],n//x['n'],axis=1),n//x['n'],axis=2)
    return np.array_equal(lift(a),lift(b))

def support(a,b):
    """Exact finite cell-pair modulus; no stochastic or value-oracle input."""
    if identical(a,b):return dict(bound=F(0),identity=True,dates=[],cell_pair_checks=0)
    grid=math.lcm(a['n'],b['n']);ia=np.indices((a['n'],a['n'])).reshape(2,-1).T*(grid//a['n']);ib=np.indices((b['n'],b['n'])).reshape(2,-1).T*(grid//b['n'])
    dist=np.maximum(0,np.maximum(ia[:,None,:]-(ib[None,:,:]+grid//b['n']),ib[None,:,:]-(ia[:,None,:]+grid//a['n']))).sum(axis=2)
    delta=F(0);total=F(0);dates=[];checks=0
    for t in range(2):
        eligible=dist*delta.denominator<=delta.numerator*grid
        diff=np.abs(a['actions'][t].astype(np.int64).reshape(-1,1)-b['actions'][t].astype(np.int64).reshape(1,-1))
        alpha=F(int(diff[eligible].max()),4096);next_delta=min(F(2),F(11,16)*delta+F(3,4)*alpha)
        total+=BETA**t*(4*delta+F(13,16)*alpha)
        dates.append(dict(date=t,state_l1_bound=delta,action_bound=alpha,next_state_l1_bound=next_delta,eligible_cell_pairs=int(eligible.sum())))
        delta=next_delta;checks+=dist.size
    total+=BETA**2*5*delta
    return dict(bound=min(H,total),uncapped_bound=total,identity=False,dates=dates,cell_pair_checks=checks)

def sqrt_upper(x,bits=60):
    x=F(x)
    if x<0:raise ValueError('Negative square root')
    scale=1<<bits;num=x.numerator*scale*scale;den=x.denominator
    k=math.isqrt(num//den)
    if k*k*den<num:k+=1
    return F(k,scale)

def endpoint_interval(lo,hi,lower,upper,identity=False):
    lo=np.asarray(lo);hi=np.asarray(hi);n=len(lo);lower=F(lower);upper=F(upper)
    if identity:
        assert np.array_equal(lo,hi) and not np.any(lo)
        return dict(interval=(F(0),F(0)),width=F(0),identity=True,precision_met=True,equivalent=True,strictly_lower=False,strictly_higher=False)
    assert n>1 and np.all(lo<=hi)
    assert sum(F(9)**k/math.factorial(k) for k in range(25))>5200
    def moments(values):
        s=sum(map(int,values));ss=sum(int(z)**2 for z in values)
        mean=F(s,n*SCALE);var=F(n*ss-s*s,n*(n-1)*SCALE*SCALE)
        radius_sampling=sqrt_upper(18*var/n)
        radius_range=F(21)*(upper-lower)/(n-1)
        return mean,var,radius_sampling,radius_range
    ml,vl,sl,rl=moments(lo);mu,vu,su,ru=moments(hi)
    out=(max(lower,ml-sl-rl),min(upper,mu+su+ru));width=out[1]-out[0]
    assert width>=0
    return dict(interval=out,width=width,identity=False,sample_count=n,mean_lower=ml,mean_upper=mu,variance_lower=vl,variance_upper=vu,sampling_radius_lower=sl,sampling_radius_upper=su,range_radius=rl,mean_bin_enclosure_width=mu-ml,arithmetic_rounding_per_endpoint=F(1,SCALE),support=(lower,upper),precision_met=width<=F(1,256),equivalent=out[0]>=-F(1,256) and out[1]<=F(1,256),strictly_lower=out[1]<0,strictly_higher=out[0]>0)
