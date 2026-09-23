"""Same-family representation audit; frozen R20 inputs, no new optimization."""
from pathlib import Path
import sys,json,hashlib
from decimal import Decimal,ROUND_CEILING,ROUND_FLOOR
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r21';OLD=ROOT/'revisions/2026-09-23-r20'
sys.path.insert(0,str(REV/'replication'))
from audit import hull,Q,I

def read(p):return json.loads(p.read_text())
def rounded(x,places=8,upper=True):
 return str(Decimal.from_float(float(x)).quantize(Decimal(10)**(-places),rounding=ROUND_CEILING if upper else ROUND_FLOOR))
def main():
 common=[];neural=[];direct=read(OLD/'results/classical_stochastic/records.json');last=[max((r for r in direct if r['vertex']==v),key=lambda r:r['step']) for v in range(4)]
 for seed in range(20100,20105):
  params=[read(OLD/f'results/neural/seed{seed}/vertex{v}/network_0000.json')['parameters'] for v in range(4)]
  assert all(p==params[0] for p in params)
  common.append({'seed':seed,'all_four_initial_parameter_dicts_identical':True,'parameter_sha256':hashlib.sha256(json.dumps(params[0],sort_keys=True,separators=(',',':')).encode()).hexdigest()})
  rows=[r for r in read(OLD/f'results/neural/seed{seed}/records.json') if r['step']==1000]
  neural.append({'seed':seed,'final_generation_seconds':sum(r['generation_seconds'] for r in rows),'all_checkpoint_check_seconds':sum(r['verification_cumulative_seconds'] for r in rows),'final_check_seconds':sum(r['seconds'] for r in rows)})
 assert len(set(x['parameter_sha256'] for x in common))==5
 vertices=[]
 for v,r in enumerate(last):
  direct_interval=r['value_interval'];p=REV/f"results/replay/binary/classical_stochastic/vertex{v}/actor_{r['step']:04d}.json"
  if p.exists():
   d=read(p)['value_interval'];direct_interval=[min(d[0],direct_interval[0]),max(d[1],direct_interval[1])]
  vals=[hull(seed,v,1000) for seed in range(20100,20105)]
  upper=I(r['optimal_value_upper']);ngaps=[float((upper-I(a.lo)).hi) for a in vals]
  cg=float((upper-I(direct_interval[0])).hi)
  advantage=min(float((I(direct_interval[0])-I(a.hi)).lo) for a in vals)
  assert cg<min(ngaps) and advantage>0
  vertices.append({'vertex':v,'u':r['u0'],'x':r['x0'],'best_neural_certified_regret':min(ngaps),'direct_certified_regret':cg,'direct_payoff_advantage_over_each_neural_lower':advantage})
 d={'review_commit':'bc118f20f6361cdeae668141e45f64c436ee6a2a','snapshot_reviewed':'6951c3b01b5102ef3d743a6ab14f9cc595b08804','scope':'20 vertex policy comparisons; no inference of all-interior payoff ordering','initialization':common,'independent_seed_replicates':5,'independent_vertex_initializations':False,'neural_costs':neural,'direct_costs':{'final_generation_seconds':sum(r['generation_seconds'] for r in last),'all_checkpoint_check_seconds':sum(r['verification_cumulative_seconds'] for r in last),'final_check_seconds':sum(r['seconds'] for r in last)},'vertices':vertices,'minimum_direct_payoff_advantage':min(r['direct_payoff_advantage_over_each_neural_lower'] for r in vertices)}
 (REV/'results/representation_audit.json').write_text(json.dumps(d,indent=2)+'\n')
 lines=[r'\begin{table}[htbp]\centering\small',r'\caption{Representation ablation at the final retained work level. Both methods use the same stochastic logistic family and unrestricted upper. The final column is a certified payoff ordering, not merely a comparison of regret bounds.}',r'\setlength{\tabcolsep}{3pt}\begin{tabular}{rrrrr}\toprule',r'$u$ & $x$ & Best neural bound & Direct bound & Direct payoff gain $\geq$ \\ \midrule']
 for r in vertices:lines.append(f"{r['u']} & {r['x']} & {rounded(r['best_neural_certified_regret'])} & {rounded(r['direct_certified_regret'])} & {rounded(r['direct_payoff_advantage_over_each_neural_lower'],8,False)}"+r' \\')
 lines += [r'\bottomrule\end{tabular}',r'\end{table}']
 (REV/'paper/table_representation.tex').write_text('\n'.join(lines)+'\n')
 lines=[r'\begin{table}[htbp]\centering\small',r'\caption{Unpooled four-expert cost at the final retained work level (seconds). The final-check column is a subset of all checkpoint checking, not an additional charge. The shared dual and MPFR costs remain separate.}',r'\begin{tabular}{lrrr}\toprule',r'Method & Generation & All checking & Final checking \\ \midrule']
 for r in neural:lines.append(f"Seed {r['seed']} & {rounded(r['final_generation_seconds'],3)} & {rounded(r['all_checkpoint_check_seconds'],3)} & {rounded(r['final_check_seconds'],3)}"+r' \\')
 r=d['direct_costs'];lines.append(f"Direct & {rounded(r['final_generation_seconds'],3)} & {rounded(r['all_checkpoint_check_seconds'],3)} & {rounded(r['final_check_seconds'],3)}"+r' \\')
 lines += [r'\bottomrule\end{tabular}',r'\end{table}'];(REV/'paper/table_generation.tex').write_text('\n'.join(lines)+'\n')
 print(json.dumps(d,indent=2))
if __name__=='__main__':main()
