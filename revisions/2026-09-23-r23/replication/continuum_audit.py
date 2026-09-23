"""A posteriori directed continuum certification of every prescribed R23 arm."""
from pathlib import Path
import sys,json,time
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r23'
sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r22/replication'))
from continuum import I,Q,PEXIT,hess_bounds,read,save,general_jensen
from moment_jensen import moment_jensen

def main():
 H=hess_bounds();rows=[];comparisons=[];start=time.perf_counter()
 for seed in (23000,23100,23200):
  base=REV/f'results/crossed/seed{seed}'
  initial=[read(base/f'vertex{v}/initial_actor.json') for v in range(4)]
  initial_c=[read(base/f'vertex{v}/initial_certificate.json') for v in range(4)]
  qi=[read(base/f'vertex{v}/quotient_initial_actor.json') for v in range(4)]
  qic=[read(base/f'vertex{v}/quotient_initial_certificate.json') for v in range(4)]
  gamma=moment_jensen(initial,initial_c,H);save(REV/f'results/moments/seed{seed}_initial.json',gamma)
  gammaq=gamma if initial==qi and initial_c==qic else moment_jensen(qi,qic,H)
  save(REV/f'results/moments/seed{seed}_quotient_initial.json',gammaq)
  for rep in ('neural','direct','quotient'):
   for opt in ('adam','lbfgsb'):
    rr=[read(base/f'vertex{v}/{rep}_{opt}/record.json') for v in range(4)]
    finals=[r['delivered_certificate'] for r in rr];old=qic if rep=='quotient' else initial_c;g=gammaq if rep=='quotient' else gamma
    B=max(float((I(c['optimal_value_upper'])-I(c['value_interval'][0])+16*PEXIT).hi) for c in finals)
    vertex_gain=min(float((I(c['value_interval'][0])-I(o['value_interval'][1])).lo) for c,o in zip(finals,old))
    gain=float((I(vertex_gain)-I(g['bound'])-16*PEXIT).lo)
    row={'base_seed':seed,'representation':rep,'optimizer':opt,'K_regret_upper':B,'K_gain_from_initial_lower':gain,'strict_uniform_improvement_certified':gain>0,'jensen_initial_upper':g['bound'],'accepted_corners':sum(r['accepted'] for r in rr),'function_evaluations':sum(r['function_evaluations'] for r in rr),'gradient_evaluations':sum(r['gradient_evaluations'] for r in rr),'line_search_evaluations':sum(r['line_search_evaluations'] for r in rr),'generation_seconds':sum(r['generation_seconds'] for r in rr),'initial_checker_seconds':sum(r['initial_checker_seconds'] for r in rr),'final_checker_seconds':sum(r['final_checker_seconds'] for r in rr),'root_calls':sum(r['root_accounting']['calls'] for r in rr),'root_bisections':sum(r['root_accounting']['bisections'] for r in rr)}
    if gain>0:row['true_regret_ratio_upper']=float((I(B)/(I(B)+I(gain))).hi)
    rows.append(row)
  neural=[read(base/f'vertex{v}/neural_adam/record.json')['delivered_certificate'] for v in range(4)]
  for rep in ('direct','quotient'):
   actors=[read(base/f'vertex{v}/{rep}_adam/delivered_actor.json') for v in range(4)]
   certs=[read(base/f'vertex{v}/{rep}_adam/record.json')['delivered_certificate'] for v in range(4)]
   gd=moment_jensen(actors,certs,H);save(REV/f'results/moments/seed{seed}_{rep}_adam_final.json',gd)
   vertex=min(float((I(a['value_interval'][0])-I(b['value_interval'][1])).lo) for a,b in zip(neural,certs))
   gain=float((I(vertex)-I(gd['bound'])-16*PEXIT).lo)
   comparisons.append({'base_seed':seed,'comparison':'neural_adam_minus_'+rep+'_adam','minimum_vertex_payoff_gain_lower':vertex,'comparator_jensen_upper':gd['bound'],'uniform_payoff_gain_lower':gain,'positive_uniform_gain_certified':gain>0,'optimizer_budget_conditional':True,'unconditional_neural_advantage':False})
  print('R23 continuum',seed,'initial Gamma',gamma['bound'],'comparisons',comparisons[-2:],flush=True)
 save(REV/'results/continuum.json',{'rows':rows,'comparisons':comparisons,'hessian_absolute_upper':H,'seconds':time.perf_counter()-start,'scope':'t=0, K=[1.98,2.02]x[1.24,1.26], k=2','analysis_status':'a posteriori certified properties of all prospective R23 configurations; comparisons specified in protocol','theorem':'R22 nonsynchronized pair-moment Jensen theorem, retained and explicitly cited in R23','arithmetic':'directed rational/Taylor binary64; same mathematical derivation as inherited checker'})
if __name__=='__main__':main()
