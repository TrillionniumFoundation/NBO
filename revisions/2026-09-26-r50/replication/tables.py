"""Generate every numerical table directly from retained exact result records."""
from pathlib import Path
from fractions import Fraction as F
import json,gzip,statistics,csv,hashlib
ROOT=Path(__file__).resolve().parent.parent;REPO=ROOT.parents[1];GEN=ROOT/'paper/generated';GEN.mkdir(parents=True,exist_ok=True)

def fl(x):return float(F(str(x)))
def num(x):return f'{fl(x):.6f}'
def low(x):return f'{(F(str(x))*10**6).__floor__()/10**6:.6f}'
def high(x):return f'{(F(str(x))*10**6).__ceil__()/10**6:.6f}'
def sci(x):return f'{fl(x):.3g}'
def wr(name,rows): (GEN/name).write_text('\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+'\n')
def main():
 d=[json.loads(p.read_text()) for p in sorted((ROOT/'results').glob('*-highs-*.json'))];finite=[json.loads(p.read_text()) for p in sorted((ROOT/'results').glob('finite-*.json'))];price=[json.loads(p.read_text()) for p in sorted((ROOT/'results').glob('price-audit-*.json'))]
 assert len(d)==78 and len(finite)==48 and len(price)==8
 from evaluate import CONFIGS
 rows=[]
 for key,_ in CONFIGS:
  z=[v for v in d if v['factor']==key];ds=[v for v in z if v['method']=='highs-ds'];ip=[v for v in z if v['method']=='highs-ipm']
  rows.append([key.replace('_',r'\_'),f"{sum(v['target_met'] for v in ds)}/3",f"{sum(v['target_met'] for v in ip)}/3",max(v['N'] for v in z),sci(max(fl(v['width']) for v in z)),f"{statistics.median(v['all_in_seconds'] for v in ds):.3f}",f"{statistics.median(v['all_in_seconds'] for v in ip):.3f}",f"{max(v['peak_mib'] for v in z):.1f}"])
 wr('diffuse_factors.tex',rows)
 wr('diffuse_all.tex',[[v['case'],v['method'].replace('highs-',''),v['N'],low(v['lower']),high(v['upper']),sci(v['width']),f"{v['all_in_seconds']:.3f}",f"{v['proof_bytes']/1024:.1f}"] for v in d])
 wr('diffuse_economic.tex',[[v['case'],num(v['preferred_policy_cost']),num(v['certified_saving_lower']),f"{100*fl(v['relative_width']):.4f}",f"{100*fl(v['normalized_decision_loss']):.4f}"] for v in d if v['method']=='highs-ds'])
 cases=sorted(set(v['case'] for v in finite));idx={(v['case'],v['method'],int(v['budget_seconds'])):v for v in finite}
 wr('finite_compare.tex',[[c,*[sci(idx[c,m,b]['width']) for b in [2,8] for m in ['price','budget']],f"{idx[c,'budget',8]['budget_dimension']}/{idx[c,'budget',8]['probability_dimension']}"] for c in cases])
 wr('finite_all.tex',[[v['case'],v['method'],int(v['budget_seconds']),low(v['lower']),high(v['upper']),sci(v['width']),f"{v['all_in_seconds']:.2f}",v['nodes'],f"{v['peak_mib']:.1f}"] for v in finite])
 wr('price_audit.tex',[[v['case'],v['masks'],v['exact_occupation_certificates'],v['pruned_masks'],low(v['ideal_lower']),high(v['ideal_upper']),sci(F(v['ideal_upper'])-F(v['ideal_lower']))] for v in price])
 wr('price_caps.tex',[[v['case'],*[sci(c['loss_upper']) for c in v['cap_rows']],f"{v['construction_seconds']+v['verification_seconds']:.2f}"] for v in price])
 old=REPO/'revisions/2026-09-26-r48/results';ar=ROOT/'paper/archive_r48/generated';ar.mkdir(parents=True,exist_ok=True)
 for category,names in [('primary',['warranty0','warranty1','warranty2','inventory0','inventory1','inventory2','queue0','queue1','queue2','ties0','ties1','ties2']),('fleet',['fleet0','fleet1'])]:
  rows=[]
  for c in names:
   p=json.loads((old/f'{c}_price.json').read_text());a=json.loads((old/f'{c}_direct.json').read_text());wid=F(p['upper'])-F(p['lower']);u=F(p['upper']);dw=F(a['upper'])-F(a['lower']);label={'warranty':'W','inventory':'I','queue':'Q','ties':'T','fleet':'F'}[c[:-1]]+c[-1]
   rows.append([label,high(u),sci(dw),sci(wid),f'{100*float(wid/u) if u else 0:.4f}',p['nodes'],str(p['stop']).replace('_',r'\_')])
  wr(f'historical_{category}.tex',rows);(ar/f'{category}_rows.tex').write_text((GEN/f'historical_{category}.tex').read_text())
 # Exact endpoints remain in JSON; CSV is a human-oriented decimal work curve.
 with (ROOT/'results/work_curves.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['case','method','grid_or_nodes','cumulative_seconds','lower','upper','width'])
  for v in d:
   for a in v['trajectory']:w.writerow([v['case'],v['method'],a['N'],a['cumulative_seconds'],fl(a['lower']),fl(a['upper']),fl(a['width'])])
  for v in finite:
   for a in v['trajectory']:
    if 'lower' in a and 'upper' in a:w.writerow([v['case'],v['method']+str(v['budget_seconds']),a.get('nodes',''),a.get('seconds',''),fl(a['lower']),fl(a['upper']),fl(F(a['upper'])-F(a['lower']))])
 stats=dict(diffuse_cases=39,diffuse_runs=len(d),diffuse_target_hits=sum(v['target_met'] for v in d),diffuse_all_in_seconds=sum(v['all_in_seconds'] for v in d),diffuse_max_all_in_seconds=max(v['all_in_seconds'] for v in d),diffuse_width_min=min(fl(v['width']) for v in d),diffuse_width_max=max(fl(v['width']) for v in d),diffuse_max_variables=max(v['lp_variables'] for v in d),diffuse_max_proof_bytes=max(v['proof_bytes'] for v in d),diffuse_max_peak_mib=max(v['peak_mib'] for v in d),diffuse_proofs=sum(len(v['trajectory']) for v in d),finite_runs=len(finite),finite_hits={f'{m}-{b}s':sum(v['target_met'] for v in finite if v['method']==m and int(v['budget_seconds'])==b) for m in ['price','budget'] for b in [2,8]},price_audits=len(price),price_resolved_1e8=sum(F(v['ideal_upper'])-F(v['ideal_lower'])<=F(1,10**8) for v in price),cross_language=json.loads((ROOT/'results/cross-language.json').read_text())['checked'])
 metrics={'DiffuseHits':stats['diffuse_target_hits'],'DiffuseProofs':stats['diffuse_proofs'],'PriceResolved':stats['price_resolved_1e8'],'BudgetTwo':stats['finite_hits']['budget-2s'],'BudgetEight':stats['finite_hits']['budget-8s'],'PriceTwo':stats['finite_hits']['price-2s'],'PriceEight':stats['finite_hits']['price-8s'],'DiffuseSeconds':f"{stats['diffuse_all_in_seconds']:.2f}",'DiffuseMaxVariables':stats['diffuse_max_variables'],'DiffuseMaxMemory':f"{stats['diffuse_max_peak_mib']:.1f}"}
 (GEN/'metrics.tex').write_text(''.join('\\newcommand{\\RFF'+k+'}{'+str(v)+'}\n' for k,v in metrics.items()))
 (ROOT/'SUMMARY.json').write_text(json.dumps(stats,indent=2)+'\n');print(json.dumps(stats,indent=2))
if __name__=='__main__':main()
