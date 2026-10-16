"""R77 publication tables derived only from frozen, replayed records."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
import json
R=Path(__file__).resolve().parents[1]
LABEL={'zero':'Zero','relu-n8':'R8','bernstein-n8':'B8','relu-n16':'R16','bernstein-n16':'B16'}
NAMES=tuple(LABEL)

def read(p):return json.loads(Path(p).read_text())
def put(name,text):
    if any(ord(c)<32 and c not in '\n\r\t' for c in text):raise AssertionError('Control character in publication text')
    path=R/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
def decimal(x,upper=True,places=6):
    x=F(x)
    with localcontext() as ctx:
        ctx.prec=100
        value=Decimal(x.numerator)/Decimal(x.denominator)
        return format(value.quantize(Decimal(10)**(-places),rounding=ROUND_CEILING if upper else ROUND_FLOOR),'f')
def interval(record,places=6):
    lo,hi=record['interval_exact'];return '['+decimal(lo,False,places)+', '+decimal(hi,True,places)+']'
def tag(key):
    a,b=key.split('-minus-');return LABEL[a]+' $-$ '+LABEL[b]
def table(name,caption,label,headers,rows,note,cols=None,long=False):
    cols=cols or 'l'+'r'*(len(headers)-1);head=' & '.join(headers)+r' \\'+'\n'
    body='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
    if long:
        text=r'{\small\setlength{\tabcolsep}{4pt}'+'\n'+r'\begin{longtable}{'+cols+'}\n'+r'\caption{'+caption+'}'+r'\label{'+label+r'}\\'+'\n'+r'\toprule'+'\n'+head+r'\midrule\endfirsthead'+'\n'+r'\toprule'+'\n'+head+r'\midrule\endhead'+'\n'+body+'\n'+r'\bottomrule\end{longtable}}'+'\n'+r'\noindent{\footnotesize '+note+'}\n'
    else:
        text=r'\begin{table}[htbp]\centering'+'\n'+r'\caption{'+caption+'}'+r'\label{'+label+'}\n'+r'{\small\setlength{\tabcolsep}{4pt}\begin{tabular}{'+cols+'}\n'+r'\toprule'+'\n'+head+r'\midrule'+'\n'+body+'\n'+r'\bottomrule\end{tabular}}'+'\n'+r'\par\smallskip{\footnotesize '+note+'}\n'+r'\end{table}'+'\n'
    put('tables/'+name+'.tex',text)

def main():
    summary=read(R/'results77/summary.json');receipt=read(R/'audit/SERVICE_RECEIPT77.json')
    if summary['status']!='passed' or receipt['returncode']!=0:raise AssertionError('Incomplete economic calculation')
    data=summary['inference'];conditional=data['conditional'];rows=[]
    for name in NAMES:
        gain='--' if name=='zero' else interval(conditional['contrasts']['zero-minus-'+name])
        rows.append([LABEL[name],interval(conditional['costs'][name]),gain])
    table('cost77','Original-law costs of the constructed controllers','tab:cost77',
        ['Controller','Expected cost','Gain over zero incumbent'],rows,
        'R and B denote the original nine-coefficient ReLU and Bernstein constructions; the number is the coordinate cover size. All policies are frozen before the new evaluation rows. The displayed observations integrate the last innovation analytically without changing expected cost. Endpoints are rounded outward. Paired gain intervals, not differences of marginal cost intervals, determine gain signs.','lcc')
    comparisons=('relu-n8-minus-bernstein-n8','relu-n16-minus-bernstein-n16','relu-n8-minus-relu-n16','bernstein-n8-minus-bernstein-n16')
    rows=[]
    for key in comparisons:
        v=conditional['contrasts'][key]
        rows.append([tag(key),interval(v),decimal(v['width_exact'],True),'Yes' if v['equivalence_at_margin'] else 'No'])
    table('pairs77','Paired feature and acquisition comparisons','tab:pairs77',
        ['First minus second','Expected-cost difference','Full width','Equivalent'],rows,
        'A negative interval identifies lower cost for the first controller. Equivalence is determined from exact endpoints at the predeclared two-sided margin 1/256. The separate full-width target is also 1/256. Matched-basis comparisons hold the acquisition contract fixed; cross-resolution comparisons do not.','lcrc')
    allpairs=[v for est in data.values() for v in est['contrasts'].values()]
    passed=sum(v['paired_width_target_passed'] for v in allpairs);equiv=sum(v['equivalence_at_margin'] for v in allpairs)
    gains={key:v for key,v in conditional['contrasts'].items() if key.startswith('zero-minus-')}
    positive=[(key,v) for key,v in gains.items() if F(v['interval_exact'][0])>0]
    smallest=min(F(v['width_exact']) for v in allpairs);largest=max(F(v['width_exact']) for v in allpairs)
    sentences=[r'\paragraph{Outcomes of the fixed precision design.}',
        'Across both estimators, '+str(passed)+' of the twenty paired intervals meet the declared full-width target. Their widths range from '+decimal(smallest,False)+' to '+decimal(largest,True)+'. Exactly '+str(equiv)+' meet the separate equivalence criterion. Neither a failed width target nor a failed equivalence comparison is omitted.']
    if positive:
        sentences.append('The conditionally integrated comparisons identify a positive gain over the zero-investment incumbent for '+str(len(positive))+' of the four constructed policies. These are gains of complete implemented controllers, not reductions in a qualification objective.')
    else:sentences.append('The conditionally integrated comparisons do not identify a positive gain over the zero-investment incumbent at the stated joint coverage. The numerical intervals, including the unresolved signs, are retained in full.')
    matched=[conditional['contrasts'][key] for key in comparisons[:2]]
    low=sum(v['sign']=='negative' for v in matched);high=sum(v['sign']=='positive' for v in matched);unresolved=2-low-high
    sentences.append('At the two matched acquisition resolutions, the ReLU-minus-Bernstein comparisons identify '+str(low)+' lower-cost ReLU outcomes, '+str(high)+' higher-cost outcomes, and '+str(unresolved)+' unresolved signs. This finite comparison is not a universal representation ranking.')
    put('tables/findings77.tex','\n\n'.join(sentences)+'\n')
    rows=[]
    for est in ('cash','conditional'):
        for name in NAMES:
            v=data[est]['costs'][name]
            rows.append(['C' if est=='cash' else 'Y',LABEL[name],interval(v),decimal(v['width_exact'],True)])
    table('all-costs77','Every marginal original-law cost interval','tab:all-costs77',
        ['Observation','Controller','Cost interval','Full width'],rows,
        'C is full cash cost and Y integrates the last innovation. Both estimate the same policy cost. All ten intervals belong to the declared joint family. Marginal intervals need not meet the target assigned to paired differences.','llcr',True)
    rows=[]
    for est in ('cash','conditional'):
        for key,v in data[est]['contrasts'].items():
            rows.append(['C' if est=='cash' else 'Y',tag(key),interval(v),v['sign'],'Yes' if v['paired_width_target_passed'] else 'No','Yes' if v['equivalence_at_margin'] else 'No'])
    table('all-pairs77','Every paired policy-cost interval and declared decision','tab:all-pairs77',
        ['Obs.','First minus second','Difference interval','Sign','Width','Equiv.'],rows,
        'Width and Equiv. are exact-endpoint decisions at the separate predeclared thresholds, each 1/256. Positive zero-minus-controller means a gain from replacing the zero incumbent. Common-path dependence is retained; the twenty intervals are not twenty independent samples.','llclcc',True)
    rows=[]
    for est in ('cash','conditional'):
        for key,v in data[est]['contrasts'].items():
            p=v['width_decomposition']
            rows.append(['C' if est=='cash' else 'Y',tag(key),decimal(p['numerical'],True,9),decimal(p['sampling_variance'],True,6),decimal(p['finite_support'],True,6)])
    table('width77','Exact sources of paired interval width','tab:width77',
        ['Obs.','Contrast','Numerical','Variance terms','Support term'],rows,
        'Unrounded components sum exactly to the recorded width. The numerical term is the mean retained full-bin endpoint width, including acquisition and arithmetic effects; these are not asserted to be separately additive causes. Variance terms use exact endpoint sample variances and upward rational square roots.','llrrr',True)
    rows=[]
    for name in NAMES:
        v=summary['work'][name];construction='--' if name=='zero' else format(summary['controller_metadata'][name]['construction_seconds'],'.3f')
        rows.append([LABEL[name],construction,format(v['float_evaluation_seconds'],'.3f'),format(v['integer_evaluation_seconds'],'.3f'),format(v['seconds_through_output'],'.3f'),v['integer_acquisition_ambiguities']])
    table('work77','Measured construction and complete independent evaluation phases','tab:work77',
        ['Policy','Prior build (s)','Float (s)','Integer (s)','Through output (s)','Ambiguities'],rows,
        'Prior construction clocks are inherited unchanged and include the original matched fitting ablations. Through-output time includes lookup preparation, both evaluators, exact midpoint checks and compressed arrays. The two evaluation columns are only components of that total. Ambiguities count endpoint rectangles spanning more than one actor cell. These are inference-service timings, not new generator cold-start competitions.','lrrrrr')
    worktext=r'\paragraph{The parent process.}'+'\nThe complete five-controller service took '+format(receipt['complete_process_seconds'],'.3f')+' seconds from process launch through shutdown and log flushing. Exact statistical postprocessing took '+format(summary['statistical_inference_seconds'],'.3f')+' seconds; process peak resident memory was '+str(summary['peak_rss_kib'])+' KiB. Each arithmetic implementation evaluated '+str(summary['rows']*len(NAMES))+' complete policy trajectories, and the additional rational midpoint check covered '+str(sum(v['exact_midpoint_checks'] for v in summary['work'].values()))+' predetermined policy trajectories. The recorded number of original-optimum value queries is zero. CPU frequency is observed where available, not claimed locked.\n'
    put('tables/work-summary77.tex',worktext)
    report=dict(status='passed',source_summary=summary['source_freeze_sha256'],paired_intervals=20,width_target_passed=passed,equivalence_passed=equiv,
        identified_gains_against_zero=len(positive),matched_relu_lower=low,matched_relu_higher=high,matched_unresolved=unresolved,
        min_paired_width=str(smallest),max_paired_width=str(largest),complete_process_seconds=receipt['complete_process_seconds'])
    put('audit/TABLES77.json',json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
