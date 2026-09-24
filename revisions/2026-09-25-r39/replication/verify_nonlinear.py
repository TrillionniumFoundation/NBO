"""Independent nonlinear checker: SymPy endpoint geometry + Python big integers.
No multistate/Boxes, NumPy arithmetic, or construction routine is imported.
NumPy is used only to read the published arrays. All subsequent arithmetic is
scalar arbitrary precision, and installed-rule regions are independently cut.
"""
from pathlib import Path
import json,hashlib,time
from itertools import product
from sympy import Rational as Q, floor, ceiling
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'2026-09-24-r38';S=1<<34
COEFF=[((65,5,0,3),(70,3,0,2)),((15,3,70,2),(70,3,0,2)),((65,5,0,3),(15,4,70,2)),((10,2,80,2),(10,2,80,2))]
COST=[Q(0),Q(9,50),Q(9,50),Q(8,25)]
def down(q):return int(floor(q))
def up(q):return int(ceiling(q))
def raw(x,y):return 3 if x<Q(1,4) and y<Q(1,4) else 1 if x<Q(9,20) else 2 if y<Q(9,20) else 0

def geometry(n):
    coordinates=[]
    for i in range(n):
        l,r=Q(i,n),Q(i+1,n);cuts=sorted({l,r}|{q for q in (Q(1,4),Q(9,20)) if l<q<r})
        coordinates.append(sorted(set(cuts+[(a+b)/2 for a,b in zip(cuts,cuts[1:])])))
    images=[[[] for _ in (0,1)] for a in range(4)];rlo=[[] for _ in range(4)];rhi=[[] for _ in range(4)];klo=[[] for _ in range(4)];khi=[[] for _ in range(4)];gl=[];gh=[]
    for i in range(n):
        for j in range(n):
            xl,xr=Q(i,n),Q(i+1,n);yl,yr=Q(j,n),Q(j+1,n)
            possible={raw(x,y) for x,y in product(coordinates[i],coordinates[j])}
            gl.append(down((xl+yl)*S/4));gh.append(up((xr+yr)*S/4))
            for a in range(4):
                rlo[a].append(down(((xl+yl)/2-COST[a])*S));rhi[a].append(up(((xr+yr)/2-COST[a])*S))
                klo[a].append(0 if a in possible else down((1+(xl+yl)/2)*S))
                khi[a].append(0 if possible=={a} else up((1+(xr+yr)/2)*S))
                for z in (0,1):
                    ranges=[]
                    for component,(s,b,c,d) in enumerate(COEFF[a]):
                        vals=[(s*(x if component==0 else y)+b*x*y+c+d*z)/100 for x,y in product((xl,xr),(yl,yr))]
                        low,high=min(vals),max(vals);assert 0<=low<=high<=1
                        il=min(n-1,down(n*low));ih=min(n-1,down(n*high));ranges.append(range(il,ih+1))
                    images[a][z].append([x*n+y for x,y in product(*ranges)])
    return images,rlo,rhi,klo,khi,gl,gh

def verify(row,check_upper=True):
    tic=time.perf_counter();n,T=row['mesh'],row['T'];M=n*n;eps=Q(row['epsilon']);p=ROOT/'results'/row['proof_file']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['proof_sha256']
    dat=np.load(p);data={name:dat[name].ravel().tolist() for name in dat.files}
    assert all(len(v)==M and all(type(x) is int for x in v) for v in data.values())
    im,rl,rh,kl,kh,gl,gh=geometry(n)
    def continuation(v,a,i,upper):
        vals=[(max if upper else min)(v[j] for j in im[a][z][i]) for z in (0,1)]
        q=19*(3*vals[0]+2*vals[1]);return -(-q//100) if upper else q//100
    prices=list(map(Q,row['prices']));mus=row['local_multipliers'];assert all(q>=0 for q in prices+mus)
    for i in range(M):
        assert data[f'L_{T}'][i]<=gl[i]<=gh[i]<=data[f'U_{T}'][i]
        assert data[f'F_{T}'][i]==data[f'B_{T}'][i]==0
        for lam in prices:assert data[f'W_{str(lam).replace("/","_")}_{T}'][i]>=up(lam*gh[i])
    counts={'state_date_cells':0,'support_action_inequalities':0}
    for t in range(T-1,-1,-1):
        for i in range(M):
            lo=[rl[a][i]+continuation(data[f'L_{t+1}'],a,i,False) for a in range(4)]
            hi=[rh[a][i]+continuation(data[f'U_{t+1}'],a,i,True) for a in range(4)]
            assert data[f'L_{t}'][i]<=max(lo) and data[f'U_{t}'][i]>=max(hi)
            floors=[0]
            for lam in prices:
                key=str(lam).replace('/','_');w=data[f'W_{key}_{t}'][i];wn=data[f'W_{key}_{t+1}']
                for a in range(4):
                    assert w>=up(lam*rh[a][i])-kl[a][i]+continuation(wn,a,i,True)
                    counts['support_action_inequalities']+=1
                floors.append(down(lam*(data[f'L_{t}'][i]-up(eps*S)))-w)
            assert data[f'F_{t}'][i]<=max(floors)
            z=[kl[a][i]+continuation(data[f'B_{t+1}'],a,i,False) for a in range(4)]
            dual=[min(z[a]+mu*(data[f'L_{t}'][i]-up(eps*S)-hi[a]) for a in range(4)) for mu in mus]
            assert 0<=data[f'B_{t}'][i]<=max([data[f'F_{t}'][i]]+dual)
            counts['state_date_cells']+=1
    lower=Q(sum(data['B_0']),M*S);assert lower==Q(row['restart_support_lower'])
    upper=None;maxgap=0
    if check_upper and row.get('upper_source'):
        policies=np.load(OLD/'results'/row['upper_source'])['policy'].reshape(T,M).tolist();jl=gl[:];cu=[0]*M
        for t in range(T-1,-1,-1):
            newj=[];newc=[]
            for i,a in enumerate(policies[t]):
                assert a in range(4)
                newj.append(rl[a][i]+continuation(jl,a,i,False))
                newc.append(kh[a][i]+continuation(cu,a,i,True))
            jl,cu=newj,newc;maxgap=max(maxgap,max(data[f'U_{t}'][i]-jl[i] for i in range(M)))
        upper=Q(sum(cu),S*M);assert upper<=Q(row['upper']) and Q(maxgap,S)<=eps
        assert lower<=upper
    return {'passed':True,'T':T,'mesh':n,'epsilon':str(eps),'lower':str(lower),'independently_recomputed_upper':str(upper) if upper is not None else None,
       'regret_bound':str(Q(maxgap,S)) if upper is not None else None,'seconds':time.perf_counter()-tic,**counts,
       'arithmetic':'SymPy Rational endpoint geometry and Python arbitrary-precision scalar integer induction'}
if __name__=='__main__':
    data=json.loads((ROOT/'results/nonlinear_support.json').read_text());rows=[]
    for T,n in ((8,64),(32,64)):
        row=next(r for r in data['outcomes'] if r['T']==T and r['mesh']==n);v=verify(row);rows.append(v);print(v,flush=True)
    (ROOT/'results/verify_nonlinear.json').write_text(json.dumps({'outcomes':rows,'coverage':'Only the named complete objects; no independent label is assigned to unlisted meshes.'},sort_keys=True,indent=2)+'\n')
