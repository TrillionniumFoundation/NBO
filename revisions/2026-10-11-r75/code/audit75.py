"""Independent all-path replay and exact economic accounts; no new samples."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,time
import numpy as np
import common74 as c
import integer74 as q
import study74 as s
R=Path(__file__).resolve().parents[1]

def main():
    start=time.perf_counter();s.freeze_check();s.main(replay=True)
    record=json.loads((R/'results74/study.json').read_text())
    if record['status']!='passed':raise AssertionError('Prospective execution incomplete')
    actors=c.actors();bins=np.load(R/'results74/bins.npz')['bins']
    if bins.shape!=(c.N,4):raise AssertionError('Changed sample shape')
    regenerated=np.random.Generator(np.random.PCG64(c.SEED)).integers(0,1<<c.BIN_BITS,size=(c.N,4),dtype=np.uint64)
    if not np.array_equal(bins,regenerated):raise AssertionError('Changed declared stream')
    integer=np.load(R/'results74/integer-endpoints.npz');floating=np.load(R/'results74/float-endpoints.npz')
    count=0;ambiguity=np.zeros((5,2),dtype=np.int64)
    for j,actor in enumerate(actors):
        for first in range(0,c.N,2048):
            last=min(c.N,first+2048);lo,hi,amb=q.path(actor,bins[first:last]);ambiguity[j]+=amb
            if not np.array_equal(lo,integer['lower'][j,first:last]) or not np.array_equal(hi,integer['upper'][j,first:last]):raise AssertionError(('Independent whole-path replay disagreement',actor['name'],first))
            for a,b,u,v in zip(lo,hi,floating['lower'][j,first:last],floating['upper'][j,first:last]):
                if F(float(u))>F(int(b),c.SCALE) or F(float(v))<F(int(a),c.SCALE):raise AssertionError('Replayed floating/integer nonoverlap')
            count+=last-first
    if ambiguity.tolist()!=record['ambiguous_integer_actions']:raise AssertionError('Acquisition ambiguity changed')
    for (a,b),row in zip(c.PAIRS,record['supports']):
        if q.independent_support(actors[a],actors[b])!=F(row['bound']):raise AssertionError('Independent support disagreement')
    contrasts=record['inference']['contrasts'];ledgers={};gains={}
    for key,v in contrasts.items():
        endpoints=list(map(F,v['interval']))
        if v['identity']:continue
        terms=[F(v['mean_bin_enclosure_width']),F(v['sampling_radius_lower'])+F(v['sampling_radius_upper']),2*F(v['range_radius'])]
        unclipped=sum(terms);width=endpoints[1]-endpoints[0]
        if width>unclipped:raise AssertionError('Width ledger invalid')
        ledgers[key]=dict(mean_enclosure=str(terms[0]),sampling=str(terms[1]),range=str(terms[2]),unclipped=str(unclipped),clipping_reduction=str(unclipped-width),width=str(width),precision_met=v['precision_met'])
        gains[key]=dict(gain_interval=list(map(str,[-endpoints[1],-endpoints[0]])),additional_one_off_price_per_deployment_at_unit_loss_value_lower=str(-endpoints[1]))
    audit=dict(status='passed',controlling_review_commit='4b27b56f4514f6c1d77b69fe707f7202f8b06b19',baseline_commit='5b6bb84fe02e6c7295624c1d9ba5266eef6c5717',
        original_law_rows=c.N,recomputed_integer_paths=count,recomputed_actor_calls=count*2,recomputed_support_cell_pairs=record['support_cell_pair_checks'],
        declared_estimands=13,paired_estimands=len(contrasts),paired_precision_successes=sum(v['precision_met'] for v in contrasts.values()),
        paired_precision_failures=[k for k,v in contrasts.items() if not v['precision_met']],strictly_lower_contrasts=[k for k,v in contrasts.items() if v['strictly_lower']],
        equivalent_contrasts=[k for k,v in contrasts.items() if v['equivalent']],acquisition_ambiguities=ambiguity.tolist(),ledgers=ledgers,gains=gains,
        inherited_construction_services=4,current_new_training_services=0,additional_independent_sample_families_from_replay=0,seconds=time.perf_counter()-start,
        scope='Every frozen original-law integer path and acquired-action range independently re-evaluated; exact confidence endpoints and primitive supports replayed. This is not independent re-integration of historical large recursive trees.',
        study_sha256=c.sha(R/'results74/study.json'))
    c.save(R/'audit/RESULT_AUDIT75.json',audit)
    print(json.dumps({k:audit[k] for k in ('status','original_law_rows','recomputed_integer_paths','paired_precision_successes','paired_precision_failures','seconds')},indent=2))
if __name__=='__main__':main()
