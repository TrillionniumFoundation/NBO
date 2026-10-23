"""Exact complete-record identity to F126, after deleting clocks/metadata only."""
import argparse
from cache126c import *


def key(r):return tuple(r[k] for k in ('index','budget','arm','training_loss','mode','row'))


def run(primary,timings,output):
    out,tick,info=start(output,'R126C-exact-complete-scientific-record-identity')
    try:
        gate=verify_sources(); original=rows(ROOT/'results126/primary01/records126.jsonl.gz')
        reference={key(r):fingerprint(r) for r in original}
        assert len(reference)==len(original)==1584
        checks=0;counts=Counter();paths=[]
        for path,expected_states in [(primary,range(9))]+[(t,range(1)) for t in timings]:
            data=rows(Path(path)/'records126c.jsonl.gz')
            expected={(v,c+(r,)) for v in VARIANTS for c in catalog() for r in expected_states}
            actual={(r['variant126c'],key(r)) for r in data}
            assert len(data)==len(actual)==len(expected) and actual==expected
            for r in data:
                ident=key(r)
                assert fingerprint(r)==reference[ident],('scientific record mismatch',str(path),r['variant126c'],ident)
                radius,regret=F(r['action_distance_upper']),F(r['certified_regret_upper'])
                assert radius>=0 and radius*radius>=regret
                if r['variant126c']=='uncached':assert not r['cache_stats126c']
                else:
                    assert all(isinstance(v,int) and v>=0 for v in r['cache_stats126c'].values())
                    counts.update(r['cache_stats126c'])
                checks+=1
            paths.append(dict(path=str(path),rows=len(data),sha256=sha(Path(path)/'records126c.jsonl.gz')))
        assert len(timings)==3 and checks==4224
        finish(out,tick,exact_full_scientific_records=checks,primary_decisions=3168,timing_decisions=1056,
            clock_and_metadata_only_exclusions=True,all_decisions_and_economic_work_identical_to_F126=True,
            exact_distance_square_checks=checks,cache_counts=dict(counts),inputs=paths,
            original_economic_evaluations=0,source=gate)
    except BaseException:fail(out,tick);raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--primary',required=True);p.add_argument('--timing',action='append',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.primary,a.timing,a.output)
