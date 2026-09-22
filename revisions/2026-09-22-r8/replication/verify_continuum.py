"""R8 continuous-generator witnesses, without simulated exits in the bound.

mpmath.iv outward interval arithmetic encloses all points of each rectangle.
Frozen binary64 policy entries are interpreted as exact real constants. The
bilinear extension is componentwise convex and feasible on the original box.
This is a verified (potentially loose) bound, not a precision-success flag.
"""
from __future__ import annotations
import hashlib, json, math, pathlib, time
import numpy as np
from mpmath import iv
iv.dps = 40
ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT/'revisions/2026-09-22-r8/results'
OLD = ROOT/'revisions/2026-09-21-r5/results'

def I(a, b=None):
    return iv.mpf(a if b is None else [a,b])
def low(v):
    return float(np.nextafter(float(v.a), -np.inf))
def high(v):
    return float(np.nextafter(float(v.b), np.inf))
def sq(v):
    return v**2

def flow(u,c,th,k='2'):
    return iv.exp((1-u)*iv.ln(c))/(1-u)-I(k)*sq(th)/2

def rg(u,x,c,th,p,k='2'):
    """R_a(G), G=-.02(u-2)^2+.1 log x, original NDU primitives."""
    G=-I('.02')*sq(u-2)+I('.1')*iv.ln(x)
    return (flow(u,c,th,k)-I('.04')*(u-2)*th+I('.002')
            +I('.006')*p-I('.1')*c/x-I('.00005')
            -I('.002')*sq(p)-I('.04')*G)

def upper_witness(cells=160):
    # For G, c=.8 is optimal since c^(-u)>.1/x; theta=-.04(u-2)/k;
    # p=.8 is optimal since .006-.004p>0 throughout [-.5,.8].
    max_rg=-math.inf
    for j in range(cells):
        u=I(I('1.2')+I('1.6')*j/cells, I('1.2')+I('1.6')*(j+1)/cells)
        for m in range(cells):
            x=I(I('.5')+I('1.5')*m/cells, I('.5')+I('1.5')*(m+1)/cells)
            v=(iv.exp((1-u)*iv.ln(I('.8')))/(1-u)+I('.0004')*sq(u-2)
               +I('.002')+I('.0048')-I('.08')/x-I('.00005')-I('.00128')
               +I('.0008')*sq(u-2)-I('.004')*iv.ln(x))
            max_rg=max(max_rg,high(v))
    alpha=float(np.nextafter(-max_rg,-np.inf))
    assert 0<alpha<8
    return alpha, max_rg

def certify_policy(tag,alpha):
    cfg=json.loads((OLD/(tag+'.json')).read_text())['config']
    assert cfg['k']==2 and cfg['fee']==8 and cfg['rho']==.04
    z=np.load(OLD/(tag+'.npz'))
    a=z['proposal'].reshape(cfg['n'],cfg['nu'],cfg['nx'],3)
    assert np.isfinite(a).all()
    assert (a>=np.array([.05,-.2,-.5])-1e-12).all()
    assert (a<=np.array([.8,.2,.8])+1e-12).all()
    min_rg=math.inf
    for n in range(cfg['n']):
        for j in range(cfg['nu']-1):
            u=I(I('1.2')+I('1.6')*j/(cfg['nu']-1),I('1.2')+I('1.6')*(j+1)/(cfg['nu']-1))
            for m in range(cfg['nx']-1):
                x=I(I('.5')+I('1.5')*m/(cfg['nx']-1),I('.5')+I('1.5')*(m+1)/(cfg['nx']-1))
                block=a[n,j:j+2,m:m+2].reshape(4,3)
                c,th,p=[I(float(block[:,i].min()),float(block[:,i].max())) for i in range(3)]
                r=rg(u,x,c,th,p,str(cfg['k']))+8+I('.32')*(1-I(n+1)/cfg['n'])
                min_rg=min(min_rg,low(r))
    beta=max(0.,float(np.nextafter(-min_rg,np.inf)))
    C=(1-iv.exp(-I('.04')))/I('.04')
    bound=high(8+(I(beta)-I(alpha))*C)
    return {'tag':tag,'n':cfg['n'],'cells':cfg['n']*(cfg['nu']-1)*(cfg['nx']-1),
        'policy_sha256':hashlib.sha256((OLD/(tag+'.npz')).read_bytes()).hexdigest(),
        'lower_residual_bound':min_rg,'beta':beta,'alpha':alpha,
        'continuous_regret_upper_bound_t0':bound,'target':.01,'meets_target':bound<=.01,
        'deployment':'R5 raw nodal proposal, bilinear state feedback, frozen between dates',
        'process':'original continuous Brownian NDU with exact first exit',
        'scope':'uniform real-arithmetic witness bound; not floating-point runtime conformance'}

def run():
    OUT.mkdir(parents=True,exist_ok=True); start=time.perf_counter()
    alpha,r=upper_witness()
    tags=['n6_s10_w48_a600_c800_lr0.004','n12_s10_w48_a600_c800_lr0.004']
    records=[certify_policy(tag,alpha) for tag in tags]
    payload={'arithmetic':'mpmath.iv 40 decimal digits, outward binary64 output',
        'upper_rg':r,'alpha':alpha,'records':records,'seconds':time.perf_counter()-start,
        'note':'Every time/state cell and the full continuous control domain is covered. The wide bound is retained, not reported as numerical convergence.'}
    (OUT/'continuum_witnesses.json').write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps(payload,indent=2))
if __name__=='__main__': run()
