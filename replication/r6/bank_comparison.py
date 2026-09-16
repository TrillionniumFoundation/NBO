#!/usr/bin/env python3
"""Same exact Bellman oracle, scalar OLS coverage, and neural-action attribution.
The scalar statewise OLS construction equals R5's adjacent-chord construction:
exact anchor policies outside an adjacent interval cannot improve its lower
policy envelope. We check that fact, not rename OLS as a new algorithm.
"""
from common import *
import contracts as c

def focal_ols(e,center,epsilon=1e-3):
    start=time.perf_counter();bank=[e.optimal(0.),e.optimal(1.)];history=[]
    while True:
        bank.sort(key=lambda z:z['d']);candidates=[]
        for i in range(len(bank)-1):
            a,b=bank[i]['d'],bank[i+1]['d']
            fa,fb=bank[i]['feature'][:,0,center],bank[i+1]['feature'][:,0,center]
            ia,ib=fa[0]-2*fa[2],fb[0]-2*fb[2];den=fa[1]-fb[1]
            x=float(np.clip((ib-ia)/den if abs(den)>1e-14 else a,a,b))
            for q in (a,b,x):
                u=(b-q)/(b-a)*bank[i]['value'][0,center]+(q-a)/(b-a)*bank[i+1]['value'][0,center]
                lo=max(ia+q*fa[1],ib+q*fb[1]);candidates.append((float(u-lo),q))
        gap,q=max(candidates);history.append(dict(anchors=len(bank),gap=gap,next=q))
        if gap<=epsilon:break
        if len(bank)>=80:raise RuntimeError('OLS did not converge')
        bank.append(e.optimal(q))
    return bank,dict(seconds=time.perf_counter()-start,history=history)

def scalar_ols_certificate(bank):
    """Independent full-policy-envelope checks at all adjacent corner weights.
    Value computation uses every policy, not just the adjacent pair. Exact
    anchor optimality proves that no additional corner is needed in the cell.
    """
    f=np.stack([r['feature'] for r in bank]);inter=f[:,0]-2*f[:,2];slope=f[:,1]
    maximum=0.;difference=0.
    for i in range(len(bank)-1):
        a,b=bank[i]['d'],bank[i+1]['d'];den=slope[i]-slope[i+1]
        x=np.divide(inter[i+1]-inter[i],den,out=np.full_like(den,a),where=abs(den)>1e-14)
        for q in (a,b,np.clip(x,a,b)):
            all_values=inter+q*slope;lo=all_values.max(0)
            pair=np.maximum(all_values[i],all_values[i+1]);difference=max(difference,float(abs(lo-pair).max()))
            u=(b-q)/(b-a)*bank[i]['value']+(q-a)/(b-a)*bank[i+1]['value']
            maximum=max(maximum,float((u-lo).max()))
    assert difference<2e-11
    return dict(uniform_bound=maximum,full_envelope_minus_adjacent_pair_max=difference)

def run():
    e=c.Economy();center=int(np.linalg.norm(e.states-[2,1.25],axis=1).argmin())
    initial,initial_log=focal_ols(e,center)
    initial_all=max(c.interval_certificate(initial,i,i+1)['upper_loss'] for i in range(len(initial)-1))
    t=time.perf_counter();bank,cert,hist=c.adaptive_bank(e);elapsed=time.perf_counter()-t
    original=np.load(ROOT/'replication/r5/output/contract_bank.npz')
    assert len(bank)==len(original['d']) and abs(np.array([r['d'] for r in bank])-original['d']).max()<1e-10
    # This envelope calculation is independent; it establishes scalar OLS
    # equivalence. It is not a reimplementation of the authors' deep-RL code.
    ols,ols_time=timed(lambda:scalar_ols_certificate(bank))
    mesh=[];tm=time.perf_counter();extras=e.extra;e.extra=[]
    for r in bank:
        x=e.optimal(r['d']);x['value']=r['value'] # original neural-inclusive oracle remains the upper target
        mesh.append(x)
    mesh_seconds=time.perf_counter()-tm;e.extra=extras
    mesh_cert=[c.interval_certificate(mesh,i,i+1) for i in range(len(mesh)-1)]
    mesh_bound=max(r['upper_loss'] for r in mesh_cert)
    assert mesh_bound<1e-3
    losses=[]
    for r,m in zip(bank,mesh):
        mv=m['feature'][0]+r['d']*m['feature'][1]-2*m['feature'][2]
        losses.append(dict(d=r['d'],maximum_full_target_loss=float((r['value']-mv).max()),focal_loss=float(r['value'][0,center]-mv[0,center])))
    memory=lambda bs:sum(r['policy'].nbytes+r['feature'].nbytes for r in bs)
    result=dict(source_sha256=sha(__file__),epsilon=1e-3,exact_oracle='same 1565 common actions plus three frozen neural actions at every node',
        kernel_build_seconds=e.build_seconds,
        initial_distribution_ols=dict(anchors=len(initial),preparation_seconds=initial_log['seconds'],memory_bytes=memory(initial),
            focal_bound=initial_log['history'][-1]['gap'],all_state_date_bound=initial_all,history=initial_log['history']),
        statewise_ols=dict(anchors=len(bank),preparation_seconds=elapsed,memory_bytes=memory(bank),
            uniform_bound=max(x['upper_loss'] for x in cert),history=hist,
            independent_full_envelope_check=ols,full_envelope_check_timing=ols_time),
        restricted_neural_free_bank=dict(anchors=len(mesh),policy_construction_seconds=mesh_seconds,memory_bytes=memory(mesh),
            upper_information='same full-target oracle and same 47 locations; no claim of autonomous mesh-only anchor discovery',
            uniform_bound_vs_original_full_target=mesh_bound,anchor_losses=losses,
            original_deposited_neural_decisions=int((original['policies']>=len(e.menu)).sum()),
            policy_index_disagreements=int(sum((r['policy']!=original['policies'][i]).sum() for i,r in enumerate(bank))),
            original_policy_value_max_difference=float(max(abs((e.evaluate(original['policies'][i])[0]+r['d']*e.evaluate(original['policies'][i])[1]-2*e.evaluate(original['policies'][i])[2])-r['value']).max() for i,r in enumerate(bank))),
            neural_selected_decisions=int(sum((r['policy']>=len(e.menu)).sum() for r in bank)),total_decisions=int(sum(r['policy'].size for r in bank))))
    save('bank_comparison.json',result)
    np.savez_compressed(OUT/'statewise_bank.npz',d=np.array([r['d'] for r in bank]),features=np.stack([r['feature'] for r in bank]),policies=np.stack([r['policy'] for r in bank]),values=np.stack([r['value'] for r in bank]))
    np.savez_compressed(OUT/'mesh_bank.npz',d=original['d'],features=np.stack([r['feature'] for r in mesh]),policies=np.stack([r['policy'] for r in mesh]))
    print('BANK COMPARISON',json.dumps(jsonable({k:v for k,v in result.items() if k not in ('statewise_ols','restricted_neural_free_bank')})),flush=True)
    return result
if __name__=='__main__':run()
