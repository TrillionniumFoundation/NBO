"""Validated payoff/first/second derivatives on an unchanged-economy slice.
Constant c=3/4, p=0, theta in [-1/5,1/5], (u0,x0)=(2,5/4).
Analytic Gaussian moments plus geometric/exponential remainder bounds;
MPFR directed endpoints, and an explicit stopped-path likelihood-ratio bridge.
"""
from __future__ import annotations
import json, math, sys, time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-24-r28'
sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r16/replication'))
import mpfr_interval as M
I=M.I;Q=I.rational
N=100;K=20;RHO=Q('0.04');SIG=Q('0.05')

def write(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def factorial2(n):
    r=1
    for j in range(n,0,-2):r*=j
    return r

def polynomial():
    """Full Gaussian-moment polynomial; no sample quadrature is certified."""
    started=time.perf_counter();a=M.log(Q(F(4,3)));c=[I(1)]
    for n in range(1,N+1):c.append(a**n/Q(math.factorial(n))-c[-1])
    moments=[];time_tail=M.exp(RHO)*RHO**(K+1)/Q(math.factorial(K+1))
    for m in range(N+1):
        v=I(0)
        for ell in range(K+1):v=v+(-RHO)**ell/Q(math.factorial(ell)*(m+ell+1))
        moments.append(v+I(-float(time_tail.hi),float(time_tail.hi)))
    coeff=[I(0) for _ in range(N+1)]
    for n in range(N+1):
        for j in range(0,n+1,2):
            factor=Q(math.comb(n,j)*factorial2(j-1))*SIG**j*moments[n-j//2]
            coeff[n-j]=coeff[n-j]-Q(F(4,3))*c[n]*factor
    x1=(Q('1.25')-Q('0.75')/Q('0.02'))*M.exp(Q('0.02'))+Q('0.75')/Q('0.02')
    assert float(x1.lo)>.5 and float(x1.hi)<1.25
    coeff[0]=coeff[0]+M.exp(-RHO)*(-Q('0.02')*SIG.square()+Q('0.1')*M.log(x1))
    coeff[2]=coeff[2]-Q('0.02')*M.exp(-RHO)
    return coeff,moments[0],x1,time.perf_counter()-started

def error_budgets(k):
    """Bounds for derivative orders 0,1,2, uniformly over the theta box."""
    e=M.exp(Q(-50));tail=[2*e/Q(10),2*e]
    for j in range(2,N+3):tail.append(2*Q(10)**(j-1)*e+Q(j-1)*tail[j-2])
    q=Q('0.7');central=2*q**(N+1)/(1-q)
    poly_tail=[]
    for r in range(3):
        v=I(0)
        for n in range(N+1):
            for j in range(n+1):
                v=v+2*Q(math.comb(n,j))*Q('0.2')**(n-j)*SIG**j*tail[j+r]
        poly_tail.append(v)
    flow=[central+6*tail[0]+poly_tail[0],
          (central+6*tail[1]+poly_tail[1])/SIG,
          (2*central+6*(tail[2]+tail[0])+poly_tail[2]+poly_tail[0])/SIG.square()]
    terminal=[Q('.0144')*tail[0]+Q('.0001')*tail[2],
              (Q('.0144')*tail[1]+Q('.0001')*tail[3])/SIG,
              (Q('.0144')*(tail[2]+tail[0])+Q('.0001')*(tail[4]+tail[2]))/SIG.square()]
    pexit=4*M.exp(Q(-72));root=M.sqrt(pexit);H=Q('14.4');kk=Q(k)
    stopping=[2*H*pexit,2*H*root/SIG+kk*Q('.2')*pexit,
        2*H*M.sqrt(2*pexit)/SIG.square()+2*kk*Q('.2')*root/SIG+kk*pexit]
    total=[flow[j]+terminal[j]+stopping[j] for j in range(3)]
    return total,{'exit_probability_upper':float(pexit.hi),'central_series_remainder':float(central.hi),
        'flow_remainders':[float(v.hi) for v in flow],'terminal_remainders':[float(v.hi) for v in terminal],
        'stopped_bridge_remainders':[float(v.hi) for v in stopping],
        'total_remainders':[float(v.hi) for v in total],'path_payoff_absolute_bound':14.4,
        'gaussian_cutoff':10,'geometric_degree':N,'discount_taylor_degree':K}

def horner(coeff,x):
    v=I(0)
    for c in reversed(coeff):v=v*x+c
    return v

class Oracle:
    def __init__(self,k):
        start=time.perf_counter();self.k=F(k);self.coeff,mass,self.x1,_=polynomial()
        self.coeff[2]=self.coeff[2]-Q(self.k)*mass/2
        self.err,self.budget=error_budgets(self.k)
        self.derivatives=[self.coeff]
        for _ in range(2):self.derivatives.append([Q(j)*c for j,c in enumerate(self.derivatives[-1])][1:])
        self.setup_seconds=time.perf_counter()-start;self.calls=0;self.seconds=0.
    def evaluate(self,theta,order=0):
        start=time.perf_counter();x=theta if isinstance(theta,I) else Q(theta)
        v=horner(self.derivatives[order],x);e=float(self.err[order].hi)
        out=v+I(-e,e);self.calls+=1;self.seconds+=time.perf_counter()-start
        return out
    def smoothness(self):
        rows=[]
        for i in range(80):
            lo=F(-1,5)+F(i,200);hi=lo+F(1,200)
            cell=I(float(Q(lo).lo),float(Q(hi).hi));v=self.evaluate(cell,2)
            rows.append({'theta_interval':[str(lo),str(hi)],'second_derivative_interval':v.pair()})
        upper=max(v['second_derivative_interval'][1] for v in rows);lower=min(v['second_derivative_interval'][0] for v in rows)
        assert upper<0
        return {'lipschitz_gradient_bound':max(abs(lower),abs(upper)),'strong_concavity_lower':-upper,'cells':rows}

class OracleUnresolved(Exception):pass

def poll(o,h,start,L):
    sigma=F(1,100);kappa=F(1,100000);x=F(start);lo=F(-1,5);hi=F(1,5);rows=[];calls=0;started=time.perf_counter()
    def checked(y):
        nonlocal calls
        v=o.evaluate(y);calls+=1
        if float((I(v.hi)-I(v.lo)).hi)>float(Q(kappa*h*h).lo):raise OracleUnresolved('requested interval width unattained')
        return v
    for iteration in range(10000):
        incumbent=checked(x);accepted=False;trials=[]
        for direction in (-1,1):
            candidate=x+direction*h
            if not lo<=candidate<=hi:
                trials.append({'direction':direction,'status':'GEOMETRIC_SHORT_FACE','distance_to_face':str(x-lo if direction<0 else hi-x)})
                continue
            v=checked(candidate);accept=float(v.lo)>float((I(incumbent.hi)+Q(sigma*h*h)).hi)
            trials.append({'direction':direction,'theta':str(candidate),'interval':v.pair(),'accepted':accept})
            if accept:x=candidate;accepted=True;break
        rows.append({'iteration':iteration,'incumbent_interval':incumbent.pair(),'deployed_theta':str(x),'accepted':accepted,'trials':trials})
        if not accepted:break
    else:raise RuntimeError('poll resource cap; no stationarity claim')
    C=float((Q(sigma)+2*Q(kappa)+Q(F.from_float(L))/2).hi)
    return x,{'mesh':str(h),'start':str(start),'theta':str(x),'oracle_calls':calls,'status':'COMPLETE_UNSUCCESSFUL_FEASIBLE_POLL',
        'projected_gradient_tau1_bound':float((Q(h)*Q(F.from_float(max(1.,C)))).hi),
        'actual_final_gradient_interval':o.evaluate(x,1).pair(),'payoff_interval':o.evaluate(x).pair(),
        'elapsed_seconds':time.perf_counter()-started,'trajectory':rows,'forcing_sigma':str(sigma),'oracle_kappa':str(kappa)}

def global_slice_gap(o,x,m):
    """Strong-concavity upper model, maximized over the actual feasible interval."""
    gradient=o.evaluate(x,1);dl=Q(F(-1,5)-x);du=Q(F(1,5)-x);upper=I(0)
    for g in (float(gradient.lo),float(gradient.hi)):
        z=min(float(du.hi),max(float(dl.lo),g/m))
        v=I(g)*I(z)-Q(F.from_float(m))*I(z).square()/2
        upper=I(0,max(float(upper.hi),float(v.hi)))
    if (x==F(1,5) and float(gradient.lo)>=0) or (x==F(-1,5) and float(gradient.hi)<=0):return 0.
    safe=I(max(abs(float(gradient.lo)),abs(float(gradient.hi)))).square()/(2*Q(F.from_float(m)))
    return float(safe.hi)

def main():
    records=[]
    for k in (F(1,2),F(2)):
        overall=time.perf_counter();o=Oracle(k);smooth=o.smoothness();x=F(0);polls=[]
        for h in (F(1,25),F(1,50),F(1,100),F(1,200)):
            x,r=poll(o,h,x,smooth['lipschitz_gradient_bound']);polls.append(r)
        a,b=F(-1,5),F(1,5)
        if float(o.evaluate(b,1).lo)>0:opt_interval=[str(b),str(b)];kind='upper-face global optimum'
        elif float(o.evaluate(a,1).hi)<0:opt_interval=[str(a),str(a)];kind='lower-face global optimum'
        else:
            for _ in range(34):
                c=(a+b)/2;g=o.evaluate(c,1)
                if float(g.lo)>0:a=c
                elif float(g.hi)<0:b=c
                else:break
            opt_interval=[str(a),str(b)];kind='unique interior global optimum bracket'
        gap=global_slice_gap(o,x,smooth['strong_concavity_lower'])
        record={'k':str(k),'constant_controls':{'c':'3/4','p':'0','theta_box':['-1/5','1/5']},
            'initial_state':['0','2','5/4'],'wealth_at_horizon_interval':o.x1.pair(),'error_budget':o.budget,
            'smoothness':smooth,'polls':polls,'optimal_theta_interval':opt_interval,'optimum_type':kind,
            'final_poll_theta':str(x),'restricted_class_global_regret_upper':gap,'restricted_target_0_01_met':gap<=.01,
            'original_full_state_target_met':False,'financed_47_dimensional_gradient_bridge_established':False,
            'setup_seconds':o.setup_seconds,'oracle_total_calls_including_derivative_audit':o.calls,
            'oracle_total_seconds_including_derivative_audit':o.seconds,'standalone_seconds':time.perf_counter()-overall,
            'arithmetic':'MPFR directed 128-bit intermediate arithmetic, outward binary64 endpoints',
            'theorem_scope':'unchanged stopped economy, single initial state and one-dimensional admissible constant-control class'}
        write(REV/f'results/slice_k{str(k).replace("/","_")}.json',record);records.append(record)
        print('SLICE',k,x,gap,kind,opt_interval,flush=True)
    write(REV/'results/slice_summary.json',records)
if __name__=='__main__':main()
