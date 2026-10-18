"""Deterministic tables and workload-safe price regions from all executed rows."""
from __future__ import annotations
import pathlib,json,csv,hashlib,statistics,collections,itertools,math,sys
from fractions import Fraction as Q
R=pathlib.Path(__file__).resolve().parents[1]
ARMS=('online','quadratic-ls','quadratic-ca','relu-ls','relu-ca','spline-ls','spline-ca')
LABEL={'online':'Online','quadratic-ls':'Quadratic LS','quadratic-ca':'Quadratic CA','relu-ls':'ReLU LS','relu-ca':'ReLU CA','spline-ls':'Spline LS','spline-ca':'Spline CA'}

def load(p):return json.loads(pathlib.Path(p).read_text())
def dump(p,o):pathlib.Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
def num(v,d=4):return f'{v:.{d}f}'
def run():
    c=load(R/'results97/CAMPAIGN97.json')
    if c.get('status')!='executed' or len(c['configurations'])!=84 or len(c['timings'])!=42:raise AssertionError('Incomplete campaign')
    records={};sha={};stage=collections.defaultdict(lambda:collections.Counter());regions=[];counts=collections.Counter()
    for row in c['configurations']:
        if row['exit_code']!=0:raise AssertionError('Failed cell cannot be excluded')
        p=R/row['path'];a=load(p/'acquisition.json');e=load(p/'evaluation.json')
        with (p/'evaluation.csv').open() as f:data=list(csv.DictReader(f))
        if len(data)!=64:raise AssertionError('Diagnostic rows changed')
        if any(float(x['loss'])>1/256 or float(x['width'])>1/8192 for x in data):raise AssertionError('Unqualified complete service')
        key=(row['index'],row['rank'],row['labels'],row['arm']);records[key]=(row,a,e)
        for name in ('acquisition.json','evaluation.json','evaluation.csv','model.bin'):
            sha[str((p/name).relative_to(R))]=hashlib.sha256((p/name).read_bytes()).hexdigest()
        stage[(row['index'],row['arm'])].update(e['counts']);counts['rows']+=64;counts['rejected']+=e['rejected'];counts['refined']+=e['refined_rows'];counts['rational_fallback']+=e['exact_fallbacks']
        for bx in range(4):
            for by in range(4):
                sub=[z for z in data if min(3,int(4*float(z['x0'])))==bx and min(3,int(4*float(z['x1'])))==by]
                regions.append({'risk_index':row['index'],'rank':row['rank'],'labels':row['labels'],'arm':row['arm'],'x0_bin':bx,'x1_bin':by,'rows':len(sub),
                    'rejected':sum(z['rejected']=='True' for z in sub),'loss_reason':sum(z['loss_reason']=='True' for z in sub),'width_reason':sum(z['width_reason']=='True' for z in sub)})
    if counts['rows']!=5376:raise AssertionError('Full row count failed')
    budget=[]
    for index,rank,labels,kind in itertools.product(range(2),(4,5,6),(256,1024),('quadratic','relu','spline')):
        _,ls,le=records[index,rank,labels,kind+'-ls'];_,ca,ce=records[index,rank,labels,kind+'-ca']
        if ls['fit_record']['selected']!=ca['fit_record']['selected']:raise AssertionError('Readout comparison changed geometry')
        if ls['payload_bytes']!=ca['payload_bytes'] or ls['payload_bytes']!=32*(rank-2):raise AssertionError('Matched payload failed')
        retained=ca['candidate_cover'] if ca['readout_admitted'] else ca['baseline_cover']
        if retained['span']>ls['baseline_cover']['span']:raise AssertionError('Verified selection worsened certificate')
        budget.append({'risk_index':index,'rank':rank,'labels':labels,'family':kind,'payload_bytes':ls['payload_bytes'],
                       'ls_span':ls['baseline_cover']['span'],'ca_span':retained['span'],'ls_rejected':le['rejected'],'ca_rejected':ce['rejected'],
                       'candidate_retained':ca['readout_admitted']})
    lines=[r'\begin{table}[t]',r'\centering\small',r'\caption{Complete-service diagnostics over the fixed rank and label budgets}\label{tab:diagnostics97}',r'\begin{tabular}{llrrrr}\toprule',r'Risk & Service & Proposals & Rejected & Refined & Exact \\ \midrule']
    for index in range(2):
        for arm in ARMS:
            es=[v[2] for k,v in records.items() if k[0]==index and k[3]==arm]
            lines.append(f'{(.5,.75)[index]} & {LABEL[arm]} & 384 & {sum(e["rejected"] for e in es)} & {sum(e["refined_rows"] for e in es)} & {sum(e["exact_fallbacks"] for e in es)} '+r'\\')
    lines += [r'\bottomrule\end{tabular}',r'\par\smallskip\parbox{\linewidth}{\footnotesize Each risk--service row aggregates three design ranks and two training budgets, with 64 states per cell. Rejected first proposals remain in the complete service. These are construction diagnostics, not a new population superiority test.}',r'\end{table}']
    (R/'tables/diagnostics97.tex').write_text('\n'.join(lines)+'\n')
    lines=[r'\begin{longtable}{rrrlrrrr}',r'\caption{All matched-budget residual and admission comparisons}\label{tab:budgets97}\\',r'\toprule $\alpha$ & Rank & Labels & Family & LS span & CA span & LS rej. & CA rej. \\ \midrule\endfirsthead',r'\toprule $\alpha$ & Rank & Labels & Family & LS span & CA span & LS rej. & CA rej. \\ \midrule\endhead']
    for a in budget:lines.append(f'{(.5,.75)[a["risk_index"]]} & {a["rank"]} & {a["labels"]} & {a["family"].capitalize()} & {num(a["ls_span"])} & {num(a["ca_span"])} & {a["ls_rejected"]} & {a["ca_rejected"]} '+r'\\')
    lines += [r'\bottomrule\end{longtable}'];(R/'tables/budgets97.tex').write_text('\n'.join(lines)+'\n')
    clocks={};clines=[r'\begin{table}[t]',r'\centering\small',r'\caption{Measured acquisition brackets and whole-workload clocks}\label{tab:clocks97}',r'\begin{tabular}{llrrr}\toprule',r'Risk & Service & Acquisition bracket & Workload median & Workload range \\ \midrule']
    for index in range(2):
        for arm in ARMS:
            cell,a,e=records[index,6,1024,arm];ts=[q['seconds'] for q in c['timings'] if q['index']==index and q['arm']==arm]
            clocks[index,arm]={'klo':a['acquisition_inside_seconds'],'khi':cell['complete_acquire_and_probe_process_seconds'],'slo':min(ts),'shi':max(ts),'median':statistics.median(ts)}
            x=clocks[index,arm]
            if x['klo']>x['khi']:raise AssertionError('Invalid acquisition bracket')
            clines.append(f'{(.5,.75)[index]} & {LABEL[arm]} & [{num(x["klo"],3)}, {num(x["khi"],3)}] & {num(x["median"],3)} & [{num(x["slo"],3)}, {num(x["shi"],3)}] '+r'\\')
    clines += [r'\bottomrule\end{tabular}',r'\par\smallskip\parbox{\linewidth}{\footnotesize Seconds. Rank six and 1,024 training labels. Acquisition lower endpoint is the timed internal construction; the upper endpoint is its entire fresh process including the subsequent diagnostic probe. Each workload has 32 decisions. Three fresh workload repetitions are descriptive, with frequency uncontrolled. Neither bracket is a statistical confidence interval for future execution.}',r'\end{table}']
    (R/'tables/clocks97.tex').write_text('\n'.join(clines)+'\n')
    prices=[]
    for index,arm,baseline in itertools.product(range(2),ARMS,('online','quadratic-ls')):
        if arm==baseline:continue
        a=clocks[index,arm];b=clocks[index,baseline]
        sminus=Q(b['slo'])-Q(a['shi']);splus=Q(b['shi'])-Q(a['slo'])
        kminus=Q(a['klo'])-Q(b['khi']);kplus=Q(a['khi'])-Q(b['klo'])
        for price,fee,m in itertools.product((Q(0),Q(1,100),Q(1,10),Q(1),Q(10)),(Q(0),Q(1,100),Q(1,10)),(1,10,100,1000,10000)):
            lower=m*(price*sminus-32*Q(1,256))-price*kplus-fee
            upper=m*(price*splus+32*Q(1,256))-price*kminus-fee
            status='adopt' if lower>0 else 'reject' if upper<0 else 'unresolved'
            prices.append({'risk_index':index,'arm':arm,'baseline':baseline,'price':str(price),'fee':str(fee),'workloads':m,'decisions_per_workload':32,
                           'lower':str(lower),'upper':str(upper),'status':status,'interpretation':'conditional on observed clock envelopes; deterministic policy bound, not a pilot confidence interval'})
    pcount=collections.Counter(p['status'] for p in prices)
    summary={'source':c['source'],'counts':dict(counts),'budget_pairs':36,'strict_span_improvements':sum(v['ca_span']<v['ls_span'] for v in budget),
             'price_grid_cells':len(prices),'price_grid_counts':dict(pcount),'budget_rows':budget,'input_sha256':sha,'all_cells_validated':True,
             'clock_warning':'Frequency uncontrolled; ranges descriptive. Internal-to-full-process acquisition brackets are subtracted by interval arithmetic, not upper minus upper.'}
    dump(R/'results97/SUMMARY97.json',summary);dump(R/'results97/PRICE_GRID97.json',prices);dump(R/'results97/STATE_REGIONS97.json',regions)
    dump(R/'results97/OPERATIONS97.json',[{'risk_index':k[0],'arm':k[1],'counts':dict(v)} for k,v in stage.items()])
    text=(r'Across the 84 fixed configurations, all 5,376 complete services meet the unchanged admission criteria. '
          +f'There are {counts["rejected"]:,} rejected first proposals, {counts["refined"]:,} refined rows, and {counts["rational_fallback"]:,} exact-fallback entries. '
          +f'The verified readout rule strictly reduces the whole-domain residual span in {summary["strict_span_improvements"]} of the 36 matched family--budget comparisons. '
          +f'The predeclared price grid contains {len(prices):,} comparisons: {pcount["adopt"]:,} conditional adoption regions, {pcount["reject"]:,} conditional rejection regions, and {pcount["unresolved"]:,} unresolved regions. '
          +r'These counts are sensitivity classifications, not frequencies of economically calibrated opportunities.'+'\n')
    (R/'tables/summary97.tex').write_text(text)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('input_sha256','budget_rows')},indent=2))
if __name__=='__main__':run()
