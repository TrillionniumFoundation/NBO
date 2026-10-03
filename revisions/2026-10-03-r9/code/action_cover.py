"""Signed mean-value bounds and verified face domination for the unchanged R8 economy.

Derivative bounds are used only when every cubature leg stays wholly inside
or wholly outside each wealth stopping face. All crossed interpolation cells
and reflection slopes enter the hull. Unresolved boxes retain their bounds.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
R8=ROOT/'revisions/2026-10-03-r8'
sys.path.insert(0,str(R8/'code'))
from action_enclosure_tight import CornerEncloser
from action_enclosure import I,exp_i,log_i,up,down,reflect,clip,terminal
from continuous_actor import Model,LO,HI
OUT=Path(__file__).resolve().parents[1]/'results'

class SignedEncloser(CornerEncloser):
    def __init__(self,m,vlo,vhi=None):
        super().__init__(m,vlo,vhi)
        du=I(m.us[1:])-I(m.us[:-1]);dy=I(m.ys[1:])-I(m.ys[:-1])
        self.su=(I(self.gridlo[1:,:],self.gridhi[1:,:])-I(self.gridlo[:-1,:],self.gridhi[:-1,:]))/I(du.lo[:,None],du.hi[:,None])
        self.sy=(I(self.gridlo[:,1:],self.gridhi[:,1:])-I(self.gridlo[:,:-1],self.gridhi[:,:-1]))/I(dy.lo[None,:],dy.hi[None,:])
        self.gradient_boxes=0
    def slopes(self,u,y):
        m=self.m
        il=np.clip(np.searchsorted(m.us,u.lo,side='left')-1,0,m.nu-2)
        ih=np.clip(np.searchsorted(m.us,u.hi,side='right')-1,0,m.nu-2)
        jl=np.clip(np.searchsorted(m.ys,y.lo,side='left')-1,0,m.nx-2)
        jh=np.clip(np.searchsorted(m.ys,y.hi,side='right')-1,0,m.nx-2)
        ul=np.full(len(il),np.inf);uh=np.full(len(il),-np.inf)
        yl=np.full(len(il),np.inf);yh=np.full(len(il),-np.inf)
        for di in range(int(np.max(ih-il))+1):
          ii=np.minimum(il+di,m.nu-2)
          for dj in range(int(np.max(jh-jl))+1):
            jj=np.minimum(jl+dj,m.nx-2);valid=(ii<=ih)&(jj<=jh)
            uu=I(np.maximum(u.lo,m.us[ii]),np.maximum(np.maximum(u.lo,m.us[ii]),np.minimum(u.hi,m.us[ii+1])))
            yy=I(np.maximum(y.lo,m.ys[jj]),np.maximum(np.maximum(y.lo,m.ys[jj]),np.minimum(y.hi,m.ys[jj+1])))
            wu=(uu-I(m.us[ii]))/(I(m.us[ii+1])-I(m.us[ii]))
            wy=(yy-I(m.ys[jj]))/(I(m.ys[jj+1])-I(m.ys[jj]))
            su=(1-wy)*I(self.su.lo[ii,jj],self.su.hi[ii,jj])+wy*I(self.su.lo[ii,jj+1],self.su.hi[ii,jj+1])
            sy=(1-wu)*I(self.sy.lo[ii,jj],self.sy.hi[ii,jj])+wu*I(self.sy.lo[ii+1,jj],self.sy.hi[ii+1,jj])
            ul=np.minimum(ul,np.where(valid,su.lo,np.inf));uh=np.maximum(uh,np.where(valid,su.hi,-np.inf))
            yl=np.minimum(yl,np.where(valid,sy.lo,np.inf));yh=np.maximum(yh,np.where(valid,sy.hi,-np.inf))
        return I(ul,uh),I(yl,yh)
    def gradient(self,rows,alo,ahi):
        self.gradient_boxes+=len(rows);m=self.m
        c=I(alo[:,0],ahi[:,0]);p=I(alo[:,1],ahi[:,1]);th=I(alo[:,2],ahi[:,2])
        u=I(m.points[rows,0]);y=I(m.points[rows,1]);n=len(rows)
        gc=I(m.h)*exp_i((1-u)*y-u*log_i(c));gp=I(np.zeros(n));gt=-I(m.h)*I(m.cost)*th
        regular=np.ones(n,bool)
        for z1,z2 in [(math.sqrt(2),0),(-math.sqrt(2),0),(0,math.sqrt(2)),(0,-math.sqrt(2))]:
            raw=u+th*m.h+I(.08*math.sqrt(m.h)*z1)
            un=reflect(raw,m.us[0],m.us[-1])
            sglo=np.where((raw.hi<=m.us[0])|(raw.lo>=m.us[-1]),-1.,1.);sghi=sglo.copy()
            crossing=((raw.lo<m.us[0])&(raw.hi>m.us[0]))|((raw.lo<m.us[-1])&(raw.hi>m.us[-1]))
            sglo=np.where(crossing,-1.,sglo);sghi=np.where(crossing,1.,sghi)
            shock=.2*math.sqrt(m.h)*(-.3*z1+math.sqrt(.91)*z2)
            yn=y+(I(.02)+I(.06)*p-c-I(.02)*p.square())*m.h+I(shock)*p
            inside=(yn.lo>=m.ys[0])&(yn.hi<=m.ys[-1]);outside=(yn.hi<m.ys[0])|(yn.lo>m.ys[-1])
            regular &= inside|outside
            clipped=clip(yn,m.ys[0],m.ys[-1]);su,sy=self.slopes(un,clipped)
            gu=exp_i((1-un)*clipped)*(1-(1-un)*clipped)/(1-un).square()
            fu=I(np.where(outside,gu.lo,su.lo),np.where(outside,gu.hi,su.hi))
            fy=I(np.where(outside,0.,sy.lo),np.where(outside,0.,sy.hi))
            gc=gc+I(m.q/4)*fy*(-m.h)
            gp=gp+I(m.q/4)*fy*(I(m.h)*(I(.06)-I(.04)*p)+I(shock))
            gt=gt+I(m.q/4)*fu*I(m.h)*I(sglo,sghi)
        return I(np.c_[gc.lo,gp.lo,gt.lo],np.c_[gc.hi,gp.hi,gt.hi]),regular
    def bounded(self,rows,lo,hi):
        natural=self.q(rows,lo,hi);g,smooth=self.gradient(rows,lo,hi)
        center=lo+(hi-lo)/2;point=self.q(rows,center)
        radius=g*I((I(lo)-I(center)).lo,(I(hi)-I(center)).hi)
        mean=I(point.hi)
        for d in range(3):mean=mean+I(radius.hi[:,d])
        upper=np.where(smooth,np.minimum(natural.hi,mean.hi),natural.hi)
        return upper,point.lo,center,g,smooth

def maximize(m,v,initial,tolerance=.0002,max_depth=45,max_boxes=500000,face_reduce=True):
    start=time.perf_counter();e=SignedEncloser(m,v);allrows=np.arange(m.N)
    inc=e.q(allrows,initial).lo;policy=initial.copy()
    rows=np.flatnonzero(~m.boundary);lo=np.tile(LO,(len(rows),1));hi=np.tile(HI,(len(rows),1))
    unresolved=np.full(m.N,-np.inf);pruned=0;faces=0;regular_count=0;stopped=False;history=[]
    for depth in range(max_depth+1):
        upper,point,center,grad,regular=e.bounded(rows,lo,hi);regular_count+=int(regular.sum())
        np.maximum.at(inc,rows,point)
        ids=np.flatnonzero(point>=inc[rows]);policy[rows[ids]]=center[ids]
        if face_reduce:
            lowface=regular[:,None]&(grad.hi<0)&(hi>lo)
            highface=regular[:,None]&(grad.lo>0)&(hi>lo)
            if np.any(lowface|highface):
                faces+=int(np.sum(lowface|highface))
                hi=np.where(lowface,lo,hi);lo=np.where(highface,hi,lo)
                changed=np.any(lowface|highface,axis=1)
                val=e.q(rows[changed],lo[changed],hi[changed]);upper[changed]=np.minimum(upper[changed],val.hi)
                mid=lo[changed]+(hi[changed]-lo[changed])/2;pv=e.q(rows[changed],mid).lo
                np.maximum.at(inc,rows[changed],pv)
                ids=np.flatnonzero(pv>=inc[rows[changed]]);policy[rows[changed][ids]]=mid[ids]
        keep=upper>up(inc[rows]+tolerance);pruned+=int((~keep).sum())
        history.append({'depth':depth,'boxes':len(rows),'remaining':int(keep.sum()),'q_evaluations':e.boxes,'gradient_boxes':e.gradient_boxes})
        if not np.any(keep):rows=np.array([],int);break
        rows,lo,hi,upper,gradlo,gradhi=[a[keep] for a in [rows,lo,hi,upper,grad.lo,grad.hi]]
        if depth==max_depth or e.boxes+8*len(rows)>max_boxes:
            np.maximum.at(unresolved,rows,upper);stopped=True;break
        width=hi-lo;score=width*np.maximum(abs(gradlo),abs(gradhi))
        d=score.argmax(axis=1) if depth%4!=3 else (width/(HI-LO)).argmax(axis=1)
        idx=np.arange(len(rows));mid=lo[idx,d]+(hi[idx,d]-lo[idx,d])/2
        stuck=(mid<=lo[idx,d])|(mid>=hi[idx,d])
        if np.any(stuck):
            np.maximum.at(unresolved,rows[stuck],upper[stuck]);stopped=True
            good=~stuck;rows,lo,hi,d,mid=[a[good] for a in [rows,lo,hi,d,mid]];idx=np.arange(len(rows))
        if len(rows)==0:break
        lh=hi.copy();lh[idx,d]=mid;rl=lo.copy();rl[idx,d]=mid
        rows=np.r_[rows,rows];lo=np.r_[lo,rl];hi=np.r_[lh,hi]
    bound=np.maximum(up(inc+tolerance),unresolved)
    g=terminal(I(m.points[:,0]),I(m.points[:,1]));bound[m.boundary]=g.hi[m.boundary]
    achieved=e.q(allrows,policy).lo
    if np.any(achieved<inc-1e-9):raise AssertionError('incumbent-policy mismatch')
    return bound,policy,dict(seconds=time.perf_counter()-start,box_evaluations=e.boxes,
        gradient_boxes=e.gradient_boxes,verified_face_reductions=faces,regular_boxes=regular_count,
        depth=depth,pruned_leaves=pruned,unresolved_leaves=len(rows),budget_exhausted=stopped,
        maximum_optimization_bracket=float(np.max(up(bound-achieved))),tolerance=tolerance,
        max_depth=max_depth,max_boxes=max_boxes,history=history)

def verify(raw_name,tolerance=.0002,max_boxes=500000,tag=None):
    path=Path(raw_name).resolve();z=np.load(path);pi=z['policy'];nt,n,_=pi.shape
    shape=json.loads(path.with_suffix('.json').read_text())['state_grid'];m=Model(*shape,nt)
    g=terminal(I(m.points[:,0]),I(m.points[:,1]));lo=g.lo.copy();hi=g.hi.copy();opt=g.hi.copy()
    lowers=[lo.copy()];uppers=[hi.copy()];optimal=[opt.copy()];proposals=[];hist=[];start=time.perf_counter()
    for t in range(nt-1,-1,-1):
        pv=CornerEncloser(m,lo,hi).q(np.arange(n),pi[t]);lo,hi=pv.lo,pv.hi
        opt,proposal,stats=maximize(m,opt,pi[t],tolerance=tolerance,max_boxes=max_boxes)
        lowers.append(lo.copy());uppers.append(hi.copy());optimal.append(opt.copy());proposals.append(proposal)
        hist.append(dict(t=t,regret=float(np.max(up(opt-lo))),**stats));print(json.dumps({k:v for k,v in hist[-1].items() if k!='history'}),flush=True)
    lower,upper,best=[np.array(v[::-1]) for v in [lowers,uppers,optimal]]
    OUT.mkdir(parents=True,exist_ok=True);tag=tag or path.stem+'_signed_cover'
    raw=OUT/f'{tag}.npz';np.savez_compressed(raw,policy_lower=lower,policy_upper=upper,optimal_upper=best,cover_proposals=np.array(proposals[::-1]))
    result={'seconds':time.perf_counter()-start,'input':str(path.relative_to(ROOT)),'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'policy_regret_upper':float(np.max(up(best-lower))),'history':hist,'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),
      'state_grid':shape,'steps':nt,'scope':'complete continuous action box, every declared state/time node; unchanged economic primitives and R8 nodal transition',
      'continuous_state_time_error':None,'all_action_optimizations_closed':all(not h['budget_exhausted'] for h in hist)}
    (OUT/f'{tag}.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('raw');p.add_argument('--tolerance',type=float,default=.0002);p.add_argument('--max-boxes',type=int,default=500000)
    p.add_argument('--tag',default=None);a=p.parse_args();verify(a.raw,a.tolerance,a.max_boxes,a.tag)
