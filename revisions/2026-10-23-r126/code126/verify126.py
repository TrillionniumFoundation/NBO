"""Exact source/design/arithmetic replay; independent126 is separate economics."""
import argparse, collections
from common126 import *


IDENTITY_FIELDS=('action_hex','complete_policy_lower','complete_policy_upper','certified_regret_upper',
                 'width','target_qualified126','direct_requested_terminal_contexts126','stop126','counts126')


def run(primary,timings,output):
    out,tick,info=start(output,'saved-certificate-census-and-timing-replay')
    try:
        verified=verify_inputs(); import service126 as svc; svc.configure()
        data=rows(Path(primary)/'records126.jsonl.gz')
        key=lambda r:tuple(r[k] for k in ('index','budget','arm','training_loss','mode','row'))
        table={key(r):r for r in data}
        expected={c+(i,) for c in catalog() for i in range(len(STATES))}
        assert len(data)==len(table)==1584 and set(table)==expected
        checks=1; queries=0; candidate_count=0; improvements=0
        for r in data:
            state=STATES[r['row']]; A=F(1,8)+sum(map(F,state))/16
            assert tuple(r['state126'])==state and 0<=F(r['action'])<=A; checks+=1
            assert F(r['certified_regret_upper'])<=TAU and F(r['width'])<=OMEGA; checks+=1
            assert r['target_qualified126']==(F(r['certified_regret_upper'])<=TARGET and F(r['width'])<=OMEGA); checks+=1
            assert F(r['complete_policy_lower'])<=F(r['complete_policy_upper']); checks+=1
            if r['mode']!='direct_terminal': continue
            qs=r['new_queries126']; saved=r['initial_support_certificates']
            assert r['direct_requested_terminal_contexts126']==sum(q['requested_terminal_nodes'] for q in qs)<=NODE_BUDGET; checks+=1
            assert all(q['bins'] in LADDER and q['requested_terminal_nodes']==2*q['bins']+1 for q in qs); checks+=1
            assert len({(q['action'],q['bins']) for q in qs})==len(qs); checks+=1
            successful=[q['certificate'] for q in qs if q['completed']]
            assert saved==successful; checks+=1; queries+=len(qs)
            for q in qs:
                assert 0<=F(q['action'])<=A and q['center']<MAX_CENTERS; checks+=1
                if q['completed']:
                    assert q['certificate']['original_state']==[list(state)] and q['certificate']['alpha']==r['alpha']; checks+=1
                    assert F(q['action'])==F(q['certificate']['original_action']); checks+=1
            by_query={int(c['query']):c for c in r['candidate_records126']}
            for idx,record in by_query.items():
                case=svc.make_case([q['certificate'] for q in qs[:idx+1] if q['completed']],state,r['alpha'],F(record['case']['incumbent']))
                assert plain(case)==record['case']; checks+=1
                common=svc.env.support_minimum(case)
                for c in record['certificates']:
                    replay=svc.terminal_certificate(case,F(c['b']),common)
                    assert plain(replay)==c; checks+=1; candidate_count+=1
            for a in r['acceptances126']:
                if a['reason']!='strict-original-policy-improvement': continue
                record=by_query[a['query']]; case=svc.env.normalize(record['case'])
                old=next(c for c in record['certificates'] if c['b']==a['old_action'])
                new=next(c for c in record['certificates'] if c['b']==a['action'])
                _,upper=svc.env.contrast(case,F(a['old_action']),F(a['action']))
                upper=min(upper,F(new['upper'])-DELTA-F(old['lower']))
                assert F(a['gain_lower'])==-upper-DELTA>0 and new['qualified']; checks+=1; improvements+=1
            selected=r['selected_certificate126']
            if selected is not None:
                assert selected['qualified'] and F(selected['b'])==F(r['action']); checks+=1
                final=svc.final_row(selected,state) if not isinstance(selected['b'],str) else svc.final_row({**selected,'b':F(selected['b'])},state)
                for field in ('action_hex','complete_policy_lower','complete_policy_upper','certified_regret_upper','width'):
                    assert final[field]==r[field]; checks+=1
        matched=0
        for k,r in table.items():
            if r['arm']!='relu': continue
            partner=list(k); partner[2]='hinge'; other=table[tuple(partner)]
            for field in IDENTITY_FIELDS:
                assert r[field]==other[field],('matched geometry differs',k,field); checks+=1
            matched+=1
        timed_count=0
        for timing in timings:
            timed=rows(Path(timing)/'records126.jsonl.gz')
            assert len(timed)==176 and {key(r) for r in timed}=={c+(0,) for c in catalog()}; checks+=1
            for r in timed:
                primary_row=table[key(r)]
                for field in IDENTITY_FIELDS:
                    assert r[field]==primary_row[field],('timing changed scientific outcome',timing,key(r),field); checks+=1
            timed_count+=len(timed)
        assert len(timings)==3 and timed_count==528; checks+=1
        finish(out,tick,checks=checks,primary_decisions=len(data),timing_decisions=timed_count,
            direct_query_attempts=queries,exact_candidate_replays=candidate_count,
            strict_original_policy_improvements=improvements,matched_relu_hinge_pairs=matched,
            independent_economic_evaluations=0,source=verified)
    except BaseException: fail(out,tick); raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--primary',required=True);p.add_argument('--timing',action='append',required=True)
    p.add_argument('--output',required=True);a=p.parse_args();run(a.primary,a.timing,a.output)
