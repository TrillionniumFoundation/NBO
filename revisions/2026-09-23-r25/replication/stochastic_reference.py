"""Full state-time verification in a manufactured unspanned-risk economy.
No sample, floating loss or two-grid difference is an accuracy certificate.
The optimal witness is supplied by construction, explicitly not learned.
"""
from __future__ import annotations
import hashlib,json,math,sys,time
from pathlib import Path
import numpy as np
import torch
from scipy.optimize import minimize
from numpy.polynomial.legendre import leggauss
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r25'
sys.path.insert(0,str(ROOT/'revisions/2026-09-22-r14/replication'))
import interval64 as IA
I=IA.I;Q=I.rational
PROTOCOL='b0e932c49b02759a7bcda3b30c534fdc390999b7'
torch.set_default_dtype(torch.float64);torch.set_num_threads(1);torch.use_deterministic_algorithms(True)

def write(p,o):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2,allow_nan=False)+'\n')

def controls(t,x,z):return (.8+.2*t)*(1/x+.1*z),.64*(1+.1*x*z)
def tensor_rule():
    nodes=[];weights=[]
    for n,lo,hi in ((5,0,1),(9,.5,2),(7,-1,1)):
        g,w=leggauss(n);nodes.append((lo+hi)/2+(hi-lo)*g/2);weights.append(w/2)
    g=np.stack(np.meshgrid(*nodes,indexing='ij'),-1).reshape(-1,3)
    w=np.prod(np.stack(np.meshgrid(*weights,indexing='ij'),-1),-1).reshape(-1)
    return torch.tensor(g),torch.tensor(w),nodes[1]

class Actor(torch.nn.Module):
    def __init__(self):
        super().__init__();self.layers=torch.nn.ModuleList([torch.nn.Linear(3,12),torch.nn.Linear(12,12),torch.nn.Linear(12,2)])
    def forward(self,s):
        q=torch.stack([2*s[:,0]-1,(s[:,1]-1.25)/.75,s[:,2]],-1)
        for layer in self.layers[:-1]:q=torch.tanh(layer(q))
        return torch.sigmoid(self.layers[-1](q))*torch.tensor([2.2,1.])
    def export(self):return [{'w':l.weight.detach().tolist(),'b':l.bias.detach().tolist()} for l in self.layers]

class Limit(Exception):pass

def fit(seed):
    path=REV/f'results/stochastic_reference/neural{seed}'
    if (path/'fit.json').exists():return json.loads((path/'fit.json').read_text())
    torch.manual_seed(seed);net=Actor();s,w,_=tensor_rule();aa,pp=controls(s[:,0],s[:,1],s[:,2]);aa=aa.detach();pp=pp.detach()
    params=list(net.parameters());sizes=[p.numel() for p in params];history=[];calls=0;start=time.perf_counter()
    def vector():return np.concatenate([p.detach().numpy().ravel() for p in params]).copy()
    def assign(x):
        at=0
        with torch.no_grad():
            for p,n in zip(params,sizes):p.copy_(torch.tensor(x[at:at+n]).reshape(p.shape));at+=n
    accepted=vector();initial=net.export()
    def fun(x):
        nonlocal calls
        if calls>=2500:raise Limit()
        assign(x);net.zero_grad(set_to_none=True);a=net(s)
        deficit=((a[:,0]-aa).square()+.0625*(.8+.2*s[:,0])*(a[:,1]-pp).square())/2
        loss=(w*deficit).sum();loss.backward();calls+=1
        g=np.concatenate([p.grad.detach().numpy().ravel() for p in params]).copy()
        if not np.isfinite(g).all():raise FloatingPointError('reference nonfinite gradient')
        history.append({'call':calls,'loss':float(loss.detach()),'gradient_norm':float(np.linalg.norm(g)),'seconds':time.perf_counter()-start})
        return float(loss.detach()),g
    def callback(x):
        nonlocal accepted
        accepted=x.copy()
    try:
        r=minimize(fun,accepted,jac=True,method='L-BFGS-B',callback=callback,
            options={'maxiter':2500,'maxfun':2500,'maxls':40,'ftol':1e-15,'gtol':1e-10})
        assign(r.x);termination=str(r.message)
    except Limit:assign(accepted);termination='2500-call cap, last accepted iterate'
    out={'seed':seed,'type':'neural','layers':net.export(),'initial_layers':initial,'calls':calls,
         'generation_seconds':time.perf_counter()-start,'termination':termination,
         'known_witness_used_in_training':True,'orders':[5,9,7],'architecture':[3,12,12,2],
         'protocol_commit':PROTOCOL,'final_training_loss':history[-1]['loss']}
    write(path/'history.json',history);write(path/'fit.json',out);print('REFERENCE FIT',seed,calls,out['final_training_loss'],flush=True)
    return out

def exact_interval(s):
    t,x,z=s[:,0],s[:,1],s[:,2];A=Q('.8')+Q('.2')*t
    a=A*(1/x+Q('.1')*z);p=Q('.64')*(1+Q('.1')*x*z)
    val=IA.stack([a,p],axis=-1)
    deriv=[IA.stack([Q('.2')*(1/x+Q('.1')*z),I(np.zeros(t.lo.shape))],axis=-1),
           IA.stack([-A/x.square(),Q('.064')*z],axis=-1),IA.stack([Q('.1')*A,Q('.064')*x],axis=-1)]
    return val,deriv

def neural_interval(s,layers,derivatives=True):
    n=s.lo.shape[0];t,x,z=s[:,0],s[:,1],s[:,2]
    h=IA.stack([2*t-1,(x-Q('1.25'))/Q('.75'),z],axis=-1)
    d=[]
    if derivatives:
        for i,scale in enumerate((I(2),1/Q('.75'),I(1))):
            basis=np.zeros((n,3));basis[:,i]=1;d.append(I(basis)*scale)
    for i,l in enumerate(layers):
        w=np.asarray(l['w']);h=IA.affine(h,w,np.asarray(l['b']))
        if derivatives:d=[IA.affine(q,w) for q in d]
        if i<2:
            h=IA.tanh(h);factor=(1-h.square()).intersect(0,1)
        else:
            h=1/(1+IA.exp(-h));factor=(h*(1-h)).intersect(0,.25)
        if derivatives:d=[q*factor for q in d]
    scales=IA.stack([Q('2.2'),I(1)]);h=h*scales;d=[q*scales for q in d]
    return h,d

def horner(x,coef):
    r=I(np.zeros(x.lo.shape))
    for c in reversed(coef):r=r*x+I(c)
    return r

def direct_interval(s,coef,derivatives=True):
    t,x,z=s[:,0],s[:,1],s[:,2];A=Q('.8')+Q('.2')*t;xi=(x-Q('1.25'))/Q('.75')
    P=horner(xi,coef);a=A*(P+Q('.1')*z);p=Q('.64')*(1+Q('.1')*x*z)
    val=IA.stack([a,p],axis=-1);deriv=[]
    if derivatives:
        dx=horner(xi,[i*coef[i] for i in range(1,len(coef))])/Q('.75')
        deriv=[IA.stack([Q('.2')*(P+Q('.1')*z),I(np.zeros(t.lo.shape))],axis=-1),
               IA.stack([A*dx,Q('.064')*z],axis=-1),IA.stack([Q('.1')*A,Q('.064')*x],axis=-1)]
    return val,deriv

def cover(shape):
    # All endpoints and centers are dyadic: no rounding uncertainty in cover.
    edges=[np.linspace(lo,hi,n+1) for n,(lo,hi) in zip(shape,((0,1),(.5,2),(-1,1)))]
    lo=np.stack(np.meshgrid(*[e[:-1] for e in edges],indexing='ij'),-1).reshape(-1,3)
    hi=np.stack(np.meshgrid(*[e[1:] for e in edges],indexing='ij'),-1).reshape(-1,3)
    return lo,hi

def verify(fit,name):
    path=REV/f'results/stochastic_reference/{name}';attempts=[];start=time.perf_counter()
    fn=(lambda s,d:neural_interval(s,fit['layers'],d)) if fit['type']=='neural' else (lambda s,d:direct_interval(s,fit['coefficients'],d))
    for shape in ((8,32,16),(16,64,32),(32,128,64)):
        lo,hi=cover(shape);center=(lo+hi)/2;radius=(hi-lo)/2;bounds=[];error_bounds=[]
        for a in range(0,len(lo),1024):
            sl=slice(a,a+1024);box=I(lo[sl],hi[sl]);mid=I(center[sl]);actor,dactor=fn(box,True);_,dexact=exact_interval(box)
            ac,_=fn(mid,False);ec,_=exact_interval(mid);err=I((ac-ec).maxabs())
            for k in range(3):err=err+I((dactor[k]-dexact[k]).maxabs())*I(radius[sl,k:k+1])
            A=Q('.8')+Q('.2')*box[:,0]
            deficit=(err[:,0].square()+Q('.0625')*A*err[:,1].square())/2
            bounds.append(deficit.hi);error_bounds.append(err.hi)
        d=np.concatenate(bounds);errors=np.concatenate(error_bounds);D=I(float(d.max()))
        C=(1-IA.exp(-Q('.04')))/Q('.04');bound=(C*D).hi
        attempt={'shape':list(shape),'cells':len(lo),'hamiltonian_deficit_upper':float(D.hi),'regret_upper':float(bound),
                 'max_investment_error_upper':float(errors[:,0].max()),'max_portfolio_error_upper':float(errors[:,1].max()),
                 'cumulative_verification_seconds':time.perf_counter()-start,'complete_cover':True,'failed_cells':0}
        attempts.append(attempt);print('REFERENCE VERIFY',name,shape,float(bound),flush=True)
        if bound<=.001:break
    path.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(path/'cell_bounds.npz',lower=lo,upper=hi,deficit_upper=d,action_error_upper=errors)
    restarts=[]
    for t in (0,.25,.5,.75,1):
        Ct=(1-IA.exp(-Q('.04')*(1-I(t))))/Q('.04')
        # The mathematical terminal factor is exactly zero.
        b=0. if t==1 else float((Ct*D).hi)
        restarts.append({'start_time':t,'all_states_regret_upper':b})
    out={'status':'CERTIFIED','economy':'manufactured unspanned-risk stopped investment benchmark',
         'is_original_economy':False,'current_state_only':True,'domain':{'t':[0,1],'x':[.5,2],'z':[-1,1]},
         'target':.001,'target_established':bool(bound<=.001),'attempts':attempts,'final':attempt,'restart_slices':restarts,
         'stopping_face_discrepancy':0,'proof':'exact Hamiltonian completion and bounded stopped Ito formula',
         'verification_seconds':time.perf_counter()-start,'generation_seconds':fit['generation_seconds'],
         'cell_array_sha256':hashlib.sha256((path/'cell_bounds.npz').read_bytes()).hexdigest(),
         'interval_backend':'inherited R14 rational-Taylor outward binary64','protocol_commit':PROTOCOL,
         'known_witness_used_in_training':True,'stochastic_paths_not_used_for_certificate':True,
         'action_admissibility':'sigmoid architecture' if fit['type']=='neural' else 'box projection; unprojected error upper-bounds projected error'}
    write(path/'certificate.json',out);return out

def main():
    out=[]
    for seed in (25201,25202):
        fitdata=fit(seed);out.append({'method':'neural','seed':seed,'fit':fitdata,'certificate':verify(fitdata,f'neural{seed}')})
    start=time.perf_counter();_,_,x=tensor_rule();xi=(x-1.25)/.75
    cheb=np.polynomial.chebyshev.chebfit(xi,1/x,8);coeff=np.polynomial.chebyshev.cheb2poly(cheb)
    fitdata={'type':'direct','coefficients':coeff.tolist(),'generation_seconds':time.perf_counter()-start,
             'degree':8,'known_witness_used_in_training':True,'fit_nodes':x.tolist(),
             'deployment_action_projection':[[0.,2.2],[0.,1.]],
             'certificate_uses_unprojected_error_and_nonexpansiveness':True}
    write(REV/'results/stochastic_reference/direct/fit.json',fitdata)
    out.append({'method':'direct','seed':None,'fit':fitdata,'certificate':verify(fitdata,'direct')})
    write(REV/'results/stochastic_reference_summary.json',out)
if __name__=='__main__':main()
