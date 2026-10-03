"""Independent mpmath.iv replay of complete scalar R6 covers.

No R6 arithmetic routine is imported. Stored binary64 coefficients denote exact
real numbers. The conclusion remains conditional on mpmath's implementation,
not a formal proof of machine execution. Decimal precision: 40 digits.
"""
from pathlib import Path
import hashlib, json, time
import numpy as np
from mpmath import iv
ROOT=Path(__file__).resolve().parents[3]
OLD=ROOT/'revisions/2026-09-29-r6/results'
OUT=Path(__file__).resolve().parents[1]/'results'
iv.dps=40

def scalar(x): return iv.mpf(float(x))
def tanh(x): return 1-2/(iv.exp(2*x)+1)
def prepare(layers):
    return [([[scalar(x) for x in row] for row in z['weight']], [scalar(x) for x in z['bias']]) for z in layers]
def jets(x,layers):
    h=[x];d=[iv.mpf(1)];dd=[iv.mpf(0)]
    for k,(w,b) in enumerate(layers):
        hh=[];dx=[];dxx=[]
        for row,bi in zip(w,b):
            v=bi;v1=iv.mpf(0);v2=iv.mpf(0)
            for a,z,z1,z2 in zip(row,h,d,dd): v+=a*z;v1+=a*z1;v2+=a*z2
            if k<len(layers)-1:
                th=tanh(v);one=1-th**2
                # The exact derivative of tanh lies in [0,1].
                one=iv.mpf([max(iv.mpf(0).a,one.a),min(iv.mpf(1).b,one.b)])
                v2=-2*th*one*v1**2+one*v2;v1=one*v1;v=th
            hh.append(v);dx.append(v1);dxx.append(v2)
        h,d,dd=hh,dx,dxx
    return h[0],d[0],dd[0]
def bounds(x):
    return np.nextafter(float(x.a),-np.inf),np.nextafter(float(x.b),np.inf)
def clip_endpoint(z,l,u):
    if z<=0:return u
    return min(max(1/z,l),u)
def leaf(a,b,model,vnet,anet):
    p={k:scalar(x) for k,x in model['parameters'].items()}
    l,u=p['lower'],p['upper'];x=iv.mpf([float(a),float(b)]);scale=2/(u-l);z=scale*(x-l)-1
    n,nz,nzz=jets(z,vnet);nx=nz*scale;nxx=nzz*scale**2
    g0,g1=map(scalar,model['boundary_values']);slope=(g1-g0)/(u-l)
    q=(x-l)*(u-x);qp=l+u-2*x
    v=g0+slope*(x-l)+q*n;vx=slope+qp*n+q*nx;vxx=-2*n+2*qp*nx+q*nxx
    # Endpoint monotonicity is evaluated in interval arithmetic, not floats.
    low=clip_endpoint(vx.b,p['c_lower'].a,p['c_upper'].b)
    high=clip_endpoint(vx.a,p['c_lower'].a,p['c_upper'].b)
    best=iv.mpf([low.a,high.b])
    if anet is None:c=best
    else:
        raw,_,_=jets(z,anet)
        c=p['c_lower']+(p['c_upper']-p['c_lower'])*(1+tanh(raw/2))/2
    r=p['discount']*v-iv.log(c)-(p['income']+p['interest']*x-c)*vx-p['volatility']**2*x**2*vxx/2
    if anet is None:gap=iv.mpf(0)
    else:
        literal=iv.log(best)-iv.log(c)+(c-best)*vx
        cap=iv.mpf(max(c.b,best.b));strong=cap**2*(1/c-vx)**2/2
        gap=iv.mpf([0,max(iv.mpf(0).b,min(literal.b,strong.b))])
    lo,hi=bounds(r);_,gaphi=bounds(gap)
    return [a,b,lo,hi,max(0,gaphi)]
def replay(method):
    name=f'consumption_{method}_s11_w16_d2_r8_c60_a40'
    source=OLD/(name+'.json');cover=OLD/(name+'_interval_leaves.npz')
    model=json.loads(source.read_text());leaves=np.load(cover)['leaves'];p=model['parameters']
    assert leaves[0,0]==p['lower'] and leaves[-1,1]==p['upper']
    assert np.array_equal(leaves[:-1,1],leaves[1:,0]) and np.all(leaves[:,1]>leaves[:,0])
    vnet=prepare(model['value']);anet=prepare(model['actor']) if model['actor'] is not None else None
    start=time.perf_counter();new=[]
    for k,(a,b,*_) in enumerate(leaves):
        new.append(leaf(a,b,model,vnet,anet))
        if (k+1)%1000==0:print(method,k+1,'/',len(leaves),flush=True)
    new=np.array(new);e=float(np.max(abs(new[:,2:4])));eta=float(new[:,4].max());boundary=[]
    for x,g in zip([p['lower'],p['upper']],model['boundary_values']):
        delta=scalar(g)-iv.log(scalar(p['income'])+scalar(p['discount'])*scalar(x))/scalar(p['discount'])
        lo,hi=bounds(delta);boundary.append(max(abs(lo),abs(hi)))
    B=max(boundary);regret=2*scalar(B)+(2*scalar(e)+scalar(eta))/scalar(p['discount'])
    out=dict(method=method,seed=11,library='mpmath.iv',decimal_precision=iv.dps,
        leaves=len(new),covered=True,domain=[p['lower'],p['upper']],residual_upper=e,action_gap_upper=eta,
        boundary_error_by_face=boundary,policy_regret_upper=bounds(regret)[1],seconds=time.perf_counter()-start,
        passed=bool(e<=.002 and eta<=.0002),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        cover_sha256=hashlib.sha256(cover.read_bytes()).hexdigest(),scope='continuous scalar state/action domain',
        assumptions=['mpmath.iv arithmetic correctness','stored binary64 weights are exact real coefficients','stopped diffusion comparison'],
        formal_machine_proof=False)
    OUT.mkdir(parents=True,exist_ok=True);np.savez_compressed(OUT/f'independent_interval_{method}.npz',leaves=new)
    (OUT/f'independent_interval_{method}.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
    return out
if __name__=='__main__':
    import sys
    for method in (sys.argv[1:] or ['nbo','direct']):replay(method)
