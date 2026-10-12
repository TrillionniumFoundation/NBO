"""Tables from recovered exact records; execution and replay clocks differ.
Cost endpoints are outward rounded, guaranteed tolerance ranges inward rounded.
"""
from pathlib import Path
from fractions import Fraction as F
import json
import tables82 as t
import frontier83 as f
R=Path(__file__).resolve().parents[1];N=t.NAMES

def cap(item):
    if not item['nonempty']:return r'$\varnothing$'
    e=F(item['supremum'])
    if e==f.MAX_EXCESS and item['supremum_included']:return r'$[0,2^{-12}]$'
    v=e*10**9;k=v.numerator//v.denominator
    if F(k,10**9)==e and not item['supremum_included']:k-=1
    if k<0:return r'$\varnothing$'
    return '$[0,'+t.end(F(k,10**9),digits=9)+']$'

def main():
    a=f.read(R/'results83/frontier.json');m=f.read(R/'results83/transfer.json');execution=f.read(R/'results83/EXECUTION83.json')
    if not execution['full_reintegration']:raise AssertionError('Complete executed reintegration required')
    services=[f.read(R/'results82'/f'{k}-n{n}.json') for n,k in f.MODELS]
    focus=[x for x in m['pairwise'] if x['first']=='calibrated-relu-n16' and x['second']=='calibrated-bernstein-n16' and x['rung']==3]
    t.table('fine-classes82','Fine-grid optimizer-class cost differences',
        [r'$\epsilon$','Binary-mass band','Actionwise band','Sign'],
        [[t.eps(x['extra_objective']),t.band(x['coarse_interval']),t.band(x['optimizer_sublevel_interval']),x['sign']] for x in focus],
        'ReLU minus Bernstein costs for all qualified readout pairs with fixed labels and terminal actors. Every earlier dyadic level is retained. Cost endpoints are rounded outward; allowances are exact.')
    rows=[]
    for s in services:
        for tier in s['tiers']:
            for x in tier['sublevels']:
                rows.append([N[s['name']],t.eps(x['extra_objective']),f"{tier['state_subdivisions']}/{tier['shock_bins']}",x['possible_alternatives'],t.end(x['coarse_radius'],True),t.end(x['lower']),t.end(x['upper'],True)])
    t.table('sublevels82','Every model, allowance and integration level',
        ['Actor',r'$\epsilon$',r'$r/q$','Actions',r'$Hq_\epsilon$',r'$v^-$',r'$v^+$'],rows,
        'R and B denote calibrated ReLU and Bernstein; 8 and 16 are acquisition resolutions. All 48 inherited model--allowance--level bands are shown. These are deterministic refinements, not independent observations.',True)
    rungs=((2,8),(4,16),(8,32),(16,64));rows=[]
    for x in m['pairwise']:
        r,q=rungs[x['rung']];lo,hi=x['optimizer_sublevel_interval']
        rows.append([N[x['first']]+'--'+N[x['second']],t.eps(x['extra_objective']),f'{r}/{q}',t.end(lo),t.end(hi,True),x['sign']])
    t.table('all-pairs82','Every directed optimizer-class comparison',
        ['Pair',r'$\epsilon$',r'$r/q$','Lower','Upper','Sign'],rows,
        'All 72 comparisons use the existing R80 joint event plus deterministic actionwise transfer. Inconclusive coarse ReLU classes and adverse comparisons remain in the catalogue.',True)
    rows=[]
    for x in m['own_controller']:
        ref='Zero' if x['reference']=='zero' else 'Legacy '+N[x['class_name']]
        rows.append([N[x['class_name']],ref,t.eps(x['extra_objective']),t.end(x['reference_minus_class'][0]),t.end(x['reference_minus_class'][1],True)])
    t.table('own-gains82','All fixed-reference classwide gains',
        ['Class','Reference',r'$\epsilon$','Lower gain','Upper gain'],rows,
        'Fixed reference cost minus each calibrated class cost. All 24 final-level zero and same-resolution legacy comparisons are retained. No reference is renamed by dropping an identity prefix or refitted.',True)
    rows=[];clocks=execution['current_replay_work']
    for s in services:
        for tier,clock in zip(s['tiers'],clocks[s['name']]):
            rows.append([N[s['name']],f"{tier['state_subdivisions']}/{tier['shock_bins']}",len(tier['per_action']),sum(x['boxes'] for x in tier['per_action']),f"{clock['seconds']:.3f}",clock['binary64_actor_queries'],clock['integer_actor_queries']])
    t.table('work82','Executed R83 independent recovery work',
        ['Actor',r'$r/q$','Pairs','Boxes','Seconds','Float queries','Integer queries'],rows,
        'Each box is reevaluated by both independent arithmetic implementations. These are the first completed R83 recovery-run clocks, including endpoint hashing and rational checks within each level. They do not replace the failed R82 integration clocks or measure a matched training-speed comparison. Subsequent verification has separately named clocks.',True)
    standard=next(x for x in focus if x['extra_objective']=='1/65536')
    t.put('tables/finding82.tex','At the standard objective allowance $2^{-16}$, the ReLU-minus-Bernstein class interval is $'+t.band(standard['optimizer_sublevel_interval'])+'$, compared with the binary-mass interval $'+t.band(standard['coarse_interval'])+'$. The positive actionwise interval applies uniformly to the stated approximate-optimizer classes. No new attained-policy sample is used.\n')
    t.put('tables/work-finding82.tex','The completed recovery reevaluates '+format(execution['paired_boxes_per_implementation'],',')+' paired boxes per arithmetic implementation and verifies '+format(execution['exact_rational_midpoint_checks'],',')+' exact rational midpoint differences. Its independently recorded time through the verification calculations is '+f"{execution['seconds']:.3f}"+' seconds; peak resident memory is '+format(execution['peak_rss_kib'],',')+' KiB. The failed R82 run retains its own partial integration-phase clocks and exception record. This recovery is not a new policy-cost sample.\n')
    rows=[];allrows=[]
    for pair in a['pairwise_frontiers']:
        name=N[pair['first']]+'--'+N[pair['second']]
        rows.append([name,cap(pair['targets']['positive']['common_excess_limit']),cap(pair['targets']['equivalent']['common_excess_limit'])])
        for kind,item in pair['targets'].items():
            bound=item['common_excess_limit']
            allrows.append([name,{'positive':r'$J_1>J_2$','negative':r'$J_1<J_2$','equivalent':r'$|J_1-J_2|<2^{-8}$'}[kind],len(item['stripes']),cap(bound),('yes' if bound['supremum_included'] else 'no') if bound['nonempty'] else '--'])
    t.table('frontier83','Certified common optimization tolerances',
        ['Pair','Second has lower cost','Equivalent within $2^{-8}$'],rows,
        'Every tolerance in each displayed closed interval is certified. Decimal endpoints are rounded inward, not estimates of the exact boundary. Empty means this sufficient interval test is inconclusive even at zero excess. Exact rational frontiers, boundary inclusion and heterogeneous-tolerance strips are deposited. R denotes ReLU and B Bernstein.')
    t.table('frontier-all83','All eighteen tolerance-frontier targets',
        ['Pair','Target','Strips','Guaranteed common range','Exact end included'],allrows,
        'The strip count concerns the full two-dimensional sufficient region, not just its equal-tolerance slice. The last column refers to the exact rational supremum, not the inward-rounded displayed endpoint. Every returned and excluded pair of tolerance strata is independently checked.',True)
    rows=[]
    for x in a['own_controller_frontiers']:
        last=x['all_tolerances_gain'][-1];ref='Zero' if x['reference']=='zero' else 'Legacy '+N[x['class_name']]
        rows.append([N[x['class_name']],ref,t.band(last['gain_interval'])])
    t.table('own-all83','Uniform gains at the largest integrated allowance',
        ['Class','Reference',r'Gain for $0\le\epsilon\le2^{-12}$'],rows,
        'Every optimizer-class output in the displayed tolerance interval is included. All four zero-controller gains have positive lower endpoints. The coarse ReLU-versus-legacy comparison remains inconclusive. The full exact step function for every reference is deposited.',True)
    tables={p.name:f.sha(p) for p in (R/'tables').glob('*8[23].tex')}
    f.save(R/'audit/TABLES83.json',dict(status='passed',tables=tables,frontier_targets=18,model_tolerance_strata=a['model_tolerance_strata'],
        independent_grid_checks=a['independent_frontier_grid_checks'],original_discrete_bands=48,pairwise_transfers=72,own_transfers=24,
        execution83_sha256=f.sha(R/'results83/EXECUTION83.json'),new_cost_rows=0))
    print(json.dumps(dict(status='passed',tables=len(tables),frontier_targets=18)))
if __name__=='__main__':main()
