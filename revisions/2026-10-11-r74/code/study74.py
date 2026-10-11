"""Prospective frozen-controller study; inference uses independent integer outputs."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,os,platform,sys,time
import numpy as np
import common74 as c
import float74 as p
import integer74 as q
R=Path(__file__).resolve().parents[1]

def freeze_check():
    freeze=json.loads((R/'SOURCE_FREEZE74.json').read_text())
    for name,h in freeze['files'].items():
        if c.sha(R/name)!=h:raise AssertionError('Changed prospective source: '+name)
    for name,h in freeze['controller_sources'].items():
        if c.sha(R/name)!=h:raise AssertionError('Changed frozen controller: '+name)
    return freeze

def infer(policies,low,high,supports):
    result={};absolute={};H=int(c.H*c.SCALE)
    for k,policy in enumerate(policies):
        absolute[policy['name']]=c.endpoint_interval(np.maximum(low[k],0),np.minimum(high[k],H),F(0),c.H)
    for z,(a,b) in enumerate(c.PAIRS):
        K=F(supports[z]['bound']);bound=int(K*c.SCALE)
        if K*c.SCALE!=bound:raise AssertionError('Support cannot be represented exactly')
        if supports[z]['identity']:
            assert c.identical(policies[a],policies[b])
            lo=np.zeros(c.N,dtype=np.int64);hi=lo.copy()
        else:
            lo=np.maximum(low[a]-high[b],-bound);hi=np.minimum(high[a]-low[b],bound)
        result[policies[a]['name']+'-minus-'+policies[b]['name']]=c.endpoint_interval(lo,hi,-K,K,supports[z]['identity'])
    return dict(absolute_costs=absolute,contrasts=result,family_error='1/100',family_estimands=13,one_sided_log_upper=9,target_width='1/256',equivalence_margin='1/256')

def main(replay=False):
    start=time.perf_counter();freeze=freeze_check();policies=c.actors();out=R/'results74';out.mkdir(exist_ok=True)
    if replay:
        record=json.loads((out/'study.json').read_text())
        for name,h in record['file_sha256'].items():
            if c.sha(out/name)!=h:raise AssertionError('Changed scientific record: '+name)
        arrays=np.load(out/'integer-endpoints.npz');low=arrays['lower'];high=arrays['upper']
        summary=infer(policies,low,high,record['supports'])
        if c.encode(summary)!=record['inference']:raise AssertionError('Exact inference replay disagreement')
        c.save(R/'audit/REPLAY74.json',dict(status='passed',new_observations=0,integer_policy_paths=5*c.N,inference_recomputed=True,scientific_files_checked=record['file_sha256'],seconds=time.perf_counter()-start))
        print('R74 exact inference and complete file replay passed',flush=True);return
    if (out/'study.json').exists():raise RuntimeError('Refusing to overwrite the prospective execution')
    c.save(out/'started.json',dict(design_commit=freeze['design_commit'],source_freeze_sha256=c.sha(R/'SOURCE_FREEZE74.json'),started_unix=time.time(),python=platform.python_version(),numpy=np.__version__,machine=platform.machine(),affinity=sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None))
    begin=time.perf_counter();supports=[c.support(policies[a],policies[b]) for a,b in c.PAIRS];support_seconds=time.perf_counter()-begin
    begin=time.perf_counter()
    for row,(a,b) in zip(supports,c.PAIRS):
        assert q.independent_support(policies[a],policies[b])==row['bound']
    support_audit_seconds=time.perf_counter()-begin
    c.save(out/'supports-before-sampling.json',supports)
    rng=np.random.Generator(np.random.PCG64(c.SEED));bins=rng.integers(0,1<<c.BIN_BITS,size=(c.N,4),dtype=np.uint64)
    np.savez_compressed(out/'bins.npz',bins=bins)
    lower=np.empty((5,c.N),dtype=float);upper=np.empty_like(lower);integer_lo=np.empty((5,c.N),dtype=np.int64);integer_hi=np.empty_like(integer_lo)
    production_seconds=0.;integer_seconds=0.;amb_float=np.zeros((5,2),dtype=np.int64);amb_int=amb_float.copy();differing_widths=0;maximum_float_width=0.;maximum_integer_width=0.
    for first in range(0,c.N,2048):
        last=min(first+2048,c.N);block=bins[first:last]
        for j,policy in enumerate(policies):
            now=time.perf_counter();lo,hi,amb=p.path(policy,block);production_seconds+=time.perf_counter()-now
            lower[j,first:last]=lo;upper[j,first:last]=hi;amb_float[j]+=amb
            now=time.perf_counter();il,iu,amb=q.path(policy,block);integer_seconds+=time.perf_counter()-now
            integer_lo[j,first:last]=il;integer_hi[j,first:last]=iu;amb_int[j]+=amb
            exact_lo=np.array([F(int(x),c.SCALE) for x in il],dtype=object)
            exact_hi=np.array([F(int(x),c.SCALE) for x in iu],dtype=object)
            bad=np.array([F(float(l))>h or F(float(u))<v for l,u,v,h in zip(lo,hi,exact_lo,exact_hi)])
            if bad.any():
                np.savez_compressed(out/'DISAGREEMENT.npz',bins=block[bad],float_lo=lo[bad],float_hi=hi[bad],integer_lo=il[bad],integer_hi=iu[bad])
                raise AssertionError('Independent enclosure nonoverlap: '+policy['name'])
            differing_widths+=int(np.count_nonzero(hi-lo!=(iu-il).astype(float)/c.SCALE))
            maximum_float_width=max(maximum_float_width,float((hi-lo).max()));maximum_integer_width=max(maximum_integer_width,float((iu-il).max()/c.SCALE))
        if first%(2048*16)==0:print('verified original-law rows',last,flush=True)
    np.savez_compressed(out/'float-endpoints.npz',lower=lower,upper=upper)
    np.savez_compressed(out/'integer-endpoints.npz',lower=integer_lo,upper=integer_hi)
    now=time.perf_counter();inference=infer(policies,integer_lo,integer_hi,supports);inference_seconds=time.perf_counter()-now
    exact_checks=0
    for k in (0,1,17,255,4095,65535,131071):
        for side in (0,F(1,2),1):
            coordinates=[F(int(bins[k,j])+side,1<<c.BIN_BITS) for j in (0,1)]
            coordinates += [F(int(bins[k,j])+side-(1<<(c.BIN_BITS-1)),1<<(c.BIN_BITS+4)) for j in (2,3)]
            for j,policy in enumerate(policies):
                value=q.point(policy,coordinates)
                assert F(int(integer_lo[j,k]),c.SCALE)<=value<=F(int(integer_hi[j,k]),c.SCALE)
                assert F(float(lower[j,k]))<=value<=F(float(upper[j,k]))
                exact_checks+=1
    files={name:c.sha(out/name) for name in ('bins.npz','float-endpoints.npz','integer-endpoints.npz','supports-before-sampling.json')}
    record=dict(status='passed',design_commit=freeze['design_commit'],base_commit=freeze['base_commit'],source_freeze_sha256=c.sha(R/'SOURCE_FREEZE74.json'),
        controllers=[{k:v for k,v in x.items() if k!='actions'} for x in policies],supports=supports,inference=inference,file_sha256=files,
        original_law_rows=c.N,policy_path_evaluations=5*c.N,independent_integer_policy_paths=5*c.N,new_policy_training_services=0,
        support_cell_pair_checks=sum(s['cell_pair_checks'] for s in supports),production_actor_calls=10*c.N,independent_actor_calls=10*c.N,
        ambiguous_float_actions=amb_float,ambiguous_integer_actions=amb_int,nonoverlapping_enclosures=0,valid_different_enclosure_widths=differing_widths,
        max_float_bin_width=maximum_float_width,max_integer_bin_width=maximum_integer_width,exact_point_and_face_checks=exact_checks,
        times=dict(support_seconds=support_seconds,independent_support_seconds=support_audit_seconds,production_seconds=production_seconds,integer_seconds=integer_seconds,inference_seconds=inference_seconds),
        seconds_before_final_record=time.perf_counter()-start,
        statistical_scope='Fixed complete policies; original continuous product law enclosed by IID-model bin rows. Shared rows are not independent datasets. Seed gives reproducibility only.',
        work_scope='New qualification service; historical R73 construction clocks are separate, not jointly re-executed cold-start measurements. All new endpoints independently recomputed, not all historical descendant trees.')
    c.save(out/'study.json',record);c.save(out/'clock.json',dict(seconds_through_study_output=time.perf_counter()-start,study_sha256=c.sha(out/'study.json')))
    print(json.dumps(c.encode(dict(status='passed',inference=inference,times=record['times'])),indent=2),flush=True)
if __name__=='__main__':main('--replay' in sys.argv)
