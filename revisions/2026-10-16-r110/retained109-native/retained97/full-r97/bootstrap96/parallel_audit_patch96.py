"""Parallelize only independent endpoint checks before the scientific freeze."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'code/independent96.py';s=p.read_text()
if 'def endpoint_job96(' in s:raise RuntimeError('Audit scheduler already installed')
anchor='def audit(tag,fixtures=8):'
worker='''def endpoint_job96(job):
    index,alpha,arm,j,row,obj=job
    x=[row['x0'],row['x1']];a=row['actions'];reconstructed=None
    if obj is not None:
        reconstructed=fitted_proposal(x,alpha,obj)
        if abs(reconstructed-row['proposed'])>F(1,2**29):
            raise AssertionError(f'Independent proposal disagreement: {index}/{arm}/{j}')
    lo,hi=endpoints(x,a,alpha);lb=original_lower(x,a,alpha)
    if not (row['lower']<=lo<=hi<=row['upper']):
        raise AssertionError(f'Independent enclosure not contained: {index}/{arm}/{j}')
    if hi-lb>TAU:raise AssertionError(f'Independent admission failed: {index}/{arm}/{j}')
    return dict(index=index,arm=arm,row=j,
        proposed_action=str(reconstructed) if reconstructed is not None else None,
        lower=str(lo),upper=str(hi),optimum_lower=str(lb),contained=True)


'''
if s.count(anchor)!=1:raise RuntimeError('Unexpected independent checker')
s=s.replace(anchor,worker+anchor)
start=s.index('            for j in ids:');end=s.index('    receipt.update(success=True',start)
s=s[:start]+'''            jobs=[(index,alpha,arm,j,arms[arm][j],obj) for j in ids]
            from concurrent.futures import ProcessPoolExecutor
            import os
            workers=min(4,os.cpu_count() or 1)
            receipt['endpoint_workers']=workers
            receipt['endpoint_execution']='Same fixed fixtures, rational algorithms and ordered records; parallel validation only, no additional observations.'
            with ProcessPoolExecutor(max_workers=workers) as pool:
                for result in pool.map(endpoint_job96,jobs,chunksize=1):
                    receipt['random_endpoints'].append(result)
                    dump(dest,receipt)
'''+s[end:]
p.write_text(s)
proto=R/'PROTOCOL96.md'
proto.write_text(proto.read_text()+'\n### Pre-construction independent-audit scheduling\n\nThe fixed rational endpoint checks may use up to four worker processes (bounded by the reported processor count). Fixture identities, order, arithmetic, containment tests and sample sizes are unchanged. The independent-audit receipt records the worker count and complete parent elapsed time. This scheduling does not create fits or independent observations and is fixed before construction and confirmation.\n')
print('Installed deterministic parallel endpoint validation; all scientific comparison rules unchanged.')
