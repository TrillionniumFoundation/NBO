"""Outward action-box enclosures for the original NDU cubature economy.

No concavity or sampled-Lipschitz assumption is used. The function encloses
all continuous controls in each box, including stopping discontinuities.
The certificate is for the stated finite-state/time interpolated economy;
it is not a continuous-state/time HJB error bound.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/2026-09-29-r6/code'))
from interval_certificate import I,exp_i,log_i,down,up
from continuous_actor import Model,LO,HI
OUT=Path(__file__).resolve().parents[1]/'results'

def clip(x,lo,hi):return I(np.clip(x.lo,lo,hi),np.clip(x.hi,lo,hi))
def reflect(x,lo,hi):
    # This economy's single-step preference increments cannot span both ends.
    if np.any(x.lo<2*lo-hi) or np.any(x.hi>2*hi-lo):raise ValueError('reflection range')
    lower=x.lo.copy();upper=x.hi.copy()
    below=x.hi<=lo;above=x.lo>=hi;crosslo=(x.lo<lo)&(x.hi>lo);crosshi=(x.lo<hi)&(x.hi>hi)
    reflectedlo=2*I(lo)-x;reflectedhi=2*I(hi)-x
    lower=np.where(below,reflectedlo.lo,lower);upper=np.where(below,reflectedlo.hi,upper)
    lower=np.where(above,reflectedhi.lo,lower);upper=np.where(above,reflectedhi.hi,upper)
    lower=np.where(crosslo,lo,lower);upper=np.where(crosslo,np.maximum(reflectedlo.hi,x.hi),upper)
    lower=np.where(crosshi,np.minimum(x.lo,reflectedhi.lo),lower);upper=np.where(crosshi,hi,upper)
    return clip(I(lower,upper),lo,hi)

def terminal(u,y):return exp_i((1-u)*y)/(1-u)

class Encloser:
    def __init__(self,m,vlo,vhi=None):
        self.m=m;self.v=I(vlo,vhi);self.shape=(m.nu,m.nx)
        self.gridlo=self.v.lo.reshape(self.shape);self.gridhi=self.v.hi.reshape(self.shape)
        # Cellwise slopes: maxima over each cell's opposite edges are exact
        # Lipschitz bounds for bilinear interpolation in that coordinate.
        du=I(m.us[1:])-I(m.us[:-1]);dy=I(m.ys[1:])-I(m.ys[:-1])
        v=I(self.gridlo,self.gridhi)
        su=(I(v.lo[1:,:],v.hi[1:,:])-I(v.lo[:-1,:],v.hi[:-1,:]))/I(du.lo[:,None],du.hi[:,None])
        sy=(I(v.lo[:,1:],v.hi[:,1:])-I(v.lo[:,:-1],v.hi[:,:-1]))/I(dy.lo[None,:],dy.hi[None,:])
        self.lu=np.maximum(su.absmax()[:,:-1],su.absmax()[:,1:])
        self.ly=np.maximum(sy.absmax()[:-1,:],sy.absmax()[1:,:])
        self.boxes=0
    def interp(self,u,y):
        m=self.m
        uc=(u.lo+u.hi)/2;yc=(y.lo+y.hi)/2
        i=np.clip(np.searchsorted(m.us,uc,side='right')-1,0,m.nu-2)
        j=np.clip(np.searchsorted(m.ys,yc,side='right')-1,0,m.nx-2)
        wu=(I(uc)-I(m.us[i]))/(I(m.us[i+1])-I(m.us[i]))
        wy=(I(yc)-I(m.ys[j]))/(I(m.ys[j+1])-I(m.ys[j]))
        def value(a,b):return I(self.gridlo[i+a,j+b],self.gridhi[i+a,j+b])
        middle=(1-wu)*(1-wy)*value(0,0)+wu*(1-wy)*value(1,0)+(1-wu)*wy*value(0,1)+wu*wy*value(1,1)
        il=np.clip(np.searchsorted(m.us,u.lo,side='right')-1,0,m.nu-2)
        ih=np.clip(np.searchsorted(m.us,u.hi,side='left'),0,m.nu-2)
        jl=np.clip(np.searchsorted(m.ys,y.lo,side='right')-1,0,m.nx-2)
        jh=np.clip(np.searchsorted(m.ys,y.hi,side='left'),0,m.nx-2)
        lu=np.zeros_like(uc);ly=np.zeros_like(yc)
        for di in range(int(np.max(ih-il))+1):
            ii=np.minimum(il+di,m.nu-2)
            for dj in range(int(np.max(jh-jl))+1):
                jj=np.minimum(jl+dj,m.nx-2);valid=(ii<=ih)&(jj<=jh)
                lu=np.maximum(lu,np.where(valid,self.lu[ii,jj],0));ly=np.maximum(ly,np.where(valid,self.ly[ii,jj],0))
        radius=I(lu)*(I(uc)-u).absmax()+I(ly)*(I(yc)-y).absmax()
        return middle+I(-radius.hi,radius.hi)
    def q(self,rows,alo,ahi=None):
        self.boxes+=len(rows);m=self.m;a=I(alo,ahi)
        consumption=I(a.lo[:,0],a.hi[:,0]);p=I(a.lo[:,1],a.hi[:,1]);theta=I(a.lo[:,2],a.hi[:,2])
        u=I(m.points[rows,0]);y=I(m.points[rows,1])
        reward=I(m.h)*(exp_i((1-u)*(log_i(consumption)+y))/(1-u)-I(.5*m.cost)*theta.square())
        continuation=I(np.zeros(len(rows)))
        for z1,z2 in [(math.sqrt(2),0),(-math.sqrt(2),0),(0,math.sqrt(2)),(0,-math.sqrt(2))]:
            un=reflect(u+theta*m.h+I(.08*math.sqrt(m.h)*z1),m.us[0],m.us[-1])
            yn=y+(I(.02)+I(.06)*p-consumption-I(.02)*p.square())*m.h+I(.2*math.sqrt(m.h)*(-.3*z1+math.sqrt(.91)*z2))*p
            inside=(yn.lo>=m.ys[0])&(yn.hi<=m.ys[-1]);outside=(yn.hi<m.ys[0])|(yn.lo>m.ys[-1])
            clipped=clip(yn,m.ys[0],m.ys[-1]);interpolated=self.interp(un,clipped)
            stopping=terminal(un,clipped)
            # When the box straddles an exit face, take the union. This keeps
            # the exact stopping payoff, rather than presuming continuity.
            lower=np.where(inside,interpolated.lo,np.where(outside,stopping.lo,np.minimum(interpolated.lo,stopping.lo)))
            upper=np.where(inside,interpolated.hi,np.where(outside,stopping.hi,np.maximum(interpolated.hi,stopping.hi)))
            continuation=continuation+I(lower,upper)/4
        result=reward+I(m.q)*continuation
        boundary=m.boundary[rows]
        if np.any(boundary):
            g=terminal(u,y);result=I(np.where(boundary,g.lo,result.lo),np.where(boundary,g.hi,result.hi))
        return result

def maximize(m,v,initial,tolerance=.002,max_depth=18,max_boxes=300000):
    """Complete cover until the declared budget, with safe unresolved upper.

    Pruned boxes have upper <= incumbent+tolerance. If a budget is exhausted,
    every unresolved box contributes its upper bound. No false convergence.
    """
    e=Encloser(m,v);active=np.flatnonzero(~m.boundary);allrows=np.arange(m.N)
    inc=e.q(allrows,initial).lo
    rows=active;lo=np.tile(LO,(len(rows),1));hi=np.tile(HI,(len(rows),1))
    unresolved=np.full(m.N,-np.inf);accepted_count=0;depth=0;stopped=False
    for depth in range(max_depth+1):
        bounds=e.q(rows,lo,hi);middle=(lo+hi)/2;candidate=e.q(rows,middle)
        np.maximum.at(inc,rows,candidate.lo)
        keep=bounds.hi>inc[rows]+tolerance;accepted_count+=int((~keep).sum())
        if not np.any(keep):rows=np.array([],int);break
        rows,lo,hi,upper=rows[keep],lo[keep],hi[keep],bounds.hi[keep]
        if depth==max_depth or e.boxes+4*len(rows)>max_boxes:
            np.maximum.at(unresolved,rows,upper);stopped=True;break
        # Normalized longest side makes every dimension shrink on every
        # infinite branch. Ties are deterministic and are not sample slopes.
        u=m.points[rows,0];y=m.points[rows,1]
        lu=float(np.max(e.lu));ly=float(np.max(e.ly))
        scores=np.c_[(hi[:,0]-lo[:,0])*m.h*(lo[:,0]**(-u)*np.exp((1-u)*y)+m.q*ly),
                     (hi[:,1]-lo[:,1])*m.q*ly*(.06*m.h+.2*math.sqrt(2*m.h)),
                     (hi[:,2]-lo[:,2])*m.h*(m.cost*.45+m.q*lu)]
        # A depth-modulo safeguard forces every control to be bisected,
        # independent of the heuristic sensitivity scores.
        dimension=np.argmax(scores,axis=1) if depth%4!=3 else ((hi-lo)/(HI-LO)).argmax(axis=1)
        r=np.arange(len(rows));mid=(lo[r,dimension]+hi[r,dimension])/2
        left_hi=hi.copy();left_hi[r,dimension]=mid;right_lo=lo.copy();right_lo[r,dimension]=mid
        rows=np.r_[rows,rows];lo=np.r_[lo,right_lo];hi=np.r_[left_hi,hi]
    upper=np.maximum(up(inc+tolerance),unresolved)
    g=terminal(I(m.points[:,0]),I(m.points[:,1]));upper[m.boundary]=g.hi[m.boundary]
    return upper,dict(box_evaluations=e.boxes,depth=depth,pruned_leaves=accepted_count,
        unresolved_leaves=len(rows),budget_exhausted=stopped,
        maximum_optimization_bracket=float(np.max(upper-inc)),tolerance=tolerance,
        max_depth=max_depth,max_boxes=max_boxes)

def verify(raw_name,tolerance=.002,max_depth=18,max_boxes=300000):
    raw=OUT/raw_name;z=np.load(raw);policy=z['policy'];nt,n,_=policy.shape
    shape=json.loads(raw.with_suffix('.json').read_text())['state_grid'];m=Model(*shape,nt)
    g=terminal(I(m.points[:,0]),I(m.points[:,1]));plo=g.lo.copy();phi=g.hi.copy();opt=g.hi.copy()
    lowers=[plo.copy()];uppers=[phi.copy()];optimal=[opt.copy()];history=[];start=time.perf_counter()
    for t in range(nt-1,-1,-1):
        en=Encloser(m,plo,phi);pv=en.q(np.arange(n),policy[t]);plo,phi=pv.lo,pv.hi
        opt,stats=maximize(m,opt,policy[t],tolerance,max_depth,max_boxes)
        lowers.append(plo.copy());uppers.append(phi.copy());optimal.append(opt.copy())
        history.append(dict(t=t,elapsed_seconds=time.perf_counter()-start,
            regret_upper=float(np.max(up(opt-plo))),**stats))
        print(json.dumps(history[-1]),flush=True)
    lower=np.array(lowers[::-1]);upper=np.array(uppers[::-1]);best=np.array(optimal[::-1]);tag=raw.stem+'_action_certificate'
    np.savez_compressed(OUT/f'{tag}.npz',policy_lower=lower,policy_upper=upper,optimal_upper=best)
    report=dict(raw_input=raw.name,raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
        scope='all stored state/time nodes and the complete three-dimensional continuous action box; no continuous-state/time claim',
        arithmetic='inherited R6 outward primitive/transcendental arithmetic; exact real interpretation of stored primitive constants and nodal abscissae',
        seconds=time.perf_counter()-start,policy_regret_upper=float(np.max(up(best-lower))),
        policy_evaluation_bracket_max=float(np.max(up(upper-lower))),history=history,
        all_action_optimizations_closed=all(not h['budget_exhausted'] for h in history),
        continuous_state_time_error=None)
    (OUT/f'{tag}.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('raw');p.add_argument('--max-boxes',type=int,default=300000);p.add_argument('--depth',type=int,default=18);p.add_argument('--tolerance',type=float,default=.002)
    a=p.parse_args();verify(a.raw,a.tolerance,a.depth,a.max_boxes)
