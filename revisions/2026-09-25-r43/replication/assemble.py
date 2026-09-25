"""Create publication tables from independently checked rational endpoints."""
from fractions import Fraction as F
from pathlib import Path
import json,math
R=Path(__file__).resolve().parents[1];G=R/'paper/generated'

def dec(x,d=6,up=False):
    x=F(x);den=10**d
    integer=-((-x.numerator*den)//x.denominator) if up else (x.numerator*den)//x.denominator
    sign='-' if integer<0 else '';integer=abs(integer)
    return sign+str(integer//den)+'.'+str(integer%den).zfill(d)
def approx(x,d=3): return f'{float(x):.{d}g}'
def rows(name,lines): (G/name).write_text('\n'.join(' & '.join(map(str,x))+r' \\' for x in lines)+'\n')
def main():
    finite=json.loads((R/'results/finite_suite.json').read_text());scale=json.loads((R/'results/scaling.json').read_text());cont=json.loads((R/'results/continuum.json').read_text())
    assert len(finite)==16 and len(scale)==8 and len(cont['fibers'])==17
    assert all('failure' not in x for x in finite+scale+cont['fibers'])
    lines=[];work=[];constants=[]
    for a in finite:
        lo,hi=F(a['lower']),F(a['upper']);width=hi-lo;status='Cap' if a['lp_status'] else 'Solved'
        lines.append([a['case'][4:],a['n'],a['T'],a['m'],'S' if a['mode']=='scaled' else 'U',dec(lo),dec(hi,up=True),dec(100*width/hi,3,True) if hi else '0',status])
        path=R/'proofs'/(a['case']+'_'+a['mode']+'.json.gz')
        work.append([a['case'][4:],'S' if a['mode']=='scaled' else 'U',a['policy_coordinates'],a['variables'],a['nonzeros'],f"{a['build_seconds']:.3f}",f"{a['lp_seconds']:.3f}",f"{a['arithmetic_seconds']:.3f}",f"{a['check']['seconds']:.3f}",path.stat().st_size])
        if a['mode']=='scaled':
            th=a['theory'];constants.append([a['case'][4:],str(a['epsilon']),approx(F(a['d_min'])),approx(F(a['lplus'])-F(a['lminus'])),approx(F(th['E_D'])),approx(F(th['E_S'])),approx(F(th['exact_LP_width_bound']))])
    rows('controlled_rows.tex',lines);rows('controlled_work.tex',work);rows('controlled_constants.tex',constants)
    sc=[]
    for i in range(0,len(scale),2):
        u,a=scale[i:i+2];w=F(a['upper'])-F(a['lower']);wu=F(u['upper'])-F(u['lower']);ep=F(a['epsilon'])
        sc.append([dec(ep,4),dec(wu,9,True),dec(w,9,True),approx(w/ep**2,5),f"{a['build_seconds']+a['lp_seconds']+a['arithmetic_seconds']:.3f}",f"{a['check']['seconds']:.3f}"])
    rows('scaling_rows.tex',sc)
    ff=[]
    for a in cont['integrals']:
        lo,hi=F(a['lower']),F(a['upper']);ff.append([a['cells'],dec(lo),dec(hi,up=True),dec(100*(hi-lo)/hi,3,True),dec(a['weighted_finite_width'],6,True),dec(a['remaining_partition_and_value_change'],6,True)])
    rows('fiber_rows.tex',ff)
    rows('all_fibers.tex',[[i,dec(F('.01')/(1+F(i,16)),8),dec(a['lower']),dec(a['upper'],up=True),dec(F(a['upper'])-F(a['lower']),9,True),f"{a['check']['seconds']:.3f}"] for i,a in enumerate(cont['fibers'])])
    improved=sum((F(finite[i]['upper'])-F(finite[i]['lower']))-(F(finite[i+1]['upper'])-F(finite[i+1]['lower']))>F(1,10**8) for i in range(0,16,2))
    long=finite[11];small=scale[-1];uu=scale[-2];fi=cont['integrals'][-1]
    metrics=dict(RControlledImproved=str(improved),RControlledCaps=str(sum(a['lp_status']!=0 for a in finite)),RLongLower=dec(long['lower']),RLongUpper=dec(long['upper'],up=True),RLongRelative=dec(100*(F(long['upper'])-F(long['lower']))/F(long['upper']),3,True),RScaleGap=dec(F(small['upper'])-F(small['lower']),9,True),RScaleUnscaled=dec(F(uu['upper'])-F(uu['lower']),9,True),RFiberLower=dec(fi['lower']),RFiberUpper=dec(fi['upper'],up=True),RFiberRelative=dec(100*(F(fi['upper'])-F(fi['lower']))/F(fi['upper']),3,True))
    (G/'r43_metrics.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+v+'}' for k,v in metrics.items())+'\n')
    (R/'results/publication_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
if __name__=='__main__': main()
