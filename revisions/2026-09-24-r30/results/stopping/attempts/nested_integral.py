"""Validated non-negligible stopping in the unchanged R29 diffusion.

A half-line killed kernel retains the lower boundary exactly. The far upper
boundary and the t=0 truncation have separate analytic error bounds.
"""
from flint import arb,acb,ctx
from pathlib import Path
import argparse,json,time,hashlib
ctx.prec=90
A=arb(6)/5; B=arb(14)/5; U=arb(61)/50; SIG=arb(1)/20
C=arb(3)/4; X0=arb(5)/4; R=arb(1)/25; K=arb(2); T0=arb('0.000001')
SQ2PI=(2*arb.pi()).sqrt(); LOGC=C.log()
OUT=Path(__file__).resolve().parents[1]/'results/stopping'

def record(x):
    return {'ball':x.str(18),'lo':x.lower().str(22),'hi':x.upper().str(22),'radius':x.rad().str(10)}
def wealth(t):return (X0-C/(arb(1)/50))*((arb(1)/50)*t).exp()+C/(arb(1)/50)
def exit_prob(theta):
    d=U-A;z1=(d+theta)/SIG;z2=(-d+theta)/SIG
    phi=lambda z:(z/(arb(2).sqrt())).erfc()/2
    # lower-boundary hitting probability by time one
    hit=phi(z1)+(-2*theta*d/SIG**2).exp()*phi(-z2)
    # Probability of upper exit without conditioning on lower survival.
    opposite=2*(-(B-U-arb(1)/5)**2/(2*SIG**2)).exp()
    return hit+arb(0,opposite),opposite

def dynkin_integrand(t,y,theta,order,analytic=False):
    x=wealth(t);g=-arb(1)/50*(y-2)**2+arb(1)/10*x.log(analytic=analytic)
    h=((1-y)*LOGC).exp()/(1-y)-K*theta**2/2+8-arb(1)/25*theta*(y-2)-arb(1)/20000+arb(1)/500-C/(10*x)-R*g+arb(8)/25*(1-t)
    score=(y-U-theta*t)/(SIG**2)
    first=-K*theta-(y-2)/25
    if order==1:h=score*h+first
    elif order==2:h=(score**2-t/SIG**2)*h+2*score*first-K
    density=(-(y-U-theta*t)**2/(2*SIG**2*t)).exp()/(SIG*t.sqrt(analytic=analytic)*SQ2PI)
    absorb=-(-2*(U-A)*(y-A)/(SIG**2*t)).expm1()
    return density*absorb*h

def payoff_derivative(theta,order):
    stats={'point_calls':0,'enclosure_calls':0}
    def outer(s,analytic):
        t=s*s
        if not (s.real>0) or not (wealth(t).real>0):return acb('nan')
        # Analytic enclosures use fixed interval integration in y. Point calls
        # use rigorous adaptive Gauss integration. No decimal quadrature is
        # ever promoted to an enclosure.
        large=float(s.real.rad())+float(s.imag.rad())>1e-12
        if large:
            stats['enclosure_calls']+=1;z=acb(0)
            for i in range(64):
                l=A+(B-A)*i/64;r=A+(B-A)*(i+1)/64
                y=acb(arb((l+r)/2,(r-l)/2))
                z+=dynkin_integrand(t,y,theta,order,analytic)*(r-l)
        else:
            stats['point_calls']+=1
            z=acb.integral(lambda y,an:dynkin_integrand(t,y,theta,order,an),A,B,
                           abs_tol=arb('1e-13'),rel_tol=arb('1e-13'),eval_limit=12000,depth_limit=35)
        return 2*s*(-R*t).exp()*z
    cuts=[T0.sqrt(),arb(1)/100,arb(1)/20,arb(1)/10,arb(1)/5,arb(2)/5,arb(4)/5,arb(1)]
    total=acb(0)
    for l,r in zip(cuts,cuts[1:]):
        if l<r:
            total+=acb.integral(outer,l,r,abs_tol=arb('1e-7'),rel_tol=arb('1e-7'),eval_limit=12000,depth_limit=30)
    M=arb(20);M1=arb(2);M2=arb(8);_,p=exit_prob(theta)
    if order==0:err=M*T0+M*p
    elif order==1:err=M1*T0+2*M/(3*SIG)*T0**arb('1.5')+M/SIG*p.sqrt()+M1*p
    else:err=M2*T0+4*M1/(3*SIG)*T0**arb('1.5')+M*arb(2).sqrt()/(2*SIG**2)*T0**2+M*arb(2).sqrt()/SIG**2*p.sqrt()+2*M1/SIG*p.sqrt()+M2*p
    result=total.real+arb(0,err)
    if order==0:result+=-arb(1)/50*(U-2)**2+arb(1)/10*X0.log()-8
    if not result.is_finite():raise ArithmeticError('nonfinite validated integral')
    return result,err,stats

def main():
    pa=argparse.ArgumentParser();pa.add_argument('--theta',default=None);pa.add_argument('--order',type=int,default=None);args=pa.parse_args()
    OUT.mkdir(exist_ok=True,parents=True)
    ts=[args.theta] if args.theta is not None else ['-0.2','-0.1','0','0.1','0.2']
    orders=[args.order] if args.order is not None else [0,1,2]
    for text in ts:
        theta=arb(text);p,upper=exit_prob(theta)
        row={'theta':text,'exit_probability':record(p),'opposite_boundary_probability_upper':record(upper),'derivatives':{},'time_cutoff':str(T0),'precision_bits':ctx.prec}
        for j in orders:
            start=time.perf_counter()
            try:
                v,e,stats=payoff_derivative(theta,j);row['derivatives'][str(j)]={'enclosure':record(v),'analytic_remainder':record(e),'seconds':time.perf_counter()-start,**stats}
                print(text,j,v,'seconds',time.perf_counter()-start,flush=True)
            except Exception as exc:
                row['derivatives'][str(j)]={'error':repr(exc),'seconds':time.perf_counter()-start};print('UNRESOLVED',text,j,repr(exc),flush=True)
        row['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        suffix='' if args.order is None else '_order'+str(args.order)
        (OUT/(text.replace('-','minus').replace('.','p')+suffix+'.json')).write_text(json.dumps(row,indent=2)+'\n')

if __name__=='__main__':main()
