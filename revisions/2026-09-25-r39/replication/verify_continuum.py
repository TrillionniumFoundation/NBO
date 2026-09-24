"""Independent SymPy checks for the new continuum lotteries and restart bounds.
Reuses ONLY the R38 independent parser/primitive specification, never its
constructor. Full support super-solutions are rebuilt from primitive rows.
Pointwise operating proofs include isolated values; cost integrals explicitly
use the nonsingular-transition/absolutely-continuous initial-law contract.
"""
from pathlib import Path
import sys,json,gzip,hashlib,bisect,time,copy
from sympy import Rational as Q
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'2026-09-24-r38'
sys.path.insert(0,str(OLD/'replication'))
import verify_primary as v
sys.set_int_max_str_digits(200000)
Z,O=v.Z,v.O;S=1<<40

def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def cells(knots):
    xs=sorted(knots);return [(l,r,False) for l,r in zip(xs,xs[1:])]+[(x,x,True) for x in xs]
def pullback(f):return {(x-c)/a for row in v.TRANS for a,c in row for x in f[0] if 0<(x-c)/a<1}
def endpoints(h,l,r):return v.at(h,l),v.at(h,r)
def eq(h,l,r):assert endpoints(h,l,r)==(0,0)
def nonneg(h,l,r):assert min(endpoints(h,l,r))>=0

def check_operating(d):
    assert d['schema']=='NBO-R39-continuum-randomized-v1' and d['model']==v.MODEL
    assert d['policy_class']=='randomized_Markov_common_continuation' and d['constraint']=='every_time_every_state'
    T=d['T'];eps=Q(d['epsilon']);V=list(map(v.parse,d['V']));J=list(map(v.parse,d['J']));raw=list(map(v.parse,d['raw']));op=list(map(v.parse,d['operating_policy']))
    pol=[{k:v.parse(z) for k,z in pp.items()} for pp in d['policy']]
    assert len(J)==len(V)==T+1 and len(pol)==len(raw)==len(op)==T
    for f in (J[-1],V[-1]):
        assert all(a==Q(1,2) and b==0 for a,b in f[1]) and all(y==x/2 for x,y in zip(f[0],f[2]))
    count=0
    for t in range(T-1,-1,-1):
        pp=pol[t];assert pp['raw']==raw[t]
        for p in (raw[t],op[t],pp['best']):v.policy_shape(p)
        knots={Z,O}|set(V[t][0])|set(J[t][0])|set(op[t][0])|pullback(V[t+1])|pullback(J[t+1])
        for f in pp.values():knots.update(f[0])
        for l,r,point in cells(knots):
            x=(l+r)/2;curv=v.line(V[t],x,point);curj=v.line(J[t],x,point)
            qv=[v.qrow(V[t+1],a,x,point,True) for a in range(3)]
            qj=[v.qrow(J[t+1],a,x,point,True) for a in range(3)]
            for q in qv:nonneg(v.subtract(curv,q),l,r)
            eq(v.subtract(curv,qv[v.act(op[t],x)]),l,r)
            a=v.act(raw[t],x);b=v.act(pp['best'],x);num=v.line(pp['num'],x,point);den=v.line(pp['den'],x,point)
            eq(v.subtract(den,v.subtract(qj[b],qj[a])),l,r)
            eq(v.subtract(curj,v.plus(qj[a],num)),l,r)
            nonneg(num,l,r);nonneg(v.subtract(den,num),l,r)
            nonneg(v.plus(v.subtract(curj,curv),(Z,eps)),l,r);nonneg(v.subtract(curv,curj),l,r)
            for q in qj:nonneg(v.subtract(qj[b],q),l,r)
            count+=1
    return V,J,raw,pol,count

def overlap(xs,l,r):
    start=max(0,bisect.bisect_left(xs,l)-1);stop=min(len(xs)-1,bisect.bisect_right(xs,r)+1)
    ids=[j for j in range(start,stop) if xs[j]<r and xs[j+1]>l]
    assert ids;return ids

def mass(name,l,r):return r-l if name=='uniform' else r*r-l*l if name=='high_condition' else 2*(r-l)-(r*r-l*l)
def parsegrid(d):
    out=[]
    for row in d:
        z=copy.deepcopy(row);z['xs']=list(map(Q,z['xs']));xs=z['xs'];assert xs[0]==0 and xs[-1]==1 and all(l<r for l,r in zip(xs,xs[1:]))
        assert len(z['lower'])==len(xs)-1;out.append(z)
    return out

def check_cost(d,pol):
    grids=parsegrid(d['cost_grids']);assert d['scale']==S and len(grids)==len(pol)+1
    assert grids[-1]['lower']==grids[-1]['upper']==[0]
    count=0
    for t in range(len(pol)-1,-1,-1):
        pp=pol[t];g=grids[t];ng=grids[t+1];assert all(x in g['xs'] for p in pp.values() for x in p[0])
        for i,(l,r) in enumerate(zip(g['xs'],g['xs'][1:])):
            mid=(l+r)/2;a=v.act(pp['raw'],mid);b=v.act(pp['best'],mid)
            assert (a,b)==(g['raw'][i],g['best'][i]);num=v.line(pp['num'],mid);den=v.line(pp['den'],mid)
            ratios=[Z,Z] if num==(Z,Z) else [v.at(num,x)/v.at(den,x) for x in (l,r)]
            pl,pu=Q(g['probability_lower'][i],S),Q(g['probability_upper'][i],S)
            assert 0<=pl<=min(ratios)<=max(ratios)<=pu<=1
            def expected(action,upper):
                val=Z
                for p,(a0,c0) in zip(v.PROBS,v.TRANS[action]):
                    ids=overlap(ng['xs'],a0*l+c0,a0*r+c0)
                    vals=[ng['upper' if upper else 'lower'][j] for j in ids]
                    val+=v.BETA*p*(max(vals) if upper else min(vals))
                return val
            alo,ahi=expected(a,False),expected(a,True);blo,bhi=expected(b,False),expected(b,True)
            wl=S*(1+l) if a!=b else Z;wh=S*(1+r) if a!=b else Z
            low=min((1-p)*alo+p*(blo+wl) for p in (pl,pu));high=max((1-p)*ahi+p*(bhi+wh) for p in (pl,pu))
            assert 0<=g['lower'][i]<=low and high<=g['upper'][i];count+=1
    g=grids[0]
    for name,row in d['initial_bounds'].items():
        lo=sum(Q(c,S)*mass(name,l,r) for l,r,c in zip(g['xs'],g['xs'][1:],g['lower']))
        hi=sum(Q(c,S)*mass(name,l,r) for l,r,c in zip(g['xs'],g['xs'][1:],g['upper']))
        assert Q(row['lottery_cost_lower'])<=lo<=hi<=Q(row['lottery_cost_upper'])
    return count

SUPPORT_CACHE={}
def check_support(T,proposal,raw):
    key=(T,proposal)
    if key in SUPPORT_CACHE:return SUPPORT_CACHE[key]
    p=OLD/'results/supports'/f'support_H{T}_{proposal}.json.gz';d=read(p);assert list(map(v.parse,d['raw']))==raw
    supports=[];count=0
    for row in d['supports']:
        lam=Q(row['multiplier']);assert lam>=0;W=list(map(v.parse,row['W']));assert len(W)==T+1
        for l,r,point in cells(W[-1][0]):
            x=(l+r)/2;term=(Z,lam*x/2) if point else (lam/2,Z)
            nonneg(v.subtract(v.line(W[-1],x,point),term),l,r)
        for t in range(T-1,-1,-1):
            knots=set(W[t][0])|set(raw[t][0])|pullback(W[t+1])
            for l,r,point in cells(knots):
                x=(l+r)/2;a0=v.act(raw[t],x);w=v.line(W[t],x,point)
                for a in range(3):
                    change=int(a!=a0)
                    stage=(Z,lam*(x-v.COST[a])-change*(1+x)) if point else (lam-change,-lam*v.COST[a]-change)
                    rhs=v.plus(stage,v.qrow(W[t+1],a,x,point,False));nonneg(v.subtract(w,rhs),l,r);count+=1
        supports.append((lam,W))
    SUPPORT_CACHE[key]=(supports,count);return supports,count

def check_floor(Fs,V,eps,supports):
    for t,f in enumerate(Fs[:-1]):
        knots=set(f[0])|set(V[t][0])
        for _,W in supports:knots.update(W[t][0])
        for l,r,point in cells(knots):
            x=(l+r)/2;stored=v.line(f,x,point);budget=v.plus(v.line(V[t],x,point),(Z,-eps))
            valid=[(Z,Z)]+[v.subtract(v.scale(budget,lam),v.line(W[t],x,point)) for lam,W in supports]
            assert any(endpoints(v.subtract(stored,z),l,r)==(0,0) for z in valid)
    assert all(a==b==0 for a,b in Fs[-1][1]) and all(y==0 for y in Fs[-1][2])

def range_open(f,l,r):
    vals=[]
    for j in overlap(f[0],l,r):
        a,b=f[1][j];ll=max(l,f[0][j]);rr=min(r,f[0][j+1]);vals.extend((a*ll+b,a*rr+b))
    return min(vals),max(vals)

def qrange(f,action,l,r):
    cuts=sorted({l,r}|{x for x in pullback(f) if l<x<r});vals=[]
    for a,b in zip(cuts,cuts[1:]):vals.extend(endpoints(v.qrow(f,action,(a+b)/2,False,True),a,b))
    return min(vals),max(vals)

def check_restart(d,V,raw,supports):
    assert d['schema']=='NBO-R39-primary-restart-v1' and d['scale']==S
    Fs=list(map(v.parse,d['support']));eps=Q(d['epsilon']);check_floor(Fs,V,eps,supports)
    grids=parsegrid(d['grids']);T=d['T'];assert grids[-1]['lower']==[0];count=0
    for t in range(T-1,-1,-1):
        g,ng=grids[t],grids[t+1]
        assert all(x in g['xs'] for x in raw[t][0])
        for i,(l,r) in enumerate(zip(g['xs'],g['xs'][1:])):
            a0=v.act(raw[t],(l+r)/2);b=range_open(V[t],l,r)[0]-eps
            q=[qrange(V[t+1],a,l,r)[1] for a in range(3)];z=[]
            for a in range(3):
                c=Z
                for p,(aa,cc) in zip(v.PROBS,v.TRANS[a]):
                    ids=overlap(ng['xs'],aa*l+cc,aa*r+cc);c+=v.BETA*p*min(ng['lower'][j] for j in ids)
                z.append(c+(S*(1+l) if a!=a0 else Z))
            vertices=[z[a] for a in range(3) if q[a]>=b]
            for a in range(3):
                for aa in range(3):
                    if q[a]<b<q[aa]:vertices.append(((q[aa]-b)*z[a]+(b-q[a])*z[aa])/(q[aa]-q[a]))
            assert vertices
            bound=max(Z,S*range_open(Fs[t],l,r)[0],min(vertices))
            assert 0<=g['lower'][i]<=bound;count+=1
    g=grids[0]
    for name,lower in d['initial_lower'].items():
        integral=sum(Q(c,S)*mass(name,l,r) for l,r,c in zip(g['xs'],g['xs'][1:],g['lower']))
        assert Q(lower)<=integral
    return count

def verify_one(p):
    p=Path(p);tic=time.perf_counter();d=read(p);base=ROOT.parents[1]/d['base_file']
    assert hashlib.sha256(base.read_bytes()).hexdigest()==d['base_sha256']
    bd=read(base);assert d['raw']==bd['raw'] and d['V']==bd['V']
    V,J,raw,pol,operating=check_operating(d);cost=check_cost(d,pol)
    supports,supportcount=check_support(d['T'],d['proposal'],raw)
    rp=ROOT/'results/restart'/p.name.replace('random_','restart_');rd=read(rp)
    restart=check_restart(rd,V,raw,supports)
    out={'file':str(p.relative_to(ROOT)),'passed':True,'operating_cells_and_points':operating,
         'cost_cells':cost,'restart_cells':restart,'support_inequalities_for_horizon_rule':supportcount,
         'seconds':time.perf_counter()-tic,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
         'restart_sha256':hashlib.sha256(rp.read_bytes()).hexdigest()}
    print(out,flush=True);return out

def verify_group(paths):
    return [verify_one(p) for p in paths]

def main():
    import argparse
    from concurrent.futures import ProcessPoolExecutor
    ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=4);args=ap.parse_args()
    groups={}
    for p in sorted((ROOT/'results/randomized').glob('*.json.gz')):
        key=p.name.split('_eps')[0];groups.setdefault(key,[]).append(str(p))
    assert len(groups)==21
    if args.workers==1: batches=map(verify_group,groups.values());rows=[v for b in batches for v in b]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            rows=[v for b in pool.map(verify_group,groups.values()) for v in b]
    assert len(rows)==42
    (ROOT/'results/verify_continuum.json').write_text(json.dumps({'outcomes':rows,
         'independence':'SymPy parser and primitive rows; no constructor imports.',
         'support_families_checked':len(groups),'workers':args.workers,
         'point_mass_scope':'All-state operating checks include every knot; cost claims are integrated under the three absolutely continuous initial laws.'},sort_keys=True,indent=2)+'\n')
if __name__=='__main__':main()
