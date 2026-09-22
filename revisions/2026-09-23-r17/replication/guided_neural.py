"""Complete-cover proposal objective and independent MPFR acceptance loop."""
from pathlib import Path
import sys,json,time,hashlib,resource,platform,argparse
import numpy as np
import torch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];R16=ROOT/'revisions/2026-09-23-r16/replication'
sys.path.insert(0,str(R16));import accessibility_certificate as C
from accessibility_neural import Net,serialize
import interval_objective as D

def run(out,seed,width,all_faces=False,steps=(0,100,400),lr=.003):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(1);torch.set_default_dtype(torch.float64);torch.manual_seed(seed);np.random.seed(seed);torch.use_deterministic_algorithms(True)
    actor=Net(3,width).double();critic=Net(1,width).double()
    with torch.no_grad():
        actor.layers[-1].weight.mul_(.1);critic.layers[-1].weight.mul_(.1)
        actor.layers[-1].bias.copy_(torch.atanh(torch.tensor([(.75-.425)/.375,.5,-.15/.65])))
        critic.layers[-1].bias.fill_(6.7)
    pars=list(actor.parameters())+list(critic.parameters());opt=torch.optim.Adam(pars,lr=lr)
    exact,idx=C.cell_grid(4,16,16);s=D.I(torch.tensor(exact.lo),torch.tensor(exact.hi))
    protocol={'seed':seed,'width':width,'all_faces':all_faces,'steps':list(steps),'lr':lr,'temperature':.15,'grid':[4,16,16],'delta':2**-24,'proposal_arithmetic':'torch float64, NOT certified','acceptance':'strict decrease in independent full-cover MPFR bound','selection':'raw proposals all retained; incumbent not substituted for proposals'}
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');ph=hashlib.sha256((out/'protocol.json').read_bytes()).hexdigest()
    start=time.perf_counter();generation=0.;audit_time=0.;history=[];ledger=[];inc=float('inf');incpath=None
    for step in range(max(steps)+1):
        if step:
            tick=time.perf_counter();loss=D.objective(s,actor,critic,all_faces=all_faces)
            if not torch.isfinite(loss):raise ArithmeticError('Nonfinite proposal objective')
            opt.zero_grad();loss.backward();torch.nn.utils.clip_grad_norm_(pars,100);opt.step();generation+=time.perf_counter()-tick
            if step%20==0:history.append({'step':step,'proposal_upper_surrogate':float(loss.detach()),'generation_seconds':generation})
        if step in steps:
            d={'format':'binary64 weights round-trip JSON','version':'R17','seed':seed,'step':step,'width':width,'k':2,'all_faces_ablation':all_faces,'actor':serialize(actor),'critic':serialize(critic),'protocol_sha256':ph,'training_wall_seconds':generation}
            p=out/f'network_step{step:04d}.json';p.write_text(json.dumps(d,indent=2)+'\n')
            with torch.no_grad():surrogate=float(D.objective(s,actor,critic,all_faces=all_faces))
            r=C.audit(p,out/f'certificate{step}.json',(4,16,16),chunk=1024);audit_time+=r['wall_seconds'];bound=r['t0_regret_upper'];accepted=bound<inc
            if accepted:inc=bound;incpath=p.name
            ledger.append({'step':step,'raw_bound':bound,'proposal_surrogate':surrogate,'accepted':accepted,'incumbent_bound':inc,'incumbent_network':incpath,'generation_seconds':generation,'audit_seconds_cumulative':audit_time,'total_seconds':time.perf_counter()-start,'certificate':f'certificate{step}.json'})
            (out/'acceptance.json').write_text(json.dumps(ledger,indent=2)+'\n');(out/'history.json').write_text(json.dumps(history,indent=2)+'\n')
    (out/'resources.json').write_text(json.dumps({'wall_seconds':time.perf_counter()-start,'generation_seconds':generation,'audit_seconds':audit_time,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'torch':torch.__version__,'numpy':np.__version__,'platform':platform.platform(),'threads':1,'seeds_retained':True},indent=2)+'\n')
    return ledger
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--seed',type=int,default=17000);p.add_argument('--width',type=int,default=16);p.add_argument('--steps',nargs='+',type=int,default=[0,100,400]);p.add_argument('--all-faces',action='store_true');p.add_argument('--lr',type=float,default=.003)
    a=p.parse_args();run(a.out,a.seed,a.width,a.all_faces,a.steps,a.lr)
