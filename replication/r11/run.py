"""Execute R11 science; fail closed if any required certificate fails."""
from __future__ import annotations
import os, sys, time, json, hashlib, platform, itertools
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
from pathlib import Path
import numpy as np
import scipy
from core import (ROOT, BOX, EPS, Model, Contract, Directional, Joint,
                  first_moments, r7, old, SIGNS)
from contracts import arithmetic_audit
OUT=ROOT/'replication/r11/output'

def dump(name,data):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(r7.serial(data),indent=2,allow_nan=False)+'\n')

def selected_direct(base,c,z,lam,d):
    """Independent Bellman evaluation of the selected stopping policy.
    Uses selected-control transitions, not CSR reward or transition arrays.
    """
    p=z['p'];v=np.empty_like(z['v']);v[-1]=base.terminal
    acts=base.e[0].controls(np.minimum(p,c.na-1));ss=base.e[0].states
    for n in range(7,-1,-1):
        value=np.zeros(base.ns)
        for prob,e in zip((1-lam,lam),base.e):
            y,live,disc,flow,_,_,alpha=old.transition(ss,acts[n],1/8,e.model)
            ann=-np.expm1(-e.model.rho*alpha/8)/e.model.rho
            value+=prob*np.mean(flow+d*ann+disc*np.where(live,old.interpolate(v[n+1].reshape(e.shape),y),old.terminal(y)),axis=-1)
        stopped=p[n]==c.stop;value[stopped]=base.terminal[stopped]-c.fee
        v[n]=value
    # Date zero of z is the inherited finite menu; compare later common values.
    return float(abs(v[1:]-z['v'][1:]).max())

def directional(base):
    rows=[];witness=None
    for lam,d in itertools.product((0.,.125,.25),(.4,.425,.45)):
        sol={}
        for mode,adj in (('full',True),('up',True),('down',True),('zero',False)):
            cc=Directional(base,0.,8,'full' if mode=='zero' else mode)
            sol[mode]=cc.pair(lam,d,adj)
        rows.append({'law':lam,'benefit':d,'differences':{m:float(z['positive']['value'][0,base.center]-z['nonpositive']['value'][0,base.center]) for m,z in sol.items()},
                     'up_full_initial_error':max(float(abs(sol['full'][s]['value'][0,base.center]-sol['up'][s]['value'][0,base.center])) for s in SIGNS),
                     'down_zero_initial_error':max(float(abs(sol['down'][s]['value'][0,base.center]-sol['zero'][s]['value'][0,base.center])) for s in SIGNS)})
        if lam==.125 and d==.425:
            i=int(np.linalg.norm(base.e[0].states-[1.25,1.59375],axis=1).argmin());s='nonpositive'
            witness={'state':base.e[0].states[i], 'full_minus_up':sol['full'][s]['value'][0,i]-sol['up'][s]['value'][0,i],
                     'down_minus_zero':sol['down'][s]['value'][0,i]-sol['zero'][s]['value'][0,i]}
        print('DIRECTION',lam,d,rows[-1]['differences'],flush=True)
    assert max(max(r['up_full_initial_error'],r['down_zero_initial_error']) for r in rows)<2e-11
    return {'nine_point_replays':rows,'alternative_initial_state':witness,'scope':'Point diagnostics; continuum direction is established separately by the transport certificate.'}

def parts(base,state,action,v,lam,d):
    out=np.zeros(5)
    for prob,e in zip((1-lam,lam),base.e):
        y,live,disc,flow,effort,_,alpha=old.transition(np.asarray(state)[None,:],np.asarray(action)[None,:],1/8,e.model)
        ann=-np.expm1(-e.model.rho*alpha/8)/e.model.rho
        gv=old.terminal(y);vg=old.interpolate(base.terminal.reshape(e.shape),y)
        vv=old.interpolate(v.reshape(e.shape),y)
        out+=prob*np.array([(flow+e.model.k*effort+d*ann).mean(),(-e.model.k*effort).mean(),
                            (disc*(~live)*gv).mean(),(disc*live*vg).mean(),(disc*live*(vv-vg)).mean()])
    return out

def mechanism(joint):
    base=joint.base;ans={}
    for name,F,m in (('noncancellable',0.,8),('active_center',.8,1)):
        aa=joint.solve(.125,.425,F,True,.8,.5,m);zz=joint.solve(.125,.425,F,False,.8,.5,m)
        row={}
        for s in SIGNS:
            act=aa['first'][s]['action'];zero=act.copy();zero[1]=0.
            if not np.allclose(zero,zz['first'][s]['action'],rtol=0,atol=2e-13):raise AssertionError('financial replacement term is not zero')
            local=parts(base,[2,1.25],act,aa['v'][1],.125,.425)-parts(base,[2,1.25],zero,aa['v'][1],.125,.425)
            future=sum(parts(base,[2,1.25],zero,aa['v'][1],.125,.425)-parts(base,[2,1.25],zero,zz['v'][1],.125,.425))
            actual=aa['first'][s]['value']-zz['first'][s]['value']
            assert abs(sum(local)+future-actual)<2e-11
            row[s]={'local_components':local,'local_gain':sum(local),'future_option':future,'actual_option':actual,'reconstruction_error':abs(sum(local)+future-actual)}
        row['relative_local']=row['positive']['local_gain']-row['nonpositive']['local_gain']
        row['relative_future']=row['positive']['future_option']-row['nonpositive']['future_option']
        ans[name]=row
    c=Contract(base,0.,8);z=c.pair(.125,.425,True)['nonpositive'];i=int(np.linalg.norm(base.e[0].states-[1.25,1.59375],axis=1).argmin())
    a=base.e[0].controls(z['policy'])[0,i];a0=a.copy();a0[1]=0
    out={'action':a,'same_financial_zero_action':a0,'one_step_components':parts(base,base.e[0].states[i],a,z['value'][1],.125,.425)-parts(base,base.e[0].states[i],a0,z['value'][1],.125,.425)}
    masses=[]
    for act in (a,a0):
        mass=0.
        for prob,e in zip((.875,.125),base.e):
            y,live,disc,_,_,_,_=old.transition(base.e[0].states[[i]],act[None,:],1/8,e.model)
            mask=(base.e[0].states[:,0]==1.2).astype(float).reshape(e.shape)
            mass+=prob*np.mean(disc*live*old.interpolate(mask,y))
        masses.append(mass)
    out['discounted_next_lower_preference_boundary_mass']=masses
    ans['alternative_state']=out;ans['component_order']=['noncost_flow','adjustment_cost','immediate_discharge','live_liquidation_benchmark','continuation_excess_over_liquidation']
    return ans

def stress(joint):
    rows=[];max_replay=0.;max_direct=0.
    expected={(.8,.8,.5):[.000196740684027,-.000191857347061],(.8,.82,.5):[.000554759103774,.000197830973605],
              (.8,.8,.51):[-.000011968637109,-.000425519084378],(.85,.8,.5):[.000196740684027,-.000209326961178],
              (.85,.82,.5):[.000554759103774,.000178901666151],(.85,.8,.51):[-.000011968637109,-.000442988698495]}
    for F,lam,d in itertools.product((.8,.85),(.125,0.),(.425,)):
        if lam==0:d=.4
        for L,S in ((.8,.5),(.82,.5),(.8,.51)):
            row={'fee':F,'law':lam,'benefit':d,'long':L,'short':S,'regimes':{}}
            for adj in (True,False):
                z=joint.solve(lam,d,F,adj,L,S);f=z['c'].moments(z['p'],lam)[:,1]
                val={s:z['first'][s]['value'] for s in SIGNS}
                row['regimes'][str(adj)]={'delta':val['positive']-val['nonpositive'],
                  'classes':{s:dict(value=val[s],action=z['first'][s]['action'],moments=first_moments(joint.base,f,lam,z['first'][s]['action'])) for s in SIGNS}}
                max_direct=max(max_direct,selected_direct(joint.base,z['c'],z,lam,d))
            if lam==.125:
                for j,adj in enumerate((True,False)):max_replay=max(max_replay,abs(row['regimes'][str(adj)]['delta']-expected[F,L,S][j]))
            rows.append(row)
    assert max(max_replay,max_direct)<2e-11, (max_replay,max_direct)
    return {'cases':rows,'maximum_report_replay_error':max_replay,'maximum_selected_direct_error':max_direct,
            'moment_order':['base_payoff','discounted_duration','discounted_surrender','quadratic_effort']}

def institutions(joint):
    b=joint.base;R=joint.reachability();rows=[];frontiers={};cost_coefficient=.02
    for adj in (True,False):
        z=joint.solve(.125,.425,0.,adj,.8,.5,8);V=z['v'];s=max(SIGNS,key=lambda s:z['first'][s]['value'])
        W=z['first'][s]['value'];f=z['c'].moments(z['p'],.125)[:,1]
        A=float(first_moments(b,f,.125,z['first'][s]['action'])[1]);outside=float(b.terminal[b.center])
        F=np.array([max([0.]+[float((b.terminal-V[n])[R[n]&~b.e[0].boundary].max()) for n in range(m,8)]) for m in range(1,9)])
        frontier=[]
        for m,E in enumerate(F,1):
            robust=E+(1e-5 if m<8 else 0.)
            zz=joint.solve(.125,.425,robust,adj,.8,.5,m)
            error=max(abs(zz['first'][ss]['value']-z['first'][ss]['value']) for ss in SIGNS)
            assert error<2e-11
            frontier.append({'minimum_term':m,'exact_statewise_capacity':E,'strict_test_capacity':robust,'implemented_value_error':error})
        frontiers[str(adj)]=frontier
        for kap in (0.,.005,.01,.02,.04):
            grant=np.maximum(0,outside-W+cost_coefficient*F**2)
            term=kap*np.arange(8)/8;total=grant+term;chosen=int(total.argmin())
            rows.append({'adjustment':adj,'term_cost_rate':kap,'chosen_term':chosen+1,'capacity':F[chosen],
                         'capacity_cost':cost_coefficient*F[chosen]**2,'term_cost':term[chosen],
                         'grant':grant[chosen],'duration':A,'chosen_class':s,'total_procurement_cost':total[chosen],
                         'break_even_service_flow':total[chosen]/A,'all_eight_costs':total})
    return {'capacity_cost_coefficient':cost_coefficient,'term_cost':'kappa * (m-1)/8, paid by the principal',
            'fee_recipient':'external enforcement sector; implementation fees are inactive',
            'selection':'continue on an indifference; strict fee perturbations independently replay implementation',
            'frontiers':frontiers,'choices':rows}

def validate_region(joint,certificate):
    rng=np.random.default_rng(110918);rows=[];B=joint.box
    points=[{k:sum(v)/2 for k,v in B.items()}]+[{k:float(rng.uniform(*v)) for k,v in B.items()} for _ in range(5)]
    for p in points:
        vals=[]
        for adj,m in ((True,1),(False,1),(False,8)):
            vals.append(joint.solve(p['law'],p['benefit'],p['fee'],adj,p['long'],p['short'],m))
        numbers={'adjusted':vals[0]['first']['positive']['value']-vals[0]['first']['nonpositive']['value'],
                 'zero':vals[1]['first']['positive']['value']-vals[1]['first']['nonpositive']['value'],
                 'active_surrender_gain':vals[1]['first']['positive']['value']-vals[2]['first']['positive']['value']}
        for k,v in numbers.items():assert certificate['bounds'][k][0]<=v<=certificate['bounds'][k][1]
        for adj,z in ((True,vals[0]),(False,vals[1])):
            f=z['c'].moments(z['p'],p['law'])[:,1]
            for s in SIGNS:
                mm=first_moments(joint.base,f,p['law'],z['first'][s]['action'])
                assert abs(mm[0]+p['benefit']*mm[1]-p['fee']*mm[2]-z['first'][s]['value'])<2e-11
        rows.append({'parameters':p,'values':numbers})
    return {'direct_interior_points':rows,'interpretation':'Validation of the regional certificate, not its proof.'}

def array_manifest(base,joint):
    out={}
    for i,e in enumerate(base.e):
        for n,k in enumerate([e.common]+e.extra):
            for field in ('base','duration','effort','settlement','exit_discount'):
                a=getattr(k,field);out[f'{i}.{n}.{field}']={'shape':a.shape,'dtype':str(a.dtype),'sha256':hashlib.sha256(a.tobytes()).hexdigest()}
            for field in ('data','indices','indptr'):
                a=getattr(k.matrix,field);out[f'{i}.{n}.csr.{field}']={'shape':a.shape,'dtype':str(a.dtype),'sha256':hashlib.sha256(a.tobytes()).hexdigest()}
    for i,m in enumerate(joint.fm.rows):
        for field in ('data','indices','indptr'):
            a=getattr(m,field);out[f'first.{i}.{field}']={'shape':a.shape,'dtype':str(a.dtype),'sha256':hashlib.sha256(a.tobytes()).hexdigest()}
    for i in (0,1):
        for field,aa in (('reward',joint.fm.reward[i]),('duration',joint.fm.duration[i])):
            out[f'first.{i}.{field}']={'shape':aa.shape,'dtype':str(aa.dtype),'sha256':hashlib.sha256(aa.tobytes()).hexdigest()}
    aa=joint.fm.actions
    out['first.actions']={'shape':aa.shape,'dtype':str(aa.dtype),'sha256':hashlib.sha256(aa.tobytes()).hexdigest()}
    return out

def main():
    t=time.perf_counter();base=Model();joint=Joint(base)
    dump('environment.json',{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform(),
          'kernel_payload_bytes':base.nbytes,'constructor_seconds':base.build_seconds,'source_commit':os.getenv('GITHUB_SHA','local-authored-source')})
    dump('array_manifest.json',array_manifest(base,joint))
    dump('directional.json',directional(base));dump('mechanism.json',mechanism(joint));dump('stress.json',stress(joint))
    # A separate cache gives an unambiguous common endpoint bill for this workload.
    joint.cache={};joint.solve_seconds=0.;joint.solve_count=0
    a=joint.region('chord');endpoint_bill=joint.solve_seconds
    assert a['certified'];dump('chord_certificate.json',a);print('CHORD',a['bounds'],flush=True)
    b=joint.region('count');assert b['certified'];dump('count_certificate.json',b);print('COUNT',b['bounds'],flush=True)
    dominance=joint.dominance();assert dominance['certified'];dump('dominance.json',dominance)
    dump('institutions.json',institutions(joint))
    ts=time.perf_counter();validation=validate_region(joint,a)
    validation['new_validation_seconds']=time.perf_counter()-ts
    arith=arithmetic_audit(Contract(base,BOX['fee'][1],1),BOX['law'][1]-BOX['law'][0],1.)
    assert max(r['negative_minus_zero_upper'] for r in dominance['dates'])<0
    validation['arithmetic']=arith;validation['all_required_checks_passed']=True;dump('validation.json',validation)
    np.savez_compressed(OUT/'certificate_arrays.npz',**joint.artifacts)
    knots={'actions':joint.fm.actions}
    for k in (0,1):
        knots[f'reward.{k}']=joint.fm.reward[k];knots[f'duration.{k}']=joint.fm.duration[k]
        for fld in ('data','indices','indptr'):
            knots[f'csr.{k}.{fld}']=getattr(joint.fm.rows[k],fld)
        knots[f'csr.{k}.shape']=np.array(joint.fm.rows[k].shape)
    np.savez_compressed(OUT/'first_date_operator.npz',**knots)
    dump('work_account.json',{'constructor_seconds':base.build_seconds,'shared_endpoint_seconds':endpoint_bill,
        'shared_endpoint_solves':a['endpoint_solves_in_invocation'],'validation_seconds':validation['new_validation_seconds'],
        'chord_nonendpoint_seconds':a['nonendpoint_seconds'],'count_nonendpoint_seconds':b['nonendpoint_seconds'],
        'chord_matched_total_seconds':base.build_seconds+endpoint_bill+a['nonendpoint_seconds']+validation['new_validation_seconds'],
        'count_matched_total_seconds':base.build_seconds+endpoint_bill+b['nonendpoint_seconds']+validation['new_validation_seconds'],
        'scope':'Same 5D decision and active-surrender test, same bank/corners, common construction/endpoints/validation charged to each. Kernel payload is not process peak memory.',
        'full_script_seconds':time.perf_counter()-t})
    print('ALL R11 SCIENTIFIC CHECKS PASSED',flush=True)
if __name__=='__main__':main()
