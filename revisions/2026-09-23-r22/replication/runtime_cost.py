"""Online conditional-price cost diagnostic; not an accuracy certificate."""
from pathlib import Path
import json,time
import numpy as np
from scipy.special import expit
from numpy.polynomial.legendre import leggauss
from numpy.polynomial.hermite import hermgauss
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r22'

def main():
    ds=[json.loads((REV/f'results/crossed/seed22000/vertex{v}/neural_adam/delivered_actor.json').read_text()) for v in range(4)]
    cs=[json.loads((REV/f'results/crossed/seed22000/vertex{v}/neural_adam/record.json').read_text())['delivered_certificate'] for v in range(4)]
    b=np.array([d['b'] for d in ds]);s=np.array([d['s'] for d in ds]);reserve=np.array([sum(c['reserve_interval'])/2 for c in cs])
    tg,tw=leggauss(8);z,zw=hermgauss(16);z*=np.sqrt(2);zw/=np.sqrt(np.pi)
    def prices(t,y,repeat):
        j0=min(15,int(t*16));jj=np.arange(j0,16);lo=np.maximum(t,jj/16);hi=(jj+1)/16
        q=lo[:,None]+(hi-lo)[:,None]*(tg+1)/2;w=(hi-lo)[:,None]*tw/2
        dt=q-t;lp=np.log(y)+.065*dt[:,:,None]+.3*np.sqrt(dt[:,:,None])*z
        bb=np.tile(b[:,jj],(repeat,1));ss=np.tile(s[:,jj],(repeat,1));rr=np.tile(reserve,repeat)
        sig=expit(bb[:,:,None,None]-ss[:,:,None,None]*lp)
        disc=np.exp(-.02*dt)*w
        price=rr*np.exp(-.02*(1-t))+np.sum((np.sum((.5+.3*sig)*zw,axis=-1))*disc,axis=(-1,-2))
        yd=np.sum(np.sum(-.3*ss[:,:,None,None]*sig*(1-sig)*zw,axis=-1)*disc,axis=(-1,-2))
        return price,-1.5*yd/price
    rows=[]
    for repeat in [1,2,4,8]:
        for _ in range(3):prices(.37,1.,repeat)
        ts=[];checksum=0.
        for j in range(256):
            t=.99*j/255;y=float(np.exp(-1+2*((37*j)%256)/255));start=time.perf_counter();v,p=prices(t,y,repeat)
            ts.append(time.perf_counter()-start);checksum+=float(v.sum()+p.sum())
        rows.append({'experts':4*repeat,'queries':256,'median_seconds':float(np.median(ts)),
          'p90_seconds':float(np.quantile(ts,.9)),'compiled_coefficient_bytes':4*repeat*16*3*8,
          'reserve_bytes':4*repeat*8,'maximum_quadrature_nodes_per_query':4*repeat*16*8*16,'finite_checksum':checksum})
    (REV/'results/runtime_cost.json').write_text(json.dumps({'rows':rows,
          'scope':'ordinary-float quadrature timing diagnostic, not a rigorous online price/hedge enclosure',
          'quadrature':[8,16],'network_forward_calls_online':0,
          'duplicated_experts_for_scaling_only':True,'certification_claim_for_timing_run':False},indent=2)+'\n')
if __name__=='__main__':main()
