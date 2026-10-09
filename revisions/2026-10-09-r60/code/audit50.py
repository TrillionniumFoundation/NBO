"""Reconstruct mathematical records and numerical intervals; never retrain."""
from __future__ import annotations
import json,math,itertools,statistics,hashlib
from collections import Counter,defaultdict
from pathlib import Path
from fractions import Fraction as F
import operators50 as o
import study50 as st
s=o.s;R=Path(__file__).resolve().parents[1]
def dump(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
SEEN={}
def audit_checkpoint(path):
    digest=s.H(path)
    if digest in SEEN:return SEEN[digest]
    j=s.read(path);T=j['T'];b=sum((o.BETA**t*F(row['component']) for t,row in enumerate(j['rows'])),F(0))+o.BETA**T*F(j['terminal_width'])
    assert b==F(j['policy_bound_exact']) and F(float(j['policy_bound_upper']))>=b,path
    # Reconstruct original-owner transforms, actual FVI moduli and all grid radii.
    for raw in j['models']:
        model=s.Model.load(raw);assert model.h==F(raw['state_cover'])
    for row in j['rows']:
        assert F(row['component'])==F(row['optimal_residual_upper'])+F(row['selected_policy_upper'])
    SEEN[digest]=j
    return j

def main():
    st.verify_freeze()
    evidence={'R49-main.zip':'d367b908c754dfa66efd5b6ed40fd6ce46a6e6606cde959811afb850b4b3c601','R49-graded.zip':'280f32e6cc66344e31c5e04487cd813bdaf21908f6860d1449b2c297f4268517','R48-publication.zip':'b82272add8e7ea630ef1ab45455b079514fd848311e2d23db84d2b11ab9cd5df'}
    for n,h in evidence.items():assert s.H(R/'evidence'/n)==h,n
    for name in ('EXECUTION_COMPLETE.json','COMMON_EXECUTION_COMPLETE.json','VERIFIED_EXECUTION_COMPLETE.json'):
        m=s.read(R/'audit'/name)
        for n,h in m['result_sha256'].items():assert s.H(R/n)==h,n
    from common50 import common_verify
    common_verify()
    services=[s.read(p) for p in sorted((R/'results/services').glob('*/record.json'))];assert len(services)==51
    groups=defaultdict(list)
    for j in services:
        path=R/'results/services'/f"{j['spec']['key']}-r{j['repetition']}"/j['checkpoint'];assert s.H(path)==j['checkpoint_sha256'];q=audit_checkpoint(path)
        assert j['attained']==(F(q['policy_bound_exact'])<=j['spec']['epsilon']);groups[j['spec']['key']].append(j)
    for vals in groups.values():assert len(vals)==3 and len({q['checkpoint_sha256'] for q in vals})==1
    common=[s.read(p) for p in sorted((R/'results/commonaccuracy').glob('*/record.json'))];assert len(common)==18
    common_groups=defaultdict(list)
    for j in common:
        common_groups[(j['dimension'],j['method'])].append(j)
        folder=R/'results/commonaccuracy'/j['key']
        for a in j['attempts']:assert s.H(folder/a['checkpoint'])==a['checkpoint_sha256'];audit_checkpoint(folder/a['checkpoint'])
        assert all(F(a['policy_bound_exact'])>5 for a in j['attempts'][:-1]);assert j['attained']==(F(j['attempts'][-1]['policy_bound_exact'])<=5)
    for vals in common_groups.values():assert len(vals)==3 and len({tuple(a['checkpoint_sha256'] for a in q['attempts']) for q in vals})==1
    direct=[s.read(p) for p in sorted((R/'results/direct-verified').glob('*.json')) if not p.name.endswith('.clock.json')];assert len(direct)==28
    corrections=[]
    for j in direct:
        old=s.read(R/'results/direct'/f"{j['spec']['key']}.json");assert old['stream_sha256']==j['stream_sha256'] and old['paths']==j['paths']
        assert all(old['contrasts'][k]['sign']==v['sign'] for k,v in j['contrasts'].items())
        corrections.append(dict(key=j['spec']['key'],identical_stream=True,maximum_endpoint_change=max(abs(F(old['contrasts'][k]['interval_exact'][i])-F(v['interval_exact'][i])) for k,v in j['contrasts'].items() for i in range(2))))
    dump(R/'audit/NUMERICAL_REPLAY_AUDIT.json',[{**v,'maximum_endpoint_change':str(v['maximum_endpoint_change'])} for v in corrections])
    counters={};intervals=0;blocks=defaultdict(list);gates=Counter();strict=Counter();uncertainty=Counter()
    for j in direct:
        blocks[j['spec']['block']].append(j);n=0
        for rec in list(j['absolute_cost'].values())+list(j['contrasts'].values()):
            a,b=map(F,rec['support_exact']);A=s.c.enclosure(a)[0];B=s.c.enclosure(b)[1]
            lo,hi=st.inference.confidence(rec['lower_endpoint_moments'],rec['upper_endpoint_moments'],A,B);lo=max(a,lo);hi=min(b,hi)
            assert [str(lo),str(hi)]==rec['interval_exact'];assert rec['lower_endpoint_moments']['n']==131072
            assert F(rec['interval'][0])<=lo<=hi<=F(rec['interval'][1]);intervals+=1;n+=1
        assert n==10
        for k,c in enumerate(j['actor_and_gate_counts']):
            gates[str(k)]+=c.get('gate_queries',0);strict[str(k)]+=c.get('strict_action_changes',0)
            assert c.get('largest_accepted_advantage_upper',0)<=0
            uncertainty['ambiguous_acquisitions']+=c.get('ambiguous_acquisitions',0);uncertainty['conservative_hull_fallbacks']+=c.get('conservative_hull_fallbacks',0)
        assert j['paths']==131072 and j['log_upper']==13
        for path,h in zip(j['spec']['paths'],j['spec']['hashes']):assert s.H(R/path)==h
    assert intervals==280
    assert sum((F(13)**i/math.factorial(i) for i in range(41)),F(0))>4*512/F(1,100)
    for name,rows in blocks.items():
        counters[name]={key:dict(Counter(j['contrasts'][key]['sign'] for j in rows)) for key in ('left-minus-right','left-repaired-minus-right-repaired','left-minus-left-repaired','right-minus-right-repaired')}
    summary=dict(services=51,distinct_primary_services=17,primary_checkpoint_identity=True,primary_attainment=dict(Counter(('success' if j['attained'] else 'failure') for j in services)),primary_attainment_by_method={m:dict(Counter('success' if j['attained'] else 'failure' for j in services if j['spec']['method']==m)) for m in ('compiled-witness','tensor-fvi','surplus-fvi')},common_services=18,common_attempts=sum(len(j['attempts']) for j in common),common_attainments=sum(j['attained'] for j in common),common_repeated_identity=True,direct_groups=28,direct_estimands=intervals,primary_direct_estimands=250,amendment_direct_estimands=30,paths_per_group=131072,total_paths=28*131072,direct_signs_by_block=counters,gate_queries=dict(gates),accepted_changes=dict(strict),uncertainty=dict(uncertainty),direct_seconds=sum(j['seconds_before_record'] for j in direct),evidence_sha256=evidence,primary_execution_seconds=s.read(R/'audit/EXECUTION_COMPLETE.json')['elapsed_seconds'],common_execution_seconds=s.read(R/'audit/COMMON_EXECUTION_COMPLETE.json')['elapsed_seconds'])
    dump(R/'audit/RESULT_AUDIT.json',summary)
    dump(R/'audit/COMPARISON_LEDGER.json',dict(services=services,common_services=common,direct=direct))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
