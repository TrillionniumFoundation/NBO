"""Artificial unequal-half fixture for the declared 32/16 reporting rule.

Only pure saved-table functions are invoked. No original state, actor, economic
oracle, process timing campaign or source authenticator is called or replaced.
The first-half synthetic contrasts differ from the all-32 means by construction.
"""
import argparse, hashlib, importlib.util, json, sys
from fractions import Fraction as Q
from pathlib import Path

revision=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(revision/'code122'))
import report122 as r

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    source=revision/'verification122/report_protocol_adapter122.py'
    spec=importlib.util.spec_from_file_location('artificial_protocol_adapter122',source)
    adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    keys=[k+(s,) for k in r.catalog() for s in r.SERVICES]
    ranks={k:j%11-5 for j,k in enumerate(keys)}
    data={'independent':{}}
    for k in keys:
        for j in range(32):
            value=Q(ranks[k],65536)*(1 if j<16 else -1)
            data['independent'][(k[0],j,*k[1:])]={
                'final_key_id':str((k,j)),
                'independent_policy_lower':str(value),'independent_policy_upper':str(value)}
    clocks={}
    for s in r.SCENARIOS:
        for j,k in enumerate(keys):
            clocks[s,k]={'n':32 if s=='primary32' else 16,
                'historical_complete_acquisition_seconds':Q(j+1,10),
                'shared_process_residual_seconds':Q(2),
                'cold_load_seconds':Q(1,10),'complete_cohort_seconds':Q(j%5+2)}
    original=r.price_tables(data,clocks)
    checks={};adapter.install_protocol_adapter(r,checks,out)
    corrected=r.price_tables(data,clocks)
    assert tuple(map(len,corrected))==(2784,28800,384,96)
    assertions=0
    for old,new in zip(original[0],corrected[0]):
        assert old['total_allocated_seconds']==new['total_allocated_seconds']
        assert old['seconds_per_decision']==new['seconds_per_decision']
        assert new['economic_state_units']==(32 if new['scenario']=='primary32' else 16)
        assertions+=3
    differences=0
    for old,new in zip(original[1],corrected[1]):
        k,b=r.cell(new['candidate']),r.cell(new['comparator'])
        expected=Q(0) if new['scenario']=='primary32' else Q(ranks[b]-ranks[k],65536)
        assert old['sample_gain_lower']==old['sample_gain_upper']==0
        assert new['sample_gain_lower']==new['sample_gain_upper']==expected
        assert new['extra_seconds_per_decision']==old['extra_seconds_per_decision']
        assert new['statistical_adoption_claim'] is False
        assertions+=4;differences+=old['sample_gain_lower']!=new['sample_gain_lower']
    assert differences>0 and differences==checks['changed_timing_mean_endpoint_rows']
    for old,new in zip(original[:3],corrected[:3]):
        assert [z for z in old if z['scenario']=='primary32']==[z for z in new if z['scenario']=='primary32']
        assertions+=1
    for name,rows in zip(adapter.TABLES,corrected):
        r.save_rows(out,'CORRECTED_ARTIFICIAL_'+name,rows,name=='PRICE_CONSTRAINTS122')
    result=dict(status='executed-artificial-unequal-half-fixture',scientific_experiment=False,
        new_states=0,new_training=0,new_economic_calls=0,new_timing_processes=0,
        source_authenticator_replaced=False,frozen_source_changed=False,
        frozen_reporter_sha256=digest(revision/'code122/report122.py'),
        protocol_adapter_sha256=digest(source),fixture_sha256=digest(__file__),
        exact_assertions=assertions,checks=checks,
        all_original_32_state_pair_means_exact_zero=True,
        timing_means_independently_expected_from_first_16=True,
        all_costs_exactly_unchanged=True,all_primary_tables_exactly_unchanged=True,
        changed_timing_constraint_rows=differences,
        artificial_output_manifest=[{'path':p.name,'bytes':p.stat().st_size,'sha256':digest(p)}
            for p in sorted(out.iterdir()) if p.is_file()])
    (out/'PROTOCOL_FIXTURE_RESULT122.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='artificial_output_manifest'},indent=2))

if __name__=='__main__':main()
