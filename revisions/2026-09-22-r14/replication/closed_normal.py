"""Closed truncated-lognormal formulas for a distinct dual cross-check/pilot.
NumPy/SciPy values are proposals/diagnostics, never interval certificates.
"""
import numpy as np
from scipy.special import ndtr

def moments(t,m,y0):
    t=np.asarray(t,float);m=np.asarray(m,float);mu=np.log(y0)-.025*t;v=.09*t;s=np.sqrt(v)
    if np.any(s<=0):raise ValueError('Use interior quadrature nodes t>0')
    r=m-1;q=r/m;lo=np.log(.2);hi=np.log(12.);a=-m*np.log(.8)
    def cdf(l):return ndtr((l-mu)/s)
    def emom(q,a,b):
        z1=(a-mu-q*v)/s;z2=(b-mu-q*v)/s;ee=np.exp(q*mu+q*q*v/2)
        val=ee*(ndtr(z2)-ndtr(z1))
        first=(mu+q*v)*val+s*ee*(np.exp(-z1*z1/2)-np.exp(-z2*z2/2))/np.sqrt(2*np.pi)
        return val,first
    ya=.2*cdf(lo)+emom(1,lo,a)[0];ey=.2*cdf(lo)+emom(1,lo,hi)[0]+12*(1-cdf(hi))
    mq,mq1=emom(q,a,hi);pcap=cdf(a);phigh=1-cdf(hi)
    es=-.8**(-r)/r*pcap-.8*ya-m/r*mq-m/r*12**q*phigh+.01*ey-.004*np.log(.5)
    bc=.8**(-r)*(1+r*np.log(.8))/r**2;bh=12**q*(1-q*np.log(12))/r**2
    beta=bc*pcap+(mq-q*mq1)/r**2+bh*phigh;bl=-mq1/m**2
    return es,beta,bl
