"""Cell-corner interval enclosure; independent refinement of the R8 cover.

A bilinear interpolant attains its rectangle extrema at a corner of every
intersected grid cell. This replaces a valid, but looser, slope envelope.
All stopping-face unions and unresolved branch bounds remain explicit.
"""
from __future__ import annotations
import argparse,json,time,hashlib
import numpy as np
import action_enclosure as base
from action_enclosure import I,up,terminal,Model,OUT

class CornerEncloser(base.Encloser):
    def interp(self,u,y):
        m=self.m
        il=np.clip(np.searchsorted(m.us,u.lo,side='right')-1,0,m.nu-2)
        ih=np.clip(np.searchsorted(m.us,u.hi,side='left'),0,m.nu-2)
        jl=np.clip(np.searchsorted(m.ys,y.lo,side='right')-1,0,m.nx-2)
        jh=np.clip(np.searchsorted(m.ys,y.hi,side='left'),0,m.nx-2)
        lower=np.full(len(il),np.inf);upper=np.full(len(il),-np.inf)
        for di in range(int(np.max(ih-il))+1):
            ii=np.minimum(il+di,m.nu-2)
            for dj in range(int(np.max(jh-jl))+1):
                jj=np.minimum(jl+dj,m.nx-2)
                ul=np.maximum(u.lo,m.us[ii]);uh=np.minimum(u.hi,m.us[ii+1])
                yl=np.maximum(y.lo,m.ys[jj]);yh=np.minimum(y.hi,m.ys[jj+1])
                valid=(ii<=ih)&(jj<=jh)&(ul<=uh)&(yl<=yh)
                def value(a,b):return I(self.gridlo[ii+a,jj+b],self.gridhi[ii+a,jj+b])
                for uu in [ul,uh]:
                    wu=(I(uu)-I(m.us[ii]))/(I(m.us[ii+1])-I(m.us[ii]))
                    for yy in [yl,yh]:
                        wy=(I(yy)-I(m.ys[jj]))/(I(m.ys[jj+1])-I(m.ys[jj]))
                        z=(1-wu)*(1-wy)*value(0,0)+wu*(1-wy)*value(1,0)+(1-wu)*wy*value(0,1)+wu*wy*value(1,1)
                        lower=np.minimum(lower,np.where(valid,z.lo,np.inf))
                        upper=np.maximum(upper,np.where(valid,z.hi,-np.inf))
        if not np.all(np.isfinite(lower)) or not np.all(np.isfinite(upper)):
            raise FloatingPointError('uncovered interpolation rectangle')
        return I(lower,upper)


def verify(raw_name,tolerance=.0005,max_depth=30,max_boxes=1600000):
    raw=OUT/raw_name;z=np.load(raw);policy=z['policy'];nt,n,_=policy.shape
    shape=json.loads(raw.with_suffix('.json').read_text())['state_grid'];m=Model(*shape,nt)
    g=terminal(I(m.points[:,0]),I(m.points[:,1]));plo=g.lo.copy();phi=g.hi.copy();opt=g.hi.copy()
    lower=[plo.copy()];upper=[phi.copy()];optimal=[opt.copy()];history=[];start=time.perf_counter()
    original=base.Encloser;base.Encloser=CornerEncloser
    try:
        for t in range(nt-1,-1,-1):
            pv=CornerEncloser(m,plo,phi).q(np.arange(n),policy[t]);plo,phi=pv.lo,pv.hi
            opt,stats=base.maximize(m,opt,policy[t],tolerance,max_depth,max_boxes)
            lower.append(plo.copy());upper.append(phi.copy());optimal.append(opt.copy())
            history.append(dict(t=t,elapsed_seconds=time.perf_counter()-start,
                regret_upper=float(np.max(up(opt-plo))),**stats))
            print(json.dumps(history[-1]),flush=True)
    finally:base.Encloser=original
    lower=np.array(lower[::-1]);upper=np.array(upper[::-1]);optimal=np.array(optimal[::-1])
    tag=raw.stem+'_corner_certificate'
    np.savez_compressed(OUT/f'{tag}.npz',policy_lower=lower,policy_upper=upper,optimal_upper=optimal)
    report=dict(raw_input=raw.name,raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
        scope='complete continuous action box at all stored finite state/time nodes; exact nodal interpolation with discrete exit monitoring',
        seconds=time.perf_counter()-start,policy_regret_upper=float(np.max(up(optimal-lower))),
        policy_evaluation_bracket_max=float(np.max(up(upper-lower))),history=history,
        all_action_optimizations_closed=all(not h['budget_exhausted'] for h in history),
        continuous_state_time_error=None,
        previous_enclosure_retained='continuous_actor_s11_search_action_certificate.json',
        interval_implementation='R6 outward arithmetic; R8 cell-corner cover; conditional floating-point model, not formal machine proof')
    (OUT/f'{tag}.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('raw');p.add_argument('--max-boxes',type=int,default=1600000);p.add_argument('--depth',type=int,default=30);p.add_argument('--tolerance',type=float,default=.0005)
    a=p.parse_args();verify(a.raw,a.tolerance,a.depth,a.max_boxes)
