"""Independent whole-cell checker: no Bellman envelope optimizer is invoked.
The construction and verification share only rational representation, model
primitives, and affine composition. This checker does not re-run training.
"""
from coupled import *
import gzip, copy


def require(condition,message):
    if not condition: raise ValueError(message)


def pointwise_leq(left:PW,right:PW,active:PW|None=None):
    fs=[left,right]+([] if active is None else [active]); xs=sorted(set(x for f in fs for x in f.xs))
    for x in xs:
        if active is None or active.at(x): require(left.at(x)<=right.at(x),'knot inequality failed')
    for l,r in zip(xs,xs[1:]):
        z=(l+r)/2
        if active is None or active.at(z):
            a,b=left.line(z); c,d=right.line(z)
            require((a-c)*l+b-d<=0 and (a-c)*r+b-d<=0,'open-cell limiting inequality failed')


def pointwise_equal(left:PW,right:PW):
    pointwise_leq(left,right); pointwise_leq(right,left)


def check(cert:dict):
    require(cert.get('model')==model(),'changed or absent model')
    eps=F(cert['epsilon']); require(eps>0,'nonpositive tolerance')
    U=[PW.load(x) for x in cert['U']]; raw=[PW.load(x) for x in cert['raw']]
    p=[PW.load(x) for x in cert['policy']]; D=[PW.load(x) for x in cert['D']]; J=[PW.load(x) for x in cert['J']]
    T=len(p); require(T>0 and len(raw)==T and len(U)==len(D)==len(J)==T+1,'wrong horizon or missing date')
    for f in raw+p:
        require(all(a==0 and b in (0,1,2) for a,b in f.ab) and all(y in (0,1,2) for y in f.ys),'infeasible compiled action')
    pointwise_equal(U[T],affine(F(1,2))); pointwise_equal(J[T],affine(F(1,2))); pointwise_equal(D[T],affine())
    eta=eps/sum((BETA**j for j in range(T)),ZERO); e=ZERO; maxgap=ZERO
    zero=cert.get('mode')=='zero_intervention'
    for t in reversed(range(T)):
        q=q_functions(U[t+1]);
        for f in q: pointwise_leq(f,U[t])
        pointwise_equal(J[t],select(q_functions(J[t+1]),p[t]))
        gap=linear_comb([U[t],J[t]],[ONE,-ONE]); maxgap=max(maxgap,gap.extent()[1])
        if zero:
            pointwise_equal(p[t],raw[t]); pointwise_equal(D[t],affine()); require(gap.extent()[1]<=eps,'raw policy not globally certified')
        else:
            e=eta+BETA*e
            require(gap.extent()[1]<=e,'regret envelope exceeded')
            selected=select(q,p[t]); require(linear_comb([U[t],selected],[ONE,-ONE]).extent()[1]<=eta,'selected action not admissible')
            allowed=[threshold(linear_comb([U[t],f],[ONE,-ONE]),eta) for f in q]
            cq=q_functions(D[t+1],operating=False)
            cq=[linear_comb([v,intervention(raw[t],a)],[ONE,ONE]) for a,v in enumerate(cq)]
            for a,f in enumerate(cq): pointwise_leq(D[t],f,allowed[a])
            pointwise_equal(D[t],select(cq,p[t]))
    return {'certified':True,'max_regret':str(maxgap),'mode':'zero_intervention' if zero else 'cost_minimum_in_certified_class'}


def audit_all(folder:Path):
    results=[]; zeros=[]; total=0.
    for file in sorted((folder/'certificates').glob('*.json.gz')):
        if file.name.startswith('zero_'): continue
        data=gzip.decompress(file.read_bytes()); cert=json.loads(data)
        tic=time.perf_counter(); checked=check(cert); elapsed=time.perf_counter()-tic; total+=elapsed
        results.append({'file':file.name,'sha256':hashlib.sha256(data).hexdigest(),'seconds':elapsed,**checked})
        # A certified incumbent has globally minimal intervention cost zero,
        # even if a conservative stagewise class would exclude it.
        raw=[PW.load(p) for p in cert['raw']]; U=[PW.load(v) for v in cert['U']]
        tic=time.perf_counter(); V=evaluate(raw)
        bound=max(linear_comb([u,v],[ONE,-ONE]).extent()[1] for u,v in zip(U,V))
        if bound<=F(cert['epsilon']):
            z={**cert,'mode':'zero_intervention','policy':cert['raw'],'J':[v.dump() for v in V],'D':[affine().dump()]*(len(raw)+1)}
            checkedzero=check(z); zeros.append({'file':file.name,'seconds_including_own_evaluation':time.perf_counter()-tic,**checkedzero})
            encoded=json.dumps(z,sort_keys=True,separators=(',',':')).encode()
            with gzip.GzipFile(filename=str(folder/'certificates'/('zero_'+file.name)),mode='wb',mtime=0) as f: f.write(encoded)
    require(len(results)==42,'incomplete registered cohort')
    require(len(zeros)==12,'unexpected zero-intervention result; investigate rather than relabel')
    out={'checker':'whole-cell endpoint/limit comparisons without envelope maximization','certificate_count':len(results),'zero_intervention_count':len(zeros),'independent_check_seconds':total,'results':results,'zero_intervention_certificates':zeros}
    (folder/'independent_audit.json').write_text(json.dumps(out,indent=2,sort_keys=True)); return out


def tests():
    T=2; eps=F(1,20); U,qs,wl=witnesses(T,eps); raw=stress_policy(T)
    _,cert=summary_case(T,eps,U,qs,wl,raw,'stress',{})
    check(cert); mutations=[]
    def reject(name,mutate):
        bad=copy.deepcopy(cert); mutate(bad)
        try: check(bad)
        except (ValueError,AssertionError,KeyError,IndexError): mutations.append(name); return
        raise AssertionError('accepted malformed certificate: '+name)
    reject('changed_model',lambda x:x['model'].__setitem__('beta','1'))
    reject('missing_model',lambda x:x.pop('model'))
    reject('negative_tolerance',lambda x:x.__setitem__('epsilon','-1/100'))
    reject('missing_date',lambda x:x['U'].pop())
    reject('missing_interval',lambda x:x['policy'][0]['affine'].pop())
    reject('wrong_endpoint',lambda x:x['U'][0]['points'].__setitem__(0,'-100'))
    reject('false_cost',lambda x:x['D'][0]['points'].__setitem__(0,'999'))
    reject('infeasible_action',lambda x:x['policy'][0]['points'].__setitem__(0,'3'))
    # Point spikes are not erased by interval normalization or integration.
    spike=PW([ZERO,F(1,2),ONE],[(ZERO,ZERO),(ZERO,ZERO)],[ZERO,ONE,ZERO]).norm()
    require(spike.at(F(1,2))==1 and len(spike.ab)==2,'isolated point lost')
    mapped=compose(spike,F(1,2),F(1,4)); require(mapped.at(F(1,2))==1,'preimage singleton lost')
    # Exhaustive two-period tree enumeration at rational restart states,
    # including adaptive second-date actions, independently checks V*.
    from itertools import product
    V,opt,_=exact_dp(2)
    for x in (ZERO,F(1,3),F(1,2),ONE):
        values=[]
        for a in range(3):
            states=[s*x+b for s,b in MAPS[a]]
            for suffix in product(range(3),repeat=2):
                v=x-COSTS[a]
                for prob,y,b in zip(PROBS,states,suffix):
                    continuation=y-COSTS[b]+BETA*sum((p*(s*y+c)/2 for p,(s,c) in zip(PROBS,MAPS[b])),ZERO)
                    v+=BETA*prob*continuation
                values.append(v)
        require(max(values)==V[0].at(x),'finite tree exhaustive comparison failed')
    return {'rejected_mutations':mutations,'point_and_preimage_checks':True,'exhaustive_two_period_tree_checks':4,'passed':True}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--folder',type=Path); args=ap.parse_args(); r=tests()
    if args.folder:
        (args.folder/'tests.json').write_text(json.dumps(r,indent=2)); a=audit_all(args.folder); print('checked',a['certificate_count'],'zero-cost',a['zero_intervention_count'])
    print(json.dumps(r,indent=2))
