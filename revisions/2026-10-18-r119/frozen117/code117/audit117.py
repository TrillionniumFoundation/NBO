"""Separate standard-library exact audit of every R117 output row and gate.

No fitting, production risk, interval or service code is imported here.
An independently implemented primitive/risk audit is separately required.
"""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,time,statistics
KEYS=('lower','upper','optimum_lower','loss','width')
ARMS=('online','quadratic','relu','hinge','spline','poly2','poly3','grid')


def load(p):return json.loads(Path(p).read_text())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fr(x):return F(x)
def save(p,obj):Path(p).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')


def audit(out):
    out=Path(out);start=time.perf_counter();checks=0;decisions=0;attempts=0
    def ck(ok,msg):
        nonlocal checks
        if not ok:raise ArithmeticError(msg)
        checks+=1
    def bounds(row):
        a={k:fr(row[k]) for k in KEYS}
        ck(a['lower']<=a['upper'],'Reversed cost enclosure')
        ck(a['optimum_lower']<=a['upper'],'Contradictory optimum bound')
        ck(a['loss']>=a['upper']-a['optimum_lower']>=0,'Non-outward regret bound')
        ck(a['width']>=a['upper']-a['lower']>=0,'Non-outward width')
        return a['loss']<=F(1,256) and a['width']<=F(1,8192)
    manifests=['CATALOGUE.json']+[f'timing/PROCESS-{r}.json' for r in range(7)]
    for mf in manifests:
        for entry in load(out/mf)['entries']:
            path=out/entry['path'];ck(digest(path)==entry['sha256'],'Stored file identity')
            data=load(path);byrow={}
            for trial in data.get('attempts',[]):
                attempts+=1;ok=bounds(trial);ck(ok==trial['qualified'],'Qualification predicate')
                byrow.setdefault(trial['row'],[]).append(trial)
            for j,row in enumerate(data['rows']):
                decisions+=1;ck(row['row']==j,'Complete ordered rows')
                ck(bounds(row),'Final original qualification')
                capacity=F(1,8)+(fr(row['x0'])+fr(row['x1']))/16
                ck(0<=fr(row['action'])<=capacity,'Original action feasibility')
                ck(fr(row['action_distance_upper'])**2>=fr(row['loss']),'Action-distance upper bound')
                if data['service']=='geometric':
                    seq=byrow[j];init=[v for v in seq if v['kind']=='initial']
                    allowed=[8,16,32,64,128]
                    ck([v['bins'] for v in init]==allowed[:len(init)],'Ordered paid precision ladder')
                    ck(all(not v['qualified'] for v in init[:-1]),'A resolved proposal was queried again')
                    ck(init[-1]['bins']==row['first_resolution'],'First resolution receipt')
                    if init[-1]['qualified']:
                        ck(len(seq)==len(init),'Uncharged work after acceptance')
                        ck(row['action']==row['proposed'],'Accepted proposal action changed')
                    else:ck(init[-1]['bins']==128,'Premature fallback')
                    final=seq[-1]
                    ck(row['action']==final['action'],'Returned action trace')
                    for k in KEYS:ck(row[k]==final[k],'Returned certificate trace')
    ck(decisions==11776,'All primary and timing decisions')
    campaign=load(out/'CAMPAIGN117.json')
    ck(len(campaign['processes'])==7 and all(p['exit_code']==0 for p in campaign['processes']),'Seven actual successful processes')
    kernel=load(out/'KERNEL_REPLAY108.json');ck(kernel['status']=='passed' and kernel['checks']==3072,'Independent original kernel replay')
    contrasts=[];equivalence=[];frontier=[]
    refs=load(out/'REFERENCE117.json')['records']
    for i in range(2):
        for arm in ARMS:
            a=load(out/'catalogue'/f'{i}-{arm}-compiled.json');b=load(out/'catalogue'/f'{i}-{arm}-geometric.json')
            ref=next(v for v in refs if v['index']==i and v['arm']==arm);rr={v['row']:v for v in ref['rows']}
            ls=[];us=[];same=0;improved=0;worsened=0
            for j,(aa,bb) in enumerate(zip(a['rows'],b['rows'])):
                ck(aa['proposed']==bb['proposed'],'Common actually realized proposal')
                if aa['action']==bb['action']:lo=hi=F(0);same+=1;ck(j not in rr,'Unnecessary identity reference')
                else:
                    r=rr[j];ck(r['control_action']==aa['action'] and r['treatment_action']==bb['action'],'Reference action identity')
                    for side,old in (('control',aa),('treatment',bb)):
                        bounds(r[side])
                        ck(max(fr(r[side]['lower']),fr(old['lower']))<=min(fr(r[side]['upper']),fr(old['upper'])),'Contradictory repeated policy intervals')
                    lo=max(-F(1,256),fr(r['treatment']['lower'])-fr(r['control']['upper']))
                    hi=min(F(1,256),fr(r['treatment']['upper'])-fr(r['control']['lower']))
                    ck(lo<=hi,'Policy contrast support')
                ls.append(lo);us.append(hi);improved+=hi<0;worsened+=lo>0
            contrasts.append(dict(index=i,arm=arm,same_actions=same,changed_actions=144-same,
                treatment_strictly_better=improved,treatment_strictly_worse=worsened,
                mean_policy_contrast=[str(sum(ls,F(0))/144),str(sum(us,F(0))/144)]))
            acquisition=load(out/'models'/f'{i}-{arm}'/'acquisition.json')
            charged=load(out/'models'/f'{i}-relu'/'acquisition.json') if arm=='hinge' else acquisition
            cost=sum(charged.get(k,0.) for k in ('fit_seconds','audit_seconds','serialization_seconds','label_cost_if_standalone_seconds'))
            if arm=='hinge':cost+=acquisition.get('serialization_seconds',0.)
            for service,data in (('compiled',a),('geometric',b)):
                clocks=[load(out/'timing'/f'{r}-{i}-{arm}-{service}.json')['seconds'] for r in range(7)]
                certs=sum(data['counts'].get(k,0) for k in ('r96_midpoint_terminal_rows','r96_endpoint_terminal_rows'))
                frontier.append(dict(index=i,arm=arm,service=service,primary_seconds=data['seconds'],
                    continuation_locations=certs,original_certificates=data['counts'].get('r96_original_action_certificates',0),
                    timing_seconds=clocks,timing_median=statistics.median(clocks),timing_range=[min(clocks),max(clocks)],
                    standalone_acquisition_seconds=cost,standalone_32_decision_seconds=cost+statistics.median(clocks),
                    payload_bytes=acquisition['payload_bytes'],first_rejections=sum(v['first_rejected'] for v in data['rows']),
                    resolutions={str(n):sum(v.get('first_resolution',128)==n for v in data['rows']) for n in (8,16,32,64,128)},
                    qualified_decisions=len(data['rows']),max_loss=max(v['loss'] for v in data['rows']),max_width=max(v['width'] for v in data['rows'])))
        for service in ('compiled','geometric'):
            a=load(out/'catalogue'/f'{i}-relu-{service}.json')['rows'];b=load(out/'catalogue'/f'{i}-hinge-{service}.json')['rows']
            equivalence.append(dict(index=i,service=service,identical_actions=sum(x['action']==y['action'] for x,y in zip(a,b)),
                identical_certificates=sum(all(x[k]==y[k] for k in KEYS) for x,y in zip(a,b))))
    diagnostic=load(out/'EXACT117.json');ck(len(diagnostic['rows'])==120,'Complete exact diagnostic')
    for r in diagnostic['rows']:
        a,star,theta=map(F,(r['action'],r['optimal_action'],r['risk']))
        cost=4*(a-F(1,2))**2+F(15,16)*a*theta
        optimum=4*(star-F(1,2))**2+F(15,16)*star*theta
        ck(cost==F(r['original_cost']) and optimum==F(r['optimal_cost']),'Independent economic objective reconstruction')
        ck(F(r['regret'])==cost-optimum==4*(a-star)**2,'Action-estimation exact loss identity')
        ck(0<=F(r['regret'])<=F(r['regret_bound']),'Exact loss certificate')
        if r['qualified']:ck(F(r['regret'])<=F(r['epsilon']),'Claimed tolerance')
        for step in r['trace']:
            lo,hi=F(step['lower']),F(step['upper']);ck(lo<=theta<=hi,'Exact reference inside each risk bracket')
            bound=4*(F(15,16)*(hi-lo)/16+F(1,2**30))**2
            ck(bound==F(step['regret_bound']),'Squared-gap allowance')
    result=dict(status='passed',rational_record_checks=checks,decision_rows=decisions,paid_attempt_rows=attempts,
        frontier=frontier,policy_contrasts=contrasts,encoding_equivalence=equivalence,
        kernel_checks=kernel['checks'],exact_method_rows=120,seconds=time.perf_counter()-start,
        neural_exclusive_claim=False,population_confidence_claim=False,
        scope='Every recorded current decision, paid precision gate, same-policy reference and exact diagnostic; independent primitive replay is separately recorded. Not a formal proof or full historical replay.')
    save(out/'AUDIT117.json',result);print('AUDIT PASSED',checks,decisions,attempts)
    return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();audit(a.output)
