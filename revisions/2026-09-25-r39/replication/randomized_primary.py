"""All-restart feasible common Markov lotteries on the unchanged R38 continuum.
Operating values are exact piecewise affine. Lottery probabilities are affine
ratios. Dyadic interval costs cover open cells; positive affine transitions
preserve null sets, so the stated initial integrals include no point masses.
"""
from pathlib import Path
from fractions import Fraction as F
from bisect import bisect_left,bisect_right
import sys,json,gzip,hashlib,time,resource,argparse
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'2026-09-24-r38'
sys.path.insert(0,str(OLD/'replication'))
import kernel as k
Z,O=F(0),F(1);S=1<<40

def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def encode(v):
    if isinstance(v,F):return str(v)
    if isinstance(v,dict):return {a:encode(b) for a,b in v.items()}
    if isinstance(v,(tuple,list)):return [encode(z) for z in v]
    return v

def save(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);b=json.dumps(encode(v),sort_keys=True).encode()
    p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b+b'\n')

def floor(x):return x.numerator//x.denominator
def ceil(x):return -((-x.numerator)//x.denominator)
def affine_value(ab,x):return ab[0]*x+ab[1]

def construct(raw,V,eps):
    T=len(raw);J=[None]*T+[k.affine(F(1,2))];pol=[None]*T
    for t in reversed(range(T)):
        qs=k.q_functions(J[t+1]);qraw=k.select(qs,raw[t]);qbest,best=k.envelope(qs)
        budget=k.linear_comb([V[t]],[O],b=-eps)
        J[t],_=k.envelope([qraw,budget])
        num=k.linear_comb([J[t],qraw],[O,-O]);den=k.linear_comb([qbest,qraw],[O,-O])
        assert num.extent()[0]>=0 and k.linear_comb([den,num],[O,-O]).extent()[0]>=0
        assert k.linear_comb([J[t],V[t]],[O,-O]).extent()[1]<=0
        pol[t]={'raw':raw[t],'best':best,'num':num,'den':den}
    return J,pol

def cost_boxes(pol,N):
    T=len(pol);grids=[None]*T+[{'xs':[Z,O],'lower':[0],'upper':[0]}]
    for t in reversed(range(T)):
        pp=pol[t];xs=sorted({F(j,N) for j in range(N+1)}|{x for f in pp.values() for x in f.xs})
        ng=grids[t+1];cl=[];cu=[];pl=[];pu=[];ra=[];ba=[]
        for l,r in zip(xs,xs[1:]):
            mid=(l+r)/2;a=int(pp['raw'].at(mid));b=int(pp['best'].at(mid));na=pp['num'].line(mid);da=pp['den'].line(mid)
            if na==(Z,Z):pmin=pmax=Z
            else:
                vals=[]
                for x in (l,r):
                    nn=affine_value(na,x);dd=affine_value(da,x)
                    assert dd>0 and 0<=nn<=dd;vals.append(nn/dd)
                pmin,pmax=min(vals),max(vals)
            plo=floor(S*pmin);phi=ceil(S*pmax);assert 0<=plo<=phi<=S
            def cont(action,upper):
                vals=[]
                for m,c in k.MAPS[action]:
                    il=max(0,bisect_right(ng['xs'],m*l+c)-1)
                    ir=min(len(ng['lower'])-1,bisect_left(ng['xs'],m*r+c)-1)
                    assert il<=ir
                    vals.append((max if upper else min)(ng['upper' if upper else 'lower'][il:ir+1]))
                numerator=19*(3*vals[0]+2*vals[1])
                return -(-numerator//100) if upper else numerator//100
            alo,ahi=cont(a,False),cont(a,True);blo,bhi=cont(b,False),cont(b,True)
            wlo=floor((1+l)*S) if a!=b else 0;whi=ceil((1+r)*S) if a!=b else 0
            low=min((S-p)*alo+p*(blo+wlo) for p in (plo,phi))//S
            high=-(-max((S-p)*ahi+p*(bhi+whi) for p in (plo,phi))//S)
            assert 0<=low<=high
            cl.append(low);cu.append(high);pl.append(plo);pu.append(phi);ra.append(a);ba.append(b)
        grids[t]={'xs':xs,'lower':cl,'upper':cu,'probability_lower':pl,'probability_upper':pu,'raw':ra,'best':ba}
    integrals={}
    for name in ('uniform','high_condition','low_condition'):
        low=high=0;g=grids[0]
        for l,r,cl,cu in zip(g['xs'],g['xs'][1:],g['lower'],g['upper']):
            mass=r-l if name=='uniform' else r*r-l*l if name=='high_condition' else 2*(r-l)-(r*r-l*l)
            low+=floor(cl*mass);high+=ceil(cu*mass)
        integrals[name]={'lower':F(low,S),'upper':F(high,S)}
    return grids,integrals

def weighted_pw(f,name):
    if name=='uniform':return f.integral()
    val=Z
    for (a,b),l,r in zip(f.ab,f.xs,f.xs[1:]):
        high=2*a*(r**3-l**3)/3+b*(r*r-l*l)
        val+=high if name=='high_condition' else a*(r*r-l*l)+2*b*(r-l)-high
    return val

def run(N=1024):
    primary=read(OLD/'results/primary.json')['outcomes'];diag=read(OLD/'results/gap_study.json')['outcomes']
    dm={(v['T'],v['proposal'],v['epsilon']):v for v in diag};rows=[]
    for row in sorted(primary,key=lambda z:(z['T'],z['proposal'],F(z['epsilon']))):
        tic=time.perf_counter();source=OLD/'results'/row['proof_file'];base=read(source)
        raw=list(map(k.PW.load,base['raw']));V=list(map(k.PW.load,base['V']));eps=F(base['epsilon'])
        J,pol=construct(raw,V,eps);grids,integrals=cost_boxes(pol,N)
        d=dm[(row['T'],row['proposal'],row['epsilon'])];gf=read(OLD/'results'/d['proof_file']);support=k.PW.load(gf['B_V_refined'][0])
        inherited=k.PW.load(base['C'][0]);detlower=k.PW.load(base['lower'][0])
        scopes={}
        for name,value in integrals.items():
            lo=weighted_pw(support,name);old=weighted_pw(inherited,name);up=min(value['upper'],old)
            if name=='uniform':lo=max(lo,F(row['inherited_randomized_lower']))
            assert lo<=up,(row['T'],row['proposal'],lo,up)
            scopes[name]={'lower':lo,'upper':up,'lottery_cost_lower':value['lower'],'lottery_cost_upper':value['upper'],
               'lottery_cost_width':value['upper']-value['lower'],'inherited_deterministic_upper':old,
               'deterministic_lower':weighted_pw(detlower,name),'gap':up-lo,'relative_gap':(up-lo)/up if up else Z,
               'strict_randomized_improvement':bool(value['upper']<weighted_pw(detlower,name))}
        name=f"random_H{row['T']}_{row['proposal']}_eps{str(eps).replace('/','_')}.json.gz"
        proof={'schema':'NBO-R39-continuum-randomized-v1','T':row['T'],'epsilon':str(eps),'proposal':row['proposal'],
               'base_file':str(source.relative_to(ROOT.parents[1])),'base_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
               'model':base['model'],'V':base['V'],'operating_policy':base['operating_policy'],'raw':base['raw'],
               'J':[z.dump() for z in J],'policy':[{a:b.dump() for a,b in z.items()} for z in pol],
               'cost_grids':grids,'scale':S,'mesh':N,'initial_bounds':scopes,
               'policy_class':'randomized_Markov_common_continuation','constraint':'every_time_every_state',
               'cost_integral_scope':'absolutely_continuous_initial_distribution; finite isolated points have zero mass'}
        p=ROOT/'results/randomized'/name;save(p,proof)
        out={a:proof[a] for a in ('T','epsilon','proposal','policy_class','constraint','mesh')}
        out.update(initial_bounds=scopes,proof_file='randomized/'+name,proof_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
             max_operating_pieces=max(len(j.ab) for j in J),max_cost_cells=max(len(z['lower']) for z in grids),
             seconds=time.perf_counter()-tic,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        rows.append(out);save(ROOT/'results/randomized_primary.json',{'outcomes':rows,'development_cohort':True})
        z=scopes['uniform'];print(row['T'],row['proposal'],str(eps),float(z['lower']),float(z['upper']),float(z['lottery_cost_width']),z['strict_randomized_improvement'],out['seconds'],flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--mesh',type=int,default=1024);args=ap.parse_args();run(args.mesh)
