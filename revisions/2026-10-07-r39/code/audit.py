"""R39 offline audit and all-state ReLU verification; never retimes R38.

Stored binary64 coefficients denote exact real dyadics. Every ReLU break point
is included by an outward interval, including roots that are not dyadic.
The original 315 service records and clocks are read-only inputs.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict, Counter
import hashlib,json,sys,statistics,math
import numpy as np
HERE=Path(__file__).resolve().parents[1]
OLD=HERE.parent/'2026-10-07-r38'
sys.path.insert(0,str(OLD/'code'))
from nonlinear import I, spline, lipschitz


def network(net,x:I):
    v=I.point(net['intercept'])+I.point(net['linear'])*x
    for w,b,c in zip(net['w'],net['b'],net['c']):
        q=w*x+b
        v=v+c*I(np.maximum(q.lo,0),np.maximum(q.hi,0))
    return v


def breakpoint_bound(net,knots,values):
    """Enclose sup_[0,1]|network - spline| over every affine-piece endpoint."""
    knots=np.asarray(knots,dtype=float);values=np.asarray(values,dtype=float)
    if not (knots.ndim==1 and len(knots)==len(values) and knots[0]==0 and knots[-1]==1 and np.all(np.diff(knots)>0)):
        raise ValueError('A strictly increasing partition of [0,1] is required')
    arrays=[np.atleast_1d(net[k]).astype(float) for k in ('w','b','c','linear','intercept')]
    if not all(np.isfinite(a).all() for a in arrays):raise ValueError('Nonfinite network')
    if not len(net['w'])==len(net['b'])==len(net['c']):raise ValueError('Network dimensions')
    boxes=[(float(x),float(x)) for x in knots]
    for w,b in zip(net['w'],net['b']):
        if w==0:continue
        root=I.point(-float(b))/float(w)
        if root.hi>=0 and root.lo<=1:
            boxes.append((max(0.,float(root.lo)),min(1.,float(root.hi))))
    x=I(np.array([b[0] for b in boxes]),np.array([b[1] for b in boxes]))
    delta=network(net,x)-spline(x,knots,values,lipschitz(knots,values))
    return dict(uniform_error_upper=float(np.max(np.maximum(abs(delta.lo),abs(delta.hi)))),
                tested_boxes=len(boxes),neural_width=len(net['w']),state_domain=[0,1],
                guarantee='All affine-piece endpoints enclosed; not a sampling bound')


def exact_sup(net,knots,values):
    """Independent rational check, used only for audit, not timed production."""
    k=list(map(F,knots));v=list(map(F,values))
    w,b,c=([F(x) for x in net[name]] for name in ('w','b','c'))
    pts=set(k)
    pts.update(-bb/ww for ww,bb in zip(w,b) if ww and 0<=-bb/ww<=1)
    import bisect
    answer=F(0)
    for x in pts:
        j=min(len(k)-2,max(0,bisect.bisect_right(k,x)-1))
        sv=v[j]+(v[j+1]-v[j])*(x-k[j])/(k[j+1]-k[j])
        nv=F(net['intercept'])+F(net['linear'])*x+sum(cc*max(F(0),ww*x+bb) for ww,bb,cc in zip(w,b,c))
        answer=max(answer,abs(nv-sv))
    return answer


def load():
    run=OLD/'results/run-1';freeze=json.loads((run/'SOURCE_FREEZE.json').read_text())
    for name,h in freeze['files'].items():
        assert hashlib.sha256((OLD/name).read_bytes()).hexdigest()==h,name
    index=json.loads((run/'EXECUTIONS.json').read_text());groups=defaultdict(list)
    for row in index:
        assert row['returncode']==0,row['id']
        raw=run/'raw'/(row['id']+'.json')
        assert hashlib.sha256(raw.read_bytes()).hexdigest()==row['clock']['record_sha256']
        if row['id']=='warmup':continue
        s=row['specification'];row['record']=json.loads(raw.read_text())
        groups[(s['kind'],s['name'],s.get('method',''))].append(row)
    assert len(index)==316 and len(groups)==105
    assert all(len(rows)==3 for rows in groups.values())
    return groups,freeze


def main():
    groups,freeze=load();summaries=[];checks=[];unique={}
    for key,rows in sorted(groups.items()):
        times=[r['clock']['service_through_fsync_seconds'] for r in rows]
        v=rows[0]['record'];entry=dict(kind=key[0],name=key[1],method=key[2],replicates=3,
            service_seconds_median=statistics.median(times),service_seconds_min=min(times),service_seconds_max=max(times),
            peak_process_rss_kib=max(r['record']['process_peak_rss_kib'] for r in rows),
            service_ids=[r['id'] for r in rows])
        if key[0]=='policy':
            assert all(r['record']['certified'] for r in rows)
            entry.update(policy_gap_upper=v['policy_gap_upper'],counts=v['trials'][-1]['counts'],
                minimum_domain_margin=v['trials'][-1]['minimum_domain_margin'],
                epsilon=rows[0]['specification']['epsilon'],precision_trials=len(v['trials']))
        elif key[0] in ('neural','nonlinear'):
            entry.update(policy_gap_upper=v['candidate']['policy_gap_upper'],initial_actions=v['initial_actions'],
                own_policy_values=v['own_policy_values'],counterfactual=v.get('counterfactual'))
            if key[0]=='neural':
                for row in rows:
                    r=row['record'];knots=r['candidate']['knots']
                    for t,(net,values,prior) in enumerate(zip(r['networks'],r['candidate']['values'],r['uniform_network_checks'])):
                        digest=hashlib.sha256(json.dumps([net,knots,values],sort_keys=True).encode()).hexdigest()
                        if digest not in unique:
                            bound=breakpoint_bound(net,knots,values)
                            exact=exact_sup(net,knots,values)
                            assert F(bound['uniform_error_upper'])>=exact
                            assert bound['uniform_error_upper']<=prior['uniform_error_upper']
                            unique[digest]=dict(**bound,exact_rational_check=True,exact_sup_numerator=str(exact.numerator),exact_sup_denominator=str(exact.denominator))
                        checks.append(dict(service=row['id'],date=t,network_sha256=digest,
                            previous_upper=prior['uniform_error_upper'],new_upper=unique[digest]['uniform_error_upper']))
        else:entry['first_pass']=v['first_pass']
        summaries.append(entry)
    # Off-grid roots, zero hidden slopes, and endpoint roots are independent fixtures.
    fixtures=[dict(w=[3.,0.,-7.],b=[-1.,2.,2.],c=[.2,-.3,.7],linear=.125,intercept=-.5),
              dict(w=[1.,-2.],b=[0.,2.],c=[1.,1.],linear=0.,intercept=0.)]
    for net in fixtures:
        knots=[0.,.25,.5,1.];values=[.125,-.25,.2,.75]
        assert F(breakpoint_bound(net,knots,values)['uniform_error_upper'])>=exact_sup(net,knots,values)
    result=dict(review_commit='71949aa40c62c960dab824137bed12bb3516ff85',
        evidence_commit='2bb7a39a16c558da8269becc642b180847b2eb5c',source_freeze=freeze['source_commit'],
        original_service_count=315,original_clock_replacements=0,source_hashes_verified=True,
        result_hashes_verified=True,policy_services_certified=288,unique_networks=len(unique),
        network_checks=len(checks),rational_endpoint_checks_passed=len(unique)+len(fixtures),
        all_new_bounds_no_larger=True,network_bounds=checks,unique_network_certificates=unique,
        groups=summaries,inference='Deterministic objects; three clocks each; no population or universal superiority claim')
    (HERE/'audit').mkdir(exist_ok=True)
    (HERE/'audit/R39_AUDIT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('groups','network_bounds','unique_network_certificates')},indent=2))
    print('Network bounds:', min(r['new_upper'] for r in checks),max(r['new_upper'] for r in checks))

if __name__=='__main__':main()
