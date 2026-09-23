"""Centered second-order certificates for fixed R25 policies; no retraining."""
from __future__ import annotations
from fractions import Fraction as F
import hashlib, importlib.util, json, math, sys, time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]; REV=ROOT/'revisions/2026-09-23-r26'
spec=importlib.util.spec_from_file_location('r25_reference',ROOT/'revisions/2026-09-23-r25/replication/stochastic_reference.py')
S=importlib.util.module_from_spec(spec);sys.modules[spec.name]=S;spec.loader.exec_module(S)
IA,I,Q=S.IA,S.I,S.Q
PAIRS=((0,0),(0,1),(0,2),(1,1),(1,2),(2,2))
def write(p:Path,x:object)->None:
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def neural_jet(s:I,layers:list[dict],second:bool=True):
    n=s.lo.shape[0];t,x,z=s[:,0],s[:,1],s[:,2]
    v=IA.stack([2*t-1,(x-Q('1.25'))/Q('.75'),z],axis=-1)
    g=np.zeros((n,3,3))
    for k in range(3):g[:,k,k]=1
    g=I(g)*IA.stack([I(2),1/Q('.75'),I(1)])
    h=I(np.zeros((n,6,3))) if second else None
    for k,l in enumerate(layers):
        w=np.asarray(l['w']);v=IA.affine(v,w,np.asarray(l['b']));g=IA.affine(g,w)
        if second:h=IA.affine(h,w)
        if k<len(layers)-1:
            v=IA.tanh(v);fp=(1-v.square()).intersect(0,1);fpp=-2*v*fp
        else:
            v=1/(1+IA.exp(-v));fp=(v*(1-v)).intersect(0,.25);fpp=fp*(1-2*v)
        if second:
            products=IA.stack([g[:,i,:]*g[:,j,:] for i,j in PAIRS],axis=1)
            h=h*fp[:,None,:]+products*fpp[:,None,:]
        g=g*fp[:,None,:]
    scales=IA.stack([Q('2.2'),I(1)])
    return v*scales,g*scales,None if h is None else h*scales

def exact_jet(s:I,second:bool=True):
    v,der=S.exact_interval(s);g=IA.stack(der,axis=1)
    if not second:return v,g,None
    t,x,z=s[:,0],s[:,1],s[:,2];A=Q('.8')+Q('.2')*t;zero=I(np.zeros(t.lo.shape));const=zero+Q('.064')
    aa=[zero,-Q('.2')/x.square(),zero+Q('.02'),2*A/(x*x*x),zero,zero]
    pp=[zero,zero,zero,zero,const,zero]
    h=IA.stack([IA.stack([a,p],axis=-1) for a,p in zip(aa,pp)],axis=1)
    return v,g,h

def cell_errors(lo:np.ndarray,hi:np.ndarray,layers:list[dict]):
    center=(lo+hi)/2;radius=(hi-lo)/2;box,mid=I(lo,hi),I(center)
    _,gb,hb=neural_jet(box,layers);_,ge,he=exact_jet(box)
    vm,gm,_=neural_jet(mid,layers,False);ve,gme,_=exact_jet(mid,False)
    err0=I((vm-ve).maxabs());first=err0;second=err0
    for i in range(3):
        r=I(radius[:,i:i+1]);first=first+I((gb[:,i,:]-ge[:,i,:]).maxabs())*r
        second=second+I((gm[:,i,:]-gme[:,i,:]).maxabs())*r
    for k,(i,j) in enumerate(PAIRS):
        term=I((hb[:,k,:]-he[:,k,:]).maxabs())*I(radius[:,i:i+1])*I(radius[:,j:j+1])
        second=second+term/(2 if i==j else 1)
    return first.hi,second.hi,np.minimum(first.hi,second.hi)

def verify(seed:int)->dict:
    source=ROOT/f'revisions/2026-09-23-r25/results/stochastic_reference/neural{seed}/fit.json'
    fit=json.loads(source.read_text());path=REV/f'results/jets/neural{seed}';start=time.perf_counter();attempts=[]
    for shape in ((4,16,8),(8,32,16),(16,64,32)):
        tic=time.perf_counter();lo,hi=S.cover(shape);one=[];two=[];mins=[]
        for a in range(0,len(lo),512):
            sl=slice(a,a+512);x,y,z=cell_errors(lo[sl],hi[sl],fit['layers']);one.append(x);two.append(y);mins.append(z)
        one,two,err=np.concatenate(one),np.concatenate(two),np.concatenate(mins)
        A=Q('.8')+Q('.2')*I(lo[:,0],hi[:,0]);ei=I(err)
        deficit=(ei[:,0].square()+Q('.0625')*A*ei[:,1].square())/2
        e1=I(one);d1=(e1[:,0].square()+Q('.0625')*A*e1[:,1].square())/2
        C=(1-IA.exp(-Q('.04')))/Q('.04');bound=float((C*I(float(deficit.hi.max()))).hi)
        first_bound=float((C*I(float(d1.hi.max()))).hi)
        p=path/('cells_'+'_'.join(map(str,shape))+'.npz');p.parent.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(p,lower=lo,upper=hi,first_error_upper=one,second_error_upper=two,error_upper=err,deficit_upper=deficit.hi)
        row={'shape':list(shape),'cells':len(lo),'first_order_regret_upper_same_cells':first_bound,'regret_upper':bound,
             'deficit_upper':float(deficit.hi.max()),'seconds':time.perf_counter()-tic,'complete_cover':True,'failed_cells':0,
             'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        attempts.append(row);print('JET',seed,shape,first_bound,bound,flush=True)
        if bound<=.001:break
    out={'seed':seed,'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'policy_unchanged':True,'economy':'manufactured unspanned-risk stopped investment','is_original_economy':False,
         'target':.001,'target_established':bound<=.001,'attempts':attempts,'regret_upper':bound,
         'verification_seconds':time.perf_counter()-start,'floating_weights_treated_as_exact':True,
         'decoder_constants':'exact displayed rational constants; real-valued deployment',
         'restart_upper':[{'t':t,'upper':0. if t==1 else float(((1-IA.exp(-Q('.04')*(1-I(t))))/Q('.04')*I(row['deficit_upper'])).hi)} for t in (0,.25,.5,.75,1)]}
    write(path/'certificate.json',out);return out

def polynomial_mul(a:list[F],b:list[F])->list[F]:
    c=[F(0)]*(len(a)+len(b)-1)
    for i,u in enumerate(a):
        for j,v in enumerate(b):c[i+j]+=u*v
    return c

def bernstein_local(coef:list[F],a:F,b:F)->list[F]:
    """Exact power-to-Bernstein transform on xi=a+(b-a)s, 0<=s<=1."""
    n=len(coef)-1;power=[F(0)]*(n+1)
    for j,c in enumerate(coef):
        for k in range(j+1):power[k]+=c*math.comb(j,k)*a**(j-k)*(b-a)**k
    return [sum((power[k]*F(math.comb(i,k),math.comb(n,k)) for k in range(i+1)),F(0)) for i in range(n+1)]

def direct_certificate()->dict:
    start=time.perf_counter();source=ROOT/'revisions/2026-09-23-r25/results/stochastic_reference/direct/fit.json'
    fit=json.loads(source.read_text());p=[F(float(x)) for x in fit['coefficients']]
    residual=polynomial_mul(p,[F(5,4),F(3,4)]);residual[0]-=1
    rows=[];worst=F(0)
    for j in range(64):
        a,b=F(-1)+F(j,32),F(-1)+F(j+1,32);beta=bernstein_local(residual,a,b)
        minx=(5+3*a)/4;error=max(abs(min(beta)),abs(max(beta)))/minx;worst=max(worst,error)
        rows.append({'xi':[str(a),str(b)],'bernstein_coefficients':[str(x) for x in beta],'reciprocal_error_upper':str(error)})
    D=Q(worst).square()/2;C=(1-IA.exp(-Q('.04')))/Q('.04');bound=float((C*D).hi)
    out={'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'policy_unchanged':True,'proof':'exact rational Bernstein convex hull for xP-1 divided by positive x',
         'portfolio_error_exactly_zero':True,'action_error_rational_upper':str(worst),
         'regret_upper':bound,'cells_x':64,'uniform_all_state_time':True,'projection_nonexpansive':True,
         'is_original_economy':False,'verification_seconds':time.perf_counter()-start,'cells':rows}
    write(REV/'results/jets/direct_exact.json',out);print('BERNSTEIN',bound,flush=True);return out

def main():
    results=[verify(s) for s in (25201,25202)];direct=direct_certificate()
    write(REV/'results/jet_summary.json',{'neural':results,'direct':direct})
if __name__=='__main__':main()
