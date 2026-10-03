"""Optional JIT of scalar polynomial kernels; no fast-math transformations.

Numba is an acceleration layer only. The analytical error budget and input
clipping are identical to the NumPy implementation. Exact coefficient
arrays avoid differing compile-time evaluations of factorial fractions.
"""
import math
import numpy as np
try:
    from numba import njit
except ImportError:
    njit=None

EXP_COEFF=np.array([1/math.factorial(k) for k in range(15)],dtype=np.float64)
LOG_COEFF=np.array([1/(2*j+1) for j in range(18)],dtype=np.float64)

if njit is not None:
    @njit(cache=True,fastmath=False)
    def tanh_kernel(x):
        out=np.empty_like(x)
        for j in range(x.size):
            v=min(20.,max(-20.,x[j]));r=v/256.;z=EXP_COEFF[14]
            for k in range(13,-1,-1):z=z*r+EXP_COEFF[k]
            for k in range(9):z=z*z
            out[j]=1.-2./(1.+z)
        return out

    @njit(cache=True,fastmath=False)
    def log_kernel(x):
        out=np.empty_like(x);q0=1./3.;p0=LOG_COEFF[17]
        for k in range(16,-1,-1):p0=LOG_COEFF[k]+q0*q0*p0
        l2=2*q0*p0
        for j in range(x.size):
            m,e=math.frexp(x[j]);q=(2*m-1)/(2*m+1);q2=q*q;p=LOG_COEFF[17]
            for k in range(16,-1,-1):p=LOG_COEFF[k]+q2*p
            out[j]=2*q*p+(e-1)*l2
        return out
else:
    tanh_kernel=log_kernel=None
