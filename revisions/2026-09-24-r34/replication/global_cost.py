"""Class-free primal/dual certificates for an all-restart regret constraint.
Exact arithmetic; no optimal-value input is used by the support constructor.
The independent checker does not call the maximizing envelope routine.
"""
from coupled import *
from audit import require, pointwise_equal, pointwise_leq, check as check_class
import gzip, copy, resource

PRICES = tuple(map(F, (0, 1, 4, 16, 64, 256, 1024, 4096)))
BUDGETS = (F(1, 100), F(1, 20))
WITNESS_ACCURACY = F(1, 10000)
NAMES = ('defer','occupancy_stress','spline33','spline129','neural31001','neural31002','neural31003')


def encoded(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def save(obj, file):
    data=encoded(obj)
    with gzip.GzipFile(filename=str(file),mode='wb',mtime=0) as out: out.write(data)
    return {'file':str(file.name),'sha256':hashlib.sha256(data).hexdigest(),'uncompressed_bytes':len(data),'compressed_bytes':file.stat().st_size}


def load(file):
    return json.loads(gzip.decompress(file.read_bytes()))


def valid_policy(policy, T):
    require(len(policy)==T,'wrong policy horizon')
    for f in policy:
        require(all(a==0 and b in (0,1,2) for a,b in f.ab) and all(y in (0,1,2) for y in f.ys),'infeasible action')


def support_q(next_value, raw, lam):
    cont=q_functions(next_value, operating=False)
    return [linear_comb([v,intervention(raw,a)],[ONE,-ONE],lam,-lam*COSTS[a]) for a,v in enumerate(cont)]


def build_inputs(T):
    tic=time.perf_counter(); U,q,log=witnesses(T,WITNESS_ACCURACY)
    gamma=[envelope(row)[1] for row in q]
    defects=[linear_comb([u,select(row,p)],[ONE,-ONE]).extent()[1] for u,row,p in zip(U,q,gamma)]
    b=[ZERO]*(T+1)
    for t in reversed(range(T)): b[t]=defects[t]+BETA*b[t+1]
    L=[linear_comb([u],[ONE],b=-err) for u,err in zip(U,b)]
    log['total_constructive_input_seconds']=time.perf_counter()-tic
    log['defects']=list(map(str,defects)); log['propagated_error']=list(map(str,b))
    return U,gamma,defects,L,log


def check_inputs(U,gamma,defects):
    T=len(gamma); require(len(U)==T+1 and len(defects)==T,'missing witness date')
    valid_policy(gamma,T); pointwise_equal(U[-1],affine(F(1,2)))
    b=[ZERO]*(T+1)
    for t in reversed(range(T)):
        require(defects[t]>=0,'negative defect')
        qs=q_functions(U[t+1])
        for q in qs: pointwise_leq(q,U[t])
        require(linear_comb([U[t],select(qs,gamma[t])],[ONE,-ONE]).extent()[1]<=defects[t],'false compression defect')
        b[t]=defects[t]+BETA*b[t+1]
    return [linear_comb([u],[ONE],b=-err) for u,err in zip(U,b)]


def check_support(cert):
    require(cert.get('model')==model(),'wrong model')
    lam=F(cert['multiplier']); require(lam>=0,'negative multiplier')
    U=[PW.load(d) for d in cert['U']]; gamma=[PW.load(d) for d in cert['gamma']]
    defects=list(map(F,cert['defects'])); check_inputs(U,gamma,defects)
    raw=[PW.load(d) for d in cert['raw']]; policy=[PW.load(d) for d in cert['policy']]
    W=[PW.load(d) for d in cert['W']]; J=[PW.load(d) for d in cert['J']]; C=[PW.load(d) for d in cert['C']]
    T=len(raw); valid_policy(raw,T); valid_policy(policy,T)
    require(T>0 and len(gamma)==T and len(W)==len(J)==len(C)==T+1,'wrong support dimensions')
    pointwise_equal(W[T],affine(lam/2)); pointwise_equal(J[T],affine(F(1,2))); pointwise_equal(C[T],affine())
    for t in reversed(range(T)):
        qs=support_q(W[t+1],raw[t],lam)
        for qa in qs: pointwise_leq(qa,W[t])
        pointwise_equal(W[t],select(qs,policy[t]))
        pointwise_equal(J[t],select(q_functions(J[t+1]),policy[t]))
        cq=[linear_comb([v,intervention(raw[t],a)],[ONE,ONE]) for a,v in enumerate(q_functions(C[t+1],operating=False))]
        pointwise_equal(C[t],select(cq,policy[t]))
        pointwise_equal(W[t],linear_comb([J[t],C[t]],[lam,-ONE]))
    return {'certified':True,'support_optimality':'unrestricted, all states and restart dates','regret_upper':str(max(linear_comb([u,j],[ONE,-ONE]).extent()[1] for u,j in zip(U,J)))}


def solve_support(U,gamma,defects,raw,lam):
    T=len(raw); tic=time.perf_counter()
    W=[None]*(T+1); p=[None]*T; W[T]=affine(lam/2)
    for t in reversed(range(T)): W[t],p[t]=envelope(support_q(W[t+1],raw[t],lam))
    solve_seconds=time.perf_counter()-tic; tic=time.perf_counter()
    J=evaluate(p); C=evaluate(p,raw); evaluation_seconds=time.perf_counter()-tic
    cert={'model':model(),'multiplier':str(lam),'U':[u.dump() for u in U],'gamma':[x.dump() for x in gamma],'defects':list(map(str,defects)),
          'raw':[x.dump() for x in raw],'policy':[x.dump() for x in p],'W':[x.dump() for x in W],'J':[x.dump() for x in J],'C':[x.dump() for x in C]}
    tic=time.perf_counter(); check=check_support(cert); check_seconds=time.perf_counter()-tic
    record={**check,'multiplier':str(lam),'solve_seconds':solve_seconds,'evaluation_seconds':evaluation_seconds,'check_seconds':check_seconds,
            'operating_value':str(J[0].integral()),'intervention_cost':str(C[0].integral()),'max_support_pieces':max(len(w.ab) for w in W),
            'max_value_pieces':max(len(w.ab) for w in J+C),'max_bits':max(w.bits() for w in U+W+J+C)}
    return cert,record


def lower_envelope(L,supports,eps):
    bounds=[]; selectors=[]
    for t in range(len(L)):
        terms=[affine()]+[linear_comb([L[t],PW.load(c['W'][t])],[F(c['multiplier']),-ONE],b=-F(c['multiplier'])*eps) for c in supports]
        bound,selector=envelope(terms); bounds.append(bound); selectors.append(selector)
    return bounds,selectors


def check_summary(cert,supports):
    require(cert.get('model')==model(),'wrong summary model')
    eps=F(cert['epsilon']); require(eps>0,'bad tolerance')
    U=[PW.load(x) for x in cert['U']]; gamma=[PW.load(x) for x in cert['gamma']]
    L=check_inputs(U,gamma,list(map(F,cert['defects'])))
    p=[PW.load(x) for x in cert['policy']]; raw=[PW.load(x) for x in cert['raw']]
    J=[PW.load(x) for x in cert['J']]; C=[PW.load(x) for x in cert['C']]
    FU=[PW.load(x) for x in cert['feasibility_U']]
    B=[PW.load(x) for x in cert['cost_lower']]; idx=[PW.load(x) for x in cert['lower_selector']]
    T=len(raw); valid_policy(raw,T);valid_policy(p,T)
    require(len(FU)==len(J)==len(C)==len(B)==len(idx)==T+1,'missing summary date')
    require(len(supports)==len(PRICES),'incomplete multiplier set')
    for i,s in enumerate(supports):
        require(s['model']==cert['model'] and s['raw']==cert['raw'] and s['U']==cert['U'] and s['defects']==cert['defects'] and s['gamma']==cert['gamma'],'mismatched support')
        require(F(s['multiplier'])==PRICES[i],'changed multiplier order')
        require(hashlib.sha256(encoded(s)).hexdigest()==cert['support_sha256'][i],'changed support bytes')
    pointwise_equal(FU[T],affine(F(1,2)));pointwise_equal(J[T],affine(F(1,2)));pointwise_equal(C[T],affine())
    for t in reversed(range(T)):
        for q in q_functions(FU[t+1]): pointwise_leq(q,FU[t])
        pointwise_equal(J[t],select(q_functions(J[t+1]),p[t]))
        require(linear_comb([FU[t],J[t]],[ONE,-ONE]).extent()[1]<=eps,'infeasible primal policy')
        cq=[linear_comb([v,intervention(raw[t],a)],[ONE,ONE]) for a,v in enumerate(q_functions(C[t+1],operating=False))]
        pointwise_equal(C[t],select(cq,p[t]))
    for t in range(T+1):
        terms=[affine()]+[linear_comb([L[t],PW.load(s['W'][t])],[F(s['multiplier']),-ONE],b=-F(s['multiplier'])*eps) for s in supports]
        require(all(a==0 and b.denominator==1 and 0<=b<len(terms) for a,b in idx[t].ab) and all(v.denominator==1 and 0<=v<len(terms) for v in idx[t].ys),'invalid lower selector')
        for term in terms: pointwise_leq(term,B[t])
        pointwise_equal(B[t],select(terms,idx[t]))
        pointwise_leq(B[t],C[t])
    require(F(cert['integrated_cost_gap'])==C[0].integral()-B[0].integral(),'wrong reported primal-dual gap')
    return {'certified':True,'global_lower_scope':'all all-restart-regret-feasible policies, not just local class','gap':cert['integrated_cost_gap']}


def tests():
    U,g,d,L,log=build_inputs(2); raw=stress_policy(2); cert,rec=solve_support(U,g,d,raw,F(4)); check_support(cert)
    rejected=[]
    def reject(name,mutate):
        bad=copy.deepcopy(cert);mutate(bad)
        try: check_support(bad)
        except (ValueError,AssertionError,KeyError,IndexError): rejected.append(name);return
        raise AssertionError('invalid certificate accepted: '+name)
    reject('model',lambda x:x['model'].__setitem__('beta','1'))
    reject('negative_multiplier',lambda x:x.__setitem__('multiplier','-1'))
    reject('missing_date',lambda x:x['W'].pop())
    reject('isolated_support_point',lambda x:x['W'][0]['points'].__setitem__(0,'-1000'))
    reject('false_cost_point',lambda x:x['C'][0]['points'].__setitem__(0,'1000'))
    reject('false_compression_defect',lambda x:x['defects'].__setitem__(0,'-1'))
    reject('infeasible_action',lambda x:x['policy'][0]['points'].__setitem__(0,'5'))
    reject('wrong_terminal',lambda x:x['W'][-1]['points'].__setitem__(0,'1'))
    from itertools import product
    W=[PW.load(x) for x in cert['W']]; lam=F(4); checks=0
    for x in (ZERO,F(1,3),F(1,2),ONE):
        vals=[]
        for a in range(3):
            ys=[m*x+b for m,b in MAPS[a]]
            for suffix in product(range(3),repeat=2):
                val=lam*(x-COSTS[a])-(1+x)*(a!=raw[0].at(x))
                for prob,y,b in zip(PROBS,ys,suffix):
                    val+=BETA*prob*(lam*(y-COSTS[b])-(1+y)*(b!=raw[1].at(y))+BETA*lam*sum((p*(m*y+c)/2 for p,(m,c) in zip(PROBS,MAPS[b])),ZERO))
                vals.append(val)
        require(max(vals)==W[0].at(x),'exhaustive support-tree mismatch');checks+=1
    return {'passed':True,'mutation_rejections':rejected,'exhaustive_support_tree_checks':checks}


def run(source:Path,out:Path,T:int):
    out.mkdir(parents=True,exist_ok=True);(out/'certificates').mkdir(exist_ok=True)
    U,gamma,defects,L,wlog=build_inputs(T)
    # Independent exact operating comparator; not an input to build_inputs or solve_support.
    V,opt,exact_log=exact_dp(T)
    report={'horizon':T,'model':model(),'multipliers':list(map(str,PRICES)),'witness_parameter':str(WITNESS_ACCURACY),'witness':wlog,
            'exact_operating_control':exact_log,'python':sys.version,'platform':platform.platform(),
            'timing_scope':'installed-proposal R34 computation; inherited fitting is reported separately and not rerun',
            'source_files':[],'supports':[],'outcomes':[],'failures':[]}
    for name in NAMES:
        fp=source/'proposals'/f'H{T}_{name}.json';frozen=json.loads(fp.read_text());raw=[PW.load(p) for p in frozen['compiled']]
        report['source_files'].append({'path':str(fp),'sha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'inherited_proposal_stats':frozen['stats']})
        supports=[];records=[]
        for lam in PRICES:
            try:
                cert,rec=solve_support(U,gamma,defects,raw,lam)
                rec['proposal']=name;rec['reference_true_regret']=str(max(linear_comb([v,PW.load(j)],[ONE,-ONE]).extent()[1] for v,j in zip(V,cert['J'])))
                tic=time.perf_counter();storage=save(cert,out/'certificates'/f'H{T}_{name}_lambda{lam}.json.gz');rec['encoding_seconds']=time.perf_counter()-tic
                rec.update(storage);records.append(rec);supports.append(cert);report['supports'].append(rec)
                print('SUPPORT',T,name,lam,'regret',float(F(rec['regret_upper'])),'cost',float(F(rec['intervention_cost'])),flush=True)
            except Exception as exc:
                report['failures'].append({'proposal':name,'multiplier':str(lam),'error':repr(exc)});print('UNRESOLVED SUPPORT',T,name,lam,repr(exc),flush=True)
            (out/f'H{T}.json').write_text(json.dumps(report,indent=2,sort_keys=True))
        if len(supports)!=len(PRICES): continue
        for eps in BUDGETS:
            try:
                start=time.perf_counter();cf=source/'certificates'/f'H{T}_{name}_e{eps.numerator}_{eps.denominator}.json.gz'
                old=load(cf);check_class(old)
                # Reconstruct the classical comparator from primitives on this
                # machine. Its entire construction is charged, not a free input.
                ctic=time.perf_counter()
                cU,cq,cwl=witnesses(T,eps)
                cal=admissible(cU,cq,F(cwl['eta']))
                cp,cD=repair(raw,cal);cJ=evaluate(cp);cC=evaluate(cp,raw)
                fresh_class={'model':model(),'epsilon':str(eps),'U':[u.dump() for u in cU],'raw':[p.dump() for p in raw],
                             'policy':[p.dump() for p in cp],'D':[d.dump() for d in cD],'J':[j.dump() for j in cJ]}
                check_class(fresh_class)
                require(fresh_class==old,'reconstructed class differs from frozen inherited certificate')
                class_storage=save(fresh_class,out/'certificates'/f'H{T}_{name}_epsilon{eps.numerator}_{eps.denominator}_class_baseline.json.gz')
                class_seconds=time.perf_counter()-ctic
                candidates=[]
                for s,r in zip(supports,records):
                    if F(r['regret_upper'])<=eps:
                        candidates.append((F(r['intervention_cost']),str(s['multiplier']),s['policy'],s['J'],s['C'],s['U']))
                # Retained class-optimal candidate is independently re-evaluated.
                candidates.append((cC[0].integral(),'inherited_class',old['policy'],[j.dump() for j in cJ],[c.dump() for c in cC],old['U']))
                best=min(candidates,key=lambda row:(row[0],row[1]));B,idx=lower_envelope(L,supports,eps)
                J=[PW.load(j) for j in best[3]];C=[PW.load(c) for c in best[4]]
                rawJ=evaluate(raw);pres=min(linear_comb([j,r],[ONE,-ONE]).extent()[0] for j,r in zip(J,rawJ))
                gap=best[0]-B[0].integral();class_saving=cC[0].integral()-best[0]
                result={'model':model(),'epsilon':str(eps),'proposal':name,'T':T,'U':[u.dump() for u in U],'gamma':[g.dump() for g in gamma],
                        'defects':list(map(str,defects)),'raw':[p.dump() for p in raw],'policy':best[2],'J':best[3],'C':best[4],'feasibility_U':best[5],
                        'cost_lower':[b.dump() for b in B],'lower_selector':[i.dump() for i in idx],'selected':best[1],
                        'support_sha256':[hashlib.sha256(encoded(s)).hexdigest() for s in supports],'integrated_cost_gap':str(gap)}
                assembly_seconds=time.perf_counter()-start;tic=time.perf_counter();checked=check_summary(result,supports);checking_seconds=time.perf_counter()-tic
                tic=time.perf_counter();storage=save(result,out/'certificates'/f'H{T}_{name}_epsilon{eps.numerator}_{eps.denominator}_primal_dual.json.gz');encoding_seconds=time.perf_counter()-tic
                r={'T':T,'proposal':name,'epsilon':str(eps),'selected':best[1],'feasible_price_count':len(candidates)-1,
                   'global_cost_lower':str(B[0].integral()),'cost_upper':str(best[0]),'global_cost_gap':str(gap),'operating_value':str(J[0].integral()),
                   'all_restart_regret_upper':str(max(linear_comb([PW.load(u),j],[ONE,-ONE]).extent()[1] for u,j in zip(best[5],J))),
                   'all_restart_cost_gap_upper':str(max(linear_comb([c,b],[ONE,-ONE]).extent()[1] for c,b in zip(C,B))),
                   'class_cost':str(cC[0].integral()),'saving_vs_class':str(class_saving),'preservation_margin':str(pres),'preservation_certified':pres>=0,
                   'fresh_class_baseline_seconds':class_seconds,'fresh_class_baseline':class_storage,
                   'class_candidate_recheck_and_bound_construction_seconds':assembly_seconds,'summary_check_seconds':checking_seconds,'summary_encoding_seconds':encoding_seconds,
                   'all_support_construction_seconds':sum(s['solve_seconds']+s['evaluation_seconds']+s['encoding_seconds'] for s in records),
                   'all_support_checker_seconds':sum(s['check_seconds'] for s in records),
                   'witness_construction_seconds':wlog['total_constructive_input_seconds'],'certified':checked['certified'],**storage}
                r['total_installed_seconds_including_fresh_class_construction']=sum(r[k] for k in ['class_candidate_recheck_and_bound_construction_seconds','summary_check_seconds','summary_encoding_seconds','all_support_construction_seconds','all_support_checker_seconds','witness_construction_seconds'])
                report['outcomes'].append(r)
                print('SUMMARY',T,name,eps,'cost',float(best[0]),'lower',float(B[0].integral()),'gap',float(gap),'saved',float(class_saving),'selected',best[1],flush=True)
            except Exception as exc:
                report['failures'].append({'proposal':name,'epsilon':str(eps),'error':repr(exc)});print('UNRESOLVED SUMMARY',T,name,eps,repr(exc),flush=True)
            report['peak_process_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            (out/f'H{T}.json').write_text(json.dumps(report,indent=2,sort_keys=True))
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path);ap.add_argument('--out',type=Path);ap.add_argument('--horizon',type=int,choices=[4,8,12]);ap.add_argument('--test',action='store_true');args=ap.parse_args()
    if args.test:
        r=tests();print(json.dumps(r,indent=2))
        if args.out:args.out.mkdir(exist_ok=True,parents=True);(args.out/'tests.json').write_text(json.dumps(r,indent=2))
    if args.horizon:
        require(args.source is not None and args.out is not None,'--source and --out required')
        run(args.source,args.out,args.horizon)
