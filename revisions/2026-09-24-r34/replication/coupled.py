"""Exact one-dimensional Bellman certificates, including isolated tie points.
All certificates use fractions; floating point is restricted to proposal fitting.
Run: python coupled.py --smoke, or --study OUTPUT_DIRECTORY.
"""
from __future__ import annotations
from fractions import Fraction as F
from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from pathlib import Path
import argparse, hashlib, json, time, sys, platform
from typing import Callable

if not __debug__:
    raise RuntimeError("Certificate checks require Python without -O")

ZERO, ONE = F(0), F(1)
CAP = 200000
BETA = F(19,20)
PROBS = (F(3,5), F(2,5))
MAPS = (((F(3,4),ZERO),(F(3,4),F(1,20))),
        ((F(17,20),F(1,10)),(F(17,20),F(7,50))),
        ((F(1,10),F(4,5)),(F(1,10),F(17,20))))
COSTS = (ZERO,F(3,20),F(9,20))

@dataclass
class PW:
    """Affine on OPEN knot intervals, with separately represented knot values."""
    xs: list[F]
    ab: list[tuple[F,F]]
    ys: list[F]
    def __post_init__(self):
        assert self.xs[0] == 0 and self.xs[-1] == 1
        assert len(self.xs) == len(self.ys) == len(self.ab)+1
        assert all(a < b for a,b in zip(self.xs,self.xs[1:]))
        if len(self.ab)>CAP: raise RuntimeError(f'piece cap: {len(self.ab)}>{CAP}')
    def at(self,x:F)->F:
        if not 0<=x<=1: raise ValueError('state outside [0,1]')
        i=bisect_left(self.xs,x)
        if i<len(self.xs) and self.xs[i]==x: return self.ys[i]
        a,b=self.ab[i-1]; return a*x+b
    def line(self,x:F)->tuple[F,F]:
        i=min(len(self.ab)-1,max(0,bisect_right(self.xs,x)-1))
        return self.ab[i]
    def norm(self)->PW:
        xs=[self.xs[0]]; ab=[]; ys=[self.ys[0]]
        for i in range(1,len(self.xs)-1):
            if self.ab[i-1]==self.ab[i] and self.ys[i]==self.ab[i][0]*self.xs[i]+self.ab[i][1]:
                continue
            ab.append(self.ab[i-1]); xs.append(self.xs[i]); ys.append(self.ys[i])
        ab.append(self.ab[-1]); xs.append(ONE); ys.append(self.ys[-1])
        return PW(xs,ab,ys)
    def extent(self)->tuple[F,F]:
        vv=self.ys[:]
        for (a,b),l,r in zip(self.ab,self.xs,self.xs[1:]): vv.extend((a*l+b,a*r+b))
        return min(vv),max(vv)
    def integral(self)->F:
        return sum((a*(r*r-l*l)/2+b*(r-l) for (a,b),l,r in zip(self.ab,self.xs,self.xs[1:])),ZERO)
    def dump(self)->dict:
        return {'knots':list(map(str,self.xs)), 'affine':[[str(a),str(b)] for a,b in self.ab], 'points':list(map(str,self.ys))}
    @classmethod
    def load(cls,d:dict)->PW:
        return cls(list(map(F,d['knots'])),[tuple(map(F,z)) for z in d['affine']],list(map(F,d['points'])))
    def bits(self)->int:
        v=self.xs+self.ys+[z for ab in self.ab for z in ab]
        return max(max(abs(x.numerator).bit_length(),x.denominator.bit_length()) for x in v)

def affine(a=ZERO,b=ZERO)->PW:
    a,b=F(a),F(b); return PW([ZERO,ONE],[(a,b)],[b,a+b])

def linear_comb(fs:list[PW],cs:list[F],a=ZERO,b=ZERO)->PW:
    xs=sorted(set(x for f in fs for x in f.xs))
    ab=[]
    for l,r in zip(xs,xs[1:]):
        lines=[f.line((l+r)/2) for f in fs]
        ab.append((F(a)+sum((c*z[0] for c,z in zip(cs,lines)),ZERO),F(b)+sum((c*z[1] for c,z in zip(cs,lines)),ZERO)))
    ys=[F(a)*x+F(b)+sum((c*f.at(x) for c,f in zip(cs,fs)),ZERO) for x in xs]
    return PW(xs,ab,ys).norm()

def compose(f:PW,a:F,b:F)->PW:
    assert a>0 and 0<=b<=a+b<=1
    xs=sorted({ZERO,ONE}|{(x-b)/a for x in f.xs if 0<(x-b)/a<1})
    ab=[]
    for l,r in zip(xs,xs[1:]):
        m,c=f.line(a*(l+r)/2+b); ab.append((m*a,m*b+c))
    return PW(xs,ab,[f.at(a*x+b) for x in xs]).norm()

def q_functions(next_value:PW, operating=True)->list[PW]:
    return [linear_comb([compose(next_value,*m) for m in MAPS[a]], [BETA*p for p in PROBS],ONE if operating else ZERO,-COSTS[a] if operating else ZERO) for a in range(3)]

def threshold(f:PW,limit:F)->PW:
    xs=set(f.xs)
    for (m,b),l,r in zip(f.ab,f.xs,f.xs[1:]):
        if m:
            z=(limit-b)/m
            if l<z<r: xs.add(z)
    xs=sorted(xs)
    ab=[(ZERO,F(f.at((l+r)/2)<=limit)) for l,r in zip(xs,xs[1:])]
    return PW(xs,ab,[F(f.at(x)<=limit) for x in xs]).norm()

def envelope(fs:list[PW],maximize=True,allowed:list[PW]|None=None)->tuple[PW,PW]:
    extra=[] if allowed is None else allowed
    coarse=sorted(set(x for f in fs+extra for x in f.xs)); xs=set(coarse)
    for l,r in zip(coarse,coarse[1:]):
        z=(l+r)/2; eligible=[i for i in range(len(fs)) if allowed is None or allowed[i].at(z)]
        if not eligible: raise ValueError('empty admissible OPEN cell')
        for ii,i in enumerate(eligible):
            ai,bi=fs[i].line(z)
            for j in eligible[ii+1:]:
                aj,bj=fs[j].line(z)
                if ai!=aj:
                    w=(bj-bi)/(ai-aj)
                    if l<w<r: xs.add(w)
    xs=sorted(xs)
    if len(xs)>CAP+1: raise RuntimeError('envelope piece cap')
    def choose(z):
        eligible=[i for i in range(len(fs)) if allowed is None or allowed[i].at(z)]
        if not eligible: raise ValueError('empty admissible POINT')
        return min(eligible,key=lambda i:((-fs[i].at(z) if maximize else fs[i].at(z)),i))
    choices=[choose((l+r)/2) for l,r in zip(xs,xs[1:])]
    points=[choose(x) for x in xs]
    value=PW(xs,[fs[i].line((l+r)/2) for i,l,r in zip(choices,xs,xs[1:])],[fs[i].at(x) for i,x in zip(points,xs)]).norm()
    policy=PW(xs,[(ZERO,F(i)) for i in choices],list(map(F,points))).norm()
    return value,policy

def select(fs:list[PW],policy:PW)->PW:
    xs=sorted(set(policy.xs)|set(x for f in fs for x in f.xs))
    ab=[fs[int(policy.at((l+r)/2))].line((l+r)/2) for l,r in zip(xs,xs[1:])]
    return PW(xs,ab,[fs[int(policy.at(x))].at(x) for x in xs]).norm()

def intervention(policy:PW,action:int)->PW:
    ab=[(ZERO,ZERO) if b==action else (ONE,ONE) for a,b in policy.ab]
    assert all(a==0 for a,b in policy.ab)
    ys=[ZERO if y==action else 1+x for x,y in zip(policy.xs,policy.ys)]
    return PW(policy.xs[:],ab,ys).norm()

def dyadic_up(x:F,bits:int)->F:
    n=x.numerator*(1<<bits); d=x.denominator
    return F(-(-n//d),1<<bits)

def dyadic_near(x:F,bits:int)->F:
    return F((x.numerator*(1<<bits)*2+x.denominator)//(2*x.denominator),1<<bits)

def interpolate(xs:list[F],ys:list[F])->PW:
    ab=[]
    for l,r,vl,vr in zip(xs,xs[1:],ys,ys[1:]):
        a=(vr-vl)/(r-l); ab.append((a,vl-a*l))
    return PW(xs,ab,ys).norm()

def compress_upper(f:PW,delta:F)->tuple[PW,dict]:
    # The input is continuous convex. No sampled-only test is accepted.
    assert all(f.at(x)==a*x+b for (a,b),x in zip(f.ab,f.xs))
    assert all(a<=c for (a,b),(c,d) in zip(f.ab,f.ab[1:]))
    kept={0,len(f.xs)-1}; stack=[(0,len(f.xs)-1)]
    while stack:
        i,j=stack.pop()
        if j==i+1: continue
        l,r=f.xs[i],f.xs[j]; vl,vr=f.at(l),f.at(r)
        m=(vr-vl)/(r-l)
        err,k=max((vl+m*(f.xs[k]-l)-f.at(f.xs[k]),k) for k in range(i+1,j))
        if err>delta/2: kept.add(k); stack.extend(((i,k),(k,j)))
    for bits in (24,32,48,64,96,128):
        xs=sorted({ZERO,ONE}|{dyadic_near(f.xs[i],bits) for i in kept})
        # Round ordered secant slopes, not point values independently.
        # This preserves convexity and bounds vertical drift by 2^(1-q).
        ys=[dyadic_up(f.at(ZERO),bits+16)]
        for l,r in zip(xs,xs[1:]):
            slope=dyadic_up((f.at(r)-f.at(l))/(r-l),bits+16)
            ys.append(ys[-1]+slope*(r-l))
        g=interpolate(xs,ys)
        assert all(a<=c for (a,b),(c,d) in zip(g.ab,g.ab[1:]))
        difference=linear_comb([g,f],[ONE,-ONE]); lo,hi=difference.extent()
        if 0<=lo<=hi<=delta:
            return g,{'original_pieces':len(f.ab),'pieces':len(g.ab),'round_bits':bits,'error_upper':str(hi),'bits':g.bits()}
    raise RuntimeError('dyadic global compression check failed')

def witnesses(T:int,eps:F)->tuple[list[PW],list[list[PW]],dict]:
    eta=eps/sum((BETA**j for j in range(T)),ZERO)
    U=[None]*(T+1); U[T]=affine(F(1,2)); qs=[None]*T; log=[]
    tic=time.perf_counter()
    for t in reversed(range(T)):
        qs[t]=q_functions(U[t+1]); exact,_=envelope(qs[t])
        U[t],record=compress_upper(exact,eta/4); log.append({'date':t,**record})
        for q in qs[t]: assert linear_comb([U[t],q],[ONE,-ONE]).extent()[0]>=0
    return U,qs,{'seconds':time.perf_counter()-tic,'eta':str(eta),'dates':log}

def exact_dp(T:int)->tuple[list[PW],list[PW],dict]:
    tic=time.perf_counter(); v=[None]*(T+1); p=[None]*T; v[T]=affine(F(1,2))
    for t in reversed(range(T)): v[t],p[t]=envelope(q_functions(v[t+1]))
    return v,p,{'seconds':time.perf_counter()-tic,'pieces':[len(x.ab) for x in v],'max_bits':max(x.bits() for x in v)}

def evaluate(policies:list[PW],raw:list[PW]|None=None)->list[PW]:
    T=len(policies); vals=[None]*(T+1); vals[T]=affine(F(1,2)) if raw is None else affine()
    for t in reversed(range(T)):
        qs=q_functions(vals[t+1],operating=raw is None)
        if raw is not None: qs=[linear_comb([q,intervention(raw[t],a)],[ONE,ONE]) for a,q in enumerate(qs)]
        vals[t]=select(qs,policies[t])
    return vals

def admissible(U:list[PW],qs:list[list[PW]],eta:F)->list[list[PW]]:
    return [[threshold(linear_comb([u,q],[ONE,-ONE]),eta) for q in row] for u,row in zip(U,qs)]

def repair(raw:list[PW],allowed:list[list[PW]],dynamic=True)->tuple[list[PW],list[PW]]:
    T=len(raw); D=[None]*(T+1); p=[None]*T; D[T]=affine()
    for t in reversed(range(T)):
        continuation=q_functions(D[t+1],operating=False) if dynamic else [affine()]*3
        cost=[linear_comb([q,intervention(raw[t],a)],[ONE,ONE]) for a,q in enumerate(continuation)]
        D[t],p[t]=envelope(cost,maximize=False,allowed=allowed[t])
    if not dynamic: D=evaluate(p,raw)
    return p,D

def verify(U,qs,eta,allowed,raw,policy,D,J)->dict:
    # Independent comparisons, including OPEN-cell limits and isolated knot values.
    T=len(raw); e=ZERO; max_upper=ZERO; residual=ZERO
    for t in reversed(range(T)):
        recomputed=q_functions(U[t+1])
        for qa in recomputed: assert linear_comb([U[t],qa],[ONE,-ONE]).extent()[0]>=0
        chosen=select(recomputed,policy[t]); assert linear_comb([U[t],chosen],[ONE,-ONE]).extent()[1]<=eta
        e=eta+BETA*e
        gap=linear_comb([U[t],J[t]],[ONE,-ONE]).extent()[1]
        assert gap<=e; max_upper=max(max_upper,gap)
        qcost=q_functions(D[t+1],operating=False)
        costs=[linear_comb([q,intervention(raw[t],a)],[ONE,ONE]) for a,q in enumerate(qcost)]
        minimum,selector=envelope(costs,maximize=False,allowed=allowed[t])
        assert linear_comb([D[t],minimum],[ONE,-ONE]).extent()==(ZERO,ZERO)
        assert linear_comb([select(costs,policy[t]),D[t]],[ONE,-ONE]).extent()==(ZERO,ZERO)
    return {'all_restart_regret_upper':str(max_upper),'cost_bellman_residual':str(residual),'certified':True}

def summary_case(T,eps,U,qs,wlog,raw,name,proposal_stats,exact_values=None)->tuple[dict,dict]:
    stage={}; tic=time.perf_counter(); raw_values=evaluate(raw); stage['raw_evaluation']=time.perf_counter()-tic
    tic=time.perf_counter(); allowed=admissible(U,qs,F(wlog['eta'])); stage['allowed_construction']=time.perf_counter()-tic
    tic=time.perf_counter(); policy,D=repair(raw,allowed); stage['dynamic_cost_solve']=time.perf_counter()-tic
    tic=time.perf_counter(); point,P=repair(raw,allowed,dynamic=False); stage['pointwise_control']=time.perf_counter()-tic
    tic=time.perf_counter(); J=evaluate(policy); C=evaluate(policy,raw); stage['final_evaluation']=time.perf_counter()-tic
    for a,b in zip(C,D): assert linear_comb([a,b],[ONE,-ONE]).extent()==(ZERO,ZERO)
    tic=time.perf_counter(); checks=verify(U,qs,F(wlog['eta']),allowed,raw,policy,D,J); stage['verification']=time.perf_counter()-tic
    raw_bound=max(linear_comb([u,v],[ONE,-ONE]).extent()[1] for u,v in zip(U,raw_values))
    raw_true=max(linear_comb([u,v],[ONE,-ONE]).extent()[1] for u,v in zip(exact_values,raw_values)) if exact_values else None
    preserve=min(linear_comb([j,v],[ONE,-ONE]).extent()[0] for j,v in zip(J,raw_values))
    saving=linear_comb([P[0],D[0]],[ONE,-ONE]); assert saving.extent()[0]>=0
    pointJ=evaluate(point)
    record={'T':T,'epsilon':str(eps),'proposal':name,'proposal_stats':proposal_stats,'stages_seconds':stage,'witness_seconds':wlog['seconds'],**checks,
      'raw_regret_upper':str(raw_bound),'raw_exact_regret':str(raw_true) if raw_true is not None else None,'raw_pass':bool(raw_true<=eps) if raw_true is not None else bool(raw_bound<=eps),
      'preservation_margin':str(preserve),'preservation_certified':preserve>=0,'operating_value':str(J[0].integral()),'raw_operating_value':str(raw_values[0].integral()),'pointwise_operating_value':str(pointJ[0].integral()),
      'intervention_cost':str(D[0].integral()),'pointwise_intervention_cost':str(P[0].integral()),'occupancy_cost_saving':str(saving.integral()),'max_cost_saving':str(saving.extent()[1]),
      'policy_pieces':[len(p.ab) for p in policy],'cost_pieces':[len(v.ab) for v in D],'max_bits':max(v.bits() for v in U+D+J),
      'raw_policy_sha256':hashlib.sha256(json.dumps([p.dump() for p in raw],sort_keys=True).encode()).hexdigest()}
    if exact_values: record['exact_operating_value']=str(exact_values[0].integral())
    cert={'model':model(),'epsilon':str(eps),'U':[v.dump() for v in U],'raw':[p.dump() for p in raw],'policy':[p.dump() for p in policy],'D':[v.dump() for v in D],'J':[v.dump() for v in J]}
    tic=time.perf_counter(); encoded=json.dumps(cert,sort_keys=True,separators=(',',':')).encode(); stage['serialization']=time.perf_counter()-tic
    record['certificate_bytes']=len(encoded); record['certificate_sha256']=hashlib.sha256(encoded).hexdigest()
    # Baseline/control construction is reported separately, not charged as algorithm work.
    algorithm_stages=['raw_evaluation','allowed_construction','dynamic_cost_solve','final_evaluation','verification','serialization']
    record['installed_total_seconds']=wlog['seconds']+sum(stage[k] for k in algorithm_stages)+proposal_stats.get('compile_seconds',0)
    record['cold_total_seconds']=record['installed_total_seconds']+proposal_stats.get('fit_seconds',0)
    return record,cert

def model()->dict:
    return {'beta':str(BETA),'probabilities':list(map(str,PROBS)),'costs':list(map(str,COSTS)),'transitions':[[[str(a),str(b)] for a,b in row] for row in MAPS],'terminal':'x/2','reward':'x-cost[action]','revision_cost':'(1+x)*1[action!=raw]','domain':['0','1']}

def stress_policy(T:int)->list[PW]:
    p=PW([ZERO,F(9,10),ONE],[(ZERO,ZERO),(ZERO,ONE)],[ZERO,ONE,ONE]); return [p]*(T-1)+[affine()]

def smoke():
    T=4; eps=F(1,20); U,qs,wl=witnesses(T,eps); V,opt,dl=exact_dp(T)
    print('witness',wl, 'exact',dl,flush=True)
    for name,raw in [('defer',[affine()]*T),('stress',stress_policy(T))]:
        r,c=summary_case(T,eps,U,qs,wl,raw,name,{},V)
        print(name,{k:v for k,v in r.items() if k not in ['stages_seconds']},flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--smoke',action='store_true'); args=ap.parse_args()
    if args.smoke: smoke()
