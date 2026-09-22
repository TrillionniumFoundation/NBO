"""Third code path: closed truncated-lognormal moments and high-precision quadrature.
These are numerical cross-checks of independently CERTIFIED intervals; agreement
between precision levels is not itself used as a rigorous error bound.
"""
from pathlib import Path
import argparse,json,time,functools
import mpmath as mp
ROOT=Path(__file__).resolve().parents[3]

def check(pilot,dual,digits):
    start=time.perf_counter();mp.mp.dps=digits;data=json.loads(pilot.read_text());n=len(data['theta'])
    th=[mp.mpf(float(v)) for v in data['theta']];yy=mp.mpf(float(data['y0']));mu0=mp.log(yy);lo=mp.log(mp.mpf('.2'));hi=mp.log(12);lc=mp.log(mp.mpf('.8'))
    C=lambda x:mp.erfc(-x/mp.sqrt(2))/2
    @functools.lru_cache(maxsize=50000)
    def vals(t,j):
        m=2+sum(th[:j])/n+th[j]*(t-mp.mpf(j)/n);r=m-1;q=r/m;mu=mu0-mp.mpf('.025')*t;v=mp.mpf('.09')*t;s=mp.sqrt(v);a=-m*lc
        def cdf(l):return C((l-mu)/s)
        def moment(q,a,b):
            z1=(a-mu-q*v)/s;z2=(b-mu-q*v)/s;ee=mp.exp(q*mu+q*q*v/2)
            val=ee*(C(z2)-C(z1));first=(mu+q*v)*val+s*ee*(mp.exp(-z1*z1/2)-mp.exp(-z2*z2/2))/mp.sqrt(2*mp.pi)
            return val,first
        ya=mp.mpf('.2')*cdf(lo)+moment(1,lo,a)[0]
        ey=mp.mpf('.2')*cdf(lo)+moment(1,lo,hi)[0]+12*(1-cdf(hi))
        mq,mq1=moment(q,a,hi);pa=cdf(a);pb=1-cdf(hi)
        source=-mp.exp(-r*lc)/r*pa-mp.mpf('.8')*ya-m/r*mq-m/r*mp.exp(q*hi)*pb+mp.mpf('.01')*ey-mp.mpf('.004')*mp.log(mp.mpf('.5'))
        bc=mp.exp(-r*lc)*(1+r*lc)/r**2;bh=mp.exp(q*hi)*(1-q*hi)/r**2
        beta=bc*pa+(mq-q*mq1)/r**2+bh*pb;bl=-mq1/m**2
        return source,beta,bl
    result=[]
    for which in range(3):
        val=mp.mpf(0)
        for j in range(n):
            def f(t):return mp.exp(-mp.mpf('.04')*t)*vals(t,j)[which]*(mp.mpf('.00375')*t if which==2 else 1)
            # Explicit small-time cuts handle the initial switching layer.
            a,b=mp.mpf(j)/n,mp.mpf(j+1)/n
            cuts=[a]+([mp.mpf('0.00001'),mp.mpf('0.0001'),mp.mpf('0.001')] if j==0 else [])+[b]
            val+=mp.quad(f,cuts)
        result.append(val)
    b0=result[1]+mp.exp(-mp.mpf('.04'))*(-mp.mpf('.04')*sum(th)/n)
    intervals=[dual['source_integral_interval'],dual['b0_interval'],dual['covariance_interval']]
    values=[result[0],b0,result[2]]
    enclosed=[]
    for value,iv in zip(values,intervals):
        ok=mp.mpf(float(iv[0]))<=value<=mp.mpf(float(iv[1]));enclosed.append(bool(ok))
        if not ok:raise AssertionError('Closed-normal cross-check outside certified interval')
    return {'digits':digits,'source_integral':str(values[0]),'b0':str(values[1]),'covariance':str(values[2]),
      'inside_independent_intervals':enclosed,'seconds':time.perf_counter()-start,'method':'closed normal moments; mpmath quadrature',
      'scope':'high-precision numerical cross-check, not the interval proof or a proof from convergence'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--library',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--digits',nargs='+',type=int,default=[40,70]);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    for k in ['0.5','4.25','8']:
        d=json.loads((a.library/f'dual_k{k}.json').read_text());rows=[]
        for digits in a.digits:
            r=check(ROOT/d['pilot_path'],d,digits);rows.append(r);print(json.dumps({'k':k,**r}),flush=True)
            (a.out/f'k{k}.json').write_text(json.dumps({'k':float(k),'records':rows},indent=2)+'\n')
