"""Disclosed reporting-only corrections to the unchanged F-frozen reporter.

The schema adapter verifies/removes duplicate already-equal raw-mean keywords.
This separate adapter implements REPORTING_SPEC122's existing state-matching
rule: primary costs use the 32-state economics, while timing costs use the
matching first 16 states. The frozen code incorrectly used all 32 economics
for every clock. Its entire original price-table output is retained unchanged
as diagnostic evidence. No policy, state, statistical interval, clock, cost
formula, comparator, volume, qualification or scientific source is changed.
"""
from __future__ import annotations
import hashlib, importlib.util, json, subprocess, sys, time
from fractions import Fraction as Q
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
FROZEN_REPORTER_SHA256='b504bab12124c1a7dab04e5307b30297ab957aa918178c89f9c211556e8b11e2'
SCHEMA_ADAPTER_SHA256='7b0a1f2d520990509b63db504162ec009869f580825675ec83649029e696462a'
TABLES=('COST_VOLUMES122','PRICE_CONSTRAINTS122','PRICE_MENUS122','ALL_THREE_CLOCK_INTERSECTIONS122')

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def install_protocol_adapter(frozen,checks,output):
    original=frozen.price_tables
    def matched_price_tables(data,clocks):
        old=original(data,clocks)
        checks['unchanged_frozen_price_tables_calls']=checks.get('unchanged_frozen_price_tables_calls',0)+1
        for name,rows in zip(TABLES,old):
            frozen.save_rows(output,'FROZEN_CODE_DIAGNOSTIC_'+name,rows,name=='PRICE_CONSTRAINTS122')
        volumes,constraints,menus,intersections=old
        newvolumes=[r if r['scenario']=='primary32' else dict(r,economic_state_units=16) for r in volumes]
        means={}
        corrected=[]
        grouped={}
        for row in constraints:
            s=row['scenario'];k=frozen.cell(row['candidate']);b=frozen.cell(row['comparator'])
            if s=='primary32':
                fixed=row
            else:
                pair=k,b
                if pair not in means:
                    frozen.require(k[0]==b[0],'Cross-objective timing comparison forbidden')
                    lowers=[];uppers=[]
                    for j in range(16):
                        x=data['independent'][(k[0],j,*k[1:])]
                        y=data['independent'][(b[0],j,*b[1:])]
                        if x['final_key_id']==y['final_key_id']:lo=hi=Q(0)
                        else:
                            lo=max(-frozen.TAU,Q(y['independent_policy_lower'])-Q(x['independent_policy_upper']))
                            hi=min(frozen.TAU,Q(y['independent_policy_upper'])-Q(x['independent_policy_lower']))
                            frozen.require(lo<=hi,'Matched timing policy bounds conflict with qualification')
                        lowers.append(lo);uppers.append(hi)
                    means[pair]=(sum(lowers,Q(0))/16,sum(uppers,Q(0))/16)
                lo,hi=means[pair];extra=row['extra_seconds_per_decision']
                fixed=dict(row,sample_gain_lower=lo,sample_gain_upper=hi,sample_gain_sign=frozen.sign(lo,hi),
                    sufficient_price_domain=frozen.price_domain(lo,extra),
                    upper_not_ruled_out_domain=frozen.price_domain(hi,extra),
                    policy_means_conditional_on_32_saved_states=False,
                    policy_means_conditional_on_first_16_saved_states=True)
            corrected.append(fixed)
            key=s,row['volume'],k
            lower,upper=grouped.get(key,(frozen.all_domain(),frozen.all_domain()))
            grouped[key]=(frozen.intersection(lower,fixed['sufficient_price_domain']),
                          frozen.intersection(upper,fixed['upper_not_ruled_out_domain']))
        newmenus=[]
        for row in menus:
            key=row['scenario'],row['volume'],frozen.cell(row)
            lower,upper=grouped[key]
            if row['scenario']=='primary32':
                frozen.require((lower,upper)==(row['sufficient_price_domain'],row['upper_not_ruled_out_domain']),
                    'Protocol reporting correction changed a primary32 menu')
                newmenus.append(row)
            else:newmenus.append(dict(row,sufficient_price_domain=lower,upper_not_ruled_out_domain=upper))
        newintersections=[]
        for row in intersections:
            k=frozen.cell(row);lower=upper=frozen.all_domain()
            for s in frozen.SCENARIOS[1:]:
                lo,hi=grouped[s,row['volume'],k]
                lower=frozen.intersection(lower,lo);upper=frozen.intersection(upper,hi)
            newintersections.append(dict(row,sufficient_price_domain=lower,upper_not_ruled_out_domain=upper))
        new=(newvolumes,corrected,newmenus,newintersections)
        for oldrows,newrows in zip(old[:3],new[:3]):
            frozen.require([r for r in oldrows if r['scenario']=='primary32']==
                           [r for r in newrows if r['scenario']=='primary32'],
                           'Reporting correction changed primary32 table content')
        frozen.require(len(means)==1800,'Full conventional timing comparison census differs')
        checks.update(original_diagnostic_rows=[len(r) for r in old],
            matched_timing_policy_pairs=len(means),matched_state_units=16,
            matched_timing_constraint_rows=sum(r['scenario']!='primary32' for r in corrected),
            unchanged_primary_table_rows=[sum(r['scenario']=='primary32' for r in rows) for rows in old[:3]],
            changed_timing_mean_endpoint_rows=sum((a['sample_gain_lower'],a['sample_gain_upper'])!=
                (b['sample_gain_lower'],b['sample_gain_upper']) for a,b in zip(constraints,corrected)),
            all_three_clock_intersections=len(newintersections))
        return new
    frozen.price_tables=matched_price_tables

def main():
    argv=list(sys.argv)
    if '--repair-commit' not in sys.argv:raise ValueError('Published reporting --repair-commit required')
    position=sys.argv.index('--repair-commit');commit=sys.argv[position+1]
    if len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('Full immutable reporting correction commit required')
    own=Path(__file__).resolve();schema=own.with_name('report_schema_adapter122.py')
    for p in (own,schema,ROOT/'provenance122/REPORTING_AMENDMENT122.md'):
        relative=str(p.relative_to(REPO))
        if subprocess.check_output(['git','show',commit+':'+relative],cwd=REPO)!=p.read_bytes():
            raise ValueError('Reporting source differs from immutable correction commit: '+relative)
    if digest(ROOT/'code122/report122.py')!=FROZEN_REPORTER_SHA256 or digest(schema)!=SCHEMA_ADAPTER_SHA256:
        raise ValueError('Frozen reporter or separately tested schema adapter bytes changed')
    del sys.argv[position:position+2]
    if '--output' not in sys.argv or '--source-commit' not in sys.argv:
        raise ValueError('Original frozen reporter output and F arguments required')
    output=Path(sys.argv[sys.argv.index('--output')+1]).resolve()
    source=sys.argv[sys.argv.index('--source-commit')+1]
    sys.path.insert(0,str(ROOT/'code122'))
    import report122 as frozen
    spec=importlib.util.spec_from_file_location('r122_published_schema_adapter',schema)
    adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    schema_checks={};protocol_checks={}
    adapter.install_adapter(frozen,schema_checks)
    install_protocol_adapter(frozen,protocol_checks,output)
    started=time.perf_counter();status='failed'
    try:
        frozen.main()
        if schema_checks!={'exact_redundant_value_equalities':232,'safe_cells_checked':116,'frozen_economics_calls':1}:
            raise ArithmeticError('Complete schema equality census differs')
        expected={'unchanged_frozen_price_tables_calls':1,'original_diagnostic_rows':[2784,28800,384,96],
            'matched_timing_policy_pairs':1800,'matched_state_units':16,'matched_timing_constraint_rows':21600,
            'unchanged_primary_table_rows':[696,7200,96],'all_three_clock_intersections':96}
        if any(protocol_checks.get(k)!=v for k,v in expected.items()):
            raise ArithmeticError('Complete protocol correction census differs')
        status='executed'
    finally:
        if output.is_dir():
            elapsed=time.perf_counter()-started
            schema_receipt=dict(status=status,source_commit_F=source,reporting_adapter_commit=commit,
                adapter_path=str(schema.relative_to(REPO)),adapter_sha256=digest(schema),
                frozen_reporter_sha256=FROZEN_REPORTER_SHA256,actual_command=argv,checks=schema_checks,
                elapsed_seconds=elapsed,elapsed_clock_shared_with_protocol_adapter_not_additive=True,
                removed_input_keys_only=list(adapter.FIELDS),original_frozen_files_changed=False,
                saved_input_files_changed=False,new_states=0,new_training=0,new_economic_evaluations=0,
                statistical_or_cost_rules_changed=False,original_frozen_attempt_success_asserted=False,
                nested_in_disclosed_protocol_adapter=True,
                scope='Schema component only: duplicate already-equal raw means removed from shallow copies; separate REPORTING_PROTOCOL_ADAPTER122.json discloses timed-cohort aggregation correction.')
            with (output/'REPORTING_ADAPTER122.json').open('x') as f:
                json.dump(schema_receipt,f,indent=2,sort_keys=True);f.write('\n')
            receipt=dict(status=status,source_commit_F=source,reporting_adapter_commit=commit,
                adapter_path=str(own.relative_to(REPO)),adapter_sha256=digest(own),
                schema_adapter_path=str(schema.relative_to(REPO)),schema_adapter_sha256=digest(schema),
                frozen_reporter_sha256=FROZEN_REPORTER_SHA256,
                reporting_amendment_sha256=digest(ROOT/'provenance122/REPORTING_AMENDMENT122.md'),
                actual_command=argv,elapsed_seconds=elapsed,
                schema_checks=schema_checks,protocol_checks=protocol_checks,
                diagnostic_prefix='FROZEN_CODE_DIAGNOSTIC_',
                frozen_original_all_32_menus_preserved=True,primary32_tables_changed=False,
                original_frozen_files_changed=False,saved_input_files_changed=False,
                new_states=0,new_training=0,new_economic_evaluations=0,
                statistical_rules_changed=False,cost_rules_changed=False,
                reporting_aggregation_changed_to_match_frozen_protocol=True,
                original_frozen_attempt_success_asserted=False,
                scope='Two disclosed reporting-only corrections: exact-equality duplicate keyword removal; timed menu economics from the fixed first16 saved states as required by REPORTING_SPEC122. Original all32-for-all-clocks tables remain diagnostic outputs.')
            with (output/'REPORTING_PROTOCOL_ADAPTER122.json').open('x') as f:
                json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n')

if __name__=='__main__':main()
