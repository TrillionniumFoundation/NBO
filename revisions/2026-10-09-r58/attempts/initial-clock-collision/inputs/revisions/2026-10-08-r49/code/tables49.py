"""Generate all displayed R49 numbers from the verified immutable catalogue."""
from __future__ import annotations
import collections,csv,itertools,json,statistics
from service49 import *
from analyze49 import write
SHORT={'compiled-witness':'W','tensor-fvi':'F','curvature-fvi':'A'}
LAWS={'uniform':'U','1/8':'L','1/2':'C','7/8':'H'}
def number(x,n=5):return f'{float(F(x)):.{n}g}'
def tick(x):return '--' if x is None else str(x)
def table(name,caption,head,rows,align,notes=''):
    p=HERE/'tables'/(name+'.tex');p.parent.mkdir(exist_ok=True)
    header=' & '.join(head)+r' \\'+'\n'
    text='{\\small\n\\setlength{\\tabcolsep}{3.5pt}\n\\begin{longtable}{@{}'+align+'@{}}\n'
    text+='\\caption{'+caption+'}\\label{tab:'+name+'}\\\\\n\\toprule\n'+header+'\\midrule\n\\endfirsthead\n\\toprule\n'+header+'\\midrule\n\\endhead\n\\bottomrule\n\\endfoot\n'
    text+='\n'.join(' & '.join(map(str,r))+r' \\' for r in rows)
    text+='\n\\end{longtable}\n}\n'
    if notes:text+='\\noindent{\\footnotesize '+notes+'\\par}\n'
    p.write_text(text)

def main():
    a=read(HERE/'audit/RESULT_AUDIT.json');assert a['passed']
    summary=read(HERE/'audit/PUBLICATION_SUMMARY.json')
    records={}
    for p in (HERE/'results/services').glob('*/record.json'):
        j=read(p);records[(j['dimension'],j['horizon'],j['price'],j['method'],j['repeat'])]=j
    rows=[[SHORT[m]]+[f"{summary['attainment'][m][str(q)]}/12" for q in (4,2,1,F(1,2))] for m in METHODS]
    table('attainment49','Block A separated-resource attainment',['Method','$4$','$2$','$1$','$1/2$'],rows,'lrrrr','W: compiled witness; F: uniform FVI; A: pilot-curvature bisection FVI. Twelve services per method are four economies, each repeated three times. They are not twelve independent economic tasks or optimizer draws.')
    rows=[];front=read(HERE/'audit/TOLERANCE_FRONTIERS.json')
    for j in front:
        if j['d']!=2:continue
        bands=[]
        for b in j['intervals']:
            identity=tuple(None if b['methods'][m] is None else b['methods'][m]['N'] for m in METHODS)
            if bands and bands[-1]['identity']==identity:bands[-1]['right_open']=b['right_open']
            else:bands.append({**b,'identity':identity})
        for b in bands:
            left=number(b['left_closed'],6);right=r'\infty' if b['right_open'] is None else number(b['right_open'],6)
            line=[f"({j['T']},{j['p']})",f'$[{left},{right})$']
            for m in METHODS:
                z=b['methods'][m];line.append('--' if z is None else f"{z['N']}; {z['median_seconds']:.3f}")
            rows.append(line)
    table('frontier49','Complete positive-tolerance frontiers in two states',['$(T,p)$','Tolerance interval','W: $N$; sec.','F: $N$; sec.','A: $N$; sec.'],rows,'llrrr','Each time is the median complete prefix over three isolated repetitions. A dash is a capped failure. Adjacent bands with identical returned rungs are merged. Printed cutoffs are rounded; exact rational endpoints in the deposited frontier determine membership, including equality. The action and integration budgets are uniquely fixed by $N$ in the common ladder. Minima, maxima and counts are deposited, not replaced by these medians.')
    rows=[]
    for dd,T in itertools.product((2,3,4),(2,3)):
        row=[dd,T]
        for m in METHODS[:2]:
            z=next(v for v in summary['dimension_target'] if v['d']==dd and v['T']==T and v['method']==m)
            row += [f"{z['attained']}/3",tick(z['N']),'--' if z['median_seconds'] is None else f"{z['median_seconds']:.3f}"]
        rows.append(row)
    table('dimension49','Repeated common-accuracy comparison: target five, price one',['$d$','$T$','W pass','$N$','sec.','F pass','$N$','sec.'],rows,'rrrrrrrr','All dimensions face the same coarse target five; caps and allocations remain explicit. Two-state observations are reused from the main catalogue and not counted twice. This finite comparison does not identify an asymptotic scaling law.')
    allr=[];csvrows=[]
    for key,j in sorted(records.items()):
        dd,T,p,m,rep=key
        if rep:continue
        for i,r in enumerate(j['attempts']):
            times=[records[(dd,T,p,m,k)]['attempts'][i]['prefix_seconds'] for k in range(3)]
            allr.append([f'{dd};{T};{p}',SHORT[m],f"{r['N']},{r['K']},{r['M']}",number(r['bound_exact'],7),f'{statistics.median(times):.3f}',f'[{min(times):.3f},{max(times):.3f}]'])
            csvrows.append({'dimension':dd,'horizon':T,'price':p,'method':m,'N':r['N'],'K':r['K'],'M':r['M'],'bound_exact':r['bound_exact'],'median_prefix_seconds':statistics.median(times),'minimum_prefix_seconds':min(times),'maximum_prefix_seconds':max(times),'prefix_innovation_midpoints':r['prefix_counts']['innovation_midpoints'],'stored_actor_scalars':r['counts']['stored_actor_scalars'],'checkpoint_sha256':r['checkpoint_sha256']})
    table('rungs49','All distinct construction rungs and complete-prefix times',['$d;T;p$','Method','$N,K,M$','Bound','Median sec.','Range sec.'],allr,'llrrrr')
    with (HERE/'audit/RUNG_FRONTIER.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=csvrows[0].keys());w.writeheader();w.writerows(csvrows)
    cat=read(HERE/'audit/DIRECT_CATALOGUE.json');pairs=[];sensors=[]
    for s in cat['specs']:
        j=read(HERE/'results/direct'/(s['key']+'.json'))
        (pairs if s['kind']=='pair' else sensors).append(j)
    rows=[]
    for ver,target,bits in itertools.chain(itertools.product(('R49',),(4,2,1),(None,8)),itertools.product(('R48',),(2,),(None,8))):
        js=[j for j in pairs if j['spec']['frontier']==ver and j['spec']['target']==target and j['spec']['bits'][0]==bits]
        if not js:continue
        counts=collections.Counter(j['sign'] for j in js);fees=[F(j['replacement']['fee_certifying_both_not_profitable']) for j in js]
        rows.append([ver,target,'E' if bits is None else bits,len(js),counts['left-lower'],counts['left-higher'],counts['unresolved'],f'[{number(min(fees),4)},{number(max(fees),4)}]'])
    table('direct49','Actual costs of the returned policies and fee sensitivity',['Pair','$\varepsilon$','Bits','$n$',r'\shortstack{W\\lower}',r'\shortstack{W\\higher}','Unres.',r'\shortstack{Sufficient\\fee range}'],rows,'lrrrrrrr','E denotes full information. Counts cover every declared initial law and economic cell in the group; they do not rank all initial states. The fee is sufficient to certify that neither directional switch pays. It is not the smaller threshold that merely removes identified profitability. All new intervals share one 99 percent family conditional on the independent-bin model.')
    rows=[]
    for j in pairs:
        s=j['spec'];lo,hi=j['interval_exact'];rows.append([s['frontier'],f"{s['T']};{s['p']}",s['target'],LAWS[s['law']],'E' if s['bits'][0] is None else s['bits'][0],number(lo,6),number(hi,6)])
    table('all-direct49','Every actual first-crossing policy-cost interval',['Pair','$T;p$','$\varepsilon$','Law','Bits','Lower','Upper'],rows,'llrrr rr'.replace(' ',''),'Endpoints are displayed to six significant digits; exact rational endpoints and policy hashes govern every sign and fee conclusion. R48 rows evaluate the old favorable N=32 witness versus N=64 FVI pair under fresh independent interval paths.')
    rows=[]
    for j in sensors:
        s=j['spec'];lo,hi=j['interval_exact'];rows.append([f"{s['T']};{s['p']}",SHORT[s['method']],s['bits'][0],number(lo,6),number(hi,6)])
    table('all-sensor49','Every actual sensor-cost difference relative to 16 bits',['$T;p$','Method','Bits','Lower','Upper'],rows,'llrrr','All rows use the uniform initial law and the actual first-target-one controller. Self-comparisons are exact identities. Both policies use the declared robust repair and action quantum.')
    decisions=read(HERE/'audit/SENSOR_DECISIONS.json');rows=[]
    for j in decisions:
        c=[x['certified_bits'] for x in j['decisions']];u=[x['net_upper_selected_bits'] for x in j['decisions']];reg=[F(x['selected_regret_upper']) for x in j['decisions']]
        rows.append([f"{j['T']};{j['p']}",SHORT[j['method']],','.join(map(str,c)),','.join(map(str,u)),f'[{number(min(reg),4)},{number(max(reg),4)}]'])
    table('sensor49','Information choice on the same evaluated bit grid',['$T;p$','Method',r'\shortstack{Bound-minimizing\\bits}',r'\shortstack{Net-selected\\bits}',r'\shortstack{Net-regret\\bound range}'],rows,'llrrr','Bit triples correspond, in order, to prices $1/16384,1/4096,1/1024$ per coordinate-bit. The net selector minimizes the upper actual-net-cost interval. Its regret bound is against the best bit in the finite catalogue, not an estimated unconstrained optimum. Every price-specific value and all nonnegative-price envelopes are deposited.')
    all_dec=[z for j in decisions for z in j['decisions']];proven=sum(F(j['net_selected_minus_certified_interval'][1])<0 for j in all_dec);reg=[F(j['selected_regret_upper']) for j in all_dec]
    ftime=summary['timing']['tensor-fvi'];atime=summary['timing']['curvature-fvi'];signs=summary['new_frontier_signs'];old=summary['r48_favorable_signs']
    text=(f"The original block A contains {summary['services']} services and {summary['rungs']} rungs. Repeated mathematical checkpoints are byte-identical. "
          f"The pilot-curvature bisection generator realizes nonuniform axes in {summary['adaptive_nonuniform_date_models']} of {summary['adaptive_total_date_models']} date models; its name alone does not establish effective adaptation. "
          f"At common successful declared target-by-repetition comparisons, witness is faster than uniform FVI in {ftime['witness_faster']} of {ftime['common']} and slower in {ftime['witness_slower']}. "
          f"Against pilot-curvature bisection FVI, the corresponding counts are {atime['witness_faster']} faster and {atime['witness_slower']} slower out of {atime['common']}. "
          "These counts summarize selected targets; Table~\\ref{tab:frontier49} and the exact deposited partition, rather than a binary attainment headline, are the primary work comparison.\n\n")
    text+=(f"The new first-crossing direct-cost intervals identify lower witness cost in {signs.get('left-lower',0)} cases, higher cost in {signs.get('left-higher',0)}, and leave {signs.get('unresolved',0)} unresolved. "
           f"For the separately evaluated favorable R48 work pair, the corresponding counts are {old.get('left-lower',0)}, {old.get('left-higher',0)} and {old.get('unresolved',0)}. "
           "A cheaper first crossing and a sharper bound therefore receive an actual economic comparison rather than an inferred ranking. The detailed intervals and initial actions are retained, including every adverse outcome.\n\n")
    text+=(f"Across the {len(all_dec)} declared controller--price decisions, the upper-net-cost selector is certified strictly cheaper than the all-state-bound minimizer in {proven}. "
           f"Its cost-regret upper bounds relative to the best evaluated bit range from {number(min(reg),6)} to {number(max(reg),6)} in the normalized economic units. "
           "Where the comparison does not identify a strict improvement it remains unresolved; midpoint choices are descriptive, not true optima. This is a finite expected-net-cost conclusion under the uniform initial law, not a calibrated welfare result or a universal preference for coarse observation.\n\n")
    text+=(f"The direct and sensor study contains {summary['sampled_contrasts']} sampled contrasts, totaling {summary['sampled_paths']:,} interval paths, with a separately recorded joint evaluation time of {summary['joint_direct_seconds']:.2f} seconds. "
           "Identity rows use no simulated paths. This evaluation work is not allocated to one favored generator or hidden inside another method's construction clock.\n")
    (HERE/'results-discussion49.tex').write_text(text)
    write(HERE/'audit/EDITORIAL_NUMBERS.json',{'direct_signs':signs,'r48_favorable_signs':old,'sensor_price_decisions':len(all_dec),'net_selector_proven_cheaper_than_bound_selector':proven,'net_regret_range':list(map(str,(min(reg),max(reg)))),'printed_cutoffs_are_rounded':True})
    print(text)
if __name__=='__main__':main()
