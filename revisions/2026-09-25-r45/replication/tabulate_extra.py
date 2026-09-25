"""Rebuild the supplementary tables from preserved outputs, without a solver."""
from pathlib import Path
from fractions import Fraction as F
import json, gzip, sys
if hasattr(sys, 'set_int_max_str_digits'): sys.set_int_max_str_digits(0)
ROOT=Path(__file__).resolve().parents[3]
R=Path(__file__).resolve().parents[1]; G=R/'paper/generated'
OLD=ROOT/'revisions/2026-09-25-r43'
def load(p): return json.loads(p.read_text())
def fmt(v):
    v=float(F(v)) if isinstance(v,str) else float(v)
    if v==0: return '0'
    if abs(v)<1e-4 or abs(v)>=1e5:
        a,b=f'{v:.3e}'.split('e'); return rf'${a}\times10^{{{int(b)}}}$'
    return f'{v:.6f}'
def rows(name, data):
    (G/name).write_text('\n'.join(' & '.join(map(str,x))+r' \\' for x in data)+'\n')
def label(n): return n.replace('maintenance','M').replace('inventory','I').replace('queue','Q').replace('tie','T')
def main():
    data=load(R/'results/global_results.json')['records']; progress=[];work=[];statuses=[]
    for x in data:
        for key,m in [('bellman','B'),('aggregate','A')]:
            z=x[key];q=z['summary'];v=z['verification'];s=z['root_status']
            progress.append([x['label'],m,q['nodes'],q['stop'].replace('_',r'\_'),fmt(q['root_gap']),fmt(v['gap'])])
            work.append([x['label'],m,f"{q['seconds']:.3f}",f"{q['lp_seconds']:.3f}",f"{v['seconds']:.3f}",f"{z['proof_bytes']/1024:.1f}"])
            statuses.append([x['label'],m,s['lp_status'],'Yes' if s['primal_available'] else 'No','Yes' if s['dual_available'] else 'No',s['variables']])
    rows('global_progress.tex',progress);rows('global_resources.tex',work);rows('global_root_status.tex',statuses)
    rows('precision_floors.tex',[[label(x['name']),fmt(x['DC']),fmt(x['DJ']),fmt(x['floor_float']),x['width_level'],x['sufficient_full_tree_depth']] for x in load(R/'results/precision_contract.json')['rows']])
    pr=[]
    for line in (OLD/'paper/generated/primary_savings_full.tex').read_text().splitlines():
        z=[v.strip() for v in line.replace(r'\\','').split('&')]
        if len(z)!=7:continue
        t,n,e,lr,ur,sv,rel=z;u=F(ur);s=F(sv);d=u+s
        pr.append([t,n,e,ur,sv,'--' if not d else f'{100*float(s/d):.2f}','--' if not u else f'{100*float(s/u):.2f}'])
    assert len(pr)==42;rows('primary_percentages.tex',pr)
    x=load(OLD/'results/continuum.json');m=json.loads(gzip.decompress((OLD/'proofs/fiber_00_scaled.json.gz').read_bytes()))['model']
    a=max(abs(F(v)) for rr in m['r'] for v in rr);b=max(F(v) for rr in m['k'] for v in rr);c=max(abs(F(v)) for v in m['terminal'])
    accounting=[];errors=[]
    for z in x['integrals']:
        k=z['cells'];used=x['fibers'][::16//k]
        accounting.append([k,len(used),f"{z['gap']:.6f}",f"{float(F(z['weighted_finite_width'])):.6f}",f"{float(F(z['remaining_partition_and_value_change'])):.6f}",f"{sum(y['lp_seconds'] for y in used):.4f}",f"{sum(y['build_seconds']+y['arithmetic_seconds'] for y in used):.4f}",f"{sum(y['check']['seconds'] for y in used):.4f}"])
        errors.append([k,f'{float(a/k):.8f}',f'{float(b/(2*k)):.8f}',f'{float(c/k):.8f}',0])
    rows('fiber_accounting.tex',accounting);rows('fiber_primitive_errors.tex',errors)

    qrows=load(R/'results/quantized_precision_contract.json')['rows']
    rows('quantized_precision.tex',[[label(x['name']),fmt(x['maximum_disadvantage']),fmt(x['floor_float']),x['sufficient_probability_bits'],x['width_level'],x['sufficient_full_tree_depth']] for x in qrows])

    print('Rebuilt additional tables without changing frozen inputs.')
if __name__=='__main__': main()
