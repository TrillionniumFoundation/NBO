"""Reconstruct the additional block without pooling cross-host clocks."""
from __future__ import annotations
import collections,itertools,statistics
from analyze49 import *
import graded49 as g

def main():
    done=read(HERE/'graded/audit/EXECUTION_COMPLETE.json')
    for name,h in {**done['source_hashes'],**done['result_hashes']}.items():assert H(HERE/name)==h,name
    records={};checked=0;nonuniform=0;models=0;cross=[];geometries=[]
    for path in sorted((HERE/'graded/results/services').glob('*/record.json')):
        j=read(path);key=(j['horizon'],j['price'],j['method'],j['repeat']);assert j['dimension']==2;records[key]=j;cum={};last=-1
        for row in j['attempts']:
            p=path.parent/row['checkpoint'];assert H(p)==row['checkpoint_sha256'];q=read(p);checked+=1
            assert row['prefix_seconds']>last;last=row['prefix_seconds']
            value=sum((BETA**t*F(z['component']) for t,z in enumerate(q['rows'])),F(0))+BETA**q['T']*F(q['terminal_width'])
            assert value==F(q['policy_bound_exact'])==F(row['bound_exact']);assert F(row['bound_upper'])>=value
            for k,v in q['counts'].items():cum[k]=max(cum.get(k,0),v) if k=='maximum_coefficient_bits' else cum.get(k,0)+v
            assert cum==row['prefix_counts']
            actual=0
            for model in q['models']:
                axes=[list(map(lambda x:F(float(x)),a)) for a in model['axes']]
                assert all(all(a<b for a,b in zip(ax,ax[1:])) and ax[0]==0 and ax[-1]==1 for ax in axes)
                if q['method']=='graded-fvi':assert all((x*2**24).denominator==1 for ax in axes for x in ax)
                h=sum((max(b-a for a,b in zip(ax,ax[1:]))/2 for ax in axes),F(0));assert h==F(model['state_cover'])
                actual+=any(len(set(b-a for a,b in zip(ax,ax[1:])))>1 for ax in axes)
            assert actual==q['nonuniform_date_models']
            if q['method']=='graded-fvi':
                nonuniform+=actual;models+=len(q['models'])
                if not j['repeat']:geometries.append({'T':j['horizon'],'p':j['price'],'N':q['N'],'nonuniform_date_models':actual,'date_models':len(q['models']),'cover_radii':[m['state_cover'] for m in q['models']]})
            else:
                original=HERE/'results/services'/path.parent.name/row['checkpoint']
                cross.append({'block_B_path':str(p.relative_to(HERE)),'block_A_path':str(original.relative_to(HERE)),'identical_policy_checkpoint':H(original)==H(p),'A_sha256':H(original),'B_sha256':H(p)})
        for target,first in j['first_crossings'].items():
            a=next((r for r in j['attempts'] if F(r['bound_exact'])<=F(target)),None);assert (a is None)==(first is None)
            if a:assert all(first[k]==a[k] for k in first)
    assert len(records)==36 and checked==216
    for key,j in records.items():
        if key[-1]:assert [r['checkpoint_sha256'] for r in j['attempts']]==[r['checkpoint_sha256'] for r in records[key[:-1]+(0,)]['attempts']]
    fronts=[]
    for T,p in itertools.product((2,3),(1,4)):
        cuts=sorted({F(0)}|{F(a['bound_exact']) for m in g.METHODS for a in records[(T,p,m,0)]['attempts']});bands=[]
        for lo,hi in zip(cuts,cuts[1:]+[None]):
            selected={}
            for m in g.METHODS:
                a=[next((a for a in records[(T,p,m,r)]['attempts'] if F(a['bound_exact'])<=lo),None) for r in range(3)]
                selected[m]=None if a[0] is None else {'N':a[0]['N'],'K':a[0]['K'],'M':a[0]['M'],'median_seconds':statistics.median(v['prefix_seconds'] for v in a),'minimum_seconds':min(v['prefix_seconds'] for v in a),'maximum_seconds':max(v['prefix_seconds'] for v in a),'prefix_counts':a[0]['prefix_counts']}
            bands.append({'left_closed':str(lo),'right_open':None if hi is None else str(hi),'methods':selected})
        fronts.append({'T':T,'p':p,'d':2,'intervals':bands})
    attainment={m:{str(q):sum(j['first_crossings'][str(q)] is not None for k,j in records.items() if k[2]==m) for q in (4,2,1,F(1,2))} for m in g.METHODS}
    timing={}
    for m in g.METHODS[1:]:
        pairs=[]
        for T,p,r,target in itertools.product((2,3),(1,4),range(3),('4','2','1','1/2')):
            w=records[(T,p,g.METHODS[0],r)]['first_crossings'][target];f=records[(T,p,m,r)]['first_crossings'][target]
            if w and f:pairs.append((w['prefix_seconds'],f['prefix_seconds']))
        timing[m]={'common':len(pairs),'witness_faster':sum(a<b for a,b in pairs),'witness_slower':sum(a>b for a,b in pairs)}
    summary={'services':36,'rungs':216,'nonuniform_date_models':nonuniform,'graded_date_models':models,'attainment':attainment,'timing':timing,'repetition_checkpoint_identity':True,'cross_block_policy_checkpoints':len(cross),'cross_block_identical_checkpoints':sum(x['identical_policy_checkpoint'] for x in cross),'source_commit':done['source_commit'],'workflow_run':done['workflow_run'],'complete_seconds':done['total_seconds'],'clocks_pooled_across_blocks':False,'source_files_verified':len(done['source_hashes']),'result_files_verified':len(done['result_hashes'])}
    write(HERE/'audit/GRADED_SUMMARY.json',summary);write(HERE/'audit/GRADED_TOLERANCE_FRONTIERS.json',fronts);write(HERE/'audit/GRADED_GEOMETRY.json',geometries);write(HERE/'audit/CROSS_BLOCK_POLICY_IDENTITIES.json',cross)
    original=read(HERE/'audit/PUBLICATION_SUMMARY.json')
    write(HERE/'audit/COMBINED_EVIDENCE_SUMMARY.json',{'services':original['services']+36,'rungs':original['rungs']+216,'block_A':original,'block_B':summary,'timings_remain_separate':True,'no_new_direct_inference_for_graded_policy':True})
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
