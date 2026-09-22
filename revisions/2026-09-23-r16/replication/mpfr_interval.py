"""MPFR-directed interval backend; independent elementary and basic arithmetic.
Shared with R14: analytic dual/primal formulas and rational quadrature proof.
This is a numerical cross-check, not a formal proof of the shared mathematics.
"""
from pathlib import Path
from fractions import Fraction
import ctypes as C, subprocess, math
import numpy as np
HERE=Path(__file__).resolve().parent
SO=HERE/'mpfr_bridge.so'
if not SO.exists() or SO.stat().st_mtime<(HERE/'mpfr_bridge.c').stat().st_mtime:
    subprocess.run(['gcc','-O2','-std=c11','-shared','-fPIC',str(HERE/'mpfr_bridge.c'),'-Wl,-l:libmpfr.so.6','-o',str(SO)],check=True)
lib=C.CDLL(str(SO));lib.version.restype=C.c_char_p
VERSION=lib.version().decode()
ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
lib.unary.argtypes=[C.c_int,C.c_size_t,ptr,ptr,C.c_int]
lib.binary.argtypes=[C.c_int,C.c_size_t,ptr,ptr,ptr,C.c_int]
def unary(op,a,upper):
    a=np.asarray(a,float);shape=a.shape;a=np.ascontiguousarray(a.reshape(-1));out=np.empty_like(a)
    if lib.unary(op,len(a),a,out,int(upper)):raise ArithmeticError('MPFR unary failure')
    if not np.isfinite(out).all():raise ArithmeticError('MPFR nonfinite endpoint')
    return out.reshape(shape)
def binary(op,a,b,upper):
    a,b=np.broadcast_arrays(a,b);shape=a.shape;a=np.ascontiguousarray(a.reshape(-1));b=np.ascontiguousarray(b.reshape(-1));out=np.empty_like(a)
    if lib.binary(op,len(a),a,b,out,int(upper)):raise ArithmeticError('MPFR binary failure')
    if not np.isfinite(out).all():raise ArithmeticError('MPFR nonfinite endpoint')
    return out.reshape(shape)
def down(x):return np.nextafter(x,-np.inf)
def up(x):return np.nextafter(x,np.inf)
class I:
    def __init__(self,lo,hi=None):
        self.lo=np.asarray(lo,float);self.hi=np.asarray(lo if hi is None else hi,float)
        if np.any(self.lo>self.hi) or not (np.isfinite(self.lo).all() and np.isfinite(self.hi).all()):raise ArithmeticError('Invalid interval')
    @staticmethod
    def rational(x):
        q=Fraction(x);f=float(q)
        return I(math.nextafter(f,-math.inf) if Fraction(f)>q else f,math.nextafter(f,math.inf) if Fraction(f)<q else f)
    def __add__(self,b):
        b=as_i(b);return I(binary(0,self.lo,b.lo,False),binary(0,self.hi,b.hi,True))
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,b):return self+-as_i(b)
    def __rsub__(self,b):return as_i(b)+-self
    def __mul__(self,b):
        b=as_i(b);pairs=[(self.lo,b.lo),(self.lo,b.hi),(self.hi,b.lo),(self.hi,b.hi)]
        return I(np.minimum.reduce([binary(1,a,c,False) for a,c in pairs]),np.maximum.reduce([binary(1,a,c,True) for a,c in pairs]))
    __rmul__=__mul__
    def __truediv__(self,b):
        b=as_i(b)
        if np.any((b.lo<=0)&(b.hi>=0)):raise ArithmeticError('Division through zero')
        return self*I(binary(2,1.,b.hi,False),binary(2,1.,b.lo,True))
    def __rtruediv__(self,b):return as_i(b)/self
    def square(self):
        lo=np.minimum(binary(1,self.lo,self.lo,False),binary(1,self.hi,self.hi,False))
        hi=np.maximum(binary(1,self.lo,self.lo,True),binary(1,self.hi,self.hi,True))
        return I(np.where((self.lo<=0)&(self.hi>=0),0,lo),hi)
    def __pow__(self,n):
        if not isinstance(n,int) or n<0:raise ValueError('Nonnegative integer powers only')
        z=I(1);a=self
        while n:
            if n&1:z=z*a
            n//=2
            if n:a=a.square()
        return z
    def __getitem__(self,k):return I(self.lo[k],self.hi[k])
    def reshape(self,*s):return I(self.lo.reshape(*s),self.hi.reshape(*s))
    def maxabs(self):return np.maximum(abs(self.lo),abs(self.hi))
    def pair(self):return [float(self.lo),float(self.hi)]
    def clip(self,lo,hi):return I(np.clip(self.lo,lo,hi),np.clip(self.hi,lo,hi))
    def intersect(self,lo,hi):return I(np.maximum(self.lo,lo),np.minimum(self.hi,hi))
def as_i(x):return x if isinstance(x,I) else I(x)
def exp(a):
    a=as_i(a);return I(unary(0,a.lo,False),unary(0,a.hi,True))
def log(a):
    a=as_i(a)
    if np.any(a.lo<=0):raise ArithmeticError('Log domain')
    return I(unary(1,a.lo,False),unary(1,a.hi,True))
def tanh(a):
    a=as_i(a);return I(unary(2,a.lo,False),unary(2,a.hi,True))
def sqrt(a):
    a=as_i(a)
    if np.any(a.lo<0):raise ArithmeticError('Sqrt domain')
    return I(unary(3,a.lo,False),unary(3,a.hi,True))
def cat(xs,axis=0):return I(np.concatenate([x.lo for x in xs],axis),np.concatenate([x.hi for x in xs],axis))
def stack(xs,axis=0):return I(np.stack([x.lo for x in xs],axis),np.stack([x.hi for x in xs],axis))
def add_reduce(a,axis=0):
    a=I(np.moveaxis(a.lo,axis,0),np.moveaxis(a.hi,axis,0))
    while len(a.lo)>1:
        n=len(a.lo)//2;z=a[:2*n:2]+a[1:2*n:2]
        a=cat([z,a[-1:]]) if len(a.lo)%2 else z
    return a[0]
def affine(a,weight,bias=None):
    w=np.asarray(weight,float);out=I(np.zeros((*a.lo.shape[:-1],w.shape[0])))
    for j in range(w.shape[1]):out=out+a[...,j].reshape(*a.lo.shape[:-1],1)*I(w[:,j])
    return out if bias is None else out+I(bias)
def exact_clip(a,low,high):
    a=as_i(a);l=I.rational(low);h=I.rational(high)
    return I(np.maximum(l.lo,np.minimum(h.lo,a.lo)),np.maximum(l.hi,np.minimum(h.hi,a.hi)))
def test():
    # Exact-rational checks of basic arithmetic, including cancellation.
    rng=np.random.default_rng(1616);n=0
    for a,b in rng.uniform(-100,100,(150,2)):
        for r,v in [(I(a)+I(b),Fraction(a)+Fraction(b)),(I(a)*I(b),Fraction(a)*Fraction(b)),(I(a)/I(b),Fraction(a)/Fraction(b))]:
            assert Fraction(float(r.lo))<=v<=Fraction(float(r.hi));n+=1
    assert exp(I(0)).pair()==[1.,1.] and log(I(1)).pair()==[0.,0.]
    assert tanh(I(0)).pair()==[0.,0.]
    for f,a in [(log,I(-1)),(sqrt,I(-1))]:
        try:f(a)
        except ArithmeticError:pass
        else:raise AssertionError('Must reject invalid domain')
    return {'status':'PASS','mpfr_version':VERSION,'precision_bits':128,'exact_rational_checks':n,'rounding':'RNDD lower, RNDU upper, including conversion to binary64','formal_verification':False}
if __name__=='__main__':
    import json
    print(json.dumps(test(),indent=2))
