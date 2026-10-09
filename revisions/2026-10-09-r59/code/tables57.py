"""Publication tables derived exclusively from the complete R57 replay."""
from pathlib import Path
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
from fractions import Fraction as F
import json,statistics
R=Path(__file__).resolve().parents[1]
NAMES={'common-only':'C','relu-menu':'N','relu-exact':'X','quadratic-exact':'Q','extra-trees-menu':'E'}
ORDER=tuple(NAMES)
def put(name,text):
    if name.endswith('.tex') and any(ord(c)<32 and c not in '\n\r\t' for c in text):raise ValueError('Control character in LaTeX')
    path=R/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
def ep(v,lower=False,d=5):
    if isinstance(v,str):v=float(F(v))
    return format(Decimal.from_float(float(v)).quantize(Decimal(10)**(-d),rounding=ROUND_FLOOR if lower else ROUND_CEILING),'f')
def band(v):return '['+ep(v[0],True)+', '+ep(v[1])+']'
def num(v):return f'{v:.3f}'
def ident(row):return f"{row['d']}/{row['T']}-{10 if row['target']=='9/10' else 20}-{NAMES[row['mode']]}-{(57101,57203,57307).index(row['seed'])+1}"
def table(name,caption,label,heads,rows,note,cols=None,long=False):
    cols=cols or 'l'+'r'*(len(heads)-1)
    rowtext='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
    header=' & '.join(heads)+r' \\'+'\n\\hline\n'
    if long:
        text='\\begingroup\\small\\setlength{\\tabcolsep}{3pt}\n\\begin{longtable}{'+cols+'}\n\\caption{'+caption+'}\\label{'+label+'}\\\\\n\\hline\n'+header+'\\endfirsthead\n\\multicolumn{'+str(len(heads))+'}{c}{'+caption+' (continued)}\\\\\n\\hline\n'+header+'\\endhead\n\\hline\n\\endfoot\n'+rowtext+'\n\\end{longtable}\n\\endgroup\n{\\footnotesize '+note+'}\n'
    else:
        text='\\begin{table}[htbp]\n\\centering\\caption{'+caption+'}\\label{'+label+'}\n{\\small\\setlength{\\tabcolsep}{4pt}\\begin{tabular}{'+cols+'}\n\\hline\n'+header+rowtext+'\n\\hline\\end{tabular}}\n\\par\\smallskip{\\footnotesize '+note+'}\n\\end{table}\n'
    put('tables/'+name+'.tex',text)
def main():
    a=json.loads((R/'audit/RESULT_AUDIT57.json').read_text());rows=a['rows'];pairs=a['paired'];grouped=[]
    for d,T in ((2,2),(4,4),(8,6)):
        for target in ('9/10','4/5'):
            for mode in ORDER:
                rr=[r for r in rows if (r['d'],r['target'],r['mode'])==(d,target,mode)]
                times=[r['whole_process_seconds'] for r in rr]
                grouped.append(dict(d=d,T=T,target=target,mode=mode,attained=sum(r['status']=='target_attained' for r in rr),cost_upper=max(r['stages'][-1]['cost'][1] for r in rr),time_min=min(times),time_median=statistics.median(times),time_max=max(times),search_median=statistics.median(sum(z['search_seconds'] for z in r['stages']) for r in rr),fit_median=statistics.median(sum(z['fit_seconds'] for z in r['stages']) for r in rr),verify_median=statistics.median(sum(z['verification_seconds'] for z in r['stages']) for r in rr),infer_median=statistics.median(sum(z['inference_seconds'] for z in r['stages']) for r in rr),bytes_max=max(r['serialized_bytes'] for r in rr),rss_max=max(r['peak_rss_kib'] for r in rr)))
    for target,name in [('4/5','target20-57'),('9/10','target10-57')]:
        rr=[[f"{r['d']}/{r['T']}",NAMES[r['mode']],f"{r['attained']}/3",ep(r['cost_upper']),num(r['time_median']),f"{num(r['time_min'])}--{num(r['time_max'])}"] for r in grouped if r['target']==target]
        table(name,'Prospective '+('twenty' if target=='4/5' else 'ten')+'-percent target services','tab:'+name,['$d/T$','Mode','Reached','Cost upper','Median (s)','Range (s)'],rr,'C uses common candidates without fitting. N uses the trained ReLU menu; X adds its exact algebraic witness; Q uses quadratic exact search; E uses ExtraTrees menu proposals. All modes receive the same exact terminal action. Three different training seeds are reconstructed separately. Cost upper is the largest returned-policy upper endpoint across those seeds, not a confidence bound for a population mean. Complete process times include every own failed attempt and inference look.','rlrrrr')
    rr=[]
    for d in (2,4,8):
        for other in ('common-only','relu-menu','quadratic-exact','extra-trees-menu'):
            pp=[r['contrasts'][other] for r in pairs if r['d']==d];rr.append([d,NAMES[other],sum(x['classification']=='relu_less_costly' for x in pp),sum(x['classification']=='relu_more_costly' for x in pp),sum(x['classification']=='identity' for x in pp),sum(x['classification']=='unresolved' for x in pp)])
    table('paired-summary57','Fresh returned-policy cost comparisons','tab:paired-summary57',['$d$','X versus','X lower','X higher','Identity','Unresolved'],rr,'Each row covers both targets and all three training seeds. A negative paired difference favors X. Identity means equal complete policy arrays on the same observation partition, not merely overlapping intervals. Other unresolved intervals are not equivalence findings. The fresh comparison stream is independent of the corresponding stopping information under the sampling model.','rlrrrr')
    rr=[]
    for d in (2,4,8):
        for mode in ('relu-exact','quadratic-exact'):
            pp=[r for r in rows if r['d']==d and r['mode']==mode];sts=[z for r in pp for z in r['stages']];dates=[v for z in sts for v in z['dates']]
            rr.append([d,NAMES[mode],sum(z['grid_regret_positive'] for z in sts),sum(z['extra_witness_changes'] for z in dates),sum(z['upper_strict_improvements'] for z in dates),sum(z['root_isolations'] for z in sts),sum(z['exact_candidate_evaluations'] for z in sts)])
    table('attribution57','Objective search and whole-cell deployment attribution','tab:attribution57',['$d$','Mode','$\kappa>0$','Changed','Stricter','Roots','Values'],rr,'Counts are cell--attempt records across all own target services, including repeated reconstruction at the other target; they are not independent economic observations. Positive optimization loss refers to the nonterminal menu witness compared with the exact lattice witness. Changed and stricter counts remove only the extra algebraic proposal while retaining the shared verifier. Root and value counts include the common terminal solver, which is not credited as a neural-specific contribution.','rlrrrrr')
    rr=[]
    for r in grouped:
        if r['target']=='4/5':rr.append([f"{r['d']}/{r['T']}",NAMES[r['mode']],num(r['fit_median']),num(r['search_median']),num(r['verify_median']),num(r['infer_median']),r['bytes_max'],r['rss_max']])
    table('components57','Recorded work components at the twenty-percent target','tab:components57',['$d/T$','Mode','Fit (s)','Search (s)','Verify (s)','Infer (s)','Bytes','RSS (KiB)'],rr,'Components sum within a run, but their separate medians need not sum to the median complete process time. They exclude some serialization and process overhead that is included in the complete clock. Bytes and RSS are maxima across the three runs. Cross-task runners are not treated as a controlled hardware-scaling regression.','rlrrrrrr',True)
    rr=[];econ=[]
    for r in rows:
        z=r['stages'][-1];rr.append([ident(r),len(r['stages']),z['leaves'],sum(x['paths'] for x in r['stages']),num(r['whole_process_seconds']),'yes' if r['status']=='target_attained' else 'no'])
        econ.append([ident(r),band(z['cost']),band(z['gain']),ep(z['policy_loss_bound_exact'][0])])
    table('registry57','Every prospective target-service return','tab:registry57',['Service','Attempts','Leaves','Paths','Work (s)','Reached'],rr,'Service identifiers encode dimension/horizon, percent-reduction target, mode, and seed index 1--3. Paths sum the final cumulative look in each attempted construction; nested looks are not double-counted. All 90 services are retained, including every budget exhaustion.','lrrrrl',True)
    table('cost-registry57','Every returned policy and its original Bellman account','tab:cost-registry57',['Service','Expected cost','Gain from installed','All-state bound'],econ,'Intervals are outward rounded. The last column is the one-sweep policy-loss bound against the original Bellman optimum, including the old-continuation term, not merely the local greedy gap. The expected-cost target and this conservative uniform bound are different quantities.','lccr',True)
    rr=[]
    for r in pairs:
        for other,v in r['contrasts'].items():rr.append([f"{r['d']}/{r['T']}",10 if r['target']=='9/10' else 20,(57101,57203,57307).index(r['seed'])+1,NAMES[other],band(v['interval']),{'identity':'identity','unresolved':'unresolved','relu_less_costly':'X lower','relu_more_costly':'X higher'}[v['classification']]])
    table('paired-registry57','Every independent validation contrast','tab:paired-registry57',['$d/T$','Target','Seed','X minus','Cost difference','Conclusion'],rr,'Each nonidentity interval comes from 65,536 fresh continuous-bin paths for the five returned policies. Negative values favor X. Full raw endpoint arrays, stream hashes, fitted models and prospective stopping records are deposited.','rrrlcl',True)
    rr=[]
    for r in rows:
        if r['target']!='4/5' or r['seed']!=57101:continue
        for st in r['stages']:
            for z in st['dates']:rr.append([ident(r),st['stage']+1,z['date'],z['changed'],z['extra_witness_changes'],ep(z['candidate_component_upper']),ep(z['cover_component_upper']),ep(z['gap_upper'])])
    table('date-ledger57','Datewise verification for the first declared seed','tab:date-ledger57',['Service','Attempt','Date','Changed','Extra','$U-C$','$C-L$','$U-L$'],rr,'This printed subset uses the first prespecified seed and the twenty-percent target for all modes. Every seed and target is in the machine-readable audit. Each numerical entry is a maximum over leaves; maxima of the first two components need not add to the maximum total gap.','lrrrrrrr',True)
    cls=a['paired_classifications']
    text=(f"The new cohort executes {a['services']} separate prospective target services. Of these, {a['attained']} attain their declared target and {a['budget_exhausted']} return a budget-exhausted safe candidate. The audit regenerates {a['unique_certificate_and_solver_reintegrations']} distinct fitted-model certificate and action-search calculations and checks {a['checked_stopping_looks']} stopping looks. In the trained ReLU-exact services, {a['neural_positive_center_regrets']} nonterminal cell--attempt records have strictly positive menu optimization loss, while the additional algebraic candidate changes {a['neural_extra_witness_cell_decisions']} deployed cell--attempt decisions. These counts refer to the declared service records, not independent samples. Among the 72 fresh paired comparisons with ReLU-exact, {cls['relu_less_costly']} identify lower ReLU-exact cost, {cls['relu_more_costly']} identify higher cost, {cls['identity']} are exact policy identities and {cls['unresolved']} remain unresolved.\n")
    put('tables/outcomes57.tex',text)
    fastest=[]
    for d in (2,4,8):
        eligible=[r for r in grouped if r['d']==d and r['target']=='4/5' and r['attained']==3]
        if eligible:fastest.append(dict(d=d,mode=min(eligible,key=lambda z:z['time_median'])['mode']))
    put('tables/summary57.json',json.dumps(dict(groups=grouped,fastest_observed_median_at20=fastest,paired_classifications=cls,paired_partial_clock_sum=sum(x['seconds_through_endpoints'] for x in pairs)),indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status='generated',services=len(rows),paired_sets=len(pairs),tables=9)))
if __name__=='__main__':main()
