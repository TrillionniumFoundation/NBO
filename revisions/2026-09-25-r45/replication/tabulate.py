"""Deterministic tables from frozen rational endpoints; no solver is run.

SCIP's native dual bounds are presented only as solver-reported numbers.
The best certified intersection uses only independently checked lower bounds
and exact feasible-policy upper endpoints, including SCIP's repaired policy.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
import csv, json, sys, math, hashlib
if hasattr(sys,'set_int_max_str_digits'): sys.set_int_max_str_digits(0)
ROOT=Path(__file__).resolve().parents[3]; R=ROOT/'revisions/2026-09-25-r45'
OLD=ROOT/'revisions/2026-09-25-r44'; GEN=R/'paper/generated'; OUT=R/'results'
GEN.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
def load(p): return json.loads(p.read_text())
def f(v): return float(F(str(v)))
def fmt(v):
    x=f(v)
    if x==0:return '0'
    if abs(x)<1e-4 or abs(x)>=1e5:
        mant,exp=f'{x:.3e}'.split('e');return rf'${mant}\!\times\!10^{{{int(exp)}}}$'
    return f'{x:.6f}' if abs(x)<.01 else f'{x:.4f}'
def rows(name,lines): (GEN/name).write_text('\n'.join(' & '.join(map(str,row))+r' \\' for row in lines)+'\n')
p=load(OLD/'PROTOCOL.json'); names=p['primary_environments']+p['tie_environments']
main=[];work=[];native=[];interval=[];constants=[];records=[]
const=load(OLD/'results/all_model_constants.json')
for name in names:
    model=load(OLD/'models'/f'{name}.json')
    b=load(OLD/'results'/name/'bellman.json');a=load(OLD/'results'/name/'aggregate.json');s=load(OLD/'results'/name/'scip.json')
    lb=max(F(b['verification']['lower']),F(a['verification']['lower']))
    ub=min(F(b['verification']['upper']),F(a['verification']['upper']),F(s['candidate_verification']['upper']))
    gap=ub-lb; met=gap<=F(1,1000)
    assert lb<=ub
    label=name.replace('maintenance','M').replace('inventory','I').replace('queue','Q').replace('tie','T')
    main.append([label,model['n'],model['T'],model['m'],fmt(b['verification']['gap']),fmt(a['verification']['gap']),fmt(gap), 'Yes' if met else 'No'])
    interval.append([label,fmt(lb),fmt(ub),fmt(gap),f'{100*float(gap/ub):.4f}' if ub else '0','Yes' if met else 'No'])
    native.append([label,s['summary']['status'].replace('_',r'\_'),fmt(s['summary']['native_gap']),s['summary']['nodes'],f"{s['summary']['seconds']:.2f}",fmt(gap)])
    for labelmethod,x in [('B',b),('A',a)]:
        q=x['summary'];v=x['verification']
        work.append([label,labelmethod,q['nodes'],q['stop'].replace('_',r'\_'),fmt(q['root_gap']),fmt(v['gap']),f"{q['seconds']:.2f}",f"{v['seconds']:.2f}",f"{x['proof_bytes']/1024:.1f}"])
    c=const[name]
    constants.append([label,'Yes' if c['strict'] else 'No',fmt(f(c['d_min'])),fmt(f(c['lambda_minus'])),fmt(f(c['lambda_plus'])),fmt(f(c['exact_LP_theorem_bound'])) if c['theorem_applies'] else '--'])
    records.append(dict(name=name,label=label,n=model['n'],T=model['T'],m=model['m'],epsilon=model['epsilon'],beta=model['beta'],
       bellman=b,aggregate=a,scip=s,intersection=dict(lower=str(lb),upper=str(ub),gap=float(gap),relative_gap=float(gap/ub) if ub else 0,target='1/1000',target_met=met)))
rows('global_summary.tex',main);rows('global_work.tex',work);rows('native_baseline.tex',native);rows('global_intersections.tex',interval);rows('global_constants.tex',constants)
summary=dict(cases=16,primary_cases=12,near_tie_variants=4,
  bellman_target=sum(x['bellman']['verification']['target_met'] for x in records),
  aggregate_target=sum(x['aggregate']['verification']['target_met'] for x in records),
  intersection_target=sum(x['intersection']['target_met'] for x in records),
  native_scip_target=sum(x['scip']['summary']['native_target_met'] for x in records),
  bellman_narrower=sum(x['bellman']['verification']['gap']<x['aggregate']['verification']['gap'] for x in records),
  aggregate_narrower=sum(x['aggregate']['verification']['gap']<x['bellman']['verification']['gap'] for x in records),
  equal_width=sum(x['aggregate']['verification']['gap']==x['bellman']['verification']['gap'] for x in records),
  bellman_nonroot_target=[x['name'] for x in records if x['bellman']['verification']['target_met'] and x['bellman']['summary']['nodes']>1],
  aggregate_nonroot_target=[x['name'] for x in records if x['aggregate']['verification']['target_met'] and x['aggregate']['summary']['nodes']>1])
(OUT/'global_results.json').write_text(json.dumps(dict(summary=summary,records=records),indent=2)+'\n')
with (OUT/'global_results.csv').open('w',newline='') as fh:
    writer=csv.writer(fh);writer.writerow(['case','n','T','m','method','lower_exact','upper_exact','absolute_width','relative_width','target_met','nodes','stop','search_seconds','archived_check_seconds'])
    for x in records:
        for method in ['bellman','aggregate']:
            d=x[method];v=d['verification'];z=d['summary'];writer.writerow([x['name'],x['n'],x['T'],x['m'],method,v['lower'],v['upper'],v['gap'],v['relative_gap'],v['target_met'],z['nodes'],z['stop'],z['seconds'],v['seconds']])
        v=x['intersection'];writer.writerow([x['name'],x['n'],x['T'],x['m'],'certified_intersection',v['lower'],v['upper'],v['gap'],v['relative_gap'],v['target_met'],'','combined three computations','',''])
# R43 paired root experiments: preserve both individual endpoints and add the intersection.
rootrows=[];rootwork=[];rootconst=[]
for j in range(8):
    ds={m:load(ROOT/'revisions/2026-09-25-r43/results'/f'case{j:02}_{m}.json') for m in ['unscaled','scaled']}
    # Files wrap their metadata under metadata, as stored by the constructor.
    ds={k:(v.get('metadata',v)) for k,v in ds.items()}
    la=max(F(v['lower']) for v in ds.values());ua=min(F(v['upper']) for v in ds.values())
    rootrows.append([f'{j:02}',fmt(ds['unscaled']['gap']),fmt(ds['scaled']['gap']),fmt(ua-la),f'{100*float((ua-la)/ua):.4f}' if ua else '0','Yes' if ua-la<=F(1,1000) else 'No'])
    c=ds['scaled'];rootconst.append([f'{j:02}',fmt(f(c['d_min'])),fmt(f(c['lminus'])),fmt(f(c['lplus']))])
    for m,v in ds.items():
        rootwork.append([f'{j:02}',m,v.get('lp_status','--'),fmt(v['lower']),fmt(v['upper']),fmt(v['gap']),f"{v.get('lp_seconds',0):.3f}"])
rows('r43_intersections.tex',rootrows);rows('r43_root_work.tex',rootwork);rows('r43_constants.tex',rootconst)
# Complete multi-family, seven-allowance diagnostic. The finite arithmetic loss
# is not an exact LP primal-dual gap and is not silently supplied as one.
sc=load(OLD/'results/scaling_diagnostics.json'); sr=[];cr=[];series={};allsc=[]
for x in sc:
    fam=x['family'];eps=x['epsilon'];m=x['mode'];v=x['verification'];c=x['constants'];meta=x['metadata']
    allsc.append(dict(family=fam,epsilon=eps,mode=m,verified_width=v['gap'],constants=c,metadata=meta,verification=v))
    if m!='scaled':continue
    other=next(y for y in sc if y['family']==fam and y['epsilon']==eps and y['mode']=='unscaled')
    sr.append([fam[0].upper(),rf'$10^{{-{round(-math.log10(f(eps)))}}}$',fmt(other['verification']['gap']),fmt(v['gap']),fmt(x['measured_width_over_epsilon_squared']),fmt(f(c['exact_LP_theorem_bound'])) if c['theorem_applies'] else '--'])
    cr.append([fam[0].upper(),rf'$10^{{-{round(-math.log10(f(eps)))}}}$',fmt(f(c['ED_max'])) if c['theorem_applies'] else '--',fmt(f(c['ES0'])) if c['theorem_applies'] else '--',fmt(f(c['DC'])) if c['theorem_applies'] else '--',fmt(f(c['chi'])) if c['theorem_applies'] else '--',fmt(f(c['rho'])) if c['theorem_applies'] else '--',fmt(f(c['repair_term'])) if c['theorem_applies'] else '--'])
    series.setdefault(fam,[]).append((f(eps),v['gap']))
rows('scaling_full.tex',sr);rows('scaling_constants.tex',cr)
slopes=[]
for fam,seq in series.items():
    seq.sort(reverse=True)
    for (e1,w1),(e2,w2) in zip(seq,seq[1:]):
        slopes.append(dict(family=fam,epsilon_from=e1,epsilon_to=e2,width_from=w1,width_to=w2,
             descriptive_secant_slope=math.log(w1/w2)/math.log(e1/e2) if w1>0 and w2>0 else None))
(OUT/'scaling_retabulation.json').write_text(json.dumps(dict(rows=allsc,descriptive_slopes=slopes,interpretation='Descriptive secants, not an estimated universal exponent; exact-LP bound excludes unquantified LP optimality loss.'),indent=2)+'\n')
print(json.dumps(summary,indent=2));print('generated',len(list(GEN.glob('*.tex'))),'tables')
