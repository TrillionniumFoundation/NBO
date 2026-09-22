"""Typeset only recorded outcomes; upper endpoints rounded upward for certificates."""
from __future__ import annotations
from decimal import Decimal,ROUND_CEILING
import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-22-r11';OUT=REV/'paper/tables'
OUT.mkdir(parents=True,exist_ok=True)
def up(x,d=8):return format(Decimal.from_float(float(x)).quantize(Decimal(10)**-d,rounding=ROUND_CEILING),f'.{d}f')
def write(name,lines): (OUT/f'{name}.tex').write_text('\n'.join(lines)+'\n')
def run():
 s=json.loads((REV/'results/accuracy/summary.json').read_text());names={'tracking':'Tracking','mean_reverting':'Mean-reverting','ill_conditioned':'Ill-conditioned'}
 lines=[r'\begin{tabular}{lrrrr}',r'\toprule',r'Case & B: $N=16$ & B: $N=32$ & B: $N=128$ & Adam (400) \\',r'\midrule']
 for case,name in names.items():
  rr=[r for r in s['rows'] if r['case']==case]
  vals=[next(r['absolute_regret'][1] for r in rr if r['method']=='quadratic_Bellman' and r['slabs']==n) for n in [16,32,128]]+[next(r['absolute_regret'][1] for r in rr if r.get('updates')==400)]
  lines.append(name+' & '+' & '.join(up(v) for v in vals)+r' \\')
 write('accuracy',lines+[r'\bottomrule',r'\end{tabular}'])
 lines=[r'\begin{tabular}{llrrr}',r'\toprule',r'Case & Method & $.01$ (sec.) & $.003$ (sec.) & $.001$ (sec.) \\',r'\midrule']
 for case,name in names.items():
  for method,label in [('quadratic_Bellman','B'),('Adam_gain','A')]:
   vals=[]
   for tar in [.01,.003,.001]:
    r=next(v for v in s['matched_accuracy_frontier'] if v['case']==case and v['method']==method and v['target']==tar)
    vals.append(f"{r['first']['cumulative_seconds']:.3f}" if r['attained'] else '---')
   lines.append(name+' & '+label+' & '+' & '.join(vals)+r' \\')
 write('accuracy_frontier',lines+[r'\bottomrule',r'\end{tabular}'])
 p=REV/'results/robustness/summary.json'
 if not p.exists():return
 z=json.loads(p.read_text());assert z['status']=='PASS'
 lines=[r'\begin{tabular}{rrrrrrrr}',r'\toprule',r'$d$ & NBO & SOC & LQ & Mean diff. & Median diff. & Wins & Adj. $p$ \\',r'\midrule']
 for r in z['rows']:
  lines.append(f"{r['dimension']} & {r['means']['nbo']:.4f} & {r['means']['soc']:.4f} & {r['means']['lq']:.4f} & {r['mean_difference']:.4f} & {r['median_difference']:.4f} & {r['nbo_wins']}/12 & {r['bonferroni_three_p']:.5f}"+r' \\')
 write('robustness',lines+[r'\bottomrule',r'\end{tabular}'])
 lines=[r'\begin{tabular}{rllrr}',r'\toprule',r'$d$ & NBO selected & SOC selected & NBO sec. & SOC sec. \\',r'\midrule']
 for r in z['rows']:
  sel=r['selected'];n=sel['nbo']['config'];c=sel['soc']['config']
  # Short IDs bind to the exhaustive candidate tables in the protocol and raw tuning records.
  ns=f"{sel['nbo']['candidate']} ($m={n['mult']:.3g}$)";cs=f"{sel['soc']['candidate']} ($m={c['mult']:.3g}$)"
  tune=json.loads((REV/f"results/robustness/d{r['dimension']}/tuning/tuning.json").read_text())
  clocks={m:sum(v.get('training_seconds',0.) for v in tune['rows'] if v['method']==m) for m in ['nbo','soc']}
  lines.append(f"{r['dimension']} & {ns} & {cs} & {clocks['nbo']:.2f} & {clocks['soc']:.2f}"+r' \\')
 write('tuning',lines+[r'\bottomrule',r'\end{tabular}'])
if __name__=='__main__':run()
