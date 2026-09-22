"""Second implementation of the full affine-preference dual certificate.

Independent arithmetic, analytic source formulas, interval automatic Hessians,
and rational-root Gauss moment integration. No historical certifier imports.
The shared mathematical supporting-plane/variance/localization theorem is
explicitly a trusted analytic input, with its finite primitive tests rerun here.
"""
from __future__ import annotations
import argparse,json,time,hashlib
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from interval64 import I,exp,log,add_reduce,stack,exact_clip
from validated_gauss import Q,sqrt,weighted_moments
ROOT=Path(__file__).resolve().parents[3]

class J:
    def __init__(self,v,d0=0,d1=0,h00=0,h01=0,h11=0):
        self.a=[x if isinstance(x,I) else I(x) for x in (v,d0,d1,h00,h01,h11)]
    def __add__(self,b):
        b=jj(b);return J(*[a+c for a,c in zip(self.a,b.a)])
    __radd__=__add__
    def __neg__(self):return J(*[-a for a in self.a])
    def __sub__(self,b):return self+-jj(b)
    def __rsub__(self,b):return jj(b)+-self
    def __mul__(self,b):
        a,au,al,auu,aul,all_=self.a;b,bu,bl,buu,bul,bll=jj(b).a
        return J(a*b,au*b+a*bu,al*b+a*bl,auu*b+2*au*bu+a*buu,aul*b+au*bl+al*bu+a*bul,all_*b+2*al*bl+a*bll)
    __rmul__=__mul__
    def compose(self,v,d,dd):
        _,a,b,aa,ab,bb=self.a
        return J(v,d*a,d*b,dd*a.square()+d*aa,dd*a*b+d*ab,dd*b.square()+d*bb)
    def inverse(self):
        v=self.a[0];return self.compose(1/v,-1/v.square(),2/(v.square()*v))
    def __truediv__(self,b):return self*jj(b).inverse()
    def __rtruediv__(self,b):return jj(b)*self.inverse()

def jj(x):return x if isinstance(x,J) else J(x)
def ej(a):
    a=jj(a);v=exp(a.a[0]);return a.compose(v,v,v)

def source(u,l):
    U=J(u,1,0);L=J(l,0,1);r=U-1;y=ej(L)
    cap=-ej(-r*log(Q('.8')))/r-y*Q('.8')
    interior=-U/r*ej(r/U*L)
    constant=y*Q('.01')-Q('.004')*log(Q('.5'))
    cap=cap+constant;interior=interior+constant
    cut=u*(-log(Q('.8')));onlycap=l.hi<cut.lo;onlyint=l.lo>cut.hi
    arr=[]
    for a,b in zip(cap.a,interior.a):
        lo=np.minimum(a.lo,b.lo);hi=np.maximum(a.hi,b.hi)
        lo=np.where(onlycap,a.lo,np.where(onlyint,b.lo,lo));hi=np.where(onlycap,a.hi,np.where(onlyint,b.hi,hi))
        arr.append(I(lo,hi))
    return arr

def primitives():
    def cover(a,b,n):
        return I([float(Q(F(a)+(F(b)-F(a))*F(i,n)).lo) for i in range(n)],
                 [float(Q(F(a)+(F(b)-F(a))*F(i+1,n)).hi) for i in range(n)])
    u=cover('1.5','2.3',1600);h=float(source(u,log(Q(12)))[3].hi.max())
    u=cover('2.3','2.5',2000);b=float(source(u,log(Q(12)))[1].hi.max());left=float(source(Q('2.2'),log(Q(12)))[1].lo)
    m=cover('2','2.2',1000);vals12=source(m,log(Q(12)));vals02=source(m,log(Q('.2')))
    floor=float(vals12[0].lo.min());ceiling=float(vals02[0].hi.max());beta=float(max(vals12[1].maxabs().max(),vals02[1].maxabs().max()))
    continuation=-Q('7.1')-Q('1.1')*Q('.75')-Q('.04')*Q('.0068')
    assert h<0 and b<left and floor>-7.1 and ceiling<0 and beta<1.1 and continuation.lo>-8
    return {'status':'PASS','Huu_upper':h,'beta_upper_high_u':b,'beta_lower_at_2.2':left,'source_floor':floor,
      'source_ceiling':ceiling,'beta_absolute_bound':beta,'continuation_floor':continuation.pair(),
      'complete_cover_counts':[1600,2000,1000],'production_certifier_imports':False,
      'analytic_dependencies':'The displayed monotonicity identities and stopped dual/localization theorem, proved in the supplement.'}

def gap(q,theta,k):
    q=I(q);a=exact_clip(q/Q(k),'-.2','.2')
    g=q*a-Q(k)/2*a.square()-q*theta+Q(k)/2*theta.square()
    return max(0,float(g.hi))

def run(pilot,k,ns=16,nz=256,robust=False):
    clock=time.perf_counter();d=json.loads(Path(pilot).read_text());y0=I(d['y0']);theta=I(np.asarray(d['theta'],float));n=len(theta.lo)
    assert y0.lo>Q('1.2').hi and y0.hi<Q('2.4').lo
    assert np.all(theta.lo>=0) and np.all(theta.hi<=Q('.2').lo)
    mu=I(0);mleft=[]
    for j in range(n):mleft.append(mu);mu=mu+theta[j]/n
    ml=stack(mleft);M=log(y0);bT=-Q('.04')*mu
    terminal=-Q('.02')*mu.square()*exp(-Q('.04'));base=Q('.75')*y0+Q('.1')*log(Q('.5'))
    Z=16*exp(-Q(18))+8*(exp(-22*log(y0/Q('.2'))+Q('22.33'))+exp(-22*log(Q(12)/y0)+Q('22.33')))
    aa=Q(F(12,11));D2=exp(aa*M+aa.square()*Q('.09')/2)*((M+aa*Q('.09')).square()+Q('.09'))/16
    variance=Q('.09')*D2/(24*Q(k));tail=2*exp(-Q(18))
    floor=Q('7.11' if robust else '7.1'); beta_bound=Q('1.11' if robust else '1.1')
    assert (-floor-beta_bound*Q('.75')-Q('.04')*Q('.0068')).lo>-8
    if robust:variance=variance*Q('1.1');tail=2*tail
    vl=[];vr=[];slabs=[]
    for j in range(n):
        a,b=sqrt(Q(F(j,n))),sqrt(Q(F(j+1,n)))
        for h in range(ns):vl.append(a+(b-a)*Q(F(h,ns)));vr.append(a+(b-a)*Q(F(h+1,ns)));slabs.append(j)
    vl,vr=stack(vl),stack(vr);vc=I((vl.lo+vr.hi)/2);vbox=I(np.maximum(0,vl.lo),vr.hi)
    rz=Q(F(6,nz));zl=stack([Q(-6+F(12*i,nz)) for i in range(nz)]);zr=stack([Q(-6+F(12*(i+1),nz)) for i in range(nz)]);zc=I((zl.lo+zr.hi)/2);zbox=I(zl.lo,zr.hi)
    mv=weighted_moments(vl,vr,vc,'v');mz=weighted_moments(zl,zr,zc,'z');nt=len(slabs)
    def broadcast(v,z):return I(np.repeat(v.lo,nz),np.repeat(v.hi,nz)),I(np.tile(z.lo,nt),np.tile(z.hi,nt))
    sl=np.repeat(np.array(slabs),nz);th=I(theta.lo[sl],theta.hi[sl]);um=I(ml.lo[sl],ml.hi[sl]);left=Q(F(1,n))*I(sl)
    def evaluate(V,Z):
        u=2+um+th*(V.square()-left);l=M-Q('.025')*V.square()-Q('.3')*V*Z
        if np.min(l.lo)<log(Q('.2')).lo or np.max(l.hi)>log(Q(12)).hi:raise ArithmeticError('Clipping face enters source cover')
        S,B,Sl,Huu,Hul,Hll=source(u,l)
        uv=2*th*V;lv=-Q('.05')*V-Q('.3')*Z;lz=-Q('.3')*V
        Sv=B*uv+Sl*lv;Sz=Sl*lz
        Hvv=Huu*uv.square()+2*Hul*uv*lv+Hll*lv.square()+B*2*th-Sl*Q('.05')
        Hvz=Hul*uv*lz+Hll*lv*lz-Sl*Q('.3');Hzz=Hll*lz.square()
        return S,B,Sv,Sz,Hvv,Hvz,Hzz,Hul
    V,Zc=broadcast(vc,zc);val=evaluate(V,Zc)
    VB,ZB=broadcast(vbox,zbox);box=evaluate(VB,ZB)
    mvv=[I(np.repeat(v.lo,nz),np.repeat(v.hi,nz)) for v in mv];mzz=[I(np.tile(z.lo,nt),np.tile(z.hi,nt)) for z in mz]
    mass=mvv[0]*mzz[0];S,B,Sv,Sz,*_=val
    approx=add_reduce(S*mass+Sv*mvv[1]*mzz[0]+Sz*mvv[0]*mzz[1])
    radv=I(np.maximum(vc.lo-vl.lo,vr.hi-vc.hi));rv=I(np.repeat(np.nextafter(radv.hi,np.inf),nz))
    rem=add_reduce(I(box[4].maxabs())/2*mvv[2]*mzz[0]+I(box[5].maxabs())*rv*rz*mass+I(box[6].maxabs())/2*mvv[0]*mzz[2])
    integ=approx+I(-rem.hi,rem.hi)+I(float((-floor*tail*(1-exp(-Q('.04')))/Q('.04')).lo),0)
    cov=add_reduce(Q('.00375')*VB.square()*box[7]*mass)+I(-float((Q('.00375')*Q('2.5')*tail/2).hi),0)
    assert cov.hi<0
    BB=box[1].reshape(nt,nz);gaussmass=mz[0].reshape(1,nz)
    beta_range=add_reduce(BB*gaussmass,axis=-1)+I(-float((beta_bound*tail).hi),float((beta_bound*tail).hi))
    beta_integral=beta_range*mv[0]
    future=exp(-Q('.04'))*bT;g=I(0)
    for j in range(nt-1,-1,-1):
        partial=beta_range[j]*I(0,mv[0].hi[j])
        qq=(future+partial)*exp(Q('.04')*vbox[j].square())
        qgap=max(gap(float(qq.lo),theta[slabs[j]],k),gap(float(qq.hi),theta[slabs[j]],k))
        g=g+I(qgap)*mv[0][j];future=future+beta_integral[j]
    cost=I(0)
    for j in range(n):
        cost=cost+Q(k)/2*theta[j].square()*(exp(-Q('.04')*Q(F(j,n)))-exp(-Q('.04')*Q(F(j+1,n))))/Q('.04')
    upper=base+terminal-cost+integ+cov+I(g.hi)+variance+Z
    result={'status':'VALID_UPPER_BOUND','k':float(F(k)),'pilot_path':str(Path(pilot).resolve().relative_to(ROOT)),
      'pilot_sha256':hashlib.sha256(Path(pilot).read_bytes()).hexdigest(),'method':'independent automatic source Hessians and rational-root Gauss weight moments',
      'time_subcells_per_slab':ns,'time_cells':nt,'normal_cells':nz,'source_boxes':nt*nz,
      'source_integral_interval':integ.pair(),'source_remainder_upper':float(rem.hi),'covariance_interval':cov.pair(),
      'control_gap_upper':float(g.hi),'variance_allowance':variance.pair(),'localization':Z.pair(),
      'optimal_value_upper':float(upper.hi),'b0_interval':future.pair(),'y0':d['y0'],'terminal_tangent':terminal.pair(),
      'robust_primitive_test':robust,'initial_state':[0,2,1.25],'seconds':time.perf_counter()-clock,'production_certifier_imports':False,
      'arithmetic':'standalone rational Taylor binary64 intervals; rational Gauss root signs; interval automatic differentiation',
      'scope':'Upper bound over all original continuous adapted controls; affine-preference mathematical dual retained'}
    return result

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--pilot',type=Path);a.add_argument('--k');a.add_argument('--out',type=Path,required=True);a.add_argument('--ns',type=int,default=16);a.add_argument('--nz',type=int,default=256);a.add_argument('--primitives',action='store_true');a.add_argument('--robust',action='store_true');v=a.parse_args()
    r=primitives() if v.primitives else run(v.pilot,v.k,v.ns,v.nz,v.robust);v.out.parent.mkdir(parents=True,exist_ok=True);v.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
