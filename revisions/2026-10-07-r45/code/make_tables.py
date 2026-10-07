"""Audit all frozen services and materialize article tables without retraining."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,statistics,itertools
R=Path(__file__).resolve().parents[1]
J=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
METHODS=('min-plus-ReLU','piecewise-linear-spline');TARGETS=('1/2','1/4','1/8')
short={METHODS[0]:'ReLU envelope',METHODS[1]:'Spline'}
def table(caption,label,cols,head,rows,note):
 return '\\begin{table}[tbp]\n\\centering\n\\caption{'+caption+'}\\label{'+label+'}\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+head+' \\\\\n\\midrule\n'+'\n'.join(r+' \\\\' for r in rows)+'\n\\bottomrule\n\\end{tabular}\n\\par\\smallskip{\\footnotesize '+note+'}\n\\end{table}\n'
def main():
 records=sorted((R/'results/services').glob('service-*/record.json'));assert len(records)==24
 groups={};rows_audit=[];source=J(R/'audit/SOURCE_FREEZE.json')['sha256']
 for n,h in source.items():assert sha(R/n)==h,n
 for p in records:
  d=J(p);key=(d['method'],d['horizon'],d['price']);groups.setdefault(key,[]).append(d)
  assert d['repeat'] in (0,1,2) and [a['N'] for a in d['attempts']]==[16,32,64,128,256,512]
  for name,h in d['source_hashes'].items():assert source['code/'+name]==h
  assert J(p.parent/'clock.json')['record_sha256']==sha(p)
  cumulative=0
  for a in d['attempts']:
   cp=p.parent/f"checkpoint-N{a['N']}.json";assert a['checkpoint_sha256']==sha(cp)
   q=J(cp);assert q['method']==d['method'] and q['T']==d['horizon'] and q['price']==d['price']
   gap=sum((F(15,16)**t*(F(z['residual_upper'])-F(z['residual_lower'])+F(z['actor_allowance'])) for t,z in enumerate(q['rows'])),F(0))+F(15,16)**q['T']*F(q['terminal_width'])
   assert gap==F(q['policy_bound_exact'])==F(a['policy_bound_exact'])
   assert F(a['policy_bound_upper'])>=gap
   assert a['counts']['q_evaluations']==q['T']*(a['N']+1)**2
   cumulative+=a['counts']['q_evaluations'];assert cumulative==a['cumulative_q_evaluations']
   assert len(q['actors'])==q['T'] and all(len(v)==a['N']+1 and all(0<=x<=.25 for x in v) for v in q['actors'])
   rows_audit.append({'service':p.parent.name,'N':a['N'],'checkpoint_sha256':sha(cp),'gap_exact':str(gap)})
  for target in TARGETS:
   first=next((a for a in d['attempts'] if F(a['policy_bound_exact'])<=F(target)),None)
   reported=d['first_crossings'][target]
   assert (first is None)==(reported is None)
   if first:assert first['N']==reported['N'] and first['seconds_through_checkpoint_fsync']==reported['seconds_through_checkpoint_fsync']
 assert set(groups)==set(itertools.product(METHODS,(2,4),(1,4)))
 cells=[];att_rows=[];work_rows=[];front_rows=[]
 for (method,T,p),values in groups.items():
  assert sorted(v['repeat'] for v in values)==[0,1,2]
  # Policies and every exact certificate must coincide across timing repetitions.
  assert len({tuple(a['checkpoint_sha256'] for a in v['attempts']) for v in values})==1
  first=values[0];hits={e:first['first_crossings'][e] for e in TARGETS}
  final=first['attempts'][-1]
  rows=[]
  for n,a in enumerate(first['attempts']):
   times=[v['attempts'][n]['seconds_through_checkpoint_fsync'] for v in values]
   rows.append({'N':a['N'],'bound':a['policy_bound_upper'],'median_seconds':statistics.median(times),'min_seconds':min(times),'max_seconds':max(times),'cumulative_q':a['cumulative_q_evaluations'],'compiled_knots':a['counts']['compiled_knots'],'actor_scalars':a['counts']['actor_scalar_storage'],'checkpoint_bytes':a['checkpoint_bytes'],'max_rational_bits':a['counts']['max_rational_bit_length']})
   front_rows.append(f"{short[method]} & {T} & {p} & {a['N']} & {a['policy_bound_upper']:.5f} & {a['cumulative_q_evaluations']:,} & {statistics.median(times):.4f}")
  cells.append({'method':method,'T':T,'price':p,'frontier':rows,'first_crossings':{k:None if v is None else v['N'] for k,v in hits.items()},'peak_rss_kib':[v['peak_process_rss_kib'] for v in values]})
  att_rows.append(f"{short[method]} & {T} & {p} & "+' & '.join('--' if hits[e] is None else str(hits[e]['N']) for e in TARGETS)+f" & {final['policy_bound_upper']:.5f}")
  index=next((i for i,a in enumerate(first['attempts']) if F(a['policy_bound_exact'])<=F(1,8)),5)
  a=first['attempts'][index];ts=[v['attempts'][index]['seconds_through_checkpoint_fsync'] for v in values]
  status='cap' if hits['1/8'] is None else 'target'
  work_rows.append(f"{short[method]} & {T},{p} & {a['N']} & {a['cumulative_q_evaluations']:,} & {statistics.median(ts):.4f} & [{min(ts):.4f}, {max(ts):.4f}] & {status}")
 summary={'services':24,'economy_cells':4,'timing_repetitions_per_cell':3,'rungs':144,'unique_method_cell_frontier_rows':48,'all_checkpoint_hashes_equal_across_repetitions':True,
 'attainment':{m:{e:sum(d['first_crossings'][e] is not None for d in (J(p) for p in records) if d['method']==m) for e in TARGETS} for m in METHODS},'cells':cells}
 signs=[]
 for T,p,rep,e in itertools.product((2,4),(1,4),range(3),TARGETS):
  a=next(v for v in groups[(METHODS[0],T,p)] if v['repeat']==rep)['first_crossings'][e]
  b=next(v for v in groups[(METHODS[1],T,p)] if v['repeat']==rep)['first_crossings'][e]
  if a and b:signs.append(a['seconds_through_checkpoint_fsync']>b['seconds_through_checkpoint_fsync'])
 summary['common_successful_paired_times']=len(signs);summary['neural_slower_pairs']=sum(signs)
 summary['scope']='Deterministic backend, finite cap and local sequential runner timings. No original training success probabilities, direct cost contrast, frequency control, or full FLOP counts.'
 (R/'audit/PUBLICATION_SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
 (R/'audit/RESULT_AUDIT.json').write_text(json.dumps({'successful':True,'records':24,'checkpoint_count':144,'reconstructed_bounds':rows_audit,'original_results_not_modified':True},indent=2)+'\n')
 (R/'tables/constructive45.tex').write_text(table('First certified state/action resolution in the complete constructive catalogue','tab:constructive45','lrrrrrr','Generator & $T$ & $p$ & $0.5$ & $0.25$ & $0.125$ & Final gap',att_rows,'Entries are first qualifying $N=A$ on the fixed ladder. Each row represents three identical deterministic policy/certificate arrays, not three independent economic tasks. A dash is a retained failure at the declared cap $N=512$. Final gaps use the cap for both methods.'))
 (R/'tables/work45.tex').write_text(table('Complete prefix work at target $0.125$, or at the failed cap','tab:work45','lrrrrll','Generator & $T,p$ & $N$ & Queries & Median s & Range s & Exit',work_rows,'Queries sum all Bellman evaluations on earlier failed rungs and the reported rung. Clocks include construction, verification and durable checkpoints. Ranges contain the three isolated observations. A cap row is not time to successful certification. Independent economic comparison is not included.'))
 front='\\section{Complete constructive verification frontiers}\n\\begin{longtable}{lrrrrrr}\n\\caption{All 48 distinct method--economy--resolution rows}\\label{tab:frontier45}\\\\\n\\toprule\nGenerator & $T$ & $p$ & $N$ & Gap & Prefix queries & Median s\\\\\n\\midrule\\endfirsthead\n\\toprule\nGenerator & $T$ & $p$ & $N$ & Gap & Prefix queries & Median s\\\\\n\\midrule\\endhead\n'+'\n'.join(z+' \\\\' for z in front_rows)+'\n\\bottomrule\\end{longtable}\nEvery row represents three byte-identical policy and certificate checkpoints with distinct clocks. Complete counts, storage, memory, and the individual clocks are deposited in the machine-readable records. The full frontier includes unsuccessful rungs; no refined neural row is substituted for an original failed service.\n'
 (R/'tables/frontier45.tex').write_text(front)
 text=f"The neural backend certifies all twelve services at $0.5$ and $0.25$, and nine of twelve at $0.125$. The spline certifies all twelve at every target. The three neural failures are repetitions of the same horizon-four, price-four economy: the final gap is approximately $0.12503$, just above $0.125$. They remain failures rather than being rounded into attainment. Across the {len(signs)} common successful method/target/repetition comparisons, the spline reaches the target earlier in every recorded observation. Thus the new execution establishes reproducible complete construction and a transparent frontier, not neural cost superiority. The deterministic termination corollary concerns its specified sufficient budget; the predeclared finite ladder need not contain that budget.\n"
 (R/'tables/outcome45.tex').write_text(text)
 print(json.dumps({k:v for k,v in summary.items() if k!='cells'},indent=2))
if __name__=='__main__':main()
