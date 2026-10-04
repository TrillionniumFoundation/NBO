"""Evaluate exactly one frozen R15 policy on its new R16 common-path bank.

There is no optimizer, stopping rule or candidate selection in this worker.
Original policy metadata and new assessment metadata have separate identities.
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import re
import sys
import time
import traceback

from replication_pipeline import (PROTOCOL,CANDIDATES,CANDIDATE_SOURCE,CANDIDATE_EVIDENCE,
    bank,read,write,sha,require,safe,validate_protocol)

ROOT=Path(__file__).resolve().parents[3]

def execute(protocol,trial_id,method_id,out):
    start=time.perf_counter();protocol=Path(protocol).resolve();out=Path(out).resolve()
    p=read(protocol);candidates=read(ROOT/CANDIDATES);validate_protocol(p,candidates)
    match=re.fullmatch(r'd(\d+)_s(\d+)',trial_id);require(match is not None,'unknown trial identifier')
    d,seed=map(int,match.groups());rows=[r for r in candidates['files'] if (r['dimension'],r['stream_seed'],r['method_id'])==(d,seed,method_id)]
    require(len(rows)==1,'policy absent from the exact original candidate inventory');candidate=rows[0]
    source=os.environ.get('NBO_R16_REPLICATION_SOURCE_COMMIT','');fingerprint=os.environ.get('NBO_R16_REPLICATION_FINGERPRINT','')
    require(bool(re.fullmatch('[0-9a-f]{40}',source)) and bool(re.fullmatch('[0-9a-f]{64}',fingerprint)),'source-bound official launcher required')
    require(os.environ.get('GITHUB_RUN_ATTEMPT','1')=='1','second confirmation attempt is inadmissible')
    require(sha(ROOT/CANDIDATES)==p['candidate_inventory_sha256'],'candidate inventory changed')
    checkpoint=safe(ROOT,candidate['path']);require(sha(checkpoint)==candidate['sha256'],'selected R15 policy changed')
    out.mkdir(parents=True,exist_ok=True);require(not (out/'RESULT.json').exists(),'refusing to overwrite confirmation')
    noise,key=bank(p,d,seed)
    metadata=dict(method_id=method_id,trial_id=trial_id,dimension=d,stream_seed=seed,
        source_commit=source,numerical_source_commit=source,protocol_sha256=sha(protocol),assessment_fingerprint=fingerprint,
        candidate_source_commit=CANDIDATE_SOURCE,candidate_evidence_commit=CANDIDATE_EVIDENCE,
        candidate_protocol_sha256=candidate['candidate_protocol_sha256'],method_fingerprint=candidate['method_fingerprint'],
        primitives_sha256=p['design']['primitives_sha256'],epsilon=.1,checkpoint_sha256=candidate['sha256'],
        original_selected_policy_path=candidate['path'],original_attained_online=candidate['original_attained_online'],
        original_selected_stage=candidate['original_selected_stage'],is_confirmation=True,noise_key=key,
        fallback=candidate['fallback'],analytic_schedule=candidate['fallback'])
    result=dict(metadata,record_type='R16 prospective independent confirmation of a fixed R15 policy',complete=False,
        training_runs=0,new_optimizer_draws=0,new_stopping_decisions=0,original_stopping_unchanged=True,
        confirmation_independent_of_selection=True,bank_conditioning='Conditional on all R15 observations, fitting and policy selection; newly domain-separated R16 bank.',
        failure=None,final_confirmation=None)
    write(out/'START.json',dict(metadata,stage='before historical policy reload and independent simulation'))
    fatal=None
    try:
        # The unchanged historical runtime is imported inside the timed child.
        sys.path.insert(0,str(ROOT/'revisions/2026-10-04-r15/code'))
        from training_core import load_candidate
        from actor_verifier import verify
        from method_statistics import ConfidenceBudget
        actor,_,state=load_candidate(checkpoint)
        for field,value in [('source_commit',CANDIDATE_SOURCE),('method_id',method_id),('dimension',d),('seed',seed),
                            ('protocol_sha256',candidate['candidate_protocol_sha256']),('method_fingerprint',candidate['method_fingerprint']),
                            ('primitives_sha256',p['design']['primitives_sha256']),('epsilon',.1)]:
            require(state.get(field)==value,'original candidate checkpoint identity mismatch: '+field)
        require(state['params']==p['design']['primitives'],'candidate economy changed')
        require(bool(getattr(actor,'is_analytical_schedule',False))==candidate['fallback'],'historical fallback identity mismatch')
        budget=ConfidenceBudget(p['inference']['family_alpha'],p['inference']['event_count'])
        row=verify(actor,dimension=d,steps=p['confirmation']['steps'],paths=p['confirmation']['paths_per_seed'],
                   noise_seed=noise,event_alpha=budget.event_alpha,primitives=p['design']['primitives'],
                   out=out/'confirmation',record_id='confirmation',metadata=metadata)
        require(row['noise_hash']!=candidate['original_confirmation_noise_hash'],'original R15 innovations reused')
        require(row['initial_state_hash']!=candidate['original_initial_state_hash'],'original R15 initial sample reused')
        row['raw_path']='confirmation/'+row['raw_path'];row['json_path']='confirmation/'+row['json_path']
        result.update(complete=True,confidence=budget.as_dict(),final_confirmation=row,verification_work=row['work'])
        require(sha(checkpoint)==candidate['sha256'],'original weights changed during new confirmation')
    except Exception as exc:
        fatal=exc;result['failure']=dict(error_type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
        write(out/'FAILURE.json',result['failure'])
    finally:
        result['seconds_before_final_result_write']=time.perf_counter()-start
        result['timing_authority']='Independent parent WORK.json covers process launch through durable evidence; these are additional assessment costs only.'
        write(out/'RESULT.json',result)
    if fatal:raise RuntimeError('replication failed; no candidate, seed or bank replacement is permitted') from fatal
    return dict(complete=True,trial_id=trial_id,method_id=method_id,mean=result['final_confirmation']['mean'],
                lower=result['final_confirmation']['lower'],upper=result['final_confirmation']['upper'])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol',type=Path,required=True);parser.add_argument('--trial-id',required=True)
    parser.add_argument('--method-id',required=True);parser.add_argument('--out',type=Path,required=True)
    import json
    print(json.dumps(execute(**vars(parser.parse_args())),indent=2,allow_nan=False))

if __name__=='__main__':main()
