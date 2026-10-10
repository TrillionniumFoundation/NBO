"""Publication replay of the entire frozen R69 catalogue, with explicit scope."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import hashlib,json,math,sys,time
import numpy as np
import inspect70 as inspect
import independent70 as independent
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-11-r69'
sys.path.insert(0,str(OLD/'code'))
import science69 as science
import readout69 as readout
import independent69 as midpoint

def load(p):return json.loads(p.read_text())
def arrays(p):
    with np.load(p) as z:return {key:z[key].copy() for key in z.files}
def save(name,j):inspect.save(name,j)
def array_digest(a):
    h=hashlib.sha256()
    for key,v in sorted(a.items()):h.update(key.encode());h.update(str(v.dtype).encode());h.update(str(v.shape).encode());h.update(v.tobytes())
    return h.hexdigest()
def need(ok,label):
    if not ok:raise AssertionError(label)

def main():
    start=time.perf_counter();inspect.main();catalogue=load(R/'audit/CATALOGUE70.json');summary=load(R/'audit/SUMMARY70.json')
    traces={};path_records=[];contrasts=[];training=[];validation=[];training_identity={};model_identity=[];cert_cache={};warnings=[]
    def path(file,spec,randomfile=None):
        tr=arrays(file);rr=arrays(randomfile) if randomfile else {k:v for k,v in tr.items() if k.endswith('_index')}
        identity=array_digest({**rr,**tr})+str(spec['T'])+str(spec['group']=='vector')
        if identity not in traces:
            point=midpoint.audit_paths(rr,tr,spec['T'],spec['group']=='vector')
            full=independent.path_bins(rr,tr,spec['T'],spec['group']=='vector')
            traces[identity]=dict(point=point,full=full)
        path_records.append(dict(file=str(file.relative_to(OLD)),payload_digest=identity,**traces[identity]))
        return tr
    for row in catalogue['rows']:
        spec=row['spec'];folder=OLD/'results69'/spec['key'];j=load(folder/'summary.json')
        need(row['returned'] and j['status']=='returned',('Retained nonreturn',spec['key']))
        group=spec['group'];models=load(folder/'model.json') if (folder/'model.json').exists() else {}
        if group=='reuse':models=models['models']
        fit=j.get('training',{});raw=arrays(folder/'training.npz') if (folder/'training.npz').exists() else {}
        if group in ('comparison','validation','reuse') and spec['kind'] in readout.LEARNED:
            identity=(spec['d'],spec['T'],spec['seed']);digest=array_digest(raw)
            if identity in training_identity:need(training_identity[identity]==digest,('Unequal purchased information',spec['key']))
            training_identity[identity]=digest
            for report in fit['dates']:
                r=report['r'];certificate=report.get('exact_certificate')
                if not report['optimizer']['success']:warnings.append(dict(key=spec['key'],date=r,message=report['optimizer']['message']))
                if certificate is not None:
                    cachekey=(digest,spec['kind'],r,json.dumps(models[str(r)],sort_keys=True))
                    if cachekey not in cert_cache:
                        c={key[len(f'r{r}_'):]:v for key,v in raw.items() if key.startswith(f'r{r}_')}
                        G,_=readout.q.regularity(r-1,spec['d']);lam=F(13,16)+readout.B*G*F(3*spec['d'],8)
                        c.update(tol=report['tolerance'],K=report['recovery_root_cap'],allowance=readout.q.up(lam*(F(1,2**32)+F(1,2**36))))
                        cert_cache[cachekey]=readout.exact_certificate(c,spec['kind'],models[str(r)]['weights'],report['margin'],report['penalty'])
                    got=cert_cache[cachekey]
                    for name in ('value_exact','dual_gap_exact','feature_partition_verified','coefficient_count'):need(got[name]==certificate[name],('Readout certificate',spec['key'],r,name))
                    need(F(got['dual_gap_exact'])>=0,'Negative convex dual gap')
                    training.append(dict(key=spec['key'],d=spec['d'],T=spec['T'],kind=spec['kind'],seed=spec['seed'],r=r,**got))
        if group=='comparison' or group=='vector':path(folder/'trace.npz',spec)
        if group=='reuse':
            for block in j['blocks']:path(folder/f"block{block['block']:02d}.npz",spec)
        if group=='validation':
            a=arrays(folder/'validation.npz')
            for report in j['validation']:
                prefix=f"r{report['r']}_";v={key[len(prefix):]:value for key,value in a.items() if key.startswith(prefix)}
                tol=next(z['tolerance'] for z in fit['dates'] if z['r']==report['r'])
                proposed=readout.prediction(spec['kind'],models,v['x'],report['r'],v['cap'])
                from validation70 import verify as verify_validation
                differences=verify_validation(v,proposed,models,report['r'],spec['kind'],readout,tol)
                if differences:warnings.append(dict(key=spec['key'],date=report['r'],prediction_replay_differences=differences))
                need(np.array_equal(v['additional_root_queries'],report['K']*(v['score']>tol)),('Executed recovery count',spec['key']))
                need(np.all(v['additional_root_queries']<=report['K']*v['loss']) and np.all(v['gap']<=tol),('Work loss/gap',spec['key']))
                exactmean=sum((F(float(z)) for z in v['loss']),F(0))/len(v['loss'])
                # The printed floating validation bound is descriptive. Compute
                # a fresh outward exact-sum bound for publication.
                from decimal import Decimal,localcontext
                with localcontext() as ctx:
                    ctx.prec=80;rad=(Decimal(12)/Decimal(2*len(v['loss']))).sqrt()+Decimal('1e-70')
                    m=Decimal(exactmean.numerator)/Decimal(exactmean.denominator)
                    upper=min(Decimal(report['K']),Decimal(report['K'])*(m+rad))
                    numeric=float(upper)
                    if Decimal.from_float(numeric)<upper:numeric=float(np.nextafter(numeric,np.inf))
                validation.append(dict(key=spec['key'],d=spec['d'],T=spec['T'],kind=spec['kind'],seed=spec['seed'],r=report['r'],rows=len(v['loss']),screen_returns=int(np.sum(v['score']<=tol)),loss_mean=float(exactmean),mean_root_queries=float(v['additional_root_queries'].mean()),root_cap=report['K'],validated_root_upper=numeric,descendant_queries=report['recovery_work']['q_queries'],endpoint_queries=report['endpoint_work']['q_queries']))
        if group=='inference':
            pp={kind:path(folder/(kind+'-paths.npz'),spec,folder/'randoms.npz') for kind in j['arms']}
            for name,rec in j['centered'].items():
                a,b=name.split('-minus-');Gs=[F(j['arms'][kind]['accounts'][0]['center_upper_exact']) for kind in (a,b)]
                result=independent.centered_interval((pp[a]['center_lo'],pp[a]['center_hi']),(pp[b]['center_lo'],pp[b]['center_hi']),rec,*Gs)
                need(rec['rows']==1024 and rec['margin_exact']=='1/256','Changed inference design')
                lo,hi=rec['interval'];margin=F(1,256)
                need(rec['equivalent_at_margin']==(F(lo)>=-margin and F(hi)<=margin),'Equivalence predicate')
                contrasts.append(dict(task=[spec['d'],spec['T']],contrast=name,interval=rec['interval'],equivalence=rec['equivalent_at_margin'],**result))
            for kind in ('hat-relu','bernstein4'):
                fitted=load(folder/(kind+'-model.json'))
                for group2 in ('comparison','reuse'):
                    for rep in range(4):
                        name=f"{group2}-d{spec['d']}-T{spec['T']}-{kind}-s6901-r{rep}"
                        other=load(OLD/'results69'/name/'model.json')
                        if group2=='reuse':other=other['models']
                        need(other==fitted,('Cost/work policy identity',name))
                        model_identity.append(dict(inference=spec['key'],service=name,status='model_arrays_identical; runtime-contract equality is additionally required for deployment transfer'))
    record=dict(status='passed',source_commit=catalogue['source_commit'],source_freeze_sha256=catalogue['freeze_sha256'],service_count=len(catalogue['rows']),files_hash_checked=catalogue['files_checked'],
        physical_path_archives=len(path_records),unique_path_payloads=len(traces),
        archived_path_rows=sum(x['full']['rows'] for x in path_records),independently_evaluated_unique_rows=sum(x['full']['rows'] for x in traces.values()),
        unique_full_bin_rows=sum(x['full']['full_bin_rows'] for x in traces.values()),unique_ambiguous_rows=sum(x['full']['ambiguous_rows'] for x in traces.values()),
        readout_certificates_replayed=len(training),unique_rational_certificates=len(cert_cache),validation_date_records=len(validation),validation_contexts=sum(x['rows'] for x in validation),
        centered_contrasts=len(contrasts),equivalent_contrasts=sum(x['equivalence'] for x in contrasts),matched_policy_identities=len(model_identity),warnings=warnings,seconds=time.perf_counter()-start,
        new_scientific_services=0,new_independent_inference_rows=0,
        scope='All frozen R69 receipts and stored files; independently coded exact full-bin cash-path intervals on unique unambiguous payloads; independent exact midpoint checks; exact centered interval summation; achieved convex readout certificates and independent-context loss replay. This is not independent regeneration of optimal Bellman advantages or full large vector descendant trees.')
    save('RESULT_AUDIT70.json',record);save('DETAILS70.json',dict(paths=path_records,training=training,validation=validation,contrasts=contrasts,model_identity=model_identity))
    print(json.dumps(record,indent=2))
if __name__=='__main__':
    try:main()
    except Exception:
        import traceback
        save('DISAGREEMENT70.json',dict(status='failed',traceback=traceback.format_exc(),scope='Do not infer a scientific enclosure error until the independent extension and its comparison relation have been checked.'))
        raise
