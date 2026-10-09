"""Reconstruct every record and derive exact tolerance/price frontiers."""
from __future__ import annotations
import collections,csv,itertools,json,statistics
from service49 import *
import direct49 as d
from diagnostics import sensor_curve

def write(p,j):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n')

def price_envelope(rows,S):
    lines={b:(F(j['interval_exact'][0]),F(j['interval_exact'][1]),2*S*b) for b,j in rows.items()}
    cuts={F(0)}
    for side in (0,1):
        for i,j in itertools.combinations(lines,2):
            x=(lines[j][side]-lines[i][side])/(lines[i][2]-lines[j][2])
            if x>=0:cuts.add(x)
    cuts=sorted(cuts);out=[]
    for left,right in zip(cuts,cuts[1:]+[None]):
        x=left+1 if right is None else (left+right)/2
        li=min(lines,key=lambda b:(lines[b][0]+x*lines[b][2],b));ui=min(lines,key=lambda b:(lines[b][1]+x*lines[b][2],b))
        pair=(li,ui)
        if out and out[-1]['indices']==list(pair):out[-1]['right']=None if right is None else str(right)
        else:out.append({'left':str(left),'right':None if right is None else str(right),'indices':list(pair),'regret_intercept':str(lines[ui][1]-lines[li][0]),'regret_slope':str(lines[ui][2]-lines[li][2])})
    return {'lines':{str(b):list(map(str,l)) for b,l in lines.items()},'open_intervals':out,'boundary_rule':'evaluate all lines exactly and choose the smallest bit index among ties'}

def sensor_analysis(rows):
    spec=next(iter(rows.values()))['spec'];payload=read(HERE.parent/spec['paths'][0]);T=payload['T'];S=sum((BETA**t for t in range(T)),F(0));Ka=F(1,16)
    # FVI uses its actual critic modulus in addition to the primitive graph modulus.
    A=sum((BETA**t*(F(row['L_graph'])+F(model['L'])+2*F(row['D'])*Ka) for t,(row,model) in enumerate(zip(payload['rows'],payload['models']))),F(0))
    K=sum((BETA**t*F(row['D'])/4096 for t,row in enumerate(payload['rows'])),F(0));G=F(payload['policy_bound_exact'])
    decisions=[]
    for price in map(F,spec['bit_prices']):
        costs={b:(F(j['interval_exact'][0])+2*S*b*price,F(j['interval_exact'][1])+2*S*b*price) for b,j in rows.items()}
        upper=min(costs,key=lambda b:(costs[b][1],b));cert=min(rows,key=lambda b:(G+K+A/F(2**b)+2*S*b*price,b))
        midpoint=min(costs,key=lambda b:((costs[b][0]+costs[b][1])/2,b));lower=min(v[0] for v in costs.values())
        decisions.append({'price':str(price),'certified_bits':cert,'net_upper_selected_bits':upper,'midpoint_selected_bits':midpoint,'selected_regret_upper':str(costs[upper][1]-lower),'certified_choice_regret_upper':str(costs[cert][1]-lower),'net_selected_minus_certified_interval':[str(costs[upper][0]-costs[cert][1]),str(costs[upper][1]-costs[cert][0])],'selected_net_interval_relative_to_reference_policy':[str(x) for x in costs[upper]],'certified_augmented_loss':str(G+K+A/F(2**cert)+2*S*cert*price)})
    return {'T':spec['T'],'p':spec['p'],'method':spec['method'],'policy_sha256':spec['hashes'][0],'acquisition_coefficient':str(A),'quantization_allowance':str(K),'decisions':decisions,'all_nonnegative_prices':price_envelope(rows,S)}

def main():
    done=read(HERE/'audit/EXECUTION_COMPLETE.json')
    for name,digest in done['source_hashes'].items():assert H(HERE/name)==digest,name
    for name,digest in done['result_hashes'].items():assert H(HERE/name)==digest,name
    records={};ncheck=0;adaptive=0;nmodels=0
    for path in sorted((HERE/'results/services').glob('*/record.json')):
        j=read(path);key=(j['dimension'],j['horizon'],j['price'],j['method'],j['repeat']);records[key]=j
        cum={};last=-1
        for row in j['attempts']:
            p=path.parent/row['checkpoint'];assert H(p)==row['checkpoint_sha256'];q=read(p);ncheck+=1
            assert row['prefix_seconds']>last;last=row['prefix_seconds']
            value=sum((BETA**t*F(r['component']) for t,r in enumerate(q['rows'])),F(0))+BETA**q['T']*F(q['terminal_width'])
            assert value==F(q['policy_bound_exact'])==F(row['bound_exact']);assert F(row['bound_upper'])>=value
            for k,v in q['counts'].items():cum[k]=max(cum.get(k,0),v) if k=='maximum_coefficient_bits' else cum.get(k,0)+v
            assert cum==row['prefix_counts']
            if j['method']=='compiled-witness':
                a,b,cq=coefficients(j['dimension'],j['horizon'],j['price']);eta=value-a/q['N']-b/q['K']-cq/q['M'];assert 0<=eta<F(1,10**7)
            if j['method']=='curvature-fvi':adaptive+=q['nonuniform_date_models'];nmodels+=len(q['models'])
        for target,first in j['first_crossings'].items():
            a=next((r for r in j['attempts'] if F(r['bound_exact'])<=F(target)),None)
            assert (a is None)==(first is None)
            if a:assert all(first[k]==a[k] for k in first)
    assert len(records)==60 and ncheck==300,(len(records),ncheck)
    for key,j in records.items():
        if key[-1]:assert [a['checkpoint_sha256'] for a in j['attempts']]==[a['checkpoint_sha256'] for a in records[key[:-1]+(0,)]['attempts']]
    frontiers=[]
    for dd,T,p in sorted({k[:3] for k in records}):
        methods=[m for m in METHODS if (dd,T,p,m,0) in records];cuts=sorted({F(0)}|{F(a['bound_exact']) for m in methods for a in records[(dd,T,p,m,0)]['attempts']});out=[]
        for left,right in zip(cuts,cuts[1:]+[None]):
            selected={}
            for m in methods:
                arr=[next((a for a in records[(dd,T,p,m,rep)]['attempts'] if F(a['bound_exact'])<=left),None) for rep in range(3)]
                selected[m]=None if arr[0] is None else {'N':arr[0]['N'],'K':arr[0]['K'],'M':arr[0]['M'],'median_seconds':statistics.median(a['prefix_seconds'] for a in arr),'min_seconds':min(a['prefix_seconds'] for a in arr),'max_seconds':max(a['prefix_seconds'] for a in arr),'innovation_midpoints':arr[0]['prefix_counts']['innovation_midpoints'],'stored_actor_scalars':arr[0]['counts']['stored_actor_scalars']}
            out.append({'left_closed':str(left),'right_open':None if right is None else str(right),'methods':selected})
        frontiers.append({'d':dd,'T':T,'p':p,'intervals':out})
    attainment={m:{str(t):sum(j['first_crossings'][str(t)] is not None for k,j in records.items() if k[0]==2 and k[3]==m) for t in (4,2,1,F(1,2))} for m in METHODS}
    time_counts={}
    for m in METHODS[1:]:
        pairs=[]
        for T,p,rep,target in itertools.product((2,3),(1,4),range(3),('4','2','1','1/2')):
            w=records[(2,T,p,METHODS[0],rep)]['first_crossings'][target];f=records[(2,T,p,m,rep)]['first_crossings'][target]
            if w and f:pairs.append((w['prefix_seconds'],f['prefix_seconds']))
        time_counts[m]={'common':len(pairs),'witness_faster':sum(a<b for a,b in pairs),'witness_slower':sum(a>b for a,b in pairs)}
    dimension=[]
    for dd,T,m in itertools.product((2,3,4),(2,3),METHODS[:2]):
        a=[records[(dd,T,1,m,rep)]['first_crossings']['5'] for rep in range(3)]
        dimension.append({'d':dd,'T':T,'method':m,'attained':sum(x is not None for x in a),'target':'5','N':a[0]['N'] if a[0] else None,'median_seconds':statistics.median(x['prefix_seconds'] for x in a) if all(a) else None})
    direct=[];sens=collections.defaultdict(dict);npaths=0
    cat=read(HERE/'audit/DIRECT_CATALOGUE.json')
    for spec in cat['specs']:
        j=read(HERE/'results/direct'/(spec['key']+'.json'));assert j['spec']==spec
        for n,h in zip(spec['paths'],spec['hashes']):assert H(HERE.parent/n)==h
        if j['identity']:assert j['interval_exact']==['0','0'] and j['paths']==0
        else:
            lo,hi=d.inherited.confidence(j['lower_endpoint_moments'],j['upper_endpoint_moments'],*map(float,map(F,j['support_exact'])))
            assert [str(lo),str(hi)]==j['interval_exact'],j['key'];npaths+=j['paths']
        if spec['kind']=='sensor':sens[(spec['T'],spec['p'],spec['method'])][spec['bits'][0]]=j
        else:direct.append(j)
    decisions=[sensor_analysis(rows) for rows in sens.values()]
    # Historical analysis is deterministic re-expression, not a new study.
    oldfees=[]
    for path in sorted((HERE.parent/'2026-10-08-r48/results/direct').glob('*.json')):
        if path.name.endswith('.clock.json'):continue
        j=read(path);oldfees.append({'key':j['key'],'source_sha256':H(path),'interval_exact':j['interval_exact'],'fees':d.fee_account(*j['interval_exact'])})
    sensitive=[]
    for target in map(F,('0.8','0.85','0.9','0.95','0.99','1','1.003','1.014','1.05','1.1')):
        for ver in ('2026-10-08-r48','2026-10-08-r49'):
            row={'revision':ver[-3:],'target':str(target),'attainment':{}}
            for m in METHODS[:2]:
                jj=[read(p) for p in (HERE.parent/ver/'results/services').glob(f'{m}-d2-*/record.json')]
                row['attainment'][m]=sum(any(F(a['bound_exact'])<=target for a in j['attempts']) for j in jj)
            sensitive.append(row)
    counts=collections.Counter(j['sign'] for j in direct)
    main_direct=[j for j in direct if j['spec']['frontier']=='R49'];oldpair=[j for j in direct if j['spec']['frontier']=='R48']
    summary={'services':len(records),'rungs':ncheck,'main_services':36,'repetition_checkpoint_identity':True,'attainment':attainment,'timing':time_counts,'adaptive_nonuniform_date_models':adaptive,'adaptive_total_date_models':nmodels,'dimension_target':dimension,'direct_records':len(direct),'direct_signs':dict(counts),'new_frontier_signs':dict(collections.Counter(j['sign'] for j in main_direct)),'r48_favorable_signs':dict(collections.Counter(j['sign'] for j in oldpair)),'sensor_records':sum(len(x) for x in sens.values()),'sampled_paths':npaths,'sampled_contrasts':sum(not read(HERE/'results/direct'/(x['key']+'.json'))['identity'] for x in cat['specs']),'missing_economic_tasks':cat['missing'],'sensor_decisions':decisions,'execution_source_commit':done['source_commit'],'seconds_science':done['total_seconds'],'joint_direct_seconds':sum(read(HERE/'results/direct'/(s['key']+'.clock.json'))['seconds_through_record_fsync'] for s in cat['specs']),'historical_clocks_spliced':False}
    write(HERE/'audit/TOLERANCE_FRONTIERS.json',frontiers);write(HERE/'audit/TARGET_SENSITIVITY.json',sensitive);write(HERE/'audit/REPLACEMENT_FEE_FRONTIERS.json',{'R48':oldfees,'R49':[{'key':j['key'],'interval_exact':j['interval_exact'],'fees':j['replacement']} for j in direct]});write(HERE/'audit/SENSOR_DECISIONS.json',decisions);write(HERE/'audit/PUBLICATION_SUMMARY.json',summary)
    write(HERE/'audit/RESULT_AUDIT.json',{'passed':True,'source_hashes':len(done['source_hashes']),'result_hashes':len(done['result_hashes']),'services':60,'rungs':300,'policy_bounds_reconstructed':300,'repetition_policy_identity':True,'direct_records_reconstructed':len(cat['specs']),'sampled_moment_pairs_reconstructed':summary['sampled_contrasts'],'source':done['source_commit']})
    print(json.dumps({k:v for k,v in summary.items() if k not in ('sensor_decisions','dimension_target')},indent=2))
if __name__=='__main__':main()
