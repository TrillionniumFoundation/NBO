"""Regenerate descriptive tables from exact endpoints; never rerun optimization."""
from pathlib import Path
from fractions import Fraction as F
import json,gzip,sys,csv
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1];P=ROOT/'revisions/2026-09-25-r46';O=ROOT/'revisions/2026-09-25-r44';G=R/'paper/generated';G.mkdir(parents=True,exist_ok=True)
def load(p):return json.loads(p.read_text())
def label(n):return n.replace('maintenance','M').replace('inventory','I').replace('queue','Q').replace('tie','T')
def fmt(v):
 v=float(F(v)) if isinstance(v,str) else float(v)
 if v==0:return '0'
 if abs(v)<1e-4 or abs(v)>=1e5:
  a,b=f'{v:.3e}'.split('e');return rf'${a}\times10^{{{int(b)}}}$'
 return f'{v:.6f}'
def rows(n,r):(G/n).write_text('\n'.join(' & '.join(map(str,x))+r' \\' for x in r)+'\n')
names=[f'{family}{i}' for family in ['maintenance','inventory','queue','tie'] for i in range(4)]
main=[];allrows=[];resources=[];intersections=[];dimensions=[];records=[];prices=[];progress=[]
replay=load(R/'results/r46_recheck.json') if (R/'results/r46_recheck.json').exists() else {}
byproof={x['path']:x for x in replay.get('records',replay.get('results',[]))}
for name in names:
 m=load(O/'models'/f'{name}.json');cs=load(P/'results'/f'{name}.json');sr={key:load(P/'results'/f'{name}_{key}.json') for key in ['price_root','price_search']}
 old=[load(O/'results'/name/f'{key}.json') for key in ['bellman','aggregate']];sc=load(O/'results'/name/'scip.json');c,r=cs
 endpoints=[(F(x['lower']),F(x['upper'])) for x in cs+list(sr.values())]+[(F(x['verification']['lower']),F(x['verification']['upper'])) for x in old]
 low=max(x[0] for x in endpoints);up=min([x[1] for x in endpoints]+[F(sc['candidate_verification']['upper'])]);gap=up-low;assert gap>=0
 full=sr['price_search'];q=full['summary'];fwidth=F(full['upper'])-F(full['lower']);met=fwidth<=F(1,1000)
 main.append([label(name),fmt(c['gap']),fmt(r['gap']),fmt(sr['price_root']['summary']['gap']),fmt(fwidth),q['nodes'],'Yes' if met else 'No'])
 intersections.append([label(name),fmt(low),fmt(up),fmt(gap),f'{100*float(gap/up):.4f}' if up else '0','Yes' if gap<=F(1,1000) else 'No'])
 dimensions.append([label(name),m['n'],m['T'],m['m'],r['face_dimension'],r['variables'],r['constraints']])
 for d in cs:
  prices.append([label(name),d['method'],f"{d['lp_seconds']:.4f}",f"{d['certificate_seconds']:.4f}",f"{d['total_seconds']:.4f}",f"{d['proof_bytes']/1024:.2f}"])
 for k,d in sr.items():
  z=d['summary'];progress.append([label(name),'Root' if k=='price_root' else 'Search',z['nodes'],z['stop'].replace('_',r'\_'),fmt(z['root_gap']),fmt(z['gap'])])
  resources.append([label(name),'Root' if k=='price_root' else 'Search',f"{z['seconds']:.3f}",f"{z['lp_seconds']:.3f}",f"{d['proof_bytes']/1024:.1f}",f"{z['maxrss_kib']/1024:.1f}"])
 for d in cs+list(sr.values()):
  z=d.get('summary',{});g=F(d['upper'])-F(d['lower']);allrows.append(dict(case=name,method=d['method'],lower=d['lower'],upper=d['upper'],absolute_width=float(g),relative_width=float(g/F(d['upper'])) if F(d['upper']) else 0,target_met=g<=F(1,1000),nodes=z.get('nodes',0),stop=z.get('stop','price LP proposal'),seconds=d.get('seconds',d.get('total_seconds')),lp_seconds=d.get('lp_seconds',z.get('lp_seconds')),proof_bytes=d['proof_bytes']))
 records.append(dict(case=name,primary=not name.startswith('tie'),full_search_target=met,full_search_nodes=q['nodes'],portfolio_lower=str(low),portfolio_upper=str(up),portfolio_gap=float(gap),portfolio_target=gap<=F(1,1000),price_root_target=F(sr['price_root']['upper'])-F(sr['price_root']['lower'])<=F(1,1000)))
rows('price_summary.tex',main);rows('price_intersections.tex',intersections);rows('price_dimensions.tex',dimensions);rows('price_times.tex',prices);rows('price_progress.tex',progress);rows('price_resources.tex',resources)
with (R/'results/price_results.csv').open('w',newline='') as fh:
 w=csv.DictWriter(fh,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
summary=dict(primary_search_targets=sum(x['full_search_target'] for x in records if x['primary']),tie_search_targets=sum(x['full_search_target'] for x in records if not x['primary']),portfolio_targets=sum(x['portfolio_target'] for x in records),nonroot_search_targets=[x['case'] for x in records if x['full_search_target'] and x['full_search_nodes']>1])
(R/'results/price_summary.json').write_text(json.dumps(dict(summary=summary,records=records),indent=2)+'\n')
dec=load(P/'results/price_gap_decomposition.json');rows('gap_decomposition.tex',[[label(x['name']),fmt(x['initial_complementarity']),fmt(x['action_slack']),fmt(x['price_flow_slack']),fmt(x['nonnegative_cost_improvement']),fmt(x['gap'])] for x in dec])
witness=load(R/'results/witness_audit.json');ind=load(R/'results/independent_witness.json');wr=[];ws=[]
for b in [16,24,32,40]:
 xs=[x for x in witness if x['bits']==b];vs=[x for x in ind['results'] if x['bits']==b]
 ws.append([b,len(xs),sum(x['target_met'] for x in xs),sum(x['guard_passed'] for x in xs),fmt(max(x['actual_lower_loss'] for x in xs)),fmt(max(x['lower_budget'] for x in xs)),f"{sum(x['total_seconds'] for x in xs):.3f}",f"{sum(x['seconds'] for x in vs):.3f}"])
for x in witness:
 wr.append([label(x['name']),x['bits'],fmt(x['gap']),fmt(x['actual_lower_loss']),fmt(x['lower_budget']),fmt(x['actual_upper_change']),fmt(x['upper_budget']) if x['upper_budget'] is not None else '--'])
rows('witness_summary.tex',ws);rows('witness_full.tex',wr)
print(json.dumps(summary,indent=2));print('All',len(allrows),'price results and',len(witness),'witness outcomes retained.')
