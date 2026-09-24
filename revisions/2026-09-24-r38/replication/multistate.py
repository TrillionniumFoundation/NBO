"""Nonlinear two-component economy: whole-box integer enclosures, no sampled certificate.
All array arithmetic in certificates is signed int64 with an explicit overflow bound.
A tensor-grid midpoint DP supplies a classical floating-point proposal only.
"""
from __future__ import annotations
import hashlib,json,time,resource
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from primary import ROOT,save,digest
S=1<<34
# component polynomial (linear own-state coefficient, bilinear coefficient, intercept, shock increment)/100
MAPS=(((65,5,0,3),(70,3,0,2)),((15,3,70,2),(70,3,0,2)),
      ((65,5,0,3),(15,4,70,2)),((10,2,80,2),(10,2,80,2)))
COSTS=(0,18,18,32)
MODEL={'state':'[0,1]^2','horizons':[4,8,16,32],'meshes':[16,32,64,128,256],
 'maps_numerator_coefficients':MAPS,'coefficient_denominator':100,'beta':'19/20','probabilities':['3/5','2/5'],
 'reward':'(x+y)/2-cost[action]','operating_costs':['0','9/50','9/50','8/25'],
 'terminal':'(x+y)/4','revision_cost':'(1+(x+y)/2)*1[action!=installed(x,y)]',
 'installed':'overhaul if x<1/4 and y<1/4; otherwise repair x if x<9/20; otherwise repair y if y<9/20; otherwise defer',
 'operating_tolerance':'1/2','integer_scale':S,'initial_distribution':'uniform square'}
def ceildiv(a,d):return -np.floor_divide(-a,d)
def ahash(a):return hashlib.sha256(np.asarray(a,dtype='<i8').tobytes(order='C')).hexdigest()
def raw(x,y):return np.where((x<.25)&(y<.25),3,np.where(x<.45,1,np.where(y<.45,2,0)))
class Boxes:
    def __init__(self,n):
        self.n=n;self.i,self.j=np.meshgrid(np.arange(n,dtype=np.int64),np.arange(n,dtype=np.int64),indexing='ij')
        i,j=self.i,self.j;self.indices=[]
        for a in range(4):
            shockrows=[]
            for shock in (0,1):
                corners=[]
                for component,(own,cross,constant,noise) in enumerate(MAPS[a]):
                    h=i if component==0 else j
                    lo=own*h*n+cross*i*j+(constant+noise*shock)*n*n
                    hi=own*(h+1)*n+cross*(i+1)*(j+1)+(constant+noise*shock)*n*n
                    assert lo.min()>=0 and hi.max()<=100*n*n
                    lower=np.minimum(lo//(100*n),n-1);upper=np.minimum(hi//(100*n),n-1)
                    assert np.all(upper-lower<=1)
                    corners.append((lower,upper))
                shockrows.append(corners)
            self.indices.append(shockrows)
        self.reward_lo=np.stack([((i+j)*100-2*n*c)*S//(200*n) for c in COSTS])
        self.reward_hi=np.stack([ceildiv(((i+j+2)*100-2*n*c)*S,200*n) for c in COSTS])
        self.terminal_lo=(i+j)*S//(4*n);self.terminal_hi=ceildiv((i+j+2)*S,4*n)
        wlo=(2*n+i+j)*S//(2*n);whi=ceildiv((2*n+i+j+2)*S,2*n)
        # Conservative possible installed actions on the entire closed box.
        possible=np.stack([((i+1)*20>=9*n)&((j+1)*20>=9*n),
           (i*20<9*n)&(((i+1)*4>=n)|((j+1)*4>=n)),
           ((i+1)*20>=9*n)&(j*20<9*n), (i*4<n)&(j*4<n)])
        assert np.all(possible.any(axis=0))
        self.kl=np.stack([np.where(possible[a],0,wlo) for a in range(4)])
        self.ku=np.stack([np.where(possible[a]&(possible.sum(axis=0)==1),0,whi) for a in range(4)])
        self.raw=raw((i+.5)/n,(j+.5)/n).astype(np.int64)
    def image(self,v,a,z,upper):
        (il,ih),(jl,jh)=self.indices[a][z]
        stack=np.stack([v[il,jl],v[il,jh],v[ih,jl],v[ih,jh]])
        return stack.max(axis=0) if upper else stack.min(axis=0)
    def continuation(self,v,upper):
        rows=[]
        for a in range(4):
            num=19*(3*self.image(v,a,0,upper)+2*self.image(v,a,1,upper))
            assert np.max(np.abs(num))<2**62
            rows.append(ceildiv(num,100) if upper else num//100)
        return np.stack(rows)
    def q(self,v,upper):return self.continuation(v,upper)+(self.reward_hi if upper else self.reward_lo)
    def take(self,rows,pol):return np.take_along_axis(rows,pol[None],axis=0)[0]
def witnesses(box,T):
    L=[None]*(T+1);U=[None]*(T+1);D=[None]*(T+1);R=[None]*(T+1)
    L[T]=box.terminal_lo;U[T]=box.terminal_hi;D[T]=np.zeros_like(L[T]);R[T]=np.zeros_like(L[T])
    for t in reversed(range(T)):
        ql=box.q(L[t+1],False);qu=box.q(U[t+1],True);L[t]=ql.max(axis=0);U[t]=qu.max(axis=0)
        allowed=L[t][None]-qu<=S//2
        z=box.kl+box.continuation(D[t+1],False)
        D[t]=np.where(allowed,z,2**60).min(axis=0)
        z=box.kl+box.continuation(R[t+1],False);b=L[t][None]-S//2-qu
        R[t]=np.maximum.reduce([np.zeros_like(L[t])]+[(z+mu*b).min(axis=0) for mu in (0,1,4,16,64)])
        assert np.all(L[t]<=U[t]) and np.all(D[t]>=R[t]) and np.all(R[t]>=0)
    return L,U,D,R

def evaluate(box,policies):
    T=len(policies);jl=box.terminal_lo;ju=box.terminal_hi;cl=np.zeros_like(jl);cu=np.zeros_like(jl);stages=[]
    for t in reversed(range(T)):
        p=policies[t];jl=box.take(box.q(jl,False),p);ju=box.take(box.q(ju,True),p)
        cl=box.take(box.kl+box.continuation(cl,False),p);cu=box.take(box.ku+box.continuation(cu,True),p)
        assert np.all(jl<=ju) and np.all(cl<=cu)
        stages.append({'t':t,'J_lower':ahash(jl),'J_upper':ahash(ju),'C_lower':ahash(cl),'C_upper':ahash(cu)})
    return jl,ju,cl,cu,stages

def generator(box,T,U,mode,penalty):
    jl=box.terminal_lo;ju=box.terminal_hi;cl=np.zeros_like(jl);cu=np.zeros_like(jl)
    policies=[None]*T;maxgap=0;fallback=0;stage=[]
    for t in reversed(range(T)):
        ql=box.q(jl,False);qh=box.q(ju,True);zc=box.ku+box.continuation(cu,True);zc_low=box.kl+box.continuation(cl,False)
        if mode=='pilot_raw':p=box.raw
        else:
            feasible=U[t][None]-ql<=S//2;some=feasible.any(axis=0)
            score=zc-penalty*ql;chosen=np.where(feasible,score,2**60).argmin(axis=0)
            p=np.where(some,chosen,ql.argmax(axis=0));fallback+=int((~some).sum())
        policies[t]=p;jl=box.take(ql,p);ju=box.take(qh,p);cl=box.take(zc_low,p);cu=box.take(zc,p)
        maxgap=max(maxgap,int((U[t]-jl).max()))
        stage.append({'t':t,'J_lower':ahash(jl),'J_upper':ahash(ju),'C_lower':ahash(cl),'C_upper':ahash(cu)})
    # Re-evaluate the frozen policy, separately from candidate selection.
    ejl,eju,ecl,ecu,check=evaluate(box,policies)
    assert stage==check and np.array_equal(ecu,cu)
    return policies,cl,cu,maxgap,fallback,check

def interpolate(v,x,y,n):
    a=np.clip(x*n-.5,0,n-1);b=np.clip(y*n-.5,0,n-1)
    i=np.minimum(a.astype(np.int64),n-2);j=np.minimum(b.astype(np.int64),n-2);s=a-i;t=b-j
    return (1-s)*(1-t)*v[i,j]+s*(1-t)*v[i+1,j]+(1-s)*t*v[i,j+1]+s*t*v[i+1,j+1]
def classical(box,T,price):
    n=box.n;x=(box.i+.5)/n;y=(box.j+.5)/n;w=price*(x+y)/4;policies=[None]*T
    for t in reversed(range(T)):
        rows=[]
        for a in range(4):
            ev=0.
            for z,p in enumerate((.6,.4)):
                out=[]
                for component,(own,cross,constant,noise) in enumerate(MAPS[a]):
                    out.append((own*(x if component==0 else y)+cross*x*y+constant+noise*z)/100)
                ev+=p*interpolate(w,*out,n)
            rows.append(price*((x+y)/2-COSTS[a]/100)-(1+(x+y)/2)*(a!=box.raw)+.95*ev)
        w=np.max(rows,axis=0);policies[t]=np.argmax(rows,axis=0)
    return policies

def checked_policy(box,T,U,policies):
    jl=box.terminal_lo;ju=box.terminal_hi;cl=np.zeros_like(jl);cu=np.zeros_like(jl);gap=0;hashes=[]
    for t in reversed(range(T)):
        p=policies[t];jl=box.take(box.q(jl,False),p);ju=box.take(box.q(ju,True),p)
        cl=box.take(box.kl+box.continuation(cl,False),p);cu=box.take(box.ku+box.continuation(cu,True),p)
        gap=max(gap,int((U[t]-jl).max()));hashes.append({'t':t,'J_lower':ahash(jl),'J_upper':ahash(ju),'C_lower':ahash(cl),'C_upper':ahash(cu)})
    return cl,cu,gap,hashes

def run():
    root=ROOT/'results/multistate';root.mkdir(parents=True,exist_ok=True);save(root/'model.json',MODEL)
    rows=[];witnessrows=[];start=time.perf_counter()
    for T in (4,8,16,32):
        for n in (16,32,64,128,256):
            tic=time.perf_counter();box=Boxes(n);L,U,D,R=witnesses(box,T);wt=time.perf_counter()-tic
            wf=root/f'witness_T{T}_N{n}.npz';np.savez_compressed(wf,L=np.stack(L),U=np.stack(U))
            witnessrows.append({'T':T,'mesh':n,'seconds':wt,'max_operating_enclosure_width':str(F(max(int((u-l).max()) for u,l in zip(U,L)),S)),
              'deterministic_lower_integral':str(F(int(D[0].sum()),S*n*n)),'randomized_lower_integral':str(F(int(R[0].sum()),S*n*n)),
              'witness_file':str(wf.relative_to(ROOT/'results')),'file_sha256':hashlib.sha256(wf.read_bytes()).hexdigest(),
              'deterministic_lower_hashes':[ahash(a) for a in D],'randomized_lower_hashes':[ahash(a) for a in R]})
            methods=[('restart',0),('restart',4)]+([('pilot_raw',0)] if n<=128 else [])
            for mode,penalty in methods:
                tic=time.perf_counter();pol,cl,cu,gap,fallback,hashes=generator(box,T,U,mode,penalty)
                if gap<=S//2:assert np.all(D[0]<=cu) and np.all(R[0]<=cu)
                pf=root/f'policy_{mode}{penalty}_T{T}_N{n}.npz';np.savez_compressed(pf,policy=np.stack(pol).astype(np.uint8))
                r={'T':T,'mesh':n,'method':mode,'penalty':penalty,'operating_tolerance':'1/2','certified':gap<=S//2,
                   'all_restart_regret_bound':str(F(gap,S)),'revision_cost_lower':str(F(int(cl.sum()),S*n*n)),
                   'revision_cost_upper':str(F(int(cu.sum()),S*n*n)),'fallback_boxes':fallback,
                   'seconds':time.perf_counter()-tic,'policy_file':str(pf.relative_to(ROOT/'results')),
                   'policy_sha256':ahash(np.stack(pol)),'date_array_hashes':hashes,'reevaluation_passed':True,
                   'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
                rows.append(r);print(T,n,mode,penalty,'regret',float(F(gap,S)),'pass',r['certified'],flush=True)
            # Same operating tolerance and revision objective, classical grid scalarization portfolio.
            candidates=[];tic=time.perf_counter()
            for price in (4,16,64,256):
                pol=classical(box,T,price);cl,cu,gap,hashes=checked_policy(box,T,U,pol)
                candidates.append((gap>S//2,int(cu.sum()),price,pol,cl,cu,gap,hashes))
            fail,_,price,pol,cl,cu,gap,hashes=min(candidates,key=lambda x:(x[0],x[1],x[2]))
            pf=root/f'policy_classical_T{T}_N{n}.npz';np.savez_compressed(pf,policy=np.stack(pol).astype(np.uint8))
            rows.append({'T':T,'mesh':n,'method':'classical_scalarization','selected_price':price,'operating_tolerance':'1/2','certified':not fail,
             'all_restart_regret_bound':str(F(gap,S)),'revision_cost_lower':str(F(int(cl.sum()),S*n*n)),'revision_cost_upper':str(F(int(cu.sum()),S*n*n)),
             'candidate_results':[{'price':a[2],'certified':not a[0],'regret_bound':str(F(a[6],S)),'cost_upper':str(F(a[1],S*n*n))} for a in candidates],
             'seconds':time.perf_counter()-tic,'policy_file':str(pf.relative_to(ROOT/'results')),'policy_sha256':ahash(np.stack(pol)),
             'date_array_hashes':hashes,'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
            save(ROOT/'results/multistate_progress.json',{'outcomes':rows,'witnesses':witnessrows})
    assert len(rows)==76
    save(ROOT/'results/multistate.json',{'outcomes':rows,'witnesses':witnessrows,'cases':76,'seconds':time.perf_counter()-start,
       'pilot_cases':16,'restart_cases':40,'classical_comparisons':20,'certificate_arithmetic':'outward integer bounds, scale 2^34',
       'overflow_bound':'All intermediate absolute values checked below 2^62; maximum model value <40, maximum cost <40, local multiplier <=64.',
       'scope':'Separate nonlinear economy at epsilon=1/2. Does not replace primary epsilon=1/100 or 1/20. Chronology is fresh R38 execution, not a reconstructed R35/R36 run.',
       'verification':'All whole-box bounds constructed by interval induction. Restart policies separately re-evaluated; same integer arithmetic kernel, not included in the independent SymPy 42-object claim.'})
if __name__=='__main__':run()
