"""Production exact finite-cover fallback, kept separate from independent94.

This deliberately conservative totalization is charged if entered. The
primary report records its actual frequency, never presumed zero.
"""
from fractions import Fraction as F
import math


def primitive(x, a, alpha):
    d = len(x); b = [F(1, 2) if j % 2 == 0 else F(1, 4) for j in range(d)]
    s = [1 if j % 2 == 0 else -1 for j in range(d)]
    def cost(y, terminal=False):
        return (F(4 if terminal else 2, d)*sum((v-F(5,8))**2 for v in y)
                + sum((y[j]-y[(j+1)%d])**2 for j in range(d))/F(4*d)
                + 2*max(F(0), F(1,2)-2*sum(y)/d)**2)
    y = [F(1,16)+x[j]/2+x[(j+1)%d]/8+x[j]*(1-x[(j+1)%d])/16+b[j]*a for j in range(d)]
    D = F(10,d)*sum(y[j]*s[j] for j in range(d)); R = F(1,32); L=2*R*alpha
    z = max(-R, min(R-L, -D/10-L/2))
    m1 = -L*(2*z+L)/(2*(2*R-L))
    m2 = (2*R**3-L*(3*z*z+3*z*L+L*L))/(3*(2*R-L))
    g = [F(8,d)*(y[j]-F(5,8))+(2*y[j]-y[(j-1)%d]-y[(j+1)%d])/F(2*d)
         - F(8,d)*max(F(0),F(1,2)-2*sum(y)/d)+F(10,d)*m1*s[j] for j in range(d)]
    value = cost(x)+a*a+4*a**4+F(15,16)*(cost(y, True)+D*m1+5*m2)
    grad = 2*a+16*a**3+F(15,16)*sum(g[j]*b[j] for j in range(d))
    return value, grad


def terminal(x, alpha):
    cap = F(1,8)+sum(x)/F(8*len(x)); lo, hi=F(0),cap
    for _ in range(80):
        a=(lo+hi)/2; v,g=primitive(x,a,alpha)
        delta=max(-a,min(cap-a,-g/2)); lower=v+g*delta+delta*delta
        if v-lower <= F(1,2**30):
            return lower,v
        if g < 0: lo=a
        else: hi=a
    raise ArithmeticError('Exact terminal bisection failed its primitive bound')


def exact_cost(x, a, alpha, bins):
    d=len(x); R=F(1,32)
    def succ(z):
        return [F(1,16)+x[j]/2+x[(j+1)%d]/8+x[j]*(1-x[(j+1)%d])/16
                +(F(1,2) if j%2==0 else F(1,4))*a+(1 if j%2==0 else -1)*z for j in range(d)]
    mid=[terminal(succ(-R+(2*j+1)*R/bins),alpha)[0] for j in range(bins)]
    end=[terminal(succ(-R+2*j*R/bins),alpha)[1] for j in range(bins+1)]
    endpoints=[v for j in range(bins) for v in (end[j],end[j+1])]
    def tail(v):
        k=int(len(v)*(1-alpha));return sum(sorted(v)[-k:])/k
    base=F(2,d)*sum((v-F(5,8))**2 for v in x)+sum((x[j]-x[(j+1)%d])**2 for j in range(d))/F(4*d)+2*max(F(0),F(1,2)-2*sum(x)/d)**2+a*a+4*a**4
    return base+F(15,16)*tail(mid),base+F(15,16)*(tail(endpoints)+F(1,2**20))


def exact_service(state, alpha):
    x=list(map(lambda v:F(float(v)),state));alpha=F(float(alpha))
    cap=F(1,8)+sum(x)/F(8*len(x));m=1024;n=256
    values=[exact_cost(x, cap*j/m, alpha, n) for j in range(m+1)]
    j=min(range(m+1),key=lambda k:(values[k][1],k))
    lower_optimum=min(v[0] for v in values)-F(7,8*m)
    a=cap*j/m;low,high=values[j]
    # The realized binary action is rounded down; charge that perturbation.
    realized=F(math.floor(a*2**40),2**40);pad=7*abs(a-realized)
    low-=pad;high+=pad
    if high-lower_optimum > F(1,256) or high-low > F(1,8192):
        raise ArithmeticError('Exact finite-cover constants contradicted')
    import numpy as np
    return (float(realized),float(np.nextafter(float(low),-np.inf)),
            float(np.nextafter(float(high),np.inf)),
            float(np.nextafter(float(lower_optimum),-np.inf)),n)
