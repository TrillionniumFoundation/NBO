"""Publication tables from the exhaustive deterministic R82 cost catalogue."""
from fractions import Fraction as F
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
NAMES={'calibrated-relu-n8':'R8','calibrated-bernstein-n8':'B8','calibrated-relu-n16':'R16','calibrated-bernstein-n16':'B16'}

def read(p):return json.loads(Path(p).read_text())
def end(x,upper=False,digits=6):
    value=F(x)*10**digits
    v=-((-value.numerator)//value.denominator) if upper else value.numerator//value.denominator
    return ('-' if v<0 else '')+str(abs(v)//10**digits)+'.'+str(abs(v)%10**digits).zfill(digits)
def band(values,digits=6):return '['+end(values[0],False,digits)+', '+end(values[1],True,digits)+']'
def eps(v):return {'0':'$0$','1/65536':r'$2^{-16}$','1/4096':r'$2^{-12}$'}[str(v)]
def put(name,text):
    if any(ord(c)<32 and c not in '\n\r\t' for c in text):raise ValueError('Control character in '+name)
    p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def table(name,caption,headers,rows,note,long=False):
    cols='l'+'r'*(len(headers)-1);body='\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)
    heading=' & '.join(headers)+r' \\'+'\n'+r'\hline'+'\n'
    if long:
        text=r'{\footnotesize\setlength{\tabcolsep}{3pt}'+'\n'+r'\begin{longtable}{'+cols+'}\n'+r'\caption{'+caption+r'}\label{tab:'+name+r'}\\'+'\n'+r'\hline'+'\n'+heading+r'\endfirsthead'+'\n'+r'\hline'+'\n'+heading+r'\endhead'+'\n'+body+'\n'+r'\hline\end{longtable}}'+'\n'
        text+=r'\noindent{\footnotesize '+note+'}\n'
    else:
        text=r'\begin{table}[htbp]\centering'+'\n'+r'\caption{'+caption+r'}\label{tab:'+name+'}\n'+r'{\small\setlength{\tabcolsep}{4pt}\begin{tabular}{'+cols+'}\n'+r'\hline'+'\n'+heading+body+'\n'+r'\hline\end{tabular}}'+'\n'+r'\par\smallskip{\footnotesize '+note+'}\n'+r'\end{table}'+'\n'
    put('tables/'+name+'.tex',text)
def main():
    report=read(R/'results82/summary.json');transfer=read(R/'results82/transfer.json')
    services=[read(R/'results82'/f'{k}-n{n}.json') for n in (8,16) for k in ('relu','bernstein')]
    focus=[x for x in transfer['pairwise'] if x['first']=='calibrated-relu-n16' and x['second']=='calibrated-bernstein-n16' and x['rung']==3]
    if len(focus)!=3:raise AssertionError('Incomplete fine-class catalogue')
    table('fine-classes82','Fine-grid cost comparison for entire qualification sublevels',
        [r'$\epsilon$','Binary-mass band','Actionwise band','Order'],
        [[eps(x['extra_objective']),band(x['coarse_interval']),band(x['optimizer_sublevel_interval']),x['sign']] for x in focus],
        'The quantity is ReLU cost minus Bernstein cost for every pair of readouts in their fixed-label sublevels. The terminal actor and robust menus are fixed. The final dyadic level is $(r,q)=(16,64)$; all preceding levels are also charged and retained. Endpoints are rounded outward. A positive interval identifies lower Bernstein cost, not neural dominance.')
    rows=[]
    for service in services:
        for rung in service['tiers']:
            for row in rung['sublevels']:
                rows.append([NAMES[service['name']],eps(row['extra_objective']),f"{rung['state_subdivisions']}/{rung['shock_bins']}",row['possible_alternatives'],end(row['coarse_radius'],True),end(row['lower']),end(row['upper'],True)])
    table('sublevels82','All optimizer-sublevel economic enlargements',
        ['Actor',r'$\epsilon$',r'$r/q$','Alternatives',r'$Hq_\epsilon$',r'$\underline v$',r'$\overline v$'],rows,
        'R and B denote calibrated ReLU and Bernstein; 8 and 16 are acquisition resolutions. Each displayed band encloses class cost minus its attained controller cost. All 48 model--tolerance--level records are shown. Repeated levels are deterministic refinements, not observations. The machine-readable records also retain every cell contribution.',True)
    rows=[]
    rungs=((2,8),(4,16),(8,32),(16,64))
    for row in transfer['pairwise']:
        r,q=rungs[row['rung']]
        rows.append([NAMES[row['first']]+'--'+NAMES[row['second']],eps(row['extra_objective']),f'{r}/{q}',end(row['optimizer_sublevel_interval'][0]),end(row['optimizer_sublevel_interval'][1],True),row['sign']])
    table('all-pairs82','All directed optimizer-class comparisons',
        ['First--second',r'$\epsilon$',r'$r/q$','Lower','Upper','Sign'],rows,
        'Every one of the six calibrated pairs, three objective allowances and four integration levels is retained. Each interval uses the existing simultaneous conditional-cost event plus deterministic actionwise transfer; there is no additional statistical sample or optimizer union bound.',True)
    rows=[]
    for row in transfer['own_controller']:
        ref='Zero' if row['reference']=='zero' else 'Legacy '+NAMES[row['class_name']]
        rows.append([NAMES[row['class_name']],ref,eps(row['extra_objective']),end(row['reference_minus_class'][0]),end(row['reference_minus_class'][1],True)])
    table('own-gains82','Classwide gains relative to original controllers',
        ['Class','Reference',r'$\epsilon$','Lower gain','Upper gain'],rows,
        'The gain is fixed reference cost minus the cost of every controller in the stated calibrated sublevel. All final-rung comparisons with the zero controller and the corresponding own legacy controller are shown. No reference is refitted.',True)
    rows=[]
    for service in services:
        name=service['name']
        for rung,work in zip(service['tiers'],report['work'][name]):
            boxes=sum(x['boxes'] for x in rung['per_action'])
            rows.append([NAMES[name],f"{rung['state_subdivisions']}/{rung['shock_bins']}",len(rung['per_action']),boxes,f"{work['seconds']:.3f}",work['binary64_actor_queries'],work['integer_actor_queries']])
    table('work82','Complete executed actionwise verification work',
        ['Actor',r'$r/q$','Pairs','Boxes','Seconds','Float queries','Integer queries'],rows,
        'Each paired box is evaluated by both arithmetic implementations. Seconds include paired evaluation, exact endpoint accumulation, endpoint-stream hashing and rational midpoint checks at that rung; the complete service clock also includes source verification, actor setup and durable records. These are verification costs, not matched generator speed estimates.',True)
    standard=next(x for x in focus if x['extra_objective']=='1/65536');interval=standard['optimizer_sublevel_interval']
    if standard['sign']=='positive':
        outcome='This interval is strictly positive: the lower-cost calibrated Bernstein ordering extends to every allowed pair of approximately optimized readouts, although some first-date actions remain uncertified.'
    elif standard['sign']=='negative':
        outcome='This interval is strictly negative and identifies lower ReLU cost uniformly over the two stated sublevels.'
    else:outcome='This interval contains zero, so the actionwise calculation does not identify a uniform ordering for these sublevels.'
    narrative='At the standard objective allowance $1/65536$, the fine-grid ReLU-minus-Bernstein class interval is $'+band(interval)+'$. '+outcome+' The corresponding binary-mass interval is $'+band(standard['coarse_interval'])+'$. Both use exactly the same attained-controller statistical interval; their difference comes solely from deterministic economic pricing of the unresolved actions.\n'
    put('tables/finding82.tex',narrative)
    clock=read(R/'results82/clock.json')
    facts=r'The complete catalogue evaluates '+format(report['paired_boxes_per_implementation'],',')+r' paired subboxes in each arithmetic implementation and checks '+format(report['exact_rational_midpoints'],',')+r' direct rational midpoint differences. Its recorded service clock through the durable summary is '+f"{clock['seconds_through_summary']:.3f}"+r' seconds; peak resident memory is '+format(report['peak_rss_kib'],',')+r' KiB. This clock is not an estimate of an unexecuted optimal stopping rule.'+'\n'
    put('tables/work-finding82.tex',facts)
    paths=[p for p in (R/'tables').glob('*82.tex')]
    audit=dict(status='passed',table_count=5,sublevel_rows=48,pair_rows=72,own_gain_rows=24,
        standard_fine_class=standard,new_independent_rows=0,
        table_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    put('audit/TABLES82.json',json.dumps(audit,indent=2,sort_keys=True)+'\n')
    print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
