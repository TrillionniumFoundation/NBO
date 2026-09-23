"""R28 fixed-schedule recentered transport and coupled rollback.
The differentiable objective only proposes policies. Unchanged MPFR stopped-
payoff enclosures decide deployment. Historical dual inputs are explicit.
"""
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json, os, platform, resource, sys, time
from pathlib import Path
import numpy as np
import torch
os.environ['BACKEND']='mpfr'
ROOT=Path(__file__).resolve().parents[3]
REV=ROOT/'revisions/2026-09-24-r28';OUT=REV/'results/central'
spec=importlib.util.spec_from_file_location('r28_inherited_study',ROOT/'revisions/2026-09-23-r24/replication/study.py')
S=importlib.util.module_from_spec(spec);sys.modules[spec.name]=S;spec.loader.exec_module(S)
torch.set_num_threads(1);torch.set_default_dtype(torch.float64);torch.use_deterministic_algorithms(True)

def clean(x):
    if isinstance(x,torch.Tensor):return x.detach().cpu().tolist()
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [clean(v) for v in x]
    return x

def write(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(clean(x),indent=2,allow_nan=False)+'\n')

def sha(x):return hashlib.sha256(json.dumps(clean(x),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def state(net,opt=None):return {'network':copy.deepcopy(net.state_dict()),'optimizer':copy.deepcopy(opt.state_dict()) if opt else None}
def flatten_state(opt,params,key):return torch.cat([opt.state[p][key].flatten() for p in params])
def interval_width(c):return c['value_interval'][1]-c['value_interval'][0] if c.get('status')=='CERTIFIED' else None

def mechanism(seed,orders):
    start=time.perf_counter();setupstart=start
    neural=S.network(seed);carrier=copy.deepcopy(neural);obj=S.setup(orders=orders)
    opt=torch.optim.Adam(S.parameters(neural),lr=.08);q=S.CHART
    m=torch.zeros(len(S.vector(carrier)));v=m.clone()
    setup_seconds=time.perf_counter()-setupstart
    history=[];ngen=cgen=diagnostic=0.
    for t in range(1,201):
        ts=time.perf_counter();old=torch.tensor(S.vector(carrier));raw=carrier(S.NODES).detach().flatten()
        economic=S.Coordinates(raw,q);economic.zero_grad(set_to_none=True)
        loss=-obj(economic);loss.backward();g=economic.z.grad.detach().clone()
        B=q.T@S.flat_jacobian(carrier);gp=B.T@g
        m=.9*m+.1*gp;v=.999*v+.001*gp.square()
        dp=-.08*(m/(1-.9**t))/((v/(1-.999**t)).sqrt()+1e-8)
        S.assign(carrier,(old+dp).numpy());newraw=carrier(S.NODES).detach().flatten()
        realized=q.T@(newraw-raw);remainder=realized-B@dp
        cgen+=time.perf_counter()-ts
        ts=time.perf_counter();opt.zero_grad(set_to_none=True);nloss=-obj(neural);nloss.backward();opt.step()
        ngen+=time.perf_counter()-ts
        ts=time.perf_counter();params=S.parameters(neural)
        history.append({'step':t,'neural_surrogate_payoff_before':-float(nloss.detach()),
          'carrier_surrogate_payoff_before':-float(loss.detach()),
          'parameter_discrepancy_linf':float(np.max(np.abs(S.vector(neural)-S.vector(carrier)))),
          'first_moment_discrepancy_linf':float((flatten_state(opt,params,'exp_avg')-m).abs().max()),
          'second_moment_discrepancy_linf':float((flatten_state(opt,params,'exp_avg_sq')-v).abs().max()),
          'output_discrepancy_linf':float((neural(S.NODES).detach().flatten()-newraw).abs().max()),
          'economic_carrier_recenter_discrepancy':0.,'effective_trust_scale':1.,'output_cap_active':False,
          'parameter_step_norm':float(dp.norm()),'quotient_output_step_norm':float(realized.norm()),
          'nonlinear_remainder_retained_norm':float(remainder.norm()),
          'moment_state_dimensions':len(m),'linearized_output_step_norm':float((B@dp).norm())})
        diagnostic+=time.perf_counter()-ts
    path=OUT/f'mechanism_s{seed}_q{orders[0]}_{orders[1]}'
    finals={}
    for name,net in [('neural',neural),('recentered_transport',carrier)]:
        actor=obj(net,True);write(path/f'{name}_actor.json',actor)
        write(path/f'{name}_parameters.json',net.state_dict())
        cert,seconds=S.cert(actor) if seed==27101 else ({'status':'NOT_REQUESTED_IN_FROZEN_PROTOCOL'},0.)
        finals[name]={'certificate':cert,'checker_seconds':seconds,'actor_sha256':sha(actor)}
    write(path/'carrier_moments.json',{'m':m,'v':v,'step':200})
    write(path/'neural_optimizer.json',opt.state_dict());write(path/'history.json',history)
    row={'seed':seed,'orders':orders,'steps':200,'rate':.08,'setup_seconds':setup_seconds,
       'neural_generation_seconds':ngen,'transport_generation_seconds':cgen,'diagnostic_seconds':diagnostic,
       'finals':finals,'max_parameter_discrepancy':max(h['parameter_discrepancy_linf'] for h in history),
       'max_first_moment_discrepancy':max(h['first_moment_discrepancy_linf'] for h in history),
       'max_second_moment_discrepancy':max(h['second_moment_discrepancy_linf'] for h in history),
       'max_output_discrepancy':max(h['output_discrepancy_linf'] for h in history),
       'max_retained_nonlinear_remainder':max(h['nonlinear_remainder_retained_norm'] for h in history),
       'max_economic_carrier_mismatch':0.,'capped_steps':0,'standalone_seconds':time.perf_counter()-start,
       'process_high_water_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
       'algebraic_equivalence_is_a_theorem_not_a_floating_point_test':True,
       'historical_dual_construction_included':False}
    write(path/'summary.json',row);print('MECHANISM',seed,orders,row['max_parameter_discrepancy'],flush=True);return row

def production(seed,method,gated):
    start=time.perf_counter();modelstart=start
    neural=S.network(seed);net=neural if method=='neural_adam' else S.Coordinates(neural(S.NODES).detach(),S.CHART)
    obj=S.setup(orders=(8,16));rate=.08 if method=='neural_adam' else .32
    opt=torch.optim.Adam(S.parameters(net),lr=rate) if method.endswith('adam') else None
    setup_seconds=time.perf_counter()-modelstart
    initial_actor=obj(net,True);inc,initial_seconds=S.cert(initial_actor)
    if inc.get('status')!='CERTIFIED':raise RuntimeError(f'Initial checker failed: {inc}')
    path=OUT/f'production_s{seed}_{method}_{"gated" if gated else "ungated"}'
    write(path/'initial_actor.json',initial_actor);write(path/'initial_certificate.json',inc)
    rows=[];generation=checking=bookkeeping=0.;calls=0;accepted=0;rejected=0
    for block in range(1,5):
        ts=time.perf_counter();saved=state(net,opt);saved_sha=sha(saved);before=copy.deepcopy(inc)
        bookkeeping+=time.perf_counter()-ts
        ts=time.perf_counter()
        if opt:
            hist=[]
            for step in range(100):
                opt.zero_grad(set_to_none=True);loss=-obj(net);loss.backward()
                if not torch.isfinite(loss) or any(not torch.isfinite(p.grad).all() for p in S.parameters(net)):
                    raise FloatingPointError('Nonfinite production proposal; run retained as failure')
                opt.step();hist.append({'step':step+1,'surrogate_loss_before':float(loss.detach())})
            gen=time.perf_counter()-ts;ncall=100;termination='fixed_100_call_block'
        else:
            ans=S.optimize(net,obj,'lbfgsb',rate,cap=100,checkpoints=(100,))
            gen=ans['generation_seconds'];ncall=ans['gradient_calls'];termination=ans['termination'];hist=ans['history']
        generation+=gen;calls+=ncall;candidate=obj(net,True);candidate_state=state(net,opt)
        cert,check_seconds=S.cert(candidate);checking+=check_seconds
        ts=time.perf_counter();margin=(cert['value_interval'][0]-before['value_interval'][1]) if cert.get('status')=='CERTIFIED' and before.get('status')=='CERTIFIED' else None
        passes=margin is not None and margin>0
        if gated and not passes:
            net.load_state_dict(saved['network'])
            if opt:opt.load_state_dict(saved['optimizer'])
            rejected+=1;restored_sha=sha(state(net,opt));assert restored_sha==saved_sha
            deployment='REJECT_AND_RESTORE';inc=before
        else:
            inc=cert;restored_sha=None;accepted+=1;deployment='ACCEPT_CERTIFIED' if gated else 'DEPLOY_WITHOUT_GATE'
        book=time.perf_counter()-ts;bookkeeping+=book
        actual=state(net,opt)
        row={'block':block,'candidate_certificate':cert,'incumbent_before':before,'deployed_certificate':inc,
           'strict_margin':margin,'candidate_interval_width':interval_width(cert),'gate_passed':passes,'deployment':deployment,
           'saved_state_sha256':saved_sha,'candidate_state_sha256':sha(candidate_state),'deployed_state_sha256':sha(actual),
           'restored_state_sha256':restored_sha,'rollback_exact':restored_sha==saved_sha if restored_sha else None,
           'generation_seconds':gen,'checker_seconds':check_seconds,'decision_and_restore_seconds':book,
           'gradient_calls':ncall,'termination':termination,'candidate_actor_sha256':sha(candidate)}
        write(path/f'block_{block}/history.json',hist);write(path/f'block_{block}/candidate_actor.json',candidate)
        write(path/f'block_{block}/saved_state.json',saved);write(path/f'block_{block}/candidate_state.json',candidate_state)
        write(path/f'block_{block}/deployed_state.json',actual);write(path/f'block_{block}/decision.json',row);rows.append(row)
    final_actor=obj(net,True);write(path/'final_actor.json',final_actor)
    row={'seed':seed,'method':method,'gated':gated,'rate':rate if opt else None,'orders':[8,16],
      'blocks':4,'calls_per_block_cap':100,'gradient_calls':calls,'setup_seconds':setup_seconds,
      'initial_checker_seconds':initial_seconds,'generation_seconds':generation,'checker_seconds':checking,
      'bookkeeping_seconds':bookkeeping,'standalone_elapsed_seconds':time.perf_counter()-start,
      'measured_component_sum_seconds':setup_seconds+initial_seconds+generation+checking+bookkeeping,
      'accepted_blocks':accepted,'rejected_blocks':rejected,'decisions':rows,'initial_certificate':json.loads((path/'initial_certificate.json').read_text()),
      'final_certificate':inc,'final_actor_sha256':sha(final_actor),
      'all_rejections_restored_exact':all(a['rollback_exact'] for a in rows if a['deployment']=='REJECT_AND_RESTORE'),
      'lbfgsb_restarted_in_both_arms':True,'historical_dual_construction_included':False,
      'process_high_water_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      'timing_scope':'serial same-process measured pipeline including all initial and block checks; cached validated quadrature shared, historical dual inputs separately identified'}
    write(path/'summary.json',row);print('PRODUCTION',seed,method,gated,inc.get('regret_upper'),rejected,flush=True);return row

def main():
    p=argparse.ArgumentParser();p.add_argument('--part',choices=['mechanism','production','all'],default='all');args=p.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    lib=ROOT/'revisions/2026-09-23-r16/results/fresh_library'
    inputs={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in lib.glob('*.json')}
    write(OUT/'environment.json',{'python':sys.version,'numpy':np.__version__,'torch':torch.__version__,'platform':platform.platform(),
      'backend':'mpfr','torch_threads':torch.get_num_threads(),'historical_dual_inputs_sha256':inputs,
      'dual_construction_measured_in_this_script':False,'shared_quadrature_cache_charge':'first certifier call includes construction; subsequent standalone timings are warm-cache, not true cold runs'})
    if args.part in ['all','mechanism']:
        rows=[mechanism(seed,orders) for seed in [27101,27102,27103] for orders in [(8,16),(12,24)]];write(OUT/'mechanism_summary.json',rows)
    if args.part in ['all','production']:
        rows=[production(seed,method,gated) for seed in [27201,27202] for method in ['neural_adam','direct_adam','direct_lbfgsb'] for gated in [False,True]];write(OUT/'production_summary.json',rows)
if __name__=='__main__':main()
