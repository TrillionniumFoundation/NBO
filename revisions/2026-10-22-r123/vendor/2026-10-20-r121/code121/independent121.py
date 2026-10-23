"""Complete independent rational evaluation of all new R121 policy/proposal keys.

This program does not fit or change actors. Every declared record is retained.
The returned intervals concern the original nested objective and the stated
implemented future-controller allowance, never a substituted quadrature model.
"""
from __future__ import annotations
import argparse,gzip,json,resource,time,traceback
from pathlib import Path
from fractions import Fraction as F
from custody121 import verify_source
from io121 import append_jsonl,digest,exclusive_attempt,write_json
import exact121 as ex

ARMS=('quadratic','relu','hinge','spline','poly2','poly3','grid')
BUDGETS=(5,9)
LOSSES=('value','marginal')
N=64


def identities():
    return {(i,j,b,a,l) for i in range(2) for j in range(N)
            for b in BUDGETS for a in ARMS for l in LOSSES}|{
            (i,j,0,'online','online') for i in range(2) for j in range(N)}


def identity(r):
    return (r['index'],r['row'],r['budget'],r['arm'],r['loss'])


def read_rows(path):
    op=gzip.open if str(path).endswith('.gz') else open
    with op(path,'rt',encoding='utf-8') as f:return [json.loads(s) for s in f if s.strip()]


def catalogue(rows):
    seen=set();actions={};states={};references={}
    for r in rows:
        ident=identity(r);ex.require(ident not in seen,'Unique primary identity');seen.add(ident)
        x=tuple(map(F,r['state']));alpha=F(r['alpha']);a=F(r['action'])
        ex.require(len(x)==2 and all(0<=v<1 and (v*2**40).denominator==1 for v in x),'Exact sampled state')
        ex.require(alpha==(F(1,2) if r['index']==0 else F(3,4)),'Original declared AVaR')
        ex.require(r['state_hex']==[float(v).hex() for v in x],'State serialization')
        ex.require(r['action_hex']==float(a).hex(),'Final action serialization')
        ex.require(r['population_observation'] is True and r['repeat'] is None,'Primary population rows only')
        ex.require(r['original_initial_state_batch_size']==1,'Fixed statewise service')
        ex.require(r['qualified'] is True,'Completed original qualification')
        if r['row'] in states:ex.require(states[r['row']]==x,'Same state across frozen methods')
        states[r['row']]=x
        cap=F(1,8)+sum(x)/16
        proposal=r['first_proposal_action']
        if proposal is None:
            ex.require(r.get('proposal_numerical_failure') is True,'Unavailable raw proposal has its saved numerical failure')
            references[(ident,'proposal')]=None
        roles=[('final',a)]+([] if proposal is None else [('proposal',F(proposal))])
        for role,action in roles:
            ex.require(0<=action<=cap,'Original feasible '+role)
            k=ex.key(x,action,alpha);actions[k]={'x':x,'a':action,'alpha':alpha}
            references[(ident,role)]=k
    ex.require(seen==identities() and len(rows)==len(seen),'All 3712 declared primary decisions')
    return actions,references


def compare(rows,references,policies,out):
    # Shared validation bounds are never input to experimental decisions.
    optima={}
    for p in policies.values():
        sk=(tuple(p['state_hex']),float(p['alpha']).hex())
        lo,hi=p['optimum_lower'],p['q_upper']
        if sk in optima:lo,hi=max(lo,optima[sk][0]),min(hi,optima[sk][1])
        ex.require(lo<=hi,'Nonempty independent original optimum interval')
        optima[sk]=(lo,hi)
    for sk,(lo,hi) in sorted(optima.items()):
        append_jsonl(out/'original_optima121.jsonl',ex.encoded({'state_hex':sk[0],'alpha_hex':sk[1],'lower':lo,'upper':hi}))
    records={identity(r):r for r in rows}
    for r in rows:
        ident=identity(r);final=policies[references[(ident,'final')]]
        proposal=None if references[(ident,'proposal')] is None else policies[references[(ident,'proposal')]]
        lo,hi=optima[(tuple(r['state_hex']),float(r['alpha']).hex())]
        pl,pu=F(r['complete_policy_lower']),F(r['complete_policy_upper'])
        ex.require(pl<=pu and max(pl,final['j_lower'])<=min(pu,final['j_upper']),'Production/independent original-policy compatibility')
        ex.require(F(r['original_optimum_lower'])<=hi,'Production optimum lower/independent feasible upper compatibility')
        rl,ru=max(F(0),final['j_lower']-hi),final['j_upper']-lo
        prl,pru=(None,None) if proposal is None else (max(F(0),proposal['j_lower']-hi),proposal['j_upper']-lo)
        ex.require(0<=rl<=ru,'Independent nonnegative final original regret')
        if proposal is not None:ex.require(0<=prl<=pru,'Independent nonnegative raw proposal regret')
        cap=F(1,8)+sum(map(F,r['state']))/16
        result={k:r[k] for k in ['index','row','budget','arm','loss','state_hex','action_hex']}
        result.update(key_id=final['key_id'],proposal_key_id=None if proposal is None else proposal['key_id'],
                      j_lower=final['j_lower'],j_upper=final['j_upper'],
                      original_optimum_lower=lo,original_optimum_upper=hi,
                      original_regret_lower=rl,original_regret_upper=ru,
                      squared_original_action_error_upper=min(cap**2,ru),
                      proposal_j_lower=None if proposal is None else proposal['j_lower'],proposal_j_upper=None if proposal is None else proposal['j_upper'],
                      proposal_regret_lower=prl,proposal_regret_upper=pru,
                      proposal_squared_original_action_error_upper=None if proposal is None else min(cap**2,pru),
                      proposal_equals_final=None if proposal is None else references[(ident,'proposal')]==references[(ident,'final')],
                      proposal_unavailable_due_to_recorded_numerical_failure=proposal is None,
                      compatibility_does_not_certify_narrower_production_endpoints=True)
        if r['loss']=='marginal':
            vi=(r['index'],r['row'],r['budget'],r['arm'],'value')
            vp=policies[references[(vi,'final')]]
            if references[(vi,'final')]==references[(ident,'final')]:gl=gu=F(0)
            else:
                gl=max(-ex.TAU,vp['j_lower']-final['j_upper'])
                gu=min(ex.TAU,vp['j_upper']-final['j_lower'])
            ex.require(-ex.TAU<=gl<=gu<=ex.TAU,'Signed loss-treatment gain support')
            result.update(value_incumbent_key_id=vp['key_id'],marginal_gain_lower=gl,marginal_gain_upper=gu,
                          gain_is_not_assumed_nonnegative=True)
        append_jsonl(out/'comparisons121.jsonl',ex.encoded(result));ex.count('independent_policy_comparisons')
    return len(optima)


def main():
    p=argparse.ArgumentParser();p.add_argument('--source-commit',required=True)
    p.add_argument('--primary',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();source=verify_source(a.source_commit)
    out,initial=exclusive_attempt(a.output,'independent121',source);clock=time.perf_counter();trace=None
    try:
        primary=a.primary.resolve();input_hash=digest(primary)
        write_json(out/'PRIMARY_INPUT121.json',{'path':str(primary),'bytes':primary.stat().st_size,'sha256':input_hash})
        rows=read_rows(primary);actions,refs=catalogue(rows);ir,primitive=ex.load_primitives()
        write_json(out/'INDEPENDENT_DESIGN121.json',{'unique_policy_and_proposal_keys':len(actions),'primary_rows':len(rows),
            'bins':ex.BINS,'terminal_steps':ex.TERMINAL_STEPS,'expected_terminal_contexts':len(actions)*(2*ex.BINS+1),
            'all_final_and_raw_proposal_keys_required':True,'primitive':primitive,'outcome_dependent_refinement':False})
        trace=ex.ExactTrace(out/'terminal_witnesses121.jsonl.gz');policies={}
        for j,(k,v) in enumerate(sorted(actions.items())):
            append_jsonl(out/'PROGRESS121.jsonl',{'event':'key-start','index':j,'key_id':ex.key_id(k)})
            result=ex.evaluate_action(ir,k,v,trace);policies[k]=result
            append_jsonl(out/'policies121.jsonl',ex.encoded(result))
            append_jsonl(out/'PROGRESS121.jsonl',{'event':'key-complete','index':j,'key_id':ex.key_id(k),'seconds':result['seconds']})
            if (j+1)%32==0 or j+1==len(actions):print('INDEPENDENT',j+1,'/',len(actions),round(time.perf_counter()-clock,3),flush=True)
        trace.close();trace=None;state_count=compare(rows,refs,policies,out)
        ex.require(digest(primary)==input_hash,'Immutable primary input')
        write_json(out/'EXECUTION121.json',{'status':'executed','exit_code':0,'source':source,
            'started_unix':initial['started_unix'],'ended_unix':time.time(),'total_seconds':time.perf_counter()-clock,
            'primary_rows':len(rows),'unique_policy_and_proposal_keys':len(policies),'state_risk_optimum_intervals':state_count,
            'counts':ex.COUNTS,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'external_authorship_claimed':False,'exact_rounded_future_policy_equality_claimed':False,
            'new_original_policy_and_proposal_evaluations':True})
    except BaseException:
        if trace is not None:trace.close()
        append_jsonl(out/'FAILED121.jsonl',{'status':'failed','source':source,'ended_unix':time.time(),
            'elapsed_seconds':time.perf_counter()-clock,'counts':ex.COUNTS,'exception':traceback.format_exc(),
            'all_partial_evidence_retained':True});raise


if __name__=='__main__':main()
