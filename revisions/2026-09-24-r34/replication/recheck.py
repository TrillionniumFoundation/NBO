"""Read-only certificate audit: forbid calls to the optimizing envelope.
Run after the complete study. Recompute every economic scalar from rationals.
"""
from pathlib import Path
import argparse, copy, gzip, hashlib, json, time
import coupled, audit, global_cost as gc
from global_cost import F, PW, ZERO, ONE, BETA, linear_comb, evaluate


def forbidden(*args, **kwargs):
    raise AssertionError('optimizer called by independent checker')


def reject_mutations(cert, supports):
    rejected=[]
    def reject(name, mutate):
        bad=copy.deepcopy(cert); mutate(bad)
        try: gc.check_summary(bad,supports)
        except (ValueError,AssertionError,KeyError,IndexError): rejected.append(name);return
        raise AssertionError('invalid summary accepted: '+name)
    reject('lower_point_inflated',lambda x:x['cost_lower'][0]['points'].__setitem__(0,'9999'))
    reject('false_integrated_gap',lambda x:x.__setitem__('integrated_cost_gap','-1'))
    reject('support_hash_changed',lambda x:x['support_sha256'].__setitem__(0,'0'*64))
    reject('missing_summary_date',lambda x:x['C'].pop())
    reject('missing_interval',lambda x:x['policy'][0]['affine'].pop())
    reject('false_feasibility_upper',lambda x:x['feasibility_U'][0]['points'].__setitem__(0,'-999'))
    reject('nonintegral_lower_selector',lambda x:x['lower_selector'][0]['points'].__setitem__(0,'1/2'))
    reject('wrong_terminal_cost',lambda x:x['C'][-1]['points'].__setitem__(0,'1'))
    return rejected


def audit_folder(folder:Path):
    # These bindings cover every module through which a shared optimizer could
    # otherwise be called. Exact affine composition and comparisons remain.
    coupled.envelope=audit.envelope=gc.envelope=forbidden
    start=time.perf_counter();records=[];n_support=n_summary=n_class=0;mutations=[]
    def checked_load(meta):
        f=folder/'certificates'/meta['file'];raw=gzip.decompress(f.read_bytes())
        gc.require(hashlib.sha256(raw).hexdigest()==meta['sha256'],'changed serialized certificate')
        return json.loads(raw)
    for T in (4,8,12):
        d=json.loads((folder/f'H{T}.json').read_text())
        gc.require(not d['failures'] and len(d['supports'])==56 and len(d['outcomes'])==14,'incomplete study')
        cache={}
        for item in d['supports']:
            obj=checked_load(item);tic=time.perf_counter();res=gc.check_support(obj)
            gc.require(res['regret_upper']==item['regret_upper'],'support metric mismatch')
            p=PW.load(obj['C'][0]);gc.require(str(p.integral())==item['intervention_cost'],'support cost mismatch')
            cache[(item['proposal'],F(item['multiplier']))]=obj
            records.append({'file':item['file'],'sha256':item['sha256'],'seconds':time.perf_counter()-tic,'kind':'support'})
            n_support+=1
        for item in d['outcomes']:
            base=checked_load(item['fresh_class_baseline']);tic=time.perf_counter();audit.check(base)
            records.append({'file':item['fresh_class_baseline']['file'],'sha256':item['fresh_class_baseline']['sha256'],'seconds':time.perf_counter()-tic,'kind':'class_baseline'})
            n_class+=1
            obj=checked_load(item);supports=[cache[(item['proposal'],p)] for p in gc.PRICES]
            tic=time.perf_counter();gc.check_summary(obj,supports)
            J=[PW.load(v) for v in obj['J']];C=[PW.load(v) for v in obj['C']];B=[PW.load(v) for v in obj['cost_lower']]
            FU=[PW.load(v) for v in obj['feasibility_U']];raw=[PW.load(v) for v in obj['raw']]
            rawJ=evaluate(raw);baseC=PW.load(base['D'][0]).integral()
            checks={'cost_upper':C[0].integral(),'global_cost_lower':B[0].integral(),
                    'global_cost_gap':C[0].integral()-B[0].integral(),'class_cost':baseC,
                    'saving_vs_class':baseC-C[0].integral(),'operating_value':J[0].integral(),
                    'all_restart_regret_upper':max(linear_comb([u,j],[ONE,-ONE]).extent()[1] for u,j in zip(FU,J)),
                    'preservation_margin':min(linear_comb([j,v],[ONE,-ONE]).extent()[0] for j,v in zip(J,rawJ))}
            for k,v in checks.items():gc.require(F(item[k])==v,'summary metric mismatch: '+k)
            gc.require(bool(item['preservation_certified'])==(checks['preservation_margin']>=0),'preservation flag mismatch')
            records.append({'file':item['file'],'sha256':item['sha256'],'seconds':time.perf_counter()-tic,'kind':'primal_dual'})
            n_summary+=1
            if not mutations:mutations=reject_mutations(obj,supports)
    gc.require((n_support,n_summary,n_class)==(168,42,42),'wrong declared counts')
    # A constructive sufficient price, independent of the observed proposals.
    sufficient=[]
    for T in (4,8,12):
        H=sum((BETA**i for i in range(T)),ZERO)
        upper=F(1,40000)+2*H/F(4096)
        gc.require(upper<F(1,100),'predeclared largest multiplier not sufficiently large')
        sufficient.append({'T':T,'regret_bound':str(upper),'below_1_100':True})
    result={'passed':True,'support_count':n_support,'primal_dual_count':n_summary,'fresh_class_count':n_class,
            'total_certificates':len(records),'optimizer_disabled':True,'summary_mutations_rejected':mutations,
            'sufficient_price_bounds':sufficient,'whole_audit_seconds':time.perf_counter()-start,'records':records}
    (folder/'independent_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True))
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('folder',type=Path);args=ap.parse_args()
    out=audit_folder(args.folder)
    print(json.dumps({k:v for k,v in out.items() if k!='records'},indent=2))
