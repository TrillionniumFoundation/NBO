"""Validated non-negligible stopping in the unchanged R29 diffusion.

A half-line killed kernel retains the lower boundary exactly. The far upper
boundary and the t=0 truncation have separate analytic error bounds.
"""
from flint import arb,acb,ctx
from pathlib import Path
import argparse,json,time,hashlib
ctx.prec=200
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

DEGREE=128
# Uniform Taylor remainder on |y-2| <= .8. Coefficients are ball-enclosed.
UTILITY_COEFF=[]
v=arb(1); term=arb(1)
for n in range(DEGREE+1):
    if n:
        term*=(-LOGC)/n
        v=term-v
    UTILITY_COEFF.append(-v/C)
UTILITY_REMAINDER=(arb(16)/9)*(arb(4)/5)**(DEGREE+1)/(arb(1)/5)


def moments(t, mean, analytic=False):
    """Noncentral truncated Gaussian moments about y=2; exact recurrence."""
    variance=SIG**2*t;sd=variance.sqrt(analytic=analytic)
    za=(A-mean)/sd;zb=(B-mean)/sd
    m0=((za/arb(2).sqrt()).erfc()-(zb/arb(2).sqrt()).erfc())/2
    da=(-za**2/2).exp()/(sd*SQ2PI);db=(-zb**2/2).exp()/(sd*SQ2PI)
    z=[m0,(mean-2)*m0+variance*(da-db)]
    pa=acb(1);pb=acb(1)
    for n in range(2,DEGREE+3):
        pa*=A-2;pb*=B-2
        z.append((mean-2)*z[-1]+(n-1)*variance*z[-2]+variance*(pa*da-pb*db))
    return z


def payoff_derivative(theta,order):
    stats={'integrand_calls':0}
    image_weight=(-2*theta*(U-A)/SIG**2).exp()
    def outer(s,analytic):
        stats['integrand_calls']+=1
        t=s*s
        if not (s.real>0) or not (wealth(t).real>0):return acb('nan')
        a=moments(t,U+theta*t,analytic)
        b=moments(t,2*A-U+theta*t,analytic)
        z=[aa-image_weight*bb for aa,bb in zip(a,b)]
        x=wealth(t)
        const=-K*theta**2/2+8-arb(1)/20000+arb(1)/500-C/(10*x)-arb(1)/250*x.log(analytic=analytic)+arb(8)/25*(1-t)
        c1=-theta/25;c2=arb(1)/1250
        h=[]
        for shift in range(order+1):
            h.append(sum((coef*z[n+shift] for n,coef in enumerate(UTILITY_COEFF)),acb(0))+const*z[shift]+c1*z[shift+1]+c2*z[shift+2])
        if order==0:ans=h[0]
        else:
            q=2-U-theta*t
            hprime=-K*theta*z[0]-z[1]/25
            if order==1:ans=(h[1]+q*h[0])/SIG**2+hprime
            else:
                hp1=-K*theta*z[1]-z[2]/25
                ans=(h[2]+2*q*h[1]+q**2*h[0])/SIG**4-t/SIG**2*h[0]+2*(hp1+q*hprime)/SIG**2-K*z[0]
        return 2*s*(-R*t).exp()*ans
    cuts=[T0.sqrt(),arb(1)/100,arb(1)/20,arb(1)/10,arb(1)/5,arb(2)/5,arb(4)/5,arb(1)]
    total=acb(0)
    for l,r in zip(cuts,cuts[1:]):
        if l<r:
            part=acb.integral(outer,l,r,abs_tol=arb('1e-6'),rel_tol=arb('1e-6'),eval_limit=30000,depth_limit=35)
            if not part.is_finite():raise ArithmeticError('nonfinite polynomial-moment integral on '+str(l)+' to '+str(r))
            total+=part
    M=arb(20);M1=arb(2);M2=arb(8);_,p=exit_prob(theta)
    if order==0:err=M*T0+M*p+UTILITY_REMAINDER
    elif order==1:err=M1*T0+2*M/(3*SIG)*T0**arb('1.5')+M/SIG*p.sqrt()+M1*p+2*UTILITY_REMAINDER/(3*SIG)
    else:err=M2*T0+4*M1/(3*SIG)*T0**arb('1.5')+M*arb(2).sqrt()/(2*SIG**2)*T0**2+M*arb(2).sqrt()/SIG**2*p.sqrt()+2*M1/SIG*p.sqrt()+M2*p+UTILITY_REMAINDER*arb(2).sqrt()/(2*SIG**2)
    if not total.imag.contains(0):raise ArithmeticError('complex quadrature failed reality check')
    result=total.real+arb(0,err)
    if order==0:result+=-arb(1)/50*(U-2)**2+arb(1)/10*X0.log()-8
    if not result.is_finite():raise ArithmeticError('nonfinite validated integral')
    if result.rad()>arb('0.005'):raise ArithmeticError('enclosure width exceeded practical .01 budget: '+str(result))
    stats['utility_degree']=DEGREE
    stats['utility_remainder']=str(UTILITY_REMAINDER)
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
