"""All-restart lower-bound propagation; construction and optimizer-free checks.

The lower bound retains every action, including randomized mixtures. Exact
Fractions describe all open cells AND isolated boundary points. Nothing in this
module changes the incumbent or the certified deployed policy.
"""
from global_cost import *
import argparse, copy, gzip, hashlib, json, time

LOCAL_PRICES = PRICES
VERSION = 'r34-all-restart-local-dual-1'


def hash_obj(obj):
    return hashlib.sha256(encoded(obj)).hexdigest()


def selector_valid(p, n):
    require(all(a == ZERO and b.denominator == 1 and 0 <= b < n for a,b in p.ab)
            and all(v.denominator == 1 and 0 <= v < n for v in p.ys),
            'invalid source selector')


def local_actions(U_next, L_now, A_next, raw_now, epsilon, mu):
    q = q_functions(U_next)
    z = [linear_comb([v,intervention(raw_now,a)], [ONE,ONE])
         for a,v in enumerate(q_functions(A_next,operating=False))]
    return [linear_comb([zz,L_now,qq],[ONE,mu,-mu],b=-mu*epsilon)
            for zz,qq in zip(z,q)]


def construct(base):
    eps=F(base['epsilon']); T=base['T']
    U=[PW.load(x) for x in base['U']]
    L=check_inputs(U,[PW.load(x) for x in base['gamma']],list(map(F,base['defects'])))
    B=[PW.load(x) for x in base['cost_lower']]
    raw=[PW.load(x) for x in base['raw']]
    A=[None]*(T+1); A[T]=affine(); stages=[None]*T
    max_intermediate=0; tic=time.perf_counter()
    for t in reversed(range(T)):
        mins=[]; policies=[]
        for mu in LOCAL_PRICES:
            fs=local_actions(U[t+1],L[t],A[t+1],raw[t],eps,mu)
            m,p=envelope(fs,maximize=False)
            max_intermediate=max(max_intermediate,len(m.ab),max(len(f.ab) for f in fs))
            mins.append(m);policies.append(p)
        terms=[affine(),B[t]]+mins
        A[t],source=envelope(terms,maximize=True)
        stages[t]={'minima':[m.dump() for m in mins],
                   'minimizers':[p.dump() for p in policies], 'source':source.dump()}
    seconds=time.perf_counter()-tic
    obj={'version':VERSION,'model':model(),'T':T,'proposal':base['proposal'],
         'epsilon':base['epsilon'],'base_sha256':hash_obj(base),
         'support_sha256':base['support_sha256'],
         'local_multipliers':list(map(str,LOCAL_PRICES)),
         'A':[v.dump() for v in A],'stages':stages,
         'integrated_improvement':str(A[0].integral()-B[0].integral()),
         'integrated_cost_gap':str(PW.load(base['C'][0]).integral()-A[0].integral())}
    allpw=A+[PW.load(v) for st in stages for v in st['minima']]
    meta={'construction_seconds':seconds,'max_stored_closure_pieces':max(len(a.ab) for a in A),
          'max_local_function_pieces':max_intermediate,
          'max_bits':max(v.bits() for v in allpw),
          'additional_unrestricted_support_solves':0}
    return obj,meta


def check_closure(obj,base):
    """Check a closure AFTER the base and its support portfolio are checked.

    No envelope or optimizing routine is called. All extrema are proved by
    exact whole-cell inequalities plus selector equalities, including points.
    """
    require(obj['version']==VERSION and obj['model']==model(),'wrong closure model/version')
    require(obj['base_sha256']==hash_obj(base),'wrong base hash')
    require(obj['support_sha256']==base['support_sha256'],'wrong support hash')
    require(obj['local_multipliers']==list(map(str,LOCAL_PRICES)),'changed multiplier portfolio')
    eps=F(obj['epsilon']); T=obj['T']
    require(eps>0 and T==base['T'] and obj['epsilon']==base['epsilon'] and obj['proposal']==base['proposal'],'wrong closure scope')
    U=[PW.load(x) for x in base['U']]
    L=check_inputs(U,[PW.load(x) for x in base['gamma']],list(map(F,base['defects'])))
    B=[PW.load(x) for x in base['cost_lower']];C=[PW.load(x) for x in base['C']]
    raw=[PW.load(x) for x in base['raw']]
    A=[PW.load(x) for x in obj['A']];stages=obj['stages']
    require(len(A)==T+1 and len(stages)==T,'missing closure date')
    pointwise_equal(A[T],affine());pointwise_equal(B[T],affine())
    for t in reversed(range(T)):
        st=stages[t]
        require(len(st['minima'])==len(st['minimizers'])==len(LOCAL_PRICES),'missing multiplier')
        mins=[PW.load(x) for x in st['minima']]
        for mu,m,pd in zip(LOCAL_PRICES,mins,st['minimizers']):
            p=PW.load(pd);selector_valid(p,3)
            fs=local_actions(U[t+1],L[t],A[t+1],raw[t],eps,mu)
            for f in fs:pointwise_leq(m,f)
            pointwise_equal(m,select(fs,p))
        terms=[affine(),B[t]]+mins
        s=PW.load(st['source']);selector_valid(s,len(terms))
        for f in terms:pointwise_leq(f,A[t])
        pointwise_equal(A[t],select(terms,s))
        pointwise_leq(B[t],A[t]);pointwise_leq(A[t],C[t])
    inc=A[0].integral()-B[0].integral();gap=C[0].integral()-A[0].integral()
    require(F(obj['integrated_improvement'])==inc and F(obj['integrated_cost_gap'])==gap,'false closure scalar')
    require(inc>=0 and gap>=0,'negative improvement or primal gap')
    return {'passed':True,'integrated_improvement':str(inc),'new_global_lower':str(A[0].integral()),
            'old_global_lower':str(B[0].integral()),'new_global_gap':str(gap),
            'old_global_gap':base['integrated_cost_gap'],
            'upper_cost':str(C[0].integral()),
            'all_restart_max_pointwise_improvement':str(max(linear_comb([a,b],[ONE,-ONE]).extent()[1] for a,b in zip(A,B))),
            'all_restart_order_verified':True,'extra_support_solves':0}


def reject_mutations(obj,base):
    rejected=[]
    def reject(name,mutate):
        bad=copy.deepcopy(obj);mutate(bad)
        try:check_closure(bad,base)
        except (ValueError,AssertionError,KeyError,IndexError,TypeError):rejected.append(name);return
        raise AssertionError('corruption accepted: '+name)
    reject('negative_multiplier',lambda x:x['local_multipliers'].__setitem__(0,'-1'))
    reject('missing_multiplier',lambda x:x['stages'][0]['minima'].pop())
    reject('isolated_lower_point',lambda x:x['A'][0]['points'].__setitem__(0,'9999'))
    reject('isolated_minimum_point',lambda x:x['stages'][0]['minima'][0]['points'].__setitem__(0,'9999'))
    reject('illegal_minimizer',lambda x:x['stages'][0]['minimizers'][0]['points'].__setitem__(0,'3'))
    reject('fractional_source_selector',lambda x:x['stages'][0]['source']['points'].__setitem__(0,'1/2'))
    reject('wrong_terminal',lambda x:x['A'][-1]['points'].__setitem__(0,'1'))
    reject('missing_date',lambda x:x['A'].pop())
    reject('changed_base_hash',lambda x:x.__setitem__('base_sha256','0'*64))
    reject('changed_support_hash',lambda x:x['support_sha256'].__setitem__(0,'0'*64))
    reject('overstated_gap',lambda x:x.__setitem__('integrated_cost_gap','-1'))
    reject('changed_tolerance',lambda x:x.__setitem__('epsilon','1/2'))
    return rejected


def exhaustive_tests():
    """Finite-tree sanity check, not a substitute for the continuum proof.

    At each of 4 restart states enumerate 27 deterministic two-period plans,
    then all unordered equal mixtures, retaining the restart feasibility
    constraint at each reached history. This includes randomized first actions
    and conditional mixtures of future actions, without actionwise screening.
    """
    from itertools import product,combinations_with_replacement
    U,g,d,L,_=build_inputs(2); raw=stress_policy(2);V,_,_=exact_dp(2)
    eps=F(1,20);supports=[solve_support(U,g,d,raw,p)[0] for p in PRICES]
    B,idx=lower_envelope(L,supports,eps)
    # Enough data to build the lower-bound closure; feasibility upper is not
    # used in the construction. This synthetic base is not published as a
    # checked primal certificate.
    base={'T':2,'proposal':'two_period_test','epsilon':str(eps),'U':[x.dump() for x in U],
          'gamma':[x.dump() for x in g],'defects':list(map(str,d)),
          'cost_lower':[x.dump() for x in B],'raw':[x.dump() for x in raw],
          'support_sha256':[hash_obj(s) for s in supports], 'C':[affine(b=10).dump()]*3}
    obj,_=construct(base);A=[PW.load(x) for x in obj['A']]
    n=nr=eligible=eligible_random=0
    for x in (ZERO,F(1,3),F(1,2),ONE):
        plans=[]
        for a in range(3):
            ys=[m*x+b for m,b in MAPS[a]]
            for suffix in product(range(3),repeat=2):
                vals=[];costs=[]
                for y,b in zip(ys,suffix):
                    vals.append(y-COSTS[b]+BETA*sum((p*(m*y+c)/2 for p,(m,c) in zip(PROBS,MAPS[b])),ZERO))
                    costs.append((1+y)*(b!=raw[1].at(y)))
                j=x-COSTS[a]+BETA*sum((p*v for p,v in zip(PROBS,vals)),ZERO)
                c=(1+x)*(a!=raw[0].at(x))+BETA*sum((p*v for p,v in zip(PROBS,costs)),ZERO)
                gaps=[V[1].at(y)-v for y,v in zip(ys,vals)]
                feasible=V[0].at(x)-j<=eps and all(v<=eps for v in gaps)
                if feasible:require(A[0].at(x)<=c,'deterministic tree violates lower bound');eligible+=1
                plans.append((a,j,c,gaps));n+=1
        for p,q in combinations_with_replacement(plans,2):
            nr+=1;j=(p[1]+q[1])/2;c=(p[2]+q[2])/2
            if p[0]==q[0]: future=all((u+v)/2<=eps for u,v in zip(p[3],q[3]))
            else:future=all(v<=eps for v in p[3]+q[3])
            if V[0].at(x)-j<=eps and future:
                require(A[0].at(x)<=c,'randomized tree violates lower bound');eligible_random+=1
    require(eligible>0 and eligible_random>0,'vacuous exhaustive tests')
    return {'passed':True,'deterministic_plans':n,'equal_mixture_plans':nr,
            'restart_feasible_deterministic_plans':eligible,'restart_feasible_equal_mixtures':eligible_random,
            'state_count':4,'note':'Checks conditional expected feasibility for mixtures sharing the same observable first action; different first actions identify the mixture component.'}


def run(folder):
    (folder/'closures').mkdir(exist_ok=True);out={'version':VERSION,'protocol_commit':'70526abec87eeadd52dd7b30eaf75a78ba70e79c','outcomes':[],'failures':[]}
    for T in (4,8,12):
        d=json.loads((folder/f'H{T}.json').read_text())
        for rec in d['outcomes']:
            name=rec['file']
            try:
                raw=gzip.decompress((folder/'certificates'/name).read_bytes())
                require(hashlib.sha256(raw).hexdigest()==rec['sha256'],'base bytes changed')
                base=json.loads(raw);obj,stats=construct(base)
                tic=time.perf_counter();res=check_closure(obj,base);stats['internal_check_seconds']=time.perf_counter()-tic
                tic=time.perf_counter();stored=save(obj,folder/'closures'/name.replace('_primal_dual','_restart_closure'));stats['serialization_seconds']=time.perf_counter()-tic
                res.update({'T':T,'proposal':rec['proposal'],'epsilon':rec['epsilon'],
                            'base_file':name,'base_sha256':rec['sha256'],**stats,**stored})
                out['outcomes'].append(res)
                print('CLOSURE',T,rec['proposal'],rec['epsilon'],'improvement',float(F(res['integrated_improvement'])),'gap',float(F(res['new_global_gap'])),flush=True)
            except Exception as exc:
                out['failures'].append({'T':T,'base_file':name,'error':repr(exc)})
                print('UNRESOLVED',T,name,repr(exc),flush=True)
            (folder/'restart_closure.json').write_text(json.dumps(out,indent=2,sort_keys=True))
    require(len(out['outcomes'])==42 and not out['failures'],'incomplete closure cohort')
    return out


def independent(folder):
    import coupled,audit,global_cost as gc,recheck
    tic=time.perf_counter()
    # Audit all base witnesses and supports before consuming their lower bounds.
    base_audit=recheck.audit_folder(folder)
    def forbidden(*args,**kwargs):raise AssertionError('optimizer called during closure audit')
    global envelope
    envelope=coupled.envelope=audit.envelope=gc.envelope=forbidden
    dataset=json.loads((folder/'restart_closure.json').read_text())
    records=[];mutations=[];start=time.perf_counter()
    for rec in dataset['outcomes']:
        data=gzip.decompress((folder/'closures'/rec['file']).read_bytes())
        require(hashlib.sha256(data).hexdigest()==rec['sha256'],'changed closure bytes')
        obj=json.loads(data)
        base=load(folder/'certificates'/rec['base_file'])
        require(hash_obj(base)==rec['base_sha256'],'changed summary bytes')
        cstart=time.perf_counter();res=check_closure(obj,base)
        for k,v in res.items():require(rec[k]==v,'changed closure metric '+k)
        records.append({'file':rec['file'],'sha256':rec['sha256'],'seconds':time.perf_counter()-cstart,'passed':True})
        if not mutations:mutations=reject_mutations(obj,base)
    require(len(records)==42 and not dataset['failures'],'incomplete independent cohort')
    result={'passed':True,'optimizer_disabled':True,'base_certificates':base_audit['total_certificates'],
            'closure_certificates':42,'total_certificates':base_audit['total_certificates']+42,
            'closure_only_seconds':time.perf_counter()-start,'whole_seconds':time.perf_counter()-tic,
            'mutation_rejections':mutations,'records':records}
    (folder/'restart_independent_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True))
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('folder',type=Path);ap.add_argument('--audit',action='store_true');ap.add_argument('--test',action='store_true');args=ap.parse_args()
    if args.test:
        result=exhaustive_tests();(args.folder/'restart_tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
    elif args.audit:
        result=independent(args.folder);print(json.dumps({k:v for k,v in result.items() if k!='records'}))
    else:run(args.folder)
