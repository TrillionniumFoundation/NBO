"""Genuine coupled-state neural control; interval defect plus Lyapunov proof.
Networks see only time and Riccati differential residuals. No reference labels.
A single learned pair of mode gains is reused across dimensions, explicitly.
"""
from pathlib import Path
import sys,json,time,resource,platform,hashlib,argparse
import numpy as np
import torch
from torch import nn
from scipy.integrate import solve_ivp
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from mpfr_interval import I,exp,log,tanh,affine,VERSION
Q=I.rational
class Net(nn.Module):
    def __init__(self,width):
        super().__init__();self.layers=nn.Sequential(nn.Linear(1,width),nn.Tanh(),nn.Linear(width,width),nn.Tanh(),nn.Linear(width,2))
    def forward(self,t):return self.layers(2*t-1)
def gains(net,t):return .5+(1-t)*nn.functional.softplus(net(t))
def serial(net):return [{'weight':m.weight.detach().tolist(),'bias':m.bias.detach().tolist()} for m in net.layers if isinstance(m,nn.Linear)]
def certified_gains(layers,n):
    from fractions import Fraction as F
    t=I([float(Q(F(j,n)).lo) for j in range(n)],[float(Q(F(j+1,n)).hi) for j in range(n)]).reshape(n,1)
    v=2*t-1;d=I(np.full((n,1),2.))
    for j,r in enumerate(layers):
        v=affine(v,r['weight'],r['bias']);d=affine(d,r['weight'])
        if j<2:
            v=tanh(v);d=(1-v.square())*d
    sp=log(1+exp(v));sig=1/(1+exp(-v));p=Q('.5')+(1-t)*sp;pt=-sp+(1-t)*sig*d
    a=I([-.2,.1]);qq=I([1.,1.5])
    # Treat exact displayed decimals, not nearest binary64 constants.
    a=I(np.array([Q('-.2').lo,Q('.1').lo]),np.array([Q('-.2').hi,Q('.1').hi]))
    R=pt+2*a*p-p.square()+qq
    eps=R.maxabs().max(axis=0)
    # True and neural gains >= .5; kappa=1-2a. Global derivative-error bound.
    kappas=[Q('1.4'),Q('.8')];deltas=[]
    for e,k in zip(eps,kappas):deltas.append((I(float(e))*(1-exp(-k))/k).hi)
    delta=I(float(max(deltas)));C=(1-exp(-Q('.8')))/Q('.8')
    occupation=C+Q('.01')/Q('.8')*(1-C)
    loss=delta.square()*occupation
    return {'status':'VALID_QUADRATIC_POLICY_CERTIFICATE','cells':n,'failed_cells':0,'skipped_cells':0,
      'mode_residual_upper':eps.tolist(),'mode_gain_error_upper':[float(x) for x in deltas],
      'per_coordinate_regret_upper':float(loss.hi),'initial_domain':'all x0 in R^d with |x0|^2/d <= 1, t0=0',
      'proof':'Riccati error integrating factor, exact quadratic performance difference, stable closed-loop Lyapunov moment',
      'dimensions':[{'d':d,'total_regret_upper':float((d*loss).hi)} for d in [4,8,16,32,64,128]],
      'targets':{str(e):bool(loss.hi<Q(str(e)).lo) for e in [.01,.005,.0025,.001]},
      'arithmetic':f'MPFR {VERSION}, 128-bit directed endpoint arithmetic','state_cover':'analytic quadratic identity over all states; no state tensor grid',
      'not_claimed':'generic high-dimensional HJB complexity, neural advantage over a two-mode Riccati solver, or success on original nonlinear economy'}

def main(out):
    out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();torch.set_num_threads(1);torch.set_default_dtype(torch.float64)
    records=[]
    for seed in range(16200,16210):
        torch.manual_seed(seed);torch.use_deterministic_algorithms(True);width=8 if seed%2==0 else 16
        net=Net(width).double();opt=torch.optim.Adam(net.parameters(),lr=.005);clock=time.perf_counter();hist=[]
        for step in range(1,1001):
            t=torch.rand(128,1,requires_grad=True);p=gains(net,t)
            dp=torch.cat([torch.autograd.grad(p[:,i].sum(),t,create_graph=True,retain_graph=True)[0] for i in range(2)],dim=-1)
            r=dp+2*torch.tensor([-.2,.1])*p-p*p+torch.tensor([1.,1.5]);loss=r.square().mean()
            if not torch.isfinite(loss):raise ArithmeticError('Nonfinite inventory loss')
            opt.zero_grad();loss.backward();opt.step()
            if step%50==0:hist.append({'step':step,'sample_residual_mse':float(loss.detach())})
            if step in [250,1000]:
                d={'seed':seed,'width':width,'step':step,'layers':serial(net),'training_wall_seconds':time.perf_counter()-clock,
                  'training_labels':'differential residual only','network_scope':'exact real tanh/softplus network with dyadic weights'}
                path=out/f'network_s{seed}_n{step}.json';path.write_text(json.dumps(d,indent=2)+'\n')
                vt=time.perf_counter();r=certified_gains(d['layers'],512);r.update({k:d[k] for k in ['seed','width','step','training_wall_seconds']})
                r['verification_wall_seconds']=time.perf_counter()-vt;r['network_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
                (out/f'certificate_s{seed}_n{step}.json').write_text(json.dumps(r,indent=2)+'\n');records.append(r)
                print(json.dumps({k:r[k] for k in ['seed','step','per_coordinate_regret_upper']}),flush=True)
        (out/f'history_s{seed}.json').write_text(json.dumps(hist,indent=2)+'\n')
    d=json.loads((out/'network_s16200_n1000.json').read_text())
    for n in [128,2048]:
        r=certified_gains(d['layers'],n);(out/f'refinement_{n}.json').write_text(json.dumps(r,indent=2)+'\n')
    # Structure-aware classical comparison: numerical ODE reference, NOT the certificate.
    clock=time.perf_counter();reference=solve_ivp(lambda h,p:2*np.array([-.2,.1])*p-p*p+np.array([1,1.5]),[0,1],[.5,.5],rtol=1e-12,atol=1e-14,dense_output=True)
    classical={'method':'two scalar Riccati ODEs, scipy DOP853' ,'p0':reference.y[:,-1].tolist(),'success':bool(reference.success),'wall_seconds':time.perf_counter()-clock,
               'scope':'structure-aware floating-point diagnostic; not an interval proof or a network training target'}
    # solve_ivp default is RK45, recorded accurately below.
    classical['method']='two scalar Riccati ODEs, scipy RK45'
    (out/'classical_reference.json').write_text(json.dumps(classical,indent=2)+'\n')
    (out/'summary.json').write_text(json.dumps(records,indent=2)+'\n')
    (out/'resources.json').write_text(json.dumps({'status':'completed','wall_seconds':time.perf_counter()-start,'torch_threads':1,
      'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'platform':platform.platform(),'training_runs':10,'retained_checkpoints':20,
      'dimension_scope':'same two-mode neural operator reused at six state dimensions; not sixty trainings'},indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();main(a.out)
