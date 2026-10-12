"""R84 publication tables; exact rational endpoints round outwards."""
from pathlib import Path
from fractions import Fraction as F
import json,re
R=Path(__file__).resolve().parents[1]
MODELS=((8,'relu'),(8,'bernstein'),(16,'relu'),(16,'bernstein'))
METHODS=('original_actionwise_band','complete_menu_band','compatible_band')

def read(p):return json.loads(Path(p).read_text())
def write(p,t):
    p=R/p;p.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix=='.tex' and any(ord(c)<32 and c not in '\n\r\t' for c in t):raise AssertionError('Invalid TeX control character')
    p.write_text(t)
def end(x,lower,d=6):
    x=F(x);s=10**d;v=(x.numerator*s)//x.denominator if lower else -((-x.numerator*s)//x.denominator)
    sign='-' if v<0 else '';v=abs(v);return sign+str(v//s)+'.'+str(v%s).zfill(d)
def band(x):return '['+end(x[0],True)+', '+end(x[1],False)+']'
def name(s):return ('R' if 'relu' in s else 'B')+s.rsplit('-n',1)[1]
def tolerance(s):
    x=F(s)
    return '$0$' if not x else '$2^{-'+str(x.denominator.bit_length()-1)+'}$'
def narrow_interval(value):
    text=str(value)
    match=re.fullmatch(r'\[(-?\d+\.\d+), (-?\d+\.\d+)\]',text)
    if not match:return text
    return r'\shortstack[r]{$['+match[1]+r',$\\$'+match[2]+r']$}'
def table(path,caption,label,heads,rows,note,cols,long=False):
    if long:
        heads=[r'\shortstack[l]{First minus\\second}' if h=='First minus second' else h for h in heads]
        rows=[[narrow_interval(cell) for cell in row] for row in rows]
        note+=' Each interval is displayed on two lines, with its lower endpoint above its upper endpoint; no endpoint digit or catalogue row is omitted.'
    head=' & '.join(heads)+r' \\'+'\n'
    body='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+'\n'
    if long:
        text='{\\small\\setlength{\\tabcolsep}{3pt}\\renewcommand{\\arraystretch}{1.12}\n\\begin{longtable}{'+cols+'}\n\\caption{'+caption+'}\\label{'+label+r'}\\'+'\n\\hline\n'+head+'\\hline\n\\endfirsthead\n\\hline\n'+head+'\\hline\n\\endhead\n'+body+'\\hline\n\\end{longtable}}\n{\\footnotesize '+note+'}\n'
    else:
        text='\\begin{table}[htbp]\n\\centering\n\\caption{'+caption+'}\\label{'+label+'}\n{\\small\\setlength{\\tabcolsep}{3pt}\n\\begin{tabular}{'+cols+'}\n\\hline\n'+head+'\\hline\n'+body+'\\hline\n\\end{tabular}}\n\\par\\smallskip\n{\\footnotesize '+note+'}\n\\end{table}\n'
    write('tables/'+path+'.tex',text)

def main():
    models=[read(R/f'results84/{k}-n{n}.json') for n,k in MODELS]
    transfers=read(R/'results84/transfer.json')['pairwise'];execution=read(R/'results84/summary.json');verify=read(R/'audit/VERIFY84.json');process=read(R/'audit/PROCESS84.json')
    rows=[]
    for r in models:
        t=r['economic'][-1]
        rows.append([name(r['name']),len(r['singletons']),len(r['pairs']),t['active_alternatives'],t['active_conflicts'],band(t['original_actionwise_band']),band(t['compatible_band'])])
    table('compatibility84','Original-law cost deviations at excess qualification objective $2^{-12}$','tab:compatibility84',
        ['Model','Single','Joint','Allowed','Cuts','Actionwise','Compatible'],rows,
        'R and B denote calibrated ReLU and Bernstein readouts; the suffix is the acquisition size in each state coordinate. Bounds concern each optimizer class relative to its attained controller. Single and joint are qualification-problem counts; allowed and cuts apply at the displayed tolerance. Both interval endpoints are rounded outwards. Every tolerance, including unchanged bounds, appears in the appendix.','lrrrrcc')
    rows=[]
    for r in transfers:
        if F(r['extra_objective'])==F(1,4096):rows.append([name(r['first'])+'--'+name(r['second']),band(r['original_actionwise_band']),band(r['compatible_band']),r['sign']])
    table('comparisons84','All paired optimizer-class comparisons at excess objective $2^{-12}$','tab:comparisons84',
        ['First minus second','Actionwise interval','Compatible interval','Sign'],rows,
        'Intervals use the same R80 simultaneous attained-controller cost event and the same original economic law. Positive means that the first controller class has higher cost throughout the certified pair of classes. An interval containing zero remains unresolved. These rows add no fitting attempt or independent observation.','lccr')
    rows=[]
    for r in models:
        for t in r['economic']:
            rows.append([name(r['name']),tolerance(t['extra_objective']),t['active_alternatives'],t['active_conflicts']]+[band(t[m]) for m in METHODS])
    table('all-bounds84','Every declared optimizer-class tolerance and its three nested bounds','tab:all-bounds84',
        ['Model',r'$\epsilon$','Allowed','Cuts','Actionwise','Full menu','Compatible'],rows,
        'Closed weak winner regions retain ties conservatively. Strict qualification inequalities alone exclude actions or joint events; threshold equality is retained. A zero interval follows from the absence of alternative actions in the covered class, not from rounding a small nonzero interval.','lcrrccc',True)
    rows=[]
    for r in transfers:
        rows.append([name(r['first'])+'--'+name(r['second']),tolerance(r['extra_objective']),band(r['original_actionwise_band']),band(r['compatible_band']),r['sign'],'yes' if r['equivalent_at_1_over_256'] else 'no'])
    table('all-comparisons84','Complete simultaneous class-cost catalogue','tab:all-comparisons84',
        ['First minus second',r'$\epsilon$','Actionwise','Compatible','Sign',r'$1/256$ eq.'],rows,
        'Equivalence requires the exact rational interval to be strictly inside the predeclared margin. It is distinct from a signed ranking; both can hold for a small nonzero cost difference. The displayed six-decimal endpoints are descriptive and do not decide a boundary test.','lcccrc',True)
    rows=[]
    for r in models:
        t=execution['phase_seconds'][r['name']]
        rows.append([name(r['name']),len(r['singletons']),len(r['pairs']),f"{t['singleton_seconds']:.3f}",f"{t['pair_seconds']:.3f}",f"{t['economic_seconds']:.3f}",f"{t['total_seconds']:.3f}"])
    table('work84','Incremental certificate work for the completed catalogue','tab:work84',
        ['Model','Single','Joint','Single (s)','Joint (s)','Assign (s)','Total (s)'],rows,
        'Times belong to one recorded ARM execution, not a cross-basis speed experiment or population timing estimate. The complete interpreter boundary is '+f"{process['wall_seconds_through_interpreter_shutdown']:.3f}"+' seconds and includes imports, input reads, all calculations, durable records and shutdown. Its child peak resident set is '+str(process['child_peak_rss_kib'])+' KiB. Previously paid fitting, integration and cost inference retain their original clocks; independent checking and publication overhead have separate records.','lrrrrrr')
    def compact(row):
        return {**{k:row[k] for k in ('first','second','extra_objective','sign','equivalent_at_1_over_256')},'original':band(row[METHODS[0]]),'compatible':band(row[METHODS[2]])}
    gains=[compact(row) for row in transfers if (F(row[METHODS[0]][0])<=0<=F(row[METHODS[0]][1])) and row['sign']!='unresolved']
    rb=next(x for x in transfers if x['first']=='calibrated-relu-n16' and x['second']=='calibrated-bernstein-n16' and F(x['extra_objective'])==F(1,65536))
    bb=next(x for x in transfers if x['first']=='calibrated-bernstein-n8' and x['second']=='calibrated-bernstein-n16' and F(x['extra_objective'])==F(1,4096))
    coarse=models[0]['economic'][-1]
    macros={'FullMenuProblems':str(execution['singleton_certificates']),'JointProblems':str(execution['joint_event_certificates']),
        'ExactInfeasible':str(execution['exact_infeasibility_certificates']),'IndependentInequalities':str(verify['independent_assignment_inequalities']),
        'CoarseReLUBefore':band(coarse[METHODS[0]]),'CoarseReLUAfter':band(coarse[METHODS[2]]),
        'FineBasisAfter':band(rb[METHODS[2]]),'BernsteinResolutionBefore':band(bb[METHODS[0]]),'BernsteinResolutionAfter':band(bb[METHODS[2]]),
        'BernsteinRefinementFee':end(bb[METHODS[2]][0],True),
        'CompleteScientificSeconds':f"{process['wall_seconds_through_interpreter_shutdown']:.3f}"}
    write('tables/macros84.tex','\n'.join('\\providecommand{\\'+k+'}{'+val+'}' for k,val in macros.items())+'\n')
    summary=dict(status='passed',newly_identified_signed_comparisons=gains,macros=macros,model_records=len(models)*6,comparison_records=len(transfers),
        certificate_counts={k:execution[k] for k in ('singleton_certificates','joint_event_certificates','exact_infeasibility_certificates')},
        compatibility_strict_contractions=sum(s['strictly_tighter_compatibility_tolerances'] for s in verify['services']),
        menu_strict_contractions=sum(s['strictly_tighter_winner_tolerances'] for s in verify['services']),
        independently_verified_assignment_inequalities=verify['independent_assignment_inequalities'])
    write('audit/TABLES84.json',json.dumps(summary,indent=2,sort_keys=True)+'\n');print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()
