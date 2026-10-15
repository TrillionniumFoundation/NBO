"""Verified warm-start terminal optimizer; pre-confirmation engineering amendment.
The floating proposal is never trusted. A strong-monotonicity residual localizes
all constrained minimizers over each state box. This replaces slow interval
bisection, without changing the economy, fit, protocol design or acceptance target.
"""
from __future__ import annotations
import numpy as np
from economy100 import Economy
from interval100 import I

class WarmEconomy(Economy):
    def optimal_u_box(self,x,steps=44,box=False):
        A=self.capacity(x);shape=np.broadcast_shapes(A.lo.shape,A.hi.shape)
        n=int(np.prod(shape)) if shape else 1
        _,d0=self.terminal(x,I(0)*A,box=box)
        _,d1=self.terminal(x,A,box=box)
        at0=np.asarray(d0.lo>=0);at1=np.asarray(d1.hi<=0)
        if np.any(at0 & at1):raise ArithmeticError('incompatible endpoint signs')
        fixed=at0|at1
        middle=np.where(at1,1.,0.).reshape(-1)
        mask=(~fixed).reshape(-1)
        if np.any(mask):
            centers=np.column_stack([np.broadcast_to(v.mid(),shape).reshape(-1)[mask] for v in x])
            _,_,af=self.fast_value_grad(centers)
            caps=1/8+centers.sum(axis=-1)/16
            middle[mask]=np.clip(af/caps,0,1)
        middle=middle.reshape(shape)
        self.counts.terminal_solves+=n
        if np.all(fixed):return I(middle)
        _,derivative=self.terminal(x,I(middle)*A,box=box)
        # d Qa/du = Qaa*A >= 2*A_lo. Keep zero in the derivative interval:
        # a lower curvature bound cannot provide a nonzero lower root distance.
        residual=I(np.minimum(derivative.lo,0),np.maximum(derivative.hi,0))
        enclosure=(I(middle)-residual/I(2*A.lo)).clip(0,1)
        return I(np.where(fixed,middle,enclosure.lo),np.where(fixed,middle,enclosure.hi))
