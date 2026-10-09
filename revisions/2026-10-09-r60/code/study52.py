"""Exhaustive, source-frozen action-null ablation on the original economy.

This is a deterministic terminal certificate study. It generates no new
Monte Carlo cost intervals and does not replace any historical observation.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json, os, platform, resource, subprocess, sys, time
from pathlib import Path
from fractions import Fraction as F
import operators50 as o
R=Path(__file__).resolve().parents[1]
np=o.np; I=o.I
AMPLITUDES=(0,1,16,4096)
SOURCE_NAMES=['STUDY_PROTOCOL52.md','code/study52.py','code/contrast52.py','code/tests52.py',
              'code/operators50.py','code/tests51.py']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w') as f:
        f.write(json.dumps(j,indent=2,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())

def catalogue():
    root=R/'inputs/revisions/2026-10-08-r49/results/services'
    paths=sorted(root.glob('*/checkpoint*.json'))
    if len(paths)!=8:raise ValueError('The fixed catalogue must contain exactly eight policies')
    return [{'key':p.parent.name,'path':str(p.relative_to(R)),'sha256':sha(p)} for p in paths]

def freeze():
    path=R/'audit/SOURCE_FREEZE52.json'
    if path.exists():raise FileExistsError(path)
    import study50
    study50.verify_freeze()
    save(path,{'source_commit':os.environ.get('NBO52_SOURCE_SHA','local-unpublished'),
               'predecessor_commit':'62ffa8d0753c82a1363831f49a297c815d89204f',
               'protocol_first_commit':'3e4230c7e4ec4ab456b7722ff859a70d35de2172',
               'sha256':{n:sha(R/n) for n in SOURCE_NAMES},'catalogue':catalogue(),
               'amplitudes':AMPLITUDES,'cells_per_policy':65536,
               'interpretation':'known algebra; prospectively fixed deterministic robustness ablation, not independent cost data'})

def verify():
    j=json.loads((R/'audit/SOURCE_FREEZE52.json').read_text())
    for n,h in j['sha256'].items():
        if sha(R/n)!=h:raise ValueError('Changed scientific source: '+n)
    if catalogue()!=j['catalogue']:raise ValueError('Changed policy catalogue')
    return j

def service(index):
    frozen=verify();spec=frozen['catalogue'][index]
    out=R/'results52'/spec['key']
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True)
    cpus=sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else []
    if cpus:os.sched_setaffinity(0,{cpus[0]})
    start=time.perf_counter();cpu=time.process_time()
    payload=json.loads((R/spec['path']).read_text());policy=o.AcquiredPolicy(payload,8)
    if policy.d!=2:raise ValueError('The frozen legacy catalogue is two-dimensional')
    bins=np.array([(i,j) for i in range(256) for j in range(256)],dtype=np.int64)
    all_base=[];all_proposal=[];all_lower=[];all_upper=[];all_repaired=[]
    reference=o.AcquiredPolicy(payload,8)
    for first in range(0,len(bins),2048):
        b=bins[first:first+2048]
        base=policy._cell_base(policy.T-1,b)
        proposal=o.proposal(b,8,policy.p,policy.counts)
        diff=o.final_difference(I(b/256,(b+1)/256),I.point(proposal),I.point(base),policy.p)
        repaired=np.where(diff.hi<=0,proposal,base)
        _,old=reference.cell_actions(policy.T-1,b,True)
        if not np.array_equal(repaired,old):raise AssertionError('Changed inherited terminal policy')
        all_base.append(base);all_proposal.append(proposal);all_lower.append(diff.lo)
        all_upper.append(diff.hi);all_repaired.append(repaired)
    base=np.concatenate(all_base);prop=np.concatenate(all_proposal)
    lo=np.concatenate(all_lower);hi=np.concatenate(all_upper);new=np.concatenate(all_repaired)
    if np.any(~np.isfinite(lo)) or np.any(~np.isfinite(hi)) or np.any(lo>hi):raise AssertionError('Invalid interval')
    bi=np.rint(base*4096).astype(np.int64);vi=np.rint(prop*4096).astype(np.int64)
    ni=np.rint(new*4096).astype(np.int64)
    cap=(4096*(256*2+bins.sum(axis=1)))//(8*2*256)
    violations=int(np.count_nonzero((bi<0)|(vi<0)|(ni<0)|(bi>cap)|(vi>cap)|(ni>cap)))
    if violations:raise AssertionError('Infeasible acquired-cell action')
    changed=(bi!=vi);rows=[];old_indices=[]
    for M in AMPLITUDES:
        allowance=o.s.c.rat_i(o.BETA*F(2*M))
        scalar=(I(hi,hi)+allowance).hi<=0 if M else hi<=0
        local=hi<=0
        got=np.where(local,vi,bi)
        if not np.array_equal(got,ni):raise AssertionError('Null-amplitude policy dependence')
        old=np.where(scalar,vi,bi);old_indices.append(old)
        rows.append({'M':M,'global_error_width':2*M,'action_error_allowance':0,
                     'scalar_strict_changes':int(np.count_nonzero(changed&scalar)),
                     'contrast_strict_changes':int(np.count_nonzero(changed&local)),
                     'scalar_blocked_changes':int(np.count_nonzero(changed&~scalar)),
                     'contrast_blocked_changes':int(np.count_nonzero(changed&~local)),
                     'equal_proposals':int(np.count_nonzero(~changed)),
                     'identical_to_inherited_repaired_policy':True})
    compute_seconds=time.perf_counter()-start
    file=out/'cells.csv.gz'
    with file.open('wb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as gz:
            gz.write(b'i,j,base,proposal,contrast,lower_hex,upper_hex,scalar_M0,scalar_M1,scalar_M16,scalar_M4096\n')
            for k,(i,j) in enumerate(bins):
                line=[str(i),str(j),str(bi[k]),str(vi[k]),str(ni[k]),float(lo[k]).hex(),float(hi[k]).hex()]+[str(a[k]) for a in old_indices]
                gz.write((','.join(line)+'\n').encode('ascii'))
        raw.flush();os.fsync(raw.fileno())
    serialized_seconds=time.perf_counter()-start
    rec={'key':spec['key'],'T':policy.T,'price':policy.p,'dimension':2,'cells':len(bins),
         'input':spec,'amplitudes':rows,'feasibility_violations':violations,
         'maximum_accepted_true_cost_upper':float(np.max(hi[(ni!=bi)])) if np.any(ni!=bi) else None,
         'counts':policy.counts,'independent_inherited_replay_counts':reference.counts,
         'centered_gate_evaluations':len(bins),'amplitude_gate_evaluations':2*len(bins)*len(AMPLITUDES),
         'construction_seconds':compute_seconds,'through_cells_fsync_seconds':serialized_seconds,
         'serialization_seconds':serialized_seconds-compute_seconds,
         'cpu_seconds':time.process_time()-cpu,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
         'affinity':cpus[:1],'python':platform.python_version(),'numpy':np.__version__,
         'cell_file':file.name,'cell_sha256':sha(file),'cell_bytes':file.stat().st_size,
         'clock_scope':'load input, enumerate cells, proposals, centered intervals, inherited-policy replay, all gates, and durable cell serialization; no inherited construction clock is spliced in'}
    save(out/'record.json',rec)
    save(out/'clock.json',{'record_sha256':sha(out/'record.json'),'through_record_fsync_seconds':time.perf_counter()-start})
    print(json.dumps({'key':spec['key'],'cells':len(bins),'changes':[q['scalar_strict_changes'] for q in rows],
                      'contrast_changes':rows[0]['contrast_strict_changes'],'seconds':time.perf_counter()-start}),flush=True)

def execute():
    verify();start=time.perf_counter()
    for i in range(8):subprocess.run([sys.executable,__file__,'--service',str(i)],check=True)
    files=sorted((R/'results52').rglob('*'))
    save(R/'audit/EXECUTION52.json',{'status':'completed','services':8,'cells':524288,
             'new_independent_cost_estimands':0,'elapsed_seconds':time.perf_counter()-start,
             'source_freeze_sha256':sha(R/'audit/SOURCE_FREEZE52.json'),
             'files':{str(p.relative_to(R)):sha(p) for p in files if p.is_file()}})

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--execute',action='store_true');ap.add_argument('--service',type=int)
    a=ap.parse_args()
    if a.freeze:freeze()
    elif a.execute:execute()
    elif a.service is not None:service(a.service)
