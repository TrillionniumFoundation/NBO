"""Generate every displayed result from exact checked summaries, with outward endpoints."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'paper/generated'
def read(name):return json.loads((ROOT/'results'/name).read_text())
def fmt(x,n=4,direction=None):
    if x is None:return '--'
    q=F(x);s=10**n
    if direction=='lower':i=(q*s).numerator//(q*s).denominator
    elif direction=='upper':i=-((-q*s).numerator//(-q*s).denominator)
    else:return f'{float(q):.{n}f}'
    return f'{i//s}.{i%s:0{n}d}'
def text(x):return str(x).replace('_',r'\_')
def line(values):return ' & '.join(map(str,values))+r' \\'+'\n'
def write(name,lines):(OUT/name).write_text(''.join(lines))
def run():
    OUT.mkdir(parents=True,exist_ok=True);primary=read('primary_combined.json')['outcomes'];finite=read('finite.json')['outcomes'];nonlinear=read('nonlinear_support.json')['outcomes'];diag=read('diagnostics.json')
    scopes=('uniform','high_condition','low_condition');d={s:[r['initial_bounds'][s] for r in primary] for s in scopes}
    strict={s:sum(z['strict_randomized_improvement'] for z in rs) for s,rs in d.items()}
    ex=next(r['initial_bounds']['uniform'] for r in primary if r['T']==12 and r['proposal']=='defer' and r['epsilon']=='1/100')
    nn=next(r for r in nonlinear if r['T']==32 and r['mesh']==256)
    metrics={'PrimaryStrict':strict['uniform'],'PrimaryHighStrict':strict['high_condition'],'PrimaryLowStrict':strict['low_condition'],
        'PrimaryZero':sum(F(r['upper'])==0 for r in d['uniform']),'PrimaryPositive':sum(F(r['upper'])>0 for r in d['uniform']),
        'LocalImproveCount':sum(F(r['local_support_improvement'])>0 for r in d['uniform']),
        'PrimaryExampleLower':fmt(ex['lower'],4,'lower'),'PrimaryExampleUpper':fmt(ex['upper'],4,'upper'),
        'NonlinearFineLower':fmt(nn['restart_support_lower'],4,'lower'),'NonlinearFineUpper':fmt(nn['upper'],4,'upper'),
        'NonlinearFineRelative':fmt(100*F(nn['relative_gap']),2),
        'FinitePositiveClosed':sum(r['closed'] and F(r['upper'])>0 and r['order']=='verified_McCormick' for r in finite),
        'FiniteZero':sum(F(r['upper'])==0 and r['order']=='verified_McCormick' for r in finite)}
    write('metrics.tex',['\\newcommand{\\'+k+'}{'+str(v)+'}\n' for k,v in metrics.items()])
    rows=[];work=[]
    for r in sorted(finite,key=lambda r:(r['seed'],r['order']=='verified_McCormick')):
        method='M' if r['order']=='verified_McCormick' else 'I'
        rows.append(line([r['n'],r['T'],method,fmt(r['lower'],4,'lower'),fmt(r['upper'],4,'upper'),fmt(100*F(r['relative_gap']),2),fmt(r['end_to_end_seconds'],2)]))
        work.append(line([r['seed'],method,fmt(r['gap'],6,'upper'),r['evaluations'],text(r['stop']),fmt(F(r['peak_rss_kib'],1024),1),fmt(r['end_to_end_seconds'],2),'yes' if r['closed'] else 'no']))
    write('finite_rows.tex',rows);write('finite_work.tex',work)
    rows=[]
    for T in (4,8,12):
        rr=[r['initial_bounds']['uniform'] for r in primary if r['T']==T]
        rows.append(line([T,len(rr),sum(F(r['upper'])==0 for r in rr),sum(r['strict_randomized_improvement'] for r in rr),sum(F(r['local_support_improvement'])>0 for r in rr),fmt(100*max(F(r['relative_gap']) for r in rr),2)]))
    write('primary_summary.tex',rows)
    for scope in scopes:
        rows=[]
        for r in primary:
            z=r['initial_bounds'][scope]
            rows.append(line([r['T'],text(r['proposal']),fmt(r['epsilon'],2),fmt(z['lower'],5,'lower'),fmt(z['upper'],5,'upper'),fmt(z['gap'],5,'upper'),fmt(100*F(z['relative_gap']),2),'yes' if z['strict_randomized_improvement'] else 'no']))
        write('primary_'+scope+'.tex',rows)
    rows=[];selected=[];tight=[]
    for r in nonlinear:
        check='full' if (r['T'],r['mesh']) in ((8,64),(32,64)) else 'not independent'
        row=line([r['T'],r['mesh'],fmt(r['restart_support_lower'],4,'lower'),fmt(r['upper'],4,'upper'),fmt(100*F(r['relative_gap']),2) if r['relative_gap'] else '--',check])
        if (r['T'],r['mesh']) in ((8,64),(16,128),(32,64),(32,128),(32,256)):selected.append(row)
        rows.append(line([r['T'],r['mesh'],fmt(r['support_only_lower'],4,'lower'),fmt(r['restart_support_lower'],4,'lower'),fmt(r['upper'],4,'upper'),fmt(100*F(r['relative_gap']),2) if r['relative_gap'] else '--',fmt(F(r['array_payload_bytes'],2**20),1)]))
    write('nonlinear_selected.tex',selected);write('nonlinear_all.tex',rows)
    for r in read('nonlinear_tight_tolerance.json')['outcomes']:
        tight.append(line([r['T'],r['mesh'],fmt(r['epsilon'],2),fmt(r['restart_support_lower'],5,'lower'),fmt(r['operating_witness_width'],5,'upper'),r'uncertified upper']))
    write('nonlinear_tight.tex',tight)
    rows=[]
    for r in diag['deterministic_outcomes']:
        rows.append(line([r['T'],text(r['proposal']),fmt(r['epsilon'],2),fmt(r['gap'],6,'upper'),fmt(100*F(r['gap_over_upper']),2) if r['gap_over_upper'] is not None else '--',fmt(r['necessary_selector_regret'],5,'upper'),fmt(r['necessary_selector_excess'],5,'upper')]))
    write('deterministic_gaps.tex',rows)
    loci=[]
    for e in diag['integrated_not_functionwise']:
        for item in e['full_restart_disagreement']:
            loci.append(r'\paragraph{Restart date '+str(item['date'])+'.}\n')
            for z in item['open_intervals']:
                loci.append('Open interval with endpoints '+r'\path{'+z['left']+'} and '+r'\path{'+z['right']+'}. The difference has slope '+r'\path{'+z['slope']+'} and intercept '+r'\path{'+z['intercept']+'}.\n\n')
            for z in item['isolated_points']:
                loci.append('At '+r'\path{'+z['x']+'}, the separately represented difference is '+r'\path{'+z['difference']+'}.\n\n')
    write('exception_locus.tex',loci)
    rows=[]
    for r in diag['local_lp_inherited']['outcomes']:
        rows.append(line([text(r['witness']),fmt(r['epsilon'],2),str(r['tolerance']).replace('/',r'/'),r['whole_cells_verified'],fmt(F(r['continuous_local_upper'])-F(r['continuous_local_lower']),6,'upper'),fmt(r['seconds'],2)]))
    write('local_work.tex',rows)
    (ROOT/'results/paper_metrics.json').write_text(json.dumps(metrics,sort_keys=True,indent=2)+'\n')
    print(json.dumps(metrics,indent=2))
if __name__=='__main__':run()
