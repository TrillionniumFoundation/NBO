"""Reconstruct frozen R48 evidence and deterministic publication tables."""
from __future__ import annotations
import collections, itertools, statistics
from common import *
from tensor import Model
from direct48 import confidence,FEE,PATHS,support

def report(path,obj):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')

def main():
    complete=read(R/'audit/EXECUTION_COMPLETE.json')
    for name,digest in complete['source_hashes'].items():assert H(R/name)==digest,name
    for name,digest in complete['result_hashes'].items():assert H(R/name)==digest,name
    services=[];checkpoints=0;groups=collections.defaultdict(list);reconstructed=0
    for path in sorted((R/'results/services').glob('*/record.json')):
        rec=read(path);d=rec['dimension'];T=rec['horizon'];p=rec['price'];C,G,Fx,Fa,Ca,Ka=moduli(d,p)
        first={k:None for k in ('4','2','1','1/2','1/4')};cum={};digests=[]
        for at in rec['attempts']:
            cp=path.parent/f"checkpoint-N{at['N']}.json";assert H(cp)==at['checkpoint_sha256'];payload=read(cp)
            assert payload['N']==at['N'] and payload['method']==rec['method'] and payload['dimension']==d
            models=[Model.load(m) for m in payload['models']];components=[]
            assert len(models)==T+1 and len(payload['actors'])==T
            for t,row in enumerate(payload['rows']):
                future=models[t+1];m=models[t];A=C+BETA*Fx*future.L;D=Ca+BETA*Fa*future.L;L=A+D*Ka
                e=F(row['query_error']);h=m.h;k=F(1,8*at['N'])+(F(1,2**50) if d==3 else 0)
                assert (A,D,L,h,k)==tuple(F(row[v]) for v in ('A','D','L_graph','state_cover','action_cover'))
                assert e>=BETA*future.L*F(d,64*at['N'])
                u=D*k+e+(2 if m.kind=='witness' else 1)*L*h
                selected=e+(0 if m.kind=='witness' else F(row['nearest_excess']))
                assert u==F(row['optimal_residual_upper']) and selected==F(row['selected_policy_upper']) and u+selected==F(row['component'])
                assert len(payload['actors'][t])==m.S;components.append(BETA**t*(u+selected));reconstructed+=1
            terminal=2*F(payload['terminal_error'])+2*G*models[-1].h
            bound=sum(components,F(0))+BETA**T*terminal
            assert terminal==F(payload['terminal_width']) and bound==F(payload['policy_bound_exact'])==F(at['bound_exact'])
            assert c.upper(bound)==at['bound_upper']
            for k,v in at['counts'].items():cum[k]=max(cum.get(k,0),v) if k=='maximum_coefficient_bits' else cum.get(k,0)+v
            assert cum==at['prefix_counts']
            for k in first:
                if first[k] is None and bound<=F(k):first[k]={j:at[j] for j in ('N','bound_exact','prefix_seconds','prefix_cpu_seconds')}
            checkpoints+=1;digests.append(at['checkpoint_sha256'])
        assert first==rec['first_crossings'];clock=read(path.parent/'clock.json');assert clock['record_sha256']==H(path)
        rec['seconds_through_record_fsync']=clock['seconds_through_record_fsync'];rec['checkpoint_sequence']=digests
        services.append(rec);groups[(d,T,p,rec['method'])].append(rec)
    assert len(services)==44 and checkpoints==204
    cells=[];attainment={m:{target:0 for target in ('4','2','1','1/2','1/4')} for m in ('compiled-witness','tensor-fvi','adaptive-fvi')}
    for (d,T,p,m),rr in sorted(groups.items()):
        if d==2:
            assert len(rr)==3 and all(x['checkpoint_sequence']==rr[0]['checkpoint_sequence'] for x in rr)
            for rec in rr:
                for target,crossing in rec['first_crossings'].items():attainment[m][target]+=crossing is not None
        else:assert len(rr)==1
        times=[x['seconds_through_record_fsync'] for x in rr]
        final=rr[0]['attempts'][-1]
        cells.append({'dimension':d,'T':T,'p':p,'method':m,'N':final['N'],'bound':final['bound_upper'],'median_seconds':statistics.median(times),'min_seconds':min(times),'max_seconds':max(times),'repetitions':len(rr),'prefix_counts':final['prefix_counts'],'peak_rss_kib':max(x['peak_rss_kib'] for x in rr)})
    contrasts=[]
    for path in sorted((R/'results/direct').glob('*.json')):
        if path.name.endswith('.clock.json'):continue
        rec=read(path);assert rec['paths']==PATHS and not rec['development_only'];a,b=map(F,rec['support_exact']);assert (a,b)==support(rec['T'],rec['price'])
        A=c.enclosure(a)[0];B=c.enclosure(b)[1];lo,hi=confidence(rec['lower_endpoint_moments'],rec['upper_endpoint_moments'],A,B)
        assert list(map(str,(lo,hi)))==rec['interval_exact'];assert rec['neither_direction_recoups_fee']==(-FEE<lo and hi<FEE)
        for q in rec['policy_files']:assert H(P47/q['path'])==q['sha256']
        clock=read(path.with_suffix('.clock.json'));assert clock['record_sha256']==H(path)
        rec['total_pair_seconds']=clock['seconds_through_record_fsync'];contrasts.append(rec)
    assert len(contrasts)==48
    frontiers=[]
    for d,T,p in sorted({(x['dimension'],x['horizon'],x['price']) for x in services}):
        selected={m:rr for (dd,tt,pp,m),rr in groups.items() if (d,T,p)==(dd,tt,pp)}
        cuts=sorted({F(0)}|{F(a['bound_exact']) for rr in selected.values() for a in rr[0]['attempts']});rows=[]
        for left,right in zip(cuts,cuts[1:]+[None]):
            choices={}
            for m,rr in selected.items():
                aa=[next((a for a in r['attempts'] if F(a['bound_exact'])<=left),None) for r in rr]
                choices[m]=None if aa[0] is None else {'N':aa[0]['N'],'median_prefix_seconds':statistics.median(a['prefix_seconds'] for a in aa),'min_prefix_seconds':min(a['prefix_seconds'] for a in aa),'max_prefix_seconds':max(a['prefix_seconds'] for a in aa),'median_prefix_cpu_seconds':statistics.median(a['prefix_cpu_seconds'] for a in aa),'prefix_counts':aa[0]['prefix_counts'],'checkpoint_bytes':aa[0]['checkpoint_bytes']}
            rows.append({'epsilon_left_closed':str(left),'epsilon_right_open':None if right is None else str(right),'methods':choices})
        frontiers.append({'dimension':d,'T':T,'p':p,'intervals':rows})
    compiler=read(R/'results/diagnostics/compiler.json');sensors=read(R/'results/diagnostics/sensors.json')
    speed=[(r['dense_load_seconds']+r['dense_query_seconds'])/(r['compile_seconds']+r['compiled_query_seconds']) for c0 in compiler for r in c0['repetitions']]
    direct_summary={'groups':48,'total_paths':sum(x['paths'] for x in contrasts),'signs':dict(collections.Counter(x['sign'] for x in contrasts)),'fee_not_recouped_both_directions':sum(x['neither_direction_recoups_fee'] for x in contrasts),'max_absolute_endpoint':max(abs(v) for x in contrasts for v in x['interval']),'max_width':max(x['interval'][1]-x['interval'][0] for x in contrasts),'total_joint_pair_seconds':sum(x['total_pair_seconds'] for x in contrasts),'actor_queries':sum(sum(x['actor_queries']) for x in contrasts),'ambiguous_actor_queries':sum(sum(x['ambiguous_actors']) for x in contrasts)}
    summary={'revision':'R48','services':len(services),'rungs':checkpoints,'reconstructed_date_components':reconstructed,'core_attainment_out_of_12':attainment,'cells':cells,'direct':direct_summary,'compiler':{'frozen_checkpoints':len(compiler),'repetitions':len(speed),'median_dense_over_compiled_including_setup':statistics.median(speed),'min_ratio':min(speed),'max_ratio':max(speed),'attribution':'exact compiler of same envelope, not neural-exclusive speedup'},'sensor_choices':dict(collections.Counter(str(q['selected_bits']) for x in sensors for q in x['curves'])),'historical_results_modified':False,'scientific_source_commit':complete['source_commit'],'workflow_run':complete['workflow_run']}
    report(R/'audit/PUBLICATION_SUMMARY.json',summary);report(R/'audit/COMPLETE_WORK_FRONTIERS.json',frontiers)
    report(R/'audit/DIRECT_INTERVALS.json',[{k:x[k] for k in ('key','T','price','initial_law','sensor_bits','interval','sign','neither_direction_recoups_fee','mean_path_enclosure_width','total_pair_seconds')} for x in contrasts])
    report(R/'audit/RESULT_AUDIT.json',{'passed':True,'frozen_files_verified':len(complete['result_hashes']),'services':len(services),'rungs':checkpoints,'direct_groups':len(contrasts),'date_components':reconstructed,'source_commit':complete['source_commit'],'scope':'record hashes, exact policy-bound formulas, compiled witness maps, complete first crossings, confidence and fee decisions; no retiming or new sampling'})
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
