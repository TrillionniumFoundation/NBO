"""New neural actors, independently ordered by stopped-policy value.
No inherited actor/witness enters training. The inherited certified upper
envelope is loaded only after all new actors have been generated.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
import sys,json,time,hashlib,resource,platform,argparse,copy
import numpy as np
import torch
from torch import nn
from numpy.polynomial.legendre import leggauss
from numpy.polynomial.hermite import hermgauss
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'revisions/2026-09-23-r19'
sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r16/replication'))
import mpfr_interval as M
sys.modules['interval64']=M
sys.path.insert(0,str(ROOT/'revisions/2026-09-22-r14/replication'))
from independent_primal import evaluate
from fresh_time_frontier import generate_policy
I,Q=M.I,M.I.rational
PROTOCOL='2e19256c5d40f7f0d090cccd6d86892958ae2147'
SEEDS=range(19100,19105);CHECKPOINTS=(0,50,200,800)
def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class TimeActor(nn.Module):
    def __init__(self):
        super().__init__();self.layers=nn.Sequential(nn.Linear(1,16),nn.Tanh(),nn.Linear(16,16),nn.Tanh(),nn.Linear(16,2))
        with torch.no_grad():
            self.layers[-1].weight.mul_(.1);self.layers[-1].bias[0]=0.;self.layers[-1].bias[1]=np.arctanh(-.5)
    def forward(self,t):return self.layers(t)
def proposal_setup(n=16):
    tg,tw=leggauss(16);zg,zw=hermgauss(40)
    tt=torch.tensor((np.arange(n)[:,None]+(tg+1)/2)/n);ww=torch.tensor(tw/(2*n));zz=torch.tensor(zg);wz=torch.tensor(zw/np.sqrt(np.pi))
    edges=torch.arange(n+1)/n;dw=(torch.exp(-.02*edges[:-1])-torch.exp(-.02*edges[1:]))/.02
    budget=1.25-.5*np.exp(-.02)-1e-7
    def controls(net):
        logits=net((2*(torch.arange(n)+.5)/n-1).reshape(n,1))
        raw=.006*torch.tanh(logits[:,0]);c=raw+(budget-(dw*raw).sum())/dw.sum()
        return c,.1+.1*torch.tanh(logits[:,1])
    def value(c,theta):
        mu=2+(torch.cumsum(theta,0)-theta)[:,None]/n+theta[:,None]*(tt-edges[:-1,None])
        u=mu[:,:,None]+.05*torch.sqrt(2*tt)[:,:,None]*zz
        flow=(-torch.exp(-(u-1)*torch.log(c[:,None,None]))/(u-1)*wz).sum(-1)-theta[:,None].square()
        xt=np.exp(.02)*(1.25-(c*dw).sum())
        return (torch.exp(-.04*tt)*flow*ww).sum()+np.exp(-.04)*(-.02*((theta.sum()/n)**2+.0025)+.1*torch.log(xt))
    return controls,value

def train(out, inline_gate=False):
    torch.set_num_threads(1);torch.set_default_dtype(torch.float64);controls,value=proposal_setup();rows=[]
    for seed in SEEDS:
        torch.manual_seed(seed);net=TimeActor();opt=torch.optim.Adam(net.parameters(),lr=.003);clock=time.perf_counter();verification_elapsed=0.;incumbent=None;incumbent_state=None;decisions=[]
        for step in range(max(CHECKPOINTS)+1):
            if step in CHECKPOINTS:
                with torch.no_grad():c,th=controls(net);v=float(value(c,th));cc=c.tolist();theta=th.tolist()
                layers=[{'weight':l.weight.detach().tolist(),'bias':l.bias.detach().tolist()} for l in net.layers if isinstance(l,nn.Linear)]
                base={'seed':seed,'step':step,'k':2.,'protocol_commit':PROTOCOL,'generation_seconds':time.perf_counter()-clock-verification_elapsed,
                      'initialization':'fresh random neural weights; no stored policy/value labels','proposal_value':v}
                netp=out/f'seed{seed}/network_step{step:04d}.json';write(netp,{**base,'architecture':'1-16-16-2 tanh; budget-normalized consumption and tanh preference outputs','layers':layers})
                ap=out/f'seed{seed}/actor_step{step:04d}.json';write(ap,{**base,'slabs':16,'c':cc,'theta':theta,'p':[0.]*16,
                    'network_path':str(netp.relative_to(ROOT)),'network_sha256':sha(netp),'deployment':'serialized dyadic 16-slab controls; network-to-policy compilation occurs once',
                    'scope':'neural-generated time-control subclass, not a whole-state feedback architecture'})
                rows.append({'seed':seed,'step':step,'actor_path':str(ap.relative_to(ROOT)),'actor_sha256':sha(ap),'generation_seconds':base['generation_seconds'],'proposal_value':v})
                print('GENERATED',seed,step,v,flush=True)
                if inline_gate:
                    gate_start=time.perf_counter();checked=evaluate(ap,'2')
                    write(ap.with_name(ap.stem.replace('actor','value')+'.json'),checked)
                    accepted=incumbent is None or checked['value_interval'][0]>incumbent['value_interval'][1]
                    decisions.append({'step':step,'accepted':accepted,'value_interval':checked['value_interval'],
                        'verification_finished_before_next_adam_update':True,'actor_sha256':sha(ap)})
                    if accepted:
                        incumbent=checked;incumbent_state=(copy.deepcopy(net.state_dict()),copy.deepcopy(opt.state_dict()))
                    else:
                        net.load_state_dict(incumbent_state[0]);opt.load_state_dict(incumbent_state[1])
                    verification_elapsed+=time.perf_counter()-gate_start
                    write(out/f'seed{seed}/inline_gate.json',decisions)
            if step<max(CHECKPOINTS):
                opt.zero_grad();c,th=controls(net);loss=-value(c,th);loss.backward();torch.nn.utils.clip_grad_norm_(net.parameters(),100);opt.step()
    write(out/'generated.json',rows);return rows

def upper_comparator():
    npth=ROOT/'revisions/2026-09-23-r16/results/fresh_library/nodes.json';nodes=json.loads(npth.read_text())
    lo=max((r for r in nodes if F(r['k'])<=2),key=lambda r:r['k']);hi=min((r for r in nodes if F(r['k'])>=2),key=lambda r:r['k'])
    lam=(F(hi['k'])-2)/(F(hi['k'])-F(lo['k']));u=Q(lam)*I(lo['U'])+Q(1-lam)*I(hi['U'])
    return {'optimal_upper':float(u.hi),'scope':'(0,2,1.25), k=2, unrestricted original continuous-time controls',
        'proof':'convexity of V in k and interpolation of two inherited directed optimal upper bounds',
        'endpoints':[lo,hi],'lambda_rational':str(lam),'source_path':str(npth.relative_to(ROOT)),'source_sha256':sha(npth),
        'shared_upper_historical_generation_seconds':sum(r['dual_generation_seconds'] for r in [lo,hi]),
        'shared_upper_historical_verification_seconds':sum(r['dual_verification_seconds'] for r in [lo,hi]),
        'timing_scope':'historical upper-comparator cost, not newly executed or silently free'}

def verify(out,rows,seed_filter=None):
    upper=upper_comparator();write(out/'upper_comparator.json',upper);result=[]
    seeds=[seed_filter] if seed_filter is not None else list(SEEDS)
    for seed in seeds:
        incumbent=None
        for row in [r for r in rows if r['seed']==seed]:
            ap=ROOT/row['actor_path'];vp=ap.with_name(ap.stem.replace('actor','value')+'.json')
            v=json.loads(vp.read_text()) if vp.exists() else evaluate(ap,'2')
            if v['actor_sha256']!=sha(ap):v=evaluate(ap,'2')
            write(vp,v)
            lower,high=v['value_interval'];margin=None if incumbent is None else (I(lower)-I(incumbent['value_interval'][1])).pair()
            accepted=incumbent is None or margin[0]>0
            rr={**row,'value_interval':v['value_interval'],'verification_seconds':v['seconds'],'accepted':accepted,
                'improvement_over_previous_incumbent_interval':margin,'regret_upper':float((I(upper['optimal_upper'])-I(lower)).hi),
                'target_0.01':bool((I(upper['optimal_upper'])-I(lower)).hi<Q('.01').lo),'state':[0,2,1.25],'portfolio':0,
                'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
            if incumbent is None:initial=rr
            rr['improvement_over_initial_lower']=float((I(lower)-I(initial['value_interval'][1])).lo)
            if accepted:incumbent=rr
            result.append(rr);write(out/f'seed{seed}/verified_results.json',[r for r in result if r['seed']==seed]);print('VERIFIED',seed,row['step'],rr['regret_upper'],margin,flush=True)
        corners=[]
        for u in ['1.98','2.02']:
            for x in ['1.24','1.26']:corners.append(evaluate(ROOT/incumbent['actor_path'],'2',u0=u,x0=x))
        write(out/f'seed{seed}/final_corner_values.json',corners)
    allrows=[]
    for seed in SEEDS:
        p=out/f'seed{seed}/verified_results.json'
        if p.exists():allrows.extend(json.loads(p.read_text()))
    write(out/'results.json',allrows)

def classical(out):
    torch.set_num_threads(1);torch.set_default_dtype(torch.float64);upper=upper_comparator();baseline=[]
    for n in [16,32,64]:
        ap=out/f'classical_slsqp_n{n}.json';a=generate_policy(n,2);write(ap,a);v=evaluate(ap,'2');write(out/f'classical_value_n{n}.json',v)
        baseline.append({'slabs':n,'actor_path':str(ap.relative_to(ROOT)),'value_interval':v['value_interval'],
            'generation_seconds':a['seconds'],'verification_seconds':v['seconds'],'optimizer_success':a['optimizer_success'],
            'regret_upper':float((I(upper['optimal_upper'])-I(v['value_interval'][0])).hi),
            'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'scope':'fresh non-neural time-control comparator; not Markov-chain or semi-Lagrangian'})
        write(out/'classical_frontier.json',baseline);print('CLASSICAL',n,baseline[-1]['regret_upper'],flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['train','verify','classical','all'],default='all');ap.add_argument('--seed',type=int);a=ap.parse_args()
    out=R/'results/policy_sensitive';out.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    if a.phase in ['train','all']:rows=train(out,inline_gate=(a.phase=='all'))
    else:rows=json.loads((out/'generated.json').read_text())
    if a.phase in ['verify','all']:verify(out,rows,a.seed)
    if a.phase in ['classical','all']:classical(out)
    write(out/f'resources_{a.phase}_{a.seed}.json',{'wall_seconds':time.perf_counter()-start,'python':platform.python_version(),'torch':torch.__version__,
          'numpy':np.__version__,'mpfr':M.VERSION,'threads':1,'protocol_commit':PROTOCOL,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
if __name__=='__main__':main()
