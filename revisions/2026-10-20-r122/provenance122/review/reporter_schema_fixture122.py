"""Artificial zero-economics schema integration only; never scientific evidence."""
import importlib.util,json,sys,types
from pathlib import Path
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
revision=Path(__file__).resolve().parents[2]
code=revision/'code122'
sys.path.insert(0,str(code))
import report122 as r
out=args.output.resolve()
out.mkdir(exist_ok=False)
def write(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+'\n')
def rows(p,items):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(x)+'\n' for x in items))
F='1'*40;D='2'*40
a=types.SimpleNamespace(primary=out/'primary',independent=out/'independent',stats=out/'stats',source_commit=F)
binding={'source_commit':F,'state_commit':D,'actor_commit':r.ACTOR_COMMIT,'state_directory':str(out/'states')}
aq={tuple(x[k] for k in ('index','budget','arm','loss')):x for x in map(json.loads,(r.R121/'results121/report-attempt01/tables121/fit_and_acquisition121.jsonl').read_text().splitlines())}
def actor_sha(k):return None if k[2]=='online' else aq[k]['model_sha256']
for p,seconds in [(out/'states',1),(a.primary,4100),(a.independent,1),(a.stats,1)]+[(a.primary/'timing'/f'attempt{i:02d}',1000) for i in range(3)]:
 write(p/'EXECUTION122.json',{'status':'executed','exit_code':0,'seconds':seconds})
 write(p/'VERIFIED_SOURCE122.json',{'source_commit':F})
 if 'timing' not in str(p):write(p/'OUTER_EXECUTION122.json',{'status':'executed','exit_code':0,'outer_seconds':seconds+1,'child_output':str(p)})
write(a.primary/'START122.json',{'argv':['campaign122.py','--states',str(out/'states')]})
write(a.primary/'STATES_USED122.json',binding)
write(out/'states/STATE_MANIFEST122.json',{'ARTIFICIAL_SCHEMA_ONLY':True})
write(out/'states/states122.json',{'ARTIFICIAL_SCHEMA_ONLY':True})
(out/'states/entropy122.bin').write_bytes(b'ARTIFICIAL NO DRAW')
write(a.primary/'TIMINGS122.json',{'primary_catalogue_seconds_excluding_children':1000,'processes':[{'repeat':i,'exit_code':0,'outer_seconds':1001} for i in range(3)]})
primary=[]
for scenario in r.SCENARIOS:
 p=a.primary if scenario=='primary32' else a.primary/'timing'/('attempt'+scenario[-2:]);n=32 if scenario=='primary32' else 16
 records=[];cohorts=[]
 for i,b,arm,loss in r.catalog():
  for service in r.SERVICES:
   cohorts.append(dict(index=i,budget=b,arm=arm,loss=loss,service=service,n=n,cold_load_seconds=0.1,service_sum_seconds=0.7,record_serialization_seconds=0.1,complete_cohort_seconds=1.0,actor_sha256=actor_sha((i,b,arm,loss))))
   for j in range(n):
    records.append(dict(index=i,row=j,budget=b,arm=arm,loss=loss,service=service,source_commit=F,state_commit=D,actor_commit=r.ACTOR_COMMIT,
     action=0.0,baseline_action=0.0,action_hex=0.0.hex(),baseline_action_hex=0.0.hex(),state_hex=[0.0.hex(),0.0.hex()],
     baseline_lower=0.0,baseline_upper=0.0,complete_policy_lower=0.0,complete_policy_upper=0.0,
     certified_policy_gain_lower='0',qualified=True,extra_candidate_economic_queries=0,refinement_count=0,paid_refinement_attempt_count=0,paid_refinement_levels_started=[],
     accepted_improvement=False,candidate_rejected=False,improvement_stop='synthetic-identity',certified_regret_upper=0.0,action_distance_upper=0.0,
     first_rejected=False,refused_candidate_bound_attempts=0,candidate_algebra_attempts=0,candidate_bound_attempts=0,counts={}))
 rows(p/'records122.jsonl',records);rows(p/'cohorts122.jsonl',cohorts)
 if n==32:primary=records
ind=[]
for q in primary:
 z={k:q[k] for k in ('index','row','budget','arm','loss','service','source_commit','state_commit','actor_commit','state_hex')}
 for prefix in ('independent_policy','independent_q','independent_optimum','independent_gain','independent_regret'):z.update({prefix+'_lower':'0',prefix+'_upper':'0'})
 z.update(theorem_gain_lower='0',independent_gain_claim_confirmed=True,independent_candidate_interval_contained=True,independent_compatibility=True,squared_original_action_error_upper='0',original_action_hex=0.0.hex(),final_key_id=f'{q["index"]}-{q["row"]}',baseline_key_id=f'{q["index"]}-{q["row"]}')
 ind.append(z)
rows(a.independent/'COMPARISONS122.jsonl',ind)
write(a.independent/'INPUTS122.json',{'primary_sha256':r.digest(a.primary/'records122.jsonl'),'primary_state_binding':binding})
write(a.stats/'INPUTS122.json',{'primary_sha256':r.digest(a.primary/'records122.jsonl'),'independent_sha256':r.digest(a.independent/'COMPARISONS122.jsonl'),'primary_states':32})
safe=[];signed=[]
for i,b,arm,loss in r.catalog():
 for service in r.SERVICES:
  basic=dict(index=i,budget=b,arm=arm,loss=loss,service=service,n=32,sample_gain_lower='0',sample_gain_upper='0',population_gain_lower='0',population_gain_upper='0',joint_failure_at_most='1/20')
  for comparator in ('online-control','quadratic-value-control'):signed.append(dict(**basic,comparator=comparator,simultaneous_family_size=348,delta='3/100',support=['-1/256','1/256']))
  if service!='control':safe.append(dict(**basic,simultaneous_family_size=116,delta='1/100',support=['0','1/256']))
rows(a.stats/'STATS122.jsonl',safe);rows(a.stats/'SIGNED_COMPARISONS122.jsonl',signed)
table=r.R121/'results121/report-attempt01/tables121/fit_and_acquisition121.jsonl'
write(out/'SOURCE_FREEZE122.json',{'scientific_files':{str(table.relative_to(r.REPO)):r.digest(table)},'ARTIFICIAL_SCHEMA_ONLY':True})
# The F/D source authenticator is deliberately replaced in this synthetic-only
# fixture. Its real Git checks are separately executed by the production program.
r.ROOT=out;r.validated_primary=lambda p,s:(primary,binding)
inputs=r.Inputs();data=r.validate_and_load(a,inputs)
groups,contrasts,states,counters=r.economics(data);clocks,clockmap=r.all_clocks(data)
volumes,price,menus,allthree=r.price_tables(data,clockmap)
assert [len(x) for x in (groups,contrasts,states,counters,clocks,volumes,price,menus,allthree)]==[174,116,5568,174,696,2784,28800,384,96]
assert all(x['accepted_action_independent_gain_confirmations']==0 for x in groups)
assert sum(x['independent_raw_gain_confirmations'] for x in groups)==5568
assert all(x['sufficient_price_domain']['empty'] for x in menus)
art=out/'tables';art.mkdir();r.save_rows(art,'SYNTHETIC_CELLS',groups)
write(out/'SYNTHETIC_SCHEMA_RESULT.json',{'status':'executed-schema-only','scientific_experiment':False,'new_states':0,'new_economic_calls':0,'source_authenticator_replaced_only_inside_fixture':True,'counts':dict(policy=174,safe=116,signed=348,state=5568,clocks=696,volumes=2784,price=28800,menus=384,intersections=96),'accepted_improvement_validation_denominator':0,'all_unchanged_confirmations_kept_separate':5568})
print(json.dumps(json.loads((out/'SYNTHETIC_SCHEMA_RESULT.json').read_text()),indent=2))
