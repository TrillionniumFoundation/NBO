"""Rebuild publication tables only from audited R69 records."""
from pathlib import Path
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
from fractions import Fraction as F
import json,statistics
R=Path(__file__).resolve().parents[1]
METHOD={'adaptive':'A','upper-minimizer':'U','hat-relu':'H','bernstein4':'B','label-relu':'L','quadratic':'Q','r67-relu':'R','simplicial':'S','uniform':'U','hat-vector':'H','quadratic-vector':'Q'}
def read(name):return json.loads((R/'audit'/name).read_text())
def put(name,text):
    if any(ord(x)<32 and x not in '\n\r\t' for x in text):raise ValueError('Nonprinting character: '+name)
    p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def fmt(x,n=3):return f'{x:.{n}f}'
def end(x,lower,n=6):return format(Decimal.from_float(float(x)).quantize(Decimal(10)**(-n),rounding=ROUND_FLOOR if lower else ROUND_CEILING),'f')
def band(a,n=6):return '['+end(a[0],True,n)+', '+end(a[1],False,n)+']'
def ran(values,n=0):
    lo,hi=min(values),max(values)
    return fmt(lo,n) if lo==hi else fmt(lo,n)+'--'+fmt(hi,n)
def table(name,caption,heads,rows,note,cols=None,long=False):
    cols=cols or 'l'+'r'*(len(heads)-1);label='tab:'+name
    if long:
        text='\\begingroup\\small\\setlength{\\tabcolsep}{3pt}\n\\begin{longtable}{'+cols+'}\n\\caption{'+caption+'}\\label{'+label+'}\\\\\n\\hline\n'+' & '.join(heads)+r' \\'+'\n\\hline\\endfirsthead\n\\hline\n'+' & '.join(heads)+r' \\'+'\n\\hline\\endhead\n'
        text+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+'\n\\hline\n\\end{longtable}\\endgroup\n{\\footnotesize '+note+'}\\par\n'
    else:
        text='\\begin{table}[htbp]\n\\centering\\caption{'+caption+'}\\label{'+label+'}\n{\\small\\setlength{\\tabcolsep}{3pt}\n\\begin{tabular}{'+cols+'}\n\\hline\n'+' & '.join(heads)+r' \\'+'\n\\hline\n'
        text+='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+'\n\\hline\\end{tabular}}\n\\par\\smallskip{\\footnotesize '+note+'}\n\\end{table}\n'
    put('tables/'+name+'.tex',text)
def main():
    s=read('SUMMARY70.json');a=read('RESULT_AUDIT70.json');d=read('DETAILS70.json');cat=read('CATALOGUE70.json')['rows']
    rows=[]
    for x in s['cold']:
        rows.append([f"{x['d']},{x['T']}",METHOD[x['kind']],x['n'],ran(x['q_queries']),fmt(x['seconds_median']),band(x['seconds_range'],3)])
    table('cold70','Complete cold-start services at a common information budget',['$(d,T)$','Rule','Processes','Policy queries','Median (s)','Range (s)'],rows,
        'A: adaptive; U: upper-chord minimizer; H: certificate-aware hat--ReLU; B: certificate-aware Bernstein; L: label-loss hat--ReLU; Q: quadratic. Queries concern the policy workload; training and validation queries are additional. Four process repetitions per seed are descriptive clocks, not independent fits or confidence bounds. All complete times include launch and shutdown.','lcrrcc')
    rows=[]
    for x in s['reuse']:
        stable=sum(z is not None for z in x['stable_crossings'])
        rows.append([f"{x['d']},{x['T']}",METHOD[x['kind']],ran(x['q_queries']),fmt(x['seconds_median']),band(x['seconds_range'],3),f"{x['wins']}/{x['n']}" if x['kind']!='adaptive' else '--',f"{stable}/{x['n']}" if x['kind']!='adaptive' else '--'])
    table('reuse70','Sixty-four-block prospective reuse',['$(d,T)$','Rule','Policy queries','Median (s)','Range (s)','Wins','Stable'],rows,
        'A complete-time win is relative to the adaptive process with the same repetition index. Stable means an observed cumulative crossing by index 48 that persists through index 63. The last summary and shutdown belong to complete clocks, not prefix clocks. The stale identity at index 16 is declined in every process. The same adaptive repetition is shared across matched seeds; these comparisons are not independent trials.','lcrcccc')
    rows=[];inference_machine=[]
    for x in s['inference']:
        for name,z in x['centered'].items():
            first,second=name.split('-minus-')
            rows.append([f"{x['spec']['d']},{x['spec']['T']}",METHOD[first]+'--'+METHOD[second],band(z['interval']),end(z['mean_numerical_width'],False),end(z['sampling_radius'],False),'Yes' if z['equivalent_at_margin'] else 'No'])
            inference_machine.append(dict(task=[x['spec']['d'],x['spec']['T']],contrast=name,interval=z['interval'],numerical_allocation_passed=z['mean_numerical_width']/2<=1/512,sampling_allocation_passed=z['sampling_radius']<=1/512,equivalent=z['equivalent_at_margin']))
    table('inference70','Bellman-centered expected policy-cost differences',['$(d,T)$','Pair','Simultaneous interval','Numerical width','Radius','Margin'],rows,
        'Pair first minus second; R is the unchanged R67 ReLU readout at seed 6603. Every task uses 1,024 new common-path rows, not that number per pair. All intervals are outward-rounded. Margin denotes containment in the prospectively specified interval $[-1/256,1/256]$, not strict superiority. The numerical term is a full width; the sampling term is a half-width.','lccrrc')
    rows=[]
    for x in s['vector']:
        q=[z for z in x['q_queries'] if z is not None]
        rows.append([f"{x['d']},{x['T']}",METHOD[x['kind']],x['n'],ran(q),fmt(x['seconds_median'],2),x['rss_max']])
    table('vector70','Two-control and two-innovation complete services',['$(d,T)$','Rule','Processes','Queries','Median (s)','Peak KiB'],rows,
        'S: simplicial; U: largest-edge uniform refinement; H and Q: trained two-output hat and quadratic proposals. Ordinary services have eight continuous-bin paths. Horizon-four services have one path, and H transfers its three-date readout. These are workload records, not precision-designed estimates of population policy costs. Peak memory is the maximum observed resident set within the listed processes.','lcrrrr')
    rows=[]
    for x in d['validation']:
        rows.append([f"{x['d']},{x['T']},{x['r']}",METHOD[x['kind']],str(x['seed'])[-1],x['screen_returns'],fmt(x['mean_root_queries'],2),end(x['validated_root_upper'],False,3),x['descendant_queries']])
    table('validation70','Independent-context work-loss validation',['$(d,T,r)$','Rule','Seed','Returns','Root mean','Upper','All recovery queries'],rows,
        'Each row has 256 new contexts; seed suffix 1 or 2 denotes 6901 or 6902. The upper bound is independently recomputed from an exact sample sum and an outward radius. It applies to the declared complete-action mesh recovery and context law, not automatically to an adaptive on-policy stream. Recovery-query totals include descendants.','lcrrrrr',True)
    unique={}
    for x in d['training']:
        unique[(x['d'],x['T'],x['kind'],x['seed'],x['r'])]=x
    rows=[]
    for key,x in sorted(unique.items()):
        rows.append([f"{x['d']},{x['T']},{x['r']}",METHOD[x['kind']],str(x['seed'])[-1],x['coefficient_count'],f"{x['value']:.3g}",f"{x['dual_gap']:.3g}",f"{x['work_upper']:.3g}"])
    table('training70','Achieved convex readout certificates',['$(d,T,r)$','Rule','Seed','Weights','$F(w)$','$D(w)$',r'$F(w)/\tau^2$'],rows,
        'These are achieved objective and optimization-gap values, not optimizer flags or hidden-layer convergence claims. The complete rational fractions are retained in DETAILS70.json. Repeated services of the same readout are listed once here and remain separately charged in their receipts.','lcrrrrr',True)
    rows=[]
    for x in s['inference']:
        for kind,z in x['arms'].items():
            rows.append([f"{x['spec']['d']},{x['spec']['T']}",METHOD[kind],z['evaluation_q_queries'],fmt(z['seconds'],2),f"{z['conditional_mean']:.3g}",f"{z['bin_mean']:.2g}",z['ambiguous_paths']])
    table('precision-work70','Paid inference work and raw enclosure components',['$(d,T)$','Rule','Evaluator queries','Arm (s)','Conditional','State-bin','Ambiguous'],rows,
        'Component columns are mean full widths before valid regret-range intersections. They do not add to the final narrower contrast width. Arm clocks are internal diagnostics; complete shared inference is charged as a whole: '+', '.join(fmt(x['seconds'],2)+' seconds' for x in s['inference'])+'. State-bin widths include propagated arithmetic. No acquisition ambiguity is discarded.','lcrrrrr')
    rows=[];economic=[]
    for x in s['inference']:
        dim,T=x['spec']['d'],x['spec']['T']
        for kind in ('hat-relu','bernstein4'):
            cost=x['centered']['adaptive-minus-'+kind]['interval'];upper=-cost[0]
            for rep in range(4):
                old=next(z for z in cat if z['spec']['group']=='reuse' and (z['spec']['d'],z['spec']['T'],z['spec']['kind'],z['spec']['repeat'])==(dim,T,'adaptive',rep))
                new=next(z for z in cat if z['spec']['group']=='reuse' and (z['spec']['d'],z['spec']['T'],z['spec']['kind'],z['spec']['seed'],z['spec']['repeat'])==(dim,T,kind,6901,rep))
                saving=old['seconds']-new['seconds'];threshold=504*upper/saving if saving>0 else None
                economic.append(dict(d=dim,T=T,kind=kind,repeat=rep,saving=saving,qualification_seconds=x['seconds'],qualification_adjusted_saving=saving-x['seconds'],policy_cost_upper=upper,multiplier=504,fee_zero_compute_price_ratio_threshold=threshold,scope='Conditional on the same numerical callable policy; model-array matching alone does not establish cross-platform policy identity. Observed clocks are not future runtime bounds.'))
                rows.append([f'{dim},{T}',METHOD[kind],rep,fmt(saving,3),end(504*upper,False,4),'--' if threshold is None else end(threshold,False,4)])
    table('adoption70','Conditional reuse-stage adoption thresholds',['$(d,T)$','Rule','Repeat','Saving (s)','Loss upper','$p/v$ threshold'],rows,
        'Seed 6901; zero incremental installation fee and common or previously paid qualification. The loss upper is 504 times the corresponding policy-cost upper endpoint. A displayed positive-saving threshold describes the adoption region only when the numerical callable policy is the one evaluated by inference. Saved parameter equality is checked, but cross-platform numerical equality is an additional requirement. A dash means no positive work saving in that matched observation. Newly purchased qualification work must be added before claiming a first-purchase saving. Prices are declared inputs, not estimated currency values.','lcrrrr',True)
    put('audit/TABLES70.json',json.dumps(dict(status='passed',inference=inference_machine,economic=economic,training_unique=len(unique),validation_rows=len(d['validation'])),indent=2,sort_keys=True)+'\n')
    small={kind:sorted((x for x in d['validation'] if x['d']==2 and x['T']==2 and x['kind']==kind),key=lambda x:x['seed']) for kind in ('hat-relu','bernstein4')}
    counts=lambda kind:' and '.join(str(x['screen_returns']) for x in small[kind])
    maxgap=max(F(x['dual_gap_exact']) for x in unique.values())
    if maxgap>F(1,10**7):raise AssertionError('Displayed readout gap bound')
    paragraph='At a fixed purchased-information and coefficient budget, the hat--ReLU readouts close '+counts('hat-relu')+' of 256 small-task validation contexts for the two seeds, compared with '+counts('bernstein4')+' for Bernstein. The achieved exact box dual gaps are at most $10^{-7}$ across the certificate-aware catalogue. This is a method-specific improvement in the declared context screen, not a uniform complete-runtime advantage. All methods and both tasks remain in the supplementary validation table.\n'
    put('tables/screen-findings70.tex',paragraph)
    print(json.dumps(dict(tables=8,equivalent=sum(x['equivalent'] for x in inference_machine),all_precision_allocations_met=all(x['sampling_allocation_passed'] and x['numerical_allocation_passed'] for x in inference_machine),vector=s['vector']),indent=2))
if __name__=='__main__':main()
