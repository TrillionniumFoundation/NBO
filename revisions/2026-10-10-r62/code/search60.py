"""Exact action-search implementations with explicit matched input/output contracts.

The C++ backend uses arbitrary-size rational numbers. NumPy intervals only
exclude candidates; exact rational comparison always chooses the witness.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
import hashlib,json,math,os,subprocess,time
import numpy as np
import sympy as sp
import screen58 as sc
n=sc.n;R=Path(__file__).resolve().parents[1]
METHODS=('sympy','reduced-sympy','vector-exhaustive','screen-unreduced','screen-reduced','native-exhaustive','native-piecewise','adaptive')

@dataclass
class Objective:
    q1:F
    q2:F
    q4:F
    features:list
    squares:list
    def value(self,a):
        a=F(a)
        return self.q1*a+self.q2*a*a+self.q4*a**4+sum(w*sc.a.old.hinge(z+s*a,r) for w,z,s,r in self.features)+sum(w*max(F(0),z+s*a)**2 for w,z,s in self.squares)
    def payload(self):return dict(q1=str(self.q1),q2=str(self.q2),q4=str(self.q4),features=[[str(x) for x in f] for f in self.features],squares=[[str(x) for x in f] for f in self.squares])
    @classmethod
    def load(cls,p):return cls(F(p['q1']),F(p['q2']),F(p['q4']),[tuple(map(F,z)) for z in p['features']],[tuple(map(F,z)) for z in p['squares']])
    @classmethod
    def from_critic(cls,state,critic):
        q1,q2,f,s,_=sc.a.reduce_objective(state,critic)
        return cls(q1,q2,F(4),f,s)
    def reduced(self,cap):
        z,offset=sc.simplify((self.q1,self.q2,self.features,self.squares,self.value),F(cap))
        return Objective(z[0],z[1],self.q4,z[2],z[3]),offset

def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def compile_native():
    binary=R/'build/native60';binary.parent.mkdir(exist_ok=True)
    start=time.perf_counter();cmd=['g++','-O3','-std=c++17',str(R/'code/search60.cpp'),'-o',str(binary)]
    subprocess.run(cmd,check=True,capture_output=True,text=True)
    record=dict(command=cmd,seconds=time.perf_counter()-start,source_sha256=digest(R/'code/search60.cpp'),binary_sha256=digest(binary),compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0],exact_backend='Boost cpp_rational/cpp_int; no floating root calculation')
    (R/'audit').mkdir(exist_ok=True);(R/'audit/NATIVE_COMPILE60.json').write_text(json.dumps(record,indent=2)+'\n')
    return record

def native_batch(queries):
    """Each query is (objective, maximum index, denominator, mode, indices)."""
    lines=[str(len(queries))]
    for o,cap,Q,mode,selected in queries:
        if not isinstance(cap,(int,np.integer)) or not isinstance(Q,(int,np.integer)) or Q<=0 or not 0<=cap<=Q:raise ValueError('Invalid lattice')
        lines.append(f'{mode} {cap} {Q} {o.q1} {o.q2} {o.q4} {len(o.features)} {len(o.squares)}')
        lines.extend(' '.join(map(str,f)) for f in o.features)
        lines.extend(' '.join(map(str,f)) for f in o.squares)
        if mode==2:lines.append(str(len(selected))+' '+' '.join(map(str,selected)))
    raw=('\n'.join(lines)+'\n').encode();begin=time.perf_counter()
    process=subprocess.run([str(R/'build/native60')],input=raw,capture_output=True,check=True)
    output=process.stdout.decode().splitlines()
    if len(output)!=len(queries):raise AssertionError('Incomplete native reply')
    rows=[]
    for line in output:
        k,v,e,d,p,b,t,c=line.split()
        rows.append(dict(index=int(k),objective_exact=str(F(v)),exact_evaluations=int(e),difference_queries=int(d),pieces=int(p),max_recorded_operand_bits=int(b),ties_among_evaluated=int(t),candidate_count=int(c)))
    return rows,dict(native_request_bytes=len(raw),native_response_bytes=len(process.stdout),native_process_seconds=time.perf_counter()-begin)

def native(o,cap,Q,mode=1,selected=None):
    rows,work=native_batch([(o,cap,Q,mode,selected)]);rows[0].update(work);return rows[0]

def endpoints(o,cap,Q):
    x=n.I.point(np.arange(cap+1,dtype=float))/n.s.c.rat_i(F(Q))
    val=n.s.c.rat_i(o.q1)*x+n.s.c.rat_i(o.q2)*x.square()+n.s.c.rat_i(o.q4)*x.square().square()
    peak=0
    for group in ([f for f in o.features if f[3]==0],[f for f in o.features if f[3]>0]):
        if not group:continue
        def col(j):
            v=n.s.c.array_i([f[j] for f in group]);return n.I(v.lo[:,None],v.hi[:,None])
        xi=n.I(x.lo[None,:],x.hi[None,:]);z=col(1)+col(2)*xi
        if group[0][3]==0:h=sc.positive(z)
        else:
            ri=col(3);h=(sc.positive(z+ri).square()-sc.positive(z-ri).square())/(4*ri)
        terms=col(0)*h;peak=max(peak,terms.lo.nbytes+terms.hi.nbytes)
        while len(terms.lo)>1:
            m=len(terms.lo)//2
            pair=n.I(terms.lo[:2*m:2],terms.hi[:2*m:2])+n.I(terms.lo[1:2*m:2],terms.hi[1:2*m:2])
            terms=n.I(np.concatenate((pair.lo,terms.lo[-1:])),np.concatenate((pair.hi,terms.hi[-1:]))) if len(terms.lo)%2 else pair
        val=val+n.I(terms.lo[0],terms.hi[0])
    for w,z,s in o.squares:val=val+n.s.c.rat_i(w)*sc.positive(n.s.c.rat_i(z)+n.s.c.rat_i(s)*x).square()
    return val,peak

def sympy_search(o,cap,Q):
    knots={F(0),F(cap,Q)}
    for w,z,s,r in o.features:
        if s:
            for edge in (-r,r):
                k=(edge-z)/s
                if 0<k<F(cap,Q):knots.add(k)
    for w,z,s in o.squares:
        if s and 0<-z/s<F(cap,Q):knots.add(-z/s)
    ks=sorted(knots);indices={0,cap};roots=0;x=sp.Symbol('a')
    def near(l,h):
        indices.update(range(max(0,math.floor(l*Q)),min(cap,math.ceil(h*Q))+1))
    for k in ks:near(k,k)
    for l,h in zip(ks,ks[1:]):
        midpoint=(l+h)/2;c1=o.q1;c2=o.q2
        for w,z,s,r in o.features:
            v=z+s*midpoint
            if v>=r:c1+=w*s
            elif r and v>-r:c1+=w*s*(z+r)/(2*r);c2+=w*s*s/(4*r)
        for w,z,s in o.squares:
            if z+s*midpoint>0:c1+=2*w*z*s;c2+=w*s*s
        poly=sp.Poly(sp.Rational(4*o.q4)*x**3+sp.Rational(2*c2)*x+sp.Rational(c1),x)
        if poly.is_zero:continue
        for (lo,hi),mult in poly.intervals(eps=sp.Rational(1,4*Q),inf=sp.Rational(l),sup=sp.Rational(h)):
            roots+=1;near(F(int(lo.p),int(lo.q)),F(int(hi.p),int(hi.q)))
    scores={k:o.value(F(k,Q)) for k in indices};best=min(scores,key=lambda k:(scores[k],k))
    return dict(index=best,objective_exact=str(scores[best]),exact_evaluations=len(scores),candidate_count=len(scores),isolated_roots=roots,pieces=max(0,len(ks)-1),max_recorded_operand_bits=max(max(v.numerator.bit_length(),v.denominator.bit_length()) for v in scores.values()))

def bound(o,lo,hi,bits=53):
    """Exact natural interval followed by outward dyadic endpoint coarsening.
    bits controls final bound resolution, not the internal arithmetic precision.
    """
    low=F(0);high=F(0)
    for c,a,b in ((o.q1,lo,hi),(o.q2,lo*lo,hi*hi),(o.q4,lo**4,hi**4)):
        u,v=sorted((c*a,c*b));low+=u;high+=v
    for w,z,s,r in o.features:
        a,b=sorted((z+s*lo,z+s*hi));u,v=sorted((w*sc.a.old.hinge(a,r),w*sc.a.old.hinge(b,r)));low+=u;high+=v
    for w,z,s in o.squares:
        a,b=sorted((z+s*lo,z+s*hi));u,v=sorted((w*max(F(0),a)**2,w*max(F(0),b)**2));low+=u;high+=v
    D=1<<bits
    return F(math.floor(low*D),D),F(math.ceil(high*D),D)

def adaptive(o,cap,Q,bits=53,node_limit=256):
    seeds=sorted({0,cap,cap//2});vals={k:o.value(F(k,Q)) for k in seeds};best=min(vals,key=lambda k:(vals[k],k));score=vals[best]
    stack=[(0,cap)];nodes=0;pruned=0;peak=1;exact=len(seeds)
    while stack:
        if nodes>=node_limit:
            r=native(o,cap,Q);r.update(fallback=True,fallback_reason='node-budget',pair_nodes=nodes,pruned_nodes=pruned,peak_stack=peak,pre_fallback_exact_evaluations=exact,bound_fraction_bits=bits);return r
        l,h=stack.pop();nodes+=1;lower,upper=bound(o,F(l,Q),F(h,Q),bits)
        if lower>score or (lower==score and l>=best):pruned+=1;continue
        if l==h:
            v=o.value(F(l,Q));exact+=1
            if (v,l)<(score,best):score=v;best=l
        else:
            m=(l+h)//2;stack.extend(((m+1,h),(l,m)));peak=max(peak,len(stack))
    return dict(index=best,objective_exact=str(score),exact_evaluations=exact,candidate_count=exact,pair_nodes=nodes,pruned_nodes=pruned,peak_stack=peak,fallback=False,bound_fraction_bits=bits,max_recorded_operand_bits=max(score.numerator.bit_length(),score.denominator.bit_length()))

def solve(o,cap,Q,method,bits=53,node_limit=256):
    start=time.perf_counter();active=o;offset=F(0)
    if method in ('reduced-sympy','vector-exhaustive','screen-reduced','native-piecewise','adaptive'):active,offset=o.reduced(F(cap,Q))
    if method in ('sympy','reduced-sympy'):r=sympy_search(active,cap,Q);r['objective_exact']=str(F(r['objective_exact'])+offset)
    elif method in ('native-exhaustive','native-piecewise'):
        r=native(active,cap,Q,0 if method=='native-exhaustive' else 1);r['objective_exact']=str(F(r['objective_exact'])+offset)
    elif method=='adaptive':r=adaptive(active,cap,Q,bits,node_limit);r['objective_exact']=str(F(r['objective_exact'])+offset)
    elif method in ('vector-exhaustive','screen-unreduced','screen-reduced'):
        if cap+1>sc.MAX_LATTICE and method!='vector-exhaustive':
            r=native(active,cap,Q);r.update(fallback=True,fallback_reason='lattice-limit',retained_points=r['candidate_count'],screened_points=0);r['objective_exact']=str(F(r['objective_exact'])+offset)
        else:
            try:
                with np.errstate(over='raise',invalid='raise',divide='raise',under='ignore'):v,peak=endpoints(active,cap,Q);keep,cutoff=sc.survivors(v.lo,v.hi)
            except (ArithmeticError,ValueError):
                r=native(active,cap,Q);r.update(fallback=True,fallback_reason='invalid-enclosure');r['objective_exact']=str(F(r['objective_exact'])+offset)
            else:
                ids=list(range(cap+1)) if method=='vector-exhaustive' else list(map(int,keep));r=native(o,cap,Q,2,ids)
                j=r['index'];score=F(r['objective_exact'])-offset
                if not F(float(v.lo[j]))<=score<=F(float(v.hi[j])):raise AssertionError('Selected original exact value outside interval')
                r.update(screened_points=cap+1,retained_points=len(ids),screen_survivors=len(keep),largest_single_pair_array_bytes=peak,endpoint_sha256=hashlib.sha256(v.lo.tobytes()+v.hi.tobytes()).hexdigest(),max_endpoint_width=float(v.width().max()),fallback=False)
    else:raise ValueError(method)
    if F(r['objective_exact'])!=o.value(F(r['index'],Q)):raise AssertionError('Native witness differs from Python exact objective')
    r.update(method=method,seconds=time.perf_counter()-start,lattice_size=cap+1,original_ridges=len(o.features),active_ridges=len(active.features),eliminated_ridges=len(o.features)-len(active.features),offset_exact=str(offset))
    return r

def proposals(critics,part):
    """Native root-free witness; every common terminal solve is unchanged."""
    grid=n.propose(critics,part);exact=grid.copy();queries=[];locations=[];records=[]
    for t in range(len(critics)-1):
        for k in range(len(part.lo)):
            if t==len(critics)-2:
                r=sc.a.minimize(part.centers[k],critics[t+1],int(part.capindex[k]));grid[t,k]=exact[t,k]=r['index'];r.update(date=t,leaf=k,common_terminal=True);records.append(r)
            else:
                original=Objective.from_critic(part.centers[k],critics[t+1]);obj,offset=original.reduced(F(int(part.capindex[k]),4096))
                queries.append((obj,int(part.capindex[k]),4096,1,None));locations.append((t,k,original,obj,offset))
    results,work=native_batch(queries)
    for r,(t,k,original,obj,offset) in zip(results,locations):
        exact[t,k]=r['index'];r['objective_exact']=str(F(r['objective_exact'])+offset)
        if original.value(F(r['index'],4096))!=F(r['objective_exact']):raise AssertionError('Neural native objective identity')
        r.update(date=t,leaf=k,common_terminal=False,grid_index=int(grid[t,k]),active_ridges=len(obj.features),eliminated_ridges=len(original.features)-len(obj.features),grid_regret_exact=str(original.value(F(int(grid[t,k]),4096))-F(r['objective_exact'])))
        if F(r['grid_regret_exact'])<0:raise AssertionError('Native exact witness worse than original menu')
        records.append(r)
    return grid,exact,sorted(records,key=lambda r:(r['date'],r['leaf'])),work
